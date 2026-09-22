"""
add.py -- build 3D models with nothing but Python code.
==============================================================================

Version 2.0  |  Martynas Sabaliauskas (VU MIF DMSTI)  |  MIT licence

A tiny, dependency-free 3D modelling kernel for teaching.  The whole library
uses only ``math`` and ``random`` from the standard library: no NumPy, no
mesh library, no modelling program.  Every triangle you see was computed by
code you can read.

Quick start
-----------
::

    import add

    add.box([0, 0, 0], 1, [255, 0, 0])          # a red cube
    add.sphere([2, 0, 0], 0.6, 20, [0, 128, 255])
    add.save("model.off")                        # or "model.obj"

Three layers of API
-------------------
1. **Draw** -- ``box``, ``sphere``, ``tube``, ``parametric`` ... add shapes to
   the current scene.
2. **Shape** -- ``layer()`` takes the scene out as a *mesh object* you can
   ``move``, ``rotate``, ``mirror``, ``twist`` or combine with booleans;
   ``mesh(M)`` puts one back.
3. **Finish** -- ``clean()`` repairs the model, ``check()`` reports on it,
   ``save()`` writes ``.off`` or ``.obj`` (+ ``.mtl``).

Only ``import add``
-------------------
``math`` and ``random`` are re-exported, so ``add.sin(t)``, ``add.pi``,
``add.randint(1, 6)`` and ``add.seed(7)`` all work and a model file needs no
other import.  (``import math`` still works too, of course.)

What is in 2.0
--------------
Booleans written from scratch (``union``, ``difference``, ``intersect``,
``cut``); the five regular polyhedra (``tetrahedron`` ... ``icosahedron``,
``polyhedron_points``) and a geodesic ``sphere`` of triangles; vertex tools
(``neighbors``, ``valence``, ``set_vertex``, ``dual``, ``truncate``,
``refine``, ``spherify``); smooth surfaces (``catmull_clark`` and
``smooth``, the generalised Catmull-Clark algorithm); a catalogue of named
surfaces (``surface``); parts, placing and colour functions; repair and
``check()`` with the Sketchfab limits (``limit_colors``, ``obj_size``);
see-through colours and image textures for ``.obj`` files
(``transparent``, ``opacity``, ``texture``, ``write_png``).

Compatibility
-------------
Code written for add.py 1.2 keeps working unchanged: the old names
(``cube2``, ``cylinder2``, ``cylinder3``, ``cone2``, ``rectangle3D``,
``spin3D``, ``curve``, ``off``, ``zoom`` ...) are all still here, and so are
the module-level ``add.vertices`` / ``add.faces`` string lists.  The one
visible change is ``sphere``, now made of triangles; ``quadsphere`` is the
old six-patch version.

Coordinate convention
---------------------
Right-handed, Y up.  X is drawn red, Y green, Z blue (see ``axes``).
A face is *outward* when its vertices run counter-clockwise as seen from
outside the model.
"""

import math
import random as _random

# Everything in ``math`` and ``random`` is available straight from this
# module, so a model needs nothing but ``import add``:  add.sin, add.pi,
# add.sqrt, add.randint, add.uniform, add.choice, add.seed ...
from math import *          # noqa: F401,F403
from random import *        # noqa: F401,F403

__version__ = "2.0"
__all__ = []  # filled in at the bottom of the file

#: Numerical tolerance used by welding, boolean operations and plane tests.
EPS = 1e-9

#: Colour used when a function is called without one.
DEFAULT_COLOR = (160, 160, 160)


# ============================================================================
#  1. Small helpers -- vectors and colours
# ============================================================================
# Points are plain 3-element tuples/lists.  These helpers are deliberately
# written out in full so that every line is readable without prior knowledge.

def _sub(a, b):
    """Vector a - b."""
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _add3(a, b):
    """Vector a + b."""
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _scale(a, s):
    """Vector a * s."""
    return (a[0] * s, a[1] * s, a[2] * s)


def _dot(a, b):
    """Scalar (dot) product."""
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a, b):
    """Vector (cross) product."""
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def _norm(a):
    """Length of a vector."""
    return math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])


def _unit(a):
    """Vector of length 1 pointing the same way as ``a`` (0 vector stays 0)."""
    n = _norm(a)
    if n < EPS:
        return (0.0, 0.0, 0.0)
    return (a[0] / n, a[1] / n, a[2] / n)


def _perp(n):
    """Some unit vector perpendicular to ``n``."""
    if abs(n[0]) < 0.9:
        other = (1.0, 0.0, 0.0)
    else:
        other = (0.0, 1.0, 0.0)
    return _unit(_cross(n, other))


def _frame(direction):
    """Return three unit vectors (u, v, w) with w along ``direction``.

    ``u`` is chosen as the first world axis (X, then Y, then Z) that is not
    parallel to ``w``, so a profile drawn in ``(u, v)`` keeps its natural
    orientation: for a shape along Z, ``u = X`` and ``v = Y``; for one
    standing up along Y, ``u = X`` and ``v = -Z``.
    """
    w = _unit(direction)
    if _norm(w) < EPS:
        w = (0.0, 0.0, 1.0)
    for cand in ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)):
        d = _dot(w, cand)
        if abs(d) < 0.9:
            u = _unit((cand[0] - w[0] * d, cand[1] - w[1] * d, cand[2] - w[2] * d))
            break
    v = _cross(w, u)
    return u, v, w


def _num(x):
    """Format a float the short way, so .off/.obj files stay small."""
    if x == int(x) and abs(x) < 1e15:
        return str(int(x))
    return repr(round(x, 9))


def rgb(color):
    """Normalise anything colour-like into a ``(r, g, b)`` tuple of 0..255 ints.

    Accepts ``[255, 0, 0]``, ``(1.0, 0.0, 0.0)`` (floats 0..1 are scaled),
    ``"#ff0000"``, ``"red"`` or ``None`` (-> :data:`DEFAULT_COLOR`).

    A fourth value is the *opacity*: ``[120, 190, 255, 0.4]`` or
    ``"#78beff66"`` is a see-through blue, kept as a fourth element of the
    tuple (see :func:`transparent`).  A fifth, a file name, is an image
    texture (see :func:`texture`).  Both only take effect in ``.obj``
    files; everything else treats the colour as before.
    """
    if color is None:
        return DEFAULT_COLOR
    if isinstance(color, str):
        s = color.strip().lower()
        if s in COLORS:
            return COLORS[s]
        s = s.lstrip("#")
        if len(s) in (3, 4):
            s = "".join(ch * 2 for ch in s)
        if len(s) in (6, 8):
            out = (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))
            if len(s) == 8 and int(s[6:8], 16) < 255:
                return out + (round(int(s[6:8], 16) / 255.0, 3),)
            return out
        raise ValueError("unknown colour: %r" % color)
    r, g, b = color[0], color[1], color[2]
    if isinstance(r, float) and isinstance(g, float) and isinstance(b, float) \
            and max(r, g, b) <= 1.0:
        r, g, b = r * 255.0, g * 255.0, b * 255.0
    out = []
    for c in (r, g, b):
        c = int(round(c))
        out.append(0 if c < 0 else (255 if c > 255 else c))
    out = (out[0], out[1], out[2])
    alpha, image = 1.0, None
    if len(color) > 3 and color[3] is not None:
        alpha = float(color[3])
        if alpha > 1.0:                            # given as 0..255
            alpha /= 255.0
        alpha = round(0.0 if alpha < 0 else (1.0 if alpha > 1 else alpha), 3)
    if len(color) > 4 and color[4]:
        image = str(color[4])
    if image is not None:
        return out + (alpha, image)
    if alpha < 1.0:
        return out + (alpha,)
    return out


def transparent(color, alpha=0.5):
    """A see-through version of a colour: ``alpha`` is the opacity, 0 for
    invisible and 1 for solid.

    Any drawing function takes the result in place of a colour, so a
    window is ``add.cuboid(c, [2, 1.5, 0.05], add.transparent("sky", 0.35))``.
    The opacity is written to the ``.mtl`` file of an ``.obj`` model (as
    ``d``); ``.off`` files stay plain colours.  See also :func:`opacity`.
    """
    c = rgb(color)
    return rgb((c[0], c[1], c[2], alpha) + tuple(c[4:5]))


def _material(c):
    """``(r, g, b, alpha, image)`` for any colour tuple."""
    return (c[0], c[1], c[2],
            c[3] if len(c) > 3 else 1.0,
            c[4] if len(c) > 4 else None)


#: A handful of named colours, so ``add.box(c, 1, "red")`` works.
COLORS = {
    "black": (0, 0, 0), "white": (255, 255, 255), "grey": (128, 128, 128),
    "gray": (128, 128, 128), "red": (255, 0, 0), "green": (0, 255, 0),
    "blue": (0, 0, 255), "yellow": (255, 255, 0), "cyan": (0, 255, 255),
    "magenta": (255, 0, 255), "orange": (255, 140, 0), "purple": (128, 0, 200),
    "pink": (255, 130, 180), "brown": (139, 69, 19), "gold": (212, 175, 55),
    "silver": (192, 192, 192), "navy": (0, 0, 128), "teal": (0, 128, 128),
    "lime": (140, 255, 60), "sky": (120, 190, 255),
}


def hsv(h, s=1.0, v=1.0):
    """Colour from hue/saturation/value, all in 0..1.  Hue wraps around.

    Handy for rainbows::

        for i in range(n):
            add.box([i, 0, 0], 0.9, add.hsv(i / n))
    """
    h = (h % 1.0) * 6.0
    i = int(h)
    f = h - i
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    table = [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)]
    r, g, b = table[i % 6]
    return (int(r * 255), int(g * 255), int(b * 255))


def gradient(t, a, b):
    """Blend between colours ``a`` and ``b``; ``t`` runs 0 -> 1."""
    a, b = rgb(a), rgb(b)
    t = 0.0 if t < 0 else (1.0 if t > 1 else t)
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def random_color(seed=None):
    """A random colour.  Pass ``seed`` for a repeatable one."""
    r = _random if seed is None else _random.Random(seed)
    return (r.randint(0, 255), r.randint(0, 255), r.randint(0, 255))


# ============================================================================
#  2. Mesh -- the one data structure in this library
# ============================================================================

class Mesh(object):
    """A list of vertices and a list of coloured faces.

    ``M.V`` is a list of ``[x, y, z]`` points, ``M.F`` a list of index lists
    (a face may have any number of corners) and ``M.C`` the colour of each
    face.  ``len(M.F)`` is the polygon count.

    For backwards compatibility a mesh also behaves like the old
    ``[vertices, faces]`` pair of *string* lists, so ``M[0]`` and ``M[1]``
    still give you exactly what add.py 1.2 produced.
    """

    __slots__ = ("V", "F", "C", "UV")

    def __init__(self, V=None, F=None, C=None, UV=None):
        self.V = V if V is not None else []
        self.F = F if F is not None else []
        self.C = C if C is not None else []
        #: Texture coordinates, one ``[(u, v), ...]`` per face (or ``None``
        #: for a face without a texture); ``None`` when nothing is textured.
        self.UV = UV

    # -- basic dunder methods ------------------------------------------------

    def __repr__(self):
        return "<Mesh %d vertices, %d faces>" % (len(self.V), len(self.F))

    def __len__(self):
        return 2                      # old code saw a 2-element pair

    def __iter__(self):
        yield self.vertex_strings()
        yield self.face_strings()

    def __getitem__(self, i):
        """``M[0]`` -> vertex strings, ``M[1]`` -> face strings (old API)."""
        if i == 0:
            return self.vertex_strings()
        if i == 1:
            return self.face_strings()
        raise IndexError("a mesh has only M[0] (vertices) and M[1] (faces)")

    # -- old string representation ------------------------------------------

    def vertex_strings(self):
        """The vertices as ``"x y z"`` strings (add.py 1.2 representation)."""
        return ["%s %s %s" % (_num(p[0]), _num(p[1]), _num(p[2]))
                for p in self.V]

    def face_strings(self):
        """The faces as ``"n i0 i1 .. r g b"`` strings (1.2 representation)."""
        out = []
        for f, c in zip(self.F, self.C):
            out.append("%d %s %d %d %d" % (len(f), " ".join(str(i) for i in f),
                                           c[0], c[1], c[2]))
        return out

    # -- construction --------------------------------------------------------

    def copy(self):
        """An independent copy."""
        return Mesh([list(p) for p in self.V],
                    [list(f) for f in self.F],
                    list(self.C),
                    None if self.UV is None else
                    [None if t is None else list(t) for t in self.UV])

    def add_vertex(self, p):
        """Append a point and return its index."""
        self.V.append([float(p[0]), float(p[1]), float(p[2])])
        return len(self.V) - 1

    def add_face(self, indices, color=None, uv=None):
        """Append one face given as a sequence of vertex indices."""
        self.F.append(list(indices))
        self.C.append(rgb(color))
        if uv is not None:
            if self.UV is None:
                self.UV = [None] * (len(self.F) - 1)
            self.UV.append(list(uv))
        elif self.UV is not None:
            self.UV.append(None)

    def add_polygon(self, points, color=None):
        """Append one face given as a sequence of 3D points."""
        base = len(self.V)
        for p in points:
            self.add_vertex(p)
        self.add_face(range(base, len(self.V)), color)

    def extend(self, other):
        """Append another mesh to this one (in place)."""
        other = as_mesh(other)
        shift = len(self.V)
        self.V.extend([list(p) for p in other.V])
        if other.UV is not None and self.UV is None:
            self.UV = [None] * len(self.F)
        for f, c in zip(other.F, other.C):
            self.F.append([i + shift for i in f])
            self.C.append(c)
        if self.UV is not None:
            if other.UV is None:
                self.UV.extend([None] * len(other.F))
            else:
                self.UV.extend([None if t is None else list(t)
                                for t in other.UV])
        return self

    def uv_of(self, i):
        """The texture coordinates of face ``i``, or ``None``."""
        return None if self.UV is None else self.UV[i]

    # -- convenience ---------------------------------------------------------

    @property
    def polygons(self):
        """Number of faces."""
        return len(self.F)

    def face_points(self, i):
        """The corner points of face ``i`` as a list of ``[x, y, z]``."""
        return [self.V[k] for k in self.F[i]]


def as_mesh(obj):
    """Accept a :class:`Mesh`, a ``[vertex_strings, face_strings]`` pair or
    ``None`` (the current scene) and always return a :class:`Mesh`.

    This is what lets ten-year-old student code and new code mix freely.
    """
    if obj is None:
        return _scene
    if isinstance(obj, Mesh):
        return obj
    if isinstance(obj, (list, tuple)) and len(obj) == 2:
        return _mesh_from_strings(obj[0], obj[1])
    raise TypeError("expected a mesh, got %r" % type(obj).__name__)


def _mesh_from_strings(vertex_strings, face_strings):
    """Rebuild a Mesh from the add.py 1.2 string representation."""
    M = Mesh()
    for s in vertex_strings:
        if isinstance(s, str):
            parts = s.split()
            M.V.append([float(parts[0]), float(parts[1]), float(parts[2])])
        else:                                   # already a point
            M.V.append([float(s[0]), float(s[1]), float(s[2])])
    for s in face_strings:
        if isinstance(s, str):
            parts = s.split()
            n = int(parts[0])
            idx = [int(x) for x in parts[1:1 + n]]
            rest = parts[1 + n:]
            color = DEFAULT_COLOR
            if len(rest) >= 3:
                color = rgb([float(rest[0]), float(rest[1]), float(rest[2])])
            M.F.append(idx)
            M.C.append(color)
        else:                                   # (indices, colour) pair
            M.F.append(list(s[0]))
            M.C.append(rgb(s[1]) if len(s) > 1 else DEFAULT_COLOR)
    return M


# ============================================================================
#  3. The current scene (the "default layer")
# ============================================================================

_scene = Mesh()


class _StringView(object):
    """Makes ``add.vertices`` / ``add.faces`` look like the old string lists.

    It is a live window on the current scene, so ``len(add.faces)`` answers
    "how many polygons do I have?" and ``add.faces += [...]`` still works for
    anybody who learned the 1.2 internals.
    """

    __slots__ = ("_which",)

    def __init__(self, which):
        self._which = which

    def _list(self):
        if self._which == 0:
            return _scene.vertex_strings()
        return _scene.face_strings()

    def __len__(self):
        return len(_scene.V) if self._which == 0 else len(_scene.F)

    def __getitem__(self, i):
        return self._list()[i]

    def __iter__(self):
        return iter(self._list())

    def __repr__(self):
        return repr(self._list())

    def __eq__(self, other):
        return self._list() == other

    def __iadd__(self, items):
        """``add.vertices += [...]`` / ``add.faces += [...]`` (old style)."""
        if self._which == 0:
            for s in items:
                parts = s.split() if isinstance(s, str) else s
                _scene.add_vertex([float(parts[0]), float(parts[1]),
                                   float(parts[2])])
        else:
            for s in items:
                parts = s.split()
                n = int(parts[0])
                idx = [int(x) for x in parts[1:1 + n]]
                rest = parts[1 + n:]
                color = rgb([float(x) for x in rest[:3]]) if len(rest) >= 3 \
                    else DEFAULT_COLOR
                _scene.add_face(idx, color)
        return self

    def append(self, s):
        self.__iadd__([s])


#: The current scene's vertices, in the add.py 1.2 string form.
vertices = _StringView(0)
#: The current scene's faces, in the add.py 1.2 string form.
faces = _StringView(1)


def scene():
    """The :class:`Mesh` everything is currently being drawn into."""
    return _scene


def clear():
    """Throw away everything drawn so far."""
    global _scene
    _scene = Mesh()


def layer():
    """Take the scene out as a mesh and start a fresh, empty scene.

    This is the workhorse of the library: draw something, ``layer()`` it,
    transform the result, then ``mesh()`` it back (possibly many times)::

        add.box([0, 0, 0], 1, "red")
        brick = add.layer()
        for i in range(10):
            add.mesh(add.move(brick, [i, 0, 0]))
    """
    global _scene
    M = _scene
    _scene = Mesh()
    return M


_stack = []


def push():
    """Put the scene aside and start a fresh, empty one.

    Use it inside a function that builds a part, so that the part cannot
    accidentally scoop up everything drawn before it -- the commonest
    surprise for anyone using :func:`layer`::

        def wheel(r):
            add.push()                 # nothing else can get in
            add.cylinder(...)
            add.torus(...)
            return add.pop()           # and the old scene comes back
    """
    global _scene
    _stack.append(_scene)
    _scene = Mesh()


def pop():
    """Return what was drawn since :func:`push` and restore the old scene."""
    global _scene
    made = _scene
    _scene = _stack.pop() if _stack else Mesh()
    return made


def make(draw, *args, **kwargs):
    """Call a drawing function and return what it drew as a mesh, without
    touching the current scene.

    ``add.make(add.sphere, [0, 0, 0], 1, 20, "red")`` is the same as
    ``push()``, ``sphere(...)``, ``pop()``; it turns any of the drawing
    functions into one that *returns* a mesh::

        ball = add.make(add.sphere, [0, 0, 0], 1)
        add.mesh(add.move(ball, [3, 0, 0]))
    """
    push()
    try:
        draw(*args, **kwargs)
    finally:
        made = pop()
    return made


def mesh(M):
    """Draw mesh ``M`` into the current scene."""
    _scene.extend(as_mesh(M))
    return M


#: ``add.paste`` is a friendlier name for :func:`mesh`.
paste = mesh


def merge(meshes):
    """Combine several meshes into one (no geometry is changed).

    ``merge`` just concatenates.  For a *watertight* combination that removes
    the parts hidden inside, use :func:`union` instead.
    """
    out = Mesh()
    for M in meshes:
        out.extend(as_mesh(M))
    return out


def copy(M=None):
    """An independent copy of ``M`` (or of the scene)."""
    return as_mesh(M).copy()

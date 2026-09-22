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


# ============================================================================
#  4. Building blocks used by every shape below
# ============================================================================

def _add_grid(M, P, color, wrap_u=False, wrap_v=False, flip=False):
    """Turn a 2D array of points ``P[i][j]`` into a quad patch.

    ``wrap_u`` / ``wrap_v`` close the patch into a tube or a torus.
    ``flip`` reverses the winding (makes the patch face the other way).
    ``color`` is one colour, or a function ``paint(i, j)`` giving the colour
    of cell ``(i, j)``.  This one helper is behind ``parametric``,
    ``revolve``, ``sweep``, ``loft``, ``sphere``, ``torus`` and ``tube``.
    """
    nu, nv = len(P), len(P[0])
    base = len(M.V)
    for row in P:
        for p in row:
            M.add_vertex(p)
    paint = color if callable(color) else None
    if paint is None:
        color = rgb(color)
    steps_u = nu if wrap_u else nu - 1
    steps_v = nv if wrap_v else nv - 1
    for i in range(steps_u):
        i2 = (i + 1) % nu
        for j in range(steps_v):
            j2 = (j + 1) % nv
            a = base + i * nv + j
            b = base + i2 * nv + j
            c = base + i2 * nv + j2
            d = base + i * nv + j2
            quad = [a, b, c, d] if not flip else [d, c, b, a]
            M.add_face(quad, rgb(paint(i, j)) if paint else color)


def _ring(center, u, v, r, k, phase=0.0):
    """``k`` points on a circle of radius ``r`` around ``center``.

    ``u`` and ``v`` are the two unit vectors spanning the circle's plane.
    """
    pts = []
    for i in range(k):
        a = phase + 2.0 * math.pi * i / k
        cs, sn = math.cos(a) * r, math.sin(a) * r
        pts.append((center[0] + u[0] * cs + v[0] * sn,
                    center[1] + u[1] * cs + v[1] * sn,
                    center[2] + u[2] * cs + v[2] * sn))
    return pts


def _fan(M, points, apex, color, flip=False, closed=True):
    """Close a ring of points with a triangle fan meeting at ``apex``.

    With ``closed=False`` the points form an open arc (a wedge lid) and no
    triangle is drawn between the last point and the first.
    """
    base = len(M.V)
    for p in points:
        M.add_vertex(p)
    tip = M.add_vertex(apex)
    n = len(points)
    paint = color if callable(color) else None
    if paint is None:
        color = rgb(color)
    for i in range(n if closed else n - 1):
        j = (i + 1) % n
        tri = [base + i, base + j, tip] if not flip else [base + j, base + i, tip]
        M.add_face(tri, rgb(paint(i)) if paint else color)


def _signed_volume(M, first_face=0):
    """Six times the signed volume of faces ``first_face..end``.

    Positive means the faces are wound outward.  Used to make sure every
    closed primitive in this library faces the right way.
    """
    total = 0.0
    for f in M.F[first_face:]:
        if len(f) < 3:
            continue
        a = M.V[f[0]]
        for t in range(1, len(f) - 1):
            b, c = M.V[f[t]], M.V[f[t + 1]]
            total += (a[0] * (b[1] * c[2] - b[2] * c[1])
                      - a[1] * (b[0] * c[2] - b[2] * c[0])
                      + a[2] * (b[0] * c[1] - b[1] * c[0]))
    return total


def _make_outward(M, first_face):
    """Flip faces ``first_face..end`` if they came out inside-out."""
    if _signed_volume(M, first_face) < 0:
        for i in range(first_face, len(M.F)):
            M.F[i].reverse()


def _grid_solid(origin, sx, sy, sz, filled, color):
    """Surface of a solid described on a rectangular grid of cells.

    ``sx``/``sy``/``sz`` are lists of cell sizes along each axis and
    ``filled(i, j, k)`` says whether cell ``(i, j, k)`` is material.  Only the
    faces between material and air are emitted, so the result is watertight
    and has no hidden geometry.  ``color`` may be a function ``(i, j, k)``.
    :func:`frame`, :func:`voxels`, :func:`pixels` and :func:`heightmap` are
    all thin wrappers around this.
    """
    nx, ny, nz = len(sx), len(sy), len(sz)
    # Coordinates of every grid line.
    X = [origin[0]]
    for s in sx:
        X.append(X[-1] + s)
    Y = [origin[1]]
    for s in sy:
        Y.append(Y[-1] + s)
    Z = [origin[2]]
    for s in sz:
        Z.append(Z[-1] + s)

    M = Mesh()
    index = {}

    def point(i, j, k):
        key = (i, j, k)
        if key not in index:
            index[key] = M.add_vertex((X[i], Y[j], Z[k]))
        return index[key]

    def solid(i, j, k):
        if 0 <= i < nx and 0 <= j < ny and 0 <= k < nz:
            return bool(filled(i, j, k))
        return False

    paint = color if callable(color) else None
    if paint is None:
        color = rgb(color)
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                if not solid(i, j, k):
                    continue
                if paint is not None:
                    color = rgb(paint(i, j, k))
                if not solid(i - 1, j, k):          # -X wall
                    M.add_face([point(i, j, k), point(i, j, k + 1),
                                point(i, j + 1, k + 1), point(i, j + 1, k)], color)
                if not solid(i + 1, j, k):          # +X wall
                    M.add_face([point(i + 1, j, k), point(i + 1, j + 1, k),
                                point(i + 1, j + 1, k + 1), point(i + 1, j, k + 1)], color)
                if not solid(i, j - 1, k):          # -Y wall
                    M.add_face([point(i, j, k), point(i + 1, j, k),
                                point(i + 1, j, k + 1), point(i, j, k + 1)], color)
                if not solid(i, j + 1, k):          # +Y wall
                    M.add_face([point(i, j + 1, k), point(i, j + 1, k + 1),
                                point(i + 1, j + 1, k + 1), point(i + 1, j + 1, k)], color)
                if not solid(i, j, k - 1):          # -Z wall
                    M.add_face([point(i, j, k), point(i, j + 1, k),
                                point(i + 1, j + 1, k), point(i + 1, j, k)], color)
                if not solid(i, j, k + 1):          # +Z wall
                    M.add_face([point(i, j, k + 1), point(i + 1, j, k + 1),
                                point(i + 1, j + 1, k + 1), point(i, j + 1, k + 1)], color)
    return M


def _emit(M, tol=1e-9):
    """Add a freshly built primitive to the scene, welding its seams first.

    Shapes are assembled from several patches (a wall plus two lids, say) and
    each patch generates its own copy of the shared rim.  Welding here means
    every primitive leaves the factory watertight.
    """
    _weld(M, tol)
    _scene.extend(M)


# ============================================================================
#  5. Flat shapes
# ============================================================================

def polygon(points, color=None):
    """One flat face through the given 3D points (any number of corners).

    The corners must be listed counter-clockwise as seen from the side you
    want to be the outside.
    """
    _scene.add_polygon(points, color)


def triangle(a, b, c, color=None):
    """A single triangle."""
    _scene.add_polygon([a, b, c], color)


def quad(a, b, c, d, color=None):
    """A single quadrilateral."""
    _scene.add_polygon([a, b, c, d], color)


def disc(center, normal, r, k=32, color=None):
    """A filled circle of radius ``r`` at ``center``, facing ``normal``.

    ``normal`` may be given either as a direction or as a second point --
    ``disc(A, B, ...)`` puts the disc at ``A`` facing ``B``, which is how the
    old :func:`circle` worked.
    """
    d = _sub(normal, center)
    if _norm(d) < EPS:
        d = normal
    u, v, w = _frame(d)
    M = Mesh()
    _fan(M, _ring(center, u, v, r, k), center, rgb(color))
    _scene.extend(M)


def ring(center, normal, r_outer, r_inner, k=32, color=None):
    """A flat annulus (a disc with a hole)."""
    d = _sub(normal, center)
    if _norm(d) < EPS:
        d = normal
    u, v, w = _frame(d)
    outer = _ring(center, u, v, r_outer, k)
    inner = _ring(center, u, v, r_inner, k)
    M = Mesh()
    _add_grid(M, [inner, outer], rgb(color), wrap_v=True)
    _scene.extend(M)


def grid(center, size, nx=10, nz=10, color=None, height=None, thickness=0.0):
    """A flat (or, with ``height(x, z)``, a hilly) rectangular patch in XZ.

    ``size`` is ``[width_x, depth_z]``.  ``height`` is an optional function
    returning the Y coordinate, and ``color`` may be a function ``(x, z)`` so
    that a landscape can be painted by position or by height::

        add.grid([0, 0, 0], [10, 10], 40, 40,
                 color=lambda x, z: "sky" if hills(x, z) < 0 else "green",
                 height=hills)

    ``thickness`` turns the sheet into a solid slab (see :func:`solidify`).
    """
    w, d = size[0], size[1]
    P = []
    xs, zs = [], []
    for i in range(nx + 1):
        row = []
        x = center[0] - w / 2.0 + w * i / nx
        xs.append(x)
        for j in range(nz + 1):
            z = center[2] - d / 2.0 + d * j / nz
            if i == 0:
                zs.append(z)
            y = center[1]
            if height is not None:
                y = center[1] + height(x, z)
            row.append((x, y, z))
        P.append(row)
    paint = color
    if callable(color):
        def paint(i, j):
            return color((xs[i] + xs[i + 1]) / 2.0, (zs[j] + zs[j + 1]) / 2.0)
    M = Mesh()
    _add_grid(M, P, paint, flip=True)
    if thickness:
        M = solidify(M, thickness)
    _scene.extend(M)


# ============================================================================
#  6. Boxes and other flat-sided solids
# ============================================================================

def box(center, edge, color=None):
    """A cube of side ``edge`` centred at ``center``."""
    cuboid(center, [edge, edge, edge], color)


def cuboid(center, sizes, color=None):
    """A rectangular block; ``sizes`` are the edge lengths along X, Y and Z."""
    ex, ey, ez = sizes[0], sizes[1], sizes[2]
    x0, y0, z0 = center[0] - ex / 2.0, center[1] - ey / 2.0, center[2] - ez / 2.0
    x1, y1, z1 = x0 + ex, y0 + ey, z0 + ez
    P = [(x0, y0, z0), (x0, y0, z1), (x0, y1, z0), (x0, y1, z1),
         (x1, y0, z0), (x1, y0, z1), (x1, y1, z0), (x1, y1, z1)]
    F = [[0, 4, 5, 1], [0, 1, 3, 2], [0, 2, 6, 4],
         [1, 5, 7, 3], [2, 3, 7, 6], [4, 6, 7, 5]]
    base = len(_scene.V)
    color = rgb(color)
    for f in F:
        _scene.add_face([base + i for i in f], color)
    for p in P:
        _scene.add_vertex(p)


def frame(center, edge, thickness, color=None):
    """The twelve edges of a cube -- a hollow cube frame.

    ``thickness`` is how thick each bar is.  Built as a 3x3x3 grid of cells
    in which a cell is material when at least two of its three indices lie on
    the outside; the whole shape therefore comes out watertight.
    """
    e, b = float(edge), float(thickness)
    mid = e - 2 * b
    sizes = [b, mid, b]
    origin = (center[0] - e / 2.0, center[1] - e / 2.0, center[2] - e / 2.0)

    def filled(i, j, k):
        return (i != 1) + (j != 1) + (k != 1) >= 2

    _scene.extend(_grid_solid(origin, sizes, sizes, sizes, filled, color))


def voxels(cells, size=1.0, origin=(0, 0, 0), color=None):
    """Build the surface of a set of unit cells -- a Minecraft-style model.

    ``cells`` is any container of ``(i, j, k)`` integer triples::

        blocks = {(x, y, z) for x in range(5) for y in range(3)
                            for z in range(5) if (x + y + z) % 3}
        add.voxels(blocks, 0.5, color="sky")
    """
    cells = set(tuple(c) for c in cells)
    if not cells:
        return
    lo = [min(c[a] for c in cells) for a in range(3)]
    hi = [max(c[a] for c in cells) for a in range(3)]
    n = [hi[a] - lo[a] + 1 for a in range(3)]
    start = (origin[0] + lo[0] * size, origin[1] + lo[1] * size,
             origin[2] + lo[2] * size)

    def filled(i, j, k):
        return (i + lo[0], j + lo[1], k + lo[2]) in cells

    _scene.extend(_grid_solid(start, [size] * n[0], [size] * n[1],
                              [size] * n[2], filled, color))


def pyramid(center, edge, height, color=None):
    """A square pyramid: base of side ``edge``, apex ``height`` above it.

    A negative ``height`` points the pyramid downwards.
    """
    e, h = float(edge), float(height)
    x, y, z = center[0] - e / 2.0, center[1] - e / 2.0, center[2] - e / 2.0
    base = [(x, y, z), (x + e, y, z), (x + e, y, z + e), (x, y, z + e)]
    apex = (x + e / 2.0, y + h, z + e / 2.0)
    M = Mesh()
    first = 0
    M.add_polygon(base[::-1], color)
    _fan(M, base, apex, rgb(color))
    _weld(M, 1e-9)
    _make_outward(M, first)
    _scene.extend(M)


def prism(profile, height, color=None, center=(0, 0, 0), axis=(0, 1, 0)):
    """A solid with a constant cross-section: a 2D ``profile`` given a depth.

    ``profile`` is a list of ``[x, y]`` points in the cross-section plane,
    listed counter-clockwise.  The result is centred on ``center`` and
    extruded along ``axis``::

        add.prism([[0, 0], [1, 0], [0.5, 1]], 3, "gold")   # triangular bar
    """
    u, v, w = _frame(axis)
    half = _scale(w, height / 2.0)
    bottom = []
    top = []
    for p in profile:
        q = (center[0] + u[0] * p[0] + v[0] * p[1],
             center[1] + u[1] * p[0] + v[1] * p[1],
             center[2] + u[2] * p[0] + v[2] * p[1])
        bottom.append(_sub(q, half))
        top.append(_add3(q, half))
    M = Mesh()
    _add_grid(M, [bottom, top], rgb(color), wrap_v=True, flip=True)
    M.add_polygon(bottom[::-1], color)
    M.add_polygon(top, color)
    _weld(M, 1e-9)
    _make_outward(M, 0)
    _scene.extend(M)


# ============================================================================
#  7. The five regular polyhedra (Platonic solids)
# ============================================================================
# Each solid is stored with its centre at the origin, so the average of its
# vertex coordinates is exactly [0, 0, 0]; ``polyhedron`` then scales it to
# the circumscribed radius ``r`` and shifts it to ``center``.  The face tables
# are wound counter-clockwise seen from outside.

def polyhedron(name, center=(0, 0, 0), r=1.0, color=None):
    """One of the five Platonic solids, inscribed in a sphere of radius ``r``.

    ``name`` is ``"tetrahedron"``, ``"cube"``, ``"octahedron"``,
    ``"dodecahedron"`` or ``"icosahedron"``.  ``r`` is the distance from the
    centre to every vertex.  The same solids also have functions of their
    own (:func:`tetrahedron` ... :func:`icosahedron`), and
    :func:`polyhedron_points` gives just the vertex coordinates::

        add.polyhedron("dodecahedron", [0, 0, 0], 2, "gold")
    """
    V, F = _platonic(name)
    scale = r / _norm(V[0])
    base = len(_scene.V)
    color = rgb(color)
    for p in V:
        _scene.add_vertex((center[0] + p[0] * scale,
                           center[1] + p[1] * scale,
                           center[2] + p[2] * scale))
    first = len(_scene.F)
    for f in F:
        _scene.add_face([base + i for i in f], color)
    _make_outward(_scene, first)


def tetrahedron(center=(0, 0, 0), r=1.0, color=None):
    """A regular tetrahedron: 4 vertices, 4 triangles, circumradius ``r``."""
    polyhedron("tetrahedron", center, r, color)


def octahedron(center=(0, 0, 0), r=1.0, color=None):
    """A regular octahedron: 6 vertices, 8 triangles, circumradius ``r``."""
    polyhedron("octahedron", center, r, color)


def dodecahedron(center=(0, 0, 0), r=1.0, color=None):
    """A regular dodecahedron: 20 vertices, 12 pentagons, circumradius ``r``."""
    polyhedron("dodecahedron", center, r, color)


def icosahedron(center=(0, 0, 0), r=1.0, color=None):
    """A regular icosahedron: 12 vertices, 20 triangles, circumradius ``r``.

    Its vertices are the natural starting point for a geodesic sphere
    (:func:`sphere`), a football (:func:`truncate`) or anything with
    twelve equally spread directions -- see :func:`polyhedron_points`.
    """
    polyhedron("icosahedron", center, r, color)


def polyhedron_points(name, center=(0, 0, 0), r=1.0):
    """The vertex coordinates of a Platonic solid, as a list of points.

    The average of the points is exactly ``center``.  Use them to place
    things evenly around a point -- twelve spikes on an icosahedron, say::

        for p in add.polyhedron_points("icosahedron", [0, 0, 0], 2):
            add.cone([0, 0, 0], p, 0.3, 12, "red")
    """
    V, F = _platonic(name)
    scale = r / _norm(V[0])
    return [[center[0] + p[0] * scale, center[1] + p[1] * scale,
             center[2] + p[2] * scale] for p in V]


def polyhedron_faces(name):
    """The face table of a Platonic solid: lists of indices into
    :func:`polyhedron_points`, counter-clockwise seen from outside."""
    return [list(f) for f in _platonic(name)[1]]


def _platonic(name):
    """Vertex and face tables for the five Platonic solids (centred at 0)."""
    name = name.lower()
    if name in ("tetrahedron", "tetra"):
        V = [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]
        F = [[0, 1, 2], [0, 3, 1], [0, 2, 3], [1, 3, 2]]
        return V, F
    if name in ("cube", "hexahedron", "box"):
        V = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
        F = [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1],
             [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]]
        return V, F
    if name in ("octahedron", "octa"):
        V = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
        F = [[0, 2, 4], [2, 1, 4], [1, 3, 4], [3, 0, 4],
             [2, 0, 5], [1, 2, 5], [3, 1, 5], [0, 3, 5]]
        return V, F
    phi = (1 + math.sqrt(5)) / 2
    if name in ("icosahedron", "icosa"):
        # The classic table: three golden rectangles, 20 triangles listed
        # counter-clockwise from outside (the same one the geodesic sphere
        # starts from).
        V = [(-1, phi, 0), (1, phi, 0), (-1, -phi, 0), (1, -phi, 0),
             (0, -1, phi), (0, 1, phi), (0, -1, -phi), (0, 1, -phi),
             (phi, 0, -1), (phi, 0, 1), (-phi, 0, -1), (-phi, 0, 1)]
        F = [[0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
             [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
             [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
             [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]]
        return V, F
    if name in ("dodecahedron", "dodeca"):
        V = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
        inv = 1.0 / phi
        for s1 in (-1, 1):
            for s2 in (-1, 1):
                V += [(0, s1 * inv, s2 * phi), (s1 * inv, s2 * phi, 0),
                      (s1 * phi, 0, s2 * inv)]
        F = _hull_faces(V, 5)
        return V, F
    raise ValueError("unknown polyhedron: %r" % name)


def _hull_faces(V, sides):
    """Faces of a convex point set: every plane with all points on one side.

    Small and slow (it tries all vertex triples) but the Platonic solids have
    at most 20 vertices, and it keeps the vertex tables above honest.
    """
    n = len(V)
    found = {}
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                nrm = _cross(_sub(V[j], V[i]), _sub(V[k], V[i]))
                if _norm(nrm) < 1e-9:
                    continue
                nrm = _unit(nrm)
                d = _dot(nrm, V[i])
                if d < 1e-9:
                    nrm, d = _scale(nrm, -1), -d
                if d <= 1e-9:
                    continue
                if any(_dot(nrm, p) > d + 1e-9 for p in V):
                    continue
                on = [t for t in range(n) if abs(_dot(nrm, V[t]) - d) < 1e-9]
                if len(on) != sides:
                    continue
                key = tuple(sorted(on))
                if key in found:
                    continue
                # Sort the coplanar points into a proper ring.
                centre = [sum(V[t][a] for t in on) / len(on) for a in range(3)]
                u = _unit(_sub(V[on[0]], centre))
                v = _cross(nrm, u)
                on.sort(key=lambda t: math.atan2(
                    _dot(_sub(V[t], centre), v), _dot(_sub(V[t], centre), u)))
                found[key] = on
    return list(found.values())


# ============================================================================
#  8. Numbers, points and 2D profiles
# ============================================================================
# Small helpers that models need all the time: blend two values, keep a
# number in range, measure a distance, turn a point, cut the corners of a
# path, and ready-made cross-sections for ``extrude`` / ``sweep`` / ``prism``.

def lerp(a, b, t):
    """Blend from ``a`` (``t = 0``) to ``b`` (``t = 1``).

    Works for numbers and for points: ``lerp([0, 0, 0], [4, 2, 0], 0.5)``
    is ``[2, 1, 0]``.
    """
    if isinstance(a, (int, float)):
        return a + (b - a) * t
    return [a[i] + (b[i] - a[i]) * t for i in range(len(a))]


def clamp(x, lo=0.0, hi=1.0):
    """``x`` limited to the range ``lo .. hi``."""
    return lo if x < lo else (hi if x > hi else x)


def remap(x, a0, a1, b0, b1):
    """Map ``x`` from the range ``a0..a1`` onto the range ``b0..b1``.

    ``remap(t, 0, 10, -1, 1)`` turns a time 0..10 into -1..1.
    """
    if abs(a1 - a0) < EPS:
        return b0
    return b0 + (b1 - b0) * (x - a0) / float(a1 - a0)


def distance(a, b):
    """Distance between two points (2D or 3D)."""
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(len(a))))


def midpoint(a, b):
    """The point half way between ``a`` and ``b``."""
    return [(a[i] + b[i]) / 2.0 for i in range(len(a))]


def direction(a, b):
    """The unit vector pointing from ``a`` to ``b``."""
    d = [b[i] - a[i] for i in range(len(a))]
    n = math.sqrt(sum(c * c for c in d))
    return d if n < EPS else [c / n for c in d]


def rotate_point(p, axis, angle, P=(0, 0, 0)):
    """Turn a single point around an axis through ``P`` (Rodrigues).

    The same rotation :func:`rotate` applies to a whole mesh -- use it to
    aim a turret, place a hand on a clock or compute where a part will end
    up before building it::

        tip = add.rotate_point([3, 0, 0], [0, 1, 0], angle, pivot)
    """
    k = _unit(axis)
    cs, sn = math.cos(angle), math.sin(angle)
    v = _sub(p, P)
    kv = _cross(k, v)
    d = _dot(k, v) * (1.0 - cs)
    return [P[0] + v[0] * cs + kv[0] * sn + k[0] * d,
            P[1] + v[1] * cs + kv[1] * sn + k[1] * d,
            P[2] + v[2] * cs + kv[2] * sn + k[2] * d]


def shade(color, factor):
    """A darker (``factor < 1``) or lighter (``factor > 1``) version of a colour.

    ``shade("red", 0.5)`` is dark red; ``shade("red", 1.5)`` is pink-ish.
    """
    r, g, b = rgb(color)
    if factor <= 1.0:
        return (int(r * factor), int(g * factor), int(b * factor))
    t = min(1.0, factor - 1.0)
    return (int(r + (255 - r) * t), int(g + (255 - g) * t), int(b + (255 - b) * t))


def chaikin(points, rounds=2, closed=False):
    """Round the corners of a polyline by cutting them (Chaikin's algorithm).

    Every round replaces each corner by two points at 1/4 and 3/4 of its
    edges, so a square becomes an octagon, then a 16-gon, and quickly a
    circle.  Works for 2D and 3D points.  Use it to smooth a hand-drawn
    path before :func:`polyline` or :func:`sweep`.
    """
    pts = [list(p) for p in points]
    for _ in range(rounds):
        n = len(pts)
        out = []
        pairs = range(n) if closed else range(n - 1)
        for i in pairs:
            a, b = pts[i], pts[(i + 1) % n]
            out.append([a[j] * 0.75 + b[j] * 0.25 for j in range(len(a))])
            out.append([a[j] * 0.25 + b[j] * 0.75 for j in range(len(a))])
        if not closed:
            out = [pts[0]] + out + [pts[-1]]
        pts = out
    return pts


# -- 2D cross-sections -------------------------------------------------------
# All profiles are lists of [x, y] points listed counter-clockwise, ready for
# ``extrude``, ``sweep``, ``prism`` and ``loft``.

def profile_circle(r, k=32, phase=0.0):
    """``k`` points on a circle of radius ``r``."""
    return [[r * math.cos(phase + 2 * math.pi * i / k),
             r * math.sin(phase + 2 * math.pi * i / k)] for i in range(k)]


def profile_ellipse(a, b, k=32):
    """``k`` points on an ellipse with half-axes ``a`` and ``b``."""
    return [[a * math.cos(2 * math.pi * i / k), b * math.sin(2 * math.pi * i / k)]
            for i in range(k)]


def profile_polygon(n, r, phase=None):
    """A regular ``n``-gon with circumradius ``r`` (a flat side at the bottom)."""
    if phase is None:
        phase = -math.pi / 2.0 + math.pi / n
    return profile_circle(r, n, phase)


def profile_star(n, r_outer, r_inner, phase=None):
    """A star with ``n`` points, alternating between the two radii."""
    if phase is None:
        phase = math.pi / 2.0
    pts = []
    for i in range(2 * n):
        r = r_outer if i % 2 == 0 else r_inner
        a = phase + math.pi * i / n
        pts.append([r * math.cos(a), r * math.sin(a)])
    return pts


def profile_rect(w, h, r=0.0, k=4):
    """A ``w`` by ``h`` rectangle, with corners rounded by ``r`` if given."""
    x, y = w / 2.0, h / 2.0
    if r <= EPS:
        return [[-x, -y], [x, -y], [x, y], [-x, y]]
    r = min(r, x, y)
    pts = []
    corners = [(x - r, y - r, 0.0), (-x + r, y - r, math.pi / 2),
               (-x + r, -y + r, math.pi), (x - r, -y + r, 3 * math.pi / 2)]
    for cx, cy, a0 in corners:
        for i in range(k + 1):
            a = a0 + (math.pi / 2) * i / k
            pts.append([cx + r * math.cos(a), cy + r * math.sin(a)])
    return pts


def profile_gear(teeth, r, depth=None, k=2):
    """The outline of a gear: ``teeth`` teeth of height ``depth`` on radius ``r``.

    The result is a closed profile; ``add.prism(profile, thickness)`` makes
    the wheel and :func:`gear` does that for you.
    """
    if depth is None:
        depth = r * 0.2
    pts = []
    n = 4 * teeth
    for i in range(n):
        phase = i % 4
        a = 2 * math.pi * i / n
        if phase in (1, 2):
            rr = r + depth / 2.0
        else:
            rr = r - depth / 2.0
        pts.append([rr * math.cos(a), rr * math.sin(a)])
    return pts


# -- points to put things on ------------------------------------------------

def points_on_line(a, b, n):
    """``n`` points evenly spaced from ``a`` to ``b`` (both included)."""
    if n <= 1:
        return [list(a)]
    return [lerp(a, b, i / float(n - 1)) for i in range(n)]


def points_on_circle(center, r, n, axis=(0, 1, 0), phase=0.0):
    """``n`` points spread evenly on a circle in the plane normal to ``axis``."""
    u, v, w = _frame(axis)
    return [list(p) for p in _ring(center, u, v, r, n, phase)]


def points_on_helix(center, r, pitch, turns, n, axis=(0, 1, 0)):
    """``n`` points along a helix of ``turns`` turns climbing ``pitch`` per turn."""
    u, v, w = _frame(axis)
    out = []
    for i in range(n):
        t = turns * i / float(max(1, n - 1))
        a = 2 * math.pi * t
        out.append([center[j] + (u[j] * math.cos(a) + v[j] * math.sin(a)) * r
                    + w[j] * pitch * t for j in range(3)])
    return out


def points_on_spiral(center, r0, r1, turns, n, axis=(0, 1, 0), rise=0.0):
    """``n`` points along a flat spiral whose radius grows from ``r0`` to ``r1``.

    ``rise`` lifts the spiral along ``axis`` as it goes -- a vortex of beads
    or a spiral staircase in one call.
    """
    u, v, w = _frame(axis)
    out = []
    for i in range(n):
        t = i / float(max(1, n - 1))
        a = 2 * math.pi * turns * t
        r = r0 + (r1 - r0) * t
        out.append([center[j] + (u[j] * math.cos(a) + v[j] * math.sin(a)) * r
                    + w[j] * rise * t for j in range(3)])
    return out


def points_on_curve(path, t0, t1, n, closed=False):
    """``n`` points ``path(t)`` for ``t`` evenly spread over ``t0 .. t1``."""
    steps = n if closed else max(1, n - 1)
    return [list(path(t0 + (t1 - t0) * i / float(steps))) for i in range(n)]


# ============================================================================
#  9. Round solids
# ============================================================================

def _revolve_grid(A, direction, profile, k, angle=2.0 * math.pi, phase=0.0):
    """Points of a surface of revolution.

    ``profile`` is a list of ``(radius, height)`` pairs; ``height`` is measured
    along ``direction`` from ``A``.  Returns the ``P[i][j]`` grid that
    :func:`_add_grid` expects.
    """
    u, v, w = _frame(direction)
    closed = abs(angle - 2.0 * math.pi) < 1e-12
    steps = k if closed else k + 1
    cs = []
    for j in range(steps):
        a = phase + angle * (j / float(k))
        cs.append((math.cos(a), math.sin(a)))
    P = []
    for r, h in profile:
        centre = _add3(A, _scale(w, h))
        row = []
        for c, s in cs:
            row.append((centre[0] + u[0] * r * c + v[0] * r * s,
                        centre[1] + u[1] * r * c + v[1] * r * s,
                        centre[2] + u[2] * r * c + v[2] * r * s))
        P.append(row)
    return P, closed


def revolve(profile, A=(0, 0, 0), B=(0, 1, 0), t0=0.0, t1=1.0, steps=40,
            k=32, color=None, angle=2.0 * math.pi, caps=True):
    """Spin a 2D profile around the axis ``A -> B`` (a lathe).

    ``profile(t)`` returns ``[radius, height]``, where *height* is the
    distance from ``A`` along the axis.  ``steps`` is the detail along the
    profile, ``k`` the detail around the axis.  Set ``angle`` to less than a
    full turn to leave a wedge cut out of the shape.

    With ``caps=True`` (the default) the ends are closed, so the lathe gives
    you a solid ready for a boolean operation; ``caps=False`` leaves the bare
    shell, which is what the old ``spin3D`` produced::

        def vase(t):
            return [1 + 0.4 * add.sin(3 * t), t]
        add.revolve(vase, [0, 0, 0], [0, 1, 0], 0, 4, 60, 40, "teal")

    ``color`` may also be a function ``color(t, a)`` of the profile
    parameter and the angle around the axis (in radians), evaluated at the
    middle of every cell -- stripes, spirals and gradients in one line::

        add.revolve(vase, [0, 0, 0], [0, 1, 0], 0, 4, 60, 40,
                    color=lambda t, a: add.hsv(t / 4.0))
    """
    pts = []
    for i in range(steps + 1):
        t = t0 + (t1 - t0) * i / float(steps)
        g = profile(t)
        pts.append((g[0], g[1]))
    direction = _sub(B, A)
    P, closed = _revolve_grid(A, direction, pts, k, angle)
    if callable(color):
        fn = color

        def color(i, j):                      # cell (i, j) -> (t, angle)
            t = t0 + (t1 - t0) * (i + 0.5) / float(steps)
            return fn(t, angle * (j + 0.5) / float(k))
        lid_a = lambda j: fn(t0, angle * (j + 0.5) / float(k))   # noqa: E731
        lid_b = lambda j: fn(t1, angle * (j + 0.5) / float(k))   # noqa: E731
        side_a, side_b = fn((t0 + t1) / 2.0, 0.0), fn((t0 + t1) / 2.0, angle)
    else:
        color = rgb(color)
        lid_a = lid_b = side_a = side_b = color
    M = Mesh()
    _add_grid(M, P, color, wrap_v=closed, flip=True)
    if caps:
        w = _unit(direction)
        first = _add3(A, _scale(w, pts[0][1]))
        last = _add3(A, _scale(w, pts[-1][1]))
        if pts[0][0] > EPS:                       # flat lid at the start
            _fan(M, P[0], first, lid_a, flip=True, closed=closed)
        if pts[-1][0] > EPS:                      # flat lid at the end
            _fan(M, P[-1], last, lid_b, closed=closed)
        if not closed:                            # the two sides of the wedge
            M.add_polygon([row[0] for row in P] + [last, first], side_a)
            M.add_polygon([row[-1] for row in P] + [last, first], side_b)
        _weld(M, 1e-9)
        _drop_degenerate(M)
        if not closed:
            M = fix_normals(M)
        _make_outward(M, 0)          # whichever way the profile was drawn
    _emit(M)


def spin3D(A, B, S, min_t, max_t, grid_t, k, RGB):
    """add.py 1.2 lathe: spin curve ``S(t) = [radius, height]`` around A->B."""
    revolve(S, A, B, min_t, max_t, grid_t, k, RGB, caps=False)


def _icosphere_grid(subdivisions):
    """Unit geodesic sphere: vertex list and triangle list.

    Start from the icosahedron, then ``subdivisions`` times split every
    triangle into four by its edge midpoints and push the new points out
    onto the sphere -- the principle of an observatory dome.  Midpoints are
    shared through a dictionary, so neighbouring triangles use the same
    vertex and the mesh is watertight: 12, 42, 162, 642 ... vertices and
    20, 80, 320, 1280 ... triangles.
    """
    V, T = _platonic("icosahedron")
    V = [list(_unit(p)) for p in V]
    T = [tuple(f) for f in T]
    for _ in range(int(subdivisions)):
        mid = {}

        def midpoint_index(a, b):
            key = (a, b) if a < b else (b, a)
            if key not in mid:
                m = _unit(((V[a][0] + V[b][0]) * 0.5,
                           (V[a][1] + V[b][1]) * 0.5,
                           (V[a][2] + V[b][2]) * 0.5))
                mid[key] = len(V)
                V.append(list(m))
            return mid[key]

        new = []
        for a, b, c in T:
            ab, bc, ca = midpoint_index(a, b), midpoint_index(b, c), \
                midpoint_index(c, a)
            new += [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
        T = new
    return V, T


def icosphere(center, r, subdivisions=3, color=None):
    """A geodesic sphere: an icosahedron whose triangles are split and
    pushed out onto the sphere ``subdivisions`` times (0..7).

    Every face is a triangle and all of them are nearly the same size, which
    is why domes and 3D printers like it.  The face count is
    ``20 * 4 ** subdivisions``: 20, 80, 320, 1280, 5120, 20480 ...
    ``color`` may be a function of the face's direction from the centre
    (a unit vector), so a globe is one line::

        add.icosphere([0, 0, 0], 2, 4, lambda d: "white" if d[1] > 0.7 else "blue")
    """
    level = int(subdivisions)
    level = 0 if level < 0 else (7 if level > 7 else level)
    V, T = _icosphere_grid(level)
    M = Mesh()
    for p in V:
        M.add_vertex((center[0] + p[0] * r, center[1] + p[1] * r,
                      center[2] + p[2] * r))
    if callable(color):
        for a, b, c in T:
            d = _unit((V[a][0] + V[b][0] + V[c][0], V[a][1] + V[b][1] + V[c][1],
                       V[a][2] + V[b][2] + V[c][2]))
            M.add_face((a, b, c), rgb(color(d)))
    else:
        color = rgb(color)
        for f in T:
            M.add_face(f, color)
    _scene.extend(M)


def sphere(center, r, k=10, color=None, subdivisions=None):
    """A sphere built from triangles -- the geodesic dome of an observatory.

    The icosahedron's 20 triangles are split into four again and again and
    every new vertex is pushed out onto the sphere, so all the triangles are
    nearly equal.  ``k`` is the detail number add.py has always taken
    (``k=10`` is fine for a marble, ``k=30`` for a planet); it picks the
    number of splits so that the face count stays close to the old
    ``6*k*k``: k=5 gives 320 triangles, k=10 1280, k=20 5120, k=40 20480.
    Pass ``subdivisions=`` (0..7) to choose the level directly, and see
    :func:`icosphere` for painting by direction.  The older six-patch
    sphere of quads is still there as :func:`quadsphere`::

        add.sphere([0, 0, 0], 1.5, 20, "sky")
    """
    if subdivisions is None:
        k = max(1, int(k))
        subdivisions = int(round(math.log(2.0 * k / 3.0, 2))) if k > 1 else 0
    icosphere(center, r, subdivisions, color)


def quadsphere(center, r, k=10, color=None):
    """A sphere built from six curved square patches (all faces are quads).

    ``k`` is the number of cells along the side of each patch, so the sphere
    has ``6 * k * k`` faces.  The quads stay nearly square everywhere.  This
    was add.py's ``sphere`` up to version 1.2; it is also exactly the
    "Minecraft sphere" construction of a cube blown up into a ball, and the
    quad layout suits :func:`smooth` and :func:`catmull_clark`.
    """
    ellipsoid(center, [r, r, r], k, color)


def ellipsoid(center, radii, k=10, color=None):
    """Like :func:`quadsphere` but with a separate radius for X, Y and Z."""
    if not isinstance(radii, (list, tuple)):
        radii = [radii, radii, radii]
    sides = [((1, 0, 0), (0, 1, 0), (0, 0, 1)),
             ((-1, 0, 0), (0, 0, 1), (0, 1, 0)),
             ((0, 1, 0), (0, 0, 1), (1, 0, 0)),
             ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
             ((0, 0, 1), (1, 0, 0), (0, 1, 0)),
             ((0, 0, -1), (0, 1, 0), (1, 0, 0))]
    # Spreading the samples with tan() keeps the cells the same size.
    warp = [math.tan(math.pi / 4.0 * (2.0 * i / k - 1.0)) for i in range(k + 1)]
    M = Mesh()
    color = rgb(color)
    for n, u, v in sides:
        P = []
        for a in warp:
            row = []
            for b in warp:
                p = _unit((n[0] + u[0] * a + v[0] * b,
                           n[1] + u[1] * a + v[1] * b,
                           n[2] + u[2] * a + v[2] * b))
                row.append((center[0] + p[0] * radii[0],
                            center[1] + p[1] * radii[1],
                            center[2] + p[2] * radii[2]))
            P.append(row)
        _add_grid(M, P, color)
    _weld(M, 1e-9)
    _scene.extend(M)


def uvsphere(center, r, nu=32, nv=16, color=None):
    """A globe-style sphere: ``nu`` meridians by ``nv`` parallels."""
    def profile(t):
        return [r * math.sin(t), r * math.cos(t)]
    P, _ = _revolve_grid((center[0], center[1] - r, center[2]), (0, 1, 0),
                         [(r * math.sin(math.pi * i / nv),
                           r - r * math.cos(math.pi * i / nv))
                          for i in range(nv + 1)], nu)
    M = Mesh()
    _add_grid(M, P, rgb(color), wrap_v=True, flip=True)
    _weld(M, 1e-9)
    _drop_degenerate(M)
    _scene.extend(M)


def torus(center, R, r, nu=48, nv=24, color=None, axis=(0, 1, 0)):
    """A doughnut: tube radius ``r`` swept round a circle of radius ``R``."""
    u, v, w = _frame(axis)
    P = []
    for i in range(nu):
        a = 2.0 * math.pi * i / nu
        ring_centre = (center[0] + (u[0] * math.cos(a) + v[0] * math.sin(a)) * R,
                       center[1] + (u[1] * math.cos(a) + v[1] * math.sin(a)) * R,
                       center[2] + (u[2] * math.cos(a) + v[2] * math.sin(a)) * R)
        out = (u[0] * math.cos(a) + v[0] * math.sin(a),
               u[1] * math.cos(a) + v[1] * math.sin(a),
               u[2] * math.cos(a) + v[2] * math.sin(a))
        row = []
        for j in range(nv):
            b = 2.0 * math.pi * j / nv
            cb, sb = math.cos(b) * r, math.sin(b) * r
            row.append((ring_centre[0] + out[0] * cb + w[0] * sb,
                        ring_centre[1] + out[1] * cb + w[1] * sb,
                        ring_centre[2] + out[2] * cb + w[2] * sb))
        P.append(row)
    M = Mesh()
    _add_grid(M, P, rgb(color), wrap_u=True, wrap_v=True)
    _make_outward(M, 0)
    _scene.extend(M)


def _tube_body(A, B, r1, r2, k, color, cap_a, cap_b):
    """Shared engine behind cylinder / cone / frustum and their variants."""
    d = _sub(B, A)
    if _norm(d) < EPS:
        return Mesh()
    u, v, w = _frame(d)
    M = Mesh()
    color = rgb(color)
    ring_a = _ring(A, u, v, r1, k)
    ring_b = _ring(B, u, v, r2, k)
    if r1 < EPS:                       # cone standing on its point
        _fan(M, ring_b, A, color, flip=True)
    elif r2 < EPS:                     # cone with the point at B
        _fan(M, ring_a, B, color)
    else:
        _add_grid(M, [ring_a, ring_b], color, wrap_v=True, flip=True)
    if cap_a and r1 >= EPS:
        _fan(M, ring_a, A, color, flip=True)
    if cap_b and r2 >= EPS:
        _fan(M, ring_b, B, color)
    _weld(M, 1e-9)
    return M


def cylinder(A, B, r, k=24, color=None):
    """A closed cylinder from ``A`` to ``B``, radius ``r``, ``k`` sides."""
    _scene.extend(_tube_body(A, B, r, r, k, color, True, True))


def tube(A, B, r, k=24, color=None):
    """A cylinder with no lids -- just the side wall (old ``cylinder2``)."""
    _scene.extend(_tube_body(A, B, r, r, k, color, False, False))


def cup(A, B, r, k=24, color=None):
    """A cylinder closed at ``A`` only (old ``cylinder3``)."""
    _scene.extend(_tube_body(A, B, r, r, k, color, True, False))


def cone(A, B, r, k=24, color=None):
    """A closed cone: circular base of radius ``r`` at ``A``, tip at ``B``."""
    _scene.extend(_tube_body(A, B, r, 0.0, k, color, True, False))


def cone_open(A, B, r, k=24, color=None):
    """Only the slanted wall of a cone (old ``cone2``)."""
    _scene.extend(_tube_body(A, B, r, 0.0, k, color, False, False))


def frustum(A, B, r1, r2, k=24, color=None, caps=True):
    """A cone with its tip cut off: radius ``r1`` at ``A``, ``r2`` at ``B``."""
    _scene.extend(_tube_body(A, B, r1, r2, k, color, caps, caps))


def pipe(A, B, r_outer, r_inner, k=24, color=None):
    """A hollow tube -- a cylinder with a cylindrical hole down the middle."""
    d = _sub(B, A)
    u, v, w = _frame(d)
    M = Mesh()
    color = rgb(color)
    oa, ob = _ring(A, u, v, r_outer, k), _ring(B, u, v, r_outer, k)
    ia, ib = _ring(A, u, v, r_inner, k), _ring(B, u, v, r_inner, k)
    _add_grid(M, [oa, ob], color, wrap_v=True, flip=True)     # outside
    _add_grid(M, [ia, ib], color, wrap_v=True)                # inside
    _add_grid(M, [ia, oa], color, wrap_v=True, flip=True)     # ring at A
    _add_grid(M, [ib, ob], color, wrap_v=True)                # ring at B
    _emit(M)


def capsule(A, B, r, k=24, color=None):
    """A cylinder with a hemisphere on each end (a "pill")."""
    d = _sub(B, A)
    length = _norm(d)
    n = max(3, k // 3)
    profile = []
    for i in range(n + 1):                       # lower hemisphere
        a = math.pi / 2 * i / n
        profile.append((r * math.sin(a), r - r * math.cos(a)))
    for i in range(n + 1):                       # upper hemisphere
        a = math.pi / 2 * i / n
        profile.append((r * math.cos(a), r + length + r * math.sin(a)))
    start = _add3(A, _scale(_unit(d), -r))
    P, _ = _revolve_grid(start, d, [(p[0], p[1]) for p in profile], k)
    M = Mesh()
    _add_grid(M, P, rgb(color), wrap_v=True, flip=True)
    _weld(M, 1e-9)
    _drop_degenerate(M)
    _make_outward(M, 0)
    _scene.extend(M)


def arrow(A, B, r=0.05, color=None, k=16, head=0.25):
    """A shaft from ``A`` to ``B`` with a cone head -- good for vectors.

    ``head`` is the fraction of the length taken by the arrowhead.
    """
    d = _sub(B, A)
    n = _norm(d)
    if n < EPS:
        return
    joint = _add3(A, _scale(d, 1.0 - head))
    cylinder(A, joint, r, k, color)
    cone(joint, B, r * 2.4, k, color)


def helix(center, r, pitch, turns, k=200, thickness=0.1, sides=12, color=None,
          axis=(0, 1, 0)):
    """A spring / helical tube of ``turns`` turns around ``axis``."""
    u, v, w = _frame(axis)

    def path(t):
        a = 2.0 * math.pi * t
        return (center[0] + (u[0] * math.cos(a) + v[0] * math.sin(a)) * r + w[0] * pitch * t,
                center[1] + (u[1] * math.cos(a) + v[1] * math.sin(a)) * r + w[1] * pitch * t,
                center[2] + (u[2] * math.cos(a) + v[2] * math.sin(a)) * r + w[2] * pitch * t)

    curve(path, 0, turns, k, sides, thickness, color, False)


# ============================================================================
# 10. Coordinate axes
# ============================================================================

def axes(C=(0, 0, 0), length=4.0, width=0.03):
    """Draw the coordinate axes: X red, Y green, Z blue, each labelled."""
    h, w = float(length), float(width)
    for direction, col, letter in (((1, 0, 0), (255, 0, 0), "X"),
                                   ((0, 1, 0), (0, 255, 0), "Y"),
                                   ((0, 0, 1), (0, 0, 255), "Z")):
        end = _add3(C, _scale(direction, h))
        tip = _add3(C, _scale(direction, h + 0.7))
        cylinder(C, end, w, 9, col)
        cone(end, tip, 2 * w, 9, col)
    # All three labels stand in the XY plane so they read the same way round.
    glyph("X", _add3(C, (h + 0.35, 0.25, 0)), (1, 0, 0), (0, 1, 0), 0.6, 3 * w,
          (255, 0, 0))
    glyph("Y", _add3(C, (0.3, h + 0.35, 0)), (1, 0, 0), (0, 1, 0), 0.6, 3 * w,
          (0, 255, 0))
    glyph("Z", _add3(C, (0.1, 0.25, h + 0.5)), (1, 0, 0), (0, 1, 0), 0.6, 3 * w,
          (0, 0, 255))


# ============================================================================
# 11. Parts that models keep needing
# ============================================================================
# Each of these could be written from the primitives above in a dozen lines;
# they are here because almost every student model contains a beam between
# two points, a wheel, a roof, a staircase, a wall of bricks or
# a tree, and the dozen lines are always the same.

def _local_mesh(M, origin, w, up, side):
    """Map a mesh built in local ``x, y, z`` coordinates into the world:
    ``x`` runs along ``w``, ``y`` along ``up`` and ``z`` along ``side``."""
    return _mapped(M, lambda p: (origin[0] + w[0] * p[0] + up[0] * p[1] + side[0] * p[2],
                                 origin[1] + w[1] * p[0] + up[1] * p[1] + side[1] * p[2],
                                 origin[2] + w[2] * p[0] + up[2] * p[1] + side[2] * p[2]))


def _ground_frame(direction, up=(0, 1, 0)):
    """Unit vectors ``(w, up, side)`` for something standing on the ground and
    running along ``direction``.  ``side`` is to the right of ``w``."""
    w = _unit(direction)
    up = _unit(up)
    side = _cross(w, up)
    if _norm(side) < EPS:                     # direction was straight up
        side = _perp(w)
        up = _cross(side, w)
    side = _unit(side)
    return w, up, side


def beam(A, B, width, height=None, color=None, up=(0, 1, 0)):
    """A rectangular bar from point ``A`` to point ``B``.

    The cross-section is ``width`` (sideways) by ``height`` (along ``up``,
    the roughly vertical direction); ``height`` defaults to ``width``.  This
    is the building block for bridges, cranes, frames and gun barrels: give
    it two points and it takes care of the orientation::

        add.beam([0, 0, 0], [4, 3, 1], 0.3, 0.5, "brown")
    """
    if height is not None and not isinstance(height, (int, float)):
        color, height = height, None          # beam(A, B, 0.3, "brown")
    if height is None:
        height = width
    w, v, u = _ground_frame(_sub(B, A), up)   # along, up, sideways
    hw, hh = width / 2.0, height / 2.0
    corners = []
    for end in (A, B):
        for sv in (-1, 1):
            for su in (-1, 1):
                corners.append((end[0] + u[0] * su * hw + v[0] * sv * hh,
                                end[1] + u[1] * su * hw + v[1] * sv * hh,
                                end[2] + u[2] * su * hw + v[2] * sv * hh))
    # corner index = 4 * (end) + 2 * (v side) + (u side)
    F = [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1], [2, 3, 7, 6],
         [0, 2, 6, 4], [1, 5, 7, 3]]
    M = Mesh()
    for p in corners:
        M.add_vertex(p)
    for f in F:
        M.add_face(f, color)
    _make_outward(M, 0)
    _scene.extend(M)


def rounded_box(center, sizes, r, k=8, color=None):
    """A box with all edges and corners rounded off by radius ``r``.

    ``sizes`` are the full edge lengths (a number means a cube).  Built by
    pushing the six patches of a quad sphere apart -- no boolean needed.
    """
    if not isinstance(sizes, (list, tuple)):
        sizes = [sizes, sizes, sizes]
    r = min(r, sizes[0] / 2.0, sizes[1] / 2.0, sizes[2] / 2.0)
    inner = [sizes[a] / 2.0 - r for a in range(3)]
    sides = [((1, 0, 0), (0, 1, 0), (0, 0, 1)),
             ((-1, 0, 0), (0, 0, 1), (0, 1, 0)),
             ((0, 1, 0), (0, 0, 1), (1, 0, 0)),
             ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
             ((0, 0, 1), (1, 0, 0), (0, 1, 0)),
             ((0, 0, -1), (0, 1, 0), (1, 0, 0))]
    warp = [math.tan(math.pi / 4.0 * (2.0 * i / k - 1.0)) for i in range(k + 1)]
    M = Mesh()
    color = rgb(color)
    for n, u, v in sides:
        P = []
        for a in warp:
            row = []
            for b in warp:
                p = _unit((n[0] + u[0] * a + v[0] * b,
                           n[1] + u[1] * a + v[1] * b,
                           n[2] + u[2] * a + v[2] * b))
                q = []
                for axis in range(3):
                    sign = 0.0 if abs(p[axis]) < 1e-12 else (1.0 if p[axis] > 0 else -1.0)
                    q.append(center[axis] + sign * inner[axis] + p[axis] * r)
                row.append(tuple(q))
            P.append(row)
        _add_grid(M, P, color)
    _weld(M, 1e-9)
    _drop_degenerate(M)
    _scene.extend(M)


def hemisphere(center, r, k=16, color=None, axis=(0, 1, 0)):
    """Half a ball with its flat side down: a dome, a bowl, a helmet.

    ``axis`` is the direction the round side points in.
    """
    revolve(lambda t: [r * math.sin(t), r * math.cos(t)], center,
            _add3(center, axis), 0.0, math.pi / 2.0, k, 4 * k, color)


def arch(A, B, height, thickness, color=None, steps=32, k=12, up=(0, 1, 0)):
    """A curved arch standing on the ground at points ``A`` and ``B``.

    The arch rises ``height`` above the line ``A -> B`` (a semicircle when
    ``height`` is half the span, an ellipse otherwise).  ``thickness`` is
    the radius of a round bar, or ``[width, depth]`` for a rectangular one
    with ``width`` across the arch and ``depth`` in the plane of the arch.
    """
    mid = midpoint(A, B)
    half = _sub(A, mid)
    lift = _scale(_unit(up), height)
    N = _unit(_cross(half, lift))             # normal of the arch's plane
    if isinstance(thickness, (list, tuple)):
        profile = profile_rect(thickness[0], thickness[1])
    else:
        profile = profile_circle(thickness, k)
    sections = []
    for i in range(steps + 1):
        t = math.pi * i / float(steps)
        c = _add3(mid, _add3(_scale(half, math.cos(t)), _scale(lift, math.sin(t))))
        T = _unit(_add3(_scale(half, -math.sin(t)), _scale(lift, math.cos(t))))
        R = _cross(T, N)                      # points outward from the arch
        sections.append([(c[0] + N[0] * a + R[0] * b,
                          c[1] + N[1] * a + R[1] * b,
                          c[2] + N[2] * a + R[2] * b) for a, b in profile])
    loft(sections, color)


def stairs(origin, n, width, rise, run, color=None, direction=(1, 0, 0)):
    """A solid flight of ``n`` steps starting at ``origin`` (the foot).

    Each step is ``rise`` high and ``run`` deep; the flight climbs along
    ``direction`` and is ``width`` wide, centred on the origin.
    """
    w, up, side = _ground_frame(direction)
    M = _grid_solid((0.0, 0.0, -width / 2.0), [run] * n, [rise] * n, [width],
                    lambda i, j, k: j <= i, color)
    _scene.extend(_local_mesh(M, origin, w, up, side))


def _hollow_prism(outer, inner, height, color, center=(0, 0, 0), axis=(0, 1, 0)):
    """A prism with a hole: ``outer`` and ``inner`` are 2D rings with the
    same number of points.  Used by :func:`gear`."""
    u, v, w = _frame(axis)
    half = _scale(w, height / 2.0)

    def lift(profile, sign):
        out = []
        for p in profile:
            q = (center[0] + u[0] * p[0] + v[0] * p[1],
                 center[1] + u[1] * p[0] + v[1] * p[1],
                 center[2] + u[2] * p[0] + v[2] * p[1])
            out.append(_add3(q, _scale(half, sign)))
        return out
    ob, ot, ib, it = lift(outer, -1), lift(outer, 1), lift(inner, -1), lift(inner, 1)
    M = Mesh()
    color = rgb(color)
    _add_grid(M, [ob, ot], color, wrap_v=True, flip=True)     # outside wall
    _add_grid(M, [ib, it], color, wrap_v=True)                # inside wall
    _add_grid(M, [it, ot], color, wrap_v=True, flip=True)     # top ring
    _add_grid(M, [ib, ob], color, wrap_v=True)                # bottom ring
    _weld(M, 1e-9)
    _make_outward(M, 0)
    return M


def gear(center, teeth, r, thickness, color=None, depth=None, hole=0.0,
         axis=(0, 1, 0)):
    """A cog wheel with ``teeth`` teeth, lying in the plane normal to ``axis``.

    ``r`` is the mean radius, ``depth`` the tooth height (default ``0.2 r``)
    and ``hole`` the radius of the axle hole (0 for a solid disc).  Two gears
    mesh when their mean radii add up to the distance between their centres
    and the tooth *pitch* ``2 * pi * r / teeth`` is the same.
    """
    outer = profile_gear(teeth, r, depth)
    if hole > EPS:
        inner = profile_circle(hole, len(outer))
        _scene.extend(_hollow_prism(outer, inner, thickness, color, center, axis))
    else:
        prism(outer, thickness, color, center, axis)


def wheel(center, r, width, color="black", axis=(0, 0, 1), k=32, spokes=0,
          hub_color="silver"):
    """A wheel whose axle points along ``axis``.

    With ``spokes=0`` it is a solid disc with a small hub; with spokes it
    becomes a tyre (a torus), a hub and ``spokes`` thin bars between them.
    """
    w = _unit(axis)
    a = _add3(center, _scale(w, -width / 2.0))
    b = _add3(center, _scale(w, width / 2.0))
    if spokes <= 0:
        cylinder(a, b, r, k, color)
        cylinder(_add3(a, _scale(w, -width * 0.15)), _add3(b, _scale(w, width * 0.15)),
                 r * 0.3, max(8, k // 2), hub_color)
        return
    tyre = width / 2.0
    torus(center, r - tyre, tyre, k, max(8, k // 2), color, axis)
    hub = max(r * 0.2, tyre)
    cylinder(a, b, hub, max(8, k // 2), hub_color)
    u, v, _ = _frame(w)
    for i in range(spokes):
        ang = 2 * math.pi * i / spokes
        tip = (center[0] + (u[0] * math.cos(ang) + v[0] * math.sin(ang)) * (r - tyre),
               center[1] + (u[1] * math.cos(ang) + v[1] * math.sin(ang)) * (r - tyre),
               center[2] + (u[2] * math.cos(ang) + v[2] * math.sin(ang)) * (r - tyre))
        cylinder(center, tip, tyre * 0.3, 8, hub_color)


def roof(center, size, height, color=None, overhang=0.0):
    """A gabled (triangular) roof over a ``size = [width_x, depth_z]`` floor.

    ``center`` is the middle of the eaves line (the roof's lowest edge sits at
    ``center[1]``), the ridge runs along Z, and ``overhang`` makes the roof
    stick out beyond the walls on every side.
    """
    w = size[0] / 2.0 + overhang
    profile = [[-w, 0.0], [w, 0.0], [0.0, float(height)]]
    prism(profile, size[1] + 2 * overhang, color, center, (0, 0, 1))


def column(base, height, r, color=None, k=24, plinth=True):
    """A classical column standing on point ``base`` (the bottom centre).

    A square plinth, a slightly tapering shaft and a square capital.
    ``plinth=False`` leaves just the shaft.
    """
    x, y, z = base[0], base[1], base[2]
    slab = 0.3 * r
    if plinth:
        cuboid([x, y + slab / 2.0, z], [2.6 * r, slab, 2.6 * r], color)
        cuboid([x, y + height - slab / 2.0, z], [2.6 * r, slab, 2.6 * r], color)
        frustum([x, y + slab, z], [x, y + height - slab, z], r, 0.85 * r, k, color)
    else:
        frustum([x, y, z], [x, y + height, z], r, 0.85 * r, k, color)


def bricks(origin, length, height, brick=(1.0, 0.5, 0.5), color="brown",
           direction=(1, 0, 0), gap=0.05, seed=None):
    """A wall of staggered bricks starting at ``origin`` (its bottom-left end).

    ``brick`` is ``[length, height, depth]`` of one brick; every second row
    is shifted by half a brick.  ``color`` may be a function ``color(i, j)``
    of the brick's column and row, and with ``seed`` each brick gets a small
    random variation of the colour instead.
    """
    bl, bh, bd = brick[0], brick[1], brick[2]
    rows = int(height / bh + 0.5)
    rnd = _random.Random(seed) if seed is not None else None
    push()
    for j in range(rows):
        shift = 0.0 if j % 2 == 0 else bl / 2.0
        x = -shift
        i = 0
        while x < length - EPS:
            x0, x1 = max(0.0, x), min(length, x + bl - gap)
            if x1 - x0 > EPS:
                if callable(color):
                    c = color(i, j)
                elif rnd is not None:
                    c = shade(color, rnd.uniform(0.8, 1.15))
                else:
                    c = color
                cuboid([(x0 + x1) / 2.0, j * bh + (bh - gap) / 2.0, 0.0],
                       [x1 - x0, bh - gap, bd], c)
            x += bl
            i += 1
    M = pop()
    w, up, side = _ground_frame(direction)
    _scene.extend(_local_mesh(M, origin, w, up, side))


def tree(at, height, trunk="brown", leaves="green", kind="round", k=10, seed=None):
    """A simple tree standing on point ``at``.

    ``kind`` is ``"round"`` (a trunk and a bunch of spheres), ``"pine"``
    (stacked cones) or ``"palm"`` (a curved trunk with leaf blades).  Give a
    ``seed`` to get a slightly different tree for every call with the same
    seed -- a forest is ``[add.tree(p, 3, seed=i) for i, p in enumerate(pts)]``.
    """
    rnd = _random.Random(seed if seed is not None else 0)
    var = (lambda a, b: rnd.uniform(a, b)) if seed is not None else (lambda a, b: (a + b) / 2.0)
    x, y, z = at[0], at[1], at[2]
    h = float(height)
    if kind == "pine":
        cylinder([x, y, z], [x, y + 0.3 * h, z], 0.05 * h, 8, trunk)
        tiers = 3
        for i in range(tiers):
            base_y = y + 0.2 * h + 0.22 * h * i
            rr = 0.32 * h * (1.0 - 0.22 * i) * var(0.9, 1.1)
            cone([x, base_y, z], [x, base_y + 0.36 * h, z], rr, k + 4, leaves)
        return
    if kind == "palm":
        lean = var(0.1, 0.25) * h
        pts = [[x + lean * (t ** 2), y + h * t, z] for t in
               [i / 8.0 for i in range(9)]]
        polyline(pts, lambda t: 0.06 * h * (1.0 - 0.5 * t), 8, trunk)
        top = pts[-1]
        n = 7
        for i in range(n):
            a = 2 * math.pi * i / n + var(-0.2, 0.2)
            dx, dz = math.cos(a), math.sin(a)
            blade = [[top[0] + dx * 0.45 * h * t, top[1] + 0.15 * h * math.sin(math.pi * t) - 0.25 * h * t * t,
                      top[2] + dz * 0.45 * h * t] for t in [j / 5.0 for j in range(6)]]
            polyline(blade, lambda t: 0.035 * h * (1.0 - t) + 0.005 * h, 6, leaves)
        return
    cylinder([x, y, z], [x, y + 0.45 * h, z], 0.06 * h, 8, trunk)
    balls = [(0.0, 0.62, 0.0, 0.33), (0.2, 0.5, 0.05, 0.22), (-0.18, 0.52, -0.1, 0.2),
             (0.02, 0.5, 0.2, 0.2), (-0.05, 0.55, -0.22, 0.2)]
    for dx, dy, dz, rr in balls:
        s = var(0.85, 1.15)
        sphere([x + dx * h * s, y + dy * h, z + dz * h * s], rr * h * var(0.9, 1.1),
               max(3, k // 3), leaves)


#: Default palette for :func:`pixels`: one letter per colour.
PALETTE = {"#": "black", "k": "grey", "w": "white", "r": "red", "g": "green",
           "b": "blue", "y": "yellow", "o": "orange", "p": "pink", "c": "cyan",
           "m": "magenta", "n": "brown", "s": "sky", "l": "lime", "t": "teal",
           "v": "purple", "d": "gold", "i": "silver", "a": "navy"}


def pixels(rows, size=1.0, origin=(0, 0, 0), colors=None, depth=1, color=None):
    """Pixel art in 3D: a list of strings becomes a block of coloured cubes.

    Every character is one cell; a space or a dot is empty.  ``colors`` maps
    characters to colours (default :data:`PALETTE`, where ``r`` is red,
    ``g`` green, ``#`` black ...).  The first string is the top row, the
    picture stands in the XY plane and is ``depth`` cells thick::

        add.pixels([".r.r.",
                    "rrrrr",
                    ".rrr.",
                    "..r.."], 0.5)                     # a heart
    """
    palette = PALETTE if colors is None else colors
    rows = [r for r in rows]
    ny = len(rows)
    nx = max(len(r) for r in rows)

    def char(i, j):
        row = rows[ny - 1 - j]
        return row[i] if i < len(row) else " "

    def filled(i, j, k):
        return char(i, j) not in " ."

    def paint(i, j, k):
        c = char(i, j)
        if c in palette:
            return palette[c]
        return color if color is not None else DEFAULT_COLOR

    _scene.extend(_grid_solid(origin, [size] * nx, [size] * ny, [size] * depth,
                              filled, paint))


def heightmap(heights, cell=1.0, origin=(0, 0, 0), color=None):
    """Columns of cubes: ``heights[i][j]`` cells stacked at column ``(i, j)``.

    ``i`` runs along X and ``j`` along Z from ``origin``.  ``color`` may be
    a function ``color(i, j, k)`` of the *cell* -- ``i`` along X, ``j`` up,
    ``k`` along Z -- so layers can be painted by height (``j``).  Build the
    list with a comprehension::

        H = [[int(3 + 2 * add.sin(i / 3.0) * add.cos(j / 3.0))
              for j in range(30)] for i in range(30)]
        add.heightmap(H, 0.5, color=lambda i, j, k: "sky" if j < 2 else "green")
    """
    nx = len(heights)
    nz = len(heights[0])
    top = max(max(int(round(h)) for h in row) for row in heights)
    if top <= 0:
        return

    def filled(i, j, k):
        return j < int(round(heights[i][k]))

    _scene.extend(_grid_solid(origin, [cell] * nx, [cell] * top, [cell] * nz,
                              filled, color))


# -- tubes through points --------------------------------------------------

def _tube_along(points, radii, k, color, closed, cap_a=None, cap_b=None):
    """The engine behind :func:`curve` and :func:`polyline`: a round tube
    through a list of 3D points with a radius per point."""
    tangents, normals = _rmf(points, closed)
    ring = [(math.cos(2 * math.pi * j / k), math.sin(2 * math.pi * j / k))
            for j in range(k)]
    P = []
    for i in range(len(points)):
        u = normals[i]
        v = _cross(tangents[i], u)
        c = points[i]
        rad = radii[i]
        row = []
        for (cx, cy) in ring:
            x, y = cx * rad, cy * rad
            row.append((c[0] + u[0] * x + v[0] * y,
                        c[1] + u[1] * x + v[1] * y,
                        c[2] + u[2] * x + v[2] * y))
        P.append(row)
    M = Mesh()
    _add_grid(M, P, color, wrap_u=closed, wrap_v=True, flip=True)
    if not closed:
        _fan(M, P[0], points[0], color if cap_a is None else cap_a, flip=True)
        _fan(M, P[-1], points[-1], color if cap_b is None else cap_b)
    return M


def polyline(points, r=0.1, k=12, color=None, closed=False, smooth=0):
    """A round tube through a list of points -- wires, pipes, rails, branches.

    ``r`` is one radius or a function ``r(t)`` of the fraction ``t`` along
    the line; ``smooth`` rounds the corners with :func:`chaikin` first.
    ``color`` may be a function ``color(t, a)`` like in :func:`curve`.
    """
    pts = [tuple(float(c) for c in p) for p in points]
    if smooth:
        pts = [tuple(p) for p in chaikin(pts, smooth, closed)]
    n = len(pts)
    if n < 2:
        return
    ts = [i / float(n if closed else n - 1) for i in range(n)]
    radii = [r(t) if callable(r) else r for t in ts]
    cells = color
    cap_a = cap_b = None
    if callable(color):
        fn = color

        def cells(i, j):
            t = (ts[i] + (ts[i + 1] if i + 1 < n else 1.0)) / 2.0
            return fn(t, 2 * math.pi * (j + 0.5) / k)
        cap_a = lambda j: fn(0.0, 2 * math.pi * (j + 0.5) / k)     # noqa: E731
        cap_b = lambda j: fn(1.0, 2 * math.pi * (j + 0.5) / k)     # noqa: E731
    _emit(_tube_along(pts, radii, k, cells, closed, cap_a, cap_b))


def wireframe(M, r=0.03, k=6, color=None, nodes=True):
    """Draw every edge of a mesh as a thin bar, with a ball at every corner.

    The result is drawn into the scene (the mesh itself is left alone).
    Without ``color`` each bar takes the colour of a face it belongs to.
    Keep the mesh small: a 10 000-face model has some 15 000 edges.
    """
    M = as_mesh(M)
    edges = {}
    for f, c in zip(M.F, M.C):
        for i in range(len(f)):
            a, b = f[i], f[(i + 1) % len(f)]
            key = (a, b) if a < b else (b, a)
            if key not in edges:
                edges[key] = c
    for (a, b), c in edges.items():
        cylinder(M.V[a], M.V[b], r, k, color if color is not None else c)
    if nodes:
        used = set()
        for a, b in edges:
            used.add(a)
            used.add(b)
        for i in used:
            sphere(M.V[i], r, 2, color if color is not None else M.C[0])


def flow(field, p0, dt=0.01, steps=1000):
    """Follow a vector field: the list of points a particle visits.

    ``field(p)`` returns the velocity ``[vx, vy, vz]`` at point ``p``; the
    path is integrated with the classical Runge-Kutta method, so it stays
    accurate even for chaotic systems like the Lorenz attractor::

        def lorenz(p):
            x, y, z = p
            return [10 * (y - x), x * (28 - z) - y, x * y - 8.0 / 3 * z]
        pts = add.flow(lorenz, [1, 1, 1], 0.01, 4000)
    """
    p = [float(c) for c in p0]
    out = [list(p)]
    for _ in range(steps):
        k1 = field(p)
        k2 = field([p[i] + 0.5 * dt * k1[i] for i in range(3)])
        k3 = field([p[i] + 0.5 * dt * k2[i] for i in range(3)])
        k4 = field([p[i] + dt * k3[i] for i in range(3)])
        p = [p[i] + dt / 6.0 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i])
             for i in range(3)]
        out.append(list(p))
    return out


def trace(field, p0, dt=0.01, steps=1000, r=0.1, k=12, color=None, every=1):
    """Draw the path of :func:`flow` as a tube (``every`` keeps each n-th point)."""
    pts = flow(field, p0, dt, steps)
    if every > 1:
        pts = pts[::every]
    polyline(pts, r, k, color)


# ============================================================================
# 12. Parametric surfaces
# ============================================================================

def parametric(S, min_u, max_u, grid_u, min_v, max_v, grid_v, RGB=None,
               wrap_u=False, wrap_v=False, flip=False, thickness=0.0,
               double_sided=False, color=None):
    """The heart of the library: draw the surface ``S(u, v) -> [x, y, z]``.

    ``grid_u`` and ``grid_v`` say how many cells to use in each direction::

        def torus(u, v):
            return [(5 + math.cos(u)) * math.cos(v),
                    math.sin(u),
                    (5 + math.cos(u)) * math.sin(v)]
        add.parametric(torus, 0, 2 * math.pi, 40, 0, 2 * math.pi, 80, "gold")

    Extras beyond add.py 1.2:

    ``wrap_u`` / ``wrap_v``
        Join the last row/column back to the first, so a closed surface has no
        seam and no duplicated vertices.
    ``thickness``
        Give the sheet a real thickness, turning it into a solid shell.  This
        is the cure for a surface that looks black from one side: a solid has
        no wrong side.
    ``double_sided``
        Cheaper alternative -- keep the sheet infinitely thin but add a copy
        of every face pointing the other way.
    ``flip``
        Turn the surface inside out.
    ``color`` as a function
        Pass ``color=lambda u, v: ...`` and every cell is painted by its own
        parameters -- stripes, checkerboards and rainbows in one line.
    """
    color = RGB if RGB is not None else color
    nu = grid_u if wrap_u else grid_u + 1
    nv = grid_v if wrap_v else grid_v + 1
    P = []
    for i in range(nu):
        u = min_u + (max_u - min_u) * i / float(grid_u)
        row = []
        for j in range(nv):
            v = min_v + (max_v - min_v) * j / float(grid_v)
            p = S(u, v)
            row.append((p[0], p[1], p[2]))
        P.append(row)
    if callable(color):
        fn = color

        def color(i, j):
            return fn(min_u + (max_u - min_u) * (i + 0.5) / float(grid_u),
                      min_v + (max_v - min_v) * (j + 0.5) / float(grid_v))
    else:
        color = rgb(color)
    M = Mesh()
    _add_grid(M, P, color, wrap_u=wrap_u, wrap_v=wrap_v, flip=flip)
    if thickness:
        M = solidify(M, thickness)
    elif double_sided:
        M = two_sided(M)
    _scene.extend(M)


def two_sided(M=None):
    """Return a copy of ``M`` in which every face also exists reversed.

    Use it when a thin surface disappears or turns black when seen from
    behind.  The polygon count doubles.
    """
    M = as_mesh(M)
    out = M.copy()
    for k, (f, c) in enumerate(zip(M.F, M.C)):
        uv = M.UV[k] if M.UV is not None else None
        out.add_face(list(reversed(f)), c,
                     None if uv is None else list(reversed(uv)))
    return out


def solidify(M=None, thickness=0.1, both_ways=True):
    """Give a thin surface a real thickness and return the closed solid.

    Every vertex is pushed along the average normal of the faces around it;
    the open border is then stitched with a wall, so the result is watertight
    and lit correctly from every angle.
    """
    M = as_mesh(M)
    normals = _vertex_normals(M)
    n = len(M.V)
    out = Mesh()
    up = thickness / 2.0 if both_ways else thickness
    down = -thickness / 2.0 if both_ways else 0.0
    for i, p in enumerate(M.V):
        nrm = normals[i]
        out.add_vertex((p[0] + nrm[0] * up, p[1] + nrm[1] * up,
                        p[2] + nrm[2] * up))
    for i, p in enumerate(M.V):
        nrm = normals[i]
        out.add_vertex((p[0] + nrm[0] * down, p[1] + nrm[1] * down,
                        p[2] + nrm[2] * down))
    for f, c in zip(M.F, M.C):
        out.add_face(f, c)                                  # outer shell
        out.add_face([i + n for i in reversed(f)], c)       # inner shell
    # Stitch the boundary: any edge used by exactly one face is on the border.
    # The wall runs outer -> inner -> inner -> outer so that it faces outwards.
    for (a, b), c in _boundary_edges(M).items():
        out.add_face([a, a + n, b + n, b], c)
    return out


def _vertex_normals(M):
    """Area-weighted average normal at every vertex."""
    acc = [[0.0, 0.0, 0.0] for _ in M.V]
    for f in M.F:
        if len(f) < 3:
            continue
        nrm = _face_normal(M, f)
        for i in f:
            acc[i][0] += nrm[0]
            acc[i][1] += nrm[1]
            acc[i][2] += nrm[2]
    out = []
    for a in acc:
        out.append(_unit(a) if _norm(a) > EPS else (0.0, 1.0, 0.0))
    return out


def _face_normal(M, f):
    """Newell's normal -- works for any polygon, convex or not, and is
    numerically stable for nearly-degenerate faces."""
    nx = ny = nz = 0.0
    n = len(f)
    for i in range(n):
        a = M.V[f[i]]
        b = M.V[f[(i + 1) % n]]
        nx += (a[1] - b[1]) * (a[2] + b[2])
        ny += (a[2] - b[2]) * (a[0] + b[0])
        nz += (a[0] - b[0]) * (a[1] + b[1])
    return (nx, ny, nz)


def _boundary_edges(M):
    """``{(a, b): colour}`` for every edge that belongs to just one face."""
    seen = {}
    for f, c in zip(M.F, M.C):
        n = len(f)
        for i in range(n):
            a, b = f[i], f[(i + 1) % n]
            key = (a, b) if a < b else (b, a)
            if key in seen:
                seen[key] = None
            else:
                seen[key] = (a, b, c)
    out = {}
    for value in seen.values():
        if value is not None:
            out[(value[0], value[1])] = value[2]
    return out


# ============================================================================
# 13. Curves, sweeps and lofts -- "copy, turn, stretch a cross-section"
# ============================================================================

def _rmf(points, closed=False):
    """Rotation-minimising frames along a polyline (double-reflection method).

    Returns ``(tangents, normals)``.  Unlike the textbook Frenet frame this
    never spins wildly at an inflection point, so swept shapes do not twist
    on their own.
    """
    n = len(points)
    tangents = []
    for i in range(n):
        if closed:
            a, b = points[(i - 1) % n], points[(i + 1) % n]
        else:
            a = points[i - 1] if i > 0 else points[i]
            b = points[i + 1] if i < n - 1 else points[i]
        t = _unit(_sub(b, a))
        if _norm(t) < EPS:
            t = tangents[-1] if tangents else (0.0, 0.0, 1.0)
        tangents.append(t)
    normals = [_perp(tangents[0])]
    for i in range(n - 1):
        v1 = _sub(points[i + 1], points[i])
        c1 = _dot(v1, v1)
        if c1 < EPS:
            normals.append(normals[-1])
            continue
        rL = _sub(normals[i], _scale(v1, 2.0 * _dot(v1, normals[i]) / c1))
        tL = _sub(tangents[i], _scale(v1, 2.0 * _dot(v1, tangents[i]) / c1))
        v2 = _sub(tangents[i + 1], tL)
        c2 = _dot(v2, v2)
        if c2 < EPS:
            normals.append(_unit(rL))
        else:
            normals.append(_unit(_sub(rL, _scale(v2, 2.0 * _dot(v2, rL) / c2))))
    if closed and n > 1:
        # Cancel the leftover twist by spreading it over the whole loop.
        t = tangents[0]
        u0, v0 = normals[0], _cross(tangents[0], normals[0])
        last = normals[-1]
        angle = math.atan2(_dot(last, v0), _dot(last, u0))
        for i in range(n):
            a = -angle * i / float(n)
            u = normals[i]
            v = _cross(tangents[i], u)
            normals[i] = _add3(_scale(u, math.cos(a)), _scale(v, math.sin(a)))
    return tangents, normals


def _sweep_profile(points, tangents, normals, profile, scale=None, twist=None):
    """Place a 2D ``profile`` at every point of a path -> grid of 3D points."""
    P = []
    n = len(points)
    for i in range(n):
        t = i / float(n - 1) if n > 1 else 0.0
        u = normals[i]
        v = _cross(tangents[i], u)
        s = scale(t) if callable(scale) else (1.0 if scale is None else scale)
        a = twist(t) if callable(twist) else (0.0 if twist is None else twist * t)
        ca, sa = math.cos(a), math.sin(a)
        c = points[i]
        row = []
        for p in profile:
            x, y = p[0] * s, p[1] * s
            x, y = x * ca - y * sa, x * sa + y * ca
            row.append((c[0] + u[0] * x + v[0] * y,
                        c[1] + u[1] * x + v[1] * y,
                        c[2] + u[2] * x + v[2] * y))
        P.append(row)
    return P


def sweep(profile, path, t0=0.0, t1=1.0, steps=100, color=None, closed=False,
          scale=None, twist=None, caps=True):
    """Slide a 2D cross-section along a 3D path -- the general shape maker.

    ``profile`` is a closed list of ``[x, y]`` points, ``path(t)`` returns a
    3D point.  ``scale`` and ``twist`` may be numbers or functions of
    ``t`` in 0..1, which is how you get a shape that grows and turns as it
    goes::

        square = [[-1, -1], [1, -1], [1, 1], [-1, 1]]
        add.sweep(square, lambda t: [0, t, 0], 0, 10, 60, "orange",
                  scale=lambda t: 1 - 0.7 * t, twist=3 * math.pi)

    Set ``closed=True`` when the path returns to its start (a ring).

    ``color`` may be a function ``color(t, j)`` of the path parameter and
    the index of the profile edge (``0`` is the edge from the first profile
    point to the second), so every side of a swept square can have its own
    colour, or the colour can change along the path.
    """
    n = steps if closed else steps + 1
    points = []
    for i in range(n):
        t = t0 + (t1 - t0) * i / float(steps)
        p = path(t)
        points.append((p[0], p[1], p[2]))
    tangents, normals = _rmf(points, closed)
    P = _sweep_profile(points, tangents, normals, profile, scale, twist)
    if callable(color):
        fn = color

        def color(i, j):
            return fn(t0 + (t1 - t0) * (i + 0.5) / float(steps), j)
        cap_a, cap_b = fn(t0, -1), fn(t1, -1)
    else:
        color = cap_a = cap_b = rgb(color)
    M = Mesh()
    _add_grid(M, P, color, wrap_u=closed, wrap_v=True, flip=True)
    if caps and not closed:
        M.add_polygon(P[0][::-1], cap_a)
        M.add_polygon(P[-1], cap_b)
        _weld(M, 1e-9)
        _make_outward(M, 0)
    _emit(M)


def curve(P, min_t, max_t, grid_t, k=16, r=0.1, RGB=None, isConnected=False,
          color=None):
    """Draw a 3D parametric curve as a round tube of radius ``r``.

    ``r`` may be a function ``r(t)`` for a tube that swells and narrows.
    ``isConnected=True`` closes the tube into a loop without a seam.
    The colour may be a function ``color(t, a)`` of the curve parameter and
    the angle around the tube (radians), for example a candy-cane spiral::

        add.curve(spiral, 0, 6 * add.pi, 300, 16, 0.2,
                  color=lambda t, a: "red" if (t + a) % 1.0 < 0.5 else "white")
    """
    color = RGB if RGB is not None else color
    if callable(color):
        fn = color

        def color(i, j):
            t = min_t + (max_t - min_t) * (i + 0.5) / float(grid_t)
            return fn(t, 2.0 * math.pi * (j + 0.5) / float(k))
        cap_a = lambda j: fn(min_t, 2.0 * math.pi * (j + 0.5) / float(k))  # noqa
        cap_b = lambda j: fn(max_t, 2.0 * math.pi * (j + 0.5) / float(k))  # noqa
    else:
        color = cap_a = cap_b = rgb(color)
    n = grid_t if isConnected else grid_t + 1
    ts, points = [], []
    for i in range(n):
        t = min_t + (max_t - min_t) * i / float(grid_t)
        ts.append(t)
        p = P(t)
        points.append((p[0], p[1], p[2]))
    radii = [r(t) if callable(r) else r for t in ts]
    _emit(_tube_along(points, radii, k, color, isConnected, cap_a, cap_b))


def extrude(profile, direction=(0, 1, 0), color=None, steps=1, twist=0.0,
            scale=1.0, center=(0, 0, 0), caps=True):
    """Pull a 2D shape out into 3D, optionally turning and tapering as it goes.

    This is the "copy the cross-section, move it, rotate it, stretch it"
    construction in one call::

        star = [[math.cos(a) * (1 if i % 2 else 0.45),
                 math.sin(a) * (1 if i % 2 else 0.45)]
                for i, a in enumerate(...)]
        add.extrude(star, [0, 4, 0], "gold", steps=60, twist=math.pi,
                    scale=lambda t: 1 - 0.6 * t)
    """
    def path(t):
        return (center[0] + direction[0] * t,
                center[1] + direction[1] * t,
                center[2] + direction[2] * t)
    sweep(profile, path, 0.0, 1.0, max(1, steps), color, False, scale, twist,
          caps)


def loft(sections, color=None, closed=False, caps=True, flip=False):
    """Skin a surface over a list of cross-sections (each a ring of 3D points).

    Every section must have the same number of points.  This is the most
    direct way to build a shape from slices you have computed yourself.
    """
    M = Mesh()
    _add_grid(M, [list(s) for s in sections], rgb(color), wrap_u=closed,
              wrap_v=True, flip=not flip)
    if caps and not closed:
        M.add_polygon(list(sections[0])[::-1], color)
        M.add_polygon(list(sections[-1]), color)
        _weld(M, 1e-9)
        _make_outward(M, 0)
    _emit(M)


def ribbon(path, t0, t1, steps, width, color=None, closed=False, twist=None,
           thickness=0.0):
    """A flat band following a 3D path -- like a strip of paper.

    With ``thickness`` it becomes a solid bar instead of a zero-thickness
    sheet, so both sides are lit.
    """
    half = width / 2.0
    profile = [(-half, 0.0), (half, 0.0)]
    n = steps if closed else steps + 1
    points = []
    for i in range(n):
        t = t0 + (t1 - t0) * i / float(steps)
        p = path(t)
        points.append((p[0], p[1], p[2]))
    tangents, normals = _rmf(points, closed)
    P = _sweep_profile(points, tangents, normals, profile, None, twist)
    M = Mesh()
    _add_grid(M, P, rgb(color), wrap_u=closed)
    if thickness:
        M = solidify(M, thickness)
    else:
        M = two_sided(M)
    _scene.extend(M)


def circle(A, B, r, k=24, RGB=None, color=None):
    """add.py 1.2 disc: a filled circle centred at ``A``, facing ``B``."""
    disc(A, B, r, k, RGB if RGB is not None else color)


# ============================================================================
# 14. A catalogue of named surfaces
# ============================================================================
# Two dozen classical parametric surfaces, ready to draw by name.  Each entry
# holds the formula, the parameter ranges, whether the surface closes on
# itself (so that it is drawn without a seam) and the constants it depends
# on.  The formulas follow the collection at drhuang.com ("parametric
# surfaces", A. Huang) and the standard references (Gray, "Modern
# Differential Geometry of Curves and Surfaces"; 3D-XplorMath).

def _catalog():
    pi, cos, sin, sinh, cosh, exp, log, tan, sqrt = (
        math.pi, math.cos, math.sin, math.sinh, math.cosh, math.exp, math.log,
        math.tan, math.sqrt)
    S = {}

    def entry(name, f, u, v, wrap=(False, False), grid=(60, 60), note="",
              flip=False, **params):
        S[name] = {"f": f, "u": u, "v": v, "wrap": wrap, "grid": grid,
                   "note": note, "flip": flip, "params": params}

    entry("bohemian_dome",
          lambda u, v, a, b, c: [a * cos(u), b * cos(v) + a * sin(u), c * sin(v)],
          (0, 2 * pi), (0, 2 * pi), (True, True),
          note="a circle swept along another circle", a=0.5, b=1.5, c=1.0)
    entry("dini",
          lambda u, v, a, b: [a * cos(u) * sin(v), a * sin(u) * sin(v),
                              a * (cos(v) + log(tan(v / 2.0))) + b * u],
          (0, 4 * pi), (0.01, 2.0), (False, False), (120, 40),
          note="a twisted pseudosphere of constant negative curvature",
          a=1.0, b=0.2)
    entry("enneper",
          lambda u, v: [u - u ** 3 / 3.0 + u * v * v, v - v ** 3 / 3.0 + u * u * v,
                        u * u - v * v],
          (-2, 2), (-2, 2), note="a minimal surface that crosses itself")

    def klein(u, v, a, b):
        r = 4.0 * (1.0 - cos(u) / 2.0)
        if u < pi:
            return [a * cos(u) * (1 + sin(u)) + r * cos(u) * cos(v),
                    b * sin(u) + r * sin(u) * cos(v), r * sin(v)]
        return [a * cos(u) * (1 + sin(u)) + r * cos(v + pi), b * sin(u),
                r * sin(v)]
    entry("klein_bottle", klein, (0, 2 * pi), (0, 2 * pi), (False, True),
          (120, 40), note="the one-sided bottle whose neck passes through "
          "its own wall", a=6.0, b=16.0)
    entry("mobius",
          lambda t, s, R: [(R + s * cos(t / 2.0)) * cos(t),
                           (R + s * cos(t / 2.0)) * sin(t), s * sin(t / 2.0)],
          (0, 2 * pi), (-0.5, 0.5), (False, False), (120, 8),
          note="a strip with one side and one edge", R=2.0)
    entry("plucker_conoid",
          lambda u, v: [u * sqrt(1 - v * v), u * v, 1 - v * v],
          (-2, 2), (-1, 1), note="a ruled surface: straight lines through "
          "a vertical axis")

    def worm(u, v, a, b):
        h = exp(u / (6.0 * pi))
        return [a * (1 - h) * cos(u) * cos(v / 2.0) ** 2,
                1 - exp(u / (b * pi)) - sin(v) + h * sin(v),
                a * (h - 1) * sin(u) * cos(v / 2.0) ** 2]
    entry("worm", worm, (0, 6 * pi), (0, 2 * pi), (False, True), (160, 40),
          note="a snail shell that widens as it turns", a=1.0, b=6.0)
    entry("sine_surface",
          lambda u, v: [sin(u), sin(v), sin(u + v)],
          (-pi, pi), (-pi, pi), (True, True),
          note="three sines; it closes on itself in both directions")
    entry("cosine_surface",
          lambda u, v: [cos(u), cos(v), cos(u + v)],
          (-pi, pi), (-pi, pi), (True, True), flip=True,
          note="the cosine twin of the sine surface")
    entry("whitney_umbrella",
          lambda u, v: [u * v, u, v * v],
          (-1.5, 1.5), (-1.5, 1.5), note="a surface with a pinch point")
    entry("helicoid",
          lambda u, v, c: [u * cos(v), u * sin(v), c * v],
          (-2, 2), (0, 2 * pi), (False, False), (30, 120),
          note="a spiral staircase; the only ruled minimal surface", c=0.5)
    entry("hyperbolic_helicoid",
          lambda u, v, a: [sinh(v) * cos(a * u) / (1 + cosh(u) * cosh(v)),
                           sinh(v) * sin(a * u) / (1 + cosh(u) * cosh(v)),
                           cosh(v) * sinh(u) / (1 + cosh(u) * cosh(v))],
          (-4, 4), (-4, 4), grid=(120, 60),
          note="a helicoid bent into a ball", a=2.5)
    entry("henneberg",
          lambda u, v: [2 * cos(v) * sinh(u) - 0.667 * cos(3 * v) * sinh(3 * u),
                        2 * sin(v) * sinh(u) + 0.667 * sin(3 * v) * sinh(3 * u),
                        2 * cos(2 * v) * cosh(2 * u)],
          (-1, 1), (-pi / 2, pi / 2), note="a one-sided minimal surface")
    entry("owl",
          lambda u, v: [v * cos(u) - 0.5 * v * v * cos(2 * u),
                        -v * sin(u) - 0.5 * v * v * sin(2 * u),
                        4 * exp(1.5 * log(v)) * cos(1.5 * u) / 3.0],
          (0, 4 * pi), (0.001, 1), (False, False), (160, 30),
          note="Maeder's owl, a twisted minimal surface")
    entry("snail",
          lambda u, v: [u * cos(v) * sin(u), u * cos(u) * cos(v), -u * sin(v)],
          (0, 2 * pi), (-pi, pi), (False, True), (120, 40),
          note="a horn that curls up on itself")
    entry("kidney",
          lambda u, v: [cos(u) * (3 * cos(v) - cos(3 * v)),
                        sin(u) * (3 * cos(v) - cos(3 * v)),
                        3 * sin(v) - sin(3 * v)],
          (0, 2 * pi), (-pi / 2, pi / 2), (True, False), (80, 40),
          note="a surface of revolution with a dent")
    entry("pillow",
          lambda u, v, a: [cos(u), cos(v), a * sin(u) * sin(v)],
          (0, pi), (-pi, pi), (False, True), (40, 80),
          note="a cushion with four corners", a=0.5)
    entry("horn",
          lambda u, v, a, b, c: [(a + u * cos(v)) * sin(b * pi * u),
                                 (a + u * cos(v)) * cos(b * pi * u) + c * u,
                                 u * sin(v)],
          (0, 1), (-pi, pi), (False, True), (60, 40),
          note="a tube that grows as it bends", a=1.0, b=1.0, c=1.0)
    entry("stiletto",
          lambda u, v: [(2 + cos(u)) * cos(v) ** 3 * sin(v),
                        (2 + cos(u + 2 * pi / 3)) * cos(v + 2 * pi / 3) ** 2
                        * sin(v + 2 * pi / 3) ** 2,
                        -(2 + cos(u - 2 * pi / 3)) * cos(v + 2 * pi / 3) ** 2
                        * sin(v + 2 * pi / 3) ** 2],
          (0, 2 * pi), (0, pi), (True, False), (80, 60),
          note="a pointed shoe")
    entry("apple",
          lambda u, v: [cos(u) * (4 + 3.8 * cos(v)), sin(u) * (4 + 3.8 * cos(v)),
                        (cos(v) + sin(v) - 1) * (1 + sin(v))
                        * log(1 - pi * v / 10.0) + 7.5 * sin(v)],
          (0, 2 * pi), (-pi, pi), (True, False), (80, 60),
          note="an apple with a dimple at the stalk")

    def kuen(u, v):
        h = 1 + u * u * sin(v) ** 2
        return [2 * (cos(u) + u * sin(u)) * sin(v) / h,
                2 * (-u * cos(u) + sin(u)) * sin(v) / h,
                log(tan(v / 2.0)) + 2 * cos(v) / h]
    entry("kuen", kuen, (-4.3, 4.3), (0.03, 3.11), grid=(120, 60),
          note="a surface of constant negative curvature")
    entry("tranguloid_trefoil",
          lambda u, v: [2 * sin(3 * u) / (2 + cos(v)),
                        2 * (sin(u) + 2 * sin(2 * u)) / (2 + cos(v + 2 * pi / 3)),
                        (cos(u) - 2 * cos(2 * u)) * (2 + cos(v))
                        * (2 + cos(v + 2 * pi / 3)) / 4.0],
          (-pi, pi), (-pi, pi), (True, True), (160, 40),
          note="a knotted tube with three lobes")
    entry("antisymmetric_torus",
          lambda u, v, R, r, a: [(R + r * cos(v) * (a + sin(u))) * cos(u),
                                 (R + r * cos(v) * (a + sin(u))) * sin(u),
                                 r * sin(v) * (a + sin(u))],
          (0, 2 * pi), (0, 2 * pi), (True, True), (80, 40),
          note="a torus whose tube is fat on one side", R=2.0, r=0.6, a=1.5)
    entry("twisted_eight_torus",
          lambda u, v, R, r: [(R + r * (cos(u / 2.0) * sin(v) - sin(u / 2.0)
                                        * sin(2 * v))) * cos(u),
                              (R + r * (cos(u / 2.0) * sin(v) - sin(u / 2.0)
                                        * sin(2 * v))) * sin(u),
                              r * (sin(u / 2.0) * sin(v) + cos(u / 2.0)
                                   * sin(2 * v))],
          (0, 2 * pi), (0, 2 * pi), (False, True), (120, 60),
          note="a figure-eight cross-section that twists once around",
          R=2.0, r=1.0)
    entry("wave_ball",
          lambda u, v: [u * cos(cos(u)) * cos(v), u * cos(cos(u)) * sin(v),
                        u * sin(cos(u))],
          (0, 14.5), (0, 2 * pi), (False, True), (160, 40),
          note="rings that ripple outwards")
    return S


#: The named surfaces: ``add.SURFACES["apple"]`` holds the formula ``f``,
#: the ranges ``u`` and ``v``, the ``wrap`` flags, a default ``grid``, a
#: one-line ``note`` and the constants ``params``.  Draw one with
#: :func:`surface`.
SURFACES = _catalog()


def surface_names():
    """The names :func:`surface` understands, alphabetically."""
    return sorted(SURFACES)


def surface_function(name, **params):
    """The ``f(u, v) -> [x, y, z]`` of a named surface, with its constants
    filled in (override any of them by keyword).  Handy for feeding
    :func:`parametric` yourself with a different range or colouring."""
    entry = SURFACES[name]
    values = dict(entry["params"])
    values.update(params)
    f = entry["f"]
    if values:
        return lambda u, v: f(u, v, **values)
    return f


def surface(name, center=(0, 0, 0), size=None, grid=None, color=None,
            thickness=0.0, double_sided=False, **params):
    """Draw one of the catalogued surfaces by name -- see :func:`surface_names`.

    ``size`` scales the surface so that its largest dimension is ``size``
    (leave it out for the natural size); ``grid`` is the number of cells,
    one number or ``[along_u, along_v]``.  ``color`` may be a function
    ``color(u, v)`` as with :func:`parametric`, and the surface's own
    constants can be changed by keyword::

        add.surface("klein_bottle", [0, 0, 0], 4, 120, "teal")
        add.surface("dini", [6, 0, 0], 4, color=lambda u, v: add.hsv(u / 12))
        add.surface("pillow", size=3, a=0.9, thickness=0.1)
    """
    entry = SURFACES[name]
    f = surface_function(name, **params)
    if grid is None:
        gu, gv = entry["grid"]
    elif isinstance(grid, (list, tuple)):
        gu, gv = grid[0], grid[1]
    else:
        gu = gv = int(grid)
    (u0, u1), (v0, v1) = entry["u"], entry["v"]
    wu, wv = entry["wrap"]
    push()
    parametric(f, u0, u1, gu, v0, v1, gv, color, wrap_u=wu, wrap_v=wv,
               flip=entry.get("flip", False), thickness=thickness,
               double_sided=double_sided)
    M = pop()
    if size is not None:
        M = fit(M, size)
    M = place(M, center)
    _scene.extend(M)


# ============================================================================
# 15. Measuring a mesh
# ============================================================================

def bbox(M=None):
    """``[[xmin, ymin, zmin], [xmax, ymax, zmax]]`` of a mesh."""
    M = as_mesh(M)
    if not M.V:
        return [[0, 0, 0], [0, 0, 0]]
    lo = [min(p[a] for p in M.V) for a in range(3)]
    hi = [max(p[a] for p in M.V) for a in range(3)]
    return [lo, hi]


def size(M=None):
    """The width, height and depth of a mesh."""
    lo, hi = bbox(M)
    return [hi[a] - lo[a] for a in range(3)]


def center(M=None):
    """The average of all vertices (what add.py 1.2 called the centre)."""
    M = as_mesh(M)
    if not M.V:
        return [0.0, 0.0, 0.0]
    n = float(len(M.V))
    return [sum(p[a] for p in M.V) / n for a in range(3)]


#: Private handle on :func:`center`, for functions whose own parameter is
#: called ``center``.
_centroid = center


def middle(M=None):
    """The centre of the bounding box -- usually what you actually want."""
    lo, hi = bbox(M)
    return [(lo[a] + hi[a]) / 2.0 for a in range(3)]


def area(M=None):
    """Total surface area."""
    M = as_mesh(M)
    total = 0.0
    for f in M.F:
        if len(f) < 3:
            continue
        a = M.V[f[0]]
        for t in range(1, len(f) - 1):
            total += _norm(_cross(_sub(M.V[f[t]], a),
                                  _sub(M.V[f[t + 1]], a))) / 2.0
    return total


def volume(M=None):
    """Enclosed volume.  Meaningful only for a closed (watertight) mesh."""
    return _signed_volume(as_mesh(M), 0) / 6.0


# ============================================================================
# 16. Moving, turning and reshaping a mesh
# ============================================================================
# Every function here takes a mesh and returns a NEW mesh; the original is
# left alone.  That is what makes chains like
#     add.move(add.rotateY(M, a, [0, 0, 0]), [0, 3, 0])
# safe to write.

def _mapped(M, f, flip=False):
    """Apply point function ``f`` to a copy of the mesh."""
    M = as_mesh(M)
    UV = None
    if M.UV is not None:
        UV = [None if t is None else (list(reversed(t)) if flip else list(t))
              for t in M.UV]
    out = Mesh([list(f(p)) for p in M.V],
               [list(reversed(x)) if flip else list(x) for x in M.F],
               list(M.C), UV)
    return out


def move(M, V):
    """Shift a mesh by vector ``V``."""
    return _mapped(M, lambda p: (p[0] + V[0], p[1] + V[1], p[2] + V[2]))


def place(M, at, use_bbox=True):
    """Move a mesh so that its centre sits exactly at ``at``."""
    c = middle(M) if use_bbox else center(M)
    return move(M, [at[0] - c[0], at[1] - c[1], at[2] - c[2]])


def rotateX(M, angle, P=(0, 0, 0)):
    """Turn a mesh around the X axis through point ``P``."""
    cs, sn = math.cos(angle), math.sin(angle)

    def f(p):
        y, z = p[1] - P[1], p[2] - P[2]
        return (p[0], P[1] + y * cs - z * sn, P[2] + y * sn + z * cs)
    return _mapped(M, f)


def rotateY(M, angle, P=(0, 0, 0)):
    """Turn a mesh around the Y axis through point ``P``."""
    cs, sn = math.cos(angle), math.sin(angle)

    def f(p):
        x, z = p[0] - P[0], p[2] - P[2]
        return (P[0] + x * cs + z * sn, p[1], P[2] + z * cs - x * sn)
    return _mapped(M, f)


def rotateZ(M, angle, P=(0, 0, 0)):
    """Turn a mesh around the Z axis through point ``P``."""
    cs, sn = math.cos(angle), math.sin(angle)

    def f(p):
        x, y = p[0] - P[0], p[1] - P[1]
        return (P[0] + x * cs - y * sn, P[1] + x * sn + y * cs, p[2])
    return _mapped(M, f)


def rotate(M, axis, angle, P=(0, 0, 0)):
    """Turn a mesh by ``angle`` around any axis through ``P``.

    Uses Rodrigues' formula, so ``axis`` can point anywhere::

        M = add.rotate(M, [1, 1, 0], math.pi / 3, [0, 0, 0])
    """
    k = _unit(axis)
    cs, sn = math.cos(angle), math.sin(angle)

    def f(p):
        v = _sub(p, P)
        kv = _cross(k, v)
        d = _dot(k, v) * (1.0 - cs)
        return (P[0] + v[0] * cs + kv[0] * sn + k[0] * d,
                P[1] + v[1] * cs + kv[1] * sn + k[1] * d,
                P[2] + v[2] * cs + kv[2] * sn + k[2] * d)
    return _mapped(M, f)


def zoom(M, s, about=None):
    """Scale a mesh by factor ``s`` (about its own centre by default)."""
    c = center(M) if about is None else about
    return _mapped(M, lambda p: (c[0] + (p[0] - c[0]) * s,
                                 c[1] + (p[1] - c[1]) * s,
                                 c[2] + (p[2] - c[2]) * s), flip=(s < 0))


def stretch(M, s, about=None):
    """Scale by a different factor along each axis, ``s = [sx, sy, sz]``."""
    c = center(M) if about is None else about
    flip = (s[0] * s[1] * s[2]) < 0
    return _mapped(M, lambda p: (c[0] + (p[0] - c[0]) * s[0],
                                 c[1] + (p[1] - c[1]) * s[1],
                                 c[2] + (p[2] - c[2]) * s[2]), flip=flip)


def fit(M, target=1.0, about=None):
    """Scale a mesh so its largest dimension equals ``target``."""
    d = max(size(M))
    return zoom(M, (target / d) if d > EPS else 1.0, about)


def mirror(M, point=(0, 0, 0), normal=(1, 0, 0)):
    """Reflect a mesh in the plane through ``point`` with the given normal.

    The face winding is reversed too, so the reflection is not inside out.
    """
    n = _unit(normal)

    def f(p):
        d = 2.0 * _dot(_sub(p, point), n)
        return (p[0] - n[0] * d, p[1] - n[1] * d, p[2] - n[2] * d)
    return _mapped(M, f, flip=True)


def transform(M, matrix):
    """Apply a 3x3 or 4x4 matrix (given as a list of rows)."""
    m = matrix

    def f(p):
        x = m[0][0] * p[0] + m[0][1] * p[1] + m[0][2] * p[2]
        y = m[1][0] * p[0] + m[1][1] * p[1] + m[1][2] * p[2]
        z = m[2][0] * p[0] + m[2][1] * p[1] + m[2][2] * p[2]
        if len(m[0]) > 3:
            x += m[0][3]
            y += m[1][3]
            z += m[2][3]
        return (x, y, z)
    det = (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
           - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
           + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))
    return _mapped(M, f, flip=(det < 0))


def deform(M, f):
    """Bend a mesh with any function you like: ``f(p) -> new point``.

    The single most powerful function in the library::

        wave = add.deform(M, lambda p: [p[0], p[1] + math.sin(p[0]), p[2]])
    """
    return _mapped(M, lambda p: f(list(p)))


def twist(M, angle, axis=(0, 1, 0), P=(0, 0, 0)):
    """Rotate a mesh progressively along ``axis`` -- a corkscrew.

    ``angle`` is the turn applied per unit of distance along the axis.
    """
    k = _unit(axis)

    def f(p):
        h = _dot(_sub(p, P), k)
        a = angle * h
        cs, sn = math.cos(a), math.sin(a)
        v = _sub(p, P)
        kv = _cross(k, v)
        d = _dot(k, v) * (1.0 - cs)
        return (P[0] + v[0] * cs + kv[0] * sn + k[0] * d,
                P[1] + v[1] * cs + kv[1] * sn + k[1] * d,
                P[2] + v[2] * cs + kv[2] * sn + k[2] * d)
    return _mapped(M, f)


def taper(M, factor, axis=1, P=(0, 0, 0)):
    """Shrink (or grow) a mesh along ``axis``; ``axis`` is 0=X, 1=Y, 2=Z.

    ``factor`` is the extra scale gained per unit of distance, so
    ``taper(M, -0.2)`` makes the model 20% thinner for every unit it rises.
    """
    other = [a for a in range(3) if a != axis]

    def f(p):
        s = 1.0 + factor * (p[axis] - P[axis])
        q = list(p)
        for a in other:
            q[a] = P[a] + (p[a] - P[a]) * s
        return q
    return _mapped(M, f)


def bend(M, angle, axis=1, around=0, P=(0, 0, 0)):
    """Bend a mesh into an arc.

    Distance along ``axis`` becomes an angle turning about ``around``;
    ``angle`` is radians per unit of length.
    """
    third = 3 - axis - around

    def f(p):
        q = list(p)
        h = p[axis] - P[axis]
        a = angle * h
        if abs(angle) < EPS:
            return q
        r = 1.0 / angle
        d = p[third] - P[third]
        q[axis] = P[axis] + (r - d) * math.sin(a)
        q[third] = P[third] + r - (r - d) * math.cos(a)
        return q
    return _mapped(M, f)


def jitter(M, amount=0.05, seed=None):
    """Nudge every vertex a little at random -- an easy hand-made look."""
    r = _random if seed is None else _random.Random(seed)
    return _mapped(M, lambda p: (p[0] + r.uniform(-amount, amount),
                                 p[1] + r.uniform(-amount, amount),
                                 p[2] + r.uniform(-amount, amount)))


# ============================================================================
# 17. Colour
# ============================================================================

def color(M, RGB):
    """Paint the whole mesh one colour and return the painted copy."""
    M = as_mesh(M)
    c = rgb(RGB)
    out = M.copy()
    out.C = [c] * len(M.F)
    return out


def opacity(M, alpha):
    """A copy of the mesh with every face made see-through: ``alpha`` is the
    opacity, 0 invisible, 1 solid (which also removes any transparency).

    Colours and textures are kept; the opacity goes into the ``.mtl`` file
    of an ``.obj`` model.  For one colour at a time use :func:`transparent`::

        glass = add.opacity(add.make(add.box, [0, 0, 0], 2, "sky"), 0.3)
    """
    M = as_mesh(M)
    out = M.copy()
    out.C = [rgb((c[0], c[1], c[2], alpha) + tuple(c[4:5])) for c in M.C]
    return out


#: Private handle on :func:`color`, for functions whose own parameter is
#: called ``color``.
_paint = color


def texture(M, image, mapping="box", scale=1.0, color="white", offset=(0, 0)):
    """Wrap an image around a mesh and return the textured copy.

    ``image`` is the file name of a picture (``.png`` or ``.jpg``) that will
    sit next to the ``.obj`` -- put both, with the ``.mtl``, in one zip for
    Sketchfab.  The mesh remembers a texture coordinate for every corner,
    worked out from the ``mapping``:

    * ``"box"`` (default): each face is projected along its dominant axis,
      so the picture repeats every ``scale`` units on every side of a box;
    * ``"xy"``, ``"xz"``, ``"yz"``: one flat projection for all faces;
    * ``"fit"``: the picture stretched once over the mesh, seen from the front
      (XY), whatever its size;
    * ``"sphere"`` / ``"cylinder"``: wrapped around the mesh's centre, with
      ``scale`` copies around;
    * or your own function ``mapping(point, normal) -> (u, v)``.

    ``color`` tints the picture (white shows it as it is) and keeps any
    transparency the faces had.  Apply textures last: transforms, ``clean``
    and ``merge`` keep them, but booleans, subdivision and ``solidify``
    rebuild the faces and drop them.  ``.off`` files cannot hold textures;
    ``.obj`` + ``.mtl`` can (``map_Kd``)::

        add.write_png("bricks.png", rows)                   # or any picture
        wall = add.texture(add.make(add.cuboid, [0, 0, 0], [4, 2, 0.3]),
                           "bricks.png", "box", scale=1.0)
        add.mesh(wall)
        add.save("house.obj")
    """
    M = as_mesh(M)
    lo, hi = bbox(M)
    mid = [(lo[a] + hi[a]) / 2.0 for a in range(3)]
    span = [max(hi[a] - lo[a], EPS) for a in range(3)]
    ox, oy = offset[0], offset[1]
    s = float(scale) if scale else 1.0

    def planar(i, j):
        return lambda p, n: ((p[i] - ox) / s, (p[j] - oy) / s)

    if callable(mapping):
        fn = mapping
    elif mapping == "box":
        flat = {0: planar(2, 1), 1: planar(0, 2), 2: planar(0, 1)}

        def fn(p, n):
            axis = max(range(3), key=lambda a: abs(n[a]))
            return flat[axis](p, n)
    elif mapping in ("xy", "xz", "yz"):
        fn = {"xy": planar(0, 1), "xz": planar(0, 2), "yz": planar(2, 1)}[mapping]
    elif mapping == "fit":
        def fn(p, n):
            return ((p[0] - lo[0]) / span[0], (p[1] - lo[1]) / span[1])
    elif mapping == "sphere":
        def fn(p, n):
            d = _unit(_sub(p, mid))
            return ((math.atan2(d[2], d[0]) / (2 * math.pi) + 0.5) * s,
                    math.asin(max(-1.0, min(1.0, d[1]))) / math.pi + 0.5)
    elif mapping == "cylinder":
        def fn(p, n):
            return ((math.atan2(p[2] - mid[2], p[0] - mid[0]) / (2 * math.pi)
                     + 0.5) * s, (p[1] - lo[1]) / span[1])
    else:
        raise ValueError("unknown texture mapping: %r" % (mapping,))

    out = M.copy()
    out.UV = []
    tint = rgb(color) if color is not None else None
    for i, f in enumerate(M.F):
        n = _unit(_face_normal(M, f))
        uv = [tuple(fn(M.V[k], n)) for k in f]
        if mapping in ("sphere", "cylinder"):          # mend the seam
            us = [t[0] for t in uv]
            if max(us) - min(us) > 0.5 * s:
                uv = [(t[0] + s if t[0] < (min(us) + max(us)) / 2.0 else t[0], t[1])
                      for t in uv]
        out.UV.append(uv)
        base = tint if tint is not None else M.C[i]
        alpha = M.C[i][3] if len(M.C[i]) > 3 else 1.0
        out.C[i] = rgb((base[0], base[1], base[2], alpha, image))
    return out


def color_by(M, fn):
    """Colour every face according to where it is: ``fn(point) -> colour``.

    ``point`` is the centre of the face, so a rainbow by height is::

        M = add.color_by(M, lambda p: add.hsv(p[1] / 10.0))
    """
    M = as_mesh(M)
    out = M.copy()
    for i, f in enumerate(M.F):
        n = float(len(f))
        p = [sum(M.V[k][a] for k in f) / n for a in range(3)]
        out.C[i] = rgb(fn(p))
    return out


def color_gradient(M, a, b, axis=1):
    """Fade the mesh from colour ``a`` to colour ``b`` along one axis."""
    lo, hi = bbox(M)
    span = hi[axis] - lo[axis]
    if span < EPS:
        return color(M, a)
    return color_by(M, lambda p: gradient((p[axis] - lo[axis]) / span, a, b))


def color_random(M, seed=None):
    """Give every face its own random colour."""
    r = _random if seed is None else _random.Random(seed)
    M = as_mesh(M)
    out = M.copy()
    out.C = [(r.randint(0, 255), r.randint(0, 255), r.randint(0, 255))
             for _ in M.F]
    return out


def palette(M=None):
    """The distinct colours of a mesh, most used first, as
    ``[(colour, number of faces), ...]``."""
    M = as_mesh(M)
    count = {}
    for c in M.C:
        count[c] = count.get(c, 0) + 1
    return sorted(count.items(), key=lambda item: (-item[1], item[0]))


def limit_colors(M, n=50):
    """Reduce a mesh to at most ``n`` distinct colours and return the copy.

    Every colour in an ``.obj`` file becomes a *material*, and Sketchfab
    merges materials beyond its limit of 100 (so keep to 50 to be safe).
    Gradients and ``color_by`` paint jobs easily produce thousands of
    shades; this groups similar shades together (median-cut quantisation,
    weighted by how many faces use each shade) and replaces each group by
    its average, so the picture hardly changes::

        model = add.limit_colors(add.layer(), 50)
        add.save("model.obj", model)
    """
    M = as_mesh(M)
    counts = {}
    for c in M.C:
        if len(c) == 3:                       # transparent and textured
            counts[c] = counts.get(c, 0) + 1  # materials are left alone
    if len(counts) <= n:
        return M.copy()
    boxes = [list(counts.items())]
    while len(boxes) < n:
        # Split the box whose colours spread the most (weighted by use).
        best, best_span, best_axis = None, -1, 0
        for b in boxes:
            if len(b) < 2:
                continue
            for axis in range(3):
                span = max(c[axis] for c, w in b) - min(c[axis] for c, w in b)
                if span > best_span:
                    best, best_span, best_axis = b, span, axis
        if best is None:
            break
        best.sort(key=lambda item: item[0][best_axis])
        total = sum(w for c, w in best)
        acc, cut = 0, 0
        for cut in range(len(best) - 1):
            acc += best[cut][1]
            if acc * 2 >= total:
                break
        boxes.remove(best)
        boxes.append(best[:cut + 1])
        boxes.append(best[cut + 1:])
    remap = {}
    for b in boxes:
        total = float(sum(w for c, w in b))
        mean = tuple(int(round(sum(c[a] * w for c, w in b) / total))
                     for a in range(3))
        for c, w in b:
            remap[c] = mean
    out = M.copy()
    out.C = [remap.get(c, c) for c in M.C]
    return out


# ============================================================================
# 18. Copies and patterns
# ============================================================================

def repeat(M, n, step):
    """Apply a transformation ``step(mesh, i)`` again and again, and merge.

    The general pattern maker -- every other array function below is a
    three-line wrapper around it::

        spiral = add.repeat(brick, 40,
                            lambda X, i: add.move(add.rotateY(X, i * 0.3), [0, i * 0.2, 0]))
    """
    out = Mesh()
    base = as_mesh(M)
    for i in range(n):
        out.extend(step(base, i))
    return out


def array_linear(M, step, n):
    """``n`` copies in a row, each moved a further ``step`` along."""
    return repeat(M, n, lambda X, i: move(X, [step[0] * i, step[1] * i,
                                              step[2] * i]))


def array_grid(M, steps, counts):
    """A 2D or 3D block of copies; ``steps`` and ``counts`` have 3 entries."""
    out = Mesh()
    base = as_mesh(M)
    for i in range(counts[0]):
        for j in range(counts[1]):
            for k in range(counts[2]):
                out.extend(move(base, [steps[0] * i, steps[1] * j,
                                       steps[2] * k]))
    return out


def array_radial(M, n, axis=(0, 1, 0), P=(0, 0, 0), angle=2.0 * math.pi,
                 rise=0.0):
    """``n`` copies arranged around an axis; ``rise`` makes it a spiral stair."""
    return repeat(M, n, lambda X, i: move(
        rotate(X, axis, angle * i / float(n), P),
        _scale(_unit(axis), rise * i)))


def array_mirror(M, point=(0, 0, 0), normal=(1, 0, 0)):
    """The mesh together with its mirror image."""
    return merge([M, mirror(M, point, normal)])


# ============================================================================
# 19. Placing parts: aim, scatter, line up
# ============================================================================
# The functions in the previous section make copies on a regular pattern.
# These put a part *somewhere in particular*: pointing along a direction,
# on the ground, at random spots on a landscape, or strung along a curve.

def aim(M, direction, axis=(0, 1, 0), P=(0, 0, 0)):
    """Turn a mesh so that its ``axis`` points along ``direction``.

    The rotation is the smallest one that does the job, about point ``P``.
    A cannon built pointing up (``axis=[0, 1, 0]``) is aimed at a target
    with ``add.aim(cannon, add.direction(pivot, target), P=pivot)``.
    """
    a, b = _unit(axis), _unit(direction)
    c = _cross(a, b)
    s, d = _norm(c), _dot(a, b)
    if s < 1e-12:
        if d > 0:
            return copy(M)
        return rotate(M, _perp(a), math.pi, P)
    return rotate(M, c, math.atan2(s, d), P)


def ground(M, y=0.0):
    """Move a mesh straight down (or up) so that its lowest point is at ``y``."""
    lo, hi = bbox(M)
    return move(M, [0.0, y - lo[1], 0.0])


def align(M, at=(0, 0, 0), anchor=(0, -1, 0)):
    """Move a mesh so that a chosen point of its bounding box lands on ``at``.

    ``anchor`` picks that point per axis: ``-1`` the minimum, ``0`` the
    middle, ``1`` the maximum.  The default ``(0, -1, 0)`` is "bottom
    centre", so ``add.align(house, [5, 0, 5])`` stands the house on the
    ground at (5, 5); ``anchor=(-1, -1, -1)`` puts its corner there.
    """
    lo, hi = bbox(M)
    shift = []
    for a in range(3):
        if anchor[a] < 0:
            p = lo[a]
        elif anchor[a] > 0:
            p = hi[a]
        else:
            p = (lo[a] + hi[a]) / 2.0
        shift.append(at[a] - p)
    return move(M, shift)


def random_points(n, lo, hi, seed=None, height=None):
    """``n`` random points in the box ``lo .. hi`` (each a 3-vector).

    With ``height(x, z)`` the Y coordinate is taken from that function
    instead, so the points lie *on* a landscape made with ``grid(...,
    height=...)``.  ``seed`` makes the result repeatable.
    """
    rnd = _random.Random(seed) if seed is not None else _random
    out = []
    for _ in range(n):
        x = rnd.uniform(lo[0], hi[0])
        z = rnd.uniform(lo[2], hi[2])
        y = height(x, z) if height is not None else rnd.uniform(lo[1], hi[1])
        out.append([x, y, z])
    return out


def scatter(M, points, seed=None, spin=True, scale=(1.0, 1.0), axis=(0, 1, 0)):
    """Copies of a mesh at every point, each turned and sized at random.

    The mesh should be built around the origin (its origin is what lands on
    the point).  ``spin`` turns each copy by a random angle about ``axis``;
    ``scale`` is the range of random size factors.  A forest::

        add.tree([0, 0, 0], 3)
        one = add.layer()
        spots = add.random_points(40, [-20, 0, -20], [20, 0, 20], seed=1, height=hills)
        add.mesh(add.scatter(one, spots, seed=1, scale=(0.7, 1.3)))
    """
    rnd = _random.Random(seed) if seed is not None else _random
    base = as_mesh(M)
    out = Mesh()
    for p in points:
        X = base
        s = rnd.uniform(scale[0], scale[1])
        if abs(s - 1.0) > EPS:
            X = zoom(X, s, (0, 0, 0))
        if spin:
            X = rotate(X, axis, rnd.uniform(0, 2 * math.pi))
        out.extend(move(X, p))
    return out


def along(M, path, n, t0=0.0, t1=1.0, axis=(0, 1, 0), closed=False, scale=None):
    """``n`` copies of a mesh strung along a curve, each turned to follow it.

    ``path`` is a function ``path(t)`` or a list of points.  The mesh's
    ``axis`` is aimed along the curve's direction at every copy (pass
    ``axis=None`` to keep the copies upright); ``scale`` is a number or a
    function ``scale(t)``.  Beads on a string, wagons on a track, stones on
    an arch::

        add.along(wagon, track, 12, 0, 1, axis=[1, 0, 0])
    """
    base = as_mesh(M)
    if callable(path):
        steps = n if closed else max(1, n - 1)
        ts = [t0 + (t1 - t0) * i / float(steps) for i in range(n)]
        pts = [tuple(path(t)) for t in ts]
        h = (t1 - t0) * 1e-4
        dirs = [_sub(path(t + h), path(t - h)) for t in ts]
    else:
        pts = [tuple(p) for p in path]
        n = len(pts)
        ts = [i / float(n if closed else max(1, n - 1)) for i in range(n)]
        dirs = []
        for i in range(n):
            a = pts[i - 1] if (i > 0 or closed) else pts[i]
            b = pts[(i + 1) % n] if (i < n - 1 or closed) else pts[i]
            dirs.append(_sub(b, a))
    out = Mesh()
    for p, t, d in zip(pts, ts, dirs):
        X = base
        if scale is not None:
            s = scale(t) if callable(scale) else scale
            X = zoom(X, s, (0, 0, 0))
        if axis is not None and _norm(d) > EPS:
            X = aim(X, d, axis)
        out.extend(move(X, p))
    return out


# ============================================================================
# 20. Repairing a model
# ============================================================================
# Models built by stacking shapes tend to collect three kinds of rubbish:
# vertices that sit on top of each other, faces that are repeated, and walls
# buried inside the model where two parts touch.  None of it is visible, but
# all of it bloats the file and upsets 3D printing and boolean operations.
# `clean()` gets rid of all three.

def _cell_keys(p, tol):
    """Grid cell(s) a point may belong to, allowing for rounding at the edges."""
    ranges = []
    for a in range(3):
        q = p[a] / tol
        k = int(math.floor(q + 0.5))
        frac = q + 0.5 - math.floor(q + 0.5)
        if frac < 0.25:
            ranges.append((k, k - 1))
        elif frac > 0.75:
            ranges.append((k, k + 1))
        else:
            ranges.append((k,))
    out = []
    for i in ranges[0]:
        for j in ranges[1]:
            for k in ranges[2]:
                out.append((i, j, k))
    return out


def _weld(M, tol=1e-7):
    """Merge vertices closer than ``tol`` (in place).  Returns how many went."""
    lookup = {}
    remap = [0] * len(M.V)
    newV = []
    for i, p in enumerate(M.V):
        found = None
        for key in _cell_keys(p, tol):
            j = lookup.get(key)
            if j is not None:
                q = newV[j]
                if (abs(q[0] - p[0]) <= tol and abs(q[1] - p[1]) <= tol
                        and abs(q[2] - p[2]) <= tol):
                    found = j
                    break
        if found is None:
            found = len(newV)
            newV.append(list(p))
            for key in _cell_keys(p, tol):
                lookup.setdefault(key, found)
        remap[i] = found
    removed = len(M.V) - len(newV)
    M.V = newV
    for f in M.F:
        for i in range(len(f)):
            f[i] = remap[f[i]]
    return removed


def _keep_faces(M, keep):
    """Keep only the faces whose index is in ``keep`` (in place)."""
    removed = len(M.F) - len(keep)
    M.F = [M.F[i] for i in keep]
    M.C = [M.C[i] for i in keep]
    if M.UV is not None:
        M.UV = [M.UV[i] for i in keep]
    return removed


def _drop_degenerate(M, tol=1e-12):
    """Delete faces with no area and remove repeated corners (in place)."""
    keep = []
    for k, f in enumerate(M.F):
        clean_f = []
        uv = M.UV[k] if M.UV is not None else None
        clean_uv = [] if uv is not None else None
        for t, i in enumerate(f):                    # drop repeated corners
            if not clean_f or clean_f[-1] != i:
                clean_f.append(i)
                if clean_uv is not None:
                    clean_uv.append(uv[t])
        if len(clean_f) > 1 and clean_f[0] == clean_f[-1]:
            clean_f.pop()
            if clean_uv is not None:
                clean_uv.pop()
        if len(clean_f) < 3:
            continue
        if len(set(clean_f)) < 3:
            continue
        if _norm(_face_normal(M, clean_f)) <= tol:
            continue
        M.F[k] = clean_f
        if clean_uv is not None:
            M.UV[k] = clean_uv
        keep.append(k)
    return _keep_faces(M, keep)


def _dedup_faces(M):
    """Delete repeats of a face that is already there (in place)."""
    seen = set()
    keep = []
    for k, f in enumerate(M.F):
        key = tuple(sorted(f))
        if key in seen:
            continue
        seen.add(key)
        keep.append(k)
    return _keep_faces(M, keep)


def _drop_internal(M):
    """Delete pairs of identical faces that point opposite ways (in place).

    That is exactly what you get where two solids touch -- a wall buried
    inside the model.  Both copies are useless, so both go.
    """
    groups = {}
    for i, f in enumerate(M.F):
        groups.setdefault(tuple(sorted(f)), []).append(i)
    drop = set()
    for key, idx in groups.items():
        if len(idx) < 2:
            continue
        forward, backward = [], []
        for i in idx:
            (forward if _winding(M.F[i]) else backward).append(i)
        pairs = min(len(forward), len(backward))
        for t in range(pairs):
            drop.add(forward[t])
            drop.add(backward[t])
    if not drop:
        return 0
    return _keep_faces(M, [i for i in range(len(M.F)) if i not in drop])


def _winding(f):
    """True when the smallest index is followed by the smaller neighbour.

    A cheap, orientation-sensitive signature for a face's corner order.
    """
    k = f.index(min(f))
    return f[(k + 1) % len(f)] < f[k - 1]


def _drop_unused(M):
    """Delete vertices no face refers to (in place)."""
    used = set()
    for f in M.F:
        used.update(f)
    if len(used) == len(M.V):
        return 0
    remap = {}
    newV = []
    for i, p in enumerate(M.V):
        if i in used:
            remap[i] = len(newV)
            newV.append(p)
    removed = len(M.V) - len(newV)
    M.V = newV
    for f in M.F:
        for i in range(len(f)):
            f[i] = remap[f[i]]
    return removed


def heal(M=None, tol=1e-7):
    """Close the tiny gaps left where an edge runs past another vertex.

    After a boolean operation a long edge of one face often has two shorter
    edges of neighbouring faces lying along it, with a vertex in the middle
    that the long edge knows nothing about.  These "T-junctions" leave a
    hairline crack: the model looks fine but is not watertight, which upsets
    3D printing and further boolean operations.  Adding the missing corner to
    the long face fixes it.
    """
    M = as_mesh(M).copy()
    if not M.F or not M.V:
        return M

    # A grid roughly one edge-length wide keeps the search local.
    total = 0.0
    count = 0
    for f in M.F:
        n = len(f)
        for i in range(n):
            total += _norm(_sub(M.V[f[i]], M.V[f[(i + 1) % n]]))
            count += 1
    cell = max(total / max(1, count), tol * 10.0)

    grid = {}
    for idx, p in enumerate(M.V):
        key = (int(math.floor(p[0] / cell)), int(math.floor(p[1] / cell)),
               int(math.floor(p[2] / cell)))
        grid.setdefault(key, []).append(idx)

    def nearby(pa, pb):
        """Vertex indices in the grid cells the segment could pass through."""
        lo, hi = [], []
        for a in range(3):
            lo.append(int(math.floor((min(pa[a], pb[a]) - tol) / cell)))
            hi.append(int(math.floor((max(pa[a], pb[a]) + tol) / cell)))
        spread = 1
        for a in range(3):
            spread *= hi[a] - lo[a] + 1
        out = []
        if spread <= 512:                       # short edge: sweep its box
            for cx in range(lo[0], hi[0] + 1):
                for cy in range(lo[1], hi[1] + 1):
                    for cz in range(lo[2], hi[2] + 1):
                        out.extend(grid.get((cx, cy, cz), ()))
            return out
        # Long edge: walk along it instead of filling its whole box.
        length = _norm(_sub(pb, pa))
        steps = min(4000, int(3.0 * length / cell) + 2)
        seen_cells = set()
        for s in range(steps + 1):
            t = s / float(steps)
            key = (int(math.floor((pa[0] + (pb[0] - pa[0]) * t) / cell)),
                   int(math.floor((pa[1] + (pb[1] - pa[1]) * t) / cell)),
                   int(math.floor((pa[2] + (pb[2] - pa[2]) * t) / cell)))
            if key in seen_cells:
                continue
            seen_cells.add(key)
            for a in (-1, 0, 1):
                for b in (-1, 0, 1):
                    for c in (-1, 0, 1):
                        out.extend(grid.get((key[0] + a, key[1] + b,
                                             key[2] + c), ()))
        return out

    newF = []
    newUV = [] if M.UV is not None else None
    for k, f in enumerate(M.F):
        n = len(f)
        out = []
        uv = M.UV[k] if M.UV is not None else None
        out_uv = [] if uv is not None else None
        for i in range(n):
            a, b = f[i], f[(i + 1) % n]
            out.append(a)
            if out_uv is not None:
                out_uv.append(uv[i])
            pa, pb = M.V[a], M.V[b]
            d = _sub(pb, pa)
            L2 = _dot(d, d)
            if L2 <= tol * tol:
                continue
            hits = []
            for v in nearby(pa, pb):
                if v == a or v == b:
                    continue
                pv = M.V[v]
                t = ((pv[0] - pa[0]) * d[0] + (pv[1] - pa[1]) * d[1]
                     + (pv[2] - pa[2]) * d[2]) / L2
                if t <= 1e-9 or t >= 1.0 - 1e-9:
                    continue
                if (abs(pa[0] + d[0] * t - pv[0]) <= tol
                        and abs(pa[1] + d[1] * t - pv[1]) <= tol
                        and abs(pa[2] + d[2] * t - pv[2]) <= tol):
                    hits.append((t, v))
            if hits:
                hits.sort()
                last = None
                for t, v in hits:
                    if v != last:
                        out.append(v)
                        if out_uv is not None:
                            ua, ub = uv[i], uv[(i + 1) % n]
                            out_uv.append((ua[0] + (ub[0] - ua[0]) * t,
                                           ua[1] + (ub[1] - ua[1]) * t))
                    last = v
        newF.append(out)
        if newUV is not None:
            newUV.append(out_uv)
    M.F = newF
    M.UV = newUV
    return M


def triangulate(M=None):
    """Return a copy in which every face is a triangle (fan triangulation)."""
    M = as_mesh(M)
    out = Mesh([list(p) for p in M.V], [], [])
    for k, (f, c) in enumerate(zip(M.F, M.C)):
        uv = M.UV[k] if M.UV is not None else None
        for t in range(1, len(f) - 1):
            out.add_face([f[0], f[t], f[t + 1]], c,
                         None if uv is None else [uv[0], uv[t], uv[t + 1]])
    return out


def fix_normals(M=None, outward=True):
    """Make every face of a copy point the same way -- and, if the model is
    closed, point outward.

    Faces are walked from neighbour to neighbour: two faces that share an edge
    must run along it in opposite directions.  Each connected piece is then
    flipped as a whole if its volume came out negative.
    """
    M = as_mesh(M).copy()
    edge_faces = {}
    for i, f in enumerate(M.F):
        n = len(f)
        for t in range(n):
            a, b = f[t], f[(t + 1) % n]
            edge_faces.setdefault((a, b) if a < b else (b, a), []).append(i)

    visited = [False] * len(M.F)
    for start in range(len(M.F)):
        if visited[start]:
            continue
        component = [start]
        visited[start] = True
        stack = [start]
        while stack:
            i = stack.pop()
            f = M.F[i]
            n = len(f)
            for t in range(n):
                a, b = f[t], f[(t + 1) % n]
                key = (a, b) if a < b else (b, a)
                for j in edge_faces.get(key, ()):
                    if visited[j]:
                        continue
                    g = M.F[j]
                    m = len(g)
                    same = False
                    for s in range(m):
                        if g[s] == a and g[(s + 1) % m] == b:
                            same = True
                            break
                    if same:                       # neighbour disagrees
                        g.reverse()
                        if M.UV is not None and M.UV[j] is not None:
                            M.UV[j].reverse()
                    visited[j] = True
                    component.append(j)
                    stack.append(j)
        if outward:
            part = Mesh(M.V, [M.F[i] for i in component],
                        [M.C[i] for i in component])
            if _signed_volume(part, 0) < 0:
                for i in component:
                    M.F[i].reverse()
                    if M.UV is not None and M.UV[i] is not None:
                        M.UV[i].reverse()
    return M


def clean(M=None, tol=1e-7, weld=True, degenerate=True, duplicates=True,
          internal=True, unused=True, normals=False, report=False):
    """Repair a model and return the tidy copy.

    By default it welds coincident vertices, throws away zero-area faces,
    removes repeated faces and removes the walls buried where two solids
    touch.  Pass ``normals=True`` to also make every face point outward, and
    ``report=True`` to get ``(mesh, report_dict)`` instead of just the mesh::

        model = add.clean(add.layer())
        add.mesh(model)
    """
    M = as_mesh(M).copy()
    info = {"vertices_removed": 0, "faces_removed": 0}
    if weld:
        info["vertices_removed"] += _weld(M, tol)
    if degenerate:
        info["faces_removed"] += _drop_degenerate(M)
    if internal:
        info["faces_removed"] += _drop_internal(M)
    if duplicates:
        info["faces_removed"] += _dedup_faces(M)
    if normals:
        M = fix_normals(M)
    if unused:
        info["vertices_removed"] += _drop_unused(M)
    if report:
        return M, info
    return M


# ============================================================================
# 21. Looking at a model
# ============================================================================

def stats(M=None):
    """A dictionary describing the model: counts, size, area, volume, health."""
    M = as_mesh(M)
    lo, hi = bbox(M)
    edges = {}
    for f in M.F:
        n = len(f)
        for t in range(n):
            a, b = f[t], f[(t + 1) % n]
            key = (a, b) if a < b else (b, a)
            edges[key] = edges.get(key, 0) + 1
    open_edges = sum(1 for v in edges.values() if v == 1)
    odd_edges = sum(1 for v in edges.values() if v > 2)
    groups = {}
    for f in M.F:
        groups.setdefault(tuple(sorted(f)), []).append(f)
    duplicate_faces = back_to_back = 0
    for same in groups.values():
        if len(same) < 2:
            continue
        forward = sum(1 for f in same if _winding(f))
        backward = len(same) - forward
        back_to_back += min(forward, backward)
        duplicate_faces += len(same) - 1 - min(forward, backward)
    return {
        "vertices": len(M.V),
        "faces": len(M.F),
        "triangles": sum(max(0, len(f) - 2) for f in M.F),
        "colors": len(set(M.C)),
        "bbox": [lo, hi],
        "size": [hi[a] - lo[a] for a in range(3)],
        "area": area(M),
        "volume": volume(M),
        "open_edges": open_edges,
        "non_manifold_edges": odd_edges,
        "duplicate_faces": duplicate_faces,
        "back_to_back_faces": back_to_back,
        "closed": open_edges == 0,
        "obj_bytes": obj_size(M),
        "transparent_faces": sum(1 for c in M.C if len(c) > 3 and c[3] < 1.0),
        "textures": sorted(set(c[4] for c in M.C if len(c) > 4)),
    }


#: Sketchfab: files up to 100 MB on the free plan (the course asks for 50)
#: and at most 100 materials, i.e. colours in an ``.obj`` (50 to be safe).
SKETCHFAB_MB = 50
SKETCHFAB_COLORS = 50


def check(M=None, min_faces=10000, min_colors=3, quiet=False,
          max_mb=SKETCHFAB_MB, max_colors=SKETCHFAB_COLORS):
    """Print a health report and say whether the model meets the assignment.

    The course asks for at least 10000 polygons and at least 3 colours, and
    an ``.obj`` that Sketchfab will take: under ``max_mb`` megabytes and
    ``max_colors`` colours (each colour is a material there).  This tells
    you where you stand and what still needs repairing::

        add.check()          # look at the current scene

    Returns ``True`` when every requirement is met.
    """
    s = stats(M)
    mb = s["obj_bytes"] / 1e6
    fits = mb <= max_mb and s["colors"] <= max_colors
    ok = s["faces"] >= min_faces and s["colors"] >= min_colors and fits
    if not quiet:
        mark = lambda good: "OK " if good else "!! "
        print("-" * 56)
        print("  vertices            %d" % s["vertices"])
        print("%s polygons            %d  (need %d)"
              % (mark(s["faces"] >= min_faces), s["faces"], min_faces))
        print("%s colours             %d  (need %d, at most %d materials for Sketchfab)"
              % (mark(min_colors <= s["colors"] <= max_colors), s["colors"],
                 min_colors, max_colors))
        print("%s .obj file size      %.1f MB  (at most %d MB for Sketchfab)"
              % (mark(mb <= max_mb), mb, max_mb))
        print("   size                %.3f x %.3f x %.3f" % tuple(s["size"]))
        print("   surface area        %.3f" % s["area"])
        if s["closed"]:
            why = "yes"
        else:
            why = "no, %d edges have nothing on the other side" % s["open_edges"]
        print("%s closed surface      %s" % (mark(s["closed"]), why))
        if s["non_manifold_edges"]:
            print("   touching edges      %d   (parts meet along an edge;"
                  " normal for voxel models)" % s["non_manifold_edges"])
        if s["duplicate_faces"]:
            print("!! repeated faces      %d   -- try add.clean()"
                  % s["duplicate_faces"])
        if s["back_to_back_faces"]:
            print("   back-to-back faces  %d   (fine for a two-sided sheet;"
                  " add.clean() removes them)" % s["back_to_back_faces"])
        if s["closed"]:
            print("   volume              %.3f" % s["volume"])
        if s["transparent_faces"]:
            print("   see-through faces   %d   (opacity is kept in .obj + .mtl)"
                  % s["transparent_faces"])
        if s["textures"]:
            print("   textures            %s   (put the images next to the .obj)"
                  % ", ".join(s["textures"]))
        if s["colors"] > max_colors:
            print("   hint: add.limit_colors(M, %d) or add.save(..., colors=%d)"
                  % (max_colors, max_colors))
        if mb > max_mb:
            print("   hint: fewer cells (a smaller k, grid or subdivisions)"
                  " make the file smaller")
        print("-" * 56)
    return ok


# ============================================================================
# 22. Vertices, edges and neighbours
# ============================================================================
# The functions above treat a mesh as a whole.  These look inside it: which
# vertices are joined by an edge, how many neighbours a vertex has, how far
# they are, which faces meet at a corner.  That is what you need to build a
# model out of the *vertices* of an icosahedron or a dodecahedron, to move a
# single corner of a box before rounding it with ``smooth``, or to turn a
# polyhedron into its dual or its truncation (a football).

def _directed_edges(M):
    """``{(a, b): face index}`` for every directed edge of an oriented mesh.

    A directed edge that appears in more than one face is marked with -1
    (the mesh is not a manifold there, or two faces disagree on winding).
    """
    out = {}
    for fi, f in enumerate(M.F):
        n = len(f)
        for t in range(n):
            key = (f[t], f[(t + 1) % n])
            out[key] = -1 if key in out else fi
    return out


def _rings(M):
    """For every vertex the faces around it in order: ``[(face, next), ...]``.

    ``next`` is the vertex the face's edge leaves ``v`` towards.  Walking
    from face to face across that edge goes *clockwise* seen from outside,
    so callers reverse the list when they need a counter-clockwise ring.
    The second value of each entry tells whether the ring closes (``True``)
    or the vertex lies on a border / is not a manifold (``False``).
    """
    E = _directed_edges(M)
    corners = [[] for _ in M.V]                    # vertex -> [(face, prev, next)]
    for fi, f in enumerate(M.F):
        n = len(f)
        for t in range(n):
            corners[f[t]].append((fi, f[t - 1], f[(t + 1) % n]))
    out = []
    for v, cs in enumerate(corners):
        if not cs:
            out.append(([], False))
            continue
        by_face = {}
        ok = True
        for fi, prev, nxt in cs:
            if fi in by_face:                          # v twice in one face
                ok = False
            by_face[fi] = (prev, nxt)
        if not ok:
            out.append(([(fi, nxt) for fi, prev, nxt in cs], False))
            continue
        # Start at a border face if there is one: the face whose edge
        # prev -> v has no partner face on the other side.
        start = cs[0][0]
        for fi, prev, nxt in cs:
            if E.get((v, prev), -1) == -1:
                start = fi
                break
        ring = []
        seen = set()
        fi = start
        closed = False
        while fi not in seen:
            seen.add(fi)
            prev, nxt = by_face[fi]
            ring.append((fi, nxt))
            g = E.get((nxt, v), -1)
            if g == -1 or g not in by_face:
                break
            fi = g
        else:
            closed = (fi == start)
        if len(seen) != len(cs):                      # not all faces reached
            closed = False
            missing = [(f2, n2) for f2, p2, n2 in cs if f2 not in seen]
            ring += missing
        out.append((ring, closed))
    return out


def vertex(M, i):
    """The coordinates of vertex ``i`` as a fresh ``[x, y, z]`` list."""
    return list(as_mesh(M).V[i])


def set_vertex(M, i, point):
    """A copy of the mesh with vertex ``i`` moved to ``point``.

    Any coordinate given as ``None`` keeps its old value, so raising one
    corner of a box is ``add.set_vertex(box, 3, [None, 2.5, None])``.  The
    faces are untouched, which is exactly what you want before rounding the
    result with :func:`smooth`::

        add.box([0, 0, 0], 2)
        block = add.layer()
        block = add.set_vertex(block, 7, [2, 2, 2])     # pull one corner out
        add.mesh(add.smooth(block, 6))
    """
    return set_vertices(M, {i: point})


def set_vertices(M, changes):
    """Like :func:`set_vertex` for several vertices at once:
    ``changes`` is ``{index: point, ...}`` (``None`` coordinates are kept)."""
    out = as_mesh(M).copy()
    for i, point in changes.items():
        p = out.V[i]
        for a in range(3):
            if point[a] is not None:
                p[a] = float(point[a])
    return out


def move_vertex(M, i, delta):
    """A copy of the mesh with vertex ``i`` shifted by the vector ``delta``."""
    p = as_mesh(M).V[i]
    return set_vertices(M, {i: [p[0] + delta[0], p[1] + delta[1],
                                p[2] + delta[2]]})


def nearest_vertex(M, point):
    """The index of the vertex closest to ``point`` -- so that you can pick a
    corner by *where* it is instead of by its number::

        i = add.nearest_vertex(block, [1, 1, 1])
        block = add.set_vertex(block, i, [1.5, 1.5, 1.5])
    """
    M = as_mesh(M)
    best, best_d = -1, None
    for i, p in enumerate(M.V):
        d = ((p[0] - point[0]) ** 2 + (p[1] - point[1]) ** 2
             + (p[2] - point[2]) ** 2)
        if best_d is None or d < best_d:
            best, best_d = i, d
    return best


def edges(M=None):
    """Every edge of the mesh once, as ``(a, b)`` index pairs with ``a < b``."""
    M = as_mesh(M)
    seen = set()
    for f in M.F:
        n = len(f)
        for t in range(n):
            a, b = f[t], f[(t + 1) % n]
            if a != b:
                seen.add((a, b) if a < b else (b, a))
    return sorted(seen)


def edge_length(M, a, b):
    """The distance between vertices ``a`` and ``b``."""
    M = as_mesh(M)
    return _norm(_sub(M.V[a], M.V[b]))


def edge_lengths(M=None):
    """The length of every edge, in the order :func:`edges` lists them."""
    M = as_mesh(M)
    return [_norm(_sub(M.V[a], M.V[b])) for a, b in edges(M)]


def mean_edge_length(M=None):
    """The average edge length -- the natural "unit" of a mesh.  A regular
    polyhedron has all edges equal, so this is *the* edge length there."""
    L = edge_lengths(M)
    return sum(L) / len(L) if L else 0.0


def adjacency(M=None):
    """``neighbours[i]`` = sorted list of the vertices joined to vertex ``i``
    by an edge, for every vertex at once (faster than calling
    :func:`neighbors` in a loop)."""
    M = as_mesh(M)
    nb = [set() for _ in M.V]
    for a, b in edges(M):
        nb[a].add(b)
        nb[b].add(a)
    return [sorted(s) for s in nb]


def neighbors(M, i):
    """The vertices joined to vertex ``i`` by an edge.

    On a closed, well-formed surface they come in order *around* the vertex
    (counter-clockwise seen from outside); otherwise sorted by index::

        ico = add.make(add.icosahedron, [0, 0, 0], 1)
        add.neighbors(ico, 0)          # five of them -> [5, 1, 7, 10, 11]
    """
    M = as_mesh(M)
    ring, closed = _rings(M)[i]
    if closed:
        return [nxt for fi, nxt in reversed(ring)]
    return adjacency(M)[i]


#: British spelling of :func:`neighbors`.
neighbours = neighbors


def valence(M, i):
    """How many edges (and neighbours) vertex ``i`` has: 3 on a cube or a
    dodecahedron, 4 on an octahedron, 5 on an icosahedron."""
    return len(adjacency(M)[i])


def mean_neighbor_distance(M, i):
    """The average distance from vertex ``i`` to its neighbours."""
    M = as_mesh(M)
    nb = adjacency(M)[i]
    if not nb:
        return 0.0
    return sum(_norm(_sub(M.V[i], M.V[j])) for j in nb) / len(nb)


def vertex_faces(M, i):
    """The indices of the faces that meet at vertex ``i`` (in order around
    the vertex when the surface is closed and well formed there)."""
    M = as_mesh(M)
    ring, closed = _rings(M)[i]
    if closed:
        return [fi for fi, nxt in reversed(ring)]
    return sorted(set(fi for fi, nxt in ring))


def vertex_normal(M, i):
    """The unit normal at vertex ``i``: the average of its faces' normals."""
    M = as_mesh(M)
    acc = [0.0, 0.0, 0.0]
    for fi in vertex_faces(M, i):
        nrm = _face_normal(M, M.F[fi])
        acc[0] += nrm[0]
        acc[1] += nrm[1]
        acc[2] += nrm[2]
    return _unit(acc) if _norm(acc) > EPS else (0.0, 1.0, 0.0)


def face_center(M, i):
    """The centre (average corner) of face ``i``."""
    M = as_mesh(M)
    f = M.F[i]
    n = float(len(f))
    return [sum(M.V[k][a] for k in f) / n for a in range(3)]


def face_normal(M, i):
    """The unit normal of face ``i`` (points outward on a closed model)."""
    M = as_mesh(M)
    return _unit(_face_normal(M, M.F[i]))


def face_area(M, i):
    """The area of face ``i``."""
    M = as_mesh(M)
    return _norm(_face_normal(M, M.F[i])) / 2.0


def face_centers(M=None):
    """The centre of every face, as a list of points."""
    M = as_mesh(M)
    return [face_center(M, i) for i in range(len(M.F))]


def boundary_edges(M=None):
    """The edges that belong to only one face, as directed ``(a, b)`` pairs.
    An empty list means the surface is closed."""
    return sorted(_boundary_edges(as_mesh(M)).keys())


def boundary_loops(M=None):
    """The open borders of a mesh as closed rings of vertex indices --
    one list per hole (or per sheet edge)."""
    M = as_mesh(M)
    nxt = {}
    for a, b in _boundary_edges(M):
        nxt.setdefault(a, []).append(b)
    loops = []
    while nxt:
        start = min(nxt)
        loop = [start]
        v = nxt[start].pop()
        if not nxt[start]:
            del nxt[start]
        while v != start and v in nxt:
            loop.append(v)
            w = nxt[v].pop()
            if not nxt[v]:
                del nxt[v]
            v = w
        loops.append(loop)
    return loops


def inflate(M, amount):
    """Push every vertex out along its normal by ``amount`` (in for a
    negative value).  Turns the panels of a ball into cushions, or thickens
    a thin shape a little."""
    M = as_mesh(M)
    N = _vertex_normals(M)
    out = M.copy()
    out.V = [[p[0] + n[0] * amount, p[1] + n[1] * amount,
              p[2] + n[2] * amount] for p, n in zip(M.V, N)]
    return out


def spherify(M, center=None, r=None, amount=1.0):
    """Project every vertex onto a sphere.

    By default the sphere is centred on the average vertex and passes
    through the farthest one (so the corners of a polyhedron stay where
    they are); ``amount`` less than 1 only goes part of the way (0.5 rounds
    a cube into a cushion).  With :func:`refine` this is how a geodesic
    dome comes out of any polyhedron::

        octa = add.make(add.octahedron, [0, 0, 0], 1)
        dome = add.spherify(add.refine(octa, 3))        # 512 triangles
    """
    M = as_mesh(M)
    c = _centroid(M) if center is None else center
    if r is None:
        r = max([_norm(_sub(p, c)) for p in M.V] or [1.0])
    V = []
    for p in M.V:
        u = _unit(_sub(p, c))
        target = (c[0] + u[0] * r, c[1] + u[1] * r, c[2] + u[2] * r)
        V.append([p[a] + (target[a] - p[a]) * amount for a in range(3)])
    out = M.copy()
    out.V = V
    return out


def refine(M, steps=1):
    """Split every face into four (triangles) or into one quad per corner
    (other polygons), ``steps`` times, without moving anything.

    New vertices sit at edge midpoints (and face centres), shared between
    neighbouring faces, so the mesh stays watertight.  Colours are kept.
    This is the flat "observatory dome" split; :func:`spherify` afterwards
    pushes the new points out to a ball, :func:`catmull_clark` is the
    version that rounds the shape as it splits.
    """
    M = as_mesh(M)
    for _ in range(int(steps)):
        out = Mesh([list(p) for p in M.V], [], [])
        mid = {}

        def midpoint_index(a, b):
            key = (a, b) if a < b else (b, a)
            if key not in mid:
                pa, pb = M.V[a], M.V[b]
                mid[key] = out.add_vertex(((pa[0] + pb[0]) / 2.0,
                                           (pa[1] + pb[1]) / 2.0,
                                           (pa[2] + pb[2]) / 2.0))
            return mid[key]

        for f, c in zip(M.F, M.C):
            n = len(f)
            if n == 3:
                a, b, d = f
                ab, bd, da = midpoint_index(a, b), midpoint_index(b, d), \
                    midpoint_index(d, a)
                out.add_face([a, ab, da], c)
                out.add_face([b, bd, ab], c)
                out.add_face([d, da, bd], c)
                out.add_face([ab, bd, da], c)
            elif n >= 4:
                centre = out.add_vertex([sum(M.V[k][a] for k in f) / float(n)
                                         for a in range(3)])
                m = [midpoint_index(f[t], f[(t + 1) % n]) for t in range(n)]
                for t in range(n):
                    out.add_face([f[t], m[t], centre, m[t - 1]], c)
            else:
                out.add_face(f, c)
        M = out
    return M


def dual(M, color=None):
    """The dual polyhedron: a vertex at the centre of every face, and a face
    for every vertex, joining the centres of the faces around it.

    Cube <-> octahedron, dodecahedron <-> icosahedron, and the tetrahedron
    is its own dual.  Only vertices with a closed ring of faces get a face,
    so the model should be closed.  ``color`` paints the result; without it
    each new face takes the colour of one of the old faces around it.
    """
    M = as_mesh(M)
    out = Mesh()
    for i in range(len(M.F)):
        out.add_vertex(face_center(M, i))
    for v, (ring, closed) in enumerate(_rings(M)):
        if not closed or len(ring) < 3:
            continue
        faces = [fi for fi, nxt in reversed(ring)]
        out.add_face(faces, M.C[faces[0]] if color is None else color)
    _drop_unused(out)
    return out


def truncate(M, t=1.0 / 3.0, color=None):
    """Cut every corner off: each vertex is replaced by a small face and
    each old face loses its corners.

    ``t`` is how far along every edge the cut goes (``1/3`` turns an
    icosahedron into the football's truncated icosahedron, ``1/2`` cuts
    right to the edge midpoints).  The corner faces are painted ``color``;
    the old faces keep their colour.  Works on any closed mesh::

        ico = add.make(add.icosahedron, [0, 0, 0], 3, "white")
        ball = add.truncate(ico, 1 / 3.0, "black")     # 20 hexagons, 12 pentagons
    """
    M = as_mesh(M)
    t = float(t)
    if t > 0.5:
        t = 0.5
    out = Mesh()
    cut = {}

    def point(a, b):
        """Vertex on edge a -> b at fraction t from a."""
        key = (a, b) if t < 0.5 - 1e-12 else ((a, b) if a < b else (b, a))
        if key not in cut:
            pa, pb = M.V[a], M.V[b]
            cut[key] = out.add_vertex((pa[0] + (pb[0] - pa[0]) * t,
                                       pa[1] + (pb[1] - pa[1]) * t,
                                       pa[2] + (pb[2] - pa[2]) * t))
        return cut[key]

    for f, c in zip(M.F, M.C):
        n = len(f)
        poly = []
        for i in range(n):
            v, prev, nxt = f[i], f[i - 1], f[(i + 1) % n]
            for idx in (point(v, prev), point(v, nxt)):
                if not poly or poly[-1] != idx:
                    poly.append(idx)
        if len(poly) > 1 and poly[0] == poly[-1]:
            poly.pop()
        if len(poly) >= 3:
            out.add_face(poly, c)
    corner = rgb(color)
    for v, (ring, closed) in enumerate(_rings(M)):
        if len(ring) < 3:
            continue
        poly = [point(v, nxt) for fi, nxt in reversed(ring)]
        if len(set(poly)) >= 3:
            out.add_face(poly, corner)
    return out


def color_by_sides(M, colors, default=None):
    """Paint every face by its number of corners.

    ``colors`` is a dictionary such as ``{5: "black", 6: "white"}`` (the
    football), faces with a count not in it get ``default`` or keep their
    colour.
    """
    M = as_mesh(M)
    out = M.copy()
    for i, f in enumerate(M.F):
        n = len(f)
        if n in colors:
            out.C[i] = rgb(colors[n])
        elif default is not None:
            out.C[i] = rgb(default)
    return out


# ============================================================================
# 23. Boolean operations: union, intersection, difference
# ============================================================================
# Two solids can be added together, cut out of one another, or intersected.
# The idea used here needs no library and fits on one screen:
#
#   1. Wherever the other model's triangles could cut one of ours, slice ours
#      along their planes.  After that every piece lies wholly inside or
#      wholly outside the other solid -- no piece straddles the boundary.
#   2. Ask of each piece: is it inside?  Shoot a ray from just above the
#      piece's middle and count how many times it crosses the other surface.
#      An odd count means inside.
#   3. Keep the pieces the operation asks for, and turn the borrowed ones
#      round when the operation says so:
#
#        union         keep A outside B  +  B outside A
#        intersection  keep A inside  B  +  B inside  A
#        difference    keep A outside B  +  B inside  A, reversed
#
# Two grids keep both steps local, so the work grows roughly with the number
# of faces rather than with its square.  Booleans want *closed* solids --
# ``add.check()`` will tell you whether yours is closed.

#: How far a point may be from a plane and still count as lying in it.
BOOL_EPS = 1e-9

_COPLANAR, _FRONT, _BACK, _SPANNING = 0, 1, 2, 3


class _Poly(object):
    """One planar polygon that remembers its plane and its colour."""

    __slots__ = ("pts", "n", "w", "c")

    def __init__(self, pts, c, n=None, w=None):
        self.pts = pts
        self.c = c
        if n is None:
            nx = ny = nz = 0.0
            m = len(pts)
            for i in range(m):
                a, b = pts[i], pts[(i + 1) % m]
                nx += (a[1] - b[1]) * (a[2] + b[2])
                ny += (a[2] - b[2]) * (a[0] + b[0])
                nz += (a[0] - b[0]) * (a[1] + b[1])
            n = _unit((nx, ny, nz))
            w = _dot(n, pts[0])
        self.n = n
        self.w = w


def _split(pn, pw, poly, front, back, eps=BOOL_EPS):
    """Cut ``poly`` with plane ``(pn, pw)``; a polygon lying in the plane or
    entirely on one side is filed whole."""
    types = []
    poly_type = 0
    for p in poly.pts:
        t = pn[0] * p[0] + pn[1] * p[1] + pn[2] * p[2] - pw
        kind = _BACK if t < -eps else (_FRONT if t > eps else _COPLANAR)
        poly_type |= kind
        types.append(kind)

    if poly_type != _SPANNING:
        (back if poly_type == _BACK else front).append(poly)
        return
    f, b = [], []
    m = len(poly.pts)
    for i in range(m):
        j = (i + 1) % m
        ti, tj = types[i], types[j]
        vi, vj = poly.pts[i], poly.pts[j]
        if ti != _BACK:
            f.append(vi)
        if ti != _FRONT:
            b.append(vi)
        if (ti | tj) == _SPANNING:
            di = pn[0] * vi[0] + pn[1] * vi[1] + pn[2] * vi[2] - pw
            dj = pn[0] * vj[0] + pn[1] * vj[1] + pn[2] * vj[2] - pw
            t = di / (di - dj)
            cut = (vi[0] + (vj[0] - vi[0]) * t,
                   vi[1] + (vj[1] - vi[1]) * t,
                   vi[2] + (vj[2] - vi[2]) * t)
            f.append(cut)
            b.append(cut)
    if len(f) >= 3:
        front.append(_Poly(f, poly.c, poly.n, poly.w))
    if len(b) >= 3:
        back.append(_Poly(b, poly.c, poly.n, poly.w))


# ---------------------------------------------------------------------------
#  Two little indexes that keep the search local
# ---------------------------------------------------------------------------

class _BoxGrid(object):
    """Which triangles live near a given box -- a uniform 3D hash.

    Triangles are filed in every cell their bounding box touches; a triangle
    so long that it would fill hundreds of cells goes on a short "oversize"
    list that every query checks.  Candidates are then filtered by a real
    box overlap test, so a query returns only triangles that could matter.
    """

    __slots__ = ("cell", "buckets", "oversize", "boxes")

    MAX_CELLS = 64

    def __init__(self, polys, diagonal):
        self.cell = max(diagonal / 32.0, 1e-9)
        self.buckets = {}
        self.oversize = []
        self.boxes = []
        for i, p in enumerate(polys):
            lo = [min(q[a] for q in p.pts) for a in range(3)]
            hi = [max(q[a] for q in p.pts) for a in range(3)]
            self.boxes.append((lo, hi))
            keys = self._keys(lo, hi, self.MAX_CELLS)
            if keys is None:
                self.oversize.append(i)
            else:
                for key in keys:
                    self.buckets.setdefault(key, []).append(i)

    def _keys(self, lo, hi, limit=None):
        c = self.cell
        r = []
        total = 1
        for a in range(3):
            first = int(math.floor(lo[a] / c))
            last = int(math.floor(hi[a] / c))
            r.append((first, last))
            total *= last - first + 1
            if limit is not None and total > limit:
                return None
        out = []
        for i in range(r[0][0], r[0][1] + 1):
            for j in range(r[1][0], r[1][1] + 1):
                for k in range(r[2][0], r[2][1] + 1):
                    out.append((i, j, k))
        return out

    def near(self, lo, hi):
        """Indices of triangles whose bounding box overlaps ``lo..hi``."""
        keys = self._keys(lo, hi, 4096)
        if keys is None:
            candidates = range(len(self.boxes))
        else:
            seen = set(self.oversize)
            for key in keys:
                seen.update(self.buckets.get(key, ()))
            candidates = seen
        out = []
        for i in candidates:
            blo, bhi = self.boxes[i]
            if (bhi[0] < lo[0] - 1e-9 or blo[0] > hi[0] + 1e-9
                    or bhi[1] < lo[1] - 1e-9 or blo[1] > hi[1] + 1e-9
                    or bhi[2] < lo[2] - 1e-9 or blo[2] > hi[2] + 1e-9):
                continue
            out.append(i)
        return out


class _RayIndex(object):
    """Answers "is this point inside the solid?" by counting ray crossings.

    All rays travel in the same direction, so the triangles can be bucketed
    once on the two axes across that direction; a query then only looks at the
    handful of triangles standing in the ray's way.
    """

    __slots__ = ("d", "e1", "e2", "cell", "buckets", "tris")

    def __init__(self, polys, direction):
        self.d = _unit(direction)
        self.e1 = _perp(self.d)
        self.e2 = _cross(self.d, self.e1)
        self.tris = []
        for p in polys:
            for t in range(1, len(p.pts) - 1):
                self.tris.append((p.pts[0], p.pts[t], p.pts[t + 1]))
        span = 0.0
        flat = []
        for tri in self.tris:
            uv = [(_dot(q, self.e1), _dot(q, self.e2)) for q in tri]
            lo = (min(q[0] for q in uv), min(q[1] for q in uv))
            hi = (max(q[0] for q in uv), max(q[1] for q in uv))
            flat.append((lo, hi))
            span = max(span, hi[0] - lo[0], hi[1] - lo[1])
        self.cell = max(span, 1e-9)
        self.buckets = {}
        for i, (lo, hi) in enumerate(flat):
            for a in range(int(math.floor(lo[0] / self.cell)),
                           int(math.floor(hi[0] / self.cell)) + 1):
                for b in range(int(math.floor(lo[1] / self.cell)),
                               int(math.floor(hi[1] / self.cell)) + 1):
                    self.buckets.setdefault((a, b), []).append(i)

    def inside(self, p):
        """``True`` / ``False``, or ``None`` when the ray grazes an edge."""
        key = (int(math.floor(_dot(p, self.e1) / self.cell)),
               int(math.floor(_dot(p, self.e2) / self.cell)))
        hits = 0
        for i in self.buckets.get(key, ()):
            a, b, c = self.tris[i]
            e1v, e2v = _sub(b, a), _sub(c, a)
            h = _cross(self.d, e2v)
            det = _dot(e1v, h)
            if abs(det) < 1e-14:
                continue
            inv = 1.0 / det
            s = _sub(p, a)
            u = _dot(s, h) * inv
            if u < -1e-9 or u > 1.0 + 1e-9:
                continue
            q = _cross(s, e1v)
            v = _dot(self.d, q) * inv
            if v < -1e-9 or u + v > 1.0 + 1e-9:
                continue
            t = _dot(e2v, q) * inv
            if t < 1e-12:
                continue
            # Too close to an edge, a corner or the start of the ray to trust.
            if (abs(u) < 1e-9 or abs(v) < 1e-9 or abs(u + v - 1.0) < 1e-9
                    or t < 1e-9):
                return None
            hits += 1
        return hits % 2 == 1


#: Three awkward directions; if one ray grazes an edge the next one is tried.
_RAY_DIRECTIONS = ((0.5773502691896258, 0.5773502691896257, 0.5773502691896256),
                   (0.2672612419124244, -0.5345224838248488, 0.8017837257372732),
                   (-0.7071067811865475, 0.408248290463863, 0.5773502691896258))


class _Solid(object):
    """A mesh prepared for boolean work: triangles, a box grid and ray indexes."""

    __slots__ = ("polys", "grid", "rays", "lo", "hi", "scale")

    def __init__(self, M):
        self.polys = _to_polys(M)
        lo = [min(p[a] for q in self.polys for p in q.pts) for a in range(3)] \
            if self.polys else [0.0, 0.0, 0.0]
        hi = [max(p[a] for q in self.polys for p in q.pts) for a in range(3)] \
            if self.polys else [0.0, 0.0, 0.0]
        self.lo, self.hi = lo, hi
        self.scale = max(1e-9, max(hi[a] - lo[a] for a in range(3)))
        diagonal = math.sqrt(sum((hi[a] - lo[a]) ** 2 for a in range(3)))
        self.grid = _BoxGrid(self.polys, max(diagonal, 1e-9)) if self.polys else None
        self.rays = []

    def ray_index(self, which):
        while len(self.rays) <= which:
            self.rays.append(_RayIndex(self.polys,
                                       _RAY_DIRECTIONS[len(self.rays)]))
        return self.rays[which]

    def contains(self, p):
        """Is point ``p`` inside this solid?"""
        for which in range(len(_RAY_DIRECTIONS)):
            answer = self.ray_index(which).inside(p)
            if answer is not None:
                return answer
        return False

    def cutters(self, poly):
        """Planes to cut ``poly`` with, and the triangles it may lie on.

        Normally a nearby triangle contributes its own plane.  A triangle
        lying in the *same* plane as ``poly`` would not cut it at all, yet the
        two faces may still overlap -- think of two boxes whose tops are
        flush.  For those, the three planes standing on the triangle's edges
        are used instead, which carves the shared patch out cleanly.
        """
        lo = [min(q[a] for q in poly.pts) for a in range(3)]
        hi = [max(q[a] for q in poly.pts) for a in range(3)]
        planes = []
        flush = []
        for i in self.grid.near(lo, hi):
            t = self.polys[i]
            if abs(abs(_dot(t.n, poly.n)) - 1.0) < 1e-9 \
                    and abs(_dot(t.n, poly.pts[0]) - t.w) < 1e-9:
                flush.append(i)
                for k in range(3):               # the triangle's edge planes
                    p, q = t.pts[k], t.pts[(k + 1) % 3]
                    side = _cross(t.n, _sub(q, p))
                    if _norm(side) > 1e-12:
                        side = _unit(side)
                        planes.append(((i, k + 1), side, _dot(side, p)))
            else:
                planes.append(((i, 0), t.n, t.w))
        return planes, flush

    def facing_at(self, point, plane_normal, flush):
        """Does ``point`` sit on one of the ``flush`` triangles?

        Returns ``+1`` when the triangle faces the same way as
        ``plane_normal``, ``-1`` when it faces the other way, ``None`` when
        the point is not on any of them.
        """
        for i in flush:
            t = self.polys[i]
            on = True
            for k in range(3):
                p, q = t.pts[k], t.pts[(k + 1) % 3]
                side = _cross(t.n, _sub(q, p))
                if _dot(side, _sub(point, p)) < -1e-12 * max(1.0, _norm(side)):
                    on = False
                    break
            if on:
                return 1 if _dot(t.n, plane_normal) > 0 else -1
        return None


def _split_against(poly, other):
    """Chop ``poly`` until no piece can straddle ``other``'s surface.

    Pieces are cut one at a time and the search is redone for each new piece,
    so a face far from the action stops being cut as soon as it moves out of
    the way -- which is what keeps a drilled plate from shattering into
    thousands of slivers.
    """
    done_pieces = []
    work = [(poly, frozenset())]
    guard = 0
    while work:
        piece, done = work.pop()
        guard += 1
        if guard > 20000:                        # pathological input; stop
            done_pieces.append(piece)
            continue
        planes, flush = other.cutters(piece)
        chosen = None
        for pid, pn, pw in planes:
            if pid in done:
                continue
            front = back = False
            for p in piece.pts:
                t = pn[0] * p[0] + pn[1] * p[1] + pn[2] * p[2] - pw
                if t > BOOL_EPS:
                    front = True
                elif t < -BOOL_EPS:
                    back = True
            if front and back:
                chosen = (pid, pn, pw)
                break
            done = done | {pid}                  # this plane can never cut it
        if chosen is None:
            done_pieces.append((piece, flush))
            continue
        pid, pn, pw = chosen
        f, b = [], []
        _split(pn, pw, piece, f, b)
        rest = done | {pid}
        for part in f + b:
            work.append((part, rest))
    return done_pieces


def _keep_pieces(source, other, keep, flip, paint=None):
    """Cut ``source``'s faces against ``other`` and keep the wanted pieces.

    ``keep`` is a set drawn from ``"in"``, ``"out"``, ``"same"`` and
    ``"opp"``: whether a piece ends up inside the other solid, outside it, or
    lying on its surface facing the same or the opposite way.
    """
    out = []
    if other.grid is None:
        return out
    for poly in source.polys:
        # Wholly outside the other model's box: no cutting, no doubt.
        if any(max(q[a] for q in poly.pts) < other.lo[a] - 1e-9
               or min(q[a] for q in poly.pts) > other.hi[a] + 1e-9
               for a in range(3)):
            if "out" in keep:
                out.append(poly)
            continue
        for piece, flush in _split_against(poly, other):
            n = len(piece.pts)
            centre = (sum(q[0] for q in piece.pts) / n,
                      sum(q[1] for q in piece.pts) / n,
                      sum(q[2] for q in piece.pts) / n)
            facing = other.facing_at(centre, piece.n, flush) if flush else None
            if facing is not None:
                state = "same" if facing > 0 else "opp"
            else:
                state = "in" if other.contains(centre) else "out"
            if state not in keep:
                continue
            c = piece.c if paint is None else paint
            if flip:
                out.append(_Poly(piece.pts[::-1], c,
                                 (-piece.n[0], -piece.n[1], -piece.n[2]),
                                 -piece.w))
            else:
                out.append(_Poly(piece.pts, c, piece.n, piece.w))
    return out


def _to_polys(M):
    """Mesh -> list of triangles (so no face can be twisted or non-planar)."""
    M = as_mesh(M)
    polys = []
    for f, c in zip(M.F, M.C):
        if len(f) < 3:
            continue
        pts = [tuple(M.V[i]) for i in f]
        for t in range(1, len(pts) - 1):
            p = _Poly([pts[0], pts[t], pts[t + 1]], c)
            if _norm(p.n) > 0.5:                 # skip degenerate slivers
                polys.append(p)
    return polys


def _from_polys(polys, tidy=True):
    """List of polygons -> Mesh, welded and with its T-junctions closed."""
    M = Mesh()
    for p in polys:
        M.add_polygon(p.pts, p.c)
    if tidy:
        _weld(M, 1e-7)
        _drop_degenerate(M)
        _dedup_faces(M)
        M = heal(M, 1e-7)
        _drop_degenerate(M)
        _drop_unused(M)
    return M


def _boxes_apart(A, B, slack=1e-9):
    """True when two meshes cannot possibly touch."""
    la, ha = bbox(A)
    lb, hb = bbox(B)
    for a in range(3):
        if ha[a] < lb[a] - slack or hb[a] < la[a] - slack:
            return True
    return False


#: Which pieces each operation keeps.  ``A`` gets the shared surface so that
#: a patch where the two solids are flush is kept exactly once.
_RULES = {
    "union":        ({"out", "same"}, {"out"}, False),
    "intersection": ({"in", "same"}, {"in"}, False),
    "difference":   ({"out", "opp"}, {"in"}, True),
}


def _csg(A, B, op, paint=None):
    """The three boolean operations, all from the same two half-steps."""
    if op not in _RULES:
        raise ValueError("unknown boolean operation: %r" % op)
    keep_a, keep_b, flip_b = _RULES[op]
    a, b = _Solid(A), _Solid(B)
    polys = (_keep_pieces(a, b, keep_a, False)
             + _keep_pieces(b, a, keep_b, flip_b, paint))
    return _from_polys(polys)


def union(*meshes):
    """Fuse solids into one, removing everything hidden inside.

    Unlike :func:`merge`, which only stacks meshes into the same file,
    ``union`` really welds them: the buried walls disappear and the result is
    a single watertight solid::

        add.box([0, 0, 0], 2, "red")
        a = add.layer()
        add.sphere([1, 1, 1], 1.3, 16, "blue")
        b = add.layer()
        add.mesh(add.union(a, b))
    """
    meshes = _flatten(meshes)
    if not meshes:
        return Mesh()
    out = as_mesh(meshes[0])
    for other in meshes[1:]:
        other = as_mesh(other)
        if not other.F:
            continue
        if not out.F:
            out = other
        elif _boxes_apart(out, other):
            out = merge([out, other])            # nothing to cut: just stack
        else:
            out = _csg(out, other, "union")
    return out


def difference(A, *others, **options):
    """Cut the other solids out of ``A``.

    ``difference`` is how you drill, engrave and slot::

        add.cuboid([0, 0, 0], [4, 1, 4], "brown")
        plate = add.layer()
        add.cylinder([0, -1, 0], [0, 1, 0], 0.6, 32, "brown")
        drill = add.layer()
        add.mesh(add.difference(plate, drill))

    The freshly exposed surface keeps the colour of the tool that cut it,
    which makes a hole easy to see.  Pass ``color=`` to paint it instead::

        add.difference(plate, drill, color="black")
    """
    paint = rgb(options["color"]) if options.get("color") is not None else None
    for key in options:
        if key != "color":
            raise TypeError("unexpected argument %r" % key)
    out = as_mesh(A)
    for other in _flatten(others):
        other = as_mesh(other)
        if not other.F or not out.F or _boxes_apart(out, other):
            continue
        out = _csg(out, other, "difference", paint)
    return out


def intersect(*meshes):
    """Keep only the space that all the solids have in common."""
    meshes = _flatten(meshes)
    if not meshes:
        return Mesh()
    out = as_mesh(meshes[0])
    for other in meshes[1:]:
        other = as_mesh(other)
        if not out.F or not other.F or _boxes_apart(out, other):
            return Mesh()
        out = _csg(out, other, "intersection")
    return out


def symmetric_difference(A, B):
    """Everything that is in one solid or the other but not in both."""
    return union(difference(A, B), difference(B, A))


def _flatten(items):
    """Allow ``union(a, b, c)`` and ``union([a, b, c])`` to mean the same."""
    out = []
    for x in items:
        if isinstance(x, Mesh):
            out.append(x)
        elif isinstance(x, (list, tuple)) and len(x) == 2 \
                and all(isinstance(y, (list, tuple, _StringView)) for y in x):
            out.append(as_mesh(x))               # old [vertices, faces] pair
        elif isinstance(x, (list, tuple)):
            out.extend(_flatten(x))
        else:
            out.append(as_mesh(x))
    return out


def add_solids(*meshes):
    """Alias of :func:`union`."""
    return union(*meshes)


def subtract(A, *others):
    """Alias of :func:`difference`."""
    return difference(A, *others)


def common(*meshes):
    """Alias of :func:`intersect`."""
    return intersect(*meshes)


# ---------------------------------------------------------------------------
#  Cheap relatives of the boolean operations
# ---------------------------------------------------------------------------

def cut(M, point=(0, 0, 0), normal=(0, 1, 0), cap=True, color=None):
    """Slice a solid with an infinite plane and keep the part *behind* it.

    "Behind" means the side the normal points away from, so
    ``cut(M, [0, 0, 0], [0, 1, 0])`` keeps the bottom half and throws the top
    away.  Cut twice with opposite normals to keep a slab.

    Far cheaper than a full boolean, because a plane needs no searching.  With
    ``cap=True`` the exposed cross-section is closed with a new flat face, so
    the result stays watertight -- perfect for cut-away drawings::

        half = add.cut(model, [0, 0, 0], [0, 0, 1])
    """
    M = as_mesh(M)
    n = _unit(normal)
    w = _dot(n, point)
    out = Mesh()
    rim = []
    for f, c in zip(M.F, M.C):
        poly = _Poly([tuple(M.V[i]) for i in f], c)
        front, back = [], []
        _split(n, w, poly, front, back, 1e-12)
        for p in back:
            out.add_polygon(p.pts, p.c)
            m = len(p.pts)
            for i in range(m):
                a, b = p.pts[i], p.pts[(i + 1) % m]
                if abs(_dot(n, a) - w) < 1e-9 and abs(_dot(n, b) - w) < 1e-9:
                    rim.append((a, b))
    if cap and rim:
        for loop in _loops(rim):
            if len(loop) >= 3:
                out.add_polygon(loop, color if color is not None else
                                (M.C[0] if M.C else None))
    _weld(out, 1e-7)
    _drop_degenerate(out)
    _drop_unused(out)
    return out


def _loops(edges):
    """Chain a bag of (a, b) segments into closed rings of points."""
    def key(p):
        return (round(p[0], 7), round(p[1], 7), round(p[2], 7))

    nxt = {}
    coords = {}
    for a, b in edges:
        nxt.setdefault(key(a), []).append(key(b))
        coords[key(a)] = a
        coords[key(b)] = b
    loops = []
    used = set()
    for start in list(nxt):
        if start in used:
            continue
        loop = []
        cur = start
        while cur in nxt and cur not in used:
            used.add(cur)
            loop.append(coords[cur])
            options = [k for k in nxt[cur] if k not in used]
            if not options:
                break
            cur = options[0]
        if len(loop) >= 3:
            loops.append(loop)
    return loops


def inside(M, p):
    """Is point ``p`` inside the (closed) mesh?  Ray casting: odd = inside.

    ``p`` may also be a *list* of points, which returns a list of answers
    and is far faster than asking one point at a time, because the mesh is
    indexed only once::

        hits = add.inside(ring, add.random_points(400, lo, hi, seed=3))
    """
    solid = _Solid(M)
    if len(p) and isinstance(p[0], (list, tuple)):
        return [solid.contains((q[0], q[1], q[2])) for q in p]
    return solid.contains((p[0], p[1], p[2]))


# ============================================================================
# 24. Smooth surfaces: Catmull-Clark and uniform n-grids
# ============================================================================
# A coarse polygon mesh -- a box with a corner pulled out, a dodecahedron, a
# letter -- can be treated as the *control net* of a smooth surface.
# Catmull-Clark subdivision (1978) rounds it by splitting every face into
# quads and averaging; done for ever it converges to the *limit surface*.
#
# ``catmull_clark`` is the classical step.  ``smooth`` goes further: it is
# the generalised algorithm of M. Sabaliauskas, "Uniform n-grids on
# Catmull-Clark limit surfaces of arbitrary polygon meshes" (2026).  For
# ANY n = 1, 2, 3, 4, 5 ... it puts n cells on every edge of the control
# mesh with all the new vertices *exactly* on the limit surface (classical
# subdivision only reaches n = 2, 4, 8 ...), and near the extraordinary
# vertices (valence != 4) and non-quad faces it reparameterises the surface
# so that the cells come out evenly sized.  The code below is a line-by-line
# port of the reference implementation (unisub.js / unisub.hpp) into plain
# Python, so that it too needs nothing but ``import add``.

class _Topo(object):
    """A polygon mesh with its edges and adjacency worked out.

    ``E[e] = [a, b, f0, f1]`` (f1 = -1 on a border), ``VF[v]`` faces at a
    vertex, ``VE[v]`` edges at a vertex, ``FE[f][k]`` the edge leaving
    corner ``k`` of face ``f``, ``FN[f][k]`` the face across that edge.
    """

    __slots__ = ("V", "F", "E", "VF", "VE", "FE", "FN", "boundary")

    def __init__(self, V, F):
        self.V = V
        self.F = F
        nv, nf = len(V), len(F)
        self.E = []
        self.VF = [[] for _ in range(nv)]
        self.VE = [[] for _ in range(nv)]
        self.FE = [None] * nf
        self.FN = [None] * nf
        emap = {}
        for f in range(nf):
            p = F[f]
            m = len(p)
            if m < 3:
                raise ValueError("face with fewer than 3 vertices")
            fe = [0] * m
            for k in range(m):
                a, b = p[k], p[(k + 1) % m]
                if a == b:
                    raise ValueError("degenerate edge in face %d" % f)
                key = (a, b) if a < b else (b, a)
                e = emap.get(key)
                if e is None:
                    e = len(self.E)
                    self.E.append([key[0], key[1], f, -1])
                    emap[key] = e
                    self.VE[a].append(e)
                    self.VE[b].append(e)
                else:
                    ed = self.E[e]
                    if ed[3] >= 0:
                        raise ValueError("non-manifold edge (more than two "
                                         "faces meet along it)")
                    if ed[2] == f:
                        raise ValueError("edge used twice by the same face")
                    ed[3] = f
                fe[k] = e
            self.FE[f] = fe
            for k in range(m):
                self.VF[p[k]].append(f)
        for f in range(nf):
            fe = self.FE[f]
            self.FN[f] = [self.E[e][3] if self.E[e][2] == f else self.E[e][2]
                          for e in fe]
        self.boundary = [False] * nv
        for ed in self.E:
            if ed[3] < 0:
                self.boundary[ed[0]] = True
                self.boundary[ed[1]] = True

    def all_quads(self):
        for f in self.F:
            if len(f) != 4:
                return False
        return True

    def centroid(self, f):
        p = self.F[f]
        n = float(len(p))
        return [sum(self.V[v][a] for v in p) / n for a in range(3)]

    def ordered_ring(self, v):
        """Neighbours and faces counter-clockwise around ``v``, or ``None``."""
        VF = self.VF[v]
        if not VF:
            return None
        start = VF[0]
        for f in VF:
            k = self.F[f].index(v)
            if self.FN[f][k] < 0:
                start = f
                break
        nbrs, faces = [], []
        f = start
        guard = 0
        while True:
            p = self.F[f]
            m = len(p)
            k = p.index(v)
            nxt, prv = p[(k + 1) % m], p[(k + m - 1) % m]
            if not faces:
                nbrs.append(nxt)
            faces.append(f)
            nbrs.append(prv)
            g = self.FN[f][(k + m - 1) % m]
            if g < 0:
                break
            if g == start:
                nbrs.pop()
                break
            f = g
            guard += 1
            if guard > len(VF) + 2:
                return None
        if len(faces) != len(VF):
            return None
        return nbrs, faces


def _cc_subdivide(T):
    """One Catmull-Clark step on a :class:`_Topo`.

    Returns ``(new topology, parent)`` where ``parent[i]`` is the face of
    ``T`` that new quad ``i`` came from.  New vertices are numbered: the old
    vertices first, then one per edge, then one per face.  Border edges and
    vertices follow the cubic B-spline curve rules, so an open sheet keeps
    a smooth rim, and a vertex with a single face stays where it is.
    """
    V, F, E = T.V, T.F, T.E
    nv, ne, nf = len(V), len(E), len(F)
    R = [None] * (nv + ne + nf)
    for f in range(nf):
        R[nv + ne + f] = T.centroid(f)
    for e in range(ne):
        a, b, f0, f1 = E[e]
        pa, pb = V[a], V[b]
        if f1 < 0:
            R[nv + e] = [(pa[0] + pb[0]) * 0.5, (pa[1] + pb[1]) * 0.5,
                         (pa[2] + pb[2]) * 0.5]
        else:
            c0, c1 = R[nv + ne + f0], R[nv + ne + f1]
            R[nv + e] = [(pa[0] + pb[0] + c0[0] + c1[0]) * 0.25,
                         (pa[1] + pb[1] + c0[1] + c1[1]) * 0.25,
                         (pa[2] + pb[2] + c0[2] + c1[2]) * 0.25]
    for v in range(nv):
        p = V[v]
        VF, VE = T.VF[v], T.VE[v]
        if not VF:
            R[v] = list(p)
            continue
        if T.boundary[v]:
            if len(VF) <= 1:
                R[v] = list(p)
                continue
            s = [0.0, 0.0, 0.0]
            cnt = 0
            for e in VE:
                ed = E[e]
                if ed[3] < 0:
                    q = V[ed[1] if ed[0] == v else ed[0]]
                    s[0] += q[0]
                    s[1] += q[1]
                    s[2] += q[2]
                    cnt += 1
            if cnt != 2:
                R[v] = list(p)
                continue
            R[v] = [(s[0] + 6 * p[0]) / 8.0, (s[1] + 6 * p[1]) / 8.0,
                    (s[2] + 6 * p[2]) / 8.0]
        else:
            n = len(VE)
            Q = [0.0, 0.0, 0.0]
            Rm = [0.0, 0.0, 0.0]
            for f in VF:
                c = R[nv + ne + f]
                Q[0] += c[0]
                Q[1] += c[1]
                Q[2] += c[2]
            for e in VE:
                ed = E[e]
                pa, pb = V[ed[0]], V[ed[1]]
                Rm[0] += (pa[0] + pb[0]) * 0.5
                Rm[1] += (pa[1] + pb[1]) * 0.5
                Rm[2] += (pa[2] + pb[2]) * 0.5
            nfc = float(len(VF))
            R[v] = [(Q[0] / nfc + 2 * Rm[0] / n + (n - 3) * p[0]) / n,
                    (Q[1] / nfc + 2 * Rm[1] / n + (n - 3) * p[1]) / n,
                    (Q[2] / nfc + 2 * Rm[2] / n + (n - 3) * p[2]) / n]
    newF = []
    parent = []
    for f in range(nf):
        p = F[f]
        fe = T.FE[f]
        m = len(p)
        for k in range(m):
            newF.append([p[k], nv + fe[k], nv + ne + f, nv + fe[(k + m - 1) % m]])
            parent.append(f)
    return _Topo(R, newF), parent


def _cc_lambda(N):
    """Subdominant eigenvalue of the Catmull-Clark subdivision matrix."""
    if N == 4:
        return 0.5
    c = math.cos(2 * math.pi / N)
    return (c + 5 + math.sqrt((c + 1) * (c + 9))) / 16.0


def _cc_gamma(N):
    """Exponent of the radial reparameterisation at a valence-N vertex:
    ``gamma = -1 / log2(lambda_N)`` (1 for the regular valence 4)."""
    if N == 4:
        return 1.0
    return 1.0 / (-math.log(_cc_lambda(N), 2))


def _cc_limit_positions(T):
    """Limit position of every vertex of a quad topology (exact formula).

    A mesh with other polygons is subdivided once first -- after that step
    the formula is exact for the original vertices too.
    """
    if not T.all_quads():
        S, parent = _cc_subdivide(T)
        return _cc_limit_positions(S)[:len(T.V)]
    V, E = T.V, T.E
    L = [None] * len(V)
    for v in range(len(V)):
        p = V[v]
        VF = T.VF[v]
        if not VF:
            L[v] = list(p)
            continue
        if T.boundary[v]:
            if len(VF) <= 1:
                L[v] = list(p)
                continue
            s = [0.0, 0.0, 0.0]
            cnt = 0
            for e in T.VE[v]:
                ed = E[e]
                if ed[3] < 0:
                    q = V[ed[1] if ed[0] == v else ed[0]]
                    s[0] += q[0]
                    s[1] += q[1]
                    s[2] += q[2]
                    cnt += 1
            if cnt != 2:
                L[v] = list(p)
                continue
            L[v] = [(s[0] + 4 * p[0]) / 6.0, (s[1] + 4 * p[1]) / 6.0,
                    (s[2] + 4 * p[2]) / 6.0]
        else:
            ring = T.ordered_ring(v)
            if ring is None:
                L[v] = list(p)
                continue
            nbrs, faces = ring
            n = len(nbrs)
            se = [0.0, 0.0, 0.0]
            sf = [0.0, 0.0, 0.0]
            for j in range(n):
                q = V[nbrs[j]]
                se[0] += q[0]
                se[1] += q[1]
                se[2] += q[2]
                poly = T.F[faces[j]]
                d = V[poly[(poly.index(v) + 2) % 4]]
                sf[0] += d[0]
                sf[1] += d[1]
                sf[2] += d[2]
            den = float(n * (n + 5))
            L[v] = [(n * n * p[0] + 4 * se[0] + sf[0]) / den,
                    (n * n * p[1] + 4 * se[1] + sf[1]) / den,
                    (n * n * p[2] + 4 * se[2] + sf[2]) / den]
    return L


def _cc_limit_tangents(T, v):
    """Two tangent vectors of the limit surface at an inner vertex."""
    if T.boundary[v]:
        return None
    ring = T.ordered_ring(v)
    if ring is None:
        return None
    nbrs, faces = ring
    for f in faces:
        if len(T.F[f]) != 4:
            S, parent = _cc_subdivide(T)
            return _cc_limit_tangents(S, v)
    n = len(nbrs)
    c = math.cos(2 * math.pi / n)
    A = 1 + c + math.sqrt((c + 1) * (c + 9))
    t1 = [0.0, 0.0, 0.0]
    t2 = [0.0, 0.0, 0.0]
    for j in range(n):
        a0 = 2 * math.pi * j / n
        a1 = 2 * math.pi * (j + 1) / n
        poly = T.F[faces[j]]
        fj = T.V[poly[(poly.index(v) + 2) % 4]]
        e = T.V[nbrs[j]]
        w1, w2 = A * math.cos(a0), math.cos(a0) + math.cos(a1)
        s1, s2 = A * math.sin(a0), math.sin(a0) + math.sin(a1)
        for a in range(3):
            t1[a] += e[a] * w1 + fj[a] * w2
            t2[a] += e[a] * s1 + fj[a] * s2
    return t1, t2


def _bspline_basis(t):
    """The four uniform cubic B-spline basis functions at ``t`` in [0, 1]."""
    t2 = t * t
    t3 = t2 * t
    return ((1 - 3 * t + 3 * t2 - t3) / 6.0, (4 - 6 * t2 + 3 * t3) / 6.0,
            (1 + 3 * t + 3 * t2 - 3 * t3) / 6.0, t3 / 6.0)


def _eval_bicubic(P, u, v):
    """Point of the bicubic B-spline patch with 4x4 control net ``P[i][j]``."""
    Nu = _bspline_basis(u)
    Nv = _bspline_basis(v)
    x = y = z = 0.0
    for i in range(4):
        wi = Nu[i]
        if wi == 0.0:
            continue
        row = P[i]
        for j in range(4):
            w = wi * Nv[j]
            c = row[j]
            x += c[0] * w
            y += c[1] * w
            z += c[2] * w
    return [x, y, z]


def _regular_stencil(T, f):
    """The 4x4 control net of quad ``f`` when its surroundings are regular
    (all valences 4, all faces quads), or ``None``.

    Missing rows along a border are reflected (``2a - b``), which is the
    B-spline curve rule for the rim.
    """
    q = T.F[f]
    if len(q) != 4:
        return None
    V = T.V
    P = [[None] * 4 for _ in range(4)]
    have = [[0] * 4 for _ in range(4)]
    P[1][1], P[2][1], P[2][2], P[1][2] = V[q[0]], V[q[1]], V[q[2]], V[q[3]]
    have[1][1] = have[2][1] = have[2][2] = have[1][2] = 1
    ci = (1, 2, 2, 1)
    cj = (1, 1, 2, 2)
    for k in range(4):
        v = q[k]
        bnd = T.boundary[v]
        nfc = len(T.VF[v])
        if not bnd and (nfc != 4 or len(T.VE[v]) != 4):
            return None
        if bnd and nfc > 2:
            return None
        ring = T.ordered_ring(v)
        if ring is None:
            return None
        nb, fc = ring
        for g in fc:
            if len(T.F[g]) != 4:
                return None
        vn, vp = q[(k + 1) % 4], q[(k + 3) % 4]
        dn = (ci[(k + 1) % 4] - ci[k], cj[(k + 1) % 4] - cj[k])
        dp = (ci[(k + 3) % 4] - ci[k], cj[(k + 3) % 4] - cj[k])
        n = len(nb)
        if vn not in nb:
            return None
        s = nb.index(vn)
        if nb[(s + 1) % n] != vp:
            return None
        dirs = (dn, dp, (-dn[0], -dn[1]), (-dp[0], -dp[1]))
        for idx in range(n):
            off = (idx - s) % 4
            gi, gj = ci[k] + dirs[off][0], cj[k] + dirs[off][1]
            if gi < 0 or gi > 3 or gj < 0 or gj > 3:
                return None
            P[gi][gj] = V[nb[idx]]
            have[gi][gj] = 1
        for idx in range(len(fc)):
            off = (idx - s) % 4
            poly = T.F[fc[idx]]
            diag = poly[(poly.index(v) + 2) % 4]
            gi = ci[k] + dirs[off][0] + dirs[(off + 1) % 4][0]
            gj = cj[k] + dirs[off][1] + dirs[(off + 1) % 4][1]
            if gi < 0 or gi > 3 or gj < 0 or gj > 3:
                return None
            P[gi][gj] = V[diag]
            have[gi][gj] = 1
    miss = (not have[0][1] and not have[0][2], not have[3][1] and not have[3][2],
            not have[1][0] and not have[2][0], not have[1][3] and not have[2][3])
    if (have[0][1] != have[0][2] or have[3][1] != have[3][2]
            or have[1][0] != have[2][0] or have[1][3] != have[2][3]):
        return None

    def refl(a, b):
        return [2 * a[0] - b[0], 2 * a[1] - b[1], 2 * a[2] - b[2]]

    def bil(a, b, c):
        return [a[0] + b[0] - c[0], a[1] + b[1] - c[1], a[2] + b[2] - c[2]]

    for t in (1, 2):
        if miss[0]:
            P[0][t] = refl(P[1][t], P[2][t])
        if miss[1]:
            P[3][t] = refl(P[2][t], P[1][t])
        if miss[2]:
            P[t][0] = refl(P[t][1], P[t][2])
        if miss[3]:
            P[t][3] = refl(P[t][2], P[t][1])
    if not have[0][0]:
        P[0][0] = (refl(P[1][0], P[2][0]) if miss[0] else
                   refl(P[0][1], P[0][2]) if miss[2] else
                   bil(P[0][1], P[1][0], P[1][1]))
    if not have[3][0]:
        P[3][0] = (refl(P[2][0], P[1][0]) if miss[1] else
                   refl(P[3][1], P[3][2]) if miss[2] else
                   bil(P[3][1], P[2][0], P[2][1]))
    if not have[0][3]:
        P[0][3] = (refl(P[1][3], P[2][3]) if miss[0] else
                   refl(P[0][2], P[0][1]) if miss[3] else
                   bil(P[0][2], P[1][3], P[1][2]))
    if not have[3][3]:
        P[3][3] = (refl(P[2][3], P[1][3]) if miss[1] else
                   refl(P[3][2], P[3][1]) if miss[3] else
                   bil(P[3][2], P[2][3], P[2][2]))
    return P


def _neighbourhood(T, f, origin_corner):
    """The faces around face ``f`` as a small mesh of their own, with ``f``
    first and its corners rotated so that ``origin_corner`` comes first."""
    faces = [f]
    seen = set([f])
    for v in T.F[f]:
        for g in T.VF[v]:
            if g not in seen:
                seen.add(g)
                faces.append(g)
    vmap = {}
    LV, LF = [], []
    for g in faces:
        poly = T.F[g]
        m = len(poly)
        start = origin_corner if g == f else 0
        out = []
        for k in range(m):
            v = poly[(start + k) % m]
            idx = vmap.get(v)
            if idx is None:
                idx = len(LV)
                LV.append(T.V[v])
                vmap[v] = idx
            out.append(idx)
        LF.append(out)
    return _Topo(LV, LF)


class _PatchTree(object):
    """Evaluates the limit surface over one quad next to an extraordinary
    vertex by subdividing its neighbourhood only as deep as a query needs
    (Algorithm 1 of the paper)."""

    __slots__ = ("root",)
    MAX_DEPTH = 48

    def __init__(self, T, f):
        self.root = self._node(_neighbourhood(T, f, 0), 0)

    @staticmethod
    def _node(L, depth):
        return {"M": L, "depth": depth, "P": _regular_stencil(L, 0),
                "child": [None, None, None, None], "sub": None}

    def _child(self, node, k):
        ch = node["child"][k]
        if ch is not None:
            return ch
        if node["sub"] is None:
            node["sub"], parent = _cc_subdivide(node["M"])
        origin = (0, 3, 2, 1)
        ch = self._node(_neighbourhood(node["sub"], k, origin[k]),
                        node["depth"] + 1)
        node["child"][k] = ch
        return ch

    def eval(self, u, v):
        node = self.root
        depth = 0
        while node["P"] is None:
            if depth >= self.MAX_DEPTH:
                L = _cc_limit_positions(node["M"])
                corner = (0 if v < 0.5 else 3) if u < 0.5 else (1 if v < 0.5 else 2)
                return L[node["M"].F[0][corner]]
            if u < 0.5:
                if v < 0.5:
                    k, u, v = 0, 2 * u, 2 * v
                else:
                    k, u, v = 3, 2 * u, 2 * v - 1
            else:
                if v < 0.5:
                    k, u, v = 1, 2 * u - 1, 2 * v
                else:
                    k, u, v = 2, 2 * u - 1, 2 * v - 1
            node = self._child(node, k)
            depth += 1
        return _eval_bicubic(node["P"], u, v)


def _nu_norm(a, b, p):
    """The paper's norm ``nu(s, t) = ((s^p + t^p) / (1 + s^p t^p))^(1/p)``."""
    if p > 64:
        return max(a, b)
    ap, bp = a ** p, b ** p
    return ((ap + bp) / (1 + ap * bp)) ** (1.0 / p)


class _PolygonDomain(object):
    """The regular m-gon in the plane, split into m kites
    ``[corner_k, edge_mid_k, centre, edge_mid_{k-1}]`` (Section 5 of the
    paper): the parameter domain of one control face."""

    __slots__ = ("m", "P", "E")
    _cache = {}

    def __init__(self, m):
        self.m = m
        self.P = [(math.cos(2 * math.pi * k / m), math.sin(2 * math.pi * k / m))
                  for k in range(m)]
        self.E = [((self.P[k][0] + self.P[(k + 1) % m][0]) / 2.0,
                   (self.P[k][1] + self.P[(k + 1) % m][1]) / 2.0)
                  for k in range(m)]

    @classmethod
    def get(cls, m):
        d = cls._cache.get(m)
        if d is None:
            d = cls._cache[m] = cls(m)
        return d

    def kite_map(self, k, u, v):
        a, b, d = self.P[k], self.E[k], self.E[(k + self.m - 1) % self.m]
        wa, wb, wd = (1 - u) * (1 - v), u * (1 - v), (1 - u) * v
        return (a[0] * wa + b[0] * wb + d[0] * wd,
                a[1] * wa + b[1] * wb + d[1] * wd)

    def kite_of(self, x):
        if x[0] == 0 and x[1] == 0:
            return 0
        t = math.atan2(x[1], x[0]) / (2 * math.pi) * self.m + 0.5
        return int(math.floor(t)) % self.m

    def kite_inverse(self, k, x):
        a, b, d = self.P[k], self.E[k], self.E[(k + self.m - 1) % self.m]
        e1 = (b[0] - a[0], b[1] - a[1])
        e2 = (d[0] - a[0], d[1] - a[1])
        e3 = (-(b[0] + d[0] - a[0]), -(b[1] + d[1] - a[1]))
        u = v = 0.5
        for _ in range(40):
            rx = a[0] + e1[0] * u + e2[0] * v + e3[0] * u * v - x[0]
            ry = a[1] + e1[1] * u + e2[1] * v + e3[1] * u * v - x[1]
            jux, juy = e1[0] + e3[0] * v, e1[1] + e3[1] * v
            jvx, jvy = e2[0] + e3[0] * u, e2[1] + e3[1] * u
            det = jux * jvy - juy * jvx
            if abs(det) < 1e-300:
                break
            du = (rx * jvy - ry * jvx) / det
            dv = (jux * ry - juy * rx) / det
            u -= du
            v -= dv
            if abs(du) + abs(dv) < 1e-16:
                break
        return (min(1.0, max(0.0, u)), min(1.0, max(0.0, v)))

    def wachspress(self, x):
        m = self.m
        A = [0.0] * m
        for j in range(m):
            a, b = self.P[j], self.P[(j + 1) % m]
            s = (a[0] - x[0]) * (b[1] - x[1]) - (a[1] - x[1]) * (b[0] - x[0])
            A[j] = s if s > 0 else 0.0
        lam = [0.0] * m
        total = 0.0
        for i in range(m):
            w = 1.0
            im = (i + m - 1) % m
            for j in range(m):
                if j != i and j != im:
                    w *= A[j]
            lam[i] = w
            total += w
        if total > 0:
            for i in range(m):
                lam[i] /= total
        else:
            best, bd = 0, None
            for i in range(m):
                dx, dy = self.P[i][0] - x[0], self.P[i][1] - x[1]
                d = dx * dx + dy * dy
                if bd is None or d < bd:
                    bd, best = d, i
            for i in range(m):
                lam[i] = 0.0
            lam[best] = 1.0
        return lam

    def corner_nu(self, lam, k, p):
        m = self.m
        kp, km = (k + 1) % m, (k + m - 1) % m
        s, t = 1 - lam[k] - lam[km], 1 - lam[k] - lam[kp]
        if m == 3:
            ds, dt = 1 - lam[km], 1 - lam[kp]
            s = s / ds if ds > 1e-300 else 0.0
            t = t / dt if dt > 1e-300 else 0.0
        s = min(1.0, max(0.0, s))
        t = min(1.0, max(0.0, t))
        return _nu_norm(s, t, p)


def _face_reparam(dom, gamma, gamma_centre, p):
    """The map psi of one control face: Wachspress blend of the radial
    corner maps, then the radial centre map.  Returns ``(trivial, apply)``."""
    m = dom.m
    any_corner = any(g != 1 for g in gamma)
    trivial = not any_corner and gamma_centre == 1

    def apply(x):
        y = x
        if any_corner:
            lam = dom.wachspress(x)
            y0 = y1 = 0.0
            for k in range(m):
                w = lam[k]
                if w == 0:
                    continue
                if gamma[k] == 1:
                    y0 += x[0] * w
                    y1 += x[1] * w
                    continue
                nu = dom.corner_nu(lam, k, p)
                r = nu ** (gamma[k] - 1) if nu > 0 else 0.0
                P = dom.P[k]
                y0 += (P[0] + (x[0] - P[0]) * r) * w
                y1 += (P[1] + (x[1] - P[1]) * r) * w
            y = (y0, y1)
        if gamma_centre != 1:
            k = dom.kite_of(y)
            uv = dom.kite_inverse(k, y)
            nuF = _nu_norm(1 - uv[0], 1 - uv[1], p)
            if nuF > 0:
                r = nuF ** (gamma_centre - 1)
                y = (y[0] * r, y[1] * r)
        return y

    return trivial, apply


def _face_node_count(m, n):
    q = n // 2
    if n % 2 == 1:
        return m * q * q
    return m * (q - 1) * (q - 1) + m * (q - 1) + 1 if q >= 1 else 0


def _topology_of(M, repair=True):
    """Build the :class:`_Topo` of a mesh, tidying it first when asked."""
    M = as_mesh(M)
    if repair:
        M = _repair_for_subdivision(M)
    else:
        M = M.copy()
    return _Topo([list(p) for p in M.V], [list(f) for f in M.F]), M


def _repair_for_subdivision(M):
    """Weld, drop rubbish, close T-junctions, cut non-manifold edges and
    vertices apart, drop unused vertices and make the winding consistent --
    everything subdivision needs from a model built by stacking parts."""
    M = M.copy()
    lo, hi = bbox(M)
    diag = _norm(_sub(hi, lo))
    tol = 1e-7 * (diag if diag > 0 else 1.0)
    _weld(M, tol)
    _drop_degenerate(M)
    _drop_internal(M)
    _dedup_faces(M)
    M = heal(M, 1e-6 * (diag if diag > 0 else 1.0))
    _drop_degenerate(M)
    _cut_non_manifold(M)
    _drop_unused(M)
    if M.F:
        M = fix_normals(M)
    return M


def _cut_non_manifold(M):
    """Separate faces that meet along an edge shared by three or more faces,
    or only at a vertex, by giving them copies of the vertex (in place)."""
    for _pass in range(4):
        emap = {}
        for f, poly in enumerate(M.F):
            m = len(poly)
            for k in range(m):
                a, b = poly[k], poly[(k + 1) % m]
                emap.setdefault((a, b) if a < b else (b, a), []).append((f, k))
        any_bad = False
        partner = [[-1] * len(poly) for poly in M.F]
        detach = []
        for lst in emap.values():
            if len(lst) == 2:
                (f0, k0), (f1, k1) = lst
                partner[f0][k0] = f1
                partner[f1][k1] = f0
                continue
            if len(lst) < 2:
                continue
            any_bad = True
            used = [False] * len(lst)
            for i in range(len(lst)):
                if used[i]:
                    continue
                fa, ka = lst[i]
                a0 = M.F[fa][ka]
                best = -1
                for j in range(i + 1, len(lst)):
                    if not used[j] and M.F[lst[j][0]][lst[j][1]] != a0:
                        best = j
                        break
                if best < 0:
                    for j in range(i + 1, len(lst)):
                        if not used[j]:
                            best = j
                            break
                if best < 0:
                    detach.append(lst[i])
                    used[i] = True
                    continue
                used[i] = used[best] = True
                fb, kb = lst[best]
                partner[fa][ka] = fb
                partner[fb][kb] = fa
        for f, k in detach:
            m = len(M.F[f])
            for idx in (k, (k + 1) % m):
                M.V.append(list(M.V[M.F[f][idx]]))
                M.F[f][idx] = len(M.V) - 1
        vf = [[] for _ in M.V]
        for f, poly in enumerate(M.F):
            for k, v in enumerate(poly):
                vf[v].append((f, k))
        nv0 = len(M.V)
        any_split = False
        for v in range(nv0):
            lst = vf[v]
            if len(lst) <= 1:
                continue
            pos = {}
            for i, (f, k) in enumerate(lst):
                pos[f] = i
            group = list(range(len(lst)))

            def find(x):
                while group[x] != x:
                    group[x] = group[group[x]]
                    x = group[x]
                return x

            for i, (f, k) in enumerate(lst):
                m = len(M.F[f])
                for g in (partner[f][k], partner[f][(k + m - 1) % m]):
                    if g < 0:
                        continue
                    j = pos.get(g)
                    if j is not None:
                        a, b = find(i), find(j)
                        if a != b:
                            group[a] = b
            fan = {}
            for i, (f, k) in enumerate(lst):
                r = find(i)
                vid = fan.get(r)
                if vid is None:
                    vid = v
                    if fan:
                        M.V.append(list(M.V[v]))
                        vid = len(M.V) - 1
                    fan[r] = vid
                M.F[f][k] = vid
            if len(fan) > 1:
                any_split = True
        if not any_bad and not any_split:
            break
    return M


def catmull_clark(M, steps=1, repair=True):
    """Classical Catmull-Clark subdivision: every face becomes quads and
    the shape is rounded, ``steps`` times.

    A cube turns into a rounded cube, then into a near sphere; a
    dodecahedron into a ball with twelve soft dimples.  Border edges are
    kept as smooth curves.  Faces inherit the colour of the face they came
    from.  ``repair=True`` first welds and tidies the mesh the way
    subdivision needs (parts that only touch are cut apart).  For any
    number of cells per edge -- not only 2, 4, 8 -- see :func:`smooth`::

        add.box([0, 0, 0], 2, "red")
        add.mesh(add.catmull_clark(add.layer(), 3))     # 384 quads
    """
    T, M = _topology_of(M, repair)
    colors = list(M.C)
    for _ in range(int(steps)):
        T, parent = _cc_subdivide(T)
        colors = [colors[p] for p in parent]
    return Mesh([list(p) for p in T.V], [list(f) for f in T.F], colors)


def smooth(M, n=4, uniform=True, centre=True, p=2.0, scale=1.0, repair=True):
    """Round a polygon mesh into its Catmull-Clark limit surface, sampled
    with ``n`` cells along every control edge -- for *any* ``n``.

    This is the generalised Catmull-Clark algorithm (Sabaliauskas, 2026):
    each control face (triangle, quad, pentagon ...) is covered by a grid
    of ``n x n`` cells per corner kite, every node of which lies exactly on
    the smooth limit surface.  ``n = 1`` moves the control vertices to the
    surface without adding faces; ``n = 2`` is the classical subdivision
    step (with the vertices at their limit); ``n = 3, 5, 7`` leave a small
    polygon in the middle of each face, even ``n`` meet at a centre node.
    Cells keep the colour of the control face they lie on, so a coloured
    box stays a coloured pillow.

    ``uniform=True`` applies the paper's reparameterisation near the
    extraordinary vertices and non-quad faces, so that the cells come out
    evenly sized; ``uniform=False`` gives the plain characteristic-map
    grid.  ``centre`` switches the extra centre map of non-quad faces,
    ``p`` is the exponent of the blending norm and ``scale`` multiplies
    the exponents (1 = the theoretical value).  ``repair=True`` welds and
    tidies the mesh first.  Non-manifold meshes are cut apart, so voxel
    models and stacked parts smooth too -- they just stay separate pieces::

        add.dodecahedron([0, 0, 0], 2, "gold")
        add.mesh(add.smooth(add.layer(), 5))           # 12 * 5 ... cells
    """
    n = int(n)
    if n < 1:
        raise ValueError("n must be at least 1")
    T, M0 = _topology_of(M, repair)
    if not T.F:
        return Mesh()
    colors = list(M0.C)
    T1, parent1 = _cc_subdivide(T)
    q, odd = n // 2, (n % 2 == 1)
    nv, ne, nf = len(T.V), len(T.E), len(T.F)
    face_base = [0] * (nf + 1)
    kite_offset = [0] * (nf + 1)
    face_base[0] = nv + ne * (n - 1)
    for f in range(nf):
        m = len(T.F[f])
        face_base[f + 1] = face_base[f] + _face_node_count(m, n)
        kite_offset[f + 1] = kite_offset[f] + m
    total = face_base[nf]
    GV = [None] * total
    done = [False] * total
    L = _cc_limit_positions(T1)
    for v in range(nv):
        GV[v] = L[v]
        done[v] = True
    F1 = T1.F
    V1 = T1.V

    def edge_node(f, k, t):
        poly = T.F[f]
        m = len(poly)
        a, b = poly[k], poly[(k + 1) % m]
        e = T.FE[f][k]
        tt = t if a < b else n - t
        return nv + e * (n - 1) + (tt - 1)

    def node_id(f, k, i, j):
        poly = T.F[f]
        m = len(poly)
        if i == 0 and j == 0:
            return poly[k]
        if j == 0:
            return edge_node(f, k, i)
        if i == 0:
            return edge_node(f, (k + m - 1) % m, n - j)
        base = face_base[f]
        if not odd:
            inner = m * (q - 1) * (q - 1)
            if i == q and j == q:
                return base + inner + m * (q - 1)
            if i == q:
                return base + inner + k * (q - 1) + (j - 1)
            if j == q:
                return base + inner + ((k + m - 1) % m) * (q - 1) + (i - 1)
            return base + k * (q - 1) * (q - 1) + (i - 1) * (q - 1) + (j - 1)
        return base + k * q * q + (i - 1) * q + (j - 1)

    out_faces = []
    out_colors = []
    for f in range(nf):
        poly = T.F[f]
        m = len(poly)
        dom = _PolygonDomain.get(m)
        gamma = [1.0] * m
        gamma_centre = 1.0
        if uniform:
            for k in range(m):
                v = poly[k]
                g = 1.0 if T.boundary[v] else _cc_gamma(len(T.VE[v]))
                gamma[k] = 1 + (g - 1) * scale
            if m != 4 and centre:
                gamma_centre = 1 + (_cc_gamma(m) - 1) * scale
        trivial, apply = _face_reparam(dom, gamma, gamma_centre, p)
        evaluators = [None] * m

        def evaluate(k, u, v):
            ev = evaluators[k]
            if ev is None:
                P = _regular_stencil(T1, kite_offset[f] + k)
                ev = evaluators[k] = (P, None) if P is not None else \
                    (None, _PatchTree(T1, kite_offset[f] + k))
            if ev[0] is not None:
                return _eval_bicubic(ev[0], u, v)
            return ev[1].eval(u, v)

        for k in range(m):
            for i in range(q + 1):
                for j in range(q + 1):
                    nid = node_id(f, k, i, j)
                    if done[nid]:
                        continue
                    u0, v0 = 2.0 * i / n, 2.0 * j / n
                    kk, u, v = k, u0, v0
                    if not trivial:
                        y = apply(dom.kite_map(k, u0, v0))
                        kk = dom.kite_of(y)
                        u, v = dom.kite_inverse(kk, y)
                    if u > 1 - 1e-12 and v > 1 - 1e-12:
                        GV[nid] = L[nv + ne + f]        # the face point
                    else:
                        GV[nid] = evaluate(kk, u, v)
                    done[nid] = True
        color = colors[f]
        for k in range(m):
            for i in range(q):
                for j in range(q):
                    out_faces.append([node_id(f, k, i, j), node_id(f, k, i + 1, j),
                                      node_id(f, k, i + 1, j + 1),
                                      node_id(f, k, i, j + 1)])
                    out_colors.append(color)
        if odd:
            for k in range(m):
                k1 = (k + 1) % m
                for j in range(q):
                    out_faces.append([node_id(f, k, q, j), node_id(f, k1, j, q),
                                      node_id(f, k1, j + 1, q),
                                      node_id(f, k, q, j + 1)])
                    out_colors.append(color)
            out_faces.append([node_id(f, k, q, q) for k in range(m)])
            out_colors.append(color)
    for i in range(total):
        if GV[i] is None:                       # cannot happen; keep files valid
            GV[i] = [0.0, 0.0, 0.0]
    return Mesh([list(p) for p in GV], out_faces, out_colors)


#: Other name for :func:`catmull_clark`.
subdivide = catmull_clark


# ============================================================================
# 25. Saving and loading
# ============================================================================

def save(path, M=None, clear_scene=None, colors=None):
    """Write a model to disk; the file format follows the extension.

    ``.off`` (the course format), ``.obj`` (+ a ``.mtl`` colour file, which is
    what Sketchfab and most other tools want), ``.ply`` or ``.stl``::

        add.save("dragon.obj")

    Called without a mesh it saves -- and then empties -- the current scene,
    exactly like add.py 1.2's ``off()``.  ``colors=50`` reduces the model
    to at most that many colours first (see :func:`limit_colors`), which
    keeps an ``.obj`` within Sketchfab's material limit.
    """
    if clear_scene is None:
        clear_scene = M is None
    mesh_to_save = as_mesh(M)
    if colors is not None:
        mesh_to_save = limit_colors(mesh_to_save, colors)
    ext = path.lower().rsplit(".", 1)[-1] if "." in path else "off"
    if ext == "obj":
        _write_obj(path, mesh_to_save)
    elif ext == "ply":
        _write_ply(path, mesh_to_save)
    elif ext == "stl":
        _write_stl(path, mesh_to_save)
    else:
        _write_off(path, mesh_to_save)
    if clear_scene:
        clear()
    return path


def off(path, M=None):
    """Write an OFF file (and empty the scene) -- the add.py 1.2 behaviour."""
    clear_scene = M is None
    _write_off(path, as_mesh(M))
    if clear_scene:
        clear()
    return path


def obj(path, M=None, mtl=None):
    """Write an OBJ file plus the matching MTL colour file.

    OBJ is what you need for Sketchfab: upload the ``.obj`` and ``.mtl``
    together (in one ``.zip``/``.7z``) and the colours come along.
    """
    clear_scene = M is None
    _write_obj(path, as_mesh(M), mtl)
    if clear_scene:
        clear()
    return path


def _write_off(path, M):
    with open(path, "w") as f:
        f.write("OFF\n%d %d 0\n" % (len(M.V), len(M.F)))
        out = []
        for p in M.V:
            out.append("%s %s %s\n" % (_num(p[0]), _num(p[1]), _num(p[2])))
        f.write("".join(out))
        out = []
        for face, c in zip(M.F, M.C):
            out.append("%d %s %d %d %d\n" % (len(face),
                                             " ".join(str(i) for i in face),
                                             c[0], c[1], c[2]))
        f.write("".join(out))


def _material_name(c):
    """``color_rrggbb``, plus ``_aNNN`` when see-through and ``_tNAME`` when
    textured -- one material per distinct look."""
    r, g, b, alpha, image = _material(c)
    name = "color_%02x%02x%02x" % (r, g, b)
    if alpha < 1.0:
        name += "_a%03d" % int(round(alpha * 1000))
    if image:
        stem = image.replace("\\", "/").rsplit("/", 1)[-1].rsplit(".", 1)[0]
        name += "_t" + "".join(ch if ch.isalnum() else "_" for ch in stem)
    return name


def _write_obj(path, M, mtl_path=None):
    if mtl_path is None:
        mtl_path = path[:-4] + ".mtl" if path.lower().endswith(".obj") \
            else path + ".mtl"
    mtl_name = mtl_path.replace("\\", "/").rsplit("/", 1)[-1]

    palette = []
    seen = {}
    for c in M.C:
        if c not in seen:
            seen[c] = _material_name(c)
            palette.append(c)

    with open(path, "w") as f:
        f.write("# written by add.py %s\n" % __version__)
        f.write("mtllib %s\n" % mtl_name)
        f.write("o model\n")
        out = []
        for p in M.V:
            out.append("v %s %s %s\n" % (_num(p[0]), _num(p[1]), _num(p[2])))
        f.write("".join(out))
        # Texture coordinates, one line per distinct (u, v) of textured faces.
        vt_index = {}
        if M.UV is not None:
            out = []
            for k, c in enumerate(M.C):
                uv = M.UV[k]
                if uv is None or len(c) < 5:
                    continue
                for t in uv:
                    key = (round(t[0], 6), round(t[1], 6))
                    if key not in vt_index:
                        vt_index[key] = len(vt_index) + 1
                        out.append("vt %s %s\n" % (_num(key[0]), _num(key[1])))
            f.write("".join(out))
        # Group faces by colour: one `usemtl` line per colour, not per face.
        by_color = {}
        for k, (face, c) in enumerate(zip(M.F, M.C)):
            by_color.setdefault(c, []).append(k)
        for c in palette:
            f.write("usemtl %s\n" % seen[c])
            out = []
            textured = len(c) > 4 and M.UV is not None
            for k in by_color[c]:
                face = M.F[k]
                uv = M.UV[k] if textured else None
                if uv is None:
                    out.append("f %s\n" % " ".join(str(i + 1) for i in face))
                else:
                    out.append("f %s\n" % " ".join(
                        "%d/%d" % (i + 1, vt_index[(round(t[0], 6), round(t[1], 6))])
                        for i, t in zip(face, uv)))
            f.write("".join(out))

    with open(mtl_path, "w") as f:
        f.write("# written by add.py %s\n" % __version__)
        for c in palette:
            r, g, b, alpha, image = _material(c)
            f.write("newmtl %s\n" % seen[c])
            f.write("Kd %.6f %.6f %.6f\n" % (r / 255.0, g / 255.0, b / 255.0))
            f.write("Ka 0.100000 0.100000 0.100000\n")
            f.write("Ks 0.000000 0.000000 0.000000\n")
            f.write("d %.3f\n" % alpha)
            f.write("illum 1\n")
            if image:
                f.write("map_Kd %s\n" % image.replace("\\", "/").rsplit("/", 1)[-1])
            f.write("\n")
    return path


def obj_size(M=None):
    """How many bytes :func:`save` would write for this model as ``.obj``
    (the ``.mtl`` file is tiny and not counted).

    Sketchfab's free plan accepts uploads up to 100 MB (200 MB Pro, 500 MB
    Premium); the course asks for models under 50 MB.  The size is worked
    out from the numbers themselves, without writing a file::

        print(add.obj_size() / 1e6, "MB")
    """
    M = as_mesh(M)
    total = 50                                          # header lines
    for p in M.V:
        total += 5 + len(_num(p[0])) + len(_num(p[1])) + len(_num(p[2]))
    seen = set()
    vts = set()
    for k, (face, c) in enumerate(zip(M.F, M.C)):
        total += 2 + len(face)
        textured = len(c) > 4 and M.UV is not None and M.UV[k] is not None
        for i in face:
            total += len(str(i + 1))
        if textured:
            for t in M.UV[k]:
                key = (round(t[0], 6), round(t[1], 6))
                if key not in vts:
                    vts.add(key)
                    total += 6 + len(_num(key[0])) + len(_num(key[1]))
                total += 1 + len(str(len(vts)))           # "/vt" per corner
        if c not in seen:
            seen.add(c)
            total += 20 + (8 if len(c) > 3 else 0) + (10 + len(str(c[4])) if len(c) > 4 else 0)
    return total


def _write_ply(path, M):
    with open(path, "w") as f:
        f.write("ply\nformat ascii 1.0\ncomment add.py %s\n" % __version__)
        f.write("element vertex %d\n" % len(M.V))
        f.write("property float x\nproperty float y\nproperty float z\n")
        f.write("element face %d\n" % len(M.F))
        f.write("property list uchar int vertex_indices\n")
        f.write("property uchar red\nproperty uchar green\nproperty uchar blue\n")
        f.write("end_header\n")
        for p in M.V:
            f.write("%s %s %s\n" % (_num(p[0]), _num(p[1]), _num(p[2])))
        for face, c in zip(M.F, M.C):
            f.write("%d %s %d %d %d\n" % (len(face),
                                          " ".join(str(i) for i in face),
                                          c[0], c[1], c[2]))


def _write_stl(path, M):
    """ASCII STL -- the 3D printing format.  STL has no colours."""
    with open(path, "w") as f:
        f.write("solid addpy\n")
        for face in M.F:
            for t in range(1, len(face) - 1):
                a, b, c = M.V[face[0]], M.V[face[t]], M.V[face[t + 1]]
                n = _unit(_cross(_sub(b, a), _sub(c, a)))
                f.write("facet normal %.6e %.6e %.6e\n" % n)
                f.write("  outer loop\n")
                for p in (a, b, c):
                    f.write("    vertex %.6e %.6e %.6e\n" % (p[0], p[1], p[2]))
                f.write("  endloop\nendfacet\n")
        f.write("endsolid addpy\n")


class Stream(object):
    """Write a model part by part, straight to disk, so that a model far
    bigger than the computer's memory can still be built.

    ``add.stream(path)`` returns one of these.  Every :meth:`add` writes a
    mesh (or the current scene, which is then cleared) to the file at once
    and forgets it; :meth:`close` finishes the file.  Works for ``.obj``
    (materials, opacity and textures included; the ``.mtl`` is written on
    close) and ``.off`` (the counts in the header are filled in on close).
    Use it as a context manager or call ``close()`` yourself::

        with add.stream("castle.obj") as out:
            for i in range(100):
                add.sphere([i, 0, 0], 0.4, 20, "red")
                out.add()                    # the scene, then cleared
            out.add(add.make(add.box, [0, 5, 0], 2, "gold"))
        print(out.faces, "faces,", out.bytes / 1e6, "MB")
    """

    def __init__(self, path):
        self.path = path
        self.faces = 0
        self.vertices = 0
        self.bytes = 0
        self.materials = {}                    # colour tuple -> material name
        self._kind = "obj" if path.lower().endswith(".obj") else "off"
        self._vt = 0
        self._file = open(path, "w")
        if self._kind == "obj":
            mtl = path[:-4] + ".mtl"
            self._mtl = mtl
            self._file.write("# written by add.py %s\n" % __version__)
            self._file.write("mtllib %s\n" % mtl.replace("\\", "/").rsplit("/", 1)[-1])
            self._file.write("o model\n")
        else:
            self._file.write("OFF\n")
            self._header_at = self._file.tell()
            self._file.write("%12d %12d 0\n" % (0, 0))
            self._offV, self._offF = [], []
        self._current = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False

    def add(self, M=None):
        """Write a mesh to the file now.  Without a mesh the current scene is
        written and then cleared.  Returns the number of faces written."""
        if M is None:
            M = _scene
            clear_after = True
        else:
            M = as_mesh(M)
            clear_after = False
        if self._file is None:
            raise ValueError("stream is closed")
        f = self._file
        base = self.vertices
        out = []
        if self._kind == "obj":
            for p in M.V:
                out.append("v %s %s %s\n" % (_num(p[0]), _num(p[1]), _num(p[2])))
            vt_index = {}
            if M.UV is not None:
                for k, c in enumerate(M.C):
                    uv = M.UV[k]
                    if uv is None or len(c) < 5:
                        continue
                    for t in uv:
                        key = (round(t[0], 6), round(t[1], 6))
                        if key not in vt_index:
                            self._vt += 1
                            vt_index[key] = self._vt
                            out.append("vt %s %s\n" % (_num(key[0]), _num(key[1])))
            by_color = {}
            order = []
            for k, c in enumerate(M.C):
                if c not in by_color:
                    by_color[c] = []
                    order.append(c)
                by_color[c].append(k)
            for c in order:
                name = self.materials.get(c)
                if name is None:
                    name = self.materials[c] = _material_name(c)
                if c != self._current:
                    out.append("usemtl %s\n" % name)
                    self._current = c
                textured = len(c) > 4 and M.UV is not None
                for k in by_color[c]:
                    face = M.F[k]
                    uv = M.UV[k] if textured else None
                    if uv is None:
                        out.append("f %s\n" % " ".join(str(i + base + 1) for i in face))
                    else:
                        out.append("f %s\n" % " ".join(
                            "%d/%d" % (i + base + 1,
                                       vt_index[(round(t[0], 6), round(t[1], 6))])
                            for i, t in zip(face, uv)))
            text = "".join(out)
        else:
            # OFF wants every vertex before every face, so the two lists are
            # kept as text and written on close (that is why .obj is the
            # format for really big models).
            for p in M.V:
                self._offV.append("%s %s %s\n" % (_num(p[0]), _num(p[1]), _num(p[2])))
            for face, c in zip(M.F, M.C):
                self._offF.append("%d %s %d %d %d\n" % (
                    len(face), " ".join(str(i + base) for i in face), c[0], c[1], c[2]))
            text = ""
        if text:
            f.write(text)
            self.bytes += len(text)
        self.vertices += len(M.V)
        self.faces += len(M.F)
        if clear_after:
            clear()
        return len(M.F)

    def close(self):
        """Finish the file (the ``.mtl``, or the OFF header)."""
        if self._file is None:
            return self.path
        if self._kind == "obj":
            with open(self._mtl, "w") as m:
                m.write("# written by add.py %s\n" % __version__)
                for c, name in self.materials.items():
                    r, g, b, alpha, image = _material(c)
                    m.write("newmtl %s\n" % name)
                    m.write("Kd %.6f %.6f %.6f\n" % (r / 255.0, g / 255.0, b / 255.0))
                    m.write("Ka 0.100000 0.100000 0.100000\n")
                    m.write("Ks 0.000000 0.000000 0.000000\n")
                    m.write("d %.3f\n" % alpha)
                    m.write("illum 1\n")
                    if image:
                        m.write("map_Kd %s\n" % image.replace("\\", "/").rsplit("/", 1)[-1])
                    m.write("\n")
        else:
            text = "".join(self._offV) + "".join(self._offF)
            self._file.write(text)
            self.bytes += len(text)
            self._file.seek(self._header_at)
            self._file.write("%12d %12d 0\n" % (self.vertices, self.faces))
        self._file.close()
        self._file = None
        return self.path


def stream(path):
    """Open a :class:`Stream`: a model written to ``path`` part by part,
    without ever holding all of it in memory.

    The ordinary :func:`save` keeps the whole model in memory, which is fine
    up to a few million faces.  For a model of hundreds of megabytes -- a
    castle with every brick -- build it in parts and hand each part to the
    stream as soon as it is finished::

        out = add.stream("castle.obj")
        add.bricks([0, 0, 0], 40, 6, [0.5, 0.25, 0.5], "brown", seed=1)
        out.add()                       # writes the scene and clears it
        out.add(add.make(add.tree, [10, 0, 0], 5))
        out.close()                     # writes castle.mtl
        print(out.faces, out.bytes)

    For ``.off`` the vertices and faces are kept as text until ``close()``
    (the format wants all vertices before all faces), so ``.obj`` is the
    one to use for really big models.
    """
    return Stream(path)


def load(path, color=None):
    """Read a model from an ``.off``, ``.obj`` or ``.ply`` file.

    Returns a mesh you can transform and ``mesh()`` into the scene::

        letter = add.load("letters/A.off")
        add.mesh(add.move(add.zoom(letter, 0.1), [0, 2, 0]))
    """
    ext = path.lower().rsplit(".", 1)[-1] if "." in path else "off"
    if ext == "obj":
        M = _read_obj(path, color)
    elif ext == "ply":
        M = _read_ply(path, color)
    else:
        M = _read_off(path, color)
    return M


def _clean_lines(path):
    """Non-empty lines of a file with ``#`` comments stripped."""
    out = []
    with open(path, "r") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if line:
                out.append(line)
    return out


def _read_off(path, color=None):
    """Read an OFF file.  Colours may be missing, integer or 0..1 floats."""
    lines = _clean_lines(path)
    if not lines:
        return Mesh()
    row = 0
    head = lines[0].split()
    if head[0].upper().endswith("OFF"):
        row = 1
        if len(head) >= 3:                 # counts on the same line as OFF
            counts = head[1:]
        else:
            counts = lines[1].split()
            row = 2
    else:
        counts = head
        row = 1
    nv, nf = int(counts[0]), int(counts[1])

    M = Mesh()
    for _ in range(nv):
        p = lines[row].split()
        row += 1
        M.add_vertex((float(p[0]), float(p[1]), float(p[2])))

    default = rgb(color) if color is not None else DEFAULT_COLOR
    for _ in range(nf):
        p = lines[row].split()
        row += 1
        n = int(p[0])
        face = [int(x) for x in p[1:1 + n]]
        rest = p[1 + n:]
        c = default
        if len(rest) >= 3 and color is None:
            vals = [float(x) for x in rest[:3]]
            if max(vals) <= 1.0 and any(v != int(v) for v in vals):
                vals = [v * 255.0 for v in vals]
            c = rgb(vals)
        M.add_face(face, c)
    return M


def _read_obj(path, color=None):
    M = Mesh()
    materials = {}
    current = rgb(color) if color is not None else DEFAULT_COLOR
    folder = path.replace("\\", "/").rsplit("/", 1)
    folder = folder[0] + "/" if len(folder) > 1 else ""
    vt = []
    with open(path, "r") as f:
        for line in f:
            parts = line.split()
            if not parts or parts[0].startswith("#"):
                continue
            tag = parts[0]
            if tag == "v":
                M.add_vertex((float(parts[1]), float(parts[2]),
                              float(parts[3])))
            elif tag == "vt":
                vt.append((float(parts[1]), float(parts[2]) if len(parts) > 2
                           else 0.0))
            elif tag == "f":
                face = []
                uv = []
                for p in parts[1:]:
                    bits = p.split("/")
                    idx = int(bits[0])
                    face.append(idx - 1 if idx > 0 else len(M.V) + idx)
                    if len(bits) > 1 and bits[1]:
                        t = int(bits[1])
                        uv.append(vt[t - 1 if t > 0 else len(vt) + t])
                textured = len(current) > 4 and len(uv) == len(face)
                M.add_face(face, current, uv if textured else None)
            elif tag == "mtllib" and color is None:
                try:
                    materials.update(_read_mtl(folder + parts[1]))
                except IOError:
                    pass
            elif tag == "usemtl" and color is None:
                current = materials.get(parts[1], DEFAULT_COLOR)
    return M


def _read_mtl(path):
    """``{material name: colour}``, with opacity (``d`` / ``Tr``) and the
    texture image (``map_Kd``) kept in the colour tuple."""
    out = {}
    name = None
    with open(path, "r") as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue
            if parts[0] == "newmtl":
                name = parts[1]
                out[name] = DEFAULT_COLOR
            elif name is None:
                continue
            elif parts[0] == "Kd":
                c = out[name]
                out[name] = rgb([float(parts[1]) * 255, float(parts[2]) * 255,
                                 float(parts[3]) * 255] + list(c[3:]))
            elif parts[0] in ("d", "Tr") and len(parts) > 1:
                alpha = float(parts[1])
                if parts[0] == "Tr":
                    alpha = 1.0 - alpha
                c = out[name]
                out[name] = rgb((c[0], c[1], c[2], alpha) + tuple(c[4:5]))
            elif parts[0] == "map_Kd" and len(parts) > 1:
                c = out[name]
                out[name] = rgb((c[0], c[1], c[2], c[3] if len(c) > 3 else 1.0,
                                 parts[-1]))
    return out


def write_png(path, rows):
    """Write a picture -- a list of rows, each a list of colours -- as a
    ``.png``, to use as a texture (see :func:`texture`).

    Row 0 is the top of the picture.  Any colour form that :func:`rgb`
    accepts works, so a 64 x 64 chequerboard is::

        rows = [["white" if (x // 8 + y // 8) % 2 else "black"
                 for x in range(64)] for y in range(64)]
        add.write_png("check.png", rows)
    """
    import struct
    import zlib
    height = len(rows)
    width = len(rows[0]) if height else 0
    raw = bytearray()
    for row in rows:
        raw.append(0)                                   # filter type "none"
        for c in row:
            c = rgb(c)
            raw.append(c[0])
            raw.append(c[1])
            raw.append(c[2])

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", header))
        f.write(chunk(b"IDAT", zlib.compress(bytes(raw), 6)))
        f.write(chunk(b"IEND", b""))
    return path


def _read_ply(path, color=None):
    with open(path, "r") as f:
        text = f.read().split("\n")
    nv = nf = 0
    head = 0
    props = []
    element = None
    for i, line in enumerate(text):
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "element":
            element = parts[1]
            if element == "vertex":
                nv = int(parts[2])
            elif element == "face":
                nf = int(parts[2])
        elif parts[0] == "property" and element == "vertex":
            props.append(parts[-1])
        elif parts[0] == "end_header":
            head = i + 1
            break
    M = Mesh()
    row = head
    for _ in range(nv):
        vals = text[row].split()
        row += 1
        d = dict(zip(props, vals))
        M.add_vertex((float(d.get("x", 0)), float(d.get("y", 0)),
                      float(d.get("z", 0))))
    default = rgb(color) if color is not None else DEFAULT_COLOR
    for _ in range(nf):
        vals = text[row].split()
        row += 1
        n = int(vals[0])
        face = [int(v) for v in vals[1:1 + n]]
        c = default
        if len(vals) >= 1 + n + 3 and color is None:
            c = rgb([float(v) for v in vals[1 + n:4 + n]])
        M.add_face(face, c)
    return M


def load_font(folder, characters=None, suffix=".off"):
    """Load a whole folder of letter or digit models into a dictionary.

    ``add.load_font("letters")`` gives ``{"A": mesh, "B": mesh, ...}`` so a
    word can be written with a loop instead of one ``load`` per character.
    """
    import os
    out = {}
    names = characters
    if names is None:
        try:
            names = [n[:-len(suffix)] for n in os.listdir(folder)
                     if n.endswith(suffix)]
        except OSError:
            return out
    for name in names:
        try:
            out[name] = load(os.path.join(folder, name + suffix))
        except (IOError, OSError, ValueError):
            pass
    return out


def typeset(characters, font, at=(0, 0, 0), size=1.0, spacing=1.0, color=None,
            plane=((1, 0, 0), (0, 1, 0))):
    """Lay a string of already-loaded glyph *meshes* out in a row and merge them.

    ``font`` is the dictionary returned by :func:`load_font` -- letters that
    were modelled as .off files, like the course's letter set.  (For a
    quick label drawn from add.py's own built-in font see :func:`text`.)
    """
    u, v = plane
    out = Mesh()
    x = 0.0
    for ch in characters:
        glyph_mesh = font.get(ch) or font.get(ch.upper())
        if glyph_mesh is None:
            x += spacing
            continue
        G = fit(as_mesh(glyph_mesh), size)
        G = place(G, (0, 0, 0))
        pos = (at[0] + u[0] * x * spacing * size,
               at[1] + u[1] * x * spacing * size,
               at[2] + u[2] * x * spacing * size)
        G = move(G, pos)
        if color is not None:
            G = _paint(G, color)
        out.extend(G)
        x += 1.0
    return out


# ============================================================================
# 26. Letters and labels
# ============================================================================
# A small stroke font: every character is a few polylines on a grid that is
# 4 units wide and 6 units tall (Y up).  ``text`` draws them as round bars,
# so a model can carry its own title, a scale or a name plate.

_FONT = {
    "A": (4, [[(0, 0), (0, 4), (2, 6), (4, 4), (4, 0)], [(0, 2), (4, 2)]]),
    "B": (4, [[(0, 0), (0, 6), (3, 6), (4, 5), (4, 4), (3, 3), (0, 3)],
              [(3, 3), (4, 2), (4, 1), (3, 0), (0, 0)]]),
    "C": (4, [[(4, 5), (3, 6), (1, 6), (0, 5), (0, 1), (1, 0), (3, 0), (4, 1)]]),
    "D": (4, [[(0, 0), (0, 6), (3, 6), (4, 5), (4, 1), (3, 0), (0, 0)]]),
    "E": (4, [[(4, 6), (0, 6), (0, 0), (4, 0)], [(0, 3), (3, 3)]]),
    "F": (4, [[(4, 6), (0, 6), (0, 0)], [(0, 3), (3, 3)]]),
    "G": (4, [[(4, 5), (3, 6), (1, 6), (0, 5), (0, 1), (1, 0), (3, 0), (4, 1),
               (4, 3), (2, 3)]]),
    "H": (4, [[(0, 0), (0, 6)], [(4, 0), (4, 6)], [(0, 3), (4, 3)]]),
    "I": (2, [[(0, 6), (2, 6)], [(1, 6), (1, 0)], [(0, 0), (2, 0)]]),
    "J": (4, [[(4, 6), (4, 1), (3, 0), (1, 0), (0, 1)]]),
    "K": (4, [[(0, 0), (0, 6)], [(4, 6), (0, 2)], [(1.3, 3), (4, 0)]]),
    "L": (4, [[(0, 6), (0, 0), (4, 0)]]),
    "M": (4, [[(0, 0), (0, 6), (2, 3), (4, 6), (4, 0)]]),
    "N": (4, [[(0, 0), (0, 6), (4, 0), (4, 6)]]),
    "O": (4, [[(1, 0), (0, 1), (0, 5), (1, 6), (3, 6), (4, 5), (4, 1), (3, 0), (1, 0)]]),
    "P": (4, [[(0, 0), (0, 6), (3, 6), (4, 5), (4, 4), (3, 3), (0, 3)]]),
    "Q": (4, [[(1, 0), (0, 1), (0, 5), (1, 6), (3, 6), (4, 5), (4, 1), (3, 0), (1, 0)],
              [(2.5, 1.5), (4.3, -0.3)]]),
    "R": (4, [[(0, 0), (0, 6), (3, 6), (4, 5), (4, 4), (3, 3), (0, 3)], [(2, 3), (4, 0)]]),
    "S": (4, [[(4, 5), (3, 6), (1, 6), (0, 5), (0, 4), (1, 3), (3, 3), (4, 2),
               (4, 1), (3, 0), (1, 0), (0, 1)]]),
    "T": (4, [[(0, 6), (4, 6)], [(2, 6), (2, 0)]]),
    "U": (4, [[(0, 6), (0, 1), (1, 0), (3, 0), (4, 1), (4, 6)]]),
    "V": (4, [[(0, 6), (2, 0), (4, 6)]]),
    "W": (4, [[(0, 6), (1, 0), (2, 4), (3, 0), (4, 6)]]),
    "X": (4, [[(0, 0), (4, 6)], [(0, 6), (4, 0)]]),
    "Y": (4, [[(0, 6), (2, 3), (4, 6)], [(2, 3), (2, 0)]]),
    "Z": (4, [[(0, 6), (4, 6), (0, 0), (4, 0)]]),
    "0": (4, [[(1, 0), (0, 1), (0, 5), (1, 6), (3, 6), (4, 5), (4, 1), (3, 0), (1, 0)],
              [(0.6, 1), (3.4, 5)]]),
    "1": (4, [[(0.5, 4.5), (2, 6), (2, 0)], [(0.5, 0), (3.5, 0)]]),
    "2": (4, [[(0, 5), (1, 6), (3, 6), (4, 5), (4, 4), (0, 0), (4, 0)]]),
    "3": (4, [[(0, 6), (4, 6), (2, 3.5), (3, 3.5), (4, 2.5), (4, 1), (3, 0), (1, 0), (0, 1)]]),
    "4": (4, [[(3, 0), (3, 6), (0, 2), (4, 2)]]),
    "5": (4, [[(4, 6), (0, 6), (0, 3), (3, 3), (4, 2), (4, 1), (3, 0), (1, 0), (0, 1)]]),
    "6": (4, [[(4, 5), (3, 6), (1, 6), (0, 5), (0, 1), (1, 0), (3, 0), (4, 1), (4, 2),
               (3, 3), (0, 3)]]),
    "7": (4, [[(0, 6), (4, 6), (1.5, 0)]]),
    "8": (4, [[(1, 3), (0, 4), (0, 5), (1, 6), (3, 6), (4, 5), (4, 4), (3, 3), (1, 3),
               (0, 2), (0, 1), (1, 0), (3, 0), (4, 1), (4, 2), (3, 3)]]),
    "9": (4, [[(4, 3), (1, 3), (0, 4), (0, 5), (1, 6), (3, 6), (4, 5), (4, 1), (3, 0),
               (1, 0), (0, 1)]]),
    " ": (2, []),
    ".": (1, [[(0.5, 0), (0.5, 0.3)]]),
    ",": (1, [[(0.6, 0.5), (0.3, -0.8)]]),
    ":": (1, [[(0.5, 1), (0.5, 1.3)], [(0.5, 4), (0.5, 4.3)]]),
    ";": (1, [[(0.6, 1), (0.3, -0.5)], [(0.5, 4), (0.5, 4.3)]]),
    "!": (1, [[(0.5, 6), (0.5, 2)], [(0.5, 0), (0.5, 0.3)]]),
    "?": (4, [[(0, 5), (1, 6), (3, 6), (4, 5), (4, 4), (2, 2.5), (2, 1.8)], [(2, 0), (2, 0.3)]]),
    "-": (4, [[(0.5, 3), (3.5, 3)]]),
    "+": (4, [[(0.5, 3), (3.5, 3)], [(2, 1.5), (2, 4.5)]]),
    "=": (4, [[(0.5, 2), (3.5, 2)], [(0.5, 4), (3.5, 4)]]),
    "*": (4, [[(0.5, 1.5), (3.5, 4.5)], [(0.5, 4.5), (3.5, 1.5)], [(2, 1), (2, 5)]]),
    "/": (4, [[(0, 0), (4, 6)]]),
    "\\": (4, [[(0, 6), (4, 0)]]),
    "(": (2, [[(1.5, 6.5), (0.4, 5), (0.4, 1), (1.5, -0.5)]]),
    ")": (2, [[(0.5, 6.5), (1.6, 5), (1.6, 1), (0.5, -0.5)]]),
    "[": (2, [[(1.6, 6.5), (0.4, 6.5), (0.4, -0.5), (1.6, -0.5)]]),
    "]": (2, [[(0.4, 6.5), (1.6, 6.5), (1.6, -0.5), (0.4, -0.5)]]),
    "'": (1, [[(0.5, 6), (0.5, 4.5)]]),
    '"': (2, [[(0.4, 6), (0.4, 4.5)], [(1.6, 6), (1.6, 4.5)]]),
    "_": (4, [[(0, -0.5), (4, -0.5)]]),
    "%": (4, [[(0, 0), (4, 6)], [(0, 4.5), (0, 6), (1.5, 6), (1.5, 4.5), (0, 4.5)],
              [(2.5, 0), (2.5, 1.5), (4, 1.5), (4, 0), (2.5, 0)]]),
    "#": (4, [[(1, 0), (1.5, 6)], [(2.5, 0), (3, 6)], [(0, 2), (4, 2)], [(0, 4), (4, 4)]]),
    "<": (4, [[(4, 6), (0, 3), (4, 0)]]),
    ">": (4, [[(0, 6), (4, 3), (0, 0)]]),
    "^": (4, [[(0.5, 4), (2, 6), (3.5, 4)]]),
    "&": (4, [[(4, 0), (1, 3.5), (1, 5), (2, 6), (3, 5), (3, 4), (0, 1.5), (1, 0), (2, 0), (4, 2.5)]]),
    "@": (4, [[(3, 2), (3, 4), (1.5, 4), (1.5, 2), (3.3, 2), (4, 3), (4, 5), (3, 6), (1, 6),
               (0, 5), (0, 1), (1, 0), (3.5, 0)]]),
    "$": (4, [[(4, 5), (3, 6), (1, 6), (0, 5), (0, 4), (1, 3), (3, 3), (4, 2), (4, 1),
               (3, 0), (1, 0), (0, 1)], [(2, -0.5), (2, 6.5)]]),
    "|": (1, [[(0.5, -0.5), (0.5, 6.5)]]),
}

#: Accents for the Lithuanian letters, drawn on top of the base letter.
_ACCENTS = {
    "caron": [[(1, 8), (2, 7), (3, 8)]],                     # Č Š Ž
    "dot": [[(2, 7.3), (2, 7.6)]],                           # Ė
    "macron": [[(1, 7.5), (3, 7.5)]],                        # Ū
    "ogonek": [[(4, 0), (3.6, -0.8), (4.5, -1.1)]],           # Ą Ę Į Ų
}

#: Lithuanian and some other accented letters: (base letter, accent).
_LETTERS = {
    "Ą": ("A", "ogonek"), "Č": ("C", "caron"), "Ę": ("E", "ogonek"),
    "Ė": ("E", "dot"), "Į": ("I", "ogonek"), "Š": ("S", "caron"),
    "Ų": ("U", "ogonek"), "Ū": ("U", "macron"), "Ž": ("Z", "caron"),
    "Ä": ("A", "dot"), "Ö": ("O", "dot"), "Ü": ("U", "dot"),
    "Ā": ("A", "macron"), "Ē": ("E", "macron"), "Ī": ("I", "macron"),
    "Ō": ("O", "macron"), "Ň": ("N", "caron"), "Ř": ("R", "caron"),
    "Ě": ("E", "caron"), "Ď": ("D", "caron"), "Ť": ("T", "caron"),
}


def _strokes(ch):
    """``(advance width, [polyline, ...])`` for one character."""
    ch = ch.upper()
    if ch in _FONT:
        return _FONT[ch]
    if ch in _LETTERS:
        base, accent = _LETTERS[ch]
        width, lines = _FONT[base]
        extra = _ACCENTS[accent]
        if accent == "ogonek" and width < 4:      # hook under a narrow letter
            extra = [[(x - (4 - width), y) for x, y in line] for line in extra]
        return width, lines + extra
    return 4, [[(0, 0), (4, 0), (4, 6), (0, 6), (0, 0)]]   # unknown: a box


def text_width(string, size=1.0, spacing=1.0):
    """The width a line of :func:`text` will take up, in model units."""
    unit = size / 6.0
    total = 0.0
    for ch in string:
        w, _ = _strokes(ch)
        total += (w + 1.5 * spacing) * unit
    return max(0.0, total - 1.5 * spacing * unit)


def text(string, at=(0, 0, 0), size=1.0, thickness=None, color=None,
         u=(1, 0, 0), v=(0, 1, 0), align="left", spacing=1.0, k=8):
    """Write a label into the scene as round bars.

    ``size`` is the height of a capital letter, ``at`` the bottom-left
    corner of the text (or bottom-centre / bottom-right with ``align``).
    ``u`` is the writing direction and ``v`` the up direction, so a label
    can lie flat on the ground with ``u=[1, 0, 0], v=[0, 0, -1]`` or stand
    on a wall.  Letters, digits, punctuation and the Lithuanian letters
    ĄČĘĖĮŠŲŪŽ are available; lower-case letters are drawn as capitals.
    ``\\n`` starts a new line.  Returns the width of the widest line::

        add.text("LABAS 2026", [0, 0, 0], 1.0, color="navy")
    """
    if isinstance(at, dict):
        raise TypeError("text(string, font, ...) with loaded letters is now "
                        "typeset(string, font, ...)")
    unit = size / 6.0
    r = thickness if thickness is not None else 0.45 * unit
    u, v = _unit(u), _unit(v)
    lines = string.split("\n")
    widest = 0.0
    for row, line in enumerate(lines):
        width = text_width(line, size, spacing)
        widest = max(widest, width)
        if align == "center":
            start = -width / 2.0
        elif align == "right":
            start = -width
        else:
            start = 0.0
        y_off = -row * 1.6 * size
        x = start
        for ch in line:
            w, strokes = _strokes(ch)
            for line_pts in strokes:
                pts = []
                for (gx, gy) in line_pts:
                    px, py = x + gx * unit, y_off + gy * unit
                    pts.append((at[0] + u[0] * px + v[0] * py,
                                at[1] + u[1] * px + v[1] * py,
                                at[2] + u[2] * px + v[2] * py))
                for i in range(len(pts) - 1):
                    if distance(pts[i], pts[i + 1]) > EPS:
                        cylinder(pts[i], pts[i + 1], r, k, color)
                for p in pts:
                    sphere(p, r, 2, color)
            x += (w + 1.5 * spacing) * unit
    return widest


#: ``add.write`` is another name for :func:`text`.
write = text
#: ``add.label`` is another name for :func:`text`.
label = text


def glyph(letter, origin, u, v, size=1.0, thickness=0.04, color=None):
    """Draw one character as thin bars in the ``u``/``v`` plane
    (used by :func:`axes`; :func:`text` is the general version)."""
    text(letter, origin, size, thickness, color, u, v)


# ============================================================================
# 27. add.py 1.2 names
# ============================================================================
# Everything below exists so that models written for earlier versions of the
# course keep running unchanged.  New code should prefer the names on the
# right-hand side, which say what the shape is instead of numbering it.

def newface(A, RGB):
    """add.py 1.2 name for :func:`polygon`."""
    polygon(A, RGB)


def cube(c, e, RGB):
    """add.py 1.2 name for :func:`box`."""
    box(c, e, RGB)


def rectangle3D(c, e, RGB):
    """add.py 1.2 name for :func:`cuboid`."""
    cuboid(c, e, RGB)


def cube2(c, e, b, RGB):
    """add.py 1.2 name for :func:`frame` (a hollow cube of bars)."""
    frame(c, e, b, RGB)


def cylinder2(A, B, r, k, RGB):
    """add.py 1.2 name for :func:`tube` (a cylinder with no lids)."""
    tube(A, B, r, k, RGB)


def cylinder3(A, B, r, k, RGB):
    """add.py 1.2 name for :func:`cup` (a cylinder closed at ``A``)."""
    cup(A, B, r, k, RGB)


def cone2(A, B, r, k, RGB):
    """add.py 1.2 name for :func:`cone_open` (the slanted wall only)."""
    cone_open(A, B, r, k, RGB)


#: Other spelling of :func:`sphere`.
ball = sphere
#: Other spelling of :func:`cuboid`.
block = cuboid
#: Other spelling of :func:`cuboid`.
cuboid3D = cuboid
#: Other spelling of :func:`revolve`.
lathe = revolve
#: Other spelling of :func:`revolve`.
solid_of_revolution = revolve
#: Other spelling of :func:`clean`.
weld = clean
#: Other spelling of :func:`zoom`.
scale = zoom
#: Other spelling of :func:`move`.
translate = move
#: Other spelling of :func:`mirror`.
reflect = mirror


# ============================================================================
# 28. A one-line demonstration
# ============================================================================

def demo(path="demo.off"):
    """Build a small model that exercises most of the library.

    Run ``python add.py`` to produce ``demo.off`` and see the report.  The
    rainbow ring is painted with hundreds of shades; the save reduces them
    to 50 so that the same model would also upload to Sketchfab as .obj.
    """
    clear()
    axes([0, 0, 0], 3.0)

    # A block with a hole drilled through it, cut out with a boolean.
    cuboid([0, -1.2, 0], [4, 0.6, 4], "brown")
    plate = layer()
    cylinder([0, -2, 0], [0, 0, 0], 0.9, 32, "brown")
    drill = layer()
    mesh(difference(plate, drill))

    # A twisted, tapering star column: copy + rotate + stretch a cross-section.
    star = []
    for i in range(12):
        a = 2 * math.pi * i / 12
        r = 0.6 if i % 2 else 0.28
        star.append([math.cos(a) * r, math.sin(a) * r])
    extrude(star, [0, 3.2, 0], "gold", steps=60, twist=math.pi,
            scale=lambda t: 1.0 - 0.55 * t, center=(0, -0.9, 0))

    # A surface of revolution and a parametric surface.
    revolve(lambda t: [0.7 + 0.25 * math.sin(4 * t), t], [2.4, -0.9, 0],
            [2.4, 0.1, 0], 0, 2.6, 60, 40, "teal")

    def shell(u, v):
        return [(1.2 + 0.45 * math.cos(u)) * math.cos(v) - 2.6,
                0.45 * math.sin(u) + 0.6,
                (1.2 + 0.45 * math.cos(u)) * math.sin(v)]
    parametric(shell, 0, 2 * math.pi, 40, 0, 2 * math.pi, 80, "sky",
               wrap_u=True, wrap_v=True)

    # A rainbow of spheres on a ring.
    sphere([0, 0, 0], 0.22, 8, "white")
    bead = layer()
    mesh(color_by(array_radial(move(bead, [2.2, 1.9, 0]), 24),
                  lambda p: hsv(math.atan2(p[2], p[0]) / (2 * math.pi))))

    check()
    return save(path, colors=SKETCHFAB_COLORS)   # the .obj stays Sketchfab-ready


if __name__ == "__main__":
    print("add.py %s" % __version__)
    print("written to %s" % demo())


# ============================================================================
#  Public names
# ============================================================================

# The names that came in from ``math`` and ``random`` stay usable as
# ``add.sin`` and friends but are not part of add.py's own vocabulary.
_REEXPORTED = set(dir(math)) | set(dir(_random)) | {"math"}

__all__ = sorted(name for name, value in list(globals().items())
                 if not name.startswith("_")
                 and name not in _REEXPORTED
                 and (callable(value) or name in ("vertices", "faces",
                                                  "COLORS", "PALETTE", "EPS",
                                                  "DEFAULT_COLOR", "BOOL_EPS",
                                                  "SURFACES", "SKETCHFAB_MB",
                                                  "SKETCHFAB_COLORS")))

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

Compatibility
-------------
Code written for add.py 1.2 keeps working unchanged: the old names
(``cube2``, ``cylinder2``, ``cylinder3``, ``cone2``, ``rectangle3D``,
``spin3D``, ``curve``, ``off``, ``zoom`` ...) are all still here, and so are
the module-level ``add.vertices`` / ``add.faces`` string lists.

Coordinate convention
---------------------
Right-handed, Y up.  X is drawn red, Y green, Z blue (see ``axes``).
A face is *outward* when its vertices run counter-clockwise as seen from
outside the model.
"""

import math
import random

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
    """Return three unit vectors (u, v, w) with w along ``direction``."""
    w = _unit(direction)
    if _norm(w) < EPS:
        w = (0.0, 0.0, 1.0)
    u = _perp(w)
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
    """
    if color is None:
        return DEFAULT_COLOR
    if isinstance(color, str):
        s = color.strip().lower()
        if s in COLORS:
            return COLORS[s]
        s = s.lstrip("#")
        if len(s) == 3:
            s = s[0] * 2 + s[1] * 2 + s[2] * 2
        if len(s) == 6:
            return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))
        raise ValueError("unknown colour: %r" % color)
    r, g, b = color[0], color[1], color[2]
    if isinstance(r, float) and isinstance(g, float) and isinstance(b, float) \
            and max(r, g, b) <= 1.0:
        r, g, b = r * 255.0, g * 255.0, b * 255.0
    out = []
    for c in (r, g, b):
        c = int(round(c))
        out.append(0 if c < 0 else (255 if c > 255 else c))
    return (out[0], out[1], out[2])


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
    r = random if seed is None else random.Random(seed)
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

    __slots__ = ("V", "F", "C")

    def __init__(self, V=None, F=None, C=None):
        self.V = V if V is not None else []
        self.F = F if F is not None else []
        self.C = C if C is not None else []

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
                    list(self.C))

    def add_vertex(self, p):
        """Append a point and return its index."""
        self.V.append([float(p[0]), float(p[1]), float(p[2])])
        return len(self.V) - 1

    def add_face(self, indices, color=None):
        """Append one face given as a sequence of vertex indices."""
        self.F.append(list(indices))
        self.C.append(rgb(color))

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
        for f, c in zip(other.F, other.C):
            self.F.append([i + shift for i in f])
            self.C.append(c)
        return self

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
    This one helper is behind ``parametric``, ``revolve``, ``sweep``,
    ``loft``, ``sphere``, ``torus`` and ``tube``.
    """
    nu, nv = len(P), len(P[0])
    base = len(M.V)
    for row in P:
        for p in row:
            M.add_vertex(p)
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
            M.add_face(quad, color)


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


def _fan(M, points, apex, color, flip=False):
    """Close a ring of points with a triangle fan meeting at ``apex``."""
    base = len(M.V)
    for p in points:
        M.add_vertex(p)
    tip = M.add_vertex(apex)
    n = len(points)
    for i in range(n):
        j = (i + 1) % n
        tri = [base + i, base + j, tip] if not flip else [base + j, base + i, tip]
        M.add_face(tri, color)


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
    and has no hidden geometry.  :func:`frame` and :func:`voxels` are both
    three-line wrappers around this.
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

    color = rgb(color)
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                if not solid(i, j, k):
                    continue
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


def grid(center, size, nx=10, nz=10, color=None, height=None):
    """A flat (or, with ``height(x, z)``, a hilly) rectangular patch in XZ.

    ``size`` is ``[width_x, depth_z]``.  ``height`` is an optional function
    returning the Y coordinate::

        add.grid([0, 0, 0], [10, 10], 40, 40, "green",
                 height=lambda x, z: math.sin(x) * math.cos(z))
    """
    w, d = size[0], size[1]
    P = []
    for i in range(nx + 1):
        row = []
        x = center[0] - w / 2.0 + w * i / nx
        for j in range(nz + 1):
            z = center[2] - d / 2.0 + d * j / nz
            y = center[1]
            if height is not None:
                y = center[1] + height(x, z)
            row.append((x, y, z))
        P.append(row)
    M = Mesh()
    _add_grid(M, P, rgb(color), flip=True)
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


def polyhedron(name, center=(0, 0, 0), r=1.0, color=None):
    """One of the five Platonic solids, inscribed in a sphere of radius ``r``.

    ``name`` is ``"tetrahedron"``, ``"cube"``, ``"octahedron"``,
    ``"dodecahedron"`` or ``"icosahedron"``.
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


def _platonic(name):
    """Vertex and face tables for the five Platonic solids."""
    name = name.lower()
    if name in ("tetrahedron", "tetra"):
        V = [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]
        F = [[0, 1, 2], [0, 3, 1], [0, 2, 3], [1, 3, 2]]
        return V, F
    if name in ("cube", "hexahedron"):
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
        V = []
        for s1 in (-1, 1):
            for s2 in (-1, 1):
                V += [(0, s1 * 1.0, s2 * phi), (s1 * 1.0, s2 * phi, 0),
                      (s1 * phi, 0, s2 * 1.0)]
        F = _hull_faces(V, 3)
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
#  7. Round solids
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
            return [1 + 0.4 * math.sin(3 * t), t]
        add.revolve(vase, [0, 0, 0], [0, 1, 0], 0, 4, 60, 40, "teal")
    """
    pts = []
    for i in range(steps + 1):
        t = t0 + (t1 - t0) * i / float(steps)
        g = profile(t)
        pts.append((g[0], g[1]))
    direction = _sub(B, A)
    P, closed = _revolve_grid(A, direction, pts, k, angle)
    color = rgb(color)
    M = Mesh()
    _add_grid(M, P, color, wrap_v=closed, flip=True)
    if caps:
        w = _unit(direction)
        first = _add3(A, _scale(w, pts[0][1]))
        last = _add3(A, _scale(w, pts[-1][1]))
        if pts[0][0] > EPS:                       # flat lid at the start
            _fan(M, P[0], first, color, flip=True)
        if pts[-1][0] > EPS:                      # flat lid at the end
            _fan(M, P[-1], last, color)
        if not closed:                            # the two sides of the wedge
            M.add_polygon([row[0] for row in P] + [last, first], color)
            M.add_polygon([row[-1] for row in P] + [last, first], color)
        _weld(M, 1e-9)
        _drop_degenerate(M)
        if not closed:
            M = fix_normals(M)
    _emit(M)


def spin3D(A, B, S, min_t, max_t, grid_t, k, RGB):
    """add.py 1.2 lathe: spin curve ``S(t) = [radius, height]`` around A->B."""
    revolve(S, A, B, min_t, max_t, grid_t, k, RGB, caps=False)


def sphere(center, r, k=10, color=None):
    """A sphere built from six curved square patches (a "quad sphere").

    ``k`` is the number of cells along the side of each patch, so the sphere
    has ``6 * k * k`` faces.  The quads stay nearly square everywhere, which
    is why this looks better than a globe made of latitude/longitude strips.
    """
    ellipsoid(center, [r, r, r], k, color)


def ellipsoid(center, radii, k=10, color=None):
    """Like :func:`sphere` but with a separate radius for X, Y and Z."""
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
    length = _norm(d)
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
#  8. Coordinate axes
# ============================================================================

# Each capital letter is a few line segments in a unit square, so the axis
# labels cost five lines of code instead of a page of baked-in coordinates.
_GLYPHS = {
    "X": [((0, 0), (1, 1)), ((0, 1), (1, 0))],
    "Y": [((0, 1), (0.5, 0.5)), ((1, 1), (0.5, 0.5)), ((0.5, 0.5), (0.5, 0))],
    "Z": [((0, 1), (1, 1)), ((1, 1), (0, 0)), ((0, 0), (1, 0))],
}


def glyph(letter, origin, u, v, size=1.0, thickness=0.04, color=None):
    """Draw one of the letters X, Y, Z as thin bars in the ``u``/``v`` plane."""
    for (p, q) in _GLYPHS[letter.upper()]:
        a = (origin[0] + (u[0] * p[0] + v[0] * p[1]) * size,
             origin[1] + (u[1] * p[0] + v[1] * p[1]) * size,
             origin[2] + (u[2] * p[0] + v[2] * p[1]) * size)
        b = (origin[0] + (u[0] * q[0] + v[0] * q[1]) * size,
             origin[1] + (u[1] * q[0] + v[1] * q[1]) * size,
             origin[2] + (u[2] * q[0] + v[2] * q[1]) * size)
        cylinder(a, b, thickness, 6, color)


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
#  9. Parametric surfaces
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
    """
    color = rgb(RGB if RGB is not None else color)
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
    for f, c in zip(M.F, M.C):
        out.add_face(list(reversed(f)), c)
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
# 10. Curves, sweeps and lofts -- "copy, turn, stretch a cross-section"
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
    """
    n = steps if closed else steps + 1
    points = []
    for i in range(n):
        t = t0 + (t1 - t0) * i / float(steps)
        p = path(t)
        points.append((p[0], p[1], p[2]))
    tangents, normals = _rmf(points, closed)
    P = _sweep_profile(points, tangents, normals, profile, scale, twist)
    M = Mesh()
    _add_grid(M, P, rgb(color), wrap_u=closed, wrap_v=True, flip=True)
    if caps and not closed:
        M.add_polygon(P[0][::-1], color)
        M.add_polygon(P[-1], color)
        _weld(M, 1e-9)
        _make_outward(M, 0)
    _emit(M)


def curve(P, min_t, max_t, grid_t, k=16, r=0.1, RGB=None, isConnected=False,
          color=None):
    """Draw a 3D parametric curve as a round tube of radius ``r``.

    ``r`` may be a function ``r(t)`` for a tube that swells and narrows.
    ``isConnected=True`` closes the tube into a loop without a seam.
    """
    color = rgb(RGB if RGB is not None else color)
    n = grid_t if isConnected else grid_t + 1
    ts, points = [], []
    for i in range(n):
        t = min_t + (max_t - min_t) * i / float(grid_t)
        ts.append(t)
        p = P(t)
        points.append((p[0], p[1], p[2]))
    tangents, normals = _rmf(points, isConnected)
    circle_profile = [(math.cos(2 * math.pi * j / k), math.sin(2 * math.pi * j / k))
                      for j in range(k)]
    grid_points = []
    for i in range(len(points)):
        radius = r(ts[i]) if callable(r) else r
        u = normals[i]
        v = _cross(tangents[i], u)
        c = points[i]
        row = []
        for (cx, cy) in circle_profile:
            x, y = cx * radius, cy * radius
            row.append((c[0] + u[0] * x + v[0] * y,
                        c[1] + u[1] * x + v[1] * y,
                        c[2] + u[2] * x + v[2] * y))
        grid_points.append(row)
    M = Mesh()
    _add_grid(M, grid_points, color, wrap_u=isConnected, wrap_v=True, flip=True)
    if not isConnected:
        _fan(M, grid_points[0], points[0], color, flip=True)
        _fan(M, grid_points[-1], points[-1], color)
    _emit(M)


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
# 11. Measuring a mesh
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
# 12. Moving, turning and reshaping a mesh
# ============================================================================
# Every function here takes a mesh and returns a NEW mesh; the original is
# left alone.  That is what makes chains like
#     add.move(add.rotateY(M, a, [0, 0, 0]), [0, 3, 0])
# safe to write.

def _mapped(M, f, flip=False):
    """Apply point function ``f`` to a copy of the mesh."""
    M = as_mesh(M)
    out = Mesh([list(f(p)) for p in M.V],
               [list(reversed(x)) if flip else list(x) for x in M.F],
               list(M.C))
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
    r = random if seed is None else random.Random(seed)
    return _mapped(M, lambda p: (p[0] + r.uniform(-amount, amount),
                                 p[1] + r.uniform(-amount, amount),
                                 p[2] + r.uniform(-amount, amount)))


# ============================================================================
# 13. Colour
# ============================================================================

def color(M, RGB):
    """Paint the whole mesh one colour and return the painted copy."""
    M = as_mesh(M)
    c = rgb(RGB)
    return Mesh([list(p) for p in M.V], [list(f) for f in M.F],
                [c] * len(M.F))


#: Private handle on :func:`color`, for functions whose own parameter is
#: called ``color``.
_paint = color


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
    r = random if seed is None else random.Random(seed)
    M = as_mesh(M)
    out = M.copy()
    out.C = [(r.randint(0, 255), r.randint(0, 255), r.randint(0, 255))
             for _ in M.F]
    return out


# ============================================================================
# 14. Copies and patterns
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
# 15. Repairing a model
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


def _drop_degenerate(M, tol=1e-12):
    """Delete faces with no area and remove repeated corners (in place)."""
    F, C = [], []
    for f, c in zip(M.F, M.C):
        clean_f = []
        for i in f:                                  # drop repeated corners
            if not clean_f or clean_f[-1] != i:
                clean_f.append(i)
        if len(clean_f) > 1 and clean_f[0] == clean_f[-1]:
            clean_f.pop()
        if len(clean_f) < 3:
            continue
        if len(set(clean_f)) < 3:
            continue
        if _norm(_face_normal(M, clean_f)) <= tol:
            continue
        F.append(clean_f)
        C.append(c)
    removed = len(M.F) - len(F)
    M.F, M.C = F, C
    return removed


def _dedup_faces(M):
    """Delete repeats of a face that is already there (in place)."""
    seen = set()
    F, C = [], []
    for f, c in zip(M.F, M.C):
        key = tuple(sorted(f))
        if key in seen:
            continue
        seen.add(key)
        F.append(f)
        C.append(c)
    removed = len(M.F) - len(F)
    M.F, M.C = F, C
    return removed


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
    F = [f for i, f in enumerate(M.F) if i not in drop]
    C = [c for i, c in enumerate(M.C) if i not in drop]
    removed = len(M.F) - len(F)
    M.F, M.C = F, C
    return removed


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
    for f in M.F:
        n = len(f)
        out = []
        for i in range(n):
            a, b = f[i], f[(i + 1) % n]
            out.append(a)
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
                    last = v
        newF.append(out)
    M.F = newF
    return M


def triangulate(M=None):
    """Return a copy in which every face is a triangle (fan triangulation)."""
    M = as_mesh(M)
    out = Mesh([list(p) for p in M.V], [], [])
    for f, c in zip(M.F, M.C):
        for t in range(1, len(f) - 1):
            out.add_face([f[0], f[t], f[t + 1]], c)
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
                    visited[j] = True
                    component.append(j)
                    stack.append(j)
        if outward:
            part = Mesh(M.V, [M.F[i] for i in component],
                        [M.C[i] for i in component])
            if _signed_volume(part, 0) < 0:
                for i in component:
                    M.F[i].reverse()
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
# 16. Looking at a model
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
        "closed": open_edges == 0 and odd_edges == 0,
    }


def check(M=None, min_faces=10000, min_colors=3, quiet=False):
    """Print a health report and say whether the model meets the assignment.

    The course asks for at least 10000 polygons and at least 3 colours; this
    tells you where you stand and what still needs repairing::

        add.check()          # look at the current scene
    """
    s = stats(M)
    ok = s["faces"] >= min_faces and s["colors"] >= min_colors
    if not quiet:
        mark = lambda good: "OK " if good else "!! "
        print("-" * 56)
        print("  vertices            %d" % s["vertices"])
        print("%s polygons            %d  (need %d)"
              % (mark(s["faces"] >= min_faces), s["faces"], min_faces))
        print("%s colours             %d  (need %d)"
              % (mark(s["colors"] >= min_colors), s["colors"], min_colors))
        print("   size                %.3f x %.3f x %.3f" % tuple(s["size"]))
        print("   surface area        %.3f" % s["area"])
        if s["closed"]:
            why = "yes"
        elif s["open_edges"]:
            why = "no, %d edges have nothing on the other side" % s["open_edges"]
        else:
            why = "no, %d edges are shared by more than two faces" \
                % s["non_manifold_edges"]
        print("%s closed surface      %s" % (mark(s["closed"]), why))
        if s["duplicate_faces"]:
            print("!! repeated faces      %d   -- try add.clean()"
                  % s["duplicate_faces"])
        if s["back_to_back_faces"]:
            print("   back-to-back faces  %d   (fine for a two-sided sheet;"
                  " add.clean() removes them)" % s["back_to_back_faces"])
        if s["closed"]:
            print("   volume              %.3f" % s["volume"])
        print("-" * 56)
    return ok


# ============================================================================
# 17. Boolean operations: union, intersection, difference
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
    """Is point ``p`` inside the (closed) mesh?  Ray casting: odd = inside."""
    return _Solid(M).contains((p[0], p[1], p[2]))


# ============================================================================
# 18. Saving and loading
# ============================================================================

def save(path, M=None, clear_scene=None):
    """Write a model to disk; the file format follows the extension.

    ``.off`` (the course format), ``.obj`` (+ a ``.mtl`` colour file, which is
    what Sketchfab and most other tools want), ``.ply`` or ``.stl``::

        add.save("dragon.obj")

    Called without a mesh it saves -- and then empties -- the current scene,
    exactly like add.py 1.2's ``off()``.
    """
    if clear_scene is None:
        clear_scene = M is None
    mesh_to_save = as_mesh(M)
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


def _write_obj(path, M, mtl_path=None):
    if mtl_path is None:
        mtl_path = path[:-4] + ".mtl" if path.lower().endswith(".obj") \
            else path + ".mtl"
    mtl_name = mtl_path.replace("\\", "/").rsplit("/", 1)[-1]

    palette = []
    seen = {}
    for c in M.C:
        if c not in seen:
            seen[c] = "color_%02x%02x%02x" % c
            palette.append(c)

    with open(path, "w") as f:
        f.write("# written by add.py %s\n" % __version__)
        f.write("mtllib %s\n" % mtl_name)
        f.write("o model\n")
        out = []
        for p in M.V:
            out.append("v %s %s %s\n" % (_num(p[0]), _num(p[1]), _num(p[2])))
        f.write("".join(out))
        # Group faces by colour: one `usemtl` line per colour, not per face.
        by_color = {}
        for face, c in zip(M.F, M.C):
            by_color.setdefault(c, []).append(face)
        for c in palette:
            f.write("usemtl %s\n" % seen[c])
            out = []
            for face in by_color[c]:
                out.append("f %s\n" % " ".join(str(i + 1) for i in face))
            f.write("".join(out))

    with open(mtl_path, "w") as f:
        f.write("# written by add.py %s\n" % __version__)
        for c in palette:
            f.write("newmtl %s\n" % seen[c])
            f.write("Kd %.6f %.6f %.6f\n" % (c[0] / 255.0, c[1] / 255.0,
                                             c[2] / 255.0))
            f.write("Ka 0.100000 0.100000 0.100000\n")
            f.write("Ks 0.000000 0.000000 0.000000\n")
            f.write("d 1.0\nillum 1\n\n")
    return path


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
    with open(path, "r") as f:
        for line in f:
            parts = line.split()
            if not parts or parts[0].startswith("#"):
                continue
            tag = parts[0]
            if tag == "v":
                M.add_vertex((float(parts[1]), float(parts[2]),
                              float(parts[3])))
            elif tag == "f":
                face = []
                for p in parts[1:]:
                    idx = int(p.split("/")[0])
                    face.append(idx - 1 if idx > 0 else len(M.V) + idx)
                M.add_face(face, current)
            elif tag == "mtllib" and color is None:
                try:
                    materials.update(_read_mtl(folder + parts[1]))
                except IOError:
                    pass
            elif tag == "usemtl" and color is None:
                current = materials.get(parts[1], DEFAULT_COLOR)
    return M


def _read_mtl(path):
    out = {}
    name = None
    with open(path, "r") as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue
            if parts[0] == "newmtl":
                name = parts[1]
            elif parts[0] == "Kd" and name:
                out[name] = rgb([float(parts[1]) * 255, float(parts[2]) * 255,
                                 float(parts[3]) * 255])
    return out


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


def text(characters, font, at=(0, 0, 0), size=1.0, spacing=1.0, color=None,
         plane=((1, 0, 0), (0, 1, 0))):
    """Lay a string of already-loaded glyphs out in a row and merge them.

    ``font`` is the dictionary returned by :func:`load_font`.
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
# 19. add.py 1.2 names
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


#: Other spellings people reach for.
ball = sphere
block = cuboid
cuboid3D = cuboid
lathe = revolve
solid_of_revolution = revolve
weld = clean
scale = zoom
translate = move
reflect = mirror


# ============================================================================
# 20. A one-line demonstration
# ============================================================================

def demo(path="demo.off"):
    """Build a small model that exercises most of the library.

    Run ``python add.py`` to produce ``demo.off`` and see the report.
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
    return save(path)


if __name__ == "__main__":
    print("add.py %s" % __version__)
    print("written to %s" % demo())


# ============================================================================
#  Public names
# ============================================================================

__all__ = sorted(name for name, value in list(globals().items())
                 if not name.startswith("_")
                 and name not in ("math", "random")
                 and (callable(value) or name in ("vertices", "faces",
                                                  "COLORS", "EPS",
                                                  "DEFAULT_COLOR",
                                                  "BOOL_EPS")))

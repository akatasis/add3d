import contextlib
import io
import math
import random

from parity_case import add, case, record, run, save_as, save_case, save_mesh  # noqa: F401


# -- helpers (the C++ twin has the same ones) ---------------------------------

def save_file(ext, M):
    """add.save(<case>.<ext>, M): the model tidied by clean(M, tol=1e-6) and written."""
    save_as(ext, M)


def raises(fn):
    try:
        fn()
    except Exception:                                   # noqa: BLE001
        return True
    return False


def capture(fn):
    """What fn prints (and what it returns)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        value = fn()
    return buf.getvalue(), value


def face_str(f):
    return " ".join(str(i) for i in f)


def dump(M):
    """Every number of a mesh, at full precision."""
    record("V %d" % len(M.V))
    for p in M.V:
        record(p)
    record("F %d" % len(M.F))
    for f, c in zip(M.F, M.C):
        record(face_str(f))
        record(c)
    if M.UV is None:
        record("no uv")
    else:
        for t in M.UV:
            if t is None:
                record("none")
            else:
                record(t)


def record_report(info):
    record("removed %d vertices, %d faces; cut %d; split %d" % (
        info["vertices_removed"], info["faces_removed"], info["faces_cut"], info["faces_split"]))


def record_polys(polys):
    record(len(polys))
    for p in polys:
        record(p)


def cuboid(M, c, s, color=None):
    """A box as 8 shared corners and 6 outward quads."""
    x0, y0, z0 = c[0] - s[0] / 2.0, c[1] - s[1] / 2.0, c[2] - s[2] / 2.0
    x1, y1, z1 = c[0] + s[0] / 2.0, c[1] + s[1] / 2.0, c[2] + s[2] / 2.0
    base = len(M.V)
    for p in ([x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
              [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]):
        M.add_vertex(p)
    for f in ([0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [2, 3, 7, 6], [1, 2, 6, 5], [0, 4, 7, 3]):
        M.add_face([base + i for i in f], color)


def cuboid_polys(M, c, s, color=None):
    """A box as 6 separate quads (24 corners: clean() has to weld them)."""
    x0, y0, z0 = c[0] - s[0] / 2.0, c[1] - s[1] / 2.0, c[2] - s[2] / 2.0
    x1, y1, z1 = c[0] + s[0] / 2.0, c[1] + s[1] / 2.0, c[2] + s[2] / 2.0
    P = [[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
         [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]]
    for f in ([0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [2, 3, 7, 6], [1, 2, 6, 5], [0, 4, 7, 3]):
        M.add_polygon([P[i] for i in f], color)


def textured_cuboid(M, c, s, color):
    """A box whose every face carries texture coordinates."""
    x0, y0, z0 = c[0] - s[0] / 2.0, c[1] - s[1] / 2.0, c[2] - s[2] / 2.0
    x1, y1, z1 = c[0] + s[0] / 2.0, c[1] + s[1] / 2.0, c[2] + s[2] / 2.0
    base = len(M.V)
    for p in ([x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
              [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]):
        M.add_vertex(p)
    uv = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    for f in ([0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [2, 3, 7, 6], [1, 2, 6, 5], [0, 4, 7, 3]):
        M.add_face([base + i for i in f], color, uv)


def quad_xz(M, x0, z0, x1, z1, y, up=True, color=None):
    """A flat rectangle at height y, facing up (+Y) or down."""
    pts = [[x0, y, z0], [x0, y, z1], [x1, y, z1], [x1, y, z0]]
    if not up:
        pts.reverse()
    M.add_polygon(pts, color)


def quad_xy(M, x0, y0, x1, y1, z, front=True, color=None):
    """A flat rectangle at depth z, facing +Z (front) or -Z."""
    pts = [[x0, y0, z], [x1, y0, z], [x1, y1, z], [x0, y1, z]]
    if not front:
        pts.reverse()
    M.add_polygon(pts, color)


def turned(M, ax, ay):
    """A copy turned by ax around X, then by ay around Y (through the origin)."""
    out = add.Mesh([], [list(f) for f in M.F], list(M.C),
                   None if M.UV is None else [None if t is None else list(t) for t in M.UV])
    ca, sa = math.cos(ax), math.sin(ax)
    cb, sb = math.cos(ay), math.sin(ay)
    for p in M.V:
        x, y, z = p[0], p[1] * ca - p[2] * sa, p[1] * sa + p[2] * ca
        out.V.append([x * cb + z * sb, y, z * cb - x * sb])
    return out


def l_shape(M, c, color=None, z=0.0):
    x, y = c[0], c[1]
    M.add_polygon([[x, y, z], [x + 2, y, z], [x + 2, y + 1, z], [x + 1, y + 1, z],
                   [x + 1, y + 2, z], [x, y + 2, z]], color)


def star_points(cx, cy, n, r1, r2, z=0.0, phase=0.0):
    pts = []
    for i in range(2 * n):
        a = phase + math.pi * i / n
        r = r1 if i % 2 == 0 else r2
        pts.append([cx + r * math.cos(a), cy + r * math.sin(a), z])
    return pts


def grid_of_quads(M, n, m, colors):
    """n x m unit quads in the XZ plane sharing their corners, facing up."""
    base = len(M.V)
    for i in range(n + 1):
        for j in range(m + 1):
            M.add_vertex([i * 1.0, 0.0, j * 1.0])
    for i in range(n):
        for j in range(m):
            a = base + i * (m + 1) + j
            M.add_face([a, a + 1, a + m + 2, a + m + 1], colors[(i + j) % len(colors)])


# -- the helpers already written (wave 0) --------------------------------------

@case
def cell_keys():
    tol = 1e-7
    for p in ([0.0, 0.0, 0.0], [1e-7, 2.4e-8, -2.6e-8], [0.12345678, -3.00000004, 7.5e-8],
              [5e-8, 5.00001e-8, 4.99999e-8], [-1.23e-7, 1.77e-7, 123.456]):
        keys = add._cell_keys(p, tol)
        record(" / ".join("%d %d %d" % k for k in keys))
    record(raises(lambda: add._cell_keys([float("nan"), 0.0, 0.0], tol)))
    record(raises(lambda: add._cell_keys([0.0, float("inf"), 0.0], tol)))


@case
def weld_near():
    M = add.Mesh()
    M.add_polygon([[0, 0, 0], [1, 0, 0], [1, 1, 0]], "red")
    M.add_polygon([[1 + 4e-8, 1e-8, 0], [0, -3e-8, 5e-8], [1, 0, 1]], "blue")
    M.add_polygon([[1.00000009, 0.99999991, 0], [1, 1, 1], [1, 0, 1 + 2e-7]])
    M.add_polygon([[0.5, 0.5, 0.5], [0.5 + 0.9e-7, 0.5, 0.5], [0.5, 0.5 - 1.2e-7, 0.5]])
    record(add._weld(M, 1e-7))
    dump(M)
    N = add.Mesh()
    N.add_polygon([[0, 0, 0], [1, 0, 0], [0.9999, 0, 0]])
    record(add._weld(N, 1e-3))
    dump(N)
    B = add.Mesh()
    B.add_polygon([[float("nan"), 0, 0], [1, 0, 0], [0, 1, 0]])
    record(raises(lambda: add._weld(B, 1e-7)))


@case
def keep_faces_uv():
    M = add.Mesh()
    M.add_polygon([[0, 0, 0], [1, 0, 0], [1, 1, 0]], "red")
    M.add_face([0, 1, 2], "blue", [(0, 0), (1, 0), (1, 1)])
    M.add_face([2, 1, 0], "green")
    M.add_face([0, 2, 1], "white", [(0.5, 0.25), (0.75, 0), (1, 1)])
    record(add._keep_faces(M, [3, 1, 2]))
    dump(M)
    N = add.Mesh()
    N.add_polygon([[0, 0, 0], [1, 0, 0], [1, 1, 0]], "red")
    N.add_polygon([[0, 0, 1], [1, 0, 1], [1, 1, 1]], "blue")
    record(add._keep_faces(N, [1]))
    dump(N)


@case
def not_finite():
    M = add.Mesh()
    M.add_polygon([[0, 0, 0], [1, 0, 0], [1, 1, 0]], "red")
    M.add_polygon([[0, 0, 1], [float("nan"), 0, 1], [1, 1, 1]], "blue")
    M.add_polygon([[0, 0, 2], [1, float("inf"), 2], [1, 1, 2], [0, 1, float("-inf")]], "green")
    M.add_polygon([[0, 0, 3], [1, 0, 3], [1, 1, 3]], "white")
    M.add_vertex([float("nan"), float("nan"), 0])
    record(face_str(sorted(add._not_finite(M))))
    record(add._drop_not_finite(M))
    dump(M)
    N = add.Mesh()
    N.add_polygon([[1e308, 1e308, 1e308], [1e308, 0, 0], [0, 1e308, 0]])
    record(face_str(sorted(add._not_finite(N))))
    record(add._drop_not_finite(N))
    record(len(N.F))


@case
def split_repeats():
    for f, uv in (([0, 1, 2, 0, 3, 4], None),
                  ([0, 1, 1, 2, 3, 3, 0], None),
                  ([5, 6, 7, 5, 8, 9, 7, 10], [(i * 0.5, 1.0 - i * 0.25) for i in range(8)]),
                  ([1, 2, 3, 4], [(0, 0), (1, 0), (1, 1), (0, 1)]),
                  ([1, 2, 1, 2], None),
                  ([3, 3, 3], [(0, 0), (1, 1), (2, 2)])):
        pieces = add._split_repeats(f, uv)
        record(len(pieces))
        for pf, puv in pieces:
            record(face_str(pf))
            if puv is None:
                record("none")
            else:
                record(puv)


@case
def drop_degenerate():
    M = add.Mesh()
    for i in range(12):
        M.add_vertex([math.cos(i * 0.5), math.sin(i * 0.5), 0.1 * i])
    M.add_vertex([0, 0, 0])
    M.add_vertex([1, 1, 1])
    M.add_vertex([2, 2, 2])
    M.add_face([0, 1, 2], "red")
    M.add_face([0, 1, 1, 2, 2], "blue")                    # repeated corners
    M.add_face([0, 1, 2, 0, 3, 4, 5], "green")             # pinched at 0
    M.add_face([12, 13, 14], "white")                      # a straight line: no area
    M.add_face([3, 4], "yellow")                           # too short
    M.add_face([6, 7, 8, 7], "cyan")                       # back and forth
    M.add_face([9, 10, 11, 9, 9], "magenta")
    M.add_face([], "orange")
    M.add_face([1, 2, 3, 4, 1, 5, 6, 7, 5, 8], "purple")    # pinched twice
    record(add._drop_degenerate(M))
    dump(M)
    T = add.Mesh()
    for i in range(8):
        T.add_vertex([math.cos(i * 0.8), math.sin(i * 0.8), 0.0])
    T.add_face([0, 1, 2, 3], "red", [(0, 0), (1, 0), (1, 1), (0, 1)])
    T.add_face([0, 1, 2, 0, 4, 5], "blue", [(0, 0), (1, 0), (1, 1), (0.5, 0.5), (0, 1), (0.25, 0.75)])
    T.add_face([4, 5, 5, 6], "green")
    T.add_face([6, 7, 7, 0], "white", [(0.1, 0.2), (0.3, 0.4), (0.5, 0.6), (0.7, 0.8)])
    record(add._drop_degenerate(T, 1e-9))
    dump(T)


@case
def dedup_faces():
    M = add.Mesh()
    cuboid(M, [0, 0, 0], [1, 1, 1], "red")
    M.add_face([3, 2, 1, 0], "blue")                        # the bottom, turned round
    M.add_face([2, 1, 0, 3], "green")                       # the bottom again, rotated
    M.add_face([4, 5, 6, 7], "white")
    M.add_face([4, 5, 6], "white")
    record(add._dedup_faces(M))
    dump(M)


@case
def drop_internal():
    M = add.Mesh()
    cuboid(M, [0, 0, 0], [1, 1, 1], "red")
    cuboid(M, [1, 0, 0], [1, 1, 1], "blue")
    add._weld(M)
    record(add._drop_internal(M))
    dump(M)
    N = add.Mesh()
    for p in ([0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]):
        N.add_vertex(p)
    N.add_face([0, 1, 2, 3], "red")
    N.add_face([3, 2, 1, 0], "blue")
    N.add_face([1, 2, 3, 0], "green")
    N.add_face([0, 3, 2, 1], "white")
    N.add_face([2, 3, 0, 1], "yellow")
    N.add_face([0, 1, 2], "cyan")
    record(add._drop_internal(N))
    dump(N)
    E = add.Mesh()
    E.add_polygon([[0, 0, 0], [1, 0, 0], [1, 1, 0]])
    record(add._drop_internal(E))
    E.add_face([], "red")
    E.add_face([], "blue")
    record(raises(lambda: add._drop_internal(E)))


@case
def winding():
    for f in ([0, 1, 2], [2, 1, 0], [5, 3, 9, 4], [4, 9, 3, 5], [7], [3, 1, 1, 2], [1, 3, 1, 0, 2]):
        record(add._winding(f))
    record(raises(lambda: add._winding([])))


@case
def drop_unused():
    M = add.Mesh()
    for i in range(10):
        M.add_vertex([i * 1.0, i * i * 0.5, -i * 1.0])
    M.add_face([7, 2, 9], "red")
    M.add_face([2, 4, 7, 5], "blue")
    record(add._drop_unused(M))
    dump(M)
    record(add._drop_unused(M))


@case
def poly_area2():
    for pts in ([(0, 0), (1, 0), (1, 1), (0, 1)],
                [(0, 0), (0, 1), (1, 1), (1, 0)],
                [(0.1, 0.2), (3.3, -0.7), (2.25, 4.125), (-1.5, 2.0), (0.0, 1.0)],
                [(1, 1), (2, 2)], [(5, 5)], []):
        record(add._poly_area2(pts))


# -- the 2D pieces of the overlap machinery -----------------------------------

@case
def clip_half():
    sq = [(0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)]
    tri = [(0.0, 0.0), (3.0, 0.5), (1.0, 2.5)]
    for pts in (sq, tri):
        for a, b in (((1.0, -1.0), (1.0, 3.0)), ((0.0, 0.5), (4.0, 1.5)), ((-1.0, 1.0), (3.0, 1.0)),
                     ((5.0, 0.0), (5.0, 1.0)), ((0.0, 0.0), (2.0, 2.0)), ((2.0, 0.0), (2.0, 2.0))):
            for keep_left in (True, False):
                record(add._clip_half(pts, a, b, keep_left))
    record(add._clip_half([], (0.0, 0.0), (1.0, 0.0), True))


@case
def convex_minus():
    A = [(0.0, 0.0), (4.0, 0.0), (4.0, 3.0), (0.0, 3.0)]
    Bs = [[(1.0, 1.0), (2.0, 1.0), (2.0, 2.0), (1.0, 2.0)],            # inside A
          [(3.0, 1.0), (5.0, 1.0), (5.0, 2.0), (3.0, 2.0)],            # over one side
          [(4.0, 0.0), (6.0, 0.0), (6.0, 3.0), (4.0, 3.0)],            # touching along a side
          [(7.0, 0.0), (8.0, 0.0), (8.0, 1.0)],                        # far away
          [(-1.0, -1.0), (5.0, -1.0), (5.0, 4.0), (-1.0, 4.0)],        # covering all of A
          [(2.0, -1.0), (5.0, 1.5), (2.0, 4.0)],                       # a triangle across
          [(0.0, 0.0), (4.0, 0.0), (4.0, 3.0), (0.0, 3.0)],            # A itself
          [(1.0, 1.0), (1.0 + 1e-6, 1.0), (1.0, 1.0 + 1e-6)]]          # a speck
    for B in Bs:
        for eps in (1e-9, 1e-3):
            pieces = add._convex_minus(A, B, eps)
            record(len(pieces) == 1 and pieces[0] is A)
            record_polys(pieces)


@case
def ears():
    L = [(0.0, 0.0), (2.0, 0.0), (2.0, 1.0), (1.0, 1.0), (1.0, 2.0), (0.0, 2.0)]
    star = [(p[0], p[1]) for p in star_points(0.0, 0.0, 5, 2.0, 0.8)]
    comb = [(0.0, 0.0), (5.0, 0.0), (5.0, 2.0), (4.0, 2.0), (4.0, 1.0), (3.0, 1.0), (3.0, 2.0),
            (2.0, 2.0), (2.0, 1.0), (1.0, 1.0), (1.0, 2.0), (0.0, 2.0)]
    square = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    straight = [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0), (2.0, 1.0), (0.0, 1.0)]
    bowtie = [(0.0, 0.0), (2.0, 2.0), (2.0, 0.0), (0.0, 2.0)]
    for pts in (L, star, comb, square, straight, bowtie, square[:3]):
        record_polys(add._ears(pts))
        record_polys(add._convex_pieces(pts))
        tris = add._ear_triangles(pts)
        if tris is None:
            record("none")
        else:
            record(" / ".join(face_str(t) for t in tris))


@case
def is_concave():
    M = add.Mesh()
    l_shape(M, [0, 0], "red")
    M.add_polygon(star_points(5.0, 0.0, 6, 2.0, 1.0), "blue")
    M.add_polygon([[0, 0, 5], [1, 0, 5], [1, 1, 5], [0, 1, 5]], "green")
    M.add_polygon([[0, 0, 6], [0, 1, 6], [1, 1, 6], [1, 0, 6]], "white")
    M.add_polygon([[0, 0, 7], [1, 0, 7], [2, 0, 7], [2, 1, 7], [0, 1, 7]], "yellow")
    M.add_polygon([[0, 0, 8], [2, 2, 8], [2, 0, 8], [0, 2, 8]], "cyan")
    M.add_polygon([[0, 0, 9], [1, 0, 9], [2, 0, 9], [3, 0, 9]], "magenta")
    M.add_polygon([[0, 0, 10], [1, 0, 10], [1, 1, 10]], "orange")
    M.add_polygon([[0, 0, 11], [2, 0, 11], [2, 2, 11], [1.0, 1.0 - 1e-12, 11], [0, 2, 11]], "pink")
    for f in M.F:
        record(add._is_concave(M, f))
    record(add._is_concave(M, M.F[0], (0.0, 0.0, -1.0)))
    record(add._is_concave(M, M.F[2], (0.0, 0.0, -1.0)))
    record(add._is_concave(M, M.F[0], (0.0, 0.0, 0.0)))
    record(add.concave_faces(M))
    T = turned(M, 0.7, -1.9)
    record(add.concave_faces(T))
    add.mesh(M)
    record(add.concave_faces())


@case
def split_concave():
    M = add.Mesh()
    l_shape(M, [0, 0], "red")
    M.add_polygon(star_points(5.0, 0.0, 5, 2.0, 0.7), "blue")
    M.add_polygon([[0, 0, 5], [1, 0, 5], [1, 1, 5], [0, 1, 5]], "green")
    pts = [[0, 0, 6], [5, 0, 6], [5, 2, 6], [4, 2, 6], [4, 1, 6], [3, 1, 6], [3, 2, 6],
           [2, 2, 6], [2, 1, 6], [1, 1, 6], [1, 2, 6], [0, 2, 6]]
    M.add_polygon(pts[::-1], "white")                       # a comb, clockwise
    M.add_polygon([[0, 0, 8], [2, 2, 8], [2, 0, 8], [0, 2, 8]], "cyan")    # crosses itself: no ears
    M.add_polygon([[0, 0, 9], [3, 0, 9], [3, 3, 9], [2, 3, 9], [2, 1, 9], [1, 1, 9], [1, 3, 9], [0, 3, 9]],
                  "yellow")
    T = turned(M, 0.3, 2.2)
    record(add._split_concave(T))
    dump(T)
    U = add.Mesh()
    for p in ([0, 0, 0], [2, 0, 0], [2, 1, 0], [1, 1, 0], [1, 2, 0], [0, 2, 0]):
        U.add_vertex(p)
    U.add_face([0, 1, 2, 3, 4, 5], "red", [(0, 0), (1, 0), (1, 0.5), (0.5, 0.5), (0.5, 1), (0, 1)])
    U.add_face([5, 4, 3, 2, 1, 0], "blue")
    U.add_face([0, 1, 2], "green", [(0, 0), (1, 0), (1, 1)])
    record(add._split_concave(U))
    dump(U)
    record(add._split_concave(U))


# -- the overlap machinery ----------------------------------------------------

def overlap_scene():
    """Faces in a few planes, overlapping every which way."""
    M = add.Mesh()
    quad_xz(M, 0, 0, 4, 4, 0.0, True, "red")               # a floor ...
    quad_xz(M, 1, 1, 2, 2, 0.0, True, "blue")              # ... a tile lying on it
    quad_xz(M, 3, 3, 5, 5, 0.0, True, "green")             # ... one sticking out
    quad_xz(M, 1, 2.5, 3, 3.5, 0.0, False, "white")        # ... the bottom of something standing on it
    quad_xz(M, 6, 0, 7, 1, 0.0, True, "yellow")            # ... one on its own
    quad_xy(M, 0, 0, 3, 3, 1.0, True, "cyan")               # a wall
    quad_xy(M, 1, 1, 2, 2, 1.0, True, "magenta")            # a picture on it
    quad_xy(M, 2.5, 0, 4, 1, 1.0004, False, "orange")       # nearly in its plane, facing away
    l_shape(M, [10, 0], "pink", 2.0)                        # an L ...
    quad_xy(M, 10.5, 0.5, 12.5, 2.5, 2.0, True, "purple")   # ... and a square across its notch
    return M


@case
def overlap_groups():
    M = overlap_scene()
    groups = add._overlap_groups(M, 1e-3)
    record(len(groups))
    for key, (u, v, n, polys) in groups.items():
        record(list(key))
        record(u)
        record(v)
        record(n)
        for area, i, pts, bb, flipped in polys:
            record(area)
            record(i)
            record(pts)
            record(list(bb))
            record(flipped)
    T = turned(M, 0.4, 0.9)
    groups = add._overlap_groups(T, 1e-3)
    record(len(groups))
    for key, (u, v, n, polys) in groups.items():
        record(list(key))
        record(n)
        record(face_str([p[1] for p in polys]))


@case
def plane_keys():
    """Normals with a component that rounds to -0.0 or 0.0: one plane, the first key kept."""
    M = add.Mesh()
    M.add_polygon([[0, 0, 0], [0, 0, 1], [1, 0.0004, 1], [1, 0.0004, 0]], "red")          # n ~ (-0.0004, 1, 0)
    M.add_polygon([[0.5, 0.0003, 0], [0.5, 0.0003, 1], [1.5, 0.0002, 1], [1.5, 0.0002, 0]], "blue")
    M.add_polygon([[0, 0, 0.2], [0.9, 0.0002, 0.2], [0.9, 0.0002, 0.8], [0, 0, 0.8]], "green")     # facing down
    M.add_polygon([[0, 0.0000004, 3], [0, 0.0000004, 4], [1, 0.0000004, 4], [1, 0.0000004, 3]], "white")
    M.add_polygon([[0.2, -0.0000004, 3.2], [0.2, -0.0000004, 3.8], [0.8, -0.0000004, 3.8],
                   [0.8, -0.0000004, 3.2]], "yellow")
    groups = add._overlap_groups(M, 1e-3)
    for key, (u, v, n, polys) in groups.items():
        record(list(key))
        record(u)
        record(v)
        record(n)
        record(face_str([p[1] for p in polys]))
    count, replaced = add._overlap_scan(M, 1e-3, True)
    record(count)
    for i, (pieces, u, v, n, d, flipped) in replaced.items():
        record(i)
        record_polys(pieces)
        record(d)
    C = add.clean(M)
    dump(C)


@case
def convex_overlap2():
    A = [(0.0, 0.0), (4.0, 0.0), (4.0, 3.0), (0.0, 3.0)]
    for B in ([(1.0, 1.0), (2.0, 1.0), (2.0, 2.0), (1.0, 2.0)],
              [(3.0, 1.0), (5.0, 1.0), (5.0, 2.0), (3.0, 2.0)],
              [(4.0, 0.0), (6.0, 0.0), (6.0, 3.0), (4.0, 3.0)],
              [(2.0, -1.0), (5.0, 1.5), (2.0, 4.0)]):
        record(add._convex_overlap2(A, B))
        record(add._convex_overlap2(B, A))


@case
def minus_all():
    A = [[(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]]
    holes = []
    for i in range(5):
        for j in range(5):
            x, y = 0.5 + 2 * i, 0.5 + 2 * j
            holes.append([(x, y), (x + 1, y), (x + 1, y + 1), (x, y + 1)])
    for n in (1, 2, 3, 6, 25):
        rest = add._minus_all(A, holes[:n], 1e-9)
        if rest is None:
            record("none")
        else:
            record_polys(rest)
    rest = add._minus_all(A, holes, 1e-9, 1000)
    record(len(rest))
    record(add._minus_all(A, [], 1e-9) == A)


def record_scan(M, tol, cut):
    count, replaced = add._overlap_scan(M, tol, cut)
    record(count)
    record(len(replaced))
    for i, (pieces, u, v, n, d, flipped) in replaced.items():
        record(i)
        record_polys(pieces)
        record(u)
        record(v)
        record(n)
        record(d)
        record(flipped)


@case
def overlap_scan():
    M = overlap_scene()
    record_scan(M, 1e-3, False)
    record_scan(M, 1e-3, True)
    record_scan(M, 1e-5, True)
    record_scan(turned(M, -0.6, 2.5), 1e-3, True)


@case
def cut_overlaps():
    M = overlap_scene()
    record(add._cut_overlaps(M))
    dump(M)
    N = turned(overlap_scene(), 1.1, 0.35)
    record(add._cut_overlaps(N, 1e-3))
    dump(N)


@case
def cut_overlaps_uv():
    M = add.Mesh()
    wood = (255, 255, 255, 1.0, "wood.png")
    for p in ([0, 0, 0], [4, 0, 0], [4, 3, 0], [0, 3, 0], [3, 1, 0], [6, 1, 0], [6, 2, 0], [3, 2, 0]):
        M.add_vertex(p)
    M.add_face([0, 1, 2, 3], wood, [(0, 0), (1, 0), (1, 1), (0, 1)])
    M.add_face([4, 5, 6, 7], wood, [(0.1, 0.2), (0.9, 0.2), (0.9, 0.7), (0.1, 0.7)])
    M.add_face([7, 6, 5, 4], "red")
    M.add_polygon([[1, 1, 0], [1.5, 1, 0], [1.5, 1.5, 0]], "blue")
    record(add._cut_overlaps(M))
    dump(M)
    T = turned(M, 0.5, 0.25)
    C = add.clean(T)
    dump(C)
    save_file("obj", T)


@case
def overlaps_count():
    M = overlap_scene()
    record(add.overlaps(M))
    record(add.overlaps(M, 1e-6))
    record(add.overlaps(M, 0.1))
    record(add.overlaps(add.Mesh()))
    add.mesh(M)
    record(add.overlaps())
    B = add.Mesh()
    B.add_polygon([[float("nan"), 0, 0], [1, 0, 0], [1, 1, 0]])
    B.add_polygon([[0, 0, 0], [1, 0, 0], [1, 1, 0]])
    record(raises(lambda: add.overlaps(B)))
    record(raises(lambda: add.overlaps(M, 0.0)))


# -- shattering: a face that would fall into more than 64 pieces is left whole ---

@case
def shatter_strip():
    M = add.Mesh()
    quad_xz(M, 0, 0, 100, 0.1, 0.0, True, "red")               # a strip (area 10) ...
    for i in range(70):                                       # ... under 70 bars (area 15 each)
        x = 0.7 + i * 1.4
        quad_xz(M, x, -15, x + 0.5, 15, 0.0, True, "blue")
    quad_xz(M, 0.8, -15.25, 1.1, -14.75, 0.0, True, "green")  # and a tile across a bar's end
    record_scan(M, 1e-3, False)
    record_scan(M, 1e-3, True)
    info_M = add.clean(M, report=True)
    record_report(info_M[1])
    save_mesh(info_M[0], "clean")


@case
def shatter_floor():
    M = add.Mesh()
    cuboid(M, [50, -0.5, 5], [100, 1, 10], "grey")           # a slab, top at y = 0
    for i in range(70):                                       # 70 boxes standing on it
        cuboid(M, [1 + (i % 35) * 2.8, 0.5, 2.5 + (i // 35) * 5], [1, 1, 1], "red")
    record(add.overlaps(M))
    info_M = add.clean(M, report=True)
    record_report(info_M[1])
    save_file("off", M)


@case
def big_floor():
    """A floor so much bigger than the tiles that it is checked against everyone."""
    M = add.Mesh()
    quad_xz(M, 0, 0, 20, 20, 0.0, True, "grey")
    for i in range(30):
        x, z = (i * 7) % 20 + 0.25, (i * 3) % 20 + 0.25
        quad_xz(M, x, z, x + 0.5, z + 0.5, 0.0, i % 3 != 0, "red" if i % 2 else "blue")
    quad_xz(M, 19.75, 5, 20.25, 5.5, 0.0, True, "green")
    quad_xz(M, -0.25, -0.25, 0.25, 0.25, 0.0, False, "white")
    record_scan(M, 1e-3, True)
    info_M = add.clean(M, report=True)
    record_report(info_M[1])
    dump(info_M[0])


# -- heal: T-junctions ---------------------------------------------------------

@case
def heal_t_junctions():
    M = add.Mesh()
    for p in ([0, 0, 0], [2, 0, 0], [2, 1, 0], [0, 1, 0], [1, 1, 0], [2, 2, 0], [0, 2, 0],
              [0.5, 1, 0], [1.5, 1.0000000001, 0], [2.0, 0.5, 0], [3, 0, 0], [3, 1, 0]):
        M.add_vertex(p)
    M.add_face([0, 1, 2, 3], "red")                          # its top edge has 3 vertices on it
    M.add_face([3, 7, 4, 6], "blue")
    M.add_face([4, 8, 2, 5, 6], "green")
    M.add_face([1, 10, 11, 2], "white")                      # its left edge passes 9
    M.add_face([9, 10, 1], "yellow")
    H = add.heal(M)
    dump(H)
    dump(add.heal(M, 1e-12))
    dump(add.heal(M, 0.01))
    add.mesh(M)
    dump(add.heal())
    record(len(add.scene().F[0]))


@case
def heal_uv():
    M = add.Mesh()
    for p in ([0, 0, 0], [4, 0, 0], [4, 2, 0], [0, 2, 0], [1, 2, 0], [3, 2, 0], [2, 2, 0], [2, 3, 0]):
        M.add_vertex(p)
    M.add_face([0, 1, 2, 3], "red", [(0, 0), (1, 0), (1, 0.5), (0, 0.5)])
    M.add_face([3, 4, 7], "blue")
    M.add_face([4, 6, 7], "blue", [(0.2, 0.2), (0.4, 0.2), (0.3, 0.9)])
    M.add_face([6, 5, 7], "green")
    M.add_face([5, 2, 7], "green", [(0.6, 0.1), (0.8, 0.1), (0.7, 0.3)])
    dump(add.heal(M))


@case
def heal_long_edge():
    """Many short edges and a long diagonal one: walk along it."""
    M = add.Mesh()
    a = M.add_vertex([0, 0, 0])
    b = M.add_vertex([6, 6, 6])
    c = M.add_vertex([6, 0, 0])
    M.add_face([a, b, c], "red")
    for i in range(1, 30):
        t = i / 5.0
        p = M.add_vertex([t, t, t])
        q = M.add_vertex([t + 0.05, t, t - 0.05])
        r = M.add_vertex([t, t + 0.05, t + 0.02])
        M.add_face([p, q, r], "blue")
    M.add_vertex([3.0000000001, 3, 3])
    M.add_face([len(M.V) - 1, 4, 5], "green")
    H = add.heal(M)
    record(face_str(H.F[0]))
    dump(H)


@case
def heal_edge_cases():
    record(len(add.heal(add.Mesh()).F))
    M = add.Mesh()
    M.add_vertex([0, 0, 0])
    record(len(add.heal(M).V))
    N = add.Mesh()
    N.add_polygon([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    N.add_face([0, 1], "red")
    dump(add.heal(N))
    record(raises(lambda: add.heal(N, 0.0)))
    B = add.Mesh()
    B.add_polygon([[float("nan"), 0, 0], [1, 0, 0], [1, 1, 0]])
    record(raises(lambda: add.heal(B)))
    I = add.Mesh()
    I.add_polygon([[0, 0, 0], [1e308, 0, 0], [0, 1e308, 0]])
    record(raises(lambda: add.heal(I)))


# -- triangulate, fix_normals ---------------------------------------------------

@case
def triangulate():
    M = add.Mesh()
    l_shape(M, [0, 0], "red")
    M.add_polygon([[0, 0, 1], [1, 0, 1], [1, 1, 1]], "blue")
    M.add_face([0, 1], "green")
    M.add_face([], "green")
    M.add_face([6, 7, 8, 2], add.transparent("sky", 0.3), [(0, 0), (1, 0), (1, 1), (0, 1)])
    T = add.triangulate(M)
    dump(T)
    N = add.Mesh()
    cuboid(N, [0, 0, 0], [1, 2, 3], "red")
    dump(add.triangulate(N))
    add.mesh(N)
    record(len(add.triangulate().F))


@case
def fix_normals():
    M = add.Mesh()
    cuboid(M, [0, 0, 0], [1, 1, 1], "red")
    M.F[1].reverse()
    M.F[4].reverse()
    cuboid(M, [3, 0, 0], [1, 2, 1], "blue")
    for f in M.F[6:]:
        f.reverse()                                        # an inside-out box
    M.add_polygon([[0, 5, 0], [1, 5, 0], [1, 5, 1]], "green")    # a loose triangle
    dump(add.fix_normals(M))
    dump(add.fix_normals(M, False))
    add.mesh(M)
    dump(add.fix_normals())
    O = add.Mesh()
    for p in ([0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [2, 0, 0], [2, 1, 0], [0, 2, 0], [1, 2, 0]):
        O.add_vertex(p)
    O.add_face([0, 1, 2, 3], "red", [(0, 0), (1, 0), (1, 1), (0, 1)])
    O.add_face([1, 2, 5, 4], "blue", [(0, 0), (0, 1), (1, 1), (1, 0)])
    O.add_face([3, 2, 7, 6], "green")
    O.add_face([2, 3, 6], "white")                          # a third face on edge 2-3
    dump(add.fix_normals(O))


# -- clean --------------------------------------------------------------------

@case
def clean_boxes():
    M = add.Mesh()
    cuboid_polys(M, [0, 0, 0], [1, 1, 1], "red")
    cuboid_polys(M, [1, 0, 0], [1, 1, 1], "red")              # sharing a wall
    cuboid_polys(M, [0.5, 1, 0], [1, 1, 1], "blue")           # standing across both
    cuboid(M, [0, 0, 0], [1, 1, 1], "red")                   # the first one again
    C, info = add.clean(M, report=True)
    record_report(info)
    dump(C)
    save_file("off", M)


@case
def clean_flags():
    M = add.Mesh()
    cuboid_polys(M, [0, 0, 0], [1, 1, 1], "red")
    cuboid_polys(M, [1, 0.25, 0], [1, 0.5, 0.5], "blue")
    M.add_polygon([[0, 3, 0], [1, 3, 0], [2, 3, 0]], "green")
    M.add_polygon([[0, 4, 0], [2, 4, 0], [2, 5, 0], [1, 5, 0], [1, 6, 0], [0, 6, 0]], "white")
    M.add_face([0, 1, 2, 3], "red")
    M.add_face([3, 2, 1, 0], "yellow")
    M.add_vertex([9, 9, 9])
    M.add_polygon([[5, 0, 0], [6, 0, 0], [float("nan"), 1, 0]], "cyan")
    for flags in ({}, {"weld": False}, {"degenerate": False}, {"duplicates": False}, {"internal": False},
                  {"unused": False}, {"normals": True}, {"overlaps": False}, {"convex": False},
                  {"tol": 0.3}, {"weld": False, "overlaps": True, "convex": True}):
        C, info = add.clean(M, report=True, **flags)
        record(" ".join(sorted(flags)))
        record_report(info)
        dump(C)
    record(len(add.clean(M).F))


@case
def clean_scene():
    cuboid_polys(add.scene(), [0, 0, 0], [2, 1, 2], "red")
    cuboid_polys(add.scene(), [0, 1, 0], [1, 1, 1], "blue")
    C = add.clean()
    dump(C)
    record(len(add.scene().F))
    save_case()


@case
def clean_tower():
    """Boxes stacked on each other (contacts) and side by side (walls)."""
    M = add.Mesh()
    for i in range(4):
        cuboid(M, [0, i + 0.5, 0], [2.0 - i * 0.4, 1, 2.0 - i * 0.4], add.hsv(i / 4.0))
    cuboid(M, [1.5, 0.5, 0], [1, 1, 1], "red")
    cuboid(M, [0, 0.5, 1.4], [0.8, 1, 0.8], add.transparent("sky", 0.4))
    C, info = add.clean(M, tol=1e-6, report=True)
    record_report(info)
    dump(C)
    save_file("obj", M)
    save_file("off", M)


@case
def clean_turned():
    M = add.Mesh()
    cuboid(M, [0, 0.5, 0], [2, 1, 2], "red")
    cuboid(M, [0.3, 1.5, 0.2], [1, 1, 1], "blue")
    cuboid(M, [1.5, 0.25, 0], [1, 0.5, 1], "green")
    T = turned(M, 0.35, 1.2)
    C, info = add.clean(T, report=True)
    record_report(info)
    dump(C)
    save_file("off", T)


@case
def clean_textured():
    M = add.Mesh()
    textured_cuboid(M, [0, 0.5, 0], [2, 1, 2], (255, 255, 255, 1.0, "bricks.png"))
    textured_cuboid(M, [0.5, 1.5, 0.5], [1, 1, 1], (200, 180, 160, 1.0, "wood.jpg"))
    textured_cuboid(M, [1.5, 0.5, 0], [1, 1, 1], (255, 255, 255, 0.5, "glass.png"))
    C, info = add.clean(M, report=True)
    record_report(info)
    dump(C)
    save_file("obj", M)


# -- random scenes: boxes and tiles on a half-unit grid (lots of shared planes) --

def random_scene(seed, n, kind):
    r = random.Random(seed)
    colors = ["red", "green", "blue", "white", add.transparent("sky", 0.5)]
    M = add.Mesh()
    if kind == "floor":
        cuboid(M, [0, -0.5, 0], [8, 1, 8], "grey")
    for i in range(n):
        x = r.randint(-6, 6) * 0.5
        z = r.randint(-6, 6) * 0.5
        sx = r.randint(1, 4) * 0.5
        sz = r.randint(1, 4) * 0.5
        c = r.choice(colors)
        if kind == "tiles":
            y = r.randint(0, 1) * 0.5
            up = r.random() < 0.7
            quad_xz(M, x, z, x + sx, z + sz, y, up, c)
        else:
            sy = r.randint(1, 3) * 0.5
            y = r.randint(0, 2) * 0.5 if kind != "floor" else 0.0
            if r.random() < 0.5:
                cuboid(M, [x, y + sy / 2.0, z], [sx, sy, sz], c)
            else:
                cuboid_polys(M, [x, y + sy / 2.0, z], [sx, sy, sz], c)
    if kind == "turned":
        M = turned(M, r.uniform(-1, 1), r.uniform(-3, 3))
    return M


def random_case(seed, n, kind):
    M = random_scene(seed, n, kind)
    C, info = add.clean(M, report=True)
    record_report(info)
    record(add.overlaps(M))
    record(add.overlaps(C))
    record(add.concave_faces(C))
    save_mesh(C, "clean")
    save_file("obj", M)


@case
def random_boxes_1():
    random_case(1, 12, "boxes")


@case
def random_boxes_2():
    random_case(2, 25, "boxes")


@case
def random_boxes_3():
    random_case(3, 40, "boxes")


@case
def random_floor_1():
    random_case(11, 15, "floor")


@case
def random_floor_2():
    random_case(12, 30, "floor")


@case
def random_tiles_1():
    random_case(21, 20, "tiles")


@case
def random_tiles_2():
    random_case(22, 50, "tiles")


@case
def random_turned_1():
    random_case(31, 15, "turned")


@case
def random_turned_2():
    random_case(32, 30, "turned")


# -- stats and check -----------------------------------------------------------

def record_stats(s):
    record("vertices %d faces %d triangles %d colors %d" % (s["vertices"], s["faces"], s["triangles"],
                                                            s["colors"]))
    record(s["bbox"][0])
    record(s["bbox"][1])
    record(s["size"])
    record(s["area"])
    record(s["volume"])
    record("open %d non-manifold %d dup-vertices %d dup-faces %d back-to-back %d" % (
        s["open_edges"], s["non_manifold_edges"], s["duplicate_vertices"], s["duplicate_faces"],
        s["back_to_back_faces"]))
    record(s["closed"])
    record(s["obj_bytes"])
    record(s["transparent_faces"])
    record(len(s["textures"]))
    for t in s["textures"]:
        record(t)


def messy():
    """A model with a bit of everything check() complains about."""
    M = add.Mesh()
    cuboid(M, [0, 0, 0], [1, 1, 1], "red")
    cuboid(M, [3, 0, 0], [1, 1, 1], (255, 255, 255, 1.0, "tiles/floor.png"))
    M.add_face([0, 3, 2, 1], "red")                          # repeated
    M.add_face([1, 2, 3, 0], "blue")                         # back to back
    M.add_face([0, 1, 9], "green")                           # a third face on edge 0-1
    M.add_vertex([0.5, 0.5, 0.5])
    M.add_vertex([0.5, 0.5, 0.5000000001])
    M.add_polygon([[0, 3, 0], [2, 3, 0], [2, 4, 0], [1, 4, 0], [1, 5, 0], [0, 5, 0]],
                  add.transparent("sky", 0.25))
    M.add_polygon([[0.2, 3.2, 0], [0.8, 3.2, 0], [0.8, 3.8, 0]], (255, 255, 255, 1.0, "a.png"))
    return M


@case
def stats():
    M = messy()
    record_stats(add.stats(M))
    N = add.Mesh()
    cuboid(N, [0, 0, 0], [1, 2, 3], "red")
    record_stats(add.stats(N))
    record_stats(add.stats(add.Mesh()))
    add.mesh(N)
    record_stats(add.stats())
    S = add.Mesh()
    for p in ([0, 0, 0], [-0.0, 1, 0], [0.0000001, 1, 0], [1, 1, 1], [1, 1, 1.0000004], [2, 2, 2]):
        S.add_vertex(p)
    S.add_face([0, 1, 3], "red")
    S.add_face([2, 4, 5], "red")
    S.add_face([0, 1, 3], "red")
    S.add_face([3, 1, 0], "red")
    S.add_face([1, 3, 0], "red")
    record_stats(add.stats(S))
    B = add.Mesh()
    B.add_polygon([[float("nan"), 0, 0], [1, 0, 0], [1, 1, 0]])
    record(raises(lambda: add.stats(B)))
    E = add.Mesh()
    E.add_polygon([[0, 0, 0], [1, 0, 0], [1, 1, 0]])
    E.add_face([], "red")
    E.add_face([], "blue")
    record(raises(lambda: add.stats(E)))


def record_check(fn):
    text, ok = capture(fn)
    record(text)
    record(ok)


@case
def format_numbers():
    """How check() writes numbers: Python's "%.3f", "%.1f" and "%d" of a float."""
    for x in (float("nan"), -float("nan"), float("inf"), -float("inf"), 0.0, -0.0, -0.0004, 0.0005, 0.0015,
              2.5e-4, 0.05, 0.25, 1.25, 2.5, -2.5, 49.99, 1e20, -123.4565, 5e-324, 1e300):
        record("%.3f" % x)
        record("%.1f" % x)
        try:
            record("%d" % x)
        except Exception:                           # noqa: BLE001
            record("raised")


@case
def check_messy():
    M = messy()
    record_check(lambda: add.check(M))
    record_check(lambda: add.check(M, 10, 2))
    record_check(lambda: add.check(M, 10, 2, True))
    record_check(lambda: add.check(M, 5, 1, False, 0.0001, 3))
    record_check(lambda: add.check(M, 5, 1, False, 2.5, 3))
    B = add.Mesh()
    B.add_polygon([[float("nan"), 0, 0], [1, 0, 0], [1, 1, 0]])
    record(raises(lambda: capture(lambda: add.check(B))))


@case
def check_closed():
    M = add.Mesh()
    cuboid(M, [0, 0, 0], [1, 2, 3], "red")
    cuboid(M, [0, 0, 5], [1, 1, 1], "green")
    cuboid(M, [0, 0, 8], [1, 1, 1], "blue")
    record_check(lambda: add.check(M))
    record_check(lambda: add.check(M, 18))
    add.mesh(M)
    record_check(lambda: add.check())
    record_check(lambda: add.check(add.Mesh()))


@case
def check_passes():
    M = add.Mesh()
    grid_of_quads(M, 100, 100, ["red", "green", "blue"])
    record_check(lambda: add.check(M))
    record_check(lambda: add.check(M, 10000, 3, False, 1e-6))
    record_check(lambda: add.check(M, 10001))
    record_stats(add.stats(M))


@case
def check_overlaps():
    M = overlap_scene()
    record_check(lambda: add.check(M, 1, 1))


# -- saving goes through clean() ------------------------------------------------

@case
def save_messy():
    M = messy()
    save_file("off", M)
    save_file("obj", M)


@case
def save_overlaps():
    M = overlap_scene()
    save_file("off", M)
    save_file("obj", turned(M, 0.2, 0.1))


if __name__ == "__main__":
    import sys
    run(sys.argv)

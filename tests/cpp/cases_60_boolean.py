"""Parity cases for _src/60_boolean.py: union, difference, intersect,
symmetric_difference and their aliases, cut and inside -- and the machinery
under them: _Poly, _split, _BoxGrid (whose set order decides which plane
cuts first), _RayIndex, _Solid, _split_against, _keep_pieces, _loops (see
cases_60_boolean.cpp)."""
import math

from parity_case import _current, add, case, record, run, save_case, save_mesh  # noqa: F401


def ints(xs):
    return " ".join("%d" % i for i in xs)


def pt(p):
    return [float(p[0]), float(p[1]), float(p[2])]


def bits(xs):
    return "".join("1" if x else "0" for x in xs)


def maybe(x):
    """True / False / None as a word."""
    return "None" if x is None else ("True" if x else "False")


def dump(M):
    """Every vertex, face and colour of a mesh, exactly."""
    record(len(M.V))
    for p in M.V:
        record(pt(p))
    record(len(M.F))
    for f, c in zip(M.F, M.C):
        record(ints(f))
        record(c)


def keep(M, tag):
    """The mesh to <case>_<tag>.off, and exactly into <case>.txt."""
    record(tag)
    dump(M)
    save_mesh(M, tag)


def make_box(c, e, color=None):
    return add.make(add.box, c, e, color)


def make_cuboid(c, s, color=None):
    return add.make(add.cuboid, c, s, color)


def make_sphere(c, r, k=10, color=None):
    return add.make(add.sphere, c, r, k, color)


def make_cylinder(a, b, r, k=24, color=None):
    return add.make(add.cylinder, a, b, r, k, color)


def make_cone(a, b, r, k=24, color=None):
    return add.make(add.cone, a, b, r, k, color)


def make_torus(c, R, r, nu=48, nv=24, color=None, axis=(0, 1, 0)):
    return add.make(add.torus, c, R, r, nu, nv, color, axis)


def make_poly(name, c, r, color=None):
    return add.make(add.polyhedron, name, c, r, color)


def all_three(A, B, tag=""):
    keep(add.union(A, B), tag + "union")
    keep(add.difference(A, B), tag + "diff_ab")
    keep(add.difference(B, A), tag + "diff_ba")
    keep(add.intersect(A, B), tag + "inter")


# ---------------------------------------------------------------------------
#  Boxes
# ---------------------------------------------------------------------------

@case
def b_box_overlap():
    A = make_cuboid([0, 0, 0], [2, 2, 2], "red")
    B = make_cuboid([1, 0.5, 0.25], [2, 2, 2], "blue")
    all_three(A, B)
    all_three(make_box([0.3, -0.2, 0.1], 1.5, "gold"), make_box([-0.4, 0.35, 0.6], 1.1, "teal"), "b_")


@case
def b_box_touching():
    A = make_box([0, 0, 0], 2, "red")
    all_three(A, make_box([2, 0, 0], 2, "blue"))                # a whole face shared
    all_three(A, make_box([2, 0.5, 0.5], 2, "green"), "part_")  # part of a face shared
    all_three(A, make_box([2, 2, 0], 2, "navy"), "edge_")       # only an edge
    all_three(A, make_box([2, 2, 2], 2, "pink"), "corner_")     # only a corner


@case
def b_coplanar():
    A = make_cuboid([0, 0, 0], [2, 1, 2], "red")
    B = make_cuboid([1, 0, 0.5], [2, 1, 1], "blue")  # top and bottom flush with A's
    all_three(A, B)
    all_three(A, make_cuboid([0.5, 0.25, 0], [1, 0.5, 3], "green"), "top_")  # only the top flush
    all_three(A, A, "same_")                                                 # the very same box
    all_three(A, add.mirror(A, [0, 0, 0], [1, 0, 0]), "mirror_")             # mirrored: its corners in another order


@case
def b_nested():
    big = make_box([0, 0, 0], 3, "red")
    small = make_cuboid([0.2, -0.1, 0.3], [1, 1.2, 0.8], "blue")
    all_three(big, small)
    all_three(big, make_cuboid([0, 0, 0], [3, 1, 1], "green"), "flush_")  # inside, touching two faces


@case
def b_disjoint():
    A = make_box([0, 0, 0], 1, "red")
    B = make_box([3, 0.5, 0], 1, "blue")
    all_three(A, B)
    keep(add.union([A, B, make_box([0, 3, 0], 1, "green")]), "three")


# ---------------------------------------------------------------------------
#  Several solids, curved solids
# ---------------------------------------------------------------------------

@case
def b_union_many():
    parts = [make_box([0, 0, 0], 1, "red"), make_box([0.7, 0.3, 0.2], 1, "green"), make_box([1.4, 0.6, 0.4], 1, "blue"),
             make_sphere([2.1, 0.9, 0.6], 0.6, 6, "gold")]
    keep(add.union(parts), "chain")
    keep(add.union(parts[:1]), "one")
    balls = [make_sphere([0, 0, 0], 1, 6, "red"), make_sphere([0.9, 0.2, 0.1], 0.8, 6, "white"),
             make_sphere([0.4, 0.8, -0.3], 0.7, 6, "sky")]
    keep(add.union(balls), "balls")
    keep(add.union([balls[0], make_box([5, 0, 0], 1), balls[1]]), "gap")


@case
def b_voxels():
    """Touching unit cubes, as a student stacks them: shared faces, edges and corners."""
    cells = [(0, 0, 0), (1, 0, 0), (2, 0, 0), (1, 1, 0), (1, 1, 1), (0, 0, 1), (2, 1, 1)]
    cubes = [make_box(list(c), 1, add.hsv(i / 7.0)) for i, c in enumerate(cells)]
    keep(add.union(cubes), "union")
    keep(add.difference(make_cuboid([1, 0.5, 0.5], [3, 2, 2], "white"), cubes[::2]), "carved")
    keep(add.intersect(add.union(cubes[:4]), make_cuboid([1, 0.25, 0], [2, 1, 1], "red")), "trimmed")


@case
def b_turned():
    """A solid and a turned copy of itself: faces that are flush up to rounding."""
    A = make_cuboid([0.1, 0, -0.05], [1.2, 0.8, 1.6], "red")
    for q in (1, 2, 4):
        B = add.rotate(A, [0, 1, 0], q * math.pi / 4)
        keep(add.union(A, B), "u%d" % q)
        keep(add.difference(A, B), "d%d" % q)
        keep(add.intersect(A, B), "i%d" % q)
    S = add.make(add.prism, add.profile_star(5, 0.8, 0.4), 1, "teal")
    for k in (1, 2):
        T = add.rotate(S, [0, 1, 0], k * math.pi / 5)
        keep(add.union(S, T), "star_u%d" % k)
        keep(add.difference(S, T), "star_d%d" % k)


@case
def b_intersect_many():
    a = make_cuboid([0, 0, 0], [3, 1, 1], "red")
    b = make_cuboid([0, 0, 0], [1, 3, 1], "green")
    c = make_cuboid([0, 0, 0], [1, 1, 3], "blue")
    keep(add.intersect([a, b, c]), "cross")
    keep(add.intersect([make_sphere([0, 0, 0], 1, 6, "red"), make_box([0.5, 0.5, 0.5], 1.2, "blue"),
                        make_cylinder([0, -2, 0], [0, 2, 0], 0.6, 12, "green")]), "round")
    keep(add.intersect([a, make_box([5, 0, 0], 1), c]), "gap")
    keep(add.intersect([a]), "one")


@case
def b_symmetric():
    keep(add.symmetric_difference(make_box([0, 0, 0], 2, "red"), make_box([1, 0.5, 0.25], 2, "blue")), "boxes")
    keep(add.symmetric_difference(make_sphere([0, 0, 0], 1, 6, "white"), make_box([0.8, 0, 0], 1.2, "black")), "ball")
    keep(add.symmetric_difference(make_box([0, 0, 0], 1), make_box([3, 0, 0], 1)), "apart")


@case
def b_drill():
    add.cuboid([0, -1.2, 0], [4, 0.6, 4], "brown")
    plate = add.layer()
    add.cylinder([0, -2, 0], [0, 0, 0], 0.9, 32, "brown")
    drill = add.layer()
    add.mesh(add.difference(plate, drill))
    save_case()
    add.cuboid([0, 0, 0], [4, 1, 4], "brown")
    plate = add.layer()
    add.cylinder([0, -1, 0], [0, 1, 0], 0.6, 32, "brown")
    drill = add.layer()
    keep(add.difference(plate, drill), "doc")
    keep(add.difference(plate, drill, color="black"), "painted")


@case
def b_curved():
    B = make_box([0, 0, 0], 1.5, "red")
    S = make_sphere([0.3, 0.2, 0.1], 1, 6, "white")
    all_three(B, S)
    C = make_cylinder([-1, -1, -0.5], [1, 1, 0.5], 0.4, 16, "blue")
    all_three(make_sphere([0, 0, 0], 1, 6, "gold"), C, "tilt_")
    T = make_torus([0, 0, 0], 1.0, 0.35, 16, 8, "teal")
    keep(add.difference(T, make_box([1, 0, 0], 0.8, "red")), "torus_bite")
    keep(add.intersect(T, make_cuboid([0, 0, 0], [3, 0.3, 3], "red")), "torus_slab")
    K = make_cone([0, -1, 0], [0, 1, 0], 1, 12, "green")
    H = make_cylinder([-2, 0, 0], [2, 0, 0], 0.3, 12)
    keep(add.difference(K, H), "cone_drill")
    keep(add.union(make_cylinder([0, -1, 0], [0, 1, 0], 0.5, 12, "red"),
                   make_cylinder([-1, 0, 0], [1, 0, 0], 0.5, 12, "blue")), "pipes")


@case
def b_paint():
    plate = make_cuboid([0, 0, 0], [4, 1, 4], "brown")
    drills = [make_cylinder([x, -1, 0], [x, 1, 0], 0.4, 12, "red") for x in (-1.2, 0, 1.2)]
    keep(add.difference(plate, drills), "own")
    keep(add.difference(plate, drills, color="black"), "black")
    keep(add.difference(plate, drills, color=add.transparent("sky", 0.4)), "clear")
    keep(add.difference(plate, drills[0], drills[2], color=(10, 20, 30)), "two")
    keep(add.difference(plate, [], color="black"), "none")


@case
def b_colors():
    T = add.texture(make_box([0, 0, 0], 1, "white"), "wood.png")
    G = add.opacity(make_sphere([0.5, 0.3, 0.2], 0.6, 6, "sky"), 0.5)
    keep(add.union(T, G), "union")
    keep(add.difference(T, G), "diff")
    keep(add.difference(G, T, color=add.transparent("red", 0.25)), "diff_painted")
    keep(add.intersect(G, T), "inter")
    add.obj(_current[0] + "_apart.obj", add.union(T, add.move(G, [5, 0, 0])))   # (merged: the texture kept)
    add.obj(_current[0] + "_first.obj", add.union(add.Mesh(), T))
    try:
        add._csg(T, G, "xor")
    except ValueError:
        record("raised")


@case
def b_aliases():
    a = make_box([0, 0, 0], 1, "red")
    b = make_box([0.5, 0.25, 0], 1, "blue")
    c = make_box([-0.3, 0.4, 0.2], 1, "green")
    keep(add.add_solids(a, b), "add2")
    keep(add.add_solids([a, b, c]), "add3")
    keep(add.subtract(a, b), "sub2")
    keep(add.subtract(a, [b, c]), "sub3")
    keep(add.common(a, b), "common2")
    keep(add.common([a, b, c]), "common3")


@case
def b_empty():
    a = make_box([0, 0, 0], 1, "red")
    E = add.Mesh()
    keep(add.union([]), "u_none")
    keep(add.union([E]), "u_empty")
    keep(add.union([E, a]), "u_ea")
    keep(add.union([a, E]), "u_ae")
    keep(add.difference(E, a), "d_ea")
    keep(add.difference(a, E), "d_ae")
    keep(add.intersect([]), "i_none")
    keep(add.intersect([E, a]), "i_ea")
    keep(add.intersect([a, E]), "i_ae")
    keep(add.difference(a, a), "d_aa")
    keep(add.difference(a, make_box([0, 0, 0], 2)), "d_swallowed")
    keep(add.intersect(a, make_box([0.25, 0.25, 0.25], 0.5, "blue")), "i_inner")
    V = add.Mesh()                                            # faces without area, and one of two corners
    for p in ([0, 0, 0], [1, 0, 0], [2, 0, 0], [0.5, 0.5, 0.5]):
        V.add_vertex(p)
    V.add_face([0, 1, 2], "blue")
    V.add_face([0, 3], "green")
    keep(add.union(a, V), "u_flat")                            # (add.py: A is lost -- see the report)
    keep(add.difference(a, V), "d_flat")
    keep(add.intersect(a, V), "i_flat")
    keep(add.union(V, a), "u_flat2")


# ---------------------------------------------------------------------------
#  cut
# ---------------------------------------------------------------------------

@case
def b_cut_box():
    B = make_box([0, 0, 0], 2, "red")
    keep(add.cut(B), "default")
    keep(add.cut(B, [0, 0.5, 0], [0, 1, 0], False), "open")
    keep(add.cut(B, [0, 0, 0], [1, 1, 0], True, "blue"), "diagonal")
    keep(add.cut(B, [0.2, 0.1, -0.3], [1, 2, 3]), "slant")
    keep(add.cut(B, [0, 1, 0], [0, 1, 0]), "on_top")          # the plane of the top face
    keep(add.cut(B, [0, -1, 0], [0, 1, 0]), "on_bottom")
    keep(add.cut(B, [0, 5, 0], [0, 1, 0]), "all_behind")
    keep(add.cut(B, [0, -5, 0], [0, 1, 0]), "all_front")
    keep(add.cut(B, [0, 0, 0], [0, -1, 0], True, add.transparent("gold", 0.5)), "upside")
    keep(add.cut(B, [1, 1, 1], [1, 1, 1]), "corner")
    keep(add.cut(B, [0, 0, 0], [0, 0, 0]), "no_normal")
    add.box([0, 0, 0], 1, "green")
    keep(add.cut(add.scene(), [0, 0.1, 0], [0, 1, 0]), "scene")
    save_case()
    odd = make_box([0, 0, 0], 1, "red")                       # faces of two and of one corner
    odd.add_face([0, 7], "blue")
    odd.add_face([3], "green")
    odd.add_polygon([[0.5, 0.2, -0.3], [-0.2, -0.4, 0.1]], "gold")
    keep(add.cut(odd, [0.1, 0, 0], [1, 0.3, 0]), "odd")
    odd.add_face([], "blue")                                  # a face of no corners: add.py fails
    try:
        add.cut(odd)
    except IndexError:
        record("raised")


@case
def b_cut_curved():
    S = make_sphere([0, 0, 0], 1, 10, "white")
    for i, n in enumerate(([0, 1, 0], [1, 1, 0], [0.3, -0.5, 0.8], [-1, 0.2, 0.1])):
        keep(add.cut(S, [0.1 * i, -0.2, 0.05], n, True, "red"), "sphere%d" % i)
    T = make_torus([0, 0, 0], 1.0, 0.35, 16, 8, "teal")
    keep(add.cut(T), "torus_flat")                            # two rings: two caps
    keep(add.cut(T, [0, 0, 0], [1, 0, 0]), "torus_upright")   # two round cross-sections
    keep(add.cut(T, [0.2, 0.1, 0], [1, 2, 0.5], True, "black"), "torus_slant")
    C = make_cylinder([0, -1, 0], [0, 1, 0], 0.5, 16, "blue")
    keep(add.cut(C, [0, 0.2, 0], [0.4, 1, 0.3]), "cyl_slant")
    keep(add.cut(C, [0, 0, 0], [1, 0, 0], False), "cyl_half_open")
    keep(add.cut(add.cut(C, [0, 0.5, 0], [0, 1, 0]), [0, -0.5, 0], [0, -1, 0]), "slab")
    keep(add.cut(make_cone([0, 0, 0], [0, 2, 0], 1, 12, "gold"), [0, 1, 0], [1, 1, 0]), "cone")
    keep(add.cut(add.make(add.tube, [0, -1, 0], [0, 1, 0], 0.5, 12, "red"), [0, 0, 0], [1, 0, 0]), "tube")
    keep(add.cut(add.make(add.grid, [0, 0, 0], [2, 2], 4, 4, "green"), [0, 0, 0], [1, 0, 0.5]), "sheet")


# ---------------------------------------------------------------------------
#  inside
# ---------------------------------------------------------------------------

@case
def b_inside_points():
    B = make_box([0, 0, 0], 2, "red")
    # (z = 0.9999999995: just under the top face, which all three rays graze -- False)
    for p in ([0, 0, 0], [0.9, 0.9, 0.9], [1.1, 0, 0], [0, -3, 0], [1, 0, 0], [1, 1, 0], [1, 1, 1],
              [0.5, 1, 0.25], [-1, -1, -1], [0.999999999, 0, 0], [1.000000001, 0, 0], [0.3, 0.2, -1],
              [0.1, 0.2, 0.9999999995], [1e30, 0, 0]):
        record(add.inside(B, p))
    S = make_sphere([0, 0, 0], 1, 10, "white")
    for p in ([0, 0, 0], [0.5, 0.5, 0.5], [0.6, 0.6, 0.6], [0, 1, 0], [0, 0.99, 0], [0, 1.01, 0]):
        record(add.inside(S, p))
    T = make_torus([0, 0, 0], 1.0, 0.35, 16, 8, "teal")
    for p in ([0, 0, 0], [1, 0, 0], [0, 0, -1], [0.7, 0.1, 0.7], [1.4, 0, 0], [1.3, 0, 0], [0, 0.3, 1]):
        record(add.inside(T, p))
    O = make_poly("octahedron", [0, 0, 0], 1)
    for p in ([0, 0, 0], [0.3, 0.3, 0.3], [0.34, 0.33, 0.33], [1, 0, 0], [0.5, 0.5, 0], [0, 0, 0.999]):
        record(add.inside(O, p))
    record(add.inside(add.Mesh(), [0, 0, 0]))
    record(add.inside(add.Mesh(), [1e30, -1e30, 5]))
    for p in ([float("nan"), 0, 0], [0, float("inf"), 0], [0, 0, float("-inf")]):
        try:
            add.inside(B, p)
        except (ValueError, OverflowError):
            record("raised")
    far = add.Mesh()                                          # 2e154 wide: add.py's (hi - lo) ** 2 overflows
    far.add_polygon([[-1e154, 0, 0], [-1e154, 1, 0], [-1e154, 0, 1]], "red")
    far.add_polygon([[1e154, 0, 0], [1e154, 0, 1], [1e154, 1, 0]], "red")
    record(len(add._to_polys(far)))
    try:
        add.inside(far, [0, 0, 0])
    except OverflowError:
        record("raised")
    wide = add.Mesh()                                         # 1e154 wide: no overflow, and cell numbers
    wide.add_polygon([[-0.5e154, 0, 0], [-0.5e154, 1, 0], [-0.5e154, 0, 1]], "red")   # far past 64 bits
    wide.add_polygon([[0.5e154, 0, 0], [0.5e154, 0, 1], [0.5e154, 1, 0]], "red")
    record(bits(add.inside(wide, [[0, 0.2, 0.2], [0.5e154, 0.2, 0.2], [-0.6e154, 0.2, 0.2], [0.5e154, 1, 1]])))


@case
def b_inside_list():
    T = make_torus([0, 0, 0], 1.0, 0.35, 16, 8, "teal")
    pts = add.random_points(300, [-1.5, -0.5, -1.5], [1.5, 0.5, 1.5], seed=3)
    record(bits(add.inside(T, pts)))
    S = make_sphere([0.2, 0, 0], 1, 6, "white")
    pts = add.random_points(200, [-1.2, -1.2, -1.2], [1.4, 1.2, 1.2], seed=4)
    record(bits(add.inside(S, pts)))
    D = add.difference(make_box([0, 0, 0], 2), make_sphere([0, 0, 0], 1.2, 6))
    pts = add.random_points(200, [-1.1, -1.1, -1.1], [1.1, 1.1, 1.1], seed=5)
    record(bits(add.inside(D, pts)))
    grid = [[x * 0.25, y * 0.25, 0.1] for x in range(-5, 6) for y in range(-5, 6)]
    record(bits(add.inside(make_box([0, 0, 0], 2), grid)))
    record(bits(add.inside(add.Mesh(), [[0, 0, 0], [1, 1, 1]])))
    try:
        add.inside(T, [])
    except IndexError:
        record("raised")


# ---------------------------------------------------------------------------
#  The machinery
# ---------------------------------------------------------------------------

@case
def b_poly_split():
    shapes = [[[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]],
              [[0, 0, 0], [2, 0, 1], [2, 2, 1], [0.5, 2.5, 0], [-1, 1, -0.5]],
              [[0, 0, 0], [1, 1, 1], [2, 2, 2]],
              [[0.1, 0.2, 0.3], [1.7, -0.4, 0.9]],
              [[0, 0, 0], [0, 0, 1e-12], [0, 1e-12, 0]]]
    planes = [((1.0, 0.0, 0.0), 0.5), ((0.0, 1.0, 0.0), 0.0), ((0.6, 0.8, 0.0), 1.0), ((0.0, 0.0, 1.0), 5.0),
              ((0.5773502691896258, 0.5773502691896258, 0.5773502691896258), 0.8)]
    for pts in shapes:
        p = add._Poly([tuple(float(x) for x in q) for q in pts], add.rgb("red"))
        record(pt(p.n))
        record(p.w)
        for pn, pw in planes:
            for eps in (add.BOOL_EPS, 1e-12, 0.3):
                front, back = [], []
                add._split(pn, pw, p, front, back, eps)
                record("%d %d" % (len(front), len(back)))
                for q in front + back:
                    record(len(q.pts))
                    for x in q.pts:
                        record(pt(x))
                    record(pt(q.n))
                    record(q.w)


@case
def b_near_order():
    S = add._Solid(make_sphere([0.1, 0.2, 0.3], 1.3, 10, "white"))
    record(S.grid.cell)
    record(len(S.grid.oversize))
    record(pt(S.lo))
    record(pt(S.hi))
    record(S.scale)
    r = add.Random(11)
    for _ in range(60):
        c = [r.uniform(-1.5, 1.5) for _ in range(3)]
        h = [r.uniform(0, 0.8) for _ in range(3)]
        lo = [c[a] - h[a] for a in range(3)]
        hi = [c[a] + h[a] for a in range(3)]
        record(ints(S.grid.near(lo, hi)))
    record(ints(S.grid.near([-9, -9, -9], [9, 9, 9])))
    T = add._Solid(add.merge([make_box([0, 0, 0], 1), make_cuboid([0, 0, 0], [40, 0.1, 0.1]),
                              make_sphere([3, 0, 0], 0.5, 6)]))
    record(ints(T.grid.oversize))
    for x in range(-2, 5):
        record(ints(T.grid.near([x - 0.3, -0.3, -0.3], [x + 0.3, 0.3, 0.3])))


@case
def b_rays():
    for M in (make_box([0, 0, 0], 2), make_torus([0, 0, 0], 1.0, 0.35, 16, 8), make_poly("tetrahedron", [0, 0, 0], 1),
              add.Mesh()):
        S = add._Solid(M)
        for which in range(3):
            R = S.ray_index(which)
            record(pt(R.d))
            record(pt(R.e1))
            record(pt(R.e2))
            record(R.cell)
            record(len(R.tris))
            answers = []
            for p in ([0, 0, 0], [1, 1, 1], [1, 0, 0], [0.5, 0.5, 0.5], [0, 1, 0], [-1, 0.2, 0.3], [1, 0.3, -0.2],
                      [0.25, 0.25, -0.2], [0.577, 0.577, 0.577]):
                answers.append(maybe(R.inside(tuple(p))))
            record(" ".join(answers))
        pts = [tuple(p) for p in add.random_points(40, [-1.2, -1.2, -1.2], [1.2, 1.2, 1.2], seed=8)]
        record(bits(S.contains(p) for p in pts))
        for p in M.V[:12]:
            record(maybe(S.ray_index(0).inside(tuple(p))))
            record(S.contains(tuple(p)))


@case
def b_pieces():
    A = add._Solid(make_box([0, 0, 0], 2, "red"))
    B = add._Solid(make_cuboid([1, 0, 0.5], [2, 2, 1], "blue"))
    for i, P in enumerate(A.polys):
        for piece, flush in add._split_against(P, B):
            record("%d %s" % (i, ints(flush)))
            for x in piece.pts:
                record(pt(x))
    for keep_set in (["out"], ["in"], ["same"], ["opp"], ["out", "same"], ["in", "opp"]):
        for flip in (False, True):
            for src, other in ((A, B), (B, A)):
                out = add._keep_pieces(src, other, set(keep_set), flip, add.rgb("gold") if flip else None)
                record(len(out))
                for q in out:
                    record(len(q.pts))
                    record(pt(q.n))
                    record(q.w)
                    record(q.c)
    polys = add._to_polys(make_sphere([0, 0, 0], 1, 6, "white"))
    record(len(polys))
    record(pt(polys[7].n))
    record(polys[7].w)
    M = add._from_polys(polys[:40])
    dump(M)
    dump(add._from_polys(polys[:5], False))
    record(add._boxes_apart(make_box([0, 0, 0], 1), make_box([1, 0, 0], 1)))
    record(add._boxes_apart(make_box([0, 0, 0], 1), make_box([1.00000001, 0, 0], 1)))
    record(add._boxes_apart(make_box([0, 0, 0], 1), make_box([1, 0, 0], 1), -1e-3))


@case
def b_loops():
    def run_loops(edges):
        out = add._loops(edges)
        record(len(out))
        for loop in out:
            record(len(loop))
            for p in loop:
                record(pt(p))

    sq = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
    run_loops([(sq[i], sq[(i + 1) % 4]) for i in range(4)])
    run_loops([(sq[(i + 1) % 4], sq[i]) for i in (2, 0, 3, 1)])
    run_loops([(sq[i], sq[(i + 1) % 4]) for i in range(3)])        # open: a chain of three
    run_loops([(sq[0], sq[1]), (sq[1], sq[2])])                    # too short
    tri = [(3, 0, 0), (4, 0, 0), (3.5, 1, 0)]
    run_loops([(sq[i], sq[(i + 1) % 4]) for i in range(4)] + [(tri[i], tri[(i + 1) % 3]) for i in range(3)])
    run_loops([(sq[0], sq[1]), (sq[1], sq[2]), (sq[1], (1, -1, 0)), ((1, -1, 0), sq[0]), (sq[2], sq[3]),
               (sq[3], sq[0])])                                    # a branch at sq[1]
    run_loops([((0.0, 0.0, 0.0), (1.00000001, 0, 0)), ((1.00000004, 0, 0), (1, 1, 0)),
               ((1, 1.00000002, 0), (-0.0, 1, 0)), ((0.0, 1, -0.0), (-0.0, -0.0, 0.00000003))])
    run_loops([])


@case
def b_intset():
    """Python's own set order (which _BoxGrid.near keeps), for sets built the way near()
    builds them -- small ones, and one past 50000 keys, where the table grows differently."""
    r = add.Random(5)
    for n, hi in ((3, 10), (5, 8), (6, 100), (20, 50), (100, 1000), (1000, 3000), (3000, 100000),
                  (100000, 400000)):
        s = set([r.randint(0, hi) for _ in range(r.randint(0, 6))])
        for _ in range(5):
            s.update([r.randint(0, hi) for _ in range(n // 5 + 1)])
        record(ints(s))


@case
def b_far():
    """Two small boxes far from the origin: the cell numbers of the box grid pass 2**53,
    beyond which a double no longer holds every whole number (add.py's are exact)."""
    A = make_box([7e11, 0, 0], 1e-3, "red")
    B = make_box([7e11 + 3e-4, 2e-4, 1e-4], 1e-3, "blue")
    SA, SB = add._Solid(A), add._Solid(B)
    record(SB.grid.cell)
    for P in SA.polys:
        lo = [min(q[a] for q in P.pts) for a in range(3)]
        hi = [max(q[a] for q in P.pts) for a in range(3)]
        record(ints(SB.grid.near(lo, hi)))
        record("%d %d" % (len(add._split_against(P, SB)), len(SB.grid.near(hi, hi))))
    all_three(A, B)
    record(bits(add.inside(B, [[7e11 + 3e-4, 2e-4, 1e-4], [7e11, 0, 0], [7e11 + 7e-4, 5e-4, 5e-4]])))
    # A small ball further out: its triangles are small enough to be filed in cells, and the
    # cell numbers (about 9.3e15) are only every second whole number as a double.
    SF = add._Solid(make_sphere([1e12, 0, 0], 1e-3, 6, "white"))
    SG = add._Solid(make_box([1e12 + 2e-4, 3e-4, 0], 1e-3, "red"))
    record(SF.grid.cell)
    record(ints(SF.grid.oversize))
    r = add.Random(2)
    for _ in range(40):
        c = [1e12 + r.uniform(-1e-3, 1e-3), r.uniform(-1e-3, 1e-3), r.uniform(-1e-3, 1e-3)]
        h = r.uniform(0, 4e-4)
        record(ints(SF.grid.near([c[0] - h, c[1] - h, c[2] - h], [c[0] + h, c[1] + h, c[2] + h])))
    for src, other, keep_set, flip in ((SG, SF, {"out"}, False), (SF, SG, {"in"}, True), (SF, SG, {"out"}, False)):
        out = add._keep_pieces(src, other, keep_set, flip)
        record(len(out))
        for q in out:
            for x in q.pts:
                record(pt(x))


@case
def b_guard():
    """More than 20000 pieces from one face: add.py stops cutting it -- and then cannot
    unpack the bare piece it returned (see the report)."""
    B = add.Mesh()                                            # 250 tall thin blades across the face
    for k in range(250):
        a = math.pi * k / 250 + 0.1
        c, s = math.cos(a), math.sin(a)
        ox, oz = 0.37 * math.sin(3.1 * k), 0.41 * math.cos(2.3 * k)
        B.add_polygon([[ox - 3 * c, 0.5, oz - 3 * s], [ox + 3 * c, 0.5, oz + 3 * s], [ox, 1.5, oz]], "blue")
    top = add.Mesh()
    top.add_polygon([[-1, 1, -1], [-1, 1, 1], [1, 1, 1], [1, 1, -1]], "red")
    res = add._split_against(add._Solid(top).polys[0], add._Solid(B))
    record(len(res))
    record(ints([i for i, x in enumerate(res) if isinstance(x, add._Poly)]))
    good = [x for x in res if not isinstance(x, add._Poly)]
    for piece, flush in good[:3] + good[-3:]:
        record(ints(flush))
        for x in piece.pts:
            record(pt(x))
    try:
        add.union(top, B)
    except TypeError:
        record("raised")


@case
def b_stress():
    makers = [lambda c, s, col: make_cuboid(c, [s, 0.8 * s, 1.1 * s], col),
              lambda c, s, col: make_sphere(c, 0.6 * s, 6, col),
              lambda c, s, col: make_cylinder([c[0], c[1] - 0.6 * s, c[2]], [c[0], c[1] + 0.6 * s, c[2]], 0.4 * s, 10,
                                              col),
              lambda c, s, col: make_cone([c[0], c[1] - 0.5 * s, c[2]], [c[0], c[1] + 0.5 * s, c[2]], 0.6 * s, 10, col),
              lambda c, s, col: make_poly("octahedron", c, 0.7 * s, col),
              lambda c, s, col: make_poly("dodecahedron", c, 0.7 * s, col),
              lambda c, s, col: make_torus(c, 0.5 * s, 0.2 * s, 12, 6, col)]
    colors = ["red", "green", "blue", "gold", "white", "teal", "pink"]
    for seed in range(21):
        r = add.Random(seed)
        ka = r.randint(0, len(makers) - 1)
        kb = r.randint(0, len(makers) - 1)
        ca = [r.uniform(-0.2, 0.2) for _ in range(3)]
        cb = [r.uniform(-0.6, 0.6) for _ in range(3)]
        sa = r.uniform(1.0, 1.6)
        sb = r.uniform(0.6, 1.4)
        axis = [r.uniform(-1, 1) for _ in range(3)]
        angle = r.uniform(0, math.pi)
        A = makers[ka](ca, sa, colors[ka])
        B = add.rotate(makers[kb](cb, sb, colors[kb]), axis, angle, cb)
        record("seed %d: %d %d" % (seed, ka, kb))
        keep(add.union(A, B), "u%d" % seed)
        keep(add.difference(A, B), "d%d" % seed)
        keep(add.intersect(A, B), "i%d" % seed)


@case
def b_chain():
    M = make_box([0, 0, 0], 2, "white")
    holes = [make_cylinder([x, -2, z], [x, 2, z], 0.25, 10, "red") for x, z in ((-0.5, -0.5), (0.5, 0.5), (0.5, -0.5))]
    M = add.difference(M, holes)
    keep(M, "drilled")
    M = add.union(M, make_cuboid([0, 1.2, 0], [1, 0.4, 1], "blue"))
    keep(M, "capped")
    M = add.intersect(M, make_sphere([0, 0, 0], 1.6, 6, "gold"))
    keep(M, "rounded")
    M = add.cut(M, [0, 0, 0.1], [0, 0, 1], True, "black")
    keep(M, "halved")
    record(bits(add.inside(M, [[0, 0, 0], [-0.5, 0, -0.5], [0.8, 0.8, -0.8], [0, 1.3, 0]])))


@case
def b_scene():
    add.box([0, 0, 0], 2, "red")
    a = add.layer()
    add.sphere([1, 1, 1], 1.3, 16, "blue")
    b = add.layer()
    add.mesh(add.union(a, b))
    save_case()


if __name__ == "__main__":
    import sys
    run(sys.argv)

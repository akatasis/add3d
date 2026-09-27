"""Parity cases for _src/65_subdivide.py: the topology, one Catmull-Clark step
and the limit positions and tangents, the regular stencils and the patch
trees, the reparameterisation (norm, polygon domains, face maps), the repair,
and catmull_clark / smooth / subdivide themselves (see cases_65_subdivide.cpp)."""
import math

from parity_case import _current, add, case, record, run, save_case, save_mesh  # noqa: F401

SIX = ["red", (10, 200, 30), add.transparent("sky", 0.4), "#123456", (250, 250, 5), "navy"]


# -- helpers (the C++ twin has the same ones) -----------------------------------

def ints(xs):
    return " ".join("%d" % i for i in xs)


def floats(xs):
    return " ".join(repr(float(x)) for x in xs)


def pt(p):
    return [float(p[0]), float(p[1]), float(p[2])]


def dump(M):
    """Every vertex (at full precision), face and colour of a mesh."""
    record("V %d" % len(M.V))
    for p in M.V:
        record(pt(p))
    record("F %d" % len(M.F))
    for f, c in zip(M.F, M.C):
        record(ints(f))
        record(c)


def result(M, tag=""):
    """The mesh exactly as it is: an .off file, and every number in the .txt."""
    save_mesh(M, tag)
    record("-- " + tag)
    dump(M)


def error(fn):
    """Run fn and record the message of the exception it raises."""
    try:
        fn()
    except Exception as e:  # noqa: BLE001
        record("error: %s" % e)
        return
    record("no error")


def topo(T):
    """Every table of a _Topo."""
    record("V %d F %d E %d" % (len(T.V), len(T.F), len(T.E)))
    for e in T.E:
        record(ints(e))
    for v in range(len(T.V)):
        record("v%d: VF %s | VE %s | %s" % (v, ints(T.VF[v]), ints(T.VE[v]), T.boundary[v]))
    for f in range(len(T.F)):
        record("f%d: FE %s | FN %s" % (f, ints(T.FE[f]), ints(T.FN[f])))
    record(T.all_quads())
    for f in range(len(T.F)):
        record(pt(T.centroid(f)))
    for v in range(len(T.V)):
        r = T.ordered_ring(v)
        record("ring %d: %s" % (v, "None" if r is None else ints(r[0]) + " | " + ints(r[1])))


def shape(T):
    """The points and faces of a _Topo."""
    record("V %d F %d" % (len(T.V), len(T.F)))
    for p in T.V:
        record(pt(p))
    for f in T.F:
        record(ints(f))


def net(P):
    """A 4 x 4 control net (or None)."""
    if P is None:
        record("None")
        return
    for row in P:
        for c in row:
            record(pt(c))


def from_faces(V, F, colors=None):
    M = add.Mesh()
    for p in V:
        M.add_vertex(p)
    for i, f in enumerate(F):
        M.add_face(f, colors[i % len(colors)] if colors else None)
    return M


def as_topo(M):
    return add._Topo([list(p) for p in M.V], [list(f) for f in M.F])


CUBE_F = [[0, 4, 6, 2], [1, 3, 7, 5], [0, 1, 5, 4], [2, 6, 7, 3], [0, 2, 3, 1], [4, 5, 7, 6]]


def cube(lo=(-1.0, -0.75, -0.5), hi=(1.0, 1.25, 0.9), colors=SIX, faces=CUBE_F):
    """A box from lo to hi as 8 shared corners and 6 quads, one colour each."""
    V = [[hi[0] if k & 1 else lo[0], hi[1] if k & 2 else lo[1], hi[2] if k & 4 else lo[2]] for k in range(8)]
    return from_faces(V, faces, colors)


def open_box():
    """The cube without its last face: an open box."""
    return cube(faces=CUBE_F[:5])


def welded(M):
    M = M.copy()
    add._weld(M, 1e-9)
    return M


def two_cubes(offset):
    """Two unit cubes, the second moved by ``offset``: (1, 1, 0) shares an edge, (1, 1, 1) a corner."""
    hi = (offset[0] + 1.0, offset[1] + 1.0, offset[2] + 1.0)
    return add.merge([cube((0.0, 0.0, 0.0), (1.0, 1.0, 1.0), ["red"]), cube(offset, hi, ["blue"])])


def book():
    """Three quads that share one edge, and a fourth hanging off one of them."""
    V = [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [-0.5, 0.0, 0.8], [-0.5, 1.0, 0.8],
         [-0.5, 0.0, -0.8], [-0.5, 1.0, -0.8], [2.0, 0.0, 0.3], [2.0, 1.0, 0.3]]
    return from_faces(V, [[0, 2, 3, 1], [0, 1, 5, 4], [0, 6, 7, 1], [2, 8, 9, 3]], SIX)


def patch(nx=4, nz=3):
    """An open, bumpy sheet of quads."""
    V = []
    for i in range(nx + 1):
        for j in range(nz + 1):
            x = -1.0 + 2.0 * i / nx
            z = -0.7 + 1.9 * j / nz
            V.append([x, 0.3 * math.sin(2 * x + z) + 0.1 * x * z, z])
    F = []
    for i in range(nx):
        for j in range(nz):
            a = i * (nz + 1) + j
            F.append([a, a + 1, a + nz + 2, a + nz + 1])
    return from_faces(V, F, SIX)


def pent_pyramid():
    """A pentagon and five triangles: valence 5 at the (off-centre) apex, 3 round the base."""
    V = [[math.cos(2 * math.pi * k / 5), 0.0, math.sin(2 * math.pi * k / 5)] for k in range(5)]
    V.append([0.1, 1.3, -0.05])
    F = [[0, 1, 2, 3, 4]] + [[k, 5, (k + 1) % 5] for k in range(5)]
    return from_faces(V, F, SIX)


def bipyramid(k=6):
    """Two k-sided pyramids base to base: valence k at the tips."""
    V = [[math.cos(2 * math.pi * i / k), 0.0, math.sin(2 * math.pi * i / k)] for i in range(k)]
    V += [[0.0, 1.1, 0.0], [0.05, -0.9, 0.1]]
    F = [[i, k, (i + 1) % k] for i in range(k)] + [[(i + 1) % k, k + 1, i] for i in range(k)]
    return from_faces(V, F, SIX)


def octa(r=1.0):
    V = [[r, 0, 0], [-r, 0, 0], [0, r, 0], [0, -r, 0], [0, 0, r], [0, 0, -r]]
    F = [[0, 2, 4], [1, 4, 2], [0, 4, 3], [1, 3, 4], [0, 5, 2], [1, 2, 5], [0, 3, 5], [1, 5, 3]]
    return from_faces(V, F, SIX)


def ring_of_boxes():
    """Eight boxes round a missing middle one, as drawn (not welded): a ring, once repaired."""
    add.push()
    for i in range(3):
        for j in range(3):
            if (i, j) != (1, 1):
                add.box([i, 0, j], 1, SIX[(i + j) % 6])
    return add.pop()


def l_boxes():
    """Three boxes in an L (as drawn)."""
    add.push()
    add.box([0, 0, 0], 1, "red")
    add.box([1, 0, 0], 1, "green")
    add.box([0, 1, 0], 1, "blue")
    return add.pop()


def quads_apart():
    """A box as 6 separate quads (24 corners)."""
    M = add.Mesh()
    C = cube()
    for k, f in enumerate(C.F):
        M.add_polygon([C.V[i] for i in f], SIX[k])
    return M


def messy():
    """A cube with a repeated face and a degenerate one."""
    M = cube()
    M.add_face([0, 4, 6, 2], "red")
    M.add_face([1, 1, 3], "blue")
    return M


# -- the topology ----------------------------------------------------------------

@case
def topo_tables():
    for M in (patch(3, 2), pent_pyramid(), cube(), open_box()):
        topo(as_topo(M))
    # a vertex where two fans touch, an isolated vertex (7), a triangle on an edge
    V = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.2], [-1.0, -1.0, 0.1],
         [0.0, -1.0, 0.3], [5.0, 5.0, 5.0], [0.5, 2.0, 0.0]]
    topo(add._Topo(V, [[0, 1, 2, 3], [0, 4, 5, 6], [3, 2, 8]]))
    # two faces that disagree on the way round their shared edge
    topo(add._Topo(V, [[0, 1, 2, 3], [2, 3, 8]]))


@case
def topo_errors():
    V = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0], [0.5, 0.5, 1.0]]
    error(lambda: add._Topo(V, [[0, 1, 2], [0, 1]]))
    error(lambda: add._Topo(V, [[0, 1, 2, 3], [0, 1, 1, 4]]))
    error(lambda: add._Topo(V, [[0, 1, 2], [0, 1, 4], [1, 0, 3]]))
    error(lambda: add._Topo(V, [[0, 1, 0, 2]]))
    error(lambda: add._Topo(V, [[0, 1, 2, 0, 3, 4]]))
    T = add._Topo(V, [[0, 1, 2, 0, 3, 4]])              # a face through vertex 0 twice is accepted
    topo(T)


@case
def cc_constants():
    for N in range(1, 13):
        record(add._cc_lambda(N))
        record(add._cc_gamma(N))
    record(add._cc_gamma(100))
    error(lambda: add._cc_lambda(0))


@case
def cc_step():
    for M in (pent_pyramid(), patch(3, 2), open_box()):
        T = as_topo(M)
        S, parent = add._cc_subdivide(T)
        record(ints(parent))
        topo(S)
    # a vertex without faces and one with a single face are kept where they are
    V = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0], [3.0, 3.0, 3.0], [-1.0, 0.0, 0.2],
         [-1.0, -1.0, 0.1], [0.0, -1.0, 0.3]]
    S, parent = add._cc_subdivide(add._Topo(V, [[0, 1, 2, 3], [0, 5, 6, 7]]))
    record(ints(parent))
    shape(S)


@case
def limit_positions():
    for M in (patch(), cube(), pent_pyramid(), open_box(), octa()):
        for p in add._cc_limit_positions(as_topo(M)):
            record(pt(p))
    V = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0], [5.0, 5.0, 5.0], [-1.0, 0.0, 0.2],
         [-1.0, -1.0, 0.1], [0.0, -1.0, 0.3]]
    for p in add._cc_limit_positions(add._Topo(V, [[0, 1, 2, 3], [0, 5, 6, 7]])):
        record(pt(p))
    # an inner vertex whose faces do not make one fan (one of them flipped)
    T = add._Topo([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -1.0, 0.0]],
                  [[0, 1, 2], [0, 2, 3], [0, 4, 3], [0, 1, 4]])
    for p in add._cc_limit_positions(T):
        record(pt(p))


@case
def limit_tangents():
    for M in (cube(), octa(), patch(4, 4), pent_pyramid()):
        T = as_topo(M)
        for v in range(len(T.V)):
            t = add._cc_limit_tangents(T, v)
            if t is None:
                record("None")
            else:
                record(pt(t[0]))
                record(pt(t[1]))


@case
def basis_bicubic():
    for t in [0.0, 0.25, 1.0 / 3, 0.5, 0.9, 1.0, -0.5, 1.5]:
        record(floats(add._bspline_basis(t)))
    T = as_topo(patch(4, 3))
    P = add._regular_stencil(T, 4)
    for u, v in [(0.0, 0.0), (0.5, 0.25), (1.0, 1.0), (0.1, 0.9), (1.0, 0.0)]:
        record(pt(add._eval_bicubic(P, u, v)))


@case
def stencils():
    T = as_topo(patch(4, 3))
    for f in range(len(T.F)):
        net(add._regular_stencil(T, f))
    T = as_topo(patch(1, 1))                      # one lone quad: every row reflected
    net(add._regular_stencil(T, 0))
    T = as_topo(patch(1, 3))                      # a strip one quad wide
    for f in range(len(T.F)):
        net(add._regular_stencil(T, f))
    T, _ = add._topology_of(add.make(add.torus, [0, 0, 0], 2.0, 0.6, 8, 5, "gold"))
    for f in range(0, len(T.F), 7):
        net(add._regular_stencil(T, f))
    T = as_topo(cube())
    net(add._regular_stencil(T, 0))               # valence 3: none
    T1, _ = add._cc_subdivide(T)
    T2, _ = add._cc_subdivide(T1)
    for f in range(0, len(T2.F), 5):
        net(add._regular_stencil(T2, f))
    T = as_topo(pent_pyramid())
    net(add._regular_stencil(T, 0))               # not a quad
    T = as_topo(open_box())
    T1, _ = add._cc_subdivide(T)
    for f in range(len(T1.F)):
        net(add._regular_stencil(T1, f))


@case
def neighbourhoods():
    T = as_topo(pent_pyramid())
    T1, _ = add._cc_subdivide(T)
    for f, origin in [(0, 0), (3, 2), (7, 1), (12, 3), (19, 0)]:
        L = add._neighbourhood(T1, f, origin)
        shape(L)
        record(ints(L.VE[0]) + " | " + ints([1 if b else 0 for b in L.boundary]))


@case
def patch_trees():
    T = as_topo(cube())
    T1, _ = add._cc_subdivide(T)
    tree = add._PatchTree(T1, 0)
    for u, v in [(0.0, 0.0), (0.5, 0.5), (1.0, 1.0), (0.3, 0.7), (1e-3, 2e-3), (0.75, 0.1), (0.999, 0.0),
                 (0.0, 0.6), (0.25, 0.25), (0.0, 1e-9)]:
        record(pt(tree.eval(u, v)))
    T = as_topo(pent_pyramid())
    T1, _ = add._cc_subdivide(T)
    for f in (0, 4, 5, 9):
        tree = add._PatchTree(T1, f)
        for u, v in [(0.1, 0.2), (0.6, 0.05), (0.0, 0.0), (0.5, 0.5), (0.9, 0.95)]:
            record(pt(tree.eval(u, v)))
    T = as_topo(open_box())
    T1, _ = add._cc_subdivide(T)
    tree = add._PatchTree(T1, 1)
    for u, v in [(0.1, 0.2), (0.6, 0.05), (0.0, 0.0), (0.5, 0.5)]:
        record(pt(tree.eval(u, v)))


# -- the reparameterisation ------------------------------------------------------

@case
def nu_norms():
    for a, b in [(0.0, 0.0), (0.3, 0.7), (1.0, 0.2), (0.5, 0.5), (1e-9, 0.999), (1.0, 1.0), (0.7, 0.3)]:
        for p in [0.5, 1.0, 2.0, 3.7, 64.0, 64.5, 1e9]:
            record(add._nu_norm(a, b, p))
    record(add._nu_norm(0.2, 0.4, -1.0))
    error(lambda: add._nu_norm(0.3, 0.4, 0.0))
    error(lambda: add._nu_norm(0.0, 0.4, -1.0))
    error(lambda: add._nu_norm(1e-200, 0.4, -2.0))


@case
def domains():
    xs = [(0.0, 0.0), (0.3, 0.1), (-0.2, 0.5), (0.9, -0.3), (1.0, 0.0), (0.0, -1.0), (2.0, 2.0), (-0.7, -0.05),
          (0.5, 1e-17), (-1.0, 0.0), (-0.3, -1e-300)]
    for m in (3, 4, 5, 6, 8):
        dom = add._PolygonDomain.get(m)
        record("m %d" % dom.m)
        for P in dom.P:
            record(P)
        for E in dom.E:
            record(E)
        for k in range(m):
            for u, v in [(0.0, 0.0), (0.25, 0.5), (1.0, 1.0), (0.6, 0.1)]:
                record(dom.kite_map(k, u, v))
        for x in xs:
            k = dom.kite_of(x)
            record(k)
            record(dom.kite_inverse(k, x))
            record(dom.kite_inverse((k + 1) % m, x))
            lam = dom.wachspress(x)
            record(floats(lam))
            for k2 in range(m):
                record(dom.corner_nu(lam, k2, 2.0))
            record(dom.corner_nu(lam, 0, 100.0))
    record(add._PolygonDomain(7).E[3])


@case
def reparams():
    xs = [(0.0, 0.0), (0.3, 0.1), (-0.2, 0.5), (0.9, -0.3), (0.99, 0.01), (0.5, 0.0), (-0.4, -0.4), (1.0, 0.0)]
    for m, gamma, gc, p in [(3, [0.7776275156074476, 1.0, 1.2], 1.0, 2.0),
                            (5, [1.0, 1.0, 1.0, 1.0, 1.0], 1.1593839643382764, 2.0),
                            (6, [1.2711881726573797, 1.0, 1.0, 0.8, 1.0, 1.0], 1.3, 3.0),
                            (4, [1.0, 1.0, 1.0, 1.0], 1.0, 2.0),
                            (4, [0.7776275156074476, 1.0, 1.0, 1.0], 1.0, 100.0),
                            (3, [0.5, 0.5, 0.5], 0.6, 1.0)]:
        dom = add._PolygonDomain.get(m)
        trivial, apply = add._face_reparam(dom, gamma, gc, p)
        record(trivial)
        for x in xs:
            record(apply(x))


@case
def node_counts():
    for m in (3, 4, 5, 6):
        record(ints([add._face_node_count(m, n) for n in range(0, 9)]))


# -- the repair ------------------------------------------------------------------

@case
def cut_non_manifold():
    for M in (welded(two_cubes((1.0, 1.0, 0.0))), welded(two_cubes((1.0, 1.0, 1.0))), book()):
        M = M.copy()
        add._cut_non_manifold(M)
        dump(M)
    # four faces on one edge, all the same way round (so no pair agrees), and a bow tie
    V = [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [-1.0, 1.0, 0.0],
         [0.0, 0.0, 1.0], [0.0, 1.0, 1.0], [0.0, 0.0, -1.0], [0.0, 1.0, -1.0]]
    M = from_faces(V, [[0, 1, 3, 2], [0, 1, 5, 4], [0, 1, 7, 6], [0, 1, 9, 8]], SIX)
    add._cut_non_manifold(M)
    dump(M)
    M = from_faces([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -1.0, 0.0]],
                   [[0, 1, 2], [0, 3, 4]], ["red"])
    add._cut_non_manifold(M)
    dump(M)


@case
def repairs():
    for M in (ring_of_boxes(), l_boxes(), two_cubes((1.0, 1.0, 0.0)), book(), messy(), quads_apart(), add.Mesh()):
        dump(add._repair_for_subdivision(M))


@case
def topologies():
    T, M = add._topology_of(ring_of_boxes(), False)
    record("%d %d %d %d" % (len(T.V), len(T.F), len(T.E), len(M.V)))
    T, M = add._topology_of(ring_of_boxes())
    topo(T)
    dump(M)


# -- catmull_clark ---------------------------------------------------------------

@case
def cc_cube():
    M = cube()
    for steps in (1, 2, 3):
        result(add.catmull_clark(M, steps), "s%d" % steps)


@case
def cc_box_scene():
    add.box([0, 0, 0], 2, "red")
    add.mesh(add.catmull_clark(add.layer(), 3))
    save_case()


@case
def cc_prism():
    M = add.make(add.prism, add.profile_polygon(5, 1.0), 1.5, "gold")
    result(add.catmull_clark(M, 1), "s1")
    result(add.catmull_clark(M, 2), "s2")
    L = add.make(add.prism, [[0, 0], [2, 0], [2, 1], [1, 1], [1, 2], [0, 2]], 1.0, "orange")
    result(add.catmull_clark(L, 2), "L")


@case
def cc_tetra():
    M = add.make(add.tetrahedron, [0, 0, 0], 1.0, "blue")
    for steps in (1, 2, 3):
        result(add.catmull_clark(M, steps), "s%d" % steps)


@case
def cc_patch():
    for steps in (1, 2):
        result(add.catmull_clark(patch(), steps), "s%d" % steps)
    result(add.catmull_clark(patch(), 2, False), "raw")
    result(add.catmull_clark(open_box(), 2), "openbox")


@case
def cc_tri_pent():
    for steps in (1, 2):
        result(add.catmull_clark(pent_pyramid(), steps), "s%d" % steps)
    D = add.make(add.dodecahedron, [0, 0, 0], 1.0, "gold")
    I = add.make(add.icosahedron, [3, 0, 0], 1.0, "sky")
    result(add.catmull_clark(add.merge([D, I]), 1), "di")


@case
def cc_nonmanifold():
    result(add.catmull_clark(two_cubes((1.0, 1.0, 0.0))), "edge")
    result(add.catmull_clark(two_cubes((1.0, 1.0, 1.0))), "vertex")
    result(add.catmull_clark(book(), 2), "book")
    result(add.catmull_clark(welded(two_cubes((1.0, 1.0, 1.0))), 1, False), "vertex_raw")
    result(add.catmull_clark(ring_of_boxes(), 2), "ring")


@case
def cc_errors():
    error(lambda: add.catmull_clark(welded(two_cubes((1.0, 1.0, 0.0))), 1, False))
    error(lambda: add.catmull_clark(book(), 1, False))
    V = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]]
    error(lambda: add.catmull_clark(from_faces(V, [[0, 1, 2], [0, 1]]), 1, False))
    error(lambda: add.catmull_clark(from_faces(V, [[0, 1, 1, 2]]), 1, False))
    error(lambda: add.catmull_clark(from_faces(V, [[0, 1, 2, 3], [0, 1, 0, 2]]), 1, False))


@case
def cc_colours():
    M = cube(colors=["red", add.transparent("green", 0.25), (1, 2, 3), "#abcdef80", "white", "black"])
    C = add.catmull_clark(M, 2)
    result(C)
    add.obj(_current[0] + ".obj", C)
    T = add.catmull_clark(add.texture(cube(), "wood.png", "box"), 1)
    dump(T)
    add.obj(_current[0] + "_tex.obj", T)


@case
def cc_steps():
    M = cube()
    result(add.catmull_clark(M, 0), "s0")
    result(add.subdivide(M, 2), "sub2")
    result(add.subdivide(pent_pyramid(), 1, False), "sub_raw")
    result(add.catmull_clark(M, -1), "neg")
    result(add.catmull_clark(add.Mesh()), "empty")


@case
def cc_apart():
    M = cube()
    M.add_vertex([5, 5, 5])
    result(add.catmull_clark(M, 1, False), "isolated_raw")
    result(add.catmull_clark(M, 1, True), "isolated")
    result(add.catmull_clark(quads_apart(), 1, False), "quads_raw")
    result(add.catmull_clark(quads_apart(), 1), "quads")
    result(add.catmull_clark(messy(), 1), "messy")


# -- smooth ----------------------------------------------------------------------

@case
def sm_cube():
    M = cube()
    for n in range(1, 7):
        result(add.smooth(M, n), "n%d" % n)


@case
def sm_cube_plain():
    M = cube()
    for n in (1, 2, 3, 4):
        result(add.smooth(M, n, False), "n%d" % n)


@case
def sm_octa():
    M = octa()
    for n in range(1, 7):
        result(add.smooth(M, n), "n%d" % n)
    result(add.smooth(M, 3, True, False), "nocentre")
    result(add.smooth(M, 4, False), "plain")


@case
def sm_p_scale():
    M = pent_pyramid()
    result(add.smooth(M, 3, True, True, 1.0), "p1")
    result(add.smooth(M, 3, True, True, 3.5), "p3_5")
    result(add.smooth(M, 3, True, True, 100.0), "p100")
    result(add.smooth(M, 4, True, True, 2.0, 0.5), "s0_5")
    result(add.smooth(M, 4, True, True, 2.0, 2.0), "s2")
    result(add.smooth(M, 4, True, True, 2.0, 0.0), "s0")
    result(add.smooth(M, 5, True, False, 1.5, 1.25), "mix")


@case
def sm_centre():
    M = add.make(add.prism, add.profile_polygon(5, 1.0), 1.5, "gold")
    for n in (2, 3, 4):
        result(add.smooth(M, n, True, True), "on%d" % n)
        result(add.smooth(M, n, True, False), "off%d" % n)
        result(add.smooth(M, n, False), "plain%d" % n)


@case
def sm_l_block():
    result(add.smooth(l_boxes(), 3), "boxes3")
    result(add.smooth(l_boxes(), 4), "boxes4")
    L = add.make(add.prism, [[0, 0], [2, 0], [2, 1], [1, 1], [1, 2], [0, 2]], 1.0, "orange")
    result(add.smooth(L, 3), "prism3")
    result(add.smooth(L, 2, False), "prism_plain")


@case
def sm_ring():
    R = ring_of_boxes()
    result(add.smooth(R, 2), "n2")
    result(add.smooth(R, 5), "n5")
    result(add.smooth(R, 6, False), "plain6")


@case
def sm_valence():
    result(add.smooth(add.make(add.icosahedron, [0, 0, 0], 1.0, "white"), 3), "icosa")
    result(add.smooth(add.make(add.sphere, [0, 0, 0], 1.0, 10, "sky", 1), 2), "geo")
    result(add.smooth(bipyramid(6), 4), "bipyramid6")
    result(add.smooth(bipyramid(5), 3), "bipyramid5")
    result(add.smooth(add.make(add.dodecahedron, [0, 0, 0], 1.0, "gold"), 3), "dodeca")
    result(add.smooth(add.make(add.cylinder, [0, 0, 0], [0, 2, 0], 0.5, 8, "red"), 3), "cylinder")


@case
def sm_open():
    for n in (1, 2, 3, 4):
        result(add.smooth(patch(), n), "patch%d" % n)
    result(add.smooth(open_box(), 3), "openbox3")
    result(add.smooth(open_box(), 4, False), "openbox_plain")
    result(add.smooth(add.make(add.tube, [0, 0, 0], [0, 2, 0], 0.5, 8, "teal"), 3), "tube")
    G = add.make(add.grid, [0, 0, 0], [2, 2], 4, 3, "lime", lambda x, z: 0.2 * math.sin(3 * x) * math.cos(2 * z))
    result(add.smooth(G, 4), "grid")
    result(add.smooth(book(), 3), "book")
    result(add.smooth(patch(1, 1), 5), "lone_quad")


@case
def sm_misc():
    result(add.smooth(add.make(add.tetrahedron, [0, 0, 0], 1.0, "red"), 2), "tetra2")
    result(add.smooth(add.make(add.torus, [0, 0, 0], 2.0, 0.6, 8, 5, "gold"), 3), "torus")
    result(add.smooth(add.make(add.uvsphere, [0, 0, 0], 1.0, 8, 4, "blue"), 2), "uvsphere")
    result(add.smooth(add.make(add.frame, [0, 0, 0], 2.0, 0.4, "brown"), 2), "frame")
    result(add.smooth(two_cubes((1.0, 1.0, 0.0)), 3), "nm_edge")
    result(add.smooth(two_cubes((1.0, 1.0, 1.0)), 2), "nm_vertex")
    result(add.smooth(cube(), 3, True, True, 2.0, 1.0, False), "norepair")
    result(add.smooth(quads_apart(), 2, True, True, 2.0, 1.0, False), "apart_raw")
    result(add.smooth(add.Mesh(), 3), "empty")


@case
def sm_errors():
    error(lambda: add.smooth(cube(), 0))
    error(lambda: add.smooth(cube(), -3))
    error(lambda: add.smooth(cube(), 3, True, True, 0.0))
    error(lambda: add.smooth(book(), 3, True, True, 2.0, 1.0, False))
    error(lambda: add.smooth(cube(), 3, True, True, 2.0, 1e4))
    error(lambda: add.smooth(cube(), 3, True, True, -1.0))
    error(lambda: add.smooth(cube(), 3, True, True, 2.0, 1.0))


@case
def sm_raw_shapes():
    M = cube()
    M.F[0].reverse()                                  # one face the wrong way round
    result(add.smooth(M, 3, True, True, 2.0, 1.0, False), "flipped")
    result(add.catmull_clark(M, 2, False), "flipped_cc")
    result(add.smooth(welded(two_cubes((1.0, 1.0, 1.0))), 3, True, True, 2.0, 1.0, False), "touching_raw")
    result(add.smooth(cube(), 3, True, True, 2.0, 1000.0), "s1000")


@case
def sm_colours():
    M = cube(colors=["red", add.transparent("green", 0.25), (1, 2, 3), "#abcdef80", "white", "black"])
    S = add.smooth(M, 3)
    result(S)
    add.obj(_current[0] + ".obj", S)
    add.mesh(add.smooth(add.make(add.box, [0, 0, 0], 2, "red"), 5))
    save_case()


if __name__ == "__main__":
    import sys
    run(sys.argv)

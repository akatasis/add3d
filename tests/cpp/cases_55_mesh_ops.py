"""Parity cases for _src/55_mesh_ops.py: vertices, edges, neighbours, faces,
borders, inflate / spherify / refine / dual / truncate (see
cases_55_mesh_ops.cpp)."""
import math

from parity_case import _current, add, case, record, run, save_case, save_mesh  # noqa: F401

SIX = ["red", (10, 200, 30), add.transparent("sky", 0.4), "#123456", (250, 250, 5), "navy"]
PHI = (1 + math.sqrt(5)) / 2

#: Vertices (x, y, z), (y, z, x), (z, x, y) whose nearest to the origin Python's ``** 2``
#: finds differently from ``x * x`` (found by search).
TIES = [(1.4050326807183406, 0.4468445654703572, 1.4270568530698329),
        (1.0153553763542957, 1.3452739161380447, 1.1450256657771676),
        (-0.7115232226960133, -0.5445620771153004, -0.9360590698721349)]


def ints(xs):
    return " ".join("%d" % i for i in xs)


def floats(xs):
    return " ".join(repr(float(x)) for x in xs)


def pairs(es):
    return " ".join("%d-%d" % (a, b) for a, b in es)


def lists(xss):
    return [ints(xs) for xs in xss]


def pt(p):
    return [float(p[0]), float(p[1]), float(p[2])]


def save_obj(M, tag):
    """The mesh exactly as it is, as .obj + .mtl (faces of any size kept whole)."""
    add.obj(_current[0] + "_" + tag + ".obj", M)


def from_faces(V, F, colors=None):
    M = add.Mesh()
    for p in V:
        M.add_vertex(p)
    for i, f in enumerate(F):
        M.add_face(f, colors[i % len(colors)] if colors else None)
    return M


CUBE_F = [[0, 4, 6, 2], [1, 3, 7, 5], [0, 1, 5, 4], [2, 6, 7, 3], [0, 2, 3, 1], [4, 5, 7, 6]]


def cube(lo=(-0.5, -0.25, -0.75), hi=(0.5, 0.75, 1.25), colors=None, faces=CUBE_F):
    V = [[hi[0] if k & 1 else lo[0], hi[1] if k & 2 else lo[1], hi[2] if k & 4 else lo[2]] for k in range(8)]
    return from_faces(V, faces, colors)


def tube():
    """The cube without its bottom and top: two border loops."""
    return cube(colors=SIX, faces=[[0, 4, 6, 2], [1, 3, 7, 5], [0, 2, 3, 1], [4, 5, 7, 6]])


def octa(r=1.0):
    V = [[r, 0, 0], [-r, 0, 0], [0, r, 0], [0, -r, 0], [0, 0, r], [0, 0, -r]]
    F = [[0, 2, 4], [1, 4, 2], [0, 4, 3], [1, 3, 4], [0, 5, 2], [1, 2, 5], [0, 3, 5], [1, 5, 3]]
    return from_faces(V, F, SIX)


def tetra():
    V = [[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]]
    return from_faces(V, [[0, 1, 2], [0, 3, 1], [0, 2, 3], [1, 3, 2]], ["red", "green", "blue", "gold"])


def icosa():
    p = PHI
    V = [[-1, p, 0], [1, p, 0], [-1, -p, 0], [1, -p, 0], [0, -1, p], [0, 1, p], [0, -1, -p], [0, 1, -p],
         [p, 0, -1], [p, 0, 1], [-p, 0, -1], [-p, 0, 1]]
    F = [[0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11], [1, 5, 9], [5, 11, 4], [11, 10, 2],
         [10, 7, 6], [7, 1, 8], [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9], [4, 9, 5],
         [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]]
    return from_faces(V, F, ["white", "sky"])


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


def mixed():
    """A convex pentagon, a concave one, a triangle and a two-corner face."""
    M = add.Mesh()
    M.add_polygon([[0, 0, 0], [2, 0, 0], [2.5, 1, 0.2], [1, 2, 0.1], [-0.5, 1, 0]], "red")
    M.add_polygon([[3, 0, 0], [5, 0, 0], [5, 2, 0], [4, 1, 0], [3, 2, 0]], "green")
    M.add_polygon([[0, 3, 0], [1, 3, 0], [0.5, 4, 1]], (1, 2, 3))
    M.add_face([0, 5], "blue")
    return M


def touching():
    """Two triangles that share one corner only."""
    return from_faces([[0, 0, 0], [1, 0, 0], [0, 1, 0], [-1, 0, 0], [0, -1, 0]], [[0, 1, 2], [0, 3, 4]], ["red"])


def weird():
    """Everything _rings has to cope with: two cones meeting at vertex 0, a face
    through vertex 7 twice, two faces that disagree on the winding of edge
    13-14, a vertex without faces (17) and a two-corner face."""
    V = [[0, 0, 0], [1, 0, 0.5], [0, 1, 0.5], [-1, -1, 0.5], [1, 0, -0.5], [0, 1, -0.5], [-1, -1, -0.5],
         [3, 0, 0], [4, -1, 0], [4, 1, 0], [2, 1, 0], [2, -1, 0], [5, 0, 0],
         [0, 5, 0], [1, 5, 0], [0, 6, 0], [0, 4, 0],
         [9, 9, 9],
         [7, 0, 0], [8, 0.5, 0]]
    F = [[0, 1, 2], [0, 2, 3], [0, 3, 1], [0, 5, 4], [0, 6, 5], [0, 4, 6],
         [7, 8, 9, 7, 10, 11], [8, 12, 9],
         [13, 14, 15], [13, 14, 16],
         [18, 19]]
    return from_faces(V, F, SIX)


def dump(M):
    """Every vertex, face and colour of a mesh, exactly."""
    record(len(M.V))
    for p in M.V:
        record(pt(p))
    record(len(M.F))
    for f, c in zip(M.F, M.C):
        record(ints(f))
        record(c)


def mangled(seed):
    """A polyhedron with faces dropped, flipped and doubled, and a few random faces
    (two to five corners, a corner maybe repeated) added."""
    r = add.Random(seed)
    base = [icosa, octa, cube, tetra][r.randint(0, 3)]()
    M = add.Mesh()
    for p in base.V:
        M.add_vertex(p)
    for f, c in zip(base.F, base.C):
        roll = r.randint(0, 9 if seed < 20 else 39)
        if roll == 0:
            continue
        if roll == 1:
            f = list(reversed(f))
        M.add_face(f, c)
        if roll == 2:
            M.add_face(f, c)
    for _ in range(r.randint(0, 3)):
        k = r.randint(2, 5)
        M.add_face([r.randint(0, len(base.V) - 1) for _ in range(k)], SIX[r.randint(0, 5)])
    return M


def shapes():
    return [cube(colors=SIX), octa(), icosa(), tetra(), patch(3, 2), tube(), weird(), mixed(), touching()]


@case
def m_vertex():
    M = cube(colors=SIX)
    record(add.vertex(M, 3))
    record(add.vertex(M, -1))
    save_mesh(add.set_vertex(M, 3, [None, 2.5, None]), "set1")
    save_mesh(add.set_vertex(M, -2, [1, 2, 3]), "set_neg")
    save_mesh(add.set_vertices(M, {0: [None, None, -3], 5: [0.5, 0.25, None]}), "set_many")
    save_mesh(add.set_vertices(M, {}), "set_none")
    save_mesh(add.set_vertices(M, {7: [5, None, None], -1: [None, 6, 0.5]}), "alias")
    save_mesh(add.set_vertices(M, {-1: [5, None, 6], 7: [None, None, 1]}), "alias2")
    save_mesh(add.set_vertices(M, dict([(3, [1, None, None]), (2, [0, 0, 0]), (3, [None, 2, None])])), "repeat")
    save_mesh(add.set_vertices(M, {1: [9, 9, 9], 4: [8, 8, 8]}), "map")
    save_mesh(add.move_vertex(M, 7, [0.1, 0.2, -0.3]), "moved")
    save_mesh(add.move_vertex(M, -8, [1, 0, 0]), "moved_neg")
    record(add.nearest_vertex(M, [1, 1, 1]))
    record(add.nearest_vertex(M, [0, -0.25, -0.75]))
    record(add.nearest_vertex(add.Mesh(), [0, 0, 0]))
    for x, y, z in TIES:
        record(add.nearest_vertex(from_faces([[x, y, z], [y, z, x], [z, x, y]], []), [0, 0, 0]))
    for bad in (8, -9):
        try:
            add.vertex(M, bad)
        except IndexError:
            record("raised")


@case
def m_edges():
    for M in shapes():
        record(pairs(add.edges(M)))
        record(floats(add.edge_lengths(M)))
        record(add.mean_edge_length(M))
        record(add.edge_length(M, 0, 1))
        record(add.edge_length(M, -1, 2))
        record(lists(add.adjacency(M)))
    record(add.mean_edge_length(add.Mesh()))
    record(pairs(add.edges(add.Mesh())))
    add.mesh(octa())
    record(pairs(add.edges()))
    record(floats(add.edge_lengths()))
    record(add.mean_edge_length())
    record(lists(add.adjacency()))
    save_case()


@case
def m_rings():
    for M in shapes():
        record(" ".join("%d,%d:%d" % (k[0], k[1], v) for k, v in sorted(add._directed_edges(M).items())))
        for ring, closed in add._rings(M):
            record("%s %s" % (closed, " ".join("%d:%d" % e for e in ring)))


@case
def m_neighbors():
    for M in shapes():
        for i in range(len(M.V)):
            record(ints(add.neighbors(M, i)))
            record(add.valence(M, i))
            record(add.mean_neighbor_distance(M, i))
            record(ints(add.vertex_faces(M, i)))
            record(pt(add.vertex_normal(M, i)))
        record(ints(add.neighbours(M, -1)))
        record(ints(add.vertex_faces(M, -2)))
        record(add.valence(M, -3))


@case
def m_faces():
    for M in shapes():
        for i in range(len(M.F)):
            record(pt(add.face_center(M, i)))
            record(pt(add.face_normal(M, i)))
            record(add.face_area(M, i))
        record(add.face_centers(M))
        record(pt(add.face_center(M, -1)))
        record(pt(add.face_normal(M, -2)))
        record(add.face_area(M, -2))
        try:
            add.face_center(M, len(M.F))
        except IndexError:
            record("raised")
    add.mesh(patch(2, 2))
    record(add.face_centers())
    save_case()


@case
def m_boundary():
    for M in shapes() + [add.Mesh()]:
        record(pairs(add.boundary_edges(M)))
        record(lists(add.boundary_loops(M)))
    add.mesh(patch(2, 2))
    add.mesh(touching())
    record(pairs(add.boundary_edges()))
    record(lists(add.boundary_loops()))
    save_case()


@case
def m_inflate_spherify():
    C = cube(colors=SIX)
    save_mesh(add.inflate(C, 0.1), "inflate")
    save_mesh(add.inflate(patch(), -0.2), "inflate_patch")
    save_mesh(add.inflate(weird(), 0.3), "inflate_weird")
    save_mesh(add.spherify(C), "default")
    save_mesh(add.spherify(C, [0, 0, 0], 2.0, 0.5), "given")
    save_mesh(add.spherify(C, None, None, 0.25), "part")
    save_mesh(add.spherify(C, [0.1, 0.2, 0.3]), "center")
    save_mesh(add.spherify(C, None, 0), "r0")
    save_mesh(add.spherify(add.Mesh()), "empty")
    save_mesh(add.spherify(add.refine(octa(), 3)), "dome")


@case
def m_refine():
    save_mesh(add.refine(octa()), "octa1")
    save_mesh(add.refine(cube(colors=SIX), 2), "cube2")
    save_mesh(add.refine(mixed()), "mixed")
    save_mesh(add.refine(weird()), "weird")
    save_mesh(add.refine(cube(), 0), "zero")
    save_mesh(add.refine(icosa(), -1), "negative")
    save_obj(add.refine(add.texture(cube(colors=SIX), "a.png")), "textured")


@case
def m_dual():
    save_obj(add.dual(cube(colors=SIX)), "cube")
    save_obj(add.dual(octa(), "gold"), "octa")
    save_obj(add.dual(icosa()), "icosa")
    save_obj(add.dual(tetra()), "tetra")
    save_obj(add.dual(patch(3, 2)), "patch")
    save_obj(add.dual(weird()), "weird")
    save_obj(add.dual(add.dual(icosa()), add.transparent("red", 0.5)), "icosa2")
    save_obj(add.dual(add.Mesh()), "empty")


@case
def m_truncate():
    save_obj(add.truncate(icosa(), 1 / 3.0, "black"), "football")
    save_obj(add.truncate(cube(colors=SIX)), "cube")
    save_obj(add.truncate(octa(), 0.5), "half")
    save_obj(add.truncate(tetra(), 0.9, (10, 20, 30)), "over")
    save_obj(add.truncate(tetra(), 0.5 - 1e-13), "near_half")
    save_obj(add.truncate(patch(3, 2), 0.25), "patch")
    save_obj(add.truncate(weird(), 0.3), "weird")
    save_obj(add.truncate(mixed(), 0.2, "red"), "mixed")
    save_obj(add.truncate(touching()), "touching")


@case
def m_color_by_sides():
    F = add.truncate(icosa())
    save_mesh(add.color_by_sides(F, {5: "black", 6: "white"}), "football")
    save_mesh(add.color_by_sides(mixed(), {3: "red"}), "keep")
    save_mesh(add.color_by_sides(mixed(), {3: "red", 2: (1, 2, 3)}, "blue"), "fallback")
    save_mesh(add.color_by_sides(cube(colors=SIX), {}, add.transparent("gold", 0.5)), "all")


@case
def m_mangled():
    for seed in range(40):
        M = mangled(seed)
        dump(M)
        for ring, closed in add._rings(M):
            record("%s %s" % (closed, " ".join("%d:%d" % e for e in ring)))
        for i in range(len(M.V)):
            record(ints(add.neighbors(M, i)))
            record(ints(add.vertex_faces(M, i)))
            record(pt(add.vertex_normal(M, i)))
        record(pairs(add.edges(M)))
        record(pairs(add.boundary_edges(M)))
        record(lists(add.boundary_loops(M)))
        dump(add.dual(M))
        dump(add.truncate(M, 0.3))
        dump(add.truncate(M, 0.5, "black"))
        dump(add.refine(M))


if __name__ == "__main__":
    import sys
    run(sys.argv)

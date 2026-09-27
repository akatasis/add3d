from parity_case import add, case, record, run, save_case, save_mesh  # noqa: F401
import math


def points(ps):
    """A list of points as lists of floats (so that record() writes them as points)."""
    return [[float(c) for c in p] for p in ps]


def record_faces(F):
    record(len(F))
    for f in F:
        record(" ".join(str(i) for i in f))


def raises(fn, *args):
    """Record whether fn(*args) raises (an exception would end the case)."""
    try:
        fn(*args)
    except Exception:                 # noqa: BLE001
        record("raises")
        return
    record("returns")


# -- the helpers every shape is built with ------------------------------------------

@case
def add_grid_helper():
    P = [[(i, 0.5 * j * j, 0.25 * i * j) for j in range(4)] for i in range(3)]
    M = add.Mesh()
    for wrap_u in (False, True):
        for wrap_v in (False, True):
            for flip in (False, True):
                add._add_grid(M, P, "red" if flip else (10, 20, 30), wrap_u, wrap_v, flip)
    add._add_grid(M, P, lambda i, j: add.hsv(0.1 * i + 0.05 * j), wrap_v=True)
    add._add_grid(M, P, lambda i, j: add.random_color(), flip=True)
    add._add_grid(M, [[(0, 0, 0), (1, 0, 0)]], "blue")                 # one row: no cells
    save_mesh(M)


@case
def add_grid_empty():
    raises(add._add_grid, add.Mesh(), [], "red")


@case
def ring_fan_helpers():
    u, v, w = add._frame((1, 2, 3))
    record(points(add._ring((1, 2, 3), u, v, 1.5, 5)))
    record(points(add._ring((0, 0, 0), (1, 0, 0), (0, 0, 1), 2.0, 3, 0.4)))
    record(points(add._ring((0, 0, 0), u, v, 1.0, 0)))
    M = add.Mesh()
    ring = add._ring((0, 0, 0), (1, 0, 0), (0, 1, 0), 1.0, 6)
    add._fan(M, ring, (0, 0, 1), "red")
    add._fan(M, ring, (0, 0, -1), "blue", flip=True)
    add._fan(M, ring, (0, 0, 2), lambda i: add.hsv(i / 6.0), closed=False)
    add._fan(M, ring, (0, 0, -2), lambda i: add.random_color(), True, False)
    add._fan(M, ring[:1], (0, 0, 3), "gold")
    add._fan(M, [], (0, 0, 3), "gold")
    save_mesh(M)


@case
def volume_helpers():
    M = add.Mesh()
    add._add_grid(M, [add._ring((0, 0, 0), (1, 0, 0), (0, 0, 1), 1.0, 8),
                      add._ring((0, 1, 0), (1, 0, 0), (0, 0, 1), 1.0, 8)], "red", wrap_v=True)
    record(add._signed_volume(M))
    record(add._signed_volume(M, 3))
    record(add._signed_volume(M, 100))
    add._fan(M, add._ring((0, 1, 0), (1, 0, 0), (0, 0, 1), 1.0, 8), (0, 1, 0), "blue")
    add._fan(M, add._ring((0, 0, 0), (1, 0, 0), (0, 0, 1), 1.0, 8), (0, 0, 0), "blue", True)
    M.add_face([0, 1], "gold")                                         # too short to count
    record(add._signed_volume(M))
    add._make_outward(M, 0)
    record(add._signed_volume(M))
    add._make_outward(M, 5)
    save_mesh(M)


@case
def emit_helper():
    M = add.Mesh()
    add._add_grid(M, [add._ring((0, 0, 0), (1, 0, 0), (0, 0, 1), 1.0, 5),
                      add._ring((0, 1, 0), (1, 0, 0), (0, 0, 1), 1.0, 5)], "red", wrap_v=True)
    add._fan(M, add._ring((0, 1, 0), (1, 0, 0), (0, 0, 1), 1.0, 5), (0, 1, 0), "blue")
    add.box([5, 0, 0], 1)
    add._emit(M)
    M2 = add.Mesh()
    M2.add_polygon([[0, 0, 0], [1, 0, 0], [1, 1, 0]], "red")
    M2.add_polygon([[1, 1, 0], [1, 0, 0], [1 + 1e-10, 1, 1]], "red")
    add._emit(M2, 1e-6)
    save_case()


@case
def grid_solid_helper():
    M = add._grid_solid((0, 0, 0), [1, 0.5, 2], [1, 1], [0.5, 0.5, 0.5],
                        lambda i, j, k: (i + j + k) % 2 == 0,
                        lambda i, j, k: add.hsv(i / 3.0 + j / 7.0 + k / 11.0))
    save_mesh(M, "a")
    M = add._grid_solid((1.5, -2, 0.25), [0.3, 0.3], [0.7], [1, 2, 3, 4],
                        lambda i, j, k: not (i == 1 and k == 2), "gold")
    save_mesh(M, "b")
    M = add._grid_solid((0, 0, 0), [], [1], [1], lambda i, j, k: True, None)
    record(len(M.V))
    M = add._grid_solid((0, 0, 0), [1, 1, 1], [1, 1, 1], [1, 1, 1], lambda i, j, k: True,
                        lambda i, j, k: add.random_color())
    save_mesh(M, "c")


# -- flat shapes ---------------------------------------------------------------------

@case
def flat_shapes():
    add.polygon([[0, 0, 0], [1, 0, 0], [1.5, 1, 0], [0.5, 1.7, 0], [-0.5, 1, 0]], "red")
    add.polygon([[0, 0, 1], [1, 0, 1], [0, 1, 1]])
    add.polygon([[0, 0, 1.5], [2, 0, 1.5], [2, 2, 1.5], [1, 0.5, 1.5], [0, 2, 1.5]], "teal")   # not convex
    add.triangle([0, 0, 2], [1, 0, 2], [0, 1, 2.5], (0.2, 0.4, 0.6))
    add.triangle([0, 0, 3], [1, 0, 3], [0, 1, 3])
    add.quad([0, 0, 4], [1, 0, 4], [1, 1, 4.2], [0, 1, 4], "#ff8800")
    add.quad([0, 0, 5], [1, 0, 5], [1, 1, 5], [0, 1, 5], add.transparent("sky", 0.4))
    save_case()


@case
def discs():
    add.disc([0, 0, 0], [0, 1, 0], 1.0)
    add.disc([1, 2, 3], [1, 5, 3], 0.5, 6, "red")                    # facing a second point
    add.disc([1, 1, 1], [1, 1, 1], 0.75, 5, "blue")                   # normal == centre: a direction
    add.disc([4, 0, 0], [4, -1, 0], 1.0, 7)
    add.disc([6, 0, 0], [7, 0, 0], 1.0, 4, "gold")
    add.disc([8, 0, 0], [8, 0, 3], 1.0, 3)
    add.disc([10, 0, 0], [10, 0, 0.5], 0.5, 1)
    add.disc([12, 0, 0], [12, 0, 0.5], 0.5, 2)
    add.disc([0, 5, 0], [0.5, 6, 0.2], 1.25, 9, (1.0, 0.5, 0.0))
    save_case()


@case
def rings():
    add.ring([0, 0, 0], [0, 1, 0], 1.0, 0.5)
    add.ring([3, 0, 0], [3, 0, 1], 1.0, 0.8, 6, "red")
    add.ring([0, 0, 0], [0, 0, 0], 2.0, 1.5, 5, "blue")               # normal == centre: a direction
    add.ring([6, 0, 0], [7, 1, 1], 0.5, 1.0, 4, "gold")               # inner bigger than outer
    add.ring([9, 0, 0], [9, 1, 0], 1.0, 0.0, 3)
    save_case()


def hills(x, z):
    return 0.5 * math.sin(x) * math.cos(0.7 * z)


@case
def grids():
    add.grid([0, 0, 0], [4, 3])
    add.grid([6, 0, 0], [2, 2], 3, 2, "red")
    add.grid([0, 0, 6], [5, 4], 8, 6, "green", hills)
    add.grid([6, 0, 6], [3, 3.5], 5, 7, lambda x, z: "sky" if hills(x, z) < 0 else "white", hills)
    add.grid([12, 1, 0], [1.5, 2.5], 4, 3, lambda x, z: add.hsv(x + z))
    add.grid([12, 0, 6], [2, 2], 2, 2, lambda x, z: add.random_color())
    add.grid([0, -2, 12], [3, 3], 1, 1, (0.5, 0.25, 1.0))
    save_case()


@case
def grids_thick():
    add.grid([0, 0, 0], [4, 3], 4, 3, "red", None, 0.2)
    add.grid([6, 0, 0], [4, 4], 6, 5, lambda x, z: "gold" if x > 6 else "navy", hills, 0.3)
    add.grid([0, 0, 6], [2, 2], 2, 2, "blue", thickness=-0.1)
    save_case()


@case
def grid_empty():
    raises(add.grid, [0, 0, 0], [1, 1], -1, 2)
    save_case()


# -- boxes and other flat-sided solids ------------------------------------------------

@case
def boxes():
    add.box([0, 0, 0], 1)
    add.box([1, 2, 3], 2.5, "red")
    add.cuboid([4, 0, 0], [1, 2, 3])
    add.cuboid([8, 0.5, -1], [0.5, 0.25, 4], "gold")
    add.cuboid([0, 5, 0], [-1, 1, 1], "blue")
    add.polygon([[0, 0, 9], [1, 0, 9], [0, 1, 9]])
    add.box([0, 0, 9], 0.1, (0.1, 0.2, 0.3))
    save_case()


@case
def frames():
    add.frame([0, 0, 0], 2, 0.2, "gold")
    add.frame([3, 1, 0], 1, 0.1)
    add.frame([6, 0, 0], 1.5, 0.5, "red")
    add.frame([9, 0, 0], 1, 0.7, "blue")                              # bars wider than the cube
    save_case()


@case
def voxels_basic():
    add.voxels([(0, 0, 0), (1, 0, 0), (1, 1, 0), (-1, 0, 2), (0, 0, 0)], 0.5, (1, 2, 3), "red")
    blocks = [(x, y, z) for x in range(5) for y in range(3) for z in range(5) if (x + y + z) % 3]
    add.voxels(blocks, 1.0, (0, 5, 0), "sky")
    hollow = [(x, y, z) for x in range(3) for y in range(3) for z in range(3) if (x, y, z) != (1, 1, 1)]
    add.voxels(hollow, 0.25, (8, 0, 0))
    add.voxels([(3, -2, 7)])
    add.voxels([])
    save_case()


@case
def pyramids():
    add.pyramid([0, 0, 0], 2, 3, "red")
    add.pyramid([3, 0, 0], 1, -2)
    add.pyramid([6, 1, 2], 1.5, 0.5, "gold")
    save_case()


@case
def prisms():
    add.prism([[0, 0], [1, 0], [0.5, 1]], 3, "gold")
    add.prism(add.profile_star(5, 1.0, 0.4), 0.5, "red", (4, 0, 0), (1, 1, 0))
    add.prism([[0, 0], [0.5, 1], [1, 0]], 1, "blue", (0, 4, 0))                # clockwise
    add.prism(add.profile_rect(1, 2, 0.3), 2, "teal", (4, 4, 0), (0, 0, 1))
    add.prism(add.profile_circle(0.5, 7), 1.5, None, (8, 0, 0), (1, 0, 0))
    add.prism([[0, 0], [1, 0], [1, 1], [0, 1]], -1, "navy", (8, 4, 0), (0, -1, 0))
    save_case()


# -- the Platonic solids -----------------------------------------------------------------

@case
def polyhedra():
    x = 0
    for name in ("tetrahedron", "tetra", "cube", "hexahedron", "box", "octahedron", "octa",
                 "dodecahedron", "dodeca", "icosahedron", "icosa", "Cube", "ICOSAHEDRON"):
        add.polyhedron(name, [x, 0, 0], 1.0, "red")
        x += 3
    add.polyhedron("dodecahedron")
    add.polyhedron("icosahedron", [0, 4, 0], 2.5)
    add.polyhedron("cube", [4, 4, 0], -1.0, "blue")                 # negative r: turned outward again
    add.tetrahedron()
    add.tetrahedron([0, 8, 0], 0.5, "gold")
    add.octahedron([2, 8, 0], 1.5)
    add.dodecahedron([5, 8, 0], 1.25, "teal")
    add.icosahedron([8, 8, 0], 0.75, (0.3, 0.6, 0.9))
    save_case()


@case
def polyhedron_unknown():
    raises(add.polyhedron, "pentahedron")
    raises(add.polyhedron_points, "")
    raises(add.polyhedron_faces, "cubes")
    raises(add.polyhedron_faces, "cube")


@case
def polyhedron_tables():
    for name in ("tetrahedron", "cube", "octahedron", "dodecahedron", "icosahedron"):
        record(name)
        record(points(add.polyhedron_points(name)))
        record(points(add.polyhedron_points(name, [1, 2, 3], 2.5)))
        record_faces(add.polyhedron_faces(name))
    record(points(add.polyhedron_points("Dodeca", [0.5, 0, 0], 0.1)))
    record_faces(add.polyhedron_faces("ICOSA"))
    record_faces(add._hull_faces([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 1]], 3))
    record_faces(add._hull_faces([[x, y, z] for x in (0, 1) for y in (0, 1) for z in (0, 1)], 4))


@case
def voxels_colour_function():
    add.voxels([(0, 0, 0), (0, 1, 0), (1, 1, 0), (2, 3, 1)], 0.5, (1, 2, 3),
               color=lambda i, j, k: "red" if j else ("gold" if i + k else "blue"))
    save_case()


if __name__ == "__main__":
    import sys
    run(sys.argv)

from parity_case import _current, add, case, record, run, save_case, save_mesh  # noqa: F401
import math


def points(ps):
    """A list of points as lists of floats (so that record() writes them as points)."""
    return [[float(c) for c in p] for p in ps]


def saddle(u, v):
    return [u, u * u - v * v, v]


def torus_uv(u, v):
    return [(2 + 0.5 * math.cos(u)) * math.cos(v), 0.5 * math.sin(u), (2 + 0.5 * math.cos(u)) * math.sin(v)]


def shared_mesh():
    """A small open mesh whose faces share vertices: a triangle, a quad, a pentagon, and an
    edge (0-2) that belongs to three faces."""
    M = add.Mesh()
    for p in [[0, 0, 0], [1, 0, 0], [1, 1, 0.2], [0, 1, 0], [2, 0, 0.3], [2, 1, 0], [0.5, 2, 0.5],
              [1.5, 2.5, 0.1], [2.5, 2, 0]]:
        M.add_vertex(p)
    M.add_face([0, 1, 2], "red")
    M.add_face([0, 2, 3], "blue")
    M.add_face([1, 4, 5, 2], "gold")
    M.add_face([2, 5, 8, 7, 6], (10, 20, 30))
    M.add_face([2, 0, 6], "teal")
    return M


# -- parametric surfaces -------------------------------------------------------------

@case
def parametric_basic():
    add.parametric(saddle, -1, 1, 6, -1, 1, 4)
    add.parametric(saddle, 2, 3, 3, -1, 1, 3, "red", flip=True)
    add.parametric(torus_uv, 0, 2 * math.pi, 12, 0, 2 * math.pi, 16, "gold", True, True)
    add.parametric(torus_uv, 0, 2 * math.pi, 8, 0, 2 * math.pi, 5, "blue", wrap_u=True)
    add.parametric(torus_uv, 0, 2 * math.pi, 5, 0, 2 * math.pi, 7, "teal", wrap_v=True, flip=True)
    add.parametric(saddle, 5, 6, 1, 0, 1, 1, (0.5, 0.5, 0.5))
    add.parametric(saddle, 7, 8, 2, 0, 1, 3, lambda u, v: add.transparent("sky", v))
    save_case()


@case
def parametric_colors():
    add.parametric(saddle, -1, 1, 5, -1, 1, 5, color=lambda u, v: "red" if u * v > 0 else "white")
    add.parametric(saddle, 2, 3, 4, 0, 1, 3, lambda u, v: add.hsv(u + v))
    add.parametric(saddle, 4, 5, 3, 0, 1, 2, None, color="green")
    add.parametric(torus_uv, 0, 2 * math.pi, 6, 0, 2 * math.pi, 4, lambda u, v: add.random_color(), True, True)
    save_case()


@case
def parametric_thick():
    add.parametric(saddle, -1, 1, 4, -1, 1, 4, "red", thickness=0.2)
    add.parametric(saddle, 2, 3, 3, 0, 1, 3, "blue", double_sided=True)
    add.parametric(saddle, 4, 5, 3, 0, 1, 3, "gold", thickness=-0.1, double_sided=True)
    add.parametric(torus_uv, 0, 2 * math.pi, 6, 0, 2 * math.pi, 8, "teal", True, True, thickness=0.1)
    add.parametric(saddle, 6, 7, 2, 0, 1, 2, lambda u, v: add.hsv(v), False, False, True, 0.3)
    save_case()


@case
def parametric_empty():
    try:
        add.parametric(saddle, 0, 1, 0, 0, 1, 3, "red", wrap_u=True)
    except Exception:                 # noqa: BLE001
        record("raises")
    save_case()


# -- two_sided and solidify ------------------------------------------------------------

@case
def two_sided_meshes():
    M = shared_mesh()
    save_mesh(add.two_sided(M), "a")
    add.parametric(saddle, -1, 1, 2, -1, 1, 2, "red")
    save_mesh(add.two_sided(), "scene")
    save_mesh(add.two_sided(add.Mesh()), "empty")
    save_case()


@case
def two_sided_textured():
    M = add.Mesh()
    for p in [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [2, 0, 0], [2, 1, 0]]:
        M.add_vertex(p)
    M.add_face([0, 1, 2, 3], (255, 255, 255, 1.0, "wood.png"), [(0, 0), (1, 0), (1, 1), (0, 1)])
    M.add_face([1, 4, 2], "red")
    M.add_face([4, 5, 2], (255, 255, 255, 1.0, "wood.png"), [(0.5, 0.25), (1, 0.125), (0.75, 1)])
    out = add.two_sided(M)
    add.obj(_current[0] + ".obj", out)
    save_mesh(out)


@case
def solidify_meshes():
    M = shared_mesh()
    save_mesh(add.solidify(M), "a")
    save_mesh(add.solidify(M, 0.3, False), "b")
    save_mesh(add.solidify(M, -0.2), "c")
    add.box([0, 0, 0], 1)                                               # closed: no border wall
    save_mesh(add.solidify(), "scene")
    Z = add.Mesh()                                                      # a face with no area
    for p in [[0, 0, 0], [1, 0, 0], [2, 0, 0]]:
        Z.add_vertex(p)
    Z.add_face([0, 1, 2], "red")
    Z.add_vertex([5, 5, 5])                                             # a vertex of no face
    save_mesh(add.solidify(Z, 0.5), "flat")
    save_case()


# -- sweeps, curves, extrusions, lofts, ribbons -------------------------------------------

square = [[-0.5, -0.5], [0.5, -0.5], [0.5, 0.5], [-0.5, 0.5]]
tri = [[0.0, 0.0], [0.4, 0.0], [0.0, 0.3]]


@case
def sweeps():
    add.sweep(square, lambda t: [0, t, 0], 0, 3, 6, "orange")
    add.sweep(square, lambda t: [2 + math.cos(t), math.sin(t), 0.3 * t], 0, 4, 12, "red",
              scale=lambda t: 1 - 0.5 * t, twist=math.pi)
    add.sweep(tri, lambda t: [math.cos(t) * 3, 0, math.sin(t) * 3 + 8], 0, 2 * math.pi, 16, "blue", closed=True)
    add.sweep(square, lambda t: [t, 0, 5], 0, 1, 3, "gold", scale=2, twist=lambda t: t * t, caps=False)
    add.sweep(tri, lambda t: [t, t * t, -3], -1, 1, 5, closed=True, twist=1.5)
    add.sweep(square, lambda t: [5, t, t * t], 0, 2, 4, "teal", scale=0.5)
    add.sweep(tri, lambda t: [9, 0, 0], 0, 1, 2, "red")                  # the path stands still
    add.sweep(tri, lambda t: [math.sin(3 * t), t, -6])
    save_case()


@case
def sweep_colors():
    add.sweep(square, lambda t: [0, t, 0], 0, 3, 5, lambda t, j: add.hsv(t / 3.0 + j / 8.0))
    add.sweep(tri, lambda t: [2, t, math.sin(t)], 0, 2, 4, lambda t, j: "black" if j < 0 else "white")
    add.sweep(square, lambda t: [4 + math.cos(t), 0, math.sin(t)], 0, 2 * math.pi, 6,
              lambda t, j: add.random_color(), True)
    add.sweep(tri, lambda t: [7, t, 0], 0, 1, 3, lambda t, j: add.random_color(), caps=False)
    save_case()


@case
def sweep_empty():
    try:
        add.sweep(square, lambda t: [0, t, 0], 0, 1, 0, "red", True)
    except Exception:                 # noqa: BLE001
        record("raises")
    save_case()


@case
def curves():
    add.curve(lambda t: [math.cos(t), t / 4.0, math.sin(t)], 0, 2 * math.pi, 30)
    add.curve(lambda t: [t, math.sin(t), 0], 0, 3, 12, 6, 0.2, "red")
    add.curve(lambda t: [3 + math.cos(t), 0, math.sin(t)], 0, 2 * math.pi, 16, 8, 0.1, "blue", True)
    add.curve(lambda t: [t, 2, 0], 0, 2, 5, 5, lambda t: 0.1 + 0.1 * t,
              color=lambda t, a: "red" if (t + a) % 1.0 < 0.5 else "white")
    add.curve(lambda t: [t, 3, math.cos(t)], 0, 2, 4, 4, 0.2, lambda t, a: add.random_color())
    add.curve(lambda t: [6 + math.cos(t), 3, math.sin(t)], 0, 2 * math.pi, 6, 3, lambda t: 0.1 + 0.02 * t,
              lambda t, a: add.random_color(), True)
    add.curve(lambda t: [t, 5, 0], 0, 1, 1, 3, 0.1, None, color="gold")
    save_case()


@case
def extrusions():
    star = add.profile_star(5, 1.0, 0.45)
    add.extrude(star, [0, 4, 0], "gold", steps=20, twist=math.pi, scale=lambda t: 1 - 0.6 * t)
    add.extrude(square, [1, 1, 0], "red", center=(4, 0, 0))
    add.extrude(square, [0, 0, 2], "blue", 0, center=(8, 0, 0))
    add.extrude(square, [0, 2, 0], "teal", 3, lambda t: 2 * t, 0.5, (12, 0, 0), False)
    add.extrude(square, [0, 2, 0], lambda t, j: "red" if j == 1 else ("white" if j >= 0 else "black"), 4,
                center=(16, 0, 0))
    add.extrude(tri)
    add.extrude(tri, [0, -1, 0], "navy", 2, 0.5, 2.0, (0, 0, 5))
    save_case()


def section(y, r, k=6, phase=0.0):
    return [[math.cos(2 * math.pi * i / k + phase) * r, y, math.sin(2 * math.pi * i / k + phase) * r]
            for i in range(k)]


@case
def lofts():
    add.loft([section(0, 1.0), section(1, 0.6), section(2, 0.9)], "teal")
    add.loft([[[p[0] + 4, p[1], p[2]] for p in section(y, 0.5 + 0.1 * y)] for y in range(4)], "red", closed=True)
    add.loft([[[p[0] + 8, p[1], p[2]] for p in section(y, 0.7, 5, 0.2 * y)] for y in range(3)], "blue", caps=False)
    add.loft([[[p[0], p[1], p[2] + 4] for p in section(y, 0.8, 4)] for y in range(3)], "gold", flip=True)
    add.loft([section(0, 1.0, 3), section(-1, 1.0, 3)])
    save_case()


@case
def loft_empty():
    try:
        add.loft([], "red")
    except Exception:                 # noqa: BLE001
        record("raises")
    save_case()


@case
def ribbons():
    add.ribbon(lambda t: [math.cos(t) * 2, 0.2 * t, math.sin(t) * 2], 0, 2 * math.pi, 24, 0.5)
    add.ribbon(lambda t: [t, 0, 3], 0, 4, 8, 0.3, "red", twist=math.pi)
    add.ribbon(lambda t: [math.cos(t) * 2 + 6, 0, math.sin(t) * 2], 0, 2 * math.pi, 20, 0.4, "blue", closed=True,
               twist=lambda t: 2 * math.pi * t)
    add.ribbon(lambda t: [t, 1, 6], 0, 3, 6, 0.5, "gold", thickness=0.1)
    add.ribbon(lambda t: [math.cos(t) + 10, math.sin(t), 0], 0, 2 * math.pi, 12, 0.2, "teal", True, None, -0.05)
    save_case()


@case
def circles():
    add.circle([0, 0, 0], [0, 1, 0], 1.0)
    add.circle([2, 0, 0], [3, 1, 0], 0.5, 6, "red")
    add.circle([4, 0, 0], [0, 0, 0], 0.5, 5, None, "blue")
    add.circle([6, 0, 0], [6, 0, 0], 0.5, 3, (0.1, 0.2, 0.3))
    save_case()


# -- the helpers -------------------------------------------------------------------

@case
def surface_helpers():
    M = shared_mesh()
    record(points(add._vertex_normals(M)))
    for f in M.F:
        record(list(add._face_normal(M, f)))
    record(list(add._face_normal(M, [])))
    for (a, b), c in add._boundary_edges(M).items():
        record("%d %d" % (a, b))
        record(c)
    Z = add.Mesh()
    Z.add_vertex([0, 0, 0])
    Z.add_vertex([1, 1, 1])
    Z.add_face([0, 1], "red")
    record(points(add._vertex_normals(Z)))
    record(len(add._boundary_edges(Z)))


@case
def rmf_and_sweep_profile():
    path = [[0, 0, 0], [1, 0, 0], [2, 1, 0], [2, 2, 1], [2, 2, 1], [1, 3, 2], [0, 3, 2]]
    T, N = add._rmf(path)
    record(points(T))
    record(points(N))
    T2, N2 = add._rmf(path, True)
    record(points(T2))
    record(points(N2))
    T3, N3 = add._rmf([[1, 2, 3]])
    record(points(T3))
    record(points(N3))
    T4, N4 = add._rmf([[1, 2, 3], [1, 2, 3], [1, 2, 4]], True)
    record(points(T4))
    record(points(N4))
    for scale, twist in ((None, None), (2.0, None), (lambda t: 1 + t, 0.5), (0.5, lambda t: t * t)):
        P = add._sweep_profile(path, T, N, [[1, 0], [0, 1], [-1, -0.5]], scale, twist)
        for row in P:
            record(points(row))
    P = add._sweep_profile([[0, 0, 0]], [(0.0, 0.0, 1.0)], [(1.0, 0.0, 0.0)], [[1, 2]], None, 3.0)
    record(points(P[0]))
    try:
        add._rmf([])
    except Exception:                 # noqa: BLE001
        record("raises")


if __name__ == "__main__":
    import sys
    run(sys.argv)

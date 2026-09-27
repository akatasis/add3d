"""Parity cases for _src/45_place.py: aim, ground, align, random_points,
scatter, along (see cases_45_place.cpp)."""
import math

from parity_case import add, case, record, run, save_mesh  # noqa: F401

SIX = ["red", (10, 200, 30), add.transparent("sky", 0.4), "#123456", (250, 250, 5), "navy"]


def cube(lo=(-0.5, -0.25, -0.75), hi=(0.5, 0.75, 1.25), colors=None):
    M = add.Mesh()
    for k in range(8):
        M.add_vertex([hi[0] if k & 1 else lo[0], hi[1] if k & 2 else lo[1], hi[2] if k & 4 else lo[2]])
    for i, f in enumerate([[0, 4, 6, 2], [1, 3, 7, 5], [0, 1, 5, 4], [2, 6, 7, 3], [0, 2, 3, 1], [4, 5, 7, 6]]):
        M.add_face(f, colors[i] if colors else None)
    return M


def path(t):
    return [3 * math.cos(t), t, 3 * math.sin(t)]


@case
def p_aim():
    M = cube(colors=SIX)
    save_mesh(add.aim(M, [1, 1, 0]), "diag")
    save_mesh(add.aim(M, [0, 3, 0]), "same")
    save_mesh(add.aim(M, [0, -2, 0]), "opposite")
    save_mesh(add.aim(M, [0, 0, 1], [1, 0, 0], [0.5, 0.5, 0.5]), "pivot")
    save_mesh(add.aim(M, [1e-13, -1, 0]), "nearly_opposite")
    save_mesh(add.aim(M, [1, 0, 0], [1, 0, 0]), "x_x")
    save_mesh(add.aim(M, [-1, 0, 0], [1, 0, 0], [1, 1, 1]), "x_minus_x")
    save_mesh(add.aim(M, [0, 0, 0]), "zero")
    save_mesh(add.aim(M, add.direction([1, 2, 3], [-2, 0.5, 4]), [0, 0, 1], [1, 2, 3]), "direction")


@case
def p_ground_align():
    M = cube(colors=SIX)
    save_mesh(add.ground(M), "ground")
    save_mesh(add.ground(M, 2.5), "ground_y")
    save_mesh(add.align(M), "align")
    save_mesh(add.align(M, [5, 0, 5]), "align_at")
    save_mesh(add.align(M, [1, 2, 3], [-1, -1, -1]), "corner")
    save_mesh(add.align(M, [1, 2, 3], [1, 0, 1]), "max")
    save_mesh(add.align(M, [0, 0, 0], [0.5, -0.5, 0]), "fractions")
    save_mesh(add.ground(add.Mesh()), "empty")


@case
def p_random_points():
    record(add.random_points(4, [-1, 0, -2], [1, 1, 2], 1))
    record(add.random_points(3, [0, 0, 0], [10, 5, 10]))
    record(add.random_points(3, [-5, 0, -5], [5, 0, 5], 2, lambda x, z: math.sin(x) * math.cos(z)))
    record(add.random_points(0, [0, 0, 0], [1, 1, 1], 3))
    record(add.random_points(2, [1, 1, 1], [0, 0, 0], 0))
    record(add.random_points(2, [1, 1, 1], [3, 3, 3], -7))
    record(add.random())


@case
def p_scatter():
    M = cube(colors=SIX)
    pts = [[0, 0, 0], [3, 0, 1], [-2, 1, 4]]
    save_mesh(add.scatter(M, pts, 5), "seed")
    save_mesh(add.scatter(M, pts, 5, False, (0.5, 1.5)), "nospin")
    save_mesh(add.scatter(M, pts, None, True, (0.8, 1.2), [1, 0, 0]), "global")
    save_mesh(add.scatter(M, pts, 9, True, (1.0, 1.0)), "scale1")
    save_mesh(add.scatter(M, [], 9), "none")
    spots = add.random_points(5, [-10, 0, -10], [10, 0, 10], 1, lambda x, z: 0.1 * x * z)
    save_mesh(add.scatter(M, spots, 1, True, (0.7, 1.3)), "forest")
    record(add.random())


@case
def p_along():
    M = cube(colors=SIX)
    save_mesh(add.along(M, path, 6, 0, math.pi), "fn")
    save_mesh(add.along(M, path, 6, 0, 2 * math.pi, [1, 0, 0], True), "closed")
    save_mesh(add.along(M, path, 5, 0, 1, None), "upright")
    save_mesh(add.along(M, path, 4, 0, 2, [0, 1, 0], False, 0.5), "scale")
    save_mesh(add.along(M, path, 4, 0, 2, [0, 1, 0], False, lambda t: 1 + t), "scale_fn")
    save_mesh(add.along(M, path, 4, -1, 2, None, True, lambda t: 0.5 + t * t), "upright_scale_fn")
    save_mesh(add.along(M, path, 1), "one")
    save_mesh(add.along(M, path, 0), "zero")
    save_mesh(add.along(M, path, 3, 1, 1), "same_t")
    pts = [[0, 0, 0], [2, 0, 0], [2, 2, 0], [0, 2, 1]]
    save_mesh(add.along(M, pts, 0), "list")
    save_mesh(add.along(M, pts, 99, 5, 7, [0, 0, 1], True, 0.5), "list_closed")
    save_mesh(add.along(M, pts, 0, 0, 1, None, False, lambda t: 2 - t), "list_upright")
    save_mesh(add.along(M, [[0, 0, 0], [0, 0, 0], [1, 0, 0]], 0), "list_repeat")
    save_mesh(add.along(M, [[1, 2, 3]], 0), "list_one")
    save_mesh(add.along(M, [], 0), "list_empty")


@case
def p_along_calls():
    """The path is called in add.py's order: every point, then t + h and t - h."""
    calls = []

    def traced(t):
        calls.append(t)
        return [t, t * t, 1.0]
    add.along(cube(), traced, 3, 0.5, 1.5)
    record(calls)


@case
def p_random():
    M = cube(colors=SIX)
    for seed in range(10):
        r = add.Random(seed)
        pts = []
        for _ in range(r.randint(1, 7)):
            x = r.uniform(-3, 3)
            y = r.uniform(-3, 3)
            z = r.uniform(-3, 3)
            pts.append([x, y, z])
        closed = r.randint(0, 1) == 1
        ax = [r.uniform(-1, 1), r.uniform(-1, 1), r.uniform(-1, 1)]
        save_mesh(add.along(M, pts, 0, 0, 1, ax, closed, r.uniform(0.5, 1.5)), "along%d" % seed)
        d = [r.uniform(-1, 1), r.uniform(-1, 1), r.uniform(-1, 1)]
        save_mesh(add.aim(M, d, ax, pts[0]), "aim%d" % seed)
        save_mesh(add.aim(M, [-c for c in ax], ax), "aim_back%d" % seed)
        save_mesh(add.align(M, pts[-1], [r.randint(-1, 1), r.randint(-1, 1), r.randint(-1, 1)]), "align%d" % seed)
        save_mesh(add.scatter(M, pts, seed, r.randint(0, 1) == 1, (0.5, 2.0), ax), "scatter%d" % seed)


if __name__ == "__main__":
    import sys
    run(sys.argv)

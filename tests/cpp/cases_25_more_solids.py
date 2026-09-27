from parity_case import add, case, record, run, save_case, save_mesh  # noqa: F401
import math
import random


def points(ps):
    """A list of points as lists of floats (so that record() writes them as points)."""
    return [[float(c) for c in p] for p in ps]


def raises(fn, *args):
    """Record whether fn(*args) raises (an exception would end the case)."""
    try:
        fn(*args)
    except Exception:                 # noqa: BLE001
        record("raises")
        return
    record("returns")


def shift(pts, dx, dy, dz):
    return [[p[0] + dx, p[1] + dy, p[2] + dz] for p in pts]


def lorenz(p):
    x, y, z = p
    return [10 * (y - x), x * (28 - z) - y, x * y - 8.0 / 3 * z]


# -- the helpers -------------------------------------------------------------------------

@case
def ground_frames():
    for d, up in (((1, 0, 0), (0, 1, 0)), ((0, 0, 2), (0, 1, 0)), ((1, 2, 3), (0, 1, 0)),
                  ((0, 1, 0), (0, 1, 0)), ((0, -3, 0), (0, 1, 0)), ((0, 0, 0), (0, 1, 0)),
                  ((1, 1, 0), (0, 0, 1)), ((2, 0, 0), (1, 0, 0)), ((1, 0, 0), (0, 0, 0)),
                  ((1, 0, 0), (0, 5, 1))):
        for vec in add._ground_frame(d, up):
            record([float(c) for c in vec])
    for vec in add._ground_frame((0.3, -0.2, 0.9)):
        record([float(c) for c in vec])


@case
def local_meshes():
    add.box([0.5, 0.25, -1], 1, "red")
    add.cuboid([2, 0, 0], [1, 2, 0.5], "blue")
    M = add.layer()
    w, up, side = add._ground_frame((1, 0, 1))
    save_mesh(add._local_mesh(M, (1, 2, 3), w, up, side), "a")
    save_mesh(add._local_mesh(M, (0, 0, 0), (0, 0, 1), (1, 0, 0), (0, 1, 0)), "b")
    save_mesh(add._local_mesh(M, (-1, 0.5, 2), (0.5, 0.1, 0), (0, 2, 0), (0.3, 0, -1)), "c")


@case
def hollow_prisms():
    outer = add.profile_gear(8, 1.0)
    inner = add.profile_circle(0.4, len(outer))
    save_mesh(add._hollow_prism(outer, inner, 0.5, "red"), "a")
    save_mesh(add._hollow_prism(outer, inner, 0.3, "blue", (1, 2, 3), (1, 1, 0)), "b")
    save_mesh(add._hollow_prism(add.profile_rect(2, 1), add.profile_rect(1, 0.5), -1.0, None, (0, 0, 0), (0, 0, 1)),
              "c")
    save_mesh(add._hollow_prism(add.profile_circle(1.0, 6), add.profile_circle(0.5, 6), 1.0, (10, 20, 30),
                                (0, 0, 0), (0, -1, 0)), "d")


@case
def tube_along_helper():
    pts = [(0, 0, 0), (1, 0, 0), (1.5, 1, 0), (1.5, 1, 1)]
    save_mesh(add._tube_along(pts, [0.1, 0.2, 0.15, 0.1], 6, "red", False), "open")
    save_mesh(add._tube_along(pts, [0.1, 0.1, 0.1, 0.1], 5, "blue", True), "closed")
    save_mesh(add._tube_along(pts, [0.2, 0.1, 0.1, 0.05], 4, lambda i, j: add.hsv(0.1 * i + 0.2 * j), False,
                              lambda j: "gold", lambda j: add.hsv(j / 4.0)), "painted")


@case
def set_order_helper():
    special = [[-1, -2, 0, 7, 15, 8, 16, 24, -1], list(range(100, 0, -1)), [0] * 5, [5, 37, 69, 101],
               [], [2 ** 40, 3, 2 ** 40 + 3, 8], list(range(0, 400, 7)) + list(range(3, 300, 5))]
    rnd = random.Random(3)
    for trial in range(60):
        n = rnd.randint(0, 150)
        hi = rnd.choice([5, 30, 200, 5000, 10 ** 9])
        lo = rnd.choice([0, 0, -3, -100])
        special.append([rnd.randint(lo, hi) for _ in range(n)])
    for added in special:
        s = set()
        for x in added:
            s.add(x)
        record(" ".join(str(x) for x in added))
        record(" ".join(str(x) for x in s))


# -- beams, boxes, arches, stairs --------------------------------------------------------------

@case
def beams():
    add.beam([0, 0, 0], [4, 3, 1], 0.3, 0.5, "brown")
    add.beam([0, 0, 2], [3, 0, 2], 0.2)
    add.beam([0, 0, 4], [0, 3, 4], 0.25, None, "red")                   # straight up
    add.beam([2, 0, 4], [2, -2, 4], 0.25, 0.1, "blue")                  # straight down
    add.beam([5, 0, 0], [5, 1, 3], 0.4, "gold")                         # the colour in the height's place
    add.beam([5, 0, 4], [6, 2, 3], 0.2, (255, 0, 128))
    add.beam([6, 0, 0], [9, 1, 0], 0.3, 0.6, "teal", (1, 0, 0))         # up along the beam
    add.beam([6, 2, 0], [9, 2, 1], 0.3, 0.2, "navy", (0, 0, 1))
    add.beam([0, 5, 0], [2, 6, -1], 0.3, "green", up=(0, 0, 1))
    add.beam([10, 0, 0], [10, 0, 0], 0.5, 0.5, "red")                   # A == B
    add.beam([10, 2, 0], [12, 2, 0], 1, 2, (0.5, 0.25, 1.0))
    save_case()


@case
def rounded_boxes():
    add.rounded_box([0, 0, 0], [2, 1, 1.5], 0.2)
    add.rounded_box([3, 0, 0], 1.5, 0.3, 4, "red")                    # a number: a cube
    add.rounded_box([6, 0, 0], [1, 2, 3], 5.0, 3, "blue")             # r larger than half the smallest side
    add.rounded_box([0, 3, 0], [1, 1, 1], 0.0, 2, "gold")             # r = 0: a sharp box
    add.rounded_box([3, 3, 0], [2, 0.5, 1], 0.1, 1, "teal")           # k = 1
    add.rounded_box([6, 3, 0], [1, 1, 2], 0.25, 5, (0.2, 0.4, 0.6))
    add.rounded_box([0, 6, 0], [1, 1, 1], 0.5, 6, "navy")              # r = half: a ball
    add.rounded_box([3, 6, 0], [-1, 1, 1], 0.2, 3)                    # a negative size
    save_case()


@case
def rounded_box_bad():
    raises(add.rounded_box, [0, 0, 0], [1, 1, 1], 0.2, 0)
    raises(add.rounded_box, [0, 0, 0], [1, 1, 1], 0.2, -1)
    save_case()


@case
def hemispheres():
    add.hemisphere([0, 0, 0], 1.0)
    add.hemisphere([3, 0, 0], 0.5, 4, "red")
    add.hemisphere([6, 0, 0], 0.8, 6, "blue", (0, -1, 0))              # a bowl
    add.hemisphere([0, 3, 0], 0.7, 5, "gold", (1, 1, 0))
    add.hemisphere([3, 3, 0], 1.0, 3, lambda t, a: add.hsv(a / 6.0))
    add.hemisphere([6, 3, 0], 0.5, 2, None, (0, 0, 2))
    add.hemisphere([9, 3, 0], 0.5, 4, lambda t, a: "white" if t > 1.0 else "red")
    save_case()


@case
def arches():
    add.arch([0, 0, 0], [4, 0, 0], 2.0, 0.2)
    add.arch([0, 0, 2], [3, 0, 2], 3.0, 0.15, "red", 16, 6)
    add.arch([5, 0, 0], [5, 0, 4], 1.0, [0.4, 0.2], "blue", 8)
    add.arch([0, 0, 6], [2, 1, 7], 1.5, (0.3, 0.1), "gold", 12, 5, (0, 0, 1))
    add.arch([8, 0, 0], [10, 0, 0], 1.0, 0.1, (0.5, 0.2, 0.9), 4, 3, (1, 1, 0))
    add.arch([8, 0, 4], [11, 0, 4], 1.5, 0.2, None, 1, 4)
    save_case()


@case
def arch_bad():
    raises(add.arch, [0, 0, 0], [4, 0, 0], 2.0, 0.2, "red", 0)
    raises(add.arch, [0, 0, 0], [4, 0, 0], 2.0, 0.2, "red", -1)
    save_case()


@case
def stairs_case():
    add.stairs([0, 0, 0], 5, 1.0, 0.2, 0.3)
    add.stairs([3, 0, 0], 3, 2.0, 0.5, 0.5, "red", (0, 0, 1))
    add.stairs([0, 0, 4], 4, 1.5, 0.25, 0.4, "blue", (1, 0, 1))
    add.stairs([6, 0, 0], 2, 1.0, 0.3, 0.3, "gold", (-1, 0, 0))
    add.stairs([0, 3, 0], 3, 1.0, 0.2, 0.2, "teal", (0, 1, 0))         # straight up
    add.stairs([6, 3, 0], 1, 0.5, 1.0, 1.0)
    add.stairs([9, 3, 0], 0, 1.0, 0.2, 0.3)                            # no steps
    add.stairs([9, 0, 0], -2, 1.0, 0.2, 0.3)
    add.stairs([0, 6, 0], 3, 1.0, 0.3, 0.3, "navy", (1, -0.5, 0))
    save_case()


# -- machine parts and buildings ------------------------------------------------------------------

@case
def gears():
    add.gear([0, 0, 0], 12, 1.0, 0.3)
    add.gear([3, 0, 0], 8, 0.8, 0.2, "gold", 0.3)
    add.gear([6, 0, 0], 10, 1.0, 0.25, "red", None, 0.4)
    add.gear([0, 3, 0], 6, 0.5, 0.2, "blue", 0.1, 0.2, (0, 0, 1))
    add.gear([3, 3, 0], 16, 1.2, 0.1, "silver", None, 1e-10)          # a hole below EPS: none
    add.gear([6, 3, 0], 3, 0.6, 0.4, (0.3, 0.3, 0.3), 0.2, 0.3, (1, 1, 1))
    add.gear([9, 3, 0], 12, 1.0, -0.3, "teal", None, 0.5)             # a negative thickness
    save_case()


@case
def gear_no_teeth():
    # (two faces without corners: counted, not written -- see the report on empty OFF faces)
    add.gear([9, 0, 0], 0, 1.0, 0.3, "red")
    M = add.layer()
    record(len(M.V))
    record(" ".join(str(len(f)) for f in M.F))
    add.gear([9, 0, 0], 0, 1.0, 0.3, "red", None, 0.5)
    M = add.layer()
    record(len(M.V))
    record(" ".join(str(len(f)) for f in M.F))


@case
def wheels():
    add.wheel([0, 0, 0], 1.0, 0.3)
    add.wheel([3, 0, 0], 0.8, 0.4, "red", (1, 0, 0), 12)
    add.wheel([6, 0, 0], 1.0, 0.2, "black", (0, 0, 1), 24, 6)
    add.wheel([0, 3, 0], 0.7, 0.3, "blue", (0, 1, 0), 8, 3, "gold")
    add.wheel([3, 3, 0], 1.0, 0.25, "navy", (1, 1, 0), 30, 5, (200, 200, 200))
    add.wheel([6, 3, 0], 0.5, 0.2, "teal", (0, 0, 1), 5, 0, "red")    # k // 2 < 8
    add.wheel([9, 3, 0], 0.4, 1.0, "red", (0, 0, 1), 16, 4)           # the tyre wider than the wheel
    save_case()


@case
def roofs():
    add.roof([0, 0, 0], [4, 6], 2)
    add.roof([6, 1, 0], [3, 3], 1.5, "red", 0.3)
    add.roof([0, 3, 6], [2.5, 4], 0.8, (0.6, 0.2, 0.1), -0.2)
    save_case()


@case
def columns():
    add.column([0, 0, 0], 3.0, 0.3)
    add.column([2, 0, 0], 2.0, 0.25, "white", 12)
    add.column([4, 0, 0], 2.5, 0.2, "gold", 8, False)
    add.column([6, 1, 2], 1.0, 0.5, None, 5, True)
    save_case()


@case
def bricks_plain():
    add.bricks([0, 0, 0], 4.0, 2.0)
    add.bricks([0, 0, 3], 3.3, 1.2, [0.8, 0.3, 0.4], "red", (1, 0, 0), 0.02)
    save_case()


@case
def bricks_seeded():
    add.bricks([0, 0, 0], 5.0, 1.5, [1.0, 0.5, 0.5], "brown", (1, 0, 0), 0.05, 7)
    add.bricks([0, 0, 3], 2.0, 1.0, [0.5, 0.25, 0.3], (200, 100, 50), (0, 0, 1), 0.03, 1)
    add.bricks([0, 3, 0], 2.0, 1.0, [0.5, 0.25, 0.3], "gold", (1, 0, 0), 0.03, 0)
    add.bricks([0, 5, 0], 2.0, 1.0, [0.5, 0.25, 0.3], "red", (1, 0, 0), 0.03, -12)
    save_case()


@case
def bricks_colors():
    add.bricks([0, 0, 0], 4.0, 2.0, [1.0, 0.5, 0.5], lambda i, j: "red" if (i + j) % 2 else "white")
    add.bricks([0, 3, 0], 3.0, 1.0, [0.6, 0.3, 0.3], lambda i, j: add.hsv(i / 7.0 + j / 3.0), (1, 0, 1), 0.04, 5)
    add.bricks([0, 6, 0], 2.0, 1.0, [0.5, 0.5, 0.5], lambda i, j: add.random_color())
    save_case()


@case
def bricks_directions():
    add.bricks([1, 2, 3], 2.0, 1.0, [0.5, 0.5, 0.5], "brown", (0, 0, -1))
    add.bricks([0, 0, 0], 2.0, 1.0, [0.5, 0.5, 0.5], "gold", (0, 1, 0))          # straight up
    add.bricks([5, 0, 0], 2.0, 0.2, [0.5, 0.5, 0.5], "red")                     # int(0.2 / 0.5 + 0.5) = 0 rows
    add.bricks([5, 0, 5], 0.0, 1.0)                                             # no length
    add.bricks([8, 0, 0], 1.7, 0.74, [0.5, 0.25, 0.25], "teal", (1, 0, 0), 0.1) # 3.46 rows -> 3
    add.bricks([8, 0, 4], 1.0, 0.5, [0.3, 0.5, 0.2], "navy", (1, 0, 0), 0.4)    # gaps wider than half a brick
    add.bricks([8, 3, 4], 2.0, -1.0, [0.5, 0.5, 0.5], "red")                    # negative height
    save_case()


@case
def bricks_bad():
    raises(add.bricks, [0, 0, 0], 2.0, 1.0, [0.5, 0.0, 0.5])
    raises(add.bricks, [0, 0, 0], 2.0, float("nan"), [0.5, 0.5, 0.5])
    raises(add.bricks, [0, 0, 0], 2.0, float("inf"), [0.5, 0.5, 0.5])
    save_case()


@case
def trees_round():
    add.tree([0, 0, 0], 3)
    add.tree([4, 0, 0], 2.5, "brown", "green", "round", 12, 1)
    add.tree([8, 0, 0], 3, "brown", "lime", "round", 6, 2)
    add.tree([0, 0, 4], 2, "brown", "green", "oak", 9)                 # any other kind: round
    add.tree([4, 0, 4], 2, (90, 60, 30), "teal", "round", 30, 0)
    add.tree([8, 0, 4], 1.5, "brown", "green", "round", -4, -3)
    save_case()


@case
def trees_pine():
    add.tree([0, 0, 0], 4, "brown", "green", "pine")
    add.tree([4, 0, 0], 3, (100, 50, 0), "teal", "pine", 6, 3)
    add.tree([8, 0, 0], 2.5, "brown", "green", "pine", 0, 11)
    save_case()


@case
def trees_palm():
    add.tree([0, 0, 0], 4, "brown", "green", "palm")
    add.tree([4, 0, 0], 3, "brown", "lime", "palm", 10, 5)
    add.tree([8, 1, 2], 2, "gold", "green", "palm", 4, 99)
    save_case()


# -- pixels and height maps ------------------------------------------------------------------------

@case
def palette_table():
    for key in sorted(add.PALETTE):
        record(key)
        record(add.rgb(add.PALETTE[key]))


HEART = [".r.r.", "rrrrr", ".rrr.", "..r.."]


@case
def pixels_basic():
    add.pixels(HEART, 0.5)
    add.pixels(["#kw", "rgb", "yop", "cmn", "slt", "vdi", "a.x"], 1.0, (5, 0, 0))   # every colour, one unknown
    add.pixels(["ab", "", "a  b"], 0.25, (0, 5, 0), None, 3)
    add.pixels(["rr", "r"], 1.0, (0, 0, 5), None, 2, "gold")
    save_case()


@case
def pixels_colors():
    add.pixels(["xyx", "yzy"], 1.0, (0, 0, 0), {"x": "red", "y": (0, 0, 255)})
    add.pixels(["█▓█", "▓ ▓", "ąčę"], 0.5, (5, 0, 0), {"█": "black", "▓": "grey", "č": "red"}, 1, "sky")
    add.pixels(["ab.c"], 2.0, (0, 5, 0), {}, 1)
    add.pixels(["rgb"], 1.0, (0, 0, 5), None, 0)                      # depth 0: nothing
    add.pixels(["", " ", ". ."], 1.0)                                  # nothing filled
    save_case()


@case
def pixels_bad():
    raises(add.pixels, [])
    save_case()


@case
def heightmaps():
    H = [[int(3 + 2 * math.sin(i / 3.0) * math.cos(j / 3.0)) for j in range(8)] for i in range(6)]
    add.heightmap(H, 0.5)
    add.heightmap([[1, 2, 3], [0, 1, 2]], 1.0, (5, 0, 0), lambda i, j, k: "sky" if j < 1 else "green")
    add.heightmap([[0.5, 1.5, 2.5], [3.49, -1, 2.51]], 0.25, (0, 0, 5), "red")    # halves go to even
    add.heightmap([[0, 0], [0, -2]], 1.0, (5, 0, 5))                              # nothing
    add.heightmap([[2, 2, 2, 7]], 0.3, (9, 0, 0), lambda i, j, k: add.hsv(j / 7.0))
    add.heightmap([[1, 2], [2, 3, 4, 5]], 1.0, (0, 5, 0))            # rows longer than the first: cut
    save_case()


@case
def heightmap_bad():
    raises(add.heightmap, [])
    raises(add.heightmap, [[1, 2], []])
    raises(add.heightmap, [[1, 2], [3]])                              # a row shorter than the first
    raises(add.heightmap, [[1, 2, 3], [2, float("nan"), 1]])
    raises(add.heightmap, [[float("inf")]])
    save_case()


# -- tubes through points ----------------------------------------------------------------------------

PTS = [[0, 0, 0], [1, 0.5, 0], [2, 0, 0.5], [3, 1, 1], [3, 2, 0]]


@case
def polylines():
    add.polyline(PTS)
    add.polyline(shift(PTS, 0, 3, 0), 0.2, 8, "red")
    add.polyline(shift(PTS, 5, 0, 0), lambda t: 0.05 + 0.2 * t, 6, "blue")
    add.polyline(shift(PTS, 0, 0, 4), 0.1, 5, "gold", True)                     # closed
    add.polyline(shift(PTS, 5, 3, 0), 0.15, 7, "teal", False, 2)                # smooth
    add.polyline(shift(PTS, 0, 6, 0), 0.1, 6, "navy", True, 1)                  # closed and smooth
    add.polyline([[0, 0, 8], [1, 0, 8]], 0.1, 3)
    add.polyline([[0, 0, 9]], 0.1)                                              # one point: nothing
    add.polyline([], 0.1)
    add.polyline([[0, 0, 10], [0, 0, 10], [1, 0, 10], [1, 0, 10], [1, 1, 10]], 0.1, 4, "red")   # repeats
    add.polyline([[5, 5, 5], [6, 5, 5], [6, 6, 5]], 0.1, 4, "blue", False, -1)  # smooth < 0: none
    save_case()


@case
def polyline_colors():
    pts = [[0, 0, 0], [1, 1, 0], [2, 0, 0], [3, 1, 0]]
    add.polyline(pts, 0.2, 8, lambda t, a: add.hsv(t))
    add.polyline(shift(pts, 0, 3, 0), 0.2, 6, lambda t, a: "red" if a < math.pi else "white", True)
    add.polyline(shift(pts, 0, 6, 0), lambda t: 0.1 + 0.1 * t, 5, lambda t, a: add.hsv(t + a / 10.0), False, 2)
    add.polyline(shift(pts, 5, 0, 0), 0.1, 4, lambda t, a: add.random_color())
    add.polyline(shift(pts, 5, 3, 0), 0.1, 3, lambda t, a: add.transparent("sky", 0.25 + 0.5 * t), True, 1)
    save_case()


@case
def wireframes():
    add.box([0, 0, 0], 1, "red")
    M = add.layer()
    add.wireframe(M)
    add.wireframe(add.move(M, [2, 0, 0]), 0.05, 4, "blue")
    add.wireframe(add.move(M, [4, 0, 0]), 0.02, 3, None, False)
    S = add.make(add.icosphere, [0, 3, 0], 1.0, 1, lambda d: "white" if d[1] > 0 else "navy")
    add.wireframe(S, 0.02, 5)
    add.wireframe(add.Mesh())
    save_case()


@case
def wireframe_orders():
    # Faces with scattered vertex numbers: the balls come in the order CPython's set gives them.
    M = add.Mesh()
    for i in range(80):
        M.add_vertex([math.cos(i * 0.7) * (1 + i * 0.01), math.sin(i * 1.3), i * 0.05])
    M.add_face([70, 3, 41], "red")
    M.add_face([41, 3, 12, 77], "blue")
    M.add_face([12, 8, 40, 72], "gold")
    M.add_face([64, 32, 0, 72], "teal")
    M.add_face([79, 47, 15, 31, 63], "pink")
    add.wireframe(M, 0.01, 3)
    add.wireframe(M, 0.02, 4, "white")
    save_case()


@case
def wireframe_scene():
    add.box([0, 0, 0], 1, "red")
    add.tetrahedron([2, 0, 0], 0.5, "blue")
    add.wireframe(add.scene(), 0.02, 4)
    save_case()


@case
def flows():
    record(points(add.flow(lorenz, [1, 1, 1], 0.01, 50)))
    record(points(add.flow(lambda p: [-p[1], p[0], 0.1], [1, 0, 0], 0.1, 20)))
    record(points(add.flow(lambda p: [1, 2, 3], [0.5, 0, -1], 0.25, 3)))
    record(points(add.flow(lorenz, [1, 1, 1], 0.01, 0)))
    record(points(add.flow(lambda p: [p[0] * p[1], -p[2], p[0] - p[1]], [0.3, 0.2, 0.1])))   # 1000 steps


@case
def traces():
    add.trace(lambda p: [-p[1], p[0], 0.2], [1, 0, 0], 0.1, 60)
    add.trace(lorenz, [1, 1, 1], 0.01, 300, 0.2, 6, "red", 10)
    add.trace(lambda p: [-p[1], p[0], 0.1], [2, 0, 3], 0.2, 40, lambda t: 0.05 + 0.1 * t, 5,
              lambda t, a: add.hsv(t), 3)
    add.trace(lambda p: [0, 0, 0], [0, 5, 0], 0.1, 10)                 # standing still
    add.trace(lambda p: [0.2, 0.1 * p[0], 0], [0, 8, 0])               # the defaults: 1000 steps
    add.trace(lambda p: [1, 0, 0], [0, 10, 0], 0.5, 3, 0.1, 4, "blue", 5)   # every > the points: one point
    save_case()


if __name__ == "__main__":
    import sys
    run(sys.argv)

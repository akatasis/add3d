from parity_case import add, case, record, run, save_case, save_mesh  # noqa: F401
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def ported(section):
    """Is section NN_name of add.hpp there?  (See the .cpp: the cases that need a section
    that is still being ported run once that section's own tests are here too.)"""
    return bool(os.environ.get("PARITY_PENDING")) or os.path.exists(os.path.join(HERE, "cases_%s.cpp" % section))


WITH_50 = ported("50_clean")      # revolve, spin3D: fix_normals()
WITH_75 = ported("75_text")       # axes: glyph()


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


# -- spheres -----------------------------------------------------------------------

@case
def spheres():
    add.sphere([0, 0, 0], 1.0)
    add.sphere([3, 0, 0], 0.5, 1, "red")
    add.sphere([6, 0, 0], 0.5, 2, "blue")
    add.sphere([9, 0, 0], 0.7, 5)
    add.sphere([0, 3, 0], 0.7, 4, (0.1, 0.9, 0.3))
    add.sphere([0, 6, 0], 1.2, 10, "gold", 1)
    add.sphere([3, 6, 0], 0.3, 50, "teal", 0)
    save_case()


@case
def sphere_levels():
    for k in (-5, 0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 16, 17, 20, 33, 34):
        add.sphere([0, 0, 0], 1.0, k)
        record(len(add.layer().F))
    for level in (-1, 0, 2, 3):
        add.sphere([0, 0, 0], 1.0, 1000, None, level)
        record(len(add.layer().F))


@case
def icosphere_levels():
    for level in (-3, 0, 1, 2, 9):
        add.icosphere([0.5, -1, 2], 1.5, level)
        S = add.layer()
        record(len(S.V))
        record(len(S.F))
        s = 0.0
        for p in S.V:
            s = s + p[0]
            s = s + p[1]
            s = s + p[2]
        record(s)
        record(points(S.V[-3:]))
        record_faces(S.F[-2:])


@case
def icospheres():
    add.icosphere([0, 0, 0], 1.0)
    add.icosphere([3, 0, 0], 1.5, 0, "red")
    add.icosphere([6, 0, 0], 0.5, -2)
    add.icosphere([0, 3, 0], 2.0, 2, lambda d: "white" if d[1] > 0.7 else "blue")
    add.icosphere([5, 3, 0], 1.0, 1, lambda d: add.hsv(math.atan2(d[2], d[0]) / (2 * math.pi)))
    add.sphere([0, 7, 0], 1.0, 5, lambda d: (0.5 + 0.5 * d[0], 0.5 + 0.5 * d[1], 0.5 + 0.5 * d[2]))
    add.sphere([5, 7, 0], 1.0, 3, lambda d: add.random_color(), 1)
    add.icosphere([10, 3, 0], 1.0, 1, lambda d: add.transparent("sky", 0.5 + 0.25 * d[1]))
    save_case()


@case
def quad_spheres():
    add.quadsphere([0, 0, 0], 1.0)
    add.quadsphere([3, 0, 0], 0.5, 3, "red")
    add.quadsphere([6, 0, 0], 0.75, 1, "gold")
    add.ellipsoid([0, 3, 0], [1.0, 2.0, 0.5])
    add.ellipsoid([4, 3, 0], [0.5, 0.5, 1.5], 4, "teal")
    add.ellipsoid([8, 3, 0], [0.3, -0.6, 0.9], 2, (0.25, 0.5, 0.75))
    save_case()


@case
def uv_spheres_and_tori():
    add.uvsphere([0, 0, 0], 1.0)
    add.uvsphere([3, 0, 0], 0.8, 8, 5, "red")
    add.uvsphere([6, 0, 0], 0.5, 3, 2)
    add.uvsphere([9, 0, 0], 0.5, 4, 1, "blue")
    add.torus([0, 4, 0], 2.0, 0.5)
    add.torus([6, 4, 0], 1.0, 0.3, 12, 6, "gold", [1, 0, 0])
    add.torus([0, 8, 0], 1.5, 0.4, 7, 5, "sky", [1, 1, 1])
    add.torus([6, 8, 0], 1.0, 0.25, 3, 3, "red", [0, 0, -1])
    add.torus([10, 8, 0], 0.5, 0.75, 8, 4, "navy")                    # a self-crossing spindle torus
    save_case()


# -- cylinders, cones and friends ---------------------------------------------------

@case
def cylinders():
    add.cylinder([0, 0, 0], [0, 2, 0], 0.5)
    add.cylinder([2, 0, 0], [3, 1, 2], 0.3, 7, "red")
    add.tube([4, 0, 0], [4, 0, 3], 0.4, 6, "blue")
    add.tube([5, 0, 0], [5, 1, 0], 0.4)
    add.cup([6, 0, 0], [6, -2, 0], 0.5, 5, "green")
    add.cup([7, 0, 0], [7, 1, 0], 0.5)
    add.cylinder([0, 0, 5], [0, 0, 5], 1.0)                           # A == B: nothing
    add.cylinder([1, 1, 1], [1, 1, 1.5], 0.25, 3)
    add.cylinder([2, 1, 1], [2, 1, 1.5], 0.25, 1, "red")
    save_case()


@case
def cones():
    add.cone([0, 4, 0], [0, 6, 0], 0.8)
    add.cone([2, 4, 0], [2.5, 3, 1], 0.4, 3, "gold")
    add.cone_open([4, 4, 0], [4, 6, 0], 0.6, 8, "teal")
    add.cone_open([5, 4, 0], [5, 5, 0], 0.6)
    add.frustum([6, 4, 0], [6, 6, 0], 0.8, 0.3)
    add.frustum([8, 4, 0], [8, 6, 0], 0.3, 0.8, 9, "pink", False)
    add.frustum([10, 4, 0], [10, 6, 0], 0.0, 0.5, 6, "navy")          # r1 = 0: a cone on its point
    add.frustum([12, 4, 0], [12, 6, 0], 0.5, 0.0, 6, "navy")
    add.frustum([14, 4, 0], [14, 6, 0], 0.0, 0.0, 4, "red")
    add.frustum([16, 4, 0], [17, 6, 1], 0.5, 1e-10, 5, "blue", False)
    save_case()


@case
def pipes_capsules_arrows():
    add.pipe([0, 0, 0], [0, 2, 0], 1.0, 0.7)
    add.pipe([3, 0, 0], [4, 1, 1], 0.5, 0.2, 7, "red")
    add.pipe([6, 0, 0], [6, 0, 0], 0.5, 0.2, 5, "gold")                # A == B: flat
    add.capsule([0, 4, 0], [0, 6, 0], 0.5)
    add.capsule([3, 4, 0], [5, 4, 1], 0.3, 8, "blue")
    add.capsule([6, 4, 0], [6, 7, 0], 0.4, 4, "gold")                  # k // 3 = 1 -> 3
    add.capsule([8, 4, 0], [8, 4, 0], 0.5, 12)                           # no length: a ball
    add.capsule([10, 4, 0], [10, 3, 0], 0.25, 13, "red")
    add.arrow([0, 8, 0], [2, 9, 1])
    add.arrow([3, 8, 0], [3, 11, 0], 0.1, "red", 8, 0.4)
    add.arrow([5, 8, 0], [5, 8, 0])                                      # nothing
    add.arrow([6, 8, 0], [7, 8, 0], 0.05, "blue", 5, 1.0)
    save_case()


@case
def helices():
    add.helix([0, 0, 0], 1.0, 0.5, 3)
    add.helix([4, 0, 0], 0.5, 0.2, 1.5, 40, 0.05, 6, "red", [1, 0, 0])
    add.helix([0, 4, 0], 2.0, 1.0, 0.5, 20, 0.3, 5, "blue", [1, 1, 0])
    add.helix([8, 0, 0], 1.0, -0.5, 2, 30, 0.1, 4, "gold", [0, 0, 1])
    save_case()


# -- the helpers -------------------------------------------------------------------

@case
def round_helpers():
    P, closed = add._revolve_grid([0, 0, 0], [0, 1, 0], [[1.0, 0.0], [1.5, 1.0], [0.5, 2.0]], 6)
    record(closed)
    for row in P:
        record(points(row))
    P, closed = add._revolve_grid([1, 2, 3], [1, 1, 0], [[1.0, 0.0], [0.5, 1.0]], 4, math.pi, 0.3)
    record(closed)
    for row in P:
        record(points(row))
    P, closed = add._revolve_grid([0, 0, 0], [0, 0, 0], [[1.0, 0.5]], 3, 2 * math.pi, 0.1)
    record(closed)
    for row in P:
        record(points(row))
    P, closed = add._revolve_grid([0, 0, 0], [0, 1, 0], [], 3)
    record(closed)
    record(len(P))
    V, T = add._icosphere_grid(1)
    record(points(V))
    record_faces(T)
    V, T = add._icosphere_grid(0)
    record(points(V))
    record_faces(T)
    M = add._tube_body([0, 0, 0], [1, 2, 0], 0.5, 0.25, 5, "red", True, False)
    save_mesh(M, "tube")
    M = add._tube_body([0, 0, 0], [0, 0, 0], 0.5, 0.25, 5, "red", True, True)
    record(len(M.V))
    record(len(M.F))


# -- revolve (needs fix_normals: section 50) ------------------------------------------

def vase(t):
    return [1 + 0.4 * math.sin(3 * t), t]


def from_list(pts):
    """The points of a list one after the other -- what add.hpp's revolve does with a list
    of [radius, height] points (add.py itself wants a function)."""
    it = iter(pts)
    return lambda t: next(it)


if WITH_50:
    @case
    def revolve_basic():
        add.revolve(vase, [0, 0, 0], [0, 1, 0], 0, 4, 60, 40, "teal")
        add.revolve(vase, [4, 0, 0], [5, 1, 0], 0, 2, 8, 6)
        add.revolve(lambda t: [0.5, t], [8, 0, 0], [8, 1, 0], 0, 1, 1, 5, "red")
        add.revolve(lambda t: [math.sin(t), -math.cos(t)], [0, 0, 5], [0, 1, 5], 0, math.pi, 10, 12, "gold")
        add.revolve(lambda t: [1 - t, t], [3, 0, 5], [3, 2, 5], 0, 1, 4, 8, "blue")
        add.revolve(lambda t: [t, 0.3 * t], [6, 0, 5], [6, 1, 5], 0, 1, 3, 7, "navy")
        add.revolve(lambda t: [1.0, -t], [9, 0, 5], [9, 1, 5], 0, 2, 2, 6)              # drawn downwards
        add.revolve(lambda t: [1.0, t], [12, 0, 5], [12, 1, 5], 0, 1, 2, 3, "red", 2 * math.pi - 1e-13)
        save_case()

    @case
    def revolve_defaults():
        add.revolve(lambda t: [0.5 + 0.2 * t, t])
        save_case()

    @case
    def revolve_colors():
        add.revolve(vase, [0, 0, 0], [0, 1, 0], 0, 4, 12, 10, lambda t, a: add.hsv(t / 4.0))
        add.revolve(vase, [4, 0, 0], [4, 1, 0], 0, 4, 6, 8, lambda t, a: "red" if a < math.pi else "white")
        add.revolve(vase, [8, 0, 0], [8, 1, 0], 0, 2, 4, 5, lambda t, a: add.random_color())
        save_case()

    @case
    def revolve_wedges():
        add.revolve(vase, [0, 0, 0], [0, 1, 0], 0, 4, 12, 10, "teal", math.pi)
        add.revolve(vase, [4, 0, 0], [4, 1, 0], 0, 4, 6, 8, lambda t, a: add.hsv(a / 6.0), 1.5)
        add.revolve(lambda t: [t, t], [8, 0, 0], [8, 1, 0], 0, 1, 3, 4, "gold", math.pi / 2)
        add.revolve(vase, [0, 0, 5], [0, 1, 5], 0, 4, 6, 6, lambda t, a: add.random_color(), 4.0)
        add.revolve(lambda t: [1.0, -t], [4, 0, 5], [4, 1, 5], 0, 1, 2, 3, "red", 1.0)
        save_case()

    @case
    def revolve_no_caps():
        add.revolve(vase, [0, 0, 0], [0, 1, 0], 0, 4, 10, 12, "teal", caps=False)
        add.revolve(vase, [4, 0, 0], [4, 1, 0], 0, 4, 10, 12, "red", math.pi, False)
        add.revolve(vase, [8, 0, 0], [8, 1, 0], 0, 4, 5, 6, lambda t, a: add.hsv(a), 2.0, False)
        save_case()

    @case
    def revolve_list():
        pts = [[0.0, 0.0], [1.0, 0.0], [1.2, 0.5], [0.8, 1.0], [0.9, 1.5], [0.0, 1.6]]
        add.revolve(from_list(pts), [0, 0, 0], [0, 1, 0], 0, 1, len(pts) - 1, 12, "teal")
        add.revolve(from_list(pts), [3, 0, 0], [3, 2, 0], 0.5, 2.5, len(pts) - 1, 7, lambda t, a: add.hsv(t + a))
        add.revolve(from_list(pts[1:5]), [6, 0, 0], [6, 1, 0], 0, 1, 3, 8, "red", math.pi)
        add.revolve(from_list(pts[1:4]), [9, 0, 0], [9, 1, 0], 0, 1, 2, 5, "blue", 2 * math.pi, False)
        save_case()

    @case
    def revolve_bad():
        raises(add.revolve, lambda t: [1.0, t], [0, 0, 0], [0, 1, 0], 0, 1, -1)       # no samples at all
        raises(add.revolve, from_list([]), [0, 0, 0], [0, 1, 0], 0, 1, -1)
        save_case()

    @case
    def spin3D_case():
        add.spin3D([0, 0, 0], [0, 2, 0], vase, 0, 4, 20, 16, "gold")
        add.spin3D([3, 0, 0], [4, 1, 1], lambda t: [0.5 + 0.1 * t, t], 0, 1, 3, 5, (10, 20, 30))
        save_case()


# -- axes (needs glyph: section 75) ----------------------------------------------------

if WITH_75:
    @case
    def axes_default():
        add.axes()
        save_case()

    @case
    def axes_custom():
        add.axes([1, 2, 3], 2.5, 0.05)
        add.axes([0, 0, 0], -1.0, 0.1)
        save_case()


if __name__ == "__main__":
    import sys
    run(sys.argv)

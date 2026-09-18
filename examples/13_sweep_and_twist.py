"""
13 -- copy a cross-section, move it, turn it, stretch it.

This is the workhorse of hand-made 3D: take a flat outline, carry it along a
path and let it rotate and change size as it goes.

    add.extrude(profile, direction, colour, steps, twist, scale)
    add.sweep(profile, path, t0, t1, steps, colour, scale=, twist=)

``twist`` is the total turn in radians; ``scale`` may be a number or a
function of the position ``t`` along the path (0 at the start, 1 at the end).
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import add
import math

TAU = 2 * math.pi
CELL = 3.6
shown = []


def polygon_profile(sides, r=1.0, inner=None):
    """A regular polygon, or a star when ``inner`` is given."""
    pts = []
    n = sides * (2 if inner else 1)
    for i in range(n):
        a = TAU * i / n
        rad = r if (inner is None or i % 2 == 0) else inner
        pts.append([math.cos(a) * rad, math.sin(a) * rad])
    return pts


def show(name, build, col, size=3.0):
    build(col)
    shown.append((name, add.place(add.fit(add.layer(), size), (0, 0, 0))))


SQUARE = [[-0.6, -0.6], [0.6, -0.6], [0.6, 0.6], [-0.6, 0.6]]
STAR = polygon_profile(6, 0.8, 0.35)
TRIANGLE = polygon_profile(3, 0.8)

# --- plain extrusion, then the same with a twist, then with a taper --------
show("straight bar", lambda c: add.extrude(SQUARE, [0, 3, 0], c), "red")

show("twisted bar", lambda c: add.extrude(SQUARE, [0, 3, 0], c, steps=60,
                                          twist=math.pi), "orange")

show("tapered bar", lambda c: add.extrude(SQUARE, [0, 3, 0], c, steps=40,
                                          scale=lambda t: 1 - 0.8 * t), "gold")

show("twisted star column",
     lambda c: add.extrude(STAR, [0, 3.4, 0], c, steps=90, twist=1.6 * math.pi,
                           scale=lambda t: 1 - 0.45 * t), "lime")

show("bulging column",
     lambda c: add.extrude(polygon_profile(16, 0.7), [0, 3.4, 0], c, steps=80,
                           scale=lambda t: 1 + 0.5 * math.sin(math.pi * t)),
     "teal")

# --- sweeping along a curved path -----------------------------------------
show("square through a helix",
     lambda c: add.sweep(SQUARE, lambda t: [math.cos(t), t / 4.0, math.sin(t)],
                         0, 4 * TAU, 260, c, scale=0.28), "sky")

show("triangle round a ring",
     lambda c: add.sweep(TRIANGLE, lambda t: [2 * math.cos(t), 0,
                                              2 * math.sin(t)],
                         0, TAU, 160, c, closed=True, scale=0.5,
                         twist=lambda t: 2 * TAU * t), "purple")

show("ribbon knot",
     lambda c: add.sweep([[-0.5, -0.06], [0.5, -0.06], [0.5, 0.06],
                          [-0.5, 0.06]],
                         lambda t: [math.sin(t) + 2 * math.sin(2 * t),
                                    -math.sin(3 * t),
                                    math.cos(t) - 2 * math.cos(2 * t)],
                         0, TAU, 300, c, closed=True,
                         twist=lambda t: 3 * TAU * t), "magenta")

show("horn from a growing circle",
     lambda c: add.sweep(polygon_profile(24, 1.0),
                         lambda t: [1.6 * math.cos(t) * math.exp(0.12 * t),
                                    0.5 * t,
                                    1.6 * math.sin(t) * math.exp(0.12 * t)],
                         0, 3.2 * math.pi, 200, c,
                         scale=lambda t: 0.12 + 1.2 * t * t), "brown")

# --- a screw thread, built by sweeping a triangle along a helix ------------
show("screw thread",
     lambda c: add.sweep([[0, -0.22], [0.42, 0], [0, 0.22]],
                         lambda t: [math.cos(t), t / 9.0, math.sin(t)],
                         0, 7 * TAU, 700, c), "silver")

# --- an arch: a square swept along half a circle, then mirrored -----------
def arch(c):
    add.sweep(SQUARE, lambda t: [2.4 * math.cos(t), 2.4 * math.sin(t), 0],
              0, math.pi, 90, c, scale=0.5)
    legs = add.layer()
    add.mesh(legs)
    add.mesh(add.move(legs, [0, -1.6, 0]))


show("arch", arch, "navy")

# --- a leaf: a profile that starts and ends at nothing ---------------------
show("leaf blade",
     lambda c: add.sweep(polygon_profile(12, 1.0),
                         lambda t: [0, t, 0], 0, 4, 90, c,
                         scale=lambda t: 0.9 * math.sin(math.pi * t) ** 0.7
                         + 0.02,
                         twist=0.4 * math.pi), "pink")

columns = 4
for i, (name, M) in enumerate(shown):
    add.mesh(add.move(M, [(i % columns) * CELL, 0, (i // columns) * CELL]))
    print("%2d. %s" % (i + 1, name))

add.check()
add.save("sweeps.off")

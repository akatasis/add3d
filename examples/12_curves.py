"""
12 -- parametric curves, drawn as round tubes.

``add.curve(P, t_from, t_to, steps, sides, radius, colour, closed)`` follows
the 3D curve ``P(t)`` and wraps a tube around it.  The tube never twists on
its own: the library carries a rotation-minimising frame along the curve, so
a square profile stays square all the way round a loop.

``radius`` may be a function of ``t`` -- a tube that swells and tapers.
"""
import add

TAU = 2 * add.pi
CELL = 3.4
shown = []


def show(name, build, col, size=2.6):
    build(col)
    shown.append((name, add.place(add.fit(add.layer(), size), (0, 0, 0))))


# --- a circle and a spiral -------------------------------------------------
show("circle", lambda c: add.curve(
    lambda t: [add.cos(t), 0, add.sin(t)], 0, TAU, 80, 16, 0.12, c, True), "red")

show("helix", lambda c: add.curve(
    lambda t: [add.cos(t), t / 6.0, add.sin(t)], 0, 6 * TAU, 400, 14, 0.1,
    c, False), "orange")

show("conical spiral", lambda c: add.curve(
    lambda t: [t * add.cos(t) / 20, t / 20.0, t * add.sin(t) / 20],
    0, 8 * TAU, 400, 14, 0.09, c, False), "gold")

# --- knots -----------------------------------------------------------------
show("trefoil knot", lambda c: add.curve(
    lambda t: [add.sin(t) + 2 * add.sin(2 * t), -add.sin(3 * t),
               add.cos(t) - 2 * add.cos(2 * t)],
    0, TAU, 300, 18, 0.28, c, True), "lime")

show("(3,4) torus knot", lambda c: add.curve(
    lambda t: [(2 + add.cos(4 * t / 3.0)) * add.cos(t),
               add.sin(4 * t / 3.0),
               (2 + add.cos(4 * t / 3.0)) * add.sin(t)],
    0, 3 * TAU, 500, 18, 0.22, c, True), "teal")

show("figure eight knot", lambda c: add.curve(
    lambda t: [(2 + add.cos(2 * t)) * add.cos(3 * t),
               add.sin(4 * t),
               (2 + add.cos(2 * t)) * add.sin(3 * t)],
    0, TAU, 400, 18, 0.22, c, True), "sky")

# --- Lissajous curves ------------------------------------------------------
show("Lissajous 3:2", lambda c: add.curve(
    lambda t: [add.sin(3 * t), add.sin(2 * t + 1), add.sin(4 * t + 2)],
    0, TAU, 300, 14, 0.07, c, True), "purple")

show("Lissajous 5:4", lambda c: add.curve(
    lambda t: [add.sin(5 * t), add.sin(4 * t), add.sin(3 * t + 1)],
    0, TAU, 400, 14, 0.06, c, True), "magenta")

# --- a curve whose radius changes -----------------------------------------
show("tapering vine", lambda c: add.curve(
    lambda t: [add.cos(t) * (1 + t / 12.0), t / 8.0,
               add.sin(t) * (1 + t / 12.0)],
    0, 5 * TAU, 400, 16, lambda t: 0.22 * (1 - t / (5 * TAU)) + 0.02,
    c, False), "brown")

show("beaded ring", lambda c: add.curve(
    lambda t: [add.cos(t), 0.25 * add.sin(6 * t), add.sin(t)],
    0, TAU, 300, 16, lambda t: 0.08 + 0.07 * (1 + add.sin(12 * t)),
    c, True), "navy")

# --- rose curves lifted into 3D -------------------------------------------
show("rose k=5", lambda c: add.curve(
    lambda t: [add.cos(5 * t) * add.cos(t), 0.25 * add.sin(5 * t),
               add.cos(5 * t) * add.sin(t)],
    0, TAU, 400, 14, 0.06, c, True), "pink")

show("spherical spiral", lambda c: add.curve(
    lambda t: [add.sin(t / 10.0) * add.cos(t), add.cos(t / 10.0),
               add.sin(t / 10.0) * add.sin(t)],
    0.001, 10 * add.pi - 0.001, 500, 12, 0.045, c, False), "silver")

columns = 4
for i, (name, M) in enumerate(shown):
    add.mesh(add.move(M, [(i % columns) * CELL, 0, (i // columns) * CELL]))
    print("%2d. %s" % (i + 1, name))

add.check()
add.save("curves.off")

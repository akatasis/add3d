"""
26 -- vector fields, flows and strange attractors.

Mathematics makes good models.  ``flow`` integrates a vector field with
Runge-Kutta and ``trace`` draws the path as a tube: the Lorenz butterfly,
coloured along its length by a colour function, and the Rössler band,
drawn with ``polyline`` so that the tube can thin out towards the end.
A small field of arrows shows the direction of flow: one arrow, ``aim``-ed
along the field at every grid point and coloured by speed.  Beads on a
helix and cubes on a spiral show ``points_on_helix`` / ``points_on_spiral``.

Parameters: ``STEPS`` (length of the curves), ``RHO`` (the Lorenz parameter).
"""
import add

STEPS = 6000
RHO = 28.0
add.axes([0, 0, 0], 3.0)


# --------------------------------------------------------------------------
#  the Lorenz attractor
# --------------------------------------------------------------------------
def lorenz(p):
    x, y, z = p
    return [10.0 * (y - x), x * (RHO - z) - y, x * y - 8.0 / 3.0 * z]


add.push()
add.trace(lorenz, [1.0, 1.0, 1.0], 0.006, STEPS, r=0.35, k=10, every=2,
          color=lambda t, a: add.hsv(0.7 * t, 0.9, 1.0))
# the attractor lives around z = 25: bring it down, shrink it, stand it up
L = add.pop()
L = add.rotateX(add.zoom(L, 0.22, (0, 0, 0)), -add.pi / 2, (0, 0, 0))
add.mesh(add.move(L, [-12, 2, 0]))
add.text("LORENZ", [-15.5, 0, 6], 1.0, color="navy", k=6, u=[1, 0, 0], v=[0, 0, -1])


# --------------------------------------------------------------------------
#  the Rössler attractor: flow() gives the points, polyline() draws them
# --------------------------------------------------------------------------
def rossler(p):
    x, y, z = p
    return [-y - z, x + 0.2 * y, 0.2 + z * (x - 5.7)]


pts = add.flow(rossler, [1.0, 1.0, 0.0], 0.02, STEPS)[::3]
pts = [[0.3 * p[0] + 8, 0.3 * p[2] + 1, 0.3 * p[1] + 8] for p in pts]
add.polyline(pts, lambda t: 0.06 + 0.16 * (1 - t), 8,
             color=lambda t, a: add.gradient(t, "orange", "purple"))
add.text("RÖSSLER", [5, 0, 13.5], 1.0, color="navy", k=6, u=[1, 0, 0], v=[0, 0, -1])


# --------------------------------------------------------------------------
#  an arrow field: the same arrow aimed along the field at every point
# --------------------------------------------------------------------------
def swirl(p):
    return [-p[2] + 0.3 * p[0], 0.4 * add.sin(p[0]), p[0] + 0.3 * p[2]]


add.push()
add.arrow([0, 0, 0], [0, 1, 0], 0.08, "grey", 8)           # points up, 1 long
one = add.pop()
for x in range(-4, 5):
    for z in range(-4, 5):
        p = [x * 1.1 + 10, 0.6, z * 1.1 - 8]
        v = swirl([p[0] - 10, p[1], p[2] + 8])
        speed = add.clamp(add.remap(add.distance(v, [0, 0, 0]), 0, 6, 0, 1))
        A = add.zoom(one, 0.4 + 0.6 * speed, (0, 0, 0))
        A = add.aim(A, v)
        add.mesh(add.color(add.move(A, p), add.hsv(0.66 - 0.66 * speed)))
add.text("FIELD", [8, 0, -1.5], 1.0, color="navy", k=6, u=[1, 0, 0], v=[0, 0, -1])


# --------------------------------------------------------------------------
#  beads on a helix, cubes on a spiral
# --------------------------------------------------------------------------
add.push()
add.sphere([0, 0, 0], 0.3, 5, "gold")
bead = add.pop()
beads = add.points_on_helix([-10, 0.3, -8], 2.0, 1.6, 4, 90)
add.mesh(add.scatter(bead, beads, seed=1, spin=False, scale=(0.7, 1.3)))
add.curve(lambda t: [-10 + 2 * add.cos(2 * add.pi * t), 0.3 + 1.6 * t, -8 + 2 * add.sin(2 * add.pi * t)],
          0, 4, 240, 8, 0.05, "black")

add.push()
add.box([0, 0, 0], 0.5, "teal")
cube = add.pop()
spiral = add.points_on_spiral([0, 0.25, -8], 0.3, 4.5, 3, 60, rise=3.0)
add.mesh(add.along(cube, spiral, len(spiral), axis=[1, 0, 0],
                   scale=lambda t: 0.5 + t))

add.mesh(add.limit_colors(add.layer(), 50))   # at most 50 colours, so the .obj suits Sketchfab
add.check()
add.save("vector_fields.off")

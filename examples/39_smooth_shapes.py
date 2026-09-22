"""
39 -- pull a few corners, then round the shape: generalised Catmull-Clark.

Front row: a box is taken out as a layer, two of its corners are moved with
``add.set_vertex`` (``None`` keeps a coordinate as it was), and the result
is rounded into its Catmull-Clark limit surface with ``add.smooth``.  The
control mesh is drawn next to it as a wire frame so that you can see what
was rounded.  Every cell keeps the colour of the control face it lies on.

Middle row: the same pentagonal prism smoothed with ``n = 1 ... 7`` cells
per control edge.  Classical subdivision only reaches 2, 4, 8 ...; the
generalised algorithm (Sabaliauskas 2026) gives every ``n``, with all the
vertices exactly on the smooth surface.  Odd ``n`` leave a small polygon in
the middle of each face, even ``n`` meet at a centre node.

Back row: a flat seven-pointed star -- one single polygon -- sampled
with ``uniform=False`` (the plain characteristic-map grid, cells crowd
towards the centre) and ``uniform=True`` (the paper's reparameterisation,
cells evenly sized).  The cells are drawn as wire frames.

Parameter: ``PULL`` (how far the two corners are pulled out).
"""
import add

PULL = 1.6

# --- front row: the pulled box -------------------------------------------
add.box([0, 0, 0], 2, "gold")
block = add.layer()                                   # 8 vertices, 6 faces
block = add.color_random(block, seed=3)               # one colour per face
i = add.nearest_vertex(block, [1, 1, 1])              # the corner at (1, 1, 1)
j = add.nearest_vertex(block, [-1, -1, 1])
block = add.set_vertex(block, i, [1 + PULL, 1 + PULL, None])     # pull it out, keep z
block = add.set_vertex(block, j, [-1 - PULL, None, 1 + PULL])
print("moved corners", i, "and", j, "->", add.vertex(block, i), add.vertex(block, j))

add.wireframe(add.move(block, [-4.5, 0, 4]), 0.05, 8, [40, 40, 40])
add.mesh(add.move(add.smooth(block, 8), [0, 0, 4]))          # 8 cells per edge
add.mesh(add.move(add.catmull_clark(block, 2), [4.5, 0, 4]))  # classical, 2 steps

# --- middle row: n = 1 ... 7 on one prism --------------------------------
prism = add.make(add.prism, add.profile_polygon(5, 1.0), 1.4, "teal")   # not layer():
prism = add.color_random(prism, seed=5)                                  # the scene is not empty
for n in range(1, 8):
    x = (n - 4) * 2.6
    add.mesh(add.move(add.smooth(prism, n), [x, 0, -0.5]))
    add.text(str(n), [x, -1.0, 1.0], 0.5, color="black", u=[1, 0, 0], v=[0, 0, -1],
             align="center")

# --- back row: uniform or not, on a single star polygon ------------------
star = add.profile_star(7, 2.0, 1.1)
face = add.make(add.polygon, [[x, 0, y] for x, y in star][::-1], "orange")
for x, uniform, label in ((-3.2, False, "PLAIN"), (3.2, True, "UNIFORM")):
    grid = add.smooth(face, 6, uniform=uniform)
    add.mesh(add.move(grid, [x, -0.6, -5]))
    add.wireframe(add.move(grid, [x, -0.6, -5]), 0.025, 6, [40, 40, 40], nodes=False)
    add.text(label, [x, -0.6, -2.4], 0.4, color="black", u=[1, 0, 0], v=[0, 0, -1],
             align="center")

add.check()
add.save("smooth_shapes.off")

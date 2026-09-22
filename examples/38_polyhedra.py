"""
38 -- the five regular polyhedra and what can be made of them.

Row by row (front to back):

1. the Platonic solids themselves -- ``add.tetrahedron``, ``add.polyhedron
   ("cube")``, ``add.octahedron``, ``add.dodecahedron``, ``add.icosahedron``,
   all with their vertices on a sphere of the same radius and the average of
   their vertex coordinates exactly at the centre;
2. their duals (``add.dual``: a vertex for every face) -- cube and
   octahedron swap, dodecahedron and icosahedron swap, the tetrahedron is
   its own dual;
3. their truncations (``add.truncate``: every corner cut off) -- the
   truncated icosahedron is the football of example 37;
4. geodesic domes (``add.refine`` splits every face into four, three times,
   ``add.spherify`` pushes the points out onto the sphere) -- the
   icosahedron gives ``add.sphere`` itself;
5. the smooth limit surfaces (``add.smooth``: generalised Catmull-Clark
   with 8 cells per edge) -- five different soft balls.

Parameter: ``LEVEL`` (refinement steps of the domes).
"""
import add

LEVEL = 3
NAMES = ["tetrahedron", "cube", "octahedron", "dodecahedron", "icosahedron"]
COLORS = ["red", "gold", "green", "sky", "purple"]
STEP = 3.4                                   # spacing between solids
R = 1.2

for col, (name, color) in enumerate(zip(NAMES, COLORS)):
    x = (col - 2) * STEP
    solid = add.make(add.polyhedron, name, [0, 0, 0], R, color)
    points = add.polyhedron_points(name, [0, 0, 0], R)
    centre = [sum(p[a] for p in points) / len(points) for a in range(3)]
    print("%-13s %2d vertices %2d faces %2d edges, valence %d, edge %.3f, "
          "vertex average %s" % (name, len(points), len(solid.F),
                                 len(add.edges(solid)), add.valence(solid, 0),
                                 add.mean_edge_length(solid),
                                 [round(c, 9) + 0.0 for c in centre]))

    rows = [
        solid,                                                  # 1. the solid
        add.color(add.dual(solid), add.shade(color, 0.75)),     # 2. its dual
        add.truncate(solid, 1 / 3.0, add.shade(color, 0.5)),    # 3. corners cut
        add.spherify(add.refine(solid, LEVEL)),                 # 4. geodesic dome
        add.smooth(solid, 8),                                   # 5. limit surface
    ]
    for row, shape in enumerate(rows):
        # duals and smooth balls come out smaller: scale each back to radius R
        reach = max(add.distance(p, [0, 0, 0]) for p in shape.V)
        add.mesh(add.move(add.zoom(shape, R / reach, [0, 0, 0]), [x, 0, -row * STEP]))
    # the edges of the plain solid, to show its structure
    add.wireframe(add.move(solid, [x, 0, 0]), 0.03, 6, [40, 40, 40])
    add.text(name.upper(), [x, -R - 0.05, 1.8], 0.24, color="black",
             u=[1, 0, 0], v=[0, 0, -1], align="center")

for row, label in enumerate(["SOLID", "DUAL", "TRUNCATED", "GEODESIC", "SMOOTH"]):
    add.text(label, [-2 * STEP - 2.1, -R - 0.05, -row * STEP], 0.24,
             color="black", u=[1, 0, 0], v=[0, 0, -1], align="center")

add.check()
add.save("polyhedra.off")

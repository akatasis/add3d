"""
37 -- a football from the twelve vertices of an icosahedron.

A classic football is a *truncated icosahedron*: cut every corner off an
icosahedron one third of the way along its edges and you get 12 pentagons
(one per old vertex) and 20 hexagons (one per old face).

The left ball is built by hand from coordinates, to show the vertex tools:
``add.polyhedron_points`` gives the twelve vertices, ``add.neighbors``
lists the five neighbours of each in order around it, and ``add.lerp``
walks a third of the way along every edge.  The right ball is the same
thing in one call (``add.truncate``), painted by the number of corners
(``add.color_by_sides``) and rounded into a real ball with the
generalised Catmull-Clark surface (``add.smooth``), which keeps each panel
its own colour.

Parameter: ``CUT`` (1/3 gives the football; 1/2 cuts to the edge midpoints).
"""
import add

CUT = 1 / 3.0
R = 2.5

# --- the icosahedron and what we know about it --------------------------
ico = add.make(add.icosahedron, [0, 0, 0], R, "white")
points = add.polyhedron_points("icosahedron", [0, 0, 0], R)
print("icosahedron: %d vertices, %d faces, %d edges"
      % (len(points), len(ico.F), len(add.edges(ico))))
print("vertex 0 has %d neighbours, %.3f apart on average (edge length %.3f)"
      % (add.valence(ico, 0), add.mean_neighbor_distance(ico, 0),
         add.mean_edge_length(ico)))

# --- ball 1: panels built by hand from the coordinates -------------------
for v in range(len(points)):                          # one pentagon per vertex
    ring = add.neighbors(ico, v)                      # 5 neighbours, in order
    add.polygon([add.lerp(points[v], points[u], CUT) for u in ring], "black")
for f in ico.F:                                       # one hexagon per face
    corners = []
    for i in range(3):
        a, b = f[i], f[(i + 1) % 3]
        corners.append(add.lerp(points[a], points[b], CUT))
        corners.append(add.lerp(points[b], points[a], CUT))
    add.polygon(corners, "white")
panels = add.clean(add.layer())                       # weld the shared corners
add.mesh(add.move(panels, [-3.2, 0, 0]))
add.wireframe(add.move(panels, [-3.2, 0, 0]), 0.03, 6, [40, 40, 40], nodes=False)

# --- ball 2: add.truncate + add.smooth -----------------------------------
ball = add.truncate(ico, CUT)                         # 32 flat panels
ball = add.color_by_sides(ball, {5: "black", 6: "white"})
ball = add.smooth(ball, 16)                           # round: 11 520 cells on the limit surface
add.mesh(add.move(ball, [3.2, 0, 0]))

# a floor to stand on, and the names
add.cylinder([0, -R - 0.4, 0], [0, -R - 0.1, 0], 7.5, 64, [60, 140, 60])
add.text("32 PANELS", [-3.2, -R - 0.1, 3.4], 0.5, color="white", u=[1, 0, 0],
         v=[0, 0, -1], align="center")
add.text("SMOOTHED", [3.2, -R - 0.1, 3.4], 0.5, color="white", u=[1, 0, 0],
         v=[0, 0, -1], align="center")

add.check()
add.save("football.off")

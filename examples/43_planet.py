"""
43 -- a planet with craters, an ocean and two rocky moons.

The planet is a geodesic sphere (``add.icosphere``) whose vertices are
lifted by a bumpy height function and painted by height and latitude with
``add.color_by``: ocean, beach, land, mountains, and snow at the poles.
Craters are punched at a few face centres (``add.face_centers``) with
``add.difference``.  The moons are an octahedron and a tetrahedron,
refined, pushed out to a ball and roughened with ``add.jitter``; the ring
is a flat annulus given a little thickness with ``add.solidify``.

Everything here also uses the vertex tools: ``add.adjacency`` averages
each vertex height with its neighbours once (a cheap smoothing of the
noise), and ``add.polyhedron_faces`` / ``add.edge_length`` measure the
moons before they are roughened.

Parameter: ``ROUGH`` (height of the mountains).
"""
import add

add.seed(7)
ROUGH = 0.18
R = 3.0


def bumps(p):
    """A cheap 'noise': sums of sines with different directions."""
    x, y, z = p
    return (add.sin(3.1 * x + 1.3 * y) + add.sin(2.7 * y - 1.9 * z)
            + add.sin(2.3 * z + 3.7 * x) + 0.5 * add.sin(7 * x) * add.sin(5 * z)) / 3.5


# --- the planet -----------------------------------------------------------
globe = add.make(add.icosphere, [0, 0, 0], R, 5)           # 20480 triangles
heights = [bumps(p) for p in globe.V]
neighbours = add.adjacency(globe)                            # once, for all vertices
heights = [(h + sum(heights[j] for j in nb) / len(nb)) / 2.0
           for h, nb in zip(heights, neighbours)]           # average with the ring
lifted = add.Mesh([[c * (1 + ROUGH * max(h, 0.0)) for c in p]
                   for p, h in zip(globe.V, heights)],       # sea level stays at R
                  [list(f) for f in globe.F], list(globe.C))


def paint(p):
    d = add.distance(p, [0, 0, 0]) - R
    lat = abs(p[1]) / R
    if lat > 0.82:
        return "white"
    if d < 0.003:
        return [30, 80, 180]                                 # ocean
    if d < 0.03:
        return [230, 210, 150]                               # beach
    if d < 0.25:
        return [80, 150, 60]                                 # land
    return [150, 140, 130]                                   # mountains


planet = add.color_by(lifted, paint)
# craters: a ball subtracted at a few face centres
centres = add.face_centers(planet)
for k in range(0, len(centres), 5100):
    c = centres[k]
    hole = add.make(add.sphere, [c[0] * 1.03, c[1] * 1.03, c[2] * 1.03], 0.35, 8, "grey")
    planet = add.difference(planet, hole)
add.mesh(planet)

# --- moons and a ring -------------------------------------------------------
for draw, at, size, color in ((add.octahedron, [5.2, 1.2, -1.5], 0.7, [150, 140, 130]),
                              (add.tetrahedron, [-4.8, -0.8, 2.6], 0.6, [120, 110, 100])):
    moon = add.make(draw, [0, 0, 0], size, color)
    print(draw.__name__, "has", len(add.polyhedron_faces(draw.__name__)), "faces, edge",
          round(add.edge_length(moon, 0, 1), 3))
    moon = add.spherify(add.refine(moon, 3))
    moon = add.jitter(moon, 0.05, seed=1)
    add.mesh(add.move(moon, at))
band = add.make(add.ring, [0, 0, 0], [0.15, 1, 0.05], 5.4, 4.2, 96, [200, 190, 170])
add.mesh(add.solidify(band, 0.05))                          # a flat ring is an open sheet

add.check()
add.save("planet.off")

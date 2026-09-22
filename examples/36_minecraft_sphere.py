"""
36 -- the "Minecraft sphere": a cube blown up into a ball, and a ball of blocks.

Three ways to make a sphere stand side by side:

1. ``cube_sphere`` -- the construction of the course's Maple worksheet
   ``sfera(m)``: each of the six faces of a cube is covered with an m x m
   grid whose lines are spaced by ``cot(pi/4 + pi/2 * i/m)`` (so that the
   cells stay the same size after the bend), and every grid point is
   pushed out onto the sphere by dividing by its length.  Six patches,
   ``6 * m * m`` quads, no poles.  ``add.quadsphere`` is the same thing in
   one call.
2. ``block_sphere`` -- the Minecraft way: every unit block whose centre is
   within the radius, ``add.voxels`` draws only the outside walls.
3. ``add.sphere`` -- the geodesic sphere of triangles (example 38 shows
   where it comes from).

Run with ``--fine`` for the detailed version (``minecraft_sphere_fine.off``,
about 500 000 polygons); the default is the Sketchfab-sized one.

Parameter: ``M`` (grid lines per cube face) and ``R`` (blocks in the radius).
"""
import sys
import add

FINE = "--fine" in sys.argv
M = 300 if FINE else 40                       # 6 * M * M quads
R = 40 if FINE else 12                        # blocks from the centre to the skin


def cube_sphere(m, center, r, colors):
    """The Maple sfera(m), written with a vertex dictionary instead of index
    arithmetic: shared corners are found by their coordinates."""
    mesh = add.Mesh()
    index = {}

    def vertex(p):
        key = (round(p[0], 9), round(p[1], 9), round(p[2], 9))
        if key not in index:
            index[key] = mesh.add_vertex([center[a] + r * p[a] for a in range(3)])
        return index[key]

    def line(i):                              # cot(pi/4 + pi/2 * i/m): from 1 down to -1
        return 1.0 / add.tan(add.pi / 4 + add.pi / 2 * i / m)

    # face 1 is z = 1; the other five are the same grid turned around
    sides = [lambda x, y, z: (x, y, z), lambda x, y, z: (-z, y, x),
             lambda x, y, z: (-x, y, -z), lambda x, y, z: (z, y, -x),
             lambda x, y, z: (x, z, -y), lambda x, y, z: (x, -z, y)]
    for s, side in enumerate(sides):
        for i in range(m):
            for j in range(m):
                corners = []
                for a, b in ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)):
                    x, y = line(a), line(b)
                    d = add.sqrt(x * x + y * y + 1)           # push out onto the sphere
                    corners.append(vertex(side(x / d, y / d, 1 / d)))
                mesh.add_face(corners, colors[(i + j) % 2])   # chequered
    return add.fix_normals(mesh)              # all six patches facing outward


def block_sphere(radius, center, size, paint):
    cells = set()
    for i in range(-radius, radius + 1):
        for j in range(-radius, radius + 1):
            for k in range(-radius, radius + 1):
                if i * i + j * j + k * k <= radius * radius:
                    cells.add((i, j, k))
    add.voxels(cells, size, origin=[center[a] - size / 2.0 for a in range(3)],
               color=paint)


SPACING = 7.5
# 1. the Maple sphere
add.mesh(cube_sphere(M, [-SPACING, 0, 0], 3, [[70, 130, 220], [40, 80, 160]]))
# 2. the ball of blocks, painted like a planet: grass on top, dirt, then stone
def paint(i, j, k):
    y = j - R                                 # cell index -> height from the centre
    if y > R * 0.55:
        return [90, 170, 60]
    if y > 0:
        return [140, 95, 55]
    return [125, 125, 130]


block_sphere(R, [0, 0, 0], 3.0 / R, paint)
# 3. the geodesic sphere for comparison
add.sphere([SPACING, 0, 0], 3, 60 if FINE else 20, [230, 80, 60])

add.text("MAPLE", [-SPACING, -3.6, 3.6], 0.6, color="navy", u=[1, 0, 0], v=[0, 0, -1],
         align="center")
add.text("BLOCKS", [0, -3.6, 3.6], 0.6, color="navy", u=[1, 0, 0], v=[0, 0, -1],
         align="center")
add.text("GEODESIC", [SPACING, -3.6, 3.6], 0.6, color="navy", u=[1, 0, 0], v=[0, 0, -1],
         align="center")

add.check()
add.save("minecraft_sphere_fine.off" if FINE else "minecraft_sphere.off")

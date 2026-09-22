"""
42 -- pillow letters: blocks, united, then rounded.

Each letter is a few ``add.cuboid`` blocks that overlap.  ``add.union``
melts them into one watertight solid (the walls hidden inside disappear),
and ``add.smooth`` then rounds the solid into a soft cushion -- the coarse
block mesh is the control net of the smooth surface, so a thin bar becomes
a rounded bar and a corner becomes a soft corner.  Cells keep the colour of
the block they came from.

Along the way the mesh tools measure what was built: ``add.edge_lengths``
(the shortest and longest edge), ``add.face_area`` (the biggest face) and
``add.boundary_loops`` (an empty list once the solid is closed).  Finally
``add.inflate`` puffs each letter out a little, and ``add.move_vertex`` /
``add.set_vertices`` bend the plinth they stand on.

Parameter: ``N`` (cells per control edge in the smoothing).
"""
import add

N = 6
T = 0.9                                        # bar thickness
H = 4.0                                        # letter height


def letter_A(color):
    add.cuboid([-0.9, H / 2, 0], [T, H, T], color)
    add.cuboid([0.9, H / 2, 0], [T, H, T], color)
    add.cuboid([0, H - T / 2, 0], [2.7, T, T], color)
    add.cuboid([0, H / 2, 0], [2.7, T, T], color)


def letter_D(color):
    add.cuboid([-0.9, H / 2, 0], [T, H, T], color)
    add.cuboid([0.3, H - T / 2, 0], [1.5, T, T], color)
    add.cuboid([0.3, T / 2, 0], [1.5, T, T], color)
    add.cuboid([0.9, H / 2, 0], [T, H - 1.2, T], color)


def build(draw, color, x):
    blocks = add.make(draw, color)                       # the overlapping blocks
    solid = blocks
    parts = [add.Mesh(list(blocks.V), [list(f) for f in blocks.F[i:i + 6]],
                      list(blocks.C[i:i + 6])) for i in range(0, len(blocks.F), 6)]
    solid = parts[0]
    for part in parts[1:]:
        solid = add.union(solid, part)                   # melt the blocks together
    L = add.edge_lengths(solid)
    big = max(range(len(solid.F)), key=lambda i: add.face_area(solid, i))
    print("letter: %d faces, edges %.2f .. %.2f, biggest face %.2f, holes: %s"
          % (len(solid.F), min(L), max(L), add.face_area(solid, big),
             add.boundary_loops(solid)))
    soft = add.smooth(solid, N)                          # the cushion
    soft = add.inflate(soft, 0.06)                       # puff it up a little
    add.mesh(add.move(soft, [x, 0.3, 0]))


build(letter_A, "red", -2.0)
build(letter_D, "gold", 1.6)
build(letter_D, "sky", 5.2)

# the plinth: a slab whose top corners are pushed about, then rounded too
slab = add.make(add.cuboid, [1.6, -0.3, 0], [10, 0.6, 3], [90, 90, 100])
top = [i for i, p in enumerate(slab.V) if p[1] > 0 - 1e-9]
slab = add.set_vertices(slab, {i: [None, 0.35, None] for i in top})   # raise the whole top
slab = add.move_vertex(slab, add.nearest_vertex(slab, [6.6, 0.35, 1.5]), [0.4, 0.5, 0.4])
add.mesh(add.smooth(slab, 12))

add.check()
add.save("pillow_letters.off")

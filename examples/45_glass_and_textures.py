"""
45 -- glass and pictures: see-through surfaces and image textures.

Two things that only an ``.obj`` + ``.mtl`` pair can carry (an ``.off``
file has plain colours):

* **transparency** -- ``add.transparent(colour, alpha)`` makes a colour
  see-through (``alpha`` 0 = invisible, 1 = solid) and works wherever a
  colour does; ``add.opacity(mesh, alpha)`` does it to a finished part.
  The opacity is written as ``d`` in the ``.mtl`` file;
* **textures** -- ``add.texture(mesh, "picture.png", mapping)`` wraps an
  image around a part (``map_Kd`` in the ``.mtl``), with the texture
  coordinates worked out by a box, planar, spherical or cylindrical
  mapping.  The pictures here are *generated* with ``add.write_png`` --
  bricks, wood, a chequerboard and a little planet map -- so the example
  needs no files, but any ``.png`` or ``.jpg`` of yours works the same way.

The scene: a fish tank with glass walls and water, a textured globe, and
a brick house on a wooden table with glass in its window openings --
through them, and through the open door, you see the room inside.
Everything without transparency or textures is exactly as before, so
``.off`` files of old models are unchanged.

Parameter: ``GLASS`` (opacity of the glass, 0.2 = very clear).
"""
import add

GLASS = 0.3
add.seed(3)

# --- 1. the pictures, drawn pixel by pixel ---------------------------------
def brick_rows(w=96, h=96):
    rows = []
    for y in range(h):
        row = []
        course = y // 16                                  # one course of bricks
        for x in range(w):
            xx = (x + (8 if course % 2 else 0)) % 32
            mortar = y % 16 < 2 or xx < 2
            row.append([200, 200, 190] if mortar else
                       [150 + 25 * ((x * 7 + y * 3) % 3), 60, 40])
        rows.append(row)
    return rows


def wood_rows(w=128, h=128):
    return [[add.gradient(0.5 + 0.5 * add.sin(x / 6.0 + 2 * add.sin(y / 23.0)),
                          [190, 140, 80], [120, 75, 35]) for x in range(w)]
            for y in range(h)]


def planet_rows(w=256, h=128):
    rows = []
    for y in range(h):
        lat = (0.5 - y / float(h)) * add.pi              # +pi/2 at the top
        row = []
        for x in range(w):
            lon = x / float(w) * 2 * add.pi
            land = (add.sin(3 * lon + 2 * lat) + add.sin(5 * lat - lon)
                    + 0.6 * add.sin(9 * lon) * add.cos(4 * lat))
            if abs(lat) > 1.25:
                row.append("white")                       # polar caps
            elif land > 0.9:
                row.append([90, 150, 60] if land < 1.6 else [150, 140, 120])
            else:
                row.append([30, 80, 180] if land < 0.6 else [230, 210, 150])
        rows.append(row)
    return rows


add.write_png("bricks.png", brick_rows())
add.write_png("wood.png", wood_rows())
add.write_png("planet.png", planet_rows())
add.write_png("check.png", [["white" if (x // 8 + y // 8) % 2 else [40, 40, 40]
                             for x in range(64)] for y in range(64)])

# --- 2. a wooden table ------------------------------------------------------
table = add.make(add.cuboid, [0, -0.15, 0], [16, 0.3, 9], "brown")
add.mesh(add.texture(table, "wood.png", "box", scale=3.0))
for x in (-7, 7):
    for z in (-3.8, 3.8):
        add.cylinder([x, -3.5, z], [x, -0.3, z], 0.25, 12, [90, 60, 30])

# --- 3. the fish tank ---------------------------------------------------------
TANK = [-4.5, 1.5, 0]
glass = add.transparent([170, 220, 255], GLASS)
for dx, dz, sx, sz in ((-2.5, 0, 0.06, 3), (2.5, 0, 0.06, 3), (0, -1.5, 5, 0.06),
                       (0, 1.5, 5, 0.06)):                 # four glass walls
    add.cuboid([TANK[0] + dx, TANK[1], TANK[2] + dz], [sx, 3, sz], glass)
add.cuboid([TANK[0], 0.03, TANK[2]], [5, 0.06, 3], glass)  # glass bottom
add.cuboid([TANK[0], 1.2, TANK[2]], [4.88, 2.3, 2.88],
           add.transparent([60, 140, 220], 0.35))          # the water
for i in range(40):                                        # pebbles
    add.sphere([TANK[0] + add.uniform(-2.2, 2.2), 0.2, TANK[2] + add.uniform(-1.2, 1.2)],
               add.uniform(0.1, 0.22), 6, add.choice([[150, 140, 130], [110, 100, 90],
                                                       [200, 190, 170]]))
# a fish: a stretched sphere, a tail and an eye; a second, ghostly one made
# see-through as a whole with add.opacity
fish = add.make(add.sphere, [0, 0, 0], 0.55, 10, "orange")
fish = add.stretch(fish, [1.6, 1.0, 0.5])
add.mesh(add.move(fish, [TANK[0] - 0.4, 1.5, TANK[2]]))
add.mesh(add.move(add.opacity(add.zoom(fish, 0.6), 0.5), [TANK[0] + 1.2, 2.2, TANK[2] - 0.6]))
add.mesh(add.move(add.make(add.prism, [[0, 0], [0.7, 0.45], [0.7, -0.45]], 0.08,
                           "orange", (0, 0, 0), (0, 0, 1)),
                  [TANK[0] + 0.5, 1.5, TANK[2]]))
add.sphere([TANK[0] - 1.05, 1.62, TANK[2] + 0.22], 0.07, 4, "black")

# --- 4. a brick house you can look into ------------------------------------
# The walls are hollow -- a box minus a smaller box -- and the door and the
# windows are cut right through them, so the glass sits in real openings
# and the room behind it shows.  Cut first, texture afterwards: a boolean
# rebuilds the faces and would drop the bricks.  Outside 10 cm of brick,
# inside 15 cm of plaster and a floor.
HOUSE = [3.5, 0, 0]
hx, hz = HOUSE[0], HOUSE[2]
W, D, H = 5.0, 4.0, 2.8                                     # outside: width (x), depth (z), height
openings = [add.make(add.cuboid, [hx, 1.07, hz + 2.0], [1.0, 1.9, 0.8]),         # the door, from the floorboards up
            add.make(add.cuboid, [hx - 1.5, 1.6, hz + 2.0], [1.2, 1.0, 0.8]),   # two windows in front
            add.make(add.cuboid, [hx + 1.5, 1.6, hz + 2.0], [1.2, 1.0, 0.8]),
            add.make(add.cuboid, [hx + 2.5, 1.6, hz], [0.8, 1.0, 2.0]),         # one on each side
            add.make(add.cuboid, [hx - 2.5, 1.6, hz], [0.8, 1.0, 1.6]),
            add.make(add.cuboid, [hx, 1.6, hz - 2.0], [1.6, 1.0, 0.8])]         # and one at the back
bricks = add.difference(add.make(add.cuboid, [hx, H / 2, hz], [W, H, D]),
                        add.make(add.cuboid, [hx, H / 2, hz], [W - 0.2, H + 1, D - 0.2]), *openings)
add.mesh(add.texture(bricks, "bricks.png", "box", scale=1.5))
plaster = add.difference(add.make(add.cuboid, [hx, H / 2, hz], [W - 0.2, H, D - 0.2]),
                         add.make(add.cuboid, [hx, 1.55, hz], [W - 0.5, 2.9, D - 0.5]), *openings)
add.mesh(add.color(plaster, [236, 228, 208]))
add.cuboid([hx, 2.77, hz], [W - 0.5, 0.06, D - 0.5], [236, 228, 208])            # the ceiling, under the roof
floor = add.make(add.cuboid, [hx, 0.11, hz], [W - 0.5, 0.02, D - 0.5])
add.mesh(add.texture(floor, "wood.png", "xz", scale=1.0))                       # floorboards


def window(x, z, w, along):
    """Glass in the opening at (x, 1.6, z), ``w`` wide and 1 high, in a
    white frame with a cross of glazing bars; ``along`` is the axis the
    wall runs along ("x" for the front and back, "z" for the sides)."""
    def bar(dx, dy, sx, sy):                                  # a bar across the wall's plane
        if along == "x":
            add.cuboid([x + dx, 1.6 + dy, z], [sx, sy, 0.08], "white")
        else:
            add.cuboid([x, 1.6 + dy, z + dx], [0.08, sy, sx], "white")
    add.cuboid([x, 1.6, z], [w, 1.0, 0.03] if along == "x" else [0.03, 1.0, w], glass)
    for dy in (-0.47, 0.47):
        bar(0, dy, w, 0.06)                                   # sill and head of the frame
    for dx in (-w / 2 + 0.03, w / 2 - 0.03):
        bar(dx, 0, 0.06, 1.0)                                 # its sides
    bar(0, 0, 0.05, 1.0)                                      # the glazing bars
    bar(0, 0.05, w, 0.05)


window(hx - 1.5, hz + 1.875, 1.2, "x")
window(hx + 1.5, hz + 1.875, 1.2, "x")
window(hx, hz - 1.875, 1.6, "x")
window(hx + 2.375, hz, 2.0, "z")
window(hx - 2.375, hz, 1.6, "z")
door = add.make(add.cuboid, [hx, 1.07, hz + 1.8], [0.98, 1.88, 0.05], [90, 60, 30])
door.extend(add.make(add.sphere, [hx + 0.38, 1.05, hz + 1.84], 0.04, 6, "gold"))  # the handle
add.mesh(add.rotateY(door, 1.35, [hx - 0.49, 0, hz + 1.8]))   # open: swung in on its hinge
add.roof([hx, H, hz], [W, D], 1.4, [120, 40, 30], overhang=0.3)

# the room: a rug, a table with a lamp (its glass shade is see-through
# too), two chairs, a bed, a shelf of books and a map on the wall
add.cuboid([hx, 0.13, hz + 0.2], [2.2, 0.02, 1.5], [150, 40, 40])
add.cuboid([hx, 0.84, hz + 0.2], [1.2, 0.06, 0.8], "brown")
for dx in (-0.54, 0.54):
    for dz in (-0.34, 0.34):
        add.cuboid([hx + dx, 0.47, hz + 0.2 + dz], [0.06, 0.72, 0.06], "brown")
add.cylinder([hx, 0.87, hz + 0.2], [hx, 1.2, hz + 0.2], 0.03, 8, "gold")
add.sphere([hx, 1.32, hz + 0.2], 0.16, 10, add.transparent("yellow", 0.6))
for s in (-1, 1):                                             # the chairs, facing the table
    cx = hx + s * 0.95
    add.cuboid([cx, 0.55, hz + 0.2], [0.45, 0.05, 0.45], "brown")
    for dx in (-0.19, 0.19):
        for dz in (-0.19, 0.19):
            add.cuboid([cx + dx, 0.33, hz + 0.2 + dz], [0.05, 0.43, 0.05], "brown")
    add.cuboid([cx + s * 0.2, 0.85, hz + 0.2], [0.05, 0.6, 0.45], "brown")
add.cuboid([hx - 1.24, 0.3, hz - 1.2], [2.0, 0.36, 1.0], [90, 60, 30])          # the bed: frame,
add.cuboid([hx - 1.24, 0.54, hz - 1.2], [1.9, 0.12, 0.9], "white")              # mattress,
add.cuboid([hx - 1.1, 0.62, hz - 1.2], [1.5, 0.06, 0.94], [40, 70, 160])        # blanket
add.cuboid([hx - 1.94, 0.65, hz - 1.2], [0.35, 0.1, 0.6], "white")              # and pillow
sx, sz = hx + 1.55, hz - 1.55                                 # the shelf: a back, two sides, four boards ...
add.cuboid([sx, 0.95, sz - 0.13], [1.2, 1.7, 0.04], "brown")
for dx in (-0.58, 0.58):
    add.cuboid([sx + dx, 0.95, sz], [0.04, 1.7, 0.3], "brown")
for level in (0.12, 0.6, 1.08, 1.76):
    add.cuboid([sx, level + 0.015, sz], [1.12, 0.03, 0.26], "brown")
    x = sx - 0.54
    while level < 1.5 and x + 0.1 < sx + 0.54:              # ... and rows of books
        t = add.uniform(0.05, 0.1)
        add.cuboid([x + t / 2, level + 0.17, sz + 0.02], [t, 0.28, 0.2],
                   add.choice(["red", [40, 70, 160], [60, 120, 60], "gold"]))
        x += t + 0.015
picture = add.make(add.cuboid, [hx - 1.5, 1.75, hz - 1.73], [1.1, 0.6, 0.03])
add.mesh(add.texture(picture, "planet.png", "fit"))                             # a map of the planet
add.cuboid([hx - 1.5, 1.75, hz - 1.74], [1.2, 0.7, 0.02], [90, 60, 30])         # in a frame

# --- 5. a globe with the planet map, on a chequered stand ------------------
globe = add.make(add.sphere, [0, 0, 0], 1.1, 30, "white")
globe = add.rotateX(globe, 0.4)
add.mesh(add.move(add.texture(globe, "planet.png", "sphere"), [-0.6, 1.9, 2.7]))
stand = add.make(add.cylinder, [-0.6, 0, 2.7], [-0.6, 0.8, 2.7], 0.5, 24, "white")
add.mesh(add.texture(stand, "check.png", "cylinder", scale=6))

add.check()
model = add.layer()                                      # saving twice: keep it
add.save("glass_and_textures.off", model)                # colours only
add.save("glass_and_textures.obj", model)                # + .mtl with d and map_Kd
print("for Sketchfab: zip glass_and_textures.obj, .mtl and the four .png files")

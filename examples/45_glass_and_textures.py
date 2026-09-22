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

The scene: a fish tank with glass walls and water, a brick house with
glass windows on a wooden table, and a textured globe.  Everything
without transparency or textures is exactly as before, so ``.off`` files
of old models are unchanged.

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

# --- 4. a brick house with glass windows and a roof of shingles ------------
HOUSE = [3.5, 0, 0]
walls = add.make(add.cuboid, [HOUSE[0], 1.4, HOUSE[2]], [5, 2.8, 4], "red")
door = add.make(add.cuboid, [HOUSE[0], 0.9, HOUSE[2] + 2.0], [1.0, 1.8, 0.3], "red")
win1 = add.make(add.cuboid, [HOUSE[0] - 1.5, 1.6, HOUSE[2] + 2.0], [1.2, 1.0, 0.3], "red")
win2 = add.make(add.cuboid, [HOUSE[0] + 1.5, 1.6, HOUSE[2] + 2.0], [1.2, 1.0, 0.3], "red")
win3 = add.make(add.cuboid, [HOUSE[0] + 2.5, 1.6, HOUSE[2]], [0.3, 1.0, 2.0], "red")
for hole in (door, win1, win2, win3):
    walls = add.difference(walls, hole)
add.mesh(add.texture(walls, "bricks.png", "box", scale=1.5))
add.cuboid([HOUSE[0] - 1.5, 1.6, HOUSE[2] + 2.0], [1.2, 1.0, 0.04], glass)
add.cuboid([HOUSE[0] + 1.5, 1.6, HOUSE[2] + 2.0], [1.2, 1.0, 0.04], glass)
add.cuboid([HOUSE[0] + 2.5, 1.6, HOUSE[2]], [0.04, 1.0, 2.0], glass)
add.cuboid([HOUSE[0], 0.9, HOUSE[2] + 2.0], [1.0, 1.8, 0.06], [90, 60, 30])   # the door
add.roof([HOUSE[0], 2.8, HOUSE[2]], [5.0, 4.0], 1.4, [120, 40, 30], overhang=0.3)
# something to see through the windows: a table lamp inside
add.cylinder([HOUSE[0], 0, HOUSE[2]], [HOUSE[0], 1.2, HOUSE[2]], 0.08, 8, "gold")
add.sphere([HOUSE[0], 1.4, HOUSE[2]], 0.35, 8, add.transparent("yellow", 0.7))

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

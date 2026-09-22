"""
46 -- Algoritmų pilis: the castle. The showcase model of add.py 2.0.

A castle on a hill in a lake, with everything a castle needs: an octagonal
curtain wall of individual bricks with eight round towers, a gatehouse with
a portcullis and a drawbridge hanging on real chains, a palace with round
towers and copper spires, a chapel with stained glass, a great hall behind
glass windows, and a courtyard full of life -- barrels, crates, stacks of
planks and bricks, a well, a cart, a trebuchet, a smithy, weapon racks,
suits of armour, banners, torches, trees.  The lake is transparent, so the
fish, the pebbles and the sunken boat can be seen through the water.

Easter eggs, for anyone who walks inside: the great hall with the king's
throne, a feast laid on the long table (roast pig, chickens, bread, cheese,
fruit, wine), chandeliers, a chess game in progress, the name of the castle
carved above the throne -- and, in the ground floor of the big tower, a
treasure with a dragon asleep on it.

Every brick, plank, chain link, cobblestone and roof tile is its own piece
of geometry, so the file is written *streaming* (``add.stream``): parts go
to disk as soon as they are finished and the model can be far bigger than
the memory of the computer.

    python3 46_castle.py              Sketchfab size: 26 MB, 48 materials, 10 s
    python3 46_castle.py --full       every cobblestone and grass tuft, ~180 MB
    python3 46_castle.py --ultra      more than a gigabyte (a few minutes)

Parameter: ``DETAIL`` (1, 2 or 3, also set by the flags above).  For
Sketchfab zip castle.obj, castle.mtl and the castle_*.png textures.
"""
import sys
import time

import add

DETAIL = 1
if "--full" in sys.argv:
    DETAIL = 2
if "--ultra" in sys.argv:
    DETAIL = 3
OUT = {1: "castle.obj", 2: "castle_full.obj", 3: "castle_ultra.obj"}[DETAIL]
add.seed(2026)
started = time.time()

# --------------------------------------------------------------------------
#  Palette -- a fixed set of colours, so the Sketchfab variant stays under
#  50 materials (colours + textures + glass are all materials in an .obj).
# --------------------------------------------------------------------------
P = {
    "stone": [196, 186, 160], "stone_dark": [150, 140, 118], "mortar": [120, 112, 98],
    "brick": [172, 96, 62], "brick_dark": [138, 72, 46], "brick_light": [196, 120, 82],
    "wood": [128, 86, 48], "wood_dark": [88, 58, 32], "wood_light": [176, 128, 80],
    "iron": [70, 70, 76], "steel": [190, 195, 205], "gold": [222, 178, 60],
    "copper": [72, 150, 120], "slate": [70, 82, 104], "red": [178, 34, 40],
    "white": [240, 236, 226], "black": [28, 26, 26], "leaf": [62, 124, 48],
    "leaf_dark": [40, 92, 36], "trunk": [92, 64, 40], "grass": [96, 150, 58],
    "grass_dry": [140, 158, 70], "rock": [118, 112, 104], "sand": [200, 184, 140],
    "lakebed": [150, 140, 110], "straw": [214, 178, 92], "rope": [178, 150, 96],
    "bread": [196, 140, 76], "cheese": [232, 196, 80], "meat": [150, 78, 52],
    "apple": [190, 40, 40], "grape": [110, 50, 130], "orange": [230, 140, 40],
    "pig": [226, 168, 150], "cushion": [150, 24, 40], "blue": [40, 70, 160],
    "purple": [96, 40, 140], "flame_core": [255, 230, 120], "bone": [226, 220, 200],
    "dragon": [56, 120, 70], "dragon_belly": [180, 190, 120], "glass_frame": [60, 60, 66],
    "water_dark": [30, 70, 110],
}
if DETAIL == 1:                                        # fewer materials for Sketchfab: near colours share one
    for a, b in (("mortar", "stone_dark"), ("rock", "stone_dark"), ("lakebed", "sand"), ("bone", "white"),
                 ("cushion", "red"), ("glass_frame", "iron"), ("trunk", "wood_dark"), ("straw", "cheese"),
                 ("bread", "wood_light"), ("rope", "wood_light"), ("apple", "red"), ("dragon_belly", "leaf"),
                 ("brick_dark", "brick"), ("brick_light", "brick"), ("water_dark", "blue")):
        P[a] = P[b]
GLASS = add.transparent([170, 210, 245], 0.35)
WATER = add.transparent([50, 120, 200], 0.5)
FLAME = add.transparent([255, 150, 40], 0.65)
SMOKE = add.transparent([150, 150, 160], 0.3)


def k_(n):
    """Sides of a round part, scaled by the detail level."""
    return max(6, int(n * (0.6, 1.0, 1.6)[DETAIL - 1]))


# --------------------------------------------------------------------------
#  Textures, drawn pixel by pixel with add.write_png
# --------------------------------------------------------------------------
def png(name, w, h, pixel):
    add.write_png(name, [[pixel(x, y) for x in range(w)] for y in range(h)])
    return name


def hash2(x, y, s=0):
    """A cheap repeatable pseudo-random number in 0..1 for pixel (x, y)."""
    n = (x * 374761393 + y * 668265263 + s * 1274126177) & 0xffffffff
    n = (n ^ (n >> 13)) * 1274126177 & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffff) / 65535.0


def ashlar(x, y):                                      # cut stone blocks
    course, row_y = divmod(y, 32)
    xx = (x + (32 if course % 2 else 0)) % 64
    if row_y < 3 or xx < 3:
        return P["mortar"]
    v = 0.85 + 0.3 * hash2(x // 64 + (course % 2) * 100, course) + 0.06 * hash2(x, y, 3)
    return add.shade(P["stone"], v)


def brick_px(x, y):
    course, row_y = divmod(y, 16)
    xx = (x + (16 if course % 2 else 0)) % 32
    if row_y < 2 or xx < 2:
        return [205, 198, 185]
    return add.shade(P["brick"], 0.8 + 0.4 * hash2(x // 32 + (course % 2) * 50, course))




def slate_px(x, y):
    row, ry = divmod(y, 12)
    xx = (x + (10 if row % 2 else 0)) % 20
    if ry < 2 or xx < 2:
        return [40, 46, 60]
    return add.shade(P["slate"], 0.8 + 0.4 * hash2(x // 20, row))


def planks_px(x, y):
    plank = x // 24
    grain = 0.5 + 0.5 * add.sin(y / 5.0 + 3 * add.sin(x / 9.0 + plank))
    if x % 24 < 2:
        return P["wood_dark"]
    return add.gradient(0.35 * grain + 0.3 * hash2(plank, 0), P["wood_light"], P["wood"])


def cobble_px(x, y):
    cx, cy = (x // 24) * 24 + 12 + int(8 * hash2(x // 24, y // 24)) - 4, (y // 24) * 24 + 12
    d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
    if d > 10:
        return [96, 88, 76]
    return add.shade([160, 150, 132], 0.75 + 0.4 * hash2(x // 24, y // 24, 7) + 0.15 * (1 - d / 10))


def banner_px(x, y):                                   # the coat of arms of the castle
    w, h = 96, 128
    if y > h - 24 + abs(x - w / 2) * 0.5:              # the pointed bottom of the shield
        return [0, 0, 0]
    if abs((x - w / 2) - (y - h / 2) * 0.6) < 10:      # a gold bend
        return P["gold"]
    for cx, cy in ((24, 32), (72, 32), (48, 96)):      # three white roundels
        if (x - cx) ** 2 + (y - cy) ** 2 < 100:
            return P["white"]
    return P["red"] if (x + y) % 2 else add.shade(P["red"], 0.9)


def stained_px(x, y):
    if x % 16 < 2 or y % 16 < 2:
        return [30, 30, 30]
    palette = [[200, 40, 40], [40, 60, 180], [230, 190, 40], [40, 150, 70], [230, 230, 240]]
    return palette[int(5 * hash2(x // 16, y // 16, 11))]




def marble_px(x, y):
    v = add.sin(x / 11.0 + 2 * add.sin(y / 17.0)) * add.cos(y / 13.0)
    return add.gradient(0.5 + 0.5 * v, [236, 232, 226], [190, 186, 182])




TEX = {
    "stone": png("castle_stone.png", 128, 128, ashlar),
    "brick": png("castle_brick.png", 128, 128, brick_px),
    "slate": png("castle_slate.png", 80, 96, slate_px),
    "planks": png("castle_planks.png", 96, 96, planks_px),
    "cobble": png("castle_cobble.png", 96, 96, cobble_px),
    "banner": png("castle_banner.png", 96, 128, banner_px),
    "glass": png("castle_glass.png", 64, 96, stained_px),
    "marble": png("castle_marble.png", 96, 96, marble_px),
}


def textured(M, name, mapping="box", scale=1.0):
    return add.texture(M, TEX[name], mapping, scale=scale)


# --------------------------------------------------------------------------
#  Streaming output: every finished part goes straight to the file
# --------------------------------------------------------------------------
out = add.stream(OUT)                                  # an add.Stream


def flush(label):
    n = out.add()
    print("  %-28s %9d faces  %7.1f MB  %5.0fs" % (label, n, out.bytes / 1e6, time.time() - started))


# --------------------------------------------------------------------------
#  1. The hill, the lake and the moat
# --------------------------------------------------------------------------
PLATEAU = 14.0
WATER_Y = 1.5
WORLD = 300.0                                          # the lake is this wide
MOAT = (-20, 20, 54, 62)                               # x0, x1, z0, z1 (on grid lines)
MOAT_Y = 9.0


def ground(x, z):
    """Height of the land: a plateau, a slope, a cliff and the lake bed."""
    r = add.sqrt(x * x + z * z)
    if r <= 58:
        return PLATEAU
    cliff = add.clamp((-x / max(r, 1) - 0.55) / 0.3)      # the west side is a cliff
    run = add.lerp(36.0, 14.0, cliff)
    t = add.clamp((r - 58) / run)
    y = PLATEAU - 13.0 * t * t * (3 - 2 * t)
    if r > 58 + run:                                    # the shore and the lake bed
        y = 1.0 - 0.18 * (r - 58 - run)
    return max(y, -4.5) + 0.35 * add.sin(x / 7.0) * add.cos(z / 9.0) * (1 if r > 58 else 0)


def ground_color(x, z):
    y = ground(x, z)
    slope = abs(ground(x + 1, z) - y) + abs(ground(x, z + 1) - y)
    if y < WATER_Y + 0.4:
        return P["lakebed"] if y < WATER_Y - 0.5 else P["sand"]
    if slope > 0.9:
        return P["rock"]
    patch = add.sin(x / 9.0) * add.cos(z / 11.0) + 0.5 * add.sin(x / 4.0 + z / 5.0)
    return P["grass_dry"] if patch > 0.55 else P["grass"]


N_GROUND = (150, 300, 600)[DETAIL - 1]                 # cells of 2, 1 and 0.5 units
land = add.Mesh()
index = {}


def land_vertex(i, j):
    if (i, j) not in index:
        x, z = -WORLD / 2 + WORLD * i / N_GROUND, -WORLD / 2 + WORLD * j / N_GROUND
        index[(i, j)] = land.add_vertex([x, ground(x, z), z])
    return index[(i, j)]


cell = WORLD / N_GROUND
for i in range(N_GROUND):
    for j in range(N_GROUND):
        x, z = -WORLD / 2 + (i + 0.5) * cell, -WORLD / 2 + (j + 0.5) * cell
        if MOAT[0] < x < MOAT[1] and MOAT[2] < z < MOAT[3]:
            continue                                   # the moat is dug out here
        land.add_face([land_vertex(i, j), land_vertex(i, j + 1),
                       land_vertex(i + 1, j + 1), land_vertex(i + 1, j)], ground_color(x, z))
add.mesh(land)
land, index = None, None                               # free the memory
# the moat: a stone-lined pit with a kerb, and a floor of rock
for x0, x1, z0, z1 in ((MOAT[0] - 1, MOAT[0], MOAT[2] - 1, MOAT[3] + 1), (MOAT[1], MOAT[1] + 1, MOAT[2] - 1, MOAT[3] + 1),
                       (MOAT[0], MOAT[1], MOAT[2] - 1, MOAT[2]), (MOAT[0], MOAT[1], MOAT[3], MOAT[3] + 1)):
    add.cuboid([(x0 + x1) / 2, (MOAT_Y - 0.5 + PLATEAU + 0.3) / 2, (z0 + z1) / 2],
               [x1 - x0, PLATEAU + 0.3 - MOAT_Y + 0.5, z1 - z0], P["stone_dark"])
add.cuboid([0, MOAT_Y - 0.25, (MOAT[2] + MOAT[3]) / 2], [MOAT[1] - MOAT[0], 0.5, MOAT[3] - MOAT[2]], P["rock"])
flush("hill, lake bed and moat")

# the water: one sheet with gentle ripples, given a thickness so it has an underside
def ripple(x, z):
    return WATER_Y + 0.08 * add.sin(x / 3.0 + z / 5.0) + 0.05 * add.cos(z / 2.5)


add.grid([0, 0, 0], [WORLD, WORLD], (60, 150, 300)[DETAIL - 1], (60, 150, 300)[DETAIL - 1],
         color=WATER, height=ripple, thickness=0.4)
add.cuboid([0, (MOAT_Y + 12.5) / 2, (MOAT[2] + MOAT[3]) / 2],
           [MOAT[1] - MOAT[0], 12.5 - MOAT_Y, MOAT[3] - MOAT[2]], WATER)   # the moat
flush("water")

# under the water: pebbles, fish, reeds, lily pads and a sunken rowing boat
add.seed(7)
N_PEBBLES = (1500, 25000, 140000)[DETAIL - 1]
for i in range(N_PEBBLES):
    a, r = add.uniform(0, 2 * add.pi), 96 + 39 * add.sqrt(add.random())
    x, z = r * add.cos(a), r * add.sin(a)
    add.sphere([x, ground(x, z) + 0.1, z], add.uniform(0.15, 0.5), 4,
               add.choice([P["rock"], P["stone_dark"], P["sand"]]))
    if (i + 1) % 20000 == 0:
        flush("pebbles (%d)" % (i + 1))
for i in range((30, 150, 3000)[DETAIL - 1]):               # fish
    a, r = add.uniform(0, 2 * add.pi), add.uniform(100, 130)
    x, z = r * add.cos(a), r * add.sin(a)
    fish = add.stretch(add.make(add.sphere, [0, 0, 0], 0.5, 6), [1.6, 0.9, 0.45])
    fish = add.color(fish, add.choice([P["orange"], P["steel"], P["gold"]]))
    tail = add.make(add.prism, [[0, 0], [0.6, 0.35], [0.6, -0.35]], 0.06, P["orange"],
                    (0.75, 0, 0), (0, 0, 1))
    add.mesh(add.move(add.rotateY(add.merge([fish, tail]), a + add.pi / 2), [x, add.uniform(-2, 1), z]))
for i in range((40, 200, 800)[DETAIL - 1]):                # reeds near the shore
    a, r = add.uniform(0, 2 * add.pi), add.uniform(93, 98)
    x, z = r * add.cos(a), r * add.sin(a)
    for j in range(3):
        add.cylinder([x + j * 0.2, ground(x, z), z], [x + j * 0.25, WATER_Y + add.uniform(1, 2.2), z + 0.1],
                     0.04, 5, P["leaf_dark"])
for i in range((30, 120, 400)[DETAIL - 1]):                # lily pads
    a, r = add.uniform(0, 2 * add.pi), add.uniform(94, 102)
    add.disc([r * add.cos(a), WATER_Y + 0.02, r * add.sin(a)], [0, 1, 0], add.uniform(0.3, 0.6), 12, P["leaf"])
# the sunken boat: planks of a hull, lying on the bed
boat = add.Mesh()
for j in range(7):
    t = j / 6.0
    w = 2.0 * add.sin(add.pi * t) + 0.4
    boat.extend(add.make(add.cuboid, [0, 0.35 * (1 - w / 2.4), (t - 0.5) * 7], [w, 0.15, 1.05], P["wood_dark"]))
boat = add.rotate(boat, [1, 0, 0.3], 0.5)
add.mesh(add.move(boat, [70, ground(70, 82) + 0.6, 82]))
add.cuboid([70, ground(70, 82) + 0.3, 82], [1.2, 0.8, 0.8], P["wood"])          # a chest
flush("under water")

# the road up the hill: a cobbled strip following the ground, and a jetty
def road(u, v):
    z = 63 + u * 33
    x = v * 6 - 3 + 4 * add.sin(u * 3)
    return [x, ground(x, z) + 0.12, z]


road_mesh = add.make(add.parametric, road, 0, 1, 60, 0, 1, 6, P["stone"])
add.mesh(textured(road_mesh, "cobble", "xz", scale=3))
for i in range(12):                                         # the jetty into the lake
    z = 94 + i * 1.0
    add.cuboid([1.0, WATER_Y + 0.35, z], [3.0, 0.12, 0.85], P["wood"])
for z in (94, 100, 105.5):
    for x in (-0.4, 2.4):
        add.cylinder([x, ground(x, z), z], [x, WATER_Y + 0.9, z], 0.15, 8, P["wood_dark"])
# a rowing boat tied to the jetty
boat = add.Mesh()
for j in range(7):
    t = j / 6.0
    w = 1.8 * add.sin(add.pi * t) + 0.3
    boat.extend(add.make(add.cuboid, [0, 0.3 * (1 - w / 2.1), (t - 0.5) * 5], [w, 0.12, 0.75], P["wood"]))
boat.extend(add.make(add.cuboid, [0, 0.45, 0], [1.6, 0.08, 0.3], P["wood_light"]))    # thwart
for s in (-1, 1):
    boat.extend(add.make(add.cylinder, [s * 0.9, 0.5, 0.2], [s * 2.2, 0.2, -1.5], 0.05, 6, P["wood_light"]))
add.mesh(add.move(boat, [4.5, WATER_Y - 0.1, 99]))
add.polyline([[2.4, WATER_Y + 0.9, 100], [3.6, WATER_Y + 0.4, 99.5]], 0.03, 6, P["rope"])
flush("road and jetty")

# the forest on the slopes
add.seed(11)
trees = 0
while trees < (140, 260, 360)[DETAIL - 1]:
    a, r = add.uniform(0, 2 * add.pi), add.uniform(60, 90)
    x, z = r * add.cos(a), r * add.sin(a)
    if MOAT[0] - 6 < x < MOAT[1] + 6 and z > 40:          # keep the road clear
        continue
    y = ground(x, z)
    if y < WATER_Y + 1.5:
        continue
    kind = "pine" if hash2(trees, 1) > 0.5 else "round"
    h = add.uniform(4, 9)
    leaf = P["leaf"] if hash2(trees, 2) > 0.4 else P["leaf_dark"]
    add.tree([x, y - 0.2, z], h, P["trunk"], leaf, kind, k_(8), seed=trees)
    if DETAIL == 3:                                        # single leaves all over the crown
        for j in range(600):
            u, v, w = add.gauss(0, 1), add.gauss(0, 1), add.gauss(0, 1)
            L = add.sqrt(u * u + v * v + w * w) or 1.0
            rr = 0.36 * h if kind == "round" else 0.3 * h * (1 - abs(v) / L)
            cy = y + (0.55 * h if kind == "round" else 0.5 * h)
            c = [x + rr * u / L, cy + rr * v / L * (1.0 if kind == "round" else 1.4), z + rr * w / L]
            a = hash2(j, trees) * 6.28
            q = [[c[0] - 0.12 * add.cos(a), c[1], c[2] - 0.12 * add.sin(a)], [c[0] + 0.12 * add.cos(a), c[1], c[2] + 0.12 * add.sin(a)],
                 [c[0] + 0.12 * add.cos(a), c[1] + 0.2, c[2] + 0.12 * add.sin(a)], [c[0] - 0.12 * add.cos(a), c[1] + 0.2, c[2] - 0.12 * add.sin(a)]]
            add.polygon(q, P["leaf"] if (j % 2) else leaf)
    trees += 1
    if trees % 60 == 0:
        flush("forest (%d trees)" % trees)
flush("forest")

if DETAIL >= 2:                                            # tufts of grass on the slopes and the meadow
    add.seed(13)
    n = 0
    while n < (30000, 300000)[DETAIL - 2]:
        a, r = add.uniform(0, 2 * add.pi), 52 + 40 * add.sqrt(add.random())
        x, z = r * add.cos(a), r * add.sin(a)
        y = ground(x, z)
        if y < WATER_Y + 1.0 or (abs(x) < 5.5 and z > 50) or (MOAT[0] - 1 < x < MOAT[1] + 1 and MOAT[2] - 1 < z < MOAT[3] + 1):
            continue
        for j in range(3):
            b = a + j * 2.1 + hash2(n, j)
            h = 0.25 + 0.3 * hash2(n, j, 2)
            add.polygon([[x - 0.05 * add.cos(b), y, z - 0.05 * add.sin(b)], [x + 0.05 * add.cos(b), y, z + 0.05 * add.sin(b)],
                         [x + 0.12 * add.sin(b), y + h, z - 0.12 * add.cos(b)]], P["leaf"] if hash2(n, j, 3) > 0.5 else P["grass"])
        n += 1
        if n % 30000 == 0:
            flush("grass (%d tufts)" % n)
    flush("grass")

# --------------------------------------------------------------------------
#  Building blocks used all over the castle
# --------------------------------------------------------------------------
G = PLATEAU                                            # the ground level inside the walls
BLOCK = {1: (1.6, 0.8), 2: (1.0, 0.5), 3: (0.6, 0.3)}[DETAIL]   # size of one wall stone


def shade_of(name, i, n=3, spread=0.16):
    """One of ``n`` fixed shades of a palette colour.  The shades are fixed
    (not random) so that the material count of the file stays small; the
    Sketchfab variant uses two shades, the others three."""
    if DETAIL == 1:
        if name not in ("stone", "stone_dark"):
            return P[name]
        i, n = i % 2, 2
    key = "%s~%d" % (name, i)
    if key not in P:
        P[key] = add.shade(P[name], 1 - spread + 2 * spread * i / max(1, n - 1))
    return P[key]


def pick(name, x, y, n=3):
    """A repeatable shade for the stone / brick / plank at (x, y)."""
    return shade_of(name, int(hash2(int(x * 7), int(y * 7)) * n) % n, n)


def frame_to(M, a, d, n):
    """Move a part built along +X (with +Z = outward) so that +X runs along
    ``d`` and +Z along ``n``, starting from point ``a``."""
    return add.transform(M, [[d[0], 0, n[0], a[0]],
                             [0, 1, 0, a[1]],
                             [d[2], 0, n[2], a[2]]])


def outward(a, b, centre=(0, 0)):
    """Unit direction a -> b in XZ and the unit normal pointing away from ``centre``."""
    dx, dz = b[0] - a[0], b[2] - a[2]
    L = add.sqrt(dx * dx + dz * dz)
    d = (dx / L, 0, dz / L)
    n = (dz / L, 0, -dx / L)
    mx, mz = (a[0] + b[0]) / 2 - centre[0], (a[2] + b[2]) / 2 - centre[1]
    if n[0] * mx + n[2] * mz < 0:
        n = (-n[0], 0, -n[2])
    return L, d, n


def stone_face(length, y0, y1, z, depth, name="stone", size=None, gap=0.06, seed=0):
    """A skin of staggered stone blocks on the plane ``z`` (facing +Z when
    ``depth`` > 0), from x = 0..length and y0..y1, drawn into the scene."""
    bl, bh = size or BLOCK
    rows = max(1, int(round((y1 - y0) / bh)))
    bh = (y1 - y0) / rows
    for j in range(rows):
        y = y0 + j * bh
        x = -(bl / 2) if j % 2 else 0.0
        while x < length:
            x0, x1 = max(x, 0.0), min(x + bl, length)
            if x1 - x0 > 0.08:
                add.cuboid([(x0 + x1) / 2, y + bh / 2, z + depth / 2],
                           [x1 - x0 - gap, bh - gap, abs(depth)], pick(name, x + seed * 97, j + seed))
            x += bl


def merlons(length, y, z0, z1, h=1.6, w=1.4, gap=0.9, name="stone"):
    """A crenellated parapet along x = 0..length at height ``y``, between z0 and z1."""
    x = 0.0
    i = 0
    while x < length - 0.3:
        w1 = min(w, length - x)
        add.cuboid([x + w1 / 2, y + h / 2, (z0 + z1) / 2], [w1, h, abs(z1 - z0)], pick(name, i, 3))
        x += w + gap
        i += 1


def wall_segment(a, b, y0, y1, t=2.4, walk=True, inner_blocks=True):
    """A piece of curtain wall from ``a`` to ``b``: a core, faces of stone
    blocks, a walk on top with a crenellated parapet outside and a low one inside."""
    L, d, n = outward(a, b)
    add.push()
    core = add.make(add.cuboid, [L / 2, (y0 + y1) / 2, 0], [L, y1 - y0, t], P["mortar"])
    add.mesh(textured(core, "stone", scale=3.0))
    stone_face(L, y0, y1, t / 2, 0.22, "stone", seed=int(a[0] + a[2]))
    if inner_blocks:
        stone_face(L, y0, y1, -t / 2, -0.22, "stone_dark", seed=int(a[0] - a[2]))
    if walk:
        walkway = add.make(add.cuboid, [L / 2, y1 + 0.15, 0], [L, 0.3, t + 0.5], P["stone_dark"])
        add.mesh(textured(walkway, "cobble", "xz", scale=1.5))
        merlons(L, y1 + 0.3, t / 2 - 0.5, t / 2 + 0.25)
        add.cuboid([L / 2, y1 + 0.6, -t / 2 + 0.2], [L, 0.6, 0.4], P["stone"])
    M = add.pop()
    add.mesh(frame_to(M, [a[0], 0, a[2]], d, n))


def tex_round(M, name, cx, cz, r, period=3.0):
    """Texture a round part so the picture repeats every ``period`` units
    both round the drum and up it (the built-in cylinder mapping stretches)."""
    return add.texture(M, TEX[name], lambda p, n: (add.atan2(p[2] - cz, p[0] - cx) * r / period,
                                                    p[1] / period))


def cone_roof(centre, y, r, h, k, name="slate", tiles=False, color=None):
    """A conical roof: textured, plain ``color``, or (``tiles``) made of
    individual slates."""
    if color is not None:
        add.cone([centre[0], y, centre[2]], [centre[0], y + h, centre[2]], r, k, color)
        add.sphere([centre[0], y + h + 0.3, centre[2]], 0.35, k_(8), P["gold"])
        return
    if not tiles:
        add.mesh(tex_round(add.make(add.cone, [centre[0], y, centre[2]], [centre[0], y + h, centre[2]], r, k),
                           name, centre[0], centre[2], r, 1.5))
        return
    rows = max(4, int(h / 0.5))
    for j in range(rows):
        t0, t1 = j / rows, (j + 1) / rows
        r0, r1 = r * (1 - t0), r * (1 - t1)
        yy0, yy1 = y + h * t0, y + h * t1
        count = max(6, int(2 * add.pi * r0 / 0.45))
        for i in range(count):
            a0 = 2 * add.pi * (i + (0.5 if j % 2 else 0)) / count
            a1 = 2 * add.pi * (i + 0.92 + (0.5 if j % 2 else 0)) / count
            p = [[centre[0] + r0 * add.cos(a0), yy0 - 0.06, centre[2] + r0 * add.sin(a0)],
                 [centre[0] + r0 * add.cos(a1), yy0 - 0.06, centre[2] + r0 * add.sin(a1)],
                 [centre[0] + r1 * add.cos(a1), yy1, centre[2] + r1 * add.sin(a1)],
                 [centre[0] + r1 * add.cos(a0), yy1, centre[2] + r1 * add.sin(a0)]]
            add.polygon(p[::-1], shade_of("slate", (i + j) % 3))
    add.cone([centre[0], y + h - 0.5, centre[2]], [centre[0], y + h + 0.05, centre[2]], 0.25, 8, P["slate"])


def round_tower(centre, y0, y1, r, k, roof_h=None, name="stone", spire="slate", corbels=True,
                spire_color=None, slits=True):
    """A round tower on point ``centre``: a stone drum, a corbelled top with
    a walk, arrow slits, and a conical roof (``roof_h``; 0 for an open top)."""
    cx, cz = centre[0], centre[2]
    drum = add.make(add.cylinder, [cx, y0, cz], [cx, y1, cz], r, k, P["stone"])
    add.mesh(tex_round(drum, name, cx, cz, r, 3.0))
    if DETAIL >= 2:                                                # stone courses round the drum
        bl, bh = BLOCK
        rows = int((y1 - y0) / bh)
        for j in range(rows):
            count = max(6, int(2 * add.pi * r / bl))
            for i in range(count):
                a = 2 * add.pi * (i + (0.5 if j % 2 else 0)) / count
                block = add.make(add.cuboid, [0, 0, 0], [bl - 0.06, bh - 0.06, 0.24], pick(name, i, j))
                block = add.rotateY(block, -a)
                add.mesh(add.move(block, [cx + (r + 0.1) * add.cos(a), y0 + (j + 0.5) * bh, cz + (r + 0.1) * add.sin(a)]))
    if corbels:                                                    # the machicolations
        for i in range(k):
            a = 2 * add.pi * i / k
            add.cuboid([cx + (r + 0.35) * add.cos(a), y1 - 0.5, cz + (r + 0.35) * add.sin(a)], [0.5, 0.9, 0.5], P["stone_dark"])
        ring = add.make(add.cylinder, [cx, y1, cz], [cx, y1 + 0.35, cz], r + 0.7, k, P["stone_dark"])
        add.mesh(ring)
        for i in range(k):
            a = 2 * add.pi * (i + 0.5) / k
            add.cuboid([cx + (r + 0.45) * add.cos(a), y1 + 0.35 + 0.6, cz + (r + 0.45) * add.sin(a)],
                       [0.6, 1.2, 0.6], pick(name, i, 1))
    if slits:                                                      # arrow slits
        for j in range(2):
            for i in range(4):
                a = 2 * add.pi * i / 4 + add.pi / 4
                slit = add.make(add.cuboid, [0, 0, 0], [0.22, 1.5, 0.3], P["black"])
                add.mesh(add.move(add.rotateY(slit, -a), [cx + r * add.cos(a), y0 + 4 + 5 * j, cz + r * add.sin(a)]))
    if roof_h:
        cone_roof([cx, 0, cz], y1 + 0.35, r + 0.9, roof_h, k, spire, tiles=(DETAIL >= 2 and spire_color is None),
                  color=spire_color)


def square_tower(centre, y0, y1, w, roof_h, name="stone"):
    """A square tower with stone faces, a corbelled top and a pyramid roof."""
    cx, cz = centre[0], centre[2]
    core = add.make(add.cuboid, [cx, (y0 + y1) / 2, cz], [w, y1 - y0, w], P["mortar"])
    add.mesh(textured(core, "stone", scale=3.0))
    for side in range(4):
        add.push()
        stone_face(w, y0, y1, w / 2, 0.22, name, seed=side + int(cx))
        M = add.pop()
        add.mesh(add.move(add.rotateY(M, side * add.pi / 2, [w / 2, 0, 0]), [cx - w / 2, 0, cz]))
    for i in range(int(w / 0.9)):                                  # corbels
        s = -w / 2 + 0.45 + i * 0.9
        for dx, dz in ((s, w / 2 + 0.3), (s, -w / 2 - 0.3), (w / 2 + 0.3, s), (-w / 2 - 0.3, s)):
            add.cuboid([cx + dx, y1 - 0.5, cz + dz], [0.5, 0.9, 0.5], P["stone_dark"])
    add.cuboid([cx, y1 + 0.2, cz], [w + 1.4, 0.4, w + 1.4], P["stone_dark"])
    ww = w + 1.4
    side = add.make(merlons, ww, 0.4, 0, 0.5)                     # one side of the parapet
    for i in range(4):
        add.mesh(add.move(add.rotateY(side, i * add.pi / 2, [ww / 2, 0, ww / 2]), [cx - ww / 2, y1, cz - ww / 2]))
    if roof_h:
        e = w + 0.6
        roof = add.make(add.pyramid, [cx, y1 + 0.4 + e / 2, cz], e, roof_h)
        add.mesh(add.texture(roof, TEX["slate"], "box", scale=0.4))


# --------------------------------------------------------------------------
#  2. The curtain wall: an octagon with eight round towers
# --------------------------------------------------------------------------
R_OCT = 50.0 / add.cos(add.pi / 8)                     # corner radius for a 50-unit apothem
CORNERS = [[R_OCT * add.cos(add.pi / 8 + k * add.pi / 4), 0, R_OCT * add.sin(add.pi / 8 + k * add.pi / 4)]
           for k in range(8)]
WALL_TOP = G + 12
GATE_X = 10.5                                          # the gatehouse takes the middle of the south wall

for k in range(8):
    a, b = CORNERS[k], CORNERS[(k + 1) % 8]
    if k == 1:                                         # the south wall, in two halves
        wall_segment(a, [GATE_X, 0, 50.0], G - 1, WALL_TOP)
        wall_segment([-GATE_X, 0, 50.0], b, G - 1, WALL_TOP)
    else:
        wall_segment(a, b, G - 1, WALL_TOP)
    flush("curtain wall %d" % (k + 1))

for k, c in enumerate(CORNERS):
    round_tower(c, G - 1, G + 16, 4.5, k_(24), roof_h=8)
    flush("tower %d" % (k + 1))


# --------------------------------------------------------------------------
#  3. The gatehouse: two square towers, an arched passage, a portcullis,
#     a drawbridge on chains, banners and two guards in armour
# --------------------------------------------------------------------------
def arch_fill(x0, x1, ys, y1, z0, z1, cx, r, color, n=None):
    """The piece of wall above an arched opening: everything between the
    arc (centre ``(cx, ys)``, radius ``r``) and the rectangle x0..x1, ys..y1,
    extruded from z0 to z1.  Returned as a closed, welded mesh."""
    n = n or k_(16)
    arc = [(cx + r * add.cos(add.pi * i / n), ys + r * add.sin(add.pi * i / n)) for i in range(n + 1)]
    corners = [(x1, ys), (x1, y1), (x0, y1), (x0, ys)]
    lengths = [y1 - ys, x1 - x0, y1 - ys]
    total = float(sum(lengths))

    def rim(t):                                        # a point on the rectangle, by fraction
        d = t * total
        for (ax, ay), (bx, by), L in zip(corners, corners[1:], lengths):
            if d <= L + 1e-9:
                return (ax + (bx - ax) * d / L, ay + (by - ay) * d / L)
            d -= L
        return corners[-1]

    rect = [rim(i / float(n)) for i in range(n + 1)]
    M = add.Mesh()

    def at(p, z):
        return [p[0], p[1], z]

    for i in range(n):
        M.add_polygon([at(rect[i], z1), at(rect[i + 1], z1), at(arc[i + 1], z1), at(arc[i], z1)], color)
        M.add_polygon([at(arc[i], z0), at(arc[i + 1], z0), at(rect[i + 1], z0), at(rect[i], z0)], color)
        M.add_polygon([at(arc[i], z0), at(arc[i], z1), at(arc[i + 1], z1), at(arc[i + 1], z0)], color)
        M.add_polygon([at(rect[i + 1], z0), at(rect[i + 1], z1), at(rect[i], z1), at(rect[i], z0)], color)
    M.add_polygon([at(arc[0], z0), at(arc[0], z1), at(rect[0], z1), at(rect[0], z0)], color)
    M.add_polygon([at(rect[-1], z0), at(rect[-1], z1), at(arc[-1], z1), at(arc[-1], z0)], color)
    return add.fix_normals(add.clean(M))


def voussoirs(cx, cy, r, z, depth, count, color_fn, width=0.8, thickness=0.3):
    """The wedge-shaped stones round an arch, on the face ``z``."""
    for i in range(count):
        a0, a1 = add.pi * i / count, add.pi * (i + 1) / count
        am = (a0 + a1) / 2
        stone = add.make(add.cuboid, [0, 0, 0], [(a1 - a0) * (r + width / 2) - 0.05, width, abs(depth)], color_fn(i))
        stone = add.rotateZ(stone, am - add.pi / 2)
        add.mesh(add.move(stone, [cx + (r + width / 2) * add.cos(am), cy + (r + width / 2) * add.sin(am), z + depth / 2]))


def vsub(a, b):
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]


def vlen(a):
    return add.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])


def vunit(a):
    L = vlen(a) or 1.0
    return [a[0] / L, a[1] / L, a[2] / L]


def vcross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def chain(a, b, link=0.22, thick=0.05, color=None):
    """A chain of linked rings from ``a`` to ``b``: every other link is turned
    by 90 degrees round the line, like a real chain."""
    color = color or P["iron"]
    d = vsub(b, a)
    L = vlen(d)
    d = vunit(d)
    helper = [0, 1, 0] if abs(d[1]) < 0.9 else [1, 0, 0]
    u = vunit(vcross(d, helper))
    v = vcross(d, u)
    n = max(1, int(L / (link * 1.45)))
    for i in range(n + 1):
        t = min(L, i * link * 1.45)
        c = [a[k] + d[k] * t for k in range(3)]
        add.torus(c, link, thick, k_(12), k_(6), color, axis=(u if i % 2 == 0 else v))


def armour(at, facing=0.0, weapon="spear", shield=True):
    """A suit of plate armour standing on point ``at`` (a guard, or a statue):
    helmet with visor, breastplate, pauldrons, arms, gauntlets, legs and
    boots, holding a spear or a sword, with the castle's shield."""
    add.push()
    S, D = P["steel"], P["iron"]
    kk = k_(10)
    for s in (-1, 1):                                                  # legs and boots
        add.capsule([s * 0.22, 0.25, 0], [s * 0.24, 1.0, 0], 0.13, kk, S)
        add.cuboid([s * 0.24, 0.1, 0.1], [0.26, 0.2, 0.5], D)
        add.sphere([s * 0.24, 0.98, 0], 0.16, kk, D)                     # knee
    add.capsule([0, 1.05, 0], [0, 1.95, 0], 0.33, kk, S)                 # breastplate
    add.cuboid([0, 1.1, 0], [0.75, 0.25, 0.55], D)                       # fauld
    for s in (-1, 1):                                                  # pauldrons and arms
        add.sphere([s * 0.42, 1.85, 0], 0.2, kk, D)
        add.capsule([s * 0.48, 1.75, 0], [s * 0.55, 1.1, 0.15], 0.1, kk, S)
        add.sphere([s * 0.56, 1.05, 0.2], 0.12, kk, D)                   # gauntlet
    add.sphere([0, 2.25, 0], 0.26, kk, S)                                # helmet
    add.cuboid([0, 2.2, 0.24], [0.36, 0.05, 0.08], P["black"])          # the visor slit
    add.cone([0, 2.45, 0], [0, 2.75, 0], 0.05, 6, P["red"])              # a plume
    if weapon == "spear":
        add.cylinder([0.58, 0.0, 0.2], [0.58, 3.2, 0.2], 0.035, 6, P["wood"])
        add.cone([0.58, 3.2, 0.2], [0.58, 3.7, 0.2], 0.08, 6, S)
    else:
        add.cuboid([0.62, 1.3, 0.55], [0.06, 0.14, 1.2], S)              # sword blade
        add.cuboid([0.62, 1.3, -0.1], [0.4, 0.06, 0.08], P["gold"])      # cross-guard
    if shield:
        board = add.make(add.cuboid, [-0.62, 1.35, 0.32], [0.55, 0.75, 0.06], P["red"])
        add.mesh(add.texture(board, TEX["banner"], "fit"))
    M = add.pop()
    add.mesh(add.move(add.rotateY(M, facing), at))


def banner(at, w=1.6, h=2.6, facing=0.0, pole=True):
    """A cloth banner waving from a pole, with the castle's arms on it."""
    def cloth(u, v):
        return [(u - 0.5) * w, -v * h, 0.18 * add.sin(3 * u + 2 * v) * v]
    M = add.make(add.parametric, cloth, 0, 1, k_(10), 0, 1, k_(14), P["red"], double_sided=True)
    M = add.texture(M, TEX["banner"], lambda p, n: (p[0] / w + 0.5, 1 + p[1] / h))
    add.push()
    add.mesh(M)
    add.cylinder([-w / 2 - 0.05, 0, 0], [w / 2 + 0.1, 0, 0], 0.04, 6, P["wood_dark"])
    if pole:
        add.cylinder([-w / 2 - 0.05, -h, 0], [-w / 2 - 0.05, 0.6, 0], 0.05, 6, P["wood_dark"])
        add.sphere([-w / 2 - 0.05, 0.65, 0], 0.09, 6, P["gold"])
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


GATE_Z0, GATE_Z1 = 47.0, 53.0                          # the gate block, along the passage
GATE_TOP = G + 13
SPRING = G + 4.5                                       # the arch springs here; 2.5 more to the apex
for s in (-1, 1):
    square_tower([s * 7, 0, 50], G - 1, G + 20, 7, 6)
    banner([s * 7, G + 17.5, 53.6 + 0.2])
# the passage: jambs, the arch fill (textured), voussoirs on both faces
for s in (-1, 1):
    jamb = add.make(add.cuboid, [s * 3.0, (G - 1 + SPRING) / 2, 50], [1.0, SPRING - G + 1, GATE_Z1 - GATE_Z0], P["stone"])
    add.mesh(textured(jamb, "stone", scale=3.0))
add.mesh(textured(arch_fill(-3.5, 3.5, SPRING, GATE_TOP, GATE_Z0, GATE_Z1, 0, 2.5, P["stone"]), "stone", scale=3.0))
for z, depth in ((GATE_Z1, 0.25), (GATE_Z0, -0.25)):
    voussoirs(0, SPRING, 2.5, z, depth, k_(13), lambda i: shade_of("stone", i % 3), width=0.6)
add.cuboid([0, GATE_TOP + 0.2, 50], [7.0, 0.4, GATE_Z1 - GATE_Z0 + 0.6], P["stone_dark"])
add.push()
merlons(7.0, 0.4, 0, 0.5)
add.mesh(add.move(add.pop(), [-3.5, GATE_TOP, GATE_Z1]))
add.text("ADD 2.0", [0, G + 8.2, GATE_Z1 + 0.15], 0.9, 0.08, P["gold"], align="center", k=6)
# a lamp on each side of the gate
for s in (-1, 1):
    add.cuboid([s * 3.9, G + 4.2, GATE_Z1 + 0.3], [0.3, 0.3, 0.6], P["iron"])
    add.sphere([s * 3.9, G + 4.9, GATE_Z1 + 0.45], 0.28, k_(10), FLAME)
flush("gatehouse")

# the portcullis, lowered to a third, in a slot just inside the outer face
PORT_Z = GATE_Z1 - 0.7
PORT_BOTTOM = G + 2.4
for i in range(8):
    x = -2.1 + i * 0.6
    add.cylinder([x, PORT_BOTTOM + 0.4, PORT_Z], [x, GATE_TOP - 0.2, PORT_Z], 0.07, k_(8), P["iron"])
    add.cone([x, PORT_BOTTOM + 0.4, PORT_Z], [x, PORT_BOTTOM, PORT_Z], 0.07, k_(8), P["iron"])
for y in (PORT_BOTTOM + 0.9, PORT_BOTTOM + 2.3, PORT_BOTTOM + 3.7, PORT_BOTTOM + 5.1):
    add.cuboid([0, y, PORT_Z], [4.5, 0.12, 0.12], P["iron"])
# the wooden gate behind it: two leaves on hinges, one wide open, one ajar
for s, angle in ((-1, 1.3), (1, -0.25)):
    leaf = add.Mesh()                                  # hinge at x = 0, planks towards +x
    for i in range(6):
        leaf.extend(add.make(add.cuboid, [0.2 + i * 0.4, 2.6, 0], [0.38, 5.0, 0.2], pick("wood", i, s + 2)))
    for y in (0.6, 2.6, 4.6):
        leaf.extend(add.make(add.cuboid, [1.2, y, -0.14], [2.4, 0.25, 0.08], P["iron"]))
        for i in range(6):
            leaf.extend(add.make(add.sphere, [0.2 + i * 0.4, y, -0.2], 0.05, 4, P["iron"]))
    if s > 0:
        leaf = add.mirror(leaf, [0, 0, 0], [1, 0, 0])   # the right leaf opens towards -x
    leaf = add.rotateY(leaf, angle)
    add.mesh(add.move(leaf, [s * 2.5, G, GATE_Z0 + 0.6]))
flush("portcullis and gate")

# the drawbridge: planks on two beams, resting on both banks, with its chains
BRIDGE_Z0, BRIDGE_Z1 = GATE_Z1 - 0.3, MOAT[3] + 0.8
for s in (-1, 1):
    add.cuboid([s * 1.9, G + 0.12, (BRIDGE_Z0 + BRIDGE_Z1) / 2], [0.3, 0.25, BRIDGE_Z1 - BRIDGE_Z0], P["wood_dark"])
planks = int(4.6 / 0.42)
for i in range(planks):
    x = -2.3 + 0.21 + i * 0.42
    add.cuboid([x, G + 0.32, (BRIDGE_Z0 + BRIDGE_Z1) / 2], [0.4, 0.15, BRIDGE_Z1 - BRIDGE_Z0], pick("wood", i, 9))
for z in (BRIDGE_Z0 + 0.3, BRIDGE_Z1 - 0.3):               # iron straps at both ends
    add.cuboid([0, G + 0.42, z], [4.7, 0.05, 0.2], P["iron"])
for s in (-1, 1):
    hole = [s * 2.0, G + 10.2, GATE_Z1]
    add.cuboid([hole[0], hole[1], hole[2] - 0.2], [0.6, 0.6, 0.5], P["black"])
    chain([s * 2.0, G + 0.5, BRIDGE_Z1 - 0.4], [hole[0], hole[1], hole[2] + 0.1])
    add.torus([s * 2.0, G + 0.5, BRIDGE_Z1 - 0.4], 0.16, 0.05, k_(10), k_(6), P["iron"], axis=(1, 0, 0))
flush("drawbridge and chains")

# two guards, and a third one asleep on the wall walk later on
armour([-3.2, G, GATE_Z1 + 1.0], add.pi * 0.05)
armour([3.2, G, GATE_Z1 + 1.0], -add.pi * 0.05, weapon="sword")
flush("guards")


# --------------------------------------------------------------------------
#  4. The palace: a great hall with glass windows, corner towers with copper
#     spires, a chapel with stained glass, a tiled roof, balconies, a porch
# --------------------------------------------------------------------------
KX0, KX1, KZ0, KZ1 = -22.0, 22.0, -30.0, -2.0            # the footprint of the main block
KY = G + 0.8                                            # the hall floor (on a plinth)
HALL_H = 9.0                                            # floor to ceiling
FLOOR2 = KY + HALL_H + 0.6                              # the upper floor
EAVE = FLOOR2 + 5.0
WT = 1.2                                                # wall thickness


def opening(x, y0, y1, w, arched=True, glass=True, sill=True):
    return {"x": x, "y0": y0, "y1": y1, "w": w, "arched": arched, "glass": glass, "sill": sill}


def pierced_wall(length, height, openings, thickness=WT, name="stone"):
    """A wall along +X (0..length, 0..height, centred on z = 0) with arched
    or square openings cut through it, glazed and framed.  Returned as a mesh."""
    slab = add.make(add.cuboid, [length / 2, height / 2, 0], [length, height, thickness], P["stone"])
    holes = []
    for o in openings:
        r = o["w"] / 2
        top = o["y1"] - (r if o["arched"] else 0)
        holes.append(add.make(add.cuboid, [o["x"], (o["y0"] + top) / 2, 0], [o["w"], top - o["y0"], thickness + 2]))
        if o["arched"]:
            holes.append(add.make(add.cylinder, [o["x"], top, -thickness], [o["x"], top, thickness], r, k_(14)))
    wall = add.difference(slab, *holes) if holes else slab
    wall = textured(wall, name, scale=3.0)
    add.push()
    add.mesh(wall)
    for o in openings:
        r = o["w"] / 2
        top = o["y1"] - (r if o["arched"] else 0)
        x0, x1 = o["x"] - r, o["x"] + r
        if o["glass"]:
            add.cuboid([o["x"], (o["y0"] + o["y1"]) / 2, 0], [o["w"], o["y1"] - o["y0"], 0.08], GLASS)
            add.cuboid([o["x"], (o["y0"] + top) / 2, 0], [0.1, top - o["y0"], 0.14], P["glass_frame"])       # mullion
            add.cuboid([o["x"], o["y0"] + (top - o["y0"]) * 0.62, 0], [o["w"], 0.1, 0.14], P["glass_frame"])   # transom
        for x in (x0 + 0.06, x1 - 0.06):                                                                   # jamb bars
            add.cuboid([x, (o["y0"] + top) / 2, 0], [0.12, top - o["y0"], thickness * 0.6], P["glass_frame"])
        if o["arched"]:
            add.arch([x0 + 0.06, top, 0], [x1 - 0.06, top, 0], r - 0.06, 0.06, P["glass_frame"], k_(12), 6)
            for z in (thickness / 2, -thickness / 2):                                                  # arch stones
                voussoirs(o["x"], top, r, z, 0.12 if z > 0 else -0.12, k_(9),
                          lambda i: shade_of("stone", i % 3), width=0.45)
        else:
            add.cuboid([o["x"], top + 0.15, 0], [o["w"] + 0.5, 0.3, thickness + 0.2], P["stone_dark"])     # lintel
        if o["sill"]:
            add.cuboid([o["x"], o["y0"] - 0.1, thickness / 2 + 0.1], [o["w"] + 0.5, 0.2, 0.5], P["stone_dark"])
    return add.pop()


def stand_wall(M, a, b, y):
    L, d, n = outward([a[0], 0, a[1]], [b[0], 0, b[1]], centre=((KX0 + KX1) / 2, (KZ0 + KZ1) / 2))
    add.mesh(frame_to(M, [a[0], y, a[1]], d, n))


# the plinth the palace stands on, with four steps up to the door
add.mesh(textured(add.make(add.cuboid, [0, (G + KY) / 2, (KZ0 + KZ1) / 2],
                           [KX1 - KX0 + 1.6, KY - G, KZ1 - KZ0 + 1.6], P["stone_dark"]), "stone", scale=3.0))
add.stairs([0, G, KZ1 + 0.8 + 2.4], 4, 7.0, (KY - G) / 4, 0.6, P["stone_dark"], direction=(0, 0, -1))

# the four walls of the ground and upper floors
south = [opening(22, 0, 5.2, 4.0, glass=False, sill=False)]          # the door, in the middle
for x in (6, 11, 15.5):
    for s in (-1, 1):
        south.append(opening(22 + s * x, 1.6, 7.4, 2.2))
        south.append(opening(22 + s * x, HALL_H + 1.5, HALL_H + 4.0, 1.6))
south.append(opening(22, HALL_H + 1.5, HALL_H + 4.0, 1.6))
north = [o for o in south if o["glass"]]
side = [opening(z, 1.6, 7.4, 2.2) for z in (7, 14, 21)]
side += [opening(z, HALL_H + 1.5, HALL_H + 4.0, 1.6) for z in (5.5, 10.5, 17.5, 22.5)]
east = [opening(3, HALL_H + 1.5, HALL_H + 4.0, 1.6), opening(25, HALL_H + 1.5, HALL_H + 4.0, 1.6)]
stand_wall(pierced_wall(KX1 - KX0, EAVE - KY, south), (KX0, KZ1), (KX1, KZ1), KY)
flush("palace: south wall")
stand_wall(pierced_wall(KX1 - KX0, EAVE - KY, north), (KX1, KZ0), (KX0, KZ0), KY)
flush("palace: north wall")
stand_wall(pierced_wall(KZ1 - KZ0, EAVE - KY, side), (KX0, KZ1), (KX0, KZ0), KY)
flush("palace: west wall")
stand_wall(pierced_wall(KZ1 - KZ0, EAVE - KY, east), (KX1, KZ0), (KX1, KZ1), KY)
flush("palace: east wall")

# the floor between the storeys and the hall floor
add.mesh(textured(add.make(add.cuboid, [0, KY + HALL_H + 0.3, (KZ0 + KZ1) / 2],
                           [KX1 - KX0 - 0.4, 0.6, KZ1 - KZ0 - 0.4], P["wood"]), "planks", "xz", scale=2))
for i in range(int((KZ1 - KZ0) / 3)):                    # the ceiling beams of the hall
    z = KZ0 + WT + 1.5 + i * 3
    add.cuboid([0, KY + HALL_H - 0.3, z], [KX1 - KX0 - 0.6, 0.6, 0.6], P["wood_dark"])
add.cuboid([0, KY - 0.1, (KZ0 + KZ1) / 2], [KX1 - KX0 - 0.4, 0.2, KZ1 - KZ0 - 0.4], P["black"])
for i in range(int((KX1 - KX0 - 0.4) / 2)):                # a chessboard floor of 2-unit marble squares
    for j in range(int((KZ1 - KZ0 - 0.4) / 2)):
        x, z = KX0 + 0.2 + i * 2, KZ0 + 0.2 + j * 2
        add.polygon([[x, KY + 0.01, z], [x, KY + 0.01, z + 2], [x + 2, KY + 0.01, z + 2], [x + 2, KY + 0.01, z]],
                    P["white"] if (i + j) % 2 else P["wood_dark"])
flush("palace: floors")

# the roof: a hip roof of individual tiles in the zigzag colours of Bojnice,
# over a plain textured roof that closes it from below; three dormers a side
TILE = {1: (0.6, 0.5), 2: (0.4, 0.35), 3: (0.25, 0.22)}[DETAIL]
ROOF_H = 8.0
RIDGE_Y = EAVE + ROOF_H
OVER = 0.7
TILE_COLORS = [[40, 120, 70], [200, 150, 40], [150, 40, 40], [40, 80, 140]]
for i, c in enumerate(TILE_COLORS):
    P["tile%d" % i] = c


def tile_face(A, B, C, D):
    """Cover the planar face A-B (eave) .. D-C (ridge) with rows of tiles."""
    tw, th = TILE
    n = vunit(vcross(vsub(B, A), vsub(D, A)))
    lift = [0.06 * n[k] for k in range(3)]
    rows = max(1, int(vlen(vsub(D, A)) / th))
    for j in range(rows):
        t0, t1 = j / float(rows), (j + 1) / float(rows)
        L0 = [A[k] + (D[k] - A[k]) * t0 for k in range(3)]
        R0 = [B[k] + (C[k] - B[k]) * t0 for k in range(3)]
        L1 = [A[k] + (D[k] - A[k]) * t1 for k in range(3)]
        R1 = [B[k] + (C[k] - B[k]) * t1 for k in range(3)]
        width = vlen(vsub(R0, L0))
        cols = max(1, int(width / tw))
        for i in range(cols):
            u0, u1 = i / float(cols), (i + 1) / float(cols)
            q = [[L0[k] + (R0[k] - L0[k]) * u0 + lift[k] for k in range(3)],
                 [L0[k] + (R0[k] - L0[k]) * u1 + lift[k] for k in range(3)],
                 [L1[k] + (R1[k] - L1[k]) * u1 + lift[k] for k in range(3)],
                 [L1[k] + (R1[k] - L1[k]) * u0 + lift[k] for k in range(3)]]
            band = ((i + j) // 3) % 2 + 2 * (((i - j) // 3) % 2)     # diamonds
            add.polygon(q, P["tile%d" % band])


def hip_roof(x0, x1, z0, z1, y, h, inset=8.0, over=OVER, dormers=()):
    ex0, ex1, ez0, ez1 = x0 - over, x1 + over, z0 - over, z1 + over
    zc = (z0 + z1) / 2
    r0, r1 = [x0 + inset, y + h, zc], [x1 - inset, y + h, zc]
    south = ([ex0, y, ez1], [ex1, y, ez1], r1, r0)
    north = ([ex1, y, ez0], [ex0, y, ez0], r0, r1)
    east = ([ex1, y, ez1], [ex1, y, ez0], r1, r1)
    west = ([ex0, y, ez0], [ex0, y, ez1], r0, r0)
    base = add.Mesh()
    for face in (south, north, east, west):
        base.add_polygon([face[0], face[1], face[2]] + ([face[3]] if face[3] is not face[2] else []), P["tile2"])
    base.add_polygon([[ex0, y, ez0], [ex1, y, ez0], [ex1, y, ez1], [ex0, y, ez1]][::-1], P["wood_dark"])
    add.mesh(base)
    for face in (south, north, east, west):
        tile_face(*face)
    add.cuboid([(x0 + x1) / 2, y + h, zc], [x1 - x0 - 2 * inset + 0.4, 0.3, 0.5], P["copper"])   # ridge cap
    for x in dormers:                                                          # dormers, both sides
        for s in (1, -1):
            zf = (ez1 - 2.4) if s > 0 else (ez0 + 2.4)
            yf = y + h * 2.4 / (ez1 - zc)
            add.mesh(textured(add.make(add.cuboid, [x, yf + 1.1, zf - s * 1.3], [2.4, 2.8, 2.6], P["stone"]), "stone", scale=3))
            top = add.make(add.roof, [x, yf + 2.5, zf - s * 1.3], [2.8, 2.9], 1.4, P["slate"], 0.15)
            add.mesh(add.texture(top, TEX["slate"], "box", scale=0.4))
            add.cuboid([x, yf + 1.2, zf + s * 0.02], [1.2, 1.5, 0.08], GLASS)
            add.cuboid([x, yf + 1.2, zf + s * 0.05], [0.08, 1.5, 0.1], P["glass_frame"])
            add.cuboid([x, yf + 1.2, zf + s * 0.05], [1.2, 0.08, 0.1], P["glass_frame"])
            for dx in (-0.62, 0.62):
                add.cuboid([x + dx, yf + 1.2, zf + s * 0.05], [0.1, 1.6, 0.1], P["glass_frame"])


hip_roof(KX0, KX1, KZ0, KZ1, EAVE, ROOF_H, dormers=(-12, 0, 12))
for x in (-16, 16):                                                            # chimneys
    add.mesh(textured(add.make(add.cuboid, [x, RIDGE_Y - 1.5, (KZ0 + KZ1) / 2], [1.4, 5.0, 1.4], P["brick"]), "brick", scale=1.5))
    add.cuboid([x, RIDGE_Y + 1.1, (KZ0 + KZ1) / 2], [1.8, 0.3, 1.8], P["stone_dark"])
    for i in range((3, 6, 10)[DETAIL - 1]):                                    # smoke
        add.sphere([x + 0.3 * add.sin(i), RIDGE_Y + 1.8 + i * 0.8, (KZ0 + KZ1) / 2 + 0.3 * add.cos(i * 1.3)],
                   0.35 + 0.1 * i, k_(8), SMOKE)
flush("palace: roof")

# corner towers with copper spires; the big tower (donjon) in the north-west
for cx, cz in ((KX1, KZ1), (KX1, KZ0), (KX0, KZ1)):
    round_tower([cx, 0, cz], G - 1, EAVE + 4, 4.5, k_(24), roof_h=9, spire_color=P["copper"], slits=False)
    for j, y in enumerate((KY + 3, KY + 12, KY + 17)):                         # small windows
        for i in range(3):
            a = add.pi / 4 + i * add.pi / 2 + (add.pi / 8 if j % 2 else 0)
            win = add.make(add.cuboid, [0, 0, 0], [0.7, 1.4, 0.3], P["black"])
            win.extend(add.make(add.cuboid, [0, 0, 0.02], [0.5, 1.2, 0.3], GLASS))
            add.mesh(add.move(add.rotateY(win, -a), [cx + 4.5 * add.cos(a), y, cz + 4.5 * add.sin(a)]))
flush("palace: corner towers")

DON = (KX0 - 3.0, KZ0 - 3.0)                                                   # the donjon
DON_R = 6.5
DON_TOP = EAVE + 12
door = add.make(add.cuboid, [DON[0] - DON_R, G + 1.6, DON[1]], [4, 3.4, 3.0])
door.extend(add.make(add.cylinder, [DON[0] - DON_R - 2, G + 3.3, DON[1]], [DON[0] - DON_R + 2, G + 3.3, DON[1]], 1.5, k_(14)))
lower = add.make(add.pipe, [DON[0], G - 1, DON[1]], [DON[0], G + 7.5, DON[1]], DON_R, DON_R - 1.0, k_(28))
lower = add.difference(lower, door)
add.mesh(tex_round(lower, "stone", DON[0], DON[1], DON_R, 3.0))
add.mesh(textured(add.make(add.cylinder, [DON[0], G - 0.5, DON[1]], [DON[0], G + 0.1, DON[1]], DON_R - 0.9, k_(28),
                           P["stone_dark"]), "cobble", "xz", scale=2))                                   # treasury floor
add.mesh(tex_round(add.make(add.cylinder, [DON[0], G + 7.5, DON[1]], [DON[0], DON_TOP, DON[1]], DON_R, k_(28)),
                   "stone", DON[0], DON[1], DON_R, 3.0))
# the corbels, walk and spire of the donjon, reusing the tower builder without a drum
add.push()
round_tower([DON[0], 0, DON[1]], DON_TOP - 0.1, DON_TOP, DON_R, k_(28), roof_h=12, spire_color=P["copper"], slits=False)
add.mesh(add.pop())
add.cylinder([DON[0], DON_TOP + 12.5, DON[1]], [DON[0], DON_TOP + 17, DON[1]], 0.06, 6, P["iron"])   # flagpole
banner([DON[0] + 0.05, DON_TOP + 16.8, DON[1]], 1.4, 1.0, add.pi / 2, pole=False)
for j, y in enumerate((KY + 9, KY + 15, KY + 21)):
    for i in range(4):
        a = i * add.pi / 2 + (add.pi / 4 if j % 2 else 0)
        win = add.make(add.cuboid, [0, 0, 0], [0.7, 1.4, 0.3], P["black"])
        win.extend(add.make(add.cuboid, [0, 0, 0.02], [0.5, 1.2, 0.3], GLASS))
        add.mesh(add.move(add.rotateY(win, -a), [DON[0] + DON_R * add.cos(a), y, DON[1] + DON_R * add.sin(a)]))
flush("palace: donjon")

# the chapel wing on the east side: stained glass, buttresses, a spire
CH_X0, CH_X1, CH_Z0, CH_Z1 = KX1, 34.0, KZ0 + 7, KZ1 - 7
CH_TOP = KY + 9.0
chapel_east = [opening(z, 1.2, 7.6, 1.7) for z in (2.5, 7, 11.5)]
chapel_end = [opening(6, 1.0, 8.0, 3.2)]
add.push()
stand_wall(pierced_wall(CH_Z1 - CH_Z0, CH_TOP - KY, chapel_east), (CH_X1, CH_Z0), (CH_X1, CH_Z1), KY)
stand_wall(pierced_wall(CH_X1 - CH_X0, CH_TOP - KY, chapel_end), (CH_X0, CH_Z1), (CH_X1, CH_Z1), KY)
stand_wall(pierced_wall(CH_X1 - CH_X0, CH_TOP - KY, chapel_end), (CH_X1, CH_Z0), (CH_X0, CH_Z0), KY)
chapel = add.pop()
# the plain glass of the chapel becomes stained glass
for i, c in enumerate(chapel.C):
    if c == GLASS:
        chapel.C[i] = add.rgb((255, 255, 255, 0.55, TEX["glass"]))
        f = chapel.F[i]
        lo = min(chapel.V[k][1] for k in f)
        if chapel.UV is None:
            chapel.UV = [None] * len(chapel.F)
        chapel.UV[i] = [((chapel.V[k][0] + chapel.V[k][2]) / 3.0, (chapel.V[k][1] - lo) / 3.0) for k in f]
add.mesh(chapel)
add.mesh(textured(add.make(add.cuboid, [(CH_X0 + CH_X1) / 2, KY - 0.1, (CH_Z0 + CH_Z1) / 2],
                           [CH_X1 - CH_X0 + 1.2, 0.2, CH_Z1 - CH_Z0 + 1.2], P["stone_dark"]), "marble", "xz", scale=2))
add.mesh(textured(add.make(add.cuboid, [(CH_X0 + CH_X1) / 2, (G + KY) / 2, (CH_Z0 + CH_Z1) / 2],
                           [CH_X1 - CH_X0 + 1.6, KY - G, CH_Z1 - CH_Z0 + 1.6], P["stone_dark"]), "stone", scale=3))
for z in (CH_Z0 + 3.5, (CH_Z0 + CH_Z1) / 2, CH_Z1 - 3.5):                     # buttresses on the east wall
    add.cuboid([CH_X1 + 0.5, (KY + KY + 5) / 2, z], [1.0, 5.0, 1.0], P["stone_dark"])
    add.cuboid([CH_X1 + 0.3, KY + 6.0, z], [0.6, 2.0, 0.8], P["stone_dark"])
for x in (CH_X0 + 3.5, CH_X1 - 3.5):
    for z, s in ((CH_Z1 + 0.5, 1), (CH_Z0 - 0.5, -1)):
        add.cuboid([x, KY + 2.5, z], [1.0, 5.0, 1.0], P["stone_dark"])
        add.cuboid([x, KY + 6.0, z - s * 0.2], [0.8, 2.0, 0.6], P["stone_dark"])
chapel_roof = add.make(add.roof, [(CH_X0 + CH_X1) / 2, CH_TOP, (CH_Z0 + CH_Z1) / 2],
                       [CH_Z1 - CH_Z0, CH_X1 - CH_X0 + 1.0], 7.0, P["slate"], 0.5)
chapel_roof = add.rotateY(chapel_roof, add.pi / 2, [(CH_X0 + CH_X1) / 2, 0, (CH_Z0 + CH_Z1) / 2])
add.mesh(add.texture(chapel_roof, TEX["slate"], "box", scale=0.5))
add.cuboid([CH_X1 + 0.3, CH_TOP - 0.3, (CH_Z0 + CH_Z1) / 2], [0.6, 0.6, CH_Z1 - CH_Z0 + 1.0], P["stone_dark"])  # cornice
SPIRE = [(CH_X0 + CH_X1) / 2, 0, (CH_Z0 + CH_Z1) / 2]
add.cylinder([SPIRE[0], CH_TOP + 5.5, SPIRE[2]], [SPIRE[0], CH_TOP + 8.5, SPIRE[2]], 1.0, 8, P["stone"])
add.cone([SPIRE[0], CH_TOP + 8.5, SPIRE[2]], [SPIRE[0], CH_TOP + 17.5, SPIRE[2]], 1.3, 8, P["copper"])
add.sphere([SPIRE[0], CH_TOP + 17.8, SPIRE[2]], 0.3, k_(8), P["gold"])
add.cuboid([SPIRE[0], CH_TOP + 18.9, SPIRE[2]], [0.1, 1.6, 0.1], P["gold"])                      # the cross
add.cuboid([SPIRE[0], CH_TOP + 19.2, SPIRE[2]], [0.8, 0.1, 0.1], P["gold"])
flush("chapel")

# the porch and the balconies of the south front
for s in (-1, 1):
    add.column([s * 2.8, KY, KZ1 + 3.2], 5.0, 0.35, P["stone"], k_(14))
add.mesh(textured(add.make(add.cuboid, [0, KY + 5.3, KZ1 + 1.9], [7.6, 0.5, 4.0], P["stone"]), "stone", scale=3))
for x in (-11, 0, 11):                                                          # balconies
    add.cuboid([x, KY + HALL_H + 0.45, KZ1 + 1.3], [4.4, 0.3, 1.8], P["stone_dark"])
    for dx in (-1.9, 1.9):
        add.cuboid([x + dx, KY + HALL_H - 0.1, KZ1 + 0.9], [0.4, 0.8, 0.8], P["stone_dark"])
    rail = KY + HALL_H + 0.6
    for i in range(9):
        bx = x - 2.0 + i * 0.5
        add.cylinder([bx, rail, KZ1 + 2.1], [bx, rail + 0.9, KZ1 + 2.1], 0.07, 6, P["stone"])
    for dz in range(4):
        for dx in (-2.1, 2.1):
            add.cylinder([x + dx, rail, KZ1 + 0.7 + dz * 0.45], [x + dx, rail + 0.9, KZ1 + 0.7 + dz * 0.45], 0.07, 6, P["stone"])
    add.cuboid([x, rail + 0.95, KZ1 + 1.4], [4.5, 0.12, 0.2], P["stone"])
    add.cuboid([x, rail + 0.95, KZ1 + 2.1], [4.5, 0.12, 0.2], P["stone"])
    for dx in (-2.15, 2.15):
        add.cuboid([x + dx, rail + 0.95, KZ1 + 1.4], [0.2, 0.12, 1.5], P["stone"])
# the double door of the hall, both leaves open into the hall
for s, angle in ((-1, 1.9), (1, -1.9)):
    leaf = add.Mesh()
    for i in range(5):
        leaf.extend(add.make(add.cuboid, [0.2 + i * 0.4, 2.5, 0], [0.38, 4.9, 0.16], pick("wood_dark", i, 5)))
    for y in (0.7, 2.5, 4.3):
        leaf.extend(add.make(add.cuboid, [1.0, y, 0.11], [2.0, 0.2, 0.06], P["iron"]))
    leaf.extend(add.make(add.torus, [1.5, 2.4, 0.2], 0.18, 0.04, 12, 6, P["gold"], axis=(0, 0, 1)))
    if s > 0:
        leaf = add.mirror(leaf, [0, 0, 0], [1, 0, 0])
    add.mesh(add.move(add.rotateY(leaf, angle), [s * 1.95, KY, KZ1 - 0.4]))
flush("porch, balconies and doors")


# --------------------------------------------------------------------------
#  5. Props: furniture, food, vessels, weapons -- everything is built at
#     the origin and then moved into place
# --------------------------------------------------------------------------
def lathe(points, at, k, color, scale=1.0):
    """A turned object (goblet, jug, bowl, candlestick): ``points`` are
    ``[radius, height]`` pairs of the profile, bottom first."""
    n = len(points) - 1
    pts = [[r * scale, h * scale] for r, h in points]
    add.revolve(lambda t: pts[min(n, int(round(t)))], at, [at[0], at[1] + 1, at[2]], 0, n, n, k, color)


def goblet(at, color=None):
    lathe([[0.0, 0], [0.13, 0], [0.13, 0.02], [0.04, 0.05], [0.04, 0.2], [0.07, 0.24], [0.15, 0.3],
           [0.16, 0.45], [0.12, 0.45], [0.11, 0.3], [0.0, 0.28]], at, k_(10), color or P["gold"])


def jug(at, color=None):
    color = color or P["brick"]
    lathe([[0.0, 0], [0.16, 0], [0.24, 0.15], [0.26, 0.35], [0.18, 0.5], [0.15, 0.6], [0.17, 0.66],
           [0.12, 0.66], [0.11, 0.55], [0.0, 0.5]], at, k_(10), color)
    add.torus([at[0] + 0.24, at[1] + 0.4, at[2]], 0.13, 0.03, k_(10), 6, color, axis=(0, 0, 1))


def bowl(at, r=0.35, color=None, fruit=None):
    color = color or P["wood_light"]
    lathe([[0.0, 0], [r * 0.5, 0], [r * 0.9, r * 0.35], [r, r * 0.5], [r * 0.9, r * 0.5], [r * 0.8, r * 0.35],
           [r * 0.4, r * 0.12], [0.0, r * 0.12]], at, k_(12), color)
    if fruit:
        for i in range(7):
            a = 2 * add.pi * i / 6
            rr = r * 0.5 if i < 6 else 0
            add.sphere([at[0] + rr * add.cos(a), at[1] + r * 0.35 + (0.05 if i == 6 else 0), at[2] + rr * add.sin(a)],
                       r * 0.3, k_(8), fruit[i % len(fruit)])


def candle(at, h=0.35, r=0.04):
    add.cylinder(at, [at[0], at[1] + h, at[2]], r, k_(8), P["white"])
    add.cylinder([at[0], at[1] + h, at[2]], [at[0], at[1] + h + 0.05, at[2]], 0.008, 4, P["black"])
    add.sphere([at[0], at[1] + h + 0.12, at[2]], 0.07, k_(8), FLAME)
    add.sphere([at[0], at[1] + h + 0.1, at[2]], 0.03, 4, P["flame_core"])


def candelabra(at, arms=3, h=0.6):
    lathe([[0.0, 0], [0.18, 0], [0.18, 0.03], [0.05, 0.06], [0.05, h - 0.1], [0.08, h], [0.0, h]], at, k_(8), P["gold"])
    for i in range(arms):
        a = 2 * add.pi * i / arms
        tip = [at[0] + 0.3 * add.cos(a), at[1] + h + 0.05, at[2] + 0.3 * add.sin(a)]
        add.polyline([[at[0], at[1] + h - 0.25, at[2]], [at[0] + 0.2 * add.cos(a), at[1] + h - 0.2, at[2] + 0.2 * add.sin(a)], tip],
                     0.025, 6, P["gold"], smooth=1)
        candle(tip, 0.3, 0.035)


def plate(at, r=0.3):
    add.cylinder(at, [at[0], at[1] + 0.03, at[2]], r, k_(12), P["steel"])


def chicken_roast(at):
    plate(at, 0.4)
    add.mesh(add.move(add.stretch(add.make(add.sphere, [0, 0, 0], 0.3, k_(10), P["meat"]), [1.0, 0.7, 0.8]), [at[0], at[1] + 0.22, at[2]]))
    for s in (-1, 1):
        add.capsule([at[0] + s * 0.15, at[1] + 0.12, at[2] + 0.1], [at[0] + s * 0.32, at[1] + 0.3, at[2] + 0.28], 0.06, k_(8), P["meat"])
        add.sphere([at[0] + s * 0.34, at[1] + 0.32, at[2] + 0.3], 0.05, 4, P["bone"])


def bread(at, n=1):
    for i in range(n):
        loaf = add.stretch(add.make(add.sphere, [0, 0, 0], 0.22, k_(10), P["bread"]), [1.5, 0.7, 1.0])
        add.mesh(add.move(add.rotateY(loaf, i * 0.7), [at[0] + 0.25 * i, at[1] + 0.15, at[2] + 0.1 * i]))


def cheese(at):
    add.mesh(add.move(add.make(add.revolve, lambda t: [0.32, 0.22 * t], [0, 0, 0], [0, 1, 0], 0, 1, 1, k_(12),
                               P["cheese"], 2 * add.pi * 0.8), at))
    add.mesh(add.move(add.make(add.prism, [[0, 0], [0.3, -0.1], [0.3, 0.1]], 0.2, P["cheese"], (0, 0, 0)),
                      [at[0] + 0.55, at[1] + 0.1, at[2] + 0.3]))


def grapes(at, n=12):
    for i in range(n):
        a = 2.4 * i
        rr = 0.12 * (1 - i / float(n)) + 0.02
        add.sphere([at[0] + rr * add.cos(a), at[1] + 0.25 - 0.018 * i, at[2] + rr * add.sin(a)], 0.045, k_(6), P["grape"])
    add.cylinder([at[0], at[1] + 0.25, at[2]], [at[0] + 0.1, at[1] + 0.35, at[2]], 0.01, 4, P["leaf_dark"])


def fruit(at, color, r=0.12):
    add.sphere([at[0], at[1] + r, at[2]], r, k_(10), color)
    add.cylinder([at[0], at[1] + 2 * r - 0.02, at[2]], [at[0] + 0.02, at[1] + 2 * r + 0.06, at[2]], 0.01, 4, P["trunk"])


def roast_pig(at):
    """The centrepiece of the feast: a whole roast pig with an apple in its mouth."""
    plate(at, 1.0)
    add.push()
    add.mesh(add.stretch(add.make(add.sphere, [0, 0.42, 0], 0.42, k_(16), P["pig"]), [1.0, 0.85, 2.0]))
    add.sphere([0, 0.5, -0.95], 0.3, k_(12), P["pig"])
    add.cylinder([0, 0.45, -1.15], [0, 0.45, -1.35], 0.1, k_(8), P["pig"])
    add.cylinder([0, 0.45, -1.35], [0, 0.45, -1.37], 0.1, k_(8), P["cushion"])
    add.sphere([0, 0.42, -1.5], 0.11, k_(8), P["apple"])
    for s in (-1, 1):
        add.mesh(add.rotateX(add.make(add.prism, [[0, 0], [0.16, 0], [0.08, 0.28]], 0.04, P["pig"], (s * 0.2, 0.75, -0.9), (0, 0, 1)), 0.4, (0, 0.75, -0.9)))
        add.capsule([s * 0.35, 0.3, -0.6], [s * 0.5, 0.08, -0.85], 0.09, k_(8), P["pig"])
        add.capsule([s * 0.35, 0.3, 0.6], [s * 0.5, 0.08, 0.85], 0.09, k_(8), P["pig"])
    add.helix([0, 0.6, 0.85], 0.06, 0.05, 2.5, 30, 0.015, 4, P["pig"], axis=(0, 0, 1))
    for i in range(6):                                        # roasting herbs
        add.polyline([[0.1 * add.sin(i), 0.85, -0.5 + i * 0.2], [0.15 * add.cos(i), 0.95, -0.4 + i * 0.2]], 0.01, 4, P["leaf"])
    add.mesh(add.move(add.pop(), [at[0], at[1] + 0.03, at[2]]))


def barrel(at, r=0.45, h=1.2, k=None, upright=True, color=None):
    """A barrel of separate staves with three iron hoops."""
    k = k or k_(14)
    color = color or P["wood"]
    add.push()
    for i in range(k):
        a0, a1 = 2 * add.pi * i / k, 2 * add.pi * (i + 0.93) / k
        stave = []
        for t in (0.0, 0.5, 1.0):
            rr = r * (0.9 + 0.1 * add.sin(add.pi * t)) if t != 0.5 else r
            stave.append([rr, h * t])
        prof = stave
        piece = add.make(add.revolve, lambda t: prof[min(2, int(round(t)))], [0, 0, 0], [0, 1, 0], 0, 2, 2, 1,
                         pick("wood", i, 3), angle=a1 - a0, caps=False)
        add.mesh(add.rotateY(piece, -a0))
    for t in (0.12, 0.5, 0.88):
        rr = r * (0.9 + 0.1 * add.sin(add.pi * t))
        add.torus([0, h * t, 0], rr, 0.035, k, 6, P["iron"])
    add.disc([0, h - 0.03, 0], [0, 1, 0], r * 0.88, k, P["wood_dark"])
    add.disc([0, 0.03, 0], [0, -1, 0], r * 0.88, k, P["wood_dark"])
    M = add.pop()
    if not upright:
        M = add.rotateX(M, add.pi / 2)
        M = add.move(M, [0, r, h / 2])
    add.mesh(add.move(M, at))


def crate(at, s=0.9, color=None):
    """A wooden crate: planks with corner posts and an iron strap."""
    color = color or P["wood_light"]
    add.push()
    for i in range(4):
        add.cuboid([0, s * (i + 0.5) / 4, s / 2], [s, s / 4 - 0.02, 0.06], pick("wood_light", i, 1))
        add.cuboid([0, s * (i + 0.5) / 4, -s / 2], [s, s / 4 - 0.02, 0.06], pick("wood_light", i, 2))
        add.cuboid([s / 2, s * (i + 0.5) / 4, 0], [0.06, s / 4 - 0.02, s], pick("wood_light", i, 3))
        add.cuboid([-s / 2, s * (i + 0.5) / 4, 0], [0.06, s / 4 - 0.02, s], pick("wood_light", i, 4))
    add.cuboid([0, s - 0.03, 0], [s, 0.06, s], P["wood"])
    for sx in (-1, 1):
        for sz in (-1, 1):
            add.cuboid([sx * s / 2, s / 2, sz * s / 2], [0.1, s, 0.1], P["wood_dark"])
    add.cuboid([0, s / 2, 0], [s + 0.04, 0.12, s + 0.04], P["iron"])
    add.mesh(add.move(add.pop(), at))


def sack(at, r=0.4):
    add.mesh(add.move(add.stretch(add.make(add.sphere, [0, 0, 0], r, k_(10), P["sand"]), [1.0, 0.8, 1.0]), [at[0], at[1] + r * 0.7, at[2]]))
    add.cylinder([at[0], at[1] + r * 1.4, at[2]], [at[0] + 0.05, at[1] + r * 1.7, at[2]], r * 0.3, k_(8), P["sand"])
    add.torus([at[0], at[1] + r * 1.5, at[2]], r * 0.3, 0.015, k_(8), 4, P["rope"])


def sword(at, up=(0, 1, 0), length=1.1, color=None):
    """A sword whose point is at ``at`` and whose blade runs along ``up``."""
    color = color or P["steel"]
    u = vunit(up)
    tip = at
    hilt = [at[k] + u[k] * length for k in range(3)]
    grip = [at[k] + u[k] * (length + 0.3) for k in range(3)]
    add.beam(tip, hilt, 0.12, 0.02, color)
    add.cone(hilt, tip, 0.001, 4, color)
    helper = [0, 0, 1] if abs(u[2]) < 0.9 else [1, 0, 0]
    side = vunit(vcross(u, helper))
    add.beam([hilt[k] - side[k] * 0.2 for k in range(3)], [hilt[k] + side[k] * 0.2 for k in range(3)], 0.05, 0.05, P["gold"])
    add.cylinder(hilt, grip, 0.035, 6, P["wood_dark"])
    add.sphere(grip, 0.06, 6, P["gold"])


def spear(at, length=3.0):
    add.cylinder(at, [at[0], at[1] + length, at[2]], 0.035, 6, P["wood"])
    add.cone([at[0], at[1] + length, at[2]], [at[0], at[1] + length + 0.45, at[2]], 0.07, 6, P["steel"])


def axe(at, length=1.2):
    add.cylinder(at, [at[0], at[1] + length, at[2]], 0.035, 6, P["wood"])
    add.mesh(add.move(add.make(add.prism, [[0, -0.25], [0.35, -0.3], [0.4, 0.3], [0, 0.2]], 0.04, P["steel"], (0, 0, 0), (0, 0, 1)),
                      [at[0], at[1] + length - 0.35, at[2]]))


def shield(at, facing=0.0, r=0.5):
    """A round shield with the castle's arms, standing on edge."""
    M = add.make(add.cylinder, [0, r, -0.03], [0, r, 0.03], r, k_(16), P["red"])
    M = add.texture(M, TEX["banner"], "fit")
    M.extend(add.make(add.sphere, [0, r, 0.06], 0.1, k_(8), P["iron"]))
    add.mesh(add.move(add.rotateY(M, facing), at))


def torch(at, facing=0.0):
    """A wall torch: an iron bracket, a wooden shaft and a flame."""
    add.push()
    add.cuboid([0, 0, 0.1], [0.1, 0.5, 0.2], P["iron"])
    add.cylinder([0, -0.2, 0.3], [0, 0.6, 0.35], 0.05, 6, P["wood_dark"])
    add.cylinder([0, 0.55, 0.35], [0, 0.75, 0.35], 0.09, 6, P["rope"])
    add.sphere([0, 0.9, 0.35], 0.16, k_(8), FLAME)
    add.sphere([0, 0.85, 0.35], 0.08, k_(6), P["flame_core"])
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def chandelier(at, r=1.1, hang=2.0):
    """A ring of candles hanging on chains from the ceiling."""
    add.torus(at, r, 0.05, k_(20), 6, P["iron"])
    for i in range(8):
        a = 2 * add.pi * i / 8
        p = [at[0] + r * add.cos(a), at[1] + 0.05, at[2] + r * add.sin(a)]
        add.cylinder([p[0], p[1], p[2]], [p[0], p[1] + 0.08, p[2]], 0.07, 6, P["iron"])
        candle([p[0], p[1] + 0.08, p[2]], 0.3, 0.035)
    top = [at[0], at[1] + hang, at[2]]
    for i in range(3):
        a = 2 * add.pi * i / 3
        chain([at[0] + r * add.cos(a), at[1], at[2] + r * add.sin(a)], top, 0.07, 0.015)
    add.cylinder(top, [top[0], top[1] + 0.3, top[2]], 0.12, 6, P["iron"])


def chair(at, facing=0.0, color=None):
    color = color or P["wood"]
    add.push()
    add.cuboid([0, 0.45, 0], [0.5, 0.06, 0.5], color)
    for sx in (-0.2, 0.2):
        for sz in (-0.2, 0.2):
            add.cuboid([sx, 0.22, sz], [0.05, 0.45, 0.05], color)
        add.cuboid([sx, 0.75, -0.22], [0.05, 0.6, 0.05], color)
    add.cuboid([0, 0.85, -0.22], [0.5, 0.25, 0.04], color)
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def chess_set(at):
    """A game in progress on a small table."""
    add.cuboid([at[0], at[1] + 0.7, at[2]], [1.2, 0.06, 1.2], P["wood_dark"])
    for i in range(8):
        for j in range(8):
            x, z = at[0] - 0.5 + i * 0.125, at[2] - 0.5 + j * 0.125
            add.polygon([[x, at[1] + 0.735, z], [x, at[1] + 0.735, z + 0.125], [x + 0.125, at[1] + 0.735, z + 0.125],
                         [x + 0.125, at[1] + 0.735, z]], P["white"] if (i + j) % 2 else P["black"])
    for sx in (-0.45, 0.45):
        for sz in (-0.45, 0.45):
            add.cuboid([at[0] + sx, at[1] + 0.35, at[2] + sz], [0.08, 0.7, 0.08], P["wood_dark"])
    add.seed(3)
    for i in range(8):
        for j in range(8):
            if hash2(i, j, 5) < 0.45:
                continue
            white = (j < 4) if hash2(i, j, 6) < 0.8 else (j >= 4)
            c = P["white"] if white else P["black"]
            x, z = at[0] - 0.4375 + i * 0.125, at[2] - 0.4375 + j * 0.125
            kind = hash2(i, j, 8)
            add.cylinder([x, at[1] + 0.75, z], [x, at[1] + 0.78, z], 0.045, 6, c)
            if kind < 0.6:                                                # pawn
                add.cylinder([x, at[1] + 0.78, z], [x, at[1] + 0.86, z], 0.02, 6, c)
                add.sphere([x, at[1] + 0.9, z], 0.035, 5, c)
            elif kind < 0.85:                                              # rook / bishop
                add.cylinder([x, at[1] + 0.78, z], [x, at[1] + 0.95, z], 0.028, 6, c)
                add.cylinder([x, at[1] + 0.95, z], [x, at[1] + 1.0, z], 0.04, 6, c)
            else:                                                          # king / queen
                add.cylinder([x, at[1] + 0.78, z], [x, at[1] + 1.02, z], 0.025, 6, c)
                add.sphere([x, at[1] + 1.05, z], 0.04, 5, c)
                add.cone([x, at[1] + 1.08, z], [x, at[1] + 1.16, z], 0.02, 4, P["gold"])
    chair([at[0], at[1], at[2] + 0.9], add.pi)
    chair([at[0], at[1], at[2] - 0.9], 0)


# --------------------------------------------------------------------------
#  6. Easter egg 1: the great hall -- throne, feast, chandeliers, fireplace
# --------------------------------------------------------------------------
HX0, HX1, HZ0, HZ1 = KX0 + WT, KX1 - WT, KZ0 + WT, KZ1 - WT     # inside the walls
HALL_MID = (HZ0 + HZ1) / 2
# columns, the carpet, the dais and the throne
for x in (-9, 9):
    for z in (-24, -18, -12, -6):
        add.mesh(textured(add.make(add.column, [x, KY, z], HALL_H, 0.45, P["white"], k_(14)), "marble", scale=2))
add.cuboid([0, KY + 0.02, (HZ1 + HZ0 + 3.6) / 2], [3.0, 0.04, HZ1 - HZ0 - 3.6], P["red"])
for sx in (-1.4, 1.4):
    add.cuboid([sx, KY + 0.03, (HZ1 + HZ0 + 3.6) / 2], [0.2, 0.04, HZ1 - HZ0 - 3.6], P["gold"])
add.cuboid([0, KY + 0.3, HZ0 + 2.0], [10, 0.6, 4.0], P["stone_dark"])
add.cuboid([0, KY + 0.62, HZ0 + 2.0], [9.6, 0.04, 3.6], P["red"])
add.stairs([0, KY, HZ0 + 4.0 + 1.0], 2, 6, 0.3, 0.5, P["stone_dark"], direction=(0, 0, -1))
THRONE = [0, KY + 0.6, HZ0 + 1.4]
add.push()
add.cuboid([0, 0.5, 0], [1.6, 0.25, 1.4], P["wood_dark"])
for sx in (-0.7, 0.7):
    for sz in (-0.6, 0.6):
        add.cuboid([sx, 0.2, sz], [0.15, 0.4, 0.15], P["gold"])
add.cuboid([0, 1.9, -0.6], [1.7, 2.8, 0.22], P["wood_dark"])
add.mesh(add.make(add.prism, [[-0.85, 0], [0.85, 0], [0, 0.7]], 0.22, P["gold"], (0, 3.3, -0.6), (0, 0, 1)))
for sx in (-0.85, 0.85):
    add.sphere([sx, 3.35, -0.6], 0.12, k_(8), P["gold"])
add.cuboid([0, 2.0, -0.47], [1.3, 2.0, 0.06], P["cushion"])
for sx in (-0.8, 0.8):
    add.cuboid([sx, 0.95, 0.05], [0.14, 0.6, 1.2], P["wood_dark"])
    add.cuboid([sx, 1.28, 0.05], [0.18, 0.08, 1.3], P["gold"])
    add.sphere([sx, 1.32, 0.65], 0.1, k_(8), P["gold"])
add.cuboid([0, 0.7, 0.1], [1.3, 0.16, 1.1], P["cushion"])
add.torus([0, 0.85, 0.2], 0.28, 0.05, k_(16), 6, P["gold"])                     # the crown, left on the seat
for i in range(5):
    a = 2 * add.pi * i / 5
    add.cone([0.28 * add.cos(a), 0.88, 0.2 + 0.28 * add.sin(a)], [0.26 * add.cos(a), 1.15, 0.2 + 0.26 * add.sin(a)], 0.05, 5, P["gold"])
    add.sphere([0.27 * add.cos(a), 1.16, 0.2 + 0.27 * add.sin(a)], 0.035, 4, P["red"])
add.mesh(add.move(add.pop(), THRONE))
# a canopy above the throne, and the name of the castle on the wall
add.cuboid([0, KY + 5.0, HZ0 + 0.9], [3.6, 0.15, 1.8], P["red"])
for i in range(12):
    add.cuboid([-1.75 + i * 0.32, KY + 4.82, HZ0 + 1.8], [0.2, 0.25, 0.05], P["gold"])
add.mesh(textured(add.make(add.cuboid, [0, KY + 2.6, HZ0 + 0.08], [3.4, 4.6, 0.06], P["red"]), "banner", "fit"))
add.text("ALGORITMŲ PILIS", [0, KY + 7.7, HZ0 + 0.12], 0.8, 0.07, P["gold"], align="center", k=6)
for s in (-1, 1):                                                                 # torch stands by the dais
    add.cylinder([s * 4.2, KY + 0.6, HZ0 + 1.5], [s * 4.2, KY + 2.4, HZ0 + 1.5], 0.06, 6, P["iron"])
    add.cylinder([s * 4.2, KY + 2.4, HZ0 + 1.5], [s * 4.2, KY + 2.6, HZ0 + 1.5], 0.14, 6, P["iron"])
    add.sphere([s * 4.2, KY + 2.85, HZ0 + 1.5], 0.24, k_(8), FLAME)
    armour([s * 6.5, KY + 0.6, HZ0 + 1.6], 0, weapon="spear" if s < 0 else "sword", shield=(s > 0))
flush("hall: throne")

# the feast: two long tables with cloths and benches, laden with food
TABLE_Z0, TABLE_Z1 = HZ0 + 7.0, HZ1 - 5.0
for tx in (-6.0, 6.0):
    L = TABLE_Z1 - TABLE_Z0
    zc = (TABLE_Z0 + TABLE_Z1) / 2
    add.mesh(textured(add.make(add.cuboid, [tx, KY + 1.0, zc], [2.0, 0.1, L], P["wood"]), "planks", "xz", scale=1.5))
    add.cuboid([tx, KY + 1.07, zc], [2.2, 0.03, L + 0.3], P["white"])
    for sx in (-1.1, 1.1):
        add.cuboid([tx + sx, KY + 0.82, zc], [0.03, 0.5, L + 0.3], P["white"])
    for z in (TABLE_Z0 + 0.6, zc, TABLE_Z1 - 0.6):
        for sx in (-0.8, 0.8):
            add.cuboid([tx + sx, KY + 0.5, z], [0.15, 1.0, 0.15], P["wood_dark"])
        add.cuboid([tx, KY + 0.25, z], [1.8, 0.1, 0.15], P["wood_dark"])
    for sx in (-1.7, 1.7):                                                       # benches
        add.cuboid([tx + sx, KY + 0.5, zc], [0.45, 0.08, L - 0.4], P["wood"])
        for z in (TABLE_Z0 + 0.5, TABLE_Z1 - 0.5):
            add.cuboid([tx + sx, KY + 0.25, z], [0.4, 0.5, 0.12], P["wood_dark"])
    top = KY + 1.09
    z = TABLE_Z0 + 0.8
    i = 0
    while z < TABLE_Z1 - 0.8:
        kind = i % 6
        if kind == 0:
            chicken_roast([tx - 0.3, top, z])
            goblet([tx + 0.6, top, z - 0.3])
        elif kind == 1:
            bread([tx + 0.2, top, z], 2)
            jug([tx - 0.6, top, z + 0.2])
        elif kind == 2:
            cheese([tx - 0.4, top, z])
            goblet([tx + 0.5, top, z + 0.3])
            goblet([tx + 0.7, top, z - 0.4])
        elif kind == 3:
            bowl([tx, top, z], 0.4, P["wood_light"], (P["apple"], P["orange"], P["apple"], P["cheese"]))
            grapes([tx + 0.7, top, z + 0.2])
        elif kind == 4:
            candelabra([tx, top, z])
            plate([tx - 0.6, top, z + 0.3])
            fruit([tx - 0.6, top + 0.03, z + 0.3], P["apple"])
            plate([tx + 0.6, top, z - 0.3])
            fruit([tx + 0.6, top + 0.03, z - 0.3], P["orange"], 0.14)
        else:
            plate([tx - 0.5, top, z], 0.35)
            add.mesh(add.move(add.stretch(add.make(add.sphere, [0, 0, 0], 0.2, k_(10), P["steel"]), [0.7, 0.5, 1.6]), [tx - 0.5, top + 0.12, z]))
            jug([tx + 0.5, top, z], P["blue"])
        z += 1.3
        i += 1
roast_pig([-6.0, KY + 1.09, (TABLE_Z0 + TABLE_Z1) / 2 + 0.65])
flush("hall: the feast")

# chandeliers, the fireplace, tapestries, weapons on the wall, a chess game
for z in (HZ0 + 6, HALL_MID, HZ1 - 6):
    chandelier([0, KY + 5.5, z], 1.2, HALL_H - 5.5 - 0.6)
FIRE = [HX0 + 0.6, KY, HALL_MID]
add.mesh(textured(add.make(add.cuboid, [HX0 + 0.5, KY + 4.5, HALL_MID], [1.0, HALL_H, 5.0], P["stone_dark"]), "stone", scale=3))
add.cuboid([HX0 + 0.9, KY + 1.4, HALL_MID], [0.7, 2.8, 3.0], P["black"])                   # the hearth opening
for sz in (-1.6, 1.6):
    add.cuboid([HX0 + 1.0, KY + 1.4, HALL_MID + sz], [1.0, 2.8, 0.4], P["stone"])
add.cuboid([HX0 + 1.0, KY + 3.0, HALL_MID], [1.2, 0.4, 4.0], P["stone"])                   # the mantelpiece
for i in range(4):                                                                        # logs and flames
    add.cylinder([HX0 + 0.7, KY + 0.2 + 0.18 * i, HALL_MID - 1.0 + 0.3 * i], [HX0 + 1.2, KY + 0.35 + 0.2 * i, HALL_MID + 1.0 - 0.3 * i], 0.12, 6, P["trunk"])
for i in range(7):
    add.sphere([HX0 + 0.9 + 0.1 * add.sin(i * 2.0), KY + 0.6 + 0.25 * i, HALL_MID + 0.8 * add.sin(i * 1.7)], 0.4 - 0.04 * i, k_(8), FLAME)
add.sphere([HX0 + 0.9, KY + 0.7, HALL_MID], 0.3, k_(8), P["flame_core"])
candelabra([HX0 + 1.0, KY + 3.2, HALL_MID - 1.2])
goblet([HX0 + 1.0, KY + 3.2, HALL_MID + 1.2])
shield([HX0 + 0.12, KY + 5.2, HALL_MID], add.pi / 2, 0.6)                                 # arms above the fire
sword([HX0 + 0.15, KY + 4.4, HALL_MID - 0.9], (0, 1, 0.7))
sword([HX0 + 0.15, KY + 4.4, HALL_MID + 0.9], (0, 1, -0.7))
for i, z in enumerate((HZ0 + 3.5, HZ1 - 3.5)):                                            # tapestries, west and east walls
    for x, facing in ((HX0 + 0.08, add.pi / 2), (HX1 - 0.08, -add.pi / 2)):
        M = add.make(add.cuboid, [0, 0, 0], [0.04, 3.6, 2.4], P["red"])
        M = add.texture(M, TEX["banner"], lambda p, n: (p[2] / 2.4 + 0.5, p[1] / 3.6 + 0.5))
        add.mesh(add.move(M, [x, KY + 4.5, z]))
        add.cylinder([x, KY + 6.4, z - 1.4], [x, KY + 6.4, z + 1.4], 0.05, 6, P["wood_dark"])
for x in (-16.5, 16.5):                                                                   # torches between the windows
    for z in (HZ0 + 0.7, HZ1 - 0.7):
        torch([x, KY + 3.0, z + (0.0 if z < HALL_MID else 0.0)], 0 if z < HALL_MID else add.pi)
chess_set([HX1 - 3.0, KY, HZ1 - 4.0])
for i in range(3):                                                                        # a few barrels of wine in the corner
    barrel([HX1 - 1.2 - (i % 2) * 1.1, KY, HZ0 + 1.0 + i * 0.5 + (i // 2) * 1.0], 0.42, 1.1, upright=(i != 1))
flush("hall: fireplace and furnishings")


# --------------------------------------------------------------------------
#  7. Easter egg 2: the treasury in the big tower, with a dragon asleep on it
# --------------------------------------------------------------------------
TR = [DON[0], G + 0.1, DON[1]]
add.seed(42)
HEAP = [TR[0] + 0.6, TR[1], TR[2]]
add.mesh(add.move(add.stretch(add.make(add.hemisphere, [0, 0, 0], 3.0, k_(18), P["gold"]), [1.0, 0.45, 1.0], (0, 0, 0)), HEAP))
for i in range((350, 1200, 4000)[DETAIL - 1]):                                   # coins
    a, rr = add.uniform(0, 2 * add.pi), add.uniform(0, 4.6)
    x, z = HEAP[0] + rr * add.cos(a), HEAP[2] + rr * add.sin(a)
    d = add.sqrt((x - HEAP[0]) ** 2 + (z - HEAP[2]) ** 2)
    y = HEAP[1] + (0.45 * add.sqrt(max(0.0, 9 - d * d)) if d < 3 else 0.0)
    coin = add.make(add.cylinder, [0, 0, 0], [0, 0.025, 0], 0.09, k_(8), P["gold"])
    coin = add.rotateX(coin, add.uniform(-0.5, 0.5))
    add.mesh(add.move(add.rotateY(coin, a), [x, y + 0.02, z]))
for i in range((25, 60, 150)[DETAIL - 1]):                                        # gems
    a, rr = add.uniform(0, 2 * add.pi), add.uniform(0, 2.8)
    d2 = rr * rr
    add.sphere([HEAP[0] + rr * add.cos(a), HEAP[1] + 0.45 * add.sqrt(9 - d2) + 0.08, HEAP[2] + rr * add.sin(a)],
               add.uniform(0.07, 0.14), 4, add.choice([P["red"], P["blue"], P["purple"], P["leaf"]]))
for i in range(4):
    a = 1.1 + i * 1.5
    goblet([HEAP[0] + 2.2 * add.cos(a), HEAP[1] + 0.45 * add.sqrt(9 - 2.2 * 2.2), HEAP[2] + 2.2 * add.sin(a)])
sword([HEAP[0] - 1.0, HEAP[1] + 0.9, HEAP[2] + 1.0], (0.2, 1, 0.1))
# an open chest, gold spilling out
CHEST = [TR[0] - 3.0, TR[1], TR[2] + 2.5]
add.push()
add.cuboid([0, 0.4, 0], [1.6, 0.8, 1.0], P["wood_dark"])
add.cuboid([0, 0.5, 0], [1.66, 0.12, 1.06], P["iron"])
for sx in (-0.7, 0.7):
    add.cuboid([sx, 0.4, 0], [0.1, 0.82, 1.06], P["iron"])
add.mesh(add.rotateX(add.make(add.cuboid, [0, 0.12, 0], [1.6, 0.24, 1.0], P["wood_dark"]), -1.9, (0, 0.8, -0.5)))
add.mesh(add.move(add.stretch(add.make(add.sphere, [0, 0, 0], 0.7, k_(10), P["gold"]), [1.0, 0.5, 0.7]), [0, 0.75, 0]))
for i in range(12):
    add.cylinder([add.uniform(-0.7, 0.7), 0.95 + add.uniform(0, 0.1), add.uniform(-0.4, 0.4)],
                 [add.uniform(-0.7, 0.7), 0.97 + add.uniform(0, 0.1), add.uniform(-0.4, 0.4)], 0.08, k_(8), P["gold"])
add.mesh(add.move(add.rotateY(add.pop(), 0.6), CHEST))
add.torus([TR[0] + 3.5, TR[1] + 0.06, TR[2] - 2.8], 0.35, 0.06, k_(16), 6, P["gold"])   # a crown that rolled away
add.sphere([TR[0] - 3.6, TR[1] + 0.25, TR[2] - 2.6], 0.25, k_(10), P["bone"])            # ... and the last thief
add.cuboid([TR[0] - 3.6, TR[1] + 0.08, TR[2] - 2.4], [0.3, 0.14, 0.25], P["bone"])
for i in range(4):
    add.cylinder([TR[0] - 3.2 + 0.25 * i, TR[1] + 0.05, TR[2] - 2.9], [TR[0] - 3.1 + 0.25 * i, TR[1] + 0.05, TR[2] - 1.9], 0.04, 5, P["bone"])
flush("treasury")


def dragon(at, facing=0.0, size=1.0):
    """A dragon curled up asleep: body, head with horns, folded wings, spines."""
    add.push()

    def radius(t):
        return 0.55 * add.sin(add.pi * min(1.0, 0.3 + 0.9 * t)) ** 0.6 * (1 - 0.6 * t) + 0.05

    def spine(t):                                                          # a spiral lying on the heap of gold
        a = 1.5 * add.pi * t
        rr = 2.6 - 1.7 * t
        heap = 0.45 * add.sqrt(max(0.0, 9 - (size * rr) ** 2)) / size
        return [rr * add.cos(a), heap + 0.8 * radius(t), rr * add.sin(a)]

    pts = [spine(i / 40.0) for i in range(41)]
    body = add.make(add.polyline, pts, radius, k_(14), P["dragon"], smooth=0)

    def belly(p):                                                          # lighter underneath
        s = min(pts, key=lambda q: (q[0] - p[0]) ** 2 + (q[2] - p[2]) ** 2)
        return P["dragon_belly"] if p[1] < s[1] - 0.12 else P["dragon"]

    add.mesh(add.color_by(body, belly))
    for i in range(0, 34, 2):                                               # spines along the back
        p = pts[i]
        r = radius(i / 40.0)
        add.cone([p[0], p[1] + r * 0.9, p[2]], [p[0], p[1] + r * 0.9 + 0.35 * (1 - i / 40.0) + 0.1, p[2]], 0.08, 4, P["dragon"])
    add.cone(pts[-2], [pts[-1][0] * 1.1, pts[-1][1], pts[-1][2] * 1.1], 0.06, 4, P["dragon"])
    tail = pts[-1]
    add.mesh(add.move(add.make(add.prism, [[0, 0], [0.5, -0.3], [0.5, 0.3]], 0.06, P["dragon"], (0, 0, 0)), tail))
    head_at = [pts[0][0] + 0.9, pts[0][1] + 0.1, pts[0][2] - 0.2]            # the head lies on the front paws
    head = add.stretch(add.make(add.sphere, [0, 0, 0], 0.55, k_(14), P["dragon"]), [1.5, 0.75, 0.9])
    add.mesh(add.move(head, head_at))
    for s in (-1, 1):
        add.cone([head_at[0] - 0.3, head_at[1] + 0.3, head_at[2] + s * 0.25], [head_at[0] - 0.8, head_at[1] + 0.9, head_at[2] + s * 0.45], 0.08, 5, P["bone"])
        add.sphere([head_at[0] + 0.72, head_at[1] + 0.02, head_at[2] + s * 0.16], 0.05, 4, P["black"])   # nostrils
        add.cuboid([head_at[0] + 0.25, head_at[1] + 0.22, head_at[2] + s * 0.3], [0.3, 0.03, 0.08], P["black"])   # closed eyes
        for i in range(3):                                                   # smoke from the nostrils
            add.sphere([head_at[0] + 0.9 + 0.25 * i, head_at[1] + 0.1 + 0.2 * i, head_at[2] + s * (0.2 + 0.1 * i)], 0.08 + 0.05 * i, k_(6), SMOKE)
        paw = [head_at[0] - 0.2, 0.15, head_at[2] + s * 0.7]
        add.capsule([paw[0] - 0.6, 0.25, paw[2]], paw, 0.16, k_(8), P["dragon"])
        for j in range(3):
            add.cone([paw[0] + 0.1, 0.12, paw[2] - 0.12 + j * 0.12], [paw[0] + 0.4, 0.05, paw[2] - 0.15 + j * 0.15], 0.04, 4, P["bone"])
        wing = add.make(add.prism, [[0, 0], [1.8, 0.3], [0.9, 1.1]], 0.05, P["dragon"], (0, 0, 0), (0, 0, 1))
        wing.extend(add.make(add.polyline, [[0, 0, 0], [0.9, 1.1, 0], [1.8, 0.3, 0]], 0.05, 5, P["dragon_belly"]))
        wing = add.rotateZ(wing, -1.25)                                       # folded down along the flank
        wing = add.rotateY(wing, add.pi / 2 + (add.pi if s > 0 else 0))
        add.mesh(add.move(wing, [pts[8][0], pts[8][1] + 0.35, pts[8][2] + s * 0.3]))
    M = add.pop()
    M = add.stretch(M, [size, size, size], (0, 0, 0))
    add.mesh(add.move(add.rotateY(M, facing), at))


dragon([HEAP[0], HEAP[1], HEAP[2]], -1.2, 1.1)
for i in range(6):                                                          # torches round the treasury wall
    a = 2 * add.pi * i / 6 + 0.3
    torch([TR[0] + (DON_R - 1.05) * add.cos(a), TR[1] + 2.4, TR[2] + (DON_R - 1.05) * add.sin(a)], -a - add.pi / 2)
flush("dragon")


# --------------------------------------------------------------------------
#  8. The courtyard: cobbles, the well, the fountain, the smithy, a market,
#     a trebuchet, a cannon, carts, barrels, crates, weapon racks, animals
# --------------------------------------------------------------------------
YARD_R = 47.0
if DETAIL == 1:
    add.mesh(textured(add.make(add.cylinder, [0, G - 0.3, 0], [0, G + 0.06, 0], YARD_R, 48, P["stone_dark"]), "cobble", "xz", scale=2))
else:
    add.mesh(textured(add.make(add.cylinder, [0, G - 0.3, 0], [0, G + 0.02, 0], YARD_R, 96, P["mortar"]), "cobble", "xz", scale=2))
    add.seed(5)
    step = 0.5 if DETAIL == 2 else 0.3
    n = 0
    x = -YARD_R
    while x < YARD_R:
        z = -YARD_R
        while z < YARD_R:
            xx, zz = x + add.uniform(-0.1, 0.1) * step, z + add.uniform(-0.1, 0.1) * step
            inside = xx * xx + zz * zz < (YARD_R - 0.5) ** 2
            in_palace = KX0 - 1 < xx < KX1 + 1 and KZ0 - 1 < zz < KZ1 + 1
            if inside and not in_palace:
                stone = add.make(add.sphere, [0, 0, 0], step * 0.55, subdivisions=(0 if DETAIL == 2 else 1),
                                 color=pick("stone_dark", n, 0))
                add.mesh(add.move(add.stretch(stone, [1.0, 0.45, 1.0], (0, 0, 0)), [xx, G + 0.02, zz]))
                n += 1
                if n % 6000 == 0:
                    flush("cobblestones (%d)" % n)
            z += step
        x += step
flush("courtyard ground")

# the road through the gate, continuing the cobbled way to the palace
add.mesh(textured(add.make(add.cuboid, [0, G + 0.08, (KZ1 + 3 + GATE_Z1 + 1) / 2], [5.0, 0.08, GATE_Z1 + 1 - KZ1 - 3], P["stone"]), "cobble", "xz", scale=1.5))


def well(at):
    """A well with a windlass, a rope and a bucket, under a little roof."""
    add.push()
    add.mesh(textured(add.make(add.pipe, [0, 0, 0], [0, 1.0, 0], 1.2, 0.9, k_(16), P["stone"]), "stone", scale=1.5))
    for i in range(k_(12)):
        a = 2 * add.pi * i / k_(12)
        add.cuboid([1.05 * add.cos(a), 1.06, 1.05 * add.sin(a)], [0.45, 0.14, 0.45], pick("stone", i, 4))
    add.cylinder([0, 0.02, 0], [0, 0.05, 0], 0.9, k_(16), WATER)
    for sx in (-1.4, 1.4):
        add.cuboid([sx, 1.4, 0], [0.2, 2.8, 0.2], P["wood_dark"])
    add.cylinder([-1.4, 2.2, 0], [1.4, 2.2, 0], 0.16, k_(10), P["wood"])                         # the windlass
    add.helix([0, 2.2, 0], 0.17, 0.05, 6, 40, 0.02, 4, P["rope"], axis=(1, 0, 0))
    add.polyline([[1.55, 2.2, 0], [1.75, 2.2, 0], [1.75, 2.6, 0], [1.95, 2.6, 0]], 0.04, 6, P["iron"])   # the crank
    add.cylinder([0, 2.2, 0], [0, 1.4, 0], 0.015, 4, P["rope"])
    add.mesh(add.move(add.make(add.revolve, lambda t: [[0.18, 0], [0.22, 0.3], [0.2, 0.3], [0.16, 0.02]][min(3, int(round(t)))],
                               [0, 0, 0], [0, 1, 0], 0, 3, 3, k_(10), P["wood_dark"]), [0, 1.1, 0]))
    add.arch([-0.2, 1.4, 0], [0.2, 1.4, 0], 0.25, 0.015, P["iron"], 8, 4)
    roof = add.make(add.roof, [0, 2.8, 0], [3.6, 2.2], 1.0, P["slate"], 0.2)
    add.mesh(add.texture(roof, TEX["slate"], "box", scale=0.4))
    add.mesh(add.move(add.pop(), at))


def fountain(at):
    add.push()
    add.mesh(textured(add.make(add.pipe, [0, 0, 0], [0, 0.7, 0], 2.6, 2.3, k_(24), P["stone"]), "marble", scale=2))
    add.cylinder([0, 0.05, 0], [0, 0.55, 0], 2.3, k_(24), WATER)
    add.column([0, 0, 0], 1.8, 0.25, P["white"], k_(12))
    lathe([[0.0, 0], [0.3, 0], [0.9, 0.25], [1.0, 0.4], [0.9, 0.4], [0.8, 0.28], [0.25, 0.1], [0.0, 0.1]], [0, 1.9, 0], k_(16), P["white"])
    add.cylinder([0, 2.1, 0], [0, 2.4, 0], 0.9, k_(16), WATER)
    add.cylinder([0, 1.9, 0], [0, 3.2, 0], 0.06, 6, WATER)
    for i in range(8):
        a = 2 * add.pi * i / 8
        arc = [[0.1 * add.cos(a) * j + 0.55 * add.cos(a) * (j / 6.0) ** 0.5 * 2.5, 3.2 - 0.9 * (j / 6.0) ** 2 * 3.0,
                0.1 * add.sin(a) * j + 0.55 * add.sin(a) * (j / 6.0) ** 0.5 * 2.5] for j in range(7)]
        add.polyline(arc, 0.04, 5, WATER)
    add.mesh(add.move(add.pop(), at))


def cart(at, facing=0.0, load="barrels"):
    add.push()
    add.mesh(textured(add.make(add.cuboid, [0, 0.9, 0], [3.2, 0.12, 1.8], P["wood"]), "planks", "xz", scale=1.5))
    for sz in (-0.9, 0.9):
        for i in range(3):
            add.cuboid([0, 1.1 + i * 0.28, sz], [3.2, 0.2, 0.06], pick("wood", i, 6))
        for sx in (-1.5, 0, 1.5):
            add.cuboid([sx, 1.25, sz], [0.08, 0.8, 0.08], P["wood_dark"])
    for sx in (-1.5, 1.5):
        for i in range(3):
            add.cuboid([sx, 1.1 + i * 0.28, 0], [0.06, 0.2, 1.8], pick("wood", i, 7))
    add.cylinder([0, 0.75, -1.05], [0, 0.75, 1.05], 0.08, 6, P["iron"])
    for sz in (-1.0, 1.0):
        add.wheel([0, 0.75, sz], 0.75, 0.12, P["wood_dark"], (0, 0, 1), k_(18), spokes=8, hub_color=P["iron"])
    for sz in (-0.5, 0.5):
        add.cylinder([1.6, 0.85, sz], [3.8, 0.6, sz], 0.06, 6, P["wood_dark"])                  # the shafts
    if load == "barrels":
        barrel([-0.9, 0.96, 0.0], 0.42, 1.0, upright=False)
        barrel([0.0, 0.96, 0.0], 0.42, 1.0, upright=False)
        sack([0.9, 0.96, 0.3], 0.35)
        sack([0.9, 0.96, -0.4], 0.32)
    else:
        for i in range(18):                                                   # hay
            add.sphere([add.uniform(-1.3, 1.3), 1.2 + add.uniform(0, 0.5), add.uniform(-0.6, 0.6)], add.uniform(0.35, 0.55), k_(8), P["straw"])
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def plank_stack(at, n=4, facing=0.0):
    add.push()
    for j in range(n):
        for i in range(5):
            if j % 2 == 0:
                add.cuboid([0, 0.08 + j * 0.16, -0.7 + i * 0.35], [3.0, 0.15, 0.3], pick("wood_light", i, j))
            else:
                add.cuboid([-1.2 + i * 0.6, 0.08 + j * 0.16, 0], [0.3, 0.15, 1.7], pick("wood_light", i, j))
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def brick_stack(at, nx=6, ny=5, nz=3):
    for j in range(ny):
        for i in range(nx):
            for k in range(nz):
                if j == ny - 1 and hash2(i, k, j) < 0.4:
                    continue
                add.cuboid([at[0] + (i + 0.5) * 0.62 + (0.31 if j % 2 else 0), at[1] + (j + 0.5) * 0.31, at[2] + (k + 0.5) * 0.32],
                           [0.6, 0.29, 0.3], pick("brick", i + 7 * j, k))


def weapon_rack(at, facing=0.0):
    add.push()
    for sx in (-1.4, 1.4):
        add.cuboid([sx, 0.9, 0], [0.15, 1.8, 0.15], P["wood_dark"])
    add.cuboid([0, 1.7, 0], [3.0, 0.12, 0.12], P["wood_dark"])
    add.cuboid([0, 0.5, 0], [3.0, 0.12, 0.12], P["wood_dark"])
    for i in range(5):
        spear([-1.1 + i * 0.55, 0.0, 0.12], 2.6)
    for i in range(3):
        sword([-0.9 + i * 0.9, 0.6, -0.14], (0, 1, 0), 0.9)
    axe([0.6, 0.0, -0.3], 1.3)
    axe([-0.4, 0.0, -0.3], 1.1)
    shield([-1.9, 0.0, -0.1], 0.3, 0.45)
    shield([1.9, 0.0, -0.1], -0.3, 0.45)
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def dummy(at):
    """A training dummy: a post, a straw body and an old shield."""
    add.cylinder(at, [at[0], at[1] + 2.2, at[2]], 0.08, 6, P["wood_dark"])
    add.sphere([at[0], at[1] + 1.5, at[2]], 0.4, k_(10), P["straw"])
    add.sphere([at[0], at[1] + 2.1, at[2]], 0.22, k_(8), P["straw"])
    add.cylinder([at[0] - 0.7, at[1] + 1.6, at[2]], [at[0] + 0.7, at[1] + 1.6, at[2]], 0.05, 6, P["wood_dark"])
    shield([at[0] - 0.7, at[1] + 1.2, at[2] + 0.1], 0, 0.35)


def trebuchet(at, facing=0.0):
    add.push()
    for sz in (-1.2, 1.2):                                                    # two A-frames
        add.beam([-1.6, 0, sz], [0, 4.5, sz], 0.25, 0.25, P["wood_dark"])
        add.beam([1.6, 0, sz], [0, 4.5, sz], 0.25, 0.25, P["wood_dark"])
        add.beam([-1.8, 0.15, sz], [1.8, 0.15, sz], 0.3, 0.3, P["wood_dark"])
        add.beam([-0.9, 2.2, sz], [0.9, 2.2, sz], 0.18, 0.18, P["wood"])
    add.beam([0, 0.15, -1.4], [0, 0.15, 1.4], 0.3, 0.3, P["wood_dark"])
    add.cylinder([0, 4.5, -1.5], [0, 4.5, 1.5], 0.12, k_(8), P["iron"])         # the axle
    arm = add.make(add.beam, [-2.4, 0, 0], [5.5, 0, 0], 0.25, 0.3, P["wood"])
    arm.extend(add.make(add.cuboid, [-2.4, -0.9, 0], [1.2, 1.2, 1.2], P["iron"]))   # the counterweight
    arm.extend(add.make(add.cylinder, [5.4, 0, 0], [5.6, 0, 0], 0.08, 6, P["iron"]))
    sling = add.make(add.polyline, [[5.5, 0, 0], [6.5, -2.2, 0], [7.5, -2.9, 0]], 0.02, 4, P["rope"])
    sling.extend(add.make(add.sphere, [7.5, -2.9, 0], 0.4, k_(10), P["rock"]))
    arm.extend(sling)
    add.mesh(add.move(add.rotateZ(arm, 0.55), [0, 4.5, 0]))
    for sx in (-1.6, 1.6):
        for sz in (-1.5, 1.5):
            add.wheel([sx, 0.45, sz], 0.45, 0.2, P["wood_dark"], (0, 0, 1), k_(14), spokes=6, hub_color=P["iron"])
    for i, (dx, dz) in enumerate(((3.2, 1.2), (3.9, 1.5), (3.5, 2.0), (3.6, 1.55))):                 # a pile of stone balls
        add.sphere([dx, 0.4 + (0.6 if i == 3 else 0), dz], 0.4, k_(10), P["rock"])
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def cannon(at, facing=0.0):
    add.push()
    for sz in (-0.35, 0.35):
        add.mesh(add.make(add.prism, [[-1.2, 0.3], [1.0, 0.3], [0.6, 1.1], [-0.9, 0.9]], 0.16, P["wood_dark"], (0, 0, sz), (0, 0, 1)))
    add.cylinder([-0.6, 0.6, -0.5], [-0.6, 0.6, 0.5], 0.06, 6, P["iron"])
    for sz in (-0.5, 0.5):
        add.wheel([-0.6, 0.6, sz], 0.6, 0.15, P["wood_dark"], (0, 0, 1), k_(14), spokes=8, hub_color=P["iron"])
    barrel_ = add.make(add.frustum, [-1.0, 1.05, 0], [1.9, 1.15, 0], 0.32, 0.22, k_(14), P["copper"])
    barrel_.extend(add.make(add.sphere, [-1.05, 1.05, 0], 0.3, k_(10), P["copper"]))
    barrel_.extend(add.make(add.torus, [1.8, 1.15, 0], 0.24, 0.05, k_(14), 6, P["copper"], axis=(1, 0, 0)))
    barrel_.extend(add.make(add.cylinder, [1.9, 1.15, 0], [1.75, 1.15, 0], 0.17, k_(10), P["black"]))
    add.mesh(barrel_)
    for j in range(3):                                                        # a pyramid of cannon balls
        for i in range(3 - j):
            for k in range(3 - j):
                add.sphere([-2.2 + (i + 0.5 * j) * 0.5, 0.25 + j * 0.42, -0.5 + (k + 0.5 * j) * 0.5], 0.25, k_(8), P["iron"])
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def smithy(at, facing=0.0):
    """An open forge: posts and a lean-to roof, the hearth, anvil, trough, tools."""
    add.push()
    for sx in (-3.0, 3.0):
        add.cuboid([sx, 1.7, 2.4], [0.25, 3.4, 0.25], P["wood_dark"])
        add.cuboid([sx, 2.2, -2.4], [0.25, 4.4, 0.25], P["wood_dark"])
    add.mesh(textured(add.make(add.cuboid, [0, 2.2, -2.5], [6.4, 4.4, 0.3], P["stone"]), "brick", scale=1.5))   # the back wall
    roof = add.make(add.polygon, [[-3.4, 3.5, 2.9], [3.4, 3.5, 2.9], [3.4, 4.5, -2.8], [-3.4, 4.5, -2.8]], P["slate"])
    roof.extend(add.make(add.polygon, [[-3.4, 3.5, 2.9], [-3.4, 4.5, -2.8], [3.4, 4.5, -2.8], [3.4, 3.5, 2.9]], P["wood_dark"]))
    add.mesh(add.texture(roof, TEX["slate"], "xz", scale=0.5))
    for i in range(4):
        add.beam([-3.2 + i * 2.1, 3.42, 2.6], [-3.2 + i * 2.1, 4.42, -2.6], 0.15, 0.15, P["wood_dark"])
    add.mesh(textured(add.make(add.cuboid, [-1.6, 0.5, -1.4], [2.2, 1.0, 1.8], P["brick"]), "brick", scale=1.0))   # the hearth
    add.cuboid([-1.6, 1.05, -1.4], [1.6, 0.1, 1.2], P["black"])
    for i in range(5):
        add.sphere([-1.9 + 0.15 * i, 1.2 + 0.12 * i, -1.5 + 0.1 * add.sin(i * 2)], 0.28 - 0.03 * i, k_(8), FLAME)
    add.sphere([-1.6, 1.25, -1.4], 0.18, k_(6), P["flame_core"])
    add.mesh(textured(add.make(add.cuboid, [-1.6, 3.0, -2.0], [1.0, 4.0, 0.9], P["brick"]), "brick", scale=1.0))  # chimney
    for i in range(4):
        add.sphere([-1.6 + 0.2 * add.sin(i), 5.3 + 0.7 * i, -2.0], 0.3 + 0.1 * i, k_(8), SMOKE)
    add.cylinder([1.0, 0, 0.2], [1.0, 0.7, 0.2], 0.35, k_(10), P["trunk"])                       # the anvil on a stump
    add.cuboid([1.0, 0.85, 0.2], [0.5, 0.3, 0.3], P["iron"])
    add.cuboid([1.0, 1.08, 0.2], [1.1, 0.16, 0.34], P["iron"])
    add.cone([1.55, 1.08, 0.2], [2.0, 1.08, 0.2], 0.09, 6, P["iron"])
    add.cylinder([1.2, 1.16, 0.1], [1.2, 1.55, 0.6], 0.03, 5, P["wood"])                          # a hammer left on it
    add.cuboid([1.2, 1.55, 0.6], [0.14, 0.14, 0.3], P["iron"])
    add.cuboid([2.2, 0.35, -1.2], [1.6, 0.7, 0.8], P["wood_dark"])                                # the water trough
    add.cuboid([2.2, 0.66, -1.2], [1.5, 0.04, 0.7], WATER)
    for i in range(4):                                                                             # horseshoes on the wall
        add.torus([-2.6 + i * 0.5, 2.4, -2.32], 0.14, 0.035, 8, 4, P["iron"], axis=(0, 0, 1))
    add.polyline([[2.6, 0.0, 1.2], [2.6, 1.2, 1.2]], 0.04, 5, P["iron"])                           # tongs leaning on a post
    add.polyline([[2.7, 0.0, 1.3], [2.65, 1.2, 1.2]], 0.04, 5, P["iron"])
    add.wheel([-2.6, 0.6, 1.2], 0.6, 0.25, P["stone_dark"], (1, 0, 0), k_(14), hub_color=P["iron"])   # the grindstone
    add.cuboid([-2.6, 0.3, 1.2], [0.5, 0.6, 1.3], P["wood_dark"])
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def cottage(at, facing=0.0, w=7.0, d=5.0, h=3.2):
    """A half-timbered house with a thatched roof."""
    add.push()
    add.cuboid([0, h / 2, 0], [w, h, d], P["white"])
    for x in (-w / 2, w / 2):
        add.cuboid([x, h / 2, 0], [0.2, h, 0.2], P["wood_dark"])
        for z in (-d / 2, d / 2):
            add.cuboid([x, h / 2, z], [0.2, h, 0.2], P["wood_dark"])
    for z in (-d / 2, d / 2):
        for i in range(1, int(w / 1.5)):
            add.cuboid([-w / 2 + i * 1.5, h / 2, z], [0.16, h, 0.14], P["wood_dark"])
        add.cuboid([0, h - 0.1, z], [w, 0.2, 0.14], P["wood_dark"])
        add.cuboid([0, h / 2, z], [w, 0.16, 0.14], P["wood_dark"])
        add.beam([-w / 2, 0.2, z], [-w / 2 + 1.5, h / 2 - 0.1, z], 0.12, 0.12, P["wood_dark"])
        add.beam([w / 2, 0.2, z], [w / 2 - 1.5, h / 2 - 0.1, z], 0.12, 0.12, P["wood_dark"])
    for x in (-w / 2, w / 2):
        add.cuboid([x, h / 2, 0], [0.14, 0.16, d], P["wood_dark"])
    for sx in (-w / 4, w / 4):                                                               # windows
        add.cuboid([sx, h * 0.55, d / 2 + 0.02], [1.0, 1.0, 0.06], GLASS)
        add.cuboid([sx, h * 0.55, d / 2 + 0.05], [1.1, 0.08, 0.08], P["wood_dark"])
        add.cuboid([sx, h * 0.55, d / 2 + 0.05], [0.08, 1.1, 0.08], P["wood_dark"])
        for dx in (-0.55, 0.55):
            add.cuboid([sx + dx, h * 0.55, d / 2 + 0.05], [0.08, 1.1, 0.08], P["wood_dark"])
    add.cuboid([0, 1.0, d / 2 + 0.03], [1.1, 2.0, 0.1], P["wood_dark"])                       # the door
    add.sphere([0.35, 1.0, d / 2 + 0.1], 0.06, 4, P["gold"])
    thatch = add.make(add.roof, [0, h, 0], [w + 0.6, d + 0.6], 2.6, P["straw"], 0.4)
    add.mesh(add.rotateY(thatch, add.pi / 2))
    add.cuboid([w / 4, h + 2.0, 0], [0.7, 2.5, 0.7], P["stone_dark"])
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def chicken(at, facing=0.0):
    add.push()
    add.mesh(add.stretch(add.make(add.sphere, [0, 0.32, 0], 0.22, k_(8), P["white"]), [1.3, 0.9, 1.0]))
    add.sphere([0.3, 0.55, 0], 0.11, k_(6), P["white"])
    add.cone([0.4, 0.55, 0], [0.55, 0.53, 0], 0.035, 4, P["orange"])
    add.cuboid([0.3, 0.68, 0], [0.12, 0.08, 0.03], P["red"])
    add.mesh(add.make(add.prism, [[-0.2, 0.35], [-0.5, 0.6], [-0.45, 0.3]], 0.05, P["black"], (0, 0, 0), (0, 0, 1)))
    for sz in (-0.08, 0.08):
        add.cylinder([0.02, 0.15, sz], [0.02, 0, sz], 0.02, 4, P["orange"])
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def haystack(at, r=1.3, h=2.2):
    add.cone(at, [at[0], at[1] + h, at[2]], r, k_(12), P["straw"])
    add.cylinder([at[0], at[1] + h - 0.3, at[2]], [at[0], at[1] + h + 0.5, at[2]], 0.05, 4, P["wood_dark"])


def garden(at, w=8.0, d=5.0):
    """Flower beds with a low hedge round a small tree."""
    add.push()
    for x in (-w / 2, w / 2):
        add.cuboid([x, 0.3, 0], [0.5, 0.6, d + 0.5], P["leaf_dark"])
    for z in (-d / 2, d / 2):
        add.cuboid([0, 0.3, z], [w + 0.5, 0.6, 0.5], P["leaf_dark"])
    add.cuboid([0, 0.05, 0], [w - 0.6, 0.1, d - 0.6], P["trunk"])
    add.seed(9)
    for i in range((60, 160, 400)[DETAIL - 1]):
        x, z = add.uniform(-w / 2 + 0.6, w / 2 - 0.6), add.uniform(-d / 2 + 0.6, d / 2 - 0.6)
        if abs(x) < 1.0 and abs(z) < 1.0:
            continue
        add.cylinder([x, 0.1, z], [x, 0.45, z], 0.015, 4, P["leaf"])
        add.sphere([x, 0.5, z], 0.09, 4, add.choice([P["red"], P["cheese"], P["white"], P["purple"], P["orange"]]))
    add.tree([0, 0.1, 0], 3.5, P["trunk"], P["leaf"], "round", k_(8), seed=3)
    add.mesh(add.move(add.pop(), at))


def market(at, facing=0.0):
    """A market stall: a counter under a striped awning, and the goods."""
    add.push()
    add.mesh(textured(add.make(add.cuboid, [0, 0.95, 0], [4.0, 0.1, 1.6], P["wood"]), "planks", "xz", scale=1.5))
    for sx in (-1.8, 1.8):
        for sz in (-0.6, 0.6):
            add.cuboid([sx, 0.45, sz], [0.12, 0.9, 0.12], P["wood_dark"])
        add.cuboid([sx, 1.9, -0.9], [0.12, 2.0, 0.12], P["wood_dark"])
        add.cuboid([sx, 1.5, 0.9], [0.12, 1.2, 0.12], P["wood_dark"])
    for i in range(8):                                                                   # the striped awning
        x = -2.0 + i * 0.5 + 0.25
        add.mesh(add.make(add.polygon, [[x - 0.25, 2.9, -1.1], [x + 0.25, 2.9, -1.1], [x + 0.25, 2.1, 1.2], [x - 0.25, 2.1, 1.2]],
                          P["red"] if i % 2 else P["white"]))
        add.mesh(add.make(add.polygon, [[x - 0.25, 2.9, -1.1], [x - 0.25, 2.1, 1.2], [x + 0.25, 2.1, 1.2], [x + 0.25, 2.9, -1.1]],
                          P["red"] if i % 2 else P["white"]))
    bowl([-1.4, 1.0, 0.2], 0.4, P["wood_light"], (P["apple"], P["apple"], P["cheese"]))
    bowl([-0.6, 1.0, -0.3], 0.4, P["wood_light"], (P["orange"], P["orange"]))
    bread([0.2, 1.0, 0.2], 3)
    cheese([1.0, 1.0, -0.3])
    for i in range(3):
        add.mesh(add.move(add.stretch(add.make(add.sphere, [0, 0, 0], 0.18, k_(8), P["steel"]), [0.6, 0.5, 1.7]), [1.5, 1.1, -0.5 + i * 0.4]))
    jug([1.6, 1.0, 0.5])
    sack([-1.2, 0.0, 1.3], 0.4)
    sack([-0.4, 0.0, 1.4], 0.35)
    crate([0.9, 0.0, 1.4], 0.7)
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


well([12, G, 24])
fountain([0, G, 15])
market([-12, G, 30], 0.3)
smithy([-34, G, 6], add.pi / 2 - 0.3)
cottage([-33, G, 22], add.pi / 2 + 0.2)
haystack([-36, G, 32])
haystack([-33.5, G, 34.5], 1.0, 1.8)
cart([-24, G, 36], 0.4, "hay")
cart([17, G, 42], -0.9, "barrels")
trebuchet([28, G, 18], -0.7)
cannon([8, G, 41], -0.3)
cannon([-8, G, 41], 0.3)
weapon_rack([-26, G, 12], 0.4)
weapon_rack([-22, G, 14], 0.4)
dummy([-19, G, 20])
plank_stack([30, G, 30], 5, 0.3)
plank_stack([30, G, 32.5], 3, 0.25)
brick_stack([33, G, 25])
brick_stack([33, G, 21], 5, 3, 2)
garden([30, G, 2])
garden([-32, G, -8], 6, 6)
for i in range(4):                                                                       # barrels and crates by the wall
    barrel([36 + (i % 2) * 1.0, G + (1.2 if i >= 2 else 0), 10 + (i // 2) * 0.0 + (i % 2) * 0.1], 0.45, 1.2)
barrel([38.5, G, 12.5], 0.45, 1.2, upright=False)
crate([36, G, 14], 0.9)
crate([36, G + 0.9, 14], 0.8)
crate([37.5, G, 14.5], 0.7)
sack([35, G, 16], 0.4)
sack([35.8, G, 16.4], 0.36)
add.seed(21)
for i in range(9):                                                                       # chickens round the cottage
    chicken([-30 + add.uniform(-6, 5), G + 0.06, 24 + add.uniform(-4, 6)], add.uniform(0, 6.28))
for x, z in ((15, 8), (-15, 8), (40, 0), (-40, 0), (24, 40), (-30, 40)):                 # trees in the yard
    add.tree([x, G, z], 6.5, P["trunk"], P["leaf"], "round", k_(9), seed=int(x + z))
flush("courtyard")

# torches along the inside of the wall, stairs up to the walk, flags on the towers
for k in range(8):
    a, b = CORNERS[k], CORNERS[(k + 1) % 8]
    L, d, n = outward(a, b)
    for t in (0.25, 0.5, 0.75):
        if k == 1 and abs(t - 0.5) < 0.3:
            continue
        p = [a[0] + d[0] * L * t - n[0] * 1.45, G + 3.5, a[2] + d[2] * L * t - n[2] * 1.45]
        torch(p, add.atan2(-n[0], -n[2]))
    a2 = [a[0] - n[0] * 1.9, G, a[2] - n[2] * 1.9]                                          # stairs along the inner face
    if k in (3, 7):
        steps = 24
        add.mesh(frame_to(add.make(add.stairs, [0, 0, 0], steps, 1.8, (WALL_TOP - G) / steps, 0.6, P["stone_dark"], (1, 0, 0)),
                          [a2[0] + d[0] * 6, G, a2[2] + d[2] * 6], d, n))
for k, c in enumerate(CORNERS):
    top = G + 16 + 0.35 + 8
    add.cylinder([c[0], top, c[2]], [c[0], top + 3.5, c[2]], 0.06, 6, P["iron"])
    banner([c[0] + 0.05, top + 3.3, c[2]], 1.3, 0.9, add.pi / 2 + k * 0.4, pole=False)
# guards on the wall walk: two on patrol, one asleep by a tower
armour([CORNERS[0][0] - 5, WALL_TOP + 0.3, CORNERS[0][2] + 3], 2.0)
armour([CORNERS[4][0] + 6, WALL_TOP + 0.3, CORNERS[4][2] - 4], -1.2, weapon="sword")
sleeper = add.make(armour, [0, 0, 0], 0, weapon="spear", shield=False)
add.mesh(add.move(add.rotateX(sleeper, -add.pi / 2 + 0.1), [CORNERS[6][0] + 4.5, WALL_TOP + 0.6, CORNERS[6][2] + 2.0]))
flush("wall walk")


def horse(at, facing=0.0, color=None, saddle=True):
    """A horse standing still: body, neck, head, ears, mane, tail, four legs."""
    color = color or P["trunk"]
    add.push()
    add.capsule([-0.9, 1.35, 0], [0.9, 1.35, 0], 0.42, k_(12), color)
    add.capsule([0.8, 1.5, 0], [1.5, 2.3, 0], 0.22, k_(10), color)                       # neck
    add.mesh(add.move(add.stretch(add.make(add.sphere, [0, 0, 0], 0.24, k_(10), color), [1.9, 1.0, 0.9], (0, 0, 0)), [1.75, 2.35, 0]))
    add.sphere([2.15, 2.28, 0], 0.16, k_(8), color)                                        # muzzle
    for sz in (-0.1, 0.1):
        add.cone([1.5, 2.5, sz], [1.45, 2.8, sz * 1.5], 0.06, 5, color)
        add.sphere([2.0, 2.45, sz * 1.6], 0.035, 4, P["black"])
    for i in range(7):                                                                    # mane
        add.sphere([0.85 + i * 0.1, 1.85 + i * 0.1, 0], 0.1, 4, P["black"])
    add.polyline([[-1.2, 1.5, 0], [-1.45, 1.1, 0.05], [-1.5, 0.6, 0.0]], 0.06, 5, P["black"])   # tail
    for sx in (-0.65, 0.65):
        for sz in (-0.22, 0.22):
            add.capsule([sx, 1.2, sz], [sx, 0.15, sz], 0.11, k_(8), color)
            add.cylinder([sx, 0.15, sz], [sx, 0.0, sz], 0.12, k_(8), P["black"])
    if saddle:
        add.mesh(add.move(add.stretch(add.make(add.sphere, [0, 0, 0], 0.45, k_(10), P["red"]), [1.0, 0.5, 1.1], (0, 0, 0)), [0.1, 1.55, 0]))
        add.cuboid([0.1, 1.85, 0], [0.7, 0.2, 0.5], P["wood_dark"])
        add.torus([1.95, 2.3, 0], 0.2, 0.02, 8, 4, P["iron"], axis=(1, 0, 0))                # bridle
        add.polyline([[1.9, 2.2, 0.2], [0.6, 1.9, 0.25]], 0.015, 4, P["rope"])
        for sz in (-0.5, 0.5):
            add.polyline([[0.1, 1.75, sz], [0.1, 1.0, sz]], 0.02, 4, P["rope"])
            add.cuboid([0.1, 0.95, sz], [0.2, 0.05, 0.12], P["iron"])
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def rider(at, facing=0.0):
    """A knight in armour sitting on a horse, lance up."""
    add.push()
    horse([0, 0, 0], 0, P["wood_dark"])
    S, D = P["steel"], P["iron"]
    add.capsule([0.1, 2.05, 0], [0.1, 2.85, 0], 0.3, k_(10), S)
    add.sphere([0.1, 3.15, 0], 0.25, k_(10), S)
    add.cuboid([0.1, 3.1, 0.24], [0.34, 0.05, 0.08], P["black"])
    add.cone([0.1, 3.35, 0], [0.0, 3.7, 0], 0.05, 5, P["red"])
    for sz in (-1, 1):
        add.capsule([0.1, 2.0, sz * 0.25], [0.5, 1.4, sz * 0.5], 0.11, k_(8), S)
        add.cuboid([0.55, 1.3, sz * 0.5], [0.3, 0.15, 0.18], D)
        add.sphere([0.1, 2.75, sz * 0.4], 0.18, k_(8), D)
        add.capsule([0.15, 2.7, sz * 0.45], [0.6, 2.2, sz * 0.35], 0.09, k_(8), S)
    add.cylinder([0.6, 1.2, 0.35], [0.9, 5.0, 0.3], 0.04, 6, P["wood"])                       # the lance
    add.cone([0.9, 5.0, 0.3], [0.95, 5.5, 0.3], 0.06, 6, S)
    add.mesh(add.texture(add.make(add.cuboid, [0.62, 2.3, -0.7], [0.5, 0.7, 0.06], P["red"]), TEX["banner"], "fit"))
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def stable(at, facing=0.0):
    """An open stable with two stalls and horses, hay and a trough."""
    add.push()
    for sx in (-4.0, 0.0, 4.0):
        add.cuboid([sx, 1.6, 2.5], [0.25, 3.2, 0.25], P["wood_dark"])
        add.cuboid([sx, 2.0, -2.5], [0.25, 4.0, 0.25], P["wood_dark"])
    add.mesh(textured(add.make(add.cuboid, [0, 2.0, -2.6], [8.4, 4.0, 0.2], P["wood"]), "planks", "xy", scale=1.5))
    add.mesh(textured(add.make(add.cuboid, [-4.1, 1.6, 0], [0.2, 3.2, 5.2], P["wood"]), "planks", "yz", scale=1.5))
    add.cuboid([0, 0.9, 0], [0.12, 1.8, 5.0], P["wood_light"])                              # the partition
    roof = add.make(add.polygon, [[-4.5, 3.3, 3.0], [4.5, 3.3, 3.0], [4.5, 4.2, -2.9], [-4.5, 4.2, -2.9]], P["straw"])
    roof.extend(add.make(add.polygon, [[-4.5, 3.3, 3.0], [-4.5, 4.2, -2.9], [4.5, 4.2, -2.9], [4.5, 3.3, 3.0]], P["wood_dark"]))
    add.mesh(roof)
    add.cuboid([0, 4.25, -2.9], [9.2, 0.3, 0.3], P["straw"])
    for sx in (-2.0, 2.0):
        for i in range(3):
            add.cuboid([sx, 0.4 + i * 0.5, 2.5], [3.8, 0.15, 0.1], P["wood_light"])          # the half doors
    for i in range(20):
        add.sphere([add.uniform(-3.6, -0.4), 0.15, add.uniform(-2.2, 1.8)], add.uniform(0.2, 0.35), k_(6), P["straw"])
    add.cuboid([2.0, 0.3, -1.9], [2.6, 0.6, 0.7], P["wood_dark"])
    add.cuboid([2.0, 0.55, -1.9], [2.5, 0.05, 0.6], WATER)
    horse([-2.0, 0, 0.2], add.pi / 2 + 0.2, P["trunk"], saddle=False)
    horse([2.0, 0, 0.0], -add.pi / 2 - 0.3, P["sand"], saddle=False)
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def fence(a, b, h=1.1, rails=2, color=None):
    color = color or P["wood_dark"]
    L = vlen(vsub(b, a))
    n = max(1, int(L / 2.2))
    for i in range(n + 1):
        t = i / float(n)
        p = [a[k] + (b[k] - a[k]) * t for k in range(3)]
        add.cuboid([p[0], p[1] + h / 2, p[2]], [0.15, h, 0.15], color)
    for j in range(rails):
        y = h * (j + 1) / (rails + 1) + 0.1
        add.beam([a[0], a[1] + y, a[2]], [b[0], b[1] + y, b[2]], 0.1, 0.16, color)


def dovecote(at):
    add.cylinder(at, [at[0], at[1] + 3.6, at[2]], 0.7, k_(12), P["white"])
    add.cone([at[0], at[1] + 3.6, at[2]], [at[0], at[1] + 4.8, at[2]], 0.95, k_(12), P["slate"])
    for i in range(6):
        a = 2 * add.pi * i / 6
        add.cuboid([at[0] + 0.66 * add.cos(a), at[1] + 2.6 + (i % 2) * 0.6, at[2] + 0.66 * add.sin(a)], [0.2, 0.28, 0.2], P["black"])
        add.cuboid([at[0] + 0.72 * add.cos(a), at[1] + 2.42 + (i % 2) * 0.6, at[2] + 0.72 * add.sin(a)], [0.34, 0.05, 0.34], P["wood"])
    for i in range(4):
        a = 1.0 + i * 1.7
        add.mesh(add.move(add.stretch(add.make(add.sphere, [0, 0, 0], 0.1, 4, P["white"]), [1.6, 0.9, 1.0], (0, 0, 0)),
                          [at[0] + 0.8 * add.cos(a), at[1] + 2.55 + (i % 2) * 0.6, at[2] + 0.8 * add.sin(a)]))


def dog(at, facing=0.0):
    add.push()
    add.capsule([-0.35, 0.45, 0], [0.35, 0.45, 0], 0.17, k_(8), P["wood_light"])
    add.sphere([0.5, 0.65, 0], 0.15, k_(8), P["wood_light"])
    add.capsule([0.55, 0.6, 0], [0.75, 0.55, 0], 0.07, 6, P["wood_light"])
    add.sphere([0.8, 0.55, 0], 0.035, 4, P["black"])
    for sz in (-0.1, 0.1):
        add.mesh(add.make(add.prism, [[0, 0], [0.12, 0], [0.06, 0.2]], 0.03, P["wood_dark"], (0.45, 0.75, sz), (0, 0, 1)))
    for sx in (-0.3, 0.3):
        for sz in (-0.1, 0.1):
            add.cylinder([sx, 0.4, sz], [sx, 0.0, sz], 0.05, 5, P["wood_light"])
    add.polyline([[-0.5, 0.5, 0], [-0.7, 0.75, 0.05]], 0.04, 4, P["wood_light"])
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def laundry(a, b):
    """A washing line with clothes on it."""
    for p in (a, b):
        add.cylinder(p, [p[0], p[1] + 2.4, p[2]], 0.06, 6, P["wood_dark"])
    add.polyline([[a[0], a[1] + 2.3, a[2]], [(a[0] + b[0]) / 2, a[1] + 2.15, (a[2] + b[2]) / 2], [b[0], b[1] + 2.3, b[2]]], 0.015, 4, P["rope"], smooth=1)
    L = vlen(vsub(b, a))
    for i in range(int(L / 1.1)):
        t = (i + 0.5) / int(L / 1.1)
        p = [a[k] + (b[k] - a[k]) * t for k in range(3)]
        d = vunit(vsub(b, a))
        cloth = add.make(add.cuboid, [0, 0, 0], [0.8, 1.0 + 0.3 * (i % 2), 0.04],
                         [P["white"], P["blue"], P["red"], P["cheese"], P["leaf"]][i % 5])
        add.mesh(add.move(add.rotateY(cloth, -add.atan2(d[2], d[0])), [p[0], p[1] + 2.15 - 0.5 - 0.15 * (i % 2) - 0.05 * add.sin(t * 6), p[2]]))


def tilt(a, b):
    """The barrier of the jousting lists, with pennants."""
    fence(a, b, 1.3, 1, P["white"])
    L = vlen(vsub(b, a))
    for i in range(int(L / 2.2) + 1):
        t = i / float(int(L / 2.2))
        p = [a[k] + (b[k] - a[k]) * t for k in range(3)]
        add.cylinder([p[0], p[1] + 1.3, p[2]], [p[0], p[1] + 2.3, p[2]], 0.03, 4, P["wood_dark"])
        add.mesh(add.make(add.prism, [[0, 0], [0.7, -0.15], [0, -0.3]], 0.02, P["red"] if i % 2 else P["blue"], (p[0], p[1] + 2.3, p[2]), (0, 0, 1)))


def ladder(at, h=9.0, lean=0.35, facing=0.0):
    add.push()
    for sx in (-0.35, 0.35):
        add.beam([sx, 0, 0], [sx, h * add.cos(lean), -h * add.sin(lean)], 0.08, 0.08, P["wood"])
    for i in range(1, int(h / 0.45)):
        t = i * 0.45 / h
        add.cylinder([-0.35, h * add.cos(lean) * t, -h * add.sin(lean) * t], [0.35, h * add.cos(lean) * t, -h * add.sin(lean) * t], 0.035, 5, P["wood"])
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


stable([10, G, -40], 0)
fence([2, G, -36], [2, G, -44])
fence([18, G, -36], [18, G, -44])
horse([14, G, -38], 0.5, P["wood_light"], saddle=False)
dovecote([-6, G, -40])
rider([-6, G, 36], 0.9)
tilt([2, G, 30], [16, G, 30])
add.mesh(add.move(add.make(add.cuboid, [0, 0.7, 0], [0.4, 1.4, 0.4], P["stone_dark"]), [-2, G, 38]))     # a mounting block
laundry([-40, G, 14], [-38, G, 22])
dog([9, G, 20], 2.5)
dog([-20, G, 26], -1.0)
ladder([-42, G, 4], 8.5, 0.28, add.pi / 2 - 0.2)
ladder([40, G, 4], 8.5, 0.28, -add.pi / 2 + 0.2)
add.seed(31)
for i in range(6):                                                              # birds over the lake and the yard
    a = i * 1.1
    p = [70 * add.cos(a), 26 + 4 * add.sin(i * 2.1), 70 * add.sin(a)]
    bird = add.stretch(add.make(add.sphere, [0, 0, 0], 0.25, k_(8), P["white"]), [2.0, 0.6, 0.8], (0, 0, 0))
    for sz in (-1, 1):
        bird.extend(add.make(add.prism, [[0, 0], [0.3, sz * 1.4], [-0.3, sz * 1.4]], 0.04, P["white"], (0, 0.05, 0), (0, 1, 0)))
    add.mesh(add.move(add.rotateY(bird, a + add.pi / 2), p))
flush("stable, lists and animals")


# --------------------------------------------------------------------------
#  Done: close the file (this writes the .mtl) and report
# --------------------------------------------------------------------------
out.close()
print("\n%s: %d faces, %d vertices, %.1f MB, %d materials, %.0f s" % (
    OUT, out.faces, out.vertices, out.bytes / 1e6, len(out.materials), time.time() - started))
if DETAIL == 1:
    ok = out.bytes <= add.SKETCHFAB_MB * 1e6 and len(out.materials) <= add.SKETCHFAB_COLORS
    print("Sketchfab limits (%d MB, %d materials): %s" % (add.SKETCHFAB_MB, add.SKETCHFAB_COLORS, "OK" if ok else "EXCEEDED"))
    print("Zip castle.obj, castle.mtl and the castle_*.png textures together for the upload.")

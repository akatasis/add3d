"""
22 -- a lighthouse on a rocky island.

A complete scene the way a course project is built: a landscape from a
height function, a striped tower from a lathe with a *colour function*, a
keeper's house from ready-made parts (``bricks``, ``roof``, ``arch``,
``stairs``), palms and rocks scattered with ``random_points`` /
``scatter``, a fence strung ``along`` a path, a rowing boat lofted from
cross-sections and a date written with ``text``.

Parameters: ``BANDS`` (stripes on the tower) and ``SEED`` (the island).
"""
import add

BANDS = 7
SEED = 7
rng = add.Random(SEED)

SEA = [40, 110, 170]
SAND = [214, 190, 140]
GRASS = [86, 150, 70]
ROCK = [120, 112, 105]
WALL = [235, 230, 220]
RED = [200, 40, 40]


# --------------------------------------------------------------------------
#  the island: a height field, coloured by height
# --------------------------------------------------------------------------
def island(x, z):
    """Height of the island at (x, z): a bump with a rocky, noisy rim."""
    d = add.sqrt(x * x + z * z)
    ridge = 0.25 * add.sin(3.0 * add.atan2(z, x)) * add.exp(-((d - 9) / 3.0) ** 2)
    return 4.0 * add.exp(-(d / 8.5) ** 2) + ridge - 0.8


def ground_color(x, z):
    h = island(x, z)
    if h < 0.05:
        return SAND
    t = add.clamp(add.remap(h, 0.05, 2.0, 0.0, 1.0))
    return add.lerp(SAND, GRASS, t) if h < 1.6 else add.lerp(GRASS, ROCK, t)


add.grid([0, 0, 0], [40, 40], 90, 90, ground_color, island, thickness=0.3)

# the sea: a flat sheet, rippled with ``deform`` and shaded darker far away.
# push()/pop() keep the island out of the sheet (a bare layer() would take
# everything drawn so far).
add.push()
add.grid([0, 0, 0], [46, 46], 46, 46, SEA)
sea = add.deform(add.pop(), lambda p: [p[0], 0.08 * add.sin(1.3 * p[0] + p[2])
                                        + 0.05 * add.cos(2.1 * p[2]), p[2]])
add.mesh(add.color_gradient(sea, add.shade(SEA, 0.55), SEA, axis=2))


# --------------------------------------------------------------------------
#  the lighthouse: a lathe with red and white bands, gallery, lantern, dome
# --------------------------------------------------------------------------
TOP = island(0, 0)
H = 9.0


def tower_profile(t):
    return [1.6 - 0.9 * t, t * H]          # radius narrows as it rises


def bands(t, a):
    return RED if int(t * BANDS) % 2 == 0 else WALL


add.revolve(tower_profile, [0, TOP - 0.2, 0], [0, TOP + 1, 0], 0, 1, 80, 48, bands)

# the gallery: a disc, a railing of posts and two rails running around it.
# The post is built between push() and pop() so that layer()-style capture
# cannot swallow the island drawn above.
add.cylinder([0, TOP + H, 0], [0, TOP + H + 0.25, 0], 1.25, 48, add.shade(WALL, 0.8))
add.push()
add.cylinder([1.15, TOP + H + 0.25, 0], [1.15, TOP + H + 1.0, 0], 0.04, 8, "black")
post = add.pop()
add.mesh(add.array_radial(post, 16))
add.torus([0, TOP + H + 1.0, 0], 1.15, 0.035, 48, 8, "black")
add.torus([0, TOP + H + 0.6, 0], 1.15, 0.025, 48, 8, "black")

# the lantern room and its dome
add.tube([0, TOP + H + 0.25, 0], [0, TOP + H + 1.6, 0], 0.75, 24, [150, 220, 255])
add.cylinder([0, TOP + H + 0.5, 0], [0, TOP + H + 1.3, 0], 0.3, 16, "gold")   # the lamp
add.cylinder([0, TOP + H + 1.6, 0], [0, TOP + H + 1.75, 0], 0.9, 24, RED)
add.hemisphere([0, TOP + H + 1.75, 0], 0.9, 12, RED)
add.sphere([0, TOP + H + 2.75, 0], 0.12, 4, "gold")

# a door at the foot and a short flight of steps up to it
add.arch([-0.6, TOP, 1.5], [0.6, TOP, 1.5], 0.7, [0.25, 0.2], "brown")
add.cuboid([0, TOP + 0.6, 1.5], [1.2, 1.2, 0.2], "brown")
add.stairs([0, TOP - 0.5, 3.4], 3, 1.4, 0.16, 0.5, ROCK, direction=[0, 0, -1])


# --------------------------------------------------------------------------
#  the keeper's house: walls of bricks, a roof, a chimney, an arched door
# --------------------------------------------------------------------------
def house():
    add.push()
    add.cuboid([0, 1.1, 0], [4.0, 2.2, 3.0], WALL)
    add.bricks([-2.0, 0, 1.5], 4.0, 0.9, [0.6, 0.3, 0.12], "brown", seed=SEED)
    add.roof([0, 2.2, 0], [4.0, 3.0], 1.4, RED, overhang=0.3)
    add.cuboid([1.2, 3.1, 0], [0.5, 1.4, 0.5], add.shade(RED, 0.6))       # chimney
    add.arch([-0.45, 0, 1.55], [0.45, 0, 1.55], 1.0, [0.16, 0.15], "brown")
    add.cuboid([0, 0.75, 1.55], [0.9, 1.5, 0.1], [90, 60, 30])
    for x in (-1.3, 1.3):                                                  # windows
        add.cuboid([x, 1.3, 1.55], [0.7, 0.7, 0.1], [150, 220, 255])
    return add.pop()


site = [5.0, island(5.0, 3.0), 3.0]
add.mesh(add.align(add.rotateY(house(), 0.5), site))

# a fence of posts along a curved path from the house to the lighthouse
add.push()
add.cylinder([0, 0, 0], [0, 0.6, 0], 0.05, 6, "brown")
add.sphere([0, 0.62, 0], 0.07, 3, "brown")
fence_post = add.pop()
path = add.chaikin([[4.5, 0, 6], [2, 0, 7], [-1, 0, 5], [-2.5, 0, 2]], 2)
path = [[p[0], island(p[0], p[2]), p[2]] for p in path]
add.mesh(add.along(fence_post, path, len(path), axis=None))
add.polyline([[p[0], p[1] + 0.55, p[2]] for p in path], 0.02, 6, "brown")


# --------------------------------------------------------------------------
#  nature: palms and rocks scattered over the island
# --------------------------------------------------------------------------
spots = [p for p in add.random_points(60, [-12, 0, -12], [12, 0, 12], SEED, island)
         if 0.05 < p[1] < 1.4 and add.distance(p, [0, p[1], 0]) > 3.5
         and add.distance(p, site) > 3.0]
for i, p in enumerate(spots[:8]):
    add.tree(p, rng.uniform(2.0, 3.2), "brown", "green", kind="palm", seed=i)

add.push()
add.sphere([0, 0, 0], 0.5, 5, ROCK)
rock = add.jitter(add.stretch(add.pop(), [1.3, 0.7, 1.0]), 0.08, seed=SEED)
rocks = add.random_points(70, [-13, 0, -13], [13, 0, 13], SEED + 1, island)
rocks = [p for p in rocks if -0.6 < p[1] < 0.3 and add.distance(p, site) > 3.0]
add.mesh(add.scatter(rock, rocks, seed=SEED, scale=(0.5, 1.6)))


# --------------------------------------------------------------------------
#  a rowing boat: cross-sections lofted into a hull, and a rope to a post
# --------------------------------------------------------------------------
def boat():
    add.push()
    sections = []
    for i in range(9):
        t = i / 8.0
        w = 0.55 * add.sin(add.pi * t) ** 0.5 + 0.02       # beam of the boat
        y = 0.25 - 0.4 * add.sin(add.pi * t)               # keel depth
        x = -1.4 + 2.8 * t
        ring = [[x, 0.4, -w], [x, y + 0.15, -w * 0.7], [x, y, 0], [x, y + 0.15, w], [x, 0.4, w]]
        sections.append(ring)
    add.loft(sections, [150, 90, 50])
    hull = add.solidify(add.layer(), 0.06)
    add.mesh(hull)
    for x in (-0.6, 0.3):                                   # thwarts (seats)
        add.cuboid([x, 0.32, 0], [0.18, 0.05, 0.9], [200, 160, 100])
    return add.pop()


B = add.rotateY(add.zoom(boat(), 1.4, (0, 0, 0)), 0.9)
B = add.move(B, [-6.5, -0.05, 9.5])
add.mesh(B)
add.polyline([[-6.0, 0.35, 8.6], [-5.0, 0.6, 8.0], [-4.3, island(-4.3, 7.4) + 0.5, 7.4]],
             0.03, 6, [230, 220, 190])
add.cylinder([-4.3, island(-4.3, 7.4), 7.4], [-4.3, island(-4.3, 7.4) + 0.6, 7.4],
             0.06, 6, "brown")

# a plaque with the year, standing on the grass
add.cuboid([2.6, island(2.6, 2) + 0.4, 2.0], [1.7, 0.8, 0.12], ROCK)
add.text("1863", [1.9, island(2.6, 2) + 0.2, 2.07], 0.4, color="gold", k=6)

add.check()
add.save("lighthouse.off")

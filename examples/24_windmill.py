"""
24 -- a windmill on a hill.

The tower is an octagon pulled up with ``extrude`` (tapering as it rises),
the cap is a lathe, and the four sails are *one* sail copied around the
shaft with ``array_radial`` -- so ``SAIL_ANGLE`` turns all of them at once.
The hill is a ``grid`` with a height function; trees, bushes and tulips
are scattered on it with ``random_points`` (which reads the same height
function, so everything stands on the ground).

Parameters: ``SAIL_ANGLE``, ``SEED``.
"""
import add

SAIL_ANGLE = 0.35
SEED = 5
rng = add.Random(SEED)

BRICK = [150, 75, 50]
WOOD = [110, 75, 45]
CLOTH = [240, 235, 220]
THATCH = [170, 140, 80]
GRASS = [96, 160, 72]


# --------------------------------------------------------------------------
#  the hill
# --------------------------------------------------------------------------
def hill(x, z):
    return 2.2 * add.exp(-((x * x + z * z) / 60.0)) + 0.25 * add.sin(0.8 * x) * add.cos(0.7 * z)


def meadow(x, z):
    t = add.clamp(add.remap(hill(x, z), 0.0, 2.2, 0.0, 1.0))
    return add.lerp(add.shade(GRASS, 0.75), GRASS, t)


add.grid([0, 0, 0], [36, 36], 72, 72, meadow, hill, thickness=0.4)
TOP = hill(0, 0)


# --------------------------------------------------------------------------
#  the mill: brick base, tapering octagonal tower, cap, door, windows
# --------------------------------------------------------------------------
H = 7.0
add.extrude(add.profile_polygon(8, 2.6), [0, H, 0], BRICK, steps=1,
            scale=lambda t: 1.0 - 0.3 * t, center=(0, TOP - 0.3, 0))
# the brick courses are painted on as thin rings
for i in range(14):
    y = TOP + 0.5 * i
    add.pipe([0, y, 0], [0, y + 0.04, 0], 2.62 - 0.78 * i / 14.0, 2.5 - 0.78 * i / 14.0,
             8, add.shade(BRICK, 0.7))
add.cylinder([0, TOP + H - 0.35, 0], [0, TOP + H + 0.2, 0], 1.95, 8, WOOD)     # the stage


def cap(t):
    """Profile of the cap: a rounded, slightly pointed roof."""
    return [2.0 * add.cos(t) ** 0.7 if t < add.pi / 2 else 0.0, TOP + H + 0.2 + 2.2 * add.sin(t)]


add.revolve(cap, [0, 0, 0], [0, 1, 0], 0, add.pi / 2, 24, 32, THATCH)

add.arch([-0.55, TOP, 2.3], [0.55, TOP, 2.3], 0.6, [0.2, 0.25], WOOD)         # the door
add.cuboid([0, TOP + 0.65, 2.32], [1.1, 1.3, 0.12], add.shade(WOOD, 0.6))
add.stairs([0, TOP - 0.45, 3.6], 3, 1.6, 0.15, 0.45, [130, 130, 125], [0, 0, -1])
for i in range(3):                                                             # windows
    y = TOP + 2.0 + 1.6 * i
    r = 2.6 - 0.3 * 2.6 * (y - TOP) / H
    for a in (0.0, add.pi / 2, add.pi):
        c = [r * add.sin(a), y, r * add.cos(a)]
        add.push()
        add.cuboid([0, 0, 0], [0.7, 0.9, 0.2], [180, 220, 240])
        add.cuboid([0, 0, 0.02], [0.8, 1.0, 0.16], WOOD)
        win = add.pop()
        add.mesh(add.move(add.rotateY(win, a), c))


# --------------------------------------------------------------------------
#  the sails: one sail, copied four times around the shaft
# --------------------------------------------------------------------------
HUB = [0, TOP + H + 1.1, 2.2]
add.cylinder([0, HUB[1], 0.4], [0, HUB[1], 2.6], 0.22, 12, WOOD)             # the shaft
add.sphere(HUB, 0.42, 6, WOOD)

add.push()
add.beam(HUB, [0, HUB[1] + 5.2, HUB[2]], 0.16, 0.2, WOOD)                    # the spar
for i in range(9):                                                            # lattice bars
    y = HUB[1] + 1.2 + 0.45 * i
    add.beam([-0.9, y, HUB[2] + 0.05], [0.25, y, HUB[2] + 0.05], 0.06, 0.06, WOOD)
add.beam([-0.9, HUB[1] + 1.2, HUB[2] + 0.05], [-0.9, HUB[1] + 4.8, HUB[2] + 0.05],
         0.06, 0.06, WOOD)
add.cuboid([-0.35, HUB[1] + 3.0, HUB[2] + 0.12], [1.05, 3.6, 0.03], CLOTH)   # the cloth
sail = add.pop()
sails = add.array_radial(sail, 4, [0, 0, 1], HUB)
add.mesh(add.rotate(sails, [0, 0, 1], SAIL_ANGLE, HUB))


# --------------------------------------------------------------------------
#  the garden: a fence, trees, bushes and rows of tulips
# --------------------------------------------------------------------------
add.push()
add.cylinder([0, 0, 0], [0, 0.7, 0], 0.05, 6, WOOD)
post = add.pop()
ring = add.points_on_circle([0, 0, 0], 7.5, 40)
ring = [[p[0], hill(p[0], p[2]), p[2]] for p in ring]
add.mesh(add.along(post, ring, len(ring), axis=None, closed=True))
add.polyline([[p[0], p[1] + 0.62, p[2]] for p in ring], 0.025, 6, WOOD, closed=True)
add.polyline([[p[0], p[1] + 0.35, p[2]] for p in ring], 0.025, 6, WOOD, closed=True)

for i, p in enumerate(add.random_points(14, [-16, 0, -16], [16, 0, 16], SEED, hill)):
    if add.distance([p[0], 0, p[2]], [0, 0, 0]) > 9:
        add.tree(p, rng.uniform(2.2, 3.4), WOOD, add.shade(GRASS, rng.uniform(0.6, 0.9)),
                 kind="round" if i % 3 else "pine", seed=i)

add.push()
add.sphere([0, 0.3, 0], 0.35, 4, add.shade(GRASS, 0.55))
bush = add.pop()
bushes = [p for p in add.random_points(30, [-9, 0, -9], [9, 0, 9], SEED + 1, hill)
          if 3.3 < add.distance([p[0], 0, p[2]], [0, 0, 0]) < 7]
add.mesh(add.scatter(bush, bushes, seed=SEED, scale=(0.6, 1.5)))

add.push()                                                                    # one tulip
add.cylinder([0, 0, 0], [0, 0.35, 0], 0.015, 5, "green")
add.sphere([0, 0.42, 0], 0.07, 3, "red")
tulip = add.stretch(add.pop(), [1, 1.3, 1], (0, 0, 0))
for row in range(5):                                                          # rows in a field
    x0 = 9.5 + row * 0.7
    line = [[x0, hill(x0, z), z] for z in [-6 + 0.5 * k for k in range(25)]]
    field = add.along(tulip, line, len(line), axis=None)
    add.mesh(add.color_by(field, lambda p: add.hsv(0.0 if p[1] < hill(p[0], p[2]) + 0.4
                                                   else 0.02 + 0.045 * row, 0.9, 1.0)
                          if p[1] > hill(p[0], p[2]) + 0.38 else "green"))

add.text("MALŪNAS", [-2.6, TOP + 0.35, 2.75], 0.5, color=CLOTH, k=6)

add.check()
add.save("windmill.off")

"""
23 -- a steam locomotive with its tender.

Machines are assemblies: every part is built around its own origin, then
placed.  ``wheel`` makes the spoked drivers, ``beam`` the rails and rods,
``rotate_point`` works out where the crank pins are for a given wheel
angle, so the connecting rods always fit, and ``array_mirror`` gives the
far side of the engine for free.  The coal in the tender is a
``heightmap``; the smoke is a sphere strung ``along`` a curve with a
growing ``scale``.

Parameters: ``ANGLE`` turns the wheels (and the rods follow), ``SEED``
shapes the coal and the smoke.
"""
import add

ANGLE = 0.8                     # rotation of the driving wheels (radians)
SEED = 11
rng = add.Random(SEED)

BLACK = [30, 30, 34]
IRON = [70, 72, 78]
RED = [150, 30, 30]
BRASS = [200, 160, 60]
GREEN = [30, 90, 60]

RAIL_TOP = 0.2
R = 0.85                        # driver radius
AXLE = RAIL_TOP + R             # height of the driving axles
Z = 0.82                        # the wheels sit just outside the rails


# --------------------------------------------------------------------------
#  track and ground
# --------------------------------------------------------------------------
add.grid([0, -0.35, 0], [24, 14], 48, 28, GREEN,
         height=lambda x, z: 0.08 * add.sin(1.7 * x) * add.cos(2.3 * z))
add.cuboid([0, -0.1, 0], [22, 0.3, 3.2], [140, 130, 115])                 # ballast
add.push()
add.cuboid([0, 0.08, 0], [0.25, 0.14, 2.4], [110, 80, 50])
sleeper = add.pop()
add.mesh(add.array_linear(add.move(sleeper, [-10.5, 0, 0]), [0.6, 0, 0], 36))
for z in (-0.7, 0.7):
    add.beam([-11, RAIL_TOP - 0.05, z], [11, RAIL_TOP - 0.05, z], 0.1, 0.1, "silver")


# --------------------------------------------------------------------------
#  wheels, crank pins and rods (one side; mirrored later)
# --------------------------------------------------------------------------
add.push()
drivers = [-1.6, 0.0, 1.6]
pins = []
for x in drivers:
    add.wheel([x, AXLE, Z], R, 0.16, IRON, axis=[0, 0, 1], spokes=12, hub_color=RED)
    # the crank pin: a point on the wheel, turned by ANGLE about the axle
    pin = add.rotate_point([x + 0.5, AXLE, Z + 0.15], [0, 0, 1], ANGLE, [x, AXLE, Z])
    add.cylinder([pin[0], pin[1], Z + 0.02], [pin[0], pin[1], Z + 0.25], 0.06, 10, BRASS)
    pins.append(pin)
add.beam(pins[0], pins[-1], 0.08, 0.14, "silver")                          # coupling rod
piston = [3.0, AXLE + 0.05, Z + 0.15]
add.beam(pins[-1], piston, 0.08, 0.12, "silver")                           # main rod
add.cylinder([2.6, AXLE + 0.05, Z + 0.15], [3.4, AXLE + 0.05, Z + 0.15], 0.28, 16, BLACK)
for x in (2.9, 3.5):                                                       # leading wheels
    add.wheel([x, RAIL_TOP + 0.38, Z], 0.38, 0.14, IRON, axis=[0, 0, 1], spokes=8)
side = add.pop()
add.mesh(add.array_mirror(side, [0, 0, 0], [0, 0, 1]))
for x in drivers:
    add.cylinder([x, AXLE, -Z], [x, AXLE, Z], 0.08, 10, IRON)              # axles


# --------------------------------------------------------------------------
#  boiler, smokebox, chimney, domes, cab
# --------------------------------------------------------------------------
BY = AXLE + 0.95                                                           # boiler axis
add.cylinder([-1.2, BY, 0], [3.1, BY, 0], 0.9, 40, BLACK)
for x in (-0.2, 1.0, 2.2):                                                 # boiler bands
    add.torus([x, BY, 0], 0.9, 0.035, 40, 8, BRASS)
add.hemisphere([3.1, BY, 0], 0.9, 12, IRON, axis=[1, 0, 0])               # smokebox door
add.cylinder([3.35, BY, 0], [3.55, BY, 0], 0.22, 16, BRASS)                # headlamp
add.sphere([3.58, BY, 0], 0.16, 4, "gold")
add.frustum([2.4, BY + 0.6, 0], [2.4, BY + 1.5, 0], 0.22, 0.34, 20, BLACK)  # chimney
add.pipe([2.4, BY + 1.5, 0], [2.4, BY + 1.75, 0], 0.36, 0.26, 20, BLACK)
add.hemisphere([0.8, BY + 0.55, 0], 0.42, 10, BRASS)                       # steam dome
add.cylinder([0.8, BY + 0.55, 0], [0.8, BY + 0.85, 0], 0.42, 20, BRASS)
add.hemisphere([0.8, BY + 0.85, 0], 0.42, 10, BRASS)
add.hemisphere([-0.3, BY + 0.6, 0], 0.3, 10, BLACK)                        # sand dome
add.cuboid([1.0, AXLE + 0.05, 0], [5.0, 0.3, 1.9], RED)                    # running board

# the cab: a rounded box with windows and a roof that sticks out
add.rounded_box([-2.2, BY + 0.2, 0], [2.0, 2.2, 2.3], 0.12, 5, RED)
for z in (-1.16, 1.16):
    add.cuboid([-2.0, BY + 0.6, z], [0.9, 0.7, 0.05], [170, 220, 240])
    add.cuboid([-2.75, BY + 0.6, z], [0.35, 0.7, 0.05], [170, 220, 240])
add.rounded_box([-2.2, BY + 1.42, 0], [2.4, 0.16, 2.7], 0.07, 4, BLACK)
add.cuboid([-2.2, AXLE - 0.1, 0], [2.0, 0.4, 2.0], IRON)                   # cab floor
add.stairs([-3.1, RAIL_TOP + 0.05, 1.2], 2, 0.5, 0.35, 0.3, IRON, direction=[0, 0, -1])

# a cowcatcher: bars fanning out from the buffer beam
for i, p in enumerate(add.points_on_line([3.6, RAIL_TOP + 0.05, -0.9],
                                         [3.6, RAIL_TOP + 0.05, 0.9], 9)):
    add.beam(p, [4.4 - 0.25 * abs(i - 4), AXLE + 0.35, p[2] * 0.75], 0.05, 0.05, RED)
add.cuboid([3.55, AXLE + 0.35, 0], [0.15, 0.3, 2.0], RED)                  # buffer beam


# --------------------------------------------------------------------------
#  the tender: a box on small wheels, heaped with coal
# --------------------------------------------------------------------------
TX = -5.4                                                                  # tender centre
add.cuboid([TX, AXLE + 0.55, 0], [3.6, 1.6, 2.2], RED)
add.cuboid([TX, AXLE - 0.25, 0], [3.2, 0.3, 1.9], IRON)
for x in (TX - 1.2, TX - 0.4, TX + 0.4, TX + 1.2):
    add.cylinder([x, RAIL_TOP + 0.4, -Z], [x, RAIL_TOP + 0.4, Z], 0.06, 8, IRON)
    for z in (-Z, Z):
        add.wheel([x, RAIL_TOP + 0.4, z], 0.4, 0.14, IRON, axis=[0, 0, 1], spokes=8)
add.beam([TX + 1.8, AXLE + 0.1, 0], [-3.2, AXLE + 0.1, 0], 0.3, 0.12, IRON)  # coupling
coal = [[int(add.clamp(rng.gauss(2.5, 1.2), 1, 4)) for j in range(9)] for i in range(14)]
add.heightmap(coal, 0.22, [TX - 1.55, AXLE + 1.05, -1.0],
              color=lambda i, j, k: add.shade(BLACK, rng.uniform(0.6, 1.6)))
add.text("ADD 2.1", [TX - 1.2, AXLE + 0.5, 1.12], 0.45, color=BRASS, k=6)
add.text("ADD 2.1", [TX + 1.2, AXLE + 0.5, -1.12], 0.45, color=BRASS, k=6,
         u=[-1, 0, 0])


# --------------------------------------------------------------------------
#  smoke: one sphere placed along a curve, growing and fading as it rises
# --------------------------------------------------------------------------
def plume(t):
    return [2.4 - 4.5 * t * t + 0.3 * add.sin(9 * t),
            BY + 1.9 + 4.0 * t,
            0.5 * add.sin(5 * t) * t]


add.push()
add.sphere([0, 0, 0], 0.32, 5, "white")
puff = add.jitter(add.pop(), 0.05, seed=SEED)
smoke = add.along(puff, plume, 14, 0, 1, axis=None, scale=lambda t: 0.6 + 2.6 * t)
add.mesh(add.color_gradient(smoke, [90, 90, 95], [235, 235, 240], axis=1))

lo, hi = add.bbox()
print("the train is %.1f long, %.1f high" % (hi[0] - lo[0], hi[1] - lo[1]))
add.check()
add.save("locomotive.off")

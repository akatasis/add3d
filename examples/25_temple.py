"""
25 -- a round temple (a *tholos*).

Architecture is repetition: ``COLUMNS`` columns stand on the points that
``points_on_circle`` gives, the entablature is a ``pipe``, the dome a
``hemisphere``, the triglyphs one block copied round with ``array_radial``.
The floor is a ``parametric`` disc whose *colour function* draws the
chequerboard, the statue a lathe painted by a colour function; the porch in front is built face by face with ``polygon``,
``triangle`` and ``quad`` to show that nothing stops you from placing
single faces by hand.

Parameters: ``COLUMNS``, ``RADIUS``.
"""
import add

COLUMNS = 14
RADIUS = 6.0
MARBLE = [235, 228, 215]
DARK = [90, 80, 75]
GOLD = [212, 175, 55]
GRASS = [110, 160, 85]
STONE = [160, 150, 140]

add.grid([0, -0.2, 0], [50, 50], 40, 40, GRASS, thickness=0.4)


# --------------------------------------------------------------------------
#  the stepped base: five discs, each a little smaller than the one below
# --------------------------------------------------------------------------
for i in range(5):
    add.cylinder([0, 0.32 * i, 0], [0, 0.32 * (i + 1), 0], RADIUS + 3.4 - 0.6 * i, 72, MARBLE)
FLOOR = 0.32 * 5

# the floor: a disc drawn as a parametric surface with a chequered colour
add.parametric(lambda u, v: [u * add.cos(v), FLOOR + 0.02, u * add.sin(v)],
               0.01, RADIUS + 0.5, 12, 0, 2 * add.pi, 48, wrap_v=True, flip=True,
               color=lambda u, v: DARK if (int(u / 0.55) + int(v / (2 * add.pi / 48))) % 2 else MARBLE)


# --------------------------------------------------------------------------
#  columns, entablature, dome
# --------------------------------------------------------------------------
H = 6.0
for p in add.points_on_circle([0, FLOOR, 0], RADIUS, COLUMNS):
    add.column(p, H, 0.42, MARBLE, 20)
add.pipe([0, FLOOR + H, 0], [0, FLOOR + H + 0.7, 0], RADIUS + 0.9, RADIUS - 0.9, 72, MARBLE)
add.torus([0, FLOOR + H + 0.72, 0], RADIUS + 0.3, 0.12, 72, 10, GOLD)
add.pipe([0, FLOOR + H + 0.7, 0], [0, FLOOR + H + 1.4, 0], RADIUS + 0.6, RADIUS - 0.6, 72, MARBLE)
# triglyphs: little blocks with grooves, repeated around the frieze
add.push()
add.cuboid([RADIUS + 0.65, FLOOR + H + 1.05, 0], [0.12, 0.55, 0.5], DARK)
add.mesh(add.array_radial(add.pop(), COLUMNS * 2))

add.hemisphere([0, FLOOR + H + 1.4, 0], RADIUS + 0.3, 20, [180, 90, 70])
add.cylinder([0, FLOOR + H + 1.4 + RADIUS + 0.2, 0], [0, FLOOR + H + 1.4 + RADIUS + 1.1, 0],
             0.7, 16, MARBLE)
add.cone([0, FLOOR + H + 1.4 + RADIUS + 1.1, 0], [0, FLOOR + H + 1.4 + RADIUS + 2.2, 0],
         0.9, 16, GOLD)

# inside: an altar and a statue (a lathe with a colour that fades upwards)
add.rounded_box([0, FLOOR + 0.55, 0], [2.0, 1.1, 1.2], 0.12, 5, DARK)
add.revolve(lambda t: [0.45 + 0.25 * add.sin(2.2 * t) * (1 - t) + 0.2 * (t > 0.85), t * 2.4],
            [0, FLOOR + 1.1, 0], [0, FLOOR + 2.1, 0], 0, 1, 40, 32,
            color=lambda t, a: add.gradient(t, GOLD, MARBLE))
add.sphere([0, FLOOR + 3.85, 0], 0.4, 8, GOLD)


# --------------------------------------------------------------------------
#  the porch: a pediment built face by face
# --------------------------------------------------------------------------
Z0 = RADIUS + 3.4                                # front edge of the bottom step
for x in (-2.0, 2.0):
    add.column([x, FLOOR - 0.32, Z0 + 1.2], H - 0.5, 0.36, MARBLE, 16)
y0, y1 = FLOOR - 0.32 + H - 0.5, FLOOR - 0.32 + H + 0.2
z0, z1 = Z0 + 0.4, Z0 + 2.0
add.quad([-2.8, y0, z1], [2.8, y0, z1], [2.8, y1, z1], [-2.8, y1, z1], MARBLE)   # architrave front
add.quad([-2.8, y1, z1], [2.8, y1, z1], [2.8, y1, z0], [-2.8, y1, z0], MARBLE)   # its top
add.quad([2.8, y0, z1], [2.8, y0, z0], [2.8, y1, z0], [2.8, y1, z1], MARBLE)     # right end
add.quad([-2.8, y0, z0], [-2.8, y0, z1], [-2.8, y1, z1], [-2.8, y1, z0], MARBLE)  # left end
add.quad([-2.8, y0, z0], [-2.8, y1, z0], [2.8, y1, z0], [2.8, y0, z0], MARBLE)   # back
add.quad([-2.8, y0, z0], [2.8, y0, z0], [2.8, y0, z1], [-2.8, y0, z1], MARBLE)   # underside
add.triangle([-2.8, y1, z1], [2.8, y1, z1], [0, y1 + 1.6, z1], [200, 190, 170])  # the gable
add.triangle([2.8, y1, z0], [-2.8, y1, z0], [0, y1 + 1.6, z0], [200, 190, 170])
add.polygon([[-2.8, y1, z1], [0, y1 + 1.6, z1], [0, y1 + 1.6, z0], [-2.8, y1, z0]], STONE)
add.polygon([[2.8, y1, z0], [0, y1 + 1.6, z0], [0, y1 + 1.6, z1], [2.8, y1, z1]], STONE)
add.text("MMXXVI", [-1.6, y0 + 0.15, z1 + 0.02], 0.4, color=GOLD, k=6)

# a paved path curving away from the porch, one flagstone placed along it
add.push()
add.cuboid([0, 0.05, 0], [0.9, 0.1, 0.6], STONE)
flag = add.pop()
path = add.chaikin([[0, 0, Z0 + 2.5], [1, 0, Z0 + 6], [-3, 0, Z0 + 10], [-2, 0, Z0 + 14]], 3)
add.mesh(add.along(flag, path, len(path), axis=[0, 0, 1]))

# a ring of tall cypresses: pine trees stretched upwards
add.push()
add.tree([0, 0, 0], 3.0, [80, 55, 35], [40, 90, 50], kind="pine")
cypress = add.stretch(add.pop(), [0.55, 2.2, 0.55], (0, 0, 0))
add.mesh(add.scatter(cypress, add.points_on_circle([0, 0, 0], RADIUS + 9, 18, phase=0.1),
                     seed=1, scale=(0.8, 1.2)))

add.check()
add.save("temple.off")

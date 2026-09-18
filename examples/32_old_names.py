"""
32 -- a still life written in the add.py 1.2 vocabulary.

Every function of add.py 1.2 still exists under its old name -- ``cube``,
``cube2``, ``cylinder2``, ``cylinder3``, ``cone2``, ``rectangle3D``,
``spin3D``, ``curve``, ``newface``, ``circle``, ``off`` -- with the same
argument order, so a model written for the old course runs unchanged.
This file uses only those names (plus a few of the other spellings such
as ``ball``, ``block``, ``lathe``, ``translate``, ``subtract``), and builds
a table with a lamp, a vase, a picture and a pair of dice.

Parameter: ``SIDES`` (how round the turned parts are).
"""
import add

SIDES = 64
WOOD = [160, 110, 60]
BRASS = [190, 150, 70]

# the table: a slab on four legs (rectangle3D = a box with three sizes)
add.rectangle3D([0, 3.0, 0], [10, 0.3, 6], WOOD)
for x in (-4.5, 4.5):
    for z in (-2.6, 2.6):
        add.rectangle3D([x, 1.5, z], [0.4, 3.0, 0.4], add.shade(WOOD, 0.8))

# the lamp: cylinder3 is closed at A only, cone2 is the open cone wall
add.cylinder3([-3, 3.15, -1], [-3, 3.45, -1], 1.0, SIDES, BRASS)
add.cylinder([-3, 3.45, -1], [-3, 6.5, -1], 0.12, 12, BRASS)
add.cone2([-3, 6.3, -1], [-3, 7.9, -1], 1.4, SIDES, [200, 60, 50])
add.ball([-3, 6.75, -1], 0.4, 10, [255, 240, 180])           # the bulb
add.curve(lambda t: [-3 + 1.3 * add.sin(t), 3.15 + 0.15 * add.sin(4 * t), -1 - 1.5 * t / 3.0],
          0, 3, 40, 8, 0.05, [40, 40, 40], False)             # the cable


def vase(t):                                                  # spin3D: [radius, height]
    return [0.9 + 0.5 * add.sin(2.2 * t) - 0.3 * t, t * 2.6]


add.spin3D([2.5, 3.15, -1.5], [2.5, 4.15, -1.5], vase, 0, 1, 60, SIDES, [60, 110, 170])
add.circle([2.5, 3.16, -1.5], [2.5, 4.0, -1.5], 0.9, SIDES, [60, 110, 170])   # its base disc
add.cylinder2([2.5, 5.7, -1.5], [2.7, 7.6, -1.6], 0.05, 8, "green")          # a stem
add.lathe(lambda t: [0.6 * add.sin(t) ** 0.6, 0.35 * t], [2.7, 7.6, -1.6], [2.7, 8.6, -1.6],
          0.01, add.pi, 30, 30, "red")                        # the flower head

# a picture in a frame, standing at the back: newface draws one flat face
add.cube2([0, 4.4, 1.9], 2.5, 0.12, WOOD)                     # cube2 is a hollow cube frame
add.newface([[-1.2, 3.2, 3.1], [1.2, 3.2, 3.1], [1.2, 5.6, 3.1], [-1.2, 5.6, 3.1]],
            [120, 170, 220])
add.newface([[-1.2, 3.2, 3.09], [1.2, 3.2, 3.09], [1.2, 3.9, 3.09], [-1.2, 3.9, 3.09]],
            [90, 150, 80])
add.ball([0.4, 4.9, 3.05], 0.3, 8, "yellow")

# the dice: subtract (difference) drills the pips into a cube.  (push/pop
# are new, but a boolean needs the parts as separate meshes.)
for n, (x, spots) in enumerate([(-0.8, [(0, 0)]), (0.8, [(-1, -1), (1, 1), (-1, 1), (1, -1), (0, 0)])]):
    add.push()
    add.cube([0, 0, 0], 1.2, "white")
    body = add.pop()
    add.push()
    for (i, j) in spots:
        add.sphere([i * 0.35, 0.6, j * 0.35], 0.16, 6, "black")
    pips = add.pop()
    die = add.subtract(body, pips)
    die = add.translate(add.rotateY(die, 0.4 * n), [x, 3.75, -1.6])
    add.paste(die)

# a rounded cube (common = intersection) and a doubled block (add_solids = union)
add.push()
add.cube([0, 0, 0], 1.0, [220, 120, 40])
c = add.pop()
add.push()
add.sphere([0, 0, 0], 0.68, 10, [220, 120, 40])
s = add.pop()
add.paste(add.translate(add.common(c, s), [3.6, 3.65, -2.2]))
add.push()
add.block([0, 0, 0], [1.2, 0.5, 0.5], [90, 160, 90])
a = add.pop()
add.push()
add.block([0, 0, 0], [0.5, 0.5, 1.2], [90, 160, 90])
b = add.pop()
cross = add.weld(add.add_solids(a, b))
add.paste(add.translate(cross, [3.6, 3.4, 0.4]))
add.paste(add.reflect(add.translate(add.scale(cross, 0.6), [3.0, 3.3, 1.6]), [3.6, 0, 0], [1, 0, 0]))

add.check()
add.off("old_names.off")

"""
27 -- a robot reaching for a ball.

A figure is a tree of parts: each limb is built along the Y axis around
the origin, then ``aim``-ed at the point it should reach and moved into
place.  ``direction``, ``distance`` and ``midpoint`` do the geometry, so
changing ``TARGET`` moves both arms and the head follows.  The face is
``pixels`` art, the antenna a ``twist``-ed bar, the chest plate a ``gear``,
the neck a ``helix`` spring; ``transform`` with a shear matrix flattens a
copy of the robot into its shadow.

Parameters: ``TARGET`` (where the ball is), ``LEAN``.
"""
import add

TARGET = [2.6, 3.4, 2.0]
LEAN = 0.15                     # how much the body leans towards the ball

STEEL = [175, 180, 190]
DARK = [60, 65, 75]
BLUE = [40, 110, 200]
GLASS = [40, 40, 50]
LIGHT = [120, 255, 120]


# --------------------------------------------------------------------------
#  parts, each built around the origin along +Y
# --------------------------------------------------------------------------
def limb(length, r, color):
    """A capsule along +Y from the origin, with a ball joint at each end."""
    add.push()
    add.capsule([0, 0, 0], [0, length, 0], r, 12, color)
    add.sphere([0, 0, 0], r * 1.35, 5, DARK)
    add.sphere([0, length, 0], r * 1.35, 5, DARK)
    return add.pop()


def reach(start, end, r, color=STEEL):
    """A limb from ``start`` to ``end``: build it upright, aim it, move it."""
    part = limb(add.distance(start, end), r, color)
    add.mesh(add.move(add.aim(part, add.direction(start, end)), start))


# the body: a rounded box, leaning a little towards the target
BODY = [0, 3.2, 0]
add.push()
add.rounded_box([0, 0, 0], [2.4, 2.6, 1.5], 0.35, 7, STEEL)
add.gear([0, 0.35, 0.8], 12, 0.5, 0.16, BLUE, axis=[0, 0, 1], hole=0.12)
for i in range(3):                                          # a row of buttons
    add.sphere([-0.7 + 0.7 * i, -0.85, 0.78], 0.09, 3, add.hsv(i / 3.0))
add.text("ADD", [-0.42, -0.35, 0.78], 0.28, color=DARK, k=6)
body = add.pop()
towards = add.direction([0, 0, 0], [TARGET[0], 0, TARGET[2]])
body = add.rotate(body, [-towards[2], 0, towards[0]], LEAN, (0, -1.3, 0))
add.mesh(add.move(body, BODY))

# the neck (a spring) and the head, turned to look at the ball
NECK = [BODY[0], BODY[1] + 1.3, BODY[2]]
add.helix(NECK, 0.32, 0.22, 3, 120, 0.06, 8, DARK)
HEAD = [NECK[0], NECK[1] + 0.66 + 0.9, NECK[2]]
add.push()
add.rounded_box([0, 0, 0], [1.7, 1.6, 1.4], 0.4, 7, STEEL)
add.cuboid([0, 0.05, 0.68], [1.1, 1.15, 0.05], GLASS)                        # the screen
add.pixels(["r.....r", ".r...r.", "..r.r..", ".......", "g.....g", ".ggggg."],
           0.11, [-0.385, -0.42, 0.66], colors={"r": LIGHT, "g": BLUE}, depth=1)
add.cylinder([0, 0.8, 0], [0, 1.3, 0], 0.05, 6, DARK)                         # antenna
add.push()
add.cuboid([0, 1.75, 0], [0.16, 0.9, 0.16], BLUE)
add.mesh(add.twist(add.pop(), 3.0, [0, 1, 0], [0, 0, 0]))
add.push()
add.sphere([0, 2.35, 0], 0.22, 3, LIGHT)
add.wireframe(add.pop(), 0.015, 5, DARK)
head = add.pop()
look = add.direction(HEAD, TARGET)
head = add.aim(head, [look[0], 0, look[2]], [0, 0, 1])          # face the ball
add.mesh(add.move(head, HEAD))

# arms: upper arm from the shoulder to an elbow, forearm on to the hand
for side in (-1, 1):
    shoulder = [BODY[0] + 1.35 * side, BODY[1] + 0.9, BODY[2]]
    hand = [TARGET[0] + 0.45 * side, TARGET[1], TARGET[2] - 0.5]
    elbow = add.midpoint(shoulder, hand)
    elbow = [elbow[0] + 0.5 * side, elbow[1] - 0.9, elbow[2] + 0.3]
    reach(shoulder, elbow, 0.22)
    reach(elbow, hand, 0.19)
    add.push()                                                  # a three-finger gripper
    for a in (0, 2.1, 4.2):
        tip = add.rotate_point([0.26, 0.45, 0], [0, 1, 0], a)
        add.capsule([0, 0, 0], tip, 0.05, 8, DARK)
    grip = add.aim(add.pop(), add.direction(hand, TARGET))
    add.mesh(add.move(grip, hand))

# legs and feet
for side in (-1, 1):
    hip = [BODY[0] + 0.6 * side, BODY[1] - 1.3, BODY[2]]
    foot = [hip[0] + 0.3 * side, 0.35, hip[2] + 0.1]
    reach(hip, foot, 0.24)
    add.rounded_box([foot[0], 0.2, foot[2] + 0.2], [0.75, 0.4, 1.2], 0.15, 5, DARK)

# the ball, floating just where the hands meet, with a white band round it
add.sphere(TARGET, 0.45, 8, [230, 60, 60])
add.push()
add.sphere([0, 0, 0], 0.46, 4, "white")
band = add.stretch(add.pop(), [1.0, 0.1, 1.0], (0, 0, 0))
add.mesh(add.move(band, TARGET))

# the shadow: a copy of everything so far, flattened and sheared onto the floor
robot = add.layer()
shear = [[1, 0.6, 0, 0],
         [0, 0.0, 0, 0.01],
         [0, 0.35, 1, 0],
         [0, 0, 0, 1]]
add.mesh(robot)
add.mesh(add.color(add.transform(robot, shear), [165, 165, 175]))

# the floor last, so that it is not part of the shadow
add.grid([0, 0, 0], [14, 14], 14, 14,
         lambda x, z: [225, 225, 230] if (int(x + 20) + int(z + 20)) % 2 else [205, 205, 212])

add.check()
add.save("robot.off")

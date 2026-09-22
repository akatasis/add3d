"""
35 -- a knotted parametric curve drawn as a tube.

The curve is a sum of two rotating circles ("epicycles") with a slow
up-and-down motion, so it ties itself into a knot before it closes.  All
the frequencies (``s1``, ``v1``, ``s2``, ``v2``) are multiples of 0.2, so
over ``t`` in ``[0, 10 pi]`` every term returns to where it started and the
tube closes without a seam (``isConnected=True``).

``add.curve`` sweeps a circle of ``k`` sides along the curve: 3000 steps x
20 sides = 60 000 quads from three lines of maths.

Part 1 is the curve exactly as it was posed (one white tube, ``kreive1.off``);
part 2 paints the same tube by its parameter, twelve colours in all.

Parameter: ``s2`` (the fast frequency -- try 3.2 or 7.2 for other knots).
"""
import add

a1, b1, s1, v1 = 5, 10, 0.4, -1
a2, b2, s2, v2 = 2.1, 2.1, 5.2, 0.2


def P(t):
    x = (a1 * add.cos(s1 * t) * add.sin(v1 * t) + b1 * add.sin(s1 * t) * add.cos(v1 * t)
         + a2 * add.cos(s2 * t) * add.sin(v2 * t) + b2 * add.sin(s2 * t) * add.cos(v2 * t))
    y = 5 * add.sin(t)
    z = (-a1 * add.sin(s1 * t) * add.sin(v1 * t) + b1 * add.cos(s1 * t) * add.cos(v1 * t)
         - a2 * add.sin(s2 * t) * add.sin(v2 * t) + b2 * add.cos(s2 * t) * add.cos(v2 * t))
    return [x, y, z]


# --- part 1: the curve as posed, one white tube --------------------------
add.curve(P, 0, 10 * add.pi, 3000, 20, 0.25, [255, 255, 255], True)
add.check()
add.off("kreive1.off")                        # add.off() saves and clears the scene

# --- part 2: the same tube coloured along its length ---------------------
def rainbow(t, angle):
    return add.hsv(int(t / (10 * add.pi) * 12) / 12.0)


add.curve(P, 0, 10 * add.pi, 3000, 20, 0.25, color=rainbow, isConnected=True)
add.check()
add.save("knot_curve.off")

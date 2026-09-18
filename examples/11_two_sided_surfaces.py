"""
11 -- why a surface can look black, and the two ways to fix it.

A parametric surface is a sheet with no thickness.  Every face points one
way; from the other side a renderer sees its back, which is usually drawn
black or not at all.  Students hit this the first time they look at a saddle
from underneath.

Three copies of the same saddle:

    left    the plain sheet         -- one good side, one dead side
    middle  ``double_sided=True``   -- every face also exists reversed;
                                       cheap, still zero thickness
    right   ``thickness=0.1``       -- a real solid: watertight, printable,
                                       correct from every angle
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import add
import math


def saddle(u, v):
    return [u, (v * v - u * u) / 2.0, v]


add.parametric(saddle, -2, 2, 40, -2, 2, 40, "red")
plain = add.layer()

add.parametric(saddle, -2, 2, 40, -2, 2, 40, "gold", double_sided=True)
both = add.layer()

add.parametric(saddle, -2, 2, 40, -2, 2, 40, "teal", thickness=0.12)
solid = add.layer()

add.mesh(add.move(plain, [-5, 0, 0]))
add.mesh(both)
add.mesh(add.move(solid, [5, 0, 0]))

for name, M in (("plain sheet", plain), ("double sided", both),
                ("solid shell", solid)):
    s = add.stats(M)
    print("%-14s %6d faces   closed: %s" % (name, s["faces"], s["closed"]))

# The same trick rescues a ribbon, a leaf or a flower petal -- anything you
# would otherwise have to look at from exactly the right side.
add.check()
add.save("two_sided.off")

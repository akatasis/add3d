"""
16 -- adding, cutting and intersecting solids.

    add.union(A, B)        everything in either, with the buried walls gone
    add.intersect(A, B)    only what they have in common
    add.difference(A, B)   A with B carved out of it
    add.cut(A, point, n)   a quick straight slice with a plane

These need *closed* solids -- ``add.check()`` will tell you whether yours is
closed.  The freshly exposed surface keeps the colour of the tool that cut
it, so a hole is easy to see; pass ``color=`` to difference to override that.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import add
import math

CELL = 4.2
shown = []


def pair():
    """A box and a ball that overlap -- the standard demonstration."""
    add.box([0, 0, 0], 2.0, "red")
    a = add.layer()
    add.sphere([0.9, 0.9, 0.9], 1.3, 24, "blue")
    b = add.layer()
    return a, b


def show(name, M, size=3.0):
    shown.append((name, add.place(add.fit(M, size), (0, 0, 0))))


a, b = pair()
show("merge (no boolean)", add.merge([a, b]))
show("union", add.union(a, b))
show("difference", add.difference(a, b))
show("intersection", add.intersect(a, b))

# --- a hollow ball: a sphere minus a smaller sphere, then sliced open ------
add.sphere([0, 0, 0], 1.6, 32, "gold")
outer = add.layer()
add.sphere([0, 0, 0], 1.3, 32, "brown")
inner = add.layer()
shell = add.difference(outer, inner)
show("hollow ball, cut open", add.cut(shell, [0, 0, 0], [0.4, 0.3, 1.0]))

# --- a cube with all twelve edges rounded, the CSG way ---------------------
add.box([0, 0, 0], 2.0, "teal")
cube = add.layer()
add.sphere([0, 0, 0], 1.32, 40, "teal")
ball = add.layer()
show("rounded cube", add.intersect(cube, ball))

# --- a cross drilled through a block --------------------------------------
add.box([0, 0, 0], 2.0, "lime")
block = add.layer()
drills = []
for axis in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
    add.cylinder([-2 * axis[0], -2 * axis[1], -2 * axis[2]],
                 [2 * axis[0], 2 * axis[1], 2 * axis[2]], 0.55, 32, "black")
    drills.append(add.layer())
show("three holes", add.difference(block, drills))

# --- a ring made by subtracting a cylinder from a torus -------------------
add.torus([0, 0, 0], 1.4, 0.55, 64, 28, "magenta")
ring = add.layer()
add.cuboid([0, 1.0, 0], [6, 1.2, 6], "silver")
knife = add.layer()
show("torus, sliced", add.difference(ring, knife))

# --- letters cut out of a slab --------------------------------------------
add.cuboid([0, 0, 0], [4.0, 0.7, 1.6], "silver")
slab = add.layer()
stamps = []
for i, x in enumerate((-1.3, 0.0, 1.3)):
    add.cylinder([x, -1, 0], [x, 1, 0], 0.45, 28, "navy")
    stamps.append(add.layer())
show("perforated slab", add.difference(slab, stamps))

# --- a pipe junction: union of two tubes, then hollowed out ---------------
add.cylinder([0, -1.6, 0], [0, 1.6, 0], 0.8, 40, "orange")
t1 = add.layer()
add.cylinder([-1.6, 0, 0], [1.6, 0, 0], 0.8, 40, "orange")
t2 = add.layer()
add.cylinder([0, -1.8, 0], [0, 1.8, 0], 0.6, 40, "navy")
h1 = add.layer()
add.cylinder([-1.8, 0, 0], [1.8, 0, 0], 0.6, 40, "navy")
h2 = add.layer()
show("pipe elbow", add.difference(add.union(t1, t2), h1, h2))

# --- symmetric difference: what is in one but not both --------------------
a, b = pair()
show("symmetric difference", add.symmetric_difference(a, b))

# --- a stack of slices: cut() used repeatedly -----------------------------
add.sphere([0, 0, 0], 1.6, 36, "purple")
ball = add.layer()
slices = []
for i in range(6):
    y = -1.6 + 3.2 * i / 6.0
    # cut() keeps the side the normal points AWAY from, so the first call
    # keeps everything below y + 0.42 and the second everything above y.
    piece = add.cut(add.cut(ball, [0, y + 0.42, 0], [0, 1, 0]),
                    [0, y, 0], [0, -1, 0])
    slices.append(add.move(piece, [0, i * 0.18, 0]))
show("sliced ball", add.merge(slices))

# --- a gear, built from a cylinder and a ring of teeth --------------------
add.cylinder([0, -0.3, 0], [0, 0.3, 0], 1.5, 64, "gold")
disc = add.layer()
add.cuboid([1.6, 0, 0], [0.7, 0.62, 0.42], "gold")
tooth = add.layer()
add.cylinder([0, -0.5, 0], [0, 0.5, 0], 0.45, 32, "black")
bore = add.layer()
gear = add.difference(add.union(disc, add.array_radial(tooth, 16)), bore)
show("gear", gear)

columns = 4
for i, (name, M) in enumerate(shown):
    add.mesh(add.move(M, [(i % columns) * CELL, 0, (i // columns) * CELL]))
    print("%2d. %-24s %6d faces" % (i + 1, name, M.polygons))

add.check()
add.save("booleans.off")

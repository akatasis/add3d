"""
17 -- fractals: a small rule, applied again and again.

Recursion is where "a 3D model written as a program" really earns its keep.
None of these could sensibly be drawn by hand, and each is a dozen lines.
"""
import add

CELL = 7.0
shown = []


def show(name, M, size=5.0):
    shown.append((name, add.place(add.fit(M, size), (0, 0, 0))))


# --------------------------------------------------------------------------
#  Menger sponge -- a cube with its middles removed, over and over
# --------------------------------------------------------------------------
def menger(level):
    """Which unit cells of a 3**level grid are solid."""
    cells = set()
    n = 3 ** level
    for x in range(n):
        for y in range(n):
            for z in range(n):
                a, b, c = x, y, z
                solid = True
                for _ in range(level):
                    middles = (a % 3 == 1) + (b % 3 == 1) + (c % 3 == 1)
                    if middles >= 2:
                        solid = False
                        break
                    a, b, c = a // 3, b // 3, c // 3
                if solid:
                    cells.add((x, y, z))
    return cells


add.voxels(menger(3), 1.0, color="gold")
sponge = add.layer()
show("Menger sponge (level 3)", add.color_by(
    sponge, lambda p: add.hsv(0.08 + p[1] / 90.0, 0.6, 1.0)))


# --------------------------------------------------------------------------
#  Sierpinski tetrahedron -- four copies of itself, half the size
# --------------------------------------------------------------------------
def sierpinski(level, col):
    add.polyhedron("tetrahedron", [0, 0, 0], 1.0, col)
    piece = add.layer()
    for step in range(level):
        s = 2.0 ** step
        copies = [add.move(piece, [0, 0, 0]),
                  add.move(piece, [0, s * 1.633, s * 1.633]),
                  add.move(piece, [s * 1.633, 0, s * 1.633]),
                  add.move(piece, [s * 1.633, s * 1.633, 0])]
        piece = add.merge(copies)
    return piece


show("Sierpinski tetrahedron", add.color_by(
    sierpinski(5, "white"), lambda p: add.hsv((p[0] + p[2]) / 90.0, 0.7, 1.0)))


# --------------------------------------------------------------------------
#  A recursive tree -- a trunk that splits into smaller trunks
# --------------------------------------------------------------------------
add.seed(11)


def branch(start, direction, length, radius, depth):
    end = [start[i] + direction[i] * length for i in range(3)]
    col = "brown" if depth > 2 else "lime"
    add.cylinder(start, end, radius, 8, col)
    if depth == 0:
        add.sphere(end, radius * 3.2, 6, "lime")
        return
    for _ in range(3):
        d = [direction[i] + add.uniform(-0.65, 0.65) for i in range(3)]
        d[1] += 0.45
        n = add.sqrt(sum(a * a for a in d))
        d = [a / n for a in d]
        branch(end, d, length * add.uniform(0.6, 0.8), radius * 0.68,
               depth - 1)


branch([0, 0, 0], [0, 1, 0], 2.2, 0.22, 5)
show("recursive tree", add.layer())


# --------------------------------------------------------------------------
#  A Koch-like snowflake extruded into a solid prism
# --------------------------------------------------------------------------
def koch(points, level):
    if level == 0:
        return points
    out = []
    n = len(points)
    for i in range(n):
        a = points[i]
        b = points[(i + 1) % n]
        d = [(b[0] - a[0]) / 3.0, (b[1] - a[1]) / 3.0]
        p1 = [a[0] + d[0], a[1] + d[1]]
        p2 = [a[0] + 2 * d[0], a[1] + 2 * d[1]]
        # the tip of the little triangle: rotate d by -60 degrees
        cs, sn = add.cos(-add.pi / 3), add.sin(-add.pi / 3)
        tip = [p1[0] + d[0] * cs - d[1] * sn, p1[1] + d[0] * sn + d[1] * cs]
        out += [a, p1, tip, p2]
    return koch(out, level - 1)


triangle = [[add.cos(a), add.sin(a)]
            for a in (add.pi / 2, add.pi / 2 + 2 * add.pi / 3,
                      add.pi / 2 + 4 * add.pi / 3)]
add.extrude(koch(triangle, 4), [0, 0.45, 0], "sky")
show("Koch snowflake prism", add.layer())


# --------------------------------------------------------------------------
#  A Pythagoras tree of boxes, grown in 3D
# --------------------------------------------------------------------------
def pythagoras(corner, along, depth):
    """A square standing on the edge ``corner -> corner + along``.

    ``up`` is ``along`` turned a quarter turn, so the square is
    corner, corner+along, corner+along+up, corner+up.  On its top edge sit
    two smaller squares, meeting at a right angle -- and so on downwards.
    """
    if depth == 0:
        return
    up = (-along[1], along[0])
    p = [(corner[0], corner[1]), (corner[0] + along[0], corner[1] + along[1]),
         (corner[0] + along[0] + up[0], corner[1] + along[1] + up[1]),
         (corner[0] + up[0], corner[1] + up[1])]
    add.extrude([list(q) for q in p], [0, 0, 0.35],
                add.hsv(0.08 + 0.035 * depth, 0.5, 0.55 + 0.05 * depth),
                center=(0, 0, -0.175))
    a, b = p[3], p[2]                                # the top edge
    apex = ((a[0] + b[0]) / 2.0 + up[0] / 2.0, (a[1] + b[1]) / 2.0 + up[1] / 2.0)
    pythagoras(a, (apex[0] - a[0], apex[1] - a[1]), depth - 1)
    pythagoras(apex, (b[0] - apex[0], b[1] - apex[1]), depth - 1)


pythagoras((0.0, 0.0), (1.4, 0.0), 9)
show("Pythagoras tree", add.layer())


columns = 3
for i, (name, M) in enumerate(shown):
    add.mesh(add.move(M, [(i % columns) * CELL, 0, (i // columns) * CELL]))
    print("%2d. %-26s %7d faces" % (i + 1, name, M.polygons))

add.check()
add.save("fractals.off")

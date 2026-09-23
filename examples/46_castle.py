"""
46 -- Algoritmų pilis: the castle. The showcase model of add.py 2.0.

A castle on a hill in a transparent lake, with everything a castle needs:
an octagonal curtain wall of individual stone blocks, eight hollow round
towers with spiral stairs, doors and lookout platforms, a gatehouse with a
portcullis and a drawbridge hanging on real chains, a palace with glass
windows, balconies, dormers, a roof of single tiles and copper spires, a
chapel with stained glass and an altar, and a courtyard full of life: a
well, a fountain, a smithy, a market, a stable, a trebuchet, cannons,
carts, barrels, crates, planks, bricks, weapon racks, guards in armour,
horses, chickens, a dog.  The lake is transparent, so the fish, the
pebbles and the sunken boat can be seen through the water.

Easter eggs, for anyone who walks inside: the great hall with the king on
his throne, a feast on the long tables (roast pig, chickens, bread,
cheese, fruit, wine), chandeliers, a chess study on a little table ("White
to play and win"), the name of the castle above the throne; the soldiers'
dormitory upstairs with sleeping men; the attic full of old junk; and, in
the big tower, the treasury with a dragon asleep on the gold, the armoury
and the lord's chamber.

There are no image textures: every stone block, brick, plank, roof tile,
cobblestone, pane of stained glass and coat of arms is geometry, drawn by
this program.  Round things get many sides (``k_``), flat things few, so
the detail goes where the eye goes.  The model is written *streaming*
(``add.stream``) to two files at once -- ``castle.off`` (about 400 MB) and
``castle.obj`` (the same model with the water and the glass see-through;
compressed with 7-Zip it is under 100 MB, which Sketchfab accepts) -- so
it is never held in memory as a whole, and every part is tidied on the
way: welded vertices, no repeated or buried faces, no overlapping faces
that would flicker.  Fewer than 100 colours are used.  MeshLab opens the
``.off`` in about 2.5 GB of memory (blades of grass and leaves share
their root vertices to keep it there); Sketchfab takes the ``.obj``.

    python3 46_castle.py              -> castle.off + castle.obj + castle.mtl

Parameter: ``DENSITY`` (1.0 is the model; 0.1 -- ``CASTLE_DENSITY=0.1`` in
the environment -- thins the pebbles, grass, leaves and cobbles for a quick
run while editing, and is what the documentation pictures are made from).
"""
import os
import sys
import time

import add

DENSITY = float(os.environ.get("CASTLE_DENSITY", "1.0"))    # 0.1 for a quick test run
OUT_OFF, OUT_OBJ = "castle.off", "castle.obj"
add.seed(2026)
started = time.time()


def count(n):
    """A number of small things, scaled by the density."""
    return max(1, int(n * DENSITY))


def k_(n):
    """Sides of a round part: round things must look round."""
    return max(12, int(n * 2.4))


# --------------------------------------------------------------------------
#  Palette -- a fixed set of colours, so the file stays under 50 materials
#  (colours + textures + glass are all materials in an .obj).
# --------------------------------------------------------------------------
P = {
    "stone": [196, 186, 160], "stone_dark": [150, 140, 118], "mortar": [120, 112, 98],
    "brick": [172, 96, 62], "wood": [128, 86, 48], "wood_dark": [88, 58, 32],
    "wood_light": [176, 128, 80], "iron": [70, 70, 76], "steel": [190, 195, 205],
    "gold": [222, 178, 60], "copper": [72, 150, 120], "slate": [70, 82, 104],
    "red": [178, 34, 40], "white": [240, 236, 226], "black": [28, 26, 26],
    "leaf": [62, 124, 48], "leaf_dark": [40, 92, 36], "trunk": [92, 64, 40],
    "grass": [96, 150, 58], "grass_dry": [140, 158, 70], "rock": [118, 112, 104],
    "sand": [200, 184, 140], "lakebed": [150, 140, 110], "straw": [214, 178, 92],
    "rope": [178, 150, 96], "bread": [196, 140, 76], "cheese": [232, 196, 80],
    "meat": [150, 78, 52], "apple": [190, 40, 40], "grape": [110, 50, 130],
    "orange": [230, 140, 40], "pig": [226, 168, 150], "cushion": [150, 24, 40],
    "blue": [40, 70, 160], "purple": [96, 40, 140], "flame_core": [255, 230, 120],
    "bone": [226, 220, 200], "dragon": [56, 120, 70], "dragon_belly": [180, 190, 120], "dragon_wing": [38, 88, 52],
    "glass_frame": [60, 60, 66], "skin": [222, 186, 150], "linen": [214, 206, 186],
}
P["spire"] = [150, 72, 54]                              # the reddish-brown of the palace spires
P["earth"] = [146, 128, 98]                             # packed earth of the courtyard ...
P["earth_light"] = [162, 145, 114]                      # ... trodden dry beside the paths
P["earth_dark"] = [128, 110, 82]                        # ... damp in the shadow of the walls
GLASS = add.transparent([170, 210, 245], 0.35)
WATER = add.transparent([50, 120, 200], 0.5)
FLAME = add.transparent([255, 150, 40], 0.65)
SMOKE = add.transparent([150, 150, 160], 0.3)
STAINED = [add.transparent(c, 0.6) for c in ([200, 40, 40], [40, 60, 180], [230, 190, 40], [40, 150, 70], [230, 230, 240])]
COLOR_LIMIT = 100                                      # distinct colours (materials) allowed in the model


# --------------------------------------------------------------------------
#  No textures: a cheap repeatable pseudo-random number picks shades
# --------------------------------------------------------------------------
def hash2(x, y, s=0):
    """A cheap repeatable pseudo-random number in 0..1 for the pair (x, y)."""
    n = (x * 374761393 + y * 668265263 + s * 1274126177) & 0xffffffff
    n = (n ^ (n >> 13)) * 1274126177 & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffff) / 65535.0


# --------------------------------------------------------------------------
#  Streaming output: every finished part is tidied once (welded, no
#  repeated, buried or overlapping faces) and goes straight to both files.
#  Four decimals per coordinate are plenty and keep the files compact.
# --------------------------------------------------------------------------
out = add.stream(OUT_OFF, clean=False, precision=4)    # add.Stream objects
out_obj = add.stream(OUT_OBJ, clean=False, precision=4)


def flush(label, clean=None):
    """Write the scene to both files; ``clean=False`` skips the tidying for
    a part that is thousands of separate small things (pebbles, grass)."""
    M = add.layer()
    if clean is not False:
        M = add.clean(M, tol=1e-6)
    out.add(M, clean=False)
    n = out_obj.add(M, clean=False)
    print("  %-30s %9d faces  %7.1f MB  %5.0fs" % (label, n, out.bytes / 1e6, time.time() - started))
    sys.stdout.flush()


# --------------------------------------------------------------------------
#  Small vector helpers and building blocks used all over the castle
# --------------------------------------------------------------------------
def vsub(a, b):
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]


def vlen(a):
    return add.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])


def vunit(a):
    L = vlen(a) or 1.0
    return [a[0] / L, a[1] / L, a[2] / L]


def vcross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


SHADED = ("stone", "stone_dark", "brick", "wood", "wood_light", "wood_dark", "slate", "spire")


def shade_of(name, i, n=3, spread=0.14):
    """One of ``n`` fixed shades of a palette colour -- fixed, not random,
    so that the colour count of the model stays small (under 100)."""
    if name not in SHADED:
        return P[name]
    key = "%s~%d" % (name, i % n)
    if key not in P:
        P[key] = add.shade(P[name], 1 - spread + 2 * spread * (i % n) / max(1, n - 1))
    return P[key]


def pick(name, x, y, n=3):
    """A repeatable shade for the stone / brick / plank at (x, y)."""
    return shade_of(name, int(hash2(int(x * 7), int(y * 7)) * n) % n, n)


def frame_to(M, a, d, n):
    """Move a part built along +X (with +Z = outward) so that +X runs along
    ``d`` and +Z along ``n``, starting from point ``a``."""
    return add.transform(M, [[d[0], 0, n[0], a[0]],
                             [0, 1, 0, a[1]],
                             [d[2], 0, n[2], a[2]]])


def outward(a, b, centre=(0, 0)):
    """Unit direction a -> b in XZ and the unit normal pointing away from ``centre``."""
    dx, dz = b[0] - a[0], b[2] - a[2]
    L = add.sqrt(dx * dx + dz * dz)
    d = (dx / L, 0, dz / L)
    n = (dz / L, 0, -dx / L)
    mx, mz = (a[0] + b[0]) / 2 - centre[0], (a[2] + b[2]) / 2 - centre[1]
    if n[0] * mx + n[2] * mz < 0:
        n = (-n[0], 0, -n[2])
    return L, d, n


def sheet(points, color, thick=0.02, hinge=False):
    """A leaf, a blade of grass, a sheet of cloth: one polygon and its
    back, a hair apart, so it is seen from both sides without flicker.
    With ``hinge`` the back shares the first edge (the root of a blade,
    the stalk of a leaf) and only the far corners are set back: two
    vertices fewer per sheet, which is a third of the file for the
    hundreds of thousands of blades and leaves; a triangle, or a
    quadrilateral whose first and last edges are parallel, stays flat."""
    n = vunit(vcross(vsub(points[1], points[0]), vsub(points[2], points[0])))
    back = [[q[0] - n[0] * thick, q[1] - n[1] * thick, q[2] - n[2] * thick] for q in points]
    if not hinge:
        add.polygon(points, color)
        add.polygon(back[::-1], color)
        return
    M = add.Mesh()
    for q in points:
        M.add_vertex(q)
    for q in back[2:]:
        M.add_vertex(q)
    k = len(points)
    M.add_face(list(range(k)), color)                                       # the front ...
    M.add_face([1, 0] + list(range(2 * k - 3, k - 1, -1)), color)             # ... and the back, on the same root
    add.mesh(M)


def solid(points_xz, y0, y1, color):
    """A closed solid with a flat polygon (in XZ) as its cross-section,
    from height y0 to y1 -- a step, a platform, a slab of any outline."""
    area = 0.0
    for i in range(len(points_xz)):
        x0, z0 = points_xz[i]
        x1, z1 = points_xz[(i + 1) % len(points_xz)]
        area += x0 * z1 - x1 * z0
    pts = list(points_xz) if area < 0 else list(reversed(points_xz))     # top face must point up
    M = add.Mesh()
    M.add_polygon([[x, y1, z] for x, z in pts], color)
    M.add_polygon([[x, y0, z] for x, z in reversed(pts)], color)
    for i in range(len(pts)):
        (x0, z0), (x1, z1) = pts[i], pts[(i + 1) % len(pts)]
        M.add_polygon([[x0, y0, z0], [x1, y0, z1], [x1, y1, z1], [x0, y1, z0]], color)
    return M


BLOCK = (1.0, 0.5)                                     # size of one wall stone
DOOR_W, DOOR_H = 2.0, 3.4                              # one size of doorway everywhere (the gate and the hall door are bigger):
                                                       # a man in armour walks through with a head and more to spare


def trimmed(x0, x1, y0, y1, skip, least=0.15):
    """The parts of the block x0..x1, y0..y1 that lie clear of the openings
    in ``skip``.  An opening is ``(x0, x1, y0, y1)`` or, arched,
    ``(x0, x1, y0, y1, (cx, cy, r))`` with the arch's centre and radius:
    above the springing line ``cy`` only the round part counts.  A block
    that meets an opening is not left out but cut short, so the courses
    run right up to the stone surround (with pieces above and below it
    where a course straddles the opening's top or sill), the way a mason
    fits closers round a window; slivers under ``least`` are dropped."""
    pieces = [(x0, x1, y0, y1)]
    for o in skip:
        sx0, sx1, sy0, sy1 = o[:4]
        out = []
        for piece in pieces:
            px0, px1, py0, py1 = piece
            if not (px1 > sx0 and px0 < sx1 and py1 > sy0 and py0 < sy1):
                out.append(piece)
                continue
            fx0, fx1, fy0, fy1 = sx0, sx1, sy0, sy1          # the part of the piece to cut away
            if len(o) > 4 and py0 >= o[4][1]:                # above the springing line: only the arch
                cx, cy, r = o[4]
                dy = py0 - cy                                # the piece's nearest edge to the centre
                if dy >= r:
                    out.append(piece)
                    continue
                w = add.sqrt(r * r - dy * dy)                # the arch's half width at that edge
                fx0, fx1, fy0 = max(sx0, cx - w), min(sx1, cx + w), cy
                if not (px1 > fx0 and px0 < fx1):
                    out.append(piece)
                    continue
            if fx0 > px0:
                out.append((px0, fx0, py0, py1))             # left of the opening, full height
            if fx1 < px1:
                out.append((fx1, px1, py0, py1))             # right of it
            mx0, mx1 = max(px0, fx0), min(px1, fx1)
            if fy0 > py0:
                out.append((mx0, mx1, py0, fy0))             # below the sill
            if fy1 < py1:
                out.append((mx0, mx1, fy1, py1))             # above the head
        pieces = out
    return [p for p in pieces if p[1] - p[0] >= least and p[3] - p[2] >= least]


def stone_face(length, y0, y1, z, depth, name="stone", size=None, gap=0.06, seed=0, skip=()):
    """A skin of staggered stone blocks on the plane ``z`` (facing +Z when
    ``depth`` > 0), from x = 0..length and y0..y1; ``skip`` lists the
    openings -- windows and doors -- that the blocks are fitted round
    (see :func:`trimmed`)."""
    bl, bh = size or BLOCK
    rows = max(1, int(round((y1 - y0) / bh)))
    bh = (y1 - y0) / rows
    for j in range(rows):
        y = y0 + j * bh
        x = -(bl / 2) if j % 2 else 0.0
        while x < length:
            x0, x1 = max(x, 0.0), min(x + bl, length)
            x += bl
            if x1 - x0 < 0.12:
                continue
            for px0, px1, py0, py1 in trimmed(x0, x1, y, y + bh, skip, least=min(0.15, bh * 0.4)):
                add.cuboid([(px0 + px1) / 2, (py0 + py1) / 2, z + depth / 2],
                           [px1 - px0 - gap, py1 - py0 - gap, abs(depth)], pick(name, px0 + seed * 97, j + seed))


def brick_box(centre, size, name="brick"):
    """A brick-built block: a mortar core with skins of small bricks on the
    four vertical faces (chimneys, hearths, the smithy's wall)."""
    cx, cy, cz = centre
    w, h, d = size
    add.cuboid(centre, size, P["mortar"])
    for face in range(4):
        add.push()
        stone_face(w if face % 2 == 0 else d, 0, h, 0, 0.06, name, size=(0.4, 0.2), gap=0.03, seed=face + int(cx * 3))
        M = add.move(add.pop(), [-(w if face % 2 == 0 else d) / 2, -h / 2, (d if face % 2 == 0 else w) / 2])
        add.mesh(add.move(add.rotateY(M, face * add.pi / 2), centre))


def rect_minus(p, h):
    """The rectangle p = (x0, x1, z0, z1) with the rectangle h taken away,
    as up to four rectangles."""
    px0, px1, pz0, pz1 = p
    hx0, hx1, hz0, hz1 = h
    if px1 <= hx0 or px0 >= hx1 or pz1 <= hz0 or pz0 >= hz1:
        return [p]
    out = []
    if hx0 > px0:
        out.append((px0, hx0, pz0, pz1))
    if hx1 < px1:
        out.append((hx1, px1, pz0, pz1))
    mx0, mx1 = max(px0, hx0), min(px1, hx1)
    if hz0 > pz0:
        out.append((mx0, mx1, pz0, hz0))
    if hz1 < pz1:
        out.append((mx0, mx1, hz1, pz1))
    return out


def board_minus_circle(p, circle, along):
    """A board p = (x0, x1, z0, z1) running ``along`` "x" or "z", sawn off
    square where it meets the circle (cx, cz, r): the cut clears the circle
    over the whole width of the board."""
    px0, px1, pz0, pz1 = p
    cx, cz, r = circle
    if along == "x":
        d = min(max(cz, pz0), pz1) - cz
        if d * d >= r * r:
            return [p]
        half = add.sqrt(r * r - d * d)
        return [q for q in ((px0, min(px1, cx - half), pz0, pz1), (max(px0, cx + half), px1, pz0, pz1)) if q[1] > q[0]]
    d = min(max(cx, px0), px1) - cx
    if d * d >= r * r:
        return [p]
    half = add.sqrt(r * r - d * d)
    return [q for q in ((px0, px1, pz0, min(pz1, cz - half)), (px0, px1, max(pz0, cz + half), pz1)) if q[3] > q[2]]


def plank_floor(x0, x1, z0, z1, y, thick=0.04, width=0.3, length=3.0, name="wood", along="z", avoid=None,
                holes=(), rounds=()):
    """A floor of separate boards (staggered, three shades) whose top is at
    ``y``.  Where the floor is open the boards are sawn off at the edge --
    ``holes`` are rectangles (x0, x1, z0, z1), a stairwell; ``rounds`` are
    circles (cx, cz, r), a tower passing through -- rather than left lying
    across the opening or taken out whole; a board running along an edge is
    cut lengthwise.  ``avoid(x, z)`` still leaves out whole boards."""
    rows = int((x1 - x0) / width) if along == "z" else int((z1 - z0) / width)
    span = (z1 - z0) if along == "z" else (x1 - x0)
    for i in range(rows):
        offset = (i % 3) * length / 3.0
        t = -offset
        while t < span:
            t0, t1 = max(t, 0.0), min(t + length, span)
            t += length
            if t1 - t0 < 0.15:
                continue
            if along == "z":                                         # the board, 1 cm in from its neighbours
                board = (x0 + i * width + 0.01, x0 + (i + 1) * width - 0.01, z0 + t0 + 0.01, z0 + t1 - 0.01)
            else:
                board = (x0 + t0 + 0.01, x0 + t1 - 0.01, z0 + i * width + 0.01, z0 + (i + 1) * width - 0.01)
            if avoid and avoid((board[0] + board[1]) / 2, (board[2] + board[3]) / 2):
                continue
            pieces = [board]
            for hole in holes:
                pieces = [q for piece in pieces for q in rect_minus(piece, hole)]
            for circle in rounds:
                pieces = [q for piece in pieces for q in board_minus_circle(piece, circle, along)]
            shade = shade_of(name, int(hash2(i, int(t0 * 10)) * 3))
            for bx0, bx1, bz0, bz1 in pieces:
                if bx1 - bx0 > 0.05 and bz1 - bz0 > 0.05:          # no slivers
                    add.cuboid([(bx0 + bx1) / 2, y - thick / 2, (bz0 + bz1) / 2], [bx1 - bx0, thick, bz1 - bz0], shade)


def arms(w, h, thick=0.04, field=None):
    """The coat of arms of the castle as geometry, built in the XY plane
    facing +Z with its bottom-left corner at the origin: a red field with
    a gold border, a gold bend and three white roundels."""
    field = field or P["red"]
    add.push()
    add.cuboid([w / 2, h / 2, 0], [w, h, thick], field)
    z = thick / 2
    band = add.make(add.cuboid, [0, 0, 0], [w * 0.16, add.sqrt(w * w + h * h) * 0.95, 0.01], P["gold"])
    add.mesh(add.move(add.rotateZ(band, add.atan2(w, h)), [w / 2, h / 2, z + 0.005]))
    for cx, cy in ((w * 0.25, h * 0.78), (w * 0.75, h * 0.78), (w * 0.5, h * 0.22)):
        add.cylinder([cx, cy, z], [cx, cy, z + 0.012], w * 0.1, 12, P["white"])
    for x in (0.02, w - 0.02):
        add.cuboid([x, h / 2, z + 0.004], [0.04, h, 0.008], P["gold"])
    for y in (0.02, h - 0.02):
        add.cuboid([w / 2, y, z + 0.004], [w, 0.04, 0.008], P["gold"])
    return add.pop()


def merlons(length, y, z0, z1, h=1.6, w=1.4, gap=0.9, name="stone"):
    """A crenellated parapet along x = 0..length at height ``y``, between z0 and z1."""
    x = 0.0
    i = 0
    while x < length - 0.3:
        w1 = min(w, length - x)
        add.cuboid([x + w1 / 2, y + h / 2, (z0 + z1) / 2], [w1, h, abs(z1 - z0)], pick(name, i, 3))
        x += w + gap
        i += 1


def arch_fill(x0, x1, ys, y1, z0, z1, cx, r, color, n=None):
    """The piece of wall above an arched opening: everything between the
    arc (centre ``(cx, ys)``, radius ``r``) and the rectangle x0..x1, ys..y1,
    extruded from z0 to z1.  Returned as a closed, welded mesh."""
    n = n or k_(10)
    arc = [(cx + r * add.cos(add.pi * i / n), ys + r * add.sin(add.pi * i / n)) for i in range(n + 1)]
    corners = [(x1, ys), (x1, y1), (x0, y1), (x0, ys)]
    lengths = [y1 - ys, x1 - x0, y1 - ys]
    total = float(sum(lengths))

    def rim(t):
        d = t * total
        for (ax, ay), (bx, by), L in zip(corners, corners[1:], lengths):
            if d <= L + 1e-9:
                return (ax + (bx - ax) * d / L, ay + (by - ay) * d / L)
            d -= L
        return corners[-1]

    rect = [rim(i / float(n)) for i in range(n + 1)]
    M = add.Mesh()

    def at(p, z):
        return [p[0], p[1], z]

    for i in range(n):
        M.add_polygon([at(rect[i], z1), at(rect[i + 1], z1), at(arc[i + 1], z1), at(arc[i], z1)], color)
        M.add_polygon([at(arc[i], z0), at(arc[i + 1], z0), at(rect[i + 1], z0), at(rect[i], z0)], color)
        M.add_polygon([at(arc[i], z0), at(arc[i], z1), at(arc[i + 1], z1), at(arc[i + 1], z0)], color)
        M.add_polygon([at(rect[i + 1], z0), at(rect[i + 1], z1), at(rect[i], z1), at(rect[i], z0)], color)
    M.add_polygon([at(arc[0], z0), at(arc[0], z1), at(rect[0], z1), at(rect[0], z0)], color)
    M.add_polygon([at(rect[-1], z0), at(rect[-1], z1), at(arc[-1], z1), at(arc[-1], z0)], color)
    return add.fix_normals(add.clean(M))


def voussoirs(cx, cy, r, z, depth, n, color_fn, width=0.5):
    """The wedge-shaped stones round an arch, on the face ``z``."""
    for i in range(n):
        a0, a1 = add.pi * i / n, add.pi * (i + 1) / n
        am = (a0 + a1) / 2
        stone = add.make(add.cuboid, [0, 0, 0], [(a1 - a0) * (r + width / 2) - 0.05, width, abs(depth)], color_fn(i))
        stone = add.rotateZ(stone, am - add.pi / 2)
        add.mesh(add.move(stone, [cx + (r + width / 2) * add.cos(am), cy + (r + width / 2) * add.sin(am), z + depth / 2]))


def jamb_stones(x0, x1, y0, y1, z, depth, name="stone"):
    """Quoins: the dressed stones up both sides of an opening (x0..x1, from
    y0 to y1), alternately long and short like real masonry, on the face
    ``z`` standing ``depth`` proud of it."""
    for side, x_edge in ((-1, x0), (1, x1)):
        y = y0
        i = 0
        while y < y1 - 0.02:
            h = min(0.5 if i % 2 == 0 else 0.3, y1 - y)
            w = 0.42 if i % 2 == 0 else 0.3
            add.cuboid([x_edge + side * w / 2, y + h / 2, z + depth / 2], [w - 0.03, h - 0.03, abs(depth)],
                       shade_of(name, i + (0 if side < 0 else 1)))
            y += h
            i += 1


def arch_profile(y0, w, h, n=None):
    """The outline of an arched opening ``w`` wide and ``h`` tall standing
    on ``y0``, as (s, y) points anticlockwise: a rectangle under a
    semicircular head.  One closed outline, so the solid extruded from
    it is a single cutter (two overlapping cutters would leave the wall
    standing where they overlap)."""
    r = w / 2
    n = n or k_(10)
    pts = [(-r, y0), (r, y0), (r, y0 + h - r)]
    pts += [(r * add.cos(add.pi * i / n), y0 + h - r + r * add.sin(add.pi * i / n)) for i in range(1, n)]
    pts.append((-r, y0 + h - r))
    return pts


def spiral_stair(cx, cz, y0, y1, r_out=3.3, r_in=0.35, rise=0.28, sweep=0.36, start=0.0, color="stone_dark",
                 newel=True, arcs=3, r_of=None):
    """A spiral stair round a newel post at (cx, cz), from y0 up to y1,
    turning anticlockwise as it climbs.  Each step is a solid wedge out to
    ``r_out`` -- or, with ``r_of(angle)``, out to the wall of a shaft of
    any outline (a square tower: the steps reach into its corners)."""
    n = max(1, int(round((y1 - y0) / rise)))
    rise = (y1 - y0) / float(n)
    for i in range(n):
        a0 = start + i * sweep
        a1 = a0 + sweep
        pts = [(cx + r_in * add.cos(a0), cz + r_in * add.sin(a0))]
        for a in outline_angles(a0, a1, arcs, r_of):
            rr = r_of(a) if r_of else r_out
            pts.append((cx + rr * add.cos(a), cz + rr * add.sin(a)))
        pts.append((cx + r_in * add.cos(a1), cz + r_in * add.sin(a1)))
        add.mesh(solid(pts, y0 + i * rise, y0 + (i + 1) * rise, shade_of(color, i)))
    if newel:
        add.cylinder([cx, y0, cz], [cx, y1 + 1.0, cz], r_in, k_(8), P["stone"])
    return start + n * sweep                            # the angle where the stair arrives


def outline_angles(a0, a1, arcs, r_of=None):
    """Angles from a0 to a1 in ``arcs`` steps -- plus, when ``r_of`` is the
    outline of a square, the exact corner angles that fall between, so a
    step or a floor fits the corner sharply."""
    out = [a0 + (a1 - a0) * j / arcs for j in range(arcs + 1)]
    if r_of is not None:
        k0 = int(add.floor((a0 - add.pi / 4) / (add.pi / 2))) + 1
        while add.pi / 4 + k0 * add.pi / 2 < a1 - 1e-9:
            corner = add.pi / 4 + k0 * add.pi / 2
            if corner > a0 + 1e-9:
                out.append(corner)
            k0 += 1
        out.sort()
    return out


def square_outline(half):
    """r(angle) of a square of half-width ``half`` round the origin."""
    return lambda a: half / max(abs(add.cos(a)), abs(add.sin(a)))


def flagstones(x0, x1, z0, z1, y, size=0.9, thick=0.06, name="stone_dark", avoid=None):
    """A paving of flat stones (three shades, small gaps) whose top is at ``y``."""
    nx, nz = max(1, int((x1 - x0) / size)), max(1, int((z1 - z0) / size))
    sx, sz = (x1 - x0) / nx, (z1 - z0) / nz
    for i in range(nx):
        for j in range(nz):
            cx, cz = x0 + (i + 0.5) * sx, z0 + (j + 0.5) * sz
            if avoid and avoid(cx, cz):
                continue
            add.cuboid([cx, y - thick / 2, cz], [sx - 0.05, thick, sz - 0.05], shade_of(name, int(hash2(i, j, 4) * 3)))


def wall_segment(a, b, y0, y1, t=2.4, walk=True):
    """A piece of curtain wall from ``a`` to ``b``: a core, faces of stone
    blocks on both sides, a walk on top with a crenellated parapet outside
    and a low one inside."""
    L, d, n = outward(a, b)
    add.push()
    add.cuboid([L / 2, (y0 + y1) / 2, 0], [L, y1 - y0, t], P["mortar"])
    stone_face(L, y0, y1, t / 2, 0.22, "stone", seed=int(a[0] + a[2]))
    stone_face(L, y0, y1, -t / 2, -0.22, "stone_dark", seed=int(a[0] - a[2]))
    if walk:
        add.cuboid([L / 2, y1 + 0.15, 0], [L, 0.3, t + 0.5], P["mortar"])
        flagstones(0, L, -t / 2 - 0.25, t / 2 + 0.25, y1 + 0.3)
        merlons(L, y1 + 0.3, t / 2 - 0.5, t / 2 + 0.25)
        add.cuboid([L / 2, y1 + 0.6, -t / 2 + 0.2], [L, 0.6, 0.4], P["stone"])
    M = add.pop()
    add.mesh(frame_to(M, [a[0], 0, a[2]], d, n))


def cone_roof(centre, y, r, h, k, tiles=True, color=None):
    """A conical roof of individual slates (or a plain ``color`` cone)."""
    cx, cz = centre[0], centre[2]
    if color is not None:
        add.cone([cx, y, cz], [cx, y + h, cz], r, k, color)
        add.sphere([cx, y + h + 0.3, cz], 0.35, 8, P["gold"])
        return
    add.cone([cx, y, cz], [cx, y + h, cz], r, k, P["slate"])
    if not tiles:
        return
    rows = max(4, int(h / 0.45))
    for j in range(rows):
        t0, t1 = j / float(rows), (j + 1) / float(rows)
        r0, r1 = r * (1 - t0), r * (1 - t1)
        yy0, yy1 = y + h * t0, y + h * t1
        n = max(8, int(2 * add.pi * r0 / 0.42))
        for i in range(n):
            a0 = 2 * add.pi * (i + (0.5 if j % 2 else 0)) / n
            a1 = 2 * add.pi * (i + 0.92 + (0.5 if j % 2 else 0)) / n
            q = [[cx + (r0 + 0.05) * add.cos(a0), yy0 - 0.06, cz + (r0 + 0.05) * add.sin(a0)],
                 [cx + (r0 + 0.05) * add.cos(a1), yy0 - 0.06, cz + (r0 + 0.05) * add.sin(a1)],
                 [cx + (r1 + 0.05) * add.cos(a1), yy1, cz + (r1 + 0.05) * add.sin(a1)],
                 [cx + (r1 + 0.05) * add.cos(a0), yy1, cz + (r1 + 0.05) * add.sin(a0)]]
            add.polygon(q[::-1], shade_of("slate", int(hash2(i, j, 8) * 3)))
    add.cone([cx, y + h - 0.5, cz], [cx, y + h + 0.05, cz], 0.25, 8, P["slate"])


def tile_face(A, B, C, D, blocked=None, size=None, colours="spire"):
    """Cover the planar face A-B (eave) .. D-C (ridge; C may equal D for a
    triangle) with rows of tiles, each a thin two-sided sheet lifted a
    little off the face; ``blocked(x, z)`` says where to leave tiles out.
    ``colours`` names a shaded palette colour: "spire" for the clay tiles
    of the palace, "slate" for the towers."""
    tw, th = size or TILE
    n = vunit(vcross(vsub(B, A), vsub(D, A)))
    rows = max(1, int(vlen(vsub(D, A)) / th))
    for j in range(rows):
        t0, t1 = j / float(rows), (j + 1) / float(rows)
        L0 = [A[k] + (D[k] - A[k]) * t0 for k in range(3)]
        R0 = [B[k] + (C[k] - B[k]) * t0 for k in range(3)]
        L1 = [A[k] + (D[k] - A[k]) * t1 for k in range(3)]
        R1 = [B[k] + (C[k] - B[k]) * t1 for k in range(3)]
        width = vlen(vsub(R0, L0))
        cols = max(1, int(width / tw))
        for i in range(cols):
            u0, u1 = i / float(cols), (i + 1) / float(cols)
            q = [[L0[k] + (R0[k] - L0[k]) * u0 for k in range(3)], [L0[k] + (R0[k] - L0[k]) * u1 for k in range(3)],
                 [L1[k] + (R1[k] - L1[k]) * u1 for k in range(3)], [L1[k] + (R1[k] - L1[k]) * u0 for k in range(3)]]
            if vlen(vsub(q[2], q[3])) < 0.01 and vlen(vsub(q[1], q[0])) < 0.01:
                continue
            cxz = ((q[0][0] + q[2][0]) / 2, (q[0][2] + q[2][2]) / 2)
            if blocked and blocked(*cxz):
                continue
            colour = shade_of(colours, int(hash2(i, j, 5) * 3))
            lifted = [[p[k] + n[k] * 0.06 for k in range(3)] for p in q]
            if vlen(vsub(lifted[2], lifted[3])) < 0.01:                        # a triangle at the apex
                lifted = lifted[:3]
            sheet(lifted[::-1], colour, 0.05)


TILE = (0.28, 0.25)


def radial_cutter(cx, cz, a, y0, w, h, r_from, r_to):
    """An arched solid pointing outwards from (cx, cz) at angle ``a``, from
    radius ``r_from`` to ``r_to``: subtract it from a drum to cut an arched
    door or a window ``w`` wide and ``h`` tall with its sill on ``y0``."""
    M = add.make(add.prism, [[y, s] for s, y in arch_profile(y0, w, h)], r_to - r_from, None,
                 ((r_from + r_to) / 2, 0, 0), (1, 0, 0))
    return add.move(add.rotateY(M, -a), [cx, 0, cz])


def tex_round(M, name, cx, cz, r, period=3.0):
    """The core of a round tower is plain mortar; the stone blocks go on top."""
    return add.color(M, P["mortar"])


def ring_block(cx, cz, r0, r1, a0, a1, y0, y1, color, arcs=2):
    """A block of a round wall: the piece of the ring r0..r1 between the
    angles a0 and a1, from y0 up to y1 -- a chess rook's masonry."""
    pts = [(cx + r0 * add.cos(a0 + (a1 - a0) * j / arcs), cz + r0 * add.sin(a0 + (a1 - a0) * j / arcs)) for j in range(arcs + 1)]
    pts += [(cx + r1 * add.cos(a1 - (a1 - a0) * j / arcs), cz + r1 * add.sin(a1 - (a1 - a0) * j / arcs)) for j in range(arcs + 1)]
    add.mesh(solid(pts, y0, y1, color))


def stone_ring(cx, cz, r, y0, y1, name="stone", skip=()):
    """Courses of stone blocks round a drum of radius ``r``, every block a
    piece of the ring.  ``skip`` lists the openings as ``(angle,
    half_width_angle, y_bottom, y_top[, arch_radius])``: the blocks are
    fitted round them -- cut short at the jambs, a sliver over the sill
    and under the head, and stepped round an arched head -- rather than
    left out, the way a mason closes up to a window."""
    bl, bh = BLOCK
    rows = int((y1 - y0) / bh)
    for j in range(rows):
        n = max(8, int(2 * add.pi * r / bl))
        for i in range(n):
            a = 2 * add.pi * (i + (0.5 if j % 2 else 0)) / n
            y = y0 + (j + 0.5) * bh
            half = add.pi / n
            spans = [(a - half + 0.03 / r, a + half - 0.03 / r, y - bh / 2 + 0.03, y + bh / 2 - 0.03)]
            for o in skip:
                sa, sw, sy0, sy1 = o[:4]
                sw += 0.06 / r                                             # room for the jamb stones
                out = []
                for pa0, pa1, py0, py1 in spans:
                    da = (sa - (pa0 + pa1) / 2 + add.pi) % (2 * add.pi) - add.pi     # the opening, seen from this block
                    oa0, oa1 = (pa0 + pa1) / 2 + da - sw, (pa0 + pa1) / 2 + da + sw
                    oy0, oy1 = sy0 - 0.06, sy1 + 0.06
                    if len(o) > 4 and py0 >= sy1 - o[4]:                   # over the springing line: the round head
                        dy = py0 - (sy1 - o[4])
                        if dy >= o[4]:
                            out.append((pa0, pa1, py0, py1))
                            continue
                        ww = (add.sqrt(o[4] ** 2 - dy * dy) + 0.06) / r
                        oa0, oa1 = (pa0 + pa1) / 2 + da - ww, (pa0 + pa1) / 2 + da + ww
                        oy0 = sy1 - o[4]
                    if pa1 <= oa0 or pa0 >= oa1 or py1 <= oy0 or py0 >= oy1:
                        out.append((pa0, pa1, py0, py1))
                        continue
                    if oa0 > pa0:
                        out.append((pa0, oa0, py0, py1))
                    if oa1 < pa1:
                        out.append((oa1, pa1, py0, py1))
                    ma0, ma1 = max(pa0, oa0), min(pa1, oa1)
                    if oy0 > py0:
                        out.append((ma0, ma1, py0, oy0))
                    if oy1 < py1:
                        out.append((ma0, ma1, oy1, py1))
                spans = out
            for pa0, pa1, py0, py1 in spans:
                if (pa1 - pa0) * r >= 0.15 and py1 - py0 >= 0.1:
                    ring_block(cx, cz, r + 0.02, r + 0.24, pa0, pa1, py0, py1, pick(name, i, j))


def rook_top(cx, cz, r, r_in, y1, k, name="stone"):
    """The top of a round tower as a chess rook has it: a course of corbel
    blocks, a ring, and merlons with embrasures between them -- every
    piece a sector of the ring, nothing square."""
    for i in range(k):                                                          # corbels
        a = 2 * add.pi * (i + 0.5) / k
        ring_block(cx, cz, r - 0.1, r + 0.7, a - add.pi / k * 0.42, a + add.pi / k * 0.42, y1 - 1.0, y1, P["stone_dark"])
    add.pipe([cx, y1, cz], [cx, y1 + 0.35, cz], r + 0.7, r_in, k, P["stone_dark"])
    m = k // 2
    for i in range(m):                                                          # merlons, an embrasure between each pair
        a = 2 * add.pi * (i + 0.5) / m
        ring_block(cx, cz, r + 0.1, r + 0.7, a - add.pi / m * 0.5, a + add.pi / m * 0.5, y1 + 0.35, y1 + 1.55, pick(name, i, 1))


HEADROOM = 9 * 0.36                                    # the platform stays open over the last 9 steps: 9 x 0.28 - 0.35 = 2.17 m of headroom


def stair_tower(cx, cz, y_floor, r_out, stops, y_top, start=0.0, rise=0.28, color="stone_dark", r_of=None):
    """A spiral stair from ``y_floor`` to ``y_top`` with a landing at every
    stop ``(level, a_from, a_to)`` -- a sector of floor from angle a_from to
    a_to at that level, where a door leads out.  Returns the angle where
    the stair arrives at the top.  The steps are steep (0.28 m) and narrow
    (0.36 rad) so that one turn climbs 4.9 m: the stair passes over a
    doorway with room to spare."""
    a, y = start, y_floor
    for level, a_from, a_to in list(stops) + [(y_top, None, None)]:
        n = max(1, int(round((level - y) / rise)))
        if a_from is None:
            sweep = 0.36
            a_from = a + n * sweep
        else:
            delta = (a_from - a) % (2 * add.pi)
            m = min(range(8), key=lambda m: abs(delta + 2 * add.pi * m - n * 0.36))
            sweep = (delta + 2 * add.pi * m) / n
        spiral_stair(cx, cz, y, level, r_out, start=a, sweep=sweep, rise=rise, color=color, newel=False, r_of=r_of)
        a, y = a_from, level
        if a_to is not None:
            pts = [(cx, cz)]
            for aa in outline_angles(a_from, a_to, max(3, int((a_to - a_from) / 0.25)), r_of):
                rr = r_of(aa) if r_of else r_out
                pts.append((cx + rr * add.cos(aa), cz + rr * add.sin(aa)))
            add.mesh(solid(pts, level - rise, level, shade_of(color, 1)))
            a = a_to
    add.cylinder([cx, y_floor, cz], [cx, y_top + 1.2, cz], 0.35, k_(8), P["stone"])      # the newel post
    return a


def guard_wall(cx, cz, a, r0, r1, y, side=-1, h=1.0, t=0.35, name="stone"):
    """A low stone wall where a floor ends in a drop into a stairwell:
    along the radius at angle ``a`` from ``r0`` to ``r1``, standing on
    ``y``, on the ``side`` of that radius where the floor is (-1: towards
    smaller angles).  Two courses of blocks round a mortar core under a
    coping of dark stone -- the tower's own masonry, hip-high."""
    dx, dz = add.cos(a), add.sin(a)
    lx, lz = -dz * side, dx * side                                         # across the wall, into the floor

    def block(u0, u1, w0, w1, y0, y1, color):
        add.mesh(solid([(cx + dx * u + lx * w, cz + dz * u + lz * w) for u, w in ((u0, w0), (u1, w0), (u1, w1), (u0, w1))],
                       y0, y1, color))
    block(r0, r1, 0.02, t - 0.02, y, y + h - 0.1, P["mortar"])             # the core ...
    bh = (h - 0.12) / 2
    for j in range(2):                                                     # ... two courses of blocks, the joints staggered ...
        u, i = r0 - (BLOCK[0] / 2 if j else 0.0), 0
        while u < r1:
            u0, u1 = max(u, r0), min(u + BLOCK[0], r1)
            if u1 - u0 >= 0.15:
                block(u0 + 0.02, u1 - 0.02, 0.0, t, y + j * bh + 0.02, y + (j + 1) * bh - 0.02, pick(name, i, j))
            u += BLOCK[0]
            i += 1
    block(r0, r1, -0.04, t + 0.04, y + h - 0.12, y + h, P["stone_dark"])   # ... and the coping


def guard_arc(cx, cz, r0, r1, a0, a1, y, h=1.0, name="stone"):
    """The same low wall bent round the centre: the ring r0..r1 from angle
    ``a0`` to ``a1`` -- along the inner edge of a stairwell that hugs the wall."""
    r = (r0 + r1) / 2
    arcs = max(2, int((a1 - a0) * r1 / 0.3))
    ring_block(cx, cz, r0 + 0.02, r1 - 0.02, a0, a1, y, y + h - 0.1, P["mortar"], arcs)
    bh = (h - 0.12) / 2
    n = max(1, int(round((a1 - a0) * r / BLOCK[0])))
    step = (a1 - a0) / n
    for j in range(2):
        for i in range(n + 1):
            b0, b1 = max(a0, a0 + (i - 0.5 * j) * step), min(a1, a0 + (i + 1 - 0.5 * j) * step)
            if (b1 - b0) * r >= 0.15:
                ring_block(cx, cz, r0, r1, b0 + 0.02 / r, b1 - 0.02 / r, y + j * bh + 0.02, y + (j + 1) * bh - 0.02,
                           pick(name, i, j), max(1, int((b1 - b0) * r1 / 0.3)))
    ring_block(cx, cz, r0 - 0.04, r1 + 0.04, a0, a1, y + h - 0.12, y + h, P["stone_dark"], arcs)


def platform(cx, cz, r, y, thick, hole_from, hole_to, color=None, r_of=None):
    """A platform -- round, or of the outline ``r_of`` -- with a sector left
    open where a stair arrives.  The top step is flush with the platform at
    ``hole_to``: that is the way out, and it stays open.  At ``hole_from``
    the stair runs two metres below the edge: a low stone wall guards it."""
    color = color or P["stone_dark"]
    pts = [(cx, cz)]
    for a in outline_angles(hole_to, hole_to + 2 * add.pi - (hole_to - hole_from), 40, r_of):
        rr = r_of(a) if r_of else r
        pts.append((cx + rr * add.cos(a), cz + rr * add.sin(a)))
    add.mesh(solid(pts, y - thick, y, color))
    guard_wall(cx, cz, hole_from, 0.0, (r_of(hole_from) if r_of else r) + 0.15, y)    # from the newel to the parapet ring


def round_tower(centre, y0, y1, r, doors, walk=None, y_floor=None, roof_h=8.0, roof_color=None,
                slits=True, lantern=True, cutters=(), name="stone", windows=(), blocks=True, walls=(), stops=None):
    """A hollow round tower on ``centre``: a drum of stone with a ground
    door and doors onto the wall walk, arrow slits, a spiral stair with
    landings, a lookout platform on top with a parapet and a roof on posts.

    ``doors`` is a list of ``(angle, level)`` doorways cut through the drum
    (the level is the floor of the doorway; a doorway may add its own
    ``width, height`` -- the default is DOOR_W x DOOR_H, man-high and more);
    ``walk`` is ``(level, a_from, a_to)`` -- the landing at the wall walk
    with doors at both ends."""
    cx, cz = centre[0], centre[2]
    r_in = r - 1.0
    y_floor = G + 0.1 if y_floor is None else y_floor
    drum = add.make(add.pipe, [cx, y0, cz], [cx, y1, cz], r, r_in, k_(24))
    holes = []
    skip = []
    for d in doors:
        a, level = d[0], d[1]
        w, h = d[2:4] if len(d) > 2 else (DOOR_W, DOOR_H)
        holes.append(radial_cutter(cx, cz, a, level, w, h, r_in - 0.5, r + 0.5))
        skip.append((a, w / 2 / r, level, level + h, w / 2))
    for a, level, w, h in windows:
        holes.append(radial_cutter(cx, cz, a, level, w, h, r_in - 0.5, r + 0.5))
        skip.append((a, w / 2 / r, level, level + h, w / 2))
    if slits:
        for j in range(2):
            for i in range(4):
                a = 2 * add.pi * i / 4 + add.pi / 4 + j * add.pi / 8
                level = y_floor + 3.5 + 4.5 * j
                holes.append(radial_cutter(cx, cz, a, level, 0.28, 1.3, r_in - 0.5, r + 0.5))
                skip.append((a, 0.14 / r, level, level + 1.3, 0.14))
    drum = add.difference(drum, *(holes + list(cutters)))
    add.mesh(tex_round(drum, name, cx, cz, r, 3.0))
    if blocks:
        for a in walls:                                                         # no blocks where a wall joins
            skip.append((a, 1.6 / r, y0, y1))
        stone_ring(cx, cz, r, max(y0, G - 0.5), y1 - 1.0, name, skip)
    add.cylinder([cx, y_floor - 0.3, cz], [cx, y_floor, cz], r_in + 0.2, k_(16), P["stone_dark"])
    if stops is None:
        stops = [walk] if walk else []
    arrive = stair_tower(cx, cz, y_floor, r_in - 0.05, stops, y1, start=doors[0][0] + 1.0)
    platform(cx, cz, r_in + 0.2, y1, 0.35, arrive - HEADROOM, arrive)
    k = k_(24)
    rook_top(cx, cz, r, r_in + 0.2, y1, k, name)
    if roof_h:
        base = y1 + 0.35
        if lantern:                                                             # stout oak posts, a ring beam, braces
            for i in range(8):
                a = 2 * add.pi * i / 8 + add.pi / 8
                px, pz = cx + (r - 0.35) * add.cos(a), cz + (r - 0.35) * add.sin(a)
                add.cuboid([px, base + 1.4, pz], [0.42, 2.8, 0.42], P["wood_dark"])
                add.cuboid([px, base + 0.12, pz], [0.6, 0.24, 0.6], P["stone_dark"])           # a stone footing
                for s in (-1, 1):                                                              # knee braces to the beam
                    q = [cx + (r - 0.35) * add.cos(a + s * 0.28), base + 2.75, cz + (r - 0.35) * add.sin(a + s * 0.28)]
                    add.beam([px, base + 1.8, pz], q, 0.14, 0.14, P["wood_dark"])
            add.pipe([cx, base + 2.8, cz], [cx, base + 3.15, cz], r + 0.9, r - 0.7, k, P["wood_dark"])
            base += 3.15
        cone_roof([cx, 0, cz], base, r + 0.9, roof_h, k, tiles=(roof_color is None), color=roof_color)
    return arrive


def square_tower(centre, y0, y1, w, doors, walk_stops, roof_h, name="stone", windows=()):
    """A hollow square tower: four walls of stone blocks, arched doors, a
    spiral stair with landings, a top platform with a parapet and a
    pyramid roof on posts.  ``doors``: (side, level) with side 0..3 = +x,
    +z, -x, -z; ``walk_stops``: (level, a_from, a_to) landings."""
    cx, cz = centre[0], centre[2]
    t = 1.0
    shell = add.make(add.cuboid, [cx, (y0 + y1) / 2, cz], [w, y1 - y0, w])
    inner = add.make(add.cuboid, [cx, (y0 + y1) / 2 + 0.5, cz], [w - 2 * t, y1 - y0, w - 2 * t])
    holes = [inner]
    skip = {0: [], 1: [], 2: [], 3: []}
    for d in doors:
        side, level = d[0], d[1]
        dw, dh = d[2:4] if len(d) > 2 else (DOOR_W, DOOR_H)
        a = side * add.pi / 2
        holes.append(radial_cutter(cx, cz, a, level, dw, dh, w / 2 - t - 0.5, w / 2 + 0.5))
        skip[side].append((w / 2 - dw / 2, w / 2 + dw / 2, level, level + dh))
    for side, level, ww, h in windows:
        a = side * add.pi / 2
        holes.append(radial_cutter(cx, cz, a, level, ww, h, w / 2 - t - 0.5, w / 2 + 0.5))
        skip[side].append((w / 2 - ww / 2, w / 2 + ww / 2, level, level + h))
    shell = add.difference(shell, *holes)
    add.mesh(add.color(shell, P["mortar"]))
    for side in range(4):                                                       # stone faces
        add.push()
        stone_face(w, max(y0, G - 0.5), y1 - 0.9, w / 2, 0.22, name, seed=side + int(cx), skip=skip[side])
        M = add.move(add.pop(), [-w / 2, 0, 0])                                 # built facing +z ...
        M = add.rotateY(M, add.pi / 2 - side * add.pi / 2)                       # ... turned to face side 0..3
        add.mesh(add.move(M, [cx, 0, cz]))
    add.cuboid([cx, G - 0.15, cz], [w - 2 * t + 0.4, 0.3, w - 2 * t + 0.4], P["stone_dark"])
    arrive = stair_tower(cx, cz, G, w / 2 - t - 0.05, walk_stops, y1, start=doors[0][0] * add.pi / 2 + 1.0,
                         r_of=square_outline(w / 2 - t - 0.05))                  # the steps reach into the corners
    platform(cx, cz, w / 2 - t + 0.15, y1, 0.35, arrive - HEADROOM, arrive, r_of=square_outline(w / 2 - t + 0.15))
    for i in range(int(w / 0.9)):                                                # corbels
        s = -w / 2 + 0.45 + i * 0.9
        for dx, dz in ((s, w / 2 + 0.3), (s, -w / 2 - 0.3), (w / 2 + 0.3, s), (-w / 2 - 0.3, s)):
            add.cuboid([cx + dx, y1 - 0.5, cz + dz], [0.5, 0.9, 0.5], P["stone_dark"])
    ring = add.make(add.cuboid, [cx, y1 + 0.2, cz], [w + 1.4, 0.4, w + 1.4], P["stone_dark"])
    add.mesh(add.difference(ring, add.make(add.cuboid, [cx, y1 + 0.2, cz], [w - 2 * t + 0.3, 1, w - 2 * t + 0.3])))
    ww = w + 1.4
    side = add.make(merlons, ww, 0.4, 0, 0.5)
    for i in range(4):
        add.mesh(add.move(add.rotateY(side, i * add.pi / 2, [ww / 2, 0, ww / 2]), [cx - ww / 2, y1, cz - ww / 2]))
    base = y1 + 0.4
    for sx in (-1, 1):                                                          # posts and the roof
        for sz in (-1, 1):
            add.cuboid([cx + sx * (w / 2 - 0.4), base + 1.4, cz + sz * (w / 2 - 0.4)], [0.3, 2.8, 0.3], P["wood_dark"])
    add.cuboid([cx, base + 2.9, cz], [w + 0.8, 0.25, w + 0.8], P["wood_dark"])
    e = w + 0.6
    add.pyramid([cx, base + 3.0 + e / 2, cz], e, roof_h, P["slate"])
    top = base + 3.0 + roof_h
    apex = [cx, top, cz]
    f = 1 - 0.55 / roof_h                                                       # the slates stop under the cap: each face's are lifted
    hip = add.sqrt(2) * e / 2                                                   # off it along its own normal, so their tips would not
    m = [roof_h / add.sqrt(roof_h ** 2 + hip ** 2), hip / add.sqrt(roof_h ** 2 + hip ** 2)]    # meet at the apex
    for i in range(4):                                                          # slates on the four faces
        a0, a1 = i * add.pi / 2, (i + 1) * add.pi / 2
        c0 = [cx + e / 2 * add.sqrt(2) * add.cos(a0 + add.pi / 4), base + 3.0, cz + e / 2 * add.sqrt(2) * add.sin(a0 + add.pi / 4)]
        c1 = [cx + e / 2 * add.sqrt(2) * add.cos(a1 + add.pi / 4), base + 3.0, cz + e / 2 * add.sqrt(2) * add.sin(a1 + add.pi / 4)]
        u0 = [c0[k] + (apex[k] - c0[k]) * f for k in range(3)]
        u1 = [c1[k] + (apex[k] - c1[k]) * f for k in range(3)]
        tile_face(c1, c0, u0, u1, size=(0.45, 0.4), colours="slate")
        ca, sa = add.cos(a0 + add.pi / 4), add.sin(a0 + add.pi / 4)             # a lead roll over the hip, where the
        lift = [m[0] * ca * 0.07, m[1] * 0.07, m[0] * sa * 0.07]                # slates of two faces meet
        tip = [c0[k] + (apex[k] - c0[k]) * 0.95 for k in range(3)]
        add.cylinder([c0[k] + lift[k] for k in range(3)], [tip[k] + lift[k] for k in range(3)], 0.09, 6, P["iron"])
    add.pyramid([cx, top - 0.1, cz], 1.2, 1.2, P["iron"])                       # a lead cap over the apex, and a finial
    add.cylinder([cx, top + 0.4, cz], [cx, top + 1.5, cz], 0.05, 8, P["iron"])
    add.sphere([cx, top + 1.55, cz], 0.14, 8, P["gold"])
    return arrive


# --------------------------------------------------------------------------
#  1. The hill, the lake and the moat
# --------------------------------------------------------------------------
G = 14.0                                               # the plateau: ground level inside the walls
PLATEAU = G
R_OCT = 50.0 / add.cos(add.pi / 8)                     # the curtain wall: an octagon, apothem 50, corner radius R_OCT
PHI = [add.pi / 8 + k * add.pi / 4 for k in range(8)]
CORNERS = [[R_OCT * add.cos(a), 0, R_OCT * add.sin(a)] for a in PHI]
TOWER_R = 4.5


def octagon_r(x, z):
    """The 'radius' of a point in the octagon: 50 on the curtain wall."""
    return max(x * add.cos(a) + z * add.sin(a) for a in (k * add.pi / 4 for k in range(8)))


def near_corner(x, z, margin=0.0):
    """Within one of the eight corner towers (plus ``margin``)."""
    return any((x - c[0]) ** 2 + (z - c[2]) ** 2 < (TOWER_R + margin) ** 2 for c in CORNERS)


def octagon_outline(apothem):
    """r(angle) of the octagon with the given apothem, corners on PHI."""
    return lambda a: apothem / add.cos(((a + add.pi / 8) % (add.pi / 4)) - add.pi / 8)
WATER_Y = 1.5
WORLD = 300.0                                          # the lake is this wide
BOTTOM = -6.0                                          # the underside of the land
MOAT = (-20, 20, 56, 64)                               # x0, x1, z0, z1 (on grid lines)
MOAT_Y = 9.0


def ground(x, z):
    """Height of the land: a plateau, a slope, a cliff and the lake bed."""
    r = add.sqrt(x * x + z * z)
    if r <= 58:
        return PLATEAU
    cliff = add.clamp((-x / max(r, 1) - 0.55) / 0.3)      # the west side is a cliff
    run = add.lerp(36.0, 14.0, cliff)
    t = add.clamp((r - 58) / run)
    y = PLATEAU - 13.0 * t * t * (3 - 2 * t)
    if r > 58 + run:                                    # the shore and the lake bed
        y = 1.0 - 0.18 * (r - 58 - run)
    return max(y, -4.5) + 0.35 * add.sin(x / 7.0) * add.cos(z / 9.0) * (1 if r > 58 else 0)


def ground_color(x, z):
    y = ground(x, z)
    slope = abs(ground(x + 1, z) - y) + abs(ground(x, z + 1) - y)
    if y < WATER_Y + 0.4:
        return P["lakebed"] if y < WATER_Y - 0.5 else P["sand"]
    if slope > 0.9:
        return P["rock"]
    patch = add.sin(x / 9.0) * add.cos(z / 11.0) + 0.5 * add.sin(x / 4.0 + z / 5.0)
    return P["grass_dry"] if patch > 0.55 else P["grass"]


N_GROUND = 800                                         # cells of 0.375 units
land = add.Mesh()
index = {}


def land_vertex(i, j):
    if (i, j) not in index:
        x, z = -WORLD / 2 + WORLD * i / N_GROUND, -WORLD / 2 + WORLD * j / N_GROUND
        index[(i, j)] = land.add_vertex([x, ground(x, z), z])
    return index[(i, j)]


cell = WORLD / N_GROUND
for i in range(N_GROUND):
    for j in range(N_GROUND):
        x, z = -WORLD / 2 + (i + 0.5) * cell, -WORLD / 2 + (j + 0.5) * cell
        if MOAT[0] < x < MOAT[1] and MOAT[2] < z < MOAT[3]:
            continue                                   # the moat is dug out here
        land.add_face([land_vertex(i, j), land_vertex(i, j + 1),
                       land_vertex(i + 1, j + 1), land_vertex(i + 1, j)], ground_color(x, z))
# the land is a closed block: four sides down to BOTTOM, and an underside
edges = ([(0, j) for j in range(N_GROUND + 1)],                          # x = -150, along z
         [(i, N_GROUND) for i in range(N_GROUND + 1)],                   # z = +150, along x
         [(N_GROUND, j) for j in reversed(range(N_GROUND + 1))],         # x = +150
         [(i, 0) for i in reversed(range(N_GROUND + 1))])                # z = -150
for chain in edges:
    for (i0, j0), (i1, j1) in zip(chain, chain[1:]):
        a, b = land_vertex(i0, j0), land_vertex(i1, j1)
        pa, pb = land.V[a], land.V[b]
        land.add_polygon([[pa[0], BOTTOM, pa[2]], [pb[0], BOTTOM, pb[2]], pb, pa], P["sand"])
land.add_polygon([[-WORLD / 2, BOTTOM, -WORLD / 2], [-WORLD / 2, BOTTOM, WORLD / 2],
                  [WORLD / 2, BOTTOM, WORLD / 2], [WORLD / 2, BOTTOM, -WORLD / 2]], P["sand"])
add.mesh(add.fix_normals(land))
land, index = None, None                               # free the memory
# the moat: a stone-lined pit with a kerb, and a floor of rock
for x0, x1, z0, z1 in ((MOAT[0] - 1, MOAT[0], MOAT[2] - 1, MOAT[3] + 1), (MOAT[1], MOAT[1] + 1, MOAT[2] - 1, MOAT[3] + 1),
                       (MOAT[0], MOAT[1], MOAT[2] - 1, MOAT[2]), (MOAT[0], MOAT[1], MOAT[3], MOAT[3] + 1)):
    add.cuboid([(x0 + x1) / 2, (MOAT_Y - 0.5 + PLATEAU + 0.3) / 2, (z0 + z1) / 2],
               [x1 - x0, PLATEAU + 0.3 - MOAT_Y + 0.5, z1 - z0], P["stone_dark"])
add.cuboid([0, MOAT_Y - 0.25, (MOAT[2] + MOAT[3]) / 2], [MOAT[1] - MOAT[0], 0.5, MOAT[3] - MOAT[2]], P["rock"])
flush("hill, lake bed and moat")


# the water: a closed transparent block whose top has gentle ripples and
# whose sides go down below the lake bed, so nothing hangs in the air
def ripple(x, z):
    return WATER_Y + 0.08 * add.sin(x / 3.0 + z / 5.0) + 0.05 * add.cos(z / 2.5)


N_WATER = 400
W_EDGE = WORLD / 2 - 0.3                               # a little inside the land's sides
W_BOTTOM = -5.2
water = add.Mesh()
windex = {}


def water_vertex(i, j):
    if (i, j) not in windex:
        x, z = -W_EDGE + 2 * W_EDGE * i / N_WATER, -W_EDGE + 2 * W_EDGE * j / N_WATER
        windex[(i, j)] = water.add_vertex([x, ripple(x, z), z])
    return windex[(i, j)]


for i in range(N_WATER):
    for j in range(N_WATER):
        water.add_face([water_vertex(i, j), water_vertex(i, j + 1),
                        water_vertex(i + 1, j + 1), water_vertex(i + 1, j)], WATER)
edges = ([(0, j) for j in range(N_WATER + 1)], [(i, N_WATER) for i in range(N_WATER + 1)],
         [(N_WATER, j) for j in reversed(range(N_WATER + 1))], [(i, 0) for i in reversed(range(N_WATER + 1))])
for chain in edges:
    for (i0, j0), (i1, j1) in zip(chain, chain[1:]):
        pa, pb = water.V[water_vertex(i0, j0)], water.V[water_vertex(i1, j1)]
        water.add_polygon([[pa[0], W_BOTTOM, pa[2]], [pb[0], W_BOTTOM, pb[2]], pb, pa], WATER)
water.add_polygon([[-W_EDGE, W_BOTTOM, -W_EDGE], [-W_EDGE, W_BOTTOM, W_EDGE],
                   [W_EDGE, W_BOTTOM, W_EDGE], [W_EDGE, W_BOTTOM, -W_EDGE]], WATER)
add.mesh(add.fix_normals(water))
water, windex = None, None
add.cuboid([0, (MOAT_Y + 12.5) / 2, (MOAT[2] + MOAT[3]) / 2],
           [MOAT[1] - MOAT[0], 12.5 - MOAT_Y, MOAT[3] - MOAT[2]], WATER)   # the moat
flush("water")


# under the water: pebbles, fish, reeds, lily pads and a sunken rowing boat
def fish(at, facing, color, size=1.0):
    add.push()
    add.mesh(add.stretch(add.make(add.sphere, [0, 0, 0], 0.5, 8, color), [1.6, 0.9, 0.45], (0, 0, 0)))
    add.mesh(add.make(add.prism, [[0, 0], [0.6, 0.35], [0.6, -0.35]], 0.06, color, (0.75, 0, 0), (0, 0, 1)))
    add.mesh(add.make(add.prism, [[0, 0], [-0.3, 0.3], [0.2, 0.3]], 0.04, color, (0.1, 0.4, 0), (0, 0, 1)))     # dorsal fin
    for s in (-1, 1):
        add.sphere([-0.45, 0.12, s * 0.2], 0.06, 4, P["white"], 0)
        add.sphere([-0.5, 0.12, s * 0.22], 0.03, 3, P["black"], 0)
    M = add.pop()
    add.mesh(add.move(add.rotateY(add.stretch(M, [size, size, size], (0, 0, 0)), facing), at))


# a cobblestone template -- a rounded dome turned on the lathe, 84 faces -- copied thousands of times
_dome = [[0.2, -0.02], [0.2, 0.03], [0.185, 0.07], [0.15, 0.1], [0.09, 0.118], [0.0, 0.122]]
COBBLE = add.make(add.revolve, lambda t: _dome[min(5, int(round(t)))], [0, 0, 0], [0, 1, 0], 0, 5, 5, 14, P["stone_dark"])
COBBLES = [add.color(add.stretch(COBBLE, [sx, 1.0, sz], (0, 0, 0)), shade_of("stone_dark", i % 3))
           for i, (sx, sz) in enumerate(((0.95, 0.95), (0.95, 0.8), (0.8, 0.95), (0.9, 0.9), (0.82, 0.88), (0.88, 0.82)))]


def cobble_area(inside, x0, x1, z0, z1, y, step=0.44, scale=1.0, seed=0):
    """Cobbles on a jittered grid over the rectangle x0..x1, z0..z1 where
    ``inside(x, z)`` is true.  Stones of radius 0.2 * scale at ``step`` *
    scale apart with a little jitter never touch each other."""
    n = 0
    i = 0
    x = x0
    while x < x1:
        j = 0
        z = z0 + (step * scale / 2 if i % 2 else 0)
        while z < z1:
            xx = x + (hash2(i, j, seed) - 0.5) * 0.04 * scale
            zz = z + (hash2(i, j, seed + 1) - 0.5) * 0.04 * scale
            if inside(xx, zz):
                stone = COBBLES[int(hash2(i, j, seed + 2) * 6) % 6]
                if scale != 1.0:
                    stone = add.stretch(stone, [scale, scale, scale], (0, 0, 0))
                add.mesh(add.move(add.rotateY(stone, hash2(i, j, seed + 3) * 6.28), [xx, y, zz]))
                n += 1
            z += step * scale
            j += 1
        x += step * scale
        i += 1
    return n


def flag_path(points, width=2.4, y=None, row=0.6, cell=0.45, gap=0.06, thick=0.07, avoid=None):
    """A path of split flagstones along the polyline ``points`` (in XZ):
    rows of irregular flat stones across the width, staggered, each a
    little inside its cell so that no two stones touch.  At a bend the
    stones of the next leg take over."""
    y = G + 0.02 if y is None else y
    legs = []
    for k in range(len(points) - 1):
        a, b = points[k], points[k + 1]
        d = vunit([b[0] - a[0], 0, b[1] - a[1]])
        legs.append((a, b, d, vlen([b[0] - a[0], 0, b[1] - a[1]])))

    def on_other_leg(px, pz, me):
        for k, (a, b, d, L) in enumerate(legs):
            if k == me:
                continue
            t = (px - a[0]) * d[0] + (pz - a[1]) * d[2]
            if -0.1 < t < L + 0.1:
                side = abs((px - a[0]) * d[2] - (pz - a[1]) * d[0])
                if side < width / 2 - 0.02 and k > me:
                    return True
        return False

    count_ = 0
    for k, (a, b, d, L) in enumerate(legs):
        n = [d[2], 0, -d[0]]
        cols = max(1, int(width / cell))
        cw = width / cols
        rows = max(1, int(L / row))
        rl = L / rows
        for i in range(rows):
            for j in range(cols):
                t0, t1 = i * rl + gap / 2, (i + 1) * rl - gap / 2
                u0, u1 = -width / 2 + j * cw + gap / 2, -width / 2 + (j + 1) * cw - gap / 2
                if (i + j) % 2:                                     # every other stone is two cells long
                    if j % 2:
                        continue
                    if j + 1 < cols:
                        u1 = -width / 2 + (j + 2) * cw - gap / 2
                cx_, cz_ = a[0] + d[0] * (t0 + t1) / 2 + n[0] * (u0 + u1) / 2, a[1] + d[2] * (t0 + t1) / 2 + n[2] * (u0 + u1) / 2
                if on_other_leg(cx_, cz_, k) or (avoid and avoid(cx_, cz_)):
                    continue
                pts = []
                for (tt, uu, jx, jz) in ((t0, u0, 1, 1), (t1, u0, -1, 1), (t1, u1, -1, -1), (t0, u1, 1, -1)):
                    tt += jx * hash2(i, j, 31 + k) * 0.05
                    uu += jz * hash2(i, j, 41 + k) * 0.05
                    pts.append((a[0] + d[0] * tt + n[0] * uu, a[1] + d[2] * tt + n[2] * uu))
                add.mesh(solid(pts, y - 0.02, y + thick, shade_of("stone_dark", int(hash2(i, j, 51) * 3))))
                count_ += 1
    return count_
PEBBLE = add.make(add.icosahedron, [0, 0, 0], 1.0)
add.seed(7)
N_PEBBLES = count(24000)
i = 0
while i < N_PEBBLES:                                   # stones lie on the whole bed of the lake, out to its edges
    x, z = add.uniform(-W_EDGE + 1, W_EDGE - 1), add.uniform(-W_EDGE + 1, W_EDGE - 1)
    if ground(x, z) > WATER_Y - 0.25:
        continue
    a = add.uniform(0, 2 * add.pi)
    rr = add.uniform(0.15, 0.45)
    pebble = add.color(add.stretch(PEBBLE, [rr * add.uniform(0.8, 1.3), rr * 0.6, rr], (0, 0, 0)),
                       add.choice([P["rock"], P["stone_dark"], P["sand"]]))
    add.mesh(add.move(add.rotateY(pebble, a), [x, ground(x, z) + 0.05, z]))
    i += 1
    if i % 10000 == 0:
        flush("pebbles (%d)" % i, clean=False)
flush("pebbles", clean=False)
i = 0
while i < count(900):                                  # fish wherever the water is deep enough
    x, z = add.uniform(-W_EDGE + 2, W_EDGE - 2), add.uniform(-W_EDGE + 2, W_EDGE - 2)
    bed = ground(x, z)
    if bed > WATER_Y - 1.4:
        continue
    fish([x, add.uniform(bed + 0.5, WATER_Y - 0.5), z], add.atan2(x, z) + add.pi / 2 + add.uniform(-0.7, 0.7),
         add.choice([P["orange"], P["steel"], P["gold"], P["blue"]]), add.uniform(0.6, 1.3))
    i += 1
flush("fish", clean=False)
for i in range(count(800)):                            # reeds near the shore
    a, r = add.uniform(0, 2 * add.pi), add.uniform(93, 98)
    x, z = r * add.cos(a), r * add.sin(a)
    for j in range(3):
        add.cylinder([x + j * 0.2, ground(x, z), z], [x + j * 0.25, WATER_Y + add.uniform(1, 2.2), z + 0.1],
                     0.04, 6, P["leaf_dark"])
for i in range(count(400)):                            # lily pads, floating on the surface
    a, r = add.uniform(0, 2 * add.pi), add.uniform(94, 102)
    x, z = r * add.cos(a), r * add.sin(a)
    add.cylinder([x, ripple(x, z) + 0.02, z], [x, ripple(x, z) + 0.06, z], add.uniform(0.3, 0.6), 16, P["leaf"])
# the sunken boat: planks of a hull, lying on the bed, and a chest beside it
boat = add.Mesh()
for j in range(7):
    t = j / 6.0
    w = 2.0 * add.sin(add.pi * t) + 0.4
    boat.extend(add.make(add.cuboid, [0, 0.35 * (1 - w / 2.4), (t - 0.5) * 7], [w, 0.15, 1.05], P["wood_dark"]))
boat = add.rotate(boat, [1, 0, 0.3], 0.5)
add.mesh(add.move(boat, [70, ground(70, 82) + 0.6, 82]))
add.cuboid([72.5, ground(72.5, 84) + 0.4, 84], [1.2, 0.8, 0.8], P["wood"])
flush("under water")


# the road up the hill: a cobbled strip following the ground, and a jetty
def road(u, v):
    z = MOAT[3] + 1 + u * (96 - MOAT[3] - 1)
    x = v * 6 - 3 + 4 * add.sin(u * 3)
    return [x, ground(x, z) + 0.12, z]


def on_road(x, z, margin=0.6):
    """Is (x, z) on the road up the hill (its cobbled strip plus ``margin``),
    on the drawbridge, or on the landing before the gate?"""
    if abs(x) < 5.5 + margin and 50 < z < MOAT[3] + 1.5:
        return True
    u = (z - (MOAT[3] + 1)) / (96 - MOAT[3] - 1)
    if -0.02 < u < 1.05:
        return abs(x - 4 * add.sin(min(1.0, u) * 3)) < 3 + margin
    return False


add.parametric(road, 0, 1, 60, 0, 1, 6, P["stone_dark"], thickness=0.25)
for i in range(count(1600)):                           # cobbles along the road up the hill
    u, v = add.random(), add.random()
    q = road(u, v)
    add.mesh(add.move(add.rotateY(COBBLE, add.uniform(0, 6.3)), [q[0], q[1] - 0.02, q[2]]))
for i in range(12):                                    # the jetty into the lake
    z = 94 + i * 1.0
    add.cuboid([1.0, WATER_Y + 0.35, z], [3.0, 0.12, 0.85], P["wood"])
for z in (94, 100, 105.5):
    for x in (-0.4, 2.4):
        add.cylinder([x, ground(x, z), z], [x, WATER_Y + 0.9, z], 0.15, 12, P["wood_dark"])
# a rowing boat tied to the jetty, floating on the water
boat = add.Mesh()
for j in range(7):
    t = j / 6.0
    w = 1.8 * add.sin(add.pi * t) + 0.3
    boat.extend(add.make(add.cuboid, [0, 0.3 * (1 - w / 2.1), (t - 0.5) * 5], [w, 0.12, 0.75], P["wood"]))
boat.extend(add.make(add.cuboid, [0, 0.45, 0], [1.6, 0.08, 0.3], P["wood_light"]))    # thwart
for s in (-1, 1):
    boat.extend(add.make(add.cylinder, [s * 0.9, 0.5, 0.2], [s * 2.2, 0.2, -1.5], 0.05, 8, P["wood_light"]))
add.mesh(add.move(boat, [4.5, WATER_Y - 0.1, 99]))
add.polyline([[2.4, WATER_Y + 0.9, 100], [3.6, WATER_Y + 0.4, 99.5]], 0.03, 6, P["rope"])
flush("road and jetty")

# the forest on the slopes: low-poly trees -- a trunk and a crown of
# overlapping leaf blobs in two greens (pines: a stack of cones)
def blob_tree(at, h, kind, seed):
    x, y, z = at
    add.cylinder([x, y, z], [x, y + 0.45 * h, z], 0.05 * h, 8, P["trunk"])
    if kind == "pine":
        for j in range(4):
            r, base = 0.28 * h * (1 - 0.2 * j), y + 0.25 * h + j * 0.17 * h
            add.cone([x, base, z], [x, base + 0.34 * h, z], r, 10, P["leaf_dark"] if j % 2 else P["leaf"])
        return
    for j in range(7):
        u, v, w = hash2(seed, j, 5) - 0.5, hash2(seed, j, 6) - 0.5, hash2(seed, j, 7) - 0.5
        c = [x + 0.32 * h * u, y + 0.62 * h + 0.22 * h * v, z + 0.32 * h * w]
        r = h * (0.16 + 0.1 * hash2(seed, j, 8))
        add.mesh(add.stretch(add.make(add.sphere, c, r, 4, (P["leaf"], P["leaf_dark"], P["grass"])[j % 3]), [1.0, 0.85, 1.0], c))
    add.sphere([x, y + 0.8 * h, z], 0.2 * h, 4, P["leaf"])                                   # the crown's top


add.seed(11)
trees = 0
while trees < count(450):
    a, r = add.uniform(0, 2 * add.pi), add.uniform(60, 90)
    x, z = r * add.cos(a), r * add.sin(a)
    if on_road(x, z, 5.0):                                # keep the road clear
        continue
    y = ground(x, z)
    if y < WATER_Y + 1.5:
        continue
    kind = "pine" if hash2(trees, 1) > 0.5 else "round"
    blob_tree([x, y - 0.2, z], add.uniform(4, 9), kind, trees)
    trees += 1
    if trees % 150 == 0:
        flush("forest (%d trees)" % trees, clean=False)
flush("forest", clean=False)

# tufts of grass on the slopes and the meadow (thin solid blades)
add.seed(13)
n = 0
while n < count(150000):
    a, r = add.uniform(0, 2 * add.pi), 50 + 42 * add.sqrt(add.random())
    x, z = r * add.cos(a), r * add.sin(a)
    y = ground(x, z)
    if y < WATER_Y + 1.0 or octagon_r(x, z) < 51.5 or on_road(x, z) or near_corner(x, z, 0.3) \
            or (MOAT[0] - 1 < x < MOAT[1] + 1 and MOAT[2] - 1 < z < MOAT[3] + 1):
        continue
    for j in range(3):
        b = a + j * 2.1 + hash2(n, j)
        h = 0.25 + 0.3 * hash2(n, j, 2)
        sheet([[x - 0.05 * add.cos(b), y, z - 0.05 * add.sin(b)], [x + 0.05 * add.cos(b), y, z + 0.05 * add.sin(b)],
               [x + 0.12 * add.sin(b), y + h, z - 0.12 * add.cos(b)]], P["leaf"] if hash2(n, j, 3) > 0.5 else P["grass"], 0.01, hinge=True)
    n += 1
    if n % 30000 == 0:
        flush("grass (%d tufts)" % n, clean=False)
flush("grass", clean=False)


# --------------------------------------------------------------------------
#  2. The curtain wall: an octagon with eight hollow round towers
# --------------------------------------------------------------------------
WALL_TOP = G + 12
WALK = WALL_TOP + 0.3                                  # the wall walk surface
TOWER_TOP = G + 17
GATE_X = 10.5                                          # the gatehouse takes the middle of the south wall
GATE_W = 7.0


def along(a, b, s):
    """The point ``s`` units from ``a`` towards ``b`` (in XZ)."""
    L, d, n = outward(a, b)
    return [a[0] + d[0] * s, 0, a[2] + d[2] * s]


for k in range(8):
    a, b = CORNERS[k], CORNERS[(k + 1) % 8]
    if k == 1:                                         # the south wall, in two halves, to the gate towers
        wall_segment(along(a, b, TOWER_R - 0.5), [GATE_X - 0.5, 0, 50.0], G - 1, WALL_TOP)
        wall_segment([-GATE_X + 0.5, 0, 50.0], along(b, a, TOWER_R - 0.5), G - 1, WALL_TOP)
    else:
        wall_segment(along(a, b, TOWER_R - 0.5), along(b, a, TOWER_R - 0.5), G - 1, WALL_TOP)
    flush("curtain wall %d" % (k + 1))

ARRIVE = []                                            # where each tower's stair reaches the top
for k, c in enumerate(CORNERS):
    to_next = PHI[k] + 5 * add.pi / 8                  # door directions: along the two walls, and inward
    to_prev = PHI[k] + 11 * add.pi / 8
    inward = PHI[k] + add.pi
    walk = (WALK, to_next - 0.35, to_prev + 0.35)
    ARRIVE.append(round_tower(c, G - 1, TOWER_TOP, TOWER_R, doors=[(inward, G), (to_next, WALK), (to_prev, WALK)],
                              walk=walk, walls=(to_next, to_prev)))
    flush("tower %d" % (k + 1))


# --------------------------------------------------------------------------
#  3. The gatehouse: two hollow square towers with stairs, an arched
#     passage, a portcullis, a landing, the drawbridge on chains, guards
# --------------------------------------------------------------------------
def chain(a, b, link=0.22, thick=0.05, color=None):
    """A chain of linked rings from ``a`` to ``b``: every other link is turned
    by 90 degrees round the line, like a real chain."""
    color = color or P["iron"]
    d = vsub(b, a)
    L = vlen(d)
    d = vunit(d)
    helper = [0, 1, 0] if abs(d[1]) < 0.9 else [1, 0, 0]
    u = vunit(vcross(d, helper))
    v = vcross(d, u)
    n = max(1, int(L / (link * 1.45)))
    for i in range(n + 1):
        t = min(L, i * link * 1.45)
        c = [a[k] + d[k] * t for k in range(3)]
        add.torus(c, link, thick, k_(10), k_(6), color, axis=(u if i % 2 == 0 else v))


def armour(at, facing=0.0, weapon="spear", shield=True, plume=True):
    """A suit of plate armour standing on point ``at``: boots on the ground,
    legs, breastplate, pauldrons, arms, gauntlets, helmet with a visor slit,
    holding a spear (butt on the ground, the shaft in the gauntlet) or a
    sword (resting point-down, both gauntlets on the pommel), and a shield."""
    add.push()
    S, D = P["steel"], P["iron"]
    ks, kc = 8, k_(8)
    for s in (-1, 1):                                                  # boots, legs, knees
        add.cuboid([s * 0.24, 0.1, 0.08], [0.26, 0.2, 0.5], D)
        add.capsule([s * 0.24, 0.32, 0], [s * 0.24, 1.0, 0], 0.13, kc, S)
        add.sphere([s * 0.24, 0.98, 0.02], 0.15, ks, D)
    add.capsule([0, 1.12, 0], [0, 1.95, 0], 0.33, kc, S)                 # breastplate
    add.cuboid([0, 1.12, 0], [0.75, 0.25, 0.55], D)                      # fauld
    add.sphere([0, 2.32, 0], 0.26, ks, S)                                # helmet
    add.cuboid([0, 2.3, 0.24], [0.36, 0.05, 0.08], P["black"])          # the visor slit
    if plume:
        add.cone([0, 2.55, 0], [0, 2.85, -0.05], 0.05, 6, P["red"])
    for s in (-1, 1):                                                  # pauldrons
        add.sphere([s * 0.42, 1.9, 0], 0.2, ks, D)
    if weapon == "crossbow":
        # the crossbow at the shoulder, pointing out over the parapet
        add.cuboid([0.22, 1.62, 0.5], [0.07, 0.09, 1.0], P["wood_dark"])                    # the stock
        add.cuboid([0.22, 1.7, 0.72], [0.05, 0.04, 0.5], P["iron"])                          # the bolt in its groove
        for sx in (-1, 1):                                                                 # the bow, swept back
            add.beam([0.22, 1.66, 0.95], [0.22 + sx * 0.42, 1.66, 0.8], 0.035, 0.05, P["iron"])
        add.cylinder([-0.2, 1.66, 0.8], [0.64, 1.66, 0.8], 0.012, 5, P["rope"])            # the string
        add.capsule([0.5, 1.8, 0], [0.32, 1.5, 0.25], 0.1, kc, S)                           # right hand at the trigger
        add.sphere([0.3, 1.5, 0.3], 0.12, ks, D)
        add.capsule([-0.5, 1.8, 0], [0.05, 1.5, 0.6], 0.1, kc, S)                            # left hand under the stock
        add.sphere([0.12, 1.5, 0.65], 0.12, ks, D)
    elif weapon == "bow":
        # a longbow held out in the left hand, the right drawing the string
        stave = [[-0.34, 0.75 + 1.5 * t / 8, 0.42 + 0.2 * add.sin(add.pi * t / 8)] for t in range(9)]
        add.polyline(stave, 0.03, 6, P["wood_dark"])
        add.cylinder(stave[0], stave[-1], 0.01, 5, P["rope"])                              # the string
        add.cylinder([-0.34, 1.5, 0.15], [-0.34, 1.5, 0.95], 0.015, 5, P["wood"])          # the arrow, nocked
        add.cone([-0.34, 1.5, 0.95], [-0.34, 1.5, 1.05], 0.03, 5, S)
        add.capsule([-0.5, 1.8, 0], [-0.36, 1.5, 0.35], 0.1, kc, S)                          # left arm out to the grip
        add.sphere([-0.34, 1.5, 0.42], 0.12, ks, D)
        add.capsule([0.5, 1.8, 0], [0.0, 1.55, 0.15], 0.1, kc, S)                            # right arm drawn back
        add.sphere([-0.15, 1.52, 0.15], 0.12, ks, D)
    elif weapon == "spear":
        # right arm bent, the gauntlet closed round the shaft at chest height
        add.capsule([0.5, 1.8, 0], [0.62, 1.4, 0.35], 0.1, kc, S)
        add.sphere([0.62, 1.4, 0.4], 0.12, ks, D)
        add.cylinder([0.62, 0.0, 0.4], [0.62, 3.3, 0.4], 0.035, 8, P["wood"])   # the shaft, butt on the ground
        add.cone([0.62, 3.3, 0.4], [0.62, 3.8, 0.4], 0.08, 8, S)
        add.capsule([-0.5, 1.8, 0], [-0.55, 1.15, 0.15], 0.1, kc, S)     # left arm down, holding the shield
        add.sphere([-0.56, 1.1, 0.2], 0.12, ks, D)
    else:
        # both arms down to the pommel of a sword resting point-down in front
        for s in (-1, 1):
            add.capsule([s * 0.5, 1.8, 0], [s * 0.15, 1.15, 0.42], 0.1, kc, S)
        add.sphere([0, 1.1, 0.45], 0.14, ks, D)                          # the two gauntlets, one lump
        add.sphere([0, 1.22, 0.45], 0.06, 6, P["gold"])                  # pommel
        add.cylinder([0, 1.2, 0.45], [0, 0.95, 0.45], 0.035, 8, P["wood_dark"])
        add.cuboid([0, 0.93, 0.45], [0.4, 0.05, 0.05], P["gold"])        # cross-guard
        add.cuboid([0, 0.5, 0.45], [0.1, 0.86, 0.025], S)                # blade, point on the ground
        add.cone([0, 0.08, 0.45], [0, 0.0, 0.45], 0.05, 4, S)
    if shield:
        add.mesh(add.move(arms(0.55, 0.75, 0.06), [-0.62 - 0.275, 1.35 - 0.375, 0.32]))
    M = add.pop()
    add.mesh(add.move(add.rotateY(M, facing), at))


def lying_armour(at, facing=0.0):
    """A guard asleep on his back on the surface ``at`` (head towards
    ``facing``), the spear laid beside him."""
    M = add.make(armour, [0, 0, 0], 0, weapon="none", shield=False, plume=False)
    M = add.rotateX(M, -add.pi / 2)                                      # standing -> on his back, head at -z
    M = add.move(M, [0, 0.36, 0])                                        # the breastplate rests on the floor
    M.extend(add.make(add.cylinder, [0.8, 0.04, -1.5], [0.8, 0.04, 1.8], 0.035, 8, P["wood"]))
    M.extend(add.make(add.cone, [0.8, 0.04, -1.5], [0.8, 0.04, -2.0], 0.08, 8, P["steel"]))
    add.mesh(add.move(add.rotateY(M, facing), at))


def banner(at, w=1.6, h=2.6, facing=0.0, pole=True):
    """A cloth banner hanging from a cross-bar on a pole, with the castle's
    arms on it, swung a little as if in a breeze."""
    add.push()
    add.mesh(add.rotateX(add.move(arms(w, h, 0.03), [-w / 2, -h, 0]), 0.12))
    add.cylinder([-w / 2 - 0.05, 0, 0], [w / 2 + 0.1, 0, 0], 0.04, 8, P["wood_dark"])
    if pole:
        add.cylinder([-w / 2 - 0.05, -h, 0], [-w / 2 - 0.05, 0.6, 0], 0.05, 8, P["wood_dark"])
        add.sphere([-w / 2 - 0.05, 0.65, 0], 0.09, 6, P["gold"])
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def arms_color(u, v):
    """The colour of the castle's arms at the point (u, v) of a cloth, both
    0..1 (u along, v down): a red field with a gold border, a gold bend
    from the top corner at the pole, three white roundels."""
    if u < 0.04 or u > 0.96 or v < 0.05 or v > 0.95:
        return P["gold"]
    for cu, cv in ((0.28, 0.25), (0.72, 0.25), (0.5, 0.75)):
        if (u - cu) ** 2 + ((v - cv) * 0.7) ** 2 < 0.011:
            return P["white"]
    if abs(u - v) < 0.1:
        return P["gold"]
    return P["red"]


def flag(at, w=1.4, h=1.0, facing=0.0, phase=0.0):
    """A flag flying from the top of a pole at ``at``: a cloth fixed along
    the pole down its whole hoist, waving more towards the fly, with the
    castle's arms in its weave."""
    def cloth(u, v):
        return [u * w, -v * h, 0.16 * w * u ** 1.3 * add.sin(5.5 * u - 1.2 * v + phase)]
    M = add.make(add.parametric, cloth, 0, 1, 16, 0, 1, 7, P["red"], thickness=0.015)
    M = add.color_by(M, lambda q: arms_color(min(1.0, max(0.0, q[0] / w)), min(1.0, max(0.0, -q[1] / h))))
    add.mesh(add.move(add.rotateY(M, facing), at))


GATE_Z0, GATE_Z1 = 47.0, 53.0                          # the gate block, along the passage
GATE_TOP = G + 13
SPRING = G + 4.5                                       # the arch springs here; 2.5 more to the apex
GATE_ROOF = GATE_TOP + 0.4
for s in (-1, 1):
    # doors: to the courtyard (side 3 = -z), onto the wall walk (outer side), onto the gate roof (inner side)
    outer, inner = (0, 2) if s > 0 else (2, 0)
    stops = [(WALK, outer * add.pi / 2 - 0.35, outer * add.pi / 2 + 0.35),
             (GATE_ROOF, inner * add.pi / 2 - 0.35, inner * add.pi / 2 + 0.35)]
    square_tower([s * 7, 0, 50], G - 1, G + 20, GATE_W, doors=[(3, G), (outer, WALK), (inner, GATE_ROOF)],
                 walk_stops=stops, roof_h=6, windows=[(1, G + 8, 0.9, 1.6), (1, G + 15, 0.9, 1.6), (3, G + 15, 0.9, 1.6)])
    banner([s * 7, G + 17.5, 53.5 + 0.5])
# the passage: jambs, the arch fill (textured), voussoirs on both faces
for s in (-1, 1):
    add.cuboid([s * 3.0, (G - 1 + SPRING) / 2, 50], [1.0, SPRING - G + 1, GATE_Z1 - GATE_Z0], P["mortar"])
add.mesh(arch_fill(-3.5, 3.5, SPRING, GATE_TOP, GATE_Z0, GATE_Z1, 0, 2.5, P["mortar"]))
for z, depth in ((GATE_Z1, 0.25), (GATE_Z0, -0.25)):                          # stone skins on both faces, round the arch
    add.push()
    stone_face(GATE_W, G - 1, GATE_TOP, 0, 0.22, "stone", seed=int(z),
               skip=[(GATE_W / 2 - 3.15, GATE_W / 2 + 3.15, G - 1, SPRING + 3.15, (GATE_W / 2, SPRING, 3.15))])
    add.mesh(add.move(add.pop() if depth > 0 else add.mirror(add.pop(), [0, 0, 0], [0, 0, 1]), [-GATE_W / 2, 0, z]))
    voussoirs(0, SPRING, 2.5, z, depth, 13, lambda i: shade_of("stone", i), width=0.6)
add.cuboid([0, GATE_TOP + 0.2, 50], [GATE_W, 0.4, GATE_Z1 - GATE_Z0 + 0.6], P["stone_dark"])   # the gate roof
add.mesh(add.move(add.make(merlons, GATE_W, 0.4, 0, 0.5), [-3.5, GATE_TOP, GATE_Z1]))
add.mesh(add.move(add.make(merlons, GATE_W, 0.4, -0.5, 0), [-3.5, GATE_TOP, GATE_Z0]))
add.text("ADD 2.0", [0, G + 8.2, GATE_Z1 + 0.36], 0.9, 0.08, P["gold"], align="center", k=8)
for s in (-1, 1):                                      # a lamp on each side of the gate
    add.cuboid([s * 3.9, G + 4.2, GATE_Z1 + 0.3], [0.3, 0.3, 0.6], P["iron"])
    add.sphere([s * 3.9, G + 4.9, GATE_Z1 + 0.45], 0.28, 8, FLAME)
# the paved landing between the gate and the moat, and the paved passage
PAVE = G + 0.1                                         # top of the paving: level with the cobblestones
add.cuboid([0, (G - 0.3 + G + 0.02) / 2, (GATE_Z1 + MOAT[2] - 1) / 2], [26, 0.32, MOAT[2] - 1 - GATE_Z1], P["mortar"])
add.cuboid([0, (G - 0.3 + G + 0.02) / 2, (GATE_Z0 + GATE_Z1) / 2], [7.0, 0.32, GATE_Z1 - GATE_Z0], P["mortar"])
cobble_area(lambda x, z: (z >= GATE_Z1 or abs(x) < 2.45) and hash2(int(x * 9), int(z * 9), 77) < max(DENSITY, 0.35),
            -13, 13, GATE_Z0, MOAT[2] - 1, G + 0.02, step=0.44, scale=0.7, seed=5)      # cobbles: landing and passage
flush("gatehouse")

# the portcullis, lowered to a third, in a slot just inside the outer face
PORT_Z = GATE_Z1 - 0.7
PORT_BOTTOM = G + 2.4
for i in range(8):
    x = -2.1 + i * 0.6
    add.cylinder([x, PORT_BOTTOM + 0.4, PORT_Z], [x, GATE_TOP - 0.2, PORT_Z], 0.07, 12, P["iron"])
    add.cone([x, PORT_BOTTOM + 0.4, PORT_Z], [x, PORT_BOTTOM, PORT_Z], 0.07, 12, P["iron"])
for y in (PORT_BOTTOM + 0.9, PORT_BOTTOM + 2.3, PORT_BOTTOM + 3.7, PORT_BOTTOM + 5.1):
    add.cuboid([0, y, PORT_Z], [4.5, 0.12, 0.12], P["iron"])
# the wooden gate behind it: two leaves on hinges, one wide open, one ajar;
# their tops follow the arch, so that closed they fill it exactly
for s, angle in ((-1, 1.3), (1, -0.25)):
    leaf = add.Mesh()                                  # hinge at x = 0, planks towards +x

    def gate_top(x):                                   # the arch: centre 2.5 from the hinge, radius 2.5
        return SPRING - G - 0.06 + add.sqrt(max(0.0, 2.5 ** 2 - (x - 2.5) ** 2))

    for i in range(6):
        x0, x1 = 0.02 + i * 0.4, 0.02 + (i + 1) * 0.4 - 0.02
        profile = [[x0, 0.06], [x1, 0.06], [x1, gate_top(x1)], [(x0 + x1) / 2, gate_top((x0 + x1) / 2)], [x0, gate_top(x0)]]
        leaf.extend(add.make(add.prism, profile, 0.2, pick("wood", i, s + 2), (0, 0, 0), (0, 0, 1)))
    for y in (0.6, 2.6, 4.4):
        leaf.extend(add.make(add.cuboid, [1.2, y, -0.14], [2.4, 0.25, 0.08], P["iron"]))
        for i in range(6):
            leaf.extend(add.make(add.sphere, [0.2 + i * 0.4, y, -0.2], 0.05, 4, P["iron"]))
    if s > 0:
        leaf = add.mirror(leaf, [0, 0, 0], [1, 0, 0])   # the right leaf opens towards -x
    leaf = add.rotateY(leaf, angle)
    add.mesh(add.move(leaf, [s * 2.5, G, GATE_Z0 + 0.6]))
    add.cylinder([s * 2.5, G, GATE_Z0 + 0.6], [s * 2.5, G + 5.2, GATE_Z0 + 0.6], 0.06, 8, P["iron"])   # the hinge pin
flush("portcullis and gate")

# the drawbridge: planks on two beams, spanning the moat from bank to bank, with its chains
BRIDGE_Z0, BRIDGE_Z1 = MOAT[2] - 0.6, MOAT[3] + 0.8
for s in (-1, 1):
    add.cuboid([s * 1.9, G + 0.12, (BRIDGE_Z0 + BRIDGE_Z1) / 2], [0.3, 0.25, BRIDGE_Z1 - BRIDGE_Z0], P["wood_dark"])
planks = int(4.6 / 0.42)
for i in range(planks):
    x = -2.3 + 0.21 + i * 0.42
    add.cuboid([x, G + 0.32, (BRIDGE_Z0 + BRIDGE_Z1) / 2], [0.4, 0.15, BRIDGE_Z1 - BRIDGE_Z0], pick("wood", i, 9))
for z in (BRIDGE_Z0 + 0.3, BRIDGE_Z1 - 0.3):               # iron straps at both ends
    add.cuboid([0, G + 0.42, z], [4.7, 0.05, 0.2], P["iron"])
add.cylinder([-2.5, G + 0.12, BRIDGE_Z0], [2.5, G + 0.12, BRIDGE_Z0], 0.08, 12, P["iron"])   # the hinge bar on the bank
for s in (-1, 1):
    hole = [s * 2.0, G + 10.2, GATE_Z1]
    add.cuboid([hole[0], hole[1], hole[2] - 0.2], [0.6, 0.6, 0.5], P["black"])
    chain([s * 2.0, G + 0.5, BRIDGE_Z1 - 0.4], [hole[0], hole[1], hole[2] + 0.1])
    add.torus([s * 2.0, G + 0.5, BRIDGE_Z1 - 0.4], 0.16, 0.05, k_(10), k_(6), P["iron"], axis=(1, 0, 0))
flush("drawbridge and chains")

# two guards on the landing, and one on the wall walk
armour([-3.4, PAVE, GATE_Z1 + 1.4], add.pi * 0.08)
armour([3.4, PAVE, GATE_Z1 + 1.4], -add.pi * 0.08, weapon="sword")
flush("guards")


# --------------------------------------------------------------------------
#  4. The palace: the great hall below, the soldiers' dormitory above, the
#     attic under a tiled hip roof; corner towers and the donjon; a chapel
# --------------------------------------------------------------------------
KX0, KX1, KZ0, KZ1 = -22.0, 22.0, -30.0, -2.0            # the footprint of the main block
KY = G + 0.8                                            # the hall floor (on a plinth)
HALL_H = 9.0                                            # floor to ceiling
SLAB = 0.6
FLOOR2 = KY + HALL_H + SLAB                             # the dormitory floor
UPPER_H = 5.0
EAVE = FLOOR2 + UPPER_H                                 # the attic floor / the eaves
ROOF_H = 8.0
RIDGE_Y = EAVE + ROOF_H
WT = 1.2                                                # wall thickness
TOWER_R2 = 4.5
PALACE_TOWERS = [(KX1, KZ1), (KX1, KZ0), (KX0, KZ1)]    # SE, NE, SW corners
DON = (KX0 - 3.0, KZ0 - 3.0)                            # the donjon, at the NW corner
DON_R = 6.5
DON_TOP = EAVE + 12
CYLS = [(cx, cz, TOWER_R2) for cx, cz in PALACE_TOWERS] + [(DON[0], DON[1], DON_R)]


def tower_cutters(y0, y1, extra=0.05):
    """The towers' outer cylinders, to cut the palace walls, floors and
    roof where a tower stands."""
    return [add.make(add.cylinder, [cx, y0, cz], [cx, y1, cz], r + extra, k_(24)) for cx, cz, r in CYLS]


def near_tower(x, z, margin=0.3):
    return any((x - cx) ** 2 + (z - cz) ** 2 < (r + margin) ** 2 for cx, cz, r in CYLS)


def opening(x, y0, y1, w, arched=True, kind="window"):
    """An opening in a wall: ``kind`` is "window", "door" (a wooden door,
    open) or "french" (a glazed door down to the floor, onto a balcony)."""
    return {"x": x, "y0": y0, "y1": y1, "w": w, "arched": arched, "kind": kind}


FRAME = 0.12                                            # section of the window frames


def window_frame(o, thickness):
    """Frame, glazing bars and glass of one opening, built at the origin of
    the wall (x along the wall, y up, z through it).  The frame runs all
    the way round: two jambs, a sill or threshold, and an arched head of
    the same section as the jambs; a mullion up to the head, a transom."""
    r = o["w"] / 2
    top = o["y1"] - (r if o["arched"] else 0)              # the springing line
    x0, x1 = o["x"] - r, o["x"] + r
    ins = 0.03                                            # frames sit a hair inside the cut faces
    zf = 0.0
    if o["kind"] == "stained":                                                                           # leaded panes of coloured glass
        pw, ph = 0.26, 0.3
        cols, rows = int((o["w"] - 2 * ins) / pw), int((o["y1"] - o["y0"] - ins) / ph)
        pw, ph = (o["w"] - 2 * ins) / cols, (o["y1"] - o["y0"] - ins) / rows
        for i in range(cols):
            for j in range(rows):
                px, py = x0 + ins + (i + 0.5) * pw, o["y0"] + ins + (j + 0.5) * ph
                if py > top and (px - o["x"]) ** 2 + (py - top) ** 2 > (r - ins) ** 2:
                    continue                                                                             # outside the arch
                add.cuboid([px, py, zf], [pw, ph, 0.04], STAINED[int(hash2(i, j, 21 + int(o["x"] * 10)) * 5) % 5])
        for i in range(1, cols):                                                                         # lead cames
            add.cuboid([x0 + ins + i * pw, (o["y0"] + top) / 2, zf], [0.03, top - o["y0"], 0.06], P["black"])
        for j in range(1, rows):
            py = o["y0"] + ins + j * ph
            hw = (o["w"] - 2 * ins) if py <= top else 2 * add.sqrt(max(0.0, (r - ins) ** 2 - (py - top) ** 2))
            if hw > 0.05:
                add.cuboid([o["x"], py, zf], [hw, 0.03, 0.06], P["black"])
    if o["kind"] == "window":
        add.cuboid([o["x"], (o["y0"] + o["y1"]) / 2, zf], [o["w"] - 2 * ins, o["y1"] - o["y0"] - ins, 0.06], GLASS)
        add.cuboid([o["x"], (o["y0"] + top) / 2, zf], [FRAME, top - o["y0"], 0.14], P["glass_frame"])     # mullion
        add.cuboid([o["x"], o["y0"] + (top - o["y0"]) * 0.6, zf], [o["w"] - 2 * ins, FRAME, 0.14], P["glass_frame"])   # transom
        add.cuboid([o["x"], o["y0"] + FRAME / 2 + ins, zf], [o["w"] - 2 * ins, FRAME, 0.14], P["glass_frame"])   # bottom rail
    for x in (x0 + ins + FRAME / 2, x1 - ins - FRAME / 2):                                             # jambs
        add.cuboid([x, (o["y0"] + top) / 2 + ins / 2, zf], [FRAME, top - o["y0"] - ins, 0.14], P["glass_frame"])
    if o["arched"]:                                                                                     # the arched head, same section
        add.arch([x0 + ins + FRAME / 2, top, zf], [x1 - ins - FRAME / 2, top, zf], r - ins - FRAME / 2, [0.14, FRAME],
                 P["glass_frame"], k_(14))
        if o["kind"] == "window":
            add.cuboid([o["x"], top + (r - ins - FRAME) / 2, zf], [FRAME, r - ins - FRAME, 0.14], P["glass_frame"])   # mullion into the arch
    else:
        add.cuboid([o["x"], top - ins - FRAME / 2, zf], [o["w"] - 2 * ins, FRAME, 0.14], P["glass_frame"])   # head rail
    if o["kind"] == "french":                                                                            # two glazed leaves, open,
        add.cuboid([o["x"], top + FRAME / 2, zf], [o["w"] - 2 * ins, FRAME, 0.14], P["glass_frame"])     # under a fixed fanlight
        if o["arched"]:
            fan = add.make(add.cylinder, [o["x"], top, zf - 0.03], [o["x"], top, zf + 0.03], r - ins - FRAME, k_(14), GLASS)
            add.mesh(add.cut(fan, [o["x"], top + FRAME, zf], [0, -1, 0], cap=False))
            for i in (1, 2, 3):                                                                          # radial glazing bars
                aa = add.pi * i / 4
                add.beam([o["x"], top + FRAME / 2, zf], [o["x"] + (r - ins - FRAME / 2) * add.cos(aa), top + (r - ins - FRAME / 2) * add.sin(aa), zf],
                         0.14, FRAME * 0.7, P["glass_frame"])
        for s in (-1, 1):
            leaf = add.Mesh()
            hl = top - o["y0"] - 2 * ins                                                                  # leaf height
            leaf.extend(add.make(add.cuboid, [r / 2 - ins, hl / 2 + ins, 0], [r - 2 * ins, hl, 0.06], GLASS))
            for dx in (ins + FRAME / 2, r - ins - FRAME / 2):
                leaf.extend(add.make(add.cuboid, [dx, hl / 2 + ins, 0], [FRAME, hl, 0.1], P["wood_dark"]))
            for dy in (ins + FRAME / 2, hl + ins - FRAME / 2, hl * 0.5 + ins):
                leaf.extend(add.make(add.cuboid, [r / 2, dy, 0], [r - 2 * ins, FRAME, 0.1], P["wood_dark"]))
            if s > 0:
                leaf = add.mirror(leaf, [0, 0, 0], [1, 0, 0])
            leaf = add.rotateY(leaf, -s * 1.2)                                                           # hinged at its jamb, open inward
            add.mesh(add.move(leaf, [o["x"] + s * r, o["y0"], -thickness / 2 + 0.2]))
    if o["kind"] == "door":                                                                              # a wooden door with arched
        for s, angle in ((-1, 1.5), (1, 0.35)):                                                          # leaves, one wide open, one ajar
            leaf = add.Mesh()
            n = 5
            pw = (r - 0.08) / n
            for i in range(n):
                x0, x1 = 0.04 + i * pw, 0.04 + (i + 1) * pw - 0.02

                def arc_top(x):                                                                          # the leaf follows the arch
                    dx = x - r
                    return top - o["y0"] - 0.06 + (add.sqrt(max(0.0, (r - 0.06) ** 2 - dx * dx)) if o["arched"] else 0.0)
                profile = [[x0, 0.04], [x1, 0.04], [x1, arc_top(x1)], [(x0 + x1) / 2, arc_top((x0 + x1) / 2)], [x0, arc_top(x0)]]
                leaf.extend(add.make(add.prism, profile, 0.16, pick("wood_dark", i, 5), (0, 0, 0), (0, 0, 1)))
            for dy in (0.5, (top - o["y0"]) / 2, top - o["y0"] - 0.5):
                leaf.extend(add.make(add.cuboid, [r / 2, dy, 0.11], [r - 0.12, 0.2, 0.06], P["iron"]))
            leaf.extend(add.make(add.torus, [r * 0.75, (top - o["y0"]) / 2, 0.2], 0.14, 0.03, 16, 8, P["gold"], axis=(0, 0, 1)))
            if s > 0:
                leaf = add.mirror(leaf, [0, 0, 0], [1, 0, 0])
            add.mesh(add.move(add.rotateY(leaf, -s * angle), [o["x"] + s * (r - 0.02), o["y0"], -thickness / 2 + 0.25]))


def pierced_wall(length, height, openings, thickness=WT, name="stone", cutters=(), sills=True):
    """A wall along +X (0..length, 0..height, centred on z = 0) with arched
    or square openings cut through it, glazed, framed and given stone
    surrounds; ``cutters`` are extra solids (the towers) subtracted from
    it.  Returned as a mesh built at the origin."""
    slab = add.make(add.cuboid, [length / 2, height / 2, 0], [length, height, thickness], P["stone"])
    holes = []
    for o in openings:
        r = o["w"] / 2
        top = o["y1"] - (r if o["arched"] else 0)
        holes.append(add.make(add.cuboid, [o["x"], (o["y0"] + top) / 2, 0], [o["w"], top - o["y0"], thickness + 2]))
        if o["arched"]:
            holes.append(add.make(add.cylinder, [o["x"], top, -thickness], [o["x"], top, thickness], r, k_(14)))
    wall = add.difference(slab, *(holes + list(cutters))) if (holes or cutters) else slab
    add.push()
    add.mesh(add.color(wall, P["mortar"]))
    skip = []
    for o in openings:                                                                        # the skins leave the openings
        r = o["w"] / 2                                                                        # and their stone surrounds free
        top = o["y1"] - (r if o["arched"] else 0)
        if o["arched"]:
            skip.append((o["x"] - r - 0.45, o["x"] + r + 0.45, o["y0"] - 0.25, top + r + 0.45, (o["x"], top, r + 0.45)))
        else:
            skip.append((o["x"] - r - 0.45, o["x"] + r + 0.45, o["y0"] - 0.25, top + 0.35))
        if o["kind"] == "french":                                                             # the balcony slab and its corbels
            skip.append((o["x"] - 2.28, o["x"] + 2.28, o["y0"] - 1.15, o["y0"]))
    for cutter in cutters:                                                                    # ... and the towers
        lo, hi = add.bbox(cutter)
        skip.append((lo[0] - 0.3, hi[0] + 0.3, -1, height + 1))
    stone_face(length, 0, height, thickness / 2, 0.22, name, seed=int(length), skip=skip)
    stone_face(length, 0, height, -thickness / 2, -0.22, name, seed=int(length) + 7, skip=skip)
    for o in openings:
        r = o["w"] / 2
        top = o["y1"] - (r if o["arched"] else 0)
        window_frame(o, thickness)
        for z in (thickness / 2, -thickness / 2):                                             # the stone surround, both faces:
            depth = 0.1 if z > 0 else -0.1
            jamb_stones(o["x"] - r, o["x"] + r, o["y0"], top, z, depth)                       # quoins up the sides ...
            if o["arched"]:
                voussoirs(o["x"], top, r, z, depth, 9, lambda i: shade_of("stone", i), width=0.42)   # ... and round the arch
        if not o["arched"]:
            add.cuboid([o["x"], top + 0.15, 0], [o["w"] + 0.9, 0.3, thickness + 0.2], P["stone_dark"])   # lintel
        if sills and o["kind"] in ("window", "stained"):
            add.cuboid([o["x"], o["y0"] - 0.1, thickness / 2 + 0.1], [o["w"] + 0.5, 0.2, 0.5], P["stone_dark"])
    return add.pop()


def stand_wall(M, a, b, y, centre=None):
    centre = centre or ((KX0 + KX1) / 2, (KZ0 + KZ1) / 2)
    L, d, n = outward([a[0], 0, a[1]], [b[0], 0, b[1]], centre=centre)
    add.mesh(frame_to(M, [a[0], y, a[1]], d, n))


def local_cutters(a, b, y, cutters):
    """Bring world-space cutters into the frame of a wall from a to b at
    height y (the inverse of stand_wall)."""
    L, d, n = outward([a[0], 0, a[1]], [b[0], 0, b[1]], centre=((KX0 + KX1) / 2, (KZ0 + KZ1) / 2))
    out = []
    for C in cutters:
        out.append(add.transform(add.move(C, [-a[0], -y, -a[1]]),
                                 [[d[0], 0, d[2], 0], [0, 1, 0, 0], [n[0], 0, n[2], 0]]))
    return out


# the plinth is the hall floor: its top is the walking surface (KY)
PL = 0.8
plinth = add.make(add.cuboid, [0, (G - 0.5 + KY) / 2, (KZ0 + KZ1) / 2], [KX1 - KX0 + 2 * PL, KY - G + 0.5, KZ1 - KZ0 + 2 * PL], P["stone_dark"])
plinth = add.difference(plinth, *tower_cutters(G - 1, KY + 1))
add.mesh(add.color(plinth, P["stone_dark"]))
add.stairs([0, G, KZ1 + PL + 2.4], 4, 7.0, (KY - G) / 4, 0.6, P["stone_dark"], direction=(0, 0, -1))
flush("palace: plinth")

WIN_LO = (1.6, 7.4, 2.2)                               # ground-floor windows: y0, y1, width
WIN_UP = (HALL_H + SLAB + 0.9, HALL_H + SLAB + 3.4, 1.6)
BALCONY_X = (-11.0, 0.0, 11.0)
south = [opening(22, 0, 5.2, 4.0, kind="door")]
north = []
for x in (6, 11, 15.5):
    for s in (-1, 1):
        south.append(opening(22 + s * x, WIN_LO[0], WIN_LO[1], WIN_LO[2]))
        north.append(opening(22 + s * x, WIN_LO[0], WIN_LO[1], WIN_LO[2]))
        if x != 11:
            south.append(opening(22 + s * x, WIN_UP[0], WIN_UP[1], WIN_UP[2]))
        north.append(opening(22 + s * x, WIN_UP[0], WIN_UP[1], WIN_UP[2]))
north.append(opening(22, WIN_UP[0], WIN_UP[1], WIN_UP[2]))
for bx in BALCONY_X:                                   # glazed doors onto the balconies
    south.append(opening(22 + bx, HALL_H + SLAB, HALL_H + SLAB + 3.0, 1.6, kind="french"))
west = [opening(z, WIN_LO[0], WIN_LO[1], WIN_LO[2]) for z in (7, 21)]
west += [opening(z, WIN_UP[0], WIN_UP[1], WIN_UP[2]) for z in (5.5, 10.5, 17.5, 22.5)]
east = [opening(14, 0, DOOR_H, DOOR_W, kind="door")]  # into the chapel
east += [opening(z, WIN_UP[0], WIN_UP[1], WIN_UP[2]) for z in (5.5, 10.5, 17.5, 22.5)]
CUT = tower_cutters(G - 2, RIDGE_Y + 2)
WALLS = {"south": ((KX0, KZ1), (KX1, KZ1), south), "north": ((KX1, KZ0), (KX0, KZ0), north),
         "west": ((KX0, KZ1), (KX0, KZ0), west), "east": ((KX1, KZ0), (KX1, KZ1), east)}
for name in ("south", "north", "west", "east"):
    a, b, ops = WALLS[name]
    length = abs(b[0] - a[0]) + abs(b[1] - a[1])
    M = pierced_wall(length, EAVE - KY, ops, cutters=local_cutters(a, b, KY, CUT))
    stand_wall(M, a, b, KY)
    flush("palace: %s wall" % name)

# the chessboard floor of the hall (marble squares, sunk a little into the plinth)
for i in range(int((KX1 - KX0 - 2 * WT) / 2)):
    for j in range(int((KZ1 - KZ0 - 2 * WT) / 2)):
        x, z = KX0 + WT + 0.1 + i * 2, KZ0 + WT + 0.1 + j * 2
        if near_tower(x + 1, z + 1, 0.5):
            continue
        add.cuboid([x + 1, KY, z + 1], [1.9, 0.1, 1.9], P["white"] if (i + j) % 2 else P["wood_dark"])
# the floor between the storeys, its beams below, and the attic floor with a hatch
slab = add.make(add.cuboid, [0, KY + HALL_H + SLAB / 2 - 0.02, (KZ0 + KZ1) / 2], [KX1 - KX0 - 0.4, SLAB - 0.04, KZ1 - KZ0 - 0.4], P["wood_dark"])
add.mesh(add.difference(slab, *CUT))
TOWER_ROUNDS = [(cx, cz, r + 0.05) for cx, cz, r in CYLS]         # where the towers pass through the floors
plank_floor(KX0 + 0.2, KX1 - 0.2, KZ0 + 0.2, KZ1 - 0.2, KY + HALL_H + SLAB, rounds=TOWER_ROUNDS)
for i in range(int((KZ1 - KZ0) / 3)):
    z = KZ0 + WT + 1.5 + i * 3
    x0, x1 = KX0 + WT - 0.3, KX1 - WT + 0.3
    while near_tower(x0, z, 0.3):
        x0 += 0.5
    while near_tower(x1, z, 0.3):
        x1 -= 0.5
    add.cuboid([(x0 + x1) / 2, KY + HALL_H - 0.28, z], [x1 - x0, 0.6, 0.6], P["wood_dark"])
HATCH = (0.0, KZ0 + 6.0)                               # the ladder-stair to the attic comes up here
attic = add.make(add.cuboid, [0, EAVE - 0.22, (KZ0 + KZ1) / 2], [KX1 - KX0 - 0.4, 0.36, KZ1 - KZ0 - 0.4], P["wood_dark"])
HOLE = (HATCH[0] - 1.1, HATCH[0] + 1.1, HATCH[1] - 0.6, HATCH[1] + 4.6)          # the stairwell in the attic floor
attic = add.difference(attic, add.make(add.cuboid, [HATCH[0], EAVE - 0.2, (HOLE[2] + HOLE[3]) / 2], [2.2, 1, HOLE[3] - HOLE[2]]), *CUT)
add.mesh(attic)
plank_floor(KX0 + 0.2, KX1 - 0.2, KZ0 + 0.2, KZ1 - 0.2, EAVE, along="x", holes=[HOLE], rounds=TOWER_ROUNDS)   # sawn round the stairwell
for x in (HOLE[0] - 0.1, HOLE[1] + 0.1):                                        # a rail round the stairwell: along both
    for z in (HOLE[2] - 0.1, (HOLE[2] + HOLE[3]) / 2, HOLE[3] + 0.1):           # sides and across the far end, where the
        add.cuboid([x, EAVE + 0.45, z], [0.08, 0.9, 0.08], P["wood_dark"])     # stair is deep below; the near end, where
    add.cuboid([x, EAVE + 0.9, (HOLE[2] + HOLE[3]) / 2], [0.06, 0.06, HOLE[3] - HOLE[2] + 0.3], P["wood_dark"])   # the top
add.cuboid([HATCH[0], EAVE + 0.9, HOLE[3] + 0.1], [HOLE[1] - HOLE[0] + 0.3, 0.06, 0.06], P["wood_dark"])    # step is, is the way in
flush("palace: floors")

# the three corner towers: a door to the courtyard, doors into the hall
# and into the dormitory, a stair with landings, a lookout under a copper spire
for cx, cz in PALACE_TOWERS:
    out_a = add.atan2(cz - (KZ0 + KZ1) / 2, cx - (KX0 + KX1) / 2)      # away from the palace
    in_a = out_a + add.pi                                            # into the palace
    stops = [(KY, in_a - 0.4, in_a + 0.4), (FLOOR2, in_a - 0.4, in_a + 0.4)]
    round_tower([cx, 0, cz], G - 1, EAVE + 4, TOWER_R2, doors=[(out_a, G), (in_a, KY), (in_a, FLOOR2)], walk=None,
                roof_h=9, roof_color=P["spire"], slits=False,
                windows=[(out_a + 0.9, KY + 3, 0.7, 1.4), (out_a - 0.9, KY + 3, 0.7, 1.4),
                         (out_a, FLOOR2 + 1.2, 0.7, 1.4), (out_a + 1.0, EAVE + 0.6, 0.7, 1.4), (out_a - 1.0, EAVE + 0.6, 0.7, 1.4)],
                stops=stops)
    flush("palace: corner tower")


def disc_with_hole(cx, cz, r, y, thick, r_hole, a_from, a_to, color):
    """A floor disc with an annular sector (a stairwell) left open between
    angles ``a_from`` and ``a_to`` and radii ``r_hole``..``r``."""
    pts = []
    n = 48
    for j in range(n + 1):                                             # the outer rim, the long way round
        a = a_to + (2 * add.pi - (a_to - a_from)) * j / n
        pts.append((cx + r * add.cos(a), cz + r * add.sin(a)))
    m = 8
    for j in range(m + 1):                                             # then along the inner rim, past the stairwell
        a = a_from + (a_to - a_from) * j / float(m)
        pts.append((cx + r_hole * add.cos(a), cz + r_hole * add.sin(a)))
    add.mesh(solid(pts, y - thick, y, color))


def wall_stair(cx, cz, y0, y1, r_in, r_out, start, rise=0.24, depth=0.3):
    """A stair hugging a round wall (steps are annular sectors), from y0 up
    to y1 starting at angle ``start``; returns the arrival angle."""
    n = max(1, int(round((y1 - y0) / rise)))
    rise = (y1 - y0) / float(n)
    sweep = depth / ((r_in + r_out) / 2)
    for i in range(n):
        a0, a1 = start + i * sweep, start + (i + 1) * sweep
        pts = [(cx + r_in * add.cos(a0), cz + r_in * add.sin(a0)), (cx + r_out * add.cos(a0), cz + r_out * add.sin(a0)),
               (cx + r_out * add.cos(a1), cz + r_out * add.sin(a1)), (cx + r_in * add.cos(a1), cz + r_in * add.sin(a1))]
        add.mesh(solid(pts, y0 + i * rise, y0 + (i + 1) * rise, shade_of("stone_dark", i)))
        if i % 3 == 0:                                                 # a rope handrail on posts along the open side
            add.cylinder([cx + (r_in + 0.1) * add.cos(a0), y0 + (i + 1) * rise, cz + (r_in + 0.1) * add.sin(a0)],
                         [cx + (r_in + 0.1) * add.cos(a0), y0 + (i + 1) * rise + 0.9, cz + (r_in + 0.1) * add.sin(a0)], 0.04, 8, P["iron"])
    rope = [[cx + (r_in + 0.1) * add.cos(start + i * sweep), y0 + (i + 1) * rise + 0.9, cz + (r_in + 0.1) * add.sin(start + i * sweep)]
            for i in range(0, n, 3)]
    if len(rope) > 1:
        add.polyline(rope, 0.03, 8, P["rope"])
    return start + n * sweep


# the donjon: a big hollow tower with the treasury, the armoury and the
# lord's chamber on three floors, a wall-hugging stair and a lookout on top
DON_IN = DON_R - 1.0
F1, F2 = FLOOR2, EAVE + 4.0
drum = add.make(add.pipe, [DON[0], G - 1, DON[1]], [DON[0], DON_TOP, DON[1]], DON_R, DON_IN, k_(28))
holes = [radial_cutter(DON[0], DON[1], add.pi, G, DOOR_W, DOOR_H, DON_IN - 0.5, DON_R + 0.5),    # out, to the west
         radial_cutter(DON[0], DON[1], add.pi / 4, KY, DOOR_W, DOOR_H, DON_IN - 0.5, DON_R + 0.5),      # into the hall
         radial_cutter(DON[0], DON[1], add.pi / 4, FLOOR2, DOOR_W, DOOR_H, DON_IN - 0.5, DON_R + 0.5)]  # into the dormitory
DON_WINDOWS = [(add.pi * 0.75, KY + 4, 0.8, 1.6), (add.pi * 1.25, KY + 5, 0.8, 1.6), (add.pi * 0.75, F1 + 1.5, 0.9, 1.8),
               (add.pi * 1.25, F1 + 1.5, 0.9, 1.8), (add.pi * 1.75, F1 + 1.5, 0.9, 1.8), (add.pi * 0.6, F2 + 1.5, 1.2, 2.2),
               (add.pi * 1.1, F2 + 1.5, 1.2, 2.2), (add.pi * 1.6, F2 + 1.5, 1.2, 2.2)]
skip = [(add.pi, DOOR_W / 2 / DON_R, G, G + DOOR_H, DOOR_W / 2), (add.pi / 4, DOOR_W / 2 / DON_R, KY, KY + DOOR_H, DOOR_W / 2),
        (add.pi / 4, DOOR_W / 2 / DON_R, FLOOR2, FLOOR2 + DOOR_H, DOOR_W / 2)]
for a, level, w, h in DON_WINDOWS:
    holes.append(radial_cutter(DON[0], DON[1], a, level, w, h, DON_IN - 0.5, DON_R + 0.5))
    skip.append((a, w / 2 / DON_R, level, level + h, w / 2))
add.mesh(tex_round(add.difference(drum, *holes), "stone", DON[0], DON[1], DON_R, 3.0))
stone_ring(DON[0], DON[1], DON_R, G - 0.5, DON_TOP - 1.0, "stone", skip)
for a, level, w, h in DON_WINDOWS:                                                    # glass in the windows
    pane = add.make(add.cuboid, [DON_R - 0.5, level + h / 2, 0], [0.06, h - 0.1, w - 0.1], GLASS)
    pane.extend(add.make(add.cuboid, [DON_R - 0.5, level + h / 2, 0], [0.1, h - 0.1, FRAME], P["glass_frame"]))
    pane.extend(add.make(add.cuboid, [DON_R - 0.5, level + h * 0.55, 0], [0.1, FRAME, w - 0.1], P["glass_frame"]))
    add.mesh(add.move(add.rotateY(pane, -a), [DON[0], 0, DON[1]]))
add.cylinder([DON[0], G - 0.5, DON[1]], [DON[0], G + 0.1, DON[1]], DON_IN + 0.2, k_(28), P["stone_dark"])
a = wall_stair(DON[0], DON[1], G + 0.1, KY, DON_IN - 1.7, DON_IN - 0.05, add.pi * 1.35)       # up to the hall door ...
add.mesh(solid([(DON[0] + rr * add.cos(aa), DON[1] + rr * add.sin(aa)) for rr, aa in                 # ... a landing there ...
                ((DON_IN - 1.7, a), (DON_IN - 0.05, a), (DON_IN - 0.05, a + 0.5), (DON_IN - 1.7, a + 0.5))], KY - 0.24, KY, P["stone_dark"]))
WALL_HEAD = 10 * (0.3 / (DON_IN - 0.875))                                                       # 10 steps of the wall stair: 10 x 0.24 - 0.4 = 2 m of headroom
a = wall_stair(DON[0], DON[1], KY, F1, DON_IN - 1.7, DON_IN - 0.05, a + 0.5)                   # ... and on to the armoury
disc_with_hole(DON[0], DON[1], DON_IN + 0.2, F1, 0.4, DON_IN - 1.7, a - WALL_HEAD, a, P["wood"])
a = wall_stair(DON[0], DON[1], F1, F2, DON_IN - 1.7, DON_IN - 0.05, a + 0.1)
disc_with_hole(DON[0], DON[1], DON_IN + 0.2, F2, 0.4, DON_IN - 1.7, a - WALL_HEAD, a, P["wood"])
a = wall_stair(DON[0], DON[1], F2, DON_TOP, DON_IN - 1.7, DON_IN - 0.05, a + 0.1)
disc_with_hole(DON[0], DON[1], DON_IN + 0.2, DON_TOP, 0.4, DON_IN - 1.7, a - WALL_HEAD, a, P["stone_dark"])
guard_wall(DON[0], DON[1], a - WALL_HEAD, DON_IN - 2.05, DON_IN + 0.35, DON_TOP)                # the lookout's stairwell: a low stone
guard_arc(DON[0], DON[1], DON_IN - 2.05, DON_IN - 1.7, a - WALL_HEAD, a - 0.15, DON_TOP)        # wall round the drop, open where one arrives
kk = k_(28)
rook_top(DON[0], DON[1], DON_R, DON_IN + 0.2, DON_TOP, kk)                                     # corbels and merlons, then the lantern and spire
for i in range(10):                                                                   # the lantern: stout posts and braces
    aa = 2 * add.pi * i / 10
    px, pz = DON[0] + (DON_R - 0.4) * add.cos(aa), DON[1] + (DON_R - 0.4) * add.sin(aa)
    add.cuboid([px, DON_TOP + 0.35 + 1.475, pz], [0.45, 2.95, 0.45], P["wood_dark"])
    add.cuboid([px, DON_TOP + 0.47, pz], [0.65, 0.24, 0.65], P["stone_dark"])
    for s in (-1, 1):
        q = [DON[0] + (DON_R - 0.4) * add.cos(aa + s * 0.24), DON_TOP + 3.25, DON[1] + (DON_R - 0.4) * add.sin(aa + s * 0.24)]
        add.beam([px, DON_TOP + 2.2, pz], q, 0.15, 0.15, P["wood_dark"])
add.pipe([DON[0], DON_TOP + 3.3, DON[1]], [DON[0], DON_TOP + 3.65, DON[1]], DON_R + 0.9, DON_R - 0.75, kk, P["wood_dark"])
cone_roof([DON[0], 0, DON[1]], DON_TOP + 3.65, DON_R + 0.9, 12, kk, color=P["spire"])
add.cylinder([DON[0], DON_TOP + 15.7, DON[1]], [DON[0], DON_TOP + 20, DON[1]], 0.06, 8, P["iron"])   # the flagpole
add.sphere([DON[0], DON_TOP + 20.05, DON[1]], 0.1, 6, P["gold"])
flag([DON[0], DON_TOP + 19.9, DON[1]], 1.8, 1.2, add.pi * 0.3)
flush("palace: donjon")

# the hip roof: a solid (cut where the towers pass through it) covered
# with rows of individual clay tiles in the shades of the spires
OVER = 0.7
INSET = 8.0


ROOF_T = 0.35                                          # the roof shell: rafters and boards, this thick
DORMER_D = 4.0                                         # a dormer reaches this far back from its face
DORMER_IN = 1.2                                        # ... and its face stands this far up from the eaves


def hip_roof(x0, x1, z0, z1, y, h, inset=INSET, over=OVER, cutters=(), dormers=(), blocked=None):
    """A hipped roof as a hollow shell ``ROOF_T`` thick -- the attic is a
    real room under it -- tiled outside, with walk-in dormers: a bay you
    step up into from the attic floor, a window in its face."""
    ex0, ex1, ez0, ez1 = x0 - over, x1 + over, z0 - over, z1 + over
    zc = (z0 + z1) / 2
    r0, r1 = [x0 + inset, y + h, zc], [x1 - inset, y + h, zc]
    south = ([ex0, y, ez1], [ex1, y, ez1], r1, r0)
    north = ([ex1, y, ez0], [ex0, y, ez0], r0, r1)
    east = ([ex1, y, ez1], [ex1, y, ez0], r1, r1)
    west = ([ex0, y, ez0], [ex0, y, ez1], r0, r0)
    # the inner surface: every plane moved in by ROOF_T
    tz, tx = add.atan2(h, ez1 - zc), add.atan2(h, inset + over)          # the pitch of the long and the hip slopes
    dz, dx = ROOF_T / add.sin(tz), ROOF_T / add.sin(tx)
    yr = y + h - ROOF_T / add.cos(tz)                                    # the inner ridge ...
    xr = (inset + over) * (1 - ROOF_T / (h * add.cos(tz))) + dx            # ... ends this far in from the outer eaves' ends
    ir0, ir1 = [ex0 + xr, yr, zc], [ex1 - xr, yr, zc]
    ix0, ix1, iz0, iz1 = ex0 + dx, ex1 - dx, ez0 + dz, ez1 - dz
    shell = add.Mesh()
    for face in (south, north, east, west):
        shell.add_polygon([face[0], face[1], face[2]] + ([face[3]] if face[3] is not face[2] else []), P["spire"])
    for face in (([ix0, y, iz1], [ix1, y, iz1], ir1, ir0), ([ix1, y, iz0], [ix0, y, iz0], ir0, ir1),
                 ([ix1, y, iz1], [ix1, y, iz0], ir1, ir1), ([ix0, y, iz0], [ix0, y, iz1], ir0, ir0)):
        pts = [face[0], face[1], face[2]] + ([face[3]] if face[3] is not face[2] else [])
        shell.add_polygon(pts[::-1], P["wood_dark"])                     # the underside of the boards, seen from the attic
    ring = [([ex0, y, ez0], [ex1, y, ez0], [ix1, y, iz0], [ix0, y, iz0]), ([ex1, y, ez0], [ex1, y, ez1], [ix1, y, iz1], [ix1, y, iz0]),
            ([ex1, y, ez1], [ex0, y, ez1], [ix0, y, iz1], [ix1, y, iz1]), ([ex0, y, ez1], [ex0, y, ez0], [ix0, y, iz0], [ix0, y, iz1])]
    for q in ring:                                                       # the eaves' soffit
        shell.add_polygon(q, P["wood_dark"])
    shell = add.fix_normals(add.clean(shell))
    bays = []
    for x in dormers:                                                    # the bay of every dormer, cut through the shell
        for sg in (1, -1):
            zf = (ez1 - DORMER_IN) if sg > 0 else (ez0 + DORMER_IN)
            yf = y + h * DORMER_IN / (ez1 - zc)
            bays.append(add.make(add.cuboid, [x, yf + 1.4, zf - sg * (DORMER_D / 2 - 0.1)], [1.8, 2.8, DORMER_D - 0.2]))
    if cutters or bays:
        shell = add.difference(shell, *(list(cutters) + bays))
    add.mesh(shell)

    def bay(xx, zz):
        deep = min(abs(zz - ez1), abs(zz - ez0))
        return any(abs(xx - dxr) < 1.3 and DORMER_IN - 0.1 < deep < DORMER_IN + DORMER_D + 0.15 for dxr in dormers)

    keep_out = (lambda xx, zz: bay(xx, zz) or (blocked(xx, zz) if blocked else False))
    for face in (south, north, east, west):
        tile_face(*face, blocked=keep_out)
    add.cuboid([(x0 + x1) / 2, y + h, zc], [x1 - x0 - 2 * inset + 0.4, 0.3, 0.5], shade_of("spire", 2))   # ridge cap, in the tiles' colour
    for x in dormers:                                                    # the dormers, both sides
        for sg in (1, -1):
            zf = (ez1 - DORMER_IN) if sg > 0 else (ez0 + DORMER_IN)
            yf = y + h * DORMER_IN / (ez1 - zc)
            zb = zf - sg * DORMER_D                                      # the back of the bay
            box = add.make(add.cuboid, [x, yf + 1.1, (zf + zb) / 2], [2.4, 2.8, DORMER_D], P["mortar"])
            hollow = add.make(add.cuboid, [x, yf + 1.2, (zf + zb) / 2], [1.8, 2.4, DORMER_D - 0.6])   # walls 0.3 thick all round
            doorway = add.make(add.cuboid, [x, yf + 0.9, zb], [1.8, 1.8, 1.0])               # a doorway in the back, from the attic
            window = arch_solid(x, yf + 0.55, 1.2, 1.7, zf, 0.8)                              # the window through the face
            add.mesh(add.color(add.difference(box, hollow, doorway, window), P["mortar"]))    # (one cutter each: they overlap)
            add.push()                                                   # stone facing of the front, fitted round the window
            stone_face(2.4, 0, 2.8, 0, 0.1, "stone", size=(0.6, 0.3), seed=int(x), skip=[(0.5, 1.9, 0.79, 2.65, (1.2, 1.95, 0.7))])
            face = add.move(add.pop(), [-1.2, yf - 0.3, 0])
            add.mesh(add.move(face if sg > 0 else add.mirror(face, [0, 0, 0], [0, 0, 1]), [x, 0, zf]))
            add.mesh(add.move(add.make(add.roof, [0, 0, 0], [2.8, DORMER_D + 0.3], 1.4, P["spire"], 0.15), [x, yf + 2.5, (zf + zb) / 2]))
            add.mesh(add.color(arch_solid(x, yf + 0.55, 1.14, 1.64, zf - sg * 0.15, 0.06), GLASS))   # the pane, mid-wall
            add.cuboid([x, yf + 1.35, zf - sg * 0.15], [0.08, 1.7, 0.1], P["glass_frame"])   # mullion and transom
            add.cuboid([x, yf + 1.2, zf - sg * 0.15], [1.2, 0.08, 0.1], P["glass_frame"])
            add.cuboid([x, yf + 0.55, zf - sg * 0.5], [1.6, 0.1, 1.0], P["stone_dark"])       # the sill ledge inside
            rise = (yf - y) / 3
            for i in range(3):                                           # three steps up from the attic floor into the bay
                add.cuboid([x, y + (i + 1) * rise / 2, zb - sg * (0.35 * (2 - i) + 0.175)], [1.6, (i + 1) * rise, 0.35], shade_of("wood", i))


def arch_solid(cx, y0, w, h, z, depth):
    """An arched opening (like a doorway) as a solid, to cut through a
    wall along z: ``w`` wide, ``h`` tall on ``y0``, centred on (cx, z)."""
    return add.make(add.prism, [[sx, sy] for sx, sy in arch_profile(y0, w, h)], depth, None, (cx, 0, z), (0, 0, 1))


hip_roof(KX0, KX1, KZ0, KZ1, EAVE, ROOF_H, cutters=tower_cutters(EAVE - 1, RIDGE_Y + 2), dormers=(-12, 0, 12),
         blocked=lambda x, z: near_tower(x, z, 0.4))
# the chimney of the great hall's fireplace, on the west wall, through the roof
CHIM_X, CHIM_Z = KX0 + 1.0, (KZ0 + KZ1) / 2
brick_box([CHIM_X, (EAVE + EAVE + 6.5) / 2, CHIM_Z], [1.6, 6.5, 2.0])
add.cuboid([CHIM_X, EAVE + 6.6, CHIM_Z], [2.0, 0.3, 2.4], P["stone_dark"])
for i in range(count(8)):                                                             # smoke
    add.sphere([CHIM_X + 0.3 * add.sin(i), EAVE + 7.2 + i * 0.8, CHIM_Z + 0.3 * add.cos(i * 1.3)], 0.35 + 0.1 * i, 8, SMOKE)
flush("palace: roof")

# the balconies of the south front, each behind its glazed doors
for bx in BALCONY_X:
    add.cuboid([bx, FLOOR2 - 0.15, KZ1 + 0.6 + 0.9], [4.4, 0.3, 1.8], P["stone_dark"])
    for dx in (-1.9, 1.9):
        add.cuboid([bx + dx, FLOOR2 - 0.7, KZ1 + 0.6 + 0.4], [0.4, 0.8, 0.8], P["stone_dark"])
    rail = FLOOR2
    for i in range(9):
        x = bx - 2.0 + i * 0.5
        add.cylinder([x, rail, KZ1 + 0.6 + 1.7], [x, rail + 0.9, KZ1 + 0.6 + 1.7], 0.07, 12, P["stone"])
    for dz in range(4):
        for dx in (-2.1, 2.1):
            add.cylinder([bx + dx, rail, KZ1 + 0.6 + 0.35 + dz * 0.45], [bx + dx, rail + 0.9, KZ1 + 0.6 + 0.35 + dz * 0.45], 0.07, 12, P["stone"])
    add.cuboid([bx, rail + 0.95, KZ1 + 0.6 + 1.7], [4.5, 0.12, 0.2], P["stone"])
    for dx in (-2.15, 2.15):
        add.cuboid([bx + dx, rail + 0.95, KZ1 + 0.6 + 1.0], [0.2, 0.12, 1.6], P["stone"])
# the porch over the main door: two columns and a slab
for s in (-1, 1):
    add.column([s * 2.8, KY, KZ1 + PL + 2.4], 5.0, 0.35, P["stone"], k_(14))
add.cuboid([0, KY + 5.3, KZ1 + PL + 1.15], [7.6, 0.5, 2.9], P["stone"])
flush("palace: balconies and porch")

# the chapel wing on the east side: stained glass, a gable roof and a spire
CH_X0, CH_X1, CH_Z0, CH_Z1 = KX1, 34.0, KZ0 + 7, KZ1 - 7
CH_TOP = KY + 9.0
CH_C = ((CH_X0 + CH_X1) / 2, (CH_Z0 + CH_Z1) / 2)
chapel_east = [opening(z, 1.2, 7.6, 1.7, kind="stained") for z in (2.5, 7.0, 11.5)]
chapel_south = [opening(6, 0, DOOR_H, DOOR_W, kind="door"), opening(2.5, 2.0, 6.5, 1.4, kind="stained"), opening(9.5, 2.0, 6.5, 1.4, kind="stained")]
chapel_north = [opening(6, 1.0, 8.0, 3.2, kind="stained")]
for a, b, ops in (((CH_X1, CH_Z0), (CH_X1, CH_Z1), chapel_east), ((CH_X0, CH_Z1), (CH_X1, CH_Z1), chapel_south),
                  ((CH_X1, CH_Z0), (CH_X0, CH_Z0), chapel_north)):
    length = abs(b[0] - a[0]) + abs(b[1] - a[1])
    stand_wall(pierced_wall(length, CH_TOP - KY, ops), a, b, KY, centre=CH_C)
add.cuboid([CH_C[0], (G - 0.5 + KY) / 2, CH_C[1]], [CH_X1 - CH_X0 + PL, KY - G + 0.5, CH_Z1 - CH_Z0 + 2 * PL], P["stone_dark"])
add.stairs([CH_C[0], G, CH_Z1 + PL + 1.8], 4, 4.0, (KY - G) / 4, 0.45, P["stone_dark"], direction=(0, 0, -1))
add.roof([CH_C[0], CH_TOP, CH_C[1]], [CH_X1 - CH_X0 + 1.0, CH_Z1 - CH_Z0 + 1.0], 7.0, P["slate"], 0.4)
for sg in (-1, 1):                                                              # slates on both slopes
    eave_x = CH_C[0] + sg * ((CH_X1 - CH_X0 + 1.0) / 2 + 0.4)
    ez0, ez1 = CH_C[1] - (CH_Z1 - CH_Z0 + 1.0) / 2 - 0.4, CH_C[1] + (CH_Z1 - CH_Z0 + 1.0) / 2 + 0.4
    A, B = [eave_x, CH_TOP, ez1 if sg > 0 else ez0], [eave_x, CH_TOP, ez0 if sg > 0 else ez1]
    D, C = [CH_C[0], CH_TOP + 7.0, A[2]], [CH_C[0], CH_TOP + 7.0, B[2]]
    tile_face(A, B, C, D, size=(0.45, 0.4), colours="slate")
add.cuboid([CH_X1 + 0.3, CH_TOP - 0.3, CH_C[1]], [0.6, 0.6, CH_Z1 - CH_Z0 + 1.0], P["stone_dark"])   # cornice
add.cylinder([CH_C[0], CH_TOP + 5.5, CH_C[1]], [CH_C[0], CH_TOP + 8.5, CH_C[1]], 1.0, 8, P["stone"])
add.cone([CH_C[0], CH_TOP + 8.5, CH_C[1]], [CH_C[0], CH_TOP + 17.5, CH_C[1]], 1.3, 8, P["spire"])
add.sphere([CH_C[0], CH_TOP + 17.8, CH_C[1]], 0.3, 8, P["gold"])
add.cuboid([CH_C[0], CH_TOP + 18.9, CH_C[1]], [0.1, 1.6, 0.1], P["gold"])                      # the cross
add.cuboid([CH_C[0], CH_TOP + 19.2, CH_C[1]], [0.8, 0.1, 0.1], P["gold"])
flush("chapel")


# --------------------------------------------------------------------------
#  5. Props: furniture, food, vessels, weapons -- everything is built at
#     the origin and then moved into place
# --------------------------------------------------------------------------
def lathe(points, at, k, color, scale=1.0):
    """A turned object (goblet, jug, bowl, candlestick): ``points`` are
    ``[radius, height]`` pairs of the profile, bottom first."""
    n = len(points) - 1
    pts = [[r * scale, h * scale] for r, h in points]
    add.revolve(lambda t: pts[min(n, int(round(t)))], at, [at[0], at[1] + 1, at[2]], 0, n, n, k, color)


def goblet(at, color=None):
    lathe([[0.0, 0], [0.13, 0], [0.13, 0.02], [0.04, 0.05], [0.04, 0.2], [0.07, 0.24], [0.15, 0.3],
           [0.16, 0.45], [0.12, 0.45], [0.11, 0.3], [0.0, 0.28]], at, k_(8), color or P["gold"])


def jug(at, color=None):
    color = color or P["brick"]
    lathe([[0.0, 0], [0.16, 0], [0.24, 0.15], [0.26, 0.35], [0.18, 0.5], [0.15, 0.6], [0.17, 0.66],
           [0.12, 0.66], [0.11, 0.55], [0.0, 0.5]], at, k_(8), color)
    add.torus([at[0] + 0.24, at[1] + 0.4, at[2]], 0.13, 0.03, k_(8), 8, color, axis=(0, 0, 1))


def bowl(at, r=0.35, color=None, fruit=None):
    color = color or P["wood_light"]
    lathe([[0.0, 0], [r * 0.5, 0], [r * 0.9, r * 0.35], [r, r * 0.5], [r * 0.9, r * 0.5], [r * 0.8, r * 0.35],
           [r * 0.4, r * 0.12], [0.0, r * 0.12]], at, k_(10), color)
    if fruit:
        for i in range(7):
            a = 2 * add.pi * i / 6
            rr = r * 0.5 if i < 6 else 0
            add.sphere([at[0] + rr * add.cos(a), at[1] + r * 0.35 + (0.05 if i == 6 else 0), at[2] + rr * add.sin(a)],
                       r * 0.3, 6, fruit[i % len(fruit)])


def candle(at, h=0.35, r=0.04):
    add.cylinder(at, [at[0], at[1] + h, at[2]], r, 12, P["white"])
    add.cylinder([at[0], at[1] + h, at[2]], [at[0], at[1] + h + 0.05, at[2]], 0.008, 4, P["black"])
    add.sphere([at[0], at[1] + h + 0.12, at[2]], 0.07, 6, FLAME)
    add.sphere([at[0], at[1] + h + 0.1, at[2]], 0.03, 4, P["flame_core"])


def candelabra(at, arms=3, h=0.6):
    lathe([[0.0, 0], [0.18, 0], [0.18, 0.03], [0.05, 0.06], [0.05, h - 0.1], [0.08, h], [0.0, h]], at, k_(8), P["gold"])
    for i in range(arms):
        a = 2 * add.pi * i / arms
        tip = [at[0] + 0.3 * add.cos(a), at[1] + h + 0.05, at[2] + 0.3 * add.sin(a)]
        add.polyline([[at[0], at[1] + h - 0.25, at[2]], [at[0] + 0.2 * add.cos(a), at[1] + h - 0.2, at[2] + 0.2 * add.sin(a)], tip],
                     0.025, 8, P["gold"], smooth=1)
        candle(tip, 0.3, 0.035)


def plate(at, r=0.3):
    add.cylinder(at, [at[0], at[1] + 0.03, at[2]], r, k_(10), P["steel"])


def chicken_roast(at):
    plate(at, 0.4)
    add.mesh(add.move(add.stretch(add.make(add.sphere, [0, 0, 0], 0.3, 8, P["meat"]), [1.0, 0.7, 0.8], (0, 0, 0)), [at[0], at[1] + 0.22, at[2]]))
    for s in (-1, 1):
        add.capsule([at[0] + s * 0.15, at[1] + 0.12, at[2] + 0.1], [at[0] + s * 0.32, at[1] + 0.3, at[2] + 0.28], 0.06, 12, P["meat"])
        add.sphere([at[0] + s * 0.34, at[1] + 0.32, at[2] + 0.3], 0.05, 4, P["bone"])


def bread(at, n=1):
    for i in range(n):
        loaf = add.stretch(add.make(add.sphere, [0, 0, 0], 0.22, 8, P["bread"]), [1.5, 0.7, 1.0], (0, 0, 0))
        add.mesh(add.move(add.rotateY(loaf, i * 0.7), [at[0] + 0.25 * i, at[1] + 0.15, at[2] + 0.1 * i]))


def cheese(at):
    add.mesh(add.move(add.make(add.revolve, lambda t: [0.32, 0.22 * t], [0, 0, 0], [0, 1, 0], 0, 1, 1, k_(10),
                               P["cheese"], 2 * add.pi * 0.8), at))
    add.mesh(add.move(add.make(add.prism, [[0, 0], [0.3, -0.1], [0.3, 0.1]], 0.2, P["cheese"], (0, 0, 0)),
                      [at[0] + 0.55, at[1] + 0.1, at[2] + 0.3]))


def grapes(at, n=12):
    for i in range(n):
        a = 2.4 * i
        rr = 0.12 * (1 - i / float(n)) + 0.02
        add.sphere([at[0] + rr * add.cos(a), at[1] + 0.25 - 0.018 * i, at[2] + rr * add.sin(a)], 0.045, 5, P["grape"])
    add.cylinder([at[0], at[1] + 0.25, at[2]], [at[0] + 0.1, at[1] + 0.35, at[2]], 0.01, 4, P["leaf_dark"])


def fruit(at, color, r=0.12):
    add.sphere([at[0], at[1] + r, at[2]], r, 8, color)
    add.cylinder([at[0], at[1] + 2 * r - 0.02, at[2]], [at[0] + 0.02, at[1] + 2 * r + 0.06, at[2]], 0.01, 4, P["trunk"])


def roast_pig(at):
    """The centrepiece of the feast: a whole roast pig on a big platter.
    The ears grow out of the head, the tail out of the rump, the herbs are
    stuck into the back -- nothing floats."""
    plate(at, 1.1)
    add.push()
    add.mesh(add.stretch(add.make(add.sphere, [0, 0.42, 0], 0.42, 10, P["pig"]), [1.0, 0.85, 2.0], (0, 0.42, 0)))     # body
    head = [0, 0.5, -0.95]
    add.sphere(head, 0.3, 10, P["pig"])
    add.cylinder([0, 0.45, -1.15], [0, 0.45, -1.35], 0.1, 12, P["pig"])                                   # snout
    add.cylinder([0, 0.45, -1.35], [0, 0.45, -1.37], 0.1, 12, P["cushion"])
    add.sphere([0, 0.14, -1.36], 0.11, 8, P["apple"])                                                      # the apple: in the mouth, resting on the platter
    add.mesh(add.stretch(add.make(add.sphere, [0, 0.3, -1.3], 0.09, 8, P["pig"]), [1.0, 1.4, 0.6], (0, 0.3, -1.3)))   # the lower jaw, open on the apple
    for s in (-1, 1):
        add.sphere([s * 0.12, 0.6, -1.2], 0.03, 4, P["black"])                                             # eyes
        add.cone([s * 0.12, 0.55, -0.92], [s * 0.26, 0.85, -1.0], 0.1, 8, P["pig"])                        # ears, rooted in the head
        add.capsule([s * 0.35, 0.3, -0.6], [s * 0.5, 0.08, -0.85], 0.09, 12, P["pig"])                     # legs
        add.capsule([s * 0.35, 0.3, 0.6], [s * 0.5, 0.08, 0.85], 0.09, 12, P["pig"])
    add.helix([0, 0.55, 0.82], 0.06, 0.05, 2.5, 30, 0.015, 6, P["pig"], axis=(0, 0, 1))                    # the curly tail, from the rump
    for i in range(6):                                                                                     # herbs stuck into the back
        add.cylinder([0.1 * add.sin(i), 0.6, -0.5 + i * 0.2], [0.15 * add.cos(i), 0.95, -0.4 + i * 0.2], 0.012, 5, P["leaf"])
    add.mesh(add.move(add.pop(), [at[0], at[1] + 0.03, at[2]]))


def barrel(at, r=0.45, h=1.2, k=None, upright=True):
    """A barrel of separate staves with three iron hoops."""
    k = k or k_(14)
    add.push()
    for i in range(k):
        a0, a1 = 2 * add.pi * i / k, 2 * add.pi * (i + 0.93) / k
        prof = [[r * 0.9, 0], [r, h / 2], [r * 0.9, h]]
        piece = add.make(add.revolve, lambda t: prof[min(2, int(round(t)))], [0, 0, 0], [0, 1, 0], 0, 2, 2, 1,
                         pick("wood", i, 3), angle=a1 - a0, caps=False)
        add.mesh(add.rotateY(piece, -a0))
    for t in (0.12, 0.5, 0.88):
        rr = r * (0.9 + 0.1 * add.sin(add.pi * t))
        add.torus([0, h * t, 0], rr, 0.035, k, 8, P["iron"])
    add.cylinder([0, h - 0.08, 0], [0, h - 0.03, 0], r * 0.88, k, P["wood_dark"])
    add.cylinder([0, 0.03, 0], [0, 0.08, 0], r * 0.88, k, P["wood_dark"])
    M = add.pop()
    if not upright:
        M = add.rotateX(M, add.pi / 2)
        M = add.move(M, [0, r, h / 2])
    add.mesh(add.move(M, at))


def crate(at, s=0.9):
    """A wooden crate: planks with corner posts and an iron strap."""
    add.push()
    for i in range(4):
        add.cuboid([0, s * (i + 0.5) / 4, s / 2], [s, s / 4 - 0.02, 0.06], pick("wood_light", i, 1))
        add.cuboid([0, s * (i + 0.5) / 4, -s / 2], [s, s / 4 - 0.02, 0.06], pick("wood_light", i, 2))
        add.cuboid([s / 2, s * (i + 0.5) / 4, 0], [0.06, s / 4 - 0.02, s], pick("wood_light", i, 3))
        add.cuboid([-s / 2, s * (i + 0.5) / 4, 0], [0.06, s / 4 - 0.02, s], pick("wood_light", i, 4))
    add.cuboid([0, s - 0.03, 0], [s, 0.06, s], P["wood"])
    for sx in (-1, 1):
        for sz in (-1, 1):
            add.cuboid([sx * s / 2, s / 2, sz * s / 2], [0.1, s, 0.1], P["wood_dark"])
    add.cuboid([0, s / 2, 0], [s + 0.04, 0.12, s + 0.04], P["iron"])
    add.mesh(add.move(add.pop(), at))


def sack(at, r=0.4):
    add.mesh(add.move(add.stretch(add.make(add.sphere, [0, 0, 0], r, 8, P["sand"]), [1.0, 0.8, 1.0], (0, 0, 0)), [at[0], at[1] + r * 0.7, at[2]]))
    add.cylinder([at[0], at[1] + r * 1.4, at[2]], [at[0] + 0.05, at[1] + r * 1.7, at[2]], r * 0.3, 12, P["sand"])
    add.torus([at[0], at[1] + r * 1.5, at[2]], r * 0.3, 0.015, 12, 6, P["rope"])


def sword(at, up=(0, 1, 0), length=1.1, color=None, side=None):
    """A sword whose point is at ``at`` and whose blade runs along ``up``;
    ``side`` (optional) is the direction of the cross-guard, i.e. the flat
    of the blade -- give it for a sword hung flat against a wall."""
    color = color or P["steel"]
    u = vunit(up)
    tip = at
    hilt = [at[k] + u[k] * length for k in range(3)]
    grip = [at[k] + u[k] * (length + 0.3) for k in range(3)]
    if side is None:
        helper = [0, 0, 1] if abs(u[2]) < 0.9 else [1, 0, 0]
        side = vunit(vcross(u, helper))
        add.beam([at[k] + u[k] * 0.1 for k in range(3)], hilt, 0.12, 0.02, color)
    else:
        side = vunit(side)
        add.beam([at[k] + u[k] * 0.1 for k in range(3)], hilt, 0.02, 0.12, color, up=side)
    add.cone([at[k] + u[k] * 0.1 for k in range(3)], tip, 0.05, 4, color)
    add.beam([hilt[k] - side[k] * 0.2 for k in range(3)], [hilt[k] + side[k] * 0.2 for k in range(3)], 0.05, 0.05, P["gold"])
    add.cylinder(hilt, grip, 0.035, 8, P["wood_dark"])
    add.sphere(grip, 0.06, 6, P["gold"])


def spear(at, length=3.0):
    add.cylinder(at, [at[0], at[1] + length, at[2]], 0.035, 8, P["wood"])
    add.cone([at[0], at[1] + length, at[2]], [at[0], at[1] + length + 0.45, at[2]], 0.07, 8, P["steel"])


def axe(at, length=1.2):
    add.cylinder(at, [at[0], at[1] + length, at[2]], 0.035, 8, P["wood"])
    add.mesh(add.move(add.make(add.prism, [[0, -0.25], [0.35, -0.3], [0.4, 0.3], [0, 0.2]], 0.04, P["steel"], (0, 0, 0), (0, 0, 1)),
                      [at[0], at[1] + length - 0.35, at[2]]))


def shield(at, facing=0.0, r=0.5):
    """A round shield with the castle's arms, standing on edge."""
    M = add.make(add.cylinder, [0, r, -0.03], [0, r, 0.03], r, k_(16), P["red"])
    M.extend(add.make(add.torus, [0, r, 0], r - 0.02, 0.03, k_(16), 8, P["iron"], axis=(0, 0, 1)))       # the rim
    band = add.make(add.cuboid, [0, 0, 0], [r * 0.3, r * 1.9, 0.012], P["gold"])                           # the bend
    M.extend(add.move(add.rotateZ(band, add.pi / 4), [0, r, 0.035]))
    for a in (add.pi / 2 + 0.9, add.pi / 2 - 0.9, -add.pi / 2):                                            # the roundels
        M.extend(add.make(add.cylinder, [r * 0.55 * add.cos(a), r + r * 0.55 * add.sin(a), 0.03],
                          [r * 0.55 * add.cos(a), r + r * 0.55 * add.sin(a), 0.045], r * 0.17, 10, P["white"]))
    M.extend(add.make(add.sphere, [0, r, 0.06], 0.1, 8, P["iron"]))                                          # the boss
    add.mesh(add.move(add.rotateY(M, facing), at))


def torch(at, facing=0.0):
    """A wall torch: an iron bracket on the wall, a wooden shaft, a flame.
    ``at`` is the point on the wall, ``facing`` the direction out of it."""
    add.push()
    add.cuboid([0, 0, 0.1], [0.1, 0.5, 0.2], P["iron"])
    add.cylinder([0, -0.2, 0.3], [0, 0.6, 0.35], 0.05, 8, P["wood_dark"])
    add.cylinder([0, 0.55, 0.35], [0, 0.75, 0.35], 0.09, 8, P["rope"])
    add.sphere([0, 0.9, 0.35], 0.16, 8, FLAME)
    add.sphere([0, 0.85, 0.35], 0.08, 6, P["flame_core"])
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def chandelier(at, r=1.1, hang=2.0):
    """A ring of candles hanging on chains from the ceiling."""
    add.torus(at, r, 0.05, k_(20), 8, P["iron"])
    for i in range(8):
        a = 2 * add.pi * i / 8
        p = [at[0] + r * add.cos(a), at[1] + 0.05, at[2] + r * add.sin(a)]
        add.cylinder([p[0], p[1] - 0.06, p[2]], [p[0], p[1] + 0.08, p[2]], 0.07, 8, P["iron"])
        candle([p[0], p[1] + 0.08, p[2]], 0.3, 0.035)
    top = [at[0], at[1] + hang, at[2]]
    for i in range(3):
        a = 2 * add.pi * i / 3
        chain([at[0] + r * add.cos(a), at[1], at[2] + r * add.sin(a)], top, 0.07, 0.015)
    add.cylinder(top, [top[0], top[1] + 0.3, top[2]], 0.12, 8, P["iron"])


def chair(at, facing=0.0, color=None):
    color = color or P["wood"]
    add.push()
    add.cuboid([0, 0.45, 0], [0.5, 0.06, 0.5], color)
    for sx in (-0.2, 0.2):
        for sz in (-0.2, 0.2):
            add.cuboid([sx, 0.22, sz], [0.05, 0.45, 0.05], color)
        add.cuboid([sx, 0.75, -0.22], [0.05, 0.6, 0.05], color)
    add.cuboid([0, 0.85, -0.22], [0.5, 0.25, 0.04], color)
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def table(at, w, d, h=0.8, color=None, cloth=False):
    color = color or P["wood"]
    add.push()
    add.cuboid([0, h - 0.05, 0], [w, 0.1, d], color)
    for sx in (-w / 2 + 0.15, w / 2 - 0.15):
        for sz in (-d / 2 + 0.15, d / 2 - 0.15):
            add.cuboid([sx, (h - 0.1) / 2, sz], [0.12, h - 0.1, 0.12], P["wood_dark"])
    if cloth:
        add.cuboid([0, h + 0.015, 0], [w + 0.2, 0.03, d + 0.2], P["white"])
    add.mesh(add.move(add.pop(), at))


def bed(at, facing=0.0, sleeper=True, canopy=False):
    """A wooden bed with a mattress, pillow and blanket -- and someone
    asleep under the blanket, head on the pillow."""
    add.push()
    add.cuboid([0, 0.3, 0], [1.1, 0.12, 2.2], P["wood"])
    for sx in (-0.5, 0.5):
        for sz, hh in ((-1.05, 0.9), (1.05, 0.6)):
            add.cuboid([sx, hh / 2, sz], [0.1, hh, 0.1], P["wood_dark"])
    add.cuboid([0, 0.7, -1.05], [1.1, 0.4, 0.06], P["wood_dark"])                              # headboard
    add.cuboid([0, 0.5, 1.05], [1.1, 0.2, 0.06], P["wood_dark"])
    add.cuboid([0, 0.46, 0], [1.0, 0.2, 2.1], P["linen"])                                       # mattress
    add.mesh(add.move(add.stretch(add.make(add.sphere, [0, 0, 0], 0.25, 8, P["white"]), [1.4, 0.45, 0.9], (0, 0, 0)), [0, 0.62, -0.75]))
    if sleeper:
        add.sphere([0, 0.72, -0.72], 0.17, 8, P["skin"])                                         # the head on the pillow
        add.mesh(add.move(add.stretch(add.make(add.sphere, [0, 0, 0], 0.4, 8, P["red"]), [1.1, 0.5, 1.9], (0, 0, 0)), [0, 0.62, 0.15]))   # blanket over the body
    else:
        add.cuboid([0, 0.6, 0.2], [0.95, 0.06, 1.5], P["red"])                                    # a folded blanket
    if canopy:
        for sx in (-0.55, 0.55):
            for sz in (-1.1, 1.1):
                add.cylinder([sx, 0, sz], [sx, 2.4, sz], 0.06, 12, P["wood_dark"])
        add.cuboid([0, 2.45, 0], [1.4, 0.1, 2.5], P["red"])
        for sz in (-1.1, 1.1):
            add.cuboid([0, 2.25, sz], [1.3, 0.3, 0.04], P["gold"])
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def chest(at, facing=0.0, open_lid=False, s=1.0):
    add.push()
    add.cuboid([0, 0.4 * s, 0], [1.6 * s, 0.8 * s, 1.0 * s], P["wood_dark"])
    add.cuboid([0, 0.5 * s, 0], [1.66 * s, 0.12 * s, 1.06 * s], P["iron"])
    for sx in (-0.7, 0.7):
        add.cuboid([sx * s, 0.4 * s, 0], [0.1 * s, 0.82 * s, 1.06 * s], P["iron"])
    lid = add.make(add.cuboid, [0, 0.12 * s, 0], [1.6 * s, 0.24 * s, 1.0 * s], P["wood_dark"])
    if open_lid:
        lid = add.rotateX(lid, -1.9, (0, 0, -0.5 * s))
    add.mesh(add.move(lid, [0, 0.8 * s, 0]))
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def chess_piece(kind, x, y, z, color, s=1.0):
    """A pawn or a king, standing on square centre (x, z) at table height y
    (``s`` scales the piece)."""
    add.cylinder([x, y, z], [x, y + 0.03 * s, z], 0.045 * s, 12, color)
    if kind == "P":
        add.cylinder([x, y + 0.03 * s, z], [x, y + 0.09 * s, z], 0.022 * s, 10, color)
        add.sphere([x, y + 0.115 * s, z], 0.03 * s, 6, color)
    else:                                                                          # K
        add.cylinder([x, y + 0.03 * s, z], [x, y + 0.2 * s, z], 0.028 * s, 10, color)
        add.cylinder([x, y + 0.2 * s, z], [x, y + 0.23 * s, z], 0.04 * s, 10, color)
        add.cuboid([x, y + 0.29 * s, z], [0.02 * s, 0.1 * s, 0.02 * s], P["gold"])      # the cross
        add.cuboid([x, y + 0.31 * s, z], [0.07 * s, 0.02 * s, 0.02 * s], P["gold"])


def chess_study(at, square=0.2):
    """A chess study set up on a big table: White to play and win.
    White: Kg1, pawns a2 b2 c5 d5 f5.  Black: Kh4, pawns b4 c7 d7 g7 h7 g2."""
    s = square / 0.125                                                             # the pieces grow with the squares
    board = 8 * square
    table(at, board + 0.4, board + 0.4, 0.72, P["wood_dark"])
    for i in range(8):
        for j in range(8):
            x, z = at[0] - 3.5 * square + i * square, at[2] - 3.5 * square + j * square
            add.cuboid([x, at[1] + 0.735, z], [square, 0.03, square], P["white"] if (i + j) % 2 else P["black"])
    position = {"white": [("K", "g1"), ("P", "a2"), ("P", "b2"), ("P", "c5"), ("P", "d5"), ("P", "f5")],
                "black": [("K", "h4"), ("P", "b4"), ("P", "c7"), ("P", "d7"), ("P", "g7"), ("P", "h7"), ("P", "g2")]}
    for side, pieces in position.items():
        for kind, sq in pieces:
            i, j = "abcdefgh".index(sq[0]), int(sq[1]) - 1
            chess_piece(kind, at[0] - 3.5 * square + i * square, at[1] + 0.75, at[2] - 3.5 * square + j * square,
                        P["white"] if side == "white" else P["black"], s)
    chair([at[0], at[1], at[2] + board / 2 + 0.45], add.pi)
    chair([at[0], at[1], at[2] - board / 2 - 0.45], 0)
    add.text("WHITE TO PLAY AND WIN", [at[0], at[1] + 0.724, at[2] + board / 2 + 0.12], 0.06 * s, 0.006, P["gold"],
             align="center", u=[1, 0, 0], v=[0, 0, -1], k=6)


def sitting_man(at, facing=0.0, shirt=None):
    """A man sitting on a bench (his seat at ``at``), feet on the floor."""
    shirt = shirt or P["linen"]
    add.push()
    add.capsule([0, 0.5, 0], [0, 1.1, 0], 0.22, 12, shirt)                          # torso
    add.sphere([0, 1.35, 0], 0.17, 8, P["skin"])
    add.sphere([0, 1.45, 0], 0.15, 8, P["wood_dark"])                                 # hair
    for s in (-1, 1):
        add.capsule([s * 0.12, 0.45, 0.05], [s * 0.15, 0.45, 0.5], 0.1, 12, P["wood_dark"])    # thighs forward
        add.capsule([s * 0.15, 0.45, 0.5], [s * 0.15, 0.05, 0.55], 0.08, 12, P["wood_dark"])   # shins down
        add.cuboid([s * 0.15, 0.05, 0.62], [0.16, 0.1, 0.3], P["black"])                      # feet
        add.capsule([s * 0.25, 1.05, 0], [s * 0.3, 0.6, 0.35], 0.07, 12, shirt)               # arms to the table
        add.sphere([s * 0.3, 0.6, 0.4], 0.07, 6, P["skin"])
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def standing_man(at, facing=0.0, shirt=None, hat=False):
    shirt = shirt or P["linen"]
    add.push()
    for s in (-1, 1):
        add.capsule([s * 0.14, 0.1, 0], [s * 0.14, 0.9, 0], 0.1, 12, P["wood_dark"])
        add.cuboid([s * 0.14, 0.05, 0.06], [0.18, 0.1, 0.32], P["black"])
    add.capsule([0, 0.95, 0], [0, 1.6, 0], 0.23, 12, shirt)
    add.sphere([0, 1.85, 0], 0.17, 8, P["skin"])
    if hat:
        add.cylinder([0, 1.95, 0], [0, 2.05, 0], 0.16, 12, P["wood"])
        add.cylinder([0, 1.95, 0], [0, 1.97, 0], 0.28, 12, P["wood"])
    else:
        add.sphere([0, 1.95, 0], 0.15, 8, P["wood_dark"])
    for s in (-1, 1):
        add.capsule([s * 0.28, 1.5, 0], [s * 0.34, 0.85, 0.05], 0.07, 12, shirt)
        add.sphere([s * 0.35, 0.8, 0.06], 0.07, 6, P["skin"])
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


# --------------------------------------------------------------------------
#  6. Easter egg 1: the great hall -- throne, feast, chandeliers, fireplace
# --------------------------------------------------------------------------
HX0, HX1, HZ0, HZ1 = KX0 + WT, KX1 - WT, KZ0 + WT, KZ1 - WT     # inside the walls
HALL_MID = (HZ0 + HZ1) / 2
for x in (-9, 9):                                                  # columns
    for z in (-24, -18, -12, -6):
        add.column([x, KY + 0.04, z], HALL_H - 0.04, 0.45, P["white"], k_(14))
# the red carpet from the door to the dais, with gold edges (sunk into the floor squares)
add.cuboid([0, KY + 0.06, (HZ1 + HZ0 + 3.6) / 2], [3.0, 0.04, HZ1 - HZ0 - 3.6], P["red"])
for sx in (-1.4, 1.4):
    add.cuboid([sx, KY + 0.065, (HZ1 + HZ0 + 3.6) / 2], [0.2, 0.05, HZ1 - HZ0 - 3.6], P["gold"])
add.cuboid([0, KY + 0.33, HZ0 + 2.0], [10, 0.6, 4.0], P["stone_dark"])                     # the dais
add.cuboid([0, KY + 0.64, HZ0 + 2.0], [9.6, 0.04, 3.6], P["red"])
add.stairs([0, KY + 0.04, HZ0 + 4.0 + 1.0], 2, 6, 0.3, 0.5, P["stone_dark"], direction=(0, 0, -1))
THRONE = [0, KY + 0.64, HZ0 + 1.4]
add.push()
add.cuboid([0, 0.5, 0], [1.6, 0.25, 1.4], P["wood_dark"])
for sx in (-0.7, 0.7):
    for sz in (-0.6, 0.6):
        add.cuboid([sx, 0.2, sz], [0.15, 0.4, 0.15], P["gold"])
add.cuboid([0, 1.9, -0.6], [1.7, 2.8, 0.22], P["wood_dark"])
add.mesh(add.make(add.prism, [[-0.85, 0], [0.85, 0], [0, 0.7]], 0.22, P["gold"], (0, 3.3, -0.6), (0, 0, 1)))
for sx in (-0.85, 0.85):
    add.sphere([sx, 3.35, -0.6], 0.12, 8, P["gold"])
add.cuboid([0, 2.0, -0.47], [1.3, 2.0, 0.06], P["cushion"])
for sx in (-0.8, 0.8):
    add.cuboid([sx, 0.95, 0.05], [0.14, 0.6, 1.2], P["wood_dark"])
    add.cuboid([sx, 1.28, 0.05], [0.18, 0.08, 1.3], P["gold"])
    add.sphere([sx, 1.32, 0.65], 0.1, 8, P["gold"])
add.cuboid([0, 0.7, 0.1], [1.3, 0.16, 1.1], P["cushion"])
add.cuboid([0, 0.17, 1.05], [0.9, 0.34, 0.5], P["cushion"])                     # a footstool
add.cuboid([0, 0.35, 1.05], [0.94, 0.04, 0.54], P["gold"])
add.mesh(add.move(add.pop(), THRONE))


def crown(at, r=0.2):
    """A royal crown: a gold band set with rubies and pearls, four fleurs-
    de-lis, four pearl-studded arches over a red velvet cap, and an orb
    with a small cross on top -- rich, but not overdone."""
    add.push()
    add.pipe([0, 0, 0], [0, 0.12, 0], r, r - 0.025, k_(18), P["gold"])
    add.torus([0, 0.0, 0], r, 0.02, k_(18), 8, P["gold"])
    add.torus([0, 0.12, 0], r, 0.02, k_(18), 8, P["gold"])
    add.mesh(add.stretch(add.make(add.sphere, [0, 0.16, 0], r - 0.03, 8, P["red"]), [1.0, 1.1, 1.0], (0, 0.12, 0)))   # the velvet cap
    for i in range(8):                                                     # rubies and pearls round the band
        a = 2 * add.pi * i / 8
        add.sphere([r * add.cos(a), 0.06, r * add.sin(a)], 0.022, 4, P["red"] if i % 2 else P["white"])
    for i in range(4):                                                     # fleurs-de-lis, and the arches from them
        a = 2 * add.pi * i / 4 + add.pi / 4
        x, z = r * add.cos(a), r * add.sin(a)
        add.cone([x, 0.12, z], [x * 1.05, 0.28, z * 1.05], 0.035, 6, P["gold"])
        for s in (-1, 1):
            add.sphere([x - s * 0.04 * add.sin(a), 0.2, z + s * 0.04 * add.cos(a)], 0.018, 4, P["gold"])
        arc = [[x * add.cos(t * add.pi / 2), 0.16 + 0.24 * add.sin(t * add.pi / 2), z * add.cos(t * add.pi / 2)] for t in (0, 0.25, 0.5, 0.75, 1.0)]
        add.polyline(arc, 0.014, 8, P["gold"], smooth=1)
        for t in (0.2, 0.4, 0.6, 0.8):
            add.sphere([x * add.cos(t * add.pi / 2), 0.16 + 0.24 * add.sin(t * add.pi / 2) + 0.012, z * add.cos(t * add.pi / 2)], 0.012, 3, P["white"])
    add.sphere([0, 0.42, 0], 0.035, 6, P["gold"])                          # the orb and its cross
    add.cuboid([0, 0.49, 0], [0.01, 0.07, 0.01], P["gold"])
    add.cuboid([0, 0.5, 0], [0.05, 0.01, 0.01], P["gold"])
    add.mesh(add.move(add.pop(), at))


def king(at, facing=0.0):
    """The king sitting on his throne -- built in the throne's own frame,
    so that everything rests where it should: his seat on the cushion
    (top at 0.78), his forearms on the gold rails of the armrests (top at
    1.32, x = +-0.8), his feet on the footstool (top at 0.37, z 0.8..1.3),
    his back against the cushioned backrest.  A purple robe trimmed with
    ermine, red hose, black shoes with gold buckles, a gold chain with a
    ruby, a ring, a sceptre in the right hand and the crown on his head."""
    add.push()
    SEAT, RAIL, STOOL = 0.78, 1.32, 0.37
    # the lap and the thighs, flat on the cushion, knees just past its front edge
    add.cuboid([0, SEAT + 0.1, 0.25], [0.5, 0.2, 0.75], P["purple"])
    for s in (-1, 1):
        add.capsule([s * 0.14, SEAT + 0.1, -0.15], [s * 0.15, SEAT + 0.1, 0.62], 0.1, 14, P["purple"])
        add.sphere([s * 0.15, SEAT + 0.1, 0.7], 0.11, 8, P["purple"])                             # knee
        add.capsule([s * 0.15, SEAT + 0.02, 0.8], [s * 0.15, STOOL + 0.09, 0.86], 0.08, 14, P["red"])   # shin, in red hose
        add.cuboid([s * 0.15, STOOL + 0.06, 0.98], [0.16, 0.12, 0.34], P["black"])               # the shoe on the footstool
        add.cuboid([s * 0.15, STOOL + 0.1, 1.0], [0.12, 0.03, 0.06], P["gold"])                   # its buckle
    # the body, leaning on the backrest; the robe spreads over the seat behind
    add.capsule([0, SEAT + 0.2, -0.2], [0, SEAT + 0.85, -0.24], 0.27, 16, P["purple"])
    add.cuboid([0, SEAT + 0.08, -0.2], [0.8, 0.16, 0.5], P["purple"])
    add.torus([0, SEAT + 0.98, -0.24], 0.22, 0.06, 18, 8, P["white"])                              # ermine collar
    add.cuboid([0, SEAT + 0.5, 0.04], [0.16, 0.62, 0.04], P["white"])                              # ermine front
    for i in range(4):
        add.sphere([-0.05 + (i % 2) * 0.1, SEAT + 0.28 + i * 0.14, 0.065], 0.015, 3, P["black"])   # its spots
    add.polyline([[-0.24, SEAT + 0.9, -0.05], [0, SEAT + 0.66, 0.06], [0.24, SEAT + 0.9, -0.05]], 0.015, 8, P["gold"], smooth=1)
    add.sphere([0, SEAT + 0.64, 0.08], 0.03, 5, P["red"])                                         # the ruby on the chain
    # arms: upper arms down from the shoulders, forearms resting on the armrest rails
    for s in (-1, 1):
        add.capsule([s * 0.3, SEAT + 0.8, -0.2], [s * 0.72, RAIL + 0.08, -0.15], 0.075, 12, P["purple"])
        add.capsule([s * 0.8, RAIL + 0.075, -0.15], [s * 0.8, RAIL + 0.075, 0.45], 0.075, 12, P["purple"])
        add.torus([s * 0.8, RAIL + 0.075, 0.45], 0.075, 0.02, 12, 6, P["white"], axis=(0, 0, 1))   # ermine cuff
        add.sphere([s * 0.8, RAIL + 0.08, 0.58], 0.07, 8, P["skin"])                               # hand
    add.torus([-0.8, RAIL + 0.13, 0.6], 0.025, 0.008, 10, 5, P["gold"], axis=(0, 1, 0))            # a ring on the left hand
    add.cylinder([0.8, RAIL + 0.02, 0.58], [0.84, RAIL + 0.9, 0.5], 0.02, 10, P["gold"])            # the sceptre, held upright
    add.sphere([0.84, RAIL + 0.94, 0.5], 0.05, 8, P["red"])
    add.torus([0.84, RAIL + 0.94, 0.5], 0.06, 0.012, 14, 6, P["gold"], axis=(0, 0, 1))
    # the head, on a short neck, with a face, beard and moustache, and the crown
    add.cylinder([0, SEAT + 0.98, -0.22], [0, SEAT + 1.1, -0.22], 0.08, 10, P["skin"])
    add.sphere([0, SEAT + 1.26, -0.22], 0.18, 10, P["skin"])
    for s in (-1, 1):
        add.sphere([s * 0.065, SEAT + 1.3, -0.06], 0.02, 4, P["white"])
        add.sphere([s * 0.065, SEAT + 1.3, -0.045], 0.011, 3, P["black"])
        add.capsule([s * 0.02, SEAT + 1.21, -0.045], [s * 0.1, SEAT + 1.19, -0.08], 0.016, 6, P["white"])   # moustache
        add.mesh(add.stretch(add.make(add.sphere, [s * 0.075, SEAT + 1.34, -0.09], 0.03, 5, P["white"]), [1.6, 0.4, 0.8], (s * 0.075, SEAT + 1.34, -0.09)))   # eyebrow
    add.sphere([0, SEAT + 1.24, -0.045], 0.028, 5, P["skin"])                                     # nose
    add.mesh(add.stretch(add.make(add.sphere, [0, SEAT + 1.1, -0.1], 0.1, 8, P["white"]), [1.1, 1.6, 0.6], (0, SEAT + 1.12, -0.1)))   # beard
    crown([0, SEAT + 1.38, -0.22], 0.17)
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


king(THRONE)
# a canopy above the throne, the arms on the wall and the name of the castle
add.cuboid([0, KY + 5.0, HZ0 + 0.9], [3.6, 0.15, 1.8], P["red"])
for i in range(12):
    add.cuboid([-1.75 + i * 0.32, KY + 4.82, HZ0 + 1.8], [0.2, 0.25, 0.05], P["gold"])
add.mesh(add.move(arms(3.4, 4.6, 0.06), [-1.7, KY + 0.3, HZ0 + 0.25]))            # the arms on the wall behind the throne
add.text("ALGORITMŲ PILIS", [0, KY + 7.7, HZ0 + 0.34], 0.8, 0.07, P["gold"], align="center", k=8)
for s in (-1, 1):                                                                 # torch stands by the dais, guards
    add.cylinder([s * 4.2, KY + 0.64, HZ0 + 1.5], [s * 4.2, KY + 2.4, HZ0 + 1.5], 0.06, 8, P["iron"])
    add.cylinder([s * 4.2, KY + 2.4, HZ0 + 1.5], [s * 4.2, KY + 2.6, HZ0 + 1.5], 0.14, 8, P["iron"])
    add.sphere([s * 4.2, KY + 2.85, HZ0 + 1.5], 0.24, 8, FLAME)
    armour([s * 6.5, KY + 0.64, HZ0 + 1.6], 0, weapon="spear" if s < 0 else "sword", shield=(s > 0))
flush("hall: throne")

# the feast: two long tables with cloths and benches, laden with food, and
# the roast pig on its own clear stretch of the left table
TABLE_Z0, TABLE_Z1 = HZ0 + 7.0, HZ1 - 5.0
for tx in (-6.0, 6.0):
    L = TABLE_Z1 - TABLE_Z0
    zc = (TABLE_Z0 + TABLE_Z1) / 2
    add.cuboid([tx, KY + 0.98, zc], [2.0, 0.06, L], P["wood_dark"])
    plank_floor(tx - 1.0, tx + 1.0, TABLE_Z0, TABLE_Z1, KY + 1.05, thick=0.04, width=0.25, length=4.0)
    add.cuboid([tx, KY + 1.065, zc], [2.2, 0.03, L + 0.3], P["white"])
    for sx in (-1.1, 1.1):
        add.cuboid([tx + sx, KY + 0.83, zc], [0.03, 0.5, L + 0.3], P["white"])
    for z in (TABLE_Z0 + 0.6, zc, TABLE_Z1 - 0.6):
        for sx in (-0.8, 0.8):
            add.cuboid([tx + sx, KY + 0.5, z], [0.15, 0.96, 0.15], P["wood_dark"])
        add.cuboid([tx, KY + 0.25, z], [1.8, 0.1, 0.15], P["wood_dark"])
    for sx in (-1.7, 1.7):                                                       # benches
        add.cuboid([tx + sx, KY + 0.5, zc], [0.45, 0.08, L - 0.4], P["wood"])
        for z in (TABLE_Z0 + 0.5, TABLE_Z1 - 0.5):
            add.cuboid([tx + sx, KY + 0.25, z], [0.4, 0.5, 0.12], P["wood_dark"])
    top = KY + 1.08
    z = TABLE_Z0 + 0.8
    i = 0
    while z < TABLE_Z1 - 0.8:
        if tx < 0 and abs(z - zc) < 1.9:                                         # the pig's stretch
            z += 1.3
            i += 1
            continue
        kind = i % 6
        if kind == 0:
            chicken_roast([tx - 0.3, top, z])
            goblet([tx + 0.65, top, z - 0.3])
        elif kind == 1:
            bread([tx + 0.2, top, z], 2)
            jug([tx - 0.6, top, z + 0.2])
        elif kind == 2:
            cheese([tx - 0.5, top, z])
            goblet([tx + 0.5, top, z + 0.3])
            goblet([tx + 0.75, top, z - 0.4])
        elif kind == 3:
            bowl([tx - 0.1, top, z], 0.4, P["wood_light"], (P["apple"], P["orange"], P["apple"], P["cheese"]))
            grapes([tx + 0.7, top, z + 0.2])
        elif kind == 4:
            candelabra([tx, top, z])
            plate([tx - 0.65, top, z + 0.3])
            fruit([tx - 0.65, top + 0.03, z + 0.3], P["apple"])
            plate([tx + 0.65, top, z - 0.3])
            fruit([tx + 0.65, top + 0.03, z - 0.3], P["orange"], 0.14)
        else:
            plate([tx - 0.5, top, z], 0.35)
            add.mesh(add.move(add.stretch(add.make(add.sphere, [0, 0, 0], 0.2, 8, P["steel"]), [0.7, 0.5, 1.6], (0, 0, 0)), [tx - 0.5, top + 0.12, z]))
            jug([tx + 0.55, top, z], P["blue"])
        z += 1.3
        i += 1
    for j in range(6):                                                           # guests on the benches
        zz = TABLE_Z0 + 1.2 + j * 2.1
        if j % 2 == 0:
            sitting_man([tx - 1.7, KY + 0.54, zz], add.pi / 2, add.choice([P["blue"], P["leaf"], P["linen"]]))
        else:
            sitting_man([tx + 1.7, KY + 0.54, zz], -add.pi / 2, add.choice([P["red"], P["purple"], P["linen"]]))
roast_pig([-6.0, KY + 1.08, (TABLE_Z0 + TABLE_Z1) / 2])
flush("hall: the feast")

# chandeliers, the fireplace, tapestries, weapons on the wall, a chess study
for z in (HZ0 + 6, HALL_MID, HZ1 - 6):
    chandelier([0, KY + 5.5, z], 1.2, HALL_H - 5.5 - 0.6)
# the chimney breast on the west wall: a stone-faced block with the fire in
# a recess between two pilasters, under a mantelpiece
breast = add.make(add.cuboid, [HX0 + 0.5, KY + HALL_H / 2, HALL_MID], [1.0, HALL_H, 5.0], P["mortar"])
recess = add.make(add.cuboid, [HX0 + 0.85, KY + 1.4, HALL_MID], [1.0, 2.8, 3.0])          # open at the front, 0.65 deep
add.mesh(add.color(add.difference(breast, recess), P["mortar"]))
add.cuboid([HX0 + 0.43, KY + 1.4, HALL_MID], [0.15, 2.79, 2.99], P["black"])              # the sooty back of the recess
add.push()
stone_face(5.0, 0, HALL_H, 0, 0.12, "stone_dark", size=(0.7, 0.35), seed=3,
           skip=[(0.7, 4.3, 0, 2.85), (0.45, 4.55, 2.75, 3.25)])                           # the pilasters, the mantel
add.mesh(add.move(add.rotateY(add.pop(), add.pi / 2), [HX0 + 1.0, KY, HALL_MID + 2.5]))   # built along +x, turned to face +x
for sz in (-1.6, 1.6):                                                                    # the pilasters
    add.cuboid([HX0 + 1.0, KY + 1.4, HALL_MID + sz], [1.0, 2.8, 0.4], P["stone"])
add.cuboid([HX0 + 1.0, KY + 3.0, HALL_MID], [1.2, 0.4, 4.0], P["stone"])                   # the mantelpiece
for i in range(4):                                                                        # logs and flames in the recess
    add.cylinder([HX0 + 0.55, KY + 0.2 + 0.18 * i, HALL_MID - 1.0 + 0.3 * i], [HX0 + 0.95, KY + 0.35 + 0.2 * i, HALL_MID + 1.0 - 0.3 * i], 0.12, 10, P["trunk"])
for i in range(7):
    add.sphere([HX0 + 0.8 + 0.1 * add.sin(i * 2.0), KY + 0.6 + 0.25 * i, HALL_MID + 0.8 * add.sin(i * 1.7)], 0.4 - 0.04 * i, 8, FLAME)
add.sphere([HX0 + 0.8, KY + 0.7, HALL_MID], 0.3, 8, P["flame_core"])
candelabra([HX0 + 1.0, KY + 3.2, HALL_MID - 1.2])
goblet([HX0 + 1.0, KY + 3.2, HALL_MID + 1.2])
shield([HX0 + 1.12 + 0.04, KY + 5.2, HALL_MID], add.pi / 2, 0.6)                          # arms hung on the chimney breast
sword([HX0 + 1.12 + 0.07, KY + 3.5, HALL_MID - 0.9], (0, 1, 0.7), side=(0, 0.7, -1))         # a pair of swords hung flat below it
sword([HX0 + 1.12 + 0.07, KY + 3.5, HALL_MID + 0.9], (0, 1, -0.7), side=(0, 0.7, 1))
for z in (HZ0 + 3.5, HZ1 - 3.5):                                                          # tapestries, west and east walls
    for x, facing in ((HX0 + 0.26, add.pi / 2), (HX1 - 0.26, -add.pi / 2)):
        M = add.rotateY(add.move(arms(2.4, 3.6, 0.04), [-1.2, -1.8, 0]), facing)
        add.mesh(add.move(M, [x, KY + 4.5, z]))
        add.cylinder([x, KY + 6.4, z - 1.4], [x, KY + 6.4, z + 1.4], 0.05, 8, P["wood_dark"])
for x in (-16.5, 16.5):                                                                   # torches on the long walls
    torch([x, KY + 3.0, HZ0 + 0.24], 0)
    torch([x, KY + 3.0, HZ1 - 0.24], add.pi)
chess_study([HX1 - 5.5, KY + 0.04, HZ1 - 9.0])
for i in range(3):                                                                        # a few barrels of wine in the corner
    barrel([HX1 - 1.4 - (i % 2) * 1.1, KY + 0.04, HZ0 + 1.6 + (i // 2) * 1.0], 0.42, 1.1, upright=(i != 1))
flush("hall: fireplace and furnishings")


# --------------------------------------------------------------------------
#  7. Upstairs: the soldiers' dormitory, and the attic full of old things
# --------------------------------------------------------------------------
DX0, DX1, DZ0, DZ1 = HX0, HX1, HZ0, HZ1
add.seed(17)
beds = []
for i in range(8):                                                     # beds along the north wall, heads to the wall
    x = DX0 + 3.0 + i * 4.8
    if near_tower(x, DZ0 + 1.2, 1.5):
        continue
    beds.append((x, DZ0 + 1.5, 0.0))
for x in (-16.0, -6.0, 6.0, 16.0):                                     # ... and between the balcony doors on the south
    beds.append((x, DZ1 - 1.5, add.pi))
for j, (x, z, facing) in enumerate(beds):
    asleep = j % 3 != 1
    bed([x, FLOOR2, z], facing, sleeper=asleep)
    chest([x, FLOOR2, z + (1.9 if facing == 0 else -1.9)], 0, s=0.6)     # a chest at the foot of every bed
    if not asleep:
        armour([x + 1.2, FLOOR2, z + (0.5 if facing == 0 else -0.5)], facing + add.pi, weapon="none", shield=False, plume=False)  # armour on a stand
        add.cuboid([x + 1.2, FLOOR2 + 0.05, z + (0.5 if facing == 0 else -0.5)], [0.6, 0.1, 0.6], P["wood_dark"])
    for k in range(2):                                                 # boots by the bed
        add.cuboid([x - 0.7 + k * 0.28, FLOOR2 + 0.12, z + (0.4 if facing == 0 else -0.4)], [0.22, 0.24, 0.5], P["black"])
table([0, FLOOR2, HALL_MID], 6.0, 1.2, 0.8)                            # the long table in the middle
for sx in (-1.0, 1.0):
    add.cuboid([0, FLOOR2 + 0.45, HALL_MID + sx], [5.6, 0.08, 0.35], P["wood"])
    for dx in (-2.5, 2.5):
        add.cuboid([dx, FLOOR2 + 0.22, HALL_MID + sx], [0.3, 0.44, 0.3], P["wood_dark"])
candle([0, FLOOR2 + 0.8, HALL_MID], 0.4, 0.05)
jug([1.2, FLOOR2 + 0.8, HALL_MID - 0.3])
goblet([-0.9, FLOOR2 + 0.8, HALL_MID + 0.2])
bread([-2.0, FLOOR2 + 0.8, HALL_MID], 2)
sitting_man([-1.0, FLOOR2 + 0.5, HALL_MID - 1.0], 0, P["blue"])
sitting_man([1.4, FLOOR2 + 0.5, HALL_MID + 1.0], add.pi, P["leaf"])
for i in range(8):                                                     # spears on pegs along the east wall
    add.cylinder([DX1 - 0.45, FLOOR2 + 0.2, DZ0 + 4 + i * 0.6], [DX1 - 0.55, FLOOR2 + 3.4, DZ0 + 4 + i * 0.6], 0.035, 8, P["wood"])
    add.cone([DX1 - 0.55, FLOOR2 + 3.4, DZ0 + 4 + i * 0.6], [DX1 - 0.57, FLOOR2 + 3.85, DZ0 + 4 + i * 0.6], 0.07, 8, P["steel"])
add.cuboid([DX1 - 0.5, FLOOR2 + 2.6, DZ0 + 6.1], [0.1, 0.12, 5.0], P["wood_dark"])       # the peg rail
for i in range(4):
    shield([DX1 - 0.3, FLOOR2 + 2.2, DZ1 - 3 - i * 1.4], -add.pi / 2, 0.45)
# the chimney breast of the fireplace below passes through here, warm to sleep beside
brick_box([DX0 + 0.5, FLOOR2 + UPPER_H / 2, HALL_MID], [1.0, UPPER_H, 3.0])
add.cuboid([DX0 + 1.4, FLOOR2 + 0.45, HALL_MID + 2.5], [1.2, 0.9, 1.2], P["iron"])          # an iron stove
add.cylinder([DX0 + 1.4, FLOOR2 + 0.9, HALL_MID + 2.5], [DX0 + 1.4, FLOOR2 + 1.6, HALL_MID + 2.5], 0.12, 12, P["iron"])
add.cylinder([DX0 + 1.4, FLOOR2 + 1.6, HALL_MID + 2.5], [DX0 + 0.98, FLOOR2 + 1.6, HALL_MID + 2.5], 0.12, 12, P["iron"])
for x in (-16.5, 16.5):
    torch([x, FLOOR2 + 2.6, DZ0 + 0.24], 0)
    torch([x, FLOOR2 + 2.6, DZ1 - 0.24], add.pi)
# the wooden stair up to the attic hatch (the hatch is in the attic floor at HATCH)
STAIR_STEPS = 14
STAIR_FOOT = HOLE[2] + STAIR_STEPS * 0.5                              # the top step ends where the attic floor begins
add.stairs([HATCH[0], FLOOR2, STAIR_FOOT], STAIR_STEPS, 1.8, UPPER_H / STAIR_STEPS, 0.5, P["wood"], direction=(0, 0, -1))
for s in (-1, 1):                                                     # a handrail on posts
    rail = [[HATCH[0] + s * 0.95, FLOOR2 + 1.0 + UPPER_H * t, STAIR_FOOT - STAIR_STEPS * 0.5 * t] for t in (0.0, 0.5, 1.0)]
    add.polyline(rail, 0.04, 8, P["wood_dark"])
    for t in (0.0, 0.5, 1.0):
        add.cylinder([rail[int(t * 2)][0], FLOOR2 + UPPER_H * t, rail[int(t * 2)][2]], rail[int(t * 2)], 0.04, 8, P["wood_dark"])
flush("dormitory")

# the attic: rafters, and everything nobody uses any more
XC, ZC = (KX0 + KX1) / 2, (KZ0 + KZ1) / 2
for i in range(int((KX1 - KX0 - 2 * INSET) / 2.5) + 1):                 # rafters under the two long slopes
    x = KX0 + INSET + i * 2.5
    hz = (KZ1 - KZ0) / 2 - 0.2
    for sg in (-1, 1):                                                   # under the boards of the shell, not in them
        add.beam([x, EAVE + 0.15, ZC + sg * (hz - 0.9)], [x, EAVE + ROOF_H - 0.95, ZC], 0.18, 0.3, P["wood_dark"])
add.beam([KX0 + INSET, EAVE + ROOF_H - 1.0, ZC], [KX1 - INSET, EAVE + ROOF_H - 1.0, ZC], 0.25, 0.3, P["wood_dark"])   # the ridge beam
add.seed(23)
ATTIC_X = list(range(int(KX0 + 4), int(KX1 - 3), 4))
for k, x in enumerate(ATTIC_X):
    kind = k % 7
    zz = KZ0 + 6 + (k % 3) * 6
    if abs(x - HATCH[0]) < 2.5 and abs(zz - HATCH[1]) < 3:
        zz += 6
    if kind == 0:
        chest([x, EAVE, zz], 0.4, open_lid=True, s=0.9)
        sack([x + 1.5, EAVE, zz + 0.3], 0.35)
    elif kind == 1:
        barrel([x, EAVE, zz], 0.42, 1.1)
        barrel([x + 1.1, EAVE, zz + 0.3], 0.42, 1.1, upright=False)
    elif kind == 2:                                                   # a broken cart wheel and a chair on its side
        M = add.make(add.wheel, [0, 0, 0], 0.75, 0.12, P["wood_dark"], (0, 0, 1), k_(18), spokes=8, hub_color=P["iron"])
        add.mesh(add.move(add.rotateX(M, add.pi / 2 - 0.3), [x, EAVE + 0.25, zz]))
        M = add.make(chair, [0, 0, 0], 0.5)
        add.mesh(add.move(add.rotateZ(M, add.pi / 2), [x + 1.6, EAVE + 0.25, zz]))
    elif kind == 3:                                                   # a rolled carpet and a bundle of spears
        add.mesh(add.move(add.make(add.cylinder, [0, 0, -1.5], [0, 0, 1.5], 0.3, k_(12), P["red"]), [x, EAVE + 0.3, zz]))
        for i in range(5):
            add.mesh(add.move(add.rotateZ(add.make(spear, [0, 0, 0], 2.6), 0.15 * (i - 2)), [x + 1.4 + 0.1 * i, EAVE, zz + 0.1 * i]))
    elif kind == 4:                                                   # crates, a birdcage and a cracked shield
        crate([x, EAVE, zz], 0.8)
        crate([x, EAVE + 0.8, zz], 0.7)
        add.pipe([x + 1.3, EAVE, zz], [x + 1.3, EAVE + 0.05, zz], 0.3, 0.25, 16, P["iron"])
        for i in range(10):
            aa = 2 * add.pi * i / 10
            add.cylinder([x + 1.3 + 0.28 * add.cos(aa), EAVE + 0.05, zz + 0.28 * add.sin(aa)], [x + 1.3 + 0.2 * add.cos(aa), EAVE + 0.6, zz + 0.2 * add.sin(aa)], 0.01, 4, P["iron"])
        add.sphere([x + 1.3, EAVE + 0.62, zz], 0.05, 6, P["iron"])
        shield([x - 1.2, EAVE, zz + 0.3], 0.4, 0.45)
    elif kind == 5:                                                   # a dusty armour stand, a cradle
        armour([x, EAVE, zz], 0.3, weapon="none", shield=False, plume=False)
        add.cuboid([x, EAVE + 0.05, zz], [0.6, 0.1, 0.6], P["wood_dark"])
        add.cuboid([x + 1.8, EAVE + 0.35, zz], [0.9, 0.4, 0.5], P["wood"])
        for s in (-1, 1):
            add.mesh(add.move(add.make(add.cylinder, [0, 0, -0.3], [0, 0, 0.3], 0.35, 20, P["wood_dark"]), [x + 1.8 + s * 0.42, EAVE + 0.35, zz]))
    else:                                                             # a spinning wheel and old books
        add.mesh(add.move(add.make(add.wheel, [0, 0, 0], 0.55, 0.08, P["wood"], (0, 0, 1), k_(18), spokes=10, hub_color=P["wood_dark"]), [x, EAVE + 0.75, zz]))
        add.cuboid([x, EAVE + 0.2, zz], [1.4, 0.06, 0.5], P["wood"])
        for sx in (-0.55, 0.55):
            add.cuboid([x + sx, EAVE + 0.45, zz], [0.08, 0.5, 0.08], P["wood_dark"])
        for i in range(6):
            add.cuboid([x + 1.5, EAVE + 0.06 + i * 0.12, zz + 0.05 * (i % 2)], [0.5, 0.11, 0.7], add.choice([P["red"], P["blue"], P["wood_dark"], P["leaf_dark"]]))
for cx, cz in ((KX0 + 2.5, KZ0 + 2.5), (KX1 - 2.5, KZ1 - 2.5), (KX0 + 2.5, KZ1 - 2.5)):    # cobwebs in the corners
    if near_tower(cx, cz, 0.5):
        continue
    for i in range(6):
        aa = i * 0.4
        add.cylinder([cx, EAVE + 0.02, cz], [cx + 1.8 * add.cos(aa), EAVE + 1.6 * add.sin(aa) + 0.05, cz + 0.5 * add.sin(aa * 3)], 0.004, 3, P["white"])
add.sphere([HATCH[0] + 3, EAVE + 0.06, HATCH[1] + 0.5], 0.06, 6, P["stone_dark"])           # a mouse
add.cone([HATCH[0] + 3.06, EAVE + 0.06, HATCH[1] + 0.5], [HATCH[0] + 3.14, EAVE + 0.06, HATCH[1] + 0.5], 0.03, 5, P["stone_dark"])
add.cylinder([HATCH[0] + 2.95, EAVE + 0.04, HATCH[1] + 0.5], [HATCH[0] + 2.75, EAVE + 0.05, HATCH[1] + 0.6], 0.008, 4, P["stone_dark"])
flush("attic")


# --------------------------------------------------------------------------
#  8. Easter egg 2: the donjon inside -- the treasury with the dragon,
#     the armoury above it, the lord's chamber above that
# --------------------------------------------------------------------------
TR = [DON[0], G + 0.1, DON[1]]
add.seed(42)
HEAP = [TR[0] + 0.3, TR[1], TR[2] - 0.3]
HEAP_R = 2.6
add.mesh(add.move(add.stretch(add.make(add.hemisphere, [0, 0, 0], HEAP_R, 14, P["gold"]), [1.0, 0.45, 1.0], (0, 0, 0)), HEAP))


def heap_y(x, z):
    d2 = (x - HEAP[0]) ** 2 + (z - HEAP[2]) ** 2
    return HEAP[1] + (0.45 * add.sqrt(max(0.0, HEAP_R * HEAP_R - d2)) if d2 < HEAP_R * HEAP_R else 0.0)


for i in range(count(1500)):                                                       # coins
    a, rr = add.uniform(0, 2 * add.pi), add.uniform(0, 3.4)
    x, z = HEAP[0] + rr * add.cos(a), HEAP[2] + rr * add.sin(a)
    coin = add.make(add.cylinder, [0, 0, 0], [0, 0.025, 0], 0.09, 10, P["gold"])
    coin = add.rotateX(coin, add.uniform(-0.5, 0.5))
    add.mesh(add.move(add.rotateY(coin, a), [x, heap_y(x, z) + 0.02, z]))
for i in range(count(60)):                                                         # gems
    a, rr = add.uniform(0, 2 * add.pi), add.uniform(0, 2.4)
    x, z = HEAP[0] + rr * add.cos(a), HEAP[2] + rr * add.sin(a)
    add.sphere([x, heap_y(x, z) + 0.08, z], add.uniform(0.07, 0.14), 4, add.choice([P["red"], P["blue"], P["purple"], P["leaf"]]))
for i in range(4):
    a = 1.1 + i * 1.5
    x, z = HEAP[0] + 2.1 * add.cos(a), HEAP[2] + 2.1 * add.sin(a)
    goblet([x, heap_y(x, z), z])
SWORD_A = 4.5                                                                      # a sword stuck in the gold at the foot of
sx, sz = HEAP[0] + 2.1 * add.cos(SWORD_A), HEAP[2] + 2.1 * add.sin(SWORD_A)       # the heap, leaning out -- a good metre
sword([sx, heap_y(sx, sz) - 0.12, sz], (0.22 * add.cos(SWORD_A), 1, 0.22 * add.sin(SWORD_A)))   # clear of the dragon on top
chest([TR[0] - 2.8, TR[1], TR[2] + 2.4], 0.6, open_lid=True)                       # an open chest, gold spilling out
add.mesh(add.move(add.stretch(add.make(add.sphere, [0, 0, 0], 0.7, 8, P["gold"]), [1.0, 0.5, 0.7], (0, 0, 0)), [TR[0] - 2.8, TR[1] + 0.75, TR[2] + 2.4]))
for i in range(12):
    p = [TR[0] - 2.8 + add.uniform(-0.7, 0.7), TR[1] + 0.95 + add.uniform(0, 0.1), TR[2] + 2.4 + add.uniform(-0.4, 0.4)]
    add.cylinder(p, [p[0] + 0.01, p[1] + 0.025, p[2]], 0.08, 10, P["gold"])
add.torus([TR[0] + 3.3, TR[1] + 0.06, TR[2] + 2.6], 0.35, 0.06, k_(16), 8, P["gold"])      # a crown that rolled away
add.sphere([TR[0] - 3.4, TR[1] + 0.25, TR[2] - 2.4], 0.25, 8, P["bone"])                    # ... and the last thief
add.cuboid([TR[0] - 3.4, TR[1] + 0.08, TR[2] - 2.1], [0.3, 0.14, 0.25], P["bone"])
for i in range(4):
    add.cylinder([TR[0] - 3.0 + 0.25 * i, TR[1] + 0.05, TR[2] - 2.7], [TR[0] - 2.9 + 0.25 * i, TR[1] + 0.05, TR[2] - 1.7], 0.04, 6, P["bone"])
flush("treasury")


def dragon(at, facing=0.0, size=1.0):
    """A dragon curled up asleep on the heap: body, head with horns, closed
    eyes, folded wings, spines, tail -- lying on the gold, not floating."""
    add.push()

    def radius(t):
        return 0.55 * add.sin(add.pi * min(1.0, 0.3 + 0.9 * t)) ** 0.6 * (1 - 0.6 * t) + 0.05

    def spine(t):                                                          # a spiral lying on the heap of gold
        a = 1.5 * add.pi * t
        rr = 2.0 - 1.4 * t                                                 # stays well inside the stair's inner edge
        heap = 0.45 * add.sqrt(max(0.0, HEAP_R * HEAP_R - (size * rr) ** 2)) / size
        return [rr * add.cos(a), heap + 0.8 * radius(t), rr * add.sin(a)]

    pts = [spine(i / 40.0) for i in range(41)]
    body = add.make(add.polyline, pts, radius, k_(12), P["dragon"], smooth=0)

    def belly(p):                                                          # lighter underneath
        s = min(pts, key=lambda q: (q[0] - p[0]) ** 2 + (q[2] - p[2]) ** 2)
        return P["dragon_belly"] if p[1] < s[1] - 0.12 else P["dragon"]

    add.mesh(add.color_by(body, belly))
    fine = [spine(i / 200.0) for i in range(201)]                          # metres along the spine, to lay the wings
    arc = [0.0]                                                            # back along the curled body
    for i in range(200):
        arc.append(arc[-1] + vlen(vsub(fine[i + 1], fine[i])))

    def on_flank(side, u, d, w):
        """A point of a wing folded against the flank: ``u`` metres back from
        the shoulders along the spine, ``d`` metres down the side from the
        wing's top edge, ``w`` off the skin.  The wing follows the curled
        body round, so no part of it cuts through it."""
        s = arc[24] + u                                                    # the shoulders: t = 0.12
        i = min(199, max(0, [k for k in range(200) if arc[k] <= s][-1]))
        t = (i + (s - arc[i]) / max(1e-9, arc[i + 1] - arc[i])) / 200.0
        c, q0, q1 = spine(t), spine(max(0.0, t - 0.01)), spine(min(1.0, t + 0.01))
        hx, hz = q1[0] - q0[0], q1[2] - q0[2]
        L = add.sqrt(hx * hx + hz * hz) or 1.0
        r = radius(t) + 0.05
        phi = 1.05 - d / r                                                 # from high on the side downwards
        return [c[0] + side * hz / L * (r + w) * add.cos(phi), c[1] + (r + w) * add.sin(phi),
                c[2] - side * hx / L * (r + w) * add.cos(phi)]

    for side in (-1, 1):                                                   # the wings, folded along both flanks
        wing = add.make(add.parametric, lambda a, b, side=side: on_flank(side, 1.8 * a, b * (0.15 + 0.6 * add.sin(add.pi * a) ** 0.8)
                                                                         * (1 - 0.15 * abs(add.sin(3 * add.pi * a))), 0.0),
                        0, 1, 18, 0, 1, 4, P["dragon_wing"], thickness=0.03)          # darker, the edge in three scallops
        add.mesh(add.fix_normals(wing))                                    # a closed shell, turned outwards
        add.polyline([on_flank(side, 1.8 * j / 10.0, 0.0, 0.06) for j in range(11)], 0.05, 8, P["dragon_belly"])
    for i in range(0, 34, 2):                                               # spines along the back
        p = pts[i]
        r = radius(i / 40.0)
        add.cone([p[0], p[1] + r * 0.9, p[2]], [p[0], p[1] + r * 0.9 + 0.35 * (1 - i / 40.0) + 0.1, p[2]], 0.08, 6, P["dragon"])
    tail = pts[-1]
    add.mesh(add.move(add.make(add.prism, [[0, 0], [0.5, -0.3], [0.5, 0.3]], 0.06, P["dragon"], (0, 0, 0)), tail))
    head_at = [pts[0][0] + 0.8, pts[0][1] + 0.1, pts[0][2] - 0.2]            # the head lies on the front paws
    add.mesh(add.move(add.stretch(add.make(add.sphere, [0, 0, 0], 0.55, 12, P["dragon"]), [1.5, 0.75, 0.9], (0, 0, 0)), head_at))
    for s in (-1, 1):
        add.cone([head_at[0] - 0.3, head_at[1] + 0.25, head_at[2] + s * 0.25], [head_at[0] - 0.8, head_at[1] + 0.9, head_at[2] + s * 0.45], 0.08, 6, P["bone"])
        add.sphere([head_at[0] + 0.72, head_at[1] + 0.02, head_at[2] + s * 0.16], 0.05, 4, P["black"])   # nostrils
        add.cuboid([head_at[0] + 0.25, head_at[1] + 0.22, head_at[2] + s * 0.3], [0.3, 0.03, 0.08], P["black"])   # closed eyes
        for i in range(3):                                                   # smoke from the nostrils
            add.sphere([head_at[0] + 0.9 + 0.25 * i, head_at[1] + 0.1 + 0.2 * i, head_at[2] + s * (0.2 + 0.1 * i)], 0.08 + 0.05 * i, 6, SMOKE)
        paw = [head_at[0] - 0.2, heap_y(at[0] + head_at[0] - 0.2, at[2] + head_at[2] + s * 0.7) - at[1] + 0.15, head_at[2] + s * 0.7]
        add.capsule([paw[0] - 0.6, paw[1] + 0.1, paw[2]], paw, 0.16, 12, P["dragon"])
        for j in range(3):
            add.cone([paw[0] + 0.1, paw[1] - 0.03, paw[2] - 0.12 + j * 0.12], [paw[0] + 0.4, paw[1] - 0.1, paw[2] - 0.15 + j * 0.15], 0.04, 5, P["bone"])
    M = add.pop()
    M = add.stretch(M, [size, size, size], (0, 0, 0))
    add.mesh(add.move(add.rotateY(M, facing), at))


dragon([HEAP[0], HEAP[1], HEAP[2]], -1.2, 1.0)
for aa in (1.6, 2.5, 3.4, 4.0):                                             # torches on the wall, clear of the stair
    torch([TR[0] + (DON_IN - 0.05) * add.cos(aa), TR[1] + 2.6, TR[2] + (DON_IN - 0.05) * add.sin(aa)], -aa - add.pi / 2)
flush("dragon")

# the armoury on the first floor of the donjon
AY = F1
for aa in (4.1, 4.8):                                                       # racks of spears along the wall (the stair
    rack = add.make(add.cuboid, [0, 0.9, 0], [3.0, 0.12, 0.12], P["wood_dark"])   # takes the other half of the room's wall)
    rack.extend(add.make(add.cuboid, [0, 1.9, 0], [3.0, 0.12, 0.12], P["wood_dark"]))
    for j in range(6):
        rack.extend(add.make(spear, [-1.25 + j * 0.5, 0.0, 0.12], 2.6))
    add.mesh(add.move(add.rotateY(rack, add.pi / 2 - aa), [DON[0] + (DON_IN - 0.35) * add.cos(aa), AY, DON[1] + (DON_IN - 0.35) * add.sin(aa)]))
for aa in (5.3, 5.55, 5.8, 6.05, 6.3):
    shield([DON[0] + (DON_IN - 0.12) * add.cos(aa), AY + 3.2, DON[1] + (DON_IN - 0.12) * add.sin(aa)], -aa - add.pi / 2, 0.45)
for i, aa in enumerate((5.4, 5.75, 6.1)):
    x, z = DON[0] + (DON_IN - 0.6) * add.cos(aa), DON[1] + (DON_IN - 0.6) * add.sin(aa)
    armour([x, AY, z], -aa - add.pi / 2, weapon="none", shield=(i == 1), plume=False)
    add.cuboid([x, AY + 0.05, z], [0.6, 0.1, 0.6], P["wood_dark"])
table([DON[0], AY, DON[1]], 2.4, 1.2, 0.8)
for i in range(3):                                                          # helmets on the table
    add.sphere([DON[0] - 0.7 + i * 0.7, AY + 1.05, DON[1]], 0.25, 8, P["steel"])
    add.cuboid([DON[0] - 0.7 + i * 0.7, AY + 1.0, DON[1] + 0.24], [0.34, 0.05, 0.06], P["black"])
barrel([DON[0] + 2.0, AY, DON[1] + 2.0], 0.4, 0.9)
for i in range(12):                                                         # a barrel of arrows
    aa = add.uniform(0, 6.28)
    add.cylinder([DON[0] + 2.0 + 0.25 * add.cos(aa), AY + 0.5, DON[1] + 2.0 + 0.25 * add.sin(aa)],
                 [DON[0] + 2.0 + 0.3 * add.cos(aa), AY + 1.9, DON[1] + 2.0 + 0.3 * add.sin(aa)], 0.015, 5, P["wood"])
add.wheel([DON[0] - 2.2, AY + 0.6, DON[1] + 2.0], 0.5, 0.2, P["stone_dark"], (1, 0, 0), k_(16), hub_color=P["iron"])   # a grindstone
add.cuboid([DON[0] - 2.2, AY + 0.3, DON[1] + 2.0], [0.5, 0.6, 1.2], P["wood_dark"])
standing_man([DON[0] - 1.6, AY, DON[1] + 2.0], -add.pi / 2, P["blue"])
sword([DON[0] - 1.75, AY + 1.15, DON[1] + 2.0], (-1, 0.3, 0), 0.9)
for aa in (0.2, 4.45, 5.2):
    torch([DON[0] + (DON_IN - 0.05) * add.cos(aa), AY + 2.6, DON[1] + (DON_IN - 0.05) * add.sin(aa)], -aa - add.pi / 2)
flush("armoury")

# the lord's chamber on the second floor
LY = F2
add.cuboid([DON[0], LY + 0.03, DON[1]], [6.0, 0.05, 6.0], P["red"])                       # a carpet
bed([DON[0] - 2.2, LY, DON[1] + 0.5], add.pi / 2, sleeper=False, canopy=True)
table([DON[0] + 2.0, LY, DON[1] - 2.0], 1.6, 0.9, 0.8, P["wood_dark"])
chair([DON[0] + 2.0, LY, DON[1] - 1.2], add.pi, P["wood_dark"])
add.cuboid([DON[0] + 1.7, LY + 0.83, DON[1] - 2.1], [0.5, 0.06, 0.7], P["white"])           # an open book, a quill, a candle
add.cuboid([DON[0] + 1.7, LY + 0.86, DON[1] - 2.1], [0.03, 0.02, 0.7], P["wood_dark"])
add.cylinder([DON[0] + 2.4, LY + 0.83, DON[1] - 2.2], [DON[0] + 2.55, LY + 1.25, DON[1] - 2.4], 0.012, 5, P["white"])
candle([DON[0] + 2.5, LY + 0.83, DON[1] - 1.8], 0.3, 0.04)
chest([DON[0] + 2.2, LY, DON[1] + 2.4], -0.4, s=0.8)
add.cuboid([DON[0] - 2.0, LY + 1.1, DON[1] - 2.4], [1.4, 2.2, 0.7], P["wood_dark"])         # a wardrobe
add.cuboid([DON[0] - 2.0, LY + 1.1, DON[1] - 2.03], [0.04, 2.0, 0.04], P["gold"])
for i in range(2):
    add.sphere([DON[0] - 2.0 + (0.12 if i else -0.12), LY + 1.1, DON[1] - 2.02], 0.04, 4, P["gold"])
add.mesh(add.move(arms(2.4, 1.8, 0.05), [DON[0] - 1.2, LY + 0.7, DON[1] + DON_IN - 0.45]))   # a tapestry
add.cylinder([DON[0] - 1.3, LY + 2.55, DON[1] + DON_IN - 0.45], [DON[0] + 1.3, LY + 2.55, DON[1] + DON_IN - 0.45], 0.05, 8, P["wood_dark"])
standing_man([DON[0] + 0.5, LY, DON[1] + 1.0], 2.4, P["purple"], hat=True)                 # the lord himself, looking at the bed
for aa in (0.3, 1.0, 2.2):
    torch([DON[0] + (DON_IN - 0.05) * add.cos(aa), LY + 2.6, DON[1] + (DON_IN - 0.05) * add.sin(aa)], -aa - add.pi / 2)
flush("lord's chamber")


# --------------------------------------------------------------------------
#  9. Inside the chapel: the altar, the cross, pews, a lectern, candles
# --------------------------------------------------------------------------
CY = KY
add.cuboid([CH_C[0], CY + 0.03, CH_C[1]], [CH_X1 - CH_X0 - 2.6, 0.06, CH_Z1 - CH_Z0 - 2.6], P["white"])     # marble floor
for i in range(int((CH_X1 - CH_X0 - 2.6) / 1.5)):
    for j in range(int((CH_Z1 - CH_Z0 - 2.6) / 1.5)):
        if (i + j) % 2:
            add.cuboid([CH_X0 + 1.3 + 0.75 + i * 1.5, CY + 0.05, CH_Z0 + 1.3 + 0.75 + j * 1.5], [1.45, 0.05, 1.45], P["stone_dark"])
add.cuboid([CH_C[0], CY + 0.25, CH_Z0 + 2.2], [6.0, 0.4, 3.0], P["stone_dark"])                          # the altar step
add.cuboid([CH_C[0], CY + 0.95, CH_Z0 + 1.6], [2.4, 1.0, 1.0], P["white"])                                # the altar
add.cuboid([CH_C[0], CY + 1.47, CH_Z0 + 1.6], [2.6, 0.04, 1.2], P["white"])
add.cuboid([CH_C[0], CY + 1.2, CH_Z0 + 2.12], [2.4, 0.5, 0.03], P["red"])                                 # altar cloth
add.cuboid([CH_C[0], CY + 2.2, CH_Z0 + 1.6], [0.1, 1.4, 0.1], P["gold"])                                  # the cross
add.cuboid([CH_C[0], CY + 2.5, CH_Z0 + 1.6], [0.7, 0.1, 0.1], P["gold"])
for sx in (-0.9, 0.9):
    candle([CH_C[0] + sx, CY + 1.49, CH_Z0 + 1.6], 0.5, 0.05)
add.cuboid([CH_C[0], CY + 1.52, CH_Z0 + 1.9], [0.5, 0.06, 0.35], P["red"])                                # the book
add.cuboid([CH_C[0], CY + 3.0, CH_Z0 + 0.7], [1.6, 0.05, 0.05], P["gold"])                                # a hanging lamp
add.cylinder([CH_C[0], CY + 3.0, CH_Z0 + 0.7], [CH_C[0], CY + 8.5, CH_Z0 + 0.7], 0.02, 6, P["iron"])
add.sphere([CH_C[0], CY + 2.85, CH_Z0 + 0.7], 0.2, 8, P["red"])
add.sphere([CH_C[0], CY + 2.85, CH_Z0 + 0.7], 0.12, 6, FLAME)
for j in range(4):                                                                                        # pews, facing the altar
    for sx in (-2.3, 2.3):
        z = CH_Z0 + 5.0 + j * 1.6
        add.cuboid([CH_C[0] + sx, CY + 0.5, z], [3.0, 0.08, 0.45], P["wood"])
        add.cuboid([CH_C[0] + sx, CY + 0.85, z + 0.25], [3.0, 0.55, 0.06], P["wood"])                     # backrest behind
        for dx in (-1.4, 1.4):
            add.cuboid([CH_C[0] + sx + dx, CY + 0.25, z], [0.08, 0.5, 0.45], P["wood_dark"])
        add.cuboid([CH_C[0] + sx, CY + 0.12, z - 0.5], [3.0, 0.06, 0.3], P["wood_dark"])                  # the kneeler in front
for sx, shirt in ((-2.3, P["blue"]), (-1.5, P["linen"]), (2.6, P["purple"])):                          # people at prayer, facing the altar
    sitting_man([CH_C[0] + sx, CY + 0.54, CH_Z0 + 5.0 + 1.6 * (1 if sx < 0 else 2) - 0.05], add.pi, shirt)
add.cylinder([CH_C[0] - 3.5, CY, CH_Z0 + 3.6], [CH_C[0] - 3.5, CY + 1.1, CH_Z0 + 3.6], 0.08, 12, P["wood_dark"])   # the lectern
add.mesh(add.rotateX(add.make(add.cuboid, [CH_C[0] - 3.5, CY + 1.25, CH_Z0 + 3.6], [0.6, 0.05, 0.5], P["wood_dark"]), -0.5, (CH_C[0] - 3.5, CY + 1.25, CH_Z0 + 3.6)))
add.mesh(add.rotateX(add.make(add.cuboid, [CH_C[0] - 3.5, CY + 1.3, CH_Z0 + 3.6], [0.45, 0.05, 0.4], P["white"]), -0.5, (CH_C[0] - 3.5, CY + 1.25, CH_Z0 + 3.6)))
lathe([[0.0, 0], [0.3, 0], [0.12, 0.1], [0.12, 0.8], [0.45, 0.95], [0.45, 1.05], [0.35, 1.05], [0.3, 0.95], [0.0, 0.95]],
      [CH_C[0] + 3.5, CY, CH_Z1 - 2.5], k_(12), P["white"])                                              # the font
add.cylinder([CH_C[0] + 3.5, CY + 0.96, CH_Z1 - 2.5], [CH_C[0] + 3.5, CY + 1.0, CH_Z1 - 2.5], 0.3, 16, WATER)
for i in range(2):                                                                                        # candle stands by the door
    x = CH_C[0] + (-1.6 if i == 0 else 1.6)
    add.cylinder([x, CY, CH_Z1 - 1.6], [x, CY + 1.3, CH_Z1 - 1.6], 0.04, 8, P["iron"])
    add.cylinder([x, CY, CH_Z1 - 1.6], [x, CY + 0.05, CH_Z1 - 1.6], 0.2, 12, P["iron"])
    candle([x, CY + 1.3, CH_Z1 - 1.6], 0.3, 0.04)
flush("chapel inside")


# --------------------------------------------------------------------------
#  10. The courtyard: cobblestones, the well, the fountain, the smithy, a
#      market, a stable, a trebuchet, cannons, carts, barrels, animals
# --------------------------------------------------------------------------
YARD_R = 47.0
Y = G + 0.05                                           # everything in the yard stands on the earth


def in_yard(x, z, margin=1.5, road=True):
    """Is (x, z) inside the walls, clear of the wall, the towers and the
    buildings (and, with ``road``, of the road from the gate)?"""
    if octagon_r(x, z) > 48.8 - margin:
        return False
    if any((x - c[0]) ** 2 + (z - c[2]) ** 2 < (TOWER_R + margin) ** 2 for c in CORNERS):
        return False
    if KX0 - 1 - margin < x < CH_X1 + 1 + margin and KZ0 - 1 - margin < z < KZ1 + 1 + margin:
        return False
    if near_tower(x, z, margin):
        return False
    if road and abs(x) < 3.5 + margin and z > KZ1 + 3:     # the road from the gate
        return False
    return True


# the ground of the yard is packed earth in mottled shades; a cobbled square
# in front of the palace and the cobbled road from the gate; paths of split
# flagstones to the well, the market, the cottage and the smithy, the
# chapel, the stable
PLAZA = (-25.0, 36.5, KZ1 + PL + 0.2, 12.0)             # x0, x1, z0, z1 of the cobbled square
ROAD_X = 2.5
FOOTPRINTS = [(10, 10, 2.75), (12, 24, 1.7), (2.8, 1.2, 0.6), (-2.8, 1.2, 0.6), (-12, 30, 2.6), (-34, 6, 4.0), (-33, 22, 4.5), (10, -40, 5.2),
              (28, 18, 5.0), (30, 31, 2.4), (33.5, 23, 2.6), (32, 6, 5.0), (-32, -8, 4.0), (-6, -40, 1.2),
              (-22, 14, 3.2), (-30, 35, 2.0), (-23, 38, 2.8), (17, 42, 2.8), (8, 41, 2.6), (-8, 41, 2.6),
              (-19, 20, 1.2), (14, 27, 0.6), (-10, 22, 0.6), (20, 36, 0.6), (9, 20, 0.9), (-20, 26, 0.9),
              (-40, 14, 0.4), (-38, 22, 0.4), (-5, 39, 0.5), (14, -38, 1.6)]         # things standing in the yard


def on_footprint(x, z):
    if abs(x) < 3.7 and -1.4 < z < 1.4:                # the steps up to the palace door
        return True
    return any((x - fx) ** 2 + (z - fz) ** 2 < r * r for fx, fz, r in FOOTPRINTS)


def on_plaza(x, z):
    return (PLAZA[0] < x < PLAZA[1] and PLAZA[2] < z < PLAZA[3]) or (abs(x) < ROAD_X and PLAZA[3] - 0.1 <= z < GATE_Z0 + 0.5)


PATHS = [[(ROAD_X, 30), (10.5, 25.5), (12.5, 20.5), (12, 12.5)],                       # to the well
         [(-ROAD_X, 35), (-11, 33.5), (-20, 30), (-29, 25.5), (-31.5, 12), (-31, 9.5)],   # market, cottage, smithy
         [(36, 6), (39.5, -8), (39.5, -28), (30, -37), (19, -38.5)],                  # round the chapel to the stable
         [(-25, 4), (-30.5, -4), (-36, -16), (-31, -34), (-22, -41.5), (-7, -43), (1, -40)],   # west side to the dovecote and stable
         [(28, -6.2), (28, -1.5)],                                                     # the chapel door
         [(ROAD_X, 40), (7, 41.5)], [(-ROAD_X, 40), (-7, 41.5)]]                       # the cannons


def on_path(x, z, margin=0.0):
    for pts in PATHS:
        for a, b in zip(pts, pts[1:]):
            dx, dz = b[0] - a[0], b[1] - a[1]
            L2 = dx * dx + dz * dz
            t = max(0.0, min(1.0, ((x - a[0]) * dx + (z - a[1]) * dz) / L2))
            if (x - a[0] - t * dx) ** 2 + (z - a[1] - t * dz) ** 2 < (1.2 + margin) ** 2:
                return True
    return False


def paved(x, z):
    return on_plaza(x, z) or on_path(x, z)


def value_noise(x, z, cell, s=0):
    """Smooth repeatable noise in 0..1: hash values on a lattice of
    ``cell`` metres, blended between the lattice points."""
    gx, gz = x / cell, z / cell
    ix, iz = int(gx // 1), int(gz // 1)
    fx, fz = gx - ix, gz - iz
    fx, fz = fx * fx * (3 - 2 * fx), fz * fz * (3 - 2 * fz)
    a, b, c, d = hash2(ix, iz, s), hash2(ix + 1, iz, s), hash2(ix, iz + 1, s), hash2(ix + 1, iz + 1, s)
    return (a * (1 - fx) + b * fx) * (1 - fz) + (c * (1 - fx) + d * fx) * fz


def earth_shade(x, z):
    """Which earth lies at (x, z): blotches of lighter and darker ground
    from two scales of noise, dry and trodden pale beside the paths,
    damp and dark under the curtain wall."""
    v = 0.6 * value_noise(x, z, 7.0, 43) + 0.4 * value_noise(x, z, 2.5, 44)
    v += 0.35 * max(0.0, min(1.0, (octagon_r(x, z) - 42) / 7))
    if on_path(x, z, 1.0):
        v -= 0.18
    return P["earth_light"] if v < 0.38 else P["earth_dark"] if v > 0.68 else P["earth"]


EARTH_EDGE = octagon_outline(49.1)                     # the earth runs 0.3 under the curtain wall's inner face


def earth_yard(spacing=1.5, sectors=96, r_of=EARTH_EDGE):
    """The packed earth of the yard: a closed slab filling the octagon of
    the walls, whose top is a polar grid of cells with jittered corners,
    each in one of three shades."""
    n_rings = int(round(YARD_R / spacing))
    top, base = G + 0.02, G - 0.3
    rings = [[[0.0, top, 0.0]]]
    for i in range(1, n_rings + 1):
        ring = []
        for j in range(sectors):
            a = 2 * add.pi * j / sectors
            if i < n_rings:                                                        # the rim keeps the octagon's shape
                a += (hash2(i, j, 42) - 0.5) * 0.6 * 2 * add.pi / sectors
            r = r_of(a) * i / n_rings
            if i < n_rings:
                r += (hash2(i, j, 41) - 0.5) * 0.6 * spacing
            ring.append([r * add.cos(a), top, r * add.sin(a)])
        rings.append(ring)
    for j in range(sectors):                                                       # the top ...
        a, b = rings[1][j], rings[1][(j + 1) % sectors]
        add.triangle(rings[0][0], b, a, earth_shade((a[0] + b[0]) / 3, (a[2] + b[2]) / 3))
    for i in range(2, n_rings + 1):
        for j in range(sectors):
            a, b = rings[i - 1][j], rings[i - 1][(j + 1) % sectors]
            c, d = rings[i][(j + 1) % sectors], rings[i][j]
            add.quad(a, b, c, d, earth_shade((a[0] + b[0] + c[0] + d[0]) / 4, (a[2] + b[2] + c[2] + d[2]) / 4))
    rim = rings[-1]
    for j in range(sectors):                                                       # ... the side and the bottom
        a, b = rim[j], rim[(j + 1) % sectors]
        add.quad(a, b, [b[0], base, b[2]], [a[0], base, a[2]], P["earth_dark"])
        add.triangle([0.0, base, 0.0], [a[0], base, a[2]], [b[0], base, b[2]], P["earth_dark"])


earth_yard()
flush("the earth of the yard")


def yard_pebbles(step=1.6):
    """Small stones lying about on the earth (a repeatable lattice with
    jitter, so the random stream of the rest of the yard is unchanged)."""
    n = 0
    cells = int(53 / step) + 1
    for gi in range(-cells, cells + 1):
        for gj in range(-cells, cells + 1):
            if hash2(gi, gj, 45) > 0.3 * max(DENSITY, 0.2):
                continue
            x = gi * step + (hash2(gi, gj, 46) - 0.5) * 1.4
            z = gj * step + (hash2(gi, gj, 47) - 0.5) * 1.4
            if not in_yard(x, z, 0.5) or paved(x, z) or on_footprint(x, z):
                continue
            rr = 0.08 + 0.14 * hash2(gi, gj, 48)
            stone = add.color(add.stretch(PEBBLE, [rr * (0.8 + 0.5 * hash2(gi, gj, 49)), rr * 0.6, rr], (0, 0, 0)),
                              (P["rock"], P["stone_dark"], P["sand"])[int(hash2(gi, gj, 50) * 3) % 3])
            add.mesh(add.move(add.rotateY(stone, 2 * add.pi * hash2(gi, gj, 51)), [x, G + 0.04, z]))
            n += 1
    return n


n = cobble_area(lambda x, z: on_plaza(x, z) and in_yard(x, z, -0.2, road=False) and not on_footprint(x, z) and (abs(x) < ROAD_X or z < PLAZA[3])
                and hash2(int(x * 9), int(z * 9), 78) < max(DENSITY, 0.35),
                PLAZA[0], PLAZA[1], PLAZA[2], GATE_Z0 + 0.5, G + 0.02, step=0.44, scale=0.7, seed=9)
flush("cobbles: the square and the road (%d)" % n, clean=False)
n = 0
for pts in PATHS:
    n += flag_path(pts, avoid=lambda x, z: on_footprint(x, z) or not in_yard(x, z, -0.5))
flush("flagstone paths (%d stones)" % n)               # cleaned: where two paths meet, their stones overlap
add.seed(19)
n = 0
tries = 0
while n < count(60000) and tries < 600000:                                            # grass on the earth of the yard
    tries += 1
    a = add.uniform(0, 2 * add.pi)
    r = EARTH_EDGE(a) * add.sqrt(add.random())
    x, z = r * add.cos(a), r * add.sin(a)
    if not in_yard(x, z, 0.3) or paved(x, z) or on_footprint(x, z):
        continue
    for j in range(3):
        b = a + j * 2.1 + hash2(n, j)
        h = 0.2 + 0.25 * hash2(n, j, 2)
        sheet([[x - 0.05 * add.cos(b), G + 0.02, z - 0.05 * add.sin(b)], [x + 0.05 * add.cos(b), G + 0.02, z + 0.05 * add.sin(b)],
               [x + 0.1 * add.sin(b), G + 0.02 + h, z - 0.1 * add.cos(b)]], P["grass"] if hash2(n, j, 3) > 0.5 else P["grass_dry"], 0.01, hinge=True)
    n += 1
flush("grass in the yard (%d tufts)" % n, clean=False)
flush("stones lying in the yard (%d)" % yard_pebbles(), clean=False)


def well(at):
    """A well with a windlass, a rope and a bucket, under a little roof."""
    add.push()
    add.pipe([0, 0, 0], [0, 1.0, 0], 1.2, 0.9, k_(16), P["mortar"])
    for j in range(2):                                                                             # two courses of blocks
        n_b = k_(10)
        for i in range(n_b):
            a = 2 * add.pi * (i + 0.5 * j) / n_b
            add.mesh(add.move(add.rotateY(add.make(add.cuboid, [0, 0, 0], [2 * add.pi * 1.2 / n_b - 0.05, 0.45, 0.14], pick("stone", i, j)), add.pi / 2 - a),
                              [1.22 * add.cos(a), 0.25 + j * 0.5, 1.22 * add.sin(a)]))
    for i in range(k_(12)):
        a = 2 * add.pi * i / k_(12)
        add.mesh(add.move(add.rotateY(add.make(add.cuboid, [0, 0, 0], [0.45, 0.14, 0.42], pick("stone", i, 4)), add.pi / 2 - a),
                          [1.05 * add.cos(a), 1.06, 1.05 * add.sin(a)]))
    add.cylinder([0, 0.02, 0], [0, 0.05, 0], 0.9, k_(16), WATER)
    for sx in (-1.4, 1.4):
        add.cuboid([sx, 1.4, 0], [0.2, 2.8, 0.2], P["wood_dark"])
    add.cylinder([-1.4, 2.2, 0], [1.4, 2.2, 0], 0.16, k_(10), P["wood"])                         # the windlass
    add.helix([0, 2.2, 0], 0.17, 0.05, 6, 40, 0.02, 6, P["rope"], axis=(1, 0, 0))
    add.polyline([[1.55, 2.2, 0], [1.75, 2.2, 0], [1.75, 2.6, 0], [1.95, 2.6, 0]], 0.04, 8, P["iron"])   # the crank
    add.cylinder([0, 2.2, 0], [0, 1.4, 0], 0.015, 6, P["rope"])
    lathe([[0.16, 0], [0.18, 0], [0.22, 0.3], [0.2, 0.3], [0.16, 0.02]], [0, 1.1, 0], k_(10), P["wood_dark"])
    add.arch([-0.2, 1.4, 0], [0.2, 1.4, 0], 0.25, 0.015, P["iron"], 8, 6)
    add.roof([0, 2.8, 0], [3.6, 2.2], 1.0, P["slate"], 0.2)
    add.mesh(add.move(add.pop(), at))


def fountain(at):
    add.push()
    add.pipe([0, 0, 0], [0, 0.7, 0], 2.6, 2.3, k_(24), P["white"])
    add.torus([0, 0.7, 0], 2.45, 0.08, k_(24), 10, P["white"])
    add.cylinder([0, 0.05, 0], [0, 0.55, 0], 2.3, k_(24), WATER)
    add.column([0, 0, 0], 1.8, 0.25, P["white"], k_(12))
    lathe([[0.0, 0], [0.3, 0], [0.9, 0.25], [1.0, 0.4], [0.9, 0.4], [0.8, 0.28], [0.25, 0.1], [0.0, 0.1]], [0, 1.9, 0], k_(16), P["white"])
    add.cylinder([0, 2.1, 0], [0, 2.4, 0], 0.9, k_(16), WATER)
    add.cylinder([0, 1.9, 0], [0, 3.2, 0], 0.06, 8, WATER)
    for i in range(8):
        a = 2 * add.pi * i / 8
        arc = [[add.cos(a) * (0.1 * j + 1.4 * (j / 6.0) ** 0.5), 3.2 - 2.7 * (j / 6.0) ** 2, add.sin(a) * (0.1 * j + 1.4 * (j / 6.0) ** 0.5)]
               for j in range(7)]
        add.polyline(arc, 0.04, 6, WATER)
    add.mesh(add.move(add.pop(), at))


def cart(at, facing=0.0, load="barrels"):
    add.push()
    add.cuboid([0, 0.88, 0], [3.2, 0.08, 1.8], P["wood_dark"])
    plank_floor(-1.6, 1.6, -0.9, 0.9, 0.96, thick=0.04, width=0.3, length=3.2, along="x")
    for sz in (-0.9, 0.9):
        for i in range(3):
            add.cuboid([0, 1.1 + i * 0.28, sz], [3.2, 0.2, 0.06], pick("wood", i, 6))
        for sx in (-1.5, 0, 1.5):
            add.cuboid([sx, 1.25, sz], [0.08, 0.8, 0.08], P["wood_dark"])
    for sx in (-1.5, 1.5):
        for i in range(3):
            add.cuboid([sx, 1.1 + i * 0.28, 0], [0.06, 0.2, 1.8], pick("wood", i, 7))
    add.cylinder([0, 0.75, -1.05], [0, 0.75, 1.05], 0.08, 8, P["iron"])
    for sz in (-1.0, 1.0):
        add.wheel([0, 0.75, sz], 0.75, 0.12, P["wood_dark"], (0, 0, 1), k_(18), spokes=8, hub_color=P["iron"])
    for sz in (-0.5, 0.5):
        add.cylinder([1.6, 0.85, sz], [3.8, 0.6, sz], 0.06, 8, P["wood_dark"])                  # the shafts
    add.cuboid([3.7, 0.3, 0.5], [0.08, 0.6, 0.08], P["wood_dark"])                              # a prop under one shaft
    if load == "barrels":
        barrel([-0.9, 0.96, 0.0], 0.42, 1.0, upright=False)
        barrel([0.0, 0.96, 0.0], 0.42, 1.0, upright=False)
        sack([0.9, 0.96, 0.3], 0.35)
        sack([0.9, 0.96, -0.4], 0.32)
    else:
        for i in range(18):                                                   # hay
            add.sphere([add.uniform(-1.3, 1.3), 1.2 + add.uniform(0, 0.5), add.uniform(-0.6, 0.6)], add.uniform(0.35, 0.55), 6, P["straw"])
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def plank_stack(at, n=4, facing=0.0):
    add.push()
    for j in range(n):
        for i in range(5):
            if j % 2 == 0:
                add.cuboid([0, 0.08 + j * 0.16, -0.7 + i * 0.35], [3.0, 0.15, 0.3], pick("wood_light", i, j))
            else:
                add.cuboid([-1.2 + i * 0.6, 0.08 + j * 0.16, 0], [0.3, 0.15, 1.7], pick("wood_light", i, j))
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def brick_stack(at, nx=6, ny=5, nz=3):
    for j in range(ny):
        for i in range(nx):
            for k in range(nz):
                if j == ny - 1 and hash2(i, k, j) < 0.4:
                    continue
                add.cuboid([at[0] + (i + 0.5) * 0.62 + (0.31 if j % 2 else 0), at[1] + (j + 0.5) * 0.31, at[2] + (k + 0.5) * 0.32],
                           [0.6, 0.29, 0.3], pick("brick", i + 7 * j, k))


def weapon_rack(at, facing=0.0):
    add.push()
    for sx in (-1.4, 1.4):
        add.cuboid([sx, 0.9, 0], [0.15, 1.8, 0.15], P["wood_dark"])
    add.cuboid([0, 1.7, 0], [3.0, 0.12, 0.12], P["wood_dark"])
    add.cuboid([0, 0.5, 0], [3.0, 0.12, 0.12], P["wood_dark"])
    for i in range(5):
        spear([-1.1 + i * 0.55, 0.0, 0.12], 2.6)
    for i in range(3):
        sword([-0.9 + i * 0.9, 0.6, -0.14], (0, 1, 0), 0.9)
    axe([0.6, 0.0, -0.3], 1.3)
    axe([-0.4, 0.0, -0.3], 1.1)
    shield([-1.9, 0.0, -0.1], 0.3, 0.45)
    shield([1.9, 0.0, -0.1], -0.3, 0.45)
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def dummy(at):
    """A training dummy: a post, a straw body and an old shield."""
    add.cylinder(at, [at[0], at[1] + 2.2, at[2]], 0.08, 8, P["wood_dark"])
    add.sphere([at[0], at[1] + 1.5, at[2]], 0.4, 8, P["straw"])
    add.sphere([at[0], at[1] + 2.1, at[2]], 0.22, 8, P["straw"])
    add.cylinder([at[0] - 0.7, at[1] + 1.6, at[2]], [at[0] + 0.7, at[1] + 1.6, at[2]], 0.05, 8, P["wood_dark"])
    shield([at[0] - 0.7, at[1] + 1.15, at[2] + 0.1], 0, 0.35)


def trebuchet(at, facing=0.0):
    add.push()
    for sz in (-1.2, 1.2):                                                    # two A-frames
        add.beam([-1.6, 0, sz], [0, 4.5, sz], 0.25, 0.25, P["wood_dark"])
        add.beam([1.6, 0, sz], [0, 4.5, sz], 0.25, 0.25, P["wood_dark"])
        add.beam([-1.8, 0.15, sz], [1.8, 0.15, sz], 0.3, 0.3, P["wood_dark"])
        add.beam([-0.9, 2.2, sz], [0.9, 2.2, sz], 0.18, 0.18, P["wood"])
    add.beam([0, 0.15, -1.4], [0, 0.15, 1.4], 0.3, 0.3, P["wood_dark"])
    add.cylinder([0, 4.5, -1.5], [0, 4.5, 1.5], 0.12, k_(8), P["iron"])         # the axle
    arm = add.make(add.beam, [-2.4, 0, 0], [5.5, 0, 0], 0.25, 0.3, P["wood"])
    arm.extend(add.make(add.cuboid, [-2.4, -0.9, 0], [1.2, 1.2, 1.2], P["iron"]))   # the counterweight
    arm.extend(add.make(add.cylinder, [5.4, 0, 0], [5.6, 0, 0], 0.08, 8, P["iron"]))
    sling = add.make(add.polyline, [[5.5, 0, 0], [6.5, -2.2, 0], [7.5, -2.9, 0]], 0.02, 6, P["rope"])
    sling.extend(add.make(add.sphere, [7.5, -2.9, 0], 0.4, 8, P["rock"]))
    arm.extend(sling)
    add.mesh(add.move(add.rotateZ(arm, 0.55), [0, 4.5, 0]))
    for sx in (-1.6, 1.6):
        for sz in (-1.5, 1.5):
            add.wheel([sx, 0.45, sz], 0.45, 0.2, P["wood_dark"], (0, 0, 1), k_(14), spokes=6, hub_color=P["iron"])
    for i, (dx, dz) in enumerate(((3.2, 1.2), (3.9, 1.5), (3.5, 2.0), (3.55, 1.55))):                # a pile of stone balls
        add.sphere([dx, 0.4 + (0.62 if i == 3 else 0), dz], 0.4, 8, P["rock"])
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def cannon(at, facing=0.0):
    """An iron cannon on a wheeled carriage: the barrel is a real tube at
    the muzzle -- a round bore you can look into -- with reinforcing rings
    and a cascabel at the breech; the pyramid of cannon balls stands beside
    the carriage, clear of the wheels."""
    add.push()
    IRON, RING = P["iron"], P["steel"]
    for sz in (-0.35, 0.35):                                                  # the carriage cheeks
        add.mesh(add.make(add.prism, [[-1.2, 0.3], [1.0, 0.3], [0.6, 1.1], [-0.9, 0.9]], 0.16, P["wood_dark"], (0, 0, sz), (0, 0, 1)))
    add.cuboid([-0.1, 0.4, 0], [1.6, 0.2, 0.55], P["wood_dark"])                # the transom between them
    add.cylinder([-0.6, 0.6, -0.6], [-0.6, 0.6, 0.6], 0.06, 10, IRON)           # the axle
    for sz in (-0.5, 0.5):
        add.wheel([-0.6, 0.6, sz], 0.6, 0.15, P["wood_dark"], (0, 0, 1), k_(18), spokes=8, hub_color=IRON)
    y = 1.05
    add.frustum([-1.0, y, 0], [1.4, y + 0.08, 0], 0.32, 0.23, k_(18), IRON)      # the barrel, closed at the breech ...
    add.pipe([1.4, y + 0.08, 0], [1.95, y + 0.1, 0], 0.23, 0.15, k_(18), IRON)   # ... and a tube at the muzzle
    add.cylinder([1.4, y + 0.08, 0], [1.45, y + 0.081, 0], 0.15, k_(18), P["black"])   # the dark bottom of the bore
    add.sphere([-1.05, y, 0], 0.3, 10, IRON)                                   # breech
    add.sphere([-1.42, y, 0], 0.09, 8, IRON)                                   # cascabel
    add.cylinder([-1.3, y, 0], [-1.42, y, 0], 0.05, 8, IRON)
    for x, r in ((-0.6, 0.34), (0.2, 0.31), (0.9, 0.28), (1.85, 0.25)):         # reinforcing rings, the muzzle ring
        add.torus([x, y + 0.08 * (x + 1) / 2.4, 0], r - 0.03, 0.035, k_(18), 8, RING, axis=(1, 0, 0))
    for sz in (-0.4, 0.4):                                                    # trunnions on the cheeks
        add.cylinder([0.0, y, sz * 0.8], [0.0, y, sz], 0.08, 10, IRON)
    add.cylinder([-0.95, 0.5, 0.25], [-0.95, 0.5, 0.65], 0.02, 6, P["wood"])   # a ramrod leaning on the carriage
    add.cylinder([-0.95, 0.5, 0.65], [1.6, 0.3, 0.9], 0.02, 6, P["wood"])
    for j in range(3):                                                        # a pyramid of cannon balls, beside the carriage
        for i in range(3 - j):
            for k in range(3 - j):
                add.sphere([-1.4 + (i + 0.5 * j) * 0.5, 0.25 + j * 0.42, 1.3 + (k + 0.5 * j) * 0.5], 0.25, 10, IRON)
    add.cuboid([-0.9, 0.05, 1.8], [1.8, 0.1, 1.8], P["wood"])                  # ... on a wooden board
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def slab(quad, thick, color):
    """A slanted slab: the quad (four 3D points) extruded ``thick`` along
    its normal -- a lean-to roof with a real thickness."""
    n = vunit(vcross(vsub(quad[1], quad[0]), vsub(quad[3], quad[0])))
    top = [[p[k] + n[k] * thick for k in range(3)] for p in quad]
    M = add.Mesh()
    M.add_polygon(top, color)
    M.add_polygon(quad[::-1], color)
    for i in range(4):
        a, b = quad[i], quad[(i + 1) % 4]
        M.add_polygon([a, b, top[(i + 1) % 4], top[i]], color)
    return add.fix_normals(M)


def smithy(at, facing=0.0):
    """An open forge: posts and a lean-to roof, the hearth, anvil, trough, tools."""
    add.push()
    for sx in (-3.0, 3.0):
        add.cuboid([sx, 1.7, 2.4], [0.25, 3.4, 0.25], P["wood_dark"])
        add.cuboid([sx, 2.2, -2.4], [0.25, 4.4, 0.25], P["wood_dark"])
    brick_box([0, 2.2, -2.5], [6.4, 4.4, 0.3])                                                   # the back wall
    add.mesh(slab([[-3.4, 3.4, 2.9], [3.4, 3.4, 2.9], [3.4, 4.4, -2.8], [-3.4, 4.4, -2.8]], 0.2, P["slate"]))
    tile_face([-3.4, 3.6, 2.9], [3.4, 3.6, 2.9], [3.4, 4.6, -2.8], [-3.4, 4.6, -2.8], size=(0.45, 0.4), colours="slate")
    for i in range(4):
        add.beam([-3.2 + i * 2.1, 3.3, 2.6], [-3.2 + i * 2.1, 4.3, -2.6], 0.15, 0.15, P["wood_dark"])
    brick_box([-1.6, 0.5, -1.4], [2.2, 1.0, 1.8])                                                # the hearth
    add.cuboid([-1.6, 1.05, -1.4], [1.6, 0.1, 1.2], P["black"])
    for i in range(5):
        add.sphere([-1.9 + 0.15 * i, 1.2 + 0.12 * i, -1.5 + 0.1 * add.sin(i * 2)], 0.28 - 0.03 * i, 8, FLAME)
    add.sphere([-1.6, 1.25, -1.4], 0.18, 6, P["flame_core"])
    brick_box([-1.6, 3.0, -2.0], [1.0, 4.0, 0.9])                                                # chimney
    for i in range(4):
        add.sphere([-1.6 + 0.2 * add.sin(i), 5.3 + 0.7 * i, -2.0], 0.3 + 0.1 * i, 8, SMOKE)
    add.cylinder([1.0, 0, 0.2], [1.0, 0.7, 0.2], 0.35, k_(10), P["trunk"])                       # the anvil on a stump
    add.cuboid([1.0, 0.85, 0.2], [0.5, 0.3, 0.3], P["iron"])
    add.cuboid([1.0, 1.08, 0.2], [1.1, 0.16, 0.34], P["iron"])
    add.cone([1.55, 1.08, 0.2], [2.0, 1.08, 0.2], 0.09, 8, P["iron"])
    add.cylinder([1.2, 1.16, 0.1], [1.2, 1.55, 0.6], 0.03, 6, P["wood"])                          # a hammer left on it
    add.cuboid([1.2, 1.55, 0.6], [0.14, 0.14, 0.3], P["iron"])
    add.cuboid([2.2, 0.35, -1.2], [1.6, 0.7, 0.8], P["wood_dark"])                                # the water trough
    add.cuboid([2.2, 0.66, -1.2], [1.5, 0.04, 0.7], WATER)
    for i in range(4):                                                                             # horseshoes on the wall
        add.torus([-2.6 + i * 0.5, 2.4, -2.32], 0.14, 0.035, 12, 6, P["iron"], axis=(0, 0, 1))
    add.polyline([[2.6, 0.0, 1.2], [2.6, 1.2, 1.2]], 0.04, 6, P["iron"])                           # tongs leaning on a post
    add.polyline([[2.7, 0.0, 1.3], [2.65, 1.2, 1.2]], 0.04, 6, P["iron"])
    add.wheel([-2.6, 0.6, 1.2], 0.6, 0.25, P["stone_dark"], (1, 0, 0), k_(14), hub_color=P["iron"])   # the grindstone
    add.cuboid([-2.6, 0.3, 1.2], [0.5, 0.6, 1.3], P["wood_dark"])
    standing_man([0.2, 0, 0.9], add.pi, P["wood"])                                                 # the smith
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def cottage(at, facing=0.0, w=7.0, d=5.0, h=3.6):
    """A half-timbered house with a thatched roof."""
    add.push()
    add.cuboid([0, h / 2, 0], [w, h, d], P["white"])
    for x in (-w / 2, w / 2):
        add.cuboid([x, h / 2, 0], [0.2, h, 0.2], P["wood_dark"])
        for z in (-d / 2, d / 2):
            add.cuboid([x, h / 2, z], [0.2, h, 0.2], P["wood_dark"])
    for z in (-d / 2, d / 2):
        for i in range(1, int(w / 1.5)):
            if z < 0 or abs(-w / 2 + i * 1.5) > 0.75:                                       # no stud across the door
                add.cuboid([-w / 2 + i * 1.5, h / 2, z], [0.16, h, 0.14], P["wood_dark"])
        add.cuboid([0, h - 0.1, z], [w, 0.2, 0.14], P["wood_dark"])
        if z < 0:
            add.cuboid([0, h / 2, z], [w, 0.16, 0.14], P["wood_dark"])
        else:                                                                                # the middle rail stops at the door
            for x0, x1 in ((-w / 2, -0.75), (0.75, w / 2)):
                add.cuboid([(x0 + x1) / 2, h / 2, z], [x1 - x0, 0.16, 0.14], P["wood_dark"])
        add.beam([-w / 2, 0.2, z], [-w / 2 + 1.5, h / 2 - 0.1, z], 0.12, 0.12, P["wood_dark"])
        add.beam([w / 2, 0.2, z], [w / 2 - 1.5, h / 2 - 0.1, z], 0.12, 0.12, P["wood_dark"])
    for x in (-w / 2, w / 2):
        add.cuboid([x, h / 2, 0], [0.14, 0.16, d], P["wood_dark"])
    for sx in (-w / 4, w / 4):                                                               # windows
        add.cuboid([sx, h * 0.55, d / 2 + 0.02], [1.0, 1.0, 0.06], GLASS)
        add.cuboid([sx, h * 0.55, d / 2 + 0.05], [1.1, 0.08, 0.08], P["wood_dark"])
        add.cuboid([sx, h * 0.55, d / 2 + 0.05], [0.08, 1.1, 0.08], P["wood_dark"])
        for dx in (-0.55, 0.55):
            add.cuboid([sx + dx, h * 0.55, d / 2 + 0.05], [0.08, 1.1, 0.08], P["wood_dark"])
    add.cuboid([0, 1.35, d / 2 + 0.03], [1.3, 2.7, 0.1], P["wood_dark"])                      # the door, a head above a man
    add.sphere([0.45, 1.0, d / 2 + 0.1], 0.06, 4, P["gold"])
    thatch = add.make(add.roof, [0, h, 0], [w + 0.6, d + 0.6], 2.6, P["straw"], 0.4)
    add.mesh(add.rotateY(thatch, add.pi / 2))
    add.cuboid([w / 4, h + 2.0, 0], [0.7, 2.5, 0.7], P["stone_dark"])
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def chicken(at, facing=0.0):
    add.push()
    add.mesh(add.stretch(add.make(add.sphere, [0, 0.32, 0], 0.22, 8, P["white"]), [1.3, 0.9, 1.0], (0, 0.32, 0)))
    add.sphere([0.3, 0.55, 0], 0.11, 6, P["white"])
    add.cone([0.4, 0.55, 0], [0.55, 0.53, 0], 0.035, 5, P["orange"])
    add.cuboid([0.3, 0.68, 0], [0.12, 0.08, 0.03], P["red"])
    for sz in (-0.08, 0.08):
        add.sphere([0.36, 0.58, sz], 0.02, 3, P["black"])
    add.mesh(add.make(add.prism, [[-0.2, 0.35], [-0.5, 0.6], [-0.45, 0.3]], 0.05, P["black"], (0, 0, 0), (0, 0, 1)))
    for sz in (-0.08, 0.08):
        add.cylinder([0.02, 0.15, sz], [0.02, 0, sz], 0.02, 5, P["orange"])
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def haystack(at, r=1.3, h=2.2):
    add.cone(at, [at[0], at[1] + h, at[2]], r, k_(12), P["straw"])
    add.cylinder([at[0], at[1] + h - 0.3, at[2]], [at[0], at[1] + h + 0.5, at[2]], 0.05, 6, P["wood_dark"])


def garden(at, w=8.0, d=5.0):
    """Flower beds with a low hedge round a small tree."""
    add.push()
    for x in (-w / 2, w / 2):
        add.cuboid([x, 0.3, 0], [0.5, 0.6, d + 0.5], P["leaf_dark"])
    for z in (-d / 2, d / 2):
        add.cuboid([0, 0.3, z], [w + 0.5, 0.6, 0.5], P["leaf_dark"])
    add.cuboid([0, 0.05, 0], [w - 0.6, 0.1, d - 0.6], P["trunk"])
    add.seed(9)
    for i in range(count(300)):
        x, z = add.uniform(-w / 2 + 0.6, w / 2 - 0.6), add.uniform(-d / 2 + 0.6, d / 2 - 0.6)
        if abs(x) < 1.0 and abs(z) < 1.0:
            continue
        add.cylinder([x, 0.1, z], [x, 0.45, z], 0.015, 4, P["leaf"])
        add.sphere([x, 0.5, z], 0.09, 4, add.choice([P["red"], P["cheese"], P["white"], P["purple"], P["orange"]]))
    add.tree([0, 0.1, 0], 3.5, P["trunk"], P["leaf"], "round", 12, seed=3)
    add.mesh(add.move(add.pop(), at))


def market(at, facing=0.0):
    """A market stall: a counter under a striped awning, and the goods."""
    add.push()
    add.cuboid([0, 0.93, 0], [4.0, 0.06, 1.6], P["wood_dark"])
    plank_floor(-2.0, 2.0, -0.8, 0.8, 1.0, thick=0.04, width=0.27, length=4.0, along="x")
    for sx in (-1.8, 1.8):
        for sz in (-0.6, 0.6):
            add.cuboid([sx, 0.45, sz], [0.12, 0.9, 0.12], P["wood_dark"])
        add.cuboid([sx, 1.9, -0.9], [0.12, 2.0, 0.12], P["wood_dark"])
        add.cuboid([sx, 1.5, 0.9], [0.12, 1.2, 0.12], P["wood_dark"])
    for i in range(8):                                                                   # the striped awning
        x = -2.0 + i * 0.5 + 0.25
        add.mesh(slab([[x - 0.25, 2.9, -1.1], [x + 0.25, 2.9, -1.1], [x + 0.25, 2.1, 1.2], [x - 0.25, 2.1, 1.2]], 0.03,
                      P["red"] if i % 2 else P["white"]))
    bowl([-1.4, 1.0, 0.2], 0.4, P["wood_light"], (P["apple"], P["apple"], P["cheese"]))
    bowl([-0.6, 1.0, -0.3], 0.4, P["wood_light"], (P["orange"], P["orange"]))
    bread([0.2, 1.0, 0.2], 3)
    cheese([1.0, 1.0, -0.3])
    for i in range(3):
        add.mesh(add.move(add.stretch(add.make(add.sphere, [0, 0, 0], 0.18, 8, P["steel"]), [0.6, 0.5, 1.7], (0, 0, 0)), [1.5, 1.1, -0.5 + i * 0.4]))
    jug([1.6, 1.0, 0.5])
    sack([-1.2, 0.0, 1.3], 0.4)
    sack([-0.4, 0.0, 1.4], 0.35)
    crate([0.9, 0.0, 1.4], 0.7)
    standing_man([0.3, 0, -0.7], add.pi, P["leaf"], hat=True)                                # the stallholder
    standing_man([-0.9, 0, 1.9], 0, P["blue"])                                                # a customer
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def horse(at, facing=0.0, color=None, saddle=True):
    """A horse standing still: body, neck, head, ears, eyes, mane, tail, four legs."""
    color = color or P["trunk"]
    add.push()
    add.capsule([-0.9, 1.35, 0], [0.9, 1.35, 0], 0.42, k_(12), color)
    add.capsule([0.8, 1.5, 0], [1.5, 2.3, 0], 0.22, k_(10), color)                       # neck
    add.mesh(add.move(add.stretch(add.make(add.sphere, [0, 0, 0], 0.24, 10, color), [1.9, 1.0, 0.9], (0, 0, 0)), [1.75, 2.35, 0]))
    add.sphere([2.15, 2.28, 0], 0.16, 8, color)                                            # muzzle
    for sz in (-0.1, 0.1):
        add.cone([1.5, 2.5, sz], [1.45, 2.8, sz * 1.5], 0.06, 6, color)
        add.sphere([2.0, 2.45, sz * 1.6], 0.035, 4, P["black"])
    for i in range(7):                                                                    # mane
        add.sphere([0.85 + i * 0.1, 1.85 + i * 0.1, 0], 0.1, 4, P["black"])
    add.polyline([[-1.2, 1.5, 0], [-1.45, 1.1, 0.05], [-1.5, 0.6, 0.0]], 0.06, 6, P["black"])   # tail
    for sx in (-0.65, 0.65):
        for sz in (-0.22, 0.22):
            add.capsule([sx, 1.2, sz], [sx, 0.15, sz], 0.11, k_(8), color)
            add.cylinder([sx, 0.15, sz], [sx, 0.0, sz], 0.12, 12, P["black"])
    if saddle:
        add.mesh(add.move(add.stretch(add.make(add.sphere, [0, 0, 0], 0.45, 10, P["red"]), [1.0, 0.5, 1.1], (0, 0, 0)), [0.1, 1.55, 0]))
        add.cuboid([0.1, 1.85, 0], [0.7, 0.2, 0.5], P["wood_dark"])
        add.torus([1.95, 2.3, 0], 0.2, 0.02, 12, 6, P["iron"], axis=(1, 0, 0))                # bridle
        add.polyline([[1.9, 2.2, 0.2], [0.6, 1.9, 0.25]], 0.015, 4, P["rope"])
        for sz in (-0.5, 0.5):
            add.polyline([[0.1, 1.75, sz], [0.1, 1.0, sz]], 0.02, 4, P["rope"])
            add.cuboid([0.1, 0.95, sz], [0.2, 0.05, 0.12], P["iron"])
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def rider(at, facing=0.0):
    """A knight in armour sitting on a horse, lance up."""
    add.push()
    horse([0, 0, 0], 0, P["wood_dark"])
    S, D = P["steel"], P["iron"]
    add.capsule([0.1, 2.05, 0], [0.1, 2.85, 0], 0.3, k_(10), S)
    add.sphere([0.1, 3.15, 0], 0.25, 8, S)
    add.cuboid([0.1, 3.1, 0.24], [0.34, 0.05, 0.08], P["black"])
    add.cone([0.1, 3.35, 0], [0.0, 3.7, 0], 0.05, 5, P["red"])
    for sz in (-1, 1):
        add.capsule([0.1, 2.0, sz * 0.25], [0.5, 1.4, sz * 0.5], 0.11, k_(8), S)
        add.cuboid([0.55, 1.3, sz * 0.5], [0.3, 0.15, 0.18], D)
        add.sphere([0.1, 2.75, sz * 0.4], 0.18, 8, D)
        add.capsule([0.15, 2.7, sz * 0.45], [0.6, 2.2, sz * 0.35], 0.09, k_(8), S)
    add.cylinder([0.6, 1.2, 0.35], [0.9, 5.0, 0.3], 0.04, 8, P["wood"])                       # the lance
    add.cone([0.9, 5.0, 0.3], [0.95, 5.5, 0.3], 0.06, 8, S)
    add.mesh(add.move(add.rotateY(arms(0.5, 0.7, 0.06), add.pi / 2), [0.62, 1.95, -0.72]))            # the shield on the far side
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def stable(at, facing=0.0):
    """An open stable with two stalls and horses, hay and a trough."""
    add.push()
    for sx in (-4.0, 0.0, 4.0):
        add.cuboid([sx, 1.6, 2.5], [0.25, 3.2, 0.25], P["wood_dark"])
        add.cuboid([sx, 2.0, -2.5], [0.25, 4.0, 0.25], P["wood_dark"])
    for i in range(28):                                                                          # the back wall: boards
        add.cuboid([-4.05 + (i + 0.5) * 0.3, 2.0, -2.6], [0.28, 4.0, 0.2], shade_of("wood", i % 3))
    for i in range(17):                                                                          # the side wall
        add.cuboid([-4.1, 1.6, -2.55 + (i + 0.5) * 0.3], [0.2, 3.2, 0.28], shade_of("wood", (i + 1) % 3))
    add.cuboid([0, 0.9, 0], [0.12, 1.8, 5.0], P["wood_light"])                              # the partition
    add.mesh(slab([[-4.5, 3.3, 3.0], [4.5, 3.3, 3.0], [4.5, 4.2, -2.9], [-4.5, 4.2, -2.9]], 0.25, P["straw"]))
    add.cuboid([0, 4.35, -2.9], [9.2, 0.3, 0.3], P["straw"])
    for sx in (-2.0, 2.0):
        for i in range(3):
            add.cuboid([sx, 0.4 + i * 0.5, 2.5], [3.8, 0.15, 0.1], P["wood_light"])          # the half doors
    for i in range(20):
        add.sphere([add.uniform(-3.6, -0.4), 0.15, add.uniform(-2.2, 1.8)], add.uniform(0.2, 0.35), 6, P["straw"])
    add.cuboid([2.0, 0.3, -1.9], [2.6, 0.6, 0.7], P["wood_dark"])
    add.cuboid([2.0, 0.55, -1.9], [2.5, 0.05, 0.6], WATER)
    horse([-2.0, 0, 0.2], add.pi / 2 + 0.2, P["trunk"], saddle=False)
    horse([2.0, 0, 0.0], -add.pi / 2 - 0.3, P["sand"], saddle=False)
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def fence(a, b, h=1.1, rails=2, color=None):
    color = color or P["wood_dark"]
    L = vlen(vsub(b, a))
    n = max(1, int(L / 2.2))
    for i in range(n + 1):
        t = i / float(n)
        p = [a[k] + (b[k] - a[k]) * t for k in range(3)]
        add.cuboid([p[0], p[1] + h / 2, p[2]], [0.15, h, 0.15], color)
    for j in range(rails):
        y = h * (j + 1) / (rails + 1) + 0.1
        add.beam([a[0], a[1] + y, a[2]], [b[0], b[1] + y, b[2]], 0.1, 0.16, color)


def dovecote(at):
    add.cylinder(at, [at[0], at[1] + 3.6, at[2]], 0.7, k_(12), P["white"])
    add.cone([at[0], at[1] + 3.6, at[2]], [at[0], at[1] + 4.8, at[2]], 0.95, k_(12), P["slate"])
    for i in range(6):
        a = 2 * add.pi * i / 6
        add.cuboid([at[0] + 0.66 * add.cos(a), at[1] + 2.6 + (i % 2) * 0.6, at[2] + 0.66 * add.sin(a)], [0.2, 0.28, 0.2], P["black"])
        add.cuboid([at[0] + 0.72 * add.cos(a), at[1] + 2.42 + (i % 2) * 0.6, at[2] + 0.72 * add.sin(a)], [0.34, 0.05, 0.34], P["wood"])
    for i in range(4):
        a = 1.0 + i * 1.7
        bird([at[0] + 0.85 * add.cos(a), at[1] + 2.5 + (i % 2) * 0.6, at[2] + 0.85 * add.sin(a)], a + add.pi, 0.35, P["white"], False)


def bird(at, facing=0.0, size=1.0, color=None, flying=True):
    """A bird: body, head with eyes and a beak, a tail, two wings (spread
    when flying, folded when perched)."""
    color = color or P["white"]
    add.push()
    add.mesh(add.stretch(add.make(add.sphere, [0, 0, 0], 0.25, 8, color), [2.0, 0.7, 0.8], (0, 0, 0)))
    add.sphere([0.5, 0.12, 0], 0.14, 8, color)
    add.cone([0.6, 0.1, 0], [0.82, 0.08, 0], 0.05, 6, P["orange"])
    for s in (-1, 1):
        add.sphere([0.56, 0.18, s * 0.09], 0.03, 4, P["black"])
    add.mesh(add.make(add.prism, [[-0.4, 0.0], [-0.95, 0.16], [-0.95, -0.16]], 0.05, P["black"], (0, 0, 0), (0, 1, 0)))   # tail, on the centre line
    for s in (-1, 1):
        if flying:
            wing = add.make(add.prism, [[0.2, 0], [-0.35, s * 1.4], [0.35, s * 1.4]], 0.04, color, (0, 0.05, 0), (0, 1, 0))
            add.mesh(add.rotateX(wing, -s * 0.25))
        else:
            add.mesh(add.stretch(add.make(add.sphere, [0, 0, 0], 0.16, 6, P["stone_dark"]), [1.6, 0.5, 0.6], (0, 0, 0)))
    M = add.pop()
    add.mesh(add.move(add.rotateY(add.stretch(M, [size, size, size], (0, 0, 0)), facing), at))


def dog(at, facing=0.0):
    add.push()
    add.capsule([-0.35, 0.45, 0], [0.35, 0.45, 0], 0.17, k_(8), P["wood_light"])
    add.sphere([0.5, 0.65, 0], 0.15, 8, P["wood_light"])
    add.capsule([0.55, 0.6, 0], [0.75, 0.55, 0], 0.07, 8, P["wood_light"])
    add.sphere([0.8, 0.55, 0], 0.035, 4, P["black"])
    for sz in (-0.1, 0.1):
        add.sphere([0.58, 0.7, sz], 0.025, 3, P["black"])
        add.mesh(add.make(add.prism, [[0, 0], [0.12, 0], [0.06, 0.2]], 0.03, P["wood_dark"], (0.45, 0.75, sz), (0, 0, 1)))
    for sx in (-0.3, 0.3):
        for sz in (-0.1, 0.1):
            add.cylinder([sx, 0.4, sz], [sx, 0.0, sz], 0.05, 6, P["wood_light"])
    add.polyline([[-0.5, 0.5, 0], [-0.7, 0.75, 0.05]], 0.04, 6, P["wood_light"])
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def laundry(a, b):
    """A washing line with clothes on it."""
    for p in (a, b):
        add.cylinder(p, [p[0], p[1] + 2.4, p[2]], 0.06, 8, P["wood_dark"])
    add.polyline([[a[0], a[1] + 2.3, a[2]], [(a[0] + b[0]) / 2, a[1] + 2.15, (a[2] + b[2]) / 2], [b[0], b[1] + 2.3, b[2]]], 0.015, 6, P["rope"], smooth=1)
    L = vlen(vsub(b, a))
    d = vunit(vsub(b, a))
    for i in range(int(L / 1.1)):
        t = (i + 0.5) / int(L / 1.1)
        p = [a[k] + (b[k] - a[k]) * t for k in range(3)]
        cloth = add.make(add.cuboid, [0, 0, 0], [0.8, 1.0 + 0.3 * (i % 2), 0.04],
                         [P["white"], P["blue"], P["red"], P["cheese"], P["leaf"]][i % 5])
        add.mesh(add.move(add.rotateY(cloth, -add.atan2(d[2], d[0])), [p[0], p[1] + 2.15 - 0.5 - 0.15 * (i % 2) - 0.05 * add.sin(t * 6), p[2]]))


def tilt(a, b):
    """The barrier of the jousting lists, with pennants."""
    fence(a, b, 1.3, 1, P["white"])
    L = vlen(vsub(b, a))
    for i in range(int(L / 2.2) + 1):
        t = i / float(int(L / 2.2))
        p = [a[k] + (b[k] - a[k]) * t for k in range(3)]
        add.cylinder([p[0], p[1] + 1.3, p[2]], [p[0], p[1] + 2.3, p[2]], 0.03, 6, P["wood_dark"])
        sheet([[p[0], p[1] + 2.3, p[2]], [p[0] + 0.7, p[1] + 2.15, p[2]], [p[0], p[1] + 2.0, p[2]]], P["red"] if i % 2 else P["blue"])


def ladder_on_wall(k, along_t, h=8.5, lean=0.28):
    """A ladder leaning against the inner face of curtain wall ``k``: its
    foot on the ground, its top resting on the wall."""
    a, b = CORNERS[k], CORNERS[(k + 1) % 8]
    L, d, n = outward(a, b)
    p = [a[0] + d[0] * L * along_t, 0, a[2] + d[2] * L * along_t]           # a point on the wall's centre line
    inner = [p[0] - n[0] * 1.42, p[2] - n[2] * 1.42]                       # the inner face (blocks included)
    foot = [inner[0] - n[0] * h * add.sin(lean), inner[1] - n[2] * h * add.sin(lean)]
    add.push()
    for sx in (-0.35, 0.35):
        add.beam([sx, 0, 0], [sx, h * add.cos(lean), h * add.sin(lean)], 0.08, 0.08, P["wood"])
    for i in range(1, int(h / 0.45)):
        t = i * 0.45 / h
        add.cylinder([-0.35, h * add.cos(lean) * t, h * add.sin(lean) * t], [0.35, h * add.cos(lean) * t, h * add.sin(lean) * t], 0.035, 6, P["wood"])
    M = add.pop()                                                          # built leaning towards +z
    facing = add.atan2(n[0], n[2])                                         # turn +z to the wall's normal
    add.mesh(add.move(add.rotateY(M, facing), [foot[0], Y, foot[1]]))


well([12, Y, 24])
fountain([10, Y, 10])
market([-12, Y, 30], 0.3)
smithy([-34, Y, 6], add.pi / 2 - 0.3)
cottage([-33, Y, 22], add.pi / 2 + 0.2)
haystack([-30, Y, 34])
haystack([-27.5, Y, 36.5], 1.0, 1.8)
cart([-23, Y, 38], 0.4, "hay")
cart([17, Y, 42], -0.9, "barrels")
trebuchet([28, Y, 18], -0.7)
cannon([8, Y, 41], -0.3)
cannon([-8, Y, 41], 0.3)
weapon_rack([-26, Y, 12], 0.4)
weapon_rack([-22, Y, 14], 0.4)
dummy([-19, Y, 20])
plank_stack([30, Y, 30], 5, 0.3)
plank_stack([30, Y, 32.5], 3, 0.25)
brick_stack([33, Y, 25])
brick_stack([33, Y, 21], 5, 3, 2)
garden([32, Y, 6])
garden([-32, Y, -8], 6, 6)
for i in range(4):                                                                       # barrels and crates by the wall
    barrel([36 + (i % 2) * 1.0, Y + (1.2 if i >= 2 else 0), 10 + (i % 2) * 0.1], 0.45, 1.2)
barrel([38.5, Y, 12.5], 0.45, 1.2, upright=False)
crate([36, Y, 14], 0.9)
crate([36, Y + 0.9, 14], 0.8)
crate([37.5, Y, 14.5], 0.7)
sack([35, Y, 16], 0.4)
sack([35.8, Y, 16.4], 0.36)
add.seed(21)
for i in range(9):                                                                       # chickens round the cottage
    chicken([-30 + add.uniform(-6, 5), Y, 24 + add.uniform(-4, 6)], add.uniform(0, 6.28))
for x, z in ((15, 8), (-15, 8), (40, 0), (-40, 0), (24, 40), (-18, 40)):                 # trees in the yard
    assert in_yard(x, z, 2.8), (x, z)
    add.tree([x, Y, z], 6.5, P["trunk"], P["leaf"], "round", 12, seed=int(x + z))
stable([10, Y, -40], 0)
fence([2, Y, -36], [2, Y, -44])
fence([18, Y, -36], [18, Y, -44])
horse([14, Y, -38], 0.5, P["wood_light"], saddle=False)
dovecote([-6, Y, -40])
rider([-6, Y, 36], 0.9)
tilt([4, Y, 30], [16, Y, 30])
add.cuboid([-5, Y + 0.7, 39], [0.4, 1.4, 0.4], P["stone_dark"])                          # a mounting block
laundry([-40, Y, 14], [-38, Y, 22])
dog([9, Y, 20], 2.5)
dog([-20, Y, 26], -1.0)
ladder_on_wall(7, 0.62)
ladder_on_wall(3, 0.62)
standing_man([-10, Y, 22], 1.0, P["red"])                                                 # people about the yard
standing_man([14, Y, 27], -2.0, P["blue"], hat=True)
standing_man([20, Y, 36], 2.6, P["leaf"])
add.seed(31)
for i in range(count(10)):                                                                # birds over the lake and the yard
    a = i * 1.1
    bird([70 * add.cos(a), 26 + 4 * add.sin(i * 2.1), 70 * add.sin(a)], a + add.pi / 2, 1.0)
flush("courtyard")

# torches along the inside of the wall, flags on the towers, guards on duty
for k in range(8):
    a, b = CORNERS[k], CORNERS[(k + 1) % 8]
    L, d, n = outward(a, b)
    for t in (0.25, 0.5, 0.75):
        if k == 1 and abs(t - 0.5) < 0.3:
            continue
        p = [a[0] + d[0] * L * t - n[0] * 1.45, G + 3.5, a[2] + d[2] * L * t - n[2] * 1.45]
        torch(p, add.atan2(-n[0], -n[2]))
for k, c in enumerate(CORNERS):
    top = TOWER_TOP + 0.35 + 3.0 + 8.0
    add.cylinder([c[0], top, c[2]], [c[0], top + 3.5, c[2]], 0.06, 8, P["iron"])
    add.sphere([c[0], top + 3.55, c[2]], 0.09, 6, P["gold"])
    flag([c[0], top + 3.4, c[2]], 1.4, 1.0, add.pi * 0.3 + k * 0.05, phase=k * 0.8)   # all flying the same wind
a, b = CORNERS[0], CORNERS[1]
L, d, n = outward(a, b)
armour([a[0] + d[0] * L * 0.35, WALK, a[2] + d[2] * L * 0.35], add.atan2(d[0], d[2]))          # patrolling the walk
a, b = CORNERS[4], CORNERS[5]
L, d, n = outward(a, b)
armour([a[0] + d[0] * L * 0.6, WALK, a[2] + d[2] * L * 0.6], add.atan2(-d[0], -d[2]), weapon="sword")
lying_armour([a[0] + d[0] * L * 0.3, WALK, a[2] + d[2] * L * 0.3], add.atan2(d[0], d[2]))        # ... and one asleep on it
for k, c in enumerate(CORNERS):                                                              # a crossbowman on every tower top,
    aa = PHI[k]                                                                              # at the parapet, facing out ...
    if (aa - (ARRIVE[k] - HEADROOM - 0.35)) % (2 * add.pi) < HEADROOM + 0.95:                # ... clear of the stairwell and its wall
        aa = ARRIVE[k] + 0.7
    armour([c[0] + 2.3 * add.cos(aa), TOWER_TOP, c[2] + 2.3 * add.sin(aa)], add.atan2(add.cos(aa), add.sin(aa)),
           weapon="crossbow", shield=False)
for k in (2, 3, 4, 5, 6):                                                                    # archers on the wall walk, each at an
    a, b = CORNERS[k], CORNERS[(k + 1) % 8]                                                  # embrasure between two merlons
    L, d, n = outward(a, b)
    for t in (0.3, 0.7):
        x = TOWER_R - 0.5 + 1.85 + 2.3 * round((t * (L - 2 * (TOWER_R - 0.5)) - 1.85) / 2.3)
        armour([a[0] + d[0] * x + n[0] * 0.25, WALK, a[2] + d[2] * x + n[2] * 0.25], add.atan2(n[0], n[2]),
               weapon="bow" if (k + int(t * 10)) % 2 else "crossbow", shield=False)
flush("wall walk")


# --------------------------------------------------------------------------
#  Done: close both files (this writes the .mtl and the OFF header) and report
# --------------------------------------------------------------------------
out.close()
out_obj.close()
colours = len(out_obj.materials)
print("\n%s: %d faces, %d vertices, %.1f MB" % (OUT_OFF, out.faces, out.vertices, out.bytes / 1e6))
print("%s: the same model, %.1f MB, %d colours (materials), %.0f s" % (OUT_OBJ, out_obj.bytes / 1e6, colours, time.time() - started))
print("no textures; %d colours of the %d allowed" % (colours, COLOR_LIMIT))
assert colours <= COLOR_LIMIT, "too many colours"
print("Compress castle.obj and castle.mtl with 7-Zip for Sketchfab (under 100 MB).")

"""
46 -- Algoritmų pilis: the castle. The showcase model of add.py 2.0.

A castle on a hill in a transparent lake, with everything a castle needs:
an octagonal curtain wall of individual stone blocks, eight hollow round
towers with spiral stairs, doors and lookout platforms, a gatehouse -- its
passage vaulted in stone and lit by torches, a portcullis running in its
grooves -- and a drawbridge on a long iron hinge, hanging on real chains
over the moat -- a pond of natural outline lined with rough stone blocks,
its water right up to the walls and towers on both sides of the gate, so
that the only dry way in is over the bridge onto the landing where the
guards stand; piranhas circle in it, and leap; guns on the towers and over
the gate, each with its gunner; from the end of the bridge a road paved
with fieldstones runs along the moat and on down round the hill, gently
and level across, with a low stone wall on its outer side, to the harbour:
a wharf on piles where two great ships are moored, the king's with a ramp
down from its side for a knight to lead his horse ashore, and a
merchant's; rowing boats are tied up all round the shore. Inside: a palace
with glass windows, a porch on columns, balconies, dormers, a roof of
single tiles and copper spires, a chapel with stained glass and an altar,
and a courtyard full of life: a well, a fountain, a smithy, the kitchen
and bakehouse with its hearth, table and beds, log houses for the castle's
folk with hay lofts to sleep in, a half-timbered cottage, a storehouse, a
market, a stable, gardens, a field of rye, archery butts, a trebuchet,
cannons, carts, barrels, crates, planks, bricks, weapon racks, knights in
armour with the castle's arms, archers and crossbowmen in mail, townsfolk,
horses, chickens, a dog. Spruces, pines, birches, oaks, elms and limes
grow on the slopes; gulls wheel over the lake. The lake is transparent, so
the fish, the pebbles and the sunken boat can be seen through the water.

Easter eggs, for anyone who walks inside: the great hall with the king on
his throne, his counsellor and his fool, musicians, a feast on the long
tables for thirty-two guests (roast pig, chickens, fish, pies, ham,
sausages, cakes, bread, cheese, fruit, wine), the great fireplace,
chandeliers, a chess study where a commoner has White against a knight
("White to play and win"), a Latin motto above the throne, and beside the
dais a stair down to the wine cellar; the soldiers' dormitory upstairs,
with beds and bunks for the whole garrison; the attic, where the guests
sleep among the old junk and the mice; the chapel's attic, through a door
from the dormitory, with the priests' beds, the vestments, and the chalice,
the wine and the hosts on a small table; and, in the big tower, the
treasury with a dragon on the gold breathing fire, the armoury with a man
at the grindstone, the chamber of the king and the princess -- and the
princess herself on the top.  Everyone who lives in the castle has a bed.

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
P["mail"] = [128, 132, 140]                             # chain mail: the archers' and crossbowmen's shirts and coifs
P["rose"] = [212, 110, 150]                              # the princess's gown and some of the ladies'
P["birch_leaf"] = [132, 178, 74]                         # the light leaves of the birches,
P["needles"] = [36, 80, 56]                              # the blue-green needles of pines and spruces,
P["oak_leaf"] = [70, 106, 38]                            # the dark leaves of oaks
P["bark_red"] = [168, 98, 64]                            # and the red upper bark of pines
P["granite"] = [168, 130, 118]                          # the pinkish granite of fieldstones: the road to the harbour
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


def clip_half(poly, a, b, c):
    """The part of the convex polygon ``poly`` (a list of (x, y) points)
    where a*x + b*y <= c."""
    out = []
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        dp, dq = a * p[0] + b * p[1] - c, a * q[0] + b * q[1] - c
        if dp <= 0:
            out.append(p)
        if (dp < 0 < dq) or (dq < 0 < dp):
            t = dp / (dp - dq)
            out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return out


def poly_area(poly):
    """Signed area of a polygon in the plane (positive: anticlockwise)."""
    n = len(poly)
    return sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n)) / 2.0


def shrunk(poly, g):
    """The convex polygon ``poly`` with every edge moved in by ``g`` -- a
    stone cut from it with a mortar joint all round; None if nothing is left."""
    area = poly_area(poly) if len(poly) > 2 else 0.0
    if abs(area) < 1e-9:                                                  # a point or a line: nothing to cut
        return None
    sg = 1.0 if area > 0 else -1.0
    out = [(-1e4, -1e4), (1e4, -1e4), (1e4, 1e4), (-1e4, 1e4)]
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        L = add.sqrt((q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2)
        if L > 1e-9:
            a, b = sg * (q[1] - p[1]) / L, -sg * (q[0] - p[0]) / L        # the outward normal of this edge
            out = clip_half(out, a, b, a * p[0] + b * p[1] - g)
            if len(out) < 3:
                return None
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    if any(not (min(xs) - 1e-6 <= q[0] <= max(xs) + 1e-6 and min(ys) - 1e-6 <= q[1] <= max(ys) + 1e-6) for q in out):
        return None                                                       # (never more than the polygon it came from)
    return out if abs(poly_area(out)) > 1e-6 else None


def lathe(points, at, k, color, scale=1.0):
    """A turned object (goblet, jug, bowl, candlestick): ``points`` are
    ``[radius, height]`` pairs of the profile, bottom first."""
    n = len(points) - 1
    pts = [[r * scale, h * scale] for r, h in points]
    add.revolve(lambda t: pts[min(n, int(round(t)))], at, [at[0], at[1] + 1, at[2]], 0, n, n, k, color)


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


def brick_box(centre, size, name="brick", flue=None):
    """A brick-built block: a mortar core with skins of small bricks on the
    four vertical faces (chimneys, hearths, the smithy's wall).  A chimney
    gets its ``flue`` = (width, depth, how deep): a soot-black shaft open at
    the top, where the smoke comes out."""
    cx, cy, cz = centre
    w, h, d = size
    core = add.make(add.cuboid, centre, size, P["mortar"])
    if flue:
        fw, fd, deep = flue
        core = add.difference(core, add.make(add.cuboid, [cx, cy + h / 2 - deep / 2 + 0.05, cz], [fw, deep + 0.1, fd], P["black"]))
    add.mesh(core)
    for face in range(4):
        add.push()
        stone_face(w if face % 2 == 0 else d, 0, h, 0, 0.06, name, size=(0.4, 0.2), gap=0.03, seed=face + int(cx * 3))
        M = add.move(add.pop(), [-(w if face % 2 == 0 else d) / 2, -h / 2, (d if face % 2 == 0 else w) / 2])
        add.mesh(add.move(add.rotateY(M, face * add.pi / 2), centre))


def chimney_cap(centre, w, d, t, flue):
    """The stone slab on top of a chimney, ``w`` x ``d`` and ``t`` thick,
    with the opening of the ``flue`` (width, depth) through it."""
    cap = add.make(add.cuboid, centre, [w, t, d], P["stone_dark"])
    add.mesh(add.difference(cap, add.make(add.cuboid, centre, [flue[0], t + 0.2, flue[1]], P["black"])))


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


def wall_segment(a, b, y0, y1, t=2.4, walk=True, inner=True):
    """A piece of curtain wall from ``a`` to ``b``: a core, faces of stone
    blocks on both sides (``inner=False``: outside only -- a foundation), a
    walk on top with a crenellated parapet outside and a low one inside."""
    L, d, n = outward(a, b)
    add.push()
    add.cuboid([L / 2, (y0 + y1) / 2, 0], [L, y1 - y0, t], P["mortar"])
    stone_face(L, y0, y1, t / 2, 0.22, "stone", seed=int(a[0] + a[2]) + (0 if inner else 3))
    if inner:
        stone_face(L, y0, y1, -t / 2, -0.22, "stone_dark", seed=int(a[0] - a[2]))
    if walk:
        add.cuboid([L / 2, y1 + 0.15, 0], [L, 0.3, t + 0.5], P["mortar"])
        flagstones(0, L, -t / 2 - 0.25, t / 2 + 0.25, y1 + 0.3)
        merlons(L, y1 + 0.3, t / 2 - 0.5, t / 2 + 0.25)
        add.cuboid([L / 2, y1 + 0.6, -t / 2 + 0.2], [L, 0.6, 0.4], P["stone"])
    M = add.pop()
    add.mesh(frame_to(M, [a[0], 0, a[2]], d, n))


def cone_roof(centre, y, r, h, k, tiles=True, color=None, colours="slate", size=None):
    """A conical roof of individual slates -- or, with ``colours="spire"``,
    of the palace's clay tiles, the size of the tiles on its roof
    (``size``: width and height of a tile) -- or a plain ``color`` cone."""
    cx, cz = centre[0], centre[2]
    if color is not None:
        add.cone([cx, y, cz], [cx, y + h, cz], r, k, color)
        add.sphere([cx, y + h + 0.3, cz], 0.35, 8, P["gold"])
        return
    add.cone([cx, y, cz], [cx, y + h, cz], r, k, P[colours])
    if not tiles:
        return
    tw, th = size or (0.42, 0.45)
    rows = max(4, int((h if size is None else add.sqrt(h * h + r * r)) / th))
    for j in range(rows):
        t0, t1 = j / float(rows), (j + 1) / float(rows)
        r0, r1 = r * (1 - t0), r * (1 - t1)
        yy0, yy1 = y + h * t0, y + h * t1
        n = max(8, int(2 * add.pi * r0 / tw))
        for i in range(n):
            a0 = 2 * add.pi * (i + (0.5 if j % 2 else 0)) / n
            a1 = 2 * add.pi * (i + 0.92 + (0.5 if j % 2 else 0)) / n
            q = [[cx + (r0 + 0.05) * add.cos(a0), yy0 - 0.06, cz + (r0 + 0.05) * add.sin(a0)],
                 [cx + (r0 + 0.05) * add.cos(a1), yy0 - 0.06, cz + (r0 + 0.05) * add.sin(a1)],
                 [cx + (r1 + 0.05) * add.cos(a1), yy1, cz + (r1 + 0.05) * add.sin(a1)],
                 [cx + (r1 + 0.05) * add.cos(a0), yy1, cz + (r1 + 0.05) * add.sin(a0)]]
            add.polygon(q[::-1], shade_of(colours, int(hash2(i, j, 8) * 3)))
    if colours == "slate":
        add.cone([cx, y + h - 0.5, cz], [cx, y + h + 0.05, cz], 0.25, 8, P["slate"])
    else:
        add.sphere([cx, y + h + 0.3, cz], 0.35, 8, P["gold"])                          # a gold ball on the tip


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


def stone_ring(cx, cz, r, y0, y1, name="stone", skip=(), arc=None):
    """Courses of stone blocks round a drum of radius ``r``, every block a
    piece of the ring (or only the blocks between the angles ``arc``).
    ``skip`` lists the openings as ``(angle, half_width_angle, y_bottom,
    y_top[, arch_radius])``: the blocks are fitted round them -- cut short
    at the jambs, a sliver over the sill and under the head, and stepped
    round an arched head -- rather than left out, the way a mason closes up
    to a window."""
    bl, bh = BLOCK
    rows = int((y1 - y0) / bh)
    for j in range(rows):
        n = max(8, int(2 * add.pi * r / bl))
        for i in range(n):
            a = 2 * add.pi * (i + (0.5 if j % 2 else 0)) / n
            if arc and (a - arc[0]) % (2 * add.pi) > (arc[1] - arc[0]) % (2 * add.pi):
                continue
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
                slits=True, lantern=True, cutters=(), name="stone", windows=(), blocks=True, walls=(), stops=None,
                roof_tiles="slate"):
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
                for s in (-1, 1):                                                              # knee braces, their heads let
                    q = [cx + (r - 0.35) * add.cos(a + s * 0.28), base + 2.75, cz + (r - 0.35) * add.sin(a + s * 0.28)]
                    q = [px + (q[0] - px) * 1.25, base + 1.8 + 0.95 * 1.25, pz + (q[2] - pz) * 1.25]   # into the ring beam
                    add.beam([px, base + 1.8, pz], q, 0.14, 0.14, P["wood_dark"])
            add.pipe([cx, base + 2.8, cz], [cx, base + 3.15, cz], r + 0.9, r - 0.7, k, P["wood_dark"])
            base += 3.15
        cone_roof([cx, 0, cz], base, r + 0.9, roof_h, k, tiles=(roof_color is None), color=roof_color,
                  colours=roof_tiles, size=TILE if roof_tiles == "spire" else None)
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
    add.pyramid([cx, top - 0.1, cz], 1.2, 1.2, P["iron"])                       # a lead cap over the apex, and a flagpole
    add.cylinder([cx, top + 0.4, cz], [cx, top + 4.4, cz], 0.06, 8, P["iron"])  # with the castle's flag, like the round
    add.sphere([cx, top + 4.45, cz], 0.09, 6, P["gold"])                        # towers' and in the same wind
    flag([cx, top + 4.3, cz], 1.4, 1.0, add.pi * 0.3, phase=0.8 + 0.1 * cx)
    return arrive


# --------------------------------------------------------------------------
#  1. The hill, the lake and the moat
# --------------------------------------------------------------------------
G = 9.5                                                # the plateau: ground level inside the walls, 8 m over the lake
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
MOAT = (-20, 20, 56, 64)                               # where the bridge crosses the moat: x0, x1 and its two banks
MOAT_Y = G - 5.0                                       # the floor of the moat
CELLAR_STAIR = (9.3, 15.3, -28.7, -26.7)               # the wine cellar under the great hall: the stair's opening in the
CELLAR_ROOM = (10.0, 16.0, -28.6, -20.0)               # hall floor (x0, x1, z0, z1), the cellar itself,
CELLAR_Y = G - 3.1                                     # and its floor


TERRACE = (-23.0, 23.0, 52.0, 67.5)                    # level ground round the moat, where the bridge comes down,
BANK = 0.55                                            # its sides banked down to the hill at this slope


def hill(x, z):
    """Height of the hill as nature made it: a plateau, a slope, a cliff and the lake bed."""
    r = add.sqrt(x * x + z * z)
    if r <= 58:
        return PLATEAU
    cliff = add.clamp((-x / max(r, 1) - 0.55) / 0.3)      # the west side is a cliff
    run = add.lerp(36.0, 14.0, cliff)
    t = add.clamp((r - 58) / run)
    y = PLATEAU - (PLATEAU - 1.0) * t * t * (3 - 2 * t)
    if r > 58 + run:                                    # the shore and the lake bed
        y = 1.0 - 0.18 * (r - 58 - run)
    return max(y, -4.5) + 0.35 * add.sin(x / 7.0) * add.cos(z / 9.0) * (1 if r > 58 else 0)


# the road from the gate down to the harbour: from the end of the drawbridge it turns east and runs along the moat,
# only just going down (the moat's kerb a low wall beside it); past the moat it goes on down round the south-east
# side of the hill at a gentle grade, keeping to the slope -- cut into the hill on one side and banked up on the
# other, so that it is always level across -- and near the water it turns out onto the wharf.  ROAD is its centre
# line, a point a metre
ROAD_GRADE, ROAD_W, ROAD_BANK = 0.09, 2.5, 0.5         # the grade (1 in 11), half the width, the slope of its banks
DOCK_Y = WATER_Y + 1.0                                 # the top of the wharf's deck: the road comes down level with it
ROAD_Z = MOAT[3] + 1.0 + ROAD_W + 0.5                  # the road along the moat, clear of its kerb


def _hill_r(y):
    """How far out the gentle side of the hill comes down to height ``y``."""
    lo, hi = 58.0, 94.0
    for k in range(40):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if hill(mid, 0.0) > y else (lo, mid)
    return (lo + hi) / 2


def _kerb_gap(x, z):
    """How far (x, z) is from the kerb round the moat."""
    dx, dz = max(MOAT[0] - 1.0 - x, 0.0, x - MOAT[1] - 1.0), max(MOAT[2] - 1.0 - z, 0.0, z - MOAT[3] - 1.0)
    return add.sqrt(dx * dx + dz * dz)


ROAD = [(0.0, MOAT[3] + 1.0, PLATEAU)]                 # at the end of the drawbridge,
for k in range(1, 5):                                  # a quarter turn to the east,
    a = add.pi / 8 * k
    ROAD.append(((ROAD_Z - MOAT[3] - 1.0) * (1 - add.cos(a)), MOAT[3] + 1.0 + (ROAD_Z - MOAT[3] - 1.0) * add.sin(a), PLATEAU))
y = PLATEAU
while ROAD[-1][0] < TERRACE[1] - 5.0:                  # along the moat, 1 in 33,
    y -= 0.03 * add.clamp((ROAD[-1][0] - ROAD[4][0]) / 4.0)
    ROAD.append((ROAD[-1][0] + 1.0, ROAD_Z, y))
x, z, y = ROAD[-1]
head, grade = 0.0, 0.03                                # (the way it is going, as an angle in XZ; how steeply)
while y > DOCK_Y - 0.12:                               # and down round the hill,
    grade = min(ROAD_GRADE, grade + 0.01)                                         # easing into its grade
    y = max(DOCK_Y - 0.12, y - grade)
    r, a = add.sqrt(x * x + z * z), add.atan2(z, x)
    if y > DOCK_Y + 0.7:                                                          # keeping to where the hill is as high
        swing = add.clamp((_hill_r(y) - r) * 0.35, -0.6, 0.6)                     # as the road, round and in or out,
        want = add.atan2(-add.cos(a) + add.sin(a) * swing, add.sin(a) + add.cos(a) * swing)
    else:                                                                         # till near the water it turns out
        want = a                                                                  # towards the lake
    turn = (want - head + add.pi) % (2 * add.pi) - add.pi
    new = head + add.clamp(turn, -0.12, 0.12)                                     # on curves no tighter than 8 m
    while _kerb_gap(x + add.cos(new), z + add.sin(new)) < ROAD_W + 0.6 and new < head + 0.5:
        new += 0.02                                                               # (not cutting the moat's corner)
    head = new
    x, z = x + add.cos(head), z + add.sin(head)
    ROAD.append((x, z, y))
a = add.atan2(z, x)                                    # the last metre straight out, onto the wharf
ROAD.append((x + add.cos(a), z + add.sin(a), y))
DOCK_A = a                                             # the wharf runs on straight out into the lake
DOCK_C, DOCK_S = add.cos(DOCK_A), add.sin(DOCK_A)
DOCK_U0 = add.sqrt(ROAD[-1][0] ** 2 + ROAD[-1][1] ** 2)
DOCK_U1, DOCK_W = DOCK_U0 + 40.0, 4.0                  # from where the road ends, to; half its width
HARBOUR_Y = -4.6                                       # the lake bed dredged deep round the wharf, for the ships
_road_cells = {}                                       # a grid of 4 m cells: the pieces of the road near each
for k in range(len(ROAD) - 1):
    (x0, z0, y0), (x1, z1, y1) = ROAD[k], ROAD[k + 1]
    for i in range(int((min(x0, x1) - 20.0) // 4), int((max(x0, x1) + 20.0) // 4) + 1):
        for j in range(int((min(z0, z1) - 20.0) // 4), int((max(z0, z1) + 20.0) // 4) + 1):
            _road_cells.setdefault((i, j), []).append(k)


def road_at(x, z):
    """(how far (x, z) is from the road's centre line, the road's height
    there) -- or None, more than 20 m away."""
    best = None
    for k in _road_cells.get((int(x // 4), int(z // 4)), ()):
        (x0, z0, y0), (x1, z1, y1) = ROAD[k], ROAD[k + 1]
        dx, dz = x1 - x0, z1 - z0
        t = add.clamp(((x - x0) * dx + (z - z0) * dz) / (dx * dx + dz * dz))
        d = add.sqrt((x - x0 - t * dx) ** 2 + (z - z0 - t * dz) ** 2)
        if best is None or d < best[0]:
            best = (d, y0 + t * (y1 - y0))
    return best if best and best[0] < 20.0 else None


def by_terrace(x, z, margin=0.0):
    """On the terrace before the moat or over the moat (plus ``margin``)?"""
    return TERRACE[0] - margin < x < TERRACE[1] + margin and TERRACE[2] - 8 - margin < z < TERRACE[3] + margin


# the moat is a pond of natural outline before the south front: from the south-west corner tower round to the
# south-east one, its water comes right up to the curtain wall, the corner towers and the two gate towers, which go
# down to its floor -- nobody can walk round it to the gate.  The only dry way in is the drawbridge, onto the landing
# before the gate where the guards stand.  Its bank is lined with rough stone blocks (see "the moat's stonework").
GATE_X = 10.5                                          # the gatehouse takes the middle of the south wall
GATE_W = 7.0
GATE_Z0, GATE_Z1 = 47.0, 53.0                          # the gate passage, from the courtyard out to the landing
BRIDGE_X = 2.45                                        # half the width of the drawbridge's bed on its two seats,
BRIDGE_Z0, BRIDGE_Z1 = MOAT[2] - 1.0, MOAT[3] + 1.0    # and its two ends: the landing's edge, the far bank
DECK, HINGE_R = 2.3, 0.07                              # half the width of its deck, and the radius of the knuckles
                                                       # of the hinge it turns on, under the ends of its planks
WALL_FACE = 50.0 + 1.2 + 0.22                          # the outer face of the south curtain wall, its stones and all,
GATE_FRONT = 50.0 + GATE_W / 2 + 0.22                  # of the two gate towers,
TOWER_FACE = TOWER_R + 0.24                            # and of the corner towers


def _on_tower(c, deg):
    """The point on the stones of the corner tower ``c`` in the direction ``deg`` (degrees, in XZ)."""
    return (c[0] + TOWER_FACE * add.cos(deg * add.pi / 180), c[2] + TOWER_FACE * add.sin(deg * add.pi / 180))


def spline(points, step):
    """A smooth curve through ``points`` (in XZ; Catmull-Rom) as a polyline with points about ``step`` apart."""
    out = [points[0]]
    for k in range(len(points) - 1):
        p0, p1, p2, p3 = points[max(0, k - 1)], points[k], points[k + 1], points[min(len(points) - 1, k + 2)]
        n = max(1, int(add.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) / step + 0.5))
        for i in range(1, n + 1):
            t = i / float(n)
            out.append(tuple(0.5 * (2 * p1[j] + (p2[j] - p0[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (3 * p1[j] - p0[j] - 3 * p2[j] + p3[j]) * t * t * t) for j in range(2)))
    return out


MOAT_EDGE = spline([_on_tower(CORNERS[2], 94), (-21.3, 56.6), (-21.35, 58.8), (-20.85, 61.0), (-19.5, 62.75),
                    (-17.3, 63.65), (-14.2, 63.85), (-10.8, 63.45), (-7.4, 63.35), (-4.6, 63.8), (-3.2, 64.0),
                    (0.0, 64.0), (3.2, 64.0), (4.7, 63.75), (7.9, 63.3), (11.6, 63.55), (15.0, 63.9), (17.9, 63.5),
                    (19.9, 62.3), (21.0, 60.4), (21.35, 58.0), (21.25, 56.2), _on_tower(CORNERS[1], 86)], 0.25)
MOAT_OUTLINE = MOAT_EDGE + [(CORNERS[1][0], 50.0), (CORNERS[2][0], 50.0)]   # closed through the towers and the wall
LANDING = [(-6.6, GATE_Z1), (6.6, GATE_Z1), (6.6, 53.8), (5.2, 55.35), (4.95, 55.72), (4.6, 55.95), (4.3, 56.0),
           (-4.3, 56.0), (-4.6, 55.95), (-4.95, 55.72), (-5.2, 55.35), (-6.6, 53.8)]  # the landing: stone, before the gate
_moat_cells = {}                                       # a grid of 1 m cells: the pieces of the moat's edge near each
for k in range(len(MOAT_EDGE) - 1):
    (x0, z0), (x1, z1) = MOAT_EDGE[k], MOAT_EDGE[k + 1]
    for i in range(int((min(x0, x1) - 1.5) // 1), int((max(x0, x1) + 1.5) // 1) + 1):
        for j in range(int((min(z0, z1) - 1.5) // 1), int((max(z0, z1) + 1.5) // 1) + 1):
            _moat_cells.setdefault((i, j), []).append(k)


def bank_gap(x, z):
    """How far (x, z) is from the edge of the moat's water at ground level (up to 1.5 m: farther, 1.5)."""
    best = 1.5
    for k in _moat_cells.get((int(x // 1), int(z // 1)), ()):
        (x0, z0), (x1, z1) = MOAT_EDGE[k], MOAT_EDGE[k + 1]
        dx, dz = x1 - x0, z1 - z0
        t = add.clamp(((x - x0) * dx + (z - z0) * dz) / (dx * dx + dz * dz))
        best = min(best, add.sqrt((x - x0 - t * dx) ** 2 + (z - z0 - t * dz) ** 2))
    return best


def in_moat_outline(x, z):
    """Inside the edge of the moat, closed along the south front?"""
    inside = False
    for k in range(len(MOAT_OUTLINE)):
        (x0, z0), (x1, z1) = MOAT_OUTLINE[k], MOAT_OUTLINE[k - 1]
        if (z0 > z) != (z1 > z) and x < x0 + (x1 - x0) * (z - z0) / (z1 - z0):
            inside = not inside
    return inside


def castle_depth(x, z):
    """How far (x, z) lies inside the south front -- the curtain wall, the corner towers, the gate towers (their
    stones and all) and the gate passage, up to the landing; negative outside."""
    d = WALL_FACE - z
    for c in (CORNERS[1], CORNERS[2]):
        d = max(d, TOWER_FACE - add.sqrt((x - c[0]) ** 2 + (z - c[2]) ** 2))
    if abs(x) < GATE_W / 2:
        return max(d, GATE_Z1 - z)
    return max(d, min(GATE_FRONT - z, GATE_X + 0.22 - abs(x)))


def landing_depth(x, z, back=True):
    """How far (x, z) lies inside the landing (a convex outline) -- from its
    kerbs only, with ``back=False``, not from the gate; negative outside."""
    d = 1e9
    for k in range(len(LANDING)):
        if k == 1 and not back:                        # the edge from LANDING[0] to LANDING[1]: the foot of the gate
            continue
        (x0, z0), (x1, z1) = LANDING[k - 1], LANDING[k]
        L = add.sqrt((x1 - x0) ** 2 + (z1 - z0) ** 2)
        d = min(d, ((z - z0) * (x1 - x0) - (x - x0) * (z1 - z0)) / L)
    return d


def moat_dug(x, z):
    """Is the land dug out for the moat at (x, z)?  Under its water, 0.3 m in under the stones of its bank, and 0.6 m
    into the walls that stand in it (which go down to its floor); under the landing, a pier of solid masonry."""
    if not (-22.0 < x < 22.0 and 50.5 < z < 64.5):
        return False
    return (in_moat_outline(x, z) or bank_gap(x, z) < 0.3) and castle_depth(x, z) < 0.6


def in_moat(x, z, margin=0.0):
    """On the moat's water, or on its stone bank (with the coping: 1 m) plus ``margin``?"""
    if not (-23.5 - margin < x < 23.5 + margin and 50.0 < z < 66.0 + margin):
        return False
    return (in_moat_outline(x, z) or bank_gap(x, z) < 1.0 + margin) and castle_depth(x, z) < 0.0


def ground(x, z):
    """Height of the land: the hill, with the terrace round the moat, the
    road cut into its side and the harbour dug out of the lake bed."""
    y = hill(x, z)
    dx, dz = max(TERRACE[0] - x, 0.0, x - TERRACE[1]), max(TERRACE[2] - z, 0.0, z - TERRACE[3])
    y = max(y, PLATEAU - BANK * add.sqrt(dx * dx + dz * dz))
    q = road_at(x, z)
    if q:                                                                 # level across under the road and a verge
        d = max(0.0, q[0] - ROAD_W - 0.4)                                 # each side, then banked up to it or cut
        y = min(max(y, q[1] - ROAD_BANK * d), q[1] + ROAD_BANK * d)       # down to it at an even slope
    u, v = x * DOCK_C + z * DOCK_S, -x * DOCK_S + z * DOCK_C
    if u > DOCK_U0 + 5 and abs(v) < 34:
        w = add.clamp((u - DOCK_U0 - 5) / 12) * add.clamp((34 - abs(v)) / 18)
        y = min(y, y + (HARBOUR_Y - y) * w * w * (3 - 2 * w))
    if moat_dug(x, z):                                                    # the moat, down to its floor
        return MOAT_Y
    if abs(x) < BRIDGE_X - 0.05 and MOAT[3] <= z < BRIDGE_Z1 + 0.1:       # under the seat of the drawbridge's far end
        return min(y, G - 0.4)
    return y


def ground_color(x, z):
    if moat_dug(x, z):
        return P["lakebed"]                            # the moat's floor
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
        if CELLAR_STAIR[0] - 0.2 < x < CELLAR_STAIR[1] + 0.2 and CELLAR_STAIR[2] - 0.2 < z < CELLAR_STAIR[3] + 0.2:
            continue                                   # the stair down to the wine cellar
        land.add_face([land_vertex(i, j), land_vertex(i, j + 1),
                       land_vertex(i + 1, j + 1), land_vertex(i + 1, j)], ground_color(x, z))
# the land is a closed block: four sides down to BOTTOM, and an underside
edges = ([(0, j) for j in range(N_GROUND + 1)],                          # x = -150, along z
         [(i, N_GROUND) for i in range(N_GROUND + 1)],                   # z = +150, along x
         [(N_GROUND, j) for j in reversed(range(N_GROUND + 1))],         # x = +150
         [(i, 0) for i in reversed(range(N_GROUND + 1))])                # z = -150
for links in edges:
    for (i0, j0), (i1, j1) in zip(links, links[1:]):
        a, b = land_vertex(i0, j0), land_vertex(i1, j1)
        pa, pb = land.V[a], land.V[b]
        land.add_polygon([[pa[0], BOTTOM, pa[2]], [pb[0], BOTTOM, pb[2]], pb, pa], P["sand"])
land.add_polygon([[-WORLD / 2, BOTTOM, -WORLD / 2], [-WORLD / 2, BOTTOM, WORLD / 2],
                  [WORLD / 2, BOTTOM, WORLD / 2], [WORLD / 2, BOTTOM, -WORLD / 2]], P["sand"])
add.mesh(add.fix_normals(land))
land, index = None, None                               # free the memory
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
for links in edges:
    for (i0, j0), (i1, j1) in zip(links, links[1:]):
        pa, pb = water.V[water_vertex(i0, j0)], water.V[water_vertex(i1, j1)]
        water.add_polygon([[pa[0], W_BOTTOM, pa[2]], [pb[0], W_BOTTOM, pb[2]], pb, pa], WATER)
water.add_polygon([[-W_EDGE, W_BOTTOM, -W_EDGE], [-W_EDGE, W_BOTTOM, W_EDGE],
                   [W_EDGE, W_BOTTOM, W_EDGE], [W_EDGE, W_BOTTOM, -W_EDGE]], WATER)
add.mesh(add.fix_normals(water))
# the moat's water, a step below its bank: a closed block over the cells of the land's grid that it covers, down
# below its floor -- its ragged sides go into the stones of the bank, the walls and the landing, out of sight
MOAT_WATER = G - 0.75
wet = set()
for i in range(int((WORLD / 2 - 23.0) / cell), int((WORLD / 2 + 23.0) / cell) + 1):
    for j in range(int((WORLD / 2 + 50.5) / cell), int((WORLD / 2 + 65.0) / cell) + 1):
        x, z = -WORLD / 2 + (i + 0.5) * cell, -WORLD / 2 + (j + 0.5) * cell
        if (in_moat_outline(x, z) or bank_gap(x, z) < 0.25) and castle_depth(x, z) < 0.3 and landing_depth(x, z) < 0.3:
            wet.add((i, j))
water = add.Mesh()
windex = {}


def moat_vertex(i, j, y):
    if (i, j, y) not in windex:
        windex[(i, j, y)] = water.add_vertex([-WORLD / 2 + i * cell, y, -WORLD / 2 + j * cell])
    return windex[(i, j, y)]


for i, j in sorted(wet):
    top, bot = MOAT_WATER, MOAT_Y - 0.25
    water.add_face([moat_vertex(i, j, top), moat_vertex(i, j + 1, top), moat_vertex(i + 1, j + 1, top), moat_vertex(i + 1, j, top)], WATER)
    water.add_face([moat_vertex(i, j, bot), moat_vertex(i + 1, j, bot), moat_vertex(i + 1, j + 1, bot), moat_vertex(i, j + 1, bot)], WATER)
    for (di, dj), (a, b) in (((-1, 0), ((i, j), (i, j + 1))), ((1, 0), ((i + 1, j + 1), (i + 1, j))),
                             ((0, -1), ((i + 1, j), (i, j))), ((0, 1), ((i, j + 1), (i + 1, j + 1)))):
        if (i + di, j + dj) not in wet:                # a side where the water ends
            water.add_face([moat_vertex(a[0], a[1], bot), moat_vertex(b[0], b[1], bot),
                            moat_vertex(b[0], b[1], top), moat_vertex(a[0], a[1], top)], WATER)
add.mesh(add.fix_normals(water))
water, windex, wet = None, None, None
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
while i < count(900):                                  # fish wherever the water is deep enough, 0.6 to 1.3 m long
    x, z = add.uniform(-W_EDGE + 2, W_EDGE - 2), add.uniform(-W_EDGE + 2, W_EDGE - 2)
    floor = ground(x, z)
    if floor > WATER_Y - 1.4:
        continue
    fish([x, add.uniform(floor + 0.5, WATER_Y - 0.5), z], add.atan2(x, z) + add.pi / 2 + add.uniform(-0.7, 0.7),
         add.choice([P["orange"], P["steel"], P["gold"], P["blue"]]), 0.45 * add.uniform(0.6, 1.3))
    i += 1
flush("fish", clean=False)
lo, hi = 0.0, 1.0                                      # how far down the slope of ground() the water starts
for k in range(40):
    T_SHORE = (lo + hi) / 2
    lo, hi = (T_SHORE, hi) if PLATEAU - (PLATEAU - 1.0) * T_SHORE * T_SHORE * (3 - 2 * T_SHORE) > WATER_Y else (lo, T_SHORE)


def shore_r(a):
    """How far out from the centre the shore is in the direction ``a`` --
    where the slope of ground() goes under the water: 88.7 on the gentle
    side, 69.9 under the cliff."""
    return 58 + T_SHORE * add.lerp(36.0, 14.0, add.clamp((-add.cos(a) - 0.55) / 0.3))


BOAT_DEGS = (44, 78, 104, 248, 283, 318)                # where rowing boats are tied up along the shore


def by_jetty(x, z, margin=0.5):
    """By the harbour -- the end of the road, the wharf, the ships moored to
    it -- or by one of the rowing boats on the shore (plus ``margin``)?"""
    u, v = x * DOCK_C + z * DOCK_S, -x * DOCK_S + z * DOCK_C
    if DOCK_U0 - 6 - margin < u < DOCK_U1 + 8 + margin and abs(v) < 13 + margin:
        return True
    for deg in BOAT_DEGS:
        a = deg * add.pi / 180
        r = shore_r(a) + 1.9
        if (x - r * add.cos(a)) ** 2 + (z - r * add.sin(a)) ** 2 < (3.2 + margin) ** 2:
            return True
    return False


for i in range(count(800)):                            # reeds in the shallows, the same way out from the
    a, r = add.uniform(0, 2 * add.pi), add.uniform(93, 98)   # shore all round -- the shore is no circle:
    r += shore_r(a) - shore_r(0)                       # under the cliff they stand closer in
    x, z = r * add.cos(a), r * add.sin(a)
    tops = [add.uniform(1, 2.2) for j in range(3)]
    if by_jetty(x, z):
        continue
    for j in range(3):
        add.cylinder([x + j * 0.2, ground(x, z), z], [x + j * 0.25, WATER_Y + tops[j], z + 0.1],
                     0.04, 6, P["leaf_dark"])
for i in range(count(400)):                            # lily pads, floating on the surface, likewise
    a, r = add.uniform(0, 2 * add.pi), add.uniform(94, 102)
    r += shore_r(a) - shore_r(0)
    x, z = r * add.cos(a), r * add.sin(a)
    size = add.uniform(0.3, 0.6)
    if by_jetty(x, z, size):
        continue
    add.cylinder([x, ripple(x, z) + 0.02, z], [x, ripple(x, z) + 0.06, z], size, 16, P["leaf"])
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


# the road from the gate to the harbour, paved: a bed of stone along ROAD, fieldstones set close in rows across it, a
# kerb of stones on the side of the hill and a low wall of stones on the side where the hill falls away; the ground is
# cut and banked to it (see ground())
ROAD_LEN = [0.0]
for k in range(1, len(ROAD)):
    ROAD_LEN.append(ROAD_LEN[-1] + add.sqrt((ROAD[k][0] - ROAD[k - 1][0]) ** 2 + (ROAD[k][1] - ROAD[k - 1][1]) ** 2))
ROAD_T = [(0.0, 1.0)]                                  # the way the road goes at each point: off the bridge straight,
for k in range(1, len(ROAD)):                          # then along the line through its neighbours
    a, b = ROAD[k - 1], ROAD[min(len(ROAD) - 1, k + 1)]
    d = add.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)
    ROAD_T.append(((b[0] - a[0]) / d, (b[1] - a[1]) / d))


def road(u, v):
    """The point at ``u`` (0 at the drawbridge .. 1 at the wharf) along the
    road and ``v`` (0 .. 1) across it, on its surface -- level across."""
    s_ = u * ROAD_LEN[-1]
    k = min(len(ROAD) - 2, max(0, next((i for i in range(len(ROAD) - 1) if ROAD_LEN[i + 1] >= s_), len(ROAD) - 2)))
    t = (s_ - ROAD_LEN[k]) / max(1e-9, ROAD_LEN[k + 1] - ROAD_LEN[k])
    (x0, z0, y0), (x1, z1, y1) = ROAD[k], ROAD[k + 1]
    tx, tz = ROAD_T[k][0] + (ROAD_T[k + 1][0] - ROAD_T[k][0]) * t, ROAD_T[k][1] + (ROAD_T[k + 1][1] - ROAD_T[k][1]) * t
    L = add.sqrt(tx * tx + tz * tz)
    x, z = x0 + (x1 - x0) * t + (-tz / L) * (v - 0.5) * 2 * ROAD_W, z0 + (z1 - z0) * t + (tx / L) * (v - 0.5) * 2 * ROAD_W
    return [x, y0 + (y1 - y0) * t + 0.12, z]


def on_road(x, z, margin=0.6):
    """Is (x, z) on the road to the harbour (its paved strip plus
    ``margin``), on the drawbridge, or on the landing before the gate?"""
    if abs(x) < 5.5 + margin and 50 < z < MOAT[3] + 1.5:
        return True
    q = road_at(x, z)
    return q is not None and q[0] < ROAD_W + margin


add.parametric(lambda u, v: [road(u, v)[k] - (0.125 if k == 1 else 0.0) for k in range(3)], 0, 1, int(ROAD_LEN[-1] * 2), 0, 1, 6, P["stone_dark"],
               thickness=0.25)                         # the bed: a slab whose top is the road's surface
FIELD = [shade_of("stone_dark", 0), shade_of("stone_dark", 1), shade_of("stone_dark", 2), shade_of("stone", 0), shade_of("stone", 2),
         P["rock"], P["granite"], P["granite"], P["earth_light"], P["spire"]]            # fieldstones: grey, pink, brown


def fieldstone(at, r, seed, squash=0.6):
    """A rounded fieldstone of radius ``r`` (squashed flat) at ``at``."""
    M = add.stretch(PEBBLE, [r * (1.0 + 0.3 * hash2(seed, 1, 81)), r * squash, r], (0, 0, 0))
    add.mesh(add.move(add.rotateY(add.color(M, FIELD[int(hash2(seed, 2, 81) * 10) % 10]), hash2(seed, 3, 81) * 6.28), at))


laid = {}                                              # the cobbles: fieldstones of all colours and sizes, worn flat, set
n = 0                                                  # close in rows across the road -- and none on another where the rows
for i in range(int(ROAD_LEN[-1] / 0.36)):              # fan out on a bend
    u = (i + 0.5) * 0.36 / ROAD_LEN[-1]
    for j in range(11 - i % 2):
        off = -1.98 + 0.372 * (j + 0.5 * (i % 2))                                # between the kerb and the parapet
        if hash2(i, j, 71) > max(DENSITY, 0.35):
            continue
        q = road(u, 0.5 + off / (2 * ROAD_W))
        q = [q[0] + (hash2(i, j, 72) - 0.5) * 0.06, q[1], q[2] + (hash2(i, j, 73) - 0.5) * 0.06]
        size = 1.0 + 0.2 * hash2(i, j, 76)
        cx, cz = int(q[0] // 0.5), int(q[2] // 0.5)
        if any((q[0] - p_[0]) ** 2 + (q[2] - p_[1]) ** 2 < (0.14 * (size + p_[2])) ** 2
               for di in (-1, 0, 1) for dj in (-1, 0, 1) for p_ in laid.get((cx + di, cz + dj), ())):
            continue
        laid.setdefault((cx, cz), []).append((q[0], q[2], size))
        stone = add.stretch(COBBLES[int(hash2(i, j, 74) * 6) % 6], [size, 0.6 + 0.35 * hash2(i, j, 77), size], (0, 0, 0))
        add.mesh(add.move(add.rotateY(add.color(stone, FIELD[int(hash2(i, j, 78) * 10) % 10]), hash2(i, j, 75) * 6.28),
                          [q[0], q[1] - 0.03, q[2]]))
        n += 1


def along(v, s0, step):
    """Points on the road's surface at ``v`` across it, every ``step``
    metres along that line from ``s0`` metres along the road on."""
    pts = [road(min(1.0, (s0 + i * 0.05) / ROAD_LEN[-1]), v) for i in range(int((ROAD_LEN[-1] - s0) / 0.05) + 1)]
    out_, walk = [pts[0]], 0.0
    for i in range(1, len(pts)):
        walk += add.sqrt((pts[i][0] - pts[i - 1][0]) ** 2 + (pts[i][2] - pts[i - 1][2]) ** 2)
        if walk >= step:
            out_.append(pts[i])
            walk = 0.0
    return out_


for k, q in enumerate(along(0.5 - (ROAD_W - 0.2) / (2 * ROAD_W), ROAD_LEN[4] + 0.5, 0.4)):   # the kerb on the hill side:
    fieldstone([q[0], q[1] - 0.04, q[2]], 0.17 + 0.03 * hash2(k, 5, 82), k, 0.75)            # a row of stones half sunk
pts = along(0.5 + (ROAD_W - 0.27) / (2 * ROAD_W), 0.3, 0.6)      # on the side where the hill falls away, a parapet: a low
for k in range(len(pts) - 1):                                     # wall of fieldstones set in mortar, knee high
    A, B = pts[k], pts[k + 1]
    d = vunit([B[0] - A[0], 0.0, B[2] - A[2]])
    add.beam([A[0], A[1] + 0.15, A[2]], [B[0], B[1] + 0.15, B[2]], 0.54, 0.6, P["mortar"])
    for f in (0.25, 0.75):
        c = [A[j] + (B[j] - A[j]) * f for j in range(3)]
        fieldstone([c[0], c[1] + 0.47, c[2]], 0.22 + 0.04 * hash2(k, int(f * 4), 83), k * 4 + int(f * 4), 0.5)   # on top
        for sd in (-1, 1):                                                                                     # and in its faces
            fieldstone([c[0] + sd * d[2] * 0.25, c[1] + 0.22, c[2] - sd * d[0] * 0.25], 0.15 + 0.03 * hash2(k, sd, 84),
                       k * 8 + int(f * 4) + sd + 3, 0.7)
flush("the road to the harbour (%d cobbles)" % n)


# the moat's stonework.  Its bank: rough blocks of fieldstone laid in courses along the edge of the water from below
# its floor, each course set back a little, under big flat coping stones a hand over the grass.  Under each end of
# the drawbridge a seat of dressed stones that its planks rest on.  The landing before the gate: a pier of masonry
# with walls of the same blocks and a kerb round its edge.
COURSES = 9
COURSE_H = (G - 0.28 - (MOAT_Y - 0.2)) / COURSES        # from under the floor up to the seats of the bridge


def _crossing(a, b, keep):
    """The point between ``a`` (where ``keep`` fails) and ``b`` (where it holds) where it starts to hold."""
    for i in range(30):
        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        a, b = (a, m) if keep(*m) else (m, b)
    return b


def runs(points, keep):
    """The runs of the polyline ``points`` where ``keep(x, z)`` holds, cut off where it stops or starts to hold."""
    out, run = [], []
    for k, p in enumerate(points):
        if keep(*p):
            if not run and k > 0:
                run.append(_crossing(points[k - 1], p, keep))
            run.append(p)
        elif run:
            out.append(run + [_crossing(p, points[k - 1], keep)])
            run = []
    return out + ([run] if run else [])


def course(points, y0, y1, front, depth, seed, colours, lengths=(0.55, 1.05), gap=0.05, rough=0.03, stagger=False):
    """A course of stone blocks from ``y0`` to ``y1`` along the polyline ``points`` (in XZ), end to end with joints of
    ``gap``: their faces ``front`` out from the line to its left -- the water's side -- and ``depth`` deep, a little
    rough (in and out, up and down by ``rough``)."""
    acc = [0.0]
    for k in range(1, len(points)):
        acc.append(acc[-1] + add.sqrt((points[k][0] - points[k - 1][0]) ** 2 + (points[k][1] - points[k - 1][1]) ** 2))

    def at(s):
        k = max(0, min(len(points) - 2, next((i for i in range(len(points) - 1) if acc[i + 1] >= s), len(points) - 2)))
        t = (s - acc[k]) / max(1e-9, acc[k + 1] - acc[k])
        return (points[k][0] + (points[k + 1][0] - points[k][0]) * t, points[k][1] + (points[k + 1][1] - points[k][1]) * t)

    s, k = (-(lengths[0] + lengths[1]) / 4 if stagger else 0.0), 0
    while s < acc[-1] - 0.15:
        L = lengths[0] + (lengths[1] - lengths[0]) * hash2(seed, k, 91)
        a, b = max(s, 0.0), min(s + L - gap, acc[-1])
        if b - a >= 0.15:
            A, B = at(a), at(b)
            d = add.sqrt((B[0] - A[0]) ** 2 + (B[1] - A[1]) ** 2)
            nx, nz = (B[1] - A[1]) / d, -(B[0] - A[0]) / d                   # towards the water
            f = front + (hash2(seed, k, 92) - 0.5) * 2 * rough
            quad = [(A[0] + nx * f, A[1] + nz * f), (B[0] + nx * f, B[1] + nz * f),
                    (B[0] + nx * (f - depth), B[1] + nz * (f - depth)), (A[0] + nx * (f - depth), A[1] + nz * (f - depth))]
            add.mesh(solid(quad, y0 + gap / 2 + (hash2(seed, k, 93) - 0.5) * rough, y1 - gap / 2 + (hash2(seed, k, 94) - 0.5) * rough,
                           colours[int(hash2(seed, k, 95) * len(colours)) % len(colours)]))
        s += L
        k += 1


def inset(poly, d, keep=()):
    """The convex outline ``poly`` (counter-clockwise in XZ) with its edges moved in by ``d`` -- all but the ones
    numbered in ``keep``."""
    out = list(poly)
    for k in range(len(poly)):
        if k not in keep:
            (x0, z0), (x1, z1) = poly[k], poly[(k + 1) % len(poly)]
            L = add.sqrt((x1 - x0) ** 2 + (z1 - z0) ** 2)
            a, b = (z1 - z0) / L, -(x1 - x0) / L                                  # its outward normal
            out = clip_half(out, a, b, a * x0 + b * z0 - d)
    return out


BANK_STONE = FIELD[:6] + [P["granite"], shade_of("stone", 1)]
COPING = [shade_of("stone_dark", 0), shade_of("stone_dark", 1), shade_of("stone_dark", 2), P["rock"], P["granite"]]
not_seat = lambda x, z: not (abs(x) < BRIDGE_X and z > 62.0)                     # the far bank but for the bridge's seat
for j in range(COURSES):                                                          # the bank, battered 1 in 14
    y0 = MOAT_Y - 0.2 + j * COURSE_H
    for r, piece in enumerate(runs(MOAT_EDGE, not_seat) if j == COURSES - 1 else [MOAT_EDGE]):
        course(piece, y0, y0 + COURSE_H, (COURSES - 1 - j) * 0.035, 0.6, 100 * j + r, BANK_STONE, stagger=j % 2 == 1)
for r, piece in enumerate(runs(MOAT_EDGE, lambda x, z: not (abs(x) < BRIDGE_X + 0.05 and z > 62.0))):
    course(piece, G - 0.28, G + 0.15, 0.03, 0.9, 1000 + r, COPING, lengths=(0.8, 1.3), gap=0.04, rough=0.02)
QUAY = [(6.6, 53.6)] + LANDING[2:-1] + [LANDING[-1], (-6.6, 53.6)]              # round the landing, from the gate tower
QUAY = [(a[0] + (b[0] - a[0]) * t / 10.0, a[1] + (b[1] - a[1]) * t / 10.0)        # (every 10th of a side a point, where the
        for a, b in zip(QUAY, QUAY[1:]) for t in range(10)] + [QUAY[-1]]           # courses are cut for the bridge's seat)
not_notch = lambda x, z: not (abs(x) < BRIDGE_X and z > BRIDGE_Z0 + 0.5)          # on the east to the one on the west
for j in range(COURSES):                                                          # the landing's walls, upright
    y0 = MOAT_Y - 0.2 + j * COURSE_H
    for r, piece in enumerate(runs(QUAY, not_notch) if j == COURSES - 1 else [QUAY]):
        course(piece, y0, y0 + COURSE_H, 0.0, 0.6, 2000 + 100 * j + r, BANK_STONE, stagger=j % 2 == 1)
for r, piece in enumerate(runs(QUAY, lambda x, z: not (abs(x) < BRIDGE_X + 0.05 and z > BRIDGE_Z0 + 0.5))):
    course(piece, G - 0.28, G + 0.15, 0.02, 0.55, 3000 + r, COPING, lengths=(0.7, 1.1), gap=0.04, rough=0.02)
CORE = inset(LANDING, 0.3, keep=(0,))                                             # the pier's core, and its top: the
add.mesh(solid(CORE, MOAT_Y - 0.25, G - 0.28, P["mortar"]))                       # bed of the paving, up to the hinge
HINGE_GAP = BRIDGE_Z0 - HINGE_R - 0.005                                           # of the bridge and beside its deck
add.mesh(solid(clip_half(CORE, 0, 1, HINGE_GAP), G - 0.28, G + 0.02, P["mortar"]))
for sx in (-1, 1):
    add.mesh(solid(clip_half(clip_half(CORE, 0, -1, -HINGE_GAP), -sx, 0, -DECK - 0.005), G - 0.28, G + 0.02, P["mortar"]))
for z0, z1, top in ((BRIDGE_Z0 + HINGE_R + 0.005, 56.0, G - 0.052),                # the seats: three dressed stones each,
                    (MOAT[3], BRIDGE_Z1 + 0.05, G - 0.08)):                        # right up under the bridge -- under the
    y0 = G - 0.28 - (COURSE_H - 0.025)                                            # leaf of its hinge, and under the iron
    for i in range(3):                                                            # bar across its far end
        x0 = -BRIDGE_X + i * 2 * BRIDGE_X / 3
        add.cuboid([x0 + BRIDGE_X / 3, (y0 + top) / 2, (z0 + z1) / 2], [2 * BRIDGE_X / 3 - 0.04, top - y0, z1 - z0],
                   shade_of("stone", i + (z0 > 60)))
flush("the moat's stonework")


PIRANHA = [(-0.62, 0.035, 0.075, -0.065), (-0.58, 0.04, 0.08, -0.07), (-0.5, 0.06, 0.12, -0.11), (-0.4, 0.1, 0.22, -0.21),
           (-0.28, 0.135, 0.33, -0.32), (-0.14, 0.16, 0.41, -0.4), (0.0, 0.17, 0.44, -0.42), (0.14, 0.17, 0.43, -0.4),
           (0.26, 0.16, 0.39, -0.32), (0.36, 0.14, 0.33, -0.2), (0.45, 0.115, 0.25, -0.12), (0.52, 0.09, 0.17, -0.09),
           (0.58, 0.06, 0.09, -0.07), (0.62, 0.025, 0.02, -0.05)]   # (x, half-width, top, bottom): a piranha, tail to snout
PIRANHA_JAW = [(0.28, 0.12, -0.08, -0.33), (0.36, 0.115, -0.085, -0.27), (0.44, 0.1, -0.09, -0.22), (0.52, 0.08, -0.095, -0.17),
               (0.58, 0.055, -0.1, -0.14), (0.64, 0.025, -0.105, -0.125)]          # and its lower jaw, hinge to chin


def section(table, x):
    """(half-width, top, bottom) of a table of sections at ``x``, between its rows."""
    for (x0, *a), (x1, *b) in zip(table, table[1:]):
        if x <= x1:
            t = add.clamp((x - x0) / (x1 - x0))
            return [a[k] + (b[k] - a[k]) * t for k in range(3)]
    return list(table[-1][1:])


def fish_loft(table, n, m, e=1.0):
    """A body lofted through the sections of ``table``: ``n`` rings of ``m``
    points, each a rounded oval (exponent ``e``: 1 an ellipse, less a box)."""
    rings = []
    for i in range(n):
        x = table[0][0] + (table[-1][0] - table[0][0]) * i / (n - 1.0)
        w, top, bot = section(table, x)
        c, h = (top + bot) / 2, (top - bot) / 2
        rings.append([[x, c + h * abs(add.cos(2 * add.pi * j / m)) ** e * (1 if add.cos(2 * add.pi * j / m) >= 0 else -1),
                       w * abs(add.sin(2 * add.pi * j / m)) ** e * (1 if add.sin(2 * add.pi * j / m) >= 0 else -1)] for j in range(m)])
    return add.make(add.loft, rings, P["steel"])


def on_side(table, x, y, out=0.0):
    """How far out to the side the surface of a fish of ``table`` is at (x, y), plus ``out``."""
    w, top, bot = section(table, x)
    c, h = (top + bot) / 2, (top - bot) / 2
    return w * add.sqrt(max(0.0, 1 - ((y - c) / h) ** 2)) + out


def tooth_row(cx, rx, rz, a_max, n, h, colour, rim_y):
    """A row of ``n`` sharp teeth set edge to edge round the arc of a jaw
    (centre ``cx``, radii ``rx`` forwards and ``rz`` across, between the
    angles -a_max and a_max), standing on the rim at the height
    ``rim_y(x, z)``: each a thin triangular blade, its point ``h`` up
    (h < 0: down) and leaning a little into the mouth."""
    rim = lambda a: [cx + rx * add.cos(a), 0.0, rz * add.sin(a)]
    for i in range(n):
        a0, a1 = -a_max + 2 * a_max * i / n, -a_max + 2 * a_max * (i + 1) / n
        p, q, m = rim(a0), rim(a1), rim((a0 + a1) / 2)
        for v in (p, q, m):
            v[1] = rim_y(v[0], v[2])
        nx, nz = rz * add.cos((a0 + a1) / 2), rx * add.sin((a0 + a1) / 2)      # the rim's outward normal
        L = add.sqrt(nx * nx + nz * nz)
        nx, nz = nx / L, nz / L
        tip = [m[0] - 0.012 * nx, m[1] + h, m[2] - 0.012 * nz]
        front = [[v[0] + 0.005 * nx, v[1], v[2] + 0.005 * nz] for v in (p, q, tip)]
        back = [[v[0] - 0.005 * nx, v[1], v[2] - 0.005 * nz] for v in (p, q, tip)]
        M = add.Mesh()
        M.add_polygon(front, colour)
        M.add_polygon(back[::-1], colour)
        for j in range(3):
            M.add_polygon([back[j], back[(j + 1) % 3], front[(j + 1) % 3], front[j]], colour)
        add.mesh(add.fix_normals(M))


def piranha(at, facing, s=1.0, pitch=0.0, gape=0.3):
    """A red-bellied piranha: the deep, flat body of its kind, lofted
    through its sections -- a blunt head, the back rising to the dorsal
    fin, a deep belly, a slender tail stalk -- dark grey along the back,
    silver on the flanks, red on the belly and throat;
    the edge of the gill cover, big golden eyes with a glint, nostrils.
    The lower jaw, hinged down by ``gape``, reaches a little past the
    upper; round the rims of both a close row of small, sharp, triangular
    teeth, edge to edge like a saw -- the upper ones longer, pointing
    down, the lower ones up -- round the dark red mouth.  Dorsal and
    adipose fins, red anal, pelvic and pectoral fins, a forked tail dark
    at its base.  It swims towards +x, its nose ``pitch`` up; ``s`` = 1 is
    1.5 m long."""
    add.push()

    def skin(q):
        w, top, bot = section(PIRANHA, q[0])
        t = (q[1] - (top + bot) / 2) / ((top - bot) / 2)                        # -1 the belly .. 1 the back
        if t < -0.3 - 0.3 * add.clamp((q[0] - 0.25) / 0.2):                     # red below, up to the throat,
            return P["red"]
        return P["iron"] if t > 0.55 else P["mail"] if t > 0.3 else P["steel"]   # silver sides, the back dark

    add.mesh(add.color_by(fish_loft(PIRANHA, 56, 36), skin))
    add.ellipsoid([0.46, -0.1, 0], [0.11, 0.045, 0.06], 6, P["meat"])                       # the mouth, dark red inside
    tooth_row(0.5, 0.11, 0.055, 1.35, 13, -0.075, P["bone"],                                # the upper teeth
              lambda x, z: (section(PIRANHA, x)[1] + section(PIRANHA, x)[2]) / 2 + 0.008
              - (section(PIRANHA, x)[1] - section(PIRANHA, x)[2]) / 2 * add.sqrt(max(0.0, 1 - (z / section(PIRANHA, x)[0]) ** 2)))
    add.push()                                                                               # the lower jaw and its teeth
    add.mesh(add.color_by(fish_loft(PIRANHA_JAW, 12, 20, 0.7), lambda q: P["iron"] if q[1] > section(PIRANHA_JAW, q[0])[1] - 0.012 else P["red"]))
    tooth_row(0.5, 0.12, 0.06, 1.35, 13, 0.05, P["bone"], lambda x, z: section(PIRANHA_JAW, x)[1] - 0.006)
    add.mesh(add.rotateZ(add.pop(), -gape, (0.3, -0.09, 0)))
    for sz in (-1, 1):
        ez = on_side(PIRANHA, 0.4, 0.12)
        add.sphere([0.4, 0.12, sz * (ez - 0.018)], 0.052, 5, P["gold"])                     # big golden eyes,
        add.sphere([0.412, 0.12, sz * (ez + 0.022)], 0.027, 4, P["black"])                  # black pupils,
        add.sphere([0.418, 0.134, sz * (ez + 0.038)], 0.007, 2, P["white"])                 # a glint
        add.sphere([0.54, 0.1, sz * on_side(PIRANHA, 0.54, 0.1)], 0.011, 2, P["black"])      # the nostrils
        gill = [(0.27, 0.3), (0.22, 0.16), (0.2, 0.0), (0.21, -0.15), (0.26, -0.28)]         # the edge of the gill cover
        add.polyline([[x, y, sz * on_side(PIRANHA, x, y, 0.004)] for x, y in gill], 0.007, 5, P["iron"])
        for profile, z0, colour in (([[0.2, -0.17], [0.03, -0.3], [0.09, -0.15]], on_side(PIRANHA, 0.12, -0.2, 0.008), P["orange"]),   # pectoral
                                    ([[0.08, -0.37], [-0.08, -0.5], [0.0, -0.36]], 0.05, P["orange"])):                               # pelvic
            add.mesh(add.make(add.prism, profile, 0.015, colour, (0, 0, sz * z0), (0, 0, 1)))
    for profile, colour, t in (([[0.08, 0.4], [-0.04, 0.63], [-0.16, 0.62], [-0.2, 0.38]], P["iron"], 0.02),      # dorsal fin,
                               ([[-0.44, 0.17], [-0.47, 0.25], [-0.53, 0.24], [-0.52, 0.13]], P["iron"], 0.02),   # adipose fin,
                               ([[-0.1, -0.38], [-0.42, -0.19], [-0.44, -0.3], [-0.2, -0.52]], P["red"], 0.02),   # anal fin
                               ([[-0.58, 0.07], [-0.72, 0.01], [-0.9, 0.36]], P["iron"], 0.03),                   # and the two
                               ([[-0.58, -0.07], [-0.9, -0.36], [-0.72, -0.01]], P["iron"], 0.03),                # lobes of the
                               ([[-0.6, -0.12], [-0.64, -0.13], [-0.64, 0.13], [-0.6, 0.12]], P["black"], 0.045)): # tail, dark at its base
        add.mesh(add.make(add.prism, profile, t, colour, (0, 0, 0), (0, 0, 1)))
    M = add.rotateZ(add.stretch(add.pop(), [s] * 3, (0, 0, 0)), pitch)
    add.mesh(add.move(add.rotateY(M, facing), at))


shoal = []                                             # piranhas in the moat, a shoal of them circling before the gate
k = 0                                                  # just under the surface, jaws open, none touching
while len(shoal) < count(30) and k < 5000:
    x, z = -11.0 + 22.0 * hash2(k, 1, 131), 54.5 + 9.5 * hash2(k, 2, 131)
    y, size = MOAT_WATER - 0.45 - 0.8 * hash2(k, 3, 131), 0.6 + 0.15 * hash2(k, 4, 131)
    k += 1
    if not in_moat_outline(x, z) or castle_depth(x, z) > -0.9 or landing_depth(x, z) > -0.8 or bank_gap(x, z) < 1.1:
        continue
    if any((x - q[0]) ** 2 + (y - q[1]) ** 2 + (z - q[2]) ** 2 < 1.1 ** 2 for q in shoal):
        continue
    d = add.atan2(z - 59.8, x) + add.pi / 2 + (hash2(k, 5, 131) - 0.5) * 1.2                  # round and round
    piranha([x, y, z], -d, size, (hash2(k, 6, 131) - 0.5) * 0.4, 0.18 + 0.15 * hash2(k, 7, 131))
    shoal.append((x, y, z))
for x, z, d, pitch in ((-3.7, 58.4, 0.3, 0.8), (3.9, 60.2, 2.7, -0.5), (6.8, 57.6, -2.2, 0.6),    # and six of them
                       (-9.6, 57.2, 1.75, 0.5), (-6.9, 58.8, 1.4, 0.35), (-11.4, 59.8, 2.0, 0.6)):  # leaping out of the
    y = MOAT_WATER + (0.6 if pitch > 0 else 0.4)                                                # water, jaws agape,
    piranha([x, y, z], -d, 0.75, pitch, 0.4)                                                    # rings where they
    add.torus([x - 0.45 * add.cos(d), MOAT_WATER + 0.01, z - 0.45 * add.sin(d)], 0.5, 0.035, 16, 4, P["white"])   # broke
    for j in range(6):                                                                          # the surface and
        a = j * 1.05 + d                                                                        # drops flying
        add.sphere([x + 0.55 * add.cos(a), MOAT_WATER + 0.12 + 0.15 * (j % 3), z + 0.55 * add.sin(a)], 0.04, 2, P["white"])
flush("piranhas in the moat (%d)" % len(shoal))


# the forest on the slopes: low-poly trees of the northern woods, each species by its shape -- spruces in drooping
# tiers, pines tall and bare with a flat crown, birches white and slender, oaks broad on thick limbs, elms like a
# vase, limes round
def forest_tree(at, h, kind, seed):
    """A tree ``h`` tall of the given species, its foot at ``at``."""
    x, y, z = at
    rnd = lambda j: hash2(seed, j, 41)
    blob = lambda c, r, st, col: add.mesh(add.stretch(add.make(add.sphere, c, r, 4, col), st, c))
    if kind == "spruce":                                                  # a dark cone of drooping tiers, a leader on top
        add.cylinder([x, y, z], [x, y + 0.95 * h, z], 0.035 * h, 6, P["trunk"])
        for j in range(7):
            f = j / 6.0
            base = y + 0.06 * h + f * 0.76 * h
            add.cone([x, base, z], [x, base + 0.22 * h, z], 0.33 * h * (1 - 0.86 * f), 8, (P["needles"], P["leaf_dark"])[j % 2])
        add.cone([x, y + 0.84 * h, z], [x, y + 1.03 * h, z], 0.05 * h, 6, P["needles"])
    elif kind == "pine":                                                  # a tall bare trunk, red above, a flat crown
        lx, lz = (rnd(1) - 0.5) * 0.16 * h, (rnd(2) - 0.5) * 0.16 * h
        mid, top = [x + lx * 0.6, y + 0.55 * h, z + lz * 0.6], [x + lx, y + 0.9 * h, z + lz]
        add.cylinder([x, y, z], mid, 0.045 * h, 7, P["trunk"])
        add.cylinder(mid, top, 0.03 * h, 7, P["bark_red"])
        for j in range(3):                                                # dead branch stubs
            a = rnd(10 + j) * 6.28
            p0 = [x + lx * 0.5, y + (0.45 + 0.08 * j) * h, z + lz * 0.5]
            add.cylinder(p0, [p0[0] + 0.12 * h * add.cos(a), p0[1] + 0.03 * h, p0[2] + 0.12 * h * add.sin(a)], 0.008 * h, 4, P["wood_dark"])
        for j in range(5):
            a = rnd(20 + j) * 6.28
            d = 0.1 * h * (0.4 + rnd(30 + j))
            c = [top[0] + d * add.cos(a), top[1] - 0.12 * h * rnd(40 + j), top[2] + d * add.sin(a)]
            blob(c, (0.13 + 0.05 * rnd(50 + j)) * h, [1.0, 0.45, 1.0], (P["needles"], P["leaf_dark"])[j % 2])
    elif kind == "birch":                                                 # white stems with black marks, an oval crown
        stems = 2 if seed % 3 == 0 else 1
        for k in range(stems):
            a = rnd(60 + k) * 6.28
            lean = 0.06 * h * (1 + k)
            top = [x + lean * add.cos(a), y + 0.85 * h, z + lean * add.sin(a)]
            add.cylinder([x, y, z], top, 0.026 * h, 6, P["white"])
            for j in range(4):
                t = 0.15 + 0.17 * j + 0.05 * rnd(70 + j + 5 * k)
                q = [x + (top[0] - x) * t, y + (top[1] - y) * t, z + (top[2] - z) * t]
                add.cylinder([q[0], q[1], q[2]], [q[0], q[1] + 0.025 * h, q[2]], 0.0275 * h, 6, P["black"])
            for j in range(5):
                t = 0.52 + 0.1 * j
                c = [x + (top[0] - x) * t + (rnd(80 + j + 7 * k) - 0.5) * 0.12 * h, y + (top[1] - y) * t + 0.06 * h,
                     z + (top[2] - z) * t + (rnd(90 + j + 7 * k) - 0.5) * 0.12 * h]
                blob(c, (0.1 + 0.04 * rnd(95 + j)) * h, [0.85, 1.25, 0.85], (P["birch_leaf"], P["grass"])[j % 2])
    elif kind == "oak":                                                   # a thick trunk, crooked limbs, a broad crown
        fork = [x, y + 0.38 * h, z]
        add.cylinder([x, y, z], fork, 0.085 * h, 8, P["trunk"])
        ends = []
        for j in range(4):
            a = (j + rnd(100 + j) * 0.6) * 1.57
            e = [x + 0.3 * h * add.cos(a), y + (0.62 + 0.08 * rnd(110 + j)) * h, z + 0.3 * h * add.sin(a)]
            add.cylinder(fork, e, 0.035 * h, 6, P["trunk"])
            ends.append(e)
        for j, e in enumerate(ends + [[x, y + 0.8 * h, z]]):
            blob([e[0], e[1] + 0.06 * h, e[2]], (0.22 + 0.05 * rnd(120 + j)) * h, [1.1, 0.8, 1.1], (P["oak_leaf"], P["leaf_dark"], P["leaf"])[j % 3])
        for j in range(4):
            a = rnd(130 + j) * 6.28
            blob([x + 0.2 * h * add.cos(a), y + 0.88 * h, z + 0.2 * h * add.sin(a)], 0.17 * h, [1.1, 0.8, 1.1], P["oak_leaf"])
    elif kind == "elm":                                                   # stems rising apart like a vase, a wide dome
        fork = [x, y + 0.32 * h, z]
        add.cylinder([x, y, z], fork, 0.05 * h, 7, P["rock"])
        for j in range(3):
            a = (j + rnd(140 + j) * 0.5) * 2.09
            e = [x + 0.24 * h * add.cos(a), y + 0.74 * h, z + 0.24 * h * add.sin(a)]
            add.cylinder(fork, e, 0.028 * h, 6, P["rock"])
            blob([e[0], e[1] + 0.08 * h, e[2]], 0.2 * h, [1.15, 0.7, 1.15], (P["leaf"], P["grass"], P["leaf_dark"])[j])
        blob([x, y + 0.9 * h, z], 0.22 * h, [1.2, 0.6, 1.2], P["leaf"])
    else:                                                                 # a lime: a round, dense crown
        add.cylinder([x, y, z], [x, y + 0.45 * h, z], 0.05 * h, 8, P["trunk"])
        for j in range(7):
            u, v, w = rnd(150 + j) - 0.5, rnd(160 + j) - 0.5, rnd(170 + j) - 0.5
            c = [x + 0.32 * h * u, y + 0.62 * h + 0.22 * h * v, z + 0.32 * h * w]
            blob(c, h * (0.16 + 0.1 * rnd(180 + j)), [1.0, 0.85, 1.0], (P["leaf"], P["leaf_dark"], P["grass"])[j % 3])
        add.sphere([x, y + 0.8 * h, z], 0.2 * h, 4, P["leaf"])


def species(x, z, n):
    """Which tree grows at (x, z): pines and oaks up on the dry brow of the
    hill, spruces, birches, elms and limes lower down, birches and elms by
    the water."""
    r = add.sqrt(x * x + z * z)
    h = hash2(n, 3, 43)
    if r < 69:
        return ("pine", "pine", "oak", "oak", "birch", "lime")[int(h * 6)]
    if r < 81:
        return ("spruce", "spruce", "birch", "oak", "elm", "lime", "pine")[int(h * 7)]
    return ("birch", "birch", "elm", "spruce", "spruce", "lime")[int(h * 6)]


HEIGHT = {"spruce": (6, 11), "pine": (8, 12), "birch": (6, 10), "oak": (6, 9), "elm": (8, 12), "lime": (5, 9)}


add.seed(11)
trees = 0
TREES = []                                             # where they stand, and how tall: the mushrooms grow among them
while trees < count(450):
    a, r = add.uniform(0, 2 * add.pi), add.uniform(60, 90)
    x, z = r * add.cos(a), r * add.sin(a)
    if on_road(x, z, 5.0) or by_terrace(x, z, 3.0) or by_jetty(x, z, 3.0):   # keep the road, the terrace, the moat
        continue                                                              # and the harbour clear
    y = ground(x, z)
    if y < WATER_Y + 1.5:
        continue
    kind = species(x, z, trees)
    h = add.uniform(*HEIGHT[kind])
    forest_tree([x, y - 0.2, z], h, kind, trees)
    TREES.append((x, z, h))
    trees += 1
    if trees % 150 == 0:
        flush("forest (%d trees)" % trees, clean=False)
flush("forest", clean=False)


def mushroom(at, kind, s=1.0):
    """A mushroom standing on the ground at ``at``: a fly agaric (a red cap
    with white warts), a cep (a fat pale stem, a brown cap) or a
    chanterelle (a little orange funnel)."""
    x, y, z = at
    if kind == "agaric":
        add.cylinder([x, y - 0.03, z], [x, y + 0.2 * s, z], 0.025 * s, 8, P["white"])
        add.mesh(add.move(add.stretch(add.make(add.hemisphere, [0, 0, 0], 0.11 * s, 4, P["red"]), [1.0, 0.65, 1.0], (0, 0, 0)),
                          [x, y + 0.19 * s, z]))
        for j in range(5):                                                    # the white warts
            a, t = j * 2.4, 0.3 + 0.45 * hash2(j, int(x * 10), 31)
            add.cuboid([x + 0.11 * s * t * add.cos(a), y + 0.19 * s + 0.0715 * s * add.sqrt(1 - t * t),
                        z + 0.11 * s * t * add.sin(a)], [0.022 * s, 0.014 * s, 0.022 * s], P["white"])
    elif kind == "cep":
        lathe([[0.0, -0.03], [0.04, -0.03], [0.05, 0.06], [0.035, 0.15], [0.0, 0.15]], [x, y, z], 10, P["linen"], s)
        add.mesh(add.move(add.stretch(add.make(add.hemisphere, [0, 0, 0], 0.1 * s, 4, P["bread"]), [1.0, 0.7, 1.0], (0, 0, 0)),
                          [x, y + 0.14 * s, z]))
    else:
        lathe([[0.0, -0.02], [0.015, -0.02], [0.02, 0.06], [0.06, 0.1], [0.05, 0.11], [0.0, 0.085]], [x, y, z], 10, P["orange"], s)


add.seed(12)                                           # mushrooms in the forest: fewer than the fish,
mushrooms = 0                                          # in little groups round the trees
while mushrooms < count(300):
    tx, tz, th = TREES[int(add.random() * len(TREES)) % len(TREES)]
    a, d = add.uniform(0, 2 * add.pi), add.uniform(0.7, 0.8 + 0.25 * th)
    x, z = tx + d * add.cos(a), tz + d * add.sin(a)
    kind = add.choice(["agaric", "cep", "cep", "chanterelle"])
    group = [(x + add.uniform(-0.3, 0.3), z + add.uniform(-0.3, 0.3), add.uniform(0.7, 1.3)) for j in range(3)]
    if on_road(x, z, 3.0) or by_terrace(x, z, 2.0) or by_jetty(x, z, 2.0) or ground(x, z) < WATER_Y + 1.2:
        continue
    for gx, gz, gs in group[:1 + mushrooms % 3]:
        mushroom([gx, ground(gx, gz), gz], kind, gs * (1.6 if kind == "chanterelle" else 1.3))
    mushrooms += 1
flush("mushrooms (%d)" % mushrooms, clean=False)

# tufts of grass on the slopes and the meadow (thin solid blades)
add.seed(13)
n = 0
while n < count(150000):
    a, r = add.uniform(0, 2 * add.pi), 50 + 42 * add.sqrt(add.random())
    x, z = r * add.cos(a), r * add.sin(a)
    y = ground(x, z)
    if y < WATER_Y + 1.0 or octagon_r(x, z) < 51.5 or on_road(x, z) or near_corner(x, z, 0.3) \
            or in_moat(x, z) or by_jetty(x, z, 0.0):
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


def along(a, b, s):
    """The point ``s`` units from ``a`` towards ``b`` (in XZ)."""
    L, d, n = outward(a, b)
    return [a[0] + d[0] * s, 0, a[2] + d[2] * s]


for k in range(8):
    a, b = CORNERS[k], CORNERS[(k + 1) % 8]
    if k == 1:                                         # the south wall, in two halves, to the gate towers -- standing
        for y0, y1, top in ((MOAT_Y - 0.5, G - 1, False), (G - 1, WALL_TOP, True)):   # in the moat, from its floor
            wall_segment(along(a, b, TOWER_R - 0.5), [GATE_X - 0.5, 0, 50.0], y0, y1, walk=top, inner=top)
            wall_segment([-GATE_X + 0.5, 0, 50.0], along(b, a, TOWER_R - 0.5), y0, y1, walk=top, inner=top)
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
    if k in (1, 2):                                    # the two towers that stand in the moat go down to its floor,
        add.pipe([c[0], MOAT_Y - 0.5, c[2]], [c[0], G - 1, c[2]], TOWER_R, TOWER_R - 1.0, k_(24), P["mortar"])
        arc = (80, 200) if k == 1 else (-20, 100)      # with stones on the side of the water
        stone_ring(c[0], c[2], TOWER_R, MOAT_Y, G - 0.5, arc=(arc[0] * add.pi / 180, arc[1] * add.pi / 180))
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


LIFE = 1.15                                            # knights and horses are built life-size and scaled by this, like
                                                       # the archers: all the castle's people are one size


def _at(a, d, t):
    """The point ``t`` units from ``a`` along the direction ``d``."""
    return [a[0] + d[0] * t, a[1] + d[1] * t, a[2] + d[2] * t]


def joint(a, c, l1, l2, pole):
    """The middle joint (elbow, knee) of a limb from ``a`` to ``c`` whose two
    bones are ``l1`` and ``l2`` long, bent towards the direction ``pole``."""
    d = vsub(c, a)
    L = min(vlen(d), l1 + l2 - 1e-4)
    u = vunit(d)
    x = (l1 * l1 - l2 * l2 + L * L) / (2 * L)
    h = add.sqrt(max(0.0, l1 * l1 - x * x))
    k = sum(pole[i] * u[i] for i in range(3))
    p = vunit([pole[i] - u[i] * k for i in range(3)])
    return [a[i] + u[i] * x + p[i] * h for i in range(3)]


def ramp(values):
    """A function of t = 0..1 running straight through ``values``, evenly spaced."""
    n = len(values) - 1

    def f(t):
        i = min(n - 1, int(t * n))
        return values[i] + (values[i + 1] - values[i]) * (t * n - i)
    return f


def on_rings(table, y, a, n=2.0, off=0.0):
    """A point of a body lofted over level rings ``(y, half-width,
    half-depth, z of the middle)`` -- superellipses of power ``n`` -- at
    height ``y`` and angle ``a`` (from +x towards +z), ``off`` out from the
    surface; and the outward normal there."""
    if y <= table[0][0]:
        hw, hd, dz = table[0][1:]
    elif y >= table[-1][0]:
        hw, hd, dz = table[-1][1:]
    else:
        i = next(i for i in range(len(table) - 1) if y <= table[i + 1][0])
        r0, r1 = table[i], table[i + 1]
        t = (y - r0[0]) / (r1[0] - r0[0])
        hw, hd, dz = [r0[j] + (r1[j] - r0[j]) * t for j in (1, 2, 3)]
    c, s = add.cos(a), add.sin(a)
    x = hw * abs(c) ** (2.0 / n) * (1 if c >= 0 else -1)
    z = hd * abs(s) ** (2.0 / n) * (1 if s >= 0 else -1)
    gx = abs(x / hw) ** (n - 1) / hw * (1 if x >= 0 else -1)
    gz = abs(z / hd) ** (n - 1) / hd * (1 if z >= 0 else -1)
    g = add.sqrt(gx * gx + gz * gz) or 1.0
    return [x + gx / g * off, y, z + dz + gz / g * off], [gx / g, 0.0, gz / g]


def loft_rings(table, n, k, color):
    add.loft([[on_rings(table, r[0], 2 * add.pi * (i + 0.5) / k, n)[0] for i in range(k)] for r in table], color)


# the knight's body, helm and shoe: rings (y, half-width, half-depth, z of the middle), life-size
JUPON = [(0.66, 0.215, 0.168, 0.0), (0.76, 0.205, 0.158, 0.0), (0.86, 0.19, 0.145, 0.0), (0.94, 0.172, 0.13, 0.0),
         (1.04, 0.162, 0.126, 0.006), (1.16, 0.176, 0.14, 0.016), (1.28, 0.19, 0.148, 0.02), (1.38, 0.196, 0.138, 0.012),
         (1.45, 0.185, 0.12, 0.0), (1.5, 0.13, 0.095, 0.0), (1.535, 0.08, 0.075, 0.0)]
HELM = [(1.525, 0.117, 0.126, 0.012), (1.56, 0.121, 0.131, 0.012), (1.66, 0.122, 0.132, 0.012), (1.76, 0.12, 0.13, 0.012),
        (1.83, 0.114, 0.124, 0.01), (1.862, 0.1, 0.11, 0.008), (1.876, 0.06, 0.068, 0.006)]
SABATON = [(-0.085, 0.032, 0.07), (-0.066, 0.045, 0.1), (-0.02, 0.05, 0.12), (0.04, 0.05, 0.095), (0.1, 0.045, 0.07),
           (0.15, 0.034, 0.05), (0.19, 0.02, 0.032), (0.215, 0.006, 0.016)]          # (z, half-width, height) heel to toe


def great_helm(plume=True):
    """A great helm, life-size and where it sits on a knight (its rim at
    y = 1.525, the face towards +z): a flat-topped steel pot, eye slits
    either side of a gold cross on the face plate, breaths on the right
    cheek, and a plume of red feathers."""
    add.push()
    loft_rings(HELM, 2.6, 28, P["steel"])
    for s in (-1, 1):                                                                # the eye slits
        add.polyline([on_rings(HELM, 1.712, add.pi / 2 - s * (0.12 + 0.83 * i / 5.0), 2.6)[0] for i in range(6)], 0.009, 6, P["black"])
    add.polyline([on_rings(HELM, y, add.pi / 2, 2.6, 0.004)[0] for y in (1.54, 1.6, 1.66, 1.72, 1.78, 1.84)], 0.013, 6, P["gold"])
    add.polyline([on_rings(HELM, 1.748, add.pi / 2 - 1.15 + 0.23 * i, 2.6, 0.004)[0] for i in range(11)], 0.011, 6, P["gold"])
    for i in range(3):                                                               # the breaths, on the right (-x) cheek
        for j in range(3):
            p, nrm = on_rings(HELM, 1.585 + 0.03 * i, add.pi / 2 + 0.3 + 0.2 * j, 2.6)
            add.cylinder(_at(p, nrm, -0.004), _at(p, nrm, 0.003), 0.0065, 6, P["black"])
    if plume:
        add.cylinder([0, 1.868, -0.01], [0, 1.9, -0.016], 0.02, 8, P["gold"])
        for dx in (-0.035, 0.0, 0.035):
            add.polyline([[dx * 0.3, 1.89, -0.016], [dx, 2.0, -0.05], [dx * 1.6, 2.07, -0.15], [dx * 2.2, 2.05, -0.27], [dx * 2.5, 1.98, -0.34]],
                         lambda t: 0.006 + 0.03 * add.sin(add.pi * t), 7, P["red"], smooth=1)
    return add.pop()


def heater(w=0.46, h=0.58, t=0.028):
    """A heater shield with the castle's arms: a wooden board with the arms
    painted on its face -- the red field, the gold bend (clipped to the
    shield), three white roundels -- and an iron rim round its edge.  Built
    in the XY plane facing +z, the middle of its top edge at the origin."""
    R = (w * w / 4 + 0.5625 * h * h) / w                    # the lower sides: arcs from the straight upper sides to the point
    cx, cy = w / 2 - R, -0.25 * h
    end = add.atan2(-0.75 * h, -cx)
    arc = [(cx + R * add.cos(end * (1 - i / 8.0)), cy + R * add.sin(end * (1 - i / 8.0))) for i in range(9)]
    outline = arc + [(w / 2, 0.0), (-w / 2, 0.0)] + [(-x, y) for x, y in arc[:0:-1]]       # anticlockwise from the point
    add.push()
    add.prism(outline, t, P["wood"], (0, 0, 0), (0, 0, 1))
    face = shrunk(outline, 0.004)
    add.prism(face, 0.004, P["red"], (0, 0, t / 2 + 0.001), (0, 0, 1))
    band = [(u * w - w / 2, -v * h) for u, v in ((0, 0), (0.1, 0), (1, 0.9), (1, 1), (0.9, 1), (0, 0.1))]
    for i in range(len(face)):
        p, q = face[i], face[(i + 1) % len(face)]
        a, b = q[1] - p[1], p[0] - q[0]
        band = clip_half(band, a, b, a * p[0] + b * p[1])
    add.prism(band, 0.004, P["gold"], (0, 0, t / 2 + 0.004), (0, 0, 1))
    for u, v in ((0.27, 0.22), (0.73, 0.22), (0.5, 0.62)):
        add.cylinder([u * w - w / 2, -v * h, t / 2 + 0.004], [u * w - w / 2, -v * h, t / 2 + 0.009], 0.1 * w, 16, P["white"])
    add.polyline([[x, y, 0] for x, y in outline], 0.016, 6, P["iron"], closed=True)
    return add.pop()


def place_heater(top, nrm, up=(0, 1, 0)):
    """The heater shield with the middle of its top edge at ``top``, its
    face towards ``nrm`` and its length along ``up``."""
    n, u = vunit(nrm), vunit(up)
    x = vcross(u, n)
    add.mesh(add.transform(heater(), [[x[0], u[0], n[0], top[0]], [x[1], u[1], n[1], top[1]], [x[2], u[2], n[2], top[2]]]))


def sabaton(heel, fwd, color, table=SABATON):
    """An armoured shoe with a long pointed toe, its sole level at ``heel``
    (the ground below the ankle), the toe along the level direction ``fwd``;
    with another ``table`` of (z, half-width, height), a leather shoe."""
    rings = [[[hw * add.cos(add.pi * i / 6.0), h * add.sin(add.pi * i / 6.0), z] for i in range(7)] for z, hw, h in table]
    M = add.make(add.loft, rings, color)
    f = vunit([fwd[0], 0.0, fwd[2]])
    return add.transform(M, [[f[2], 0, f[0], heel[0]], [0, 1, 0, heel[1]], [-f[0], 0, f[2], heel[2]]])


def knight_leg(hip, knee, ankle, fwd, s):
    """Cuisse, knee cop with its fan, greave and sabaton of one leg (``s``:
    the side, -1 or 1 in x)."""
    S = P["steel"]
    d1, d2 = vunit(vsub(knee, hip)), vunit(vsub(ankle, knee))
    add.frustum(hip, _at(knee, d1, -0.03), 0.088, 0.066, 14, S)
    add.ellipsoid(_at(knee, [0, 0, 1], 0.012), [0.063, 0.063, 0.058], 4, S)
    add.cylinder(_at(knee, [s, 0, 0], 0.046), _at(knee, [s, 0, 0], 0.058), 0.048, 12, S)
    pts = [_at(knee, d2, 0.035), _at(knee, d2, 0.14), _at(knee, d2, 0.27), _at(ankle, d2, -0.05), ankle]
    add.polyline(pts, ramp((0.057, 0.064, 0.058, 0.05, 0.047)), 12, S)
    add.mesh(sabaton([ankle[0], ankle[1] - 0.1, ankle[2]], fwd, S))


def knight_arm(sh, el, wr, fist, s):
    """Spaulder and its lames, rerebrace, couter and its fan, vambrace, the
    gauntlet's flared cuff and the mailed fist of one arm."""
    S = P["steel"]
    d1, d2 = vunit(vsub(el, sh)), vunit(vsub(wr, el))
    add.ellipsoid([sh[0] + s * 0.012, sh[1] + 0.03, sh[2]], [0.098, 0.075, 0.108], 4, S)
    add.frustum(_at(sh, d1, 0.035), _at(sh, d1, 0.08), 0.083, 0.078, 12, S)
    add.frustum(_at(sh, d1, 0.075), _at(sh, d1, 0.12), 0.075, 0.068, 12, S)
    add.frustum(_at(sh, d1, 0.03), _at(el, d1, -0.03), 0.05, 0.044, 12, S)
    add.sphere(el, 0.05, 4, S)
    m = vunit([d1[i] + d2[i] for i in range(3)])
    out = vunit([(s if i == 0 else 0) - m[i] * m[0] * s for i in range(3)])      # sideways, square to the arm
    add.cylinder(_at(el, out, 0.034), _at(el, out, 0.046), 0.044, 12, S)
    add.frustum(_at(el, d2, 0.03), _at(wr, d2, -0.035), 0.044, 0.036, 12, S)
    add.frustum(_at(wr, d2, -0.005), _at(wr, d2, -0.08), 0.038, 0.056, 12, S)
    add.capsule(wr, _at(wr, vunit(fist), 0.055), 0.04, 9, P["iron"])


def jupon(hem=0.66):
    """The knight's body: breastplate and back under a close-fitting red
    jupon with the castle's arms on the chest -- the gold bend from his
    right shoulder and three white roundels, all following the cloth --
    a gold hem, and the knightly girdle of gold plaques low on the hips.
    A higher ``hem`` shortens the skirt (sitting in a saddle)."""
    table = JUPON if hem == JUPON[0][0] else [(hem, 0.205, 0.16, 0.0)] + [r for r in JUPON if r[0] > hem + 0.05]
    loft_rings(table, 2.3, 24, P["red"])
    for A0, A1 in ((add.pi - 0.42, 0.42), (add.pi + 0.42, 2 * add.pi - 0.42)):   # the arms on his chest and his back:
        def cloth(u, v, off):                                                # u from his right (-x), v down
            return on_rings(table, 1.42 - 0.48 * v, A0 + (A1 - A0) * u, 2.3, off)
        add.parametric(lambda p, q: cloth(min(1.0, max(0.0, p + 0.2 * q - 0.1)), p, 0.0045)[0], 0, 1, 14, 0, 1, 1, P["gold"], thickness=0.003)
        for u, v in ((0.27, 0.22), (0.73, 0.22), (0.5, 0.72)):
            p, nrm = cloth(u, v, 0.0065)
            add.cylinder(p, _at(p, nrm, 0.0035), 0.045, 16, P["white"])
    add.polyline([on_rings(table, hem + 0.012, 2 * add.pi * i / 24.0, 2.3, 0.002)[0] for i in range(24)], 0.012, 6, P["gold"], closed=True)
    add.loft([[on_rings(table, y, 2 * add.pi * (i + 0.5) / 24, 2.3, 0.008)[0] for i in range(24)] for y in (0.885, 0.925)], P["wood_dark"])
    plaque = add.make(add.cuboid, [0, 0, 0], [0.028, 0.03, 0.008], P["gold"])
    for i in range(16):
        p, nrm = on_rings(table, 0.905, 2 * add.pi * i / 16.0, 2.3, 0.012)
        big = add.stretch(plaque, [1.9, 1.4, 1.0], (0, 0, 0)) if i == 4 else plaque       # the buckle in front
        add.mesh(add.move(add.rotateY(big, add.pi / 2 - add.atan2(nrm[2], nrm[0])), p))
    p0 = on_rings(table, 0.88, add.pi / 2, 2.3, 0.012)[0]
    p1 = on_rings(table, max(hem + 0.03, 0.74), add.pi / 2, 2.3, 0.012)[0]
    add.beam(p0, p1, 0.03, 0.006, P["wood_dark"], up=[0, 0, 1])                              # the girdle's end
    add.cuboid([p1[0], p1[1] - 0.01, p1[2] + 0.003], [0.03, 0.03, 0.008], P["gold"])
    add.frustum([0, 1.48, 0.0], [0, 1.56, 0.005], 0.095, 0.07, 14, P["mail"])              # the aventail under the helm


def scabbard(hilt=True, ride=False):
    """The sword at his left (+x) hip: the scabbard hanging from the
    girdle -- down his leg, or back along the horse's flank when he rides --
    steel locket and chape, and, unless the sword is in his hands, its hilt:
    gold cross-guard, leather grip, gold wheel pommel."""
    top, tip = ([0.21, 0.86, 0.02], [0.38, 0.28, -0.55]) if ride else ([0.228, 0.87, 0.07], [0.265, 0.1, -0.2])
    d = vunit(vsub(top, tip))
    add.beam(tip, top, 0.052, 0.026, P["wood_dark"], up=[1, 0, 0])
    add.cone(_at(tip, d, 0.06), _at(tip, d, -0.02), 0.03, 6, P["steel"])
    add.beam(_at(top, d, -0.07), top, 0.058, 0.03, P["steel"], up=[1, 0, 0])
    if hilt:
        w = vunit([-d[0] * d[2], -d[1] * d[2], 1 - d[2] * d[2]])
        g = _at(top, d, 0.012)
        add.beam(_at(g, w, -0.11), _at(g, w, 0.11), 0.024, 0.024, P["gold"])
        add.cylinder(g, _at(g, d, 0.12), 0.016, 8, P["wood_dark"])
        pm = _at(g, d, 0.14)
        add.cylinder([pm[0] - 0.011, pm[1], pm[2]], [pm[0] + 0.011, pm[1], pm[2]], 0.03, 12, P["gold"])


# where his wrists go, the way his fists point, and the way his elbows bend: (right arm, left arm)
POSES = {"spear": (([-0.29, 1.08, 0.19], [0, 0.05, 1], [-0.35, -0.3, -1]), ([0.21, 1.02, 0.2], [-0.35, 0, 1], [1, -0.3, -0.6])),
         "sword": (([-0.07, 0.975, 0.27], [1, 0, 0], [-1, -0.4, -0.4]), ([0.07, 0.935, 0.27], [-1, 0, 0], [1, -0.4, -0.4])),
         "none": (([-0.245, 0.9, 0.04], [0, -1, 0.15], [0, 0, -1]), ([0.245, 0.9, 0.04], [0, -1, 0.15], [0, 0, -1])),
         "ride": (([-0.3, 1.05, 0.33], [0, 0.1, 1], [-0.4, -0.3, -1]), ([0.07, 0.98, 0.26], [-0.25, -0.2, 1], [1, -0.3, -0.5]))}


def arms_in(pose, shield=True):
    """(wrist, fist, elbow) of his right and left arm in ``pose``; a
    spearman with no shield lets his left arm hang."""
    right, left = POSES[pose]
    return right, (POSES["none"][1] if pose == "spear" and not shield else left)


def fists(pose, shield=True):
    """The middle of his right and left fist in ``pose``."""
    return [_at(wr, vunit(fist), 0.03) for wr, fist, pole in arms_in(pose, shield)]


def knight(pose="spear", shield=True, plume=True, table=None):
    """A knight in armour, life-size, standing on the origin facing +z (his
    right hand on -x).  ``pose``: "spear" (its butt on the ground, the
    shield on his left arm), "sword" (both hands on the pommel of a sword
    resting point-down, the shield standing against his left leg), "none"
    (arms by his sides: a suit on a stand), "ride" (sitting astride, the
    reins in his left hand, for :func:`rider`) or "sit" (on a chair 0.48
    high, bareheaded in his mail coif, his forearms on a ``table`` = (its
    height above the floor, its edge's distance from his hips), in the
    castle's units)."""
    add.push()
    ride, sit = pose == "ride", pose == "sit"
    dy = (0.48 / LIFE + 0.1) - 0.93 if sit else 0.0                              # sitting, all above his hips is lower
    for s in (-1, 1):
        hip = [s * 0.1, 0.93 + dy, 0.0]
        if ride:
            knee, ankle, fwd = [s * 0.335, 0.66, 0.24], [s * 0.335, 0.27, 0.3], [s * 0.25, 0, 1]
        elif sit:
            knee, ankle, fwd = [s * 0.12, 0.92 + dy, 0.43], [s * 0.125, 0.1, 0.47], [s * 0.15, 0, 1]
        else:
            ankle = [s * (0.165 if pose == "sword" else 0.115), 0.1, -0.005]
            knee, fwd = joint(hip, ankle, 0.42, 0.415, [0, 0, 1]), [s * 0.2, 0, 1]
        knight_leg(hip, knee, ankle, fwd, s)
    add.push()                                                                    # all above his hips
    jupon(0.82 if ride or sit else 0.66)
    if sit:                                                                       # his face in the mail coif
        add.ellipsoid([0, 1.665, 0.012], [0.078, 0.108, 0.095], 5, P["skin"])
        add.ellipsoid([0, 1.655, 0.103], [0.014, 0.026, 0.022], 2, P["skin"])
        for s in (-1, 1):
            add.sphere([s * 0.03, 1.685, 0.092], 0.011, 2, P["black"])
            add.capsule([s * 0.012, 1.628, 0.1], [s * 0.05, 1.615, 0.085], 0.01, 6, P["trunk"])
        add.ellipsoid([0, 1.585, 0.07], [0.058, 0.065, 0.042], 3, P["trunk"])
        add.ellipsoid([0, 1.68, -0.018], [0.1, 0.122, 0.112], 5, P["mail"])
        wy, wz = table[0] / LIFE + 0.035 - dy, table[1] / LIFE + 0.12
        arms = (([-0.16, wy, wz], [0.35, -0.2, 1], [-1, -0.4, -0.4]), ([0.16, wy, wz], [-0.35, -0.2, 1], [1, -0.4, -0.4]))
    else:
        add.mesh(great_helm(plume))
        arms = arms_in(pose, shield)
    for s, (wr, fist, pole) in zip((-1, 1), arms):
        sh = [s * 0.2, 1.425, 0.0]
        knight_arm(sh, joint(sh, wr, 0.31, 0.27, pole), wr, fist, s)
    upper = add.pop()
    add.mesh(add.move(upper, [0, dy, 0]))
    if sit:
        return add.pop()
    right, left = fists(pose, shield)
    scabbard(pose != "sword", ride)
    if pose == "spear":                                                           # the spear, in his right fist
        x, z = right[0], right[2]
        add.cylinder([x, 0.0, z], [x, 2.88, z], 0.019, 8, P["wood"])
        add.frustum([x, 2.86, z], [x, 2.95, z], 0.024, 0.02, 8, P["steel"])
        add.cone([x, 3.02, z], [x, 3.24, z], 0.042, 4, P["steel"])
        add.cone([x, 3.02, z], [x, 2.94, z], 0.042, 4, P["steel"])
    if pose == "sword":                                                           # the sword, point on the ground
        add.cylinder([-0.011, 1.02, 0.27], [0.011, 1.02, 0.27], 0.03, 12, P["gold"])
        add.cylinder([0, 1.0, 0.27], [0, 0.86, 0.27], 0.016, 8, P["wood_dark"])
        add.cuboid([0, 0.852, 0.27], [0.23, 0.022, 0.024], P["gold"])
        add.prism([[-0.025, 0.842], [0.025, 0.842], [0.007, 0.08], [0.0, 0.0], [-0.007, 0.08]], 0.01, P["steel"], (0, 0, 0.27), (0, 0, 1))
    if shield and pose == "spear":                                                # on his left arm
        n = vunit([0.32, 0, 0.95])
        c = _at(_at(left, n, 0.068), vcross([0, 1, 0], n), 0.07)
        place_heater([c[0], c[1] + 0.261, c[2]], n)
    elif shield and ride:                                                         # hung at his left side by the guige
        place_heater([0.5, 1.26, 0.1], [0.93, 0, 0.36])
        add.polyline([[0.47, 1.25, 0.03], [0.34, 1.5, 0.0], [0.14, 1.535, 0.0], [0.02, 1.5, 0.12]], 0.012, 5, P["wood_dark"])
    elif shield:                                                                  # standing on its point against his left leg
        phi = add.asin(0.145 / 0.58)
        place_heater([0.36 - 0.58 * add.sin(phi), 0.58 * add.cos(phi), 0.14], [add.cos(phi), add.sin(phi), 0], [-add.sin(phi), add.cos(phi), 0])
    return add.pop()


def armour(at, facing=0.0, weapon="spear", shield=True, plume=True):
    """A knight in armour standing on the point ``at`` facing ``facing``:
    with a spear, resting on his sword, or (``weapon="none"``) a suit of
    armour on its stand -- see :func:`knight`."""
    M = add.stretch(knight(weapon, shield, plume), [LIFE] * 3, (0, 0, 0))
    add.mesh(add.move(add.rotateY(M, facing), at))


def lying_armour(at, facing=0.0):
    """A guard asleep on his back on the surface ``at`` (head towards
    ``facing``), his spear laid beside him."""
    M = add.rotateX(knight("none", False, False), -add.pi / 2)                  # standing -> on his back, head at -z
    M = add.move(M, [0, -add.bbox(M)[0][1], 0])                                 # the back of him on the floor
    M.extend(add.make(add.cylinder, [-0.42, 0.02, 0.55], [-0.42, 0.02, -2.3], 0.019, 8, P["wood"]))
    M.extend(add.make(add.frustum, [-0.42, 0.02, -2.28], [-0.42, 0.02, -2.39], 0.024, 0.02, 8, P["steel"]))
    M.extend(add.make(add.cone, [-0.42, 0.02, -2.46], [-0.42, 0.02, -2.68], 0.042, 4, P["steel"]))
    M.extend(add.make(add.cone, [-0.42, 0.02, -2.46], [-0.42, 0.02, -2.38], 0.042, 4, P["steel"]))
    add.mesh(add.move(add.rotateY(add.stretch(M, [LIFE] * 3, (0, 0, 0)), facing), at))


def bowman(at, facing=0.0, weapon="bow"):
    """An archer (``weapon="bow"``) or a crossbowman shooting: no plate, a
    shirt and a coif of chain mail, hose and boots.  The archer stands
    side-on, his bow arm straight out to the target, the string drawn to
    his cheek with the elbow back and a quiver on his back; the
    crossbowman faces the target, the stock at his cheek, one hand at the
    trigger, the other under the fore-end, a bag of bolts at his hip.
    Built with the target towards +z and mirrored at the end, so that both
    are right-handed, like the knights: the bow in the left hand, the
    string drawn with the right, the crossbow at the right cheek."""
    add.push()
    mail, skin, kc = P["mail"], P["skin"], 12
    bow = weapon == "bow"
    legs = ((([0, 0.95, 0.1], [0, 0.1, 0.28]), ([0, 0.95, -0.1], [0, 0.1, -0.28])) if bow else
            (([-0.1, 0.95, 0.03], [-0.12, 0.1, 0.16]), ([0.1, 0.95, -0.03], [0.12, 0.1, -0.12])))
    for hip, ankle in legs:                                                         # hose and boots
        add.capsule(hip, ankle, 0.085, kc, P["wood_dark"])
        if bow:                                                                     # (side-on: the feet across the line)
            add.cuboid([ankle[0] + 0.06, 0.06, ankle[2]], [0.26, 0.12, 0.13], P["black"])
        else:
            add.cuboid([ankle[0], 0.06, ankle[2] + 0.06], [0.13, 0.12, 0.26], P["black"])
    lathe([[0.0, 0.6], [0.27, 0.6], [0.23, 0.92], [0.0, 0.92]], [0, 0, 0], k_(8), mail)   # the mail shirt: its skirt,
    add.capsule([0, 0.9, 0], [0, 1.36, 0], 0.2, kc, mail)                                 # the body,
    for y, r in ((0.7, 0.262), (0.81, 0.248), (1.04, 0.203), (1.16, 0.203), (1.28, 0.203)):
        add.torus([0, y, 0], r, 0.009, 16, 4, P["iron"])                                  # and rows of rings
    add.torus([0, 0.94, 0], 0.222, 0.03, 16, 6, P["wood_dark"])                          # the belt
    head = [0.035, 1.66, 0.02] if bow else [0.04, 1.64, 0.06]                          # (the archer's cheek at his hand)
    add.cylinder([0, 1.36, 0], [0, 1.56, 0], 0.06, kc, skin)
    add.ellipsoid(head, [0.082, 0.107, 0.097], 5, skin)
    add.ellipsoid([head[0], head[1] + 0.015, head[2] - 0.03], [0.1, 0.122, 0.112], 5, mail)   # the coif, open at the face
    add.ellipsoid([head[0], head[1] - 0.015, head[2] + 0.1], [0.014, 0.026, 0.022], 2, skin)  # the face: nose, eyes
    for s in (-1, 1):
        add.sphere([head[0] + s * 0.03, head[1] + 0.02, head[2] + 0.088], 0.011, 2, P["black"])
    if bow:
        add.capsule([0, 1.42, 0.2], [0, 1.46, 0.76], 0.06, kc, mail)                       # the bow arm, straight out
        add.sphere([0, 1.46, 0.8], 0.06, 6, skin)
        add.capsule([0, 1.42, -0.2], [0.08, 1.52, -0.52], 0.06, kc, mail)                  # the drawing arm: the elbow back,
        add.capsule([0.08, 1.52, -0.52], [0.14, 1.6, 0.03], 0.055, kc, mail)               # the hand at his cheek
        add.sphere([0.14, 1.6, 0.06], 0.06, 6, skin)
        stave = [[0.0, 1.46 + 0.8 * t, 0.8 - 0.26 * t * t] for t in (-1, -0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75, 1)]
        add.polyline(stave, 0.025, 6, P["wood"])                                           # the bow, drawn
        nock = [0.12, 1.59, 0.06]
        for tip in (stave[0], stave[-1]):
            add.cylinder(tip, nock, 0.008, 4, P["rope"])
        add.cylinder(nock, [0.02, 1.48, 0.98], 0.012, 5, P["wood_light"])                  # the arrow, on the bow hand
        add.cone([0.02, 1.48, 0.98], [0.013, 1.472, 1.06], 0.03, 5, P["steel"])
        for dx, dy in ((0.02, 0.0), (-0.01, 0.02)):
            add.cuboid([0.105 + dx, 1.575 + dy, 0.2], [0.005, 0.03, 0.12], P["white"])     # its feathers
        add.cylinder([-0.26, 0.95, -0.06], [-0.3, 1.45, -0.15], 0.07, 8, P["wood"])        # the quiver on his back
        for i in range(3):
            add.cylinder([-0.3, 1.45, -0.15], [-0.3 + 0.04 * (i - 1), 1.6, -0.17 + 0.03 * i], 0.012, 4, P["white"])
    else:
        sy = 1.5                                                                           # the crossbow, at his cheek
        add.beam([0.12, sy, 0.18], [0.12, sy + 0.02, 0.95], 0.07, 0.09, P["wood_dark"])
        for s in (-1, 1):                                                                  # its steel bow, spanned
            add.beam([0.12, sy + 0.05, 0.9], [0.12 + s * 0.26, sy + 0.05, 0.81], 0.04, 0.05, P["iron"])
            add.cylinder([0.12 + s * 0.26, sy + 0.05, 0.81], [0.12, sy + 0.07, 0.58], 0.007, 4, P["rope"])
        add.cylinder([0.12, sy + 0.08, 0.56], [0.12, sy + 0.08, 1.0], 0.012, 5, P["wood_light"])   # the bolt
        add.cone([0.12, sy + 0.08, 1.0], [0.12, sy + 0.08, 1.08], 0.025, 5, P["steel"])
        add.capsule([0.2, 1.42, 0], [0.3, 1.2, 0.12], 0.06, kc, mail)                      # right hand at the trigger
        add.capsule([0.3, 1.2, 0.12], [0.14, 1.43, 0.3], 0.055, kc, mail)
        add.sphere([0.13, 1.44, 0.32], 0.06, 6, skin)
        add.capsule([-0.2, 1.42, 0], [-0.12, 1.2, 0.38], 0.06, kc, mail)                   # left hand under the fore-end
        add.capsule([-0.12, 1.2, 0.38], [0.08, 1.43, 0.6], 0.055, kc, mail)
        add.sphere([0.1, 1.44, 0.6], 0.06, 6, skin)
        add.cuboid([0.27, 0.8, -0.06], [0.1, 0.35, 0.2], P["wood"])                       # a bag of bolts at his hip
        for i in range(3):
            add.cylinder([0.27, 0.97, -0.12 + 0.06 * i], [0.27, 1.07, -0.12 + 0.06 * i], 0.012, 4, P["iron"])
    M = add.stretch(add.pop(), [-LIFE, LIFE, LIFE], (0, 0, 0))                          # as tall as the castle's other people
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


GATE_TOP = G + 13                                      # (the gate block runs from GATE_Z0 to GATE_Z1: see the moat)
SPRING = G + 4.5                                       # the arch springs here; 2.5 more to the apex
GATE_ROOF = GATE_TOP + 0.4
GATE_ARRIVE = []                                       # where the stairs of the two gate towers reach their tops
for s in (-1, 1):
    # doors: to the courtyard (side 3 = -z), onto the wall walk (outer side), onto the gate roof (inner side)
    outer, inner = (0, 2) if s > 0 else (2, 0)
    stops = [(WALK, outer * add.pi / 2 - 0.35, outer * add.pi / 2 + 0.35),
             (GATE_ROOF, inner * add.pi / 2 - 0.35, inner * add.pi / 2 + 0.35)]
    GATE_ARRIVE.append(square_tower([s * 7, 0, 50], G - 1, G + 20, GATE_W, doors=[(3, G), (outer, WALK), (inner, GATE_ROOF)],
                       walk_stops=stops, roof_h=6, windows=[(1, G + 8, 0.9, 1.6), (1, G + 15, 0.9, 1.6), (3, G + 15, 0.9, 1.6)]))
    banner([s * 7, G + 17.5, 53.5 + 0.5])
# the passage: jambs, the arch fill, voussoirs on both faces.  Two metres in from the outer face, the portcullis's
# way: a groove up either jamb, and over the springing a long slot across the vault, up into the gatehouse, which the
# portcullis is drawn up into -- behind the windlass of the drawbridge, so that the chains never cross its way
PORT_Z, SLOT, GROOVE = GATE_Z1 - 2.0, 0.1, 0.15        # the middle of the slot, half its width, how deep the grooves are
LINING = 0.06                                          # the stones the passage is lined with: how thick
for z0, z1 in ((GATE_Z0, PORT_Z - SLOT), (PORT_Z + SLOT, GATE_Z1)):
    for s in (-1, 1):
        add.cuboid([s * (3.5 + 2.5 + LINING) / 2, (G - 1 + SPRING) / 2, (z0 + z1) / 2], [1.0 - LINING, SPRING - G + 1, z1 - z0],
                   P["mortar"])
    add.mesh(arch_fill(-3.5, 3.5, SPRING, GATE_TOP, z0, z1, 0, 2.5 + LINING, P["mortar"]))
    # the passage lined with blocks of stone laid in courses, the joints staggered: up the jambs, and round the vault
    rows = int(round((SPRING - G - 0.02) / BLOCK[1]))
    bh = (SPRING - G - 0.02) / rows
    courses = 13                                       # round the vault as many as the voussoirs of the arch
    for j in range(rows + courses):
        za = z0 - (BLOCK[0] / 2 if j % 2 else 0.0)
        while za < z1 - 0.15:
            a, b = max(za, z0), min(za + BLOCK[0], z1)
            za += BLOCK[0]
            if b - a < 0.15:
                continue
            if j < rows:                               # a course up the jambs
                y = G + 0.02 + j * bh
                for s in (-1, 1):
                    add.cuboid([s * (2.5 + LINING / 2), y + bh / 2, (a + b) / 2], [LINING, bh - 0.05, b - a - 0.05],
                               pick("stone", a * 3 + s, j))
            else:                                      # or round the vault
                c = j - rows
                a0, a1 = add.pi * c / courses + 0.01, add.pi * (c + 1) / courses - 0.01
                vblock = [[r * add.cos(t), SPRING + r * add.sin(t)] for r, t in ((2.5, a0), (2.5 + LINING + 0.02, a0),
                                                                                 (2.5 + LINING + 0.02, a1), (2.5, a1))]
                add.prism(vblock, b - a - 0.05, pick("stone", a * 3, j), (0, 0, (a + b) / 2), (0, 0, 1))
for s in (-1, 1):                                      # the masonry behind the grooves and beside the slot, and
    add.cuboid([s * (3.5 + 2.5 + GROOVE) / 2, (G - 1 + GATE_TOP) / 2, PORT_Z], [1.0 - GROOVE, GATE_TOP - G + 1, 2 * SLOT],
               P["black"])                             # the grooves' and the slot's sides, all dark in their shadow
for z0 in (PORT_Z - SLOT, PORT_Z + SLOT - 0.01):
    add.mesh(arch_fill(-2.5 - GROOVE, 2.5 + GROOVE, SPRING, GATE_TOP, z0, z0 + 0.01, 0, 2.5, P["black"]))
    for s in (-1, 1):
        add.cuboid([s * (2.5 + GROOVE / 2), (G + 0.02 + SPRING) / 2, z0 + 0.005], [GROOVE, SPRING - G - 0.02, 0.01], P["black"])
add.cuboid([0, GATE_TOP - 0.05, PORT_Z], [2 * (2.5 + GROOVE), 0.1, 2 * SLOT], P["black"])
for z, depth in ((GATE_Z1, 0.25), (GATE_Z0, -0.25)):                          # stone skins on both faces, round the arch
    add.push()
    stone_face(GATE_W, G - 1, GATE_TOP, 0, 0.22, "stone", seed=int(z),
               skip=[(GATE_W / 2 - 3.15, GATE_W / 2 + 3.15, G - 1, SPRING + 3.15, (GATE_W / 2, SPRING, 3.15))])
    add.mesh(add.move(add.pop() if depth > 0 else add.mirror(add.pop(), [0, 0, 0], [0, 0, 1]), [-GATE_W / 2, 0, z]))
    voussoirs(0, SPRING, 2.5, z, depth, 13, lambda i: shade_of("stone", i), width=0.6)
    for s in (-1, 1):                                  # and below them dressed stones up both jambs, as wide as the
        for j in range(int(round((SPRING - G + 1) / BLOCK[1]))):             # voussoirs, in the courses of the wall
            add.cuboid([s * 2.8, G - 1 + (j + 0.5) * BLOCK[1], z + depth / 2], [0.6, BLOCK[1] - 0.06, abs(depth)],
                       shade_of("stone", j + (s > 0)))
add.cuboid([0, GATE_TOP + 0.2, 50], [GATE_W, 0.4, GATE_Z1 - GATE_Z0 + 0.6], P["stone_dark"])   # the gate roof
add.mesh(add.move(add.make(merlons, GATE_W, 0.4, 0, 0.5), [-3.5, GATE_TOP, GATE_Z1]))
add.mesh(add.move(add.make(merlons, GATE_W, 0.4, -0.5, 0), [-3.5, GATE_TOP, GATE_Z0]))
GATE_TEXT, GATE_H = "ADD 2.0", 0.55                   # the gate's name on a stone tablet fixed to the wall over the arch,
TABLET_G = add.text_width(GATE_TEXT, GATE_H) + 0.5    # narrow enough to sit between the drawbridge's two chains
TABLET_Y, TABLET_H = G + 8.3, GATE_H + 0.35
add.cuboid([0, TABLET_Y, GATE_Z1 + 0.26], [TABLET_G, TABLET_H, 0.12], P["stone_dark"])
for y in (TABLET_Y - TABLET_H / 2 + 0.03, TABLET_Y + TABLET_H / 2 - 0.03):
    add.cuboid([0, y, GATE_Z1 + 0.335], [TABLET_G, 0.06, 0.03], P["gold"])
for x in (-TABLET_G / 2 + 0.03, TABLET_G / 2 - 0.03):
    add.cuboid([x, TABLET_Y, GATE_Z1 + 0.335], [0.06, TABLET_H, 0.03], P["gold"])
add.text(GATE_TEXT, [0, TABLET_Y - GATE_H / 2, GATE_Z1 + 0.35], GATE_H, 0.06, P["gold"], align="center", k=8)
for s in (-1, 1):                                      # the gate towers stand in the moat, down to its floor, with
    add.cuboid([s * 7, (MOAT_Y - 0.5 + G - 1) / 2, 50], [GATE_W, G - 1 - MOAT_Y + 0.5, GATE_W], P["mortar"])   # stones
    for side in (1, 0 if s > 0 else 2):                                          # on the sides the water comes to
        add.push()
        stone_face(GATE_W, MOAT_Y, G - 0.5, GATE_W / 2, 0.22, "stone", seed=side + int(s * 7) + 30)
        M = add.move(add.pop(), [-GATE_W / 2, 0, 0])
        add.mesh(add.move(add.rotateY(M, add.pi / 2 - side * add.pi / 2), [s * 7, 0, 50]))
# the paved passage, and the landing before the gate paved the same way (the landing's pier: see the moat's stonework)
PAVE = G + 0.1                                         # top of the paving: level with the cobblestones
add.cuboid([0, (G - 0.3 + G + 0.02) / 2, (GATE_Z0 + GATE_Z1) / 2], [7.0, 0.32, GATE_Z1 - GATE_Z0], P["mortar"])
cobble_area(lambda x, z: (abs(x) < 2.45 if z < GATE_Z1 else landing_depth(x, z, False) > 0.62 and (abs(x) < 3.3 or z > GATE_FRONT + 0.15)
                          and (z < BRIDGE_Z0 - 0.2 or abs(x) > DECK + 0.16)) and hash2(int(x * 9), int(z * 9), 77) < max(DENSITY, 0.35),
            -7, 7, GATE_Z0 + 0.075, BRIDGE_Z0 + 1.0, G + 0.02, step=0.44, scale=0.7, seed=5)   # cobbles: passage and landing,
for i in range(1, 46, 2):                              # right up to the bridge's hinge: where the last row of the
    x = -7 + i * 0.308                                 # cobbles leaves a gap before it, a smaller one
    if abs(x) < DECK + 0.16 and hash2(i, 5, 79) < max(DENSITY, 0.35):
        stone = add.stretch(COBBLES[int(hash2(i, 5, 80) * 6) % 6], [0.36, 0.36, 0.36], (0, 0, 0))
        add.mesh(add.move(add.rotateY(stone, hash2(i, 5, 81) * 6.28), [x, G + 0.02, BRIDGE_Z0 - 0.153]))
flush("gatehouse")

# the portcullis, drawn up to the springing of the arch -- a rider passes under its teeth -- into its slot: a square
# mesh of iron bars 0.4 apart, the ends of its cross bars in the grooves of the jambs
PORT_BOTTOM = SPRING + 0.1
PORT_STEP = 0.4
for i in range(13):
    x = -2.4 + i * PORT_STEP
    add.cylinder([x, PORT_BOTTOM + 0.3, PORT_Z], [x, GATE_TOP - 0.2, PORT_Z], 0.055, 12, P["iron"])
    add.cone([x, PORT_BOTTOM + 0.3, PORT_Z], [x, PORT_BOTTOM, PORT_Z], 0.055, 12, P["iron"])
for j in range(int((SPRING + 2.6 - PORT_BOTTOM - 0.3) / PORT_STEP) + 1):
    add.cuboid([0, PORT_BOTTOM + 0.3 + j * PORT_STEP, PORT_Z], [2 * (2.5 + GROOVE - 0.03), 0.09, 0.1], P["iron"])
# the wooden gate behind it: two leaves on hinges, both swung wide open;
# their tops follow the arch, so that closed they fill it exactly
for s, angle in ((-1, 1.3), (1, -1.3)):
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

# the drawbridge: a deck of planks spanning the moat from the landing to the far bank, level with the paving before the
# gate and with the road.  It turns on one long hinge of grey iron, like a piano's, just as long as the deck is wide,
# between the cobbles of the landing and the ends of the planks, a little lower than they are: its knuckles, in turn from
# a leaf let into the stone under the cobbles and from a leaf under the planks, on one long pin, and the planks' ends,
# rebated underneath, lying over it.  Across its far end, under the planks, an iron bar.  The leaf and the bar rest on
# seats of dressed stone, and every plank is nailed down to them from above
HINGE_Y = G - 0.01                                      # the pin
REBATE = (BRIDGE_Z0 + HINGE_R + 0.005, HINGE_Y + HINGE_R + 0.005)
planks = 11
for i in range(planks):
    x = (i - (planks - 1) / 2) * 0.42
    add.prism([[G - 0.03, REBATE[0]], [REBATE[1], REBATE[0]], [REBATE[1], BRIDGE_Z0], [G + 0.12, BRIDGE_Z0],
               [G + 0.12, BRIDGE_Z1], [G - 0.03, BRIDGE_Z1]], 0.4, pick("wood", i, 9), (x, 0, 0), (1, 0, 0))
for i in range(18):                                                              # the hinge's knuckles,
    x0 = -DECK + 2 * DECK * i / 18
    add.cylinder([x0 + 0.005, HINGE_Y, BRIDGE_Z0], [x0 + 2 * DECK / 18 - 0.005, HINGE_Y, BRIDGE_Z0], HINGE_R, 16, P["mail"])
add.cylinder([-DECK, HINGE_Y, BRIDGE_Z0], [DECK, HINGE_Y, BRIDGE_Z0], 0.025, 8, P["mail"])       # its pin,
add.cuboid([0, G - 0.042, BRIDGE_Z0 + 0.24], [2 * DECK, 0.02, 0.44], P["mail"])                  # its leaf under the
add.cuboid([0, G - 0.055, BRIDGE_Z1 - 0.4], [2 * DECK, 0.05, 0.18], P["iron"])                   # planks; the iron bar


def nail(x, y, z):                                      # the head of a big nail, forged and hammered home
    add.cylinder([x, y, z], [x, y + 0.012, z], 0.04, 8, P["mail"])
    add.cone([x, y + 0.012, z], [x, y + 0.03, z], 0.04, 8, P["mail"])


for i in range(planks):                                 # every plank nailed down with one nail at each end: into the
    x = (i - (planks - 1) / 2) * 0.42                   # hinge's leaf, and into the iron bar
    nail(x, G + 0.12, BRIDGE_Z0 + 0.25)
    nail(x, G + 0.12, BRIDGE_Z1 - 0.4)
# the chains run taut and parallel from the bridge's far end up into two round
# holes in the gate's front, lined with iron: behind them, inside the gatehouse,
# the windlass that winds them in and draws the bridge up against the gate -- in
# front of the portcullis's slot, so that the chains never cross its way
for s in (-1, 1):
    hole = [s * 2.0, G + 10.2, GATE_Z1 + 0.22]                                   # on the face of the stones
    add.cylinder([hole[0], hole[1], hole[2] - 0.02], [hole[0], hole[1], hole[2] + 0.05], 0.42, 16, P["iron"])     # the iron plate
    add.torus([hole[0], hole[1], hole[2] + 0.06], 0.27, 0.04, 16, 6, P["iron"], axis=(0, 0, 1))                  # the rim
    add.cylinder([hole[0], hole[1], hole[2] + 0.05], [hole[0], hole[1], hole[2] + 0.065], 0.25, 16, P["black"])  # the hole
    for a in range(4):                                                                                           # rivets
        add.sphere([hole[0] + 0.35 * add.cos(a * add.pi / 2 + 0.78), hole[1] + 0.35 * add.sin(a * add.pi / 2 + 0.78), hole[2] + 0.05],
                   0.03, 2, P["iron"])
    chain([s * 2.0, G + 0.225, BRIDGE_Z1 - 0.4], [hole[0], hole[1], hole[2] + 0.05])
    add.torus([s * 2.0, G + 0.225, BRIDGE_Z1 - 0.4], 0.16, 0.05, k_(10), k_(6), P["iron"], axis=(1, 0, 0))
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
        for i in range(1, cols):                                                                         # lead cames, up
            px = x0 + ins + i * pw                                                                       # into the arch
            y_top = top + add.sqrt(max(0.0, (r - ins) ** 2 - (px - o["x"]) ** 2)) if o["arched"] else top
            add.cuboid([px, (o["y0"] + y_top) / 2, zf], [0.03, y_top - o["y0"], 0.06], P["black"])
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
CELLAR_CUT = [add.make(add.cuboid, [(CELLAR_STAIR[0] + CELLAR_STAIR[1]) / 2, (G - 1.2 + KY + 0.2) / 2, (CELLAR_STAIR[2] + CELLAR_STAIR[3]) / 2],
                       [CELLAR_STAIR[1] - CELLAR_STAIR[0], KY + 1.4 - G, CELLAR_STAIR[3] - CELLAR_STAIR[2]]),
              add.make(add.cuboid, [(CELLAR_ROOM[0] + CELLAR_ROOM[1]) / 2, (CELLAR_Y + G - 0.15) / 2, (CELLAR_ROOM[2] + CELLAR_ROOM[3]) / 2],
                       [CELLAR_ROOM[1] - CELLAR_ROOM[0], G - 0.15 - CELLAR_Y, CELLAR_ROOM[3] - CELLAR_ROOM[2]])]
plinth = add.difference(plinth, *(tower_cutters(G - 1, KY + 1) + CELLAR_CUT))            # (and the wine cellar's stair)
add.mesh(add.color(plinth, P["stone_dark"]))
add.stairs([0, G, KZ1 + PL + 2.4], 4, 5.6, (KY - G) / 4, 0.6, P["stone_dark"], direction=(0, 0, -1))   # between the porch's pedestals
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
east += [opening(14, HALL_H + SLAB, HALL_H + SLAB + 2.6, 1.4, kind="door")]    # and above it, from the dormitory into its attic
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
        if near_tower(x + 1, z + 1, 0.5) or (CELLAR_STAIR[0] < x + 1 < CELLAR_STAIR[1] and CELLAR_STAIR[2] < z + 1 < CELLAR_STAIR[3]):
            continue
        add.cuboid([x + 1, KY, z + 1], [1.9, 0.1, 1.9], P["white"] if (i + j) % 2 else P["wood_dark"])
# the floor between the storeys, its beams below, and the attic floor with a hatch
storey = add.make(add.cuboid, [0, KY + HALL_H + SLAB / 2 - 0.02, (KZ0 + KZ1) / 2], [KX1 - KX0 - 0.4, SLAB - 0.04, KZ1 - KZ0 - 0.4], P["wood_dark"])
add.mesh(add.difference(storey, *CUT))
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
for i in range(int((KZ1 - KZ0) / 3)):                                            # the dormitory's ceiling: beams across,
    z = KZ0 + WT + 1.5 + i * 3                                                    # like the hall's -- cut short and carried
    x0, x1 = KX0 + WT - 0.3, KX1 - WT + 0.3                                       # on two trimmers at the stairwell
    while near_tower(x0, z, 0.3):
        x0 += 0.5
    while near_tower(x1, z, 0.3):
        x1 -= 0.5
    spans = [(x0, x1)] if not (HOLE[2] - 0.3 < z < HOLE[3] + 0.3) else [(x0, HOLE[0] - 0.1), (HOLE[1] + 0.1, x1)]
    for a, b in spans:
        add.cuboid([(a + b) / 2, EAVE - 0.62, z], [b - a, 0.45, 0.45], P["wood_dark"])
for x in (HOLE[0] - 0.33, HOLE[1] + 0.33):
    add.cuboid([x, EAVE - 0.62, (HOLE[2] + HOLE[3]) / 2], [0.45, 0.45, HOLE[3] - HOLE[2] + 3.6], P["wood_dark"])
plank_floor(KX0 + 0.2, KX1 - 0.2, KZ0 + 0.2, KZ1 - 0.2, EAVE, along="x", holes=[HOLE], rounds=TOWER_ROUNDS)   # sawn round the stairwell
for x in (HOLE[0] - 0.1, HOLE[1] + 0.1):                                        # a rail round the stairwell: along both
    for z in (HOLE[2] - 0.1, (HOLE[2] + HOLE[3]) / 2, HOLE[3] + 0.1):           # sides and across the far end, where the
        add.cuboid([x, EAVE + 0.45, z], [0.08, 0.9, 0.08], P["wood_dark"])     # stair is deep below; the near end, where
    add.cuboid([x, EAVE + 0.9, (HOLE[2] + HOLE[3]) / 2], [0.06, 0.06, HOLE[3] - HOLE[2] + 0.3], P["wood_dark"])   # the top
add.cuboid([HATCH[0], EAVE + 0.9, HOLE[3] + 0.1], [HOLE[1] - HOLE[0] + 0.3, 0.06, 0.06], P["wood_dark"])    # step is, is the way in
flush("palace: floors")

# the three corner towers: a door to the courtyard, doors into the hall
# and into the dormitory, a stair with landings, a lookout under a copper spire
PT_ARRIVE = []                                                       # where their stairs reach the lookouts
for cx, cz in PALACE_TOWERS:
    out_a = add.atan2(cz - (KZ0 + KZ1) / 2, cx - (KX0 + KX1) / 2)      # away from the palace
    in_a = out_a + add.pi                                            # into the palace
    stops = [(KY, in_a - 0.4, in_a + 0.4), (FLOOR2, in_a - 0.4, in_a + 0.4)]
    PT_ARRIVE.append(round_tower([cx, 0, cz], G - 1, EAVE + 4, TOWER_R2, doors=[(out_a, G), (in_a, KY), (in_a, FLOOR2)], walk=None,
                roof_h=9, roof_tiles="spire", slits=False,
                windows=[(out_a + 0.9, KY + 3, 0.7, 1.4), (out_a - 0.9, KY + 3, 0.7, 1.4),
                         (out_a, FLOOR2 + 1.2, 0.7, 1.4), (out_a + 1.0, EAVE + 0.6, 0.7, 1.4), (out_a - 1.0, EAVE + 0.6, 0.7, 1.4)],
                stops=stops))
    top = EAVE + 4 + 0.35 + 3.15 + 9                                 # the tip of its spire, the gold ball on it:
    add.cylinder([cx, top + 0.6, cz], [cx, top + 4.0, cz], 0.06, 8, P["iron"])     # a flagpole out of the ball,
    add.sphere([cx, top + 4.05, cz], 0.09, 6, P["gold"])                          # as on every tower but the chapel's
    flag([cx, top + 3.9, cz], 1.4, 1.0, add.pi * 0.3, phase=2.0 + 0.1 * (cx + cz))
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
DON_ARRIVE = a                                                                                  # where it comes out on the lookout
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
    for s in (-1, 1):                                                                 # (the braces' heads let into the ring beam)
        q = [DON[0] + (DON_R - 0.4) * add.cos(aa + s * 0.24), DON_TOP + 3.25, DON[1] + (DON_R - 0.4) * add.sin(aa + s * 0.24)]
        q = [px + (q[0] - px) * 1.2, DON_TOP + 2.2 + 1.05 * 1.2, pz + (q[2] - pz) * 1.2]
        add.beam([px, DON_TOP + 2.2, pz], q, 0.15, 0.15, P["wood_dark"])
add.pipe([DON[0], DON_TOP + 3.3, DON[1]], [DON[0], DON_TOP + 3.65, DON[1]], DON_R + 0.9, DON_R - 0.75, kk, P["wood_dark"])
cone_roof([DON[0], 0, DON[1]], DON_TOP + 3.65, DON_R + 0.9, 12, kk, colours="spire", size=TILE)   # tiled like the palace
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


def hip_roof(x0, x1, z0, z1, y, h, inset=INSET, over=OVER, cutters=(), dormers=(), north=None, blocked=None):
    """A hipped roof as a hollow shell ``ROOF_T`` thick -- the attic is a
    real room under it -- tiled outside, with walk-in dormers: a bay you
    step up into from the attic floor, a window in its face.  ``dormers``
    are where they stand along the south slope, ``north`` along the north
    one (the same as the south unless given)."""
    sides = [(x, 1) for x in dormers] + [(x, -1) for x in (dormers if north is None else north)]
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
    for x, sg in sides:                                                  # the bay of every dormer, cut through the shell
        zf = (ez1 - DORMER_IN) if sg > 0 else (ez0 + DORMER_IN)
        yf = y + h * DORMER_IN / (ez1 - zc)
        bays.append(add.make(add.cuboid, [x, yf + 1.4, zf - sg * (DORMER_D / 2 - 0.1)], [1.8, 2.8, DORMER_D - 0.2]))
    if cutters or bays:
        shell = add.difference(shell, *(list(cutters) + bays))
    add.mesh(shell)

    slope = h / (ez1 - zc)                                               # the long slopes rise this much per unit inwards
    d_eave, d_ridge = DORMER_IN + 2.5 / slope, DORMER_IN + 3.9 / slope   # a dormer's eaves and ridge run into them here

    def bay(xx, zz):                                                     # no slates under a dormer, nor where its roof meets the slope
        for dxr, sg in sides:
            if (zz > zc) != (sg > 0):
                continue
            deep = abs(zz - ez1) if sg > 0 else abs(zz - ez0)
            u = abs(xx - dxr)
            if DORMER_IN - 0.1 < deep < DORMER_IN + DORMER_D + 0.15 and u < 1.3:
                return True
            if d_eave - 0.6 < deep < d_ridge + 0.25 and u < 1.8 * min(1.0, (d_ridge + 0.25 - deep) / (d_ridge + 0.25 - d_eave)):
                return True
        return False

    keep_out = (lambda xx, zz: bay(xx, zz) or (blocked(xx, zz) if blocked else False))
    for face in (south, north, east, west):
        tile_face(*face, blocked=keep_out)
    add.cuboid([(x0 + x1) / 2, y + h, zc], [x1 - x0 - 2 * inset + 0.4, 0.3, 0.5], shade_of("spire", 2))   # ridge cap, in the tiles' colour
    for x, sg in sides:                                                  # the dormers, both sides
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
        # the dormer's roof runs back until it meets the slope of the main roof -- ridge and eaves both --
        # so that the rain runs off it; everything under the slope is cut away (3 cm under its surface)
        def zd(d, sg=sg):                                            # depth in from the eaves -> z
            return ez1 - d if sg > 0 else ez0 + d

        def under(p, sg=sg):                                         # a box whose top is sheared to just under the slope
            if p[1] < y - 5:
                return [p[0], y - 10, p[2]]
            return [p[0], y + slope * (ez1 - p[2] if sg > 0 else p[2] - ez0) - 0.03, p[2]]
        slope_cut = add.deform(add.make(add.cuboid, [x, y - 4, zd((DORMER_IN - 1 + d_ridge + 2) / 2)],
                                        [6, 8, d_ridge + 3 - DORMER_IN]), under)
        d_front = DORMER_IN - 0.3                                    # the roof starts 0.3 out from the face, as before
        gable = add.make(add.prism, [[-1.55, 0], [1.55, 0], [0, 1.4]], d_ridge + 0.3 - d_front, P["spire"],
                         (x, yf + 2.5, zd((d_front + d_ridge + 0.3) / 2)), (0, 0, 1))
        add.mesh(add.difference(gable, slope_cut))
        for side in (-1, 1):                                         # tiles on both slopes, as on the roof itself:
            q = [[x + side * 1.55, yf + 2.5, zd(d_front)], [x + side * 1.55, yf + 2.5, zd(d_eave)],   # eaves,
                 [x, yf + 3.9, zd(d_ridge)], [x, yf + 3.9, zd(d_front)]]                          # ridge
            if vcross(vsub(q[1], q[0]), vsub(q[3], q[0]))[1] < 0:  # (listed so that the face looks up)
                q = [q[1], q[0], q[3], q[2]]
            tile_face(*q)
        g = [[x - 1.55, yf + 2.5, zd(d_front)], [x + 1.55, yf + 2.5, zd(d_front)], [x, yf + 3.9, zd(d_front)]]
        if sg < 0:                                                   # the gable over the window: tiled too,
            g = [g[1], g[0], g[2]]                                   # facing out over the eaves
        tile_face(g[0], g[1], g[2], g[2])
        add.cuboid([x, yf + 3.9, zd((d_front + d_ridge + 0.3) / 2)], [0.4, 0.26, d_ridge + 0.3 - d_front],
                   shade_of("spire", 2))                             # and a ridge cap, into the roof at the back
        back = DORMER_IN + DORMER_D - 0.15                               # the side walls carried on under its eaves, from inside
        cheeks = add.make(add.cuboid, [x, yf + 2.0, zd((back + d_eave + 0.3) / 2)], [2.4, 1.0, d_eave + 0.3 - back], P["mortar"])
        add.mesh(add.difference(cheeks, slope_cut))                      # the back wall to where the eaves meet the slope
        add.push()                                                   # glass, mid-wall, in a frame all the way round
        window_frame({"x": 0, "y0": 0, "y1": 1.7, "w": 1.2, "arched": True, "kind": "window"}, 0.4)
        add.mesh(add.move(add.pop(), [x, yf + 0.55, zf - sg * 0.15]))   # with a mullion and a transom, as below
        add.cuboid([x, yf + 0.55, zf - sg * 0.5], [1.6, 0.1, 1.0], P["stone_dark"])       # the sill ledge inside
        rise = (yf - y) / 3
        for i in range(3):                                           # three steps up from the attic floor into the bay
            add.cuboid([x, y + (i + 1) * rise / 2, zb - sg * (0.35 * (2 - i) + 0.175)], [1.6, (i + 1) * rise, 0.35], shade_of("wood", i))


def arch_solid(cx, y0, w, h, z, depth):
    """An arched opening (like a doorway) as a solid, to cut through a
    wall along z: ``w`` wide, ``h`` tall on ``y0``, centred on (cx, z)."""
    return add.make(add.prism, [[sx, sy] for sx, sy in arch_profile(y0, w, h)], depth, None, (cx, 0, z), (0, 0, 1))


PALACE_DORMERS = (-12, 0, 12)                                                          # the south slope, and the north:
PALACE_DORMERS_N = (-12, 12)          # none in the middle, where the stair comes up into the attic -- turn left or right
hip_roof(KX0, KX1, KZ0, KZ1, EAVE, ROOF_H, cutters=tower_cutters(EAVE - 1, RIDGE_Y + 2), dormers=PALACE_DORMERS,
         north=PALACE_DORMERS_N, blocked=lambda x, z: near_tower(x, z, 0.4))
# the chimney of the great hall's fireplace, on the west wall, through the roof
CHIM_X, CHIM_Z = KX0 + 1.0, (KZ0 + KZ1) / 2
brick_box([CHIM_X, (EAVE + EAVE + 6.5) / 2, CHIM_Z], [1.6, 6.5, 2.0], flue=(0.7, 0.9, 1.5))
chimney_cap([CHIM_X, EAVE + 6.65, CHIM_Z], 2.0, 2.4, 0.3, (0.7, 0.9))                   # the flue open at the top
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
# the porch over the main door: two columns on pedestals beside the steps (not on them), an entablature round
# three sides, a pediment with the arms, and a gabled roof of the palace's tiles running back to the wall
PZ = KZ1 + PL + 2.7                                                          # the line of the columns
for s in (-1, 1):
    add.cuboid([s * 3.4, (G + KY) / 2, PZ], [0.95, KY - G, 0.95], P["stone_dark"])                 # a pedestal on the ground,
    add.cuboid([s * 3.4, KY + 0.06, PZ], [0.85, 0.12, 0.85], P["stone"])                          # the column's base,
    add.torus([s * 3.4, KY + 0.17, PZ], 0.34, 0.06, k_(14), 6, P["stone"])
    add.column([s * 3.4, KY + 0.12, PZ], 4.66, 0.3, P["stone"], k_(14))                             # its shaft
    add.torus([s * 3.4, KY + 4.62, PZ], 0.32, 0.05, k_(14), 6, P["stone"])                          # and capital
    add.frustum([s * 3.4, KY + 4.62, PZ], [s * 3.4, KY + 4.8, PZ], 0.3, 0.42, k_(14), P["stone"])
    add.cuboid([s * 3.4, KY + 4.86, PZ], [0.9, 0.12, 0.9], P["stone"])
    add.cuboid([s * 3.4, KY + 5.2, (KZ1 + 0.3 + PZ + 0.45) / 2], [0.7, 0.56, PZ + 0.45 - KZ1 - 0.3], P["stone"])   # the side beams
add.cuboid([0, KY + 5.2, PZ], [7.7, 0.56, 0.7], P["stone"])                                       # the architrave, and the cornice
add.cuboid([0, KY + 5.55, PZ + 0.05], [8.1, 0.14, 0.95], P["stone_dark"])
RIDGE_P, EAVE_P = KY + 7.3, KY + 5.62
tri = [[-4.05, EAVE_P], [4.05, EAVE_P], [0, RIDGE_P]]                                              # the pediment
add.mesh(add.make(add.prism, tri, 0.5, P["stone"], (0, 0, PZ), (0, 0, 1)))
add.mesh(add.move(add.make(arms, 0.8, 1.0, 0.04), [-0.4, EAVE_P + 0.18, PZ + 0.25]))
for sg in (-1, 1):                                                                                 # the roof: boards, and tiles
    A, B = [sg * 4.35, EAVE_P - 0.12, PZ + 0.55], [sg * 4.35, EAVE_P - 0.12, KZ1 + 0.3]
    C, D = [0, RIDGE_P + 0.12, KZ1 + 0.3], [0, RIDGE_P + 0.12, PZ + 0.55]
    add.mesh(slab([A, B, C, D] if sg > 0 else [B, A, D, C], 0.12, P["wood_dark"]))
    lift = [[q[0], q[1] + 0.12, q[2]] for q in (A, B, C, D)]
    q = lift if vcross(vsub(lift[1], lift[0]), vsub(lift[3], lift[0]))[1] > 0 else [lift[1], lift[0], lift[3], lift[2]]
    tile_face(*q)
add.cuboid([0, RIDGE_P + 0.3, (PZ + 0.55 + KZ1 + 0.3) / 2], [0.4, 0.26, PZ + 0.25 - KZ1], shade_of("spire", 2))   # its ridge cap
add.cuboid([0, EAVE_P - 0.05, (PZ + KZ1 + 0.3) / 2], [6.3, 0.06, PZ - KZ1 - 0.35], P["wood_dark"])   # a ceiling of boards under it
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
# the roof: a hollow shell ROOF_T thick like the palace's (slates outside,
# boards inside) over an attic, between two gables of stone
CH_EW = (CH_X1 - CH_X0 + 1.0) / 2 + 0.4                   # the eaves stand this far out from the ridge line
CH_RH = 7.0                                              # the ridge, above the wall tops
CH_ZA = CH_C[1] - (CH_Z1 - CH_Z0 + 1.0) / 2 - 0.4        # the ends of the roof
CH_ZB = CH_C[1] + (CH_Z1 - CH_Z0 + 1.0) / 2 + 0.4
CH_S = CH_RH / CH_EW                                     # the pitch: rise per metre
CH_IN = CH_RH - ROOF_T * add.sqrt(1 + CH_S * CH_S)       # the underside of the boards: its ridge above the wall tops ...
CH_IW = CH_IN / CH_S                                     # ... and how far out it comes down to them
CH_WIN = (1.3, 3.2, 3.0)                                 # the gable windows: sill above the wall tops, width, height
SURR = 0.35                                              # the band of dressed stones round them
# the attic is entered from the dormitory, through the palace wall under
# the west slope where the roof is low: a dormer over that door gives the
# headroom -- a small gabled roof from the palace wall into the slope
CH_DOOR = (1.4, 2.6)                                     # that door: width, height (on the dormitory floor)
DM_I, DM_W = 0.8, 1.5                                    # the dormer: half the passage inside, half its cheeks outside
DM_RI = FLOOR2 + CH_DOOR[1] + 1.15                       # the ridge of its ceiling, high enough that the door's arch
                                                         # and its voussoirs stay under it ...
DM_RO = DM_RI + ROOF_T * add.sqrt(2)                     # ... and of its roof (45 degrees), whose eaves
DM_EAVE = DM_W + 0.15                                    # stand out a little over the cheeks
TUR = (CH_X1 + 0.5, CH_Z1 + 0.5)                         # the little tower: a round turret at the south-east corner
TUR_R = 1.5
TUR_TOP = CH_TOP + 6.5


def dormer_valley(dz):
    """Where the dormer's roof runs into the chapel's west slope, ``dz``
    from its ridge line: the x of the valley."""
    return CH_C[0] - (CH_TOP + CH_RH - (DM_RO - abs(dz))) / CH_S


ch_shell = add.Mesh()
for sg in (-1, 1):
    e_x, i_x = CH_C[0] + sg * CH_EW, CH_C[0] + sg * CH_IW
    ch_shell.add_polygon([[e_x, CH_TOP, CH_ZA], [e_x, CH_TOP, CH_ZB], [CH_C[0], CH_TOP + CH_RH, CH_ZB], [CH_C[0], CH_TOP + CH_RH, CH_ZA]], P["slate"])
    ch_shell.add_polygon([[i_x, CH_TOP, CH_ZA], [i_x, CH_TOP, CH_ZB], [CH_C[0], CH_TOP + CH_IN, CH_ZB], [CH_C[0], CH_TOP + CH_IN, CH_ZA]], P["wood_dark"])
    ch_shell.add_polygon([[e_x, CH_TOP, CH_ZA], [i_x, CH_TOP, CH_ZA], [i_x, CH_TOP, CH_ZB], [e_x, CH_TOP, CH_ZB]], P["wood_dark"])   # the soffit
    for z in (CH_ZA, CH_ZB):                                                                                # the verges
        ch_shell.add_polygon([[e_x, CH_TOP, z], [CH_C[0], CH_TOP + CH_RH, z], [CH_C[0], CH_TOP + CH_IN, z], [i_x, CH_TOP, z]], P["wood_dark"])
passage = add.make(add.prism, [[CH_TOP, CH_C[1] - DM_I], [CH_TOP, CH_C[1] + DM_I], [DM_RI - DM_I, CH_C[1] + DM_I], [DM_RI, CH_C[1]],
                               [DM_RI - DM_I, CH_C[1] - DM_I]], 5.0, P["wood_dark"], (KX1 + 2.5, 0, 0), (1, 0, 0))   # [y, z] along x
add.mesh(add.difference(add.fix_normals(add.clean(ch_shell)), passage))                   # the way through the slope
dormer = add.make(add.prism, [[CH_TOP, CH_C[1] - DM_W], [CH_TOP, CH_C[1] + DM_W], [DM_RI - DM_W, CH_C[1] + DM_W],
                              [DM_RI - DM_EAVE, CH_C[1] + DM_EAVE], [DM_RO - DM_EAVE, CH_C[1] + DM_EAVE], [DM_RO, CH_C[1]],
                              [DM_RO - DM_EAVE, CH_C[1] - DM_EAVE], [DM_RI - DM_EAVE, CH_C[1] - DM_EAVE], [DM_RI - DM_W, CH_C[1] - DM_W]],
                  4.5, P["slate"], (KX1 + WT / 2 + 2.25, 0, 0), (1, 0, 0))                # from the palace wall's core outwards
assert KX1 + WT / 2 + 4.5 > dormer_valley(0) + 0.5                                  # (on past where its ridge meets the slope)
below = add.make(add.prism, [[KX1 - 1.0, CH_TOP - 4.0], [CH_C[0], CH_TOP - 4.0], [CH_C[0], CH_TOP + CH_RH],
                             [KX1 - 1.0, CH_TOP + CH_RH - CH_S * (CH_C[0] - KX1 + 1.0)]], 4.0, None, (0, 0, CH_C[1]), (0, 0, 1))


def dormer_colour(q):
    """Boards inside the dormer (its ceiling and the inner faces of its
    cheeks), slate outside."""
    dz = abs(q[2] - CH_C[1])
    inside = (dz < DM_I + 1e-3 and abs(q[1] - (DM_RI - dz)) < 0.02) or (abs(dz - DM_I) < 1e-3 and q[1] < DM_RI - DM_I + 0.01)
    return P["wood_dark"] if inside else P["slate"]


add.mesh(add.color_by(add.difference(dormer, passage, below), dormer_colour))         # only what stands above the slope


def chapel_tiles_off(x, z):
    """No slates under the dormer, nor inside the turret."""
    dz = z - CH_C[1]
    if abs(dz) < DM_EAVE + 0.1 and x < dormer_valley(min(abs(dz), DM_EAVE)) + 0.15:
        return True
    return (x - TUR[0]) ** 2 + (z - TUR[1]) ** 2 < (TUR_R + 0.25) ** 2


for sg in (-1, 1):                                                              # slates on both slopes
    eave_x = CH_C[0] + sg * CH_EW
    A, B = [eave_x, CH_TOP, CH_ZB if sg > 0 else CH_ZA], [eave_x, CH_TOP, CH_ZA if sg > 0 else CH_ZB]
    D, C = [CH_C[0], CH_TOP + CH_RH, A[2]], [CH_C[0], CH_TOP + CH_RH, B[2]]
    tile_face(A, B, C, D, blocked=chapel_tiles_off, size=(0.45, 0.4), colours="slate")
for sg in (-1, 1):                                                              # and on the dormer, from the palace wall to the valleys
    A = [KX1 + WT / 2 + 0.22, DM_RO - DM_EAVE, CH_C[1] + sg * DM_EAVE]
    B = [dormer_valley(DM_EAVE), DM_RO - DM_EAVE, CH_C[1] + sg * DM_EAVE]
    C, D = [dormer_valley(0), DM_RO, CH_C[1]], [KX1 + WT / 2 + 0.22, DM_RO, CH_C[1]]
    if vcross(vsub(B, A), vsub(D, A))[1] < 0:                                   # (listed so that the face looks up)
        A, B, C, D = B, A, D, C
    tile_face(A, B, C, D, size=(0.45, 0.4), colours="slate")
    add.polyline([[B[0] + 0.05, B[1] + 0.02, B[2]], [C[0], C[1] + 0.02, C[2]]], 0.1, 6, P["iron"])   # lead in the valley
    add.beam([KX1 + WT / 2 + 0.28, DM_RO + 0.06, CH_C[1] + sg * 0.02],                 # and a lead flashing where the
             [KX1 + WT / 2 + 0.28, DM_RO - DM_EAVE + 0.06, CH_C[1] + sg * DM_EAVE], 0.14, 0.12, P["iron"])  # slates meet the wall
add.cuboid([(KX1 + WT / 2 + dormer_valley(0)) / 2 + 0.05, DM_RO + 0.1, CH_C[1]],      # the dormer's ridge cap, from the wall
           [dormer_valley(0) - KX1 - WT / 2 + 0.1, 0.22, 0.34], shade_of("slate", 2))  # into the slope
add.cuboid([CH_X1 + 0.3, CH_TOP - 0.3, CH_C[1]], [0.6, 0.6, CH_Z1 - CH_Z0 + 1.0], P["stone_dark"])   # cornice


def chapel_gable(zc, out, a0, sd):
    """One gable of the chapel, on its wall at z = zc (``out``: the outward
    side, +1 or -1): a mortar core up to the underside of the roof with a
    triangular window of stained glass in it, dressed stones round the
    window on both faces, and the courses of stone blocks of the wall below
    carried on up (``a0``, ``sd``: where that wall starts and which way it
    runs, so the joints line up) and cut along the rakes."""
    xc, T = CH_C[0], CH_TOP
    ws, wb, wh = CH_WIN
    m = wh / (wb / 2)

    def unit(a, b, c):
        L = add.sqrt(a * a + b * b)
        return a / L, b / L, c / L

    def meet(e1, e2, d):                                                     # where two edges meet, both moved out by d
        det = e1[0] * e2[1] - e2[0] * e1[1]
        return ((e1[2] + d) * e2[1] - (e2[2] + d) * e1[1]) / det, (e1[0] * (e2[2] + d) - e2[0] * (e1[2] + d)) / det

    def lerp(p, q, t):
        return p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t

    # the window: a*x + b*y <= c for its sill, its left and its right edge
    edges = [unit(0, -1, -(T + ws)), unit(-m, 1, T + ws - m * (xc - wb / 2)), unit(m, 1, T + ws + m * (xc + wb / 2))]
    W = [meet(edges[0], edges[1], 0), meet(edges[0], edges[2], 0), meet(edges[1], edges[2], 0)]   # sill left, sill right, apex
    S = [meet(edges[0], edges[1], SURR), meet(edges[0], edges[2], SURR), meet(edges[1], edges[2], SURR)]
    # the core: the gable less the window, in four convex pieces
    core = clip_half([(xc - CH_IW, T), (xc + CH_IW, T), (xc, T + CH_IN)], -1, 0, -(KX1 + WT / 2))
    band = clip_half(clip_half(core, 0, -1, -W[0][1]), 0, 1, W[2][1])
    for piece in [clip_half(core, 0, 1, W[0][1]), clip_half(core, 0, -1, -W[2][1])] + [clip_half(band, -e[0], -e[1], -e[2]) for e in edges[1:]]:
        if len(piece) > 2 and abs(poly_area(piece)) > 1e-4:
            add.prism(piece, WT, P["mortar"], (0, 0, zc), (0, 0, 1))
    # both faces: the courses of blocks, fitted round the surround, and the surround
    cuts = [(0, -1, -S[2][1]), (0, 1, S[0][1])] + [(-e[0], -e[1], -e[2] - SURR) for e in edges[1:]]
    for side, seed in ((out, 12), (-out, 19)):
        zf = zc + side * (WT / 2 + 0.11)
        k = 0
        while k * BLOCK[1] < CH_IN:
            j = int(round((CH_TOP - KY) / BLOCK[1])) + k                          # the course, counted from the floor
            y0, y1 = T + k * BLOCK[1], T + (k + 1) * BLOCK[1]
            lx = -(BLOCK[0] / 2 if j % 2 else 0.0) - 2 * BLOCK[0]
            while lx < 15:
                xa, xb = sorted((a0 + sd * lx, a0 + sd * (lx + BLOCK[0])))
                rest = [(xa, y0), (xb, y0), (xb, y1), (xa, y1)]
                for a, b, c in ((-1, 0, -(KX1 + WT / 2 + 0.22)), (0, -1, -T), (-CH_S, 1, T + CH_IN - CH_S * xc), (CH_S, 1, T + CH_IN + CH_S * xc)):
                    rest = clip_half(rest, a, b, c)                           # within the gable, clear of the palace wall
                pieces = []
                for a, b, c in cuts:                                          # the part beyond each side of the surround,
                    if len(rest) < 3:                                         # and what is left to cut
                        break
                    pieces.append(clip_half(rest, a, b, c))
                    rest = clip_half(rest, -a, -b, -c)
                for piece in pieces:
                    stone = shrunk(piece, 0.03) if len(piece) > 2 else None
                    if stone is None:
                        continue
                    area = abs(poly_area(stone))
                    rim = sum(add.sqrt((stone[i][0] - stone[i - 1][0]) ** 2 + (stone[i][1] - stone[i - 1][1]) ** 2) for i in range(len(stone)))
                    if area > 0.02 and 2 * area / rim > 0.05:                  # no slivers
                        add.prism(stone, 0.22, pick("stone", lx + seed * 97, j + seed), (0, 0, zf), (0, 0, 1))
                lx += BLOCK[0]
            k += 1
        for e, ((p, q), (p2, q2)) in enumerate((((W[0], W[1]), (S[0], S[1])), ((W[1], W[2]), (S[1], S[2])), ((W[2], W[0]), (S[2], S[0])))):
            n = max(2, int(round(add.sqrt((q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2) / 0.55)))
            for i in range(n):                                                # dressed stones round the window
                stone = shrunk([lerp(p, q, i / float(n)), lerp(p, q, (i + 1) / float(n)), lerp(p2, q2, (i + 1) / float(n)), lerp(p2, q2, i / float(n))], 0.015)
                if stone:
                    add.prism(stone, 0.1, shade_of("stone", i + e), (0, 0, zc + side * (WT / 2 + 0.05)), (0, 0, 1))
    add.cuboid([xc, W[0][1] - 0.1, zc + out * (WT / 2 + 0.1)], [wb + 0.5, 0.2, 0.5], P["stone_dark"])       # the sill outside
    # the stained glass: the triangle cut into n x n small triangles of coloured glass, leaded
    G = [meet(edges[0], edges[1], -0.03), meet(edges[0], edges[2], -0.03), meet(edges[1], edges[2], -0.03)]
    n = 8

    def at(i, j):
        return (G[0][0] + (G[1][0] - G[0][0]) * i / n + (G[2][0] - G[0][0]) * j / n,
                G[0][1] + (G[1][1] - G[0][1]) * i / n + (G[2][1] - G[0][1]) * j / n)
    for i in range(n):
        for j in range(n - i):
            add.prism([at(i, j), at(i + 1, j), at(i, j + 1)], 0.04, STAINED[int(hash2(i, j, 41 + out) * 5) % 5], (0, 0, zc), (0, 0, 1))
            if i + j < n - 1:
                add.prism([at(i + 1, j), at(i + 1, j + 1), at(i, j + 1)], 0.04, STAINED[int(hash2(i, j, 44 + out) * 5) % 5], (0, 0, zc), (0, 0, 1))
    for k in range(1, n):                                                     # the lead cames, three ways
        for p, q in ((at(0, k), at(n - k, k)), (at(k, 0), at(k, n - k)), (at(k, 0), at(0, k))):
            add.beam([p[0], p[1], zc], [q[0], q[1], zc], 0.06, 0.03, P["black"])
    F = [meet(edges[0], edges[1], -0.03 - FRAME / 2), meet(edges[0], edges[2], -0.03 - FRAME / 2), meet(edges[1], edges[2], -0.03 - FRAME / 2)]
    for i in range(3):                                                        # the frame, each side run on to close the corners
        p, q = F[i], F[(i + 1) % 3]
        L = add.sqrt((q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2)
        d = ((q[0] - p[0]) / L, (q[1] - p[1]) / L)
        ends = []
        for v, u, w in ((p, q, F[(i + 2) % 3]), (q, p, F[(i + 2) % 3])):      # the corner's angle, from its two sides
            a = ((u[0] - v[0], u[1] - v[1]), (w[0] - v[0], w[1] - v[1]))
            cos_t = (a[0][0] * a[1][0] + a[0][1] * a[1][1]) / add.sqrt((a[0][0] ** 2 + a[0][1] ** 2) * (a[1][0] ** 2 + a[1][1] ** 2))
            ends.append(FRAME / 2 * add.sqrt((1 + cos_t) / (1 - cos_t)))      # half the section / tan(half the angle)
        add.beam([p[0] - d[0] * ends[0], p[1] - d[1] * ends[0], zc], [q[0] + d[0] * ends[1], q[1] + d[1] * ends[1], zc],
                 0.14, FRAME, P["glass_frame"])


chapel_gable(CH_Z0, -1, CH_X1, -1)                                              # north, over the altar
chapel_gable(CH_Z1, 1, CH_X0, 1)                                                # south, over the door
# the turret: a drum of stone blocks from the ground, a cornice, and a spire
# of clay tiles like the palace towers', with a gold ball and a cross
add.cylinder([TUR[0], G - 0.5, TUR[1]], [TUR[0], TUR_TOP, TUR[1]], TUR_R, k_(24), P["mortar"])
stone_ring(TUR[0], TUR[1], TUR_R, G - 0.5, TUR_TOP - 0.5)
add.cylinder([TUR[0], TUR_TOP - 0.5, TUR[1]], [TUR[0], TUR_TOP, TUR[1]], TUR_R + 0.35, k_(24), P["stone_dark"])
cone_roof([TUR[0], 0, TUR[1]], TUR_TOP, TUR_R + 0.45, 8.0, k_(24), colours="spire", size=TILE)
add.cuboid([TUR[0], TUR_TOP + 9.3, TUR[1]], [0.1, 1.4, 0.1], P["gold"])                          # the cross
add.cuboid([TUR[0], TUR_TOP + 9.6, TUR[1]], [0.7, 0.1, 0.1], P["gold"])
flush("chapel")


# --------------------------------------------------------------------------
#  5. Props: furniture, food, vessels, weapons -- everything is built at
#     the origin and then moved into place
# --------------------------------------------------------------------------
def goblet(at, color=None, wine=False, s=LIFE):
    """A goblet on a stem -- a real cup, hollow, with wine in it if poured
    -- 20 cm high and 10 across, times ``s`` (the people's scale; the
    treasure's chalices are bigger)."""
    lathe([[0.0, 0.0], [0.045, 0.0], [0.045, 0.008], [0.014, 0.022], [0.012, 0.085], [0.024, 0.105], [0.048, 0.13],
           [0.052, 0.2], [0.046, 0.2], [0.043, 0.135], [0.0, 0.125]], at, k_(8), color or P["gold"], s)
    add.sphere([at[0], at[1] + 0.085 * s, at[2]], 0.02 * s, 3, color or P["gold"])              # a knop on the stem
    if wine:
        add.cylinder([at[0], at[1] + 0.16 * s, at[2]], [at[0], at[1] + 0.175 * s, at[2]], 0.043 * s, k_(8), P["cushion"])


def jug(at, color=None, s=0.55):
    color = color or P["brick"]
    lathe([[0.0, 0], [0.16, 0], [0.24, 0.15], [0.26, 0.35], [0.18, 0.5], [0.15, 0.6], [0.17, 0.66],
           [0.12, 0.66], [0.11, 0.55], [0.0, 0.5]], at, k_(8), color, s)
    add.torus([at[0] + 0.24 * s, at[1] + 0.4 * s, at[2]], 0.13 * s, 0.03 * s, k_(8), 8, color, axis=(0, 0, 1))


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
    """A pewter plate with a raised rim; its floor is 0.03 above ``at``."""
    lathe([[0.0, 0], [r * 0.8, 0], [r, 0.045], [r * 0.92, 0.05], [r * 0.78, 0.03], [0.0, 0.03]], at, k_(10), P["steel"])


def garnish(at, r, n=10, seed=0, rz=None):
    """Green leaves and herbs laid in a ring (an oval, with ``rz``) on the
    floor of a dish."""
    for i in range(n):
        a = 2 * add.pi * (i + 0.5 * hash2(i, seed, 71)) / n
        leaf = add.make(add.ellipsoid, [0, 0, 0], [0.09, 0.012, 0.05], 2, P["leaf"] if i % 3 else P["grass"])
        add.mesh(add.move(add.rotateY(leaf, -a), [at[0] + r * add.cos(a), at[1] + 0.012, at[2] + (rz or r) * add.sin(a)]))


def chicken_roast(at):
    """A roast chicken on a dish: a golden breast, the drumsticks with bone
    ends in paper frills, the wings folded, herbs round it."""
    plate(at, 0.42)
    x, y, z = at[0], at[1] + 0.03, at[2]
    add.ellipsoid([x, y + 0.15, z], [0.19, 0.14, 0.24], 4, P["bread"])                          # the body
    add.ellipsoid([x, y + 0.2, z - 0.05], [0.14, 0.1, 0.16], 3, P["bread"])                     # the breast
    for s in (-1, 1):
        add.ellipsoid([x + s * 0.17, y + 0.17, z - 0.08], [0.045, 0.08, 0.12], 2, P["meat"])     # a wing, folded
        add.capsule([x + s * 0.11, y + 0.1, z + 0.12], [x + s * 0.15, y + 0.2, z + 0.3], 0.06, 10, P["meat"])   # a drumstick
        add.cylinder([x + s * 0.15, y + 0.2, z + 0.3], [x + s * 0.16, y + 0.24, z + 0.38], 0.018, 5, P["bone"])
        add.cone([x + s * 0.16, y + 0.24, z + 0.38], [x + s * 0.165, y + 0.27, z + 0.44], 0.03, 6, P["white"])   # a frill
    garnish([x, y, z], 0.29, 8, int(x * 7 + z))


def bread(at, n=1):
    """Loaves of bread: long ones with slashes across the crust, round ones
    scored with a cross."""
    for i in range(n):
        x, y, z = at[0] + 0.25 * i, at[1], at[2] + 0.1 * i
        if i % 2 == 0:
            loaf = add.stretch(add.make(add.sphere, [0, 0, 0], 0.22, 8, P["bread"]), [1.5, 0.7, 1.0], (0, 0, 0))
            for dx in (-0.16, 0.0, 0.16):
                cut = add.make(add.ellipsoid, [0, 0, 0], [0.028, 0.02, 0.1], 2, P["linen"])
                loaf.extend(add.move(add.rotateY(cut, 0.6), [dx, 0.146, 0]))
        else:
            loaf = add.stretch(add.make(add.sphere, [0, 0, 0], 0.2, 8, P["bread"]), [1.0, 0.65, 1.0], (0, 0, 0))
            for a in (0.0, add.pi / 2):
                cut = add.make(add.ellipsoid, [0, 0, 0], [0.13, 0.018, 0.025], 2, P["linen"])
                loaf.extend(add.move(add.rotateY(cut, a), [0, 0.126, 0]))
        add.mesh(add.move(add.rotateY(loaf, i * 0.7), [x, y + (0.15 if i % 2 == 0 else 0.127), z]))


def cheese(at):
    """A wheel of cheese on a board with a wedge cut from it, the wedge
    lying by it and the knife stuck in the wheel."""
    add.cylinder([at[0] + 0.15, at[1], at[2]], [at[0] + 0.15, at[1] + 0.03, at[2]], 0.5, k_(10), P["wood_light"])   # the board
    add.mesh(add.move(add.make(add.revolve, lambda t: [0.32, 0.22 * t], [0, 0, 0], [0, 1, 0], 0, 1, 1, k_(10),
                               P["cheese"], 2 * add.pi * 0.8), [at[0], at[1] + 0.03, at[2]]))
    add.mesh(add.move(add.make(add.prism, [[0, 0], [0.3, -0.1], [0.3, 0.1]], 0.2, P["cheese"], (0, 0, 0)),
                      [at[0] + 0.55, at[1] + 0.13, at[2] + 0.3]))
    add.mesh(add.move(add.rotateZ(add.make(add.prism, [[0, 0], [0.22, 0.0], [0.2, 0.04], [0, 0.035]], 0.006, P["steel"], (0, 0, 0), (0, 0, 1)), -1.1),
                      [at[0] - 0.05, at[1] + 0.33, at[2] - 0.1]))                                                   # the knife ...
    add.cylinder([at[0] - 0.05, at[1] + 0.33, at[2] - 0.1], [at[0] - 0.1, at[1] + 0.44, at[2] - 0.1], 0.018, 6, P["wood_dark"])   # ... its haft


def grapes(at, n=12):
    for i in range(n):
        a = 2.4 * i
        rr = 0.12 * (1 - i / float(n)) + 0.02
        add.sphere([at[0] + rr * add.cos(a), at[1] + 0.25 - 0.018 * i, at[2] + rr * add.sin(a)], 0.045, 5, P["grape"])
    add.cylinder([at[0], at[1] + 0.25, at[2]], [at[0] + 0.1, at[1] + 0.35, at[2]], 0.01, 4, P["leaf_dark"])


def fruit(at, color, r=0.12):
    add.sphere([at[0], at[1] + r, at[2]], r, 8, color)


def platter(at, rx, rz):
    """An oval pewter platter with a raised rim (its floor 0.03 up)."""
    dish = add.make(lathe, [[0.0, 0], [0.78, 0], [1.0, 0.05], [0.93, 0.055], [0.76, 0.03], [0.0, 0.03]], [0, 0, 0], k_(12), P["steel"])
    add.mesh(add.move(add.stretch(dish, [rx, 1.0, rz], (0, 0, 0)), at))


def fish_platter(at):
    """A great fish baked golden on an oval platter, lying on its side,
    with slices of lemon along it and herbs round it."""
    platter(at, 0.34, 0.5)
    M = add.make(fish, [0, 0, 0], 0, P["bread"], 0.34)
    add.mesh(add.move(add.rotateY(add.rotateX(M, add.pi / 2), add.pi / 2), [at[0], at[1] + 0.1, at[2]]))
    for i in range(4):
        add.cylinder([at[0] + 0.1, at[1] + 0.12, at[2] - 0.2 + 0.13 * i], [at[0] + 0.1, at[1] + 0.135, at[2] - 0.2 + 0.13 * i], 0.04, 8, P["cheese"])
    garnish([at[0], at[1] + 0.035, at[2]], 0.3, 8, seed=int(at[2] * 10))


def pie(at):
    """A pie in its dish: a golden crust with a lattice over the dark red
    of the cherries."""
    add.frustum([at[0], at[1], at[2]], [at[0], at[1] + 0.08, at[2]], 0.19, 0.22, k_(10), P["steel"])
    add.frustum([at[0], at[1] + 0.02, at[2]], [at[0], at[1] + 0.1, at[2]], 0.2, 0.21, k_(10), P["bread"])
    add.cylinder([at[0], at[1] + 0.1, at[2]], [at[0], at[1] + 0.105, at[2]], 0.19, k_(10), P["cushion"])
    for i in range(5):
        for horizontal in (True, False):
            d = -0.16 + 0.08 * i
            w = 2 * add.sqrt(0.19 ** 2 - d * d)
            size = [w, 0.02, 0.03] if horizontal else [0.03, 0.02, w]
            add.cuboid([at[0] + (0 if horizontal else d), at[1] + 0.112, at[2] + (d if horizontal else 0)], size, P["bread"])


def ham(at):
    """A baked ham on a board, the bone sticking out with a paper frill, a
    slice cut and the carving knife beside it."""
    add.cuboid([at[0], at[1] + 0.015, at[2]], [0.42, 0.03, 0.7], P["wood_light"])
    M = add.make(add.ellipsoid, [0, 0, 0], [0.15, 0.12, 0.23], 5, P["meat"])
    add.mesh(add.move(add.rotateX(M, -0.2), [at[0], at[1] + 0.14, at[2] - 0.05]))
    add.cylinder([at[0], at[1] + 0.17, at[2] + 0.12], [at[0], at[1] + 0.22, at[2] + 0.32], 0.025, 8, P["bone"])
    add.sphere([at[0], at[1] + 0.23, at[2] + 0.34], 0.035, 3, P["bone"])
    add.frustum([at[0], at[1] + 0.2, at[2] + 0.25], [at[0], at[1] + 0.21, at[2] + 0.28], 0.04, 0.03, 8, P["white"])
    add.cylinder([at[0] + 0.12, at[1] + 0.03, at[2] - 0.28], [at[0] + 0.12, at[1] + 0.045, at[2] - 0.28], 0.08, 10, P["pig"])   # a slice
    add.cuboid([at[0] - 0.16, at[1] + 0.04, at[2] + 0.0], [0.02, 0.01, 0.3], P["steel"])                                         # the knife
    add.cuboid([at[0] - 0.16, at[1] + 0.045, at[2] + 0.2], [0.03, 0.02, 0.1], P["wood_dark"])


def sausages(at):
    """Sausages, fried brown, on a plate with a pot of mustard."""
    plate(at, 0.28)
    for i in range(4):
        a = 0.5 + i * 0.45
        c = [at[0] + 0.02 * i - 0.03, at[1] + 0.07, at[2] - 0.12 + 0.08 * i]
        add.capsule([c[0] - 0.13 * add.cos(a), c[1], c[2] - 0.05 * add.sin(a)], [c[0] + 0.13 * add.cos(a), c[1], c[2] + 0.05 * add.sin(a)], 0.035, 8, P["meat"])
    add.cylinder([at[0] + 0.33, at[1], at[2] + 0.2], [at[0] + 0.33, at[1] + 0.09, at[2] + 0.2], 0.045, 8, P["white"])
    add.cylinder([at[0] + 0.33, at[1] + 0.09, at[2] + 0.2], [at[0] + 0.33, at[1] + 0.095, at[2] + 0.2], 0.04, 8, P["cheese"])


def cake(at):
    """A round cake with white icing and red berries on top."""
    plate(at, 0.3)
    add.cylinder([at[0], at[1] + 0.03, at[2]], [at[0], at[1] + 0.14, at[2]], 0.22, k_(10), P["bread"])
    add.cylinder([at[0], at[1] + 0.14, at[2]], [at[0], at[1] + 0.17, at[2]], 0.225, k_(10), P["white"])
    add.torus([at[0], at[1] + 0.17, at[2]], 0.2, 0.02, k_(10), 4, P["white"])
    for i in range(8):
        a = i * add.pi / 4
        add.sphere([at[0] + 0.14 * add.cos(a), at[1] + 0.19, at[2] + 0.14 * add.sin(a)], 0.025, 3, P["apple"])
    add.sphere([at[0], at[1] + 0.2, at[2]], 0.035, 3, P["apple"])


def tureen(at):
    """A tureen of soup, its lid set ajar, the ladle's handle out."""
    lathe([[0.0, 0], [0.1, 0], [0.12, 0.03], [0.2, 0.07], [0.21, 0.15], [0.18, 0.2], [0.17, 0.2], [0.0, 0.17]], at, k_(10), P["white"])
    add.cylinder([at[0], at[1] + 0.17, at[2]], [at[0], at[1] + 0.175, at[2]], 0.17, k_(10), P["bread"])        # the soup
    lid = add.make(lathe, [[0.0, 0.0], [0.19, 0.0], [0.17, 0.04], [0.08, 0.08], [0.03, 0.09], [0.03, 0.12], [0.0, 0.13]], [0, 0, 0], k_(8), P["white"])
    add.mesh(add.move(add.rotateZ(lid, 0.25), [at[0] - 0.02, at[1] + 0.2, at[2]]))
    add.cylinder([at[0] + 0.1, at[1] + 0.15, at[2]], [at[0] + 0.3, at[1] + 0.33, at[2] + 0.05], 0.012, 6, P["steel"])   # the ladle


def place_setting(at, side):
    """A guest's place: a plate with a roll of bread on it, a goblet of
    wine and a knife (``side``: the way the guest looks, +1 or -1 in x)."""
    plate(at, 0.17)
    add.ellipsoid([at[0], at[1] + 0.07, at[2]], [0.06, 0.04, 0.05], 3, P["bread"])
    goblet([at[0] + side * 0.2, at[1], at[2] + 0.26], wine=True)
    add.cuboid([at[0] - side * 0.02, at[1] + 0.006, at[2] - 0.24], [0.2, 0.01, 0.022], P["steel"])


PIG = [(0.55, 0.2, 0.07, 0.07), (0.49, 0.2, 0.18, 0.17), (0.37, 0.21, 0.25, 0.2), (0.15, 0.21, 0.27, 0.21), (-0.08, 0.21, 0.27, 0.21),
       (-0.26, 0.22, 0.24, 0.2), (-0.38, 0.23, 0.2, 0.17), (-0.5, 0.22, 0.16, 0.15), (-0.62, 0.19, 0.11, 0.11),
       (-0.72, 0.17, 0.075, 0.075), (-0.77, 0.17, 0.068, 0.068)]              # (z, y, half-width, half-height), rump to snout


def roast_pig(at):
    """The centrepiece of the feast: a young pig roasted golden brown, lying
    on its belly on a great oval pewter dish -- its trotters tucked under,
    ears flopped forward, eyes shut, the curly tail, an apple in its
    mouth, sprigs of herbs in its back; round it leaves, roast apples and
    onions."""
    x, y, z = at
    dish = add.make(lathe, [[0.0, 0], [0.62, 0], [0.8, 0.06], [0.74, 0.065], [0.6, 0.03], [0.0, 0.03]], [0, 0, 0], k_(12), P["steel"])
    add.mesh(add.move(add.stretch(dish, [0.72, 1.0, 1.08], (0, 0, 0)), at))
    add.push()
    rings = [[[hw * add.cos(2 * add.pi * (j + 0.5) / 16), cy + hh * add.sin(2 * add.pi * (j + 0.5) / 16) * (1.0 if add.sin(2 * add.pi * (j + 0.5) / 16) > 0 else 0.85), zz]
              for j in range(16)] for zz, cy, hw, hh in PIG]
    add.loft(rings, P["bread"])
    add.cylinder([0, 0.17, -0.765], [0, 0.17, -0.8], 0.066, 12, P["meat"])                       # the snout ...
    for s in (-1, 1):
        add.sphere([s * 0.025, 0.18, -0.8], 0.014, 2, P["black"])                                 # ... its nostrils
        ear = add.rotateX(add.make(add.ellipsoid, [0, 0, 0], [0.07, 0.014, 0.11], 3, P["meat"]), 0.55)
        add.mesh(add.move(add.rotateY(ear, s * 0.25), [s * 0.09, 0.37, -0.48]))                  # ears, flopped forward
        add.ellipsoid([s * 0.095, 0.29, -0.57], [0.012, 0.006, 0.028], 2, P["black"])             # eyes, shut
        add.capsule([s * 0.17, 0.1, -0.22], [s * 0.15, 0.07, -0.5], 0.055, 10, P["bread"])       # forelegs, tucked forward
        add.sphere([s * 0.15, 0.07, -0.53], 0.05, 3, P["meat"])
        add.capsule([s * 0.19, 0.11, 0.28], [s * 0.15, 0.07, 0.6], 0.06, 10, P["bread"])         # hind legs, stretched back
        add.sphere([s * 0.15, 0.07, 0.63], 0.05, 3, P["meat"])
    add.sphere([0, 0.1, -0.76], 0.075, 4, P["apple"])                                            # the apple in its mouth
    add.cylinder([0, 0.17, -0.77], [0.01, 0.2, -0.78], 0.008, 4, P["trunk"])
    add.helix([0, 0.27, 0.56], 0.04, 0.035, 2.5, 30, 0.012, 6, P["meat"], axis=(0, 0, 1))        # the curly tail
    for i in range(5):                                                                             # sprigs of herbs in the back
        sx, sz = 0.05 * add.sin(i * 2.3), -0.3 + i * 0.16
        add.cylinder([sx, 0.38, sz], [sx * 2, 0.55, sz + 0.03], 0.008, 4, P["leaf_dark"])
        for k in range(3):
            add.ellipsoid([sx * 2 + 0.025 * (k - 1), 0.5 + 0.03 * k, sz + 0.03], [0.02, 0.008, 0.035], 2, P["leaf"])
    M = add.pop()
    add.mesh(add.move(M, [x, y, z]))                                                               # its belly on the dish
    garnish([x, y + 0.03, z], 0.44, 16, 5, rz=0.72)
    for i in range(6):                                                                             # roast apples and onions
        a = 2 * add.pi * (i + 0.5) / 6
        px, pz = x + 0.42 * add.cos(a), z + 0.68 * add.sin(a)
        add.sphere([px, y + 0.1, pz], 0.065, 3, P["meat"] if i % 2 else P["linen"])


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
    """A wall torch in its holder.  The holder: an iron strap nailed to the
    wall, and an arm out of it ending in a ring.  The torch stands in the
    ring leaning out from the wall, its foot against the strap: a wooden
    shaft, an iron cup at its head with the burning tow, and the flame.
    ``at`` is the point on the wall, ``facing`` the direction out of it."""
    add.push()
    add.cuboid([0, -0.05, -0.025], [0.1, 0.6, 0.11], P["iron"])                     # the strap (let into the wall),
    for y in (-0.3, 0.2):
        add.cylinder([0, y, 0.03], [0, y, 0.042], 0.022, 6, P["iron"])              # its nails,
    foot, head = [0, -0.34, 0.068], [0, 0.56, 0.3]                                  # the shaft: its foot on the strap
    L = vlen(vsub(head, foot))
    d = [(head[k] - foot[k]) / L for k in range(3)]
    e = [0, -d[2], d[1]]                                                            # (across the shaft, away from the wall)
    t = (0.18 - foot[1]) / (head[1] - foot[1])
    ring = [foot[k] + (head[k] - foot[k]) * t for k in range(3)]
    near = ring[2] - 0.058 * e[2]                                                   # the ring's side next to the wall
    add.cuboid([0, ring[1] - 0.058 * e[1], (0.025 + near) / 2], [0.035, 0.035, near - 0.025], P["iron"])   # the arm,
    add.torus(ring, 0.058, 0.014, 12, 6, P["iron"], axis=d)                         # the ring
    add.cylinder(foot, head, 0.04, 8, P["wood_dark"])                               # and the torch in it:
    at_d = lambda u: [head[k] + d[k] * u for k in range(3)]
    add.frustum(head, at_d(0.14), 0.045, 0.085, 10, P["iron"])                      # the cup,
    add.cylinder(at_d(0.09), at_d(0.18), 0.068, 8, P["rope"])                       # the tow,
    add.ellipsoid(at_d(0.32), [0.1, 0.2, 0.1], 6, FLAME)                           # the flame, drawn up
    add.cone([at_d(0.32)[0], at_d(0.32)[1] + 0.11, at_d(0.32)[2]], [at_d(0.32)[0], at_d(0.32)[1] + 0.35, at_d(0.32)[2]],
             0.075, 8, FLAME)                                                       # to a point
    add.ellipsoid(at_d(0.27), [0.045, 0.1, 0.045], 5, P["flame_core"])
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


def asleep(at, facing=0.0, blanket=None, seed=0, pillow=False):
    """Someone asleep on his back under a blanket, head on a pillow towards
    -z; ``at`` is the top of what he lies on -- a mattress, the hay."""
    add.push()
    hair = P[HAIR[int(hash2(int(at[0] * 3) + seed, int(at[2] * 3), 9) * 4)]]
    blanket = blanket or P["red"]
    if pillow:                                                                                   # (a bed brings its own)
        add.mesh(add.move(add.stretch(add.make(add.sphere, [0, 0, 0], 0.25, 8, P["white"]), [1.4, 0.45, 0.9], (0, 0, 0)), [0, 0.06, -0.75]))
    add.ellipsoid([0, 0.23, -0.74], [0.09, 0.11, 0.124], 4, P["skin"])                                # the head, face up,
    add.ellipsoid([0, 0.205, -0.78], [0.094, 0.1, 0.12], 4, hair)                                     # on the pillow
    add.ellipsoid([0, 0.34, -0.7], [0.016, 0.028, 0.026], 2, P["skin"])                               # the nose
    for s in (-1, 1):
        add.ellipsoid([s * 0.035, 0.325, -0.725], [0.018, 0.005, 0.008], 2, P["black"])               # eyes shut
        add.ellipsoid([s * 0.09, 0.23, -0.74], [0.014, 0.022, 0.028], 2, P["skin"])                   # ears
        add.capsule([s * 0.3, 0.14, -0.4], [s * 0.13, 0.2, -0.08], 0.05, 8, P["linen"])               # his arms on the blanket
        add.capsule([s * 0.13, 0.2, -0.08], [s * 0.08, 0.21, 0.0], 0.034, 8, P["skin"])
    add.cuboid([0, 0.015, 0.2], [1.04, 0.03, 1.7], blanket)                                          # the blanket, over the bed ...
    rings = [[[hw * add.cos(add.pi * i / 8), 0.01 + hh * add.sin(add.pi * i / 8), zz] for i in range(9)]
             for zz, hw, hh in ((-0.6, 0.34, 0.12), (-0.3, 0.36, 0.16), (0.1, 0.34, 0.13), (0.5, 0.3, 0.1),
                                (0.8, 0.27, 0.09), (0.95, 0.25, 0.15), (1.02, 0.22, 0.09))]
    add.loft(rings, blanket)                                                                   # ... and over him
    add.cuboid([0, 0.1, -0.62], [0.74, 0.07, 0.1], P["white"])                                     # the sheet folded over it
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def bed(at, facing=0.0, sleeper=True, canopy=False, blanket=None):
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
    if sleeper:                                                                                  # asleep on his back
        asleep([0, 0.56, 0], 0.0, blanket or P["red"], int(at[0] * 3) + int(at[2] * 7))
    else:
        add.cuboid([0, 0.6, 0.2], [0.95, 0.06, 1.5], blanket or P["red"])                         # a folded blanket
    if canopy:
        for sx in (-0.55, 0.55):
            for sz in (-1.1, 1.1):
                add.cylinder([sx, 0, sz], [sx, 2.4, sz], 0.06, 12, P["wood_dark"])
        add.cuboid([0, 2.45, 0], [1.4, 0.1, 2.5], P["red"])
        for sz in (-1.1, 1.1):
            add.cuboid([0, 2.25, sz], [1.3, 0.3, 0.04], P["gold"])
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def bunk(at, facing=0.0, sleepers=(False, False), blankets=None):
    """A bunk bed for two: four tall posts, a frame, mattress, pillow and
    blanket on each tier, a rail along the top one and a ladder up at the
    foot; head towards -z.  ``sleepers`` says who is asleep in it, below
    and above."""
    blankets = blankets or (P["blue"], P["red"])
    add.push()
    for sx in (-0.5, 0.5):
        for sz in (-1.05, 1.05):
            add.cuboid([sx, 0.95, sz], [0.1, 1.9, 0.1], P["wood_dark"])                        # posts
    for tier, (y, asleep_here, blanket) in enumerate(zip((0.3, 1.3), sleepers, blankets)):
        for sx in (-0.5, 0.5):
            add.cuboid([sx, y, 0], [0.08, 0.14, 2.0], P["wood"])                                # the side rails,
        for sz in (-1.05, 1.05):
            add.cuboid([0, y + 0.1, sz], [0.9, 0.3, 0.05], P["wood"])                            # head and foot boards
        add.cuboid([0, y + 0.13, 0], [0.9, 0.12, 2.0], P["linen"])                              # the mattress
        add.mesh(add.move(add.stretch(add.make(add.sphere, [0, 0, 0], 0.22, 8, P["white"]), [1.4, 0.4, 0.8], (0, 0, 0)), [0, y + 0.24, -0.72]))
        if asleep_here:
            asleep([0, y + 0.19, 0], 0.0, blanket, tier * 5 + int(at[0] * 3) + int(at[2] * 7))
        else:
            add.cuboid([0, y + 0.22, 0.25], [0.86, 0.06, 1.3], blanket)                          # a blanket, folded back
    add.cuboid([-0.5, 1.8, 0.1], [0.06, 0.08, 1.7], P["wood"])                                  # the top tier's rail
    for sx in (-0.2, 0.2):                                                                     # the ladder at the foot
        add.cuboid([sx, 0.8, 1.13], [0.06, 1.6, 0.05], P["wood"])
    for i in range(4):
        add.cuboid([0, 0.3 + 0.33 * i, 1.13], [0.4, 0.05, 0.05], P["wood"])
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def chest(at, facing=0.0, open_lid=False, s=1.0):
    add.push()
    add.cuboid([0, 0.4 * s, 0], [1.6 * s, 0.8 * s, 1.0 * s], P["wood_dark"])
    add.cuboid([0, 0.5 * s, 0], [1.66 * s, 0.12 * s, 1.06 * s], P["iron"])
    for sx in (-0.7, 0.7):
        add.cuboid([sx * s, 0.4 * s, 0], [0.1 * s, 0.82 * s, 1.06 * s], P["iron"])
    for sx in (-1, 1):                                                                      # handles at the ends
        add.torus([sx * 0.84 * s, 0.55 * s, 0], 0.08 * s, 0.015 * s, 10, 4, P["iron"], axis=(1, 0, 0))
    add.cuboid([0, 0.66 * s, 0.51 * s], [0.18 * s, 0.22 * s, 0.03 * s], P["iron"])                        # the lock plate
    add.cuboid([0, 0.64 * s, 0.527 * s], [0.03 * s, 0.07 * s, 0.01 * s], P["black"])                       # its keyhole
    lid = add.make(add.cuboid, [0, 0.12 * s, 0], [1.6 * s, 0.24 * s, 1.0 * s], P["wood_dark"])
    lid.extend(add.make(add.cuboid, [0, 0.12 * s, 0], [1.66 * s, 0.1 * s, 1.06 * s], P["iron"]))           # an iron band round the lid
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
    """A chess study set up on a big table: White to play and win.  The
    board is seen from the White side, where the caption lies: rank 1 is
    nearest, the a-file on the left, and a1 in the left-hand corner is a
    dark square (and h1, on the right, a light one), as on any board.
    White: Kb1, pawns c5 e5 f5 g2 h2.  Black: Ka4, pawns a7 b7 e7 f7 b2 g4."""
    s = square / 0.125                                                             # the pieces grow with the squares
    board = 8 * square
    table(at, board + 0.4, board + 0.4, 0.72, P["wood_dark"])

    def centre(i, j):                                                              # file i (a = 0), rank j (rank 1 = 0):
        return at[0] - 3.5 * square + i * square, at[2] + 3.5 * square - j * square   # rank 1 on the caption's side (+z)

    for i in range(8):
        for j in range(8):
            x, z = centre(i, j)
            add.cuboid([x, at[1] + 0.735, z], [square, 0.03, square], P["black"] if (i + j) % 2 == 0 else P["white"])
    position = {"white": [("K", "b1"), ("P", "h2"), ("P", "g2"), ("P", "f5"), ("P", "e5"), ("P", "c5")],
                "black": [("K", "a4"), ("P", "g4"), ("P", "f7"), ("P", "e7"), ("P", "b7"), ("P", "a7"), ("P", "b2")]}
    for side, pieces in position.items():
        for kind, sq in pieces:
            x, z = centre("abcdefgh".index(sq[0]), int(sq[1]) - 1)
            chess_piece(kind, x, at[1] + 0.75, z, P["white"] if side == "white" else P["black"], s)
    chair([at[0], at[1], at[2] + board / 2 + 0.45], add.pi)
    chair([at[0], at[1], at[2] - board / 2 - 0.45], 0)
    top = 0.735                                                                     # the board, above the floor
    arms = (([-0.01, 0.6, 0.24], [0, 1, 0.15], [0, -1, 0.5]), ([0.17, 0.25, 0.32], [-0.3, -0.2, 1], [1, -0.3, -0.4]))
    figure([at[0], at[1] + 0.48, at[2] + board / 2 + 0.45], add.pi,                  # White: a man of the town, his chin
           person("sit", P["wood_light"], table=(top - 0.48, 0.25), seat=0.48, arms=arms, hat=True, beard=P["trunk"]))   # on his fist
    M = add.stretch(knight("sit", table=(top, 0.25)), [LIFE] * 3, (0, 0, 0))        # Black: a knight in armour, bareheaded,
    add.mesh(add.move(M, [at[0], at[1], at[2] - board / 2 - 0.45]))                  # his great helm on the floor by his chair
    add.mesh(add.move(add.stretch(great_helm(True), [LIFE] * 3, (0, 0, 0)), [at[0] - 0.6, at[1] - 1.525 * LIFE, at[2] - board / 2 - 0.4]))
    add.text("WHITE TO PLAY AND WIN", [at[0], at[1] + 0.724, at[2] + board / 2 + 0.12], 0.06 * s, 0.006, P["gold"],
             align="center", u=[1, 0, 0], v=[0, 0, -1], k=6)


SHOE = [(-0.075, 0.034, 0.055), (-0.055, 0.044, 0.08), (0.0, 0.047, 0.095), (0.07, 0.047, 0.065), (0.13, 0.04, 0.045),
        (0.18, 0.026, 0.03), (0.205, 0.008, 0.014)]                            # (z, half-width, height), heel to toe
TUNIC = [(0.5, 0.24, 0.2, 0.0), (0.62, 0.218, 0.172, 0.0), (0.8, 0.192, 0.146, 0.0), (0.94, 0.172, 0.126, 0.0),
         (1.02, 0.16, 0.12, 0.004), (1.14, 0.17, 0.128, 0.012), (1.26, 0.183, 0.134, 0.015), (1.36, 0.19, 0.127, 0.01),
         (1.43, 0.18, 0.11, 0.0), (1.49, 0.125, 0.088, 0.0), (1.525, 0.066, 0.062, 0.0)]     # (y, half-width, half-depth, z)
HAIR = ("wood_dark", "black", "trunk", "straw")


LADY = [(1.02, 0.148, 0.114, 0.004), (1.14, 0.156, 0.124, 0.012), (1.26, 0.17, 0.142, 0.024), (1.36, 0.176, 0.126, 0.014),
        (1.43, 0.166, 0.106, 0.0), (1.49, 0.118, 0.085, 0.0), (1.525, 0.062, 0.06, 0.0)]     # her bodice (y, half-width, half-depth, z)
SKIRT = [(0.015, 0.36, 0.33, 0.05), (0.2, 0.32, 0.29, 0.04), (0.45, 0.27, 0.24, 0.028), (0.7, 0.22, 0.19, 0.014),
         (0.94, 0.168, 0.134, 0.004)]                                                        # a gown's skirt, floor to waist


def lap_skirt(seat, reach, colour):
    """The skirt of a gown over the lap of a sitting figure (see
    :func:`person`), falling over the knees to the floor: a loft of rings
    along the lap and down the shins."""
    floor = -seat / LIFE
    stations = [((0, 0.1, -0.02), 0.215, 0.105, (0, 0, 1)), ((0, 0.105, 0.2), 0.225, 0.1, (0, 0, 1)),
                ((0, 0.095, 0.42), 0.235, 0.1, (0, -0.4, 1)), ((0, 0.02, 0.5), 0.25, 0.11, (0, -1, 0.4)),
                ((0, floor * 0.5, reach + 0.04), 0.275, 0.14, (0, -1, 0.05)), ((0, floor + 0.015, reach + 0.06), 0.31, 0.17, (0, -1, 0))]
    rings = []
    for c, rx, ry, t in stations:
        v = vunit(vcross(vunit(list(t)), [1, 0, 0]))
        rings.append([[c[0] + add.cos(a) * rx, c[1] + add.sin(a) * ry * v[1], c[2] + add.sin(a) * ry * v[2]]
                      for a in (2 * add.pi * (i + 0.5) / 20 for i in range(20))])
    add.loft(rings, colour)


def headwear(kind, dy, colour, trim):
    """What is worn on the head of :func:`person` (``dy`` lower when he or
    she sits): "veil", "hennin" (the tall pointed hat with a veil from its
    tip), "circlet" (a gold band with a jewel), "chaperon" (a padded roll
    with its long tail hanging), "cap", "jester" (``colour`` a pair: a
    fool's hat of three horns with bells)."""
    y = 1.665 + dy                                                             # the middle of the head
    if kind == "veil":
        add.ellipsoid([0, y + 0.04, -0.022], [0.093, 0.094, 0.106], 5, P["white"])
        add.ellipsoid([0, y - 0.1, -0.09], [0.1, 0.16, 0.035], 4, P["white"])
        add.torus([0, y + 0.047, -0.006], 0.089, 0.008, 16, 5, trim)
    elif kind == "hennin":
        base = [0, y + 0.07, -0.035]
        d = vunit([0, 0.78, -0.62])
        tip = _at(base, d, 0.55)
        add.cone(base, tip, 0.088, k_(12), colour)
        add.torus(base, 0.09, 0.014, k_(12), 5, trim, axis=d)
        sheet([[-0.02, tip[1], tip[2] + 0.01], [0.02, tip[1], tip[2] + 0.01], [0.17, y - 0.32, -0.17], [-0.17, y - 0.32, -0.17]],
              P["white"], 0.004)                                                                    # the veil
    elif kind == "circlet":
        add.torus([0, y + 0.05, -0.008], 0.087, 0.008, k_(16), 5, trim)
        add.sphere([0, y + 0.05, 0.08], 0.013, 3, P["red"])
    elif kind == "chaperon":
        add.ellipsoid([0, y + 0.075, -0.012], [0.09, 0.05, 0.1], 5, colour)
        add.torus([0, y + 0.06, -0.012], 0.088, 0.032, k_(14), 6, colour)
        add.capsule([0.07, y + 0.05, -0.05], [0.12, y - 0.26, -0.1], 0.024, 8, colour)
    elif kind == "cap":
        add.ellipsoid([0, y + 0.045, -0.014], [0.089, 0.075, 0.1], 5, colour)
    elif kind == "jester":
        add.ellipsoid([0, y + 0.04, -0.014], [0.09, 0.08, 0.1], 5, colour[0])
        for i, (hx, hz) in enumerate(((-1, 0.2), (1, 0.2), (0, -1))):
            base = [0.06 * hx, y + 0.09, 0.06 * hz - 0.014]
            mid = [0.17 * hx, y + 0.2, 0.14 * hz - 0.014]
            tip = [0.25 * hx, y + 0.09, 0.21 * hz - 0.014]
            add.frustum(base, mid, 0.04, 0.024, 8, colour[i % 2])
            add.frustum(mid, tip, 0.024, 0.008, 8, colour[i % 2])
            add.sphere(tip, 0.024, 3, P["gold"])


def person(pose="stand", tunic=None, hat=False, table=None, seat=0.53, arms=None, hose=None, hair=None, reach=0.47, lean=None,
           gown=None, trim=None, female=False, beard=None, head=None, motley=None, long_hair=False):
    """A man in a knee-length tunic, life-size, facing +z (his right hand
    on -x), like the knights: hose and leather shoes, the tunic belted at
    the waist with a purse at his side, sleeves and hands, a face with
    eyes, nose and ears, hair -- or a felt hat (``hat=True``) or a steel
    cap (``hat="steel"``).  ``pose``: "stand" (arms by his sides) or "sit"
    (on a seat at y = 0 that stands ``seat`` above the floor of the
    castle, his feet on the floor; ``table`` = (its height above the seat,
    the distance to its edge, in the castle's units) leans him over it
    with his forearms on the board, else his hands rest on his knees;
    "pray" joins them).  ``arms`` gives (wrist, fist, elbow) of each arm,
    right first, for any other pose; ``reach`` how far forward his feet
    are when he sits, ``lean`` how far he leans forward (radians).

    ``gown`` (a colour) dresses the figure in a long gown to the floor
    instead of tunic and hose, girdled in ``trim``; ``female`` gives her a
    lady's bodice and face; ``beard`` a beard and moustache of that colour;
    ``head`` something worn on the head (see :func:`headwear`); ``motley``
    = (colour, colour) the fool's two colours, counterchanged on tunic,
    sleeves and hose; ``long_hair`` lets the hair fall down the back."""
    tunic = gown or tunic or P["linen"]
    trim = trim or P["gold"]
    sit = pose != "stand"
    dy = -0.83 if sit else 0.0                                              # sitting, all above the hips is 0.83 lower
    hair = hair or P[HAIR[int(hash2(int(tunic[0]), int(tunic[1]) + int(tunic[2]), 7) * 4)]]
    hose = hose or P["wood_dark"]
    legs = (motley[1], motley[0]) if motley else (hose, hose)               # right leg, left leg
    add.push()
    for s, leg in zip((-1, 1), legs):
        if sit:
            hip, knee = [s * 0.095, 0.1, 0.0], [s * 0.11, 0.09, 0.43]
            ankle = [s * 0.115, 0.09 - seat / LIFE, reach]
            if not gown:
                add.capsule(hip, knee, 0.075, 12, motley[(1 - s) // 2] if motley else tunic)   # the tunic over his thighs
                add.capsule(knee, ankle, 0.052, 12, leg)
        else:
            hip, ankle = [s * 0.095, 0.93, 0.0], [s * 0.105, 0.09, -0.01]
            knee = joint(hip, ankle, 0.42, 0.42, [0, 0, 1])
            if not gown:
                add.capsule(hip, knee, 0.066, 12, leg)
                add.capsule(knee, ankle, 0.05, 12, leg)
        add.mesh(sabaton([ankle[0], ankle[1] - 0.09, ankle[2]], [s * 0.15, 0, 1], P["black"], SHOE))
    if gown and sit:
        lap_skirt(seat, reach, gown)
    top = LADY if female else [r for r in TUNIC if r[0] > 1.0]
    if gown and not sit:
        body = SKIRT + top
    elif gown:
        body = [(0.015, 0.22, 0.19, 0.03), (0.94 + dy, 0.17, 0.132, 0.004)] + [(y + dy, hw, hd, dz) for y, hw, hd, dz in top]
    else:
        body = [(y + dy, hw, hd, dz) for y, hw, hd, dz in TUNIC if not sit or y > 0.86]
        if sit:
            body = [(0.015, 0.205, 0.175, 0.03)] + body
    if lean is None:                                                           # leaning over the table, or a little forward
        lean = (0.3 if table else 0.12) if sit else 0.0
    add.push()
    if motley:
        add.push()
        loft_rings(body, 2.3, 20, tunic)
        add.mesh(add.color_by(add.pop(), lambda q: motley[0] if q[0] < 0 else motley[1]))
    else:
        loft_rings(body, 2.3, 20, tunic)
    if gown:                                                                   # a girdle, its end hanging in front
        add.loft([[on_rings(body, y + dy, 2 * add.pi * (i + 0.5) / 20, 2.3, 0.006)[0] for i in range(20)] for y in (0.97, 1.0)], trim)
        if not sit:
            p = on_rings(body, 0.975, add.pi / 2, 2.3, 0.012)[0]
            add.beam(p, [p[0] + 0.01, 0.55, p[2] + 0.13], 0.025, 0.008, trim, up=[0, 0, 1])
            add.polyline([on_rings(body, 0.035, 2 * add.pi * i / 24.0, 2.3, 0.006)[0] for i in range(24)], 0.012, 5, trim, closed=True)
    else:
        add.loft([[on_rings(body, y + dy, 2 * add.pi * (i + 0.5) / 20, 2.3, 0.006)[0] for i in range(20)] for y in (0.985, 1.025)], P["wood_dark"])
        p = on_rings(body, 1.005 + dy, add.pi / 2, 2.3, 0.012)[0]
        add.cuboid(p, [0.05, 0.045, 0.012], P["iron"])                                             # the buckle
        if not sit:
            p = on_rings(body, 0.95, add.pi / 2 + 0.75, 2.3, 0.03)[0]
            add.ellipsoid(p, [0.045, 0.06, 0.03], 3, P["wood"])                                     # the purse
    add.frustum([0, 1.47 + dy, 0], [0, 1.575 + dy, 0.008], 0.052 if not female else 0.044, 0.047 if not female else 0.04, 10, P["skin"])
    add.ellipsoid([0, 1.665 + dy, 0.012], [0.078, 0.108, 0.095] if not female else [0.074, 0.102, 0.09], 5, P["skin"])
    add.ellipsoid([0, 1.655 + dy, 0.103], [0.014, 0.026, 0.022] if not female else [0.011, 0.022, 0.018], 2, P["skin"])
    for s in (-1, 1):
        add.sphere([s * 0.03, 1.685 + dy, 0.092], 0.011, 2, P["black"])
        add.ellipsoid([s * 0.077, 1.665 + dy, 0.0], [0.014, 0.03, 0.02], 2, P["skin"])
    if female:                                                                 # red lips, rosy cheeks
        add.ellipsoid([0, 1.612 + dy, 0.093], [0.019, 0.007, 0.008], 2, P["apple"])
        for s in (-1, 1):
            add.ellipsoid([s * 0.043, 1.635 + dy, 0.078], [0.016, 0.011, 0.006], 2, P["pig"])
    if beard:
        add.ellipsoid([0, 1.585 + dy, 0.07], [0.058, 0.065, 0.042], 3, beard)
        for s in (-1, 1):
            add.capsule([s * 0.012, 1.628 + dy, 0.1], [s * 0.05, 1.615 + dy, 0.085], 0.01, 6, beard)
    if hat == "steel":                                                         # a kettle hat
        add.hemisphere([0, 1.715 + dy, -0.005], 0.108, 5, P["steel"])
        add.cylinder([0, 1.71 + dy, -0.005], [0, 1.722 + dy, -0.005], 0.165, k_(8), P["steel"])
    else:
        add.ellipsoid([0, 1.7 + dy, -0.014], [0.083, 0.088, 0.098], 5, hair)
        if long_hair:                                                          # falling down her back, and beside her face
            add.ellipsoid([0, 1.52 + dy, -0.075], [0.1, 0.19, 0.045], 4, hair)
            for s in (-1, 1):
                add.ellipsoid([s * 0.074, 1.6 + dy, -0.01], [0.028, 0.1, 0.05], 3, hair)
        if hat:                                                                # a felt hat with a brim
            add.cylinder([0, 1.745 + dy, -0.005], [0, 1.757 + dy, -0.005], 0.16, k_(8), P["wood"])
            add.frustum([0, 1.745 + dy, -0.005], [0, 1.85 + dy, -0.01], 0.092, 0.075, k_(8), P["wood"])
        if head:                                                               # "kind", or ("kind", its colour)
            kind, colour = head if isinstance(head, tuple) else (head, motley or tunic)
            headwear(kind, dy, colour, trim)
    upper = add.pop()
    py = 0.1 if sit else 0.93                                                  # leaning from the seat, or from the hips
    add.mesh(add.rotateX(upper, lean, [0, py, 0]))
    shoulders = [[s * (0.19 if not female else 0.178), py + (1.42 + dy - py) * add.cos(lean), (1.42 + dy - py) * add.sin(lean)] for s in (-1, 1)]
    if arms is None:
        if not sit:
            arms = [([s * 0.245, 0.86, 0.03], [0, -1, 0.1], [0, 0, -1]) for s in (-1, 1)]
        elif pose == "pray":
            arms = [([s * 0.03, 0.47, 0.25], [0, 1, 0.25], [s, -0.3, -0.2]) for s in (-1, 1)]
        elif table:
            h, d = table[0] / LIFE + 0.03, table[1] / LIFE + 0.1
            arms = [([s * 0.17, h, d], [-s * 0.3, -0.2, 1], [s, -0.3, -0.4]) for s in (-1, 1)]
        else:
            arms = [([s * 0.15, 0.2, 0.33], [0, -0.4, 1], [s, 0, -0.5]) for s in (-1, 1)]
    for s, sh, (wr, fist, pole) in zip((-1, 1), shoulders, arms):
        el = joint(sh, wr, 0.3, 0.27, pole)
        sleeve = motley[(1 + s) // 2] if motley else tunic                                     # counterchanged
        add.sphere(sh, 0.06, 3, sleeve)
        add.frustum(sh, el, 0.056, 0.047, 10, sleeve)                                          # the sleeves
        add.sphere(el, 0.047, 3, sleeve)
        add.frustum(el, _at(wr, vunit(vsub(wr, el)), -0.02), 0.047, 0.04 if not gown else 0.056, 10, sleeve)
        if gown:
            add.torus(_at(wr, vunit(vsub(wr, el)), -0.025), 0.05, 0.01, 12, 4, trim, axis=vunit(vsub(wr, el)))   # the cuff
        add.capsule(wr, _at(wr, vunit(fist), 0.06), 0.034 if not female else 0.03, 9, P["skin"])  # the hand
    return add.pop()


def sitting_man(at, facing=0.0, shirt=None, table=None, pray=False, seat=0.53):
    """A man sitting on a bench (his seat at ``at``, ``seat`` above the
    floor): at a table (see :func:`person`), at prayer, or at rest."""
    M = person("pray" if pray else "sit", shirt, table=table, seat=seat)
    add.mesh(add.move(add.rotateY(add.stretch(M, [LIFE] * 3, (0, 0, 0)), facing), at))


def standing_man(at, facing=0.0, shirt=None, hat=False):
    """A man standing on ``at``, see :func:`person`."""
    M = person("stand", shirt, hat)
    add.mesh(add.move(add.rotateY(add.stretch(M, [LIFE] * 3, (0, 0, 0)), facing), at))


def figure(at, facing, M):
    """Stand a life-size figure built by :func:`person` on ``at``, turned to ``facing``."""
    add.mesh(add.move(add.rotateY(add.stretch(M, [LIFE] * 3, (0, 0, 0)), facing), at))


def placed(M, at, x, y, z):
    """``M``, built in a frame of its own, placed at ``at`` with its axes along ``x``, ``y`` and ``z``."""
    return add.transform(M, [[x[0], y[0], z[0], at[0]], [x[1], y[1], z[1], at[1]], [x[2], y[2], z[2], at[2]]])


def frame_of(d, up):
    """Three axes (side, up, along) from a direction ``d`` and a rough ``up``."""
    d = vunit(d)
    side = vunit(vcross(up, d))
    return side, vcross(d, side), d


def scroll(a, b, r=0.025, hang=0.25):
    """A rolled parchment held between two points, a length of it hanging unrolled."""
    add.cylinder(a, b, r, 10, P["linen"])
    m = [(a[k] + b[k]) / 2 for k in range(3)]
    add.cuboid([m[0], m[1] - hang / 2, m[2] + r * 0.8], [vlen(vsub(b, a)) * 0.8, hang, 0.004], P["linen"])
    for q in (a, b):
        add.sphere(q, r * 1.3, 3, P["wood_dark"])


def advisor(at, facing=0.0):
    """The king's counsellor, standing: a long dark robe, a red chaperon
    with its tail hanging, a grey beard, the gold chain of his office, and
    a scroll of petitions in both hands."""
    arms = (([-0.12, 1.08, 0.27], [1, 0.1, 0.2], [-1, -0.6, -0.3]), ([0.12, 1.08, 0.27], [-1, 0.1, 0.2], [1, -0.6, -0.3]))
    add.push()
    add.mesh(person("stand", gown=P["slate"], trim=P["wood_dark"], beard=P["stone"], hair=P["stone"], head=("chaperon", P["red"]), arms=arms))
    add.polyline([[-0.15, 1.44, 0.1], [-0.08, 1.31, 0.155], [0.0, 1.27, 0.165], [0.08, 1.31, 0.155], [0.15, 1.44, 0.1]], 0.011, 6, P["gold"], smooth=1)
    add.cylinder([0, 1.26, 0.14], [0, 1.26, 0.158], 0.032, 10, P["gold"])                     # the badge of his office
    scroll([-0.1, 1.1, 0.33], [0.1, 1.1, 0.33])
    figure(at, facing, add.pop())


def marotte(at, d, colours):
    """The fool's bauble: a short staff with a little fool's head on top."""
    top = _at(at, d, 0.42)
    add.cylinder(at, top, 0.013, 8, P["wood"])
    head = _at(top, d, 0.04)
    add.sphere(head, 0.042, 4, P["skin"])
    for i, sx in enumerate((-1, 1)):
        tip = [head[0] + sx * 0.08, head[1] + 0.1, head[2]]
        add.cone([head[0] + sx * 0.02, head[1] + 0.02, head[2]], tip, 0.028, 6, colours[i])
        add.sphere(tip, 0.015, 2, P["gold"])


def jester(at, facing=0.0):
    """The king's fool, mid-jest: motley of red and yellow counterchanged,
    a fool's hat of three horns with golden bells, his bauble raised in
    his right hand, his left fist on his hip."""
    motley = (P["red"], P["cheese"])
    arms = (([-0.3, 1.45, 0.16], [0, 1, 0.1], [-1, -0.3, -0.4]), ([0.21, 1.0, -0.04], [-0.4, -0.6, 0.1], [1, 0.1, 0.5]))
    add.push()
    add.mesh(person("stand", motley=motley, head="jester", arms=arms))
    marotte([-0.3, 1.47, 0.2], [0.02, 1, 0.08], motley)
    for s in (-1, 1):                                                                      # bells on the curled toes of his shoes
        add.sphere([s * 0.13, 0.07, 0.22], 0.022, 3, P["gold"])
    figure(at, facing, add.pop())


def lute():
    """A lute, its front facing +y and its neck along +z: the round back of
    ribs, the flat front with its rose and bridge, the neck with its frets
    and the peg box bent back."""
    add.push()
    back = add.cut(add.make(add.ellipsoid, [0, 0, 0], [0.15, 0.085, 0.2], 6, P["wood_light"]), [0, 0, 0], [0, 1, 0])
    add.mesh(back)
    add.mesh(add.stretch(add.make(add.cylinder, [0, 0, 0], [0, 0.01, 0], 1.0, 24, P["wood"]), [0.148, 1.0, 0.198], (0, 0, 0)))
    add.cylinder([0, 0.009, 0.04], [0, 0.013, 0.04], 0.038, 12, P["black"])                  # the rose
    add.cuboid([0, 0.018, -0.12], [0.1, 0.016, 0.02], P["wood_dark"])                        # the bridge
    add.cuboid([0, 0.004, 0.33], [0.052, 0.026, 0.3], P["wood_dark"])                         # the neck
    for i in range(6):
        add.cuboid([0, 0.019, 0.22 + 0.04 * i], [0.054, 0.004, 0.005], P["bone"])            # frets
    add.cuboid([0, 0.019, 0.09], [0.034, 0.003, 0.42], P["linen"])                          # the strings
    box = add.make(add.cuboid, [0, 0, 0.075], [0.058, 0.03, 0.15], P["wood_dark"])
    add.mesh(add.move(add.rotateX(box, 1.2, [0, 0, 0]), [0, 0.0, 0.48]))                       # the peg box, bent back
    for i in range(4):
        z = 0.03 + 0.03 * i
        c = [0, -0.93 * z + 0.0, 0.48 + 0.36 * z]
        add.cylinder([c[0] - 0.045, c[1], c[2]], [c[0] + 0.045, c[1], c[2]], 0.006, 6, P["bone"])
    return add.pop()


def recorder():
    """A wooden recorder along +z, the beak at the origin."""
    add.push()
    add.frustum([0, 0, 0], [0, 0, 0.05], 0.009, 0.014, 10, P["wood_dark"])
    add.cylinder([0, 0, 0.05], [0, 0, 0.3], 0.013, 10, P["wood_dark"])
    add.frustum([0, 0, 0.3], [0, 0, 0.35], 0.013, 0.022, 10, P["wood_dark"])
    for i in range(4):
        add.sphere([0, 0.012, 0.12 + 0.045 * i], 0.004, 2, P["black"])                        # finger holes
    return add.pop()


def tabor():
    """A small drum along +x: a red shell, heads of hide, hoops and the
    zig-zag of its tension cord."""
    add.push()
    add.cylinder([-0.08, 0, 0], [0.08, 0, 0], 0.14, 20, P["red"])
    for x in (-0.085, 0.085):
        add.cylinder([x - 0.004, 0, 0], [x + 0.004, 0, 0], 0.13, 20, P["linen"])
        add.torus([x, 0, 0], 0.143, 0.01, 20, 5, P["wood"], axis=(1, 0, 0))
    pts = [[(-0.075 if i % 2 == 0 else 0.075), 0.146 * add.cos(i * add.pi / 7), 0.146 * add.sin(i * add.pi / 7)] for i in range(15)]
    add.polyline(pts, 0.005, 4, P["rope"])
    return add.pop()


def stool(at, h=0.46):
    """A round three-legged stool."""
    add.cylinder([at[0], at[1] + h - 0.05, at[2]], [at[0], at[1] + h, at[2]], 0.19, k_(10), P["wood"])
    for i in range(3):
        a = i * 2 * add.pi / 3
        add.cylinder([at[0] + 0.16 * add.cos(a), at[1], at[2] + 0.16 * add.sin(a)],
                     [at[0] + 0.11 * add.cos(a), at[1] + h - 0.05, at[2] + 0.11 * add.sin(a)], 0.025, 6, P["wood_dark"])


def musician(at, facing, kind):
    """A player at the feast: "lute" (sitting on a stool, the lute across
    his lap, left hand on its neck, right hand at the strings), "pipe"
    (standing, a recorder at his lips) or "drum" (standing, a tabor at his
    left hip and a stick in his right hand)."""
    add.push()
    if kind == "lute":
        seat = 0.46
        d, up = [0.78, 0.5, 0.36], [0, 0.35, 1]
        side, u, z = frame_of(d, up)
        body = [0.07, 0.26, 0.24]
        neck = _at(body, z, 0.36)
        arms = (([-0.02, 0.33, 0.33], [0.4, -0.5, 0.4], [-1, -0.6, -0.4]), ([neck[0] - 0.02, neck[1] - 0.03, neck[2] + 0.04], [-0.4, 0.2, -0.3], [1, -1, -0.3]))
        add.mesh(person("sit", P["leaf"], seat=seat, arms=arms, hat=True, lean=0.05))
        add.mesh(placed(lute(), body, side, u, z))
        M = add.pop()
        stool([at[0], at[1] - seat, at[2]], seat)
        figure(at, facing, M)
        return
    if kind == "pipe":
        mouth = [0, 1.618, 0.108]
        d = vunit([0, -0.62, 0.78])
        arms = (([-0.05, 1.43, 0.25], [1, 0.3, 0.3], [-1, -1, -0.2]), ([0.05, 1.51, 0.19], [-1, 0.3, 0.3], [1, -1, -0.2]))
        add.mesh(person("stand", P["blue"], arms=arms, head=("cap", P["red"])))
        side, u, z = frame_of(d, [0, 1, 0])
        add.mesh(placed(recorder(), mouth, side, u, z))
    else:
        arms = (([-0.02, 1.16, 0.3], [0.8, 0.1, 0.3], [-1, -0.4, -0.3]), ([0.27, 1.13, 0.14], [0, -1, 0.2], [1, 0.2, -0.3]))
        add.mesh(person("stand", P["cushion"], arms=arms, beard=P["trunk"], hat=True))
        add.mesh(add.move(tabor(), [0.33, 1.0, 0.12]))
        add.polyline([[0.2, 1.47, 0.05], [0.33, 1.2, 0.06], [0.33, 1.14, 0.12]], 0.01, 5, P["wood_dark"])   # its strap
        fist = [0.02, 1.16, 0.34]
        add.cylinder(fist, [0.22, 1.1, 0.2], 0.009, 6, P["wood_dark"])                              # the stick
        add.sphere([0.22, 1.1, 0.2], 0.022, 3, P["wood_dark"])
    figure(at, facing, add.pop())


def princess(at, facing=0.0):
    """The princess, a beauty, standing tall: a rose-pink gown to the floor
    with a gold girdle and hem, long golden hair, a hennin with a gold band
    and a white veil floating from its tip, a gold necklace with a ruby,
    red lips and rosy cheeks, her hands folded before her."""
    arms = (([-0.035, 1.0, 0.19], [1, -0.2, 0.4], [-1, -0.6, -0.3]), ([0.035, 1.0, 0.19], [-1, -0.2, 0.4], [1, -0.6, -0.3]))
    add.push()
    add.mesh(person("stand", gown=P["rose"], female=True, hair=P["straw"], long_hair=True, head="hennin", arms=arms))
    add.polyline([[-0.09, 1.5, 0.07], [-0.05, 1.46, 0.106], [0.0, 1.445, 0.116], [0.05, 1.46, 0.106], [0.09, 1.5, 0.07]], 0.007, 6, P["gold"], smooth=1)
    add.sphere([0, 1.432, 0.12], 0.016, 3, P["red"])
    figure(at, facing, add.pop())


def lady(at, facing, gown, head, hair, table=None, seat=0.54):
    """A lady sitting at the feast: see :func:`person`."""
    figure(at, facing, person("sit", gown=gown, female=True, head=head, hair=hair, long_hair=head != "hennin", table=table, seat=seat))


def guest(at, facing, n, table, seat):
    """Guest number ``n`` at the feast, one of many kinds: ladies in gowns
    with veils, hennins or circlets; men young and old, bearded or not, in
    tunics of all colours and hats, caps and chaperons; now and then a
    monk in his brown habit."""
    h = [hash2(n, k, 61) for k in range(6)]
    if n % 9 == 4:                                                        # a monk
        figure(at, facing, person("sit", gown=P["wood"], trim=P["rope"], hair=P["wood_dark"], beard=P["wood_dark"] if h[1] > 0.5 else None,
                                  table=table, seat=seat))
    elif h[0] < 0.42:                                                     # a lady
        gown = (P["blue"], P["red"], P["purple"], P["leaf"], P["rose"], P["cushion"], P["copper"])[int(h[1] * 7)]
        lady(at, facing, gown, ("veil", "hennin", "circlet", "veil")[int(h[2] * 4)],
             (P["straw"], P["wood_dark"], P["black"], P["trunk"], P["orange"])[int(h[3] * 5)], table, seat)
    else:                                                                 # a man
        tunic = (P["blue"], P["red"], P["purple"], P["leaf"], P["linen"], P["wood_light"], P["copper"], P["cushion"], P["gold"])[int(h[1] * 9)]
        old = h[2] > 0.7
        hair = P["white"] if old else (P["wood_dark"], P["black"], P["trunk"], P["straw"])[int(h[3] * 4)]
        beard = hair if (old or h[4] > 0.6) else None
        head = (None, None, ("chaperon", P["red"]), ("chaperon", P["black"]), ("cap", P["blue"]), ("cap", P["leaf_dark"]))[int(h[5] * 6)]
        figure(at, facing, person("sit", tunic, hat=(head is None and h[4] < 0.2), table=table, seat=seat, hair=hair, beard=beard, head=head))


# --------------------------------------------------------------------------
#  6. Easter egg 1: the great hall -- throne, feast, chandeliers, fireplace
# --------------------------------------------------------------------------
HX0, HX1, HZ0, HZ1 = KX0 + WT, KX1 - WT, KZ0 + WT, KZ1 - WT     # inside the walls, with room to spare
FX0, FX1, FZ0, FZ1 = KX0 + WT / 2 + 0.22, KX1 - WT / 2 - 0.22, KZ0 + WT / 2 + 0.22, KZ1 - WT / 2 - 0.22
                                                                 # the faces of the walls' stones: what hangs on a wall
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
THRONE_S = 0.76                                        # the throne and the king, built large, brought to the size of the castle's people
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
for sx in (-0.66, 0.66):
    add.cuboid([sx, 0.95, 0.05], [0.14, 0.6, 1.2], P["wood_dark"])
    add.cuboid([sx, 1.28, 0.05], [0.18, 0.08, 1.3], P["gold"])
    add.sphere([sx, 1.32, 0.65], 0.1, 8, P["gold"])
add.cuboid([0, 0.7, 0.1], [1.16, 0.16, 1.1], P["cushion"])
add.cuboid([0, 0.17, 1.05], [0.9, 0.34, 0.5], P["cushion"])                     # a footstool
add.cuboid([0, 0.35, 1.05], [0.94, 0.04, 0.54], P["gold"])
add.mesh(add.move(add.stretch(add.pop(), [THRONE_S] * 3, (0, 0, 0)), THRONE))


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


def king(at, facing=0.0, size=1.0):
    """The king on his throne (the throne standing on ``at``, built
    ``size`` times its drawn size): a man like the castle's other people,
    sitting upright with his back to the cushion, his feet on the
    footstool and his forearms on the gold rails of the armrests -- a
    purple robe with an ermine collar, front and cuffs, red hose, black
    shoes with gold buckles, a gold chain with a ruby, white hair, a white
    beard and moustache, the crown on his head, the sceptre upright in his
    right hand and a ring on his left."""
    seat, rail, stool = 0.78 * size, 1.32 * size, 0.37 * size
    hip_z = -0.44 * size + 0.18
    rel = (rail - seat) / LIFE + 0.04
    arms = (([-0.43, rel, 0.3], [0.2, 0.0, 1], [-1, -1, -0.8]), ([0.43, rel, 0.3], [0, -0.3, 1], [1, -1, -0.8]))
    reach = (1.05 * size - hip_z) / LIFE
    add.push()
    add.mesh(person("sit", P["purple"], seat=seat - stool, arms=arms, hose=P["red"], hair=P["white"], reach=reach, lean=0.0))
    add.mesh(add.move(add.stretch(add.make(crown, [0, 0, 0], 0.17), [0.56] * 3, (0, 0, 0)), [0, 0.885, -0.01]))   # the crown
    add.ellipsoid([0, 0.755, 0.07], [0.058, 0.072, 0.042], 3, P["white"])                         # the beard,
    for s in (-1, 1):
        add.capsule([s * 0.012, 0.795, 0.1], [s * 0.05, 0.78, 0.085], 0.01, 6, P["white"])        # the moustache,
        add.ellipsoid([s * 0.03, 0.862, 0.092], [0.02, 0.006, 0.009], 2, P["white"])              # the eyebrows
        add.torus([s * 0.43, rel, 0.28], 0.045, 0.016, 12, 5, P["white"], axis=(0, 0, 1))        # ermine cuffs
        foot = [s * 0.115, 0.09 - (seat - stool) / LIFE, reach]
        add.cuboid([foot[0], foot[1] - 0.03, foot[2] + 0.09], [0.05, 0.02, 0.035], P["gold"])      # shoe buckles
    add.torus([0, 0.675, 0.0], 0.085, 0.03, 16, 6, P["white"])                                     # the ermine collar ...
    add.cuboid([0, 0.43, 0.152], [0.07, 0.44, 0.012], P["white"])                                  # ... and front
    for i in range(4):
        add.sphere([-0.015 + (i % 2) * 0.03, 0.26 + i * 0.1, 0.16], 0.008, 2, P["black"])
    add.polyline([[-0.12, 0.655, 0.09], [0.0, 0.52, 0.152], [0.12, 0.655, 0.09]], 0.009, 6, P["gold"], smooth=1)   # the chain
    add.sphere([0, 0.51, 0.162], 0.018, 3, P["red"])
    fx, fz = -0.43 + 0.2 * 0.03 / add.sqrt(1.04), 0.3 + 0.03 / add.sqrt(1.04)
    add.cylinder([fx, rel - 0.12, fz], [fx + 0.01, rel + 0.6, fz - 0.03], 0.016, 8, P["gold"])     # the sceptre
    add.sphere([fx + 0.01, rel + 0.63, fz - 0.03], 0.035, 4, P["red"])
    add.torus([fx + 0.01, rel + 0.63, fz - 0.03], 0.042, 0.009, 12, 5, P["gold"], axis=(0, 0, 1))
    add.torus([0.43, rel + 0.015, 0.345], 0.026, 0.007, 10, 4, P["gold"], axis=(0, 0, 1))         # the ring
    M = add.move(add.stretch(add.pop(), [LIFE] * 3, (0, 0, 0)), [0, seat, hip_z])
    add.mesh(add.move(add.rotateY(M, facing), at))


king(THRONE, size=THRONE_S)
# a canopy above the throne, the arms on the wall and the name of the castle
add.cuboid([0, KY + 5.0, FZ0 + 0.9], [3.6, 0.15, 1.8], P["red"])
for i in range(12):
    add.cuboid([-1.75 + i * 0.32, KY + 4.82, FZ0 + 1.8], [0.2, 0.25, 0.05], P["gold"])
add.mesh(add.move(arms(3.4, 4.6, 0.06), [-1.7, KY + 0.3, FZ0 + 0.03]))            # the arms on the wall behind the throne
MOTTO = "VENI VIDI VICI"                                                            # a Latin motto over the throne, in gold
TABLET_W = add.text_width(MOTTO, 0.8) + 1.0                                         # letters on a tablet of dark stone, the
add.cuboid([0, KY + 8.1, FZ0 + 0.05], [TABLET_W, 1.5, 0.14], P["stone_dark"])       # tablet's back 2 cm into the wall and the
for y in (KY + 7.38, KY + 8.82):                                                    # letters half sunk into the tablet: all
    add.cuboid([0, y, FZ0 + 0.125], [TABLET_W, 0.06, 0.03], P["gold"])              # fixed to the wall, nothing in the air
for x in (-TABLET_W / 2 + 0.03, TABLET_W / 2 - 0.03):
    add.cuboid([x, KY + 8.1, FZ0 + 0.125], [0.06, 1.5, 0.03], P["gold"])
add.text(MOTTO, [0, KY + 7.7, FZ0 + 0.15], 0.8, 0.06, P["gold"], align="center", k=8)
for s in (-1, 1):                                                                 # torch stands by the dais, guards
    add.cylinder([s * 4.2, KY + 0.64, HZ0 + 1.5], [s * 4.2, KY + 2.4, HZ0 + 1.5], 0.06, 8, P["iron"])
    add.cylinder([s * 4.2, KY + 2.4, HZ0 + 1.5], [s * 4.2, KY + 2.6, HZ0 + 1.5], 0.14, 8, P["iron"])
    add.sphere([s * 4.2, KY + 2.85, HZ0 + 1.5], 0.24, 8, FLAME)
    armour([s * 6.5, KY + 0.04, HZ0 + 1.6], 0, weapon="spear" if s < 0 else "sword", shield=(s > 0))   # (on the floor, beside the dais)
advisor([-1.75, KY + 0.66, HZ0 + 2.0], 0.45)                                        # his counsellor at his right hand,
jester([3.4, KY + 0.04, HZ0 + 5.9], add.atan2(-3.4, -4.5))                          # his fool capering before the dais,
musician([-10.8, KY + 0.04 + 0.46, HZ0 + 2.0], 0.75, "lute")                        # and players by the north wall:
musician([-12.2, KY + 0.04, HZ0 + 2.4], 0.75, "pipe")                               # a lute, a pipe and a drum
musician([-13.6, KY + 0.04, HZ0 + 2.0], 0.75, "drum")
flush("hall: throne")

# the wine cellar: beside the dais a stair goes down through the floor, along the north wall, into a vaulted cellar
# under the hall -- barrels lying on their stillages along the walls, a great tun, racks of bottles, a table for
# tasting with a candle, a jug and cups
X0, X1, Z0, Z1 = CELLAR_ROOM
CY, C_SPRING, CROWN = CELLAR_Y, CELLAR_Y + 2.2, CELLAR_Y + 2.9
W = X1 - X0
R_V = (W * W / 4 + (CROWN - C_SPRING) ** 2) / (2 * (CROWN - C_SPRING))                    # the vault: a flat arch across the cellar
add.cuboid([(X0 + X1) / 2, CY - 0.1, (Z0 + Z1) / 2], [W + 1.0, 0.2, Z1 - Z0 + 1.0], P["stone_dark"])       # the floor
flags = add.Mesh()
for i in range(int(W / 0.8)):
    for j in range(int((Z1 - Z0) / 0.8)):
        flags.extend(add.make(add.cuboid, [X0 + 0.4 + i * 0.8, CY + 0.005, Z0 + 0.4 + j * 0.8], [0.76, 0.01, 0.76], shade_of("stone_dark", (i + j) % 3)))
add.mesh(flags)
for x0, x1, z0, z1 in ((X0 - 0.5, X0, Z0 - 0.5, Z1 + 0.5), (X1, X1 + 0.5, Z0 - 0.5, Z1 + 0.5),
                       (X0, X1, Z0 - 0.5, Z0), (X0, X1, Z1, Z1 + 0.5)):                   # the walls, of stone
    add.cuboid([(x0 + x1) / 2, (CY + CROWN + 0.2) / 2, (z0 + z1) / 2], [x1 - x0, CROWN + 0.2 - CY, z1 - z0], P["stone"])
arc = [[X0 + W * t, CROWN - R_V + add.sqrt(R_V * R_V - (W * (t - 0.5)) ** 2)] for t in [i / 12.0 for i in range(13)]]
vault = add.make(add.prism, arc + [[p[0], p[1] + 0.3] for p in arc[::-1]], Z1 - Z0, P["mortar"], (0, 0, (Z0 + Z1) / 2), (0, 0, 1))
add.mesh(add.color(add.difference(vault, CELLAR_CUT[0]), P["mortar"]))                 # open where the stair comes through
steps = 20
rise, run = (KY - CY) / steps, (CELLAR_STAIR[1] - 0.3 - CELLAR_STAIR[0] - 0.1) / steps
for k in range(steps):                                                                  # the stair, solid stone steps
    x = CELLAR_STAIR[0] + 0.1 + (k + 0.5) * run
    top = KY - (k + 1) * rise
    add.cuboid([x, (top + CY) / 2, Z0 + 0.95], [run + 0.02, top - CY, 1.9], shade_of("stone_dark", k % 3))
for k in range(0, steps + 1, 4):                                                       # its rail on the open side
    x = CELLAR_STAIR[0] + 0.1 + k * run
    y = KY - k * rise
    add.cylinder([x, y - 0.1, Z0 + 1.85], [x, y + 0.9, Z0 + 1.85], 0.035, 6, P["wood_dark"])
add.polyline([[CELLAR_STAIR[0] + 0.1, KY + 0.9, Z0 + 1.85], [CELLAR_STAIR[0] + 0.1 + steps * run, CY + 0.9, Z0 + 1.85]], 0.03, 6, P["wood"])
bal = [[CELLAR_STAIR[0] + 0.6, CELLAR_STAIR[3] + 0.08], [CELLAR_STAIR[1] + 0.08, CELLAR_STAIR[3] + 0.08], [CELLAR_STAIR[1] + 0.08, CELLAR_STAIR[2]]]
for (ax, az), (bx, bz) in zip(bal, bal[1:]):                                            # a stone balustrade round the opening
    n = int(max(abs(bx - ax), abs(bz - az)) / 0.3)
    for i in range(n + 1):
        t = i / float(n)
        add.mesh(add.make(lathe, [[0.0, 0], [0.07, 0], [0.07, 0.05], [0.04, 0.12], [0.07, 0.4], [0.035, 0.7], [0.07, 0.75], [0.0, 0.75]],
                          [ax + (bx - ax) * t, KY, az + (bz - az) * t], 8, P["stone"]))
    add.cuboid([(ax + bx) / 2, KY + 0.8, (az + bz) / 2], [abs(bx - ax) + 0.16, 0.1, abs(bz - az) + 0.16], P["stone"])
for x, rows in ((X0 + 0.7, (-24.6, -23.2, -21.8, -20.6)), (X1 - 0.7, (-23.2, -21.8, -20.6))):   # barrels on their stillages
    for zz in rows:
        b = add.make(barrel, [0, 0, 0], 0.4, 1.0, None, False)
        add.mesh(add.move(add.rotateY(b, add.pi / 2), [x, CY + 0.25, zz]))
    for dx in (-0.3, 0.3):
        add.cuboid([x + dx, CY + 0.125, (rows[0] + rows[-1]) / 2], [0.15, 0.25, rows[-1] - rows[0] + 0.9], P["wood_dark"])
barrel([X1 - 0.9, CY, Z0 + 2.75], 0.75, 1.9)                                             # the great tun
for i in range(3):                                                                      # a rack of bottles on the south wall
    add.cuboid([(X0 + X1) / 2, CY + 0.35 + i * 0.45, Z1 - 0.3], [3.2, 0.04, 0.5], P["wood"])
    for j in range(12):
        bx = (X0 + X1) / 2 - 1.45 + j * 0.265
        add.mesh(add.move(add.rotateX(add.make(lathe, [[0.0, 0], [0.045, 0], [0.045, 0.2], [0.018, 0.27], [0.015, 0.32], [0.0, 0.32]],
                                                   [0, 0, 0], 8, P["dragon_wing"] if (i + j) % 3 else P["wood_dark"]), add.pi / 2),
                          [bx, CY + 0.42 + i * 0.45, Z1 - 0.48]))
for x in ((X0 + X1) / 2 - 1.62, (X0 + X1) / 2 + 1.62):
    add.cuboid([x, CY + 0.7, Z1 - 0.3], [0.06, 1.4, 0.5], P["wood_dark"])
TT = [(X0 + X1) / 2 + 0.6, CY, (Z0 + Z1) / 2 + 1.2]                                     # the tasting table
table(TT, 1.2, 0.8, 0.8, P["wood_dark"])
candle([TT[0] - 0.3, TT[1] + 0.8, TT[2]], 0.25, 0.035)
jug([TT[0] + 0.1, TT[1] + 0.8, TT[2] - 0.1])
for dx in (0.35, 0.5):
    goblet([TT[0] + dx, TT[1] + 0.8, TT[2] + 0.2], wine=True)
stool([TT[0] - 0.9, TT[1], TT[2]], 0.46)
torch([X0, CY + 1.7, (Z0 + Z1) / 2 + 2.0], add.pi / 2)
torch([X1, CY + 1.7, (Z0 + Z1) / 2 + 2.0], -add.pi / 2)
flush("hall: the wine cellar")

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
    DISHES = (chicken_roast, fish_platter, pie, lambda at: (bread([at[0] - 0.12, at[1], at[2] - 0.2], 2), jug([at[0] + 0.2, at[1], at[2] + 0.3])),
              ham, lambda at: (bowl([at[0], at[1], at[2] - 0.1], 0.2, P["wood_light"], (P["apple"], P["orange"], P["apple"], P["cheese"])),
                               grapes([at[0] + 0.25, at[1], at[2] + 0.38])),
              sausages, lambda at: (candelabra(at), jug([at[0] + 0.25, at[1], at[2] + 0.25], P["blue"])),
              cake, lambda at: cheese([at[0] - 0.15, at[1], at[2]]), tureen)
    for k in range(7):                                                           # dishes down the middle, between the places
        z = TABLE_Z0 + 1.0 + 0.825 + k * 1.65
        if tx < 0 and abs(z - zc) < 1.2:                                         # the pig's stretch
            continue
        DISHES[(k + (0 if tx < 0 else 5)) % len(DISHES)]([tx, top, z])
    MORE = (pie, lambda at: bowl(at, 0.2, P["wood_light"], (P["apple"], P["orange"], P["apple"], P["cheese"])), sausages,
            lambda at: (grapes([at[0], at[1], at[2] - 0.22]), bowl([at[0], at[1], at[2] + 0.2], 0.15, P["gold"], (P["orange"], P["apple"]))),
            cake, lambda at: bread([at[0] - 0.05, at[1], at[2]], 1), tureen,
            lambda at: bowl(at, 0.2, P["wood_light"], (P["grape"], P["apple"], P["cheese"])))
    for k in range(8):                                                           # and as many again between the guests
        z = TABLE_Z0 + 1.0 + k * 1.65                                            # facing each other: sixteen of them now
        if tx < 0 and abs(z - zc) < 1.3:
            continue
        MORE[(k + (0 if tx < 0 else 3)) % len(MORE)]([tx, top, z])
    for side in (-1, 1):                                                         # eight guests a side, each at a place laid
        for k in range(8):
            z = TABLE_Z0 + 1.0 + k * 1.65
            place_setting([tx + side * 0.8, top, z], -side)
            guest([tx + side * 1.7, KY + 0.54, z], -side * add.pi / 2, int(tx) * 10 + side * 40 + k + 100, (0.525, 0.6), 0.54)
roast_pig([-6.0, KY + 1.08, (TABLE_Z0 + TABLE_Z1) / 2])
flush("hall: the feast")

# chandeliers, the fireplace, tapestries, weapons on the wall, a chess study
for z in (HZ0 + 6, HALL_MID, HZ1 - 6):
    chandelier([0, KY + 5.5, z], 1.2, HALL_H - 5.5 - 0.6)
# the chimney breast against the west wall: a stone-faced block with the fire in
# a recess between two pilasters, under a moulded mantelpiece
breast = add.make(add.cuboid, [FX0 + 0.5, KY + HALL_H / 2, HALL_MID], [1.0, HALL_H, 5.0], P["mortar"])
recess = add.make(add.cuboid, [FX0 + 0.85, KY + 1.4, HALL_MID], [1.0, 2.8, 3.0])          # open at the front, 0.65 deep
add.mesh(add.color(add.difference(breast, recess), P["mortar"]))
add.cuboid([FX0 + 0.43, KY + 1.72, HALL_MID], [0.15, 2.15, 2.99], P["black"])             # the back, sooty above ...
add.cuboid([FX0 + 0.43, KY + 0.32, HALL_MID], [0.15, 0.64, 2.99], P["brick"])             # ... brick where the fire burns
add.push()
stone_face(5.0, 0, HALL_H, 0, 0.12, "stone_dark", size=(0.7, 0.35), seed=3,
           skip=[(0.7, 4.3, 0, 2.85), (0.45, 4.55, 2.75, 3.4)])                            # the pilasters, the mantel
add.mesh(add.move(add.rotateY(add.pop(), add.pi / 2), [FX0 + 1.0, KY, HALL_MID + 2.5]))   # built along +x, turned to face +x
for sz in (-1, 1):
    jamb = add.make(add.cuboid, [0, 0, 0], [0.62, 2.6, 0.12], P["brick"])                  # the splayed brick sides of the fire
    add.mesh(add.move(add.rotateY(jamb, sz * 0.5), [FX0 + 0.72, KY + 1.4, HALL_MID + sz * 1.3]))
    z = HALL_MID + sz * 1.6
    add.cuboid([FX0 + 1.0, KY + 1.45, z], [1.0, 2.5, 0.4], P["stone"])                    # the pilasters: shaft,
    add.cuboid([FX0 + 1.02, KY + 0.12, z], [1.08, 0.24, 0.5], P["stone_dark"])            # base,
    add.cuboid([FX0 + 1.03, KY + 2.76, z], [1.1, 0.12, 0.5], P["stone_dark"])             # capital,
    add.mesh(add.make(add.prism, [[0, 0], [0.5, 0], [0.5, 0.16], [0.25, 0.45]], 0.34, P["stone"], (FX0 + 1.0, KY + 2.82, z), (0, 0, 1)))   # and a corbel
add.cuboid([FX0 + 1.0, KY + 2.72, HALL_MID], [1.0, 0.26, 2.8], P["stone"])                 # the lintel over the fire,
add.cuboid([FX0 + 1.06, KY + 3.0, HALL_MID], [1.25, 0.3, 4.1], P["stone"])                # a frieze, a moulding
add.cuboid([FX0 + 1.1, KY + 3.19, HALL_MID], [1.35, 0.08, 4.3], P["stone_dark"])           # and the shelf
add.mesh(add.move(add.rotateY(add.move(arms(0.5, 0.62, 0.03), [-0.25, -0.31, 0]), add.pi / 2), [FX0 + 1.52, KY + 2.98, HALL_MID]))  # the arms, carved
add.cuboid([FX0 + 1.3, KY + 0.06, HALL_MID], [1.9, 0.12, 4.2], P["stone_dark"])            # the hearthstone
for sz in (-0.55, 0.55):                                                                   # the andirons: a bar on two feet,
    add.cuboid([FX0 + 0.92, KY + 0.27, HALL_MID + sz], [0.7, 0.05, 0.05], P["iron"])       # an upright at the front and a
    for x in (FX0 + 0.62, FX0 + 1.22):                                                     # brass knob on it
        add.cuboid([x, KY + 0.19, HALL_MID + sz], [0.05, 0.14, 0.14], P["iron"])
    add.cylinder([FX0 + 1.25, KY + 0.12, HALL_MID + sz], [FX0 + 1.25, KY + 0.62, HALL_MID + sz], 0.03, 8, P["iron"])
    add.sphere([FX0 + 1.25, KY + 0.67, HALL_MID + sz], 0.06, 4, P["gold"])
for x, y in ((FX0 + 0.78, KY + 0.38), (FX0 + 1.06, KY + 0.38), (FX0 + 0.92, KY + 0.6)):      # three logs across them,
    add.cylinder([x, y, HALL_MID - 0.85], [x, y, HALL_MID + 0.85], 0.12, 10, P["trunk"])
    for sz in (-1, 1):
        add.cylinder([x, y, HALL_MID + sz * 0.85], [x, y, HALL_MID + sz * 0.86], 0.11, 10, P["wood_light"])   # their sawn ends
for i in range(14):                                                                        # a bed of glowing embers under them
    x, z = FX0 + 0.62 + 0.62 * hash2(i, 1, 41), HALL_MID - 0.8 + 1.6 * hash2(i, 2, 41)
    add.ellipsoid([x, KY + 0.14, z], [0.09, 0.04, 0.09], 3, P["orange"] if i % 3 else P["flame_core"])
for i in range(9):                                                                         # and the flames: tongues licking up
    z = HALL_MID - 0.7 + 1.4 * i / 8.0
    h = 0.55 + 0.55 * hash2(i, 3, 41)
    base = [FX0 + 0.85 + 0.12 * (hash2(i, 4, 41) - 0.5), KY + 0.5, z]
    add.cone(base, [base[0] - 0.08, base[1] + h, z + 0.15 * (hash2(i, 5, 41) - 0.5)], 0.16 + 0.06 * hash2(i, 6, 41), 8, FLAME)
    if i % 2 == 0:
        add.cone([base[0] + 0.03, base[1] - 0.05, z], [base[0], base[1] + h * 0.55, z], 0.09, 6, P["flame_core"])
TOOLS = [FX0 + 1.75, KY + 0.12, HALL_MID + 2.45]                                            # the fire irons on their stand:
add.cylinder([TOOLS[0], TOOLS[1], TOOLS[2]], [TOOLS[0], TOOLS[1] + 0.03, TOOLS[2]], 0.16, 10, P["iron"])
add.cylinder([TOOLS[0], TOOLS[1], TOOLS[2]], [TOOLS[0], TOOLS[1] + 0.85, TOOLS[2]], 0.02, 6, P["iron"])
add.torus([TOOLS[0], TOOLS[1] + 0.8, TOOLS[2]], 0.09, 0.012, 12, 4, P["iron"])
for i, kind in enumerate(("poker", "shovel", "tongs", "brush")):                           # poker, shovel, tongs and brush
    a = add.pi / 2 * i + 0.4
    top = [TOOLS[0] + 0.09 * add.cos(a), TOOLS[1] + 0.8, TOOLS[2] + 0.09 * add.sin(a)]
    foot = [TOOLS[0] + 0.14 * add.cos(a), TOOLS[1] + 0.06, TOOLS[2] + 0.14 * add.sin(a)]
    add.cylinder(top, foot, 0.01, 6, P["iron"])
    add.sphere(top, 0.022, 3, P["gold"])
    if kind == "shovel":
        add.cuboid([foot[0], foot[1] + 0.06, foot[2]], [0.13, 0.14, 0.01], P["iron"])
    elif kind == "brush":
        add.cylinder([foot[0], foot[1], foot[2]], [foot[0], foot[1] + 0.12, foot[2]], 0.045, 8, P["straw"])
    elif kind == "tongs":
        add.cylinder([top[0] + 0.02, top[1], top[2]], [foot[0] + 0.04, foot[1], foot[2]], 0.008, 6, P["iron"])
add.cylinder([FX0 + 1.75, KY + 0.12, HALL_MID - 2.45], [FX0 + 1.75, KY + 0.55, HALL_MID - 2.45], 0.3, 14, P["straw"])   # a basket of logs
for i in range(5):
    a = i * 1.3
    add.cylinder([FX0 + 1.75 + 0.14 * add.cos(a), KY + 0.3, HALL_MID - 2.45 + 0.14 * add.sin(a)],
                 [FX0 + 1.75 + 0.2 * add.cos(a + 0.4), KY + 0.8, HALL_MID - 2.45 + 0.2 * add.sin(a + 0.4)], 0.06, 8, P["trunk"])
bell = add.make(add.ellipsoid, [0, 0, 0], [0.16, 0.05, 0.24], 4, P["wood_dark"])            # the bellows, leant on the pilaster
bell.extend(add.make(add.cone, [0, 0, -0.2], [0, 0, -0.42], 0.035, 6, P["gold"]))
bell.extend(add.make(add.cuboid, [0, 0, 0.3], [0.05, 0.03, 0.16], P["wood"]))
add.mesh(add.move(add.rotateX(bell, -1.3), [FX0 + 1.6, KY + 0.45, HALL_MID + 1.95]))
candelabra([FX0 + 1.0, KY + 3.23, HALL_MID - 1.4])
goblet([FX0 + 1.0, KY + 3.23, HALL_MID + 1.4])
shield([FX0 + 1.12 + 0.04, KY + 5.2, HALL_MID], add.pi / 2, 0.6)                          # arms hung on the chimney breast
sword([FX0 + 1.12 + 0.07, KY + 3.5, HALL_MID - 0.9], (0, 1, 0.7), side=(0, 0.7, -1))         # a pair of swords hung flat below it
sword([FX0 + 1.12 + 0.07, KY + 3.5, HALL_MID + 0.9], (0, 1, -0.7), side=(0, 0.7, 1))
for z in (HALL_MID - 4.0, HALL_MID + 4.0):                                                # tapestries on the west and east walls,
    for x, sg in ((FX0, 1), (FX1, -1)):                                                   # clear of the windows, the towers and
        M = add.rotateY(add.move(arms(2.4, 3.6, 0.04), [-1.2, -1.8, 0]), sg * add.pi / 2)  # the fireplace, hanging from a rod
        add.mesh(add.move(M, [x + sg * 0.03, KY + 4.5, z]))
        add.cylinder([x + sg * 0.06, KY + 6.36, z - 1.4], [x + sg * 0.06, KY + 6.36, z + 1.4], 0.05, 8, P["wood_dark"])
for x in (-13.25, 13.25):                                                                 # torches on the long walls, between windows
    torch([x, KY + 3.0, FZ0], 0)
    torch([x, KY + 3.0, FZ1], add.pi)
chess_study([HX1 - 5.5, KY + 0.04, HZ1 - 9.0])
for bx, bz, up in ((HX1 - 0.6, HZ0 + 4.4, True), (HX1 - 0.6, HZ0 + 5.4, True), (HX1 - 1.7, HZ0 + 4.9, False)):
    assert not near_tower(bx, bz, 0.42 + 0.6)                                             # a few barrels of wine by the east
    barrel([bx, KY + 0.04, bz], 0.42, 1.1, upright=up)                                    # wall, clear of the corner tower
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
    sleeping = j % 3 != 1
    bed([x, FLOOR2, z], facing, sleeper=sleeping)
    chest([x, FLOOR2, z + (1.9 if facing == 0 else -1.9)], 0, s=0.6)     # a chest at the foot of every bed
    if not sleeping:
        armour([x + 1.2, FLOOR2 + 0.1, z + (0.5 if facing == 0 else -0.5)], facing + add.pi, weapon="none", shield=False, plume=False)  # armour on a stand
        add.cuboid([x + 1.2, FLOOR2 + 0.05, z + (0.5 if facing == 0 else -0.5)], [0.6, 0.1, 0.6], P["wood_dark"])
    for k in range(2):                                                 # boots by the bed
        add.cuboid([x - 0.7 + k * 0.28, FLOOR2 + 0.12, z + (0.4 if facing == 0 else -0.4)], [0.22, 0.24, 0.5], P["black"])
for row, (z, facing) in enumerate(((DZ0 + 6.4, 0.0), (DZ0 + 9.6, add.pi))):   # and bunks for the rest of the garrison, two
    for i, x in enumerate((4.5, 6.7, 8.9, 11.1, 13.3, 15.5, 17.7, 19.9)):   # rows back to back, west and east of the attic
        for sx in (-1, 1):                                             # stair (the last four for the gunners)
            k = row * 14 + i * 2 + (sx + 1) // 2 if i < 7 else 28 + row * 2 + (sx + 1) // 2
            assert not near_tower(sx * x, z, 1.7)
            bunk([sx * x, FLOOR2, z], facing, (k % 7 == 3, k % 11 == 5),
                 ((P["blue"], P["red"], P["leaf_dark"], P["wood_light"])[k % 4], (P["red"], P["slate"], P["blue"])[k % 3]))
MESS = HALL_MID + 4.0                                                  # where the soldiers eat
table([0, FLOOR2, MESS], 6.0, 1.2, 0.8)                            # the long table, clear of the attic stair
for sx in (-1.0, 1.0):
    add.cuboid([0, FLOOR2 + 0.45, MESS + sx], [5.6, 0.08, 0.35], P["wood"])
    for dx in (-2.5, 2.5):
        add.cuboid([dx, FLOOR2 + 0.22, MESS + sx], [0.3, 0.44, 0.3], P["wood_dark"])
candle([0, FLOOR2 + 0.8, MESS], 0.4, 0.05)
jug([1.2, FLOOR2 + 0.8, MESS - 0.3])
goblet([-0.9, FLOOR2 + 0.8, MESS + 0.2], wine=True)
bread([-2.0, FLOOR2 + 0.8, MESS], 2)
sitting_man([-1.0, FLOOR2 + 0.5, MESS - 1.0], 0, P["blue"], (0.3, 0.4), seat=0.5)
sitting_man([1.4, FLOOR2 + 0.5, MESS + 1.0], add.pi, P["leaf"], (0.3, 0.4), seat=0.5)
for i in range(5):                                                     # spears leaning on a rail on the east wall,
    z = KZ0 + 7.1 + i * 0.45                                           # between two windows
    add.cylinder([FX1 - 0.35, FLOOR2 + 0.02, z], [FX1 - 0.07, FLOOR2 + 3.4, z], 0.035, 8, P["wood"])
    add.cone([FX1 - 0.07, FLOOR2 + 3.4, z], [FX1 - 0.03, FLOOR2 + 3.85, z], 0.07, 8, P["steel"])
add.cuboid([FX1 - 0.05, FLOOR2 + 2.6, KZ0 + 8.0], [0.1, 0.12, 2.3], P["wood_dark"])       # the rail
for zz in (12.3, 15.7, 19.4, 20.6):                                    # shields on pegs: two by the door to the chapel's
    z = KZ0 + zz                                                       # attic, two between the next windows
    add.cylinder([FX1, FLOOR2 + 3.2, z], [FX1 - 0.12, FLOOR2 + 3.22, z], 0.02, 6, P["iron"])
    add.cuboid([FX1 - 0.07, FLOOR2 + 3.15, z], [0.02, 0.12, 0.05], P["wood_dark"])           # the strap over the peg
    shield([FX1 - 0.05, FLOOR2 + 2.2, z], -add.pi / 2, 0.45)
# the chimney breast of the fireplace below passes through here, warm to sleep beside
brick_box([FX0 + 0.5, FLOOR2 + UPPER_H / 2, HALL_MID], [1.0, UPPER_H, 3.0])
add.cuboid([FX0 + 0.7, FLOOR2 + 0.45, HALL_MID + 2.4], [1.2, 0.9, 1.2], P["iron"])          # an iron stove beside it,
add.cylinder([FX0 + 0.7, FLOOR2 + 0.9, HALL_MID + 2.4], [FX0 + 0.7, FLOOR2 + 1.6, HALL_MID + 2.4], 0.12, 12, P["iron"])
add.cylinder([FX0 + 0.7, FLOOR2 + 1.6, HALL_MID + 2.4], [FX0 + 0.7, FLOOR2 + 1.6, HALL_MID + 1.45], 0.12, 12, P["iron"])   # its pipe into the flue
for x in (-13.9, 13.9):                                                # torches between the windows, clear of the beds
    torch([x, FLOOR2 + 2.6, FZ0], 0)
    torch([x, FLOOR2 + 2.6, FZ1], add.pi)
# the wooden stair up to the attic hatch (the hatch is in the attic floor at
# HATCH): open treads housed in two stringers, a newel post at the foot and
# at the head on each side, and a handrail on a baluster at every step
STAIR_STEPS = 14
RUN, RISE = 0.5, UPPER_H / STAIR_STEPS
STAIR_FOOT = HOLE[2] + STAIR_STEPS * RUN                              # the top step ends where the attic floor begins


def nosing_y(z):
    """The line over the front edges of the treads, at ``z``."""
    return FLOOR2 + RISE + (STAIR_FOOT - z) * RISE / RUN


for i in range(STAIR_STEPS):                                          # the treads, each a little over the one below
    add.cuboid([HATCH[0], FLOOR2 + (i + 1) * RISE - 0.03, STAIR_FOOT - (i + 0.5) * RUN + 0.015], [1.62, 0.06, RUN + 0.03],
               shade_of("wood", i))
z_lo, z_hi = STAIR_FOOT + 0.094, STAIR_FOOT - (STAIR_STEPS - 1) * RUN
rail_lo, rail_hi = (FLOOR2 + 1.2, STAIR_FOOT + 0.05), (EAVE + 0.95, z_hi - 0.05)
for s in (-1, 1):
    x = HATCH[0] + s * 0.85
    add.beam([x, nosing_y(z_lo) - 0.14, z_lo], [x, nosing_y(z_hi) - 0.14, z_hi], 0.08, 0.3, P["wood_dark"])      # a stringer
    for z, y0, y1 in ((rail_lo[1], FLOOR2, rail_lo[0] + 0.05), (rail_hi[1], nosing_y(z_hi) - 0.3, rail_hi[0] + 0.05)):
        add.cuboid([x, (y0 + y1) / 2, z], [0.14, y1 - y0, 0.14], P["wood_dark"])                              # newel posts,
        add.sphere([x, y1 + 0.06, z], 0.09, 8, P["wood_dark"])                                               # capped
    add.cylinder([x, rail_lo[0], rail_lo[1]], [x, rail_hi[0], rail_hi[1]], 0.035, 8, P["wood"])             # the handrail
    for i in range(STAIR_STEPS):
        z = STAIR_FOOT - (i + 0.5) * RUN
        y_rail = rail_lo[0] + (rail_lo[1] - z) * (rail_hi[0] - rail_lo[0]) / (rail_lo[1] - rail_hi[1])
        add.cuboid([x, (nosing_y(z) + y_rail) / 2 - 0.05, z], [0.04, y_rail - nosing_y(z) + 0.1, 0.04], P["wood_dark"])
flush("dormitory")

# the attic: rafters, and everything nobody uses any more
XC, ZC = (KX0 + KX1) / 2, (KZ0 + KZ1) / 2
for sg, dormers in ((1, PALACE_DORMERS), (-1, PALACE_DORMERS_N)):      # rafters under the two long slopes, none through
    xs = [KX0 + INSET + i * 2.5 for i in range(int((KX1 - KX0 - 2 * INSET) / 2.5) + 1)]   # a dormer's bay: a pair
    xs = [x for x in xs if all(abs(x - d) > 2.1 for d in dormers)]                     # beside each instead
    for x in sorted(xs + [d + s * 1.35 for d in dormers for s in (-1, 1)]):
        hz = (KZ1 - KZ0) / 2 - 0.2                                                     # under the boards, not in them
        add.beam([x, EAVE + 0.15, ZC + sg * (hz - 0.9)], [x, EAVE + ROOF_H - 0.95, ZC], 0.18, 0.3, P["wood_dark"])
add.beam([KX0 + INSET, EAVE + ROOF_H - 1.0, ZC], [KX1 - INSET, EAVE + ROOF_H - 1.0, ZC], 0.25, 0.3, P["wood_dark"])   # the ridge beam
add.seed(23)
ATTIC_X = list(range(int(KX0 + 4), int(KX1 - 3), 4))
ATTIC_BUSY = [(HOLE[0] - 0.4, HOLE[1] + 0.4, HOLE[2] - 0.4, HOLE[3] + 0.4),      # what takes up the floor: the stairwell and
              (HATCH[0] - 3.5, HATCH[0] + 3.5, HOLE[2] - 3.0, HOLE[2])]          # the landing at its head, where one turns,
ATTIC_BUSY += [(d - 1.7, d + 1.7, KZ1 - 3.5, KZ1) for d in PALACE_DORMERS]          # the dormers' bays,
ATTIC_BUSY += [(d - 1.7, d + 1.7, KZ0, KZ0 + 3.5) for d in PALACE_DORMERS_N]
for k, x in enumerate(ATTIC_X):
    kind = k % 7
    zz = KZ0 + 6 + (k % 3) * 6
    if abs(x - HATCH[0]) < 2.5 and abs(zz - HATCH[1]) < 3:
        zz += 6
    ATTIC_BUSY.append((x - 1.8, x + 2.4, zz - 1.6, zz + 1.6))                    # and the old things
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
    elif kind == 3:                                                   # a rolled carpet and five spears
        add.mesh(add.move(add.make(add.cylinder, [0, 0, -1.5], [0, 0, 1.5], 0.3, k_(12), P["red"]), [x, EAVE + 0.3, zz]))
        for i in range(5):                                            # lying on the floor beside it
            sp = add.rotateY(add.rotateX(add.make(spear, [0, 0, 0], 2.6), add.pi / 2), 0.03 * (i - 2))
            add.mesh(add.move(sp, [x + 0.95 + 0.13 * i, EAVE + 0.05, zz - 1.5 + 0.08 * (i % 2)]))
    elif kind == 4:                                                   # crates, a birdcage and an old shield
        crate([x, EAVE, zz], 0.8)
        crate([x, EAVE + 0.8, zz], 0.7)
        bx = x + 1.3                                                  # the birdcage: a base, bars meeting in a dome,
        add.cylinder([bx, EAVE, zz], [bx, EAVE + 0.04, zz], 0.3, 16, P["iron"])      # a hoop, a ring to hang it by,
        add.pipe([bx, EAVE + 0.38, zz], [bx, EAVE + 0.41, zz], 0.295, 0.265, 16, P["iron"])   # a perch -- and the
        for i in range(10):                                           # canary still in it
            c, sn = add.cos(2 * add.pi * i / 10), add.sin(2 * add.pi * i / 10)
            add.polyline([[bx + 0.28 * c, EAVE + 0.04, zz + 0.28 * sn], [bx + 0.28 * c, EAVE + 0.45, zz + 0.28 * sn],
                          [bx + 0.2 * c, EAVE + 0.6, zz + 0.2 * sn], [bx + 0.08 * c, EAVE + 0.67, zz + 0.08 * sn],
                          [bx, EAVE + 0.69, zz]], 0.01, 4, P["iron"])
        add.torus([bx, EAVE + 0.755, zz], 0.055, 0.012, 12, 6, P["iron"], axis=(1, 0, 0))
        add.cylinder([bx - 0.27, EAVE + 0.22, zz], [bx + 0.27, EAVE + 0.22, zz], 0.012, 6, P["wood"])
        add.sphere([bx, EAVE + 0.285, zz], 0.055, 8, P["cheese"])
        add.sphere([bx + 0.05, EAVE + 0.34, zz], 0.035, 8, P["cheese"])
        add.cone([bx + 0.08, EAVE + 0.34, zz], [bx + 0.115, EAVE + 0.335, zz], 0.012, 5, P["orange"])
        add.push()                                                    # the shield lies on its back: it would not
        shield([0, 0, 0], 0, 0.45)                                    # stand on its edge by itself
        flat = add.move(add.rotateX(add.pop(), -add.pi / 2), [0, 0, 0.45])
        add.mesh(add.move(add.rotateY(flat, 0.4), [x - 1.2, EAVE + 0.03, zz + 0.3]))
    elif kind == 5:                                                   # a dusty armour stand, a cradle
        armour([x, EAVE + 0.1, zz], 0.3, weapon="none", shield=False, plume=False)
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


def mouse(at, facing=0.0, phase=0.0):
    """A little grey mouse scampering over the boards: a round body and
    head, a pointed pink nose, big round ears, black eyes, whiskers, its
    legs in mid-stride (``phase`` changes the stride) and a long thin tail
    curving behind."""
    add.push()
    add.ellipsoid([0, 0.035, 0], [0.032, 0.028, 0.055], 4, P["rock"])
    add.ellipsoid([0, 0.042, 0.062], [0.022, 0.02, 0.03], 4, P["rock"])
    add.cone([0, 0.04, 0.085], [0, 0.036, 0.105], 0.01, 6, P["pig"])
    for sd in (-1, 1):
        add.mesh(add.move(add.rotateY(add.stretch(add.make(add.sphere, [0, 0, 0], 0.013, 3, P["pig"]), [1.0, 1.0, 0.35], (0, 0, 0)), sd * 0.4),
                          [sd * 0.017, 0.062, 0.052]))
        add.sphere([sd * 0.013, 0.05, 0.078], 0.004, 2, P["black"])
        add.cylinder([sd * 0.006, 0.04, 0.096], [sd * 0.04, 0.045, 0.1], 0.0015, 3, P["white"])
        for k, z in enumerate((0.03, -0.03)):                                      # legs in mid-stride
            swing = 0.018 * add.sin(phase + k * add.pi + (sd + 1) * 0.8)
            add.cylinder([sd * 0.018, 0.02, z], [sd * 0.022, 0.002, z + swing], 0.005, 4, P["pig"])
    add.polyline([[0, 0.03, -0.05], [0.015, 0.02, -0.09], [-0.012, 0.012, -0.13], [0.02, 0.008, -0.17], [0.01, 0.006, -0.2]],
                 0.003, 4, P["pig"], smooth=1)
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))




def attic_free(x0, x1, z0, z1):
    """Is the rectangle clear of everything on the attic floor?"""
    return all(x1 <= b[0] or x0 >= b[1] or z1 <= b[2] or z0 >= b[3] for b in ATTIC_BUSY)


# the attic is where the guests of the feast and the king's people sleep: rows of beds lengthwise under the roof, between
# the old things, clear of the stairwell and the dormers, low along the eaves and high under the ridge
ATTIC_BEDS = []
for z in (KZ0 + 3.5, KZ0 + 8.8, KZ0 + 15.0, KZ0 + 21.0, KZ1 - 3.5):
    for x in [-12.5 + 2.5 * i for i in range(11)] + [-15.0, 15.0]:
        if attic_free(x - 1.25, x + 1.25, z - 0.7, z + 0.7):
            ATTIC_BEDS.append((x, z))
            ATTIC_BUSY.append((x - 1.1, x + 1.1, z - 0.55, z + 0.55))
for j, (x, z) in enumerate(ATTIC_BEDS):
    bed([x, EAVE, z], add.pi / 2 if j % 2 else -add.pi / 2, sleeper=j % 9 == 4,
        blanket=(P["blue"], P["leaf_dark"], P["red"], P["purple"], P["wood_light"])[j % 5])
mice = []
for x, z, f in ((-7.9, -23.9, 0.4), (4.1, -12.2, 2.1), (8.2, -18.1, -0.8), (-3.9, -7.2, 3.9), (14.6, -18.3, 1.3),
                (-13.1, -12.0, 4.8), (HATCH[0] + 3, HATCH[1] - 1.2, 1.2), (-10.6, -18.2, 2.6), (11.8, -7.3, 5.5)):
    if attic_free(x - 0.15, x + 0.15, z - 0.2, z + 0.2) and len(mice) < 7:
        mice.append((x, z, f))
assert len(mice) >= 5, mice
for i, (mx_, mz_, mf) in enumerate(mice):
    mouse([mx_, EAVE + 0.001, mz_], mf, i * 1.3)                                  # mice about the attic floor
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
    goblet([x, heap_y(x, z), z], s=1.8)
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


def dragon_head(fire=True):
    """The dragon's head, built looking along +x with +y up, the back of the
    skull at the origin: a long wedge of skull and snout under heavy brows,
    glowing eyes with slit pupils, a ridged nose with flared nostrils and a
    horn on it; the lower jaw dropped wide open on rows of fangs, the long
    canines top and bottom, a dark red mouth and a forked tongue; a pair of
    great horns swept back and a smaller pair under them, spikes along the
    crown, frills of spines behind the jaws; scales in two greens, a pale
    throat -- and a jet of fire out of the open jaws."""
    add.push()
    G_, D_, B_, M_ = P["dragon"], P["dragon_wing"], P["bone"], P["cushion"]

    def sgnpow(v, e):
        return abs(v) ** e * (1 if v >= 0 else -1)

    def ring(x, w, top, bot, n=20):
        """A cross-section: a rounded box ``w`` either side, from ``bot`` up to ``top``."""
        c, h = (top + bot) / 2, (top - bot) / 2
        return [[x, c + h * sgnpow(add.cos(2 * add.pi * j / n), 0.7), w * sgnpow(add.sin(2 * add.pi * j / n), 0.7)] for j in range(n)]

    def at(table, x, k):
        """Column ``k`` of a table of sections, at ``x`` (between its rows)."""
        for (x0, *a), (x1, *b) in zip(table, table[1:]):
            if x <= x1:
                t = add.clamp((x - x0) / (x1 - x0))
                return a[k - 1] + (b[k - 1] - a[k - 1]) * t
        return table[-1][k]

    def scales(q, pale):
        """Two greens in patches like scales; ``pale`` parts in plates."""
        if pale(q):
            return P["dragon_belly"] if int(q[0] * 11) % 2 else P["grass_dry"]
        return D_ if hash2(int(q[0] * 16), int(q[2] * 16 + q[1] * 11 + 40), 23) < 0.3 else G_

    SKULL = [(-0.1, 0.19, 0.21, -0.17), (0.05, 0.27, 0.31, -0.19), (0.25, 0.29, 0.35, -0.15), (0.45, 0.23, 0.29, -0.06),
             (0.62, 0.17, 0.19, -0.05), (0.85, 0.15, 0.14, -0.05), (1.05, 0.14, 0.12, -0.05), (1.18, 0.13, 0.14, -0.045),
             (1.28, 0.1, 0.11, -0.04), (1.34, 0.04, 0.06, -0.03)]          # (x, half-width, top, bottom): the skull and snout
    head = add.make(add.loft, [ring(*r) for r in SKULL], G_)
    add.mesh(add.color_by(head, lambda q: M_ if q[0] > 0.45 and q[1] < -0.035 else scales(q, lambda q: q[1] < -0.1)))   # palate red,
                                                                                              # the throat pale
    for s in (-1, 1):
        brow = add.make(add.ellipsoid, [0, 0, 0], [0.25, 0.07, 0.09], 4, D_)                     # the heavy brows,
        add.mesh(add.move(add.rotateZ(brow, -0.4), [0.37, 0.3, s * 0.18]))                       # frowning over the eyes
        add.cone([0.2, 0.35, s * 0.21], [-0.02, 0.44, s * 0.29], 0.045, 6, B_)                   # a spine back from each brow
        add.ellipsoid([0.1, 0.03, s * 0.25], [0.2, 0.1, 0.07], 4, D_)                            # the cheek over the jaw
        add.ellipsoid([0.425, 0.21, s * 0.19], [0.1, 0.06, 0.04], 4, P["black"])                 # the eyes, glowing deep
        add.ellipsoid([0.435, 0.21, s * 0.205], [0.085, 0.048, 0.04], 4, P["orange"])            # in their sockets,
        add.ellipsoid([0.45, 0.21, s * 0.243], [0.01, 0.042, 0.007], 3, P["black"])              # with slit pupils
        ridge = add.make(add.ellipsoid, [0, 0, 0], [0.26, 0.03, 0.035], 4, D_)                  # the ridges of the nose,
        add.mesh(add.move(add.rotateZ(ridge, -0.05), [0.95, 0.13, s * 0.075]))
        nostril = add.make(add.ellipsoid, [0, 0, 0], [0.04, 0.022, 0.026], 4, P["black"])        # the nostrils, flared
        add.mesh(add.move(add.rotateY(nostril, s * 0.5), [1.255, 0.085, s * 0.058]))
        add.torus([1.25, 0.09, s * 0.06], 0.03, 0.012, 8, 4, D_, axis=(0.5, 0.3, s * 0.8))
        horn = [[0.02, 0.27, s * 0.15], [-0.18, 0.42, s * 0.21], [-0.4, 0.55, s * 0.27], [-0.66, 0.58, s * 0.31],
                [-0.86, 0.5, s * 0.33], [-0.97, 0.38, s * 0.33]]
        add.polyline(horn, lambda t: 0.1 * (1 - 0.93 * t), 10, B_, smooth=2)                     # the great horns
        for j in range(4):                                                                        # ridged at the root
            c = [horn[0][k] + (horn[1][k] - horn[0][k]) * (0.3 + 0.35 * j) for k in range(3)]
            d = vunit(vsub(horn[1], horn[0]))
            add.torus(c, 0.093 - 0.009 * j, 0.013, 10, 4, P["linen"], axis=d)
        add.polyline([[-0.02, 0.1, s * 0.22], [-0.23, 0.16, s * 0.32], [-0.45, 0.16, s * 0.4], [-0.6, 0.1, s * 0.44]],
                     lambda t: 0.065 * (1 - 0.9 * t), 8, B_, smooth=2)                              # and a smaller pair
        for j in range(4):                                                                        # a frill of spines behind
            b = [0.0 - 0.08 * j, -0.05 - 0.035 * j, s * (0.22 - 0.01 * j)]                       # each jaw
            add.cone(b, [b[0] - 0.17 - 0.03 * j, b[1] - 0.03 - 0.02 * j, b[2] + s * (0.1 + 0.03 * j)], 0.045, 6, B_)
        for i in range(9):                                                                        # the upper teeth, fangs
            x = 0.5 + 0.09 * i                                                                   # among them
            w, y = 0.86 * at(SKULL, x, 1), at(SKULL, x, 3) + 0.01
            L, r = (0.24, 0.035) if i == 6 else (0.08 + 0.03 * (i % 2), 0.024)
            add.cone([x, y, s * w], [x - 0.02, y - L, s * (w - 0.015)], r, 6, B_)
        add.cone([1.29, -0.035, s * 0.03], [1.28, -0.09, s * 0.03], 0.015, 5, B_)
    add.cone([1.12, 0.13, 0], [1.21, 0.27, 0], 0.035, 6, B_)                                     # the horn on the nose
    for j in range(5):                                                                            # spikes along the crown
        x = 0.52 - 0.14 * j
        y = at(SKULL, x, 2) - 0.01
        add.cone([x, y, 0], [x - 0.05, y + 0.07 + 0.025 * j, 0], 0.035 + 0.006 * j, 6, P["red"])
    add.push()                                                                                    # the lower jaw, hinged
    JAW = [(0.27, 0.2, -0.03, -0.16), (0.45, 0.17, -0.035, -0.17), (0.7, 0.14, -0.035, -0.14),        # under the eyes
           (0.95, 0.125, -0.035, -0.12), (1.12, 0.105, -0.035, -0.12), (1.22, 0.075, -0.04, -0.11), (1.28, 0.03, -0.05, -0.085)]
    jaw = add.make(add.loft, [ring(*r, n=16) for r in JAW], G_)
    add.mesh(add.color_by(jaw, lambda q: M_ if q[1] > -0.05 and q[0] > 0.3 else scales(q, lambda q: q[1] < -0.1)))
    add.ellipsoid([0.66, -0.03, 0], [0.34, 0.022, 0.07], 4, P["red"])                            # the tongue,
    for s in (-1, 1):
        add.cone([0.97, -0.028, s * 0.012], [1.1, -0.018, s * 0.065], 0.02, 5, P["red"])           # forked
        for i in range(8):                                                                        # the lower teeth
            x = 0.48 + 0.1 * i
            w = 0.84 * at(JAW, x, 1)
            L, r = (0.17, 0.03) if i == 6 else (0.07 + 0.025 * (i % 2), 0.021)
            add.cone([x, -0.04, s * w], [x + 0.015, -0.04 + L, s * (w - 0.012)], r, 6, B_)
    add.mesh(add.rotateZ(add.pop(), -0.55, (0.32, -0.08, 0)))                                     # dropped wide open
    if fire:                                                                                      # fire: a widening jet,
        mouth, end = [0.8, -0.18, 0], [1.9, -0.5, 0]                                              # a hot core, billows at
        add.cone(end, mouth, 0.27, 14, FLAME)                                                     # its end, and sparks
        add.cone([1.55, -0.4, 0], mouth, 0.11, 10, P["flame_core"])
        for i, (dx, dy, dz, r) in enumerate(((0.0, 0.0, 0.0, 0.27), (0.1, 0.08, 0.14, 0.18), (0.08, -0.07, -0.15, 0.19), (0.2, 0.04, 0.02, 0.14))):
            add.sphere([end[0] + dx, end[1] + dy, end[2] + dz], r, 8, FLAME)
        for i in range(6):
            add.sphere([1.3 + 0.11 * i, -0.28 - 0.05 * i + 0.1 * add.sin(i * 2.3), 0.17 * add.cos(i * 1.7)], 0.022, 4, P["flame_core"])
    return add.pop()


def catmull(keys, step=0.12):
    """Points along a smooth curve through the ``keys`` (a Catmull-Rom
    spline), about ``step`` apart, and for each the index of the segment
    and the fraction along it."""
    out = []
    n = len(keys)
    for i in range(n - 1):
        p0, p1, p2, p3 = keys[max(0, i - 1)], keys[i], keys[i + 1], keys[min(n - 1, i + 2)]
        m = max(2, int(vlen(vsub(p2, p1)) / step))
        for j in range(m + (1 if i == n - 2 else 0)):
            t = j / float(m)
            out.append(([0.5 * (2 * p1[k] + (p2[k] - p0[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t * t
                                + (3 * p1[k] - p0[k] - 3 * p2[k] + p3[k]) * t * t * t) for k in range(3)], i, t))
    return out


def dragon(at, facing=0.0, size=1.0):
    """A green dragon standing guard on the heap of gold: one smooth body
    from the head down the neck, over the back and along the tail, which
    drapes off the heap and lies curled on the floor; four legs with claws
    planted on the gold; great wings half raised, each an arm and three
    long fingers with the skin stretched between them and back to the
    flank -- clear of the body and of everything round it; a red crest from
    the crown to the tail; and the head turned to the door of the hall,
    jaws open on a jet of fire."""
    add.push()

    def ground(x, z):                                                      # the gold (or the floor) under a point
        return 0.45 * add.sqrt(max(0.0, HEAP_R * HEAP_R - (x * x + z * z) * size * size)) / size

    F = vunit([0.9, -0.3, 0.42])                                           # where the head looks: the door of the hall
    nape = [2.8, 3.85, 0.4]
    keys = [nape, [2.35, 3.55, 0.22], [2.0, 3.05, 0.1], [1.75, 2.65, 0.03], [1.3, 2.4, 0.0], [0.0, 2.3, 0.0],
            [-1.4, 2.2, 0.0], [-2.15, 1.75, -0.15], [-2.65, 1.05, -0.55], [-2.9, 0.3, -1.25], [-2.75, 0.24, -2.05],
            [-2.15, 0.19, -2.7], [-1.35, 0.14, -3.0], [-0.7, 0.07, -3.05]]
    key_r = [0.2, 0.26, 0.33, 0.42, 0.62, 0.56, 0.5, 0.42, 0.34, 0.28, 0.22, 0.17, 0.12, 0.05]
    line = catmull(keys)
    pts = [q for q, i, t in line]
    rads = [key_r[i] + (key_r[min(i + 1, len(key_r) - 1)] - key_r[i]) * t for q, i, t in line]
    body = add.make(add.polyline, pts, lambda t: rads[min(len(rads) - 1, int(round(t * (len(rads) - 1))))], k_(14), P["dragon"])

    frames = []                                                            # at each point: along, up (square to it), side
    for i in range(len(pts)):
        tan = vunit(vsub(pts[min(i + 1, len(pts) - 1)], pts[max(i - 1, 0)]))
        up = vunit([-tan[0] * tan[1], 1 - tan[1] * tan[1], -tan[2] * tan[1]])
        frames.append((tan, up, vcross(tan, up)))

    def scales(p):
        """Plates across the belly, in two shades; above, green scales, a
        few of them darker."""
        j = min(range(len(pts)), key=lambda i: (pts[i][0] - p[0]) ** 2 + (pts[i][1] - p[1]) ** 2 + (pts[i][2] - p[2]) ** 2)
        d = vsub(p, pts[j])
        tan, up, side = frames[j]
        u, v = d[0] * up[0] + d[1] * up[1] + d[2] * up[2], d[0] * side[0] + d[1] * side[1] + d[2] * side[2]
        if u < -0.4 * rads[j]:
            return P["dragon_belly"] if j % 2 else P["grass_dry"]
        a = int((add.atan2(v, u) + add.pi) / (2 * add.pi) * 14)
        return P["dragon_wing"] if hash2(j, a, 13) < 0.28 else P["dragon"]

    add.mesh(add.color_by(body, scales))
    last = 0.0                                                             # the red crest along the top, from the neck to the tail
    for i in range(2, len(pts) - 3):
        last += vlen(vsub(pts[i], pts[i - 1]))
        if last < 0.3 or 0.8 < pts[i][0] < 1.0:                          # (spaced; none between the wings' roots)
            continue
        last = 0.0
        tan, up = frames[i][0], frames[i][1]
        base = [pts[i][k] + up[k] * rads[i] * 0.85 for k in range(3)]
        h = 0.1 + 0.45 * rads[i]
        add.cone(base, [base[k] + up[k] * h - tan[k] * h * 0.3 for k in range(3)], 0.05 + 0.08 * rads[i], 6, P["red"])
    add.mesh(add.move(add.make(add.prism, [[0, 0], [0.45, -0.28], [0.45, 0.28]], 0.06, P["red"], (0, 0, 0)),
                      [pts[-1][0], pts[-1][1], pts[-1][2]]))                   # the spade at the tip of the tail
    U = vunit(vcross(vcross(F, [0, 1, 0]), F))                             # the head, placed on the neck
    S = vcross(F, U)
    base = [nape[k] - F[k] * 0.14 for k in range(3)]
    head = add.stretch(dragon_head(), [1.3, 1.3, 1.3], (0, 0, 0))
    add.mesh(add.transform(head, [[F[0], U[0], S[0], base[0]], [F[1], U[1], S[1], base[1]], [F[2], U[2], S[2], base[2]]]))
    for i in range(3):                                                     # a wisp of smoke from the nostrils
        add.sphere([base[k] + F[k] * (1.63 - 0.05 * i) + U[k] * (0.28 + 0.27 * i) for k in range(3)], 0.08 + 0.05 * i, 6, SMOKE)

    def claws(tip, fwd, spread):
        """Three toes ending in claws, from ``tip`` along ``fwd``."""
        side = vunit(vcross([0, 1, 0], fwd))
        for j in (-1, 0, 1):
            t0 = [tip[k] + side[k] * spread * j for k in range(3)]
            t1 = [t0[k] + fwd[k] * 0.2 + side[k] * spread * j * 0.4 for k in range(3)]
            add.capsule(t0, t1, 0.055, 8, P["dragon"])
            add.cone(t1, [t1[k] + fwd[k] * 0.17 - (0.07 if k == 1 else 0.0) for k in range(3)], 0.045, 6, P["bone"])

    for s in (-1, 1):                                                      # the legs, standing on the gold
        sh, el = [1.05, 2.1, s * 0.5], [0.85, 1.55, s * 0.72]              # front: shoulder, elbow (bent back), wrist
        wr = [1.25, ground(1.25, s * 0.72) + 0.3, s * 0.72]
        add.capsule(sh, el, 0.2, 12, P["dragon"])
        add.capsule(el, wr, 0.15, 12, P["dragon"])
        toe = [1.45, ground(1.45, s * 0.74) + 0.07, s * 0.74]
        add.capsule(wr, toe, 0.12, 12, P["dragon"])
        claws(toe, vunit([1.0, -0.15, s * 0.1]), 0.09)
        hp, kn = [-1.3, 2.1, s * 0.4], [-0.85, 1.55, s * 0.78]             # hind: hip, knee (forward), hock (back), foot
        hk = [-1.55, ground(-1.55, s * 0.78) + 0.33, s * 0.78]
        add.capsule(hp, kn, 0.26, 12, P["dragon"])
        add.capsule(kn, hk, 0.17, 12, P["dragon"])
        toe = [-1.12, ground(-1.12, s * 0.8) + 0.07, s * 0.8]
        add.capsule(hk, toe, 0.12, 12, P["dragon"])
        claws(toe, vunit([1.0, -0.1, s * 0.05]), 0.1)
        # the wing: arm and forearm up to the wrist, three fingers fanning back, the skin between them
        s0, e, w = [0.8, 2.8, s * 0.35], [0.35, 3.75, s * 1.05], [-0.25, 4.55, s * 1.9]
        tips = [[-1.25, 4.2, s * 3.0], [-1.75, 3.35, s * 2.55], [-1.95, 2.8, s * 1.75]]
        root = [-1.3, 2.45, s * 0.42]                                      # where the skin meets the flank, at the hip
        add.capsule(s0, e, 0.11, 12, P["dragon"])
        add.capsule(e, w, 0.09, 12, P["dragon"])
        add.cone(w, [w[0] + 0.28, w[1] + 0.12, w[2] + s * 0.05], 0.06, 6, P["bone"])     # the thumb claw
        for tip in tips:
            mid = [(w[k] + tip[k]) / 2 + (0.12 if k == 1 else 0.0) for k in range(3)]
            add.polyline([w, mid, tip], lambda t: 0.065 - 0.04 * t, 8, P["dragon"])
        add.cone(tips[0], [tips[0][0] - 0.2, tips[0][1] - 0.08, tips[0][2] + s * 0.08], 0.035, 6, P["bone"])
        edges = [(tips[0], tips[1]), (tips[1], tips[2]), (tips[2], root)]
        for a, b in edges:                                                 # between the fingers, the edge in a scallop
            m = 8
            rim = []
            for j in range(m + 1):
                q = [a[k] + (b[k] - a[k]) * j / m for k in range(3)]
                pull = 0.2 * add.sin(add.pi * j / m)
                rim.append([q[k] + (w[k] - q[k]) * pull for k in range(3)])
            for j in range(m):
                sheet([w, rim[j], rim[j + 1]], P["dragon_wing"], 0.02)
        sheet([w, root, s0], P["dragon_wing"], 0.02)                        # and down to the body along the arm
        sheet([w, s0, e], P["dragon_wing"], 0.02)
    M = add.pop()
    M = add.stretch(M, [size, size, size], (0, 0, 0))
    add.mesh(add.move(add.rotateY(M, facing), at))


dragon([HEAP[0], HEAP[1], HEAP[2]], -0.35, 1.0)
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
    armour([x, AY + 0.1, z], -aa - add.pi / 2, weapon="none", shield=(i == 1), plume=False)
    add.cuboid([x, AY + 0.05, z], [0.6, 0.1, 0.6], P["wood_dark"])
table([DON[0], AY, DON[1]], 2.4, 1.2, 0.8)
for i in range(3):                                                          # great helms on the table
    helm = add.stretch(great_helm(False), [LIFE] * 3, (0, 0, 0))
    add.mesh(add.move(add.rotateY(helm, 0.6 * i - 0.6), [DON[0] - 0.7 + i * 0.7, AY + 0.802 - 1.525 * LIFE, DON[1]]))
barrel([DON[0] + 2.0, AY, DON[1] + 2.0], 0.4, 0.9)
for i in range(12):                                                         # a barrel of arrows
    aa = add.uniform(0, 6.28)
    add.cylinder([DON[0] + 2.0 + 0.25 * add.cos(aa), AY + 0.5, DON[1] + 2.0 + 0.25 * add.sin(aa)],
                 [DON[0] + 2.0 + 0.3 * add.cos(aa), AY + 1.9, DON[1] + 2.0 + 0.3 * add.sin(aa)], 0.015, 5, P["wood"])
# a grindstone in its trough of water, turned by a crank, and a man grinding a sword on it: his right hand on the
# grip, his left pressing the flat of the blade, its edge on the top of the stone
GX, GZ = DON[0] - 2.4, DON[1] + 2.0
add.cuboid([GX, AY + 0.225, GZ], [1.1, 0.45, 0.4], P["wood_dark"])                                    # the trough
add.cuboid([GX, AY + 0.42, GZ], [1.0, 0.02, 0.3], WATER)
add.wheel([GX, AY + 0.75, GZ], 0.45, 0.14, P["stone_dark"], (0, 0, 1), k_(16), hub_color=P["iron"])  # the stone
for sz in (-1, 1):
    add.cuboid([GX, AY + 0.62, GZ + sz * 0.16], [0.08, 0.34, 0.06], P["wood_dark"])                 # posts carrying the axle
add.cylinder([GX, AY + 0.75, GZ - 0.2], [GX, AY + 0.75, GZ + 0.28], 0.025, 8, P["iron"])
add.cuboid([GX, AY + 0.65, GZ + 0.28], [0.04, 0.24, 0.03], P["iron"])                               # the crank
add.cylinder([GX, AY + 0.54, GZ + 0.28], [GX, AY + 0.54, GZ + 0.4], 0.02, 6, P["wood"])
mx = GX + 1.0
hands = (([-0.035, 0.939, 0.209], [0.3, 0.0, 1], [-1, -0.8, -0.2]), ([0.052, 1.0, 0.383], [0, -0.6, 1], [1, -0.8, -0.2]))
figure([mx, AY, GZ], -add.pi / 2, person("stand", P["blue"], arms=hands, lean=0.12, hair=P["black"]))
sword([GX - 0.218, AY + 1.245, GZ], (0.985, -0.174, 0), 0.85, side=(0, 0, 1))
for aa in (0.2, 4.45, 5.2):
    torch([DON[0] + (DON_IN - 0.05) * add.cos(aa), AY + 2.6, DON[1] + (DON_IN - 0.05) * add.sin(aa)], -aa - add.pi / 2)
flush("armoury")

# the lord's chamber on the second floor
LY = F2
add.cuboid([DON[0], LY + 0.03, DON[1]], [6.0, 0.05, 6.0], P["red"])                       # a carpet
bed([DON[0] - 2.2, LY, DON[1] + 0.5], add.pi / 2, sleeper=False, canopy=True)
bed([DON[0] - 2.2, LY, DON[1] + 2.4], add.pi / 2, sleeper=False, canopy=True, blanket=P["rose"])      # and the princess's
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
#  9. Inside the chapel: the altar, the cross, pews, a lectern, candles;
#     and the attic over it, up a ladder
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
    sitting_man([CH_C[0] + sx, CY + 0.54, CH_Z0 + 5.0 + 1.6 * (1 if sx < 0 else 2) - 0.05], add.pi, shirt, pray=True, seat=0.54)
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

# the attic over the chapel: a floor of boards on beams (the chapel's
# ceiling), entered from the dormitory down three steps under the dormer;
# rafters, and the things of the altar not in use -- vestments, the
# chalice and the wine, the hosts, chests of linen, candlesticks, a
# processional cross
CA_X0, CA_X1 = KX1 + WT / 2 + 0.22, CH_X1 - WT / 2 - 0.22        # the inside faces of the walls
CA_Z0, CA_Z1 = CH_Z0 + WT / 2 + 0.22, CH_Z1 - WT / 2 - 0.22
CA_Y = CH_TOP                                                    # the attic floor
BOARD = (CA_X1 - CA_X0) / 30                                     # thirty boards across, running north-south
for k in range(8):                                               # the beams, across and into the walls
    add.cuboid([CH_C[0], CA_Y - 0.25, CA_Z0 + 1.38 + 1.4 * k], [CA_X1 - CA_X0 + 0.44, 0.3, 0.25], P["wood_dark"])
for i in range(30):
    add.cuboid([CA_X0 + (i + 0.5) * BOARD, CA_Y - 0.05, CH_C[1]], [BOARD, 0.1, CA_Z1 - CA_Z0], shade_of("wood", i))
for i in range(3):                                               # from the door: the sill carried on, two steps down
    add.cuboid([CA_X0 + 0.15 + 0.3 * i, (CA_Y + FLOOR2 - 0.2 * i) / 2, CH_C[1]], [0.3, FLOOR2 - 0.2 * i - CA_Y, 2 * DM_I - 0.1],
               shade_of("wood", i + 1))
drop = 0.15 * add.sqrt(1 + CH_S * CH_S)                          # the rafters: 0.3 deep, under the boards of the roof
for k in range(8):
    z = CA_Z0 + 1.38 + 1.4 * k
    for sg in (-1, 1):
        if sg < 0 and abs(z - CH_C[1]) < DM_W + 0.2:             # cut away where the dormer comes through
            continue
        foot = CH_C[0] + sg * (CH_IN - drop - 0.3) / CH_S if sg > 0 else CA_X0 + 0.1
        y_foot = CA_Y + CH_IN - drop - CH_S * abs(foot - CH_C[0])
        add.beam([foot, y_foot, z], [CH_C[0] + sg * 0.125, CA_Y + CH_IN - drop - CH_S * 0.125, z], 0.18, 0.3, P["wood_dark"])
add.cuboid([CH_C[0], CA_Y + CH_IN - 0.15, CH_C[1]], [0.25, 0.3, CA_Z1 - CA_Z0], P["wood_dark"])            # the ridge beam
add.cuboid([CH_X1 - 0.1, CA_Y + 0.1, CH_C[1]], [0.3, 0.2, CA_Z1 - CA_Z0], P["wood_dark"])                 # the wall plate
# on a small table under the south window: the chalice, a bottle of wine and a bowl of hosts
tx, tz = CH_C[0] - 1.7, CA_Z1 - 2.5
table([tx, CA_Y, tz], 1.1, 0.6, 0.8, cloth=True)
lathe([[0.0, 0], [0.13, 0], [0.13, 0.02], [0.04, 0.05], [0.04, 0.2], [0.07, 0.24], [0.15, 0.3],
       [0.16, 0.45], [0.12, 0.45], [0.11, 0.3], [0.0, 0.28]], [tx - 0.32, CA_Y + 0.83, tz - 0.08], k_(8), P["gold"], 0.55)
lathe([[0.0, 0], [0.07, 0], [0.075, 0.02], [0.075, 0.2], [0.05, 0.25], [0.025, 0.28], [0.025, 0.34], [0.03, 0.35],
       [0.0, 0.35]], [tx + 0.32, CA_Y + 0.83, tz - 0.1], k_(8), P["dragon_wing"])                      # bottle-green glass
add.cylinder([tx + 0.32, CA_Y + 1.18, tz - 0.1], [tx + 0.32, CA_Y + 1.21, tz - 0.1], 0.022, 8, P["wood_light"])   # the cork
bowl([tx, CA_Y + 0.83, tz + 0.1], 0.14, P["gold"])
for i in range(5):                                                 # the hosts, a little heap of white wafers
    hx, hz = tx + 0.015 * add.cos(2.1 * i), tz + 0.1 + 0.015 * add.sin(2.1 * i)
    add.cylinder([hx, CA_Y + 0.85 + 0.006 * i, hz], [hx, CA_Y + 0.855 + 0.006 * i, hz], 0.032, 12, P["white"])


def vestment(px, top, z, kind, color):
    """A vestment hanging from a peg at (px, top) in front of a wall at z:
    a chasuble with a gold cross, a white alb with its sleeves, or a stole."""
    def cloth(points, c, dz=0.0, t=0.03):
        add.prism([(px + u, top + v) for u, v in points], t, c, (0, 0, z + dz), (0, 0, 1))
    if kind == "chasuble":
        cloth([(-0.16, 0), (0.16, 0), (0.44, -0.12), (0.5, -0.55), (0.45, -1.05), (0.28, -1.22), (0, -1.28),
               (-0.28, -1.22), (-0.45, -1.05), (-0.5, -0.55), (-0.44, -0.12)], color)
        add.cuboid([px, top - 0.68, z + 0.02], [0.12, 1.12, 0.012], P["gold"])
        add.cuboid([px, top - 0.42, z + 0.02], [0.62, 0.12, 0.012], P["gold"])
    elif kind == "alb":
        cloth([(-0.2, 0), (0.2, 0), (0.42, -1.45), (-0.42, -1.45)], color)
        for s in (-1, 1):
            cloth([(s * 0.2, 0), (s * 0.18, -0.25), (s * 0.46, -0.72), (s * 0.6, -0.62)], color, -0.01)
    else:
        for s in (-1, 1):
            cloth([(s * 0.02, 0), (s * 0.12, 0), (s * 0.2, -1.05), (s * 0.1, -1.05)], color)
            add.cuboid([px + s * 0.15, top - 0.9, z + 0.02], [0.03, 0.1, 0.012], P["gold"])
            add.cuboid([px + s * 0.15, top - 0.88, z + 0.02], [0.08, 0.03, 0.012], P["gold"])


for x0, hung in ((CA_X0 + 0.8, (("chasuble", P["purple"]), ("alb", P["white"]))),
                 (CA_X1 - 3.2, (("chasuble", P["red"]), ("stole", P["leaf"])))):                     # on pegs on the north gable
    add.cuboid([x0 + 1.2, CA_Y + 1.9, CA_Z0 + 0.03], [2.4, 0.12, 0.06], P["wood_dark"])
    for i, (kind, color) in enumerate(hung):
        px = x0 + 0.6 + 1.2 * i
        add.cylinder([px, CA_Y + 1.9, CA_Z0 + 0.06], [px, CA_Y + 1.93, CA_Z0 + 0.22], 0.025, 8, P["wood_dark"])
        vestment(px, CA_Y + 1.93, CA_Z0 + 0.13, kind, color)
chest([CA_X0 + 1.35, CA_Y, CH_C[1] + 2.0], add.pi / 2, s=0.8)                                              # chests: one open,
chest([CA_X0 + 1.35, CA_Y, CH_C[1] - 2.6], add.pi / 2, open_lid=True, s=0.8)                               # full of altar linen
for i, color in enumerate((P["white"], P["linen"], P["purple"])):
    add.cuboid([CA_X0 + 1.4, CA_Y + 0.665 + 0.05 * i, CH_C[1] - 2.6 + 0.06 * (i - 1)], [0.5, 0.05, 0.9 - 0.12 * i], color)
chest([CA_X1 - 1.35, CA_Y, CH_C[1] + 1.4], -add.pi / 2, s=0.8)
for dz in (1.6, 2.3):                                                                                  # two tall candlesticks
    at = [CA_X1 - 1.4, CA_Y, CA_Z1 - dz]
    lathe([[0.0, 0], [0.22, 0], [0.22, 0.04], [0.07, 0.1], [0.045, 0.2], [0.045, 1.05], [0.09, 1.1], [0.1, 1.15], [0.0, 1.15]],
          at, k_(8), P["gold"])
    add.cylinder([at[0], CA_Y + 1.15, at[2]], [at[0], CA_Y + 1.45, at[2]], 0.035, 12, P["white"])
    add.cylinder([at[0], CA_Y + 1.45, at[2]], [at[0], CA_Y + 1.48, at[2]], 0.008, 4, P["black"])
for j, (bx, bz, facing) in enumerate(((CA_X1 - 0.9, CA_Z0 + 1.3, 0.0), (CA_X1 - 0.9, CA_Z0 + 4.6, 0.0),   # beds for the
                                     (CH_C[0], CA_Z0 + 1.3, 0.0), (CA_X0 + 0.9, CA_Z0 + 1.6, 0.0),        # priest and the
                                     (CA_X0 + 0.9, CA_Z1 - 1.5, add.pi))):                                # brothers: under
    bed([bx, CA_Y, bz], facing, sleeper=j == 1, blanket=(P["wood"], P["linen"])[j % 2])                   # the roof, clear of
                                                                                                          # the rafters' feet
px, pz = CH_C[0] + 2.2, CH_C[1] - 2.4                                                                  # the processional cross,
add.cuboid([px, CA_Y + 0.1, pz], [0.45, 0.2, 0.45], P["wood_dark"])                                     # in its stand
add.cylinder([px, CA_Y + 0.2, pz], [px, CA_Y + 2.2, pz], 0.03, 8, P["wood_dark"])
add.cuboid([px, CA_Y + 2.4, pz], [0.07, 0.55, 0.05], P["gold"])
add.cuboid([px, CA_Y + 2.48, pz], [0.42, 0.07, 0.05], P["gold"])
flush("chapel attic")


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
    if (x - TUR[0]) ** 2 + (z - TUR[1]) ** 2 < (TUR_R + 0.4 + max(0.0, margin)) ** 2:      # the chapel's turret
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
RYE = (-15.0, -7.0, 16.0, 25.0)                        # x0, x1, z0, z1 of the little field of rye west of the road
FOOTPRINTS = [(10, 10, 2.75), (12, 24, 1.7), (2.8, 1.2, 0.6), (-2.8, 1.2, 0.6), (-12, 30, 2.6), (-34, 6, 4.0), (-33, 22, 4.5), (10, -40, 5.2),
              (28, 18, 5.0), (30, 31, 2.4), (33.5, 23, 2.6), (32, 6, 5.0), (-27.8, -18, 5.4), (-6, -40, 1.2),
              (-22, 14, 3.2), (-30, 35, 2.0), (-23, 38, 2.8), (17, 42, 2.8), (8, 41, 2.6), (-8, 41, 2.6),
              (-19, 20, 1.2), (14, 27, 0.6), (-5.6, 21.5, 0.6), (20, 36, 0.6), (9, 20, 0.9), (-20, 26, 0.9),
              (-40, 14, 0.4), (-38, 22, 0.4), (-5, 39, 0.5), (14, -38, 1.6),
              (-44.2, -8.5, 6.0), (-43.2, -15.2, 1.5), (-40.0, -4.5, 1.2), (-41.0, -15.2, 0.5),     # the kitchen, its oven,
              (46.2, -5.2, 4.9), (46.2, 8.5, 0.9), (46.2, 12.3, 0.9), (37.0, 9.5, 0.5), (37.5, 12.8, 0.5),   # the stores, the butts,
              (-11.5, -37.0, 4.7), (-2.0, -35.2, 4.7), (-44.0, 8.5, 4.7), (40.5, 17.5, 4.7), (20.5, 25.0, 4.7)]   # the log houses


def on_footprint(x, z):
    if abs(x) < 3.7 and -1.4 < z < 1.4:                # the steps up to the palace door
        return True
    if RYE[0] - 0.3 < x < RYE[1] + 0.3 and RYE[2] - 0.3 < z < RYE[3] + 0.3:           # the field
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
    add.cylinder([0, 2.2, 0.175], [0, 1.69, 0.175], 0.015, 6, P["rope"])                          # the rope, off the drum,
    add.torus([0, 1.66, 0.175], 0.028, 0.011, 8, 4, P["rope"], axis=(1, 0, 0))                   # knotted round the top
    add.sphere([0, 1.7, 0.175], 0.024, 4, P["rope"])                                              # of the bucket's handle
    lathe([[0.16, 0], [0.18, 0], [0.22, 0.3], [0.2, 0.3], [0.16, 0.02]], [0, 1.1, 0.175], k_(10), P["wood_dark"])
    add.arch([-0.2, 1.4, 0.175], [0.2, 1.4, 0.175], 0.25, 0.015, P["iron"], 8, 6)
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
    """A quintain for sword practice: a post in a timber cross foot, a
    straw-stuffed body in sacking bound with rope, arms of a cross-bar,
    a wooden head in an old dented kettle hat, a battered shield on its
    left arm."""
    x, y, z = at
    for a in (0.0, add.pi / 2):                                                   # the cross foot
        add.mesh(add.move(add.rotateY(add.make(add.cuboid, [0, 0.08, 0], [1.4, 0.16, 0.16], P["wood_dark"]), a), at))
    add.cylinder([x, y, z], [x, y + 2.25, z], 0.08, 8, P["wood_dark"])
    lathe([[0.0, 0.95], [0.3, 0.95], [0.4, 1.2], [0.42, 1.55], [0.36, 1.8], [0.0, 1.85]], at, k_(10), P["sand"])   # the body
    for yy, rr in ((1.08, 0.37), (1.45, 0.43), (1.75, 0.38)):
        add.torus([x, y + yy, z], rr, 0.02, k_(10), 4, P["rope"])
    add.cylinder([x - 0.8, y + 1.65, z], [x + 0.8, y + 1.65, z], 0.05, 8, P["wood_dark"])          # the arms
    add.sphere([x, y + 2.08, z], 0.2, 4, P["wood_light"])                                             # the head ...
    add.hemisphere([x, y + 2.13, z], 0.24, 5, P["iron"])                                              # ... in a kettle hat
    add.cylinder([x, y + 2.12, z], [x, y + 2.14, z], 0.33, k_(8), P["iron"])
    shield([x - 0.75, y + 1.15, z + 0.12], 0, 0.35)


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


def cannon(at, facing=0.0, balls=True, s=1.0):
    """An iron cannon on a wheeled carriage: the barrel is a real tube at
    the muzzle -- a round bore you can look into -- with reinforcing rings
    and a cascabel at the breech; the pyramid of cannon balls stands beside
    the carriage, clear of the wheels (``balls=False``: none -- a gun on the
    walls, its balls stacked elsewhere).  ``s`` scales it: 0.75 is a lighter
    gun for a tower top."""
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
    if balls:
        ball_pile([-0.9, 0, 1.8])                                             # a pyramid of cannon balls, beside the carriage
    add.mesh(add.move(add.rotateY(add.stretch(add.pop(), [s] * 3, (0, 0, 0)), facing), at))


def ball_pile(at, facing=0.0):
    """A pyramid of fourteen cannon balls on a wooden board."""
    add.push()
    for j in range(3):
        for i in range(3 - j):
            for k in range(3 - j):
                add.sphere([-0.5 + (i + 0.5 * j) * 0.5, 0.25 + j * 0.42, -0.5 + (k + 0.5 * j) * 0.5], 0.25, 10, P["iron"])
    add.cuboid([0, 0.05, 0], [1.8, 0.1, 1.8], P["wood"])
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


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
    brick_box([-1.6, 3.0, -2.0], [1.0, 4.0, 0.9], flue=(0.4, 0.35, 0.8))                         # chimney
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
    """A half-timbered house with a thatched roof, lived in: white plaster
    walls in a frame of dark timbers, the door standing open, glazed
    windows; inside, on a floor of boards, two beds against the back wall,
    a hearth with a pot on the fire under a brick chimney that goes up
    through the thatch, a table and stools, and the woman of the house
    sitting by the fire.  Built with its door towards +z."""
    T = 0.3
    add.push()
    door = (0.0, 1.3, 2.7)
    wins = [(sx, 1.0, 1.0) for sx in (-w / 4, w / 4)]                                        # x, width, height
    SILL = h * 0.55 - 0.5
    shell = add.make(add.cuboid, [0, h / 2, 0], [w, h, d], P["white"])
    cuts = [add.make(add.cuboid, [0, (0.06 + h + 1) / 2, 0], [w - 2 * T, h + 1 - 0.06, d - 2 * T], P["white"]),
            add.make(add.cuboid, [door[0], (0.06 + door[2]) / 2, d / 2], [door[1], door[2] - 0.06, 2 * T + 0.2], P["wood_dark"])]
    cuts += [add.make(add.cuboid, [x, SILL + hh / 2, d / 2], [ww, hh, 2 * T + 0.2], P["white"]) for x, ww, hh in wins]
    add.mesh(add.difference(shell, *cuts))
    for x in (-w / 2, w / 2):
        add.cuboid([x, h / 2, 0], [0.2, h, 0.2], P["wood_dark"])
        for z in (-d / 2, d / 2):
            add.cuboid([x, h / 2, z], [0.2, h, 0.2], P["wood_dark"])
    for z in (-d / 2, d / 2):
        for i in range(1, int(w / 1.5)):
            x = -w / 2 + i * 1.5
            if z < 0 or (abs(x - door[0]) > 0.75 and all(abs(x - wx) > 0.6 for wx, _, _ in wins)):   # no stud across a door or window
                add.cuboid([x, h / 2, z], [0.16, h, 0.14], P["wood_dark"])
        add.cuboid([0, h - 0.1, z], [w, 0.2, 0.14], P["wood_dark"])
        if z < 0:
            add.cuboid([0, h / 2, z], [w, 0.16, 0.14], P["wood_dark"])
        else:                                                                                # the middle rail stops at the door
            for x0, x1 in ((-w / 2, -0.75), (0.75, w / 2)):
                add.cuboid([(x0 + x1) / 2, h / 2, z], [x1 - x0, 0.16, 0.14], P["wood_dark"])
        if z < 0:                                                                            # braces, clear of the windows
            add.beam([-w / 2, 0.2, z], [-w / 2 + 1.5, h / 2 - 0.1, z], 0.12, 0.12, P["wood_dark"])
            add.beam([w / 2, 0.2, z], [w / 2 - 1.5, h / 2 - 0.1, z], 0.12, 0.12, P["wood_dark"])
    for x in (-w / 2, w / 2):
        add.cuboid([x, h / 2, 0], [0.14, 0.16, d], P["wood_dark"])
    for x, ww, hh in wins:                                                                   # the windows: glass mid-wall, a frame
        add.push()                                                                           # of boards round them outside
        window_frame({"x": x, "y0": SILL, "y1": SILL + hh, "w": ww, "arched": False, "kind": "window"}, T)
        add.mesh(add.move(add.pop(), [0, 0, d / 2 - T / 2]))
        for sx in (-1, 1):
            add.cuboid([x + sx * (ww / 2 + 0.05), SILL + hh / 2, d / 2 + 0.03], [0.1, hh + 0.2, 0.08], P["wood_dark"])
        for y in (SILL - 0.05, SILL + hh + 0.05):
            add.cuboid([x, y, d / 2 + 0.03], [ww, 0.1, 0.08], P["wood_dark"])
    add.push()                                                                               # the door, open into the room
    add.cuboid([door[1] / 2, (0.06 + door[2]) / 2, -0.04], [door[1] - 0.04, door[2] - 0.08, 0.08], P["wood_dark"])
    add.sphere([door[1] - 0.2, 1.0, 0.03], 0.06, 4, P["gold"])
    add.mesh(add.move(add.rotateY(add.pop(), 1.25), [door[0] - door[1] / 2, 0, d / 2 - T]))
    thatch = add.make(add.roof, [0, h, 0], [d + 0.6, w + 0.6], 2.6, P["straw"], 0.4)           # the thatch, the ridge along the house
    add.mesh(add.rotateY(thatch, add.pi / 2))
    cx, cz = w / 4, -d / 2 + T + 0.3                                                           # the chimney, from the hearth up
    brick_box([cx, (0.06 + h + 2.3) / 2, cz], [0.8, h + 2.3 - 0.06, 0.6])                       # through the thatch
    chimney_cap([cx, h + 2.36, cz], 0.95, 0.75, 0.12, (0.4, 0.3))
    plank_floor(-w / 2 + T, w / 2 - T, -d / 2 + T, d / 2 - T, 0.1, along="x", holes=[(cx - 0.65, cx + 0.65, -d / 2 + T, cz + 1.05)])
    brick_box([cx, (0.06 + 0.4) / 2, cz + 0.65], [1.2, 0.34, 0.7])                              # the hearth, a fire, a pot on it
    for i, a in enumerate((0.3, -0.5, 1.2)):
        add.cylinder([cx - 0.22 * add.cos(a), 0.45, cz + 0.65 - 0.18 * add.sin(a)], [cx + 0.22 * add.cos(a), 0.45, cz + 0.65 + 0.18 * add.sin(a)],
                     0.05, 6, pick("wood", i, 7))
    for i in range(3):
        add.cone([cx - 0.12 + 0.12 * i, 0.44, cz + 0.65], [cx - 0.1 + 0.1 * i, 0.72, cz + 0.62], 0.08, 6, FLAME)
    lathe([[0.0, 0], [0.12, 0], [0.18, 0.06], [0.2, 0.18], [0.17, 0.26], [0.19, 0.28], [0.16, 0.28], [0.0, 0.22]],
          [cx + 0.42, 0.4, cz + 0.72], k_(10), P["iron"], 0.9)
    for i, x in enumerate((-w / 2 + T + 0.65, -w / 2 + T + 1.9)):                             # two beds against the back wall
        bed([x, 0.1, -d / 2 + T + 1.13], 0.0, sleeper=False, blanket=(P["blue"], P["red"])[i])
    table([cx - 0.2, 0.1, 1.05], 1.2, 0.7, 0.78, P["wood"])                                   # the table and stools
    bread([cx - 0.1, 0.88, 1.05], 1)
    jug([cx - 0.55, 0.88, 1.1], P["brick"], 0.45)
    for dx in (-0.45, 0.35):
        stool([cx - 0.2 + dx, 0.1, 1.72], 0.44)
    stool([cx - 1.2, 0.1, cz + 1.35], 0.44)                                                    # and her stool by the fire
    wife = person("sit", gown=P["blue"], female=True, head=("veil", P["white"]), hair=P["trunk"], seat=0.54, reach=0.42)
    figure([cx - 1.2, 0.1 + 0.44, cz + 1.35], 2.1, wife)
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def log_house(at, facing=0.0, W=6.6, D=5.0, loft=False, thatch=False, seed=0, folk=()):
    """A house of logs where the castle's common folk live and sleep: a
    footing of stone, walls of round logs on a core chinked dark between
    them, square posts at the corners, a plank door standing open, glazed
    windows in board casings with the shutters open, a steep gable roof of
    wooden shingles (or thatch) with board gables.  Inside, on a floor of
    boards: beds against the back wall, a table with benches, a shelf with
    bowls and a jug, a chest.  With ``loft`` a second storey under the
    roof: a hay loft on joists, reached by a ladder through a hatch, the hay
    door open in the gable with a hoist beam over it -- and the hay where
    the farmhands sleep, rolled in their blankets.  ``folk`` = who is in:
    "eat" (someone at the table), "sleep" (someone in a bed).  Built with
    its door towards +z."""
    T, FT = 0.3, 0.4                                                           # the wall core; the stone footing
    FL = FT + 0.05                                                             # the floor of boards
    H1 = FL + 2.4                                                              # the ceiling of the room below
    LF = H1 + 0.22                                                             # the loft floor
    H = FT + 0.25 * (16 if loft else 10)                                       # the tops of the walls: whole courses of logs
    PITCH = 0.9 if thatch else 0.85
    under = lambda z: H + (D / 2 + 0.3 - abs(z)) * PITCH                       # the roof's underside over |z|
    RU = under(0)
    add.push()
    add.cuboid([0, FT / 2, 0], [W + 0.7, FT, D + 0.7], P["stone_dark"])                       # the footing
    door = (-W / 2 + 1.35, 1.0, 2.0)                                                            # x, width, height
    front, back_w = [(W / 2 - 1.35, 0.8, 0.8)], [(0.4, 0.8, 0.8)]                               # windows: x, width, height
    SILL = FL + 1.0
    end_w = (0.0, 0.7, 0.8)                                                                     # on the +x end: z, width, height
    hay = (0.0, 1.0, LF + 0.15, LF + 1.45)                                                      # the hay door, -x end: z, width, y0, y1
    shell = add.make(add.cuboid, [0, (FT + H) / 2, 0], [W, H - FT, D], P["wood_dark"])
    cuts = [add.make(add.cuboid, [0, (FT - 0.01 + H + 1) / 2, 0], [W - 2 * T, H + 1 - FT + 0.01, D - 2 * T], P["wood"]),
            add.make(add.cuboid, [door[0], FL + door[2] / 2, D / 2], [door[1], door[2], 2 * T + 0.2], P["wood"])]
    cuts += [add.make(add.cuboid, [x, SILL + h / 2, D / 2], [w, h, 2 * T + 0.2], P["wood"]) for x, w, h in front]
    cuts += [add.make(add.cuboid, [x, SILL + h / 2, -D / 2], [w, h, 2 * T + 0.2], P["wood"]) for x, w, h in back_w]
    cuts.append(add.make(add.cuboid, [W / 2, SILL + end_w[2] / 2, end_w[0]], [2 * T + 0.2, end_w[2], end_w[1]], P["wood"]))
    if loft:
        cuts.append(add.make(add.cuboid, [-W / 2, (hay[2] + H) / 2, hay[0]], [2 * T + 0.2, H - hay[2] + 0.01, hay[1]], P["wood"]))
    add.mesh(add.difference(shell, *cuts))
    # the logs, course by course, stopped short of the openings where the casings go
    walls = {"+z": (D / 2 + 0.13, W, [(door[0] - door[1] / 2, door[0] + door[1] / 2, FL, FL + door[2])] +
                    [(x - w / 2, x + w / 2, SILL, SILL + h) for x, w, h in front]),
             "-z": (-(D / 2 + 0.13), W, [(x - w / 2, x + w / 2, SILL, SILL + h) for x, w, h in back_w]),
             "+x": (W / 2 + 0.13, D, [(end_w[0] - end_w[1] / 2, end_w[0] + end_w[1] / 2, SILL, SILL + end_w[2])]),
             "-x": (-(W / 2 + 0.13), D, [(hay[0] - hay[1] / 2, hay[0] + hay[1] / 2, hay[2], H + 1)] if loft else [])}
    courses = [FT + 0.125 + 0.25 * k for k in range(int((H - FT) / 0.25 + 1e-6))]
    for name, (off, L, openings) in walls.items():
        for k, yc in enumerate(courses):
            spans = [(-L / 2, L / 2)]
            for u0, u1, y0, y1 in openings:
                if yc + 0.12 > y0 - 0.1 and yc - 0.12 < y1 + 0.1:
                    spans = [piece for a, b in spans for piece in ((a, min(b, u0 - 0.1)), (max(a, u1 + 0.1), b)) if piece[1] - piece[0] > 0.05]
            for a, b in spans:
                if name in ("+z", "-z"):
                    p, q = [a, yc, off], [b, yc, off]
                else:
                    p, q = [off, yc, -a], [off, yc, -b]
                add.cylinder(p, q, 0.12, 8, pick("wood", k * 3 + len(name), a + seed))
        for u0, u1, y0, y1 in openings:                                       # casings over the log ends, up to the logs
            top = min([yc - 0.12 for yc in courses if yc - 0.12 >= y1 + 0.1 - 1e-6] + [H])
            low = max([yc + 0.12 for yc in courses if yc + 0.12 <= y0 - 0.1 + 1e-6] + [FT])
            sgn = 1 if off > 0 else -1
            boxes = [(u0 - 0.05, low, top, 0.1), (u1 + 0.05, low, top, 0.1), ((u0 + u1) / 2, y1, top, u1 - u0)]
            if y0 > FL + 0.01:
                boxes.append(((u0 + u1) / 2, low, y0, u1 - u0))
            for uc, py0, py1, bw in boxes:
                if py1 - py0 < 0.01:
                    continue
                c, size = [uc, (py0 + py1) / 2, sgn * (abs(off) + 0.005)], [bw, py1 - py0, 0.27]
                if name in ("+x", "-x"):
                    c, size = [c[2], c[1], -uc], [0.27, size[1], bw]
                add.cuboid(c, size, P["wood_dark"])
    for sx in (-1, 1):                                                          # square posts at the corners
        for sz in (-1, 1):
            add.cuboid([sx * (W / 2 + 0.175), (FT + H) / 2, sz * (D / 2 + 0.175)], [0.34, H - FT, 0.34], P["wood_dark"])
    for sz in (-1, 1):                                                          # the wall tops carried up to the roof
        prof = [[H - 0.01, sz * D / 2], [H - 0.01, sz * (D / 2 - T)], [under(D / 2 - T) + 0.03, sz * (D / 2 - T)], [under(D / 2) + 0.03, sz * D / 2]]
        add.mesh(add.make(add.prism, prof, W, P["wood"], (0, 0, 0), (1, 0, 0)))
    # the gables: boards, with battens; the hay door in the -x one
    for sx in (-1, 1):
        g = add.make(add.prism, [[H - 0.01, -(D / 2 + 0.3)], [H - 0.01, D / 2 + 0.3], [RU + 0.02, 0.0]], T, shade_of("wood_light", 1),
                     (sx * (W / 2 - T / 2), 0, 0), (1, 0, 0))
        if loft and sx < 0:
            g = add.difference(g, add.make(add.cuboid, [-W / 2, (hay[2] + hay[3]) / 2, hay[0]], [T + 0.2, hay[3] - hay[2], hay[1]], P["wood_light"]))
        if sx > 0 and loft:                                                     # a small window high in the other gable
            g = add.difference(g, add.make(add.cuboid, [W / 2, LF + 1.9, 0], [T + 0.2, 0.5, 0.5], P["wood_light"]))
        add.mesh(g)
        for i in range(int((D + 0.6) / 0.45)):
            z = -(D / 2 + 0.3) + 0.225 + i * 0.45
            y1 = under(z) - 0.02
            if loft and sx < 0 and abs(z - hay[0]) < hay[1] / 2 + 0.05 and y1 > hay[2]:
                if y1 > hay[3] + 0.05:
                    add.cuboid([sx * W / 2 + sx * 0.02, (hay[3] + y1) / 2, z], [0.04, y1 - hay[3], 0.07], P["wood_dark"])
                continue
            if sx > 0 and loft and abs(z) < 0.3:
                add.cuboid([sx * W / 2 + sx * 0.02, (H + LF + 1.65) / 2, z], [0.04, LF + 1.65 - H, 0.07], P["wood_dark"])
                if y1 > LF + 2.15:
                    add.cuboid([sx * W / 2 + sx * 0.02, (LF + 2.15 + y1) / 2, z], [0.04, y1 - LF - 2.15, 0.07], P["wood_dark"])
                continue
            if y1 > H + 0.05:
                add.cuboid([sx * W / 2 + sx * 0.02, (H + y1) / 2, z], [0.04, y1 - H, 0.07], P["wood_dark"])
    # the roof: boards on the rafters, and shingles or thatch on them
    for sz in (-1, 1):
        eave, top = [W / 2 + 0.55, under(D / 2 + 0.75), sz * (D / 2 + 0.75)], [W / 2 + 0.55, RU, 0.0]
        quad = [[-eave[0], eave[1], eave[2]], eave, top, [-top[0], top[1], top[2]]]
        if sz < 0:
            quad = [quad[1], quad[0], quad[3], quad[2]]
        add.mesh(slab(quad, 0.1, P["wood_dark"]))
        rise = 0.1 / add.cos(add.atan(PITCH))
        if thatch:
            add.mesh(slab([[q[0], q[1] + rise, q[2]] for q in quad], 0.32, P["straw"]))
        else:
            tile_face(*[[q[0], q[1] + rise, q[2]] for q in quad], size=(0.24, 0.3), colours="wood_light")
    if thatch:
        add.cylinder([-W / 2 - 0.6, RU + 0.45, 0], [W / 2 + 0.6, RU + 0.45, 0], 0.28, 10, P["straw"])   # the ridge, rolled
    else:
        add.beam([-W / 2 - 0.6, RU + 0.2, 0], [W / 2 + 0.6, RU + 0.2, 0], 0.26, 0.16, P["wood_dark"])
    # the door, open into the room on its iron straps, and glass in the windows, shutters open outside
    add.push()
    add.cuboid([door[1] / 2, FL + door[2] / 2, -0.03], [door[1] - 0.04, door[2] - 0.03, 0.06], shade_of("wood", 2))
    for y in (0.35, 1.65):
        add.cuboid([0.4, FL + y, 0.005], [0.8, 0.06, 0.02], P["iron"])
    add.mesh(add.move(add.rotateY(add.pop(), 1.3), [door[0] - door[1] / 2, 0, D / 2 - T]))
    glazed = [(x, w, h, [0, 0, D / 2 - T / 2], 0.0) for x, w, h in front] + [(x, w, h, [0, 0, -D / 2 + T / 2], 0.0) for x, w, h in back_w]
    glazed.append((0.0, end_w[1], end_w[2], [W / 2 - T / 2, 0, end_w[0]], add.pi / 2))
    for x, w, h, where, turn in glazed:
        add.push()
        window_frame({"x": x, "y0": SILL, "y1": SILL + h, "w": w, "arched": False, "kind": "window"}, T)
        add.mesh(add.move(add.rotateY(add.pop(), turn), where))
    shutter = (P["leaf_dark"], P["red"], P["blue"])[seed % 3]
    for x, w, h in front + back_w:
        sg = 1 if (x, w, h) in front else -1
        for sx in (-1, 1):
            add.cuboid([x + sx * (w / 2 + 0.1 + w / 4 + 0.02), SILL + h / 2, sg * (D / 2 + 0.275)], [w / 2, h + 0.1, 0.04], shutter)
    for sz in (-1, 1):
        add.cuboid([W / 2 + 0.275, SILL + end_w[2] / 2, end_w[0] + sz * (end_w[1] / 2 + 0.1 + end_w[1] / 4 + 0.02)], [0.04, end_w[2] + 0.1, end_w[1] / 2], shutter)
    # inside: the floor, beds against the back wall, the table and benches, a shelf, a chest
    plank_floor(-W / 2 + T, W / 2 - T, -D / 2 + T, D / 2 - T, FL, along="x")
    n_beds = 2 if loft else 3
    for i in range(n_beds):
        bed([-W / 2 + T + 0.65 + i * 1.25, FL, -D / 2 + T + 1.13], 0.0, sleeper=("sleep" in folk and i == 0),
            blanket=(P["red"], P["blue"], P["leaf_dark"], P["wood_light"])[(seed + i) % 4])
    tx, tz = W / 2 - T - 1.0, 0.75
    table([tx, FL, tz], 1.3, 0.8, 0.78, P["wood"])
    for sz in (-1, 1):
        add.cuboid([tx, FL + 0.45, tz + sz * 0.75], [1.2, 0.08, 0.28], P["wood"])
        for dx in (-0.45, 0.45):
            add.cuboid([tx + dx, FL + 0.21, tz + sz * 0.75], [0.08, 0.42, 0.22], P["wood_dark"])
    bread([tx + 0.25, FL + 0.78, tz], 1)
    bowl([tx - 0.3, FL + 0.78, tz - 0.15], 0.14)
    if "eat" in folk:
        sitting_man([tx - 0.2, FL + 0.5, tz - 0.75], 0.0, (P["leaf"], P["blue"], P["red"], P["linen"])[seed % 4], (0.3, 0.4), seat=0.5)
    add.cuboid([W / 2 - T - 0.15, FL + 1.55, -1.0], [0.3, 0.05, 1.6], P["wood_dark"])            # a shelf on the end wall
    for i, dz in enumerate((-1.55, -1.15)):
        bowl([W / 2 - T - 0.15, FL + 1.575, dz], 0.12, pick("wood", i, seed))
    jug([W / 2 - T - 0.17, FL + 1.575, -0.6], P["brick"], 0.35)
    if not loft:
        chest([W / 2 - T - 0.5, FL, -D / 2 + T + 0.45], 0.0, s=0.6)
    if loft:                                                                   # the loft: joists, a floor with a hatch, a ladder
        for i in range(int((W - 2 * T) / 0.9) + 1):
            x = -W / 2 + T + 0.3 + i * 0.9
            if x < W / 2 - T - 0.2:
                add.cuboid([x, LF - 0.13, 0], [0.12, 0.18, D - 2 * T], P["wood_dark"])
        hatch = (0.5, 1.5, -D / 2 + T + 0.1, -D / 2 + T + 1.0)
        plank_floor(-W / 2 + T, W / 2 - T, -D / 2 + T, D / 2 - T, LF, along="x", holes=[hatch])
        lx, lz0, lz1 = (hatch[0] + hatch[1]) / 2, hatch[3] + 0.6, hatch[3] - 0.15
        for sx in (-0.22, 0.22):
            add.beam([lx + sx, FL, lz0], [lx + sx, LF + 0.9, lz1], 0.06, 0.08, P["wood"])
        for i in range(8):
            t = (i + 0.5) / 8.0
            add.cylinder([lx - 0.22, FL + t * (LF + 0.9 - FL), lz0 + t * (lz1 - lz0)], [lx + 0.22, FL + t * (LF + 0.9 - FL), lz0 + t * (lz1 - lz0)],
                         0.025, 6, P["wood"])
        add.cuboid([0, LF + 0.1, 0.55], [W - 2 * T - 0.1, 0.2, D - 2 * T - 1.2], P["straw"])    # hay over the floor,
        for hx, hz, r in ((-W / 2 + T + 0.7, -0.95, 0.65), (-0.6, -D / 2 + T + 0.75, 0.85)):          # heaped up at the back
            add.mesh(add.move(add.stretch(add.make(add.hemisphere, [0, 0, 0], r, 8, P["straw"]), [1.15, 0.8, 0.85], (0, 0, 0)), [hx, LF, hz]))
        for i in range(4):                                                                        # where the hands sleep
            sx_ = -W / 2 + T + 0.6 + i * 1.1
            blanket = (P["wood_light"], P["leaf_dark"], P["blue"], P["red"])[(i + seed) % 4]
            if "sleep" in folk and i < 2:
                asleep([sx_, LF + 0.2, 0.9], add.pi, blanket, seed + i, pillow=True)
            else:
                add.cuboid([sx_, LF + 0.215, 0.95], [0.9, 0.03, 1.6], blanket)
        add.cylinder([W / 2 - T - 0.6, LF + 0.2, -0.4], [W / 2 - T - 1.2, LF + 1.5, 0.2], 0.025, 6, P["wood"])   # a pitchfork
        for k in range(3):
            add.cylinder([W / 2 - T - 1.2 - 0.05 * (k - 1), LF + 1.5, 0.2], [W / 2 - T - 1.35 - 0.05 * (k - 1), LF + 1.85, 0.35], 0.01, 4, P["iron"])
        add.cuboid([-W / 2 - 0.3, (hay[2] + hay[3]) / 2, hay[0] + hay[1] + 0.1], [0.05, hay[3] - hay[2] - 0.04, hay[1] - 0.04],
                   shade_of("wood", 1))                                   # the hay door, swung open flat against the logs
        add.cuboid([-W / 2 - 0.35, hay[3] + 0.5, hay[0]], [1.1, 0.16, 0.16], P["wood_dark"])      # the hoist beam, pulley, rope
        add.torus([-W / 2 - 0.8, hay[3] + 0.36, hay[0]], 0.09, 0.025, 10, 5, P["wood"], axis=(0, 0, 1))
        add.cylinder([-W / 2 - 0.89, hay[3] + 0.36, hay[0]], [-W / 2 - 0.89, FT + 0.3, hay[0]], 0.015, 5, P["rope"])
        add.push()                                                              # the little window in the other gable
        window_frame({"x": 0.0, "y0": LF + 1.65, "y1": LF + 2.15, "w": 0.5, "arched": False, "kind": "window"}, T)
        add.mesh(add.move(add.rotateY(add.pop(), add.pi / 2), [W / 2 - T / 2, 0, 0]))
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def chicken(at, facing=0.0, color=None, rooster=False):
    """A hen scratching about the yard -- or a rooster: a plump body, the
    wings folded on it, a tail of feathers (a rooster's long, dark and
    sickle-shaped), the neck and head with a red comb and wattles, a
    beak, eyes, and legs with three toes forward and one back."""
    color = color or P["white"]
    add.push()
    add.ellipsoid([0, 0.34, 0], [0.26, 0.19, 0.17], 4, color)
    add.sphere([0.13, 0.31, 0], 0.15, 3, color)                                    # the breast
    for s in (-1, 1):
        add.ellipsoid([-0.03, 0.37, s * 0.14], [0.19, 0.1, 0.045], 3, color)       # the wings
    for i in range(4 if rooster else 3):                                          # the tail
        a = 0.7 + 0.3 * i
        n = (0.34, 0.04, 0.03) if rooster else (0.15, 0.035, 0.03)
        feather = add.rotateZ(add.make(add.ellipsoid, [0, 0, 0], list(n), 2, P["black"] if rooster else color), add.pi - a)
        add.mesh(add.move(feather, [-0.2 - n[0] * 0.7 * add.cos(a), 0.4 + n[0] * 0.7 * add.sin(a), (i - 1.5) * 0.02]))
    add.capsule([0.15, 0.42, 0], [0.22, 0.57, 0], 0.07, 8, color)                # neck and head
    add.sphere([0.25, 0.62, 0], 0.075, 3, color)
    add.cone([0.31, 0.61, 0], [0.39, 0.595, 0], 0.024, 5, P["orange"])
    for i in range(4 if rooster else 3):                                          # the comb, the wattles
        add.sphere([0.2 + i * 0.035, 0.69 + (0.02 if rooster else 0.0) - abs(i - 1.5) * 0.01, 0], 0.035 if rooster else 0.025, 2, P["red"])
    for s in (-1, 1):
        add.ellipsoid([0.3, 0.54, s * 0.015], [0.014, 0.03 if rooster else 0.02, 0.01], 2, P["red"])
        add.sphere([0.29, 0.635, s * 0.052], 0.012, 2, P["black"])
        foot = [0.04, 0.0, s * 0.07]
        add.cylinder([0.02, 0.2, s * 0.07], foot, 0.018, 5, P["orange"])
        for a in (-0.5, 0.0, 0.5, add.pi):
            add.cylinder(foot, [foot[0] + 0.08 * add.cos(a), 0.0, foot[2] + 0.08 * add.sin(a)], 0.009, 4, P["orange"])
    add.mesh(add.move(add.rotateY(add.stretch(add.pop(), [0.78] * 3, (0, 0, 0)), facing), at))


def haystack(at, r=1.3, h=2.2):
    """A haystack built round a pole: bellied sides, a rounded top with a
    darker, weathered cap, ropes over it weighted with stones, and wisps
    of hay pulled out at its foot."""
    lathe([[0.0, 0.0], [r * 0.85, 0.0], [r, h * 0.2], [r * 0.98, h * 0.45], [r * 0.8, h * 0.7], [r * 0.45, h * 0.9], [0.0, h]],
          at, k_(12), P["straw"])
    lathe([[r * 0.55, h * 0.82], [r * 0.3, h * 0.94], [0.0, h + 0.03], [0.0, h * 0.8]], at, k_(12), P["rope"])
    add.cylinder([at[0], at[1] + h - 0.3, at[2]], [at[0], at[1] + h + 0.5, at[2]], 0.05, 6, P["wood_dark"])
    for i in range(4):                                                            # ropes over the top, stones on their ends
        a = add.pi * i / 2 + 0.4
        pts = [[at[0] + rr * add.cos(a), at[1] + yy, at[2] + rr * add.sin(a)]
               for rr, yy in ((r * 0.3 + 0.03, h * 0.94), (r * 0.8 + 0.04, h * 0.7), (r * 0.99 + 0.04, h * 0.42), (r * 1.02, h * 0.3))]
        add.polyline(pts, 0.018, 4, P["rope"])
        add.sphere([pts[-1][0] * 1.0, at[1] + h * 0.28, pts[-1][2]], 0.1, 3, P["rock"])
    for i in range(10):                                                           # wisps at the foot
        a = 2 * add.pi * (i + hash2(i, 3, 81)) / 10
        add.cylinder([at[0] + r * 0.85 * add.cos(a), at[1] + 0.03, at[2] + r * 0.85 * add.sin(a)],
                     [at[0] + (r + 0.35) * add.cos(a + 0.1), at[1] + 0.02, at[2] + (r + 0.35) * add.sin(a + 0.1)], 0.025, 4, P["straw"])


def fruit_tree(at, h=3.2):
    """A small apple tree: a trunk, a round crown of a few balls of leaves,
    red apples on it."""
    x, y, z = at
    add.cylinder([x, y, z], [x, y + 0.42 * h, z], 0.035 * h, 8, P["trunk"])
    c, r = [x, y + 0.62 * h, z], 0.3 * h
    add.sphere(c, r, 4, P["leaf"])
    for i in range(3):
        a = 2 * add.pi * i / 3 + 0.4
        add.sphere([c[0] + 0.55 * r * add.cos(a), c[1] - 0.25 * r, c[2] + 0.55 * r * add.sin(a)], 0.6 * r, 3, P["leaf"])
    for i in range(14):                                                         # apples, on the crown's lower half
        a, e = 2 * add.pi * hash2(i, 1, 61), -0.9 + 1.2 * hash2(i, 2, 61)
        rr = r + 0.02
        add.sphere([c[0] + rr * add.cos(a) * add.cos(e), c[1] + rr * add.sin(e), c[2] + rr * add.sin(a) * add.cos(e)], 0.055, 2, P["apple"])


def garden(at, w=8.0, d=5.0):
    """A pleasure garden as the Middle Ages laid them out: a low clipped
    hedge round it with a topiary ball at each corner, open in the middle
    of each side; gravel walks in a cross and round the middle; four
    raised beds edged with boards -- roses, herbs with lavender, cabbages,
    flowers -- and in the middle an apple tree in a stone-kerbed bed."""
    add.push()
    hedge, gap = P["leaf_dark"], 1.0
    for sx in (-1, 1):                                                          # the hedge, eight lengths with rounded tops
        for half in (-1, 1):
            for along_z in (True, False):
                a, b = half * gap / 2, half * (d / 2 if along_z else w / 2)
                m, L = (a + b) / 2, abs(b - a)
                p = [sx * w / 2, 0.25, m] if along_z else [m, 0.25, sx * d / 2]
                add.cuboid(p, [0.45, 0.5, L] if along_z else [L, 0.5, 0.45], hedge)
                e = [0, 0, L / 2] if along_z else [L / 2, 0, 0]
                add.cylinder([p[0] - e[0], 0.5, p[2] - e[2]], [p[0] + e[0], 0.5, p[2] + e[2]], 0.225, 10, hedge)
    for sx in (-1, 1):
        for sz in (-1, 1):
            add.sphere([sx * w / 2, 0.82, sz * d / 2], 0.34, 4, hedge)
    add.cuboid([0, 0.03, 0], [w + 0.45, 0.04, gap], P["sand"])                  # the walks
    add.cuboid([0, 0.03, 0], [gap, 0.04, d + 0.45], P["sand"])
    i0 = gap / 2 + 0.15
    X, Z = w / 2 - 0.5, d / 2 - 0.5
    c = min(1.3, 0.6 * min(X - i0, Z - i0))
    add.cylinder([0, 0.0, 0], [0, 0.045, 0], (2 * i0 + c) / add.sqrt(2) + 0.05, k_(10), P["sand"])
    beds = []
    for sx, sz in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
        outline = [(sx * (i0 + c), sz * i0), (sx * X, sz * i0), (sx * X, sz * Z), (sx * i0, sz * Z), (sx * i0, sz * (i0 + c))]
        add.mesh(solid(outline, 0.0, 0.25, P["wood_dark"]))                     # the boards ...
        add.mesh(solid(shrunk(outline, 0.07), 0.1, 0.26, P["trunk"]))            # ... and the earth in them
        beds.append((sx, sz))
    y0 = 0.26

    def spots(sx, sz, n, m, margin=0.3):
        """n x m planting spots on a grid in the bed (sx, sz), clear of its cut corner."""
        out = []
        for i in range(n):
            for j in range(m):
                x = i0 + margin + (X - i0 - 2 * margin) * (i + 0.5) / n
                z = i0 + margin + (Z - i0 - 2 * margin) * (j + 0.5) / m
                if x + z > 2 * i0 + c + 0.25:
                    out.append((sx * x, sz * z, i, j))
        return out
    for x, z, i, j in spots(1, 1, 3, 3):                                        # roses
        add.ellipsoid([x, y0 + 0.24, z], [0.27, 0.26, 0.27], 3, P["leaf_dark"])
        for k in range(6):
            a = 2 * add.pi * k / 6 + i
            col = P["red"] if (i + j) % 2 else P["white"]
            add.sphere([x + 0.2 * add.cos(a), y0 + 0.36 + 0.06 * (k % 2), z + 0.2 * add.sin(a)], 0.055, 2, col)
    for x, z, i, j in spots(-1, 1, 4, 4):                                       # herbs, and lavender
        if j % 2:
            add.ellipsoid([x, y0 + 0.1, z], [0.16, 0.12, 0.16], 2, (P["leaf"], P["grass"], P["grass_dry"])[(i + j) % 3])
        else:
            add.ellipsoid([x, y0 + 0.08, z], [0.14, 0.08, 0.14], 2, P["leaf_dark"])
            for k in range(5):
                a = 2 * add.pi * k / 5
                add.cylinder([x + 0.07 * add.cos(a), y0 + 0.1, z + 0.07 * add.sin(a)],
                              [x + 0.1 * add.cos(a), y0 + 0.36, z + 0.1 * add.sin(a)], 0.018, 4, P["purple"])
    for x, z, i, j in spots(-1, -1, 3, 4):                                      # cabbages in rows
        add.ellipsoid([x, y0 + 0.03, z], [0.26, 0.05, 0.26], 2, P["leaf"])
        add.sphere([x, y0 + 0.14, z], 0.15, 3, P["grass"])
    for x, z, i, j in spots(1, -1, 5, 5, 0.22):                                 # flowers, in clumps of colour
        col = (P["red"], P["cheese"], P["white"], P["purple"], P["orange"])[(i // 2 + j // 2 * 2) % 5]
        for k in range(3):
            fx, fz = x + 0.1 * add.cos(k * 2.1 + i), z + 0.1 * add.sin(k * 2.1 + i)
            add.cylinder([fx, y0, fz], [fx, y0 + 0.3 + 0.05 * k, fz], 0.012, 4, P["leaf"])
            add.sphere([fx, y0 + 0.33 + 0.05 * k, fz], 0.065, 2, col)
    add.pipe([0, 0, 0], [0, 0.35, 0], 0.9, 0.72, k_(12), P["stone_dark"])       # the tree in the middle
    add.cylinder([0, 0.1, 0], [0, 0.3, 0], 0.72, k_(12), P["trunk"])
    fruit_tree([0, 0.3, 0], 3.2)
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
    bowl([-1.4, 1.0, 0.2], 0.22, P["wood_light"], (P["apple"], P["apple"], P["cheese"]))
    bowl([-0.6, 1.0, -0.3], 0.22, P["wood_light"], (P["orange"], P["orange"]))
    bread([0.2, 1.0, 0.2], 3)
    cheese([1.0, 1.0, -0.3])
    for i in range(3):                                                                   # fish, laid on their sides
        f = add.rotateX(add.make(fish, [0, 0, 0], 0.0, P["steel"] if i % 2 else P["slate"], 0.32), add.pi / 2)
        add.mesh(add.move(add.rotateY(f, add.pi / 2 + 0.2 * (i - 1)), [1.5, 1.08, -0.5 + i * 0.4]))
    jug([1.6, 1.0, 0.5])
    sack([-1.2, 0.0, 1.3], 0.4)
    sack([-0.4, 0.0, 1.4], 0.35)
    crate([0.9, 0.0, 1.4], 0.7)
    standing_man([0.3, 0, -0.7], add.pi, P["leaf"], hat=True)                                # the stallholder
    standing_man([-0.9, 0, 1.9], 0, P["blue"])                                                # a customer
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


# life-size, head towards +x (its right side on +z), hooves on y = 0
HORSE = [(-0.845, 1.25, 0.09, 0.07), (-0.8, 1.24, 0.22, 0.15), (-0.72, 1.225, 0.3, 0.215), (-0.56, 1.22, 0.335, 0.25),
         (-0.35, 1.2, 0.35, 0.27), (-0.1, 1.17, 0.36, 0.285), (0.15, 1.17, 0.36, 0.29), (0.38, 1.2, 0.35, 0.265),
         (0.55, 1.24, 0.32, 0.23), (0.68, 1.23, 0.26, 0.18), (0.77, 1.2, 0.16, 0.115), (0.805, 1.2, 0.07, 0.055)]                  # the body: (x, y of the middle, half-height, half-width)
NECK = ([(0.5, 1.28), (0.66, 1.47), (0.8, 1.66), (0.92, 1.83), (1.0, 1.95)],
        (0.26, 0.2, 0.15, 0.125, 0.11), (0.3, 0.23, 0.16, 0.13, 0.12), (0.21, 0.16, 0.13, 0.11, 0.095))
HEAD = ([(0.97, 1.93), (1.07, 1.8), (1.19, 1.645), (1.28, 1.525), (1.335, 1.45)],
        (0.11, 0.1, 0.085, 0.078, 0.06), (0.17, 0.13, 0.085, 0.07, 0.055), (0.105, 0.092, 0.076, 0.07, 0.056))
FORELEG = ([(0.5, 1.02), (0.505, 0.85), (0.515, 0.66), (0.52, 0.55), (0.525, 0.46), (0.53, 0.25), (0.535, 0.2), (0.56, 0.14), (0.585, 0.09)],
           (0.1, 0.085, 0.066, 0.064, 0.05, 0.048, 0.058, 0.044, 0.048), (0.61, 0.0))
HINDLEG = ([(-0.38, 0.95), (-0.47, 0.8), (-0.56, 0.66), (-0.62, 0.58), (-0.61, 0.46), (-0.595, 0.25), (-0.59, 0.2), (-0.565, 0.14), (-0.54, 0.09)],
           (0.125, 0.1, 0.07, 0.066, 0.052, 0.05, 0.058, 0.044, 0.048), (-0.515, 0.0))


def horse_pt(x, a, off=0.0):
    """A point of the horse's body at ``x`` and angle ``a`` round it (0:
    the back, pi/2: its right side, pi: the belly), ``off`` out from it."""
    i = next((j for j in range(len(HORSE) - 2) if x <= HORSE[j + 1][0]), len(HORSE) - 2)
    r0, r1 = HORSE[i], HORSE[i + 1]
    t = max(0.0, min(1.0, (x - r0[0]) / (r1[0] - r0[0])))
    cy, hh, hw = [r0[j] + (r1[j] - r0[j]) * t for j in (1, 2, 3)]
    c, s = add.cos(a), add.sin(a)
    g = vunit([0, c / hh, s / hw])
    return [x, cy + hh * c + g[1] * off, hw * s + g[2] * off]


def tube_at(spec, u, q, off=0.0):
    """A point on a horse's neck or head: ``spec`` is a path in the middle
    plane with half-heights above and below it and half-widths; ``u`` is
    the (fractional) number of the path point, ``q`` the angle round the
    path (0: the crest or the face, pi/2: the right side), ``off`` out."""
    path, top, bottom, half = spec
    n = len(path) - 1

    def at(i):
        a, b = path[max(0, i - 1)], path[min(n, i + 1)]
        t = vunit([b[0] - a[0], b[1] - a[1], 0])
        return path[i], [-t[1], t[0]], top[i], bottom[i], half[i]
    i = min(int(u), n - 1)
    f = u - i
    A, B = at(i), at(i + 1)
    c = [A[0][k] + (B[0][k] - A[0][k]) * f for k in (0, 1)]
    nrm = vunit([A[1][0] + (B[1][0] - A[1][0]) * f, A[1][1] + (B[1][1] - A[1][1]) * f, 0])
    ht, hb, hw = [A[k] + (B[k] - A[k]) * f for k in (2, 3, 4)]
    h = ht if add.cos(q) > 0 else hb
    cq, sq = add.cos(q), add.sin(q)
    g = vunit([nrm[0] * cq / h, nrm[1] * cq / h, sq / hw])
    return [c[0] + nrm[0] * h * cq + g[0] * off, c[1] + nrm[1] * h * cq + g[1] * off, hw * sq + g[2] * off]


def horse_body(color=None, mane=None, saddle=True, stirrups=None, hand=None):
    """A horse standing still, life-size, head towards +x: a barrel of a
    body with the muscles of the shoulders and quarters, an arched neck,
    the head with its jowls, ears, eyes and nostrils, mane and forelock, a
    flowing tail, four jointed legs (knees in front, hocks behind, fetlocks,
    sloping pasterns) on dark hooves, and a head collar.  With ``saddle``:
    a saddle cloth with a gold border, a war saddle with a high cantle and
    pommel, the girth and breast strap, stirrups (at ``stirrups`` =
    (x, y, |z|) if given), a bit and the reins (to ``hand`` if given)."""
    color, mane, strap = color or P["trunk"], mane or P["black"], P["wood_dark"]
    add.push()
    add.loft([[horse_pt(r[0], 2 * add.pi * (j + 0.5) / 18) for j in range(18)] for r in HORSE], color)
    for spec, k in ((NECK, 16), (HEAD, 16)):
        add.loft([[tube_at(spec, i, 2 * add.pi * (j + 0.5) / k) for j in range(k)] for i in range(len(spec[0]))], color)
    for s in (-1, 1):
        add.ellipsoid([-0.47, 1.1, s * 0.13], [0.3, 0.32, 0.15], 4, color)                       # the quarters
        blade = add.make(add.ellipsoid, [0, 0, 0], [0.13, 0.33, 0.125], 4, color)             # the shoulder
        add.mesh(add.move(add.rotateZ(blade, 0.5), [0.5, 1.2, s * 0.13]))
        add.ellipsoid([0.95, 1.85, s * 0.055], [0.11, 0.1, 0.06], 3, color)                   # the jowl
        ear = tube_at(HEAD, 0.05, s * 0.55, -0.01)
        add.cone(ear, [ear[0] + 0.02, ear[1] + 0.13, ear[2] + s * 0.03], 0.04, 6, color)
        add.sphere(tube_at(HEAD, 0.8, s * 1.2), 0.022, 3, P["black"])                          # the eye
        add.sphere(tube_at(HEAD, 3.85, s * 0.9, -0.005), 0.017, 2, P["black"])                 # the nostril
        for pts, radii, hoof in (FORELEG, HINDLEG):
            z = s * (0.15 if hoof[0] > 0 else 0.155)
            add.polyline([[x, y, z] for x, y in pts], ramp(radii), 12, color)
            add.frustum([pts[-1][0], pts[-1][1], z], [hoof[0], hoof[1], z], 0.054, 0.068, 12, P["black"])
        add.sphere([-0.67, 0.62, s * 0.155], 0.04, 3, color)                                   # the point of the hock
    add.sphere([1.328, 1.458, 0], 0.062, 4, color)                                               # the muzzle
    add.parametric(lambda u, v: tube_at(NECK, u, v * (1.45 + 0.2 * add.sin(u * 7.0)), 0.022 - 0.01 * v), 0.3, 3.95, 18, 0, 1, 3,
                   mane, thickness=0.014)                                                      # the mane, lying to the right
    add.polyline([tube_at(NECK, 0.25 + 0.25 * i, 0.0, 0.012) for i in range(16)], 0.026, 6, mane)
    add.polyline([[1.0, 2.03, 0], tube_at(HEAD, 0.5, 0.0, 0.01), tube_at(HEAD, 0.9, 0.0, 0.008)], lambda t: 0.026 - 0.014 * t, 5, mane)
    tail = [[-0.78, 1.42, 0], [-0.86, 1.36, 0], [-0.915, 1.2, 0], [-0.935, 1.0, 0.01], [-0.935, 0.8, 0.015], [-0.925, 0.64, 0.02]]
    add.polyline(tail, ramp((0.05, 0.06, 0.075, 0.08, 0.07, 0.035)), 10, mane, smooth=1)
    add.polyline([tube_at(HEAD, 2.9, 2 * add.pi * j / 12, 0.008) for j in range(12)], 0.011, 5, strap, closed=True)   # noseband
    add.polyline([tube_at(HEAD, 0.05, q, 0.008) for q in (-1.4, -0.8, -0.3, 0.3, 0.8, 1.4)], 0.011, 5, strap)         # headpiece
    add.polyline([tube_at(HEAD, 0.45, q, 0.008) for q in (-1.3, -0.6, 0.0, 0.6, 1.3)], 0.011, 5, strap)               # browband
    for s in (-1, 1):
        add.polyline([tube_at(HEAD, 0.05, s * 1.5, 0.008), tube_at(HEAD, 1.0, s * 1.65, 0.008), tube_at(HEAD, 2.9, s * 1.62, 0.008)], 0.011, 5, strap)
    if not saddle:
        return add.pop()
    add.parametric(lambda u, v: horse_pt(-0.12 + 0.54 * u, -1.7 + 3.4 * v, 0.012), 0, 1, 12, 0, 1, 18, thickness=0.008,
                   color=lambda u, v: P["gold"] if u < 0.07 or u > 0.93 or v < 0.04 or v > 0.96 else P["red"])   # the saddle cloth
    add.loft([[horse_pt(x, 2 * add.pi * (j + 0.5) / 18, 0.022) for j in range(18)] for x in (0.31, 0.35)], strap)     # the girth
    add.ellipsoid([0.12, 1.555, 0], [0.2, 0.05, 0.19], 4, strap)                                                  # the seat
    add.cylinder([-0.1, 1.56, 0], [-0.065, 1.56, 0], 0.15, 16, P["wood"])                                         # the cantle
    add.cylinder([0.34, 1.56, 0], [0.375, 1.56, 0], 0.12, 16, P["wood"])                                          # the pommel
    add.polyline([horse_pt(0.36, -1.4, 0.025), horse_pt(0.55, -1.5, 0.015), horse_pt(0.68, -1.55, 0.015), [0.787, 1.22, 0.0],
                  horse_pt(0.68, 1.55, 0.015), horse_pt(0.55, 1.5, 0.015), horse_pt(0.36, 1.4, 0.025)], 0.013, 5, strap)   # breast strap
    for s in (-1, 1):
        x, y, z = stirrups or (0.14, 0.95, 0.3)
        add.polyline([[0.15, 1.52, s * 0.17], horse_pt((0.15 + x) / 2, s * 1.32, 0.035), [x, y + 0.05, s * z]], 0.012, 5, strap)
        add.torus([x, y, s * z], 0.055, 0.009, 12, 6, P["iron"], axis=(1, 0, 0))                  # the stirrup
        bit = tube_at(HEAD, 3.3, s * 1.9, 0.004)
        add.torus(bit, 0.022, 0.005, 10, 5, P["iron"], axis=(0, 0, 1))                            # the bit ring
        end = hand or [0.37, 1.63, s * 0.06]
        add.polyline([bit, [0.9, 1.66, s * 0.15], [0.62, 1.74, s * 0.1], end], 0.009, 5, strap, smooth=1)   # the reins
    return add.pop()


def horse(at, facing=0.0, color=None, saddle=True, mane=None):
    """A horse standing on ``at``, its head towards ``facing`` (0: +x)."""
    M = add.stretch(horse_body(color, mane, saddle), [LIFE] * 3, (0, 0, 0))
    add.mesh(add.move(add.rotateY(M, facing), at))


def rider(at, facing=0.0):
    """A knight on horseback: the knight in the saddle, his feet in the
    stirrups, the reins in his left hand, his shield hung at his left
    side, the lance upright in his right hand with a pennon of the
    castle's colours; the horse saddled and bridled."""
    seat = [0.12, 0.74, 0.0]                                              # the knight's origin, on the horse

    def on_horse(p):                                                      # (he faces +z; the horse +x)
        return [seat[0] + p[2], seat[1] + p[1], seat[2] - p[0]]
    right, left = fists("ride")
    add.push()
    add.mesh(horse_body(P["wood_dark"], None, True, (0.507, 0.953, 0.357), on_horse(left)))
    add.mesh(add.move(add.rotateY(knight("ride"), add.pi / 2), seat))
    x, z = on_horse(right)[0], on_horse(right)[2]
    add.cylinder([x, 1.07, z], [x, 4.0, z], 0.021, 8, P["wood"])                                  # the lance
    add.frustum([x, 3.98, z], [x, 4.06, z], 0.026, 0.022, 8, P["steel"])
    add.cone([x, 4.12, z], [x, 4.34, z], 0.045, 4, P["steel"])
    add.cone([x, 4.12, z], [x, 4.05, z], 0.045, 4, P["steel"])
    sheet([[x, 3.96, z], [x, 3.87, z], [x - 0.6, 3.915, z]], P["red"])                             # the pennon
    sheet([[x, 3.87, z], [x, 3.78, z], [x - 0.52, 3.83, z]], P["gold"])
    add.mesh(add.move(add.rotateY(add.stretch(add.pop(), [LIFE] * 3, (0, 0, 0)), facing), at))


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
    """A round dovecote: a whitewashed drum on a stone plinth with a little
    door, flight holes with landing ledges, a slate cone with a gold finial,
    pigeons perched and one on the roof."""
    add.cylinder(at, [at[0], at[1] + 0.6, at[2]], 0.82, k_(12), P["stone_dark"])
    add.cylinder([at[0], at[1] + 0.6, at[2]], [at[0], at[1] + 3.6, at[2]], 0.7, k_(12), P["white"])
    add.torus([at[0], at[1] + 3.55, at[2]], 0.72, 0.05, k_(12), 5, P["wood_dark"])
    add.cone([at[0], at[1] + 3.6, at[2]], [at[0], at[1] + 4.8, at[2]], 0.95, k_(12), P["slate"])
    add.sphere([at[0], at[1] + 4.85, at[2]], 0.08, 4, P["gold"])
    add.cuboid([at[0], at[1] + 1.05, at[2] + 0.69], [0.5, 0.9, 0.06], P["wood_dark"])                      # the door
    add.torus([at[0] + 0.15, at[1] + 1.0, at[2] + 0.73], 0.035, 0.008, 8, 4, P["iron"], axis=(0, 0, 1))
    bird([at[0] + 0.1, at[1] + 4.78, at[2] + 0.12], 2.0, 0.35, P["white"], False)
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


def gull(at, heading=0.0, bank=0.0, pitch=0.0, arm=0.15, hand=-0.35, size=1.0, tail=0.3):
    """A gull on the wing: a white body and head, a yellow beak with a red
    spot, black eyes, a white fan of a tail, the feet tucked under it, and
    long pointed wings -- grey above and white below, each an arm and a
    hand bent at the wrist, the hand ending in black tips.  ``arm`` lifts
    the inner wing (radians; raised on the upstroke, dropped on the
    down), ``hand`` bends the outer wing from it (down in a glide: the
    gull's M), ``bank`` rolls the bird into a turn, ``pitch`` lifts its
    head; ``heading`` is the way it flies."""
    grey, white = P["steel"], P["white"]
    add.push()
    add.ellipsoid([0, 0, 0], [0.42, 0.14, 0.15], 6, white)                                  # the body,
    add.sphere([0.4, 0.08, 0], 0.1, 8, white)                                              # the head,
    add.cone([0.48, 0.07, 0], [0.64, 0.045, 0], 0.028, 6, P["cheese"])                     # the beak and its red spot,
    add.sphere([0.585, 0.045, 0], 0.012, 3, P["red"])
    for s in (-1, 1):
        add.sphere([0.46, 0.11, s * 0.065], 0.014, 3, P["black"])                           # the eyes,
        add.cylinder([-0.22, -0.1, s * 0.04], [-0.36, -0.1, s * 0.05], 0.012, 5, P["pig"])  # the feet, tucked
    fan = [[-0.3, 0.0, 0.0], [-0.62, 0.0, tail * 0.45], [-0.66, 0.0, 0.0], [-0.62, 0.0, -tail * 0.45]]
    fan = [[x, 0.02 + (x + 0.3) * 0.15, z] for x, _, z in fan]
    add.polygon(fan[::-1], white)                                                          # the tail, a fan, both sides
    add.polygon([[x, y - 0.015, z] for x, y, z in fan], white)
    for s in (-1, 1):                                                                        # the wings
        ca, sa = add.cos(arm), add.sin(arm)
        ch, sh = add.cos(arm + hand), add.sin(arm + hand)
        root_le, root_te = [0.16, 0.05, s * 0.12], [-0.16, 0.05, s * 0.12]
        wrist = [0.0, 0.05 + 0.6 * sa, s * (0.12 + 0.6 * ca)]
        w_le, w_te = [wrist[0] + 0.14, wrist[1], wrist[2]], [wrist[0] - 0.2, wrist[1], wrist[2]]
        tip = [wrist[0] - 0.38, wrist[1] + 0.78 * sh, wrist[2] + s * 0.78 * ch]
        m_le = [w_le[k] + 0.68 * (tip[k] - w_le[k]) for k in range(3)]
        m_te = [w_te[k] + 0.6 * (tip[k] - w_te[k]) for k in range(3)]
        for poly, top in (([root_le, w_le, w_te, root_te], grey), ([w_le, m_le, m_te, w_te], grey), ([m_le, tip, m_te], P["black"])):
            n = vcross(vsub(poly[1], poly[0]), vsub(poly[2], poly[0]))
            if n[1] < 0:
                poly = poly[::-1]
            add.polygon([[x, y + 0.012, z] for x, y, z in poly], top)                      # grey above, white beneath
            add.polygon(poly[::-1], white if top is grey else P["black"])
        add.cylinder(root_le, w_le, 0.03, 6, white)                                        # the arm's leading edge
        add.cylinder(w_le, m_le, 0.018, 6, grey)
    M = add.rotateZ(add.rotateX(add.pop(), bank), pitch)
    add.mesh(add.move(add.rotateY(add.stretch(M, [size] * 3, (0, 0, 0)), heading), at))


def dog(at, facing=0.0, color=None):
    """A dog standing about: a deep chest and a tucked belly, a neck, the
    head with a muzzle, a black nose, eyes and hanging ears, four legs
    bent at the elbows and hocks on round paws, the tail up."""
    color = color or P["wood_light"]
    dark = P["wood"]
    add.push()
    add.ellipsoid([-0.02, 0.52, 0], [0.34, 0.15, 0.13], 4, color)                # the body
    add.ellipsoid([0.22, 0.5, 0], [0.17, 0.18, 0.14], 3, color)                  # the chest
    add.ellipsoid([0.27, 0.47, 0], [0.08, 0.12, 0.09], 3, P["white"])            # a white bib
    add.capsule([0.3, 0.58, 0], [0.42, 0.74, 0], 0.08, 8, color)                 # the neck
    add.ellipsoid([0.47, 0.78, 0], [0.11, 0.095, 0.085], 3, color)               # the head
    add.capsule([0.52, 0.745, 0], [0.64, 0.715, 0], 0.048, 8, color)             # the muzzle
    add.sphere([0.68, 0.72, 0], 0.024, 2, P["black"])
    for s in (-1, 1):
        add.sphere([0.54, 0.8, s * 0.05], 0.013, 2, P["black"])
        add.ellipsoid([0.44, 0.75, s * 0.09], [0.045, 0.075, 0.015], 2, dark)    # the ears, hanging
        for hip, knee, paw in (([0.24, 0.45, s * 0.08], [0.27, 0.24, s * 0.08], [0.26, 0.03, s * 0.08]),
                               ([-0.26, 0.47, s * 0.09], [-0.33, 0.22, s * 0.09], [-0.28, 0.03, s * 0.09])):
            add.capsule(hip, knee, 0.045 if hip[0] > 0 else 0.055, 8, color)
            add.capsule(knee, paw, 0.034, 8, color)
            add.ellipsoid([paw[0] + 0.03, 0.03, paw[2]], [0.05, 0.03, 0.04], 2, color)
    add.polyline([[-0.33, 0.58, 0], [-0.46, 0.68, 0.0], [-0.5, 0.84, 0.03], [-0.44, 0.95, 0.05]], lambda t: 0.035 - 0.02 * t, 6, color, smooth=1)
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


def kitchen(at, facing=0.0):
    """The castle's kitchen and bakehouse, where the servants also sleep: a
    stone house under a tiled gable roof with half-timbered gables, a great
    brick chimney with smoke rising, the plank door standing open, glazed
    windows with their shutters open.  Inside, on a floor of boards: an open
    hearth under a hood at the foot of the chimney, a cauldron hanging from a
    tripod over the fire and the cook stirring it; a table with benches where
    two men eat; three beds against the back wall, one slept in; a shelf of
    bowls and jugs, a barrel and sacks of flour.  Outside, a domed bread oven
    with a fire in its mouth and the baker by it, his peel leaning on the
    oven, firewood stacked under the eaves, a chopping block with an axe in
    it and a water barrel.  Built with its door towards +z, 10 m long and
    6 m deep."""
    W, D, H, R, T = 10.0, 6.0, 3.8, 6.6, 0.45                                 # length, depth, walls, ridge, wall thickness
    FL = 0.12                                                                  # the floor of boards inside
    add.push()
    door, windows = (-1.5, 1.4, 2.6), ((1.8, 1.0, 1.1), (3.9, 1.0, 1.1))
    end_z = D / 2 - 1.0                                                        # a window in the end, by the oven
    shell = add.make(add.cuboid, [0, H / 2, 0], [W, H, D], P["mortar"])
    room = add.make(add.cuboid, [0, (FL - 0.04 + H + 1) / 2, 0], [W - 2 * T, H + 1 - FL + 0.04, D - 2 * T], P["white"])
    holes = [add.make(add.cuboid, [door[0], (FL - 0.04 + door[2]) / 2, D / 2], [door[1], door[2] - FL + 0.04, 2 * T + 0.2], P["stone_dark"]),
             add.make(add.cuboid, [W / 2, 1.85, end_z], [2 * T + 0.2, 1.1, 1.0], P["white"])]
    holes += [add.make(add.cuboid, [x, 1.3 + h / 2, D / 2], [w, h, 2 * T + 0.2], P["white"]) for x, w, h in windows]
    add.mesh(add.difference(shell, room, *holes))                              # walls of stone, plastered white inside
    slope = (R - H + 0.38) / (D / 2 + 0.5)                                     # the roof's underside, y at |z|
    under = lambda z: H - 0.38 + (D / 2 + 0.5 - z) * slope + 0.03
    for sz in (-1, 1):                                                         # the walls carried up to the roof
        prof = [[H - 0.01, sz * D / 2], [H - 0.01, sz * (D / 2 - T)], [under(D / 2 - T), sz * (D / 2 - T)], [under(D / 2), sz * D / 2]]
        add.mesh(add.make(add.prism, prof, W, P["white"], (0, 0, 0), (1, 0, 0)))
    skips = {0: [(W / 2 + door[0] - door[1] / 2, W / 2 + door[0] + door[1] / 2, 0, door[2])] +
             [(W / 2 + x - w / 2, W / 2 + x + w / 2, 1.3, 1.3 + h) for x, w, h in windows],
             1: [(D / 2 - end_z - 0.5, D / 2 - end_z + 0.5, 1.3, 2.4)]}
    for face in range(4):                                                      # stone skins, fitted round the openings
        L = W if face % 2 == 0 else D
        add.push()
        stone_face(L, 0, H, 0, 0.08, "stone", skip=skips.get(face, ()), seed=face + 11)
        M = add.move(add.pop(), [-L / 2, 0, (D if face % 2 == 0 else W) / 2])
        add.mesh(add.rotateY(M, face * add.pi / 2))
    add.push()                                                                 # the door, standing open into the room,
    add.cuboid([door[1] / 2, (FL + door[2]) / 2, -0.035], [door[1] - 0.04, door[2] - FL - 0.04, 0.07], P["wood_dark"])
    for y in (0.6, 2.0):                                                       # on its iron straps
        add.cuboid([0.5, y, 0.005], [1.0, 0.07, 0.02], P["iron"])
    add.torus([door[1] - 0.25, 1.25, 0.03], 0.06, 0.012, 10, 5, P["iron"], axis=(0, 0, 1))
    add.mesh(add.move(add.rotateY(add.pop(), 1.25), [door[0] - door[1] / 2, 0, D / 2 - T]))
    add.cuboid([door[0], door[2] + 0.15, D / 2 + 0.07], [door[1] + 0.5, 0.3, 0.14], P["stone_dark"])   # its lintel
    glazed = [(x, w, h, [0, 0, D / 2 - T / 2], 0.0) for x, w, h in windows] + [(0.0, 1.0, 1.1, [W / 2 - T / 2, 0, end_z], add.pi / 2)]
    for x, w, h, where, turn in glazed:                                        # glass in a frame, mid-wall
        add.push()
        window_frame({"x": x, "y0": 1.3, "y1": 1.3 + h, "w": w, "arched": False, "kind": "window"}, T)
        add.mesh(add.move(add.rotateY(add.pop(), turn), where))
    for x, w, h in windows:
        add.cuboid([x, 1.25, D / 2 + 0.12], [w + 0.3, 0.1, 0.24], P["stone_dark"])          # the sill
        for sx in (-1, 1):                                                               # shutters, open against the wall
            add.cuboid([x + sx * (w * 0.75 + 0.03), 1.3 + h / 2, D / 2 + 0.11], [w / 2, h, 0.05], P["wood"])
    add.cuboid([W / 2 + 0.12, 1.25, end_z], [0.24, 0.1, 1.3], P["stone_dark"])
    for sx in (-1, 1):                                                                   # gables: plaster in a timber frame
        x = sx * (W / 2 - 0.05)
        add.mesh(add.make(add.prism, [[H, -D / 2 - 0.08], [H, D / 2 + 0.08], [R - 0.12, 0.0]], 0.26, P["white"], (x, 0, 0), (1, 0, 0)))
        x = sx * (W / 2 + 0.1)
        add.cuboid([x, H + 0.08, 0], [0.12, 0.18, D + 0.16], P["wood_dark"])
        add.cuboid([x, (H + R) / 2, 0], [0.12, R - H - 0.2, 0.16], P["wood_dark"])
        for sz in (-1, 1):
            add.beam([x, H + 0.15, sz * (D / 2 - 0.3)], [x, H + 1.3, sz * 0.08], 0.12, 0.12, P["wood_dark"])
    chimney = (2.6, -1.4, 1.2, 1.0)                                            # x, z, width, depth
    for sz in (-1, 1):                                                          # the roof: boards and clay tiles
        eave, top = [W / 2 + 0.35, H - 0.38, sz * (D / 2 + 0.5)], [W / 2 + 0.35, R, 0.0]
        quad = [[-eave[0], eave[1], eave[2]], eave, top, [-top[0], top[1], top[2]]]
        if sz < 0:
            quad = [quad[1], quad[0], quad[3], quad[2]]
        add.mesh(slab(quad, 0.15, P["wood_dark"]))
        lift = [[q[0], q[1] + 0.15 / add.cos(add.atan2(R - H + 0.38, D / 2 + 0.5)), q[2]] for q in quad]
        tile_face(*lift, blocked=lambda x, z: abs(x - chimney[0]) < chimney[2] / 2 + 0.2 and abs(z - chimney[1]) < chimney[3] / 2 + 0.2)
    add.beam([-W / 2 - 0.35, R + 0.2, 0], [W / 2 + 0.35, R + 0.2, 0], 0.3, 0.16, P["spire"])      # the ridge
    brick_box([chimney[0], (R + 1.6) / 2, chimney[1]], [chimney[2], R + 1.6, chimney[3]], flue=(0.5, 0.4, 1.0))
    chimney_cap([chimney[0], R + 1.68, chimney[1]], chimney[2] + 0.2, chimney[3] + 0.2, 0.16, (0.5, 0.4))
    for i in range(4):
        add.sphere([chimney[0] + 0.25 * add.sin(i * 1.3), R + 2.3 + 0.8 * i, chimney[1] - 0.2 * i], 0.35 + 0.12 * i, 8, SMOKE)
    cx, cz = chimney[0], chimney[1] + chimney[3] / 2 + 0.6                     # inside: the hearth at the chimney's foot,
    plank_floor(-W / 2 + T, W / 2 - T, -D / 2 + T, D / 2 - T, FL, along="x",
                holes=[(cx - 0.8, cx + 0.8, chimney[1] - chimney[3] / 2, cz + 0.6)])
    brick_box([cx, (FL - 0.04 + 0.52) / 2, cz], [1.6, 0.56 - FL, 1.2])
    hood = [[1.95, cz - 0.65], [1.95, cz + 0.7], [2.15, cz + 0.7], [3.3, cz - 0.3], [3.3, cz - 0.65]]
    add.mesh(add.make(add.prism, hood, 1.8, P["white"], (cx, 0, 0), (1, 0, 0)))  # its hood, drawing the smoke up the flue
    add.cuboid([cx, 2.02, cz + 0.72], [1.9, 0.16, 0.1], P["wood_dark"])            # a beam along the hood's mouth
    for i, (dx, dz, a) in enumerate(((-0.25, 0.1, 0.3), (0.1, -0.15, -0.4), (0.3, 0.2, 0.9))):   # logs, burning
        add.cylinder([cx + dx - 0.35 * add.cos(a), 0.6, cz + dz - 0.35 * add.sin(a)],
                     [cx + dx + 0.35 * add.cos(a), 0.6, cz + dz + 0.35 * add.sin(a)], 0.07, 7, pick("wood", i, 3))
    for i in range(5):
        a = 2 * add.pi * i / 5
        add.cone([cx + 0.2 * add.cos(a), 0.6, cz + 0.2 * add.sin(a)], [cx + 0.15 * add.cos(a), 0.8 + 0.03 * (i % 2), cz + 0.15 * add.sin(a)],
                 0.1, 8, FLAME)
    add.sphere([cx, 0.62, cz], 0.12, 4, P["flame_core"])
    PY = 0.85                                                                  # the cauldron over it, on a chain
    add.cylinder([cx, 1.96, cz], [cx, PY + 0.66, cz], 0.012, 4, P["iron"])      # from a hook in the hood
    lathe([[0.0, 0], [0.14, 0], [0.26, 0.08], [0.3, 0.22], [0.27, 0.36], [0.28, 0.4], [0.25, 0.4], [0.24, 0.36], [0.0, 0.3]],
          [cx, PY, cz], k_(12), P["iron"])
    add.torus([cx, PY + 0.4, cz], 0.26, 0.012, k_(12), 4, P["iron"], axis=(1, 0, 0))   # by its bail
    add.cylinder([cx, PY + 0.31, cz], [cx, PY + 0.315, cz], 0.24, k_(12), P["bread"])  # the pottage in it
    cook = person("stand", gown=P["brick"], female=True, head=("veil", P["white"]), hair=P["trunk"],
                  arms=(([-0.05, 1.12, 0.33], [0.25, -0.35, 1], [-1, -0.5, -0.3]), ([0.1, 1.08, 0.3], [-0.5, -0.1, 1], [1, -0.6, -0.3])))
    figure([cx, FL, cz + 1.25], add.pi, cook)                                  # the cook, stirring it
    add.cylinder([cx + 0.04, 1.44, cz + 0.92], [cx, PY + 0.33, cz + 0.1], 0.018, 6, P["wood"])   # her ladle
    tx, tz = 0.4, 1.15                                                         # the table where the servants eat
    table([tx, FL, tz], 2.0, 0.85, 0.78, P["wood"])
    for sz in (-1, 1):
        add.cuboid([tx, FL + 0.45, tz + sz * 0.825], [1.8, 0.08, 0.3], P["wood"])
        for dx in (-0.75, 0.75):
            add.cuboid([tx + dx, FL + 0.21, tz + sz * 0.825], [0.08, 0.42, 0.24], P["wood_dark"])
    top = FL + 0.78
    bread([tx + 0.3, top, tz], 1)
    bowl([tx - 0.4, top, tz - 0.2], 0.14, P["wood_light"])
    bowl([tx + 0.4, top, tz + 0.22], 0.14, P["wood_light"])
    jug([tx - 0.8, top, tz + 0.15], P["brick"], 0.5)
    sitting_man([tx - 0.4, FL + 0.5, tz - 0.825], 0, P["blue"], (0.3, 0.4), seat=0.5)
    sitting_man([tx + 0.4, FL + 0.5, tz + 0.825], add.pi, P["leaf"], (0.3, 0.4), seat=0.5)
    for i, x in enumerate((-3.85, -2.6, -1.35)):                               # three beds against the back wall
        bed([x, FL, -D / 2 + T + 1.13], 0.0, sleeper=i == 0)
    add.cuboid([W / 2 - T - 0.15, 1.5, -1.2], [0.3, 0.05, 2.4], P["wood_dark"])    # a shelf on the end wall,
    for dz in (-2.2, -0.2):
        add.cuboid([W / 2 - T - 0.04, 1.4, dz], [0.08, 0.2, 0.05], P["wood_dark"])
    for i, dz in enumerate((-2.05, -1.6, -1.15)):                              # bowls on it, and jugs
        bowl([W / 2 - T - 0.15, 1.525, dz], 0.12, pick("wood", i, 1))
    jug([W / 2 - T - 0.17, 1.525, -0.65], P["steel"], 0.35)
    jug([W / 2 - T - 0.17, 1.525, -0.3], P["brick"], 0.3)
    barrel([W / 2 - T - 0.5, FL, 0.8], 0.38, 0.9)                              # a barrel and sacks of flour
    for x in (3.2, 3.9):
        sack([x, FL, D / 2 - T - 0.4], 0.33)
    ox, oz = W / 2 + 1.7, 1.0                                                  # the bread oven at the end
    brick_box([ox, 0.45, oz], [2.2, 0.9, 2.2])
    add.hemisphere([ox, 0.9, oz], 1.0, 6, P["brick"])
    add.mesh(add.make(add.prism, [[x, y] for x, y in arch_profile(0.9, 0.56, 0.46)], 0.5, P["black"], (ox, 0, oz + 0.8), (0, 0, 1)))
    add.ellipsoid([ox, 1.02, oz + 0.9], [0.2, 0.1, 0.12], 3, FLAME)
    add.sphere([ox, 0.98, oz + 0.85], 0.07, 3, P["flame_core"])
    add.mesh(add.difference(add.make(add.cylinder, [ox - 0.3, 1.75, oz - 0.2], [ox - 0.3, 2.3, oz - 0.2], 0.12, 10, P["brick"]),
                            add.make(add.cylinder, [ox - 0.3, 2.0, oz - 0.2], [ox - 0.3, 2.4, oz - 0.2], 0.07, 10, P["black"])))   # its flue, smoking
    add.sphere([ox - 0.25, 2.7, oz - 0.3], 0.3, 6, SMOKE)
    add.cylinder([ox + 1.25, 0.0, oz + 0.2], [ox + 0.95, 1.55, oz - 0.5], 0.025, 6, P["wood"])     # the peel
    add.mesh(add.move(add.rotateX(add.make(add.cuboid, [0, 0, 0], [0.3, 0.4, 0.02], P["wood_light"]), -0.4), [ox + 1.3, 0.2, oz + 0.35]))
    baker = add.stretch(person("stand", P["white"]), [LIFE] * 3, (0, 0, 0))
    add.mesh(add.move(add.rotateY(baker, add.pi), [ox, 0, oz + 2.3]))                        # the baker, at his oven
    for i in range(8):                                                         # firewood, stacked under the eaves
        for j in range(4):
            x, y = -W / 2 + 0.35 + i * 0.21 + (j % 2) * 0.1, 0.1 + j * 0.185
            add.cylinder([x, y, D / 2 + 0.2], [x, y, D / 2 + 0.72], 0.095, 7, pick("wood", i, j))
    add.cylinder([-3.8, 0.0, D / 2 + 1.7], [-3.8, 0.5, D / 2 + 1.7], 0.3, 12, P["trunk"])         # the chopping block
    add.cylinder([-3.8, 0.47, D / 2 + 1.7], [-3.47, 1.02, D / 2 + 1.52], 0.022, 6, P["wood"])     # the axe, its bit in the block
    add.mesh(add.make(add.prism, [[-0.06, 0.0], [0.08, 0.0], [0.1, 0.12], [-0.08, 0.1]], 0.03, P["steel"], (-3.8, 0.44, D / 2 + 1.7), (0, 0, 1)))
    barrel([0.3, 0, D / 2 + 0.6], 0.42, 1.0)                                  # the water barrel
    add.cylinder([0.3, 0.92, D / 2 + 0.6], [0.3, 0.95, D / 2 + 0.6], 0.36, 12, WATER)
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def storehouse(at, facing=0.0, W=8.5, D=4.6):
    """A storehouse against the curtain wall: a timber lean-to on posts
    with stone footings, a plank floor, board walls at the back and ends,
    a roof of wooden shingles on rafters, open to the yard; inside sacks
    of grain, barrels and crates.  Built open towards +z."""
    HF, HB = 3.2, 4.6                                                          # the roof's height at the front and the back
    add.push()
    plank_floor(-W / 2, W / 2, -D / 2, D / 2, 0.16, thick=0.05, width=0.3, length=2.8, along="x")
    add.cuboid([0, 0.055, 0], [W, 0.11, D], P["stone_dark"])
    xs = [-W / 2 + 0.15, -W / 6, W / 6, W / 2 - 0.15]
    for x in xs:
        for z, h in ((D / 2 - 0.15, HF), (-D / 2 + 0.15, HB)):
            add.cuboid([x, 0.1, z], [0.4, 0.2, 0.4], P["stone_dark"])
            add.cuboid([x, h / 2, z], [0.22, h, 0.22], P["wood_dark"])
    add.cuboid([0, HF - 0.1, D / 2 - 0.15], [W, 0.2, 0.24], P["wood_dark"])                    # the plates
    add.cuboid([0, HB - 0.1, -D / 2 + 0.15], [W, 0.2, 0.24], P["wood_dark"])
    for i in range(int(W / 0.3)):                                              # the back wall: boards
        add.cuboid([-W / 2 + (i + 0.5) * W / int(W / 0.3), HB / 2, -D / 2 + 0.04], [W / int(W / 0.3) - 0.02, HB, 0.08], shade_of("wood", i % 3))
    for sx in (-1, 1):                                                          # the ends: boards up to the roof
        n = int(D / 0.3)
        for i in range(n):
            z = -D / 2 + (i + 0.5) * D / n
            h = HB + (HF - HB) * (z + D / 2) / D
            add.cuboid([sx * (W / 2 - 0.04), h / 2, z], [0.08, h, D / n - 0.02], shade_of("wood", (i + 1) % 3))
    for x in [-W / 2 + 0.1 + i * (W - 0.2) / 7 for i in range(8)]:           # the rafters
        add.beam([x, HF + 0.05, D / 2 + 0.45], [x, HB + 0.05, -D / 2 - 0.05], 0.12, 0.14, P["wood_dark"])
    quad = [[-W / 2 - 0.3, HF + 0.12, D / 2 + 0.5], [W / 2 + 0.3, HF + 0.12, D / 2 + 0.5],
            [W / 2 + 0.3, HB + 0.12, -D / 2 - 0.05], [-W / 2 - 0.3, HB + 0.12, -D / 2 - 0.05]]
    add.mesh(slab(quad, 0.08, P["wood_dark"]))
    tile_face(*[[q[0], q[1] + 0.09, q[2]] for q in quad], size=(0.3, 0.26), colours="wood")
    for i in range(6):                                                         # the stores
        sack([-W / 2 + 0.7 + (i % 3) * 0.75, 0.16 + (0.45 if i >= 3 else 0), -D / 2 + 0.6 + (i % 2) * 0.1], 0.36)
    for x in (-0.9, 0.1, 1.1):
        barrel([x, 0.16, -D / 2 + 0.75], 0.45, 1.2)
    barrel([-0.4, 0.16, 0.8], 0.45, 1.2, upright=False)
    crate([2.0, 0.16, -D / 2 + 0.7], 0.9)
    crate([2.0, 1.06, -D / 2 + 0.7], 0.8)
    crate([3.1, 0.16, -D / 2 + 0.75], 0.8)
    crate([2.6, 0.16, 0.6], 0.7)
    sack([-2.8, 0.16, 1.2], 0.4)
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


def target(at, facing=0.0):
    """An archery butt: a round boss of bound straw painted with rings,
    on a wooden stand, a few arrows in it.  Its face towards +z."""
    add.push()
    c = [0, 1.25, 0]
    add.cylinder([0, c[1], -0.15], [0, c[1], 0.15], 0.6, k_(14), P["straw"])
    for i, (r, col) in enumerate(((0.52, "white"), (0.4, "black"), (0.28, "blue"), (0.16, "red"), (0.06, "gold"))):
        add.cylinder([0, c[1], 0.15 + 0.004 * i], [0, c[1], 0.156 + 0.004 * i], r, k_(14), P[col])
    for z in (-0.08, 0.08):                                                    # the bindings
        add.torus([0, c[1], z], 0.6, 0.025, k_(14), 5, P["rope"], axis=(0, 0, 1))
    for sx in (-1, 1):                                                          # the stand: two legs in front ...
        add.beam([sx * 0.55, 0.0, 0.3], [sx * 0.2, 1.3, -0.17], 0.09, 0.09, P["wood_dark"])
    add.beam([0.0, 0.0, -0.9], [0.0, 1.5, -0.17], 0.09, 0.09, P["wood_dark"])       # ... and one behind
    add.cuboid([0, 0.62, 0.08], [0.85, 0.08, 0.08], P["wood_dark"])
    for dx, dy, ax, ay in ((0.12, 0.08, 0.05, -0.03), (-0.2, -0.15, -0.06, 0.04), (0.05, -0.3, 0.02, 0.06)):
        tip = [dx, c[1] + dy, 0.05]                                            # arrows, stuck in
        end = [dx + ax * 6, c[1] + dy + ay * 6, 0.75]
        add.cylinder(tip, end, 0.01, 5, P["wood_light"])
        add.cuboid([end[0], end[1] + 0.02, end[2] - 0.06], [0.004, 0.035, 0.1], P["white"])
    add.mesh(add.move(add.rotateY(add.pop(), facing), at))


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
garden([-27.8, Y, -18], 7, 8)                                                            # off the path, under the palace windows
kitchen([-44.2, Y, -8.5], add.pi / 2)                                                  # the kitchen by the west wall
storehouse([46.2, Y, -5.2], -add.pi / 2)                                               # the stores against the east wall
for (tx, tz), (bx, bz) in (((46.2, 8.5), (37.0, 9.5)), ((46.2, 12.3), (37.5, 12.8))):     # archers at the butts
    target([tx, Y, tz], add.atan2(bx - tx, bz - tz))
    bowman([bx, Y, bz], add.atan2(tx - bx, tz - bz), "bow")
HOUSES = [((-11.5, -37.0), add.pi, True, False, ("sleep",)), ((-2.0, -35.2), add.pi, False, True, ("eat",)),   # log houses for
          ((-44.0, 8.5), add.pi / 2, True, False, ("eat", "sleep")), ((40.5, 17.5), -add.pi / 2, False, False, ("sleep",)),   # the folk:
          ((20.5, 25.0), -add.pi / 2, True, True, ("sleep",))]                                                 # hay lofts in three
for i, ((hx, hz), facing, loft, thatch, folk) in enumerate(HOUSES):
    assert any(abs(fx - hx) < 1e-6 and abs(fz - hz) < 1e-6 for fx, fz, r in FOOTPRINTS)
    log_house([hx, Y, hz], facing, loft=loft, thatch=thatch, seed=i + 1, folk=folk)
add.seed(21)
hens = []                                                                                # chickens round the cottage: on the
while len(hens) < 9:                                                                     # earth, clear of the houses and of each other
    cx, cz = -30 + add.uniform(-7, 6), 25 + add.uniform(-6, 7)
    if (not in_yard(cx, cz, 1.0) or paved(cx, cz) or on_path(cx, cz, 0.3)
            or any((cx - fx) ** 2 + (cz - fz) ** 2 < (r + 0.45) ** 2 for fx, fz, r in FOOTPRINTS)
            or any((cx - ox) ** 2 + (cz - oz) ** 2 < 0.8 ** 2 for ox, oz in hens)):
        continue
    hens.append((cx, cz))
for i, (cx, cz) in enumerate(hens):
    chicken([cx, Y, cz], add.uniform(0, 6.28), (P["white"], P["wood_light"], P["linen"])[i % 3], rooster=(i == 4))
for (x, z), kind in zip(((15, 8), (-15, 8), (40, 0), (-40, 0), (24, 40), (-18, 40)),
                       ("lime", "lime", "birch", "birch", "oak", "elm")):                # trees in the yard: limes by the
    assert in_yard(x, z, 2.8), (x, z)                                                   # square, birches, an oak, an elm
    forest_tree([x, Y - 0.1, z], {"lime": 7.0, "oak": 7.5, "birch": 9.0, "elm": 9.0}[kind], kind, int(x * 7 + z))
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
dog([-20, Y, 26], -1.0, P["trunk"])
ladder_on_wall(7, 0.62)
ladder_on_wall(3, 0.4)                                                                   # (clear of the kitchen)
standing_man([-5.6, Y, 21.5], -add.pi / 2, P["red"])                                     # people about the yard
standing_man([14, Y, 27], -2.0, P["blue"], hat=True)
standing_man([20, Y, 36], 2.6, P["leaf"])
add.seed(31)
for i in range(count(14)):                                          # gulls over the lake and the yard, each on its own
    a = i * 1.1 + add.uniform(-0.2, 0.2)                            # circle, height and turn, at its own beat of the wings
    rad, y = add.uniform(30, 85), G + add.uniform(5, 20)
    way = 1 if i % 3 else -1                                        # most wheel one way, some the other
    heading = add.atan2(-add.cos(a), -add.sin(a)) if way > 0 else add.atan2(add.cos(a), add.sin(a))
    beat = add.uniform(0, 2 * add.pi)                               # up, gliding, down ...
    gull([rad * add.cos(a), y, rad * add.sin(a)], heading, way * add.uniform(0.1, 0.5), add.uniform(-0.1, 0.2),
         0.2 + 0.4 * add.sin(beat), -0.35 + 0.3 * add.cos(beat), add.uniform(0.85, 1.15), add.uniform(0.15, 0.4))
flush("courtyard")
# the field of rye: a strip of ploughed earth sown in rows, the rye ripe and nodding in the wind, a scarecrow in it
FX, FZ = (RYE[0] + RYE[1]) / 2, (RYE[2] + RYE[3]) / 2
add.cuboid([FX, G + 0.03, FZ], [RYE[1] - RYE[0], 0.06, RYE[3] - RYE[2]], P["earth_dark"])
EAR = add.make(add.ellipsoid, [0, 0, 0], [0.02, 0.065, 0.02], 3, P["bread"])
n = 0
for i in range(int((RYE[1] - RYE[0]) / 0.32)):                     # rows 0.32 apart, a tuft of three stalks every 0.14
    for j in range(int((RYE[3] - RYE[2]) / 0.14)):
        x = RYE[0] + 0.16 + 0.32 * i + (hash2(i, j, 92) - 0.5) * 0.1
        z = RYE[2] + 0.07 + 0.14 * j + (hash2(i, j, 93) - 0.5) * 0.06
        if hash2(i, j, 91) > max(DENSITY, 0.25) or (x - FX) ** 2 + (z - FZ) ** 2 < 0.5 ** 2:
            continue
        for k in range(3):
            h = 0.95 + 0.25 * hash2(i, j, 94 + k)
            a = 2.1 * k + 6.28 * hash2(i, j, 97)
            lean = 0.06 + 0.08 * hash2(i, j, 98 + k)                      # all a little the same way, in the wind
            top = [x + 0.03 * add.cos(a) + lean, G + 0.06 + h, z + 0.03 * add.sin(a)]
            sheet([[x - 0.012 * add.sin(a), G + 0.05, z + 0.012 * add.cos(a)], [x + 0.012 * add.sin(a), G + 0.05, z - 0.012 * add.cos(a)],
                   top], P["straw"], 0.008, hinge=True)
            tilt = add.atan2(lean, h) + 0.25 + 0.3 * hash2(i, j, 101 + k)  # the ear nods
            add.mesh(add.move(add.rotateZ(EAR, -tilt), [top[0] + 0.05 * add.sin(tilt), top[1] + 0.05 * add.cos(tilt), top[2]]))
        n += 1
add.cylinder([FX, G, FZ], [FX, G + 2.2, FZ], 0.05, 8, P["wood_dark"])                     # the scarecrow: a pole,
add.cylinder([FX, G + 1.7, FZ - 0.75], [FX, G + 1.7, FZ + 0.75], 0.035, 6, P["wood_dark"])   # a crossbar,
for sz in (-1, 1):                                                                       # an old coat on it,
    add.cylinder([FX, G + 1.7, FZ + sz * 0.1], [FX, G + 1.66, FZ + sz * 0.62], 0.085, 8, P["wood_light"])
    add.cone([FX, G + 1.66, FZ + sz * 0.62], [FX, G + 1.55, FZ + sz * 0.8], 0.05, 5, P["straw"])   # straw out of the sleeves
add.cuboid([FX, G + 1.35, FZ], [0.26, 0.75, 0.5], P["wood_light"])
add.cuboid([FX, G + 1.05, FZ + 0.12], [0.27, 0.2, 0.18], P["brick"])                       # a patch
add.cone([FX, G + 0.98, FZ], [FX, G + 0.8, FZ], 0.12, 6, P["straw"])
add.sphere([FX, G + 2.02, FZ], 0.17, 8, P["straw"])                                        # a head of straw
add.cylinder([FX, G + 2.12, FZ], [FX, G + 2.15, FZ], 0.3, 12, P["wood"])                   # and a hat
add.cone([FX, G + 2.15, FZ], [FX, G + 2.42, FZ], 0.17, 12, P["wood"])
flush("the field of rye (%d tufts)" % n, clean=False)


def ship(at, forward, L=24.0, B=7.2, seed=0, crew=(), band=None, shields=False, gangway=None):
    """A great ship, a cog, moored: a deep round-bellied hull of strakes,
    tarred below the water, three wales along each side following the sheer
    and the ends of the deck beams showing through the planking, the top
    strake painted in ``band``; a deck with bulwarks, frames inside them and
    a cap rail; hawse holes and two anchors catted at the bow, a capstan, a
    hatch with a grating, barrels and coils of rope; a castle aft with a
    cabin and a door, a deck on it with a balustrade (``shields`` hung along
    it), lanterns at its corners and a flagstaff; a platform forward with a
    rail, a bowsprit; one tall mast with a crenellated fighting top, the yard
    with the sail furled on it and lashed, lifts and braces, shrouds set up
    with deadeyes on chainplates, with ratlines, the stays, a flag at the
    masthead; the rudder hung on iron straps, its tiller.  ``at`` is the
    middle of the ship at the waterline, ``forward`` the way the bow points
    (x, z); ``crew`` = (x, z, facing) of sailors on deck, in the ship's
    frame (x forward, z to port).  With ``gangway`` = (x, y): the bulwark
    opened on the starboard side about x, and a ramp from the gunwale down
    to a quay at height y, wide and gentle enough to lead a horse aboard --
    boards with cleats across, a rail each side."""
    band = band or P["red"]
    half = lambda t: max(0.16, (B / 2) * (1 - abs(t) ** 2.4) ** 0.55)                 # the half-breadth at the gunwale,
    sheer = lambda t: 1.5 + 0.9 * t * t + (0.3 * t if t > 0 else 0.0)                 # the gunwale's height (the deck),
    keel = lambda t: -2.1 + 2.4 * abs(t) ** 6                                          # and the keel's, rising to stem and stern
    xs = lambda t: t * L / 2 + (0.9 * t ** 3 if t > 0 else 0.4 * t ** 3)               # the stem raked forward
    tx = lambda x: add.clamp(x / (L / 2), -1.0, 1.0)

    def side(t, y):
        """How far out the hull's side is at station ``t``, height ``y``."""
        sh, k = sheer(t), keel(t)
        if not k < y < sh:
            return None
        sphi = ((sh - y) / (sh - k)) ** (1 / 0.55)
        return half(t) * add.sqrt(max(0.0, 1 - sphi * sphi))
    n = 31
    FRAC = (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.88, 0.94, 0.975, 0.993)     # down the side, evenly, finer at the bilge
    rings = []
    for i in range(n):                                                                 # each section: down the port side by
        t = -1 + 2.0 * i / (n - 1)                                                     # height, the keel, up the starboard side
        sh, k = sheer(t), keel(t)
        port = [[xs(t), sh - (sh - k) * f, side(t, sh - (sh - k) * f) if f > 0 else half(t)] for f in FRAC]
        rings.append(port + [[xs(t), k, 0.0]] + [[x, y, -z] for x, y, z in port[::-1]])
    add.push()
    add.loft(rings, P["wood"])
    hull = add.pop()

    def strake(q):                                                                     # tar below, planks above, a deck on top
        t = tx(q[0])
        if abs(q[2]) < 0.55 * half(t) and q[1] > sheer(t) - 0.3:
            return shade_of("wood_light", int(q[0] * 1.3) % 3)
        if q[1] < 0.15:
            return P["wood_dark"] if q[1] < -0.6 else P["black"]
        if q[1] > sheer(t) - 0.4:
            return band                                                                # the painted top strake
        return shade_of("wood", int((q[1] + 2.1) / 0.32) % 3)
    add.push()
    add.mesh(add.color_by(hull, strake))
    for yw in (0.3, 0.85, 1.35):                                                       # the wales, along the sheer
        for sg in (-1, 1):
            pts = []
            for i in range(41):
                t = -0.97 + 1.94 * i / 40
                y = yw + 0.45 * t * t
                w = side(t, y)
                if w is not None and w > 0.3:
                    pts.append([xs(t), y, sg * (w + 0.03)])
            add.polyline(pts, 0.08, 6, P["wood_dark"])
    for x in (-7.2, -4.8, -2.4, 0.0, 2.4, 4.8, 7.2):                                   # the ends of the deck beams, through the side
        t = tx(x)
        y = 1.1 + 0.45 * t * t
        w = side(t, y)
        for sg in (-1, 1):
            add.cuboid([xs(t), y, sg * (w + 0.1)], [0.26, 0.26, 0.34], P["wood_dark"])
    gap = []                                                                           # (where the gangway opens it)
    for i in range(n - 1):                                                             # the bulwarks, a cap rail on them,
        t0, t1 = -1 + 2.0 * i / (n - 1), -1 + 2.0 * (i + 1) / (n - 1)               # frames inside
        for sg in (-1, 1):
            a, b = [xs(t0), sheer(t0), sg * half(t0)], [xs(t1), sheer(t1), sg * half(t1)]
            if gangway and sg < 0 and abs((a[0] + b[0]) / 2 - gangway[0]) < 1.1:
                gap += [a[0], b[0]]
                continue
            quad = [a, b, [b[0], b[1] + 0.55, b[2]], [a[0], a[1] + 0.55, a[2]]]
            sheet(quad if sg < 0 else quad[::-1], band, 0.07)
            add.cuboid([(a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 0.58, (a[2] + b[2]) / 2], [abs(b[0] - a[0]) + 0.02, 0.06, 0.14], P["wood_dark"])
            if 2 < i < n - 4:
                add.cuboid([a[0], a[1] + 0.27, sg * (half(t0) - 0.12)], [0.1, 0.55, 0.12], P["wood_dark"])
    x0, x1 = -L / 2 + 1.0, -L / 2 + 6.4                                                # the castle aft: a cabin narrowing to
    z0, z1 = half(2 * x0 / L) - 0.3, half(2 * x1 / L) - 0.3                            # the stern, a deck over it with a rail
    ya, top = sheer(2 * x1 / L) - 0.1, sheer(2 * x0 / L) + 2.0
    add.mesh(solid([(x0, -z0), (x1, -z1), (x1, z1), (x0, z0)], ya, top, shade_of("wood", 1)))
    add.mesh(solid([(x0 - 0.2, -z0 - 0.15), (x1 + 0.3, -z1 - 0.15), (x1 + 0.3, z1 + 0.15), (x0 - 0.2, z0 + 0.15)], top, top + 0.12, P["wood_dark"]))
    add.cuboid([x1 + 0.04, ya + 1.0, 0], [0.08, 1.8, 0.9], P["wood_dark"])            # its door, on iron straps
    for y in (ya + 0.45, ya + 1.55):
        add.cuboid([x1 + 0.09, y, 0.1], [0.02, 0.06, 0.7], P["iron"])
    for zz in (1.2, 1.8):                                                              # a ladder up to it, beside the door
        add.beam([x1 + 0.9, ya, zz], [x1 + 0.2, top + 0.1, zz], 0.08, 0.08, P["wood"])
    for k in range(1, 7):
        u = k / 7.0
        add.cylinder([x1 + 0.9 - 0.7 * u, ya + (top + 0.1 - ya) * u, 1.2], [x1 + 0.9 - 0.7 * u, ya + (top + 0.1 - ya) * u, 1.8], 0.03, 5, P["wood"])
    for sg in (-1, 1):
        for i in range(11):
            u = i / 10.0
            x, z = x0 + (x1 - x0) * u, sg * (z0 + (z1 - z0) * u)
            add.cylinder([x, top + 0.12, z], [x, top + 0.75, z], 0.04, 6, P["wood_dark"])
        add.cylinder([x0, top + 0.78, sg * z0], [x1, top + 0.78, sg * z1], 0.05, 6, P["wood"])
        add.cylinder([x0, top + 0.12, sg * z0], [x1, top + 0.12, sg * z1], 0.04, 6, P["wood"])
        if shields:                                                                    # shields hung on the rail
            for i in range(5):
                u = (i + 0.5) / 5.0
                x, z = x0 + (x1 - x0) * u, sg * (z0 + (z1 - z0) * u + 0.1)
                c = (P["red"], P["gold"], P["blue"])[i % 3]
                add.cylinder([x, top + 0.45, z], [x, top + 0.45, z + sg * 0.06], 0.33, 12, c)
                add.cuboid([x, top + 0.45, z + sg * 0.065], [0.08, 0.5, 0.02], P["white"] if c is not P["gold"] else P["red"])
                add.cuboid([x, top + 0.5, z + sg * 0.065], [0.4, 0.08, 0.02], P["white"] if c is not P["gold"] else P["red"])
        lx, lz = x0 + 0.1, sg * (z0 - 0.1)                                             # lanterns on the corners
        add.cylinder([lx, top + 0.12, lz], [lx, top + 1.5, lz], 0.05, 6, P["iron"])
        add.cuboid([lx, top + 1.65, lz], [0.28, 0.36, 0.28], P["iron"])
        add.sphere([lx, top + 1.65, lz], 0.1, 6, FLAME)
        add.cone([lx, top + 1.83, lz], [lx, top + 2.0, lz], 0.18, 8, P["iron"])
    add.cylinder([x0 + 0.3, top + 0.12, 0], [x0 + 0.3, top + 3.6, 0], 0.07, 8, P["wood_dark"])   # the flagstaff at the stern
    yf = sheer(0.8)                                                                    # the platform forward, narrowing, railed
    fore = [(L / 2 - 5.2, -half(0.6) + 0.3), (L / 2 - 5.2, half(0.6) - 0.3), (L / 2 - 1.2, half(0.9) - 0.25), (L / 2 - 1.2, -half(0.9) + 0.25)]
    add.mesh(solid(fore, yf + 1.1, yf + 1.25, P["wood_dark"]))
    for sg in (-1, 1):
        add.cuboid([L / 2 - 5.1, yf + 0.6, sg * (half(0.6) - 0.5)], [0.2, 1.2, 0.2], P["wood_dark"])
        (xa_, za_), (xb_, zb_) = fore[0 if sg < 0 else 1], fore[3 if sg < 0 else 2]
        for i in range(7):
            u = i / 6.0
            add.cylinder([xa_ + (xb_ - xa_) * u, yf + 1.25, za_ + (zb_ - za_) * u], [xa_ + (xb_ - xa_) * u, yf + 1.85, za_ + (zb_ - za_) * u],
                         0.035, 6, P["wood_dark"])
        add.cylinder([xa_, yf + 1.88, za_], [xb_, yf + 1.88, zb_], 0.045, 6, P["wood"])
    add.cylinder([L / 2 - 0.2, sheer(1.0) + 0.3, 0], [L / 2 + 5.0, sheer(1.0) + 2.6, 0], 0.18, 8, P["wood_dark"])   # the bowsprit
    MX, TOP = 1.2, 19.0                                                                # the mast, the fighting top, the yard
    add.cylinder([MX, sheer(0.1) - 0.5, 0], [MX, TOP + 1.2, 0], 0.3, 12, P["wood"])
    add.cylinder([MX, TOP - 1.2, 0], [MX, TOP - 0.6, 0], 0.85, 12, P["wood_dark"])
    add.pipe([MX, TOP - 0.6, 0], [MX, TOP + 0.1, 0], 0.85, 0.75, 12, P["wood_dark"])
    for i in range(8):
        a = 2 * add.pi * i / 8
        add.cuboid([MX + 0.8 * add.cos(a), TOP + 0.22, 0.8 * add.sin(a)], [0.2, 0.24, 0.2], P["wood_dark"])
    add.cylinder([MX, TOP - 3.2, -7.0], [MX, TOP - 3.2, 7.0], 0.16, 8, P["wood_dark"])
    add.cylinder([MX + 0.3, TOP - 3.45, -6.2], [MX + 0.3, TOP - 3.45, 6.2], 0.38, 10, P["linen"])       # the sail, furled
    for i in range(6):                                                                 # and lashed to the yard
        z = -5.5 + i * 2.2
        add.torus([MX + 0.3, TOP - 3.45, z], 0.4, 0.03, 10, 4, P["rope"], axis=(0, 0, 1))
    for sg in (-1, 1):
        add.cylinder([MX, TOP + 0.3, 0], [MX, TOP - 3.2, sg * 6.8], 0.025, 4, P["rope"])                # the lifts,
        add.cylinder([MX, TOP - 3.2, sg * 6.8], [x0 + 0.4, top + 0.8, sg * (z0 - 0.1)], 0.025, 4, P["rope"])   # the braces
    for sg in (-1, 1):                                                                 # the shrouds, set up with deadeyes on
        feet = [[MX - 1.6 + 1.1 * k, sheer(0.05) + 0.62, sg * (half(0.05) + 0.1)] for k in range(4)]   # chainplates, with ratlines
        for f in feet:
            add.cylinder(f, [MX, TOP - 1.3, sg * 0.3], 0.03, 4, P["rope"])
            add.cylinder([f[0], f[1] - 0.12, f[2]], [f[0], f[1] + 0.02, f[2]], 0.12, 8, P["wood_dark"])
            add.cuboid([f[0], f[1] - 0.6, f[2] - sg * 0.02], [0.06, 1.0, 0.04], P["iron"])
        for k in range(1, 12):
            y = feet[0][1] + (TOP - 1.3 - feet[0][1]) * k / 12.0
            u = k / 12.0
            add.cylinder([feet[0][0] + (MX - feet[0][0]) * u, y, sg * (feet[0][2] * sg + (0.3 - feet[0][2] * sg) * u)],
                         [feet[3][0] + (MX - feet[3][0]) * u, y, sg * (feet[3][2] * sg + (0.3 - feet[3][2] * sg) * u)], 0.015, 3, P["rope"])
    add.cylinder([MX, TOP + 0.4, 0], [L / 2 + 4.8, sheer(1.0) + 2.5, 0], 0.035, 4, P["rope"])           # the stays
    add.cylinder([MX, TOP + 0.4, 0], [x0 + 0.3, top + 0.8, 0], 0.035, 4, P["rope"])
    add.cuboid([-L / 2 - 0.35, 0.2, 0], [0.7, 3.4, 0.22], P["wood_dark"])             # the rudder on the sternpost,
    for y in (-0.8, 0.4, 1.4):
        add.cuboid([-L / 2 - 0.2, y, 0], [1.0, 0.1, 0.3], P["iron"])
    add.cylinder([-L / 2 - 0.5, 1.9, 0], [-L / 2 + 1.6, 2.6, 0], 0.07, 6, P["wood_dark"])   # its tiller through the stern
    for sg in (-1, 1):                                                                 # the anchors, catted at the bow, the
        t = 0.9                                                                        # cables into the hawse holes
        ax, ay = xs(t) - 0.4, sheer(t) - 1.7
        az = sg * (half(t) + 0.3)
        add.cylinder([ax, ay, az], [ax, ay + 1.6, az], 0.07, 6, P["iron"])
        add.polyline([[ax - 0.55, ay + 0.45, az], [ax - 0.3, ay + 0.08, az], [ax, ay, az], [ax + 0.3, ay + 0.08, az], [ax + 0.55, ay + 0.45, az]],
                     0.06, 6, P["iron"], smooth=1)
        add.cylinder([ax - 0.4, ay + 1.45, az], [ax + 0.4, ay + 1.45, az], 0.06, 6, P["wood_dark"])
        add.cylinder([ax, ay + 1.6, az], [ax - 0.1, sheer(t) + 0.55, az - sg * 0.2], 0.03, 4, P["rope"])
        th = 0.93
        yh = sheer(th) - 0.55
        wh = side(th, yh) or 0.4
        add.cylinder([xs(th) - 0.2, yh, sg * (wh + 0.02)], [xs(th) - 0.2, yh, sg * (wh + 0.05)], 0.16, 10, P["black"])
    yd = sheer(0.2)                                                                    # on deck: a hatch with a grating,
    add.cuboid([4.0, yd + 0.12, 0], [2.4, 0.24, 2.0], P["wood_dark"])                   # a capstan, barrels, coils of rope
    for i in range(5):
        add.cuboid([4.0, yd + 0.25, -0.8 + 0.4 * i], [2.2, 0.04, 0.12], P["wood"])
    for i in range(5):
        add.cuboid([3.1 + 0.45 * i, yd + 0.26, 0], [0.12, 0.04, 1.9], P["wood"])
    cx = 7.4
    lathe([[0.0, 0], [0.45, 0], [0.4, 0.1], [0.32, 0.2], [0.3, 0.75], [0.42, 0.85], [0.42, 1.05], [0.0, 1.05]], [cx, sheer(tx(cx)), 0], 12, P["wood"])
    for a in range(4):
        add.cylinder([cx - 0.9 * add.cos(a * add.pi / 4), sheer(tx(cx)) + 0.95, -0.9 * add.sin(a * add.pi / 4)],
                     [cx + 0.9 * add.cos(a * add.pi / 4), sheer(tx(cx)) + 0.95, 0.9 * add.sin(a * add.pi / 4)], 0.04, 6, P["wood_dark"])
    for k, (bx, bz) in enumerate(((5.8, 1.9), (5.8, 1.1), (6.5, 1.5), (-1.6, -2.0))):
        barrel([bx, sheer(tx(bx)), bz], 0.4, 1.0)
    for cx_, cz_ in ((-2.5, -1.8), (2.6, 2.2)):
        add.torus([cx_, sheer(tx(cx_)) + 0.08, cz_], 0.45, 0.08, 12, 6, P["rope"])
        add.torus([cx_, sheer(tx(cx_)) + 0.22, cz_], 0.38, 0.08, 12, 6, P["rope"])
    if gangway:                                                                        # the gangway: a post at each end of
        gx, quay = gangway                                                             # the opening, the ramp resting on the
        for e in (min(gap), max(gap)):                                                 # gunwale and reaching down to the quay
            add.cuboid([e, sheer(tx(e)) + 0.33, -(half(tx(e)) - 0.1)], [0.16, 0.66, 0.16], P["wood_dark"])   # at 1 in 4
        rim, deck = -half(tx(gx)), sheer(tx(gx))
        reach = (deck - quay) / 0.25
        A, B = [gx, deck + 0.04 + 0.35 * 0.25, rim + 0.35], [gx, quay + 0.04, rim - reach]
        add.beam(A, B, 1.8, 0.08, shade_of("wood_light", 1))
        span = vlen(vsub(B, A))
        for c in range(1, int(span / 0.35)):                                           # cleats for the hooves
            p = [A[j] + (B[j] - A[j]) * c * 0.35 / span for j in range(3)]
            add.beam([gx - 0.8, p[1] + 0.065, p[2]], [gx + 0.8, p[1] + 0.065, p[2]], 0.06, 0.05, P["wood"])
        for sx in (-0.84, 0.84):                                                       # the rails
            tops = []
            for f in (0.12, 0.88):
                p = [A[j] + (B[j] - A[j]) * f for j in range(3)]
                add.cylinder([gx + sx, p[1] + 0.03, p[2]], [gx + sx, p[1] + 0.95, p[2]], 0.04, 6, P["wood_dark"])
                tops.append([gx + sx, p[1] + 0.95, p[2]])
            add.cylinder(tops[0], tops[1], 0.035, 6, P["wood"])
    for cx_, cz_, cf in crew:                                                          # sailors about the deck
        figure([cx_, sheer(tx(cx_)), cz_], cf, person("stand", (P["blue"], P["linen"], P["red"])[int(abs(cx_) * 3) % 3], hat=(cz_ > 0),
                                                      hair=(P["wood_dark"], P["black"], P["straw"])[int(abs(cz_) * 5) % 3]))
    M = add.pop()
    fx, fz = forward
    fl = add.sqrt(fx * fx + fz * fz)
    xa = [fx / fl, 0, fz / fl]
    za = [-xa[2], 0, xa[0]]                                                            # x cross y: a right-handed frame
    add.mesh(placed(M, at, xa, [0, 1, 0], za))
    flag([at[0] + MX * xa[0], at[1] + TOP + 1.1, at[2] + MX * xa[2]], 2.2, 1.3, add.pi * 0.3, phase=seed * 0.7)   # in the castle's wind
    flag([at[0] + (x0 + 0.3) * xa[0], at[1] + top + 3.5, at[2] + (x0 + 0.3) * xa[2]], 1.6, 1.0, add.pi * 0.3, phase=seed * 0.7 + 0.4)
    return lambda x, y, z: [at[0] + x * xa[0] + z * za[0], at[1] + y, at[2] + x * xa[2] + z * za[2]]


def rowboat(at, heading, oars=True):
    """A rowing boat afloat, ``at`` the middle of it at the waterline,
    ``heading`` the way its bow points (radians, as rotateY): an open hull
    of strakes a hand thick, riding high and dry inside, with a pointed bow
    and a transom, floorboards, two thwarts and a seat in the stern, a pair
    of oars shipped along the thwarts, a ring in the stem for the rope."""
    L, B = 4.6, 1.5
    half = lambda t: max(0.05, (B / 2) * (1 - abs(t) ** 2.2) ** 0.6) if t > 0 else max(0.34, (B / 2) * (1 - abs(t) ** 3) ** 0.6)
    sheer = lambda t: 0.55 + 0.16 * t * t
    keel = lambda t: -0.12 + 0.3 * abs(t) ** 4
    rings = []
    for i in range(13):
        t = -1 + i / 6.0
        h, sh, k = half(t), sheer(t), keel(t)
        outer = [[t * L / 2, sh - (sh - k) * max(0.0, add.sin(add.pi * j / 9)) ** 0.6, h * add.cos(add.pi * j / 9)] for j in range(10)]
        hi, ki = max(0.0, h - 0.05), k + 0.14
        inner = [[t * L / 2, sh - (sh - ki) * max(0.0, add.sin(add.pi * j / 9)) ** 0.6, hi * add.cos(add.pi * j / 9)] for j in range(9, -1, -1)]
        rings.append(outer + inner)
    add.push()
    add.loft(rings, P["wood"], caps=False)
    for ring, sg in ((rings[0], -1), (rings[-1], 1)):                                  # the transom and the stem close the ends
        cap = ring[:10]
        n = vcross(vsub(cap[1], cap[0]), vsub(cap[2], cap[0]))
        add.polygon(cap if n[0] * sg > 0 else cap[::-1], P["wood_dark"])
    hull = add.pop()
    add.push()
    add.mesh(add.color_by(hull, lambda q: P["wood_dark"] if q[1] < 0.02 else shade_of("wood", int((q[1] + 0.3) / 0.12) % 3)))
    add.cuboid([0, keel(0) + 0.155, 0], [3.2, 0.03, 0.6], shade_of("wood_light", 0))    # the floorboards
    for x in (-0.3, 0.6):                                                              # the thwarts
        t = x / (L / 2)
        add.cuboid([x, sheer(t) - 0.12, 0], [0.26, 0.05, 2 * half(t) - 0.12], P["wood_light"])
    t = -1.75 / (L / 2)
    add.cuboid([-1.75, sheer(t) - 0.12, 0], [0.5, 0.05, 2 * half(t) - 0.12], P["wood_light"])
    if oars:
        for sg in (-1, 1):
            add.cylinder([-1.4, sheer(0) - 0.065, sg * 0.36], [1.5, sheer(0) - 0.065, sg * 0.3], 0.03, 6, P["wood_light"])
            add.cuboid([1.35, sheer(0) - 0.065, sg * 0.31], [0.55, 0.02, 0.13], P["wood_light"])
    add.torus([L / 2 - 0.02, sheer(1) - 0.08, 0], 0.05, 0.012, 8, 4, P["iron"], axis=(0, 0, 1))
    M = add.pop()
    add.mesh(add.move(add.rotateY(M, heading), at))


# the harbour: a broad wharf on piles running straight out from the end of the road into water dredged deep, two
# great ships moored along it, the king's and a merchant's, a crane, the cargo; rowing boats pulled up all round the
# island, tied to stakes on the shore -- the guests came in them.  The wharf is built along +x (u, out from the
# centre of the island) with v across, then turned to DOCK_A
def dock_pt(u, v, y):
    """The world point ``u`` out along the wharf, ``v`` across it, at height ``y``."""
    return [u * DOCK_C - v * DOCK_S, y, u * DOCK_S + v * DOCK_C]


U_SHORE = next(u * 0.25 for u in range(int(DOCK_U0 * 4), 600) if ground(*[dock_pt(u * 0.25, 0, 0)[k] for k in (0, 2)]) < WATER_Y - 0.1)
KING_U, GANG_X = DOCK_U1 - 14.5, 4.45                                                        # the king's ship, its gangway
POSTS = [(u, sg) for sg in (-1, 1) for u in range(int(U_SHORE + 5), int(DOCK_U1), 6)         # bollards on the edges, but
         if not (sg > 0 and abs(u - KING_U - GANG_X) < 1.6)]                                 # where the ramp comes down
add.push()
add.cuboid([(DOCK_U0 - 1.0 + U_SHORE + 1.5) / 2, (DOCK_Y - 0.23 - 1.5) / 2, 0], [U_SHORE + 1.5 - DOCK_U0 + 1.0, DOCK_Y - 0.23 + 1.5, 2 * DOCK_W + 0.6],
           P["stone_dark"])                                                                  # the abutment of stone on the shore
rows = [U_SHORE + 1.2 + 3.0 * k for k in range(int((DOCK_U1 - U_SHORE - 1.2) / 3.0) + 1)]
for k, u in enumerate(rows):                                                                 # piles in rows, a cap beam on each
    for v in (-DOCK_W + 0.3, -1.3, 1.3, DOCK_W - 0.3):
        x, _, z = dock_pt(u, v, 0)
        add.cylinder([u, ground(x, z) - 0.4, v], [u, DOCK_Y - 0.44, v], 0.18, 10, pick("wood_dark", k, v))
    add.cuboid([u, DOCK_Y - 0.33, 0], [0.34, 0.24, 2 * DOCK_W + 0.3], P["wood_dark"])
    if k % 2 and u < DOCK_U1 - 8:                                                            # braces under the deep part
        for v0 in (-DOCK_W + 0.3, 1.3):
            add.beam([u, DOCK_Y - 0.5, v0], [u, WATER_Y - 1.2, v0 + 2.6], 0.12, 0.14, P["wood_dark"])
for v in (-3.6, -1.8, 0.0, 1.8, 3.6):                                                        # stringers along
    add.cuboid([(DOCK_U0 + DOCK_U1) / 2, DOCK_Y - 0.13, v], [DOCK_U1 - DOCK_U0, 0.2, 0.18], P["wood"])
n = int((DOCK_U1 - DOCK_U0) / 0.3)
for i in range(n):                                                                           # the deck: planks across, with gaps,
    pitch = (DOCK_U1 - DOCK_U0) / n                                                          # from the end of the road
    u = DOCK_U0 + (i + 0.5) * pitch
    add.cuboid([u, DOCK_Y - 0.03, (hash2(i, 3, 17) - 0.5) * 0.06], [pitch - 0.02, 0.06, 2 * DOCK_W - 0.02 * hash2(i, 4, 17)], pick("wood", i, 13))
for sg in (-1, 1):                                                                           # fender logs along the sides,
    add.cylinder([U_SHORE, DOCK_Y - 0.28, sg * (DOCK_W + 0.12)], [DOCK_U1 + 0.1, DOCK_Y - 0.28, sg * (DOCK_W + 0.12)], 0.15, 10, P["wood_dark"])
    for u in (u for u, side in POSTS if side == sg):                                         # the bollards
        add.cylinder([u, DOCK_Y, sg * (DOCK_W - 0.35)], [u, DOCK_Y + 0.55, sg * (DOCK_W - 0.35)], 0.2, 12, P["wood_dark"])
        add.cylinder([u, DOCK_Y + 0.55, sg * (DOCK_W - 0.35)], [u, DOCK_Y + 0.62, sg * (DOCK_W - 0.35)], 0.26, 12, P["wood_dark"])
for i in range(8):                                                                           # a ladder down at the end
    y = DOCK_Y - 0.3 - i * 0.36
    add.cylinder([DOCK_U1 + 0.12, y, 1.9], [DOCK_U1 + 0.12, y, 2.5], 0.03, 6, P["wood_dark"])
for v in (1.9, 2.5):
    add.cylinder([DOCK_U1 + 0.12, DOCK_Y, v], [DOCK_U1 + 0.12, WATER_Y - 1.4, v], 0.05, 6, P["wood_dark"])
CU = DOCK_U1 - 9.0                                                                           # the crane: a post, a jib out over
add.cylinder([CU, DOCK_Y, -2.4], [CU, DOCK_Y + 6.5, -2.4], 0.25, 12, P["wood_dark"])        # the merchant ship, a rope and a
add.cuboid([CU, DOCK_Y + 0.2, -2.4], [1.2, 0.4, 1.2], P["wood_dark"])                       # sling of barrels
add.beam([CU, DOCK_Y + 2.0, -2.4], [CU, DOCK_Y + 6.8, -7.8], 0.2, 0.22, P["wood_dark"])
add.beam([CU, DOCK_Y + 6.3, -2.4], [CU, DOCK_Y + 6.8, -7.6], 0.1, 0.1, P["wood_dark"])
add.cylinder([CU, DOCK_Y + 6.75, -7.7], [CU, DOCK_Y + 4.6, -7.7], 0.025, 4, P["rope"])
for k, (du, dv) in enumerate(((-0.3, 0.0), (0.3, 0.1), (0.0, 0.45))):
    barrel([CU + du, DOCK_Y + 3.4, -7.7 + dv], 0.35, 0.9)
add.torus([CU, DOCK_Y + 4.55, -7.6], 0.5, 0.03, 12, 4, P["rope"])
add.cylinder([CU, DOCK_Y + 0.9, -2.1], [CU, DOCK_Y + 6.6, -7.6], 0.02, 4, P["rope"])       # the hauling line
for k, (u, v) in enumerate(((DOCK_U1 - 14.0, -2.6), (DOCK_U1 - 13.1, -2.8), (DOCK_U1 - 13.6, -1.9), (DOCK_U1 - 20.0, 2.4),
                            (DOCK_U1 - 19.1, 2.2))):                                         # cargo waiting on the wharf
    barrel([u, DOCK_Y, v], 0.4, 1.0)
for k, (u, v) in enumerate(((DOCK_U1 - 23.5, -2.5), (DOCK_U1 - 23.5, -1.6), (DOCK_U1 - 26.0, 2.6))):
    crate([u, DOCK_Y, v], 0.85)
crate([DOCK_U1 - 23.5, DOCK_Y + 0.85, -2.05], 0.75)
for k, (u, v) in enumerate(((DOCK_U1 - 30.0, -2.8), (DOCK_U1 - 30.7, -2.5), (DOCK_U1 - 30.3, -1.9))):
    sack([u, DOCK_Y, v], 0.36)
for u in (U_SHORE + 3.0, DOCK_U1 - 1.0):                                                     # lanterns on posts
    add.cylinder([u, DOCK_Y, -DOCK_W + 0.4], [u, DOCK_Y + 2.8, -DOCK_W + 0.4], 0.08, 8, P["wood_dark"])
    add.cuboid([u, DOCK_Y + 3.0, -DOCK_W + 0.4], [0.3, 0.4, 0.3], P["iron"])
    add.sphere([u, DOCK_Y + 3.0, -DOCK_W + 0.4], 0.12, 6, FLAME)
add.mesh(add.rotateY(add.pop(), -DOCK_A))
# the ships, moored along the wharf with bow and stern lines to the bollards, fenders between; the king's ship with
# its gangway open and a ramp down onto the wharf
SHIPS = [((KING_U, DOCK_W + 0.3 + 3.6, 1), 1), ((DOCK_U1 - 16.0, -(DOCK_W + 0.3 + 3.6), -1), 2)]
for (u, v, way), seed in SHIPS:
    ship(dock_pt(u, v, WATER_Y), (way * DOCK_C, way * DOCK_S), seed=seed, band=P["red"] if seed == 1 else P["blue"], shields=seed == 1,
         gangway=(GANG_X, DOCK_Y - WATER_Y) if seed == 1 else None,
         crew=((3.0, 1.2, 0.6), (-3.5, -1.0, 2.5), (-9.0, 0.4, 1.6)) if seed == 1 else ((5.0, 0.8, 1.0), (-2.0, -1.4, 4.0)))
    sg = 1 if v > 0 else -1
    for du in (-11.0, 11.5):                                                          # the lines
        post = min((p for p, side in POSTS if side == sg), key=lambda p: abs(p - u - du))                            # to the nearest
        b = dock_pt(post, sg * (DOCK_W - 0.35), DOCK_Y + 0.5)                                                               # bollard
        h = dock_pt(u + du * 0.85, v - sg * 2.2, WATER_Y + 2.7)
        add.polyline([h, [(h[0] + b[0]) / 2, (h[1] + b[1]) / 2 - 0.35, (h[2] + b[2]) / 2], b], 0.04, 6, P["rope"], smooth=1)
    for du in (-6.0, 0.0, 6.0):                                                       # fenders: bundles of rope
        c = dock_pt(u + du, sg * (DOCK_W + 0.3), WATER_Y + 0.9)
        add.mesh(add.move(add.stretch(add.make(add.sphere, [0, 0, 0], 0.3, 8, P["rope"]), [1.0, 1.6, 1.0], (0, 0, 0)), c))
# the rowing boats: one at the wharf's ladder, the rest all round the island by the shore, each tied to a stake
BOATS = [(dock_pt(DOCK_U1 + 1.4, 3.6, 0), DOCK_A + add.pi / 2 + 0.25, None)]
for deg in BOAT_DEGS:
    a = deg * add.pi / 180
    r = shore_r(a) + 1.9
    head = a + add.pi / 2 + (0.5 if deg % 2 else -0.4)                                    # along the shore, the bow turned in
    BOATS.append(([r * add.cos(a), 0, r * add.sin(a)], head, [(shore_r(a) - 1.8) * add.cos(a), (shore_r(a) - 1.8) * add.sin(a)]))
for (bx, _, bz), head, stake in BOATS:
    rowboat([bx, WATER_Y, bz], add.atan2(-add.sin(head), add.cos(head)), oars=True)
    bow = [bx + 2.28 * add.cos(head), WATER_Y + 0.63, bz + 2.28 * add.sin(head)]
    if stake is None:                                                                     # tied to the ladder
        tie = dock_pt(DOCK_U1 + 0.15, 2.5, DOCK_Y - 0.4)
    else:                                                                                 # or to a stake on the shore
        sy = ground(*stake)
        add.cylinder([stake[0], sy - 0.3, stake[1]], [stake[0], sy + 0.7, stake[1]], 0.06, 8, P["wood_dark"])
        tie = [stake[0], sy + 0.55, stake[1]]
    add.polyline([bow, [(bow[0] + tie[0]) / 2, min(bow[1], tie[1]) - 0.25, (bow[2] + tie[2]) / 2], tie], 0.025, 5, P["rope"], smooth=1)
flush("the harbour, the ships and the boats")


# fishermen: with so many fish in the lake, two on the wharf and one on the shore
def creel(at, fish_n=3):
    """A wicker basket with a rope handle and the catch in it."""
    lathe([[0.0, 0.0], [0.2, 0.0], [0.26, 0.12], [0.27, 0.3], [0.24, 0.3], [0.23, 0.14], [0.0, 0.05]], at, k_(10), P["straw"])
    for y in (0.1, 0.2):
        add.torus([at[0], at[1] + y, at[2]], 0.255, 0.012, k_(10), 4, P["wood_light"])
    add.arch([at[0] - 0.24, at[1] + 0.3, at[2]], [at[0] + 0.24, at[1] + 0.3, at[2]], 0.2, 0.015, P["rope"], 8, 5)
    for i in range(fish_n):
        f = add.rotateX(add.make(fish, [0, 0, 0], 0.0, (P["steel"], P["gold"], P["slate"])[i % 3], 0.22), add.pi / 2)
        add.mesh(add.move(add.rotateY(f, 1.3 * i), [at[0] + 0.05 * (i - 1), at[1] + 0.12 + 0.05 * i, at[2]]))


def fisherman(at, facing=0.0, pose="sit", tunic=None, hat=False, seat=0.53, rod=3.8):
    """A man fishing: sitting (on ``at``, a seat ``seat`` above where his
    feet rest) or standing, both hands on a rod that rises over the water
    in front of him; the line hangs from its tip to a red and white float
    on the lake."""
    sit = pose == "sit"
    d = [0.0, add.sin(0.45), add.cos(0.45)] if sit else [0.0, 0.5, 0.866]
    R = [-0.1, 0.32, 0.3] if sit else [-0.1, 1.05, 0.22]
    L = _at(R, d, 0.2 if sit else 0.18)
    M = person(pose, tunic, hat, seat=seat, arms=((R, d, [-1, -0.5, -0.3]), (L, d, [1, -0.5, -0.2])))
    tip = _at(R, d, rod / LIFE)
    M.extend(add.make(add.polyline, [_at(R, d, -0.25), _at(R, d, 1.4), tip], ramp((0.022, 0.014, 0.006)), 6, P["wood"]))
    c, s_ = add.cos(facing), add.sin(facing)

    def world(p):                                                       # the figure's frame -> the castle's
        x, y, z = p[0] * LIFE, p[1] * LIFE, p[2] * LIFE
        return [at[0] + x * c + z * s_, at[1] + y, at[2] + z * c - x * s_]
    add.mesh(add.move(add.rotateY(add.stretch(M, [LIFE] * 3, (0, 0, 0)), facing), at))
    t = world(tip)
    out = [s_, 0.0, c]                                                   # his forward direction, level
    bob = [t[0] + out[0] * 0.5, ripple(t[0], t[2]) + 0.02, t[2] + out[2] * 0.5]
    add.cylinder(t, bob, 0.005, 4, P["white"])
    add.sphere(bob, 0.05, 3, P["red"])
    add.sphere([bob[0], bob[1] + 0.035, bob[2]], 0.03, 2, P["white"])


OUT = add.atan2(DOCK_C, DOCK_S)                                                                   # facing out from the wharf's end
fisherman(dock_pt(DOCK_U1 - 0.1, 0.9, DOCK_Y), OUT, "sit", P["blue"], hat=True)                  # at the end of the wharf,
creel(dock_pt(DOCK_U1 - 0.35, 0.15, DOCK_Y))                                                      # his legs over the edge
fisherman(dock_pt(DOCK_U1 - 0.3, -1.9, DOCK_Y), OUT, "stand", P["leaf"])                          # and beside him, standing
creel(dock_pt(DOCK_U1 - 0.9, -2.6, DOCK_Y), 2)
FA = add.pi / 3                                                          # and on a rock on the gentle shore to the south-east
fx, fz = 87.4 * add.cos(FA), 87.4 * add.sin(FA)
rock_y = ground(fx, fz)
add.mesh(add.move(add.stretch(add.make(add.sphere, [0, 0, 0], 0.5, 6, P["rock"]), [1.2, 0.9, 1.0], (0, 0, 0)), [fx, rock_y + 0.05, fz]))
feet = [fx + 0.55 * add.cos(FA), fz + 0.55 * add.sin(FA)]
fisherman([fx, rock_y + 0.5, fz], add.atan2(add.cos(FA), add.sin(FA)), "sit", P["red"], seat=rock_y + 0.5 - ground(*feet))
creel([fx + 0.8 * add.sin(FA), ground(fx + 0.8 * add.sin(FA), fz - 0.8 * add.cos(FA)), fz - 0.8 * add.cos(FA)])
flush("fishermen")

# torches along the inside of the wall, flags on the towers, guards on duty:
# knights in plate, archers and crossbowmen in mail
for k in range(8):
    a, b = CORNERS[k], CORNERS[(k + 1) % 8]
    L, d, n = outward(a, b)
    for t in (0.25, 0.5, 0.75):
        if k == 1 and abs(t - 0.5) < 0.3:
            continue
        p = [a[0] + d[0] * L * t - n[0] * 1.45, G + 3.5, a[2] + d[2] * L * t - n[2] * 1.45]
        torch(p, add.atan2(-n[0], -n[2]))
for z in (PORT_Z + 1.0, PORT_Z - 1.0):                 # four in the gate passage, one on either side of it before the
    for s in (-1, 1):                                  # portcullis and one behind it, and one on each gate tower
        torch([s * 2.5, G + 2.3, z], -s * add.pi / 2)  # beside the gate
for s in (-1, 1):
    torch([s * 4.3, G + 3.3, GATE_FRONT], 0.0)
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
GUN_A = [PHI[k] + (add.pi / 8 if k % 2 else -add.pi / 8) for k in range(8)]                 # every tower top has a gun (see
XBOW_A = [PHI[k] + (-0.7 if k % 2 else 0.7) for k in range(8)]                               # "the guns on the walls"), and
for k, c in enumerate(CORNERS):                                                              # a crossbowman at the parapet,
    aa = XBOW_A[k]                                                                           # facing out on the other side of
    assert (aa - (ARRIVE[k] - HEADROOM - 0.35)) % (2 * add.pi) >= HEADROOM + 0.95            # it, clear of the stairwell and its wall
    bowman([c[0] + 2.3 * add.cos(aa), TOWER_TOP, c[2] + 2.3 * add.sin(aa)], add.atan2(add.cos(aa), add.sin(aa)), "crossbow")
for k in (2, 3, 4, 5, 6):                                                                    # archers on the wall walk, each at an
    a, b = CORNERS[k], CORNERS[(k + 1) % 8]                                                  # embrasure between two merlons
    L, d, n = outward(a, b)
    for t in (0.3, 0.7):
        x = TOWER_R - 0.5 + 1.85 + 2.3 * round((t * (L - 2 * (TOWER_R - 0.5)) - 1.85) / 2.3)
        bowman([a[0] + d[0] * x + n[0] * 0.25, WALK, a[2] + d[2] * x + n[2] * 0.25], add.atan2(n[0], n[2]),
               "bow" if (k + int(t * 10)) % 2 else "crossbow")
flush("wall walk")


def watchman(at, facing=0.0):
    """The lookout of the donjon: a man in a steel cap on a chair (its seat
    at ``at``), a spyglass to his right eye, both hands on it, keeping
    watch over the road and the lake."""
    M = person("sit", P["blue"], hat="steel", seat=0.48,
               arms=(([-0.07, 0.8, 0.24], [0.3, 0.1, 1], [-1, -0.5, -0.3]), ([0.02, 0.81, 0.44], [-0.4, 0.1, 1], [1, -0.6, 0])))
    M.extend(add.make(add.cylinder, [-0.03, 0.855, 0.1], [-0.03, 0.87, 0.5], 0.028, 10, P["gold"]))          # the spyglass
    M.extend(add.make(add.cylinder, [-0.03, 0.87, 0.5], [-0.03, 0.874, 0.64], 0.04, 10, P["gold"]))
    add.mesh(add.move(add.rotateY(add.stretch(M, [LIFE] * 3, (0, 0, 0)), facing), at))


LOOK_A = 2 * add.pi * 3 / 14                                                                  # the donjon's lookout: a chair
lx, lz = DON[0] + 4.5 * add.cos(LOOK_A), DON[1] + 4.5 * add.sin(LOOK_A)                        # facing an embrasure to the south,
chair([lx, DON_TOP, lz], add.pi / 2 - LOOK_A, P["wood_dark"])                                  # towards the gate, the road and
watchman([lx, DON_TOP + 0.48, lz], add.pi / 2 - LOOK_A)                                        # the lake, and the watchman in it
princess([DON[0], DON_TOP, DON[1]], add.atan2(-DON[0], 50.0 - DON[1]))                          # in the middle of the highest
                                                                                                # tower, the princess, looking out to the gate


def clear_of_stair(arrive, ang, head):
    """Is the angle ``ang`` on a tower top clear of the opening where its
    stair comes up (``head`` wide, ending at ``arrive``) and of the low
    wall round it?"""
    return (ang - (arrive - head - 0.35)) % (2 * add.pi) >= head + 0.95


def along_clear(arrive, head, t):
    """The angle a fraction ``t`` of the way round the part of a tower top
    that is clear of the stairwell."""
    a0 = arrive + 0.6
    return a0 + t * (2 * add.pi - head - 0.95)


for k, c in enumerate(CORNERS):                                     # a second man on every tower of the wall: an archer,
    ang = along_clear(ARRIVE[k], HEADROOM, 0.96 if k % 2 else 0.12)  # at the end of the free part of the top beyond the
    assert clear_of_stair(ARRIVE[k], ang, HEADROOM)                  # gun, away from the crossbowman
    bowman([c[0] + 2.6 * add.cos(ang), TOWER_TOP, c[2] + 2.6 * add.sin(ang)], add.atan2(add.cos(ang), add.sin(ang)), "bow")
tops = [((s * 7, 50), G + 20, GATE_ARRIVE[i], 1.65) for i, s in enumerate((-1, 1))]                 # two on each gate tower
tops += [(PALACE_TOWERS[i], EAVE + 4, PT_ARRIVE[i], 2.3) for i in range(len(PALACE_TOWERS))]       # and each palace tower
for i, ((cx, cz), y, arrive, radius) in enumerate(tops):
    for j, t in enumerate((0.25, 0.75)):
        ang = along_clear(arrive, HEADROOM, t)
        bowman([cx + radius * add.cos(ang), y, cz + radius * add.sin(ang)], add.atan2(add.cos(ang), add.sin(ang)),
               "bow" if (i + j) % 2 else "crossbow")
for da in (1.3, -1.3, 2.2, -2.2):                                   # and a crossbowman by the watchman on the donjon
    ang = LOOK_A + da
    if clear_of_stair(DON_ARRIVE, ang, WALL_HEAD):
        bowman([DON[0] + 4.3 * add.cos(ang), DON_TOP, DON[1] + 4.3 * add.sin(ang)], add.atan2(add.cos(ang), add.sin(ang)), "crossbow")
        break
flush("the donjon's lookout, shooters on the towers")


# the guns on the walls, ready for the enemy, and their gunners -- the newest trade in the garrison.  Over the gate,
# on the roof between the gate towers, two heavy guns point out over the drawbridge through the embrasures, with a
# pile of balls and a keg of powder behind them; on every tower of the wall a lighter gun points out between two
# posts of its lantern.  By each gun its gunner, the linstock in his hand and its match alight.
def gunner(at, facing=0.0):
    """A gunner: a coat of buff leather over red hose, a steel cap, a powder
    horn at his hip, and in his right hand the linstock -- its butt on the
    ground, the slow match smouldering in the fork at its head."""
    M = person("stand", P["bread"], hat="steel", hose=P["red"],
               arms=(([-0.26, 1.0, 0.17], [0, 0, 1], [-0.4, 0, -1]), ([0.245, 0.86, 0.03], [0, -1, 0.1], [0, 0, -1])))
    add.push()
    butt, head = [-0.29, 0.02, 0.24], [-0.255, 1.62, 0.18]                  # the linstock, up through his fist
    add.cylinder(butt, head, 0.018, 6, P["wood"])
    add.cone(butt, [butt[0], butt[1] - 0.02, butt[2]], 0.02, 6, P["iron"])  # its shoe
    for sx in (-1, 1):                                                      # the fork at its head, the match wound round
        tip = [head[0] + sx * 0.05, head[1] + 0.1, head[2]]                 # one prong, its end alight
        add.cylinder(head, tip, 0.008, 4, P["iron"])
        add.cylinder([tip[0], tip[1] - 0.05, tip[2]], [tip[0], tip[1] - 0.01, tip[2]], 0.014, 6, P["rope"])
    add.sphere([head[0] + 0.05, head[1] + 0.115, head[2]], 0.017, 3, P["orange"])
    add.sphere([head[0] + 0.06, head[1] + 0.2, head[2]], 0.035, 3, SMOKE)
    add.cone([0.215, 1.0, -0.07], [0.245, 0.84, 0.05], 0.035, 8, P["bone"])  # the powder horn
    add.cylinder([0.215, 1.0, -0.07], [0.212, 1.02, -0.085], 0.035, 8, P["wood_dark"])
    M.extend(add.pop())
    add.mesh(add.move(add.rotateY(add.stretch(M, [LIFE] * 3, (0, 0, 0)), facing), at))


GUN_Z = GATE_Z1 + 0.35 - 1.95                          # the gate's guns: their muzzles in the embrasures
for x in (-1.65, 0.65):
    cannon([x, GATE_ROOF, GUN_Z], -add.pi / 2, balls=False)
gunner([-0.5, GATE_ROOF, GUN_Z - 1.8], 0.0)
gunner([1.75, GATE_ROOF, GUN_Z - 1.8], 0.0)
ball_pile([-2.2, GATE_ROOF, GATE_Z0 + 0.95])
barrel([2.35, GATE_ROOF, GATE_Z0 + 0.95], 0.4, 0.95)
for k, c in enumerate(CORNERS):                        # the towers' guns, the gunner beside the breech on the side of
    a, side = GUN_A[k], (-1 if k % 2 else 1)           # the crossbowman
    cannon([c[0] + 2.5 * add.cos(a), TOWER_TOP, c[2] + 2.5 * add.sin(a)], -a, balls=False, s=0.75)
    gx, gz = c[0] + 1.79 * add.cos(a) - side * 1.05 * add.sin(a), c[2] + 1.79 * add.sin(a) + side * 1.05 * add.cos(a)
    gunner([gx, TOWER_TOP, gz], add.pi / 2 - a)
flush("the guns on the walls and their gunners")


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

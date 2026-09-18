"""
28 -- a voxel island.

Block worlds are height maps: a table of integers says how many cubes
stand on each cell, and ``heightmap`` builds only the visible faces of the
whole thing in one go.  The colour function paints each *layer* --
water, sand, grass, rock, snow -- so the terrain colours itself.
``pixels`` draws a flag and a signpost from strings of characters;
``voxels`` places single cubes for the campfire, and trees are scattered
on the surface with ``random_points`` reading the same height table.

Parameters: ``SIZE`` (cells across), ``SEED``.
"""
import add

SIZE = 44
SEED = 3
CELL = 0.5
rng = add.Random(SEED)

WATER, SAND, GRASS, ROCK, SNOW = [50, 120, 200], [225, 205, 150], [95, 165, 75], [130, 125, 120], "white"


# --------------------------------------------------------------------------
#  the terrain table: smooth bumps plus a little noise, rounded to cubes
# --------------------------------------------------------------------------
bumps = [(rng.uniform(-14, 14), rng.uniform(-14, 14), rng.uniform(3, 9), rng.uniform(5, 9))
         for _ in range(7)]


def height(i, j):
    x, z = i - SIZE / 2.0, j - SIZE / 2.0
    h = 2.0 - 0.02 * (x * x + z * z) ** 0.5 * 2.2            # the island falls away
    for bx, bz, amp, width in bumps:
        h += amp * add.exp(-((x - bx) ** 2 + (z - bz) ** 2) / width ** 2)
    return int(add.clamp(h + rng.uniform(-0.3, 0.3), 1, 16))


H = [[height(i, j) for j in range(SIZE)] for i in range(SIZE)]
SEA = 3                                   # cells at or below this level are water


def paint(i, j, k):
    top = H[i][k]
    if top <= SEA:
        return WATER if j == top - 1 else add.shade(WATER, 0.8)
    if j < SEA:
        return SAND
    if top < SEA + 2:
        return SAND
    if j >= 13:
        return SNOW
    if j >= 10:
        return ROCK
    return GRASS if j == top - 1 else add.shade(GRASS, 0.75)


add.heightmap(H, CELL, [-SIZE * CELL / 2, 0, -SIZE * CELL / 2], paint)


def surface(x, z):
    """World height of the terrain at world (x, z), for placing things."""
    i = int(add.clamp((x + SIZE * CELL / 2) / CELL, 0, SIZE - 1))
    k = int(add.clamp((z + SIZE * CELL / 2) / CELL, 0, SIZE - 1))
    return H[i][k] * CELL


# --------------------------------------------------------------------------
#  trees, a campfire, a signpost and a flag
# --------------------------------------------------------------------------
spots = [p for p in add.random_points(120, [-10, 0, -10], [10, 0, 10], SEED, surface)
         if SEA * CELL + 1.0 < p[1] < 10 * CELL]
for n, p in enumerate(spots[:28]):
    add.tree(p, rng.uniform(1.6, 2.6), [90, 60, 40], add.shade(GRASS, rng.uniform(0.6, 0.9)),
             kind="pine" if n % 4 == 0 else "round", seed=n)

# the highest point: a flag on a pole
peak = max((H[i][k], i, k) for i in range(SIZE) for k in range(SIZE))
px, pz = (peak[1] + 0.5) * CELL - SIZE * CELL / 2, (peak[2] + 0.5) * CELL - SIZE * CELL / 2
py = peak[0] * CELL
add.cylinder([px, py, pz], [px, py + 4.0, pz], 0.06, 8, "silver")
add.pixels(["yyyyyyyy", "ggggyyyy", "ggggrrrr", "rrrrrrrr"], 0.28, [px + 0.06, py + 2.9, pz - 0.1],
           depth=1)
add.sphere([px, py + 4.05, pz], 0.12, 4, "gold")

# a campfire on the beach (the first random spot that lies on sand)
beach = [p for p in add.random_points(400, [-10, 0, 2], [10, 0, 10], SEED + 2, surface)
         if abs(p[1] - (SEA + 1) * CELL) < 1e-9]
cx, cz = beach[0][0], beach[0][2]
cy = surface(cx, cz)
add.voxels([(0, 0, 0), (1, 0, 0), (2, 0, 0), (0, 0, 2), (1, 0, 2), (2, 0, 2),
            (0, 0, 1), (2, 0, 1)], CELL * 0.5, [cx - CELL * 0.75, cy, cz - CELL * 0.75], [80, 50, 30])
for n in range(6):
    add.sphere([cx + rng.uniform(-0.15, 0.15), cy + 0.35 + 0.22 * n, cz + rng.uniform(-0.15, 0.15)],
               0.28 - 0.035 * n, 3, add.gradient(n / 5.0, "yellow", "red"))

# a signpost with the island's name
sx, sz = 2.0, 8.0
sy = surface(sx, sz)
add.cylinder([sx, sy, sz], [sx, sy + 1.6, sz], 0.07, 6, [110, 80, 50])
add.cuboid([sx, sy + 1.4, sz], [2.6, 0.55, 0.12], [150, 110, 70])
add.text("SALA", [sx - 0.95, sy + 1.2, sz + 0.07], 0.4, color="white", k=6)
add.text("SALA", [sx + 0.95, sy + 1.2, sz - 0.07], 0.4, color="white", k=6, u=[-1, 0, 0])

# a rowing boat of coloured cubes, moored off the beach
add.pixels(["n....n", "nnnnnn"], CELL, [-8.5, SEA * CELL - 0.2, 9.5], depth=3,
           colors={"n": [150, 90, 50]})

# the name of the island written on the water, flat
add.text("VOXEL ISLAND", [-8, SEA * CELL + 0.02, -10], 1.2, color=add.shade(WATER, 1.3), k=6,
         u=[1, 0, 0], v=[0, 0, -1])

add.check()
add.save("voxel_island.off")

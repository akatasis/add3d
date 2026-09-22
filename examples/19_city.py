"""
19 -- a procedural city.

One parameter, ``SEED``, decides the whole town; another, ``BLOCKS``, decides
how big it is.  That is what the assignment means by "the shape must depend
on a parameter": change one number, get a different model.
"""
import add

SEED = 2026
BLOCKS = 7                      # the city is BLOCKS x BLOCKS street blocks
rng = add.Random(SEED)

WINDOW = [255, 235, 150]
ROAD = [60, 60, 66]
PARK = [70, 130, 70]


def tower(width, depth, height, style):
    """One building, built on a scene of its own and returned as a mesh.

    ``add.push()`` puts the streets aside so that the ``layer()`` calls below
    cannot swallow them; ``add.pop()`` gives the building back and restores
    the city.
    """
    add.push()
    body = add.hsv(rng.uniform(0.5, 0.65), rng.uniform(0.05, 0.3),
                   rng.uniform(0.55, 0.95))
    if style == 0:                                     # a plain slab
        add.cuboid([0, height / 2, 0], [width, height, depth], body)
    elif style == 1:                                   # stepped setbacks
        steps = rng.randint(2, 4)
        y = 0.0
        for s in range(steps):
            h = height / steps
            k = 1.0 - 0.18 * s
            add.cuboid([0, y + h / 2, 0], [width * k, h, depth * k], body)
            y += h
    elif style == 2:                                   # a round tower
        add.cylinder([0, 0, 0], [0, height, 0], width / 2, 24, body)
        add.cone([0, height, 0], [0, height + width, 0], width / 2, 24,
                 [180, 60, 60])
    else:                                              # a tapering tower
        add.extrude([[-width / 2, -depth / 2], [width / 2, -depth / 2],
                     [width / 2, depth / 2], [-width / 2, depth / 2]],
                    [0, height, 0], body, steps=8,
                    scale=lambda t: 1 - 0.45 * t, center=(0, 0, 0))
    shell = add.layer()

    # windows: small bright plates pressed into the walls
    if style != 2:
        rows = max(1, int(height / 0.55))
        for r in range(rows):
            y = 0.35 + r * 0.55
            if y > height - 0.3:
                break
            for sx, sz, w, d in ((width / 2, 0, 0.06, depth * 0.8),
                                 (-width / 2, 0, 0.06, depth * 0.8),
                                 (0, depth / 2, width * 0.8, 0.06),
                                 (0, -depth / 2, width * 0.8, 0.06)):
                if rng.random() < 0.55:
                    add.cuboid([sx, y, sz], [w, 0.3, d], WINDOW)
        shell = add.merge([shell, add.layer()])

    if style in (0, 1) and rng.random() < 0.4:         # a roof mast
        add.cylinder([0, height, 0], [0, height + rng.uniform(0.5, 1.6), 0],
                     0.05, 6, [200, 60, 60])
        shell = add.merge([shell, add.layer()])
    add.pop()
    return shell


# --------------------------------------------------------------------------
#  streets and blocks
# --------------------------------------------------------------------------
SPAN = BLOCKS * 4.0
add.cuboid([SPAN / 2, -0.15, SPAN / 2], [SPAN + 4, 0.3, SPAN + 4], ROAD)

for bx in range(BLOCKS):
    for bz in range(BLOCKS):
        x0, z0 = bx * 4.0, bz * 4.0
        if rng.random() < 0.12:                        # a park
            add.cuboid([x0 + 1.5, 0.02, z0 + 1.5], [3.2, 0.08, 3.2], PARK)
            for _ in range(rng.randint(2, 5)):
                px = x0 + rng.uniform(0.3, 2.7)
                pz = z0 + rng.uniform(0.3, 2.7)
                h = rng.uniform(0.6, 1.3)
                add.cylinder([px, 0, pz], [px, h, pz], 0.06, 6, [90, 60, 40])
                add.sphere([px, h + 0.28, pz], 0.32, 8, [60, 150, 60])
            continue
        add.cuboid([x0 + 1.5, 0.02, z0 + 1.5], [3.4, 0.08, 3.4], [90, 90, 96])
        for cell in range(rng.randint(1, 4)):
            w = rng.uniform(0.7, 1.4)
            d = rng.uniform(0.7, 1.4)
            h = rng.uniform(1.2, 7.0) * (1.6 if (bx - BLOCKS / 2) ** 2
                                         + (bz - BLOCKS / 2) ** 2 < 4 else 1.0)
            style = rng.choice([0, 0, 1, 2, 3])
            piece = tower(w, d, h, style)
            add.mesh(add.move(piece, [x0 + rng.uniform(0.7, 2.3), 0,
                                      z0 + rng.uniform(0.7, 2.3)]))

add.mesh(add.limit_colors(add.layer(), 50))   # at most 50 colours, so the .obj suits Sketchfab
add.check()
add.save("city.off")

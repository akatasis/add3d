"""
08 -- one formula, a hundred shapes: the superformula.

Johan Gielis noticed in 2003 that a single equation describes starfish,
flowers, diatoms, crystals and plain circles, depending on six numbers:

    r(t) = ( |cos(m t / 4) / a| ^ n2  +  |sin(m t / 4) / b| ^ n3 ) ^ (-1 / n1)

Wrap two of those radial functions around each other and you get a surface.
Changing one number changes the creature -- which is exactly the kind of
"one parameter controls the shape" the assignment asks for.
"""
import add

TAU = 2 * add.pi


def super_r(t, m, n1, n2, n3, a=1.0, b=1.0):
    """The superformula radius at angle ``t``."""
    p = abs(add.cos(m * t / 4.0) / a) ** n2
    q = abs(add.sin(m * t / 4.0) / b) ** n3
    s = p + q
    if s < 1e-12:
        return 0.0
    return s ** (-1.0 / n1)


def supershape(p1, p2):
    """A 3D surface from two sets of superformula parameters."""
    def S(u, v):                       # u around the equator, v pole to pole
        r1 = super_r(u, *p1)
        r2 = super_r(v, *p2)
        return [r1 * add.cos(u) * r2 * add.cos(v),
                r2 * add.sin(v),
                r1 * add.sin(u) * r2 * add.cos(v)]
    return S


#: (name, equator parameters, meridian parameters)
SHAPES = [
    ("sphere",      (0, 1, 1, 1),      (0, 1, 1, 1)),
    ("star",        (5, 0.4, 0.4, 0.4), (5, 0.4, 0.4, 0.4)),
    ("flower",      (6, 1, 7, 8),      (6, 1, 7, 8)),
    ("starfish",    (5, 0.2, 1.7, 1.7), (5, 0.2, 1.7, 1.7)),
    ("cube-ish",    (4, 40, 40, 40),   (4, 40, 40, 40)),
    ("diamond",     (4, 1, 1, 1),      (4, 1, 1, 1)),
    ("pillow",      (4, 1, 1, 1),      (0, 1, 1, 1)),
    ("gear",        (12, 15, 15, 15),  (12, 15, 15, 15)),
    ("seed pod",    (3, 4.5, 10, 10),  (3, 4.5, 10, 10)),
    ("shell",       (7, 0.2, 1.7, 1.7), (2, 0.5, 1.7, 1.7)),
    ("coral",       (8, 0.5, 0.5, 8),  (8, 0.5, 0.5, 8)),
    ("bulb",        (2, 0.7, 0.3, 0.2), (2, 0.7, 0.3, 0.2)),
]

CELL = 3.0
columns = 4
shown = []
for i, (name, p1, p2) in enumerate(SHAPES):
    add.parametric(supershape(p1, p2), -add.pi, add.pi, 120,
                   -add.pi / 2, add.pi / 2, 90,
                   add.hsv(i / float(len(SHAPES)), 0.55, 0.95),
                   wrap_u=True)
    # layer() must be taken before anything else is drawn, or the next shape
    # would scoop up the ones already placed.
    shown.append(add.place(add.fit(add.layer(), 2.2), (0, 0, 0)))
    print("%2d. %s" % (i + 1, name))

for i, M in enumerate(shown):
    add.mesh(add.move(M, [(i % columns) * CELL, 0, (i // columns) * CELL]))

add.check()
add.save("supershapes.off")

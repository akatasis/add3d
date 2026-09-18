"""
07 -- surfaces with a twist: one-sided and self-intersecting.

These are the surfaces that are hard to hold in your head and easy to write
down.  Several of them are *non-orientable*: they have only one side, so the
idea of "outside" stops making sense.  Give them a thickness and they become
ordinary two-sided solids again -- which is also the honest way to see them.
"""
import add

TAU = 2 * add.pi
CELL = 3.4
shown = []


def show(name, build, col, size=2.4):
    build(col)
    shown.append((name, add.place(add.fit(add.layer(), size), (0, 0, 0))))


# --------------------------------------------------------------------------
#  Möbius strip -- one edge, one side
# --------------------------------------------------------------------------
def mobius(u, v):
    return [(1 + v / 2 * add.cos(u / 2)) * add.cos(u),
            v / 2 * add.sin(u / 2),
            (1 + v / 2 * add.cos(u / 2)) * add.sin(u)]


show("Mobius strip", lambda c: add.parametric(mobius, 0, TAU, 160, -1, 1, 10,
                                              c, double_sided=True), "red")

# A wide Möbius band, given a real thickness: now it is a solid you can print.
show("Mobius solid", lambda c: add.parametric(mobius, 0, TAU, 160, -1, 1, 10,
                                              c, thickness=0.09), "orange")


# --------------------------------------------------------------------------
#  Klein bottle, figure-eight immersion -- a bottle with no inside
# --------------------------------------------------------------------------
def klein8(u, v):
    r = 2.0
    cu, su = add.cos(u / 2), add.sin(u / 2)
    sv, s2v = add.sin(v), add.sin(2 * v)
    f = r + cu * sv - su * s2v
    return [f * add.cos(u), su * sv + cu * s2v, f * add.sin(u)]


show("Klein bottle (fig-8)",
     lambda c: add.parametric(klein8, 0, TAU, 120, 0, TAU, 60, c,
                              wrap_u=True, wrap_v=True), "gold")


# --------------------------------------------------------------------------
#  Klein bottle, the classic bottle shape
# --------------------------------------------------------------------------
def klein_bottle(u, v):
    cu, su = add.cos(u), add.sin(u)
    cv, sv = add.cos(v), add.sin(v)
    if u < add.pi:
        x = 3 * cu * (1 + su) + (2 * (1 - cu / 2)) * cu * cv
        z = -8 * su - 2 * (1 - cu / 2) * su * cv
    else:
        x = 3 * cu * (1 + su) + (2 * (1 - cu / 2)) * add.cos(v + add.pi)
        z = -8 * su
    y = -2 * (1 - cu / 2) * sv
    return [x, y, z]


show("Klein bottle", lambda c: add.parametric(klein_bottle, 0, TAU, 120, 0,
                                              TAU, 60, c, wrap_v=True,
                                              double_sided=True), "lime")


# --------------------------------------------------------------------------
#  Boy's surface -- the projective plane immersed in space
# --------------------------------------------------------------------------
def boy(u, v):
    cu, su = add.cos(u), add.sin(u)
    cv, sv = add.cos(v), add.sin(v)
    d = 2 - add.sqrt(2) * add.sin(3 * u) * add.sin(2 * v)
    return [add.sqrt(2) * cv * cv * add.cos(2 * u) / d + cv * cv * add.cos(2 * u) * 0,
            3 * cv * cv / d - 1.5,
            add.sqrt(2) * cv * cv * add.sin(2 * u) / d]


def boy_full(u, v):
    """A fuller Boy's surface: the Bryant-Kusner style parametrisation."""
    cu, su = add.cos(u), add.sin(u)
    cv, sv = add.cos(v), add.sin(v)
    d = 2 - add.sqrt(2) * add.sin(3 * u) * add.sin(2 * v)
    x = (add.sqrt(2) * cv * cv * add.cos(2 * u)
         + cu * add.sin(2 * v)) / d
    y = (add.sqrt(2) * cv * cv * add.sin(2 * u)
         - su * add.sin(2 * v)) / d
    z = 3 * cv * cv / d
    return [x, z - 1.2, y]


show("Boy's surface", lambda c: add.parametric(boy_full, 0, add.pi, 100,
                                               -add.pi / 2, add.pi / 2, 100,
                                               c, wrap_u=True,
                                               double_sided=True), "teal")


# --------------------------------------------------------------------------
#  Roman (Steiner) surface and the cross-cap
# --------------------------------------------------------------------------
def roman(u, v):
    su, cu = add.sin(u), add.cos(u)
    sv, cv = add.sin(v), add.cos(v)
    return [su * su * add.sin(2 * v) / 2,
            su * cu * sv,
            su * cu * cv]


show("Roman surface", lambda c: add.parametric(roman, 0, add.pi, 90, 0,
                                               TAU, 90, c, wrap_v=True,
                                               double_sided=True), "purple")


def cross_cap(u, v):
    su, cu = add.sin(u), add.cos(u)
    sv, cv = add.sin(v), add.cos(v)
    return [su * add.sin(2 * v) / 2, su * su * cv, su * cu * (1 + cv) / 1.0]


show("cross-cap", lambda c: add.parametric(cross_cap, 0, add.pi, 90, 0, TAU,
                                           90, c, wrap_v=True,
                                           double_sided=True), "magenta")


# --------------------------------------------------------------------------
#  Enneper's minimal surface and Henneberg's surface
# --------------------------------------------------------------------------
def enneper(u, v):
    return [u - u ** 3 / 3 + u * v * v,
            u * u - v * v,
            v - v ** 3 / 3 + v * u * u]


show("Enneper surface", lambda c: add.parametric(enneper, -2, 2, 60, -2, 2,
                                                 60, c, thickness=0.09), "sky")


def scherk(u, v):
    """Scherk's surface: cos(y) = cos(x) e^z, drawn as a height field."""
    return [u, add.log(abs(add.cos(v) / add.cos(u))), v]


show("Scherk surface", lambda c: add.parametric(
    scherk, -1.4, 1.4, 60, -1.4, 1.4, 60, c, thickness=0.08), "brown")


# --------------------------------------------------------------------------
#  Trefoil knot ribbon -- a band that follows a knot
# --------------------------------------------------------------------------
def trefoil_path(t):
    return [add.sin(t) + 2 * add.sin(2 * t),
            -add.sin(3 * t),
            -add.cos(t) + 2 * add.cos(2 * t)]


show("trefoil ribbon", lambda c: add.ribbon(trefoil_path, 0, TAU, 220, 0.8, c,
                                            closed=True, twist=3 * add.pi,
                                            thickness=0.06), "navy")


# --------------------------------------------------------------------------
#  lay them out and save
# --------------------------------------------------------------------------
columns = 4
for i, (name, M) in enumerate(shown):
    add.mesh(add.move(M, [(i % columns) * CELL, 0, (i // columns) * CELL]))
    print("%2d. %s" % (i + 1, name))

add.check()
add.save("surfaces_exotic.off")

"""
09 -- surfaces that look like things: shells, fruit, horns and waves.

Nature is surprisingly parametric.  A seashell is a circle whose radius grows
while it spirals; an apple is a sphere with a dent; a horn is a cone wrapped
round a logarithmic spiral.
"""
import add

TAU = 2 * add.pi
CELL = 3.4
shown = []


def show(name, build, col, size=2.4):
    build(col)
    shown.append((name, add.place(add.fit(add.layer(), size), (0, 0, 0))))


# --------------------------------------------------------------------------
#  A seashell: a circle that spirals outwards while it grows
# --------------------------------------------------------------------------
def seashell(u, v):
    a, b, c = 0.2, 1.0, 0.1
    n = 2.0
    w = add.exp(a * u)
    return [w * (b + add.cos(v)) * add.cos(n * u),
            w * (c * u / 2 + add.sin(v)),
            w * (b + add.cos(v)) * add.sin(n * u)]


show("seashell", lambda c: add.parametric(seashell, 0, 6 * add.pi, 240,
                                          0, TAU, 36, c, wrap_v=True), "orange")


# --------------------------------------------------------------------------
#  A snail shell with a sharper spiral
# --------------------------------------------------------------------------
def snail(u, v):
    k = 0.16
    r = add.exp(k * u)
    tube = 0.32 * r
    return [r * add.cos(u) + tube * add.cos(v) * add.cos(u),
            0.45 * r + tube * add.sin(v),
            r * add.sin(u) + tube * add.cos(v) * add.sin(u)]


show("snail", lambda c: add.parametric(snail, 0, 8 * add.pi, 300, 0, TAU, 30,
                                       c, wrap_v=True), "brown")


# --------------------------------------------------------------------------
#  Dini's surface -- a helical version of the pseudosphere
# --------------------------------------------------------------------------
def dini(u, v):
    return [add.cos(u) * add.sin(v),
            add.cos(v) + add.log(add.tan(v / 2)) + 0.2 * u,
            add.sin(u) * add.sin(v)]


show("Dini's surface", lambda c: add.parametric(dini, 0, 4 * add.pi, 180,
                                                0.05, 2.0, 40, c), "lime")


# --------------------------------------------------------------------------
#  Apple and lemon -- two spheres with the poles pulled about
# --------------------------------------------------------------------------
def apple(u, v):
    r1, r2 = 4.0, 3.8
    return [add.cos(u) * (r1 + r2 * add.cos(v)) + add.pow(v / add.pi, 100),
            -2.3 * add.log(1 - v * 0.3157) + 6 * add.sin(v)
            + 2 * add.cos(v),
            add.sin(u) * (r1 + r2 * add.cos(v))]


show("apple", lambda c: add.parametric(apple, 0, TAU, 60, -add.pi, add.pi,
                                       60, c, wrap_u=True), "red")


def lemon(u, v):
    return [add.cos(u / 2) ** 4 * add.cos(v) * 2,
            add.sin(u) / 2,
            add.cos(u / 2) ** 4 * add.sin(v) * 2]


show("lemon", lambda c: add.parametric(lemon, -add.pi, add.pi, 60, 0, TAU,
                                       60, c, wrap_v=True), "yellow")


# --------------------------------------------------------------------------
#  A heart
# --------------------------------------------------------------------------
def heart(u, v):
    s = add.sin(v)
    return [s * (15 * add.sin(u) - 4 * add.sin(3 * u)),
            8 * add.cos(v),
            s * (15 * add.cos(u) - 5 * add.cos(2 * u)
                 - 2 * add.cos(3 * u) - add.cos(4 * u))]


show("heart", lambda c: add.parametric(heart, 0, TAU, 80, 0, add.pi, 50, c,
                                       wrap_u=True), "pink")


# --------------------------------------------------------------------------
#  A horn, a trumpet flower and a twisted column
# --------------------------------------------------------------------------
def horn(u, v):
    r = 0.12 * (1 + 1.4 * u / TAU) ** 2
    R = 1.4 * add.exp(0.22 * u)
    return [(R + r * add.cos(v)) * add.cos(u),
            r * add.sin(v) + 0.6 * u,
            (R + r * add.cos(v)) * add.sin(u)]


show("horn", lambda c: add.parametric(horn, 0, 3.6 * add.pi, 180, 0, TAU, 28,
                                      c, wrap_v=True), "gold")


def trumpet(u, v):
    r = 0.3 + 1.9 * (u / 3.0) ** 4
    return [r * add.cos(v), u, r * add.sin(v)]


show("trumpet flower", lambda c: add.parametric(
    trumpet, 0, 3.0, 50, 0, TAU, 60, c, wrap_v=True, thickness=0.05), "magenta")


def fluted(u, v):
    r = 1.0 + 0.16 * add.cos(9 * (v + 0.5 * u))
    return [r * add.cos(v), u, r * add.sin(v)]


show("fluted column", lambda c: add.parametric(fluted, 0, 5.0, 60, 0, TAU, 90,
                                               c, wrap_v=True), "silver")


# --------------------------------------------------------------------------
#  A breather surface -- a soliton of the sine-Gordon equation
# --------------------------------------------------------------------------
def breather(u, v):
    b = 0.4
    w = add.sqrt(1 - b * b)
    denom = b * ((w * add.cosh(b * u)) ** 2 + (b * add.sin(w * v)) ** 2)
    return [-u + 2 * w * w * add.cosh(b * u) * add.sinh(b * u) / denom,
            2 * w * add.cosh(b * u) * (-w * add.cos(v) * add.cos(w * v)
                                        - add.sin(v) * add.sin(w * v)) / denom,
            2 * w * add.cosh(b * u) * (-w * add.sin(v) * add.cos(w * v)
                                        + add.cos(v) * add.sin(w * v)) / denom]


show("breather", lambda c: add.parametric(breather, -13, 13, 160, -14, 14,
                                          200, c, double_sided=True), "teal")


# --------------------------------------------------------------------------
#  Ripples on a pond and a drop
# --------------------------------------------------------------------------
show("ripples", lambda c: add.parametric(
    lambda u, v: [u, add.sin(add.sqrt(u * u + v * v) * 3)
                  / (1 + 0.4 * (u * u + v * v)), v],
    -4, 4, 90, -4, 4, 90, c, thickness=0.05), "sky")


def drop(u, v):
    return [0.5 * (1 - add.cos(u)) * add.sin(u) * add.cos(v),
            add.cos(u),
            0.5 * (1 - add.cos(u)) * add.sin(u) * add.sin(v)]


show("drop", lambda c: add.parametric(drop, 0, add.pi, 60, 0, TAU, 60, c,
                                      wrap_v=True), "navy")


# --------------------------------------------------------------------------
columns = 4
for i, (name, M) in enumerate(shown):
    add.mesh(add.move(M, [(i % columns) * CELL, 0, (i // columns) * CELL]))
    print("%2d. %s" % (i + 1, name))

add.check()
add.save("surfaces_nature.off")

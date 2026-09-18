"""
14 -- the lathe: spin a profile around an axis.

``add.revolve(profile, A, B, t0, t1, steps, k, colour)`` turns a
``profile(t) -> [radius, height]`` around the axis from ``A`` to ``B``.  It is
how a potter works, and it is the fastest way to a vase, a chess piece, a
bottle or a lamp.

Give it ``angle=`` less than a full turn to cut a wedge out and see inside.
"""
import add

CELL = 3.2
shown = []


def show(name, build, col, size=2.8):
    build(col)
    shown.append((name, add.place(add.fit(add.layer(), size), (0, 0, 0))))


def lathe(profile, col, height=4.0, steps=120, k=48, **kw):
    add.revolve(profile, [0, 0, 0], [0, 1, 0], 0, height, steps, k, col, **kw)


# --- a vase: radius as a smooth function of height -------------------------
show("vase", lambda c: lathe(lambda t: [1.1 + 0.55 * add.sin(1.2 * t)
                                        - 0.18 * t, t], c), "teal")

# --- a wine glass ----------------------------------------------------------
def glass(t):
    if t < 0.12:
        return [1.0, t]                      # foot
    if t < 0.2:
        return [1.0 - (t - 0.12) * 9, t]
    if t < 1.6:
        return [0.12, t]                     # stem
    s = (t - 1.6) / 2.4
    return [0.12 + 1.15 * add.sqrt(max(0.0, s)) * (1 - 0.25 * s), t]


show("wine glass", lambda c: lathe(glass, c, 4.0, 160), "sky")

# --- a bottle --------------------------------------------------------------
def bottle(t):
    if t < 2.6:
        return [1.0, t]
    if t < 3.2:
        return [1.0 - 0.62 * (t - 2.6) / 0.6, t]
    return [0.38, t]


show("bottle", lambda c: lathe(bottle, c, 4.2, 140), "green")

# --- chess pieces ----------------------------------------------------------
def pawn(t):
    r = (0.85 * add.exp(-3.0 * t) + 0.22
         + 0.42 * add.exp(-28 * (t - 1.35) ** 2)
         + 0.36 * add.exp(-40 * (t - 2.15) ** 2))
    return [r, t]


show("pawn", lambda c: lathe(pawn, c, 2.5, 140), "silver")


def rook(t):
    if t < 0.35:
        return [0.85 - 0.5 * t, t]
    if t < 1.9:
        return [0.45 + 0.1 * add.exp(-4 * (t - 0.35)), t]
    if t < 2.15:
        return [0.45 + (t - 1.9) * 1.4, t]
    return [0.8, t]


show("rook", lambda c: lathe(rook, c, 2.4, 120), "brown")


def queen(t):
    r = (0.95 * add.exp(-2.6 * t) + 0.2
         + 0.45 * add.exp(-30 * (t - 1.5) ** 2)
         + 0.30 * add.exp(-60 * (t - 2.5) ** 2)
         + 0.55 * add.exp(-45 * (t - 3.1) ** 2))
    return [r, t]


show("queen", lambda c: lathe(queen, c, 3.4, 170), "gold")

# --- a lamp shade: open at both ends ---------------------------------------
show("lamp shade", lambda c: lathe(lambda t: [0.5 + 0.45 * t, t], c, 2.2, 40,
                                   caps=False), "yellow")

# --- a doughnut, from a circular profile -----------------------------------
show("doughnut", lambda c: add.revolve(
    lambda t: [2 + add.cos(t), add.sin(t)], [0, 0, 0], [0, 1, 0],
    0, 2 * add.pi, 40, 72, c), "orange")

# --- a fluted column: the profile wobbles ----------------------------------
show("beaded column", lambda c: lathe(
    lambda t: [0.55 + 0.2 * abs(add.sin(2.4 * t)), t], c, 5.0, 220), "purple")

# --- a spinning top --------------------------------------------------------
show("spinning top", lambda c: lathe(
    lambda t: [1.0 * add.sin(add.pi * min(1.0, t / 1.6)) ** 0.6
               if t < 1.6 else max(0.04, 0.35 - 0.3 * (t - 1.6)), t],
    c, 2.6, 140), "red")

# --- cut open to show the wall ---------------------------------------------
show("cup, cut open", lambda c: lathe(
    lambda t: [1.0 + 0.1 * t, t], c, 2.4, 40, angle=1.55 * add.pi), "magenta")

# --- a screw-like profile --------------------------------------------------
show("ribbed pot", lambda c: lathe(
    lambda t: [1.0 + 0.35 * add.sin(3.0 * t) * add.exp(-0.25 * t), t],
    c, 3.6, 180), "navy")

columns = 4
for i, (name, M) in enumerate(shown):
    add.mesh(add.move(M, [(i % columns) * CELL, 0, (i // columns) * CELL]))
    print("%2d. %s" % (i + 1, name))

add.check()
add.save("lathe.off")

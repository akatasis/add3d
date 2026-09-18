"""
06 -- the classic parametric surfaces.

Each one is three formulas.  ``add.parametric`` walks a rectangle of (u, v)
values, calls your function at every grid point and joins the points up.

    def surface(u, v):
        return [x(u, v), y(u, v), z(u, v)]

    add.parametric(surface, u_from, u_to, u_detail,
                             v_from, v_to, v_detail, colour)
"""
import add

TAU = 2 * add.pi
CELL = 3.2
shown = []


def show(name, build, col, size=2.2):
    """Build one surface, scale it to a standard size and park it on a grid."""
    build(col)
    M = add.place(add.fit(add.layer(), size), (0, 0, 0))
    shown.append((name, M))


# --------------------------------------------------------------------------
#  1. Sphere        x = r cos u sin v,  y = r cos v,  z = r sin u sin v
# --------------------------------------------------------------------------
show("sphere", lambda c: add.parametric(
    lambda u, v: [add.cos(u) * add.sin(v), add.cos(v), add.sin(u) * add.sin(v)],
    0, TAU, 48, 0, add.pi, 24, c, wrap_u=True), "red")

# --------------------------------------------------------------------------
#  2. Torus         a circle of radius b swept round a circle of radius a
# --------------------------------------------------------------------------
show("torus", lambda c: add.parametric(
    lambda u, v: [(3 + add.cos(u)) * add.cos(v), add.sin(u),
                  (3 + add.cos(u)) * add.sin(v)],
    0, TAU, 28, 0, TAU, 56, c, wrap_u=True, wrap_v=True), "orange")

# --------------------------------------------------------------------------
#  3. Cylinder and 4. Cone -- the two simplest ruled surfaces
# --------------------------------------------------------------------------
show("cylinder", lambda c: add.parametric(
    lambda u, v: [add.cos(u), v, add.sin(u)],
    0, TAU, 48, -1.5, 1.5, 8, c, wrap_u=True, thickness=0.08), "gold")

show("cone", lambda c: add.parametric(
    lambda u, v: [v * add.cos(u), v, v * add.sin(u)],
    0, TAU, 48, 0, 2, 12, c, wrap_u=True), "lime")

# --------------------------------------------------------------------------
#  5. Hyperbolic paraboloid -- the saddle, y = v² - u²
# --------------------------------------------------------------------------
show("saddle", lambda c: add.parametric(
    lambda u, v: [u, v * v - u * u, v],
    -1.5, 1.5, 36, -1.5, 1.5, 36, c, thickness=0.06), "teal")

# --------------------------------------------------------------------------
#  6. One-sheet hyperboloid -- straight lines that make a curved surface
# --------------------------------------------------------------------------
show("hyperboloid", lambda c: add.parametric(
    lambda u, v: [add.cosh(v) * add.cos(u), add.sinh(v),
                  add.cosh(v) * add.sin(u)],
    0, TAU, 48, -1.2, 1.2, 20, c, wrap_u=True, thickness=0.06), "sky")

# --------------------------------------------------------------------------
#  7. Helicoid -- a spiral ramp, and 8. its relative the catenoid
# --------------------------------------------------------------------------
show("helicoid", lambda c: add.parametric(
    lambda u, v: [v * add.cos(u), 0.45 * u, v * add.sin(u)],
    0, 3 * TAU, 120, -1.2, 1.2, 10, c, thickness=0.06), "purple")

show("catenoid", lambda c: add.parametric(
    lambda u, v: [add.cosh(v) * add.cos(u), v, add.cosh(v) * add.sin(u)],
    0, TAU, 48, -1.4, 1.4, 20, c, wrap_u=True, thickness=0.05), "magenta")

# --------------------------------------------------------------------------
#  9. Monkey saddle -- three valleys instead of two
# --------------------------------------------------------------------------
show("monkey saddle", lambda c: add.parametric(
    lambda u, v: [u, u ** 3 - 3 * u * v * v, v],
    -1.3, 1.3, 40, -1.3, 1.3, 40, c, thickness=0.05), "brown")

# -------------------------------------------------------------------------
# 10. Egg box -- y = sin(x) cos(z), the surface everybody draws first
# -------------------------------------------------------------------------
show("egg box", lambda c: add.parametric(
    lambda u, v: [u, add.sin(u) * add.cos(v), v],
    -4, 4, 48, -4, 4, 48, c, thickness=0.12), "navy")

# -------------------------------------------------------------------------
# 11. Torus knot tube -- a curve given thickness by sweeping a circle
# -------------------------------------------------------------------------
def knot(u, v):
    p, q, r = 2, 3, 0.35
    cu = add.cos(q * u)
    x = (2 + cu) * add.cos(p * u)
    y = -add.sin(q * u)
    z = (2 + cu) * add.sin(p * u)
    # a small circle around the curve, drawn with a numerical tangent
    h = 1e-4
    t = [((2 + add.cos(q * (u + h))) * add.cos(p * (u + h)) - x) / h,
         (-add.sin(q * (u + h)) - y) / h,
         ((2 + add.cos(q * (u + h))) * add.sin(p * (u + h)) - z) / h]
    n = add.sqrt(sum(a * a for a in t))
    t = [a / n for a in t]
    e1 = [-t[2], 0, t[0]]
    n1 = add.sqrt(sum(a * a for a in e1)) or 1.0
    e1 = [a / n1 for a in e1]
    e2 = [t[1] * e1[2] - t[2] * e1[1], t[2] * e1[0] - t[0] * e1[2],
          t[0] * e1[1] - t[1] * e1[0]]
    return [x + r * (e1[0] * add.cos(v) + e2[0] * add.sin(v)),
            y + r * (e1[1] * add.cos(v) + e2[1] * add.sin(v)),
            z + r * (e1[2] * add.cos(v) + e2[2] * add.sin(v))]


show("torus knot", lambda c: add.parametric(knot, 0, TAU, 220, 0, TAU, 18, c,
                                            wrap_u=True, wrap_v=True), "cyan")

# -------------------------------------------------------------------------
# 12. Pseudosphere -- constant negative curvature, the "trumpet"
# -------------------------------------------------------------------------
show("pseudosphere", lambda c: add.parametric(
    lambda u, v: [add.cos(v) / add.cosh(u), u - add.tanh(u),
                  add.sin(v) / add.cosh(u)],
    -3.5, 3.5, 60, 0, TAU, 40, c, wrap_v=True), "silver")


# --------------------------------------------------------------------------
#  lay them out and save
# --------------------------------------------------------------------------
columns = 4
for i, (name, M) in enumerate(shown):
    add.mesh(add.move(M, [(i % columns) * CELL, 0, (i // columns) * CELL]))
    print("%2d. %s" % (i + 1, name))

add.check()
add.save("surfaces_classic.off")

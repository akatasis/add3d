

# ============================================================================
# 14. A catalogue of named surfaces
# ============================================================================
# Two dozen classical parametric surfaces, ready to draw by name.  Each entry
# holds the formula, the parameter ranges, whether the surface closes on
# itself (so that it is drawn without a seam) and the constants it depends
# on.  The formulas follow the collection at drhuang.com ("parametric
# surfaces", A. Huang) and the standard references (Gray, "Modern
# Differential Geometry of Curves and Surfaces"; 3D-XplorMath).

def _catalog():
    pi, cos, sin, sinh, cosh, exp, log, tan, sqrt = (
        math.pi, math.cos, math.sin, math.sinh, math.cosh, math.exp, math.log,
        math.tan, math.sqrt)
    S = {}

    def entry(name, f, u, v, wrap=(False, False), grid=(60, 60), note="",
              flip=False, **params):
        S[name] = {"f": f, "u": u, "v": v, "wrap": wrap, "grid": grid,
                   "note": note, "flip": flip, "params": params}

    entry("bohemian_dome",
          lambda u, v, a, b, c: [a * cos(u), b * cos(v) + a * sin(u), c * sin(v)],
          (0, 2 * pi), (0, 2 * pi), (True, True),
          note="a circle swept along another circle", a=0.5, b=1.5, c=1.0)
    entry("dini",
          lambda u, v, a, b: [a * cos(u) * sin(v), a * sin(u) * sin(v),
                              a * (cos(v) + log(tan(v / 2.0))) + b * u],
          (0, 4 * pi), (0.01, 2.0), (False, False), (120, 40),
          note="a twisted pseudosphere of constant negative curvature",
          a=1.0, b=0.2)
    entry("enneper",
          lambda u, v: [u - u ** 3 / 3.0 + u * v * v, v - v ** 3 / 3.0 + u * u * v,
                        u * u - v * v],
          (-2, 2), (-2, 2), note="a minimal surface that crosses itself")

    def klein(u, v, a, b):
        r = 4.0 * (1.0 - cos(u) / 2.0)
        if u < pi:
            return [a * cos(u) * (1 + sin(u)) + r * cos(u) * cos(v),
                    b * sin(u) + r * sin(u) * cos(v), r * sin(v)]
        return [a * cos(u) * (1 + sin(u)) + r * cos(v + pi), b * sin(u),
                r * sin(v)]
    entry("klein_bottle", klein, (0, 2 * pi), (0, 2 * pi), (False, True),
          (120, 40), note="the one-sided bottle whose neck passes through "
          "its own wall", a=6.0, b=16.0)
    entry("mobius",
          lambda t, s, R: [(R + s * cos(t / 2.0)) * cos(t),
                           (R + s * cos(t / 2.0)) * sin(t), s * sin(t / 2.0)],
          (0, 2 * pi), (-0.5, 0.5), (False, False), (120, 8),
          note="a strip with one side and one edge", R=2.0)
    entry("plucker_conoid",
          lambda u, v: [u * sqrt(1 - v * v), u * v, 1 - v * v],
          (-2, 2), (-1, 1), note="a ruled surface: straight lines through "
          "a vertical axis")

    def worm(u, v, a, b):
        h = exp(u / (6.0 * pi))
        return [a * (1 - h) * cos(u) * cos(v / 2.0) ** 2,
                1 - exp(u / (b * pi)) - sin(v) + h * sin(v),
                a * (h - 1) * sin(u) * cos(v / 2.0) ** 2]
    entry("worm", worm, (0, 6 * pi), (0, 2 * pi), (False, True), (160, 40),
          note="a snail shell that widens as it turns", a=1.0, b=6.0)
    entry("sine_surface",
          lambda u, v: [sin(u), sin(v), sin(u + v)],
          (-pi, pi), (-pi, pi), (True, True),
          note="three sines; it closes on itself in both directions")
    entry("cosine_surface",
          lambda u, v: [cos(u), cos(v), cos(u + v)],
          (-pi, pi), (-pi, pi), (True, True), flip=True,
          note="the cosine twin of the sine surface")
    entry("whitney_umbrella",
          lambda u, v: [u * v, u, v * v],
          (-1.5, 1.5), (-1.5, 1.5), note="a surface with a pinch point")
    entry("helicoid",
          lambda u, v, c: [u * cos(v), u * sin(v), c * v],
          (-2, 2), (0, 2 * pi), (False, False), (30, 120),
          note="a spiral staircase; the only ruled minimal surface", c=0.5)
    entry("hyperbolic_helicoid",
          lambda u, v, a: [sinh(v) * cos(a * u) / (1 + cosh(u) * cosh(v)),
                           sinh(v) * sin(a * u) / (1 + cosh(u) * cosh(v)),
                           cosh(v) * sinh(u) / (1 + cosh(u) * cosh(v))],
          (-4, 4), (-4, 4), grid=(120, 60),
          note="a helicoid bent into a ball", a=2.5)
    entry("henneberg",
          lambda u, v: [2 * cos(v) * sinh(u) - 0.667 * cos(3 * v) * sinh(3 * u),
                        2 * sin(v) * sinh(u) + 0.667 * sin(3 * v) * sinh(3 * u),
                        2 * cos(2 * v) * cosh(2 * u)],
          (-1, 1), (-pi / 2, pi / 2), note="a one-sided minimal surface")
    entry("owl",
          lambda u, v: [v * cos(u) - 0.5 * v * v * cos(2 * u),
                        -v * sin(u) - 0.5 * v * v * sin(2 * u),
                        4 * exp(1.5 * log(v)) * cos(1.5 * u) / 3.0],
          (0, 4 * pi), (0.001, 1), (False, False), (160, 30),
          note="Maeder's owl, a twisted minimal surface")
    entry("snail",
          lambda u, v: [u * cos(v) * sin(u), u * cos(u) * cos(v), -u * sin(v)],
          (0, 2 * pi), (-pi, pi), (False, True), (120, 40),
          note="a horn that curls up on itself")
    entry("kidney",
          lambda u, v: [cos(u) * (3 * cos(v) - cos(3 * v)),
                        sin(u) * (3 * cos(v) - cos(3 * v)),
                        3 * sin(v) - sin(3 * v)],
          (0, 2 * pi), (-pi / 2, pi / 2), (True, False), (80, 40),
          note="a surface of revolution with a dent")
    entry("pillow",
          lambda u, v, a: [cos(u), cos(v), a * sin(u) * sin(v)],
          (0, pi), (-pi, pi), (False, True), (40, 80),
          note="a cushion with four corners", a=0.5)
    entry("horn",
          lambda u, v, a, b, c: [(a + u * cos(v)) * sin(b * pi * u),
                                 (a + u * cos(v)) * cos(b * pi * u) + c * u,
                                 u * sin(v)],
          (0, 1), (-pi, pi), (False, True), (60, 40),
          note="a tube that grows as it bends", a=1.0, b=1.0, c=1.0)
    entry("stiletto",
          lambda u, v: [(2 + cos(u)) * cos(v) ** 3 * sin(v),
                        (2 + cos(u + 2 * pi / 3)) * cos(v + 2 * pi / 3) ** 2
                        * sin(v + 2 * pi / 3) ** 2,
                        -(2 + cos(u - 2 * pi / 3)) * cos(v + 2 * pi / 3) ** 2
                        * sin(v + 2 * pi / 3) ** 2],
          (0, 2 * pi), (0, pi), (True, False), (80, 60),
          note="a pointed shoe")
    entry("apple",
          lambda u, v: [cos(u) * (4 + 3.8 * cos(v)), sin(u) * (4 + 3.8 * cos(v)),
                        (cos(v) + sin(v) - 1) * (1 + sin(v))
                        * log(1 - pi * v / 10.0) + 7.5 * sin(v)],
          (0, 2 * pi), (-pi, pi), (True, False), (80, 60),
          note="an apple with a dimple at the stalk")

    def kuen(u, v):
        h = 1 + u * u * sin(v) ** 2
        return [2 * (cos(u) + u * sin(u)) * sin(v) / h,
                2 * (-u * cos(u) + sin(u)) * sin(v) / h,
                log(tan(v / 2.0)) + 2 * cos(v) / h]
    entry("kuen", kuen, (-4.3, 4.3), (0.03, 3.11), grid=(120, 60),
          note="a surface of constant negative curvature")
    entry("tranguloid_trefoil",
          lambda u, v: [2 * sin(3 * u) / (2 + cos(v)),
                        2 * (sin(u) + 2 * sin(2 * u)) / (2 + cos(v + 2 * pi / 3)),
                        (cos(u) - 2 * cos(2 * u)) * (2 + cos(v))
                        * (2 + cos(v + 2 * pi / 3)) / 4.0],
          (-pi, pi), (-pi, pi), (True, True), (160, 40),
          note="a knotted tube with three lobes")
    entry("antisymmetric_torus",
          lambda u, v, R, r, a: [(R + r * cos(v) * (a + sin(u))) * cos(u),
                                 (R + r * cos(v) * (a + sin(u))) * sin(u),
                                 r * sin(v) * (a + sin(u))],
          (0, 2 * pi), (0, 2 * pi), (True, True), (80, 40),
          note="a torus whose tube is fat on one side", R=2.0, r=0.6, a=1.5)
    entry("twisted_eight_torus",
          lambda u, v, R, r: [(R + r * (cos(u / 2.0) * sin(v) - sin(u / 2.0)
                                        * sin(2 * v))) * cos(u),
                              (R + r * (cos(u / 2.0) * sin(v) - sin(u / 2.0)
                                        * sin(2 * v))) * sin(u),
                              r * (sin(u / 2.0) * sin(v) + cos(u / 2.0)
                                   * sin(2 * v))],
          (0, 2 * pi), (0, 2 * pi), (False, True), (120, 60),
          note="a figure-eight cross-section that twists once around",
          R=2.0, r=1.0)
    entry("wave_ball",
          lambda u, v: [u * cos(cos(u)) * cos(v), u * cos(cos(u)) * sin(v),
                        u * sin(cos(u))],
          (0, 14.5), (0, 2 * pi), (False, True), (160, 40),
          note="rings that ripple outwards")
    return S


#: The named surfaces: ``add.SURFACES["apple"]`` holds the formula ``f``,
#: the ranges ``u`` and ``v``, the ``wrap`` flags, a default ``grid``, a
#: one-line ``note`` and the constants ``params``.  Draw one with
#: :func:`surface`.
SURFACES = _catalog()


def surface_names():
    """The names :func:`surface` understands, alphabetically."""
    return sorted(SURFACES)


def surface_function(name, **params):
    """The ``f(u, v) -> [x, y, z]`` of a named surface, with its constants
    filled in (override any of them by keyword).  Handy for feeding
    :func:`parametric` yourself with a different range or colouring."""
    entry = SURFACES[name]
    values = dict(entry["params"])
    values.update(params)
    f = entry["f"]
    if values:
        return lambda u, v: f(u, v, **values)
    return f


def surface(name, center=(0, 0, 0), size=None, grid=None, color=None,
            thickness=0.0, double_sided=False, **params):
    """Draw one of the catalogued surfaces by name -- see :func:`surface_names`.

    ``size`` scales the surface so that its largest dimension is ``size``
    (leave it out for the natural size); ``grid`` is the number of cells,
    one number or ``[along_u, along_v]``.  ``color`` may be a function
    ``color(u, v)`` as with :func:`parametric`, and the surface's own
    constants can be changed by keyword::

        add.surface("klein_bottle", [0, 0, 0], 4, 120, "teal")
        add.surface("dini", [6, 0, 0], 4, color=lambda u, v: add.hsv(u / 12))
        add.surface("pillow", size=3, a=0.9, thickness=0.1)
    """
    entry = SURFACES[name]
    f = surface_function(name, **params)
    if grid is None:
        gu, gv = entry["grid"]
    elif isinstance(grid, (list, tuple)):
        gu, gv = grid[0], grid[1]
    else:
        gu = gv = int(grid)
    (u0, u1), (v0, v1) = entry["u"], entry["v"]
    wu, wv = entry["wrap"]
    push()
    parametric(f, u0, u1, gu, v0, v1, gv, color, wrap_u=wu, wrap_v=wv,
               flip=entry.get("flip", False), thickness=thickness,
               double_sided=double_sided)
    M = pop()
    if size is not None:
        M = fit(M, size)
    M = place(M, center)
    _scene.extend(M)

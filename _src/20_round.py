

# ============================================================================
#  7. Round solids
# ============================================================================

def _revolve_grid(A, direction, profile, k, angle=2.0 * math.pi, phase=0.0):
    """Points of a surface of revolution.

    ``profile`` is a list of ``(radius, height)`` pairs; ``height`` is measured
    along ``direction`` from ``A``.  Returns the ``P[i][j]`` grid that
    :func:`_add_grid` expects.
    """
    u, v, w = _frame(direction)
    closed = abs(angle - 2.0 * math.pi) < 1e-12
    steps = k if closed else k + 1
    cs = []
    for j in range(steps):
        a = phase + angle * (j / float(k))
        cs.append((math.cos(a), math.sin(a)))
    P = []
    for r, h in profile:
        centre = _add3(A, _scale(w, h))
        row = []
        for c, s in cs:
            row.append((centre[0] + u[0] * r * c + v[0] * r * s,
                        centre[1] + u[1] * r * c + v[1] * r * s,
                        centre[2] + u[2] * r * c + v[2] * r * s))
        P.append(row)
    return P, closed


def revolve(profile, A=(0, 0, 0), B=(0, 1, 0), t0=0.0, t1=1.0, steps=40,
            k=32, color=None, angle=2.0 * math.pi, caps=True):
    """Spin a 2D profile around the axis ``A -> B`` (a lathe).

    ``profile(t)`` returns ``[radius, height]``, where *height* is the
    distance from ``A`` along the axis.  ``steps`` is the detail along the
    profile, ``k`` the detail around the axis.  Set ``angle`` to less than a
    full turn to leave a wedge cut out of the shape.

    With ``caps=True`` (the default) the ends are closed, so the lathe gives
    you a solid ready for a boolean operation; ``caps=False`` leaves the bare
    shell, which is what the old ``spin3D`` produced::

        def vase(t):
            return [1 + 0.4 * math.sin(3 * t), t]
        add.revolve(vase, [0, 0, 0], [0, 1, 0], 0, 4, 60, 40, "teal")
    """
    pts = []
    for i in range(steps + 1):
        t = t0 + (t1 - t0) * i / float(steps)
        g = profile(t)
        pts.append((g[0], g[1]))
    direction = _sub(B, A)
    P, closed = _revolve_grid(A, direction, pts, k, angle)
    color = rgb(color)
    M = Mesh()
    _add_grid(M, P, color, wrap_v=closed, flip=True)
    if caps:
        w = _unit(direction)
        first = _add3(A, _scale(w, pts[0][1]))
        last = _add3(A, _scale(w, pts[-1][1]))
        if pts[0][0] > EPS:                       # flat lid at the start
            _fan(M, P[0], first, color, flip=True)
        if pts[-1][0] > EPS:                      # flat lid at the end
            _fan(M, P[-1], last, color)
        if not closed:                            # the two sides of the wedge
            M.add_polygon([row[0] for row in P] + [last, first], color)
            M.add_polygon([row[-1] for row in P] + [last, first], color)
        _weld(M, 1e-9)
        _drop_degenerate(M)
        if not closed:
            M = fix_normals(M)
    _emit(M)


def spin3D(A, B, S, min_t, max_t, grid_t, k, RGB):
    """add.py 1.2 lathe: spin curve ``S(t) = [radius, height]`` around A->B."""
    revolve(S, A, B, min_t, max_t, grid_t, k, RGB, caps=False)


def sphere(center, r, k=10, color=None):
    """A sphere built from six curved square patches (a "quad sphere").

    ``k`` is the number of cells along the side of each patch, so the sphere
    has ``6 * k * k`` faces.  The quads stay nearly square everywhere, which
    is why this looks better than a globe made of latitude/longitude strips.
    """
    ellipsoid(center, [r, r, r], k, color)


def ellipsoid(center, radii, k=10, color=None):
    """Like :func:`sphere` but with a separate radius for X, Y and Z."""
    if not isinstance(radii, (list, tuple)):
        radii = [radii, radii, radii]
    sides = [((1, 0, 0), (0, 1, 0), (0, 0, 1)),
             ((-1, 0, 0), (0, 0, 1), (0, 1, 0)),
             ((0, 1, 0), (0, 0, 1), (1, 0, 0)),
             ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
             ((0, 0, 1), (1, 0, 0), (0, 1, 0)),
             ((0, 0, -1), (0, 1, 0), (1, 0, 0))]
    # Spreading the samples with tan() keeps the cells the same size.
    warp = [math.tan(math.pi / 4.0 * (2.0 * i / k - 1.0)) for i in range(k + 1)]
    M = Mesh()
    color = rgb(color)
    for n, u, v in sides:
        P = []
        for a in warp:
            row = []
            for b in warp:
                p = _unit((n[0] + u[0] * a + v[0] * b,
                           n[1] + u[1] * a + v[1] * b,
                           n[2] + u[2] * a + v[2] * b))
                row.append((center[0] + p[0] * radii[0],
                            center[1] + p[1] * radii[1],
                            center[2] + p[2] * radii[2]))
            P.append(row)
        _add_grid(M, P, color)
    _weld(M, 1e-9)
    _scene.extend(M)


def uvsphere(center, r, nu=32, nv=16, color=None):
    """A globe-style sphere: ``nu`` meridians by ``nv`` parallels."""
    def profile(t):
        return [r * math.sin(t), r * math.cos(t)]
    P, _ = _revolve_grid((center[0], center[1] - r, center[2]), (0, 1, 0),
                         [(r * math.sin(math.pi * i / nv),
                           r - r * math.cos(math.pi * i / nv))
                          for i in range(nv + 1)], nu)
    M = Mesh()
    _add_grid(M, P, rgb(color), wrap_v=True, flip=True)
    _weld(M, 1e-9)
    _drop_degenerate(M)
    _scene.extend(M)


def torus(center, R, r, nu=48, nv=24, color=None, axis=(0, 1, 0)):
    """A doughnut: tube radius ``r`` swept round a circle of radius ``R``."""
    u, v, w = _frame(axis)
    P = []
    for i in range(nu):
        a = 2.0 * math.pi * i / nu
        ring_centre = (center[0] + (u[0] * math.cos(a) + v[0] * math.sin(a)) * R,
                       center[1] + (u[1] * math.cos(a) + v[1] * math.sin(a)) * R,
                       center[2] + (u[2] * math.cos(a) + v[2] * math.sin(a)) * R)
        out = (u[0] * math.cos(a) + v[0] * math.sin(a),
               u[1] * math.cos(a) + v[1] * math.sin(a),
               u[2] * math.cos(a) + v[2] * math.sin(a))
        row = []
        for j in range(nv):
            b = 2.0 * math.pi * j / nv
            cb, sb = math.cos(b) * r, math.sin(b) * r
            row.append((ring_centre[0] + out[0] * cb + w[0] * sb,
                        ring_centre[1] + out[1] * cb + w[1] * sb,
                        ring_centre[2] + out[2] * cb + w[2] * sb))
        P.append(row)
    M = Mesh()
    _add_grid(M, P, rgb(color), wrap_u=True, wrap_v=True)
    _make_outward(M, 0)
    _scene.extend(M)


def _tube_body(A, B, r1, r2, k, color, cap_a, cap_b):
    """Shared engine behind cylinder / cone / frustum and their variants."""
    d = _sub(B, A)
    if _norm(d) < EPS:
        return Mesh()
    u, v, w = _frame(d)
    length = _norm(d)
    M = Mesh()
    color = rgb(color)
    ring_a = _ring(A, u, v, r1, k)
    ring_b = _ring(B, u, v, r2, k)
    if r1 < EPS:                       # cone standing on its point
        _fan(M, ring_b, A, color, flip=True)
    elif r2 < EPS:                     # cone with the point at B
        _fan(M, ring_a, B, color)
    else:
        _add_grid(M, [ring_a, ring_b], color, wrap_v=True, flip=True)
    if cap_a and r1 >= EPS:
        _fan(M, ring_a, A, color, flip=True)
    if cap_b and r2 >= EPS:
        _fan(M, ring_b, B, color)
    _weld(M, 1e-9)
    return M


def cylinder(A, B, r, k=24, color=None):
    """A closed cylinder from ``A`` to ``B``, radius ``r``, ``k`` sides."""
    _scene.extend(_tube_body(A, B, r, r, k, color, True, True))


def tube(A, B, r, k=24, color=None):
    """A cylinder with no lids -- just the side wall (old ``cylinder2``)."""
    _scene.extend(_tube_body(A, B, r, r, k, color, False, False))


def cup(A, B, r, k=24, color=None):
    """A cylinder closed at ``A`` only (old ``cylinder3``)."""
    _scene.extend(_tube_body(A, B, r, r, k, color, True, False))


def cone(A, B, r, k=24, color=None):
    """A closed cone: circular base of radius ``r`` at ``A``, tip at ``B``."""
    _scene.extend(_tube_body(A, B, r, 0.0, k, color, True, False))


def cone_open(A, B, r, k=24, color=None):
    """Only the slanted wall of a cone (old ``cone2``)."""
    _scene.extend(_tube_body(A, B, r, 0.0, k, color, False, False))


def frustum(A, B, r1, r2, k=24, color=None, caps=True):
    """A cone with its tip cut off: radius ``r1`` at ``A``, ``r2`` at ``B``."""
    _scene.extend(_tube_body(A, B, r1, r2, k, color, caps, caps))


def pipe(A, B, r_outer, r_inner, k=24, color=None):
    """A hollow tube -- a cylinder with a cylindrical hole down the middle."""
    d = _sub(B, A)
    u, v, w = _frame(d)
    M = Mesh()
    color = rgb(color)
    oa, ob = _ring(A, u, v, r_outer, k), _ring(B, u, v, r_outer, k)
    ia, ib = _ring(A, u, v, r_inner, k), _ring(B, u, v, r_inner, k)
    _add_grid(M, [oa, ob], color, wrap_v=True, flip=True)     # outside
    _add_grid(M, [ia, ib], color, wrap_v=True)                # inside
    _add_grid(M, [ia, oa], color, wrap_v=True, flip=True)     # ring at A
    _add_grid(M, [ib, ob], color, wrap_v=True)                # ring at B
    _emit(M)


def capsule(A, B, r, k=24, color=None):
    """A cylinder with a hemisphere on each end (a "pill")."""
    d = _sub(B, A)
    length = _norm(d)
    n = max(3, k // 3)
    profile = []
    for i in range(n + 1):                       # lower hemisphere
        a = math.pi / 2 * i / n
        profile.append((r * math.sin(a), r - r * math.cos(a)))
    for i in range(n + 1):                       # upper hemisphere
        a = math.pi / 2 * i / n
        profile.append((r * math.cos(a), r + length + r * math.sin(a)))
    start = _add3(A, _scale(_unit(d), -r))
    P, _ = _revolve_grid(start, d, [(p[0], p[1]) for p in profile], k)
    M = Mesh()
    _add_grid(M, P, rgb(color), wrap_v=True, flip=True)
    _weld(M, 1e-9)
    _drop_degenerate(M)
    _make_outward(M, 0)
    _scene.extend(M)


def arrow(A, B, r=0.05, color=None, k=16, head=0.25):
    """A shaft from ``A`` to ``B`` with a cone head -- good for vectors.

    ``head`` is the fraction of the length taken by the arrowhead.
    """
    d = _sub(B, A)
    n = _norm(d)
    if n < EPS:
        return
    joint = _add3(A, _scale(d, 1.0 - head))
    cylinder(A, joint, r, k, color)
    cone(joint, B, r * 2.4, k, color)


def helix(center, r, pitch, turns, k=200, thickness=0.1, sides=12, color=None,
          axis=(0, 1, 0)):
    """A spring / helical tube of ``turns`` turns around ``axis``."""
    u, v, w = _frame(axis)

    def path(t):
        a = 2.0 * math.pi * t
        return (center[0] + (u[0] * math.cos(a) + v[0] * math.sin(a)) * r + w[0] * pitch * t,
                center[1] + (u[1] * math.cos(a) + v[1] * math.sin(a)) * r + w[1] * pitch * t,
                center[2] + (u[2] * math.cos(a) + v[2] * math.sin(a)) * r + w[2] * pitch * t)

    curve(path, 0, turns, k, sides, thickness, color, False)


# ============================================================================
#  8. Coordinate axes
# ============================================================================

# Each capital letter is a few line segments in a unit square, so the axis
# labels cost five lines of code instead of a page of baked-in coordinates.
_GLYPHS = {
    "X": [((0, 0), (1, 1)), ((0, 1), (1, 0))],
    "Y": [((0, 1), (0.5, 0.5)), ((1, 1), (0.5, 0.5)), ((0.5, 0.5), (0.5, 0))],
    "Z": [((0, 1), (1, 1)), ((1, 1), (0, 0)), ((0, 0), (1, 0))],
}


def glyph(letter, origin, u, v, size=1.0, thickness=0.04, color=None):
    """Draw one of the letters X, Y, Z as thin bars in the ``u``/``v`` plane."""
    for (p, q) in _GLYPHS[letter.upper()]:
        a = (origin[0] + (u[0] * p[0] + v[0] * p[1]) * size,
             origin[1] + (u[1] * p[0] + v[1] * p[1]) * size,
             origin[2] + (u[2] * p[0] + v[2] * p[1]) * size)
        b = (origin[0] + (u[0] * q[0] + v[0] * q[1]) * size,
             origin[1] + (u[1] * q[0] + v[1] * q[1]) * size,
             origin[2] + (u[2] * q[0] + v[2] * q[1]) * size)
        cylinder(a, b, thickness, 6, color)


def axes(C=(0, 0, 0), length=4.0, width=0.03):
    """Draw the coordinate axes: X red, Y green, Z blue, each labelled."""
    h, w = float(length), float(width)
    for direction, col, letter in (((1, 0, 0), (255, 0, 0), "X"),
                                   ((0, 1, 0), (0, 255, 0), "Y"),
                                   ((0, 0, 1), (0, 0, 255), "Z")):
        end = _add3(C, _scale(direction, h))
        tip = _add3(C, _scale(direction, h + 0.7))
        cylinder(C, end, w, 9, col)
        cone(end, tip, 2 * w, 9, col)
    # All three labels stand in the XY plane so they read the same way round.
    glyph("X", _add3(C, (h + 0.35, 0.25, 0)), (1, 0, 0), (0, 1, 0), 0.6, 3 * w,
          (255, 0, 0))
    glyph("Y", _add3(C, (0.3, h + 0.35, 0)), (1, 0, 0), (0, 1, 0), 0.6, 3 * w,
          (0, 255, 0))
    glyph("Z", _add3(C, (0.1, 0.25, h + 0.5)), (1, 0, 0), (0, 1, 0), 0.6, 3 * w,
          (0, 0, 255))

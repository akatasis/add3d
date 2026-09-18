

# ============================================================================
#  7. Numbers, points and 2D profiles
# ============================================================================
# Small helpers that models need all the time: blend two values, keep a
# number in range, measure a distance, turn a point, cut the corners of a
# path, and ready-made cross-sections for ``extrude`` / ``sweep`` / ``prism``.

def lerp(a, b, t):
    """Blend from ``a`` (``t = 0``) to ``b`` (``t = 1``).

    Works for numbers and for points: ``lerp([0, 0, 0], [4, 2, 0], 0.5)``
    is ``[2, 1, 0]``.
    """
    if isinstance(a, (int, float)):
        return a + (b - a) * t
    return [a[i] + (b[i] - a[i]) * t for i in range(len(a))]


def clamp(x, lo=0.0, hi=1.0):
    """``x`` limited to the range ``lo .. hi``."""
    return lo if x < lo else (hi if x > hi else x)


def remap(x, a0, a1, b0, b1):
    """Map ``x`` from the range ``a0..a1`` onto the range ``b0..b1``.

    ``remap(t, 0, 10, -1, 1)`` turns a time 0..10 into -1..1.
    """
    if abs(a1 - a0) < EPS:
        return b0
    return b0 + (b1 - b0) * (x - a0) / float(a1 - a0)


def distance(a, b):
    """Distance between two points (2D or 3D)."""
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(len(a))))


def midpoint(a, b):
    """The point half way between ``a`` and ``b``."""
    return [(a[i] + b[i]) / 2.0 for i in range(len(a))]


def direction(a, b):
    """The unit vector pointing from ``a`` to ``b``."""
    d = [b[i] - a[i] for i in range(len(a))]
    n = math.sqrt(sum(c * c for c in d))
    return d if n < EPS else [c / n for c in d]


def rotate_point(p, axis, angle, P=(0, 0, 0)):
    """Turn a single point around an axis through ``P`` (Rodrigues).

    The same rotation :func:`rotate` applies to a whole mesh -- use it to
    aim a turret, place a hand on a clock or compute where a part will end
    up before building it::

        tip = add.rotate_point([3, 0, 0], [0, 1, 0], angle, pivot)
    """
    k = _unit(axis)
    cs, sn = math.cos(angle), math.sin(angle)
    v = _sub(p, P)
    kv = _cross(k, v)
    d = _dot(k, v) * (1.0 - cs)
    return [P[0] + v[0] * cs + kv[0] * sn + k[0] * d,
            P[1] + v[1] * cs + kv[1] * sn + k[1] * d,
            P[2] + v[2] * cs + kv[2] * sn + k[2] * d]


def shade(color, factor):
    """A darker (``factor < 1``) or lighter (``factor > 1``) version of a colour.

    ``shade("red", 0.5)`` is dark red; ``shade("red", 1.5)`` is pink-ish.
    """
    r, g, b = rgb(color)
    if factor <= 1.0:
        return (int(r * factor), int(g * factor), int(b * factor))
    t = min(1.0, factor - 1.0)
    return (int(r + (255 - r) * t), int(g + (255 - g) * t), int(b + (255 - b) * t))


def chaikin(points, rounds=2, closed=False):
    """Round the corners of a polyline by cutting them (Chaikin's algorithm).

    Every round replaces each corner by two points at 1/4 and 3/4 of its
    edges, so a square becomes an octagon, then a 16-gon, and quickly a
    circle.  Works for 2D and 3D points.  Use it to smooth a hand-drawn
    path before :func:`polyline` or :func:`sweep`.
    """
    pts = [list(p) for p in points]
    for _ in range(rounds):
        n = len(pts)
        out = []
        pairs = range(n) if closed else range(n - 1)
        for i in pairs:
            a, b = pts[i], pts[(i + 1) % n]
            out.append([a[j] * 0.75 + b[j] * 0.25 for j in range(len(a))])
            out.append([a[j] * 0.25 + b[j] * 0.75 for j in range(len(a))])
        if not closed:
            out = [pts[0]] + out + [pts[-1]]
        pts = out
    return pts


# -- 2D cross-sections -------------------------------------------------------
# All profiles are lists of [x, y] points listed counter-clockwise, ready for
# ``extrude``, ``sweep``, ``prism`` and ``loft``.

def profile_circle(r, k=32, phase=0.0):
    """``k`` points on a circle of radius ``r``."""
    return [[r * math.cos(phase + 2 * math.pi * i / k),
             r * math.sin(phase + 2 * math.pi * i / k)] for i in range(k)]


def profile_ellipse(a, b, k=32):
    """``k`` points on an ellipse with half-axes ``a`` and ``b``."""
    return [[a * math.cos(2 * math.pi * i / k), b * math.sin(2 * math.pi * i / k)]
            for i in range(k)]


def profile_polygon(n, r, phase=None):
    """A regular ``n``-gon with circumradius ``r`` (a flat side at the bottom)."""
    if phase is None:
        phase = -math.pi / 2.0 + math.pi / n
    return profile_circle(r, n, phase)


def profile_star(n, r_outer, r_inner, phase=None):
    """A star with ``n`` points, alternating between the two radii."""
    if phase is None:
        phase = math.pi / 2.0
    pts = []
    for i in range(2 * n):
        r = r_outer if i % 2 == 0 else r_inner
        a = phase + math.pi * i / n
        pts.append([r * math.cos(a), r * math.sin(a)])
    return pts


def profile_rect(w, h, r=0.0, k=4):
    """A ``w`` by ``h`` rectangle, with corners rounded by ``r`` if given."""
    x, y = w / 2.0, h / 2.0
    if r <= EPS:
        return [[-x, -y], [x, -y], [x, y], [-x, y]]
    r = min(r, x, y)
    pts = []
    corners = [(x - r, y - r, 0.0), (-x + r, y - r, math.pi / 2),
               (-x + r, -y + r, math.pi), (x - r, -y + r, 3 * math.pi / 2)]
    for cx, cy, a0 in corners:
        for i in range(k + 1):
            a = a0 + (math.pi / 2) * i / k
            pts.append([cx + r * math.cos(a), cy + r * math.sin(a)])
    return pts


def profile_gear(teeth, r, depth=None, k=2):
    """The outline of a gear: ``teeth`` teeth of height ``depth`` on radius ``r``.

    The result is a closed profile; ``add.prism(profile, thickness)`` makes
    the wheel and :func:`gear` does that for you.
    """
    if depth is None:
        depth = r * 0.2
    pts = []
    n = 4 * teeth
    for i in range(n):
        phase = i % 4
        a = 2 * math.pi * i / n
        if phase in (1, 2):
            rr = r + depth / 2.0
        else:
            rr = r - depth / 2.0
        pts.append([rr * math.cos(a), rr * math.sin(a)])
    return pts


# -- points to put things on ------------------------------------------------

def points_on_line(a, b, n):
    """``n`` points evenly spaced from ``a`` to ``b`` (both included)."""
    if n <= 1:
        return [list(a)]
    return [lerp(a, b, i / float(n - 1)) for i in range(n)]


def points_on_circle(center, r, n, axis=(0, 1, 0), phase=0.0):
    """``n`` points spread evenly on a circle in the plane normal to ``axis``."""
    u, v, w = _frame(axis)
    return [list(p) for p in _ring(center, u, v, r, n, phase)]


def points_on_helix(center, r, pitch, turns, n, axis=(0, 1, 0)):
    """``n`` points along a helix of ``turns`` turns climbing ``pitch`` per turn."""
    u, v, w = _frame(axis)
    out = []
    for i in range(n):
        t = turns * i / float(max(1, n - 1))
        a = 2 * math.pi * t
        out.append([center[j] + (u[j] * math.cos(a) + v[j] * math.sin(a)) * r
                    + w[j] * pitch * t for j in range(3)])
    return out


def points_on_spiral(center, r0, r1, turns, n, axis=(0, 1, 0), rise=0.0):
    """``n`` points along a flat spiral whose radius grows from ``r0`` to ``r1``.

    ``rise`` lifts the spiral along ``axis`` as it goes -- a vortex of beads
    or a spiral staircase in one call.
    """
    u, v, w = _frame(axis)
    out = []
    for i in range(n):
        t = i / float(max(1, n - 1))
        a = 2 * math.pi * turns * t
        r = r0 + (r1 - r0) * t
        out.append([center[j] + (u[j] * math.cos(a) + v[j] * math.sin(a)) * r
                    + w[j] * rise * t for j in range(3)])
    return out


def points_on_curve(path, t0, t1, n, closed=False):
    """``n`` points ``path(t)`` for ``t`` evenly spread over ``t0 .. t1``."""
    steps = n if closed else max(1, n - 1)
    return [list(path(t0 + (t1 - t0) * i / float(steps))) for i in range(n)]

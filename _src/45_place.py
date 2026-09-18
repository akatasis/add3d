

# ============================================================================
# 17. Placing parts: aim, scatter, line up
# ============================================================================
# The functions in the previous section make copies on a regular pattern.
# These put a part *somewhere in particular*: pointing along a direction,
# on the ground, at random spots on a landscape, or strung along a curve.

def aim(M, direction, axis=(0, 1, 0), P=(0, 0, 0)):
    """Turn a mesh so that its ``axis`` points along ``direction``.

    The rotation is the smallest one that does the job, about point ``P``.
    A cannon built pointing up (``axis=[0, 1, 0]``) is aimed at a target
    with ``add.aim(cannon, add.direction(pivot, target), P=pivot)``.
    """
    a, b = _unit(axis), _unit(direction)
    c = _cross(a, b)
    s, d = _norm(c), _dot(a, b)
    if s < 1e-12:
        if d > 0:
            return copy(M)
        return rotate(M, _perp(a), math.pi, P)
    return rotate(M, c, math.atan2(s, d), P)


def ground(M, y=0.0):
    """Move a mesh straight down (or up) so that its lowest point is at ``y``."""
    lo, hi = bbox(M)
    return move(M, [0.0, y - lo[1], 0.0])


def align(M, at=(0, 0, 0), anchor=(0, -1, 0)):
    """Move a mesh so that a chosen point of its bounding box lands on ``at``.

    ``anchor`` picks that point per axis: ``-1`` the minimum, ``0`` the
    middle, ``1`` the maximum.  The default ``(0, -1, 0)`` is "bottom
    centre", so ``add.align(house, [5, 0, 5])`` stands the house on the
    ground at (5, 5); ``anchor=(-1, -1, -1)`` puts its corner there.
    """
    lo, hi = bbox(M)
    shift = []
    for a in range(3):
        if anchor[a] < 0:
            p = lo[a]
        elif anchor[a] > 0:
            p = hi[a]
        else:
            p = (lo[a] + hi[a]) / 2.0
        shift.append(at[a] - p)
    return move(M, shift)


def random_points(n, lo, hi, seed=None, height=None):
    """``n`` random points in the box ``lo .. hi`` (each a 3-vector).

    With ``height(x, z)`` the Y coordinate is taken from that function
    instead, so the points lie *on* a landscape made with ``grid(...,
    height=...)``.  ``seed`` makes the result repeatable.
    """
    rnd = _random.Random(seed) if seed is not None else _random
    out = []
    for _ in range(n):
        x = rnd.uniform(lo[0], hi[0])
        z = rnd.uniform(lo[2], hi[2])
        y = height(x, z) if height is not None else rnd.uniform(lo[1], hi[1])
        out.append([x, y, z])
    return out


def scatter(M, points, seed=None, spin=True, scale=(1.0, 1.0), axis=(0, 1, 0)):
    """Copies of a mesh at every point, each turned and sized at random.

    The mesh should be built around the origin (its origin is what lands on
    the point).  ``spin`` turns each copy by a random angle about ``axis``;
    ``scale`` is the range of random size factors.  A forest::

        add.tree([0, 0, 0], 3)
        one = add.layer()
        spots = add.random_points(40, [-20, 0, -20], [20, 0, 20], seed=1, height=hills)
        add.mesh(add.scatter(one, spots, seed=1, scale=(0.7, 1.3)))
    """
    rnd = _random.Random(seed) if seed is not None else _random
    base = as_mesh(M)
    out = Mesh()
    for p in points:
        X = base
        s = rnd.uniform(scale[0], scale[1])
        if abs(s - 1.0) > EPS:
            X = zoom(X, s, (0, 0, 0))
        if spin:
            X = rotate(X, axis, rnd.uniform(0, 2 * math.pi))
        out.extend(move(X, p))
    return out


def along(M, path, n, t0=0.0, t1=1.0, axis=(0, 1, 0), closed=False, scale=None):
    """``n`` copies of a mesh strung along a curve, each turned to follow it.

    ``path`` is a function ``path(t)`` or a list of points.  The mesh's
    ``axis`` is aimed along the curve's direction at every copy (pass
    ``axis=None`` to keep the copies upright); ``scale`` is a number or a
    function ``scale(t)``.  Beads on a string, wagons on a track, stones on
    an arch::

        add.along(wagon, track, 12, 0, 1, axis=[1, 0, 0])
    """
    base = as_mesh(M)
    if callable(path):
        steps = n if closed else max(1, n - 1)
        ts = [t0 + (t1 - t0) * i / float(steps) for i in range(n)]
        pts = [tuple(path(t)) for t in ts]
        h = (t1 - t0) * 1e-4
        dirs = [_sub(path(t + h), path(t - h)) for t in ts]
    else:
        pts = [tuple(p) for p in path]
        n = len(pts)
        ts = [i / float(n if closed else max(1, n - 1)) for i in range(n)]
        dirs = []
        for i in range(n):
            a = pts[i - 1] if (i > 0 or closed) else pts[i]
            b = pts[(i + 1) % n] if (i < n - 1 or closed) else pts[i]
            dirs.append(_sub(b, a))
    out = Mesh()
    for p, t, d in zip(pts, ts, dirs):
        X = base
        if scale is not None:
            s = scale(t) if callable(scale) else scale
            X = zoom(X, s, (0, 0, 0))
        if axis is not None and _norm(d) > EPS:
            X = aim(X, d, axis)
        out.extend(move(X, p))
    return out

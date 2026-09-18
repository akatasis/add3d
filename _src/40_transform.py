

# ============================================================================
# 13. Measuring a mesh
# ============================================================================

def bbox(M=None):
    """``[[xmin, ymin, zmin], [xmax, ymax, zmax]]`` of a mesh."""
    M = as_mesh(M)
    if not M.V:
        return [[0, 0, 0], [0, 0, 0]]
    lo = [min(p[a] for p in M.V) for a in range(3)]
    hi = [max(p[a] for p in M.V) for a in range(3)]
    return [lo, hi]


def size(M=None):
    """The width, height and depth of a mesh."""
    lo, hi = bbox(M)
    return [hi[a] - lo[a] for a in range(3)]


def center(M=None):
    """The average of all vertices (what add.py 1.2 called the centre)."""
    M = as_mesh(M)
    if not M.V:
        return [0.0, 0.0, 0.0]
    n = float(len(M.V))
    return [sum(p[a] for p in M.V) / n for a in range(3)]


def middle(M=None):
    """The centre of the bounding box -- usually what you actually want."""
    lo, hi = bbox(M)
    return [(lo[a] + hi[a]) / 2.0 for a in range(3)]


def area(M=None):
    """Total surface area."""
    M = as_mesh(M)
    total = 0.0
    for f in M.F:
        if len(f) < 3:
            continue
        a = M.V[f[0]]
        for t in range(1, len(f) - 1):
            total += _norm(_cross(_sub(M.V[f[t]], a),
                                  _sub(M.V[f[t + 1]], a))) / 2.0
    return total


def volume(M=None):
    """Enclosed volume.  Meaningful only for a closed (watertight) mesh."""
    return _signed_volume(as_mesh(M), 0) / 6.0


# ============================================================================
# 14. Moving, turning and reshaping a mesh
# ============================================================================
# Every function here takes a mesh and returns a NEW mesh; the original is
# left alone.  That is what makes chains like
#     add.move(add.rotateY(M, a, [0, 0, 0]), [0, 3, 0])
# safe to write.

def _mapped(M, f, flip=False):
    """Apply point function ``f`` to a copy of the mesh."""
    M = as_mesh(M)
    out = Mesh([list(f(p)) for p in M.V],
               [list(reversed(x)) if flip else list(x) for x in M.F],
               list(M.C))
    return out


def move(M, V):
    """Shift a mesh by vector ``V``."""
    return _mapped(M, lambda p: (p[0] + V[0], p[1] + V[1], p[2] + V[2]))


def place(M, at, use_bbox=True):
    """Move a mesh so that its centre sits exactly at ``at``."""
    c = middle(M) if use_bbox else center(M)
    return move(M, [at[0] - c[0], at[1] - c[1], at[2] - c[2]])


def rotateX(M, angle, P=(0, 0, 0)):
    """Turn a mesh around the X axis through point ``P``."""
    cs, sn = math.cos(angle), math.sin(angle)

    def f(p):
        y, z = p[1] - P[1], p[2] - P[2]
        return (p[0], P[1] + y * cs - z * sn, P[2] + y * sn + z * cs)
    return _mapped(M, f)


def rotateY(M, angle, P=(0, 0, 0)):
    """Turn a mesh around the Y axis through point ``P``."""
    cs, sn = math.cos(angle), math.sin(angle)

    def f(p):
        x, z = p[0] - P[0], p[2] - P[2]
        return (P[0] + x * cs + z * sn, p[1], P[2] + z * cs - x * sn)
    return _mapped(M, f)


def rotateZ(M, angle, P=(0, 0, 0)):
    """Turn a mesh around the Z axis through point ``P``."""
    cs, sn = math.cos(angle), math.sin(angle)

    def f(p):
        x, y = p[0] - P[0], p[1] - P[1]
        return (P[0] + x * cs - y * sn, P[1] + x * sn + y * cs, p[2])
    return _mapped(M, f)


def rotate(M, axis, angle, P=(0, 0, 0)):
    """Turn a mesh by ``angle`` around any axis through ``P``.

    Uses Rodrigues' formula, so ``axis`` can point anywhere::

        M = add.rotate(M, [1, 1, 0], math.pi / 3, [0, 0, 0])
    """
    k = _unit(axis)
    cs, sn = math.cos(angle), math.sin(angle)

    def f(p):
        v = _sub(p, P)
        kv = _cross(k, v)
        d = _dot(k, v) * (1.0 - cs)
        return (P[0] + v[0] * cs + kv[0] * sn + k[0] * d,
                P[1] + v[1] * cs + kv[1] * sn + k[1] * d,
                P[2] + v[2] * cs + kv[2] * sn + k[2] * d)
    return _mapped(M, f)


def zoom(M, s, about=None):
    """Scale a mesh by factor ``s`` (about its own centre by default)."""
    c = center(M) if about is None else about
    return _mapped(M, lambda p: (c[0] + (p[0] - c[0]) * s,
                                 c[1] + (p[1] - c[1]) * s,
                                 c[2] + (p[2] - c[2]) * s), flip=(s < 0))


def stretch(M, s, about=None):
    """Scale by a different factor along each axis, ``s = [sx, sy, sz]``."""
    c = center(M) if about is None else about
    flip = (s[0] * s[1] * s[2]) < 0
    return _mapped(M, lambda p: (c[0] + (p[0] - c[0]) * s[0],
                                 c[1] + (p[1] - c[1]) * s[1],
                                 c[2] + (p[2] - c[2]) * s[2]), flip=flip)


def fit(M, target=1.0, about=None):
    """Scale a mesh so its largest dimension equals ``target``."""
    d = max(size(M))
    return zoom(M, (target / d) if d > EPS else 1.0, about)


def mirror(M, point=(0, 0, 0), normal=(1, 0, 0)):
    """Reflect a mesh in the plane through ``point`` with the given normal.

    The face winding is reversed too, so the reflection is not inside out.
    """
    n = _unit(normal)

    def f(p):
        d = 2.0 * _dot(_sub(p, point), n)
        return (p[0] - n[0] * d, p[1] - n[1] * d, p[2] - n[2] * d)
    return _mapped(M, f, flip=True)


def transform(M, matrix):
    """Apply a 3x3 or 4x4 matrix (given as a list of rows)."""
    m = matrix

    def f(p):
        x = m[0][0] * p[0] + m[0][1] * p[1] + m[0][2] * p[2]
        y = m[1][0] * p[0] + m[1][1] * p[1] + m[1][2] * p[2]
        z = m[2][0] * p[0] + m[2][1] * p[1] + m[2][2] * p[2]
        if len(m[0]) > 3:
            x += m[0][3]
            y += m[1][3]
            z += m[2][3]
        return (x, y, z)
    det = (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
           - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
           + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))
    return _mapped(M, f, flip=(det < 0))


def deform(M, f):
    """Bend a mesh with any function you like: ``f(p) -> new point``.

    The single most powerful function in the library::

        wave = add.deform(M, lambda p: [p[0], p[1] + math.sin(p[0]), p[2]])
    """
    return _mapped(M, lambda p: f(list(p)))


def twist(M, angle, axis=(0, 1, 0), P=(0, 0, 0)):
    """Rotate a mesh progressively along ``axis`` -- a corkscrew.

    ``angle`` is the turn applied per unit of distance along the axis.
    """
    k = _unit(axis)

    def f(p):
        h = _dot(_sub(p, P), k)
        a = angle * h
        cs, sn = math.cos(a), math.sin(a)
        v = _sub(p, P)
        kv = _cross(k, v)
        d = _dot(k, v) * (1.0 - cs)
        return (P[0] + v[0] * cs + kv[0] * sn + k[0] * d,
                P[1] + v[1] * cs + kv[1] * sn + k[1] * d,
                P[2] + v[2] * cs + kv[2] * sn + k[2] * d)
    return _mapped(M, f)


def taper(M, factor, axis=1, P=(0, 0, 0)):
    """Shrink (or grow) a mesh along ``axis``; ``axis`` is 0=X, 1=Y, 2=Z.

    ``factor`` is the extra scale gained per unit of distance, so
    ``taper(M, -0.2)`` makes the model 20% thinner for every unit it rises.
    """
    other = [a for a in range(3) if a != axis]

    def f(p):
        s = 1.0 + factor * (p[axis] - P[axis])
        q = list(p)
        for a in other:
            q[a] = P[a] + (p[a] - P[a]) * s
        return q
    return _mapped(M, f)


def bend(M, angle, axis=1, around=0, P=(0, 0, 0)):
    """Bend a mesh into an arc.

    Distance along ``axis`` becomes an angle turning about ``around``;
    ``angle`` is radians per unit of length.
    """
    third = 3 - axis - around

    def f(p):
        q = list(p)
        h = p[axis] - P[axis]
        a = angle * h
        if abs(angle) < EPS:
            return q
        r = 1.0 / angle
        d = p[third] - P[third]
        q[axis] = P[axis] + (r - d) * math.sin(a)
        q[third] = P[third] + r - (r - d) * math.cos(a)
        return q
    return _mapped(M, f)


def jitter(M, amount=0.05, seed=None):
    """Nudge every vertex a little at random -- an easy hand-made look."""
    r = _random if seed is None else _random.Random(seed)
    return _mapped(M, lambda p: (p[0] + r.uniform(-amount, amount),
                                 p[1] + r.uniform(-amount, amount),
                                 p[2] + r.uniform(-amount, amount)))


# ============================================================================
# 15. Colour
# ============================================================================

def color(M, RGB):
    """Paint the whole mesh one colour and return the painted copy."""
    M = as_mesh(M)
    c = rgb(RGB)
    return Mesh([list(p) for p in M.V], [list(f) for f in M.F],
                [c] * len(M.F))


#: Private handle on :func:`color`, for functions whose own parameter is
#: called ``color``.
_paint = color


def color_by(M, fn):
    """Colour every face according to where it is: ``fn(point) -> colour``.

    ``point`` is the centre of the face, so a rainbow by height is::

        M = add.color_by(M, lambda p: add.hsv(p[1] / 10.0))
    """
    M = as_mesh(M)
    out = M.copy()
    for i, f in enumerate(M.F):
        n = float(len(f))
        p = [sum(M.V[k][a] for k in f) / n for a in range(3)]
        out.C[i] = rgb(fn(p))
    return out


def color_gradient(M, a, b, axis=1):
    """Fade the mesh from colour ``a`` to colour ``b`` along one axis."""
    lo, hi = bbox(M)
    span = hi[axis] - lo[axis]
    if span < EPS:
        return color(M, a)
    return color_by(M, lambda p: gradient((p[axis] - lo[axis]) / span, a, b))


def color_random(M, seed=None):
    """Give every face its own random colour."""
    r = _random if seed is None else _random.Random(seed)
    M = as_mesh(M)
    out = M.copy()
    out.C = [(r.randint(0, 255), r.randint(0, 255), r.randint(0, 255))
             for _ in M.F]
    return out


# ============================================================================
# 16. Copies and patterns
# ============================================================================

def repeat(M, n, step):
    """Apply a transformation ``step(mesh, i)`` again and again, and merge.

    The general pattern maker -- every other array function below is a
    three-line wrapper around it::

        spiral = add.repeat(brick, 40,
                            lambda X, i: add.move(add.rotateY(X, i * 0.3), [0, i * 0.2, 0]))
    """
    out = Mesh()
    base = as_mesh(M)
    for i in range(n):
        out.extend(step(base, i))
    return out


def array_linear(M, step, n):
    """``n`` copies in a row, each moved a further ``step`` along."""
    return repeat(M, n, lambda X, i: move(X, [step[0] * i, step[1] * i,
                                              step[2] * i]))


def array_grid(M, steps, counts):
    """A 2D or 3D block of copies; ``steps`` and ``counts`` have 3 entries."""
    out = Mesh()
    base = as_mesh(M)
    for i in range(counts[0]):
        for j in range(counts[1]):
            for k in range(counts[2]):
                out.extend(move(base, [steps[0] * i, steps[1] * j,
                                       steps[2] * k]))
    return out


def array_radial(M, n, axis=(0, 1, 0), P=(0, 0, 0), angle=2.0 * math.pi,
                 rise=0.0):
    """``n`` copies arranged around an axis; ``rise`` makes it a spiral stair."""
    return repeat(M, n, lambda X, i: move(
        rotate(X, axis, angle * i / float(n), P),
        _scale(_unit(axis), rise * i)))


def array_mirror(M, point=(0, 0, 0), normal=(1, 0, 0)):
    """The mesh together with its mirror image."""
    return merge([M, mirror(M, point, normal)])

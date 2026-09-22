

# ============================================================================
# 15. Measuring a mesh
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


#: Private handle on :func:`center`, for functions whose own parameter is
#: called ``center``.
_centroid = center


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
# 16. Moving, turning and reshaping a mesh
# ============================================================================
# Every function here takes a mesh and returns a NEW mesh; the original is
# left alone.  That is what makes chains like
#     add.move(add.rotateY(M, a, [0, 0, 0]), [0, 3, 0])
# safe to write.

def _mapped(M, f, flip=False):
    """Apply point function ``f`` to a copy of the mesh."""
    M = as_mesh(M)
    UV = None
    if M.UV is not None:
        UV = [None if t is None else (list(reversed(t)) if flip else list(t))
              for t in M.UV]
    out = Mesh([list(f(p)) for p in M.V],
               [list(reversed(x)) if flip else list(x) for x in M.F],
               list(M.C), UV)
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
# 17. Colour
# ============================================================================

def color(M, RGB):
    """Paint the whole mesh one colour and return the painted copy."""
    M = as_mesh(M)
    c = rgb(RGB)
    out = M.copy()
    out.C = [c] * len(M.F)
    return out


def opacity(M, alpha):
    """A copy of the mesh with every face made see-through: ``alpha`` is the
    opacity, 0 invisible, 1 solid (which also removes any transparency).

    Colours and textures are kept; the opacity goes into the ``.mtl`` file
    of an ``.obj`` model.  For one colour at a time use :func:`transparent`::

        glass = add.opacity(add.make(add.box, [0, 0, 0], 2, "sky"), 0.3)
    """
    M = as_mesh(M)
    out = M.copy()
    out.C = [rgb((c[0], c[1], c[2], alpha) + tuple(c[4:5])) for c in M.C]
    return out


#: Private handle on :func:`color`, for functions whose own parameter is
#: called ``color``.
_paint = color


def texture(M, image, mapping="box", scale=1.0, color="white", offset=(0, 0)):
    """Wrap an image around a mesh and return the textured copy.

    ``image`` is the file name of a picture (``.png`` or ``.jpg``) that will
    sit next to the ``.obj`` -- put both, with the ``.mtl``, in one zip for
    Sketchfab.  The mesh remembers a texture coordinate for every corner,
    worked out from the ``mapping``:

    * ``"box"`` (default): each face is projected along its dominant axis,
      so the picture repeats every ``scale`` units on every side of a box;
    * ``"xy"``, ``"xz"``, ``"yz"``: one flat projection for all faces;
    * ``"fit"``: the picture stretched once over the mesh, seen from the front
      (XY), whatever its size;
    * ``"sphere"`` / ``"cylinder"``: wrapped around the mesh's centre, with
      ``scale`` copies around;
    * or your own function ``mapping(point, normal) -> (u, v)``.

    ``color`` tints the picture (white shows it as it is) and keeps any
    transparency the faces had.  Apply textures last: transforms, ``clean``
    and ``merge`` keep them, but booleans, subdivision and ``solidify``
    rebuild the faces and drop them.  ``.off`` files cannot hold textures;
    ``.obj`` + ``.mtl`` can (``map_Kd``)::

        add.write_png("bricks.png", rows)                   # or any picture
        wall = add.texture(add.make(add.cuboid, [0, 0, 0], [4, 2, 0.3]),
                           "bricks.png", "box", scale=1.0)
        add.mesh(wall)
        add.save("house.obj")
    """
    M = as_mesh(M)
    lo, hi = bbox(M)
    mid = [(lo[a] + hi[a]) / 2.0 for a in range(3)]
    span = [max(hi[a] - lo[a], EPS) for a in range(3)]
    ox, oy = offset[0], offset[1]
    s = float(scale) if scale else 1.0

    def planar(i, j):
        return lambda p, n: ((p[i] - ox) / s, (p[j] - oy) / s)

    if callable(mapping):
        fn = mapping
    elif mapping == "box":
        flat = {0: planar(2, 1), 1: planar(0, 2), 2: planar(0, 1)}

        def fn(p, n):
            axis = max(range(3), key=lambda a: abs(n[a]))
            return flat[axis](p, n)
    elif mapping in ("xy", "xz", "yz"):
        fn = {"xy": planar(0, 1), "xz": planar(0, 2), "yz": planar(2, 1)}[mapping]
    elif mapping == "fit":
        def fn(p, n):
            return ((p[0] - lo[0]) / span[0], (p[1] - lo[1]) / span[1])
    elif mapping == "sphere":
        def fn(p, n):
            d = _unit(_sub(p, mid))
            return ((math.atan2(d[2], d[0]) / (2 * math.pi) + 0.5) * s,
                    math.asin(max(-1.0, min(1.0, d[1]))) / math.pi + 0.5)
    elif mapping == "cylinder":
        def fn(p, n):
            return ((math.atan2(p[2] - mid[2], p[0] - mid[0]) / (2 * math.pi)
                     + 0.5) * s, (p[1] - lo[1]) / span[1])
    else:
        raise ValueError("unknown texture mapping: %r" % (mapping,))

    out = M.copy()
    out.UV = []
    tint = rgb(color) if color is not None else None
    for i, f in enumerate(M.F):
        n = _unit(_face_normal(M, f))
        uv = [tuple(fn(M.V[k], n)) for k in f]
        if mapping in ("sphere", "cylinder"):          # mend the seam
            us = [t[0] for t in uv]
            if max(us) - min(us) > 0.5 * s:
                uv = [(t[0] + s if t[0] < (min(us) + max(us)) / 2.0 else t[0], t[1])
                      for t in uv]
        out.UV.append(uv)
        base = tint if tint is not None else M.C[i]
        alpha = M.C[i][3] if len(M.C[i]) > 3 else 1.0
        out.C[i] = rgb((base[0], base[1], base[2], alpha, image))
    return out


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


def palette(M=None):
    """The distinct colours of a mesh, most used first, as
    ``[(colour, number of faces), ...]``."""
    M = as_mesh(M)
    count = {}
    for c in M.C:
        count[c] = count.get(c, 0) + 1
    return sorted(count.items(), key=lambda item: (-item[1], item[0]))


def limit_colors(M, n=50):
    """Reduce a mesh to at most ``n`` distinct colours and return the copy.

    Every colour in an ``.obj`` file becomes a *material*, and Sketchfab
    merges materials beyond its limit of 100 (so keep to 50 to be safe).
    Gradients and ``color_by`` paint jobs easily produce thousands of
    shades; this groups similar shades together (median-cut quantisation,
    weighted by how many faces use each shade) and replaces each group by
    its average, so the picture hardly changes::

        model = add.limit_colors(add.layer(), 50)
        add.save("model.obj", model)
    """
    M = as_mesh(M)
    counts = {}
    for c in M.C:
        if len(c) == 3:                       # transparent and textured
            counts[c] = counts.get(c, 0) + 1  # materials are left alone
    if len(counts) <= n:
        return M.copy()
    boxes = [list(counts.items())]
    while len(boxes) < n:
        # Split the box whose colours spread the most (weighted by use).
        best, best_span, best_axis = None, -1, 0
        for b in boxes:
            if len(b) < 2:
                continue
            for axis in range(3):
                span = max(c[axis] for c, w in b) - min(c[axis] for c, w in b)
                if span > best_span:
                    best, best_span, best_axis = b, span, axis
        if best is None:
            break
        best.sort(key=lambda item: item[0][best_axis])
        total = sum(w for c, w in best)
        acc, cut = 0, 0
        for cut in range(len(best) - 1):
            acc += best[cut][1]
            if acc * 2 >= total:
                break
        boxes.remove(best)
        boxes.append(best[:cut + 1])
        boxes.append(best[cut + 1:])
    remap = {}
    for b in boxes:
        total = float(sum(w for c, w in b))
        mean = tuple(int(round(sum(c[a] * w for c, w in b) / total))
                     for a in range(3))
        for c, w in b:
            remap[c] = mean
    out = M.copy()
    out.C = [remap.get(c, c) for c in M.C]
    return out


# ============================================================================
# 18. Copies and patterns
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



# ============================================================================
#  9. Parametric surfaces
# ============================================================================

def parametric(S, min_u, max_u, grid_u, min_v, max_v, grid_v, RGB=None,
               wrap_u=False, wrap_v=False, flip=False, thickness=0.0,
               double_sided=False, color=None):
    """The heart of the library: draw the surface ``S(u, v) -> [x, y, z]``.

    ``grid_u`` and ``grid_v`` say how many cells to use in each direction::

        def torus(u, v):
            return [(5 + math.cos(u)) * math.cos(v),
                    math.sin(u),
                    (5 + math.cos(u)) * math.sin(v)]
        add.parametric(torus, 0, 2 * math.pi, 40, 0, 2 * math.pi, 80, "gold")

    Extras beyond add.py 1.2:

    ``wrap_u`` / ``wrap_v``
        Join the last row/column back to the first, so a closed surface has no
        seam and no duplicated vertices.
    ``thickness``
        Give the sheet a real thickness, turning it into a solid shell.  This
        is the cure for a surface that looks black from one side: a solid has
        no wrong side.
    ``double_sided``
        Cheaper alternative -- keep the sheet infinitely thin but add a copy
        of every face pointing the other way.
    ``flip``
        Turn the surface inside out.
    """
    color = rgb(RGB if RGB is not None else color)
    nu = grid_u if wrap_u else grid_u + 1
    nv = grid_v if wrap_v else grid_v + 1
    P = []
    for i in range(nu):
        u = min_u + (max_u - min_u) * i / float(grid_u)
        row = []
        for j in range(nv):
            v = min_v + (max_v - min_v) * j / float(grid_v)
            p = S(u, v)
            row.append((p[0], p[1], p[2]))
        P.append(row)
    M = Mesh()
    _add_grid(M, P, color, wrap_u=wrap_u, wrap_v=wrap_v, flip=flip)
    if thickness:
        M = solidify(M, thickness)
    elif double_sided:
        M = two_sided(M)
    _scene.extend(M)


def two_sided(M=None):
    """Return a copy of ``M`` in which every face also exists reversed.

    Use it when a thin surface disappears or turns black when seen from
    behind.  The polygon count doubles.
    """
    M = as_mesh(M)
    out = M.copy()
    for f, c in zip(M.F, M.C):
        out.add_face(list(reversed(f)), c)
    return out


def solidify(M=None, thickness=0.1, both_ways=True):
    """Give a thin surface a real thickness and return the closed solid.

    Every vertex is pushed along the average normal of the faces around it;
    the open border is then stitched with a wall, so the result is watertight
    and lit correctly from every angle.
    """
    M = as_mesh(M)
    normals = _vertex_normals(M)
    n = len(M.V)
    out = Mesh()
    up = thickness / 2.0 if both_ways else thickness
    down = -thickness / 2.0 if both_ways else 0.0
    for i, p in enumerate(M.V):
        nrm = normals[i]
        out.add_vertex((p[0] + nrm[0] * up, p[1] + nrm[1] * up,
                        p[2] + nrm[2] * up))
    for i, p in enumerate(M.V):
        nrm = normals[i]
        out.add_vertex((p[0] + nrm[0] * down, p[1] + nrm[1] * down,
                        p[2] + nrm[2] * down))
    for f, c in zip(M.F, M.C):
        out.add_face(f, c)                                  # outer shell
        out.add_face([i + n for i in reversed(f)], c)       # inner shell
    # Stitch the boundary: any edge used by exactly one face is on the border.
    # The wall runs outer -> inner -> inner -> outer so that it faces outwards.
    for (a, b), c in _boundary_edges(M).items():
        out.add_face([a, a + n, b + n, b], c)
    return out


def _vertex_normals(M):
    """Area-weighted average normal at every vertex."""
    acc = [[0.0, 0.0, 0.0] for _ in M.V]
    for f in M.F:
        if len(f) < 3:
            continue
        nrm = _face_normal(M, f)
        for i in f:
            acc[i][0] += nrm[0]
            acc[i][1] += nrm[1]
            acc[i][2] += nrm[2]
    out = []
    for a in acc:
        out.append(_unit(a) if _norm(a) > EPS else (0.0, 1.0, 0.0))
    return out


def _face_normal(M, f):
    """Newell's normal -- works for any polygon, convex or not, and is
    numerically stable for nearly-degenerate faces."""
    nx = ny = nz = 0.0
    n = len(f)
    for i in range(n):
        a = M.V[f[i]]
        b = M.V[f[(i + 1) % n]]
        nx += (a[1] - b[1]) * (a[2] + b[2])
        ny += (a[2] - b[2]) * (a[0] + b[0])
        nz += (a[0] - b[0]) * (a[1] + b[1])
    return (nx, ny, nz)


def _boundary_edges(M):
    """``{(a, b): colour}`` for every edge that belongs to just one face."""
    seen = {}
    for f, c in zip(M.F, M.C):
        n = len(f)
        for i in range(n):
            a, b = f[i], f[(i + 1) % n]
            key = (a, b) if a < b else (b, a)
            if key in seen:
                seen[key] = None
            else:
                seen[key] = (a, b, c)
    out = {}
    for value in seen.values():
        if value is not None:
            out[(value[0], value[1])] = value[2]
    return out


# ============================================================================
# 10. Curves, sweeps and lofts -- "copy, turn, stretch a cross-section"
# ============================================================================

def _rmf(points, closed=False):
    """Rotation-minimising frames along a polyline (double-reflection method).

    Returns ``(tangents, normals)``.  Unlike the textbook Frenet frame this
    never spins wildly at an inflection point, so swept shapes do not twist
    on their own.
    """
    n = len(points)
    tangents = []
    for i in range(n):
        if closed:
            a, b = points[(i - 1) % n], points[(i + 1) % n]
        else:
            a = points[i - 1] if i > 0 else points[i]
            b = points[i + 1] if i < n - 1 else points[i]
        t = _unit(_sub(b, a))
        if _norm(t) < EPS:
            t = tangents[-1] if tangents else (0.0, 0.0, 1.0)
        tangents.append(t)
    normals = [_perp(tangents[0])]
    for i in range(n - 1):
        v1 = _sub(points[i + 1], points[i])
        c1 = _dot(v1, v1)
        if c1 < EPS:
            normals.append(normals[-1])
            continue
        rL = _sub(normals[i], _scale(v1, 2.0 * _dot(v1, normals[i]) / c1))
        tL = _sub(tangents[i], _scale(v1, 2.0 * _dot(v1, tangents[i]) / c1))
        v2 = _sub(tangents[i + 1], tL)
        c2 = _dot(v2, v2)
        if c2 < EPS:
            normals.append(_unit(rL))
        else:
            normals.append(_unit(_sub(rL, _scale(v2, 2.0 * _dot(v2, rL) / c2))))
    if closed and n > 1:
        # Cancel the leftover twist by spreading it over the whole loop.
        t = tangents[0]
        u0, v0 = normals[0], _cross(tangents[0], normals[0])
        last = normals[-1]
        angle = math.atan2(_dot(last, v0), _dot(last, u0))
        for i in range(n):
            a = -angle * i / float(n)
            u = normals[i]
            v = _cross(tangents[i], u)
            normals[i] = _add3(_scale(u, math.cos(a)), _scale(v, math.sin(a)))
    return tangents, normals


def _sweep_profile(points, tangents, normals, profile, scale=None, twist=None):
    """Place a 2D ``profile`` at every point of a path -> grid of 3D points."""
    P = []
    n = len(points)
    for i in range(n):
        t = i / float(n - 1) if n > 1 else 0.0
        u = normals[i]
        v = _cross(tangents[i], u)
        s = scale(t) if callable(scale) else (1.0 if scale is None else scale)
        a = twist(t) if callable(twist) else (0.0 if twist is None else twist * t)
        ca, sa = math.cos(a), math.sin(a)
        c = points[i]
        row = []
        for p in profile:
            x, y = p[0] * s, p[1] * s
            x, y = x * ca - y * sa, x * sa + y * ca
            row.append((c[0] + u[0] * x + v[0] * y,
                        c[1] + u[1] * x + v[1] * y,
                        c[2] + u[2] * x + v[2] * y))
        P.append(row)
    return P


def sweep(profile, path, t0=0.0, t1=1.0, steps=100, color=None, closed=False,
          scale=None, twist=None, caps=True):
    """Slide a 2D cross-section along a 3D path -- the general shape maker.

    ``profile`` is a closed list of ``[x, y]`` points, ``path(t)`` returns a
    3D point.  ``scale`` and ``twist`` may be numbers or functions of
    ``t`` in 0..1, which is how you get a shape that grows and turns as it
    goes::

        square = [[-1, -1], [1, -1], [1, 1], [-1, 1]]
        add.sweep(square, lambda t: [0, t, 0], 0, 10, 60, "orange",
                  scale=lambda t: 1 - 0.7 * t, twist=3 * math.pi)

    Set ``closed=True`` when the path returns to its start (a ring).
    """
    n = steps if closed else steps + 1
    points = []
    for i in range(n):
        t = t0 + (t1 - t0) * i / float(steps)
        p = path(t)
        points.append((p[0], p[1], p[2]))
    tangents, normals = _rmf(points, closed)
    P = _sweep_profile(points, tangents, normals, profile, scale, twist)
    M = Mesh()
    _add_grid(M, P, rgb(color), wrap_u=closed, wrap_v=True, flip=True)
    if caps and not closed:
        M.add_polygon(P[0][::-1], color)
        M.add_polygon(P[-1], color)
        _weld(M, 1e-9)
        _make_outward(M, 0)
    _emit(M)


def curve(P, min_t, max_t, grid_t, k=16, r=0.1, RGB=None, isConnected=False,
          color=None):
    """Draw a 3D parametric curve as a round tube of radius ``r``.

    ``r`` may be a function ``r(t)`` for a tube that swells and narrows.
    ``isConnected=True`` closes the tube into a loop without a seam.
    """
    color = rgb(RGB if RGB is not None else color)
    n = grid_t if isConnected else grid_t + 1
    ts, points = [], []
    for i in range(n):
        t = min_t + (max_t - min_t) * i / float(grid_t)
        ts.append(t)
        p = P(t)
        points.append((p[0], p[1], p[2]))
    tangents, normals = _rmf(points, isConnected)
    circle_profile = [(math.cos(2 * math.pi * j / k), math.sin(2 * math.pi * j / k))
                      for j in range(k)]
    grid_points = []
    for i in range(len(points)):
        radius = r(ts[i]) if callable(r) else r
        u = normals[i]
        v = _cross(tangents[i], u)
        c = points[i]
        row = []
        for (cx, cy) in circle_profile:
            x, y = cx * radius, cy * radius
            row.append((c[0] + u[0] * x + v[0] * y,
                        c[1] + u[1] * x + v[1] * y,
                        c[2] + u[2] * x + v[2] * y))
        grid_points.append(row)
    M = Mesh()
    _add_grid(M, grid_points, color, wrap_u=isConnected, wrap_v=True, flip=True)
    if not isConnected:
        _fan(M, grid_points[0], points[0], color, flip=True)
        _fan(M, grid_points[-1], points[-1], color)
    _emit(M)


def extrude(profile, direction=(0, 1, 0), color=None, steps=1, twist=0.0,
            scale=1.0, center=(0, 0, 0), caps=True):
    """Pull a 2D shape out into 3D, optionally turning and tapering as it goes.

    This is the "copy the cross-section, move it, rotate it, stretch it"
    construction in one call::

        star = [[math.cos(a) * (1 if i % 2 else 0.45),
                 math.sin(a) * (1 if i % 2 else 0.45)]
                for i, a in enumerate(...)]
        add.extrude(star, [0, 4, 0], "gold", steps=60, twist=math.pi,
                    scale=lambda t: 1 - 0.6 * t)
    """
    def path(t):
        return (center[0] + direction[0] * t,
                center[1] + direction[1] * t,
                center[2] + direction[2] * t)
    sweep(profile, path, 0.0, 1.0, max(1, steps), color, False, scale, twist,
          caps)


def loft(sections, color=None, closed=False, caps=True, flip=False):
    """Skin a surface over a list of cross-sections (each a ring of 3D points).

    Every section must have the same number of points.  This is the most
    direct way to build a shape from slices you have computed yourself.
    """
    M = Mesh()
    _add_grid(M, [list(s) for s in sections], rgb(color), wrap_u=closed,
              wrap_v=True, flip=not flip)
    if caps and not closed:
        M.add_polygon(list(sections[0])[::-1], color)
        M.add_polygon(list(sections[-1]), color)
        _weld(M, 1e-9)
        _make_outward(M, 0)
    _emit(M)


def ribbon(path, t0, t1, steps, width, color=None, closed=False, twist=None,
           thickness=0.0):
    """A flat band following a 3D path -- like a strip of paper.

    With ``thickness`` it becomes a solid bar instead of a zero-thickness
    sheet, so both sides are lit.
    """
    half = width / 2.0
    profile = [(-half, 0.0), (half, 0.0)]
    n = steps if closed else steps + 1
    points = []
    for i in range(n):
        t = t0 + (t1 - t0) * i / float(steps)
        p = path(t)
        points.append((p[0], p[1], p[2]))
    tangents, normals = _rmf(points, closed)
    P = _sweep_profile(points, tangents, normals, profile, None, twist)
    M = Mesh()
    _add_grid(M, P, rgb(color), wrap_u=closed)
    if thickness:
        M = solidify(M, thickness)
    else:
        M = two_sided(M)
    _scene.extend(M)


def circle(A, B, r, k=24, RGB=None, color=None):
    """add.py 1.2 disc: a filled circle centred at ``A``, facing ``B``."""
    disc(A, B, r, k, RGB if RGB is not None else color)

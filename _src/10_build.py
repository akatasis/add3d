

# ============================================================================
#  4. Building blocks used by every shape below
# ============================================================================

def _add_grid(M, P, color, wrap_u=False, wrap_v=False, flip=False):
    """Turn a 2D array of points ``P[i][j]`` into a quad patch.

    ``wrap_u`` / ``wrap_v`` close the patch into a tube or a torus.
    ``flip`` reverses the winding (makes the patch face the other way).
    ``color`` is one colour, or a function ``paint(i, j)`` giving the colour
    of cell ``(i, j)``.  This one helper is behind ``parametric``,
    ``revolve``, ``sweep``, ``loft``, ``sphere``, ``torus`` and ``tube``.
    """
    nu, nv = len(P), len(P[0])
    base = len(M.V)
    for row in P:
        for p in row:
            M.add_vertex(p)
    paint = color if callable(color) else None
    if paint is None:
        color = rgb(color)
    steps_u = nu if wrap_u else nu - 1
    steps_v = nv if wrap_v else nv - 1
    for i in range(steps_u):
        i2 = (i + 1) % nu
        for j in range(steps_v):
            j2 = (j + 1) % nv
            a = base + i * nv + j
            b = base + i2 * nv + j
            c = base + i2 * nv + j2
            d = base + i * nv + j2
            quad = [a, b, c, d] if not flip else [d, c, b, a]
            M.add_face(quad, rgb(paint(i, j)) if paint else color)


def _ring(center, u, v, r, k, phase=0.0):
    """``k`` points on a circle of radius ``r`` around ``center``.

    ``u`` and ``v`` are the two unit vectors spanning the circle's plane.
    """
    pts = []
    for i in range(k):
        a = phase + 2.0 * math.pi * i / k
        cs, sn = math.cos(a) * r, math.sin(a) * r
        pts.append((center[0] + u[0] * cs + v[0] * sn,
                    center[1] + u[1] * cs + v[1] * sn,
                    center[2] + u[2] * cs + v[2] * sn))
    return pts


def _fan(M, points, apex, color, flip=False, closed=True):
    """Close a ring of points with a triangle fan meeting at ``apex``.

    With ``closed=False`` the points form an open arc (a wedge lid) and no
    triangle is drawn between the last point and the first.
    """
    base = len(M.V)
    for p in points:
        M.add_vertex(p)
    tip = M.add_vertex(apex)
    n = len(points)
    paint = color if callable(color) else None
    if paint is None:
        color = rgb(color)
    for i in range(n if closed else n - 1):
        j = (i + 1) % n
        tri = [base + i, base + j, tip] if not flip else [base + j, base + i, tip]
        M.add_face(tri, rgb(paint(i)) if paint else color)


def _signed_volume(M, first_face=0):
    """Six times the signed volume of faces ``first_face..end``.

    Positive means the faces are wound outward.  Used to make sure every
    closed primitive in this library faces the right way.
    """
    total = 0.0
    for f in M.F[first_face:]:
        if len(f) < 3:
            continue
        a = M.V[f[0]]
        for t in range(1, len(f) - 1):
            b, c = M.V[f[t]], M.V[f[t + 1]]
            total += (a[0] * (b[1] * c[2] - b[2] * c[1])
                      - a[1] * (b[0] * c[2] - b[2] * c[0])
                      + a[2] * (b[0] * c[1] - b[1] * c[0]))
    return total


def _make_outward(M, first_face):
    """Flip faces ``first_face..end`` if they came out inside-out."""
    if _signed_volume(M, first_face) < 0:
        for i in range(first_face, len(M.F)):
            M.F[i].reverse()


def _grid_solid(origin, sx, sy, sz, filled, color):
    """Surface of a solid described on a rectangular grid of cells.

    ``sx``/``sy``/``sz`` are lists of cell sizes along each axis and
    ``filled(i, j, k)`` says whether cell ``(i, j, k)`` is material.  Only the
    faces between material and air are emitted, so the result is watertight
    and has no hidden geometry.  ``color`` may be a function ``(i, j, k)``.
    :func:`frame`, :func:`voxels`, :func:`pixels` and :func:`heightmap` are
    all thin wrappers around this.
    """
    nx, ny, nz = len(sx), len(sy), len(sz)
    # Coordinates of every grid line.
    X = [origin[0]]
    for s in sx:
        X.append(X[-1] + s)
    Y = [origin[1]]
    for s in sy:
        Y.append(Y[-1] + s)
    Z = [origin[2]]
    for s in sz:
        Z.append(Z[-1] + s)

    M = Mesh()
    index = {}

    def point(i, j, k):
        key = (i, j, k)
        if key not in index:
            index[key] = M.add_vertex((X[i], Y[j], Z[k]))
        return index[key]

    def solid(i, j, k):
        if 0 <= i < nx and 0 <= j < ny and 0 <= k < nz:
            return bool(filled(i, j, k))
        return False

    paint = color if callable(color) else None
    if paint is None:
        color = rgb(color)
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                if not solid(i, j, k):
                    continue
                if paint is not None:
                    color = rgb(paint(i, j, k))
                if not solid(i - 1, j, k):          # -X wall
                    M.add_face([point(i, j, k), point(i, j, k + 1),
                                point(i, j + 1, k + 1), point(i, j + 1, k)], color)
                if not solid(i + 1, j, k):          # +X wall
                    M.add_face([point(i + 1, j, k), point(i + 1, j + 1, k),
                                point(i + 1, j + 1, k + 1), point(i + 1, j, k + 1)], color)
                if not solid(i, j - 1, k):          # -Y wall
                    M.add_face([point(i, j, k), point(i + 1, j, k),
                                point(i + 1, j, k + 1), point(i, j, k + 1)], color)
                if not solid(i, j + 1, k):          # +Y wall
                    M.add_face([point(i, j + 1, k), point(i, j + 1, k + 1),
                                point(i + 1, j + 1, k + 1), point(i + 1, j + 1, k)], color)
                if not solid(i, j, k - 1):          # -Z wall
                    M.add_face([point(i, j, k), point(i, j + 1, k),
                                point(i + 1, j + 1, k), point(i + 1, j, k)], color)
                if not solid(i, j, k + 1):          # +Z wall
                    M.add_face([point(i, j, k + 1), point(i + 1, j, k + 1),
                                point(i + 1, j + 1, k + 1), point(i, j + 1, k + 1)], color)
    return M


def _emit(M, tol=1e-9):
    """Add a freshly built primitive to the scene, welding its seams first.

    Shapes are assembled from several patches (a wall plus two lids, say) and
    each patch generates its own copy of the shared rim.  Welding here means
    every primitive leaves the factory watertight.
    """
    _weld(M, tol)
    _scene.extend(M)


# ============================================================================
#  5. Flat shapes
# ============================================================================

def polygon(points, color=None):
    """One flat face through the given 3D points (any number of corners).

    The corners must be listed counter-clockwise as seen from the side you
    want to be the outside.
    """
    _scene.add_polygon(points, color)


def triangle(a, b, c, color=None):
    """A single triangle."""
    _scene.add_polygon([a, b, c], color)


def quad(a, b, c, d, color=None):
    """A single quadrilateral."""
    _scene.add_polygon([a, b, c, d], color)


def disc(center, normal, r, k=32, color=None):
    """A filled circle of radius ``r`` at ``center``, facing ``normal``.

    ``normal`` may be given either as a direction or as a second point --
    ``disc(A, B, ...)`` puts the disc at ``A`` facing ``B``, which is how the
    old :func:`circle` worked.
    """
    d = _sub(normal, center)
    if _norm(d) < EPS:
        d = normal
    u, v, w = _frame(d)
    M = Mesh()
    _fan(M, _ring(center, u, v, r, k), center, rgb(color))
    _scene.extend(M)


def ring(center, normal, r_outer, r_inner, k=32, color=None):
    """A flat annulus (a disc with a hole)."""
    d = _sub(normal, center)
    if _norm(d) < EPS:
        d = normal
    u, v, w = _frame(d)
    outer = _ring(center, u, v, r_outer, k)
    inner = _ring(center, u, v, r_inner, k)
    M = Mesh()
    _add_grid(M, [inner, outer], rgb(color), wrap_v=True)
    _scene.extend(M)


def grid(center, size, nx=10, nz=10, color=None, height=None, thickness=0.0):
    """A flat (or, with ``height(x, z)``, a hilly) rectangular patch in XZ.

    ``size`` is ``[width_x, depth_z]``.  ``height`` is an optional function
    returning the Y coordinate, and ``color`` may be a function ``(x, z)`` so
    that a landscape can be painted by position or by height::

        add.grid([0, 0, 0], [10, 10], 40, 40,
                 color=lambda x, z: "sky" if hills(x, z) < 0 else "green",
                 height=hills)

    ``thickness`` turns the sheet into a solid slab (see :func:`solidify`).
    """
    w, d = size[0], size[1]
    P = []
    xs, zs = [], []
    for i in range(nx + 1):
        row = []
        x = center[0] - w / 2.0 + w * i / nx
        xs.append(x)
        for j in range(nz + 1):
            z = center[2] - d / 2.0 + d * j / nz
            if i == 0:
                zs.append(z)
            y = center[1]
            if height is not None:
                y = center[1] + height(x, z)
            row.append((x, y, z))
        P.append(row)
    paint = color
    if callable(color):
        def paint(i, j):
            return color((xs[i] + xs[i + 1]) / 2.0, (zs[j] + zs[j + 1]) / 2.0)
    M = Mesh()
    _add_grid(M, P, paint, flip=True)
    if thickness:
        M = solidify(M, thickness)
    _scene.extend(M)


# ============================================================================
#  6. Boxes and other flat-sided solids
# ============================================================================

def box(center, edge, color=None):
    """A cube of side ``edge`` centred at ``center``."""
    cuboid(center, [edge, edge, edge], color)


def cuboid(center, sizes, color=None):
    """A rectangular block; ``sizes`` are the edge lengths along X, Y and Z."""
    ex, ey, ez = sizes[0], sizes[1], sizes[2]
    x0, y0, z0 = center[0] - ex / 2.0, center[1] - ey / 2.0, center[2] - ez / 2.0
    x1, y1, z1 = x0 + ex, y0 + ey, z0 + ez
    P = [(x0, y0, z0), (x0, y0, z1), (x0, y1, z0), (x0, y1, z1),
         (x1, y0, z0), (x1, y0, z1), (x1, y1, z0), (x1, y1, z1)]
    F = [[0, 4, 5, 1], [0, 1, 3, 2], [0, 2, 6, 4],
         [1, 5, 7, 3], [2, 3, 7, 6], [4, 6, 7, 5]]
    base = len(_scene.V)
    color = rgb(color)
    for f in F:
        _scene.add_face([base + i for i in f], color)
    for p in P:
        _scene.add_vertex(p)


def frame(center, edge, thickness, color=None):
    """The twelve edges of a cube -- a hollow cube frame.

    ``thickness`` is how thick each bar is.  Built as a 3x3x3 grid of cells
    in which a cell is material when at least two of its three indices lie on
    the outside; the whole shape therefore comes out watertight.
    """
    e, b = float(edge), float(thickness)
    mid = e - 2 * b
    sizes = [b, mid, b]
    origin = (center[0] - e / 2.0, center[1] - e / 2.0, center[2] - e / 2.0)

    def filled(i, j, k):
        return (i != 1) + (j != 1) + (k != 1) >= 2

    _scene.extend(_grid_solid(origin, sizes, sizes, sizes, filled, color))


def voxels(cells, size=1.0, origin=(0, 0, 0), color=None):
    """Build the surface of a set of unit cells -- a Minecraft-style model.

    ``cells`` is any container of ``(i, j, k)`` integer triples::

        blocks = {(x, y, z) for x in range(5) for y in range(3)
                            for z in range(5) if (x + y + z) % 3}
        add.voxels(blocks, 0.5, color="sky")
    """
    cells = set(tuple(c) for c in cells)
    if not cells:
        return
    lo = [min(c[a] for c in cells) for a in range(3)]
    hi = [max(c[a] for c in cells) for a in range(3)]
    n = [hi[a] - lo[a] + 1 for a in range(3)]
    start = (origin[0] + lo[0] * size, origin[1] + lo[1] * size,
             origin[2] + lo[2] * size)

    def filled(i, j, k):
        return (i + lo[0], j + lo[1], k + lo[2]) in cells

    _scene.extend(_grid_solid(start, [size] * n[0], [size] * n[1],
                              [size] * n[2], filled, color))


def pyramid(center, edge, height, color=None):
    """A square pyramid: base of side ``edge``, apex ``height`` above it.

    A negative ``height`` points the pyramid downwards.
    """
    e, h = float(edge), float(height)
    x, y, z = center[0] - e / 2.0, center[1] - e / 2.0, center[2] - e / 2.0
    base = [(x, y, z), (x + e, y, z), (x + e, y, z + e), (x, y, z + e)]
    apex = (x + e / 2.0, y + h, z + e / 2.0)
    M = Mesh()
    first = 0
    M.add_polygon(base[::-1], color)
    _fan(M, base, apex, rgb(color))
    _weld(M, 1e-9)
    _make_outward(M, first)
    _scene.extend(M)


def prism(profile, height, color=None, center=(0, 0, 0), axis=(0, 1, 0)):
    """A solid with a constant cross-section: a 2D ``profile`` given a depth.

    ``profile`` is a list of ``[x, y]`` points in the cross-section plane,
    listed counter-clockwise.  The result is centred on ``center`` and
    extruded along ``axis``::

        add.prism([[0, 0], [1, 0], [0.5, 1]], 3, "gold")   # triangular bar
    """
    u, v, w = _frame(axis)
    half = _scale(w, height / 2.0)
    bottom = []
    top = []
    for p in profile:
        q = (center[0] + u[0] * p[0] + v[0] * p[1],
             center[1] + u[1] * p[0] + v[1] * p[1],
             center[2] + u[2] * p[0] + v[2] * p[1])
        bottom.append(_sub(q, half))
        top.append(_add3(q, half))
    M = Mesh()
    _add_grid(M, [bottom, top], rgb(color), wrap_v=True, flip=True)
    M.add_polygon(bottom[::-1], color)
    M.add_polygon(top, color)
    _weld(M, 1e-9)
    _make_outward(M, 0)
    _scene.extend(M)


def polyhedron(name, center=(0, 0, 0), r=1.0, color=None):
    """One of the five Platonic solids, inscribed in a sphere of radius ``r``.

    ``name`` is ``"tetrahedron"``, ``"cube"``, ``"octahedron"``,
    ``"dodecahedron"`` or ``"icosahedron"``.
    """
    V, F = _platonic(name)
    scale = r / _norm(V[0])
    base = len(_scene.V)
    color = rgb(color)
    for p in V:
        _scene.add_vertex((center[0] + p[0] * scale,
                           center[1] + p[1] * scale,
                           center[2] + p[2] * scale))
    first = len(_scene.F)
    for f in F:
        _scene.add_face([base + i for i in f], color)
    _make_outward(_scene, first)


def _platonic(name):
    """Vertex and face tables for the five Platonic solids."""
    name = name.lower()
    if name in ("tetrahedron", "tetra"):
        V = [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]
        F = [[0, 1, 2], [0, 3, 1], [0, 2, 3], [1, 3, 2]]
        return V, F
    if name in ("cube", "hexahedron"):
        V = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
        F = [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1],
             [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]]
        return V, F
    if name in ("octahedron", "octa"):
        V = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
        F = [[0, 2, 4], [2, 1, 4], [1, 3, 4], [3, 0, 4],
             [2, 0, 5], [1, 2, 5], [3, 1, 5], [0, 3, 5]]
        return V, F
    phi = (1 + math.sqrt(5)) / 2
    if name in ("icosahedron", "icosa"):
        V = []
        for s1 in (-1, 1):
            for s2 in (-1, 1):
                V += [(0, s1 * 1.0, s2 * phi), (s1 * 1.0, s2 * phi, 0),
                      (s1 * phi, 0, s2 * 1.0)]
        F = _hull_faces(V, 3)
        return V, F
    if name in ("dodecahedron", "dodeca"):
        V = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
        inv = 1.0 / phi
        for s1 in (-1, 1):
            for s2 in (-1, 1):
                V += [(0, s1 * inv, s2 * phi), (s1 * inv, s2 * phi, 0),
                      (s1 * phi, 0, s2 * inv)]
        F = _hull_faces(V, 5)
        return V, F
    raise ValueError("unknown polyhedron: %r" % name)


def _hull_faces(V, sides):
    """Faces of a convex point set: every plane with all points on one side.

    Small and slow (it tries all vertex triples) but the Platonic solids have
    at most 20 vertices, and it keeps the vertex tables above honest.
    """
    n = len(V)
    found = {}
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                nrm = _cross(_sub(V[j], V[i]), _sub(V[k], V[i]))
                if _norm(nrm) < 1e-9:
                    continue
                nrm = _unit(nrm)
                d = _dot(nrm, V[i])
                if d < 1e-9:
                    nrm, d = _scale(nrm, -1), -d
                if d <= 1e-9:
                    continue
                if any(_dot(nrm, p) > d + 1e-9 for p in V):
                    continue
                on = [t for t in range(n) if abs(_dot(nrm, V[t]) - d) < 1e-9]
                if len(on) != sides:
                    continue
                key = tuple(sorted(on))
                if key in found:
                    continue
                # Sort the coplanar points into a proper ring.
                centre = [sum(V[t][a] for t in on) / len(on) for a in range(3)]
                u = _unit(_sub(V[on[0]], centre))
                v = _cross(nrm, u)
                on.sort(key=lambda t: math.atan2(
                    _dot(_sub(V[t], centre), v), _dot(_sub(V[t], centre), u)))
                found[key] = on
    return list(found.values())



# ============================================================================
# 11. Parts that models keep needing
# ============================================================================
# Each of these could be written from the primitives above in a dozen lines;
# they are here because almost every student model contains a beam between
# two points, a wheel, a roof, a staircase, a wall of bricks or
# a tree, and the dozen lines are always the same.

def _local_mesh(M, origin, w, up, side):
    """Map a mesh built in local ``x, y, z`` coordinates into the world:
    ``x`` runs along ``w``, ``y`` along ``up`` and ``z`` along ``side``."""
    return _mapped(M, lambda p: (origin[0] + w[0] * p[0] + up[0] * p[1] + side[0] * p[2],
                                 origin[1] + w[1] * p[0] + up[1] * p[1] + side[1] * p[2],
                                 origin[2] + w[2] * p[0] + up[2] * p[1] + side[2] * p[2]))


def _ground_frame(direction, up=(0, 1, 0)):
    """Unit vectors ``(w, up, side)`` for something standing on the ground and
    running along ``direction``.  ``side`` is to the right of ``w``."""
    w = _unit(direction)
    up = _unit(up)
    side = _cross(w, up)
    if _norm(side) < EPS:                     # direction was straight up
        side = _perp(w)
        up = _cross(side, w)
    side = _unit(side)
    return w, up, side


def beam(A, B, width, height=None, color=None, up=(0, 1, 0)):
    """A rectangular bar from point ``A`` to point ``B``.

    The cross-section is ``width`` (sideways) by ``height`` (along ``up``,
    the roughly vertical direction); ``height`` defaults to ``width``.  This
    is the building block for bridges, cranes, frames and gun barrels: give
    it two points and it takes care of the orientation::

        add.beam([0, 0, 0], [4, 3, 1], 0.3, 0.5, "brown")
    """
    if height is not None and not isinstance(height, (int, float)):
        color, height = height, None          # beam(A, B, 0.3, "brown")
    if height is None:
        height = width
    w, v, u = _ground_frame(_sub(B, A), up)   # along, up, sideways
    hw, hh = width / 2.0, height / 2.0
    corners = []
    for end in (A, B):
        for sv in (-1, 1):
            for su in (-1, 1):
                corners.append((end[0] + u[0] * su * hw + v[0] * sv * hh,
                                end[1] + u[1] * su * hw + v[1] * sv * hh,
                                end[2] + u[2] * su * hw + v[2] * sv * hh))
    # corner index = 4 * (end) + 2 * (v side) + (u side)
    F = [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1], [2, 3, 7, 6],
         [0, 2, 6, 4], [1, 5, 7, 3]]
    M = Mesh()
    for p in corners:
        M.add_vertex(p)
    for f in F:
        M.add_face(f, color)
    _make_outward(M, 0)
    _scene.extend(M)


def rounded_box(center, sizes, r, k=8, color=None):
    """A box with all edges and corners rounded off by radius ``r``.

    ``sizes`` are the full edge lengths (a number means a cube).  Built by
    pushing the six patches of a quad sphere apart -- no boolean needed.
    """
    if not isinstance(sizes, (list, tuple)):
        sizes = [sizes, sizes, sizes]
    r = min(r, sizes[0] / 2.0, sizes[1] / 2.0, sizes[2] / 2.0)
    inner = [sizes[a] / 2.0 - r for a in range(3)]
    sides = [((1, 0, 0), (0, 1, 0), (0, 0, 1)),
             ((-1, 0, 0), (0, 0, 1), (0, 1, 0)),
             ((0, 1, 0), (0, 0, 1), (1, 0, 0)),
             ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
             ((0, 0, 1), (1, 0, 0), (0, 1, 0)),
             ((0, 0, -1), (0, 1, 0), (1, 0, 0))]
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
                q = []
                for axis in range(3):
                    sign = 0.0 if abs(p[axis]) < 1e-12 else (1.0 if p[axis] > 0 else -1.0)
                    q.append(center[axis] + sign * inner[axis] + p[axis] * r)
                row.append(tuple(q))
            P.append(row)
        _add_grid(M, P, color)
    _weld(M, 1e-9)
    _drop_degenerate(M)
    _scene.extend(M)


def hemisphere(center, r, k=16, color=None, axis=(0, 1, 0)):
    """Half a ball with its flat side down: a dome, a bowl, a helmet.

    ``axis`` is the direction the round side points in.
    """
    revolve(lambda t: [r * math.sin(t), r * math.cos(t)], center,
            _add3(center, axis), 0.0, math.pi / 2.0, k, 4 * k, color)


def arch(A, B, height, thickness, color=None, steps=32, k=12, up=(0, 1, 0)):
    """A curved arch standing on the ground at points ``A`` and ``B``.

    The arch rises ``height`` above the line ``A -> B`` (a semicircle when
    ``height`` is half the span, an ellipse otherwise).  ``thickness`` is
    the radius of a round bar, or ``[width, depth]`` for a rectangular one
    with ``width`` across the arch and ``depth`` in the plane of the arch.
    """
    mid = midpoint(A, B)
    half = _sub(A, mid)
    lift = _scale(_unit(up), height)
    N = _unit(_cross(half, lift))             # normal of the arch's plane
    if isinstance(thickness, (list, tuple)):
        profile = profile_rect(thickness[0], thickness[1])
    else:
        profile = profile_circle(thickness, k)
    sections = []
    for i in range(steps + 1):
        t = math.pi * i / float(steps)
        c = _add3(mid, _add3(_scale(half, math.cos(t)), _scale(lift, math.sin(t))))
        T = _unit(_add3(_scale(half, -math.sin(t)), _scale(lift, math.cos(t))))
        R = _cross(T, N)                      # points outward from the arch
        sections.append([(c[0] + N[0] * a + R[0] * b,
                          c[1] + N[1] * a + R[1] * b,
                          c[2] + N[2] * a + R[2] * b) for a, b in profile])
    loft(sections, color)


def stairs(origin, n, width, rise, run, color=None, direction=(1, 0, 0)):
    """A solid flight of ``n`` steps starting at ``origin`` (the foot).

    Each step is ``rise`` high and ``run`` deep; the flight climbs along
    ``direction`` and is ``width`` wide, centred on the origin.
    """
    w, up, side = _ground_frame(direction)
    M = _grid_solid((0.0, 0.0, -width / 2.0), [run] * n, [rise] * n, [width],
                    lambda i, j, k: j <= i, color)
    _scene.extend(_local_mesh(M, origin, w, up, side))


def _hollow_prism(outer, inner, height, color, center=(0, 0, 0), axis=(0, 1, 0)):
    """A prism with a hole: ``outer`` and ``inner`` are 2D rings with the
    same number of points.  Used by :func:`gear`."""
    u, v, w = _frame(axis)
    half = _scale(w, height / 2.0)

    def lift(profile, sign):
        out = []
        for p in profile:
            q = (center[0] + u[0] * p[0] + v[0] * p[1],
                 center[1] + u[1] * p[0] + v[1] * p[1],
                 center[2] + u[2] * p[0] + v[2] * p[1])
            out.append(_add3(q, _scale(half, sign)))
        return out
    ob, ot, ib, it = lift(outer, -1), lift(outer, 1), lift(inner, -1), lift(inner, 1)
    M = Mesh()
    color = rgb(color)
    _add_grid(M, [ob, ot], color, wrap_v=True, flip=True)     # outside wall
    _add_grid(M, [ib, it], color, wrap_v=True)                # inside wall
    _add_grid(M, [it, ot], color, wrap_v=True, flip=True)     # top ring
    _add_grid(M, [ib, ob], color, wrap_v=True)                # bottom ring
    _weld(M, 1e-9)
    _make_outward(M, 0)
    return M


def gear(center, teeth, r, thickness, color=None, depth=None, hole=0.0,
         axis=(0, 1, 0)):
    """A cog wheel with ``teeth`` teeth, lying in the plane normal to ``axis``.

    ``r`` is the mean radius, ``depth`` the tooth height (default ``0.2 r``)
    and ``hole`` the radius of the axle hole (0 for a solid disc).  Two gears
    mesh when their mean radii add up to the distance between their centres
    and the tooth *pitch* ``2 * pi * r / teeth`` is the same.
    """
    outer = profile_gear(teeth, r, depth)
    if hole > EPS:
        inner = profile_circle(hole, len(outer))
        _scene.extend(_hollow_prism(outer, inner, thickness, color, center, axis))
    else:
        prism(outer, thickness, color, center, axis)


def wheel(center, r, width, color="black", axis=(0, 0, 1), k=32, spokes=0,
          hub_color="silver"):
    """A wheel whose axle points along ``axis``.

    With ``spokes=0`` it is a solid disc with a small hub; with spokes it
    becomes a tyre (a torus), a hub and ``spokes`` thin bars between them.
    """
    w = _unit(axis)
    a = _add3(center, _scale(w, -width / 2.0))
    b = _add3(center, _scale(w, width / 2.0))
    if spokes <= 0:
        cylinder(a, b, r, k, color)
        cylinder(_add3(a, _scale(w, -width * 0.15)), _add3(b, _scale(w, width * 0.15)),
                 r * 0.3, max(8, k // 2), hub_color)
        return
    tyre = width / 2.0
    torus(center, r - tyre, tyre, k, max(8, k // 2), color, axis)
    hub = max(r * 0.2, tyre)
    cylinder(a, b, hub, max(8, k // 2), hub_color)
    u, v, _ = _frame(w)
    for i in range(spokes):
        ang = 2 * math.pi * i / spokes
        tip = (center[0] + (u[0] * math.cos(ang) + v[0] * math.sin(ang)) * (r - tyre),
               center[1] + (u[1] * math.cos(ang) + v[1] * math.sin(ang)) * (r - tyre),
               center[2] + (u[2] * math.cos(ang) + v[2] * math.sin(ang)) * (r - tyre))
        cylinder(center, tip, tyre * 0.3, 8, hub_color)


def roof(center, size, height, color=None, overhang=0.0):
    """A gabled (triangular) roof over a ``size = [width_x, depth_z]`` floor.

    ``center`` is the middle of the eaves line (the roof's lowest edge sits at
    ``center[1]``), the ridge runs along Z, and ``overhang`` makes the roof
    stick out beyond the walls on every side.
    """
    w = size[0] / 2.0 + overhang
    profile = [[-w, 0.0], [w, 0.0], [0.0, float(height)]]
    prism(profile, size[1] + 2 * overhang, color, center, (0, 0, 1))


def column(base, height, r, color=None, k=24, plinth=True):
    """A classical column standing on point ``base`` (the bottom centre).

    A square plinth, a slightly tapering shaft and a square capital.
    ``plinth=False`` leaves just the shaft.
    """
    x, y, z = base[0], base[1], base[2]
    slab = 0.3 * r
    if plinth:
        cuboid([x, y + slab / 2.0, z], [2.6 * r, slab, 2.6 * r], color)
        cuboid([x, y + height - slab / 2.0, z], [2.6 * r, slab, 2.6 * r], color)
        frustum([x, y + slab, z], [x, y + height - slab, z], r, 0.85 * r, k, color)
    else:
        frustum([x, y, z], [x, y + height, z], r, 0.85 * r, k, color)


def bricks(origin, length, height, brick=(1.0, 0.5, 0.5), color="brown",
           direction=(1, 0, 0), gap=0.05, seed=None):
    """A wall of staggered bricks starting at ``origin`` (its bottom-left end).

    ``brick`` is ``[length, height, depth]`` of one brick; every second row
    is shifted by half a brick.  ``color`` may be a function ``color(i, j)``
    of the brick's column and row, and with ``seed`` each brick gets a small
    random variation of the colour instead.
    """
    bl, bh, bd = brick[0], brick[1], brick[2]
    rows = int(height / bh + 0.5)
    rnd = _random.Random(seed) if seed is not None else None
    push()
    for j in range(rows):
        shift = 0.0 if j % 2 == 0 else bl / 2.0
        x = -shift
        i = 0
        while x < length - EPS:
            x0, x1 = max(0.0, x), min(length, x + bl - gap)
            if x1 - x0 > EPS:
                if callable(color):
                    c = color(i, j)
                elif rnd is not None:
                    c = shade(color, rnd.uniform(0.8, 1.15))
                else:
                    c = color
                cuboid([(x0 + x1) / 2.0, j * bh + (bh - gap) / 2.0, 0.0],
                       [x1 - x0, bh - gap, bd], c)
            x += bl
            i += 1
    M = pop()
    w, up, side = _ground_frame(direction)
    _scene.extend(_local_mesh(M, origin, w, up, side))


def tree(at, height, trunk="brown", leaves="green", kind="round", k=10, seed=None):
    """A simple tree standing on point ``at``.

    ``kind`` is ``"round"`` (a trunk and a bunch of spheres), ``"pine"``
    (stacked cones) or ``"palm"`` (a curved trunk with leaf blades).  Give a
    ``seed`` to get a slightly different tree for every call with the same
    seed -- a forest is ``[add.tree(p, 3, seed=i) for i, p in enumerate(pts)]``.
    """
    rnd = _random.Random(seed if seed is not None else 0)
    var = (lambda a, b: rnd.uniform(a, b)) if seed is not None else (lambda a, b: (a + b) / 2.0)
    x, y, z = at[0], at[1], at[2]
    h = float(height)
    if kind == "pine":
        cylinder([x, y, z], [x, y + 0.3 * h, z], 0.05 * h, 8, trunk)
        tiers = 3
        for i in range(tiers):
            base_y = y + 0.2 * h + 0.22 * h * i
            rr = 0.32 * h * (1.0 - 0.22 * i) * var(0.9, 1.1)
            cone([x, base_y, z], [x, base_y + 0.36 * h, z], rr, k + 4, leaves)
        return
    if kind == "palm":
        lean = var(0.1, 0.25) * h
        pts = [[x + lean * (t ** 2), y + h * t, z] for t in
               [i / 8.0 for i in range(9)]]
        polyline(pts, lambda t: 0.06 * h * (1.0 - 0.5 * t), 8, trunk)
        top = pts[-1]
        n = 7
        for i in range(n):
            a = 2 * math.pi * i / n + var(-0.2, 0.2)
            dx, dz = math.cos(a), math.sin(a)
            blade = [[top[0] + dx * 0.45 * h * t, top[1] + 0.15 * h * math.sin(math.pi * t) - 0.25 * h * t * t,
                      top[2] + dz * 0.45 * h * t] for t in [j / 5.0 for j in range(6)]]
            polyline(blade, lambda t: 0.035 * h * (1.0 - t) + 0.005 * h, 6, leaves)
        return
    cylinder([x, y, z], [x, y + 0.45 * h, z], 0.06 * h, 8, trunk)
    balls = [(0.0, 0.62, 0.0, 0.33), (0.2, 0.5, 0.05, 0.22), (-0.18, 0.52, -0.1, 0.2),
             (0.02, 0.5, 0.2, 0.2), (-0.05, 0.55, -0.22, 0.2)]
    for dx, dy, dz, rr in balls:
        s = var(0.85, 1.15)
        sphere([x + dx * h * s, y + dy * h, z + dz * h * s], rr * h * var(0.9, 1.1),
               max(3, k // 3), leaves)


#: Default palette for :func:`pixels`: one letter per colour.
PALETTE = {"#": "black", "k": "grey", "w": "white", "r": "red", "g": "green",
           "b": "blue", "y": "yellow", "o": "orange", "p": "pink", "c": "cyan",
           "m": "magenta", "n": "brown", "s": "sky", "l": "lime", "t": "teal",
           "v": "purple", "d": "gold", "i": "silver", "a": "navy"}


def pixels(rows, size=1.0, origin=(0, 0, 0), colors=None, depth=1, color=None):
    """Pixel art in 3D: a list of strings becomes a block of coloured cubes.

    Every character is one cell; a space or a dot is empty.  ``colors`` maps
    characters to colours (default :data:`PALETTE`, where ``r`` is red,
    ``g`` green, ``#`` black ...).  The first string is the top row, the
    picture stands in the XY plane and is ``depth`` cells thick::

        add.pixels([".r.r.",
                    "rrrrr",
                    ".rrr.",
                    "..r.."], 0.5)                     # a heart
    """
    palette = PALETTE if colors is None else colors
    rows = [r for r in rows]
    ny = len(rows)
    nx = max(len(r) for r in rows)

    def char(i, j):
        row = rows[ny - 1 - j]
        return row[i] if i < len(row) else " "

    def filled(i, j, k):
        return char(i, j) not in " ."

    def paint(i, j, k):
        c = char(i, j)
        if c in palette:
            return palette[c]
        return color if color is not None else DEFAULT_COLOR

    _scene.extend(_grid_solid(origin, [size] * nx, [size] * ny, [size] * depth,
                              filled, paint))


def heightmap(heights, cell=1.0, origin=(0, 0, 0), color=None):
    """Columns of cubes: ``heights[i][j]`` cells stacked at column ``(i, j)``.

    ``i`` runs along X and ``j`` along Z from ``origin``.  ``color`` may be
    a function ``color(i, j, k)`` of the *cell* -- ``i`` along X, ``j`` up,
    ``k`` along Z -- so layers can be painted by height (``j``).  Build the
    list with a comprehension::

        H = [[int(3 + 2 * add.sin(i / 3.0) * add.cos(j / 3.0))
              for j in range(30)] for i in range(30)]
        add.heightmap(H, 0.5, color=lambda i, j, k: "sky" if j < 2 else "green")
    """
    nx = len(heights)
    nz = len(heights[0])
    top = max(max(int(round(h)) for h in row) for row in heights)
    if top <= 0:
        return

    def filled(i, j, k):
        return j < int(round(heights[i][k]))

    _scene.extend(_grid_solid(origin, [cell] * nx, [cell] * top, [cell] * nz,
                              filled, color))


# -- tubes through points --------------------------------------------------

def _tube_along(points, radii, k, color, closed, cap_a=None, cap_b=None):
    """The engine behind :func:`curve` and :func:`polyline`: a round tube
    through a list of 3D points with a radius per point."""
    tangents, normals = _rmf(points, closed)
    ring = [(math.cos(2 * math.pi * j / k), math.sin(2 * math.pi * j / k))
            for j in range(k)]
    P = []
    for i in range(len(points)):
        u = normals[i]
        v = _cross(tangents[i], u)
        c = points[i]
        rad = radii[i]
        row = []
        for (cx, cy) in ring:
            x, y = cx * rad, cy * rad
            row.append((c[0] + u[0] * x + v[0] * y,
                        c[1] + u[1] * x + v[1] * y,
                        c[2] + u[2] * x + v[2] * y))
        P.append(row)
    M = Mesh()
    _add_grid(M, P, color, wrap_u=closed, wrap_v=True, flip=True)
    if not closed:
        _fan(M, P[0], points[0], color if cap_a is None else cap_a, flip=True)
        _fan(M, P[-1], points[-1], color if cap_b is None else cap_b)
    return M


def polyline(points, r=0.1, k=12, color=None, closed=False, smooth=0):
    """A round tube through a list of points -- wires, pipes, rails, branches.

    ``r`` is one radius or a function ``r(t)`` of the fraction ``t`` along
    the line; ``smooth`` rounds the corners with :func:`chaikin` first.
    ``color`` may be a function ``color(t, a)`` like in :func:`curve`.
    """
    pts = [tuple(float(c) for c in p) for p in points]
    if smooth:
        pts = [tuple(p) for p in chaikin(pts, smooth, closed)]
    n = len(pts)
    if n < 2:
        return
    ts = [i / float(n if closed else n - 1) for i in range(n)]
    radii = [r(t) if callable(r) else r for t in ts]
    cells = color
    cap_a = cap_b = None
    if callable(color):
        fn = color

        def cells(i, j):
            t = (ts[i] + (ts[i + 1] if i + 1 < n else 1.0)) / 2.0
            return fn(t, 2 * math.pi * (j + 0.5) / k)
        cap_a = lambda j: fn(0.0, 2 * math.pi * (j + 0.5) / k)     # noqa: E731
        cap_b = lambda j: fn(1.0, 2 * math.pi * (j + 0.5) / k)     # noqa: E731
    _emit(_tube_along(pts, radii, k, cells, closed, cap_a, cap_b))


def wireframe(M, r=0.03, k=6, color=None, nodes=True):
    """Draw every edge of a mesh as a thin bar, with a ball at every corner.

    The result is drawn into the scene (the mesh itself is left alone).
    Without ``color`` each bar takes the colour of a face it belongs to.
    Keep the mesh small: a 10 000-face model has some 15 000 edges.
    """
    M = as_mesh(M)
    edges = {}
    for f, c in zip(M.F, M.C):
        for i in range(len(f)):
            a, b = f[i], f[(i + 1) % len(f)]
            key = (a, b) if a < b else (b, a)
            if key not in edges:
                edges[key] = c
    for (a, b), c in edges.items():
        cylinder(M.V[a], M.V[b], r, k, color if color is not None else c)
    if nodes:
        used = set()
        for a, b in edges:
            used.add(a)
            used.add(b)
        for i in used:
            sphere(M.V[i], r, 2, color if color is not None else M.C[0])


def flow(field, p0, dt=0.01, steps=1000):
    """Follow a vector field: the list of points a particle visits.

    ``field(p)`` returns the velocity ``[vx, vy, vz]`` at point ``p``; the
    path is integrated with the classical Runge-Kutta method, so it stays
    accurate even for chaotic systems like the Lorenz attractor::

        def lorenz(p):
            x, y, z = p
            return [10 * (y - x), x * (28 - z) - y, x * y - 8.0 / 3 * z]
        pts = add.flow(lorenz, [1, 1, 1], 0.01, 4000)
    """
    p = [float(c) for c in p0]
    out = [list(p)]
    for _ in range(steps):
        k1 = field(p)
        k2 = field([p[i] + 0.5 * dt * k1[i] for i in range(3)])
        k3 = field([p[i] + 0.5 * dt * k2[i] for i in range(3)])
        k4 = field([p[i] + dt * k3[i] for i in range(3)])
        p = [p[i] + dt / 6.0 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i])
             for i in range(3)]
        out.append(list(p))
    return out


def trace(field, p0, dt=0.01, steps=1000, r=0.1, k=12, color=None, every=1):
    """Draw the path of :func:`flow` as a tube (``every`` keeps each n-th point)."""
    pts = flow(field, p0, dt, steps)
    if every > 1:
        pts = pts[::every]
    polyline(pts, r, k, color)

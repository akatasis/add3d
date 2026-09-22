

# ============================================================================
# 22. Vertices, edges and neighbours
# ============================================================================
# The functions above treat a mesh as a whole.  These look inside it: which
# vertices are joined by an edge, how many neighbours a vertex has, how far
# they are, which faces meet at a corner.  That is what you need to build a
# model out of the *vertices* of an icosahedron or a dodecahedron, to move a
# single corner of a box before rounding it with ``smooth``, or to turn a
# polyhedron into its dual or its truncation (a football).

def _directed_edges(M):
    """``{(a, b): face index}`` for every directed edge of an oriented mesh.

    A directed edge that appears in more than one face is marked with -1
    (the mesh is not a manifold there, or two faces disagree on winding).
    """
    out = {}
    for fi, f in enumerate(M.F):
        n = len(f)
        for t in range(n):
            key = (f[t], f[(t + 1) % n])
            out[key] = -1 if key in out else fi
    return out


def _rings(M):
    """For every vertex the faces around it in order: ``[(face, next), ...]``.

    ``next`` is the vertex the face's edge leaves ``v`` towards.  Walking
    from face to face across that edge goes *clockwise* seen from outside,
    so callers reverse the list when they need a counter-clockwise ring.
    The second value of each entry tells whether the ring closes (``True``)
    or the vertex lies on a border / is not a manifold (``False``).
    """
    E = _directed_edges(M)
    corners = [[] for _ in M.V]                    # vertex -> [(face, prev, next)]
    for fi, f in enumerate(M.F):
        n = len(f)
        for t in range(n):
            corners[f[t]].append((fi, f[t - 1], f[(t + 1) % n]))
    out = []
    for v, cs in enumerate(corners):
        if not cs:
            out.append(([], False))
            continue
        by_face = {}
        ok = True
        for fi, prev, nxt in cs:
            if fi in by_face:                          # v twice in one face
                ok = False
            by_face[fi] = (prev, nxt)
        if not ok:
            out.append(([(fi, nxt) for fi, prev, nxt in cs], False))
            continue
        # Start at a border face if there is one: the face whose edge
        # prev -> v has no partner face on the other side.
        start = cs[0][0]
        for fi, prev, nxt in cs:
            if E.get((v, prev), -1) == -1:
                start = fi
                break
        ring = []
        seen = set()
        fi = start
        closed = False
        while fi not in seen:
            seen.add(fi)
            prev, nxt = by_face[fi]
            ring.append((fi, nxt))
            g = E.get((nxt, v), -1)
            if g == -1 or g not in by_face:
                break
            fi = g
        else:
            closed = (fi == start)
        if len(seen) != len(cs):                      # not all faces reached
            closed = False
            missing = [(f2, n2) for f2, p2, n2 in cs if f2 not in seen]
            ring += missing
        out.append((ring, closed))
    return out


def vertex(M, i):
    """The coordinates of vertex ``i`` as a fresh ``[x, y, z]`` list."""
    return list(as_mesh(M).V[i])


def set_vertex(M, i, point):
    """A copy of the mesh with vertex ``i`` moved to ``point``.

    Any coordinate given as ``None`` keeps its old value, so raising one
    corner of a box is ``add.set_vertex(box, 3, [None, 2.5, None])``.  The
    faces are untouched, which is exactly what you want before rounding the
    result with :func:`smooth`::

        add.box([0, 0, 0], 2)
        block = add.layer()
        block = add.set_vertex(block, 7, [2, 2, 2])     # pull one corner out
        add.mesh(add.smooth(block, 6))
    """
    return set_vertices(M, {i: point})


def set_vertices(M, changes):
    """Like :func:`set_vertex` for several vertices at once:
    ``changes`` is ``{index: point, ...}`` (``None`` coordinates are kept)."""
    out = as_mesh(M).copy()
    for i, point in changes.items():
        p = out.V[i]
        for a in range(3):
            if point[a] is not None:
                p[a] = float(point[a])
    return out


def move_vertex(M, i, delta):
    """A copy of the mesh with vertex ``i`` shifted by the vector ``delta``."""
    p = as_mesh(M).V[i]
    return set_vertices(M, {i: [p[0] + delta[0], p[1] + delta[1],
                                p[2] + delta[2]]})


def nearest_vertex(M, point):
    """The index of the vertex closest to ``point`` -- so that you can pick a
    corner by *where* it is instead of by its number::

        i = add.nearest_vertex(block, [1, 1, 1])
        block = add.set_vertex(block, i, [1.5, 1.5, 1.5])
    """
    M = as_mesh(M)
    best, best_d = -1, None
    for i, p in enumerate(M.V):
        d = ((p[0] - point[0]) ** 2 + (p[1] - point[1]) ** 2
             + (p[2] - point[2]) ** 2)
        if best_d is None or d < best_d:
            best, best_d = i, d
    return best


def edges(M=None):
    """Every edge of the mesh once, as ``(a, b)`` index pairs with ``a < b``."""
    M = as_mesh(M)
    seen = set()
    for f in M.F:
        n = len(f)
        for t in range(n):
            a, b = f[t], f[(t + 1) % n]
            if a != b:
                seen.add((a, b) if a < b else (b, a))
    return sorted(seen)


def edge_length(M, a, b):
    """The distance between vertices ``a`` and ``b``."""
    M = as_mesh(M)
    return _norm(_sub(M.V[a], M.V[b]))


def edge_lengths(M=None):
    """The length of every edge, in the order :func:`edges` lists them."""
    M = as_mesh(M)
    return [_norm(_sub(M.V[a], M.V[b])) for a, b in edges(M)]


def mean_edge_length(M=None):
    """The average edge length -- the natural "unit" of a mesh.  A regular
    polyhedron has all edges equal, so this is *the* edge length there."""
    L = edge_lengths(M)
    return sum(L) / len(L) if L else 0.0


def adjacency(M=None):
    """``neighbours[i]`` = sorted list of the vertices joined to vertex ``i``
    by an edge, for every vertex at once (faster than calling
    :func:`neighbors` in a loop)."""
    M = as_mesh(M)
    nb = [set() for _ in M.V]
    for a, b in edges(M):
        nb[a].add(b)
        nb[b].add(a)
    return [sorted(s) for s in nb]


def neighbors(M, i):
    """The vertices joined to vertex ``i`` by an edge.

    On a closed, well-formed surface they come in order *around* the vertex
    (counter-clockwise seen from outside); otherwise sorted by index::

        ico = add.make(add.icosahedron, [0, 0, 0], 1)
        add.neighbors(ico, 0)          # five of them -> [5, 1, 7, 10, 11]
    """
    M = as_mesh(M)
    ring, closed = _rings(M)[i]
    if closed:
        return [nxt for fi, nxt in reversed(ring)]
    return adjacency(M)[i]


#: British spelling of :func:`neighbors`.
neighbours = neighbors


def valence(M, i):
    """How many edges (and neighbours) vertex ``i`` has: 3 on a cube or a
    dodecahedron, 4 on an octahedron, 5 on an icosahedron."""
    return len(adjacency(M)[i])


def mean_neighbor_distance(M, i):
    """The average distance from vertex ``i`` to its neighbours."""
    M = as_mesh(M)
    nb = adjacency(M)[i]
    if not nb:
        return 0.0
    return sum(_norm(_sub(M.V[i], M.V[j])) for j in nb) / len(nb)


def vertex_faces(M, i):
    """The indices of the faces that meet at vertex ``i`` (in order around
    the vertex when the surface is closed and well formed there)."""
    M = as_mesh(M)
    ring, closed = _rings(M)[i]
    if closed:
        return [fi for fi, nxt in reversed(ring)]
    return sorted(set(fi for fi, nxt in ring))


def vertex_normal(M, i):
    """The unit normal at vertex ``i``: the average of its faces' normals."""
    M = as_mesh(M)
    acc = [0.0, 0.0, 0.0]
    for fi in vertex_faces(M, i):
        nrm = _face_normal(M, M.F[fi])
        acc[0] += nrm[0]
        acc[1] += nrm[1]
        acc[2] += nrm[2]
    return _unit(acc) if _norm(acc) > EPS else (0.0, 1.0, 0.0)


def face_center(M, i):
    """The centre (average corner) of face ``i``."""
    M = as_mesh(M)
    f = M.F[i]
    n = float(len(f))
    return [sum(M.V[k][a] for k in f) / n for a in range(3)]


def face_normal(M, i):
    """The unit normal of face ``i`` (points outward on a closed model)."""
    M = as_mesh(M)
    return _unit(_face_normal(M, M.F[i]))


def face_area(M, i):
    """The area of face ``i``."""
    M = as_mesh(M)
    return _norm(_face_normal(M, M.F[i])) / 2.0


def face_centers(M=None):
    """The centre of every face, as a list of points."""
    M = as_mesh(M)
    return [face_center(M, i) for i in range(len(M.F))]


def boundary_edges(M=None):
    """The edges that belong to only one face, as directed ``(a, b)`` pairs.
    An empty list means the surface is closed."""
    return sorted(_boundary_edges(as_mesh(M)).keys())


def boundary_loops(M=None):
    """The open borders of a mesh as closed rings of vertex indices --
    one list per hole (or per sheet edge)."""
    M = as_mesh(M)
    nxt = {}
    for a, b in _boundary_edges(M):
        nxt.setdefault(a, []).append(b)
    loops = []
    while nxt:
        start = min(nxt)
        loop = [start]
        v = nxt[start].pop()
        if not nxt[start]:
            del nxt[start]
        while v != start and v in nxt:
            loop.append(v)
            w = nxt[v].pop()
            if not nxt[v]:
                del nxt[v]
            v = w
        loops.append(loop)
    return loops


def inflate(M, amount):
    """Push every vertex out along its normal by ``amount`` (in for a
    negative value).  Turns the panels of a ball into cushions, or thickens
    a thin shape a little."""
    M = as_mesh(M)
    N = _vertex_normals(M)
    out = M.copy()
    out.V = [[p[0] + n[0] * amount, p[1] + n[1] * amount,
              p[2] + n[2] * amount] for p, n in zip(M.V, N)]
    return out


def spherify(M, center=None, r=None, amount=1.0):
    """Project every vertex onto a sphere.

    By default the sphere is centred on the average vertex and passes
    through the farthest one (so the corners of a polyhedron stay where
    they are); ``amount`` less than 1 only goes part of the way (0.5 rounds
    a cube into a cushion).  With :func:`refine` this is how a geodesic
    dome comes out of any polyhedron::

        octa = add.make(add.octahedron, [0, 0, 0], 1)
        dome = add.spherify(add.refine(octa, 3))        # 512 triangles
    """
    M = as_mesh(M)
    c = _centroid(M) if center is None else center
    if r is None:
        r = max([_norm(_sub(p, c)) for p in M.V] or [1.0])
    V = []
    for p in M.V:
        u = _unit(_sub(p, c))
        target = (c[0] + u[0] * r, c[1] + u[1] * r, c[2] + u[2] * r)
        V.append([p[a] + (target[a] - p[a]) * amount for a in range(3)])
    out = M.copy()
    out.V = V
    return out


def refine(M, steps=1):
    """Split every face into four (triangles) or into one quad per corner
    (other polygons), ``steps`` times, without moving anything.

    New vertices sit at edge midpoints (and face centres), shared between
    neighbouring faces, so the mesh stays watertight.  Colours are kept.
    This is the flat "observatory dome" split; :func:`spherify` afterwards
    pushes the new points out to a ball, :func:`catmull_clark` is the
    version that rounds the shape as it splits.
    """
    M = as_mesh(M)
    for _ in range(int(steps)):
        out = Mesh([list(p) for p in M.V], [], [])
        mid = {}

        def midpoint_index(a, b):
            key = (a, b) if a < b else (b, a)
            if key not in mid:
                pa, pb = M.V[a], M.V[b]
                mid[key] = out.add_vertex(((pa[0] + pb[0]) / 2.0,
                                           (pa[1] + pb[1]) / 2.0,
                                           (pa[2] + pb[2]) / 2.0))
            return mid[key]

        for f, c in zip(M.F, M.C):
            n = len(f)
            if n == 3:
                a, b, d = f
                ab, bd, da = midpoint_index(a, b), midpoint_index(b, d), \
                    midpoint_index(d, a)
                out.add_face([a, ab, da], c)
                out.add_face([b, bd, ab], c)
                out.add_face([d, da, bd], c)
                out.add_face([ab, bd, da], c)
            elif n >= 4:
                centre = out.add_vertex([sum(M.V[k][a] for k in f) / float(n)
                                         for a in range(3)])
                m = [midpoint_index(f[t], f[(t + 1) % n]) for t in range(n)]
                for t in range(n):
                    out.add_face([f[t], m[t], centre, m[t - 1]], c)
            else:
                out.add_face(f, c)
        M = out
    return M


def dual(M, color=None):
    """The dual polyhedron: a vertex at the centre of every face, and a face
    for every vertex, joining the centres of the faces around it.

    Cube <-> octahedron, dodecahedron <-> icosahedron, and the tetrahedron
    is its own dual.  Only vertices with a closed ring of faces get a face,
    so the model should be closed.  ``color`` paints the result; without it
    each new face takes the colour of one of the old faces around it.
    """
    M = as_mesh(M)
    out = Mesh()
    for i in range(len(M.F)):
        out.add_vertex(face_center(M, i))
    for v, (ring, closed) in enumerate(_rings(M)):
        if not closed or len(ring) < 3:
            continue
        faces = [fi for fi, nxt in reversed(ring)]
        out.add_face(faces, M.C[faces[0]] if color is None else color)
    _drop_unused(out)
    return out


def truncate(M, t=1.0 / 3.0, color=None):
    """Cut every corner off: each vertex is replaced by a small face and
    each old face loses its corners.

    ``t`` is how far along every edge the cut goes (``1/3`` turns an
    icosahedron into the football's truncated icosahedron, ``1/2`` cuts
    right to the edge midpoints).  The corner faces are painted ``color``;
    the old faces keep their colour.  Works on any closed mesh::

        ico = add.make(add.icosahedron, [0, 0, 0], 3, "white")
        ball = add.truncate(ico, 1 / 3.0, "black")     # 20 hexagons, 12 pentagons
    """
    M = as_mesh(M)
    t = float(t)
    if t > 0.5:
        t = 0.5
    out = Mesh()
    cut = {}

    def point(a, b):
        """Vertex on edge a -> b at fraction t from a."""
        key = (a, b) if t < 0.5 - 1e-12 else ((a, b) if a < b else (b, a))
        if key not in cut:
            pa, pb = M.V[a], M.V[b]
            cut[key] = out.add_vertex((pa[0] + (pb[0] - pa[0]) * t,
                                       pa[1] + (pb[1] - pa[1]) * t,
                                       pa[2] + (pb[2] - pa[2]) * t))
        return cut[key]

    for f, c in zip(M.F, M.C):
        n = len(f)
        poly = []
        for i in range(n):
            v, prev, nxt = f[i], f[i - 1], f[(i + 1) % n]
            for idx in (point(v, prev), point(v, nxt)):
                if not poly or poly[-1] != idx:
                    poly.append(idx)
        if len(poly) > 1 and poly[0] == poly[-1]:
            poly.pop()
        if len(poly) >= 3:
            out.add_face(poly, c)
    corner = rgb(color)
    for v, (ring, closed) in enumerate(_rings(M)):
        if len(ring) < 3:
            continue
        poly = [point(v, nxt) for fi, nxt in reversed(ring)]
        if len(set(poly)) >= 3:
            out.add_face(poly, corner)
    return out


def color_by_sides(M, colors, default=None):
    """Paint every face by its number of corners.

    ``colors`` is a dictionary such as ``{5: "black", 6: "white"}`` (the
    football), faces with a count not in it get ``default`` or keep their
    colour.
    """
    M = as_mesh(M)
    out = M.copy()
    for i, f in enumerate(M.F):
        n = len(f)
        if n in colors:
            out.C[i] = rgb(colors[n])
        elif default is not None:
            out.C[i] = rgb(default)
    return out



# ============================================================================
# 23. Boolean operations: union, intersection, difference
# ============================================================================
# Two solids can be added together, cut out of one another, or intersected.
# The idea used here needs no library and fits on one screen:
#
#   1. Wherever the other model's triangles could cut one of ours, slice ours
#      along their planes.  After that every piece lies wholly inside or
#      wholly outside the other solid -- no piece straddles the boundary.
#   2. Ask of each piece: is it inside?  Shoot a ray from just above the
#      piece's middle and count how many times it crosses the other surface.
#      An odd count means inside.
#   3. Keep the pieces the operation asks for, and turn the borrowed ones
#      round when the operation says so:
#
#        union         keep A outside B  +  B outside A
#        intersection  keep A inside  B  +  B inside  A
#        difference    keep A outside B  +  B inside  A, reversed
#
# Two grids keep both steps local, so the work grows roughly with the number
# of faces rather than with its square.  Booleans want *closed* solids --
# ``add.check()`` will tell you whether yours is closed.

#: How far a point may be from a plane and still count as lying in it.
BOOL_EPS = 1e-9

_COPLANAR, _FRONT, _BACK, _SPANNING = 0, 1, 2, 3


class _Poly(object):
    """One planar polygon that remembers its plane and its colour."""

    __slots__ = ("pts", "n", "w", "c")

    def __init__(self, pts, c, n=None, w=None):
        self.pts = pts
        self.c = c
        if n is None:
            nx = ny = nz = 0.0
            m = len(pts)
            for i in range(m):
                a, b = pts[i], pts[(i + 1) % m]
                nx += (a[1] - b[1]) * (a[2] + b[2])
                ny += (a[2] - b[2]) * (a[0] + b[0])
                nz += (a[0] - b[0]) * (a[1] + b[1])
            n = _unit((nx, ny, nz))
            w = _dot(n, pts[0])
        self.n = n
        self.w = w


def _split(pn, pw, poly, front, back, eps=BOOL_EPS):
    """Cut ``poly`` with plane ``(pn, pw)``; a polygon lying in the plane or
    entirely on one side is filed whole."""
    types = []
    poly_type = 0
    for p in poly.pts:
        t = pn[0] * p[0] + pn[1] * p[1] + pn[2] * p[2] - pw
        kind = _BACK if t < -eps else (_FRONT if t > eps else _COPLANAR)
        poly_type |= kind
        types.append(kind)

    if poly_type != _SPANNING:
        (back if poly_type == _BACK else front).append(poly)
        return
    f, b = [], []
    m = len(poly.pts)
    for i in range(m):
        j = (i + 1) % m
        ti, tj = types[i], types[j]
        vi, vj = poly.pts[i], poly.pts[j]
        if ti != _BACK:
            f.append(vi)
        if ti != _FRONT:
            b.append(vi)
        if (ti | tj) == _SPANNING:
            di = pn[0] * vi[0] + pn[1] * vi[1] + pn[2] * vi[2] - pw
            dj = pn[0] * vj[0] + pn[1] * vj[1] + pn[2] * vj[2] - pw
            t = di / (di - dj)
            cut = (vi[0] + (vj[0] - vi[0]) * t,
                   vi[1] + (vj[1] - vi[1]) * t,
                   vi[2] + (vj[2] - vi[2]) * t)
            f.append(cut)
            b.append(cut)
    if len(f) >= 3:
        front.append(_Poly(f, poly.c, poly.n, poly.w))
    if len(b) >= 3:
        back.append(_Poly(b, poly.c, poly.n, poly.w))


# ---------------------------------------------------------------------------
#  Two little indexes that keep the search local
# ---------------------------------------------------------------------------

class _BoxGrid(object):
    """Which triangles live near a given box -- a uniform 3D hash.

    Triangles are filed in every cell their bounding box touches; a triangle
    so long that it would fill hundreds of cells goes on a short "oversize"
    list that every query checks.  Candidates are then filtered by a real
    box overlap test, so a query returns only triangles that could matter.
    """

    __slots__ = ("cell", "buckets", "oversize", "boxes")

    MAX_CELLS = 64

    def __init__(self, polys, diagonal):
        self.cell = max(diagonal / 32.0, 1e-9)
        self.buckets = {}
        self.oversize = []
        self.boxes = []
        for i, p in enumerate(polys):
            lo = [min(q[a] for q in p.pts) for a in range(3)]
            hi = [max(q[a] for q in p.pts) for a in range(3)]
            self.boxes.append((lo, hi))
            keys = self._keys(lo, hi, self.MAX_CELLS)
            if keys is None:
                self.oversize.append(i)
            else:
                for key in keys:
                    self.buckets.setdefault(key, []).append(i)

    def _keys(self, lo, hi, limit=None):
        c = self.cell
        r = []
        total = 1
        for a in range(3):
            first = int(math.floor(lo[a] / c))
            last = int(math.floor(hi[a] / c))
            r.append((first, last))
            total *= last - first + 1
            if limit is not None and total > limit:
                return None
        out = []
        for i in range(r[0][0], r[0][1] + 1):
            for j in range(r[1][0], r[1][1] + 1):
                for k in range(r[2][0], r[2][1] + 1):
                    out.append((i, j, k))
        return out

    def near(self, lo, hi):
        """Indices of triangles whose bounding box overlaps ``lo..hi``."""
        keys = self._keys(lo, hi, 4096)
        if keys is None:
            candidates = range(len(self.boxes))
        else:
            seen = set(self.oversize)
            for key in keys:
                seen.update(self.buckets.get(key, ()))
            candidates = seen
        out = []
        for i in candidates:
            blo, bhi = self.boxes[i]
            if (bhi[0] < lo[0] - 1e-9 or blo[0] > hi[0] + 1e-9
                    or bhi[1] < lo[1] - 1e-9 or blo[1] > hi[1] + 1e-9
                    or bhi[2] < lo[2] - 1e-9 or blo[2] > hi[2] + 1e-9):
                continue
            out.append(i)
        return out


class _RayIndex(object):
    """Answers "is this point inside the solid?" by counting ray crossings.

    All rays travel in the same direction, so the triangles can be bucketed
    once on the two axes across that direction; a query then only looks at the
    handful of triangles standing in the ray's way.
    """

    __slots__ = ("d", "e1", "e2", "cell", "buckets", "tris")

    def __init__(self, polys, direction):
        self.d = _unit(direction)
        self.e1 = _perp(self.d)
        self.e2 = _cross(self.d, self.e1)
        self.tris = []
        for p in polys:
            for t in range(1, len(p.pts) - 1):
                self.tris.append((p.pts[0], p.pts[t], p.pts[t + 1]))
        span = 0.0
        flat = []
        for tri in self.tris:
            uv = [(_dot(q, self.e1), _dot(q, self.e2)) for q in tri]
            lo = (min(q[0] for q in uv), min(q[1] for q in uv))
            hi = (max(q[0] for q in uv), max(q[1] for q in uv))
            flat.append((lo, hi))
            span = max(span, hi[0] - lo[0], hi[1] - lo[1])
        self.cell = max(span, 1e-9)
        self.buckets = {}
        for i, (lo, hi) in enumerate(flat):
            for a in range(int(math.floor(lo[0] / self.cell)),
                           int(math.floor(hi[0] / self.cell)) + 1):
                for b in range(int(math.floor(lo[1] / self.cell)),
                               int(math.floor(hi[1] / self.cell)) + 1):
                    self.buckets.setdefault((a, b), []).append(i)

    def inside(self, p):
        """``True`` / ``False``, or ``None`` when the ray grazes an edge."""
        key = (int(math.floor(_dot(p, self.e1) / self.cell)),
               int(math.floor(_dot(p, self.e2) / self.cell)))
        hits = 0
        for i in self.buckets.get(key, ()):
            a, b, c = self.tris[i]
            e1v, e2v = _sub(b, a), _sub(c, a)
            h = _cross(self.d, e2v)
            det = _dot(e1v, h)
            if abs(det) < 1e-14:
                continue
            inv = 1.0 / det
            s = _sub(p, a)
            u = _dot(s, h) * inv
            if u < -1e-9 or u > 1.0 + 1e-9:
                continue
            q = _cross(s, e1v)
            v = _dot(self.d, q) * inv
            if v < -1e-9 or u + v > 1.0 + 1e-9:
                continue
            t = _dot(e2v, q) * inv
            if t < 1e-12:
                continue
            # Too close to an edge, a corner or the start of the ray to trust.
            if (abs(u) < 1e-9 or abs(v) < 1e-9 or abs(u + v - 1.0) < 1e-9
                    or t < 1e-9):
                return None
            hits += 1
        return hits % 2 == 1


#: Three awkward directions; if one ray grazes an edge the next one is tried.
_RAY_DIRECTIONS = ((0.5773502691896258, 0.5773502691896257, 0.5773502691896256),
                   (0.2672612419124244, -0.5345224838248488, 0.8017837257372732),
                   (-0.7071067811865475, 0.408248290463863, 0.5773502691896258))


class _Solid(object):
    """A mesh prepared for boolean work: triangles, a box grid and ray indexes."""

    __slots__ = ("polys", "grid", "rays", "lo", "hi", "scale")

    def __init__(self, M):
        self.polys = _to_polys(M)
        lo = [min(p[a] for q in self.polys for p in q.pts) for a in range(3)] \
            if self.polys else [0.0, 0.0, 0.0]
        hi = [max(p[a] for q in self.polys for p in q.pts) for a in range(3)] \
            if self.polys else [0.0, 0.0, 0.0]
        self.lo, self.hi = lo, hi
        self.scale = max(1e-9, max(hi[a] - lo[a] for a in range(3)))
        diagonal = math.sqrt(sum((hi[a] - lo[a]) ** 2 for a in range(3)))
        self.grid = _BoxGrid(self.polys, max(diagonal, 1e-9)) if self.polys else None
        self.rays = []

    def ray_index(self, which):
        while len(self.rays) <= which:
            self.rays.append(_RayIndex(self.polys,
                                       _RAY_DIRECTIONS[len(self.rays)]))
        return self.rays[which]

    def contains(self, p):
        """Is point ``p`` inside this solid?"""
        for which in range(len(_RAY_DIRECTIONS)):
            answer = self.ray_index(which).inside(p)
            if answer is not None:
                return answer
        return False

    def cutters(self, poly):
        """Planes to cut ``poly`` with, and the triangles it may lie on.

        Normally a nearby triangle contributes its own plane.  A triangle
        lying in the *same* plane as ``poly`` would not cut it at all, yet the
        two faces may still overlap -- think of two boxes whose tops are
        flush.  For those, the three planes standing on the triangle's edges
        are used instead, which carves the shared patch out cleanly.
        """
        lo = [min(q[a] for q in poly.pts) for a in range(3)]
        hi = [max(q[a] for q in poly.pts) for a in range(3)]
        planes = []
        flush = []
        for i in self.grid.near(lo, hi):
            t = self.polys[i]
            if abs(abs(_dot(t.n, poly.n)) - 1.0) < 1e-9 \
                    and abs(_dot(t.n, poly.pts[0]) - t.w) < 1e-9:
                flush.append(i)
                for k in range(3):               # the triangle's edge planes
                    p, q = t.pts[k], t.pts[(k + 1) % 3]
                    side = _cross(t.n, _sub(q, p))
                    if _norm(side) > 1e-12:
                        side = _unit(side)
                        planes.append(((i, k + 1), side, _dot(side, p)))
            else:
                planes.append(((i, 0), t.n, t.w))
        return planes, flush

    def facing_at(self, point, plane_normal, flush):
        """Does ``point`` sit on one of the ``flush`` triangles?

        Returns ``+1`` when the triangle faces the same way as
        ``plane_normal``, ``-1`` when it faces the other way, ``None`` when
        the point is not on any of them.
        """
        for i in flush:
            t = self.polys[i]
            on = True
            for k in range(3):
                p, q = t.pts[k], t.pts[(k + 1) % 3]
                side = _cross(t.n, _sub(q, p))
                if _dot(side, _sub(point, p)) < -1e-12 * max(1.0, _norm(side)):
                    on = False
                    break
            if on:
                return 1 if _dot(t.n, plane_normal) > 0 else -1
        return None


def _split_against(poly, other):
    """Chop ``poly`` until no piece can straddle ``other``'s surface.

    Pieces are cut one at a time and the search is redone for each new piece,
    so a face far from the action stops being cut as soon as it moves out of
    the way -- which is what keeps a drilled plate from shattering into
    thousands of slivers.
    """
    done_pieces = []
    work = [(poly, frozenset())]
    guard = 0
    while work:
        piece, done = work.pop()
        guard += 1
        if guard > 20000:                        # pathological input; stop
            done_pieces.append(piece)
            continue
        planes, flush = other.cutters(piece)
        chosen = None
        for pid, pn, pw in planes:
            if pid in done:
                continue
            front = back = False
            for p in piece.pts:
                t = pn[0] * p[0] + pn[1] * p[1] + pn[2] * p[2] - pw
                if t > BOOL_EPS:
                    front = True
                elif t < -BOOL_EPS:
                    back = True
            if front and back:
                chosen = (pid, pn, pw)
                break
            done = done | {pid}                  # this plane can never cut it
        if chosen is None:
            done_pieces.append((piece, flush))
            continue
        pid, pn, pw = chosen
        f, b = [], []
        _split(pn, pw, piece, f, b)
        rest = done | {pid}
        for part in f + b:
            work.append((part, rest))
    return done_pieces


def _keep_pieces(source, other, keep, flip, paint=None):
    """Cut ``source``'s faces against ``other`` and keep the wanted pieces.

    ``keep`` is a set drawn from ``"in"``, ``"out"``, ``"same"`` and
    ``"opp"``: whether a piece ends up inside the other solid, outside it, or
    lying on its surface facing the same or the opposite way.
    """
    out = []
    if other.grid is None:
        return out
    for poly in source.polys:
        # Wholly outside the other model's box: no cutting, no doubt.
        if any(max(q[a] for q in poly.pts) < other.lo[a] - 1e-9
               or min(q[a] for q in poly.pts) > other.hi[a] + 1e-9
               for a in range(3)):
            if "out" in keep:
                out.append(poly)
            continue
        for piece, flush in _split_against(poly, other):
            n = len(piece.pts)
            centre = (sum(q[0] for q in piece.pts) / n,
                      sum(q[1] for q in piece.pts) / n,
                      sum(q[2] for q in piece.pts) / n)
            facing = other.facing_at(centre, piece.n, flush) if flush else None
            if facing is not None:
                state = "same" if facing > 0 else "opp"
            else:
                state = "in" if other.contains(centre) else "out"
            if state not in keep:
                continue
            c = piece.c if paint is None else paint
            if flip:
                out.append(_Poly(piece.pts[::-1], c,
                                 (-piece.n[0], -piece.n[1], -piece.n[2]),
                                 -piece.w))
            else:
                out.append(_Poly(piece.pts, c, piece.n, piece.w))
    return out


def _to_polys(M):
    """Mesh -> list of triangles (so no face can be twisted or non-planar)."""
    M = as_mesh(M)
    polys = []
    for f, c in zip(M.F, M.C):
        if len(f) < 3:
            continue
        pts = [tuple(M.V[i]) for i in f]
        for t in range(1, len(pts) - 1):
            p = _Poly([pts[0], pts[t], pts[t + 1]], c)
            if _norm(p.n) > 0.5:                 # skip degenerate slivers
                polys.append(p)
    return polys


def _from_polys(polys, tidy=True):
    """List of polygons -> Mesh, welded and with its T-junctions closed."""
    M = Mesh()
    for p in polys:
        M.add_polygon(p.pts, p.c)
    if tidy:
        _weld(M, 1e-7)
        _drop_degenerate(M)
        _dedup_faces(M)
        M = heal(M, 1e-7)
        _drop_degenerate(M)
        _drop_unused(M)
    return M


def _boxes_apart(A, B, slack=1e-9):
    """True when two meshes cannot possibly touch."""
    la, ha = bbox(A)
    lb, hb = bbox(B)
    for a in range(3):
        if ha[a] < lb[a] - slack or hb[a] < la[a] - slack:
            return True
    return False


#: Which pieces each operation keeps.  ``A`` gets the shared surface so that
#: a patch where the two solids are flush is kept exactly once.
_RULES = {
    "union":        ({"out", "same"}, {"out"}, False),
    "intersection": ({"in", "same"}, {"in"}, False),
    "difference":   ({"out", "opp"}, {"in"}, True),
}


def _csg(A, B, op, paint=None):
    """The three boolean operations, all from the same two half-steps."""
    if op not in _RULES:
        raise ValueError("unknown boolean operation: %r" % op)
    keep_a, keep_b, flip_b = _RULES[op]
    a, b = _Solid(A), _Solid(B)
    polys = (_keep_pieces(a, b, keep_a, False)
             + _keep_pieces(b, a, keep_b, flip_b, paint))
    return _from_polys(polys)


def union(*meshes):
    """Fuse solids into one, removing everything hidden inside.

    Unlike :func:`merge`, which only stacks meshes into the same file,
    ``union`` really welds them: the buried walls disappear and the result is
    a single watertight solid::

        add.box([0, 0, 0], 2, "red")
        a = add.layer()
        add.sphere([1, 1, 1], 1.3, 16, "blue")
        b = add.layer()
        add.mesh(add.union(a, b))
    """
    meshes = _flatten(meshes)
    if not meshes:
        return Mesh()
    out = as_mesh(meshes[0])
    for other in meshes[1:]:
        other = as_mesh(other)
        if not other.F:
            continue
        if not out.F:
            out = other
        elif _boxes_apart(out, other):
            out = merge([out, other])            # nothing to cut: just stack
        else:
            out = _csg(out, other, "union")
    return out


def difference(A, *others, **options):
    """Cut the other solids out of ``A``.

    ``difference`` is how you drill, engrave and slot::

        add.cuboid([0, 0, 0], [4, 1, 4], "brown")
        plate = add.layer()
        add.cylinder([0, -1, 0], [0, 1, 0], 0.6, 32, "brown")
        drill = add.layer()
        add.mesh(add.difference(plate, drill))

    The freshly exposed surface keeps the colour of the tool that cut it,
    which makes a hole easy to see.  Pass ``color=`` to paint it instead::

        add.difference(plate, drill, color="black")
    """
    paint = rgb(options["color"]) if options.get("color") is not None else None
    for key in options:
        if key != "color":
            raise TypeError("unexpected argument %r" % key)
    out = as_mesh(A)
    for other in _flatten(others):
        other = as_mesh(other)
        if not other.F or not out.F or _boxes_apart(out, other):
            continue
        out = _csg(out, other, "difference", paint)
    return out


def intersect(*meshes):
    """Keep only the space that all the solids have in common."""
    meshes = _flatten(meshes)
    if not meshes:
        return Mesh()
    out = as_mesh(meshes[0])
    for other in meshes[1:]:
        other = as_mesh(other)
        if not out.F or not other.F or _boxes_apart(out, other):
            return Mesh()
        out = _csg(out, other, "intersection")
    return out


def symmetric_difference(A, B):
    """Everything that is in one solid or the other but not in both."""
    return union(difference(A, B), difference(B, A))


def _flatten(items):
    """Allow ``union(a, b, c)`` and ``union([a, b, c])`` to mean the same."""
    out = []
    for x in items:
        if isinstance(x, Mesh):
            out.append(x)
        elif isinstance(x, (list, tuple)) and len(x) == 2 \
                and all(isinstance(y, (list, tuple, _StringView)) for y in x):
            out.append(as_mesh(x))               # old [vertices, faces] pair
        elif isinstance(x, (list, tuple)):
            out.extend(_flatten(x))
        else:
            out.append(as_mesh(x))
    return out


def add_solids(*meshes):
    """Alias of :func:`union`."""
    return union(*meshes)


def subtract(A, *others):
    """Alias of :func:`difference`."""
    return difference(A, *others)


def common(*meshes):
    """Alias of :func:`intersect`."""
    return intersect(*meshes)


# ---------------------------------------------------------------------------
#  Cheap relatives of the boolean operations
# ---------------------------------------------------------------------------

def cut(M, point=(0, 0, 0), normal=(0, 1, 0), cap=True, color=None):
    """Slice a solid with an infinite plane and keep the part *behind* it.

    "Behind" means the side the normal points away from, so
    ``cut(M, [0, 0, 0], [0, 1, 0])`` keeps the bottom half and throws the top
    away.  Cut twice with opposite normals to keep a slab.

    Far cheaper than a full boolean, because a plane needs no searching.  With
    ``cap=True`` the exposed cross-section is closed with a new flat face, so
    the result stays watertight -- perfect for cut-away drawings::

        half = add.cut(model, [0, 0, 0], [0, 0, 1])
    """
    M = as_mesh(M)
    n = _unit(normal)
    w = _dot(n, point)
    out = Mesh()
    rim = []
    for f, c in zip(M.F, M.C):
        poly = _Poly([tuple(M.V[i]) for i in f], c)
        front, back = [], []
        _split(n, w, poly, front, back, 1e-12)
        for p in back:
            out.add_polygon(p.pts, p.c)
            m = len(p.pts)
            for i in range(m):
                a, b = p.pts[i], p.pts[(i + 1) % m]
                if abs(_dot(n, a) - w) < 1e-9 and abs(_dot(n, b) - w) < 1e-9:
                    rim.append((a, b))
    if cap and rim:
        for loop in _loops(rim):
            if len(loop) >= 3:
                out.add_polygon(loop, color if color is not None else
                                (M.C[0] if M.C else None))
    _weld(out, 1e-7)
    _drop_degenerate(out)
    _drop_unused(out)
    return out


def _loops(edges):
    """Chain a bag of (a, b) segments into closed rings of points."""
    def key(p):
        return (round(p[0], 7), round(p[1], 7), round(p[2], 7))

    nxt = {}
    coords = {}
    for a, b in edges:
        nxt.setdefault(key(a), []).append(key(b))
        coords[key(a)] = a
        coords[key(b)] = b
    loops = []
    used = set()
    for start in list(nxt):
        if start in used:
            continue
        loop = []
        cur = start
        while cur in nxt and cur not in used:
            used.add(cur)
            loop.append(coords[cur])
            options = [k for k in nxt[cur] if k not in used]
            if not options:
                break
            cur = options[0]
        if len(loop) >= 3:
            loops.append(loop)
    return loops


def inside(M, p):
    """Is point ``p`` inside the (closed) mesh?  Ray casting: odd = inside.

    ``p`` may also be a *list* of points, which returns a list of answers
    and is far faster than asking one point at a time, because the mesh is
    indexed only once::

        hits = add.inside(ring, add.random_points(400, lo, hi, seed=3))
    """
    solid = _Solid(M)
    if len(p) and isinstance(p[0], (list, tuple)):
        return [solid.contains((q[0], q[1], q[2])) for q in p]
    return solid.contains((p[0], p[1], p[2]))

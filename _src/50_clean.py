

# ============================================================================
# 20. Repairing a model
# ============================================================================
# Models built by stacking shapes tend to collect three kinds of rubbish:
# vertices that sit on top of each other, faces that are repeated, and walls
# buried inside the model where two parts touch.  None of it is visible, but
# all of it bloats the file and upsets 3D printing and boolean operations.
# `clean()` gets rid of all three.

def _cell_keys(p, tol):
    """Grid cell(s) a point may belong to, allowing for rounding at the edges."""
    ranges = []
    for a in range(3):
        q = p[a] / tol
        k = int(math.floor(q + 0.5))
        frac = q + 0.5 - math.floor(q + 0.5)
        if frac < 0.25:
            ranges.append((k, k - 1))
        elif frac > 0.75:
            ranges.append((k, k + 1))
        else:
            ranges.append((k,))
    out = []
    for i in ranges[0]:
        for j in ranges[1]:
            for k in ranges[2]:
                out.append((i, j, k))
    return out


def _weld(M, tol=1e-7):
    """Merge vertices closer than ``tol`` (in place).  Returns how many went."""
    lookup = {}
    remap = [0] * len(M.V)
    newV = []
    for i, p in enumerate(M.V):
        found = None
        for key in _cell_keys(p, tol):
            j = lookup.get(key)
            if j is not None:
                q = newV[j]
                if (abs(q[0] - p[0]) <= tol and abs(q[1] - p[1]) <= tol
                        and abs(q[2] - p[2]) <= tol):
                    found = j
                    break
        if found is None:
            found = len(newV)
            newV.append(list(p))
            for key in _cell_keys(p, tol):
                lookup.setdefault(key, found)
        remap[i] = found
    removed = len(M.V) - len(newV)
    M.V = newV
    for f in M.F:
        for i in range(len(f)):
            f[i] = remap[f[i]]
    return removed


def _keep_faces(M, keep):
    """Keep only the faces whose index is in ``keep`` (in place)."""
    removed = len(M.F) - len(keep)
    M.F = [M.F[i] for i in keep]
    M.C = [M.C[i] for i in keep]
    if M.UV is not None:
        M.UV = [M.UV[i] for i in keep]
    return removed


def _not_finite(M):
    """The vertices with a coordinate that is not a finite number (NaN or
    infinite -- a division by zero somewhere).  Quick when there are none."""
    finite = math.isfinite
    if finite(sum(p[0] + p[1] + p[2] for p in M.V)):
        return set()
    return set(i for i, p in enumerate(M.V) if not (finite(p[0]) and finite(p[1]) and finite(p[2])))


def _drop_not_finite(M):
    """Delete the vertices that are not finite numbers, and the faces that
    use them (in place).  Returns how many faces went."""
    bad = _not_finite(M)
    if not bad:
        return 0
    removed = _keep_faces(M, [k for k, f in enumerate(M.F) if bad.isdisjoint(f)])
    remap, newV = {}, []
    for i, p in enumerate(M.V):
        if i not in bad:
            remap[i] = len(newV)
            newV.append(p)
    M.V = newV
    for f in M.F:
        f[:] = [remap[i] for i in f]
    return removed


def _split_repeats(f, uv):
    """Cut a face that visits a vertex twice into loops that do not.

    ``[a, b, c, a, d]`` -- a polygon pinched at ``a`` -- becomes
    ``[a, b, c]`` and ``[a, d]`` (the second is then dropped as too short).
    Consecutive repeats are removed first.  Returns ``[(face, uv), ...]``.
    """
    clean_f, clean_uv = [], ([] if uv is not None else None)
    for t, i in enumerate(f):                        # drop repeated corners
        if not clean_f or clean_f[-1] != i:
            clean_f.append(i)
            if clean_uv is not None:
                clean_uv.append(uv[t])
    if len(clean_f) > 1 and clean_f[0] == clean_f[-1]:
        clean_f.pop()
        if clean_uv is not None:
            clean_uv.pop()
    if len(set(clean_f)) == len(clean_f):
        return [(clean_f, clean_uv)]
    seen = {}
    for j, i in enumerate(clean_f):
        if i in seen:                                # pinch: split here
            a = seen[i]
            first = (clean_f[a:j], clean_uv[a:j] if clean_uv is not None else None)
            rest = (clean_f[j:] + clean_f[:a],
                    (clean_uv[j:] + clean_uv[:a]) if clean_uv is not None else None)
            return _split_repeats(first[0], first[1]) + _split_repeats(rest[0], rest[1])
        seen[i] = j
    return [(clean_f, clean_uv)]


def _drop_degenerate(M, tol=1e-12):
    """Delete faces with no area, remove repeated corners and split faces
    pinched at a vertex (in place)."""
    keep = []
    extra_F, extra_C, extra_UV = [], [], []
    for k, f in enumerate(M.F):
        uv = M.UV[k] if M.UV is not None else None
        pieces = [(list(f), uv)] if len(set(f)) == len(f) else _split_repeats(f, uv)
        first = True
        for clean_f, clean_uv in pieces:
            if len(clean_f) < 3 or len(set(clean_f)) < 3:
                continue
            if _norm(_face_normal(M, clean_f)) <= tol:
                continue
            if first:
                M.F[k] = clean_f
                if clean_uv is not None:
                    M.UV[k] = clean_uv
                keep.append(k)
                first = False
            else:                                    # a second loop of a pinched face
                extra_F.append(clean_f)
                extra_C.append(M.C[k])
                extra_UV.append(clean_uv)
    removed = _keep_faces(M, keep)
    if extra_F:
        M.F.extend(extra_F)
        M.C.extend(extra_C)
        if M.UV is not None:
            M.UV.extend(extra_UV)
        removed -= len(extra_F)
    return removed


def _dedup_faces(M):
    """Delete repeats of a face that is already there (in place)."""
    seen = set()
    keep = []
    for k, f in enumerate(M.F):
        key = tuple(sorted(f))
        if key in seen:
            continue
        seen.add(key)
        keep.append(k)
    return _keep_faces(M, keep)


def _drop_internal(M):
    """Delete pairs of identical faces that point opposite ways (in place).

    That is exactly what you get where two solids touch -- a wall buried
    inside the model.  Both copies are useless, so both go.
    """
    groups = {}
    for i, f in enumerate(M.F):
        groups.setdefault(tuple(sorted(f)), []).append(i)
    drop = set()
    for key, idx in groups.items():
        if len(idx) < 2:
            continue
        forward, backward = [], []
        for i in idx:
            (forward if _winding(M.F[i]) else backward).append(i)
        pairs = min(len(forward), len(backward))
        for t in range(pairs):
            drop.add(forward[t])
            drop.add(backward[t])
    if not drop:
        return 0
    return _keep_faces(M, [i for i in range(len(M.F)) if i not in drop])


def _winding(f):
    """True when the smallest index is followed by the smaller neighbour.

    A cheap, orientation-sensitive signature for a face's corner order.
    """
    k = f.index(min(f))
    return f[(k + 1) % len(f)] < f[k - 1]


def _drop_unused(M):
    """Delete vertices no face refers to (in place)."""
    used = set()
    for f in M.F:
        used.update(f)
    if len(used) == len(M.V):
        return 0
    remap = {}
    newV = []
    for i, p in enumerate(M.V):
        if i in used:
            remap[i] = len(newV)
            newV.append(p)
    removed = len(M.V) - len(newV)
    M.V = newV
    for f in M.F:
        for i in range(len(f)):
            f[i] = remap[f[i]]
    return removed


def heal(M=None, tol=1e-7):
    """Close the tiny gaps left where an edge runs past another vertex.

    After a boolean operation a long edge of one face often has two shorter
    edges of neighbouring faces lying along it, with a vertex in the middle
    that the long edge knows nothing about.  These "T-junctions" leave a
    hairline crack: the model looks fine but is not watertight, which upsets
    3D printing and further boolean operations.  Adding the missing corner to
    the long face fixes it.
    """
    M = as_mesh(M).copy()
    if not M.F or not M.V:
        return M

    # A grid roughly one edge-length wide keeps the search local.
    total = 0.0
    count = 0
    for f in M.F:
        n = len(f)
        for i in range(n):
            total += _norm(_sub(M.V[f[i]], M.V[f[(i + 1) % n]]))
            count += 1
    cell = max(total / max(1, count), tol * 10.0)

    grid = {}
    for idx, p in enumerate(M.V):
        key = (int(math.floor(p[0] / cell)), int(math.floor(p[1] / cell)),
               int(math.floor(p[2] / cell)))
        grid.setdefault(key, []).append(idx)

    def nearby(pa, pb):
        """Vertex indices in the grid cells the segment could pass through."""
        lo, hi = [], []
        for a in range(3):
            lo.append(int(math.floor((min(pa[a], pb[a]) - tol) / cell)))
            hi.append(int(math.floor((max(pa[a], pb[a]) + tol) / cell)))
        spread = 1
        for a in range(3):
            spread *= hi[a] - lo[a] + 1
        out = []
        if spread <= 512:                       # short edge: sweep its box
            for cx in range(lo[0], hi[0] + 1):
                for cy in range(lo[1], hi[1] + 1):
                    for cz in range(lo[2], hi[2] + 1):
                        out.extend(grid.get((cx, cy, cz), ()))
            return out
        # Long edge: walk along it instead of filling its whole box.
        length = _norm(_sub(pb, pa))
        steps = min(4000, int(3.0 * length / cell) + 2)
        seen_cells = set()
        for s in range(steps + 1):
            t = s / float(steps)
            key = (int(math.floor((pa[0] + (pb[0] - pa[0]) * t) / cell)),
                   int(math.floor((pa[1] + (pb[1] - pa[1]) * t) / cell)),
                   int(math.floor((pa[2] + (pb[2] - pa[2]) * t) / cell)))
            if key in seen_cells:
                continue
            seen_cells.add(key)
            for a in (-1, 0, 1):
                for b in (-1, 0, 1):
                    for c in (-1, 0, 1):
                        out.extend(grid.get((key[0] + a, key[1] + b,
                                             key[2] + c), ()))
        return out

    newF = []
    newUV = [] if M.UV is not None else None
    for k, f in enumerate(M.F):
        n = len(f)
        out = []
        uv = M.UV[k] if M.UV is not None else None
        out_uv = [] if uv is not None else None
        for i in range(n):
            a, b = f[i], f[(i + 1) % n]
            out.append(a)
            if out_uv is not None:
                out_uv.append(uv[i])
            pa, pb = M.V[a], M.V[b]
            d = _sub(pb, pa)
            L2 = _dot(d, d)
            if L2 <= tol * tol:
                continue
            hits = []
            for v in nearby(pa, pb):
                if v == a or v == b:
                    continue
                pv = M.V[v]
                t = ((pv[0] - pa[0]) * d[0] + (pv[1] - pa[1]) * d[1]
                     + (pv[2] - pa[2]) * d[2]) / L2
                if t <= 1e-9 or t >= 1.0 - 1e-9:
                    continue
                if (abs(pa[0] + d[0] * t - pv[0]) <= tol
                        and abs(pa[1] + d[1] * t - pv[1]) <= tol
                        and abs(pa[2] + d[2] * t - pv[2]) <= tol):
                    hits.append((t, v))
            if hits:
                hits.sort()
                last = None
                for t, v in hits:
                    if v != last:
                        out.append(v)
                        if out_uv is not None:
                            ua, ub = uv[i], uv[(i + 1) % n]
                            out_uv.append((ua[0] + (ub[0] - ua[0]) * t,
                                           ua[1] + (ub[1] - ua[1]) * t))
                    last = v
        newF.append(out)
        if newUV is not None:
            newUV.append(out_uv)
    M.F = newF
    M.UV = newUV
    return M


# -- coplanar overlaps: the cause of flicker ("z-fighting") in viewers -------

def _poly_area2(pts):
    """Twice the signed area of a 2D polygon (positive when counter-clockwise)."""
    a = 0.0
    n = len(pts)
    for i in range(n):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % n]
        a += x0 * y1 - x1 * y0
    return a


def _clip_half(pts, a, b, keep_left):
    """Sutherland-Hodgman: the part of convex polygon ``pts`` on one side of
    the directed line a -> b (left = the inside of a counter-clockwise polygon)."""
    ax, ay = a
    bx, by = b
    ex, ey = bx - ax, by - ay
    out = []
    n = len(pts)
    if n == 0:
        return out
    prev = pts[-1]
    prev_s = ex * (prev[1] - ay) - ey * (prev[0] - ax)
    for cur in pts:
        cur_s = ex * (cur[1] - ay) - ey * (cur[0] - ax)
        cur_in = cur_s >= 0 if keep_left else cur_s <= 0
        prev_in = prev_s >= 0 if keep_left else prev_s <= 0
        if cur_in != prev_in:
            t = prev_s / (prev_s - cur_s)
            out.append((prev[0] + (cur[0] - prev[0]) * t, prev[1] + (cur[1] - prev[1]) * t))
        if cur_in:
            out.append(cur)
        prev, prev_s = cur, cur_s
    return out


def _convex_minus(A, B, eps):
    """Convex polygon ``A`` with convex polygon ``B`` taken away, as a list
    of convex pieces (both counter-clockwise).  ``A`` comes back untouched
    when the two only touch along an edge."""
    inside = A
    for i in range(len(B)):
        inside = _clip_half(inside, B[i], B[(i + 1) % len(B)], True)
        if len(inside) < 3:
            return [A]
    if abs(_poly_area2(inside)) <= eps:
        return [A]
    pieces = []
    current = A
    for i in range(len(B)):
        a, b = B[i], B[(i + 1) % len(B)]
        outside = _clip_half(current, a, b, False)
        if len(outside) >= 3 and abs(_poly_area2(outside)) > eps:
            pieces.append(outside)
        current = _clip_half(current, a, b, True)
        if len(current) < 3:
            break
    return pieces


def _ears(pts):
    """Ear-clipping triangulation of a simple 2D polygon (counter-clockwise);
    returns triangles as lists of points."""
    idx = list(range(len(pts)))
    tris = []
    guard = 0
    while len(idx) > 3 and guard < 10 * len(pts):
        guard += 1
        n = len(idx)
        found = False
        for k in range(n):
            i0, i1, i2 = idx[k - 1], idx[k], idx[(k + 1) % n]
            a, b, c = pts[i0], pts[i1], pts[i2]
            if (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) <= 0:
                continue                             # a reflex corner, not an ear
            ok = True
            for j in idx:
                if j in (i0, i1, i2):
                    continue
                p = pts[j]
                s1 = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
                s2 = (c[0] - b[0]) * (p[1] - b[1]) - (c[1] - b[1]) * (p[0] - b[0])
                s3 = (a[0] - c[0]) * (p[1] - c[1]) - (a[1] - c[1]) * (p[0] - c[0])
                if s1 > 0 and s2 > 0 and s3 > 0:
                    ok = False
                    break
            if ok:
                tris.append([a, b, c])
                del idx[k]
                found = True
                break
        if not found:
            break
    if len(idx) == 3:
        tris.append([pts[idx[0]], pts[idx[1]], pts[idx[2]]])
    return tris


def _convex_pieces(pts):
    """A counter-clockwise 2D polygon as convex pieces: itself if convex,
    ear triangles otherwise."""
    n = len(pts)
    for i in range(n):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % n]
        if (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) < 0:
            return _ears(pts)
    return [pts]


def _ear_triangles(pts):
    """Ear clipping of a simple counter-clockwise 2D polygon: the triangles
    as index triples, or None when no ear can be found (an outline that
    crosses itself)."""
    idx = list(range(len(pts)))
    tris = []
    while len(idx) > 3:
        n = len(idx)
        for k in range(n):
            i0, i1, i2 = idx[k - 1], idx[k], idx[(k + 1) % n]
            a, b, c = pts[i0], pts[i1], pts[i2]
            if (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) <= 0:
                continue                             # a reflex (or straight) corner is no ear
            blocked = False
            for j in idx:
                if j == i0 or j == i1 or j == i2:
                    continue
                q = pts[j]
                if ((b[0] - a[0]) * (q[1] - a[1]) - (b[1] - a[1]) * (q[0] - a[0]) >= 0 and
                        (c[0] - b[0]) * (q[1] - b[1]) - (c[1] - b[1]) * (q[0] - b[0]) >= 0 and
                        (a[0] - c[0]) * (q[1] - c[1]) - (a[1] - c[1]) * (q[0] - c[0]) >= 0):
                    blocked = True                   # another corner inside: cutting here would overlap
                    break
            if not blocked:
                tris.append((i0, i1, i2))
                del idx[k]
                break
        else:
            return None
    tris.append((idx[0], idx[1], idx[2]))
    return tris


def _is_concave(M, f, n=None):
    """Does face ``f`` turn the wrong way anywhere along its outline?  A
    convex polygon turns the same way as its normal at every corner."""
    k = len(f)
    if k < 4:
        return False
    n = n or _face_normal(M, f)
    ln = math.sqrt(n[0] * n[0] + n[1] * n[1] + n[2] * n[2])
    if ln < 1e-12:
        return False
    nx, ny, nz = n[0] / ln, n[1] / ln, n[2] / ln
    P = [M.V[i] for i in f]
    for i in range(k):
        a, b, c = P[i - 1], P[i], P[(i + 1) % k]
        e1x, e1y, e1z = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        e2x, e2y, e2z = c[0] - b[0], c[1] - b[1], c[2] - b[2]
        turn = ((e1y * e2z - e1z * e2y) * nx + (e1z * e2x - e1x * e2z) * ny + (e1x * e2y - e1y * e2x) * nz)
        if turn < -1e-9 * (e1x * e1x + e1y * e1y + e1z * e1z + e2x * e2x + e2y * e2y + e2z * e2z):
            return True
    return False


def _split_concave(M):
    """Cut every face that is not convex into triangles (in place).

    A viewer draws a polygon as a fan of triangles from its first corner,
    which is right for a convex outline and wrong for any other: the fan
    covers the notch -- the stair hole in a floor, the inside corner of an
    L-shaped slab.  Ear clipping in the face's own plane gives triangles
    that cover exactly the polygon, turning the same way as the face.
    Convex faces are left as they are.  Returns how many faces were cut."""
    newF, newC, newUV = [], [], []
    count = 0
    for k, f in enumerate(M.F):
        tris = None
        if len(f) > 3:
            n = _face_normal(M, f)
            if _is_concave(M, f, n):
                u, v, w = _frame(n)
                pts = [(_dot(M.V[i], u), _dot(M.V[i], v)) for i in f]
                order = list(range(len(f)))
                flip = _poly_area2(pts) < 0
                if flip:
                    order.reverse()
                    pts = pts[::-1]
                ears = _ear_triangles(pts)
                if ears is not None:
                    tris = []
                    for a, b, c in ears:
                        t = [order[a], order[b], order[c]]
                        if flip:
                            t.reverse()
                        tris.append(t)
        uv = M.UV[k] if M.UV is not None else None
        if tris is None:
            newF.append(f)
            newC.append(M.C[k])
            newUV.append(uv)
            continue
        count += 1
        for t in tris:
            newF.append([f[i] for i in t])
            newC.append(M.C[k])
            newUV.append(None if uv is None else [uv[i] for i in t])
    if count:
        M.F, M.C = newF, newC
        if M.UV is not None:
            M.UV = newUV
    return count


def concave_faces(M=None):
    """How many faces are not convex.  A viewer draws a polygon as a fan
    from its first corner, so such a face shows wrongly -- the fan covers
    its notch.  :func:`clean` (and :func:`save`) cut them into triangles."""
    M = as_mesh(M)
    return sum(1 for f in M.F if len(f) > 3 and _is_concave(M, f))


def _overlap_groups(M, tol):
    """Faces grouped by their plane -- whichever way they face: a slab
    standing on a floor overlaps it just as a tile laid on it does -- each
    as a counter-clockwise 2D polygon in the plane's frame:
    ``{key: (u, v, n, [(area, index, pts2d, bbox, flipped), ...])}``, where
    ``flipped`` says the face looks the other way than the frame's normal."""
    groups = {}
    for i, f in enumerate(M.F):
        if len(f) < 3:
            continue
        n = _face_normal(M, f)
        ln = _norm(n)
        if ln < 1e-12:
            continue
        n = (n[0] / ln, n[1] / ln, n[2] / ln)
        c = [0.0, 0.0, 0.0]
        for k in f:
            p = M.V[k]
            c[0] += p[0]
            c[1] += p[1]
            c[2] += p[2]
        d = _dot(n, c) / len(f)
        nk = (round(n[0], 3), round(n[1], 3), round(n[2], 3))
        if nk < (0.0, 0.0, 0.0) or nk == (0.0, 0.0, 0.0) and n[2] < 0:   # one key for both sides of a plane
            nk, d = (-nk[0] + 0.0, -nk[1] + 0.0, -nk[2] + 0.0), -d
        key = nk + (round(d / tol) * tol,)
        groups.setdefault(key, []).append(i)
    out = {}
    for key, idx in groups.items():
        if len(idx) < 2:
            continue
        n = _unit((key[0], key[1], key[2]))
        u, v, w = _frame(n)
        polys = []
        for i in idx:
            pts = [(_dot(M.V[k], u), _dot(M.V[k], v)) for k in M.F[i]]
            area2 = _poly_area2(pts)
            flipped = area2 < 0
            if flipped:
                pts = pts[::-1]
                area2 = -area2
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            polys.append((area2 / 2.0, i, pts, (min(xs), min(ys), max(xs), max(ys)), flipped))
        out[key] = (u, v, n, polys)
    return out


def _convex_overlap2(A, B):
    """Twice the area of the intersection of two convex counter-clockwise polygons."""
    inside = A
    for i in range(len(B)):
        inside = _clip_half(inside, B[i], B[(i + 1) % len(B)], True)
        if len(inside) < 3:
            return 0.0
    return abs(_poly_area2(inside))


def _minus_all(pieces, others, eps, limit=64):
    """``pieces`` (convex polygons) with every polygon of ``others`` taken
    away; stops early, returning None, when the result would shatter into
    more than ``limit`` pieces."""
    for other in others:
        pieces = [q for part in pieces for q in _convex_minus(part, other, eps)]
        if len(pieces) > limit:
            return None
    return pieces


def _overlap_scan(M, tol, cut):
    """The engine behind :func:`overlaps` and :func:`_cut_overlaps`: walk
    every plane group largest face first and find the kept faces each one
    overlaps (a grid of cells makes this fast for thousands of faces in one
    plane, such as a floor of tiles).

    Faces looking the same way: the smaller one is cut back to the pieces
    outside the bigger (the bigger wins, the flicker goes).  Faces looking
    opposite ways -- two solids touching, a box on a floor -- meet on a
    patch nobody can see: it is cut out of both, which is what a union of
    the two solids would leave.  A face that would shatter into more than
    64 pieces (a floor under a thousand boxes) is left whole, and so are
    the faces touching it.

    Returns ``(count, replaced)``; ``replaced`` maps a face index to
    ``(pieces, u, v, n, d, flipped)``."""
    touched = set()
    replaced = {}
    for key, (u, v, n, polys) in _overlap_groups(M, tol).items():
        polys.sort(key=lambda t: -t[0])
        largest = polys[0][0]
        eps = 1e-9 * (1.0 + largest)
        cell = max(1e-6, math.sqrt(max(1e-12, polys[len(polys) // 2][0])) * 2.0)
        grid = {}
        big = []                                     # a few big faces: checked against everyone
        drawn = {}                                   # face -> its convex pieces as drawn
        current = {}                                 # face -> its pieces now
        flip = {}
        contacts = {}                                # bigger face -> smaller faces lying on its back

        def cells(bb):
            return (int(math.floor(bb[0] / cell)), int(math.floor(bb[1] / cell)),
                    int(math.floor(bb[2] / cell)), int(math.floor(bb[3] / cell)))

        def keep(entry, bb):
            x0, y0, x1, y1 = cells(bb)
            if (x1 - x0 + 1) * (y1 - y0 + 1) > 400:
                big.append(entry)
                return
            for cx in range(x0, x1 + 1):
                for cy in range(y0, y1 + 1):
                    grid.setdefault((cx, cy), []).append(entry)

        for area, i, pts, bb, flipped in polys:
            x0, y0, x1, y1 = cells(bb)
            seen = set()
            candidates = list(big)
            for cx in range(x0, x1 + 1):
                for cy in range(y0, y1 + 1):
                    for entry in grid.get((cx, cy), ()):
                        if id(entry) not in seen:
                            seen.add(id(entry))
                            candidates.append(entry)
            own = _convex_pieces(pts)                # the face as it was drawn
            pieces = own
            changed = False
            for k, kbb in candidates:
                if bb[0] >= kbb[2] or bb[2] <= kbb[0] or bb[1] >= kbb[3] or bb[3] <= kbb[1]:
                    continue
                kpieces = drawn[k]
                if flip[k] != flipped:               # back to back: remember the contact
                    if any(_convex_overlap2(a, b) > eps for a in pieces for b in kpieces):
                        contacts.setdefault(k, []).append(i)
                    continue
                new_pieces = []
                for piece in pieces:
                    parts = [piece]
                    for other in kpieces:
                        parts = [q for part in parts for q in _convex_minus(part, other, eps)]
                    if len(parts) != 1 or parts[0] is not piece:
                        changed = True
                    new_pieces.extend(parts)
                pieces = new_pieces
                if changed and (not cut or len(pieces) > 64):
                    break
            if changed:
                touched.add(i)
                if cut and len(pieces) <= 64:
                    replaced[i] = (pieces, u, v, n, key[3], flipped)
            # later, smaller faces are cut against the face as drawn: the same
            # result as against its pieces, with far less to compare
            drawn[i] = own
            current[i] = pieces if (cut and len(pieces) <= 64) else own
            flip[i] = flipped
            keep((i, bb), bb)
        for k, small in contacts.items():            # the patches where solids touch
            if not cut:
                touched.add(k)
                touched.update(small)
                continue
            rest = _minus_all(current[k], [q for i in small for q in current[i]], eps)
            if rest is None:
                continue                             # the bigger face would shatter: leave the contact
            replaced[k] = (rest, u, v, n, key[3], flip[k])
            current[k] = rest
            touched.add(k)
            for i in small:
                left = _minus_all(current[i], drawn[k], eps)
                if left is not None:
                    replaced[i] = (left, u, v, n, key[3], flip[i])
                    current[i] = left
                    touched.add(i)
    return len(touched), replaced


def overlaps(M=None, tol=1e-3):
    """How many faces lie in the same plane as a bigger face and overlap it,
    facing the same way (they flicker in a viewer) or the opposite way (a
    box standing on a floor: its bottom flickers through the floor in a
    viewer that draws both sides).  :func:`clean` (and :func:`save`) cut
    them back; see also :func:`check`."""
    return _overlap_scan(as_mesh(M), tol, False)[0]


def _cut_overlaps(M, tol=1e-3):
    """Where two faces lie in one plane and overlap -- facing the same way
    or opposite ways -- cut the smaller one back so that only the larger
    covers the shared patch (in place).  This is what stops the flicker
    between the side of a beam and the face of the wall it runs into, and
    takes the bottom off a chest standing on a floor.  Returns how many
    faces were cut."""
    count, replaced = _overlap_scan(M, tol, True)
    if not replaced:
        return 0
    keep_idx = [i for i in range(len(M.F)) if i not in replaced]
    new_F, new_C, new_UV = [], [], []
    for i, (pieces, u, v, n, d, flipped) in replaced.items():
        f = M.F[i]
        base = [n[0] * d, n[1] * d, n[2] * d]        # a point of the plane
        # texture coordinates: the affine map of the original corners, if any
        uv = M.UV[i] if M.UV is not None else None
        affine = None
        if uv is not None and len(f) >= 3:
            P2 = [(_dot(M.V[k], u), _dot(M.V[k], v)) for k in f]
            for a in range(len(f)):
                b, c = (a + 1) % len(f), (a + 2) % len(f)
                det = ((P2[b][0] - P2[a][0]) * (P2[c][1] - P2[a][1])
                       - (P2[c][0] - P2[a][0]) * (P2[b][1] - P2[a][1]))
                if abs(det) > 1e-12:
                    affine = (P2[a], P2[b], P2[c], uv[a], uv[b], uv[c], det)
                    break
        for piece in pieces:
            if len(piece) < 3 or abs(_poly_area2(piece)) <= 1e-12:
                continue
            idx = []
            piece_uv = [] if affine else None
            for s_, t_ in piece:
                idx.append(M.add_vertex([base[0] + u[0] * s_ + v[0] * t_,
                                         base[1] + u[1] * s_ + v[1] * t_,
                                         base[2] + u[2] * s_ + v[2] * t_]))
                if affine:
                    a, b, c, ua, ub, uc, det = affine
                    l1 = ((s_ - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (t_ - a[1])) / det
                    l2 = ((b[0] - a[0]) * (t_ - a[1]) - (s_ - a[0]) * (b[1] - a[1])) / det
                    piece_uv.append((ua[0] + l1 * (ub[0] - ua[0]) + l2 * (uc[0] - ua[0]),
                                     ua[1] + l1 * (ub[1] - ua[1]) + l2 * (uc[1] - ua[1])))
            if flipped:                              # the face looked the other way: keep it so
                idx.reverse()
                if piece_uv:
                    piece_uv.reverse()
            new_F.append(idx)
            new_C.append(M.C[i])
            new_UV.append(piece_uv)
    _keep_faces(M, keep_idx)
    M.F.extend(new_F)
    M.C.extend(new_C)
    if M.UV is not None:
        M.UV.extend(new_UV)
    elif any(t is not None for t in new_UV):
        M.UV = [None] * (len(M.F) - len(new_F)) + new_UV
    return count


def triangulate(M=None):
    """Return a copy in which every face is a triangle (fan triangulation)."""
    M = as_mesh(M)
    out = Mesh([list(p) for p in M.V], [], [])
    for k, (f, c) in enumerate(zip(M.F, M.C)):
        uv = M.UV[k] if M.UV is not None else None
        for t in range(1, len(f) - 1):
            out.add_face([f[0], f[t], f[t + 1]], c,
                         None if uv is None else [uv[0], uv[t], uv[t + 1]])
    return out


def fix_normals(M=None, outward=True):
    """Make every face of a copy point the same way -- and, if the model is
    closed, point outward.

    Faces are walked from neighbour to neighbour: two faces that share an edge
    must run along it in opposite directions.  Each connected piece is then
    flipped as a whole if its volume came out negative.
    """
    M = as_mesh(M).copy()
    edge_faces = {}
    for i, f in enumerate(M.F):
        n = len(f)
        for t in range(n):
            a, b = f[t], f[(t + 1) % n]
            edge_faces.setdefault((a, b) if a < b else (b, a), []).append(i)

    visited = [False] * len(M.F)
    for start in range(len(M.F)):
        if visited[start]:
            continue
        component = [start]
        visited[start] = True
        stack = [start]
        while stack:
            i = stack.pop()
            f = M.F[i]
            n = len(f)
            for t in range(n):
                a, b = f[t], f[(t + 1) % n]
                key = (a, b) if a < b else (b, a)
                for j in edge_faces.get(key, ()):
                    if visited[j]:
                        continue
                    g = M.F[j]
                    m = len(g)
                    same = False
                    for s in range(m):
                        if g[s] == a and g[(s + 1) % m] == b:
                            same = True
                            break
                    if same:                       # neighbour disagrees
                        g.reverse()
                        if M.UV is not None and M.UV[j] is not None:
                            M.UV[j].reverse()
                    visited[j] = True
                    component.append(j)
                    stack.append(j)
        if outward:
            part = Mesh(M.V, [M.F[i] for i in component],
                        [M.C[i] for i in component])
            if _signed_volume(part, 0) < 0:
                for i in component:
                    M.F[i].reverse()
                    if M.UV is not None and M.UV[i] is not None:
                        M.UV[i].reverse()
    return M


def clean(M=None, tol=1e-7, weld=True, degenerate=True, duplicates=True,
          internal=True, unused=True, normals=False, report=False, overlaps=True, convex=True):
    """Repair a model and return the tidy copy.

    By default it welds coincident vertices, throws away zero-area faces
    (and splits faces pinched at a vertex), removes repeated faces, removes
    the walls buried where two solids touch, and cuts back faces that lie
    in one plane and overlap: the smaller of two looking the same way (the
    faces that flicker in a viewer), and the patch where two solids stand
    on each other, out of both (``overlaps``; see :func:`overlaps`).
    Finally a face that is not convex is cut into triangles (``convex``;
    see :func:`concave_faces`), because a viewer would fan it over its notch.
    Pass ``normals=True`` to also make every face point outward, and
    ``report=True`` to get ``(mesh, report_dict)`` instead of just the mesh::

        model = add.clean(add.layer())
        add.mesh(model)
    """
    M = as_mesh(M).copy()
    info = {"vertices_removed": 0, "faces_removed": 0, "faces_cut": 0, "faces_split": 0}
    n = len(M.V)
    info["faces_removed"] += _drop_not_finite(M)     # a vertex that is not a number cannot be mended
    info["vertices_removed"] += n - len(M.V)
    if weld:
        info["vertices_removed"] += _weld(M, tol)
    if degenerate:
        info["faces_removed"] += _drop_degenerate(M)
    if internal:
        info["faces_removed"] += _drop_internal(M)
    if duplicates:
        info["faces_removed"] += _dedup_faces(M)
    if overlaps:
        info["faces_cut"] += _cut_overlaps(M)
        if info["faces_cut"] and weld:
            _weld(M, tol)                            # the new corners meet their neighbours ...
            M = heal(M, tol)                         # ... and the neighbours' long edges learn of them
            if degenerate:                           # a corner welded onto its neighbour can leave a face
                info["faces_removed"] += _drop_degenerate(M)   # visiting a vertex twice, or without area
            if duplicates:
                info["faces_removed"] += _dedup_faces(M)
    if convex:
        info["faces_split"] += _split_concave(M)
    if normals:
        M = fix_normals(M)
    if unused:
        info["vertices_removed"] += _drop_unused(M)
    if report:
        return M, info
    return M


# ============================================================================
# 21. Looking at a model
# ============================================================================

def stats(M=None):
    """A dictionary describing the model: counts, size, area, volume, health."""
    M = as_mesh(M)
    lo, hi = bbox(M)
    edges = {}
    for f in M.F:
        n = len(f)
        for t in range(n):
            a, b = f[t], f[(t + 1) % n]
            key = (a, b) if a < b else (b, a)
            edges[key] = edges.get(key, 0) + 1
    open_edges = sum(1 for v in edges.values() if v == 1)
    odd_edges = sum(1 for v in edges.values() if v > 2)
    spots = {}
    for p in M.V:                                    # vertices sitting on the same spot
        spots[(round(p[0], 6), round(p[1], 6), round(p[2], 6))] = 1
    duplicate_vertices = len(M.V) - len(spots)
    groups = {}
    for f in M.F:
        groups.setdefault(tuple(sorted(f)), []).append(f)
    duplicate_faces = back_to_back = 0
    for same in groups.values():
        if len(same) < 2:
            continue
        forward = sum(1 for f in same if _winding(f))
        backward = len(same) - forward
        back_to_back += min(forward, backward)
        duplicate_faces += len(same) - 1 - min(forward, backward)
    return {
        "vertices": len(M.V),
        "faces": len(M.F),
        "triangles": sum(max(0, len(f) - 2) for f in M.F),
        "colors": len(set(M.C)),
        "bbox": [lo, hi],
        "size": [hi[a] - lo[a] for a in range(3)],
        "area": area(M),
        "volume": volume(M),
        "open_edges": open_edges,
        "non_manifold_edges": odd_edges,
        "duplicate_vertices": duplicate_vertices,
        "duplicate_faces": duplicate_faces,
        "back_to_back_faces": back_to_back,
        "closed": open_edges == 0,
        "obj_bytes": obj_size(M),
        "transparent_faces": sum(1 for c in M.C if len(c) > 3 and c[3] < 1.0),
        "textures": sorted(set(c[4] for c in M.C if len(c) > 4)),
    }


#: Sketchfab: files up to 100 MB on the free plan (the course asks for 50)
#: and at most 100 materials, i.e. colours in an ``.obj`` (50 to be safe).
SKETCHFAB_MB = 50
SKETCHFAB_COLORS = 50


def check(M=None, min_faces=10000, min_colors=3, quiet=False,
          max_mb=SKETCHFAB_MB, max_colors=SKETCHFAB_COLORS):
    """Print a health report and say whether the model meets the assignment.

    The course asks for at least 10000 polygons and at least 3 colours, and
    an ``.obj`` that Sketchfab will take: under ``max_mb`` megabytes and
    ``max_colors`` colours (each colour is a material there).  This tells
    you where you stand and what still needs repairing::

        add.check()          # look at the current scene

    Returns ``True`` when every requirement is met.
    """
    s = stats(M)
    mb = s["obj_bytes"] / 1e6
    fits = mb <= max_mb and s["colors"] <= max_colors
    ok = s["faces"] >= min_faces and s["colors"] >= min_colors and fits
    if not quiet:
        mark = lambda good: "OK " if good else "!! "
        print("-" * 56)
        print("  vertices            %d" % s["vertices"])
        print("%s polygons            %d  (need %d)"
              % (mark(s["faces"] >= min_faces), s["faces"], min_faces))
        print("%s colours             %d  (need %d, at most %d materials for Sketchfab)"
              % (mark(min_colors <= s["colors"] <= max_colors), s["colors"],
                 min_colors, max_colors))
        print("%s .obj file size      %.1f MB  (at most %d MB for Sketchfab)"
              % (mark(mb <= max_mb), mb, max_mb))
        print("   size                %.3f x %.3f x %.3f" % tuple(s["size"]))
        print("   surface area        %.3f" % s["area"])
        if s["closed"]:
            why = "yes"
        else:
            why = "no, %d edges have nothing on the other side" % s["open_edges"]
        print("%s closed surface      %s" % (mark(s["closed"]), why))
        if s["non_manifold_edges"]:
            print("   repeated edges      %d   (an edge shared by more than two faces:"
                  " parts meet along it; normal for voxel models)" % s["non_manifold_edges"])
        if s["duplicate_vertices"]:
            print("!! repeated vertices   %d   (two vertices on one spot -- add.clean() welds them)"
                  % s["duplicate_vertices"])
        if s["duplicate_faces"]:
            print("!! repeated faces      %d   -- add.clean() removes them"
                  % s["duplicate_faces"])
        if s["back_to_back_faces"]:
            print("   back-to-back faces  %d   (fine for a two-sided sheet;"
                  " add.clean() removes them)" % s["back_to_back_faces"])
        flicker = overlaps(M)
        if flicker:
            print("!! overlapping faces   %d   (lying on a bigger face in the same plane:"
                  " they flicker in a viewer -- add.clean() cuts them)" % flicker)
        notched = concave_faces(M)
        if notched:
            print("!! non-convex faces    %d   (a viewer draws a polygon as a fan and"
                  " covers its notch -- add.clean() cuts them into triangles)" % notched)
        if s["closed"]:
            print("   volume              %.3f" % s["volume"])
        if s["transparent_faces"]:
            print("   see-through faces   %d   (opacity is kept in .obj + .mtl)"
                  % s["transparent_faces"])
        if s["textures"]:
            print("   textures            %s   (put the images next to the .obj)"
                  % ", ".join(s["textures"]))
        if s["colors"] > max_colors:
            print("   hint: add.limit_colors(M, %d) or add.save(..., colors=%d)"
                  % (max_colors, max_colors))
        if mb > max_mb:
            print("   hint: fewer cells (a smaller k, grid or subdivisions)"
                  " make the file smaller")
        print("-" * 56)
    return ok

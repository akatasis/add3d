

# ============================================================================
# 18. Repairing a model
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


def _drop_degenerate(M, tol=1e-12):
    """Delete faces with no area and remove repeated corners (in place)."""
    F, C = [], []
    for f, c in zip(M.F, M.C):
        clean_f = []
        for i in f:                                  # drop repeated corners
            if not clean_f or clean_f[-1] != i:
                clean_f.append(i)
        if len(clean_f) > 1 and clean_f[0] == clean_f[-1]:
            clean_f.pop()
        if len(clean_f) < 3:
            continue
        if len(set(clean_f)) < 3:
            continue
        if _norm(_face_normal(M, clean_f)) <= tol:
            continue
        F.append(clean_f)
        C.append(c)
    removed = len(M.F) - len(F)
    M.F, M.C = F, C
    return removed


def _dedup_faces(M):
    """Delete repeats of a face that is already there (in place)."""
    seen = set()
    F, C = [], []
    for f, c in zip(M.F, M.C):
        key = tuple(sorted(f))
        if key in seen:
            continue
        seen.add(key)
        F.append(f)
        C.append(c)
    removed = len(M.F) - len(F)
    M.F, M.C = F, C
    return removed


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
    F = [f for i, f in enumerate(M.F) if i not in drop]
    C = [c for i, c in enumerate(M.C) if i not in drop]
    removed = len(M.F) - len(F)
    M.F, M.C = F, C
    return removed


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
    for f in M.F:
        n = len(f)
        out = []
        for i in range(n):
            a, b = f[i], f[(i + 1) % n]
            out.append(a)
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
                    last = v
        newF.append(out)
    M.F = newF
    return M


def triangulate(M=None):
    """Return a copy in which every face is a triangle (fan triangulation)."""
    M = as_mesh(M)
    out = Mesh([list(p) for p in M.V], [], [])
    for f, c in zip(M.F, M.C):
        for t in range(1, len(f) - 1):
            out.add_face([f[0], f[t], f[t + 1]], c)
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
                    visited[j] = True
                    component.append(j)
                    stack.append(j)
        if outward:
            part = Mesh(M.V, [M.F[i] for i in component],
                        [M.C[i] for i in component])
            if _signed_volume(part, 0) < 0:
                for i in component:
                    M.F[i].reverse()
    return M


def clean(M=None, tol=1e-7, weld=True, degenerate=True, duplicates=True,
          internal=True, unused=True, normals=False, report=False):
    """Repair a model and return the tidy copy.

    By default it welds coincident vertices, throws away zero-area faces,
    removes repeated faces and removes the walls buried where two solids
    touch.  Pass ``normals=True`` to also make every face point outward, and
    ``report=True`` to get ``(mesh, report_dict)`` instead of just the mesh::

        model = add.clean(add.layer())
        add.mesh(model)
    """
    M = as_mesh(M).copy()
    info = {"vertices_removed": 0, "faces_removed": 0}
    if weld:
        info["vertices_removed"] += _weld(M, tol)
    if degenerate:
        info["faces_removed"] += _drop_degenerate(M)
    if internal:
        info["faces_removed"] += _drop_internal(M)
    if duplicates:
        info["faces_removed"] += _dedup_faces(M)
    if normals:
        M = fix_normals(M)
    if unused:
        info["vertices_removed"] += _drop_unused(M)
    if report:
        return M, info
    return M


# ============================================================================
# 19. Looking at a model
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
        "duplicate_faces": duplicate_faces,
        "back_to_back_faces": back_to_back,
        "closed": open_edges == 0,
    }


def check(M=None, min_faces=10000, min_colors=3, quiet=False):
    """Print a health report and say whether the model meets the assignment.

    The course asks for at least 10000 polygons and at least 3 colours; this
    tells you where you stand and what still needs repairing::

        add.check()          # look at the current scene
    """
    s = stats(M)
    ok = s["faces"] >= min_faces and s["colors"] >= min_colors
    if not quiet:
        mark = lambda good: "OK " if good else "!! "
        print("-" * 56)
        print("  vertices            %d" % s["vertices"])
        print("%s polygons            %d  (need %d)"
              % (mark(s["faces"] >= min_faces), s["faces"], min_faces))
        print("%s colours             %d  (need %d)"
              % (mark(s["colors"] >= min_colors), s["colors"], min_colors))
        print("   size                %.3f x %.3f x %.3f" % tuple(s["size"]))
        print("   surface area        %.3f" % s["area"])
        if s["closed"]:
            why = "yes"
        else:
            why = "no, %d edges have nothing on the other side" % s["open_edges"]
        print("%s closed surface      %s" % (mark(s["closed"]), why))
        if s["non_manifold_edges"]:
            print("   touching edges      %d   (parts meet along an edge;"
                  " normal for voxel models)" % s["non_manifold_edges"])
        if s["duplicate_faces"]:
            print("!! repeated faces      %d   -- try add.clean()"
                  % s["duplicate_faces"])
        if s["back_to_back_faces"]:
            print("   back-to-back faces  %d   (fine for a two-sided sheet;"
                  " add.clean() removes them)" % s["back_to_back_faces"])
        if s["closed"]:
            print("   volume              %.3f" % s["volume"])
        print("-" * 56)
    return ok

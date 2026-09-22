

# ============================================================================
# 24. Smooth surfaces: Catmull-Clark and uniform n-grids
# ============================================================================
# A coarse polygon mesh -- a box with a corner pulled out, a dodecahedron, a
# letter -- can be treated as the *control net* of a smooth surface.
# Catmull-Clark subdivision (1978) rounds it by splitting every face into
# quads and averaging; done for ever it converges to the *limit surface*.
#
# ``catmull_clark`` is the classical step.  ``smooth`` goes further: it is
# the generalised algorithm of M. Sabaliauskas, "Uniform n-grids on
# Catmull-Clark limit surfaces of arbitrary polygon meshes" (2026).  For
# ANY n = 1, 2, 3, 4, 5 ... it puts n cells on every edge of the control
# mesh with all the new vertices *exactly* on the limit surface (classical
# subdivision only reaches n = 2, 4, 8 ...), and near the extraordinary
# vertices (valence != 4) and non-quad faces it reparameterises the surface
# so that the cells come out evenly sized.  The code below is a line-by-line
# port of the reference implementation (unisub.js / unisub.hpp) into plain
# Python, so that it too needs nothing but ``import add``.

class _Topo(object):
    """A polygon mesh with its edges and adjacency worked out.

    ``E[e] = [a, b, f0, f1]`` (f1 = -1 on a border), ``VF[v]`` faces at a
    vertex, ``VE[v]`` edges at a vertex, ``FE[f][k]`` the edge leaving
    corner ``k`` of face ``f``, ``FN[f][k]`` the face across that edge.
    """

    __slots__ = ("V", "F", "E", "VF", "VE", "FE", "FN", "boundary")

    def __init__(self, V, F):
        self.V = V
        self.F = F
        nv, nf = len(V), len(F)
        self.E = []
        self.VF = [[] for _ in range(nv)]
        self.VE = [[] for _ in range(nv)]
        self.FE = [None] * nf
        self.FN = [None] * nf
        emap = {}
        for f in range(nf):
            p = F[f]
            m = len(p)
            if m < 3:
                raise ValueError("face with fewer than 3 vertices")
            fe = [0] * m
            for k in range(m):
                a, b = p[k], p[(k + 1) % m]
                if a == b:
                    raise ValueError("degenerate edge in face %d" % f)
                key = (a, b) if a < b else (b, a)
                e = emap.get(key)
                if e is None:
                    e = len(self.E)
                    self.E.append([key[0], key[1], f, -1])
                    emap[key] = e
                    self.VE[a].append(e)
                    self.VE[b].append(e)
                else:
                    ed = self.E[e]
                    if ed[3] >= 0:
                        raise ValueError("non-manifold edge (more than two "
                                         "faces meet along it)")
                    if ed[2] == f:
                        raise ValueError("edge used twice by the same face")
                    ed[3] = f
                fe[k] = e
            self.FE[f] = fe
            for k in range(m):
                self.VF[p[k]].append(f)
        for f in range(nf):
            fe = self.FE[f]
            self.FN[f] = [self.E[e][3] if self.E[e][2] == f else self.E[e][2]
                          for e in fe]
        self.boundary = [False] * nv
        for ed in self.E:
            if ed[3] < 0:
                self.boundary[ed[0]] = True
                self.boundary[ed[1]] = True

    def all_quads(self):
        for f in self.F:
            if len(f) != 4:
                return False
        return True

    def centroid(self, f):
        p = self.F[f]
        n = float(len(p))
        return [sum(self.V[v][a] for v in p) / n for a in range(3)]

    def ordered_ring(self, v):
        """Neighbours and faces counter-clockwise around ``v``, or ``None``."""
        VF = self.VF[v]
        if not VF:
            return None
        start = VF[0]
        for f in VF:
            k = self.F[f].index(v)
            if self.FN[f][k] < 0:
                start = f
                break
        nbrs, faces = [], []
        f = start
        guard = 0
        while True:
            p = self.F[f]
            m = len(p)
            k = p.index(v)
            nxt, prv = p[(k + 1) % m], p[(k + m - 1) % m]
            if not faces:
                nbrs.append(nxt)
            faces.append(f)
            nbrs.append(prv)
            g = self.FN[f][(k + m - 1) % m]
            if g < 0:
                break
            if g == start:
                nbrs.pop()
                break
            f = g
            guard += 1
            if guard > len(VF) + 2:
                return None
        if len(faces) != len(VF):
            return None
        return nbrs, faces


def _cc_subdivide(T):
    """One Catmull-Clark step on a :class:`_Topo`.

    Returns ``(new topology, parent)`` where ``parent[i]`` is the face of
    ``T`` that new quad ``i`` came from.  New vertices are numbered: the old
    vertices first, then one per edge, then one per face.  Border edges and
    vertices follow the cubic B-spline curve rules, so an open sheet keeps
    a smooth rim, and a vertex with a single face stays where it is.
    """
    V, F, E = T.V, T.F, T.E
    nv, ne, nf = len(V), len(E), len(F)
    R = [None] * (nv + ne + nf)
    for f in range(nf):
        R[nv + ne + f] = T.centroid(f)
    for e in range(ne):
        a, b, f0, f1 = E[e]
        pa, pb = V[a], V[b]
        if f1 < 0:
            R[nv + e] = [(pa[0] + pb[0]) * 0.5, (pa[1] + pb[1]) * 0.5,
                         (pa[2] + pb[2]) * 0.5]
        else:
            c0, c1 = R[nv + ne + f0], R[nv + ne + f1]
            R[nv + e] = [(pa[0] + pb[0] + c0[0] + c1[0]) * 0.25,
                         (pa[1] + pb[1] + c0[1] + c1[1]) * 0.25,
                         (pa[2] + pb[2] + c0[2] + c1[2]) * 0.25]
    for v in range(nv):
        p = V[v]
        VF, VE = T.VF[v], T.VE[v]
        if not VF:
            R[v] = list(p)
            continue
        if T.boundary[v]:
            if len(VF) <= 1:
                R[v] = list(p)
                continue
            s = [0.0, 0.0, 0.0]
            cnt = 0
            for e in VE:
                ed = E[e]
                if ed[3] < 0:
                    q = V[ed[1] if ed[0] == v else ed[0]]
                    s[0] += q[0]
                    s[1] += q[1]
                    s[2] += q[2]
                    cnt += 1
            if cnt != 2:
                R[v] = list(p)
                continue
            R[v] = [(s[0] + 6 * p[0]) / 8.0, (s[1] + 6 * p[1]) / 8.0,
                    (s[2] + 6 * p[2]) / 8.0]
        else:
            n = len(VE)
            Q = [0.0, 0.0, 0.0]
            Rm = [0.0, 0.0, 0.0]
            for f in VF:
                c = R[nv + ne + f]
                Q[0] += c[0]
                Q[1] += c[1]
                Q[2] += c[2]
            for e in VE:
                ed = E[e]
                pa, pb = V[ed[0]], V[ed[1]]
                Rm[0] += (pa[0] + pb[0]) * 0.5
                Rm[1] += (pa[1] + pb[1]) * 0.5
                Rm[2] += (pa[2] + pb[2]) * 0.5
            nfc = float(len(VF))
            R[v] = [(Q[0] / nfc + 2 * Rm[0] / n + (n - 3) * p[0]) / n,
                    (Q[1] / nfc + 2 * Rm[1] / n + (n - 3) * p[1]) / n,
                    (Q[2] / nfc + 2 * Rm[2] / n + (n - 3) * p[2]) / n]
    newF = []
    parent = []
    for f in range(nf):
        p = F[f]
        fe = T.FE[f]
        m = len(p)
        for k in range(m):
            newF.append([p[k], nv + fe[k], nv + ne + f, nv + fe[(k + m - 1) % m]])
            parent.append(f)
    return _Topo(R, newF), parent


def _cc_lambda(N):
    """Subdominant eigenvalue of the Catmull-Clark subdivision matrix."""
    if N == 4:
        return 0.5
    c = math.cos(2 * math.pi / N)
    return (c + 5 + math.sqrt((c + 1) * (c + 9))) / 16.0


def _cc_gamma(N):
    """Exponent of the radial reparameterisation at a valence-N vertex:
    ``gamma = -1 / log2(lambda_N)`` (1 for the regular valence 4)."""
    if N == 4:
        return 1.0
    return 1.0 / (-math.log(_cc_lambda(N), 2))


def _cc_limit_positions(T):
    """Limit position of every vertex of a quad topology (exact formula).

    A mesh with other polygons is subdivided once first -- after that step
    the formula is exact for the original vertices too.
    """
    if not T.all_quads():
        S, parent = _cc_subdivide(T)
        return _cc_limit_positions(S)[:len(T.V)]
    V, E = T.V, T.E
    L = [None] * len(V)
    for v in range(len(V)):
        p = V[v]
        VF = T.VF[v]
        if not VF:
            L[v] = list(p)
            continue
        if T.boundary[v]:
            if len(VF) <= 1:
                L[v] = list(p)
                continue
            s = [0.0, 0.0, 0.0]
            cnt = 0
            for e in T.VE[v]:
                ed = E[e]
                if ed[3] < 0:
                    q = V[ed[1] if ed[0] == v else ed[0]]
                    s[0] += q[0]
                    s[1] += q[1]
                    s[2] += q[2]
                    cnt += 1
            if cnt != 2:
                L[v] = list(p)
                continue
            L[v] = [(s[0] + 4 * p[0]) / 6.0, (s[1] + 4 * p[1]) / 6.0,
                    (s[2] + 4 * p[2]) / 6.0]
        else:
            ring = T.ordered_ring(v)
            if ring is None:
                L[v] = list(p)
                continue
            nbrs, faces = ring
            n = len(nbrs)
            se = [0.0, 0.0, 0.0]
            sf = [0.0, 0.0, 0.0]
            for j in range(n):
                q = V[nbrs[j]]
                se[0] += q[0]
                se[1] += q[1]
                se[2] += q[2]
                poly = T.F[faces[j]]
                d = V[poly[(poly.index(v) + 2) % 4]]
                sf[0] += d[0]
                sf[1] += d[1]
                sf[2] += d[2]
            den = float(n * (n + 5))
            L[v] = [(n * n * p[0] + 4 * se[0] + sf[0]) / den,
                    (n * n * p[1] + 4 * se[1] + sf[1]) / den,
                    (n * n * p[2] + 4 * se[2] + sf[2]) / den]
    return L


def _cc_limit_tangents(T, v):
    """Two tangent vectors of the limit surface at an inner vertex."""
    if T.boundary[v]:
        return None
    ring = T.ordered_ring(v)
    if ring is None:
        return None
    nbrs, faces = ring
    for f in faces:
        if len(T.F[f]) != 4:
            S, parent = _cc_subdivide(T)
            return _cc_limit_tangents(S, v)
    n = len(nbrs)
    c = math.cos(2 * math.pi / n)
    A = 1 + c + math.sqrt((c + 1) * (c + 9))
    t1 = [0.0, 0.0, 0.0]
    t2 = [0.0, 0.0, 0.0]
    for j in range(n):
        a0 = 2 * math.pi * j / n
        a1 = 2 * math.pi * (j + 1) / n
        poly = T.F[faces[j]]
        fj = T.V[poly[(poly.index(v) + 2) % 4]]
        e = T.V[nbrs[j]]
        w1, w2 = A * math.cos(a0), math.cos(a0) + math.cos(a1)
        s1, s2 = A * math.sin(a0), math.sin(a0) + math.sin(a1)
        for a in range(3):
            t1[a] += e[a] * w1 + fj[a] * w2
            t2[a] += e[a] * s1 + fj[a] * s2
    return t1, t2


def _bspline_basis(t):
    """The four uniform cubic B-spline basis functions at ``t`` in [0, 1]."""
    t2 = t * t
    t3 = t2 * t
    return ((1 - 3 * t + 3 * t2 - t3) / 6.0, (4 - 6 * t2 + 3 * t3) / 6.0,
            (1 + 3 * t + 3 * t2 - 3 * t3) / 6.0, t3 / 6.0)


def _eval_bicubic(P, u, v):
    """Point of the bicubic B-spline patch with 4x4 control net ``P[i][j]``."""
    Nu = _bspline_basis(u)
    Nv = _bspline_basis(v)
    x = y = z = 0.0
    for i in range(4):
        wi = Nu[i]
        if wi == 0.0:
            continue
        row = P[i]
        for j in range(4):
            w = wi * Nv[j]
            c = row[j]
            x += c[0] * w
            y += c[1] * w
            z += c[2] * w
    return [x, y, z]


def _regular_stencil(T, f):
    """The 4x4 control net of quad ``f`` when its surroundings are regular
    (all valences 4, all faces quads), or ``None``.

    Missing rows along a border are reflected (``2a - b``), which is the
    B-spline curve rule for the rim.
    """
    q = T.F[f]
    if len(q) != 4:
        return None
    V = T.V
    P = [[None] * 4 for _ in range(4)]
    have = [[0] * 4 for _ in range(4)]
    P[1][1], P[2][1], P[2][2], P[1][2] = V[q[0]], V[q[1]], V[q[2]], V[q[3]]
    have[1][1] = have[2][1] = have[2][2] = have[1][2] = 1
    ci = (1, 2, 2, 1)
    cj = (1, 1, 2, 2)
    for k in range(4):
        v = q[k]
        bnd = T.boundary[v]
        nfc = len(T.VF[v])
        if not bnd and (nfc != 4 or len(T.VE[v]) != 4):
            return None
        if bnd and nfc > 2:
            return None
        ring = T.ordered_ring(v)
        if ring is None:
            return None
        nb, fc = ring
        for g in fc:
            if len(T.F[g]) != 4:
                return None
        vn, vp = q[(k + 1) % 4], q[(k + 3) % 4]
        dn = (ci[(k + 1) % 4] - ci[k], cj[(k + 1) % 4] - cj[k])
        dp = (ci[(k + 3) % 4] - ci[k], cj[(k + 3) % 4] - cj[k])
        n = len(nb)
        if vn not in nb:
            return None
        s = nb.index(vn)
        if nb[(s + 1) % n] != vp:
            return None
        dirs = (dn, dp, (-dn[0], -dn[1]), (-dp[0], -dp[1]))
        for idx in range(n):
            off = (idx - s) % 4
            gi, gj = ci[k] + dirs[off][0], cj[k] + dirs[off][1]
            if gi < 0 or gi > 3 or gj < 0 or gj > 3:
                return None
            P[gi][gj] = V[nb[idx]]
            have[gi][gj] = 1
        for idx in range(len(fc)):
            off = (idx - s) % 4
            poly = T.F[fc[idx]]
            diag = poly[(poly.index(v) + 2) % 4]
            gi = ci[k] + dirs[off][0] + dirs[(off + 1) % 4][0]
            gj = cj[k] + dirs[off][1] + dirs[(off + 1) % 4][1]
            if gi < 0 or gi > 3 or gj < 0 or gj > 3:
                return None
            P[gi][gj] = V[diag]
            have[gi][gj] = 1
    miss = (not have[0][1] and not have[0][2], not have[3][1] and not have[3][2],
            not have[1][0] and not have[2][0], not have[1][3] and not have[2][3])
    if (have[0][1] != have[0][2] or have[3][1] != have[3][2]
            or have[1][0] != have[2][0] or have[1][3] != have[2][3]):
        return None

    def refl(a, b):
        return [2 * a[0] - b[0], 2 * a[1] - b[1], 2 * a[2] - b[2]]

    def bil(a, b, c):
        return [a[0] + b[0] - c[0], a[1] + b[1] - c[1], a[2] + b[2] - c[2]]

    for t in (1, 2):
        if miss[0]:
            P[0][t] = refl(P[1][t], P[2][t])
        if miss[1]:
            P[3][t] = refl(P[2][t], P[1][t])
        if miss[2]:
            P[t][0] = refl(P[t][1], P[t][2])
        if miss[3]:
            P[t][3] = refl(P[t][2], P[t][1])
    if not have[0][0]:
        P[0][0] = (refl(P[1][0], P[2][0]) if miss[0] else
                   refl(P[0][1], P[0][2]) if miss[2] else
                   bil(P[0][1], P[1][0], P[1][1]))
    if not have[3][0]:
        P[3][0] = (refl(P[2][0], P[1][0]) if miss[1] else
                   refl(P[3][1], P[3][2]) if miss[2] else
                   bil(P[3][1], P[2][0], P[2][1]))
    if not have[0][3]:
        P[0][3] = (refl(P[1][3], P[2][3]) if miss[0] else
                   refl(P[0][2], P[0][1]) if miss[3] else
                   bil(P[0][2], P[1][3], P[1][2]))
    if not have[3][3]:
        P[3][3] = (refl(P[2][3], P[1][3]) if miss[1] else
                   refl(P[3][2], P[3][1]) if miss[3] else
                   bil(P[3][2], P[2][3], P[2][2]))
    return P


def _neighbourhood(T, f, origin_corner):
    """The faces around face ``f`` as a small mesh of their own, with ``f``
    first and its corners rotated so that ``origin_corner`` comes first."""
    faces = [f]
    seen = set([f])
    for v in T.F[f]:
        for g in T.VF[v]:
            if g not in seen:
                seen.add(g)
                faces.append(g)
    vmap = {}
    LV, LF = [], []
    for g in faces:
        poly = T.F[g]
        m = len(poly)
        start = origin_corner if g == f else 0
        out = []
        for k in range(m):
            v = poly[(start + k) % m]
            idx = vmap.get(v)
            if idx is None:
                idx = len(LV)
                LV.append(T.V[v])
                vmap[v] = idx
            out.append(idx)
        LF.append(out)
    return _Topo(LV, LF)


class _PatchTree(object):
    """Evaluates the limit surface over one quad next to an extraordinary
    vertex by subdividing its neighbourhood only as deep as a query needs
    (Algorithm 1 of the paper)."""

    __slots__ = ("root",)
    MAX_DEPTH = 48

    def __init__(self, T, f):
        self.root = self._node(_neighbourhood(T, f, 0), 0)

    @staticmethod
    def _node(L, depth):
        return {"M": L, "depth": depth, "P": _regular_stencil(L, 0),
                "child": [None, None, None, None], "sub": None}

    def _child(self, node, k):
        ch = node["child"][k]
        if ch is not None:
            return ch
        if node["sub"] is None:
            node["sub"], parent = _cc_subdivide(node["M"])
        origin = (0, 3, 2, 1)
        ch = self._node(_neighbourhood(node["sub"], k, origin[k]),
                        node["depth"] + 1)
        node["child"][k] = ch
        return ch

    def eval(self, u, v):
        node = self.root
        depth = 0
        while node["P"] is None:
            if depth >= self.MAX_DEPTH:
                L = _cc_limit_positions(node["M"])
                corner = (0 if v < 0.5 else 3) if u < 0.5 else (1 if v < 0.5 else 2)
                return L[node["M"].F[0][corner]]
            if u < 0.5:
                if v < 0.5:
                    k, u, v = 0, 2 * u, 2 * v
                else:
                    k, u, v = 3, 2 * u, 2 * v - 1
            else:
                if v < 0.5:
                    k, u, v = 1, 2 * u - 1, 2 * v
                else:
                    k, u, v = 2, 2 * u - 1, 2 * v - 1
            node = self._child(node, k)
            depth += 1
        return _eval_bicubic(node["P"], u, v)


def _nu_norm(a, b, p):
    """The paper's norm ``nu(s, t) = ((s^p + t^p) / (1 + s^p t^p))^(1/p)``."""
    if p > 64:
        return max(a, b)
    ap, bp = a ** p, b ** p
    return ((ap + bp) / (1 + ap * bp)) ** (1.0 / p)


class _PolygonDomain(object):
    """The regular m-gon in the plane, split into m kites
    ``[corner_k, edge_mid_k, centre, edge_mid_{k-1}]`` (Section 5 of the
    paper): the parameter domain of one control face."""

    __slots__ = ("m", "P", "E")
    _cache = {}

    def __init__(self, m):
        self.m = m
        self.P = [(math.cos(2 * math.pi * k / m), math.sin(2 * math.pi * k / m))
                  for k in range(m)]
        self.E = [((self.P[k][0] + self.P[(k + 1) % m][0]) / 2.0,
                   (self.P[k][1] + self.P[(k + 1) % m][1]) / 2.0)
                  for k in range(m)]

    @classmethod
    def get(cls, m):
        d = cls._cache.get(m)
        if d is None:
            d = cls._cache[m] = cls(m)
        return d

    def kite_map(self, k, u, v):
        a, b, d = self.P[k], self.E[k], self.E[(k + self.m - 1) % self.m]
        wa, wb, wd = (1 - u) * (1 - v), u * (1 - v), (1 - u) * v
        return (a[0] * wa + b[0] * wb + d[0] * wd,
                a[1] * wa + b[1] * wb + d[1] * wd)

    def kite_of(self, x):
        if x[0] == 0 and x[1] == 0:
            return 0
        t = math.atan2(x[1], x[0]) / (2 * math.pi) * self.m + 0.5
        return int(math.floor(t)) % self.m

    def kite_inverse(self, k, x):
        a, b, d = self.P[k], self.E[k], self.E[(k + self.m - 1) % self.m]
        e1 = (b[0] - a[0], b[1] - a[1])
        e2 = (d[0] - a[0], d[1] - a[1])
        e3 = (-(b[0] + d[0] - a[0]), -(b[1] + d[1] - a[1]))
        u = v = 0.5
        for _ in range(40):
            rx = a[0] + e1[0] * u + e2[0] * v + e3[0] * u * v - x[0]
            ry = a[1] + e1[1] * u + e2[1] * v + e3[1] * u * v - x[1]
            jux, juy = e1[0] + e3[0] * v, e1[1] + e3[1] * v
            jvx, jvy = e2[0] + e3[0] * u, e2[1] + e3[1] * u
            det = jux * jvy - juy * jvx
            if abs(det) < 1e-300:
                break
            du = (rx * jvy - ry * jvx) / det
            dv = (jux * ry - juy * rx) / det
            u -= du
            v -= dv
            if abs(du) + abs(dv) < 1e-16:
                break
        return (min(1.0, max(0.0, u)), min(1.0, max(0.0, v)))

    def wachspress(self, x):
        m = self.m
        A = [0.0] * m
        for j in range(m):
            a, b = self.P[j], self.P[(j + 1) % m]
            s = (a[0] - x[0]) * (b[1] - x[1]) - (a[1] - x[1]) * (b[0] - x[0])
            A[j] = s if s > 0 else 0.0
        lam = [0.0] * m
        total = 0.0
        for i in range(m):
            w = 1.0
            im = (i + m - 1) % m
            for j in range(m):
                if j != i and j != im:
                    w *= A[j]
            lam[i] = w
            total += w
        if total > 0:
            for i in range(m):
                lam[i] /= total
        else:
            best, bd = 0, None
            for i in range(m):
                dx, dy = self.P[i][0] - x[0], self.P[i][1] - x[1]
                d = dx * dx + dy * dy
                if bd is None or d < bd:
                    bd, best = d, i
            for i in range(m):
                lam[i] = 0.0
            lam[best] = 1.0
        return lam

    def corner_nu(self, lam, k, p):
        m = self.m
        kp, km = (k + 1) % m, (k + m - 1) % m
        s, t = 1 - lam[k] - lam[km], 1 - lam[k] - lam[kp]
        if m == 3:
            ds, dt = 1 - lam[km], 1 - lam[kp]
            s = s / ds if ds > 1e-300 else 0.0
            t = t / dt if dt > 1e-300 else 0.0
        s = min(1.0, max(0.0, s))
        t = min(1.0, max(0.0, t))
        return _nu_norm(s, t, p)


def _face_reparam(dom, gamma, gamma_centre, p):
    """The map psi of one control face: Wachspress blend of the radial
    corner maps, then the radial centre map.  Returns ``(trivial, apply)``."""
    m = dom.m
    any_corner = any(g != 1 for g in gamma)
    trivial = not any_corner and gamma_centre == 1

    def apply(x):
        y = x
        if any_corner:
            lam = dom.wachspress(x)
            y0 = y1 = 0.0
            for k in range(m):
                w = lam[k]
                if w == 0:
                    continue
                if gamma[k] == 1:
                    y0 += x[0] * w
                    y1 += x[1] * w
                    continue
                nu = dom.corner_nu(lam, k, p)
                r = nu ** (gamma[k] - 1) if nu > 0 else 0.0
                P = dom.P[k]
                y0 += (P[0] + (x[0] - P[0]) * r) * w
                y1 += (P[1] + (x[1] - P[1]) * r) * w
            y = (y0, y1)
        if gamma_centre != 1:
            k = dom.kite_of(y)
            uv = dom.kite_inverse(k, y)
            nuF = _nu_norm(1 - uv[0], 1 - uv[1], p)
            if nuF > 0:
                r = nuF ** (gamma_centre - 1)
                y = (y[0] * r, y[1] * r)
        return y

    return trivial, apply


def _face_node_count(m, n):
    q = n // 2
    if n % 2 == 1:
        return m * q * q
    return m * (q - 1) * (q - 1) + m * (q - 1) + 1 if q >= 1 else 0


def _topology_of(M, repair=True):
    """Build the :class:`_Topo` of a mesh, tidying it first when asked."""
    M = as_mesh(M)
    if repair:
        M = _repair_for_subdivision(M)
    else:
        M = M.copy()
    return _Topo([list(p) for p in M.V], [list(f) for f in M.F]), M


def _repair_for_subdivision(M):
    """Weld, drop rubbish, close T-junctions, cut non-manifold edges and
    vertices apart, drop unused vertices and make the winding consistent --
    everything subdivision needs from a model built by stacking parts."""
    M = M.copy()
    lo, hi = bbox(M)
    diag = _norm(_sub(hi, lo))
    tol = 1e-7 * (diag if diag > 0 else 1.0)
    _weld(M, tol)
    _drop_degenerate(M)
    _drop_internal(M)
    _dedup_faces(M)
    M = heal(M, 1e-6 * (diag if diag > 0 else 1.0))
    _drop_degenerate(M)
    _cut_non_manifold(M)
    _drop_unused(M)
    if M.F:
        M = fix_normals(M)
    return M


def _cut_non_manifold(M):
    """Separate faces that meet along an edge shared by three or more faces,
    or only at a vertex, by giving them copies of the vertex (in place)."""
    for _pass in range(4):
        emap = {}
        for f, poly in enumerate(M.F):
            m = len(poly)
            for k in range(m):
                a, b = poly[k], poly[(k + 1) % m]
                emap.setdefault((a, b) if a < b else (b, a), []).append((f, k))
        any_bad = False
        partner = [[-1] * len(poly) for poly in M.F]
        detach = []
        for lst in emap.values():
            if len(lst) == 2:
                (f0, k0), (f1, k1) = lst
                partner[f0][k0] = f1
                partner[f1][k1] = f0
                continue
            if len(lst) < 2:
                continue
            any_bad = True
            used = [False] * len(lst)
            for i in range(len(lst)):
                if used[i]:
                    continue
                fa, ka = lst[i]
                a0 = M.F[fa][ka]
                best = -1
                for j in range(i + 1, len(lst)):
                    if not used[j] and M.F[lst[j][0]][lst[j][1]] != a0:
                        best = j
                        break
                if best < 0:
                    for j in range(i + 1, len(lst)):
                        if not used[j]:
                            best = j
                            break
                if best < 0:
                    detach.append(lst[i])
                    used[i] = True
                    continue
                used[i] = used[best] = True
                fb, kb = lst[best]
                partner[fa][ka] = fb
                partner[fb][kb] = fa
        for f, k in detach:
            m = len(M.F[f])
            for idx in (k, (k + 1) % m):
                M.V.append(list(M.V[M.F[f][idx]]))
                M.F[f][idx] = len(M.V) - 1
        vf = [[] for _ in M.V]
        for f, poly in enumerate(M.F):
            for k, v in enumerate(poly):
                vf[v].append((f, k))
        nv0 = len(M.V)
        any_split = False
        for v in range(nv0):
            lst = vf[v]
            if len(lst) <= 1:
                continue
            pos = {}
            for i, (f, k) in enumerate(lst):
                pos[f] = i
            group = list(range(len(lst)))

            def find(x):
                while group[x] != x:
                    group[x] = group[group[x]]
                    x = group[x]
                return x

            for i, (f, k) in enumerate(lst):
                m = len(M.F[f])
                for g in (partner[f][k], partner[f][(k + m - 1) % m]):
                    if g < 0:
                        continue
                    j = pos.get(g)
                    if j is not None:
                        a, b = find(i), find(j)
                        if a != b:
                            group[a] = b
            fan = {}
            for i, (f, k) in enumerate(lst):
                r = find(i)
                vid = fan.get(r)
                if vid is None:
                    vid = v
                    if fan:
                        M.V.append(list(M.V[v]))
                        vid = len(M.V) - 1
                    fan[r] = vid
                M.F[f][k] = vid
            if len(fan) > 1:
                any_split = True
        if not any_bad and not any_split:
            break
    return M


def catmull_clark(M, steps=1, repair=True):
    """Classical Catmull-Clark subdivision: every face becomes quads and
    the shape is rounded, ``steps`` times.

    A cube turns into a rounded cube, then into a near sphere; a
    dodecahedron into a ball with twelve soft dimples.  Border edges are
    kept as smooth curves.  Faces inherit the colour of the face they came
    from.  ``repair=True`` first welds and tidies the mesh the way
    subdivision needs (parts that only touch are cut apart).  For any
    number of cells per edge -- not only 2, 4, 8 -- see :func:`smooth`::

        add.box([0, 0, 0], 2, "red")
        add.mesh(add.catmull_clark(add.layer(), 3))     # 384 quads
    """
    T, M = _topology_of(M, repair)
    colors = list(M.C)
    for _ in range(int(steps)):
        T, parent = _cc_subdivide(T)
        colors = [colors[p] for p in parent]
    return Mesh([list(p) for p in T.V], [list(f) for f in T.F], colors)


def smooth(M, n=4, uniform=True, centre=True, p=2.0, scale=1.0, repair=True):
    """Round a polygon mesh into its Catmull-Clark limit surface, sampled
    with ``n`` cells along every control edge -- for *any* ``n``.

    This is the generalised Catmull-Clark algorithm (Sabaliauskas, 2026):
    each control face (triangle, quad, pentagon ...) is covered by a grid
    of ``n x n`` cells per corner kite, every node of which lies exactly on
    the smooth limit surface.  ``n = 1`` moves the control vertices to the
    surface without adding faces; ``n = 2`` is the classical subdivision
    step (with the vertices at their limit); ``n = 3, 5, 7`` leave a small
    polygon in the middle of each face, even ``n`` meet at a centre node.
    Cells keep the colour of the control face they lie on, so a coloured
    box stays a coloured pillow.

    ``uniform=True`` applies the paper's reparameterisation near the
    extraordinary vertices and non-quad faces, so that the cells come out
    evenly sized; ``uniform=False`` gives the plain characteristic-map
    grid.  ``centre`` switches the extra centre map of non-quad faces,
    ``p`` is the exponent of the blending norm and ``scale`` multiplies
    the exponents (1 = the theoretical value).  ``repair=True`` welds and
    tidies the mesh first.  Non-manifold meshes are cut apart, so voxel
    models and stacked parts smooth too -- they just stay separate pieces::

        add.dodecahedron([0, 0, 0], 2, "gold")
        add.mesh(add.smooth(add.layer(), 5))           # 12 * 5 ... cells
    """
    n = int(n)
    if n < 1:
        raise ValueError("n must be at least 1")
    T, M0 = _topology_of(M, repair)
    if not T.F:
        return Mesh()
    colors = list(M0.C)
    T1, parent1 = _cc_subdivide(T)
    q, odd = n // 2, (n % 2 == 1)
    nv, ne, nf = len(T.V), len(T.E), len(T.F)
    face_base = [0] * (nf + 1)
    kite_offset = [0] * (nf + 1)
    face_base[0] = nv + ne * (n - 1)
    for f in range(nf):
        m = len(T.F[f])
        face_base[f + 1] = face_base[f] + _face_node_count(m, n)
        kite_offset[f + 1] = kite_offset[f] + m
    total = face_base[nf]
    GV = [None] * total
    done = [False] * total
    L = _cc_limit_positions(T1)
    for v in range(nv):
        GV[v] = L[v]
        done[v] = True
    F1 = T1.F
    V1 = T1.V

    def edge_node(f, k, t):
        poly = T.F[f]
        m = len(poly)
        a, b = poly[k], poly[(k + 1) % m]
        e = T.FE[f][k]
        tt = t if a < b else n - t
        return nv + e * (n - 1) + (tt - 1)

    def node_id(f, k, i, j):
        poly = T.F[f]
        m = len(poly)
        if i == 0 and j == 0:
            return poly[k]
        if j == 0:
            return edge_node(f, k, i)
        if i == 0:
            return edge_node(f, (k + m - 1) % m, n - j)
        base = face_base[f]
        if not odd:
            inner = m * (q - 1) * (q - 1)
            if i == q and j == q:
                return base + inner + m * (q - 1)
            if i == q:
                return base + inner + k * (q - 1) + (j - 1)
            if j == q:
                return base + inner + ((k + m - 1) % m) * (q - 1) + (i - 1)
            return base + k * (q - 1) * (q - 1) + (i - 1) * (q - 1) + (j - 1)
        return base + k * q * q + (i - 1) * q + (j - 1)

    out_faces = []
    out_colors = []
    for f in range(nf):
        poly = T.F[f]
        m = len(poly)
        dom = _PolygonDomain.get(m)
        gamma = [1.0] * m
        gamma_centre = 1.0
        if uniform:
            for k in range(m):
                v = poly[k]
                g = 1.0 if T.boundary[v] else _cc_gamma(len(T.VE[v]))
                gamma[k] = 1 + (g - 1) * scale
            if m != 4 and centre:
                gamma_centre = 1 + (_cc_gamma(m) - 1) * scale
        trivial, apply = _face_reparam(dom, gamma, gamma_centre, p)
        evaluators = [None] * m

        def evaluate(k, u, v):
            ev = evaluators[k]
            if ev is None:
                P = _regular_stencil(T1, kite_offset[f] + k)
                ev = evaluators[k] = (P, None) if P is not None else \
                    (None, _PatchTree(T1, kite_offset[f] + k))
            if ev[0] is not None:
                return _eval_bicubic(ev[0], u, v)
            return ev[1].eval(u, v)

        for k in range(m):
            for i in range(q + 1):
                for j in range(q + 1):
                    nid = node_id(f, k, i, j)
                    if done[nid]:
                        continue
                    u0, v0 = 2.0 * i / n, 2.0 * j / n
                    kk, u, v = k, u0, v0
                    if not trivial:
                        y = apply(dom.kite_map(k, u0, v0))
                        kk = dom.kite_of(y)
                        u, v = dom.kite_inverse(kk, y)
                    if u > 1 - 1e-12 and v > 1 - 1e-12:
                        GV[nid] = L[nv + ne + f]        # the face point
                    else:
                        GV[nid] = evaluate(kk, u, v)
                    done[nid] = True
        color = colors[f]
        for k in range(m):
            for i in range(q):
                for j in range(q):
                    out_faces.append([node_id(f, k, i, j), node_id(f, k, i + 1, j),
                                      node_id(f, k, i + 1, j + 1),
                                      node_id(f, k, i, j + 1)])
                    out_colors.append(color)
        if odd:
            for k in range(m):
                k1 = (k + 1) % m
                for j in range(q):
                    out_faces.append([node_id(f, k, q, j), node_id(f, k1, j, q),
                                      node_id(f, k1, j + 1, q),
                                      node_id(f, k, q, j + 1)])
                    out_colors.append(color)
            out_faces.append([node_id(f, k, q, q) for k in range(m)])
            out_colors.append(color)
    for i in range(total):
        if GV[i] is None:                       # cannot happen; keep files valid
            GV[i] = [0.0, 0.0, 0.0]
    return Mesh([list(p) for p in GV], out_faces, out_colors)


#: Other name for :func:`catmull_clark`.
subdivide = catmull_clark

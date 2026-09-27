// ============================================================================
//  16. Smooth surfaces: Catmull-Clark subdivision and its limit surface
//      (add.py: _src/65_subdivide.py)
// ============================================================================
namespace add {

namespace detail {
//: The neighbours and the faces counter-clockwise around a vertex (add.py's ``(nbrs, faces)``).
struct OrderedRing {
    std::vector<int> nbrs, faces;
};
//: A polygon mesh with its edges and adjacency worked out (add.py's _Topo).  ``E[e] = {a, b, f0, f1}``
//: (f1 = -1 on a border), ``VF[v]`` the faces at a vertex, ``VE[v]`` the edges at a vertex, ``FE[f][k]``
//: the edge leaving corner k of face f, ``FN[f][k]`` the face across that edge.  Building one throws
//: std::invalid_argument (add.py: ValueError) for a face with fewer than 3 corners, a degenerate edge,
//: an edge used twice by one face or an edge shared by more than two faces.
struct Topo {
    Points V;
    std::vector<Face> F;
    std::vector<std::array<int, 4>> E;
    std::vector<std::vector<int>> VF, VE, FE, FN;
    std::vector<bool> boundary;

    Topo() {}
    Topo(Points V_, std::vector<Face> F_);
    //: Is every face a quad?
    bool all_quads() const;
    //: The average corner of face ``f``.
    Point centroid(int f) const;
    //: Neighbours and faces counter-clockwise around ``v``; std::nullopt (add.py: None) when they
    //: do not make one fan.
    std::optional<OrderedRing> ordered_ring(int v) const;
};
//: One Catmull-Clark step: the new topology and ``parent[i]``, the face new quad ``i`` came from.
inline std::pair<Topo, std::vector<int>> cc_subdivide(const Topo& T);
//: Subdominant eigenvalue of the Catmull-Clark subdivision matrix at a valence-N vertex.
inline double cc_lambda(int N);
//: Exponent of the radial reparameterisation at a valence-N vertex: -1 / log2(lambda_N).
inline double cc_gamma(int N);
//: Limit position of every vertex (a mesh with other polygons than quads is subdivided once first).
inline Points cc_limit_positions(const Topo& T);
//: Two tangent vectors of the limit surface at an inner vertex (std::nullopt: add.py's None).
inline std::optional<std::pair<Point, Point>> cc_limit_tangents(const Topo& T, int v);
//: The four uniform cubic B-spline basis functions at ``t``.
inline std::array<double, 4> bspline_basis(double t);
//: The 4 x 4 control net ``P[i][j]`` of a bicubic B-spline patch.
using BicubicNet = std::array<std::array<Point, 4>, 4>;
//: The point of the bicubic B-spline patch with control net ``P`` at (u, v).
inline Point eval_bicubic(const BicubicNet& P, double u, double v);
//: The control net of quad ``f`` when its surroundings are regular, else std::nullopt (add.py: None).
inline std::optional<BicubicNet> regular_stencil(const Topo& T, int f);
//: The faces around face ``f`` as a small mesh of their own, ``f`` first with ``origin_corner`` first.
inline Topo neighbourhood(const Topo& T, int f, int origin_corner);
//: Evaluates the limit surface over one quad next to an extraordinary vertex by subdividing its
//: neighbourhood only as deep as a query needs (add.py's _PatchTree).
class PatchTree {
  public:
    static constexpr int MAX_DEPTH = 48;
    PatchTree(const Topo& T, int f);
    Point eval(double u, double v);

  private:
    struct Node {
        Topo M;
        int depth = 0;
        std::optional<BicubicNet> P;
        std::array<std::unique_ptr<Node>, 4> child;
        std::optional<Topo> sub;
    };
    std::unique_ptr<Node> root;
    static std::unique_ptr<Node> node(Topo L, int depth);
    Node* child(Node& nd, int k);
};
//: The paper's norm nu(s, t) = ((s^p + t^p) / (1 + s^p t^p))^(1/p) (max(s, t) for p > 64).
inline double nu_norm(double a, double b, double p);
//: The regular m-gon in the plane split into m kites [corner_k, edge_mid_k, centre, edge_mid_{k-1}]:
//: the parameter domain of one control face (add.py's _PolygonDomain).
class PolygonDomain {
  public:
    int m = 0;
    std::vector<Point2> P, E;
    explicit PolygonDomain(int m_);
    //: The (cached) domain of an m-gon.
    static const PolygonDomain& get(int m);
    Point2 kite_map(int k, double u, double v) const;
    int kite_of(const Point2& x) const;
    Point2 kite_inverse(int k, const Point2& x) const;
    std::vector<double> wachspress(const Point2& x) const;
    double corner_nu(const std::vector<double>& lam, int k, double p) const;
};
//: The map psi of one control face (add.py's ``(trivial, apply)``): ``trivial`` when it changes
//: nothing, ``apply(x)`` (or ``psi(x)``) the Wachspress blend of the radial corner maps, then the
//: radial centre map.
struct FaceReparam {
    PolygonDomain dom;
    std::vector<double> gamma;
    double gamma_centre = 1.0, p = 2.0;
    bool any_corner = false, trivial = true;
    Point2 apply(const Point2& x) const;
    Point2 operator()(const Point2& x) const { return apply(x); }
};
inline FaceReparam face_reparam(const PolygonDomain& dom, const std::vector<double>& gamma, double gamma_centre,
                                double p);
//: How many nodes smooth() puts inside an m-gon (neither corners nor on its edges) for ``n``.
inline long long face_node_count(long long m, long long n);
//: The Topo of a mesh (tidied first when asked) and the mesh it was built from.
inline std::pair<Topo, Mesh> topology_of(const Mesh& M, bool repair = true);
//: Weld, drop rubbish, close T-junctions, cut non-manifold edges and vertices apart, drop unused
//: vertices and make the winding consistent -- everything subdivision needs.
inline Mesh repair_for_subdivision(const Mesh& M);
//: Separate faces that meet along an edge of three or more faces, or only at a vertex, by giving
//: them copies of the vertex (in place).
inline Mesh& cut_non_manifold(Mesh& M);
//: Python's ``a % b`` and ``a // b`` for whole numbers (b > 0): never negative / rounded down.
inline long long subd_mod(long long a, long long b);
inline long long subd_floordiv(long long a, long long b);
//: Python's ``xs.index(x)``: the first place of ``x`` (std::invalid_argument when it is not there).
inline int subd_index(const std::vector<int>& xs, int x);
//: Python's float ``x ** y`` (detail::py_pow) with its errors: zero to a negative power throws
//: std::domain_error (ZeroDivisionError), a result too large std::overflow_error (OverflowError).
inline double subd_pow(double x, double y);
}  // namespace detail

//: Classical Catmull-Clark subdivision, ``steps`` times: every face becomes quads and the shape is
//: rounded.  Faces inherit the colour of the face they came from; ``repair`` first welds and tidies
//: the mesh the way subdivision needs (parts that only touch are cut apart).
inline Mesh catmull_clark(const Mesh& M, int steps = 1, bool repair = true);
//: Round a polygon mesh into its Catmull-Clark limit surface, sampled with ``n`` cells along every
//: control edge -- for any ``n`` (the generalised algorithm, Sabaliauskas 2026).  ``uniform`` applies
//: the reparameterisation near extraordinary vertices and non-quad faces, ``centre`` the extra centre
//: map of non-quad faces, ``p`` is the exponent of the blending norm, ``scale`` multiplies the
//: exponents, ``repair`` tidies the mesh first.
inline Mesh smooth(const Mesh& M, int n = 4, bool uniform = true, bool centre = true, double p = 2.0,
                   double scale = 1.0, bool repair = true);
//: ``subdivide`` is catmull_clark.
inline Mesh subdivide(const Mesh& M, int steps = 1, bool repair = true);

}  // namespace add
//@@definitions
namespace add {

namespace detail {

inline long long subd_mod(long long a, long long b) {
    long long r = a % b;
    return r < 0 ? r + b : r;
}

inline long long subd_floordiv(long long a, long long b) {
    long long q = a / b;
    return (a % b != 0 && a < 0) ? q - 1 : q;
}

inline int subd_index(const std::vector<int>& xs, int x) {
    for (size_t i = 0; i < xs.size(); ++i)
        if (xs[i] == x) return (int)i;
    throw std::invalid_argument(std::to_string(x) + " is not in list");
}

inline double subd_pow(double x, double y) {
    if (x == 0.0 && y < 0.0 && std::isfinite(y))
        throw std::domain_error("0.0 cannot be raised to a negative power");
    double r = py_pow(x, y);
    if (std::isinf(r) && std::isfinite(x) && std::isfinite(y))
        throw std::overflow_error("(34, 'Numerical result out of range')");
    return r;
}

// -- the topology -------------------------------------------------------------

inline Topo::Topo(Points V_, std::vector<Face> F_) : V(std::move(V_)), F(std::move(F_)) {
    int nv = (int)V.size(), nf = (int)F.size();
    VF.assign(nv, {});
    VE.assign(nv, {});
    FE.assign(nf, {});
    FN.assign(nf, {});
    std::unordered_map<unsigned long long, int> emap;         // (only looked up: no order needed)
    for (int f = 0; f < nf; ++f) {
        const Face& p = F[f];
        int m = (int)p.size();
        if (m < 3) throw std::invalid_argument("face with fewer than 3 vertices");
        std::vector<int> fe(m, 0);
        for (int k = 0; k < m; ++k) {
            int a = p[k], b = p[(k + 1) % m];
            if (a == b) throw std::invalid_argument("degenerate edge in face " + std::to_string(f));
            int k0 = a < b ? a : b, k1 = a < b ? b : a;
            unsigned long long key = ((unsigned long long)(unsigned int)k0 << 32) | (unsigned int)k1;
            auto it = emap.find(key);
            int e;
            if (it == emap.end()) {
                e = (int)E.size();
                E.push_back({k0, k1, f, -1});
                emap.emplace(key, e);
                VE.at(a).push_back(e);
                VE.at(b).push_back(e);
            } else {
                e = it->second;
                std::array<int, 4>& ed = E[e];
                if (ed[3] >= 0) throw std::invalid_argument("non-manifold edge (more than two faces meet along it)");
                if (ed[2] == f) throw std::invalid_argument("edge used twice by the same face");
                ed[3] = f;
            }
            fe[k] = e;
        }
        FE[f] = fe;
        for (int k = 0; k < m; ++k) VF.at(p[k]).push_back(f);
    }
    for (int f = 0; f < nf; ++f) {
        const std::vector<int>& fe = FE[f];
        std::vector<int> fn;
        fn.reserve(fe.size());
        for (int e : fe) fn.push_back(E[e][2] == f ? E[e][3] : E[e][2]);
        FN[f] = fn;
    }
    boundary.assign(nv, false);
    for (const std::array<int, 4>& ed : E)
        if (ed[3] < 0) {
            boundary[ed[0]] = true;
            boundary[ed[1]] = true;
        }
}

inline bool Topo::all_quads() const {
    for (const Face& f : F)
        if (f.size() != 4) return false;
    return true;
}

inline Point Topo::centroid(int f) const {
    const Face& p = F[f];
    double n = (double)p.size();
    Point out;
    for (int a = 0; a < 3; ++a) {
        double s = 0.0;                                        // (add.py's _total: in order)
        for (int v : p) s = s + V[v][a];
        out[a] = s / n;
    }
    return out;
}

inline std::optional<OrderedRing> Topo::ordered_ring(int v) const {
    const std::vector<int>& vf = VF[v];
    if (vf.empty()) return std::nullopt;
    int start = vf[0];
    for (int f : vf) {
        int k = subd_index(F[f], v);
        if (FN[f][k] < 0) {
            start = f;
            break;
        }
    }
    OrderedRing R;
    int f = start;
    int guard = 0;
    while (true) {
        const Face& p = F[f];
        int m = (int)p.size();
        int k = subd_index(p, v);
        int nxt = p[(k + 1) % m], prv = p[(k + m - 1) % m];
        if (R.faces.empty()) R.nbrs.push_back(nxt);
        R.faces.push_back(f);
        R.nbrs.push_back(prv);
        int g = FN[f][(k + m - 1) % m];
        if (g < 0) break;
        if (g == start) {
            R.nbrs.pop_back();
            break;
        }
        f = g;
        guard += 1;
        if (guard > (int)vf.size() + 2) return std::nullopt;
    }
    if (R.faces.size() != vf.size()) return std::nullopt;
    return R;
}

// -- Catmull-Clark subdivision and its limit ------------------------------------

inline std::pair<Topo, std::vector<int>> cc_subdivide(const Topo& T) {
    const Points& V = T.V;
    const std::vector<Face>& F = T.F;
    const std::vector<std::array<int, 4>>& E = T.E;
    int nv = (int)V.size(), ne = (int)E.size(), nf = (int)F.size();
    Points R(nv + ne + nf);
    for (int f = 0; f < nf; ++f) R[nv + ne + f] = T.centroid(f);
    for (int e = 0; e < ne; ++e) {
        int a = E[e][0], b = E[e][1], f0 = E[e][2], f1 = E[e][3];
        const Point& pa = V[a];
        const Point& pb = V[b];
        if (f1 < 0) {
            R[nv + e] = {(pa[0] + pb[0]) * 0.5, (pa[1] + pb[1]) * 0.5, (pa[2] + pb[2]) * 0.5};
        } else {
            const Point& c0 = R[nv + ne + f0];
            const Point& c1 = R[nv + ne + f1];
            R[nv + e] = {(pa[0] + pb[0] + c0[0] + c1[0]) * 0.25, (pa[1] + pb[1] + c0[1] + c1[1]) * 0.25,
                         (pa[2] + pb[2] + c0[2] + c1[2]) * 0.25};
        }
    }
    for (int v = 0; v < nv; ++v) {
        const Point& p = V[v];
        const std::vector<int>& VF = T.VF[v];
        const std::vector<int>& VE = T.VE[v];
        if (VF.empty()) {
            R[v] = p;
            continue;
        }
        if (T.boundary[v]) {
            if (VF.size() <= 1) {
                R[v] = p;
                continue;
            }
            double s[3] = {0.0, 0.0, 0.0};
            int cnt = 0;
            for (int e : VE) {
                const std::array<int, 4>& ed = E[e];
                if (ed[3] < 0) {
                    const Point& q = V[ed[0] == v ? ed[1] : ed[0]];
                    s[0] += q[0];
                    s[1] += q[1];
                    s[2] += q[2];
                    cnt += 1;
                }
            }
            if (cnt != 2) {
                R[v] = p;
                continue;
            }
            R[v] = {(s[0] + 6 * p[0]) / 8.0, (s[1] + 6 * p[1]) / 8.0, (s[2] + 6 * p[2]) / 8.0};
        } else {
            int n = (int)VE.size();
            double Q[3] = {0.0, 0.0, 0.0};
            double Rm[3] = {0.0, 0.0, 0.0};
            for (int f : VF) {
                const Point& c = R[nv + ne + f];
                Q[0] += c[0];
                Q[1] += c[1];
                Q[2] += c[2];
            }
            for (int e : VE) {
                const std::array<int, 4>& ed = E[e];
                const Point& pa = V[ed[0]];
                const Point& pb = V[ed[1]];
                Rm[0] += (pa[0] + pb[0]) * 0.5;
                Rm[1] += (pa[1] + pb[1]) * 0.5;
                Rm[2] += (pa[2] + pb[2]) * 0.5;
            }
            double nfc = (double)VF.size();
            R[v] = {(Q[0] / nfc + 2 * Rm[0] / n + (n - 3) * p[0]) / n,
                    (Q[1] / nfc + 2 * Rm[1] / n + (n - 3) * p[1]) / n,
                    (Q[2] / nfc + 2 * Rm[2] / n + (n - 3) * p[2]) / n};
        }
    }
    std::vector<Face> newF;
    std::vector<int> parent;
    for (int f = 0; f < nf; ++f) {
        const Face& p = F[f];
        const std::vector<int>& fe = T.FE[f];
        int m = (int)p.size();
        for (int k = 0; k < m; ++k) {
            newF.push_back({p[k], nv + fe[k], nv + ne + f, nv + fe[(k + m - 1) % m]});
            parent.push_back(f);
        }
    }
    return {Topo(std::move(R), std::move(newF)), std::move(parent)};
}

inline double cc_lambda(int N) {
    if (N == 4) return 0.5;
    if (N == 0) throw std::domain_error("float division by zero");
    double c = std::cos(2 * pi / N);
    return (c + 5 + std::sqrt((c + 1) * (c + 9))) / 16.0;
}

inline double cc_gamma(int N) {
    if (N == 4) return 1.0;
    return 1.0 / (-(std::log(cc_lambda(N)) / std::log(2.0)));      // (math.log(x, 2) is log(x) / log(2))
}

inline Points cc_limit_positions(const Topo& T) {
    if (!T.all_quads()) {
        Points L = cc_limit_positions(cc_subdivide(T).first);
        L.resize(T.V.size());                                  // [:len(T.V)]
        return L;
    }
    const Points& V = T.V;
    const std::vector<std::array<int, 4>>& E = T.E;
    Points L(V.size());
    for (int v = 0; v < (int)V.size(); ++v) {
        const Point& p = V[v];
        const std::vector<int>& VF = T.VF[v];
        if (VF.empty()) {
            L[v] = p;
            continue;
        }
        if (T.boundary[v]) {
            if (VF.size() <= 1) {
                L[v] = p;
                continue;
            }
            double s[3] = {0.0, 0.0, 0.0};
            int cnt = 0;
            for (int e : T.VE[v]) {
                const std::array<int, 4>& ed = E[e];
                if (ed[3] < 0) {
                    const Point& q = V[ed[0] == v ? ed[1] : ed[0]];
                    s[0] += q[0];
                    s[1] += q[1];
                    s[2] += q[2];
                    cnt += 1;
                }
            }
            if (cnt != 2) {
                L[v] = p;
                continue;
            }
            L[v] = {(s[0] + 4 * p[0]) / 6.0, (s[1] + 4 * p[1]) / 6.0, (s[2] + 4 * p[2]) / 6.0};
        } else {
            std::optional<OrderedRing> ring = T.ordered_ring(v);
            if (!ring) {
                L[v] = p;
                continue;
            }
            const std::vector<int>& nbrs = ring->nbrs;
            const std::vector<int>& faces = ring->faces;
            int n = (int)nbrs.size();
            double se[3] = {0.0, 0.0, 0.0};
            double sf[3] = {0.0, 0.0, 0.0};
            for (int j = 0; j < n; ++j) {
                const Point& q = V[nbrs[j]];
                se[0] += q[0];
                se[1] += q[1];
                se[2] += q[2];
                const Face& poly = T.F[faces.at(j)];
                const Point& d = V[poly[(subd_index(poly, v) + 2) % 4]];
                sf[0] += d[0];
                sf[1] += d[1];
                sf[2] += d[2];
            }
            double den = (double)(n * (n + 5));
            L[v] = {(n * n * p[0] + 4 * se[0] + sf[0]) / den, (n * n * p[1] + 4 * se[1] + sf[1]) / den,
                    (n * n * p[2] + 4 * se[2] + sf[2]) / den};
        }
    }
    return L;
}

inline std::optional<std::pair<Point, Point>> cc_limit_tangents(const Topo& T, int v) {
    if (T.boundary[v]) return std::nullopt;
    std::optional<OrderedRing> ring = T.ordered_ring(v);
    if (!ring) return std::nullopt;
    const std::vector<int>& nbrs = ring->nbrs;
    const std::vector<int>& faces = ring->faces;
    for (int f : faces)
        if (T.F[f].size() != 4) return cc_limit_tangents(cc_subdivide(T).first, v);
    int n = (int)nbrs.size();
    double c = std::cos(2 * pi / n);
    double A = 1 + c + std::sqrt((c + 1) * (c + 9));
    Point t1{0.0, 0.0, 0.0};
    Point t2{0.0, 0.0, 0.0};
    for (int j = 0; j < n; ++j) {
        double a0 = 2 * pi * j / n;
        double a1 = 2 * pi * (j + 1) / n;
        const Face& poly = T.F[faces.at(j)];
        const Point& fj = T.V[poly[(subd_index(poly, v) + 2) % 4]];
        const Point& e = T.V[nbrs[j]];
        double w1 = A * std::cos(a0), w2 = std::cos(a0) + std::cos(a1);
        double s1 = A * std::sin(a0), s2 = std::sin(a0) + std::sin(a1);
        for (int a = 0; a < 3; ++a) {
            t1[a] += e[a] * w1 + fj[a] * w2;
            t2[a] += e[a] * s1 + fj[a] * s2;
        }
    }
    return std::make_pair(t1, t2);
}

// -- the regular patches: bicubic B-splines -------------------------------------

inline std::array<double, 4> bspline_basis(double t) {
    double t2 = t * t;
    double t3 = t2 * t;
    return {(1 - 3 * t + 3 * t2 - t3) / 6.0, (4 - 6 * t2 + 3 * t3) / 6.0, (1 + 3 * t + 3 * t2 - 3 * t3) / 6.0,
            t3 / 6.0};
}

inline Point eval_bicubic(const BicubicNet& P, double u, double v) {
    std::array<double, 4> Nu = bspline_basis(u);
    std::array<double, 4> Nv = bspline_basis(v);
    double x = 0.0, y = 0.0, z = 0.0;
    for (int i = 0; i < 4; ++i) {
        double wi = Nu[i];
        if (wi == 0.0) continue;
        const std::array<Point, 4>& row = P[i];
        for (int j = 0; j < 4; ++j) {
            double w = wi * Nv[j];
            const Point& c = row[j];
            x += c[0] * w;
            y += c[1] * w;
            z += c[2] * w;
        }
    }
    return {x, y, z};
}

inline std::optional<BicubicNet> regular_stencil(const Topo& T, int f) {
    const Face& q = T.F[f];
    if (q.size() != 4) return std::nullopt;
    const Points& V = T.V;
    BicubicNet P{};
    int have[4][4] = {};
    P[1][1] = V[q[0]];
    P[2][1] = V[q[1]];
    P[2][2] = V[q[2]];
    P[1][2] = V[q[3]];
    have[1][1] = have[2][1] = have[2][2] = have[1][2] = 1;
    const int ci[4] = {1, 2, 2, 1};
    const int cj[4] = {1, 1, 2, 2};
    for (int k = 0; k < 4; ++k) {
        int v = q[k];
        bool bnd = T.boundary[v];
        int nfc = (int)T.VF[v].size();
        if (!bnd && (nfc != 4 || T.VE[v].size() != 4)) return std::nullopt;
        if (bnd && nfc > 2) return std::nullopt;
        std::optional<OrderedRing> ring = T.ordered_ring(v);
        if (!ring) return std::nullopt;
        const std::vector<int>& nb = ring->nbrs;
        const std::vector<int>& fc = ring->faces;
        for (int g : fc)
            if (T.F[g].size() != 4) return std::nullopt;
        int vn = q[(k + 1) % 4], vp = q[(k + 3) % 4];
        const int dn[2] = {ci[(k + 1) % 4] - ci[k], cj[(k + 1) % 4] - cj[k]};
        const int dp[2] = {ci[(k + 3) % 4] - ci[k], cj[(k + 3) % 4] - cj[k]};
        int n = (int)nb.size();
        auto at = std::find(nb.begin(), nb.end(), vn);
        if (at == nb.end()) return std::nullopt;
        int s = (int)(at - nb.begin());
        if (nb[(s + 1) % n] != vp) return std::nullopt;
        const int dirs[4][2] = {{dn[0], dn[1]}, {dp[0], dp[1]}, {-dn[0], -dn[1]}, {-dp[0], -dp[1]}};
        for (int idx = 0; idx < n; ++idx) {
            int off = (int)subd_mod(idx - s, 4);
            int gi = ci[k] + dirs[off][0], gj = cj[k] + dirs[off][1];
            if (gi < 0 || gi > 3 || gj < 0 || gj > 3) return std::nullopt;
            P[gi][gj] = V[nb[idx]];
            have[gi][gj] = 1;
        }
        for (int idx = 0; idx < (int)fc.size(); ++idx) {
            int off = (int)subd_mod(idx - s, 4);
            const Face& poly = T.F[fc[idx]];
            int diag = poly[(subd_index(poly, v) + 2) % 4];
            int gi = ci[k] + dirs[off][0] + dirs[(off + 1) % 4][0];
            int gj = cj[k] + dirs[off][1] + dirs[(off + 1) % 4][1];
            if (gi < 0 || gi > 3 || gj < 0 || gj > 3) return std::nullopt;
            P[gi][gj] = V[diag];
            have[gi][gj] = 1;
        }
    }
    const bool miss[4] = {!have[0][1] && !have[0][2], !have[3][1] && !have[3][2], !have[1][0] && !have[2][0],
                          !have[1][3] && !have[2][3]};
    if (have[0][1] != have[0][2] || have[3][1] != have[3][2] || have[1][0] != have[2][0] ||
        have[1][3] != have[2][3])
        return std::nullopt;

    auto refl = [](const Point& a, const Point& b) -> Point {
        return {2 * a[0] - b[0], 2 * a[1] - b[1], 2 * a[2] - b[2]};
    };
    auto bil = [](const Point& a, const Point& b, const Point& c) -> Point {
        return {a[0] + b[0] - c[0], a[1] + b[1] - c[1], a[2] + b[2] - c[2]};
    };
    for (int t : {1, 2}) {
        if (miss[0]) P[0][t] = refl(P[1][t], P[2][t]);
        if (miss[1]) P[3][t] = refl(P[2][t], P[1][t]);
        if (miss[2]) P[t][0] = refl(P[t][1], P[t][2]);
        if (miss[3]) P[t][3] = refl(P[t][2], P[t][1]);
    }
    if (!have[0][0])
        P[0][0] = miss[0] ? refl(P[1][0], P[2][0]) : miss[2] ? refl(P[0][1], P[0][2]) : bil(P[0][1], P[1][0], P[1][1]);
    if (!have[3][0])
        P[3][0] = miss[1] ? refl(P[2][0], P[1][0]) : miss[2] ? refl(P[3][1], P[3][2]) : bil(P[3][1], P[2][0], P[2][1]);
    if (!have[0][3])
        P[0][3] = miss[0] ? refl(P[1][3], P[2][3]) : miss[3] ? refl(P[0][2], P[0][1]) : bil(P[0][2], P[1][3], P[1][2]);
    if (!have[3][3])
        P[3][3] = miss[1] ? refl(P[2][3], P[1][3]) : miss[3] ? refl(P[3][2], P[3][1]) : bil(P[3][2], P[2][3], P[2][2]);
    return P;
}

// -- the irregular patches: subdivided only as deep as needed -------------------

inline Topo neighbourhood(const Topo& T, int f, int origin_corner) {
    std::vector<int> faces{f};
    std::unordered_set<int> seen{f};                           // (only looked up: the order is faces')
    for (int v : T.F[f])
        for (int g : T.VF[v])
            if (!seen.count(g)) {
                seen.insert(g);
                faces.push_back(g);
            }
    std::unordered_map<int, int> vmap;
    Points LV;
    std::vector<Face> LF;
    for (int g : faces) {
        const Face& poly = T.F[g];
        int m = (int)poly.size();
        int start = g == f ? origin_corner : 0;
        Face out;
        for (int k = 0; k < m; ++k) {
            int v = poly[(start + k) % m];
            auto it = vmap.find(v);
            int idx;
            if (it == vmap.end()) {
                idx = (int)LV.size();
                LV.push_back(T.V[v]);
                vmap.emplace(v, idx);
            } else {
                idx = it->second;
            }
            out.push_back(idx);
        }
        LF.push_back(out);
    }
    return Topo(std::move(LV), std::move(LF));
}

inline PatchTree::PatchTree(const Topo& T, int f) : root(node(neighbourhood(T, f, 0), 0)) {}

inline std::unique_ptr<PatchTree::Node> PatchTree::node(Topo L, int depth) {
    std::unique_ptr<Node> nd(new Node());
    nd->M = std::move(L);
    nd->depth = depth;
    nd->P = regular_stencil(nd->M, 0);
    return nd;
}

inline PatchTree::Node* PatchTree::child(Node& nd, int k) {
    if (nd.child[k]) return nd.child[k].get();
    if (!nd.sub) nd.sub = cc_subdivide(nd.M).first;
    static const int origin[4] = {0, 3, 2, 1};
    nd.child[k] = node(neighbourhood(*nd.sub, k, origin[k]), nd.depth + 1);
    return nd.child[k].get();
}

inline Point PatchTree::eval(double u, double v) {
    Node* nd = root.get();
    int depth = 0;
    while (!nd->P) {
        if (depth >= MAX_DEPTH) {
            Points L = cc_limit_positions(nd->M);
            int corner = u < 0.5 ? (v < 0.5 ? 0 : 3) : (v < 0.5 ? 1 : 2);
            return L[nd->M.F[0][corner]];
        }
        int k;
        if (u < 0.5) {
            if (v < 0.5) {
                k = 0; u = 2 * u; v = 2 * v;
            } else {
                k = 3; u = 2 * u; v = 2 * v - 1;
            }
        } else {
            if (v < 0.5) {
                k = 1; u = 2 * u - 1; v = 2 * v;
            } else {
                k = 2; u = 2 * u - 1; v = 2 * v - 1;
            }
        }
        nd = child(*nd, k);
        depth += 1;
    }
    return eval_bicubic(*nd->P, u, v);
}

// -- the reparameterisation (Sections 4 and 5 of the paper) ---------------------

inline double nu_norm(double a, double b, double p) {
    if (p > 64) return std::max(a, b);                         // (Python's max: the first of equals)
    double ap = subd_pow(a, p), bp = subd_pow(b, p);
    double base = (ap + bp) / (1 + ap * bp);
    if (p == 0) throw std::domain_error("float division by zero");      // (add.py: 1.0 / p)
    return subd_pow(base, 1.0 / p);
}

inline PolygonDomain::PolygonDomain(int m_) : m(m_) {
    for (int k = 0; k < m; ++k) P.push_back({std::cos(2 * pi * k / m), std::sin(2 * pi * k / m)});
    for (int k = 0; k < m; ++k)
        E.push_back({(P[k][0] + P[(k + 1) % m][0]) / 2.0, (P[k][1] + P[(k + 1) % m][1]) / 2.0});
}

inline const PolygonDomain& PolygonDomain::get(int m) {
    static std::map<int, PolygonDomain> cache;                 // (references stay valid)
    auto it = cache.find(m);
    if (it == cache.end()) it = cache.emplace(m, PolygonDomain(m)).first;
    return it->second;
}

inline Point2 PolygonDomain::kite_map(int k, double u, double v) const {
    const Point2& a = P[k];
    const Point2& b = E[k];
    const Point2& d = E[(k + m - 1) % m];
    double wa = (1 - u) * (1 - v), wb = u * (1 - v), wd = (1 - u) * v;
    return {a[0] * wa + b[0] * wb + d[0] * wd, a[1] * wa + b[1] * wb + d[1] * wd};
}

inline int PolygonDomain::kite_of(const Point2& x) const {
    if (x[0] == 0 && x[1] == 0) return 0;
    double t = std::atan2(x[1], x[0]) / (2 * pi) * m + 0.5;
    return (int)subd_mod(cell_floor(t), m);                    // int(math.floor(t)) % m
}

inline Point2 PolygonDomain::kite_inverse(int k, const Point2& x) const {
    const Point2& a = P[k];
    const Point2& b = E[k];
    const Point2& d = E[(k + m - 1) % m];
    const double e1[2] = {b[0] - a[0], b[1] - a[1]};
    const double e2[2] = {d[0] - a[0], d[1] - a[1]};
    const double e3[2] = {-(b[0] + d[0] - a[0]), -(b[1] + d[1] - a[1])};
    double u = 0.5, v = 0.5;
    for (int it = 0; it < 40; ++it) {
        double rx = a[0] + e1[0] * u + e2[0] * v + e3[0] * u * v - x[0];
        double ry = a[1] + e1[1] * u + e2[1] * v + e3[1] * u * v - x[1];
        double jux = e1[0] + e3[0] * v, juy = e1[1] + e3[1] * v;
        double jvx = e2[0] + e3[0] * u, jvy = e2[1] + e3[1] * u;
        double det = jux * jvy - juy * jvx;
        if (std::fabs(det) < 1e-300) break;
        double du = (rx * jvy - ry * jvx) / det;
        double dv = (jux * ry - juy * rx) / det;
        u -= du;
        v -= dv;
        if (std::fabs(du) + std::fabs(dv) < 1e-16) break;
    }
    return {std::min(1.0, std::max(0.0, u)), std::min(1.0, std::max(0.0, v))};    // (as Python's min/max)
}

inline std::vector<double> PolygonDomain::wachspress(const Point2& x) const {
    std::vector<double> A(m, 0.0);
    for (int j = 0; j < m; ++j) {
        const Point2& a = P[j];
        const Point2& b = P[(j + 1) % m];
        double s = (a[0] - x[0]) * (b[1] - x[1]) - (a[1] - x[1]) * (b[0] - x[0]);
        A[j] = s > 0 ? s : 0.0;
    }
    std::vector<double> lam(m, 0.0);
    double total = 0.0;
    for (int i = 0; i < m; ++i) {
        double w = 1.0;
        int im = (i + m - 1) % m;
        for (int j = 0; j < m; ++j)
            if (j != i && j != im) w *= A[j];
        lam[i] = w;
        total += w;
    }
    if (total > 0) {
        for (int i = 0; i < m; ++i) lam[i] /= total;
    } else {
        int best = 0;
        bool have_bd = false;                                  // (add.py: bd = None)
        double bd = 0.0;
        for (int i = 0; i < m; ++i) {
            double dx = P[i][0] - x[0], dy = P[i][1] - x[1];
            double d = dx * dx + dy * dy;
            if (!have_bd || d < bd) {
                bd = d;
                best = i;
                have_bd = true;
            }
        }
        for (int i = 0; i < m; ++i) lam[i] = 0.0;
        lam[best] = 1.0;
    }
    return lam;
}

inline double PolygonDomain::corner_nu(const std::vector<double>& lam, int k, double p) const {
    int kp = (k + 1) % m, km = (k + m - 1) % m;
    double s = 1 - lam[k] - lam[km], t = 1 - lam[k] - lam[kp];
    if (m == 3) {
        double ds = 1 - lam[km], dt = 1 - lam[kp];
        s = ds > 1e-300 ? s / ds : 0.0;
        t = dt > 1e-300 ? t / dt : 0.0;
    }
    s = std::min(1.0, std::max(0.0, s));
    t = std::min(1.0, std::max(0.0, t));
    return nu_norm(s, t, p);
}

inline FaceReparam face_reparam(const PolygonDomain& dom, const std::vector<double>& gamma, double gamma_centre,
                                double p) {
    FaceReparam R{dom, gamma, gamma_centre, p};
    R.any_corner = false;
    for (double g : gamma)
        if (g != 1) {
            R.any_corner = true;
            break;
        }
    R.trivial = !R.any_corner && gamma_centre == 1;
    return R;
}

inline Point2 FaceReparam::apply(const Point2& x) const {
    const int m = dom.m;
    Point2 y = x;
    if (any_corner) {
        std::vector<double> lam = dom.wachspress(x);
        double y0 = 0.0, y1 = 0.0;
        for (int k = 0; k < m; ++k) {
            double w = lam[k];
            if (w == 0) continue;
            if (gamma[k] == 1) {
                y0 += x[0] * w;
                y1 += x[1] * w;
                continue;
            }
            double nu = dom.corner_nu(lam, k, p);
            double r = nu > 0 ? subd_pow(nu, gamma[k] - 1) : 0.0;
            const Point2& Pk = dom.P[k];
            y0 += (Pk[0] + (x[0] - Pk[0]) * r) * w;
            y1 += (Pk[1] + (x[1] - Pk[1]) * r) * w;
        }
        y = {y0, y1};
    }
    if (gamma_centre != 1) {
        int k = dom.kite_of(y);
        Point2 uv = dom.kite_inverse(k, y);
        double nuF = nu_norm(1 - uv[0], 1 - uv[1], p);
        if (nuF > 0) {
            double r = subd_pow(nuF, gamma_centre - 1);
            y = {y[0] * r, y[1] * r};
        }
    }
    return y;
}

inline long long face_node_count(long long m, long long n) {
    long long q = subd_floordiv(n, 2);
    if (subd_mod(n, 2) == 1) return m * q * q;
    return q >= 1 ? m * (q - 1) * (q - 1) + m * (q - 1) + 1 : 0;
}

// -- getting a mesh ready -------------------------------------------------------

inline std::pair<Topo, Mesh> topology_of(const Mesh& M0, bool repair) {
    Mesh M = repair ? repair_for_subdivision(M0) : M0.copy();
    Topo T(M.V, M.F);
    return {std::move(T), std::move(M)};
}

inline Mesh repair_for_subdivision(const Mesh& M0) {
    Mesh M = M0.copy();
    std::array<Point, 2> lohi = add::bbox(M);
    double diag = detail::norm(detail::sub(lohi[1], lohi[0]));
    double tol = 1e-7 * (diag > 0 ? diag : 1.0);
    detail::weld(M, tol);
    detail::drop_degenerate(M);
    detail::drop_internal(M);
    detail::dedup_faces(M);
    M = add::heal(M, 1e-6 * (diag > 0 ? diag : 1.0));
    detail::drop_degenerate(M);
    detail::cut_non_manifold(M);
    detail::drop_unused(M);
    if (!M.F.empty()) M = add::fix_normals(M);
    return M;
}

inline Mesh& cut_non_manifold(Mesh& M) {
    typedef std::pair<int, int> Corner;                        // (face, corner)
    for (int pass = 0; pass < 4; ++pass) {
        // emap: edge -> the corners it leaves from, in the order add.py's dict keeps the edges.
        std::vector<std::vector<Corner>> emap;
        std::unordered_map<unsigned long long, size_t> where;
        for (int f = 0; f < (int)M.F.size(); ++f) {
            const Face& poly = M.F[f];
            int m = (int)poly.size();
            for (int k = 0; k < m; ++k) {
                int a = poly[k], b = poly[(k + 1) % m];
                int k0 = a < b ? a : b, k1 = a < b ? b : a;
                unsigned long long key = ((unsigned long long)(unsigned int)k0 << 32) | (unsigned int)k1;
                auto it = where.find(key);
                if (it == where.end()) {
                    where.emplace(key, emap.size());
                    emap.push_back(std::vector<Corner>{Corner(f, k)});
                } else {
                    emap[it->second].push_back(Corner(f, k));
                }
            }
        }
        bool any_bad = false;
        std::vector<std::vector<int>> partner;
        partner.reserve(M.F.size());
        for (const Face& poly : M.F) partner.push_back(std::vector<int>(poly.size(), -1));
        std::vector<Corner> detach;
        for (const std::vector<Corner>& lst : emap) {
            if (lst.size() == 2) {
                int f0 = lst[0].first, k0 = lst[0].second, f1 = lst[1].first, k1 = lst[1].second;
                partner[f0][k0] = f1;
                partner[f1][k1] = f0;
                continue;
            }
            if (lst.size() < 2) continue;
            any_bad = true;
            std::vector<bool> used(lst.size(), false);
            for (size_t i = 0; i < lst.size(); ++i) {
                if (used[i]) continue;
                int fa = lst[i].first, ka = lst[i].second;
                int a0 = M.F[fa][ka];
                long long best = -1;
                for (size_t j = i + 1; j < lst.size(); ++j)
                    if (!used[j] && M.F[lst[j].first][lst[j].second] != a0) {
                        best = (long long)j;
                        break;
                    }
                if (best < 0)
                    for (size_t j = i + 1; j < lst.size(); ++j)
                        if (!used[j]) {
                            best = (long long)j;
                            break;
                        }
                if (best < 0) {
                    detach.push_back(lst[i]);
                    used[i] = true;
                    continue;
                }
                used[i] = true;
                used[(size_t)best] = true;
                int fb = lst[(size_t)best].first, kb = lst[(size_t)best].second;
                partner[fa][ka] = fb;
                partner[fb][kb] = fa;
            }
        }
        for (const Corner& c : detach) {
            int f = c.first, k = c.second;
            int m = (int)M.F[f].size();
            for (int idx : {k, (k + 1) % m}) {
                Point copy = M.V[M.F[f][idx]];
                M.V.push_back(copy);
                M.F[f][idx] = (int)M.V.size() - 1;
            }
        }
        std::vector<std::vector<Corner>> vf(M.V.size());
        for (int f = 0; f < (int)M.F.size(); ++f) {
            const Face& poly = M.F[f];
            for (int k = 0; k < (int)poly.size(); ++k) vf.at(poly[k]).push_back({f, k});
        }
        int nv0 = (int)M.V.size();
        bool any_split = false;
        for (int v = 0; v < nv0; ++v) {
            const std::vector<Corner>& lst = vf[v];
            if (lst.size() <= 1) continue;
            std::unordered_map<int, int> pos;                  // face -> its (last) place in lst
            for (int i = 0; i < (int)lst.size(); ++i) pos[lst[i].first] = i;
            std::vector<int> group(lst.size());
            for (int i = 0; i < (int)lst.size(); ++i) group[i] = i;
            auto find = [&group](int x) {
                while (group[x] != x) {
                    group[x] = group[group[x]];
                    x = group[x];
                }
                return x;
            };
            for (int i = 0; i < (int)lst.size(); ++i) {
                int f = lst[i].first, k = lst[i].second;
                int m = (int)M.F[f].size();
                for (int g : {partner[f][k], partner[f][(k + m - 1) % m]}) {
                    if (g < 0) continue;
                    auto it = pos.find(g);
                    if (it != pos.end()) {
                        int a = find(i), b = find(it->second);
                        if (a != b) group[a] = b;
                    }
                }
            }
            std::unordered_map<int, int> fan;                  // (only looked up and counted)
            for (int i = 0; i < (int)lst.size(); ++i) {
                int f = lst[i].first, k = lst[i].second;
                int r = find(i);
                auto it = fan.find(r);
                int vid;
                if (it == fan.end()) {
                    vid = v;
                    if (!fan.empty()) {
                        Point copy = M.V[v];
                        M.V.push_back(copy);
                        vid = (int)M.V.size() - 1;
                    }
                    fan.emplace(r, vid);
                } else {
                    vid = it->second;
                }
                M.F[f][k] = vid;
            }
            if (fan.size() > 1) any_split = true;
        }
        if (!any_bad && !any_split) break;
    }
    return M;
}

}  // namespace detail

inline Mesh catmull_clark(const Mesh& M, int steps, bool repair) {
    std::pair<detail::Topo, Mesh> tm = detail::topology_of(M, repair);
    detail::Topo T = std::move(tm.first);
    std::vector<Color> colors = tm.second.C;
    for (int s = 0; s < steps; ++s) {
        std::pair<detail::Topo, std::vector<int>> sub = detail::cc_subdivide(T);
        T = std::move(sub.first);
        std::vector<Color> next;
        next.reserve(sub.second.size());
        for (int p : sub.second) next.push_back(colors.at(p));
        colors = std::move(next);
    }
    return Mesh(T.V, T.F, colors);
}

inline Mesh smooth(const Mesh& M, int n, bool uniform, bool centre, double p, double scale, bool repair) {
    if (n < 1) throw std::invalid_argument("n must be at least 1");
    std::pair<detail::Topo, Mesh> tm = detail::topology_of(M, repair);
    const detail::Topo& T = tm.first;
    if (T.F.empty()) return Mesh();
    const std::vector<Color>& colors = tm.second.C;
    std::pair<detail::Topo, std::vector<int>> sub1 = detail::cc_subdivide(T);
    const detail::Topo& T1 = sub1.first;
    int q = n / 2;
    bool odd = n % 2 == 1;
    int nv = (int)T.V.size(), ne = (int)T.E.size(), nf = (int)T.F.size();
    std::vector<int> face_base(nf + 1, 0);
    std::vector<int> kite_offset(nf + 1, 0);
    face_base[0] = nv + ne * (n - 1);
    for (int f = 0; f < nf; ++f) {
        int m = (int)T.F[f].size();
        face_base[f + 1] = face_base[f] + (int)detail::face_node_count(m, n);
        kite_offset[f + 1] = kite_offset[f] + m;
    }
    int total = face_base[nf];
    Points GV(total);                                          // (a node never reached stays 0, 0, 0)
    std::vector<bool> done(total, false);
    Points L = detail::cc_limit_positions(T1);
    for (int v = 0; v < nv; ++v) {
        GV[v] = L[v];
        done[v] = true;
    }

    auto edge_node = [&](int f, int k, int t) {
        const Face& poly = T.F[f];
        int m = (int)poly.size();
        int a = poly[k], b = poly[(k + 1) % m];
        int e = T.FE[f][k];
        int tt = a < b ? t : n - t;
        return nv + e * (n - 1) + (tt - 1);
    };

    auto node_id = [&](int f, int k, int i, int j) {
        const Face& poly = T.F[f];
        int m = (int)poly.size();
        if (i == 0 && j == 0) return poly[k];
        if (j == 0) return edge_node(f, k, i);
        if (i == 0) return edge_node(f, (k + m - 1) % m, n - j);
        int base = face_base[f];
        if (!odd) {
            int inner = m * (q - 1) * (q - 1);
            if (i == q && j == q) return base + inner + m * (q - 1);
            if (i == q) return base + inner + k * (q - 1) + (j - 1);
            if (j == q) return base + inner + ((k + m - 1) % m) * (q - 1) + (i - 1);
            return base + k * (q - 1) * (q - 1) + (i - 1) * (q - 1) + (j - 1);
        }
        return base + k * q * q + (i - 1) * q + (j - 1);
    };

    // The evaluator of one kite: its control net when it is regular, else a patch tree.
    struct KiteEval {
        bool made = false;
        std::optional<detail::BicubicNet> P;
        std::unique_ptr<detail::PatchTree> tree;
    };

    std::vector<Face> out_faces;
    std::vector<Color> out_colors;
    for (int f = 0; f < nf; ++f) {
        const Face& poly = T.F[f];
        int m = (int)poly.size();
        const detail::PolygonDomain& dom = detail::PolygonDomain::get(m);
        std::vector<double> gamma(m, 1.0);
        double gamma_centre = 1.0;
        if (uniform) {
            for (int k = 0; k < m; ++k) {
                int v = poly[k];
                double g = T.boundary[v] ? 1.0 : detail::cc_gamma((int)T.VE[v].size());
                gamma[k] = 1 + (g - 1) * scale;
            }
            if (m != 4 && centre) gamma_centre = 1 + (detail::cc_gamma(m) - 1) * scale;
        }
        detail::FaceReparam psi = detail::face_reparam(dom, gamma, gamma_centre, p);
        std::vector<KiteEval> evaluators(m);

        auto evaluate = [&](int k, double u, double v) -> Point {
            KiteEval& ev = evaluators[k];
            if (!ev.made) {
                ev.P = detail::regular_stencil(T1, kite_offset[f] + k);
                if (!ev.P) ev.tree.reset(new detail::PatchTree(T1, kite_offset[f] + k));
                ev.made = true;
            }
            if (ev.P) return detail::eval_bicubic(*ev.P, u, v);
            return ev.tree->eval(u, v);
        };

        for (int k = 0; k < m; ++k)
            for (int i = 0; i < q + 1; ++i)
                for (int j = 0; j < q + 1; ++j) {
                    int nid = node_id(f, k, i, j);
                    if (done[nid]) continue;
                    double u0 = 2.0 * i / n, v0 = 2.0 * j / n;
                    int kk = k;
                    double u = u0, v = v0;
                    if (!psi.trivial) {
                        Point2 y = psi.apply(dom.kite_map(k, u0, v0));
                        kk = dom.kite_of(y);
                        Point2 uv = dom.kite_inverse(kk, y);
                        u = uv[0];
                        v = uv[1];
                    }
                    if (u > 1 - 1e-12 && v > 1 - 1e-12) GV[nid] = L[nv + ne + f];     // the face point
                    else GV[nid] = evaluate(kk, u, v);
                    done[nid] = true;
                }
        const Color& color = colors.at(f);
        for (int k = 0; k < m; ++k)
            for (int i = 0; i < q; ++i)
                for (int j = 0; j < q; ++j) {
                    out_faces.push_back({node_id(f, k, i, j), node_id(f, k, i + 1, j), node_id(f, k, i + 1, j + 1),
                                         node_id(f, k, i, j + 1)});
                    out_colors.push_back(color);
                }
        if (odd) {
            for (int k = 0; k < m; ++k) {
                int k1 = (k + 1) % m;
                for (int j = 0; j < q; ++j) {
                    out_faces.push_back({node_id(f, k, q, j), node_id(f, k1, j, q), node_id(f, k1, j + 1, q),
                                         node_id(f, k, q, j + 1)});
                    out_colors.push_back(color);
                }
            }
            Face centre_face;
            for (int k = 0; k < m; ++k) centre_face.push_back(node_id(f, k, q, q));
            out_faces.push_back(centre_face);
            out_colors.push_back(color);
        }
    }
    return Mesh(GV, out_faces, out_colors);
}

inline Mesh subdivide(const Mesh& M, int steps, bool repair) { return catmull_clark(M, steps, repair); }

}  // namespace add

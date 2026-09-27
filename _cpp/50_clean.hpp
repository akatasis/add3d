// ============================================================================
//  13. Repair and report: clean(), stats(), check()
//      (add.py: _src/50_clean.py)
// ============================================================================
namespace add {

namespace detail {
//: Merge vertices closer than ``tol`` (in place).  Returns how many went.
inline int weld(Mesh& M, double tol = 1e-7);
//: For every vertex the index of the first one lying on it (within ``tol``, the way weld
//: would merge them), the mesh unchanged.
inline std::vector<int> weld_map(const std::vector<Point>& V, double tol = 1e-7);
//: Six times the signed volume of the faces ``faces`` measured from their own middle, and
//: the size of the piece, cubed (see fix_normals).
inline std::pair<double, double> piece_volume(const Mesh& M, const std::vector<int>& faces, const std::vector<int>& rep);
//: Keep only the faces whose index is in ``keep`` (in place); how many went.
inline int keep_faces(Mesh& M, const std::vector<int>& keep);
//: The vertices with a coordinate that is not a finite number.
inline std::set<int> not_finite(const Mesh& M);
//: Delete the vertices that are not finite numbers and their faces; how many faces went.
inline int drop_not_finite(Mesh& M);
//: Cut a face that visits a vertex twice into loops that do not.
inline std::vector<std::pair<Face, std::vector<Point2>>> split_repeats(const Face& f, const std::vector<Point2>* uv);
//: Delete faces with no area, remove repeated corners, split pinched faces (in place).
inline int drop_degenerate(Mesh& M, double tol = 1e-12);
//: Delete repeats of a face that is already there (in place).
inline int dedup_faces(Mesh& M);
//: Delete pairs of identical faces that point opposite ways (in place).
inline int drop_internal(Mesh& M);
//: True when the smallest index is followed by the smaller neighbour.
inline bool winding(const Face& f);
//: Delete vertices no face refers to (in place).
inline int drop_unused(Mesh& M);
//: Twice the signed area of a 2D polygon (positive when counter-clockwise).
inline double poly_area2(const Profile& pts);
//: Python's ``int(math.floor(x))`` -- a grid cell number.  As in Python, an exception
//: for a NaN or an infinite ``x``; unlike Python, whose integers have no limit, also
//: for a cell number beyond 64 bits (coordinates ~1e12 times the tolerance).
inline long long cell_floor(double x);
//: Python's ``round(x)`` (to a whole number, halves to even) as a float; an
//: exception for a NaN or an infinite ``x``, as in Python.
inline double key_round(double x);
//: Sutherland-Hodgman: the part of convex polygon ``pts`` on one side of the
//: directed line a -> b (left = the inside of a counter-clockwise polygon).
inline Profile clip_half(const Profile& pts, const Point2& a, const Point2& b, bool keep_left);
//: Convex polygon ``A`` with convex polygon ``B`` taken away, as convex pieces.
//: ``untouched`` (when given) is set to whether A came back as it was -- add.py
//: then returns the very list [A], which its callers test with ``is``.
inline std::vector<Profile> convex_minus(const Profile& A, const Profile& B, double eps,
                                         bool* untouched = nullptr);
//: Ear-clipping triangulation of a simple counter-clockwise 2D polygon (triangles as points).
inline std::vector<Profile> ears(const Profile& pts);
//: A counter-clockwise 2D polygon as convex pieces: itself if convex, ear triangles otherwise.
inline std::vector<Profile> convex_pieces(const Profile& pts);
//: Ear clipping as index triples, or nothing when no ear can be found (add.py: None).
inline std::optional<std::vector<std::array<int, 3>>> ear_triangles(const Profile& pts);
//: Does face ``f`` turn the wrong way anywhere along its outline?  (``n``: its normal, if known.)
inline bool is_concave(const Mesh& M, const Face& f, std::optional<Point> n = std::nullopt);
//: Cut every face that is not convex into triangles (in place); how many faces were cut.
inline int split_concave(Mesh& M);
//: One face of a plane group: add.py's ``(area, index, pts2d, bbox, flipped)``.
struct PlanePoly {
    double area = 0.0;
    int index = 0;
    Profile pts;
    std::array<double, 4> bb{};
    bool flipped = false;
};
//: Faces lying in one plane (either way round): the key, the plane's frame and the faces.
struct PlaneGroup {
    std::array<double, 4> key{};                 // (nx, ny, nz, d) rounded
    Point u, v, n;
    std::vector<PlanePoly> polys;
};
//: Faces grouped by their plane, in the order add.py's dict keeps them (groups of one left out).
inline std::vector<PlaneGroup> overlap_groups(const Mesh& M, double tol);
//: Twice the area of the intersection of two convex counter-clockwise polygons.
inline double convex_overlap2(const Profile& A, const Profile& B);
//: ``pieces`` with every polygon of ``others`` taken away; nothing (add.py: None) when
//: the result would shatter into more than ``limit`` pieces.
inline std::optional<std::vector<Profile>> minus_all(std::vector<Profile> pieces, const std::vector<Profile>& others,
                                                     double eps, size_t limit = 64);
//: A face cut back by overlap_scan: add.py's ``(pieces, u, v, n, d, flipped)``.
struct CutFace {
    std::vector<Profile> pieces;
    Point u, v, n;
    double d = 0.0;
    bool flipped = false;
};
//: What overlap_scan found: how many faces overlap, and the faces to replace (face
//: index -> its pieces) in the order add.py's dict keeps them.
struct OverlapScan {
    int count = 0;
    std::vector<std::pair<int, CutFace>> replaced;
};
//: The engine behind overlaps() and cut_overlaps().
inline OverlapScan overlap_scan(const Mesh& M, double tol, bool cut);
//: Cut back faces that lie in one plane and overlap (in place); how many faces were cut.
inline int cut_overlaps(Mesh& M, double tol = 0.001);
//: Python's ``"%.Nf" % x`` (printf's, except that a NaN is "nan" whatever its sign).
inline std::string check_f(double x, int decimals);
//: Python's ``"%d" % x`` of a float: its whole part (an exception for a NaN or an infinity).
inline std::string check_d(double x);
}  // namespace detail

//: Close the tiny gaps left where an edge runs past another vertex.
inline Mesh heal(const Mesh& M, double tol = 1e-7);
inline Mesh heal();
//: How many faces are not convex.
inline int concave_faces(const Mesh& M);
inline int concave_faces();
//: How many faces lie in the same plane as a bigger face and overlap it.
inline int overlaps(const Mesh& M, double tol = 0.001);
inline int overlaps();
//: A copy in which every face is a triangle (fan triangulation).
inline Mesh triangulate(const Mesh& M);
inline Mesh triangulate();
//: Make every face of a copy point the same way (outward, if the model is closed).
inline Mesh fix_normals(const Mesh& M, bool outward = true);
inline Mesh fix_normals();

//: What clean() did (with report = true).
struct CleanReport {
    int vertices_removed = 0, faces_removed = 0, faces_cut = 0, faces_split = 0;
};
//: Repair a model and return the tidy copy (see add.py's clean).  ``report``, when
//: given, receives what was done.
inline Mesh clean(const Mesh& M, double tol = 1e-7, bool weld = true, bool degenerate = true,
                  bool duplicates = true, bool internal = true, bool unused = true, bool normals = false,
                  CleanReport* report = nullptr, bool overlaps = true, bool convex = true);
inline Mesh clean();

//: What stats() tells about a model.
struct Stats {
    int vertices = 0, faces = 0, triangles = 0, colors = 0;
    std::array<Point, 2> bbox{};
    Point size;
    double area = 0.0, volume = 0.0;
    int open_edges = 0, non_manifold_edges = 0, duplicate_vertices = 0, duplicate_faces = 0,
        back_to_back_faces = 0;
    bool closed = false;
    long long obj_bytes = 0;
    int transparent_faces = 0;
    std::vector<std::string> textures;
};
//: Counts, size, area, volume, health.
inline Stats stats(const Mesh& M);
inline Stats stats();

inline constexpr int SKETCHFAB_MB = 50;
inline constexpr int SKETCHFAB_COLORS = 50;
//: Print a health report and say whether the model meets the assignment.
inline bool check(const Mesh& M, int min_faces = 10000, int min_colors = 3, bool quiet = false,
                  double max_mb = SKETCHFAB_MB, int max_colors = SKETCHFAB_COLORS);
inline bool check();

}  // namespace add
//@@definitions
namespace add {

namespace detail {

struct CellKey {
    long long i, j, k;
    bool operator==(const CellKey& o) const { return i == o.i && j == o.j && k == o.k; }
};
struct CellKeyHash {
    size_t operator()(const CellKey& c) const {
        uint64_t h = (uint64_t)c.i * 0x9E3779B97F4A7C15ull;
        h ^= (uint64_t)c.j * 0xC2B2AE3D27D4EB4Full + (h << 6) + (h >> 2);
        h ^= (uint64_t)c.k * 0x165667B19E3779F9ull + (h << 6) + (h >> 2);
        return (size_t)h;
    }
};

inline long long cell_floor(double x) {
    if (std::isnan(x)) throw std::invalid_argument("cannot convert float NaN to integer");
    if (std::isinf(x)) throw std::overflow_error("cannot convert float infinity to integer");
    double f = std::floor(x);
    // Python's integers have no limit; a cell number beyond 64 bits (a coordinate some
    // 1e12 times the tolerance) is refused here rather than silently wrapped round.
    // (Strictly inside the range, so that the neighbours k - 1 and k + 1 fit too.)
    if (!(f > -9223372036854775808.0 && f < 9223372036854775808.0))
        throw std::overflow_error("cell number out of the 64-bit range: coordinates too large for the tolerance");
    return (long long)f;
}

inline double key_round(double x) {
    if (std::isnan(x)) throw std::invalid_argument("cannot convert float NaN to integer");
    if (std::isinf(x)) throw std::overflow_error("cannot convert float infinity to integer");
    return std::nearbyint(x) + 0.0;                            // (a whole number: never -0.0)
}

//: Grid cell(s) a point may belong to, allowing for rounding at the edges.
inline std::vector<CellKey> cell_keys(const Point& p, double tol) {
    std::vector<long long> ranges[3];
    for (int a = 0; a < 3; ++a) {
        double q = p[a] / tol;
        long long k = cell_floor(q + 0.5);                     // (NaN, inf: an exception, as in add.py)
        double frac = q + 0.5 - std::floor(q + 0.5);
        if (frac < 0.25) ranges[a] = {k, k - 1};
        else if (frac > 0.75) ranges[a] = {k, k + 1};
        else ranges[a] = {k};
    }
    std::vector<CellKey> out;
    for (long long i : ranges[0])
        for (long long j : ranges[1])
            for (long long k : ranges[2]) out.push_back({i, j, k});
    return out;
}

inline int weld(Mesh& M, double tol) {
    std::unordered_map<CellKey, int, CellKeyHash> lookup;
    std::vector<int> remap(M.V.size(), 0);
    std::vector<Point> newV;
    for (size_t i = 0; i < M.V.size(); ++i) {
        const Point& p = M.V[i];
        int found = -1;
        std::vector<CellKey> keys = cell_keys(p, tol);
        for (const CellKey& key : keys) {
            auto it = lookup.find(key);
            if (it != lookup.end()) {
                const Point& q = newV[it->second];
                if (std::fabs(q[0] - p[0]) <= tol && std::fabs(q[1] - p[1]) <= tol && std::fabs(q[2] - p[2]) <= tol) {
                    found = it->second;
                    break;
                }
            }
        }
        if (found < 0) {
            found = (int)newV.size();
            newV.push_back(p);
            for (const CellKey& key : keys) lookup.emplace(key, found);
        }
        remap[i] = found;
    }
    int removed = (int)(M.V.size() - newV.size());
    M.V = std::move(newV);
    for (Face& f : M.F)
        for (int& i : f) i = remap[i];
    return removed;
}

inline std::vector<int> weld_map(const std::vector<Point>& V, double tol) {
    std::unordered_map<CellKey, int, CellKeyHash> lookup;
    std::vector<int> rep(V.size(), 0);
    for (size_t i = 0; i < V.size(); ++i) {
        const Point& p = V[i];
        int found = -1;
        std::vector<CellKey> keys = cell_keys(p, tol);
        for (const CellKey& key : keys) {
            auto it = lookup.find(key);
            if (it != lookup.end()) {
                const Point& q = V[it->second];
                if (std::fabs(q[0] - p[0]) <= tol && std::fabs(q[1] - p[1]) <= tol && std::fabs(q[2] - p[2]) <= tol) {
                    found = it->second;
                    break;
                }
            }
        }
        if (found < 0) {
            found = (int)i;
            for (const CellKey& key : keys) lookup.emplace(key, found);
        }
        rep[i] = found;
    }
    return rep;
}

inline std::pair<double, double> piece_volume(const Mesh& M, const std::vector<int>& faces, const std::vector<int>& rep) {
    std::set<int> corners;
    for (int fi : faces)
        for (int i : M.F[fi]) corners.insert(rep[i]);
    double n = (double)corners.size();
    double c[3], size = 0.0;
    for (int a = 0; a < 3; ++a) {
        double s = 0.0, lo = 0.0, hi = 0.0;
        bool first = true;
        for (int i : corners) {
            double v = M.V[i][a];
            s = s + v;
            if (first || v < lo) lo = v;
            if (first || v > hi) hi = v;
            first = false;
        }
        c[a] = s / n;
        if (a == 0 || hi - lo > size) size = hi - lo;
    }
    double total = 0.0;
    for (int fi : faces) {
        const Face& f = M.F[fi];
        if (f.size() < 3) continue;
        double a[3] = {M.V[f[0]][0] - c[0], M.V[f[0]][1] - c[1], M.V[f[0]][2] - c[2]};
        for (size_t t = 1; t + 1 < f.size(); ++t) {
            double b[3] = {M.V[f[t]][0] - c[0], M.V[f[t]][1] - c[1], M.V[f[t]][2] - c[2]};
            double d[3] = {M.V[f[t + 1]][0] - c[0], M.V[f[t + 1]][1] - c[1], M.V[f[t + 1]][2] - c[2]};
            total += (a[0] * (b[1] * d[2] - b[2] * d[1])
                      - a[1] * (b[0] * d[2] - b[2] * d[0])
                      + a[2] * (b[0] * d[1] - b[1] * d[0]));
        }
    }
    return {total, std::pow(size, 3.0)};
}

inline int keep_faces(Mesh& M, const std::vector<int>& keep) {
    int removed = (int)M.F.size() - (int)keep.size();
    std::vector<Face> F;
    std::vector<Color> C;
    std::vector<std::vector<Point2>> UV;
    F.reserve(keep.size());
    C.reserve(keep.size());
    for (int i : keep) {
        F.push_back(std::move(M.F[i]));
        C.push_back(M.C[i]);
        if (M.has_uv) UV.push_back(M.UV[i]);
    }
    M.F = std::move(F);
    M.C = std::move(C);
    if (M.has_uv) M.UV = std::move(UV);
    return removed;
}

inline std::set<int> not_finite(const Mesh& M) {
    double total = 0.0;
    for (const Point& p : M.V) total += p[0] + p[1] + p[2];
    std::set<int> bad;
    if (std::isfinite(total)) return bad;
    for (size_t i = 0; i < M.V.size(); ++i) {
        const Point& p = M.V[i];
        if (!(std::isfinite(p[0]) && std::isfinite(p[1]) && std::isfinite(p[2]))) bad.insert((int)i);
    }
    return bad;
}

inline int drop_not_finite(Mesh& M) {
    std::set<int> bad = not_finite(M);
    if (bad.empty()) return 0;
    std::vector<int> keep;
    for (size_t k = 0; k < M.F.size(); ++k) {
        bool ok = true;
        for (int i : M.F[k])
            if (bad.count(i)) { ok = false; break; }
        if (ok) keep.push_back((int)k);
    }
    int removed = keep_faces(M, keep);
    std::vector<int> remap(M.V.size(), -1);
    std::vector<Point> newV;
    for (size_t i = 0; i < M.V.size(); ++i) {
        if (!bad.count((int)i)) {
            remap[i] = (int)newV.size();
            newV.push_back(M.V[i]);
        }
    }
    M.V = std::move(newV);
    for (Face& f : M.F)
        for (int& i : f) i = remap[i];
    return removed;
}

inline std::vector<std::pair<Face, std::vector<Point2>>> split_repeats(const Face& f, const std::vector<Point2>* uv) {
    Face clean_f;
    std::vector<Point2> clean_uv;
    for (size_t t = 0; t < f.size(); ++t) {                    // drop repeated corners
        int i = f[t];
        if (clean_f.empty() || clean_f.back() != i) {
            clean_f.push_back(i);
            if (uv) clean_uv.push_back((*uv)[t]);
        }
    }
    if (clean_f.size() > 1 && clean_f.front() == clean_f.back()) {
        clean_f.pop_back();
        if (uv) clean_uv.pop_back();
    }
    std::set<int> distinct(clean_f.begin(), clean_f.end());
    if (distinct.size() == clean_f.size()) return {{clean_f, clean_uv}};
    std::map<int, size_t> seen;
    for (size_t j = 0; j < clean_f.size(); ++j) {
        int i = clean_f[j];
        auto it = seen.find(i);
        if (it != seen.end()) {                                // pinch: split here
            size_t a = it->second;
            Face first(clean_f.begin() + a, clean_f.begin() + j);
            Face rest(clean_f.begin() + j, clean_f.end());
            rest.insert(rest.end(), clean_f.begin(), clean_f.begin() + a);
            std::vector<Point2> first_uv, rest_uv;
            if (uv) {
                first_uv.assign(clean_uv.begin() + a, clean_uv.begin() + j);
                rest_uv.assign(clean_uv.begin() + j, clean_uv.end());
                rest_uv.insert(rest_uv.end(), clean_uv.begin(), clean_uv.begin() + a);
            }
            auto out = split_repeats(first, uv ? &first_uv : nullptr);
            auto more = split_repeats(rest, uv ? &rest_uv : nullptr);
            out.insert(out.end(), more.begin(), more.end());
            return out;
        }
        seen[i] = j;
    }
    return {{clean_f, clean_uv}};
}

inline int drop_degenerate(Mesh& M, double tol) {
    std::vector<int> keep;
    std::vector<Face> extra_F;
    std::vector<Color> extra_C;
    std::vector<std::vector<Point2>> extra_UV;
    for (size_t k = 0; k < M.F.size(); ++k) {
        const std::vector<Point2>* uv = M.has_uv ? &M.UV[k] : nullptr;
        if (uv && uv->empty()) uv = nullptr;
        const Face& f = M.F[k];
        std::set<int> distinct(f.begin(), f.end());
        std::vector<std::pair<Face, std::vector<Point2>>> pieces;
        if (distinct.size() == f.size()) pieces.push_back({f, uv ? *uv : std::vector<Point2>()});
        else pieces = split_repeats(f, uv);
        bool first = true;
        for (auto& piece : pieces) {
            Face& clean_f = piece.first;
            std::set<int> d2(clean_f.begin(), clean_f.end());
            if (clean_f.size() < 3 || d2.size() < 3) continue;
            if (norm(face_normal(M, clean_f)) <= tol) continue;
            if (first) {
                M.F[k] = clean_f;
                if (uv) M.UV[k] = piece.second;
                keep.push_back((int)k);
                first = false;
            } else {                                           // a second loop of a pinched face
                extra_F.push_back(clean_f);
                extra_C.push_back(M.C[k]);
                extra_UV.push_back(piece.second);
            }
        }
    }
    int removed = keep_faces(M, keep);
    if (!extra_F.empty()) {
        M.F.insert(M.F.end(), extra_F.begin(), extra_F.end());
        M.C.insert(M.C.end(), extra_C.begin(), extra_C.end());
        if (M.has_uv) M.UV.insert(M.UV.end(), extra_UV.begin(), extra_UV.end());
        removed -= (int)extra_F.size();
    }
    return removed;
}

inline int dedup_faces(Mesh& M) {
    std::set<Face> seen;
    std::vector<int> keep;
    for (size_t k = 0; k < M.F.size(); ++k) {
        Face key = M.F[k];
        std::sort(key.begin(), key.end());
        if (seen.count(key)) continue;
        seen.insert(key);
        keep.push_back((int)k);
    }
    return keep_faces(M, keep);
}

inline bool winding(const Face& f) {
    if (f.empty()) throw std::invalid_argument("min() arg is an empty sequence");   // (as add.py)
    size_t k = (size_t)(std::min_element(f.begin(), f.end()) - f.begin());
    size_t n = f.size();
    return f[(k + 1) % n] < f[(k + n - 1) % n];
}

inline int drop_internal(Mesh& M) {
    std::map<Face, std::vector<int>> groups;
    std::vector<Face> order;                                   // (the keys in the order they first came)
    for (size_t i = 0; i < M.F.size(); ++i) {
        Face key = M.F[i];
        std::sort(key.begin(), key.end());
        auto it = groups.find(key);
        if (it == groups.end()) {
            groups[key] = {(int)i};
            order.push_back(key);
        } else {
            it->second.push_back((int)i);
        }
    }
    std::set<int> drop;
    for (const Face& key : order) {
        const std::vector<int>& idx = groups[key];
        if (idx.size() < 2) continue;
        std::vector<int> forward, backward;
        for (int i : idx) (winding(M.F[i]) ? forward : backward).push_back(i);
        size_t pairs = std::min(forward.size(), backward.size());
        for (size_t t = 0; t < pairs; ++t) {
            drop.insert(forward[t]);
            drop.insert(backward[t]);
        }
    }
    if (drop.empty()) return 0;
    std::vector<int> keep;
    for (size_t i = 0; i < M.F.size(); ++i)
        if (!drop.count((int)i)) keep.push_back((int)i);
    return keep_faces(M, keep);
}

inline int drop_unused(Mesh& M) {
    std::vector<char> used(M.V.size(), 0);
    size_t count = 0;
    for (const Face& f : M.F)
        for (int i : f)
            if (!used[i]) { used[i] = 1; ++count; }
    if (count == M.V.size()) return 0;
    std::vector<int> remap(M.V.size(), -1);
    std::vector<Point> newV;
    for (size_t i = 0; i < M.V.size(); ++i) {
        if (used[i]) {
            remap[i] = (int)newV.size();
            newV.push_back(M.V[i]);
        }
    }
    int removed = (int)(M.V.size() - newV.size());
    M.V = std::move(newV);
    for (Face& f : M.F)
        for (int& i : f) i = remap[i];
    return removed;
}

inline double poly_area2(const Profile& pts) {
    double a = 0.0;
    size_t n = pts.size();
    for (size_t i = 0; i < n; ++i) {
        double x0 = pts[i][0], y0 = pts[i][1];
        double x1 = pts[(i + 1) % n][0], y1 = pts[(i + 1) % n][1];
        a += x0 * y1 - x1 * y0;
    }
    return a;
}

// -- coplanar overlaps: the cause of flicker ("z-fighting") in viewers -------

inline Profile clip_half(const Profile& pts, const Point2& a, const Point2& b, bool keep_left) {
    double ax = a[0], ay = a[1];
    double bx = b[0], by = b[1];
    double ex = bx - ax, ey = by - ay;
    Profile out;
    size_t n = pts.size();
    if (n == 0) return out;
    Point2 prev = pts[n - 1];
    double prev_s = ex * (prev[1] - ay) - ey * (prev[0] - ax);
    for (const Point2& cur : pts) {
        double cur_s = ex * (cur[1] - ay) - ey * (cur[0] - ax);
        bool cur_in = keep_left ? cur_s >= 0 : cur_s <= 0;
        bool prev_in = keep_left ? prev_s >= 0 : prev_s <= 0;
        if (cur_in != prev_in) {
            double t = prev_s / (prev_s - cur_s);
            out.push_back({prev[0] + (cur[0] - prev[0]) * t, prev[1] + (cur[1] - prev[1]) * t});
        }
        if (cur_in) out.push_back(cur);
        prev = cur;
        prev_s = cur_s;
    }
    return out;
}

inline std::vector<Profile> convex_minus(const Profile& A, const Profile& B, double eps, bool* untouched) {
    if (untouched) *untouched = true;
    size_t nb = B.size();
    Profile inside = A;
    for (size_t i = 0; i < nb; ++i) {
        inside = clip_half(inside, B[i], B[(i + 1) % nb], true);
        if (inside.size() < 3) return {A};
    }
    if (std::fabs(poly_area2(inside)) <= eps) return {A};
    if (untouched) *untouched = false;
    std::vector<Profile> pieces;
    Profile current = A;
    for (size_t i = 0; i < nb; ++i) {
        const Point2& a = B[i];
        const Point2& b = B[(i + 1) % nb];
        Profile outside = clip_half(current, a, b, false);
        if (outside.size() >= 3 && std::fabs(poly_area2(outside)) > eps) pieces.push_back(outside);
        current = clip_half(current, a, b, true);
        if (current.size() < 3) break;
    }
    return pieces;
}

inline std::vector<Profile> ears(const Profile& pts) {
    std::vector<int> idx(pts.size());
    std::iota(idx.begin(), idx.end(), 0);
    std::vector<Profile> tris;
    long long guard = 0;
    while (idx.size() > 3 && guard < 10 * (long long)pts.size()) {
        guard += 1;
        int n = (int)idx.size();
        bool found = false;
        for (int k = 0; k < n; ++k) {
            int i0 = idx[(k + n - 1) % n], i1 = idx[k], i2 = idx[(k + 1) % n];
            const Point2& a = pts[i0];
            const Point2& b = pts[i1];
            const Point2& c = pts[i2];
            if ((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) <= 0)
                continue;                                      // a reflex corner, not an ear
            bool ok = true;
            for (int j : idx) {
                if (j == i0 || j == i1 || j == i2) continue;
                const Point2& p = pts[j];
                double s1 = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]);
                double s2 = (c[0] - b[0]) * (p[1] - b[1]) - (c[1] - b[1]) * (p[0] - b[0]);
                double s3 = (a[0] - c[0]) * (p[1] - c[1]) - (a[1] - c[1]) * (p[0] - c[0]);
                if (s1 > 0 && s2 > 0 && s3 > 0) {
                    ok = false;
                    break;
                }
            }
            if (ok) {
                tris.push_back({a, b, c});
                idx.erase(idx.begin() + k);
                found = true;
                break;
            }
        }
        if (!found) break;
    }
    if (idx.size() == 3) tris.push_back({pts[idx[0]], pts[idx[1]], pts[idx[2]]});
    return tris;
}

inline std::vector<Profile> convex_pieces(const Profile& pts) {
    size_t n = pts.size();
    for (size_t i = 0; i < n; ++i) {
        const Point2& a = pts[(i + n - 1) % n];
        const Point2& b = pts[i];
        const Point2& c = pts[(i + 1) % n];
        if ((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) < 0) return ears(pts);
    }
    return {pts};
}

inline std::optional<std::vector<std::array<int, 3>>> ear_triangles(const Profile& pts) {
    std::vector<int> idx(pts.size());
    std::iota(idx.begin(), idx.end(), 0);
    std::vector<std::array<int, 3>> tris;
    while (idx.size() > 3) {
        int n = (int)idx.size();
        bool cut = false;
        for (int k = 0; k < n; ++k) {
            int i0 = idx[(k + n - 1) % n], i1 = idx[k], i2 = idx[(k + 1) % n];
            const Point2& a = pts[i0];
            const Point2& b = pts[i1];
            const Point2& c = pts[i2];
            if ((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) <= 0)
                continue;                                      // a reflex (or straight) corner is no ear
            bool blocked = false;
            for (int j : idx) {
                if (j == i0 || j == i1 || j == i2) continue;
                const Point2& q = pts[j];
                if ((b[0] - a[0]) * (q[1] - a[1]) - (b[1] - a[1]) * (q[0] - a[0]) >= 0 &&
                    (c[0] - b[0]) * (q[1] - b[1]) - (c[1] - b[1]) * (q[0] - b[0]) >= 0 &&
                    (a[0] - c[0]) * (q[1] - c[1]) - (a[1] - c[1]) * (q[0] - c[0]) >= 0) {
                    blocked = true;                            // another corner inside: cutting here would overlap
                    break;
                }
            }
            if (!blocked) {
                tris.push_back({i0, i1, i2});
                idx.erase(idx.begin() + k);
                cut = true;
                break;
            }
        }
        if (!cut) return std::nullopt;
    }
    if (idx.size() < 3) throw std::out_of_range("list index out of range");   // (add.py: an IndexError)
    tris.push_back({idx[0], idx[1], idx[2]});
    return tris;
}

inline bool is_concave(const Mesh& M, const Face& f, std::optional<Point> n_) {
    size_t k = f.size();
    if (k < 4) return false;
    Point n = n_ ? *n_ : face_normal(M, f);
    double ln = std::sqrt(n[0] * n[0] + n[1] * n[1] + n[2] * n[2]);
    if (ln < 1e-12) return false;
    double nx = n[0] / ln, ny = n[1] / ln, nz = n[2] / ln;
    Points P;
    P.reserve(k);
    for (int i : f) P.push_back(M.V[i]);
    for (size_t i = 0; i < k; ++i) {
        const Point& a = P[(i + k - 1) % k];
        const Point& b = P[i];
        const Point& c = P[(i + 1) % k];
        double e1x = b[0] - a[0], e1y = b[1] - a[1], e1z = b[2] - a[2];
        double e2x = c[0] - b[0], e2y = c[1] - b[1], e2z = c[2] - b[2];
        double turn = ((e1y * e2z - e1z * e2y) * nx + (e1z * e2x - e1x * e2z) * ny + (e1x * e2y - e1y * e2x) * nz);
        if (turn < -1e-9 * (e1x * e1x + e1y * e1y + e1z * e1z + e2x * e2x + e2y * e2y + e2z * e2z)) return true;
    }
    return false;
}

inline int split_concave(Mesh& M) {
    std::vector<Face> newF;
    std::vector<Color> newC;
    std::vector<std::vector<Point2>> newUV;
    int count = 0;
    for (size_t k = 0; k < M.F.size(); ++k) {
        const Face& f = M.F[k];
        std::optional<std::vector<std::array<int, 3>>> tris;
        if (f.size() > 3) {
            Point n = face_normal(M, f);
            if (is_concave(M, f, n)) {
                Frame fr = frame(n);
                Profile pts;
                for (int i : f) pts.push_back({dot(M.V[i], fr.u), dot(M.V[i], fr.v)});
                std::vector<int> order(f.size());
                std::iota(order.begin(), order.end(), 0);
                bool flip = poly_area2(pts) < 0;
                if (flip) {
                    std::reverse(order.begin(), order.end());
                    std::reverse(pts.begin(), pts.end());
                }
                auto found = ear_triangles(pts);
                if (found) {
                    tris.emplace();
                    for (const auto& ear : *found) {
                        std::array<int, 3> t = {order[ear[0]], order[ear[1]], order[ear[2]]};
                        if (flip) std::reverse(t.begin(), t.end());
                        tris->push_back(t);
                    }
                }
            }
        }
        const std::vector<Point2> none;
        const std::vector<Point2>& uv = M.has_uv ? M.UV[k] : none;   // (empty: add.py's None)
        if (!tris) {
            newF.push_back(f);
            newC.push_back(M.C[k]);
            newUV.push_back(uv);
            continue;
        }
        count += 1;
        for (const auto& t : *tris) {
            newF.push_back({f[t[0]], f[t[1]], f[t[2]]});
            newC.push_back(M.C[k]);
            newUV.push_back(uv.empty() ? std::vector<Point2>()
                                       : std::vector<Point2>{uv.at(t[0]), uv.at(t[1]), uv.at(t[2])});
        }
    }
    if (count) {
        M.F = std::move(newF);
        M.C = std::move(newC);
        if (M.has_uv) M.UV = std::move(newUV);
    }
    return count;
}

inline std::vector<PlaneGroup> overlap_groups(const Mesh& M, double tol) {
    // add.py's dict {key: [face, ...]}: the keys in the order they first came (a key
    // equal to an earlier one -- 0.0 and -0.0 are equal -- joins that one's group).
    std::map<std::array<double, 4>, size_t> where;
    std::vector<std::pair<std::array<double, 4>, std::vector<int>>> groups;
    for (size_t i = 0; i < M.F.size(); ++i) {
        const Face& f = M.F[i];
        if (f.size() < 3) continue;
        Point n = face_normal(M, f);
        double ln = norm(n);
        if (ln < 1e-12) continue;
        n = {n[0] / ln, n[1] / ln, n[2] / ln};
        Point c{0.0, 0.0, 0.0};
        for (int k : f) {
            const Point& p = M.V[k];
            c[0] += p[0];
            c[1] += p[1];
            c[2] += p[2];
        }
        double d = dot(n, c) / (double)f.size();
        std::array<double, 3> nk = {py_round(n[0], 3), py_round(n[1], 3), py_round(n[2], 3)};
        bool below = false;                                    // nk < (0, 0, 0) as Python compares tuples
        for (int a = 0; a < 3; ++a)
            if (nk[a] != 0.0) {
                below = nk[a] < 0.0;
                break;
            }
        bool zero = nk[0] == 0.0 && nk[1] == 0.0 && nk[2] == 0.0;
        if (below || (zero && n[2] < 0)) {                     // one key for both sides of a plane
            nk = {-nk[0] + 0.0, -nk[1] + 0.0, -nk[2] + 0.0};
            d = -d;
        }
        std::array<double, 4> key = {nk[0], nk[1], nk[2], key_round(d / tol) * tol};
        auto it = where.find(key);
        if (it == where.end()) {
            where.emplace(key, groups.size());
            groups.push_back({key, {(int)i}});
        } else {
            groups[it->second].second.push_back((int)i);
        }
    }
    std::vector<PlaneGroup> out;
    for (const auto& g : groups) {
        const std::vector<int>& idx = g.second;
        if (idx.size() < 2) continue;
        PlaneGroup G;
        G.key = g.first;
        G.n = unit({g.first[0], g.first[1], g.first[2]});
        Frame fr = frame(G.n);
        G.u = fr.u;
        G.v = fr.v;
        for (int i : idx) {
            Profile pts;
            for (int k : M.F[i]) pts.push_back({dot(M.V[k], G.u), dot(M.V[k], G.v)});
            double area2 = poly_area2(pts);
            bool flipped = area2 < 0;
            if (flipped) {
                std::reverse(pts.begin(), pts.end());
                area2 = -area2;
            }
            double x0 = pts[0][0], y0 = pts[0][1], x1 = pts[0][0], y1 = pts[0][1];
            for (const Point2& p : pts) {                      // (Python's min / max: the first of equals)
                if (p[0] < x0) x0 = p[0];
                if (p[1] < y0) y0 = p[1];
                if (p[0] > x1) x1 = p[0];
                if (p[1] > y1) y1 = p[1];
            }
            PlanePoly P;
            P.area = area2 / 2.0;
            P.index = i;
            P.pts = std::move(pts);
            P.bb = {x0, y0, x1, y1};
            P.flipped = flipped;
            G.polys.push_back(std::move(P));
        }
        out.push_back(std::move(G));
    }
    return out;
}

inline double convex_overlap2(const Profile& A, const Profile& B) {
    size_t nb = B.size();
    Profile inside = A;
    for (size_t i = 0; i < nb; ++i) {
        inside = clip_half(inside, B[i], B[(i + 1) % nb], true);
        if (inside.size() < 3) return 0.0;
    }
    return std::fabs(poly_area2(inside));
}

inline std::optional<std::vector<Profile>> minus_all(std::vector<Profile> pieces, const std::vector<Profile>& others,
                                                     double eps, size_t limit) {
    for (const Profile& other : others) {
        std::vector<Profile> next;
        for (const Profile& part : pieces) {
            std::vector<Profile> q = convex_minus(part, other, eps);
            next.insert(next.end(), q.begin(), q.end());
        }
        pieces = std::move(next);
        if (pieces.size() > limit) return std::nullopt;
    }
    return pieces;
}

inline OverlapScan overlap_scan(const Mesh& M, double tol, bool cut) {
    std::set<int> touched;
    std::vector<std::pair<int, CutFace>> replaced;             // add.py's dict: in the order the keys first came
    std::map<int, size_t> replaced_at;
    auto replace = [&](int i, CutFace r) {
        auto it = replaced_at.find(i);
        if (it == replaced_at.end()) {
            replaced_at.emplace(i, replaced.size());
            replaced.push_back({i, std::move(r)});
        } else {
            replaced[it->second].second = std::move(r);         // (a dict keeps a key where it first came)
        }
    };
    for (PlaneGroup& G : overlap_groups(M, tol)) {
        std::vector<PlanePoly>& polys = G.polys;
        std::stable_sort(polys.begin(), polys.end(),
                         [](const PlanePoly& a, const PlanePoly& b) { return -a.area < -b.area; });
        double largest = polys[0].area;
        double eps = 1e-9 * (1.0 + largest);
        double cell = std::max(1e-6, std::sqrt(std::max(1e-12, polys[polys.size() / 2].area)) * 2.0);
        std::unordered_map<CellKey, std::vector<int>, CellKeyHash> grid;    // (cx, cy) -> faces
        std::vector<int> big;                                  // a few big faces: checked against everyone
        std::map<int, std::vector<Profile>> drawn;             // face -> its convex pieces as drawn
        std::map<int, std::vector<Profile>> current;           // face -> its pieces now
        std::map<int, bool> flip;
        std::map<int, std::array<double, 4>> box;              // face -> its bounding box
        std::vector<std::pair<int, std::vector<int>>> contacts;   // bigger face -> smaller faces on its back
        std::map<int, size_t> contacts_at;

        auto cells = [&](const std::array<double, 4>& bb) {
            return std::array<long long, 4>{cell_floor(bb[0] / cell), cell_floor(bb[1] / cell),
                                            cell_floor(bb[2] / cell), cell_floor(bb[3] / cell)};
        };
        auto keep = [&](int entry, const std::array<double, 4>& bb) {
            std::array<long long, 4> c = cells(bb);
            if (((double)c[2] - (double)c[0] + 1.0) * ((double)c[3] - (double)c[1] + 1.0) > 400) {   // (cannot overflow)
                big.push_back(entry);
                return;
            }
            for (long long cx = c[0]; cx <= c[2]; ++cx)
                for (long long cy = c[1]; cy <= c[3]; ++cy) grid[CellKey{cx, cy, 0}].push_back(entry);
        };

        for (const PlanePoly& P : polys) {
            const int i = P.index;
            const std::array<double, 4>& bb = P.bb;
            const bool flipped = P.flipped;
            std::array<long long, 4> c = cells(bb);
            std::set<int> seen;
            std::vector<int> candidates = big;
            for (long long cx = c[0]; cx <= c[2]; ++cx)
                for (long long cy = c[1]; cy <= c[3]; ++cy) {
                    auto it = grid.find(CellKey{cx, cy, 0});
                    if (it == grid.end()) continue;
                    for (int entry : it->second)
                        if (seen.insert(entry).second) candidates.push_back(entry);
                }
            std::vector<Profile> own = convex_pieces(P.pts);   // the face as it was drawn
            std::vector<Profile> pieces = own;
            bool changed = false;
            for (int k : candidates) {
                const std::array<double, 4>& kbb = box[k];
                if (bb[0] >= kbb[2] || bb[2] <= kbb[0] || bb[1] >= kbb[3] || bb[3] <= kbb[1]) continue;
                const std::vector<Profile>& kpieces = drawn[k];
                if (flip[k] != flipped) {                      // back to back: remember the contact
                    bool any = false;
                    for (const Profile& a : pieces) {
                        for (const Profile& b : kpieces)
                            if (convex_overlap2(a, b) > eps) {
                                any = true;
                                break;
                            }
                        if (any) break;
                    }
                    if (any) {
                        auto it = contacts_at.find(k);
                        if (it == contacts_at.end()) {
                            contacts_at.emplace(k, contacts.size());
                            contacts.push_back({k, {i}});
                        } else {
                            contacts[it->second].second.push_back(i);
                        }
                    }
                    continue;
                }
                std::vector<Profile> new_pieces;
                for (const Profile& piece : pieces) {
                    // ``parts`` stays the very list [piece] (add.py tests ``parts[0] is piece``)
                    // for as long as every subtraction gives the piece back untouched.
                    bool same = true;
                    std::vector<Profile> parts;
                    for (const Profile& other : kpieces) {
                        if (same) {
                            bool untouched = true;
                            std::vector<Profile> q = convex_minus(piece, other, eps, &untouched);
                            if (!untouched) {
                                same = false;
                                parts = std::move(q);
                            }
                        } else {
                            std::vector<Profile> next;
                            for (const Profile& part : parts) {
                                std::vector<Profile> q = convex_minus(part, other, eps);
                                next.insert(next.end(), q.begin(), q.end());
                            }
                            parts = std::move(next);
                        }
                    }
                    if (same) {
                        new_pieces.push_back(piece);
                    } else {
                        changed = true;
                        new_pieces.insert(new_pieces.end(), parts.begin(), parts.end());
                    }
                }
                pieces = std::move(new_pieces);
                if (changed && (!cut || pieces.size() > 64)) break;
            }
            if (changed) {
                touched.insert(i);
                if (cut && pieces.size() <= 64) replace(i, CutFace{pieces, G.u, G.v, G.n, G.key[3], flipped});
            }
            // later, smaller faces are cut against the face as drawn: the same
            // result as against its pieces, with far less to compare
            bool keep_pieces = cut && pieces.size() <= 64;
            drawn[i] = own;
            current[i] = keep_pieces ? pieces : own;
            flip[i] = flipped;
            box[i] = bb;
            keep(i, bb);
        }
        for (const auto& contact : contacts) {                 // the patches where solids touch
            int k = contact.first;
            const std::vector<int>& small = contact.second;
            if (!cut) {
                touched.insert(k);
                touched.insert(small.begin(), small.end());
                continue;
            }
            std::vector<Profile> others;
            for (int i : small)
                for (const Profile& q : current[i]) others.push_back(q);
            std::optional<std::vector<Profile>> rest = minus_all(current[k], others, eps);
            if (!rest) continue;                               // the bigger face would shatter: leave the contact
            replace(k, CutFace{*rest, G.u, G.v, G.n, G.key[3], flip[k]});
            current[k] = *rest;
            touched.insert(k);
            for (int i : small) {
                std::optional<std::vector<Profile>> left = minus_all(current[i], drawn[k], eps);
                if (left) {
                    replace(i, CutFace{*left, G.u, G.v, G.n, G.key[3], flip[i]});
                    current[i] = *left;
                    touched.insert(i);
                }
            }
        }
    }
    OverlapScan out;
    out.count = (int)touched.size();
    out.replaced = std::move(replaced);
    return out;
}

inline int cut_overlaps(Mesh& M, double tol) {
    OverlapScan scan = overlap_scan(M, tol, true);
    if (scan.replaced.empty()) return 0;
    std::vector<char> gone(M.F.size(), 0);
    for (const auto& r : scan.replaced) gone[r.first] = 1;
    std::vector<int> keep_idx;
    for (size_t i = 0; i < M.F.size(); ++i)
        if (!gone[i]) keep_idx.push_back((int)i);
    std::vector<Face> new_F;
    std::vector<Color> new_C;
    std::vector<std::vector<Point2>> new_UV;                   // (empty: add.py's None)
    struct Affine { Point2 a, b, c, ua, ub, uc; double det; };
    for (const auto& r : scan.replaced) {
        int i = r.first;
        const CutFace& R = r.second;
        const Point &u = R.u, &v = R.v, &n = R.n;
        double d = R.d;
        const Face f = M.F[i];
        Point base{n[0] * d, n[1] * d, n[2] * d};              // a point of the plane
        // texture coordinates: the affine map of the original corners, if any
        const std::vector<Point2>* uv = M.has_uv && !M.UV[i].empty() ? &M.UV[i] : nullptr;
        std::optional<Affine> affine;
        if (uv && f.size() >= 3) {
            Profile P2;
            for (int k : f) P2.push_back({dot(M.V[k], u), dot(M.V[k], v)});
            size_t nf = f.size();
            for (size_t a = 0; a < nf; ++a) {
                size_t b = (a + 1) % nf, c = (a + 2) % nf;
                double det = ((P2[b][0] - P2[a][0]) * (P2[c][1] - P2[a][1])
                              - (P2[c][0] - P2[a][0]) * (P2[b][1] - P2[a][1]));
                if (std::fabs(det) > 1e-12) {
                    affine = Affine{P2[a], P2[b], P2[c], uv->at(a), uv->at(b), uv->at(c), det};
                    break;
                }
            }
        }
        for (const Profile& piece : R.pieces) {
            if (piece.size() < 3 || std::fabs(poly_area2(piece)) <= 1e-12) continue;
            Face idx;
            std::vector<Point2> piece_uv;
            for (const Point2& st : piece) {
                double s_ = st[0], t_ = st[1];
                idx.push_back(M.add_vertex({base[0] + u[0] * s_ + v[0] * t_,
                                            base[1] + u[1] * s_ + v[1] * t_,
                                            base[2] + u[2] * s_ + v[2] * t_}));
                if (affine) {
                    const Affine& A = *affine;
                    const Point2 &a = A.a, &b = A.b, &c = A.c, &ua = A.ua, &ub = A.ub, &uc = A.uc;
                    double l1 = ((s_ - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (t_ - a[1])) / A.det;
                    double l2 = ((b[0] - a[0]) * (t_ - a[1]) - (s_ - a[0]) * (b[1] - a[1])) / A.det;
                    piece_uv.push_back({ua[0] + l1 * (ub[0] - ua[0]) + l2 * (uc[0] - ua[0]),
                                        ua[1] + l1 * (ub[1] - ua[1]) + l2 * (uc[1] - ua[1])});
                }
            }
            if (R.flipped) {                                   // the face looked the other way: keep it so
                std::reverse(idx.begin(), idx.end());
                std::reverse(piece_uv.begin(), piece_uv.end());
            }
            new_F.push_back(std::move(idx));
            new_C.push_back(M.C[i]);
            new_UV.push_back(std::move(piece_uv));
        }
    }
    keep_faces(M, keep_idx);
    M.F.insert(M.F.end(), new_F.begin(), new_F.end());
    M.C.insert(M.C.end(), new_C.begin(), new_C.end());
    if (M.has_uv) {
        M.UV.insert(M.UV.end(), new_UV.begin(), new_UV.end());
    } else if (std::any_of(new_UV.begin(), new_UV.end(), [](const std::vector<Point2>& t) { return !t.empty(); })) {
        M.has_uv = true;                                       // (cannot happen: no texture, no affine map)
        M.UV.assign(M.F.size() - new_F.size(), {});
        M.UV.insert(M.UV.end(), new_UV.begin(), new_UV.end());
    }
    return scan.count;
}

}  // namespace detail

inline Mesh heal(const Mesh& M0, double tol) {
    using namespace detail;
    Mesh M = M0;
    if (M.F.empty() || M.V.empty()) return M;

    // A grid roughly one edge-length wide keeps the search local.
    double total = 0.0;
    long long count = 0;
    for (const Face& f : M.F) {
        size_t n = f.size();
        for (size_t i = 0; i < n; ++i) {
            total += norm(sub(M.V[f[i]], M.V[f[(i + 1) % n]]));
            count += 1;
        }
    }
    double cell = std::max(total / (double)std::max(1LL, count), tol * 10.0);

    std::unordered_map<CellKey, std::vector<int>, CellKeyHash> grid;
    for (size_t idx = 0; idx < M.V.size(); ++idx) {
        const Point& p = M.V[idx];
        CellKey key{cell_floor(p[0] / cell), cell_floor(p[1] / cell), cell_floor(p[2] / cell)};
        grid[key].push_back((int)idx);
    }
    auto add_cell = [&](std::vector<int>& out, const CellKey& key) {
        auto it = grid.find(key);
        if (it != grid.end()) out.insert(out.end(), it->second.begin(), it->second.end());
    };

    // Vertex indices in the grid cells the segment could pass through.
    auto nearby = [&](const Point& pa, const Point& pb) {
        long long lo[3], hi[3];
        for (int a = 0; a < 3; ++a) {
            lo[a] = cell_floor((std::min(pa[a], pb[a]) - tol) / cell);
            hi[a] = cell_floor((std::max(pa[a], pb[a]) + tol) / cell);
        }
        double spread = 1;                                     // (as a float: it cannot overflow)
        for (int a = 0; a < 3; ++a) spread *= (double)hi[a] - (double)lo[a] + 1.0;
        std::vector<int> out;
        if (spread <= 512) {                                   // short edge: sweep its box
            for (long long cx = lo[0]; cx <= hi[0]; ++cx)
                for (long long cy = lo[1]; cy <= hi[1]; ++cy)
                    for (long long cz = lo[2]; cz <= hi[2]; ++cz) add_cell(out, CellKey{cx, cy, cz});
            return out;
        }
        // Long edge: walk along it instead of filling its whole box.
        double length = norm(sub(pb, pa));
        double x = 3.0 * length / cell;
        if (!std::isfinite(x)) cell_floor(x);                   // (int() of a NaN or an infinity: an exception)
        long long steps = x < 4000.0 ? std::min<long long>(4000, (long long)x + 2) : 4000;
        std::unordered_set<CellKey, CellKeyHash> seen_cells;
        for (long long s = 0; s <= steps; ++s) {
            double t = (double)s / (double)steps;
            CellKey key{cell_floor((pa[0] + (pb[0] - pa[0]) * t) / cell),
                        cell_floor((pa[1] + (pb[1] - pa[1]) * t) / cell),
                        cell_floor((pa[2] + (pb[2] - pa[2]) * t) / cell)};
            if (!seen_cells.insert(key).second) continue;
            for (long long a = -1; a <= 1; ++a)
                for (long long b = -1; b <= 1; ++b)
                    for (long long c = -1; c <= 1; ++c) add_cell(out, CellKey{key.i + a, key.j + b, key.k + c});
        }
        return out;
    };

    std::vector<Face> newF;
    std::vector<std::vector<Point2>> newUV;                    // (used when the mesh has texture coordinates)
    for (size_t k = 0; k < M.F.size(); ++k) {
        const Face& f = M.F[k];
        size_t n = f.size();
        Face out;
        const std::vector<Point2>* uv = M.has_uv && !M.UV[k].empty() ? &M.UV[k] : nullptr;
        std::vector<Point2> out_uv;
        for (size_t i = 0; i < n; ++i) {
            int a = f[i], b = f[(i + 1) % n];
            out.push_back(a);
            if (uv) out_uv.push_back(uv->at(i));
            const Point& pa = M.V[a];
            const Point& pb = M.V[b];
            Point d = sub(pb, pa);
            double L2 = dot(d, d);
            if (L2 <= tol * tol) continue;
            std::vector<std::pair<double, int>> hits;
            for (int v : nearby(pa, pb)) {
                if (v == a || v == b) continue;
                const Point& pv = M.V[v];
                double t = ((pv[0] - pa[0]) * d[0] + (pv[1] - pa[1]) * d[1]
                            + (pv[2] - pa[2]) * d[2]) / L2;
                if (t <= 1e-9 || t >= 1.0 - 1e-9) continue;
                if (std::fabs(pa[0] + d[0] * t - pv[0]) <= tol
                        && std::fabs(pa[1] + d[1] * t - pv[1]) <= tol
                        && std::fabs(pa[2] + d[2] * t - pv[2]) <= tol)
                    hits.push_back({t, v});
            }
            if (!hits.empty()) {
                std::sort(hits.begin(), hits.end());           // (by t, then by vertex -- as Python sorts tuples)
                bool have_last = false;
                int last = 0;
                for (const auto& h : hits) {
                    double t = h.first;
                    int v = h.second;
                    if (!have_last || v != last) {
                        out.push_back(v);
                        if (uv) {
                            const Point2& ua = uv->at(i);
                            const Point2& ub = uv->at((i + 1) % n);
                            out_uv.push_back({ua[0] + (ub[0] - ua[0]) * t, ua[1] + (ub[1] - ua[1]) * t});
                        }
                    }
                    last = v;
                    have_last = true;
                }
            }
        }
        newF.push_back(std::move(out));
        if (M.has_uv) newUV.push_back(std::move(out_uv));
    }
    M.F = std::move(newF);
    if (M.has_uv) M.UV = std::move(newUV);
    return M;
}
inline Mesh heal() { return heal(scene()); }

inline int concave_faces(const Mesh& M) {
    int count = 0;
    for (const Face& f : M.F)
        if (f.size() > 3 && detail::is_concave(M, f)) count += 1;
    return count;
}
inline int concave_faces() { return concave_faces(scene()); }

inline int overlaps(const Mesh& M, double tol) { return detail::overlap_scan(M, tol, false).count; }
inline int overlaps() { return overlaps(scene()); }

inline Mesh triangulate(const Mesh& M) {
    Mesh out;
    out.V = M.V;
    for (size_t k = 0; k < M.F.size() && k < M.C.size(); ++k) {
        const Face& f = M.F[k];
        const Color& c = M.C[k];
        const std::vector<Point2>* uv = M.has_uv && !M.UV[k].empty() ? &M.UV[k] : nullptr;
        for (size_t t = 1; t + 1 < f.size(); ++t) {
            if (uv) out.add_face({f[0], f[t], f[t + 1]}, c, {uv->at(0), uv->at(t), uv->at(t + 1)});
            else out.add_face({f[0], f[t], f[t + 1]}, c);
        }
    }
    return out;
}
inline Mesh triangulate() { return triangulate(scene()); }

inline Mesh fix_normals(const Mesh& M0, bool outward) {
    Mesh M = M0;
    std::vector<int> rep = detail::weld_map(M.V);            // (corners lying on one another count as one)
    std::map<std::pair<int, int>, std::vector<int>> edge_faces;
    for (size_t i = 0; i < M.F.size(); ++i) {
        const Face& f = M.F[i];
        size_t n = f.size();
        for (size_t t = 0; t < n; ++t) {
            int a = rep[f[t]], b = rep[f[(t + 1) % n]];
            if (a != b) edge_faces[a < b ? std::make_pair(a, b) : std::make_pair(b, a)].push_back((int)i);
        }
    }

    std::vector<char> visited(M.F.size(), 0);
    for (size_t start = 0; start < M.F.size(); ++start) {
        if (visited[start]) continue;
        std::vector<int> component{(int)start};
        visited[start] = 1;
        std::vector<int> stack{(int)start};
        while (!stack.empty()) {
            int i = stack.back();
            stack.pop_back();
            const Face& f = M.F[i];                            // (only unvisited neighbours are turned round)
            size_t n = f.size();
            for (size_t t = 0; t < n; ++t) {
                int a = rep[f[t]], b = rep[f[(t + 1) % n]];
                if (a == b) continue;
                const std::vector<int>& around = edge_faces[a < b ? std::make_pair(a, b) : std::make_pair(b, a)];
                if (around.size() != 2) continue;              // (an open edge, or one of three faces or more)
                for (int j : around) {
                    if (visited[j]) continue;
                    Face& g = M.F[j];
                    size_t m = g.size();
                    bool same = false;
                    for (size_t s = 0; s < m; ++s)
                        if (rep[g[s]] == a && rep[g[(s + 1) % m]] == b) {
                            same = true;
                            break;
                        }
                    if (same) {                                // neighbour disagrees
                        std::reverse(g.begin(), g.end());
                        if (M.has_uv) std::reverse(M.UV[j].begin(), M.UV[j].end());
                    }
                    visited[j] = 1;
                    component.push_back(j);
                    stack.push_back(j);
                }
            }
        }
        if (outward) {
            std::pair<double, double> pv = detail::piece_volume(M, component, rep);
            if (pv.first < -1e-9 * pv.second) {
                for (int i : component) {
                    std::reverse(M.F[i].begin(), M.F[i].end());
                    if (M.has_uv) std::reverse(M.UV[i].begin(), M.UV[i].end());
                }
            }
        }
    }
    return M;
}
inline Mesh fix_normals() { return fix_normals(scene()); }

inline Mesh clean(const Mesh& M0, double tol, bool weld, bool degenerate, bool duplicates, bool internal, bool unused,
                  bool normals, CleanReport* report, bool overlaps, bool convex) {
    Mesh M = M0;
    CleanReport info;
    size_t n = M.V.size();
    info.faces_removed += detail::drop_not_finite(M);        // a vertex that is not a number cannot be mended
    info.vertices_removed += (int)(n - M.V.size());
    if (weld) info.vertices_removed += detail::weld(M, tol);
    if (degenerate) info.faces_removed += detail::drop_degenerate(M);
    if (internal) info.faces_removed += detail::drop_internal(M);
    if (duplicates) info.faces_removed += detail::dedup_faces(M);
    if (overlaps) {
        info.faces_cut += detail::cut_overlaps(M);
        if (info.faces_cut && weld) {
            detail::weld(M, tol);                              // the new corners meet their neighbours ...
            M = heal(M, tol);                                  // ... and the neighbours' long edges learn of them
            if (degenerate)                                    // a corner welded onto its neighbour can leave a face
                info.faces_removed += detail::drop_degenerate(M);   // visiting a vertex twice, or without area
            if (duplicates) info.faces_removed += detail::dedup_faces(M);
        }
    }
    if (convex) info.faces_split += detail::split_concave(M);
    if (normals) M = fix_normals(M);
    if (unused) info.vertices_removed += detail::drop_unused(M);
    if (report) *report = info;
    return M;
}
inline Mesh clean() { return clean(scene()); }

inline Stats stats(const Mesh& M) {
    Stats s;
    std::array<Point, 2> bb = bbox(M);
    const Point& lo = bb[0];
    const Point& hi = bb[1];
    std::map<std::pair<int, int>, int> edges;
    for (const Face& f : M.F) {
        size_t n = f.size();
        for (size_t t = 0; t < n; ++t) {
            int a = f[t], b = f[(t + 1) % n];
            edges[a < b ? std::make_pair(a, b) : std::make_pair(b, a)] += 1;
        }
    }
    int open_edges = 0, odd_edges = 0;
    for (const auto& edge : edges) {
        if (edge.second == 1) open_edges += 1;
        if (edge.second > 2) odd_edges += 1;
    }
    // vertices sitting on the same spot (add.py: a dict of rounded points, where
    // 0.0 and -0.0 are one key and a point with a NaN is always a key of its own)
    std::set<std::array<double, 3>> spots;
    size_t lone = 0;
    for (const Point& p : M.V) {
        std::array<double, 3> key = {detail::py_round(p[0], 6), detail::py_round(p[1], 6),
                                     detail::py_round(p[2], 6)};
        if (std::isnan(key[0]) || std::isnan(key[1]) || std::isnan(key[2])) lone += 1;
        else spots.insert(key);
    }
    int duplicate_vertices = (int)M.V.size() - (int)(spots.size() + lone);
    std::map<Face, std::vector<const Face*>> groups;
    for (const Face& f : M.F) {
        Face key = f;
        std::sort(key.begin(), key.end());
        groups[key].push_back(&f);
    }
    int duplicate_faces = 0, back_to_back = 0;
    for (const auto& g : groups) {
        const std::vector<const Face*>& same = g.second;
        if (same.size() < 2) continue;
        int forward = 0;
        for (const Face* f : same)
            if (detail::winding(*f)) forward += 1;
        int backward = (int)same.size() - forward;
        back_to_back += std::min(forward, backward);
        duplicate_faces += (int)same.size() - 1 - std::min(forward, backward);
    }
    s.vertices = (int)M.V.size();
    s.faces = (int)M.F.size();
    s.triangles = 0;
    for (const Face& f : M.F) s.triangles += std::max(0, (int)f.size() - 2);
    s.colors = (int)std::set<Color>(M.C.begin(), M.C.end()).size();
    s.bbox = {lo, hi};
    s.size = {hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]};
    s.area = area(M);
    s.volume = volume(M);
    s.open_edges = open_edges;
    s.non_manifold_edges = odd_edges;
    s.duplicate_vertices = duplicate_vertices;
    s.duplicate_faces = duplicate_faces;
    s.back_to_back_faces = back_to_back;
    s.closed = open_edges == 0;
    // add.py's obj_size writes every coordinate with _num, whose int(x) raises for
    // a NaN or an infinity: stats() of such a mesh is an error there, so it is here.
    for (const Point& p : M.V)
        for (int a = 0; a < 3; ++a)
            if (!std::isfinite(p[a])) detail::cell_floor(p[a]);    // (throws)
    s.obj_bytes = obj_size(M);
    s.transparent_faces = 0;
    for (const Color& c : M.C)
        if (c.alpha < 1.0) s.transparent_faces += 1;
    std::set<std::string> images;
    for (const Color& c : M.C)
        if (!c.image.empty()) images.insert(c.image);
    s.textures.assign(images.begin(), images.end());           // (sorted, as add.py's sorted(set(...)))
    return s;
}
inline Stats stats() { return stats(scene()); }

namespace detail {
inline std::string check_f(double x, int decimals) {
    if (std::isnan(x)) return "nan";
    return fmt("%.*f", decimals, x);
}
inline std::string check_d(double x) {
    if (!std::isfinite(x)) cell_floor(x);
    double w = std::trunc(x);
    if (w == 0) return "0";
    return fmt("%.0f", w);
}
}  // namespace detail

inline bool check(const Mesh& M, int min_faces, int min_colors, bool quiet, double max_mb, int max_colors) {
    using detail::fmt;
    Stats s = stats(M);
    double mb = (double)s.obj_bytes / 1e6;
    bool fits = mb <= max_mb && s.colors <= max_colors;
    bool ok = s.faces >= min_faces && s.colors >= min_colors && fits;
    if (!quiet) {
        auto mark = [](bool good) { return std::string(good ? "OK " : "!! "); };
        std::ostream& out = std::cout;
        out << std::string(56, '-') << "\n";
        out << fmt("  vertices            %d", s.vertices) << "\n";
        out << mark(s.faces >= min_faces) << fmt(" polygons            %d  (need %d)", s.faces, min_faces) << "\n";
        out << mark(min_colors <= s.colors && s.colors <= max_colors)
            << fmt(" colours             %d  (need %d, at most %d materials for Sketchfab)", s.colors, min_colors,
                   max_colors)
            << "\n";
        out << mark(mb <= max_mb) << " .obj file size      " << detail::check_f(mb, 1) << " MB  (at most "
            << detail::check_d(max_mb) << " MB for Sketchfab)\n";
        out << "   size                " << detail::check_f(s.size[0], 3) << " x " << detail::check_f(s.size[1], 3)
            << " x " << detail::check_f(s.size[2], 3) << "\n";
        out << "   surface area        " << detail::check_f(s.area, 3) << "\n";
        std::string why;
        if (s.closed) why = "yes";
        else why = fmt("no, %d edges have nothing on the other side", s.open_edges);
        out << mark(s.closed) << " closed surface      " << why << "\n";
        if (s.non_manifold_edges)
            out << fmt("   repeated edges      %d   (an edge shared by more than two faces:"
                       " parts meet along it; normal for voxel models)", s.non_manifold_edges) << "\n";
        if (s.duplicate_vertices)
            out << fmt("!! repeated vertices   %d   (two vertices on one spot -- add.clean() welds them)",
                       s.duplicate_vertices) << "\n";
        if (s.duplicate_faces)
            out << fmt("!! repeated faces      %d   -- add.clean() removes them", s.duplicate_faces) << "\n";
        if (s.back_to_back_faces)
            out << fmt("   back-to-back faces  %d   (fine for a two-sided sheet;"
                       " add.clean() removes them)", s.back_to_back_faces) << "\n";
        int flicker = overlaps(M);
        if (flicker)
            out << fmt("!! overlapping faces   %d   (lying on a bigger face in the same plane:"
                       " they flicker in a viewer -- add.clean() cuts them)", flicker) << "\n";
        int notched = concave_faces(M);
        if (notched)
            out << fmt("!! non-convex faces    %d   (a viewer draws a polygon as a fan and"
                       " covers its notch -- add.clean() cuts them into triangles)", notched) << "\n";
        if (s.closed) out << "   volume              " << detail::check_f(s.volume, 3) << "\n";
        if (s.transparent_faces)
            out << fmt("   see-through faces   %d   (opacity is kept in .obj + .mtl)", s.transparent_faces) << "\n";
        if (!s.textures.empty()) {
            std::string names;
            for (size_t i = 0; i < s.textures.size(); ++i) names += (i ? ", " : "") + s.textures[i];
            out << "   textures            " << names << "   (put the images next to the .obj)\n";
        }
        if (s.colors > max_colors)
            out << fmt("   hint: add.limit_colors(M, %d) or add.save(..., colors=%d)", max_colors, max_colors) << "\n";
        if (mb > max_mb)
            out << "   hint: fewer cells (a smaller k, grid or subdivisions)"
                   " make the file smaller\n";
        out << std::string(56, '-') << "\n";
    }
    return ok;
}
inline bool check() { return check(scene()); }

}  // namespace add

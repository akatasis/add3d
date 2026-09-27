// ============================================================================
//  15. Booleans: union, difference, intersection, cut
//      (add.py: _src/60_boolean.py)
// ============================================================================
// Two solids can be added together, cut out of one another, or intersected.
// The idea used here needs no library and fits on one screen:
//
//   1. Wherever the other model's triangles could cut one of ours, slice ours
//      along their planes.  After that every piece lies wholly inside or
//      wholly outside the other solid -- no piece straddles the boundary.
//   2. Ask of each piece: is it inside?  Shoot a ray from just above the
//      piece's middle and count how many times it crosses the other surface.
//      An odd count means inside.
//   3. Keep the pieces the operation asks for, and turn the borrowed ones
//      round when the operation says so:
//
//        union         keep A outside B  +  B outside A
//        intersection  keep A inside  B  +  B inside  A
//        difference    keep A outside B  +  B inside  A, reversed
//
// Two grids keep both steps local, so the work grows roughly with the number
// of faces rather than with its square.  Booleans want *closed* solids --
// add::check() will tell you whether yours is closed.
namespace add {

//: How far a point may be from a plane and still count as lying in it.
inline constexpr double BOOL_EPS = 1e-9;

namespace detail {

//: Where a point or a polygon lies with respect to a plane (add.py's _COPLANAR ... _SPANNING).
inline constexpr int COPLANAR = 0, FRONT = 1, BACK = 2, SPANNING = 3;

//: One planar polygon that remembers its plane and its colour (add.py's _Poly).
struct Poly {
    Points pts;
    Color c;
    Point n;                                   // the unit normal (0 for a polygon without area)
    double w = 0.0;                            // n . p for the points p of the plane
    //: The plane worked out from the corners (Newell's normal).
    Poly(Points pts_, const Color& c_);
    //: The plane given.
    Poly(Points pts_, const Color& c_, const Point& n_, double w_) : pts(std::move(pts_)), c(c_), n(n_), w(w_) {}
};

//: Cut ``poly`` with plane (pn, pw); a polygon lying in the plane or entirely on one side is filed whole.
inline void split(const Point& pn, double pw, const Poly& poly, std::vector<Poly>& front, std::vector<Poly>& back,
                  double eps = BOOL_EPS);
//: Python's ``min(q[a] for q in pts)`` / ``max(...)``: coordinate ``a`` (the first of equal values).
inline double coord_min(const Points& pts, int a);
inline double coord_max(const Points& pts, int a);

//: Python's ``int(math.floor(x))`` -- a grid cell number -- kept exactly as a whole-number double, so
//: that it never overflows (Python's integers have no limit either); an exception for a NaN or an
//: infinite ``x``, as in Python.
inline double floor_cell(double x);
//: The next whole number after ``i`` that a double can hold: i + 1 (beyond 2**53 the next double).
//: Python's ``range`` also visits the numbers in between, but no point ever falls into their cells.
inline double next_cell(double i);
//: A grid cell: (i, j, k) whole numbers (k = 0 for a 2D grid).
struct GridKey {
    double i, j, k;
    bool operator==(const GridKey& o) const { return i == o.i && j == o.j && k == o.k; }
};
struct GridKeyHash {
    size_t operator()(const GridKey& c) const;
};

//: A Python ``set`` of whole numbers 0, 1, 2 ... that goes through them in the order CPython's
//: own set does (its hash table, slot by slot) -- the order decides which plane cuts first.
class IntSet {
  public:
    IntSet() : table_(8, -1) {}
    //: Add a number (nothing happens when it is already there).
    void add(int key);
    //: The numbers, in the order a Python ``for`` loop over the set gives them.
    std::vector<int> items() const;

  private:
    std::vector<int> table_;                   // -1: an empty slot
    size_t mask_ = 7, fill_ = 0, used_ = 0;
    //: The slot where ``key`` is, or the free slot where it would go.
    size_t slot(int key) const;
    void resize(size_t minused);
};

//: Which triangles live near a given box -- a uniform 3D hash (add.py's _BoxGrid).  Triangles are
//: filed in every cell their bounding box touches; one that would fill more than MAX_CELLS cells
//: goes on the short "oversize" list that every query checks.
struct BoxGrid {
    static constexpr long long MAX_CELLS = 64;
    double cell = 0.0;
    std::unordered_map<GridKey, std::vector<int>, GridKeyHash> buckets;
    std::vector<int> oversize;
    std::vector<std::array<Point, 2>> boxes;
    BoxGrid(const std::vector<Poly>& polys, double diagonal);
    //: The cells of the box lo..hi, or nothing (add.py: None) when there are more than ``limit``.
    std::optional<std::vector<GridKey>> keys(const Point& lo, const Point& hi,
                                             std::optional<long long> limit = std::nullopt) const;
    //: Indices of triangles whose bounding box overlaps lo..hi (in add.py's order).
    std::vector<int> near(const Point& lo, const Point& hi) const;
};

//: Answers "is this point inside the solid?" by counting ray crossings (add.py's _RayIndex).
//: All rays travel in the same direction, so the triangles are bucketed once on the two axes
//: across that direction.
struct RayIndex {
    Point d, e1, e2;
    double cell = 0.0;
    std::unordered_map<GridKey, std::vector<int>, GridKeyHash> buckets;
    std::vector<std::array<Point, 3>> tris;
    RayIndex(const std::vector<Poly>& polys, const Point& direction);
    //: true / false, or nothing (add.py: None) when the ray grazes an edge.
    std::optional<bool> inside(const Point& p) const;
};

//: Three awkward directions; if one ray grazes an edge the next one is tried.
inline const std::array<Point, 3> RAY_DIRECTIONS = {Point{0.5773502691896258, 0.5773502691896257, 0.5773502691896256},
                                                    Point{0.2672612419124244, -0.5345224838248488, 0.8017837257372732},
                                                    Point{-0.7071067811865475, 0.408248290463863, 0.5773502691896258}};

//: A plane that may cut a polygon: its id -- (triangle, 0) for the triangle's own plane,
//: (triangle, k + 1) for the plane standing on its edge k -- its normal and its offset.
struct CutPlane {
    std::pair<int, int> pid;
    Point n;
    double w;
};

//: A mesh prepared for boolean work: triangles, a box grid and ray indexes (add.py's _Solid).
struct Solid {
    std::vector<Poly> polys;
    std::optional<BoxGrid> grid;               // (add.py: None for a mesh without triangles)
    std::vector<RayIndex> rays;
    Point lo, hi;
    double scale = 0.0;
    explicit Solid(const Mesh& M);
    //: The ray index of direction ``which``, built the first time it is needed.
    const RayIndex& ray_index(size_t which);
    //: Is point ``p`` inside this solid?
    bool contains(const Point& p);
    //: Planes to cut ``poly`` with, and the triangles it may lie on (flush with it).
    std::pair<std::vector<CutPlane>, std::vector<int>> cutters(const Poly& poly) const;
    //: Does ``point`` sit on one of the ``flush`` triangles?  +1 when the triangle faces the same
    //: way as ``plane_normal``, -1 when the other way, nothing (add.py: None) when on none of them.
    std::optional<int> facing_at(const Point& point, const Point& plane_normal, const std::vector<int>& flush) const;
};

//: A piece of a face, cut until it cannot straddle the other solid, with the triangles it lies
//: flush on.  (``bare``: add.py gave up on a pathological face and returned the bare piece, which
//: its caller cannot unpack -- an error there, so here.)
struct FlushPiece {
    Poly piece;
    std::vector<int> flush;
    bool bare = false;
};
//: Chop ``poly`` until no piece can straddle ``other``'s surface.
inline std::vector<FlushPiece> split_against(const Poly& poly, const Solid& other);
//: Which pieces an operation keeps: a set drawn from "in", "out", "same" and "opp".
using KeepSet = std::set<std::string>;
//: Cut ``source``'s faces against ``other`` and keep the wanted pieces (turned round with ``flip``,
//: painted ``paint`` when it is given).
inline std::vector<Poly> keep_pieces(const Solid& source, Solid& other, const KeepSet& keep, bool flip,
                                     std::optional<Color> paint = std::nullopt);
//: Mesh -> list of triangles (so no face can be twisted or non-planar).
inline std::vector<Poly> to_polys(const Mesh& M);
//: List of polygons -> Mesh, welded and with its T-junctions closed.
inline Mesh from_polys(const std::vector<Poly>& polys, bool tidy = true);
//: True when two meshes cannot possibly touch.
inline bool boxes_apart(const Mesh& A, const Mesh& B, double slack = 1e-9);
//: What an operation keeps of A and of B, and whether B's pieces are turned round.
struct BoolRule {
    KeepSet keep_a, keep_b;
    bool flip_b;
};
//: Which pieces each operation keeps ("union", "intersection", "difference").  A gets the shared
//: surface so that a patch where the two solids are flush is kept exactly once.
inline const std::map<std::string, BoolRule>& RULES();
//: The three boolean operations, all from the same two half-steps.
inline Mesh csg(const Mesh& A, const Mesh& B, const std::string& op, std::optional<Color> paint = std::nullopt);
//: Chain a bag of (a, b) segments into closed rings of points.
inline std::vector<Points> loops(const std::vector<std::pair<Point, Point>>& edges);

}  // namespace detail

//: Fuse solids into one, removing everything hidden inside.  (``union`` is a
//: C++ keyword: the function is called union_; add_solids is the same.)
inline Mesh union_(const std::vector<Mesh>& meshes);
inline Mesh union_(const Mesh& A, const Mesh& B);
//: Cut the other solids out of A (``paint``: the colour of the cut surfaces, else each keeps its cutter's).
inline Mesh difference(const Mesh& A, const std::vector<Mesh>& others, std::optional<Color> paint = std::nullopt);
inline Mesh difference(const Mesh& A, const Mesh& B, std::optional<Color> paint = std::nullopt);
//: Keep only the space that all the solids have in common.
inline Mesh intersect(const std::vector<Mesh>& meshes);
inline Mesh intersect(const Mesh& A, const Mesh& B);
//: Everything that is in one solid or the other but not in both.
inline Mesh symmetric_difference(const Mesh& A, const Mesh& B);
//: Aliases: add_solids = union_, subtract = difference, common = intersect.
inline Mesh add_solids(const std::vector<Mesh>& meshes);
inline Mesh add_solids(const Mesh& A, const Mesh& B);
inline Mesh subtract(const Mesh& A, const std::vector<Mesh>& others);
inline Mesh subtract(const Mesh& A, const Mesh& B);
inline Mesh common(const std::vector<Mesh>& meshes);
inline Mesh common(const Mesh& A, const Mesh& B);
//: Slice a solid with an infinite plane and keep the part behind it (``cap`` closes the cut).
inline Mesh cut(const Mesh& M, const Point& point = {0, 0, 0}, const Point& normal = {0, 1, 0}, bool cap = true,
                std::optional<Color> color = std::nullopt);
//: Is point p inside the (closed) mesh?  (A list of points gives a list of answers, and is far
//: faster than asking one point at a time.  As in add.py, an empty list is an error.)
inline bool inside(const Mesh& M, const Point& p);
inline std::vector<bool> inside(const Mesh& M, const Points& ps);

}  // namespace add
//@@definitions
namespace add {

namespace detail {

inline Poly::Poly(Points pts_, const Color& c_) : pts(std::move(pts_)), c(c_) {
    double nx = 0.0, ny = 0.0, nz = 0.0;
    size_t m = pts.size();
    for (size_t i = 0; i < m; ++i) {
        const Point& a = pts[i];
        const Point& b = pts[(i + 1) % m];
        nx += (a[1] - b[1]) * (a[2] + b[2]);
        ny += (a[2] - b[2]) * (a[0] + b[0]);
        nz += (a[0] - b[0]) * (a[1] + b[1]);
    }
    n = unit({nx, ny, nz});
    if (pts.empty()) throw std::out_of_range("list index out of range");   // (add.py: pts[0] of no points)
    w = dot(n, pts[0]);
}

inline void split(const Point& pn, double pw, const Poly& poly, std::vector<Poly>& front, std::vector<Poly>& back,
                  double eps) {
    std::vector<int> types;
    int poly_type = 0;
    for (const Point& p : poly.pts) {
        double t = pn[0] * p[0] + pn[1] * p[1] + pn[2] * p[2] - pw;
        int kind = t < -eps ? BACK : (t > eps ? FRONT : COPLANAR);
        poly_type |= kind;
        types.push_back(kind);
    }

    if (poly_type != SPANNING) {
        (poly_type == BACK ? back : front).push_back(poly);
        return;
    }
    Points f, b;
    size_t m = poly.pts.size();
    for (size_t i = 0; i < m; ++i) {
        size_t j = (i + 1) % m;
        int ti = types[i], tj = types[j];
        const Point& vi = poly.pts[i];
        const Point& vj = poly.pts[j];
        if (ti != BACK) f.push_back(vi);
        if (ti != FRONT) b.push_back(vi);
        if ((ti | tj) == SPANNING) {
            double di = pn[0] * vi[0] + pn[1] * vi[1] + pn[2] * vi[2] - pw;
            double dj = pn[0] * vj[0] + pn[1] * vj[1] + pn[2] * vj[2] - pw;
            double t = di / (di - dj);
            Point cut = {vi[0] + (vj[0] - vi[0]) * t,
                         vi[1] + (vj[1] - vi[1]) * t,
                         vi[2] + (vj[2] - vi[2]) * t};
            f.push_back(cut);
            b.push_back(cut);
        }
    }
    if (f.size() >= 3) front.push_back(Poly(f, poly.c, poly.n, poly.w));
    if (b.size() >= 3) back.push_back(Poly(b, poly.c, poly.n, poly.w));
}

// ---------------------------------------------------------------------------
//  Two little indexes that keep the search local
// ---------------------------------------------------------------------------

inline double floor_cell(double x) {
    if (std::isnan(x)) throw std::invalid_argument("cannot convert float NaN to integer");
    if (std::isinf(x)) throw std::overflow_error("cannot convert float infinity to integer");
    return std::floor(x) + 0.0;                                // (a whole number: never -0.0)
}

inline double next_cell(double i) {
    return std::fabs(i) < 9007199254740992.0 ? i + 1.0 : std::nextafter(i, inf);
}

inline size_t GridKeyHash::operator()(const GridKey& c) const {
    std::hash<double> h;
    size_t s = h(c.i);
    s ^= h(c.j) + 0x9E3779B97F4A7C15ull + (s << 6) + (s >> 2);
    s ^= h(c.k) + 0x9E3779B97F4A7C15ull + (s << 6) + (s >> 2);
    return s;
}

// CPython's set of ints (hash(i) = i) is an open-addressing table of 8 slots to start with.  A key
// is looked for in slot hash & mask and the 9 slots after it (LINEAR_PROBES, when they are inside
// the table), then further on: perturb >>= 5, i = (i * 5 + 1 + perturb) & mask.  The table grows
// once it is 3/5 full: to the power of two above used * 4 (used * 2 past 50000 keys), the keys
// going in again in the order of their old slots.
inline size_t IntSet::slot(int key) const {
    size_t i = (size_t)key & mask_;
    size_t perturb = (size_t)key;
    while (true) {
        size_t last = i + 9 <= mask_ ? i + 9 : i;
        for (size_t e = i; e <= last; ++e)
            if (table_[e] < 0 || table_[e] == key) return e;
        perturb >>= 5;
        i = (i * 5 + 1 + perturb) & mask_;
    }
}

inline void IntSet::add(int key) {
    size_t e = slot(key);
    if (table_[e] == key) return;                              // already there
    table_[e] = key;
    fill_ += 1;
    used_ += 1;
    if (fill_ * 5 >= mask_ * 3) resize(used_ > 50000 ? used_ * 2 : used_ * 4);
}

inline void IntSet::resize(size_t minused) {
    size_t newsize = 8;
    while (newsize <= minused) newsize <<= 1;
    std::vector<int> old = std::move(table_);
    table_.assign(newsize, -1);
    mask_ = newsize - 1;
    for (int key : old)
        if (key >= 0) table_[slot(key)] = key;
    fill_ = used_;
}

inline std::vector<int> IntSet::items() const {
    std::vector<int> out;
    for (int key : table_)
        if (key >= 0) out.push_back(key);
    return out;
}

inline double coord_min(const Points& pts, int a) {
    if (pts.empty()) throw std::invalid_argument("min() arg is an empty sequence");
    double m = pts[0][a];
    for (const Point& q : pts)
        if (q[a] < m) m = q[a];
    return m;
}
inline double coord_max(const Points& pts, int a) {
    if (pts.empty()) throw std::invalid_argument("max() arg is an empty sequence");
    double m = pts[0][a];
    for (const Point& q : pts)
        if (q[a] > m) m = q[a];
    return m;
}

inline BoxGrid::BoxGrid(const std::vector<Poly>& polys, double diagonal) {
    cell = std::max(diagonal / 32.0, 1e-9);
    for (size_t i = 0; i < polys.size(); ++i) {
        const Poly& p = polys[i];
        Point lo{coord_min(p.pts, 0), coord_min(p.pts, 1), coord_min(p.pts, 2)};
        Point hi{coord_max(p.pts, 0), coord_max(p.pts, 1), coord_max(p.pts, 2)};
        boxes.push_back({lo, hi});
        std::optional<std::vector<GridKey>> ks = keys(lo, hi, MAX_CELLS);
        if (!ks) {
            oversize.push_back((int)i);
        } else {
            for (const GridKey& key : *ks) buckets[key].push_back((int)i);
        }
    }
}

inline std::optional<std::vector<GridKey>> BoxGrid::keys(const Point& lo, const Point& hi,
                                                        std::optional<long long> limit) const {
    double c = cell;
    std::array<std::pair<double, double>, 3> r;
    double total = 1;                                          // (a double: exact while it is small, and
    for (int a = 0; a < 3; ++a) {                              // it cannot overflow)
        double first = floor_cell(lo[a] / c);
        double last = floor_cell(hi[a] / c);
        r[a] = {first, last};
        total *= last - first + 1;
        if (limit && total > (double)*limit) return std::nullopt;
    }
    std::vector<GridKey> out;
    for (double i = r[0].first; i <= r[0].second; i = next_cell(i))
        for (double j = r[1].first; j <= r[1].second; j = next_cell(j))
            for (double k = r[2].first; k <= r[2].second; k = next_cell(k)) out.push_back({i, j, k});
    return out;
}

inline std::vector<int> BoxGrid::near(const Point& lo, const Point& hi) const {
    std::optional<std::vector<GridKey>> ks = keys(lo, hi, 4096);
    std::vector<int> candidates;
    if (!ks) {
        for (size_t i = 0; i < boxes.size(); ++i) candidates.push_back((int)i);
    } else {
        IntSet seen;                                           // (add.py: a set -- its order matters)
        for (int i : oversize) seen.add(i);
        for (const GridKey& key : *ks) {
            auto it = buckets.find(key);
            if (it == buckets.end()) continue;
            for (int i : it->second) seen.add(i);
        }
        candidates = seen.items();
    }
    std::vector<int> out;
    for (int i : candidates) {
        const Point& blo = boxes[i][0];
        const Point& bhi = boxes[i][1];
        if (bhi[0] < lo[0] - 1e-9 || blo[0] > hi[0] + 1e-9
                || bhi[1] < lo[1] - 1e-9 || blo[1] > hi[1] + 1e-9
                || bhi[2] < lo[2] - 1e-9 || blo[2] > hi[2] + 1e-9)
            continue;
        out.push_back(i);
    }
    return out;
}

inline RayIndex::RayIndex(const std::vector<Poly>& polys, const Point& direction) {
    d = unit(direction);
    e1 = perp(d);
    e2 = cross(d, e1);
    for (const Poly& p : polys)
        for (size_t t = 1; t + 1 < p.pts.size(); ++t) tris.push_back({p.pts[0], p.pts[t], p.pts[t + 1]});
    double span = 0.0;
    std::vector<std::array<double, 4>> flat;                   // (lo u, lo v, hi u, hi v) of each triangle
    for (const std::array<Point, 3>& tri : tris) {
        double uv[3][2];
        for (int q = 0; q < 3; ++q) {
            uv[q][0] = dot(tri[q], e1);
            uv[q][1] = dot(tri[q], e2);
        }
        double lo0 = uv[0][0], lo1 = uv[0][1], hi0 = uv[0][0], hi1 = uv[0][1];
        for (int q = 0; q < 3; ++q) {                          // (Python's min / max: the first of equals)
            if (uv[q][0] < lo0) lo0 = uv[q][0];
            if (uv[q][1] < lo1) lo1 = uv[q][1];
            if (uv[q][0] > hi0) hi0 = uv[q][0];
            if (uv[q][1] > hi1) hi1 = uv[q][1];
        }
        flat.push_back({lo0, lo1, hi0, hi1});
        double m = span;                                       // max(span, hi[0] - lo[0], hi[1] - lo[1])
        if (hi0 - lo0 > m) m = hi0 - lo0;
        if (hi1 - lo1 > m) m = hi1 - lo1;
        span = m;
    }
    cell = std::max(span, 1e-9);
    for (size_t i = 0; i < flat.size(); ++i) {
        const std::array<double, 4>& f = flat[i];              // (lo u, lo v, hi u, hi v)
        double a_first = floor_cell(f[0] / cell), a_last = floor_cell(f[2] / cell);
        for (double a = a_first; a <= a_last; a = next_cell(a)) {
            double b_first = floor_cell(f[1] / cell), b_last = floor_cell(f[3] / cell);
            for (double b = b_first; b <= b_last; b = next_cell(b)) buckets[GridKey{a, b, 0.0}].push_back((int)i);
        }
    }
}

inline std::optional<bool> RayIndex::inside(const Point& p) const {
    double ka = floor_cell(dot(p, e1) / cell);
    double kb = floor_cell(dot(p, e2) / cell);
    int hits = 0;
    auto it = buckets.find(GridKey{ka, kb, 0.0});
    if (it != buckets.end()) {
        for (int i : it->second) {
            const Point& a = tris[i][0];
            const Point& b = tris[i][1];
            const Point& c = tris[i][2];
            Point e1v = sub(b, a), e2v = sub(c, a);
            Point h = cross(d, e2v);
            double det = dot(e1v, h);
            if (std::fabs(det) < 1e-14) continue;
            double inv = 1.0 / det;
            Point s = sub(p, a);
            double u = dot(s, h) * inv;
            if (u < -1e-9 || u > 1.0 + 1e-9) continue;
            Point q = cross(s, e1v);
            double v = dot(d, q) * inv;
            if (v < -1e-9 || u + v > 1.0 + 1e-9) continue;
            double t = dot(e2v, q) * inv;
            if (t < 1e-12) continue;
            // Too close to an edge, a corner or the start of the ray to trust.
            if (std::fabs(u) < 1e-9 || std::fabs(v) < 1e-9 || std::fabs(u + v - 1.0) < 1e-9 || t < 1e-9)
                return std::nullopt;
            hits += 1;
        }
    }
    return hits % 2 == 1;
}

inline Solid::Solid(const Mesh& M) {
    polys = to_polys(M);
    if (!polys.empty()) {
        lo = hi = polys[0].pts[0];
        for (int a = 0; a < 3; ++a)                            // (Python's min / max: the first of equals)
            for (const Poly& q : polys)
                for (const Point& p : q.pts) {
                    if (p[a] < lo[a]) lo[a] = p[a];
                    if (p[a] > hi[a]) hi[a] = p[a];
                }
    } else {
        lo = {0.0, 0.0, 0.0};
        hi = {0.0, 0.0, 0.0};
    }
    double widest = hi[0] - lo[0];
    for (int a = 1; a < 3; ++a)
        if (hi[a] - lo[a] > widest) widest = hi[a] - lo[a];
    scale = std::max(1e-9, widest);
    double total = 0.0;                                        // (add.py's _total: in order, from 0)
    for (int a = 0; a < 3; ++a) {
        double squared = py_pow(hi[a] - lo[a], 2);
        if (std::isinf(squared) && std::isfinite(hi[a] - lo[a]))   // (Python's ** raises when it overflows)
            throw std::overflow_error("(34, 'Numerical result out of range')");
        total = total + squared;
    }
    double diagonal = std::sqrt(total);
    if (!polys.empty()) grid.emplace(polys, std::max(diagonal, 1e-9));
}

inline const RayIndex& Solid::ray_index(size_t which) {
    while (rays.size() <= which) rays.emplace_back(polys, RAY_DIRECTIONS[rays.size()]);
    return rays[which];
}

inline bool Solid::contains(const Point& p) {
    for (size_t which = 0; which < RAY_DIRECTIONS.size(); ++which) {
        std::optional<bool> answer = ray_index(which).inside(p);
        if (answer) return *answer;
    }
    return false;
}

// Normally a nearby triangle contributes its own plane.  A triangle lying in the *same* plane as
// ``poly`` would not cut it at all, yet the two faces may still overlap -- think of two boxes whose
// tops are flush.  For those, the three planes standing on the triangle's edges are used instead,
// which carves the shared patch out cleanly.
inline std::pair<std::vector<CutPlane>, std::vector<int>> Solid::cutters(const Poly& poly) const {
    Point plo{coord_min(poly.pts, 0), coord_min(poly.pts, 1), coord_min(poly.pts, 2)};
    Point phi{coord_max(poly.pts, 0), coord_max(poly.pts, 1), coord_max(poly.pts, 2)};
    std::vector<CutPlane> planes;
    std::vector<int> flush;
    if (!grid) throw std::runtime_error("'NoneType' object has no attribute 'near'");   // (as add.py: no triangles)
    for (int i : grid->near(plo, phi)) {
        const Poly& t = polys[i];
        if (std::fabs(std::fabs(dot(t.n, poly.n)) - 1.0) < 1e-9 && std::fabs(dot(t.n, poly.pts[0]) - t.w) < 1e-9) {
            flush.push_back(i);
            for (int k = 0; k < 3; ++k) {                      // the triangle's edge planes
                const Point& p = t.pts[k];
                const Point& q = t.pts[(k + 1) % 3];
                Point side = cross(t.n, sub(q, p));
                if (norm(side) > 1e-12) {
                    side = unit(side);
                    planes.push_back({{i, k + 1}, side, dot(side, p)});
                }
            }
        } else {
            planes.push_back({{i, 0}, t.n, t.w});
        }
    }
    return {planes, flush};
}

inline std::optional<int> Solid::facing_at(const Point& point, const Point& plane_normal,
                                           const std::vector<int>& flush) const {
    for (int i : flush) {
        const Poly& t = polys[i];
        bool on = true;
        for (int k = 0; k < 3; ++k) {
            const Point& p = t.pts[k];
            const Point& q = t.pts[(k + 1) % 3];
            Point side = cross(t.n, sub(q, p));
            if (dot(side, sub(point, p)) < -1e-12 * std::max(1.0, norm(side))) {
                on = false;
                break;
            }
        }
        if (on) return dot(t.n, plane_normal) > 0 ? 1 : -1;
    }
    return std::nullopt;
}

// Pieces are cut one at a time and the search is redone for each new piece, so a face far from
// the action stops being cut as soon as it moves out of the way -- which is what keeps a drilled
// plate from shattering into thousands of slivers.
inline std::vector<FlushPiece> split_against(const Poly& poly, const Solid& other) {
    using Done = std::set<std::pair<int, int>>;                // (add.py: a frozenset of plane ids)
    std::vector<FlushPiece> done_pieces;
    std::vector<std::pair<Poly, Done>> work;
    work.push_back({poly, Done()});
    int guard = 0;
    while (!work.empty()) {
        Poly piece = std::move(work.back().first);
        Done done = std::move(work.back().second);
        work.pop_back();
        guard += 1;
        if (guard > 20000) {                                   // pathological input; stop
            done_pieces.push_back({piece, {}, true});
            continue;
        }
        std::pair<std::vector<CutPlane>, std::vector<int>> found = other.cutters(piece);
        const std::vector<CutPlane>& planes = found.first;
        const std::vector<int>& flush = found.second;
        const CutPlane* chosen = nullptr;
        for (const CutPlane& plane : planes) {
            if (done.count(plane.pid)) continue;
            const Point& pn = plane.n;
            double pw = plane.w;
            bool front = false, back = false;
            for (const Point& p : piece.pts) {
                double t = pn[0] * p[0] + pn[1] * p[1] + pn[2] * p[2] - pw;
                if (t > BOOL_EPS) front = true;
                else if (t < -BOOL_EPS) back = true;
            }
            if (front && back) {
                chosen = &plane;
                break;
            }
            done.insert(plane.pid);                            // this plane can never cut it
        }
        if (!chosen) {
            done_pieces.push_back({piece, flush, false});
            continue;
        }
        std::vector<Poly> f, b;
        split(chosen->n, chosen->w, piece, f, b);
        Done rest = done;
        rest.insert(chosen->pid);
        for (Poly& part : f) work.push_back({std::move(part), rest});
        for (Poly& part : b) work.push_back({std::move(part), rest});
    }
    return done_pieces;
}

// ``keep`` is a set drawn from "in", "out", "same" and "opp": whether a piece ends up inside the
// other solid, outside it, or lying on its surface facing the same or the opposite way.
inline std::vector<Poly> keep_pieces(const Solid& source, Solid& other, const KeepSet& keep, bool flip,
                                     std::optional<Color> paint) {
    std::vector<Poly> out;
    if (!other.grid) return out;
    for (const Poly& poly : source.polys) {
        // Wholly outside the other model's box: no cutting, no doubt.
        bool apart = false;
        for (int a = 0; a < 3 && !apart; ++a)
            apart = coord_max(poly.pts, a) < other.lo[a] - 1e-9 || coord_min(poly.pts, a) > other.hi[a] + 1e-9;
        if (apart) {
            if (keep.count("out")) out.push_back(poly);
            continue;
        }
        for (const FlushPiece& found : split_against(poly, other)) {
            if (found.bare) throw std::runtime_error("cannot unpack non-iterable _Poly object");   // (as add.py)
            const Poly& piece = found.piece;
            const std::vector<int>& flush = found.flush;
            size_t n = piece.pts.size();
            double sx = 0.0, sy = 0.0, sz = 0.0;               // (add.py's _total: in order, from 0)
            for (const Point& q : piece.pts) sx = sx + q[0];
            for (const Point& q : piece.pts) sy = sy + q[1];
            for (const Point& q : piece.pts) sz = sz + q[2];
            Point centre = {sx / (double)n, sy / (double)n, sz / (double)n};
            std::optional<int> facing = !flush.empty() ? other.facing_at(centre, piece.n, flush) : std::nullopt;
            std::string state;
            if (facing) state = *facing > 0 ? "same" : "opp";
            else state = other.contains(centre) ? "in" : "out";
            if (!keep.count(state)) continue;
            Color c = paint ? *paint : piece.c;
            if (flip) {
                out.push_back(Poly(Points(piece.pts.rbegin(), piece.pts.rend()), c,
                                   {-piece.n[0], -piece.n[1], -piece.n[2]}, -piece.w));
            } else {
                out.push_back(Poly(piece.pts, c, piece.n, piece.w));
            }
        }
    }
    return out;
}

inline std::vector<Poly> to_polys(const Mesh& M) {
    std::vector<Poly> polys;
    for (size_t k = 0; k < M.F.size() && k < M.C.size(); ++k) {
        const Face& f = M.F[k];
        const Color& c = M.C[k];
        if (f.size() < 3) continue;
        Points pts;
        for (int i : f) pts.push_back(M.V[i]);
        for (size_t t = 1; t + 1 < pts.size(); ++t) {
            Poly p({pts[0], pts[t], pts[t + 1]}, c);
            if (norm(p.n) > 0.5) polys.push_back(std::move(p));   // skip degenerate slivers
        }
    }
    return polys;
}

inline Mesh from_polys(const std::vector<Poly>& polys, bool tidy) {
    Mesh M;
    for (const Poly& p : polys) M.add_polygon(p.pts, p.c);
    if (tidy) {
        detail::weld(M, 1e-7);
        detail::drop_degenerate(M);
        detail::dedup_faces(M);
        M = heal(M, 1e-7);
        detail::drop_degenerate(M);
        detail::drop_unused(M);
    }
    return M;
}

inline bool boxes_apart(const Mesh& A, const Mesh& B, double slack) {
    std::array<Point, 2> ba = bbox(A);
    std::array<Point, 2> bb = bbox(B);
    const Point& la = ba[0];
    const Point& ha = ba[1];
    const Point& lb = bb[0];
    const Point& hb = bb[1];
    for (int a = 0; a < 3; ++a)
        if (ha[a] < lb[a] - slack || hb[a] < la[a] - slack) return true;
    return false;
}

inline const std::map<std::string, BoolRule>& RULES() {
    static const std::map<std::string, BoolRule> rules = {
        {"union", {{"out", "same"}, {"out"}, false}},
        {"intersection", {{"in", "same"}, {"in"}, false}},
        {"difference", {{"out", "opp"}, {"in"}, true}},
    };
    return rules;
}

inline Mesh csg(const Mesh& A, const Mesh& B, const std::string& op, std::optional<Color> paint) {
    auto rule = RULES().find(op);
    if (rule == RULES().end()) throw std::invalid_argument("unknown boolean operation: '" + op + "'");
    const KeepSet& keep_a = rule->second.keep_a;
    const KeepSet& keep_b = rule->second.keep_b;
    bool flip_b = rule->second.flip_b;
    Solid a(A);
    Solid b(B);
    std::vector<Poly> polys = keep_pieces(a, b, keep_a, false);
    std::vector<Poly> more = keep_pieces(b, a, keep_b, flip_b, paint);
    polys.insert(polys.end(), more.begin(), more.end());
    return from_polys(polys);
}

inline std::vector<Points> loops(const std::vector<std::pair<Point, Point>>& edges) {
    using Key = std::array<double, 3>;
    auto key = [](const Point& p) { return Key{py_round(p[0], 7), py_round(p[1], 7), py_round(p[2], 7)}; };

    // add.py's dicts: ``nxt`` keeps its keys in the order they first came; in ``coords`` the last
    // point given for a key wins.  (Keys compare as Python's do: 0.0 and -0.0 are one key.)
    std::vector<std::pair<Key, std::vector<Key>>> nxt;
    std::map<Key, size_t> nxt_at;
    std::map<Key, Point> coords;
    for (const std::pair<Point, Point>& edge : edges) {
        const Point& a = edge.first;
        const Point& b = edge.second;
        Key ka = key(a);
        auto it = nxt_at.find(ka);
        if (it == nxt_at.end()) {
            it = nxt_at.emplace(ka, nxt.size()).first;
            nxt.push_back({ka, {}});
        }
        nxt[it->second].second.push_back(key(b));
        coords[key(a)] = a;
        coords[key(b)] = b;
    }
    std::vector<Points> out;
    std::set<Key> used;
    for (const auto& entry : nxt) {
        const Key& start = entry.first;
        if (used.count(start)) continue;
        Points loop;
        Key cur = start;
        while (nxt_at.count(cur) && !used.count(cur)) {
            used.insert(cur);
            loop.push_back(coords.at(cur));
            std::vector<Key> options;
            for (const Key& k : nxt[nxt_at.at(cur)].second)
                if (!used.count(k)) options.push_back(k);
            if (options.empty()) break;
            cur = options[0];
        }
        if (loop.size() >= 3) out.push_back(loop);
    }
    return out;
}

}  // namespace detail

inline Mesh union_(const std::vector<Mesh>& meshes) {
    if (meshes.empty()) return Mesh();
    Mesh out = meshes[0];
    for (size_t k = 1; k < meshes.size(); ++k) {
        const Mesh& other = meshes[k];
        if (other.F.empty()) continue;
        if (out.F.empty()) out = other;
        else if (detail::boxes_apart(out, other)) out = merge({out, other});   // nothing to cut: just stack
        else out = detail::csg(out, other, "union");
    }
    return out;
}
inline Mesh union_(const Mesh& A, const Mesh& B) { return union_(std::vector<Mesh>{A, B}); }

inline Mesh difference(const Mesh& A, const std::vector<Mesh>& others, std::optional<Color> paint) {
    Mesh out = A;
    for (const Mesh& other : others) {
        if (other.F.empty() || out.F.empty() || detail::boxes_apart(out, other)) continue;
        out = detail::csg(out, other, "difference", paint);
    }
    return out;
}
inline Mesh difference(const Mesh& A, const Mesh& B, std::optional<Color> paint) {
    return difference(A, std::vector<Mesh>{B}, paint);
}

inline Mesh intersect(const std::vector<Mesh>& meshes) {
    if (meshes.empty()) return Mesh();
    Mesh out = meshes[0];
    for (size_t k = 1; k < meshes.size(); ++k) {
        const Mesh& other = meshes[k];
        if (out.F.empty() || other.F.empty() || detail::boxes_apart(out, other)) return Mesh();
        out = detail::csg(out, other, "intersection");
    }
    return out;
}
inline Mesh intersect(const Mesh& A, const Mesh& B) { return intersect(std::vector<Mesh>{A, B}); }

inline Mesh symmetric_difference(const Mesh& A, const Mesh& B) {
    Mesh a_only = difference(A, B);
    Mesh b_only = difference(B, A);
    return union_(a_only, b_only);
}

inline Mesh add_solids(const std::vector<Mesh>& meshes) { return union_(meshes); }
inline Mesh add_solids(const Mesh& A, const Mesh& B) { return union_(A, B); }
inline Mesh subtract(const Mesh& A, const std::vector<Mesh>& others) { return difference(A, others); }
inline Mesh subtract(const Mesh& A, const Mesh& B) { return difference(A, B); }
inline Mesh common(const std::vector<Mesh>& meshes) { return intersect(meshes); }
inline Mesh common(const Mesh& A, const Mesh& B) { return intersect(A, B); }

// ---------------------------------------------------------------------------
//  Cheap relatives of the boolean operations
// ---------------------------------------------------------------------------

// "Behind" means the side the normal points away from, so cut(M, {0, 0, 0}, {0, 1, 0}) keeps the
// bottom half and throws the top away.  Cut twice with opposite normals to keep a slab.  Far
// cheaper than a full boolean, because a plane needs no searching.  With cap = true the exposed
// cross-section is closed with a new flat face, so the result stays watertight.
inline Mesh cut(const Mesh& M, const Point& point, const Point& normal, bool cap, std::optional<Color> color) {
    using namespace detail;
    Point n = unit(normal);
    double w = dot(n, point);
    Mesh out;
    std::vector<std::pair<Point, Point>> rim;
    for (size_t k = 0; k < M.F.size() && k < M.C.size(); ++k) {
        Points pts;
        for (int i : M.F[k]) pts.push_back(M.V[i]);
        Poly poly(pts, M.C[k]);
        std::vector<Poly> front, back;
        split(n, w, poly, front, back, 1e-12);
        for (const Poly& p : back) {
            out.add_polygon(p.pts, p.c);
            size_t m = p.pts.size();
            for (size_t i = 0; i < m; ++i) {
                const Point& a = p.pts[i];
                const Point& b = p.pts[(i + 1) % m];
                if (std::fabs(dot(n, a) - w) < 1e-9 && std::fabs(dot(n, b) - w) < 1e-9) rim.push_back({a, b});
            }
        }
    }
    if (cap && !rim.empty()) {
        for (const Points& loop : loops(rim))
            if (loop.size() >= 3) out.add_polygon(loop, color ? *color : (!M.C.empty() ? M.C[0] : DEFAULT_COLOR));
    }
    detail::weld(out, 1e-7);
    detail::drop_degenerate(out);
    detail::drop_unused(out);
    return out;
}

inline bool inside(const Mesh& M, const Point& p) {
    detail::Solid solid(M);
    return solid.contains(p);
}
inline std::vector<bool> inside(const Mesh& M, const Points& ps) {
    detail::Solid solid(M);
    if (ps.empty()) throw std::out_of_range("list index out of range");   // (add.py takes [] for a point)
    std::vector<bool> out;
    for (const Point& q : ps) out.push_back(solid.contains(q));
    return out;
}

}  // namespace add

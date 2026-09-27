// ============================================================================
//  11. Placing things: aim, ground, align, scatter, along
//      (add.py: _src/45_place.py)
// ============================================================================
namespace add {

namespace detail {
//: The copies of along(): mesh M scaled, aimed and moved to every point.
inline Mesh along_copies(const Mesh& M, const Points& pts, const std::vector<double>& ts, const Points& dirs,
                         const std::optional<Point>& axis, const Scalar& scale);
}  // namespace detail

//: Turn a mesh so that its ``axis`` points along ``direction``.
inline Mesh aim(const Mesh& M, const Point& direction, const Point& axis = {0, 1, 0}, const Point& P = {0, 0, 0});
//: Move a mesh straight down (or up) so that its lowest point is at height y.
inline Mesh ground(const Mesh& M, double y = 0.0);
//: Move a mesh so that a chosen point of its bounding box (``anchor``: -1, 0 or 1 per axis) lands on ``at``.
inline Mesh align(const Mesh& M, const Point& at = {0, 0, 0}, const Point& anchor = {0, -1, 0});
//: ``n`` random points in the box lo .. hi (with ``height``: y = height(x, z)).
inline Points random_points(int n, const Point& lo, const Point& hi, std::optional<long long> seed = std::nullopt,
                            const std::function<double(double, double)>& height = nullptr);
//: Copies of a mesh at every point, each turned (``spin``) and sized (between scale[0] and scale[1]) at random.
inline Mesh scatter(const Mesh& M, const Points& points, std::optional<long long> seed = std::nullopt,
                    bool spin = true, const Point2& scale = {1.0, 1.0}, const Point& axis = {0, 1, 0});
//: ``n`` copies of a mesh strung along a curve -- a function path(t) for t in t0 .. t1, or a list of
//: points (then there is one copy per point, and n, t0 and t1 are not used) -- each turned so that its
//: ``axis`` follows the curve (std::nullopt: the copies stay upright); ``scale`` a number or a function of t.
inline Mesh along(const Mesh& M, const std::function<Point(double)>& path, int n, double t0 = 0.0, double t1 = 1.0,
                  std::optional<Point> axis = Point{0, 1, 0}, bool closed = false, const Scalar& scale = Scalar());
inline Mesh along(const Mesh& M, const Points& path, int n, double t0 = 0.0, double t1 = 1.0,
                  std::optional<Point> axis = Point{0, 1, 0}, bool closed = false, const Scalar& scale = Scalar());

}  // namespace add
//@@definitions
namespace add {

inline Mesh aim(const Mesh& M, const Point& direction, const Point& axis, const Point& P) {
    Point a = detail::unit(axis), b = detail::unit(direction);
    Point c = cross(a, b);
    double s = detail::norm(c), d = dot(a, b);
    if (s < 1e-12) {
        if (d > 0) return M;
        return rotate(M, detail::perp(a), pi, P);
    }
    return rotate(M, c, std::atan2(s, d), P);
}

inline Mesh ground(const Mesh& M, double y) {
    std::array<Point, 2> bb = bbox(M);
    return move(M, {0.0, y - bb[0][1], 0.0});
}

inline Mesh align(const Mesh& M, const Point& at, const Point& anchor) {
    std::array<Point, 2> bb = bbox(M);
    const Point& lo = bb[0];
    const Point& hi = bb[1];
    Point shift;
    for (int a = 0; a < 3; ++a) {
        double p;
        if (anchor[a] < 0) p = lo[a];
        else if (anchor[a] > 0) p = hi[a];
        else p = (lo[a] + hi[a]) / 2.0;
        shift[a] = at[a] - p;
    }
    return move(M, shift);
}

inline Points random_points(int n, const Point& lo, const Point& hi, std::optional<long long> seed,
                            const std::function<double(double, double)>& height) {
    Random local = seed ? Random(*seed) : Random(0);
    Random& rnd = seed ? local : detail::rng();
    Points out;
    for (int i = 0; i < n; ++i) {
        double x = rnd.uniform(lo[0], hi[0]);                  // (x, then z, then y)
        double z = rnd.uniform(lo[2], hi[2]);
        double y = height ? height(x, z) : rnd.uniform(lo[1], hi[1]);
        out.push_back({x, y, z});
    }
    return out;
}

inline Mesh scatter(const Mesh& M, const Points& points, std::optional<long long> seed, bool spin,
                    const Point2& scale, const Point& axis) {
    Random local = seed ? Random(*seed) : Random(0);
    Random& rnd = seed ? local : detail::rng();
    Mesh out;
    for (const Point& p : points) {
        double s = rnd.uniform(scale[0], scale[1]);
        Mesh X = std::fabs(s - 1.0) > EPS ? zoom(M, s, Point{0, 0, 0}) : M;
        if (spin) {
            double angle = rnd.uniform(0, 2 * pi);
            X = rotate(X, axis, angle);
        }
        out.extend(move(X, p));
    }
    return out;
}

namespace detail {
inline Mesh along_copies(const Mesh& M, const Points& pts, const std::vector<double>& ts, const Points& dirs,
                         const std::optional<Point>& axis, const Scalar& scale) {
    Mesh out;
    for (size_t i = 0; i < pts.size() && i < ts.size() && i < dirs.size(); ++i) {
        Mesh X = M;
        if (scale) {
            double s = scale(ts[i]);
            X = zoom(X, s, Point{0, 0, 0});
        }
        if (axis && norm(dirs[i]) > EPS) X = aim(X, dirs[i], *axis);
        out.extend(move(X, pts[i]));
    }
    return out;
}
}  // namespace detail

inline Mesh along(const Mesh& M, const std::function<Point(double)>& path, int n, double t0, double t1,
                  std::optional<Point> axis, bool closed, const Scalar& scale) {
    int steps = closed ? n : std::max(1, n - 1);
    std::vector<double> ts;
    for (int i = 0; i < n; ++i) ts.push_back(t0 + (t1 - t0) * i / (double)steps);
    Points pts;
    for (double t : ts) pts.push_back(path(t));
    double h = (t1 - t0) * 1e-4;
    Points dirs;
    for (double t : ts) {
        Point ahead = path(t + h);                             // (in this order, as add.py calls them)
        Point behind = path(t - h);
        dirs.push_back(detail::sub(ahead, behind));
    }
    return detail::along_copies(M, pts, ts, dirs, axis, scale);
}

inline Mesh along(const Mesh& M, const Points& path, int, double, double, std::optional<Point> axis, bool closed,
                  const Scalar& scale) {
    const Points& pts = path;
    int n = (int)pts.size();
    std::vector<double> ts;
    for (int i = 0; i < n; ++i) ts.push_back(i / (double)(closed ? n : std::max(1, n - 1)));
    Points dirs;
    for (int i = 0; i < n; ++i) {
        const Point& a = (i > 0 || closed) ? pts[(size_t)((i - 1 + n) % n)] : pts[(size_t)i];
        const Point& b = (i < n - 1 || closed) ? pts[(size_t)((i + 1) % n)] : pts[(size_t)i];
        dirs.push_back(detail::sub(b, a));
    }
    return detail::along_copies(M, pts, ts, dirs, axis, scale);
}

}  // namespace add

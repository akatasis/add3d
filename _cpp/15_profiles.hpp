// ============================================================================
//  5. Helpers and 2D profiles: numbers, points, outlines, points along curves
//     (add.py: _src/15_profiles.py)
// ============================================================================
namespace add {

//: Blend from ``a`` (t = 0) to ``b`` (t = 1) -- numbers or points.
inline double lerp(double a, double b, double t);
inline Point lerp(const Point& a, const Point& b, double t);
inline Point2 lerp(const Point2& a, const Point2& b, double t);
//: Blend two colours (as add.py blends two colour lists; the result is read as a colour).
inline Color lerp(const Color& a, const Color& b, double t);
//: ``x`` limited to the range lo .. hi.
inline double clamp(double x, double lo = 0.0, double hi = 1.0);
//: Map ``x`` from the range a0..a1 onto the range b0..b1.
inline double remap(double x, double a0, double a1, double b0, double b1);
//: Distance between two points (2D or 3D).
inline double distance(const Point& a, const Point& b);
inline double distance(const Point2& a, const Point2& b);
//: The point half way between ``a`` and ``b``.
inline Point midpoint(const Point& a, const Point& b);
inline Point2 midpoint(const Point2& a, const Point2& b);
//: The unit vector pointing from ``a`` to ``b`` (the difference itself when they coincide).
inline Point direction(const Point& a, const Point& b);
//: Turn a single point around an axis through ``P`` (Rodrigues).
inline Point rotate_point(const Point& p, const Point& axis, double angle, const Point& P = {0, 0, 0});
//: A darker (factor < 1) or lighter (factor > 1) version of a colour.
inline Color shade(const Color& color, double factor);
//: Round the corners of a polyline by cutting them (Chaikin's algorithm).
inline Points chaikin(const Points& points, int rounds = 2, bool closed = false);
inline Profile chaikin(const Profile& points, int rounds = 2, bool closed = false);
//: ``k`` points on a circle of radius ``r``.
inline Profile profile_circle(double r, int k = 32, double phase = 0.0);
//: ``k`` points on an ellipse with half-axes ``a`` and ``b``.
inline Profile profile_ellipse(double a, double b, int k = 32);
//: A regular n-gon with circumradius ``r`` (a flat side at the bottom unless ``phase`` is given).
inline Profile profile_polygon(int n, double r, std::optional<double> phase = std::nullopt);
//: A star with ``n`` points, alternating between the two radii.
inline Profile profile_star(int n, double r_outer, double r_inner, std::optional<double> phase = std::nullopt);
//: A w by h rectangle, with corners rounded by ``r`` if given.
inline Profile profile_rect(double w, double h, double r = 0.0, int k = 4);
//: The outline of a gear: ``teeth`` teeth of height ``depth`` on radius ``r``.
inline Profile profile_gear(int teeth, double r, std::optional<double> depth = std::nullopt, int k = 2);
//: ``n`` points evenly spaced from ``a`` to ``b`` (both included).
inline Points points_on_line(const Point& a, const Point& b, int n);
//: ``n`` points spread evenly on a circle in the plane normal to ``axis``.
inline Points points_on_circle(const Point& center, double r, int n, const Point& axis = {0, 1, 0},
                               double phase = 0.0);
//: ``n`` points along a helix of ``turns`` turns climbing ``pitch`` per turn.
inline Points points_on_helix(const Point& center, double r, double pitch, double turns, int n,
                              const Point& axis = {0, 1, 0});
//: ``n`` points along a flat spiral whose radius grows from r0 to r1.
inline Points points_on_spiral(const Point& center, double r0, double r1, double turns, int n,
                               const Point& axis = {0, 1, 0}, double rise = 0.0);
//: ``n`` points path(t) for t evenly spread over t0 .. t1.
inline Points points_on_curve(const std::function<Point(double)>& path, double t0, double t1, int n,
                              bool closed = false);

}  // namespace add
//@@definitions
namespace add {

inline double lerp(double a, double b, double t) { return a + (b - a) * t; }
inline Point lerp(const Point& a, const Point& b, double t) {
    return {a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t};
}
inline Point2 lerp(const Point2& a, const Point2& b, double t) {
    return {a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t};
}
inline Color lerp(const Color& a, const Color& b, double t) {
    double r = a.r + (b.r - a.r) * t, g = a.g + (b.g - a.g) * t, bl = a.b + (b.b - a.b) * t;
    return Color(r, g, bl);                                    // (floats, read by rgb(): 0..1 ones are scaled)
}

inline double clamp(double x, double lo, double hi) { return x < lo ? lo : (x > hi ? hi : x); }

inline double remap(double x, double a0, double a1, double b0, double b1) {
    if (std::fabs(a1 - a0) < EPS) return b0;
    return b0 + (b1 - b0) * (x - a0) / (a1 - a0);
}

inline double distance(const Point& a, const Point& b) {
    double s = 0.0;                                            // (Python: sum of the squares, in order)
    for (int i = 0; i < 3; ++i) s += detail::py_pow(a[i] - b[i], 2);
    return std::sqrt(s);
}
inline double distance(const Point2& a, const Point2& b) {
    double s = 0.0;
    for (int i = 0; i < 2; ++i) s += detail::py_pow(a[i] - b[i], 2);
    return std::sqrt(s);
}

inline Point midpoint(const Point& a, const Point& b) {
    return {(a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0, (a[2] + b[2]) / 2.0};
}
inline Point2 midpoint(const Point2& a, const Point2& b) { return {(a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0}; }

inline Point direction(const Point& a, const Point& b) {
    Point d{b[0] - a[0], b[1] - a[1], b[2] - a[2]};
    double s = 0.0;
    for (int i = 0; i < 3; ++i) s += d[i] * d[i];
    double n = std::sqrt(s);
    if (n < EPS) return d;
    return {d[0] / n, d[1] / n, d[2] / n};
}

inline Point rotate_point(const Point& p, const Point& axis, double angle, const Point& P) {
    Point k = detail::unit(axis);
    double cs = std::cos(angle), sn = std::sin(angle);
    Point v = detail::sub(p, P);
    Point kv = cross(k, v);
    double d = dot(k, v) * (1.0 - cs);
    return {P[0] + v[0] * cs + kv[0] * sn + k[0] * d,
            P[1] + v[1] * cs + kv[1] * sn + k[1] * d,
            P[2] + v[2] * cs + kv[2] * sn + k[2] * d};
}

inline Color shade(const Color& color, double factor) {
    int r = color.r, g = color.g, b = color.b;
    if (factor <= 1.0) return Color((int)(r * factor), (int)(g * factor), (int)(b * factor));
    double t = std::min(1.0, factor - 1.0);
    return Color((int)(r + (255 - r) * t), (int)(g + (255 - g) * t), (int)(b + (255 - b) * t));
}

template <class P_>
inline std::vector<P_> chaikin_(const std::vector<P_>& points, int rounds, bool closed, int dim) {
    std::vector<P_> pts = points;
    if (!closed && pts.empty() && rounds > 0) throw std::out_of_range("list index out of range");   // (as Python)
    for (int round = 0; round < rounds; ++round) {
        size_t n = pts.size();
        std::vector<P_> out;
        size_t pairs = closed ? n : (n > 0 ? n - 1 : 0);
        if (!closed && n > 0) out.push_back(pts[0]);
        for (size_t i = 0; i < pairs; ++i) {
            const P_& a = pts[i];
            const P_& b = pts[(i + 1) % n];
            P_ p, q;
            for (int j = 0; j < dim; ++j) {
                p[j] = a[j] * 0.75 + b[j] * 0.25;
                q[j] = a[j] * 0.25 + b[j] * 0.75;
            }
            out.push_back(p);
            out.push_back(q);
        }
        if (!closed && n > 0) out.push_back(pts[n - 1]);
        pts = out;
    }
    return pts;
}
inline Points chaikin(const Points& points, int rounds, bool closed) { return chaikin_(points, rounds, closed, 3); }
inline Profile chaikin(const Profile& points, int rounds, bool closed) { return chaikin_(points, rounds, closed, 2); }

inline Profile profile_circle(double r, int k, double phase) {
    Profile out;
    for (int i = 0; i < k; ++i)
        out.push_back({r * std::cos(phase + 2 * pi * i / k), r * std::sin(phase + 2 * pi * i / k)});
    return out;
}

inline Profile profile_ellipse(double a, double b, int k) {
    Profile out;
    for (int i = 0; i < k; ++i) out.push_back({a * std::cos(2 * pi * i / k), b * std::sin(2 * pi * i / k)});
    return out;
}

inline Profile profile_polygon(int n, double r, std::optional<double> phase) {
    double ph = phase ? *phase : -pi / 2.0 + pi / n;
    return profile_circle(r, n, ph);
}

inline Profile profile_star(int n, double r_outer, double r_inner, std::optional<double> phase) {
    double ph = phase ? *phase : pi / 2.0;
    Profile pts;
    for (int i = 0; i < 2 * n; ++i) {
        double r = i % 2 == 0 ? r_outer : r_inner;
        double a = ph + pi * i / n;
        pts.push_back({r * std::cos(a), r * std::sin(a)});
    }
    return pts;
}

inline Profile profile_rect(double w, double h, double r, int k) {
    double x = w / 2.0, y = h / 2.0;
    if (r <= EPS) return {{-x, -y}, {x, -y}, {x, y}, {-x, y}};
    if (x < r) r = x;                                          // r = min(r, x, y) (the first of equals)
    if (y < r) r = y;
    Profile pts;
    const double corners[4][3] = {{x - r, y - r, 0.0}, {-x + r, y - r, pi / 2},
                                  {-x + r, -y + r, pi}, {x - r, -y + r, 3 * pi / 2}};
    for (const auto& c : corners) {
        double cx = c[0], cy = c[1], a0 = c[2];
        for (int i = 0; i < k + 1; ++i) {
            double a = a0 + (pi / 2) * i / k;
            pts.push_back({cx + r * std::cos(a), cy + r * std::sin(a)});
        }
    }
    return pts;
}

inline Profile profile_gear(int teeth, double r, std::optional<double> depth, int /*k: not used (as in add.py)*/) {
    double dp = depth ? *depth : r * 0.2;
    Profile pts;
    int n = 4 * teeth;
    for (int i = 0; i < n; ++i) {
        int phase = i % 4;
        double a = 2 * pi * i / n;
        double rr = (phase == 1 || phase == 2) ? r + dp / 2.0 : r - dp / 2.0;
        pts.push_back({rr * std::cos(a), rr * std::sin(a)});
    }
    return pts;
}

inline Points points_on_line(const Point& a, const Point& b, int n) {
    if (n <= 1) return {a};
    Points out;
    for (int i = 0; i < n; ++i) out.push_back(lerp(a, b, i / (double)(n - 1)));
    return out;
}

inline Points points_on_circle(const Point& center, double r, int n, const Point& axis, double phase) {
    detail::Frame fr = detail::frame(axis);
    return detail::ring(center, fr.u, fr.v, r, n, phase);
}

inline Points points_on_helix(const Point& center, double r, double pitch, double turns, int n, const Point& axis) {
    detail::Frame fr = detail::frame(axis);
    const Point &u = fr.u, &v = fr.v, &w = fr.w;
    Points out;
    for (int i = 0; i < n; ++i) {
        double t = turns * i / (double)std::max(1, n - 1);
        double a = 2 * pi * t;
        Point p;
        for (int j = 0; j < 3; ++j)
            p[j] = center[j] + (u[j] * std::cos(a) + v[j] * std::sin(a)) * r + w[j] * pitch * t;
        out.push_back(p);
    }
    return out;
}

inline Points points_on_spiral(const Point& center, double r0, double r1, double turns, int n, const Point& axis,
                               double rise) {
    detail::Frame fr = detail::frame(axis);
    const Point &u = fr.u, &v = fr.v, &w = fr.w;
    Points out;
    for (int i = 0; i < n; ++i) {
        double t = i / (double)std::max(1, n - 1);
        double a = 2 * pi * turns * t;
        double r = r0 + (r1 - r0) * t;
        Point p;
        for (int j = 0; j < 3; ++j)
            p[j] = center[j] + (u[j] * std::cos(a) + v[j] * std::sin(a)) * r + w[j] * rise * t;
        out.push_back(p);
    }
    return out;
}

inline Points points_on_curve(const std::function<Point(double)>& path, double t0, double t1, int n, bool closed) {
    int steps = closed ? n : std::max(1, n - 1);
    Points out;
    for (int i = 0; i < n; ++i) out.push_back(path(t0 + (t1 - t0) * i / (double)steps));
    return out;
}

}  // namespace add

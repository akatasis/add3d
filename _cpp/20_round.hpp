// ============================================================================
//  6. Round shapes: spheres, cylinders, cones, tori, revolve, helix
//     (add.py: _src/20_round.py)
// ============================================================================
namespace add {

namespace detail {
//: Points of a surface of revolution (the P[i][j] grid add_grid expects) and whether it
//: closes all the way round (add.py returns the pair (P, closed)).
inline std::pair<std::vector<Points>, bool> revolve_grid(const Point& A, const Point& direction,
                                                         const Profile& profile, int k, double angle = 2.0 * pi,
                                                         double phase = 0.0);
//: Unit geodesic sphere: vertices and triangles.
inline std::pair<Points, std::vector<Face>> icosphere_grid(int subdivisions);
//: The engine behind cylinder / cone / frustum and their variants: the finished (welded) mesh.
inline Mesh tube_body(const Point& A, const Point& B, double r1, double r2, int k, const Color& color, bool cap_a,
                      bool cap_b);
}  // namespace detail

//: A 2D profile spun round the axis A -> B (a lathe): ``profile(t)`` gives [radius, height] (the
//: height measured along the axis from A) for t from t0 to t1, sampled steps + 1 times.
//: ``color`` may be a function (t, angle) of the middle of each cell.  A list of [radius, height]
//: points (add.hpp only; add.py needs a function) is spun as it is: point i is the sample at
//: t = t0 + (t1 - t0) * i / (n - 1), and ``steps`` is not used.
inline void revolve(const Profile& profile, const Point& A = {0, 0, 0}, const Point& B = {0, 1, 0}, double t0 = 0.0,
                    double t1 = 1.0, int steps = 40, int k = 32, const ColorOf<double, double>& color = DEFAULT_COLOR,
                    double angle = 2.0 * pi, bool caps = true);
inline void revolve(const std::function<Point2(double)>& profile, const Point& A = {0, 0, 0},
                    const Point& B = {0, 1, 0}, double t0 = 0.0, double t1 = 1.0, int steps = 40, int k = 32,
                    const ColorOf<double, double>& color = DEFAULT_COLOR, double angle = 2.0 * pi, bool caps = true);
//: add.py 1.2 lathe: spin the curve S(t) = [radius, height] around A -> B.
inline void spin3D(const Point& A, const Point& B, const std::function<Point2(double)>& S, double min_t, double max_t,
                   int grid_t, int k, const Color& RGB);
//: A geodesic sphere: an icosahedron whose triangles are split ``subdivisions`` times (0..7).
//: ``color`` may be a function of the face's direction from the centre (a unit vector).
inline void icosphere(const Point& center, double r, int subdivisions = 3,
                      const ColorOf<Point>& color = DEFAULT_COLOR);
//: A sphere built from triangles (``k`` sets the fineness; or give ``subdivisions``); ``color``
//: may be a function of the direction, as in icosphere.
inline void sphere(const Point& center, double r, int k = 10, const ColorOf<Point>& color = DEFAULT_COLOR,
                   std::optional<int> subdivisions = std::nullopt);
//: A sphere built from six curved square patches (all faces are quads).
inline void quadsphere(const Point& center, double r, int k = 10, const Color& color = DEFAULT_COLOR);
//: Like quadsphere but with a separate radius for X, Y and Z.
inline void ellipsoid(const Point& center, const Point& radii, int k = 10, const Color& color = DEFAULT_COLOR);
//: A globe-style sphere: nu meridians by nv parallels.
inline void uvsphere(const Point& center, double r, int nu = 32, int nv = 16, const Color& color = DEFAULT_COLOR);
//: A doughnut: tube radius r swept round a circle of radius R.
inline void torus(const Point& center, double R, double r, int nu = 48, int nv = 24,
                  const Color& color = DEFAULT_COLOR, const Point& axis = {0, 1, 0});
//: A closed cylinder from A to B, radius r, k sides.
inline void cylinder(const Point& A, const Point& B, double r, int k = 24, const Color& color = DEFAULT_COLOR);
//: A cylinder with no lids -- just the side wall (old cylinder2).
inline void tube(const Point& A, const Point& B, double r, int k = 24, const Color& color = DEFAULT_COLOR);
//: A cylinder closed at A only (old cylinder3).
inline void cup(const Point& A, const Point& B, double r, int k = 24, const Color& color = DEFAULT_COLOR);
//: A closed cone: circular base of radius r at A, tip at B.
inline void cone(const Point& A, const Point& B, double r, int k = 24, const Color& color = DEFAULT_COLOR);
//: Only the slanted wall of a cone (old cone2).
inline void cone_open(const Point& A, const Point& B, double r, int k = 24, const Color& color = DEFAULT_COLOR);
//: A cone with its tip cut off: radius r1 at A, r2 at B.
inline void frustum(const Point& A, const Point& B, double r1, double r2, int k = 24,
                    const Color& color = DEFAULT_COLOR, bool caps = true);
//: A hollow tube -- a cylinder with a cylindrical hole down the middle.
inline void pipe(const Point& A, const Point& B, double r_outer, double r_inner, int k = 24,
                 const Color& color = DEFAULT_COLOR);
//: A cylinder with a hemisphere on each end (a "pill").
inline void capsule(const Point& A, const Point& B, double r, int k = 24, const Color& color = DEFAULT_COLOR);
//: A shaft from A to B with a cone head -- good for vectors.
inline void arrow(const Point& A, const Point& B, double r = 0.05, const Color& color = DEFAULT_COLOR, int k = 16,
                  double head = 0.25);
//: A spring / helical tube of ``turns`` turns around ``axis``.
inline void helix(const Point& center, double r, double pitch, double turns, int k = 200, double thickness = 0.1,
                  int sides = 12, const Color& color = DEFAULT_COLOR, const Point& axis = {0, 1, 0});
//: The coordinate axes: X red, Y green, Z blue, each labelled.
inline void axes(const Point& C = {0, 0, 0}, double length = 4.0, double width = 0.03);

}  // namespace add
//@@definitions
namespace add {

namespace detail {

inline std::pair<std::vector<Points>, bool> revolve_grid(const Point& A, const Point& direction,
                                                         const Profile& profile, int k, double angle, double phase) {
    Frame fr = frame(direction);
    const Point &u = fr.u, &v = fr.v, &w = fr.w;
    bool closed = std::fabs(angle - 2.0 * pi) < 1e-12;
    int steps = closed ? k : k + 1;
    std::vector<std::pair<double, double>> cs;
    for (int j = 0; j < steps; ++j) {
        double a = phase + angle * (j / (double)k);
        cs.push_back({std::cos(a), std::sin(a)});
    }
    std::vector<Points> P;
    for (const Point2& rh : profile) {
        double r = rh[0], h = rh[1];
        Point centre = add3(A, scale(w, h));
        Points row;
        for (const std::pair<double, double>& q : cs) {
            double c = q.first, s = q.second;
            row.push_back({centre[0] + u[0] * r * c + v[0] * r * s,
                           centre[1] + u[1] * r * c + v[1] * r * s,
                           centre[2] + u[2] * r * c + v[2] * r * s});
        }
        P.push_back(row);
    }
    return {P, closed};
}

inline std::pair<Points, std::vector<Face>> icosphere_grid(int subdivisions) {
    std::pair<Points, std::vector<Face>> VT = platonic("icosahedron");
    Points V;
    for (const Point& p : VT.first) V.push_back(unit(p));
    std::vector<Face> T = VT.second;
    for (int round = 0; round < subdivisions; ++round) {
        std::map<std::pair<int, int>, int> mid;
        auto midpoint_index = [&](int a, int b) {
            std::pair<int, int> key = a < b ? std::make_pair(a, b) : std::make_pair(b, a);
            auto it = mid.find(key);
            if (it != mid.end()) return it->second;
            Point m = unit({(V[a][0] + V[b][0]) * 0.5, (V[a][1] + V[b][1]) * 0.5, (V[a][2] + V[b][2]) * 0.5});
            int made = (int)V.size();
            mid[key] = made;
            V.push_back(m);
            return made;
        };
        std::vector<Face> next;
        for (const Face& f : T) {
            int a = f[0], b = f[1], c = f[2];
            int ab = midpoint_index(a, b);
            int bc = midpoint_index(b, c);
            int ca = midpoint_index(c, a);
            next.push_back({a, ab, ca});
            next.push_back({b, bc, ab});
            next.push_back({c, ca, bc});
            next.push_back({ab, bc, ca});
        }
        T = next;
    }
    return {V, T};
}

inline Mesh tube_body(const Point& A, const Point& B, double r1, double r2, int k, const Color& color, bool cap_a,
                      bool cap_b) {
    Point d = sub(B, A);
    if (norm(d) < EPS) return Mesh();
    Frame fr = frame(d);
    Mesh M;
    Points ring_a = ring(A, fr.u, fr.v, r1, k);
    Points ring_b = ring(B, fr.u, fr.v, r2, k);
    if (r1 < EPS)                                              // cone standing on its point
        fan(M, ring_b, A, color, true);
    else if (r2 < EPS)                                         // cone with the point at B
        fan(M, ring_a, B, color);
    else
        add_grid(M, {ring_a, ring_b}, color, false, true, true);
    if (cap_a && r1 >= EPS) fan(M, ring_a, A, color, true);
    if (cap_b && r2 >= EPS) fan(M, ring_b, B, color);
    detail::weld(M, 1e-9);
    return M;
}

}  // namespace detail

// -- revolve -----------------------------------------------------------------------

inline void revolve(const std::function<Point2(double)>& profile, const Point& A, const Point& B, double t0,
                    double t1, int steps, int k, const ColorOf<double, double>& color, double angle, bool caps) {
    if (steps == 0)
        throw std::domain_error("float division by zero");      // (as Python: ZeroDivisionError)
    Profile pts;
    for (int i = 0; i < steps + 1; ++i) {
        double t = t0 + (t1 - t0) * i / (double)steps;
        Point2 g = profile(t);
        pts.push_back({g[0], g[1]});
    }
    Point direction = detail::sub(B, A);
    std::pair<std::vector<Points>, bool> grid_ = detail::revolve_grid(A, direction, pts, k, angle);
    const std::vector<Points>& P = grid_.first;
    bool closed = grid_.second;
    detail::CellPaint cells = color.color;
    ColorOf<int> lid_a = color.color, lid_b = color.color;
    Color side_a = color.color, side_b = color.color;
    if (color.callable()) {                                    // cell (i, j) -> (t, angle), at its middle
        cells = detail::CellPaint([&](int i, int j) {
            double t = t0 + (t1 - t0) * (i + 0.5) / (double)steps;
            return color(t, angle * (j + 0.5) / (double)k);
        });
        lid_a = ColorOf<int>([&](int j) { return color(t0, angle * (j + 0.5) / (double)k); });
        lid_b = ColorOf<int>([&](int j) { return color(t1, angle * (j + 0.5) / (double)k); });
        side_a = color((t0 + t1) / 2.0, 0.0);
        side_b = color((t0 + t1) / 2.0, angle);
    }
    Mesh M;
    detail::add_grid(M, P, cells, false, closed, true);
    if (caps) {
        Point w = detail::unit(direction);
        Point first = detail::add3(A, detail::scale(w, pts[0][1]));
        Point last = detail::add3(A, detail::scale(w, pts.back()[1]));
        if (pts[0][0] > EPS)                                   // flat lid at the start
            detail::fan(M, P[0], first, lid_a, true, closed);
        if (pts.back()[0] > EPS)                               // flat lid at the end
            detail::fan(M, P.back(), last, lid_b, false, closed);
        if (!closed) {                                         // the two sides of the wedge
            Points side;                                       // (at(): add.py's row[0] fails on k < 0)
            for (const Points& row : P) side.push_back(row.at(0));
            side.push_back(last);
            side.push_back(first);
            M.add_polygon(side, side_a);
            side.clear();
            for (const Points& row : P) side.push_back(row.at(row.size() - 1));
            side.push_back(last);
            side.push_back(first);
            M.add_polygon(side, side_b);
        }
        detail::weld(M, 1e-9);
        detail::drop_degenerate(M);
        if (!closed) M = fix_normals(M);
        detail::make_outward(M, 0);                            // whichever way the profile was drawn
    }
    detail::emit(M);
}

inline void revolve(const Profile& profile, const Point& A, const Point& B, double t0, double t1,
                    int /*steps: the list's own*/, int k, const ColorOf<double, double>& color, double angle,
                    bool caps) {
    // The list as the function add.py samples: its i-th call gives point i.
    size_t next = 0;
    std::function<Point2(double)> sample = [&](double) { return profile.at(next++); };
    revolve(sample, A, B, t0, t1, (int)profile.size() - 1, k, color, angle, caps);
}

inline void spin3D(const Point& A, const Point& B, const std::function<Point2(double)>& S, double min_t, double max_t,
                   int grid_t, int k, const Color& RGB) {
    revolve(S, A, B, min_t, max_t, grid_t, k, RGB, 2.0 * pi, false);
}

// -- spheres -------------------------------------------------------------------------

inline void icosphere(const Point& center, double r, int subdivisions, const ColorOf<Point>& color) {
    int level = subdivisions;
    level = level < 0 ? 0 : (level > 7 ? 7 : level);
    std::pair<Points, std::vector<Face>> VT = detail::icosphere_grid(level);
    const Points& V = VT.first;
    Mesh M;
    for (const Point& p : V) M.add_vertex({center[0] + p[0] * r, center[1] + p[1] * r, center[2] + p[2] * r});
    if (color.callable()) {
        for (const Face& f : VT.second) {
            int a = f[0], b = f[1], c = f[2];
            Point d = detail::unit({V[a][0] + V[b][0] + V[c][0], V[a][1] + V[b][1] + V[c][1],
                                    V[a][2] + V[b][2] + V[c][2]});
            M.add_face({a, b, c}, color(d));
        }
    } else {
        for (const Face& f : VT.second) M.add_face(f, color.color);
    }
    detail::current().extend(M);
}

inline void sphere(const Point& center, double r, int k, const ColorOf<Point>& color,
                   std::optional<int> subdivisions) {
    int level;
    if (!subdivisions) {
        k = std::max(1, k);
        // Python's math.log(x, 2) is log(x) / log(2), and round() rounds half to even.
        level = k > 1 ? (int)std::nearbyint(std::log(2.0 * k / 3.0) / std::log(2.0)) : 0;
    } else {
        level = *subdivisions;
    }
    icosphere(center, r, level, color);
}

inline void quadsphere(const Point& center, double r, int k, const Color& color) {
    ellipsoid(center, {r, r, r}, k, color);
}

inline void ellipsoid(const Point& center, const Point& radii, int k, const Color& color) {
    static const int sides[6][3][3] = {{{1, 0, 0}, {0, 1, 0}, {0, 0, 1}},
                                       {{-1, 0, 0}, {0, 0, 1}, {0, 1, 0}},
                                       {{0, 1, 0}, {0, 0, 1}, {1, 0, 0}},
                                       {{0, -1, 0}, {1, 0, 0}, {0, 0, 1}},
                                       {{0, 0, 1}, {1, 0, 0}, {0, 1, 0}},
                                       {{0, 0, -1}, {0, 1, 0}, {1, 0, 0}}};
    // Spreading the samples with tan() keeps the cells the same size.
    std::vector<double> warp;
    for (int i = 0; i < k + 1; ++i) warp.push_back(std::tan(pi / 4.0 * (2.0 * i / k - 1.0)));
    Mesh M;
    for (const auto& side : sides) {
        const int *n = side[0], *u = side[1], *v = side[2];
        std::vector<Points> P;
        for (double a : warp) {
            Points row;
            for (double b : warp) {
                Point p = detail::unit({n[0] + u[0] * a + v[0] * b,
                                        n[1] + u[1] * a + v[1] * b,
                                        n[2] + u[2] * a + v[2] * b});
                row.push_back({center[0] + p[0] * radii[0], center[1] + p[1] * radii[1], center[2] + p[2] * radii[2]});
            }
            P.push_back(row);
        }
        detail::add_grid(M, P, color);
    }
    detail::weld(M, 1e-9);
    detail::current().extend(M);
}

inline void uvsphere(const Point& center, double r, int nu, int nv, const Color& color) {
    Profile profile;
    for (int i = 0; i < nv + 1; ++i) profile.push_back({r * std::sin(pi * i / nv), r - r * std::cos(pi * i / nv)});
    std::vector<Points> P = detail::revolve_grid({center[0], center[1] - r, center[2]}, {0, 1, 0}, profile, nu).first;
    Mesh M;
    detail::add_grid(M, P, color, false, true, true);
    detail::weld(M, 1e-9);
    detail::drop_degenerate(M);
    detail::current().extend(M);
}

inline void torus(const Point& center, double R, double r, int nu, int nv, const Color& color, const Point& axis) {
    detail::Frame fr = detail::frame(axis);
    const Point &u = fr.u, &v = fr.v, &w = fr.w;
    std::vector<Points> P;
    for (int i = 0; i < nu; ++i) {
        double a = 2.0 * pi * i / nu;
        Point ring_centre{center[0] + (u[0] * std::cos(a) + v[0] * std::sin(a)) * R,
                          center[1] + (u[1] * std::cos(a) + v[1] * std::sin(a)) * R,
                          center[2] + (u[2] * std::cos(a) + v[2] * std::sin(a)) * R};
        Point out{u[0] * std::cos(a) + v[0] * std::sin(a),
                  u[1] * std::cos(a) + v[1] * std::sin(a),
                  u[2] * std::cos(a) + v[2] * std::sin(a)};
        Points row;
        for (int j = 0; j < nv; ++j) {
            double b = 2.0 * pi * j / nv;
            double cb = std::cos(b) * r, sb = std::sin(b) * r;
            row.push_back({ring_centre[0] + out[0] * cb + w[0] * sb,
                           ring_centre[1] + out[1] * cb + w[1] * sb,
                           ring_centre[2] + out[2] * cb + w[2] * sb});
        }
        P.push_back(row);
    }
    Mesh M;
    detail::add_grid(M, P, color, true, true);
    detail::make_outward(M, 0);
    detail::current().extend(M);
}

// -- cylinders, cones and friends ------------------------------------------------------

inline void cylinder(const Point& A, const Point& B, double r, int k, const Color& color) {
    detail::current().extend(detail::tube_body(A, B, r, r, k, color, true, true));
}

inline void tube(const Point& A, const Point& B, double r, int k, const Color& color) {
    detail::current().extend(detail::tube_body(A, B, r, r, k, color, false, false));
}

inline void cup(const Point& A, const Point& B, double r, int k, const Color& color) {
    detail::current().extend(detail::tube_body(A, B, r, r, k, color, true, false));
}

inline void cone(const Point& A, const Point& B, double r, int k, const Color& color) {
    detail::current().extend(detail::tube_body(A, B, r, 0.0, k, color, true, false));
}

inline void cone_open(const Point& A, const Point& B, double r, int k, const Color& color) {
    detail::current().extend(detail::tube_body(A, B, r, 0.0, k, color, false, false));
}

inline void frustum(const Point& A, const Point& B, double r1, double r2, int k, const Color& color, bool caps) {
    detail::current().extend(detail::tube_body(A, B, r1, r2, k, color, caps, caps));
}

inline void pipe(const Point& A, const Point& B, double r_outer, double r_inner, int k, const Color& color) {
    Point d = detail::sub(B, A);
    detail::Frame fr = detail::frame(d);
    Mesh M;
    Points oa = detail::ring(A, fr.u, fr.v, r_outer, k), ob = detail::ring(B, fr.u, fr.v, r_outer, k);
    Points ia = detail::ring(A, fr.u, fr.v, r_inner, k), ib = detail::ring(B, fr.u, fr.v, r_inner, k);
    detail::add_grid(M, {oa, ob}, color, false, true, true);  // outside
    detail::add_grid(M, {ia, ib}, color, false, true);        // inside
    detail::add_grid(M, {ia, oa}, color, false, true, true);  // ring at A
    detail::add_grid(M, {ib, ob}, color, false, true);        // ring at B
    detail::emit(M);
}

inline void capsule(const Point& A, const Point& B, double r, int k, const Color& color) {
    Point d = detail::sub(B, A);
    double length = detail::norm(d);
    int n = std::max(3, k / 3);                                // (k // 3: the same for k >= 0, and 3 below that)
    Profile profile;
    for (int i = 0; i < n + 1; ++i) {                          // lower hemisphere
        double a = pi / 2 * i / n;
        profile.push_back({r * std::sin(a), r - r * std::cos(a)});
    }
    for (int i = 0; i < n + 1; ++i) {                          // upper hemisphere
        double a = pi / 2 * i / n;
        profile.push_back({r * std::cos(a), r + length + r * std::sin(a)});
    }
    Point start = detail::add3(A, detail::scale(detail::unit(d), -r));
    std::vector<Points> P = detail::revolve_grid(start, d, profile, k).first;
    Mesh M;
    detail::add_grid(M, P, color, false, true, true);
    detail::weld(M, 1e-9);
    detail::drop_degenerate(M);
    detail::make_outward(M, 0);
    detail::current().extend(M);
}

inline void arrow(const Point& A, const Point& B, double r, const Color& color, int k, double head) {
    Point d = detail::sub(B, A);
    double n = detail::norm(d);
    if (n < EPS) return;
    Point joint = detail::add3(A, detail::scale(d, 1.0 - head));
    cylinder(A, joint, r, k, color);
    cone(joint, B, r * 2.4, k, color);
}

inline void helix(const Point& center, double r, double pitch, double turns, int k, double thickness, int sides,
                  const Color& color, const Point& axis) {
    detail::Frame fr = detail::frame(axis);
    const Point &u = fr.u, &v = fr.v, &w = fr.w;
    auto path = [&](double t) {
        double a = 2.0 * pi * t;
        return Point{center[0] + (u[0] * std::cos(a) + v[0] * std::sin(a)) * r + w[0] * pitch * t,
                     center[1] + (u[1] * std::cos(a) + v[1] * std::sin(a)) * r + w[1] * pitch * t,
                     center[2] + (u[2] * std::cos(a) + v[2] * std::sin(a)) * r + w[2] * pitch * t};
    };
    curve(path, 0, turns, k, sides, thickness, color, false);
}

// -- coordinate axes ---------------------------------------------------------------------

inline void axes(const Point& C, double length, double width) {
    double h = length, w = width;
    const Point directions[3] = {{1, 0, 0}, {0, 1, 0}, {0, 0, 1}};
    const Color cols[3] = {Color(255, 0, 0), Color(0, 255, 0), Color(0, 0, 255)};
    for (int q = 0; q < 3; ++q) {
        Point end = detail::add3(C, detail::scale(directions[q], h));
        Point tip = detail::add3(C, detail::scale(directions[q], h + 0.7));
        cylinder(C, end, w, 9, cols[q]);
        cone(end, tip, 2 * w, 9, cols[q]);
    }
    // All three labels stand in the XY plane so they read the same way round.
    glyph("X", detail::add3(C, {h + 0.35, 0.25, 0}), {1, 0, 0}, {0, 1, 0}, 0.6, 3 * w, Color(255, 0, 0));
    glyph("Y", detail::add3(C, {0.3, h + 0.35, 0}), {1, 0, 0}, {0, 1, 0}, 0.6, 3 * w, Color(0, 255, 0));
    glyph("Z", detail::add3(C, {0.1, 0.25, h + 0.5}), {1, 0, 0}, {0, 1, 0}, 0.6, 3 * w, Color(0, 0, 255));
}

}  // namespace add

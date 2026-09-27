#include "parity.hpp"

// revolve() and spin3D() call fix_normals() (section 50) and axes() calls glyph() (section
// 75).  With a header that lacks those sections their calls compile but cannot link, so
// their cases are built only when that section's own tests are here too (at integration)
// -- or when PARITY_PENDING is defined (with PARITY_PENDING=1 set for the Python half).
#if defined(PARITY_PENDING) || __has_include("cases_50_clean.cpp")
#define WITH_50 1
#else
#define WITH_50 0
#endif
#if defined(PARITY_PENDING) || __has_include("cases_75_text.cpp")
#define WITH_75 1
#else
#define WITH_75 0
#endif

using add::Point;
using add::Point2;
using add::Points;
using add::Profile;

static void record_faces(const std::vector<add::Face>& F) {
    record((long long)F.size());
    for (const add::Face& f : F) {
        std::string s;
        for (size_t i = 0; i < f.size(); ++i) s += (i ? " " : "") + std::to_string(f[i]);
        record(s);
    }
}

// Record whether f() throws (an exception would end the case).
template <class F>
static void raises(F f) {
    try {
        f();
    } catch (const std::exception&) {
        record("raises");
        return;
    }
    record("returns");
}

// -- spheres -----------------------------------------------------------------------

CASE(spheres) {
    add::sphere({0, 0, 0}, 1.0);
    add::sphere({3, 0, 0}, 0.5, 1, "red");
    add::sphere({6, 0, 0}, 0.5, 2, "blue");
    add::sphere({9, 0, 0}, 0.7, 5);
    add::sphere({0, 3, 0}, 0.7, 4, {0.1, 0.9, 0.3});
    add::sphere({0, 6, 0}, 1.2, 10, "gold", 1);
    add::sphere({3, 6, 0}, 0.3, 50, "teal", 0);
    save_case();
}

CASE(sphere_levels) {
    for (int k : {-5, 0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 16, 17, 20, 33, 34}) {
        add::sphere({0, 0, 0}, 1.0, k);
        record((long long)add::layer().F.size());
    }
    for (int level : {-1, 0, 2, 3}) {
        add::sphere({0, 0, 0}, 1.0, 1000, add::DEFAULT_COLOR, level);
        record((long long)add::layer().F.size());
    }
}

CASE(icosphere_levels) {
    for (int level : {-3, 0, 1, 2, 9}) {
        add::icosphere({0.5, -1, 2}, 1.5, level);
        add::Mesh S = add::layer();
        record((long long)S.V.size());
        record((long long)S.F.size());
        double s = 0.0;
        for (const Point& p : S.V) {
            s = s + p[0];
            s = s + p[1];
            s = s + p[2];
        }
        record(s);
        record(Points(S.V.end() - 3, S.V.end()));
        record_faces(std::vector<add::Face>(S.F.end() - 2, S.F.end()));
    }
}

CASE(icospheres) {
    add::icosphere({0, 0, 0}, 1.0);
    add::icosphere({3, 0, 0}, 1.5, 0, "red");
    add::icosphere({6, 0, 0}, 0.5, -2);
    add::icosphere({0, 3, 0}, 2.0, 2, [](const Point& d) { return d[1] > 0.7 ? "white" : "blue"; });
    add::icosphere({5, 3, 0}, 1.0, 1, [](const Point& d) { return add::hsv(std::atan2(d[2], d[0]) / (2 * add::pi)); });
    add::sphere({0, 7, 0}, 1.0, 5,
                [](const Point& d) { return add::Color(0.5 + 0.5 * d[0], 0.5 + 0.5 * d[1], 0.5 + 0.5 * d[2]); });
    add::sphere({5, 7, 0}, 1.0, 3, [](const Point&) { return add::random_color(); }, 1);
    add::icosphere({10, 3, 0}, 1.0, 1, [](const Point& d) { return add::transparent("sky", 0.5 + 0.25 * d[1]); });
    save_case();
}

CASE(quad_spheres) {
    add::quadsphere({0, 0, 0}, 1.0);
    add::quadsphere({3, 0, 0}, 0.5, 3, "red");
    add::quadsphere({6, 0, 0}, 0.75, 1, "gold");
    add::ellipsoid({0, 3, 0}, {1.0, 2.0, 0.5});
    add::ellipsoid({4, 3, 0}, {0.5, 0.5, 1.5}, 4, "teal");
    add::ellipsoid({8, 3, 0}, {0.3, -0.6, 0.9}, 2, {0.25, 0.5, 0.75});
    save_case();
}

CASE(uv_spheres_and_tori) {
    add::uvsphere({0, 0, 0}, 1.0);
    add::uvsphere({3, 0, 0}, 0.8, 8, 5, "red");
    add::uvsphere({6, 0, 0}, 0.5, 3, 2);
    add::uvsphere({9, 0, 0}, 0.5, 4, 1, "blue");
    add::torus({0, 4, 0}, 2.0, 0.5);
    add::torus({6, 4, 0}, 1.0, 0.3, 12, 6, "gold", {1, 0, 0});
    add::torus({0, 8, 0}, 1.5, 0.4, 7, 5, "sky", {1, 1, 1});
    add::torus({6, 8, 0}, 1.0, 0.25, 3, 3, "red", {0, 0, -1});
    add::torus({10, 8, 0}, 0.5, 0.75, 8, 4, "navy");                    // a self-crossing spindle torus
    save_case();
}

// -- cylinders, cones and friends ---------------------------------------------------

CASE(cylinders) {
    add::cylinder({0, 0, 0}, {0, 2, 0}, 0.5);
    add::cylinder({2, 0, 0}, {3, 1, 2}, 0.3, 7, "red");
    add::tube({4, 0, 0}, {4, 0, 3}, 0.4, 6, "blue");
    add::tube({5, 0, 0}, {5, 1, 0}, 0.4);
    add::cup({6, 0, 0}, {6, -2, 0}, 0.5, 5, "green");
    add::cup({7, 0, 0}, {7, 1, 0}, 0.5);
    add::cylinder({0, 0, 5}, {0, 0, 5}, 1.0);                          // A == B: nothing
    add::cylinder({1, 1, 1}, {1, 1, 1.5}, 0.25, 3);
    add::cylinder({2, 1, 1}, {2, 1, 1.5}, 0.25, 1, "red");
    save_case();
}

CASE(cones) {
    add::cone({0, 4, 0}, {0, 6, 0}, 0.8);
    add::cone({2, 4, 0}, {2.5, 3, 1}, 0.4, 3, "gold");
    add::cone_open({4, 4, 0}, {4, 6, 0}, 0.6, 8, "teal");
    add::cone_open({5, 4, 0}, {5, 5, 0}, 0.6);
    add::frustum({6, 4, 0}, {6, 6, 0}, 0.8, 0.3);
    add::frustum({8, 4, 0}, {8, 6, 0}, 0.3, 0.8, 9, "pink", false);
    add::frustum({10, 4, 0}, {10, 6, 0}, 0.0, 0.5, 6, "navy");         // r1 = 0: a cone on its point
    add::frustum({12, 4, 0}, {12, 6, 0}, 0.5, 0.0, 6, "navy");
    add::frustum({14, 4, 0}, {14, 6, 0}, 0.0, 0.0, 4, "red");
    add::frustum({16, 4, 0}, {17, 6, 1}, 0.5, 1e-10, 5, "blue", false);
    save_case();
}

CASE(pipes_capsules_arrows) {
    add::pipe({0, 0, 0}, {0, 2, 0}, 1.0, 0.7);
    add::pipe({3, 0, 0}, {4, 1, 1}, 0.5, 0.2, 7, "red");
    add::pipe({6, 0, 0}, {6, 0, 0}, 0.5, 0.2, 5, "gold");               // A == B: flat
    add::capsule({0, 4, 0}, {0, 6, 0}, 0.5);
    add::capsule({3, 4, 0}, {5, 4, 1}, 0.3, 8, "blue");
    add::capsule({6, 4, 0}, {6, 7, 0}, 0.4, 4, "gold");                 // k // 3 = 1 -> 3
    add::capsule({8, 4, 0}, {8, 4, 0}, 0.5, 12);                          // no length: a ball
    add::capsule({10, 4, 0}, {10, 3, 0}, 0.25, 13, "red");
    add::arrow({0, 8, 0}, {2, 9, 1});
    add::arrow({3, 8, 0}, {3, 11, 0}, 0.1, "red", 8, 0.4);
    add::arrow({5, 8, 0}, {5, 8, 0});                                     // nothing
    add::arrow({6, 8, 0}, {7, 8, 0}, 0.05, "blue", 5, 1.0);
    save_case();
}

CASE(helices) {
    add::helix({0, 0, 0}, 1.0, 0.5, 3);
    add::helix({4, 0, 0}, 0.5, 0.2, 1.5, 40, 0.05, 6, "red", {1, 0, 0});
    add::helix({0, 4, 0}, 2.0, 1.0, 0.5, 20, 0.3, 5, "blue", {1, 1, 0});
    add::helix({8, 0, 0}, 1.0, -0.5, 2, 30, 0.1, 4, "gold", {0, 0, 1});
    save_case();
}

// -- the helpers -------------------------------------------------------------------

CASE(round_helpers) {
    auto g = add::detail::revolve_grid({0, 0, 0}, {0, 1, 0}, {{1.0, 0.0}, {1.5, 1.0}, {0.5, 2.0}}, 6);
    record(g.second);
    for (const Points& row : g.first) record(row);
    g = add::detail::revolve_grid({1, 2, 3}, {1, 1, 0}, {{1.0, 0.0}, {0.5, 1.0}}, 4, add::pi, 0.3);
    record(g.second);
    for (const Points& row : g.first) record(row);
    g = add::detail::revolve_grid({0, 0, 0}, {0, 0, 0}, {{1.0, 0.5}}, 3, 2 * add::pi, 0.1);
    record(g.second);
    for (const Points& row : g.first) record(row);
    g = add::detail::revolve_grid({0, 0, 0}, {0, 1, 0}, {}, 3);
    record(g.second);
    record((long long)g.first.size());
    auto VT = add::detail::icosphere_grid(1);
    record(VT.first);
    record_faces(VT.second);
    VT = add::detail::icosphere_grid(0);
    record(VT.first);
    record_faces(VT.second);
    add::Mesh M = add::detail::tube_body({0, 0, 0}, {1, 2, 0}, 0.5, 0.25, 5, "red", true, false);
    save_mesh(M, "tube");
    M = add::detail::tube_body({0, 0, 0}, {0, 0, 0}, 0.5, 0.25, 5, "red", true, true);
    record((long long)M.V.size());
    record((long long)M.F.size());
}

// -- revolve (needs fix_normals: section 50) ------------------------------------------

#if WITH_50
static Point2 vase(double t) { return {1 + 0.4 * std::sin(3 * t), t}; }

CASE(revolve_basic) {
    add::revolve(vase, {0, 0, 0}, {0, 1, 0}, 0, 4, 60, 40, "teal");
    add::revolve(vase, {4, 0, 0}, {5, 1, 0}, 0, 2, 8, 6);
    add::revolve([](double t) { return Point2{0.5, t}; }, {8, 0, 0}, {8, 1, 0}, 0, 1, 1, 5, "red");
    add::revolve([](double t) { return Point2{std::sin(t), -std::cos(t)}; }, {0, 0, 5}, {0, 1, 5}, 0, add::pi, 10,
                 12, "gold");
    add::revolve([](double t) { return Point2{1 - t, t}; }, {3, 0, 5}, {3, 2, 5}, 0, 1, 4, 8, "blue");
    add::revolve([](double t) { return Point2{t, 0.3 * t}; }, {6, 0, 5}, {6, 1, 5}, 0, 1, 3, 7, "navy");
    add::revolve([](double t) { return Point2{1.0, -t}; }, {9, 0, 5}, {9, 1, 5}, 0, 2, 2, 6);   // drawn downwards
    add::revolve([](double t) { return Point2{1.0, t}; }, {12, 0, 5}, {12, 1, 5}, 0, 1, 2, 3, "red",
                 2 * add::pi - 1e-13);
    save_case();
}

CASE(revolve_defaults) {
    add::revolve([](double t) { return Point2{0.5 + 0.2 * t, t}; });
    save_case();
}

CASE(revolve_colors) {
    add::revolve(vase, {0, 0, 0}, {0, 1, 0}, 0, 4, 12, 10, [](double t, double) { return add::hsv(t / 4.0); });
    add::revolve(vase, {4, 0, 0}, {4, 1, 0}, 0, 4, 6, 8, [](double, double a) { return a < add::pi ? "red" : "white"; });
    add::revolve(vase, {8, 0, 0}, {8, 1, 0}, 0, 2, 4, 5, [](double, double) { return add::random_color(); });
    save_case();
}

CASE(revolve_wedges) {
    add::revolve(vase, {0, 0, 0}, {0, 1, 0}, 0, 4, 12, 10, "teal", add::pi);
    add::revolve(vase, {4, 0, 0}, {4, 1, 0}, 0, 4, 6, 8, [](double, double a) { return add::hsv(a / 6.0); }, 1.5);
    add::revolve([](double t) { return Point2{t, t}; }, {8, 0, 0}, {8, 1, 0}, 0, 1, 3, 4, "gold", add::pi / 2);
    add::revolve(vase, {0, 0, 5}, {0, 1, 5}, 0, 4, 6, 6, [](double, double) { return add::random_color(); }, 4.0);
    add::revolve([](double t) { return Point2{1.0, -t}; }, {4, 0, 5}, {4, 1, 5}, 0, 1, 2, 3, "red", 1.0);
    save_case();
}

CASE(revolve_no_caps) {
    add::revolve(vase, {0, 0, 0}, {0, 1, 0}, 0, 4, 10, 12, "teal", 2 * add::pi, false);
    add::revolve(vase, {4, 0, 0}, {4, 1, 0}, 0, 4, 10, 12, "red", add::pi, false);
    add::revolve(vase, {8, 0, 0}, {8, 1, 0}, 0, 4, 5, 6, [](double, double a) { return add::hsv(a); }, 2.0, false);
    save_case();
}

CASE(revolve_list) {
    // A list of [radius, height] points is spun as it is (``steps`` is not used).
    Profile pts{{0.0, 0.0}, {1.0, 0.0}, {1.2, 0.5}, {0.8, 1.0}, {0.9, 1.5}, {0.0, 1.6}};
    add::revolve(pts, {0, 0, 0}, {0, 1, 0}, 0, 1, 40, 12, "teal");
    add::revolve(pts, {3, 0, 0}, {3, 2, 0}, 0.5, 2.5, 0, 7, [](double t, double a) { return add::hsv(t + a); });
    add::revolve(Profile(pts.begin() + 1, pts.begin() + 5), {6, 0, 0}, {6, 1, 0}, 0, 1, 3, 8, "red", add::pi);
    add::revolve(Profile(pts.begin() + 1, pts.begin() + 4), {9, 0, 0}, {9, 1, 0}, 0, 1, 2, 5, "blue", 2 * add::pi,
                 false);
    save_case();
}

CASE(revolve_bad) {
    raises([] { add::revolve([](double t) { return Point2{1.0, t}; }, {0, 0, 0}, {0, 1, 0}, 0, 1, -1); });
    raises([] { add::revolve(Profile{}, {0, 0, 0}, {0, 1, 0}, 0, 1, -1); });
    save_case();
}

CASE(spin3D_case) {
    add::spin3D({0, 0, 0}, {0, 2, 0}, vase, 0, 4, 20, 16, "gold");
    add::spin3D({3, 0, 0}, {4, 1, 1}, [](double t) { return Point2{0.5 + 0.1 * t, t}; }, 0, 1, 3, 5, {10, 20, 30});
    save_case();
}
#endif

// -- axes (needs glyph: section 75) ----------------------------------------------------

#if WITH_75
CASE(axes_default) {
    add::axes();
    save_case();
}

CASE(axes_custom) {
    add::axes({1, 2, 3}, 2.5, 0.05);
    add::axes({0, 0, 0}, -1.0, 0.1);
    save_case();
}
#endif

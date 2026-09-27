#include "parity.hpp"

using add::Point;
using add::Point2;
using add::Points;
using add::Profile;

static Point saddle(double u, double v) { return {u, u * u - v * v, v}; }

static Point torus_uv(double u, double v) {
    return {(2 + 0.5 * std::cos(u)) * std::cos(v), 0.5 * std::sin(u), (2 + 0.5 * std::cos(u)) * std::sin(v)};
}

// A small open mesh whose faces share vertices: a triangle, a quad, a pentagon, and an
// edge (0-2) that belongs to three faces.
static add::Mesh shared_mesh() {
    add::Mesh M;
    for (const Point& p : Points{{0, 0, 0}, {1, 0, 0}, {1, 1, 0.2}, {0, 1, 0}, {2, 0, 0.3}, {2, 1, 0}, {0.5, 2, 0.5},
                                 {1.5, 2.5, 0.1}, {2.5, 2, 0}})
        M.add_vertex(p);
    M.add_face({0, 1, 2}, "red");
    M.add_face({0, 2, 3}, "blue");
    M.add_face({1, 4, 5, 2}, "gold");
    M.add_face({2, 5, 8, 7, 6}, {10, 20, 30});
    M.add_face({2, 0, 6}, "teal");
    return M;
}

// -- parametric surfaces -------------------------------------------------------------

CASE(parametric_basic) {
    add::parametric(saddle, -1, 1, 6, -1, 1, 4);
    add::parametric(saddle, 2, 3, 3, -1, 1, 3, "red", false, false, true);
    add::parametric(torus_uv, 0, 2 * add::pi, 12, 0, 2 * add::pi, 16, "gold", true, true);
    add::parametric(torus_uv, 0, 2 * add::pi, 8, 0, 2 * add::pi, 5, "blue", true);
    add::parametric(torus_uv, 0, 2 * add::pi, 5, 0, 2 * add::pi, 7, "teal", false, true, true);
    add::parametric(saddle, 5, 6, 1, 0, 1, 1, {0.5, 0.5, 0.5});
    add::parametric(saddle, 7, 8, 2, 0, 1, 3, [](double, double v) { return add::transparent("sky", v); });
    save_case();
}

CASE(parametric_colors) {
    add::parametric(saddle, -1, 1, 5, -1, 1, 5, [](double u, double v) { return u * v > 0 ? "red" : "white"; });
    add::parametric(saddle, 2, 3, 4, 0, 1, 3, [](double u, double v) { return add::hsv(u + v); });
    add::parametric(saddle, 4, 5, 3, 0, 1, 2, "green");
    add::parametric(torus_uv, 0, 2 * add::pi, 6, 0, 2 * add::pi, 4, [](double, double) { return add::random_color(); },
                    true, true);
    save_case();
}

CASE(parametric_thick) {
    add::parametric(saddle, -1, 1, 4, -1, 1, 4, "red", false, false, false, 0.2);
    add::parametric(saddle, 2, 3, 3, 0, 1, 3, "blue", false, false, false, 0.0, true);
    add::parametric(saddle, 4, 5, 3, 0, 1, 3, "gold", false, false, false, -0.1, true);
    add::parametric(torus_uv, 0, 2 * add::pi, 6, 0, 2 * add::pi, 8, "teal", true, true, false, 0.1);
    add::parametric(saddle, 6, 7, 2, 0, 1, 2, [](double, double v) { return add::hsv(v); }, false, false, true, 0.3);
    save_case();
}

CASE(parametric_empty) {
    try {
        add::parametric(saddle, 0, 1, 0, 0, 1, 3, "red", true);
    } catch (const std::exception&) {
        record("raises");
    }
    save_case();
}

// -- two_sided and solidify ------------------------------------------------------------

CASE(two_sided_meshes) {
    add::Mesh M = shared_mesh();
    save_mesh(add::two_sided(M), "a");
    add::parametric(saddle, -1, 1, 2, -1, 1, 2, "red");
    save_mesh(add::two_sided(), "scene");
    save_mesh(add::two_sided(add::Mesh()), "empty");
    save_case();
}

CASE(two_sided_textured) {
    add::Mesh M;
    for (const Point& p : Points{{0, 0, 0}, {1, 0, 0}, {1, 1, 0}, {0, 1, 0}, {2, 0, 0}, {2, 1, 0}}) M.add_vertex(p);
    add::Color wood(255, 255, 255);
    wood.image = "wood.png";
    M.add_face({0, 1, 2, 3}, wood, {{0, 0}, {1, 0}, {1, 1}, {0, 1}});
    M.add_face({1, 4, 2}, "red");
    M.add_face({4, 5, 2}, wood, {{0.5, 0.25}, {1, 0.125}, {0.75, 1}});
    add::Mesh out = add::two_sided(M);
    add::obj(parity::current() + ".obj", out);
    save_mesh(out);
}

CASE(solidify_meshes) {
    add::Mesh M = shared_mesh();
    save_mesh(add::solidify(M), "a");
    save_mesh(add::solidify(M, 0.3, false), "b");
    save_mesh(add::solidify(M, -0.2), "c");
    add::box({0, 0, 0}, 1);                                            // closed: no border wall
    save_mesh(add::solidify(), "scene");
    add::Mesh Z;                                                       // a face with no area
    for (const Point& p : Points{{0, 0, 0}, {1, 0, 0}, {2, 0, 0}}) Z.add_vertex(p);
    Z.add_face({0, 1, 2}, "red");
    Z.add_vertex({5, 5, 5});                                           // a vertex of no face
    save_mesh(add::solidify(Z, 0.5), "flat");
    save_case();
}

// -- sweeps, curves, extrusions, lofts, ribbons -------------------------------------------

static const Profile square{{-0.5, -0.5}, {0.5, -0.5}, {0.5, 0.5}, {-0.5, 0.5}};
static const Profile tri{{0.0, 0.0}, {0.4, 0.0}, {0.0, 0.3}};

CASE(sweeps) {
    add::sweep(square, [](double t) { return Point{0, t, 0}; }, 0, 3, 6, "orange");
    add::sweep(square, [](double t) { return Point{2 + std::cos(t), std::sin(t), 0.3 * t}; }, 0, 4, 12, "red", false,
               [](double t) { return 1 - 0.5 * t; }, add::pi);
    add::sweep(tri, [](double t) { return Point{std::cos(t) * 3, 0, std::sin(t) * 3 + 8}; }, 0, 2 * add::pi, 16,
               "blue", true);
    add::sweep(square, [](double t) { return Point{t, 0, 5}; }, 0, 1, 3, "gold", false, 2,
               [](double t) { return t * t; }, false);
    add::sweep(tri, [](double t) { return Point{t, t * t, -3}; }, -1, 1, 5, add::DEFAULT_COLOR, true, add::Scalar(),
               1.5);
    add::sweep(square, [](double t) { return Point{5, t, t * t}; }, 0, 2, 4, "teal", false, 0.5);
    add::sweep(tri, [](double) { return Point{9, 0, 0}; }, 0, 1, 2, "red");   // the path stands still
    add::sweep(tri, [](double t) { return Point{std::sin(3 * t), t, -6}; });
    save_case();
}

CASE(sweep_colors) {
    add::sweep(square, [](double t) { return Point{0, t, 0}; }, 0, 3, 5,
               [](double t, int j) { return add::hsv(t / 3.0 + j / 8.0); });
    add::sweep(tri, [](double t) { return Point{2, t, std::sin(t)}; }, 0, 2, 4,
               [](double, int j) { return j < 0 ? "black" : "white"; });
    add::sweep(square, [](double t) { return Point{4 + std::cos(t), 0, std::sin(t)}; }, 0, 2 * add::pi, 6,
               [](double, int) { return add::random_color(); }, true);
    add::sweep(tri, [](double t) { return Point{7, t, 0}; }, 0, 1, 3, [](double, int) { return add::random_color(); },
               false, add::Scalar(), add::Scalar(), false);
    save_case();
}

CASE(sweep_empty) {
    try {
        add::sweep(square, [](double t) { return Point{0, t, 0}; }, 0, 1, 0, "red", true);
    } catch (const std::exception&) {
        record("raises");
    }
    save_case();
}

CASE(curves) {
    add::curve([](double t) { return Point{std::cos(t), t / 4.0, std::sin(t)}; }, 0, 2 * add::pi, 30);
    add::curve([](double t) { return Point{t, std::sin(t), 0}; }, 0, 3, 12, 6, 0.2, "red");
    add::curve([](double t) { return Point{3 + std::cos(t), 0, std::sin(t)}; }, 0, 2 * add::pi, 16, 8, 0.1, "blue",
               true);
    add::curve([](double t) { return Point{t, 2, 0}; }, 0, 2, 5, 5, [](double t) { return 0.1 + 0.1 * t; },
               [](double t, double a) { return std::fmod(t + a, 1.0) < 0.5 ? "red" : "white"; });
    add::curve([](double t) { return Point{t, 3, std::cos(t)}; }, 0, 2, 4, 4, 0.2,
               [](double, double) { return add::random_color(); });
    add::curve([](double t) { return Point{6 + std::cos(t), 3, std::sin(t)}; }, 0, 2 * add::pi, 6, 3,
               [](double t) { return 0.1 + 0.02 * t; }, [](double, double) { return add::random_color(); }, true);
    add::curve([](double t) { return Point{t, 5, 0}; }, 0, 1, 1, 3, 0.1, "gold");
    save_case();
}

CASE(extrusions) {
    Profile star = add::profile_star(5, 1.0, 0.45);
    add::extrude(star, {0, 4, 0}, "gold", 20, add::pi, [](double t) { return 1 - 0.6 * t; });
    add::extrude(square, {1, 1, 0}, "red", 1, 0.0, 1.0, {4, 0, 0});
    add::extrude(square, {0, 0, 2}, "blue", 0, 0.0, 1.0, {8, 0, 0});
    add::extrude(square, {0, 2, 0}, "teal", 3, [](double t) { return 2 * t; }, 0.5, {12, 0, 0}, false);
    add::extrude(square, {0, 2, 0}, [](double, int j) { return j == 1 ? "red" : (j >= 0 ? "white" : "black"); }, 4,
                 0.0, 1.0, {16, 0, 0});
    add::extrude(tri);
    add::extrude(tri, {0, -1, 0}, "navy", 2, 0.5, 2.0, {0, 0, 5});
    save_case();
}

static Points section(double y, double r, int k = 6, double phase = 0.0) {
    Points out;
    for (int i = 0; i < k; ++i)
        out.push_back({std::cos(2 * add::pi * i / k + phase) * r, y, std::sin(2 * add::pi * i / k + phase) * r});
    return out;
}

static Points shifted(const Points& ps, double dx, double dz) {
    Points out;
    for (const Point& p : ps) out.push_back({p[0] + dx, p[1], p[2] + dz});
    return out;
}

CASE(lofts) {
    add::loft({section(0, 1.0), section(1, 0.6), section(2, 0.9)}, "teal");
    std::vector<Points> s2, s3, s4;
    for (int y = 0; y < 4; ++y) s2.push_back(shifted(section(y, 0.5 + 0.1 * y), 4, 0));
    add::loft(s2, "red", true);
    for (int y = 0; y < 3; ++y) s3.push_back(shifted(section(y, 0.7, 5, 0.2 * y), 8, 0));
    add::loft(s3, "blue", false, false);
    for (int y = 0; y < 3; ++y) s4.push_back(shifted(section(y, 0.8, 4), 0, 4));
    add::loft(s4, "gold", false, true, true);
    add::loft({section(0, 1.0, 3), section(-1, 1.0, 3)});
    save_case();
}

CASE(loft_empty) {
    try {
        add::loft({}, "red");
    } catch (const std::exception&) {
        record("raises");
    }
    save_case();
}

CASE(ribbons) {
    add::ribbon([](double t) { return Point{std::cos(t) * 2, 0.2 * t, std::sin(t) * 2}; }, 0, 2 * add::pi, 24, 0.5);
    add::ribbon([](double t) { return Point{t, 0, 3}; }, 0, 4, 8, 0.3, "red", false, add::pi);
    add::ribbon([](double t) { return Point{std::cos(t) * 2 + 6, 0, std::sin(t) * 2}; }, 0, 2 * add::pi, 20, 0.4,
                "blue", true, [](double t) { return 2 * add::pi * t; });
    add::ribbon([](double t) { return Point{t, 1, 6}; }, 0, 3, 6, 0.5, "gold", false, add::Scalar(), 0.1);
    add::ribbon([](double t) { return Point{std::cos(t) + 10, std::sin(t), 0}; }, 0, 2 * add::pi, 12, 0.2, "teal",
                true, add::Scalar(), -0.05);
    save_case();
}

CASE(circles) {
    add::circle({0, 0, 0}, {0, 1, 0}, 1.0);
    add::circle({2, 0, 0}, {3, 1, 0}, 0.5, 6, "red");
    add::circle({4, 0, 0}, {0, 0, 0}, 0.5, 5, "blue");
    add::circle({6, 0, 0}, {6, 0, 0}, 0.5, 3, {0.1, 0.2, 0.3});
    save_case();
}

// -- the helpers -------------------------------------------------------------------

CASE(surface_helpers) {
    add::Mesh M = shared_mesh();
    record(add::detail::vertex_normals(M));
    for (const add::Face& f : M.F) record(add::detail::face_normal(M, f));
    record(add::detail::face_normal(M, {}));
    for (const add::detail::BorderEdge& e : add::detail::boundary_edges(M)) {
        record(std::to_string(e.a) + " " + std::to_string(e.b));
        record(e.color);
    }
    add::Mesh Z;
    Z.add_vertex({0, 0, 0});
    Z.add_vertex({1, 1, 1});
    Z.add_face({0, 1}, "red");
    record(add::detail::vertex_normals(Z));
    record((long long)add::detail::boundary_edges(Z).size());
}

CASE(rmf_and_sweep_profile) {
    Points path{{0, 0, 0}, {1, 0, 0}, {2, 1, 0}, {2, 2, 1}, {2, 2, 1}, {1, 3, 2}, {0, 3, 2}};
    auto TN = add::detail::rmf(path);
    record(TN.first);
    record(TN.second);
    auto TN2 = add::detail::rmf(path, true);
    record(TN2.first);
    record(TN2.second);
    auto TN3 = add::detail::rmf({{1, 2, 3}});
    record(TN3.first);
    record(TN3.second);
    auto TN4 = add::detail::rmf({{1, 2, 3}, {1, 2, 3}, {1, 2, 4}}, true);
    record(TN4.first);
    record(TN4.second);
    const std::pair<add::Scalar, add::Scalar> options[] = {
        {add::Scalar(), add::Scalar()},
        {2.0, add::Scalar()},
        {[](double t) { return 1 + t; }, 0.5},
        {0.5, [](double t) { return t * t; }}};
    for (const auto& st : options) {
        auto P = add::detail::sweep_profile(path, TN.first, TN.second, {{1, 0}, {0, 1}, {-1, -0.5}}, st.first, st.second);
        for (const Points& row : P) record(row);
    }
    auto P = add::detail::sweep_profile({{0, 0, 0}}, {{0.0, 0.0, 1.0}}, {{1.0, 0.0, 0.0}}, {{1, 2}}, add::Scalar(), 3.0);
    record(P[0]);
    try {
        add::detail::rmf({});
    } catch (const std::exception&) {
        record("raises");
    }
}

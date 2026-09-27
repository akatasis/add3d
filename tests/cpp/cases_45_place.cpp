// Parity cases for _cpp/45_place.hpp: aim, ground, align, random_points, scatter, along
// (see cases_45_place.py).
#include "parity.hpp"

using add::Color;
using add::Mesh;
using add::Point;

static const std::vector<Color> SIX = {"red", Color(10, 200, 30), add::transparent("sky", 0.4), "#123456",
                                       Color(250, 250, 5), "navy"};

static Mesh cube(Point lo = {-0.5, -0.25, -0.75}, Point hi = {0.5, 0.75, 1.25}, const std::vector<Color>& colors = {}) {
    Mesh M;
    for (int k = 0; k < 8; ++k) M.add_vertex({k & 1 ? hi[0] : lo[0], k & 2 ? hi[1] : lo[1], k & 4 ? hi[2] : lo[2]});
    std::vector<add::Face> faces = {{0, 4, 6, 2}, {1, 3, 7, 5}, {0, 1, 5, 4}, {2, 6, 7, 3}, {0, 2, 3, 1}, {4, 5, 7, 6}};
    for (size_t i = 0; i < faces.size(); ++i) M.add_face(faces[i], colors.empty() ? add::DEFAULT_COLOR : colors[i]);
    return M;
}

static Point path(double t) { return {3 * std::cos(t), t, 3 * std::sin(t)}; }

CASE(p_aim) {
    Mesh M = cube({-0.5, -0.25, -0.75}, {0.5, 0.75, 1.25}, SIX);
    save_mesh(add::aim(M, {1, 1, 0}), "diag");
    save_mesh(add::aim(M, {0, 3, 0}), "same");
    save_mesh(add::aim(M, {0, -2, 0}), "opposite");
    save_mesh(add::aim(M, {0, 0, 1}, {1, 0, 0}, {0.5, 0.5, 0.5}), "pivot");
    save_mesh(add::aim(M, {1e-13, -1, 0}), "nearly_opposite");
    save_mesh(add::aim(M, {1, 0, 0}, {1, 0, 0}), "x_x");
    save_mesh(add::aim(M, {-1, 0, 0}, {1, 0, 0}, {1, 1, 1}), "x_minus_x");
    save_mesh(add::aim(M, {0, 0, 0}), "zero");
    save_mesh(add::aim(M, add::direction({1, 2, 3}, {-2, 0.5, 4}), {0, 0, 1}, {1, 2, 3}), "direction");
}

CASE(p_ground_align) {
    Mesh M = cube({-0.5, -0.25, -0.75}, {0.5, 0.75, 1.25}, SIX);
    save_mesh(add::ground(M), "ground");
    save_mesh(add::ground(M, 2.5), "ground_y");
    save_mesh(add::align(M), "align");
    save_mesh(add::align(M, {5, 0, 5}), "align_at");
    save_mesh(add::align(M, {1, 2, 3}, {-1, -1, -1}), "corner");
    save_mesh(add::align(M, {1, 2, 3}, {1, 0, 1}), "max");
    save_mesh(add::align(M, {0, 0, 0}, {0.5, -0.5, 0}), "fractions");
    save_mesh(add::ground(Mesh()), "empty");
}

CASE(p_random_points) {
    record(add::random_points(4, {-1, 0, -2}, {1, 1, 2}, 1));
    record(add::random_points(3, {0, 0, 0}, {10, 5, 10}));
    record(add::random_points(3, {-5, 0, -5}, {5, 0, 5}, 2, [](double x, double z) { return std::sin(x) * std::cos(z); }));
    record(add::random_points(0, {0, 0, 0}, {1, 1, 1}, 3));
    record(add::random_points(2, {1, 1, 1}, {0, 0, 0}, 0));
    record(add::random_points(2, {1, 1, 1}, {3, 3, 3}, -7));
    record(add::random());
}

CASE(p_scatter) {
    Mesh M = cube({-0.5, -0.25, -0.75}, {0.5, 0.75, 1.25}, SIX);
    add::Points pts = {{0, 0, 0}, {3, 0, 1}, {-2, 1, 4}};
    save_mesh(add::scatter(M, pts, 5), "seed");
    save_mesh(add::scatter(M, pts, 5, false, {0.5, 1.5}), "nospin");
    save_mesh(add::scatter(M, pts, std::nullopt, true, {0.8, 1.2}, {1, 0, 0}), "global");
    save_mesh(add::scatter(M, pts, 9, true, {1.0, 1.0}), "scale1");
    save_mesh(add::scatter(M, {}, 9), "none");
    add::Points spots = add::random_points(5, {-10, 0, -10}, {10, 0, 10}, 1, [](double x, double z) { return 0.1 * x * z; });
    save_mesh(add::scatter(M, spots, 1, true, {0.7, 1.3}), "forest");
    record(add::random());
}

CASE(p_along) {
    Mesh M = cube({-0.5, -0.25, -0.75}, {0.5, 0.75, 1.25}, SIX);
    save_mesh(add::along(M, path, 6, 0, add::pi), "fn");
    save_mesh(add::along(M, path, 6, 0, 2 * add::pi, Point{1, 0, 0}, true), "closed");
    save_mesh(add::along(M, path, 5, 0, 1, std::nullopt), "upright");
    save_mesh(add::along(M, path, 4, 0, 2, Point{0, 1, 0}, false, 0.5), "scale");
    save_mesh(add::along(M, path, 4, 0, 2, Point{0, 1, 0}, false, [](double t) { return 1 + t; }), "scale_fn");
    save_mesh(add::along(M, path, 4, -1, 2, std::nullopt, true, [](double t) { return 0.5 + t * t; }), "upright_scale_fn");
    save_mesh(add::along(M, path, 1), "one");
    save_mesh(add::along(M, path, 0), "zero");
    save_mesh(add::along(M, path, 3, 1, 1), "same_t");
    add::Points pts = {{0, 0, 0}, {2, 0, 0}, {2, 2, 0}, {0, 2, 1}};
    save_mesh(add::along(M, pts, 0), "list");
    save_mesh(add::along(M, pts, 99, 5, 7, Point{0, 0, 1}, true, 0.5), "list_closed");
    save_mesh(add::along(M, pts, 0, 0, 1, std::nullopt, false, [](double t) { return 2 - t; }), "list_upright");
    save_mesh(add::along(M, add::Points{{0, 0, 0}, {0, 0, 0}, {1, 0, 0}}, 0), "list_repeat");
    save_mesh(add::along(M, add::Points{{1, 2, 3}}, 0), "list_one");
    save_mesh(add::along(M, add::Points{}, 0), "list_empty");
}

//: The path is called in add.py's order: every point, then t + h and t - h.
CASE(p_along_calls) {
    std::vector<double> calls;
    auto traced = [&calls](double t) {
        calls.push_back(t);
        return Point{t, t * t, 1.0};
    };
    add::along(cube(), traced, 3, 0.5, 1.5);
    record(calls);
}


CASE(p_random) {
    Mesh M = cube({-0.5, -0.25, -0.75}, {0.5, 0.75, 1.25}, SIX);
    for (long long seed = 0; seed < 10; ++seed) {
        add::Random r(seed);
        add::Points pts;
        long long count = r.randint(1, 7);
        for (long long i = 0; i < count; ++i) {
            double x = r.uniform(-3, 3);
            double y = r.uniform(-3, 3);
            double z = r.uniform(-3, 3);
            pts.push_back({x, y, z});
        }
        bool closed = r.randint(0, 1) == 1;
        Point ax;
        for (int a = 0; a < 3; ++a) ax[a] = r.uniform(-1, 1);
        double s = r.uniform(0.5, 1.5);
        std::string tag = std::to_string(seed);
        save_mesh(add::along(M, pts, 0, 0, 1, ax, closed, s), "along" + tag);
        Point d;
        for (int a = 0; a < 3; ++a) d[a] = r.uniform(-1, 1);
        save_mesh(add::aim(M, d, ax, pts[0]), "aim" + tag);
        save_mesh(add::aim(M, {-ax[0], -ax[1], -ax[2]}, ax), "aim_back" + tag);
        Point anchor;
        for (int a = 0; a < 3; ++a) anchor[a] = (double)r.randint(-1, 1);
        save_mesh(add::align(M, pts.back(), anchor), "align" + tag);
        bool spin = r.randint(0, 1) == 1;
        save_mesh(add::scatter(M, pts, seed, spin, {0.5, 2.0}, ax), "scatter" + tag);
    }
}

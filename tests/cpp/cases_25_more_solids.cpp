#include "parity.hpp"

using add::Color;
using add::Point;
using add::Point2;
using add::Points;
using add::Profile;

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

static Points shift(const Points& pts, double dx, double dy, double dz) {
    Points out;
    for (const Point& p : pts) out.push_back({p[0] + dx, p[1] + dy, p[2] + dz});
    return out;
}

static Point lorenz(const Point& p) {
    double x = p[0], y = p[1], z = p[2];
    return {10 * (y - x), x * (28 - z) - y, x * y - 8.0 / 3 * z};
}

static std::string joined(const std::vector<long long>& xs) {
    std::string s;
    for (size_t i = 0; i < xs.size(); ++i) s += (i ? " " : "") + std::to_string(xs[i]);
    return s;
}

static std::string face_sizes(const add::Mesh& M) {
    std::string s;
    for (size_t i = 0; i < M.F.size(); ++i) s += (i ? " " : "") + std::to_string(M.F[i].size());
    return s;
}

// -- the helpers -------------------------------------------------------------------------

CASE(ground_frames) {
    const Point dirs[][2] = {{{1, 0, 0}, {0, 1, 0}}, {{0, 0, 2}, {0, 1, 0}}, {{1, 2, 3}, {0, 1, 0}},
                             {{0, 1, 0}, {0, 1, 0}}, {{0, -3, 0}, {0, 1, 0}}, {{0, 0, 0}, {0, 1, 0}},
                             {{1, 1, 0}, {0, 0, 1}}, {{2, 0, 0}, {1, 0, 0}}, {{1, 0, 0}, {0, 0, 0}},
                             {{1, 0, 0}, {0, 5, 1}}};
    for (const auto& d : dirs)
        for (const Point& vec : add::detail::ground_frame(d[0], d[1])) record(vec);
    for (const Point& vec : add::detail::ground_frame({0.3, -0.2, 0.9})) record(vec);
}

CASE(local_meshes) {
    add::box({0.5, 0.25, -1}, 1, "red");
    add::cuboid({2, 0, 0}, {1, 2, 0.5}, "blue");
    add::Mesh M = add::layer();
    std::array<Point, 3> fr = add::detail::ground_frame({1, 0, 1});
    save_mesh(add::detail::local_mesh(M, {1, 2, 3}, fr[0], fr[1], fr[2]), "a");
    save_mesh(add::detail::local_mesh(M, {0, 0, 0}, {0, 0, 1}, {1, 0, 0}, {0, 1, 0}), "b");
    save_mesh(add::detail::local_mesh(M, {-1, 0.5, 2}, {0.5, 0.1, 0}, {0, 2, 0}, {0.3, 0, -1}), "c");
}

CASE(hollow_prisms) {
    Profile outer = add::profile_gear(8, 1.0);
    Profile inner = add::profile_circle(0.4, (int)outer.size());
    save_mesh(add::detail::hollow_prism(outer, inner, 0.5, "red"), "a");
    save_mesh(add::detail::hollow_prism(outer, inner, 0.3, "blue", {1, 2, 3}, {1, 1, 0}), "b");
    save_mesh(add::detail::hollow_prism(add::profile_rect(2, 1), add::profile_rect(1, 0.5), -1.0, add::DEFAULT_COLOR,
                                        {0, 0, 0}, {0, 0, 1}),
              "c");
    save_mesh(add::detail::hollow_prism(add::profile_circle(1.0, 6), add::profile_circle(0.5, 6), 1.0, {10, 20, 30},
                                        {0, 0, 0}, {0, -1, 0}),
              "d");
}

CASE(tube_along_helper) {
    Points pts{{0, 0, 0}, {1, 0, 0}, {1.5, 1, 0}, {1.5, 1, 1}};
    save_mesh(add::detail::tube_along(pts, {0.1, 0.2, 0.15, 0.1}, 6, "red", false), "open");
    save_mesh(add::detail::tube_along(pts, {0.1, 0.1, 0.1, 0.1}, 5, "blue", true), "closed");
    add::ColorOf<int> cap_a = [](int) { return "gold"; };
    add::ColorOf<int> cap_b = [](int j) { return add::hsv(j / 4.0); };
    save_mesh(add::detail::tube_along(pts, {0.2, 0.1, 0.1, 0.05}, 4,
                                      add::detail::CellPaint([](int i, int j) { return add::hsv(0.1 * i + 0.2 * j); }),
                                      false, &cap_a, &cap_b),
              "painted");
}

CASE(set_order_helper) {
    std::vector<std::vector<long long>> special{{-1, -2, 0, 7, 15, 8, 16, 24, -1}, {}, {0, 0, 0, 0, 0},
                                                {5, 37, 69, 101}, {}, {1099511627776LL, 3, 1099511627779LL, 8}, {}};
    for (long long i = 100; i > 0; --i) special[1].push_back(i);
    for (long long i = 0; i < 400; i += 7) special[6].push_back(i);
    for (long long i = 3; i < 300; i += 5) special[6].push_back(i);
    add::Random rnd(3);
    for (int trial = 0; trial < 60; ++trial) {
        long long n = rnd.randint(0, 150);
        long long hi = rnd.choice(std::vector<long long>{5, 30, 200, 5000, 1000000000LL});
        long long lo = rnd.choice(std::vector<long long>{0, 0, -3, -100});
        std::vector<long long> added;
        for (long long q = 0; q < n; ++q) added.push_back(rnd.randint(lo, hi));
        special.push_back(added);
    }
    for (const std::vector<long long>& added : special) {
        record(joined(added));
        record(joined(add::detail::py_set_iteration_order(added)));
    }
}

// -- beams, boxes, arches, stairs --------------------------------------------------------------

CASE(beams) {
    add::beam({0, 0, 0}, {4, 3, 1}, 0.3, 0.5, "brown");
    add::beam({0, 0, 2}, {3, 0, 2}, 0.2);
    add::beam({0, 0, 4}, {0, 3, 4}, 0.25, std::nullopt, "red");        // straight up
    add::beam({2, 0, 4}, {2, -2, 4}, 0.25, 0.1, "blue");               // straight down
    add::beam({5, 0, 0}, {5, 1, 3}, 0.4, "gold");                      // the colour in the height's place
    add::beam({5, 0, 4}, {6, 2, 3}, 0.2, {255, 0, 128});
    add::beam({6, 0, 0}, {9, 1, 0}, 0.3, 0.6, "teal", {1, 0, 0});      // up along the beam
    add::beam({6, 2, 0}, {9, 2, 1}, 0.3, 0.2, "navy", {0, 0, 1});
    add::beam({0, 5, 0}, {2, 6, -1}, 0.3, "green", {0, 0, 1});
    add::beam({10, 0, 0}, {10, 0, 0}, 0.5, 0.5, "red");                // A == B
    add::beam({10, 2, 0}, {12, 2, 0}, 1, 2, {0.5, 0.25, 1.0});
    save_case();
}

CASE(rounded_boxes) {
    add::rounded_box({0, 0, 0}, {2, 1, 1.5}, 0.2);
    add::rounded_box({3, 0, 0}, 1.5, 0.3, 4, "red");                   // a number: a cube
    add::rounded_box({6, 0, 0}, {1, 2, 3}, 5.0, 3, "blue");            // r larger than half the smallest side
    add::rounded_box({0, 3, 0}, {1, 1, 1}, 0.0, 2, "gold");            // r = 0: a sharp box
    add::rounded_box({3, 3, 0}, {2, 0.5, 1}, 0.1, 1, "teal");          // k = 1
    add::rounded_box({6, 3, 0}, {1, 1, 2}, 0.25, 5, {0.2, 0.4, 0.6});
    add::rounded_box({0, 6, 0}, {1, 1, 1}, 0.5, 6, "navy");             // r = half: a ball
    add::rounded_box({3, 6, 0}, {-1, 1, 1}, 0.2, 3);                   // a negative size
    save_case();
}

CASE(rounded_box_bad) {
    raises([] { add::rounded_box({0, 0, 0}, {1, 1, 1}, 0.2, 0); });
    raises([] { add::rounded_box({0, 0, 0}, {1, 1, 1}, 0.2, -1); });
    save_case();
}

CASE(hemispheres) {
    add::hemisphere({0, 0, 0}, 1.0);
    add::hemisphere({3, 0, 0}, 0.5, 4, "red");
    add::hemisphere({6, 0, 0}, 0.8, 6, "blue", {0, -1, 0});             // a bowl
    add::hemisphere({0, 3, 0}, 0.7, 5, "gold", {1, 1, 0});
    add::hemisphere({3, 3, 0}, 1.0, 3, [](double, double a) { return add::hsv(a / 6.0); });
    add::hemisphere({6, 3, 0}, 0.5, 2, add::DEFAULT_COLOR, {0, 0, 2});
    add::hemisphere({9, 3, 0}, 0.5, 4, [](double t, double) { return t > 1.0 ? "white" : "red"; });
    save_case();
}

CASE(arches) {
    add::arch({0, 0, 0}, {4, 0, 0}, 2.0, 0.2);
    add::arch({0, 0, 2}, {3, 0, 2}, 3.0, 0.15, "red", 16, 6);
    add::arch({5, 0, 0}, {5, 0, 4}, 1.0, {0.4, 0.2}, "blue", 8);
    add::arch({0, 0, 6}, {2, 1, 7}, 1.5, {0.3, 0.1}, "gold", 12, 5, {0, 0, 1});
    add::arch({8, 0, 0}, {10, 0, 0}, 1.0, 0.1, {0.5, 0.2, 0.9}, 4, 3, {1, 1, 0});
    add::arch({8, 0, 4}, {11, 0, 4}, 1.5, 0.2, add::DEFAULT_COLOR, 1, 4);
    save_case();
}

CASE(arch_bad) {
    raises([] { add::arch({0, 0, 0}, {4, 0, 0}, 2.0, 0.2, "red", 0); });
    raises([] { add::arch({0, 0, 0}, {4, 0, 0}, 2.0, 0.2, "red", -1); });
    save_case();
}

CASE(stairs_case) {
    add::stairs({0, 0, 0}, 5, 1.0, 0.2, 0.3);
    add::stairs({3, 0, 0}, 3, 2.0, 0.5, 0.5, "red", {0, 0, 1});
    add::stairs({0, 0, 4}, 4, 1.5, 0.25, 0.4, "blue", {1, 0, 1});
    add::stairs({6, 0, 0}, 2, 1.0, 0.3, 0.3, "gold", {-1, 0, 0});
    add::stairs({0, 3, 0}, 3, 1.0, 0.2, 0.2, "teal", {0, 1, 0});       // straight up
    add::stairs({6, 3, 0}, 1, 0.5, 1.0, 1.0);
    add::stairs({9, 3, 0}, 0, 1.0, 0.2, 0.3);                          // no steps
    add::stairs({9, 0, 0}, -2, 1.0, 0.2, 0.3);
    add::stairs({0, 6, 0}, 3, 1.0, 0.3, 0.3, "navy", {1, -0.5, 0});
    save_case();
}

// -- machine parts and buildings ------------------------------------------------------------------

CASE(gears) {
    add::gear({0, 0, 0}, 12, 1.0, 0.3);
    add::gear({3, 0, 0}, 8, 0.8, 0.2, "gold", 0.3);
    add::gear({6, 0, 0}, 10, 1.0, 0.25, "red", std::nullopt, 0.4);
    add::gear({0, 3, 0}, 6, 0.5, 0.2, "blue", 0.1, 0.2, {0, 0, 1});
    add::gear({3, 3, 0}, 16, 1.2, 0.1, "silver", std::nullopt, 1e-10);  // a hole below EPS: none
    add::gear({6, 3, 0}, 3, 0.6, 0.4, {0.3, 0.3, 0.3}, 0.2, 0.3, {1, 1, 1});
    add::gear({9, 3, 0}, 12, 1.0, -0.3, "teal", std::nullopt, 0.5);    // a negative thickness
    save_case();
}

CASE(gear_no_teeth) {
    add::gear({9, 0, 0}, 0, 1.0, 0.3, "red");
    add::Mesh M = add::layer();
    record((long long)M.V.size());
    record(face_sizes(M));
    add::gear({9, 0, 0}, 0, 1.0, 0.3, "red", std::nullopt, 0.5);
    M = add::layer();
    record((long long)M.V.size());
    record(face_sizes(M));
}

CASE(wheels) {
    add::wheel({0, 0, 0}, 1.0, 0.3);
    add::wheel({3, 0, 0}, 0.8, 0.4, "red", {1, 0, 0}, 12);
    add::wheel({6, 0, 0}, 1.0, 0.2, "black", {0, 0, 1}, 24, 6);
    add::wheel({0, 3, 0}, 0.7, 0.3, "blue", {0, 1, 0}, 8, 3, "gold");
    add::wheel({3, 3, 0}, 1.0, 0.25, "navy", {1, 1, 0}, 30, 5, {200, 200, 200});
    add::wheel({6, 3, 0}, 0.5, 0.2, "teal", {0, 0, 1}, 5, 0, "red");   // k // 2 < 8
    add::wheel({9, 3, 0}, 0.4, 1.0, "red", {0, 0, 1}, 16, 4);          // the tyre wider than the wheel
    save_case();
}

CASE(roofs) {
    add::roof({0, 0, 0}, {4, 6}, 2);
    add::roof({6, 1, 0}, {3, 3}, 1.5, "red", 0.3);
    add::roof({0, 3, 6}, {2.5, 4}, 0.8, {0.6, 0.2, 0.1}, -0.2);
    save_case();
}

CASE(columns) {
    add::column({0, 0, 0}, 3.0, 0.3);
    add::column({2, 0, 0}, 2.0, 0.25, "white", 12);
    add::column({4, 0, 0}, 2.5, 0.2, "gold", 8, false);
    add::column({6, 1, 2}, 1.0, 0.5, add::DEFAULT_COLOR, 5, true);
    save_case();
}

CASE(bricks_plain) {
    add::bricks({0, 0, 0}, 4.0, 2.0);
    add::bricks({0, 0, 3}, 3.3, 1.2, {0.8, 0.3, 0.4}, "red", {1, 0, 0}, 0.02);
    save_case();
}

CASE(bricks_seeded) {
    add::bricks({0, 0, 0}, 5.0, 1.5, {1.0, 0.5, 0.5}, "brown", {1, 0, 0}, 0.05, 7);
    add::bricks({0, 0, 3}, 2.0, 1.0, {0.5, 0.25, 0.3}, {200, 100, 50}, {0, 0, 1}, 0.03, 1);
    add::bricks({0, 3, 0}, 2.0, 1.0, {0.5, 0.25, 0.3}, "gold", {1, 0, 0}, 0.03, 0);
    add::bricks({0, 5, 0}, 2.0, 1.0, {0.5, 0.25, 0.3}, "red", {1, 0, 0}, 0.03, -12);
    save_case();
}

CASE(bricks_colors) {
    add::bricks({0, 0, 0}, 4.0, 2.0, {1.0, 0.5, 0.5}, [](int i, int j) { return (i + j) % 2 ? "red" : "white"; });
    add::bricks({0, 3, 0}, 3.0, 1.0, {0.6, 0.3, 0.3}, [](int i, int j) { return add::hsv(i / 7.0 + j / 3.0); },
                {1, 0, 1}, 0.04, 5);
    add::bricks({0, 6, 0}, 2.0, 1.0, {0.5, 0.5, 0.5}, [](int, int) { return add::random_color(); });
    save_case();
}

CASE(bricks_directions) {
    add::bricks({1, 2, 3}, 2.0, 1.0, {0.5, 0.5, 0.5}, "brown", {0, 0, -1});
    add::bricks({0, 0, 0}, 2.0, 1.0, {0.5, 0.5, 0.5}, "gold", {0, 1, 0});          // straight up
    add::bricks({5, 0, 0}, 2.0, 0.2, {0.5, 0.5, 0.5}, "red");                     // int(0.2 / 0.5 + 0.5) = 0 rows
    add::bricks({5, 0, 5}, 0.0, 1.0);                                             // no length
    add::bricks({8, 0, 0}, 1.7, 0.74, {0.5, 0.25, 0.25}, "teal", {1, 0, 0}, 0.1); // 3.46 rows -> 3
    add::bricks({8, 0, 4}, 1.0, 0.5, {0.3, 0.5, 0.2}, "navy", {1, 0, 0}, 0.4);    // gaps wider than half a brick
    add::bricks({8, 3, 4}, 2.0, -1.0, {0.5, 0.5, 0.5}, "red");                    // negative height
    save_case();
}

CASE(bricks_bad) {
    raises([] { add::bricks({0, 0, 0}, 2.0, 1.0, {0.5, 0.0, 0.5}); });
    raises([] { add::bricks({0, 0, 0}, 2.0, std::nan(""), {0.5, 0.5, 0.5}); });
    raises([] { add::bricks({0, 0, 0}, 2.0, add::inf, {0.5, 0.5, 0.5}); });
    save_case();
}

CASE(trees_round) {
    add::tree({0, 0, 0}, 3);
    add::tree({4, 0, 0}, 2.5, "brown", "green", "round", 12, 1);
    add::tree({8, 0, 0}, 3, "brown", "lime", "round", 6, 2);
    add::tree({0, 0, 4}, 2, "brown", "green", "oak", 9);                // any other kind: round
    add::tree({4, 0, 4}, 2, {90, 60, 30}, "teal", "round", 30, 0);
    add::tree({8, 0, 4}, 1.5, "brown", "green", "round", -4, -3);
    save_case();
}

CASE(trees_pine) {
    add::tree({0, 0, 0}, 4, "brown", "green", "pine");
    add::tree({4, 0, 0}, 3, {100, 50, 0}, "teal", "pine", 6, 3);
    add::tree({8, 0, 0}, 2.5, "brown", "green", "pine", 0, 11);
    save_case();
}

CASE(trees_palm) {
    add::tree({0, 0, 0}, 4, "brown", "green", "palm");
    add::tree({4, 0, 0}, 3, "brown", "lime", "palm", 10, 5);
    add::tree({8, 1, 2}, 2, "gold", "green", "palm", 4, 99);
    save_case();
}

// -- pixels and height maps ------------------------------------------------------------------------

CASE(palette_table) {
    for (const auto& kv : add::PALETTE()) {
        record(kv.first);
        record(kv.second);
    }
}

static const std::vector<std::string> HEART{".r.r.", "rrrrr", ".rrr.", "..r.."};

CASE(pixels_basic) {
    add::pixels(HEART, 0.5);
    add::pixels({"#kw", "rgb", "yop", "cmn", "slt", "vdi", "a.x"}, 1.0, {5, 0, 0});   // every colour, one unknown
    add::pixels({"ab", "", "a  b"}, 0.25, {0, 5, 0}, add::PALETTE(), 3);
    add::pixels({"rr", "r"}, 1.0, {0, 0, 5}, add::PALETTE(), 2, "gold");
    save_case();
}

CASE(pixels_colors) {
    add::pixels({"xyx", "yzy"}, 1.0, {0, 0, 0}, {{"x", "red"}, {"y", {0, 0, 255}}});
    add::pixels({"█▓█", "▓ ▓", "ąčę"}, 0.5, {5, 0, 0}, {{"█", "black"}, {"▓", "grey"}, {"č", "red"}}, 1, "sky");
    add::pixels({"ab.c"}, 2.0, {0, 5, 0}, {}, 1);
    add::pixels({"rgb"}, 1.0, {0, 0, 5}, add::PALETTE(), 0);          // depth 0: nothing
    add::pixels({"", " ", ". ."}, 1.0);                                // nothing filled
    save_case();
}

CASE(pixels_bad) {
    raises([] { add::pixels({}); });
    save_case();
}

CASE(heightmaps) {
    std::vector<std::vector<double>> H;
    for (int i = 0; i < 6; ++i) {
        std::vector<double> row;
        for (int j = 0; j < 8; ++j) row.push_back((int)(3 + 2 * std::sin(i / 3.0) * std::cos(j / 3.0)));
        H.push_back(row);
    }
    add::heightmap(H, 0.5);
    add::heightmap({{1, 2, 3}, {0, 1, 2}}, 1.0, {5, 0, 0}, [](int, int j, int) { return j < 1 ? "sky" : "green"; });
    add::heightmap({{0.5, 1.5, 2.5}, {3.49, -1, 2.51}}, 0.25, {0, 0, 5}, "red");   // halves go to even
    add::heightmap({{0, 0}, {0, -2}}, 1.0, {5, 0, 5});                            // nothing
    add::heightmap({{2, 2, 2, 7}}, 0.3, {9, 0, 0}, [](int, int j, int) { return add::hsv(j / 7.0); });
    add::heightmap({{1, 2}, {2, 3, 4, 5}}, 1.0, {0, 5, 0});          // rows longer than the first: cut
    save_case();
}

CASE(heightmap_bad) {
    raises([] { add::heightmap({}); });
    raises([] { add::heightmap({{1, 2}, {}}); });
    raises([] { add::heightmap({{1, 2}, {3}}); });                   // a row shorter than the first
    raises([] { add::heightmap({{1, 2, 3}, {2, std::nan(""), 1}}); });
    raises([] { add::heightmap({{add::inf}}); });
    save_case();
}

// -- tubes through points ----------------------------------------------------------------------------

static const Points PTS{{0, 0, 0}, {1, 0.5, 0}, {2, 0, 0.5}, {3, 1, 1}, {3, 2, 0}};

CASE(polylines) {
    add::polyline(PTS);
    add::polyline(shift(PTS, 0, 3, 0), 0.2, 8, "red");
    add::polyline(shift(PTS, 5, 0, 0), [](double t) { return 0.05 + 0.2 * t; }, 6, "blue");
    add::polyline(shift(PTS, 0, 0, 4), 0.1, 5, "gold", true);                   // closed
    add::polyline(shift(PTS, 5, 3, 0), 0.15, 7, "teal", false, 2);              // smooth
    add::polyline(shift(PTS, 0, 6, 0), 0.1, 6, "navy", true, 1);                // closed and smooth
    add::polyline({{0, 0, 8}, {1, 0, 8}}, 0.1, 3);
    add::polyline({{0, 0, 9}}, 0.1);                                            // one point: nothing
    add::polyline({}, 0.1);
    add::polyline({{0, 0, 10}, {0, 0, 10}, {1, 0, 10}, {1, 0, 10}, {1, 1, 10}}, 0.1, 4, "red");   // repeats
    add::polyline({{5, 5, 5}, {6, 5, 5}, {6, 6, 5}}, 0.1, 4, "blue", false, -1); // smooth < 0: none
    save_case();
}

CASE(polyline_colors) {
    Points pts{{0, 0, 0}, {1, 1, 0}, {2, 0, 0}, {3, 1, 0}};
    add::polyline(pts, 0.2, 8, [](double t, double) { return add::hsv(t); });
    add::polyline(shift(pts, 0, 3, 0), 0.2, 6, [](double, double a) { return a < add::pi ? "red" : "white"; }, true);
    add::polyline(shift(pts, 0, 6, 0), [](double t) { return 0.1 + 0.1 * t; }, 5,
                  [](double t, double a) { return add::hsv(t + a / 10.0); }, false, 2);
    add::polyline(shift(pts, 5, 0, 0), 0.1, 4, [](double, double) { return add::random_color(); });
    add::polyline(shift(pts, 5, 3, 0), 0.1, 3, [](double t, double) { return add::transparent("sky", 0.25 + 0.5 * t); },
                  true, 1);
    save_case();
}

CASE(wireframes) {
    add::box({0, 0, 0}, 1, "red");
    add::Mesh M = add::layer();
    add::wireframe(M);
    add::wireframe(add::move(M, {2, 0, 0}), 0.05, 4, Color("blue"));
    add::wireframe(add::move(M, {4, 0, 0}), 0.02, 3, std::nullopt, false);
    add::Mesh S = add::make([] { add::icosphere({0, 3, 0}, 1.0, 1, [](const Point& d) { return d[1] > 0 ? "white" : "navy"; }); });
    add::wireframe(S, 0.02, 5);
    add::wireframe(add::Mesh());
    save_case();
}

CASE(wireframe_orders) {
    // Faces with scattered vertex numbers: the balls come in the order CPython's set gives them.
    add::Mesh M;
    for (int i = 0; i < 80; ++i) M.add_vertex({std::cos(i * 0.7) * (1 + i * 0.01), std::sin(i * 1.3), i * 0.05});
    M.add_face({70, 3, 41}, "red");
    M.add_face({41, 3, 12, 77}, "blue");
    M.add_face({12, 8, 40, 72}, "gold");
    M.add_face({64, 32, 0, 72}, "teal");
    M.add_face({79, 47, 15, 31, 63}, "pink");
    add::wireframe(M, 0.01, 3);
    add::wireframe(M, 0.02, 4, Color("white"));
    save_case();
}

CASE(wireframe_scene) {
    add::box({0, 0, 0}, 1, "red");
    add::tetrahedron({2, 0, 0}, 0.5, "blue");
    add::wireframe(add::scene(), 0.02, 4);
    save_case();
}

CASE(flows) {
    record(add::flow(lorenz, {1, 1, 1}, 0.01, 50));
    record(add::flow([](const Point& p) { return Point{-p[1], p[0], 0.1}; }, {1, 0, 0}, 0.1, 20));
    record(add::flow([](const Point&) { return Point{1, 2, 3}; }, {0.5, 0, -1}, 0.25, 3));
    record(add::flow(lorenz, {1, 1, 1}, 0.01, 0));
    record(add::flow([](const Point& p) { return Point{p[0] * p[1], -p[2], p[0] - p[1]}; }, {0.3, 0.2, 0.1}));
}

CASE(traces) {
    add::trace([](const Point& p) { return Point{-p[1], p[0], 0.2}; }, {1, 0, 0}, 0.1, 60);
    add::trace(lorenz, {1, 1, 1}, 0.01, 300, 0.2, 6, "red", 10);
    add::trace([](const Point& p) { return Point{-p[1], p[0], 0.1}; }, {2, 0, 3}, 0.2, 40,
               [](double t) { return 0.05 + 0.1 * t; }, 5, [](double t, double) { return add::hsv(t); }, 3);
    add::trace([](const Point&) { return Point{0, 0, 0}; }, {0, 5, 0}, 0.1, 10);          // standing still
    add::trace([](const Point& p) { return Point{0.2, 0.1 * p[0], 0}; }, {0, 8, 0});      // the defaults: 1000 steps
    add::trace([](const Point&) { return Point{1, 0, 0}; }, {0, 10, 0}, 0.5, 3, 0.1, 4, "blue", 5);   // one point
    save_case();
}

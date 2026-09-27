#include "parity.hpp"

using add::Point;
using add::Points;

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

// -- the helpers every shape is built with ------------------------------------------

CASE(add_grid_helper) {
    std::vector<Points> P;
    for (int i = 0; i < 3; ++i) {
        Points row;
        for (int j = 0; j < 4; ++j) row.push_back({(double)i, 0.5 * j * j, 0.25 * i * j});
        P.push_back(row);
    }
    add::Mesh M;
    for (bool wrap_u : {false, true})
        for (bool wrap_v : {false, true})
            for (bool flip : {false, true})
                add::detail::add_grid(M, P, flip ? add::Color("red") : add::Color(10, 20, 30), wrap_u, wrap_v, flip);
    add::detail::add_grid(M, P, add::detail::CellPaint([](int i, int j) { return add::hsv(0.1 * i + 0.05 * j); }),
                          false, true);
    add::detail::add_grid(M, P, add::detail::CellPaint([](int, int) { return add::random_color(); }), false, false,
                          true);
    add::detail::add_grid(M, {{{0, 0, 0}, {1, 0, 0}}}, "blue");       // one row: no cells
    save_mesh(M);
}

CASE(add_grid_empty) {
    add::Mesh M;
    raises([&] { add::detail::add_grid(M, {}, "red"); });
}

CASE(ring_fan_helpers) {
    add::detail::Frame fr = add::detail::frame({1, 2, 3});
    record(add::detail::ring({1, 2, 3}, fr.u, fr.v, 1.5, 5));
    record(add::detail::ring({0, 0, 0}, {1, 0, 0}, {0, 0, 1}, 2.0, 3, 0.4));
    record(add::detail::ring({0, 0, 0}, fr.u, fr.v, 1.0, 0));
    add::Mesh M;
    Points ring = add::detail::ring({0, 0, 0}, {1, 0, 0}, {0, 1, 0}, 1.0, 6);
    add::detail::fan(M, ring, {0, 0, 1}, "red");
    add::detail::fan(M, ring, {0, 0, -1}, "blue", true);
    add::detail::fan(M, ring, {0, 0, 2}, [](int i) { return add::hsv(i / 6.0); }, false, false);
    add::detail::fan(M, ring, {0, 0, -2}, [](int) { return add::random_color(); }, true, false);
    add::detail::fan(M, Points(ring.begin(), ring.begin() + 1), {0, 0, 3}, "gold");
    add::detail::fan(M, {}, {0, 0, 3}, "gold");
    save_mesh(M);
}

CASE(volume_helpers) {
    add::Mesh M;
    add::detail::add_grid(M, {add::detail::ring({0, 0, 0}, {1, 0, 0}, {0, 0, 1}, 1.0, 8),
                              add::detail::ring({0, 1, 0}, {1, 0, 0}, {0, 0, 1}, 1.0, 8)},
                          "red", false, true);
    record(add::detail::signed_volume(M));
    record(add::detail::signed_volume(M, 3));
    record(add::detail::signed_volume(M, 100));
    add::detail::fan(M, add::detail::ring({0, 1, 0}, {1, 0, 0}, {0, 0, 1}, 1.0, 8), {0, 1, 0}, "blue");
    add::detail::fan(M, add::detail::ring({0, 0, 0}, {1, 0, 0}, {0, 0, 1}, 1.0, 8), {0, 0, 0}, "blue", true);
    M.add_face({0, 1}, "gold");                                        // too short to count
    record(add::detail::signed_volume(M));
    add::detail::make_outward(M, 0);
    record(add::detail::signed_volume(M));
    add::detail::make_outward(M, 5);
    save_mesh(M);
}

CASE(emit_helper) {
    add::Mesh M;
    add::detail::add_grid(M, {add::detail::ring({0, 0, 0}, {1, 0, 0}, {0, 0, 1}, 1.0, 5),
                              add::detail::ring({0, 1, 0}, {1, 0, 0}, {0, 0, 1}, 1.0, 5)},
                          "red", false, true);
    add::detail::fan(M, add::detail::ring({0, 1, 0}, {1, 0, 0}, {0, 0, 1}, 1.0, 5), {0, 1, 0}, "blue");
    add::box({5, 0, 0}, 1);
    add::detail::emit(M);
    add::Mesh M2;
    M2.add_polygon({{0, 0, 0}, {1, 0, 0}, {1, 1, 0}}, "red");
    M2.add_polygon({{1, 1, 0}, {1, 0, 0}, {1 + 1e-10, 1, 1}}, "red");
    add::detail::emit(M2, 1e-6);
    save_case();
}

CASE(grid_solid_helper) {
    add::Mesh M = add::detail::grid_solid(
        {0, 0, 0}, {1, 0.5, 2}, {1, 1}, {0.5, 0.5, 0.5}, [](int i, int j, int k) { return (i + j + k) % 2 == 0; },
        [](int i, int j, int k) { return add::hsv(i / 3.0 + j / 7.0 + k / 11.0); });
    save_mesh(M, "a");
    M = add::detail::grid_solid({1.5, -2, 0.25}, {0.3, 0.3}, {0.7}, {1, 2, 3, 4},
                                [](int i, int, int k) { return !(i == 1 && k == 2); }, "gold");
    save_mesh(M, "b");
    M = add::detail::grid_solid({0, 0, 0}, {}, {1}, {1}, [](int, int, int) { return true; }, add::DEFAULT_COLOR);
    record((long long)M.V.size());
    M = add::detail::grid_solid({0, 0, 0}, {1, 1, 1}, {1, 1, 1}, {1, 1, 1}, [](int, int, int) { return true; },
                                [](int, int, int) { return add::random_color(); });
    save_mesh(M, "c");
}

// -- flat shapes ---------------------------------------------------------------------

CASE(flat_shapes) {
    add::polygon({{0, 0, 0}, {1, 0, 0}, {1.5, 1, 0}, {0.5, 1.7, 0}, {-0.5, 1, 0}}, "red");
    add::polygon({{0, 0, 1}, {1, 0, 1}, {0, 1, 1}});
    add::polygon({{0, 0, 1.5}, {2, 0, 1.5}, {2, 2, 1.5}, {1, 0.5, 1.5}, {0, 2, 1.5}}, "teal");   // not convex
    add::triangle({0, 0, 2}, {1, 0, 2}, {0, 1, 2.5}, {0.2, 0.4, 0.6});
    add::triangle({0, 0, 3}, {1, 0, 3}, {0, 1, 3});
    add::quad({0, 0, 4}, {1, 0, 4}, {1, 1, 4.2}, {0, 1, 4}, "#ff8800");
    add::quad({0, 0, 5}, {1, 0, 5}, {1, 1, 5}, {0, 1, 5}, add::transparent("sky", 0.4));
    save_case();
}

CASE(discs) {
    add::disc({0, 0, 0}, {0, 1, 0}, 1.0);
    add::disc({1, 2, 3}, {1, 5, 3}, 0.5, 6, "red");                  // facing a second point
    add::disc({1, 1, 1}, {1, 1, 1}, 0.75, 5, "blue");                 // normal == centre: a direction
    add::disc({4, 0, 0}, {4, -1, 0}, 1.0, 7);
    add::disc({6, 0, 0}, {7, 0, 0}, 1.0, 4, "gold");
    add::disc({8, 0, 0}, {8, 0, 3}, 1.0, 3);
    add::disc({10, 0, 0}, {10, 0, 0.5}, 0.5, 1);
    add::disc({12, 0, 0}, {12, 0, 0.5}, 0.5, 2);
    add::disc({0, 5, 0}, {0.5, 6, 0.2}, 1.25, 9, {1.0, 0.5, 0.0});
    save_case();
}

CASE(rings) {
    add::ring({0, 0, 0}, {0, 1, 0}, 1.0, 0.5);
    add::ring({3, 0, 0}, {3, 0, 1}, 1.0, 0.8, 6, "red");
    add::ring({0, 0, 0}, {0, 0, 0}, 2.0, 1.5, 5, "blue");             // normal == centre: a direction
    add::ring({6, 0, 0}, {7, 1, 1}, 0.5, 1.0, 4, "gold");             // inner bigger than outer
    add::ring({9, 0, 0}, {9, 1, 0}, 1.0, 0.0, 3);
    save_case();
}

static double hills(double x, double z) { return 0.5 * std::sin(x) * std::cos(0.7 * z); }

CASE(grids) {
    add::grid({0, 0, 0}, {4, 3});
    add::grid({6, 0, 0}, {2, 2}, 3, 2, "red");
    add::grid({0, 0, 6}, {5, 4}, 8, 6, "green", hills);
    add::grid({6, 0, 6}, {3, 3.5}, 5, 7, [](double x, double z) { return hills(x, z) < 0 ? "sky" : "white"; }, hills);
    add::grid({12, 1, 0}, {1.5, 2.5}, 4, 3, [](double x, double z) { return add::hsv(x + z); });
    add::grid({12, 0, 6}, {2, 2}, 2, 2, [](double, double) { return add::random_color(); });
    add::grid({0, -2, 12}, {3, 3}, 1, 1, {0.5, 0.25, 1.0});
    save_case();
}

CASE(grids_thick) {
    add::grid({0, 0, 0}, {4, 3}, 4, 3, "red", nullptr, 0.2);
    add::grid({6, 0, 0}, {4, 4}, 6, 5, [](double x, double) { return x > 6 ? "gold" : "navy"; }, hills, 0.3);
    add::grid({0, 0, 6}, {2, 2}, 2, 2, "blue", nullptr, -0.1);
    save_case();
}

CASE(grid_empty) {
    raises([] { add::grid({0, 0, 0}, {1, 1}, -1, 2); });
    save_case();
}

// -- boxes and other flat-sided solids ------------------------------------------------

CASE(boxes) {
    add::box({0, 0, 0}, 1);
    add::box({1, 2, 3}, 2.5, "red");
    add::cuboid({4, 0, 0}, {1, 2, 3});
    add::cuboid({8, 0.5, -1}, {0.5, 0.25, 4}, "gold");
    add::cuboid({0, 5, 0}, {-1, 1, 1}, "blue");
    add::polygon({{0, 0, 9}, {1, 0, 9}, {0, 1, 9}});
    add::box({0, 0, 9}, 0.1, {0.1, 0.2, 0.3});
    save_case();
}

CASE(frames) {
    add::frame({0, 0, 0}, 2, 0.2, "gold");
    add::frame({3, 1, 0}, 1, 0.1);
    add::frame({6, 0, 0}, 1.5, 0.5, "red");
    add::frame({9, 0, 0}, 1, 0.7, "blue");                            // bars wider than the cube
    save_case();
}

CASE(voxels_basic) {
    add::voxels({{0, 0, 0}, {1, 0, 0}, {1, 1, 0}, {-1, 0, 2}, {0, 0, 0}}, 0.5, {1, 2, 3}, "red");
    std::vector<add::Cell> blocks;
    for (int x = 0; x < 5; ++x)
        for (int y = 0; y < 3; ++y)
            for (int z = 0; z < 5; ++z)
                if ((x + y + z) % 3) blocks.push_back({x, y, z});
    add::voxels(blocks, 1.0, {0, 5, 0}, "sky");
    std::vector<add::Cell> hollow;
    for (int x = 0; x < 3; ++x)
        for (int y = 0; y < 3; ++y)
            for (int z = 0; z < 3; ++z)
                if (!(x == 1 && y == 1 && z == 1)) hollow.push_back({x, y, z});
    add::voxels(hollow, 0.25, {8, 0, 0});
    add::voxels({{3, -2, 7}});
    add::voxels({});
    save_case();
}

CASE(pyramids) {
    add::pyramid({0, 0, 0}, 2, 3, "red");
    add::pyramid({3, 0, 0}, 1, -2);
    add::pyramid({6, 1, 2}, 1.5, 0.5, "gold");
    save_case();
}

CASE(prisms) {
    add::prism({{0, 0}, {1, 0}, {0.5, 1}}, 3, "gold");
    add::prism(add::profile_star(5, 1.0, 0.4), 0.5, "red", {4, 0, 0}, {1, 1, 0});
    add::prism({{0, 0}, {0.5, 1}, {1, 0}}, 1, "blue", {0, 4, 0});                 // clockwise
    add::prism(add::profile_rect(1, 2, 0.3), 2, "teal", {4, 4, 0}, {0, 0, 1});
    add::prism(add::profile_circle(0.5, 7), 1.5, add::DEFAULT_COLOR, {8, 0, 0}, {1, 0, 0});
    add::prism({{0, 0}, {1, 0}, {1, 1}, {0, 1}}, -1, "navy", {8, 4, 0}, {0, -1, 0});
    save_case();
}

// -- the Platonic solids -----------------------------------------------------------------

CASE(polyhedra) {
    double x = 0;
    for (const char* name : {"tetrahedron", "tetra", "cube", "hexahedron", "box", "octahedron", "octa",
                             "dodecahedron", "dodeca", "icosahedron", "icosa", "Cube", "ICOSAHEDRON"}) {
        add::polyhedron(name, {x, 0, 0}, 1.0, "red");
        x += 3;
    }
    add::polyhedron("dodecahedron");
    add::polyhedron("icosahedron", {0, 4, 0}, 2.5);
    add::polyhedron("cube", {4, 4, 0}, -1.0, "blue");                // negative r: turned outward again
    add::tetrahedron();
    add::tetrahedron({0, 8, 0}, 0.5, "gold");
    add::octahedron({2, 8, 0}, 1.5);
    add::dodecahedron({5, 8, 0}, 1.25, "teal");
    add::icosahedron({8, 8, 0}, 0.75, {0.3, 0.6, 0.9});
    save_case();
}

CASE(polyhedron_unknown) {
    raises([] { add::polyhedron("pentahedron"); });
    raises([] { add::polyhedron_points(""); });
    raises([] { add::polyhedron_faces("cubes"); });
    raises([] { add::polyhedron_faces("cube"); });
}

CASE(polyhedron_tables) {
    for (const char* name : {"tetrahedron", "cube", "octahedron", "dodecahedron", "icosahedron"}) {
        record(name);
        record(add::polyhedron_points(name));
        record(add::polyhedron_points(name, {1, 2, 3}, 2.5));
        record_faces(add::polyhedron_faces(name));
    }
    record(add::polyhedron_points("Dodeca", {0.5, 0, 0}, 0.1));
    record_faces(add::polyhedron_faces("ICOSA"));
    record_faces(add::detail::hull_faces({{0, 0, 0}, {1, 0, 0}, {0, 1, 0}, {0, 0, 1}, {1, 1, 1}}, 3));
    Points cube;
    for (int x : {0, 1})
        for (int y : {0, 1})
            for (int z : {0, 1}) cube.push_back({(double)x, (double)y, (double)z});
    record_faces(add::detail::hull_faces(cube, 4));
}

CASE(voxels_colour_function) {
    add::voxels({{0, 0, 0}, {0, 1, 0}, {1, 1, 0}, {2, 3, 1}}, 0.5, {1, 2, 3},
                [](int i, int j, int k) { return add::Color(j ? "red" : (i + k ? "gold" : "blue")); });
    save_case();
}

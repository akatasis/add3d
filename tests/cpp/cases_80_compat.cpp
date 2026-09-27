#include "parity.hpp"

// demo() calls difference() (section 60) and save(), which needs write_ply / write_stl
// (section 70).  With a header that lacks those sections the calls compile but cannot link,
// so the demo case is built only when those sections' own tests are here too (at
// integration) -- or when PARITY_PENDING is defined (with PARITY_PENDING=1 set for the Python half).
#if defined(PARITY_PENDING) || (__has_include("cases_60_boolean.cpp") && __has_include("cases_70_io.cpp"))
#define WITH_60_70 1
#else
#define WITH_60_70 0
#endif

using add::Point;
using add::Point2;
using add::Profile;

CASE(old_names) {
    add::newface({{0, 0, 0}, {1, 0, 0}, {1, 1, 0}, {0, 1, 0}}, "red");
    add::newface({{0, 0, 1}, {1, 0, 1}, {0.5, 1, 1.5}}, {0.2, 0.4, 0.6});
    add::cube({3, 0, 0}, 1.5, "blue");
    add::rectangle3D({6, 0, 0}, {1, 2, 3}, {10, 20, 30});
    add::cube2({0, 4, 0}, 2.0, 0.2, "gold");
    add::cylinder2({3, 4, 0}, {3, 6, 0}, 0.5, 8, "teal");
    add::cylinder3({6, 4, 0}, {7, 5, 1}, 0.4, 6, "navy");
    add::cone2({9, 4, 0}, {9, 6, 0}, 0.6, 7, "pink");
    save_case();
}

CASE(other_names) {
    add::ball({0, 0, 0}, 1.0);
    add::ball({3, 0, 0}, 0.5, 5, "red");
    add::ball({6, 0, 0}, 0.7, 10, [](const Point& d) { return d[1] > 0.5 ? "white" : "blue"; }, 1);
    add::ball({9, 0, 0}, 0.4, 3, add::DEFAULT_COLOR, 0);
    add::block({0, 3, 0}, {1, 2, 3}, "gold");
    add::block({3, 3, 0}, {0.5, 0.5, 0.5});
    add::cuboid3D({6, 3, 0}, {2, 1, 1}, "teal");
    add::cuboid3D({9, 3, 0}, {1, 1, 1});
    save_case();
}

CASE(lathes) {
    add::lathe([](double t) { return Point2{0.5 + 0.2 * std::sin(3 * t), t}; }, {0, 0, 0}, {0, 1, 0}, 0, 2, 12, 10,
               "red");
    add::solid_of_revolution([](double t) { return Point2{1 - 0.5 * t, t}; }, {3, 0, 0}, {3, 1, 0}, 0, 1, 4, 8,
                             [](double, double a) { return add::hsv(a / 6.0); });
    Profile pts{{0.0, 0.0}, {1.0, 0.0}, {1.2, 0.5}, {0.8, 1.0}, {0.0, 1.2}};
    add::lathe(pts, {6, 0, 0}, {6, 1, 0}, 0, 1, (int)pts.size() - 1, 9, "gold");
    add::solid_of_revolution(Profile(pts.begin() + 1, pts.begin() + 4), {9, 0, 0}, {9, 2, 0}, 0.5, 1.5, 2, 7, "blue",
                             add::pi);
    add::lathe([](double t) { return Point2{0.3, t}; });
    add::solid_of_revolution([](double t) { return Point2{0.4 + 0.1 * t, t}; }, {0, 4, 0}, {1, 5, 0});
    add::lathe(Profile(pts.begin() + 1, pts.begin() + 4), {3, 4, 0}, {3, 5, 0}, 0, 1, 2, 6, "teal", 2 * add::pi,
               false);
    add::solid_of_revolution([](double t) { return Point2{0.5, t}; }, {6, 4, 0}, {6, 5, 0}, 0, 1, 3, 5, "red", 1.5,
                             false);
    save_case();
}

CASE(mesh_names) {
    add::box({0, 0, 0}, 1, "red");
    add::box({0.5, 0, 0}, 1, "blue");
    add::box({0.25, 0.25, 0.25}, 0.5, "gold");
    add::Mesh M = add::layer();
    save_mesh(add::weld(M), "weld");
    save_mesh(add::weld(M, 1e-3, true, true, true, true, true, true), "weld_normals");
    save_mesh(add::weld(M, 1e-7, false, false, false, false, false, false, nullptr, false, false), "weld_nothing");
    add::CleanReport info;
    add::Mesh W = add::weld(M, 1e-7, true, true, true, true, true, false, &info);
    record(info.vertices_removed);
    record(info.faces_removed);
    record(info.faces_cut);
    record(info.faces_split);
    save_mesh(W, "weld_report");
    save_mesh(add::scale(M, 2.0), "scale");
    save_mesh(add::scale(M, -0.5, Point{1, 1, 1}), "scale_about");
    save_mesh(add::translate(M, {1, 2, 3}), "translate");
    save_mesh(add::reflect(M), "reflect");
    save_mesh(add::reflect(M, {1, 0, 0}, {1, 1, 0}), "reflect_plane");
}

CASE(weld_scene) {
    add::box({0, 0, 0}, 1, "red");
    add::box({1, 0, 0}, 1, "red");
    save_mesh(add::weld(), "weld");
    save_case();                                   // the scene is left as it was
}

// -- demo (needs difference: section 60, and save: write_ply / write_stl of section 70) ----

#if WITH_60_70
CASE(demo_model) {
    record(add::demo());                           // writes demo.off
    save_case();                                   // demo() leaves the scene empty
}
#endif

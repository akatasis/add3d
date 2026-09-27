#include "parity.hpp"

using add::Point;
using add::Point2;
using add::Points;
using add::Profile;

// -- numbers and points ------------------------------------------------------------

CASE(numbers) {
    record(add::lerp(1.0, 3.0, 0.25));
    record(add::lerp(-2.5, 7.1, 1.3));
    record(add::lerp(0.1, 0.2, 0.3));
    record(add::clamp(1.5));
    record(add::clamp(-0.5));
    record(add::clamp(0.3));
    record(add::clamp(5.0, 2.0, 4.0));
    record(add::clamp(3.0, 2.0, 4.0));
    record(add::clamp(-7.0, -3.0, -1.0));
    record(add::remap(2.5, 0.0, 10.0, -1.0, 1.0));
    record(add::remap(7.0, 3.0, 3.0, 5.0, 9.0));                      // a0 == a1 -> b0
    record(add::remap(0.3, 1.0, 0.0, 10.0, 20.0));
    record(add::remap(0.1, 0.0, 0.3, 0.0, 1.0));
}

CASE(point_helpers) {
    record(add::lerp(Point{0.0, 0.0, 0.0}, Point{4.0, 2.0, -1.0}, 0.3));
    record(add::lerp(Point2{1.5, 2.5}, Point2{3.0, -1.0}, 0.75));
    record(add::distance(Point{0.0, 0.0, 0.0}, Point{1.0, 2.0, 2.0}));
    record(add::distance(Point{0.1, 0.2, 0.3}, Point{-1.7, 2.9, 0.35}));
    record(add::distance(Point2{1.0, 2.0}, Point2{4.0, 6.0}));
    record(add::distance(Point2{0.1, 0.7}, Point2{0.3, -0.2}));
    record(add::midpoint(Point{0.0, 0.0, 0.0}, Point{1.0, 3.0, -5.0}));
    record(add::midpoint(Point{0.1, 0.2, 0.3}, Point{0.7, -0.4, 1.1}));
    record(add::midpoint(Point2{1.5, 2.0}, Point2{2.0, 7.0}));
    record(add::direction({1.0, 1.0, 1.0}, {2.0, 3.0, 4.0}));
    record(add::direction({0.1, 0.2, 0.3}, {-0.5, 0.25, 0.3}));
    record(add::direction({1.0, 1.0, 1.0}, {1.0, 1.0, 1.0}));        // no length: the difference itself
    record(add::rotate_point({1.0, 0.0, 0.0}, {0.0, 1.0, 0.0}, 0.7));
    record(add::rotate_point({1.0, 2.0, 3.0}, {1.0, 1.0, 0.0}, 2.1, {0.5, -1.0, 2.0}));
    record(add::rotate_point({1.0, 2.0, 3.0}, {0.0, 0.0, 0.0}, 1.0));  // no axis
}

CASE(shades) {
    record(add::shade("red", 0.5));
    record(add::shade({10, 200, 30}, 1.4));
    record(add::shade("sky", 2.5));
    record(add::shade({100, 100, 100}, 1.0));
    record(add::shade({0.2, 0.4, 0.6}, 0.33));
    record(add::shade("#123456", 1.999));
}

CASE(chaikin_rounds) {
    Profile square{{0.0, 0.0}, {2.0, 0.0}, {2.0, 2.0}, {0.0, 2.0}};
    record(add::chaikin(square));
    record(add::chaikin(square, 1, true));
    record(add::chaikin(square, 3, true));
    record(add::chaikin(square, 0));
    Points path3{{0.0, 0.0, 0.0}, {1.0, 2.0, 0.0}, {3.0, 2.0, 1.0}, {4.0, 0.0, 2.0}};
    record(add::chaikin(path3));
    record(add::chaikin(path3, 1, true));
    record(add::chaikin(path3, 3));
    record(add::chaikin(Points{{1.0, 1.0, 1.0}}, 2));
    record(add::chaikin(Points{{1.0, 1.0, 1.0}}, 2, true));
    record(add::chaikin(Points{}, 2, true));
}

// -- profiles ----------------------------------------------------------------------

CASE(profiles) {
    record(add::profile_circle(1.5));
    record(add::profile_circle(2.0, 5, 0.3));
    record(add::profile_circle(1.0, 0));
    record(add::profile_ellipse(2.0, 1.0));
    record(add::profile_ellipse(0.5, 1.5, 7));
    record(add::profile_ellipse(0.5, 1.5, 1));
    record(add::profile_polygon(6, 1.0));
    record(add::profile_polygon(3, 2.0, 0.0));
    record(add::profile_polygon(5, 1.0, std::nullopt));
    record(add::profile_polygon(4, 0.5, -0.3));
    record(add::profile_star(5, 1.0, 0.4));
    record(add::profile_star(7, 2.0, 1.2, 0.1));
    record(add::profile_star(2, 1.0, 0.5, std::nullopt));
    record(add::profile_star(0, 1.0, 0.5));
}

CASE(rect_and_gear) {
    record(add::profile_rect(2.0, 1.0));
    record(add::profile_rect(2.0, 1.0, 0.2));
    record(add::profile_rect(2.0, 1.0, 0.8, 3));                      // r cut down to h / 2
    record(add::profile_rect(3.0, 3.0, 1.5, 2));                      // r == w / 2 == h / 2
    record(add::profile_rect(1.0, 1.0, 1e-10));                       // r <= EPS: sharp corners
    record(add::profile_rect(4.0, 2.0, 0.5, 1));
    record(add::profile_rect(0.7, 1.9, 0.25, 6));
    record(add::profile_gear(8, 2.0));
    record(add::profile_gear(5, 1.0, 0.3));
    record(add::profile_gear(3, 1.0, std::nullopt, 7));
    record(add::profile_gear(1, 0.5, 0.0));
}

// -- points to put things on ---------------------------------------------------------

CASE(points_on) {
    record(add::points_on_line({0.0, 0.0, 0.0}, {1.0, 2.0, 3.0}, 5));
    record(add::points_on_line({1.0, 1.0, 1.0}, {2.0, 2.0, 2.0}, 1));
    record(add::points_on_line({1.0, 1.0, 1.0}, {2.0, 2.0, 2.0}, 0));
    record(add::points_on_line({0.5, -1.0, 2.0}, {3.0, 3.0, 3.0}, 2));
    record(add::points_on_line({0.1, 0.2, 0.3}, {0.7, 0.9, -0.3}, 7));
    record(add::points_on_circle({0.0, 0.0, 0.0}, 1.0, 6));
    record(add::points_on_circle({1.0, 2.0, 3.0}, 2.5, 5, {1.0, 0.0, 0.0}, 0.4));
    record(add::points_on_circle({0.0, 0.0, 0.0}, 1.0, 4, {0.0, 0.0, 1.0}));
    record(add::points_on_circle({0.0, 0.0, 0.0}, 1.0, 3, {1.0, 1.0, 1.0}));
    record(add::points_on_circle({0.0, 0.0, 0.0}, 1.0, 0));
}

CASE(points_on_curves) {
    record(add::points_on_helix({0.0, 0.0, 0.0}, 1.0, 0.5, 3.0, 10));
    record(add::points_on_helix({1.0, 0.0, -1.0}, 2.0, 1.5, 1.25, 7, {0.0, 0.0, 1.0}));
    record(add::points_on_helix({0.0, 0.0, 0.0}, 1.0, 0.5, 2.0, 1));
    record(add::points_on_helix({0.0, 0.0, 0.0}, 1.0, 0.5, 2.0, 0));
    record(add::points_on_helix({0.0, 1.0, 0.0}, 0.3, -0.25, 0.7, 5, {1.0, -1.0, 0.5}));
    record(add::points_on_spiral({0.0, 0.0, 0.0}, 0.5, 2.0, 3.0, 12));
    record(add::points_on_spiral({1.0, 1.0, 1.0}, 1.0, 0.2, 1.5, 9, {1.0, 0.0, 0.0}, 2.0));
    record(add::points_on_spiral({0.0, 0.0, 0.0}, 1.0, 2.0, 1.0, 1));
    record(add::points_on_spiral({0.0, 0.0, 0.0}, 0.1, 0.3, 0.9, 4, {0.0, -1.0, 0.0}, -0.5));
    record(add::points_on_curve([](double t) { return Point{std::cos(t), std::sin(t), t / 3.0}; }, 0.0, 2 * add::pi,
                                8));
    record(add::points_on_curve([](double t) { return Point{t, t * t, 1.0}; }, -1.0, 1.0, 6, true));
    record(add::points_on_curve([](double t) { return Point{t, 0.5, 0.0}; }, 0.0, 1.0, 1));
    record(add::points_on_curve([](double t) { return Point{t, 0.5, 0.0}; }, 0.3, 0.7, 2, true));
}

CASE(lerp_colours) {
    record(add::lerp(add::Color(214, 190, 140), add::Color(86, 150, 70), 0.25));
    record(add::lerp(add::Color(0, 0, 0), add::Color(1, 2, 3), 0.3));
    record(add::lerp(add::Color("red"), add::Color("sky"), 0.5));
}

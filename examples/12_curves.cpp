// 12 -- parametric curves, drawn as round tubes.
//
// ``add::curve(P, t_from, t_to, steps, sides, radius, colour, closed)`` follows
// the 3D curve ``P(t)`` and wraps a tube around it.  The tube never twists on
// its own: the library carries a rotation-minimising frame along the curve, so
// a square profile stays square all the way round a loop.
//
// ``radius`` may be a function of ``t`` -- a tube that swells and tapers.
#include "add.hpp"

const double TAU = 2 * add::pi;
const double CELL = 3.4;
std::vector<std::pair<std::string, add::Mesh>> shown;


void show(const std::string& name, const std::function<void(const add::Color&)>& build, const add::Color& col,
          double size = 2.6) {
    build(col);
    shown.push_back({name, add::place(add::fit(add::layer(), size), {0, 0, 0})});
}


int main() {
    // --- a circle and a spiral -------------------------------------------------
    show("circle", [](const add::Color& c) {
        add::curve(
            [](double t) -> add::Point { return {add::cos(t), 0, add::sin(t)}; },
            0, TAU, 80, 16, 0.12, c, true);
    }, "red");

    show("helix", [](const add::Color& c) {
        add::curve(
            [](double t) -> add::Point { return {add::cos(t), t / 6.0, add::sin(t)}; },
            0, 6 * TAU, 400, 14, 0.1, c, false);
    }, "orange");

    show("conical spiral", [](const add::Color& c) {
        add::curve(
            [](double t) -> add::Point { return {t * add::cos(t) / 20, t / 20.0, t * add::sin(t) / 20}; },
            0, 8 * TAU, 400, 14, 0.09, c, false);
    }, "gold");

    // --- knots -----------------------------------------------------------------
    show("trefoil knot", [](const add::Color& c) {
        add::curve(
            [](double t) -> add::Point {
                return {add::sin(t) + 2 * add::sin(2 * t), -add::sin(3 * t),
                        add::cos(t) - 2 * add::cos(2 * t)};
            },
            0, TAU, 300, 18, 0.28, c, true);
    }, "lime");

    show("(3,4) torus knot", [](const add::Color& c) {
        add::curve(
            [](double t) -> add::Point {
                return {(2 + add::cos(4 * t / 3.0)) * add::cos(t),
                        add::sin(4 * t / 3.0),
                        (2 + add::cos(4 * t / 3.0)) * add::sin(t)};
            },
            0, 3 * TAU, 500, 18, 0.22, c, true);
    }, "teal");

    show("figure eight knot", [](const add::Color& c) {
        add::curve(
            [](double t) -> add::Point {
                return {(2 + add::cos(2 * t)) * add::cos(3 * t),
                        add::sin(4 * t),
                        (2 + add::cos(2 * t)) * add::sin(3 * t)};
            },
            0, TAU, 400, 18, 0.22, c, true);
    }, "sky");

    // --- Lissajous curves ------------------------------------------------------
    show("Lissajous 3:2", [](const add::Color& c) {
        add::curve(
            [](double t) -> add::Point {
                return {add::sin(3 * t), add::sin(2 * t + 1), add::sin(4 * t + 2)};
            },
            0, TAU, 300, 14, 0.07, c, true);
    }, "purple");

    show("Lissajous 5:4", [](const add::Color& c) {
        add::curve(
            [](double t) -> add::Point { return {add::sin(5 * t), add::sin(4 * t), add::sin(3 * t + 1)}; },
            0, TAU, 400, 14, 0.06, c, true);
    }, "magenta");

    // --- a curve whose radius changes -----------------------------------------
    show("tapering vine", [](const add::Color& c) {
        add::curve(
            [](double t) -> add::Point {
                return {add::cos(t) * (1 + t / 12.0), t / 8.0,
                        add::sin(t) * (1 + t / 12.0)};
            },
            0, 5 * TAU, 400, 16, [](double t) { return 0.22 * (1 - t / (5 * TAU)) + 0.02; },
            c, false);
    }, "brown");

    show("beaded ring", [](const add::Color& c) {
        add::curve(
            [](double t) -> add::Point { return {add::cos(t), 0.25 * add::sin(6 * t), add::sin(t)}; },
            0, TAU, 300, 16, [](double t) { return 0.08 + 0.07 * (1 + add::sin(12 * t)); },
            c, true);
    }, "navy");

    // --- rose curves lifted into 3D -------------------------------------------
    show("rose k=5", [](const add::Color& c) {
        add::curve(
            [](double t) -> add::Point {
                return {add::cos(5 * t) * add::cos(t), 0.25 * add::sin(5 * t),
                        add::cos(5 * t) * add::sin(t)};
            },
            0, TAU, 400, 14, 0.06, c, true);
    }, "pink");

    show("spherical spiral", [](const add::Color& c) {
        add::curve(
            [](double t) -> add::Point {
                return {add::sin(t / 10.0) * add::cos(t), add::cos(t / 10.0),
                        add::sin(t / 10.0) * add::sin(t)};
            },
            0.001, 10 * add::pi - 0.001, 500, 12, 0.045, c, false);
    }, "silver");

    int columns = 4;
    for (int i = 0; i < (int)shown.size(); ++i) {
        const auto& [name, M] = shown[i];
        add::mesh(add::move(M, {(i % columns) * CELL, 0, (i / columns) * CELL}));
        std::printf("%2d. %s\n", i + 1, name.c_str());
    }

    add::check();
    add::save("curves.off");
}

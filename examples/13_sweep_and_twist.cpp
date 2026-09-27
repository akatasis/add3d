// 13 -- copy a cross-section, move it, turn it, stretch it.
//
// This is the workhorse of hand-made 3D: take a flat outline, carry it along a
// path and let it rotate and change size as it goes.
//
//     add::extrude(profile, direction, colour, steps, twist, scale);
//     add::sweep(profile, path, t0, t1, steps, colour, closed, scale, twist);
//
// ``twist`` is the total turn in radians; ``scale`` may be a number or a
// function of the position ``t`` along the path (0 at the start, 1 at the end).
#include "add.hpp"

const double TAU = 2 * add::pi;
const double CELL = 3.6;
std::vector<std::pair<std::string, add::Mesh>> shown;


// A regular polygon, or a star when ``inner`` is given.
add::Profile polygon_profile(int sides, double r = 1.0, std::optional<double> inner = std::nullopt) {
    add::Profile pts;
    int n = sides * (inner ? 2 : 1);
    for (int i = 0; i < n; ++i) {
        double a = TAU * i / n;
        double rad = (inner == std::nullopt || i % 2 == 0) ? r : *inner;
        pts.push_back({add::cos(a) * rad, add::sin(a) * rad});
    }
    return pts;
}


void show(const std::string& name, const std::function<void(const add::Color&)>& build, const add::Color& col,
          double size = 3.0) {
    build(col);
    shown.push_back({name, add::place(add::fit(add::layer(), size), {0, 0, 0})});
}


const add::Profile SQUARE = {{-0.6, -0.6}, {0.6, -0.6}, {0.6, 0.6}, {-0.6, 0.6}};
const add::Profile STAR = polygon_profile(6, 0.8, 0.35);
const add::Profile TRIANGLE = polygon_profile(3, 0.8);


// --- an arch: a square swept along half a circle, then mirrored -----------
void arch(const add::Color& c) {
    add::sweep(SQUARE, [](double t) -> add::Point { return {2.4 * add::cos(t), 2.4 * add::sin(t), 0}; },
               0, add::pi, 90, c, /*closed=*/false, /*scale=*/0.5);
    add::Mesh legs = add::layer();
    add::mesh(legs);
    add::mesh(add::move(legs, {0, -1.6, 0}));
}


int main() {
    // --- plain extrusion, then the same with a twist, then with a taper --------
    show("straight bar", [](const add::Color& c) { add::extrude(SQUARE, {0, 3, 0}, c); }, "red");

    show("twisted bar", [](const add::Color& c) {
        add::extrude(SQUARE, {0, 3, 0}, c, /*steps=*/60,
                     /*twist=*/add::pi);
    }, "orange");

    show("tapered bar", [](const add::Color& c) {
        add::extrude(SQUARE, {0, 3, 0}, c, /*steps=*/40,
                     /*twist=*/0.0, /*scale=*/[](double t) { return 1 - 0.8 * t; });
    }, "gold");

    show("twisted star column", [](const add::Color& c) {
        add::extrude(STAR, {0, 3.4, 0}, c, /*steps=*/90, /*twist=*/1.6 * add::pi,
                     /*scale=*/[](double t) { return 1 - 0.45 * t; });
    }, "lime");

    show("bulging column", [](const add::Color& c) {
        add::extrude(polygon_profile(16, 0.7), {0, 3.4, 0}, c, /*steps=*/80, /*twist=*/0.0,
                     /*scale=*/[](double t) { return 1 + 0.5 * add::sin(add::pi * t); });
    }, "teal");

    // --- sweeping along a curved path -----------------------------------------
    show("square through a helix", [](const add::Color& c) {
        add::sweep(SQUARE, [](double t) -> add::Point { return {add::cos(t), t / 4.0, add::sin(t)}; },
                   0, 4 * TAU, 260, c, /*closed=*/false, /*scale=*/0.28);
    }, "sky");

    show("triangle round a ring", [](const add::Color& c) {
        add::sweep(TRIANGLE, [](double t) -> add::Point { return {2 * add::cos(t), 0,
                                                                  2 * add::sin(t)}; },
                   0, TAU, 160, c, /*closed=*/true, /*scale=*/0.5,
                   /*twist=*/[](double t) { return 2 * TAU * t; });
    }, "purple");

    show("ribbon knot", [](const add::Color& c) {
        add::sweep({{-0.5, -0.06}, {0.5, -0.06}, {0.5, 0.06},
                    {-0.5, 0.06}},
                   [](double t) -> add::Point { return {add::sin(t) + 2 * add::sin(2 * t),
                                                        -add::sin(3 * t),
                                                        add::cos(t) - 2 * add::cos(2 * t)}; },
                   0, TAU, 300, c, /*closed=*/true, /*scale=*/add::Scalar(),
                   /*twist=*/[](double t) { return 3 * TAU * t; });
    }, "magenta");

    show("horn from a growing circle", [](const add::Color& c) {
        add::sweep(polygon_profile(24, 1.0),
                   [](double t) -> add::Point { return {1.6 * add::cos(t) * add::exp(0.12 * t),
                                                        0.5 * t,
                                                        1.6 * add::sin(t) * add::exp(0.12 * t)}; },
                   0, 3.2 * add::pi, 200, c,
                   /*closed=*/false, /*scale=*/[](double t) { return 0.12 + 1.2 * t * t; });
    }, "brown");

    // --- a screw thread, built by sweeping a triangle along a helix ------------
    show("screw thread", [](const add::Color& c) {
        add::sweep({{0, -0.22}, {0.42, 0}, {0, 0.22}},
                   [](double t) -> add::Point { return {add::cos(t), t / 9.0, add::sin(t)}; },
                   0, 7 * TAU, 700, c);
    }, "silver");

    // --- an arch: a square swept along half a circle, then mirrored -----------
    // (the function arch() is written above main)
    show("arch", arch, "navy");

    // --- a leaf: a profile that starts and ends at nothing ---------------------
    show("leaf blade", [](const add::Color& c) {
        add::sweep(polygon_profile(12, 1.0),
                   [](double t) -> add::Point { return {0, t, 0}; }, 0, 4, 90, c, /*closed=*/false,
                   /*scale=*/[](double t) { return 0.9 * add::detail::py_pow(add::sin(add::pi * t), 0.7)
                                                   + 0.02; },
                   /*twist=*/0.4 * add::pi);
    }, "pink");

    int columns = 4;
    for (int i = 0; i < (int)shown.size(); ++i) {
        const auto& [name, M] = shown[i];
        add::mesh(add::move(M, {(i % columns) * CELL, 0, (i / columns) * CELL}));
        std::printf("%2d. %s\n", i + 1, name.c_str());
    }

    add::check();
    add::save("sweeps.off");
}

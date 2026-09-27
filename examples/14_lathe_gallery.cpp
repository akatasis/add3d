// 14 -- the lathe: spin a profile around an axis.
//
// ``add::revolve(profile, A, B, t0, t1, steps, k, colour)`` turns a
// ``profile(t) -> {radius, height}`` around the axis from ``A`` to ``B``.  It is
// how a potter works, and it is the fastest way to a vase, a chess piece, a
// bottle or a lamp.
//
// Give it an ``angle`` less than a full turn to cut a wedge out and see inside.
#include "add.hpp"

const double CELL = 3.2;
std::vector<std::pair<std::string, add::Mesh>> shown;


void show(const std::string& name, const std::function<void(add::Color)>& build, const add::Color& col,
          double size = 2.8) {
    build(col);
    shown.push_back({name, add::place(add::fit(add::layer(), size), {0, 0, 0})});
}


// (Python passes any other keyword on to revolve with **kw: here that is angle and caps.)
void lathe(const std::function<add::Point2(double)>& profile, const add::Color& col, double height = 4.0,
           int steps = 120, int k = 48, double angle = 2.0 * add::pi, bool caps = true) {
    add::revolve(profile, {0, 0, 0}, {0, 1, 0}, 0, height, steps, k, col, angle, caps);
}


int main() {
    // --- a vase: radius as a smooth function of height -------------------------
    show("vase", [](add::Color c) {
        lathe([](double t) { return add::Point2{1.1 + 0.55 * add::sin(1.2 * t) - 0.18 * t, t}; }, c);
    }, "teal");

    // --- a wine glass ----------------------------------------------------------
    auto glass = [](double t) -> add::Point2 {
        if (t < 0.12)
            return {1.0, t};                      // foot
        if (t < 0.2)
            return {1.0 - (t - 0.12) * 9, t};
        if (t < 1.6)
            return {0.12, t};                     // stem
        double s = (t - 1.6) / 2.4;
        return {0.12 + 1.15 * add::sqrt(std::max(0.0, s)) * (1 - 0.25 * s), t};
    };

    show("wine glass", [&](add::Color c) { lathe(glass, c, 4.0, 160); }, "sky");

    // --- a bottle --------------------------------------------------------------
    auto bottle = [](double t) -> add::Point2 {
        if (t < 2.6)
            return {1.0, t};
        if (t < 3.2)
            return {1.0 - 0.62 * (t - 2.6) / 0.6, t};
        return {0.38, t};
    };

    show("bottle", [&](add::Color c) { lathe(bottle, c, 4.2, 140); }, "green");

    // --- chess pieces ----------------------------------------------------------
    auto pawn = [](double t) -> add::Point2 {
        double r = (0.85 * add::exp(-3.0 * t) + 0.22
                    + 0.42 * add::exp(-28 * add::detail::py_pow(t - 1.35, 2))
                    + 0.36 * add::exp(-40 * add::detail::py_pow(t - 2.15, 2)));
        return {r, t};
    };

    show("pawn", [&](add::Color c) { lathe(pawn, c, 2.5, 140); }, "silver");

    auto rook = [](double t) -> add::Point2 {
        if (t < 0.35)
            return {0.85 - 0.5 * t, t};
        if (t < 1.9)
            return {0.45 + 0.1 * add::exp(-4 * (t - 0.35)), t};
        if (t < 2.15)
            return {0.45 + (t - 1.9) * 1.4, t};
        return {0.8, t};
    };

    show("rook", [&](add::Color c) { lathe(rook, c, 2.4, 120); }, "brown");

    auto queen = [](double t) -> add::Point2 {
        double r = (0.95 * add::exp(-2.6 * t) + 0.2
                    + 0.45 * add::exp(-30 * add::detail::py_pow(t - 1.5, 2))
                    + 0.30 * add::exp(-60 * add::detail::py_pow(t - 2.5, 2))
                    + 0.55 * add::exp(-45 * add::detail::py_pow(t - 3.1, 2)));
        return {r, t};
    };

    show("queen", [&](add::Color c) { lathe(queen, c, 3.4, 170); }, "gold");

    // --- a lamp shade: open at both ends ---------------------------------------
    show("lamp shade", [](add::Color c) {
        lathe([](double t) { return add::Point2{0.5 + 0.45 * t, t}; }, c, 2.2, 40,
              48, 2.0 * add::pi, false);                 // k and angle as by default; caps = false
    }, "yellow");

    // --- a doughnut, from a circular profile -----------------------------------
    show("doughnut", [](add::Color c) {
        add::revolve([](double t) { return add::Point2{2 + add::cos(t), add::sin(t)}; }, {0, 0, 0}, {0, 1, 0},
                     0, 2 * add::pi, 40, 72, c);
    }, "orange");

    // --- a fluted column: the profile wobbles ----------------------------------
    show("beaded column", [](add::Color c) {
        lathe([](double t) { return add::Point2{0.55 + 0.2 * std::abs(add::sin(2.4 * t)), t}; }, c, 5.0, 220);
    }, "purple");

    // --- a spinning top --------------------------------------------------------
    show("spinning top", [](add::Color c) {
        lathe([](double t) {
                  return add::Point2{t < 1.6 ? 1.0 * add::detail::py_pow(add::sin(add::pi * std::min(1.0, t / 1.6)), 0.6)
                                             : std::max(0.04, 0.35 - 0.3 * (t - 1.6)), t};
              },
              c, 2.6, 140);
    }, "red");

    // --- cut open to show the wall ---------------------------------------------
    show("cup, cut open", [](add::Color c) {
        lathe([](double t) { return add::Point2{1.0 + 0.1 * t, t}; }, c, 2.4, 40, 48, 1.55 * add::pi);   // angle
    }, "magenta");

    // --- a screw-like profile --------------------------------------------------
    show("ribbed pot", [](add::Color c) {
        lathe([](double t) { return add::Point2{1.0 + 0.35 * add::sin(3.0 * t) * add::exp(-0.25 * t), t}; },
              c, 3.6, 180);
    }, "navy");

    int columns = 4;
    for (int i = 0; i < (int)shown.size(); ++i) {
        const auto& [name, M] = shown[i];
        add::mesh(add::move(M, {(i % columns) * CELL, 0, (i / columns) * CELL}));
        std::printf("%2d. %s\n", i + 1, name.c_str());
    }

    add::check();
    add::save("lathe.off");
}

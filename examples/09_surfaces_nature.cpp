// 09 -- surfaces that look like things: shells, fruit, horns and waves.
//
// Nature is surprisingly parametric.  A seashell is a circle whose radius grows
// while it spirals; an apple is a sphere with a dent; a horn is a cone wrapped
// round a logarithmic spiral.
#include "add.hpp"

const double TAU = 2 * add::pi;
const double CELL = 3.4;
std::vector<std::pair<std::string, add::Mesh>> shown;


void show(const std::string& name, const std::function<void(const add::Color&)>& build, const add::Color& col,
          double size = 2.4) {
    build(col);
    shown.push_back({name, add::place(add::fit(add::layer(), size), {0, 0, 0})});
}


// --------------------------------------------------------------------------
//  A seashell: a circle that spirals outwards while it grows
// --------------------------------------------------------------------------
add::Point seashell(double u, double v) {
    double a = 0.2, b = 1.0, c = 0.1;
    double n = 2.0;
    double w = add::exp(a * u);
    return {w * (b + add::cos(v)) * add::cos(n * u),
            w * (c * u / 2 + add::sin(v)),
            w * (b + add::cos(v)) * add::sin(n * u)};
}


// --------------------------------------------------------------------------
//  A snail shell with a sharper spiral
// --------------------------------------------------------------------------
add::Point snail(double u, double v) {
    double k = 0.16;
    double r = add::exp(k * u);
    double tube = 0.32 * r;
    return {r * add::cos(u) + tube * add::cos(v) * add::cos(u),
            0.45 * r + tube * add::sin(v),
            r * add::sin(u) + tube * add::cos(v) * add::sin(u)};
}


// --------------------------------------------------------------------------
//  Dini's surface -- a helical version of the pseudosphere
// --------------------------------------------------------------------------
add::Point dini(double u, double v) {
    return {add::cos(u) * add::sin(v),
            add::cos(v) + add::log(add::tan(v / 2)) + 0.2 * u,
            add::sin(u) * add::sin(v)};
}


// --------------------------------------------------------------------------
//  Apple and lemon -- two spheres with the poles pulled about
// --------------------------------------------------------------------------
add::Point apple(double u, double v) {
    double r1 = 4.0, r2 = 3.8;
    return {add::cos(u) * (r1 + r2 * add::cos(v)) + add::pow(v / add::pi, 100),
            -2.3 * add::log(1 - v * 0.3157) + 6 * add::sin(v)
            + 2 * add::cos(v),
            add::sin(u) * (r1 + r2 * add::cos(v))};
}


add::Point lemon(double u, double v) {
    return {add::detail::py_pow(add::cos(u / 2), 4) * add::cos(v) * 2,
            add::sin(u) / 2,
            add::detail::py_pow(add::cos(u / 2), 4) * add::sin(v) * 2};
}


// --------------------------------------------------------------------------
//  A heart
// --------------------------------------------------------------------------
add::Point heart(double u, double v) {
    double s = add::sin(v);
    return {s * (15 * add::sin(u) - 4 * add::sin(3 * u)),
            8 * add::cos(v),
            s * (15 * add::cos(u) - 5 * add::cos(2 * u)
                 - 2 * add::cos(3 * u) - add::cos(4 * u))};
}


// --------------------------------------------------------------------------
//  A horn, a trumpet flower and a twisted column
// --------------------------------------------------------------------------
add::Point horn(double u, double v) {
    double r = 0.12 * add::detail::py_pow(1 + 1.4 * u / TAU, 2);
    double R = 1.4 * add::exp(0.22 * u);
    return {(R + r * add::cos(v)) * add::cos(u),
            r * add::sin(v) + 0.6 * u,
            (R + r * add::cos(v)) * add::sin(u)};
}


add::Point trumpet(double u, double v) {
    double r = 0.3 + 1.9 * add::detail::py_pow(u / 3.0, 4);
    return {r * add::cos(v), u, r * add::sin(v)};
}


add::Point fluted(double u, double v) {
    double r = 1.0 + 0.16 * add::cos(9 * (v + 0.5 * u));
    return {r * add::cos(v), u, r * add::sin(v)};
}


// --------------------------------------------------------------------------
//  A breather surface -- a soliton of the sine-Gordon equation
// --------------------------------------------------------------------------
add::Point breather(double u, double v) {
    double b = 0.4;
    double w = add::sqrt(1 - b * b);
    double denom = b * (add::detail::py_pow(w * add::cosh(b * u), 2)
                        + add::detail::py_pow(b * add::sin(w * v), 2));
    return {-u + 2 * w * w * add::cosh(b * u) * add::sinh(b * u) / denom,
            2 * w * add::cosh(b * u) * (-w * add::cos(v) * add::cos(w * v)
                                        - add::sin(v) * add::sin(w * v)) / denom,
            2 * w * add::cosh(b * u) * (-w * add::sin(v) * add::cos(w * v)
                                        + add::cos(v) * add::sin(w * v)) / denom};
}


// --------------------------------------------------------------------------
//  Ripples on a pond and a drop
// --------------------------------------------------------------------------
add::Point drop(double u, double v) {
    return {0.5 * (1 - add::cos(u)) * add::sin(u) * add::cos(v),
            add::cos(u),
            0.5 * (1 - add::cos(u)) * add::sin(u) * add::sin(v)};
}


int main() {
    show("seashell", [](const add::Color& c) {
        add::parametric(seashell, 0, 6 * add::pi, 240,
                        0, TAU, 36, c, /*wrap_u=*/false, /*wrap_v=*/true);
    }, "orange");

    show("snail", [](const add::Color& c) {
        add::parametric(snail, 0, 8 * add::pi, 300, 0, TAU, 30,
                        c, /*wrap_u=*/false, /*wrap_v=*/true);
    }, "brown");

    show("Dini's surface", [](const add::Color& c) {
        add::parametric(dini, 0, 4 * add::pi, 180,
                        0.05, 2.0, 40, c);
    }, "lime");

    show("apple", [](const add::Color& c) {
        add::parametric(apple, 0, TAU, 60, -add::pi, add::pi,
                        60, c, /*wrap_u=*/true);
    }, "red");

    show("lemon", [](const add::Color& c) {
        add::parametric(lemon, -add::pi, add::pi, 60, 0, TAU,
                        60, c, /*wrap_u=*/false, /*wrap_v=*/true);
    }, "yellow");

    show("heart", [](const add::Color& c) {
        add::parametric(heart, 0, TAU, 80, 0, add::pi, 50, c,
                        /*wrap_u=*/true);
    }, "pink");

    show("horn", [](const add::Color& c) {
        add::parametric(horn, 0, 3.6 * add::pi, 180, 0, TAU, 28,
                        c, /*wrap_u=*/false, /*wrap_v=*/true);
    }, "gold");

    show("trumpet flower", [](const add::Color& c) {
        add::parametric(
            trumpet, 0, 3.0, 50, 0, TAU, 60, c, /*wrap_u=*/false, /*wrap_v=*/true, /*flip=*/false,
            /*thickness=*/0.05);
    }, "magenta");

    show("fluted column", [](const add::Color& c) {
        add::parametric(fluted, 0, 5.0, 60, 0, TAU, 90,
                        c, /*wrap_u=*/false, /*wrap_v=*/true);
    }, "silver");

    show("breather", [](const add::Color& c) {
        add::parametric(breather, -13, 13, 160, -14, 14,
                        200, c, /*wrap_u=*/false, /*wrap_v=*/false, /*flip=*/false, /*thickness=*/0.0,
                        /*double_sided=*/true);
    }, "teal");

    // --------------------------------------------------------------------------
    //  Ripples on a pond and a drop
    // --------------------------------------------------------------------------
    show("ripples", [](const add::Color& c) {
        add::parametric(
            [](double u, double v) -> add::Point {
                return {u, add::sin(add::sqrt(u * u + v * v) * 3)
                           / (1 + 0.4 * (u * u + v * v)), v};
            },
            -4, 4, 90, -4, 4, 90, c, /*wrap_u=*/false, /*wrap_v=*/false, /*flip=*/false,
            /*thickness=*/0.05);
    }, "sky");

    show("drop", [](const add::Color& c) {
        add::parametric(drop, 0, add::pi, 60, 0, TAU, 60, c,
                        /*wrap_u=*/false, /*wrap_v=*/true);
    }, "navy");


    // --------------------------------------------------------------------------
    int columns = 4;
    for (int i = 0; i < (int)shown.size(); ++i) {
        const auto& [name, M] = shown[i];
        add::mesh(add::move(M, {(i % columns) * CELL, 0, (i / columns) * CELL}));
        std::printf("%2d. %s\n", i + 1, name.c_str());
    }

    add::check();
    add::save("surfaces_nature.off");
}

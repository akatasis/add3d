// 07 -- surfaces with a twist: one-sided and self-intersecting.
//
// These are the surfaces that are hard to hold in your head and easy to write
// down.  Several of them are *non-orientable*: they have only one side, so the
// idea of "outside" stops making sense.  Give them a thickness and they become
// ordinary two-sided solids again -- which is also the honest way to see them.
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
//  Möbius strip -- one edge, one side
// --------------------------------------------------------------------------
add::Point mobius(double u, double v) {
    return {(1 + v / 2 * add::cos(u / 2)) * add::cos(u),
            v / 2 * add::sin(u / 2),
            (1 + v / 2 * add::cos(u / 2)) * add::sin(u)};
}


// --------------------------------------------------------------------------
//  Klein bottle, figure-eight immersion -- a bottle with no inside
// --------------------------------------------------------------------------
add::Point klein8(double u, double v) {
    double r = 2.0;
    double cu = add::cos(u / 2), su = add::sin(u / 2);
    double sv = add::sin(v), s2v = add::sin(2 * v);
    double f = r + cu * sv - su * s2v;
    return {f * add::cos(u), su * sv + cu * s2v, f * add::sin(u)};
}


// --------------------------------------------------------------------------
//  Klein bottle, the classic bottle shape
// --------------------------------------------------------------------------
add::Point klein_bottle(double u, double v) {
    double cu = add::cos(u), su = add::sin(u);
    double cv = add::cos(v), sv = add::sin(v);
    double x, z;
    if (u < add::pi) {
        x = 3 * cu * (1 + su) + (2 * (1 - cu / 2)) * cu * cv;
        z = -8 * su - 2 * (1 - cu / 2) * su * cv;
    } else {
        x = 3 * cu * (1 + su) + (2 * (1 - cu / 2)) * add::cos(v + add::pi);
        z = -8 * su;
    }
    double y = -2 * (1 - cu / 2) * sv;
    return {x, y, z};
}


// --------------------------------------------------------------------------
//  Boy's surface -- the projective plane immersed in space
// --------------------------------------------------------------------------
add::Point boy(double u, double v) {
    [[maybe_unused]] double cu = add::cos(u), su = add::sin(u);
    [[maybe_unused]] double cv = add::cos(v), sv = add::sin(v);
    double d = 2 - add::sqrt(2) * add::sin(3 * u) * add::sin(2 * v);
    return {add::sqrt(2) * cv * cv * add::cos(2 * u) / d + cv * cv * add::cos(2 * u) * 0,
            3 * cv * cv / d - 1.5,
            add::sqrt(2) * cv * cv * add::sin(2 * u) / d};
}


// A fuller Boy's surface: the Bryant-Kusner style parametrisation.
add::Point boy_full(double u, double v) {
    double cu = add::cos(u), su = add::sin(u);
    [[maybe_unused]] double cv = add::cos(v), sv = add::sin(v);
    double d = 2 - add::sqrt(2) * add::sin(3 * u) * add::sin(2 * v);
    double x = (add::sqrt(2) * cv * cv * add::cos(2 * u)
                + cu * add::sin(2 * v)) / d;
    double y = (add::sqrt(2) * cv * cv * add::sin(2 * u)
                - su * add::sin(2 * v)) / d;
    double z = 3 * cv * cv / d;
    return {x, z - 1.2, y};
}


// --------------------------------------------------------------------------
//  Roman (Steiner) surface and the cross-cap
// --------------------------------------------------------------------------
add::Point roman(double u, double v) {
    double su = add::sin(u), cu = add::cos(u);
    double sv = add::sin(v), cv = add::cos(v);
    return {su * su * add::sin(2 * v) / 2,
            su * cu * sv,
            su * cu * cv};
}


add::Point cross_cap(double u, double v) {
    double su = add::sin(u), cu = add::cos(u);
    [[maybe_unused]] double sv = add::sin(v), cv = add::cos(v);
    return {su * add::sin(2 * v) / 2, su * su * cv, su * cu * (1 + cv) / 1.0};
}


// --------------------------------------------------------------------------
//  Enneper's minimal surface and Henneberg's surface
// --------------------------------------------------------------------------
add::Point enneper(double u, double v) {
    return {u - add::detail::py_pow(u, 3) / 3 + u * v * v,
            u * u - v * v,
            v - add::detail::py_pow(v, 3) / 3 + v * u * u};
}


// Scherk's surface: cos(y) = cos(x) e^z, drawn as a height field.
add::Point scherk(double u, double v) {
    return {u, add::log(std::abs(add::cos(v) / add::cos(u))), v};
}


// --------------------------------------------------------------------------
//  Trefoil knot ribbon -- a band that follows a knot
// --------------------------------------------------------------------------
add::Point trefoil_path(double t) {
    return {add::sin(t) + 2 * add::sin(2 * t),
            -add::sin(3 * t),
            -add::cos(t) + 2 * add::cos(2 * t)};
}


int main() {
    show("Mobius strip", [](const add::Color& c) {
        add::parametric(mobius, 0, TAU, 160, -1, 1, 10,
                        c, /*wrap_u=*/false, /*wrap_v=*/false, /*flip=*/false, /*thickness=*/0.0,
                        /*double_sided=*/true);
    }, "red");

    // A wide Möbius band, given a real thickness: now it is a solid you can print.
    show("Mobius solid", [](const add::Color& c) {
        add::parametric(mobius, 0, TAU, 160, -1, 1, 10,
                        c, /*wrap_u=*/false, /*wrap_v=*/false, /*flip=*/false, /*thickness=*/0.09);
    }, "orange");

    show("Klein bottle (fig-8)", [](const add::Color& c) {
        add::parametric(klein8, 0, TAU, 120, 0, TAU, 60, c,
                        /*wrap_u=*/true, /*wrap_v=*/true);
    }, "gold");

    show("Klein bottle", [](const add::Color& c) {
        add::parametric(klein_bottle, 0, TAU, 120, 0,
                        TAU, 60, c, /*wrap_u=*/false, /*wrap_v=*/true,
                        /*flip=*/false, /*thickness=*/0.0, /*double_sided=*/true);
    }, "lime");

    show("Boy's surface", [](const add::Color& c) {
        add::parametric(boy_full, 0, add::pi, 100,
                        -add::pi / 2, add::pi / 2, 100,
                        c, /*wrap_u=*/true, /*wrap_v=*/false, /*flip=*/false, /*thickness=*/0.0,
                        /*double_sided=*/true);
    }, "teal");

    show("Roman surface", [](const add::Color& c) {
        add::parametric(roman, 0, add::pi, 90, 0,
                        TAU, 90, c, /*wrap_u=*/false, /*wrap_v=*/true,
                        /*flip=*/false, /*thickness=*/0.0, /*double_sided=*/true);
    }, "purple");

    show("cross-cap", [](const add::Color& c) {
        add::parametric(cross_cap, 0, add::pi, 90, 0, TAU,
                        90, c, /*wrap_u=*/false, /*wrap_v=*/true,
                        /*flip=*/false, /*thickness=*/0.0, /*double_sided=*/true);
    }, "magenta");

    show("Enneper surface", [](const add::Color& c) {
        add::parametric(enneper, -2, 2, 60, -2, 2,
                        60, c, /*wrap_u=*/false, /*wrap_v=*/false, /*flip=*/false, /*thickness=*/0.09);
    }, "sky");

    show("Scherk surface", [](const add::Color& c) {
        add::parametric(
            scherk, -1.4, 1.4, 60, -1.4, 1.4, 60, c, /*wrap_u=*/false, /*wrap_v=*/false, /*flip=*/false,
            /*thickness=*/0.08);
    }, "brown");

    show("trefoil ribbon", [](const add::Color& c) {
        add::ribbon(trefoil_path, 0, TAU, 220, 0.8, c,
                    /*closed=*/true, /*twist=*/3 * add::pi,
                    /*thickness=*/0.06);
    }, "navy");


    // --------------------------------------------------------------------------
    //  lay them out and save
    // --------------------------------------------------------------------------
    int columns = 4;
    for (int i = 0; i < (int)shown.size(); ++i) {
        const auto& [name, M] = shown[i];
        add::mesh(add::move(M, {(i % columns) * CELL, 0, (i / columns) * CELL}));
        std::printf("%2d. %s\n", i + 1, name.c_str());
    }

    add::check();
    add::save("surfaces_exotic.off");
}

// 06 -- the classic parametric surfaces.
//
// Each one is three formulas.  ``add::parametric`` walks a rectangle of (u, v)
// values, calls your function at every grid point and joins the points up.
//
//     add::Point surface(double u, double v) {
//         return {x(u, v), y(u, v), z(u, v)};
//     }
//
//     add::parametric(surface, u_from, u_to, u_detail,
//                              v_from, v_to, v_detail, colour);
#include "add.hpp"

const double TAU = 2 * add::pi;
const double CELL = 3.2;
std::vector<std::pair<std::string, add::Mesh>> shown;


// Build one surface, scale it to a standard size and park it on a grid.
void show(const std::string& name, const std::function<void(const add::Color&)>& build, const add::Color& col,
          double size = 2.2) {
    build(col);
    add::Mesh M = add::place(add::fit(add::layer(), size), {0, 0, 0});
    shown.push_back({name, M});
}


// -------------------------------------------------------------------------
// 11. Torus knot tube -- a curve given thickness by sweeping a circle
// -------------------------------------------------------------------------
add::Point knot(double u, double v) {
    int p = 2, q = 3;
    double r = 0.35;
    double cu = add::cos(q * u);
    double x = (2 + cu) * add::cos(p * u);
    double y = -add::sin(q * u);
    double z = (2 + cu) * add::sin(p * u);
    // a small circle around the curve, drawn with a numerical tangent
    double h = 1e-4;
    std::vector<double> t = {((2 + add::cos(q * (u + h))) * add::cos(p * (u + h)) - x) / h,
                             (-add::sin(q * (u + h)) - y) / h,
                             ((2 + add::cos(q * (u + h))) * add::sin(p * (u + h)) - z) / h};
    double sum = 0;                                   // sum(a * a for a in t)
    for (double a : t) sum += a * a;
    double n = add::sqrt(sum);
    for (double& a : t) a = a / n;
    std::vector<double> e1 = {-t[2], 0, t[0]};
    double sum1 = 0;                                  // sum(a * a for a in e1)
    for (double a : e1) sum1 += a * a;
    double n1 = add::sqrt(sum1);
    if (n1 == 0) n1 = 1.0;                            // (Python: ``... or 1.0``)
    for (double& a : e1) a = a / n1;
    std::vector<double> e2 = {t[1] * e1[2] - t[2] * e1[1], t[2] * e1[0] - t[0] * e1[2],
                              t[0] * e1[1] - t[1] * e1[0]};
    return {x + r * (e1[0] * add::cos(v) + e2[0] * add::sin(v)),
            y + r * (e1[1] * add::cos(v) + e2[1] * add::sin(v)),
            z + r * (e1[2] * add::cos(v) + e2[2] * add::sin(v))};
}


int main() {
    // --------------------------------------------------------------------------
    //  1. Sphere        x = r cos u sin v,  y = r cos v,  z = r sin u sin v
    // --------------------------------------------------------------------------
    show("sphere", [](const add::Color& c) {
        add::parametric(
            [](double u, double v) -> add::Point {
                return {add::cos(u) * add::sin(v), add::cos(v), add::sin(u) * add::sin(v)};
            },
            0, TAU, 48, 0, add::pi, 24, c, /*wrap_u=*/true);
    }, "red");

    // --------------------------------------------------------------------------
    //  2. Torus         a circle of radius b swept round a circle of radius a
    // --------------------------------------------------------------------------
    show("torus", [](const add::Color& c) {
        add::parametric(
            [](double u, double v) -> add::Point {
                return {(3 + add::cos(u)) * add::cos(v), add::sin(u),
                        (3 + add::cos(u)) * add::sin(v)};
            },
            0, TAU, 28, 0, TAU, 56, c, /*wrap_u=*/true, /*wrap_v=*/true);
    }, "orange");

    // --------------------------------------------------------------------------
    //  3. Cylinder and 4. Cone -- the two simplest ruled surfaces
    // --------------------------------------------------------------------------
    show("cylinder", [](const add::Color& c) {
        add::parametric(
            [](double u, double v) -> add::Point { return {add::cos(u), v, add::sin(u)}; },
            0, TAU, 48, -1.5, 1.5, 8, c, /*wrap_u=*/true, /*wrap_v=*/false, /*flip=*/false,
            /*thickness=*/0.08);
    }, "gold");

    show("cone", [](const add::Color& c) {
        add::parametric(
            [](double u, double v) -> add::Point { return {v * add::cos(u), v, v * add::sin(u)}; },
            0, TAU, 48, 0, 2, 12, c, /*wrap_u=*/true);
    }, "lime");

    // --------------------------------------------------------------------------
    //  5. Hyperbolic paraboloid -- the saddle, y = v² - u²
    // --------------------------------------------------------------------------
    show("saddle", [](const add::Color& c) {
        add::parametric(
            [](double u, double v) -> add::Point { return {u, v * v - u * u, v}; },
            -1.5, 1.5, 36, -1.5, 1.5, 36, c, /*wrap_u=*/false, /*wrap_v=*/false, /*flip=*/false,
            /*thickness=*/0.06);
    }, "teal");

    // --------------------------------------------------------------------------
    //  6. One-sheet hyperboloid -- straight lines that make a curved surface
    // --------------------------------------------------------------------------
    show("hyperboloid", [](const add::Color& c) {
        add::parametric(
            [](double u, double v) -> add::Point {
                return {add::cosh(v) * add::cos(u), add::sinh(v),
                        add::cosh(v) * add::sin(u)};
            },
            0, TAU, 48, -1.2, 1.2, 20, c, /*wrap_u=*/true, /*wrap_v=*/false, /*flip=*/false,
            /*thickness=*/0.06);
    }, "sky");

    // --------------------------------------------------------------------------
    //  7. Helicoid -- a spiral ramp, and 8. its relative the catenoid
    // --------------------------------------------------------------------------
    show("helicoid", [](const add::Color& c) {
        add::parametric(
            [](double u, double v) -> add::Point { return {v * add::cos(u), 0.45 * u, v * add::sin(u)}; },
            0, 3 * TAU, 120, -1.2, 1.2, 10, c, /*wrap_u=*/false, /*wrap_v=*/false, /*flip=*/false,
            /*thickness=*/0.06);
    }, "purple");

    show("catenoid", [](const add::Color& c) {
        add::parametric(
            [](double u, double v) -> add::Point {
                return {add::cosh(v) * add::cos(u), v, add::cosh(v) * add::sin(u)};
            },
            0, TAU, 48, -1.4, 1.4, 20, c, /*wrap_u=*/true, /*wrap_v=*/false, /*flip=*/false,
            /*thickness=*/0.05);
    }, "magenta");

    // --------------------------------------------------------------------------
    //  9. Monkey saddle -- three valleys instead of two
    // --------------------------------------------------------------------------
    show("monkey saddle", [](const add::Color& c) {
        add::parametric(
            [](double u, double v) -> add::Point {
                return {u, add::detail::py_pow(u, 3) - 3 * u * v * v, v};
            },
            -1.3, 1.3, 40, -1.3, 1.3, 40, c, /*wrap_u=*/false, /*wrap_v=*/false, /*flip=*/false,
            /*thickness=*/0.05);
    }, "brown");

    // -------------------------------------------------------------------------
    // 10. Egg box -- y = sin(x) cos(z), the surface everybody draws first
    // -------------------------------------------------------------------------
    show("egg box", [](const add::Color& c) {
        add::parametric(
            [](double u, double v) -> add::Point { return {u, add::sin(u) * add::cos(v), v}; },
            -4, 4, 48, -4, 4, 48, c, /*wrap_u=*/false, /*wrap_v=*/false, /*flip=*/false,
            /*thickness=*/0.12);
    }, "navy");

    // -------------------------------------------------------------------------
    // 11. Torus knot tube -- a curve given thickness by sweeping a circle
    //     (the surface is the function knot(), written above main)
    // -------------------------------------------------------------------------
    show("torus knot", [](const add::Color& c) {
        add::parametric(knot, 0, TAU, 220, 0, TAU, 18, c,
                        /*wrap_u=*/true, /*wrap_v=*/true);
    }, "cyan");

    // -------------------------------------------------------------------------
    // 12. Pseudosphere -- constant negative curvature, the "trumpet"
    // -------------------------------------------------------------------------
    show("pseudosphere", [](const add::Color& c) {
        add::parametric(
            [](double u, double v) -> add::Point {
                return {add::cos(v) / add::cosh(u), u - add::tanh(u),
                        add::sin(v) / add::cosh(u)};
            },
            -3.5, 3.5, 60, 0, TAU, 40, c, /*wrap_u=*/false, /*wrap_v=*/true);
    }, "silver");


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
    add::save("surfaces_classic.off");
}

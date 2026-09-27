// 08 -- one formula, a hundred shapes: the superformula.
//
// Johan Gielis noticed in 2003 that a single equation describes starfish,
// flowers, diatoms, crystals and plain circles, depending on six numbers:
//
//     r(t) = ( |cos(m t / 4) / a| ^ n2  +  |sin(m t / 4) / b| ^ n3 ) ^ (-1 / n1)
//
// Wrap two of those radial functions around each other and you get a surface.
// Changing one number changes the creature -- which is exactly the kind of
// "one parameter controls the shape" the assignment asks for.
#include "add.hpp"

const double TAU = 2 * add::pi;


// The superformula radius at angle ``t``.
double super_r(double t, double m, double n1, double n2, double n3, double a = 1.0, double b = 1.0) {
    double p = add::detail::py_pow(std::abs(add::cos(m * t / 4.0) / a), n2);
    double q = add::detail::py_pow(std::abs(add::sin(m * t / 4.0) / b), n3);
    double s = p + q;
    if (s < 1e-12)
        return 0.0;
    return add::detail::py_pow(s, -1.0 / n1);
}


// A 3D surface from two sets of superformula parameters.
add::SurfaceFn supershape(const std::vector<double>& p1, const std::vector<double>& p2) {
    auto S = [p1, p2](double u, double v) -> add::Point {      // u around the equator, v pole to pole
        double r1 = super_r(u, p1[0], p1[1], p1[2], p1[3]);
        double r2 = super_r(v, p2[0], p2[1], p2[2], p2[3]);
        return {r1 * add::cos(u) * r2 * add::cos(v),
                r2 * add::sin(v),
                r1 * add::sin(u) * r2 * add::cos(v)};
    };
    return S;
}


//: (name, equator parameters, meridian parameters)
struct Shape {
    std::string name;
    std::vector<double> p1, p2;
};
const std::vector<Shape> SHAPES = {
    {"sphere",      {0, 1, 1, 1},       {0, 1, 1, 1}},
    {"star",        {5, 0.4, 0.4, 0.4}, {5, 0.4, 0.4, 0.4}},
    {"flower",      {6, 1, 7, 8},       {6, 1, 7, 8}},
    {"starfish",    {5, 0.2, 1.7, 1.7}, {5, 0.2, 1.7, 1.7}},
    {"cube-ish",    {4, 40, 40, 40},    {4, 40, 40, 40}},
    {"diamond",     {4, 1, 1, 1},       {4, 1, 1, 1}},
    {"pillow",      {4, 1, 1, 1},       {0, 1, 1, 1}},
    {"gear",        {12, 15, 15, 15},   {12, 15, 15, 15}},
    {"seed pod",    {3, 4.5, 10, 10},   {3, 4.5, 10, 10}},
    {"shell",       {7, 0.2, 1.7, 1.7}, {2, 0.5, 1.7, 1.7}},
    {"coral",       {8, 0.5, 0.5, 8},   {8, 0.5, 0.5, 8}},
    {"bulb",        {2, 0.7, 0.3, 0.2}, {2, 0.7, 0.3, 0.2}},
};


int main() {
    const double CELL = 3.0;
    int columns = 4;
    std::vector<add::Mesh> shown;
    for (int i = 0; i < (int)SHAPES.size(); ++i) {
        const auto& [name, p1, p2] = SHAPES[i];
        add::parametric(supershape(p1, p2), -add::pi, add::pi, 120,
                        -add::pi / 2, add::pi / 2, 90,
                        add::hsv(i / double(SHAPES.size()), 0.55, 0.95),
                        /*wrap_u=*/true);
        // layer() must be taken before anything else is drawn, or the next shape
        // would scoop up the ones already placed.
        shown.push_back(add::place(add::fit(add::layer(), 2.2), {0, 0, 0}));
        std::printf("%2d. %s\n", i + 1, name.c_str());
    }

    for (int i = 0; i < (int)shown.size(); ++i) {
        const add::Mesh& M = shown[i];
        add::mesh(add::move(M, {(i % columns) * CELL, 0, (i / columns) * CELL}));
    }

    add::check();
    add::save("supershapes.off");
}

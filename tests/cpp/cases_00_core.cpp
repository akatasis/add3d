#include "parity.hpp"

CASE(numbers) {
    const double xs[] = {0.1, 1e-5, 2.5, -3.0, 1.0 / 3, 1e16, 123456789.123456789, -0.0, 5e-324, 0.000123, 1e15 + 0.5};
    for (double x : xs) record(add::detail::num(x));
    for (double x : xs) record(x);
}

CASE(colors) {
    record(add::Color("red"));
    record(add::Color("#78beff66"));
    record(add::Color(1.0, 0.5, 0.25));
    record(add::Color(2.0, 0.5, 0.25));
    record(add::Color(300, -5, 128));
    record(add::transparent("sky", 0.35));
    record(add::hsv(0.3));
    record(add::hsv(-0.25, 0.5, 0.8));
    record(add::gradient(0.3, "red", "blue"));
    record(add::random_color(7));
}

CASE(random_numbers) {
    add::seed(7);
    for (int i = 0; i < 5; ++i) record(add::random());
    for (int i = 0; i < 5; ++i) record(add::randint(1, 6));
    for (int i = 0; i < 5; ++i) record(add::uniform(-2.0, 3.0));
    add::seed(-12345678901LL);
    record(add::random());
    record(add::randint(0, 1000000000000LL));
}

CASE(mesh_basics) {
    add::Mesh M;
    M.add_polygon({{0, 0, 0}, {1, 0, 0}, {1, 1, 0}, {0.5, 1.5, 0}, {0, 1, 0}}, "red");
    M.add_polygon({{0, 0, 1}, {1, 0, 1}, {1, 1, 1}}, add::transparent("blue", 0.25));
    add::mesh(M);
    add::push();
    add::mesh(add::move(M, {2, 0, 0}));
    add::Mesh moved = add::pop();
    add::mesh(add::rotateY(moved, 0.7, {1, 0, 0}));
    save_case();
}

CASE(gauss_numbers) {
    add::seed(3);
    for (int i = 0; i < 5; ++i) record(add::gauss(2.5, 1.2));
    add::Random r(11);
    double a = r.gauss(2.5, 1.2), b = r.gauss(2.5, 1.2), c = r.gauss();
    record(a); record(b); record(c);
    r.seed(11);
    record(r.gauss(2.5, 1.2));
}

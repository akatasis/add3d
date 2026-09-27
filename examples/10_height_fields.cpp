// 10 -- graphs of two-variable functions, y = f(x, z).
//
// The gentlest way into parametric surfaces: keep x and z as they are and let
// the function decide the height.  ``add::grid`` does exactly this, and
// ``add::parametric`` does it when you write ``{u, f(u, v), v}``.
#include "add.hpp"

const double CELL = 3.6;
const double R = 3.2;                         // each patch covers -R .. R in x and z
std::vector<std::pair<std::string, add::Mesh>> shown;


void show(const std::string& name, const std::function<double(double, double)>& f, const add::Color& col,
          int detail = 90, double thickness = 0.06) {
    add::parametric([&](double u, double v) -> add::Point { return {u, f(u, v), v}; },
                    -R, R, detail, -R, R, detail,
                    col, /*wrap_u=*/false, /*wrap_v=*/false, /*flip=*/false, /*thickness=*/thickness);
    shown.push_back({name, add::place(add::fit(add::layer(), 2.6), {0, 0, 0})});
}


int main() {
    show("sin(x) + cos(z)", [](double x, double z) { return add::sin(x) + add::cos(z); }, "red");
    show("sin(x) * cos(z)", [](double x, double z) { return add::sin(x) * add::cos(z); }, "orange");
    show("ripple", [](double x, double z) {
        return add::sin(3 * add::sqrt(x * x + z * z))
               / (1 + x * x + z * z) * 4;
    }, "gold");
    show("saddle x^2 - z^2", [](double x, double z) { return (x * x - z * z) / 4.0; }, "lime");
    show("monkey saddle", [](double x, double z) {
        return (add::detail::py_pow(x, 3) - 3 * x * z * z) / 8.0;
    }, "teal");
    show("gaussian hill", [](double x, double z) { return 3 * add::exp(-(x * x + z * z) / 3.0); }, "sky");
    show("peaks", [](double x, double z) {
        return 3 * add::detail::py_pow(1 - x, 2) * add::exp(-x * x - add::detail::py_pow(z + 1, 2)) / 3
               - 10 * (x / 5 - add::detail::py_pow(x, 3) - add::detail::py_pow(z, 5))
                 * add::exp(-x * x - z * z) / 3
               - add::exp(-add::detail::py_pow(x + 1, 2) - z * z) / 9;
    }, "navy");
    show("sombrero", [](double x, double z) {
        return 3 * add::sin(add::sqrt(x * x + z * z) + 1e-9)
               / (add::sqrt(x * x + z * z) + 1e-9);
    }, "purple");
    show("checkerboard", [](double x, double z) {
        // (for a negative odd sum C++'s % gives -1 where Python's gives 1: either way it is not 0)
        return 0.8 * ((int(add::floor(x)) + int(add::floor(z))) % 2 != 0 ? 1 : -1);
    }, "magenta", /*detail=*/64, /*thickness=*/0.1);
    show("|x| + |z| cone", [](double x, double z) { return -(std::abs(x) + std::abs(z)) / 2.0; }, "brown");
    show("interference", [](double x, double z) {
        return (add::sin(4 * add::sqrt(add::detail::py_pow(x - 1.2, 2) + z * z))
                + add::sin(4 * add::sqrt(add::detail::py_pow(x + 1.2, 2) + z * z)));
    }, "silver");
    show("plateau", [](double x, double z) {
        return 2.0 / (1 + add::exp(-4 * (2.0 - add::sqrt(x * x + z * z))));
    }, "pink");

    int columns = 4;
    for (int i = 0; i < (int)shown.size(); ++i) {
        const auto& [name, M] = shown[i];
        add::mesh(add::move(M, {(i % columns) * CELL, 0, (i / columns) * CELL}));
        std::printf("%2d. %s\n", i + 1, name.c_str());
    }

    add::check();
    add::save("height_fields.off");
}

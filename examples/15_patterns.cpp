// 15 -- one shape, many copies.
//
// Modelling by repetition: build one piece, then let the library stamp it out.
//
//     add::array_linear(M, step, n)          a row
//     add::array_grid(M, steps, counts)      a block
//     add::array_radial(M, n, axis, centre)  a ring (``rise`` makes it a spiral)
//     add::array_mirror(M, point, normal)    the piece and its reflection
//     add::repeat(M, n, step)                anything else you can write
//
// ``repeat`` is the general one: you hand it a function that says where copy
// number ``i`` goes, and it does the rest.
#include "add.hpp"

const double TAU = 2 * add::pi;
const double CELL = 5.0;
std::vector<std::pair<std::string, add::Mesh>> shown;


// The piece that gets repeated: a small pillar with a ball on top.
add::Mesh unit(const add::Color& col) {
    add::cuboid({0, 0.4, 0}, {0.5, 0.8, 0.5}, col);
    add::sphere({0, 1.0, 0}, 0.3, 10, col);
    return add::layer();
}


void show(const std::string& name, const add::Mesh& M, double size = 3.6) {
    shown.push_back({name, add::place(add::fit(M, size), {0, 0, 0})});
}


int main() {
    show("a row", add::array_linear(unit("red"), {1.0, 0, 0}, 8));

    show("a block", add::array_grid(unit("orange"), {1.0, 1.0, 1.0}, {5, 3, 5}));

    show("a ring", add::array_radial(add::move(unit("gold"), {3, 0, 0}), 18));

    show("a spiral staircase",
         add::array_radial(add::move(unit("lime"), {2.5, 0, 0}), 40, {0, 1, 0}, {0, 0, 0}, 2.0 * add::pi,
                           0.22));                  // axis, centre and angle as by default; rise = 0.22

    show("mirrored pair",
         add::array_mirror(add::move(unit("teal"), {1.2, 0, 0}), {0, 0, 0}, {1, 0, 0}));

    // --- repeat(): copy number i decides its own transformation ----------------
    show("shrinking tower",
         add::repeat(unit("sky"), 22,
                     [](const add::Mesh& M, int i) {
                         return add::move(add::zoom(M, add::detail::py_pow(0.92, i), add::Point{0, 0, 0}),
                                          {0, i * 0.55, 0});
                     }));

    show("fanned arch",
         add::repeat(unit("purple"), 24,
                     [](const add::Mesh& M, int i) {
                         return add::rotate(add::move(M, {0, 3.2, 0}),
                                            {0, 0, 1}, add::pi * i / 23.0 - add::pi / 2);
                     }));

    show("double helix",
         add::repeat(unit("magenta"), 60,
                     [](const add::Mesh& M, int i) {
                         return add::move(
                             add::rotate(M, {0, 1, 0}, i * 0.28),
                             {2.2 * add::cos(i * 0.28), i * 0.12,
                              2.2 * add::sin(i * 0.28)});
                     }));

    show("torus of cubes",
         add::repeat(unit("brown"), 160,
                     [](const add::Mesh& M, int i) {
                         return add::move(
                             add::rotate(M, {0, 1, 0}, (i % 20) * TAU / 20),
                             {(4 + 1.2 * add::cos(i * TAU / 8)) * add::cos(i * TAU / 20),
                              1.2 * add::sin(i * TAU / 8),
                              (4 + 1.2 * add::cos(i * TAU / 8)) * add::sin(i * TAU / 20)});
                     }));

    // --- copies laid out on a parametric surface ------------------------------
    // The golden-angle spiral: the way sunflower seeds are packed.
    auto on_a_sphere = [](const add::Mesh& M, int i) {
        int n = 120;
        double y = 1 - 2.0 * i / (n - 1.0);
        double r = add::sqrt(std::max(0.0, 1 - y * y));
        double a = i * add::pi * (3 - add::sqrt(5));
        add::Point p = {3.2 * r * add::cos(a), 3.2 * y, 3.2 * r * add::sin(a)};
        add::Mesh turned = add::rotate(M, {1, 0, 0}, add::acos(std::max(-1.0, std::min(1.0, y))));
        return add::move(add::rotateY(turned, -a), p);
    };

    show("seeds on a sphere", add::repeat(unit("navy"), 120, on_a_sphere));

    // --- a colour ramp applied to the whole pattern ---------------------------
    add::Mesh tower = add::repeat(unit("white"), 40,
                                  [](const add::Mesh& M, int i) {
                                      return add::move(add::rotateY(M, i * 0.5),
                                                       {0, i * 0.35, 0});
                                  });
    show("colour by height",
         add::color_by(tower, [](const add::Point& p) { return add::hsv(p[1] / 14.0, 0.7, 1.0); }));

    // --- scattering with random numbers ---------------------------------------
    add::seed(7);
    show("random scatter",
         add::repeat(unit("silver"), 90,
                     [](const add::Mesh& M, int /*i*/) {
                         // (the three random numbers are drawn in Python's order: size, x, z)
                         double s = add::uniform(0.4, 1.3);
                         double x = add::uniform(-4, 4);
                         double z = add::uniform(-4, 4);
                         return add::move(add::zoom(M, s, add::Point{0, 0, 0}), {x, 0, z});
                     }));

    int columns = 4;
    for (int i = 0; i < (int)shown.size(); ++i) {
        const auto& [name, M] = shown[i];
        add::mesh(add::move(M, {(i % columns) * CELL, 0, (i / columns) * CELL}));
        std::printf("%2d. %s\n", i + 1, name.c_str());
    }

    add::mesh(add::limit_colors(add::layer(), 50));   // at most 50 colours, so the .obj suits Sketchfab
    add::check();
    add::save("patterns.off");
}

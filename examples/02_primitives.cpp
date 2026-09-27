// 02 -- every ready-made shape, laid out on a grid.
//
// A map of the library: if you can name it, it is probably here.
#include "add.hpp"

const double STEP = 3.0;


// Position of cell (i, j) on the display grid.
add::Point at(int i, int j) {
    return {i * STEP, 0, j * STEP};
}


int main() {
    // --- row 0: flat-sided solids ----------------------------------------------
    add::Point c = at(0, 0); add::box(c, 1.6, "red");
    c = at(1, 0); add::cuboid(c, {2.2, 1.0, 1.4}, "orange");
    c = at(2, 0); add::frame(c, 1.8, 0.22, "gold");
    c = at(3, 0); add::pyramid(c, 1.8, 1.8, "lime");
    c = at(4, 0); add::prism({{0, 0}, {1.2, 0}, {0.6, 1.2}}, 1.8, "teal", c, {0, 1, 0});
    c = at(5, 0);
    std::vector<add::Cell> cells;             // the cells (x, y, z) with x + y + z even
    for (int x = 0; x < 3; ++x)
        for (int y = 0; y < 3; ++y)
            for (int z = 0; z < 3; ++z)
                if ((x + y + z) % 2 == 0) cells.push_back({x, y, z});
    add::voxels(cells, 0.6, {c[0] - 0.9, c[1] - 0.9, c[2] - 0.9}, "sky");

    // --- row 1: the five Platonic solids ---------------------------------------
    std::vector<std::string> names = {"tetrahedron", "cube", "octahedron",
                                      "dodecahedron", "icosahedron"};
    for (int i = 0; i < (int)names.size(); ++i) {
        std::string name = names[i];
        add::polyhedron(name, at(i, 1), 1.0, add::hsv(i / 5.0, 0.55, 0.95));
    }

    // --- row 2: round solids ---------------------------------------------------
    c = at(0, 2); add::sphere(c, 1.0, 16, "blue");
    c = at(1, 2); add::uvsphere(c, 1.0, 28, 14, "navy");
    c = at(2, 2); add::ellipsoid(c, {1.2, 0.6, 0.9}, 14, "purple");
    c = at(3, 2); add::torus(c, 0.9, 0.35, 40, 20, "magenta");
    c = at(4, 2); add::capsule({c[0], c[1] - 0.6, c[2]}, {c[0], c[1] + 0.6, c[2]},
                               0.5, 24, "pink");
    c = at(5, 2); add::polyhedron("icosahedron", c, 1.0, "silver");

    // --- row 3: tubes and cones ------------------------------------------------
    // (A list of functions: all of these take the same arguments A, B, r, k, colour.)
    using Shape = void (*)(const add::Point&, const add::Point&, double, int, const add::Color&);
    std::vector<Shape> tubes = {add::cylinder, add::tube, add::cup};
    for (int i = 0; i < (int)tubes.size(); ++i) {
        Shape fn = tubes[i];
        c = at(i, 3);
        fn({c[0], c[1] - 0.9, c[2]}, {c[0], c[1] + 0.9, c[2]}, 0.6, 24, "cyan");
    }
    std::vector<Shape> cones = {add::cone, add::cone_open};
    for (int i = 0; i < (int)cones.size(); ++i) {
        Shape fn = cones[i];
        c = at(3 + i, 3);
        fn({c[0], c[1] - 0.9, c[2]}, {c[0], c[1] + 0.9, c[2]}, 0.7, 24, "green");
    }
    c = at(5, 3);
    add::frustum({c[0], c[1] - 0.9, c[2]}, {c[0], c[1] + 0.9, c[2]}, 0.8, 0.35, 24,
                 "brown");

    // --- row 4: hollow and flat ------------------------------------------------
    c = at(0, 4);
    add::pipe({c[0], c[1] - 0.9, c[2]}, {c[0], c[1] + 0.9, c[2]}, 0.8, 0.5, 28,
              "grey");
    c = at(1, 4); add::disc(c, {c[0], c[1] + 1, c[2]}, 1.0, 32, "yellow");
    c = at(2, 4); add::ring(c, {c[0], c[1] + 1, c[2]}, 1.0, 0.5, 32, "yellow");
    c = at(3, 4); add::grid(c, {2.2, 2.2}, 14, 14, "lime",
                            /*height=*/[](double x, double z) {
                                return 0.3 * add::sin(3 * x) * add::cos(3 * z);
                            });
    c = at(4, 4); add::arrow({c[0], c[1] - 1, c[2]}, {c[0], c[1] + 1, c[2]}, 0.12,
                             "red");
    c = at(5, 4); add::helix(c, 0.7, 0.35, 3, 160, 0.12, 10, "gold");

    add::axes({-3, 0, -3}, 2.5);
    add::check();
    add::save("primitives.off");
}

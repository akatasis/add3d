// 16 -- adding, cutting and intersecting solids.
//
//     add::union_(A, B)       everything in either, with the buried walls gone
//     add::intersect(A, B)    only what they have in common
//     add::difference(A, B)   A with B carved out of it
//     add::cut(A, point, n)   a quick straight slice with a plane
//
// These need *closed* solids -- ``add::check()`` will tell you whether yours is
// closed.  The freshly exposed surface keeps the colour of the tool that cut
// it, so a hole is easy to see; pass a colour to difference to override that.
#include "add.hpp"

const double CELL = 4.2;
std::vector<std::pair<std::string, add::Mesh>> shown;


// A box and a ball that overlap -- the standard demonstration.
std::pair<add::Mesh, add::Mesh> pair() {
    add::box({0, 0, 0}, 2.0, "red");
    add::Mesh a = add::layer();
    add::sphere({0.9, 0.9, 0.9}, 1.3, 24, "blue");
    add::Mesh b = add::layer();
    return {a, b};
}


void show(const std::string& name, const add::Mesh& M, double size = 3.0) {
    shown.push_back({name, add::place(add::fit(M, size), {0, 0, 0})});
}


int main() {
    add::Mesh a, b;
    std::tie(a, b) = pair();
    show("merge (no boolean)", add::merge({a, b}));
    show("union", add::union_(a, b));
    show("difference", add::difference(a, b));
    show("intersection", add::intersect(a, b));

    // --- a hollow ball: a sphere minus a smaller sphere, then sliced open ------
    add::sphere({0, 0, 0}, 1.6, 32, "gold");
    add::Mesh outer = add::layer();
    add::sphere({0, 0, 0}, 1.3, 32, "brown");
    add::Mesh inner = add::layer();
    add::Mesh shell = add::difference(outer, inner);
    show("hollow ball, cut open", add::cut(shell, {0, 0, 0}, {0.4, 0.3, 1.0}));

    // --- a cube with all twelve edges rounded, the CSG way ---------------------
    add::box({0, 0, 0}, 2.0, "teal");
    add::Mesh cube = add::layer();
    add::sphere({0, 0, 0}, 1.32, 40, "teal");
    add::Mesh ball = add::layer();
    show("rounded cube", add::intersect(cube, ball));

    // --- a cross drilled through a block --------------------------------------
    add::box({0, 0, 0}, 2.0, "lime");
    add::Mesh block = add::layer();
    std::vector<add::Mesh> drills;
    for (const std::vector<int>& axis : std::vector<std::vector<int>>{{1, 0, 0}, {0, 1, 0}, {0, 0, 1}}) {
        add::cylinder({double(-2 * axis[0]), double(-2 * axis[1]), double(-2 * axis[2])},
                      {double(2 * axis[0]), double(2 * axis[1]), double(2 * axis[2])}, 0.55, 32, "black");
        drills.push_back(add::layer());
    }
    show("three holes", add::difference(block, drills));

    // --- a ring made by subtracting a cylinder from a torus -------------------
    add::torus({0, 0, 0}, 1.4, 0.55, 64, 28, "magenta");
    add::Mesh ring = add::layer();
    add::cuboid({0, 1.0, 0}, {6, 1.2, 6}, "silver");
    add::Mesh knife = add::layer();
    show("torus, sliced", add::difference(ring, knife));

    // --- letters cut out of a slab --------------------------------------------
    add::cuboid({0, 0, 0}, {4.0, 0.7, 1.6}, "silver");
    add::Mesh slab = add::layer();
    std::vector<add::Mesh> stamps;
    for (double x : {-1.3, 0.0, 1.3}) {
        add::cylinder({x, -1, 0}, {x, 1, 0}, 0.45, 28, "navy");
        stamps.push_back(add::layer());
    }
    show("perforated slab", add::difference(slab, stamps));

    // --- a pipe junction: union of two tubes, then hollowed out ---------------
    add::cylinder({0, -1.6, 0}, {0, 1.6, 0}, 0.8, 40, "orange");
    add::Mesh t1 = add::layer();
    add::cylinder({-1.6, 0, 0}, {1.6, 0, 0}, 0.8, 40, "orange");
    add::Mesh t2 = add::layer();
    add::cylinder({0, -1.8, 0}, {0, 1.8, 0}, 0.6, 40, "navy");
    add::Mesh h1 = add::layer();
    add::cylinder({-1.8, 0, 0}, {1.8, 0, 0}, 0.6, 40, "navy");
    add::Mesh h2 = add::layer();
    show("pipe elbow", add::difference(add::union_(t1, t2), {h1, h2}));

    // --- symmetric difference: what is in one but not both --------------------
    std::tie(a, b) = pair();
    show("symmetric difference", add::symmetric_difference(a, b));

    // --- a stack of slices: cut() used repeatedly -----------------------------
    add::sphere({0, 0, 0}, 1.6, 36, "purple");
    ball = add::layer();
    std::vector<add::Mesh> slices;
    for (int i = 0; i < 6; ++i) {
        double y = -1.6 + 3.2 * i / 6.0;
        // cut() keeps the side the normal points AWAY from, so the first call
        // keeps everything below y + 0.42 and the second everything above y.
        add::Mesh piece = add::cut(add::cut(ball, {0, y + 0.42, 0}, {0, 1, 0}),
                                   {0, y, 0}, {0, -1, 0});
        slices.push_back(add::move(piece, {0, i * 0.18, 0}));
    }
    show("sliced ball", add::merge(slices));

    // --- a gear, built from a cylinder and a ring of teeth --------------------
    add::cylinder({0, -0.3, 0}, {0, 0.3, 0}, 1.5, 64, "gold");
    add::Mesh disc = add::layer();
    add::cuboid({1.6, 0, 0}, {0.7, 0.62, 0.42}, "gold");
    add::Mesh tooth = add::layer();
    add::cylinder({0, -0.5, 0}, {0, 0.5, 0}, 0.45, 32, "black");
    add::Mesh bore = add::layer();
    add::Mesh gear = add::difference(add::union_(disc, add::array_radial(tooth, 16)), bore);
    show("gear", gear);

    int columns = 4;
    for (int i = 0; i < (int)shown.size(); ++i) {
        const auto& [name, M] = shown[i];
        add::mesh(add::move(M, {(i % columns) * CELL, 0, (i / columns) * CELL}));
        std::printf("%2d. %-24s %6d faces\n", i + 1, name.c_str(), (int)M.polygons());
    }

    add::check();
    add::save("booleans.off");
}

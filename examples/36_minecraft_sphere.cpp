// 36 -- the "Minecraft sphere": a cube blown up into a ball, and a ball of blocks.
//
// Three ways to make a sphere stand side by side:
//
// 1. ``cube_sphere`` -- the construction of the course's Maple worksheet
//    ``sfera(m)``: each of the six faces of a cube is covered with an m x m
//    grid whose lines are spaced by ``cot(pi/4 + pi/2 * i/m)`` (so that the
//    cells stay the same size after the bend), and every grid point is
//    pushed out onto the sphere by dividing by its length.  Six patches,
//    ``6 * m * m`` quads, no poles.  ``add::quadsphere`` is the same thing in
//    one call.
// 2. ``block_sphere`` -- the Minecraft way: every unit block whose centre is
//    within the radius, ``add::voxels`` draws only the outside walls.
// 3. ``add::sphere`` -- the geodesic sphere of triangles (example 38 shows
//    where it comes from).
//
// Run with ``--fine`` for the detailed version (``minecraft_sphere_fine.off``,
// about 500 000 polygons); the default is the Sketchfab-sized one.
//
// Parameter: ``M`` (grid lines per cube face) and ``R`` (blocks in the radius).
#include "add.hpp"


// The Maple sfera(m), written with a vertex dictionary instead of index
// arithmetic: shared corners are found by their coordinates.
add::Mesh cube_sphere(int m, const add::Point& center, double r, const std::vector<add::Color>& colors) {
    add::Mesh mesh;
    std::map<std::array<double, 3>, int> index;

    auto vertex = [&](const add::Point& p) {
        std::array<double, 3> key = {add::detail::py_round(p[0], 9), add::detail::py_round(p[1], 9),
                                     add::detail::py_round(p[2], 9)};
        if (!index.count(key))
            index[key] = mesh.add_vertex({center[0] + r * p[0], center[1] + r * p[1], center[2] + r * p[2]});
        return index[key];
    };

    auto line = [&](int i) {                              // cot(pi/4 + pi/2 * i/m): from 1 down to -1
        return 1.0 / add::tan(add::pi / 4 + add::pi / 2 * i / m);
    };

    // face 1 is z = 1; the other five are the same grid turned around
    std::vector<std::function<add::Point(double, double, double)>> sides = {
        [](double x, double y, double z) { return add::Point{x, y, z}; },
        [](double x, double y, double z) { return add::Point{-z, y, x}; },
        [](double x, double y, double z) { return add::Point{-x, y, -z}; },
        [](double x, double y, double z) { return add::Point{z, y, -x}; },
        [](double x, double y, double z) { return add::Point{x, z, -y}; },
        [](double x, double y, double z) { return add::Point{x, -z, y}; }};
    for (const auto& side : sides) {
        for (int i = 0; i < m; ++i) {
            for (int j = 0; j < m; ++j) {
                add::Face corners;
                for (auto [a, b] : std::vector<std::pair<int, int>>{{i, j}, {i + 1, j}, {i + 1, j + 1}, {i, j + 1}}) {
                    double x = line(a), y = line(b);
                    double d = add::sqrt(x * x + y * y + 1);           // push out onto the sphere
                    corners.push_back(vertex(side(x / d, y / d, 1 / d)));
                }
                mesh.add_face(corners, colors[(i + j) % 2]);   // chequered
            }
        }
    }
    return add::fix_normals(mesh);                        // all six patches facing outward
}


void block_sphere(int radius, const add::Point& center, double size,
                  const std::function<add::Color(int, int, int)>& paint) {
    std::vector<add::Cell> cells;
    for (int i = -radius; i < radius + 1; ++i)
        for (int j = -radius; j < radius + 1; ++j)
            for (int k = -radius; k < radius + 1; ++k)
                if (i * i + j * j + k * k <= radius * radius)
                    cells.push_back({i, j, k});
    add::Point origin = {center[0] - size / 2.0, center[1] - size / 2.0, center[2] - size / 2.0};
    add::voxels(cells, size, origin, paint);
}


int main(int argc, char** argv) {
    bool FINE = false;                                    // (Python: "--fine" in sys.argv)
    for (int i = 0; i < argc; ++i)
        if (std::string(argv[i]) == "--fine")
            FINE = true;
    const int M = FINE ? 300 : 40;                        // 6 * M * M quads
    const int R = FINE ? 40 : 12;                         // blocks from the centre to the skin

    const double SPACING = 7.5;
    // 1. the Maple sphere
    add::mesh(cube_sphere(M, {-SPACING, 0, 0}, 3, {{70, 130, 220}, {40, 80, 160}}));
    // 2. the ball of blocks, painted like a planet: grass on top, dirt, then stone
    auto paint = [&](int /*i*/, int j, int /*k*/) -> add::Color {
        int y = j - R;                                    // cell index -> height from the centre
        if (y > R * 0.55)
            return {90, 170, 60};
        if (y > 0)
            return {140, 95, 55};
        return {125, 125, 130};
    };

    block_sphere(R, {0, 0, 0}, 3.0 / R, paint);
    // 3. the geodesic sphere for comparison
    add::sphere({SPACING, 0, 0}, 3, FINE ? 60 : 20, {230, 80, 60});

    add::text("MAPLE", {-SPACING, -3.6, 3.6}, 0.6, std::nullopt, "navy", {1, 0, 0}, {0, 0, -1},
              "center");
    add::text("BLOCKS", {0, -3.6, 3.6}, 0.6, std::nullopt, "navy", {1, 0, 0}, {0, 0, -1},
              "center");
    add::text("GEODESIC", {SPACING, -3.6, 3.6}, 0.6, std::nullopt, "navy", {1, 0, 0}, {0, 0, -1},
              "center");

    add::check();
    add::save(FINE ? "minecraft_sphere_fine.off" : "minecraft_sphere.off");
}

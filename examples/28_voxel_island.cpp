// 28 -- a voxel island.
//
// Block worlds are height maps: a table of integers says how many cubes
// stand on each cell, and ``heightmap`` builds only the visible faces of the
// whole thing in one go.  The colour function paints each *layer* --
// water, sand, grass, rock, snow -- so the terrain colours itself.
// ``pixels`` draws a flag and a signpost from strings of characters;
// ``voxels`` places single cubes for the campfire, and trees are scattered
// on the surface with ``random_points`` reading the same height table.
//
// Parameters: ``SIZE`` (cells across), ``SEED``.
#include "add.hpp"

const int SIZE = 44;
const int SEED = 3;
const double CELL = 0.5;

const add::Color WATER = {50, 120, 200}, SAND = {225, 205, 150}, GRASS = {95, 165, 75}, ROCK = {130, 125, 120},
                 SNOW = "white";

int main() {
    add::Random rng(SEED);

    // --------------------------------------------------------------------------
    //  the terrain table: smooth bumps plus a little noise, rounded to cubes
    // --------------------------------------------------------------------------
    std::vector<std::array<double, 4>> bumps;
    for (int n = 0; n < 7; ++n) {
        double bx = rng.uniform(-14, 14);
        double bz = rng.uniform(-14, 14);
        double amp = rng.uniform(3, 9);
        double width = rng.uniform(5, 9);
        bumps.push_back({bx, bz, amp, width});
    }

    // (height, paint and surface are lambdas: they use rng, bumps and H, which are made here in main())
    auto height = [&](int i, int j) {
        double x = i - SIZE / 2.0, z = j - SIZE / 2.0;
        double h = 2.0 - 0.02 * add::detail::py_pow(x * x + z * z, 0.5) * 2.2;   // the island falls away
        for (const auto& [bx, bz, amp, width] : bumps)
            h += amp * add::exp(-(add::detail::py_pow(x - bx, 2) + add::detail::py_pow(z - bz, 2))
                                / add::detail::py_pow(width, 2));
        return int(add::clamp(h + rng.uniform(-0.3, 0.3), 1, 16));
    };

    std::vector<std::vector<double>> H;                  // (whole numbers: add::heightmap takes doubles)
    for (int i = 0; i < SIZE; ++i) {
        std::vector<double> row;
        for (int j = 0; j < SIZE; ++j) row.push_back(height(i, j));
        H.push_back(row);
    }
    const int SEA = 3;                                   // cells at or below this level are water

    auto paint = [&](int i, int j, int k) -> add::Color {
        double top = H[i][k];
        if (top <= SEA)
            return j == top - 1 ? WATER : add::shade(WATER, 0.8);
        if (j < SEA)
            return SAND;
        if (top < SEA + 2)
            return SAND;
        if (j >= 13)
            return SNOW;
        if (j >= 10)
            return ROCK;
        return j == top - 1 ? GRASS : add::shade(GRASS, 0.75);
    };

    add::heightmap(H, CELL, {-SIZE * CELL / 2, 0, -SIZE * CELL / 2}, paint);

    // World height of the terrain at world (x, z), for placing things.
    auto surface = [&](double x, double z) {
        int i = int(add::clamp((x + SIZE * CELL / 2) / CELL, 0, SIZE - 1));
        int k = int(add::clamp((z + SIZE * CELL / 2) / CELL, 0, SIZE - 1));
        return H[i][k] * CELL;
    };

    // --------------------------------------------------------------------------
    //  trees, a campfire, a signpost and a flag
    // --------------------------------------------------------------------------
    add::Points spots;
    for (const add::Point& p : add::random_points(120, {-10, 0, -10}, {10, 0, 10}, SEED, surface))
        if (SEA * CELL + 1.0 < p[1] && p[1] < 10 * CELL)
            spots.push_back(p);
    for (int n = 0; n < 28 && n < (int)spots.size(); ++n) {        // the first 28 spots
        // (the two random numbers first, in Python's order: C++ may evaluate arguments in any order)
        double tree_height = rng.uniform(1.6, 2.6);
        double leaf_shade = rng.uniform(0.6, 0.9);
        add::tree(spots[n], tree_height, {90, 60, 40}, add::shade(GRASS, leaf_shade),
                  n % 4 == 0 ? "pine" : "round", 10, n);
    }

    // the highest point: a flag on a pole
    std::tuple<double, int, int> peak = {H[0][0], 0, 0};    // the largest (H[i][k], i, k), as Python's max()
    for (int i = 0; i < SIZE; ++i)
        for (int k = 0; k < SIZE; ++k)
            peak = std::max(peak, std::make_tuple(H[i][k], i, k));
    auto [peak_h, peak_i, peak_k] = peak;
    double px = (peak_i + 0.5) * CELL - SIZE * CELL / 2, pz = (peak_k + 0.5) * CELL - SIZE * CELL / 2;
    double py = peak_h * CELL;
    add::cylinder({px, py, pz}, {px, py + 4.0, pz}, 0.06, 8, "silver");
    add::pixels({"yyyyyyyy", "ggggyyyy", "ggggrrrr", "rrrrrrrr"}, 0.28, {px + 0.06, py + 2.9, pz - 0.1},
                add::PALETTE(), 1);
    add::sphere({px, py + 4.05, pz}, 0.12, 4, "gold");

    // a campfire on the beach (the first random spot that lies on sand)
    add::Points beach;
    for (const add::Point& p : add::random_points(400, {-10, 0, 2}, {10, 0, 10}, SEED + 2, surface))
        if (std::abs(p[1] - (SEA + 1) * CELL) < 1e-9)
            beach.push_back(p);
    double cx = beach[0][0], cz = beach[0][2];
    double cy = surface(cx, cz);
    add::voxels({{0, 0, 0}, {1, 0, 0}, {2, 0, 0}, {0, 0, 2}, {1, 0, 2}, {2, 0, 2},
                 {0, 0, 1}, {2, 0, 1}}, CELL * 0.5, {cx - CELL * 0.75, cy, cz - CELL * 0.75}, {80, 50, 30});
    for (int n = 0; n < 6; ++n) {
        double dx = rng.uniform(-0.15, 0.15);           // (the two random numbers first, in Python's order)
        double dz = rng.uniform(-0.15, 0.15);
        add::sphere({cx + dx, cy + 0.35 + 0.22 * n, cz + dz},
                    0.28 - 0.035 * n, 3, add::gradient(n / 5.0, "yellow", "red"));
    }

    // a signpost with the island's name
    double sx = 2.0, sz = 8.0;
    double sy = surface(sx, sz);
    add::cylinder({sx, sy, sz}, {sx, sy + 1.6, sz}, 0.07, 6, {110, 80, 50});
    add::cuboid({sx, sy + 1.4, sz}, {2.6, 0.55, 0.12}, {150, 110, 70});
    add::text("SALA", {sx - 0.95, sy + 1.2, sz + 0.07}, 0.4, std::nullopt, "white",
              {1, 0, 0}, {0, 1, 0}, "left", 1.0, 6);
    add::text("SALA", {sx + 0.95, sy + 1.2, sz - 0.07}, 0.4, std::nullopt, "white",
              {-1, 0, 0}, {0, 1, 0}, "left", 1.0, 6);

    // a rowing boat of coloured cubes, moored off the beach
    add::pixels({"n....n", "nnnnnn"}, CELL, {-8.5, SEA * CELL - 0.2, 9.5},
                {{"n", {150, 90, 50}}}, 3);

    // the name of the island written on the water, flat
    add::text("VOXEL ISLAND", {-8, SEA * CELL + 0.02, -10}, 1.2, std::nullopt, add::shade(WATER, 1.3),
              {1, 0, 0}, {0, 0, -1}, "left", 1.0, 6);

    add::check();
    add::save("voxel_island.off");
}

// 24 -- a windmill on a hill.
//
// The tower is an octagon pulled up with ``extrude`` (tapering as it rises),
// the cap is a lathe, and the four sails are *one* sail copied around the
// shaft with ``array_radial`` -- so ``SAIL_ANGLE`` turns all of them at once.
// The hill is a ``grid`` with a height function; trees, bushes and tulips
// are scattered on it with ``random_points`` (which reads the same height
// function, so everything stands on the ground).
//
// Parameters: ``SAIL_ANGLE``, ``SEED``.
#include "add.hpp"

const double SAIL_ANGLE = 0.35;
const int SEED = 5;

const add::Color BRICK = {150, 75, 50};
const add::Color WOOD = {110, 75, 45};
const add::Color CLOTH = {240, 235, 220};
const add::Color THATCH = {170, 140, 80};
const add::Color GRASS = {96, 160, 72};

double hill(double x, double z) {
    return 2.2 * add::exp(-((x * x + z * z) / 60.0)) + 0.25 * add::sin(0.8 * x) * add::cos(0.7 * z);
}

add::Color meadow(double x, double z) {
    double t = add::clamp(add::remap(hill(x, z), 0.0, 2.2, 0.0, 1.0));
    return add::lerp(add::shade(GRASS, 0.75), GRASS, t);
}

const double TOP = hill(0, 0);
const double H = 7.0;

// Profile of the cap: a rounded, slightly pointed roof.
add::Point2 cap(double t) {
    return {t < add::pi / 2 ? 2.0 * add::detail::py_pow(add::cos(t), 0.7) : 0.0,
            TOP + H + 0.2 + 2.2 * add::sin(t)};
}

int main() {
    add::Random rng(SEED);

    // --------------------------------------------------------------------------
    //  the hill
    // --------------------------------------------------------------------------
    add::grid({0, 0, 0}, {36, 36}, 72, 72, meadow, hill, 0.4);

    // --------------------------------------------------------------------------
    //  the mill: brick base, tapering octagonal tower, cap, door, windows
    // --------------------------------------------------------------------------
    add::extrude(add::profile_polygon(8, 2.6), {0, H, 0}, BRICK, 1,
                 0.0, [](double t) { return 1.0 - 0.3 * t; }, {0, TOP - 0.3, 0});
    // the brick courses are painted on as thin rings
    for (int i = 0; i < 14; ++i) {
        double y = TOP + 0.5 * i;
        add::pipe({0, y, 0}, {0, y + 0.04, 0}, 2.62 - 0.78 * i / 14.0, 2.5 - 0.78 * i / 14.0,
                  8, add::shade(BRICK, 0.7));
    }
    add::cylinder({0, TOP + H - 0.35, 0}, {0, TOP + H + 0.2, 0}, 1.95, 8, WOOD);           // the stage

    add::revolve(cap, {0, 0, 0}, {0, 1, 0}, 0, add::pi / 2, 24, 32, THATCH);

    add::arch({-0.55, TOP, 2.3}, {0.55, TOP, 2.3}, 0.6, {0.2, 0.25}, WOOD);                // the door
    add::cuboid({0, TOP + 0.65, 2.32}, {1.1, 1.3, 0.12}, add::shade(WOOD, 0.6));
    add::stairs({0, TOP - 0.45, 3.6}, 3, 1.6, 0.15, 0.45, {130, 130, 125}, {0, 0, -1});
    for (int i = 0; i < 3; ++i) {                                                          // windows
        double y = TOP + 2.0 + 1.6 * i;
        double r = 2.6 - 0.3 * 2.6 * (y - TOP) / H;
        for (double a : {0.0, add::pi / 2, add::pi}) {
            add::Point c = {r * add::sin(a), y, r * add::cos(a)};
            add::push();
            add::cuboid({0, 0, 0}, {0.7, 0.9, 0.2}, {180, 220, 240});
            add::cuboid({0, 0, 0.02}, {0.8, 1.0, 0.16}, WOOD);
            add::Mesh win = add::pop();
            add::mesh(add::move(add::rotateY(win, a), c));
        }
    }

    // --------------------------------------------------------------------------
    //  the sails: one sail, copied four times around the shaft
    // --------------------------------------------------------------------------
    const add::Point HUB = {0, TOP + H + 1.1, 2.2};
    add::cylinder({0, HUB[1], 0.4}, {0, HUB[1], 2.6}, 0.22, 12, WOOD);                     // the shaft
    add::sphere(HUB, 0.42, 6, WOOD);

    add::push();
    add::beam(HUB, {0, HUB[1] + 5.2, HUB[2]}, 0.16, 0.2, WOOD);                            // the spar
    for (int i = 0; i < 9; ++i) {                                                          // lattice bars
        double y = HUB[1] + 1.2 + 0.45 * i;
        add::beam({-0.9, y, HUB[2] + 0.05}, {0.25, y, HUB[2] + 0.05}, 0.06, 0.06, WOOD);
    }
    add::beam({-0.9, HUB[1] + 1.2, HUB[2] + 0.05}, {-0.9, HUB[1] + 4.8, HUB[2] + 0.05},
              0.06, 0.06, WOOD);
    add::cuboid({-0.35, HUB[1] + 3.0, HUB[2] + 0.12}, {1.05, 3.6, 0.03}, CLOTH);           // the cloth
    add::Mesh sail = add::pop();
    add::Mesh sails = add::array_radial(sail, 4, {0, 0, 1}, HUB);
    add::mesh(add::rotate(sails, {0, 0, 1}, SAIL_ANGLE, HUB));

    // --------------------------------------------------------------------------
    //  the garden: a fence, trees, bushes and rows of tulips
    // --------------------------------------------------------------------------
    add::push();
    add::cylinder({0, 0, 0}, {0, 0.7, 0}, 0.05, 6, WOOD);
    add::Mesh post = add::pop();
    add::Points ring = add::points_on_circle({0, 0, 0}, 7.5, 40);
    for (add::Point& p : ring) p = {p[0], hill(p[0], p[2]), p[2]};
    add::mesh(add::along(post, ring, (int)ring.size(), 0.0, 1.0, std::nullopt, true));
    add::Points top_rail;
    for (const add::Point& p : ring) top_rail.push_back({p[0], p[1] + 0.62, p[2]});
    add::polyline(top_rail, 0.025, 6, WOOD, true);
    add::Points low_rail;
    for (const add::Point& p : ring) low_rail.push_back({p[0], p[1] + 0.35, p[2]});
    add::polyline(low_rail, 0.025, 6, WOOD, true);

    add::Points places = add::random_points(14, {-16, 0, -16}, {16, 0, 16}, SEED, hill);
    for (int i = 0; i < (int)places.size(); ++i) {
        const add::Point& p = places[i];
        if (add::distance({p[0], 0, p[2]}, {0, 0, 0}) > 9) {
            // (the two random numbers first, in Python's order: C++ may evaluate arguments in any order)
            double tree_height = rng.uniform(2.2, 3.4);
            double leaf_shade = rng.uniform(0.6, 0.9);
            add::tree(p, tree_height, WOOD, add::shade(GRASS, leaf_shade),
                      i % 3 ? "round" : "pine", 10, i);
        }
    }

    add::push();
    add::sphere({0, 0.3, 0}, 0.35, 4, add::shade(GRASS, 0.55));
    add::Mesh bush = add::pop();
    add::Points bushes;
    for (const add::Point& p : add::random_points(30, {-9, 0, -9}, {9, 0, 9}, SEED + 1, hill)) {
        double d = add::distance({p[0], 0, p[2]}, {0, 0, 0});
        if (3.3 < d && d < 7)
            bushes.push_back(p);
    }
    add::mesh(add::scatter(bush, bushes, SEED, true, {0.6, 1.5}));

    add::push();                                                                           // one tulip
    add::cylinder({0, 0, 0}, {0, 0.35, 0}, 0.015, 5, "green");
    add::sphere({0, 0.42, 0}, 0.07, 3, "red");
    add::Mesh tulip = add::stretch(add::pop(), {1, 1.3, 1}, add::Point{0, 0, 0});
    for (int row = 0; row < 5; ++row) {                                                    // rows in a field
        double x0 = 9.5 + row * 0.7;
        add::Points line;
        for (int k = 0; k < 25; ++k) {
            double z = -6 + 0.5 * k;
            line.push_back({x0, hill(x0, z), z});
        }
        add::Mesh field = add::along(tulip, line, (int)line.size(), 0.0, 1.0, std::nullopt);
        add::mesh(add::color_by(field, [&](const add::Point& p) {
            return p[1] > hill(p[0], p[2]) + 0.38
                       ? add::hsv(p[1] < hill(p[0], p[2]) + 0.4 ? 0.0 : 0.02 + 0.045 * row, 0.9, 1.0)
                       : add::Color("green");
        }));
    }

    add::text("MALŪNAS", {-2.6, TOP + 0.35, 2.75}, 0.5, std::nullopt, CLOTH,
              {1, 0, 0}, {0, 1, 0}, "left", 1.0, 6);

    add::mesh(add::limit_colors(add::layer(), 50));   // at most 50 colours, so the .obj suits Sketchfab
    add::check();
    add::save("windmill.off");
}

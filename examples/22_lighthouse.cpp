// 22 -- a lighthouse on a rocky island.
//
// A complete scene the way a course project is built: a landscape from a
// height function, a striped tower from a lathe with a *colour function*, a
// keeper's house from ready-made parts (``bricks``, ``roof``, ``arch``,
// ``stairs``), palms and rocks scattered with ``random_points`` /
// ``scatter``, a fence strung ``along`` a path, a rowing boat lofted from
// cross-sections and a date written with ``text``.
//
// Parameters: ``BANDS`` (stripes on the tower) and ``SEED`` (the island).
#include "add.hpp"

const int BANDS = 7;
const int SEED = 7;

const add::Color SEA = {40, 110, 170};
const add::Color SAND = {214, 190, 140};
const add::Color GRASS = {86, 150, 70};
const add::Color ROCK = {120, 112, 105};
const add::Color WALL = {235, 230, 220};
const add::Color RED = {200, 40, 40};

// Height of the island at (x, z): a bump with a rocky, noisy rim.
double island(double x, double z) {
    double d = add::sqrt(x * x + z * z);
    double ridge = 0.25 * add::sin(3.0 * add::atan2(z, x)) * add::exp(-add::detail::py_pow((d - 9) / 3.0, 2));
    return 4.0 * add::exp(-add::detail::py_pow(d / 8.5, 2)) + ridge - 0.8;
}

add::Color ground_color(double x, double z) {
    double h = island(x, z);
    if (h < 0.05)
        return SAND;
    double t = add::clamp(add::remap(h, 0.05, 2.0, 0.0, 1.0));
    return h < 1.6 ? add::lerp(SAND, GRASS, t) : add::lerp(GRASS, ROCK, t);
}

const double TOP = island(0, 0);
const double H = 9.0;

add::Point2 tower_profile(double t) {
    return {1.6 - 0.9 * t, t * H};          // radius narrows as it rises
}

add::Color bands(double t, double /*a*/) {
    return int(t * BANDS) % 2 == 0 ? RED : WALL;
}

add::Mesh house() {
    add::push();
    add::cuboid({0, 1.1, 0}, {4.0, 2.2, 3.0}, WALL);
    add::bricks({-2.0, 0, 1.5}, 4.0, 0.9, {0.6, 0.3, 0.12}, "brown", {1, 0, 0}, 0.05, SEED);
    add::roof({0, 2.2, 0}, {4.0, 3.0}, 1.4, RED, 0.3);
    add::cuboid({1.2, 3.1, 0}, {0.5, 1.4, 0.5}, add::shade(RED, 0.6));       // chimney
    add::arch({-0.45, 0, 1.55}, {0.45, 0, 1.55}, 1.0, {0.16, 0.15}, "brown");
    add::cuboid({0, 0.75, 1.55}, {0.9, 1.5, 0.1}, {90, 60, 30});
    for (double x : {-1.3, 1.3})                                              // windows
        add::cuboid({x, 1.3, 1.55}, {0.7, 0.7, 0.1}, {150, 220, 255});
    return add::pop();
}

add::Mesh boat() {
    add::push();
    std::vector<add::Points> sections;
    for (int i = 0; i < 9; ++i) {
        double t = i / 8.0;
        double w = 0.55 * add::detail::py_pow(add::sin(add::pi * t), 0.5) + 0.02;   // beam of the boat
        double y = 0.25 - 0.4 * add::sin(add::pi * t);               // keel depth
        double x = -1.4 + 2.8 * t;
        add::Points ring = {{x, 0.4, -w}, {x, y + 0.15, -w * 0.7}, {x, y, 0}, {x, y + 0.15, w}, {x, 0.4, w}};
        sections.push_back(ring);
    }
    add::loft(sections, {150, 90, 50});
    add::Mesh hull = add::solidify(add::layer(), 0.06);
    add::mesh(hull);
    for (double x : {-0.6, 0.3})                                   // thwarts (seats)
        add::cuboid({x, 0.32, 0}, {0.18, 0.05, 0.9}, {200, 160, 100});
    return add::pop();
}

int main() {
    add::Random rng(SEED);

    // --------------------------------------------------------------------------
    //  the island: a height field, coloured by height
    // --------------------------------------------------------------------------
    add::grid({0, 0, 0}, {40, 40}, 90, 90, ground_color, island, 0.3);

    // the sea: a flat sheet, rippled with ``deform`` and shaded darker far away.
    // push()/pop() keep the island out of the sheet (a bare layer() would take
    // everything drawn so far).
    add::push();
    add::grid({0, 0, 0}, {46, 46}, 46, 46, SEA);
    add::Mesh sea = add::deform(add::pop(), [](const add::Point& p) {
        return add::Point{p[0], 0.08 * add::sin(1.3 * p[0] + p[2]) + 0.05 * add::cos(2.1 * p[2]), p[2]};
    });
    add::mesh(add::color_gradient(sea, add::shade(SEA, 0.55), SEA, 2));

    // --------------------------------------------------------------------------
    //  the lighthouse: a lathe with red and white bands, gallery, lantern, dome
    // --------------------------------------------------------------------------
    add::revolve(tower_profile, {0, TOP - 0.2, 0}, {0, TOP + 1, 0}, 0, 1, 80, 48, bands);

    // the gallery: a disc, a railing of posts and two rails running around it.
    // The post is built between push() and pop() so that layer()-style capture
    // cannot swallow the island drawn above.
    add::cylinder({0, TOP + H, 0}, {0, TOP + H + 0.25, 0}, 1.25, 48, add::shade(WALL, 0.8));
    add::push();
    add::cylinder({1.15, TOP + H + 0.25, 0}, {1.15, TOP + H + 1.0, 0}, 0.04, 8, "black");
    add::Mesh post = add::pop();
    add::mesh(add::array_radial(post, 16));
    add::torus({0, TOP + H + 1.0, 0}, 1.15, 0.035, 48, 8, "black");
    add::torus({0, TOP + H + 0.6, 0}, 1.15, 0.025, 48, 8, "black");

    // the lantern room and its dome
    add::tube({0, TOP + H + 0.25, 0}, {0, TOP + H + 1.6, 0}, 0.75, 24, {150, 220, 255});
    add::cylinder({0, TOP + H + 0.5, 0}, {0, TOP + H + 1.3, 0}, 0.3, 16, "gold");   // the lamp
    add::cylinder({0, TOP + H + 1.6, 0}, {0, TOP + H + 1.75, 0}, 0.9, 24, RED);
    add::hemisphere({0, TOP + H + 1.75, 0}, 0.9, 12, RED);
    add::sphere({0, TOP + H + 2.75, 0}, 0.12, 4, "gold");

    // a door at the foot and a short flight of steps up to it
    add::arch({-0.6, TOP, 1.5}, {0.6, TOP, 1.5}, 0.7, {0.25, 0.2}, "brown");
    add::cuboid({0, TOP + 0.6, 1.5}, {1.2, 1.2, 0.2}, "brown");
    add::stairs({0, TOP - 0.5, 3.4}, 3, 1.4, 0.16, 0.5, ROCK, {0, 0, -1});

    // --------------------------------------------------------------------------
    //  the keeper's house: walls of bricks, a roof, a chimney, an arched door
    // --------------------------------------------------------------------------
    add::Point site = {5.0, island(5.0, 3.0), 3.0};
    add::mesh(add::align(add::rotateY(house(), 0.5), site));

    // a fence of posts along a curved path from the house to the lighthouse
    add::push();
    add::cylinder({0, 0, 0}, {0, 0.6, 0}, 0.05, 6, "brown");
    add::sphere({0, 0.62, 0}, 0.07, 3, "brown");
    add::Mesh fence_post = add::pop();
    add::Points path = add::chaikin({{4.5, 0, 6}, {2, 0, 7}, {-1, 0, 5}, {-2.5, 0, 2}}, 2);
    for (add::Point& p : path) p = {p[0], island(p[0], p[2]), p[2]};
    add::mesh(add::along(fence_post, path, (int)path.size(), 0.0, 1.0, std::nullopt));
    add::Points rail;
    for (const add::Point& p : path) rail.push_back({p[0], p[1] + 0.55, p[2]});
    add::polyline(rail, 0.02, 6, "brown");

    // --------------------------------------------------------------------------
    //  nature: palms and rocks scattered over the island
    // --------------------------------------------------------------------------
    add::Points spots;
    for (const add::Point& p : add::random_points(60, {-12, 0, -12}, {12, 0, 12}, SEED, island))
        if (0.05 < p[1] && p[1] < 1.4 && add::distance(p, {0, p[1], 0}) > 3.5
            && add::distance(p, site) > 3.0)
            spots.push_back(p);
    for (int i = 0; i < 8 && i < (int)spots.size(); ++i)          // the first 8 spots
        add::tree(spots[i], rng.uniform(2.0, 3.2), "brown", "green", "palm", 10, i);

    add::push();
    add::sphere({0, 0, 0}, 0.5, 5, ROCK);
    add::Mesh rock = add::jitter(add::stretch(add::pop(), {1.3, 0.7, 1.0}), 0.08, SEED);
    add::Points rocks;
    for (const add::Point& p : add::random_points(70, {-13, 0, -13}, {13, 0, 13}, SEED + 1, island))
        if (-0.6 < p[1] && p[1] < 0.3 && add::distance(p, site) > 3.0)
            rocks.push_back(p);
    add::mesh(add::scatter(rock, rocks, SEED, true, {0.5, 1.6}));

    // --------------------------------------------------------------------------
    //  a rowing boat: cross-sections lofted into a hull, and a rope to a post
    // --------------------------------------------------------------------------
    add::Mesh B = add::rotateY(add::zoom(boat(), 1.4, add::Point{0, 0, 0}), 0.9);
    B = add::move(B, {-6.5, -0.05, 9.5});
    add::mesh(B);
    add::polyline({{-6.0, 0.35, 8.6}, {-5.0, 0.6, 8.0}, {-4.3, island(-4.3, 7.4) + 0.5, 7.4}},
                  0.03, 6, {230, 220, 190});
    add::cylinder({-4.3, island(-4.3, 7.4), 7.4}, {-4.3, island(-4.3, 7.4) + 0.6, 7.4},
                  0.06, 6, "brown");

    // a plaque with the year, standing on the grass
    add::cuboid({2.6, island(2.6, 2) + 0.4, 2.0}, {1.7, 0.8, 0.12}, ROCK);
    add::text("1863", {1.9, island(2.6, 2) + 0.2, 2.07}, 0.4, std::nullopt, "gold",
              {1, 0, 0}, {0, 1, 0}, "left", 1.0, 6);

    add::mesh(add::limit_colors(add::layer(), 50));   // at most 50 colours, so the .obj suits Sketchfab
    add::check();
    add::save("lighthouse.off");
}

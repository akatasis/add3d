// 29 -- two bridges over a river.
//
// A suspension bridge and an old stone bridge side by side.  The towers and
// deck are ``beam`` bars; the main cables are ``polyline`` tubes through
// points computed from a parabola with ``lerp``; every hanger is a beam
// from a deck point (``points_on_line``) up to the cable.  The railing is a
// rectangle ``sweep``-ed along the deck, the lamp posts are one post
// ``along`` the deck, the cars are ``rounded_box``-es with ``wheel``s strung
// along the road.  The stone bridge is three ``arch``-es with ``bricks``
// parapets, and the tower tops are sliced at a slant with ``cut``.
//
// Parameters: ``SPAN`` (length of the main span), ``CARS``.
#include "add.hpp"

const double SPAN = 24.0;
const int CARS = 7;

const add::Color STEEL = {200, 60, 50};
const add::Color DECK = {90, 90, 95};
const add::Color STONE = {150, 140, 125};
const add::Color WATER = {50, 110, 160};
const add::Color BANK = {95, 140, 70};

double valley(double x, double z) {
    double bank = 1.8 * (1 - add::exp(-add::detail::py_pow(z / 7.0, 4)));            // flat bed, steep banks
    return bank - 2.0 + 0.15 * add::sin(0.7 * x) * add::cos(0.9 * z);
}

const double HALF = SPAN / 2.0;
const double DECK_Y = 1.4;
const double TOWER_H = 9.0;

// A point on the main cable: a parabola between the tower tops.
add::Point cable(double t, double side) {
    double x = -HALF + SPAN * t;
    double y = add::lerp(TOWER_H, DECK_Y + 0.8, 1 - add::detail::py_pow(2 * t - 1, 2));
    return {x, y, side};
}

add::Mesh car(const add::Color& color) {
    add::push();
    add::rounded_box({0, 0.35, 0}, {1.8, 0.5, 0.9}, 0.12, 4, color);
    add::rounded_box({-0.1, 0.75, 0}, {1.0, 0.45, 0.8}, 0.15, 4, {170, 210, 240});
    for (double wx : {-0.6, 0.6})
        for (double wz : {-0.42, 0.42})
            add::wheel({wx, 0.2, wz}, 0.2, 0.16, "black", {0, 0, 1}, 12);
    return add::pop();
}

int main() {
    add::Random rng(SPAN + CARS);             // (31.0: as in Python, the same as the seed 31)

    // --------------------------------------------------------------------------
    //  the river valley: a height field with a channel, and rippled water
    // --------------------------------------------------------------------------
    add::grid({0, 0, 0}, {SPAN + 24, 28}, 96, 56,
              [](double x, double z) { return valley(x, z) > -0.9 ? BANK : add::Color{120, 105, 80}; },
              valley, 0.4);
    add::push();
    add::grid({0, -1.0, 0}, {SPAN + 24, 13}, 48, 26, WATER);
    add::Mesh water = add::deform(add::pop(), [](const add::Point& p) {
        return add::Point{p[0], p[1] + 0.06 * add::sin(2 * p[0] + p[2]), p[2]};
    });
    add::mesh(add::color_gradient(water, add::shade(WATER, 0.7), WATER, 0));

    // --------------------------------------------------------------------------
    //  the suspension bridge
    // --------------------------------------------------------------------------
    for (double x : {-HALF, HALF}) {                          // towers: two legs, two cross beams
        add::push();
        for (double z : {-1.6, 1.6})
            add::beam({x, -2.2, z}, {x, TOWER_H, z}, 0.8, 0.8, STEEL);
        add::beam({x, DECK_Y + 2.0, -2.0}, {x, DECK_Y + 2.0, 2.0}, 0.7, 0.5, STEEL);
        add::beam({x, TOWER_H - 1.2, -2.0}, {x, TOWER_H - 1.2, 2.0}, 0.7, 0.5, STEEL);
        add::Mesh tower = add::pop();
        add::mesh(add::cut(tower, {x, TOWER_H - 0.4, 0}, {0.35, 1, 0}));     // a slanted top
    }

    add::beam({-HALF - 12, DECK_Y, 0}, {HALF + 12, DECK_Y, 0}, 4.0, 0.5, DECK);   // the deck
    for (int x = -int(HALF) - 12; x < int(HALF) + 12; x += 2)      // the centre line
        add::cuboid({x + 0.5, DECK_Y + 0.26, 0}, {1.0, 0.02, 0.15}, "white");

    for (double side : {-2.1, 2.1}) {
        add::Points pts;
        for (int i = 0; i < 61; ++i) pts.push_back(cable(i / 60.0, side));
        add::polyline(pts, 0.12, 10, STEEL);
        add::polyline({{-HALF - 12, DECK_Y - 1.5, side}, {-HALF, TOWER_H, side}}, 0.1, 8, STEEL);
        add::polyline({{HALF, TOWER_H, side}, {HALF + 12, DECK_Y - 1.5, side}}, 0.1, 8, STEEL);
        for (const add::Point& p : add::points_on_line({-HALF + 1, DECK_Y + 0.25, side},
                                                       {HALF - 1, DECK_Y + 0.25, side}, 23)) {
            double t = (p[0] + HALF) / SPAN;
            add::beam(p, cable(t, side), 0.06, 0.06, STEEL);
        }
    }

    // railings: a small rectangle swept along both edges of the deck
    for (double side : {-1.95, 1.95}) {
        add::sweep(add::profile_rect(0.08, 0.08),
                   [&](double t) { return add::Point{-HALF - 12 + (SPAN + 24) * t, DECK_Y + 1.0, side}; },
                   0, 1, 40, DECK);
        add::push();
        add::cylinder({0, 0, 0}, {0, 0.95, 0}, 0.03, 6, DECK);
        add::Mesh rail_post = add::pop();
        add::mesh(add::along(rail_post,
                             [&](double t) {
                                 return add::Point{-HALF - 12 + (SPAN + 24) * t, DECK_Y + 0.25, side};
                             },
                             40, 0, 1, std::nullopt));
    }

    // lamp posts, every few metres, on one side
    add::push();
    add::cylinder({0, 0, 0}, {0, 2.2, 0}, 0.06, 8, "black");
    add::cylinder({0, 2.2, 0}, {0.5, 2.4, 0}, 0.05, 8, "black");
    add::sphere({0.55, 2.35, 0}, 0.18, 4, {255, 240, 170});
    add::Mesh lamp = add::pop();
    add::mesh(add::along(lamp,
                         [](double t) {
                             return add::Point{-HALF - 10 + (SPAN + 20) * t, DECK_Y + 0.25, 1.6};
                         },
                         10, 0, 1, std::nullopt));

    // cars: a body, a cabin and four wheels; each lane gets its own colours
    for (auto [lane, direction] : {std::pair{-0.9, 1.0}, std::pair{0.9, -1.0}}) {
        int n = CARS / 2 + (lane < 0);
        for (const add::Point& p : add::points_on_line({-HALF - 10, DECK_Y + 0.25, lane},
                                                       {HALF + 10, DECK_Y + 0.25, lane}, n)) {
            add::Mesh one = car(add::hsv(rng.random(), 0.85, 0.9));
            one = add::aim(one, {direction, 0, 0}, {1, 0, 0});       // face the way it drives
            add::mesh(add::move(one, {p[0] + rng.uniform(-2, 2), p[1], p[2]}));
        }
    }

    // --------------------------------------------------------------------------
    //  the old stone bridge, a little way upstream
    // --------------------------------------------------------------------------
    const double ZB = -9.5;
    std::vector<double> piers = {-8.0, 0.0, 8.0};
    for (int i = 0; i < (int)piers.size() - 1; ++i) {
        double a = piers[i], b = piers[i + 1];
        add::arch({a + 1.0, -1.6, ZB}, {b - 1.0, -1.6, ZB}, 3.0, {3.0, 0.7}, STONE, 24);
    }
    for (double x : piers)
        add::cuboid({x, -0.6, ZB}, {2.0, 3.2, 3.4}, STONE);
    add::cuboid({0, 1.35, ZB}, {20, 0.5, 3.0}, add::shade(STONE, 0.85));               // the roadway
    for (double side : {-1.35, 1.35})
        add::bricks({-10, 1.6, ZB + side}, 20, 0.8, {0.8, 0.27, 0.3}, STONE, {1, 0, 0}, 0.05, 1);
    add::text("1785", {-1.0, 1.75, ZB + 1.55}, 0.4, std::nullopt, add::shade(STONE, 0.5),
              {1, 0, 0}, {0, 1, 0}, "left", 1.0, 6);

    // a rowing boat passing under it: a lofted hull, as in example 22
    add::push();
    std::vector<add::Points> sections;
    for (int i = 0; i < 7; ++i) {
        double t = i / 6.0;
        double w = 0.45 * add::detail::py_pow(add::sin(add::pi * t), 0.5) + 0.02,
               y = 0.2 - 0.35 * add::sin(add::pi * t), x = -1.2 + 2.4 * t;
        sections.push_back({{x, 0.35, -w}, {x, y, 0}, {x, 0.35, w}});
    }
    add::loft(sections, {160, 100, 60});
    add::Mesh boat = add::solidify(add::pop(), 0.05);
    add::mesh(add::move(add::rotateY(boat, 0.4), {3.0, -1.0, ZB + 4.0}));

    add::Mesh bridge = add::limit_colors(add::layer(), 50);   // at most 50 colours, so the .obj suits Sketchfab
    std::printf("faces lying on other faces: %d -- the cause of flicker; save() cuts them\n",
                add::overlaps(bridge));
    std::printf("faces that are not convex: %d -- a viewer would fan them; save() cuts them\n",
                add::concave_faces(bridge));
    add::mesh(bridge);
    add::check();
    add::save("bridge.off");
}

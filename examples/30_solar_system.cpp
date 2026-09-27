// 30 -- a solar system with banded planets.
//
// A planet is a lathe: ``revolve`` spins a half circle, and a *colour
// function* of (t, angle) paints it -- latitude bands for Jupiter, a
// pseudo-random map of continents for Earth, a great red spot, ice caps.
// Orbits are closed ``curve`` loops, moons are one small sphere strung
// ``along`` a circle, the asteroid belt is a jittered rock ``scatter``-ed on
// random points of an annulus, the comet a ``polyline`` whose radius and
// colour both fade along its tail.  Names are written with ``text``.
//
// Parameters: ``DAY`` (turns the planets on their orbits), ``SEED``.
#include "add.hpp"

const double DAY = 40.0;
const int SEED = 9;


// A ball of radius ``r`` painted by ``paint(latitude, longitude)``.
//
// Latitude runs -1 (south pole) .. 1 (north pole), longitude 0 .. 2pi.
void planet(const add::Point& center, double r, const std::function<add::Color(double, double)>& paint,
            int k = 24, double tilt = 0.0) {
    add::push();
    add::revolve([&](double t) { return add::Point2{r * add::sin(t), r * add::cos(t)}; }, {0, -r, 0}, {0, r, 0},
                 0, add::pi, k, 2 * k,
                 [&](double t, double a) { return paint(add::cos(t), a); });
    add::Mesh body = add::rotateZ(add::pop(), tilt);
    add::mesh(add::move(body, center));
}


// A cheap, repeatable 'noise': a few sine waves added up.
double noise(double lat, double lon, int seed) {
    double v = 0.0;
    for (int i = 1; i < 5; ++i)
        v += add::sin(i * 2.3 * lon + seed * i) * add::cos(i * 1.7 * lat * 3 + seed) / i;
    return v;
}


// A closed thin ring, and the point on it where the planet sits today.
add::Point orbit(double radius, double phase, double tilt = 0.0) {
    add::curve([&](double t) {
        return add::Point{radius * add::cos(t), radius * 0.0 + tilt * add::sin(t), radius * add::sin(t)};
    }, 0, 2 * add::pi, 160, 6, 0.03, {70, 70, 90}, true);
    double a = phase + DAY / add::detail::py_pow(radius, 1.5) * 4.0;
    return {radius * add::cos(a), tilt * add::sin(a), radius * add::sin(a)};
}


add::Color earth(double lat, double lon) {
    if (std::abs(lat) > 0.88)
        return "white";                                   // ice caps
    double land = noise(lat, lon, 4) + 0.3 * noise(lat, 2 * lon, 5);
    if (land > 0.55)
        return std::abs(lat) < 0.7 ? add::Color(90, 140, 60) : add::Color(150, 160, 140);
    if (land > 0.45)
        return {200, 190, 130};                           // beaches
    return land > 0.0 ? add::Color(40, 90, 190) : add::Color(25, 60, 150);
}


add::Color jupiter(double lat, double lon) {
    int band = (int)((lat + 1) * 6.5);
    add::Color base = std::vector<add::Color>{{220, 190, 150}, {190, 140, 100},
                                              {230, 210, 180}, {170, 120, 90}}[band % 4];
    double d = add::detail::py_pow(lon - 4.0, 2) * 3 + add::detail::py_pow((lat + 0.35) * 8, 2);
    if (d < 1.2)
        return {200, 70, 50};                             // the great red spot
    return add::shade(base, 0.9 + 0.15 * add::sin(9 * lon + 20 * lat));
}


int main() {
    add::Random rng(SEED);

    // --------------------------------------------------------------------------
    //  the sun and the planets
    // --------------------------------------------------------------------------
    planet({0, 0, 0}, 3.0, [](double lat, double lon) {
        return add::gradient(0.5 + 0.5 * noise(lat, lon, 1), "yellow", "orange");
    }, 28);
    for (const add::Point& q : add::points_on_circle({0, 0, 0}, 3.0, 24)) {         // solar flares
        add::Point tip = add::lerp({0, 0, 0}, q, rng.uniform(1.15, 1.45));
        add::cone(q, tip, rng.uniform(0.15, 0.3), 8, "orange");
    }

    add::Point p = orbit(5.0, 0.3);
    planet(p, 0.35, [](double lat, double lon) {
        return add::gradient(0.5 + 0.4 * noise(lat, lon, 2), {140, 130, 120}, {90, 80, 70});
    }, 12);
    add::text("MERCURY", {p[0] - 0.8, p[1] + 0.6, p[2]}, 0.35,
              std::nullopt, "white", {1, 0, 0}, {0, 1, 0}, "left", 1.0, 5);

    p = orbit(7.0, 2.0);
    planet(p, 0.55, [](double lat, double lon) {
        return add::gradient(0.5 + 0.5 * noise(lat, lon, 3), {230, 200, 150}, {200, 150, 90});
    }, 14);
    add::text("VENUS", {p[0] - 0.6, p[1] + 0.8, p[2]}, 0.35,
              std::nullopt, "white", {1, 0, 0}, {0, 1, 0}, "left", 1.0, 5);

    p = orbit(9.5, 4.1);
    planet(p, 0.6, earth, 18, 0.4);
    add::text("EARTH", {p[0] - 0.6, p[1] + 0.85, p[2]}, 0.35,
              std::nullopt, "white", {1, 0, 0}, {0, 1, 0}, "left", 1.0, 5);
    add::push();
    add::sphere({0, 0, 0}, 0.14, 4, {200, 200, 205});
    add::Mesh moon = add::pop();
    add::mesh(add::along(moon, [&](double t) {
        return add::Point{p[0] + 1.1 * add::cos(t), p[1] + 0.2 * add::sin(t), p[2] + 1.1 * add::sin(t)};
    }, 1, DAY / 3.0, DAY / 3.0 + 1, std::nullopt));

    p = orbit(12.0, 5.5);
    planet(p, 0.45, [](double lat, double lon) {
        return std::abs(lat) < 0.9 ? add::gradient(0.5 + 0.5 * noise(lat, lon, 6), {200, 90, 50}, {140, 60, 40})
                                   : add::Color("white");
    }, 14);
    add::text("MARS", {p[0] - 0.5, p[1] + 0.7, p[2]}, 0.35,
              std::nullopt, "white", {1, 0, 0}, {0, 1, 0}, "left", 1.0, 5);

    // the asteroid belt: one jittered rock, scattered on random points of a ring
    add::push();
    add::sphere({0, 0, 0}, 0.12, 3, {120, 110, 100});
    add::Mesh rock = add::jitter(add::pop(), 0.04, SEED);
    add::Points belt;
    for (int i = 0; i < 260; ++i) {
        double a = rng.uniform(0, 2 * add::pi);
        double rr = rng.uniform(14.0, 16.5);
        belt.push_back({rr * add::cos(a), rng.uniform(-0.3, 0.3), rr * add::sin(a)});
    }
    add::mesh(add::scatter(rock, belt, SEED, true, {0.4, 1.8}));

    p = orbit(20.0, 1.2);
    planet(p, 1.7, jupiter, 26);
    add::text("JUPITER", {p[0] - 1.0, p[1] + 2.0, p[2]}, 0.4,
              std::nullopt, "white", {1, 0, 0}, {0, 1, 0}, "left", 1.0, 5);
    add::push();
    add::sphere({0, 0, 0}, 0.1, 3, {220, 200, 160});
    add::mesh(add::along(add::pop(), [&](double t) {
        return add::Point{p[0] + 2.4 * add::cos(t), p[1] + 0.3 * add::sin(2 * t), p[2] + 2.4 * add::sin(t)};
    }, 4, DAY / 5.0, DAY / 5.0 + 2 * add::pi, std::nullopt, true));

    p = orbit(26.0, 3.3);
    planet(p, 1.4, [](double lat, double /*lon*/) {
        return add::gradient(0.5 + 0.5 * add::sin(9 * lat), {230, 215, 170}, {200, 175, 120});
    }, 24, 0.45);
    add::push();
    add::ring({0, 0, 0}, {0, 1, 0}, 3.0, 1.9, 64, {210, 195, 160});
    add::ring({0, 0, 0}, {0, 1, 0}, 1.85, 1.7, 64, {160, 140, 110});
    add::Mesh rings = add::two_sided(add::rotateZ(add::pop(), 0.45));
    add::mesh(add::move(rings, p));
    add::text("SATURN", {p[0] - 0.9, p[1] + 2.2, p[2]}, 0.4,
              std::nullopt, "white", {1, 0, 0}, {0, 1, 0}, "left", 1.0, 5);

    // a comet with a tail that thins and fades away from the sun
    add::Point head = {-9.0, 2.5, -13.0};
    add::Point away = add::direction({0, 0, 0}, head);
    add::Points tail;
    for (int i = 0; i < 13; ++i) {
        double t = i / 12.0;
        tail.push_back(add::lerp(head, {head[0] + away[0] * 9, head[1] + away[1] * 9, head[2] + away[2] * 9}, t));
    }
    add::polyline(tail, [](double t) { return 0.3 * (1 - t) + 0.02; }, 8,
                  [](double t, double /*a*/) { return add::gradient(t, "white", {40, 40, 60}); });
    add::sphere(head, 0.35, 5, "white");

    // a ground plane of stars: tiny bright spheres far below
    for (const add::Point& q : add::random_points(200, {-32, -6, -32}, {32, -6, 32}, SEED + 1))
        add::sphere(q, rng.uniform(0.05, 0.12), 2, "white");

    add::mesh(add::limit_colors(add::layer(), 50));   // at most 50 colours, so the .obj suits Sketchfab
    add::check();
    add::save("solar_system.off");
}

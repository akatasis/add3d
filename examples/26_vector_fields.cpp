// 26 -- vector fields, flows and strange attractors.
//
// Mathematics makes good models.  ``flow`` integrates a vector field with
// Runge-Kutta and ``trace`` draws the path as a tube: the Lorenz butterfly,
// coloured along its length by a colour function, and the Rössler band,
// drawn with ``polyline`` so that the tube can thin out towards the end.
// A small field of arrows shows the direction of flow: one arrow, ``aim``-ed
// along the field at every grid point and coloured by speed.  Beads on a
// helix and cubes on a spiral show ``points_on_helix`` / ``points_on_spiral``.
//
// Parameters: ``STEPS`` (length of the curves), ``RHO`` (the Lorenz parameter).
#include "add.hpp"

const int STEPS = 6000;
const double RHO = 28.0;

add::Point lorenz(const add::Point& p) {
    auto [x, y, z] = p;
    return {10.0 * (y - x), x * (RHO - z) - y, x * y - 8.0 / 3.0 * z};
}

add::Point rossler(const add::Point& p) {
    auto [x, y, z] = p;
    return {-y - z, x + 0.2 * y, 0.2 + z * (x - 5.7)};
}

add::Point swirl(const add::Point& p) {
    return {-p[2] + 0.3 * p[0], 0.4 * add::sin(p[0]), p[0] + 0.3 * p[2]};
}

int main() {
    add::axes({0, 0, 0}, 3.0);

    // --------------------------------------------------------------------------
    //  the Lorenz attractor
    // --------------------------------------------------------------------------
    add::push();
    add::trace(lorenz, {1.0, 1.0, 1.0}, 0.006, STEPS, 0.35, 10,
               [](double t, double /*a*/) { return add::hsv(0.7 * t, 0.9, 1.0); }, 2);
    // the attractor lives around z = 25: bring it down, shrink it, stand it up
    add::Mesh L = add::pop();
    L = add::rotateX(add::zoom(L, 0.22, add::Point{0, 0, 0}), -add::pi / 2, {0, 0, 0});
    add::mesh(add::move(L, {-12, 2, 0}));
    add::text("LORENZ", {-15.5, 0, 6}, 1.0, std::nullopt, "navy", {1, 0, 0}, {0, 0, -1}, "left", 1.0, 6);

    // --------------------------------------------------------------------------
    //  the Rössler attractor: flow() gives the points, polyline() draws them
    // --------------------------------------------------------------------------
    add::Points all = add::flow(rossler, {1.0, 1.0, 0.0}, 0.02, STEPS);
    add::Points pts;
    for (size_t i = 0; i < all.size(); i += 3) pts.push_back(all[i]);          // [::3]: every third point
    for (add::Point& p : pts) p = {0.3 * p[0] + 8, 0.3 * p[2] + 1, 0.3 * p[1] + 8};
    add::polyline(pts, [](double t) { return 0.06 + 0.16 * (1 - t); }, 8,
                  [](double t, double /*a*/) { return add::gradient(t, "orange", "purple"); });
    add::text("RÖSSLER", {5, 0, 13.5}, 1.0, std::nullopt, "navy", {1, 0, 0}, {0, 0, -1}, "left", 1.0, 6);

    // --------------------------------------------------------------------------
    //  an arrow field: the same arrow aimed along the field at every point
    // --------------------------------------------------------------------------
    add::push();
    add::arrow({0, 0, 0}, {0, 1, 0}, 0.08, "grey", 8);           // points up, 1 long
    add::Mesh one = add::pop();
    for (int x = -4; x < 5; ++x) {
        for (int z = -4; z < 5; ++z) {
            add::Point p = {x * 1.1 + 10, 0.6, z * 1.1 - 8};
            add::Point v = swirl({p[0] - 10, p[1], p[2] + 8});
            double speed = add::clamp(add::remap(add::distance(v, {0, 0, 0}), 0, 6, 0, 1));
            add::Mesh A = add::zoom(one, 0.4 + 0.6 * speed, add::Point{0, 0, 0});
            A = add::aim(A, v);
            add::mesh(add::color(add::move(A, p), add::hsv(0.66 - 0.66 * speed)));
        }
    }
    add::text("FIELD", {8, 0, -1.5}, 1.0, std::nullopt, "navy", {1, 0, 0}, {0, 0, -1}, "left", 1.0, 6);

    // --------------------------------------------------------------------------
    //  beads on a helix, cubes on a spiral
    // --------------------------------------------------------------------------
    add::push();
    add::sphere({0, 0, 0}, 0.3, 5, "gold");
    add::Mesh bead = add::pop();
    add::Points beads = add::points_on_helix({-10, 0.3, -8}, 2.0, 1.6, 4, 90);
    add::mesh(add::scatter(bead, beads, 1, false, {0.7, 1.3}));
    add::curve([](double t) { return add::Point{-10 + 2 * add::cos(2 * add::pi * t), 0.3 + 1.6 * t,
                                                -8 + 2 * add::sin(2 * add::pi * t)}; },
               0, 4, 240, 8, 0.05, "black");

    add::push();
    add::box({0, 0, 0}, 0.5, "teal");
    add::Mesh cube = add::pop();
    add::Points spiral = add::points_on_spiral({0, 0.25, -8}, 0.3, 4.5, 3, 60, {0, 1, 0}, 3.0);
    add::mesh(add::along(cube, spiral, (int)spiral.size(), 0.0, 1.0, add::Point{1, 0, 0}, false,
                         [](double t) { return 0.5 + t; }));

    add::mesh(add::limit_colors(add::layer(), 50));   // at most 50 colours, so the .obj suits Sketchfab
    add::check();
    add::save("vector_fields.off");
}

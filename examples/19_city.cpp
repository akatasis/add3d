// 19 -- a procedural city.
//
// One parameter, ``SEED``, decides the whole town; another, ``BLOCKS``, decides
// how big it is.  That is what the assignment means by "the shape must depend
// on a parameter": change one number, get a different model.
#include "add.hpp"

const int SEED = 2026;
const int BLOCKS = 7;                      // the city is BLOCKS x BLOCKS street blocks
add::Random rng(SEED);

const add::Color WINDOW = {255, 235, 150};
const add::Color ROAD = {60, 60, 66};
const add::Color PARK = {70, 130, 70};


// One building, built on a scene of its own and returned as a mesh.
//
// ``add::push()`` puts the streets aside so that the ``layer()`` calls below
// cannot swallow them; ``add::pop()`` gives the building back and restores
// the city.
add::Mesh tower(double width, double depth, double height, int style) {
    add::push();
    double hue = rng.uniform(0.5, 0.65);               // (drawn one by one, in Python's order)
    double saturation = rng.uniform(0.05, 0.3);
    double value = rng.uniform(0.55, 0.95);
    add::Color body = add::hsv(hue, saturation, value);
    if (style == 0) {                                  // a plain slab
        add::cuboid({0, height / 2, 0}, {width, height, depth}, body);
    } else if (style == 1) {                           // stepped setbacks
        int steps = (int)rng.randint(2, 4);
        double y = 0.0;
        for (int s = 0; s < steps; ++s) {
            double h = height / steps;
            double k = 1.0 - 0.18 * s;
            add::cuboid({0, y + h / 2, 0}, {width * k, h, depth * k}, body);
            y += h;
        }
    } else if (style == 2) {                           // a round tower
        add::cylinder({0, 0, 0}, {0, height, 0}, width / 2, 24, body);
        add::cone({0, height, 0}, {0, height + width, 0}, width / 2, 24,
                  {180, 60, 60});
    } else {                                           // a tapering tower
        add::extrude({{-width / 2, -depth / 2}, {width / 2, -depth / 2},
                      {width / 2, depth / 2}, {-width / 2, depth / 2}},
                     {0, height, 0}, body, 8, 0.0,     // steps = 8, no twist
                     [](double t) { return 1 - 0.45 * t; }, {0, 0, 0});   // scale, center
    }
    add::Mesh shell = add::layer();

    // windows: small bright plates pressed into the walls
    if (style != 2) {
        int rows = std::max(1, int(height / 0.55));
        for (int r = 0; r < rows; ++r) {
            double y = 0.35 + r * 0.55;
            if (y > height - 0.3)
                break;
            for (const auto& [sx, sz, w, d] : std::vector<std::array<double, 4>>{
                     {width / 2, 0, 0.06, depth * 0.8},
                     {-width / 2, 0, 0.06, depth * 0.8},
                     {0, depth / 2, width * 0.8, 0.06},
                     {0, -depth / 2, width * 0.8, 0.06}}) {
                if (rng.random() < 0.55)
                    add::cuboid({sx, y, sz}, {w, 0.3, d}, WINDOW);
            }
        }
        shell = add::merge({shell, add::layer()});
    }

    if ((style == 0 || style == 1) && rng.random() < 0.4) {   // a roof mast
        add::cylinder({0, height, 0}, {0, height + rng.uniform(0.5, 1.6), 0},
                      0.05, 6, {200, 60, 60});
        shell = add::merge({shell, add::layer()});
    }
    add::pop();
    return shell;
}


int main() {
    // --------------------------------------------------------------------------
    //  streets and blocks
    // --------------------------------------------------------------------------
    const double SPAN = BLOCKS * 4.0;
    add::cuboid({SPAN / 2, -0.15, SPAN / 2}, {SPAN + 4, 0.3, SPAN + 4}, ROAD);

    for (int bx = 0; bx < BLOCKS; ++bx) {
        for (int bz = 0; bz < BLOCKS; ++bz) {
            double x0 = bx * 4.0, z0 = bz * 4.0;
            if (rng.random() < 0.12) {                 // a park
                add::cuboid({x0 + 1.5, 0.02, z0 + 1.5}, {3.2, 0.08, 3.2}, PARK);
                int trees = (int)rng.randint(2, 5);
                for (int tree = 0; tree < trees; ++tree) {
                    double px = x0 + rng.uniform(0.3, 2.7);
                    double pz = z0 + rng.uniform(0.3, 2.7);
                    double h = rng.uniform(0.6, 1.3);
                    add::cylinder({px, 0, pz}, {px, h, pz}, 0.06, 6, {90, 60, 40});
                    add::sphere({px, h + 0.28, pz}, 0.32, 8, {60, 150, 60});
                }
                continue;
            }
            add::cuboid({x0 + 1.5, 0.02, z0 + 1.5}, {3.4, 0.08, 3.4}, {90, 90, 96});
            int cells = (int)rng.randint(1, 4);
            for (int cell = 0; cell < cells; ++cell) {
                double w = rng.uniform(0.7, 1.4);
                double d = rng.uniform(0.7, 1.4);
                double h = rng.uniform(1.2, 7.0) * (add::detail::py_pow(bx - BLOCKS / 2.0, 2)
                                                    + add::detail::py_pow(bz - BLOCKS / 2.0, 2) < 4 ? 1.6 : 1.0);
                int style = rng.choice(std::vector<int>{0, 0, 1, 2, 3});
                add::Mesh piece = tower(w, d, h, style);
                double x = x0 + rng.uniform(0.7, 2.3);    // (drawn one by one, in Python's order)
                double z = z0 + rng.uniform(0.7, 2.3);
                add::mesh(add::move(piece, {x, 0, z}));
            }
        }
    }

    add::mesh(add::limit_colors(add::layer(), 50));   // at most 50 colours, so the .obj suits Sketchfab
    add::check();
    add::save("city.off");
}

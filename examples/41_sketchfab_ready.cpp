// 41 -- getting a model ready for Sketchfab: file size and colour count.
//
// Sketchfab takes ``.obj`` + ``.mtl`` (upload both in one zip).  Two things
// matter: the file size (100 MB on the free plan; the course asks for 50) and
// the number of *materials* -- every distinct colour of the model becomes
// one, and Sketchfab starts merging them above 100.  A gradient painted with
// ``add::color_by`` can easily use thousands of shades, so the recipe is:
//
// 1. build, and paint as freely as you like;
// 2. ``add::palette`` shows how many colours there are and which are common;
// 3. ``add::limit_colors(M, 50)`` groups similar shades into at most 50;
// 4. ``add::obj_size`` says how big the .obj will be before writing it;
// 5. ``add::save("x.obj", M, std::nullopt, 50)`` does step 3 while saving.
//
// The model: a vase from ``add::revolve`` painted with a two-way gradient, a
// quad sphere with a rainbow, and an owl surface (``add::surface_function``
// fed to ``add::parametric`` with our own range and colouring).
//
// Parameter: ``COLORS`` (the colour budget).
#include "add.hpp"

const int COLORS = 50;


// What Python's print() shows for a list of (colour, count) pairs: [((4, 4, 130), 482), ...].
std::string str(const std::vector<std::pair<add::Color, int>>& items) {
    std::string out = "[";
    for (size_t i = 0; i < items.size(); ++i) {
        const add::Color& c = items[i].first;
        out += (i > 0 ? ", " : "") + std::string("((") + std::to_string(c.r) + ", " + std::to_string(c.g) + ", "
               + std::to_string(c.b) + "), " + std::to_string(items[i].second) + ")";
    }
    return out + "]";
}


// a vase painted by height *and* angle: thousands of different shades
add::Point2 vase(double t) {
    return {1.2 + 0.5 * add::sin(2.2 * t) + 0.15 * add::cos(9 * t), t};
}


int main() {
    add::revolve(vase, {-4, 0, 0}, {-4, 1, 0}, 0, 4.5, 90, 72,
                 [](double t, double a) { return add::hsv(t / 6.0 + 0.1 * add::sin(4 * a), 0.8, 0.95); },
                 2 * add::pi, true);

    // a quad sphere (six patches of quads) painted by direction.  add::make()
    // builds it as a separate mesh, so the vase is not scooped up with it.
    add::Mesh ball = add::make([] { add::quadsphere({0, 1.5, 0}, 1.5, 30); });
    ball = add::color_by(ball, [](const add::Point& p) { return add::hsv((p[1] + 1) / 6.0, 0.9, 1.0); });
    add::mesh(ball);

    // the owl from the catalogue, but on our own parameter range and colouring
    add::SurfaceFn owl = add::surface_function("owl");
    add::Mesh sheet = add::make([&] {
        add::parametric(owl, 0, 4 * add::pi, 160, 0.001, 1, 30,
                        [](double /*u*/, double v) { return add::gradient(v, "navy", "white"); },
                        false, false, false, 0.04);
    });
    add::mesh(add::place(add::fit(sheet, 3.2), {4.5, 1.6, 0}));

    add::Mesh model = add::layer();
    std::printf("colours before: %zu\n", add::palette(model).size());
    std::vector<std::pair<add::Color, int>> most_used = add::palette(model);
    most_used.resize(std::min<size_t>(most_used.size(), 3));      // (Python: [:3])
    std::printf("most used: %s\n", str(most_used).c_str());
    std::printf("obj size before: %.2f MB\n", add::obj_size(model) / 1e6);

    add::Mesh small = add::limit_colors(model, COLORS);
    std::printf("colours after : %zu\n", add::palette(small).size());
    add::mesh(small);
    add::check();
    add::save("sketchfab_ready.off");
    add::save("sketchfab_ready.obj", small);              // .obj + .mtl, at most 50 materials
    std::printf("written sketchfab_ready.obj, %.2f MB\n", add::obj_size(small) / 1e6);
}

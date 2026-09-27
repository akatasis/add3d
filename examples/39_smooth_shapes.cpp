// 39 -- pull a few corners, then round the shape: generalised Catmull-Clark.
//
// Front row: a box is taken out as a layer, two of its corners are moved with
// ``add::set_vertex`` (``std::nullopt`` keeps a coordinate as it was), and the result
// is rounded into its Catmull-Clark limit surface with ``add::smooth``.  The
// control mesh is drawn next to it as a wire frame so that you can see what
// was rounded.  Every cell keeps the colour of the control face it lies on.
//
// Middle row: the same pentagonal prism smoothed with ``n = 1 ... 7`` cells
// per control edge.  Classical subdivision only reaches 2, 4, 8 ...; the
// generalised algorithm (Sabaliauskas 2026) gives every ``n``, with all the
// vertices exactly on the smooth surface.  Odd ``n`` leave a small polygon in
// the middle of each face, even ``n`` meet at a centre node.
//
// Back row: a flat seven-pointed star -- one single polygon -- sampled
// with ``uniform = false`` (the plain characteristic-map grid, cells crowd
// towards the centre) and ``uniform = true`` (the paper's reparameterisation,
// cells evenly sized).  The cells are drawn as wire frames.
//
// Parameter: ``PULL`` (how far the two corners are pulled out).
#include "add.hpp"

const double PULL = 1.6;


// What Python's print() shows for a list of three numbers: [2.6, 2.6, 1.0].
std::string str(const add::Point& p) {
    return "[" + add::detail::py_repr(p[0]) + ", " + add::detail::py_repr(p[1]) + ", "
           + add::detail::py_repr(p[2]) + "]";
}


int main() {
    // --- front row: the pulled box -------------------------------------------
    add::box({0, 0, 0}, 2, "gold");
    add::Mesh block = add::layer();                       // 8 vertices, 6 faces
    block = add::color_random(block, 3);                  // one colour per face
    int i = add::nearest_vertex(block, {1, 1, 1});        // the corner at (1, 1, 1)
    int j = add::nearest_vertex(block, {-1, -1, 1});
    block = add::set_vertex(block, i, {1 + PULL, 1 + PULL, std::nullopt});    // pull it out, keep z
    block = add::set_vertex(block, j, {-1 - PULL, std::nullopt, 1 + PULL});
    std::printf("moved corners %d and %d -> %s %s\n", i, j,
                str(add::vertex(block, i)).c_str(), str(add::vertex(block, j)).c_str());

    add::wireframe(add::move(block, {-4.5, 0, 4}), 0.05, 8, add::Color(40, 40, 40));
    add::mesh(add::move(add::smooth(block, 8), {0, 0, 4}));           // 8 cells per edge
    add::mesh(add::move(add::catmull_clark(block, 2), {4.5, 0, 4}));  // classical, 2 steps

    // --- middle row: n = 1 ... 7 on one prism --------------------------------
    add::Mesh prism = add::make([] { add::prism(add::profile_polygon(5, 1.0), 1.4, "teal"); });  // not layer():
    prism = add::color_random(prism, 5);                                                         // the scene is not empty
    for (int n = 1; n < 8; ++n) {
        double x = (n - 4) * 2.6;
        add::mesh(add::move(add::smooth(prism, n), {x, 0, -0.5}));
        add::text(std::to_string(n), {x, -1.0, 1.0}, 0.5, std::nullopt, "black", {1, 0, 0}, {0, 0, -1},
                  "center");
    }

    // --- back row: uniform or not, on a single star polygon ------------------
    add::Profile star = add::profile_star(7, 2.0, 1.1);
    add::Points corners;
    for (auto [x, y] : star)
        corners.push_back({x, 0, y});
    std::reverse(corners.begin(), corners.end());         // (Python: [::-1])
    add::Mesh face = add::make([&] { add::polygon(corners, "orange"); });
    for (auto [x, uniform, label] : std::vector<std::tuple<double, bool, std::string>>{{-3.2, false, "PLAIN"},
                                                                                        {3.2, true, "UNIFORM"}}) {
        add::Mesh grid = add::smooth(face, 6, uniform);
        add::mesh(add::move(grid, {x, -0.6, -5}));
        add::wireframe(add::move(grid, {x, -0.6, -5}), 0.025, 6, add::Color(40, 40, 40), false);
        add::text(label, {x, -0.6, -2.4}, 0.4, std::nullopt, "black", {1, 0, 0}, {0, 0, -1},
                  "center");
    }

    add::check();
    add::save("smooth_shapes.off");
}

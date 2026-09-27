// 31 -- the workbench: measuring, repairing, inspecting and saving.
//
// Not every function draws.  This example is a tour of the ones that look
// *at* a model: ``stats``/``check`` report on it, ``bbox``, ``size``,
// ``center``, ``middle``, ``area`` and ``volume`` measure it, ``inside``
// asks whether a point is in it, and ``clean``, ``heal``, ``fix_normals``
// and ``triangulate`` repair it.  A deliberately broken mesh is built by
// hand with the ``Mesh`` class, repaired, and shown next to the original.
// The models are saved in every format (``save``, ``off``, ``obj``) and one
// is ``load``-ed straight back.
//
// Parameter: ``SAMPLES`` (points thrown at the torus for the inside test).
#include <cstdio>                                        // std::remove (Python: os.remove)
#include "add.hpp"

const int SAMPLES = 400;


// What Python's print() shows for a mesh, a list of three numbers and a colour:
// <Mesh 8 vertices, 6 faces>, [1.0, 2.5, 0.0] and (120, 190, 255).
std::string str(const add::Mesh& M) {
    return "<Mesh " + std::to_string(M.V.size()) + " vertices, " + std::to_string(M.F.size()) + " faces>";
}

std::string str(const add::Point& p) {
    return "[" + add::detail::py_repr(p[0]) + ", " + add::detail::py_repr(p[1]) + ", "
           + add::detail::py_repr(p[2]) + "]";
}

std::string str(const add::Color& c) {
    return "(" + std::to_string(c.r) + ", " + std::to_string(c.g) + ", " + std::to_string(c.b) + ")";
}

// [round(c, n) for c in p]
add::Point rounded(const add::Point& p, int n) {
    return {add::detail::py_round(p[0], n), add::detail::py_round(p[1], n), add::detail::py_round(p[2], n)};
}


int main() {
    add::Random rng(1);
    add::axes({0, 0, 0}, 2.5);

    // --------------------------------------------------------------------------
    //  1. a broken model, made by hand, and its repaired twin
    // --------------------------------------------------------------------------
    add::Mesh M;                                             // a cube, face by face
    add::Points corners = {{0, 0, 0}, {1, 0, 0}, {1, 1, 0}, {0, 1, 0}, {0, 0, 1}, {1, 0, 1}, {1, 1, 1}, {0, 1, 1}};
    for (const add::Point& p : corners)
        M.add_vertex(p);
    M.add_face({0, 3, 2, 1}, "red");                         // bottom
    M.add_face({4, 5, 6, 7}, "red");                         // top
    M.add_face({0, 1, 5, 4}, "red");                         // front
    M.add_face({2, 3, 7, 6}, "red");                         // back
    M.add_face({1, 2, 6, 5}, "red");                         // right
    M.add_face({3, 0, 4, 7}, "red");                         // left, wound the WRONG way
    M.add_face({3, 0, 4, 7}, "red");                         // ... and added twice
    M.add_face({0, 3, 7, 4}, "red");                         // ... and once more, the right way
    M.add_vertex({0.5, 0.5, 0.5});                           // an unused vertex
    std::printf("hand-made cube: %s outward volume %.3f\n", str(M).c_str(), add::volume(M));
    add::Mesh broken = add::zoom(M, 2.0, add::Point{0, 0, 0});
    add::mesh(add::move(broken, {-6, 0, -3}));

    add::Mesh repaired = add::clean(broken);                 // weld, drop duplicates, fix winding
    repaired = add::fix_normals(repaired);
    std::printf("after clean(): %s volume %.3f closed: %s\n", str(repaired).c_str(), add::volume(repaired),
                add::stats(repaired).closed ? "True" : "False");
    add::mesh(add::color(add::move(repaired, {-3, 0, -3}), "green"));
    add::text("BROKEN", {-6.2, -0.7, -0.9}, 0.4, std::nullopt, "red", {1, 0, 0}, {0, 0, -1}, "left", 1.0, 5);
    add::text("CLEANED", {-3.4, -0.7, -0.9}, 0.4, std::nullopt, "green", {1, 0, 0}, {0, 0, -1}, "left", 1.0, 5);

    // --------------------------------------------------------------------------
    //  2. a T-junction: two boxes sharing a wall at different resolutions
    // --------------------------------------------------------------------------
    add::push();
    add::cuboid({0, 0.5, 0}, {2, 1, 2}, "sky");
    add::cuboid({0, 1.5, 0.5}, {1, 1, 1}, "sky");            // sits on the first one's top
    add::Mesh pair = add::pop();
    std::printf("stacked boxes: open edges before heal: %d\n", add::stats(pair).open_edges);
    add::Mesh joined = add::heal(add::union_(add::cut(pair, {0, 1, 0}, {0, 1, 0}),
                                             add::cut(pair, {0, 1, 0}, {0, -1, 0})));
    std::printf("               open edges after union+heal: %d\n", add::stats(joined).open_edges);
    add::mesh(add::move(joined, {1.5, 0, -3.5}));
    add::mesh(add::move(add::color(add::triangulate(joined), "teal"), {4.5, 0, -3.5}));
    add::text("UNION", {1.0, -0.7, -0.9}, 0.4, std::nullopt, "navy", {1, 0, 0}, {0, 0, -1}, "left", 1.0, 5);
    add::text("TRIANGLES", {3.6, -0.7, -0.9}, 0.4, std::nullopt, "teal", {1, 0, 0}, {0, 0, -1}, "left", 1.0, 5);

    // --------------------------------------------------------------------------
    //  3. inside or outside?  random points coloured by a torus
    // --------------------------------------------------------------------------
    add::push();
    add::torus({0, 0, 0}, 1.6, 0.6, 36, 18, "gold");
    add::Mesh ring = add::pop();
    add::mesh(add::move(ring, {-4, 1.2, 3}));
    add::Points points = add::random_points(SAMPLES, {-2.4, -0.8, -2.4}, {2.4, 0.8, 2.4}, 3);
    std::vector<bool> answers = add::inside(ring, points);   // one call for all the points
    int hits = 0;
    for (bool hit : answers)
        hits += hit;
    for (size_t i = 0; i < points.size(); ++i) {
        add::Point q = points[i];
        bool hit = answers[i];
        if (hit)
            add::sphere({q[0] - 4, q[1] + 1.2, q[2] + 3}, 0.07, 3, "red");
        else
            add::sphere({q[0] - 4, q[1] + 1.2, q[2] + 3}, 0.04, 2, {90, 90, 100});
    }
    double box_volume = 4.8 * 1.6 * 4.8;
    std::printf("torus volume by counting: %.2f, exact %.2f, mesh %.2f\n",
                box_volume * hits / SAMPLES, 2 * add::detail::py_pow(add::pi, 2) * 1.6 * add::detail::py_pow(0.6, 2),
                add::volume(ring));

    // --------------------------------------------------------------------------
    //  4. measuring: bounding box, sizes, centres, area
    // --------------------------------------------------------------------------
    add::push();
    add::cone({0, 0, 0}, {0, 2.5, 0}, 1.0, 24, "orange");
    add::Mesh cone = add::pop();
    auto [lo, hi] = add::bbox(cone);
    std::printf("cone bbox %s %s size %s\n", str(lo).c_str(), str(hi).c_str(), str(add::size(cone)).c_str());
    std::printf("cone centre of mass %s, middle of box %s\n",
                str(rounded(add::center(cone), 2)).c_str(), str(rounded(add::middle(cone), 2)).c_str());
    std::printf("cone area %.3f (exact %.3f)\n", add::area(cone),
                add::pi * 1.0 * (1.0 + add::sqrt(1 + add::detail::py_pow(2.5, 2))));
    add::mesh(add::move(cone, {1.5, 0, 3}));
    add::push();
    add::box({0, 0, 0}, 0.12, "black");
    add::Mesh dot = add::pop();
    add::mesh(add::move(dot, {1.5 + add::center(cone)[0], add::center(cone)[1], 3}));    // mark the centroid
    add::Mesh frame = add::copy(cone);                       // an independent copy to play with
    add::wireframe(add::move(add::triangulate(frame), {4.5, 0, 3}), 0.02, 5, add::Color("orange"), false);

    // --------------------------------------------------------------------------
    //  5. colours and saving
    // --------------------------------------------------------------------------
    std::printf("rgb('sky') = %s  gradient = %s  random = %s\n", str(add::rgb("sky")).c_str(),
                str(add::gradient(0.5, "red", "blue")).c_str(), str(add::random_color(7)).c_str());
    add::push();
    add::sphere({0, 0, 0}, 0.9, 12, "white");
    add::Mesh ball = add::color_random(add::pop(), 2);       // every face its own colour
    ball = add::limit_colors(ball, 24);                      // ... then grouped into 24 shades
    add::mesh(add::move(ball, {7.5, 1.0, 3}));
    add::glyph("Z", {7.0, 2.3, 3}, {1, 0, 0}, {0, 1, 0}, 0.6, 0.04, "navy");

    add::Mesh& everything = add::scene();                    // the live scene object
    std::printf("scene so far: %s\n", str(everything).c_str());
    std::printf("colours: %zu  .obj size: %.2f MB\n", add::palette().size(), add::obj_size() / 1e6);
    add::save("workbench.obj", add::scene(), false, 50);   // .obj + .mtl; the scene stays (false: keep it)
    add::save("workbench.ply", add::scene(), false);       // (without false -- or a mesh -- the scene is emptied)
    add::obj("workbench_copy.obj");                          // add.py 1.2 style: writes and clears
    std::printf("after obj(): scene is %s\n", str(add::scene()).c_str());
    std::remove("workbench_copy.obj");
    std::remove("workbench_copy.mtl");
    add::Mesh back = add::load("workbench.obj");             // and straight back in
    add::mesh(back);
    add::check();
    add::off("workbench.off");

    // and finally the library's own one-line demonstration model
    std::printf("demo written to %s\n", add::demo("demo.off").c_str());
}

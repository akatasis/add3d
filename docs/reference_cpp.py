# -*- coding: utf-8 -*-
"""
The C++ twin of every documentation example in ``reference.py``.

``EXAMPLES[name]`` is the example of the public name ``name`` of add.py,
written in C++ for add.hpp: the body of a function, which
``tests/cpp/run_docs.py`` compiles and runs next to the Python example (a
fresh scene, ``seed(0)`` first, the scene left at the end written out) and
checks that both build the very same model, byte for byte.
``tools/make_docs.py`` shows it under the Python example.

How Python turns into C++ here:

* ``add.box([0, 0, 0], 2, "red")``  ->  ``add::box({0, 0, 0}, 2, "red");``
* keyword arguments are given in order (the declaration names them), and a
  comment says which one was meant when it is not obvious;
* ``M=None`` (the scene) is the overload without the mesh;
* a function passed as an argument is a lambda;
* ``add.make(add.box, [0, 0, 0], 2)``  ->  ``add::make([] { add::box({0, 0, 0}, 2); })``;
* ``union`` is ``add::union_`` (``union`` is a C++ keyword);
* ``print(x)`` -> ``std::cout << x << "\\n";`` (or ``std::printf``).
"""

#: The Python names with no C++ function of their own: what to use instead
#: (English, Lithuanian).  (``union`` is ``add::union_``.)
NO_CPP = {
    "as_mesh": ("C++ has no as_mesh: every function takes an add::Mesh, and the "
                "scene is add::scene().",
                "C++ neturi as_mesh: kiekviena funkcija priima add::Mesh, o scena "
                "yra add::scene()."),
    "vertices": ("In C++ the points of the scene are add::scene().V.",
                 "C++ kalboje scenos taškai yra add::scene().V."),
    "faces": ("In C++ the faces of the scene are add::scene().F and their colours "
              "add::scene().C.",
              "C++ kalboje scenos sienos yra add::scene().F, o jų spalvos -- "
              "add::scene().C."),
}

EXAMPLES = {

"BOOL_EPS": """\
std::cout << add::BOOL_EPS << "\\n";
""",

"COLORS": """\
for (const std::pair<const std::string, std::array<int, 3>>& c : add::COLORS())
    std::cout << c.first << " ";     // black blue brown ... (a std::map is sorted)
std::cout << "\\n";
add::box({0, 0, 0}, 1, "gold");
""",

"DEFAULT_COLOR": """\
add::box({0, 0, 0}, 1);               // drawn in add::DEFAULT_COLOR
std::cout << add::DEFAULT_COLOR << "\\n";
""",

"EPS": """\
std::cout << add::EPS << "\\n";                     // 1e-09
""",

"Mesh": """\
add::Mesh M;
int a = M.add_vertex({0, 0, 0});
int b = M.add_vertex({1, 0, 0});
int c = M.add_vertex({0, 1, 0});
M.add_face({a, b, c}, "red");
std::cout << M << " " << M.polygons() << " " << M.V[1] << " " << M.F[0].size() << "\\n";
add::mesh(M);
""",

"PALETTE": """\
for (const std::pair<const std::string, add::Color>& p : add::PALETTE())
    std::cout << p.first << " " << p.second << "\\n";
add::pixels({"rgb", "b.r"}, 0.5);    // letters of the palette
""",

"SKETCHFAB_COLORS": """\
add::sphere({0, 0, 0}, 1, 10, "red");
add::check(add::scene(), 10000, 3, false, add::SKETCHFAB_MB, add::SKETCHFAB_COLORS);   // max_colors
""",

"SKETCHFAB_MB": """\
std::cout << add::SKETCHFAB_MB << " " << add::SKETCHFAB_COLORS << "\\n";
""",

"SURFACES": """\
const add::SurfaceEntry& info = add::SURFACES().at("klein_bottle");
std::cout << info.note << " " << info.u << " " << info.v;
for (const std::pair<const std::string, double>& c : info.params)
    std::cout << " " << c.first << "=" << c.second;
std::cout << "\\n";
""",

"Stream": """\
add::Stream out("parts.off");
for (int i = 0; i < 5; ++i) {
    add::sphere({i * 3.0, 0, 0}, 1, 10, add::hsv(i / 5.0));
    out.add();
}
out.close();                          // as at the end of Python's with block
std::cout << out.faces << " " << out.vertices << "\\n";
""",

"add_solids": """\
add::Mesh a = add::make([] { add::box({0, 0, 0}, 2, "red"); });
add::Mesh b = add::make([] { add::box({1, 1, 1}, 2, "blue"); });
add::mesh(add::add_solids(a, b));
""",

"adjacency": """\
add::Mesh M = add::make([] { add::octahedron({0, 0, 0}, 1); });
std::vector<std::vector<int>> adj = add::adjacency(M);
for (size_t i = 0; i < adj.size(); ++i) {
    std::cout << i << ":";
    for (int nb : adj[i]) std::cout << " " << nb;
    std::cout << "\\n";
}
""",

"aim": """\
add::Mesh rocket = add::make([] { add::cone({0, 0, 0}, {0, 3, 0}, 0.5, 16, "red"); });
add::mesh(add::aim(rocket, {1, 1, 0}));   // its axis now points along (1, 1, 0)
""",

"align": """\
add::Mesh M = add::make([] { add::box({0, 0, 0}, 2, "gold"); });
add::mesh(add::align(M, {0, 0, 0}, {-1, -1, -1}));    // anchor: the corner at the origin
""",

"along": """\
add::Mesh car = add::make([] { add::cuboid({0, 0.2, 0}, {0.6, 0.4, 1}, "red"); });
auto loop = [](double t) { return add::Point{4 * add::cos(t), 0, 4 * add::sin(t)}; };
add::mesh(add::along(car, loop, 12, 0, 2 * add::pi, add::Point{0, 1, 0}, true));   // closed
""",

"arch": """\
add::arch({-2, 0, 0}, {2, 0, 0}, 3, 0.4, "grey");
""",

"area": """\
add::Mesh M = add::make([] { add::box({0, 0, 0}, 2); });
std::cout << add::area(M) << "\\n";
""",

"array_grid": """\
add::Mesh block = add::make([] { add::box({0, 0, 0}, 0.8, "sky"); });
add::mesh(add::array_grid(block, {1, 1, 1}, {4, 3, 4}));
""",

"array_linear": """\
add::Mesh post = add::make([] { add::cylinder({0, 0, 0}, {0, 2, 0}, 0.1, 8, "brown"); });
add::mesh(add::array_linear(post, {1.5, 0, 0}, 8));
""",

"array_mirror": """\
add::Mesh half = add::make([] { add::cone({1, 0, 0}, {3, 2, 0}, 0.5, 12, "gold"); });
add::mesh(add::array_mirror(half, {0, 0, 0}, {1, 0, 0}));
""",

"array_radial": """\
add::Mesh step = add::make([] { add::cuboid({2, 0, 0}, {2, 0.2, 0.6}, "grey"); });
add::mesh(add::array_radial(step, 24, {0, 1, 0}, {0, 0, 0}, 2 * add::pi, 0.25));   // rise: a spiral staircase
""",

"arrow": """\
add::arrow({0, 0, 0}, {3, 2, 0}, 0.08, "red");
""",

"as_mesh": """\
add::box({0, 0, 0}, 1, "red");
add::Mesh& M = add::scene();          // the scene itself (C++ has no as_mesh)
add::Mesh pair(M.V, M.F, M.C);        // no old string lists in C++: a Mesh from V, F and C
std::cout << pair.polygons() << "\\n";
""",

"axes": """\
add::axes({0, 0, 0}, 3);
add::box({1, 1, 1}, 1, "gold");
""",

"ball": """\
add::ball({0, 0, 0}, 1, 10, "red");
""",

"bbox": """\
add::Mesh M = add::make([] { add::sphere({1, 2, 3}, 1, 5); });
std::array<add::Point, 2> bb = add::bbox(M);
std::cout << bb[0] << " " << bb[1] << "\\n";
""",

"beam": """\
add::beam({0, 0, 0}, {4, 2, 1}, 0.3, 0.2, "brown");
""",

"bend": """\
add::Mesh bar = add::make([] { add::cuboid({0, 3, 0}, {0.5, 6, 0.5}, "gold"); });
bar = add::refine(bar, 3);
add::mesh(add::bend(bar, 0.4, 1, 0));   // axis, around
""",

"block": """\
add::block({0, 0, 0}, {4, 1, 2}, "brown");
""",

"boundary_edges": """\
add::Mesh sheet = add::make([] { add::grid({0, 0, 0}, {4, 4}, 4, 4); });
std::cout << add::boundary_edges(sheet).size() << "\\n";    // 16 edges around the rim
std::cout << add::boundary_edges(add::make([] { add::box({0, 0, 0}, 1); })).size() << "\\n";   // closed
""",

"boundary_loops": """\
add::Mesh sheet = add::make([] { add::grid({0, 0, 0}, {4, 4}, 4, 4); });
std::vector<int> rim = add::boundary_loops(sheet)[0];
add::Points points;
for (int i : rim) points.push_back(sheet.V[i]);
add::polyline(points, 0.05, 8, "red", true);   // closed
""",

"box": """\
add::box({0, 0, 0}, 2, "red");
""",

"bricks": """\
add::bricks({0, 0, 0}, 6, 3, {1.0, 0.5, 0.5}, "brown");   // brick (the default), color
""",

"capsule": """\
add::capsule({0, 0, 0}, {0, 3, 0}, 0.5, 24, "red");
""",

"catmull_clark": """\
add::box({0, 0, 0}, 2, "red");
add::mesh(add::catmull_clark(add::layer(), 3));     // a rounded cube, 384 quads
""",

"center": """\
add::Mesh M = add::make([] { add::box({1, 2, 3}, 2); });
std::cout << add::center(M) << "\\n";   // [1.0, 2.0, 3.0]
""",

"chaikin": """\
add::Profile outline = add::chaikin(add::Profile{{0, 0}, {2, 0}, {2, 2}, {0, 2}}, 3, true);   // closed
add::prism(outline, 1, "teal");           // a rounded square bar
""",

"check": """\
add::sphere({0, 0, 0}, 2, 30, "red");
add::box({3, 0, 0}, 1, "blue");
add::cone({0, 3, 0}, {0, 5, 0}, 1, 12, "gold");
bool ok = add::check();
std::cout << std::boolalpha << ok << "\\n";
""",

"circle": """\
add::circle({0, 0, 0}, {0, 1, 0}, 2, 32, {255, 200, 0});
""",

"clamp": """\
std::cout << add::clamp(1.7) << " " << add::clamp(-3, -1, 1) << "\\n";
""",

"clean": """\
add::box({0, 0, 0}, 2, "red");
add::box({2, 0, 0}, 2, "red");            // touches the first one
add::cuboid({1, 0, 0}, {6, 0.5, 2}, "blue");   // runs through both: overlapping faces
add::CleanReport report;
add::Mesh model = add::clean(add::layer(), 1e-7, true, true, true, true, true, false, &report);
std::cout << report.vertices_removed << " " << report.faces_removed << " " << report.faces_cut << " "
          << report.faces_split << "\\n";  // hidden walls gone, overlaps cut
add::mesh(model);
""",

"clear": """\
add::box({0, 0, 0}, 1, "red");
add::clear();
std::cout << add::scene().F.size() << "\\n";   // 0 (the faces of the scene)
""",

"color": """\
add::Mesh ball = add::make([] { add::sphere({0, 0, 0}, 1, 10, "red"); });
add::mesh(add::color(ball, "blue"));
""",

"color_by": """\
add::Mesh M = add::make([] { add::sphere({0, 0, 0}, 2, 20); });
add::mesh(add::color_by(M, [](const add::Point& p) { return add::hsv((p[1] + 2) / 4.0); }));
""",

"color_by_sides": """\
add::Mesh ico = add::make([] { add::icosahedron({0, 0, 0}, 3); });
add::Mesh ball = add::color_by_sides(add::truncate(ico), {{5, "black"}, {6, "white"}});
add::mesh(add::smooth(ball, 8));
""",

"color_gradient": """\
add::Mesh M = add::make([] { add::cylinder({0, 0, 0}, {0, 5, 0}, 1, 32); });
add::mesh(add::color_gradient(M, "navy", "white"));
""",

"color_random": """\
add::Mesh M = add::make([] { add::dodecahedron({0, 0, 0}, 2); });
add::mesh(add::color_random(M, 3));   // seed
""",

"column": """\
add::column({0, 0, 0}, 4, 0.4, "white");
""",

"common": """\
add::Mesh a = add::make([] { add::box({0, 0, 0}, 2, "red"); });
add::Mesh b = add::make([] { add::box({1, 1, 1}, 2, "blue"); });
add::mesh(add::common(a, b));
""",

"concave_faces": """\
add::polygon({{0, 0, 0}, {0, 0, 3}, {1, 0, 3}, {1, 0, 1}, {4, 0, 1}, {4, 0, 0}}, "red");   // an L
std::cout << add::concave_faces() << "\\n";    // 1 -- a viewer would fan it over the notch
add::mesh(add::clean(add::layer()));
std::cout << add::concave_faces() << "\\n";    // 0 -- cut into triangles
""",

"cone": """\
add::cone({0, 0, 0}, {0, 3, 0}, 1, 32, "red");
""",

"cone2": """\
add::cone2({0, 0, 0}, {0, 3, 0}, 1, 32, {255, 0, 0});
""",

"cone_open": """\
add::cone_open({0, 0, 0}, {0, 3, 0}, 1, 32, "red");
""",

"copy": """\
add::box({0, 0, 0}, 1, "red");
add::Mesh M = add::copy();             // a copy of the scene
M.V[0][1] += 5;                        // the scene is untouched
std::cout << add::scene().V[0][1] << "\\n";
""",

"cube": """\
add::cube({0, 0, 0}, 2, {255, 0, 0});
""",

"cube2": """\
add::cube2({0, 0, 0}, 3, 0.2, {212, 175, 55});
""",

"cuboid": """\
add::cuboid({0, 0, 0}, {4, 1, 2}, "brown");
""",

"cuboid3D": """\
add::cuboid3D({0, 0, 0}, {4, 1, 2}, "brown");
""",

"cup": """\
add::cup({0, 0, 0}, {0, 2, 0}, 0.8, 32, "teal");
""",

"curve": """\
auto knot = [](double t) {
    return add::Point{add::sin(t) + 2 * add::sin(2 * t), add::cos(t) - 2 * add::cos(2 * t),
                      -add::sin(3 * t)};
};

add::curve(knot, 0, 2 * add::pi, 200, 16, 0.25, "red", true);   // isConnected
""",

"cut": """\
add::Mesh ball = add::make([] { add::sphere({0, 0, 0}, 2, 10, "red"); });
add::mesh(add::cut(ball, {0, 0.5, 0}, {0, 1, 0}));     // keeps the part below y = 0.5
""",

"cylinder": """\
add::cylinder({0, 0, 0}, {0, 3, 0}, 0.5, 24, "gold");
""",

"cylinder2": """\
add::cylinder2({0, 0, 0}, {0, 3, 0}, 0.5, 24, {212, 175, 55});
""",

"cylinder3": """\
add::cylinder3({0, 0, 0}, {0, 2, 0}, 0.8, 32, {0, 128, 128});
""",

"deform": """\
add::Mesh bar = add::make([] { add::cuboid({0, 0, 0}, {8, 0.5, 0.5}, "gold"); });
bar = add::refine(bar, 3);            // more vertices to bend
add::mesh(add::deform(bar, [](const add::Point& p) {
    return add::Point{p[0], p[1] + add::sin(p[0]), p[2]};
}));
""",

"demo": """\
add::demo("demo.off");
""",

"difference": """\
add::Mesh plate = add::make([] { add::cuboid({0, 0, 0}, {4, 1, 4}, "brown"); });
add::Mesh drill = add::make([] { add::cylinder({0, -1, 0}, {0, 1, 0}, 0.6, 32, "black"); });
add::mesh(add::difference(plate, drill));
""",

"direction": """\
std::cout << add::direction({0, 0, 0}, {0, 5, 0}) << "\\n";   // [0.0, 1.0, 0.0]
""",

"disc": """\
add::disc({0, 0, 0}, {0, 1, 0}, 2, 48, "gold");     // facing up
""",

"distance": """\
std::cout << add::distance({0, 0, 0}, {3, 4, 0}) << "\\n";
""",

"dodecahedron": """\
add::dodecahedron({0, 0, 0}, 1.5, "gold");
""",

"dual": """\
add::Mesh cube = add::make([] { add::box({0, 0, 0}, 2, "gold"); });
add::mesh(add::dual(cube));               // an octahedron
add::wireframe(cube, 0.03, 6, "black");
""",

"edge_length": """\
add::Mesh M = add::make([] { add::icosahedron({0, 0, 0}, 1); });
add::Edge ab = add::edges(M)[0];
std::cout << add::edge_length(M, ab.first, ab.second) << "\\n";
""",

"edge_lengths": """\
add::Mesh M = add::make([] { add::dodecahedron({0, 0, 0}, 1); });
std::vector<double> L = add::edge_lengths(M);
std::cout << L.size() << " " << *std::min_element(L.begin(), L.end()) << " "
          << *std::max_element(L.begin(), L.end()) << "\\n";
""",

"edges": """\
add::Mesh M = add::make([] { add::box({0, 0, 0}, 2); });
std::vector<add::Edge> E = add::edges(M);
std::cout << E.size();                       // 12 edges
for (int k = 0; k < 3; ++k) std::cout << " (" << E[k].first << ", " << E[k].second << ")";
std::cout << "\\n";
""",

"ellipsoid": """\
add::ellipsoid({0, 0, 0}, {3, 1, 1.5}, 12, "gold");
""",

"extrude": """\
add::extrude(add::profile_star(6, 1.0, 0.5), {0, 3, 0}, "gold",
             40, add::pi, [](double t) { return 1 - 0.5 * t; });   // steps, twist, scale
""",

"face_area": """\
add::Mesh M = add::make([] { add::box({0, 0, 0}, 2); });
std::cout << add::face_area(M, 0) << "\\n";
""",

"face_center": """\
add::Mesh M = add::make([] { add::box({0, 0, 0}, 2); });
std::cout << add::face_center(M, 0) << "\\n";
""",

"face_centers": """\
add::Mesh M = add::make([] { add::dodecahedron({0, 0, 0}, 2); });
for (add::Point c : add::face_centers(M))
    add::sphere(c, 0.15, 5, "red");
""",

"face_normal": """\
add::Mesh M = add::make([] { add::box({0, 0, 0}, 2); });
for (int i = 0; i < 6; ++i) {
    add::Point c = add::face_center(M, i), n = add::face_normal(M, i);
    add::arrow(c, c + n, 0.05, "red");
}
""",

"faces": """\
add::box({0, 0, 0}, 1, "red");
const add::Mesh& S = add::scene();      // add.faces in C++: the scene's faces S.F, colours S.C
std::cout << S.F.size() << " " << S.F[0].size() << " " << S.C[0] << "\\n";
""",

"fit": """\
add::Mesh ball = add::make([] { add::sphere({0, 0, 0}, 37, 10, "red"); });
add::mesh(add::fit(ball, 2));             // now 2 units across
""",

"fix_normals": """\
add::Mesh M = add::make([] { add::box({0, 0, 0}, 2, "red"); });
std::reverse(M.F[0].begin(), M.F[0].end());      // spoil one face
std::cout << add::volume(M) << " " << add::volume(add::fix_normals(M)) << "\\n";
""",

"flow": """\
auto field = [](const add::Point& p) { return add::Point{-p[2], 0.3, p[0]}; };   // a spiral field
add::Points pts = add::flow(field, {1, 0, 0}, 0.05, 200);
std::cout << pts.size() << " " << pts.back() << "\\n";
""",

"frame": """\
add::frame({0, 0, 0}, 3, 0.2, "gold");
""",

"frustum": """\
add::frustum({0, 0, 0}, {0, 2, 0}, 1.0, 0.5, 32, "gold");
""",

"gear": """\
add::gear({0, 0, 0}, 16, 2, 0.4, "silver", std::nullopt, 0.4);   // depth, hole
""",

"glyph": """\
add::glyph("Ž", {0, 0, 0}, {1, 0, 0}, {0, 1, 0}, 2, 0.1, "red");
""",

"gradient": """\
for (int i = 0; i < 10; ++i)
    add::box({double(i), 0, 0}, 0.9, add::gradient(i / 9.0, "navy", "white"));
""",

"grid": """\
auto hills = [](double x, double z) { return 0.6 * add::sin(x) * add::cos(z); };

add::grid({0, 0, 0}, {10, 10}, 40, 40,
          [&](double x, double z) { return hills(x, z) < 0 ? "sky" : "green"; },   // color
          hills);                                                                  // height
""",

"ground": """\
add::Mesh ball = add::make([] { add::sphere({0, 5, 0}, 1, 10, "red"); });
add::mesh(add::ground(ball));            // now resting on y = 0
""",

"heal": """\
add::Mesh a = add::make([] { add::box({0, 0, 0}, 2, "red"); });
add::Mesh b = add::make([] { add::box({1, 1, 1}, 2, "blue"); });
add::Mesh fixed = add::heal(add::difference(a, b));
std::cout << std::boolalpha << add::stats(fixed).closed << "\\n";
""",

"heightmap": """\
add::heightmap({{1, 2, 3}, {2, 4, 2}, {3, 2, 1}}, 0.8, {0, 0, 0}, "green");   // origin, color
""",

"helix": """\
add::helix({0, 0, 0}, 1.5, 0.8, 5, 300, 0.15, 12, "silver");
""",

"hemisphere": """\
add::hemisphere({0, 0, 0}, 2, 16, "gold");
""",

"hsv": """\
for (int i = 0; i < 12; ++i)
    add::box({double(i), 0, 0}, 0.9, add::hsv(i / 12.0));
""",

"icosahedron": """\
add::icosahedron({0, 0, 0}, 1.5, "purple");
add::Mesh ico = add::make([] { add::icosahedron({0, 0, 0}, 1.5); });
std::cout << add::valence(ico, 0) << " " << add::mean_edge_length(ico) << "\\n";
""",

"icosphere": """\
add::icosphere({0, 0, 0}, 2, 4, [](const add::Point& d) { return d[1] > 0.7 ? "white" : "blue"; });
add::icosphere({5, 0, 0}, 2, 1, "gold");            // 80 triangles
""",

"inflate": """\
add::Mesh ico = add::make([] { add::icosahedron({0, 0, 0}, 2, "white"); });
add::Mesh ball = add::color_by_sides(add::truncate(ico), {{5, "black"}, {6, "white"}});
add::mesh(add::inflate(ball, 0.15));
""",

"inside": """\
add::Mesh ball = add::make([] { add::sphere({0, 0, 0}, 2, 10); });
std::cout << std::boolalpha << add::inside(ball, {0, 0, 0}) << " "
          << add::inside(ball, {5, 0, 0}) << "\\n";
""",

"intersect": """\
add::Mesh a = add::make([] { add::box({0, 0, 0}, 2, "red"); });
add::Mesh b = add::make([] { add::sphere({0, 0, 0}, 1.3, 10, "blue"); });
add::mesh(add::intersect(a, b));
""",

"jitter": """\
add::Mesh rock = add::make([] { add::sphere({0, 0, 0}, 1, 5, "grey"); });
add::mesh(add::jitter(rock, 0.08, 1));   // seed
""",

"label": """\
add::label("A", {0, 0, 0}, 1.0, std::nullopt, "navy");   // thickness, color
""",

"lathe": """\
add::lathe([](double t) { return add::Point2{1 + 0.3 * add::sin(3 * t), t}; },
           {0, 0, 0}, {0, 1, 0}, 0, 4, 40, 32, "teal");
""",

"layer": """\
add::box({0, 0, 0}, 1, "red");
add::Mesh brick = add::layer();                    // the scene is empty again
for (int i = 0; i < 5; ++i)
    add::mesh(add::move(brick, {i * 1.2, 0, 0}));
""",

"lerp": """\
std::cout << add::lerp(0, 10, 0.25) << "\\n";                                     // 2.5
std::cout << add::lerp(add::Point{0, 0, 0}, add::Point{2, 4, 6}, 0.5) << "\\n";   // [1.0, 2.0, 3.0]
""",

"limit_colors": """\
add::Mesh M = add::make([] { add::sphere({0, 0, 0}, 2, 20); });
M = add::color_by(M, [](const add::Point& p) { return add::hsv(p[1] / 4.0); });
std::cout << add::palette(M).size() << "\\n";
add::Mesh few = add::limit_colors(M, 50);
std::cout << add::palette(few).size() << "\\n";          // 50
add::save("few.obj", few);
""",

"load": """\
add::box({0, 0, 0}, 2, "red");
add::save("part.off");
add::Mesh part = add::load("part.off");
add::mesh(add::move(part, {3, 0, 0}));
""",

"load_font": """\
std::filesystem::create_directory("letters");
for (std::string ch : {"A", "B"}) {
    add::text(ch, {0, 0, 0}, 1, std::nullopt, "navy");   // thickness, color
    add::save("letters/" + ch + ".off");
}
std::map<std::string, add::Mesh> font = add::load_font("letters");
std::cout << font.size() << "\\n";
""",

"loft": """\
std::vector<add::Points> rings;
for (int i = 0; i < 6; ++i) {
    double r = 1 + 0.5 * add::sin(i);
    add::Points ring;
    for (int k = 0; k < 24; ++k) {
        double a = 2 * add::pi * k / 24;
        ring.push_back({r * add::cos(a), double(i), r * add::sin(a)});
    }
    rings.push_back(ring);
}
add::loft(rings, "teal");
""",

"make": """\
add::Mesh ball = add::make([] { add::sphere({0, 0, 0}, 1, 10, "red"); });
add::mesh(add::move(ball, {3, 0, 0}));
add::mesh(add::move(ball, {-3, 0, 0}));
""",

"mean_edge_length": """\
add::Mesh M = add::make([] { add::icosahedron({0, 0, 0}, 1); });
std::cout << add::mean_edge_length(M) << "\\n";            // 1.0515 for r = 1
""",

"mean_neighbor_distance": """\
add::Mesh ico = add::make([] { add::icosahedron({0, 0, 0}, 2); });
std::cout << add::mean_neighbor_distance(ico, 0) << "\\n";
""",

"merge": """\
add::Mesh a = add::make([] { add::box({0, 0, 0}, 1, "red"); });
add::Mesh b = add::make([] { add::sphere({2, 0, 0}, 0.6, 10, "blue"); });
add::Mesh both = add::merge({a, b});
std::cout << both.polygons() << "\\n";
add::mesh(both);
""",

"mesh": """\
add::Mesh ball = add::make([] { add::sphere({0, 0, 0}, 1, 10, "red"); });
add::mesh(ball);
add::mesh(add::move(ball, {2.5, 0, 0}));
""",

"middle": """\
add::Mesh M = add::make([] { add::cone({0, 0, 0}, {0, 4, 0}, 1, 12); });
std::cout << add::middle(M) << " " << add::center(M) << "\\n";   // bbox centre vs. vertex average
""",

"midpoint": """\
std::cout << add::midpoint({0, 0, 0}, {2, 2, 2}) << "\\n";     // [1.0, 1.0, 1.0]
""",

"mirror": """\
add::Mesh wing = add::make([] { add::cuboid({2, 0, 0}, {3, 0.2, 1}, "gold"); });
add::mesh(wing);
add::mesh(add::mirror(wing, {0, 0, 0}, {1, 0, 0}));
""",

"move": """\
add::Mesh ball = add::make([] { add::sphere({0, 0, 0}, 1, 10, "red"); });
add::mesh(add::move(ball, {3, 0, 0}));
""",

"move_vertex": """\
add::Mesh block = add::make([] { add::box({0, 0, 0}, 2, "gold"); });
block = add::move_vertex(block, 0, {-1, -1, -1});
add::mesh(block);
""",

"nearest_vertex": """\
add::Mesh M = add::make([] { add::sphere({0, 0, 0}, 1, 10); });
int i = add::nearest_vertex(M, {0, 5, 0});       // the top of the ball
std::cout << i << " " << add::vertex(M, i) << "\\n";
""",

"neighbors": """\
add::Mesh ico = add::make([] { add::icosahedron({0, 0, 0}, 1); });
for (int v : add::neighbors(ico, 0))      // five of them, in order around
    std::cout << v << " ";
std::cout << "\\n";
""",

"neighbours": """\
add::Mesh ico = add::make([] { add::icosahedron({0, 0, 0}, 1); });
for (int v : add::neighbours(ico, 0))
    std::cout << v << " ";
std::cout << "\\n";
""",

"newface": """\
add::newface({{0, 0, 0}, {2, 0, 0}, {1, 2, 0}}, {255, 0, 0});
""",

"obj": """\
add::box({0, 0, 0}, 2, "red");
add::obj("model.obj");                   // model.obj + model.mtl
""",

"obj_size": """\
add::Mesh M = add::make([] { add::sphere({0, 0, 0}, 1, 30, "red"); });
std::cout << add::obj_size(M) / 1e6 << " MB\\n";
""",

"octahedron": """\
add::octahedron({0, 0, 0}, 1.5, "green");
""",

"off": """\
add::box({0, 0, 0}, 2, "red");
add::off("model.off");
""",

"opacity": """\
add::Mesh glass = add::opacity(add::make([] { add::box({0, 0, 0}, 2, "sky"); }), 0.3);
add::mesh(glass);
add::sphere({0, 0, 0}, 0.5, 10, "red");  // seen through the glass in .obj
""",

"overlaps": """\
add::cuboid({0, 0, 0}, {2, 6, 1}, "red");
add::cuboid({0, 0, 0}, {5, 1, 1}, "blue");   // the front faces share a plane
std::cout << add::overlaps() << "\\n";        // 2 -- they would flicker
add::mesh(add::clean(add::layer()));
std::cout << add::overlaps() << "\\n";        // 0
""",

"palette": """\
add::Mesh M = add::make([] { add::sphere({0, 0, 0}, 2, 10); });
M = add::color_by(M, [](const add::Point& p) { return p[1] > 0 ? "red" : "blue"; });
for (const std::pair<add::Color, int>& entry : add::palette(M))
    std::cout << entry.first << " " << entry.second << "\\n";   // (0, 0, 255) 656, (255, 0, 0) 624
""",

"parametric": """\
auto torus = [](double u, double v) {
    return add::Point{(3 + add::cos(u)) * add::cos(v), add::sin(u),
                      (3 + add::cos(u)) * add::sin(v)};
};

add::parametric(torus, 0, 2 * add::pi, 24, 0, 2 * add::pi, 60, "gold",
                true, true);                 // wrap_u, wrap_v
add::parametric([](double u, double v) { return add::Point{u, add::sin(u) * add::cos(v), v}; },
                -3, 3, 30, -3, 3, 30,
                [](double u, double v) { return add::hsv(u / 6.0); },   // color
                false, false, false, 0.1);   // wrap_u, wrap_v, flip, thickness
""",

"paste": """\
add::Mesh ball = add::make([] { add::sphere({0, 0, 0}, 1, 10, "red"); });
add::paste(ball);                      // same as add::mesh(ball)
""",

"pipe": """\
add::pipe({0, 0, 0}, {0, 3, 0}, 0.6, 0.4, 32, "silver");
""",

"pixels": """\
add::pixels({"..r..",
             ".rrr.",
             "rrrrr",
             "..g..",
             "..g.."}, 0.5, {0, 0, 0}, add::PALETTE(), 1, "red");   // origin, colors, depth, color
""",

"place": """\
add::Mesh ball = add::make([] { add::sphere({7, 7, 7}, 1, 10, "red"); });
add::mesh(add::place(ball, {0, 1, 0}));   // now centred at (0, 1, 0)
""",

"points_on_circle": """\
for (const add::Point& p : add::points_on_circle({0, 0, 0}, 3, 12))
    add::box(p, 0.5, "gold");
""",

"points_on_curve": """\
auto wave = [](double t) { return add::Point{t, add::sin(t), 0}; };
for (const add::Point& p : add::points_on_curve(wave, 0, 2 * add::pi, 20))
    add::sphere(p, 0.15, 6, "red");
""",

"points_on_helix": """\
for (const add::Point& p : add::points_on_helix({0, 0, 0}, 2, 1.5, 3, 60))
    add::sphere(p, 0.2, 6, "sky");
""",

"points_on_line": """\
for (const add::Point& p : add::points_on_line({0, 0, 0}, {8, 0, 0}, 5))
    add::sphere(p, 0.3, 6, "red");
""",

"points_on_spiral": """\
for (const add::Point& p : add::points_on_spiral({0, 0, 0}, 0.5, 4, 3, 80))
    add::box(p, 0.25, "purple");
""",

"polygon": """\
add::polygon({{0, 0, 0}, {2, 0, 0}, {2, 2, 0}, {1, 3, 0}, {0, 2, 0}}, "gold");
""",

"polyhedron": """\
std::vector<std::string> names = {"tetrahedron", "cube", "octahedron",
                                  "dodecahedron", "icosahedron"};
for (int i = 0; i < 5; ++i)
    add::polyhedron(names[i], {i * 2.5, 0, 0}, 1, add::hsv(i / 5.0));
""",

"polyhedron_faces": """\
add::Points P = add::polyhedron_points("cube", {0, 0, 0}, 1);
for (const add::Face& f : add::polyhedron_faces("cube")) {
    add::Points corners;
    for (int i : f) corners.push_back(P[i]);
    add::polygon(corners, "sky");                   // the cube, face by face
}
""",

"polyhedron_points": """\
for (const add::Point& p : add::polyhedron_points("icosahedron", {0, 0, 0}, 2))
    add::cone({0, 0, 0}, p, 0.3, 12, "red");        // twelve spikes
""",

"polyline": """\
add::polyline({{0, 0, 0}, {2, 1, 0}, {3, 3, 1}, {1, 4, 0}}, 0.15, 12, "sky",
              false, 2);   // closed, smooth
""",

"pop": """\
add::push();
add::cylinder({0, 0, 0}, {0, 2, 0}, 0.5, 24, "gold");
add::Mesh part = add::pop();
add::mesh(add::move(part, {3, 0, 0}));
""",

"prism": """\
add::prism(add::profile_star(5, 1.0, 0.5), 2, "purple");
add::prism({{0, 0}, {1, 0}, {0.5, 1}}, 3, "gold", {3, 0, 0});   // center
""",

"profile_circle": """\
add::extrude(add::profile_circle(1, 24), {0, 3, 0}, "gold");
""",

"profile_ellipse": """\
add::extrude(add::profile_ellipse(1.5, 0.7, 32), {0, 2, 0}, "sky");
""",

"profile_gear": """\
add::prism(add::profile_gear(12, 1.0, 0.25), 0.4, "silver");
""",

"profile_polygon": """\
add::prism(add::profile_polygon(6, 1), 2, "gold");
""",

"profile_rect": """\
add::extrude(add::profile_rect(2, 1, 0.3), {0, 3, 0}, "purple");
""",

"profile_star": """\
add::prism(add::profile_star(5, 1.0, 0.45), 0.5, "gold");
""",

"push": """\
add::box({0, 0, 0}, 1, "red");           // already in the scene
add::push();
add::sphere({0, 0, 0}, 1, 10, "blue");
add::Mesh ball = add::pop();             // only the sphere
// len(add.faces) of add.py: the faces of the scene, add::scene().F
std::cout << ball.polygons() << " " << add::scene().F.size() << "\\n";   // 1280 6
""",

"pyramid": """\
add::pyramid({0, 0, 0}, 3, 2, "gold");
""",

"quad": """\
add::quad({0, 0, 0}, {2, 0, 0}, {2, 2, 0}, {0, 2, 0}, "sky");
""",

"quadsphere": """\
add::quadsphere({0, 0, 0}, 1.5, 12, "sky");       // 864 quads
""",

"random_color": """\
add::seed(1);
for (int i = 0; i < 5; ++i)
    add::box({double(i), 0, 0}, 0.9, add::random_color());
std::cout << std::boolalpha << (add::random_color(7) == add::random_color(7)) << "\\n";   // true
""",

"random_points": """\
auto height = [](double x, double z) { return 0.3 * add::sin(x) * add::cos(z); };
add::Points pts = add::random_points(30, {-5, 0, -5}, {5, 0, 5}, 1, height);   // seed, height
for (const add::Point& p : pts)
    add::sphere(p, 0.2, 5, "red");
""",

"rectangle3D": """\
add::rectangle3D({0, 0, 0}, {4, 1, 2}, {0, 128, 255});
""",

"refine": """\
add::Mesh cube = add::make([] { add::box({0, 0, 0}, 2, "gold"); });
std::cout << add::refine(cube, 2).polygons() << "\\n";   // 96 quads, same shape
add::Mesh tet = add::make([] { add::tetrahedron({0, 0, 0}, 2, "red"); });
add::mesh(add::refine(tet, 3));                         // 256 triangles
""",

"reflect": """\
add::Mesh wing = add::make([] { add::cuboid({2, 0, 0}, {3, 0.2, 1}, "gold"); });
add::mesh(add::reflect(wing, {0, 0, 0}, {1, 0, 0}));
""",

"remap": """\
std::cout << add::remap(5, 0, 10, -1, 1) << "\\n";   // 0
""",

"repeat": """\
add::Mesh brick = add::make([] { add::box({0, 0, 0}, 0.9, "red"); });
add::Mesh spiral = add::repeat(brick, 40, [](const add::Mesh& X, int i) {
    return add::move(add::rotateY(X, i * 0.3), {3, i * 0.2, 0});
});
add::mesh(spiral);
""",

"revolve": """\
auto vase = [](double t) {
    return add::Point2{1 + 0.4 * add::sin(3 * t), t};
};

add::revolve(vase, {0, 0, 0}, {0, 1, 0}, 0, 4, 60, 40, "teal");
add::revolve(vase, {4, 0, 0}, {4, 1, 0}, 0, 4, 60, 40,
             [](double t, double a) { return add::hsv(t / 4.0); });   // color
""",

"rgb": """\
std::cout << add::rgb("sky") << " " << add::rgb("#ff8000") << " "
          << add::rgb({1.0, 0.5, 0.0}) << "\\n";
std::cout << add::rgb({0, 0, 255, 0.5}) << "\\n";       // with an opacity
""",

"ribbon": """\
add::ribbon([](double t) { return add::Point{add::cos(t) * 2, t * 0.3, add::sin(t) * 2}; },
            0, 4 * add::pi, 120, 0.5, "purple",
            false, [](double t) { return t / 2; });     // closed, twist
""",

"ring": """\
add::ring({0, 0, 0}, {0, 1, 0}, 2, 1.5, 48, "silver");
""",

"roof": """\
add::cuboid({0, 1, 0}, {4, 2, 3}, "brown");
add::roof({0, 2, 0}, {4, 3}, 1.2, {120, 40, 30}, 0.3);   // overhang
""",

"rotate": """\
add::Mesh bar = add::make([] { add::cuboid({0, 0, 0}, {4, 1, 1}, "gold"); });
add::mesh(add::rotate(bar, {1, 1, 0}, add::pi / 3));
""",

"rotateX": """\
add::Mesh bar = add::make([] { add::cuboid({0, 0, 0}, {1, 4, 1}, "gold"); });
add::mesh(add::rotateX(bar, add::pi / 4));
""",

"rotateY": """\
add::Mesh bar = add::make([] { add::cuboid({3, 0, 0}, {1, 1, 4}, "gold"); });
for (int i = 0; i < 6; ++i)
    add::mesh(add::rotateY(bar, i * add::pi / 3));
""",

"rotateZ": """\
add::Mesh bar = add::make([] { add::cuboid({0, 0, 0}, {4, 1, 1}, "gold"); });
add::mesh(add::rotateZ(bar, add::pi / 6, {-2, 0, 0}));
""",

"rotate_point": """\
add::Point pin = add::rotate_point({1, 0, 0}, {0, 0, 1}, add::pi / 2);
for (int i = 0; i < 3; ++i) std::cout << std::round(pin[i] * 1e6) / 1e6 << " ";   // 0 1 0
std::cout << "\\n";
""",

"rounded_box": """\
add::rounded_box({0, 0, 0}, {3, 2, 1}, 0.3, 8, "sky");
""",

"save": """\
add::box({0, 0, 0}, 2, "red");
add::sphere({3, 0, 0}, 1, 10, "blue");
add::save("model.off");                  // and the scene is cleared
add::Mesh M = add::make([] { add::sphere({0, 0, 0}, 1, 10, "red"); });
add::save("model.obj", M);               // .obj + .mtl, the scene stays
add::save("model.stl", M);
""",

"scale": """\
add::Mesh ball = add::make([] { add::sphere({0, 0, 0}, 1, 10, "red"); });
add::mesh(add::scale(ball, 2));
""",

"scatter": """\
add::Mesh tree = add::make([] { add::tree({0, 0, 0}, 2); });
add::Points pts = add::random_points(12, {-6, 0, -6}, {6, 0, 6}, 2);   // seed
add::mesh(add::scatter(tree, pts, 1, true, {0.6, 1.4}));               // seed, spin, scale
""",

"scene": """\
add::box({0, 0, 0}, 1, "red");
std::cout << add::scene() << "\\n";    // <Mesh 8 vertices, 6 faces>
""",

"set_vertex": """\
add::Mesh block = add::make([] { add::box({0, 0, 0}, 2, "gold"); });
int i = add::nearest_vertex(block, {1, 1, 1});
block = add::set_vertex(block, i, {2.5, 2.5, std::nullopt});   // pull a corner, keep z
add::mesh(add::smooth(block, 6));
""",

"set_vertices": """\
add::Mesh block = add::make([] { add::box({0, 0, 0}, 2, "gold"); });
std::vector<int> top;
for (int i = 0; i < (int)block.V.size(); ++i)
    if (block.V[i][1] > 0) top.push_back(i);
std::map<int, add::PartialPoint> changes;
for (int i : top) changes[i] = {std::nullopt, 3, std::nullopt};
block = add::set_vertices(block, changes);   // a taller box
add::mesh(block);
""",

"shade": """\
add::Color dark = add::shade("gold", 0.6);
add::box({0, 0, 0}, 1, "gold");
add::box({1.5, 0, 0}, 1, dark);
""",

"size": """\
add::Mesh M = add::make([] { add::cuboid({0, 0, 0}, {4, 1, 2}); });
std::cout << add::size(M) << "\\n";    // [4.0, 1.0, 2.0]
""",

"smooth": """\
add::dodecahedron({0, 0, 0}, 2, "gold");
add::mesh(add::smooth(add::layer(), 5));            // 12 * 61 cells, 5 per edge
add::Mesh block = add::make([] { add::box({5, 0, 0}, 2, "sky"); });
block = add::set_vertex(block, 7, {7, 3, 2});       // pull a corner out ...
add::mesh(add::smooth(block, 8));                   // ... and round it
""",

"solid_of_revolution": """\
add::solid_of_revolution([](double t) { return add::Point2{1 + 0.3 * add::sin(3 * t), t}; },
                         {0, 0, 0}, {0, 1, 0}, 0, 4, 40, 32, "teal");
""",

"solidify": """\
add::Mesh sheet = add::make([] {
    add::parametric([](double u, double v) { return add::Point{u, add::sin(u) * add::cos(v), v}; },
                    -3, 3, 30, -3, 3, 30, "sky");
});
add::mesh(add::solidify(sheet, 0.2));
""",

"sphere": """\
add::sphere({0, 0, 0}, 1.5, 20, "sky");             // 5120 triangles
add::sphere({4, 0, 0}, 1.5, 5, "gold");             // 320
add::sphere({8, 0, 0}, 1.5, 10, "red", 2);          // subdivisions (k is then not used)
""",

"spherify": """\
add::Mesh octa = add::make([] { add::octahedron({0, 0, 0}, 2, "sky"); });
add::mesh(add::spherify(add::refine(octa, 3)));   // a geodesic dome, 512 triangles
add::Mesh cube = add::make([] { add::box({5, 0, 0}, 2, "gold"); });
add::mesh(add::spherify(add::refine(cube, 2), std::nullopt, std::nullopt, 0.5));   // amount: a cushion
""",

"spin3D": """\
add::spin3D({0, 0, 0}, {0, 1, 0}, [](double t) { return add::Point2{1 + 0.3 * add::sin(4 * t), t}; },
            0, 3, 40, 32, {200, 120, 60});
""",

"stairs": """\
add::stairs({0, 0, 0}, 8, 2, 0.3, 0.5, "grey");
""",

"stats": """\
add::Mesh M = add::make([] { add::torus({0, 0, 0}, 3, 1); });
add::Stats s = add::stats(M);
std::cout << s.faces << " " << std::boolalpha << s.closed << " "
          << std::round(s.volume * 100) / 100 << " " << s.obj_bytes << "\\n";
""",

"stream": """\
std::unique_ptr<add::Stream> out = add::stream("big.obj");
for (int i = 0; i < 20; ++i) {
    add::bricks({0, 0, i * 2.0}, 10, 2, {1, 0.5, 0.5}, "brown",
                {1, 0, 0}, 0.05, i);       // direction, gap, seed
    out->add();                            // written now, scene cleared
}
out->add(add::make([] { add::tree({12, 0, 0}, 5); }));
out->close();                              // writes big.mtl too
std::cout << out->faces << " faces, " << out->bytes << " bytes, "
          << out->materials.size() << " materials\\n";
""",

"stretch": """\
add::Mesh ball = add::make([] { add::sphere({0, 0, 0}, 1, 10, "red"); });
add::mesh(add::stretch(ball, {3, 1, 0.5}));   // an ellipsoid
""",

"subdivide": """\
add::box({0, 0, 0}, 2, "red");
add::mesh(add::subdivide(add::layer(), 2));
""",

"subtract": """\
add::Mesh a = add::make([] { add::box({0, 0, 0}, 2, "red"); });
add::Mesh b = add::make([] { add::box({1, 1, 1}, 2, "blue"); });
add::mesh(add::subtract(a, b));
""",

"surface": """\
add::surface("klein_bottle", {0, 0, 0}, 4, 100, "teal");
add::surface("apple", {6, 0, 0}, 3, std::nullopt,            // grid: the surface's own
             [](double u, double v) { return add::hsv(u / 6.3); });
add::surface("pillow", {-6, 0, 0}, 3, std::nullopt, add::DEFAULT_COLOR,
             0.1, false, {{"a", 0.9}});                      // thickness, double_sided, a = 0.9
""",

"surface_function": """\
add::SurfaceFn owl = add::surface_function("owl");
add::parametric(owl, 0, 4 * add::pi, 120, 0.001, 1, 30,
                [](double u, double v) { return add::hsv(v); },
                false, false, false, 0.03);   // wrap_u, wrap_v, flip, thickness
""",

"surface_names": """\
for (const std::string& name : add::surface_names()) std::cout << name << "\\n";
""",

"sweep": """\
auto path = [](double t) { return add::Point{add::cos(t) * 3, t * 0.5, add::sin(t) * 3}; };
add::sweep(add::profile_star(5, 0.5, 0.25), path, 0, 4 * add::pi, 120, "gold",
           false, add::Scalar(), [](double t) { return t; });   // closed, scale, twist
""",

"symmetric_difference": """\
add::Mesh a = add::make([] { add::box({0, 0, 0}, 2, "red"); });
add::Mesh b = add::make([] { add::box({1, 1, 1}, 2, "blue"); });
add::mesh(add::symmetric_difference(a, b));
""",

"taper": """\
add::Mesh bar = add::make([] { add::cuboid({0, 2, 0}, {1, 4, 1}, "gold"); });
add::mesh(add::taper(bar, -0.2));         // 20 % thinner per unit of height
""",

"tetrahedron": """\
add::tetrahedron({0, 0, 0}, 1.5, "red");
""",

"text": """\
add::text("LABAS 2026", {0, 0, 0}, 1.0, std::nullopt, "navy");   // std::nullopt: the default thickness
add::text("ĄČĘ\\nĖĮŠ", {0, 3, 0}, 0.8, std::nullopt, "red", {1, 0, 0}, {0, 1, 0}, "center");   // u, v, align
add::text("FLAT", {0, -2, 0}, 1.0, std::nullopt, "teal", {1, 0, 0}, {0, 0, -1});              // u, v
""",

"text_width": """\
double w = add::text_width("LABAS", 1.0);
add::text("LABAS", {-w / 2, 0, 0}, 1.0, std::nullopt, "navy");   // centred by hand
""",

"texture": """\
std::vector<std::vector<add::Color>> rows(64, std::vector<add::Color>(64));
for (int y = 0; y < 64; ++y)
    for (int x = 0; x < 64; ++x)
        rows[y][x] = (x / 8 + y / 8) % 2 ? "white" : "black";
add::write_png("check.png", rows);
add::Mesh wall = add::make([] { add::cuboid({0, 0, 0}, {4, 2, 0.3}); });
add::mesh(add::texture(wall, "check.png", "box", 1.0));    // scale
add::Mesh ball = add::make([] { add::sphere({0, 3, 0}, 1, 10); });
add::mesh(add::texture(ball, "check.png", "sphere", 4));   // scale
add::save("textured.obj");                                 // .obj + .mtl (map_Kd check.png)
""",

"torus": """\
add::torus({0, 0, 0}, 3, 0.8, 48, 24, "gold");
add::torus({0, 0, 0}, 3, 0.3, 48, 12, "silver", {1, 0, 0});   // axis
""",

"trace": """\
auto field = [](const add::Point& p) { return add::Point{-p[2], 0.3, p[0]}; };
add::trace(field, {1, 0, 0}, 0.05, 200, 0.08, 8, "red");
""",

"transform": """\
add::Mesh M = add::make([] { add::box({0, 0, 0}, 1, "red"); });
std::vector<std::vector<double>> shear = {{1, 0.5, 0}, {0, 1, 0}, {0, 0, 1}};
add::mesh(add::transform(M, shear));
""",

"translate": """\
add::Mesh ball = add::make([] { add::sphere({0, 0, 0}, 1, 10, "red"); });
add::mesh(add::translate(ball, {3, 0, 0}));
""",

"transparent": """\
add::Color glass = add::transparent("sky", 0.35);
add::cuboid({0, 1, 0}, {2, 1.5, 0.05}, glass);     // a window pane
add::save("window.obj");                           // opacity goes into the .mtl
""",

"tree": """\
add::tree({0, 0, 0}, 4);
add::tree({3, 0, 0}, 3, "brown", "green", "pine");   // kind
""",

"triangle": """\
add::triangle({0, 0, 0}, {2, 0, 0}, {1, 2, 0}, "red");
""",

"triangulate": """\
add::Mesh M = add::make([] { add::box({0, 0, 0}, 2, "red"); });
std::cout << add::triangulate(M).polygons() << "\\n";   // 12
""",

"truncate": """\
add::Mesh ico = add::make([] { add::icosahedron({0, 0, 0}, 3, "white"); });
add::Mesh ball = add::truncate(ico, 1 / 3.0, "black");      // 20 hexagons + 12 pentagons
add::mesh(ball);
add::Mesh cube = add::make([] { add::box({7, 0, 0}, 3, "gold"); });
add::mesh(add::truncate(cube, 0.5, "red"));                 // a cuboctahedron
""",

"tube": """\
add::tube({0, 0, 0}, {0, 3, 0}, 0.5, 24, "gold");
""",

"twist": """\
add::Mesh bar = add::make([] { add::cuboid({0, 2, 0}, {1, 4, 1}, "gold"); });
bar = add::refine(bar, 3);
add::mesh(add::twist(bar, 0.6));
""",

"two_sided": """\
add::Mesh sheet = add::make([] { add::grid({0, 0, 0}, {4, 4}, 10, 10, "sky"); });
add::mesh(add::two_sided(sheet));
""",

"typeset": """\
std::filesystem::create_directory("glyphs");
for (std::string ch : {"A", "D", "D"}) {
    add::text(ch, {0, 0, 0}, 1, std::nullopt, "navy");
    add::save("glyphs/" + ch + ".off");
}
std::map<std::string, add::Mesh> font = add::load_font("glyphs");
add::mesh(add::typeset("ADD", font, {0, 0, 0}, 2, 1.0, "gold"));   // spacing, color
""",

"union": """\
add::Mesh a = add::make([] { add::box({0, 0, 0}, 2, "red"); });
add::Mesh b = add::make([] { add::sphere({1, 1, 1}, 1.2, 10, "blue"); });
add::mesh(add::union_(a, b));   // union_: union is a C++ keyword
""",

"uvsphere": """\
add::uvsphere({0, 0, 0}, 1.5, 32, 16, "sky");
""",

"valence": """\
for (std::string name : {"cube", "octahedron", "icosahedron"}) {
    add::Mesh M = add::make([&] { add::polyhedron(name); });
    std::cout << name << " " << add::valence(M, 0) << "\\n";
}
""",

"vertex": """\
add::Mesh M = add::make([] { add::box({0, 0, 0}, 2); });
std::cout << add::vertex(M, 7) << "\\n";
""",

"vertex_faces": """\
add::Mesh M = add::make([] { add::box({0, 0, 0}, 2); });
for (int f : add::vertex_faces(M, 0)) std::cout << f << " ";   // three faces meet at a corner
std::cout << "\\n";
""",

"vertex_normal": """\
add::Mesh M = add::make([] { add::sphere({0, 0, 0}, 1, 10); });
std::cout << add::vertex_normal(M, 0) << "\\n";
for (int i = 0; i < (int)M.V.size(); i += 40) {   // a few spikes along the normals
    add::Point n = add::vertex_normal(M, i);
    add::cone(M.V[i], M.V[i] + 0.5 * n, 0.05, 6, "red");
}
""",

"vertices": """\
add::box({0, 0, 0}, 1, "red");
// add.vertices, the add.py 1.2 list of strings, is add::scene().V in C++
std::cout << add::scene().V.size() << " " << add::scene().V[0] << "\\n";
""",

"volume": """\
add::Mesh M = add::make([] { add::sphere({0, 0, 0}, 1, 20); });
std::printf("%.3f %.3f\\n", add::volume(M), 4 / 3.0 * add::pi);
""",

"voxels": """\
std::vector<add::Cell> blocks;
for (int x = 0; x < 6; ++x)
    for (int y = 0; y < 3; ++y)
        for (int z = 0; z < 6; ++z)
            if ((x + y + z) % 3) blocks.push_back({x, y, z});
add::voxels(blocks, 0.5, {0, 0, 0}, "sky");   // origin
""",

"weld": """\
add::box({0, 0, 0}, 2, "red");
add::box({2, 0, 0}, 2, "red");
add::mesh(add::weld(add::layer()));
""",

"wheel": """\
add::wheel({0, 0, 0}, 1.5, 0.5, "black", {0, 0, 1}, 32, 8);   // axis, k, spokes
""",

"wireframe": """\
add::Mesh cube = add::make([] { add::box({0, 0, 0}, 2); });
add::wireframe(cube, 0.05, 8, "gold");
""",

"write": """\
add::write("HELLO", {0, 0, 0}, 1.0, std::nullopt, "navy");   // std::nullopt: the default thickness
""",

"write_png": """\
std::vector<std::vector<add::Color>> rows(64, std::vector<add::Color>(64));
for (int y = 0; y < 64; ++y)
    for (int x = 0; x < 64; ++x)
        rows[y][x] = add::hsv(x / 64.0, 1, 1 - y / 128.0);
add::write_png("rainbow.png", rows);
add::mesh(add::texture(add::make([] { add::box({0, 0, 0}, 2); }), "rainbow.png", "box", 2));   // scale
""",

"zoom": """\
add::Mesh ball = add::make([] { add::sphere({0, 0, 0}, 1, 10, "red"); });
add::mesh(add::zoom(ball, 2.5));
""",

}

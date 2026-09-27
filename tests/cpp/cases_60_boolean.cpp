// Parity cases for _cpp/60_boolean.hpp: union_, difference, intersect,
// symmetric_difference and their aliases, cut and inside -- and the machinery
// under them: Poly, split, BoxGrid (whose set order decides which plane cuts
// first), RayIndex, Solid, split_against, keep_pieces, loops (see
// cases_60_boolean.py).
#include "parity.hpp"

using add::Color;
using add::Face;
using add::Mesh;
using add::Point;
using add::Points;
using add::detail::fmt;

static const Color GREY = add::DEFAULT_COLOR;

static std::string ints(const std::vector<int>& xs) {
    std::string s;
    for (size_t i = 0; i < xs.size(); ++i) s += (i ? " " : "") + std::to_string(xs[i]);
    return s;
}

static std::string bits(const std::vector<bool>& xs) {
    std::string s;
    for (bool x : xs) s += x ? "1" : "0";
    return s;
}

//: true / false / nothing as a word (Python's True / False / None).
static std::string maybe(std::optional<bool> x) { return !x ? "None" : (*x ? "True" : "False"); }

//: Every vertex, face and colour of a mesh, exactly.
static void dump(const Mesh& M) {
    record(M.V.size());
    for (const Point& p : M.V) record(p);
    record(M.F.size());
    for (size_t i = 0; i < M.F.size() && i < M.C.size(); ++i) {
        record(ints(M.F[i]));
        record(M.C[i]);
    }
}

//: The mesh to <case>_<tag>.off, and exactly into <case>.txt.
static void keep(const Mesh& M, const std::string& tag) {
    record(tag);
    dump(M);
    save_mesh(M, tag);
}

static Mesh make_box(const Point& c, double e, const Color& color = GREY) {
    return add::make([&] { add::box(c, e, color); });
}
static Mesh make_cuboid(const Point& c, const Point& s, const Color& color = GREY) {
    return add::make([&] { add::cuboid(c, s, color); });
}
static Mesh make_sphere(const Point& c, double r, int k = 10, const Color& color = GREY) {
    return add::make([&] { add::sphere(c, r, k, color); });
}
static Mesh make_cylinder(const Point& a, const Point& b, double r, int k = 24, const Color& color = GREY) {
    return add::make([&] { add::cylinder(a, b, r, k, color); });
}
static Mesh make_cone(const Point& a, const Point& b, double r, int k = 24, const Color& color = GREY) {
    return add::make([&] { add::cone(a, b, r, k, color); });
}
static Mesh make_torus(const Point& c, double R, double r, int nu = 48, int nv = 24, const Color& color = GREY,
                  const Point& axis = {0, 1, 0}) {
    return add::make([&] { add::torus(c, R, r, nu, nv, color, axis); });
}
static Mesh make_poly(const std::string& name, const Point& c, double r, const Color& color = GREY) {
    return add::make([&] { add::polyhedron(name, c, r, color); });
}

static void all_three(const Mesh& A, const Mesh& B, const std::string& tag = "") {
    keep(add::union_(A, B), tag + "union");
    keep(add::difference(A, B), tag + "diff_ab");
    keep(add::difference(B, A), tag + "diff_ba");
    keep(add::intersect(A, B), tag + "inter");
}

// ---------------------------------------------------------------------------
//  Boxes
// ---------------------------------------------------------------------------

CASE(b_box_overlap) {
    Mesh A = make_cuboid({0, 0, 0}, {2, 2, 2}, "red");
    Mesh B = make_cuboid({1, 0.5, 0.25}, {2, 2, 2}, "blue");
    all_three(A, B);
    Mesh C = make_box({0.3, -0.2, 0.1}, 1.5, "gold");
    Mesh D = make_box({-0.4, 0.35, 0.6}, 1.1, "teal");
    all_three(C, D, "b_");
}

CASE(b_box_touching) {
    Mesh A = make_box({0, 0, 0}, 2, "red");
    all_three(A, make_box({2, 0, 0}, 2, "blue"));                // a whole face shared
    all_three(A, make_box({2, 0.5, 0.5}, 2, "green"), "part_");  // part of a face shared
    all_three(A, make_box({2, 2, 0}, 2, "navy"), "edge_");       // only an edge
    all_three(A, make_box({2, 2, 2}, 2, "pink"), "corner_");     // only a corner
}

CASE(b_coplanar) {
    Mesh A = make_cuboid({0, 0, 0}, {2, 1, 2}, "red");
    Mesh B = make_cuboid({1, 0, 0.5}, {2, 1, 1}, "blue");  // top and bottom flush with A's
    all_three(A, B);
    all_three(A, make_cuboid({0.5, 0.25, 0}, {1, 0.5, 3}, "green"), "top_");  // only the top flush
    all_three(A, A, "same_");                                                 // the very same box
    all_three(A, add::mirror(A, {0, 0, 0}, {1, 0, 0}), "mirror_");            // mirrored: its corners in another order
}

CASE(b_nested) {
    Mesh big = make_box({0, 0, 0}, 3, "red");
    Mesh small = make_cuboid({0.2, -0.1, 0.3}, {1, 1.2, 0.8}, "blue");
    all_three(big, small);
    all_three(big, make_cuboid({0, 0, 0}, {3, 1, 1}, "green"), "flush_");  // inside, touching two faces
}

CASE(b_disjoint) {
    Mesh A = make_box({0, 0, 0}, 1, "red");
    Mesh B = make_box({3, 0.5, 0}, 1, "blue");
    all_three(A, B);
    keep(add::union_({A, B, make_box({0, 3, 0}, 1, "green")}), "three");
}

// ---------------------------------------------------------------------------
//  Several solids, curved solids
// ---------------------------------------------------------------------------

CASE(b_union_many) {
    std::vector<Mesh> parts = {make_box({0, 0, 0}, 1, "red"), make_box({0.7, 0.3, 0.2}, 1, "green"),
                               make_box({1.4, 0.6, 0.4}, 1, "blue"), make_sphere({2.1, 0.9, 0.6}, 0.6, 6, "gold")};
    keep(add::union_(parts), "chain");
    keep(add::union_(std::vector<Mesh>(parts.begin(), parts.begin() + 1)), "one");
    std::vector<Mesh> balls = {make_sphere({0, 0, 0}, 1, 6, "red"), make_sphere({0.9, 0.2, 0.1}, 0.8, 6, "white"),
                               make_sphere({0.4, 0.8, -0.3}, 0.7, 6, "sky")};
    keep(add::union_(balls), "balls");
    keep(add::union_({balls[0], make_box({5, 0, 0}, 1), balls[1]}), "gap");
}

//: Touching unit cubes, as a student stacks them: shared faces, edges and corners.
CASE(b_voxels) {
    Points cells = {{0, 0, 0}, {1, 0, 0}, {2, 0, 0}, {1, 1, 0}, {1, 1, 1}, {0, 0, 1}, {2, 1, 1}};
    std::vector<Mesh> cubes;
    for (size_t i = 0; i < cells.size(); ++i) cubes.push_back(make_box(cells[i], 1, add::hsv(i / 7.0)));
    keep(add::union_(cubes), "union");
    std::vector<Mesh> every_other;
    for (size_t i = 0; i < cubes.size(); i += 2) every_other.push_back(cubes[i]);
    keep(add::difference(make_cuboid({1, 0.5, 0.5}, {3, 2, 2}, "white"), every_other), "carved");
    Mesh first = add::union_(std::vector<Mesh>(cubes.begin(), cubes.begin() + 4));
    keep(add::intersect(first, make_cuboid({1, 0.25, 0}, {2, 1, 1}, "red")), "trimmed");
}

//: A solid and a turned copy of itself: faces that are flush up to rounding.
CASE(b_turned) {
    Mesh A = make_cuboid({0.1, 0, -0.05}, {1.2, 0.8, 1.6}, "red");
    for (int q : {1, 2, 4}) {
        Mesh B = add::rotate(A, {0, 1, 0}, q * add::pi / 4);
        keep(add::union_(A, B), fmt("u%d", q));
        keep(add::difference(A, B), fmt("d%d", q));
        keep(add::intersect(A, B), fmt("i%d", q));
    }
    Mesh S = add::make([] { add::prism(add::profile_star(5, 0.8, 0.4), 1, "teal"); });
    for (int k : {1, 2}) {
        Mesh T = add::rotate(S, {0, 1, 0}, k * add::pi / 5);
        keep(add::union_(S, T), fmt("star_u%d", k));
        keep(add::difference(S, T), fmt("star_d%d", k));
    }
}

CASE(b_intersect_many) {
    Mesh a = make_cuboid({0, 0, 0}, {3, 1, 1}, "red");
    Mesh b = make_cuboid({0, 0, 0}, {1, 3, 1}, "green");
    Mesh c = make_cuboid({0, 0, 0}, {1, 1, 3}, "blue");
    keep(add::intersect({a, b, c}), "cross");
    keep(add::intersect({make_sphere({0, 0, 0}, 1, 6, "red"), make_box({0.5, 0.5, 0.5}, 1.2, "blue"),
                         make_cylinder({0, -2, 0}, {0, 2, 0}, 0.6, 12, "green")}),
         "round");
    keep(add::intersect({a, make_box({5, 0, 0}, 1), c}), "gap");
    keep(add::intersect(std::vector<Mesh>{a}), "one");
}

CASE(b_symmetric) {
    Mesh A = make_box({0, 0, 0}, 2, "red"), B = make_box({1, 0.5, 0.25}, 2, "blue");
    keep(add::symmetric_difference(A, B), "boxes");
    Mesh S = make_sphere({0, 0, 0}, 1, 6, "white"), C = make_box({0.8, 0, 0}, 1.2, "black");
    keep(add::symmetric_difference(S, C), "ball");
    Mesh P = make_box({0, 0, 0}, 1), Q = make_box({3, 0, 0}, 1);
    keep(add::symmetric_difference(P, Q), "apart");
}

CASE(b_drill) {
    add::cuboid({0, -1.2, 0}, {4, 0.6, 4}, "brown");
    Mesh plate = add::layer();
    add::cylinder({0, -2, 0}, {0, 0, 0}, 0.9, 32, "brown");
    Mesh drill = add::layer();
    add::mesh(add::difference(plate, drill));
    save_case();
    add::cuboid({0, 0, 0}, {4, 1, 4}, "brown");
    plate = add::layer();
    add::cylinder({0, -1, 0}, {0, 1, 0}, 0.6, 32, "brown");
    drill = add::layer();
    keep(add::difference(plate, drill), "doc");
    keep(add::difference(plate, drill, "black"), "painted");
}

CASE(b_curved) {
    Mesh B = make_box({0, 0, 0}, 1.5, "red");
    Mesh S = make_sphere({0.3, 0.2, 0.1}, 1, 6, "white");
    all_three(B, S);
    Mesh C = make_cylinder({-1, -1, -0.5}, {1, 1, 0.5}, 0.4, 16, "blue");
    all_three(make_sphere({0, 0, 0}, 1, 6, "gold"), C, "tilt_");
    Mesh T = make_torus({0, 0, 0}, 1.0, 0.35, 16, 8, "teal");
    keep(add::difference(T, make_box({1, 0, 0}, 0.8, "red")), "torus_bite");
    keep(add::intersect(T, make_cuboid({0, 0, 0}, {3, 0.3, 3}, "red")), "torus_slab");
    Mesh K = make_cone({0, -1, 0}, {0, 1, 0}, 1, 12, "green");
    Mesh H = make_cylinder({-2, 0, 0}, {2, 0, 0}, 0.3, 12);
    keep(add::difference(K, H), "cone_drill");
    Mesh P = make_cylinder({0, -1, 0}, {0, 1, 0}, 0.5, 12, "red");
    Mesh Q = make_cylinder({-1, 0, 0}, {1, 0, 0}, 0.5, 12, "blue");
    keep(add::union_(P, Q), "pipes");
}

CASE(b_paint) {
    Mesh plate = make_cuboid({0, 0, 0}, {4, 1, 4}, "brown");
    std::vector<Mesh> drills;
    for (double x : {-1.2, 0.0, 1.2}) drills.push_back(make_cylinder({x, -1, 0}, {x, 1, 0}, 0.4, 12, "red"));
    keep(add::difference(plate, drills), "own");
    keep(add::difference(plate, drills, "black"), "black");
    keep(add::difference(plate, drills, add::transparent("sky", 0.4)), "clear");
    keep(add::difference(plate, {drills[0], drills[2]}, Color(10, 20, 30)), "two");
    keep(add::difference(plate, std::vector<Mesh>{}, "black"), "none");
}

CASE(b_colors) {
    Mesh T = add::texture(make_box({0, 0, 0}, 1, "white"), "wood.png");
    Mesh G = add::opacity(make_sphere({0.5, 0.3, 0.2}, 0.6, 6, "sky"), 0.5);
    keep(add::union_(T, G), "union");
    keep(add::difference(T, G), "diff");
    keep(add::difference(G, T, add::transparent("red", 0.25)), "diff_painted");
    keep(add::intersect(G, T), "inter");
    add::obj(parity::current() + "_apart.obj", add::union_(T, add::move(G, {5, 0, 0})));   // (merged: the texture kept)
    add::obj(parity::current() + "_first.obj", add::union_(Mesh(), T));
    try {
        add::detail::csg(T, G, "xor");
    } catch (const std::invalid_argument&) {
        record("raised");
    }
}

CASE(b_aliases) {
    Mesh a = make_box({0, 0, 0}, 1, "red");
    Mesh b = make_box({0.5, 0.25, 0}, 1, "blue");
    Mesh c = make_box({-0.3, 0.4, 0.2}, 1, "green");
    keep(add::add_solids(a, b), "add2");
    keep(add::add_solids({a, b, c}), "add3");
    keep(add::subtract(a, b), "sub2");
    keep(add::subtract(a, {b, c}), "sub3");
    keep(add::common(a, b), "common2");
    keep(add::common({a, b, c}), "common3");
}

CASE(b_empty) {
    Mesh a = make_box({0, 0, 0}, 1, "red");
    Mesh E;
    keep(add::union_(std::vector<Mesh>{}), "u_none");
    keep(add::union_(std::vector<Mesh>{E}), "u_empty");
    keep(add::union_({E, a}), "u_ea");
    keep(add::union_({a, E}), "u_ae");
    keep(add::difference(E, a), "d_ea");
    keep(add::difference(a, E), "d_ae");
    keep(add::intersect(std::vector<Mesh>{}), "i_none");
    keep(add::intersect({E, a}), "i_ea");
    keep(add::intersect({a, E}), "i_ae");
    keep(add::difference(a, a), "d_aa");
    keep(add::difference(a, make_box({0, 0, 0}, 2)), "d_swallowed");
    keep(add::intersect(a, make_box({0.25, 0.25, 0.25}, 0.5, "blue")), "i_inner");
    Mesh V;                                                   // faces without area, and one of two corners
    for (const Point& p : Points{{0, 0, 0}, {1, 0, 0}, {2, 0, 0}, {0.5, 0.5, 0.5}}) V.add_vertex(p);
    V.add_face({0, 1, 2}, "blue");
    V.add_face({0, 3}, "green");
    keep(add::union_(a, V), "u_flat");                        // (add.py: A is lost -- see the report)
    keep(add::difference(a, V), "d_flat");
    keep(add::intersect(a, V), "i_flat");
    keep(add::union_(V, a), "u_flat2");
}

// ---------------------------------------------------------------------------
//  cut
// ---------------------------------------------------------------------------

CASE(b_cut_box) {
    Mesh B = make_box({0, 0, 0}, 2, "red");
    keep(add::cut(B), "default");
    keep(add::cut(B, {0, 0.5, 0}, {0, 1, 0}, false), "open");
    keep(add::cut(B, {0, 0, 0}, {1, 1, 0}, true, Color("blue")), "diagonal");
    keep(add::cut(B, {0.2, 0.1, -0.3}, {1, 2, 3}), "slant");
    keep(add::cut(B, {0, 1, 0}, {0, 1, 0}), "on_top");        // the plane of the top face
    keep(add::cut(B, {0, -1, 0}, {0, 1, 0}), "on_bottom");
    keep(add::cut(B, {0, 5, 0}, {0, 1, 0}), "all_behind");
    keep(add::cut(B, {0, -5, 0}, {0, 1, 0}), "all_front");
    keep(add::cut(B, {0, 0, 0}, {0, -1, 0}, true, add::transparent("gold", 0.5)), "upside");
    keep(add::cut(B, {1, 1, 1}, {1, 1, 1}), "corner");
    keep(add::cut(B, {0, 0, 0}, {0, 0, 0}), "no_normal");
    add::box({0, 0, 0}, 1, "green");
    keep(add::cut(add::scene(), {0, 0.1, 0}, {0, 1, 0}), "scene");
    save_case();
    Mesh odd = make_box({0, 0, 0}, 1, "red");                 // faces of two and of one corner
    odd.add_face({0, 7}, "blue");
    odd.add_face({3}, "green");
    odd.add_polygon({{0.5, 0.2, -0.3}, {-0.2, -0.4, 0.1}}, "gold");
    keep(add::cut(odd, {0.1, 0, 0}, {1, 0.3, 0}), "odd");
    odd.add_face({}, "blue");                                 // a face of no corners: add.py fails
    try {
        add::cut(odd);
    } catch (const std::out_of_range&) {
        record("raised");
    }
}

CASE(b_cut_curved) {
    Mesh S = make_sphere({0, 0, 0}, 1, 10, "white");
    Points normals = {{0, 1, 0}, {1, 1, 0}, {0.3, -0.5, 0.8}, {-1, 0.2, 0.1}};
    for (int i = 0; i < 4; ++i)
        keep(add::cut(S, {0.1 * i, -0.2, 0.05}, normals[i], true, Color("red")), fmt("sphere%d", i));
    Mesh T = make_torus({0, 0, 0}, 1.0, 0.35, 16, 8, "teal");
    keep(add::cut(T), "torus_flat");                          // two rings: two caps
    keep(add::cut(T, {0, 0, 0}, {1, 0, 0}), "torus_upright"); // two round cross-sections
    keep(add::cut(T, {0.2, 0.1, 0}, {1, 2, 0.5}, true, Color("black")), "torus_slant");
    Mesh C = make_cylinder({0, -1, 0}, {0, 1, 0}, 0.5, 16, "blue");
    keep(add::cut(C, {0, 0.2, 0}, {0.4, 1, 0.3}), "cyl_slant");
    keep(add::cut(C, {0, 0, 0}, {1, 0, 0}, false), "cyl_half_open");
    keep(add::cut(add::cut(C, {0, 0.5, 0}, {0, 1, 0}), {0, -0.5, 0}, {0, -1, 0}), "slab");
    keep(add::cut(make_cone({0, 0, 0}, {0, 2, 0}, 1, 12, "gold"), {0, 1, 0}, {1, 1, 0}), "cone");
    keep(add::cut(add::make([] { add::tube({0, -1, 0}, {0, 1, 0}, 0.5, 12, "red"); }), {0, 0, 0}, {1, 0, 0}), "tube");
    keep(add::cut(add::make([] { add::grid({0, 0, 0}, {2, 2}, 4, 4, "green"); }), {0, 0, 0}, {1, 0, 0.5}), "sheet");
}

// ---------------------------------------------------------------------------
//  inside
// ---------------------------------------------------------------------------

CASE(b_inside_points) {
    Mesh B = make_box({0, 0, 0}, 2, "red");
    // (z = 0.9999999995: just under the top face, which all three rays graze -- false)
    for (const Point& p : Points{{0, 0, 0}, {0.9, 0.9, 0.9}, {1.1, 0, 0}, {0, -3, 0}, {1, 0, 0}, {1, 1, 0}, {1, 1, 1},
                                 {0.5, 1, 0.25}, {-1, -1, -1}, {0.999999999, 0, 0}, {1.000000001, 0, 0},
                                 {0.3, 0.2, -1}, {0.1, 0.2, 0.9999999995}, {1e30, 0, 0}})
        record(add::inside(B, p));
    Mesh S = make_sphere({0, 0, 0}, 1, 10, "white");
    for (const Point& p : Points{{0, 0, 0}, {0.5, 0.5, 0.5}, {0.6, 0.6, 0.6}, {0, 1, 0}, {0, 0.99, 0}, {0, 1.01, 0}})
        record(add::inside(S, p));
    Mesh T = make_torus({0, 0, 0}, 1.0, 0.35, 16, 8, "teal");
    for (const Point& p :
         Points{{0, 0, 0}, {1, 0, 0}, {0, 0, -1}, {0.7, 0.1, 0.7}, {1.4, 0, 0}, {1.3, 0, 0}, {0, 0.3, 1}})
        record(add::inside(T, p));
    Mesh O = make_poly("octahedron", {0, 0, 0}, 1);
    for (const Point& p :
         Points{{0, 0, 0}, {0.3, 0.3, 0.3}, {0.34, 0.33, 0.33}, {1, 0, 0}, {0.5, 0.5, 0}, {0, 0, 0.999}})
        record(add::inside(O, p));
    record(add::inside(Mesh(), Point{0, 0, 0}));
    record(add::inside(Mesh(), Point{1e30, -1e30, 5}));
    for (const Point& p : Points{{std::nan(""), 0, 0}, {0, add::inf, 0}, {0, 0, -add::inf}}) {
        try {
            add::inside(B, p);
        } catch (const std::exception&) {
            record("raised");
        }
    }
    Mesh far;                                                 // 2e154 wide: add.py's (hi - lo) ** 2 overflows
    far.add_polygon({{-1e154, 0, 0}, {-1e154, 1, 0}, {-1e154, 0, 1}}, "red");
    far.add_polygon({{1e154, 0, 0}, {1e154, 0, 1}, {1e154, 1, 0}}, "red");
    record(add::detail::to_polys(far).size());
    try {
        add::inside(far, Point{0, 0, 0});
    } catch (const std::overflow_error&) {
        record("raised");
    }
    Mesh wide;                                                // 1e154 wide: no overflow, and cell numbers
    wide.add_polygon({{-0.5e154, 0, 0}, {-0.5e154, 1, 0}, {-0.5e154, 0, 1}}, "red");   // far past 64 bits
    wide.add_polygon({{0.5e154, 0, 0}, {0.5e154, 0, 1}, {0.5e154, 1, 0}}, "red");
    record(bits(add::inside(wide, Points{{0, 0.2, 0.2}, {0.5e154, 0.2, 0.2}, {-0.6e154, 0.2, 0.2}, {0.5e154, 1, 1}})));
}

CASE(b_inside_list) {
    Mesh T = make_torus({0, 0, 0}, 1.0, 0.35, 16, 8, "teal");
    Points pts = add::random_points(300, {-1.5, -0.5, -1.5}, {1.5, 0.5, 1.5}, 3);
    record(bits(add::inside(T, pts)));
    Mesh S = make_sphere({0.2, 0, 0}, 1, 6, "white");
    pts = add::random_points(200, {-1.2, -1.2, -1.2}, {1.4, 1.2, 1.2}, 4);
    record(bits(add::inside(S, pts)));
    Mesh cube = make_box({0, 0, 0}, 2);
    Mesh ball = make_sphere({0, 0, 0}, 1.2, 6);
    Mesh D = add::difference(cube, ball);
    pts = add::random_points(200, {-1.1, -1.1, -1.1}, {1.1, 1.1, 1.1}, 5);
    record(bits(add::inside(D, pts)));
    Points grid;
    for (int x = -5; x < 6; ++x)
        for (int y = -5; y < 6; ++y) grid.push_back({x * 0.25, y * 0.25, 0.1});
    record(bits(add::inside(make_box({0, 0, 0}, 2), grid)));
    record(bits(add::inside(Mesh(), Points{{0, 0, 0}, {1, 1, 1}})));
    try {
        add::inside(T, Points{});
    } catch (const std::out_of_range&) {
        record("raised");
    }
}

// ---------------------------------------------------------------------------
//  The machinery
// ---------------------------------------------------------------------------

using add::detail::Poly;

CASE(b_poly_split) {
    std::vector<Points> shapes = {{{0, 0, 0}, {1, 0, 0}, {1, 1, 0}, {0, 1, 0}},
                                  {{0, 0, 0}, {2, 0, 1}, {2, 2, 1}, {0.5, 2.5, 0}, {-1, 1, -0.5}},
                                  {{0, 0, 0}, {1, 1, 1}, {2, 2, 2}},
                                  {{0.1, 0.2, 0.3}, {1.7, -0.4, 0.9}},
                                  {{0, 0, 0}, {0, 0, 1e-12}, {0, 1e-12, 0}}};
    std::vector<std::pair<Point, double>> planes = {
        {{1.0, 0.0, 0.0}, 0.5}, {{0.0, 1.0, 0.0}, 0.0}, {{0.6, 0.8, 0.0}, 1.0}, {{0.0, 0.0, 1.0}, 5.0},
        {{0.5773502691896258, 0.5773502691896258, 0.5773502691896258}, 0.8}};
    for (const Points& pts : shapes) {
        Poly p(pts, Color("red"));
        record(p.n);
        record(p.w);
        for (const auto& plane : planes) {
            for (double eps : {add::BOOL_EPS, 1e-12, 0.3}) {
                std::vector<Poly> front, back;
                add::detail::split(plane.first, plane.second, p, front, back, eps);
                record(fmt("%d %d", (int)front.size(), (int)back.size()));
                std::vector<Poly> both = front;
                both.insert(both.end(), back.begin(), back.end());
                for (const Poly& q : both) {
                    record(q.pts.size());
                    for (const Point& x : q.pts) record(x);
                    record(q.n);
                    record(q.w);
                }
            }
        }
    }
}

CASE(b_near_order) {
    add::detail::Solid S(make_sphere({0.1, 0.2, 0.3}, 1.3, 10, "white"));
    record(S.grid->cell);
    record(S.grid->oversize.size());
    record(S.lo);
    record(S.hi);
    record(S.scale);
    add::Random r(11);
    for (int n = 0; n < 60; ++n) {
        Point c, h;
        for (int a = 0; a < 3; ++a) c[a] = r.uniform(-1.5, 1.5);
        for (int a = 0; a < 3; ++a) h[a] = r.uniform(0, 0.8);
        Point lo{c[0] - h[0], c[1] - h[1], c[2] - h[2]};
        Point hi{c[0] + h[0], c[1] + h[1], c[2] + h[2]};
        record(ints(S.grid->near(lo, hi)));
    }
    record(ints(S.grid->near({-9, -9, -9}, {9, 9, 9})));
    add::detail::Solid T(
        add::merge({make_box({0, 0, 0}, 1), make_cuboid({0, 0, 0}, {40, 0.1, 0.1}), make_sphere({3, 0, 0}, 0.5, 6)}));
    record(ints(T.grid->oversize));
    for (int x = -2; x < 5; ++x) record(ints(T.grid->near({x - 0.3, -0.3, -0.3}, {x + 0.3, 0.3, 0.3})));
}

CASE(b_rays) {
    std::vector<Mesh> meshes = {make_box({0, 0, 0}, 2), make_torus({0, 0, 0}, 1.0, 0.35, 16, 8),
                                make_poly("tetrahedron", {0, 0, 0}, 1),
                                Mesh()};
    for (const Mesh& M : meshes) {
        add::detail::Solid S(M);
        for (size_t which = 0; which < 3; ++which) {
            const add::detail::RayIndex& R = S.ray_index(which);
            record(R.d);
            record(R.e1);
            record(R.e2);
            record(R.cell);
            record(R.tris.size());
            std::string answers;
            for (const Point& p : Points{{0, 0, 0}, {1, 1, 1}, {1, 0, 0}, {0.5, 0.5, 0.5}, {0, 1, 0}, {-1, 0.2, 0.3},
                                         {1, 0.3, -0.2}, {0.25, 0.25, -0.2}, {0.577, 0.577, 0.577}})
                answers += (answers.empty() ? "" : " ") + maybe(R.inside(p));
            record(answers);
        }
        Points pts = add::random_points(40, {-1.2, -1.2, -1.2}, {1.2, 1.2, 1.2}, 8);
        std::vector<bool> in;
        for (const Point& p : pts) in.push_back(S.contains(p));
        record(bits(in));
        for (size_t i = 0; i < M.V.size() && i < 12; ++i) {
            record(maybe(S.ray_index(0).inside(M.V[i])));
            record(S.contains(M.V[i]));
        }
    }
}

CASE(b_pieces) {
    add::detail::Solid A(make_box({0, 0, 0}, 2, "red"));
    add::detail::Solid B(make_cuboid({1, 0, 0.5}, {2, 2, 1}, "blue"));
    for (size_t i = 0; i < A.polys.size(); ++i) {
        for (const add::detail::FlushPiece& found : add::detail::split_against(A.polys[i], B)) {
            record(fmt("%d %s", (int)i, ints(found.flush).c_str()));
            for (const Point& x : found.piece.pts) record(x);
        }
    }
    std::vector<std::vector<std::string>> sets = {{"out"}, {"in"}, {"same"}, {"opp"}, {"out", "same"}, {"in", "opp"}};
    for (const std::vector<std::string>& keep_set : sets) {
        for (bool flip : {false, true}) {
            for (int which = 0; which < 2; ++which) {
                add::detail::Solid& src = which == 0 ? A : B;
                add::detail::Solid& other = which == 0 ? B : A;
                std::optional<Color> paint;
                if (flip) paint = Color("gold");
                std::vector<Poly> out = add::detail::keep_pieces(
                    src, other, add::detail::KeepSet(keep_set.begin(), keep_set.end()), flip, paint);
                record(out.size());
                for (const Poly& q : out) {
                    record(q.pts.size());
                    record(q.n);
                    record(q.w);
                    record(q.c);
                }
            }
        }
    }
    std::vector<Poly> polys = add::detail::to_polys(make_sphere({0, 0, 0}, 1, 6, "white"));
    record(polys.size());
    record(polys[7].n);
    record(polys[7].w);
    Mesh M = add::detail::from_polys(std::vector<Poly>(polys.begin(), polys.begin() + 40));
    dump(M);
    dump(add::detail::from_polys(std::vector<Poly>(polys.begin(), polys.begin() + 5), false));
    record(add::detail::boxes_apart(make_box({0, 0, 0}, 1), make_box({1, 0, 0}, 1)));
    record(add::detail::boxes_apart(make_box({0, 0, 0}, 1), make_box({1.00000001, 0, 0}, 1)));
    record(add::detail::boxes_apart(make_box({0, 0, 0}, 1), make_box({1, 0, 0}, 1), -1e-3));
}

static void run_loops(const std::vector<std::pair<Point, Point>>& edges) {
    std::vector<Points> out = add::detail::loops(edges);
    record(out.size());
    for (const Points& loop : out) {
        record(loop.size());
        for (const Point& p : loop) record(p);
    }
}

CASE(b_loops) {
    Points sq = {{0, 0, 0}, {1, 0, 0}, {1, 1, 0}, {0, 1, 0}};
    std::vector<std::pair<Point, Point>> e;
    for (int i = 0; i < 4; ++i) e.push_back({sq[i], sq[(i + 1) % 4]});
    run_loops(e);
    e.clear();
    for (int i : {2, 0, 3, 1}) e.push_back({sq[(i + 1) % 4], sq[i]});
    run_loops(e);
    e.clear();
    for (int i = 0; i < 3; ++i) e.push_back({sq[i], sq[(i + 1) % 4]});   // open: a chain of three
    run_loops(e);
    run_loops({{sq[0], sq[1]}, {sq[1], sq[2]}});                         // too short
    Points tri = {{3, 0, 0}, {4, 0, 0}, {3.5, 1, 0}};
    e.clear();
    for (int i = 0; i < 4; ++i) e.push_back({sq[i], sq[(i + 1) % 4]});
    for (int i = 0; i < 3; ++i) e.push_back({tri[i], tri[(i + 1) % 3]});
    run_loops(e);
    run_loops({{sq[0], sq[1]}, {sq[1], sq[2]}, {sq[1], {1, -1, 0}}, {{1, -1, 0}, sq[0]}, {sq[2], sq[3]},
               {sq[3], sq[0]}});                                           // a branch at sq[1]
    run_loops({{{0.0, 0.0, 0.0}, {1.00000001, 0, 0}}, {{1.00000004, 0, 0}, {1, 1, 0}},
               {{1, 1.00000002, 0}, {-0.0, 1, 0}}, {{0.0, 1, -0.0}, {-0.0, -0.0, 0.00000003}}});
    run_loops({});
}

//: Python's own set order (which BoxGrid::near keeps), for sets built the way near() builds
//: them -- small ones, and one past 50000 keys, where the table grows differently.
CASE(b_intset) {
    add::Random r(5);
    for (const std::pair<int, int>& nh : std::vector<std::pair<int, int>>{
             {3, 10}, {5, 8}, {6, 100}, {20, 50}, {100, 1000}, {1000, 3000}, {3000, 100000}, {100000, 400000}}) {
        int n = nh.first, hi = nh.second;
        add::detail::IntSet s;
        long long first = r.randint(0, 6);
        for (long long i = 0; i < first; ++i) s.add((int)r.randint(0, hi));
        for (int round = 0; round < 5; ++round)
            for (int i = 0; i < n / 5 + 1; ++i) s.add((int)r.randint(0, hi));
        record(ints(s.items()));
    }
}

//: Two small boxes far from the origin: the cell numbers of the box grid pass 2**53, beyond
//: which a double no longer holds every whole number (add.py's are exact).
CASE(b_far) {
    Mesh A = make_box({7e11, 0, 0}, 1e-3, "red");
    Mesh B = make_box({7e11 + 3e-4, 2e-4, 1e-4}, 1e-3, "blue");
    add::detail::Solid SA(A), SB(B);
    record(SB.grid->cell);
    for (const Poly& P : SA.polys) {
        Point lo, hi;
        for (int a = 0; a < 3; ++a) {
            lo[a] = add::detail::coord_min(P.pts, a);
            hi[a] = add::detail::coord_max(P.pts, a);
        }
        record(ints(SB.grid->near(lo, hi)));
        record(fmt("%d %d", (int)add::detail::split_against(P, SB).size(), (int)SB.grid->near(hi, hi).size()));
    }
    all_three(A, B);
    record(bits(add::inside(B, Points{{7e11 + 3e-4, 2e-4, 1e-4}, {7e11, 0, 0}, {7e11 + 7e-4, 5e-4, 5e-4}})));
    // A small ball further out: its triangles are small enough to be filed in cells, and the
    // cell numbers (about 9.3e15) are only every second whole number as a double.
    add::detail::Solid SF(make_sphere({1e12, 0, 0}, 1e-3, 6, "white"));
    add::detail::Solid SG(make_box({1e12 + 2e-4, 3e-4, 0}, 1e-3, "red"));
    record(SF.grid->cell);
    record(ints(SF.grid->oversize));
    add::Random r(2);
    for (int n = 0; n < 40; ++n) {
        Point c;
        c[0] = 1e12 + r.uniform(-1e-3, 1e-3);
        c[1] = r.uniform(-1e-3, 1e-3);
        c[2] = r.uniform(-1e-3, 1e-3);
        double h = r.uniform(0, 4e-4);
        record(ints(SF.grid->near({c[0] - h, c[1] - h, c[2] - h}, {c[0] + h, c[1] + h, c[2] + h})));
    }
    struct Run {
        add::detail::Solid* src;
        add::detail::Solid* other;
        add::detail::KeepSet keep;
        bool flip;
    };
    for (const Run& run : {Run{&SG, &SF, {"out"}, false}, Run{&SF, &SG, {"in"}, true}, Run{&SF, &SG, {"out"}, false}}) {
        std::vector<Poly> out = add::detail::keep_pieces(*run.src, *run.other, run.keep, run.flip);
        record(out.size());
        for (const Poly& q : out)
            for (const Point& x : q.pts) record(x);
    }
}

//: More than 20000 pieces from one face: add.py stops cutting it -- and then cannot unpack the
//: bare piece it returned (see the report).
CASE(b_guard) {
    Mesh B;                                                   // 250 tall thin blades across the face
    for (int k = 0; k < 250; ++k) {
        double a = add::pi * k / 250 + 0.1;
        double c = std::cos(a), s = std::sin(a);
        double ox = 0.37 * std::sin(3.1 * k), oz = 0.41 * std::cos(2.3 * k);
        B.add_polygon({{ox - 3 * c, 0.5, oz - 3 * s}, {ox + 3 * c, 0.5, oz + 3 * s}, {ox, 1.5, oz}}, "blue");
    }
    Mesh top;
    top.add_polygon({{-1, 1, -1}, {-1, 1, 1}, {1, 1, 1}, {1, 1, -1}}, "red");
    std::vector<add::detail::FlushPiece> res =
        add::detail::split_against(add::detail::Solid(top).polys[0], add::detail::Solid(B));
    record(res.size());
    std::vector<int> bare;
    std::vector<add::detail::FlushPiece> good;
    for (size_t i = 0; i < res.size(); ++i) {
        if (res[i].bare) bare.push_back((int)i);
        else good.push_back(res[i]);
    }
    record(ints(bare));
    std::vector<add::detail::FlushPiece> ends(good.begin(), good.begin() + 3);
    ends.insert(ends.end(), good.end() - 3, good.end());
    for (const add::detail::FlushPiece& found : ends) {
        record(ints(found.flush));
        for (const Point& x : found.piece.pts) record(x);
    }
    try {
        add::union_(top, B);
    } catch (const std::runtime_error&) {
        record("raised");
    }
}

CASE(b_stress) {
    using Maker = std::function<Mesh(const Point&, double, const Color&)>;
    std::vector<Maker> makers = {
        [](const Point& c, double s, const Color& col) { return make_cuboid(c, {s, 0.8 * s, 1.1 * s}, col); },
        [](const Point& c, double s, const Color& col) { return make_sphere(c, 0.6 * s, 6, col); },
        [](const Point& c, double s, const Color& col) {
            return make_cylinder({c[0], c[1] - 0.6 * s, c[2]}, {c[0], c[1] + 0.6 * s, c[2]}, 0.4 * s, 10, col);
        },
        [](const Point& c, double s, const Color& col) {
            return make_cone({c[0], c[1] - 0.5 * s, c[2]}, {c[0], c[1] + 0.5 * s, c[2]}, 0.6 * s, 10, col);
        },
        [](const Point& c, double s, const Color& col) { return make_poly("octahedron", c, 0.7 * s, col); },
        [](const Point& c, double s, const Color& col) { return make_poly("dodecahedron", c, 0.7 * s, col); },
        [](const Point& c, double s, const Color& col) { return make_torus(c, 0.5 * s, 0.2 * s, 12, 6, col); }};
    std::vector<Color> colors = {"red", "green", "blue", "gold", "white", "teal", "pink"};
    for (int seed = 0; seed < 21; ++seed) {
        add::Random r(seed);
        int ka = (int)r.randint(0, (long long)makers.size() - 1);
        int kb = (int)r.randint(0, (long long)makers.size() - 1);
        Point ca, cb, axis;
        for (int a = 0; a < 3; ++a) ca[a] = r.uniform(-0.2, 0.2);
        for (int a = 0; a < 3; ++a) cb[a] = r.uniform(-0.6, 0.6);
        double sa = r.uniform(1.0, 1.6);
        double sb = r.uniform(0.6, 1.4);
        for (int a = 0; a < 3; ++a) axis[a] = r.uniform(-1, 1);
        double angle = r.uniform(0, add::pi);
        Mesh A = makers[ka](ca, sa, colors[ka]);
        Mesh B = add::rotate(makers[kb](cb, sb, colors[kb]), axis, angle, cb);
        record(fmt("seed %d: %d %d", seed, ka, kb));
        keep(add::union_(A, B), fmt("u%d", seed));
        keep(add::difference(A, B), fmt("d%d", seed));
        keep(add::intersect(A, B), fmt("i%d", seed));
    }
}

CASE(b_chain) {
    Mesh M = make_box({0, 0, 0}, 2, "white");
    std::vector<Mesh> holes;
    for (const std::pair<double, double>& xz :
         std::vector<std::pair<double, double>>{{-0.5, -0.5}, {0.5, 0.5}, {0.5, -0.5}})
        holes.push_back(make_cylinder({xz.first, -2, xz.second}, {xz.first, 2, xz.second}, 0.25, 10, "red"));
    M = add::difference(M, holes);
    keep(M, "drilled");
    M = add::union_(M, make_cuboid({0, 1.2, 0}, {1, 0.4, 1}, "blue"));
    keep(M, "capped");
    M = add::intersect(M, make_sphere({0, 0, 0}, 1.6, 6, "gold"));
    keep(M, "rounded");
    M = add::cut(M, {0, 0, 0.1}, {0, 0, 1}, true, Color("black"));
    keep(M, "halved");
    record(bits(add::inside(M, Points{{0, 0, 0}, {-0.5, 0, -0.5}, {0.8, 0.8, -0.8}, {0, 1.3, 0}})));
}

CASE(b_scene) {
    add::box({0, 0, 0}, 2, "red");
    Mesh a = add::layer();
    add::sphere({1, 1, 1}, 1.3, 16, "blue");
    Mesh b = add::layer();
    add::mesh(add::union_(a, b));
    save_case();
}

// Parity cases for _cpp/55_mesh_ops.hpp: vertices, edges, neighbours, faces, borders,
// inflate / spherify / refine / dual / truncate (see cases_55_mesh_ops.py).
#include "parity.hpp"

using add::Color;
using add::Face;
using add::Mesh;
using add::Point;
using add::Points;

static const std::vector<Color> SIX = {"red", Color(10, 200, 30), add::transparent("sky", 0.4), "#123456",
                                       Color(250, 250, 5), "navy"};
static const double PHI = (1 + std::sqrt(5.0)) / 2;

//: Vertices (x, y, z), (y, z, x), (z, x, y) whose nearest to the origin Python's ``** 2``
//: finds differently from ``x * x`` (found by search).
static const Points TIES = {{1.4050326807183406, 0.4468445654703572, 1.4270568530698329},
                            {1.0153553763542957, 1.3452739161380447, 1.1450256657771676},
                            {-0.7115232226960133, -0.5445620771153004, -0.9360590698721349}};

static std::string ints(const std::vector<int>& xs) {
    std::string s;
    for (size_t i = 0; i < xs.size(); ++i) s += (i ? " " : "") + std::to_string(xs[i]);
    return s;
}

static std::string floats(const std::vector<double>& xs) {
    std::string s;
    for (size_t i = 0; i < xs.size(); ++i) s += (i ? " " : "") + add::detail::py_repr(xs[i]);
    return s;
}

static std::string pairs(const std::vector<add::Edge>& es) {
    std::string s;
    for (size_t i = 0; i < es.size(); ++i)
        s += (i ? " " : "") + std::to_string(es[i].first) + "-" + std::to_string(es[i].second);
    return s;
}

static std::vector<std::string> lists(const std::vector<std::vector<int>>& xss) {
    std::vector<std::string> out;
    for (const std::vector<int>& xs : xss) out.push_back(ints(xs));
    return out;
}

//: The mesh exactly as it is, as .obj + .mtl (faces of any size kept whole).
static void save_obj(const Mesh& M, const std::string& tag) { add::obj(parity::current() + "_" + tag + ".obj", M); }

static Mesh from_faces(const Points& V, const std::vector<Face>& F, const std::vector<Color>& colors = {}) {
    Mesh M;
    for (const Point& p : V) M.add_vertex(p);
    for (size_t i = 0; i < F.size(); ++i) M.add_face(F[i], colors.empty() ? add::DEFAULT_COLOR : colors[i % colors.size()]);
    return M;
}

static const std::vector<Face> CUBE_F = {{0, 4, 6, 2}, {1, 3, 7, 5}, {0, 1, 5, 4}, {2, 6, 7, 3}, {0, 2, 3, 1}, {4, 5, 7, 6}};

static Mesh cube(Point lo = {-0.5, -0.25, -0.75}, Point hi = {0.5, 0.75, 1.25}, const std::vector<Color>& colors = {},
                 const std::vector<Face>& faces = CUBE_F) {
    Points V;
    for (int k = 0; k < 8; ++k) V.push_back({k & 1 ? hi[0] : lo[0], k & 2 ? hi[1] : lo[1], k & 4 ? hi[2] : lo[2]});
    return from_faces(V, faces, colors);
}

static const Point LO = {-0.5, -0.25, -0.75}, HI = {0.5, 0.75, 1.25};

//: The cube without its bottom and top: two border loops.
static Mesh tube() { return cube(LO, HI, SIX, {{0, 4, 6, 2}, {1, 3, 7, 5}, {0, 2, 3, 1}, {4, 5, 7, 6}}); }

static Mesh octa(double r = 1.0) {
    Points V = {{r, 0, 0}, {-r, 0, 0}, {0, r, 0}, {0, -r, 0}, {0, 0, r}, {0, 0, -r}};
    std::vector<Face> F = {{0, 2, 4}, {1, 4, 2}, {0, 4, 3}, {1, 3, 4}, {0, 5, 2}, {1, 2, 5}, {0, 3, 5}, {1, 5, 3}};
    return from_faces(V, F, SIX);
}

static Mesh tetra() {
    Points V = {{1, 1, 1}, {1, -1, -1}, {-1, 1, -1}, {-1, -1, 1}};
    return from_faces(V, {{0, 1, 2}, {0, 3, 1}, {0, 2, 3}, {1, 3, 2}}, {"red", "green", "blue", "gold"});
}

static Mesh icosa() {
    double p = PHI;
    Points V = {{-1, p, 0}, {1, p, 0}, {-1, -p, 0}, {1, -p, 0}, {0, -1, p}, {0, 1, p}, {0, -1, -p}, {0, 1, -p},
                {p, 0, -1}, {p, 0, 1}, {-p, 0, -1}, {-p, 0, 1}};
    std::vector<Face> F = {{0, 11, 5}, {0, 5, 1}, {0, 1, 7}, {0, 7, 10}, {0, 10, 11}, {1, 5, 9}, {5, 11, 4},
                           {11, 10, 2}, {10, 7, 6}, {7, 1, 8}, {3, 9, 4}, {3, 4, 2}, {3, 2, 6}, {3, 6, 8},
                           {3, 8, 9}, {4, 9, 5}, {2, 4, 11}, {6, 2, 10}, {8, 6, 7}, {9, 8, 1}};
    return from_faces(V, F, {"white", "sky"});
}

//: An open, bumpy sheet of quads.
static Mesh patch(int nx = 4, int nz = 3) {
    Points V;
    for (int i = 0; i < nx + 1; ++i)
        for (int j = 0; j < nz + 1; ++j) {
            double x = -1.0 + 2.0 * i / nx;
            double z = -0.7 + 1.9 * j / nz;
            V.push_back({x, 0.3 * std::sin(2 * x + z) + 0.1 * x * z, z});
        }
    std::vector<Face> F;
    for (int i = 0; i < nx; ++i)
        for (int j = 0; j < nz; ++j) {
            int a = i * (nz + 1) + j;
            F.push_back({a, a + 1, a + nz + 2, a + nz + 1});
        }
    return from_faces(V, F, SIX);
}

//: A convex pentagon, a concave one, a triangle and a two-corner face.
static Mesh mixed() {
    Mesh M;
    M.add_polygon({{0, 0, 0}, {2, 0, 0}, {2.5, 1, 0.2}, {1, 2, 0.1}, {-0.5, 1, 0}}, "red");
    M.add_polygon({{3, 0, 0}, {5, 0, 0}, {5, 2, 0}, {4, 1, 0}, {3, 2, 0}}, "green");
    M.add_polygon({{0, 3, 0}, {1, 3, 0}, {0.5, 4, 1}}, Color(1, 2, 3));
    M.add_face({0, 5}, "blue");
    return M;
}

//: Two triangles that share one corner only.
static Mesh touching() {
    return from_faces({{0, 0, 0}, {1, 0, 0}, {0, 1, 0}, {-1, 0, 0}, {0, -1, 0}}, {{0, 1, 2}, {0, 3, 4}}, {"red"});
}

//: Everything rings() has to cope with: two cones meeting at vertex 0, a face through
//: vertex 7 twice, two faces that disagree on the winding of edge 13-14, a vertex without
//: faces (17) and a two-corner face.
static Mesh weird() {
    Points V = {{0, 0, 0}, {1, 0, 0.5}, {0, 1, 0.5}, {-1, -1, 0.5}, {1, 0, -0.5}, {0, 1, -0.5}, {-1, -1, -0.5},
                {3, 0, 0}, {4, -1, 0}, {4, 1, 0}, {2, 1, 0}, {2, -1, 0}, {5, 0, 0},
                {0, 5, 0}, {1, 5, 0}, {0, 6, 0}, {0, 4, 0},
                {9, 9, 9},
                {7, 0, 0}, {8, 0.5, 0}};
    std::vector<Face> F = {{0, 1, 2}, {0, 2, 3}, {0, 3, 1}, {0, 5, 4}, {0, 6, 5}, {0, 4, 6},
                           {7, 8, 9, 7, 10, 11}, {8, 12, 9},
                           {13, 14, 15}, {13, 14, 16},
                           {18, 19}};
    return from_faces(V, F, SIX);
}

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

//: A polyhedron with faces dropped, flipped and doubled, and a few random faces (two to
//: five corners, a corner maybe repeated) added.
static Mesh mangled(long long seed) {
    add::Random r(seed);
    int which = (int)r.randint(0, 3);
    Mesh base = which == 0 ? icosa() : which == 1 ? octa() : which == 2 ? cube() : tetra();
    Mesh M;
    for (const Point& p : base.V) M.add_vertex(p);
    for (size_t q = 0; q < base.F.size(); ++q) {
        Face f = base.F[q];
        const Color& c = base.C[q];
        long long roll = r.randint(0, seed < 20 ? 9 : 39);
        if (roll == 0) continue;
        if (roll == 1) std::reverse(f.begin(), f.end());
        M.add_face(f, c);
        if (roll == 2) M.add_face(f, c);
    }
    long long extra = r.randint(0, 3);
    for (long long e = 0; e < extra; ++e) {
        long long k = r.randint(2, 5);
        Face f;
        for (long long j = 0; j < k; ++j) f.push_back((int)r.randint(0, (long long)base.V.size() - 1));
        M.add_face(f, SIX[(size_t)r.randint(0, 5)]);
    }
    return M;
}

static std::vector<Mesh> shapes() {
    return {cube(LO, HI, SIX), octa(), icosa(), tetra(), patch(3, 2), tube(), weird(), mixed(), touching()};
}

CASE(m_vertex) {
    Mesh M = cube(LO, HI, SIX);
    record(add::vertex(M, 3));
    record(add::vertex(M, -1));
    save_mesh(add::set_vertex(M, 3, {std::nullopt, 2.5, std::nullopt}), "set1");
    save_mesh(add::set_vertex(M, -2, {1, 2, 3}), "set_neg");
    save_mesh(add::set_vertices(M, {{0, {std::nullopt, std::nullopt, -3}}, {5, {0.5, 0.25, std::nullopt}}}), "set_many");
    save_mesh(add::set_vertices(M, {}), "set_none");
    save_mesh(add::set_vertices(M, {{7, {5, std::nullopt, std::nullopt}}, {-1, {std::nullopt, 6, 0.5}}}), "alias");
    save_mesh(add::set_vertices(M, {{-1, {5, std::nullopt, 6}}, {7, {std::nullopt, std::nullopt, 1}}}), "alias2");
    save_mesh(add::set_vertices(M, {{3, {1, std::nullopt, std::nullopt}}, {2, {0, 0, 0}}, {3, {std::nullopt, 2, std::nullopt}}}),
              "repeat");
    std::map<int, Point> changes{{1, {9, 9, 9}}, {4, {8, 8, 8}}};
    save_mesh(add::set_vertices(M, changes), "map");
    save_mesh(add::move_vertex(M, 7, {0.1, 0.2, -0.3}), "moved");
    save_mesh(add::move_vertex(M, -8, {1, 0, 0}), "moved_neg");
    record(add::nearest_vertex(M, {1, 1, 1}));
    record(add::nearest_vertex(M, {0, -0.25, -0.75}));
    record(add::nearest_vertex(Mesh(), {0, 0, 0}));
    for (const Point& t : TIES)
        record(add::nearest_vertex(from_faces({{t.x, t.y, t.z}, {t.y, t.z, t.x}, {t.z, t.x, t.y}}, {}), {0, 0, 0}));
    for (int bad : {8, -9}) {
        try {
            add::vertex(M, bad);
        } catch (const std::out_of_range&) {
            record("raised");
        }
    }
}

CASE(m_edges) {
    for (const Mesh& M : shapes()) {
        record(pairs(add::edges(M)));
        record(floats(add::edge_lengths(M)));
        record(add::mean_edge_length(M));
        record(add::edge_length(M, 0, 1));
        record(add::edge_length(M, -1, 2));
        record(lists(add::adjacency(M)));
    }
    record(add::mean_edge_length(Mesh()));
    record(pairs(add::edges(Mesh())));
    add::mesh(octa());
    record(pairs(add::edges()));
    record(floats(add::edge_lengths()));
    record(add::mean_edge_length());
    record(lists(add::adjacency()));
    save_case();
}

CASE(m_rings) {
    for (const Mesh& M : shapes()) {
        std::string s;
        for (const auto& kv : add::detail::directed_edges(M))
            s += (s.empty() ? "" : " ") + add::detail::fmt("%d,%d:%d", kv.first.first, kv.first.second, kv.second);
        record(s);
        for (const add::detail::VertexRing& r : add::detail::rings(M)) {
            std::string ring;
            for (const auto& e : r.ring) ring += (ring.empty() ? "" : " ") + add::detail::fmt("%d:%d", e.first, e.second);
            record(std::string(r.closed ? "True" : "False") + " " + ring);
        }
    }
}

CASE(m_neighbors) {
    for (const Mesh& M : shapes()) {
        for (int i = 0; i < (int)M.V.size(); ++i) {
            record(ints(add::neighbors(M, i)));
            record(add::valence(M, i));
            record(add::mean_neighbor_distance(M, i));
            record(ints(add::vertex_faces(M, i)));
            record(add::vertex_normal(M, i));
        }
        record(ints(add::neighbours(M, -1)));
        record(ints(add::vertex_faces(M, -2)));
        record(add::valence(M, -3));
    }
}

CASE(m_faces) {
    for (const Mesh& M : shapes()) {
        for (int i = 0; i < (int)M.F.size(); ++i) {
            record(add::face_center(M, i));
            record(add::face_normal(M, i));
            record(add::face_area(M, i));
        }
        record(add::face_centers(M));
        record(add::face_center(M, -1));
        record(add::face_normal(M, -2));
        record(add::face_area(M, -2));
        try {
            add::face_center(M, (int)M.F.size());
        } catch (const std::out_of_range&) {
            record("raised");
        }
    }
    add::mesh(patch(2, 2));
    record(add::face_centers());
    save_case();
}

CASE(m_boundary) {
    std::vector<Mesh> all = shapes();
    all.push_back(Mesh());
    for (const Mesh& M : all) {
        record(pairs(add::boundary_edges(M)));
        record(lists(add::boundary_loops(M)));
    }
    add::mesh(patch(2, 2));
    add::mesh(touching());
    record(pairs(add::boundary_edges()));
    record(lists(add::boundary_loops()));
    save_case();
}

CASE(m_inflate_spherify) {
    Mesh C = cube(LO, HI, SIX);
    save_mesh(add::inflate(C, 0.1), "inflate");
    save_mesh(add::inflate(patch(), -0.2), "inflate_patch");
    save_mesh(add::inflate(weird(), 0.3), "inflate_weird");
    save_mesh(add::spherify(C), "default");
    save_mesh(add::spherify(C, Point{0, 0, 0}, 2.0, 0.5), "given");
    save_mesh(add::spherify(C, std::nullopt, std::nullopt, 0.25), "part");
    save_mesh(add::spherify(C, Point{0.1, 0.2, 0.3}), "center");
    save_mesh(add::spherify(C, std::nullopt, 0), "r0");
    save_mesh(add::spherify(Mesh()), "empty");
    save_mesh(add::spherify(add::refine(octa(), 3)), "dome");
}

CASE(m_refine) {
    save_mesh(add::refine(octa()), "octa1");
    save_mesh(add::refine(cube(LO, HI, SIX), 2), "cube2");
    save_mesh(add::refine(mixed()), "mixed");
    save_mesh(add::refine(weird()), "weird");
    save_mesh(add::refine(cube(), 0), "zero");
    save_mesh(add::refine(icosa(), -1), "negative");
    save_obj(add::refine(add::texture(cube(LO, HI, SIX), "a.png")), "textured");
}

CASE(m_dual) {
    save_obj(add::dual(cube(LO, HI, SIX)), "cube");
    save_obj(add::dual(octa(), "gold"), "octa");
    save_obj(add::dual(icosa()), "icosa");
    save_obj(add::dual(tetra()), "tetra");
    save_obj(add::dual(patch(3, 2)), "patch");
    save_obj(add::dual(weird()), "weird");
    save_obj(add::dual(add::dual(icosa()), add::transparent("red", 0.5)), "icosa2");
    save_obj(add::dual(Mesh()), "empty");
}

CASE(m_truncate) {
    save_obj(add::truncate(icosa(), 1 / 3.0, "black"), "football");
    save_obj(add::truncate(cube(LO, HI, SIX)), "cube");
    save_obj(add::truncate(octa(), 0.5), "half");
    save_obj(add::truncate(tetra(), 0.9, {10, 20, 30}), "over");
    save_obj(add::truncate(tetra(), 0.5 - 1e-13), "near_half");
    save_obj(add::truncate(patch(3, 2), 0.25), "patch");
    save_obj(add::truncate(weird(), 0.3), "weird");
    save_obj(add::truncate(mixed(), 0.2, "red"), "mixed");
    save_obj(add::truncate(touching()), "touching");
}

CASE(m_color_by_sides) {
    Mesh F = add::truncate(icosa());
    save_mesh(add::color_by_sides(F, {{5, "black"}, {6, "white"}}), "football");
    save_mesh(add::color_by_sides(mixed(), {{3, "red"}}), "keep");
    save_mesh(add::color_by_sides(mixed(), {{3, "red"}, {2, Color(1, 2, 3)}}, "blue"), "fallback");
    save_mesh(add::color_by_sides(cube(LO, HI, SIX), {}, add::transparent("gold", 0.5)), "all");
}

CASE(m_mangled) {
    for (long long seed = 0; seed < 40; ++seed) {
        Mesh M = mangled(seed);
        dump(M);
        for (const add::detail::VertexRing& r : add::detail::rings(M)) {
            std::string ring;
            for (const auto& e : r.ring) ring += (ring.empty() ? "" : " ") + add::detail::fmt("%d:%d", e.first, e.second);
            record(std::string(r.closed ? "True" : "False") + " " + ring);
        }
        for (int i = 0; i < (int)M.V.size(); ++i) {
            record(ints(add::neighbors(M, i)));
            record(ints(add::vertex_faces(M, i)));
            record(add::vertex_normal(M, i));
        }
        record(pairs(add::edges(M)));
        record(pairs(add::boundary_edges(M)));
        record(lists(add::boundary_loops(M)));
        dump(add::dual(M));
        dump(add::truncate(M, 0.3));
        dump(add::truncate(M, 0.5, "black"));
        dump(add::refine(M));
    }
}

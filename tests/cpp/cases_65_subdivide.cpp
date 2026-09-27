// Parity cases for _cpp/65_subdivide.hpp: the topology, one Catmull-Clark step and the limit
// positions and tangents, the regular stencils and the patch trees, the reparameterisation (norm,
// polygon domains, face maps), the repair, and catmull_clark / smooth / subdivide themselves
// (see cases_65_subdivide.py).
#include "parity.hpp"

using add::Color;
using add::Face;
using add::Mesh;
using add::Point;
using add::Point2;
using add::Points;
using add::detail::Topo;

static const std::vector<Color> SIX = {"red", Color(10, 200, 30), add::transparent("sky", 0.4), "#123456",
                                       Color(250, 250, 5), "navy"};

// -- helpers (the Python twin has the same ones) --------------------------------

static std::string ints(const std::vector<int>& xs) {
    std::string s;
    for (size_t i = 0; i < xs.size(); ++i) s += (i ? " " : "") + std::to_string(xs[i]);
    return s;
}
template <size_t N>
static std::string ints(const std::array<int, N>& xs) { return ints(std::vector<int>(xs.begin(), xs.end())); }

template <class Seq>
static std::string floats(const Seq& xs) {
    std::string s;
    bool first = true;
    for (double x : xs) {
        s += (first ? "" : " ") + add::detail::py_repr(x);
        first = false;
    }
    return s;
}

//: Every vertex (at full precision), face and colour of a mesh.
static void dump(const Mesh& M) {
    record("V " + std::to_string(M.V.size()));
    for (const Point& p : M.V) record(p);
    record("F " + std::to_string(M.F.size()));
    for (size_t k = 0; k < M.F.size() && k < M.C.size(); ++k) {
        record(ints(M.F[k]));
        record(M.C[k]);
    }
}

//: The mesh exactly as it is: an .off file, and every number in the .txt.
static void result(const Mesh& M, const std::string& tag = "") {
    save_mesh(M, tag);
    record("-- " + tag);
    dump(M);
}

//: Run fn and record the message of the exception it throws.
template <class F>
static void error(F fn) {
    try {
        fn();
    } catch (const std::exception& e) {
        record(std::string("error: ") + e.what());
        return;
    }
    record("no error");
}

static std::string yes(bool b) { return b ? "True" : "False"; }

//: Every table of a Topo.
static void topo(const Topo& T) {
    record(add::detail::fmt("V %d F %d E %d", (int)T.V.size(), (int)T.F.size(), (int)T.E.size()));
    for (const auto& e : T.E) record(ints(e));
    for (size_t v = 0; v < T.V.size(); ++v)
        record("v" + std::to_string(v) + ": VF " + ints(T.VF[v]) + " | VE " + ints(T.VE[v]) + " | " +
               yes(T.boundary[v]));
    for (size_t f = 0; f < T.F.size(); ++f)
        record("f" + std::to_string(f) + ": FE " + ints(T.FE[f]) + " | FN " + ints(T.FN[f]));
    record(T.all_quads());
    for (size_t f = 0; f < T.F.size(); ++f) record(T.centroid((int)f));
    for (size_t v = 0; v < T.V.size(); ++v) {
        auto r = T.ordered_ring((int)v);
        record("ring " + std::to_string(v) + ": " + (r ? ints(r->nbrs) + " | " + ints(r->faces) : std::string("None")));
    }
}

//: The points and faces of a Topo.
static void shape(const Topo& T) {
    record(add::detail::fmt("V %d F %d", (int)T.V.size(), (int)T.F.size()));
    for (const Point& p : T.V) record(p);
    for (const Face& f : T.F) record(ints(f));
}

//: A 4 x 4 control net (or None).
static void net(const std::optional<add::detail::BicubicNet>& P) {
    if (!P) {
        record("None");
        return;
    }
    for (const auto& row : *P)
        for (const Point& c : row) record(c);
}

static Mesh from_faces(const Points& V, const std::vector<Face>& F, const std::vector<Color>& colors = {}) {
    Mesh M;
    for (const Point& p : V) M.add_vertex(p);
    for (size_t i = 0; i < F.size(); ++i) M.add_face(F[i], colors.empty() ? add::DEFAULT_COLOR : colors[i % colors.size()]);
    return M;
}

static Topo as_topo(const Mesh& M) { return Topo(M.V, M.F); }

static const std::vector<Face> CUBE_F = {{0, 4, 6, 2}, {1, 3, 7, 5}, {0, 1, 5, 4}, {2, 6, 7, 3}, {0, 2, 3, 1}, {4, 5, 7, 6}};

//: A box from lo to hi as 8 shared corners and 6 quads, one colour each.
static Mesh cube(Point lo = {-1.0, -0.75, -0.5}, Point hi = {1.0, 1.25, 0.9}, const std::vector<Color>& colors = SIX,
                 const std::vector<Face>& faces = CUBE_F) {
    Points V;
    for (int k = 0; k < 8; ++k) V.push_back({k & 1 ? hi[0] : lo[0], k & 2 ? hi[1] : lo[1], k & 4 ? hi[2] : lo[2]});
    return from_faces(V, faces, colors);
}

//: The cube without its last face: an open box.
static Mesh open_box() {
    return cube({-1.0, -0.75, -0.5}, {1.0, 1.25, 0.9}, SIX, std::vector<Face>(CUBE_F.begin(), CUBE_F.begin() + 5));
}

static Mesh welded(const Mesh& M0) {
    Mesh M = M0.copy();
    add::detail::weld(M, 1e-9);
    return M;
}

//: Two unit cubes, the second moved by ``offset``: (1, 1, 0) shares an edge, (1, 1, 1) a corner.
static Mesh two_cubes(const Point& offset) {
    Point hi{offset[0] + 1.0, offset[1] + 1.0, offset[2] + 1.0};
    return add::merge({cube({0.0, 0.0, 0.0}, {1.0, 1.0, 1.0}, {"red"}), cube(offset, hi, {"blue"})});
}

//: Three quads that share one edge, and a fourth hanging off one of them.
static Mesh book() {
    Points V = {{0.0, 0.0, 0.0}, {0.0, 1.0, 0.0}, {1.0, 0.0, 0.0}, {1.0, 1.0, 0.0}, {-0.5, 0.0, 0.8}, {-0.5, 1.0, 0.8},
                {-0.5, 0.0, -0.8}, {-0.5, 1.0, -0.8}, {2.0, 0.0, 0.3}, {2.0, 1.0, 0.3}};
    return from_faces(V, {{0, 2, 3, 1}, {0, 1, 5, 4}, {0, 6, 7, 1}, {2, 8, 9, 3}}, SIX);
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

//: A pentagon and five triangles: valence 5 at the (off-centre) apex, 3 round the base.
static Mesh pent_pyramid() {
    Points V;
    for (int k = 0; k < 5; ++k) V.push_back({std::cos(2 * add::pi * k / 5), 0.0, std::sin(2 * add::pi * k / 5)});
    V.push_back({0.1, 1.3, -0.05});
    std::vector<Face> F = {{0, 1, 2, 3, 4}};
    for (int k = 0; k < 5; ++k) F.push_back({k, 5, (k + 1) % 5});
    return from_faces(V, F, SIX);
}

//: Two k-sided pyramids base to base: valence k at the tips.
static Mesh bipyramid(int k = 6) {
    Points V;
    for (int i = 0; i < k; ++i) V.push_back({std::cos(2 * add::pi * i / k), 0.0, std::sin(2 * add::pi * i / k)});
    V.push_back({0.0, 1.1, 0.0});
    V.push_back({0.05, -0.9, 0.1});
    std::vector<Face> F;
    for (int i = 0; i < k; ++i) F.push_back({i, k, (i + 1) % k});
    for (int i = 0; i < k; ++i) F.push_back({(i + 1) % k, k + 1, i});
    return from_faces(V, F, SIX);
}

static Mesh octa(double r = 1.0) {
    Points V = {{r, 0, 0}, {-r, 0, 0}, {0, r, 0}, {0, -r, 0}, {0, 0, r}, {0, 0, -r}};
    std::vector<Face> F = {{0, 2, 4}, {1, 4, 2}, {0, 4, 3}, {1, 3, 4}, {0, 5, 2}, {1, 2, 5}, {0, 3, 5}, {1, 5, 3}};
    return from_faces(V, F, SIX);
}

//: Eight boxes round a missing middle one, as drawn (not welded): a ring, once repaired.
static Mesh ring_of_boxes() {
    add::push();
    for (int i = 0; i < 3; ++i)
        for (int j = 0; j < 3; ++j)
            if (!(i == 1 && j == 1)) add::box({(double)i, 0, (double)j}, 1, SIX[(i + j) % 6]);
    return add::pop();
}

//: Three boxes in an L (as drawn).
static Mesh l_boxes() {
    add::push();
    add::box({0, 0, 0}, 1, "red");
    add::box({1, 0, 0}, 1, "green");
    add::box({0, 1, 0}, 1, "blue");
    return add::pop();
}

//: A box as 6 separate quads (24 corners).
static Mesh quads_apart() {
    Mesh M;
    Mesh C = cube();
    for (size_t k = 0; k < C.F.size(); ++k) {
        Points pts;
        for (int i : C.F[k]) pts.push_back(C.V[i]);
        M.add_polygon(pts, SIX[k]);
    }
    return M;
}

//: A cube with a repeated face and a degenerate one.
static Mesh messy() {
    Mesh M = cube();
    M.add_face({0, 4, 6, 2}, "red");
    M.add_face({1, 1, 3}, "blue");
    return M;
}

static Mesh prism_l() {
    return add::make([] { add::prism({{0, 0}, {2, 0}, {2, 1}, {1, 1}, {1, 2}, {0, 2}}, 1.0, "orange"); });
}

static Mesh prism_5() {
    return add::make([] { add::prism(add::profile_polygon(5, 1.0), 1.5, "gold"); });
}

static Mesh torus_8_5() {
    return add::make([] { add::torus({0, 0, 0}, 2.0, 0.6, 8, 5, "gold"); });
}

// -- the topology ----------------------------------------------------------------

CASE(topo_tables) {
    for (const Mesh& M : {patch(3, 2), pent_pyramid(), cube(), open_box()}) topo(as_topo(M));
    // a vertex where two fans touch, an isolated vertex (7), a triangle on an edge
    Points V = {{0.0, 0.0, 0.0}, {1.0, 0.0, 0.0}, {1.0, 1.0, 0.0}, {0.0, 1.0, 0.0}, {-1.0, 0.0, 0.2}, {-1.0, -1.0, 0.1},
                {0.0, -1.0, 0.3}, {5.0, 5.0, 5.0}, {0.5, 2.0, 0.0}};
    topo(Topo(V, {{0, 1, 2, 3}, {0, 4, 5, 6}, {3, 2, 8}}));
    // two faces that disagree on the way round their shared edge
    topo(Topo(V, {{0, 1, 2, 3}, {2, 3, 8}}));
}

CASE(topo_errors) {
    Points V = {{0.0, 0.0, 0.0}, {1.0, 0.0, 0.0}, {1.0, 1.0, 0.0}, {0.0, 1.0, 0.0}, {0.5, 0.5, 1.0}};
    error([&] { Topo(V, {{0, 1, 2}, {0, 1}}); });
    error([&] { Topo(V, {{0, 1, 2, 3}, {0, 1, 1, 4}}); });
    error([&] { Topo(V, {{0, 1, 2}, {0, 1, 4}, {1, 0, 3}}); });
    error([&] { Topo(V, {{0, 1, 0, 2}}); });
    error([&] { Topo(V, {{0, 1, 2, 0, 3, 4}}); });
    Topo T(V, {{0, 1, 2, 0, 3, 4}});                            // a face through vertex 0 twice is accepted
    topo(T);
}

CASE(cc_constants) {
    for (int N = 1; N < 13; ++N) {
        record(add::detail::cc_lambda(N));
        record(add::detail::cc_gamma(N));
    }
    record(add::detail::cc_gamma(100));
    error([] { add::detail::cc_lambda(0); });
}

CASE(cc_step) {
    for (const Mesh& M : {pent_pyramid(), patch(3, 2), open_box()}) {
        Topo T = as_topo(M);
        auto sp = add::detail::cc_subdivide(T);
        record(ints(sp.second));
        topo(sp.first);
    }
    // a vertex without faces and one with a single face are kept where they are
    Points V = {{0.0, 0.0, 0.0}, {1.0, 0.0, 0.0}, {1.0, 1.0, 0.0}, {0.0, 1.0, 0.0}, {3.0, 3.0, 3.0}, {-1.0, 0.0, 0.2},
                {-1.0, -1.0, 0.1}, {0.0, -1.0, 0.3}};
    auto sp = add::detail::cc_subdivide(Topo(V, {{0, 1, 2, 3}, {0, 5, 6, 7}}));
    record(ints(sp.second));
    shape(sp.first);
}

CASE(limit_positions) {
    for (const Mesh& M : {patch(), cube(), pent_pyramid(), open_box(), octa()})
        for (const Point& p : add::detail::cc_limit_positions(as_topo(M))) record(p);
    Points V = {{0.0, 0.0, 0.0}, {1.0, 0.0, 0.0}, {1.0, 1.0, 0.0}, {0.0, 1.0, 0.0}, {5.0, 5.0, 5.0}, {-1.0, 0.0, 0.2},
                {-1.0, -1.0, 0.1}, {0.0, -1.0, 0.3}};
    for (const Point& p : add::detail::cc_limit_positions(Topo(V, {{0, 1, 2, 3}, {0, 5, 6, 7}}))) record(p);
    // an inner vertex whose faces do not make one fan (one of them flipped)
    Topo T({{0.0, 0.0, 0.0}, {1.0, 0.0, 0.0}, {0.0, 1.0, 0.0}, {-1.0, 0.0, 0.0}, {0.0, -1.0, 0.0}},
           {{0, 1, 2}, {0, 2, 3}, {0, 4, 3}, {0, 1, 4}});
    for (const Point& p : add::detail::cc_limit_positions(T)) record(p);
}

CASE(limit_tangents) {
    for (const Mesh& M : {cube(), octa(), patch(4, 4), pent_pyramid()}) {
        Topo T = as_topo(M);
        for (int v = 0; v < (int)T.V.size(); ++v) {
            auto t = add::detail::cc_limit_tangents(T, v);
            if (!t) {
                record("None");
            } else {
                record(t->first);
                record(t->second);
            }
        }
    }
}

CASE(basis_bicubic) {
    for (double t : {0.0, 0.25, 1.0 / 3, 0.5, 0.9, 1.0, -0.5, 1.5}) record(floats(add::detail::bspline_basis(t)));
    Topo T = as_topo(patch(4, 3));
    auto P = add::detail::regular_stencil(T, 4);
    for (const Point2& uv : {Point2{0.0, 0.0}, Point2{0.5, 0.25}, Point2{1.0, 1.0}, Point2{0.1, 0.9}, Point2{1.0, 0.0}})
        record(add::detail::eval_bicubic(*P, uv[0], uv[1]));
}

CASE(stencils) {
    Topo T = as_topo(patch(4, 3));
    for (int f = 0; f < (int)T.F.size(); ++f) net(add::detail::regular_stencil(T, f));
    T = as_topo(patch(1, 1));                                  // one lone quad: every row reflected
    net(add::detail::regular_stencil(T, 0));
    T = as_topo(patch(1, 3));                                  // a strip one quad wide
    for (int f = 0; f < (int)T.F.size(); ++f) net(add::detail::regular_stencil(T, f));
    T = add::detail::topology_of(torus_8_5()).first;
    for (int f = 0; f < (int)T.F.size(); f += 7) net(add::detail::regular_stencil(T, f));
    T = as_topo(cube());
    net(add::detail::regular_stencil(T, 0));                   // valence 3: none
    Topo T1 = add::detail::cc_subdivide(T).first;
    Topo T2 = add::detail::cc_subdivide(T1).first;
    for (int f = 0; f < (int)T2.F.size(); f += 5) net(add::detail::regular_stencil(T2, f));
    T = as_topo(pent_pyramid());
    net(add::detail::regular_stencil(T, 0));                   // not a quad
    T = as_topo(open_box());
    T1 = add::detail::cc_subdivide(T).first;
    for (int f = 0; f < (int)T1.F.size(); ++f) net(add::detail::regular_stencil(T1, f));
}

CASE(neighbourhoods) {
    Topo T = as_topo(pent_pyramid());
    Topo T1 = add::detail::cc_subdivide(T).first;
    for (const std::pair<int, int>& fo : std::vector<std::pair<int, int>>{{0, 0}, {3, 2}, {7, 1}, {12, 3}, {19, 0}}) {
        Topo L = add::detail::neighbourhood(T1, fo.first, fo.second);
        shape(L);
        std::vector<int> b;
        for (size_t v = 0; v < L.boundary.size(); ++v) b.push_back(L.boundary[v] ? 1 : 0);
        record(ints(L.VE[0]) + " | " + ints(b));
    }
}

CASE(patch_trees) {
    Topo T = as_topo(cube());
    Topo T1 = add::detail::cc_subdivide(T).first;
    {
        add::detail::PatchTree tree(T1, 0);
        for (const Point2& uv : {Point2{0.0, 0.0}, Point2{0.5, 0.5}, Point2{1.0, 1.0}, Point2{0.3, 0.7}, Point2{1e-3, 2e-3},
                                 Point2{0.75, 0.1}, Point2{0.999, 0.0}, Point2{0.0, 0.6}, Point2{0.25, 0.25},
                                 Point2{0.0, 1e-9}})
            record(tree.eval(uv[0], uv[1]));
    }
    T = as_topo(pent_pyramid());
    T1 = add::detail::cc_subdivide(T).first;
    for (int f : {0, 4, 5, 9}) {
        add::detail::PatchTree tree(T1, f);
        for (const Point2& uv : {Point2{0.1, 0.2}, Point2{0.6, 0.05}, Point2{0.0, 0.0}, Point2{0.5, 0.5}, Point2{0.9, 0.95}})
            record(tree.eval(uv[0], uv[1]));
    }
    T = as_topo(open_box());
    T1 = add::detail::cc_subdivide(T).first;
    add::detail::PatchTree tree(T1, 1);
    for (const Point2& uv : {Point2{0.1, 0.2}, Point2{0.6, 0.05}, Point2{0.0, 0.0}, Point2{0.5, 0.5}})
        record(tree.eval(uv[0], uv[1]));
}

// -- the reparameterisation ------------------------------------------------------

CASE(nu_norms) {
    for (const Point2& ab : {Point2{0.0, 0.0}, Point2{0.3, 0.7}, Point2{1.0, 0.2}, Point2{0.5, 0.5}, Point2{1e-9, 0.999},
                             Point2{1.0, 1.0}, Point2{0.7, 0.3}})
        for (double p : {0.5, 1.0, 2.0, 3.7, 64.0, 64.5, 1e9}) record(add::detail::nu_norm(ab[0], ab[1], p));
    record(add::detail::nu_norm(0.2, 0.4, -1.0));
    error([] { add::detail::nu_norm(0.3, 0.4, 0.0); });
    error([] { add::detail::nu_norm(0.0, 0.4, -1.0); });
    error([] { add::detail::nu_norm(1e-200, 0.4, -2.0); });
}

CASE(domains) {
    const std::vector<Point2> xs = {{0.0, 0.0}, {0.3, 0.1}, {-0.2, 0.5}, {0.9, -0.3}, {1.0, 0.0}, {0.0, -1.0},
                                    {2.0, 2.0}, {-0.7, -0.05}, {0.5, 1e-17}, {-1.0, 0.0}, {-0.3, -1e-300}};
    for (int m : {3, 4, 5, 6, 8}) {
        const add::detail::PolygonDomain& dom = add::detail::PolygonDomain::get(m);
        record("m " + std::to_string(dom.m));
        for (const Point2& P : dom.P) record(P);
        for (const Point2& E : dom.E) record(E);
        for (int k = 0; k < m; ++k)
            for (const Point2& uv : {Point2{0.0, 0.0}, Point2{0.25, 0.5}, Point2{1.0, 1.0}, Point2{0.6, 0.1}})
                record(dom.kite_map(k, uv[0], uv[1]));
        for (const Point2& x : xs) {
            int k = dom.kite_of(x);
            record(k);
            record(dom.kite_inverse(k, x));
            record(dom.kite_inverse((k + 1) % m, x));
            std::vector<double> lam = dom.wachspress(x);
            record(floats(lam));
            for (int k2 = 0; k2 < m; ++k2) record(dom.corner_nu(lam, k2, 2.0));
            record(dom.corner_nu(lam, 0, 100.0));
        }
    }
    record(add::detail::PolygonDomain(7).E[3]);
}

CASE(reparams) {
    const std::vector<Point2> xs = {{0.0, 0.0}, {0.3, 0.1}, {-0.2, 0.5}, {0.9, -0.3}, {0.99, 0.01}, {0.5, 0.0},
                                    {-0.4, -0.4}, {1.0, 0.0}};
    struct Setup {
        int m;
        std::vector<double> gamma;
        double gc, p;
    };
    const std::vector<Setup> setups = {{3, {0.7776275156074476, 1.0, 1.2}, 1.0, 2.0},
                                       {5, {1.0, 1.0, 1.0, 1.0, 1.0}, 1.1593839643382764, 2.0},
                                       {6, {1.2711881726573797, 1.0, 1.0, 0.8, 1.0, 1.0}, 1.3, 3.0},
                                       {4, {1.0, 1.0, 1.0, 1.0}, 1.0, 2.0},
                                       {4, {0.7776275156074476, 1.0, 1.0, 1.0}, 1.0, 100.0},
                                       {3, {0.5, 0.5, 0.5}, 0.6, 1.0}};
    for (const Setup& s : setups) {
        const add::detail::PolygonDomain& dom = add::detail::PolygonDomain::get(s.m);
        add::detail::FaceReparam psi = add::detail::face_reparam(dom, s.gamma, s.gc, s.p);
        record(psi.trivial);
        for (const Point2& x : xs) record(psi(x));
    }
}

CASE(node_counts) {
    for (int m : {3, 4, 5, 6}) {
        std::vector<int> counts;
        for (int n = 0; n < 9; ++n) counts.push_back((int)add::detail::face_node_count(m, n));
        record(ints(counts));
    }
}

// -- the repair ------------------------------------------------------------------

CASE(cut_non_manifold) {
    for (const Mesh& M0 : {welded(two_cubes({1.0, 1.0, 0.0})), welded(two_cubes({1.0, 1.0, 1.0})), book()}) {
        Mesh M = M0.copy();
        add::detail::cut_non_manifold(M);
        dump(M);
    }
    // four faces on one edge, all the same way round (so no pair agrees), and a bow tie
    Points V = {{0.0, 0.0, 0.0}, {0.0, 1.0, 0.0}, {1.0, 0.0, 0.0}, {1.0, 1.0, 0.0}, {-1.0, 0.0, 0.0}, {-1.0, 1.0, 0.0},
                {0.0, 0.0, 1.0}, {0.0, 1.0, 1.0}, {0.0, 0.0, -1.0}, {0.0, 1.0, -1.0}};
    Mesh M = from_faces(V, {{0, 1, 3, 2}, {0, 1, 5, 4}, {0, 1, 7, 6}, {0, 1, 9, 8}}, SIX);
    add::detail::cut_non_manifold(M);
    dump(M);
    M = from_faces({{0.0, 0.0, 0.0}, {1.0, 0.0, 0.0}, {0.0, 1.0, 0.0}, {-1.0, 0.0, 0.0}, {0.0, -1.0, 0.0}},
                   {{0, 1, 2}, {0, 3, 4}}, {"red"});
    add::detail::cut_non_manifold(M);
    dump(M);
}

CASE(repairs) {
    for (const Mesh& M : {ring_of_boxes(), l_boxes(), two_cubes({1.0, 1.0, 0.0}), book(), messy(), quads_apart(), Mesh()})
        dump(add::detail::repair_for_subdivision(M));
}

CASE(topologies) {
    auto tm = add::detail::topology_of(ring_of_boxes(), false);
    record(add::detail::fmt("%d %d %d %d", (int)tm.first.V.size(), (int)tm.first.F.size(), (int)tm.first.E.size(),
                            (int)tm.second.V.size()));
    tm = add::detail::topology_of(ring_of_boxes());
    topo(tm.first);
    dump(tm.second);
}

// -- catmull_clark ---------------------------------------------------------------

CASE(cc_cube) {
    Mesh M = cube();
    for (int steps : {1, 2, 3}) result(add::catmull_clark(M, steps), "s" + std::to_string(steps));
}

CASE(cc_box_scene) {
    add::box({0, 0, 0}, 2, "red");
    add::mesh(add::catmull_clark(add::layer(), 3));
    save_case();
}

CASE(cc_prism) {
    Mesh M = prism_5();
    result(add::catmull_clark(M, 1), "s1");
    result(add::catmull_clark(M, 2), "s2");
    Mesh L = prism_l();
    result(add::catmull_clark(L, 2), "L");
}

CASE(cc_tetra) {
    Mesh M = add::make([] { add::tetrahedron({0, 0, 0}, 1.0, "blue"); });
    for (int steps : {1, 2, 3}) result(add::catmull_clark(M, steps), "s" + std::to_string(steps));
}

CASE(cc_patch) {
    for (int steps : {1, 2}) result(add::catmull_clark(patch(), steps), "s" + std::to_string(steps));
    result(add::catmull_clark(patch(), 2, false), "raw");
    result(add::catmull_clark(open_box(), 2), "openbox");
}

CASE(cc_tri_pent) {
    for (int steps : {1, 2}) result(add::catmull_clark(pent_pyramid(), steps), "s" + std::to_string(steps));
    Mesh D = add::make([] { add::dodecahedron({0, 0, 0}, 1.0, "gold"); });
    Mesh I = add::make([] { add::icosahedron({3, 0, 0}, 1.0, "sky"); });
    result(add::catmull_clark(add::merge({D, I}), 1), "di");
}

CASE(cc_nonmanifold) {
    result(add::catmull_clark(two_cubes({1.0, 1.0, 0.0})), "edge");
    result(add::catmull_clark(two_cubes({1.0, 1.0, 1.0})), "vertex");
    result(add::catmull_clark(book(), 2), "book");
    result(add::catmull_clark(welded(two_cubes({1.0, 1.0, 1.0})), 1, false), "vertex_raw");
    result(add::catmull_clark(ring_of_boxes(), 2), "ring");
}

CASE(cc_errors) {
    error([] { add::catmull_clark(welded(two_cubes({1.0, 1.0, 0.0})), 1, false); });
    error([] { add::catmull_clark(book(), 1, false); });
    Points V = {{0.0, 0.0, 0.0}, {1.0, 0.0, 0.0}, {1.0, 1.0, 0.0}, {0.0, 1.0, 0.0}};
    error([&] { add::catmull_clark(from_faces(V, {{0, 1, 2}, {0, 1}}), 1, false); });
    error([&] { add::catmull_clark(from_faces(V, {{0, 1, 1, 2}}), 1, false); });
    error([&] { add::catmull_clark(from_faces(V, {{0, 1, 2, 3}, {0, 1, 0, 2}}), 1, false); });
}

CASE(cc_colours) {
    Mesh M = cube({-1.0, -0.75, -0.5}, {1.0, 1.25, 0.9},
                  {"red", add::transparent("green", 0.25), Color(1, 2, 3), "#abcdef80", "white", "black"});
    Mesh C = add::catmull_clark(M, 2);
    result(C);
    add::obj(parity::current() + ".obj", C);
    Mesh T = add::catmull_clark(add::texture(cube(), "wood.png", "box"), 1);
    dump(T);
    add::obj(parity::current() + "_tex.obj", T);
}

CASE(cc_steps) {
    Mesh M = cube();
    result(add::catmull_clark(M, 0), "s0");
    result(add::subdivide(M, 2), "sub2");
    result(add::subdivide(pent_pyramid(), 1, false), "sub_raw");
    result(add::catmull_clark(M, -1), "neg");
    result(add::catmull_clark(Mesh()), "empty");
}

CASE(cc_apart) {
    Mesh M = cube();
    M.add_vertex({5, 5, 5});
    result(add::catmull_clark(M, 1, false), "isolated_raw");
    result(add::catmull_clark(M, 1, true), "isolated");
    result(add::catmull_clark(quads_apart(), 1, false), "quads_raw");
    result(add::catmull_clark(quads_apart(), 1), "quads");
    result(add::catmull_clark(messy(), 1), "messy");
}

// -- smooth ----------------------------------------------------------------------

CASE(sm_cube) {
    Mesh M = cube();
    for (int n = 1; n < 7; ++n) result(add::smooth(M, n), "n" + std::to_string(n));
}

CASE(sm_cube_plain) {
    Mesh M = cube();
    for (int n : {1, 2, 3, 4}) result(add::smooth(M, n, false), "n" + std::to_string(n));
}

CASE(sm_octa) {
    Mesh M = octa();
    for (int n = 1; n < 7; ++n) result(add::smooth(M, n), "n" + std::to_string(n));
    result(add::smooth(M, 3, true, false), "nocentre");
    result(add::smooth(M, 4, false), "plain");
}

CASE(sm_p_scale) {
    Mesh M = pent_pyramid();
    result(add::smooth(M, 3, true, true, 1.0), "p1");
    result(add::smooth(M, 3, true, true, 3.5), "p3_5");
    result(add::smooth(M, 3, true, true, 100.0), "p100");
    result(add::smooth(M, 4, true, true, 2.0, 0.5), "s0_5");
    result(add::smooth(M, 4, true, true, 2.0, 2.0), "s2");
    result(add::smooth(M, 4, true, true, 2.0, 0.0), "s0");
    result(add::smooth(M, 5, true, false, 1.5, 1.25), "mix");
}

CASE(sm_centre) {
    Mesh M = prism_5();
    for (int n : {2, 3, 4}) {
        result(add::smooth(M, n, true, true), "on" + std::to_string(n));
        result(add::smooth(M, n, true, false), "off" + std::to_string(n));
        result(add::smooth(M, n, false), "plain" + std::to_string(n));
    }
}

CASE(sm_l_block) {
    result(add::smooth(l_boxes(), 3), "boxes3");
    result(add::smooth(l_boxes(), 4), "boxes4");
    Mesh L = prism_l();
    result(add::smooth(L, 3), "prism3");
    result(add::smooth(L, 2, false), "prism_plain");
}

CASE(sm_ring) {
    Mesh R = ring_of_boxes();
    result(add::smooth(R, 2), "n2");
    result(add::smooth(R, 5), "n5");
    result(add::smooth(R, 6, false), "plain6");
}

CASE(sm_valence) {
    result(add::smooth(add::make([] { add::icosahedron({0, 0, 0}, 1.0, "white"); }), 3), "icosa");
    result(add::smooth(add::make([] { add::sphere({0, 0, 0}, 1.0, 10, "sky", 1); }), 2), "geo");
    result(add::smooth(bipyramid(6), 4), "bipyramid6");
    result(add::smooth(bipyramid(5), 3), "bipyramid5");
    result(add::smooth(add::make([] { add::dodecahedron({0, 0, 0}, 1.0, "gold"); }), 3), "dodeca");
    result(add::smooth(add::make([] { add::cylinder({0, 0, 0}, {0, 2, 0}, 0.5, 8, "red"); }), 3), "cylinder");
}

CASE(sm_open) {
    for (int n : {1, 2, 3, 4}) result(add::smooth(patch(), n), "patch" + std::to_string(n));
    result(add::smooth(open_box(), 3), "openbox3");
    result(add::smooth(open_box(), 4, false), "openbox_plain");
    result(add::smooth(add::make([] { add::tube({0, 0, 0}, {0, 2, 0}, 0.5, 8, "teal"); }), 3), "tube");
    Mesh G = add::make([] {
        add::grid({0, 0, 0}, {2, 2}, 4, 3, "lime", [](double x, double z) { return 0.2 * std::sin(3 * x) * std::cos(2 * z); });
    });
    result(add::smooth(G, 4), "grid");
    result(add::smooth(book(), 3), "book");
    result(add::smooth(patch(1, 1), 5), "lone_quad");
}

CASE(sm_misc) {
    result(add::smooth(add::make([] { add::tetrahedron({0, 0, 0}, 1.0, "red"); }), 2), "tetra2");
    result(add::smooth(torus_8_5(), 3), "torus");
    result(add::smooth(add::make([] { add::uvsphere({0, 0, 0}, 1.0, 8, 4, "blue"); }), 2), "uvsphere");
    result(add::smooth(add::make([] { add::frame({0, 0, 0}, 2.0, 0.4, "brown"); }), 2), "frame");
    result(add::smooth(two_cubes({1.0, 1.0, 0.0}), 3), "nm_edge");
    result(add::smooth(two_cubes({1.0, 1.0, 1.0}), 2), "nm_vertex");
    result(add::smooth(cube(), 3, true, true, 2.0, 1.0, false), "norepair");
    result(add::smooth(quads_apart(), 2, true, true, 2.0, 1.0, false), "apart_raw");
    result(add::smooth(Mesh(), 3), "empty");
}

CASE(sm_errors) {
    error([] { add::smooth(cube(), 0); });
    error([] { add::smooth(cube(), -3); });
    error([] { add::smooth(cube(), 3, true, true, 0.0); });
    error([] { add::smooth(book(), 3, true, true, 2.0, 1.0, false); });
    error([] { add::smooth(cube(), 3, true, true, 2.0, 1e4); });
    error([] { add::smooth(cube(), 3, true, true, -1.0); });
    error([] { add::smooth(cube(), 3, true, true, 2.0, 1.0); });
}

CASE(sm_raw_shapes) {
    Mesh M = cube();
    std::reverse(M.F[0].begin(), M.F[0].end());                // one face the wrong way round
    result(add::smooth(M, 3, true, true, 2.0, 1.0, false), "flipped");
    result(add::catmull_clark(M, 2, false), "flipped_cc");
    result(add::smooth(welded(two_cubes({1.0, 1.0, 1.0})), 3, true, true, 2.0, 1.0, false), "touching_raw");
    result(add::smooth(cube(), 3, true, true, 2.0, 1000.0), "s1000");
}

CASE(sm_colours) {
    Mesh M = cube({-1.0, -0.75, -0.5}, {1.0, 1.25, 0.9},
                  {"red", add::transparent("green", 0.25), Color(1, 2, 3), "#abcdef80", "white", "black"});
    Mesh S = add::smooth(M, 3);
    result(S);
    add::obj(parity::current() + ".obj", S);
    add::mesh(add::smooth(add::make([] { add::box({0, 0, 0}, 2, "red"); }), 5));
    save_case();
}

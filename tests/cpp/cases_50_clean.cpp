#include "parity.hpp"

#include <sstream>

using add::Color;
using add::Face;
using add::Mesh;
using add::Point;
using add::Point2;
using add::Points;
using add::Profile;

// -- helpers (the Python twin has the same ones) --------------------------------

//: add::save(<case>.<ext>, M) for an .off or .obj path: clean(M, 1e-6), then the writer --
//: the very steps of add::save, which cannot be linked in a development header yet (it also
//: needs limit_colors, write_ply and write_stl, from sections being ported now).  The Python
//: twin calls add.save itself.  At integration this can simply be parity::save_as(ext, M).
static void save_file(const std::string& ext, const Mesh& M) { parity::save_as(ext, M); }   // (add::save)

template <class F>
static bool raises(F fn) {
    try {
        fn();
    } catch (const std::exception&) {
        return true;
    }
    return false;
}

//: What fn prints (and what it returns).
template <class F>
static std::pair<std::string, bool> capture(F fn) {
    std::ostringstream buf;
    std::streambuf* old = std::cout.rdbuf(buf.rdbuf());
    bool value = false;
    try {
        value = fn();
    } catch (...) {
        std::cout.rdbuf(old);
        throw;
    }
    std::cout.rdbuf(old);
    return {buf.str(), value};
}

static std::string face_str(const std::vector<int>& f) {
    std::string s;
    for (size_t i = 0; i < f.size(); ++i) s += (i ? " " : "") + std::to_string(f[i]);
    return s;
}
static std::string face_str(const std::array<int, 3>& f) { return face_str(std::vector<int>(f.begin(), f.end())); }

//: Every number of a mesh, at full precision.
static void dump(const Mesh& M) {
    record("V " + std::to_string(M.V.size()));
    for (const Point& p : M.V) record(p);
    record("F " + std::to_string(M.F.size()));
    for (size_t k = 0; k < M.F.size() && k < M.C.size(); ++k) {
        record(face_str(M.F[k]));
        record(M.C[k]);
    }
    if (!M.has_uv) {
        record("no uv");
    } else {
        for (const auto& t : M.UV) {
            if (t.empty()) record("none");
            else record(t);
        }
    }
}

static void record_report(const add::CleanReport& info) {
    record(add::detail::fmt("removed %d vertices, %d faces; cut %d; split %d", info.vertices_removed,
                            info.faces_removed, info.faces_cut, info.faces_split));
}

static void record_polys(const std::vector<Profile>& polys) { record(polys); }

static void record_list(const std::array<double, 4>& xs) { record(std::vector<double>(xs.begin(), xs.end())); }

//: A box as 8 shared corners and 6 outward quads.
static void cuboid(Mesh& M, const Point& c, const Point& s, const Color& color = add::DEFAULT_COLOR) {
    double x0 = c[0] - s[0] / 2.0, y0 = c[1] - s[1] / 2.0, z0 = c[2] - s[2] / 2.0;
    double x1 = c[0] + s[0] / 2.0, y1 = c[1] + s[1] / 2.0, z1 = c[2] + s[2] / 2.0;
    int base = (int)M.V.size();
    for (const Point& p : {Point{x0, y0, z0}, Point{x1, y0, z0}, Point{x1, y1, z0}, Point{x0, y1, z0},
                           Point{x0, y0, z1}, Point{x1, y0, z1}, Point{x1, y1, z1}, Point{x0, y1, z1}})
        M.add_vertex(p);
    for (const Face& f : {Face{0, 3, 2, 1}, Face{4, 5, 6, 7}, Face{0, 1, 5, 4}, Face{2, 3, 7, 6}, Face{1, 2, 6, 5},
                          Face{0, 4, 7, 3}}) {
        Face g;
        for (int i : f) g.push_back(base + i);
        M.add_face(g, color);
    }
}

//: A box as 6 separate quads (24 corners: clean() has to weld them).
static void cuboid_polys(Mesh& M, const Point& c, const Point& s, const Color& color = add::DEFAULT_COLOR) {
    double x0 = c[0] - s[0] / 2.0, y0 = c[1] - s[1] / 2.0, z0 = c[2] - s[2] / 2.0;
    double x1 = c[0] + s[0] / 2.0, y1 = c[1] + s[1] / 2.0, z1 = c[2] + s[2] / 2.0;
    Points P = {{x0, y0, z0}, {x1, y0, z0}, {x1, y1, z0}, {x0, y1, z0},
                {x0, y0, z1}, {x1, y0, z1}, {x1, y1, z1}, {x0, y1, z1}};
    for (const Face& f : {Face{0, 3, 2, 1}, Face{4, 5, 6, 7}, Face{0, 1, 5, 4}, Face{2, 3, 7, 6}, Face{1, 2, 6, 5},
                          Face{0, 4, 7, 3}}) {
        Points pts;
        for (int i : f) pts.push_back(P[i]);
        M.add_polygon(pts, color);
    }
}

//: A box whose every face carries texture coordinates.
static void textured_cuboid(Mesh& M, const Point& c, const Point& s, const Color& color) {
    double x0 = c[0] - s[0] / 2.0, y0 = c[1] - s[1] / 2.0, z0 = c[2] - s[2] / 2.0;
    double x1 = c[0] + s[0] / 2.0, y1 = c[1] + s[1] / 2.0, z1 = c[2] + s[2] / 2.0;
    int base = (int)M.V.size();
    for (const Point& p : {Point{x0, y0, z0}, Point{x1, y0, z0}, Point{x1, y1, z0}, Point{x0, y1, z0},
                           Point{x0, y0, z1}, Point{x1, y0, z1}, Point{x1, y1, z1}, Point{x0, y1, z1}})
        M.add_vertex(p);
    std::vector<Point2> uv = {{0.0, 0.0}, {1.0, 0.0}, {1.0, 1.0}, {0.0, 1.0}};
    for (const Face& f : {Face{0, 3, 2, 1}, Face{4, 5, 6, 7}, Face{0, 1, 5, 4}, Face{2, 3, 7, 6}, Face{1, 2, 6, 5},
                          Face{0, 4, 7, 3}}) {
        Face g;
        for (int i : f) g.push_back(base + i);
        M.add_face(g, color, uv);
    }
}

//: A flat rectangle at height y, facing up (+Y) or down.
static void quad_xz(Mesh& M, double x0, double z0, double x1, double z1, double y, bool up = true,
                    const Color& color = add::DEFAULT_COLOR) {
    Points pts = {{x0, y, z0}, {x0, y, z1}, {x1, y, z1}, {x1, y, z0}};
    if (!up) std::reverse(pts.begin(), pts.end());
    M.add_polygon(pts, color);
}

//: A flat rectangle at depth z, facing +Z (front) or -Z.
static void quad_xy(Mesh& M, double x0, double y0, double x1, double y1, double z, bool front = true,
                    const Color& color = add::DEFAULT_COLOR) {
    Points pts = {{x0, y0, z}, {x1, y0, z}, {x1, y1, z}, {x0, y1, z}};
    if (!front) std::reverse(pts.begin(), pts.end());
    M.add_polygon(pts, color);
}

//: A copy turned by ax around X, then by ay around Y (through the origin).
static Mesh turned(const Mesh& M, double ax, double ay) {
    Mesh out;
    out.F = M.F;
    out.C = M.C;
    out.UV = M.UV;
    out.has_uv = M.has_uv;
    double ca = std::cos(ax), sa = std::sin(ax);
    double cb = std::cos(ay), sb = std::sin(ay);
    for (const Point& p : M.V) {
        double x = p[0], y = p[1] * ca - p[2] * sa, z = p[1] * sa + p[2] * ca;
        out.V.push_back({x * cb + z * sb, y, z * cb - x * sb});
    }
    return out;
}

static void l_shape(Mesh& M, const Point2& c, const Color& color = add::DEFAULT_COLOR, double z = 0.0) {
    double x = c[0], y = c[1];
    M.add_polygon({{x, y, z}, {x + 2, y, z}, {x + 2, y + 1, z}, {x + 1, y + 1, z}, {x + 1, y + 2, z}, {x, y + 2, z}},
                  color);
}

static Points star_points(double cx, double cy, int n, double r1, double r2, double z = 0.0, double phase = 0.0) {
    Points pts;
    for (int i = 0; i < 2 * n; ++i) {
        double a = phase + add::pi * i / n;
        double r = i % 2 == 0 ? r1 : r2;
        pts.push_back({cx + r * std::cos(a), cy + r * std::sin(a), z});
    }
    return pts;
}

//: n x m unit quads in the XZ plane sharing their corners, facing up.
static void grid_of_quads(Mesh& M, int n, int m, const std::vector<Color>& colors) {
    int base = (int)M.V.size();
    for (int i = 0; i < n + 1; ++i)
        for (int j = 0; j < m + 1; ++j) M.add_vertex({i * 1.0, 0.0, j * 1.0});
    for (int i = 0; i < n; ++i)
        for (int j = 0; j < m; ++j) {
            int a = base + i * (m + 1) + j;
            M.add_face({a, a + 1, a + m + 2, a + m + 1}, colors[(i + j) % colors.size()]);
        }
}

static const double NaN = std::numeric_limits<double>::quiet_NaN();
static const double Inf = std::numeric_limits<double>::infinity();

// -- the helpers already written (wave 0) ----------------------------------------

CASE(cell_keys) {
    double tol = 1e-7;
    for (const Point& p : {Point{0.0, 0.0, 0.0}, Point{1e-7, 2.4e-8, -2.6e-8}, Point{0.12345678, -3.00000004, 7.5e-8},
                           Point{5e-8, 5.00001e-8, 4.99999e-8}, Point{-1.23e-7, 1.77e-7, 123.456}}) {
        std::string s;
        for (const auto& k : add::detail::cell_keys(p, tol))
            s += (s.empty() ? "" : " / ") + add::detail::fmt("%lld %lld %lld", k.i, k.j, k.k);
        record(s);
    }
    record(raises([&] { add::detail::cell_keys({NaN, 0.0, 0.0}, tol); }));
    record(raises([&] { add::detail::cell_keys({0.0, Inf, 0.0}, tol); }));
}

CASE(weld_near) {
    Mesh M;
    M.add_polygon({{0, 0, 0}, {1, 0, 0}, {1, 1, 0}}, "red");
    M.add_polygon({{1 + 4e-8, 1e-8, 0}, {0, -3e-8, 5e-8}, {1, 0, 1}}, "blue");
    M.add_polygon({{1.00000009, 0.99999991, 0}, {1, 1, 1}, {1, 0, 1 + 2e-7}});
    M.add_polygon({{0.5, 0.5, 0.5}, {0.5 + 0.9e-7, 0.5, 0.5}, {0.5, 0.5 - 1.2e-7, 0.5}});
    record(add::detail::weld(M, 1e-7));
    dump(M);
    Mesh N;
    N.add_polygon({{0, 0, 0}, {1, 0, 0}, {0.9999, 0, 0}});
    record(add::detail::weld(N, 1e-3));
    dump(N);
    Mesh B;
    B.add_polygon({{NaN, 0, 0}, {1, 0, 0}, {0, 1, 0}});
    record(raises([&] { add::detail::weld(B, 1e-7); }));
}

CASE(keep_faces_uv) {
    Mesh M;
    M.add_polygon({{0, 0, 0}, {1, 0, 0}, {1, 1, 0}}, "red");
    M.add_face({0, 1, 2}, "blue", {{0, 0}, {1, 0}, {1, 1}});
    M.add_face({2, 1, 0}, "green");
    M.add_face({0, 2, 1}, "white", {{0.5, 0.25}, {0.75, 0}, {1, 1}});
    record(add::detail::keep_faces(M, {3, 1, 2}));
    dump(M);
    Mesh N;
    N.add_polygon({{0, 0, 0}, {1, 0, 0}, {1, 1, 0}}, "red");
    N.add_polygon({{0, 0, 1}, {1, 0, 1}, {1, 1, 1}}, "blue");
    record(add::detail::keep_faces(N, {1}));
    dump(N);
}

CASE(not_finite) {
    Mesh M;
    M.add_polygon({{0, 0, 0}, {1, 0, 0}, {1, 1, 0}}, "red");
    M.add_polygon({{0, 0, 1}, {NaN, 0, 1}, {1, 1, 1}}, "blue");
    M.add_polygon({{0, 0, 2}, {1, Inf, 2}, {1, 1, 2}, {0, 1, -Inf}}, "green");
    M.add_polygon({{0, 0, 3}, {1, 0, 3}, {1, 1, 3}}, "white");
    M.add_vertex({NaN, NaN, 0});
    std::set<int> bad = add::detail::not_finite(M);
    record(face_str(std::vector<int>(bad.begin(), bad.end())));
    record(add::detail::drop_not_finite(M));
    dump(M);
    Mesh N;
    N.add_polygon({{1e308, 1e308, 1e308}, {1e308, 0, 0}, {0, 1e308, 0}});
    bad = add::detail::not_finite(N);
    record(face_str(std::vector<int>(bad.begin(), bad.end())));
    record(add::detail::drop_not_finite(N));
    record(N.F.size());
}

CASE(split_repeats) {
    std::vector<Point2> uv8;
    for (int i = 0; i < 8; ++i) uv8.push_back({i * 0.5, 1.0 - i * 0.25});
    std::vector<Point2> uv4 = {{0, 0}, {1, 0}, {1, 1}, {0, 1}};
    std::vector<Point2> uv3 = {{0, 0}, {1, 1}, {2, 2}};
    std::vector<std::pair<Face, const std::vector<Point2>*>> tests = {
        {{0, 1, 2, 0, 3, 4}, nullptr}, {{0, 1, 1, 2, 3, 3, 0}, nullptr}, {{5, 6, 7, 5, 8, 9, 7, 10}, &uv8},
        {{1, 2, 3, 4}, &uv4},          {{1, 2, 1, 2}, nullptr},          {{3, 3, 3}, &uv3}};
    for (const auto& t : tests) {
        auto pieces = add::detail::split_repeats(t.first, t.second);
        record(pieces.size());
        for (const auto& piece : pieces) {
            record(face_str(piece.first));
            if (!t.second) record("none");
            else record(piece.second);
        }
    }
}

CASE(drop_degenerate) {
    Mesh M;
    for (int i = 0; i < 12; ++i) M.add_vertex({std::cos(i * 0.5), std::sin(i * 0.5), 0.1 * i});
    M.add_vertex({0, 0, 0});
    M.add_vertex({1, 1, 1});
    M.add_vertex({2, 2, 2});
    M.add_face({0, 1, 2}, "red");
    M.add_face({0, 1, 1, 2, 2}, "blue");                      // repeated corners
    M.add_face({0, 1, 2, 0, 3, 4, 5}, "green");               // pinched at 0
    M.add_face({12, 13, 14}, "white");                        // a straight line: no area
    M.add_face({3, 4}, "yellow");                             // too short
    M.add_face({6, 7, 8, 7}, "cyan");                         // back and forth
    M.add_face({9, 10, 11, 9, 9}, "magenta");
    M.add_face({}, "orange");
    M.add_face({1, 2, 3, 4, 1, 5, 6, 7, 5, 8}, "purple");     // pinched twice
    record(add::detail::drop_degenerate(M));
    dump(M);
    Mesh T;
    for (int i = 0; i < 8; ++i) T.add_vertex({std::cos(i * 0.8), std::sin(i * 0.8), 0.0});
    T.add_face({0, 1, 2, 3}, "red", {{0, 0}, {1, 0}, {1, 1}, {0, 1}});
    T.add_face({0, 1, 2, 0, 4, 5}, "blue", {{0, 0}, {1, 0}, {1, 1}, {0.5, 0.5}, {0, 1}, {0.25, 0.75}});
    T.add_face({4, 5, 5, 6}, "green");
    T.add_face({6, 7, 7, 0}, "white", {{0.1, 0.2}, {0.3, 0.4}, {0.5, 0.6}, {0.7, 0.8}});
    record(add::detail::drop_degenerate(T, 1e-9));
    dump(T);
}

CASE(dedup_faces) {
    Mesh M;
    cuboid(M, {0, 0, 0}, {1, 1, 1}, "red");
    M.add_face({3, 2, 1, 0}, "blue");                         // the bottom, turned round
    M.add_face({2, 1, 0, 3}, "green");                        // the bottom again, rotated
    M.add_face({4, 5, 6, 7}, "white");
    M.add_face({4, 5, 6}, "white");
    record(add::detail::dedup_faces(M));
    dump(M);
}

CASE(drop_internal) {
    Mesh M;
    cuboid(M, {0, 0, 0}, {1, 1, 1}, "red");
    cuboid(M, {1, 0, 0}, {1, 1, 1}, "blue");
    add::detail::weld(M);
    record(add::detail::drop_internal(M));
    dump(M);
    Mesh N;
    for (const Point& p : {Point{0, 0, 0}, Point{1, 0, 0}, Point{1, 1, 0}, Point{0, 1, 0}}) N.add_vertex(p);
    N.add_face({0, 1, 2, 3}, "red");
    N.add_face({3, 2, 1, 0}, "blue");
    N.add_face({1, 2, 3, 0}, "green");
    N.add_face({0, 3, 2, 1}, "white");
    N.add_face({2, 3, 0, 1}, "yellow");
    N.add_face({0, 1, 2}, "cyan");
    record(add::detail::drop_internal(N));
    dump(N);
    Mesh E;
    E.add_polygon({{0, 0, 0}, {1, 0, 0}, {1, 1, 0}});
    record(add::detail::drop_internal(E));
    E.add_face({}, "red");
    E.add_face({}, "blue");
    record(raises([&] { add::detail::drop_internal(E); }));
}

CASE(winding) {
    for (const Face& f : {Face{0, 1, 2}, Face{2, 1, 0}, Face{5, 3, 9, 4}, Face{4, 9, 3, 5}, Face{7}, Face{3, 1, 1, 2},
                          Face{1, 3, 1, 0, 2}})
        record(add::detail::winding(f));
    record(raises([] { add::detail::winding({}); }));
}

CASE(drop_unused) {
    Mesh M;
    for (int i = 0; i < 10; ++i) M.add_vertex({i * 1.0, i * i * 0.5, -i * 1.0});
    M.add_face({7, 2, 9}, "red");
    M.add_face({2, 4, 7, 5}, "blue");
    record(add::detail::drop_unused(M));
    dump(M);
    record(add::detail::drop_unused(M));
}

CASE(poly_area2) {
    for (const Profile& pts : {Profile{{0, 0}, {1, 0}, {1, 1}, {0, 1}}, Profile{{0, 0}, {0, 1}, {1, 1}, {1, 0}},
                               Profile{{0.1, 0.2}, {3.3, -0.7}, {2.25, 4.125}, {-1.5, 2.0}, {0.0, 1.0}},
                               Profile{{1, 1}, {2, 2}}, Profile{{5, 5}}, Profile{}})
        record(add::detail::poly_area2(pts));
}

// -- the 2D pieces of the overlap machinery ---------------------------------------

CASE(clip_half) {
    Profile sq = {{0.0, 0.0}, {2.0, 0.0}, {2.0, 2.0}, {0.0, 2.0}};
    Profile tri = {{0.0, 0.0}, {3.0, 0.5}, {1.0, 2.5}};
    std::vector<std::pair<Point2, Point2>> lines = {{{1.0, -1.0}, {1.0, 3.0}}, {{0.0, 0.5}, {4.0, 1.5}},
                                                    {{-1.0, 1.0}, {3.0, 1.0}}, {{5.0, 0.0}, {5.0, 1.0}},
                                                    {{0.0, 0.0}, {2.0, 2.0}},  {{2.0, 0.0}, {2.0, 2.0}}};
    for (const Profile& pts : {sq, tri})
        for (const auto& ab : lines)
            for (bool keep_left : {true, false}) record(add::detail::clip_half(pts, ab.first, ab.second, keep_left));
    record(add::detail::clip_half({}, {0.0, 0.0}, {1.0, 0.0}, true));
}

CASE(convex_minus) {
    Profile A = {{0.0, 0.0}, {4.0, 0.0}, {4.0, 3.0}, {0.0, 3.0}};
    std::vector<Profile> Bs = {{{1.0, 1.0}, {2.0, 1.0}, {2.0, 2.0}, {1.0, 2.0}},         // inside A
                               {{3.0, 1.0}, {5.0, 1.0}, {5.0, 2.0}, {3.0, 2.0}},         // over one side
                               {{4.0, 0.0}, {6.0, 0.0}, {6.0, 3.0}, {4.0, 3.0}},         // touching along a side
                               {{7.0, 0.0}, {8.0, 0.0}, {8.0, 1.0}},                     // far away
                               {{-1.0, -1.0}, {5.0, -1.0}, {5.0, 4.0}, {-1.0, 4.0}},     // covering all of A
                               {{2.0, -1.0}, {5.0, 1.5}, {2.0, 4.0}},                    // a triangle across
                               {{0.0, 0.0}, {4.0, 0.0}, {4.0, 3.0}, {0.0, 3.0}},         // A itself
                               {{1.0, 1.0}, {1.0 + 1e-6, 1.0}, {1.0, 1.0 + 1e-6}}};      // a speck
    for (const Profile& B : Bs)
        for (double eps : {1e-9, 1e-3}) {
            bool untouched = false;
            std::vector<Profile> pieces = add::detail::convex_minus(A, B, eps, &untouched);
            record(untouched);
            record_polys(pieces);
        }
}

CASE(ears) {
    Profile L = {{0.0, 0.0}, {2.0, 0.0}, {2.0, 1.0}, {1.0, 1.0}, {1.0, 2.0}, {0.0, 2.0}};
    Profile star;
    for (const Point& p : star_points(0.0, 0.0, 5, 2.0, 0.8)) star.push_back({p[0], p[1]});
    Profile comb = {{0.0, 0.0}, {5.0, 0.0}, {5.0, 2.0}, {4.0, 2.0}, {4.0, 1.0}, {3.0, 1.0}, {3.0, 2.0},
                    {2.0, 2.0}, {2.0, 1.0}, {1.0, 1.0}, {1.0, 2.0}, {0.0, 2.0}};
    Profile square = {{0.0, 0.0}, {1.0, 0.0}, {1.0, 1.0}, {0.0, 1.0}};
    Profile straight = {{0.0, 0.0}, {1.0, 0.0}, {2.0, 0.0}, {2.0, 1.0}, {0.0, 1.0}};
    Profile bowtie = {{0.0, 0.0}, {2.0, 2.0}, {2.0, 0.0}, {0.0, 2.0}};
    Profile tri(square.begin(), square.begin() + 3);
    for (const Profile& pts : {L, star, comb, square, straight, bowtie, tri}) {
        record_polys(add::detail::ears(pts));
        record_polys(add::detail::convex_pieces(pts));
        auto tris = add::detail::ear_triangles(pts);
        if (!tris) {
            record("none");
        } else {
            std::string s;
            for (size_t i = 0; i < tris->size(); ++i) s += (i ? " / " : "") + face_str((*tris)[i]);
            record(s);
        }
    }
}

CASE(is_concave) {
    Mesh M;
    l_shape(M, {0, 0}, "red");
    M.add_polygon(star_points(5.0, 0.0, 6, 2.0, 1.0), "blue");
    M.add_polygon({{0, 0, 5}, {1, 0, 5}, {1, 1, 5}, {0, 1, 5}}, "green");
    M.add_polygon({{0, 0, 6}, {0, 1, 6}, {1, 1, 6}, {1, 0, 6}}, "white");
    M.add_polygon({{0, 0, 7}, {1, 0, 7}, {2, 0, 7}, {2, 1, 7}, {0, 1, 7}}, "yellow");
    M.add_polygon({{0, 0, 8}, {2, 2, 8}, {2, 0, 8}, {0, 2, 8}}, "cyan");
    M.add_polygon({{0, 0, 9}, {1, 0, 9}, {2, 0, 9}, {3, 0, 9}}, "magenta");
    M.add_polygon({{0, 0, 10}, {1, 0, 10}, {1, 1, 10}}, "orange");
    M.add_polygon({{0, 0, 11}, {2, 0, 11}, {2, 2, 11}, {1.0, 1.0 - 1e-12, 11}, {0, 2, 11}}, "pink");
    for (const Face& f : M.F) record(add::detail::is_concave(M, f));
    record(add::detail::is_concave(M, M.F[0], Point{0.0, 0.0, -1.0}));
    record(add::detail::is_concave(M, M.F[2], Point{0.0, 0.0, -1.0}));
    record(add::detail::is_concave(M, M.F[0], Point{0.0, 0.0, 0.0}));
    record(add::concave_faces(M));
    Mesh T = turned(M, 0.7, -1.9);
    record(add::concave_faces(T));
    add::mesh(M);
    record(add::concave_faces());
}

CASE(split_concave) {
    Mesh M;
    l_shape(M, {0, 0}, "red");
    M.add_polygon(star_points(5.0, 0.0, 5, 2.0, 0.7), "blue");
    M.add_polygon({{0, 0, 5}, {1, 0, 5}, {1, 1, 5}, {0, 1, 5}}, "green");
    Points pts = {{0, 0, 6}, {5, 0, 6}, {5, 2, 6}, {4, 2, 6}, {4, 1, 6}, {3, 1, 6}, {3, 2, 6},
                  {2, 2, 6}, {2, 1, 6}, {1, 1, 6}, {1, 2, 6}, {0, 2, 6}};
    std::reverse(pts.begin(), pts.end());
    M.add_polygon(pts, "white");                              // a comb, clockwise
    M.add_polygon({{0, 0, 8}, {2, 2, 8}, {2, 0, 8}, {0, 2, 8}}, "cyan");      // crosses itself: no ears
    M.add_polygon({{0, 0, 9}, {3, 0, 9}, {3, 3, 9}, {2, 3, 9}, {2, 1, 9}, {1, 1, 9}, {1, 3, 9}, {0, 3, 9}},
                  "yellow");
    Mesh T = turned(M, 0.3, 2.2);
    record(add::detail::split_concave(T));
    dump(T);
    Mesh U;
    for (const Point& p : {Point{0, 0, 0}, Point{2, 0, 0}, Point{2, 1, 0}, Point{1, 1, 0}, Point{1, 2, 0},
                           Point{0, 2, 0}})
        U.add_vertex(p);
    U.add_face({0, 1, 2, 3, 4, 5}, "red", {{0, 0}, {1, 0}, {1, 0.5}, {0.5, 0.5}, {0.5, 1}, {0, 1}});
    U.add_face({5, 4, 3, 2, 1, 0}, "blue");
    U.add_face({0, 1, 2}, "green", {{0, 0}, {1, 0}, {1, 1}});
    record(add::detail::split_concave(U));
    dump(U);
    record(add::detail::split_concave(U));
}

// -- the overlap machinery ------------------------------------------------------

//: Faces in a few planes, overlapping every which way.
static Mesh overlap_scene() {
    Mesh M;
    quad_xz(M, 0, 0, 4, 4, 0.0, true, "red");                 // a floor ...
    quad_xz(M, 1, 1, 2, 2, 0.0, true, "blue");                // ... a tile lying on it
    quad_xz(M, 3, 3, 5, 5, 0.0, true, "green");               // ... one sticking out
    quad_xz(M, 1, 2.5, 3, 3.5, 0.0, false, "white");          // ... the bottom of something standing on it
    quad_xz(M, 6, 0, 7, 1, 0.0, true, "yellow");              // ... one on its own
    quad_xy(M, 0, 0, 3, 3, 1.0, true, "cyan");                 // a wall
    quad_xy(M, 1, 1, 2, 2, 1.0, true, "magenta");              // a picture on it
    quad_xy(M, 2.5, 0, 4, 1, 1.0004, false, "orange");         // nearly in its plane, facing away
    l_shape(M, {10, 0}, "pink", 2.0);                          // an L ...
    quad_xy(M, 10.5, 0.5, 12.5, 2.5, 2.0, true, "purple");     // ... and a square across its notch
    return M;
}

CASE(overlap_groups) {
    Mesh M = overlap_scene();
    std::vector<add::detail::PlaneGroup> groups = add::detail::overlap_groups(M, 1e-3);
    record(groups.size());
    for (const auto& G : groups) {
        record_list(G.key);
        record(G.u);
        record(G.v);
        record(G.n);
        for (const auto& P : G.polys) {
            record(P.area);
            record(P.index);
            record(P.pts);
            record_list(P.bb);
            record(P.flipped);
        }
    }
    Mesh T = turned(M, 0.4, 0.9);
    groups = add::detail::overlap_groups(T, 1e-3);
    record(groups.size());
    for (const auto& G : groups) {
        record_list(G.key);
        record(G.n);
        std::vector<int> idx;
        for (const auto& P : G.polys) idx.push_back(P.index);
        record(face_str(idx));
    }
}

//: Normals with a component that rounds to -0.0 or 0.0: one plane, the first key kept.
CASE(plane_keys) {
    Mesh M;
    M.add_polygon({{0, 0, 0}, {0, 0, 1}, {1, 0.0004, 1}, {1, 0.0004, 0}}, "red");        // n ~ (-0.0004, 1, 0)
    M.add_polygon({{0.5, 0.0003, 0}, {0.5, 0.0003, 1}, {1.5, 0.0002, 1}, {1.5, 0.0002, 0}}, "blue");
    M.add_polygon({{0, 0, 0.2}, {0.9, 0.0002, 0.2}, {0.9, 0.0002, 0.8}, {0, 0, 0.8}}, "green");   // facing down
    M.add_polygon({{0, 0.0000004, 3}, {0, 0.0000004, 4}, {1, 0.0000004, 4}, {1, 0.0000004, 3}}, "white");
    M.add_polygon({{0.2, -0.0000004, 3.2}, {0.2, -0.0000004, 3.8}, {0.8, -0.0000004, 3.8},
                   {0.8, -0.0000004, 3.2}}, "yellow");
    for (const auto& G : add::detail::overlap_groups(M, 1e-3)) {
        record_list(G.key);
        record(G.u);
        record(G.v);
        record(G.n);
        std::vector<int> idx;
        for (const auto& P : G.polys) idx.push_back(P.index);
        record(face_str(idx));
    }
    add::detail::OverlapScan scan = add::detail::overlap_scan(M, 1e-3, true);
    record(scan.count);
    for (const auto& r : scan.replaced) {
        record(r.first);
        record_polys(r.second.pieces);
        record(r.second.d);
    }
    Mesh C = add::clean(M);
    dump(C);
}

CASE(convex_overlap2) {
    Profile A = {{0.0, 0.0}, {4.0, 0.0}, {4.0, 3.0}, {0.0, 3.0}};
    for (const Profile& B : {Profile{{1.0, 1.0}, {2.0, 1.0}, {2.0, 2.0}, {1.0, 2.0}},
                             Profile{{3.0, 1.0}, {5.0, 1.0}, {5.0, 2.0}, {3.0, 2.0}},
                             Profile{{4.0, 0.0}, {6.0, 0.0}, {6.0, 3.0}, {4.0, 3.0}},
                             Profile{{2.0, -1.0}, {5.0, 1.5}, {2.0, 4.0}}}) {
        record(add::detail::convex_overlap2(A, B));
        record(add::detail::convex_overlap2(B, A));
    }
}

CASE(minus_all) {
    std::vector<Profile> A = {{{0.0, 0.0}, {10.0, 0.0}, {10.0, 10.0}, {0.0, 10.0}}};
    std::vector<Profile> holes;
    for (int i = 0; i < 5; ++i)
        for (int j = 0; j < 5; ++j) {
            double x = 0.5 + 2 * i, y = 0.5 + 2 * j;
            holes.push_back({{x, y}, {x + 1, y}, {x + 1, y + 1}, {x, y + 1}});
        }
    for (int n : {1, 2, 3, 6, 25}) {
        auto rest = add::detail::minus_all(A, std::vector<Profile>(holes.begin(), holes.begin() + n), 1e-9);
        if (!rest) record("none");
        else record_polys(*rest);
    }
    auto rest = add::detail::minus_all(A, holes, 1e-9, 1000);
    record(rest->size());
    record(*add::detail::minus_all(A, {}, 1e-9) == A);
}

static void record_scan(const Mesh& M, double tol, bool cut) {
    add::detail::OverlapScan scan = add::detail::overlap_scan(M, tol, cut);
    record(scan.count);
    record(scan.replaced.size());
    for (const auto& r : scan.replaced) {
        const add::detail::CutFace& R = r.second;
        record(r.first);
        record_polys(R.pieces);
        record(R.u);
        record(R.v);
        record(R.n);
        record(R.d);
        record(R.flipped);
    }
}

CASE(overlap_scan) {
    Mesh M = overlap_scene();
    record_scan(M, 1e-3, false);
    record_scan(M, 1e-3, true);
    record_scan(M, 1e-5, true);
    record_scan(turned(M, -0.6, 2.5), 1e-3, true);
}

CASE(cut_overlaps) {
    Mesh M = overlap_scene();
    record(add::detail::cut_overlaps(M));
    dump(M);
    Mesh N = turned(overlap_scene(), 1.1, 0.35);
    record(add::detail::cut_overlaps(N, 1e-3));
    dump(N);
}

CASE(cut_overlaps_uv) {
    Mesh M;
    Color wood(255, 255, 255);
    wood.image = "wood.png";
    for (const Point& p : {Point{0, 0, 0}, Point{4, 0, 0}, Point{4, 3, 0}, Point{0, 3, 0}, Point{3, 1, 0},
                           Point{6, 1, 0}, Point{6, 2, 0}, Point{3, 2, 0}})
        M.add_vertex(p);
    M.add_face({0, 1, 2, 3}, wood, {{0, 0}, {1, 0}, {1, 1}, {0, 1}});
    M.add_face({4, 5, 6, 7}, wood, {{0.1, 0.2}, {0.9, 0.2}, {0.9, 0.7}, {0.1, 0.7}});
    M.add_face({7, 6, 5, 4}, "red");
    M.add_polygon({{1, 1, 0}, {1.5, 1, 0}, {1.5, 1.5, 0}}, "blue");
    record(add::detail::cut_overlaps(M));
    dump(M);
    Mesh T = turned(M, 0.5, 0.25);
    Mesh C = add::clean(T);
    dump(C);
    save_file("obj", T);
}

CASE(overlaps_count) {
    Mesh M = overlap_scene();
    record(add::overlaps(M));
    record(add::overlaps(M, 1e-6));
    record(add::overlaps(M, 0.1));
    record(add::overlaps(Mesh()));
    add::mesh(M);
    record(add::overlaps());
    Mesh B;
    B.add_polygon({{NaN, 0, 0}, {1, 0, 0}, {1, 1, 0}});
    B.add_polygon({{0, 0, 0}, {1, 0, 0}, {1, 1, 0}});
    record(raises([&] { add::overlaps(B); }));
    record(raises([&] { add::overlaps(M, 0.0); }));
}

// -- shattering: a face that would fall into more than 64 pieces is left whole -----

CASE(shatter_strip) {
    Mesh M;
    quad_xz(M, 0, 0, 100, 0.1, 0.0, true, "red");             // a strip (area 10) ...
    for (int i = 0; i < 70; ++i) {                             // ... under 70 bars (area 15 each)
        double x = 0.7 + i * 1.4;
        quad_xz(M, x, -15, x + 0.5, 15, 0.0, true, "blue");
    }
    quad_xz(M, 0.8, -15.25, 1.1, -14.75, 0.0, true, "green"); // and a tile across a bar's end
    record_scan(M, 1e-3, false);
    record_scan(M, 1e-3, true);
    add::CleanReport info;
    Mesh C = add::clean(M, 1e-7, true, true, true, true, true, false, &info);
    record_report(info);
    save_mesh(C, "clean");
}

CASE(shatter_floor) {
    Mesh M;
    cuboid(M, {50, -0.5, 5}, {100, 1, 10}, "grey");           // a slab, top at y = 0
    for (int i = 0; i < 70; ++i)                               // 70 boxes standing on it
        cuboid(M, {1 + (i % 35) * 2.8, 0.5, 2.5 + (i / 35) * 5}, {1, 1, 1}, "red");
    record(add::overlaps(M));
    add::CleanReport info;
    add::clean(M, 1e-7, true, true, true, true, true, false, &info);
    record_report(info);
    save_file("off", M);
}

//: A floor so much bigger than the tiles that it is checked against everyone.
CASE(big_floor) {
    Mesh M;
    quad_xz(M, 0, 0, 20, 20, 0.0, true, "grey");
    for (int i = 0; i < 30; ++i) {
        double x = (i * 7) % 20 + 0.25, z = (i * 3) % 20 + 0.25;
        quad_xz(M, x, z, x + 0.5, z + 0.5, 0.0, i % 3 != 0, i % 2 ? "red" : "blue");
    }
    quad_xz(M, 19.75, 5, 20.25, 5.5, 0.0, true, "green");
    quad_xz(M, -0.25, -0.25, 0.25, 0.25, 0.0, false, "white");
    record_scan(M, 1e-3, true);
    add::CleanReport info;
    Mesh C = add::clean(M, 1e-7, true, true, true, true, true, false, &info);
    record_report(info);
    dump(C);
}

// -- heal: T-junctions ------------------------------------------------------------

CASE(heal_t_junctions) {
    Mesh M;
    for (const Point& p : {Point{0, 0, 0}, Point{2, 0, 0}, Point{2, 1, 0}, Point{0, 1, 0}, Point{1, 1, 0},
                           Point{2, 2, 0}, Point{0, 2, 0}, Point{0.5, 1, 0}, Point{1.5, 1.0000000001, 0},
                           Point{2.0, 0.5, 0}, Point{3, 0, 0}, Point{3, 1, 0}})
        M.add_vertex(p);
    M.add_face({0, 1, 2, 3}, "red");                          // its top edge has 3 vertices on it
    M.add_face({3, 7, 4, 6}, "blue");
    M.add_face({4, 8, 2, 5, 6}, "green");
    M.add_face({1, 10, 11, 2}, "white");                      // its left edge passes 9
    M.add_face({9, 10, 1}, "yellow");
    Mesh H = add::heal(M);
    dump(H);
    dump(add::heal(M, 1e-12));
    dump(add::heal(M, 0.01));
    add::mesh(M);
    dump(add::heal());
    record(add::scene().F[0].size());
}

CASE(heal_uv) {
    Mesh M;
    for (const Point& p : {Point{0, 0, 0}, Point{4, 0, 0}, Point{4, 2, 0}, Point{0, 2, 0}, Point{1, 2, 0},
                           Point{3, 2, 0}, Point{2, 2, 0}, Point{2, 3, 0}})
        M.add_vertex(p);
    M.add_face({0, 1, 2, 3}, "red", {{0, 0}, {1, 0}, {1, 0.5}, {0, 0.5}});
    M.add_face({3, 4, 7}, "blue");
    M.add_face({4, 6, 7}, "blue", {{0.2, 0.2}, {0.4, 0.2}, {0.3, 0.9}});
    M.add_face({6, 5, 7}, "green");
    M.add_face({5, 2, 7}, "green", {{0.6, 0.1}, {0.8, 0.1}, {0.7, 0.3}});
    dump(add::heal(M));
}

//: Many short edges and a long diagonal one: walk along it.
CASE(heal_long_edge) {
    Mesh M;
    int a = M.add_vertex({0, 0, 0});
    int b = M.add_vertex({6, 6, 6});
    int c = M.add_vertex({6, 0, 0});
    M.add_face({a, b, c}, "red");
    for (int i = 1; i < 30; ++i) {
        double t = i / 5.0;
        int p = M.add_vertex({t, t, t});
        int q = M.add_vertex({t + 0.05, t, t - 0.05});
        int r = M.add_vertex({t, t + 0.05, t + 0.02});
        M.add_face({p, q, r}, "blue");
    }
    M.add_vertex({3.0000000001, 3, 3});
    M.add_face({(int)M.V.size() - 1, 4, 5}, "green");
    Mesh H = add::heal(M);
    record(face_str(H.F[0]));
    dump(H);
}

CASE(heal_edge_cases) {
    record(add::heal(Mesh()).F.size());
    Mesh M;
    M.add_vertex({0, 0, 0});
    record(add::heal(M).V.size());
    Mesh N;
    N.add_polygon({{0, 0, 0}, {0, 0, 0}, {0, 0, 0}});
    N.add_face({0, 1}, "red");
    dump(add::heal(N));
    record(raises([&] { add::heal(N, 0.0); }));
    Mesh B;
    B.add_polygon({{NaN, 0, 0}, {1, 0, 0}, {1, 1, 0}});
    record(raises([&] { add::heal(B); }));
    Mesh I;
    I.add_polygon({{0, 0, 0}, {1e308, 0, 0}, {0, 1e308, 0}});
    record(raises([&] { add::heal(I); }));
}

// -- triangulate, fix_normals -------------------------------------------------------

CASE(triangulate) {
    Mesh M;
    l_shape(M, {0, 0}, "red");
    M.add_polygon({{0, 0, 1}, {1, 0, 1}, {1, 1, 1}}, "blue");
    M.add_face({0, 1}, "green");
    M.add_face({}, "green");
    M.add_face({6, 7, 8, 2}, add::transparent("sky", 0.3), {{0, 0}, {1, 0}, {1, 1}, {0, 1}});
    Mesh T = add::triangulate(M);
    dump(T);
    Mesh N;
    cuboid(N, {0, 0, 0}, {1, 2, 3}, "red");
    dump(add::triangulate(N));
    add::mesh(N);
    record(add::triangulate().F.size());
}

CASE(fix_normals) {
    Mesh M;
    cuboid(M, {0, 0, 0}, {1, 1, 1}, "red");
    std::reverse(M.F[1].begin(), M.F[1].end());
    std::reverse(M.F[4].begin(), M.F[4].end());
    cuboid(M, {3, 0, 0}, {1, 2, 1}, "blue");
    for (size_t i = 6; i < M.F.size(); ++i) std::reverse(M.F[i].begin(), M.F[i].end());   // an inside-out box
    M.add_polygon({{0, 5, 0}, {1, 5, 0}, {1, 5, 1}}, "green");      // a loose triangle
    dump(add::fix_normals(M));
    dump(add::fix_normals(M, false));
    add::mesh(M);
    dump(add::fix_normals());
    Mesh O;
    for (const Point& p : {Point{0, 0, 0}, Point{1, 0, 0}, Point{1, 1, 0}, Point{0, 1, 0}, Point{2, 0, 0},
                           Point{2, 1, 0}, Point{0, 2, 0}, Point{1, 2, 0}})
        O.add_vertex(p);
    O.add_face({0, 1, 2, 3}, "red", {{0, 0}, {1, 0}, {1, 1}, {0, 1}});
    O.add_face({1, 2, 5, 4}, "blue", {{0, 0}, {0, 1}, {1, 1}, {1, 0}});
    O.add_face({3, 2, 7, 6}, "green");
    O.add_face({2, 3, 6}, "white");                            // a third face on edge 2-3
    dump(add::fix_normals(O));
}

// -- clean ----------------------------------------------------------------------------

CASE(clean_boxes) {
    Mesh M;
    cuboid_polys(M, {0, 0, 0}, {1, 1, 1}, "red");
    cuboid_polys(M, {1, 0, 0}, {1, 1, 1}, "red");              // sharing a wall
    cuboid_polys(M, {0.5, 1, 0}, {1, 1, 1}, "blue");           // standing across both
    cuboid(M, {0, 0, 0}, {1, 1, 1}, "red");                    // the first one again
    add::CleanReport info;
    Mesh C = add::clean(M, 1e-7, true, true, true, true, true, false, &info);
    record_report(info);
    dump(C);
    save_file("off", M);
}

CASE(clean_flags) {
    Mesh M;
    cuboid_polys(M, {0, 0, 0}, {1, 1, 1}, "red");
    cuboid_polys(M, {1, 0.25, 0}, {1, 0.5, 0.5}, "blue");
    M.add_polygon({{0, 3, 0}, {1, 3, 0}, {2, 3, 0}}, "green");
    M.add_polygon({{0, 4, 0}, {2, 4, 0}, {2, 5, 0}, {1, 5, 0}, {1, 6, 0}, {0, 6, 0}}, "white");
    M.add_face({0, 1, 2, 3}, "red");
    M.add_face({3, 2, 1, 0}, "yellow");
    M.add_vertex({9, 9, 9});
    M.add_polygon({{5, 0, 0}, {6, 0, 0}, {NaN, 1, 0}}, "cyan");
    struct Flags {
        std::string name;
        double tol = 1e-7;
        bool weld = true, degenerate = true, duplicates = true, internal = true, unused = true, normals = false,
             overlaps = true, convex = true;
    };
    std::vector<Flags> all(11);
    all[1].name = "weld", all[1].weld = false;
    all[2].name = "degenerate", all[2].degenerate = false;
    all[3].name = "duplicates", all[3].duplicates = false;
    all[4].name = "internal", all[4].internal = false;
    all[5].name = "unused", all[5].unused = false;
    all[6].name = "normals", all[6].normals = true;
    all[7].name = "overlaps", all[7].overlaps = false;
    all[8].name = "convex", all[8].convex = false;
    all[9].name = "tol", all[9].tol = 0.3;
    all[10].name = "convex overlaps weld", all[10].weld = false;
    for (const Flags& f : all) {
        add::CleanReport info;
        Mesh C = add::clean(M, f.tol, f.weld, f.degenerate, f.duplicates, f.internal, f.unused, f.normals, &info,
                            f.overlaps, f.convex);
        record(f.name);
        record_report(info);
        dump(C);
    }
    record(add::clean(M).F.size());
}

CASE(clean_scene) {
    cuboid_polys(add::scene(), {0, 0, 0}, {2, 1, 2}, "red");
    cuboid_polys(add::scene(), {0, 1, 0}, {1, 1, 1}, "blue");
    Mesh C = add::clean();
    dump(C);
    record(add::scene().F.size());
    save_case();
}

//: Boxes stacked on each other (contacts) and side by side (walls).
CASE(clean_tower) {
    Mesh M;
    for (int i = 0; i < 4; ++i) cuboid(M, {0, i + 0.5, 0}, {2.0 - i * 0.4, 1, 2.0 - i * 0.4}, add::hsv(i / 4.0));
    cuboid(M, {1.5, 0.5, 0}, {1, 1, 1}, "red");
    cuboid(M, {0, 0.5, 1.4}, {0.8, 1, 0.8}, add::transparent("sky", 0.4));
    add::CleanReport info;
    Mesh C = add::clean(M, 1e-6, true, true, true, true, true, false, &info);
    record_report(info);
    dump(C);
    save_file("obj", M);
    save_file("off", M);
}

CASE(clean_turned) {
    Mesh M;
    cuboid(M, {0, 0.5, 0}, {2, 1, 2}, "red");
    cuboid(M, {0.3, 1.5, 0.2}, {1, 1, 1}, "blue");
    cuboid(M, {1.5, 0.25, 0}, {1, 0.5, 1}, "green");
    Mesh T = turned(M, 0.35, 1.2);
    add::CleanReport info;
    Mesh C = add::clean(T, 1e-7, true, true, true, true, true, false, &info);
    record_report(info);
    dump(C);
    save_file("off", T);
}

CASE(clean_textured) {
    Mesh M;
    Color bricks(255, 255, 255), wood(200, 180, 160), glass(255, 255, 255, 0.5);
    bricks.image = "bricks.png";
    wood.image = "wood.jpg";
    glass.image = "glass.png";
    textured_cuboid(M, {0, 0.5, 0}, {2, 1, 2}, bricks);
    textured_cuboid(M, {0.5, 1.5, 0.5}, {1, 1, 1}, wood);
    textured_cuboid(M, {1.5, 0.5, 0}, {1, 1, 1}, glass);
    add::CleanReport info;
    Mesh C = add::clean(M, 1e-7, true, true, true, true, true, false, &info);
    record_report(info);
    dump(C);
    save_file("obj", M);
}

// -- random scenes: boxes and tiles on a half-unit grid (lots of shared planes) --------

static Mesh random_scene(long long seed, int n, const std::string& kind) {
    add::Random r(seed);
    std::vector<Color> colors = {"red", "green", "blue", "white", add::transparent("sky", 0.5)};
    Mesh M;
    if (kind == "floor") cuboid(M, {0, -0.5, 0}, {8, 1, 8}, "grey");
    for (int i = 0; i < n; ++i) {
        double x = r.randint(-6, 6) * 0.5;
        double z = r.randint(-6, 6) * 0.5;
        double sx = r.randint(1, 4) * 0.5;
        double sz = r.randint(1, 4) * 0.5;
        Color c = r.choice(colors);
        if (kind == "tiles") {
            double y = r.randint(0, 1) * 0.5;
            bool up = r.random() < 0.7;
            quad_xz(M, x, z, x + sx, z + sz, y, up, c);
        } else {
            double sy = r.randint(1, 3) * 0.5;
            double y = kind != "floor" ? r.randint(0, 2) * 0.5 : 0.0;
            if (r.random() < 0.5) cuboid(M, {x, y + sy / 2.0, z}, {sx, sy, sz}, c);
            else cuboid_polys(M, {x, y + sy / 2.0, z}, {sx, sy, sz}, c);
        }
    }
    if (kind == "turned") {
        double ax = r.uniform(-1, 1);
        double ay = r.uniform(-3, 3);
        M = turned(M, ax, ay);
    }
    return M;
}

static void random_case(long long seed, int n, const std::string& kind) {
    Mesh M = random_scene(seed, n, kind);
    add::CleanReport info;
    Mesh C = add::clean(M, 1e-7, true, true, true, true, true, false, &info);
    record_report(info);
    record(add::overlaps(M));
    record(add::overlaps(C));
    record(add::concave_faces(C));
    save_mesh(C, "clean");
    save_file("obj", M);
}

CASE(random_boxes_1) { random_case(1, 12, "boxes"); }
CASE(random_boxes_2) { random_case(2, 25, "boxes"); }
CASE(random_boxes_3) { random_case(3, 40, "boxes"); }
CASE(random_floor_1) { random_case(11, 15, "floor"); }
CASE(random_floor_2) { random_case(12, 30, "floor"); }
CASE(random_tiles_1) { random_case(21, 20, "tiles"); }
CASE(random_tiles_2) { random_case(22, 50, "tiles"); }
CASE(random_turned_1) { random_case(31, 15, "turned"); }
CASE(random_turned_2) { random_case(32, 30, "turned"); }

// -- stats and check ----------------------------------------------------------------

static void record_stats(const add::Stats& s) {
    record(add::detail::fmt("vertices %d faces %d triangles %d colors %d", s.vertices, s.faces, s.triangles, s.colors));
    record(s.bbox[0]);
    record(s.bbox[1]);
    record(s.size);
    record(s.area);
    record(s.volume);
    record(add::detail::fmt("open %d non-manifold %d dup-vertices %d dup-faces %d back-to-back %d", s.open_edges,
                            s.non_manifold_edges, s.duplicate_vertices, s.duplicate_faces, s.back_to_back_faces));
    record(s.closed);
    record(s.obj_bytes);
    record(s.transparent_faces);
    record(s.textures.size());
    for (const std::string& t : s.textures) record(t);
}

//: A model with a bit of everything check() complains about.
static Mesh messy() {
    Mesh M;
    Color floor_tex(255, 255, 255), a_tex(255, 255, 255);
    floor_tex.image = "tiles/floor.png";
    a_tex.image = "a.png";
    cuboid(M, {0, 0, 0}, {1, 1, 1}, "red");
    cuboid(M, {3, 0, 0}, {1, 1, 1}, floor_tex);
    M.add_face({0, 3, 2, 1}, "red");                           // repeated
    M.add_face({1, 2, 3, 0}, "blue");                          // back to back
    M.add_face({0, 1, 9}, "green");                            // a third face on edge 0-1
    M.add_vertex({0.5, 0.5, 0.5});
    M.add_vertex({0.5, 0.5, 0.5000000001});
    M.add_polygon({{0, 3, 0}, {2, 3, 0}, {2, 4, 0}, {1, 4, 0}, {1, 5, 0}, {0, 5, 0}}, add::transparent("sky", 0.25));
    M.add_polygon({{0.2, 3.2, 0}, {0.8, 3.2, 0}, {0.8, 3.8, 0}}, a_tex);
    return M;
}

CASE(stats) {
    Mesh M = messy();
    record_stats(add::stats(M));
    Mesh N;
    cuboid(N, {0, 0, 0}, {1, 2, 3}, "red");
    record_stats(add::stats(N));
    record_stats(add::stats(Mesh()));
    add::mesh(N);
    record_stats(add::stats());
    Mesh S;
    for (const Point& p : {Point{0, 0, 0}, Point{-0.0, 1, 0}, Point{0.0000001, 1, 0}, Point{1, 1, 1},
                           Point{1, 1, 1.0000004}, Point{2, 2, 2}})
        S.add_vertex(p);
    S.add_face({0, 1, 3}, "red");
    S.add_face({2, 4, 5}, "red");
    S.add_face({0, 1, 3}, "red");
    S.add_face({3, 1, 0}, "red");
    S.add_face({1, 3, 0}, "red");
    record_stats(add::stats(S));
    Mesh B;
    B.add_polygon({{NaN, 0, 0}, {1, 0, 0}, {1, 1, 0}});
    record(raises([&] { add::stats(B); }));
    Mesh E;
    E.add_polygon({{0, 0, 0}, {1, 0, 0}, {1, 1, 0}});
    E.add_face({}, "red");
    E.add_face({}, "blue");
    record(raises([&] { add::stats(E); }));
}

template <class F>
static void record_check(F fn) {
    std::pair<std::string, bool> out = capture(fn);
    record(out.first);
    record(out.second);
}

//: How check() writes numbers: Python's "%.3f", "%.1f" and "%d" of a float.
CASE(format_numbers) {
    for (double x : {NaN, -NaN, Inf, -Inf, 0.0, -0.0, -0.0004, 0.0005, 0.0015, 2.5e-4, 0.05, 0.25, 1.25, 2.5, -2.5,
                     49.99, 1e20, -123.4565, 5e-324, 1e300}) {
        record(add::detail::check_f(x, 3));
        record(add::detail::check_f(x, 1));
        try {
            record(add::detail::check_d(x));
        } catch (const std::exception&) {
            record("raised");
        }
    }
}

CASE(check_messy) {
    Mesh M = messy();
    record_check([&] { return add::check(M); });
    record_check([&] { return add::check(M, 10, 2); });
    record_check([&] { return add::check(M, 10, 2, true); });
    record_check([&] { return add::check(M, 5, 1, false, 0.0001, 3); });
    record_check([&] { return add::check(M, 5, 1, false, 2.5, 3); });
    Mesh B;
    B.add_polygon({{NaN, 0, 0}, {1, 0, 0}, {1, 1, 0}});
    record(raises([&] { capture([&] { return add::check(B); }); }));
}

CASE(check_closed) {
    Mesh M;
    cuboid(M, {0, 0, 0}, {1, 2, 3}, "red");
    cuboid(M, {0, 0, 5}, {1, 1, 1}, "green");
    cuboid(M, {0, 0, 8}, {1, 1, 1}, "blue");
    record_check([&] { return add::check(M); });
    record_check([&] { return add::check(M, 18); });
    add::mesh(M);
    record_check([&] { return add::check(); });
    record_check([&] { return add::check(Mesh()); });
}

CASE(check_passes) {
    Mesh M;
    grid_of_quads(M, 100, 100, {"red", "green", "blue"});
    record_check([&] { return add::check(M); });
    record_check([&] { return add::check(M, 10000, 3, false, 1e-6); });
    record_check([&] { return add::check(M, 10001); });
    record_stats(add::stats(M));
}

CASE(check_overlaps) {
    Mesh M = overlap_scene();
    record_check([&] { return add::check(M, 1, 1); });
}

// -- saving goes through clean() ------------------------------------------------------

CASE(save_messy) {
    Mesh M = messy();
    save_file("off", M);
    save_file("obj", M);
}

CASE(save_overlaps) {
    Mesh M = overlap_scene();
    save_file("off", M);
    save_file("obj", turned(M, 0.2, 0.1));
}

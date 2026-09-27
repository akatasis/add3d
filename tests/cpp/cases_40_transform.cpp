// Parity cases for _cpp/40_transform.hpp: measuring, moving and reshaping meshes,
// colouring them, patterns of copies (see cases_40_transform.py).
#include "parity.hpp"

using add::Color;
using add::Mesh;
using add::Point;

static const std::vector<Color> SIX = {"red", Color(10, 200, 30), add::transparent("sky", 0.4), "#123456",
                                       Color(250, 250, 5), "navy"};

//: The mesh exactly as it is, as .obj + .mtl (keeps texture coordinates).
static void save_obj(const Mesh& M, const std::string& tag) { add::obj(parity::current() + "_" + tag + ".obj", M); }

static void record_palette(const std::vector<std::pair<Color, int>>& pal) {
    record(pal.size());
    for (const auto& item : pal) {
        record(item.first);
        record(item.second);
    }
}

static void record_box(const std::array<Point, 2>& b) { record(add::Points{b[0], b[1]}); }

static Color textured(Color c, const std::string& image) {
    c.image = image;
    return c;
}

static Mesh cube(Point lo = {-0.5, -0.25, -0.75}, Point hi = {0.5, 0.75, 1.25}, const std::vector<Color>& colors = {}) {
    Mesh M;
    for (int k = 0; k < 8; ++k) M.add_vertex({k & 1 ? hi[0] : lo[0], k & 2 ? hi[1] : lo[1], k & 4 ? hi[2] : lo[2]});
    std::vector<add::Face> faces = {{0, 4, 6, 2}, {1, 3, 7, 5}, {0, 1, 5, 4}, {2, 6, 7, 3}, {0, 2, 3, 1}, {4, 5, 7, 6}};
    for (size_t i = 0; i < faces.size(); ++i) M.add_face(faces[i], colors.empty() ? add::DEFAULT_COLOR : colors[i]);
    return M;
}

//: An open, bumpy sheet of quads, one colour each.
static Mesh patch(int nx = 4, int nz = 3) {
    Mesh M;
    for (int i = 0; i < nx + 1; ++i)
        for (int j = 0; j < nz + 1; ++j) {
            double x = -1.0 + 2.0 * i / nx;
            double z = -0.7 + 1.9 * j / nz;
            M.add_vertex({x, 0.3 * std::sin(2 * x + z) + 0.1 * x * z, z});
        }
    for (int i = 0; i < nx; ++i)
        for (int j = 0; j < nz; ++j) {
            int a = i * (nz + 1) + j;
            M.add_face({a, a + 1, a + nz + 2, a + nz + 1}, add::hsv((i * nz + j) / (double)(nx * nz)));
        }
    return M;
}

//: One small triangle per colour.
static Mesh triangles(const std::vector<Color>& colors) {
    Mesh M;
    for (size_t k = 0; k < colors.size(); ++k) {
        double i = (double)k;
        M.add_polygon({{i, 0, 0}, {i + 1, 0, 0}, {i, 1, 0.5 * i}}, colors[k]);
    }
    return M;
}

CASE(t_measure) {
    for (const Mesh& M : {cube(), patch(), triangles(SIX), Mesh()}) {
        record_box(add::bbox(M));
        record(add::size(M));
        record(add::center(M));
        record(add::middle(M));
        record(add::area(M));
        record(add::volume(M));
    }
    add::mesh(cube({-0.5, -0.25, -0.75}, {2, 3, 4}));
    record_box(add::bbox());
    record(add::size());
    record(add::center());
    record(add::middle());
    record(add::area());
    record(add::volume());
    save_case();
}

CASE(t_moves) {
    Mesh M = cube({-0.5, -0.25, -0.75}, {0.5, 0.75, 1.25}, SIX);
    save_mesh(add::move(M, {1, -2, 0.5}), "move");
    save_mesh(add::place(M, {3, 1, -1}), "place_bbox");
    save_mesh(add::place(patch(), {3, 1, -1}, false), "place_center");
    save_mesh(add::rotateX(M, 0.7), "rx");
    save_mesh(add::rotateY(M, -1.1, {1, 2, 3}), "ry");
    save_mesh(add::rotateZ(M, 2.5, {0.5, 0, -1}), "rz");
    save_mesh(add::rotate(M, {1, 1, 0}, add::pi / 3, {0, 1, 0}), "rot");
    save_mesh(add::rotate(M, {0, 0, 0}, 1.0), "rot_zero_axis");
    save_mesh(add::zoom(M, 1.5), "zoom");
    save_mesh(add::zoom(patch(), -0.5, Point{1, 1, 1}), "zoom_neg");
    save_mesh(add::stretch(M, {1, 2, -1}), "stretch_flip");
    save_mesh(add::stretch(M, {0.5, 2, 3}, Point{0, 0, 0}), "stretch");
    save_mesh(add::color(M, "gold"), "color");
    save_mesh(add::color(M, add::transparent("red", 0.3)), "color_t");
}

CASE(t_mapped_uv) {
    Mesh T = add::texture(cube({-0.5, -0.25, -0.75}, {0.5, 0.75, 1.25}, SIX), "w.png", "box");
    save_obj(T, "plain");
    save_obj(add::move(T, {1, 2, 3}), "move");
    save_obj(add::mirror(T), "mirror");
    save_obj(add::zoom(T, -1), "zoom_neg");
    save_obj(add::merge({T, cube()}), "merge");
    save_obj(add::array_linear(T, {2, 0, 0}, 2), "linear");
}

CASE(t_fit) {
    Mesh M = cube({-0.5, -0.25, -0.75}, {0.5, 0.75, 1.25}, SIX);
    save_mesh(add::fit(M), "default");
    save_mesh(add::fit(M, 3.0, Point{1, 0, 0}), "about");
    save_mesh(add::fit(patch(), 0.5), "patch");
    Mesh P;
    P.add_polygon({{1, 1, 1}, {1, 1, 1}, {1, 1, 1}});
    save_mesh(add::fit(P, 2.0), "point");
}

CASE(t_mirror) {
    Mesh M = cube({-0.5, -0.25, -0.75}, {0.5, 0.75, 1.25}, SIX);
    save_mesh(add::mirror(M), "default");
    save_mesh(add::mirror(M, {0.3, 0, 0}, {1, 2, -0.5}), "plane");
    save_mesh(add::mirror(patch(), {0, 0.1, 0}, {0, 1, 0}), "patch");
    save_mesh(add::array_mirror(M, {1, 0, 0}), "array");
    save_mesh(add::array_mirror(patch(), {0, 0, 0}, {0, 1, 1}), "array2");
}

CASE(t_transform) {
    Mesh M = cube({-0.5, -0.25, -0.75}, {0.5, 0.75, 1.25}, SIX);
    save_mesh(add::transform(M, {{1, 0.5, 0}, {0, 1, 0}, {0.2, 0, 2}}), "m3");
    save_mesh(add::transform(M, {{0, 1, 0}, {1, 0, 0}, {0, 0, 1}}), "swap");
    save_mesh(add::transform(M, {{0.5, 0, 0, 1}, {0, 2, 0, -1}, {0, 0, 1, 0.25}, {0, 0, 0, 1}}), "m4");
    save_mesh(add::transform(patch(), {{-1, 0, 0, 3}, {0, 1, 0, 0}, {0, 0.3, 1, 0}}), "m34_flip");
}

CASE(t_deform) {
    save_mesh(add::deform(patch(), [](const Point& p) {
                  return Point{p[0], p[1] + std::sin(3 * p[0]) * 0.2, p[2] * 1.5};
              }), "wave");
    save_mesh(add::deform(cube({-0.5, -0.25, -0.75}, {0.5, 0.75, 1.25}, SIX), [](const Point& p) {
                  return Point{p[0] * (1 + p[1]), p[1], p[2] - p[0]};
              }), "shear");
}

CASE(t_twist) {
    Mesh M = cube({-0.5, -0.25, -0.75}, {0.5, 0.75, 1.25}, SIX);
    save_mesh(add::twist(M, 0.8), "default");
    save_mesh(add::twist(M, -1.3, {1, 0, 1}, {0.2, 0, 0}), "axis");
    save_mesh(add::twist(patch(), 2.0, {1, 0, 0}), "patch");
}

CASE(t_taper) {
    Mesh M = cube({-0.5, -0.25, -0.75}, {0.5, 0.75, 1.25}, SIX);
    save_mesh(add::taper(M, -0.2), "default");
    save_mesh(add::taper(M, 0.5, 0, {0.1, 0, 0}), "x");
    save_mesh(add::taper(M, 0.3, 2), "z");
    save_mesh(add::taper(M, 0.3, -1, {0, 0, 0.5}), "neg");
    save_mesh(add::taper(patch(), 0.7, 2, {0, 1, -1}), "patch");
}

CASE(t_bend) {
    Mesh P = patch();
    Mesh C = add::stretch(cube({-0.5, -0.25, -0.75}, {0.5, 0.75, 1.25}, SIX), {0.5, 3, 0.5});
    save_mesh(add::bend(C, 0.4), "default");
    save_mesh(add::bend(P, 0.5, 0, 2, {0, -1, 0}), "x");
    save_mesh(add::bend(P, 1e-12), "tiny");
    save_mesh(add::bend(C, -0.3, 1, 2, {0.5, 0, 0}), "around_z");
    save_mesh(add::bend(C, 0.6, 1, 1), "same_axes");
}

CASE(t_jitter) {
    Mesh M = cube({-0.5, -0.25, -0.75}, {0.5, 0.75, 1.25}, SIX);
    save_mesh(add::jitter(M, 0.1, 42), "seed");
    save_mesh(add::jitter(M), "global");
    save_mesh(add::jitter(patch(), 0.2, 0), "seed0");
    record(add::random());
}

CASE(t_opacity) {
    Mesh M = cube({-0.5, -0.25, -0.75}, {0.5, 0.75, 1.25}, SIX);
    Mesh T = add::texture(M, "wood.png", "box");
    for (double a : {0.3, 1.0, 0.0, 128.0, -1.0, 0.1234, 2.0}) {
        record(add::opacity(M, a).C);
        record(add::opacity(T, a).C);
    }
    save_mesh(add::opacity(M, 0.5), "half");
    save_obj(add::opacity(T, 0.25), "textured");
}

CASE(t_texture) {
    Mesh M = cube({-0.5, -0.25, -0.75}, {0.5, 0.75, 1.25}, SIX);
    Mesh P = patch();
    for (std::string mapping : {"box", "xy", "xz", "yz", "fit", "sphere", "cylinder"}) {
        Mesh T = add::texture(M, "img/bricks.png", mapping);
        record(T.UV);
        record(T.C);
        save_obj(T, mapping);
        T = add::texture(P, "tiles.jpg", mapping, 0.5, std::nullopt, {0.25, -0.5});
        record(T.UV);
        record(T.C);
        save_obj(T, mapping + "_patch");
    }
    Mesh T = add::texture(P, "tiles.jpg", "sphere", 3, "red");
    record(T.UV);
    save_obj(T, "sphere3");
    T = add::texture(M, "c.png", "cylinder", 0, add::transparent("sky", 0.2), {5, 5});
    record(T.UV);
    record(T.C);
    save_obj(T, "cyl0");
    T = add::texture(M, "a.png", [](const Point& p, const Point& n) { return add::Point2{p[0] + n[1], p[2] * 2}; });
    record(T.UV);
    save_obj(T, "custom");
    Mesh D;
    D.add_polygon({{0, 0, 0}, {1, -1, 0}, {1, -1, 1}, {0, 0, 1}});
    D.add_polygon({{1, 0, 0}, {0, 1, 0}, {0, 0, 1}});
    D.add_polygon({{0, 0, 2}, {1, 1, 2}, {2, 2, 2}});
    D.add_polygon({{0, 0, 0}, {0, 1, 1}, {0, 1, 2}, {0, 0, 3}});
    for (std::string mapping : {"box", "sphere", "cylinder"}) {
        T = add::texture(D, "d.png", mapping, 1.5);
        record(T.UV);
        save_obj(T, "ties_" + mapping);
    }
    T = add::texture(add::opacity(M, 0.5), "", "box", 2.0, std::nullopt);
    record(T.C);
    try {
        add::texture(M, "a.png", "bogus");
    } catch (const std::invalid_argument&) {
        record("raised");
    }
}

CASE(t_color_by) {
    Mesh P = patch();
    save_mesh(add::color_by(P, [](const Point& p) { return add::hsv(p[1] * 2.0 + p[0]); }), "hsv");
    save_mesh(add::color_by(P, [](const Point& p) { return p[0] > 0 ? Color("red") : Color(0.2, 0.4, 0.6); }),
              "mixed");
    save_mesh(add::color_by(cube(), [](const Point& p) { return add::transparent("blue", p[2] + 0.5); }), "clear");
}

CASE(t_color_gradient) {
    Mesh P = patch(8, 6);
    save_mesh(add::color_gradient(P, "red", "blue"), "y");
    save_mesh(add::color_gradient(P, "red", Color(0, 255, 0), 0), "x");
    save_mesh(add::color_gradient(P, "white", "black", -1), "neg");
    Mesh F;
    F.add_polygon({{0, 0, 0}, {1, 0, 0}, {1, 0, 1}});
    save_mesh(add::color_gradient(F, add::transparent("red", 0.5), "blue"), "flat");
}

CASE(t_color_random) {
    Mesh P = patch();
    save_mesh(add::color_random(P, 7), "seed");
    save_mesh(add::color_random(P), "global");
    save_mesh(add::color_random(cube(), -3), "negative_seed");
    record(add::randint(0, 1000));
}

CASE(t_palette) {
    std::vector<Color> cs = {Color(0, 0, 0), Color(255, 0, 1), Color(254, 255, 255), "red",
                             add::transparent("red", 0.5), add::transparent("red", 0.25),
                             textured(Color(255, 0, 0, 0.5), "a.png"), textured(Color(255, 0, 0), "b.png"),
                             textured(Color(255, 0, 0), "a.png")};
    std::vector<Color> all = cs;
    all.insert(all.end(), cs.rbegin(), cs.rend());
    for (Color c : {Color("red"), Color(0, 0, 0), Color("red")}) all.push_back(c);
    Mesh M = triangles(all);
    record_palette(add::palette(M));
    record_palette(add::palette(Mesh()));
    add::mesh(M);
    add::mesh(triangles(std::vector<Color>(5, "navy")));
    record_palette(add::palette());
    save_case();
}

CASE(t_limit_colors) {
    Mesh P = add::color_random(patch(12, 10), 3);
    for (int n : {50, 10, 3, 2, 1, 0, -1, 120, 200}) record_palette(add::palette(add::limit_colors(P, n)));
    Mesh G = add::color_gradient(patch(9, 7), "red", "blue", 0);
    G = add::merge({G, add::color_by(patch(5, 5), [](const Point& p) {
                        int v = (int)(p[0] * 50);
                        return Color(((v % 256) + 256) % 256, 100, 7);                // (Python's %)
                    }),
                    add::opacity(patch(2, 2), 0.5), add::texture(patch(1, 1), "t.png")});
    for (int n : {4, 3, 7}) {
        Mesh L = add::limit_colors(G, n);
        record_palette(add::palette(L));
        save_mesh(L, "g" + std::to_string(n));
    }
    save_mesh(add::limit_colors(P, 5), "five");
}

CASE(t_arrays) {
    Mesh M = cube({-0.5, -0.25, -0.75}, {0.5, 0.75, 1.25}, SIX);
    save_mesh(add::repeat(M, 4, [](const Mesh& X, int i) { return add::move(add::rotateY(X, i * 0.3), {0, i * 0.2, 0}); }),
              "repeat");
    save_mesh(add::repeat(M, 0, [](const Mesh& X, int) { return X; }), "repeat0");
    save_mesh(add::array_linear(M, {1.5, 0, 0.25}, 3), "linear");
    save_mesh(add::array_grid(M, {2, 3, 0.5}, {2, 3, 1}), "grid");
    save_mesh(add::array_grid(M, {2, 3, 0.5}, {2, 0, 1}), "grid0");
    save_mesh(add::array_radial(M, 5), "radial");
    save_mesh(add::array_radial(M, 7, {0, 0, 1}, {1, 0, 0}, add::pi, 0.3), "spiral");
    save_mesh(add::array_radial(M, 0), "none");
}


//: Random polygons in coarse random colours (many repeats and ties), some see-through or
//: textured: palette, limit_colors, texture, measures.
CASE(t_random) {
    for (long long seed = 0; seed < 12; ++seed) {
        add::Random r(seed);
        Mesh M;
        long long count = r.randint(1, 60);
        for (long long i = 0; i < count; ++i) {
            double x = r.uniform(-2, 2);
            double y = r.uniform(-2, 2);
            double z = r.uniform(-2, 2);
            int k = (int)r.randint(3, 6);
            add::Points pts;
            for (int j = 0; j < k; ++j) {
                double a = 2 * add::pi * j / k;
                pts.push_back({x + 0.3 * std::cos(a), y + 0.2 * std::sin(a), z + 0.1 * j});
            }
            long long kind = r.randint(0, 9);
            Color c;
            if (kind < 6) {
                int cr = (int)r.randint(0, 8) * 30;
                int cg = (int)r.randint(0, 8) * 30;
                int cb = (int)r.randint(0, 8) * 30;
                c = Color(cr, cg, cb);
            } else if (kind < 8) {
                int cr = (int)r.randint(0, 255);
                double alpha = r.random();
                c = add::transparent(Color(cr, 0, 0), alpha);
            } else {
                int cg = (int)r.randint(0, 255);
                c = textured(Color(0, cg, 0), "t" + std::to_string(r.randint(0, 2)) + ".png");
            }
            M.add_polygon(pts, c);
        }
        record_palette(add::palette(M));
        for (int n : {1, 2, 5, 17}) record_palette(add::palette(add::limit_colors(M, n)));
        for (std::string mapping : {"sphere", "cylinder", "box"}) record(add::texture(M, "x.png", mapping, r.uniform(0.2, 3)).UV);
        record_box(add::bbox(M));
        record(add::area(M));
        record(add::center(M));
    }
}

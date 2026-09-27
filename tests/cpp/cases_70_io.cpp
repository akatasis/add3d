// Parity cases for _cpp/70_io.hpp: the writers behind save / off / obj (.off .obj .ply .stl),
// obj_size, the Stream, load (.off, .obj + .mtl, .ply), write_png, load_font and typeset
// (see cases_70_io.py).
//
// Every input file a case reads is written by the case itself, byte for byte the same in both
// languages.  A PNG is compared by its decoded pixels, not by its bytes: add.py compresses them
// with zlib, add.hpp stores them uncompressed (see png_record).
#include "parity.hpp"

using add::Color;
using add::Face;
using add::Mesh;
using add::Point;
using add::Points;
using add::detail::fmt;

static const double NAN_ = std::numeric_limits<double>::quiet_NaN();
static const double INF = std::numeric_limits<double>::infinity();

//: The bytes of a string literal, NULs included.
template <size_t N>
static std::string B(const char (&s)[N]) {
    return std::string(s, N - 1);
}

//: What f() does: "ok", or which kind of exception it raises -- named after Python's kinds.
template <class F>
static std::string outcome(F f) {
    try {
        f();
    } catch (const std::system_error&) {
        return "OSError";
    } catch (const std::out_of_range&) {
        return "LookupError";
    } catch (const std::overflow_error&) {
        return "OverflowError";
    } catch (const std::invalid_argument&) {
        return "ValueError";
    }
    return "ok";
}

//: A file with exactly these bytes.
static void write_file(const std::string& name, const std::string& data) {
    std::ofstream f(name, std::ios::binary);
    f << data;
}

//: A string with every character outside printable ASCII written as <XXXX>.
static std::string show(const std::string& s) {
    std::string out;
    for (size_t i = 0; i < s.size();) {
        long cp = add::detail::utf8_next(s, i);
        if (cp >= 0x20 && cp <= 0x7E) out += (char)cp;
        else out += fmt("<%04lX>", cp);
    }
    return out;
}

static std::string join(const std::vector<std::string>& xs, const std::string& sep) {
    std::string s;
    for (size_t i = 0; i < xs.size(); ++i) s += (i ? sep : "") + xs[i];
    return s;
}

//: The mesh exactly as it is, as .obj + .mtl (faces of any size kept whole).
static void save_obj(const Mesh& M, const std::string& tag) { add::obj(parity::current() + "_" + tag + ".obj", M); }

//: The mesh exactly as it is, as .off and as .obj + .mtl.
static void exact(const Mesh& M, const std::string& tag) {
    save_mesh(M, tag);
    save_obj(M, tag);
}

static Mesh from_faces(const Points& V, const std::vector<Face>& F, const std::vector<Color>& colors = {}) {
    Mesh M;
    for (const Point& p : V) M.add_vertex(p);
    for (size_t i = 0; i < F.size(); ++i) M.add_face(F[i], colors.empty() ? add::DEFAULT_COLOR : colors[i % colors.size()]);
    return M;
}

static Color with_image(Color c, const std::string& image) {
    c.image = image;
    return c;
}

//: What a stream has counted so far, and its materials in order.
static void counts(const add::Stream& out) {
    record(fmt("faces %lld vertices %lld bytes %lld removed %lld cut %lld", out.faces, out.vertices, out.bytes,
               out.removed, out.cut));
    std::vector<std::string> names;
    for (const auto& m : out.materials) names.push_back(m.second);
    record("materials: " + join(names, " "));
}

//: Two touching red boxes (the wall between them goes when tidied), a gold slab on them, a
//: cylinder with 8-corner lids, a see-through box and a textured box.
static Mesh model() {
    add::push();
    add::box({0, 0, 0}, 1, "red");
    add::box({1, 0, 0}, 1, "red");
    add::cuboid({0.5, 1, 0}, {2, 1, 0.5}, "gold");
    add::cylinder({3, 0, 0}, {3, 2, 0}, 0.5, 8, Color(10, 200, 30));
    Mesh M = add::pop();
    Mesh glass = add::opacity(add::make([] { add::box({0, 0, 3}, 1, "sky"); }), 0.35);
    Mesh tex = add::texture(add::make([] { add::box({3, 0, 3}, 1, "white"); }), "img\\wood.png");
    return add::merge({M, glass, tex});
}

//: Faces an OFF file cannot carry as they are: a convex hexagon, an L (concave), a notched
//: pentagon, a self-crossing outline, a pentagon with a corner in the middle of a side, a
//: clockwise pentagon, a star; then a face pinched at a vertex, one using a NaN vertex and a
//: plain triangle (no two of them in one plane).
static Mesh odd_faces() {
    Points V = {{0, 0, 0}, {2, 0, 0}, {3, 1, 0}, {2, 2, 0}, {0, 2, 0}, {-1, 1, 0},                // 0-5 hexagon
                {0, 0, 1}, {2, 0, 1}, {2, 1, 1}, {1, 1, 1}, {1, 2, 1}, {0, 2, 1},                  // 6-11 L
                {4, 0, 2}, {6, 0, 2}, {6, 2, 2}, {5, 0.5, 2}, {4, 2, 2},                            // 12-16 notch
                {0, 0, 3}, {2, 2, 3}, {2, 0, 3}, {0, 2, 3}, {1, -1, 3}, {1, 3, 3},                  // 17-22 crossing
                {0, 0, 4}, {1, 0, 4}, {2, 0, 4}, {2, 2, 4}, {0, 2, 4},                              // 23-27 T-junction
                {0, 0, 5}, {0, 2, 5}, {2, 2, 5}, {3, 1, 5}, {2, 0, 5},                              // 28-32 clockwise
                {NAN_, 0, 0}};                                                                      // 33
    for (int i = 0; i < 10; ++i) {
        double r = i % 2 == 0 ? 2.0 : 0.8;
        double a = 2 * add::pi * i / 10;
        V.push_back({10 + r * add::cos(a), r * add::sin(a), 6});                                    // 34-43 star
    }
    Points more = {{0, 0, 7}, {1, 0, 7}, {1, 1, 7}, {-1, 0, 7}, {-1, -1, 7},                       // 44-48 pinched
                   {0, 0, 8}, {1, 0, 8.5}, {0, 1, 9}};                                              // 49-51 triangle
    V.insert(V.end(), more.begin(), more.end());
    std::vector<Face> F = {{0, 1, 2, 3, 4, 5},       {6, 7, 8, 9, 10, 11},  {12, 13, 14, 15, 16},
                           {17, 18, 19, 20, 21, 22}, {23, 24, 25, 26, 27},  {28, 29, 30, 31, 32},
                           {34, 35, 36, 37, 38, 39, 40, 41, 42, 43},        {44, 45, 46, 44, 47, 48},
                           {6, 7, 33},               {49, 50, 51}};
    std::vector<Color> colors = {"red", Color(10, 200, 30), add::transparent("sky", 0.4), "#123456", "gold", "navy"};
    return from_faces(V, F, colors);
}

//: Two clockwise pentagons too small for a normal of their own (below EPS): off_pieces turns
//: them round -- one by ear clipping (its corners count as straight), one convex.
static Mesh tiny_faces() {
    Points V = {{0, 0, 10}, {0, 1e-5, 10}, {1e-5, 1e-5, 10}, {1.5e-5, 0.5e-5, 10}, {1e-5, 0, 10}};
    double r = 1.449e-5;
    for (int i = 0; i < 5; ++i) {
        double a = -2 * add::pi * i / 5;
        V.push_back({r * add::cos(a), r * add::sin(a), 11});
    }
    return from_faces(V, {{0, 1, 2, 3, 4}, {5, 6, 7, 8, 9}}, {"red", "blue"});
}

// -- numbers, words, letters ------------------------------------------------------

CASE(rounded_numbers) {
    const std::vector<double> xs = {0.0,   -0.0,  10.0,  100.0, 1234.0, -0.5,  -0.3,       0.3,      2.5,     3.5,
                                    0.12345678, -2.00005, 1e-5, -1e-5, 123.456, 1e20, -1e20, 5e-324, 1.0 / 3, -2.0 / 3,
                                    0.5,   1.5,   99.99995, 0.05, NAN_, -NAN_, INF, -INF};
    for (int d : {0, 1, 2, 4, 6, 9, 17, 30}) {
        std::vector<std::string> out;
        for (double x : xs) out.push_back(add::detail::rounded(x, d));
        record(join(out, " "));
    }
    record(outcome([] { add::detail::rounded(1.0, -1); }));
}

CASE(upper_letters) {
    for (auto range : {std::pair<long, long>{0, 0x180}, std::pair<long, long>{0x370, 0x530}}) {
        std::vector<std::string> out;
        for (long c = range.first; c < range.second; ++c) {
            std::string ch = add::detail::utf8_encode(c);
            std::string u = add::detail::py_upper(ch);
            if (u == ch) continue;
            std::vector<std::string> codes;
            for (size_t i = 0; i < u.size();) codes.push_back(fmt("%04lX", add::detail::utf8_next(u, i)));
            out.push_back(fmt("%04lX:", c) + join(codes, ","));
        }
        record((long long)out.size());
        record(join(out, " "));
    }
    record(show(add::detail::py_upper(
        "labas, pasauli! \xc4\x85\xc5\xbeuolas \xc3\x9f \xcf\x83\xce\xbf\xcf\x86\xce\xaf\xce\xb1 \xd1\x91\xd0\xb6")));
}

CASE(words_and_numbers) {
    const std::vector<std::string> lines = {
        "  a b\tc  ",
        "a\x0b" "b\x0c" "c\x1c" "d\x1d" "e\x1e" "f\x1f" "g\rh\ni",
        "x\xc2\xa0y\xe2\x80\x83z\xe3\x80\x80w\xc2\x85v\xe2\x80\xa8u\xe2\x80\xa9t\xe2\x80\xafs\xe2\x81\x9fr\xe1\x9a\x80q",
        "\xe2\x80\x8bp\xe2\x80\x8b",
        "",
        "   ",
        "one",
        "\xc3\xa9t\xc3\xa9 \xc4\x85"};
    for (const std::string& s : lines) {
        record(show(join(add::detail::py_split(s), "|")));
        record("[" + show(add::detail::py_strip(s)) + "]");
    }
    const std::vector<std::string> words = {
        "1_000", "1__0", "_1", "1_", "inf", "Infinity", "INFINITY", "iNf", "nan", "-nan", "+inf", "NaN", "1e400",
        "-1e400", "1e-400", "0x10", ".5", "5.", "1._5", "1_.5", "1e1_0", "1e_10", "1_e10", "in_f", ".", "e5",
        "1e", "1e+", "+.5e-3", "-.e1", "1.5E+3", "infinit", "nana", "+-1", "1.2.3", "00012", "0_0", "1.0_5",
        "1_0.5_5e1_2", "0.1", "2.5e-324", "1.7976931348623157e308", "1.8e308", "-0", "-0.0", "+7", "1.e5",
        B("1\x00"), "l", "--1", "9223372036854775807", "-9223372036854775808", "1,5", "+", "-", "", "12abc",
        "4.9406564584124654e-324", "0.30000000000000004", "123456789012345678901234567890.5", "1e-5", "1E5"};
    for (const std::string& w : words) {
        std::string f, i;
        try {
            f = add::detail::py_repr(add::detail::py_float(w));
        } catch (const std::invalid_argument&) {
            f = "ValueError";
        }
        try {
            i = std::to_string(add::detail::py_int(w));
        } catch (const std::invalid_argument&) {
            i = "ValueError";
        }
        record(show(w) + " float " + f + " int " + i);
    }
}

// -- writers -------------------------------------------------------------------------

CASE(ply_writer) {
    Mesh M = model();
    add::save(parity::current() + ".ply", M);
    add::save(parity::current() + "_raw.ply", M, std::nullopt, std::nullopt, false);
    add::save(parity::current() + "_2.ply", M, std::nullopt, 2);
    add::save(parity::current() + "_odd.ply", odd_faces(), std::nullopt, std::nullopt, false);
    add::save(parity::current() + "_oddclean.ply", odd_faces());
}

CASE(stl_writer) {
    Mesh M = model();
    add::save(parity::current() + ".stl", M);
    add::save(parity::current() + "_raw.stl", M, std::nullopt, std::nullopt, false);
    add::save(parity::current() + "_odd.stl", odd_faces(), std::nullopt, std::nullopt, false);
    // a huge triangle (its normal overflows: nan), a triangle without area, -0 coordinates
    Mesh big = from_faces({{0, 0, 0}, {1e200, 0, 0}, {0, 1e200, 0}, {1, 1, 1}, {2, 2, 2}, {3, 3, 3},
                           {-0.0, -0.0, 1}, {1, -0.0, 1}, {0, 1, 1}},
                          {{0, 1, 2}, {3, 4, 5}, {6, 7, 8}, {2, 1, 0}});
    add::save(parity::current() + "_big.stl", big, std::nullopt, std::nullopt, false);
}

CASE(save_forms) {
    Mesh M = model();
    add::box({0, 0, 0}, 1, "red");
    add::box({0, 2, 0}, 1, "blue");
    record(add::save(parity::current() + "_scene.off"));      // the scene -- then cleared
    record(add::scene().F.size());
    add::box({0, 0, 0}, 1, Color(1, 2, 3));
    add::box({2, 0, 0}, 1, Color(200, 2, 3));
    add::box({4, 0, 0}, 1, Color(1, 200, 3));
    add::save(parity::current() + "_scene.obj", add::scene(), std::nullopt, 2);   // limited to two colours
    record(add::scene().F.size());
    add::box({0, 0, 0}, 1, "red");
    add::save(parity::current() + "_scene.ply", add::scene(), false);            // the scene, kept
    record(add::scene().F.size());
    add::save(parity::current() + "_m.ply", M, true);          // another mesh, but the scene is cleared
    record(add::scene().F.size());
    add::box({0, 0, 0}, 1, "red");
    add::save(parity::current() + "_m.stl", M);               // a mesh: the scene stays
    record(add::scene().F.size());
    add::clear();
    record(add::save(parity::current() + "_noext", M));       // no extension: .off
    add::save(parity::current() + "_upper.OBJ", M);           // .OBJ: _upper.mtl
    add::save(parity::current() + "_upper.PLY", M);
    add::save(parity::current() + "_m_nc.off", M, std::nullopt, std::nullopt, false);
    add::save(parity::current() + "_m_nc.obj", M, std::nullopt, std::nullopt, false);
    add::save(parity::current() + "_m_3.off", M, std::nullopt, 3);
    add::save(parity::current() + "_empty.obj", Mesh());
    add::save(parity::current() + "_empty.stl", Mesh());
}

CASE(off_obj_writers) {
    Mesh M = model();
    record(add::off(parity::current() + "_exact.off", M));
    record(add::obj(parity::current() + "_exact.obj", M, parity::current() + "_custom.mtl"));
    record(add::obj(parity::current() + "_plain", M));        // not .obj: _plain.mtl
    add::box({0, 0, 0}, 1, "red");
    record(add::off(parity::current() + "_scene.off"));
    record(add::scene().F.size());
    add::box({0, 0, 0}, 1, "red");
    record(add::obj(parity::current() + "_scene.obj"));
    record(add::scene().F.size());
    exact(odd_faces(), "odd");
    exact(tiny_faces(), "tiny");
    add::save(parity::current() + "_odd.off", odd_faces());   // tidied: the concave faces cut first
}

CASE(sizes_and_names) {
    Mesh M = model();
    record(add::obj_size(M));
    record(outcome([] { add::obj_size(odd_faces()); }));      // a NaN vertex: _num raises
    record(outcome([] { add::obj_size(from_faces({{INF, NAN_, 0}}, {})); }));   // inf first: OverflowError
    record(add::obj_size(add::clean(odd_faces())));
    record(add::obj_size(Mesh()));
    record(add::obj_size(add::texture(add::make([] { add::sphere({0, 0, 0}, 1, 8, "red"); }), "globe.png", "sphere", 2.0)));
    add::box({0, 0, 0}, 1, "red");
    record(add::obj_size());
    add::clear();
    const std::vector<Color> colors = {"red", add::transparent("sky", 0.35), Color(1, 2, 3, 0.9994),
                                       with_image(Color(255, 0, 0, 1.0), "my tex-1.png"),
                                       with_image(Color(0, 0, 0, 0.5), "dir\\sub/wood.grain.jpg"),
                                       with_image(Color(9, 9, 9, 1.0), "noext"), with_image(Color(9, 9, 9, 1.0), ".hidden"),
                                       with_image(Color(1, 2, 3, 0.25), "\xc4\x85\xc5\xbeuolas.png"),
                                       Color(16, 32, 48, 0.001)};
    for (const Color& c : colors) record(add::detail::material_name(c));
    for (std::string name : {"img\\wood.png", "a/b/c.png", "plain.png", "dir/", ""})
        record("[" + add::detail::file_stem(name) + "]");
}

CASE(empty_faces) {
    Mesh M = from_faces({{0, 0, 0}, {1, 0, 0}, {1, 1, 0}}, {Face{}, Face{0}, Face{0, 1}, Face{0, 1, 2}, Face{2, 1}},
                        {"red", "blue", "gold", Color(1, 2, 3), add::transparent("sky", 0.5)});
    save_mesh(M);
    save_obj(M, "exact");
    add::save(parity::current() + ".ply", M, std::nullopt, std::nullopt, false);
    add::save(parity::current() + ".stl", M, std::nullopt, std::nullopt, false);
    for (std::string ext : {"obj", "off"}) {
        auto out = add::stream(parity::current() + "_stream." + ext, false);
        record(out->add(M));
        out->close();
        counts(*out);
    }
}

// -- the Stream -------------------------------------------------------------------

CASE(stream_obj_parts) {
    auto out = add::stream(parity::current() + ".obj");
    add::box({0, 0, 0}, 1, "red");
    record(out->add());                                        // the scene, then cleared
    record(add::scene().F.size());
    record(out->add(add::make([] { add::box({2, 0, 0}, 1, "red"); })));    // the same colour: no new usemtl
    record(out->add(add::opacity(add::make([] { add::box({4, 0, 0}, 1, "sky"); }), 0.4)));
    record(out->add(add::texture(add::make([] { add::box({6, 0, 0}, 1); }), "img/wood.png")));
    record(out->add(add::texture(add::make([] { add::cuboid({8, 0, 0}, {1, 2, 1}); }), "img/wood.png")));
    record(out->add(add::texture(add::make([] { add::box({10, 0, 0}, 1, "red"); }), "stone.jpg", "sphere", 2.0,
                                 std::nullopt)));
    add::box({0, 5, 0}, 1, "blue");
    record(out->add(add::scene(), false));                    // the scene again, not tidied
    record(add::scene().F.size());
    record(out->add(add::make([] { add::box({0, 7, 0}, 1, "red"); })));    // an old material comes back
    counts(*out);
    record(out->close());
    counts(*out);
    record(out->close());                                      // closing again does nothing
}

CASE(stream_obj_tidy) {
    auto out = add::stream(parity::current() + ".obj");
    Mesh B = add::make([] { add::box({0, 0, 0}, 1, "red"); });
    record(out->add(add::merge({B, add::move(B, {1, 0, 0})})));          // the wall between two boxes
    counts(*out);
    record(out->add(add::merge({add::make([] { add::box({0, 3, 0}, 2, "gold"); }),
                                add::make([] { add::box({0.25, 4.5, 0}, 1, "gold"); })})));   // a box standing on a box
    counts(*out);
    record(out->add(add::merge({B, B})));                     // every face twice
    counts(*out);
    record(out->add(add::merge({B, B}), false));              // not tidied: all written
    counts(*out);
    record(out->add(odd_faces()));
    counts(*out);
    out->close();
    counts(*out);
}

CASE(stream_obj_precision) {
    Mesh M = from_faces({{0, 0, 0}, {10, 0, 0}, {100, 0.5, 0}, {-0.5, 1.0 / 3, 2.5}, {1e-5, -1e-5, 1234.5678}},
                        {{0, 1, 2}, {0, 2, 3}, {1, 4, 3}}, {"red", "blue", Color(10, 20, 30)});
    for (int p : {4, 0, 2, 12}) {
        auto out = add::stream(parity::current() + "_" + std::to_string(p) + ".obj", false, p);
        record(out->add(M));
        record(out->add(add::move(M, {0.123456, -7.5, 1e6})));
        record(out->add(add::texture(add::make([] { add::box({0, 0, 0}, 1); }), "t.png", "sphere")));
        out->close();
        counts(*out);
    }
    auto out = add::stream(parity::current() + "_tidy.obj", true, 3);
    record(out->add(add::make([] { add::sphere({0.1234, 0, 0}, 1.0 / 3, 6, "green"); })));
    out->close();
    counts(*out);
    auto neg = add::stream(parity::current() + "_neg.obj", false, -1);
    record(outcome([&] { neg->add(M); }));                     // "%.-1f": a ValueError
    neg->close();
    counts(*neg);
}

CASE(stream_off_parts) {
    std::string name = parity::current() + ".off";
    auto out = add::stream(name);
    record(std::filesystem::exists(name));
    add::cylinder({0, 0, 0}, {0, 2, 0}, 1, 8, "red");          // 8-corner lids: pieces
    record(out->add());
    record(add::scene().F.size());
    record(out->add(add::opacity(add::make([] { add::box({3, 0, 0}, 1, "sky"); }), 0.4)));
    record(out->add(odd_faces(), false));
    record(out->add(odd_faces()));
    record(out->add(tiny_faces(), false));
    add::box({0, 5, 0}, 1, "blue");
    record(out->add(add::scene(), false));
    counts(*out);
    record(std::filesystem::exists(name + ".vertices~"));
    record(std::filesystem::exists(name + ".faces~"));
    record(out->close());
    counts(*out);
    record(std::filesystem::exists(name + ".vertices~"));
    record(std::filesystem::exists(name + ".faces~"));
    exact(add::load(name), "back");
}

CASE(stream_off_precision) {
    auto out = add::stream(parity::current() + ".off", false, 3);
    record(out->add(add::make([] { add::sphere({0.1234, 0, 0}, 1.0 / 3, 6, "green"); })));
    Mesh B = add::make([] { add::box({0, 0, 0}, 1, "red"); });
    record(out->add(add::merge({B, B}), true));               // tidied, as this part asks
    record(out->add(add::merge({B, add::move(B, {1e-7, 0, 0})})));
    counts(*out);
    out->close();
    counts(*out);
    auto out0 = add::stream(parity::current() + "_0.off", true, 0);
    record(out0->add(add::make([] { add::box({10, -0.25, 100}, 1, "red"); })));
    out0->close();
    counts(*out0);
}

CASE(stream_closed) {
    auto out = add::stream(parity::current() + ".obj");
    record(out->add(add::make([] { add::box({0, 0, 0}, 1, "red"); })));
    out->close();
    add::box({0, 0, 0}, 1, "blue");
    record(outcome([&] { out->add(); }));                      // closed: nothing written, the scene kept
    record(add::scene().F.size());
    record(outcome([&] { out->add(add::make([] { add::box({0, 0, 0}, 1); })); }));
    add::clear();
    counts(*out);
    {
        auto s = add::stream(parity::current() + "_with.obj");    // (Python: a with block) closed by the destructor
        s->add(add::make([] { add::box({0, 0, 0}, 1, "gold"); }));
        counts(*s);
    }
    {
        auto s = add::stream(parity::current() + "_with.off", true, 3);
        s->add(add::make([] { add::box({0, 0, 0}, 1, "gold"); }));
        counts(*s);
    }
}

CASE(texture_edges) {
    Mesh box = add::make([] { add::box({0, 0, 0}, 1, "red"); });
    Mesh bad = add::texture(box, "x.png", [](const Point& p, const Point&) { return add::Point2{p[0] > 0 ? NAN_ : 0.25, 0.5}; });   // some are no numbers
    Mesh worse = add::texture(box, "x.png", [](const Point&, const Point&) { return add::Point2{0.5, INF}; });
    record(outcome([&] { add::obj(parity::current() + "_nan.obj", bad); }));   // (_num raises; the .obj is left half written)
    record(outcome([&] { add::obj(parity::current() + "_inf.obj", worse); }));
    record(outcome([&] { add::obj_size(bad); }));                       // the size counts them the same way
    record(outcome([&] { add::obj_size(worse); }));
    Mesh plain = add::color(add::texture(box, "x.png"), "blue");       // texture coordinates, but no picture
    save_obj(plain, "plain");
    Mesh pinched = from_faces({{0, 0, 0}, {1, 0, 0}, {1, 1, 0}, {-1, 0, 0}, {-1, -1, 0}, {3, 3, 3}},
                              {{0, 1, 2, 0, 3, 4}, {1, 5, 2}}, {"red", "gold"});
    save_obj(add::texture(pinched, "p.png", "xy"), "pinched");   // split into loops, each with its coordinates
    auto out = add::stream(parity::current() + ".obj", false);
    record(out->add(add::texture(box, "\xc4\x85\xc5\xbeuolas.png")));   // letters that are not ASCII: bytes counts characters
    record(outcome([&] { out->add(bad); }));
    counts(*out);
    record(outcome([&] { out->add(worse); }));
    record(out->add(add::texture(add::move(box, {2, 0, 0}), "x.png")));   // vt numbers go on after the failed parts
    record(out->add(plain));
    record(out->add(add::texture(pinched, "p.png", "xy")));
    record(out->add(add::texture(box, "a/t.png")));              // two colours, one material name
    record(out->add(add::texture(box, "b/t.png")));
    counts(*out);
    out->close();
    counts(*out);
}

CASE(stream_names) {
    auto s = add::stream(parity::current() + "_SHOUT.OBJ");   // .OBJ is .obj: _SHOUT.mtl
    s->add(add::make([] { add::box({0, 0, 0}, 1, "red"); }));
    s->close();
    s = add::stream(parity::current() + "_plain");            // no extension: OFF
    s->add(add::make([] { add::box({0, 0, 0}, 1, "red"); }));
    s->close();
    counts(*s);
    s = add::stream(parity::current() + "_empty.obj");
    s->close();
    counts(*s);
    s = add::stream(parity::current() + "_empty.off");
    s->close();
    counts(*s);
}

// -- loading ----------------------------------------------------------------------

static const std::vector<std::pair<std::string, std::string>> OFF_FILES = {
    {"basic", B("OFF\n4 2 0\n0 0 0\n1 0 0\n1 1 0\n0 1 0\n3 0 1 2 255 0 0\n3 0 2 3\n")},
    {"comments", B("# a comment line\nOFF   # the header\n\n4 2 0 # counts\n0 0 0 # v0\n   1 0 0\n\n1 1 0\n0 1 0\n"
                   "# a face\n3 0 1 2 0.5 0.25 1.0\n4 0 1 2 3 1 1 1\n")},
    {"alpha", B("OFF\n3 7 0\n0 0 0\n1 0 0\n0 1 0\n3 0 1 2 255 0 0 128\n3 0 1 2 1.0 0.5 0.0 0.5\n3 0 1 2 0 0 0 0\n"
                "3 0 1 2 10 20 30 300\n3 0 1 2 0 0 1\n3 0 1 2 1 2 3 4 5 6\n3 0 1 2 0.2 0.4 0.6 1\n")},
    {"same_line", B("COFF 3 1\n0 0 0\n1 0 0\n0 1 0\n3 0 1 2 0 128 255\n")},
    {"two_on_header", B("OFF 7\n3 1 0\n0 0 0\n1 0 0\n0 1 0\n3 0 1 2\n")},
    {"no_header", B("3 1 0\n0 0 0\n1 0 0\n0 1 0\n3 2 1 0\n")},
    {"lower_header", B("noff\n3 1\n0 0 0\n1 0 0\n0 1 0\n3 0 1 2\n")},
    {"separators", B("OFF\r\n3 1 0\r\n0\t0 0\r1\x0b" "0\x0c" "0\n0\x1c" "1\x1d" "0\x1e\x1f\r\n3 0 1 2\xc2\xa0" "255\xe3\x80\x80"
                     "0\xe2\x80\x83" "0\xc2\x85\n")},
    {"numbers", B("OFF\n4 1 0\n1_000 -2.5e-3 +.5\n1e2 0 5.\n.5 1E-1 -0\n0 0 0\n4 0 1 2 3 0.25 0.5 0.75\n")},
    {"nonfinite", B("OFF\n4 2 0\ninf 0 0\n0 nan 0\n1e400 0 0\n0 0 0\n3 0 1 3\n3 1 2 3\n")},
    {"slices", B("OFF\n4 7 0\n0 0 0\n1 0 0\n1 1 0\n0 1 0\n5 0 1 2\n-1 5 6 7\n-2 0 1 2\n0 255 0 0\n2 0 1 9 9 9\n"
                 "-7 1 2\n1 3\n")},
    {"bom", B("\xef\xbb\xbf" "OFF\n3 1 0\n0 0 0\n1 0 0\n0 1 0\n3 0 1 2\n")},
    {"empty", B("")},
    {"only_comments", B("# nothing here\n\n   \n")},
    {"hexagon", B("OFF\n6 1 0\n0 0 0\n2 0 0\n3 1 0\n2 2 0\n0 2 0\n-1 1 0\n6 0 1 2 3 4 5 0 0 255\n")},
    {"extra_lines", B("OFF\n3 1 0\n0 0 0 7 8\n1 0 0\n0 1 0\n3 0 1 2\n3 2 1 0\nwhatever\n")},
    {"tabs_and_unicode", B("OFF\n3 1 0\n0\xe2\x80\x80" "0\xe2\x80\x8a" "0\n1 0\xe2\x80\xa9" "0\n0 1\xe2\x80\xaf" "0\xe2\x81\x9f\n"
                           "3 0 1\xe1\x9a\x80" "2\n")},
};

static const std::vector<std::string> OFF_ERRORS = {
    B("OFF\n1 0 0\n0 0\n"),
    B("OFF\n1 0 0\n0 0 x\n"),
    B("OFF\n2 0 0\n0 0 0\n"),
    B("OFF\nx 0 0\n"),
    B("OFF\n1\n"),
    B("OFF\n"),
    B("OFF\n0 1 0\n3 0 1 2 nan 0 0\n"),
    B("OFF\n0 1 0\n3 0 1 2 0.5 inf 0\n"),
    B("OFF\n0 1 0\n3 0 1 2 0.5 -inf 0\n"),
    B("OFF\n0 1 0\n3 0 1 2 -inf 0.5 0\n"),
    B("OFF\n0 1 0\n3 0 1 2 1 1 nan\n"),
    B("OFF\n0 1 0\n3 0 1 2.5\n"),
    B("OFF\n0 1 0\nx 0 1 2\n"),
    B("OFF\n1 0 0\n0x1 0 0\n"),
    B("OFF\n1 0 0\n0 0 0\xe2\x80\x8b\n"),
    B("OFF\n\xff\n"),
    B("OFF\n1 0 0\n\xc3\n"),
    B("OFF\n\xed\xa0\x80\n"),
    B("OFF\n\xf4\x90\x80\x80\n"),
    B("OFF\n\xe0\x80\x80\n"),
    B("OFF\n1 0 0\n1\x00 0 0\n"),
    B("OFF\n0 1 0\n3 0 1 2 1e308 1e309 0\n"),
    B("OFF\n0 1 0\n3 0 1 2 0.5 0.5 nan 0.5\n"),
};

CASE(load_off_files) {
    for (const auto& item : OFF_FILES) {
        std::string path = parity::current() + "_" + item.first + ".txt.off";
        write_file(path, item.second);
        Mesh M = add::load(path);
        record(item.first + ": " + std::to_string(M.V.size()) + " vertices, " + std::to_string(M.F.size()) + " faces");
        exact(M, item.first);
    }
    exact(add::load(parity::current() + "_alpha.txt.off", Color("navy")), "navy");   // one colour for every face
    exact(add::load(parity::current() + "_comments.txt.off", Color(0.5, 0.25, 1.0, 0.5)), "given");
    write_file(parity::current() + "_noext", OFF_FILES[0].second);  // no extension: read as .off
    exact(add::load(parity::current() + "_noext"), "noext");
}

CASE(load_off_errors) {
    for (size_t i = 0; i < OFF_ERRORS.size(); ++i) {
        std::string path = parity::current() + "_" + std::to_string(i) + ".txt.off";
        write_file(path, OFF_ERRORS[i]);
        record(std::to_string(i) + " " + outcome([&] { add::load(path); }));
    }
    record(outcome([] { add::load(parity::current() + "_missing.off"); }));
    std::filesystem::create_directory(parity::current() + "_folder.off");
    record(outcome([] { add::load(parity::current() + "_folder.off"); }));
    std::filesystem::remove(parity::current() + "_folder.off");
}

static const std::string MTL =
    B("# materials\nKd 0.1 0.2 0.3\nnewmtl red\nKd 1 0 0\nnewmtl glass\nKd 0.5 0.75 1.0\nd 0.25\n"
      "newmtl ghost\nKd 0 1 0\nTr 0.6\nnewmtl tex\nKd 1 1 1\nmap_Kd textures\\wood.png\n"
      "newmtl tiny\nKd 0.001 0.002 0.003\nnewmtl redefined\nKd 0 0 1\nnewmtl redefined\nKd 0 1 1\n"
      "newmtl texalpha\nmap_Kd -s 1 1 1 stone.png\nd 0.5\nKd 0.2 0.4 0.6\nnewmtl dbig\nd 50\n"
      "newmtl \xc5\xbe" "alias\r\nKd\t0.25 0.5 0.75\r\nd\n");

static const std::string OBJ =
    B("# model\nmtllib mats.mtl\no thing\nv 0 0 0\nv 1 0 0\nv 1 1 0\nv 0 1 0 # a comment\nvt 0 0\nvt 1 0\n"
      "vt 1 1\nvt 0.5\nf 1 2 3\nusemtl red\nf 1 2 3 4\nusemtl glass\nf -4 -3 -2\nusemtl tex\nf 1/1 2/2 3/3\n"
      "f 1/1/1 2/2/1 3/3/1 4/4/1\nf 1//1 2//1 3//1\nf 1/-4 2/-3 3/-2\nf 1/-5 2/-6 3/-7\nusemtl texalpha\n"
      "f 1/1 2/2 3/3\nusemtl tiny\nf 2 3 4\nusemtl nosuch\nf 1 3 4\nusemtl redefined\nf 1 2 4\n"
      "usemtl ghost\nf 1 2 3\nusemtl dbig\nf 2 3 4\ng group\ns off\nl 1 2\nvn 0 0 1\nf 1/2 2 3/1\n"
      "  #indented comment\n#f 1 2 3\nusemtl \xc5\xbe" "alias\nf 4 3 2 1\nf 0 1 2\nf 1 2 3/2/7/8\n");

static const std::vector<std::string> OBJ_ERRORS = {
    B("v 1 2\n"),
    B("v 0 0 0\nf 1 2 x\n"),
    B("v 0 0 0\nvt 0 0\nf 1/9 1/1 1/1\n"),
    B("mtllib\n"),
    B("usemtl\n"),
    B("vt\n"),
    B("v 0 0 0\nf 1 1 1 # c\n"),
    B("v 0 0 0\nf /1 1 1\n"),
    B("v 0 0 0\nvt 0 0\nf 1/0 1/1 1/1\n"),
    B("v 0 0 0\nvt 0 0\nf 1/-3 1/1 1/1\n"),
    B("v 0 0 0\nf 1.0 1 1\n"),
    B("v 0 0 0 \xe2\x80\x8b\nvt 1e999 0\n"),
};

CASE(load_obj_files) {
    const std::string name = parity::current();
    write_file("mats.mtl", MTL);
    write_file(name + ".txt.obj", OBJ);
    Mesh M = add::load(name + ".txt.obj");
    record(std::to_string(M.V.size()) + " vertices, " + std::to_string(M.F.size()) + " faces, uv " +
           (M.has_uv ? "True" : "False"));
    exact(M, "model");
    M = add::load(name + ".txt.obj", Color("gold"));          // one colour: the materials are not read
    exact(M, "gold");
    write_file(name + "_nomtl.txt.obj", B("mtllib nothere.mtl\nv 0 0 0\nv 1 0 0\nv 0 1 0\nusemtl red\nf 1 2 3\n"));
    exact(add::load(name + "_nomtl.txt.obj"), "nomtl");
    write_file(name + "_mtlerr.txt.obj", B("mtllib bad.mtl\nv 0 0 0\n"));
    write_file("bad.mtl", B("newmtl x\nKd 1 x 0\n"));
    record(outcome([&] { add::load(name + "_mtlerr.txt.obj"); }));   // a bad .mtl is an error, a missing one not
    std::filesystem::create_directory(name + "_sub");
    write_file(name + "_sub/mats.mtl", B("newmtl red\nKd 0 0 1\n"));
    write_file(name + "_sub/m.obj", B("mtllib mats.mtl\nv 0 0 0\nv 1 0 0\nv 0 1 0\nusemtl red\nf 1 2 3\n"));
    exact(add::load(name + "_sub/m.obj"), "sub");             // the .mtl next to the .obj
    write_file(name + "_sub\\m.obj", B("mtllib mats.mtl\nv 0 0 0\nv 1 0 0\nv 0 1 0\nusemtl red\nf 1 2 3\n"));
    exact(add::load(name + "_sub\\m.obj"), "backslash");     // a file named with a backslash: its .mtl in _sub/
    write_file(name + "_dirmtl.txt.obj", "mtllib " + name + "_sub\nv 0 0 0\n");
    record(outcome([&] { add::load(name + "_dirmtl.txt.obj"); }));   // a folder as the .mtl: left out
    std::filesystem::remove_all(name + "_sub");
    for (size_t i = 0; i < OBJ_ERRORS.size(); ++i) {
        std::string path = name + "_" + std::to_string(i) + ".txt.obj";
        write_file(path, OBJ_ERRORS[i]);
        record(std::to_string(i) + " " + outcome([&] { add::load(path); }));
    }
    record(outcome([&] { add::load(name + "_3.txt.obj", Color("red")); }));   // "mtllib" alone is fine with a colour
}

static const std::vector<std::pair<std::string, std::string>> PLY_FILES = {
    {"props", B("ply\nformat ascii 1.0\ncomment made by hand\nelement vertex 4\nproperty float x\nproperty float y\n"
                "property float z\nproperty float nx\nproperty uchar red\nelement face 5\n"
                "property list uchar int vertex_indices\nproperty uchar red\nproperty uchar green\n"
                "property uchar blue\nelement edge 1\nproperty int vertex1\nend_header\n0 0 0 1 255\n1 0 0 1 255\n"
                "1 1 0\n0 1 0 1 255 extra\n3 0 1 2 255 0 0\n3 0 2 3 0.5 0.25 1\n4 0 1 2 3\n3 0 1 3 0 0 1\n"
                "3 1 2 3 10 20 30 40\n0 1\n")},
    {"order", B("ply\nformat ascii 1.0\nelement vertex 3\nproperty float z\nproperty float y\nproperty float x\n"
                "property float x\nelement face 1\nproperty list uchar int vertex_indices\nend_header\n"
                "1 2 3 4\n5 6 7 8\n9 10 11\n3 0 1 2\n")},
    {"no_end", B("ply\nformat ascii 1.0\nelement vertex 0\nelement face 0\n")},
    {"blank_vertex", B("ply\nformat ascii 1.0\nelement vertex 3\nproperty float x\nproperty float y\nproperty float z\n"
                       "element face 1\nend_header\n\n1 0 0\n0 1 0\n3 0 1 2\n")},
    {"crlf", B("ply\r\nformat ascii 1.0\r\nelement vertex 3\r\nproperty float x\r\nproperty float y\r\n"
               "property float z\r\nelement face 2\r\nend_header\r\n0 0 0\r\n1 0 0\r\n0 1 0\r\n3 0 1 2 0 0 255\r"
               "-1 255 0\r\n")},
    {"no_vertex_props", B("ply\nelement vertex 2\nelement face 1\nend_header\n1 2 3\n4 5 6\n2 0 1\n")},
};

static const std::vector<std::string> PLY_ERRORS = {
    B("ply\nelement vertex 1\nproperty float x\n"),
    B("ply\nelement vertex 0\nelement face 1\nend_header\n\n"),
    B("ply\nelement vertex x\nend_header\n"),
    B("ply\nelement\nend_header\n"),
    B("ply\nelement vertex 0\nelement face 1\nend_header\n-3 1\n"),
    B("ply\nelement vertex 1\nproperty float x\nend_header\n1_0 2\n"),
    B("ply\nelement vertex 1\nproperty float x\nend_header\n0x1\n"),
    B("ply\nelement vertex 0\nelement face 1\nend_header\n3 0 1 2 nan 0 0\n"),
    B("ply\nelement vertex 0\nelement face 1\nend_header\n3 0 1 2 inf 0 0\n"),
    B("ply\nelement vertex 0\nelement face 1\nend_header\n3 0 1\n"),
};

CASE(load_ply_files) {
    for (const auto& item : PLY_FILES) {
        std::string path = parity::current() + "_" + item.first + ".txt.ply";
        write_file(path, item.second);
        Mesh M = add::load(path);
        record(item.first + ": " + std::to_string(M.V.size()) + " vertices, " + std::to_string(M.F.size()) + " faces");
        exact(M, item.first);
    }
    exact(add::load(parity::current() + "_props.txt.ply", Color(255, 0, 255, 0.5)), "given");
    write_file(parity::current() + "_upper.PLY", PLY_FILES[0].second);
    exact(add::load(parity::current() + "_upper.PLY"), "upper");
    for (size_t i = 0; i < PLY_ERRORS.size(); ++i) {
        std::string path = parity::current() + "_" + std::to_string(i) + ".txt.ply";
        write_file(path, PLY_ERRORS[i]);
        record(std::to_string(i) + " " + outcome([&] { add::load(path); }));
    }
}

CASE(load_roundtrip) {
    Mesh M = model();
    for (std::string ext : {"off", "obj", "ply", "OBJ"}) {
        add::save(parity::current() + "." + ext, M);
        Mesh L = add::load(parity::current() + "." + ext);
        record(ext + ": " + std::to_string(L.V.size()) + " vertices, " + std::to_string(L.F.size()) + " faces");
        exact(L, ext);
    }
    auto s = add::stream(parity::current() + "_stream.obj", true, 4);
    s->add(M);
    s->add(add::move(M, {0, 0, 10}));
    s->close();
    exact(add::load(parity::current() + "_stream.obj"), "stream");
}

// -- pictures ---------------------------------------------------------------------

//: The CRC-32 of the PNG standard, bit by bit (not the table add.hpp uses).
static uint32_t crc_bits(const std::string& data) {
    uint32_t c = 0xFFFFFFFFu;
    for (unsigned char b : data) {
        c ^= b;
        for (int k = 0; k < 8; ++k) c = (c >> 1) ^ (0xEDB88320u & (0u - (c & 1u)));
    }
    return ~c;
}

static uint32_t get32(const std::string& s, size_t pos) {
    uint32_t v = 0;
    for (size_t k = 0; k < 4; ++k) v = (v << 8) | (unsigned char)s.at(pos + k);
    return v;
}

//: The data of a zlib stream (RFC 1950) made of stored deflate blocks (RFC 1951, BTYPE 00) --
//: what add::write_png writes; an exception for anything else, a wrong LEN / NLEN or Adler-32.
static std::string inflate_stored(const std::string& z) {
    unsigned cmf = (unsigned char)z.at(0), flg = (unsigned char)z.at(1);
    if ((cmf & 0x0F) != 8 || (cmf >> 4) > 7 || (cmf * 256 + flg) % 31 != 0 || (flg & 0x20))
        throw std::runtime_error("zlib: a bad header");
    std::string out;
    size_t pos = 2;
    while (true) {
        unsigned head = (unsigned char)z.at(pos);
        if ((head >> 1) & 3) throw std::runtime_error("deflate: not a stored block");
        size_t len = (unsigned char)z.at(pos + 1) | ((size_t)(unsigned char)z.at(pos + 2) << 8);
        size_t nlen = (unsigned char)z.at(pos + 3) | ((size_t)(unsigned char)z.at(pos + 4) << 8);
        if ((len ^ 0xFFFF) != nlen || pos + 5 + len > z.size()) throw std::runtime_error("deflate: a bad LEN");
        out += z.substr(pos + 5, len);
        pos += 5 + len;
        if (head & 1) break;
    }
    uint32_t a = 1, b = 0;
    for (unsigned char x : out) {
        a = (a + x) % 65521;
        b = (b + a) % 65521;
    }
    if (get32(z, pos) != ((b << 16) | a) || pos + 4 != z.size()) throw std::runtime_error("zlib: a bad Adler-32");
    return out;
}

static std::string hex(const std::string& s) {
    std::string out;
    for (unsigned char c : s) out += fmt("%02x", c);
    return out;
}

//: Decode a PNG (check every chunk's CRC, inflate the zlib stream, checking its Adler-32), record
//: the header and the pixel bytes as png_record in cases_70_io.py does -- and delete the file:
//: add.py and add.hpp compress differently, so the files themselves differ.
static void png_record(const std::string& name) {
    std::string data;
    {
        std::ifstream f(name, std::ios::binary);
        data.assign(std::istreambuf_iterator<char>(f), std::istreambuf_iterator<char>());
    }
    record(std::string("signature ") + (data.compare(0, 8, std::string("\x89PNG\r\n\x1a\n", 8)) == 0 ? "ok" : "bad"));
    size_t pos = 8;
    std::string idat;
    std::vector<std::string> tags;
    uint32_t width = 0;
    while (pos < data.size()) {
        uint32_t n = get32(data, pos);
        std::string tag = data.substr(pos + 4, 4);
        std::string body = data.substr(pos + 8, n);
        uint32_t crc = get32(data, pos + 8 + n);
        tags.push_back(tag + (crc == crc_bits(tag + body) ? "" : "(bad crc)"));
        if (tag == "IHDR") {
            width = get32(body, 0);
            record(fmt("IHDR %u %u %u %u %u %u %u", get32(body, 0), get32(body, 4), (unsigned)(unsigned char)body[8],
                       (unsigned)(unsigned char)body[9], (unsigned)(unsigned char)body[10],
                       (unsigned)(unsigned char)body[11], (unsigned)(unsigned char)body[12]));
        } else if (tag == "IDAT") {
            idat += body;
        }
        pos += 12 + n;
    }
    record("chunks " + join(tags, " "));
    std::string raw = inflate_stored(idat);
    record(fmt("raw bytes %zu", raw.size()));
    size_t stride = std::max<size_t>(1 + 3 * (size_t)width, 1);
    for (size_t y = 0; y < raw.size(); y += stride) record(hex(raw.substr(y, stride)));
    std::remove(name.c_str());
}

CASE(png_pictures) {
    using Rows = std::vector<std::vector<Color>>;
    Rows rows;
    for (int y = 0; y < 64; ++y) {
        rows.emplace_back();
        for (int x = 0; x < 64; ++x) rows.back().push_back((x / 8 + y / 8) % 2 ? "white" : "black");
    }
    record(add::write_png(parity::current() + "_check.png", rows));
    png_record(parity::current() + "_check.png");
    rows.clear();
    for (int y = 0; y < 150; ++y) {                            // 3 stored blocks
        rows.emplace_back();
        for (int x = 0; x < 300; ++x) rows.back().push_back(add::hsv(x / 300.0, 1.0 - y / 200.0));
    }
    add::write_png(parity::current() + "_wide.png", rows);
    png_record(parity::current() + "_wide.png");
    add::write_png(parity::current() + "_one.png", Rows{{Color("red")}});
    png_record(parity::current() + "_one.png");
    add::write_png(parity::current() + "_none.png", Rows{});
    png_record(parity::current() + "_none.png");
    add::write_png(parity::current() + "_ragged.png", Rows{{Color("red"), Color("blue")}, {Color("green")}, {}});
    png_record(parity::current() + "_ragged.png");
    add::write_png(parity::current() + "_forms.png", Rows{{Color(0.5, 0.25, 1.0), Color("#ff8800"),
                                                            add::transparent("sky", 0.3), Color(300, -5, 12),
                                                            Color("#abc")}});
    png_record(parity::current() + "_forms.png");
    rows.clear();
    for (int y = 0; y < 4; ++y) {
        rows.emplace_back();
        for (int x = 0; x < 256; ++x) rows.back().push_back(Color(x, (x * 7 + y) % 256, 255 - x));
    }
    add::write_png(parity::current() + "_exact.png", rows);
    png_record(parity::current() + "_exact.png");
}

// -- letters ----------------------------------------------------------------------

static void make_font() {
    std::filesystem::create_directory("font");
    add::cuboid({0, 0.5, 0}, {0.6, 1, 0.2}, "red");
    add::cuboid({0, 1.1, 0}, {0.9, 0.2, 0.2}, "red");
    add::off("font/A.off");
    add::box({0, 0, 0}, 1, "blue");
    add::tetrahedron({0, 1, 0}, 0.5, "green");
    add::off("font/B.off");
    add::pyramid({0, 0, 0}, 1, 1.5, "gold");
    add::off("font/\xc4\x84.off");
    add::cuboid({0, 0, 0}, {0.2, 1, 0.2}, "navy");
    add::off("font/1.off");
    add::cylinder({0, 0, 0}, {0, 0.7, 0}, 0.3, 6, "teal");
    add::off("font/q.off");
    add::box({0, 0, 0}, 0.5, "lime");
    add::off("font/SS.off");                                   // what "\xc3\x9f" in upper case gives
    write_file("font/E.off", B("OFF\n0 0 0\n"));               // an empty glyph
    write_file("font/X.off", B("OFF\n1 0 0\n0 0 x\n"));        // a ValueError: left out
    std::filesystem::create_directory("font/D.off");           // a folder: an OSError, left out
    add::box({0, 0, 0}, 1, "purple");
    add::obj("font/Y.obj");
    add::cuboid({0, 0, 0}, {1, 2, 3}, "pink");
    add::obj("font/A.obj");
    std::filesystem::create_directory("font2");
    write_file("font2/T.off", B("OFF\n2 0 0\n0 0 0\n"));       // an IndexError: not caught
}

static std::vector<std::string> keys(const std::map<std::string, Mesh>& font) {
    std::vector<std::string> out;
    for (const auto& item : font) out.push_back(item.first);
    return out;
}

CASE(fonts) {
    make_font();
    struct Cleanup {                                           // (Python: try / finally)
        ~Cleanup() {
            std::error_code ec;
            std::filesystem::remove_all("font", ec);
            std::filesystem::remove_all("font2", ec);
        }
    } cleanup;
    auto font = add::load_font("font");
    record(keys(font));
    for (const auto& item : font)
        record(fmt("%s %zu vertices %zu faces", item.first.c_str(), item.second.V.size(), item.second.F.size()));
    record(keys(add::load_font("font", std::string("AQB\xc4\x84"))));
    record(keys(add::load_font("font", std::vector<std::string>{"A", "B", "Y", "AB"}, ".obj")));
    record(keys(add::load_font("font", std::nullopt, ".obj")));
    record(add::load_font("no_such_folder").size());
    record(add::load_font("font/A.off").size());              // a file, not a folder
    record(add::load_font("font", std::nullopt, "").size());
    record(keys(add::load_font("font/", std::string("A1"))));
    record(outcome([] { add::load_font("font2"); }));
    exact(add::typeset("AB A", font), "plain");
    exact(add::typeset("ab \xc4\x85 1q?E", font, {1, 2, 3}, 0.5, 1.5, Color("navy"), {Point{0, 0, 1}, Point{0, 1, 0}}),
          "options");
    exact(add::typeset("\xc4\x85" "A\xc4\x84", font, {0, 0, 0}, 2.0, 0.5, add::transparent("red", 0.5)), "accents");
    exact(add::typeset("", font), "none");
    exact(add::typeset("zz", font), "missing");
    exact(add::typeset("\xc3\x9f" "A" "\xf0\x9f\x98\x80" "B" "\xc5\x89", font, {0, 0, 0}, 1.0, 2.0), "wide");   // an emoji is one character
    record(keys(add::load_font("font", std::string("A\xf0\x9f\x98\x80"))));
    auto obj_font = add::load_font("font", std::nullopt, ".obj");
    exact(add::typeset("AYA", obj_font, {0, 0, 0}, 1.0, 1.0, std::nullopt, {Point{1, 1, 0}, Point{0, 1, 0}}), "obj");
}

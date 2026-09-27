// 21 -- loading models from files, and writing with them.
//
// Not everything has to be computed. ``load`` reads an .off, .obj or .ply
// file back into a mesh you can move, scale and paint like any other;
// ``load_font`` reads a whole folder of letters at once, and ``typeset`` lays a
// word out with them.
//
// The letter and digit models used here are the ones that have come with the
// course for years; they live in ``tests/legacy/letters`` and
// ``tests/legacy/numbers``.
#include "add.hpp"

// (Python finds its own folder from __file__; in C++, __FILE__ is this source file as it was compiled.)
const std::filesystem::path HERE = std::filesystem::path(__FILE__).parent_path();
const std::string LETTERS = (HERE / ".." / "tests" / "legacy" / "letters").string();
const std::string DIGITS = (HERE / ".." / "tests" / "legacy" / "numbers").string();

int main() {
    std::map<std::string, add::Mesh> font = add::load_font(LETTERS);
    std::map<std::string, add::Mesh> digits = add::load_font(DIGITS);
    std::printf("loaded %zu letters and %zu digits\n", font.size(), digits.size());

    // --------------------------------------------------------------------------
    //  a word, standing on a plinth
    // --------------------------------------------------------------------------
    add::Mesh word = add::typeset("ADD", font, {0, 0, 0}, 1.6, 1.15, "gold");
    word = add::rotateX(word, -add::pi / 2, {0, 0, 0});      // lay it flat, face up
    word = add::place(word, {0, 1.05, 0});
    add::mesh(word);

    add::Mesh version = add::typeset("2", digits, {0, 0, 0}, 0.9, 1.0, "silver");
    version = add::rotateX(version, -add::pi / 2, {0, 0, 0});
    add::mesh(add::place(version, {2.9, 1.0, 0}));

    add::cuboid({1.1, 0.4, 0}, {7.0, 0.9, 2.2}, {70, 60, 55});
    add::cuboid({1.1, -0.1, 0}, {7.6, 0.25, 2.8}, {50, 42, 38});

    // --------------------------------------------------------------------------
    //  the alphabet arranged on a ring, each letter turned to face outwards
    // --------------------------------------------------------------------------
    add::push();
    std::vector<std::string> names;                    // sorted(font): a std::map keeps its keys sorted
    for (const auto& entry : font) names.push_back(entry.first);
    for (int i = 0; i < (int)names.size(); ++i) {
        const std::string& ch = names[i];
        double a = 2 * add::pi * i / names.size();
        add::Mesh glyph_mesh = add::fit(font[ch], 0.9);
        glyph_mesh = add::rotateX(glyph_mesh, -add::pi / 2, {0, 0, 0});
        glyph_mesh = add::rotateY(glyph_mesh, -a + add::pi / 2, {0, 0, 0});
        glyph_mesh = add::color(glyph_mesh, add::hsv(i / double(names.size()), 0.6, 1.0));
        add::mesh(add::move(add::place(glyph_mesh, {0, 0, 0}),
                            {5.5 * add::cos(a), 0, 5.5 * add::sin(a)}));
    }
    add::Mesh ring = add::pop();
    add::mesh(add::move(ring, {1.1, 0.95, 0}));

    // --------------------------------------------------------------------------
    //  loading back a model this library itself wrote
    // --------------------------------------------------------------------------
    add::push();
    add::torus({0, 0, 0}, 1.2, 0.35, 48, 24, "teal");
    add::save("ring_for_reloading.off");
    add::pop();

    add::Mesh reloaded = add::load("ring_for_reloading.off");
    std::remove("ring_for_reloading.off");           // it was only a demonstration
    std::printf("reloaded %zu faces\n", reloaded.polygons());
    add::mesh(add::move(add::rotateX(reloaded, add::pi / 2), {1.1, 3.2, 0}));

    add::check();
    add::save("text.off");
}

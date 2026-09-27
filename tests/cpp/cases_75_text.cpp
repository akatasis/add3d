#include "parity.hpp"

using add::Point;
using add::Point2;

// Every character of the font, and some it does not have (drawn as a box).  The .txt files
// only get numbers: a character is written as its code point.
static const std::vector<std::string> ALL{"ABCDEFGHIJKLMNOPQRSTUVWXYZ", "0123456789", " .,:;!?-+=*/\\()[]'\"_%#<>^&@$|",
                                          "ĄČĘĖĮŠŲŪŽ", "ąčęėįšųūž", "ÄÖÜĀĒĪŌŇŘĚĎŤ", "äöüāēīōňřěďť",
                                          "abcdefghijklmnopqrstuvwxyz", "ıſ"};
static const std::vector<std::string> EXTRA{"ß~{}`€\t\r", "ÿÅåẞ😀", "é"};

CASE(font_tables) {
    std::vector<std::string> all = ALL;
    all.insert(all.end(), EXTRA.begin(), EXTRA.end());
    for (const std::string& s : all)
        for (char32_t ch : add::detail::text_code_points(s)) {
            add::detail::Glyph g = add::detail::strokes(ch);
            record((long long)ch);
            record(g.width);
            record((long long)g.strokes.size());
            for (const add::Profile& line : g.strokes) record(line);
        }
}

CASE(upper_map) {
    // Every character whose upper case the font has, and that upper case.
    for (char32_t cp = 0; cp < 0x110000; ++cp) {
        char32_t u = add::detail::font_upper(cp);
        if (add::detail::FONT().count(u) || add::detail::LETTERS().count(u))
            record(std::to_string((long long)cp) + " " + std::to_string((long long)u));
    }
}

CASE(text_widths) {
    for (const char* s : {"", "A", "I", " ", "AB", "LABAS 2026", "Hello, World!", "ĄČĘĖĮŠŲŪŽ", "ąčę", "a\nb", "€",
                          "iiii", "...", "é", "ıſ", "ß"}) {
        record(add::text_width(s));
        record(add::text_width(s, 2.5));
        record(add::text_width(s, 0.5, 0.0));
        record(add::text_width(s, 1.0, -3.0));
        record(add::text_width(s, -1.0, 2.0));
    }
}

CASE(text_capitals) {
    record(add::text("ABCDEFGHIJKLM", {0, 0, 0}));
    record(add::text("NOPQRSTUVWXYZ", {0, -1.6, 0}));
    save_case();
}

CASE(text_digits_punctuation) {
    record(add::text("0123456789", {0, 0, 0}, 0.8, std::nullopt, "red"));
    record(add::text(" .,:;!?-+=*/\\()[]'\"_%#<>^&@$|", {0, 2, 0}, 0.8, std::nullopt, "blue"));
    save_case();
}

CASE(text_lithuanian) {
    record(add::text("ĄČĘĖĮŠŲŪŽ\nąčęėįšųūž", {0, 0, 0}, 1.0, std::nullopt, "gold"));
    record(add::text("Ąžuolas, Šilutė, Įstrigęs ŪKININKAS", {0, -4, 0}, 0.5, 0.03, "green"));
    save_case();
}

CASE(text_other_accents) {
    record(add::text("ÄÖÜĀĒĪŌŇŘĚĎŤ\näöüāēīōňřěďť", {0, 0, 0}, 0.7, std::nullopt, "teal"));
    save_case();
}

CASE(text_lower_and_unknown) {
    record(add::text("abcdefghijklm\nnopqrstuvwxyz", {0, 0, 0}, 0.6));
    record(add::text("ıſ ß~{}`€ ÿÅåẞ😀 é\tX\r", {0, -3, 0}, 0.6, std::nullopt, "red"));
    save_case();
}

CASE(text_options) {
    record(add::text("LABAS 2026", {0, 0, 0}, 1.0, std::nullopt, "navy"));
    record(add::text("Center\nof it all", {0, 3, 0}, 0.8, 0.05, "red", {1, 0, 0}, {0, 1, 0}, "center"));
    record(add::text("RIGHT\nALIGNED\n", {0, 6, 0}, 0.5, std::nullopt, "blue", {1, 0, 0}, {0, 1, 0}, "right"));
    record(add::text("flat", {0, 0, 5}, 1.0, 0.03, "gold", {1, 0, 0}, {0, 0, -1}));
    record(add::text("tilted", {3, 0, 5}, 1.2, std::nullopt, add::DEFAULT_COLOR, {1, 1, 0}, {0, 0, 1}, "left", 0.5, 4));
    record(add::text("wide", {0, 9, 0}, 1.0, std::nullopt, "teal", {2, 0, 0}, {0, 3, 0}, "left", 2.5, 3));
    record(add::text("", {0, 12, 0}));
    record(add::text("\n\n", {0, 12, 0}));
    record(add::text("x", {0, 13, 0}, 1.0, std::nullopt, add::DEFAULT_COLOR, {0, 0, 0}, {0, 1, 0}));   // u = 0
    record(add::text("neg", {0, 15, 0}, -1.0, std::nullopt, "pink"));
    record(add::text("K!", {5, 15, 0}, 2.0, 0.0, "brown", {0, 1, 0}, {-1, 0, 0}, "middle", 1.0, 5));
    record(add::text("thin", {0, 18, 0}, 1.0, std::nullopt, {0.1, 0.9, 0.4}, {1, 0, 0}, {0, 1, 0}, "center", 0.0, 1));
    save_case();
}

CASE(text_aliases) {
    record(add::write("WRITE", {0, 0, 0}, 0.7, 0.04, "red"));
    record(add::label("Label", {0, 2, 0}, 0.7, std::nullopt, "blue", {0, 0, 1}, {0, 1, 0}, "center", 1.2, 6));
    add::glyph("G", {0, 4, 0}, {1, 0, 0}, {0, 1, 0});
    add::glyph("Ž", {2, 4, 0}, {0, 0, 1}, {0, 1, 0}, 0.8, 0.05, "gold");
    add::glyph("?", {4, 4, 0}, {1, 0, 0}, {0, 0, 1}, 1.5, 0.1, {10, 200, 30});
    add::glyph("", {6, 4, 0}, {1, 0, 0}, {0, 1, 0});
    add::glyph("AB", {6, 4, 0}, {1, 0, 0}, {0, 1, 0}, 0.5);
    add::glyph("į", {9, 4, 0}, {1, 0, 0}, {0, 1, 0}, 1.0, 0.02);
    save_case();
}

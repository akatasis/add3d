// ============================================================================
//  18. Letters and labels
//      (add.py: _src/75_text.py)
// ============================================================================
namespace add {

namespace detail {
//: One character of the stroke font: its advance width and its strokes, each a polyline on a
//: grid that is 4 units wide and 6 units tall (Y up).
struct Glyph {
    double width = 4;
    std::vector<Profile> strokes;
};
//: The stroke font (add.py's _FONT), by character (a Unicode code point).
inline const std::map<char32_t, Glyph>& FONT();
//: The accents of the Lithuanian letters, drawn on top of the base letter (add.py's _ACCENTS).
inline const std::map<std::string, std::vector<Profile>>& ACCENTS();
//: The accented letters: (base letter, accent) (add.py's _LETTERS).
inline const std::map<char32_t, std::pair<char32_t, std::string>>& LETTERS();
//: What Python's ``ch.upper()`` gives for a character, as far as the font can tell: the upper case
//: of every character whose upper case the font has (a-z, the lower-case accented letters, and
//: dotless i and long s); any other character comes back as it is (it is drawn as a box either way).
inline char32_t font_upper(char32_t ch);
//: The characters of a UTF-8 string, as the code points Python's str holds (a malformed
//: character counts as one, U+FFFD).
inline std::vector<char32_t> text_code_points(const std::string& s);
//: (advance width, [polyline, ...]) for one character (add.py's _strokes).
inline Glyph strokes(char32_t ch);
}  // namespace detail

//: The width a line of text() will take up, in model units.
inline double text_width(const std::string& string, double size = 1.0, double spacing = 1.0);
//: Write a label into the scene as round bars (UTF-8 text; lower case is drawn as capitals;
//: "\n" starts a new line; ``align``: "left", "center" or "right").  Returns the widest line's width.
inline double text(const std::string& string, const Point& at = {0, 0, 0}, double size = 1.0,
                   std::optional<double> thickness = std::nullopt, const Color& color = DEFAULT_COLOR,
                   const Point& u = {1, 0, 0}, const Point& v = {0, 1, 0}, const std::string& align = "left",
                   double spacing = 1.0, int k = 8);
//: ``write`` and ``label`` are other names for text().
inline double write(const std::string& string, const Point& at = {0, 0, 0}, double size = 1.0,
                    std::optional<double> thickness = std::nullopt, const Color& color = DEFAULT_COLOR,
                    const Point& u = {1, 0, 0}, const Point& v = {0, 1, 0}, const std::string& align = "left",
                    double spacing = 1.0, int k = 8);
inline double label(const std::string& string, const Point& at = {0, 0, 0}, double size = 1.0,
                    std::optional<double> thickness = std::nullopt, const Color& color = DEFAULT_COLOR,
                    const Point& u = {1, 0, 0}, const Point& v = {0, 1, 0}, const std::string& align = "left",
                    double spacing = 1.0, int k = 8);
//: Draw one character as thin bars in the u/v plane.
inline void glyph(const std::string& letter, const Point& origin, const Point& u, const Point& v, double size = 1.0,
                  double thickness = 0.04, const Color& color = DEFAULT_COLOR);

}  // namespace add
//@@definitions
namespace add {

namespace detail {

inline const std::map<char32_t, Glyph>& FONT() {
    static const std::map<char32_t, Glyph> table = {
        {U'A', {4, {{{0, 0}, {0, 4}, {2, 6}, {4, 4}, {4, 0}}, {{0, 2}, {4, 2}}}}},
        {U'B', {4, {{{0, 0}, {0, 6}, {3, 6}, {4, 5}, {4, 4}, {3, 3}, {0, 3}},
                    {{3, 3}, {4, 2}, {4, 1}, {3, 0}, {0, 0}}}}},
        {U'C', {4, {{{4, 5}, {3, 6}, {1, 6}, {0, 5}, {0, 1}, {1, 0}, {3, 0}, {4, 1}}}}},
        {U'D', {4, {{{0, 0}, {0, 6}, {3, 6}, {4, 5}, {4, 1}, {3, 0}, {0, 0}}}}},
        {U'E', {4, {{{4, 6}, {0, 6}, {0, 0}, {4, 0}}, {{0, 3}, {3, 3}}}}},
        {U'F', {4, {{{4, 6}, {0, 6}, {0, 0}}, {{0, 3}, {3, 3}}}}},
        {U'G', {4, {{{4, 5}, {3, 6}, {1, 6}, {0, 5}, {0, 1}, {1, 0}, {3, 0}, {4, 1},
                     {4, 3}, {2, 3}}}}},
        {U'H', {4, {{{0, 0}, {0, 6}}, {{4, 0}, {4, 6}}, {{0, 3}, {4, 3}}}}},
        {U'I', {2, {{{0, 6}, {2, 6}}, {{1, 6}, {1, 0}}, {{0, 0}, {2, 0}}}}},
        {U'J', {4, {{{4, 6}, {4, 1}, {3, 0}, {1, 0}, {0, 1}}}}},
        {U'K', {4, {{{0, 0}, {0, 6}}, {{4, 6}, {0, 2}}, {{1.3, 3}, {4, 0}}}}},
        {U'L', {4, {{{0, 6}, {0, 0}, {4, 0}}}}},
        {U'M', {4, {{{0, 0}, {0, 6}, {2, 3}, {4, 6}, {4, 0}}}}},
        {U'N', {4, {{{0, 0}, {0, 6}, {4, 0}, {4, 6}}}}},
        {U'O', {4, {{{1, 0}, {0, 1}, {0, 5}, {1, 6}, {3, 6}, {4, 5}, {4, 1}, {3, 0}, {1, 0}}}}},
        {U'P', {4, {{{0, 0}, {0, 6}, {3, 6}, {4, 5}, {4, 4}, {3, 3}, {0, 3}}}}},
        {U'Q', {4, {{{1, 0}, {0, 1}, {0, 5}, {1, 6}, {3, 6}, {4, 5}, {4, 1}, {3, 0}, {1, 0}},
                    {{2.5, 1.5}, {4.3, -0.3}}}}},
        {U'R', {4, {{{0, 0}, {0, 6}, {3, 6}, {4, 5}, {4, 4}, {3, 3}, {0, 3}}, {{2, 3}, {4, 0}}}}},
        {U'S', {4, {{{4, 5}, {3, 6}, {1, 6}, {0, 5}, {0, 4}, {1, 3}, {3, 3}, {4, 2},
                     {4, 1}, {3, 0}, {1, 0}, {0, 1}}}}},
        {U'T', {4, {{{0, 6}, {4, 6}}, {{2, 6}, {2, 0}}}}},
        {U'U', {4, {{{0, 6}, {0, 1}, {1, 0}, {3, 0}, {4, 1}, {4, 6}}}}},
        {U'V', {4, {{{0, 6}, {2, 0}, {4, 6}}}}},
        {U'W', {4, {{{0, 6}, {1, 0}, {2, 4}, {3, 0}, {4, 6}}}}},
        {U'X', {4, {{{0, 0}, {4, 6}}, {{0, 6}, {4, 0}}}}},
        {U'Y', {4, {{{0, 6}, {2, 3}, {4, 6}}, {{2, 3}, {2, 0}}}}},
        {U'Z', {4, {{{0, 6}, {4, 6}, {0, 0}, {4, 0}}}}},
        {U'0', {4, {{{1, 0}, {0, 1}, {0, 5}, {1, 6}, {3, 6}, {4, 5}, {4, 1}, {3, 0}, {1, 0}},
                    {{0.6, 1}, {3.4, 5}}}}},
        {U'1', {4, {{{0.5, 4.5}, {2, 6}, {2, 0}}, {{0.5, 0}, {3.5, 0}}}}},
        {U'2', {4, {{{0, 5}, {1, 6}, {3, 6}, {4, 5}, {4, 4}, {0, 0}, {4, 0}}}}},
        {U'3', {4, {{{0, 6}, {4, 6}, {2, 3.5}, {3, 3.5}, {4, 2.5}, {4, 1}, {3, 0}, {1, 0}, {0, 1}}}}},
        {U'4', {4, {{{3, 0}, {3, 6}, {0, 2}, {4, 2}}}}},
        {U'5', {4, {{{4, 6}, {0, 6}, {0, 3}, {3, 3}, {4, 2}, {4, 1}, {3, 0}, {1, 0}, {0, 1}}}}},
        {U'6', {4, {{{4, 5}, {3, 6}, {1, 6}, {0, 5}, {0, 1}, {1, 0}, {3, 0}, {4, 1}, {4, 2},
                     {3, 3}, {0, 3}}}}},
        {U'7', {4, {{{0, 6}, {4, 6}, {1.5, 0}}}}},
        {U'8', {4, {{{1, 3}, {0, 4}, {0, 5}, {1, 6}, {3, 6}, {4, 5}, {4, 4}, {3, 3}, {1, 3},
                     {0, 2}, {0, 1}, {1, 0}, {3, 0}, {4, 1}, {4, 2}, {3, 3}}}}},
        {U'9', {4, {{{4, 3}, {1, 3}, {0, 4}, {0, 5}, {1, 6}, {3, 6}, {4, 5}, {4, 1}, {3, 0},
                     {1, 0}, {0, 1}}}}},
        {U' ', {2, {}}},
        {U'.', {1, {{{0.5, 0}, {0.5, 0.3}}}}},
        {U',', {1, {{{0.6, 0.5}, {0.3, -0.8}}}}},
        {U':', {1, {{{0.5, 1}, {0.5, 1.3}}, {{0.5, 4}, {0.5, 4.3}}}}},
        {U';', {1, {{{0.6, 1}, {0.3, -0.5}}, {{0.5, 4}, {0.5, 4.3}}}}},
        {U'!', {1, {{{0.5, 6}, {0.5, 2}}, {{0.5, 0}, {0.5, 0.3}}}}},
        {U'?', {4, {{{0, 5}, {1, 6}, {3, 6}, {4, 5}, {4, 4}, {2, 2.5}, {2, 1.8}}, {{2, 0}, {2, 0.3}}}}},
        {U'-', {4, {{{0.5, 3}, {3.5, 3}}}}},
        {U'+', {4, {{{0.5, 3}, {3.5, 3}}, {{2, 1.5}, {2, 4.5}}}}},
        {U'=', {4, {{{0.5, 2}, {3.5, 2}}, {{0.5, 4}, {3.5, 4}}}}},
        {U'*', {4, {{{0.5, 1.5}, {3.5, 4.5}}, {{0.5, 4.5}, {3.5, 1.5}}, {{2, 1}, {2, 5}}}}},
        {U'/', {4, {{{0, 0}, {4, 6}}}}},
        {U'\\', {4, {{{0, 6}, {4, 0}}}}},
        {U'(', {2, {{{1.5, 6.5}, {0.4, 5}, {0.4, 1}, {1.5, -0.5}}}}},
        {U')', {2, {{{0.5, 6.5}, {1.6, 5}, {1.6, 1}, {0.5, -0.5}}}}},
        {U'[', {2, {{{1.6, 6.5}, {0.4, 6.5}, {0.4, -0.5}, {1.6, -0.5}}}}},
        {U']', {2, {{{0.4, 6.5}, {1.6, 6.5}, {1.6, -0.5}, {0.4, -0.5}}}}},
        {U'\'', {1, {{{0.5, 6}, {0.5, 4.5}}}}},
        {U'"', {2, {{{0.4, 6}, {0.4, 4.5}}, {{1.6, 6}, {1.6, 4.5}}}}},
        {U'_', {4, {{{0, -0.5}, {4, -0.5}}}}},
        {U'%', {4, {{{0, 0}, {4, 6}}, {{0, 4.5}, {0, 6}, {1.5, 6}, {1.5, 4.5}, {0, 4.5}},
                    {{2.5, 0}, {2.5, 1.5}, {4, 1.5}, {4, 0}, {2.5, 0}}}}},
        {U'#', {4, {{{1, 0}, {1.5, 6}}, {{2.5, 0}, {3, 6}}, {{0, 2}, {4, 2}}, {{0, 4}, {4, 4}}}}},
        {U'<', {4, {{{4, 6}, {0, 3}, {4, 0}}}}},
        {U'>', {4, {{{0, 6}, {4, 3}, {0, 0}}}}},
        {U'^', {4, {{{0.5, 4}, {2, 6}, {3.5, 4}}}}},
        {U'&', {4, {{{4, 0}, {1, 3.5}, {1, 5}, {2, 6}, {3, 5}, {3, 4}, {0, 1.5}, {1, 0}, {2, 0}, {4, 2.5}}}}},
        {U'@', {4, {{{3, 2}, {3, 4}, {1.5, 4}, {1.5, 2}, {3.3, 2}, {4, 3}, {4, 5}, {3, 6}, {1, 6},
                     {0, 5}, {0, 1}, {1, 0}, {3.5, 0}}}}},
        {U'$', {4, {{{4, 5}, {3, 6}, {1, 6}, {0, 5}, {0, 4}, {1, 3}, {3, 3}, {4, 2}, {4, 1},
                     {3, 0}, {1, 0}, {0, 1}}, {{2, -0.5}, {2, 6.5}}}}},
        {U'|', {1, {{{0.5, -0.5}, {0.5, 6.5}}}}},
    };
    return table;
}

inline const std::map<std::string, std::vector<Profile>>& ACCENTS() {
    static const std::map<std::string, std::vector<Profile>> table = {
        {"caron", {{{1, 8}, {2, 7}, {3, 8}}}},                 // Č Š Ž
        {"dot", {{{2, 7.3}, {2, 7.6}}}},                       // Ė
        {"macron", {{{1, 7.5}, {3, 7.5}}}},                    // Ū
        {"ogonek", {{{4, 0}, {3.6, -0.8}, {4.5, -1.1}}}},      // Ą Ę Į Ų
    };
    return table;
}

inline const std::map<char32_t, std::pair<char32_t, std::string>>& LETTERS() {
    static const std::map<char32_t, std::pair<char32_t, std::string>> table = {
        {0x104, {U'A', "ogonek"}}, {0x10C, {U'C', "caron"}}, {0x118, {U'E', "ogonek"}},     // Ą Č Ę
        {0x116, {U'E', "dot"}}, {0x12E, {U'I', "ogonek"}}, {0x160, {U'S', "caron"}},        // Ė Į Š
        {0x172, {U'U', "ogonek"}}, {0x16A, {U'U', "macron"}}, {0x17D, {U'Z', "caron"}},     // Ų Ū Ž
        {0xC4, {U'A', "dot"}}, {0xD6, {U'O', "dot"}}, {0xDC, {U'U', "dot"}},                // Ä Ö Ü
        {0x100, {U'A', "macron"}}, {0x112, {U'E', "macron"}}, {0x12A, {U'I', "macron"}},    // Ā Ē Ī
        {0x14C, {U'O', "macron"}}, {0x147, {U'N', "caron"}}, {0x158, {U'R', "caron"}},      // Ō Ň Ř
        {0x11A, {U'E', "caron"}}, {0x10E, {U'D', "caron"}}, {0x164, {U'T', "caron"}},       // Ě Ď Ť
    };
    return table;
}

inline char32_t font_upper(char32_t ch) {
    if (ch >= U'a' && ch <= U'z') return ch - (U'a' - U'A');
    switch (ch) {
        case 0x131: return U'I';                               // ı (dotless i) -> I
        case 0x17F: return U'S';                               // ſ (long s) -> S
        case 0xE4: case 0xF6: case 0xFC:                       // ä ö ü
            return ch - 0x20;
        case 0x101: case 0x105: case 0x10D: case 0x10F: case 0x113: case 0x117:   // ā ą č ď ē ė
        case 0x119: case 0x11B: case 0x12B: case 0x12F: case 0x148: case 0x14D:   // ę ě ī į ň ō
        case 0x159: case 0x161: case 0x165: case 0x16B: case 0x173: case 0x17E:   // ř š ť ū ų ž
            return ch - 1;
        default: return ch;
    }
}

inline std::vector<char32_t> text_code_points(const std::string& s) {
    std::vector<char32_t> out;
    size_t i = 0, n = s.size();
    while (i < n) {
        size_t j = i + 1;                                      // a lead byte and the bytes that continue it
        while (j < n && ((unsigned char)s[j] & 0xC0) == 0x80) ++j;
        unsigned char c = (unsigned char)s[i];
        size_t len = c < 0x80 ? 1 : (c & 0xE0) == 0xC0 ? 2 : (c & 0xF0) == 0xE0 ? 3 : (c & 0xF8) == 0xF0 ? 4 : 0;
        char32_t cp = len == 1 ? c : len == 2 ? (c & 0x1F) : len == 3 ? (c & 0x0F) : (c & 0x07);
        bool ok = len == j - i;
        for (size_t q = i + 1; ok && q < j; ++q) cp = (cp << 6) | ((unsigned char)s[q] & 0x3F);
        const char32_t least[5] = {0, 0, 0x80, 0x800, 0x10000};
        if (ok && (cp < least[len] || cp > 0x10FFFF || (cp >= 0xD800 && cp <= 0xDFFF))) ok = false;
        out.push_back(ok ? cp : 0xFFFD);
        i = j;
    }
    return out;
}

inline Glyph strokes(char32_t ch_) {
    char32_t ch = font_upper(ch_);
    auto found = FONT().find(ch);
    if (found != FONT().end()) return found->second;
    auto letter = LETTERS().find(ch);
    if (letter != LETTERS().end()) {
        const Glyph& base = FONT().at(letter->second.first);
        const std::string& accent = letter->second.second;
        std::vector<Profile> extra = ACCENTS().at(accent);
        if (accent == "ogonek" && base.width < 4) {            // hook under a narrow letter
            for (Profile& line : extra)
                for (Point2& p : line) p = {p[0] - (4 - base.width), p[1]};
        }
        Glyph out = base;
        out.strokes.insert(out.strokes.end(), extra.begin(), extra.end());
        return out;
    }
    return Glyph{4, {{{0, 0}, {4, 0}, {4, 6}, {0, 6}, {0, 0}}}};   // unknown: a box
}

}  // namespace detail

inline double text_width(const std::string& string, double size, double spacing) {
    double unit = size / 6.0;
    double total = 0.0;
    for (char32_t ch : detail::text_code_points(string)) {
        double w = detail::strokes(ch).width;
        total += (w + 1.5 * spacing) * unit;
    }
    return std::max(0.0, total - 1.5 * spacing * unit);
}

inline double text(const std::string& string, const Point& at_, double size, std::optional<double> thickness,
                   const Color& color_, const Point& u_, const Point& v_, const std::string& align, double spacing,
                   int k) {
    const Point at = at_;                                      // (copies: the scene grows below)
    const Color color = color_;
    double unit = size / 6.0;
    double r = thickness ? *thickness : 0.45 * unit;
    Point u = detail::unit(u_), v = detail::unit(v_);
    std::vector<std::string> lines;                            // string.split("\n")
    for (size_t start = 0;;) {
        size_t nl = string.find('\n', start);
        if (nl == std::string::npos) {
            lines.push_back(string.substr(start));
            break;
        }
        lines.push_back(string.substr(start, nl - start));
        start = nl + 1;
    }
    double widest = 0.0;
    for (size_t row = 0; row < lines.size(); ++row) {
        const std::string& line = lines[row];
        double width = text_width(line, size, spacing);
        widest = std::max(widest, width);
        double start;
        if (align == "center")
            start = -width / 2.0;
        else if (align == "right")
            start = -width;
        else
            start = 0.0;
        double y_off = -(long long)row * 1.6 * size;           // (-row: a whole number, as in add.py)
        double x = start;
        for (char32_t ch : detail::text_code_points(line)) {
            detail::Glyph g = detail::strokes(ch);
            for (const Profile& line_pts : g.strokes) {
                Points pts;
                for (const Point2& gp : line_pts) {
                    double px = x + gp[0] * unit, py = y_off + gp[1] * unit;
                    pts.push_back({at[0] + u[0] * px + v[0] * py,
                                   at[1] + u[1] * px + v[1] * py,
                                   at[2] + u[2] * px + v[2] * py});
                }
                for (size_t i = 0; i + 1 < pts.size(); ++i)
                    if (distance(pts[i], pts[i + 1]) > EPS) cylinder(pts[i], pts[i + 1], r, k, color);
                for (const Point& p : pts) sphere(p, r, 2, color);
            }
            x += (g.width + 1.5 * spacing) * unit;
        }
    }
    return widest;
}

inline double write(const std::string& string, const Point& at, double size, std::optional<double> thickness,
                    const Color& color, const Point& u, const Point& v, const std::string& align, double spacing,
                    int k) {
    return text(string, at, size, thickness, color, u, v, align, spacing, k);
}

inline double label(const std::string& string, const Point& at, double size, std::optional<double> thickness,
                    const Color& color, const Point& u, const Point& v, const std::string& align, double spacing,
                    int k) {
    return text(string, at, size, thickness, color, u, v, align, spacing, k);
}

inline void glyph(const std::string& letter, const Point& origin, const Point& u, const Point& v, double size,
                  double thickness, const Color& color) {
    text(letter, origin, size, thickness, color, u, v);
}

}  // namespace add

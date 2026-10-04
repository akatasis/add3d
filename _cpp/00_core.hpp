// ============================================================================
//  add.hpp -- build 3D models with nothing but C++ code.
// ============================================================================
//
//  Version 2.0  |  Martynas Sabaliauskas (akatasis@gmail.com)  |  MIT licence
//
//  The C++ twin of add.py: the same tiny, dependency-free 3D modelling
//  kernel for teaching, as one header file.  Only the C++17 standard
//  library is used: no mesh library, no modelling program.  Every
//  triangle you see was computed by code you can read.
//
//  Quick start
//  -----------
//
//      #include "add.hpp"
//
//      int main() {
//          add::box({0, 0, 0}, 1, {255, 0, 0});           // a red cube
//          add::sphere({2, 0, 0}, 0.6, 20, {0, 128, 255});
//          add::save("model.off");                        // or "model.obj"
//      }
//
//      g++ -std=c++17 -O2 model.cpp -o model && ./model
//
//  The same functions, the same numbers
//  ------------------------------------
//  Every function of add.py is here under the same name, with the same
//  parameters in the same order and the same defaults, and it computes the
//  same thing in the same order: a C++ program and a Python program that
//  make the same calls write byte for byte the same .off and .obj files
//  (the tests check this for every function).  Where Python has a keyword
//  argument, C++ takes the arguments in order; where Python accepts
//  ``None`` for "the current scene", C++ has an overload without the mesh;
//  a function passed as an argument is any C++ lambda.
//
//  Three layers of API
//  -------------------
//  1. Draw   -- box, sphere, tube, parametric ... add shapes to the scene.
//  2. Shape  -- layer() takes the scene out as a Mesh you can move, rotate,
//               mirror, twist or combine with booleans; mesh(M) puts it back.
//  3. Finish -- clean() repairs the model, check() reports on it, save()
//               writes .off or .obj (+ .mtl).
//
//  Coordinate convention: right-handed, Y up.  A face is outward when its
//  corners run counter-clockwise as seen from outside the model.
// ============================================================================

#ifndef ADD_HPP
#define ADD_HPP

// Floating point exactly as written: a*b+c is a product, rounded, then a sum, rounded -- never
// one fused multiply-add (which rounds once) -- so that the numbers are the same as Python's on
// every machine.  (Compile your own model with -ffp-contract=off too: see the README.)
#if defined(__clang__)
#pragma STDC FP_CONTRACT OFF
#elif defined(__GNUC__)
#pragma GCC optimize("fp-contract=off")
#endif

#include <algorithm>
#include <array>
#include <cctype>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <functional>
#include <initializer_list>
#include <iostream>
#include <limits>
#include <map>
#include <memory>
#include <numeric>
#include <optional>
#include <random>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
#if __has_include(<charconv>)
#include <charconv>
#endif

namespace add {

inline const std::string version = "2.0";

//: Numerical tolerance used by welding, boolean operations and plane tests.
inline constexpr double EPS = 1e-9;

// Everything a model needs from <cmath>, so that add::sin, add::pi, add::sqrt
// work like add.sin, add.pi, add.sqrt in Python (std::sin works too, of course).
inline constexpr double pi = 3.141592653589793;
inline constexpr double tau = 6.283185307179586;
inline constexpr double e = 2.718281828459045;
inline constexpr double inf = std::numeric_limits<double>::infinity();
using std::sin; using std::cos; using std::tan; using std::asin; using std::acos; using std::atan;
using std::atan2; using std::sinh; using std::cosh; using std::tanh; using std::exp; using std::log;
using std::log10; using std::log2; using std::pow; using std::sqrt; using std::fabs; using std::floor;
using std::ceil; using std::fmod; using std::hypot; using std::abs; using std::trunc;
inline double radians(double deg) { return deg * pi / 180.0; }
inline double degrees(double rad) { return rad * 180.0 / pi; }


// ============================================================================
//  1. Points, colours
// ============================================================================

//: A point (or a vector) in 3D: ``{x, y, z}``; ``p[0]``, ``p[1]``, ``p[2]``
//: or ``p.x``, ``p.y``, ``p.z``.  A missing coordinate is 0: ``{1, 2}``.
struct Point {
    double x = 0.0, y = 0.0, z = 0.0;
    double& operator[](int i) { return i == 0 ? x : (i == 1 ? y : z); }
    double operator[](int i) const { return i == 0 ? x : (i == 1 ? y : z); }
    bool operator==(const Point& o) const { return x == o.x && y == o.y && z == o.z; }
    bool operator!=(const Point& o) const { return !(*this == o); }
    bool operator<(const Point& o) const {
        return x != o.x ? x < o.x : (y != o.y ? y < o.y : z < o.z);
    }
};

//: A point in 2D -- a corner of a profile (a cross-section): ``{x, y}``.
struct Point2 {
    double x = 0.0, y = 0.0;
    double& operator[](int i) { return i == 0 ? x : y; }
    double operator[](int i) const { return i == 0 ? x : y; }
    bool operator==(const Point2& o) const { return x == o.x && y == o.y; }
    bool operator!=(const Point2& o) const { return !(*this == o); }
    bool operator<(const Point2& o) const { return x != o.x ? x < o.x : y < o.y; }
};

using Points = std::vector<Point>;          // a path, a ring of points
using Profile = std::vector<Point2>;        // a 2D outline
using Face = std::vector<int>;             // the corners of a face: indices into Mesh::V

inline Point operator+(const Point& a, const Point& b) { return {a.x + b.x, a.y + b.y, a.z + b.z}; }
inline Point operator-(const Point& a, const Point& b) { return {a.x - b.x, a.y - b.y, a.z - b.z}; }
inline Point operator-(const Point& a) { return {-a.x, -a.y, -a.z}; }
inline Point operator*(const Point& a, double s) { return {a.x * s, a.y * s, a.z * s}; }
inline Point operator*(double s, const Point& a) { return {a.x * s, a.y * s, a.z * s}; }
inline Point operator/(const Point& a, double s) { return {a.x / s, a.y / s, a.z / s}; }
inline Point& operator+=(Point& a, const Point& b) { a.x += b.x; a.y += b.y; a.z += b.z; return a; }
inline Point& operator-=(Point& a, const Point& b) { a.x -= b.x; a.y -= b.y; a.z -= b.z; return a; }
inline Point& operator*=(Point& a, double s) { a.x *= s; a.y *= s; a.z *= s; return a; }
inline Point2 operator+(const Point2& a, const Point2& b) { return {a.x + b.x, a.y + b.y}; }
inline Point2 operator-(const Point2& a, const Point2& b) { return {a.x - b.x, a.y - b.y}; }
inline Point2 operator*(const Point2& a, double s) { return {a.x * s, a.y * s}; }
inline Point2 operator*(double s, const Point2& a) { return {a.x * s, a.y * s}; }

inline std::ostream& operator<<(std::ostream& o, const Point& p);     // [1.0, 2.0, 3.0], as Python prints
inline std::ostream& operator<<(std::ostream& o, const Point2& p);    // a point (defined below)

//: The scalar (dot) product, the vector (cross) product and the length.
inline double dot(const Point& a, const Point& b) { return a.x * b.x + a.y * b.y + a.z * b.z; }
inline Point cross(const Point& a, const Point& b) {
    return {a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x};
}
inline double length(const Point& a) { return std::sqrt(a.x * a.x + a.y * a.y + a.z * a.z); }

namespace detail {

// Points are plain 3-number structs.  These helpers are written out in full
// (in the same order of operations as add.py's), so that every line reads
// without prior knowledge and the numbers come out exactly the same.
inline Point sub(const Point& a, const Point& b) { return {a.x - b.x, a.y - b.y, a.z - b.z}; }
inline Point add3(const Point& a, const Point& b) { return {a.x + b.x, a.y + b.y, a.z + b.z}; }
inline Point scale(const Point& a, double s) { return {a.x * s, a.y * s, a.z * s}; }
inline double norm(const Point& a) { return std::sqrt(a.x * a.x + a.y * a.y + a.z * a.z); }

//: Vector of length 1 pointing the same way as ``a`` (0 vector stays 0).
inline Point unit(const Point& a) {
    double n = norm(a);
    if (n < EPS) return {0.0, 0.0, 0.0};
    return {a.x / n, a.y / n, a.z / n};
}

//: Some unit vector perpendicular to ``n``.
inline Point perp(const Point& n) {
    Point other = std::fabs(n.x) < 0.9 ? Point{1.0, 0.0, 0.0} : Point{0.0, 1.0, 0.0};
    return unit(cross(n, other));
}

//: Three unit vectors (u, v, w) with w along ``direction``.  ``u`` is the
//: first world axis (X, then Y, then Z) that is not parallel to ``w``, so a
//: profile drawn in (u, v) keeps its natural orientation: for a shape along
//: Z, u = X and v = Y; for one standing up along Y, u = X and v = -Z.
struct Frame { Point u, v, w; };
inline Frame frame(const Point& direction) {
    Point w = unit(direction);
    if (norm(w) < EPS) w = {0.0, 0.0, 1.0};
    Point u{0.0, 0.0, 0.0};
    const Point cands[3] = {{1.0, 0.0, 0.0}, {0.0, 1.0, 0.0}, {0.0, 0.0, 1.0}};
    for (const Point& cand : cands) {
        double d = dot(w, cand);
        if (std::fabs(d) < 0.9) {
            u = unit({cand.x - w.x * d, cand.y - w.y * d, cand.z - w.z * d});
            break;
        }
    }
    Point v = cross(w, u);
    return {u, v, w};
}

// -- numbers written the way Python writes them ------------------------------

//: Python's ``x ** y`` for floats: the C library's pow, called at run time (a compiler would
//: turn std::pow(x, 2) into x * x, which is not always the same number); a negative x with a
//: whole y is pow(-x, y), negated when y is odd, as CPython does it.
inline double py_pow(double x, double y) {
    volatile double exponent = y;
    double e_ = exponent;
    if (x == 0.0 && e_ < 0.0 && std::isfinite(e_))                 // (Python: ZeroDivisionError)
        throw std::domain_error("0.0 cannot be raised to a negative power");
    double r;
    if (x < 0.0 && e_ == std::floor(e_) && std::isfinite(e_)) {
        r = std::pow(-x, e_);
        if (std::fmod(std::fabs(e_), 2.0) == 1.0) r = -r;
    } else {
        r = std::pow(x, e_);
    }
    if (std::isinf(r) && std::isfinite(x) && std::isfinite(e_))     // (Python: OverflowError)
        throw std::overflow_error("(34, 'Numerical result out of range')");
    return r;
}

//: Python's ``round(x, n)``: correctly rounded to ``n`` decimals (ties to
//: even on the exact binary value) and read back.
inline double py_round(double x, int n) {
    if (!std::isfinite(x)) return x;
    char buf[400];
    std::snprintf(buf, sizeof buf, "%.*f", n, x);
    return std::strtod(buf, nullptr);
}

//: The digits and the decimal exponent of the shortest decimal that reads
//: back as ``x`` (``x = 0.d1d2d3... * 10^decpt``) -- Python's ``repr``.
inline void shortest_digits(double x, std::string& digits, int& decpt) {
    char buf[64];
#if defined(__cpp_lib_to_chars) && __cpp_lib_to_chars >= 201611L
    auto res = std::to_chars(buf, buf + sizeof buf, x, std::chars_format::scientific);
    *res.ptr = '\0';
#else
    for (int p = 1; p <= 17; ++p) {
        std::snprintf(buf, sizeof buf, "%.*e", p - 1, x);
        if (std::strtod(buf, nullptr) == x) break;
    }
#endif
    // buf: [-]d[.ddd]e[+-]XX
    const char* s = buf;
    if (*s == '-') ++s;
    digits.clear();
    while (*s && *s != 'e') {
        if (*s != '.') digits += *s;
        ++s;
    }
    int ex = std::atoi(s + 1);
    while (digits.size() > 1 && digits.back() == '0') digits.pop_back();
    decpt = ex + 1;
}

//: Python's ``repr(x)`` of a float: the shortest string that reads back as
//: ``x``, in plain notation from 1e-4 to 1e16 and with an exponent outside.
inline std::string py_repr(double x) {
    if (std::isnan(x)) return "nan";
    if (std::isinf(x)) return x > 0 ? "inf" : "-inf";
    if (x == 0.0) return std::signbit(x) ? "-0.0" : "0.0";
    std::string digits;
    int decpt;
    shortest_digits(x, digits, decpt);
    std::string out = std::signbit(x) ? "-" : "";
    int n = (int)digits.size();
    if (decpt <= -4 || decpt > 16) {                          // d.ddde+XX
        out += digits[0];
        if (n > 1) out += "." + digits.substr(1);
        int ex = decpt - 1;
        char eb[16];
        std::snprintf(eb, sizeof eb, "e%c%02d", ex < 0 ? '-' : '+', ex < 0 ? -ex : ex);
        out += eb;
    } else if (decpt <= 0) {                                  // 0.000ddd
        out += "0." + std::string(-decpt, '0') + digits;
    } else if (decpt >= n) {                                  // ddd000.0
        out += digits + std::string(decpt - n, '0') + ".0";
    } else {                                                  // ddd.ddd
        out += digits.substr(0, decpt) + "." + digits.substr(decpt);
    }
    return out;
}

//: A float the short way, so .off/.obj files stay small (add.py's ``_num``).
inline std::string num(double x) {
    if (std::isnan(x)) throw std::invalid_argument("cannot convert float NaN to integer");
    if (std::isinf(x)) throw std::overflow_error("cannot convert float infinity to integer");
    if (x == std::trunc(x) && std::fabs(x) < 1e15)
        return std::to_string((long long)x);
    return py_repr(py_round(x, 9));
}

//: How many characters a UTF-8 string has (Python's ``len`` of a str).
inline size_t utf8_len(const std::string& s) {
    size_t n = 0;
    for (unsigned char ch : s)
        if ((ch & 0xC0) != 0x80) ++n;
    return n;
}

inline std::string lower(std::string s) {
    for (char& ch : s) ch = (char)std::tolower((unsigned char)ch);
    return s;
}

inline std::string strip(const std::string& s) {
    size_t a = 0, b = s.size();
    while (a < b && std::isspace((unsigned char)s[a])) ++a;
    while (b > a && std::isspace((unsigned char)s[b - 1])) --b;
    return s.substr(a, b - a);
}

//: ``printf`` into a std::string.
template <class... A>
inline std::string fmt(const char* f, A... args) {
    int n = std::snprintf(nullptr, 0, f, args...);
    std::string s(n > 0 ? n : 0, '\0');
    if (n > 0) std::snprintf(&s[0], n + 1, f, args...);
    return s;
}

}  // namespace detail

// Points print as Python prints them: std::cout << p  ->  [1.0, 2.0, 3.0]
inline std::ostream& operator<<(std::ostream& o, const Point& p) {
    return o << "[" << detail::py_repr(p.x) << ", " << detail::py_repr(p.y) << ", " << detail::py_repr(p.z) << "]";
}
inline std::ostream& operator<<(std::ostream& o, const Point2& p) {
    return o << "[" << detail::py_repr(p.x) << ", " << detail::py_repr(p.y) << "]";
}


//: A colour: red, green, blue (0..255), an opacity (1 = solid) and, for a
//: textured face, an image file.  Anything colour-like converts to it:
//:     {255, 0, 0}      three whole numbers 0..255
//:     {1.0, 0.5, 0.0}  three fractions 0..1 (scaled up to 0..255)
//:     {120, 190, 255, 0.4}   a see-through colour (the 4th number: opacity)
//:     "red", "#ff0000", "#f00", "#78beff66"
//: A function called without a colour uses the default grey (160, 160, 160).
struct Color {
    int r = 160, g = 160, b = 160;
    double alpha = 1.0;
    std::string image;

    Color() {}
    Color(int r_, int g_, int b_) { set_ints(r_, g_, b_); }
    Color(int r_, int g_, int b_, double a) { set_ints(r_, g_, b_); set_alpha(a); }
    Color(double r_, double g_, double b_) { set_doubles(r_, g_, b_); }
    Color(double r_, double g_, double b_, double a) { set_doubles(r_, g_, b_); set_alpha(a); }
    Color(const char* s) { parse(s); }
    Color(const std::string& s) { parse(s); }

    //: Is this face see-through (an opacity under 1)?
    bool clear() const { return alpha < 1.0; }
    bool operator==(const Color& o) const {
        return r == o.r && g == o.g && b == o.b && alpha == o.alpha && image == o.image;
    }
    bool operator!=(const Color& o) const { return !(*this == o); }
    bool operator<(const Color& o) const {
        return std::tie(r, g, b, alpha, image) < std::tie(o.r, o.g, o.b, o.alpha, o.image);
    }

  private:
    static int clamp255(double c) {
        if (std::isnan(c)) throw std::invalid_argument("cannot convert float NaN to integer");
        if (std::isinf(c)) throw std::overflow_error("cannot convert float infinity to integer");
        c = c < -1.0 ? -1.0 : (c > 256.0 ? 256.0 : c);        // (a huge number is simply too much)
        int v = (int)std::nearbyint(c);                        // round half to even, as Python's round()
        return v < 0 ? 0 : (v > 255 ? 255 : v);
    }
    void set_ints(int r_, int g_, int b_) { r = clamp255(r_); g = clamp255(g_); b = clamp255(b_); }
    void set_doubles(double r_, double g_, double b_) {
        if (std::max(r_, std::max(g_, b_)) <= 1.0) { r_ *= 255.0; g_ *= 255.0; b_ *= 255.0; }
        r = clamp255(r_); g = clamp255(g_); b = clamp255(b_);
    }
    void set_alpha(double a) {
        if (std::isnan(a)) a = 1.0;                            // (add.py: a NaN opacity makes it solid)
        if (a > 1.0) a /= 255.0;                               // given as 0..255
        a = a < 0 ? 0.0 : (a > 1.0 ? 1.0 : a);
        alpha = detail::py_round(a, 3);
    }
    void parse(const std::string& text);
};

struct ColorHash {
    size_t operator()(const Color& c) const {
        size_t h = (size_t)c.r * 73856093u ^ (size_t)c.g * 19349663u ^ (size_t)c.b * 83492791u;
        return h ^ std::hash<double>()(c.alpha) ^ std::hash<std::string>()(c.image);
    }
};

//: The default colour of a function called without one.
inline const Color DEFAULT_COLOR = Color(160, 160, 160);

//: A handful of named colours, so ``add::box(c, 1, "red")`` works.
inline const std::map<std::string, std::array<int, 3>>& COLORS() {
    static const std::map<std::string, std::array<int, 3>> table = {
        {"black", {0, 0, 0}}, {"white", {255, 255, 255}}, {"grey", {128, 128, 128}},
        {"gray", {128, 128, 128}}, {"red", {255, 0, 0}}, {"green", {0, 255, 0}},
        {"blue", {0, 0, 255}}, {"yellow", {255, 255, 0}}, {"cyan", {0, 255, 255}},
        {"magenta", {255, 0, 255}}, {"orange", {255, 140, 0}}, {"purple", {128, 0, 200}},
        {"pink", {255, 130, 180}}, {"brown", {139, 69, 19}}, {"gold", {212, 175, 55}},
        {"silver", {192, 192, 192}}, {"navy", {0, 0, 128}}, {"teal", {0, 128, 128}},
        {"lime", {140, 255, 60}}, {"sky", {120, 190, 255}},
    };
    return table;
}

inline void Color::parse(const std::string& text) {
    std::string s = detail::lower(detail::strip(text));
    auto it = COLORS().find(s);
    if (it != COLORS().end()) {
        r = it->second[0]; g = it->second[1]; b = it->second[2];
        return;
    }
    while (!s.empty() && s[0] == '#') s = s.substr(1);
    if (s.size() == 3 || s.size() == 4) {
        std::string t;
        for (char ch : s) { t += ch; t += ch; }
        s = t;
    }
    auto hex = [&](size_t i) -> int {
        char* end = nullptr;
        std::string part = s.substr(i, 2);
        long v = std::strtol(part.c_str(), &end, 16);
        if (*end != '\0' || part.size() != 2) throw std::invalid_argument("unknown colour: '" + text + "'");
        return (int)v;
    };
    if (s.size() == 6 || s.size() == 8) {
        r = hex(0); g = hex(2); b = hex(4);
        if (s.size() == 8 && hex(6) < 255) alpha = detail::py_round(hex(6) / 255.0, 3);
        return;
    }
    throw std::invalid_argument("unknown colour: '" + text + "'");
}

//: Normalise anything colour-like into a Color (add.py's ``rgb``).
inline Color rgb(const Color& c) { return c; }

// A colour prints as Python prints add.rgb(...): (255, 0, 0), (120, 190, 255, 0.4),
// (255, 255, 255, 1.0, 'wood.png').
inline std::ostream& operator<<(std::ostream& o, const Color& c) {
    o << "(" << c.r << ", " << c.g << ", " << c.b;
    if (c.alpha < 1.0 || !c.image.empty()) o << ", " << detail::py_repr(c.alpha);
    if (!c.image.empty()) o << ", '" << c.image << "'";
    return o << ")";
}

//: A see-through version of a colour: ``alpha`` is the opacity, 0 for
//: invisible and 1 for solid.  The opacity is written to the .mtl file of an
//: .obj model (as ``d``); .off files carry it as a fourth colour number.
inline Color transparent(const Color& color, double alpha = 0.5) {
    Color c = color;
    double a = std::isnan(alpha) ? 1.0 : alpha;
    if (a > 1.0) a /= 255.0;
    a = a < 0 ? 0.0 : (a > 1.0 ? 1.0 : a);
    c.alpha = detail::py_round(a, 3);
    return c;
}

//: Colour from hue/saturation/value, all in 0..1.  Hue wraps around.
inline Color hsv(double h, double s = 1.0, double v = 1.0) {
    h = h - std::floor(h);                                     // Python's h % 1.0
    h *= 6.0;
    int i = (int)h;
    double f = h - i;
    double p = v * (1 - s), q = v * (1 - s * f), t = v * (1 - s * (1 - f));
    double table[6][3] = {{v, t, p}, {q, v, p}, {p, v, t}, {p, q, v}, {t, p, v}, {v, p, q}};
    double* c = table[((i % 6) + 6) % 6];
    return Color((int)(c[0] * 255), (int)(c[1] * 255), (int)(c[2] * 255));
}

//: Blend between colours ``a`` and ``b``; ``t`` runs 0 -> 1.
inline Color gradient(double t, const Color& a, const Color& b) {
    t = t < 0 ? 0.0 : (t > 1 ? 1.0 : t);
    return Color((int)(a.r + (b.r - a.r) * t), (int)(a.g + (b.g - a.g) * t), (int)(a.b + (b.b - a.b) * t));
}


// ============================================================================
//  2. Random numbers -- the same ones as Python's ``random`` module
// ============================================================================
// A Mersenne Twister seeded exactly as Python seeds its own, so that
// add::seed(7) followed by the same calls gives the same numbers -- and the
// same model -- as add.seed(7) in Python.

class Random {
  public:
    Random() { seed_entropy(); }
    explicit Random(long long s) { seed(s); }

    //: Start the sequence again from ``s`` (Python's ``random.seed(s)``).
    void seed(long long s) {
        unsigned long long n = s < 0 ? (unsigned long long)(-(s + 1)) + 1ull : (unsigned long long)s;
        std::vector<uint32_t> key;
        while (n) { key.push_back((uint32_t)(n & 0xffffffffull)); n >>= 32; }
        if (key.empty()) key.push_back(0);
        init_by_array(key);
        has_gauss_next = false;
    }
    void seed_entropy() {
        std::random_device rd;
        std::vector<uint32_t> key;
        for (int i = 0; i < 4; ++i) key.push_back(rd());
        init_by_array(key);
        has_gauss_next = false;
    }
    //: A 32-bit random whole number.
    uint32_t next32() {
        if (mti >= N) twist();
        uint32_t y = mt[mti++];
        y ^= (y >> 11);
        y ^= (y << 7) & 0x9d2c5680u;
        y ^= (y << 15) & 0xefc60000u;
        y ^= (y >> 18);
        return y;
    }
    //: A float in [0, 1) -- Python's ``random.random()``.
    double random() {
        uint32_t a = next32() >> 5, b = next32() >> 6;
        return (a * 67108864.0 + b) * (1.0 / 9007199254740992.0);
    }
    //: ``k`` random bits -- Python's ``random.getrandbits(k)`` (k <= 64).
    unsigned long long getrandbits(int k) {
        if (k <= 32) return next32() >> (32 - k);
        unsigned long long lo = next32();
        unsigned long long hi = next32() >> (64 - k);
        return lo | (hi << 32);
    }
    //: A whole number in 0 .. n-1 (Python's ``_randbelow``).
    long long randbelow(long long n) {
        if (n <= 0) return 0;
        int k = 0;
        for (unsigned long long v = (unsigned long long)n; v; v >>= 1) ++k;
        unsigned long long r = getrandbits(k);
        while (r >= (unsigned long long)n) r = getrandbits(k);
        return (long long)r;
    }
    //: A whole number from ``a`` to ``b``, both included.
    long long randint(long long a, long long b) { return a + randbelow(b - a + 1); }
    //: ``start``, ``start + step`` ... below ``stop``.
    long long randrange(long long start, long long stop, long long step = 1) {
        long long n = step > 0 ? (stop - start + step - 1) / step : (start - stop - step - 1) / (-step);
        if (n <= 0) throw std::invalid_argument("empty range for randrange()");
        return start + step * randbelow(n);
    }
    //: A float from ``a`` to ``b``.
    double uniform(double a, double b) { return a + (b - a) * random(); }
    //: One element of a list, chosen at random.
    template <class T>
    const T& choice(const std::vector<T>& seq) { return seq.at((size_t)randbelow((long long)seq.size())); }
    //: Shuffle a list in place (Python's ``random.shuffle``).
    template <class T>
    void shuffle(std::vector<T>& x) {
        for (long long i = (long long)x.size() - 1; i > 0; --i) {
            long long j = randbelow(i + 1);
            std::swap(x[(size_t)i], x[(size_t)j]);
        }
    }
    //: A number from the normal distribution (Python's ``normalvariate``).
    double normalvariate(double mu = 0.0, double sigma = 1.0) {
        const double NV_MAGICCONST = 4 * std::exp(-0.5) / std::sqrt(2.0);
        double z;
        while (true) {
            double u1 = random();
            double u2 = 1.0 - random();
            z = NV_MAGICCONST * (u1 - 0.5) / u2;
            double zz = z * z / 4.0;
            if (zz <= -std::log(u2)) break;
        }
        return mu + z * sigma;
    }
    //: A number from the normal (Gaussian) distribution -- Python's ``random.gauss``: two numbers
    //: are made at a time, and the second is kept for the next call.
    double gauss(double mu = 0.0, double sigma = 1.0) {
        double z;
        if (has_gauss_next) {
            z = gauss_next;
            has_gauss_next = false;
        } else {
            double x2pi = random() * (2.0 * 3.141592653589793);
            double g2rad = std::sqrt(-2.0 * std::log(1.0 - random()));
            z = std::cos(x2pi) * g2rad;
            gauss_next = std::sin(x2pi) * g2rad;
            has_gauss_next = true;
        }
        return mu + z * sigma;
    }

  private:
    static const int N = 624, M = 397;
    uint32_t mt[N];
    int mti = N + 1;
    double gauss_next = 0.0;
    bool has_gauss_next = false;
    void init_genrand(uint32_t s) {
        mt[0] = s;
        for (mti = 1; mti < N; ++mti)
            mt[mti] = (1812433253u * (mt[mti - 1] ^ (mt[mti - 1] >> 30)) + (uint32_t)mti);
    }
    void init_by_array(const std::vector<uint32_t>& key) {
        init_genrand(19650218u);
        int i = 1, j = 0;
        int k = N > (int)key.size() ? N : (int)key.size();
        for (; k; --k) {
            mt[i] = (mt[i] ^ ((mt[i - 1] ^ (mt[i - 1] >> 30)) * 1664525u)) + key[j] + (uint32_t)j;
            ++i; ++j;
            if (i >= N) { mt[0] = mt[N - 1]; i = 1; }
            if (j >= (int)key.size()) j = 0;
        }
        for (k = N - 1; k; --k) {
            mt[i] = (mt[i] ^ ((mt[i - 1] ^ (mt[i - 1] >> 30)) * 1566083941u)) - (uint32_t)i;
            ++i;
            if (i >= N) { mt[0] = mt[N - 1]; i = 1; }
        }
        mt[0] = 0x80000000u;
        mti = N;
    }
    void twist() {
        static const uint32_t mag01[2] = {0x0u, 0x9908b0dfu};
        int kk;
        uint32_t y;
        for (kk = 0; kk < N - M; ++kk) {
            y = (mt[kk] & 0x80000000u) | (mt[kk + 1] & 0x7fffffffu);
            mt[kk] = mt[kk + M] ^ (y >> 1) ^ mag01[y & 0x1u];
        }
        for (; kk < N - 1; ++kk) {
            y = (mt[kk] & 0x80000000u) | (mt[kk + 1] & 0x7fffffffu);
            mt[kk] = mt[kk + (M - N)] ^ (y >> 1) ^ mag01[y & 0x1u];
        }
        y = (mt[N - 1] & 0x80000000u) | (mt[0] & 0x7fffffffu);
        mt[N - 1] = mt[M - 1] ^ (y >> 1) ^ mag01[y & 0x1u];
        mti = 0;
    }
};

namespace detail {
inline Random& rng() { static Random r; return r; }
}  // namespace detail

//: The module's own random numbers, like Python's module-level functions:
//: add::seed(7); add::randint(1, 6); add::uniform(0, 1); add::random().
inline void seed(long long s) { detail::rng().seed(s); }
inline double random() { return detail::rng().random(); }
inline double uniform(double a, double b) { return detail::rng().uniform(a, b); }
inline double gauss(double mu = 0.0, double sigma = 1.0) { return detail::rng().gauss(mu, sigma); }
inline long long randint(long long a, long long b) { return detail::rng().randint(a, b); }
inline long long randrange(long long start, long long stop, long long step = 1) {
    return detail::rng().randrange(start, stop, step);
}
template <class T>
inline const T& choice(const std::vector<T>& seq) { return detail::rng().choice(seq); }
template <class T>
inline void shuffle(std::vector<T>& x) { detail::rng().shuffle(x); }

//: A random colour.  Pass ``seed`` for a repeatable one.
inline Color random_color(std::optional<long long> seed = std::nullopt) {
    Random local = seed ? Random(*seed) : Random(0);
    Random& r = seed ? local : detail::rng();
    int a = (int)r.randint(0, 255), b = (int)r.randint(0, 255), c = (int)r.randint(0, 255);
    return Color(a, b, c);
}


// ============================================================================
//  3. Mesh -- the one data structure in this library
// ============================================================================

//: A list of vertices and a list of coloured faces.  ``M.V`` are the
//: points, ``M.F`` the faces (each a list of corner indices -- any number of
//: corners) and ``M.C`` the colour of each face; ``M.F.size()`` is the
//: polygon count.  ``M.UV`` (only for textured models) holds the texture
//: coordinates of each face -- an empty list for a face without them.
struct Mesh {
    std::vector<Point> V;
    std::vector<Face> F;
    std::vector<Color> C;
    std::vector<std::vector<Point2>> UV;       // empty, or one entry per face
    bool has_uv = false;                       // (add.py's ``UV is not None``)

    Mesh() {}
    Mesh(std::vector<Point> v, std::vector<Face> f, std::vector<Color> c)
        : V(std::move(v)), F(std::move(f)), C(std::move(c)) {}

    //: Number of faces.
    size_t polygons() const { return F.size(); }
    bool empty() const { return F.empty() && V.empty(); }

    //: An independent copy.
    Mesh copy() const { return *this; }

    //: Append a point and return its index.
    int add_vertex(const Point& p) {
        V.push_back(p);
        return (int)V.size() - 1;
    }

    //: Append one face given as a list of vertex indices.
    void add_face(const Face& indices, const Color& color = DEFAULT_COLOR) {
        F.push_back(indices);
        C.push_back(color);
        if (has_uv) UV.emplace_back();
    }

    //: Append one textured face: its corners and their texture coordinates.
    void add_face(const Face& indices, const Color& color, const std::vector<Point2>& uv) {
        if (!has_uv) {
            has_uv = true;
            UV.assign(F.size(), {});
        }
        F.push_back(indices);
        C.push_back(color);
        UV.push_back(uv);
    }

    //: Append one face given as a list of 3D points.
    void add_polygon(const Points& points, const Color& color = DEFAULT_COLOR) {
        int base = (int)V.size();
        for (const Point& p : points) add_vertex(p);
        Face f;
        for (int i = base; i < (int)V.size(); ++i) f.push_back(i);
        add_face(f, color);
    }

    //: Append another mesh to this one (in place).
    Mesh& extend(const Mesh& other) {
        int shift = (int)V.size();
        V.insert(V.end(), other.V.begin(), other.V.end());
        if (other.has_uv && !has_uv) {
            has_uv = true;
            UV.assign(F.size(), {});
        }
        for (size_t k = 0; k < other.F.size(); ++k) {
            Face f = other.F[k];
            for (int& i : f) i += shift;
            F.push_back(std::move(f));
            C.push_back(other.C[k]);
        }
        if (has_uv) {
            if (!other.has_uv) UV.resize(F.size());
            else UV.insert(UV.end(), other.UV.begin(), other.UV.end());
        }
        return *this;
    }

    //: The texture coordinates of face ``i`` (empty when it has none).
    std::vector<Point2> uv_of(size_t i) const { return has_uv ? UV[i] : std::vector<Point2>(); }

    //: The corner points of face ``i``.
    Points face_points(size_t i) const {
        Points out;
        for (int k : F[i]) out.push_back(V[k]);
        return out;
    }
};

inline std::ostream& operator<<(std::ostream& o, const Mesh& M) {
    return o << "<Mesh " << M.V.size() << " vertices, " << M.F.size() << " faces>";
}


// ============================================================================
//  4. The current scene (the "default layer")
// ============================================================================

namespace detail {
inline Mesh& current() { static Mesh s; return s; }
inline std::vector<Mesh>& stack() { static std::vector<Mesh> s; return s; }
}  // namespace detail

//: The Mesh everything is currently being drawn into.
inline Mesh& scene() { return detail::current(); }

//: Throw away everything drawn so far.
inline void clear() { detail::current() = Mesh(); }

//: Take the scene out as a mesh and start a fresh, empty scene.  The
//: workhorse of the library: draw something, layer() it, transform the
//: result, then mesh() it back (possibly many times):
//:
//:     add::box({0, 0, 0}, 1, "red");
//:     add::Mesh brick = add::layer();
//:     for (int i = 0; i < 10; ++i) add::mesh(add::move(brick, {double(i), 0, 0}));
inline Mesh layer() {
    Mesh M = std::move(detail::current());
    detail::current() = Mesh();
    return M;
}

//: Put the scene aside and start a fresh, empty one -- inside a function
//: that builds a part, so that the part cannot scoop up what was drawn
//: before it.  pop() gives the part back and restores the old scene.
inline void push() {
    detail::stack().push_back(std::move(detail::current()));
    detail::current() = Mesh();
}

//: Return what was drawn since push() and restore the old scene.
inline Mesh pop() {
    Mesh made = std::move(detail::current());
    if (!detail::stack().empty()) {
        detail::current() = std::move(detail::stack().back());
        detail::stack().pop_back();
    } else {
        detail::current() = Mesh();
    }
    return made;
}

//: Run a drawing function and return what it drew as a mesh, without
//: touching the current scene -- push(), draw(), pop() in one:
//:
//:     add::Mesh ball = add::make([] { add::sphere({0, 0, 0}, 1); });
template <class Draw>
inline Mesh make(Draw&& draw) {
    push();
    try {
        draw();
    } catch (...) {
        pop();
        throw;
    }
    return pop();
}

//: Draw mesh ``M`` into the current scene (and give it back).
inline const Mesh& mesh(const Mesh& M) {
    detail::current().extend(M);
    return M;
}

//: ``add::paste`` is a friendlier name for mesh().
inline const Mesh& paste(const Mesh& M) { return mesh(M); }

//: Combine several meshes into one (no geometry is changed).  For a
//: watertight combination that removes the parts hidden inside, use union_.
inline Mesh merge(const std::vector<Mesh>& meshes) {
    Mesh out;
    for (const Mesh& M : meshes) out.extend(M);
    return out;
}

//: An independent copy of ``M`` (or of the scene).
inline Mesh copy(const Mesh& M) { return M; }
inline Mesh copy() { return detail::current(); }


// ============================================================================
//  5. Arguments that may be a number or a function, a colour or a function
// ============================================================================

//: A number -- or a function of the fraction ``t`` along something that
//: gives the number there.  Where add.py lets a parameter be either
//: (``r=0.1`` or ``r=lambda t: 0.1 + 0.05 * t``), C++ takes one of these:
//: add::Scalar r = 0.1;  add::Scalar r = [](double t) { return 0.1 + 0.05 * t; };
struct Scalar {
    std::function<double(double)> fn;
    double value = 0.0;
    bool given = false;

    Scalar() {}
    Scalar(std::nullptr_t) {}
    Scalar(double v) : value(v), given(true) {}
    Scalar(int v) : value(v), given(true) {}
    template <class F, class = decltype(std::declval<F>()(0.0)),
              class = std::enable_if_t<!std::is_arithmetic<std::decay_t<F>>::value>>
    Scalar(F f) : fn(f), given(true) {}

    //: Was a value given at all (Python: ``is not None``)?
    explicit operator bool() const { return given; }
    //: Is it a function (Python: ``callable(x)``)?
    bool callable() const { return (bool)fn; }
    //: The value at ``t`` (the number itself when it is not a function).
    double operator()(double t) const { return fn ? fn(t) : value; }
};

//: A colour -- or a function that gives the colour of each piece.  Where
//: add.py takes ``color=lambda t, a: ...``, C++ takes a lambda with the same
//: arguments (the drawing function says which), returning anything colour-like:
//: add::ColorOf<double, double> c = [](double t, double a) { return t < 0.5 ? "red" : "white"; };
template <class... Args>
struct ColorOf {
    std::function<Color(Args...)> fn;
    Color color;

    ColorOf() {}
    ColorOf(const Color& c) : color(c) {}
    ColorOf(const char* s) : color(s) {}
    ColorOf(const std::string& s) : color(s) {}
    ColorOf(int r, int g, int b) : color(r, g, b) {}
    ColorOf(int r, int g, int b, double a) : color(r, g, b, a) {}
    ColorOf(double r, double g, double b) : color(r, g, b) {}
    ColorOf(double r, double g, double b, double a) : color(r, g, b, a) {}
    template <class F, class = std::enable_if_t<std::is_invocable<F, Args...>::value>>
    ColorOf(F f) : fn([f](Args... a) { return Color(f(a...)); }) {}

    //: Is it a function (Python: ``callable(color)``)?
    bool callable() const { return (bool)fn; }
    Color operator()(Args... a) const { return fn ? fn(a...) : color; }
};

}  // namespace add

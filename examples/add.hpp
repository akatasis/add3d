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

// ============================================================================
//  4. Building blocks: faces, boxes, prisms, the Platonic solids
//     (add.py: _src/10_build.py)
// ============================================================================
namespace add {

namespace detail {
//: The colour of cell (i, j) of a patch: one colour, or a function of (i, j).
using CellPaint = ColorOf<int, int>;
//: Turn a 2D array of points P[i][j] into a quad patch (add.py's _add_grid).
inline void add_grid(Mesh& M, const std::vector<Points>& P, const CellPaint& color, bool wrap_u = false,
                     bool wrap_v = false, bool flip = false);
//: ``k`` points on a circle of radius ``r`` around ``center`` in the plane of u and v.
inline Points ring(const Point& center, const Point& u, const Point& v, double r, int k, double phase = 0.0);
//: Close a ring of points with a triangle fan meeting at ``apex``.
inline void fan(Mesh& M, const Points& points, const Point& apex, const ColorOf<int>& color, bool flip = false,
                bool closed = true);
//: Six times the signed volume of faces first_face..end (positive: outward).
inline double signed_volume(const Mesh& M, size_t first_face = 0);
//: Flip faces first_face..end if they came out inside-out.
inline void make_outward(Mesh& M, size_t first_face);
//: Surface of a solid described on a grid of cells (see frame, voxels, pixels, heightmap).
inline Mesh grid_solid(const Point& origin, const std::vector<double>& sx, const std::vector<double>& sy,
                       const std::vector<double>& sz, const std::function<bool(int, int, int)>& filled,
                       const ColorOf<int, int, int>& color);
//: Add a freshly built primitive to the scene, welding its seams first.
inline void emit(Mesh& M, double tol = 1e-9);
//: Vertex and face tables of the five Platonic solids (centred at 0).
inline std::pair<Points, std::vector<Face>> platonic(const std::string& name);
//: Faces of a convex point set with ``sides`` corners each.
inline std::vector<Face> hull_faces(const Points& V, int sides);
}  // namespace detail

//: One flat face through the given 3D points (any number of corners).
inline void polygon(const Points& points, const Color& color = DEFAULT_COLOR);
//: A single triangle.
inline void triangle(const Point& a, const Point& b, const Point& c, const Color& color = DEFAULT_COLOR);
//: A single quadrilateral.
inline void quad(const Point& a, const Point& b, const Point& c, const Point& d, const Color& color = DEFAULT_COLOR);
//: A filled circle of radius ``r`` at ``center``, facing ``normal`` (a direction or a second point).
inline void disc(const Point& center, const Point& normal, double r, int k = 32, const Color& color = DEFAULT_COLOR);
//: A flat annulus (a disc with a hole).
inline void ring(const Point& center, const Point& normal, double r_outer, double r_inner, int k = 32,
                 const Color& color = DEFAULT_COLOR);
//: A flat (or, with ``height(x, z)``, a hilly) rectangular patch in XZ; ``size`` = {width_x, depth_z};
//: ``color`` may be a function of (x, z); ``thickness`` makes it a solid slab.
inline void grid(const Point& center, const Point2& size, int nx = 10, int nz = 10,
                 const ColorOf<double, double>& color = DEFAULT_COLOR,
                 const std::function<double(double, double)>& height = nullptr, double thickness = 0.0);
//: A cube of side ``edge`` centred at ``center``.
inline void box(const Point& center, double edge, const Color& color = DEFAULT_COLOR);
//: A rectangular block; ``sizes`` are the edge lengths along X, Y and Z.
inline void cuboid(const Point& center, const Point& sizes, const Color& color = DEFAULT_COLOR);
//: The twelve edges of a cube -- a hollow cube frame.
inline void frame(const Point& center, double edge, double thickness, const Color& color = DEFAULT_COLOR);
//: A cell (i, j, k) of a voxel model.
struct Cell {
    int i = 0, j = 0, k = 0;
    bool operator<(const Cell& o) const { return std::tie(i, j, k) < std::tie(o.i, o.j, o.k); }
    bool operator==(const Cell& o) const { return i == o.i && j == o.j && k == o.k; }
};
//: The surface of a set of unit cells -- a Minecraft-style model.
//: ``color`` may be a function of the cell (i, j, k) -- counted from the lowest cell, as in add.py.
inline void voxels(const std::vector<Cell>& cells, double size = 1.0, const Point& origin = {0, 0, 0},
                   const ColorOf<int, int, int>& color = DEFAULT_COLOR);
//: A square pyramid: base of side ``edge``, apex ``height`` above it.
inline void pyramid(const Point& center, double edge, double height, const Color& color = DEFAULT_COLOR);
//: A solid with a constant cross-section: a 2D ``profile`` given a depth along ``axis``.
inline void prism(const Profile& profile, double height, const Color& color = DEFAULT_COLOR,
                  const Point& center = {0, 0, 0}, const Point& axis = {0, 1, 0});
//: One of the five Platonic solids ("tetrahedron", "cube", "octahedron", "dodecahedron",
//: "icosahedron"), inscribed in a sphere of radius ``r``.
inline void polyhedron(const std::string& name, const Point& center = {0, 0, 0}, double r = 1.0,
                       const Color& color = DEFAULT_COLOR);
inline void tetrahedron(const Point& center = {0, 0, 0}, double r = 1.0, const Color& color = DEFAULT_COLOR);
inline void octahedron(const Point& center = {0, 0, 0}, double r = 1.0, const Color& color = DEFAULT_COLOR);
inline void dodecahedron(const Point& center = {0, 0, 0}, double r = 1.0, const Color& color = DEFAULT_COLOR);
inline void icosahedron(const Point& center = {0, 0, 0}, double r = 1.0, const Color& color = DEFAULT_COLOR);
//: The vertex coordinates of a Platonic solid.
inline Points polyhedron_points(const std::string& name, const Point& center = {0, 0, 0}, double r = 1.0);
//: The face table of a Platonic solid.
inline std::vector<Face> polyhedron_faces(const std::string& name);

}  // namespace add

// ============================================================================
//  5. Helpers and 2D profiles: numbers, points, outlines, points along curves
//     (add.py: _src/15_profiles.py)
// ============================================================================
namespace add {

//: Blend from ``a`` (t = 0) to ``b`` (t = 1) -- numbers or points.
inline double lerp(double a, double b, double t);
inline Point lerp(const Point& a, const Point& b, double t);
inline Point2 lerp(const Point2& a, const Point2& b, double t);
//: Blend two colours (as add.py blends two colour lists; the result is read as a colour).
inline Color lerp(const Color& a, const Color& b, double t);
//: ``x`` limited to the range lo .. hi.
inline double clamp(double x, double lo = 0.0, double hi = 1.0);
//: Map ``x`` from the range a0..a1 onto the range b0..b1.
inline double remap(double x, double a0, double a1, double b0, double b1);
//: Distance between two points (2D or 3D).
inline double distance(const Point& a, const Point& b);
inline double distance(const Point2& a, const Point2& b);
//: The point half way between ``a`` and ``b``.
inline Point midpoint(const Point& a, const Point& b);
inline Point2 midpoint(const Point2& a, const Point2& b);
//: The unit vector pointing from ``a`` to ``b`` (the difference itself when they coincide).
inline Point direction(const Point& a, const Point& b);
//: Turn a single point around an axis through ``P`` (Rodrigues).
inline Point rotate_point(const Point& p, const Point& axis, double angle, const Point& P = {0, 0, 0});
//: A darker (factor < 1) or lighter (factor > 1) version of a colour.
inline Color shade(const Color& color, double factor);
//: Round the corners of a polyline by cutting them (Chaikin's algorithm).
inline Points chaikin(const Points& points, int rounds = 2, bool closed = false);
inline Profile chaikin(const Profile& points, int rounds = 2, bool closed = false);
//: ``k`` points on a circle of radius ``r``.
inline Profile profile_circle(double r, int k = 32, double phase = 0.0);
//: ``k`` points on an ellipse with half-axes ``a`` and ``b``.
inline Profile profile_ellipse(double a, double b, int k = 32);
//: A regular n-gon with circumradius ``r`` (a flat side at the bottom unless ``phase`` is given).
inline Profile profile_polygon(int n, double r, std::optional<double> phase = std::nullopt);
//: A star with ``n`` points, alternating between the two radii.
inline Profile profile_star(int n, double r_outer, double r_inner, std::optional<double> phase = std::nullopt);
//: A w by h rectangle, with corners rounded by ``r`` if given.
inline Profile profile_rect(double w, double h, double r = 0.0, int k = 4);
//: The outline of a gear: ``teeth`` teeth of height ``depth`` on radius ``r``.
inline Profile profile_gear(int teeth, double r, std::optional<double> depth = std::nullopt, int k = 2);
//: ``n`` points evenly spaced from ``a`` to ``b`` (both included).
inline Points points_on_line(const Point& a, const Point& b, int n);
//: ``n`` points spread evenly on a circle in the plane normal to ``axis``.
inline Points points_on_circle(const Point& center, double r, int n, const Point& axis = {0, 1, 0},
                               double phase = 0.0);
//: ``n`` points along a helix of ``turns`` turns climbing ``pitch`` per turn.
inline Points points_on_helix(const Point& center, double r, double pitch, double turns, int n,
                              const Point& axis = {0, 1, 0});
//: ``n`` points along a flat spiral whose radius grows from r0 to r1.
inline Points points_on_spiral(const Point& center, double r0, double r1, double turns, int n,
                               const Point& axis = {0, 1, 0}, double rise = 0.0);
//: ``n`` points path(t) for t evenly spread over t0 .. t1.
inline Points points_on_curve(const std::function<Point(double)>& path, double t0, double t1, int n,
                              bool closed = false);

}  // namespace add

// ============================================================================
//  6. Round shapes: spheres, cylinders, cones, tori, revolve, helix
//     (add.py: _src/20_round.py)
// ============================================================================
namespace add {

namespace detail {
//: Points of a surface of revolution (the P[i][j] grid add_grid expects) and whether it
//: closes all the way round (add.py returns the pair (P, closed)).
inline std::pair<std::vector<Points>, bool> revolve_grid(const Point& A, const Point& direction,
                                                         const Profile& profile, int k, double angle = 2.0 * pi,
                                                         double phase = 0.0);
//: Unit geodesic sphere: vertices and triangles.
inline std::pair<Points, std::vector<Face>> icosphere_grid(int subdivisions);
//: The engine behind cylinder / cone / frustum and their variants: the finished (welded) mesh.
inline Mesh tube_body(const Point& A, const Point& B, double r1, double r2, int k, const Color& color, bool cap_a,
                      bool cap_b);
}  // namespace detail

//: A 2D profile spun round the axis A -> B (a lathe): ``profile(t)`` gives [radius, height] (the
//: height measured along the axis from A) for t from t0 to t1, sampled steps + 1 times.
//: ``color`` may be a function (t, angle) of the middle of each cell.  A list of [radius, height]
//: points (add.hpp only; add.py needs a function) is spun as it is: point i is the sample at
//: t = t0 + (t1 - t0) * i / (n - 1), and ``steps`` is not used.
inline void revolve(const Profile& profile, const Point& A = {0, 0, 0}, const Point& B = {0, 1, 0}, double t0 = 0.0,
                    double t1 = 1.0, int steps = 40, int k = 32, const ColorOf<double, double>& color = DEFAULT_COLOR,
                    double angle = 2.0 * pi, bool caps = true);
inline void revolve(const std::function<Point2(double)>& profile, const Point& A = {0, 0, 0},
                    const Point& B = {0, 1, 0}, double t0 = 0.0, double t1 = 1.0, int steps = 40, int k = 32,
                    const ColorOf<double, double>& color = DEFAULT_COLOR, double angle = 2.0 * pi, bool caps = true);
//: add.py 1.2 lathe: spin the curve S(t) = [radius, height] around A -> B.
inline void spin3D(const Point& A, const Point& B, const std::function<Point2(double)>& S, double min_t, double max_t,
                   int grid_t, int k, const Color& RGB);
//: A geodesic sphere: an icosahedron whose triangles are split ``subdivisions`` times (0..7).
//: ``color`` may be a function of the face's direction from the centre (a unit vector).
inline void icosphere(const Point& center, double r, int subdivisions = 3,
                      const ColorOf<Point>& color = DEFAULT_COLOR);
//: A sphere built from triangles (``k`` sets the fineness; or give ``subdivisions``); ``color``
//: may be a function of the direction, as in icosphere.
inline void sphere(const Point& center, double r, int k = 10, const ColorOf<Point>& color = DEFAULT_COLOR,
                   std::optional<int> subdivisions = std::nullopt);
//: A sphere built from six curved square patches (all faces are quads).
inline void quadsphere(const Point& center, double r, int k = 10, const Color& color = DEFAULT_COLOR);
//: Like quadsphere but with a separate radius for X, Y and Z.
inline void ellipsoid(const Point& center, const Point& radii, int k = 10, const Color& color = DEFAULT_COLOR);
//: A globe-style sphere: nu meridians by nv parallels.
inline void uvsphere(const Point& center, double r, int nu = 32, int nv = 16, const Color& color = DEFAULT_COLOR);
//: A doughnut: tube radius r swept round a circle of radius R.
inline void torus(const Point& center, double R, double r, int nu = 48, int nv = 24,
                  const Color& color = DEFAULT_COLOR, const Point& axis = {0, 1, 0});
//: A closed cylinder from A to B, radius r, k sides.
inline void cylinder(const Point& A, const Point& B, double r, int k = 24, const Color& color = DEFAULT_COLOR);
//: A cylinder with no lids -- just the side wall (old cylinder2).
inline void tube(const Point& A, const Point& B, double r, int k = 24, const Color& color = DEFAULT_COLOR);
//: A cylinder closed at A only (old cylinder3).
inline void cup(const Point& A, const Point& B, double r, int k = 24, const Color& color = DEFAULT_COLOR);
//: A closed cone: circular base of radius r at A, tip at B.
inline void cone(const Point& A, const Point& B, double r, int k = 24, const Color& color = DEFAULT_COLOR);
//: Only the slanted wall of a cone (old cone2).
inline void cone_open(const Point& A, const Point& B, double r, int k = 24, const Color& color = DEFAULT_COLOR);
//: A cone with its tip cut off: radius r1 at A, r2 at B.
inline void frustum(const Point& A, const Point& B, double r1, double r2, int k = 24,
                    const Color& color = DEFAULT_COLOR, bool caps = true);
//: A hollow tube -- a cylinder with a cylindrical hole down the middle.
inline void pipe(const Point& A, const Point& B, double r_outer, double r_inner, int k = 24,
                 const Color& color = DEFAULT_COLOR);
//: A cylinder with a hemisphere on each end (a "pill").
inline void capsule(const Point& A, const Point& B, double r, int k = 24, const Color& color = DEFAULT_COLOR);
//: A shaft from A to B with a cone head -- good for vectors.
inline void arrow(const Point& A, const Point& B, double r = 0.05, const Color& color = DEFAULT_COLOR, int k = 16,
                  double head = 0.25);
//: A spring / helical tube of ``turns`` turns around ``axis``.
inline void helix(const Point& center, double r, double pitch, double turns, int k = 200, double thickness = 0.1,
                  int sides = 12, const Color& color = DEFAULT_COLOR, const Point& axis = {0, 1, 0});
//: The coordinate axes: X red, Y green, Z blue, each labelled.
inline void axes(const Point& C = {0, 0, 0}, double length = 4.0, double width = 0.03);

}  // namespace add

// ============================================================================
//  7. More solids: beams, rounded boxes, arches, stairs, gears, trees, tubes
//     (add.py: _src/25_more_solids.py)
// ============================================================================
namespace add {

namespace detail {
//: Map a mesh built in local x, y, z into the world: x along w, y along up, z along side.
inline Mesh local_mesh(const Mesh& M, const Point& origin, const Point& w, const Point& up, const Point& side);
//: Unit vectors (w, up, side) for something standing on the ground running along ``direction``.
inline std::array<Point, 3> ground_frame(const Point& direction, const Point& up = {0, 1, 0});
//: A prism with a hole: outer and inner 2D rings with the same number of points (used by gear).
inline Mesh hollow_prism(const Profile& outer, const Profile& inner, double height, const Color& color,
                         const Point& center = {0, 0, 0}, const Point& axis = {0, 1, 0});
//: The engine behind curve and polyline: a round tube through points with a radius per point.
//: ``color``: the colour of cell (i, j); ``cap_a`` / ``cap_b``: of the end caps' triangles (by j).
inline Mesh tube_along(const Points& points, const std::vector<double>& radii, int k, const CellPaint& color,
                       bool closed, const ColorOf<int>* cap_a = nullptr, const ColorOf<int>* cap_b = nullptr);
//: arch() once its cross-section is known (a circle, or a rectangle).
inline void arch_loft(const Point& A, const Point& B, double height, const Profile& profile, const Color& color,
                      int steps, const Point& up);
//: The characters of a row of pixels(), one string each: a row is UTF-8 and a character is
//: one cell, as in Python's str (a byte that does not start a character joins the one before).
inline std::vector<std::string> pixel_cells(const std::string& row);
//: The order in which CPython's ``set`` gives back the whole numbers added to it in this
//: order (Objects/setobject.c: the hash of an int is the int, -1 -> -2; a table of 8 slots,
//: rebuilt 4 times as big as its use when 3/5 full; a slot is looked for at hash & mask and the
//: 9 slots after it, then at (i * 5 + 1 + perturb) & mask with perturb >>= 5).
inline std::vector<long long> py_set_iteration_order(const std::vector<long long>& added);
}  // namespace detail

//: A rectangular bar from A to B: ``width`` sideways by ``height`` along ``up`` (the width when not given).
inline void beam(const Point& A, const Point& B, double width, std::optional<double> height = std::nullopt,
                 const Color& color = DEFAULT_COLOR, const Point& up = {0, 1, 0});
//: beam(A, B, width, color): a square bar (add.py: ``beam(A, B, 0.3, "brown")``).
inline void beam(const Point& A, const Point& B, double width, const Color& color, const Point& up = {0, 1, 0});
//: A box with all edges and corners rounded off by radius r (``sizes``: the full edge lengths).
inline void rounded_box(const Point& center, const Point& sizes, double r, int k = 8,
                        const Color& color = DEFAULT_COLOR);
//: rounded_box with one number for the size: a cube.
inline void rounded_box(const Point& center, double size, double r, int k = 8, const Color& color = DEFAULT_COLOR);
//: Half a ball with its flat side down; ``axis``: the way the round side points.  ``color`` may be
//: a function (t, a), as in revolve.
inline void hemisphere(const Point& center, double r, int k = 16, const ColorOf<double, double>& color = DEFAULT_COLOR,
                       const Point& axis = {0, 1, 0});
//: A curved arch standing on the ground at A and B, ``height`` above the line A -> B; ``thickness``
//: is the radius of a round bar ...
inline void arch(const Point& A, const Point& B, double height, double thickness, const Color& color = DEFAULT_COLOR,
                 int steps = 32, int k = 12, const Point& up = {0, 1, 0});
//: ... or {width, depth} of a rectangular one (``k`` is then not used).
inline void arch(const Point& A, const Point& B, double height, const Point2& thickness,
                 const Color& color = DEFAULT_COLOR, int steps = 32, int k = 12, const Point& up = {0, 1, 0});
//: A solid flight of n steps starting at ``origin`` (the foot).
inline void stairs(const Point& origin, int n, double width, double rise, double run,
                   const Color& color = DEFAULT_COLOR, const Point& direction = {1, 0, 0});
//: A cog wheel with ``teeth`` teeth.
inline void gear(const Point& center, int teeth, double r, double thickness, const Color& color = DEFAULT_COLOR,
                 std::optional<double> depth = std::nullopt, double hole = 0.0, const Point& axis = {0, 1, 0});
//: A wheel whose axle points along ``axis``.
inline void wheel(const Point& center, double r, double width, const Color& color = "black",
                  const Point& axis = {0, 0, 1}, int k = 32, int spokes = 0, const Color& hub_color = "silver");
//: A gabled roof over a size = {width_x, depth_z} floor.
inline void roof(const Point& center, const Point2& size, double height, const Color& color = DEFAULT_COLOR,
                 double overhang = 0.0);
//: A classical column standing on ``base`` (the bottom centre).
inline void column(const Point& base, double height, double r, const Color& color = DEFAULT_COLOR, int k = 24,
                   bool plinth = true);
//: A wall of staggered bricks starting at ``origin``; ``color`` may be a function (i, j) of the
//: brick's column and row; with ``seed`` each brick gets a small random variation of the colour.
inline void bricks(const Point& origin, double length, double height, const Point& brick = {1.0, 0.5, 0.5},
                   const ColorOf<int, int>& color = "brown", const Point& direction = {1, 0, 0}, double gap = 0.05,
                   std::optional<long long> seed = std::nullopt);
//: A simple tree standing on ``at`` (kind: "round", "pine" or "palm").
inline void tree(const Point& at, double height, const Color& trunk = "brown", const Color& leaves = "green",
                 const std::string& kind = "round", int k = 10, std::optional<long long> seed = std::nullopt);
//: The colours of pixels() by character (add.py's PALETTE: "r" red, "g" green, "#" black ...).
inline const std::map<std::string, Color>& PALETTE();
//: Pixel art in 3D: a list of strings becomes a block of coloured cubes (a space or a dot is empty;
//: the first string is the top row).  ``colors`` maps characters (UTF-8, one each) to colours; a
//: character that is not there gets ``color``.
inline void pixels(const std::vector<std::string>& rows, double size = 1.0, const Point& origin = {0, 0, 0},
                   const std::map<std::string, Color>& colors = PALETTE(), int depth = 1,
                   const Color& color = DEFAULT_COLOR);
//: Columns of cubes: heights[i][j] cells stacked at column (i, j).
inline void heightmap(const std::vector<std::vector<double>>& heights, double cell = 1.0,
                      const Point& origin = {0, 0, 0}, const ColorOf<int, int, int>& color = DEFAULT_COLOR);
//: A round tube through a list of points; r a number or a function of t; ``smooth``: chaikin rounds;
//: ``color`` may be a function (t, a).
inline void polyline(const Points& points, const Scalar& r = 0.1, int k = 12,
                     const ColorOf<double, double>& color = DEFAULT_COLOR, bool closed = false, int smooth = 0);
//: Every edge of a mesh as a thin bar, with a ball at every corner.
inline void wireframe(const Mesh& M, double r = 0.03, int k = 6, std::optional<Color> color = std::nullopt,
                      bool nodes = true);
//: Follow a vector field: the list of points a particle visits (Runge-Kutta).
inline Points flow(const std::function<Point(const Point&)>& field, const Point& p0, double dt = 0.01,
                   int steps = 1000);
//: The path of flow() drawn as a tube (``every`` keeps each n-th point); ``r`` and ``color`` as in polyline.
inline void trace(const std::function<Point(const Point&)>& field, const Point& p0, double dt = 0.01,
                  int steps = 1000, const Scalar& r = 0.1, int k = 12,
                  const ColorOf<double, double>& color = DEFAULT_COLOR, int every = 1);

}  // namespace add

// ============================================================================
//  8. Surfaces: parametric, sweep, extrude, loft, ribbon
//     (add.py: _src/30_surfaces.py)
// ============================================================================
namespace add {

//: A surface S(u, v) -> point.
using SurfaceFn = std::function<Point(double, double)>;
//: A path t -> point.
using PathFn = std::function<Point(double)>;

namespace detail {
//: Area-weighted average normal at every vertex.
inline Points vertex_normals(const Mesh& M);
//: Newell's normal of a face (not normalised) -- works for any polygon.
inline Point face_normal(const Mesh& M, const Face& f);
//: A border edge (a, b) -- one that belongs to just one face -- and its face's colour.
struct BorderEdge { int a, b; Color color; };
//: Every edge that belongs to just one face, in the order add.py lists them.
inline std::vector<BorderEdge> boundary_edges(const Mesh& M);
//: Rotation-minimising frames along a polyline: tangents and normals.
inline std::pair<Points, Points> rmf(const Points& points, bool closed = false);
//: Place a 2D profile at every point of a path -> grid of 3D points.  ``scale`` and
//: ``twist``: numbers (the twist grows along the path: twist * t) or functions of t.
inline std::vector<Points> sweep_profile(const Points& points, const Points& tangents, const Points& normals,
                                         const Profile& profile, const Scalar& scale = Scalar(),
                                         const Scalar& twist = Scalar());
}  // namespace detail

//: The heart of the library: draw the surface S(u, v) over a grid of cells.  ``color``
//: may be a function of (u, v) -- the middle of each cell.  (In add.py the colour is
//: the keyword ``color`` or the 8th argument ``RGB``; here it is the 8th argument.)
inline void parametric(const SurfaceFn& S, double min_u, double max_u, int grid_u, double min_v, double max_v,
                       int grid_v, const ColorOf<double, double>& color = DEFAULT_COLOR, bool wrap_u = false,
                       bool wrap_v = false, bool flip = false, double thickness = 0.0, bool double_sided = false);
//: A copy of ``M`` in which every face also exists reversed.
inline Mesh two_sided(const Mesh& M);
inline Mesh two_sided();
//: Give a thin surface a real thickness and return the closed solid.
inline Mesh solidify(const Mesh& M, double thickness = 0.1, bool both_ways = true);
inline Mesh solidify();
//: Slide a 2D cross-section along a 3D path.  ``color`` may be a function (t, j) of
//: the place along the path and the index of the profile's edge; ``scale`` and
//: ``twist`` numbers or functions of the fraction t along the path.
inline void sweep(const Profile& profile, const PathFn& path, double t0 = 0.0, double t1 = 1.0, int steps = 100,
                  const ColorOf<double, int>& color = DEFAULT_COLOR, bool closed = false,
                  const Scalar& scale = Scalar(), const Scalar& twist = Scalar(), bool caps = true);
//: A 3D parametric curve drawn as a round tube of radius ``r`` (a number or a function
//: of t); ``color`` may be a function (t, a) of the place along it and the angle round it.
inline void curve(const PathFn& P, double min_t, double max_t, int grid_t, int k = 16, const Scalar& r = 0.1,
                  const ColorOf<double, double>& color = DEFAULT_COLOR, bool isConnected = false);
//: Pull a 2D shape out into 3D, optionally turning and tapering as it goes.
inline void extrude(const Profile& profile, const Point& direction = {0, 1, 0},
                    const ColorOf<double, int>& color = DEFAULT_COLOR, int steps = 1, const Scalar& twist = 0.0,
                    const Scalar& scale = 1.0, const Point& center = {0, 0, 0}, bool caps = true);
//: Skin a surface over a list of cross-sections (each a ring of 3D points).
inline void loft(const std::vector<Points>& sections, const Color& color = DEFAULT_COLOR, bool closed = false,
                 bool caps = true, bool flip = false);
//: A flat band following a 3D path -- like a strip of paper.
inline void ribbon(const PathFn& path, double t0, double t1, int steps, double width,
                   const Color& color = DEFAULT_COLOR, bool closed = false, const Scalar& twist = Scalar(),
                   double thickness = 0.0);
//: add.py 1.2 disc: a filled circle centred at ``A``, facing ``B``.
inline void circle(const Point& A, const Point& B, double r, int k = 24, const Color& color = DEFAULT_COLOR);

}  // namespace add

// ============================================================================
//  9. A catalogue of named surfaces
//     (add.py: _src/35_catalog.py)
// ============================================================================
namespace add {

//: Named constants of a catalogued surface (``a``, ``b``, ``n`` ...), to change its shape.
using SurfaceParams = std::map<std::string, double>;
//: One surface of the catalogue (add.py's ``SURFACES[name]``): the formula ``f(u, v, constants)``,
//: the ranges ``u`` and ``v``, the ``wrap`` flags (does it close on itself along u / v?), a
//: default ``grid``, a one-line ``note``, whether it is drawn ``flip``ped, and its constants
//: ``params`` with their default values.
struct SurfaceEntry {
    std::function<Point(double, double, const SurfaceParams&)> f;
    Point2 u, v;
    std::array<bool, 2> wrap{{false, false}};
    std::array<int, 2> grid{{60, 60}};
    std::string note;
    bool flip = false;
    SurfaceParams params;
};
//: add.py's ``SURFACES`` dictionary: look a surface up by name (``at``, ``count``), or go
//: through all of them -- (name, entry) pairs -- in add.py's order, as a Python loop does.
class SurfaceTable {
  public:
    using value_type = std::pair<std::string, SurfaceEntry>;
    const SurfaceEntry& at(const std::string& name) const {
        auto it = index_.find(name);
        if (it == index_.end()) throw std::out_of_range("'" + name + "'");   // (add.py: KeyError)
        return items_[it->second].second;
    }
    size_t count(const std::string& name) const { return index_.count(name); }
    size_t size() const { return items_.size(); }
    std::vector<value_type>::const_iterator begin() const { return items_.begin(); }
    std::vector<value_type>::const_iterator end() const { return items_.end(); }
    //: ``table[name] = entry``: a new name goes at the end, a known one keeps its place.
    void set(const std::string& name, const SurfaceEntry& entry) {
        auto it = index_.find(name);
        if (it != index_.end()) {
            items_[it->second].second = entry;
            return;
        }
        index_[name] = items_.size();
        items_.push_back({name, entry});
    }

  private:
    std::vector<value_type> items_;
    std::map<std::string, size_t> index_;
};
//: The named surfaces (add.py's ``SURFACES``).
inline const SurfaceTable& SURFACES();
//: The names surface() understands, alphabetically.
inline std::vector<std::string> surface_names();
//: The f(u, v) -> point of a named surface, with its constants set from ``params`` (a constant
//: the surface does not have makes the function throw when it is called, as in add.py).
inline SurfaceFn surface_function(const std::string& name, const SurfaceParams& params = {});
//: Draw one of the catalogued surfaces by name, fitted to ``size`` around ``center``
//: (its natural size when ``size`` is not given); ``grid`` cells each way (or {along_u,
//: along_v}; the surface's own when not given).  ``color`` may be a function (u, v).
inline void surface(const std::string& name, const Point& center = {0, 0, 0},
                    std::optional<double> size = std::nullopt, std::optional<int> grid = std::nullopt,
                    const ColorOf<double, double>& color = DEFAULT_COLOR, double thickness = 0.0,
                    bool double_sided = false, const SurfaceParams& params = {});
inline void surface(const std::string& name, const Point& center, std::optional<double> size,
                    const std::array<int, 2>& grid, const ColorOf<double, double>& color = DEFAULT_COLOR,
                    double thickness = 0.0, bool double_sided = false, const SurfaceParams& params = {});

namespace detail {
//: Build the catalogue (add.py's _catalog).
inline SurfaceTable catalog();
//: SURFACES[name], or an exception for a name that is not there (add.py: KeyError).
inline const SurfaceEntry& surface_entry(const std::string& name);
//: surface() once the grid is known.
inline void draw_surface(const std::string& name, const Point& center, std::optional<double> size, int gu, int gv,
                         const ColorOf<double, double>& color, double thickness, bool double_sided,
                         const SurfaceParams& params);
}  // namespace detail

}  // namespace add

// ============================================================================
//  10. Measuring and transforming meshes; colouring them; arrays of copies
//      (add.py: _src/40_transform.py)
// ============================================================================
namespace add {

//: A texture mapping of your own: (point, unit face normal) -> (u, v).
using TextureFn = std::function<Point2(const Point&, const Point&)>;

namespace detail {
//: Apply a point function to a copy of the mesh (reversing the faces with ``flip``).
inline Mesh mapped(const Mesh& M, const std::function<Point(const Point&)>& f, bool flip = false);
//: Python's ``seq[i]``: the position of item ``i`` in a sequence of ``n`` (a negative ``i`` counts
//: from the end); std::out_of_range where Python raises IndexError.
inline size_t seq_index(long long i, size_t n);
//: Python's order of colour tuples: (r, g, b) < (r, g, b, alpha) < (r, g, b, alpha, image).
inline bool color_tuple_less(const Color& a, const Color& b);
//: The engine of texture(): a named ``mapping``, or ``custom`` when it is given.
inline Mesh texture_map(const Mesh& M, const std::string& image, const std::string& mapping,
                        const TextureFn* custom, double scale, const std::optional<Color>& color,
                        const Point2& offset);
}  // namespace detail

//: {{xmin, ymin, zmin}, {xmax, ymax, zmax}} of a mesh (of the scene without one).
inline std::array<Point, 2> bbox(const Mesh& M);
inline std::array<Point, 2> bbox();
//: The width, height and depth of a mesh.
inline Point size(const Mesh& M);
inline Point size();
//: The average of all vertices.
inline Point center(const Mesh& M);
inline Point center();
//: The centre of the bounding box.
inline Point middle(const Mesh& M);
inline Point middle();
//: Total surface area.
inline double area(const Mesh& M);
inline double area();
//: Enclosed volume (for a closed mesh).
inline double volume(const Mesh& M);
inline double volume();
//: Shift a mesh by vector V.
inline Mesh move(const Mesh& M, const Point& V);
//: Move a mesh so that its centre (of the bounding box, or the average vertex) sits at ``at``.
inline Mesh place(const Mesh& M, const Point& at, bool use_bbox = true);
//: Turn a mesh around the X / Y / Z axis through point P.
inline Mesh rotateX(const Mesh& M, double angle, const Point& P = {0, 0, 0});
inline Mesh rotateY(const Mesh& M, double angle, const Point& P = {0, 0, 0});
inline Mesh rotateZ(const Mesh& M, double angle, const Point& P = {0, 0, 0});
//: Turn a mesh by ``angle`` around any axis through P (Rodrigues).
inline Mesh rotate(const Mesh& M, const Point& axis, double angle, const Point& P = {0, 0, 0});
//: Scale a mesh by factor s (about its own centre unless ``about`` is given).
inline Mesh zoom(const Mesh& M, double s, std::optional<Point> about = std::nullopt);
//: Scale by a different factor along each axis, s = {sx, sy, sz}.
inline Mesh stretch(const Mesh& M, const Point& s, std::optional<Point> about = std::nullopt);
//: Scale a mesh so its largest dimension equals ``target``.
inline Mesh fit(const Mesh& M, double target = 1.0, std::optional<Point> about = std::nullopt);
//: Reflect a mesh in the plane through ``point`` with the given normal.
inline Mesh mirror(const Mesh& M, const Point& point = {0, 0, 0}, const Point& normal = {1, 0, 0});
//: Apply a 3x3 or 3x4 / 4x4 matrix (a list of rows).
inline Mesh transform(const Mesh& M, const std::vector<std::vector<double>>& matrix);
//: Bend a mesh with any function: f(p) -> new point.
inline Mesh deform(const Mesh& M, const std::function<Point(const Point&)>& f);
//: Rotate a mesh progressively along ``axis`` -- a corkscrew.
inline Mesh twist(const Mesh& M, double angle, const Point& axis = {0, 1, 0}, const Point& P = {0, 0, 0});
//: Shrink (or grow) a mesh along ``axis`` (0 = X, 1 = Y, 2 = Z).
inline Mesh taper(const Mesh& M, double factor, int axis = 1, const Point& P = {0, 0, 0});
//: Bend a mesh into an arc.
inline Mesh bend(const Mesh& M, double angle, int axis = 1, int around = 0, const Point& P = {0, 0, 0});
//: Nudge every vertex a little at random.
inline Mesh jitter(const Mesh& M, double amount = 0.05, std::optional<long long> seed = std::nullopt);
//: Paint the whole mesh one colour and return the painted copy.
inline Mesh color(const Mesh& M, const Color& RGB);
//: A copy with every face made see-through (``alpha``: the opacity).
inline Mesh opacity(const Mesh& M, double alpha);
//: Wrap an image round a mesh and return the textured copy.  ``mapping``: "box", "xy", "xz", "yz",
//: "fit", "sphere", "cylinder" -- or a TextureFn (point, normal) -> (u, v).  ``color`` tints the
//: picture (std::nullopt: each face keeps its own colour); any transparency is kept.
inline Mesh texture(const Mesh& M, const std::string& image, const std::string& mapping = "box", double scale = 1.0,
                    std::optional<Color> color = Color("white"), const Point2& offset = {0, 0});
inline Mesh texture(const Mesh& M, const std::string& image, const TextureFn& mapping, double scale = 1.0,
                    std::optional<Color> color = Color("white"), const Point2& offset = {0, 0});
//: Colour every face according to where it is (the centre of the face).
inline Mesh color_by(const Mesh& M, const std::function<Color(const Point&)>& fn);
//: Fade the mesh from colour a to colour b along one axis.
inline Mesh color_gradient(const Mesh& M, const Color& a, const Color& b, int axis = 1);
//: Give every face its own random colour.
inline Mesh color_random(const Mesh& M, std::optional<long long> seed = std::nullopt);
//: The distinct colours of a mesh, most used first, with how many faces use each.
inline std::vector<std::pair<Color, int>> palette(const Mesh& M);
inline std::vector<std::pair<Color, int>> palette();
//: Reduce a mesh to at most ``n`` distinct colours.
inline Mesh limit_colors(const Mesh& M, int n = 50);
//: Apply step(mesh, i) for i = 0 .. n-1 and merge the results.
inline Mesh repeat(const Mesh& M, int n, const std::function<Mesh(const Mesh&, int)>& step);
//: ``n`` copies in a row, each moved a further ``step`` along.
inline Mesh array_linear(const Mesh& M, const Point& step, int n);
//: A 2D or 3D block of copies.
inline Mesh array_grid(const Mesh& M, const Point& steps, const std::array<int, 3>& counts);
//: ``n`` copies arranged around an axis; ``rise`` makes it a spiral stair.
inline Mesh array_radial(const Mesh& M, int n, const Point& axis = {0, 1, 0}, const Point& P = {0, 0, 0},
                         double angle = 2.0 * pi, double rise = 0.0);
//: The mesh together with its mirror image.
inline Mesh array_mirror(const Mesh& M, const Point& point = {0, 0, 0}, const Point& normal = {1, 0, 0});

}  // namespace add

// ============================================================================
//  11. Placing things: aim, ground, align, scatter, along
//      (add.py: _src/45_place.py)
// ============================================================================
namespace add {

namespace detail {
//: The copies of along(): mesh M scaled, aimed and moved to every point.
inline Mesh along_copies(const Mesh& M, const Points& pts, const std::vector<double>& ts, const Points& dirs,
                         const std::optional<Point>& axis, const Scalar& scale);
}  // namespace detail

//: Turn a mesh so that its ``axis`` points along ``direction``.
inline Mesh aim(const Mesh& M, const Point& direction, const Point& axis = {0, 1, 0}, const Point& P = {0, 0, 0});
//: Move a mesh straight down (or up) so that its lowest point is at height y.
inline Mesh ground(const Mesh& M, double y = 0.0);
//: Move a mesh so that a chosen point of its bounding box (``anchor``: -1, 0 or 1 per axis) lands on ``at``.
inline Mesh align(const Mesh& M, const Point& at = {0, 0, 0}, const Point& anchor = {0, -1, 0});
//: ``n`` random points in the box lo .. hi (with ``height``: y = height(x, z)).
inline Points random_points(int n, const Point& lo, const Point& hi, std::optional<long long> seed = std::nullopt,
                            const std::function<double(double, double)>& height = nullptr);
//: Copies of a mesh at every point, each turned (``spin``) and sized (between scale[0] and scale[1]) at random.
inline Mesh scatter(const Mesh& M, const Points& points, std::optional<long long> seed = std::nullopt,
                    bool spin = true, const Point2& scale = {1.0, 1.0}, const Point& axis = {0, 1, 0});
//: ``n`` copies of a mesh strung along a curve -- a function path(t) for t in t0 .. t1, or a list of
//: points (then there is one copy per point, and n, t0 and t1 are not used) -- each turned so that its
//: ``axis`` follows the curve (std::nullopt: the copies stay upright); ``scale`` a number or a function of t.
inline Mesh along(const Mesh& M, const std::function<Point(double)>& path, int n, double t0 = 0.0, double t1 = 1.0,
                  std::optional<Point> axis = Point{0, 1, 0}, bool closed = false, const Scalar& scale = Scalar());
inline Mesh along(const Mesh& M, const Points& path, int n, double t0 = 0.0, double t1 = 1.0,
                  std::optional<Point> axis = Point{0, 1, 0}, bool closed = false, const Scalar& scale = Scalar());

}  // namespace add

// ============================================================================
//  13. Repair and report: clean(), stats(), check()
//      (add.py: _src/50_clean.py)
// ============================================================================
namespace add {

namespace detail {
//: Merge vertices closer than ``tol`` (in place).  Returns how many went.
inline int weld(Mesh& M, double tol = 1e-7);
//: For every vertex the index of the first one lying on it (within ``tol``, the way weld
//: would merge them), the mesh unchanged.
inline std::vector<int> weld_map(const std::vector<Point>& V, double tol = 1e-7);
//: Six times the signed volume of the faces ``faces`` measured from their own middle, and
//: the size of the piece, cubed (see fix_normals).
inline std::pair<double, double> piece_volume(const Mesh& M, const std::vector<int>& faces, const std::vector<int>& rep);
//: Keep only the faces whose index is in ``keep`` (in place); how many went.
inline int keep_faces(Mesh& M, const std::vector<int>& keep);
//: The vertices with a coordinate that is not a finite number.
inline std::set<int> not_finite(const Mesh& M);
//: Delete the vertices that are not finite numbers and their faces; how many faces went.
inline int drop_not_finite(Mesh& M);
//: Cut a face that visits a vertex twice into loops that do not.
inline std::vector<std::pair<Face, std::vector<Point2>>> split_repeats(const Face& f, const std::vector<Point2>* uv);
//: Delete faces with no area, remove repeated corners, split pinched faces (in place).
inline int drop_degenerate(Mesh& M, double tol = 1e-12);
//: Delete repeats of a face that is already there (in place).
inline int dedup_faces(Mesh& M);
//: Delete pairs of identical faces that point opposite ways (in place).
inline int drop_internal(Mesh& M);
//: True when the smallest index is followed by the smaller neighbour.
inline bool winding(const Face& f);
//: Delete vertices no face refers to (in place).
inline int drop_unused(Mesh& M);
//: Twice the signed area of a 2D polygon (positive when counter-clockwise).
inline double poly_area2(const Profile& pts);
//: Python's ``int(math.floor(x))`` -- a grid cell number.  As in Python, an exception
//: for a NaN or an infinite ``x``; unlike Python, whose integers have no limit, also
//: for a cell number beyond 64 bits (coordinates ~1e12 times the tolerance).
inline long long cell_floor(double x);
//: Python's ``round(x)`` (to a whole number, halves to even) as a float; an
//: exception for a NaN or an infinite ``x``, as in Python.
inline double key_round(double x);
//: Sutherland-Hodgman: the part of convex polygon ``pts`` on one side of the
//: directed line a -> b (left = the inside of a counter-clockwise polygon).
inline Profile clip_half(const Profile& pts, const Point2& a, const Point2& b, bool keep_left);
//: Convex polygon ``A`` with convex polygon ``B`` taken away, as convex pieces.
//: ``untouched`` (when given) is set to whether A came back as it was -- add.py
//: then returns the very list [A], which its callers test with ``is``.
inline std::vector<Profile> convex_minus(const Profile& A, const Profile& B, double eps,
                                         bool* untouched = nullptr);
//: Ear-clipping triangulation of a simple counter-clockwise 2D polygon (triangles as points).
inline std::vector<Profile> ears(const Profile& pts);
//: A counter-clockwise 2D polygon as convex pieces: itself if convex, ear triangles otherwise.
inline std::vector<Profile> convex_pieces(const Profile& pts);
//: Ear clipping as index triples, or nothing when no ear can be found (add.py: None).
inline std::optional<std::vector<std::array<int, 3>>> ear_triangles(const Profile& pts);
//: Does face ``f`` turn the wrong way anywhere along its outline?  (``n``: its normal, if known.)
inline bool is_concave(const Mesh& M, const Face& f, std::optional<Point> n = std::nullopt);
//: Cut every face that is not convex into triangles (in place); how many faces were cut.
inline int split_concave(Mesh& M);
//: One face of a plane group: add.py's ``(area, index, pts2d, bbox, flipped, plane)``.
struct PlanePoly {
    double area = 0.0;
    int index = 0;
    Profile pts;
    std::array<double, 4> bb{};
    bool flipped = false;
    Point pn{0.0, 0.0, 0.0};                     // the face's own plane: its normal ...
    double pd = 0.0;                             // ... and distance
};
//: Faces lying in one plane (either way round): the key, the plane's frame and the faces.
struct PlaneGroup {
    std::array<double, 4> key{};                 // (nx, ny, nz, d) rounded
    Point u, v, n;
    std::vector<PlanePoly> polys;
};
//: Faces grouped by their plane, in the order add.py's dict keeps them (groups of one left out).
inline std::vector<PlaneGroup> overlap_groups(const Mesh& M, double tol);
//: Do faces i and k lie in one plane, every corner of each within ``tol`` of the other's
//: plane?  (One group can hold faces centimetres apart far from the origin: add.py's _same_plane.)
inline bool same_plane(const Mesh& M, const PlanePoly& A, const PlanePoly& B, double tol);
//: Twice the area of the intersection of two convex counter-clockwise polygons.
inline double convex_overlap2(const Profile& A, const Profile& B);
//: ``pieces`` with every polygon of ``others`` taken away; nothing (add.py: None) when
//: the result would shatter into more than ``limit`` pieces.
inline std::optional<std::vector<Profile>> minus_all(std::vector<Profile> pieces, const std::vector<Profile>& others,
                                                     double eps, size_t limit = 64);
//: A face cut back by overlap_scan: add.py's ``(pieces, u, v, n, d, flipped)``.
struct CutFace {
    std::vector<Profile> pieces;
    Point u, v, n;
    double d = 0.0;
    bool flipped = false;
};
//: What overlap_scan found: how many faces overlap, and the faces to replace (face
//: index -> its pieces) in the order add.py's dict keeps them.
struct OverlapScan {
    int count = 0;
    std::vector<std::pair<int, CutFace>> replaced;
};
//: The engine behind overlaps() and cut_overlaps().
inline OverlapScan overlap_scan(const Mesh& M, double tol, bool cut);
//: Cut back faces that lie in one plane and overlap (in place); how many faces were cut.
inline int cut_overlaps(Mesh& M, double tol = 0.001);
//: Python's ``"%.Nf" % x`` (printf's, except that a NaN is "nan" whatever its sign).
inline std::string check_f(double x, int decimals);
//: Python's ``"%d" % x`` of a float: its whole part (an exception for a NaN or an infinity).
inline std::string check_d(double x);
}  // namespace detail

//: Close the tiny gaps left where an edge runs past another vertex.
inline Mesh heal(const Mesh& M, double tol = 1e-7);
inline Mesh heal();
//: How many faces are not convex.
inline int concave_faces(const Mesh& M);
inline int concave_faces();
//: How many faces lie in the same plane as a bigger face and overlap it.
inline int overlaps(const Mesh& M, double tol = 0.001);
inline int overlaps();
//: A copy in which every face is a triangle (fan triangulation).
inline Mesh triangulate(const Mesh& M);
inline Mesh triangulate();
//: Make every face of a copy point the same way (outward, if the model is closed).
inline Mesh fix_normals(const Mesh& M, bool outward = true);
inline Mesh fix_normals();

//: What clean() did (with report = true).
struct CleanReport {
    int vertices_removed = 0, faces_removed = 0, faces_cut = 0, faces_split = 0;
};
//: Repair a model and return the tidy copy (see add.py's clean).  ``report``, when
//: given, receives what was done.
inline Mesh clean(const Mesh& M, double tol = 1e-7, bool weld = true, bool degenerate = true,
                  bool duplicates = true, bool internal = true, bool unused = true, bool normals = false,
                  CleanReport* report = nullptr, bool overlaps = true, bool convex = true);
inline Mesh clean();

//: What stats() tells about a model.
struct Stats {
    int vertices = 0, faces = 0, triangles = 0, colors = 0;
    std::array<Point, 2> bbox{};
    Point size;
    double area = 0.0, volume = 0.0;
    int open_edges = 0, non_manifold_edges = 0, duplicate_vertices = 0, duplicate_faces = 0,
        back_to_back_faces = 0;
    bool closed = false;
    long long obj_bytes = 0;
    int transparent_faces = 0;
    std::vector<std::string> textures;
};
//: Counts, size, area, volume, health.
inline Stats stats(const Mesh& M);
inline Stats stats();

inline constexpr int SKETCHFAB_MB = 50;
inline constexpr int SKETCHFAB_COLORS = 50;
//: Print a health report and say whether the model meets the assignment.
inline bool check(const Mesh& M, int min_faces = 10000, int min_colors = 3, bool quiet = false,
                  double max_mb = SKETCHFAB_MB, int max_colors = SKETCHFAB_COLORS);
inline bool check();

}  // namespace add

// ============================================================================
//  14. Working with vertices, edges and faces
//      (add.py: _src/55_mesh_ops.py)
// ============================================================================
namespace add {

using Edge = std::pair<int, int>;

//: A new position for a vertex: a Point, or {x, y, z} in which a coordinate may be std::nullopt to
//: keep its old value (add.py's None) -- add::set_vertex(M, 3, {std::nullopt, 2.5, std::nullopt}).
struct PartialPoint {
    std::optional<double> x, y, z;
    PartialPoint() {}
    PartialPoint(const Point& p) : x(p.x), y(p.y), z(p.z) {}
    PartialPoint(std::optional<double> x_, std::optional<double> y_, std::optional<double> z_)
        : x(x_), y(y_), z(z_) {}
};

namespace detail {
//: {(a, b): face} for every directed edge of the faces; -1 for an edge in more than one face.
inline std::map<Edge, int> directed_edges(const Mesh& M);
//: The faces round a vertex in order, each as (face, the vertex its edge leaves towards), and whether
//: the ring closes (add.py's _rings gives one such pair per vertex).
struct VertexRing {
    std::vector<std::pair<int, int>> ring;
    bool closed = false;
};
inline std::vector<VertexRing> rings(const Mesh& M);
}  // namespace detail

//: The coordinates of vertex i (a negative i counts from the end, as in Python).
inline Point vertex(const Mesh& M, int i);
//: A copy of the mesh with vertex i moved to ``point`` (a std::nullopt coordinate keeps its value).
inline Mesh set_vertex(const Mesh& M, int i, const PartialPoint& point);
//: Like set_vertex for several vertices at once: {{index, new point}, ...} -- add.py's dict, so the
//: changes are made in the order given, and an index given twice counts once, with its last point.
inline Mesh set_vertices(const Mesh& M, const std::vector<std::pair<int, PartialPoint>>& changes);
//: The same with a std::map {index: new point} (made in the order of the indices).
template <class P, class = std::enable_if_t<std::is_convertible<P, PartialPoint>::value>>
inline Mesh set_vertices(const Mesh& M, const std::map<int, P>& changes) {
    return set_vertices(M, std::vector<std::pair<int, PartialPoint>>(changes.begin(), changes.end()));
}
//: A copy of the mesh with vertex i shifted by ``delta``.
inline Mesh move_vertex(const Mesh& M, int i, const Point& delta);
//: The index of the vertex closest to ``point`` (-1 for a mesh without vertices).
inline int nearest_vertex(const Mesh& M, const Point& point);
//: Every edge once, as (a, b) with a < b, sorted.
inline std::vector<Edge> edges(const Mesh& M);
inline std::vector<Edge> edges();
//: The distance between vertices a and b.
inline double edge_length(const Mesh& M, int a, int b);
//: The length of every edge, in the order edges() lists them.
inline std::vector<double> edge_lengths(const Mesh& M);
inline std::vector<double> edge_lengths();
//: The average edge length.
inline double mean_edge_length(const Mesh& M);
inline double mean_edge_length();
//: neighbours[i] = sorted list of the vertices joined to vertex i.
inline std::vector<std::vector<int>> adjacency(const Mesh& M);
inline std::vector<std::vector<int>> adjacency();
//: The vertices joined to vertex i by an edge (in order round it on a closed mesh).
inline std::vector<int> neighbors(const Mesh& M, int i);
inline std::vector<int> neighbours(const Mesh& M, int i);
//: How many edges vertex i has.
inline int valence(const Mesh& M, int i);
//: The average distance from vertex i to its neighbours.
inline double mean_neighbor_distance(const Mesh& M, int i);
//: The faces that meet at vertex i.
inline std::vector<int> vertex_faces(const Mesh& M, int i);
//: The unit normal at vertex i.
inline Point vertex_normal(const Mesh& M, int i);
//: The centre (average corner) of face i.
inline Point face_center(const Mesh& M, int i);
//: The unit normal of face i.
inline Point face_normal(const Mesh& M, int i);
//: The area of face i.
inline double face_area(const Mesh& M, int i);
//: The centre of every face.
inline Points face_centers(const Mesh& M);
inline Points face_centers();
//: The edges that belong to only one face, as directed (a, b) pairs.
inline std::vector<Edge> boundary_edges(const Mesh& M);
inline std::vector<Edge> boundary_edges();
//: The open borders of a mesh as closed rings of vertex indices.
inline std::vector<std::vector<int>> boundary_loops(const Mesh& M);
inline std::vector<std::vector<int>> boundary_loops();
//: Push every vertex out along its normal by ``amount``.
inline Mesh inflate(const Mesh& M, double amount);
//: Project every vertex onto a sphere (``amount`` 0..1 of the way).
inline Mesh spherify(const Mesh& M, std::optional<Point> center = std::nullopt, std::optional<double> r = std::nullopt,
                     double amount = 1.0);
//: Split every face into four (triangles) or one quad per corner, ``steps`` times.
inline Mesh refine(const Mesh& M, int steps = 1);
//: The dual polyhedron.
inline Mesh dual(const Mesh& M, std::optional<Color> color = std::nullopt);
//: Cut every corner off (``t``: how far along the edges); the new corner faces are painted ``color``.
inline Mesh truncate(const Mesh& M, double t = 1.0 / 3.0, const Color& color = DEFAULT_COLOR);
//: Paint every face by its number of corners: {corners: colour}; the others get ``fallback`` (add.py's
//: ``default``) or keep their colour.
inline Mesh color_by_sides(const Mesh& M, const std::map<int, Color>& colors,
                           std::optional<Color> fallback = std::nullopt);

}  // namespace add

// ============================================================================
//  15. Booleans: union, difference, intersection, cut
//      (add.py: _src/60_boolean.py)
// ============================================================================
// Two solids can be added together, cut out of one another, or intersected.
// The idea used here needs no library and fits on one screen:
//
//   1. Wherever the other model's triangles could cut one of ours, slice ours
//      along their planes.  After that every piece lies wholly inside or
//      wholly outside the other solid -- no piece straddles the boundary.
//   2. Ask of each piece: is it inside?  Shoot a ray from just above the
//      piece's middle and count how many times it crosses the other surface.
//      An odd count means inside.
//   3. Keep the pieces the operation asks for, and turn the borrowed ones
//      round when the operation says so:
//
//        union         keep A outside B  +  B outside A
//        intersection  keep A inside  B  +  B inside  A
//        difference    keep A outside B  +  B inside  A, reversed
//
// Two grids keep both steps local, so the work grows roughly with the number
// of faces rather than with its square.  Booleans want *closed* solids --
// add::check() will tell you whether yours is closed.
namespace add {

//: How far a point may be from a plane and still count as lying in it.
inline constexpr double BOOL_EPS = 1e-9;

namespace detail {

//: Where a point or a polygon lies with respect to a plane (add.py's _COPLANAR ... _SPANNING).
inline constexpr int COPLANAR = 0, FRONT = 1, BACK = 2, SPANNING = 3;

//: One planar polygon that remembers its plane and its colour (add.py's _Poly).
struct Poly {
    Points pts;
    Color c;
    Point n;                                   // the unit normal (0 for a polygon without area)
    double w = 0.0;                            // n . p for the points p of the plane
    //: The plane worked out from the corners (Newell's normal).
    Poly(Points pts_, const Color& c_);
    //: The plane given.
    Poly(Points pts_, const Color& c_, const Point& n_, double w_) : pts(std::move(pts_)), c(c_), n(n_), w(w_) {}
};

//: Cut ``poly`` with plane (pn, pw); a polygon lying in the plane or entirely on one side is filed whole.
inline void split(const Point& pn, double pw, const Poly& poly, std::vector<Poly>& front, std::vector<Poly>& back,
                  double eps = BOOL_EPS);
//: Python's ``min(q[a] for q in pts)`` / ``max(...)``: coordinate ``a`` (the first of equal values).
inline double coord_min(const Points& pts, int a);
inline double coord_max(const Points& pts, int a);

//: Python's ``int(math.floor(x))`` -- a grid cell number -- kept exactly as a whole-number double, so
//: that it never overflows (Python's integers have no limit either); an exception for a NaN or an
//: infinite ``x``, as in Python.
inline double floor_cell(double x);
//: The next whole number after ``i`` that a double can hold: i + 1 (beyond 2**53 the next double).
//: Python's ``range`` also visits the numbers in between, but no point ever falls into their cells.
inline double next_cell(double i);
//: A grid cell: (i, j, k) whole numbers (k = 0 for a 2D grid).
struct GridKey {
    double i, j, k;
    bool operator==(const GridKey& o) const { return i == o.i && j == o.j && k == o.k; }
};
struct GridKeyHash {
    size_t operator()(const GridKey& c) const;
};

//: A Python ``set`` of whole numbers 0, 1, 2 ... that goes through them in the order CPython's
//: own set does (its hash table, slot by slot) -- the order decides which plane cuts first.
class IntSet {
  public:
    IntSet() : table_(8, -1) {}
    //: Add a number (nothing happens when it is already there).
    void add(int key);
    //: The numbers, in the order a Python ``for`` loop over the set gives them.
    std::vector<int> items() const;

  private:
    std::vector<int> table_;                   // -1: an empty slot
    size_t mask_ = 7, fill_ = 0, used_ = 0;
    //: The slot where ``key`` is, or the free slot where it would go.
    size_t slot(int key) const;
    void resize(size_t minused);
};

//: Which triangles live near a given box -- a uniform 3D hash (add.py's _BoxGrid).  Triangles are
//: filed in every cell their bounding box touches; one that would fill more than MAX_CELLS cells
//: goes on the short "oversize" list that every query checks.
struct BoxGrid {
    static constexpr long long MAX_CELLS = 64;
    double cell = 0.0;
    std::unordered_map<GridKey, std::vector<int>, GridKeyHash> buckets;
    std::vector<int> oversize;
    std::vector<std::array<Point, 2>> boxes;
    BoxGrid(const std::vector<Poly>& polys, double diagonal);
    //: The cells of the box lo..hi, or nothing (add.py: None) when there are more than ``limit``.
    std::optional<std::vector<GridKey>> keys(const Point& lo, const Point& hi,
                                             std::optional<long long> limit = std::nullopt) const;
    //: Indices of triangles whose bounding box overlaps lo..hi (in add.py's order).
    std::vector<int> near(const Point& lo, const Point& hi) const;
};

//: Answers "is this point inside the solid?" by counting ray crossings (add.py's _RayIndex).
//: All rays travel in the same direction, so the triangles are bucketed once on the two axes
//: across that direction.
struct RayIndex {
    Point d, e1, e2;
    double cell = 0.0;
    std::unordered_map<GridKey, std::vector<int>, GridKeyHash> buckets;
    std::vector<std::array<Point, 3>> tris;
    RayIndex(const std::vector<Poly>& polys, const Point& direction);
    //: true / false, or nothing (add.py: None) when the ray grazes an edge.
    std::optional<bool> inside(const Point& p) const;
};

//: Three awkward directions; if one ray grazes an edge the next one is tried.
inline const std::array<Point, 3> RAY_DIRECTIONS = {Point{0.5773502691896258, 0.5773502691896257, 0.5773502691896256},
                                                    Point{0.2672612419124244, -0.5345224838248488, 0.8017837257372732},
                                                    Point{-0.7071067811865475, 0.408248290463863, 0.5773502691896258}};

//: A plane that may cut a polygon: its id -- (triangle, 0) for the triangle's own plane,
//: (triangle, k + 1) for the plane standing on its edge k -- its normal and its offset.
struct CutPlane {
    std::pair<int, int> pid;
    Point n;
    double w;
};

//: A mesh prepared for boolean work: triangles, a box grid and ray indexes (add.py's _Solid).
struct Solid {
    std::vector<Poly> polys;
    std::optional<BoxGrid> grid;               // (add.py: None for a mesh without triangles)
    std::vector<RayIndex> rays;
    Point lo, hi;
    double scale = 0.0;
    explicit Solid(const Mesh& M);
    //: The ray index of direction ``which``, built the first time it is needed.
    const RayIndex& ray_index(size_t which);
    //: Is point ``p`` inside this solid?
    bool contains(const Point& p);
    //: Planes to cut ``poly`` with, and the triangles it may lie on (flush with it).
    std::pair<std::vector<CutPlane>, std::vector<int>> cutters(const Poly& poly) const;
    //: Does ``point`` sit on one of the ``flush`` triangles?  +1 when the triangle faces the same
    //: way as ``plane_normal``, -1 when the other way, nothing (add.py: None) when on none of them.
    std::optional<int> facing_at(const Point& point, const Point& plane_normal, const std::vector<int>& flush) const;
};

//: A piece of a face, cut until it cannot straddle the other solid, with the triangles it lies
//: flush on.  (``bare``: add.py gave up on a pathological face and returned the bare piece, which
//: its caller cannot unpack -- an error there, so here.)
struct FlushPiece {
    Poly piece;
    std::vector<int> flush;
    bool bare = false;
};
//: Chop ``poly`` until no piece can straddle ``other``'s surface.
inline std::vector<FlushPiece> split_against(const Poly& poly, const Solid& other);
//: Which pieces an operation keeps: a set drawn from "in", "out", "same" and "opp".
using KeepSet = std::set<std::string>;
//: Cut ``source``'s faces against ``other`` and keep the wanted pieces (turned round with ``flip``,
//: painted ``paint`` when it is given).
inline std::vector<Poly> keep_pieces(const Solid& source, Solid& other, const KeepSet& keep, bool flip,
                                     std::optional<Color> paint = std::nullopt);
//: Mesh -> list of triangles (so no face can be twisted or non-planar).
inline std::vector<Poly> to_polys(const Mesh& M);
//: List of polygons -> Mesh, welded and with its T-junctions closed.
inline Mesh from_polys(const std::vector<Poly>& polys, bool tidy = true);
//: True when two meshes cannot possibly touch.
inline bool boxes_apart(const Mesh& A, const Mesh& B, double slack = 1e-9);
//: What an operation keeps of A and of B, and whether B's pieces are turned round.
struct BoolRule {
    KeepSet keep_a, keep_b;
    bool flip_b;
};
//: Which pieces each operation keeps ("union", "intersection", "difference").  A gets the shared
//: surface so that a patch where the two solids are flush is kept exactly once.
inline const std::map<std::string, BoolRule>& RULES();
//: The three boolean operations, all from the same two half-steps.
inline Mesh csg(const Mesh& A, const Mesh& B, const std::string& op, std::optional<Color> paint = std::nullopt);
//: Chain a bag of (a, b) segments into closed rings of points.
inline std::vector<Points> loops(const std::vector<std::pair<Point, Point>>& edges);

}  // namespace detail

//: Fuse solids into one, removing everything hidden inside.  (``union`` is a
//: C++ keyword: the function is called union_; add_solids is the same.)
inline Mesh union_(const std::vector<Mesh>& meshes);
inline Mesh union_(const Mesh& A, const Mesh& B);
//: Cut the other solids out of A (``paint``: the colour of the cut surfaces, else each keeps its cutter's).
inline Mesh difference(const Mesh& A, const std::vector<Mesh>& others, std::optional<Color> paint = std::nullopt);
inline Mesh difference(const Mesh& A, const Mesh& B, std::optional<Color> paint = std::nullopt);
//: Keep only the space that all the solids have in common.
inline Mesh intersect(const std::vector<Mesh>& meshes);
inline Mesh intersect(const Mesh& A, const Mesh& B);
//: Everything that is in one solid or the other but not in both.
inline Mesh symmetric_difference(const Mesh& A, const Mesh& B);
//: Aliases: add_solids = union_, subtract = difference, common = intersect.
inline Mesh add_solids(const std::vector<Mesh>& meshes);
inline Mesh add_solids(const Mesh& A, const Mesh& B);
inline Mesh subtract(const Mesh& A, const std::vector<Mesh>& others);
inline Mesh subtract(const Mesh& A, const Mesh& B);
inline Mesh common(const std::vector<Mesh>& meshes);
inline Mesh common(const Mesh& A, const Mesh& B);
//: Slice a solid with an infinite plane and keep the part behind it (``cap`` closes the cut).
inline Mesh cut(const Mesh& M, const Point& point = {0, 0, 0}, const Point& normal = {0, 1, 0}, bool cap = true,
                std::optional<Color> color = std::nullopt);
//: Is point p inside the (closed) mesh?  (A list of points gives a list of answers, and is far
//: faster than asking one point at a time.  As in add.py, an empty list is an error.)
inline bool inside(const Mesh& M, const Point& p);
inline std::vector<bool> inside(const Mesh& M, const Points& ps);

}  // namespace add

// ============================================================================
//  16. Smooth surfaces: Catmull-Clark subdivision and its limit surface
//      (add.py: _src/65_subdivide.py)
// ============================================================================
namespace add {

namespace detail {
//: The neighbours and the faces counter-clockwise around a vertex (add.py's ``(nbrs, faces)``).
struct OrderedRing {
    std::vector<int> nbrs, faces;
};
//: A polygon mesh with its edges and adjacency worked out (add.py's _Topo).  ``E[e] = {a, b, f0, f1}``
//: (f1 = -1 on a border), ``VF[v]`` the faces at a vertex, ``VE[v]`` the edges at a vertex, ``FE[f][k]``
//: the edge leaving corner k of face f, ``FN[f][k]`` the face across that edge.  Building one throws
//: std::invalid_argument (add.py: ValueError) for a face with fewer than 3 corners, a degenerate edge,
//: an edge used twice by one face or an edge shared by more than two faces.
struct Topo {
    Points V;
    std::vector<Face> F;
    std::vector<std::array<int, 4>> E;
    std::vector<std::vector<int>> VF, VE, FE, FN;
    std::vector<bool> boundary;

    Topo() {}
    Topo(Points V_, std::vector<Face> F_);
    //: Is every face a quad?
    bool all_quads() const;
    //: The average corner of face ``f``.
    Point centroid(int f) const;
    //: Neighbours and faces counter-clockwise around ``v``; std::nullopt (add.py: None) when they
    //: do not make one fan.
    std::optional<OrderedRing> ordered_ring(int v) const;
};
//: One Catmull-Clark step: the new topology and ``parent[i]``, the face new quad ``i`` came from.
inline std::pair<Topo, std::vector<int>> cc_subdivide(const Topo& T);
//: Subdominant eigenvalue of the Catmull-Clark subdivision matrix at a valence-N vertex.
inline double cc_lambda(int N);
//: Exponent of the radial reparameterisation at a valence-N vertex: -1 / log2(lambda_N).
inline double cc_gamma(int N);
//: Limit position of every vertex (a mesh with other polygons than quads is subdivided once first).
inline Points cc_limit_positions(const Topo& T);
//: Two tangent vectors of the limit surface at an inner vertex (std::nullopt: add.py's None).
inline std::optional<std::pair<Point, Point>> cc_limit_tangents(const Topo& T, int v);
//: The four uniform cubic B-spline basis functions at ``t``.
inline std::array<double, 4> bspline_basis(double t);
//: The 4 x 4 control net ``P[i][j]`` of a bicubic B-spline patch.
using BicubicNet = std::array<std::array<Point, 4>, 4>;
//: The point of the bicubic B-spline patch with control net ``P`` at (u, v).
inline Point eval_bicubic(const BicubicNet& P, double u, double v);
//: The control net of quad ``f`` when its surroundings are regular, else std::nullopt (add.py: None).
inline std::optional<BicubicNet> regular_stencil(const Topo& T, int f);
//: The faces around face ``f`` as a small mesh of their own, ``f`` first with ``origin_corner`` first.
inline Topo neighbourhood(const Topo& T, int f, int origin_corner);
//: Evaluates the limit surface over one quad next to an extraordinary vertex by subdividing its
//: neighbourhood only as deep as a query needs (add.py's _PatchTree).
class PatchTree {
  public:
    static constexpr int MAX_DEPTH = 48;
    PatchTree(const Topo& T, int f);
    Point eval(double u, double v);

  private:
    struct Node {
        Topo M;
        int depth = 0;
        std::optional<BicubicNet> P;
        std::array<std::unique_ptr<Node>, 4> child;
        std::optional<Topo> sub;
    };
    std::unique_ptr<Node> root;
    static std::unique_ptr<Node> node(Topo L, int depth);
    Node* child(Node& nd, int k);
};
//: The paper's norm nu(s, t) = ((s^p + t^p) / (1 + s^p t^p))^(1/p) (max(s, t) for p > 64).
inline double nu_norm(double a, double b, double p);
//: The regular m-gon in the plane split into m kites [corner_k, edge_mid_k, centre, edge_mid_{k-1}]:
//: the parameter domain of one control face (add.py's _PolygonDomain).
class PolygonDomain {
  public:
    int m = 0;
    std::vector<Point2> P, E;
    explicit PolygonDomain(int m_);
    //: The (cached) domain of an m-gon.
    static const PolygonDomain& get(int m);
    Point2 kite_map(int k, double u, double v) const;
    int kite_of(const Point2& x) const;
    Point2 kite_inverse(int k, const Point2& x) const;
    std::vector<double> wachspress(const Point2& x) const;
    double corner_nu(const std::vector<double>& lam, int k, double p) const;
};
//: The map psi of one control face (add.py's ``(trivial, apply)``): ``trivial`` when it changes
//: nothing, ``apply(x)`` (or ``psi(x)``) the Wachspress blend of the radial corner maps, then the
//: radial centre map.
struct FaceReparam {
    PolygonDomain dom;
    std::vector<double> gamma;
    double gamma_centre = 1.0, p = 2.0;
    bool any_corner = false, trivial = true;
    Point2 apply(const Point2& x) const;
    Point2 operator()(const Point2& x) const { return apply(x); }
};
inline FaceReparam face_reparam(const PolygonDomain& dom, const std::vector<double>& gamma, double gamma_centre,
                                double p);
//: How many nodes smooth() puts inside an m-gon (neither corners nor on its edges) for ``n``.
inline long long face_node_count(long long m, long long n);
//: The Topo of a mesh (tidied first when asked) and the mesh it was built from.
inline std::pair<Topo, Mesh> topology_of(const Mesh& M, bool repair = true);
//: Weld, drop rubbish, close T-junctions, cut non-manifold edges and vertices apart, drop unused
//: vertices and make the winding consistent -- everything subdivision needs.
inline Mesh repair_for_subdivision(const Mesh& M);
//: Separate faces that meet along an edge of three or more faces, or only at a vertex, by giving
//: them copies of the vertex (in place).
inline Mesh& cut_non_manifold(Mesh& M);
//: Python's ``a % b`` and ``a // b`` for whole numbers (b > 0): never negative / rounded down.
inline long long subd_mod(long long a, long long b);
inline long long subd_floordiv(long long a, long long b);
//: Python's ``xs.index(x)``: the first place of ``x`` (std::invalid_argument when it is not there).
inline int subd_index(const std::vector<int>& xs, int x);
//: Python's float ``x ** y`` (detail::py_pow) with its errors: zero to a negative power throws
//: std::domain_error (ZeroDivisionError), a result too large std::overflow_error (OverflowError).
inline double subd_pow(double x, double y);
}  // namespace detail

//: Classical Catmull-Clark subdivision, ``steps`` times: every face becomes quads and the shape is
//: rounded.  Faces inherit the colour of the face they came from; ``repair`` first welds and tidies
//: the mesh the way subdivision needs (parts that only touch are cut apart).
inline Mesh catmull_clark(const Mesh& M, int steps = 1, bool repair = true);
//: Round a polygon mesh into its Catmull-Clark limit surface, sampled with ``n`` cells along every
//: control edge -- for any ``n`` (the generalised algorithm, Sabaliauskas 2026).  ``uniform`` applies
//: the reparameterisation near extraordinary vertices and non-quad faces, ``centre`` the extra centre
//: map of non-quad faces, ``p`` is the exponent of the blending norm, ``scale`` multiplies the
//: exponents, ``repair`` tidies the mesh first.
inline Mesh smooth(const Mesh& M, int n = 4, bool uniform = true, bool centre = true, double p = 2.0,
                   double scale = 1.0, bool repair = true);
//: ``subdivide`` is catmull_clark.
inline Mesh subdivide(const Mesh& M, int steps = 1, bool repair = true);

}  // namespace add

// ============================================================================
//  17. Saving and loading
//      (add.py: _src/70_io.py)
// ============================================================================
// (Reading a font folder needs the file system library of C++17.)
#include <cerrno>
#include <filesystem>
#include <iterator>
#include <system_error>

namespace add {

namespace detail {
//: The mesh itself, or a copy fit to be written: no face visits a vertex twice,
//: no coordinate is not a number.
inline Mesh writable(const Mesh& M);
//: The face lines of an OFF file (each face cut to at most four corners).
inline std::vector<std::string> off_face_lines(const Mesh& M, long long base = 0);
//: The pieces an OFF file carries face f as: triangles and quadrilaterals.
inline std::vector<Face> off_pieces(const Mesh& M, const Face& f);
//: ``color_rrggbb`` (+ ``_aNNN`` see-through, ``_tNAME`` textured): a material name.
inline std::string material_name(const Color& c);
inline void write_off(const std::string& path, const Mesh& M);
inline void write_obj(const std::string& path, const Mesh& M, std::optional<std::string> mtl_path = std::nullopt);
inline void write_ply(const std::string& path, const Mesh& M);
inline void write_stl(const std::string& path, const Mesh& M);
//: Is ``M`` the current scene itself?  (save, off, obj and Stream::add then empty it after
//: writing, as add.py does when no mesh is given.)
inline bool is_scene(const Mesh& M) { return &M == &current(); }
//: ``x`` with ``decimals`` decimals, trailing zeros and point dropped, "" and "-0" written as "0"
//: (add.py's ``_rounded(decimals)(x)``, the number format of a Stream with a ``precision``).
inline std::string rounded(double x, int decimals);

// -- reading files as Python reads them ---------------------------------------
// Python's exceptions are these C++ ones here: ValueError -> std::invalid_argument, IndexError
// and KeyError -> std::out_of_range, OverflowError -> std::overflow_error, OSError (a file that
// cannot be opened) -> std::system_error.  load_font() skips a file on the first and the last,
// as add.py does.

//: The text of a file as Python's ``open(path).read()`` gives it: UTF-8 (a file that is not
//: is a ValueError), with "\r\n" and "\r" read as "\n"; a missing file or a folder: OSError.
inline std::string read_text(const std::string& path);
//: Python's ``s.split(sep)`` with a one-character separator.
inline std::vector<std::string> split_on(const std::string& s, char sep);
//: Python's ``s.split()`` and ``s.strip()`` -- Python's whitespace: also \x1c..\x1f and the
//: Unicode spaces U+0085, U+00A0, U+1680, U+2000..U+200A, U+2028, U+2029, U+202F, U+205F, U+3000.
inline std::vector<std::string> py_split(const std::string& s);
inline std::string py_strip(const std::string& s);
//: Python's ``float(word)`` and ``int(word)`` of one word of a file: std::invalid_argument
//: (ValueError) for anything Python refuses -- hexadecimal, "1e", "1__0" ...  (Digits other
//: than 0-9 are refused, which Python would take; an int beyond 64 bits stops at the limit.)
inline double py_float(const std::string& word);
inline long long py_int(const std::string& word);
//: The characters (code points) of a UTF-8 string, each as a string (Python's ``for ch in s``).
inline std::vector<std::string> utf8_chars(const std::string& s);
//: Python's ``s.upper()`` for the letters of Latin-1, Latin Extended-A, Greek and Cyrillic
//: (U+0000..U+017F, U+0370..U+052F; the sharp s becomes SS); any other character stays as it is.
inline std::string py_upper(const std::string& s);
//: add.py's ``rgb()`` of a list of 3 or 4 floats read from a file (the fourth: the opacity);
//: a NaN is a ValueError and an infinity an OverflowError there, as in Python.
inline Color rgb_list(const std::vector<double>& color);
//: The non-empty lines of a file with ``#`` comments stripped (add.py's ``_clean_lines``).
inline std::vector<std::string> clean_lines(const std::string& path);
//: The readers behind load(): .off, .obj (with its .mtl), .ply.
inline Mesh read_off(const std::string& path, const std::optional<Color>& color = std::nullopt);
inline Mesh read_obj(const std::string& path, const std::optional<Color>& color = std::nullopt);
//: {material name: colour}, the opacity (``d`` / ``Tr``) and texture (``map_Kd``) included.
inline std::map<std::string, Color> read_mtl(const std::string& path);
inline Mesh read_ply(const std::string& path, const std::optional<Color>& color = std::nullopt);
}  // namespace detail

//: Write a model to disk; the file format follows the extension: .off, .obj (+ .mtl),
//: .ply or .stl.  ``save(path)`` saves -- and then empties -- the current scene.  The scene
//: passed as the mesh counts as no mesh, so that add.py's ``add.save("m.obj", colors=50)``
//: is ``add::save("m.obj", add::scene(), {}, 50)``; ``clear_scene = false`` keeps it.
//: ``colors``: reduce the model to at most that many colours first; ``clean``: tidy it
//: on the way out (see clean()).
inline std::string save(const std::string& path, const Mesh& M, std::optional<bool> clear_scene = std::nullopt,
                        std::optional<int> colors = std::nullopt, bool clean = true);
inline std::string save(const std::string& path);
//: Write an OFF file exactly as the model is (and empty the scene) -- the add.py 1.2 behaviour.
inline std::string off(const std::string& path, const Mesh& M);
inline std::string off(const std::string& path);
//: Write an OBJ file plus the matching MTL colour file.
inline std::string obj(const std::string& path, const Mesh& M, std::optional<std::string> mtl = std::nullopt);
inline std::string obj(const std::string& path);
//: How many bytes save() would write for this model as .obj.
inline long long obj_size(const Mesh& M);
inline long long obj_size();

//: Write a model part by part, straight to disk (.obj or .off), so that a model far
//: bigger than the computer's memory can still be built (see add.py's Stream):
//:
//:     auto out = add::stream("castle.obj");
//:     add::sphere({0, 0, 0}, 0.4, 20, "red");
//:     out->add();                          // the scene, then cleared
//:     out->add(add::make([] { add::box({0, 5, 0}, 2, "gold"); }));
//:     out->close();                        // (the destructor closes it too)
//:
//: ``precision``: the decimals of every coordinate; ``faces``, ``vertices``, ``bytes`` (the
//: characters written), ``removed`` and ``cut`` (what the tidying did) count as it goes.
class Stream {
  public:
    std::string path;
    bool clean_parts = true;                                   // (add.py: ``clean``)
    std::optional<int> precision;
    long long faces = 0, vertices = 0, bytes = 0, removed = 0, cut = 0;
    std::vector<std::pair<Color, std::string>> materials;     // in the order they came

    Stream(const std::string& path, bool clean = true, std::optional<int> precision = std::nullopt);
    ~Stream();
    Stream(const Stream&) = delete;
    Stream& operator=(const Stream&) = delete;
    //: Write a mesh now (``clean`` overrides the stream's setting); the number of faces written.
    //: The scene itself (add::scene()) is written and then cleared, as by add().
    long long add(const Mesh& M, std::optional<bool> clean = std::nullopt);
    //: Write the current scene now and clear it.
    long long add();
    //: Finish the file (the .mtl, or the OFF header).
    std::string close();

  private:
    std::string kind_, mtl_, vertices_path_, faces_path_;
    std::ofstream file_, faces_file_;
    bool open_ = false, has_current_ = false;
    Color current_;
    long long vt_ = 0;
    std::unordered_map<Color, std::string, ColorHash> material_index_;   // materials, to look up
    std::string num(double x) const;
};
//: Open a Stream: a model written to ``path`` part by part.
inline std::unique_ptr<Stream> stream(const std::string& path, bool clean = true,
                                      std::optional<int> precision = std::nullopt);

//: Read a model from an .off, .obj or .ply file (``color`` for faces without one).
inline Mesh load(const std::string& path, std::optional<Color> color = std::nullopt);
//: Write a picture -- rows of colours, row 0 at the top -- as a PNG file (to use as a texture).
//: (add.py compresses the pixels with zlib; add.hpp stores them uncompressed: another file,
//: the same picture.)
inline std::string write_png(const std::string& path, const std::vector<std::vector<Color>>& rows);
//: Load a whole folder of letter or digit models: {character: mesh}.  ``characters``: the ones
//: to load (every UTF-8 character one file; or a list of names); std::nullopt: every file
//: ending in ``suffix``.  A file that cannot be read is left out.
inline std::map<std::string, Mesh> load_font(const std::string& folder,
                                             std::optional<std::string> characters = std::nullopt,
                                             const std::string& suffix = ".off");
inline std::map<std::string, Mesh> load_font(const std::string& folder, const std::vector<std::string>& characters,
                                             const std::string& suffix = ".off");
//: Lay a string of already-loaded glyph meshes out in a row and merge them.
inline Mesh typeset(const std::string& characters, const std::map<std::string, Mesh>& font,
                    const Point& at = {0, 0, 0}, double size = 1.0, double spacing = 1.0,
                    std::optional<Color> color = std::nullopt,
                    const std::array<Point, 2>& plane = {Point{1, 0, 0}, Point{0, 1, 0}});

}  // namespace add

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

// ============================================================================
//  19. The add.py 1.2 names, still here
//      (add.py: _src/80_compat.py)
// ============================================================================
namespace add {

//: add.py 1.2 name for polygon().
inline void newface(const Points& A, const Color& RGB);
//: add.py 1.2 name for box().
inline void cube(const Point& c, double e, const Color& RGB);
//: add.py 1.2 name for cuboid().
inline void rectangle3D(const Point& c, const Point& e, const Color& RGB);
//: add.py 1.2 name for frame() (a hollow cube of bars).
inline void cube2(const Point& c, double e, double b, const Color& RGB);
//: add.py 1.2 name for tube() (a cylinder with no lids).
inline void cylinder2(const Point& A, const Point& B, double r, int k, const Color& RGB);
//: add.py 1.2 name for cup() (a cylinder closed at A).
inline void cylinder3(const Point& A, const Point& B, double r, int k, const Color& RGB);
//: add.py 1.2 name for cone_open() (the slanted wall only).
inline void cone2(const Point& A, const Point& B, double r, int k, const Color& RGB);
//: Other names: ball = sphere, block = cuboid3D = cuboid, lathe = solid_of_revolution = revolve,
//: weld = clean, scale = zoom, translate = move, reflect = mirror.
inline void ball(const Point& center, double r, int k = 10, const ColorOf<Point>& color = DEFAULT_COLOR,
                 std::optional<int> subdivisions = std::nullopt);
inline void block(const Point& center, const Point& sizes, const Color& color = DEFAULT_COLOR);
inline void cuboid3D(const Point& center, const Point& sizes, const Color& color = DEFAULT_COLOR);
inline void lathe(const Profile& profile, const Point& A = {0, 0, 0}, const Point& B = {0, 1, 0}, double t0 = 0.0,
                  double t1 = 1.0, int steps = 40, int k = 32, const ColorOf<double, double>& color = DEFAULT_COLOR,
                  double angle = 2.0 * pi, bool caps = true);
inline void solid_of_revolution(const Profile& profile, const Point& A = {0, 0, 0}, const Point& B = {0, 1, 0},
                                double t0 = 0.0, double t1 = 1.0, int steps = 40, int k = 32,
                                const ColorOf<double, double>& color = DEFAULT_COLOR, double angle = 2.0 * pi,
                                bool caps = true);
inline void lathe(const std::function<Point2(double)>& profile, const Point& A = {0, 0, 0},
                  const Point& B = {0, 1, 0}, double t0 = 0.0, double t1 = 1.0, int steps = 40, int k = 32,
                  const ColorOf<double, double>& color = DEFAULT_COLOR, double angle = 2.0 * pi, bool caps = true);
inline void solid_of_revolution(const std::function<Point2(double)>& profile, const Point& A = {0, 0, 0},
                                const Point& B = {0, 1, 0}, double t0 = 0.0, double t1 = 1.0, int steps = 40,
                                int k = 32, const ColorOf<double, double>& color = DEFAULT_COLOR,
                                double angle = 2.0 * pi, bool caps = true);
inline Mesh weld(const Mesh& M, double tol = 1e-7, bool weld = true, bool degenerate = true, bool duplicates = true,
                 bool internal = true, bool unused = true, bool normals = false, CleanReport* report = nullptr,
                 bool overlaps = true, bool convex = true);
inline Mesh weld();
inline Mesh scale(const Mesh& M, double s, std::optional<Point> about = std::nullopt);
inline Mesh translate(const Mesh& M, const Point& V);
inline Mesh reflect(const Mesh& M, const Point& point = {0, 0, 0}, const Point& normal = {1, 0, 0});
//: Build a small model that exercises most of the library, check it and save it to ``path``.
inline std::string demo(const std::string& path = "demo.off");

}  // namespace add

namespace add {

namespace detail {

inline void add_grid(Mesh& M, const std::vector<Points>& P, const CellPaint& color, bool wrap_u, bool wrap_v,
                     bool flip) {
    if (P.empty()) throw std::out_of_range("list index out of range");    // (add.py: len(P[0]) fails)
    int nu = (int)P.size(), nv = (int)P[0].size();
    int base = (int)M.V.size();
    for (const Points& row : P)
        for (const Point& p : row) M.add_vertex(p);
    int steps_u = wrap_u ? nu : nu - 1;
    int steps_v = wrap_v ? nv : nv - 1;
    for (int i = 0; i < steps_u; ++i) {
        int i2 = (i + 1) % nu;
        for (int j = 0; j < steps_v; ++j) {
            int j2 = (j + 1) % nv;
            int a = base + i * nv + j;
            int b = base + i2 * nv + j;
            int c = base + i2 * nv + j2;
            int d = base + i * nv + j2;
            Face q = !flip ? Face{a, b, c, d} : Face{d, c, b, a};
            M.add_face(q, color(i, j));
        }
    }
}

inline Points ring(const Point& center, const Point& u, const Point& v, double r, int k, double phase) {
    Points pts;
    for (int i = 0; i < k; ++i) {
        double a = phase + 2.0 * pi * i / k;
        double cs = std::cos(a) * r, sn = std::sin(a) * r;
        pts.push_back({center[0] + u[0] * cs + v[0] * sn,
                       center[1] + u[1] * cs + v[1] * sn,
                       center[2] + u[2] * cs + v[2] * sn});
    }
    return pts;
}

inline void fan(Mesh& M, const Points& points, const Point& apex, const ColorOf<int>& color, bool flip,
                bool closed) {
    int base = (int)M.V.size();
    for (const Point& p : points) M.add_vertex(p);
    int tip = M.add_vertex(apex);
    int n = (int)points.size();
    for (int i = 0; i < (closed ? n : n - 1); ++i) {
        int j = (i + 1) % n;
        Face tri = !flip ? Face{base + i, base + j, tip} : Face{base + j, base + i, tip};
        M.add_face(tri, color(i));
    }
}

inline double signed_volume(const Mesh& M, size_t first_face) {
    double total = 0.0;
    for (size_t q = first_face; q < M.F.size(); ++q) {
        const Face& f = M.F[q];
        if (f.size() < 3) continue;
        const Point& a = M.V[f[0]];
        for (size_t t = 1; t + 1 < f.size(); ++t) {
            const Point& b = M.V[f[t]];
            const Point& c = M.V[f[t + 1]];
            total += (a[0] * (b[1] * c[2] - b[2] * c[1])
                      - a[1] * (b[0] * c[2] - b[2] * c[0])
                      + a[2] * (b[0] * c[1] - b[1] * c[0]));
        }
    }
    return total;
}

inline void make_outward(Mesh& M, size_t first_face) {
    if (signed_volume(M, first_face) < 0)
        for (size_t i = first_face; i < M.F.size(); ++i) std::reverse(M.F[i].begin(), M.F[i].end());
}

inline Mesh grid_solid(const Point& origin, const std::vector<double>& sx, const std::vector<double>& sy,
                       const std::vector<double>& sz, const std::function<bool(int, int, int)>& filled,
                       const ColorOf<int, int, int>& color) {
    int nx = (int)sx.size(), ny = (int)sy.size(), nz = (int)sz.size();
    // Coordinates of every grid line.
    std::vector<double> X{origin[0]}, Y{origin[1]}, Z{origin[2]};
    for (double s : sx) X.push_back(X.back() + s);
    for (double s : sy) Y.push_back(Y.back() + s);
    for (double s : sz) Z.push_back(Z.back() + s);

    Mesh M;
    std::unordered_map<long long, int> index;                  // (add.py: a dict keyed by (i, j, k))
    auto point = [&](int i, int j, int k) {
        long long key = ((long long)i * (ny + 1) + j) * (nz + 1) + k;
        auto it = index.find(key);
        if (it != index.end()) return it->second;
        int made = M.add_vertex({X[i], Y[j], Z[k]});
        index.emplace(key, made);
        return made;
    };
    auto solid = [&](int i, int j, int k) {
        if (0 <= i && i < nx && 0 <= j && j < ny && 0 <= k && k < nz) return (bool)filled(i, j, k);
        return false;
    };
    Color c = color.color;                                     // (a colour function: set for every cell)
    // The corners of each wall are listed in braces, which C++ evaluates left to
    // right like add.py's list, so the vertices are made in the same order.
    for (int i = 0; i < nx; ++i) {
        for (int j = 0; j < ny; ++j) {
            for (int k = 0; k < nz; ++k) {
                if (!solid(i, j, k)) continue;
                if (color.callable()) c = color(i, j, k);
                if (!solid(i - 1, j, k))                       // -X wall
                    M.add_face(Face{point(i, j, k), point(i, j, k + 1), point(i, j + 1, k + 1), point(i, j + 1, k)},
                               c);
                if (!solid(i + 1, j, k))                       // +X wall
                    M.add_face(Face{point(i + 1, j, k), point(i + 1, j + 1, k), point(i + 1, j + 1, k + 1),
                                    point(i + 1, j, k + 1)},
                               c);
                if (!solid(i, j - 1, k))                       // -Y wall
                    M.add_face(Face{point(i, j, k), point(i + 1, j, k), point(i + 1, j, k + 1), point(i, j, k + 1)},
                               c);
                if (!solid(i, j + 1, k))                       // +Y wall
                    M.add_face(Face{point(i, j + 1, k), point(i, j + 1, k + 1), point(i + 1, j + 1, k + 1),
                                    point(i + 1, j + 1, k)},
                               c);
                if (!solid(i, j, k - 1))                       // -Z wall
                    M.add_face(Face{point(i, j, k), point(i, j + 1, k), point(i + 1, j + 1, k), point(i + 1, j, k)},
                               c);
                if (!solid(i, j, k + 1))                       // +Z wall
                    M.add_face(Face{point(i, j, k + 1), point(i + 1, j, k + 1), point(i + 1, j + 1, k + 1),
                                    point(i, j + 1, k + 1)},
                               c);
            }
        }
    }
    return M;
}

inline void emit(Mesh& M, double tol) {
    weld(M, tol);
    detail::current().extend(M);
}

inline std::pair<Points, std::vector<Face>> platonic(const std::string& name_) {
    std::string name = lower(name_);
    if (name == "tetrahedron" || name == "tetra") {
        Points V{{1, 1, 1}, {1, -1, -1}, {-1, 1, -1}, {-1, -1, 1}};
        std::vector<Face> F{{0, 1, 2}, {0, 3, 1}, {0, 2, 3}, {1, 3, 2}};
        return {V, F};
    }
    if (name == "cube" || name == "hexahedron" || name == "box") {
        Points V;
        for (int x : {-1, 1})
            for (int y : {-1, 1})
                for (int z : {-1, 1}) V.push_back({(double)x, (double)y, (double)z});
        std::vector<Face> F{{0, 1, 3, 2}, {4, 6, 7, 5}, {0, 4, 5, 1}, {2, 3, 7, 6}, {0, 2, 6, 4}, {1, 5, 7, 3}};
        return {V, F};
    }
    if (name == "octahedron" || name == "octa") {
        Points V{{1, 0, 0}, {-1, 0, 0}, {0, 1, 0}, {0, -1, 0}, {0, 0, 1}, {0, 0, -1}};
        std::vector<Face> F{{0, 2, 4}, {2, 1, 4}, {1, 3, 4}, {3, 0, 4}, {2, 0, 5}, {1, 2, 5}, {3, 1, 5}, {0, 3, 5}};
        return {V, F};
    }
    double phi = (1 + std::sqrt(5.0)) / 2;
    if (name == "icosahedron" || name == "icosa") {
        // The classic table: three golden rectangles, 20 triangles listed
        // counter-clockwise from outside (the same one the geodesic sphere
        // starts from).
        Points V{{-1, phi, 0}, {1, phi, 0}, {-1, -phi, 0}, {1, -phi, 0},
                 {0, -1, phi}, {0, 1, phi}, {0, -1, -phi}, {0, 1, -phi},
                 {phi, 0, -1}, {phi, 0, 1}, {-phi, 0, -1}, {-phi, 0, 1}};
        std::vector<Face> F{{0, 11, 5}, {0, 5, 1}, {0, 1, 7}, {0, 7, 10}, {0, 10, 11},
                            {1, 5, 9}, {5, 11, 4}, {11, 10, 2}, {10, 7, 6}, {7, 1, 8},
                            {3, 9, 4}, {3, 4, 2}, {3, 2, 6}, {3, 6, 8}, {3, 8, 9},
                            {4, 9, 5}, {2, 4, 11}, {6, 2, 10}, {8, 6, 7}, {9, 8, 1}};
        return {V, F};
    }
    if (name == "dodecahedron" || name == "dodeca") {
        Points V;
        for (int x : {-1, 1})
            for (int y : {-1, 1})
                for (int z : {-1, 1}) V.push_back({(double)x, (double)y, (double)z});
        double inv = 1.0 / phi;
        for (int s1 : {-1, 1}) {
            for (int s2 : {-1, 1}) {
                V.push_back({0, s1 * inv, s2 * phi});
                V.push_back({s1 * inv, s2 * phi, 0});
                V.push_back({s1 * phi, 0, s2 * inv});
            }
        }
        std::vector<Face> F = hull_faces(V, 5);
        return {V, F};
    }
    throw std::invalid_argument("unknown polyhedron: '" + name + "'");
}

inline std::vector<Face> hull_faces(const Points& V, int sides) {
    int n = (int)V.size();
    std::vector<Face> found;                                   // (add.py: a dict {sorted corners: ring},
    std::set<Face> keys;                                       //  in the order the faces were found)
    for (int i = 0; i < n; ++i) {
        for (int j = i + 1; j < n; ++j) {
            for (int k = j + 1; k < n; ++k) {
                Point nrm = cross(sub(V[j], V[i]), sub(V[k], V[i]));
                if (norm(nrm) < 1e-9) continue;
                nrm = unit(nrm);
                double d = dot(nrm, V[i]);
                if (d < 1e-9) {
                    nrm = scale(nrm, -1);
                    d = -d;
                }
                if (d <= 1e-9) continue;
                bool beyond = false;
                for (const Point& p : V)
                    if (dot(nrm, p) > d + 1e-9) {
                        beyond = true;
                        break;
                    }
                if (beyond) continue;
                Face on;
                for (int t = 0; t < n; ++t)
                    if (std::fabs(dot(nrm, V[t]) - d) < 1e-9) on.push_back(t);
                if ((int)on.size() != sides) continue;
                Face key = on;
                std::sort(key.begin(), key.end());
                if (keys.count(key)) continue;
                // Sort the coplanar points into a proper ring.
                Point centre;
                for (int a = 0; a < 3; ++a) {
                    double s = 0.0;                            // (add.py's _total: in order from 0)
                    for (int t : on) s += V[t][a];
                    centre[a] = s / (double)on.size();
                }
                Point u = unit(sub(V[on[0]], centre));
                Point v = cross(nrm, u);
                std::vector<std::pair<double, int>> keyed;     // (angle, corner): a stable sort by angle
                for (int t : on) keyed.push_back({std::atan2(dot(sub(V[t], centre), v), dot(sub(V[t], centre), u)), t});
                std::stable_sort(keyed.begin(), keyed.end(),
                                 [](const std::pair<double, int>& x, const std::pair<double, int>& y) {
                                     return x.first < y.first;
                                 });
                for (size_t q = 0; q < on.size(); ++q) on[q] = keyed[q].second;
                keys.insert(key);
                found.push_back(on);
            }
        }
    }
    return found;
}

}  // namespace detail

// -- flat shapes ---------------------------------------------------------------

inline void polygon(const Points& points, const Color& color) { detail::current().add_polygon(points, color); }

inline void triangle(const Point& a, const Point& b, const Point& c, const Color& color) {
    detail::current().add_polygon({a, b, c}, color);
}

inline void quad(const Point& a, const Point& b, const Point& c, const Point& d, const Color& color) {
    detail::current().add_polygon({a, b, c, d}, color);
}

inline void disc(const Point& center, const Point& normal, double r, int k, const Color& color) {
    Point d = detail::sub(normal, center);
    if (detail::norm(d) < EPS) d = normal;
    detail::Frame fr = detail::frame(d);
    Mesh M;
    detail::fan(M, detail::ring(center, fr.u, fr.v, r, k), center, color);
    detail::current().extend(M);
}

inline void ring(const Point& center, const Point& normal, double r_outer, double r_inner, int k,
                 const Color& color) {
    Point d = detail::sub(normal, center);
    if (detail::norm(d) < EPS) d = normal;
    detail::Frame fr = detail::frame(d);
    Points outer = detail::ring(center, fr.u, fr.v, r_outer, k);
    Points inner = detail::ring(center, fr.u, fr.v, r_inner, k);
    Mesh M;
    detail::add_grid(M, {inner, outer}, color, false, true);
    detail::current().extend(M);
}

inline void grid(const Point& center, const Point2& size, int nx, int nz, const ColorOf<double, double>& color,
                 const std::function<double(double, double)>& height, double thickness) {
    if (nx == 0 || nz == 0)
        throw std::domain_error("float division by zero");      // (as Python: ZeroDivisionError)
    double w = size[0], d = size[1];
    std::vector<Points> P;
    std::vector<double> xs, zs;
    for (int i = 0; i < nx + 1; ++i) {
        Points row;
        double x = center[0] - w / 2.0 + w * i / nx;
        xs.push_back(x);
        for (int j = 0; j < nz + 1; ++j) {
            double z = center[2] - d / 2.0 + d * j / nz;
            if (i == 0) zs.push_back(z);
            double y = center[1];
            if (height) y = center[1] + height(x, z);
            row.push_back({x, y, z});
        }
        P.push_back(row);
    }
    detail::CellPaint paint = color.color;
    if (color.callable())                                      // painted by the middle of each cell
        paint = detail::CellPaint(
            [&](int i, int j) { return color((xs[i] + xs[i + 1]) / 2.0, (zs[j] + zs[j + 1]) / 2.0); });
    Mesh M;
    detail::add_grid(M, P, paint, false, false, true);
    if (thickness) M = solidify(M, thickness);
    detail::current().extend(M);
}

// -- boxes and other flat-sided solids -------------------------------------------

inline void box(const Point& center, double edge, const Color& color) { cuboid(center, {edge, edge, edge}, color); }

inline void cuboid(const Point& center, const Point& sizes, const Color& color) {
    double ex = sizes[0], ey = sizes[1], ez = sizes[2];
    double x0 = center[0] - ex / 2.0, y0 = center[1] - ey / 2.0, z0 = center[2] - ez / 2.0;
    double x1 = x0 + ex, y1 = y0 + ey, z1 = z0 + ez;
    const Point P[8] = {{x0, y0, z0}, {x0, y0, z1}, {x0, y1, z0}, {x0, y1, z1},
                        {x1, y0, z0}, {x1, y0, z1}, {x1, y1, z0}, {x1, y1, z1}};
    const int F[6][4] = {{0, 4, 5, 1}, {0, 1, 3, 2}, {0, 2, 6, 4}, {1, 5, 7, 3}, {2, 3, 7, 6}, {4, 6, 7, 5}};
    Mesh& S = detail::current();
    int base = (int)S.V.size();
    for (const auto& f : F) S.add_face({base + f[0], base + f[1], base + f[2], base + f[3]}, color);
    for (const Point& p : P) S.add_vertex(p);
}

inline void frame(const Point& center, double edge, double thickness, const Color& color) {
    double e = edge, b = thickness;
    double mid = e - 2 * b;
    std::vector<double> sizes{b, mid, b};
    Point origin{center[0] - e / 2.0, center[1] - e / 2.0, center[2] - e / 2.0};
    auto filled = [](int i, int j, int k) { return (i != 1) + (j != 1) + (k != 1) >= 2; };
    detail::current().extend(detail::grid_solid(origin, sizes, sizes, sizes, filled, color));
}

inline void voxels(const std::vector<Cell>& cells_, double size, const Point& origin, const ColorOf<int, int, int>& color) {
    std::set<Cell> cells(cells_.begin(), cells_.end());
    if (cells.empty()) return;
    int lo[3], hi[3], n[3];
    for (int a = 0; a < 3; ++a) {
        auto at = [a](const Cell& c) { return a == 0 ? c.i : (a == 1 ? c.j : c.k); };
        lo[a] = hi[a] = at(*cells.begin());
        for (const Cell& c : cells) {
            lo[a] = std::min(lo[a], at(c));
            hi[a] = std::max(hi[a], at(c));
        }
        n[a] = hi[a] - lo[a] + 1;
    }
    Point start{origin[0] + lo[0] * size, origin[1] + lo[1] * size, origin[2] + lo[2] * size};
    auto filled = [&](int i, int j, int k) { return cells.count(Cell{i + lo[0], j + lo[1], k + lo[2]}) > 0; };
    detail::current().extend(detail::grid_solid(start, std::vector<double>(n[0], size),
                                                std::vector<double>(n[1], size), std::vector<double>(n[2], size),
                                                filled, color));
}

inline void pyramid(const Point& center, double edge, double height, const Color& color) {
    double e = edge, h = height;
    double x = center[0] - e / 2.0, y = center[1] - e / 2.0, z = center[2] - e / 2.0;
    Points base{{x, y, z}, {x + e, y, z}, {x + e, y, z + e}, {x, y, z + e}};
    Point apex{x + e / 2.0, y + h, z + e / 2.0};
    Mesh M;
    size_t first = 0;
    M.add_polygon(Points(base.rbegin(), base.rend()), color);
    detail::fan(M, base, apex, color);
    detail::weld(M, 1e-9);
    detail::make_outward(M, first);
    detail::current().extend(M);
}

inline void prism(const Profile& profile, double height, const Color& color, const Point& center, const Point& axis) {
    detail::Frame fr = detail::frame(axis);
    const Point &u = fr.u, &v = fr.v, &w = fr.w;
    Point half = detail::scale(w, height / 2.0);
    Points bottom, top;
    for (const Point2& p : profile) {
        Point q{center[0] + u[0] * p[0] + v[0] * p[1],
                center[1] + u[1] * p[0] + v[1] * p[1],
                center[2] + u[2] * p[0] + v[2] * p[1]};
        bottom.push_back(detail::sub(q, half));
        top.push_back(detail::add3(q, half));
    }
    Mesh M;
    detail::add_grid(M, {bottom, top}, color, false, true, true);
    M.add_polygon(Points(bottom.rbegin(), bottom.rend()), color);
    M.add_polygon(top, color);
    detail::weld(M, 1e-9);
    detail::make_outward(M, 0);
    detail::current().extend(M);
}

// -- the five regular polyhedra (Platonic solids) ----------------------------------

inline void polyhedron(const std::string& name, const Point& center, double r, const Color& color) {
    std::pair<Points, std::vector<Face>> VF = detail::platonic(name);
    const Points& V = VF.first;
    double scale = r / detail::norm(V[0]);
    Mesh& S = detail::current();
    int base = (int)S.V.size();
    for (const Point& p : V)
        S.add_vertex({center[0] + p[0] * scale, center[1] + p[1] * scale, center[2] + p[2] * scale});
    size_t first = S.F.size();
    for (const Face& f : VF.second) {
        Face g;
        for (int i : f) g.push_back(base + i);
        S.add_face(g, color);
    }
    detail::make_outward(S, first);
}

inline void tetrahedron(const Point& center, double r, const Color& color) {
    polyhedron("tetrahedron", center, r, color);
}

inline void octahedron(const Point& center, double r, const Color& color) {
    polyhedron("octahedron", center, r, color);
}

inline void dodecahedron(const Point& center, double r, const Color& color) {
    polyhedron("dodecahedron", center, r, color);
}

inline void icosahedron(const Point& center, double r, const Color& color) {
    polyhedron("icosahedron", center, r, color);
}

inline Points polyhedron_points(const std::string& name, const Point& center, double r) {
    std::pair<Points, std::vector<Face>> VF = detail::platonic(name);
    double scale = r / detail::norm(VF.first[0]);
    Points out;
    for (const Point& p : VF.first)
        out.push_back({center[0] + p[0] * scale, center[1] + p[1] * scale, center[2] + p[2] * scale});
    return out;
}

inline std::vector<Face> polyhedron_faces(const std::string& name) { return detail::platonic(name).second; }

}  // namespace add

namespace add {

inline double lerp(double a, double b, double t) { return a + (b - a) * t; }
inline Point lerp(const Point& a, const Point& b, double t) {
    return {a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t};
}
inline Point2 lerp(const Point2& a, const Point2& b, double t) {
    return {a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t};
}
inline Color lerp(const Color& a, const Color& b, double t) {
    double r = a.r + (b.r - a.r) * t, g = a.g + (b.g - a.g) * t, bl = a.b + (b.b - a.b) * t;
    return Color(r, g, bl);                                    // (floats, read by rgb(): 0..1 ones are scaled)
}

inline double clamp(double x, double lo, double hi) { return x < lo ? lo : (x > hi ? hi : x); }

inline double remap(double x, double a0, double a1, double b0, double b1) {
    if (std::fabs(a1 - a0) < EPS) return b0;
    return b0 + (b1 - b0) * (x - a0) / (a1 - a0);
}

inline double distance(const Point& a, const Point& b) {
    double s = 0.0;                                            // (Python: sum of the squares, in order)
    for (int i = 0; i < 3; ++i) s += detail::py_pow(a[i] - b[i], 2);
    return std::sqrt(s);
}
inline double distance(const Point2& a, const Point2& b) {
    double s = 0.0;
    for (int i = 0; i < 2; ++i) s += detail::py_pow(a[i] - b[i], 2);
    return std::sqrt(s);
}

inline Point midpoint(const Point& a, const Point& b) {
    return {(a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0, (a[2] + b[2]) / 2.0};
}
inline Point2 midpoint(const Point2& a, const Point2& b) { return {(a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0}; }

inline Point direction(const Point& a, const Point& b) {
    Point d{b[0] - a[0], b[1] - a[1], b[2] - a[2]};
    double s = 0.0;
    for (int i = 0; i < 3; ++i) s += d[i] * d[i];
    double n = std::sqrt(s);
    if (n < EPS) return d;
    return {d[0] / n, d[1] / n, d[2] / n};
}

inline Point rotate_point(const Point& p, const Point& axis, double angle, const Point& P) {
    Point k = detail::unit(axis);
    double cs = std::cos(angle), sn = std::sin(angle);
    Point v = detail::sub(p, P);
    Point kv = cross(k, v);
    double d = dot(k, v) * (1.0 - cs);
    return {P[0] + v[0] * cs + kv[0] * sn + k[0] * d,
            P[1] + v[1] * cs + kv[1] * sn + k[1] * d,
            P[2] + v[2] * cs + kv[2] * sn + k[2] * d};
}

inline Color shade(const Color& color, double factor) {
    int r = color.r, g = color.g, b = color.b;
    if (factor <= 1.0) return Color((int)(r * factor), (int)(g * factor), (int)(b * factor));
    double t = std::min(1.0, factor - 1.0);
    return Color((int)(r + (255 - r) * t), (int)(g + (255 - g) * t), (int)(b + (255 - b) * t));
}

template <class P_>
inline std::vector<P_> chaikin_(const std::vector<P_>& points, int rounds, bool closed, int dim) {
    std::vector<P_> pts = points;
    if (!closed && pts.empty() && rounds > 0) throw std::out_of_range("list index out of range");   // (as Python)
    for (int round = 0; round < rounds; ++round) {
        size_t n = pts.size();
        std::vector<P_> out;
        size_t pairs = closed ? n : (n > 0 ? n - 1 : 0);
        if (!closed && n > 0) out.push_back(pts[0]);
        for (size_t i = 0; i < pairs; ++i) {
            const P_& a = pts[i];
            const P_& b = pts[(i + 1) % n];
            P_ p, q;
            for (int j = 0; j < dim; ++j) {
                p[j] = a[j] * 0.75 + b[j] * 0.25;
                q[j] = a[j] * 0.25 + b[j] * 0.75;
            }
            out.push_back(p);
            out.push_back(q);
        }
        if (!closed && n > 0) out.push_back(pts[n - 1]);
        pts = out;
    }
    return pts;
}
inline Points chaikin(const Points& points, int rounds, bool closed) { return chaikin_(points, rounds, closed, 3); }
inline Profile chaikin(const Profile& points, int rounds, bool closed) { return chaikin_(points, rounds, closed, 2); }

inline Profile profile_circle(double r, int k, double phase) {
    Profile out;
    for (int i = 0; i < k; ++i)
        out.push_back({r * std::cos(phase + 2 * pi * i / k), r * std::sin(phase + 2 * pi * i / k)});
    return out;
}

inline Profile profile_ellipse(double a, double b, int k) {
    Profile out;
    for (int i = 0; i < k; ++i) out.push_back({a * std::cos(2 * pi * i / k), b * std::sin(2 * pi * i / k)});
    return out;
}

inline Profile profile_polygon(int n, double r, std::optional<double> phase) {
    double ph = phase ? *phase : -pi / 2.0 + pi / n;
    return profile_circle(r, n, ph);
}

inline Profile profile_star(int n, double r_outer, double r_inner, std::optional<double> phase) {
    double ph = phase ? *phase : pi / 2.0;
    Profile pts;
    for (int i = 0; i < 2 * n; ++i) {
        double r = i % 2 == 0 ? r_outer : r_inner;
        double a = ph + pi * i / n;
        pts.push_back({r * std::cos(a), r * std::sin(a)});
    }
    return pts;
}

inline Profile profile_rect(double w, double h, double r, int k) {
    double x = w / 2.0, y = h / 2.0;
    if (r <= EPS) return {{-x, -y}, {x, -y}, {x, y}, {-x, y}};
    if (x < r) r = x;                                          // r = min(r, x, y) (the first of equals)
    if (y < r) r = y;
    Profile pts;
    const double corners[4][3] = {{x - r, y - r, 0.0}, {-x + r, y - r, pi / 2},
                                  {-x + r, -y + r, pi}, {x - r, -y + r, 3 * pi / 2}};
    for (const auto& c : corners) {
        double cx = c[0], cy = c[1], a0 = c[2];
        for (int i = 0; i < k + 1; ++i) {
            double a = a0 + (pi / 2) * i / k;
            pts.push_back({cx + r * std::cos(a), cy + r * std::sin(a)});
        }
    }
    return pts;
}

inline Profile profile_gear(int teeth, double r, std::optional<double> depth, int /*k: not used (as in add.py)*/) {
    double dp = depth ? *depth : r * 0.2;
    Profile pts;
    int n = 4 * teeth;
    for (int i = 0; i < n; ++i) {
        int phase = i % 4;
        double a = 2 * pi * i / n;
        double rr = (phase == 1 || phase == 2) ? r + dp / 2.0 : r - dp / 2.0;
        pts.push_back({rr * std::cos(a), rr * std::sin(a)});
    }
    return pts;
}

inline Points points_on_line(const Point& a, const Point& b, int n) {
    if (n <= 1) return {a};
    Points out;
    for (int i = 0; i < n; ++i) out.push_back(lerp(a, b, i / (double)(n - 1)));
    return out;
}

inline Points points_on_circle(const Point& center, double r, int n, const Point& axis, double phase) {
    detail::Frame fr = detail::frame(axis);
    return detail::ring(center, fr.u, fr.v, r, n, phase);
}

inline Points points_on_helix(const Point& center, double r, double pitch, double turns, int n, const Point& axis) {
    detail::Frame fr = detail::frame(axis);
    const Point &u = fr.u, &v = fr.v, &w = fr.w;
    Points out;
    for (int i = 0; i < n; ++i) {
        double t = turns * i / (double)std::max(1, n - 1);
        double a = 2 * pi * t;
        Point p;
        for (int j = 0; j < 3; ++j)
            p[j] = center[j] + (u[j] * std::cos(a) + v[j] * std::sin(a)) * r + w[j] * pitch * t;
        out.push_back(p);
    }
    return out;
}

inline Points points_on_spiral(const Point& center, double r0, double r1, double turns, int n, const Point& axis,
                               double rise) {
    detail::Frame fr = detail::frame(axis);
    const Point &u = fr.u, &v = fr.v, &w = fr.w;
    Points out;
    for (int i = 0; i < n; ++i) {
        double t = i / (double)std::max(1, n - 1);
        double a = 2 * pi * turns * t;
        double r = r0 + (r1 - r0) * t;
        Point p;
        for (int j = 0; j < 3; ++j)
            p[j] = center[j] + (u[j] * std::cos(a) + v[j] * std::sin(a)) * r + w[j] * rise * t;
        out.push_back(p);
    }
    return out;
}

inline Points points_on_curve(const std::function<Point(double)>& path, double t0, double t1, int n, bool closed) {
    int steps = closed ? n : std::max(1, n - 1);
    Points out;
    for (int i = 0; i < n; ++i) out.push_back(path(t0 + (t1 - t0) * i / (double)steps));
    return out;
}

}  // namespace add

namespace add {

namespace detail {

inline std::pair<std::vector<Points>, bool> revolve_grid(const Point& A, const Point& direction,
                                                         const Profile& profile, int k, double angle, double phase) {
    Frame fr = frame(direction);
    const Point &u = fr.u, &v = fr.v, &w = fr.w;
    bool closed = std::fabs(angle - 2.0 * pi) < 1e-12;
    int steps = closed ? k : k + 1;
    std::vector<std::pair<double, double>> cs;
    for (int j = 0; j < steps; ++j) {
        double a = phase + angle * (j / (double)k);
        cs.push_back({std::cos(a), std::sin(a)});
    }
    std::vector<Points> P;
    for (const Point2& rh : profile) {
        double r = rh[0], h = rh[1];
        Point centre = add3(A, scale(w, h));
        Points row;
        for (const std::pair<double, double>& q : cs) {
            double c = q.first, s = q.second;
            row.push_back({centre[0] + u[0] * r * c + v[0] * r * s,
                           centre[1] + u[1] * r * c + v[1] * r * s,
                           centre[2] + u[2] * r * c + v[2] * r * s});
        }
        P.push_back(row);
    }
    return {P, closed};
}

inline std::pair<Points, std::vector<Face>> icosphere_grid(int subdivisions) {
    std::pair<Points, std::vector<Face>> VT = platonic("icosahedron");
    Points V;
    for (const Point& p : VT.first) V.push_back(unit(p));
    std::vector<Face> T = VT.second;
    for (int round = 0; round < subdivisions; ++round) {
        std::map<std::pair<int, int>, int> mid;
        auto midpoint_index = [&](int a, int b) {
            std::pair<int, int> key = a < b ? std::make_pair(a, b) : std::make_pair(b, a);
            auto it = mid.find(key);
            if (it != mid.end()) return it->second;
            Point m = unit({(V[a][0] + V[b][0]) * 0.5, (V[a][1] + V[b][1]) * 0.5, (V[a][2] + V[b][2]) * 0.5});
            int made = (int)V.size();
            mid[key] = made;
            V.push_back(m);
            return made;
        };
        std::vector<Face> next;
        for (const Face& f : T) {
            int a = f[0], b = f[1], c = f[2];
            int ab = midpoint_index(a, b);
            int bc = midpoint_index(b, c);
            int ca = midpoint_index(c, a);
            next.push_back({a, ab, ca});
            next.push_back({b, bc, ab});
            next.push_back({c, ca, bc});
            next.push_back({ab, bc, ca});
        }
        T = next;
    }
    return {V, T};
}

inline Mesh tube_body(const Point& A, const Point& B, double r1, double r2, int k, const Color& color, bool cap_a,
                      bool cap_b) {
    Point d = sub(B, A);
    if (norm(d) < EPS) return Mesh();
    Frame fr = frame(d);
    Mesh M;
    Points ring_a = ring(A, fr.u, fr.v, r1, k);
    Points ring_b = ring(B, fr.u, fr.v, r2, k);
    if (r1 < EPS)                                              // cone standing on its point
        fan(M, ring_b, A, color, true);
    else if (r2 < EPS)                                         // cone with the point at B
        fan(M, ring_a, B, color);
    else
        add_grid(M, {ring_a, ring_b}, color, false, true, true);
    if (cap_a && r1 >= EPS) fan(M, ring_a, A, color, true);
    if (cap_b && r2 >= EPS) fan(M, ring_b, B, color);
    detail::weld(M, 1e-9);
    return M;
}

}  // namespace detail

// -- revolve -----------------------------------------------------------------------

inline void revolve(const std::function<Point2(double)>& profile, const Point& A, const Point& B, double t0,
                    double t1, int steps, int k, const ColorOf<double, double>& color, double angle, bool caps) {
    if (steps == 0)
        throw std::domain_error("float division by zero");      // (as Python: ZeroDivisionError)
    Profile pts;
    for (int i = 0; i < steps + 1; ++i) {
        double t = t0 + (t1 - t0) * i / (double)steps;
        Point2 g = profile(t);
        pts.push_back({g[0], g[1]});
    }
    Point direction = detail::sub(B, A);
    std::pair<std::vector<Points>, bool> grid_ = detail::revolve_grid(A, direction, pts, k, angle);
    const std::vector<Points>& P = grid_.first;
    bool closed = grid_.second;
    detail::CellPaint cells = color.color;
    ColorOf<int> lid_a = color.color, lid_b = color.color;
    Color side_a = color.color, side_b = color.color;
    if (color.callable()) {                                    // cell (i, j) -> (t, angle), at its middle
        cells = detail::CellPaint([&](int i, int j) {
            double t = t0 + (t1 - t0) * (i + 0.5) / (double)steps;
            return color(t, angle * (j + 0.5) / (double)k);
        });
        lid_a = ColorOf<int>([&](int j) { return color(t0, angle * (j + 0.5) / (double)k); });
        lid_b = ColorOf<int>([&](int j) { return color(t1, angle * (j + 0.5) / (double)k); });
        side_a = color((t0 + t1) / 2.0, 0.0);
        side_b = color((t0 + t1) / 2.0, angle);
    }
    Mesh M;
    detail::add_grid(M, P, cells, false, closed, true);
    if (caps) {
        Point w = detail::unit(direction);
        Point first = detail::add3(A, detail::scale(w, pts[0][1]));
        Point last = detail::add3(A, detail::scale(w, pts.back()[1]));
        if (pts[0][0] > EPS)                                   // flat lid at the start
            detail::fan(M, P[0], first, lid_a, true, closed);
        if (pts.back()[0] > EPS)                               // flat lid at the end
            detail::fan(M, P.back(), last, lid_b, false, closed);
        if (!closed) {                                         // the two sides of the wedge
            Points side;                                       // (at(): add.py's row[0] fails on k < 0)
            for (const Points& row : P) side.push_back(row.at(0));
            side.push_back(last);
            side.push_back(first);
            M.add_polygon(side, side_a);
            side.clear();
            for (const Points& row : P) side.push_back(row.at(row.size() - 1));
            side.push_back(last);
            side.push_back(first);
            M.add_polygon(side, side_b);
        }
        detail::weld(M, 1e-9);
        detail::drop_degenerate(M);
        if (!closed) M = fix_normals(M);
        detail::make_outward(M, 0);                            // whichever way the profile was drawn
    }
    detail::emit(M);
}

inline void revolve(const Profile& profile, const Point& A, const Point& B, double t0, double t1,
                    int /*steps: the list's own*/, int k, const ColorOf<double, double>& color, double angle,
                    bool caps) {
    // The list as the function add.py samples: its i-th call gives point i.
    size_t next = 0;
    std::function<Point2(double)> sample = [&](double) { return profile.at(next++); };
    revolve(sample, A, B, t0, t1, (int)profile.size() - 1, k, color, angle, caps);
}

inline void spin3D(const Point& A, const Point& B, const std::function<Point2(double)>& S, double min_t, double max_t,
                   int grid_t, int k, const Color& RGB) {
    revolve(S, A, B, min_t, max_t, grid_t, k, RGB, 2.0 * pi, false);
}

// -- spheres -------------------------------------------------------------------------

inline void icosphere(const Point& center, double r, int subdivisions, const ColorOf<Point>& color) {
    int level = subdivisions;
    level = level < 0 ? 0 : (level > 7 ? 7 : level);
    std::pair<Points, std::vector<Face>> VT = detail::icosphere_grid(level);
    const Points& V = VT.first;
    Mesh M;
    for (const Point& p : V) M.add_vertex({center[0] + p[0] * r, center[1] + p[1] * r, center[2] + p[2] * r});
    if (color.callable()) {
        for (const Face& f : VT.second) {
            int a = f[0], b = f[1], c = f[2];
            Point d = detail::unit({V[a][0] + V[b][0] + V[c][0], V[a][1] + V[b][1] + V[c][1],
                                    V[a][2] + V[b][2] + V[c][2]});
            M.add_face({a, b, c}, color(d));
        }
    } else {
        for (const Face& f : VT.second) M.add_face(f, color.color);
    }
    detail::current().extend(M);
}

inline void sphere(const Point& center, double r, int k, const ColorOf<Point>& color,
                   std::optional<int> subdivisions) {
    int level;
    if (!subdivisions) {
        k = std::max(1, k);
        // Python's math.log(x, 2) is log(x) / log(2), and round() rounds half to even.
        level = k > 1 ? (int)std::nearbyint(std::log(2.0 * k / 3.0) / std::log(2.0)) : 0;
    } else {
        level = *subdivisions;
    }
    icosphere(center, r, level, color);
}

inline void quadsphere(const Point& center, double r, int k, const Color& color) {
    ellipsoid(center, {r, r, r}, k, color);
}

inline void ellipsoid(const Point& center, const Point& radii, int k, const Color& color) {
    static const int sides[6][3][3] = {{{1, 0, 0}, {0, 1, 0}, {0, 0, 1}},
                                       {{-1, 0, 0}, {0, 0, 1}, {0, 1, 0}},
                                       {{0, 1, 0}, {0, 0, 1}, {1, 0, 0}},
                                       {{0, -1, 0}, {1, 0, 0}, {0, 0, 1}},
                                       {{0, 0, 1}, {1, 0, 0}, {0, 1, 0}},
                                       {{0, 0, -1}, {0, 1, 0}, {1, 0, 0}}};
    // Spreading the samples with tan() keeps the cells the same size.
    std::vector<double> warp;
    for (int i = 0; i < k + 1; ++i) warp.push_back(std::tan(pi / 4.0 * (2.0 * i / k - 1.0)));
    Mesh M;
    for (const auto& side : sides) {
        const int *n = side[0], *u = side[1], *v = side[2];
        std::vector<Points> P;
        for (double a : warp) {
            Points row;
            for (double b : warp) {
                Point p = detail::unit({n[0] + u[0] * a + v[0] * b,
                                        n[1] + u[1] * a + v[1] * b,
                                        n[2] + u[2] * a + v[2] * b});
                row.push_back({center[0] + p[0] * radii[0], center[1] + p[1] * radii[1], center[2] + p[2] * radii[2]});
            }
            P.push_back(row);
        }
        detail::add_grid(M, P, color);
    }
    detail::weld(M, 1e-9);
    detail::current().extend(M);
}

inline void uvsphere(const Point& center, double r, int nu, int nv, const Color& color) {
    Profile profile;
    for (int i = 0; i < nv + 1; ++i) profile.push_back({r * std::sin(pi * i / nv), r - r * std::cos(pi * i / nv)});
    std::vector<Points> P = detail::revolve_grid({center[0], center[1] - r, center[2]}, {0, 1, 0}, profile, nu).first;
    Mesh M;
    detail::add_grid(M, P, color, false, true, true);
    detail::weld(M, 1e-9);
    detail::drop_degenerate(M);
    detail::current().extend(M);
}

inline void torus(const Point& center, double R, double r, int nu, int nv, const Color& color, const Point& axis) {
    detail::Frame fr = detail::frame(axis);
    const Point &u = fr.u, &v = fr.v, &w = fr.w;
    std::vector<Points> P;
    for (int i = 0; i < nu; ++i) {
        double a = 2.0 * pi * i / nu;
        Point ring_centre{center[0] + (u[0] * std::cos(a) + v[0] * std::sin(a)) * R,
                          center[1] + (u[1] * std::cos(a) + v[1] * std::sin(a)) * R,
                          center[2] + (u[2] * std::cos(a) + v[2] * std::sin(a)) * R};
        Point out{u[0] * std::cos(a) + v[0] * std::sin(a),
                  u[1] * std::cos(a) + v[1] * std::sin(a),
                  u[2] * std::cos(a) + v[2] * std::sin(a)};
        Points row;
        for (int j = 0; j < nv; ++j) {
            double b = 2.0 * pi * j / nv;
            double cb = std::cos(b) * r, sb = std::sin(b) * r;
            row.push_back({ring_centre[0] + out[0] * cb + w[0] * sb,
                           ring_centre[1] + out[1] * cb + w[1] * sb,
                           ring_centre[2] + out[2] * cb + w[2] * sb});
        }
        P.push_back(row);
    }
    Mesh M;
    detail::add_grid(M, P, color, true, true);
    detail::make_outward(M, 0);
    detail::current().extend(M);
}

// -- cylinders, cones and friends ------------------------------------------------------

inline void cylinder(const Point& A, const Point& B, double r, int k, const Color& color) {
    detail::current().extend(detail::tube_body(A, B, r, r, k, color, true, true));
}

inline void tube(const Point& A, const Point& B, double r, int k, const Color& color) {
    detail::current().extend(detail::tube_body(A, B, r, r, k, color, false, false));
}

inline void cup(const Point& A, const Point& B, double r, int k, const Color& color) {
    detail::current().extend(detail::tube_body(A, B, r, r, k, color, true, false));
}

inline void cone(const Point& A, const Point& B, double r, int k, const Color& color) {
    detail::current().extend(detail::tube_body(A, B, r, 0.0, k, color, true, false));
}

inline void cone_open(const Point& A, const Point& B, double r, int k, const Color& color) {
    detail::current().extend(detail::tube_body(A, B, r, 0.0, k, color, false, false));
}

inline void frustum(const Point& A, const Point& B, double r1, double r2, int k, const Color& color, bool caps) {
    detail::current().extend(detail::tube_body(A, B, r1, r2, k, color, caps, caps));
}

inline void pipe(const Point& A, const Point& B, double r_outer, double r_inner, int k, const Color& color) {
    Point d = detail::sub(B, A);
    detail::Frame fr = detail::frame(d);
    Mesh M;
    Points oa = detail::ring(A, fr.u, fr.v, r_outer, k), ob = detail::ring(B, fr.u, fr.v, r_outer, k);
    Points ia = detail::ring(A, fr.u, fr.v, r_inner, k), ib = detail::ring(B, fr.u, fr.v, r_inner, k);
    detail::add_grid(M, {oa, ob}, color, false, true, true);  // outside
    detail::add_grid(M, {ia, ib}, color, false, true);        // inside
    detail::add_grid(M, {ia, oa}, color, false, true, true);  // ring at A
    detail::add_grid(M, {ib, ob}, color, false, true);        // ring at B
    detail::emit(M);
}

inline void capsule(const Point& A, const Point& B, double r, int k, const Color& color) {
    Point d = detail::sub(B, A);
    double length = detail::norm(d);
    int n = std::max(3, k / 3);                                // (k // 3: the same for k >= 0, and 3 below that)
    Profile profile;
    for (int i = 0; i < n + 1; ++i) {                          // lower hemisphere
        double a = pi / 2 * i / n;
        profile.push_back({r * std::sin(a), r - r * std::cos(a)});
    }
    for (int i = 0; i < n + 1; ++i) {                          // upper hemisphere
        double a = pi / 2 * i / n;
        profile.push_back({r * std::cos(a), r + length + r * std::sin(a)});
    }
    Point start = detail::add3(A, detail::scale(detail::unit(d), -r));
    std::vector<Points> P = detail::revolve_grid(start, d, profile, k).first;
    Mesh M;
    detail::add_grid(M, P, color, false, true, true);
    detail::weld(M, 1e-9);
    detail::drop_degenerate(M);
    detail::make_outward(M, 0);
    detail::current().extend(M);
}

inline void arrow(const Point& A, const Point& B, double r, const Color& color, int k, double head) {
    Point d = detail::sub(B, A);
    double n = detail::norm(d);
    if (n < EPS) return;
    Point joint = detail::add3(A, detail::scale(d, 1.0 - head));
    cylinder(A, joint, r, k, color);
    cone(joint, B, r * 2.4, k, color);
}

inline void helix(const Point& center, double r, double pitch, double turns, int k, double thickness, int sides,
                  const Color& color, const Point& axis) {
    detail::Frame fr = detail::frame(axis);
    const Point &u = fr.u, &v = fr.v, &w = fr.w;
    auto path = [&](double t) {
        double a = 2.0 * pi * t;
        return Point{center[0] + (u[0] * std::cos(a) + v[0] * std::sin(a)) * r + w[0] * pitch * t,
                     center[1] + (u[1] * std::cos(a) + v[1] * std::sin(a)) * r + w[1] * pitch * t,
                     center[2] + (u[2] * std::cos(a) + v[2] * std::sin(a)) * r + w[2] * pitch * t};
    };
    curve(path, 0, turns, k, sides, thickness, color, false);
}

// -- coordinate axes ---------------------------------------------------------------------

inline void axes(const Point& C, double length, double width) {
    double h = length, w = width;
    const Point directions[3] = {{1, 0, 0}, {0, 1, 0}, {0, 0, 1}};
    const Color cols[3] = {Color(255, 0, 0), Color(0, 255, 0), Color(0, 0, 255)};
    for (int q = 0; q < 3; ++q) {
        Point end = detail::add3(C, detail::scale(directions[q], h));
        Point tip = detail::add3(C, detail::scale(directions[q], h + 0.7));
        cylinder(C, end, w, 9, cols[q]);
        cone(end, tip, 2 * w, 9, cols[q]);
    }
    // All three labels stand in the XY plane so they read the same way round.
    glyph("X", detail::add3(C, {h + 0.35, 0.25, 0}), {1, 0, 0}, {0, 1, 0}, 0.6, 3 * w, Color(255, 0, 0));
    glyph("Y", detail::add3(C, {0.3, h + 0.35, 0}), {1, 0, 0}, {0, 1, 0}, 0.6, 3 * w, Color(0, 255, 0));
    glyph("Z", detail::add3(C, {0.1, 0.25, h + 0.5}), {1, 0, 0}, {0, 1, 0}, 0.6, 3 * w, Color(0, 0, 255));
}

}  // namespace add

namespace add {

namespace detail {

inline Mesh local_mesh(const Mesh& M, const Point& origin, const Point& w, const Point& up, const Point& side) {
    return mapped(M, [&](const Point& p) {
        return Point{origin[0] + w[0] * p[0] + up[0] * p[1] + side[0] * p[2],
                     origin[1] + w[1] * p[0] + up[1] * p[1] + side[1] * p[2],
                     origin[2] + w[2] * p[0] + up[2] * p[1] + side[2] * p[2]};
    });
}

inline std::array<Point, 3> ground_frame(const Point& direction, const Point& up_) {
    Point w = unit(direction);
    Point up = unit(up_);
    Point side = cross(w, up);
    if (norm(side) < EPS) {                                    // direction was straight up
        side = perp(w);
        up = cross(side, w);
    }
    side = unit(side);
    return {w, up, side};
}

inline Mesh hollow_prism(const Profile& outer, const Profile& inner, double height, const Color& color,
                         const Point& center, const Point& axis) {
    Frame fr = frame(axis);
    const Point &u = fr.u, &v = fr.v, &w = fr.w;
    Point half = scale(w, height / 2.0);
    auto lift = [&](const Profile& profile, int sign) {
        Points out;
        for (const Point2& p : profile) {
            Point q{center[0] + u[0] * p[0] + v[0] * p[1],
                    center[1] + u[1] * p[0] + v[1] * p[1],
                    center[2] + u[2] * p[0] + v[2] * p[1]};
            out.push_back(add3(q, scale(half, sign)));
        }
        return out;
    };
    Points ob = lift(outer, -1), ot = lift(outer, 1), ib = lift(inner, -1), it = lift(inner, 1);
    Mesh M;
    add_grid(M, {ob, ot}, color, false, true, true);           // outside wall
    add_grid(M, {ib, it}, color, false, true);                 // inside wall
    add_grid(M, {it, ot}, color, false, true, true);           // top ring
    add_grid(M, {ib, ob}, color, false, true);                 // bottom ring
    detail::weld(M, 1e-9);
    make_outward(M, 0);
    return M;
}

inline Mesh tube_along(const Points& points, const std::vector<double>& radii, int k, const CellPaint& color,
                       bool closed, const ColorOf<int>* cap_a, const ColorOf<int>* cap_b) {
    auto frames = rmf(points, closed);
    const Points& tangents = frames.first;
    const Points& normals = frames.second;
    std::vector<Point2> ring_;
    for (int j = 0; j < k; ++j) ring_.push_back({std::cos(2 * pi * j / k), std::sin(2 * pi * j / k)});
    std::vector<Points> P;
    for (size_t i = 0; i < points.size(); ++i) {
        Point u = normals[i];
        Point v = cross(tangents[i], u);
        const Point& c = points[i];
        double rad = radii[i];
        Points row;
        for (const Point2& q : ring_) {
            double x = q[0] * rad, y = q[1] * rad;
            row.push_back({c[0] + u[0] * x + v[0] * y, c[1] + u[1] * x + v[1] * y, c[2] + u[2] * x + v[2] * y});
        }
        P.push_back(row);
    }
    Mesh M;
    add_grid(M, P, color, closed, true, true);
    if (!closed) {
        // add.py: the caps take ``color`` itself unless a cap colour is given (a
        // function colour is then called with the cell index j only)
        ColorOf<int> ca = cap_a ? *cap_a : (color.callable() ? ColorOf<int>([&color](int j) { return color(0, j); })
                                                             : ColorOf<int>(color.color));
        ColorOf<int> cb = cap_b ? *cap_b : (color.callable() ? ColorOf<int>([&color](int j) { return color(0, j); })
                                                             : ColorOf<int>(color.color));
        fan(M, P[0], points[0], ca, true);
        fan(M, P.back(), points.back(), cb);
    }
    return M;
}

inline void arch_loft(const Point& A, const Point& B, double height, const Profile& profile, const Color& color,
                      int steps, const Point& up) {
    Point mid = midpoint(A, B);
    Point half = sub(A, mid);
    Point lift = scale(unit(up), height);
    Point N = unit(cross(half, lift));                         // normal of the arch's plane
    std::vector<Points> sections;
    for (int i = 0; i < steps + 1; ++i) {
        if (steps == 0) throw std::domain_error("float division by zero");
        double t = pi * i / (double)steps;
        Point c = add3(mid, add3(scale(half, std::cos(t)), scale(lift, std::sin(t))));
        Point T = unit(add3(scale(half, -std::sin(t)), scale(lift, std::cos(t))));
        Point R = cross(T, N);                                 // points outward from the arch
        Points section;
        for (const Point2& ab : profile) {
            double a = ab[0], b = ab[1];
            section.push_back({c[0] + N[0] * a + R[0] * b, c[1] + N[1] * a + R[1] * b, c[2] + N[2] * a + R[2] * b});
        }
        sections.push_back(section);
    }
    loft(sections, color);
}

inline std::vector<std::string> pixel_cells(const std::string& row) {
    std::vector<std::string> out;
    for (char ch : row) {
        if (out.empty() || ((unsigned char)ch & 0xC0) != 0x80) out.emplace_back();
        out.back() += ch;
    }
    return out;
}

inline std::vector<long long> py_set_iteration_order(const std::vector<long long>& added) {
    struct Slot {
        bool full = false;
        long long key = 0;
        size_t hash = 0;
    };
    std::vector<Slot> table(8);
    size_t mask = 7, fill = 0, used = 0;
    auto insert_clean = [&](long long key, size_t hash) {  // (set_insert_clean: a key that is not there yet)
        size_t perturb = hash;
        size_t i = hash & mask;
        while (true) {
            if (!table[i].full) {
                table[i] = {true, key, hash};
                return;
            }
            if (i + 9 <= mask)
                for (size_t j = 1; j <= 9; ++j)
                    if (!table[i + j].full) {
                        table[i + j] = {true, key, hash};
                        return;
                    }
            perturb >>= 5;
            i = (i * 5 + 1 + perturb) & mask;
        }
    };
    for (long long x : added) {
        size_t hash = (size_t)(x == -1 ? -2 : x);             // (the hash of an int that fits in 61 bits)
        size_t perturb = hash;
        size_t i = hash & mask;
        bool done = false;
        while (!done) {
            size_t probes = i + 9 <= mask ? 9 : 0;
            for (size_t o = 0; o <= probes; ++o) {
                Slot& s = table[i + o];
                if (!s.full) {                                 // a new key
                    s = {true, x, hash};
                    ++fill;
                    ++used;
                    if (!(fill * 5 < mask * 3)) {              // set_table_resize: all again, in slot order
                        size_t newsize = 8;
                        size_t minused = used > 50000 ? used * 2 : used * 4;
                        while (newsize <= minused) newsize <<= 1;
                        std::vector<Slot> old(newsize);
                        old.swap(table);
                        mask = newsize - 1;
                        for (const Slot& e : old)
                            if (e.full) insert_clean(e.key, e.hash);
                    }
                    done = true;
                    break;
                }
                if (s.hash == hash && s.key == x) {            // already there
                    done = true;
                    break;
                }
            }
            if (done) break;
            perturb >>= 5;
            i = (i * 5 + 1 + perturb) & mask;
        }
    }
    std::vector<long long> out;
    for (const Slot& s : table)
        if (s.full) out.push_back(s.key);
    return out;
}

}  // namespace detail

// -- beams, boxes, arches and stairs -------------------------------------------------------

inline void beam(const Point& A, const Point& B, double width, std::optional<double> height, const Color& color,
                 const Point& up) {
    double h = height ? *height : width;
    std::array<Point, 3> frame_ = detail::ground_frame(detail::sub(B, A), up);
    const Point &v = frame_[1], &u = frame_[2];               // (frame_[0] runs along, v up, u sideways)
    double hw = width / 2.0, hh = h / 2.0;
    Points corners;
    for (const Point* end : {&A, &B})
        for (int sv : {-1, 1})
            for (int su : {-1, 1})
                corners.push_back({(*end)[0] + u[0] * su * hw + v[0] * sv * hh,
                                   (*end)[1] + u[1] * su * hw + v[1] * sv * hh,
                                   (*end)[2] + u[2] * su * hw + v[2] * sv * hh});
    // corner index = 4 * (end) + 2 * (v side) + (u side)
    const int F[6][4] = {{0, 1, 3, 2}, {4, 6, 7, 5}, {0, 4, 5, 1}, {2, 3, 7, 6}, {0, 2, 6, 4}, {1, 5, 7, 3}};
    Mesh M;
    for (const Point& p : corners) M.add_vertex(p);
    for (const auto& f : F) M.add_face({f[0], f[1], f[2], f[3]}, color);
    detail::make_outward(M, 0);
    detail::current().extend(M);
}

inline void beam(const Point& A, const Point& B, double width, const Color& color, const Point& up) {
    beam(A, B, width, std::nullopt, color, up);
}

inline void rounded_box(const Point& center, const Point& sizes, double r_, int k, const Color& color) {
    double r = r_;                                             // min(r, sizes[0] / 2.0, ...): the first of equals
    for (int a = 0; a < 3; ++a)
        if (sizes[a] / 2.0 < r) r = sizes[a] / 2.0;
    double inner[3];
    for (int a = 0; a < 3; ++a) inner[a] = sizes[a] / 2.0 - r;
    static const int sides[6][3][3] = {{{1, 0, 0}, {0, 1, 0}, {0, 0, 1}},
                                       {{-1, 0, 0}, {0, 0, 1}, {0, 1, 0}},
                                       {{0, 1, 0}, {0, 0, 1}, {1, 0, 0}},
                                       {{0, -1, 0}, {1, 0, 0}, {0, 0, 1}},
                                       {{0, 0, 1}, {1, 0, 0}, {0, 1, 0}},
                                       {{0, 0, -1}, {0, 1, 0}, {1, 0, 0}}};
    std::vector<double> warp;
    for (int i = 0; i < k + 1; ++i) {
        if (k == 0) throw std::domain_error("float division by zero");
        warp.push_back(std::tan(pi / 4.0 * (2.0 * i / k - 1.0)));
    }
    Mesh M;
    for (const auto& side : sides) {
        const int *n = side[0], *u = side[1], *v = side[2];
        std::vector<Points> P;
        for (double a : warp) {
            Points row;
            for (double b : warp) {
                Point p = detail::unit({n[0] + u[0] * a + v[0] * b,
                                        n[1] + u[1] * a + v[1] * b,
                                        n[2] + u[2] * a + v[2] * b});
                Point q;
                for (int axis = 0; axis < 3; ++axis) {
                    double sign = std::fabs(p[axis]) < 1e-12 ? 0.0 : (p[axis] > 0 ? 1.0 : -1.0);
                    q[axis] = center[axis] + sign * inner[axis] + p[axis] * r;
                }
                row.push_back(q);
            }
            P.push_back(row);
        }
        detail::add_grid(M, P, color);
    }
    detail::weld(M, 1e-9);
    detail::drop_degenerate(M);
    detail::current().extend(M);
}

inline void rounded_box(const Point& center, double size, double r, int k, const Color& color) {
    rounded_box(center, Point{size, size, size}, r, k, color);
}

inline void hemisphere(const Point& center, double r, int k, const ColorOf<double, double>& color,
                       const Point& axis) {
    std::function<Point2(double)> profile = [r](double t) { return Point2{r * std::sin(t), r * std::cos(t)}; };
    revolve(profile, center, detail::add3(center, axis), 0.0, pi / 2.0, k, 4 * k, color);
}

inline void arch(const Point& A, const Point& B, double height, double thickness, const Color& color, int steps,
                 int k, const Point& up) {
    detail::arch_loft(A, B, height, profile_circle(thickness, k), color, steps, up);
}

inline void arch(const Point& A, const Point& B, double height, const Point2& thickness, const Color& color,
                 int steps, int /*k: a round bar's*/, const Point& up) {
    detail::arch_loft(A, B, height, profile_rect(thickness[0], thickness[1]), color, steps, up);
}

inline void stairs(const Point& origin, int n, double width, double rise, double run, const Color& color,
                   const Point& direction) {
    std::array<Point, 3> fr = detail::ground_frame(direction);
    size_t count = n > 0 ? (size_t)n : 0;                     // ([run] * n: nothing for n <= 0)
    Mesh M = detail::grid_solid({0.0, 0.0, -width / 2.0}, std::vector<double>(count, run),
                                std::vector<double>(count, rise), {width},
                                [](int i, int j, int) { return j <= i; }, color);
    detail::current().extend(detail::local_mesh(M, origin, fr[0], fr[1], fr[2]));
}

// -- machine parts and buildings --------------------------------------------------------------

inline void gear(const Point& center, int teeth, double r, double thickness, const Color& color,
                 std::optional<double> depth, double hole, const Point& axis) {
    Profile outer = profile_gear(teeth, r, depth);
    if (hole > EPS) {
        Profile inner = profile_circle(hole, (int)outer.size());
        detail::current().extend(detail::hollow_prism(outer, inner, thickness, color, center, axis));
    } else {
        prism(outer, thickness, color, center, axis);
    }
}

inline void wheel(const Point& center_, double r, double width, const Color& color_, const Point& axis, int k,
                  int spokes, const Color& hub_color_) {
    const Point center = center_;                              // (copies: the scene grows below)
    const Color color = color_, hub_color = hub_color_;
    Point w = detail::unit(axis);
    Point a = detail::add3(center, detail::scale(w, -width / 2.0));
    Point b = detail::add3(center, detail::scale(w, width / 2.0));
    int sides = std::max(8, k / 2);                            // max(8, k // 2): k // 2 < 8 whenever they differ
    if (spokes <= 0) {
        cylinder(a, b, r, k, color);
        cylinder(detail::add3(a, detail::scale(w, -width * 0.15)), detail::add3(b, detail::scale(w, width * 0.15)),
                 r * 0.3, sides, hub_color);
        return;
    }
    double tyre = width / 2.0;
    torus(center, r - tyre, tyre, k, sides, color, axis);
    double hub = std::max(r * 0.2, tyre);
    cylinder(a, b, hub, sides, hub_color);
    detail::Frame fr = detail::frame(w);
    const Point &u = fr.u, &v = fr.v;
    for (int i = 0; i < spokes; ++i) {
        double ang = 2 * pi * i / spokes;
        Point tip{center[0] + (u[0] * std::cos(ang) + v[0] * std::sin(ang)) * (r - tyre),
                  center[1] + (u[1] * std::cos(ang) + v[1] * std::sin(ang)) * (r - tyre),
                  center[2] + (u[2] * std::cos(ang) + v[2] * std::sin(ang)) * (r - tyre)};
        cylinder(center, tip, tyre * 0.3, 8, hub_color);
    }
}

inline void roof(const Point& center, const Point2& size, double height, const Color& color, double overhang) {
    double w = size[0] / 2.0 + overhang;
    Profile profile{{-w, 0.0}, {w, 0.0}, {0.0, height}};
    prism(profile, size[1] + 2 * overhang, color, center, {0, 0, 1});
}

inline void column(const Point& base, double height, double r, const Color& color_, int k, bool plinth) {
    const Color color = color_;                                // (a copy: the scene grows below)
    double x = base[0], y = base[1], z = base[2];
    double slab = 0.3 * r;
    if (plinth) {
        cuboid({x, y + slab / 2.0, z}, {2.6 * r, slab, 2.6 * r}, color);
        cuboid({x, y + height - slab / 2.0, z}, {2.6 * r, slab, 2.6 * r}, color);
        frustum({x, y + slab, z}, {x, y + height - slab, z}, r, 0.85 * r, k, color);
    } else {
        frustum({x, y, z}, {x, y + height, z}, r, 0.85 * r, k, color);
    }
}

inline void bricks(const Point& origin_, double length, double height, const Point& brick,
                   const ColorOf<int, int>& color, const Point& direction, double gap, std::optional<long long> seed) {
    const Point origin = origin_;                              // (a copy: the scene changes below)
    double bl = brick[0], bh = brick[1], bd = brick[2];
    if (bh == 0.0) throw std::domain_error("float division by zero");
    double rows_ = height / bh + 0.5;
    if (std::isnan(rows_)) throw std::invalid_argument("cannot convert float NaN to integer");
    if (std::isinf(rows_)) throw std::overflow_error("cannot convert float infinity to integer");
    long long rows = (long long)rows_;                         // int(): toward zero
    std::optional<Random> rnd;
    if (seed) rnd.emplace(*seed);
    push();                                                    // (as in add.py: not popped if a colour fails)
    for (long long j = 0; j < rows; ++j) {
        double shift = j % 2 == 0 ? 0.0 : bl / 2.0;
        double x = -shift;
        int i = 0;
        while (x < length - EPS) {
            double x0 = std::max(0.0, x), x1 = std::min(length, x + bl - gap);
            if (x1 - x0 > EPS) {
                Color c;
                if (color.callable())
                    c = color(i, (int)j);
                else if (rnd)
                    c = shade(color.color, rnd->uniform(0.8, 1.15));
                else
                    c = color.color;
                cuboid({(x0 + x1) / 2.0, j * bh + (bh - gap) / 2.0, 0.0}, {x1 - x0, bh - gap, bd}, c);
            }
            x += bl;
            i += 1;
        }
    }
    Mesh M = pop();
    std::array<Point, 3> fr = detail::ground_frame(direction);
    detail::current().extend(detail::local_mesh(M, origin, fr[0], fr[1], fr[2]));
}

inline void tree(const Point& at, double height, const Color& trunk_, const Color& leaves_, const std::string& kind,
                 int k, std::optional<long long> seed) {
    const Color trunk = trunk_, leaves = leaves_;              // (copies: the scene grows below)
    Random rnd(seed ? *seed : 0);
    auto var = [&](double a, double b) { return seed ? rnd.uniform(a, b) : (a + b) / 2.0; };
    double x = at[0], y = at[1], z = at[2];
    double h = height;
    if (kind == "pine") {
        cylinder({x, y, z}, {x, y + 0.3 * h, z}, 0.05 * h, 8, trunk);
        int tiers = 3;
        for (int i = 0; i < tiers; ++i) {
            double base_y = y + 0.2 * h + 0.22 * h * i;
            double rr = 0.32 * h * (1.0 - 0.22 * i) * var(0.9, 1.1);
            cone({x, base_y, z}, {x, base_y + 0.36 * h, z}, rr, k + 4, leaves);
        }
        return;
    }
    if (kind == "palm") {
        double lean = var(0.1, 0.25) * h;
        Points pts;
        for (int i = 0; i < 9; ++i) {
            double t = i / 8.0;
            pts.push_back({x + lean * detail::py_pow(t, 2), y + h * t, z});
        }
        polyline(pts, Scalar([h](double t) { return 0.06 * h * (1.0 - 0.5 * t); }), 8, trunk);
        Point top = pts.back();
        int n = 7;
        for (int i = 0; i < n; ++i) {
            double a = 2 * pi * i / n + var(-0.2, 0.2);
            double dx = std::cos(a), dz = std::sin(a);
            Points blade;
            for (int j = 0; j < 6; ++j) {
                double t = j / 5.0;
                blade.push_back({top[0] + dx * 0.45 * h * t,
                                 top[1] + 0.15 * h * std::sin(pi * t) - 0.25 * h * t * t,
                                 top[2] + dz * 0.45 * h * t});
            }
            polyline(blade, Scalar([h](double t) { return 0.035 * h * (1.0 - t) + 0.005 * h; }), 6, leaves);
        }
        return;
    }
    cylinder({x, y, z}, {x, y + 0.45 * h, z}, 0.06 * h, 8, trunk);
    const double balls[5][4] = {{0.0, 0.62, 0.0, 0.33}, {0.2, 0.5, 0.05, 0.22}, {-0.18, 0.52, -0.1, 0.2},
                                {0.02, 0.5, 0.2, 0.2}, {-0.05, 0.55, -0.22, 0.2}};
    for (const auto& ball_ : balls) {
        double dx = ball_[0], dy = ball_[1], dz = ball_[2], rr = ball_[3];
        double s = var(0.85, 1.15);
        double radius = rr * h * var(0.9, 1.1);
        // max(3, k // 3): k // 3 < 3 whenever it differs from C++'s k / 3
        sphere({x + dx * h * s, y + dy * h, z + dz * h * s}, radius, std::max(3, k / 3), leaves);
    }
}

// -- pixels and height maps ----------------------------------------------------------------------

inline const std::map<std::string, Color>& PALETTE() {
    static const std::map<std::string, Color> table = {
        {"#", "black"}, {"k", "grey"}, {"w", "white"}, {"r", "red"}, {"g", "green"},
        {"b", "blue"}, {"y", "yellow"}, {"o", "orange"}, {"p", "pink"}, {"c", "cyan"},
        {"m", "magenta"}, {"n", "brown"}, {"s", "sky"}, {"l", "lime"}, {"t", "teal"},
        {"v", "purple"}, {"d", "gold"}, {"i", "silver"}, {"a", "navy"},
    };
    return table;
}

inline void pixels(const std::vector<std::string>& rows_, double size, const Point& origin,
                   const std::map<std::string, Color>& colors, int depth, const Color& color) {
    const std::map<std::string, Color>& palette_ = colors;
    std::vector<std::vector<std::string>> rows;
    for (const std::string& r : rows_) rows.push_back(detail::pixel_cells(r));
    int ny = (int)rows.size();
    if (rows.empty()) throw std::invalid_argument("max() arg is an empty sequence");
    size_t nx = 0;
    for (const auto& r : rows) nx = std::max(nx, r.size());
    auto cell = [&](int i, int j) -> std::string {             // (add.py's char(i, j))
        const std::vector<std::string>& row = rows[ny - 1 - j];
        return (size_t)i < row.size() ? row[i] : " ";
    };
    auto filled = [&](int i, int j, int) {
        std::string c = cell(i, j);
        return c != " " && c != ".";
    };
    auto paint = [&](int i, int j, int) -> Color {
        std::string c = cell(i, j);
        auto it = palette_.find(c);
        if (it != palette_.end()) return it->second;
        return color;
    };
    size_t nz = depth > 0 ? (size_t)depth : 0;                // ([size] * depth: nothing for depth <= 0)
    detail::current().extend(detail::grid_solid(origin, std::vector<double>(nx, size),
                                                std::vector<double>((size_t)ny, size), std::vector<double>(nz, size),
                                                filled, ColorOf<int, int, int>(paint)));
}

inline void heightmap(const std::vector<std::vector<double>>& heights, double cell, const Point& origin,
                      const ColorOf<int, int, int>& color) {
    auto whole = [](double h) -> long long {                   // int(round(h)): halves to even
        if (std::isnan(h)) throw std::invalid_argument("cannot convert float NaN to integer");
        if (std::isinf(h)) throw std::overflow_error("cannot convert float infinity to integer");
        return (long long)std::nearbyint(h);
    };
    size_t nx = heights.size();
    size_t nz = heights.at(0).size();                          // (add.py: heights[0] fails on an empty list)
    long long top = 0;
    for (size_t i = 0; i < heights.size(); ++i) {              // max(max(...) for row in heights)
        const std::vector<double>& row = heights[i];
        if (row.empty()) throw std::invalid_argument("max() arg is an empty sequence");
        long long most = whole(row[0]);
        for (size_t j = 1; j < row.size(); ++j) most = std::max(most, whole(row[j]));
        if (i == 0 || most > top) top = most;
    }
    if (top <= 0) return;
    auto filled = [&](int i, int j, int k) { return j < whole(heights[i].at(k)); };
    detail::current().extend(detail::grid_solid(origin, std::vector<double>(nx, cell),
                                                std::vector<double>((size_t)top, cell),
                                                std::vector<double>(nz, cell), filled, color));
}

// -- tubes through points ---------------------------------------------------------------------------

inline void polyline(const Points& points, const Scalar& r, int k, const ColorOf<double, double>& color, bool closed,
                     int smooth) {
    Points pts = points;
    if (smooth) pts = chaikin(pts, smooth, closed);
    int n = (int)pts.size();
    if (n < 2) return;
    std::vector<double> ts;
    for (int i = 0; i < n; ++i) ts.push_back(i / (double)(closed ? n : n - 1));
    std::vector<double> radii;
    for (double t : ts) radii.push_back(r.callable() ? r(t) : r.value);
    detail::CellPaint cells = color.color;
    ColorOf<int> cap_a, cap_b;
    bool own_caps = false;                                     // (add.py: cap_a = cap_b = None)
    if (color.callable()) {
        cells = detail::CellPaint([&](int i, int j) {
            double t = (ts[i] + (i + 1 < n ? ts[i + 1] : 1.0)) / 2.0;
            return color(t, 2 * pi * (j + 0.5) / k);
        });
        cap_a = ColorOf<int>([&](int j) { return color(0.0, 2 * pi * (j + 0.5) / k); });
        cap_b = ColorOf<int>([&](int j) { return color(1.0, 2 * pi * (j + 0.5) / k); });
        own_caps = true;
    }
    Mesh M = detail::tube_along(pts, radii, k, cells, closed, own_caps ? &cap_a : nullptr,
                                own_caps ? &cap_b : nullptr);
    detail::emit(M);
}

inline void wireframe(const Mesh& M, double r, int k, std::optional<Color> color, bool nodes) {
    // add.py keeps a dict {(min, max): colour of the first face with that edge}, in the order
    // the edges came.  (M may be the scene itself, which grows while the bars are drawn: the
    // corners are looked up afresh each time, as add.py does.)
    std::vector<std::pair<std::pair<long long, long long>, Color>> edges;
    std::set<std::pair<long long, long long>> seen;
    for (size_t q = 0; q < M.F.size() && q < M.C.size(); ++q) {
        const Face& f = M.F[q];
        size_t n = f.size();
        for (size_t i = 0; i < n; ++i) {
            long long a = f[i], b = f[(i + 1) % n];
            std::pair<long long, long long> key = a < b ? std::make_pair(a, b) : std::make_pair(b, a);
            if (seen.insert(key).second) edges.push_back({key, M.C[q]});
        }
    }
    for (const auto& e : edges) {
        Point pa = M.V[detail::seq_index(e.first.first, M.V.size())];
        Point pb = M.V[detail::seq_index(e.first.second, M.V.size())];
        cylinder(pa, pb, r, k, color ? *color : e.second);
    }
    if (nodes) {
        std::vector<long long> added;                          // (a set: in CPython's order)
        for (const auto& e : edges) {
            added.push_back(e.first.first);
            added.push_back(e.first.second);
        }
        for (long long i : detail::py_set_iteration_order(added)) {
            Point p = M.V[detail::seq_index(i, M.V.size())];
            sphere(p, r, 2, color ? *color : M.C.at(0));
        }
    }
}

inline Points flow(const std::function<Point(const Point&)>& field, const Point& p0, double dt, int steps) {
    Point p{p0[0], p0[1], p0[2]};
    Points out{p};
    for (int s = 0; s < steps; ++s) {
        Point k1 = field(p);
        Point q;
        for (int i = 0; i < 3; ++i) q[i] = p[i] + 0.5 * dt * k1[i];
        Point k2 = field(q);
        for (int i = 0; i < 3; ++i) q[i] = p[i] + 0.5 * dt * k2[i];
        Point k3 = field(q);
        for (int i = 0; i < 3; ++i) q[i] = p[i] + dt * k3[i];
        Point k4 = field(q);
        Point next;
        for (int i = 0; i < 3; ++i) next[i] = p[i] + dt / 6.0 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]);
        p = next;
        out.push_back(p);
    }
    return out;
}

inline void trace(const std::function<Point(const Point&)>& field, const Point& p0, double dt, int steps,
                  const Scalar& r, int k, const ColorOf<double, double>& color, int every) {
    Points pts = flow(field, p0, dt, steps);
    if (every > 1) {                                           // pts[::every]
        Points kept;
        for (size_t i = 0; i < pts.size(); i += (size_t)every) kept.push_back(pts[i]);
        pts = kept;
    }
    polyline(pts, r, k, color);
}

}  // namespace add

namespace add {

namespace detail {

inline Point face_normal(const Mesh& M, const Face& f) {
    double nx = 0.0, ny = 0.0, nz = 0.0;
    size_t n = f.size();
    for (size_t i = 0; i < n; ++i) {
        const Point& a = M.V[f[i]];
        const Point& b = M.V[f[(i + 1) % n]];
        nx += (a[1] - b[1]) * (a[2] + b[2]);
        ny += (a[2] - b[2]) * (a[0] + b[0]);
        nz += (a[0] - b[0]) * (a[1] + b[1]);
    }
    return {nx, ny, nz};
}

inline Points vertex_normals(const Mesh& M) {
    Points acc(M.V.size(), Point{0.0, 0.0, 0.0});
    for (const Face& f : M.F) {
        if (f.size() < 3) continue;
        Point nrm = face_normal(M, f);
        for (int i : f) {
            acc[i][0] += nrm[0];
            acc[i][1] += nrm[1];
            acc[i][2] += nrm[2];
        }
    }
    Points out;
    out.reserve(acc.size());
    for (const Point& a : acc) out.push_back(norm(a) > EPS ? unit(a) : Point{0.0, 1.0, 0.0});
    return out;
}

inline std::vector<BorderEdge> boundary_edges(const Mesh& M) {
    // add.py keeps a dict {(min, max): (a, b, colour) or None}, in the order the
    // keys first came; the edges left with one face are listed in that order.
    struct Slot { int a, b; Color c; bool shared; };
    std::map<std::pair<int, int>, size_t> where;
    std::vector<Slot> slots;
    for (size_t k = 0; k < M.F.size(); ++k) {
        const Face& f = M.F[k];
        size_t n = f.size();
        for (size_t i = 0; i < n; ++i) {
            int a = f[i], b = f[(i + 1) % n];
            std::pair<int, int> key = a < b ? std::make_pair(a, b) : std::make_pair(b, a);
            auto it = where.find(key);
            if (it != where.end()) {
                slots[it->second].shared = true;
            } else {
                where[key] = slots.size();
                slots.push_back({a, b, M.C[k], false});
            }
        }
    }
    std::vector<BorderEdge> out;                               // (a second face on an edge rules it out)
    for (const Slot& s : slots)
        if (!s.shared) out.push_back({s.a, s.b, s.c});
    return out;
}

inline std::pair<Points, Points> rmf(const Points& points, bool closed) {
    size_t n = points.size();
    Points tangents;
    for (size_t i = 0; i < n; ++i) {
        Point a, b;
        if (closed) {
            a = points[(i + n - 1) % n];
            b = points[(i + 1) % n];
        } else {
            a = i > 0 ? points[i - 1] : points[i];
            b = i < n - 1 ? points[i + 1] : points[i];
        }
        Point t = unit(sub(b, a));
        if (norm(t) < EPS) t = !tangents.empty() ? tangents.back() : Point{0.0, 0.0, 1.0};
        tangents.push_back(t);
    }
    if (tangents.empty()) throw std::out_of_range("list index out of range");   // (add.py: tangents[0] fails)
    Points normals{perp(tangents[0])};
    for (size_t i = 0; i + 1 < n; ++i) {
        Point v1 = sub(points[i + 1], points[i]);
        double c1 = dot(v1, v1);
        if (c1 < EPS) {
            normals.push_back(normals.back());
            continue;
        }
        Point rL = sub(normals[i], scale(v1, 2.0 * dot(v1, normals[i]) / c1));
        Point tL = sub(tangents[i], scale(v1, 2.0 * dot(v1, tangents[i]) / c1));
        Point v2 = sub(tangents[i + 1], tL);
        double c2 = dot(v2, v2);
        if (c2 < EPS) normals.push_back(unit(rL));
        else normals.push_back(unit(sub(rL, scale(v2, 2.0 * dot(v2, rL) / c2))));
    }
    if (closed && n > 1) {
        // Cancel the leftover twist by spreading it over the whole loop.
        Point u0 = normals[0], v0 = cross(tangents[0], normals[0]);
        Point last = normals.back();
        double angle = std::atan2(dot(last, v0), dot(last, u0));
        for (size_t i = 0; i < n; ++i) {
            double a = -angle * (double)i / (double)n;
            Point u = normals[i];
            Point v = cross(tangents[i], u);
            normals[i] = add3(scale(u, std::cos(a)), scale(v, std::sin(a)));
        }
    }
    return {tangents, normals};
}

inline std::vector<Points> sweep_profile(const Points& points, const Points& tangents, const Points& normals,
                                         const Profile& profile, const Scalar& scale_, const Scalar& twist) {
    std::vector<Points> P;
    size_t n = points.size();
    for (size_t i = 0; i < n; ++i) {
        double t = n > 1 ? (double)i / (double)(n - 1) : 0.0;
        Point u = normals[i];
        Point v = cross(tangents[i], u);
        double s = scale_.callable() ? scale_(t) : (!scale_ ? 1.0 : scale_.value);
        double a = twist.callable() ? twist(t) : (!twist ? 0.0 : twist.value * t);
        double ca = std::cos(a), sa = std::sin(a);
        const Point& c = points[i];
        Points row;
        row.reserve(profile.size());
        for (const Point2& p : profile) {
            double x = p[0] * s, y = p[1] * s;
            double x2 = x * ca - y * sa, y2 = x * sa + y * ca;
            row.push_back({c[0] + u[0] * x2 + v[0] * y2,
                           c[1] + u[1] * x2 + v[1] * y2,
                           c[2] + u[2] * x2 + v[2] * y2});
        }
        P.push_back(row);
    }
    return P;
}

}  // namespace detail

// -- parametric surfaces -----------------------------------------------------------

inline void parametric(const SurfaceFn& S, double min_u, double max_u, int grid_u, double min_v, double max_v,
                       int grid_v, const ColorOf<double, double>& color, bool wrap_u, bool wrap_v, bool flip,
                       double thickness, bool double_sided) {
    if (grid_u == 0 || grid_v == 0)
        throw std::domain_error("float division by zero");      // (as Python: ZeroDivisionError)
    int nu = wrap_u ? grid_u : grid_u + 1;
    int nv = wrap_v ? grid_v : grid_v + 1;
    std::vector<Points> P;
    for (int i = 0; i < nu; ++i) {
        double u = min_u + (max_u - min_u) * i / (double)grid_u;
        Points row;
        for (int j = 0; j < nv; ++j) {
            double v = min_v + (max_v - min_v) * j / (double)grid_v;
            Point p = S(u, v);
            row.push_back({p[0], p[1], p[2]});
        }
        P.push_back(row);
    }
    detail::CellPaint cells = color.color;
    if (color.callable())                                      // painted by the middle of each cell
        cells = detail::CellPaint([&](int i, int j) {
            return color(min_u + (max_u - min_u) * (i + 0.5) / (double)grid_u,
                         min_v + (max_v - min_v) * (j + 0.5) / (double)grid_v);
        });
    Mesh M;
    detail::add_grid(M, P, cells, wrap_u, wrap_v, flip);
    if (thickness)
        M = solidify(M, thickness);
    else if (double_sided)
        M = two_sided(M);
    detail::current().extend(M);
}

inline Mesh two_sided(const Mesh& M) {
    Mesh out = M.copy();
    for (size_t k = 0; k < M.F.size(); ++k) {
        Face f(M.F[k].rbegin(), M.F[k].rend());
        if (M.has_uv && !M.UV[k].empty())                      // (an empty list: add.py's None)
            out.add_face(f, M.C[k], std::vector<Point2>(M.UV[k].rbegin(), M.UV[k].rend()));
        else
            out.add_face(f, M.C[k]);
    }
    return out;
}
inline Mesh two_sided() { return two_sided(scene()); }

inline Mesh solidify(const Mesh& M, double thickness, bool both_ways) {
    Points normals = detail::vertex_normals(M);
    int n = (int)M.V.size();
    Mesh out;
    double up = both_ways ? thickness / 2.0 : thickness;
    double down = both_ways ? -thickness / 2.0 : 0.0;
    for (size_t i = 0; i < M.V.size(); ++i) {
        const Point &p = M.V[i], &nrm = normals[i];
        out.add_vertex({p[0] + nrm[0] * up, p[1] + nrm[1] * up, p[2] + nrm[2] * up});
    }
    for (size_t i = 0; i < M.V.size(); ++i) {
        const Point &p = M.V[i], &nrm = normals[i];
        out.add_vertex({p[0] + nrm[0] * down, p[1] + nrm[1] * down, p[2] + nrm[2] * down});
    }
    for (size_t q = 0; q < M.F.size(); ++q) {
        const Face& f = M.F[q];
        out.add_face(f, M.C[q]);                               // outer shell
        Face inner;
        for (auto it = f.rbegin(); it != f.rend(); ++it) inner.push_back(*it + n);
        out.add_face(inner, M.C[q]);                           // inner shell
    }
    // Stitch the boundary: any edge used by exactly one face is on the border.
    // The wall runs outer -> inner -> inner -> outer so that it faces outwards.
    for (const detail::BorderEdge& edge : detail::boundary_edges(M))
        out.add_face({edge.a, edge.a + n, edge.b + n, edge.b}, edge.color);
    return out;
}
inline Mesh solidify() { return solidify(scene()); }

// -- curves, sweeps and lofts ----------------------------------------------------------

inline void sweep(const Profile& profile, const PathFn& path, double t0, double t1, int steps,
                  const ColorOf<double, int>& color, bool closed, const Scalar& scale, const Scalar& twist, bool caps) {
    if (steps == 0)
        throw std::domain_error("float division by zero");      // (as Python: ZeroDivisionError)
    int n = closed ? steps : steps + 1;
    Points points;
    for (int i = 0; i < n; ++i) {
        double t = t0 + (t1 - t0) * i / (double)steps;
        Point p = path(t);
        points.push_back({p[0], p[1], p[2]});
    }
    std::pair<Points, Points> frames = detail::rmf(points, closed);
    std::vector<Points> P = detail::sweep_profile(points, frames.first, frames.second, profile, scale, twist);
    detail::CellPaint cells = color.color;
    Color cap_a = color.color, cap_b = color.color;
    if (color.callable()) {                                    // cell (i, j) -> (t, edge j of the profile)
        cells = detail::CellPaint([&](int i, int j) { return color(t0 + (t1 - t0) * (i + 0.5) / (double)steps, j); });
        cap_a = color(t0, -1);
        cap_b = color(t1, -1);
    }
    Mesh M;
    detail::add_grid(M, P, cells, closed, true, true);
    if (caps && !closed) {
        M.add_polygon(Points(P[0].rbegin(), P[0].rend()), cap_a);
        M.add_polygon(P.back(), cap_b);
        detail::weld(M, 1e-9);
        detail::make_outward(M, 0);
    }
    detail::emit(M);
}

inline void curve(const PathFn& P, double min_t, double max_t, int grid_t, int k, const Scalar& r,
                  const ColorOf<double, double>& color, bool isConnected) {
    if (grid_t == 0)
        throw std::domain_error("float division by zero");      // (as Python: ZeroDivisionError)
    detail::CellPaint cells = color.color;
    ColorOf<int> cap_a = color.color, cap_b = color.color;
    if (color.callable()) {                                    // cell (i, j) -> (t, angle round the tube)
        cells = detail::CellPaint([&](int i, int j) {
            double t = min_t + (max_t - min_t) * (i + 0.5) / (double)grid_t;
            return color(t, 2.0 * pi * (j + 0.5) / (double)k);
        });
        cap_a = ColorOf<int>([&](int j) { return color(min_t, 2.0 * pi * (j + 0.5) / (double)k); });
        cap_b = ColorOf<int>([&](int j) { return color(max_t, 2.0 * pi * (j + 0.5) / (double)k); });
    }
    int n = isConnected ? grid_t : grid_t + 1;
    std::vector<double> ts;
    Points points;
    for (int i = 0; i < n; ++i) {
        double t = min_t + (max_t - min_t) * i / (double)grid_t;
        ts.push_back(t);
        Point p = P(t);
        points.push_back({p[0], p[1], p[2]});
    }
    std::vector<double> radii;
    for (double t : ts) radii.push_back(r.callable() ? r(t) : r.value);
    Mesh M = detail::tube_along(points, radii, k, cells, isConnected, &cap_a, &cap_b);
    detail::emit(M);
}

inline void extrude(const Profile& profile, const Point& direction, const ColorOf<double, int>& color, int steps,
                    const Scalar& twist, const Scalar& scale, const Point& center, bool caps) {
    auto path = [&](double t) {
        return Point{center[0] + direction[0] * t, center[1] + direction[1] * t, center[2] + direction[2] * t};
    };
    sweep(profile, path, 0.0, 1.0, std::max(1, steps), color, false, scale, twist, caps);
}

inline void loft(const std::vector<Points>& sections, const Color& color, bool closed, bool caps, bool flip) {
    Mesh M;
    detail::add_grid(M, sections, color, closed, true, !flip);
    if (caps && !closed) {
        M.add_polygon(Points(sections[0].rbegin(), sections[0].rend()), color);
        M.add_polygon(sections.back(), color);
        detail::weld(M, 1e-9);
        detail::make_outward(M, 0);
    }
    detail::emit(M);
}

inline void ribbon(const PathFn& path, double t0, double t1, int steps, double width, const Color& color, bool closed,
                   const Scalar& twist, double thickness) {
    if (steps == 0)
        throw std::domain_error("float division by zero");      // (as Python: ZeroDivisionError)
    double half = width / 2.0;
    Profile profile{{-half, 0.0}, {half, 0.0}};
    int n = closed ? steps : steps + 1;
    Points points;
    for (int i = 0; i < n; ++i) {
        double t = t0 + (t1 - t0) * i / (double)steps;
        Point p = path(t);
        points.push_back({p[0], p[1], p[2]});
    }
    std::pair<Points, Points> frames = detail::rmf(points, closed);
    std::vector<Points> P = detail::sweep_profile(points, frames.first, frames.second, profile, Scalar(), twist);
    Mesh M;
    detail::add_grid(M, P, color, closed);
    if (thickness)
        M = solidify(M, thickness);
    else
        M = two_sided(M);
    detail::current().extend(M);
}

inline void circle(const Point& A, const Point& B, double r, int k, const Color& color) { disc(A, B, r, k, color); }

}  // namespace add

namespace add {

namespace detail {

// Two dozen classical parametric surfaces, ready to draw by name.  Each entry holds the
// formula, the parameter ranges, whether the surface closes on itself (so that it is drawn
// without a seam) and the constants it depends on.  The formulas follow the collection at
// drhuang.com ("parametric surfaces", A. Huang) and the standard references (Gray, "Modern
// Differential Geometry of Curves and Surfaces"; 3D-XplorMath).  Each is written exactly as
// in add.py (x ** n is py_pow(x, n), the C library's pow as Python calls it), so that it gives the
// very same numbers.
inline SurfaceTable catalog() {
    using std::cos; using std::sin; using std::sinh; using std::cosh; using std::exp; using std::log;
    using std::tan; using std::sqrt;
    using P = const SurfaceParams&;
    SurfaceTable S;
    auto entry = [&S](const std::string& name, std::function<Point(double, double, P)> f, Point2 u, Point2 v,
                      std::array<bool, 2> wrap, std::array<int, 2> grid, const std::string& note, bool flip,
                      SurfaceParams params) {
        S.set(name, SurfaceEntry{f, u, v, wrap, grid, note, flip, params});
    };
    const std::array<bool, 2> no_wrap{{false, false}};
    const std::array<int, 2> g60{{60, 60}};

    entry("bohemian_dome",
          [](double u, double v, P p) {
              double a = p.at("a"), b = p.at("b"), c = p.at("c");
              return Point{a * cos(u), b * cos(v) + a * sin(u), c * sin(v)};
          },
          {0, 2 * pi}, {0, 2 * pi}, {{true, true}}, g60, "a circle swept along another circle", false,
          {{"a", 0.5}, {"b", 1.5}, {"c", 1.0}});
    entry("dini",
          [](double u, double v, P p) {
              double a = p.at("a"), b = p.at("b");
              return Point{a * cos(u) * sin(v), a * sin(u) * sin(v), a * (cos(v) + log(tan(v / 2.0))) + b * u};
          },
          {0, 4 * pi}, {0.01, 2.0}, no_wrap, {{120, 40}}, "a twisted pseudosphere of constant negative curvature",
          false, {{"a", 1.0}, {"b", 0.2}});
    entry("enneper",
          [](double u, double v, P) {
              return Point{u - py_pow(u, 3) / 3.0 + u * v * v, v - py_pow(v, 3) / 3.0 + u * u * v, u * u - v * v};
          },
          {-2, 2}, {-2, 2}, no_wrap, g60, "a minimal surface that crosses itself", false, {});
    entry("klein_bottle",
          [](double u, double v, P p) {
              double a = p.at("a"), b = p.at("b");
              double r = 4.0 * (1.0 - cos(u) / 2.0);
              if (u < pi)
                  return Point{a * cos(u) * (1 + sin(u)) + r * cos(u) * cos(v), b * sin(u) + r * sin(u) * cos(v),
                               r * sin(v)};
              return Point{a * cos(u) * (1 + sin(u)) + r * cos(v + pi), b * sin(u), r * sin(v)};
          },
          {0, 2 * pi}, {0, 2 * pi}, {{false, true}}, {{120, 40}},
          "the one-sided bottle whose neck passes through its own wall", false, {{"a", 6.0}, {"b", 16.0}});
    entry("mobius",
          [](double t, double s, P p) {
              double R = p.at("R");
              return Point{(R + s * cos(t / 2.0)) * cos(t), (R + s * cos(t / 2.0)) * sin(t), s * sin(t / 2.0)};
          },
          {0, 2 * pi}, {-0.5, 0.5}, no_wrap, {{120, 8}}, "a strip with one side and one edge", false, {{"R", 2.0}});
    entry("plucker_conoid",
          [](double u, double v, P) { return Point{u * sqrt(1 - v * v), u * v, 1 - v * v}; },
          {-2, 2}, {-1, 1}, no_wrap, g60, "a ruled surface: straight lines through a vertical axis", false, {});
    entry("worm",
          [](double u, double v, P p) {
              double a = p.at("a"), b = p.at("b");
              double h = exp(u / (6.0 * pi));
              return Point{a * (1 - h) * cos(u) * py_pow(cos(v / 2.0), 2),
                           1 - exp(u / (b * pi)) - sin(v) + h * sin(v),
                           a * (h - 1) * sin(u) * py_pow(cos(v / 2.0), 2)};
          },
          {0, 6 * pi}, {0, 2 * pi}, {{false, true}}, {{160, 40}}, "a snail shell that widens as it turns", false,
          {{"a", 1.0}, {"b", 6.0}});
    entry("sine_surface",
          [](double u, double v, P) { return Point{sin(u), sin(v), sin(u + v)}; },
          {-pi, pi}, {-pi, pi}, {{true, true}}, g60, "three sines; it closes on itself in both directions", false,
          {});
    entry("cosine_surface",
          [](double u, double v, P) { return Point{cos(u), cos(v), cos(u + v)}; },
          {-pi, pi}, {-pi, pi}, {{true, true}}, g60, "the cosine twin of the sine surface", true, {});
    entry("whitney_umbrella",
          [](double u, double v, P) { return Point{u * v, u, v * v}; },
          {-1.5, 1.5}, {-1.5, 1.5}, no_wrap, g60, "a surface with a pinch point", false, {});
    entry("helicoid",
          [](double u, double v, P p) {
              double c = p.at("c");
              return Point{u * cos(v), u * sin(v), c * v};
          },
          {-2, 2}, {0, 2 * pi}, no_wrap, {{30, 120}}, "a spiral staircase; the only ruled minimal surface", false,
          {{"c", 0.5}});
    entry("hyperbolic_helicoid",
          [](double u, double v, P p) {
              double a = p.at("a");
              return Point{sinh(v) * cos(a * u) / (1 + cosh(u) * cosh(v)),
                           sinh(v) * sin(a * u) / (1 + cosh(u) * cosh(v)),
                           cosh(v) * sinh(u) / (1 + cosh(u) * cosh(v))};
          },
          {-4, 4}, {-4, 4}, no_wrap, {{120, 60}}, "a helicoid bent into a ball", false, {{"a", 2.5}});
    entry("henneberg",
          [](double u, double v, P) {
              return Point{2 * cos(v) * sinh(u) - 0.667 * cos(3 * v) * sinh(3 * u),
                           2 * sin(v) * sinh(u) + 0.667 * sin(3 * v) * sinh(3 * u),
                           2 * cos(2 * v) * cosh(2 * u)};
          },
          {-1, 1}, {-pi / 2, pi / 2}, no_wrap, g60, "a one-sided minimal surface", false, {});
    entry("owl",
          [](double u, double v, P) {
              return Point{v * cos(u) - 0.5 * v * v * cos(2 * u),
                           -v * sin(u) - 0.5 * v * v * sin(2 * u),
                           4 * exp(1.5 * log(v)) * cos(1.5 * u) / 3.0};
          },
          {0, 4 * pi}, {0.001, 1}, no_wrap, {{160, 30}}, "Maeder's owl, a twisted minimal surface", false, {});
    entry("snail",
          [](double u, double v, P) { return Point{u * cos(v) * sin(u), u * cos(u) * cos(v), -u * sin(v)}; },
          {0, 2 * pi}, {-pi, pi}, {{false, true}}, {{120, 40}}, "a horn that curls up on itself", false, {});
    entry("kidney",
          [](double u, double v, P) {
              return Point{cos(u) * (3 * cos(v) - cos(3 * v)), sin(u) * (3 * cos(v) - cos(3 * v)),
                           3 * sin(v) - sin(3 * v)};
          },
          {0, 2 * pi}, {-pi / 2, pi / 2}, {{true, false}}, {{80, 40}}, "a surface of revolution with a dent", false,
          {});
    entry("pillow",
          [](double u, double v, P p) {
              double a = p.at("a");
              return Point{cos(u), cos(v), a * sin(u) * sin(v)};
          },
          {0, pi}, {-pi, pi}, {{false, true}}, {{40, 80}}, "a cushion with four corners", false, {{"a", 0.5}});
    entry("horn",
          [](double u, double v, P p) {
              double a = p.at("a"), b = p.at("b"), c = p.at("c");
              return Point{(a + u * cos(v)) * sin(b * pi * u), (a + u * cos(v)) * cos(b * pi * u) + c * u,
                           u * sin(v)};
          },
          {0, 1}, {-pi, pi}, {{false, true}}, {{60, 40}}, "a tube that grows as it bends", false,
          {{"a", 1.0}, {"b", 1.0}, {"c", 1.0}});
    entry("stiletto",
          [](double u, double v, P) {
              return Point{(2 + cos(u)) * py_pow(cos(v), 3) * sin(v),
                           (2 + cos(u + 2 * pi / 3)) * py_pow(cos(v + 2 * pi / 3), 2) * py_pow(sin(v + 2 * pi / 3), 2),
                           -(2 + cos(u - 2 * pi / 3)) * py_pow(cos(v + 2 * pi / 3), 2) * py_pow(sin(v + 2 * pi / 3), 2)};
          },
          {0, 2 * pi}, {0, pi}, {{true, false}}, {{80, 60}}, "a pointed shoe", false, {});
    entry("apple",
          [](double u, double v, P) {
              return Point{cos(u) * (4 + 3.8 * cos(v)), sin(u) * (4 + 3.8 * cos(v)),
                           (cos(v) + sin(v) - 1) * (1 + sin(v)) * log(1 - pi * v / 10.0) + 7.5 * sin(v)};
          },
          {0, 2 * pi}, {-pi, pi}, {{true, false}}, {{80, 60}}, "an apple with a dimple at the stalk", false, {});
    entry("kuen",
          [](double u, double v, P) {
              double h = 1 + u * u * py_pow(sin(v), 2);
              return Point{2 * (cos(u) + u * sin(u)) * sin(v) / h, 2 * (-u * cos(u) + sin(u)) * sin(v) / h,
                           log(tan(v / 2.0)) + 2 * cos(v) / h};
          },
          {-4.3, 4.3}, {0.03, 3.11}, no_wrap, {{120, 60}}, "a surface of constant negative curvature", false, {});
    entry("tranguloid_trefoil",
          [](double u, double v, P) {
              return Point{2 * sin(3 * u) / (2 + cos(v)), 2 * (sin(u) + 2 * sin(2 * u)) / (2 + cos(v + 2 * pi / 3)),
                           (cos(u) - 2 * cos(2 * u)) * (2 + cos(v)) * (2 + cos(v + 2 * pi / 3)) / 4.0};
          },
          {-pi, pi}, {-pi, pi}, {{true, true}}, {{160, 40}}, "a knotted tube with three lobes", false, {});
    entry("antisymmetric_torus",
          [](double u, double v, P p) {
              double R = p.at("R"), r = p.at("r"), a = p.at("a");
              return Point{(R + r * cos(v) * (a + sin(u))) * cos(u), (R + r * cos(v) * (a + sin(u))) * sin(u),
                           r * sin(v) * (a + sin(u))};
          },
          {0, 2 * pi}, {0, 2 * pi}, {{true, true}}, {{80, 40}}, "a torus whose tube is fat on one side", false,
          {{"R", 2.0}, {"r", 0.6}, {"a", 1.5}});
    entry("twisted_eight_torus",
          [](double u, double v, P p) {
              double R = p.at("R"), r = p.at("r");
              return Point{(R + r * (cos(u / 2.0) * sin(v) - sin(u / 2.0) * sin(2 * v))) * cos(u),
                           (R + r * (cos(u / 2.0) * sin(v) - sin(u / 2.0) * sin(2 * v))) * sin(u),
                           r * (sin(u / 2.0) * sin(v) + cos(u / 2.0) * sin(2 * v))};
          },
          {0, 2 * pi}, {0, 2 * pi}, {{false, true}}, {{120, 60}},
          "a figure-eight cross-section that twists once around", false, {{"R", 2.0}, {"r", 1.0}});
    entry("wave_ball",
          [](double u, double v, P) {
              return Point{u * cos(cos(u)) * cos(v), u * cos(cos(u)) * sin(v), u * sin(cos(u))};
          },
          {0, 14.5}, {0, 2 * pi}, {{false, true}}, {{160, 40}}, "rings that ripple outwards", false, {});
    return S;
}

inline const SurfaceEntry& surface_entry(const std::string& name) { return SURFACES().at(name); }

inline void draw_surface(const std::string& name, const Point& center, std::optional<double> size, int gu, int gv,
                         const ColorOf<double, double>& color, double thickness, bool double_sided,
                         const SurfaceParams& params) {
    const SurfaceEntry& entry = surface_entry(name);
    SurfaceFn f = surface_function(name, params);
    double u0 = entry.u[0], u1 = entry.u[1], v0 = entry.v[0], v1 = entry.v[1];
    push();
    parametric(f, u0, u1, gu, v0, v1, gv, color, entry.wrap[0], entry.wrap[1], entry.flip, thickness, double_sided);
    Mesh M = pop();
    if (size) M = fit(M, *size);
    M = place(M, center);
    detail::current().extend(M);
}

}  // namespace detail

inline const SurfaceTable& SURFACES() {
    static const SurfaceTable table = detail::catalog();
    return table;
}

inline std::vector<std::string> surface_names() {
    std::vector<std::string> out;
    for (const SurfaceTable::value_type& kv : SURFACES()) out.push_back(kv.first);
    std::sort(out.begin(), out.end());
    return out;
}

inline SurfaceFn surface_function(const std::string& name, const SurfaceParams& params) {
    const SurfaceEntry& entry = detail::surface_entry(name);
    SurfaceParams values = entry.params;
    std::string unknown;                                       // a constant the formula does not take
    for (const auto& kv : params) {
        values[kv.first] = kv.second;
        if (unknown.empty() && !entry.params.count(kv.first)) unknown = kv.first;
    }
    std::function<Point(double, double, const SurfaceParams&)> f = entry.f;
    return [f, values, unknown](double u, double v) {
        if (!unknown.empty())                                  // (add.py: TypeError, when it is called)
            throw std::invalid_argument("got an unexpected keyword argument '" + unknown + "'");
        return f(u, v, values);
    };
}

inline void surface(const std::string& name, const Point& center, std::optional<double> size,
                    std::optional<int> grid, const ColorOf<double, double>& color, double thickness,
                    bool double_sided, const SurfaceParams& params) {
    const SurfaceEntry& entry = detail::surface_entry(name);
    int gu = grid ? *grid : entry.grid[0];
    int gv = grid ? *grid : entry.grid[1];
    detail::draw_surface(name, center, size, gu, gv, color, thickness, double_sided, params);
}

inline void surface(const std::string& name, const Point& center, std::optional<double> size,
                    const std::array<int, 2>& grid, const ColorOf<double, double>& color, double thickness,
                    bool double_sided, const SurfaceParams& params) {
    detail::surface_entry(name);                               // (add.py: SURFACES[name] first)
    detail::draw_surface(name, center, size, grid[0], grid[1], color, thickness, double_sided, params);
}

}  // namespace add

namespace add {

namespace detail {
inline Mesh mapped(const Mesh& M, const std::function<Point(const Point&)>& f, bool flip) {
    Mesh out;
    out.V.reserve(M.V.size());
    for (const Point& p : M.V) out.V.push_back(f(p));
    out.F = M.F;
    if (flip)
        for (Face& x : out.F) std::reverse(x.begin(), x.end());
    out.C = M.C;
    out.has_uv = M.has_uv;
    if (M.has_uv) {
        out.UV = M.UV;
        if (flip)
            for (auto& t : out.UV) std::reverse(t.begin(), t.end());
    }
    return out;
}

inline size_t seq_index(long long i, size_t n) {
    long long j = i < 0 ? i + (long long)n : i;
    if (j < 0 || j >= (long long)n) throw std::out_of_range("index out of range");
    return (size_t)j;
}

inline bool color_tuple_less(const Color& a, const Color& b) {
    if (a.r != b.r) return a.r < b.r;
    if (a.g != b.g) return a.g < b.g;
    if (a.b != b.b) return a.b < b.b;
    // add.py's colour is (r, g, b), (r, g, b, alpha) when see-through, (r, g, b, alpha, image) when
    // textured; tuples compare item by item, and a shorter one that runs out first is the smaller.
    int la = !a.image.empty() ? 5 : (a.alpha < 1.0 ? 4 : 3);
    int lb = !b.image.empty() ? 5 : (b.alpha < 1.0 ? 4 : 3);
    if (la == 3 || lb == 3) return la < lb;
    if (a.alpha != b.alpha) return a.alpha < b.alpha;
    if (la == 4 || lb == 4) return la < lb;
    return a.image < b.image;
}
}  // namespace detail

inline std::array<Point, 2> bbox(const Mesh& M) {
    if (M.V.empty()) return {Point{0, 0, 0}, Point{0, 0, 0}};
    Point lo = M.V[0], hi = M.V[0];
    for (const Point& p : M.V)
        for (int a = 0; a < 3; ++a) {
            if (p[a] < lo[a]) lo[a] = p[a];                    // (Python's min/max: the first of equals)
            if (p[a] > hi[a]) hi[a] = p[a];
        }
    return {lo, hi};
}
inline std::array<Point, 2> bbox() { return bbox(scene()); }

inline Point size(const Mesh& M) {
    auto b = bbox(M);
    return {b[1][0] - b[0][0], b[1][1] - b[0][1], b[1][2] - b[0][2]};
}
inline Point size() { return size(scene()); }

inline Point center(const Mesh& M) {
    if (M.V.empty()) return {0.0, 0.0, 0.0};
    double n = (double)M.V.size();
    Point out;
    for (int a = 0; a < 3; ++a) {
        double s = 0.0;                                         // (plain left-to-right sum, as add.py's _total)
        for (const Point& p : M.V) s += p[a];
        out[a] = s / n;
    }
    return out;
}
inline Point center() { return center(scene()); }

inline Point middle(const Mesh& M) {
    auto b = bbox(M);
    return {(b[0][0] + b[1][0]) / 2.0, (b[0][1] + b[1][1]) / 2.0, (b[0][2] + b[1][2]) / 2.0};
}
inline Point middle() { return middle(scene()); }

inline double area(const Mesh& M) {
    double total = 0.0;
    for (const Face& f : M.F) {
        if (f.size() < 3) continue;
        const Point& a = M.V[f[0]];
        for (size_t t = 1; t + 1 < f.size(); ++t)
            total += detail::norm(cross(detail::sub(M.V[f[t]], a), detail::sub(M.V[f[t + 1]], a))) / 2.0;
    }
    return total;
}
inline double area() { return area(scene()); }

inline double volume(const Mesh& M) { return detail::signed_volume(M, 0) / 6.0; }
inline double volume() { return volume(scene()); }

inline Mesh move(const Mesh& M, const Point& V) {
    return detail::mapped(M, [&](const Point& p) { return Point{p[0] + V[0], p[1] + V[1], p[2] + V[2]}; });
}

inline Mesh place(const Mesh& M, const Point& at, bool use_bbox) {
    Point c = use_bbox ? middle(M) : center(M);
    return move(M, {at[0] - c[0], at[1] - c[1], at[2] - c[2]});
}

inline Mesh rotateX(const Mesh& M, double angle, const Point& P) {
    double cs = std::cos(angle), sn = std::sin(angle);
    return detail::mapped(M, [&](const Point& p) {
        double y = p[1] - P[1], z = p[2] - P[2];
        return Point{p[0], P[1] + y * cs - z * sn, P[2] + y * sn + z * cs};
    });
}

inline Mesh rotateY(const Mesh& M, double angle, const Point& P) {
    double cs = std::cos(angle), sn = std::sin(angle);
    return detail::mapped(M, [&](const Point& p) {
        double x = p[0] - P[0], z = p[2] - P[2];
        return Point{P[0] + x * cs + z * sn, p[1], P[2] + z * cs - x * sn};
    });
}

inline Mesh rotateZ(const Mesh& M, double angle, const Point& P) {
    double cs = std::cos(angle), sn = std::sin(angle);
    return detail::mapped(M, [&](const Point& p) {
        double x = p[0] - P[0], y = p[1] - P[1];
        return Point{P[0] + x * cs - y * sn, P[1] + x * sn + y * cs, p[2]};
    });
}

inline Mesh rotate(const Mesh& M, const Point& axis, double angle, const Point& P) {
    Point k = detail::unit(axis);
    double cs = std::cos(angle), sn = std::sin(angle);
    return detail::mapped(M, [&](const Point& p) {
        Point v = detail::sub(p, P);
        Point kv = cross(k, v);
        double d = dot(k, v) * (1.0 - cs);
        return Point{P[0] + v[0] * cs + kv[0] * sn + k[0] * d,
                     P[1] + v[1] * cs + kv[1] * sn + k[1] * d,
                     P[2] + v[2] * cs + kv[2] * sn + k[2] * d};
    });
}

inline Mesh zoom(const Mesh& M, double s, std::optional<Point> about) {
    Point c = about ? *about : center(M);
    return detail::mapped(M, [&](const Point& p) {
        return Point{c[0] + (p[0] - c[0]) * s, c[1] + (p[1] - c[1]) * s, c[2] + (p[2] - c[2]) * s};
    }, s < 0);
}

inline Mesh stretch(const Mesh& M, const Point& s, std::optional<Point> about) {
    Point c = about ? *about : center(M);
    bool flip = (s[0] * s[1] * s[2]) < 0;
    return detail::mapped(M, [&](const Point& p) {
        return Point{c[0] + (p[0] - c[0]) * s[0], c[1] + (p[1] - c[1]) * s[1], c[2] + (p[2] - c[2]) * s[2]};
    }, flip);
}

inline Mesh color(const Mesh& M, const Color& RGB) {
    Mesh out = M;
    out.C.assign(M.F.size(), RGB);
    return out;
}

inline Mesh fit(const Mesh& M, double target, std::optional<Point> about) {
    Point s = size(M);
    double d = s[0];                                           // max(size(M))
    for (int a = 1; a < 3; ++a)
        if (s[a] > d) d = s[a];
    return zoom(M, d > EPS ? target / d : 1.0, about);
}

inline Mesh mirror(const Mesh& M, const Point& point, const Point& normal) {
    Point n = detail::unit(normal);
    return detail::mapped(M, [&](const Point& p) {
        double d = 2.0 * dot(detail::sub(p, point), n);
        return Point{p[0] - n[0] * d, p[1] - n[1] * d, p[2] - n[2] * d};
    }, true);
}

inline Mesh transform(const Mesh& M, const std::vector<std::vector<double>>& matrix) {
    const std::vector<std::vector<double>>& m = matrix;
    if (m.size() < 3 || m[0].size() < 3 || m[1].size() < 3 || m[2].size() < 3)
        throw std::out_of_range("transform: the matrix needs 3 rows of 3 (or 4) numbers");
    double det = (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
                  - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
                  + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]));
    return detail::mapped(M, [&](const Point& p) {
        double x = m[0][0] * p[0] + m[0][1] * p[1] + m[0][2] * p[2];
        double y = m[1][0] * p[0] + m[1][1] * p[1] + m[1][2] * p[2];
        double z = m[2][0] * p[0] + m[2][1] * p[1] + m[2][2] * p[2];
        if (m[0].size() > 3) {                                 // a translation column
            x += m[0].at(3);
            y += m[1].at(3);
            z += m[2].at(3);
        }
        return Point{x, y, z};
    }, det < 0);
}

inline Mesh deform(const Mesh& M, const std::function<Point(const Point&)>& f) { return detail::mapped(M, f); }

inline Mesh twist(const Mesh& M, double angle, const Point& axis, const Point& P) {
    Point k = detail::unit(axis);
    return detail::mapped(M, [&](const Point& p) {
        double h = dot(detail::sub(p, P), k);
        double a = angle * h;
        double cs = std::cos(a), sn = std::sin(a);
        Point v = detail::sub(p, P);
        Point kv = cross(k, v);
        double d = dot(k, v) * (1.0 - cs);
        return Point{P[0] + v[0] * cs + kv[0] * sn + k[0] * d,
                     P[1] + v[1] * cs + kv[1] * sn + k[1] * d,
                     P[2] + v[2] * cs + kv[2] * sn + k[2] * d};
    });
}

inline Mesh taper(const Mesh& M, double factor, int axis, const Point& P) {
    std::vector<int> other;                                    // (with the axis as given: -1 leaves all three)
    for (int a = 0; a < 3; ++a)
        if (a != axis) other.push_back(a);
    return detail::mapped(M, [&](const Point& p) {
        int ax = (int)detail::seq_index(axis, 3);              // p[axis], Python style
        double s = 1.0 + factor * (p[ax] - P[ax]);
        Point q = p;
        for (int a : other) q[a] = P[a] + (p[a] - P[a]) * s;
        return q;
    });
}

inline Mesh bend(const Mesh& M, double angle, int axis, int around, const Point& P) {
    int third = 3 - axis - around;
    return detail::mapped(M, [&](const Point& p) {
        Point q = p;
        int ax = (int)detail::seq_index(axis, 3);
        double h = p[ax] - P[ax];
        double a = angle * h;
        if (std::fabs(angle) < EPS) return q;
        double r = 1.0 / angle;
        int th = (int)detail::seq_index(third, 3);
        double d = p[th] - P[th];
        q[ax] = P[ax] + (r - d) * std::sin(a);
        q[th] = P[th] + r - (r - d) * std::cos(a);
        return q;
    });
}

inline Mesh jitter(const Mesh& M, double amount, std::optional<long long> seed) {
    Random local = seed ? Random(*seed) : Random(0);
    Random& r = seed ? local : detail::rng();
    return detail::mapped(M, [&](const Point& p) {
        double dx = r.uniform(-amount, amount);                // (x, then y, then z)
        double dy = r.uniform(-amount, amount);
        double dz = r.uniform(-amount, amount);
        return Point{p[0] + dx, p[1] + dy, p[2] + dz};
    });
}

inline Mesh opacity(const Mesh& M, double alpha) {
    Mesh out = M;
    for (size_t i = 0; i < M.C.size(); ++i) out.C[i] = transparent(M.C[i], alpha);   // keeps the image
    return out;
}

namespace detail {

inline Mesh texture_map(const Mesh& M, const std::string& image, const std::string& mapping,
                        const TextureFn* custom, double scale, const std::optional<Color>& color,
                        const Point2& offset) {
    std::array<Point, 2> bb = bbox(M);
    const Point lo = bb[0], hi = bb[1];
    Point mid, span;
    for (int a = 0; a < 3; ++a) mid[a] = (lo[a] + hi[a]) / 2.0;
    for (int a = 0; a < 3; ++a) span[a] = std::max(hi[a] - lo[a], EPS);
    double ox = offset[0], oy = offset[1];
    double s = scale != 0.0 ? scale : 1.0;                     // (Python: ``if scale``)

    TextureFn fn;
    if (custom) {
        fn = *custom;
    } else if (mapping == "box") {                             // each face along its dominant axis
        fn = [&](const Point& p, const Point& n) {
            int axis = 0;                                      // max(range(3), key=|n[a]|): the first largest
            for (int a = 1; a < 3; ++a)
                if (std::fabs(n[a]) > std::fabs(n[axis])) axis = a;
            int i = axis == 0 ? 2 : 0, j = axis == 1 ? 2 : 1;  // X: (z, y), Y: (x, z), Z: (x, y)
            return Point2{(p[i] - ox) / s, (p[j] - oy) / s};
        };
    } else if (mapping == "xy" || mapping == "xz" || mapping == "yz") {
        int i = mapping == "yz" ? 2 : 0, j = mapping == "xz" ? 2 : 1;
        fn = [&, i, j](const Point& p, const Point&) { return Point2{(p[i] - ox) / s, (p[j] - oy) / s}; };
    } else if (mapping == "fit") {
        fn = [&](const Point& p, const Point&) {
            return Point2{(p[0] - lo[0]) / span[0], (p[1] - lo[1]) / span[1]};
        };
    } else if (mapping == "sphere") {
        fn = [&](const Point& p, const Point&) {
            Point d = unit(sub(p, mid));
            double y = d[1] < 1.0 ? d[1] : 1.0;                // max(-1.0, min(1.0, d[1]))
            y = y > -1.0 ? y : -1.0;
            return Point2{(std::atan2(d[2], d[0]) / (2 * pi) + 0.5) * s, std::asin(y) / pi + 0.5};
        };
    } else if (mapping == "cylinder") {
        fn = [&](const Point& p, const Point&) {
            return Point2{(std::atan2(p[2] - mid[2], p[0] - mid[0]) / (2 * pi) + 0.5) * s,
                          (p[1] - lo[1]) / span[1]};
        };
    } else {
        throw std::invalid_argument("unknown texture mapping: '" + mapping + "'");
    }
    bool seam = !custom && (mapping == "sphere" || mapping == "cylinder");

    Mesh out = M;
    out.has_uv = true;
    out.UV.clear();
    for (size_t i = 0; i < M.F.size(); ++i) {
        const Face& f = M.F[i];
        Point n = unit(face_normal(M, f));
        std::vector<Point2> uv;
        uv.reserve(f.size());
        for (int k : f) uv.push_back(fn(M.V[k], n));
        if (seam) {                                            // mend the seam
            if (uv.empty()) throw std::invalid_argument("max() arg is an empty sequence");
            double hi_u = uv[0][0], lo_u = uv[0][0];           // max(us), min(us)
            for (const Point2& t : uv) {
                if (t[0] > hi_u) hi_u = t[0];
                if (t[0] < lo_u) lo_u = t[0];
            }
            if (hi_u - lo_u > 0.5 * s)
                for (Point2& t : uv) t = Point2{t[0] < (lo_u + hi_u) / 2.0 ? t[0] + s : t[0], t[1]};
        }
        out.UV.push_back(uv);
        const Color& base = color ? *color : M.C[i];
        Color c(base.r, base.g, base.b, M.C[i].alpha);         // (the tint's own opacity is not used)
        c.image = image;
        out.C[i] = c;
    }
    return out;
}

}  // namespace detail

inline Mesh texture(const Mesh& M, const std::string& image, const std::string& mapping, double scale,
                    std::optional<Color> color, const Point2& offset) {
    return detail::texture_map(M, image, mapping, nullptr, scale, color, offset);
}
inline Mesh texture(const Mesh& M, const std::string& image, const TextureFn& mapping, double scale,
                    std::optional<Color> color, const Point2& offset) {
    return detail::texture_map(M, image, "", &mapping, scale, color, offset);
}

inline Mesh color_by(const Mesh& M, const std::function<Color(const Point&)>& fn) {
    Mesh out = M;
    for (size_t i = 0; i < M.F.size(); ++i) {
        const Face& f = M.F[i];
        if (f.empty()) throw std::domain_error("float division by zero");
        double n = (double)f.size();
        Point p;
        for (int a = 0; a < 3; ++a) {
            double s = 0.0;                                     // (add.py's _total: in order)
            for (int k : f) s = s + M.V[k][a];
            p[a] = s / n;
        }
        out.C[i] = fn(p);
    }
    return out;
}

inline Mesh color_gradient(const Mesh& M, const Color& a, const Color& b, int axis) {
    std::array<Point, 2> bb = bbox(M);
    const Point lo = bb[0], hi = bb[1];
    int ax = (int)detail::seq_index(axis, 3);
    double span = hi[ax] - lo[ax];
    if (span < EPS) return color(M, a);
    return color_by(M, [&](const Point& p) { return gradient((p[ax] - lo[ax]) / span, a, b); });
}

inline Mesh color_random(const Mesh& M, std::optional<long long> seed) {
    Random local = seed ? Random(*seed) : Random(0);
    Random& r = seed ? local : detail::rng();
    Mesh out = M;
    out.C.clear();
    for (size_t i = 0; i < M.F.size(); ++i) {
        int cr = (int)r.randint(0, 255);                       // (red, then green, then blue)
        int cg = (int)r.randint(0, 255);
        int cb = (int)r.randint(0, 255);
        out.C.push_back(Color(cr, cg, cb));
    }
    return out;
}

inline std::vector<std::pair<Color, int>> palette(const Mesh& M) {
    std::vector<std::pair<Color, int>> count;                  // in the order the colours first came
    std::unordered_map<Color, size_t, ColorHash> where;
    for (const Color& c : M.C) {
        auto it = where.find(c);
        if (it == where.end()) {
            where.emplace(c, count.size());
            count.push_back({c, 1});
        } else {
            count[it->second].second += 1;
        }
    }
    std::stable_sort(count.begin(), count.end(),               // most used first, then by colour
                     [](const std::pair<Color, int>& x, const std::pair<Color, int>& y) {
                         if (x.second != y.second) return x.second > y.second;
                         return detail::color_tuple_less(x.first, y.first);
                     });
    return count;
}
inline std::vector<std::pair<Color, int>> palette() { return palette(scene()); }

inline Mesh limit_colors(const Mesh& M, int n) {
    using Item = std::pair<Color, int>;                        // a colour and how many faces use it
    auto channel = [](const Color& c, int axis) { return axis == 0 ? c.r : (axis == 1 ? c.g : c.b); };
    std::vector<Item> counts;                                  // (a dict: in the order the colours came)
    std::unordered_map<Color, size_t, ColorHash> where;
    for (const Color& c : M.C) {
        if (c.alpha < 1.0 || !c.image.empty()) continue;       // transparent and textured materials are left alone
        auto it = where.find(c);
        if (it == where.end()) {
            where.emplace(c, counts.size());
            counts.push_back({c, 1});
        } else {
            counts[it->second].second += 1;
        }
    }
    if ((long long)counts.size() <= n) return M;
    std::vector<std::vector<Item>> boxes{counts};
    while ((long long)boxes.size() < n) {
        // Split the box whose colours spread the most (weighted by use).
        long long best = -1;
        int best_span = -1, best_axis = 0;
        for (size_t bi = 0; bi < boxes.size(); ++bi) {
            const std::vector<Item>& b = boxes[bi];
            if (b.size() < 2) continue;
            for (int axis = 0; axis < 3; ++axis) {
                int top = channel(b[0].first, axis), bottom = top;
                for (const Item& it : b) {
                    top = std::max(top, channel(it.first, axis));
                    bottom = std::min(bottom, channel(it.first, axis));
                }
                int span = top - bottom;
                if (span > best_span) {
                    best = (long long)bi;
                    best_span = span;
                    best_axis = axis;
                }
            }
        }
        if (best < 0) break;
        std::vector<Item> chosen = boxes[(size_t)best];
        std::stable_sort(chosen.begin(), chosen.end(), [&](const Item& x, const Item& y) {
            return channel(x.first, best_axis) < channel(y.first, best_axis);
        });
        long long total = 0;
        for (const Item& it : chosen) total += it.second;
        long long acc = 0;
        size_t cut = 0;                                        // (Python's loop variable: the last value it took)
        for (size_t c = 0; c + 1 < chosen.size(); ++c) {
            cut = c;
            acc += chosen[c].second;
            if (acc * 2 >= total) break;
        }
        boxes.erase(boxes.begin() + best);
        boxes.push_back(std::vector<Item>(chosen.begin(), chosen.begin() + (long)(cut + 1)));
        boxes.push_back(std::vector<Item>(chosen.begin() + (long)(cut + 1), chosen.end()));
    }
    std::unordered_map<Color, Color, ColorHash> remap;
    for (const std::vector<Item>& b : boxes) {
        long long weight = 0;
        for (const Item& it : b) weight += it.second;
        double total = (double)weight;
        int mean[3];
        for (int a = 0; a < 3; ++a) {
            long long sum = 0;
            for (const Item& it : b) sum += (long long)channel(it.first, a) * it.second;
            mean[a] = (int)std::nearbyint((double)sum / total);  // round(): half to even
        }
        for (const Item& it : b) remap[it.first] = Color(mean[0], mean[1], mean[2]);
    }
    Mesh out = M;
    for (Color& c : out.C) {
        auto it = remap.find(c);
        if (it != remap.end()) c = it->second;
    }
    return out;
}

inline Mesh repeat(const Mesh& M, int n, const std::function<Mesh(const Mesh&, int)>& step) {
    Mesh out;
    for (int i = 0; i < n; ++i) out.extend(step(M, i));
    return out;
}

inline Mesh array_linear(const Mesh& M, const Point& step, int n) {
    return repeat(M, n, [&](const Mesh& X, int i) { return move(X, {step[0] * i, step[1] * i, step[2] * i}); });
}

inline Mesh array_grid(const Mesh& M, const Point& steps, const std::array<int, 3>& counts) {
    Mesh out;
    for (int i = 0; i < counts[0]; ++i)
        for (int j = 0; j < counts[1]; ++j)
            for (int k = 0; k < counts[2]; ++k) out.extend(move(M, {steps[0] * i, steps[1] * j, steps[2] * k}));
    return out;
}

inline Mesh array_radial(const Mesh& M, int n, const Point& axis, const Point& P, double angle, double rise) {
    return repeat(M, n, [&](const Mesh& X, int i) {
        return move(rotate(X, axis, angle * i / (double)n, P), detail::scale(detail::unit(axis), rise * i));
    });
}

inline Mesh array_mirror(const Mesh& M, const Point& point, const Point& normal) {
    return merge({M, mirror(M, point, normal)});
}

}  // namespace add

namespace add {

inline Mesh aim(const Mesh& M, const Point& direction, const Point& axis, const Point& P) {
    Point a = detail::unit(axis), b = detail::unit(direction);
    Point c = cross(a, b);
    double s = detail::norm(c), d = dot(a, b);
    if (s < 1e-12) {
        if (d > 0) return M;
        return rotate(M, detail::perp(a), pi, P);
    }
    return rotate(M, c, std::atan2(s, d), P);
}

inline Mesh ground(const Mesh& M, double y) {
    std::array<Point, 2> bb = bbox(M);
    return move(M, {0.0, y - bb[0][1], 0.0});
}

inline Mesh align(const Mesh& M, const Point& at, const Point& anchor) {
    std::array<Point, 2> bb = bbox(M);
    const Point& lo = bb[0];
    const Point& hi = bb[1];
    Point shift;
    for (int a = 0; a < 3; ++a) {
        double p;
        if (anchor[a] < 0) p = lo[a];
        else if (anchor[a] > 0) p = hi[a];
        else p = (lo[a] + hi[a]) / 2.0;
        shift[a] = at[a] - p;
    }
    return move(M, shift);
}

inline Points random_points(int n, const Point& lo, const Point& hi, std::optional<long long> seed,
                            const std::function<double(double, double)>& height) {
    Random local = seed ? Random(*seed) : Random(0);
    Random& rnd = seed ? local : detail::rng();
    Points out;
    for (int i = 0; i < n; ++i) {
        double x = rnd.uniform(lo[0], hi[0]);                  // (x, then z, then y)
        double z = rnd.uniform(lo[2], hi[2]);
        double y = height ? height(x, z) : rnd.uniform(lo[1], hi[1]);
        out.push_back({x, y, z});
    }
    return out;
}

inline Mesh scatter(const Mesh& M, const Points& points, std::optional<long long> seed, bool spin,
                    const Point2& scale, const Point& axis) {
    Random local = seed ? Random(*seed) : Random(0);
    Random& rnd = seed ? local : detail::rng();
    Mesh out;
    for (const Point& p : points) {
        double s = rnd.uniform(scale[0], scale[1]);
        Mesh X = std::fabs(s - 1.0) > EPS ? zoom(M, s, Point{0, 0, 0}) : M;
        if (spin) {
            double angle = rnd.uniform(0, 2 * pi);
            X = rotate(X, axis, angle);
        }
        out.extend(move(X, p));
    }
    return out;
}

namespace detail {
inline Mesh along_copies(const Mesh& M, const Points& pts, const std::vector<double>& ts, const Points& dirs,
                         const std::optional<Point>& axis, const Scalar& scale) {
    Mesh out;
    for (size_t i = 0; i < pts.size() && i < ts.size() && i < dirs.size(); ++i) {
        Mesh X = M;
        if (scale) {
            double s = scale(ts[i]);
            X = zoom(X, s, Point{0, 0, 0});
        }
        if (axis && norm(dirs[i]) > EPS) X = aim(X, dirs[i], *axis);
        out.extend(move(X, pts[i]));
    }
    return out;
}
}  // namespace detail

inline Mesh along(const Mesh& M, const std::function<Point(double)>& path, int n, double t0, double t1,
                  std::optional<Point> axis, bool closed, const Scalar& scale) {
    int steps = closed ? n : std::max(1, n - 1);
    std::vector<double> ts;
    for (int i = 0; i < n; ++i) ts.push_back(t0 + (t1 - t0) * i / (double)steps);
    Points pts;
    for (double t : ts) pts.push_back(path(t));
    double h = (t1 - t0) * 1e-4;
    Points dirs;
    for (double t : ts) {
        Point ahead = path(t + h);                             // (in this order, as add.py calls them)
        Point behind = path(t - h);
        dirs.push_back(detail::sub(ahead, behind));
    }
    return detail::along_copies(M, pts, ts, dirs, axis, scale);
}

inline Mesh along(const Mesh& M, const Points& path, int, double, double, std::optional<Point> axis, bool closed,
                  const Scalar& scale) {
    const Points& pts = path;
    int n = (int)pts.size();
    std::vector<double> ts;
    for (int i = 0; i < n; ++i) ts.push_back(i / (double)(closed ? n : std::max(1, n - 1)));
    Points dirs;
    for (int i = 0; i < n; ++i) {
        const Point& a = (i > 0 || closed) ? pts[(size_t)((i - 1 + n) % n)] : pts[(size_t)i];
        const Point& b = (i < n - 1 || closed) ? pts[(size_t)((i + 1) % n)] : pts[(size_t)i];
        dirs.push_back(detail::sub(b, a));
    }
    return detail::along_copies(M, pts, ts, dirs, axis, scale);
}

}  // namespace add

namespace add {

namespace detail {

struct CellKey {
    long long i, j, k;
    bool operator==(const CellKey& o) const { return i == o.i && j == o.j && k == o.k; }
};
struct CellKeyHash {
    size_t operator()(const CellKey& c) const {
        uint64_t h = (uint64_t)c.i * 0x9E3779B97F4A7C15ull;
        h ^= (uint64_t)c.j * 0xC2B2AE3D27D4EB4Full + (h << 6) + (h >> 2);
        h ^= (uint64_t)c.k * 0x165667B19E3779F9ull + (h << 6) + (h >> 2);
        return (size_t)h;
    }
};

inline long long cell_floor(double x) {
    if (std::isnan(x)) throw std::invalid_argument("cannot convert float NaN to integer");
    if (std::isinf(x)) throw std::overflow_error("cannot convert float infinity to integer");
    double f = std::floor(x);
    // Python's integers have no limit; a cell number beyond 64 bits (a coordinate some
    // 1e12 times the tolerance) is refused here rather than silently wrapped round.
    // (Strictly inside the range, so that the neighbours k - 1 and k + 1 fit too.)
    if (!(f > -9223372036854775808.0 && f < 9223372036854775808.0))
        throw std::overflow_error("cell number out of the 64-bit range: coordinates too large for the tolerance");
    return (long long)f;
}

inline double key_round(double x) {
    if (std::isnan(x)) throw std::invalid_argument("cannot convert float NaN to integer");
    if (std::isinf(x)) throw std::overflow_error("cannot convert float infinity to integer");
    return std::nearbyint(x) + 0.0;                            // (a whole number: never -0.0)
}

//: Grid cell(s) a point may belong to, allowing for rounding at the edges.
inline std::vector<CellKey> cell_keys(const Point& p, double tol) {
    std::vector<long long> ranges[3];
    for (int a = 0; a < 3; ++a) {
        double q = p[a] / tol;
        long long k = cell_floor(q + 0.5);                     // (NaN, inf: an exception, as in add.py)
        double frac = q + 0.5 - std::floor(q + 0.5);
        if (frac < 0.25) ranges[a] = {k, k - 1};
        else if (frac > 0.75) ranges[a] = {k, k + 1};
        else ranges[a] = {k};
    }
    std::vector<CellKey> out;
    for (long long i : ranges[0])
        for (long long j : ranges[1])
            for (long long k : ranges[2]) out.push_back({i, j, k});
    return out;
}

inline int weld(Mesh& M, double tol) {
    std::unordered_map<CellKey, int, CellKeyHash> lookup;
    std::vector<int> remap(M.V.size(), 0);
    std::vector<Point> newV;
    for (size_t i = 0; i < M.V.size(); ++i) {
        const Point& p = M.V[i];
        int found = -1;
        std::vector<CellKey> keys = cell_keys(p, tol);
        for (const CellKey& key : keys) {
            auto it = lookup.find(key);
            if (it != lookup.end()) {
                const Point& q = newV[it->second];
                if (std::fabs(q[0] - p[0]) <= tol && std::fabs(q[1] - p[1]) <= tol && std::fabs(q[2] - p[2]) <= tol) {
                    found = it->second;
                    break;
                }
            }
        }
        if (found < 0) {
            found = (int)newV.size();
            newV.push_back(p);
            for (const CellKey& key : keys) lookup.emplace(key, found);
        }
        remap[i] = found;
    }
    int removed = (int)(M.V.size() - newV.size());
    M.V = std::move(newV);
    for (Face& f : M.F)
        for (int& i : f) i = remap[i];
    return removed;
}

inline std::vector<int> weld_map(const std::vector<Point>& V, double tol) {
    std::unordered_map<CellKey, int, CellKeyHash> lookup;
    std::vector<int> rep(V.size(), 0);
    for (size_t i = 0; i < V.size(); ++i) {
        const Point& p = V[i];
        int found = -1;
        std::vector<CellKey> keys = cell_keys(p, tol);
        for (const CellKey& key : keys) {
            auto it = lookup.find(key);
            if (it != lookup.end()) {
                const Point& q = V[it->second];
                if (std::fabs(q[0] - p[0]) <= tol && std::fabs(q[1] - p[1]) <= tol && std::fabs(q[2] - p[2]) <= tol) {
                    found = it->second;
                    break;
                }
            }
        }
        if (found < 0) {
            found = (int)i;
            for (const CellKey& key : keys) lookup.emplace(key, found);
        }
        rep[i] = found;
    }
    return rep;
}

inline std::pair<double, double> piece_volume(const Mesh& M, const std::vector<int>& faces, const std::vector<int>& rep) {
    std::set<int> corners;
    for (int fi : faces)
        for (int i : M.F[fi]) corners.insert(rep[i]);
    double n = (double)corners.size();
    double c[3], size = 0.0;
    for (int a = 0; a < 3; ++a) {
        double s = 0.0, lo = 0.0, hi = 0.0;
        bool first = true;
        for (int i : corners) {
            double v = M.V[i][a];
            s = s + v;
            if (first || v < lo) lo = v;
            if (first || v > hi) hi = v;
            first = false;
        }
        c[a] = s / n;
        if (a == 0 || hi - lo > size) size = hi - lo;
    }
    double total = 0.0;
    for (int fi : faces) {
        const Face& f = M.F[fi];
        if (f.size() < 3) continue;
        double a[3] = {M.V[f[0]][0] - c[0], M.V[f[0]][1] - c[1], M.V[f[0]][2] - c[2]};
        for (size_t t = 1; t + 1 < f.size(); ++t) {
            double b[3] = {M.V[f[t]][0] - c[0], M.V[f[t]][1] - c[1], M.V[f[t]][2] - c[2]};
            double d[3] = {M.V[f[t + 1]][0] - c[0], M.V[f[t + 1]][1] - c[1], M.V[f[t + 1]][2] - c[2]};
            total += (a[0] * (b[1] * d[2] - b[2] * d[1])
                      - a[1] * (b[0] * d[2] - b[2] * d[0])
                      + a[2] * (b[0] * d[1] - b[1] * d[0]));
        }
    }
    return {total, std::pow(size, 3.0)};
}

inline int keep_faces(Mesh& M, const std::vector<int>& keep) {
    int removed = (int)M.F.size() - (int)keep.size();
    std::vector<Face> F;
    std::vector<Color> C;
    std::vector<std::vector<Point2>> UV;
    F.reserve(keep.size());
    C.reserve(keep.size());
    for (int i : keep) {
        F.push_back(std::move(M.F[i]));
        C.push_back(M.C[i]);
        if (M.has_uv) UV.push_back(M.UV[i]);
    }
    M.F = std::move(F);
    M.C = std::move(C);
    if (M.has_uv) M.UV = std::move(UV);
    return removed;
}

inline std::set<int> not_finite(const Mesh& M) {
    double total = 0.0;
    for (const Point& p : M.V) total += p[0] + p[1] + p[2];
    std::set<int> bad;
    if (std::isfinite(total)) return bad;
    for (size_t i = 0; i < M.V.size(); ++i) {
        const Point& p = M.V[i];
        if (!(std::isfinite(p[0]) && std::isfinite(p[1]) && std::isfinite(p[2]))) bad.insert((int)i);
    }
    return bad;
}

inline int drop_not_finite(Mesh& M) {
    std::set<int> bad = not_finite(M);
    if (bad.empty()) return 0;
    std::vector<int> keep;
    for (size_t k = 0; k < M.F.size(); ++k) {
        bool ok = true;
        for (int i : M.F[k])
            if (bad.count(i)) { ok = false; break; }
        if (ok) keep.push_back((int)k);
    }
    int removed = keep_faces(M, keep);
    std::vector<int> remap(M.V.size(), -1);
    std::vector<Point> newV;
    for (size_t i = 0; i < M.V.size(); ++i) {
        if (!bad.count((int)i)) {
            remap[i] = (int)newV.size();
            newV.push_back(M.V[i]);
        }
    }
    M.V = std::move(newV);
    for (Face& f : M.F)
        for (int& i : f) i = remap[i];
    return removed;
}

inline std::vector<std::pair<Face, std::vector<Point2>>> split_repeats(const Face& f, const std::vector<Point2>* uv) {
    Face clean_f;
    std::vector<Point2> clean_uv;
    for (size_t t = 0; t < f.size(); ++t) {                    // drop repeated corners
        int i = f[t];
        if (clean_f.empty() || clean_f.back() != i) {
            clean_f.push_back(i);
            if (uv) clean_uv.push_back((*uv)[t]);
        }
    }
    if (clean_f.size() > 1 && clean_f.front() == clean_f.back()) {
        clean_f.pop_back();
        if (uv) clean_uv.pop_back();
    }
    std::set<int> distinct(clean_f.begin(), clean_f.end());
    if (distinct.size() == clean_f.size()) return {{clean_f, clean_uv}};
    std::map<int, size_t> seen;
    for (size_t j = 0; j < clean_f.size(); ++j) {
        int i = clean_f[j];
        auto it = seen.find(i);
        if (it != seen.end()) {                                // pinch: split here
            size_t a = it->second;
            Face first(clean_f.begin() + a, clean_f.begin() + j);
            Face rest(clean_f.begin() + j, clean_f.end());
            rest.insert(rest.end(), clean_f.begin(), clean_f.begin() + a);
            std::vector<Point2> first_uv, rest_uv;
            if (uv) {
                first_uv.assign(clean_uv.begin() + a, clean_uv.begin() + j);
                rest_uv.assign(clean_uv.begin() + j, clean_uv.end());
                rest_uv.insert(rest_uv.end(), clean_uv.begin(), clean_uv.begin() + a);
            }
            auto out = split_repeats(first, uv ? &first_uv : nullptr);
            auto more = split_repeats(rest, uv ? &rest_uv : nullptr);
            out.insert(out.end(), more.begin(), more.end());
            return out;
        }
        seen[i] = j;
    }
    return {{clean_f, clean_uv}};
}

inline int drop_degenerate(Mesh& M, double tol) {
    std::vector<int> keep;
    std::vector<Face> extra_F;
    std::vector<Color> extra_C;
    std::vector<std::vector<Point2>> extra_UV;
    for (size_t k = 0; k < M.F.size(); ++k) {
        const std::vector<Point2>* uv = M.has_uv ? &M.UV[k] : nullptr;
        if (uv && uv->empty()) uv = nullptr;
        const Face& f = M.F[k];
        std::set<int> distinct(f.begin(), f.end());
        std::vector<std::pair<Face, std::vector<Point2>>> pieces;
        if (distinct.size() == f.size()) pieces.push_back({f, uv ? *uv : std::vector<Point2>()});
        else pieces = split_repeats(f, uv);
        bool first = true;
        for (auto& piece : pieces) {
            Face& clean_f = piece.first;
            std::set<int> d2(clean_f.begin(), clean_f.end());
            if (clean_f.size() < 3 || d2.size() < 3) continue;
            if (norm(face_normal(M, clean_f)) <= tol) continue;
            if (first) {
                M.F[k] = clean_f;
                if (uv) M.UV[k] = piece.second;
                keep.push_back((int)k);
                first = false;
            } else {                                           // a second loop of a pinched face
                extra_F.push_back(clean_f);
                extra_C.push_back(M.C[k]);
                extra_UV.push_back(piece.second);
            }
        }
    }
    int removed = keep_faces(M, keep);
    if (!extra_F.empty()) {
        M.F.insert(M.F.end(), extra_F.begin(), extra_F.end());
        M.C.insert(M.C.end(), extra_C.begin(), extra_C.end());
        if (M.has_uv) M.UV.insert(M.UV.end(), extra_UV.begin(), extra_UV.end());
        removed -= (int)extra_F.size();
    }
    return removed;
}

inline int dedup_faces(Mesh& M) {
    std::set<Face> seen;
    std::vector<int> keep;
    for (size_t k = 0; k < M.F.size(); ++k) {
        Face key = M.F[k];
        std::sort(key.begin(), key.end());
        if (seen.count(key)) continue;
        seen.insert(key);
        keep.push_back((int)k);
    }
    return keep_faces(M, keep);
}

inline bool winding(const Face& f) {
    if (f.empty()) throw std::invalid_argument("min() arg is an empty sequence");   // (as add.py)
    size_t k = (size_t)(std::min_element(f.begin(), f.end()) - f.begin());
    size_t n = f.size();
    return f[(k + 1) % n] < f[(k + n - 1) % n];
}

inline int drop_internal(Mesh& M) {
    std::map<Face, std::vector<int>> groups;
    std::vector<Face> order;                                   // (the keys in the order they first came)
    for (size_t i = 0; i < M.F.size(); ++i) {
        Face key = M.F[i];
        std::sort(key.begin(), key.end());
        auto it = groups.find(key);
        if (it == groups.end()) {
            groups[key] = {(int)i};
            order.push_back(key);
        } else {
            it->second.push_back((int)i);
        }
    }
    std::set<int> drop;
    for (const Face& key : order) {
        const std::vector<int>& idx = groups[key];
        if (idx.size() < 2) continue;
        std::vector<int> forward, backward;
        for (int i : idx) (winding(M.F[i]) ? forward : backward).push_back(i);
        size_t pairs = std::min(forward.size(), backward.size());
        for (size_t t = 0; t < pairs; ++t) {
            drop.insert(forward[t]);
            drop.insert(backward[t]);
        }
    }
    if (drop.empty()) return 0;
    std::vector<int> keep;
    for (size_t i = 0; i < M.F.size(); ++i)
        if (!drop.count((int)i)) keep.push_back((int)i);
    return keep_faces(M, keep);
}

inline int drop_unused(Mesh& M) {
    std::vector<char> used(M.V.size(), 0);
    size_t count = 0;
    for (const Face& f : M.F)
        for (int i : f)
            if (!used[i]) { used[i] = 1; ++count; }
    if (count == M.V.size()) return 0;
    std::vector<int> remap(M.V.size(), -1);
    std::vector<Point> newV;
    for (size_t i = 0; i < M.V.size(); ++i) {
        if (used[i]) {
            remap[i] = (int)newV.size();
            newV.push_back(M.V[i]);
        }
    }
    int removed = (int)(M.V.size() - newV.size());
    M.V = std::move(newV);
    for (Face& f : M.F)
        for (int& i : f) i = remap[i];
    return removed;
}

inline double poly_area2(const Profile& pts) {
    double a = 0.0;
    size_t n = pts.size();
    for (size_t i = 0; i < n; ++i) {
        double x0 = pts[i][0], y0 = pts[i][1];
        double x1 = pts[(i + 1) % n][0], y1 = pts[(i + 1) % n][1];
        a += x0 * y1 - x1 * y0;
    }
    return a;
}

// -- coplanar overlaps: the cause of flicker ("z-fighting") in viewers -------

inline Profile clip_half(const Profile& pts, const Point2& a, const Point2& b, bool keep_left) {
    double ax = a[0], ay = a[1];
    double bx = b[0], by = b[1];
    double ex = bx - ax, ey = by - ay;
    Profile out;
    size_t n = pts.size();
    if (n == 0) return out;
    Point2 prev = pts[n - 1];
    double prev_s = ex * (prev[1] - ay) - ey * (prev[0] - ax);
    for (const Point2& cur : pts) {
        double cur_s = ex * (cur[1] - ay) - ey * (cur[0] - ax);
        bool cur_in = keep_left ? cur_s >= 0 : cur_s <= 0;
        bool prev_in = keep_left ? prev_s >= 0 : prev_s <= 0;
        if (cur_in != prev_in) {
            double t = prev_s / (prev_s - cur_s);
            out.push_back({prev[0] + (cur[0] - prev[0]) * t, prev[1] + (cur[1] - prev[1]) * t});
        }
        if (cur_in) out.push_back(cur);
        prev = cur;
        prev_s = cur_s;
    }
    return out;
}

inline std::vector<Profile> convex_minus(const Profile& A, const Profile& B, double eps, bool* untouched) {
    if (untouched) *untouched = true;
    size_t nb = B.size();
    Profile inside = A;
    for (size_t i = 0; i < nb; ++i) {
        inside = clip_half(inside, B[i], B[(i + 1) % nb], true);
        if (inside.size() < 3) return {A};
    }
    if (std::fabs(poly_area2(inside)) <= eps) return {A};
    if (untouched) *untouched = false;
    std::vector<Profile> pieces;
    Profile current = A;
    for (size_t i = 0; i < nb; ++i) {
        const Point2& a = B[i];
        const Point2& b = B[(i + 1) % nb];
        Profile outside = clip_half(current, a, b, false);
        if (outside.size() >= 3 && std::fabs(poly_area2(outside)) > eps) pieces.push_back(outside);
        current = clip_half(current, a, b, true);
        if (current.size() < 3) break;
    }
    return pieces;
}

inline std::vector<Profile> ears(const Profile& pts) {
    std::vector<int> idx(pts.size());
    std::iota(idx.begin(), idx.end(), 0);
    std::vector<Profile> tris;
    long long guard = 0;
    while (idx.size() > 3 && guard < 10 * (long long)pts.size()) {
        guard += 1;
        int n = (int)idx.size();
        bool found = false;
        for (int k = 0; k < n; ++k) {
            int i0 = idx[(k + n - 1) % n], i1 = idx[k], i2 = idx[(k + 1) % n];
            const Point2& a = pts[i0];
            const Point2& b = pts[i1];
            const Point2& c = pts[i2];
            if ((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) <= 0)
                continue;                                      // a reflex corner, not an ear
            bool ok = true;
            for (int j : idx) {
                if (j == i0 || j == i1 || j == i2) continue;
                const Point2& p = pts[j];
                double s1 = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]);
                double s2 = (c[0] - b[0]) * (p[1] - b[1]) - (c[1] - b[1]) * (p[0] - b[0]);
                double s3 = (a[0] - c[0]) * (p[1] - c[1]) - (a[1] - c[1]) * (p[0] - c[0]);
                if (s1 > 0 && s2 > 0 && s3 > 0) {
                    ok = false;
                    break;
                }
            }
            if (ok) {
                tris.push_back({a, b, c});
                idx.erase(idx.begin() + k);
                found = true;
                break;
            }
        }
        if (!found) break;
    }
    if (idx.size() == 3) tris.push_back({pts[idx[0]], pts[idx[1]], pts[idx[2]]});
    return tris;
}

inline std::vector<Profile> convex_pieces(const Profile& pts) {
    size_t n = pts.size();
    for (size_t i = 0; i < n; ++i) {
        const Point2& a = pts[(i + n - 1) % n];
        const Point2& b = pts[i];
        const Point2& c = pts[(i + 1) % n];
        if ((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) < 0) return ears(pts);
    }
    return {pts};
}

inline std::optional<std::vector<std::array<int, 3>>> ear_triangles(const Profile& pts) {
    std::vector<int> idx(pts.size());
    std::iota(idx.begin(), idx.end(), 0);
    std::vector<std::array<int, 3>> tris;
    while (idx.size() > 3) {
        int n = (int)idx.size();
        bool cut = false;
        for (int k = 0; k < n; ++k) {
            int i0 = idx[(k + n - 1) % n], i1 = idx[k], i2 = idx[(k + 1) % n];
            const Point2& a = pts[i0];
            const Point2& b = pts[i1];
            const Point2& c = pts[i2];
            if ((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) <= 0)
                continue;                                      // a reflex (or straight) corner is no ear
            bool blocked = false;
            for (int j : idx) {
                if (j == i0 || j == i1 || j == i2) continue;
                const Point2& q = pts[j];
                if ((b[0] - a[0]) * (q[1] - a[1]) - (b[1] - a[1]) * (q[0] - a[0]) >= 0 &&
                    (c[0] - b[0]) * (q[1] - b[1]) - (c[1] - b[1]) * (q[0] - b[0]) >= 0 &&
                    (a[0] - c[0]) * (q[1] - c[1]) - (a[1] - c[1]) * (q[0] - c[0]) >= 0) {
                    blocked = true;                            // another corner inside: cutting here would overlap
                    break;
                }
            }
            if (!blocked) {
                tris.push_back({i0, i1, i2});
                idx.erase(idx.begin() + k);
                cut = true;
                break;
            }
        }
        if (!cut) return std::nullopt;
    }
    if (idx.size() < 3) throw std::out_of_range("list index out of range");   // (add.py: an IndexError)
    tris.push_back({idx[0], idx[1], idx[2]});
    return tris;
}

inline bool is_concave(const Mesh& M, const Face& f, std::optional<Point> n_) {
    size_t k = f.size();
    if (k < 4) return false;
    Point n = n_ ? *n_ : face_normal(M, f);
    double ln = std::sqrt(n[0] * n[0] + n[1] * n[1] + n[2] * n[2]);
    if (ln < 1e-12) return false;
    double nx = n[0] / ln, ny = n[1] / ln, nz = n[2] / ln;
    Points P;
    P.reserve(k);
    for (int i : f) P.push_back(M.V[i]);
    for (size_t i = 0; i < k; ++i) {
        const Point& a = P[(i + k - 1) % k];
        const Point& b = P[i];
        const Point& c = P[(i + 1) % k];
        double e1x = b[0] - a[0], e1y = b[1] - a[1], e1z = b[2] - a[2];
        double e2x = c[0] - b[0], e2y = c[1] - b[1], e2z = c[2] - b[2];
        double turn = ((e1y * e2z - e1z * e2y) * nx + (e1z * e2x - e1x * e2z) * ny + (e1x * e2y - e1y * e2x) * nz);
        if (turn < -1e-9 * (e1x * e1x + e1y * e1y + e1z * e1z + e2x * e2x + e2y * e2y + e2z * e2z)) return true;
    }
    return false;
}

inline int split_concave(Mesh& M) {
    std::vector<Face> newF;
    std::vector<Color> newC;
    std::vector<std::vector<Point2>> newUV;
    int count = 0;
    for (size_t k = 0; k < M.F.size(); ++k) {
        const Face& f = M.F[k];
        std::optional<std::vector<std::array<int, 3>>> tris;
        if (f.size() > 3) {
            Point n = face_normal(M, f);
            if (is_concave(M, f, n)) {
                Frame fr = frame(n);
                Profile pts;
                for (int i : f) pts.push_back({dot(M.V[i], fr.u), dot(M.V[i], fr.v)});
                std::vector<int> order(f.size());
                std::iota(order.begin(), order.end(), 0);
                bool flip = poly_area2(pts) < 0;
                if (flip) {
                    std::reverse(order.begin(), order.end());
                    std::reverse(pts.begin(), pts.end());
                }
                auto found = ear_triangles(pts);
                if (found) {
                    tris.emplace();
                    for (const auto& ear : *found) {
                        std::array<int, 3> t = {order[ear[0]], order[ear[1]], order[ear[2]]};
                        if (flip) std::reverse(t.begin(), t.end());
                        tris->push_back(t);
                    }
                }
            }
        }
        const std::vector<Point2> none;
        const std::vector<Point2>& uv = M.has_uv ? M.UV[k] : none;   // (empty: add.py's None)
        if (!tris) {
            newF.push_back(f);
            newC.push_back(M.C[k]);
            newUV.push_back(uv);
            continue;
        }
        count += 1;
        for (const auto& t : *tris) {
            newF.push_back({f[t[0]], f[t[1]], f[t[2]]});
            newC.push_back(M.C[k]);
            newUV.push_back(uv.empty() ? std::vector<Point2>()
                                       : std::vector<Point2>{uv.at(t[0]), uv.at(t[1]), uv.at(t[2])});
        }
    }
    if (count) {
        M.F = std::move(newF);
        M.C = std::move(newC);
        if (M.has_uv) M.UV = std::move(newUV);
    }
    return count;
}

inline std::vector<PlaneGroup> overlap_groups(const Mesh& M, double tol) {
    // add.py's dict {key: [face, ...]}: the keys in the order they first came (a key
    // equal to an earlier one -- 0.0 and -0.0 are equal -- joins that one's group).
    std::map<std::array<double, 4>, size_t> where;
    std::vector<std::pair<std::array<double, 4>, std::vector<int>>> groups;
    std::map<int, std::pair<Point, double>> planes;            // each face's own plane
    for (size_t i = 0; i < M.F.size(); ++i) {
        const Face& f = M.F[i];
        if (f.size() < 3) continue;
        Point n = face_normal(M, f);
        double ln = norm(n);
        if (ln < 1e-12) continue;
        n = {n[0] / ln, n[1] / ln, n[2] / ln};
        Point c{0.0, 0.0, 0.0};
        for (int k : f) {
            const Point& p = M.V[k];
            c[0] += p[0];
            c[1] += p[1];
            c[2] += p[2];
        }
        double d = dot(n, c) / (double)f.size();
        planes[(int)i] = {n, d};
        std::array<double, 3> nk = {py_round(n[0], 3), py_round(n[1], 3), py_round(n[2], 3)};
        bool below = false;                                    // nk < (0, 0, 0) as Python compares tuples
        for (int a = 0; a < 3; ++a)
            if (nk[a] != 0.0) {
                below = nk[a] < 0.0;
                break;
            }
        bool zero = nk[0] == 0.0 && nk[1] == 0.0 && nk[2] == 0.0;
        if (below || (zero && n[2] < 0)) {                     // one key for both sides of a plane
            nk = {-nk[0] + 0.0, -nk[1] + 0.0, -nk[2] + 0.0};
            d = -d;
        }
        std::array<double, 4> key = {nk[0], nk[1], nk[2], key_round(d / tol) * tol};
        auto it = where.find(key);
        if (it == where.end()) {
            where.emplace(key, groups.size());
            groups.push_back({key, {(int)i}});
        } else {
            groups[it->second].second.push_back((int)i);
        }
    }
    std::vector<PlaneGroup> out;
    for (const auto& g : groups) {
        const std::vector<int>& idx = g.second;
        if (idx.size() < 2) continue;
        PlaneGroup G;
        G.key = g.first;
        G.n = unit({g.first[0], g.first[1], g.first[2]});
        Frame fr = frame(G.n);
        G.u = fr.u;
        G.v = fr.v;
        for (int i : idx) {
            Profile pts;
            for (int k : M.F[i]) pts.push_back({dot(M.V[k], G.u), dot(M.V[k], G.v)});
            double area2 = poly_area2(pts);
            bool flipped = area2 < 0;
            if (flipped) {
                std::reverse(pts.begin(), pts.end());
                area2 = -area2;
            }
            double x0 = pts[0][0], y0 = pts[0][1], x1 = pts[0][0], y1 = pts[0][1];
            for (const Point2& p : pts) {                      // (Python's min / max: the first of equals)
                if (p[0] < x0) x0 = p[0];
                if (p[1] < y0) y0 = p[1];
                if (p[0] > x1) x1 = p[0];
                if (p[1] > y1) y1 = p[1];
            }
            PlanePoly P;
            P.area = area2 / 2.0;
            P.index = i;
            P.pts = std::move(pts);
            P.bb = {x0, y0, x1, y1};
            P.flipped = flipped;
            P.pn = planes[i].first;
            P.pd = planes[i].second;
            G.polys.push_back(std::move(P));
        }
        out.push_back(std::move(G));
    }
    return out;
}

inline bool same_plane(const Mesh& M, const PlanePoly& A, const PlanePoly& B, double tol) {
    for (int k : M.F[A.index])
        if (std::fabs(dot(B.pn, M.V[k]) - B.pd) > tol) return false;
    for (int k : M.F[B.index])
        if (std::fabs(dot(A.pn, M.V[k]) - A.pd) > tol) return false;
    return true;
}

inline double convex_overlap2(const Profile& A, const Profile& B) {
    size_t nb = B.size();
    Profile inside = A;
    for (size_t i = 0; i < nb; ++i) {
        inside = clip_half(inside, B[i], B[(i + 1) % nb], true);
        if (inside.size() < 3) return 0.0;
    }
    return std::fabs(poly_area2(inside));
}

inline std::optional<std::vector<Profile>> minus_all(std::vector<Profile> pieces, const std::vector<Profile>& others,
                                                     double eps, size_t limit) {
    for (const Profile& other : others) {
        std::vector<Profile> next;
        for (const Profile& part : pieces) {
            std::vector<Profile> q = convex_minus(part, other, eps);
            next.insert(next.end(), q.begin(), q.end());
        }
        pieces = std::move(next);
        if (pieces.size() > limit) return std::nullopt;
    }
    return pieces;
}

inline OverlapScan overlap_scan(const Mesh& M, double tol, bool cut) {
    std::set<int> touched;
    std::vector<std::pair<int, CutFace>> replaced;             // add.py's dict: in the order the keys first came
    std::map<int, size_t> replaced_at;
    auto replace = [&](int i, CutFace r) {
        auto it = replaced_at.find(i);
        if (it == replaced_at.end()) {
            replaced_at.emplace(i, replaced.size());
            replaced.push_back({i, std::move(r)});
        } else {
            replaced[it->second].second = std::move(r);         // (a dict keeps a key where it first came)
        }
    };
    for (PlaneGroup& G : overlap_groups(M, tol)) {
        std::vector<PlanePoly>& polys = G.polys;
        std::stable_sort(polys.begin(), polys.end(),
                         [](const PlanePoly& a, const PlanePoly& b) { return -a.area < -b.area; });
        double largest = polys[0].area;
        double eps = 1e-9 * (1.0 + largest);
        double cell = std::max(1e-6, std::sqrt(std::max(1e-12, polys[polys.size() / 2].area)) * 2.0);
        std::unordered_map<CellKey, std::vector<int>, CellKeyHash> grid;    // (cx, cy) -> faces
        std::vector<int> big;                                  // a few big faces: checked against everyone
        std::map<int, std::vector<Profile>> drawn;             // face -> its convex pieces as drawn
        std::map<int, std::vector<Profile>> current;           // face -> its pieces now
        std::map<int, bool> flip;
        std::map<int, std::array<double, 4>> box;              // face -> its bounding box
        std::map<int, const PlanePoly*> poly_of;               // face -> its entry (its own plane)
        std::vector<std::pair<int, std::vector<int>>> contacts;   // bigger face -> smaller faces on its back
        std::map<int, size_t> contacts_at;

        auto cells = [&](const std::array<double, 4>& bb) {
            return std::array<long long, 4>{cell_floor(bb[0] / cell), cell_floor(bb[1] / cell),
                                            cell_floor(bb[2] / cell), cell_floor(bb[3] / cell)};
        };
        auto keep = [&](int entry, const std::array<double, 4>& bb) {
            std::array<long long, 4> c = cells(bb);
            if (((double)c[2] - (double)c[0] + 1.0) * ((double)c[3] - (double)c[1] + 1.0) > 400) {   // (cannot overflow)
                big.push_back(entry);
                return;
            }
            for (long long cx = c[0]; cx <= c[2]; ++cx)
                for (long long cy = c[1]; cy <= c[3]; ++cy) grid[CellKey{cx, cy, 0}].push_back(entry);
        };

        for (const PlanePoly& P : polys) {
            const int i = P.index;
            const std::array<double, 4>& bb = P.bb;
            const bool flipped = P.flipped;
            std::array<long long, 4> c = cells(bb);
            std::set<int> seen;
            std::vector<int> candidates = big;
            for (long long cx = c[0]; cx <= c[2]; ++cx)
                for (long long cy = c[1]; cy <= c[3]; ++cy) {
                    auto it = grid.find(CellKey{cx, cy, 0});
                    if (it == grid.end()) continue;
                    for (int entry : it->second)
                        if (seen.insert(entry).second) candidates.push_back(entry);
                }
            std::vector<Profile> own = convex_pieces(P.pts);   // the face as it was drawn
            std::vector<Profile> pieces = own;
            bool changed = false;
            for (int k : candidates) {
                const std::array<double, 4>& kbb = box[k];
                if (bb[0] >= kbb[2] || bb[2] <= kbb[0] || bb[1] >= kbb[3] || bb[3] <= kbb[1]) continue;
                if (!same_plane(M, P, *poly_of[k], 1.5 * tol)) continue;
                const std::vector<Profile>& kpieces = drawn[k];
                if (flip[k] != flipped) {                      // back to back: remember the contact
                    bool any = false;
                    for (const Profile& a : pieces) {
                        for (const Profile& b : kpieces)
                            if (convex_overlap2(a, b) > eps) {
                                any = true;
                                break;
                            }
                        if (any) break;
                    }
                    if (any) {
                        auto it = contacts_at.find(k);
                        if (it == contacts_at.end()) {
                            contacts_at.emplace(k, contacts.size());
                            contacts.push_back({k, {i}});
                        } else {
                            contacts[it->second].second.push_back(i);
                        }
                    }
                    continue;
                }
                std::vector<Profile> new_pieces;
                for (const Profile& piece : pieces) {
                    // ``parts`` stays the very list [piece] (add.py tests ``parts[0] is piece``)
                    // for as long as every subtraction gives the piece back untouched.
                    bool same = true;
                    std::vector<Profile> parts;
                    for (const Profile& other : kpieces) {
                        if (same) {
                            bool untouched = true;
                            std::vector<Profile> q = convex_minus(piece, other, eps, &untouched);
                            if (!untouched) {
                                same = false;
                                parts = std::move(q);
                            }
                        } else {
                            std::vector<Profile> next;
                            for (const Profile& part : parts) {
                                std::vector<Profile> q = convex_minus(part, other, eps);
                                next.insert(next.end(), q.begin(), q.end());
                            }
                            parts = std::move(next);
                        }
                    }
                    if (same) {
                        new_pieces.push_back(piece);
                    } else {
                        changed = true;
                        new_pieces.insert(new_pieces.end(), parts.begin(), parts.end());
                    }
                }
                pieces = std::move(new_pieces);
                if (changed && (!cut || pieces.size() > 64)) break;
            }
            if (changed) {
                touched.insert(i);
                if (cut && pieces.size() <= 64) replace(i, CutFace{pieces, G.u, G.v, G.n, G.key[3], flipped});
            }
            // later, smaller faces are cut against the face as drawn: the same
            // result as against its pieces, with far less to compare
            bool keep_pieces = cut && pieces.size() <= 64;
            drawn[i] = own;
            current[i] = keep_pieces ? pieces : own;
            flip[i] = flipped;
            box[i] = bb;
            poly_of[i] = &P;
            keep(i, bb);
        }
        for (const auto& contact : contacts) {                 // the patches where solids touch
            int k = contact.first;
            const std::vector<int>& small = contact.second;
            if (!cut) {
                touched.insert(k);
                touched.insert(small.begin(), small.end());
                continue;
            }
            std::vector<Profile> others;
            for (int i : small)
                for (const Profile& q : current[i]) others.push_back(q);
            std::optional<std::vector<Profile>> rest = minus_all(current[k], others, eps);
            if (!rest) continue;                               // the bigger face would shatter: leave the contact
            replace(k, CutFace{*rest, G.u, G.v, G.n, G.key[3], flip[k]});
            current[k] = *rest;
            touched.insert(k);
            for (int i : small) {
                std::optional<std::vector<Profile>> left = minus_all(current[i], drawn[k], eps);
                if (left) {
                    replace(i, CutFace{*left, G.u, G.v, G.n, G.key[3], flip[i]});
                    current[i] = *left;
                    touched.insert(i);
                }
            }
        }
    }
    OverlapScan out;
    out.count = (int)touched.size();
    out.replaced = std::move(replaced);
    return out;
}

inline int cut_overlaps(Mesh& M, double tol) {
    OverlapScan scan = overlap_scan(M, tol, true);
    if (scan.replaced.empty()) return 0;
    std::vector<char> gone(M.F.size(), 0);
    for (const auto& r : scan.replaced) gone[r.first] = 1;
    std::vector<int> keep_idx;
    for (size_t i = 0; i < M.F.size(); ++i)
        if (!gone[i]) keep_idx.push_back((int)i);
    std::vector<Face> new_F;
    std::vector<Color> new_C;
    std::vector<std::vector<Point2>> new_UV;                   // (empty: add.py's None)
    struct Affine { Point2 a, b, c, ua, ub, uc; double det; };
    for (const auto& r : scan.replaced) {
        int i = r.first;
        const CutFace& R = r.second;
        const Point &u = R.u, &v = R.v, &n = R.n;
        const Face f = M.F[i];
        // The pieces go back onto the face's own plane, not onto the group's: the
        // group's normal is rounded to a thousandth and its distance to a millimetre,
        // so a piece put there would stand off its face by up to a thousandth of its
        // distance from the origin.  Each point (s, t) of the frame is moved along
        // ``n`` until it lies on the face; a corner of the face comes back where it was.
        Point nf = face_normal(M, f);
        double ln = norm(nf);
        nf = {nf[0] / ln, nf[1] / ln, nf[2] / ln};
        double df = 0.0;
        for (int k : f) df += dot(nf, M.V[k]);
        df /= (double)f.size();
        double nn = dot(nf, n);                                // (near 1 or -1: the face lies in the group's plane)
        std::map<std::pair<double, double>, int> corners;
        for (int k : f) corners.emplace(std::make_pair(dot(M.V[k], u), dot(M.V[k], v)), k);
        // texture coordinates: the affine map of the original corners, if any
        const std::vector<Point2>* uv = M.has_uv && !M.UV[i].empty() ? &M.UV[i] : nullptr;
        std::optional<Affine> affine;
        if (uv && f.size() >= 3) {
            Profile P2;
            for (int k : f) P2.push_back({dot(M.V[k], u), dot(M.V[k], v)});
            size_t nf = f.size();
            for (size_t a = 0; a < nf; ++a) {
                size_t b = (a + 1) % nf, c = (a + 2) % nf;
                double det = ((P2[b][0] - P2[a][0]) * (P2[c][1] - P2[a][1])
                              - (P2[c][0] - P2[a][0]) * (P2[b][1] - P2[a][1]));
                if (std::fabs(det) > 1e-12) {
                    affine = Affine{P2[a], P2[b], P2[c], uv->at(a), uv->at(b), uv->at(c), det};
                    break;
                }
            }
        }
        for (const Profile& piece : R.pieces) {
            if (piece.size() < 3 || std::fabs(poly_area2(piece)) <= 1e-12) continue;
            Face idx;
            std::vector<Point2> piece_uv;
            for (const Point2& st : piece) {
                double s_ = st[0], t_ = st[1];
                auto at = corners.find(std::make_pair(s_, t_));
                if (at != corners.end()) {                     // a corner of the face: the very point
                    const Point p = M.V[at->second];
                    idx.push_back(M.add_vertex({p[0], p[1], p[2]}));
                } else {
                    Point q{u[0] * s_ + v[0] * t_, u[1] * s_ + v[1] * t_, u[2] * s_ + v[2] * t_};
                    double h = (df - dot(nf, q)) / nn;
                    idx.push_back(M.add_vertex({q[0] + n[0] * h, q[1] + n[1] * h, q[2] + n[2] * h}));
                }
                if (affine) {
                    const Affine& A = *affine;
                    const Point2 &a = A.a, &b = A.b, &c = A.c, &ua = A.ua, &ub = A.ub, &uc = A.uc;
                    double l1 = ((s_ - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (t_ - a[1])) / A.det;
                    double l2 = ((b[0] - a[0]) * (t_ - a[1]) - (s_ - a[0]) * (b[1] - a[1])) / A.det;
                    piece_uv.push_back({ua[0] + l1 * (ub[0] - ua[0]) + l2 * (uc[0] - ua[0]),
                                        ua[1] + l1 * (ub[1] - ua[1]) + l2 * (uc[1] - ua[1])});
                }
            }
            if (R.flipped) {                                   // the face looked the other way: keep it so
                std::reverse(idx.begin(), idx.end());
                std::reverse(piece_uv.begin(), piece_uv.end());
            }
            new_F.push_back(std::move(idx));
            new_C.push_back(M.C[i]);
            new_UV.push_back(std::move(piece_uv));
        }
    }
    keep_faces(M, keep_idx);
    M.F.insert(M.F.end(), new_F.begin(), new_F.end());
    M.C.insert(M.C.end(), new_C.begin(), new_C.end());
    if (M.has_uv) {
        M.UV.insert(M.UV.end(), new_UV.begin(), new_UV.end());
    } else if (std::any_of(new_UV.begin(), new_UV.end(), [](const std::vector<Point2>& t) { return !t.empty(); })) {
        M.has_uv = true;                                       // (cannot happen: no texture, no affine map)
        M.UV.assign(M.F.size() - new_F.size(), {});
        M.UV.insert(M.UV.end(), new_UV.begin(), new_UV.end());
    }
    return scan.count;
}

}  // namespace detail

inline Mesh heal(const Mesh& M0, double tol) {
    using namespace detail;
    Mesh M = M0;
    if (M.F.empty() || M.V.empty()) return M;

    // A grid roughly one edge-length wide keeps the search local.
    double total = 0.0;
    long long count = 0;
    for (const Face& f : M.F) {
        size_t n = f.size();
        for (size_t i = 0; i < n; ++i) {
            total += norm(sub(M.V[f[i]], M.V[f[(i + 1) % n]]));
            count += 1;
        }
    }
    double cell = std::max(total / (double)std::max(1LL, count), tol * 10.0);

    std::unordered_map<CellKey, std::vector<int>, CellKeyHash> grid;
    for (size_t idx = 0; idx < M.V.size(); ++idx) {
        const Point& p = M.V[idx];
        CellKey key{cell_floor(p[0] / cell), cell_floor(p[1] / cell), cell_floor(p[2] / cell)};
        grid[key].push_back((int)idx);
    }
    auto add_cell = [&](std::vector<int>& out, const CellKey& key) {
        auto it = grid.find(key);
        if (it != grid.end()) out.insert(out.end(), it->second.begin(), it->second.end());
    };

    // Vertex indices in the grid cells the segment could pass through.
    auto nearby = [&](const Point& pa, const Point& pb) {
        long long lo[3], hi[3];
        for (int a = 0; a < 3; ++a) {
            lo[a] = cell_floor((std::min(pa[a], pb[a]) - tol) / cell);
            hi[a] = cell_floor((std::max(pa[a], pb[a]) + tol) / cell);
        }
        double spread = 1;                                     // (as a float: it cannot overflow)
        for (int a = 0; a < 3; ++a) spread *= (double)hi[a] - (double)lo[a] + 1.0;
        std::vector<int> out;
        if (spread <= 512) {                                   // short edge: sweep its box
            for (long long cx = lo[0]; cx <= hi[0]; ++cx)
                for (long long cy = lo[1]; cy <= hi[1]; ++cy)
                    for (long long cz = lo[2]; cz <= hi[2]; ++cz) add_cell(out, CellKey{cx, cy, cz});
            return out;
        }
        // Long edge: walk along it instead of filling its whole box.
        double length = norm(sub(pb, pa));
        double x = 3.0 * length / cell;
        if (!std::isfinite(x)) cell_floor(x);                   // (int() of a NaN or an infinity: an exception)
        long long steps = x < 4000.0 ? std::min<long long>(4000, (long long)x + 2) : 4000;
        std::unordered_set<CellKey, CellKeyHash> seen_cells;
        for (long long s = 0; s <= steps; ++s) {
            double t = (double)s / (double)steps;
            CellKey key{cell_floor((pa[0] + (pb[0] - pa[0]) * t) / cell),
                        cell_floor((pa[1] + (pb[1] - pa[1]) * t) / cell),
                        cell_floor((pa[2] + (pb[2] - pa[2]) * t) / cell)};
            if (!seen_cells.insert(key).second) continue;
            for (long long a = -1; a <= 1; ++a)
                for (long long b = -1; b <= 1; ++b)
                    for (long long c = -1; c <= 1; ++c) add_cell(out, CellKey{key.i + a, key.j + b, key.k + c});
        }
        return out;
    };

    std::vector<Face> newF;
    std::vector<std::vector<Point2>> newUV;                    // (used when the mesh has texture coordinates)
    for (size_t k = 0; k < M.F.size(); ++k) {
        const Face& f = M.F[k];
        size_t n = f.size();
        Face out;
        const std::vector<Point2>* uv = M.has_uv && !M.UV[k].empty() ? &M.UV[k] : nullptr;
        std::vector<Point2> out_uv;
        for (size_t i = 0; i < n; ++i) {
            int a = f[i], b = f[(i + 1) % n];
            out.push_back(a);
            if (uv) out_uv.push_back(uv->at(i));
            const Point& pa = M.V[a];
            const Point& pb = M.V[b];
            Point d = sub(pb, pa);
            double L2 = dot(d, d);
            if (L2 <= tol * tol) continue;
            std::vector<std::pair<double, int>> hits;
            for (int v : nearby(pa, pb)) {
                if (v == a || v == b) continue;
                const Point& pv = M.V[v];
                double t = ((pv[0] - pa[0]) * d[0] + (pv[1] - pa[1]) * d[1]
                            + (pv[2] - pa[2]) * d[2]) / L2;
                if (t <= 1e-9 || t >= 1.0 - 1e-9) continue;
                if (std::fabs(pa[0] + d[0] * t - pv[0]) <= tol
                        && std::fabs(pa[1] + d[1] * t - pv[1]) <= tol
                        && std::fabs(pa[2] + d[2] * t - pv[2]) <= tol)
                    hits.push_back({t, v});
            }
            if (!hits.empty()) {
                std::sort(hits.begin(), hits.end());           // (by t, then by vertex -- as Python sorts tuples)
                bool have_last = false;
                int last = 0;
                for (const auto& h : hits) {
                    double t = h.first;
                    int v = h.second;
                    if (!have_last || v != last) {
                        out.push_back(v);
                        if (uv) {
                            const Point2& ua = uv->at(i);
                            const Point2& ub = uv->at((i + 1) % n);
                            out_uv.push_back({ua[0] + (ub[0] - ua[0]) * t, ua[1] + (ub[1] - ua[1]) * t});
                        }
                    }
                    last = v;
                    have_last = true;
                }
            }
        }
        newF.push_back(std::move(out));
        if (M.has_uv) newUV.push_back(std::move(out_uv));
    }
    M.F = std::move(newF);
    if (M.has_uv) M.UV = std::move(newUV);
    return M;
}
inline Mesh heal() { return heal(scene()); }

inline int concave_faces(const Mesh& M) {
    int count = 0;
    for (const Face& f : M.F)
        if (f.size() > 3 && detail::is_concave(M, f)) count += 1;
    return count;
}
inline int concave_faces() { return concave_faces(scene()); }

inline int overlaps(const Mesh& M, double tol) { return detail::overlap_scan(M, tol, false).count; }
inline int overlaps() { return overlaps(scene()); }

inline Mesh triangulate(const Mesh& M) {
    Mesh out;
    out.V = M.V;
    for (size_t k = 0; k < M.F.size() && k < M.C.size(); ++k) {
        const Face& f = M.F[k];
        const Color& c = M.C[k];
        const std::vector<Point2>* uv = M.has_uv && !M.UV[k].empty() ? &M.UV[k] : nullptr;
        for (size_t t = 1; t + 1 < f.size(); ++t) {
            if (uv) out.add_face({f[0], f[t], f[t + 1]}, c, {uv->at(0), uv->at(t), uv->at(t + 1)});
            else out.add_face({f[0], f[t], f[t + 1]}, c);
        }
    }
    return out;
}
inline Mesh triangulate() { return triangulate(scene()); }

inline Mesh fix_normals(const Mesh& M0, bool outward) {
    Mesh M = M0;
    std::vector<int> rep = detail::weld_map(M.V);            // (corners lying on one another count as one)
    std::map<std::pair<int, int>, std::vector<int>> edge_faces;
    for (size_t i = 0; i < M.F.size(); ++i) {
        const Face& f = M.F[i];
        size_t n = f.size();
        for (size_t t = 0; t < n; ++t) {
            int a = rep[f[t]], b = rep[f[(t + 1) % n]];
            if (a != b) edge_faces[a < b ? std::make_pair(a, b) : std::make_pair(b, a)].push_back((int)i);
        }
    }

    std::vector<char> visited(M.F.size(), 0);
    for (size_t start = 0; start < M.F.size(); ++start) {
        if (visited[start]) continue;
        std::vector<int> component{(int)start};
        visited[start] = 1;
        std::vector<int> stack{(int)start};
        while (!stack.empty()) {
            int i = stack.back();
            stack.pop_back();
            const Face& f = M.F[i];                            // (only unvisited neighbours are turned round)
            size_t n = f.size();
            for (size_t t = 0; t < n; ++t) {
                int a = rep[f[t]], b = rep[f[(t + 1) % n]];
                if (a == b) continue;
                const std::vector<int>& around = edge_faces[a < b ? std::make_pair(a, b) : std::make_pair(b, a)];
                if (around.size() != 2) continue;              // (an open edge, or one of three faces or more)
                for (int j : around) {
                    if (visited[j]) continue;
                    Face& g = M.F[j];
                    size_t m = g.size();
                    bool same = false;
                    for (size_t s = 0; s < m; ++s)
                        if (rep[g[s]] == a && rep[g[(s + 1) % m]] == b) {
                            same = true;
                            break;
                        }
                    if (same) {                                // neighbour disagrees
                        std::reverse(g.begin(), g.end());
                        if (M.has_uv) std::reverse(M.UV[j].begin(), M.UV[j].end());
                    }
                    visited[j] = 1;
                    component.push_back(j);
                    stack.push_back(j);
                }
            }
        }
        if (outward) {
            std::pair<double, double> pv = detail::piece_volume(M, component, rep);
            if (pv.first < -1e-9 * pv.second) {
                for (int i : component) {
                    std::reverse(M.F[i].begin(), M.F[i].end());
                    if (M.has_uv) std::reverse(M.UV[i].begin(), M.UV[i].end());
                }
            }
        }
    }
    return M;
}
inline Mesh fix_normals() { return fix_normals(scene()); }

inline Mesh clean(const Mesh& M0, double tol, bool weld, bool degenerate, bool duplicates, bool internal, bool unused,
                  bool normals, CleanReport* report, bool overlaps, bool convex) {
    Mesh M = M0;
    CleanReport info;
    size_t n = M.V.size();
    info.faces_removed += detail::drop_not_finite(M);        // a vertex that is not a number cannot be mended
    info.vertices_removed += (int)(n - M.V.size());
    if (weld) info.vertices_removed += detail::weld(M, tol);
    if (degenerate) info.faces_removed += detail::drop_degenerate(M);
    if (internal) info.faces_removed += detail::drop_internal(M);
    if (duplicates) info.faces_removed += detail::dedup_faces(M);
    if (overlaps) {
        info.faces_cut += detail::cut_overlaps(M);
        if (info.faces_cut && weld) {
            detail::weld(M, tol);                              // the new corners meet their neighbours ...
            M = heal(M, tol);                                  // ... and the neighbours' long edges learn of them
            if (degenerate)                                    // a corner welded onto its neighbour can leave a face
                info.faces_removed += detail::drop_degenerate(M);   // visiting a vertex twice, or without area
            if (duplicates) info.faces_removed += detail::dedup_faces(M);
        }
    }
    if (convex) info.faces_split += detail::split_concave(M);
    if (normals) M = fix_normals(M);
    if (unused) info.vertices_removed += detail::drop_unused(M);
    if (report) *report = info;
    return M;
}
inline Mesh clean() { return clean(scene()); }

inline Stats stats(const Mesh& M) {
    Stats s;
    std::array<Point, 2> bb = bbox(M);
    const Point& lo = bb[0];
    const Point& hi = bb[1];
    std::map<std::pair<int, int>, int> edges;
    for (const Face& f : M.F) {
        size_t n = f.size();
        for (size_t t = 0; t < n; ++t) {
            int a = f[t], b = f[(t + 1) % n];
            edges[a < b ? std::make_pair(a, b) : std::make_pair(b, a)] += 1;
        }
    }
    int open_edges = 0, odd_edges = 0;
    for (const auto& edge : edges) {
        if (edge.second == 1) open_edges += 1;
        if (edge.second > 2) odd_edges += 1;
    }
    // vertices sitting on the same spot (add.py: a dict of rounded points, where
    // 0.0 and -0.0 are one key and a point with a NaN is always a key of its own)
    std::set<std::array<double, 3>> spots;
    size_t lone = 0;
    for (const Point& p : M.V) {
        std::array<double, 3> key = {detail::py_round(p[0], 6), detail::py_round(p[1], 6),
                                     detail::py_round(p[2], 6)};
        if (std::isnan(key[0]) || std::isnan(key[1]) || std::isnan(key[2])) lone += 1;
        else spots.insert(key);
    }
    int duplicate_vertices = (int)M.V.size() - (int)(spots.size() + lone);
    std::map<Face, std::vector<const Face*>> groups;
    for (const Face& f : M.F) {
        Face key = f;
        std::sort(key.begin(), key.end());
        groups[key].push_back(&f);
    }
    int duplicate_faces = 0, back_to_back = 0;
    for (const auto& g : groups) {
        const std::vector<const Face*>& same = g.second;
        if (same.size() < 2) continue;
        int forward = 0;
        for (const Face* f : same)
            if (detail::winding(*f)) forward += 1;
        int backward = (int)same.size() - forward;
        back_to_back += std::min(forward, backward);
        duplicate_faces += (int)same.size() - 1 - std::min(forward, backward);
    }
    s.vertices = (int)M.V.size();
    s.faces = (int)M.F.size();
    s.triangles = 0;
    for (const Face& f : M.F) s.triangles += std::max(0, (int)f.size() - 2);
    s.colors = (int)std::set<Color>(M.C.begin(), M.C.end()).size();
    s.bbox = {lo, hi};
    s.size = {hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]};
    s.area = area(M);
    s.volume = volume(M);
    s.open_edges = open_edges;
    s.non_manifold_edges = odd_edges;
    s.duplicate_vertices = duplicate_vertices;
    s.duplicate_faces = duplicate_faces;
    s.back_to_back_faces = back_to_back;
    s.closed = open_edges == 0;
    // add.py's obj_size writes every coordinate with _num, whose int(x) raises for
    // a NaN or an infinity: stats() of such a mesh is an error there, so it is here.
    for (const Point& p : M.V)
        for (int a = 0; a < 3; ++a)
            if (!std::isfinite(p[a])) detail::cell_floor(p[a]);    // (throws)
    s.obj_bytes = obj_size(M);
    s.transparent_faces = 0;
    for (const Color& c : M.C)
        if (c.alpha < 1.0) s.transparent_faces += 1;
    std::set<std::string> images;
    for (const Color& c : M.C)
        if (!c.image.empty()) images.insert(c.image);
    s.textures.assign(images.begin(), images.end());           // (sorted, as add.py's sorted(set(...)))
    return s;
}
inline Stats stats() { return stats(scene()); }

namespace detail {
inline std::string check_f(double x, int decimals) {
    if (std::isnan(x)) return "nan";
    return fmt("%.*f", decimals, x);
}
inline std::string check_d(double x) {
    if (!std::isfinite(x)) cell_floor(x);
    double w = std::trunc(x);
    if (w == 0) return "0";
    return fmt("%.0f", w);
}
}  // namespace detail

inline bool check(const Mesh& M, int min_faces, int min_colors, bool quiet, double max_mb, int max_colors) {
    using detail::fmt;
    Stats s = stats(M);
    double mb = (double)s.obj_bytes / 1e6;
    bool fits = mb <= max_mb && s.colors <= max_colors;
    bool ok = s.faces >= min_faces && s.colors >= min_colors && fits;
    if (!quiet) {
        auto mark = [](bool good) { return std::string(good ? "OK " : "!! "); };
        std::ostream& out = std::cout;
        out << std::string(56, '-') << "\n";
        out << fmt("  vertices            %d", s.vertices) << "\n";
        out << mark(s.faces >= min_faces) << fmt(" polygons            %d  (need %d)", s.faces, min_faces) << "\n";
        out << mark(min_colors <= s.colors && s.colors <= max_colors)
            << fmt(" colours             %d  (need %d, at most %d materials for Sketchfab)", s.colors, min_colors,
                   max_colors)
            << "\n";
        out << mark(mb <= max_mb) << " .obj file size      " << detail::check_f(mb, 1) << " MB  (at most "
            << detail::check_d(max_mb) << " MB for Sketchfab)\n";
        out << "   size                " << detail::check_f(s.size[0], 3) << " x " << detail::check_f(s.size[1], 3)
            << " x " << detail::check_f(s.size[2], 3) << "\n";
        out << "   surface area        " << detail::check_f(s.area, 3) << "\n";
        std::string why;
        if (s.closed) why = "yes";
        else why = fmt("no, %d edges have nothing on the other side", s.open_edges);
        out << mark(s.closed) << " closed surface      " << why << "\n";
        if (s.non_manifold_edges)
            out << fmt("   repeated edges      %d   (an edge shared by more than two faces:"
                       " parts meet along it; normal for voxel models)", s.non_manifold_edges) << "\n";
        if (s.duplicate_vertices)
            out << fmt("!! repeated vertices   %d   (two vertices on one spot -- add.clean() welds them)",
                       s.duplicate_vertices) << "\n";
        if (s.duplicate_faces)
            out << fmt("!! repeated faces      %d   -- add.clean() removes them", s.duplicate_faces) << "\n";
        if (s.back_to_back_faces)
            out << fmt("   back-to-back faces  %d   (fine for a two-sided sheet;"
                       " add.clean() removes them)", s.back_to_back_faces) << "\n";
        int flicker = overlaps(M);
        if (flicker)
            out << fmt("!! overlapping faces   %d   (lying on a bigger face in the same plane:"
                       " they flicker in a viewer -- add.clean() cuts them)", flicker) << "\n";
        int notched = concave_faces(M);
        if (notched)
            out << fmt("!! non-convex faces    %d   (a viewer draws a polygon as a fan and"
                       " covers its notch -- add.clean() cuts them into triangles)", notched) << "\n";
        if (s.closed) out << "   volume              " << detail::check_f(s.volume, 3) << "\n";
        if (s.transparent_faces)
            out << fmt("   see-through faces   %d   (opacity is kept in .obj + .mtl)", s.transparent_faces) << "\n";
        if (!s.textures.empty()) {
            std::string names;
            for (size_t i = 0; i < s.textures.size(); ++i) names += (i ? ", " : "") + s.textures[i];
            out << "   textures            " << names << "   (put the images next to the .obj)\n";
        }
        if (s.colors > max_colors)
            out << fmt("   hint: add.limit_colors(M, %d) or add.save(..., colors=%d)", max_colors, max_colors) << "\n";
        if (mb > max_mb)
            out << "   hint: fewer cells (a smaller k, grid or subdivisions)"
                   " make the file smaller\n";
        out << std::string(56, '-') << "\n";
    }
    return ok;
}
inline bool check() { return check(scene()); }

}  // namespace add

namespace add {

namespace detail {

inline std::map<Edge, int> directed_edges(const Mesh& M) {
    std::map<Edge, int> out;
    for (size_t fi = 0; fi < M.F.size(); ++fi) {
        const Face& f = M.F[fi];
        size_t n = f.size();
        for (size_t t = 0; t < n; ++t) {
            Edge key(f[t], f[(t + 1) % n]);
            auto it = out.find(key);
            if (it != out.end()) it->second = -1;
            else out.emplace(key, (int)fi);
        }
    }
    return out;
}

inline std::vector<VertexRing> rings(const Mesh& M) {
    std::map<Edge, int> E = directed_edges(M);
    auto get = [&E](int a, int b) {                            // E.get((a, b), -1)
        auto it = E.find(Edge(a, b));
        return it == E.end() ? -1 : it->second;
    };
    struct Corner { int fi, prev, next; };
    std::vector<std::vector<Corner>> corners(M.V.size());     // vertex -> [(face, prev, next)]
    for (size_t fi = 0; fi < M.F.size(); ++fi) {
        const Face& f = M.F[fi];
        size_t n = f.size();
        for (size_t t = 0; t < n; ++t) corners.at(f[t]).push_back({(int)fi, f[(t + n - 1) % n], f[(t + 1) % n]});
    }
    std::vector<VertexRing> out;
    out.reserve(corners.size());
    for (size_t v = 0; v < corners.size(); ++v) {
        const std::vector<Corner>& cs = corners[v];
        VertexRing R;
        if (cs.empty()) {
            out.push_back(R);
            continue;
        }
        std::unordered_map<int, std::pair<int, int>> by_face;
        bool ok = true;
        for (const Corner& c : cs) {
            if (by_face.count(c.fi)) ok = false;               // v twice in one face
            by_face[c.fi] = {c.prev, c.next};
        }
        if (!ok) {
            for (const Corner& c : cs) R.ring.push_back({c.fi, c.next});
            out.push_back(R);
            continue;
        }
        // Start at a border face if there is one: the face whose edge prev -> v has no partner face
        // on the other side.
        int start = cs[0].fi;
        for (const Corner& c : cs)
            if (get((int)v, c.prev) == -1) {
                start = c.fi;
                break;
            }
        std::unordered_set<int> seen;
        int fi = start;
        bool closed = false;
        while (true) {
            if (seen.count(fi)) {                              // (Python's while ... else)
                closed = (fi == start);
                break;
            }
            seen.insert(fi);
            int nxt = by_face[fi].second;
            R.ring.push_back({fi, nxt});
            int g = get(nxt, (int)v);
            if (g == -1 || !by_face.count(g)) break;
            fi = g;
        }
        if (seen.size() != cs.size()) {                        // not all faces reached
            closed = false;
            for (const Corner& c : cs)
                if (!seen.count(c.fi)) R.ring.push_back({c.fi, c.next});
        }
        R.closed = closed;
        out.push_back(R);
    }
    return out;
}

}  // namespace detail

inline Point vertex(const Mesh& M, int i) { return M.V[detail::seq_index(i, M.V.size())]; }

inline Mesh set_vertex(const Mesh& M, int i, const PartialPoint& point) { return set_vertices(M, {{i, point}}); }

inline Mesh set_vertices(const Mesh& M, const std::vector<std::pair<int, PartialPoint>>& changes) {
    // A dict: an index given again keeps its first place and takes the new point.
    std::vector<std::pair<int, PartialPoint>> dict;
    std::unordered_map<int, size_t> where;
    for (const auto& change : changes) {
        auto it = where.find(change.first);
        if (it != where.end()) {
            dict[it->second].second = change.second;
        } else {
            where.emplace(change.first, dict.size());
            dict.push_back(change);
        }
    }
    Mesh out = M;
    for (const auto& change : dict) {
        Point& p = out.V[detail::seq_index(change.first, out.V.size())];
        const PartialPoint& q = change.second;
        if (q.x) p.x = *q.x;
        if (q.y) p.y = *q.y;
        if (q.z) p.z = *q.z;
    }
    return out;
}

inline Mesh move_vertex(const Mesh& M, int i, const Point& delta) {
    const Point& p = M.V[detail::seq_index(i, M.V.size())];
    return set_vertices(M, {{i, Point{p[0] + delta[0], p[1] + delta[1], p[2] + delta[2]}}});
}

inline int nearest_vertex(const Mesh& M, const Point& point) {
    int best = -1;
    double best_d = 0.0;
    for (size_t i = 0; i < M.V.size(); ++i) {
        const Point& p = M.V[i];
        double d = detail::py_pow(p[0] - point[0], 2) + detail::py_pow(p[1] - point[1], 2) +
                   detail::py_pow(p[2] - point[2], 2);                 // (Python's ** 2)
        if (best < 0 || d < best_d) {                          // (the first of equals)
            best = (int)i;
            best_d = d;
        }
    }
    return best;
}

inline std::vector<Edge> edges(const Mesh& M) {
    std::set<Edge> seen;
    for (const Face& f : M.F) {
        size_t n = f.size();
        for (size_t t = 0; t < n; ++t) {
            int a = f[t], b = f[(t + 1) % n];
            if (a != b) seen.insert(a < b ? Edge(a, b) : Edge(b, a));
        }
    }
    return std::vector<Edge>(seen.begin(), seen.end());
}
inline std::vector<Edge> edges() { return edges(scene()); }

inline double edge_length(const Mesh& M, int a, int b) {
    return detail::norm(detail::sub(M.V[detail::seq_index(a, M.V.size())], M.V[detail::seq_index(b, M.V.size())]));
}

inline std::vector<double> edge_lengths(const Mesh& M) {
    std::vector<double> out;
    for (const Edge& e : edges(M)) out.push_back(detail::norm(detail::sub(M.V[e.first], M.V[e.second])));
    return out;
}
inline std::vector<double> edge_lengths() { return edge_lengths(scene()); }

inline double mean_edge_length(const Mesh& M) {
    std::vector<double> L = edge_lengths(M);
    if (L.empty()) return 0.0;
    double s = 0.0;                                            // (add.py's _total: in order)
    for (double x : L) s = s + x;
    return s / (double)L.size();
}
inline double mean_edge_length() { return mean_edge_length(scene()); }

inline std::vector<std::vector<int>> adjacency(const Mesh& M) {
    std::vector<std::set<int>> nb(M.V.size());
    for (const Edge& e : edges(M)) {
        nb.at(e.first).insert(e.second);
        nb.at(e.second).insert(e.first);
    }
    std::vector<std::vector<int>> out;
    out.reserve(nb.size());
    for (const std::set<int>& s : nb) out.push_back(std::vector<int>(s.begin(), s.end()));
    return out;
}
inline std::vector<std::vector<int>> adjacency() { return adjacency(scene()); }

inline std::vector<int> neighbors(const Mesh& M, int i) {
    std::vector<detail::VertexRing> R = detail::rings(M);
    const detail::VertexRing& r = R[detail::seq_index(i, R.size())];
    if (r.closed) {
        std::vector<int> out;
        for (auto it = r.ring.rbegin(); it != r.ring.rend(); ++it) out.push_back(it->second);
        return out;
    }
    std::vector<std::vector<int>> adj = adjacency(M);
    return adj[detail::seq_index(i, adj.size())];
}
inline std::vector<int> neighbours(const Mesh& M, int i) { return neighbors(M, i); }

inline int valence(const Mesh& M, int i) {
    std::vector<std::vector<int>> adj = adjacency(M);
    return (int)adj[detail::seq_index(i, adj.size())].size();
}

inline double mean_neighbor_distance(const Mesh& M, int i) {
    std::vector<std::vector<int>> adj = adjacency(M);
    const std::vector<int>& nb = adj[detail::seq_index(i, adj.size())];
    if (nb.empty()) return 0.0;
    const Point& p = M.V[detail::seq_index(i, M.V.size())];
    double s = 0.0;
    for (int j : nb) s = s + detail::norm(detail::sub(p, M.V[j]));
    return s / (double)nb.size();
}

inline std::vector<int> vertex_faces(const Mesh& M, int i) {
    std::vector<detail::VertexRing> R = detail::rings(M);
    const detail::VertexRing& r = R[detail::seq_index(i, R.size())];
    std::vector<int> out;
    if (r.closed) {
        for (auto it = r.ring.rbegin(); it != r.ring.rend(); ++it) out.push_back(it->first);
        return out;
    }
    std::set<int> faces;
    for (const auto& entry : r.ring) faces.insert(entry.first);
    return std::vector<int>(faces.begin(), faces.end());
}

inline Point vertex_normal(const Mesh& M, int i) {
    Point acc{0.0, 0.0, 0.0};
    for (int fi : vertex_faces(M, i)) {
        Point nrm = detail::face_normal(M, M.F[fi]);
        acc[0] += nrm[0];
        acc[1] += nrm[1];
        acc[2] += nrm[2];
    }
    return detail::norm(acc) > EPS ? detail::unit(acc) : Point{0.0, 1.0, 0.0};
}

inline Point face_center(const Mesh& M, int i) {
    const Face& f = M.F[detail::seq_index(i, M.F.size())];
    if (f.empty()) throw std::domain_error("float division by zero");
    double n = (double)f.size();
    Point out;
    for (int a = 0; a < 3; ++a) {
        double s = 0.0;                                        // (add.py's _total: in order)
        for (int k : f) s = s + M.V[k][a];
        out[a] = s / n;
    }
    return out;
}

inline Point face_normal(const Mesh& M, int i) {
    return detail::unit(detail::face_normal(M, M.F[detail::seq_index(i, M.F.size())]));
}

inline double face_area(const Mesh& M, int i) {
    return detail::norm(detail::face_normal(M, M.F[detail::seq_index(i, M.F.size())])) / 2.0;
}

inline Points face_centers(const Mesh& M) {
    Points out;
    out.reserve(M.F.size());
    for (size_t i = 0; i < M.F.size(); ++i) out.push_back(face_center(M, (int)i));
    return out;
}
inline Points face_centers() { return face_centers(scene()); }

inline std::vector<Edge> boundary_edges(const Mesh& M) {
    std::vector<Edge> out;
    for (const detail::BorderEdge& e : detail::boundary_edges(M)) out.push_back(Edge(e.a, e.b));
    std::sort(out.begin(), out.end());
    return out;
}
inline std::vector<Edge> boundary_edges() { return boundary_edges(scene()); }

inline std::vector<std::vector<int>> boundary_loops(const Mesh& M) {
    std::map<int, std::vector<int>> nxt;
    for (const detail::BorderEdge& e : detail::boundary_edges(M)) nxt[e.a].push_back(e.b);
    std::vector<std::vector<int>> loops;
    while (!nxt.empty()) {
        int start = nxt.begin()->first;                        // min(nxt)
        std::vector<int> loop{start};
        std::vector<int>& from_start = nxt[start];
        int v = from_start.back();                             // (list.pop(): the last one)
        from_start.pop_back();
        if (from_start.empty()) nxt.erase(start);
        while (v != start && nxt.count(v)) {
            loop.push_back(v);
            std::vector<int>& from_v = nxt[v];
            int w = from_v.back();
            from_v.pop_back();
            if (from_v.empty()) nxt.erase(v);
            v = w;
        }
        loops.push_back(loop);
    }
    return loops;
}
inline std::vector<std::vector<int>> boundary_loops() { return boundary_loops(scene()); }

inline Mesh inflate(const Mesh& M, double amount) {
    Points N = detail::vertex_normals(M);
    Mesh out = M;
    out.V.clear();
    for (size_t i = 0; i < M.V.size() && i < N.size(); ++i) {
        const Point& p = M.V[i];
        const Point& n = N[i];
        out.V.push_back({p[0] + n[0] * amount, p[1] + n[1] * amount, p[2] + n[2] * amount});
    }
    return out;
}

inline Mesh spherify(const Mesh& M, std::optional<Point> center, std::optional<double> r, double amount) {
    Point c = center ? *center : add::center(M);
    double radius;
    if (r) {
        radius = *r;
    } else if (M.V.empty()) {
        radius = 1.0;                                          // max([...] or [1.0])
    } else {
        radius = detail::norm(detail::sub(M.V[0], c));
        for (const Point& p : M.V) {
            double x = detail::norm(detail::sub(p, c));
            if (x > radius) radius = x;
        }
    }
    Points V;
    V.reserve(M.V.size());
    for (const Point& p : M.V) {
        Point u = detail::unit(detail::sub(p, c));
        Point target{c[0] + u[0] * radius, c[1] + u[1] * radius, c[2] + u[2] * radius};
        Point q;
        for (int a = 0; a < 3; ++a) q[a] = p[a] + (target[a] - p[a]) * amount;
        V.push_back(q);
    }
    Mesh out = M;
    out.V = V;
    return out;
}

inline Mesh refine(const Mesh& M0, int steps) {
    Mesh M = M0;
    for (int step = 0; step < steps; ++step) {
        Mesh out;                                              // (texture coordinates are not kept)
        out.V = M.V;
        std::map<Edge, int> mid;
        auto midpoint_index = [&](int a, int b) {
            Edge key = a < b ? Edge(a, b) : Edge(b, a);
            auto it = mid.find(key);
            if (it != mid.end()) return it->second;
            const Point& pa = M.V[a];
            const Point& pb = M.V[b];
            int k = out.add_vertex({(pa[0] + pb[0]) / 2.0, (pa[1] + pb[1]) / 2.0, (pa[2] + pb[2]) / 2.0});
            mid.emplace(key, k);
            return k;
        };
        for (size_t q = 0; q < M.F.size() && q < M.C.size(); ++q) {
            const Face& f = M.F[q];
            const Color& c = M.C[q];
            size_t n = f.size();
            if (n == 3) {
                int a = f[0], b = f[1], d = f[2];
                int ab = midpoint_index(a, b);                 // (in this order)
                int bd = midpoint_index(b, d);
                int da = midpoint_index(d, a);
                out.add_face({a, ab, da}, c);
                out.add_face({b, bd, ab}, c);
                out.add_face({d, da, bd}, c);
                out.add_face({ab, bd, da}, c);
            } else if (n >= 4) {
                Point centre_point;
                for (int a = 0; a < 3; ++a) {
                    double s = 0.0;
                    for (int k : f) s = s + M.V[k][a];
                    centre_point[a] = s / (double)n;
                }
                int centre = out.add_vertex(centre_point);
                std::vector<int> m;
                for (size_t t = 0; t < n; ++t) m.push_back(midpoint_index(f[t], f[(t + 1) % n]));
                for (size_t t = 0; t < n; ++t) out.add_face({f[t], m[t], centre, m[(t + n - 1) % n]}, c);
            } else {
                out.add_face(f, c);
            }
        }
        M = std::move(out);
    }
    return M;
}

inline Mesh dual(const Mesh& M, std::optional<Color> color) {
    Mesh out;
    for (size_t i = 0; i < M.F.size(); ++i) out.add_vertex(face_center(M, (int)i));
    std::vector<detail::VertexRing> R = detail::rings(M);
    for (const detail::VertexRing& r : R) {
        if (!r.closed || r.ring.size() < 3) continue;
        Face faces;
        for (auto it = r.ring.rbegin(); it != r.ring.rend(); ++it) faces.push_back(it->first);
        out.add_face(faces, color ? *color : M.C[faces[0]]);
    }
    detail::drop_unused(out);
    return out;
}

inline Mesh truncate(const Mesh& M, double t, const Color& color) {
    if (t > 0.5) t = 0.5;
    Mesh out;
    std::map<Edge, int> cut;
    auto point = [&](int a, int b) {                           // the vertex on edge a -> b at fraction t from a
        Edge key = t < 0.5 - 1e-12 ? Edge(a, b) : (a < b ? Edge(a, b) : Edge(b, a));
        auto it = cut.find(key);
        if (it != cut.end()) return it->second;
        const Point& pa = M.V[a];
        const Point& pb = M.V[b];
        int k = out.add_vertex({pa[0] + (pb[0] - pa[0]) * t, pa[1] + (pb[1] - pa[1]) * t, pa[2] + (pb[2] - pa[2]) * t});
        cut.emplace(key, k);
        return k;
    };
    for (size_t q = 0; q < M.F.size() && q < M.C.size(); ++q) {
        const Face& f = M.F[q];
        size_t n = f.size();
        std::vector<int> poly;
        for (size_t i = 0; i < n; ++i) {
            int v = f[i], prev = f[(i + n - 1) % n], nxt = f[(i + 1) % n];
            int first = point(v, prev);                        // (both made before either is used)
            int second = point(v, nxt);
            for (int idx : {first, second})
                if (poly.empty() || poly.back() != idx) poly.push_back(idx);
        }
        if (poly.size() > 1 && poly.front() == poly.back()) poly.pop_back();
        if (poly.size() >= 3) out.add_face(poly, M.C[q]);
    }
    const Color& corner = color;                               // (add.py: rgb(None) is the default grey)
    std::vector<detail::VertexRing> R = detail::rings(M);
    for (size_t v = 0; v < R.size(); ++v) {
        const std::vector<std::pair<int, int>>& ring = R[v].ring;
        if (ring.size() < 3) continue;
        std::vector<int> poly;
        for (auto it = ring.rbegin(); it != ring.rend(); ++it) poly.push_back(point((int)v, it->second));
        std::set<int> distinct(poly.begin(), poly.end());
        if (distinct.size() >= 3) out.add_face(poly, corner);
    }
    return out;
}

inline Mesh color_by_sides(const Mesh& M, const std::map<int, Color>& colors, std::optional<Color> fallback) {
    Mesh out = M;
    for (size_t i = 0; i < M.F.size(); ++i) {
        auto it = colors.find((int)M.F[i].size());
        if (it != colors.end()) out.C[i] = it->second;
        else if (fallback) out.C[i] = *fallback;
    }
    return out;
}

}  // namespace add

namespace add {

namespace detail {

inline Poly::Poly(Points pts_, const Color& c_) : pts(std::move(pts_)), c(c_) {
    double nx = 0.0, ny = 0.0, nz = 0.0;
    size_t m = pts.size();
    for (size_t i = 0; i < m; ++i) {
        const Point& a = pts[i];
        const Point& b = pts[(i + 1) % m];
        nx += (a[1] - b[1]) * (a[2] + b[2]);
        ny += (a[2] - b[2]) * (a[0] + b[0]);
        nz += (a[0] - b[0]) * (a[1] + b[1]);
    }
    n = unit({nx, ny, nz});
    if (pts.empty()) throw std::out_of_range("list index out of range");   // (add.py: pts[0] of no points)
    w = dot(n, pts[0]);
}

inline void split(const Point& pn, double pw, const Poly& poly, std::vector<Poly>& front, std::vector<Poly>& back,
                  double eps) {
    std::vector<int> types;
    int poly_type = 0;
    for (const Point& p : poly.pts) {
        double t = pn[0] * p[0] + pn[1] * p[1] + pn[2] * p[2] - pw;
        int kind = t < -eps ? BACK : (t > eps ? FRONT : COPLANAR);
        poly_type |= kind;
        types.push_back(kind);
    }

    if (poly_type != SPANNING) {
        (poly_type == BACK ? back : front).push_back(poly);
        return;
    }
    Points f, b;
    size_t m = poly.pts.size();
    for (size_t i = 0; i < m; ++i) {
        size_t j = (i + 1) % m;
        int ti = types[i], tj = types[j];
        const Point& vi = poly.pts[i];
        const Point& vj = poly.pts[j];
        if (ti != BACK) f.push_back(vi);
        if (ti != FRONT) b.push_back(vi);
        if ((ti | tj) == SPANNING) {
            double di = pn[0] * vi[0] + pn[1] * vi[1] + pn[2] * vi[2] - pw;
            double dj = pn[0] * vj[0] + pn[1] * vj[1] + pn[2] * vj[2] - pw;
            double t = di / (di - dj);
            Point cut = {vi[0] + (vj[0] - vi[0]) * t,
                         vi[1] + (vj[1] - vi[1]) * t,
                         vi[2] + (vj[2] - vi[2]) * t};
            f.push_back(cut);
            b.push_back(cut);
        }
    }
    if (f.size() >= 3) front.push_back(Poly(f, poly.c, poly.n, poly.w));
    if (b.size() >= 3) back.push_back(Poly(b, poly.c, poly.n, poly.w));
}

// ---------------------------------------------------------------------------
//  Two little indexes that keep the search local
// ---------------------------------------------------------------------------

inline double floor_cell(double x) {
    if (std::isnan(x)) throw std::invalid_argument("cannot convert float NaN to integer");
    if (std::isinf(x)) throw std::overflow_error("cannot convert float infinity to integer");
    return std::floor(x) + 0.0;                                // (a whole number: never -0.0)
}

inline double next_cell(double i) {
    return std::fabs(i) < 9007199254740992.0 ? i + 1.0 : std::nextafter(i, inf);
}

inline size_t GridKeyHash::operator()(const GridKey& c) const {
    std::hash<double> h;
    size_t s = h(c.i);
    s ^= h(c.j) + 0x9E3779B97F4A7C15ull + (s << 6) + (s >> 2);
    s ^= h(c.k) + 0x9E3779B97F4A7C15ull + (s << 6) + (s >> 2);
    return s;
}

// CPython's set of ints (hash(i) = i) is an open-addressing table of 8 slots to start with.  A key
// is looked for in slot hash & mask and the 9 slots after it (LINEAR_PROBES, when they are inside
// the table), then further on: perturb >>= 5, i = (i * 5 + 1 + perturb) & mask.  The table grows
// once it is 3/5 full: to the power of two above used * 4 (used * 2 past 50000 keys), the keys
// going in again in the order of their old slots.
inline size_t IntSet::slot(int key) const {
    size_t i = (size_t)key & mask_;
    size_t perturb = (size_t)key;
    while (true) {
        size_t last = i + 9 <= mask_ ? i + 9 : i;
        for (size_t e = i; e <= last; ++e)
            if (table_[e] < 0 || table_[e] == key) return e;
        perturb >>= 5;
        i = (i * 5 + 1 + perturb) & mask_;
    }
}

inline void IntSet::add(int key) {
    size_t e = slot(key);
    if (table_[e] == key) return;                              // already there
    table_[e] = key;
    fill_ += 1;
    used_ += 1;
    if (fill_ * 5 >= mask_ * 3) resize(used_ > 50000 ? used_ * 2 : used_ * 4);
}

inline void IntSet::resize(size_t minused) {
    size_t newsize = 8;
    while (newsize <= minused) newsize <<= 1;
    std::vector<int> old = std::move(table_);
    table_.assign(newsize, -1);
    mask_ = newsize - 1;
    for (int key : old)
        if (key >= 0) table_[slot(key)] = key;
    fill_ = used_;
}

inline std::vector<int> IntSet::items() const {
    std::vector<int> out;
    for (int key : table_)
        if (key >= 0) out.push_back(key);
    return out;
}

inline double coord_min(const Points& pts, int a) {
    if (pts.empty()) throw std::invalid_argument("min() arg is an empty sequence");
    double m = pts[0][a];
    for (const Point& q : pts)
        if (q[a] < m) m = q[a];
    return m;
}
inline double coord_max(const Points& pts, int a) {
    if (pts.empty()) throw std::invalid_argument("max() arg is an empty sequence");
    double m = pts[0][a];
    for (const Point& q : pts)
        if (q[a] > m) m = q[a];
    return m;
}

inline BoxGrid::BoxGrid(const std::vector<Poly>& polys, double diagonal) {
    cell = std::max(diagonal / 32.0, 1e-9);
    for (size_t i = 0; i < polys.size(); ++i) {
        const Poly& p = polys[i];
        Point lo{coord_min(p.pts, 0), coord_min(p.pts, 1), coord_min(p.pts, 2)};
        Point hi{coord_max(p.pts, 0), coord_max(p.pts, 1), coord_max(p.pts, 2)};
        boxes.push_back({lo, hi});
        std::optional<std::vector<GridKey>> ks = keys(lo, hi, MAX_CELLS);
        if (!ks) {
            oversize.push_back((int)i);
        } else {
            for (const GridKey& key : *ks) buckets[key].push_back((int)i);
        }
    }
}

inline std::optional<std::vector<GridKey>> BoxGrid::keys(const Point& lo, const Point& hi,
                                                        std::optional<long long> limit) const {
    double c = cell;
    std::array<std::pair<double, double>, 3> r;
    double total = 1;                                          // (a double: exact while it is small, and
    for (int a = 0; a < 3; ++a) {                              // it cannot overflow)
        double first = floor_cell(lo[a] / c);
        double last = floor_cell(hi[a] / c);
        r[a] = {first, last};
        total *= last - first + 1;
        if (limit && total > (double)*limit) return std::nullopt;
    }
    std::vector<GridKey> out;
    for (double i = r[0].first; i <= r[0].second; i = next_cell(i))
        for (double j = r[1].first; j <= r[1].second; j = next_cell(j))
            for (double k = r[2].first; k <= r[2].second; k = next_cell(k)) out.push_back({i, j, k});
    return out;
}

inline std::vector<int> BoxGrid::near(const Point& lo, const Point& hi) const {
    std::optional<std::vector<GridKey>> ks = keys(lo, hi, 4096);
    std::vector<int> candidates;
    if (!ks) {
        for (size_t i = 0; i < boxes.size(); ++i) candidates.push_back((int)i);
    } else {
        IntSet seen;                                           // (add.py: a set -- its order matters)
        for (int i : oversize) seen.add(i);
        for (const GridKey& key : *ks) {
            auto it = buckets.find(key);
            if (it == buckets.end()) continue;
            for (int i : it->second) seen.add(i);
        }
        candidates = seen.items();
    }
    std::vector<int> out;
    for (int i : candidates) {
        const Point& blo = boxes[i][0];
        const Point& bhi = boxes[i][1];
        if (bhi[0] < lo[0] - 1e-9 || blo[0] > hi[0] + 1e-9
                || bhi[1] < lo[1] - 1e-9 || blo[1] > hi[1] + 1e-9
                || bhi[2] < lo[2] - 1e-9 || blo[2] > hi[2] + 1e-9)
            continue;
        out.push_back(i);
    }
    return out;
}

inline RayIndex::RayIndex(const std::vector<Poly>& polys, const Point& direction) {
    d = unit(direction);
    e1 = perp(d);
    e2 = cross(d, e1);
    for (const Poly& p : polys)
        for (size_t t = 1; t + 1 < p.pts.size(); ++t) tris.push_back({p.pts[0], p.pts[t], p.pts[t + 1]});
    double span = 0.0;
    std::vector<std::array<double, 4>> flat;                   // (lo u, lo v, hi u, hi v) of each triangle
    for (const std::array<Point, 3>& tri : tris) {
        double uv[3][2];
        for (int q = 0; q < 3; ++q) {
            uv[q][0] = dot(tri[q], e1);
            uv[q][1] = dot(tri[q], e2);
        }
        double lo0 = uv[0][0], lo1 = uv[0][1], hi0 = uv[0][0], hi1 = uv[0][1];
        for (int q = 0; q < 3; ++q) {                          // (Python's min / max: the first of equals)
            if (uv[q][0] < lo0) lo0 = uv[q][0];
            if (uv[q][1] < lo1) lo1 = uv[q][1];
            if (uv[q][0] > hi0) hi0 = uv[q][0];
            if (uv[q][1] > hi1) hi1 = uv[q][1];
        }
        flat.push_back({lo0, lo1, hi0, hi1});
        double m = span;                                       // max(span, hi[0] - lo[0], hi[1] - lo[1])
        if (hi0 - lo0 > m) m = hi0 - lo0;
        if (hi1 - lo1 > m) m = hi1 - lo1;
        span = m;
    }
    cell = std::max(span, 1e-9);
    for (size_t i = 0; i < flat.size(); ++i) {
        const std::array<double, 4>& f = flat[i];              // (lo u, lo v, hi u, hi v)
        double a_first = floor_cell(f[0] / cell), a_last = floor_cell(f[2] / cell);
        for (double a = a_first; a <= a_last; a = next_cell(a)) {
            double b_first = floor_cell(f[1] / cell), b_last = floor_cell(f[3] / cell);
            for (double b = b_first; b <= b_last; b = next_cell(b)) buckets[GridKey{a, b, 0.0}].push_back((int)i);
        }
    }
}

inline std::optional<bool> RayIndex::inside(const Point& p) const {
    double ka = floor_cell(dot(p, e1) / cell);
    double kb = floor_cell(dot(p, e2) / cell);
    int hits = 0;
    auto it = buckets.find(GridKey{ka, kb, 0.0});
    if (it != buckets.end()) {
        for (int i : it->second) {
            const Point& a = tris[i][0];
            const Point& b = tris[i][1];
            const Point& c = tris[i][2];
            Point e1v = sub(b, a), e2v = sub(c, a);
            Point h = cross(d, e2v);
            double det = dot(e1v, h);
            if (std::fabs(det) < 1e-14) continue;
            double inv = 1.0 / det;
            Point s = sub(p, a);
            double u = dot(s, h) * inv;
            if (u < -1e-9 || u > 1.0 + 1e-9) continue;
            Point q = cross(s, e1v);
            double v = dot(d, q) * inv;
            if (v < -1e-9 || u + v > 1.0 + 1e-9) continue;
            double t = dot(e2v, q) * inv;
            if (t < 1e-12) continue;
            // Too close to an edge, a corner or the start of the ray to trust.
            if (std::fabs(u) < 1e-9 || std::fabs(v) < 1e-9 || std::fabs(u + v - 1.0) < 1e-9 || t < 1e-9)
                return std::nullopt;
            hits += 1;
        }
    }
    return hits % 2 == 1;
}

inline Solid::Solid(const Mesh& M) {
    polys = to_polys(M);
    if (!polys.empty()) {
        lo = hi = polys[0].pts[0];
        for (int a = 0; a < 3; ++a)                            // (Python's min / max: the first of equals)
            for (const Poly& q : polys)
                for (const Point& p : q.pts) {
                    if (p[a] < lo[a]) lo[a] = p[a];
                    if (p[a] > hi[a]) hi[a] = p[a];
                }
    } else {
        lo = {0.0, 0.0, 0.0};
        hi = {0.0, 0.0, 0.0};
    }
    double widest = hi[0] - lo[0];
    for (int a = 1; a < 3; ++a)
        if (hi[a] - lo[a] > widest) widest = hi[a] - lo[a];
    scale = std::max(1e-9, widest);
    double total = 0.0;                                        // (add.py's _total: in order, from 0)
    for (int a = 0; a < 3; ++a) {
        double squared = py_pow(hi[a] - lo[a], 2);
        if (std::isinf(squared) && std::isfinite(hi[a] - lo[a]))   // (Python's ** raises when it overflows)
            throw std::overflow_error("(34, 'Numerical result out of range')");
        total = total + squared;
    }
    double diagonal = std::sqrt(total);
    if (!polys.empty()) grid.emplace(polys, std::max(diagonal, 1e-9));
}

inline const RayIndex& Solid::ray_index(size_t which) {
    while (rays.size() <= which) rays.emplace_back(polys, RAY_DIRECTIONS[rays.size()]);
    return rays[which];
}

inline bool Solid::contains(const Point& p) {
    for (size_t which = 0; which < RAY_DIRECTIONS.size(); ++which) {
        std::optional<bool> answer = ray_index(which).inside(p);
        if (answer) return *answer;
    }
    return false;
}

// Normally a nearby triangle contributes its own plane.  A triangle lying in the *same* plane as
// ``poly`` would not cut it at all, yet the two faces may still overlap -- think of two boxes whose
// tops are flush.  For those, the three planes standing on the triangle's edges are used instead,
// which carves the shared patch out cleanly.
inline std::pair<std::vector<CutPlane>, std::vector<int>> Solid::cutters(const Poly& poly) const {
    Point plo{coord_min(poly.pts, 0), coord_min(poly.pts, 1), coord_min(poly.pts, 2)};
    Point phi{coord_max(poly.pts, 0), coord_max(poly.pts, 1), coord_max(poly.pts, 2)};
    std::vector<CutPlane> planes;
    std::vector<int> flush;
    if (!grid) throw std::runtime_error("'NoneType' object has no attribute 'near'");   // (as add.py: no triangles)
    for (int i : grid->near(plo, phi)) {
        const Poly& t = polys[i];
        if (std::fabs(std::fabs(dot(t.n, poly.n)) - 1.0) < 1e-9 && std::fabs(dot(t.n, poly.pts[0]) - t.w) < 1e-9) {
            flush.push_back(i);
            for (int k = 0; k < 3; ++k) {                      // the triangle's edge planes
                const Point& p = t.pts[k];
                const Point& q = t.pts[(k + 1) % 3];
                Point side = cross(t.n, sub(q, p));
                if (norm(side) > 1e-12) {
                    side = unit(side);
                    planes.push_back({{i, k + 1}, side, dot(side, p)});
                }
            }
        } else {
            planes.push_back({{i, 0}, t.n, t.w});
        }
    }
    return {planes, flush};
}

inline std::optional<int> Solid::facing_at(const Point& point, const Point& plane_normal,
                                           const std::vector<int>& flush) const {
    for (int i : flush) {
        const Poly& t = polys[i];
        bool on = true;
        for (int k = 0; k < 3; ++k) {
            const Point& p = t.pts[k];
            const Point& q = t.pts[(k + 1) % 3];
            Point side = cross(t.n, sub(q, p));
            if (dot(side, sub(point, p)) < -1e-12 * std::max(1.0, norm(side))) {
                on = false;
                break;
            }
        }
        if (on) return dot(t.n, plane_normal) > 0 ? 1 : -1;
    }
    return std::nullopt;
}

// Pieces are cut one at a time and the search is redone for each new piece, so a face far from
// the action stops being cut as soon as it moves out of the way -- which is what keeps a drilled
// plate from shattering into thousands of slivers.
inline std::vector<FlushPiece> split_against(const Poly& poly, const Solid& other) {
    using Done = std::set<std::pair<int, int>>;                // (add.py: a frozenset of plane ids)
    std::vector<FlushPiece> done_pieces;
    std::vector<std::pair<Poly, Done>> work;
    work.push_back({poly, Done()});
    int guard = 0;
    while (!work.empty()) {
        Poly piece = std::move(work.back().first);
        Done done = std::move(work.back().second);
        work.pop_back();
        guard += 1;
        if (guard > 20000) {                                   // pathological input; stop
            done_pieces.push_back({piece, {}, true});
            continue;
        }
        std::pair<std::vector<CutPlane>, std::vector<int>> found = other.cutters(piece);
        const std::vector<CutPlane>& planes = found.first;
        const std::vector<int>& flush = found.second;
        const CutPlane* chosen = nullptr;
        for (const CutPlane& plane : planes) {
            if (done.count(plane.pid)) continue;
            const Point& pn = plane.n;
            double pw = plane.w;
            bool front = false, back = false;
            for (const Point& p : piece.pts) {
                double t = pn[0] * p[0] + pn[1] * p[1] + pn[2] * p[2] - pw;
                if (t > BOOL_EPS) front = true;
                else if (t < -BOOL_EPS) back = true;
            }
            if (front && back) {
                chosen = &plane;
                break;
            }
            done.insert(plane.pid);                            // this plane can never cut it
        }
        if (!chosen) {
            done_pieces.push_back({piece, flush, false});
            continue;
        }
        std::vector<Poly> f, b;
        split(chosen->n, chosen->w, piece, f, b);
        Done rest = done;
        rest.insert(chosen->pid);
        for (Poly& part : f) work.push_back({std::move(part), rest});
        for (Poly& part : b) work.push_back({std::move(part), rest});
    }
    return done_pieces;
}

// ``keep`` is a set drawn from "in", "out", "same" and "opp": whether a piece ends up inside the
// other solid, outside it, or lying on its surface facing the same or the opposite way.
inline std::vector<Poly> keep_pieces(const Solid& source, Solid& other, const KeepSet& keep, bool flip,
                                     std::optional<Color> paint) {
    std::vector<Poly> out;
    if (!other.grid) return out;
    for (const Poly& poly : source.polys) {
        // Wholly outside the other model's box: no cutting, no doubt.
        bool apart = false;
        for (int a = 0; a < 3 && !apart; ++a)
            apart = coord_max(poly.pts, a) < other.lo[a] - 1e-9 || coord_min(poly.pts, a) > other.hi[a] + 1e-9;
        if (apart) {
            if (keep.count("out")) out.push_back(poly);
            continue;
        }
        for (const FlushPiece& found : split_against(poly, other)) {
            if (found.bare) throw std::runtime_error("cannot unpack non-iterable _Poly object");   // (as add.py)
            const Poly& piece = found.piece;
            const std::vector<int>& flush = found.flush;
            size_t n = piece.pts.size();
            double sx = 0.0, sy = 0.0, sz = 0.0;               // (add.py's _total: in order, from 0)
            for (const Point& q : piece.pts) sx = sx + q[0];
            for (const Point& q : piece.pts) sy = sy + q[1];
            for (const Point& q : piece.pts) sz = sz + q[2];
            Point centre = {sx / (double)n, sy / (double)n, sz / (double)n};
            std::optional<int> facing = !flush.empty() ? other.facing_at(centre, piece.n, flush) : std::nullopt;
            std::string state;
            if (facing) state = *facing > 0 ? "same" : "opp";
            else state = other.contains(centre) ? "in" : "out";
            if (!keep.count(state)) continue;
            Color c = paint ? *paint : piece.c;
            if (flip) {
                out.push_back(Poly(Points(piece.pts.rbegin(), piece.pts.rend()), c,
                                   {-piece.n[0], -piece.n[1], -piece.n[2]}, -piece.w));
            } else {
                out.push_back(Poly(piece.pts, c, piece.n, piece.w));
            }
        }
    }
    return out;
}

inline std::vector<Poly> to_polys(const Mesh& M) {
    std::vector<Poly> polys;
    for (size_t k = 0; k < M.F.size() && k < M.C.size(); ++k) {
        const Face& f = M.F[k];
        const Color& c = M.C[k];
        if (f.size() < 3) continue;
        Points pts;
        for (int i : f) pts.push_back(M.V[i]);
        for (size_t t = 1; t + 1 < pts.size(); ++t) {
            Poly p({pts[0], pts[t], pts[t + 1]}, c);
            if (norm(p.n) > 0.5) polys.push_back(std::move(p));   // skip degenerate slivers
        }
    }
    return polys;
}

inline Mesh from_polys(const std::vector<Poly>& polys, bool tidy) {
    Mesh M;
    for (const Poly& p : polys) M.add_polygon(p.pts, p.c);
    if (tidy) {
        detail::weld(M, 1e-7);
        detail::drop_degenerate(M);
        detail::dedup_faces(M);
        M = heal(M, 1e-7);
        detail::drop_degenerate(M);
        detail::drop_unused(M);
    }
    return M;
}

inline bool boxes_apart(const Mesh& A, const Mesh& B, double slack) {
    std::array<Point, 2> ba = bbox(A);
    std::array<Point, 2> bb = bbox(B);
    const Point& la = ba[0];
    const Point& ha = ba[1];
    const Point& lb = bb[0];
    const Point& hb = bb[1];
    for (int a = 0; a < 3; ++a)
        if (ha[a] < lb[a] - slack || hb[a] < la[a] - slack) return true;
    return false;
}

inline const std::map<std::string, BoolRule>& RULES() {
    static const std::map<std::string, BoolRule> rules = {
        {"union", {{"out", "same"}, {"out"}, false}},
        {"intersection", {{"in", "same"}, {"in"}, false}},
        {"difference", {{"out", "opp"}, {"in"}, true}},
    };
    return rules;
}

inline Mesh csg(const Mesh& A, const Mesh& B, const std::string& op, std::optional<Color> paint) {
    auto rule = RULES().find(op);
    if (rule == RULES().end()) throw std::invalid_argument("unknown boolean operation: '" + op + "'");
    const KeepSet& keep_a = rule->second.keep_a;
    const KeepSet& keep_b = rule->second.keep_b;
    bool flip_b = rule->second.flip_b;
    Solid a(A);
    Solid b(B);
    std::vector<Poly> polys = keep_pieces(a, b, keep_a, false);
    std::vector<Poly> more = keep_pieces(b, a, keep_b, flip_b, paint);
    polys.insert(polys.end(), more.begin(), more.end());
    return from_polys(polys);
}

inline std::vector<Points> loops(const std::vector<std::pair<Point, Point>>& edges) {
    using Key = std::array<double, 3>;
    auto key = [](const Point& p) { return Key{py_round(p[0], 7), py_round(p[1], 7), py_round(p[2], 7)}; };

    // add.py's dicts: ``nxt`` keeps its keys in the order they first came; in ``coords`` the last
    // point given for a key wins.  (Keys compare as Python's do: 0.0 and -0.0 are one key.)
    std::vector<std::pair<Key, std::vector<Key>>> nxt;
    std::map<Key, size_t> nxt_at;
    std::map<Key, Point> coords;
    for (const std::pair<Point, Point>& edge : edges) {
        const Point& a = edge.first;
        const Point& b = edge.second;
        Key ka = key(a);
        auto it = nxt_at.find(ka);
        if (it == nxt_at.end()) {
            it = nxt_at.emplace(ka, nxt.size()).first;
            nxt.push_back({ka, {}});
        }
        nxt[it->second].second.push_back(key(b));
        coords[key(a)] = a;
        coords[key(b)] = b;
    }
    std::vector<Points> out;
    std::set<Key> used;
    for (const auto& entry : nxt) {
        const Key& start = entry.first;
        if (used.count(start)) continue;
        Points loop;
        Key cur = start;
        while (nxt_at.count(cur) && !used.count(cur)) {
            used.insert(cur);
            loop.push_back(coords.at(cur));
            std::vector<Key> options;
            for (const Key& k : nxt[nxt_at.at(cur)].second)
                if (!used.count(k)) options.push_back(k);
            if (options.empty()) break;
            cur = options[0];
        }
        if (loop.size() >= 3) out.push_back(loop);
    }
    return out;
}

}  // namespace detail

inline Mesh union_(const std::vector<Mesh>& meshes) {
    if (meshes.empty()) return Mesh();
    Mesh out = meshes[0];
    for (size_t k = 1; k < meshes.size(); ++k) {
        const Mesh& other = meshes[k];
        if (other.F.empty()) continue;
        if (out.F.empty()) out = other;
        else if (detail::boxes_apart(out, other)) out = merge({out, other});   // nothing to cut: just stack
        else out = detail::csg(out, other, "union");
    }
    return out;
}
inline Mesh union_(const Mesh& A, const Mesh& B) { return union_(std::vector<Mesh>{A, B}); }

inline Mesh difference(const Mesh& A, const std::vector<Mesh>& others, std::optional<Color> paint) {
    Mesh out = A;
    for (const Mesh& other : others) {
        if (other.F.empty() || out.F.empty() || detail::boxes_apart(out, other)) continue;
        out = detail::csg(out, other, "difference", paint);
    }
    return out;
}
inline Mesh difference(const Mesh& A, const Mesh& B, std::optional<Color> paint) {
    return difference(A, std::vector<Mesh>{B}, paint);
}

inline Mesh intersect(const std::vector<Mesh>& meshes) {
    if (meshes.empty()) return Mesh();
    Mesh out = meshes[0];
    for (size_t k = 1; k < meshes.size(); ++k) {
        const Mesh& other = meshes[k];
        if (out.F.empty() || other.F.empty() || detail::boxes_apart(out, other)) return Mesh();
        out = detail::csg(out, other, "intersection");
    }
    return out;
}
inline Mesh intersect(const Mesh& A, const Mesh& B) { return intersect(std::vector<Mesh>{A, B}); }

inline Mesh symmetric_difference(const Mesh& A, const Mesh& B) {
    Mesh a_only = difference(A, B);
    Mesh b_only = difference(B, A);
    return union_(a_only, b_only);
}

inline Mesh add_solids(const std::vector<Mesh>& meshes) { return union_(meshes); }
inline Mesh add_solids(const Mesh& A, const Mesh& B) { return union_(A, B); }
inline Mesh subtract(const Mesh& A, const std::vector<Mesh>& others) { return difference(A, others); }
inline Mesh subtract(const Mesh& A, const Mesh& B) { return difference(A, B); }
inline Mesh common(const std::vector<Mesh>& meshes) { return intersect(meshes); }
inline Mesh common(const Mesh& A, const Mesh& B) { return intersect(A, B); }

// ---------------------------------------------------------------------------
//  Cheap relatives of the boolean operations
// ---------------------------------------------------------------------------

// "Behind" means the side the normal points away from, so cut(M, {0, 0, 0}, {0, 1, 0}) keeps the
// bottom half and throws the top away.  Cut twice with opposite normals to keep a slab.  Far
// cheaper than a full boolean, because a plane needs no searching.  With cap = true the exposed
// cross-section is closed with a new flat face, so the result stays watertight.
inline Mesh cut(const Mesh& M, const Point& point, const Point& normal, bool cap, std::optional<Color> color) {
    using namespace detail;
    Point n = unit(normal);
    double w = dot(n, point);
    Mesh out;
    std::vector<std::pair<Point, Point>> rim;
    for (size_t k = 0; k < M.F.size() && k < M.C.size(); ++k) {
        Points pts;
        for (int i : M.F[k]) pts.push_back(M.V[i]);
        Poly poly(pts, M.C[k]);
        std::vector<Poly> front, back;
        split(n, w, poly, front, back, 1e-12);
        for (const Poly& p : back) {
            out.add_polygon(p.pts, p.c);
            size_t m = p.pts.size();
            for (size_t i = 0; i < m; ++i) {
                const Point& a = p.pts[i];
                const Point& b = p.pts[(i + 1) % m];
                if (std::fabs(dot(n, a) - w) < 1e-9 && std::fabs(dot(n, b) - w) < 1e-9) rim.push_back({a, b});
            }
        }
    }
    if (cap && !rim.empty()) {
        for (const Points& loop : loops(rim))              // (the rim runs the way the faces round it do;
            if (loop.size() >= 3)                          //  the cap runs back along it, facing out)
                out.add_polygon(Points(loop.rbegin(), loop.rend()), color ? *color : (!M.C.empty() ? M.C[0] : DEFAULT_COLOR));
    }
    detail::weld(out, 1e-7);
    detail::drop_degenerate(out);
    detail::drop_unused(out);
    return out;
}

inline bool inside(const Mesh& M, const Point& p) {
    detail::Solid solid(M);
    return solid.contains(p);
}
inline std::vector<bool> inside(const Mesh& M, const Points& ps) {
    detail::Solid solid(M);
    if (ps.empty()) throw std::out_of_range("list index out of range");   // (add.py takes [] for a point)
    std::vector<bool> out;
    for (const Point& q : ps) out.push_back(solid.contains(q));
    return out;
}

}  // namespace add

namespace add {

namespace detail {

inline long long subd_mod(long long a, long long b) {
    long long r = a % b;
    return r < 0 ? r + b : r;
}

inline long long subd_floordiv(long long a, long long b) {
    long long q = a / b;
    return (a % b != 0 && a < 0) ? q - 1 : q;
}

inline int subd_index(const std::vector<int>& xs, int x) {
    for (size_t i = 0; i < xs.size(); ++i)
        if (xs[i] == x) return (int)i;
    throw std::invalid_argument(std::to_string(x) + " is not in list");
}

inline double subd_pow(double x, double y) {
    if (x == 0.0 && y < 0.0 && std::isfinite(y))
        throw std::domain_error("0.0 cannot be raised to a negative power");
    double r = py_pow(x, y);
    if (std::isinf(r) && std::isfinite(x) && std::isfinite(y))
        throw std::overflow_error("(34, 'Numerical result out of range')");
    return r;
}

// -- the topology -------------------------------------------------------------

inline Topo::Topo(Points V_, std::vector<Face> F_) : V(std::move(V_)), F(std::move(F_)) {
    int nv = (int)V.size(), nf = (int)F.size();
    VF.assign(nv, {});
    VE.assign(nv, {});
    FE.assign(nf, {});
    FN.assign(nf, {});
    std::unordered_map<unsigned long long, int> emap;         // (only looked up: no order needed)
    for (int f = 0; f < nf; ++f) {
        const Face& p = F[f];
        int m = (int)p.size();
        if (m < 3) throw std::invalid_argument("face with fewer than 3 vertices");
        std::vector<int> fe(m, 0);
        for (int k = 0; k < m; ++k) {
            int a = p[k], b = p[(k + 1) % m];
            if (a == b) throw std::invalid_argument("degenerate edge in face " + std::to_string(f));
            int k0 = a < b ? a : b, k1 = a < b ? b : a;
            unsigned long long key = ((unsigned long long)(unsigned int)k0 << 32) | (unsigned int)k1;
            auto it = emap.find(key);
            int e;
            if (it == emap.end()) {
                e = (int)E.size();
                E.push_back({k0, k1, f, -1});
                emap.emplace(key, e);
                VE.at(a).push_back(e);
                VE.at(b).push_back(e);
            } else {
                e = it->second;
                std::array<int, 4>& ed = E[e];
                if (ed[3] >= 0) throw std::invalid_argument("non-manifold edge (more than two faces meet along it)");
                if (ed[2] == f) throw std::invalid_argument("edge used twice by the same face");
                ed[3] = f;
            }
            fe[k] = e;
        }
        FE[f] = fe;
        for (int k = 0; k < m; ++k) VF.at(p[k]).push_back(f);
    }
    for (int f = 0; f < nf; ++f) {
        const std::vector<int>& fe = FE[f];
        std::vector<int> fn;
        fn.reserve(fe.size());
        for (int e : fe) fn.push_back(E[e][2] == f ? E[e][3] : E[e][2]);
        FN[f] = fn;
    }
    boundary.assign(nv, false);
    for (const std::array<int, 4>& ed : E)
        if (ed[3] < 0) {
            boundary[ed[0]] = true;
            boundary[ed[1]] = true;
        }
}

inline bool Topo::all_quads() const {
    for (const Face& f : F)
        if (f.size() != 4) return false;
    return true;
}

inline Point Topo::centroid(int f) const {
    const Face& p = F[f];
    double n = (double)p.size();
    Point out;
    for (int a = 0; a < 3; ++a) {
        double s = 0.0;                                        // (add.py's _total: in order)
        for (int v : p) s = s + V[v][a];
        out[a] = s / n;
    }
    return out;
}

inline std::optional<OrderedRing> Topo::ordered_ring(int v) const {
    const std::vector<int>& vf = VF[v];
    if (vf.empty()) return std::nullopt;
    int start = vf[0];
    for (int f : vf) {
        int k = subd_index(F[f], v);
        if (FN[f][k] < 0) {
            start = f;
            break;
        }
    }
    OrderedRing R;
    int f = start;
    int guard = 0;
    while (true) {
        const Face& p = F[f];
        int m = (int)p.size();
        int k = subd_index(p, v);
        int nxt = p[(k + 1) % m], prv = p[(k + m - 1) % m];
        if (R.faces.empty()) R.nbrs.push_back(nxt);
        R.faces.push_back(f);
        R.nbrs.push_back(prv);
        int g = FN[f][(k + m - 1) % m];
        if (g < 0) break;
        if (g == start) {
            R.nbrs.pop_back();
            break;
        }
        f = g;
        guard += 1;
        if (guard > (int)vf.size() + 2) return std::nullopt;
    }
    if (R.faces.size() != vf.size()) return std::nullopt;
    return R;
}

// -- Catmull-Clark subdivision and its limit ------------------------------------

inline std::pair<Topo, std::vector<int>> cc_subdivide(const Topo& T) {
    const Points& V = T.V;
    const std::vector<Face>& F = T.F;
    const std::vector<std::array<int, 4>>& E = T.E;
    int nv = (int)V.size(), ne = (int)E.size(), nf = (int)F.size();
    Points R(nv + ne + nf);
    for (int f = 0; f < nf; ++f) R[nv + ne + f] = T.centroid(f);
    for (int e = 0; e < ne; ++e) {
        int a = E[e][0], b = E[e][1], f0 = E[e][2], f1 = E[e][3];
        const Point& pa = V[a];
        const Point& pb = V[b];
        if (f1 < 0) {
            R[nv + e] = {(pa[0] + pb[0]) * 0.5, (pa[1] + pb[1]) * 0.5, (pa[2] + pb[2]) * 0.5};
        } else {
            const Point& c0 = R[nv + ne + f0];
            const Point& c1 = R[nv + ne + f1];
            R[nv + e] = {(pa[0] + pb[0] + c0[0] + c1[0]) * 0.25, (pa[1] + pb[1] + c0[1] + c1[1]) * 0.25,
                         (pa[2] + pb[2] + c0[2] + c1[2]) * 0.25};
        }
    }
    for (int v = 0; v < nv; ++v) {
        const Point& p = V[v];
        const std::vector<int>& VF = T.VF[v];
        const std::vector<int>& VE = T.VE[v];
        if (VF.empty()) {
            R[v] = p;
            continue;
        }
        if (T.boundary[v]) {
            if (VF.size() <= 1) {
                R[v] = p;
                continue;
            }
            double s[3] = {0.0, 0.0, 0.0};
            int cnt = 0;
            for (int e : VE) {
                const std::array<int, 4>& ed = E[e];
                if (ed[3] < 0) {
                    const Point& q = V[ed[0] == v ? ed[1] : ed[0]];
                    s[0] += q[0];
                    s[1] += q[1];
                    s[2] += q[2];
                    cnt += 1;
                }
            }
            if (cnt != 2) {
                R[v] = p;
                continue;
            }
            R[v] = {(s[0] + 6 * p[0]) / 8.0, (s[1] + 6 * p[1]) / 8.0, (s[2] + 6 * p[2]) / 8.0};
        } else {
            int n = (int)VE.size();
            double Q[3] = {0.0, 0.0, 0.0};
            double Rm[3] = {0.0, 0.0, 0.0};
            for (int f : VF) {
                const Point& c = R[nv + ne + f];
                Q[0] += c[0];
                Q[1] += c[1];
                Q[2] += c[2];
            }
            for (int e : VE) {
                const std::array<int, 4>& ed = E[e];
                const Point& pa = V[ed[0]];
                const Point& pb = V[ed[1]];
                Rm[0] += (pa[0] + pb[0]) * 0.5;
                Rm[1] += (pa[1] + pb[1]) * 0.5;
                Rm[2] += (pa[2] + pb[2]) * 0.5;
            }
            double nfc = (double)VF.size();
            R[v] = {(Q[0] / nfc + 2 * Rm[0] / n + (n - 3) * p[0]) / n,
                    (Q[1] / nfc + 2 * Rm[1] / n + (n - 3) * p[1]) / n,
                    (Q[2] / nfc + 2 * Rm[2] / n + (n - 3) * p[2]) / n};
        }
    }
    std::vector<Face> newF;
    std::vector<int> parent;
    for (int f = 0; f < nf; ++f) {
        const Face& p = F[f];
        const std::vector<int>& fe = T.FE[f];
        int m = (int)p.size();
        for (int k = 0; k < m; ++k) {
            newF.push_back({p[k], nv + fe[k], nv + ne + f, nv + fe[(k + m - 1) % m]});
            parent.push_back(f);
        }
    }
    return {Topo(std::move(R), std::move(newF)), std::move(parent)};
}

inline double cc_lambda(int N) {
    if (N == 4) return 0.5;
    if (N == 0) throw std::domain_error("float division by zero");
    double c = std::cos(2 * pi / N);
    return (c + 5 + std::sqrt((c + 1) * (c + 9))) / 16.0;
}

inline double cc_gamma(int N) {
    if (N == 4) return 1.0;
    return 1.0 / (-(std::log(cc_lambda(N)) / std::log(2.0)));      // (math.log(x, 2) is log(x) / log(2))
}

inline Points cc_limit_positions(const Topo& T) {
    if (!T.all_quads()) {
        Points L = cc_limit_positions(cc_subdivide(T).first);
        L.resize(T.V.size());                                  // [:len(T.V)]
        return L;
    }
    const Points& V = T.V;
    const std::vector<std::array<int, 4>>& E = T.E;
    Points L(V.size());
    for (int v = 0; v < (int)V.size(); ++v) {
        const Point& p = V[v];
        const std::vector<int>& VF = T.VF[v];
        if (VF.empty()) {
            L[v] = p;
            continue;
        }
        if (T.boundary[v]) {
            if (VF.size() <= 1) {
                L[v] = p;
                continue;
            }
            double s[3] = {0.0, 0.0, 0.0};
            int cnt = 0;
            for (int e : T.VE[v]) {
                const std::array<int, 4>& ed = E[e];
                if (ed[3] < 0) {
                    const Point& q = V[ed[0] == v ? ed[1] : ed[0]];
                    s[0] += q[0];
                    s[1] += q[1];
                    s[2] += q[2];
                    cnt += 1;
                }
            }
            if (cnt != 2) {
                L[v] = p;
                continue;
            }
            L[v] = {(s[0] + 4 * p[0]) / 6.0, (s[1] + 4 * p[1]) / 6.0, (s[2] + 4 * p[2]) / 6.0};
        } else {
            std::optional<OrderedRing> ring = T.ordered_ring(v);
            if (!ring) {
                L[v] = p;
                continue;
            }
            const std::vector<int>& nbrs = ring->nbrs;
            const std::vector<int>& faces = ring->faces;
            int n = (int)nbrs.size();
            double se[3] = {0.0, 0.0, 0.0};
            double sf[3] = {0.0, 0.0, 0.0};
            for (int j = 0; j < n; ++j) {
                const Point& q = V[nbrs[j]];
                se[0] += q[0];
                se[1] += q[1];
                se[2] += q[2];
                const Face& poly = T.F[faces.at(j)];
                const Point& d = V[poly[(subd_index(poly, v) + 2) % 4]];
                sf[0] += d[0];
                sf[1] += d[1];
                sf[2] += d[2];
            }
            double den = (double)(n * (n + 5));
            L[v] = {(n * n * p[0] + 4 * se[0] + sf[0]) / den, (n * n * p[1] + 4 * se[1] + sf[1]) / den,
                    (n * n * p[2] + 4 * se[2] + sf[2]) / den};
        }
    }
    return L;
}

inline std::optional<std::pair<Point, Point>> cc_limit_tangents(const Topo& T, int v) {
    if (T.boundary[v]) return std::nullopt;
    std::optional<OrderedRing> ring = T.ordered_ring(v);
    if (!ring) return std::nullopt;
    const std::vector<int>& nbrs = ring->nbrs;
    const std::vector<int>& faces = ring->faces;
    for (int f : faces)
        if (T.F[f].size() != 4) return cc_limit_tangents(cc_subdivide(T).first, v);
    int n = (int)nbrs.size();
    double c = std::cos(2 * pi / n);
    double A = 1 + c + std::sqrt((c + 1) * (c + 9));
    Point t1{0.0, 0.0, 0.0};
    Point t2{0.0, 0.0, 0.0};
    for (int j = 0; j < n; ++j) {
        double a0 = 2 * pi * j / n;
        double a1 = 2 * pi * (j + 1) / n;
        const Face& poly = T.F[faces.at(j)];
        const Point& fj = T.V[poly[(subd_index(poly, v) + 2) % 4]];
        const Point& e = T.V[nbrs[j]];
        double w1 = A * std::cos(a0), w2 = std::cos(a0) + std::cos(a1);
        double s1 = A * std::sin(a0), s2 = std::sin(a0) + std::sin(a1);
        for (int a = 0; a < 3; ++a) {
            t1[a] += e[a] * w1 + fj[a] * w2;
            t2[a] += e[a] * s1 + fj[a] * s2;
        }
    }
    return std::make_pair(t1, t2);
}

// -- the regular patches: bicubic B-splines -------------------------------------

inline std::array<double, 4> bspline_basis(double t) {
    double t2 = t * t;
    double t3 = t2 * t;
    return {(1 - 3 * t + 3 * t2 - t3) / 6.0, (4 - 6 * t2 + 3 * t3) / 6.0, (1 + 3 * t + 3 * t2 - 3 * t3) / 6.0,
            t3 / 6.0};
}

inline Point eval_bicubic(const BicubicNet& P, double u, double v) {
    std::array<double, 4> Nu = bspline_basis(u);
    std::array<double, 4> Nv = bspline_basis(v);
    double x = 0.0, y = 0.0, z = 0.0;
    for (int i = 0; i < 4; ++i) {
        double wi = Nu[i];
        if (wi == 0.0) continue;
        const std::array<Point, 4>& row = P[i];
        for (int j = 0; j < 4; ++j) {
            double w = wi * Nv[j];
            const Point& c = row[j];
            x += c[0] * w;
            y += c[1] * w;
            z += c[2] * w;
        }
    }
    return {x, y, z};
}

inline std::optional<BicubicNet> regular_stencil(const Topo& T, int f) {
    const Face& q = T.F[f];
    if (q.size() != 4) return std::nullopt;
    const Points& V = T.V;
    BicubicNet P{};
    int have[4][4] = {};
    P[1][1] = V[q[0]];
    P[2][1] = V[q[1]];
    P[2][2] = V[q[2]];
    P[1][2] = V[q[3]];
    have[1][1] = have[2][1] = have[2][2] = have[1][2] = 1;
    const int ci[4] = {1, 2, 2, 1};
    const int cj[4] = {1, 1, 2, 2};
    for (int k = 0; k < 4; ++k) {
        int v = q[k];
        bool bnd = T.boundary[v];
        int nfc = (int)T.VF[v].size();
        if (!bnd && (nfc != 4 || T.VE[v].size() != 4)) return std::nullopt;
        if (bnd && nfc > 2) return std::nullopt;
        std::optional<OrderedRing> ring = T.ordered_ring(v);
        if (!ring) return std::nullopt;
        const std::vector<int>& nb = ring->nbrs;
        const std::vector<int>& fc = ring->faces;
        for (int g : fc)
            if (T.F[g].size() != 4) return std::nullopt;
        int vn = q[(k + 1) % 4], vp = q[(k + 3) % 4];
        const int dn[2] = {ci[(k + 1) % 4] - ci[k], cj[(k + 1) % 4] - cj[k]};
        const int dp[2] = {ci[(k + 3) % 4] - ci[k], cj[(k + 3) % 4] - cj[k]};
        int n = (int)nb.size();
        auto at = std::find(nb.begin(), nb.end(), vn);
        if (at == nb.end()) return std::nullopt;
        int s = (int)(at - nb.begin());
        if (nb[(s + 1) % n] != vp) return std::nullopt;
        const int dirs[4][2] = {{dn[0], dn[1]}, {dp[0], dp[1]}, {-dn[0], -dn[1]}, {-dp[0], -dp[1]}};
        for (int idx = 0; idx < n; ++idx) {
            int off = (int)subd_mod(idx - s, 4);
            int gi = ci[k] + dirs[off][0], gj = cj[k] + dirs[off][1];
            if (gi < 0 || gi > 3 || gj < 0 || gj > 3) return std::nullopt;
            P[gi][gj] = V[nb[idx]];
            have[gi][gj] = 1;
        }
        for (int idx = 0; idx < (int)fc.size(); ++idx) {
            int off = (int)subd_mod(idx - s, 4);
            const Face& poly = T.F[fc[idx]];
            int diag = poly[(subd_index(poly, v) + 2) % 4];
            int gi = ci[k] + dirs[off][0] + dirs[(off + 1) % 4][0];
            int gj = cj[k] + dirs[off][1] + dirs[(off + 1) % 4][1];
            if (gi < 0 || gi > 3 || gj < 0 || gj > 3) return std::nullopt;
            P[gi][gj] = V[diag];
            have[gi][gj] = 1;
        }
    }
    const bool miss[4] = {!have[0][1] && !have[0][2], !have[3][1] && !have[3][2], !have[1][0] && !have[2][0],
                          !have[1][3] && !have[2][3]};
    if (have[0][1] != have[0][2] || have[3][1] != have[3][2] || have[1][0] != have[2][0] ||
        have[1][3] != have[2][3])
        return std::nullopt;

    auto refl = [](const Point& a, const Point& b) -> Point {
        return {2 * a[0] - b[0], 2 * a[1] - b[1], 2 * a[2] - b[2]};
    };
    auto bil = [](const Point& a, const Point& b, const Point& c) -> Point {
        return {a[0] + b[0] - c[0], a[1] + b[1] - c[1], a[2] + b[2] - c[2]};
    };
    for (int t : {1, 2}) {
        if (miss[0]) P[0][t] = refl(P[1][t], P[2][t]);
        if (miss[1]) P[3][t] = refl(P[2][t], P[1][t]);
        if (miss[2]) P[t][0] = refl(P[t][1], P[t][2]);
        if (miss[3]) P[t][3] = refl(P[t][2], P[t][1]);
    }
    if (!have[0][0])
        P[0][0] = miss[0] ? refl(P[1][0], P[2][0]) : miss[2] ? refl(P[0][1], P[0][2]) : bil(P[0][1], P[1][0], P[1][1]);
    if (!have[3][0])
        P[3][0] = miss[1] ? refl(P[2][0], P[1][0]) : miss[2] ? refl(P[3][1], P[3][2]) : bil(P[3][1], P[2][0], P[2][1]);
    if (!have[0][3])
        P[0][3] = miss[0] ? refl(P[1][3], P[2][3]) : miss[3] ? refl(P[0][2], P[0][1]) : bil(P[0][2], P[1][3], P[1][2]);
    if (!have[3][3])
        P[3][3] = miss[1] ? refl(P[2][3], P[1][3]) : miss[3] ? refl(P[3][2], P[3][1]) : bil(P[3][2], P[2][3], P[2][2]);
    return P;
}

// -- the irregular patches: subdivided only as deep as needed -------------------

inline Topo neighbourhood(const Topo& T, int f, int origin_corner) {
    std::vector<int> faces{f};
    std::unordered_set<int> seen{f};                           // (only looked up: the order is faces')
    for (int v : T.F[f])
        for (int g : T.VF[v])
            if (!seen.count(g)) {
                seen.insert(g);
                faces.push_back(g);
            }
    std::unordered_map<int, int> vmap;
    Points LV;
    std::vector<Face> LF;
    for (int g : faces) {
        const Face& poly = T.F[g];
        int m = (int)poly.size();
        int start = g == f ? origin_corner : 0;
        Face out;
        for (int k = 0; k < m; ++k) {
            int v = poly[(start + k) % m];
            auto it = vmap.find(v);
            int idx;
            if (it == vmap.end()) {
                idx = (int)LV.size();
                LV.push_back(T.V[v]);
                vmap.emplace(v, idx);
            } else {
                idx = it->second;
            }
            out.push_back(idx);
        }
        LF.push_back(out);
    }
    return Topo(std::move(LV), std::move(LF));
}

inline PatchTree::PatchTree(const Topo& T, int f) : root(node(neighbourhood(T, f, 0), 0)) {}

inline std::unique_ptr<PatchTree::Node> PatchTree::node(Topo L, int depth) {
    std::unique_ptr<Node> nd(new Node());
    nd->M = std::move(L);
    nd->depth = depth;
    nd->P = regular_stencil(nd->M, 0);
    return nd;
}

inline PatchTree::Node* PatchTree::child(Node& nd, int k) {
    if (nd.child[k]) return nd.child[k].get();
    if (!nd.sub) nd.sub = cc_subdivide(nd.M).first;
    static const int origin[4] = {0, 3, 2, 1};
    nd.child[k] = node(neighbourhood(*nd.sub, k, origin[k]), nd.depth + 1);
    return nd.child[k].get();
}

inline Point PatchTree::eval(double u, double v) {
    Node* nd = root.get();
    int depth = 0;
    while (!nd->P) {
        if (depth >= MAX_DEPTH) {
            Points L = cc_limit_positions(nd->M);
            int corner = u < 0.5 ? (v < 0.5 ? 0 : 3) : (v < 0.5 ? 1 : 2);
            return L[nd->M.F[0][corner]];
        }
        int k;
        if (u < 0.5) {
            if (v < 0.5) {
                k = 0; u = 2 * u; v = 2 * v;
            } else {
                k = 3; u = 2 * u; v = 2 * v - 1;
            }
        } else {
            if (v < 0.5) {
                k = 1; u = 2 * u - 1; v = 2 * v;
            } else {
                k = 2; u = 2 * u - 1; v = 2 * v - 1;
            }
        }
        nd = child(*nd, k);
        depth += 1;
    }
    return eval_bicubic(*nd->P, u, v);
}

// -- the reparameterisation (Sections 4 and 5 of the paper) ---------------------

inline double nu_norm(double a, double b, double p) {
    if (p > 64) return std::max(a, b);                         // (Python's max: the first of equals)
    double ap = subd_pow(a, p), bp = subd_pow(b, p);
    double base = (ap + bp) / (1 + ap * bp);
    if (p == 0) throw std::domain_error("float division by zero");      // (add.py: 1.0 / p)
    return subd_pow(base, 1.0 / p);
}

inline PolygonDomain::PolygonDomain(int m_) : m(m_) {
    for (int k = 0; k < m; ++k) P.push_back({std::cos(2 * pi * k / m), std::sin(2 * pi * k / m)});
    for (int k = 0; k < m; ++k)
        E.push_back({(P[k][0] + P[(k + 1) % m][0]) / 2.0, (P[k][1] + P[(k + 1) % m][1]) / 2.0});
}

inline const PolygonDomain& PolygonDomain::get(int m) {
    static std::map<int, PolygonDomain> cache;                 // (references stay valid)
    auto it = cache.find(m);
    if (it == cache.end()) it = cache.emplace(m, PolygonDomain(m)).first;
    return it->second;
}

inline Point2 PolygonDomain::kite_map(int k, double u, double v) const {
    const Point2& a = P[k];
    const Point2& b = E[k];
    const Point2& d = E[(k + m - 1) % m];
    double wa = (1 - u) * (1 - v), wb = u * (1 - v), wd = (1 - u) * v;
    return {a[0] * wa + b[0] * wb + d[0] * wd, a[1] * wa + b[1] * wb + d[1] * wd};
}

inline int PolygonDomain::kite_of(const Point2& x) const {
    if (x[0] == 0 && x[1] == 0) return 0;
    double t = std::atan2(x[1], x[0]) / (2 * pi) * m + 0.5;
    return (int)subd_mod(cell_floor(t), m);                    // int(math.floor(t)) % m
}

inline Point2 PolygonDomain::kite_inverse(int k, const Point2& x) const {
    const Point2& a = P[k];
    const Point2& b = E[k];
    const Point2& d = E[(k + m - 1) % m];
    const double e1[2] = {b[0] - a[0], b[1] - a[1]};
    const double e2[2] = {d[0] - a[0], d[1] - a[1]};
    const double e3[2] = {-(b[0] + d[0] - a[0]), -(b[1] + d[1] - a[1])};
    double u = 0.5, v = 0.5;
    for (int it = 0; it < 40; ++it) {
        double rx = a[0] + e1[0] * u + e2[0] * v + e3[0] * u * v - x[0];
        double ry = a[1] + e1[1] * u + e2[1] * v + e3[1] * u * v - x[1];
        double jux = e1[0] + e3[0] * v, juy = e1[1] + e3[1] * v;
        double jvx = e2[0] + e3[0] * u, jvy = e2[1] + e3[1] * u;
        double det = jux * jvy - juy * jvx;
        if (std::fabs(det) < 1e-300) break;
        double du = (rx * jvy - ry * jvx) / det;
        double dv = (jux * ry - juy * rx) / det;
        u -= du;
        v -= dv;
        if (std::fabs(du) + std::fabs(dv) < 1e-16) break;
    }
    return {std::min(1.0, std::max(0.0, u)), std::min(1.0, std::max(0.0, v))};    // (as Python's min/max)
}

inline std::vector<double> PolygonDomain::wachspress(const Point2& x) const {
    std::vector<double> A(m, 0.0);
    for (int j = 0; j < m; ++j) {
        const Point2& a = P[j];
        const Point2& b = P[(j + 1) % m];
        double s = (a[0] - x[0]) * (b[1] - x[1]) - (a[1] - x[1]) * (b[0] - x[0]);
        A[j] = s > 0 ? s : 0.0;
    }
    std::vector<double> lam(m, 0.0);
    double total = 0.0;
    for (int i = 0; i < m; ++i) {
        double w = 1.0;
        int im = (i + m - 1) % m;
        for (int j = 0; j < m; ++j)
            if (j != i && j != im) w *= A[j];
        lam[i] = w;
        total += w;
    }
    if (total > 0) {
        for (int i = 0; i < m; ++i) lam[i] /= total;
    } else {
        int best = 0;
        bool have_bd = false;                                  // (add.py: bd = None)
        double bd = 0.0;
        for (int i = 0; i < m; ++i) {
            double dx = P[i][0] - x[0], dy = P[i][1] - x[1];
            double d = dx * dx + dy * dy;
            if (!have_bd || d < bd) {
                bd = d;
                best = i;
                have_bd = true;
            }
        }
        for (int i = 0; i < m; ++i) lam[i] = 0.0;
        lam[best] = 1.0;
    }
    return lam;
}

inline double PolygonDomain::corner_nu(const std::vector<double>& lam, int k, double p) const {
    int kp = (k + 1) % m, km = (k + m - 1) % m;
    double s = 1 - lam[k] - lam[km], t = 1 - lam[k] - lam[kp];
    if (m == 3) {
        double ds = 1 - lam[km], dt = 1 - lam[kp];
        s = ds > 1e-300 ? s / ds : 0.0;
        t = dt > 1e-300 ? t / dt : 0.0;
    }
    s = std::min(1.0, std::max(0.0, s));
    t = std::min(1.0, std::max(0.0, t));
    return nu_norm(s, t, p);
}

inline FaceReparam face_reparam(const PolygonDomain& dom, const std::vector<double>& gamma, double gamma_centre,
                                double p) {
    FaceReparam R{dom, gamma, gamma_centre, p};
    R.any_corner = false;
    for (double g : gamma)
        if (g != 1) {
            R.any_corner = true;
            break;
        }
    R.trivial = !R.any_corner && gamma_centre == 1;
    return R;
}

inline Point2 FaceReparam::apply(const Point2& x) const {
    const int m = dom.m;
    Point2 y = x;
    if (any_corner) {
        std::vector<double> lam = dom.wachspress(x);
        double y0 = 0.0, y1 = 0.0;
        for (int k = 0; k < m; ++k) {
            double w = lam[k];
            if (w == 0) continue;
            if (gamma[k] == 1) {
                y0 += x[0] * w;
                y1 += x[1] * w;
                continue;
            }
            double nu = dom.corner_nu(lam, k, p);
            double r = nu > 0 ? subd_pow(nu, gamma[k] - 1) : 0.0;
            const Point2& Pk = dom.P[k];
            y0 += (Pk[0] + (x[0] - Pk[0]) * r) * w;
            y1 += (Pk[1] + (x[1] - Pk[1]) * r) * w;
        }
        y = {y0, y1};
    }
    if (gamma_centre != 1) {
        int k = dom.kite_of(y);
        Point2 uv = dom.kite_inverse(k, y);
        double nuF = nu_norm(1 - uv[0], 1 - uv[1], p);
        if (nuF > 0) {
            double r = subd_pow(nuF, gamma_centre - 1);
            y = {y[0] * r, y[1] * r};
        }
    }
    return y;
}

inline long long face_node_count(long long m, long long n) {
    long long q = subd_floordiv(n, 2);
    if (subd_mod(n, 2) == 1) return m * q * q;
    return q >= 1 ? m * (q - 1) * (q - 1) + m * (q - 1) + 1 : 0;
}

// -- getting a mesh ready -------------------------------------------------------

inline std::pair<Topo, Mesh> topology_of(const Mesh& M0, bool repair) {
    Mesh M = repair ? repair_for_subdivision(M0) : M0.copy();
    Topo T(M.V, M.F);
    return {std::move(T), std::move(M)};
}

inline Mesh repair_for_subdivision(const Mesh& M0) {
    Mesh M = M0.copy();
    std::array<Point, 2> lohi = add::bbox(M);
    double diag = detail::norm(detail::sub(lohi[1], lohi[0]));
    double tol = 1e-7 * (diag > 0 ? diag : 1.0);
    detail::weld(M, tol);
    detail::drop_degenerate(M);
    detail::drop_internal(M);
    detail::dedup_faces(M);
    M = add::heal(M, 1e-6 * (diag > 0 ? diag : 1.0));
    detail::drop_degenerate(M);
    detail::cut_non_manifold(M);
    detail::drop_unused(M);
    if (!M.F.empty()) M = add::fix_normals(M);
    return M;
}

inline Mesh& cut_non_manifold(Mesh& M) {
    typedef std::pair<int, int> Corner;                        // (face, corner)
    for (int pass = 0; pass < 4; ++pass) {
        // emap: edge -> the corners it leaves from, in the order add.py's dict keeps the edges.
        std::vector<std::vector<Corner>> emap;
        std::unordered_map<unsigned long long, size_t> where;
        for (int f = 0; f < (int)M.F.size(); ++f) {
            const Face& poly = M.F[f];
            int m = (int)poly.size();
            for (int k = 0; k < m; ++k) {
                int a = poly[k], b = poly[(k + 1) % m];
                int k0 = a < b ? a : b, k1 = a < b ? b : a;
                unsigned long long key = ((unsigned long long)(unsigned int)k0 << 32) | (unsigned int)k1;
                auto it = where.find(key);
                if (it == where.end()) {
                    where.emplace(key, emap.size());
                    emap.push_back(std::vector<Corner>{Corner(f, k)});
                } else {
                    emap[it->second].push_back(Corner(f, k));
                }
            }
        }
        bool any_bad = false;
        std::vector<std::vector<int>> partner;
        partner.reserve(M.F.size());
        for (const Face& poly : M.F) partner.push_back(std::vector<int>(poly.size(), -1));
        std::vector<Corner> detach;
        for (const std::vector<Corner>& lst : emap) {
            if (lst.size() == 2) {
                int f0 = lst[0].first, k0 = lst[0].second, f1 = lst[1].first, k1 = lst[1].second;
                partner[f0][k0] = f1;
                partner[f1][k1] = f0;
                continue;
            }
            if (lst.size() < 2) continue;
            any_bad = true;
            std::vector<bool> used(lst.size(), false);
            for (size_t i = 0; i < lst.size(); ++i) {
                if (used[i]) continue;
                int fa = lst[i].first, ka = lst[i].second;
                int a0 = M.F[fa][ka];
                long long best = -1;
                for (size_t j = i + 1; j < lst.size(); ++j)
                    if (!used[j] && M.F[lst[j].first][lst[j].second] != a0) {
                        best = (long long)j;
                        break;
                    }
                if (best < 0)
                    for (size_t j = i + 1; j < lst.size(); ++j)
                        if (!used[j]) {
                            best = (long long)j;
                            break;
                        }
                if (best < 0) {
                    detach.push_back(lst[i]);
                    used[i] = true;
                    continue;
                }
                used[i] = true;
                used[(size_t)best] = true;
                int fb = lst[(size_t)best].first, kb = lst[(size_t)best].second;
                partner[fa][ka] = fb;
                partner[fb][kb] = fa;
            }
        }
        for (const Corner& c : detach) {
            int f = c.first, k = c.second;
            int m = (int)M.F[f].size();
            for (int idx : {k, (k + 1) % m}) {
                Point copy = M.V[M.F[f][idx]];
                M.V.push_back(copy);
                M.F[f][idx] = (int)M.V.size() - 1;
            }
        }
        std::vector<std::vector<Corner>> vf(M.V.size());
        for (int f = 0; f < (int)M.F.size(); ++f) {
            const Face& poly = M.F[f];
            for (int k = 0; k < (int)poly.size(); ++k) vf.at(poly[k]).push_back({f, k});
        }
        int nv0 = (int)M.V.size();
        bool any_split = false;
        for (int v = 0; v < nv0; ++v) {
            const std::vector<Corner>& lst = vf[v];
            if (lst.size() <= 1) continue;
            std::unordered_map<int, int> pos;                  // face -> its (last) place in lst
            for (int i = 0; i < (int)lst.size(); ++i) pos[lst[i].first] = i;
            std::vector<int> group(lst.size());
            for (int i = 0; i < (int)lst.size(); ++i) group[i] = i;
            auto find = [&group](int x) {
                while (group[x] != x) {
                    group[x] = group[group[x]];
                    x = group[x];
                }
                return x;
            };
            for (int i = 0; i < (int)lst.size(); ++i) {
                int f = lst[i].first, k = lst[i].second;
                int m = (int)M.F[f].size();
                for (int g : {partner[f][k], partner[f][(k + m - 1) % m]}) {
                    if (g < 0) continue;
                    auto it = pos.find(g);
                    if (it != pos.end()) {
                        int a = find(i), b = find(it->second);
                        if (a != b) group[a] = b;
                    }
                }
            }
            std::unordered_map<int, int> fan;                  // (only looked up and counted)
            for (int i = 0; i < (int)lst.size(); ++i) {
                int f = lst[i].first, k = lst[i].second;
                int r = find(i);
                auto it = fan.find(r);
                int vid;
                if (it == fan.end()) {
                    vid = v;
                    if (!fan.empty()) {
                        Point copy = M.V[v];
                        M.V.push_back(copy);
                        vid = (int)M.V.size() - 1;
                    }
                    fan.emplace(r, vid);
                } else {
                    vid = it->second;
                }
                M.F[f][k] = vid;
            }
            if (fan.size() > 1) any_split = true;
        }
        if (!any_bad && !any_split) break;
    }
    return M;
}

}  // namespace detail

inline Mesh catmull_clark(const Mesh& M, int steps, bool repair) {
    std::pair<detail::Topo, Mesh> tm = detail::topology_of(M, repair);
    detail::Topo T = std::move(tm.first);
    std::vector<Color> colors = tm.second.C;
    for (int s = 0; s < steps; ++s) {
        std::pair<detail::Topo, std::vector<int>> sub = detail::cc_subdivide(T);
        T = std::move(sub.first);
        std::vector<Color> next;
        next.reserve(sub.second.size());
        for (int p : sub.second) next.push_back(colors.at(p));
        colors = std::move(next);
    }
    return Mesh(T.V, T.F, colors);
}

inline Mesh smooth(const Mesh& M, int n, bool uniform, bool centre, double p, double scale, bool repair) {
    if (n < 1) throw std::invalid_argument("n must be at least 1");
    std::pair<detail::Topo, Mesh> tm = detail::topology_of(M, repair);
    const detail::Topo& T = tm.first;
    if (T.F.empty()) return Mesh();
    const std::vector<Color>& colors = tm.second.C;
    std::pair<detail::Topo, std::vector<int>> sub1 = detail::cc_subdivide(T);
    const detail::Topo& T1 = sub1.first;
    int q = n / 2;
    bool odd = n % 2 == 1;
    int nv = (int)T.V.size(), ne = (int)T.E.size(), nf = (int)T.F.size();
    std::vector<int> face_base(nf + 1, 0);
    std::vector<int> kite_offset(nf + 1, 0);
    face_base[0] = nv + ne * (n - 1);
    for (int f = 0; f < nf; ++f) {
        int m = (int)T.F[f].size();
        face_base[f + 1] = face_base[f] + (int)detail::face_node_count(m, n);
        kite_offset[f + 1] = kite_offset[f] + m;
    }
    int total = face_base[nf];
    Points GV(total);                                          // (a node never reached stays 0, 0, 0)
    std::vector<bool> done(total, false);
    Points L = detail::cc_limit_positions(T1);
    for (int v = 0; v < nv; ++v) {
        GV[v] = L[v];
        done[v] = true;
    }

    auto edge_node = [&](int f, int k, int t) {
        const Face& poly = T.F[f];
        int m = (int)poly.size();
        int a = poly[k], b = poly[(k + 1) % m];
        int e = T.FE[f][k];
        int tt = a < b ? t : n - t;
        return nv + e * (n - 1) + (tt - 1);
    };

    auto node_id = [&](int f, int k, int i, int j) {
        const Face& poly = T.F[f];
        int m = (int)poly.size();
        if (i == 0 && j == 0) return poly[k];
        if (j == 0) return edge_node(f, k, i);
        if (i == 0) return edge_node(f, (k + m - 1) % m, n - j);
        int base = face_base[f];
        if (!odd) {
            int inner = m * (q - 1) * (q - 1);
            if (i == q && j == q) return base + inner + m * (q - 1);
            if (i == q) return base + inner + k * (q - 1) + (j - 1);
            if (j == q) return base + inner + ((k + m - 1) % m) * (q - 1) + (i - 1);
            return base + k * (q - 1) * (q - 1) + (i - 1) * (q - 1) + (j - 1);
        }
        return base + k * q * q + (i - 1) * q + (j - 1);
    };

    // The evaluator of one kite: its control net when it is regular, else a patch tree.
    struct KiteEval {
        bool made = false;
        std::optional<detail::BicubicNet> P;
        std::unique_ptr<detail::PatchTree> tree;
    };

    std::vector<Face> out_faces;
    std::vector<Color> out_colors;
    for (int f = 0; f < nf; ++f) {
        const Face& poly = T.F[f];
        int m = (int)poly.size();
        const detail::PolygonDomain& dom = detail::PolygonDomain::get(m);
        std::vector<double> gamma(m, 1.0);
        double gamma_centre = 1.0;
        if (uniform) {
            for (int k = 0; k < m; ++k) {
                int v = poly[k];
                double g = T.boundary[v] ? 1.0 : detail::cc_gamma((int)T.VE[v].size());
                gamma[k] = 1 + (g - 1) * scale;
            }
            if (m != 4 && centre) gamma_centre = 1 + (detail::cc_gamma(m) - 1) * scale;
        }
        detail::FaceReparam psi = detail::face_reparam(dom, gamma, gamma_centre, p);
        std::vector<KiteEval> evaluators(m);

        auto evaluate = [&](int k, double u, double v) -> Point {
            KiteEval& ev = evaluators[k];
            if (!ev.made) {
                ev.P = detail::regular_stencil(T1, kite_offset[f] + k);
                if (!ev.P) ev.tree.reset(new detail::PatchTree(T1, kite_offset[f] + k));
                ev.made = true;
            }
            if (ev.P) return detail::eval_bicubic(*ev.P, u, v);
            return ev.tree->eval(u, v);
        };

        for (int k = 0; k < m; ++k)
            for (int i = 0; i < q + 1; ++i)
                for (int j = 0; j < q + 1; ++j) {
                    int nid = node_id(f, k, i, j);
                    if (done[nid]) continue;
                    double u0 = 2.0 * i / n, v0 = 2.0 * j / n;
                    int kk = k;
                    double u = u0, v = v0;
                    if (!psi.trivial) {
                        Point2 y = psi.apply(dom.kite_map(k, u0, v0));
                        kk = dom.kite_of(y);
                        Point2 uv = dom.kite_inverse(kk, y);
                        u = uv[0];
                        v = uv[1];
                    }
                    if (u > 1 - 1e-12 && v > 1 - 1e-12) GV[nid] = L[nv + ne + f];     // the face point
                    else GV[nid] = evaluate(kk, u, v);
                    done[nid] = true;
                }
        const Color& color = colors.at(f);
        for (int k = 0; k < m; ++k)
            for (int i = 0; i < q; ++i)
                for (int j = 0; j < q; ++j) {
                    out_faces.push_back({node_id(f, k, i, j), node_id(f, k, i + 1, j), node_id(f, k, i + 1, j + 1),
                                         node_id(f, k, i, j + 1)});
                    out_colors.push_back(color);
                }
        if (odd) {
            for (int k = 0; k < m; ++k) {
                int k1 = (k + 1) % m;
                for (int j = 0; j < q; ++j) {
                    out_faces.push_back({node_id(f, k, q, j), node_id(f, k1, j, q), node_id(f, k1, j + 1, q),
                                         node_id(f, k, q, j + 1)});
                    out_colors.push_back(color);
                }
            }
            Face centre_face;
            for (int k = 0; k < m; ++k) centre_face.push_back(node_id(f, k, q, q));
            out_faces.push_back(centre_face);
            out_colors.push_back(color);
        }
    }
    return Mesh(GV, out_faces, out_colors);
}

inline Mesh subdivide(const Mesh& M, int steps, bool repair) { return catmull_clark(M, steps, repair); }

}  // namespace add

namespace add {

namespace detail {

//: (face, uv) for every face, a face pinched at a vertex split into loops.
struct SafeFace { Face face; Color color; std::vector<Point2> uv; };
inline std::vector<SafeFace> safe_faces(const Mesh& M) {
    std::vector<SafeFace> out;
    for (size_t k = 0; k < M.F.size(); ++k) {
        const Face& face = M.F[k];
        const Color& c = M.C[k];
        const std::vector<Point2>* uv = M.has_uv && !M.UV[k].empty() ? &M.UV[k] : nullptr;
        std::set<int> distinct(face.begin(), face.end());
        if (distinct.size() == face.size()) {
            out.push_back({face, c, uv ? *uv : std::vector<Point2>()});
            continue;
        }
        for (auto& piece : split_repeats(face, uv)) {
            std::set<int> d2(piece.first.begin(), piece.first.end());
            if (piece.first.size() >= 3 && d2.size() >= 3) out.push_back({piece.first, c, piece.second});
        }
    }
    return out;
}

inline Mesh writable(const Mesh& M) {
    std::set<int> bad = not_finite(M);
    bool repeats = false;
    for (const Face& f : M.F) {
        std::set<int> distinct(f.begin(), f.end());
        if (distinct.size() != f.size()) { repeats = true; break; }
    }
    if (bad.empty() && !repeats) return M;
    Mesh out;
    out.V = M.V;
    out.has_uv = M.has_uv;
    for (SafeFace& s : safe_faces(M)) {
        out.F.push_back(s.face);
        out.C.push_back(s.color);
        if (out.has_uv) out.UV.push_back(s.uv);
    }
    if (!bad.empty()) drop_not_finite(out);                    // its faces go, and it is not written either
    return out;
}

//: Is corner b of a 2D outline no corner at all -- on a straight side?
inline bool off_straight(const Point2& a, const Point2& b, const Point2& c) {
    double dx = c[0] - a[0], dy = c[1] - a[1];
    double cr = dx * (b[1] - a[1]) - dy * (b[0] - a[0]);
    return std::fabs(cr) <= 1e-5 * std::sqrt(dx * dx + dy * dy);
}

//: Twice the signed area of the triangle a b c (positive when it turns left at b).
inline double off_turn(const Point2& a, const Point2& b, const Point2& c) {
    return (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0]);
}

inline bool off_convex(const Profile& pts, const std::vector<int>& ring_) {
    int k = (int)ring_.size();
    for (int i = 0; i < k; ++i) {
        const Point2& a = pts[ring_[(i + k - 1) % k]];
        const Point2& b = pts[ring_[i]];
        const Point2& c = pts[ring_[(i + 1) % k]];
        if (off_turn(a, b, c) <= 0 || off_straight(a, b, c)) return false;
    }
    return true;
}

inline std::vector<Face> off_pieces(const Mesh& M, const Face& f) {
    int k = (int)f.size();
    if (k <= 4) return {f};
    Frame fr = frame(face_normal(M, f));
    Profile pts;
    for (int i : f) pts.push_back({dot(M.V[i], fr.u), dot(M.V[i], fr.v)});
    bool flip = poly_area2(pts) < 0;
    if (flip) std::reverse(pts.begin(), pts.end());            // work counter-clockwise
    std::vector<int> ring_(k);
    std::iota(ring_.begin(), ring_.end(), 0);
    std::vector<std::vector<int>> pieces;
    if (off_convex(pts, ring_)) {
        for (int i = 1; i < k - 2; i += 2) pieces.push_back({0, i, i + 1, i + 2});
        if (k % 2) pieces.push_back({0, k - 2, k - 1});
    } else {
        std::vector<std::array<int, 3>> tris;
        while (ring_.size() > 3) {
            int n = (int)ring_.size();
            bool cut_one = false;
            for (int j = 0; j < n; ++j) {
                int i0 = ring_[(j + n - 1) % n], i1 = ring_[j], i2 = ring_[(j + 1) % n];
                const Point2 &a = pts[i0], &b = pts[i1], &c = pts[i2];
                if (off_turn(a, b, c) <= 0 || off_straight(a, b, c)) continue;    // a reflex or straight corner
                bool inside_ = false;                                               // another corner inside?
                for (int q : ring_) {
                    if (q == i0 || q == i1 || q == i2) continue;
                    if (off_turn(a, b, pts[q]) >= 0 && off_turn(b, c, pts[q]) >= 0 && off_turn(c, a, pts[q]) >= 0) {
                        inside_ = true;
                        break;
                    }
                }
                if (inside_) continue;
                tris.push_back({i0, i1, i2});
                ring_.erase(ring_.begin() + j);
                cut_one = true;
                break;
            }
            if (!cut_one) {                                    // no ear (an outline that crosses itself):
                for (size_t j = 1; j + 1 < ring_.size(); ++j)   // the rest as a fan, as a viewer would draw it
                    tris.push_back({ring_[0], ring_[j], ring_[j + 1]});
                ring_.clear();
                break;
            }
        }
        if (!ring_.empty()) tris.push_back({ring_[0], ring_[1], ring_[2]});
        std::map<std::pair<int, int>, int> edge;
        for (size_t t = 0; t < tris.size(); ++t)
            for (int j = 0; j < 3; ++j) edge[{tris[t][j], tris[t][(j + 1) % 3]}] = (int)t;
        std::vector<char> used(tris.size(), 0);
        for (size_t t = 0; t < tris.size(); ++t) {
            if (used[t]) continue;
            used[t] = 1;
            const auto& tri = tris[t];
            std::vector<int> piece(tri.begin(), tri.end());
            for (int j = 0; j < 3; ++j) {                       // a neighbour across one side, together convex?
                int p = tri[j], q = tri[(j + 1) % 3], r = tri[(j + 2) % 3];
                auto it = edge.find({q, p});
                if (it == edge.end() || used[it->second]) continue;
                int s2 = it->second;
                int d = -1;
                for (int x : tris[s2])
                    if (x != p && x != q) { d = x; break; }
                std::vector<int> quad_{q, r, p, d};
                if (off_convex(pts, quad_)) {
                    used[s2] = 1;
                    piece = quad_;
                    break;
                }
            }
            pieces.push_back(piece);
        }
    }
    std::vector<Face> out;
    for (const std::vector<int>& piece : pieces) {
        Face face;
        for (int i : piece) face.push_back(flip ? f[k - 1 - i] : f[i]);
        if (flip) std::reverse(face.begin(), face.end());
        out.push_back(face);
    }
    return out;
}

//: The corners of a face as an .off / .ply / .obj line lists them: " ".join(str(i + shift)).
inline std::string corner_list(const Face& face, long long shift) {
    std::string s;
    for (size_t j = 0; j < face.size(); ++j) {
        if (j) s += " ";
        s += std::to_string(face[j] + shift);
    }
    return s;
}

inline std::vector<std::string> off_face_lines(const Mesh& M, long long base) {
    std::vector<std::string> lines;
    for (size_t q = 0; q < M.F.size(); ++q) {
        const Color& c = M.C[q];
        std::string tail = c.alpha < 1.0
                               ? fmt(" %d %d %d %d\n", c.r, c.g, c.b, (int)std::nearbyint(c.alpha * 255))
                               : fmt(" %d %d %d\n", c.r, c.g, c.b);
        for (const Face& piece : off_pieces(M, M.F[q]))            // "%d %s%s" (a face without
            lines.push_back(std::to_string(piece.size()) + " " + corner_list(piece, base) + tail);   // corners: "0  r g b")
    }
    return lines;
}

inline std::ofstream open_out(const std::string& path) {
    std::ofstream f(path, std::ios::out | std::ios::binary | std::ios::trunc);
    if (!f) throw std::runtime_error("cannot write " + path);
    return f;
}

inline void write_off(const std::string& path, const Mesh& M0) {
    Mesh M = writable(M0);
    std::vector<std::string> faces = off_face_lines(M);
    std::ofstream f = open_out(path);
    std::string out = "OFF\n" + std::to_string(M.V.size()) + " " + std::to_string(faces.size()) + " 0\n";
    for (const Point& p : M.V) out += num(p[0]) + " " + num(p[1]) + " " + num(p[2]) + "\n";
    f << out;
    for (const std::string& line : faces) f << line;
}

inline std::string file_stem(const std::string& image) {
    std::string s = image;
    std::replace(s.begin(), s.end(), '\\', '/');
    size_t slash = s.rfind('/');
    if (slash != std::string::npos) s = s.substr(slash + 1);
    return s;
}

inline std::string material_name(const Color& c) {
    std::string name = fmt("color_%02x%02x%02x", c.r, c.g, c.b);
    if (c.alpha < 1.0) name += fmt("_a%03d", (int)std::nearbyint(c.alpha * 1000));
    if (!c.image.empty()) {
        std::string stem = file_stem(c.image);
        size_t dot_ = stem.rfind('.');
        if (dot_ != std::string::npos) stem = stem.substr(0, dot_);
        name += "_t";
        for (char ch : stem)                                   // (non-ASCII letters are kept, as Python's
            name += ((unsigned char)ch >= 0x80 || std::isalnum((unsigned char)ch)) ? ch : '_';   // isalnum does)
    }
    return name;
}

//: A texture coordinate as an .obj file keys it: (round(u, 6), round(v, 6)).
inline std::pair<double, double> uv_key(const Point2& t) { return {py_round(t[0], 6), py_round(t[1], 6)}; }
//: Is ``key`` already in ``index``?  (A NaN never is: Python's dict does not find it again,
//: and _num then raises.)
template <class Index>
inline bool known_uv(const Index& index, const std::pair<double, double>& key) {
    return !std::isnan(key.first) && !std::isnan(key.second) && index.count(key) > 0;
}

//: An "f" line of an .obj file: the corners (numbered from ``shift``) and, for a textured
//: face, "corner/texture" pairs -- as many as both lists have (Python's zip).
template <class Index>
inline std::string obj_face_line(const Face& face, const std::vector<Point2>* uv, long long shift, Index& vt_index) {
    if (!uv) return "f " + corner_list(face, shift) + "\n";
    std::string s = "f ";
    for (size_t j = 0; j < face.size() && j < uv->size(); ++j) {
        if (j) s += " ";
        s += std::to_string(face[j] + shift) + "/" + std::to_string(vt_index[uv_key((*uv)[j])]);
    }
    return s + "\n";
}

inline void write_obj(const std::string& path, const Mesh& M0, std::optional<std::string> mtl_path) {
    Mesh M = writable(M0);
    std::string mtl;
    if (mtl_path) mtl = *mtl_path;
    else if (path.size() >= 4 && lower(path.substr(path.size() - 4)) == ".obj") mtl = path.substr(0, path.size() - 4) + ".mtl";
    else mtl = path + ".mtl";
    std::string mtl_name = file_stem(mtl);

    std::vector<Color> palette_;
    std::unordered_map<Color, std::string, ColorHash> seen;
    for (const Color& c : M.C)
        if (!seen.count(c)) {
            seen[c] = material_name(c);
            palette_.push_back(c);
        }
    std::ofstream f = open_out(path);
    std::string out = "# written by add.py " + version + "\n" + "mtllib " + mtl_name + "\n" + "o model\n";
    for (const Point& p : M.V) out += "v " + num(p[0]) + " " + num(p[1]) + " " + num(p[2]) + "\n";
    f << out;
    // Texture coordinates, one line per distinct (u, v) of textured faces.
    std::map<std::pair<double, double>, int> vt_index;
    if (M.has_uv) {
        out.clear();
        for (size_t k = 0; k < M.C.size(); ++k) {
            const std::vector<Point2>& uv = M.UV[k];
            if (uv.empty() || M.C[k].image.empty()) continue;
            for (const Point2& t : uv) {
                std::pair<double, double> key = uv_key(t);
                if (!known_uv(vt_index, key)) {
                    vt_index[key] = (int)vt_index.size() + 1;
                    std::string u = num(key.first);            // (u first: Python's order)
                    std::string v = num(key.second);
                    out += "vt " + u + " " + v + "\n";
                }
            }
        }
        f << out;
    }
    // Group faces by colour: one ``usemtl`` line per colour, not per face.
    std::unordered_map<Color, std::vector<size_t>, ColorHash> by_color;
    for (size_t k = 0; k < M.F.size(); ++k) by_color[M.C[k]].push_back(k);
    for (const Color& c : palette_) {
        f << "usemtl " << seen[c] << "\n";
        out.clear();
        bool textured = !c.image.empty() && M.has_uv;
        for (size_t k : by_color[c])
            out += obj_face_line(M.F[k], textured && !M.UV[k].empty() ? &M.UV[k] : nullptr, 1, vt_index);
        f << out;
    }
    f.close();

    std::ofstream m = open_out(mtl);
    m << "# written by add.py " << version << "\n";
    for (const Color& c : palette_) {
        m << "newmtl " << seen[c] << "\n";
        m << fmt("Kd %.6f %.6f %.6f\n", c.r / 255.0, c.g / 255.0, c.b / 255.0);
        m << "Ka 0.100000 0.100000 0.100000\n";
        m << "Ks 0.000000 0.000000 0.000000\n";
        m << fmt("d %.3f\n", c.alpha);
        m << "illum 1\n";
        if (!c.image.empty()) m << "map_Kd " << file_stem(c.image) << "\n";
        m << "\n";
    }
}

inline void write_ply(const std::string& path, const Mesh& M0) {
    Mesh M = writable(M0);
    std::ofstream f = open_out(path);
    std::string out = "ply\nformat ascii 1.0\ncomment add.py " + version + "\n";
    out += "element vertex " + std::to_string(M.V.size()) + "\n";
    out += "property float x\nproperty float y\nproperty float z\n";
    out += "element face " + std::to_string(M.F.size()) + "\n";
    out += "property list uchar int vertex_indices\n";
    out += "property uchar red\nproperty uchar green\nproperty uchar blue\n";
    out += "end_header\n";
    for (const Point& p : M.V) out += num(p[0]) + " " + num(p[1]) + " " + num(p[2]) + "\n";
    f << out;
    out.clear();
    for (size_t k = 0; k < M.F.size(); ++k) {
        const Color& c = M.C[k];
        out += std::to_string(M.F[k].size()) + " " + corner_list(M.F[k], 0) + fmt(" %d %d %d\n", c.r, c.g, c.b);
    }
    f << out;
}

//: Python's ``"%.6e" % x`` (printf's, except that a NaN is "nan" whatever its sign).
inline std::string sci6(double x) {
    if (std::isnan(x)) return "nan";
    return fmt("%.6e", x);
}

inline void write_stl(const std::string& path, const Mesh& M0) {
    Mesh M = writable(M0);
    std::ofstream f = open_out(path);
    std::string out = "solid addpy\n";
    for (const Face& face : M.F) {
        for (size_t t = 1; t + 1 < face.size(); ++t) {
            const Point& a = M.V[face[0]];
            const Point& b = M.V[face[t]];
            const Point& c = M.V[face[t + 1]];
            Point n = unit(cross(sub(b, a), sub(c, a)));
            out += "facet normal " + sci6(n[0]) + " " + sci6(n[1]) + " " + sci6(n[2]) + "\n";
            out += "  outer loop\n";
            for (const Point* p : {&a, &b, &c})
                out += "    vertex " + sci6((*p)[0]) + " " + sci6((*p)[1]) + " " + sci6((*p)[2]) + "\n";
            out += "  endloop\nendfacet\n";
        }
        if (out.size() > (1u << 20)) {
            f << out;
            out.clear();
        }
    }
    out += "endsolid addpy\n";
    f << out;
}

inline std::string rounded(double x, int decimals) {
    if (decimals < 0) throw std::invalid_argument("unsupported format character '-' (0x2d)");   // ("%.-1f")
    std::string text = check_f(x, decimals);                   // (pattern % x).rstrip("0").rstrip(".")
    size_t end = text.size();
    while (end > 0 && text[end - 1] == '0') --end;
    while (end > 0 && text[end - 1] == '.') --end;
    text.resize(end);
    return (text.empty() || text == "-0") ? "0" : text;
}

// -- reading files as Python reads them ---------------------------------------

//: Throw Python's UnicodeDecodeError (a ValueError) unless ``s`` is well-formed UTF-8.
inline void check_utf8(const std::string& s, const std::string& path) {
    size_t i = 0, n = s.size();
    while (i < n) {
        unsigned char c = (unsigned char)s[i];
        if (c < 0x80) {
            ++i;
            continue;
        }
        size_t len = 0;
        unsigned char lo = 0x80, hi = 0xBF;                    // the range of the second byte
        if (c >= 0xC2 && c <= 0xDF) len = 2;
        else if (c == 0xE0) len = 3, lo = 0xA0;
        else if (c >= 0xE1 && c <= 0xEC) len = 3;
        else if (c == 0xED) len = 3, hi = 0x9F;               // (no surrogates)
        else if (c >= 0xEE && c <= 0xEF) len = 3;
        else if (c == 0xF0) len = 4, lo = 0x90;
        else if (c >= 0xF1 && c <= 0xF3) len = 4;
        else if (c == 0xF4) len = 4, hi = 0x8F;               // (nothing beyond U+10FFFF)
        bool ok = len > 0 && i + len <= n;
        for (size_t k = 1; ok && k < len; ++k) {
            unsigned char d = (unsigned char)s[i + k];
            ok = k == 1 ? (d >= lo && d <= hi) : (d >= 0x80 && d <= 0xBF);
        }
        if (!ok)
            throw std::invalid_argument("'utf-8' codec can't decode byte " + fmt("0x%02x", c) + " in position " +
                                        std::to_string(i) + " of " + path);
        i += len;
    }
}

inline std::string read_text(const std::string& path) {
    std::error_code ec;
    if (std::filesystem::is_directory(path, ec))              // (Python: IsADirectoryError)
        throw std::system_error(std::make_error_code(std::errc::is_a_directory), "cannot read '" + path + "'");
    errno = 0;
    std::ifstream f(path, std::ios::in | std::ios::binary);
    if (!f) throw std::system_error(errno ? errno : ENOENT, std::generic_category(), "cannot read '" + path + "'");
    std::string bytes((std::istreambuf_iterator<char>(f)), std::istreambuf_iterator<char>());
    check_utf8(bytes, path);
    std::string text;                                          // universal newlines: \r\n and \r -> \n
    text.reserve(bytes.size());
    for (size_t i = 0; i < bytes.size(); ++i) {
        if (bytes[i] != '\r') {
            text += bytes[i];
            continue;
        }
        text += '\n';
        if (i + 1 < bytes.size() && bytes[i + 1] == '\n') ++i;
    }
    return text;
}

inline std::vector<std::string> split_on(const std::string& s, char sep) {
    std::vector<std::string> out;
    size_t a = 0;
    while (true) {
        size_t b = s.find(sep, a);
        if (b == std::string::npos) {
            out.push_back(s.substr(a));
            return out;
        }
        out.push_back(s.substr(a, b - a));
        a = b + 1;
    }
}

//: How many bytes the whitespace character at s[i] takes (0: it is no whitespace).
inline size_t space_at(const std::string& s, size_t i) {
    unsigned char c = (unsigned char)s[i];
    if (c == ' ' || (c >= 0x09 && c <= 0x0D) || (c >= 0x1C && c <= 0x1F)) return 1;
    unsigned char d = i + 1 < s.size() ? (unsigned char)s[i + 1] : 0;
    unsigned char e = i + 2 < s.size() ? (unsigned char)s[i + 2] : 0;
    if (c == 0xC2 && (d == 0x85 || d == 0xA0)) return 2;                      // U+0085, U+00A0
    if (c == 0xE1 && d == 0x9A && e == 0x80) return 3;                         // U+1680
    if (c == 0xE2 && d == 0x80 && ((e >= 0x80 && e <= 0x8A) || e == 0xA8 || e == 0xA9 || e == 0xAF))
        return 3;                                                               // U+2000..200A, 2028, 2029, 202F
    if (c == 0xE2 && d == 0x81 && e == 0x9F) return 3;                         // U+205F
    if (c == 0xE3 && d == 0x80 && e == 0x80) return 3;                         // U+3000
    return 0;
}

inline std::vector<std::string> py_split(const std::string& s) {
    std::vector<std::string> out;
    size_t i = 0;
    while (i < s.size()) {
        size_t w = space_at(s, i);
        if (w) {
            i += w;
            continue;
        }
        size_t start = i;
        while (i < s.size() && !space_at(s, i)) ++i;
        out.push_back(s.substr(start, i - start));
    }
    return out;
}

inline std::string py_strip(const std::string& s) {
    size_t a = 0;
    while (a < s.size() && space_at(s, a)) a += space_at(s, a);
    size_t end = a;                                            // the end of the last character that is not a space
    for (size_t i = a; i < s.size();) {
        size_t w = space_at(s, i);
        if (w) {
            i += w;
        } else {
            ++i;
            end = i;
        }
    }
    return s.substr(a, end - a);
}

inline bool ascii_digit(char ch) { return ch >= '0' && ch <= '9'; }

inline double py_float(const std::string& word) {
    auto refuse = [&]() -> double { throw std::invalid_argument("could not convert string to float: '" + word + "'"); };
    std::string cleaned;                                       // "_" only between two digits, then dropped
    bool underscores = word.find('_') != std::string::npos;
    for (size_t i = 0; underscores && i < word.size(); ++i) {
        if (word[i] != '_') {
            cleaned += word[i];
            continue;
        }
        if (!(i > 0 && ascii_digit(word[i - 1]) && i + 1 < word.size() && ascii_digit(word[i + 1]))) return refuse();
    }
    const std::string& s = underscores ? cleaned : word;
    size_t i = 0;
    bool negative = false;
    if (i < s.size() && (s[i] == '+' || s[i] == '-')) negative = s[i++] == '-';
    if (i < s.size() && s[i] != '.' && !ascii_digit(s[i])) {  // inf, infinity, nan -- in any case (ASCII only)
        std::string name;
        for (size_t k = i; k < s.size(); ++k) name += (s[k] >= 'A' && s[k] <= 'Z') ? (char)(s[k] - 'A' + 'a') : s[k];
        if (name == "inf" || name == "infinity") return negative ? -inf : inf;
        if (name == "nan") return negative ? -std::numeric_limits<double>::quiet_NaN() : std::numeric_limits<double>::quiet_NaN();
        return refuse();
    }
    size_t j = i, digits = 0;                                  // digits [. digits] | . digits
    while (j < s.size() && ascii_digit(s[j])) ++j, ++digits;
    if (j < s.size() && s[j] == '.') {
        ++j;
        while (j < s.size() && ascii_digit(s[j])) ++j, ++digits;
    }
    if (digits == 0) return refuse();
    if (j < s.size() && (s[j] == 'e' || s[j] == 'E')) {        // [e [sign] digits]
        ++j;
        if (j < s.size() && (s[j] == '+' || s[j] == '-')) ++j;
        size_t e0 = j;
        while (j < s.size() && ascii_digit(s[j])) ++j;
        if (j == e0) return refuse();
    }
    if (j != s.size()) return refuse();
    return std::strtod(s.c_str(), nullptr);                    // (correctly rounded, as Python's)
}

inline long long py_int(const std::string& word) {
    auto refuse = [&]() -> long long { throw std::invalid_argument("invalid literal for int() with base 10: '" + word + "'"); };
    size_t i = 0;
    bool negative = false;
    if (i < word.size() && (word[i] == '+' || word[i] == '-')) negative = word[i++] == '-';
    if (i >= word.size()) return refuse();
    const unsigned long long limit = negative ? 9223372036854775808ull : 9223372036854775807ull;
    unsigned long long v = 0;
    for (size_t j = i; j < word.size(); ++j) {
        char ch = word[j];
        if (ch == '_') {                                       // one "_" between two digits
            if (!(j > i && ascii_digit(word[j - 1]) && j + 1 < word.size() && ascii_digit(word[j + 1]))) return refuse();
            continue;
        }
        if (!ascii_digit(ch)) return refuse();
        unsigned d = (unsigned)(ch - '0');
        v = v > (limit - d) / 10 ? limit : v * 10 + d;         // (beyond 64 bits: stays at the limit)
    }
    if (negative) return v == 9223372036854775808ull ? std::numeric_limits<long long>::min() : -(long long)v;
    return (long long)v;
}

//: The code point of the UTF-8 character at s[i] (-1 for a byte that starts none); i moves on.
inline long utf8_next(const std::string& s, size_t& i) {
    unsigned char c = (unsigned char)s[i];
    size_t len = c < 0x80 ? 1 : c >= 0xF0 ? 4 : c >= 0xE0 ? 3 : c >= 0xC0 ? 2 : 0;
    if (len == 0 || i + len > s.size()) {
        ++i;
        return -1;
    }
    long cp = len == 1 ? c : (c & (0x7F >> len));
    for (size_t k = 1; k < len; ++k) {
        unsigned char d = (unsigned char)s[i + k];
        if ((d & 0xC0) != 0x80) {
            ++i;
            return -1;
        }
        cp = (cp << 6) | (d & 0x3F);
    }
    i += len;
    return cp;
}

inline std::string utf8_encode(long cp) {
    std::string s;
    if (cp < 0x80) {
        s += (char)cp;
    } else if (cp < 0x800) {
        s += (char)(0xC0 | (cp >> 6));
        s += (char)(0x80 | (cp & 0x3F));
    } else if (cp < 0x10000) {
        s += (char)(0xE0 | (cp >> 12));
        s += (char)(0x80 | ((cp >> 6) & 0x3F));
        s += (char)(0x80 | (cp & 0x3F));
    } else {
        s += (char)(0xF0 | (cp >> 18));
        s += (char)(0x80 | ((cp >> 12) & 0x3F));
        s += (char)(0x80 | ((cp >> 6) & 0x3F));
        s += (char)(0x80 | (cp & 0x3F));
    }
    return s;
}

inline std::vector<std::string> utf8_chars(const std::string& s) {
    std::vector<std::string> out;
    for (size_t i = 0; i < s.size();) {
        size_t start = i;
        utf8_next(s, i);
        out.push_back(s.substr(start, i - start));
    }
    return out;
}

inline std::string py_upper(const std::string& s) {
    // Runs of small letters: the first, the last, every how many, and how far on the capital is
    // (Python's str.upper() of U+0000..U+017F, U+0370..U+03FF and U+0400..U+052F).
    static const long runs[][4] = {
        {0x61, 0x7A, 1, -32},    {0xB5, 0xB5, 1, 743},    {0xE0, 0xF6, 1, -32},    {0xF8, 0xFE, 1, -32},
        {0xFF, 0xFF, 1, 121},    {0x101, 0x12F, 2, -1},   {0x131, 0x131, 1, -232}, {0x133, 0x137, 2, -1},
        {0x13A, 0x148, 2, -1},   {0x14B, 0x177, 2, -1},   {0x17A, 0x17E, 2, -1},   {0x17F, 0x17F, 1, -300},
        {0x371, 0x373, 2, -1},   {0x377, 0x377, 1, -1},   {0x37B, 0x37D, 1, 130},  {0x3AC, 0x3AC, 1, -38},
        {0x3AD, 0x3AF, 1, -37},  {0x3B1, 0x3C1, 1, -32},  {0x3C2, 0x3C2, 1, -31},  {0x3C3, 0x3CB, 1, -32},
        {0x3CC, 0x3CC, 1, -64},  {0x3CD, 0x3CE, 1, -63},  {0x3D0, 0x3D0, 1, -62},  {0x3D1, 0x3D1, 1, -57},
        {0x3D5, 0x3D5, 1, -47},  {0x3D6, 0x3D6, 1, -54},  {0x3D7, 0x3D7, 1, -8},   {0x3D9, 0x3EF, 2, -1},
        {0x3F0, 0x3F0, 1, -86},  {0x3F1, 0x3F1, 1, -80},  {0x3F2, 0x3F2, 1, 7},    {0x3F3, 0x3F3, 1, -116},
        {0x3F5, 0x3F5, 1, -96},  {0x3F8, 0x3F8, 1, -1},   {0x3FB, 0x3FB, 1, -1},   {0x430, 0x44F, 1, -32},
        {0x450, 0x45F, 1, -80},  {0x461, 0x481, 2, -1},   {0x48B, 0x4BF, 2, -1},   {0x4C2, 0x4CE, 2, -1},
        {0x4CF, 0x4CF, 1, -15},  {0x4D1, 0x52F, 2, -1}};
    std::string out;
    for (size_t i = 0; i < s.size();) {
        size_t start = i;
        long cp = utf8_next(s, i);
        if (cp == 0xDF) out += "SS";                                   // sharp s
        else if (cp == 0x149) out += utf8_encode(0x2BC) + "N";         // n with apostrophe
        else if (cp == 0x390) out += utf8_encode(0x399) + utf8_encode(0x308) + utf8_encode(0x301);   // iota with dialytika and tonos
        else if (cp == 0x3B0) out += utf8_encode(0x3A5) + utf8_encode(0x308) + utf8_encode(0x301);   // upsilon with dialytika and tonos
        else {
            bool changed = false;
            for (const auto& r : runs)
                if (cp >= r[0] && cp <= r[1] && (cp - r[0]) % r[2] == 0) {
                    out += utf8_encode(cp + r[3]);
                    changed = true;
                    break;
                }
            if (!changed) out += s.substr(start, i - start);
        }
    }
    return out;
}

inline Color rgb_list(const std::vector<double>& color) {
    double r = color.at(0), g = color.at(1), b = color.at(2);
    double top = r;                                            // Python's max(r, g, b)
    if (g > top) top = g;
    if (b > top) top = b;
    if (top <= 1.0) {
        r = r * 255.0;
        g = g * 255.0;
        b = b * 255.0;
    }
    const double parts[3] = {r, g, b};
    int out[3];
    for (int i = 0; i < 3; ++i) {                              // int(round(c)), limited to 0..255
        double c = parts[i];
        if (std::isnan(c)) throw std::invalid_argument("cannot convert float NaN to integer");
        if (std::isinf(c)) throw std::overflow_error("cannot convert float infinity to integer");
        double v = std::nearbyint(c);
        out[i] = v < 0 ? 0 : (v > 255 ? 255 : (int)v);
    }
    if (color.size() > 3) return Color(out[0], out[1], out[2], color[3]);
    return Color(out[0], out[1], out[2]);
}

//: Python's ``seq[start:stop]`` of a list of words (an end below 0 counts from the back).
inline std::vector<std::string> py_slice(const std::vector<std::string>& v, long long start, long long stop) {
    long long n = (long long)v.size();
    auto place_ = [n](long long i) { return i < 0 ? std::max(0LL, i + n) : std::min(i, n); };
    long long a = place_(start), b = place_(stop);
    if (b < a) b = a;
    return std::vector<std::string>(v.begin() + a, v.begin() + b);
}

//: A corner count n read from a line of ``size`` words, brought into -(size + 10) .. size + 10:
//: every slice [1:1 + n], [1 + n:], [1 + n:4 + n] of the line stays the same (and cannot overflow).
inline long long slice_count(long long n, size_t size) {
    long long m = (long long)size + 10;
    return std::max(-m, std::min(n, m));
}

//: A vertex index read from a file (add.hpp's faces hold int).
inline int index_of(long long i) {
    if (i < std::numeric_limits<int>::min() || i > std::numeric_limits<int>::max())
        throw std::out_of_range("vertex index out of range: " + std::to_string(i));
    return (int)i;
}

inline std::vector<std::string> clean_lines(const std::string& path) {
    std::vector<std::string> out;
    for (const std::string& line : split_on(read_text(path), '\n')) {
        std::string s = py_strip(line.substr(0, line.find('#')));
        if (!s.empty()) out.push_back(s);
    }
    return out;
}

inline Mesh read_off(const std::string& path, const std::optional<Color>& color) {
    std::vector<std::string> lines = clean_lines(path);
    if (lines.empty()) return Mesh();
    size_t row = 0;
    std::vector<std::string> head = py_split(lines[0]);
    std::vector<std::string> counts;
    std::string first = py_upper(head[0]);
    if (first.size() >= 3 && first.compare(first.size() - 3, 3, "OFF") == 0) {
        row = 1;
        if (head.size() >= 3) {                                // counts on the same line as OFF
            counts.assign(head.begin() + 1, head.end());
        } else {
            counts = py_split(lines.at(1));
            row = 2;
        }
    } else {
        counts = head;
        row = 1;
    }
    long long nv = py_int(counts.at(0));
    long long nf = py_int(counts.at(1));

    Mesh M;
    for (long long q = 0; q < nv; ++q) {
        std::vector<std::string> p = py_split(lines.at(row));
        row += 1;
        double x = py_float(p.at(0));
        double y = py_float(p.at(1));
        double z = py_float(p.at(2));
        M.add_vertex({x, y, z});
    }

    Color fallback = color ? *color : DEFAULT_COLOR;           // (add.py: ``default``)
    for (long long q = 0; q < nf; ++q) {
        std::vector<std::string> p = py_split(lines.at(row));
        row += 1;
        long long n = slice_count(py_int(p.at(0)), p.size());
        Face face;
        for (const std::string& x : py_slice(p, 1, 1 + n)) face.push_back(index_of(py_int(x)));
        std::vector<std::string> rest = py_slice(p, 1 + n, (long long)p.size());
        Color c = fallback;
        if (rest.size() >= 3 && !color) {
            std::vector<double> vals;
            for (size_t j = 0; j < rest.size() && j < 4; ++j) vals.push_back(py_float(rest[j]));
            double top = vals[0];                              // max(vals)
            for (double v : vals)
                if (v > top) top = v;
            bool fraction = false;                             // any(v != int(v) for v in vals)
            if (top <= 1.0)
                for (double v : vals) {
                    if (std::isnan(v)) throw std::invalid_argument("cannot convert float NaN to integer");
                    if (std::isinf(v)) throw std::overflow_error("cannot convert float infinity to integer");
                    if (v != std::trunc(v)) {
                        fraction = true;
                        break;
                    }
                }
            if (top <= 1.0 && fraction)
                for (double& v : vals) v = v * 255.0;
            if (vals.size() == 4) vals[3] = vals[3] / 255.0;   // r g b a: alpha as 0..255
            c = rgb_list(vals);
        }
        M.add_face(face, c);
    }
    return M;
}

inline Mesh read_obj(const std::string& path, const std::optional<Color>& color) {
    Mesh M;
    std::map<std::string, Color> materials;
    Color current = color ? *color : DEFAULT_COLOR;
    std::string folder = path;
    std::replace(folder.begin(), folder.end(), '\\', '/');
    size_t slash = folder.rfind('/');
    folder = slash != std::string::npos ? folder.substr(0, slash) + "/" : "";
    std::vector<Point2> vt;
    for (const std::string& line : split_on(read_text(path), '\n')) {
        std::vector<std::string> parts = py_split(line);
        if (parts.empty() || parts[0][0] == '#') continue;
        const std::string& tag = parts[0];
        if (tag == "v") {
            double x = py_float(parts.at(1));
            double y = py_float(parts.at(2));
            double z = py_float(parts.at(3));
            M.add_vertex({x, y, z});
        } else if (tag == "vt") {
            double u = py_float(parts.at(1));
            double v = parts.size() > 2 ? py_float(parts[2]) : 0.0;
            vt.push_back({u, v});
        } else if (tag == "f") {
            Face face;
            std::vector<Point2> uv;
            for (size_t k = 1; k < parts.size(); ++k) {
                std::vector<std::string> bits = split_on(parts[k], '/');
                long long idx = py_int(bits[0]);
                face.push_back(index_of(idx > 0 ? idx - 1 : (long long)M.V.size() + idx));
                if (bits.size() > 1 && !bits[1].empty()) {
                    long long t = py_int(bits[1]);
                    uv.push_back(vt[seq_index(t > 0 ? t - 1 : (long long)vt.size() + t, vt.size())]);
                }
            }
            bool textured = !current.image.empty() && uv.size() == face.size();
            if (textured) M.add_face(face, current, uv);
            else M.add_face(face, current);
        } else if (tag == "mtllib" && !color) {
            std::string name = folder + parts.at(1);
            std::map<std::string, Color> found;
            try {
                found = read_mtl(name);
            } catch (const std::system_error&) {               // (add.py: except IOError: pass)
            }
            for (auto& item : found) materials[item.first] = item.second;
        } else if (tag == "usemtl" && !color) {
            auto it = materials.find(parts.at(1));
            current = it != materials.end() ? it->second : DEFAULT_COLOR;
        }
    }
    return M;
}

inline std::map<std::string, Color> read_mtl(const std::string& path) {
    std::map<std::string, Color> out;
    std::optional<std::string> name;
    for (const std::string& line : split_on(read_text(path), '\n')) {
        std::vector<std::string> parts = py_split(line);
        if (parts.empty()) continue;
        if (parts[0] == "newmtl") {
            name = parts.at(1);
            out[*name] = DEFAULT_COLOR;
        } else if (!name) {
            continue;
        } else if (parts[0] == "Kd") {
            Color c = out[*name];
            double r = py_float(parts.at(1)) * 255;
            double g = py_float(parts.at(2)) * 255;
            double b = py_float(parts.at(3)) * 255;
            Color k = rgb_list({r, g, b});                     // + list(c[3:]): the opacity and texture stay
            k.alpha = c.alpha;
            k.image = c.image;
            out[*name] = k;
        } else if ((parts[0] == "d" || parts[0] == "Tr") && parts.size() > 1) {
            double alpha = py_float(parts[1]);
            if (parts[0] == "Tr") alpha = 1.0 - alpha;
            Color c = out[*name];
            Color k(c.r, c.g, c.b, alpha);
            k.image = c.image;
            out[*name] = k;
        } else if (parts[0] == "map_Kd" && parts.size() > 1) {
            Color k = out[*name];
            k.image = parts.back();
            out[*name] = k;
        }
    }
    return out;
}

inline Mesh read_ply(const std::string& path, const std::optional<Color>& color) {
    std::vector<std::string> text = split_on(read_text(path), '\n');
    long long nv = 0, nf = 0;
    size_t head = 0;
    std::vector<std::string> props;
    std::optional<std::string> element;
    for (size_t i = 0; i < text.size(); ++i) {
        std::vector<std::string> parts = py_split(text[i]);
        if (parts.empty()) continue;
        if (parts[0] == "element") {
            element = parts.at(1);
            if (*element == "vertex") nv = py_int(parts.at(2));
            else if (*element == "face") nf = py_int(parts.at(2));
        } else if (parts[0] == "property" && element && *element == "vertex") {
            props.push_back(parts.back());
        } else if (parts[0] == "end_header") {
            head = i + 1;
            break;
        }
    }
    Mesh M;
    size_t row = head;
    for (long long q = 0; q < nv; ++q) {
        std::vector<std::string> vals = py_split(text.at(row));
        row += 1;
        std::map<std::string, std::string> d;                  // dict(zip(props, vals))
        for (size_t j = 0; j < props.size() && j < vals.size(); ++j) d[props[j]] = vals[j];
        auto get = [&d](const char* key) {
            auto it = d.find(key);
            return it == d.end() ? 0.0 : py_float(it->second);
        };
        double x = get("x");
        double y = get("y");
        double z = get("z");
        M.add_vertex({x, y, z});
    }
    Color fallback = color ? *color : DEFAULT_COLOR;
    for (long long q = 0; q < nf; ++q) {
        std::vector<std::string> vals = py_split(text.at(row));
        row += 1;
        long long n = slice_count(py_int(vals.at(0)), vals.size());
        Face face;
        for (const std::string& v : py_slice(vals, 1, 1 + n)) face.push_back(index_of(py_int(v)));
        Color c = fallback;
        if ((long long)vals.size() >= 1 + n + 3 && !color) {
            std::vector<double> rgb3;
            for (const std::string& v : py_slice(vals, 1 + n, 4 + n)) rgb3.push_back(py_float(v));
            c = rgb_list(rgb3);
        }
        M.add_face(face, c);
    }
    return M;
}

//: The CRC-32 of a PNG chunk (zlib's crc32).
inline uint32_t crc32(const std::string& data) {
    static const std::array<uint32_t, 256> table = [] {
        std::array<uint32_t, 256> t{};
        for (uint32_t n = 0; n < 256; ++n) {
            uint32_t c = n;
            for (int k = 0; k < 8; ++k) c = c & 1 ? 0xEDB88320u ^ (c >> 1) : c >> 1;
            t[n] = c;
        }
        return t;
    }();
    uint32_t c = 0xFFFFFFFFu;
    for (unsigned char b : data) c = table[(c ^ b) & 0xFF] ^ (c >> 8);
    return c ^ 0xFFFFFFFFu;
}

//: The Adler-32 checksum that ends a zlib stream.
inline uint32_t adler32(const std::string& data) {
    uint32_t a = 1, b = 0;
    for (unsigned char x : data) {
        a = (a + x) % 65521;
        b = (b + a) % 65521;
    }
    return (b << 16) | a;
}

//: A 32-bit number as 4 bytes, most significant first (``struct.pack(">I", v)``).
inline std::string be32(uint32_t v) {
    std::string s(4, '\0');
    for (int k = 0; k < 4; ++k) s[k] = (char)((v >> (24 - 8 * k)) & 0xFF);
    return s;
}

//: ``data`` as a zlib stream (RFC 1950) of stored deflate blocks (RFC 1951, BTYPE 00): what
//: zlib.compress would give without compressing -- any PNG reader takes it.
inline std::string zlib_stored(const std::string& data) {
    std::string out("\x78\x01", 2);                            // deflate, 32K window; (0x7801 % 31 == 0)
    size_t pos = 0;
    do {
        size_t len = std::min<size_t>(65535, data.size() - pos);
        bool last = pos + len == data.size();
        out += (char)(last ? 1 : 0);                           // BFINAL, BTYPE = 00 (then byte-aligned)
        out += (char)(len & 0xFF);                             // LEN, then NLEN, little-endian
        out += (char)(len >> 8);
        out += (char)(~len & 0xFF);
        out += (char)((~len >> 8) & 0xFF);
        out.append(data, pos, len);
        pos += len;
    } while (pos < data.size());
    return out + be32(adler32(data));
}

//: os.path.join(folder, name) (POSIX).
inline std::string path_join(const std::string& folder, const std::string& name) {
    if (!name.empty() && name[0] == '/') return name;
    if (folder.empty() || folder.back() == '/') return folder + name;
    return folder + "/" + name;
}

//: load_font() once the names are known.
inline std::map<std::string, Mesh> load_names(const std::string& folder, const std::vector<std::string>& names,
                                              const std::string& suffix) {
    std::map<std::string, Mesh> out;
    for (const std::string& name : names) {
        try {
            Mesh M = load(path_join(folder, name + suffix));
            out[name] = std::move(M);
        } catch (const std::system_error&) {                   // (add.py: IOError, OSError,
        } catch (const std::invalid_argument&) {               //  ValueError)
        }
    }
    return out;
}

}  // namespace detail

inline long long obj_size(const Mesh& M) {
    long long total = 50;                                      // header lines
    for (const Point& p : M.V) {
        size_t x = detail::num(p[0]).size();                   // (in Python's order: an infinity raises
        size_t y = detail::num(p[1]).size();                   //  OverflowError, a NaN ValueError)
        size_t z = detail::num(p[2]).size();
        total += 5 + (long long)(x + y + z);
    }
    std::unordered_set<Color, ColorHash> seen;
    std::set<std::pair<double, double>> vts;
    for (size_t k = 0; k < M.F.size(); ++k) {
        const Face& face = M.F[k];
        const Color& c = M.C[k];
        total += 2 + (long long)face.size();
        bool textured = !c.image.empty() && M.has_uv && !M.UV[k].empty();
        for (int i : face) total += (long long)std::to_string(i + 1).size();
        if (textured) {
            for (const Point2& t : M.UV[k]) {
                std::pair<double, double> key = detail::uv_key(t);
                if (!detail::known_uv(vts, key)) {
                    vts.insert(key);
                    size_t u = detail::num(key.first).size();          // (u first: Python's order)
                    size_t v = detail::num(key.second).size();
                    total += 6 + (long long)(u + v);
                }
                total += 1 + (long long)std::to_string(vts.size()).size();   // "/vt" per corner
            }
        }
        if (!seen.count(c)) {
            seen.insert(c);
            bool longer = c.alpha < 1.0 || !c.image.empty();          // (add.py: len(c) > 3)
            total += 20 + (longer ? 8 : 0) + (!c.image.empty() ? 10 + (long long)detail::utf8_len(c.image) : 0);
        }
    }
    return total;
}
inline long long obj_size() { return obj_size(scene()); }

inline std::string save(const std::string& path, const Mesh& M, std::optional<bool> clear_scene,
                        std::optional<int> colors, bool clean_) {
    bool clear_after = clear_scene ? *clear_scene : detail::is_scene(M);
    Mesh to_save = clean_ ? clean(M, 1e-6) : M;
    if (colors) to_save = limit_colors(to_save, *colors);
    std::string ext = "off";
    size_t dot_ = path.rfind('.');
    if (dot_ != std::string::npos) ext = detail::lower(path.substr(dot_ + 1));
    if (ext == "obj") detail::write_obj(path, to_save);
    else if (ext == "ply") detail::write_ply(path, to_save);
    else if (ext == "stl") detail::write_stl(path, to_save);
    else detail::write_off(path, to_save);
    if (clear_after) clear();
    return path;
}
inline std::string save(const std::string& path) { return save(path, scene(), true); }

inline std::string off(const std::string& path, const Mesh& M) {
    bool clear_after = detail::is_scene(M);
    detail::write_off(path, M);
    if (clear_after) clear();
    return path;
}
inline std::string off(const std::string& path) { return off(path, scene()); }

inline std::string obj(const std::string& path, const Mesh& M, std::optional<std::string> mtl) {
    bool clear_after = detail::is_scene(M);
    detail::write_obj(path, M, mtl);
    if (clear_after) clear();
    return path;
}
inline std::string obj(const std::string& path) { return obj(path, scene()); }

// -- Stream -------------------------------------------------------------------

inline Stream::Stream(const std::string& path_, bool clean, std::optional<int> precision_)
    : path(path_), clean_parts(clean), precision(precision_) {
    std::string low = detail::lower(path);
    kind_ = low.size() >= 4 && low.compare(low.size() - 4, 4, ".obj") == 0 ? "obj" : "off";
    vt_ = 0;
    file_ = detail::open_out(path);
    if (kind_ == "obj") {
        mtl_ = path.substr(0, path.size() - 4) + ".mtl";
        file_ << "# written by add.py " << version << "\n";
        file_ << "mtllib " << detail::file_stem(mtl_) << "\n";
        file_ << "o model\n";
    } else {
        // OFF wants the counts first and every vertex before every face: the vertices and the
        // faces wait in two files of their own and the OFF file is put together on close, with
        // an exact header.
        file_.close();
        vertices_path_ = path + ".vertices~";
        file_ = detail::open_out(vertices_path_);
        faces_path_ = path + ".faces~";
        faces_file_ = detail::open_out(faces_path_);
    }
    has_current_ = false;
    open_ = true;
}

inline Stream::~Stream() {
    try {
        close();
    } catch (...) {                                            // (a destructor must not throw)
    }
}

inline std::string Stream::num(double x) const {
    return precision ? detail::rounded(x, *precision) : detail::num(x);
}

inline long long Stream::add(const Mesh& M0, std::optional<bool> clean) {
    bool clear_after = detail::is_scene(M0);
    if (!open_) throw std::invalid_argument("stream is closed");
    Mesh tidy;
    const Mesh* part = &M0;
    if (clean ? *clean : clean_parts) {
        CleanReport info;
        tidy = add::clean(M0, 1e-6, true, true, true, true, true, false, &info);
        removed += info.faces_removed;
        cut += info.faces_cut;
        part = &tidy;
    }
    Mesh M = detail::writable(*part);                          // tidied or not: no face visits a vertex twice
    long long base = vertices;
    std::string text;
    if (kind_ == "obj") {
        for (const Point& p : M.V) {
            std::string x = num(p[0]);
            std::string y = num(p[1]);
            std::string z = num(p[2]);
            text += "v " + x + " " + y + " " + z + "\n";
        }
        std::map<std::pair<double, double>, long long> vt_index;
        if (M.has_uv) {
            for (size_t k = 0; k < M.C.size(); ++k) {
                const std::vector<Point2>& uv = M.UV[k];
                if (uv.empty() || M.C[k].image.empty()) continue;
                for (const Point2& t : uv) {
                    std::pair<double, double> key = detail::uv_key(t);
                    if (!detail::known_uv(vt_index, key)) {
                        vt_ += 1;
                        vt_index[key] = vt_;
                        std::string u = detail::num(key.first);
                        std::string v = detail::num(key.second);
                        text += "vt " + u + " " + v + "\n";
                    }
                }
            }
        }
        std::unordered_map<Color, std::vector<size_t>, ColorHash> by_color;
        std::vector<Color> order;
        for (size_t k = 0; k < M.C.size(); ++k) {
            auto it = by_color.find(M.C[k]);
            if (it == by_color.end()) {
                it = by_color.emplace(M.C[k], std::vector<size_t>()).first;
                order.push_back(M.C[k]);
            }
            it->second.push_back(k);
        }
        for (const Color& c : order) {
            auto known = material_index_.find(c);
            if (known == material_index_.end()) {
                known = material_index_.emplace(c, detail::material_name(c)).first;
                materials.emplace_back(c, known->second);
            }
            const std::string& name = known->second;
            if (!has_current_ || c != current_) {
                text += "usemtl " + name + "\n";
                current_ = c;
                has_current_ = true;
            }
            bool textured = !c.image.empty() && M.has_uv;
            for (size_t k : by_color[c])
                text += detail::obj_face_line(M.F[k], textured && !M.UV[k].empty() ? &M.UV[k] : nullptr, base + 1,
                                              vt_index);
        }
    } else {
        for (const Point& p : M.V) {
            std::string x = num(p[0]);
            std::string y = num(p[1]);
            std::string z = num(p[2]);
            text += x + " " + y + " " + z + "\n";
        }
        std::vector<std::string> lines = detail::off_face_lines(M, base);   // at most four corners a face
        std::string joined;
        for (const std::string& line : lines) joined += line;
        faces_file_ << joined;
        bytes += (long long)joined.size();
        faces += (long long)lines.size() - (long long)M.F.size();   // (the pieces are what the file counts)
    }
    if (!text.empty()) {
        file_ << text;
        bytes += (long long)detail::utf8_len(text);            // (Python counts characters)
    }
    vertices += (long long)M.V.size();
    faces += (long long)M.F.size();
    if (clear_after) add::clear();
    return (long long)M.F.size();
}

inline long long Stream::add() { return add(scene()); }

inline std::string Stream::close() {
    if (!open_) return path;
    if (kind_ == "obj") {
        std::ofstream m = detail::open_out(mtl_);
        m << "# written by add.py " << version << "\n";
        for (const auto& item : materials) {
            const Color& c = item.first;
            m << "newmtl " << item.second << "\n";
            m << detail::fmt("Kd %.6f %.6f %.6f\n", c.r / 255.0, c.g / 255.0, c.b / 255.0);
            m << "Ka 0.100000 0.100000 0.100000\n";
            m << "Ks 0.000000 0.000000 0.000000\n";
            m << detail::fmt("d %.3f\n", c.alpha);
            m << "illum 1\n";
            if (!c.image.empty()) m << "map_Kd " << detail::file_stem(c.image) << "\n";
            m << "\n";
        }
    } else {
        file_.close();
        faces_file_.close();
        std::ofstream out = detail::open_out(path);
        std::string header = "OFF\n" + std::to_string(vertices) + " " + std::to_string(faces) + " 0\n";
        out << header;
        bytes += (long long)header.size();
        std::vector<char> chunk(1 << 20);
        for (const std::string& part : {vertices_path_, faces_path_}) {
            std::ifstream src(part, std::ios::in | std::ios::binary);
            while (src.read(chunk.data(), (std::streamsize)chunk.size()) || src.gcount() > 0)
                out.write(chunk.data(), src.gcount());
        }
        out.close();
        std::remove(vertices_path_.c_str());                   // the only files add.hpp removes
        std::remove(faces_path_.c_str());
        open_ = false;
        return path;
    }
    file_.close();
    open_ = false;
    return path;
}

inline std::unique_ptr<Stream> stream(const std::string& path, bool clean, std::optional<int> precision) {
    return std::make_unique<Stream>(path, clean, precision);
}

// -- loading ------------------------------------------------------------------

inline Mesh load(const std::string& path, std::optional<Color> color) {
    std::string ext = "off";
    size_t dot_ = path.rfind('.');
    if (dot_ != std::string::npos) ext = detail::lower(path.substr(dot_ + 1));
    if (ext == "obj") return detail::read_obj(path, color);
    if (ext == "ply") return detail::read_ply(path, color);
    return detail::read_off(path, color);
}

inline std::string write_png(const std::string& path, const std::vector<std::vector<Color>>& rows) {
    size_t height = rows.size();
    size_t width = height ? rows[0].size() : 0;
    std::string raw;
    for (const std::vector<Color>& row : rows) {
        raw += '\0';                                           // filter type "none"
        for (const Color& c : row) {
            raw += (char)c.r;
            raw += (char)c.g;
            raw += (char)c.b;
        }
    }
    auto chunk = [](const std::string& tag, const std::string& data) {
        return detail::be32((uint32_t)data.size()) + tag + data + detail::be32(detail::crc32(tag + data));
    };
    std::string header = detail::be32((uint32_t)width) + detail::be32((uint32_t)height) +
                         std::string("\x08\x02\x00\x00\x00", 5);   // 8 bits, RGB, deflate, no filter, no interlace
    std::ofstream f = detail::open_out(path);
    f << std::string("\x89PNG\r\n\x1a\n", 8);
    f << chunk("IHDR", header);
    f << chunk("IDAT", detail::zlib_stored(raw));              // (add.py: zlib.compress(raw, 6))
    f << chunk("IEND", "");
    return path;
}

inline std::map<std::string, Mesh> load_font(const std::string& folder, std::optional<std::string> characters,
                                             const std::string& suffix) {
    if (characters) return detail::load_names(folder, detail::utf8_chars(*characters), suffix);
    std::vector<std::string> names;
    std::error_code ec;
    std::filesystem::directory_iterator it(folder, ec), end;
    if (ec) return {};                                         // (add.py: OSError from os.listdir)
    for (; it != end; it.increment(ec)) {
        if (ec) return {};
        std::string n = it->path().filename().string();
        if (n.size() >= suffix.size() && n.compare(n.size() - suffix.size(), suffix.size(), suffix) == 0)
            names.push_back(suffix.empty() ? std::string() : n.substr(0, n.size() - suffix.size()));   // n[:-len(suffix)]
    }
    return detail::load_names(folder, names, suffix);
}

inline std::map<std::string, Mesh> load_font(const std::string& folder, const std::vector<std::string>& characters,
                                             const std::string& suffix) {
    return detail::load_names(folder, characters, suffix);
}

inline Mesh typeset(const std::string& characters, const std::map<std::string, Mesh>& font, const Point& at,
                    double size, double spacing, std::optional<Color> color, const std::array<Point, 2>& plane) {
    const Point& u = plane[0];
    Mesh out;
    double x = 0.0;
    for (const std::string& ch : detail::utf8_chars(characters)) {
        auto it = font.find(ch);                               // font.get(ch) or font.get(ch.upper())
        if (it == font.end()) it = font.find(detail::py_upper(ch));
        if (it == font.end()) {
            x += spacing;
            continue;
        }
        Mesh G = fit(it->second, size);
        G = place(G, {0, 0, 0});
        Point pos = {at[0] + u[0] * x * spacing * size, at[1] + u[1] * x * spacing * size,
                     at[2] + u[2] * x * spacing * size};
        G = move(G, pos);
        if (color) G = add::color(G, *color);
        out.extend(G);
        x += 1.0;
    }
    return out;
}

}  // namespace add

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

namespace add {

inline void newface(const Points& A, const Color& RGB) { polygon(A, RGB); }

inline void cube(const Point& c, double e, const Color& RGB) { box(c, e, RGB); }

inline void rectangle3D(const Point& c, const Point& e, const Color& RGB) { cuboid(c, e, RGB); }

inline void cube2(const Point& c, double e, double b, const Color& RGB) { frame(c, e, b, RGB); }

inline void cylinder2(const Point& A, const Point& B, double r, int k, const Color& RGB) { tube(A, B, r, k, RGB); }

inline void cylinder3(const Point& A, const Point& B, double r, int k, const Color& RGB) { cup(A, B, r, k, RGB); }

inline void cone2(const Point& A, const Point& B, double r, int k, const Color& RGB) { cone_open(A, B, r, k, RGB); }

inline void ball(const Point& center, double r, int k, const ColorOf<Point>& color, std::optional<int> subdivisions) {
    sphere(center, r, k, color, subdivisions);
}

inline void block(const Point& center, const Point& sizes, const Color& color) { cuboid(center, sizes, color); }

inline void cuboid3D(const Point& center, const Point& sizes, const Color& color) { cuboid(center, sizes, color); }

inline void lathe(const Profile& profile, const Point& A, const Point& B, double t0, double t1, int steps, int k,
                  const ColorOf<double, double>& color, double angle, bool caps) {
    revolve(profile, A, B, t0, t1, steps, k, color, angle, caps);
}

inline void solid_of_revolution(const Profile& profile, const Point& A, const Point& B, double t0, double t1,
                                int steps, int k, const ColorOf<double, double>& color, double angle, bool caps) {
    revolve(profile, A, B, t0, t1, steps, k, color, angle, caps);
}

inline void lathe(const std::function<Point2(double)>& profile, const Point& A, const Point& B, double t0, double t1,
                  int steps, int k, const ColorOf<double, double>& color, double angle, bool caps) {
    revolve(profile, A, B, t0, t1, steps, k, color, angle, caps);
}

inline void solid_of_revolution(const std::function<Point2(double)>& profile, const Point& A, const Point& B,
                                double t0, double t1, int steps, int k, const ColorOf<double, double>& color,
                                double angle, bool caps) {
    revolve(profile, A, B, t0, t1, steps, k, color, angle, caps);
}

inline Mesh weld(const Mesh& M, double tol, bool weld, bool degenerate, bool duplicates, bool internal, bool unused,
                 bool normals, CleanReport* report, bool overlaps, bool convex) {
    return clean(M, tol, weld, degenerate, duplicates, internal, unused, normals, report, overlaps, convex);
}
inline Mesh weld() { return clean(); }

inline Mesh scale(const Mesh& M, double s, std::optional<Point> about) { return zoom(M, s, about); }

inline Mesh translate(const Mesh& M, const Point& V) { return move(M, V); }

inline Mesh reflect(const Mesh& M, const Point& point, const Point& normal) { return mirror(M, point, normal); }

// -- a one-line demonstration ------------------------------------------------------------

inline std::string demo(const std::string& path) {
    clear();
    axes({0, 0, 0}, 3.0);

    // A block with a hole drilled through it, cut out with a boolean.
    cuboid({0, -1.2, 0}, {4, 0.6, 4}, "brown");
    Mesh plate = layer();
    cylinder({0, -2, 0}, {0, 0, 0}, 0.9, 32, "brown");
    Mesh drill = layer();
    mesh(difference(plate, drill));

    // A twisted, tapering star column: copy + rotate + stretch a cross-section.
    Profile star;
    for (int i = 0; i < 12; ++i) {
        double a = 2 * pi * i / 12;
        double r = i % 2 ? 0.6 : 0.28;
        star.push_back({std::cos(a) * r, std::sin(a) * r});
    }
    extrude(star, {0, 3.2, 0}, "gold", 60, pi, [](double t) { return 1.0 - 0.55 * t; }, {0, -0.9, 0});

    // A surface of revolution and a parametric surface.
    revolve(std::function<Point2(double)>([](double t) { return Point2{0.7 + 0.25 * std::sin(4 * t), t}; }),
            {2.4, -0.9, 0}, {2.4, 0.1, 0}, 0, 2.6, 60, 40, "teal");

    auto shell = [](double u, double v) {
        return Point{(1.2 + 0.45 * std::cos(u)) * std::cos(v) - 2.6,
                     0.45 * std::sin(u) + 0.6,
                     (1.2 + 0.45 * std::cos(u)) * std::sin(v)};
    };
    parametric(shell, 0, 2 * pi, 40, 0, 2 * pi, 80, "sky", true, true);

    // A rainbow of spheres on a ring.
    sphere({0, 0, 0}, 0.22, 8, "white");
    Mesh bead = layer();
    mesh(color_by(array_radial(move(bead, {2.2, 1.9, 0}), 24),
                  [](const Point& p) { return hsv(std::atan2(p[2], p[0]) / (2 * pi)); }));

    check();
    return save(path, scene(), std::nullopt, SKETCHFAB_COLORS);   // the .obj stays Sketchfab-ready
}

}  // namespace add

#endif  // ADD_HPP

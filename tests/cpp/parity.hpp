// The C++ half of the parity tests: every case builds a model (or computes some
// numbers) with add.hpp exactly as its Python twin in cases_*.py does with
// add.py, and writes it to <case>.off / <case>.txt; run_parity.py compares the
// files byte for byte.
//
//     CASE(red_box) {
//         add::box({0, 0, 0}, 1, "red");
//         save_case();                    // the scene, written exactly (add::off)
//     }
#include "add.hpp"

#include <cstdio>
#include <fstream>
#include <functional>
#include <string>
#include <vector>

namespace parity {

struct Case {
    std::string name;
    std::function<void()> fn;
};
inline std::vector<Case>& cases() { static std::vector<Case> c; return c; }
inline std::string& current() { static std::string s; return s; }
inline std::ofstream& out() { static std::ofstream f; return f; }
struct Reg {
    Reg(const char* n, std::function<void()> f) { cases().push_back({n, f}); }
};

//: Write the scene exactly as it is (add::off) to <case>.off, and clear it.
inline void save_case() { add::off(current() + ".off"); }
//: Write a mesh exactly as it is to <case>.off (or <case>_<tag>.off).
inline void save_mesh(const add::Mesh& M, const std::string& tag = "") {
    add::off(current() + (tag.empty() ? "" : "_" + tag) + ".off", M);
}
//: Save with add::save (so through clean()) to <case>.<ext> -- e.g. "off" or "obj".
inline void save_as(const std::string& ext, const add::Mesh& M) { add::save(current() + "." + ext, M); }

inline std::ofstream& txt() {
    if (!out().is_open()) out().open(current() + ".txt", std::ios::binary);
    return out();
}
// Numbers are written the way Python's repr() writes them.
inline void record(double x) { txt() << add::detail::py_repr(x) << "\n"; }
inline void record(int x) { txt() << x << "\n"; }
inline void record(long long x) { txt() << x << "\n"; }
inline void record(size_t x) { txt() << x << "\n"; }
inline void record(bool b) { txt() << (b ? "True" : "False") << "\n"; }
inline void record(const std::string& s) { txt() << s << "\n"; }
inline void record(const char* s) { txt() << s << "\n"; }
inline void record(const add::Point& p) {
    txt() << "[" << add::detail::py_repr(p.x) << ", " << add::detail::py_repr(p.y) << ", "
          << add::detail::py_repr(p.z) << "]\n";
}
inline void record(const add::Point2& p) {
    txt() << "[" << add::detail::py_repr(p.x) << ", " << add::detail::py_repr(p.y) << "]\n";
}
inline void record(const add::Color& c) {
    txt() << "(" << c.r << ", " << c.g << ", " << c.b;
    if (c.alpha < 1.0 || !c.image.empty()) txt() << ", " << add::detail::py_repr(c.alpha);
    if (!c.image.empty()) txt() << ", '" << c.image << "'";
    txt() << ")\n";
}
template <class T>
inline void record(const std::vector<T>& xs) {
    record((long long)xs.size());
    for (const T& x : xs) record(x);
}

}  // namespace parity

using parity::record;
using parity::save_as;
using parity::save_case;
using parity::save_mesh;

#define CASE(name)                                                     \
    static void case_##name();                                         \
    static parity::Reg reg_##name(#name, case_##name);                 \
    static void case_##name()

int main(int argc, char** argv) {
    std::vector<std::string> only(argv + 1, argv + argc);
    int n = 0;
    for (const parity::Case& c : parity::cases()) {
        if (!only.empty() && std::find(only.begin(), only.end(), c.name) == only.end()) continue;
        parity::current() = c.name;
        add::clear();
        add::seed(20260926);
        try {
            c.fn();
        } catch (const std::exception& e) {
            std::fprintf(stderr, "case %s: exception: %s\n", c.name.c_str(), e.what());
            parity::txt() << "EXCEPTION\n";
        }
        if (parity::out().is_open()) parity::out().close();
        ++n;
    }
    std::printf("%d cases\n", n);
    return 0;
}

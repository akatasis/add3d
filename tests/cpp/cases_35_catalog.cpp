#include "parity.hpp"

// surface() calls fit() (section 40).  With a header that lacks it its calls compile but
// cannot link, so its cases are built only when section 40's own tests are here too (at
// integration) -- or when PARITY_PENDING is defined (with PARITY_PENDING=1 set for the
// Python half).
#if defined(PARITY_PENDING) || __has_include("cases_40_transform.cpp")
#define WITH_40 1
#else
#define WITH_40 0
#endif

using add::Point;

// Record whether f() throws (an exception would end the case).
template <class F>
static void raises(F f) {
    try {
        f();
    } catch (const std::exception&) {
        record("raises");
        return;
    }
    record("returns");
}

CASE(names) {
    std::vector<std::string> names = add::surface_names();
    record((long long)names.size());
    for (const std::string& name : names) record(name);
    record((long long)add::SURFACES().size());
    for (const auto& kv : add::SURFACES()) record(kv.first);           // the dictionary's own order
    record(add::SURFACES().count("apple") > 0);
    record(add::SURFACES().count("nope") > 0);
}

CASE(catalogue) {
    for (const std::string& name : add::surface_names()) {
        const add::SurfaceEntry& e = add::SURFACES().at(name);
        record(name);
        record(e.u);
        record(e.v);
        record(e.wrap[0]);
        record(e.wrap[1]);
        record(e.grid[0]);
        record(e.grid[1]);
        record(e.note);
        record(e.flip);
        for (const auto& kv : e.params) {
            record(kv.first);
            record(kv.second);
        }
    }
}

CASE(functions) {
    const double at[6][2] = {{0.0, 0.0}, {0.25, 0.3}, {0.5, 0.5}, {0.8, 0.9}, {1.0, 1.0}, {0.37, 0.61}};
    for (const std::string& name : add::surface_names()) {
        add::SurfaceFn f = add::surface_function(name);
        const add::SurfaceEntry& e = add::SURFACES().at(name);
        double u0 = e.u[0], u1 = e.u[1], v0 = e.v[0], v1 = e.v[1];
        for (const auto& ab : at) {
            double u = u0 + (u1 - u0) * ab[0];
            double v = v0 + (v1 - v0) * ab[1];
            record(name);
            record(f(u, v));
        }
    }
}

CASE(functions_params) {
    add::SurfaceFn f = add::surface_function("bohemian_dome", {{"a", 0.8}, {"c", 2}});
    record(f(1.0, 2.0));
    f = add::surface_function("horn", {{"b", 2.0}});
    record(f(0.5, 1.0));
    f = add::surface_function("klein_bottle", {{"a", 3.0}, {"b", 8.0}});
    record(f(1.0, 2.0));
    record(f(4.0, 2.0));
    f = add::surface_function("antisymmetric_torus", {{"R", 3.0}, {"r", 1.0}, {"a", 0.5}});
    record(f(0.3, 0.7));
    f = add::surface_function("twisted_eight_torus", {{"r", 0.25}});
    record(f(5.0, 1.0));
    f = add::surface_function("mobius", {{"R", 1.0}});
    record(f(2.0, 0.25));
    f = add::surface_function("enneper");
    record(f(0.5, -1.5));
    f = add::surface_function("hyperbolic_helicoid", {{"a", 1.0}});
    record(f(-1.0, 2.0));
    f = add::surface_function("worm", {{"b", 3.0}});
    record(f(10.0, 1.0));
}

CASE(function_errors) {
    add::SurfaceFn f = add::surface_function("dini", {{"z", 1.0}});
    record("made");
    raises([&] { f(1.0, 1.0); });
    f = add::surface_function("enneper", {{"a", 1.0}});
    record("made");
    raises([&] { f(0.5, 0.5); });
    raises([] { add::surface_function("nope"); });
    f = add::surface_function("pillow", {{"a", 0.9}});
    raises([&] { f(1.0, 1.0); });
}

// -- surface (needs fit: section 40) ---------------------------------------------------

#if WITH_40
CASE(surfaces_all) {
    std::vector<std::string> names = add::surface_names();
    for (size_t i = 0; i < names.size(); ++i) add::surface(names[i], {4.0 * i, 0, 0}, 3, 8);
    save_case();
}

CASE(surface_options) {
    add::surface("pillow");
    add::surface("klein_bottle", {10, 0, 0}, 4, {12, 6}, "teal");
    add::surface("dini", {20, 0, 0}, 4, 10, [](double u, double) { return add::hsv(u / 12); });
    add::surface("pillow", {0, 10, 0}, 3, 6, "red", 0.1);
    add::surface("mobius", {10, 10, 0}, 2, {20, 4}, "blue", 0.0, true);
    add::surface("horn", {20, 10, 0}, std::nullopt, 8, "gold", 0.0, false, {{"a", 2.0}, {"c", 0.5}});
    add::surface("cosine_surface", {0, 20, 0}, 2, 6);
    add::surface("sine_surface", {10, 20, 0}, 2, {5, 7}, [](double, double) { return add::random_color(); });
    add::surface("snail", {20, 20, 0}, 0.5, 9, "navy", -0.05, false);
    save_case();
}

CASE(surface_errors) {
    raises([] { add::surface("nope"); });
    raises([] { add::surface("dini", {0, 0, 0}, 2, 4, add::DEFAULT_COLOR, 0.0, false, {{"z", 1.0}}); });
    record((long long)add::pop().F.size());                            // (it left the scene pushed)
    add::box({0, 0, 0}, 1);
    save_case();
}
#endif

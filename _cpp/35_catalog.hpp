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
//@@definitions
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

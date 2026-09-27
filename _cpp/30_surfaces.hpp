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
//@@definitions
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

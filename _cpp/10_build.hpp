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
//@@definitions
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

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
//@@definitions
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

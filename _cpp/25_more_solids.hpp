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
//@@definitions
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

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
//@@definitions
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

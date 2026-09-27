// 17 -- fractals: a small rule, applied again and again.
//
// Recursion is where "a 3D model written as a program" really earns its keep.
// None of these could sensibly be drawn by hand, and each is a dozen lines.
#include "add.hpp"

const double CELL = 7.0;
std::vector<std::pair<std::string, add::Mesh>> shown;


void show(const std::string& name, const add::Mesh& M, double size = 5.0) {
    shown.push_back({name, add::place(add::fit(M, size), {0, 0, 0})});
}


// --------------------------------------------------------------------------
//  Menger sponge -- a cube with its middles removed, over and over
// --------------------------------------------------------------------------
// Which unit cells of a 3**level grid are solid.
std::vector<add::Cell> menger(int level) {
    std::vector<add::Cell> cells;                  // (a set in Python: every cell is added once)
    int n = (int)add::detail::py_pow(3, level);
    for (int x = 0; x < n; ++x) {
        for (int y = 0; y < n; ++y) {
            for (int z = 0; z < n; ++z) {
                int a = x, b = y, c = z;
                bool solid = true;
                for (int step = 0; step < level; ++step) {
                    int middles = (a % 3 == 1) + (b % 3 == 1) + (c % 3 == 1);
                    if (middles >= 2) {
                        solid = false;
                        break;
                    }
                    a = a / 3; b = b / 3; c = c / 3;
                }
                if (solid)
                    cells.push_back({x, y, z});
            }
        }
    }
    return cells;
}


// --------------------------------------------------------------------------
//  Sierpinski tetrahedron -- four copies of itself, half the size
// --------------------------------------------------------------------------
add::Mesh sierpinski(int level, const add::Color& col) {
    add::polyhedron("tetrahedron", {0, 0, 0}, 1.0, col);
    add::Mesh piece = add::layer();
    for (int step = 0; step < level; ++step) {
        double s = add::detail::py_pow(2.0, step);
        std::vector<add::Mesh> copies = {add::move(piece, {0, 0, 0}),
                                         add::move(piece, {0, s * 1.633, s * 1.633}),
                                         add::move(piece, {s * 1.633, 0, s * 1.633}),
                                         add::move(piece, {s * 1.633, s * 1.633, 0})};
        piece = add::merge(copies);
    }
    return piece;
}


// --------------------------------------------------------------------------
//  A recursive tree -- a trunk that splits into smaller trunks
// --------------------------------------------------------------------------
void branch(const add::Point& start, const add::Point& direction, double length, double radius, int depth) {
    add::Point end;
    for (int i = 0; i < 3; ++i)
        end[i] = start[i] + direction[i] * length;
    std::string col = depth > 2 ? "brown" : "lime";
    add::cylinder(start, end, radius, 8, col);
    if (depth == 0) {
        add::sphere(end, radius * 3.2, 6, "lime");
        return;
    }
    for (int twig = 0; twig < 3; ++twig) {
        add::Point d;
        for (int i = 0; i < 3; ++i)
            d[i] = direction[i] + add::uniform(-0.65, 0.65);
        d[1] += 0.45;
        double n = add::sqrt(d[0] * d[0] + d[1] * d[1] + d[2] * d[2]);
        d = {d[0] / n, d[1] / n, d[2] / n};
        branch(end, d, length * add::uniform(0.6, 0.8), radius * 0.68,
               depth - 1);
    }
}


// --------------------------------------------------------------------------
//  A Koch-like snowflake extruded into a solid prism
// --------------------------------------------------------------------------
add::Profile koch(const add::Profile& points, int level) {
    if (level == 0)
        return points;
    add::Profile out;
    int n = (int)points.size();
    for (int i = 0; i < n; ++i) {
        add::Point2 a = points[i];
        add::Point2 b = points[(i + 1) % n];
        add::Point2 d = {(b[0] - a[0]) / 3.0, (b[1] - a[1]) / 3.0};
        add::Point2 p1 = {a[0] + d[0], a[1] + d[1]};
        add::Point2 p2 = {a[0] + 2 * d[0], a[1] + 2 * d[1]};
        // the tip of the little triangle: rotate d by -60 degrees
        double cs = add::cos(-add::pi / 3), sn = add::sin(-add::pi / 3);
        add::Point2 tip = {p1[0] + d[0] * cs - d[1] * sn, p1[1] + d[0] * sn + d[1] * cs};
        out.insert(out.end(), {a, p1, tip, p2});
    }
    return koch(out, level - 1);
}


// --------------------------------------------------------------------------
//  A Pythagoras tree of boxes, grown in 3D
// --------------------------------------------------------------------------
// A square standing on the edge ``corner -> corner + along``.
//
// ``up`` is ``along`` turned a quarter turn, so the square is
// corner, corner+along, corner+along+up, corner+up.  On its top edge sit
// two smaller squares, meeting at a right angle -- and so on downwards.
void pythagoras(const add::Point2& corner, const add::Point2& along, int depth) {
    if (depth == 0)
        return;
    add::Point2 up = {-along[1], along[0]};
    add::Profile p = {{corner[0], corner[1]}, {corner[0] + along[0], corner[1] + along[1]},
                      {corner[0] + along[0] + up[0], corner[1] + along[1] + up[1]},
                      {corner[0] + up[0], corner[1] + up[1]}};
    add::extrude(p, {0, 0, 0.35},
                 add::hsv(0.08 + 0.035 * depth, 0.5, 0.55 + 0.05 * depth),
                 1, 0.0, 1.0, {0, 0, -0.175});          // steps, twist, scale as by default; center
    add::Point2 a = p[3], b = p[2];                        // the top edge
    add::Point2 apex = {(a[0] + b[0]) / 2.0 + up[0] / 2.0, (a[1] + b[1]) / 2.0 + up[1] / 2.0};
    pythagoras(a, {apex[0] - a[0], apex[1] - a[1]}, depth - 1);
    pythagoras(apex, {b[0] - apex[0], b[1] - apex[1]}, depth - 1);
}


int main() {
    // Menger sponge
    add::voxels(menger(3), 1.0, {0, 0, 0}, "gold");
    add::Mesh sponge = add::layer();
    show("Menger sponge (level 3)", add::color_by(
        sponge, [](const add::Point& p) { return add::hsv(0.08 + p[1] / 90.0, 0.6, 1.0); }));

    // Sierpinski tetrahedron
    show("Sierpinski tetrahedron", add::color_by(
        sierpinski(5, "white"), [](const add::Point& p) { return add::hsv((p[0] + p[2]) / 90.0, 0.7, 1.0); }));

    // A recursive tree
    add::seed(11);
    branch({0, 0, 0}, {0, 1, 0}, 2.2, 0.22, 5);
    show("recursive tree", add::layer());

    // A Koch-like snowflake
    add::Profile triangle;
    for (double a : {add::pi / 2, add::pi / 2 + 2 * add::pi / 3,
                     add::pi / 2 + 4 * add::pi / 3})
        triangle.push_back({add::cos(a), add::sin(a)});
    add::extrude(koch(triangle, 4), {0, 0.45, 0}, "sky");
    show("Koch snowflake prism", add::layer());

    // A Pythagoras tree
    pythagoras({0.0, 0.0}, {1.4, 0.0}, 9);
    show("Pythagoras tree", add::layer());

    int columns = 3;
    for (int i = 0; i < (int)shown.size(); ++i) {
        const auto& [name, M] = shown[i];
        add::mesh(add::move(M, {(i % columns) * CELL, 0, (i / columns) * CELL}));
        std::printf("%2d. %-26s %7d faces\n", i + 1, name.c_str(), (int)M.polygons());
    }

    add::mesh(add::limit_colors(add::layer(), 50));   // at most 50 colours, so the .obj suits Sketchfab
    add::check();
    add::save("fractals.off");
}

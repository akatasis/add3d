// 38 -- the five regular polyhedra and what can be made of them.
//
// Row by row (front to back):
//
// 1. the Platonic solids themselves -- ``add::tetrahedron``, ``add::polyhedron
//    ("cube")``, ``add::octahedron``, ``add::dodecahedron``, ``add::icosahedron``,
//    all with their vertices on a sphere of the same radius and the average of
//    their vertex coordinates exactly at the centre;
// 2. their duals (``add::dual``: a vertex for every face) -- cube and
//    octahedron swap, dodecahedron and icosahedron swap, the tetrahedron is
//    its own dual;
// 3. their truncations (``add::truncate``: every corner cut off) -- the
//    truncated icosahedron is the football of example 37;
// 4. geodesic domes (``add::refine`` splits every face into four, three times,
//    ``add::spherify`` pushes the points out onto the sphere) -- the
//    icosahedron gives ``add::sphere`` itself;
// 5. the smooth limit surfaces (``add::smooth``: generalised Catmull-Clark
//    with 8 cells per edge) -- five different soft balls.
//
// Parameter: ``LEVEL`` (refinement steps of the domes).
#include "add.hpp"

const int LEVEL = 3;
const std::vector<std::string> NAMES = {"tetrahedron", "cube", "octahedron", "dodecahedron", "icosahedron"};
const std::vector<std::string> COLORS = {"red", "gold", "green", "sky", "purple"};
const double STEP = 3.4;                                  // spacing between solids
const double R = 1.2;


// What Python's print() shows for a list of three numbers: [0.0, 0.0, 0.0].
std::string str(const add::Point& p) {
    return "[" + add::detail::py_repr(p[0]) + ", " + add::detail::py_repr(p[1]) + ", "
           + add::detail::py_repr(p[2]) + "]";
}


int main() {
    for (int col = 0; col < (int)NAMES.size(); ++col) {
        std::string name = NAMES[col], color = COLORS[col];
        double x = (col - 2) * STEP;
        add::Mesh solid = add::make([&] { add::polyhedron(name, {0, 0, 0}, R, color); });
        add::Points points = add::polyhedron_points(name, {0, 0, 0}, R);
        add::Point centre;
        for (int a = 0; a < 3; ++a) {
            double s = 0.0;                               // (Python: sum(p[a] for p in points))
            for (const add::Point& p : points)
                s += p[a];
            centre[a] = s / points.size();
        }
        add::Point average = {add::detail::py_round(centre[0], 9) + 0.0, add::detail::py_round(centre[1], 9) + 0.0,
                              add::detail::py_round(centre[2], 9) + 0.0};
        std::printf("%-13s %2zu vertices %2zu faces %2zu edges, valence %d, edge %.3f, "
                    "vertex average %s\n", name.c_str(), points.size(), solid.F.size(),
                    add::edges(solid).size(), add::valence(solid, 0),
                    add::mean_edge_length(solid),
                    str(average).c_str());

        std::vector<add::Mesh> rows = {
            solid,                                                  // 1. the solid
            add::color(add::dual(solid), add::shade(color, 0.75)),  // 2. its dual
            add::truncate(solid, 1 / 3.0, add::shade(color, 0.5)),  // 3. corners cut
            add::spherify(add::refine(solid, LEVEL)),               // 4. geodesic dome
            add::smooth(solid, 8),                                  // 5. limit surface
        };
        for (int row = 0; row < (int)rows.size(); ++row) {
            const add::Mesh& shape = rows[row];
            // duals and smooth balls come out smaller: scale each back to radius R
            double reach = 0.0;                           // (Python: max(... for p in shape.V))
            for (const add::Point& p : shape.V)
                reach = std::max(reach, add::distance(p, {0, 0, 0}));
            add::mesh(add::move(add::zoom(shape, R / reach, add::Point{0, 0, 0}), {x, 0, -row * STEP}));
        }
        // the edges of the plain solid, to show its structure
        add::wireframe(add::move(solid, {x, 0, 0}), 0.03, 6, add::Color(40, 40, 40));
        std::string upper = name;                         // (Python: name.upper())
        for (char& ch : upper)
            ch = (char)std::toupper((unsigned char)ch);
        add::text(upper, {x, -R - 0.05, 1.8}, 0.24, std::nullopt, "black",
                  {1, 0, 0}, {0, 0, -1}, "center");
    }

    std::vector<std::string> labels = {"SOLID", "DUAL", "TRUNCATED", "GEODESIC", "SMOOTH"};
    for (int row = 0; row < (int)labels.size(); ++row) {
        const std::string& label = labels[row];
        add::text(label, {-2 * STEP - 2.1, -R - 0.05, -row * STEP}, 0.24,
                  std::nullopt, "black", {1, 0, 0}, {0, 0, -1}, "center");
    }

    add::check();
    add::save("polyhedra.off");
}

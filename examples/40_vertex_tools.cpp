// 40 -- building on the vertices, edges and faces of a polyhedron.
//
// Four models that need to *ask* a mesh about itself:
//
// 1. a buckyball (C60): the sixty vertices of the truncated icosahedron are
//    atoms, its ninety edges (``add::edges``) are bonds;
// 2. a spiky virus: a geodesic sphere with a spike on every vertex, pointing
//    along ``add::vertex_normal``; the twelve vertices with five neighbours
//    (``add::valence``) get red spikes, the rest blue, and the spike radius
//    comes from ``add::mean_neighbor_distance``;
// 3. a stellated dodecahedron: a pyramid on every face, built from
//    ``add::face_center`` and ``add::face_normal``;
// 4. a dodecahedron cage with its dual icosahedron inside: bars along the
//    edges, balls on the vertices, and the icosahedron's vertices are the
//    face centres (``add::dual``).
//
// Parameter: ``SPIKE`` (spike length of the virus).
#include "add.hpp"

const double SPIKE = 0.9;
const double X = 4.0;                                     // spacing


int main() {
    // --- 1. buckyball --------------------------------------------------------
    add::Mesh ico = add::make([] { add::icosahedron({0, 0, 0}, 1.6); });
    add::Mesh c60 = add::truncate(ico, 1 / 3.0);
    double bond = add::mean_edge_length(c60);
    for (const add::Point& p : c60.V)
        add::sphere({p[0] - 1.5 * X, p[1], p[2]}, 0.13, 6, {40, 40, 40});
    for (auto [a, b] : add::edges(c60)) {
        add::Point pa = c60.V[a], pb = c60.V[b];
        add::cylinder({pa[0] - 1.5 * X, pa[1], pa[2]}, {pb[0] - 1.5 * X, pb[1], pb[2]},
                      0.05, 8, "silver");
    }
    std::printf("C60: %zu atoms, %zu bonds of length %.3f\n", c60.V.size(), add::edges(c60).size(), bond);

    // --- 2. spiky virus ------------------------------------------------------
    add::Mesh shell = add::make([] { add::icosphere({0, 0, 0}, 1.3, 2, {230, 200, 90}); });   // 162 vertices
    add::mesh(add::move(shell, {-0.5 * X, 0, 0}));
    int fives = 0;
    for (int i = 0; i < (int)shell.V.size(); ++i) {
        const add::Point& p = shell.V[i];
        add::Point n = add::vertex_normal(shell, i);
        double r = 0.35 * add::mean_neighbor_distance(shell, i);
        add::Point tip = {p[0] + n[0] * SPIKE, p[1] + n[1] * SPIKE, p[2] + n[2] * SPIKE};
        bool five = add::valence(shell, i) == 5;
        fives += five;
        add::cone({p[0] - 0.5 * X, p[1], p[2]}, {tip[0] - 0.5 * X, tip[1], tip[2]}, r, 8,
                  five ? add::Color("red") : add::Color(60, 90, 200));
    }
    std::printf("virus: %zu spikes, %d of them on five-neighbour vertices\n", shell.V.size(), fives);

    // --- 3. stellated dodecahedron --------------------------------------------
    add::Mesh dode = add::make([] { add::dodecahedron({0, 0, 0}, 1.4); });
    for (int f = 0; f < (int)dode.F.size(); ++f) {
        add::Point c = add::face_center(dode, f);
        add::Point n = add::face_normal(dode, f);
        add::Point apex = {c[0] + n[0] * 1.3 + 0.5 * X, c[1] + n[1] * 1.3, c[2] + n[2] * 1.3};
        add::Points corners = dode.face_points(f);
        for (int k = 0; k < (int)corners.size(); ++k) {
            add::Point a = corners[k], b = corners[(k + 1) % corners.size()];
            add::triangle({a[0] + 0.5 * X, a[1], a[2]}, {b[0] + 0.5 * X, b[1], b[2]}, apex,
                          add::hsv(f / 12.0, 0.7, 0.9));
        }
    }

    // --- 4. cage with its dual inside ----------------------------------------
    add::Mesh cage = add::make([] { add::dodecahedron({1.5 * X, 0, 0}, 1.6); });
    add::wireframe(cage, 0.05, 8, add::Color("gold"));
    add::Mesh inner = add::dual(cage);                    // an icosahedron
    add::mesh(add::color(inner, "teal"));
    add::wireframe(inner, 0.03, 6, add::Color(40, 40, 40), false);

    // the pyramids were drawn triangle by triangle: weld their shared edges
    add::mesh(add::clean(add::layer()));
    add::check();
    add::save("vertex_tools.off");
}

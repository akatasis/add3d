// 37 -- a football from the twelve vertices of an icosahedron.
//
// A classic football is a *truncated icosahedron*: cut every corner off an
// icosahedron one third of the way along its edges and you get 12 pentagons
// (one per old vertex) and 20 hexagons (one per old face).
//
// The left ball is built by hand from coordinates, to show the vertex tools:
// ``add::polyhedron_points`` gives the twelve vertices, ``add::neighbors``
// lists the five neighbours of each in order around it, and ``add::lerp``
// walks a third of the way along every edge.  The right ball is the same
// thing in one call (``add::truncate``), painted by the number of corners
// (``add::color_by_sides``) and rounded into a real ball with the
// generalised Catmull-Clark surface (``add::smooth``), which keeps each panel
// its own colour.
//
// Parameter: ``CUT`` (1/3 gives the football; 1/2 cuts to the edge midpoints).
#include "add.hpp"

const double CUT = 1 / 3.0;
const double R = 2.5;


int main() {
    // --- the icosahedron and what we know about it --------------------------
    add::Mesh ico = add::make([] { add::icosahedron({0, 0, 0}, R, "white"); });
    add::Points points = add::polyhedron_points("icosahedron", {0, 0, 0}, R);
    std::printf("icosahedron: %zu vertices, %zu faces, %zu edges\n",
                points.size(), ico.F.size(), add::edges(ico).size());
    std::printf("vertex 0 has %d neighbours, %.3f apart on average (edge length %.3f)\n",
                add::valence(ico, 0), add::mean_neighbor_distance(ico, 0),
                add::mean_edge_length(ico));

    // --- ball 1: panels built by hand from the coordinates -------------------
    for (int v = 0; v < (int)points.size(); ++v) {        // one pentagon per vertex
        std::vector<int> ring = add::neighbors(ico, v);   // 5 neighbours, in order
        add::Points corners;
        for (int u : ring)
            corners.push_back(add::lerp(points[v], points[u], CUT));
        add::polygon(corners, "black");
    }
    for (const add::Face& f : ico.F) {                    // one hexagon per face
        add::Points corners;
        for (int i = 0; i < 3; ++i) {
            int a = f[i], b = f[(i + 1) % 3];
            corners.push_back(add::lerp(points[a], points[b], CUT));
            corners.push_back(add::lerp(points[b], points[a], CUT));
        }
        add::polygon(corners, "white");
    }
    add::Mesh panels = add::clean(add::layer());          // weld the shared corners
    add::mesh(add::move(panels, {-3.2, 0, 0}));
    add::wireframe(add::move(panels, {-3.2, 0, 0}), 0.03, 6, add::Color(40, 40, 40), false);

    // --- ball 2: add::truncate + add::smooth -----------------------------------
    add::Mesh ball = add::truncate(ico, CUT);             // 32 flat panels
    ball = add::color_by_sides(ball, {{5, "black"}, {6, "white"}});
    ball = add::smooth(ball, 16);                         // round: 11 520 cells on the limit surface
    add::mesh(add::move(ball, {3.2, 0, 0}));

    // a floor to stand on, and the names
    add::cylinder({0, -R - 0.4, 0}, {0, -R - 0.1, 0}, 7.5, 64, {60, 140, 60});
    add::text("32 PANELS", {-3.2, -R - 0.1, 3.4}, 0.5, std::nullopt, "white", {1, 0, 0},
              {0, 0, -1}, "center");
    add::text("SMOOTHED", {3.2, -R - 0.1, 3.4}, 0.5, std::nullopt, "white", {1, 0, 0},
              {0, 0, -1}, "center");

    add::check();
    add::save("football.off");
}

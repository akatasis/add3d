// 44 -- a geodesic dome: the observatory principle, built as a house.
//
// Buckminster Fuller's domes are geodesic spheres cut in half: the
// icosahedron's triangles are split (``add::refine``) and pushed out onto the
// sphere (``add::spherify``) -- the same construction as ``add::sphere`` --
// and only the top half is kept (``add::cut``).  The struts are the edges of
// that half (``add::wireframe``), the panels are the triangles themselves,
// shrunk a little towards their centres so that the struts show, and the
// rim of the cut (``add::boundary_loops``) gets a ring beam.  A door is cut
// out with ``add::difference``, and the twelve original icosahedron vertices,
// which still have five neighbours (``add::valence``) instead of six, get a
// hub of their own colour -- that is where the pentagons of a dome sit.
//
// Parameter: ``LEVEL`` (refinement steps: 2 gives a 2V-style dome, 3 a 4V).
#include "add.hpp"

const int LEVEL = 2;
const double R = 4.0;


int main() {
    // the sphere and its upper half
    add::Mesh ico = add::make([] { add::icosahedron({0, 0, 0}, R); });
    double phi = (1 + add::sqrt(5)) / 2;
    ico = add::rotateZ(ico, add::atan(1 / phi));          // turn a vertex to the very top
    add::Mesh dome = add::spherify(add::refine(ico, LEVEL));
    add::Mesh half = add::cut(dome, {0, 0, 0}, {0, -1, 0}, false);   // keep what is behind the plane
    std::printf("dome: %zu triangles, %zu open edges along the rim, one rim of %zu vertices\n",
                half.F.size(), add::boundary_edges(half).size(), add::boundary_loops(half)[0].size());

    // panels: every triangle shrunk towards its centre, coloured by height
    for (int i = 0; i < (int)half.F.size(); ++i) {
        add::Point c = add::face_center(half, i);
        add::Points corners;
        for (const add::Point& p : half.face_points(i))
            corners.push_back(add::lerp(p, c, 0.12));
        double shade = (int)(c[1] / R * 6) / 6.0;         // six bands of blue, not 180 shades
        add::polygon(corners, add::gradient(shade, {200, 220, 240}, {40, 90, 160}));
    }
    add::Mesh panels = add::solidify(add::layer(), 0.04);
    add::mesh(panels);

    // struts along the edges and hubs on the vertices; five-way hubs in red
    add::wireframe(half, 0.06, 8, add::Color(70, 70, 75), false);
    for (int v = 0; v < (int)half.V.size(); ++v) {
        if (!add::vertex_faces(half, v).empty() && half.V[v][1] > 0.05) {
            bool five = add::valence(half, v) == 5;
            add::sphere(half.V[v], five ? 0.13 : 0.09, 6, five ? add::Color("red") : add::Color(50, 50, 55));
        }
    }

    // the ring beam along the rim, and a floor
    std::vector<int> rim = add::boundary_loops(half)[0];
    for (int k = 0; k < (int)rim.size(); ++k) {
        add::Point a = half.V[rim[k]], b = half.V[rim[(k + 1) % rim.size()]];
        add::cylinder(a, b, 0.09, 8, {70, 70, 75});
    }
    add::cylinder({0, -0.25, 0}, {0, 0, 0}, R + 0.3, 64, {150, 140, 120});

    // a door: cut a block out of everything built so far
    add::Mesh house = add::layer();
    add::Mesh door = add::make([] { add::cuboid({0, 1.0, R - 0.2}, {1.3, 2.2, 1.2}, "black"); });
    add::mesh(add::difference(house, door));

    add::check();
    add::save("geodesic_dome.off");
}

// 43 -- a planet with craters, an ocean and two rocky moons.
//
// The planet is a geodesic sphere (``add::icosphere``) whose vertices are
// lifted by a bumpy height function and painted by height and latitude with
// ``add::color_by``: ocean, beach, land, mountains, and snow at the poles.
// Craters are punched at a few face centres (``add::face_centers``) with
// ``add::difference``.  The moons are an octahedron and a tetrahedron,
// refined, pushed out to a ball and roughened with ``add::jitter``; the ring
// is a flat annulus given a little thickness with ``add::solidify``.
//
// Everything here also uses the vertex tools: ``add::adjacency`` averages
// each vertex height with its neighbours once (a cheap smoothing of the
// noise), and ``add::polyhedron_faces`` / ``add::edge_length`` measure the
// moons before they are roughened.
//
// Parameter: ``ROUGH`` (height of the mountains).
#include "add.hpp"

const double ROUGH = 0.18;
const double R = 3.0;


// A cheap 'noise': sums of sines with different directions.
double bumps(const add::Point& p) {
    auto [x, y, z] = p;
    return (add::sin(3.1 * x + 1.3 * y) + add::sin(2.7 * y - 1.9 * z)
            + add::sin(2.3 * z + 3.7 * x) + 0.5 * add::sin(7 * x) * add::sin(5 * z)) / 3.5;
}


add::Color paint(const add::Point& p) {
    double d = add::distance(p, {0, 0, 0}) - R;
    double lat = std::abs(p[1]) / R;
    if (lat > 0.82)
        return "white";
    if (d < 0.003)
        return {30, 80, 180};                             // ocean
    if (d < 0.03)
        return {230, 210, 150};                           // beach
    if (d < 0.25)
        return {80, 150, 60};                             // land
    return {150, 140, 130};                               // mountains
}


// A moon: how to draw it, and the name of that function (C++ functions do not
// know their own names -- Python's draw.__name__).
struct Moon {
    void (*draw)(const add::Point&, double, const add::Color&);
    std::string name;
    add::Point at;
    double size;
    add::Color color;
};


int main() {
    add::seed(7);

    // --- the planet -----------------------------------------------------------
    add::Mesh globe = add::make([] { add::icosphere({0, 0, 0}, R, 5); });   // 20480 triangles
    std::vector<double> heights;
    for (const add::Point& p : globe.V)
        heights.push_back(bumps(p));
    std::vector<std::vector<int>> neighbours = add::adjacency(globe);      // once, for all vertices
    std::vector<double> averaged;
    for (size_t i = 0; i < heights.size(); ++i) {
        double h = heights[i];
        const std::vector<int>& nb = neighbours[i];
        double sum = 0.0;
        for (int j : nb)
            sum += heights[j];
        averaged.push_back((h + sum / nb.size()) / 2.0);  // average with the ring
    }
    heights = averaged;
    add::Points lifted_points;
    for (size_t i = 0; i < globe.V.size(); ++i) {
        const add::Point& p = globe.V[i];
        double h = heights[i];
        lifted_points.push_back({p[0] * (1 + ROUGH * std::max(h, 0.0)), p[1] * (1 + ROUGH * std::max(h, 0.0)),
                                 p[2] * (1 + ROUGH * std::max(h, 0.0))});   // sea level stays at R
    }
    add::Mesh lifted(lifted_points, globe.F, globe.C);

    add::Mesh planet = add::color_by(lifted, paint);
    // craters: a ball subtracted at a few face centres
    add::Points centres = add::face_centers(planet);
    for (size_t k = 0; k < centres.size(); k += 5100) {
        add::Point c = centres[k];
        add::Mesh hole = add::make([&] { add::sphere({c[0] * 1.03, c[1] * 1.03, c[2] * 1.03}, 0.35, 8, "grey"); });
        planet = add::difference(planet, hole);
    }
    add::mesh(planet);

    // --- moons and a ring -------------------------------------------------------
    std::vector<Moon> moons = {{add::octahedron, "octahedron", {5.2, 1.2, -1.5}, 0.7, {150, 140, 130}},
                               {add::tetrahedron, "tetrahedron", {-4.8, -0.8, 2.6}, 0.6, {120, 110, 100}}};
    for (const Moon& m : moons) {
        add::Mesh moon = add::make([&] { m.draw({0, 0, 0}, m.size, m.color); });
        std::printf("%s has %zu faces, edge %s\n", m.name.c_str(), add::polyhedron_faces(m.name).size(),
                    add::detail::py_repr(add::detail::py_round(add::edge_length(moon, 0, 1), 3)).c_str());
        moon = add::spherify(add::refine(moon, 3));
        moon = add::jitter(moon, 0.05, 1);
        add::mesh(add::move(moon, m.at));
    }
    add::Mesh band = add::make([] { add::ring({0, 0, 0}, {0.15, 1, 0.05}, 5.4, 4.2, 96, {200, 190, 170}); });
    add::mesh(add::solidify(band, 0.05));                 // a flat ring is an open sheet

    add::check();
    add::save("planet.off");
}

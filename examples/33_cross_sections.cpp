// 33 -- a gallery of cross-sections.
//
// Most solid shapes are a 2D outline moved through space.  ``profile_*``
// give the outlines -- circle, ellipse, star, gear, rounded rectangle,
// polygon -- and ``extrude``, ``prism``, ``sweep`` and ``loft`` move them:
// straight up, with a twist, along a curve, or bent afterwards with
// ``bend``.  Each piece is stood on the floor with ``ground`` and labelled;
// ``text_width`` sizes the name plates to fit.
//
// Parameter: ``TWIST`` (how much the twisted pieces turn).
#include "add.hpp"

const double TWIST = 2.5;
std::vector<std::pair<std::string, add::Mesh>> pieces;   // (name, mesh)


void piece(const std::string& name, const std::function<void()>& build) {
    add::push();
    build();
    pieces.push_back({name, add::pop()});
}


int main() {
    add::clear();                                         // start from an empty scene (it already is)

    // 1. a star extruded straight up, twisting as it goes
    piece("STAR", [] {
        add::extrude(add::profile_star(6, 1.0, 0.5), {0, 3.5, 0}, "gold",
                     50, TWIST);
    });
    // 2. a gear outline, extruded and tapered
    piece("GEAR", [] {
        add::extrude(add::profile_gear(14, 1.0, 0.25), {0, 3.0, 0}, "silver",
                     30, 0.0, [](double t) { return 1 - 0.5 * t; });
    });
    // 3. an ellipse swept along a circle: a squashed ring
    piece("ELLIPSE", [] {
        add::sweep(add::profile_ellipse(0.55, 0.25, 24),
                   [](double t) { return add::Point{1.4 * add::cos(t), 0, 1.4 * add::sin(t)}; },
                   0, 2 * add::pi, 60, "teal", true);
    });
    // 4. a circle swept along a wavy path, twisting the (invisible) frame anyway
    piece("CIRCLE", [] {
        add::sweep(add::profile_circle(0.35, 16),
                   [](double t) { return add::Point{add::sin(3 * t) * 0.6, t, add::cos(3 * t) * 0.6}; },
                   0, 3.5, 80, "orange");
    });
    // 5. a rounded rectangle, extruded and then bent into an arc
    auto bent_bar = [] {
        add::extrude(add::profile_rect(1.0, 0.5, 0.15, 5), {0, 4.0, 0}, "purple", 40);
        add::Mesh bar = add::layer();
        add::mesh(add::bend(bar, 1.6, 1, 0));
    };

    piece("BENT", bent_bar);
    // 6. a pentagon prism and its outline lofted into a twisted tower
    piece("POLYGON", [] { add::prism(add::profile_polygon(5, 1.0), 3.0, "lime", {0, 1.5, 0}); });

    auto lofted = [] {
        std::vector<add::Points> rings;
        for (int i = 0; i < 9; ++i) {
            double t = i / 8.0;
            add::Profile outline = add::profile_polygon(7, 1.0 - 0.5 * add::sin(add::pi * t), TWIST * t);
            add::Points ring;
            for (auto [x, y] : outline)
                ring.push_back({x, 3.5 * t, y});
            rings.push_back(ring);
        }
        add::loft(rings, "sky");
    };

    piece("LOFT", lofted);
    // 7. beads on a curve: points_on_curve gives the spots, spheres sit on them
    auto beads = [] {
        add::Points spots = add::points_on_curve(
            [](double t) { return add::Point{0.9 * add::cos(t), 0.3 * t, 0.9 * add::sin(t)}; }, 0, 12, 60);
        for (int i = 0; i < (int)spots.size(); ++i) {
            const add::Point& p = spots[i];
            add::sphere(p, 0.16, 4, add::hsv(i / 60.0));
        }
        add::curve([](double t) { return add::Point{0.9 * add::cos(t), 0.3 * t, 0.9 * add::sin(t)}; },
                   0, 12, 200, 6, 0.03, "black");
    };

    piece("BEADS", beads);

    // --------------------------------------------------------------------------
    //  line the pieces up on a floor, each grounded and labelled
    // --------------------------------------------------------------------------
    const double GAP = 4.2;
    std::vector<std::string> names;                       // every named colour, for the floor tiles
    for (const auto& [name, rgb] : add::COLORS())         // (sorted: a std::map keeps its keys in order)
        names.push_back(name);
    for (int i = 0; i < (int)pieces.size(); ++i) {
        auto [name, M] = pieces[i];
        double x = (i - (pieces.size() - 1) / 2.0) * GAP;
        M = add::ground(add::place(M, {0, 0, 0}), 0.0);   // centre it, then drop it to y = 0
        add::mesh(add::move(M, {x, 0, 0}));
        double w = add::text_width(name, 0.5);
        add::cuboid({x, 0.1, 2.3}, {w + 0.5, 0.2, 0.9}, add::PALETTE().at("n"));   // a name plate that fits
        add::text(name, {x - w / 2, 0.21, 2.6}, 0.5, std::nullopt, "white", {1, 0, 0}, {0, 0, -1}, "left", 1.0, 5);
        add::cuboid({x, -0.15, 0}, {GAP - 0.2, 0.3, 4.6}, add::shade(names[(3 * i) % names.size()], 0.9));
    }

    // the old string pair representation -- add.py 1.2's M[0] = ["x y z", ...] and
    // M[1] = ["n i j k r g b", ...], turned back into a mesh by as_mesh -- has no C++
    // version: an add.hpp mesh is only the Mesh struct.  So here we count what the two
    // string lists would hold (one string per vertex, one per face), and a copy stands
    // in for the mesh as_mesh would give back.
    std::cout << "scene as strings: " << add::scene().V.size() << " vertices, "
              << add::scene().F.size() << " faces\n";
    add::Mesh same = add::copy(add::scene());
    std::cout << "as_mesh gives " << same << "\n";

    add::mesh(add::limit_colors(add::layer(), 50));   // at most 50 colours, so the .obj suits Sketchfab
    add::check();
    add::save("cross_sections.off");
}

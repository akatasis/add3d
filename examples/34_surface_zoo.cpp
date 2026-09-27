// 34 -- the surface zoo: every named surface in add.py's catalogue.
//
// ``add::surface(name, ...)`` draws one of twenty-five classical parametric
// surfaces (the collection at drhuang.com): Klein bottle, Dini, Enneper,
// Boy-style owls and snails, tori with a twist ...  Here they all stand in a
// 5 x 5 grid, each scaled to the same size and labelled, so that you can pick
// the one you want to build on.  Open sheets are given a little ``thickness``
// so that every piece is a closed solid.
//
// The colouring uses two shades per surface -- 50 colours in all, which is
// exactly what an .obj for Sketchfab may have (one material per colour).
//
// Parameter: ``STRIPES`` (how many stripes each surface gets).
#include "add.hpp"

const int STRIPES = 8;
const double SIZE = 3.0;                                  // every surface fits a 3 x 3 x 3 box
const double STEP = 4.2;                                  // distance between neighbours


int main() {
    std::vector<std::string> names = add::surface_names();   // 25 names, alphabetically
    std::string joined;                                       // (Python: ", ".join(names))
    for (const std::string& name : names)
        joined += (joined.empty() ? "" : ", ") + name;
    std::printf("%zu surfaces: %s\n", names.size(), joined.c_str());

    for (int index = 0; index < (int)names.size(); ++index) {
        const std::string& name = names[index];
        int row = index / 5, col = index % 5;
        add::Point at = {(col - 2) * STEP, 0, (row - 2) * STEP};
        add::Color base = add::hsv(index / (double)names.size(), 0.75, 0.95);
        add::Color dark = add::shade(base, 0.6);
        const add::SurfaceEntry& info = add::SURFACES().at(name);
        double u0 = info.u[0], u1 = info.u[1];

        auto stripes = [=](double u, double /*v*/) {       // (u0, u1, base, dark: copied in)
            return (int)((u - u0) / (u1 - u0) * STRIPES) % 2 == 0 ? base : dark;
        };

        bool closed = info.wrap[0] && info.wrap[1];
        add::surface(name, at, SIZE, std::nullopt, stripes,
                     closed ? 0.0 : 0.06);
        // a name plate lying flat in front of the surface (one word per line)
        std::string label = name;
        for (char& ch : label)
            ch = ch == '_' ? '\n' : (char)std::toupper((unsigned char)ch);
        add::text(label, {at[0], -SIZE / 2, at[2] + SIZE / 2 + 0.45}, 0.3,
                  std::nullopt, dark, {1, 0, 0}, {0, 0, -1}, "center", 1.0, 5);
    }

    add::check();
    add::save("surface_zoo.off");
}

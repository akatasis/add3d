// 01 -- your first model.
//
// Three shapes, three colours, one file.  Compile and run it, then open first_model.off in
// MeshLab, or render it with:  python3 tools/preview.py first_model.off
//
//     g++ -std=c++17 -O2 01_first_model.cpp -o first_model && ./first_model
#include "add.hpp"

int main() {
    // Draw into the scene.  Every call adds faces; nothing is removed.
    add::box({0, 0, 0}, 2, "red");                        // centre, edge length, colour
    add::sphere({3, 0, 0}, 1.0, 20, "blue");              // centre, radius, detail, colour
    add::cylinder({0, 2, 0}, {3, 2, 0}, 0.3, 24, "gold");  // from, to, radius

    // See where you stand: polygon count, colours, whether the model is closed.
    add::check();

    // Save.  The extension decides the format: .off, .obj (+ .mtl), .ply or .stl.
    add::save("first_model.off");
}

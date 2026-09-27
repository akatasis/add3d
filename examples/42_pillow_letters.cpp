// 42 -- pillow letters: blocks, united, then rounded.
//
// Each letter is a few ``add::cuboid`` blocks that overlap.  ``add::union_``
// melts them into one watertight solid (the walls hidden inside disappear),
// and ``add::smooth`` then rounds the solid into a soft cushion -- the coarse
// block mesh is the control net of the smooth surface, so a thin bar becomes
// a rounded bar and a corner becomes a soft corner.  Cells keep the colour of
// the block they came from.
//
// Along the way the mesh tools measure what was built: ``add::edge_lengths``
// (the shortest and longest edge), ``add::face_area`` (the biggest face) and
// ``add::boundary_loops`` (an empty list once the solid is closed).  Finally
// ``add::inflate`` puffs each letter out a little, and ``add::move_vertex`` /
// ``add::set_vertices`` bend the plinth they stand on.
//
// Parameter: ``N`` (cells per control edge in the smoothing).
#include "add.hpp"

const int N = 6;
const double T = 0.9;                                     // bar thickness
const double H = 4.0;                                     // letter height


void letter_A(const add::Color& color) {
    add::cuboid({-0.9, H / 2, 0}, {T, H, T}, color);
    add::cuboid({0.9, H / 2, 0}, {T, H, T}, color);
    add::cuboid({0, H - T / 2, 0}, {2.7, T, T}, color);
    add::cuboid({0, H / 2, 0}, {2.7, T, T}, color);
}


void letter_D(const add::Color& color) {
    add::cuboid({-0.9, H / 2, 0}, {T, H, T}, color);
    add::cuboid({0.3, H - T / 2, 0}, {1.5, T, T}, color);
    add::cuboid({0.3, T / 2, 0}, {1.5, T, T}, color);
    add::cuboid({0.9, H / 2, 0}, {T, H - 1.2, T}, color);
}


// What Python's print() shows for a list of lists of numbers: [[0, 3, 2], [5, 6]], or [].
std::string str(const std::vector<std::vector<int>>& lists) {
    std::string out = "[";
    for (size_t i = 0; i < lists.size(); ++i) {
        out += i > 0 ? ", [" : "[";
        for (size_t j = 0; j < lists[i].size(); ++j)
            out += (j > 0 ? ", " : "") + std::to_string(lists[i][j]);
        out += "]";
    }
    return out + "]";
}


void build(const std::function<void(const add::Color&)>& draw, const add::Color& color, double x) {
    add::Mesh blocks = add::make([&] { draw(color); });   // the overlapping blocks
    add::Mesh solid = blocks;
    std::vector<add::Mesh> parts;
    for (size_t i = 0; i < blocks.F.size(); i += 6) {
        size_t end = std::min(i + 6, blocks.F.size());    // (Python's slice [i:i + 6])
        parts.push_back(add::Mesh(blocks.V, std::vector<add::Face>(blocks.F.begin() + i, blocks.F.begin() + end),
                                  std::vector<add::Color>(blocks.C.begin() + i, blocks.C.begin() + end)));
    }
    solid = parts[0];
    for (size_t k = 1; k < parts.size(); ++k)
        solid = add::union_(solid, parts[k]);            // melt the blocks together
    std::vector<double> L = add::edge_lengths(solid);
    int big = 0;                                          // (Python: max(range(...), key=...))
    for (int i = 1; i < (int)solid.F.size(); ++i)
        if (add::face_area(solid, i) > add::face_area(solid, big))
            big = i;
    std::printf("letter: %zu faces, edges %.2f .. %.2f, biggest face %.2f, holes: %s\n",
                solid.F.size(), *std::min_element(L.begin(), L.end()), *std::max_element(L.begin(), L.end()),
                add::face_area(solid, big), str(add::boundary_loops(solid)).c_str());
    add::Mesh soft = add::smooth(solid, N);               // the cushion
    soft = add::inflate(soft, 0.06);                      // puff it up a little
    add::mesh(add::move(soft, {x, 0.3, 0}));
}


int main() {
    build(letter_A, "red", -2.0);
    build(letter_D, "gold", 1.6);
    build(letter_D, "sky", 5.2);

    // the plinth: a slab whose top corners are pushed about, then rounded too
    add::Mesh slab = add::make([] { add::cuboid({1.6, -0.3, 0}, {10, 0.6, 3}, {90, 90, 100}); });
    std::vector<int> top;
    for (int i = 0; i < (int)slab.V.size(); ++i)
        if (slab.V[i][1] > 0 - 1e-9)
            top.push_back(i);
    std::map<int, add::PartialPoint> changes;
    for (int i : top)
        changes[i] = {std::nullopt, 0.35, std::nullopt};
    slab = add::set_vertices(slab, changes);              // raise the whole top
    slab = add::move_vertex(slab, add::nearest_vertex(slab, {6.6, 0.35, 1.5}), {0.4, 0.5, 0.4});
    add::mesh(add::smooth(slab, 12));

    add::check();
    add::save("pillow_letters.off");
}

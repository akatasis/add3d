// 18 -- a complete scene: a chess set.
//
// Everything in one place: a lathe for the pieces, layers to make each piece
// once and stamp it out, a boolean to carve the rook's battlements, a grid for
// the board, and a single ``save`` at the end.
#include "add.hpp"

const add::Color LIGHT = {235, 225, 200};
const add::Color DARK = {70, 45, 35};
const add::Color BOARD_LIGHT = {225, 210, 180};
const add::Color BOARD_DARK = {120, 70, 50};

const int SIDES = 36;                      // how round the turned pieces are


// One lathe-turned piece, standing on the origin.
add::Mesh turned(const std::function<add::Point2(double)>& profile, double height, const add::Color& col,
                 int steps = 90) {
    add::revolve(profile, {0, 0, 0}, {0, 1, 0}, 0, height, steps, SIDES, col);
    return add::layer();
}


// --------------------------------------------------------------------------
//  the six pieces, each a radius-versus-height curve
// --------------------------------------------------------------------------
add::Point2 pawn_profile(double t) {
    return {0.52 * add::exp(-4.0 * t) + 0.13
            + 0.20 * add::exp(-40 * add::detail::py_pow(t - 0.62, 2))
            + 0.23 * add::exp(-60 * add::detail::py_pow(t - 1.05, 2)), t};
}


add::Point2 bishop_profile(double t) {
    return {0.55 * add::exp(-4.5 * t) + 0.11
            + 0.18 * add::exp(-50 * add::detail::py_pow(t - 0.65, 2))
            + 0.30 * add::exp(-11 * add::detail::py_pow(t - 1.45, 2))
            + 0.10 * add::exp(-160 * add::detail::py_pow(t - 1.95, 2)), t};
}


add::Point2 queen_profile(double t) {
    return {0.62 * add::exp(-4.2 * t) + 0.12
            + 0.20 * add::exp(-45 * add::detail::py_pow(t - 0.70, 2))
            + 0.34 * add::exp(-13 * add::detail::py_pow(t - 1.60, 2))
            + 0.16 * add::exp(-90 * add::detail::py_pow(t - 2.25, 2)), t};
}


add::Point2 king_profile(double t) {
    return {0.64 * add::exp(-4.0 * t) + 0.12
            + 0.20 * add::exp(-45 * add::detail::py_pow(t - 0.72, 2))
            + 0.33 * add::exp(-12 * add::detail::py_pow(t - 1.70, 2))
            + 0.18 * add::exp(-80 * add::detail::py_pow(t - 2.40, 2)), t};
}


add::Point2 rook_profile(double t) {
    if (t < 0.28)
        return {0.62 - 0.72 * t, t};
    if (t < 1.15)
        return {0.42 - 0.10 * add::sin(add::pi * (t - 0.28) / 0.9), t};
    if (t < 1.30)
        return {0.42 + (t - 1.15) * 1.6, t};
    return {0.55, t};
}


add::Point2 knight_profile(double t) {
    return {0.60 * add::exp(-4.0 * t) + 0.16
            + 0.18 * add::exp(-50 * add::detail::py_pow(t - 0.60, 2)), t};
}


add::Mesh make_pawn(const add::Color& col) {
    add::Mesh piece = turned(pawn_profile, 1.25, col);
    add::mesh(piece);
    add::sphere({0, 1.38, 0}, 0.22, 14, col);
    return add::layer();
}


add::Mesh make_bishop(const add::Color& col) {
    add::Mesh piece = turned(bishop_profile, 2.0, col);
    add::mesh(piece);
    add::sphere({0, 2.05, 0}, 0.13, 12, col);
    add::Mesh body = add::layer();                       // take the body out FIRST ...
    add::cuboid({0, 1.80, 0}, {0.09, 0.55, 1.2}, col);
    add::Mesh notch = add::layer();                      // ... then the cutting tool
    return add::difference(body, add::rotateZ(notch, 0.35, {0, 1.8, 0}));
}


add::Mesh make_rook(const add::Color& col) {
    add::Mesh body = turned(rook_profile, 1.55, col);
    // four battlements, cut out with a boolean
    add::cuboid({0, 1.55, 0}, {1.4, 0.34, 0.26}, col);
    add::Mesh slot = add::layer();
    std::vector<add::Mesh> cuts = {slot, add::rotateY(slot, add::pi / 2, {0, 0, 0})};
    return add::difference(body, cuts);
}


add::Mesh make_queen(const add::Color& col) {
    add::Mesh piece = turned(queen_profile, 2.55, col);
    add::mesh(piece);
    add::sphere({0, 2.62, 0}, 0.16, 14, col);
    add::Mesh body = add::layer();
    // a crown of little spikes
    add::cone({0.28, 2.30, 0}, {0.36, 2.58, 0}, 0.09, 10, col);
    add::Mesh spike = add::layer();
    return add::merge({body, add::array_radial(spike, 8)});
}


add::Mesh make_king(const add::Color& col) {
    add::Mesh piece = turned(king_profile, 2.75, col);
    add::mesh(piece);
    add::cuboid({0, 3.02, 0}, {0.13, 0.55, 0.13}, col);
    add::cuboid({0, 3.12, 0}, {0.40, 0.13, 0.13}, col);
    return add::layer();
}


add::Mesh make_knight(const add::Color& col) {
    add::Mesh body = turned(knight_profile, 1.05, col);
    // the head: a swept block, bent forward
    add::cuboid({0, 0.45, 0.06}, {0.34, 1.05, 0.52}, col);
    add::Mesh head = add::layer();
    head = add::taper(add::move(head, {0, 1.05, 0}), -0.12, 1, {0, 1.05, 0});
    head = add::rotateX(head, -0.30, {0, 1.05, 0});
    add::cuboid({0, 1.72, -0.28}, {0.30, 0.34, 0.46}, col);
    add::Mesh muzzle = add::layer();
    add::cuboid({0.09, 2.00, 0.16}, {0.10, 0.28, 0.12}, col);
    add::Mesh ear = add::layer();
    return add::merge({body, head, muzzle, ear,
                       add::mirror(ear, {0, 0, 0}, {1, 0, 0})});
}


// A maker: a function that builds one kind of piece in a given colour.
using Maker = add::Mesh (*)(const add::Color&);

const std::vector<Maker> ORDER = {make_rook, make_knight, make_bishop, make_queen,
                                  make_king, make_bishop, make_knight, make_rook};


int main() {
    // --------------------------------------------------------------------------
    //  the pieces -- each shape is built once per colour and then copied
    // --------------------------------------------------------------------------
    // NOTE the order of work.  ``layer()`` takes away *everything* drawn so far,
    // so all the pieces are built while the scene is still empty; the board is
    // drawn afterwards.  Build the board first and the first ``layer()`` inside a
    // piece would swallow it.
    // (Python keys the pawn by the name "pawn"; here every piece is keyed by its maker.)
    std::map<add::Color, std::map<Maker, add::Mesh>> pieces;
    for (const add::Color& colour : {LIGHT, DARK}) {
        pieces[colour] = {{make_pawn, make_pawn(colour)}};
        for (Maker maker : std::set<Maker>(ORDER.begin(), ORDER.end()))
            pieces[colour][maker] = maker(colour);
    }

    // --------------------------------------------------------------------------
    //  the board
    // --------------------------------------------------------------------------
    for (int i = 0; i < 8; ++i) {
        for (int j = 0; j < 8; ++j) {
            add::Color col = (i + j) % 2 ? BOARD_LIGHT : BOARD_DARK;
            add::cuboid({double(i), -0.05, double(j)}, {1.0, 0.1, 1.0}, col);
        }
    }
    add::cuboid({3.5, -0.20, 3.5}, {9.6, 0.24, 9.6}, {90, 55, 40});
    add::cuboid({3.5, -0.34, 3.5}, {10.2, 0.12, 10.2}, {60, 38, 28});

    // --------------------------------------------------------------------------
    //  set the pieces out
    // --------------------------------------------------------------------------
    for (const auto& [colour, back_row, pawn_row] :
         std::vector<std::tuple<add::Color, int, int>>{{LIGHT, 0, 1}, {DARK, 7, 6}}) {
        std::map<Maker, add::Mesh>& built = pieces[colour];
        for (int i = 0; i < 8; ++i)
            add::mesh(add::move(built[make_pawn], {double(i), 0, double(pawn_row)}));
        for (int i = 0; i < (int)ORDER.size(); ++i) {
            Maker maker = ORDER[i];
            add::Mesh piece = built[maker];
            if (maker == make_knight)            // knights face the other player
                piece = add::rotateY(piece, back_row == 0 ? 0 : add::pi,
                                     {0, 0, 0});
            add::mesh(add::move(piece, {double(i), 0, double(back_row)}));
        }
    }

    add::check();
    add::save("chess_set.off");
}

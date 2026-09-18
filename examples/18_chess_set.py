"""
18 -- a complete scene: a chess set.

Everything in one place: a lathe for the pieces, layers to make each piece
once and stamp it out, a boolean to carve the rook's battlements, a grid for
the board, and a single ``save`` at the end.
"""
import add

LIGHT = [235, 225, 200]
DARK = [70, 45, 35]
BOARD_LIGHT = [225, 210, 180]
BOARD_DARK = [120, 70, 50]

SIDES = 36                      # how round the turned pieces are


def turned(profile, height, col, steps=90):
    """One lathe-turned piece, standing on the origin."""
    add.revolve(profile, [0, 0, 0], [0, 1, 0], 0, height, steps, SIDES, col)
    return add.layer()


# --------------------------------------------------------------------------
#  the six pieces, each a radius-versus-height curve
# --------------------------------------------------------------------------
def pawn_profile(t):
    return [0.52 * add.exp(-4.0 * t) + 0.13
            + 0.20 * add.exp(-40 * (t - 0.62) ** 2)
            + 0.23 * add.exp(-60 * (t - 1.05) ** 2), t]


def bishop_profile(t):
    return [0.55 * add.exp(-4.5 * t) + 0.11
            + 0.18 * add.exp(-50 * (t - 0.65) ** 2)
            + 0.30 * add.exp(-11 * (t - 1.45) ** 2)
            + 0.10 * add.exp(-160 * (t - 1.95) ** 2), t]


def queen_profile(t):
    return [0.62 * add.exp(-4.2 * t) + 0.12
            + 0.20 * add.exp(-45 * (t - 0.70) ** 2)
            + 0.34 * add.exp(-13 * (t - 1.60) ** 2)
            + 0.16 * add.exp(-90 * (t - 2.25) ** 2), t]


def king_profile(t):
    return [0.64 * add.exp(-4.0 * t) + 0.12
            + 0.20 * add.exp(-45 * (t - 0.72) ** 2)
            + 0.33 * add.exp(-12 * (t - 1.70) ** 2)
            + 0.18 * add.exp(-80 * (t - 2.40) ** 2), t]


def rook_profile(t):
    if t < 0.28:
        return [0.62 - 0.72 * t, t]
    if t < 1.15:
        return [0.42 - 0.10 * add.sin(add.pi * (t - 0.28) / 0.9), t]
    if t < 1.30:
        return [0.42 + (t - 1.15) * 1.6, t]
    return [0.55, t]


def knight_profile(t):
    return [0.60 * add.exp(-4.0 * t) + 0.16
            + 0.18 * add.exp(-50 * (t - 0.60) ** 2), t]


def make_pawn(col):
    piece = turned(pawn_profile, 1.25, col)
    add.mesh(piece)
    add.sphere([0, 1.38, 0], 0.22, 14, col)
    return add.layer()


def make_bishop(col):
    piece = turned(bishop_profile, 2.0, col)
    add.mesh(piece)
    add.sphere([0, 2.05, 0], 0.13, 12, col)
    body = add.layer()                       # take the body out FIRST ...
    add.cuboid([0, 1.80, 0], [0.09, 0.55, 1.2], col)
    notch = add.layer()                      # ... then the cutting tool
    return add.difference(body, add.rotateZ(notch, 0.35, [0, 1.8, 0]))


def make_rook(col):
    body = turned(rook_profile, 1.55, col)
    # four battlements, cut out with a boolean
    add.cuboid([0, 1.55, 0], [1.4, 0.34, 0.26], col)
    slot = add.layer()
    cuts = [slot, add.rotateY(slot, add.pi / 2, [0, 0, 0])]
    return add.difference(body, cuts)


def make_queen(col):
    piece = turned(queen_profile, 2.55, col)
    add.mesh(piece)
    add.sphere([0, 2.62, 0], 0.16, 14, col)
    body = add.layer()
    # a crown of little spikes
    add.cone([0.28, 2.30, 0], [0.36, 2.58, 0], 0.09, 10, col)
    spike = add.layer()
    return add.merge([body, add.array_radial(spike, 8)])


def make_king(col):
    piece = turned(king_profile, 2.75, col)
    add.mesh(piece)
    add.cuboid([0, 3.02, 0], [0.13, 0.55, 0.13], col)
    add.cuboid([0, 3.12, 0], [0.40, 0.13, 0.13], col)
    return add.layer()


def make_knight(col):
    body = turned(knight_profile, 1.05, col)
    # the head: a swept block, bent forward
    add.cuboid([0, 0.45, 0.06], [0.34, 1.05, 0.52], col)
    head = add.layer()
    head = add.taper(add.move(head, [0, 1.05, 0]), -0.12, 1, [0, 1.05, 0])
    head = add.rotateX(head, -0.30, [0, 1.05, 0])
    add.cuboid([0, 1.72, -0.28], [0.30, 0.34, 0.46], col)
    muzzle = add.layer()
    add.cuboid([0.09, 2.00, 0.16], [0.10, 0.28, 0.12], col)
    ear = add.layer()
    return add.merge([body, head, muzzle, ear,
                      add.mirror(ear, [0, 0, 0], [1, 0, 0])])


ORDER = [make_rook, make_knight, make_bishop, make_queen,
         make_king, make_bishop, make_knight, make_rook]

# --------------------------------------------------------------------------
#  the pieces -- each shape is built once per colour and then copied
# --------------------------------------------------------------------------
# NOTE the order of work.  ``layer()`` takes away *everything* drawn so far,
# so all the pieces are built while the scene is still empty; the board is
# drawn afterwards.  Build the board first and the first ``layer()`` inside a
# piece would swallow it.
pieces = {}
for colour in (LIGHT, DARK):
    key = tuple(colour)
    pieces[key] = {"pawn": make_pawn(colour)}
    for maker in set(ORDER):
        pieces[key][maker] = maker(colour)

# --------------------------------------------------------------------------
#  the board
# --------------------------------------------------------------------------
for i in range(8):
    for j in range(8):
        col = BOARD_LIGHT if (i + j) % 2 else BOARD_DARK
        add.cuboid([i, -0.05, j], [1.0, 0.1, 1.0], col)
add.cuboid([3.5, -0.20, 3.5], [9.6, 0.24, 9.6], [90, 55, 40])
add.cuboid([3.5, -0.34, 3.5], [10.2, 0.12, 10.2], [60, 38, 28])

# --------------------------------------------------------------------------
#  set the pieces out
# --------------------------------------------------------------------------
for colour, back_row, pawn_row in ((LIGHT, 0, 1), (DARK, 7, 6)):
    built = pieces[tuple(colour)]
    for i in range(8):
        add.mesh(add.move(built["pawn"], [i, 0, pawn_row]))
    for i, maker in enumerate(ORDER):
        piece = built[maker]
        if maker is make_knight:            # knights face the other player
            piece = add.rotateY(piece, 0 if back_row == 0 else add.pi,
                                [0, 0, 0])
        add.mesh(add.move(piece, [i, 0, back_row]))

add.check()
add.save("chess_set.off")

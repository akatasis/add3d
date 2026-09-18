"""
33 -- a gallery of cross-sections.

Most solid shapes are a 2D outline moved through space.  ``profile_*``
give the outlines -- circle, ellipse, star, gear, rounded rectangle,
polygon -- and ``extrude``, ``prism``, ``sweep`` and ``loft`` move them:
straight up, with a twist, along a curve, or bent afterwards with
``bend``.  Each piece is stood on the floor with ``ground`` and labelled;
``text_width`` sizes the name plates to fit.

Parameter: ``TWIST`` (how much the twisted pieces turn).
"""
import add

TWIST = 2.5
add.clear()                                   # start from an empty scene (it already is)
pieces = []                                   # (name, mesh)


def piece(name, build):
    add.push()
    build()
    pieces.append((name, add.pop()))


# 1. a star extruded straight up, twisting as it goes
piece("STAR", lambda: add.extrude(add.profile_star(6, 1.0, 0.5), [0, 3.5, 0], "gold",
                                  steps=50, twist=TWIST))
# 2. a gear outline, extruded and tapered
piece("GEAR", lambda: add.extrude(add.profile_gear(14, 1.0, 0.25), [0, 3.0, 0], "silver",
                                  steps=30, scale=lambda t: 1 - 0.5 * t))
# 3. an ellipse swept along a circle: a squashed ring
piece("ELLIPSE", lambda: add.sweep(add.profile_ellipse(0.55, 0.25, 24),
                                   lambda t: [1.4 * add.cos(t), 0, 1.4 * add.sin(t)],
                                   0, 2 * add.pi, 60, "teal", closed=True))
# 4. a circle swept along a wavy path, twisting the (invisible) frame anyway
piece("CIRCLE", lambda: add.sweep(add.profile_circle(0.35, 16),
                                  lambda t: [add.sin(3 * t) * 0.6, t, add.cos(3 * t) * 0.6],
                                  0, 3.5, 80, "orange"))
# 5. a rounded rectangle, extruded and then bent into an arc
def bent_bar():
    add.extrude(add.profile_rect(1.0, 0.5, 0.15, 5), [0, 4.0, 0], "purple", steps=40)
    bar = add.layer()
    add.mesh(add.bend(bar, 1.6, axis=1, around=0))


piece("BENT", bent_bar)
# 6. a pentagon prism and its outline lofted into a twisted tower
piece("POLYGON", lambda: add.prism(add.profile_polygon(5, 1.0), 3.0, "lime", (0, 1.5, 0)))


def lofted():
    rings = []
    for i in range(9):
        t = i / 8.0
        outline = add.profile_polygon(7, 1.0 - 0.5 * add.sin(add.pi * t), phase=TWIST * t)
        rings.append([[x, 3.5 * t, y] for x, y in outline])
    add.loft(rings, "sky")


piece("LOFT", lofted)
# 7. beads on a curve: points_on_curve gives the spots, spheres sit on them
def beads():
    spots = add.points_on_curve(lambda t: [0.9 * add.cos(t), 0.3 * t, 0.9 * add.sin(t)], 0, 12, 60)
    for i, p in enumerate(spots):
        add.sphere(p, 0.16, 4, add.hsv(i / 60.0))
    add.curve(lambda t: [0.9 * add.cos(t), 0.3 * t, 0.9 * add.sin(t)], 0, 12, 200, 6, 0.03, "black")


piece("BEADS", beads)

# --------------------------------------------------------------------------
#  line the pieces up on a floor, each grounded and labelled
# --------------------------------------------------------------------------
GAP = 4.2
names = sorted(add.COLORS)                    # every named colour, for the floor tiles
for i, (name, M) in enumerate(pieces):
    x = (i - (len(pieces) - 1) / 2.0) * GAP
    M = add.ground(add.place(M, [0, 0, 0]), 0.0)      # centre it, then drop it to y = 0
    add.mesh(add.move(M, [x, 0, 0]))
    w = add.text_width(name, 0.5)
    add.cuboid([x, 0.1, 2.3], [w + 0.5, 0.2, 0.9], add.PALETTE["n"])   # a name plate that fits
    add.text(name, [x - w / 2, 0.21, 2.6], 0.5, color="white", k=5, u=[1, 0, 0], v=[0, 0, -1])
    add.cuboid([x, -0.15, 0], [GAP - 0.2, 0.3, 4.6], add.shade(names[(3 * i) % len(names)], 0.9))

# the old string pair representation still works: as_mesh converts it back
old_style = [add.scene()[0], add.scene()[1]]              # ["x y z", ...], ["n i j k r g b", ...]
print("scene as strings:", len(old_style[0]), "vertices,", len(old_style[1]), "faces")
same = add.as_mesh(old_style)
print("as_mesh gives", same)

add.check()
add.save("cross_sections.off")

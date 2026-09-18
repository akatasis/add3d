

# ============================================================================
# 23. add.py 1.2 names
# ============================================================================
# Everything below exists so that models written for earlier versions of the
# course keep running unchanged.  New code should prefer the names on the
# right-hand side, which say what the shape is instead of numbering it.

def newface(A, RGB):
    """add.py 1.2 name for :func:`polygon`."""
    polygon(A, RGB)


def cube(c, e, RGB):
    """add.py 1.2 name for :func:`box`."""
    box(c, e, RGB)


def rectangle3D(c, e, RGB):
    """add.py 1.2 name for :func:`cuboid`."""
    cuboid(c, e, RGB)


def cube2(c, e, b, RGB):
    """add.py 1.2 name for :func:`frame` (a hollow cube of bars)."""
    frame(c, e, b, RGB)


def cylinder2(A, B, r, k, RGB):
    """add.py 1.2 name for :func:`tube` (a cylinder with no lids)."""
    tube(A, B, r, k, RGB)


def cylinder3(A, B, r, k, RGB):
    """add.py 1.2 name for :func:`cup` (a cylinder closed at ``A``)."""
    cup(A, B, r, k, RGB)


def cone2(A, B, r, k, RGB):
    """add.py 1.2 name for :func:`cone_open` (the slanted wall only)."""
    cone_open(A, B, r, k, RGB)


#: Other spellings people reach for.
ball = sphere
block = cuboid
cuboid3D = cuboid
lathe = revolve
solid_of_revolution = revolve
weld = clean
scale = zoom
translate = move
reflect = mirror


# ============================================================================
# 24. A one-line demonstration
# ============================================================================

def demo(path="demo.off"):
    """Build a small model that exercises most of the library.

    Run ``python add.py`` to produce ``demo.off`` and see the report.
    """
    clear()
    axes([0, 0, 0], 3.0)

    # A block with a hole drilled through it, cut out with a boolean.
    cuboid([0, -1.2, 0], [4, 0.6, 4], "brown")
    plate = layer()
    cylinder([0, -2, 0], [0, 0, 0], 0.9, 32, "brown")
    drill = layer()
    mesh(difference(plate, drill))

    # A twisted, tapering star column: copy + rotate + stretch a cross-section.
    star = []
    for i in range(12):
        a = 2 * math.pi * i / 12
        r = 0.6 if i % 2 else 0.28
        star.append([math.cos(a) * r, math.sin(a) * r])
    extrude(star, [0, 3.2, 0], "gold", steps=60, twist=math.pi,
            scale=lambda t: 1.0 - 0.55 * t, center=(0, -0.9, 0))

    # A surface of revolution and a parametric surface.
    revolve(lambda t: [0.7 + 0.25 * math.sin(4 * t), t], [2.4, -0.9, 0],
            [2.4, 0.1, 0], 0, 2.6, 60, 40, "teal")

    def shell(u, v):
        return [(1.2 + 0.45 * math.cos(u)) * math.cos(v) - 2.6,
                0.45 * math.sin(u) + 0.6,
                (1.2 + 0.45 * math.cos(u)) * math.sin(v)]
    parametric(shell, 0, 2 * math.pi, 40, 0, 2 * math.pi, 80, "sky",
               wrap_u=True, wrap_v=True)

    # A rainbow of spheres on a ring.
    sphere([0, 0, 0], 0.22, 8, "white")
    bead = layer()
    mesh(color_by(array_radial(move(bead, [2.2, 1.9, 0]), 24),
                  lambda p: hsv(math.atan2(p[2], p[0]) / (2 * math.pi))))

    check()
    return save(path)


if __name__ == "__main__":
    print("add.py %s" % __version__)
    print("written to %s" % demo())


# ============================================================================
#  Public names
# ============================================================================

# The names that came in from ``math`` and ``random`` stay usable as
# ``add.sin`` and friends but are not part of add.py's own vocabulary.
_REEXPORTED = set(dir(math)) | set(dir(_random)) | {"math"}

__all__ = sorted(name for name, value in list(globals().items())
                 if not name.startswith("_")
                 and name not in _REEXPORTED
                 and (callable(value) or name in ("vertices", "faces",
                                                  "COLORS", "PALETTE", "EPS",
                                                  "DEFAULT_COLOR",
                                                  "BOOL_EPS")))

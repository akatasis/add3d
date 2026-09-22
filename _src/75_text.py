

# ============================================================================
# 26. Letters and labels
# ============================================================================
# A small stroke font: every character is a few polylines on a grid that is
# 4 units wide and 6 units tall (Y up).  ``text`` draws them as round bars,
# so a model can carry its own title, a scale or a name plate.

_FONT = {
    "A": (4, [[(0, 0), (0, 4), (2, 6), (4, 4), (4, 0)], [(0, 2), (4, 2)]]),
    "B": (4, [[(0, 0), (0, 6), (3, 6), (4, 5), (4, 4), (3, 3), (0, 3)],
              [(3, 3), (4, 2), (4, 1), (3, 0), (0, 0)]]),
    "C": (4, [[(4, 5), (3, 6), (1, 6), (0, 5), (0, 1), (1, 0), (3, 0), (4, 1)]]),
    "D": (4, [[(0, 0), (0, 6), (3, 6), (4, 5), (4, 1), (3, 0), (0, 0)]]),
    "E": (4, [[(4, 6), (0, 6), (0, 0), (4, 0)], [(0, 3), (3, 3)]]),
    "F": (4, [[(4, 6), (0, 6), (0, 0)], [(0, 3), (3, 3)]]),
    "G": (4, [[(4, 5), (3, 6), (1, 6), (0, 5), (0, 1), (1, 0), (3, 0), (4, 1),
               (4, 3), (2, 3)]]),
    "H": (4, [[(0, 0), (0, 6)], [(4, 0), (4, 6)], [(0, 3), (4, 3)]]),
    "I": (2, [[(0, 6), (2, 6)], [(1, 6), (1, 0)], [(0, 0), (2, 0)]]),
    "J": (4, [[(4, 6), (4, 1), (3, 0), (1, 0), (0, 1)]]),
    "K": (4, [[(0, 0), (0, 6)], [(4, 6), (0, 2)], [(1.3, 3), (4, 0)]]),
    "L": (4, [[(0, 6), (0, 0), (4, 0)]]),
    "M": (4, [[(0, 0), (0, 6), (2, 3), (4, 6), (4, 0)]]),
    "N": (4, [[(0, 0), (0, 6), (4, 0), (4, 6)]]),
    "O": (4, [[(1, 0), (0, 1), (0, 5), (1, 6), (3, 6), (4, 5), (4, 1), (3, 0), (1, 0)]]),
    "P": (4, [[(0, 0), (0, 6), (3, 6), (4, 5), (4, 4), (3, 3), (0, 3)]]),
    "Q": (4, [[(1, 0), (0, 1), (0, 5), (1, 6), (3, 6), (4, 5), (4, 1), (3, 0), (1, 0)],
              [(2.5, 1.5), (4.3, -0.3)]]),
    "R": (4, [[(0, 0), (0, 6), (3, 6), (4, 5), (4, 4), (3, 3), (0, 3)], [(2, 3), (4, 0)]]),
    "S": (4, [[(4, 5), (3, 6), (1, 6), (0, 5), (0, 4), (1, 3), (3, 3), (4, 2),
               (4, 1), (3, 0), (1, 0), (0, 1)]]),
    "T": (4, [[(0, 6), (4, 6)], [(2, 6), (2, 0)]]),
    "U": (4, [[(0, 6), (0, 1), (1, 0), (3, 0), (4, 1), (4, 6)]]),
    "V": (4, [[(0, 6), (2, 0), (4, 6)]]),
    "W": (4, [[(0, 6), (1, 0), (2, 4), (3, 0), (4, 6)]]),
    "X": (4, [[(0, 0), (4, 6)], [(0, 6), (4, 0)]]),
    "Y": (4, [[(0, 6), (2, 3), (4, 6)], [(2, 3), (2, 0)]]),
    "Z": (4, [[(0, 6), (4, 6), (0, 0), (4, 0)]]),
    "0": (4, [[(1, 0), (0, 1), (0, 5), (1, 6), (3, 6), (4, 5), (4, 1), (3, 0), (1, 0)],
              [(0.6, 1), (3.4, 5)]]),
    "1": (4, [[(0.5, 4.5), (2, 6), (2, 0)], [(0.5, 0), (3.5, 0)]]),
    "2": (4, [[(0, 5), (1, 6), (3, 6), (4, 5), (4, 4), (0, 0), (4, 0)]]),
    "3": (4, [[(0, 6), (4, 6), (2, 3.5), (3, 3.5), (4, 2.5), (4, 1), (3, 0), (1, 0), (0, 1)]]),
    "4": (4, [[(3, 0), (3, 6), (0, 2), (4, 2)]]),
    "5": (4, [[(4, 6), (0, 6), (0, 3), (3, 3), (4, 2), (4, 1), (3, 0), (1, 0), (0, 1)]]),
    "6": (4, [[(4, 5), (3, 6), (1, 6), (0, 5), (0, 1), (1, 0), (3, 0), (4, 1), (4, 2),
               (3, 3), (0, 3)]]),
    "7": (4, [[(0, 6), (4, 6), (1.5, 0)]]),
    "8": (4, [[(1, 3), (0, 4), (0, 5), (1, 6), (3, 6), (4, 5), (4, 4), (3, 3), (1, 3),
               (0, 2), (0, 1), (1, 0), (3, 0), (4, 1), (4, 2), (3, 3)]]),
    "9": (4, [[(4, 3), (1, 3), (0, 4), (0, 5), (1, 6), (3, 6), (4, 5), (4, 1), (3, 0),
               (1, 0), (0, 1)]]),
    " ": (2, []),
    ".": (1, [[(0.5, 0), (0.5, 0.3)]]),
    ",": (1, [[(0.6, 0.5), (0.3, -0.8)]]),
    ":": (1, [[(0.5, 1), (0.5, 1.3)], [(0.5, 4), (0.5, 4.3)]]),
    ";": (1, [[(0.6, 1), (0.3, -0.5)], [(0.5, 4), (0.5, 4.3)]]),
    "!": (1, [[(0.5, 6), (0.5, 2)], [(0.5, 0), (0.5, 0.3)]]),
    "?": (4, [[(0, 5), (1, 6), (3, 6), (4, 5), (4, 4), (2, 2.5), (2, 1.8)], [(2, 0), (2, 0.3)]]),
    "-": (4, [[(0.5, 3), (3.5, 3)]]),
    "+": (4, [[(0.5, 3), (3.5, 3)], [(2, 1.5), (2, 4.5)]]),
    "=": (4, [[(0.5, 2), (3.5, 2)], [(0.5, 4), (3.5, 4)]]),
    "*": (4, [[(0.5, 1.5), (3.5, 4.5)], [(0.5, 4.5), (3.5, 1.5)], [(2, 1), (2, 5)]]),
    "/": (4, [[(0, 0), (4, 6)]]),
    "\\": (4, [[(0, 6), (4, 0)]]),
    "(": (2, [[(1.5, 6.5), (0.4, 5), (0.4, 1), (1.5, -0.5)]]),
    ")": (2, [[(0.5, 6.5), (1.6, 5), (1.6, 1), (0.5, -0.5)]]),
    "[": (2, [[(1.6, 6.5), (0.4, 6.5), (0.4, -0.5), (1.6, -0.5)]]),
    "]": (2, [[(0.4, 6.5), (1.6, 6.5), (1.6, -0.5), (0.4, -0.5)]]),
    "'": (1, [[(0.5, 6), (0.5, 4.5)]]),
    '"': (2, [[(0.4, 6), (0.4, 4.5)], [(1.6, 6), (1.6, 4.5)]]),
    "_": (4, [[(0, -0.5), (4, -0.5)]]),
    "%": (4, [[(0, 0), (4, 6)], [(0, 4.5), (0, 6), (1.5, 6), (1.5, 4.5), (0, 4.5)],
              [(2.5, 0), (2.5, 1.5), (4, 1.5), (4, 0), (2.5, 0)]]),
    "#": (4, [[(1, 0), (1.5, 6)], [(2.5, 0), (3, 6)], [(0, 2), (4, 2)], [(0, 4), (4, 4)]]),
    "<": (4, [[(4, 6), (0, 3), (4, 0)]]),
    ">": (4, [[(0, 6), (4, 3), (0, 0)]]),
    "^": (4, [[(0.5, 4), (2, 6), (3.5, 4)]]),
    "&": (4, [[(4, 0), (1, 3.5), (1, 5), (2, 6), (3, 5), (3, 4), (0, 1.5), (1, 0), (2, 0), (4, 2.5)]]),
    "@": (4, [[(3, 2), (3, 4), (1.5, 4), (1.5, 2), (3.3, 2), (4, 3), (4, 5), (3, 6), (1, 6),
               (0, 5), (0, 1), (1, 0), (3.5, 0)]]),
    "$": (4, [[(4, 5), (3, 6), (1, 6), (0, 5), (0, 4), (1, 3), (3, 3), (4, 2), (4, 1),
               (3, 0), (1, 0), (0, 1)], [(2, -0.5), (2, 6.5)]]),
    "|": (1, [[(0.5, -0.5), (0.5, 6.5)]]),
}

#: Accents for the Lithuanian letters, drawn on top of the base letter.
_ACCENTS = {
    "caron": [[(1, 8), (2, 7), (3, 8)]],                     # Č Š Ž
    "dot": [[(2, 7.3), (2, 7.6)]],                           # Ė
    "macron": [[(1, 7.5), (3, 7.5)]],                        # Ū
    "ogonek": [[(4, 0), (3.6, -0.8), (4.5, -1.1)]],           # Ą Ę Į Ų
}

#: Lithuanian and some other accented letters: (base letter, accent).
_LETTERS = {
    "Ą": ("A", "ogonek"), "Č": ("C", "caron"), "Ę": ("E", "ogonek"),
    "Ė": ("E", "dot"), "Į": ("I", "ogonek"), "Š": ("S", "caron"),
    "Ų": ("U", "ogonek"), "Ū": ("U", "macron"), "Ž": ("Z", "caron"),
    "Ä": ("A", "dot"), "Ö": ("O", "dot"), "Ü": ("U", "dot"),
    "Ā": ("A", "macron"), "Ē": ("E", "macron"), "Ī": ("I", "macron"),
    "Ō": ("O", "macron"), "Ň": ("N", "caron"), "Ř": ("R", "caron"),
    "Ě": ("E", "caron"), "Ď": ("D", "caron"), "Ť": ("T", "caron"),
}


def _strokes(ch):
    """``(advance width, [polyline, ...])`` for one character."""
    ch = ch.upper()
    if ch in _FONT:
        return _FONT[ch]
    if ch in _LETTERS:
        base, accent = _LETTERS[ch]
        width, lines = _FONT[base]
        extra = _ACCENTS[accent]
        if accent == "ogonek" and width < 4:      # hook under a narrow letter
            extra = [[(x - (4 - width), y) for x, y in line] for line in extra]
        return width, lines + extra
    return 4, [[(0, 0), (4, 0), (4, 6), (0, 6), (0, 0)]]   # unknown: a box


def text_width(string, size=1.0, spacing=1.0):
    """The width a line of :func:`text` will take up, in model units."""
    unit = size / 6.0
    total = 0.0
    for ch in string:
        w, _ = _strokes(ch)
        total += (w + 1.5 * spacing) * unit
    return max(0.0, total - 1.5 * spacing * unit)


def text(string, at=(0, 0, 0), size=1.0, thickness=None, color=None,
         u=(1, 0, 0), v=(0, 1, 0), align="left", spacing=1.0, k=8):
    """Write a label into the scene as round bars.

    ``size`` is the height of a capital letter, ``at`` the bottom-left
    corner of the text (or bottom-centre / bottom-right with ``align``).
    ``u`` is the writing direction and ``v`` the up direction, so a label
    can lie flat on the ground with ``u=[1, 0, 0], v=[0, 0, -1]`` or stand
    on a wall.  Letters, digits, punctuation and the Lithuanian letters
    ĄČĘĖĮŠŲŪŽ are available; lower-case letters are drawn as capitals.
    ``\\n`` starts a new line.  Returns the width of the widest line::

        add.text("LABAS 2026", [0, 0, 0], 1.0, color="navy")
    """
    if isinstance(at, dict):
        raise TypeError("text(string, font, ...) with loaded letters is now "
                        "typeset(string, font, ...)")
    unit = size / 6.0
    r = thickness if thickness is not None else 0.45 * unit
    u, v = _unit(u), _unit(v)
    lines = string.split("\n")
    widest = 0.0
    for row, line in enumerate(lines):
        width = text_width(line, size, spacing)
        widest = max(widest, width)
        if align == "center":
            start = -width / 2.0
        elif align == "right":
            start = -width
        else:
            start = 0.0
        y_off = -row * 1.6 * size
        x = start
        for ch in line:
            w, strokes = _strokes(ch)
            for line_pts in strokes:
                pts = []
                for (gx, gy) in line_pts:
                    px, py = x + gx * unit, y_off + gy * unit
                    pts.append((at[0] + u[0] * px + v[0] * py,
                                at[1] + u[1] * px + v[1] * py,
                                at[2] + u[2] * px + v[2] * py))
                for i in range(len(pts) - 1):
                    if distance(pts[i], pts[i + 1]) > EPS:
                        cylinder(pts[i], pts[i + 1], r, k, color)
                for p in pts:
                    sphere(p, r, 2, color)
            x += (w + 1.5 * spacing) * unit
    return widest


#: ``add.write`` is another name for :func:`text`.
write = text
#: ``add.label`` is another name for :func:`text`.
label = text


def glyph(letter, origin, u, v, size=1.0, thickness=0.04, color=None):
    """Draw one character as thin bars in the ``u``/``v`` plane
    (used by :func:`axes`; :func:`text` is the general version)."""
    text(letter, origin, size, thickness, color, u, v)

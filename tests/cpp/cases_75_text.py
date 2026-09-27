from parity_case import add, case, record, run, save_case, save_mesh  # noqa: F401

# Every character of the font, and some it does not have (drawn as a box).  The .txt files
# only get numbers: a character is written as its code point.
ALL = ("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "0123456789", " .,:;!?-+=*/\\()[]'\"_%#<>^&@$|",
       "ĄČĘĖĮŠŲŪŽ", "ąčęėįšųūž", "ÄÖÜĀĒĪŌŇŘĚĎŤ", "äöüāēīōňřěďť", "abcdefghijklmnopqrstuvwxyz", "ıſ")
EXTRA = ("ß~{}`€\t\r", "ÿÅåẞ😀", "é")


@case
def font_tables():
    for s in ALL + EXTRA:
        for ch in s:
            w, lines = add._strokes(ch)
            record(ord(ch))
            record(float(w))
            record(len(lines))
            for line in lines:
                record([[float(x), float(y)] for x, y in line])


@case
def upper_map():
    # Every character whose upper case the font has, and that upper case.
    keys = set(add._FONT) | set(add._LETTERS)
    for cp in range(0x110000):
        u = chr(cp).upper()
        if u in keys:
            record("%d %d" % (cp, ord(u)))


@case
def text_widths():
    for s in ("", "A", "I", " ", "AB", "LABAS 2026", "Hello, World!", "ĄČĘĖĮŠŲŪŽ", "ąčę", "a\nb", "€", "iiii",
              "...", "é", "ıſ", "ß"):
        record(add.text_width(s))
        record(add.text_width(s, 2.5))
        record(add.text_width(s, 0.5, 0.0))
        record(add.text_width(s, 1.0, -3.0))
        record(add.text_width(s, -1.0, 2.0))


@case
def text_capitals():
    record(add.text("ABCDEFGHIJKLM", [0, 0, 0]))
    record(add.text("NOPQRSTUVWXYZ", [0, -1.6, 0]))
    save_case()


@case
def text_digits_punctuation():
    record(add.text("0123456789", [0, 0, 0], 0.8, None, "red"))
    record(add.text(" .,:;!?-+=*/\\()[]'\"_%#<>^&@$|", [0, 2, 0], 0.8, None, "blue"))
    save_case()


@case
def text_lithuanian():
    record(add.text("ĄČĘĖĮŠŲŪŽ\nąčęėįšųūž", [0, 0, 0], 1.0, None, "gold"))
    record(add.text("Ąžuolas, Šilutė, Įstrigęs ŪKININKAS", [0, -4, 0], 0.5, 0.03, "green"))
    save_case()


@case
def text_other_accents():
    record(add.text("ÄÖÜĀĒĪŌŇŘĚĎŤ\näöüāēīōňřěďť", [0, 0, 0], 0.7, None, "teal"))
    save_case()


@case
def text_lower_and_unknown():
    record(add.text("abcdefghijklm\nnopqrstuvwxyz", [0, 0, 0], 0.6))
    record(add.text("ıſ ß~{}`€ ÿÅåẞ😀 é\tX\r", [0, -3, 0], 0.6, None, "red"))
    save_case()


@case
def text_options():
    record(add.text("LABAS 2026", [0, 0, 0], 1.0, None, "navy"))
    record(add.text("Center\nof it all", [0, 3, 0], 0.8, 0.05, "red", align="center"))
    record(add.text("RIGHT\nALIGNED\n", [0, 6, 0], 0.5, None, "blue", (1, 0, 0), (0, 1, 0), "right"))
    record(add.text("flat", [0, 0, 5], 1.0, 0.03, "gold", (1, 0, 0), (0, 0, -1)))
    record(add.text("tilted", [3, 0, 5], 1.2, None, None, (1, 1, 0), (0, 0, 1), "left", 0.5, 4))
    record(add.text("wide", [0, 9, 0], 1.0, None, "teal", (2, 0, 0), (0, 3, 0), "left", 2.5, 3))
    record(add.text("", [0, 12, 0]))
    record(add.text("\n\n", [0, 12, 0]))
    record(add.text("x", [0, 13, 0], 1.0, None, None, (0, 0, 0), (0, 1, 0)))       # u = 0: the letter squashed
    record(add.text("neg", [0, 15, 0], -1.0, None, "pink"))
    record(add.text("K!", [5, 15, 0], 2.0, 0.0, "brown", (0, 1, 0), (-1, 0, 0), "middle", 1.0, 5))
    record(add.text("thin", [0, 18, 0], 1.0, None, (0.1, 0.9, 0.4), (1, 0, 0), (0, 1, 0), "center", 0.0, 1))
    save_case()


@case
def text_aliases():
    record(add.write("WRITE", [0, 0, 0], 0.7, 0.04, "red"))
    record(add.label("Label", [0, 2, 0], 0.7, None, "blue", (0, 0, 1), (0, 1, 0), "center", 1.2, 6))
    add.glyph("G", [0, 4, 0], (1, 0, 0), (0, 1, 0))
    add.glyph("Ž", [2, 4, 0], (0, 0, 1), (0, 1, 0), 0.8, 0.05, "gold")
    add.glyph("?", [4, 4, 0], (1, 0, 0), (0, 0, 1), 1.5, 0.1, (10, 200, 30))
    add.glyph("", [6, 4, 0], (1, 0, 0), (0, 1, 0))
    add.glyph("AB", [6, 4, 0], (1, 0, 0), (0, 1, 0), 0.5)
    add.glyph("į", [9, 4, 0], (1, 0, 0), (0, 1, 0), 1.0, 0.02)
    save_case()


if __name__ == "__main__":
    import sys
    run(sys.argv)

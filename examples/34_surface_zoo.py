"""
34 -- the surface zoo: every named surface in add.py's catalogue.

``add.surface(name, ...)`` draws one of twenty-five classical parametric
surfaces (the collection at drhuang.com): Klein bottle, Dini, Enneper,
Boy-style owls and snails, tori with a twist ...  Here they all stand in a
5 x 5 grid, each scaled to the same size and labelled, so that you can pick
the one you want to build on.  Open sheets are given a little ``thickness``
so that every piece is a closed solid.

The colouring uses two shades per surface -- 50 colours in all, which is
exactly what an .obj for Sketchfab may have (one material per colour).

Parameter: ``STRIPES`` (how many stripes each surface gets).
"""
import add

STRIPES = 8
SIZE = 3.0                                    # every surface fits a 3 x 3 x 3 box
STEP = 4.2                                    # distance between neighbours
names = add.surface_names()                   # 25 names, alphabetically
print(len(names), "surfaces:", ", ".join(names))

for index, name in enumerate(names):
    row, col = divmod(index, 5)
    at = [(col - 2) * STEP, 0, (row - 2) * STEP]
    base = add.hsv(index / float(len(names)), 0.75, 0.95)
    dark = add.shade(base, 0.6)
    info = add.SURFACES[name]
    (u0, u1) = info["u"]

    def stripes(u, v, u0=u0, u1=u1, base=base, dark=dark):
        return base if int((u - u0) / (u1 - u0) * STRIPES) % 2 == 0 else dark

    closed = info["wrap"] == (True, True)
    add.surface(name, at, SIZE, color=stripes,
                thickness=0.0 if closed else 0.06)
    # a name plate lying flat in front of the surface (one word per line)
    label = name.replace("_", "\n").upper()
    add.text(label, [at[0], -SIZE / 2, at[2] + SIZE / 2 + 0.45], 0.3,
             color=dark, k=5, u=[1, 0, 0], v=[0, 0, -1], align="center")

add.check()
add.save("surface_zoo.off")

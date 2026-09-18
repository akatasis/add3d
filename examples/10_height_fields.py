"""
10 -- graphs of two-variable functions, y = f(x, z).

The gentlest way into parametric surfaces: keep x and z as they are and let
the function decide the height.  ``add.grid`` does exactly this, and
``add.parametric`` does it when you write ``[u, f(u, v), v]``.
"""
import add

CELL = 3.6
R = 3.2                       # each patch covers -R .. R in x and z
shown = []


def show(name, f, col, detail=90, thickness=0.06):
    add.parametric(lambda u, v: [u, f(u, v), v], -R, R, detail, -R, R, detail,
                   col, thickness=thickness)
    shown.append((name, add.place(add.fit(add.layer(), 2.6), (0, 0, 0))))


show("sin(x) + cos(z)", lambda x, z: add.sin(x) + add.cos(z), "red")
show("sin(x) * cos(z)", lambda x, z: add.sin(x) * add.cos(z), "orange")
show("ripple", lambda x, z: add.sin(3 * add.sqrt(x * x + z * z))
     / (1 + x * x + z * z) * 4, "gold")
show("saddle x^2 - z^2", lambda x, z: (x * x - z * z) / 4.0, "lime")
show("monkey saddle", lambda x, z: (x ** 3 - 3 * x * z * z) / 8.0, "teal")
show("gaussian hill", lambda x, z: 3 * add.exp(-(x * x + z * z) / 3.0), "sky")
show("peaks", lambda x, z:
     3 * (1 - x) ** 2 * add.exp(-x * x - (z + 1) ** 2) / 3
     - 10 * (x / 5 - x ** 3 - z ** 5) * add.exp(-x * x - z * z) / 3
     - add.exp(-(x + 1) ** 2 - z * z) / 9, "navy")
show("sombrero", lambda x, z: 3 * add.sin(add.sqrt(x * x + z * z) + 1e-9)
     / (add.sqrt(x * x + z * z) + 1e-9), "purple")
show("checkerboard", lambda x, z: 0.8 * (1 if (int(add.floor(x)) +
                                               int(add.floor(z))) % 2 else -1),
     "magenta", detail=64, thickness=0.1)
show("|x| + |z| cone", lambda x, z: -(abs(x) + abs(z)) / 2.0, "brown")
show("interference", lambda x, z:
     (add.sin(4 * add.sqrt((x - 1.2) ** 2 + z * z))
      + add.sin(4 * add.sqrt((x + 1.2) ** 2 + z * z))), "silver")
show("plateau", lambda x, z: 2.0 / (1 + add.exp(-4 * (2.0 - add.sqrt(
    x * x + z * z)))), "pink")

columns = 4
for i, (name, M) in enumerate(shown):
    add.mesh(add.move(M, [(i % columns) * CELL, 0, (i // columns) * CELL]))
    print("%2d. %s" % (i + 1, name))

add.check()
add.save("height_fields.off")

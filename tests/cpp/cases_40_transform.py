"""Parity cases for _src/40_transform.py: measuring, moving and reshaping
meshes, colouring them, patterns of copies (see cases_40_transform.cpp)."""
import math

from parity_case import _current, add, case, record, run, save_case, save_mesh  # noqa: F401

SIX = ["red", (10, 200, 30), add.transparent("sky", 0.4), "#123456", (250, 250, 5), "navy"]


def save_obj(M, tag):
    """The mesh exactly as it is, as .obj + .mtl (keeps texture coordinates)."""
    add.obj(_current[0] + "_" + tag + ".obj", M)


def record_palette(pal):
    record(len(pal))
    for c, n in pal:
        record(c)
        record(n)


def cube(lo=(-0.5, -0.25, -0.75), hi=(0.5, 0.75, 1.25), colors=None):
    M = add.Mesh()
    for k in range(8):
        M.add_vertex([hi[0] if k & 1 else lo[0], hi[1] if k & 2 else lo[1], hi[2] if k & 4 else lo[2]])
    for i, f in enumerate([[0, 4, 6, 2], [1, 3, 7, 5], [0, 1, 5, 4], [2, 6, 7, 3], [0, 2, 3, 1], [4, 5, 7, 6]]):
        M.add_face(f, colors[i] if colors else None)
    return M


def patch(nx=4, nz=3):
    """An open, bumpy sheet of quads, one colour each."""
    M = add.Mesh()
    for i in range(nx + 1):
        for j in range(nz + 1):
            x = -1.0 + 2.0 * i / nx
            z = -0.7 + 1.9 * j / nz
            M.add_vertex([x, 0.3 * math.sin(2 * x + z) + 0.1 * x * z, z])
    for i in range(nx):
        for j in range(nz):
            a = i * (nz + 1) + j
            M.add_face([a, a + 1, a + nz + 2, a + nz + 1], add.hsv((i * nz + j) / float(nx * nz)))
    return M


def triangles(colors):
    """One small triangle per colour."""
    M = add.Mesh()
    for i, c in enumerate(colors):
        M.add_polygon([[i, 0, 0], [i + 1, 0, 0], [i, 1, 0.5 * i]], c)
    return M


@case
def t_measure():
    for M in (cube(), patch(), triangles(SIX), add.Mesh()):
        record(add.bbox(M))
        record(add.size(M))
        record(add.center(M))
        record(add.middle(M))
        record(add.area(M))
        record(add.volume(M))
    add.mesh(cube(hi=(2, 3, 4)))
    record(add.bbox())
    record(add.size())
    record(add.center())
    record(add.middle())
    record(add.area())
    record(add.volume())
    save_case()


@case
def t_moves():
    M = cube(colors=SIX)
    save_mesh(add.move(M, [1, -2, 0.5]), "move")
    save_mesh(add.place(M, [3, 1, -1]), "place_bbox")
    save_mesh(add.place(patch(), [3, 1, -1], False), "place_center")
    save_mesh(add.rotateX(M, 0.7), "rx")
    save_mesh(add.rotateY(M, -1.1, [1, 2, 3]), "ry")
    save_mesh(add.rotateZ(M, 2.5, [0.5, 0, -1]), "rz")
    save_mesh(add.rotate(M, [1, 1, 0], math.pi / 3, [0, 1, 0]), "rot")
    save_mesh(add.rotate(M, [0, 0, 0], 1.0), "rot_zero_axis")
    save_mesh(add.zoom(M, 1.5), "zoom")
    save_mesh(add.zoom(patch(), -0.5, [1, 1, 1]), "zoom_neg")
    save_mesh(add.stretch(M, [1, 2, -1]), "stretch_flip")
    save_mesh(add.stretch(M, [0.5, 2, 3], [0, 0, 0]), "stretch")
    save_mesh(add.color(M, "gold"), "color")
    save_mesh(add.color(M, add.transparent("red", 0.3)), "color_t")


@case
def t_mapped_uv():
    T = add.texture(cube(colors=SIX), "w.png", "box")
    save_obj(T, "plain")
    save_obj(add.move(T, [1, 2, 3]), "move")
    save_obj(add.mirror(T), "mirror")
    save_obj(add.zoom(T, -1), "zoom_neg")
    save_obj(add.merge([T, cube()]), "merge")
    save_obj(add.array_linear(T, [2, 0, 0], 2), "linear")


@case
def t_fit():
    M = cube(colors=SIX)
    save_mesh(add.fit(M), "default")
    save_mesh(add.fit(M, 3.0, [1, 0, 0]), "about")
    save_mesh(add.fit(patch(), 0.5), "patch")
    P = add.Mesh()
    P.add_polygon([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
    save_mesh(add.fit(P, 2.0), "point")


@case
def t_mirror():
    M = cube(colors=SIX)
    save_mesh(add.mirror(M), "default")
    save_mesh(add.mirror(M, [0.3, 0, 0], [1, 2, -0.5]), "plane")
    save_mesh(add.mirror(patch(), [0, 0.1, 0], [0, 1, 0]), "patch")
    save_mesh(add.array_mirror(M, [1, 0, 0]), "array")
    save_mesh(add.array_mirror(patch(), [0, 0, 0], [0, 1, 1]), "array2")


@case
def t_transform():
    M = cube(colors=SIX)
    save_mesh(add.transform(M, [[1, 0.5, 0], [0, 1, 0], [0.2, 0, 2]]), "m3")
    save_mesh(add.transform(M, [[0, 1, 0], [1, 0, 0], [0, 0, 1]]), "swap")
    save_mesh(add.transform(M, [[0.5, 0, 0, 1], [0, 2, 0, -1], [0, 0, 1, 0.25], [0, 0, 0, 1]]), "m4")
    save_mesh(add.transform(patch(), [[-1, 0, 0, 3], [0, 1, 0, 0], [0, 0.3, 1, 0]]), "m34_flip")


@case
def t_deform():
    save_mesh(add.deform(patch(), lambda p: [p[0], p[1] + math.sin(3 * p[0]) * 0.2, p[2] * 1.5]), "wave")
    save_mesh(add.deform(cube(colors=SIX), lambda p: [p[0] * (1 + p[1]), p[1], p[2] - p[0]]), "shear")


@case
def t_twist():
    M = cube(colors=SIX)
    save_mesh(add.twist(M, 0.8), "default")
    save_mesh(add.twist(M, -1.3, [1, 0, 1], [0.2, 0, 0]), "axis")
    save_mesh(add.twist(patch(), 2.0, [1, 0, 0]), "patch")


@case
def t_taper():
    M = cube(colors=SIX)
    save_mesh(add.taper(M, -0.2), "default")
    save_mesh(add.taper(M, 0.5, 0, [0.1, 0, 0]), "x")
    save_mesh(add.taper(M, 0.3, 2), "z")
    save_mesh(add.taper(M, 0.3, -1, [0, 0, 0.5]), "neg")
    save_mesh(add.taper(patch(), 0.7, 2, [0, 1, -1]), "patch")


@case
def t_bend():
    P = patch()
    C = add.stretch(cube(colors=SIX), [0.5, 3, 0.5])
    save_mesh(add.bend(C, 0.4), "default")
    save_mesh(add.bend(P, 0.5, 0, 2, [0, -1, 0]), "x")
    save_mesh(add.bend(P, 1e-12), "tiny")
    save_mesh(add.bend(C, -0.3, 1, 2, [0.5, 0, 0]), "around_z")
    save_mesh(add.bend(C, 0.6, 1, 1), "same_axes")


@case
def t_jitter():
    M = cube(colors=SIX)
    save_mesh(add.jitter(M, 0.1, 42), "seed")
    save_mesh(add.jitter(M), "global")
    save_mesh(add.jitter(patch(), 0.2, 0), "seed0")
    record(add.random())


@case
def t_opacity():
    M = cube(colors=SIX)
    T = add.texture(M, "wood.png", "box")
    for a in (0.3, 1.0, 0.0, 128, -1, 0.1234, 2.0):
        record(add.opacity(M, a).C)
        record(add.opacity(T, a).C)
    save_mesh(add.opacity(M, 0.5), "half")
    save_obj(add.opacity(T, 0.25), "textured")


@case
def t_texture():
    M = cube(colors=SIX)
    P = patch()
    for mapping in ("box", "xy", "xz", "yz", "fit", "sphere", "cylinder"):
        T = add.texture(M, "img/bricks.png", mapping)
        record(T.UV)
        record(T.C)
        save_obj(T, mapping)
        T = add.texture(P, "tiles.jpg", mapping, 0.5, None, (0.25, -0.5))
        record(T.UV)
        record(T.C)
        save_obj(T, mapping + "_patch")
    T = add.texture(P, "tiles.jpg", "sphere", 3, "red")
    record(T.UV)
    save_obj(T, "sphere3")
    T = add.texture(M, "c.png", "cylinder", 0, add.transparent("sky", 0.2), (5, 5))
    record(T.UV)
    record(T.C)
    save_obj(T, "cyl0")
    T = add.texture(M, "a.png", lambda p, n: (p[0] + n[1], p[2] * 2))
    record(T.UV)
    save_obj(T, "custom")
    D = add.Mesh()
    D.add_polygon([[0, 0, 0], [1, -1, 0], [1, -1, 1], [0, 0, 1]])
    D.add_polygon([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    D.add_polygon([[0, 0, 2], [1, 1, 2], [2, 2, 2]])
    D.add_polygon([[0, 0, 0], [0, 1, 1], [0, 1, 2], [0, 0, 3]])
    for mapping in ("box", "sphere", "cylinder"):
        T = add.texture(D, "d.png", mapping, 1.5)
        record(T.UV)
        save_obj(T, "ties_" + mapping)
    T = add.texture(add.opacity(M, 0.5), "", "box", 2.0, None)
    record(T.C)
    try:
        add.texture(M, "a.png", "bogus")
    except ValueError:
        record("raised")


@case
def t_color_by():
    P = patch()
    save_mesh(add.color_by(P, lambda p: add.hsv(p[1] * 2.0 + p[0])), "hsv")
    save_mesh(add.color_by(P, lambda p: "red" if p[0] > 0 else (0.2, 0.4, 0.6)), "mixed")
    save_mesh(add.color_by(cube(), lambda p: add.transparent("blue", p[2] + 0.5)), "clear")


@case
def t_color_gradient():
    P = patch(8, 6)
    save_mesh(add.color_gradient(P, "red", "blue"), "y")
    save_mesh(add.color_gradient(P, "red", (0, 255, 0), 0), "x")
    save_mesh(add.color_gradient(P, "white", "black", -1), "neg")
    F = add.Mesh()
    F.add_polygon([[0, 0, 0], [1, 0, 0], [1, 0, 1]])
    save_mesh(add.color_gradient(F, add.transparent("red", 0.5), "blue"), "flat")


@case
def t_color_random():
    P = patch()
    save_mesh(add.color_random(P, 7), "seed")
    save_mesh(add.color_random(P), "global")
    save_mesh(add.color_random(cube(), -3), "negative_seed")
    record(add.randint(0, 1000))


@case
def t_palette():
    cs = [(0, 0, 0), (255, 0, 1), (254, 255, 255), "red",
          add.transparent("red", 0.5), add.transparent("red", 0.25),
          add.rgb((255, 0, 0, 0.5, "a.png")), add.rgb((255, 0, 0, 1.0, "b.png")),
          add.rgb((255, 0, 0, 1.0, "a.png"))]
    M = triangles(cs + list(reversed(cs)) + ["red", (0, 0, 0), "red"])
    record_palette(add.palette(M))
    record_palette(add.palette(add.Mesh()))
    add.mesh(M)
    add.mesh(triangles(["navy"] * 5))
    record_palette(add.palette())
    save_case()


@case
def t_limit_colors():
    P = add.color_random(patch(12, 10), 3)
    for n in (50, 10, 3, 2, 1, 0, -1, 120, 200):
        record_palette(add.palette(add.limit_colors(P, n)))
    G = add.color_gradient(patch(9, 7), "red", "blue", 0)
    G = add.merge([G, add.color_by(patch(5, 5), lambda p: (int(p[0] * 50) % 256, 100, 7)),
                   add.opacity(patch(2, 2), 0.5), add.texture(patch(1, 1), "t.png")])
    for n in (4, 3, 7):
        L = add.limit_colors(G, n)
        record_palette(add.palette(L))
        save_mesh(L, "g%d" % n)
    save_mesh(add.limit_colors(P, 5), "five")


@case
def t_arrays():
    M = cube(colors=SIX)
    save_mesh(add.repeat(M, 4, lambda X, i: add.move(add.rotateY(X, i * 0.3), [0, i * 0.2, 0])), "repeat")
    save_mesh(add.repeat(M, 0, lambda X, i: X), "repeat0")
    save_mesh(add.array_linear(M, [1.5, 0, 0.25], 3), "linear")
    save_mesh(add.array_grid(M, [2, 3, 0.5], [2, 3, 1]), "grid")
    save_mesh(add.array_grid(M, [2, 3, 0.5], [2, 0, 1]), "grid0")
    save_mesh(add.array_radial(M, 5), "radial")
    save_mesh(add.array_radial(M, 7, [0, 0, 1], [1, 0, 0], math.pi, 0.3), "spiral")
    save_mesh(add.array_radial(M, 0), "none")


@case
def t_random():
    """Random polygons in coarse random colours (many repeats and ties), some
    see-through or textured: palette, limit_colors, texture, measures."""
    for seed in range(12):
        r = add.Random(seed)
        M = add.Mesh()
        for i in range(r.randint(1, 60)):
            x = r.uniform(-2, 2)
            y = r.uniform(-2, 2)
            z = r.uniform(-2, 2)
            k = r.randint(3, 6)
            pts = []
            for j in range(k):
                a = 2 * math.pi * j / k
                pts.append([x + 0.3 * math.cos(a), y + 0.2 * math.sin(a), z + 0.1 * j])
            kind = r.randint(0, 9)
            if kind < 6:
                c = (r.randint(0, 8) * 30, r.randint(0, 8) * 30, r.randint(0, 8) * 30)
            elif kind < 8:
                c = add.transparent((r.randint(0, 255), 0, 0), r.random())
            else:
                c = add.rgb((0, r.randint(0, 255), 0, 1.0, "t%d.png" % r.randint(0, 2)))
            M.add_polygon(pts, c)
        record_palette(add.palette(M))
        for n in (1, 2, 5, 17):
            record_palette(add.palette(add.limit_colors(M, n)))
        for mapping in ("sphere", "cylinder", "box"):
            record(add.texture(M, "x.png", mapping, r.uniform(0.2, 3)).UV)
        record(add.bbox(M))
        record(add.area(M))
        record(add.center(M))


if __name__ == "__main__":
    import sys
    run(sys.argv)

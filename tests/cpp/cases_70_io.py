"""Parity cases for _src/70_io.py: the writers behind save / off / obj (.off .obj
.ply .stl), obj_size, the Stream, load (.off, .obj + .mtl, .ply), write_png,
load_font and typeset (see cases_70_io.cpp).

Every input file a case reads is written by the case itself, byte for byte the
same in both languages.  A PNG is compared by its decoded pixels, not by its
bytes: add.py compresses them with zlib, add.hpp stores them uncompressed (see
png_record)."""
import os
import shutil
import struct
import zlib

from parity_case import _current, add, case, record, run, save_case, save_mesh  # noqa: F401

NAN = float("nan")
INF = float("inf")


def outcome(fn, *args):
    """What fn(*args) does: "ok", or which kind of exception it raises (the C++ twin
    maps its exceptions onto the same kinds)."""
    try:
        fn(*args)
    except OSError:
        return "OSError"
    except LookupError:                   # IndexError, KeyError
        return "LookupError"
    except OverflowError:
        return "OverflowError"
    except ValueError:
        return "ValueError"
    return "ok"


def write_file(name, data):
    """A file with exactly these bytes."""
    with open(name, "wb") as f:
        f.write(data)


def show(s):
    """A string with every character outside printable ASCII written as <XXXX>."""
    return "".join(ch if " " <= ch <= "~" else "<%04X>" % ord(ch) for ch in s)


def save_obj(M, tag):
    """The mesh exactly as it is, as .obj + .mtl (faces of any size kept whole)."""
    add.obj(_current[0] + "_" + tag + ".obj", M)


def exact(M, tag):
    """The mesh exactly as it is, as .off and as .obj + .mtl."""
    save_mesh(M, tag)
    save_obj(M, tag)


def from_faces(V, F, colors=None):
    M = add.Mesh()
    for p in V:
        M.add_vertex(p)
    for i, f in enumerate(F):
        M.add_face(f, colors[i % len(colors)] if colors else None)
    return M


def counts(out):
    """What a stream has counted so far, and its materials in order."""
    record("faces %d vertices %d bytes %d removed %d cut %d"
           % (out.faces, out.vertices, out.bytes, out.removed, out.cut))
    record("materials: " + " ".join(out.materials.values()))


def model():
    """Two touching red boxes (the wall between them goes when tidied), a gold slab
    on them, a cylinder with 8-corner lids, a see-through box and a textured box."""
    add.push()
    add.box([0, 0, 0], 1, "red")
    add.box([1, 0, 0], 1, "red")
    add.cuboid([0.5, 1, 0], [2, 1, 0.5], "gold")
    add.cylinder([3, 0, 0], [3, 2, 0], 0.5, 8, (10, 200, 30))
    M = add.pop()
    glass = add.opacity(add.make(add.box, [0, 0, 3], 1, "sky"), 0.35)
    tex = add.texture(add.make(add.box, [3, 0, 3], 1, "white"), "img\\wood.png")
    return add.merge([M, glass, tex])


def odd_faces():
    """Faces an OFF file cannot carry as they are: a convex hexagon, an L (concave), a
    notched pentagon, a self-crossing outline, a pentagon with a corner in the middle of
    a side, a clockwise pentagon, a star; then a face pinched at a vertex, one using a
    NaN vertex and a plain triangle (no two of them in one plane)."""
    V = [[0, 0, 0], [2, 0, 0], [3, 1, 0], [2, 2, 0], [0, 2, 0], [-1, 1, 0],               # 0-5 hexagon
         [0, 0, 1], [2, 0, 1], [2, 1, 1], [1, 1, 1], [1, 2, 1], [0, 2, 1],                 # 6-11 L
         [4, 0, 2], [6, 0, 2], [6, 2, 2], [5, 0.5, 2], [4, 2, 2],                           # 12-16 notch
         [0, 0, 3], [2, 2, 3], [2, 0, 3], [0, 2, 3], [1, -1, 3], [1, 3, 3],                 # 17-22 crossing
         [0, 0, 4], [1, 0, 4], [2, 0, 4], [2, 2, 4], [0, 2, 4],                             # 23-27 T-junction
         [0, 0, 5], [0, 2, 5], [2, 2, 5], [3, 1, 5], [2, 0, 5],                             # 28-32 clockwise
         [NAN, 0, 0]]                                                                       # 33
    for i in range(10):
        r = 2.0 if i % 2 == 0 else 0.8
        a = 2 * add.pi * i / 10
        V.append([10 + r * add.cos(a), r * add.sin(a), 6])                                 # 34-43 star
    V += [[0, 0, 7], [1, 0, 7], [1, 1, 7], [-1, 0, 7], [-1, -1, 7],                        # 44-48 pinched
          [0, 0, 8], [1, 0, 8.5], [0, 1, 9]]                                                # 49-51 triangle
    F = [[0, 1, 2, 3, 4, 5], [6, 7, 8, 9, 10, 11], [12, 13, 14, 15, 16],
         [17, 18, 19, 20, 21, 22], [23, 24, 25, 26, 27], [28, 29, 30, 31, 32],
         list(range(34, 44)), [44, 45, 46, 44, 47, 48], [6, 7, 33], [49, 50, 51]]
    colors = ["red", (10, 200, 30), add.transparent("sky", 0.4), "#123456", "gold", "navy"]
    return from_faces(V, F, colors)



def tiny_faces():
    """Two clockwise pentagons too small for a normal of their own (below EPS): _off_pieces
    turns them round -- one by ear clipping (its corners count as straight), one convex."""
    V = [[0, 0, 10], [0, 1e-5, 10], [1e-5, 1e-5, 10], [1.5e-5, 0.5e-5, 10], [1e-5, 0, 10]]
    r = 1.449e-5
    for i in range(5):
        a = -2 * add.pi * i / 5
        V.append([r * add.cos(a), r * add.sin(a), 11])
    return from_faces(V, [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], ["red", "blue"])

# -- numbers, words, letters ---------------------------------------------------

@case
def rounded_numbers():
    xs = [0.0, -0.0, 10.0, 100.0, 1234.0, -0.5, -0.3, 0.3, 2.5, 3.5, 0.12345678, -2.00005, 1e-5, -1e-5,
          123.456, 1e20, -1e20, 5e-324, 1.0 / 3, -2.0 / 3, 0.5, 1.5, 99.99995, 0.05, NAN, -NAN, INF, -INF]
    for d in (0, 1, 2, 4, 6, 9, 17, 30):
        f = add._rounded(d)
        record(" ".join(f(x) for x in xs))
    record(outcome(lambda: add._rounded(-1)(1.0)))


@case
def upper_letters():
    for lo, hi in ((0, 0x180), (0x370, 0x530)):
        out = []
        for c in range(lo, hi):
            u = chr(c).upper()
            if u != chr(c):
                out.append("%04X:%s" % (c, ",".join("%04X" % ord(ch) for ch in u)))
        record(len(out))
        record(" ".join(out))
    record(show("labas, pasauli! \u0105\u017euolas \u00df \u03c3\u03bf\u03c6\u03af\u03b1 \u0451\u0436".upper()))


@case
def words_and_numbers():
    lines = ["  a b\tc  ", "a\x0bb\x0cc\x1cd\x1de\x1ef\x1fg\rh\ni", "x\u00a0y\u2003z\u3000w\u0085v\u2028u\u2029t\u202fs\u205fr\u1680q",
             "\u200bp\u200b", "", "   ", "one", "\u00e9t\u00e9 \u0105"]
    for s in lines:
        record(show("|".join(s.split())))
        record("[" + show(s.strip()) + "]")
    words = ["1_000", "1__0", "_1", "1_", "inf", "Infinity", "INFINITY", "iNf", "nan", "-nan", "+inf", "NaN", "1e400",
             "-1e400", "1e-400", "0x10", ".5", "5.", "1._5", "1_.5", "1e1_0", "1e_10", "1_e10", "in_f", ".", "e5",
             "1e", "1e+", "+.5e-3", "-.e1", "1.5E+3", "infinit", "nana", "+-1", "1.2.3", "00012", "0_0", "1.0_5",
             "1_0.5_5e1_2", "0.1", "2.5e-324", "1.7976931348623157e308", "1.8e308", "-0", "-0.0", "+7", "1.e5",
             "1\x00", "l", "--1", "9223372036854775807", "-9223372036854775808", "1,5", "+", "-", "", "12abc",
             "4.9406564584124654e-324", "0.30000000000000004", "123456789012345678901234567890.5", "1e-5", "1E5"]
    for w in words:
        try:
            f = repr(float(w))
        except ValueError:
            f = "ValueError"
        try:
            i = "%d" % int(w)
        except ValueError:
            i = "ValueError"
        record("%s float %s int %s" % (show(w), f, i))


# -- writers ---------------------------------------------------------------------

@case
def ply_writer():
    M = model()
    add.save(_current[0] + ".ply", M)
    add.save(_current[0] + "_raw.ply", M, clean=False)
    add.save(_current[0] + "_2.ply", M, colors=2)
    add.save(_current[0] + "_odd.ply", odd_faces(), clean=False)
    add.save(_current[0] + "_oddclean.ply", odd_faces())


@case
def stl_writer():
    M = model()
    add.save(_current[0] + ".stl", M)
    add.save(_current[0] + "_raw.stl", M, clean=False)
    add.save(_current[0] + "_odd.stl", odd_faces(), clean=False)
    # a huge triangle (its normal overflows: nan), a triangle without area, -0 coordinates
    big = from_faces([[0, 0, 0], [1e200, 0, 0], [0, 1e200, 0], [1, 1, 1], [2, 2, 2], [3, 3, 3],
                      [-0.0, -0.0, 1], [1, -0.0, 1], [0, 1, 1]],
                     [[0, 1, 2], [3, 4, 5], [6, 7, 8], [2, 1, 0]])
    add.save(_current[0] + "_big.stl", big, clean=False)


@case
def save_forms():
    M = model()
    add.box([0, 0, 0], 1, "red")
    add.box([0, 2, 0], 1, "blue")
    record(add.save(_current[0] + "_scene.off"))                # the scene -- then cleared
    record(len(add.scene().F))
    add.box([0, 0, 0], 1, (1, 2, 3))
    add.box([2, 0, 0], 1, (200, 2, 3))
    add.box([4, 0, 0], 1, (1, 200, 3))
    add.save(_current[0] + "_scene.obj", None, None, 2)          # limited to two colours
    record(len(add.scene().F))
    add.box([0, 0, 0], 1, "red")
    add.save(_current[0] + "_scene.ply", None, False)            # the scene, kept
    record(len(add.scene().F))
    add.save(_current[0] + "_m.ply", M, True)                    # another mesh, but the scene is cleared
    record(len(add.scene().F))
    add.box([0, 0, 0], 1, "red")
    add.save(_current[0] + "_m.stl", M)                         # a mesh: the scene stays
    record(len(add.scene().F))
    add.clear()
    record(add.save(_current[0] + "_noext", M))                 # no extension: .off
    add.save(_current[0] + "_upper.OBJ", M)                     # .OBJ: _upper.mtl
    add.save(_current[0] + "_upper.PLY", M)
    add.save(_current[0] + "_m_nc.off", M, clean=False)
    add.save(_current[0] + "_m_nc.obj", M, clean=False)
    add.save(_current[0] + "_m_3.off", M, colors=3)
    add.save(_current[0] + "_empty.obj", add.Mesh())
    add.save(_current[0] + "_empty.stl", add.Mesh())


@case
def off_obj_writers():
    M = model()
    record(add.off(_current[0] + "_exact.off", M))
    record(add.obj(_current[0] + "_exact.obj", M, _current[0] + "_custom.mtl"))
    record(add.obj(_current[0] + "_plain", M))                  # not .obj: _plain.mtl
    add.box([0, 0, 0], 1, "red")
    record(add.off(_current[0] + "_scene.off"))
    record(len(add.scene().F))
    add.box([0, 0, 0], 1, "red")
    record(add.obj(_current[0] + "_scene.obj"))
    record(len(add.scene().F))
    exact(odd_faces(), "odd")
    exact(tiny_faces(), "tiny")
    add.save(_current[0] + "_odd.off", odd_faces())             # tidied: the concave faces cut first


@case
def sizes_and_names():
    M = model()
    record(add.obj_size(M))
    record(outcome(add.obj_size, odd_faces()))                 # a NaN vertex: _num raises
    record(outcome(add.obj_size, from_faces([[INF, NAN, 0]], [])))   # inf first: OverflowError
    record(add.obj_size(add.clean(odd_faces())))
    record(add.obj_size(add.Mesh()))
    record(add.obj_size(add.texture(add.make(add.sphere, [0, 0, 0], 1, 8, "red"), "globe.png", "sphere", 2.0)))
    add.box([0, 0, 0], 1, "red")
    record(add.obj_size())
    add.clear()
    colors = ["red", add.transparent("sky", 0.35), (1, 2, 3, 0.9994), (255, 0, 0, 1.0, "my tex-1.png"),
              (0, 0, 0, 0.5, "dir\\sub/wood.grain.jpg"), (9, 9, 9, 1.0, "noext"), (9, 9, 9, 1.0, ".hidden"),
              (1, 2, 3, 0.25, "\u0105\u017euolas.png"), (16, 32, 48, 0.001)]
    for c in colors:
        record(add._material_name(add.rgb(c)))
    for name in ("img\\wood.png", "a/b/c.png", "plain.png", "dir/", ""):
        record("[" + name.replace("\\", "/").rsplit("/", 1)[-1] + "]")


@case
def empty_faces():
    M = from_faces([[0, 0, 0], [1, 0, 0], [1, 1, 0]], [[], [0], [0, 1], [0, 1, 2], [2, 1]],
                   ["red", "blue", "gold", (1, 2, 3), add.transparent("sky", 0.5)])
    save_mesh(M)
    save_obj(M, "exact")
    add.save(_current[0] + ".ply", M, clean=False)
    add.save(_current[0] + ".stl", M, clean=False)
    for ext in ("obj", "off"):
        out = add.stream("%s_stream.%s" % (_current[0], ext), False)
        record(out.add(M))
        out.close()
        counts(out)


# -- the Stream ------------------------------------------------------------------

@case
def stream_obj_parts():
    out = add.stream(_current[0] + ".obj")
    add.box([0, 0, 0], 1, "red")
    record(out.add())                                           # the scene, then cleared
    record(len(add.scene().F))
    record(out.add(add.make(add.box, [2, 0, 0], 1, "red")))     # the same colour: no new usemtl
    record(out.add(add.opacity(add.make(add.box, [4, 0, 0], 1, "sky"), 0.4)))
    record(out.add(add.texture(add.make(add.box, [6, 0, 0], 1), "img/wood.png")))
    record(out.add(add.texture(add.make(add.cuboid, [8, 0, 0], [1, 2, 1]), "img/wood.png")))   # vt numbers go on
    record(out.add(add.texture(add.make(add.box, [10, 0, 0], 1, "red"), "stone.jpg", "sphere", 2.0, None)))
    add.box([0, 5, 0], 1, "blue")
    record(out.add(None, False))                                # the scene again, not tidied
    record(len(add.scene().F))
    record(out.add(add.make(add.box, [0, 7, 0], 1, "red")))     # an old material comes back
    counts(out)
    record(out.close())
    counts(out)
    record(out.close())                                         # closing again does nothing


@case
def stream_obj_tidy():
    out = add.stream(_current[0] + ".obj")
    B = add.make(add.box, [0, 0, 0], 1, "red")
    record(out.add(add.merge([B, add.move(B, [1, 0, 0])])))     # the wall between two boxes
    counts(out)
    record(out.add(add.merge([add.make(add.box, [0, 3, 0], 2, "gold"),
                              add.make(add.box, [0.25, 4.5, 0], 1, "gold")])))   # a box standing on a box
    counts(out)
    record(out.add(add.merge([B, B])))                          # every face twice
    counts(out)
    record(out.add(add.merge([B, B]), False))                   # not tidied: all written
    counts(out)
    record(out.add(odd_faces()))
    counts(out)
    out.close()
    counts(out)


@case
def stream_obj_precision():
    M = from_faces([[0, 0, 0], [10, 0, 0], [100, 0.5, 0], [-0.5, 1.0 / 3, 2.5], [1e-5, -1e-5, 1234.5678]],
                   [[0, 1, 2], [0, 2, 3], [1, 4, 3]], ["red", "blue", (10, 20, 30)])
    for p in (4, 0, 2, 12):
        out = add.stream("%s_%d.obj" % (_current[0], p), False, p)
        record(out.add(M))
        record(out.add(add.move(M, [0.123456, -7.5, 1e6])))
        record(out.add(add.texture(add.make(add.box, [0, 0, 0], 1), "t.png", "sphere")))
        out.close()
        counts(out)
    out = add.stream(_current[0] + "_tidy.obj", True, 3)
    record(out.add(add.make(add.sphere, [0.1234, 0, 0], 1.0 / 3, 6, "green")))
    out.close()
    counts(out)
    out = add.stream(_current[0] + "_neg.obj", False, -1)
    record(outcome(out.add, M))                                 # "%.-1f": a ValueError
    out.close()
    counts(out)


@case
def stream_off_parts():
    name = _current[0] + ".off"
    out = add.stream(name)
    record(os.path.exists(name))
    add.cylinder([0, 0, 0], [0, 2, 0], 1, 8, "red")             # 8-corner lids: pieces
    record(out.add())
    record(len(add.scene().F))
    record(out.add(add.opacity(add.make(add.box, [3, 0, 0], 1, "sky"), 0.4)))
    record(out.add(odd_faces(), False))
    record(out.add(odd_faces()))
    record(out.add(tiny_faces(), False))
    add.box([0, 5, 0], 1, "blue")
    record(out.add(None, False))
    counts(out)
    record(os.path.exists(name + ".vertices~"))
    record(os.path.exists(name + ".faces~"))
    record(out.close())
    counts(out)
    record(os.path.exists(name + ".vertices~"))
    record(os.path.exists(name + ".faces~"))
    exact(add.load(name), "back")


@case
def stream_off_precision():
    out = add.stream(_current[0] + ".off", False, 3)
    record(out.add(add.make(add.sphere, [0.1234, 0, 0], 1.0 / 3, 6, "green")))
    B = add.make(add.box, [0, 0, 0], 1, "red")
    record(out.add(add.merge([B, B]), True))                    # tidied, as this part asks
    record(out.add(add.merge([B, add.move(B, [1e-7, 0, 0])])))
    counts(out)
    out.close()
    counts(out)
    out = add.stream(_current[0] + "_0.off", True, 0)
    record(out.add(add.make(add.box, [10, -0.25, 100], 1, "red")))
    out.close()
    counts(out)


@case
def stream_closed():
    out = add.stream(_current[0] + ".obj")
    record(out.add(add.make(add.box, [0, 0, 0], 1, "red")))
    out.close()
    add.box([0, 0, 0], 1, "blue")
    record(outcome(out.add))                                    # closed: nothing written, the scene kept
    record(len(add.scene().F))
    record(outcome(out.add, add.make(add.box, [0, 0, 0], 1)))
    add.clear()
    counts(out)
    with add.stream(_current[0] + "_with.obj") as s:            # (C++: closed by the destructor)
        s.add(add.make(add.box, [0, 0, 0], 1, "gold"))
        counts(s)
    with add.stream(_current[0] + "_with.off", True, 3) as s:
        s.add(add.make(add.box, [0, 0, 0], 1, "gold"))
        counts(s)


@case
def texture_edges():
    box = add.make(add.box, [0, 0, 0], 1, "red")
    bad = add.texture(box, "x.png", lambda p, n: (NAN if p[0] > 0 else 0.25, 0.5))   # some are no numbers
    worse = add.texture(box, "x.png", lambda p, n: (0.5, INF))
    record(outcome(add.obj, _current[0] + "_nan.obj", bad))    # (_num raises; the .obj is left half written)
    record(outcome(add.obj, _current[0] + "_inf.obj", worse))
    record(outcome(add.obj_size, bad))                          # the size counts them the same way
    record(outcome(add.obj_size, worse))
    plain = add.color(add.texture(box, "x.png"), "blue")       # texture coordinates, but no picture
    save_obj(plain, "plain")
    pinched = from_faces([[0, 0, 0], [1, 0, 0], [1, 1, 0], [-1, 0, 0], [-1, -1, 0], [3, 3, 3]],
                         [[0, 1, 2, 0, 3, 4], [1, 5, 2]], ["red", "gold"])
    save_obj(add.texture(pinched, "p.png", "xy"), "pinched")   # split into loops, each with its coordinates
    out = add.stream(_current[0] + ".obj", False)
    record(out.add(add.texture(box, "\u0105\u017euolas.png")))   # not ASCII: bytes counts characters
    record(outcome(out.add, bad))
    counts(out)
    record(outcome(out.add, worse))
    record(out.add(add.texture(add.move(box, [2, 0, 0]), "x.png")))   # vt numbers go on after the failed parts
    record(out.add(plain))
    record(out.add(add.texture(pinched, "p.png", "xy")))
    record(out.add(add.texture(box, "a/t.png")))                # two colours, one material name
    record(out.add(add.texture(box, "b/t.png")))
    counts(out)
    out.close()
    counts(out)


@case
def stream_names():
    s = add.stream(_current[0] + "_SHOUT.OBJ")                  # .OBJ is .obj: _SHOUT.mtl
    s.add(add.make(add.box, [0, 0, 0], 1, "red"))
    s.close()
    s = add.stream(_current[0] + "_plain")                      # no extension: OFF
    s.add(add.make(add.box, [0, 0, 0], 1, "red"))
    s.close()
    counts(s)
    s = add.stream(_current[0] + "_empty.obj")
    s.close()
    counts(s)
    s = add.stream(_current[0] + "_empty.off")
    s.close()
    counts(s)


# -- loading ---------------------------------------------------------------------

OFF_FILES = [
    ("basic", b"OFF\n4 2 0\n0 0 0\n1 0 0\n1 1 0\n0 1 0\n3 0 1 2 255 0 0\n3 0 2 3\n"),
    ("comments", b"# a comment line\nOFF   # the header\n\n4 2 0 # counts\n0 0 0 # v0\n   1 0 0\n\n1 1 0\n0 1 0\n"
                 b"# a face\n3 0 1 2 0.5 0.25 1.0\n4 0 1 2 3 1 1 1\n"),
    ("alpha", b"OFF\n3 7 0\n0 0 0\n1 0 0\n0 1 0\n3 0 1 2 255 0 0 128\n3 0 1 2 1.0 0.5 0.0 0.5\n3 0 1 2 0 0 0 0\n"
              b"3 0 1 2 10 20 30 300\n3 0 1 2 0 0 1\n3 0 1 2 1 2 3 4 5 6\n3 0 1 2 0.2 0.4 0.6 1\n"),
    ("same_line", b"COFF 3 1\n0 0 0\n1 0 0\n0 1 0\n3 0 1 2 0 128 255\n"),
    ("two_on_header", b"OFF 7\n3 1 0\n0 0 0\n1 0 0\n0 1 0\n3 0 1 2\n"),
    ("no_header", b"3 1 0\n0 0 0\n1 0 0\n0 1 0\n3 2 1 0\n"),
    ("lower_header", b"noff\n3 1\n0 0 0\n1 0 0\n0 1 0\n3 0 1 2\n"),
    ("separators", b"OFF\r\n3 1 0\r\n0\t0 0\r1\x0b0\x0c0\n0\x1c1\x1d0\x1e\x1f\r\n3 0 1 2\xc2\xa0255\xe3\x80\x800"
                   b"\xe2\x80\x830\xc2\x85\n"),
    ("numbers", b"OFF\n4 1 0\n1_000 -2.5e-3 +.5\n1e2 0 5.\n.5 1E-1 -0\n0 0 0\n4 0 1 2 3 0.25 0.5 0.75\n"),
    ("nonfinite", b"OFF\n4 2 0\ninf 0 0\n0 nan 0\n1e400 0 0\n0 0 0\n3 0 1 3\n3 1 2 3\n"),
    ("slices", b"OFF\n4 7 0\n0 0 0\n1 0 0\n1 1 0\n0 1 0\n5 0 1 2\n-1 5 6 7\n-2 0 1 2\n0 255 0 0\n2 0 1 9 9 9\n"
               b"-7 1 2\n1 3\n"),
    ("bom", b"\xef\xbb\xbfOFF\n3 1 0\n0 0 0\n1 0 0\n0 1 0\n3 0 1 2\n"),
    ("empty", b""),
    ("only_comments", b"# nothing here\n\n   \n"),
    ("hexagon", b"OFF\n6 1 0\n0 0 0\n2 0 0\n3 1 0\n2 2 0\n0 2 0\n-1 1 0\n6 0 1 2 3 4 5 0 0 255\n"),
    ("extra_lines", b"OFF\n3 1 0\n0 0 0 7 8\n1 0 0\n0 1 0\n3 0 1 2\n3 2 1 0\nwhatever\n"),
    ("tabs_and_unicode", b"OFF\n3 1 0\n0\xe2\x80\x800\xe2\x80\x8a0\n1 0\xe2\x80\xa90\n0 1\xe2\x80\xaf0\xe2\x81\x9f\n"
                         b"3 0 1\xe1\x9a\x802\n"),
]

OFF_ERRORS = [
    b"OFF\n1 0 0\n0 0\n",
    b"OFF\n1 0 0\n0 0 x\n",
    b"OFF\n2 0 0\n0 0 0\n",
    b"OFF\nx 0 0\n",
    b"OFF\n1\n",
    b"OFF\n",
    b"OFF\n0 1 0\n3 0 1 2 nan 0 0\n",
    b"OFF\n0 1 0\n3 0 1 2 0.5 inf 0\n",
    b"OFF\n0 1 0\n3 0 1 2 0.5 -inf 0\n",
    b"OFF\n0 1 0\n3 0 1 2 -inf 0.5 0\n",
    b"OFF\n0 1 0\n3 0 1 2 1 1 nan\n",
    b"OFF\n0 1 0\n3 0 1 2.5\n",
    b"OFF\n0 1 0\nx 0 1 2\n",
    b"OFF\n1 0 0\n0x1 0 0\n",
    b"OFF\n1 0 0\n0 0 0\xe2\x80\x8b\n",
    b"OFF\n\xff\n",
    b"OFF\n1 0 0\n\xc3\n",
    b"OFF\n\xed\xa0\x80\n",
    b"OFF\n\xf4\x90\x80\x80\n",
    b"OFF\n\xe0\x80\x80\n",
    b"OFF\n1 0 0\n1\x00 0 0\n",
    b"OFF\n0 1 0\n3 0 1 2 1e308 1e309 0\n",
    b"OFF\n0 1 0\n3 0 1 2 0.5 0.5 nan 0.5\n",
]


@case
def load_off_files():
    for name, data in OFF_FILES:
        write_file(_current[0] + "_" + name + ".txt.off", data)
        M = add.load(_current[0] + "_" + name + ".txt.off")
        record("%s: %d vertices, %d faces" % (name, len(M.V), len(M.F)))
        exact(M, name)
    M = add.load(_current[0] + "_alpha.txt.off", "navy")        # one colour for every face
    exact(M, "navy")
    M = add.load(_current[0] + "_comments.txt.off", (0.5, 0.25, 1.0, 0.5))
    exact(M, "given")
    write_file(_current[0] + "_noext", OFF_FILES[0][1])         # no extension: read as .off
    exact(add.load(_current[0] + "_noext"), "noext")


@case
def load_off_errors():
    for i, data in enumerate(OFF_ERRORS):
        write_file("%s_%d.txt.off" % (_current[0], i), data)
        record("%d %s" % (i, outcome(add.load, "%s_%d.txt.off" % (_current[0], i))))
    record(outcome(add.load, _current[0] + "_missing.off"))
    os.mkdir(_current[0] + "_folder.off")
    record(outcome(add.load, _current[0] + "_folder.off"))
    os.rmdir(_current[0] + "_folder.off")


MTL = (b"# materials\nKd 0.1 0.2 0.3\nnewmtl red\nKd 1 0 0\nnewmtl glass\nKd 0.5 0.75 1.0\nd 0.25\n"
       b"newmtl ghost\nKd 0 1 0\nTr 0.6\nnewmtl tex\nKd 1 1 1\nmap_Kd textures\\wood.png\n"
       b"newmtl tiny\nKd 0.001 0.002 0.003\nnewmtl redefined\nKd 0 0 1\nnewmtl redefined\nKd 0 1 1\n"
       b"newmtl texalpha\nmap_Kd -s 1 1 1 stone.png\nd 0.5\nKd 0.2 0.4 0.6\nnewmtl dbig\nd 50\n"
       b"newmtl \xc5\xbealias\r\nKd\t0.25 0.5 0.75\r\nd\n")

OBJ = (b"# model\nmtllib mats.mtl\no thing\nv 0 0 0\nv 1 0 0\nv 1 1 0\nv 0 1 0 # a comment\nvt 0 0\nvt 1 0\n"
       b"vt 1 1\nvt 0.5\nf 1 2 3\nusemtl red\nf 1 2 3 4\nusemtl glass\nf -4 -3 -2\nusemtl tex\nf 1/1 2/2 3/3\n"
       b"f 1/1/1 2/2/1 3/3/1 4/4/1\nf 1//1 2//1 3//1\nf 1/-4 2/-3 3/-2\nf 1/-5 2/-6 3/-7\nusemtl texalpha\n"
       b"f 1/1 2/2 3/3\nusemtl tiny\nf 2 3 4\nusemtl nosuch\nf 1 3 4\nusemtl redefined\nf 1 2 4\n"
       b"usemtl ghost\nf 1 2 3\nusemtl dbig\nf 2 3 4\ng group\ns off\nl 1 2\nvn 0 0 1\nf 1/2 2 3/1\n"
       b"  #indented comment\n#f 1 2 3\nusemtl \xc5\xbealias\nf 4 3 2 1\nf 0 1 2\nf 1 2 3/2/7/8\n")

OBJ_ERRORS = [
    b"v 1 2\n",
    b"v 0 0 0\nf 1 2 x\n",
    b"v 0 0 0\nvt 0 0\nf 1/9 1/1 1/1\n",
    b"mtllib\n",
    b"usemtl\n",
    b"vt\n",
    b"v 0 0 0\nf 1 1 1 # c\n",
    b"v 0 0 0\nf /1 1 1\n",
    b"v 0 0 0\nvt 0 0\nf 1/0 1/1 1/1\n",
    b"v 0 0 0\nvt 0 0\nf 1/-3 1/1 1/1\n",
    b"v 0 0 0\nf 1.0 1 1\n",
    b"v 0 0 0 \xe2\x80\x8b\nvt 1e999 0\n",
]


@case
def load_obj_files():
    write_file("mats.mtl", MTL)
    write_file(_current[0] + ".txt.obj", OBJ)
    M = add.load(_current[0] + ".txt.obj")
    record("%d vertices, %d faces, uv %s" % (len(M.V), len(M.F), M.UV is not None))
    exact(M, "model")
    M = add.load(_current[0] + ".txt.obj", "gold")              # one colour: the materials are not read
    exact(M, "gold")
    write_file(_current[0] + "_nomtl.txt.obj", b"mtllib nothere.mtl\nv 0 0 0\nv 1 0 0\nv 0 1 0\nusemtl red\nf 1 2 3\n")
    exact(add.load(_current[0] + "_nomtl.txt.obj"), "nomtl")
    write_file(_current[0] + "_mtlerr.txt.obj", b"mtllib bad.mtl\nv 0 0 0\n")
    write_file("bad.mtl", b"newmtl x\nKd 1 x 0\n")
    record(outcome(add.load, _current[0] + "_mtlerr.txt.obj"))  # a bad .mtl is an error, a missing one not
    os.mkdir(_current[0] + "_sub")
    write_file(_current[0] + "_sub/mats.mtl", b"newmtl red\nKd 0 0 1\n")
    write_file(_current[0] + "_sub/m.obj", b"mtllib mats.mtl\nv 0 0 0\nv 1 0 0\nv 0 1 0\nusemtl red\nf 1 2 3\n")
    exact(add.load(_current[0] + "_sub/m.obj"), "sub")          # the .mtl next to the .obj
    write_file(_current[0] + "_sub\\m.obj", b"mtllib mats.mtl\nv 0 0 0\nv 1 0 0\nv 0 1 0\nusemtl red\nf 1 2 3\n")
    exact(add.load(_current[0] + "_sub\\m.obj"), "backslash")  # a file named with a backslash: its .mtl in _sub/
    write_file(_current[0] + "_dirmtl.txt.obj", b"mtllib " + _current[0].encode() + b"_sub\nv 0 0 0\n")
    record(outcome(add.load, _current[0] + "_dirmtl.txt.obj"))  # a folder as the .mtl: left out
    shutil.rmtree(_current[0] + "_sub")
    for i, data in enumerate(OBJ_ERRORS):
        write_file("%s_%d.txt.obj" % (_current[0], i), data)
        record("%d %s" % (i, outcome(add.load, "%s_%d.txt.obj" % (_current[0], i))))
    record(outcome(add.load, _current[0] + "_3.txt.obj", "red"))  # "mtllib" alone is fine with a colour


PLY_FILES = [
    ("props", b"ply\nformat ascii 1.0\ncomment made by hand\nelement vertex 4\nproperty float x\nproperty float y\n"
              b"property float z\nproperty float nx\nproperty uchar red\nelement face 5\n"
              b"property list uchar int vertex_indices\nproperty uchar red\nproperty uchar green\n"
              b"property uchar blue\nelement edge 1\nproperty int vertex1\nend_header\n0 0 0 1 255\n1 0 0 1 255\n"
              b"1 1 0\n0 1 0 1 255 extra\n3 0 1 2 255 0 0\n3 0 2 3 0.5 0.25 1\n4 0 1 2 3\n3 0 1 3 0 0 1\n"
              b"3 1 2 3 10 20 30 40\n0 1\n"),
    ("order", b"ply\nformat ascii 1.0\nelement vertex 3\nproperty float z\nproperty float y\nproperty float x\n"
              b"property float x\nelement face 1\nproperty list uchar int vertex_indices\nend_header\n"
              b"1 2 3 4\n5 6 7 8\n9 10 11\n3 0 1 2\n"),
    ("no_end", b"ply\nformat ascii 1.0\nelement vertex 0\nelement face 0\n"),
    ("blank_vertex", b"ply\nformat ascii 1.0\nelement vertex 3\nproperty float x\nproperty float y\nproperty float z\n"
                     b"element face 1\nend_header\n\n1 0 0\n0 1 0\n3 0 1 2\n"),
    ("crlf", b"ply\r\nformat ascii 1.0\r\nelement vertex 3\r\nproperty float x\r\nproperty float y\r\n"
             b"property float z\r\nelement face 2\r\nend_header\r\n0 0 0\r\n1 0 0\r\n0 1 0\r\n3 0 1 2 0 0 255\r"
             b"-1 255 0\r\n"),
    ("no_vertex_props", b"ply\nelement vertex 2\nelement face 1\nend_header\n1 2 3\n4 5 6\n2 0 1\n"),
]

PLY_ERRORS = [
    b"ply\nelement vertex 1\nproperty float x\n",
    b"ply\nelement vertex 0\nelement face 1\nend_header\n\n",
    b"ply\nelement vertex x\nend_header\n",
    b"ply\nelement\nend_header\n",
    b"ply\nelement vertex 0\nelement face 1\nend_header\n-3 1\n",
    b"ply\nelement vertex 1\nproperty float x\nend_header\n1_0 2\n",
    b"ply\nelement vertex 1\nproperty float x\nend_header\n0x1\n",
    b"ply\nelement vertex 0\nelement face 1\nend_header\n3 0 1 2 nan 0 0\n",
    b"ply\nelement vertex 0\nelement face 1\nend_header\n3 0 1 2 inf 0 0\n",
    b"ply\nelement vertex 0\nelement face 1\nend_header\n3 0 1\n",
]


@case
def load_ply_files():
    for name, data in PLY_FILES:
        write_file(_current[0] + "_" + name + ".txt.ply", data)
        M = add.load(_current[0] + "_" + name + ".txt.ply")
        record("%s: %d vertices, %d faces" % (name, len(M.V), len(M.F)))
        exact(M, name)
    exact(add.load(_current[0] + "_props.txt.ply", (255, 0, 255, 0.5)), "given")
    write_file(_current[0] + "_upper.PLY", PLY_FILES[0][1])
    exact(add.load(_current[0] + "_upper.PLY"), "upper")
    for i, data in enumerate(PLY_ERRORS):
        write_file("%s_%d.txt.ply" % (_current[0], i), data)
        record("%d %s" % (i, outcome(add.load, "%s_%d.txt.ply" % (_current[0], i))))


@case
def load_roundtrip():
    M = model()
    for ext in ("off", "obj", "ply", "OBJ"):
        add.save(_current[0] + "." + ext, M)
        L = add.load(_current[0] + "." + ext)
        record("%s: %d vertices, %d faces" % (ext, len(L.V), len(L.F)))
        exact(L, ext)
    s = add.stream(_current[0] + "_stream.obj", True, 4)
    s.add(M)
    s.add(add.move(M, [0, 0, 10]))
    s.close()
    exact(add.load(_current[0] + "_stream.obj"), "stream")


# -- pictures ----------------------------------------------------------------------

def png_record(name):
    """Decode a PNG with zlib (which checks the Adler-32 of the stored or compressed
    data), check every chunk's CRC, record the header and the pixel bytes -- and delete
    the file: add.py and add.hpp compress differently, so the files themselves differ."""
    with open(name, "rb") as f:
        data = f.read()
    record("signature " + ("ok" if data[:8] == b"\x89PNG\r\n\x1a\n" else "bad"))
    pos, idat, tags, width = 8, b"", [], 0
    while pos < len(data):
        n = struct.unpack(">I", data[pos:pos + 4])[0]
        tag = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + n]
        crc = struct.unpack(">I", data[pos + 8 + n:pos + 12 + n])[0]
        tags.append(tag.decode("ascii") + ("" if crc == zlib.crc32(tag + body) & 0xffffffff else "(bad crc)"))
        if tag == b"IHDR":
            width = struct.unpack(">I", body[:4])[0]
            record("IHDR %d %d %d %d %d %d %d" % struct.unpack(">IIBBBBB", body))
        elif tag == b"IDAT":
            idat += body
        pos += 12 + n
    record("chunks " + " ".join(tags))
    raw = zlib.decompress(idat)
    record("raw bytes %d" % len(raw))
    stride = max(1 + 3 * width, 1)
    for y in range(0, len(raw), stride):
        record(raw[y:y + stride].hex())
    os.remove(name)


@case
def png_pictures():
    rows = [["white" if (x // 8 + y // 8) % 2 else "black" for x in range(64)] for y in range(64)]
    record(add.write_png(_current[0] + "_check.png", rows))
    png_record(_current[0] + "_check.png")
    rows = [[add.hsv(x / 300.0, 1.0 - y / 200.0) for x in range(300)] for y in range(150)]   # 3 stored blocks
    add.write_png(_current[0] + "_wide.png", rows)
    png_record(_current[0] + "_wide.png")
    add.write_png(_current[0] + "_one.png", [["red"]])
    png_record(_current[0] + "_one.png")
    add.write_png(_current[0] + "_none.png", [])
    png_record(_current[0] + "_none.png")
    add.write_png(_current[0] + "_ragged.png", [["red", "blue"], ["green"], []])
    png_record(_current[0] + "_ragged.png")
    add.write_png(_current[0] + "_forms.png", [[(0.5, 0.25, 1.0), "#ff8800", add.transparent("sky", 0.3),
                                               (300, -5, 12), "#abc"]])
    png_record(_current[0] + "_forms.png")
    add.write_png(_current[0] + "_exact.png", [[(x, (x * 7 + y) % 256, 255 - x) for x in range(256)] for y in range(4)])
    png_record(_current[0] + "_exact.png")


# -- letters -------------------------------------------------------------------------

def make_font():
    os.mkdir("font")
    add.cuboid([0, 0.5, 0], [0.6, 1, 0.2], "red")
    add.cuboid([0, 1.1, 0], [0.9, 0.2, 0.2], "red")
    add.off("font/A.off")
    add.box([0, 0, 0], 1, "blue")
    add.tetrahedron([0, 1, 0], 0.5, "green")
    add.off("font/B.off")
    add.pyramid([0, 0, 0], 1, 1.5, "gold")
    add.off("font/\u0104.off")
    add.cuboid([0, 0, 0], [0.2, 1, 0.2], "navy")
    add.off("font/1.off")
    add.cylinder([0, 0, 0], [0, 0.7, 0], 0.3, 6, "teal")
    add.off("font/q.off")
    add.box([0, 0, 0], 0.5, "lime")
    add.off("font/SS.off")                                     # what "\u00df".upper() gives
    write_file("font/E.off", b"OFF\n0 0 0\n")                  # an empty glyph
    write_file("font/X.off", b"OFF\n1 0 0\n0 0 x\n")           # a ValueError: left out
    os.mkdir("font/D.off")                                     # a folder: an OSError, left out
    add.box([0, 0, 0], 1, "purple")
    add.obj("font/Y.obj")
    add.cuboid([0, 0, 0], [1, 2, 3], "pink")
    add.obj("font/A.obj")
    os.mkdir("font2")
    write_file("font2/T.off", b"OFF\n2 0 0\n0 0 0\n")          # an IndexError: not caught


@case
def fonts():
    make_font()
    try:
        font = add.load_font("font")
        record(sorted(font))
        for name in sorted(font):
            record("%s %d vertices %d faces" % (name, len(font[name].V), len(font[name].F)))
        record(sorted(add.load_font("font", "AQB\u0104")))
        record(sorted(add.load_font("font", ["A", "B", "Y", "AB"], ".obj")))
        record(sorted(add.load_font("font", None, ".obj")))
        record(len(add.load_font("no_such_folder")))
        record(len(add.load_font("font/A.off")))                # a file, not a folder
        record(len(add.load_font("font", None, "")))
        record(sorted(add.load_font("font/", "A1")))
        record(outcome(add.load_font, "font2"))
        exact(add.typeset("AB A", font), "plain")
        exact(add.typeset("ab \u0105 1q?E", font, [1, 2, 3], 0.5, 1.5, "navy", ((0, 0, 1), (0, 1, 0))), "options")
        exact(add.typeset("\u0105A\u0104", font, [0, 0, 0], 2.0, 0.5, add.transparent("red", 0.5)), "accents")
        exact(add.typeset("", font), "none")
        exact(add.typeset("zz", font), "missing")
        exact(add.typeset("\u00dfA\U0001F600B\u0149", font, [0, 0, 0], 1.0, 2.0), "wide")   # an emoji is one character
        record(sorted(add.load_font("font", "A\U0001F600")))
        obj_font = add.load_font("font", None, ".obj")
        exact(add.typeset("AYA", obj_font, [0, 0, 0], 1.0, 1.0, None, ((1, 1, 0), (0, 1, 0))), "obj")
    finally:
        shutil.rmtree("font")
        shutil.rmtree("font2")


if __name__ == "__main__":
    import sys
    run(sys.argv)

"""
Run every example in this folder, check every model against the Sketchfab
limits, and render a picture of each model.

    python3 examples/build_all.py            build models, check, thumbnails
    python3 examples/build_all.py --models   models and the check, no pictures
    python3 examples/build_all.py --cpp      compile every C++ example (NN_*.cpp,
                                             add.hpp) and check that it writes
                                             byte for byte what its Python twin writes
                                             (the castle: its quick run, ~25 minutes)

Output goes to ``examples/out/`` (models) and ``docs/images/`` (pictures).
The check fails (exit code 1) when a model could not be uploaded to
Sketchfab as an .obj: more than 50 MB or more than 50 colours (materials).
Big "fine" variants (``--fine`` in the example) are not built here, and the
castle (46) is built at a tenth of its density (``CASTLE_DENSITY=0.1``) --
the full castle is a 1 GB .off (and an .obj meant to be uploaded
compressed with 7-Zip).
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "out")
IMAGES = os.path.join(ROOT, "docs", "images")
sys.path.insert(0, ROOT)

#: camera angles that show each model off best: name -> (turn, tilt, zoom[, background])
VIEWS = {
    "first_model": (30, 20, 1.0),
    "primitives": (22, 38, 1.15),
    "surfaces_classic": (25, 48, 1.2),
    "surfaces_exotic": (28, 46, 1.2),
    "supershapes": (25, 48, 1.2),
    "surfaces_nature": (25, 48, 1.2),
    "height_fields": (25, 46, 1.2),
    "two_sided": (30, 26, 1.15),
    "curves": (25, 46, 1.2),
    "sweeps": (28, 32, 1.15),
    "lathe": (20, 16, 1.2),
    "patterns": (25, 30, 1.15),
    "booleans": (28, 34, 1.2),
    "fractals": (14, 14, 1.15),
    "chess_set": (18, 24, 1.1),
    "city": (35, 24, 1.1),
    "text": (30, 32, 1.05),
    "lighthouse": (30, 24, 1.9),
    "locomotive": (35, 18, 1.7),
    "windmill": (25, 18, 1.8),
    "temple": (15, 12, 2.6),
    "vector_fields": (20, 35, 1.6),
    "robot": (25, 15, 2.2),
    "voxel_island": (25, 30, 1.5),
    "bridge": (35, 22, 1.7),
    "solar_system": (20, 35, 1.6, (20, 20, 40)),
    "workbench": (20, 40, 1.5),
    "old_names": (25, 25, 1.6),
    "cross_sections": (15, 25, 2.3),
    "surface_zoo": (12, 55, 1.2),
    "knot_curve": (25, 30, 1.1),
    "kreive1": (25, 30, 1.1),
    "minecraft_sphere": (8, 22, 1.5),
    "football": (15, 20, 1.6),
    "polyhedra": (12, 42, 1.15),
    "smooth_shapes": (10, 45, 1.5),
    "vertex_tools": (15, 20, 1.6),
    "sketchfab_ready": (15, 20, 1.3),
    "pillow_letters": (20, 20, 1.4),
    "planet": (20, 25, 1.3, (20, 20, 40)),
    "geodesic_dome": (25, 22, 1.3),
    "glass_and_textures": (22, 16, 1.7),
    "castle": dict(turn=28, tilt=34, at=(0, 15.5, 8), radius=58, size=(1100, 760)),
    "example1": (30, 22, 1.0), "example2": (30, 22, 1.0),
    "example3": (30, 28, 1.0), "example4": (20, 12, 1.0),
    "example5": (30, 22, 1.0), "example6": (30, 22, 1.0),
    "example7": (30, 22, 1.0), "example8": (30, 22, 1.0),
    "demo": (32, 24, 1.05),
}

#: more pictures of one model: stem -> [(picture stem, render options)]
EXTRA_VIEWS = {
    "castle": [
        ("castle_gate", dict(eye=(0, 12.6, 67), at=(0, 14.6, 30), fov=32, size=(880, 620))),     # "ADD 2.0" over the arch
        ("castle_yard", dict(eye=(16, 23, 40), at=(0, 12, 14), fov=38, size=(1100, 760))),      # the tilt, the porch
        ("castle_hall", dict(eye=(2, 15, -5), at=(0, 13, -27), fov=36, size=(1100, 760))),
        ("castle_treasury", dict(eye=(-26.8, 13.2, -28.8), at=(-24.5, 12.1, -33.2), fov=44, size=(880, 620))),
    ],
}


def model_files():
    """The models in ``examples/out``: every .off, plus any .obj that has
    no .off twin (models written streaming, like the castle)."""
    names = sorted(os.listdir(OUT))
    offs = [n for n in names if n.endswith(".off")]
    stems = set(n[:-4] for n in offs)
    objs = [n for n in names if n.endswith(".obj") and n[:-4] not in stems]
    return sorted(offs + objs)


def png_pixels(path):
    """The header and the pixel rows of a PNG file (add.hpp stores the
    picture uncompressed, add.py compresses it: the same picture)."""
    import struct
    import zlib
    data = open(path, "rb").read()
    i, idat, head = 8, b"", None
    while i < len(data):
        n = struct.unpack(">I", data[i:i + 4])[0]
        tag, body = data[i + 4:i + 8], data[i + 8:i + 8 + n]
        if tag == b"IHDR":
            head = body
        elif tag == b"IDAT":
            idat += body
        i += 12 + n
    return head, zlib.decompress(idat)


def untimed(text):
    """What a program printed, less the seconds it says it took (the castle
    prints them after every part)."""
    import re
    text = re.sub(r"(?m)\s+\d+s$", "", text)
    return re.sub(r"(?m), \d+ s$", "", text)


def cpp_check():
    """Compile every C++ example and run it next to its Python twin, each in a
    fresh folder; everything they write (and print) must be the same."""
    import shutil
    import tempfile
    cxx = os.environ.get("CXX", "g++")
    stems = sorted(n[:-4] for n in os.listdir(HERE) if n.endswith(".cpp") and n[0].isdigit())
    failed = []
    for stem in stems:
        t = time.time()
        castle = stem == "46_castle"                    # (the castle: built as its quick run, and a big file
        flags = ["-O1", "-fno-exceptions"] if castle else ["-O2"]   # to compile -- see its first lines)
        env = dict(os.environ, CASTLE_DENSITY="0.1") if castle else None
        work = tempfile.mkdtemp(prefix="add_example_")
        py_dir, cpp_dir = os.path.join(work, "py"), os.path.join(work, "cpp")
        os.makedirs(py_dir)
        os.makedirs(cpp_dir)
        exe = os.path.join(work, stem + ".exe")
        p = subprocess.run([cxx, "-std=c++17"] + flags + ["-I", HERE, os.path.join(HERE, stem + ".cpp"), "-o", exe],
                           capture_output=True, text=True)
        if p.returncode:
            print("%-34s COMPILE ERROR\n%s" % (stem + ".cpp", p.stderr[-2000:]))
            failed.append(stem)
            continue
        a = subprocess.run([sys.executable, os.path.join(HERE, stem + ".py")], cwd=py_dir,
                           capture_output=True, text=True, env=env)
        b = subprocess.run([exe], cwd=cpp_dir, capture_output=True, text=True, env=env)
        problems = []
        if a.returncode or b.returncode:
            problems.append("exit status: python %s, c++ %s" % (a.returncode, b.returncode))
        if untimed(a.stdout) != untimed(b.stdout):
            problems.append("they print different text")
        names = sorted(set(os.listdir(py_dir)) | set(os.listdir(cpp_dir)))
        for name in names:
            pa, pb = os.path.join(py_dir, name), os.path.join(cpp_dir, name)
            if not (os.path.exists(pa) and os.path.exists(pb)):
                problems.append("%s only from %s" % (name, "c++" if os.path.exists(pb) else "python"))
            elif name.lower().endswith(".png"):
                if png_pixels(pa) != png_pixels(pb):
                    problems.append(name + ": other pixels")
            elif open(pa, "rb").read() != open(pb, "rb").read():
                problems.append(name + " differs")
        shutil.rmtree(work, ignore_errors=True)
        if problems:
            failed.append(stem)
        print("%-34s %s %6.1fs  %s" % (stem + ".cpp", "FAIL" if problems else "same",
                                        time.time() - t, "; ".join(problems) if problems
                                        else "%d file%s" % (len(names), "" if len(names) == 1 else "s")))
    print()
    if failed:
        print("C++ examples that differ from their Python twins:", ", ".join(failed))
        return 1
    print("all %d C++ examples write byte for byte what their Python twins write" % len(stems))
    return 0


def main():
    if "--cpp" in sys.argv:
        return cpp_check()
    models_only = "--models" in sys.argv
    for folder in (OUT, IMAGES):
        if not os.path.isdir(folder):
            os.makedirs(folder)

    scripts = sorted(n for n in os.listdir(HERE)
                     if n.endswith(".py") and n[0].isdigit())
    os.chdir(OUT)
    env = dict(os.environ)
    env["CASTLE_DENSITY"] = env.get("CASTLE_DENSITY", "0.1")   # the full castle is ~1 GB; the docs get a lighter one
    for name in scripts:
        t = time.time()
        p = subprocess.run([sys.executable, os.path.join(HERE, name)],
                           capture_output=True, env=env)
        status = "ok  " if p.returncode == 0 else "FAIL"
        print("%-34s %s %6.1fs" % (name, status, time.time() - t))
        if p.returncode:
            print(p.stderr.decode()[-800:])

    problems = sketchfab_table()
    if models_only:
        return 1 if problems else 0

    from tools import preview
    for model in model_files():
        stem = model[:-4]
        view = VIEWS.get(stem, (30, 26, 1.1))
        if isinstance(view, dict):
            options = dict(view)
        else:
            options = dict(turn=view[0], tilt=view[1], zoom=view[2])
            if len(view) > 3:
                options["background"] = view[3]
        options.setdefault("size", (880, 620))
        source = os.path.join(OUT, model)
        if os.path.exists(source[:-4] + ".obj"):      # glass is kept in the .obj
            source = source[:-4] + ".obj"
        full = os.path.join(OUT, "castle_full", model[:-4] + ".obj")
        if stem == "castle" and os.path.exists(full):  # the full castle, rendered streaming
            source = full
        t = time.time()
        loaded = source if os.path.getsize(source) > preview.BIG_FILE else add_load(source)
        preview.render(loaded, os.path.join(IMAGES, stem + ".png"), folder=OUT, **options)
        print("%-34s -> docs/images/%s.png  %5.1fs" % (model, stem, time.time() - t))
        for extra, more in EXTRA_VIEWS.get(stem, ()):
            t = time.time()
            preview.render(loaded, os.path.join(IMAGES, extra + ".png"), folder=OUT, **more)
            print("%-34s -> docs/images/%s.png  %5.1fs" % ("", extra, time.time() - t))
    return 1 if problems else 0


def add_load(source):
    """Load a model once (several views share it)."""
    import add
    return add.load(source)


#: Sketchfab: the course wants .obj files under 50 MB with at most 50 colours.
MAX_MB = 50
MAX_COLORS = 50
#: Models meant to be uploaded compressed (7-Zip): the size limit is 100 MB
#: compressed, and the course allows them 100 colours.
COMPRESSED = {"castle.off", "castle.obj"}
MAX_COLORS_BIG = 100


def big_stats(path):
    """The numbers of the table for an .off too big to load (the castle: a
    few GB in memory), read from the file line by line: its polygons, its
    colours, and the size of the .obj written beside it."""
    colours = set()
    with open(path) as f:
        f.readline()                                  # "OFF"
        nv, nf = [int(v) for v in f.readline().split()[:2]]
        for _ in range(nv):
            f.readline()
        for _ in range(nf):
            p = f.readline().split()
            colours.add(tuple(p[1 + int(p[0]):]))
    obj = path[:-4] + ".obj"
    size = os.path.getsize(obj) if os.path.exists(obj) else os.path.getsize(path)
    return {"faces": nf, "colors": len(colours), "obj_bytes": size}


def sketchfab_table():
    """Print one line per model: polygons, colours, .obj size, verdict."""
    import add
    from tools import preview
    problems = []
    print()
    print("%-28s %9s %7s %9s  %s" % ("model", "polygons", "colours", ".obj MB",
                                      "Sketchfab"))
    for model in model_files():
        path = os.path.join(OUT, model)
        if model.endswith(".off") and os.path.getsize(path) > preview.BIG_FILE:
            s = big_stats(path)                       # (counted, not loaded)
        else:
            s = add.stats(add.load(path))
        mb = s["obj_bytes"] / 1e6
        colors = MAX_COLORS_BIG if model in COMPRESSED else MAX_COLORS
        ok = (mb <= MAX_MB or model in COMPRESSED) and s["colors"] <= colors
        verdict = "ok" if ok else ("TOO MANY COLOURS" if s["colors"] > colors else "TOO BIG")
        if model in COMPRESSED:
            verdict += " (7-Zip it: under 100 MB compressed)"
        print("%-28s %9d %7d %9.1f  %s" % (model, s["faces"], s["colors"], mb, verdict))
        if not ok:
            problems.append(model)
    if problems:
        print("over the Sketchfab limits (%d MB, %d colours):" % (MAX_MB, MAX_COLORS),
              ", ".join(problems))
    else:
        print("every model fits the Sketchfab limits (%d MB, %d colours)"
              % (MAX_MB, MAX_COLORS))
    return problems


if __name__ == "__main__":
    sys.exit(main())

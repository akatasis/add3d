"""
Run every example in this folder and render a picture of each model.

    python3 examples/build_all.py            build models and thumbnails
    python3 examples/build_all.py --models   models only, no pictures

Output goes to ``examples/out/`` (models) and ``docs/images/`` (pictures).
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

#: camera angles that show each model off best: name -> (turn, tilt, zoom)
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
    "example1": (30, 22, 1.0), "example2": (30, 22, 1.0),
    "example3": (30, 28, 1.0), "example4": (20, 12, 1.0),
    "example5": (30, 22, 1.0), "example6": (30, 22, 1.0),
    "example7": (30, 22, 1.0), "example8": (30, 22, 1.0),
    "demo": (32, 24, 1.05),
}


def main():
    models_only = "--models" in sys.argv
    for folder in (OUT, IMAGES):
        if not os.path.isdir(folder):
            os.makedirs(folder)

    scripts = sorted(n for n in os.listdir(HERE)
                     if n.endswith(".py") and n[0].isdigit())
    os.chdir(OUT)
    for name in scripts:
        t = time.time()
        p = subprocess.run([sys.executable, os.path.join(HERE, name)],
                           capture_output=True)
        status = "ok  " if p.returncode == 0 else "FAIL"
        print("%-34s %s %6.1fs" % (name, status, time.time() - t))
        if p.returncode:
            print(p.stderr.decode()[-800:])

    if models_only:
        return 0

    from tools import preview
    for model in sorted(os.listdir(OUT)):
        if not model.endswith(".off"):
            continue
        stem = model[:-4]
        turn, tilt, zoom = VIEWS.get(stem, (30, 26, 1.1))
        t = time.time()
        preview.render(os.path.join(OUT, model),
                       os.path.join(IMAGES, stem + ".png"),
                       size=(880, 620), turn=turn, tilt=tilt, zoom=zoom)
        print("%-34s -> docs/images/%s.png  %5.1fs" % (model, stem,
                                                       time.time() - t))
    return 0


if __name__ == "__main__":
    sys.exit(main())

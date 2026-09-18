"""
preview.py -- look at a model without installing anything.

A tiny software renderer: it reads an ``.off`` / ``.obj`` / ``.ply`` file (or a
mesh you already have in memory) and writes a shaded PNG.  Like add.py itself
it uses only the standard library, so it runs wherever Python runs -- handy
when MeshLab is not at hand, for checking a model over SSH, and for making the
pictures in this project's documentation.

From the command line::

    python3 tools/preview.py model.off                 # -> model.png
    python3 tools/preview.py model.off shot.png --size 1200 900 --turn 35

From Python::

    import add
    from tools import preview
    add.sphere([0, 0, 0], 1, 20, "red")
    preview.render(add.layer(), "ball.png")
"""

import math
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import add


# ---------------------------------------------------------------------------
#  PNG writing (stdlib only)
# ---------------------------------------------------------------------------

def write_png(path, width, height, pixels):
    """Write an RGB PNG.  ``pixels`` is a flat bytearray of 3 bytes per pixel."""
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)                                  # filter type "none"
        raw.extend(pixels[y * stride:(y + 1) * stride])

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", header))
        f.write(chunk(b"IDAT", zlib.compress(bytes(raw), 6)))
        f.write(chunk(b"IEND", b""))
    return path


# ---------------------------------------------------------------------------
#  Rendering
# ---------------------------------------------------------------------------

def render(model, path="preview.png", size=(900, 700), turn=35.0, tilt=22.0,
           zoom=1.0, background=(250, 250, 250), light=(-0.4, 0.8, 0.6),
           ambient=0.28, ground=True, outline=False):
    """Render a mesh (or a model file) to a PNG and return the path.

    ``turn`` and ``tilt`` are the camera angles in degrees, ``zoom`` scales the
    framing, ``light`` is the direction the light comes from.
    """
    if isinstance(model, str):
        model = add.load(model)
    M = add.as_mesh(model)
    if not M.F:
        raise ValueError("nothing to render")

    width, height = int(size[0]), int(size[1])
    lo, hi = add.bbox(M)
    centre = [(lo[a] + hi[a]) / 2.0 for a in range(3)]
    radius = max(1e-6, max(hi[a] - lo[a] for a in range(3))) * 0.5

    # Camera basis.
    ta, ti = math.radians(turn), math.radians(tilt)
    eye_dir = (math.cos(ti) * math.sin(ta), math.sin(ti), math.cos(ti) * math.cos(ta))
    distance = radius * 3.2 / max(0.05, zoom)
    eye = [centre[a] + eye_dir[a] * distance for a in range(3)]
    forward = [-eye_dir[a] for a in range(3)]
    up0 = (0.0, 1.0, 0.0)
    right = _unit(_cross(forward, up0))
    if _norm(right) < 1e-9:
        right = (1.0, 0.0, 0.0)
    up = _cross(right, forward)

    focal = 0.5 * height / math.tan(math.radians(26.0))

    # Transform every vertex into camera space once.
    cam = []
    for p in M.V:
        d = (p[0] - eye[0], p[1] - eye[1], p[2] - eye[2])
        cam.append((_dot(d, right), _dot(d, up), _dot(d, forward)))

    light = _unit(light)
    pixels = bytearray()
    for y in range(height):
        t = y / float(height - 1)
        for x in range(width):
            # A soft vertical gradient reads better than a flat background.
            shade = 1.0 - 0.10 * t
            pixels.append(int(background[0] * shade))
            pixels.append(int(background[1] * shade))
            pixels.append(int(background[2] * shade))
    depth = [1e30] * (width * height)

    half_w, half_h = width * 0.5, height * 0.5

    def project(v):
        z = v[2]
        if z <= 1e-6:
            return None
        return (half_w + v[0] * focal / z, half_h - v[1] * focal / z, z)

    triangles = 0
    for f, colour in zip(M.F, M.C):
        if len(f) < 3:
            continue
        a3 = M.V[f[0]]
        for t in range(1, len(f) - 1):
            b3, c3 = M.V[f[t]], M.V[f[t + 1]]
            n = _cross(_sub(b3, a3), _sub(c3, a3))
            ln = _norm(n)
            if ln < 1e-15:
                continue
            n = (n[0] / ln, n[1] / ln, n[2] / ln)
            lam = abs(n[0] * light[0] + n[1] * light[1] + n[2] * light[2])
            # A second, dimmer light from the camera keeps cavities readable.
            rim = abs(n[0] * eye_dir[0] + n[1] * eye_dir[1] + n[2] * eye_dir[2])
            shade = ambient + (1.0 - ambient) * (0.75 * lam + 0.25 * rim)
            col = (min(255, int(colour[0] * shade)),
                   min(255, int(colour[1] * shade)),
                   min(255, int(colour[2] * shade)))
            pa, pb, pc = (project(cam[f[0]]), project(cam[f[t]]),
                          project(cam[f[t + 1]]))
            if pa is None or pb is None or pc is None:
                continue
            triangles += _raster(pixels, depth, width, height, pa, pb, pc, col)

    write_png(path, width, height, pixels)
    return path


def _raster(pixels, depth, width, height, a, b, c, col):
    """Fill one triangle with a z-buffer test."""
    minx = max(0, int(math.floor(min(a[0], b[0], c[0]))))
    maxx = min(width - 1, int(math.ceil(max(a[0], b[0], c[0]))))
    miny = max(0, int(math.floor(min(a[1], b[1], c[1]))))
    maxy = min(height - 1, int(math.ceil(max(a[1], b[1], c[1]))))
    if minx > maxx or miny > maxy:
        return 0
    det = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
    if abs(det) < 1e-12:
        return 0
    inv = 1.0 / det
    r, g, bl = col
    for y in range(miny, maxy + 1):
        py = y + 0.5
        row = y * width
        for x in range(minx, maxx + 1):
            px = x + 0.5
            w0 = ((b[1] - c[1]) * (px - c[0]) + (c[0] - b[0]) * (py - c[1])) * inv
            if w0 < 0.0 or w0 > 1.0:
                continue
            w1 = ((c[1] - a[1]) * (px - c[0]) + (a[0] - c[0]) * (py - c[1])) * inv
            if w1 < 0.0 or w0 + w1 > 1.0:
                continue
            w2 = 1.0 - w0 - w1
            z = w0 * a[2] + w1 * b[2] + w2 * c[2]
            i = row + x
            if z >= depth[i]:
                continue
            depth[i] = z
            j = i * 3
            pixels[j] = r
            pixels[j + 1] = g
            pixels[j + 2] = bl
    return 1


# -- the three vector helpers this file needs --------------------------------

def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def _norm(a):
    return math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])


def _unit(a):
    n = _norm(a)
    return (a[0] / n, a[1] / n, a[2] / n) if n > 1e-12 else (0.0, 0.0, 1.0)


# ---------------------------------------------------------------------------

def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    src = argv[1]
    out = argv[2] if len(argv) > 2 and not argv[2].startswith("-") \
        else os.path.splitext(src)[0] + ".png"
    size = (900, 700)
    turn, tilt, zoom = 35.0, 22.0, 1.0
    i = 2
    while i < len(argv):
        if argv[i] == "--size":
            size = (int(argv[i + 1]), int(argv[i + 2]))
            i += 3
        elif argv[i] == "--turn":
            turn = float(argv[i + 1])
            i += 2
        elif argv[i] == "--tilt":
            tilt = float(argv[i + 1])
            i += 2
        elif argv[i] == "--zoom":
            zoom = float(argv[i + 1])
            i += 2
        else:
            i += 1
    print(render(src, out, size, turn, tilt, zoom))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

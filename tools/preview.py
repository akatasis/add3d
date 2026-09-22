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
    python3 tools/preview.py castle.obj hall.png --at 0 18 -34 --radius 12
    python3 tools/preview.py castle.obj in.png --eye 0 17 -22 --at 0 17 -44 --fov 40

A file bigger than 150 MB is not loaded but streamed (``render_big``): the
vertices go into a flat array, the faces are drawn as they are read, so the
600 MB castle renders in a few hundred megabytes of memory.

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


def read_png(path):
    """Read an 8-bit RGB / RGBA / grey PNG: ``(width, height, rows)`` with
    ``rows[y][x] = (r, g, b)``.  Enough for textures written by
    ``add.write_png`` and by most image programs (no palettes, no 16-bit)."""
    with open(path, "rb") as f:
        data = f.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG file: %s" % path)
    pos = 8
    width = height = 0
    depth = ctype = 0
    idat = bytearray()
    while pos < len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        tag = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + length]
        pos += 12 + length
        if tag == b"IHDR":
            width, height, depth, ctype = struct.unpack(">IIBB", body[:10])
        elif tag == b"IDAT":
            idat.extend(body)
        elif tag == b"IEND":
            break
    if depth != 8 or ctype not in (0, 2, 4, 6):
        raise ValueError("unsupported PNG (need 8-bit grey/RGB/RGBA): %s" % path)
    channels = {0: 1, 2: 3, 4: 2, 6: 4}[ctype]
    raw = zlib.decompress(bytes(idat))
    stride = width * channels
    rows = []
    prev = bytearray(stride)
    at = 0
    for y in range(height):
        ftype = raw[at]
        line = bytearray(raw[at + 1:at + 1 + stride])
        at += 1 + stride
        for i in range(stride):
            a = line[i - channels] if i >= channels else 0
            b = prev[i]
            c = prev[i - channels] if i >= channels else 0
            if ftype == 1:
                line[i] = (line[i] + a) & 255
            elif ftype == 2:
                line[i] = (line[i] + b) & 255
            elif ftype == 3:
                line[i] = (line[i] + ((a + b) >> 1)) & 255
            elif ftype == 4:
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pred = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pred) & 255
        row = []
        for x in range(width):
            px = line[x * channels:(x + 1) * channels]
            if channels >= 3:
                row.append((px[0], px[1], px[2]))
            else:
                row.append((px[0], px[0], px[0]))
        rows.append(row)
        prev = line
    return width, height, rows


# ---------------------------------------------------------------------------
#  Rendering
# ---------------------------------------------------------------------------

def render(model, path="preview.png", size=(900, 700), turn=35.0, tilt=22.0,
           zoom=1.0, background=(250, 250, 250), light=(-0.4, 0.8, 0.6),
           ambient=0.28, ground=True, outline=False, at=None, radius=None,
           eye=None, fov=26.0, folder=None):
    """Render a mesh (or a model file) to a PNG and return the path.

    ``turn`` and ``tilt`` are the camera angles in degrees, ``zoom`` scales the
    framing, ``light`` is the direction the light comes from.  By default the
    whole model is framed; ``at`` (a point) and ``radius`` frame a part of it
    instead, and ``eye`` puts the camera at an exact point looking at ``at``
    (for a view from inside a building).  ``fov`` is the half angle of view
    in degrees.  ``folder`` is where the texture pictures of a mesh given
    in memory live (for a file name it is the file's folder).
    """
    folder = folder or ""
    if isinstance(model, str):
        if os.path.getsize(model) > BIG_FILE:
            return render_big(model, path, size, turn, tilt, zoom, background, light,
                              ambient, at, radius, eye, fov)
        folder = os.path.dirname(os.path.abspath(model))
        model = add.load(model)
    M = add.as_mesh(model)
    if not M.F:
        raise ValueError("nothing to render")
    # Texture images, by file name (a missing picture falls back to colour).
    images = {}
    for colour in M.C:
        if len(colour) > 4 and colour[4] not in images:
            name = colour[4]
            try:
                images[name] = read_png(os.path.join(folder, name)
                                        if folder else name)
            except (IOError, OSError, ValueError, KeyError):
                images[name] = None

    width, height = int(size[0]), int(size[1])
    lo, hi = add.bbox(M)
    centre = [(lo[a] + hi[a]) / 2.0 for a in range(3)] if at is None else list(at)
    if radius is None:
        radius = max(1e-6, max(hi[a] - lo[a] for a in range(3))) * 0.5

    # Camera basis.
    if eye is None:
        ta, ti = math.radians(turn), math.radians(tilt)
        eye_dir = (math.cos(ti) * math.sin(ta), math.sin(ti), math.cos(ti) * math.cos(ta))
        distance = radius * 3.2 / max(0.05, zoom)
        eye = [centre[a] + eye_dir[a] * distance for a in range(3)]
    else:
        eye = list(eye)
        eye_dir = _unit(_sub(eye, centre))
    forward = [-eye_dir[a] for a in range(3)]
    up0 = (0.0, 1.0, 0.0)
    right = _unit(_cross(forward, up0))
    if _norm(right) < 1e-9:
        right = (1.0, 0.0, 0.0)
    up = _cross(right, forward)

    focal = 0.5 * height / math.tan(math.radians(fov))

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
    see_through = []                      # drawn last, far to near, blended
    for k, (f, colour) in enumerate(zip(M.F, M.C)):
        if len(f) < 3:
            continue
        alpha = colour[3] if len(colour) > 3 else 1.0
        image = images.get(colour[4]) if len(colour) > 4 else None
        uv = M.UV[k] if (image is not None and M.UV is not None) else None
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
            corners = [(cam[f[0]], uv[0] if uv else None),
                       (cam[f[t]], uv[t] if uv else None),
                       (cam[f[t + 1]], uv[t + 1] if uv else None)]
            # Corners behind the camera are clipped off at the near plane, so
            # a big floor or wall the camera stands on is still drawn.
            for clipped in _clip_near(corners, NEAR):
                pa, pb, pc = (project(clipped[0][0]), project(clipped[1][0]),
                              project(clipped[2][0]))
                if pa is None or pb is None or pc is None:
                    continue
                tex = None
                if uv is not None:
                    tex = (image, clipped[0][1], clipped[1][1], clipped[2][1], shade)
                if alpha < 1.0:
                    see_through.append(((pa[2] + pb[2] + pc[2]) / 3.0, pa, pb, pc,
                                        col, alpha, tex))
                    continue
                triangles += _raster(pixels, depth, width, height, pa, pb, pc, col,
                                     1.0, tex)
    see_through.sort(key=lambda item: -item[0])
    for z, pa, pb, pc, col, alpha, tex in see_through:
        triangles += _raster(pixels, depth, width, height, pa, pb, pc, col,
                             alpha, tex)

    write_png(path, width, height, pixels)
    return path


NEAR = 0.05                                 # camera-space clipping distance
BIG_FILE = 150 * 1024 * 1024                # files above this are rendered streaming


def _camera(lo, hi, at, radius, eye, turn, tilt, zoom, height, fov):
    """The camera basis: ``(eye, eye_dir, right, up, forward, focal)``."""
    centre = [(lo[a] + hi[a]) / 2.0 for a in range(3)] if at is None else list(at)
    if radius is None:
        radius = max(1e-6, max(hi[a] - lo[a] for a in range(3))) * 0.5
    if eye is None:
        ta, ti = math.radians(turn), math.radians(tilt)
        eye_dir = (math.cos(ti) * math.sin(ta), math.sin(ti), math.cos(ti) * math.cos(ta))
        distance = radius * 3.2 / max(0.05, zoom)
        eye = [centre[a] + eye_dir[a] * distance for a in range(3)]
    else:
        eye = list(eye)
        eye_dir = _unit(_sub(eye, centre))
    forward = [-eye_dir[a] for a in range(3)]
    right = _unit(_cross(forward, (0.0, 1.0, 0.0)))
    if _norm(right) < 1e-9:
        right = (1.0, 0.0, 0.0)
    up = _cross(right, forward)
    focal = 0.5 * height / math.tan(math.radians(fov))
    return eye, eye_dir, right, up, forward, focal


def _read_mtl(path):
    """``{material name: (r, g, b, alpha)}`` from a .mtl file (no textures)."""
    out = {}
    name = None
    try:
        with open(path) as f:
            for line in f:
                parts = line.split()
                if not parts:
                    continue
                if parts[0] == "newmtl":
                    name = parts[1]
                    out[name] = [200, 200, 200, 1.0]
                elif parts[0] == "Kd" and name:
                    out[name][0:3] = [int(round(float(v) * 255)) for v in parts[1:4]]
                elif parts[0] == "d" and name:
                    out[name][3] = float(parts[1])
    except (IOError, OSError):
        pass
    return {k: tuple(v) for k, v in out.items()}


def _big_faces(path):
    """Yield ``(vertex_reader_done, ...)``: a two-phase reader for a big
    ``.obj`` or ``.off`` -- first every vertex, then every face with its
    colour, without ever holding the faces in memory.  Returns a pair of
    generators: ``vertices()`` yields (x, y, z); ``faces()`` yields
    ``(indices, (r, g, b, alpha))``."""
    from array import array
    kind = "obj" if path.lower().endswith(".obj") else "off"
    V = array("d")
    lo = [1e30, 1e30, 1e30]
    hi = [-1e30, -1e30, -1e30]
    faces_from = 0
    if kind == "obj":
        with open(path) as f:
            for line in f:
                if line.startswith("v "):
                    x, y, z = (float(t) for t in line.split()[1:4])
                    V.append(x)
                    V.append(y)
                    V.append(z)
                    for a, v in enumerate((x, y, z)):
                        if v < lo[a]:
                            lo[a] = v
                        if v > hi[a]:
                            hi[a] = v
        materials = _read_mtl(os.path.splitext(path)[0] + ".mtl")

        def faces():
            colour = (200, 200, 200, 1.0)
            with open(path) as f:
                for line in f:
                    if line.startswith("f "):
                        idx = [int(t.split("/")[0]) - 1 for t in line.split()[1:]]
                        yield idx, colour
                    elif line.startswith("usemtl"):
                        colour = materials.get(line.split()[1], colour)
    else:
        with open(path) as f:
            head = f.readline().split()
            counts = head[1:] if len(head) >= 3 else f.readline().split()
            nv = int(counts[0])
            for _ in range(nv):
                x, y, z = (float(t) for t in f.readline().split()[:3])
                V.append(x)
                V.append(y)
                V.append(z)
                for a, v in enumerate((x, y, z)):
                    if v < lo[a]:
                        lo[a] = v
                    if v > hi[a]:
                        hi[a] = v
            faces_from = f.tell()

        def faces():
            with open(path) as f:
                f.seek(faces_from)
                for line in f:
                    p = line.split()
                    if not p:
                        continue
                    n = int(p[0])
                    idx = [int(t) for t in p[1:1 + n]]
                    rest = p[1 + n:]
                    if len(rest) >= 4:
                        colour = (int(rest[0]), int(rest[1]), int(rest[2]), int(rest[3]) / 255.0)
                    elif len(rest) >= 3:
                        colour = (int(rest[0]), int(rest[1]), int(rest[2]), 1.0)
                    else:
                        colour = (200, 200, 200, 1.0)
                    yield idx, colour
    return V, lo, hi, faces


def render_big(path, out="preview.png", size=(900, 700), turn=35.0, tilt=22.0, zoom=1.0,
               background=(250, 250, 250), light=(-0.4, 0.8, 0.6), ambient=0.28,
               at=None, radius=None, eye=None, fov=26.0):
    """Render a model file too big to load: the vertices are read into a
    flat array and turned into camera space, then the faces are streamed
    from the file and drawn one by one -- a 600 MB castle in a few hundred
    megabytes of memory.  Colours and opacity come from the .mtl (for
    .obj) or the face lines (for .off); textures are ignored."""
    V, lo, hi, faces = _big_faces(path)
    width, height = int(size[0]), int(size[1])
    eye, eye_dir, right, up, forward, focal = _camera(lo, hi, at, radius, eye, turn, tilt, zoom, height, fov)
    n = len(V) // 3
    for i in range(n):                                  # to camera space, in place
        j = 3 * i
        dx, dy, dz = V[j] - eye[0], V[j + 1] - eye[1], V[j + 2] - eye[2]
        V[j] = dx * right[0] + dy * right[1] + dz * right[2]
        V[j + 1] = dx * up[0] + dy * up[1] + dz * up[2]
        V[j + 2] = dx * forward[0] + dy * forward[1] + dz * forward[2]
    light = _unit(light)
    # the light and the eye direction in camera space, so normals can be
    # taken from the camera-space corners directly
    cam_light = (_dot(light, right), _dot(light, up), _dot(light, forward))
    cam_eye = (_dot(eye_dir, right), _dot(eye_dir, up), _dot(eye_dir, forward))
    pixels = bytearray()
    for y in range(height):
        shade = 1.0 - 0.10 * y / float(height - 1)
        row = bytes((int(background[0] * shade), int(background[1] * shade), int(background[2] * shade))) * width
        pixels.extend(row)
    depth = [1e30] * (width * height)
    half_w, half_h = width * 0.5, height * 0.5

    def project(v):
        z = v[2]
        if z <= 1e-6:
            return None
        return (half_w + v[0] * focal / z, half_h - v[1] * focal / z, z)

    see_through = []
    for idx, colour in faces():
        if len(idx) < 3:
            continue
        alpha = colour[3]
        a3 = (V[3 * idx[0]], V[3 * idx[0] + 1], V[3 * idx[0] + 2])
        for t in range(1, len(idx) - 1):
            jb, jc = 3 * idx[t], 3 * idx[t + 1]
            b3 = (V[jb], V[jb + 1], V[jb + 2])
            c3 = (V[jc], V[jc + 1], V[jc + 2])
            nx = (b3[1] - a3[1]) * (c3[2] - a3[2]) - (b3[2] - a3[2]) * (c3[1] - a3[1])
            ny = (b3[2] - a3[2]) * (c3[0] - a3[0]) - (b3[0] - a3[0]) * (c3[2] - a3[2])
            nz = (b3[0] - a3[0]) * (c3[1] - a3[1]) - (b3[1] - a3[1]) * (c3[0] - a3[0])
            ln = math.sqrt(nx * nx + ny * ny + nz * nz)
            if ln < 1e-15:
                continue
            lam = abs(nx * cam_light[0] + ny * cam_light[1] + nz * cam_light[2]) / ln
            rim = abs(nx * cam_eye[0] + ny * cam_eye[1] + nz * cam_eye[2]) / ln
            shade = ambient + (1.0 - ambient) * (0.75 * lam + 0.25 * rim)
            col = (min(255, int(colour[0] * shade)), min(255, int(colour[1] * shade)), min(255, int(colour[2] * shade)))
            if a3[2] >= NEAR and b3[2] >= NEAR and c3[2] >= NEAR:
                pieces = (((a3, None), (b3, None), (c3, None)),)
            else:
                pieces = _clip_near([(a3, None), (b3, None), (c3, None)], NEAR)
            for clipped in pieces:
                pa, pb, pc = project(clipped[0][0]), project(clipped[1][0]), project(clipped[2][0])
                if pa is None or pb is None or pc is None:
                    continue
                if alpha < 1.0:
                    see_through.append(((pa[2] + pb[2] + pc[2]) / 3.0, pa, pb, pc, col, alpha))
                    continue
                _raster(pixels, depth, width, height, pa, pb, pc, col, 1.0, None)
    see_through.sort(key=lambda item: -item[0])
    for z, pa, pb, pc, col, alpha in see_through:
        _raster(pixels, depth, width, height, pa, pb, pc, col, alpha, None)
    write_png(out, width, height, pixels)
    return out


def _clip_near(corners, near):
    """Clip a camera-space triangle against the plane z = near.

    ``corners`` are ``(point, uv)`` pairs; the result is a list of triangles
    (each again three ``(point, uv)`` pairs), empty when the whole triangle
    is behind the camera."""
    inside = [c for c in corners if c[0][2] >= near]
    if len(inside) == 3:
        return [corners]
    if not inside:
        return []
    poly = []
    n = len(corners)
    for i in range(n):
        p, q = corners[i], corners[(i + 1) % n]
        pin, qin = p[0][2] >= near, q[0][2] >= near
        if pin:
            poly.append(p)
        if pin != qin:
            t = (near - p[0][2]) / (q[0][2] - p[0][2])
            point = tuple(p[0][k] + (q[0][k] - p[0][k]) * t for k in range(3))
            uv = None
            if p[1] is not None and q[1] is not None:
                uv = (p[1][0] + (q[1][0] - p[1][0]) * t, p[1][1] + (q[1][1] - p[1][1]) * t)
            poly.append((point, uv))
    return [(poly[0], poly[i], poly[i + 1]) for i in range(1, len(poly) - 1)]


def _raster(pixels, depth, width, height, a, b, c, col, alpha=1.0, tex=None):
    """Fill one triangle with a z-buffer test.

    A see-through triangle (``alpha`` < 1) is blended over what is already
    there and does not write to the depth buffer.  ``tex`` is
    ``(image, uv_a, uv_b, uv_c, shade)`` for a textured triangle: the colour
    is then looked up in the image (nearest texel, repeating).
    """
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
    # Depth (and texture coordinates) are interpolated as 1/z, so that big
    # triangles close to the camera get the right depth at every pixel.
    ia, ib, ic = 1.0 / a[2], 1.0 / b[2], 1.0 / c[2]
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
            iz = w0 * ia + w1 * ib + w2 * ic
            z = 1.0 / iz
            i = row + x
            if z >= depth[i]:
                continue
            j = i * 3
            if tex is not None:
                image, ua, ub, uc, shade = tex
                tw, th, rows = image
                u = (w0 * ua[0] * ia + w1 * ub[0] * ib + w2 * uc[0] * ic) * z
                v = (w0 * ua[1] * ia + w1 * ub[1] * ib + w2 * uc[1] * ic) * z
                texel = rows[int((1.0 - v) * th) % th][int(u * tw) % tw]
                r = min(255, int(texel[0] * shade))
                g = min(255, int(texel[1] * shade))
                bl = min(255, int(texel[2] * shade))
            if alpha < 1.0:
                keep = 1.0 - alpha
                pixels[j] = int(pixels[j] * keep + r * alpha)
                pixels[j + 1] = int(pixels[j + 1] * keep + g * alpha)
                pixels[j + 2] = int(pixels[j + 2] * keep + bl * alpha)
                continue
            depth[i] = z
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
    at = radius = eye = None
    fov = 26.0
    i = 2
    while i < len(argv):
        if argv[i] == "--size":
            size = (int(argv[i + 1]), int(argv[i + 2]))
            i += 3
        elif argv[i] == "--at":
            at = [float(v) for v in argv[i + 1:i + 4]]
            i += 4
        elif argv[i] == "--eye":
            eye = [float(v) for v in argv[i + 1:i + 4]]
            i += 4
        elif argv[i] == "--radius":
            radius = float(argv[i + 1])
            i += 2
        elif argv[i] == "--fov":
            fov = float(argv[i + 1])
            i += 2
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
    print(render(src, out, size, turn, tilt, zoom, at=at, radius=radius,
                 eye=eye, fov=fov))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

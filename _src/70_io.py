

# ============================================================================
# 25. Saving and loading
# ============================================================================

def save(path, M=None, clear_scene=None, colors=None):
    """Write a model to disk; the file format follows the extension.

    ``.off`` (the course format), ``.obj`` (+ a ``.mtl`` colour file, which is
    what Sketchfab and most other tools want), ``.ply`` or ``.stl``::

        add.save("dragon.obj")

    Called without a mesh it saves -- and then empties -- the current scene,
    exactly like add.py 1.2's ``off()``.  ``colors=50`` reduces the model
    to at most that many colours first (see :func:`limit_colors`), which
    keeps an ``.obj`` within Sketchfab's material limit.
    """
    if clear_scene is None:
        clear_scene = M is None
    mesh_to_save = as_mesh(M)
    if colors is not None:
        mesh_to_save = limit_colors(mesh_to_save, colors)
    ext = path.lower().rsplit(".", 1)[-1] if "." in path else "off"
    if ext == "obj":
        _write_obj(path, mesh_to_save)
    elif ext == "ply":
        _write_ply(path, mesh_to_save)
    elif ext == "stl":
        _write_stl(path, mesh_to_save)
    else:
        _write_off(path, mesh_to_save)
    if clear_scene:
        clear()
    return path


def off(path, M=None):
    """Write an OFF file (and empty the scene) -- the add.py 1.2 behaviour."""
    clear_scene = M is None
    _write_off(path, as_mesh(M))
    if clear_scene:
        clear()
    return path


def obj(path, M=None, mtl=None):
    """Write an OBJ file plus the matching MTL colour file.

    OBJ is what you need for Sketchfab: upload the ``.obj`` and ``.mtl``
    together (in one ``.zip``/``.7z``) and the colours come along.
    """
    clear_scene = M is None
    _write_obj(path, as_mesh(M), mtl)
    if clear_scene:
        clear()
    return path


def _write_off(path, M):
    with open(path, "w") as f:
        f.write("OFF\n%d %d 0\n" % (len(M.V), len(M.F)))
        out = []
        for p in M.V:
            out.append("%s %s %s\n" % (_num(p[0]), _num(p[1]), _num(p[2])))
        f.write("".join(out))
        out = []
        for face, c in zip(M.F, M.C):
            out.append("%d %s %d %d %d\n" % (len(face),
                                             " ".join(str(i) for i in face),
                                             c[0], c[1], c[2]))
        f.write("".join(out))


def _material_name(c):
    """``color_rrggbb``, plus ``_aNNN`` when see-through and ``_tNAME`` when
    textured -- one material per distinct look."""
    r, g, b, alpha, image = _material(c)
    name = "color_%02x%02x%02x" % (r, g, b)
    if alpha < 1.0:
        name += "_a%03d" % int(round(alpha * 1000))
    if image:
        stem = image.replace("\\", "/").rsplit("/", 1)[-1].rsplit(".", 1)[0]
        name += "_t" + "".join(ch if ch.isalnum() else "_" for ch in stem)
    return name


def _write_obj(path, M, mtl_path=None):
    if mtl_path is None:
        mtl_path = path[:-4] + ".mtl" if path.lower().endswith(".obj") \
            else path + ".mtl"
    mtl_name = mtl_path.replace("\\", "/").rsplit("/", 1)[-1]

    palette = []
    seen = {}
    for c in M.C:
        if c not in seen:
            seen[c] = _material_name(c)
            palette.append(c)

    with open(path, "w") as f:
        f.write("# written by add.py %s\n" % __version__)
        f.write("mtllib %s\n" % mtl_name)
        f.write("o model\n")
        out = []
        for p in M.V:
            out.append("v %s %s %s\n" % (_num(p[0]), _num(p[1]), _num(p[2])))
        f.write("".join(out))
        # Texture coordinates, one line per distinct (u, v) of textured faces.
        vt_index = {}
        if M.UV is not None:
            out = []
            for k, c in enumerate(M.C):
                uv = M.UV[k]
                if uv is None or len(c) < 5:
                    continue
                for t in uv:
                    key = (round(t[0], 6), round(t[1], 6))
                    if key not in vt_index:
                        vt_index[key] = len(vt_index) + 1
                        out.append("vt %s %s\n" % (_num(key[0]), _num(key[1])))
            f.write("".join(out))
        # Group faces by colour: one `usemtl` line per colour, not per face.
        by_color = {}
        for k, (face, c) in enumerate(zip(M.F, M.C)):
            by_color.setdefault(c, []).append(k)
        for c in palette:
            f.write("usemtl %s\n" % seen[c])
            out = []
            textured = len(c) > 4 and M.UV is not None
            for k in by_color[c]:
                face = M.F[k]
                uv = M.UV[k] if textured else None
                if uv is None:
                    out.append("f %s\n" % " ".join(str(i + 1) for i in face))
                else:
                    out.append("f %s\n" % " ".join(
                        "%d/%d" % (i + 1, vt_index[(round(t[0], 6), round(t[1], 6))])
                        for i, t in zip(face, uv)))
            f.write("".join(out))

    with open(mtl_path, "w") as f:
        f.write("# written by add.py %s\n" % __version__)
        for c in palette:
            r, g, b, alpha, image = _material(c)
            f.write("newmtl %s\n" % seen[c])
            f.write("Kd %.6f %.6f %.6f\n" % (r / 255.0, g / 255.0, b / 255.0))
            f.write("Ka 0.100000 0.100000 0.100000\n")
            f.write("Ks 0.000000 0.000000 0.000000\n")
            f.write("d %.3f\n" % alpha)
            f.write("illum 1\n")
            if image:
                f.write("map_Kd %s\n" % image.replace("\\", "/").rsplit("/", 1)[-1])
            f.write("\n")
    return path


def obj_size(M=None):
    """How many bytes :func:`save` would write for this model as ``.obj``
    (the ``.mtl`` file is tiny and not counted).

    Sketchfab's free plan accepts uploads up to 100 MB (200 MB Pro, 500 MB
    Premium); the course asks for models under 50 MB.  The size is worked
    out from the numbers themselves, without writing a file::

        print(add.obj_size() / 1e6, "MB")
    """
    M = as_mesh(M)
    total = 50                                          # header lines
    for p in M.V:
        total += 5 + len(_num(p[0])) + len(_num(p[1])) + len(_num(p[2]))
    seen = set()
    vts = set()
    for k, (face, c) in enumerate(zip(M.F, M.C)):
        total += 2 + len(face)
        textured = len(c) > 4 and M.UV is not None and M.UV[k] is not None
        for i in face:
            total += len(str(i + 1))
        if textured:
            for t in M.UV[k]:
                key = (round(t[0], 6), round(t[1], 6))
                if key not in vts:
                    vts.add(key)
                    total += 6 + len(_num(key[0])) + len(_num(key[1]))
                total += 1 + len(str(len(vts)))           # "/vt" per corner
        if c not in seen:
            seen.add(c)
            total += 20 + (8 if len(c) > 3 else 0) + (10 + len(str(c[4])) if len(c) > 4 else 0)
    return total


def _write_ply(path, M):
    with open(path, "w") as f:
        f.write("ply\nformat ascii 1.0\ncomment add.py %s\n" % __version__)
        f.write("element vertex %d\n" % len(M.V))
        f.write("property float x\nproperty float y\nproperty float z\n")
        f.write("element face %d\n" % len(M.F))
        f.write("property list uchar int vertex_indices\n")
        f.write("property uchar red\nproperty uchar green\nproperty uchar blue\n")
        f.write("end_header\n")
        for p in M.V:
            f.write("%s %s %s\n" % (_num(p[0]), _num(p[1]), _num(p[2])))
        for face, c in zip(M.F, M.C):
            f.write("%d %s %d %d %d\n" % (len(face),
                                          " ".join(str(i) for i in face),
                                          c[0], c[1], c[2]))


def _write_stl(path, M):
    """ASCII STL -- the 3D printing format.  STL has no colours."""
    with open(path, "w") as f:
        f.write("solid addpy\n")
        for face in M.F:
            for t in range(1, len(face) - 1):
                a, b, c = M.V[face[0]], M.V[face[t]], M.V[face[t + 1]]
                n = _unit(_cross(_sub(b, a), _sub(c, a)))
                f.write("facet normal %.6e %.6e %.6e\n" % n)
                f.write("  outer loop\n")
                for p in (a, b, c):
                    f.write("    vertex %.6e %.6e %.6e\n" % (p[0], p[1], p[2]))
                f.write("  endloop\nendfacet\n")
        f.write("endsolid addpy\n")


class Stream(object):
    """Write a model part by part, straight to disk, so that a model far
    bigger than the computer's memory can still be built.

    ``add.stream(path)`` returns one of these.  Every :meth:`add` writes a
    mesh (or the current scene, which is then cleared) to the file at once
    and forgets it; :meth:`close` finishes the file.  Works for ``.obj``
    (materials, opacity and textures included; the ``.mtl`` is written on
    close) and ``.off`` (the counts in the header are filled in on close).
    Use it as a context manager or call ``close()`` yourself::

        with add.stream("castle.obj") as out:
            for i in range(100):
                add.sphere([i, 0, 0], 0.4, 20, "red")
                out.add()                    # the scene, then cleared
            out.add(add.make(add.box, [0, 5, 0], 2, "gold"))
        print(out.faces, "faces,", out.bytes / 1e6, "MB")
    """

    def __init__(self, path):
        self.path = path
        self.faces = 0
        self.vertices = 0
        self.bytes = 0
        self.materials = {}                    # colour tuple -> material name
        self._kind = "obj" if path.lower().endswith(".obj") else "off"
        self._vt = 0
        self._file = open(path, "w")
        if self._kind == "obj":
            mtl = path[:-4] + ".mtl"
            self._mtl = mtl
            self._file.write("# written by add.py %s\n" % __version__)
            self._file.write("mtllib %s\n" % mtl.replace("\\", "/").rsplit("/", 1)[-1])
            self._file.write("o model\n")
        else:
            self._file.write("OFF\n")
            self._header_at = self._file.tell()
            self._file.write("%12d %12d 0\n" % (0, 0))
            self._offV, self._offF = [], []
        self._current = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False

    def add(self, M=None):
        """Write a mesh to the file now.  Without a mesh the current scene is
        written and then cleared.  Returns the number of faces written."""
        if M is None:
            M = _scene
            clear_after = True
        else:
            M = as_mesh(M)
            clear_after = False
        if self._file is None:
            raise ValueError("stream is closed")
        f = self._file
        base = self.vertices
        out = []
        if self._kind == "obj":
            for p in M.V:
                out.append("v %s %s %s\n" % (_num(p[0]), _num(p[1]), _num(p[2])))
            vt_index = {}
            if M.UV is not None:
                for k, c in enumerate(M.C):
                    uv = M.UV[k]
                    if uv is None or len(c) < 5:
                        continue
                    for t in uv:
                        key = (round(t[0], 6), round(t[1], 6))
                        if key not in vt_index:
                            self._vt += 1
                            vt_index[key] = self._vt
                            out.append("vt %s %s\n" % (_num(key[0]), _num(key[1])))
            by_color = {}
            order = []
            for k, c in enumerate(M.C):
                if c not in by_color:
                    by_color[c] = []
                    order.append(c)
                by_color[c].append(k)
            for c in order:
                name = self.materials.get(c)
                if name is None:
                    name = self.materials[c] = _material_name(c)
                if c != self._current:
                    out.append("usemtl %s\n" % name)
                    self._current = c
                textured = len(c) > 4 and M.UV is not None
                for k in by_color[c]:
                    face = M.F[k]
                    uv = M.UV[k] if textured else None
                    if uv is None:
                        out.append("f %s\n" % " ".join(str(i + base + 1) for i in face))
                    else:
                        out.append("f %s\n" % " ".join(
                            "%d/%d" % (i + base + 1,
                                       vt_index[(round(t[0], 6), round(t[1], 6))])
                            for i, t in zip(face, uv)))
            text = "".join(out)
        else:
            # OFF wants every vertex before every face, so the two lists are
            # kept as text and written on close (that is why .obj is the
            # format for really big models).
            for p in M.V:
                self._offV.append("%s %s %s\n" % (_num(p[0]), _num(p[1]), _num(p[2])))
            for face, c in zip(M.F, M.C):
                self._offF.append("%d %s %d %d %d\n" % (
                    len(face), " ".join(str(i + base) for i in face), c[0], c[1], c[2]))
            text = ""
        if text:
            f.write(text)
            self.bytes += len(text)
        self.vertices += len(M.V)
        self.faces += len(M.F)
        if clear_after:
            clear()
        return len(M.F)

    def close(self):
        """Finish the file (the ``.mtl``, or the OFF header)."""
        if self._file is None:
            return self.path
        if self._kind == "obj":
            with open(self._mtl, "w") as m:
                m.write("# written by add.py %s\n" % __version__)
                for c, name in self.materials.items():
                    r, g, b, alpha, image = _material(c)
                    m.write("newmtl %s\n" % name)
                    m.write("Kd %.6f %.6f %.6f\n" % (r / 255.0, g / 255.0, b / 255.0))
                    m.write("Ka 0.100000 0.100000 0.100000\n")
                    m.write("Ks 0.000000 0.000000 0.000000\n")
                    m.write("d %.3f\n" % alpha)
                    m.write("illum 1\n")
                    if image:
                        m.write("map_Kd %s\n" % image.replace("\\", "/").rsplit("/", 1)[-1])
                    m.write("\n")
        else:
            text = "".join(self._offV) + "".join(self._offF)
            self._file.write(text)
            self.bytes += len(text)
            self._file.seek(self._header_at)
            self._file.write("%12d %12d 0\n" % (self.vertices, self.faces))
        self._file.close()
        self._file = None
        return self.path


def stream(path):
    """Open a :class:`Stream`: a model written to ``path`` part by part,
    without ever holding all of it in memory.

    The ordinary :func:`save` keeps the whole model in memory, which is fine
    up to a few million faces.  For a model of hundreds of megabytes -- a
    castle with every brick -- build it in parts and hand each part to the
    stream as soon as it is finished::

        out = add.stream("castle.obj")
        add.bricks([0, 0, 0], 40, 6, [0.5, 0.25, 0.5], "brown", seed=1)
        out.add()                       # writes the scene and clears it
        out.add(add.make(add.tree, [10, 0, 0], 5))
        out.close()                     # writes castle.mtl
        print(out.faces, out.bytes)

    For ``.off`` the vertices and faces are kept as text until ``close()``
    (the format wants all vertices before all faces), so ``.obj`` is the
    one to use for really big models.
    """
    return Stream(path)


def load(path, color=None):
    """Read a model from an ``.off``, ``.obj`` or ``.ply`` file.

    Returns a mesh you can transform and ``mesh()`` into the scene::

        letter = add.load("letters/A.off")
        add.mesh(add.move(add.zoom(letter, 0.1), [0, 2, 0]))
    """
    ext = path.lower().rsplit(".", 1)[-1] if "." in path else "off"
    if ext == "obj":
        M = _read_obj(path, color)
    elif ext == "ply":
        M = _read_ply(path, color)
    else:
        M = _read_off(path, color)
    return M


def _clean_lines(path):
    """Non-empty lines of a file with ``#`` comments stripped."""
    out = []
    with open(path, "r") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if line:
                out.append(line)
    return out


def _read_off(path, color=None):
    """Read an OFF file.  Colours may be missing, integer or 0..1 floats."""
    lines = _clean_lines(path)
    if not lines:
        return Mesh()
    row = 0
    head = lines[0].split()
    if head[0].upper().endswith("OFF"):
        row = 1
        if len(head) >= 3:                 # counts on the same line as OFF
            counts = head[1:]
        else:
            counts = lines[1].split()
            row = 2
    else:
        counts = head
        row = 1
    nv, nf = int(counts[0]), int(counts[1])

    M = Mesh()
    for _ in range(nv):
        p = lines[row].split()
        row += 1
        M.add_vertex((float(p[0]), float(p[1]), float(p[2])))

    default = rgb(color) if color is not None else DEFAULT_COLOR
    for _ in range(nf):
        p = lines[row].split()
        row += 1
        n = int(p[0])
        face = [int(x) for x in p[1:1 + n]]
        rest = p[1 + n:]
        c = default
        if len(rest) >= 3 and color is None:
            vals = [float(x) for x in rest[:3]]
            if max(vals) <= 1.0 and any(v != int(v) for v in vals):
                vals = [v * 255.0 for v in vals]
            c = rgb(vals)
        M.add_face(face, c)
    return M


def _read_obj(path, color=None):
    M = Mesh()
    materials = {}
    current = rgb(color) if color is not None else DEFAULT_COLOR
    folder = path.replace("\\", "/").rsplit("/", 1)
    folder = folder[0] + "/" if len(folder) > 1 else ""
    vt = []
    with open(path, "r") as f:
        for line in f:
            parts = line.split()
            if not parts or parts[0].startswith("#"):
                continue
            tag = parts[0]
            if tag == "v":
                M.add_vertex((float(parts[1]), float(parts[2]),
                              float(parts[3])))
            elif tag == "vt":
                vt.append((float(parts[1]), float(parts[2]) if len(parts) > 2
                           else 0.0))
            elif tag == "f":
                face = []
                uv = []
                for p in parts[1:]:
                    bits = p.split("/")
                    idx = int(bits[0])
                    face.append(idx - 1 if idx > 0 else len(M.V) + idx)
                    if len(bits) > 1 and bits[1]:
                        t = int(bits[1])
                        uv.append(vt[t - 1 if t > 0 else len(vt) + t])
                textured = len(current) > 4 and len(uv) == len(face)
                M.add_face(face, current, uv if textured else None)
            elif tag == "mtllib" and color is None:
                try:
                    materials.update(_read_mtl(folder + parts[1]))
                except IOError:
                    pass
            elif tag == "usemtl" and color is None:
                current = materials.get(parts[1], DEFAULT_COLOR)
    return M


def _read_mtl(path):
    """``{material name: colour}``, with opacity (``d`` / ``Tr``) and the
    texture image (``map_Kd``) kept in the colour tuple."""
    out = {}
    name = None
    with open(path, "r") as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue
            if parts[0] == "newmtl":
                name = parts[1]
                out[name] = DEFAULT_COLOR
            elif name is None:
                continue
            elif parts[0] == "Kd":
                c = out[name]
                out[name] = rgb([float(parts[1]) * 255, float(parts[2]) * 255,
                                 float(parts[3]) * 255] + list(c[3:]))
            elif parts[0] in ("d", "Tr") and len(parts) > 1:
                alpha = float(parts[1])
                if parts[0] == "Tr":
                    alpha = 1.0 - alpha
                c = out[name]
                out[name] = rgb((c[0], c[1], c[2], alpha) + tuple(c[4:5]))
            elif parts[0] == "map_Kd" and len(parts) > 1:
                c = out[name]
                out[name] = rgb((c[0], c[1], c[2], c[3] if len(c) > 3 else 1.0,
                                 parts[-1]))
    return out


def write_png(path, rows):
    """Write a picture -- a list of rows, each a list of colours -- as a
    ``.png``, to use as a texture (see :func:`texture`).

    Row 0 is the top of the picture.  Any colour form that :func:`rgb`
    accepts works, so a 64 x 64 chequerboard is::

        rows = [["white" if (x // 8 + y // 8) % 2 else "black"
                 for x in range(64)] for y in range(64)]
        add.write_png("check.png", rows)
    """
    import struct
    import zlib
    height = len(rows)
    width = len(rows[0]) if height else 0
    raw = bytearray()
    for row in rows:
        raw.append(0)                                   # filter type "none"
        for c in row:
            c = rgb(c)
            raw.append(c[0])
            raw.append(c[1])
            raw.append(c[2])

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


def _read_ply(path, color=None):
    with open(path, "r") as f:
        text = f.read().split("\n")
    nv = nf = 0
    head = 0
    props = []
    element = None
    for i, line in enumerate(text):
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "element":
            element = parts[1]
            if element == "vertex":
                nv = int(parts[2])
            elif element == "face":
                nf = int(parts[2])
        elif parts[0] == "property" and element == "vertex":
            props.append(parts[-1])
        elif parts[0] == "end_header":
            head = i + 1
            break
    M = Mesh()
    row = head
    for _ in range(nv):
        vals = text[row].split()
        row += 1
        d = dict(zip(props, vals))
        M.add_vertex((float(d.get("x", 0)), float(d.get("y", 0)),
                      float(d.get("z", 0))))
    default = rgb(color) if color is not None else DEFAULT_COLOR
    for _ in range(nf):
        vals = text[row].split()
        row += 1
        n = int(vals[0])
        face = [int(v) for v in vals[1:1 + n]]
        c = default
        if len(vals) >= 1 + n + 3 and color is None:
            c = rgb([float(v) for v in vals[1 + n:4 + n]])
        M.add_face(face, c)
    return M


def load_font(folder, characters=None, suffix=".off"):
    """Load a whole folder of letter or digit models into a dictionary.

    ``add.load_font("letters")`` gives ``{"A": mesh, "B": mesh, ...}`` so a
    word can be written with a loop instead of one ``load`` per character.
    """
    import os
    out = {}
    names = characters
    if names is None:
        try:
            names = [n[:-len(suffix)] for n in os.listdir(folder)
                     if n.endswith(suffix)]
        except OSError:
            return out
    for name in names:
        try:
            out[name] = load(os.path.join(folder, name + suffix))
        except (IOError, OSError, ValueError):
            pass
    return out


def typeset(characters, font, at=(0, 0, 0), size=1.0, spacing=1.0, color=None,
            plane=((1, 0, 0), (0, 1, 0))):
    """Lay a string of already-loaded glyph *meshes* out in a row and merge them.

    ``font`` is the dictionary returned by :func:`load_font` -- letters that
    were modelled as .off files, like the course's letter set.  (For a
    quick label drawn from add.py's own built-in font see :func:`text`.)
    """
    u, v = plane
    out = Mesh()
    x = 0.0
    for ch in characters:
        glyph_mesh = font.get(ch) or font.get(ch.upper())
        if glyph_mesh is None:
            x += spacing
            continue
        G = fit(as_mesh(glyph_mesh), size)
        G = place(G, (0, 0, 0))
        pos = (at[0] + u[0] * x * spacing * size,
               at[1] + u[1] * x * spacing * size,
               at[2] + u[2] * x * spacing * size)
        G = move(G, pos)
        if color is not None:
            G = _paint(G, color)
        out.extend(G)
        x += 1.0
    return out

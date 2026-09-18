

# ============================================================================
# 18. Saving and loading
# ============================================================================

def save(path, M=None, clear_scene=None):
    """Write a model to disk; the file format follows the extension.

    ``.off`` (the course format), ``.obj`` (+ a ``.mtl`` colour file, which is
    what Sketchfab and most other tools want), ``.ply`` or ``.stl``::

        add.save("dragon.obj")

    Called without a mesh it saves -- and then empties -- the current scene,
    exactly like add.py 1.2's ``off()``.
    """
    if clear_scene is None:
        clear_scene = M is None
    mesh_to_save = as_mesh(M)
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


def _write_obj(path, M, mtl_path=None):
    if mtl_path is None:
        mtl_path = path[:-4] + ".mtl" if path.lower().endswith(".obj") \
            else path + ".mtl"
    mtl_name = mtl_path.replace("\\", "/").rsplit("/", 1)[-1]

    palette = []
    seen = {}
    for c in M.C:
        if c not in seen:
            seen[c] = "color_%02x%02x%02x" % c
            palette.append(c)

    with open(path, "w") as f:
        f.write("# written by add.py %s\n" % __version__)
        f.write("mtllib %s\n" % mtl_name)
        f.write("o model\n")
        out = []
        for p in M.V:
            out.append("v %s %s %s\n" % (_num(p[0]), _num(p[1]), _num(p[2])))
        f.write("".join(out))
        # Group faces by colour: one `usemtl` line per colour, not per face.
        by_color = {}
        for face, c in zip(M.F, M.C):
            by_color.setdefault(c, []).append(face)
        for c in palette:
            f.write("usemtl %s\n" % seen[c])
            out = []
            for face in by_color[c]:
                out.append("f %s\n" % " ".join(str(i + 1) for i in face))
            f.write("".join(out))

    with open(mtl_path, "w") as f:
        f.write("# written by add.py %s\n" % __version__)
        for c in palette:
            f.write("newmtl %s\n" % seen[c])
            f.write("Kd %.6f %.6f %.6f\n" % (c[0] / 255.0, c[1] / 255.0,
                                             c[2] / 255.0))
            f.write("Ka 0.100000 0.100000 0.100000\n")
            f.write("Ks 0.000000 0.000000 0.000000\n")
            f.write("d 1.0\nillum 1\n\n")
    return path


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
    with open(path, "r") as f:
        for line in f:
            parts = line.split()
            if not parts or parts[0].startswith("#"):
                continue
            tag = parts[0]
            if tag == "v":
                M.add_vertex((float(parts[1]), float(parts[2]),
                              float(parts[3])))
            elif tag == "f":
                face = []
                for p in parts[1:]:
                    idx = int(p.split("/")[0])
                    face.append(idx - 1 if idx > 0 else len(M.V) + idx)
                M.add_face(face, current)
            elif tag == "mtllib" and color is None:
                try:
                    materials.update(_read_mtl(folder + parts[1]))
                except IOError:
                    pass
            elif tag == "usemtl" and color is None:
                current = materials.get(parts[1], DEFAULT_COLOR)
    return M


def _read_mtl(path):
    out = {}
    name = None
    with open(path, "r") as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue
            if parts[0] == "newmtl":
                name = parts[1]
            elif parts[0] == "Kd" and name:
                out[name] = rgb([float(parts[1]) * 255, float(parts[2]) * 255,
                                 float(parts[3]) * 255])
    return out


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


def text(characters, font, at=(0, 0, 0), size=1.0, spacing=1.0, color=None,
         plane=((1, 0, 0), (0, 1, 0))):
    """Lay a string of already-loaded glyphs out in a row and merge them.

    ``font`` is the dictionary returned by :func:`load_font`.
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

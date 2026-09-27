// ============================================================================
//  17. Saving and loading
//      (add.py: _src/70_io.py)
// ============================================================================
// (Reading a font folder needs the file system library of C++17.)
#include <cerrno>
#include <filesystem>
#include <iterator>
#include <system_error>

namespace add {

namespace detail {
//: The mesh itself, or a copy fit to be written: no face visits a vertex twice,
//: no coordinate is not a number.
inline Mesh writable(const Mesh& M);
//: The face lines of an OFF file (each face cut to at most four corners).
inline std::vector<std::string> off_face_lines(const Mesh& M, long long base = 0);
//: The pieces an OFF file carries face f as: triangles and quadrilaterals.
inline std::vector<Face> off_pieces(const Mesh& M, const Face& f);
//: ``color_rrggbb`` (+ ``_aNNN`` see-through, ``_tNAME`` textured): a material name.
inline std::string material_name(const Color& c);
inline void write_off(const std::string& path, const Mesh& M);
inline void write_obj(const std::string& path, const Mesh& M, std::optional<std::string> mtl_path = std::nullopt);
inline void write_ply(const std::string& path, const Mesh& M);
inline void write_stl(const std::string& path, const Mesh& M);
//: Is ``M`` the current scene itself?  (save, off, obj and Stream::add then empty it after
//: writing, as add.py does when no mesh is given.)
inline bool is_scene(const Mesh& M) { return &M == &current(); }
//: ``x`` with ``decimals`` decimals, trailing zeros and point dropped, "" and "-0" written as "0"
//: (add.py's ``_rounded(decimals)(x)``, the number format of a Stream with a ``precision``).
inline std::string rounded(double x, int decimals);

// -- reading files as Python reads them ---------------------------------------
// Python's exceptions are these C++ ones here: ValueError -> std::invalid_argument, IndexError
// and KeyError -> std::out_of_range, OverflowError -> std::overflow_error, OSError (a file that
// cannot be opened) -> std::system_error.  load_font() skips a file on the first and the last,
// as add.py does.

//: The text of a file as Python's ``open(path).read()`` gives it: UTF-8 (a file that is not
//: is a ValueError), with "\r\n" and "\r" read as "\n"; a missing file or a folder: OSError.
inline std::string read_text(const std::string& path);
//: Python's ``s.split(sep)`` with a one-character separator.
inline std::vector<std::string> split_on(const std::string& s, char sep);
//: Python's ``s.split()`` and ``s.strip()`` -- Python's whitespace: also \x1c..\x1f and the
//: Unicode spaces U+0085, U+00A0, U+1680, U+2000..U+200A, U+2028, U+2029, U+202F, U+205F, U+3000.
inline std::vector<std::string> py_split(const std::string& s);
inline std::string py_strip(const std::string& s);
//: Python's ``float(word)`` and ``int(word)`` of one word of a file: std::invalid_argument
//: (ValueError) for anything Python refuses -- hexadecimal, "1e", "1__0" ...  (Digits other
//: than 0-9 are refused, which Python would take; an int beyond 64 bits stops at the limit.)
inline double py_float(const std::string& word);
inline long long py_int(const std::string& word);
//: The characters (code points) of a UTF-8 string, each as a string (Python's ``for ch in s``).
inline std::vector<std::string> utf8_chars(const std::string& s);
//: Python's ``s.upper()`` for the letters of Latin-1, Latin Extended-A, Greek and Cyrillic
//: (U+0000..U+017F, U+0370..U+052F; the sharp s becomes SS); any other character stays as it is.
inline std::string py_upper(const std::string& s);
//: add.py's ``rgb()`` of a list of 3 or 4 floats read from a file (the fourth: the opacity);
//: a NaN is a ValueError and an infinity an OverflowError there, as in Python.
inline Color rgb_list(const std::vector<double>& color);
//: The non-empty lines of a file with ``#`` comments stripped (add.py's ``_clean_lines``).
inline std::vector<std::string> clean_lines(const std::string& path);
//: The readers behind load(): .off, .obj (with its .mtl), .ply.
inline Mesh read_off(const std::string& path, const std::optional<Color>& color = std::nullopt);
inline Mesh read_obj(const std::string& path, const std::optional<Color>& color = std::nullopt);
//: {material name: colour}, the opacity (``d`` / ``Tr``) and texture (``map_Kd``) included.
inline std::map<std::string, Color> read_mtl(const std::string& path);
inline Mesh read_ply(const std::string& path, const std::optional<Color>& color = std::nullopt);
}  // namespace detail

//: Write a model to disk; the file format follows the extension: .off, .obj (+ .mtl),
//: .ply or .stl.  ``save(path)`` saves -- and then empties -- the current scene.  The scene
//: passed as the mesh counts as no mesh, so that add.py's ``add.save("m.obj", colors=50)``
//: is ``add::save("m.obj", add::scene(), {}, 50)``; ``clear_scene = false`` keeps it.
//: ``colors``: reduce the model to at most that many colours first; ``clean``: tidy it
//: on the way out (see clean()).
inline std::string save(const std::string& path, const Mesh& M, std::optional<bool> clear_scene = std::nullopt,
                        std::optional<int> colors = std::nullopt, bool clean = true);
inline std::string save(const std::string& path);
//: Write an OFF file exactly as the model is (and empty the scene) -- the add.py 1.2 behaviour.
inline std::string off(const std::string& path, const Mesh& M);
inline std::string off(const std::string& path);
//: Write an OBJ file plus the matching MTL colour file.
inline std::string obj(const std::string& path, const Mesh& M, std::optional<std::string> mtl = std::nullopt);
inline std::string obj(const std::string& path);
//: How many bytes save() would write for this model as .obj.
inline long long obj_size(const Mesh& M);
inline long long obj_size();

//: Write a model part by part, straight to disk (.obj or .off), so that a model far
//: bigger than the computer's memory can still be built (see add.py's Stream):
//:
//:     auto out = add::stream("castle.obj");
//:     add::sphere({0, 0, 0}, 0.4, 20, "red");
//:     out->add();                          // the scene, then cleared
//:     out->add(add::make([] { add::box({0, 5, 0}, 2, "gold"); }));
//:     out->close();                        // (the destructor closes it too)
//:
//: ``precision``: the decimals of every coordinate; ``faces``, ``vertices``, ``bytes`` (the
//: characters written), ``removed`` and ``cut`` (what the tidying did) count as it goes.
class Stream {
  public:
    std::string path;
    bool clean_parts = true;                                   // (add.py: ``clean``)
    std::optional<int> precision;
    long long faces = 0, vertices = 0, bytes = 0, removed = 0, cut = 0;
    std::vector<std::pair<Color, std::string>> materials;     // in the order they came

    Stream(const std::string& path, bool clean = true, std::optional<int> precision = std::nullopt);
    ~Stream();
    Stream(const Stream&) = delete;
    Stream& operator=(const Stream&) = delete;
    //: Write a mesh now (``clean`` overrides the stream's setting); the number of faces written.
    //: The scene itself (add::scene()) is written and then cleared, as by add().
    long long add(const Mesh& M, std::optional<bool> clean = std::nullopt);
    //: Write the current scene now and clear it.
    long long add();
    //: Finish the file (the .mtl, or the OFF header).
    std::string close();

  private:
    std::string kind_, mtl_, vertices_path_, faces_path_;
    std::ofstream file_, faces_file_;
    bool open_ = false, has_current_ = false;
    Color current_;
    long long vt_ = 0;
    std::unordered_map<Color, std::string, ColorHash> material_index_;   // materials, to look up
    std::string num(double x) const;
};
//: Open a Stream: a model written to ``path`` part by part.
inline std::unique_ptr<Stream> stream(const std::string& path, bool clean = true,
                                      std::optional<int> precision = std::nullopt);

//: Read a model from an .off, .obj or .ply file (``color`` for faces without one).
inline Mesh load(const std::string& path, std::optional<Color> color = std::nullopt);
//: Write a picture -- rows of colours, row 0 at the top -- as a PNG file (to use as a texture).
//: (add.py compresses the pixels with zlib; add.hpp stores them uncompressed: another file,
//: the same picture.)
inline std::string write_png(const std::string& path, const std::vector<std::vector<Color>>& rows);
//: Load a whole folder of letter or digit models: {character: mesh}.  ``characters``: the ones
//: to load (every UTF-8 character one file; or a list of names); std::nullopt: every file
//: ending in ``suffix``.  A file that cannot be read is left out.
inline std::map<std::string, Mesh> load_font(const std::string& folder,
                                             std::optional<std::string> characters = std::nullopt,
                                             const std::string& suffix = ".off");
inline std::map<std::string, Mesh> load_font(const std::string& folder, const std::vector<std::string>& characters,
                                             const std::string& suffix = ".off");
//: Lay a string of already-loaded glyph meshes out in a row and merge them.
inline Mesh typeset(const std::string& characters, const std::map<std::string, Mesh>& font,
                    const Point& at = {0, 0, 0}, double size = 1.0, double spacing = 1.0,
                    std::optional<Color> color = std::nullopt,
                    const std::array<Point, 2>& plane = {Point{1, 0, 0}, Point{0, 1, 0}});

}  // namespace add
//@@definitions
namespace add {

namespace detail {

//: (face, uv) for every face, a face pinched at a vertex split into loops.
struct SafeFace { Face face; Color color; std::vector<Point2> uv; };
inline std::vector<SafeFace> safe_faces(const Mesh& M) {
    std::vector<SafeFace> out;
    for (size_t k = 0; k < M.F.size(); ++k) {
        const Face& face = M.F[k];
        const Color& c = M.C[k];
        const std::vector<Point2>* uv = M.has_uv && !M.UV[k].empty() ? &M.UV[k] : nullptr;
        std::set<int> distinct(face.begin(), face.end());
        if (distinct.size() == face.size()) {
            out.push_back({face, c, uv ? *uv : std::vector<Point2>()});
            continue;
        }
        for (auto& piece : split_repeats(face, uv)) {
            std::set<int> d2(piece.first.begin(), piece.first.end());
            if (piece.first.size() >= 3 && d2.size() >= 3) out.push_back({piece.first, c, piece.second});
        }
    }
    return out;
}

inline Mesh writable(const Mesh& M) {
    std::set<int> bad = not_finite(M);
    bool repeats = false;
    for (const Face& f : M.F) {
        std::set<int> distinct(f.begin(), f.end());
        if (distinct.size() != f.size()) { repeats = true; break; }
    }
    if (bad.empty() && !repeats) return M;
    Mesh out;
    out.V = M.V;
    out.has_uv = M.has_uv;
    for (SafeFace& s : safe_faces(M)) {
        out.F.push_back(s.face);
        out.C.push_back(s.color);
        if (out.has_uv) out.UV.push_back(s.uv);
    }
    if (!bad.empty()) drop_not_finite(out);                    // its faces go, and it is not written either
    return out;
}

//: Is corner b of a 2D outline no corner at all -- on a straight side?
inline bool off_straight(const Point2& a, const Point2& b, const Point2& c) {
    double dx = c[0] - a[0], dy = c[1] - a[1];
    double cr = dx * (b[1] - a[1]) - dy * (b[0] - a[0]);
    return std::fabs(cr) <= 1e-5 * std::sqrt(dx * dx + dy * dy);
}

//: Twice the signed area of the triangle a b c (positive when it turns left at b).
inline double off_turn(const Point2& a, const Point2& b, const Point2& c) {
    return (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0]);
}

inline bool off_convex(const Profile& pts, const std::vector<int>& ring_) {
    int k = (int)ring_.size();
    for (int i = 0; i < k; ++i) {
        const Point2& a = pts[ring_[(i + k - 1) % k]];
        const Point2& b = pts[ring_[i]];
        const Point2& c = pts[ring_[(i + 1) % k]];
        if (off_turn(a, b, c) <= 0 || off_straight(a, b, c)) return false;
    }
    return true;
}

inline std::vector<Face> off_pieces(const Mesh& M, const Face& f) {
    int k = (int)f.size();
    if (k <= 4) return {f};
    Frame fr = frame(face_normal(M, f));
    Profile pts;
    for (int i : f) pts.push_back({dot(M.V[i], fr.u), dot(M.V[i], fr.v)});
    bool flip = poly_area2(pts) < 0;
    if (flip) std::reverse(pts.begin(), pts.end());            // work counter-clockwise
    std::vector<int> ring_(k);
    std::iota(ring_.begin(), ring_.end(), 0);
    std::vector<std::vector<int>> pieces;
    if (off_convex(pts, ring_)) {
        for (int i = 1; i < k - 2; i += 2) pieces.push_back({0, i, i + 1, i + 2});
        if (k % 2) pieces.push_back({0, k - 2, k - 1});
    } else {
        std::vector<std::array<int, 3>> tris;
        while (ring_.size() > 3) {
            int n = (int)ring_.size();
            bool cut_one = false;
            for (int j = 0; j < n; ++j) {
                int i0 = ring_[(j + n - 1) % n], i1 = ring_[j], i2 = ring_[(j + 1) % n];
                const Point2 &a = pts[i0], &b = pts[i1], &c = pts[i2];
                if (off_turn(a, b, c) <= 0 || off_straight(a, b, c)) continue;    // a reflex or straight corner
                bool inside_ = false;                                               // another corner inside?
                for (int q : ring_) {
                    if (q == i0 || q == i1 || q == i2) continue;
                    if (off_turn(a, b, pts[q]) >= 0 && off_turn(b, c, pts[q]) >= 0 && off_turn(c, a, pts[q]) >= 0) {
                        inside_ = true;
                        break;
                    }
                }
                if (inside_) continue;
                tris.push_back({i0, i1, i2});
                ring_.erase(ring_.begin() + j);
                cut_one = true;
                break;
            }
            if (!cut_one) {                                    // no ear (an outline that crosses itself):
                for (size_t j = 1; j + 1 < ring_.size(); ++j)   // the rest as a fan, as a viewer would draw it
                    tris.push_back({ring_[0], ring_[j], ring_[j + 1]});
                ring_.clear();
                break;
            }
        }
        if (!ring_.empty()) tris.push_back({ring_[0], ring_[1], ring_[2]});
        std::map<std::pair<int, int>, int> edge;
        for (size_t t = 0; t < tris.size(); ++t)
            for (int j = 0; j < 3; ++j) edge[{tris[t][j], tris[t][(j + 1) % 3]}] = (int)t;
        std::vector<char> used(tris.size(), 0);
        for (size_t t = 0; t < tris.size(); ++t) {
            if (used[t]) continue;
            used[t] = 1;
            const auto& tri = tris[t];
            std::vector<int> piece(tri.begin(), tri.end());
            for (int j = 0; j < 3; ++j) {                       // a neighbour across one side, together convex?
                int p = tri[j], q = tri[(j + 1) % 3], r = tri[(j + 2) % 3];
                auto it = edge.find({q, p});
                if (it == edge.end() || used[it->second]) continue;
                int s2 = it->second;
                int d = -1;
                for (int x : tris[s2])
                    if (x != p && x != q) { d = x; break; }
                std::vector<int> quad_{q, r, p, d};
                if (off_convex(pts, quad_)) {
                    used[s2] = 1;
                    piece = quad_;
                    break;
                }
            }
            pieces.push_back(piece);
        }
    }
    std::vector<Face> out;
    for (const std::vector<int>& piece : pieces) {
        Face face;
        for (int i : piece) face.push_back(flip ? f[k - 1 - i] : f[i]);
        if (flip) std::reverse(face.begin(), face.end());
        out.push_back(face);
    }
    return out;
}

//: The corners of a face as an .off / .ply / .obj line lists them: " ".join(str(i + shift)).
inline std::string corner_list(const Face& face, long long shift) {
    std::string s;
    for (size_t j = 0; j < face.size(); ++j) {
        if (j) s += " ";
        s += std::to_string(face[j] + shift);
    }
    return s;
}

inline std::vector<std::string> off_face_lines(const Mesh& M, long long base) {
    std::vector<std::string> lines;
    for (size_t q = 0; q < M.F.size(); ++q) {
        const Color& c = M.C[q];
        std::string tail = c.alpha < 1.0
                               ? fmt(" %d %d %d %d\n", c.r, c.g, c.b, (int)std::nearbyint(c.alpha * 255))
                               : fmt(" %d %d %d\n", c.r, c.g, c.b);
        for (const Face& piece : off_pieces(M, M.F[q]))            // "%d %s%s" (a face without
            lines.push_back(std::to_string(piece.size()) + " " + corner_list(piece, base) + tail);   // corners: "0  r g b")
    }
    return lines;
}

inline std::ofstream open_out(const std::string& path) {
    std::ofstream f(path, std::ios::out | std::ios::binary | std::ios::trunc);
    if (!f) throw std::runtime_error("cannot write " + path);
    return f;
}

inline void write_off(const std::string& path, const Mesh& M0) {
    Mesh M = writable(M0);
    std::vector<std::string> faces = off_face_lines(M);
    std::ofstream f = open_out(path);
    std::string out = "OFF\n" + std::to_string(M.V.size()) + " " + std::to_string(faces.size()) + " 0\n";
    for (const Point& p : M.V) out += num(p[0]) + " " + num(p[1]) + " " + num(p[2]) + "\n";
    f << out;
    for (const std::string& line : faces) f << line;
}

inline std::string file_stem(const std::string& image) {
    std::string s = image;
    std::replace(s.begin(), s.end(), '\\', '/');
    size_t slash = s.rfind('/');
    if (slash != std::string::npos) s = s.substr(slash + 1);
    return s;
}

inline std::string material_name(const Color& c) {
    std::string name = fmt("color_%02x%02x%02x", c.r, c.g, c.b);
    if (c.alpha < 1.0) name += fmt("_a%03d", (int)std::nearbyint(c.alpha * 1000));
    if (!c.image.empty()) {
        std::string stem = file_stem(c.image);
        size_t dot_ = stem.rfind('.');
        if (dot_ != std::string::npos) stem = stem.substr(0, dot_);
        name += "_t";
        for (char ch : stem)                                   // (non-ASCII letters are kept, as Python's
            name += ((unsigned char)ch >= 0x80 || std::isalnum((unsigned char)ch)) ? ch : '_';   // isalnum does)
    }
    return name;
}

//: A texture coordinate as an .obj file keys it: (round(u, 6), round(v, 6)).
inline std::pair<double, double> uv_key(const Point2& t) { return {py_round(t[0], 6), py_round(t[1], 6)}; }
//: Is ``key`` already in ``index``?  (A NaN never is: Python's dict does not find it again,
//: and _num then raises.)
template <class Index>
inline bool known_uv(const Index& index, const std::pair<double, double>& key) {
    return !std::isnan(key.first) && !std::isnan(key.second) && index.count(key) > 0;
}

//: An "f" line of an .obj file: the corners (numbered from ``shift``) and, for a textured
//: face, "corner/texture" pairs -- as many as both lists have (Python's zip).
template <class Index>
inline std::string obj_face_line(const Face& face, const std::vector<Point2>* uv, long long shift, Index& vt_index) {
    if (!uv) return "f " + corner_list(face, shift) + "\n";
    std::string s = "f ";
    for (size_t j = 0; j < face.size() && j < uv->size(); ++j) {
        if (j) s += " ";
        s += std::to_string(face[j] + shift) + "/" + std::to_string(vt_index[uv_key((*uv)[j])]);
    }
    return s + "\n";
}

inline void write_obj(const std::string& path, const Mesh& M0, std::optional<std::string> mtl_path) {
    Mesh M = writable(M0);
    std::string mtl;
    if (mtl_path) mtl = *mtl_path;
    else if (path.size() >= 4 && lower(path.substr(path.size() - 4)) == ".obj") mtl = path.substr(0, path.size() - 4) + ".mtl";
    else mtl = path + ".mtl";
    std::string mtl_name = file_stem(mtl);

    std::vector<Color> palette_;
    std::unordered_map<Color, std::string, ColorHash> seen;
    for (const Color& c : M.C)
        if (!seen.count(c)) {
            seen[c] = material_name(c);
            palette_.push_back(c);
        }
    std::ofstream f = open_out(path);
    std::string out = "# written by add.py " + version + "\n" + "mtllib " + mtl_name + "\n" + "o model\n";
    for (const Point& p : M.V) out += "v " + num(p[0]) + " " + num(p[1]) + " " + num(p[2]) + "\n";
    f << out;
    // Texture coordinates, one line per distinct (u, v) of textured faces.
    std::map<std::pair<double, double>, int> vt_index;
    if (M.has_uv) {
        out.clear();
        for (size_t k = 0; k < M.C.size(); ++k) {
            const std::vector<Point2>& uv = M.UV[k];
            if (uv.empty() || M.C[k].image.empty()) continue;
            for (const Point2& t : uv) {
                std::pair<double, double> key = uv_key(t);
                if (!known_uv(vt_index, key)) {
                    vt_index[key] = (int)vt_index.size() + 1;
                    std::string u = num(key.first);            // (u first: Python's order)
                    std::string v = num(key.second);
                    out += "vt " + u + " " + v + "\n";
                }
            }
        }
        f << out;
    }
    // Group faces by colour: one ``usemtl`` line per colour, not per face.
    std::unordered_map<Color, std::vector<size_t>, ColorHash> by_color;
    for (size_t k = 0; k < M.F.size(); ++k) by_color[M.C[k]].push_back(k);
    for (const Color& c : palette_) {
        f << "usemtl " << seen[c] << "\n";
        out.clear();
        bool textured = !c.image.empty() && M.has_uv;
        for (size_t k : by_color[c])
            out += obj_face_line(M.F[k], textured && !M.UV[k].empty() ? &M.UV[k] : nullptr, 1, vt_index);
        f << out;
    }
    f.close();

    std::ofstream m = open_out(mtl);
    m << "# written by add.py " << version << "\n";
    for (const Color& c : palette_) {
        m << "newmtl " << seen[c] << "\n";
        m << fmt("Kd %.6f %.6f %.6f\n", c.r / 255.0, c.g / 255.0, c.b / 255.0);
        m << "Ka 0.100000 0.100000 0.100000\n";
        m << "Ks 0.000000 0.000000 0.000000\n";
        m << fmt("d %.3f\n", c.alpha);
        m << "illum 1\n";
        if (!c.image.empty()) m << "map_Kd " << file_stem(c.image) << "\n";
        m << "\n";
    }
}

inline void write_ply(const std::string& path, const Mesh& M0) {
    Mesh M = writable(M0);
    std::ofstream f = open_out(path);
    std::string out = "ply\nformat ascii 1.0\ncomment add.py " + version + "\n";
    out += "element vertex " + std::to_string(M.V.size()) + "\n";
    out += "property float x\nproperty float y\nproperty float z\n";
    out += "element face " + std::to_string(M.F.size()) + "\n";
    out += "property list uchar int vertex_indices\n";
    out += "property uchar red\nproperty uchar green\nproperty uchar blue\n";
    out += "end_header\n";
    for (const Point& p : M.V) out += num(p[0]) + " " + num(p[1]) + " " + num(p[2]) + "\n";
    f << out;
    out.clear();
    for (size_t k = 0; k < M.F.size(); ++k) {
        const Color& c = M.C[k];
        out += std::to_string(M.F[k].size()) + " " + corner_list(M.F[k], 0) + fmt(" %d %d %d\n", c.r, c.g, c.b);
    }
    f << out;
}

//: Python's ``"%.6e" % x`` (printf's, except that a NaN is "nan" whatever its sign).
inline std::string sci6(double x) {
    if (std::isnan(x)) return "nan";
    return fmt("%.6e", x);
}

inline void write_stl(const std::string& path, const Mesh& M0) {
    Mesh M = writable(M0);
    std::ofstream f = open_out(path);
    std::string out = "solid addpy\n";
    for (const Face& face : M.F) {
        for (size_t t = 1; t + 1 < face.size(); ++t) {
            const Point& a = M.V[face[0]];
            const Point& b = M.V[face[t]];
            const Point& c = M.V[face[t + 1]];
            Point n = unit(cross(sub(b, a), sub(c, a)));
            out += "facet normal " + sci6(n[0]) + " " + sci6(n[1]) + " " + sci6(n[2]) + "\n";
            out += "  outer loop\n";
            for (const Point* p : {&a, &b, &c})
                out += "    vertex " + sci6((*p)[0]) + " " + sci6((*p)[1]) + " " + sci6((*p)[2]) + "\n";
            out += "  endloop\nendfacet\n";
        }
        if (out.size() > (1u << 20)) {
            f << out;
            out.clear();
        }
    }
    out += "endsolid addpy\n";
    f << out;
}

inline std::string rounded(double x, int decimals) {
    if (decimals < 0) throw std::invalid_argument("unsupported format character '-' (0x2d)");   // ("%.-1f")
    std::string text = check_f(x, decimals);                   // (pattern % x).rstrip("0").rstrip(".")
    size_t end = text.size();
    while (end > 0 && text[end - 1] == '0') --end;
    while (end > 0 && text[end - 1] == '.') --end;
    text.resize(end);
    return (text.empty() || text == "-0") ? "0" : text;
}

// -- reading files as Python reads them ---------------------------------------

//: Throw Python's UnicodeDecodeError (a ValueError) unless ``s`` is well-formed UTF-8.
inline void check_utf8(const std::string& s, const std::string& path) {
    size_t i = 0, n = s.size();
    while (i < n) {
        unsigned char c = (unsigned char)s[i];
        if (c < 0x80) {
            ++i;
            continue;
        }
        size_t len = 0;
        unsigned char lo = 0x80, hi = 0xBF;                    // the range of the second byte
        if (c >= 0xC2 && c <= 0xDF) len = 2;
        else if (c == 0xE0) len = 3, lo = 0xA0;
        else if (c >= 0xE1 && c <= 0xEC) len = 3;
        else if (c == 0xED) len = 3, hi = 0x9F;               // (no surrogates)
        else if (c >= 0xEE && c <= 0xEF) len = 3;
        else if (c == 0xF0) len = 4, lo = 0x90;
        else if (c >= 0xF1 && c <= 0xF3) len = 4;
        else if (c == 0xF4) len = 4, hi = 0x8F;               // (nothing beyond U+10FFFF)
        bool ok = len > 0 && i + len <= n;
        for (size_t k = 1; ok && k < len; ++k) {
            unsigned char d = (unsigned char)s[i + k];
            ok = k == 1 ? (d >= lo && d <= hi) : (d >= 0x80 && d <= 0xBF);
        }
        if (!ok)
            throw std::invalid_argument("'utf-8' codec can't decode byte " + fmt("0x%02x", c) + " in position " +
                                        std::to_string(i) + " of " + path);
        i += len;
    }
}

inline std::string read_text(const std::string& path) {
    std::error_code ec;
    if (std::filesystem::is_directory(path, ec))              // (Python: IsADirectoryError)
        throw std::system_error(std::make_error_code(std::errc::is_a_directory), "cannot read '" + path + "'");
    errno = 0;
    std::ifstream f(path, std::ios::in | std::ios::binary);
    if (!f) throw std::system_error(errno ? errno : ENOENT, std::generic_category(), "cannot read '" + path + "'");
    std::string bytes((std::istreambuf_iterator<char>(f)), std::istreambuf_iterator<char>());
    check_utf8(bytes, path);
    std::string text;                                          // universal newlines: \r\n and \r -> \n
    text.reserve(bytes.size());
    for (size_t i = 0; i < bytes.size(); ++i) {
        if (bytes[i] != '\r') {
            text += bytes[i];
            continue;
        }
        text += '\n';
        if (i + 1 < bytes.size() && bytes[i + 1] == '\n') ++i;
    }
    return text;
}

inline std::vector<std::string> split_on(const std::string& s, char sep) {
    std::vector<std::string> out;
    size_t a = 0;
    while (true) {
        size_t b = s.find(sep, a);
        if (b == std::string::npos) {
            out.push_back(s.substr(a));
            return out;
        }
        out.push_back(s.substr(a, b - a));
        a = b + 1;
    }
}

//: How many bytes the whitespace character at s[i] takes (0: it is no whitespace).
inline size_t space_at(const std::string& s, size_t i) {
    unsigned char c = (unsigned char)s[i];
    if (c == ' ' || (c >= 0x09 && c <= 0x0D) || (c >= 0x1C && c <= 0x1F)) return 1;
    unsigned char d = i + 1 < s.size() ? (unsigned char)s[i + 1] : 0;
    unsigned char e = i + 2 < s.size() ? (unsigned char)s[i + 2] : 0;
    if (c == 0xC2 && (d == 0x85 || d == 0xA0)) return 2;                      // U+0085, U+00A0
    if (c == 0xE1 && d == 0x9A && e == 0x80) return 3;                         // U+1680
    if (c == 0xE2 && d == 0x80 && ((e >= 0x80 && e <= 0x8A) || e == 0xA8 || e == 0xA9 || e == 0xAF))
        return 3;                                                               // U+2000..200A, 2028, 2029, 202F
    if (c == 0xE2 && d == 0x81 && e == 0x9F) return 3;                         // U+205F
    if (c == 0xE3 && d == 0x80 && e == 0x80) return 3;                         // U+3000
    return 0;
}

inline std::vector<std::string> py_split(const std::string& s) {
    std::vector<std::string> out;
    size_t i = 0;
    while (i < s.size()) {
        size_t w = space_at(s, i);
        if (w) {
            i += w;
            continue;
        }
        size_t start = i;
        while (i < s.size() && !space_at(s, i)) ++i;
        out.push_back(s.substr(start, i - start));
    }
    return out;
}

inline std::string py_strip(const std::string& s) {
    size_t a = 0;
    while (a < s.size() && space_at(s, a)) a += space_at(s, a);
    size_t end = a;                                            // the end of the last character that is not a space
    for (size_t i = a; i < s.size();) {
        size_t w = space_at(s, i);
        if (w) {
            i += w;
        } else {
            ++i;
            end = i;
        }
    }
    return s.substr(a, end - a);
}

inline bool ascii_digit(char ch) { return ch >= '0' && ch <= '9'; }

inline double py_float(const std::string& word) {
    auto refuse = [&]() -> double { throw std::invalid_argument("could not convert string to float: '" + word + "'"); };
    std::string cleaned;                                       // "_" only between two digits, then dropped
    bool underscores = word.find('_') != std::string::npos;
    for (size_t i = 0; underscores && i < word.size(); ++i) {
        if (word[i] != '_') {
            cleaned += word[i];
            continue;
        }
        if (!(i > 0 && ascii_digit(word[i - 1]) && i + 1 < word.size() && ascii_digit(word[i + 1]))) return refuse();
    }
    const std::string& s = underscores ? cleaned : word;
    size_t i = 0;
    bool negative = false;
    if (i < s.size() && (s[i] == '+' || s[i] == '-')) negative = s[i++] == '-';
    if (i < s.size() && s[i] != '.' && !ascii_digit(s[i])) {  // inf, infinity, nan -- in any case (ASCII only)
        std::string name;
        for (size_t k = i; k < s.size(); ++k) name += (s[k] >= 'A' && s[k] <= 'Z') ? (char)(s[k] - 'A' + 'a') : s[k];
        if (name == "inf" || name == "infinity") return negative ? -inf : inf;
        if (name == "nan") return negative ? -std::numeric_limits<double>::quiet_NaN() : std::numeric_limits<double>::quiet_NaN();
        return refuse();
    }
    size_t j = i, digits = 0;                                  // digits [. digits] | . digits
    while (j < s.size() && ascii_digit(s[j])) ++j, ++digits;
    if (j < s.size() && s[j] == '.') {
        ++j;
        while (j < s.size() && ascii_digit(s[j])) ++j, ++digits;
    }
    if (digits == 0) return refuse();
    if (j < s.size() && (s[j] == 'e' || s[j] == 'E')) {        // [e [sign] digits]
        ++j;
        if (j < s.size() && (s[j] == '+' || s[j] == '-')) ++j;
        size_t e0 = j;
        while (j < s.size() && ascii_digit(s[j])) ++j;
        if (j == e0) return refuse();
    }
    if (j != s.size()) return refuse();
    return std::strtod(s.c_str(), nullptr);                    // (correctly rounded, as Python's)
}

inline long long py_int(const std::string& word) {
    auto refuse = [&]() -> long long { throw std::invalid_argument("invalid literal for int() with base 10: '" + word + "'"); };
    size_t i = 0;
    bool negative = false;
    if (i < word.size() && (word[i] == '+' || word[i] == '-')) negative = word[i++] == '-';
    if (i >= word.size()) return refuse();
    const unsigned long long limit = negative ? 9223372036854775808ull : 9223372036854775807ull;
    unsigned long long v = 0;
    for (size_t j = i; j < word.size(); ++j) {
        char ch = word[j];
        if (ch == '_') {                                       // one "_" between two digits
            if (!(j > i && ascii_digit(word[j - 1]) && j + 1 < word.size() && ascii_digit(word[j + 1]))) return refuse();
            continue;
        }
        if (!ascii_digit(ch)) return refuse();
        unsigned d = (unsigned)(ch - '0');
        v = v > (limit - d) / 10 ? limit : v * 10 + d;         // (beyond 64 bits: stays at the limit)
    }
    if (negative) return v == 9223372036854775808ull ? std::numeric_limits<long long>::min() : -(long long)v;
    return (long long)v;
}

//: The code point of the UTF-8 character at s[i] (-1 for a byte that starts none); i moves on.
inline long utf8_next(const std::string& s, size_t& i) {
    unsigned char c = (unsigned char)s[i];
    size_t len = c < 0x80 ? 1 : c >= 0xF0 ? 4 : c >= 0xE0 ? 3 : c >= 0xC0 ? 2 : 0;
    if (len == 0 || i + len > s.size()) {
        ++i;
        return -1;
    }
    long cp = len == 1 ? c : (c & (0x7F >> len));
    for (size_t k = 1; k < len; ++k) {
        unsigned char d = (unsigned char)s[i + k];
        if ((d & 0xC0) != 0x80) {
            ++i;
            return -1;
        }
        cp = (cp << 6) | (d & 0x3F);
    }
    i += len;
    return cp;
}

inline std::string utf8_encode(long cp) {
    std::string s;
    if (cp < 0x80) {
        s += (char)cp;
    } else if (cp < 0x800) {
        s += (char)(0xC0 | (cp >> 6));
        s += (char)(0x80 | (cp & 0x3F));
    } else if (cp < 0x10000) {
        s += (char)(0xE0 | (cp >> 12));
        s += (char)(0x80 | ((cp >> 6) & 0x3F));
        s += (char)(0x80 | (cp & 0x3F));
    } else {
        s += (char)(0xF0 | (cp >> 18));
        s += (char)(0x80 | ((cp >> 12) & 0x3F));
        s += (char)(0x80 | ((cp >> 6) & 0x3F));
        s += (char)(0x80 | (cp & 0x3F));
    }
    return s;
}

inline std::vector<std::string> utf8_chars(const std::string& s) {
    std::vector<std::string> out;
    for (size_t i = 0; i < s.size();) {
        size_t start = i;
        utf8_next(s, i);
        out.push_back(s.substr(start, i - start));
    }
    return out;
}

inline std::string py_upper(const std::string& s) {
    // Runs of small letters: the first, the last, every how many, and how far on the capital is
    // (Python's str.upper() of U+0000..U+017F, U+0370..U+03FF and U+0400..U+052F).
    static const long runs[][4] = {
        {0x61, 0x7A, 1, -32},    {0xB5, 0xB5, 1, 743},    {0xE0, 0xF6, 1, -32},    {0xF8, 0xFE, 1, -32},
        {0xFF, 0xFF, 1, 121},    {0x101, 0x12F, 2, -1},   {0x131, 0x131, 1, -232}, {0x133, 0x137, 2, -1},
        {0x13A, 0x148, 2, -1},   {0x14B, 0x177, 2, -1},   {0x17A, 0x17E, 2, -1},   {0x17F, 0x17F, 1, -300},
        {0x371, 0x373, 2, -1},   {0x377, 0x377, 1, -1},   {0x37B, 0x37D, 1, 130},  {0x3AC, 0x3AC, 1, -38},
        {0x3AD, 0x3AF, 1, -37},  {0x3B1, 0x3C1, 1, -32},  {0x3C2, 0x3C2, 1, -31},  {0x3C3, 0x3CB, 1, -32},
        {0x3CC, 0x3CC, 1, -64},  {0x3CD, 0x3CE, 1, -63},  {0x3D0, 0x3D0, 1, -62},  {0x3D1, 0x3D1, 1, -57},
        {0x3D5, 0x3D5, 1, -47},  {0x3D6, 0x3D6, 1, -54},  {0x3D7, 0x3D7, 1, -8},   {0x3D9, 0x3EF, 2, -1},
        {0x3F0, 0x3F0, 1, -86},  {0x3F1, 0x3F1, 1, -80},  {0x3F2, 0x3F2, 1, 7},    {0x3F3, 0x3F3, 1, -116},
        {0x3F5, 0x3F5, 1, -96},  {0x3F8, 0x3F8, 1, -1},   {0x3FB, 0x3FB, 1, -1},   {0x430, 0x44F, 1, -32},
        {0x450, 0x45F, 1, -80},  {0x461, 0x481, 2, -1},   {0x48B, 0x4BF, 2, -1},   {0x4C2, 0x4CE, 2, -1},
        {0x4CF, 0x4CF, 1, -15},  {0x4D1, 0x52F, 2, -1}};
    std::string out;
    for (size_t i = 0; i < s.size();) {
        size_t start = i;
        long cp = utf8_next(s, i);
        if (cp == 0xDF) out += "SS";                                   // sharp s
        else if (cp == 0x149) out += utf8_encode(0x2BC) + "N";         // n with apostrophe
        else if (cp == 0x390) out += utf8_encode(0x399) + utf8_encode(0x308) + utf8_encode(0x301);   // iota with dialytika and tonos
        else if (cp == 0x3B0) out += utf8_encode(0x3A5) + utf8_encode(0x308) + utf8_encode(0x301);   // upsilon with dialytika and tonos
        else {
            bool changed = false;
            for (const auto& r : runs)
                if (cp >= r[0] && cp <= r[1] && (cp - r[0]) % r[2] == 0) {
                    out += utf8_encode(cp + r[3]);
                    changed = true;
                    break;
                }
            if (!changed) out += s.substr(start, i - start);
        }
    }
    return out;
}

inline Color rgb_list(const std::vector<double>& color) {
    double r = color.at(0), g = color.at(1), b = color.at(2);
    double top = r;                                            // Python's max(r, g, b)
    if (g > top) top = g;
    if (b > top) top = b;
    if (top <= 1.0) {
        r = r * 255.0;
        g = g * 255.0;
        b = b * 255.0;
    }
    const double parts[3] = {r, g, b};
    int out[3];
    for (int i = 0; i < 3; ++i) {                              // int(round(c)), limited to 0..255
        double c = parts[i];
        if (std::isnan(c)) throw std::invalid_argument("cannot convert float NaN to integer");
        if (std::isinf(c)) throw std::overflow_error("cannot convert float infinity to integer");
        double v = std::nearbyint(c);
        out[i] = v < 0 ? 0 : (v > 255 ? 255 : (int)v);
    }
    if (color.size() > 3) return Color(out[0], out[1], out[2], color[3]);
    return Color(out[0], out[1], out[2]);
}

//: Python's ``seq[start:stop]`` of a list of words (an end below 0 counts from the back).
inline std::vector<std::string> py_slice(const std::vector<std::string>& v, long long start, long long stop) {
    long long n = (long long)v.size();
    auto place_ = [n](long long i) { return i < 0 ? std::max(0LL, i + n) : std::min(i, n); };
    long long a = place_(start), b = place_(stop);
    if (b < a) b = a;
    return std::vector<std::string>(v.begin() + a, v.begin() + b);
}

//: A corner count n read from a line of ``size`` words, brought into -(size + 10) .. size + 10:
//: every slice [1:1 + n], [1 + n:], [1 + n:4 + n] of the line stays the same (and cannot overflow).
inline long long slice_count(long long n, size_t size) {
    long long m = (long long)size + 10;
    return std::max(-m, std::min(n, m));
}

//: A vertex index read from a file (add.hpp's faces hold int).
inline int index_of(long long i) {
    if (i < std::numeric_limits<int>::min() || i > std::numeric_limits<int>::max())
        throw std::out_of_range("vertex index out of range: " + std::to_string(i));
    return (int)i;
}

inline std::vector<std::string> clean_lines(const std::string& path) {
    std::vector<std::string> out;
    for (const std::string& line : split_on(read_text(path), '\n')) {
        std::string s = py_strip(line.substr(0, line.find('#')));
        if (!s.empty()) out.push_back(s);
    }
    return out;
}

inline Mesh read_off(const std::string& path, const std::optional<Color>& color) {
    std::vector<std::string> lines = clean_lines(path);
    if (lines.empty()) return Mesh();
    size_t row = 0;
    std::vector<std::string> head = py_split(lines[0]);
    std::vector<std::string> counts;
    std::string first = py_upper(head[0]);
    if (first.size() >= 3 && first.compare(first.size() - 3, 3, "OFF") == 0) {
        row = 1;
        if (head.size() >= 3) {                                // counts on the same line as OFF
            counts.assign(head.begin() + 1, head.end());
        } else {
            counts = py_split(lines.at(1));
            row = 2;
        }
    } else {
        counts = head;
        row = 1;
    }
    long long nv = py_int(counts.at(0));
    long long nf = py_int(counts.at(1));

    Mesh M;
    for (long long q = 0; q < nv; ++q) {
        std::vector<std::string> p = py_split(lines.at(row));
        row += 1;
        double x = py_float(p.at(0));
        double y = py_float(p.at(1));
        double z = py_float(p.at(2));
        M.add_vertex({x, y, z});
    }

    Color fallback = color ? *color : DEFAULT_COLOR;           // (add.py: ``default``)
    for (long long q = 0; q < nf; ++q) {
        std::vector<std::string> p = py_split(lines.at(row));
        row += 1;
        long long n = slice_count(py_int(p.at(0)), p.size());
        Face face;
        for (const std::string& x : py_slice(p, 1, 1 + n)) face.push_back(index_of(py_int(x)));
        std::vector<std::string> rest = py_slice(p, 1 + n, (long long)p.size());
        Color c = fallback;
        if (rest.size() >= 3 && !color) {
            std::vector<double> vals;
            for (size_t j = 0; j < rest.size() && j < 4; ++j) vals.push_back(py_float(rest[j]));
            double top = vals[0];                              // max(vals)
            for (double v : vals)
                if (v > top) top = v;
            bool fraction = false;                             // any(v != int(v) for v in vals)
            if (top <= 1.0)
                for (double v : vals) {
                    if (std::isnan(v)) throw std::invalid_argument("cannot convert float NaN to integer");
                    if (std::isinf(v)) throw std::overflow_error("cannot convert float infinity to integer");
                    if (v != std::trunc(v)) {
                        fraction = true;
                        break;
                    }
                }
            if (top <= 1.0 && fraction)
                for (double& v : vals) v = v * 255.0;
            if (vals.size() == 4) vals[3] = vals[3] / 255.0;   // r g b a: alpha as 0..255
            c = rgb_list(vals);
        }
        M.add_face(face, c);
    }
    return M;
}

inline Mesh read_obj(const std::string& path, const std::optional<Color>& color) {
    Mesh M;
    std::map<std::string, Color> materials;
    Color current = color ? *color : DEFAULT_COLOR;
    std::string folder = path;
    std::replace(folder.begin(), folder.end(), '\\', '/');
    size_t slash = folder.rfind('/');
    folder = slash != std::string::npos ? folder.substr(0, slash) + "/" : "";
    std::vector<Point2> vt;
    for (const std::string& line : split_on(read_text(path), '\n')) {
        std::vector<std::string> parts = py_split(line);
        if (parts.empty() || parts[0][0] == '#') continue;
        const std::string& tag = parts[0];
        if (tag == "v") {
            double x = py_float(parts.at(1));
            double y = py_float(parts.at(2));
            double z = py_float(parts.at(3));
            M.add_vertex({x, y, z});
        } else if (tag == "vt") {
            double u = py_float(parts.at(1));
            double v = parts.size() > 2 ? py_float(parts[2]) : 0.0;
            vt.push_back({u, v});
        } else if (tag == "f") {
            Face face;
            std::vector<Point2> uv;
            for (size_t k = 1; k < parts.size(); ++k) {
                std::vector<std::string> bits = split_on(parts[k], '/');
                long long idx = py_int(bits[0]);
                face.push_back(index_of(idx > 0 ? idx - 1 : (long long)M.V.size() + idx));
                if (bits.size() > 1 && !bits[1].empty()) {
                    long long t = py_int(bits[1]);
                    uv.push_back(vt[seq_index(t > 0 ? t - 1 : (long long)vt.size() + t, vt.size())]);
                }
            }
            bool textured = !current.image.empty() && uv.size() == face.size();
            if (textured) M.add_face(face, current, uv);
            else M.add_face(face, current);
        } else if (tag == "mtllib" && !color) {
            std::string name = folder + parts.at(1);
            std::map<std::string, Color> found;
            try {
                found = read_mtl(name);
            } catch (const std::system_error&) {               // (add.py: except IOError: pass)
            }
            for (auto& item : found) materials[item.first] = item.second;
        } else if (tag == "usemtl" && !color) {
            auto it = materials.find(parts.at(1));
            current = it != materials.end() ? it->second : DEFAULT_COLOR;
        }
    }
    return M;
}

inline std::map<std::string, Color> read_mtl(const std::string& path) {
    std::map<std::string, Color> out;
    std::optional<std::string> name;
    for (const std::string& line : split_on(read_text(path), '\n')) {
        std::vector<std::string> parts = py_split(line);
        if (parts.empty()) continue;
        if (parts[0] == "newmtl") {
            name = parts.at(1);
            out[*name] = DEFAULT_COLOR;
        } else if (!name) {
            continue;
        } else if (parts[0] == "Kd") {
            Color c = out[*name];
            double r = py_float(parts.at(1)) * 255;
            double g = py_float(parts.at(2)) * 255;
            double b = py_float(parts.at(3)) * 255;
            Color k = rgb_list({r, g, b});                     // + list(c[3:]): the opacity and texture stay
            k.alpha = c.alpha;
            k.image = c.image;
            out[*name] = k;
        } else if ((parts[0] == "d" || parts[0] == "Tr") && parts.size() > 1) {
            double alpha = py_float(parts[1]);
            if (parts[0] == "Tr") alpha = 1.0 - alpha;
            Color c = out[*name];
            Color k(c.r, c.g, c.b, alpha);
            k.image = c.image;
            out[*name] = k;
        } else if (parts[0] == "map_Kd" && parts.size() > 1) {
            Color k = out[*name];
            k.image = parts.back();
            out[*name] = k;
        }
    }
    return out;
}

inline Mesh read_ply(const std::string& path, const std::optional<Color>& color) {
    std::vector<std::string> text = split_on(read_text(path), '\n');
    long long nv = 0, nf = 0;
    size_t head = 0;
    std::vector<std::string> props;
    std::optional<std::string> element;
    for (size_t i = 0; i < text.size(); ++i) {
        std::vector<std::string> parts = py_split(text[i]);
        if (parts.empty()) continue;
        if (parts[0] == "element") {
            element = parts.at(1);
            if (*element == "vertex") nv = py_int(parts.at(2));
            else if (*element == "face") nf = py_int(parts.at(2));
        } else if (parts[0] == "property" && element && *element == "vertex") {
            props.push_back(parts.back());
        } else if (parts[0] == "end_header") {
            head = i + 1;
            break;
        }
    }
    Mesh M;
    size_t row = head;
    for (long long q = 0; q < nv; ++q) {
        std::vector<std::string> vals = py_split(text.at(row));
        row += 1;
        std::map<std::string, std::string> d;                  // dict(zip(props, vals))
        for (size_t j = 0; j < props.size() && j < vals.size(); ++j) d[props[j]] = vals[j];
        auto get = [&d](const char* key) {
            auto it = d.find(key);
            return it == d.end() ? 0.0 : py_float(it->second);
        };
        double x = get("x");
        double y = get("y");
        double z = get("z");
        M.add_vertex({x, y, z});
    }
    Color fallback = color ? *color : DEFAULT_COLOR;
    for (long long q = 0; q < nf; ++q) {
        std::vector<std::string> vals = py_split(text.at(row));
        row += 1;
        long long n = slice_count(py_int(vals.at(0)), vals.size());
        Face face;
        for (const std::string& v : py_slice(vals, 1, 1 + n)) face.push_back(index_of(py_int(v)));
        Color c = fallback;
        if ((long long)vals.size() >= 1 + n + 3 && !color) {
            std::vector<double> rgb3;
            for (const std::string& v : py_slice(vals, 1 + n, 4 + n)) rgb3.push_back(py_float(v));
            c = rgb_list(rgb3);
        }
        M.add_face(face, c);
    }
    return M;
}

//: The CRC-32 of a PNG chunk (zlib's crc32).
inline uint32_t crc32(const std::string& data) {
    static const std::array<uint32_t, 256> table = [] {
        std::array<uint32_t, 256> t{};
        for (uint32_t n = 0; n < 256; ++n) {
            uint32_t c = n;
            for (int k = 0; k < 8; ++k) c = c & 1 ? 0xEDB88320u ^ (c >> 1) : c >> 1;
            t[n] = c;
        }
        return t;
    }();
    uint32_t c = 0xFFFFFFFFu;
    for (unsigned char b : data) c = table[(c ^ b) & 0xFF] ^ (c >> 8);
    return c ^ 0xFFFFFFFFu;
}

//: The Adler-32 checksum that ends a zlib stream.
inline uint32_t adler32(const std::string& data) {
    uint32_t a = 1, b = 0;
    for (unsigned char x : data) {
        a = (a + x) % 65521;
        b = (b + a) % 65521;
    }
    return (b << 16) | a;
}

//: A 32-bit number as 4 bytes, most significant first (``struct.pack(">I", v)``).
inline std::string be32(uint32_t v) {
    std::string s(4, '\0');
    for (int k = 0; k < 4; ++k) s[k] = (char)((v >> (24 - 8 * k)) & 0xFF);
    return s;
}

//: ``data`` as a zlib stream (RFC 1950) of stored deflate blocks (RFC 1951, BTYPE 00): what
//: zlib.compress would give without compressing -- any PNG reader takes it.
inline std::string zlib_stored(const std::string& data) {
    std::string out("\x78\x01", 2);                            // deflate, 32K window; (0x7801 % 31 == 0)
    size_t pos = 0;
    do {
        size_t len = std::min<size_t>(65535, data.size() - pos);
        bool last = pos + len == data.size();
        out += (char)(last ? 1 : 0);                           // BFINAL, BTYPE = 00 (then byte-aligned)
        out += (char)(len & 0xFF);                             // LEN, then NLEN, little-endian
        out += (char)(len >> 8);
        out += (char)(~len & 0xFF);
        out += (char)((~len >> 8) & 0xFF);
        out.append(data, pos, len);
        pos += len;
    } while (pos < data.size());
    return out + be32(adler32(data));
}

//: os.path.join(folder, name) (POSIX).
inline std::string path_join(const std::string& folder, const std::string& name) {
    if (!name.empty() && name[0] == '/') return name;
    if (folder.empty() || folder.back() == '/') return folder + name;
    return folder + "/" + name;
}

//: load_font() once the names are known.
inline std::map<std::string, Mesh> load_names(const std::string& folder, const std::vector<std::string>& names,
                                              const std::string& suffix) {
    std::map<std::string, Mesh> out;
    for (const std::string& name : names) {
        try {
            Mesh M = load(path_join(folder, name + suffix));
            out[name] = std::move(M);
        } catch (const std::system_error&) {                   // (add.py: IOError, OSError,
        } catch (const std::invalid_argument&) {               //  ValueError)
        }
    }
    return out;
}

}  // namespace detail

inline long long obj_size(const Mesh& M) {
    long long total = 50;                                      // header lines
    for (const Point& p : M.V) {
        size_t x = detail::num(p[0]).size();                   // (in Python's order: an infinity raises
        size_t y = detail::num(p[1]).size();                   //  OverflowError, a NaN ValueError)
        size_t z = detail::num(p[2]).size();
        total += 5 + (long long)(x + y + z);
    }
    std::unordered_set<Color, ColorHash> seen;
    std::set<std::pair<double, double>> vts;
    for (size_t k = 0; k < M.F.size(); ++k) {
        const Face& face = M.F[k];
        const Color& c = M.C[k];
        total += 2 + (long long)face.size();
        bool textured = !c.image.empty() && M.has_uv && !M.UV[k].empty();
        for (int i : face) total += (long long)std::to_string(i + 1).size();
        if (textured) {
            for (const Point2& t : M.UV[k]) {
                std::pair<double, double> key = detail::uv_key(t);
                if (!detail::known_uv(vts, key)) {
                    vts.insert(key);
                    size_t u = detail::num(key.first).size();          // (u first: Python's order)
                    size_t v = detail::num(key.second).size();
                    total += 6 + (long long)(u + v);
                }
                total += 1 + (long long)std::to_string(vts.size()).size();   // "/vt" per corner
            }
        }
        if (!seen.count(c)) {
            seen.insert(c);
            bool longer = c.alpha < 1.0 || !c.image.empty();          // (add.py: len(c) > 3)
            total += 20 + (longer ? 8 : 0) + (!c.image.empty() ? 10 + (long long)detail::utf8_len(c.image) : 0);
        }
    }
    return total;
}
inline long long obj_size() { return obj_size(scene()); }

inline std::string save(const std::string& path, const Mesh& M, std::optional<bool> clear_scene,
                        std::optional<int> colors, bool clean_) {
    bool clear_after = clear_scene ? *clear_scene : detail::is_scene(M);
    Mesh to_save = clean_ ? clean(M, 1e-6) : M;
    if (colors) to_save = limit_colors(to_save, *colors);
    std::string ext = "off";
    size_t dot_ = path.rfind('.');
    if (dot_ != std::string::npos) ext = detail::lower(path.substr(dot_ + 1));
    if (ext == "obj") detail::write_obj(path, to_save);
    else if (ext == "ply") detail::write_ply(path, to_save);
    else if (ext == "stl") detail::write_stl(path, to_save);
    else detail::write_off(path, to_save);
    if (clear_after) clear();
    return path;
}
inline std::string save(const std::string& path) { return save(path, scene(), true); }

inline std::string off(const std::string& path, const Mesh& M) {
    bool clear_after = detail::is_scene(M);
    detail::write_off(path, M);
    if (clear_after) clear();
    return path;
}
inline std::string off(const std::string& path) { return off(path, scene()); }

inline std::string obj(const std::string& path, const Mesh& M, std::optional<std::string> mtl) {
    bool clear_after = detail::is_scene(M);
    detail::write_obj(path, M, mtl);
    if (clear_after) clear();
    return path;
}
inline std::string obj(const std::string& path) { return obj(path, scene()); }

// -- Stream -------------------------------------------------------------------

inline Stream::Stream(const std::string& path_, bool clean, std::optional<int> precision_)
    : path(path_), clean_parts(clean), precision(precision_) {
    std::string low = detail::lower(path);
    kind_ = low.size() >= 4 && low.compare(low.size() - 4, 4, ".obj") == 0 ? "obj" : "off";
    vt_ = 0;
    file_ = detail::open_out(path);
    if (kind_ == "obj") {
        mtl_ = path.substr(0, path.size() - 4) + ".mtl";
        file_ << "# written by add.py " << version << "\n";
        file_ << "mtllib " << detail::file_stem(mtl_) << "\n";
        file_ << "o model\n";
    } else {
        // OFF wants the counts first and every vertex before every face: the vertices and the
        // faces wait in two files of their own and the OFF file is put together on close, with
        // an exact header.
        file_.close();
        vertices_path_ = path + ".vertices~";
        file_ = detail::open_out(vertices_path_);
        faces_path_ = path + ".faces~";
        faces_file_ = detail::open_out(faces_path_);
    }
    has_current_ = false;
    open_ = true;
}

inline Stream::~Stream() {
    try {
        close();
    } catch (...) {                                            // (a destructor must not throw)
    }
}

inline std::string Stream::num(double x) const {
    return precision ? detail::rounded(x, *precision) : detail::num(x);
}

inline long long Stream::add(const Mesh& M0, std::optional<bool> clean) {
    bool clear_after = detail::is_scene(M0);
    if (!open_) throw std::invalid_argument("stream is closed");
    Mesh tidy;
    const Mesh* part = &M0;
    if (clean ? *clean : clean_parts) {
        CleanReport info;
        tidy = add::clean(M0, 1e-6, true, true, true, true, true, false, &info);
        removed += info.faces_removed;
        cut += info.faces_cut;
        part = &tidy;
    }
    Mesh M = detail::writable(*part);                          // tidied or not: no face visits a vertex twice
    long long base = vertices;
    std::string text;
    if (kind_ == "obj") {
        for (const Point& p : M.V) {
            std::string x = num(p[0]);
            std::string y = num(p[1]);
            std::string z = num(p[2]);
            text += "v " + x + " " + y + " " + z + "\n";
        }
        std::map<std::pair<double, double>, long long> vt_index;
        if (M.has_uv) {
            for (size_t k = 0; k < M.C.size(); ++k) {
                const std::vector<Point2>& uv = M.UV[k];
                if (uv.empty() || M.C[k].image.empty()) continue;
                for (const Point2& t : uv) {
                    std::pair<double, double> key = detail::uv_key(t);
                    if (!detail::known_uv(vt_index, key)) {
                        vt_ += 1;
                        vt_index[key] = vt_;
                        std::string u = detail::num(key.first);
                        std::string v = detail::num(key.second);
                        text += "vt " + u + " " + v + "\n";
                    }
                }
            }
        }
        std::unordered_map<Color, std::vector<size_t>, ColorHash> by_color;
        std::vector<Color> order;
        for (size_t k = 0; k < M.C.size(); ++k) {
            auto it = by_color.find(M.C[k]);
            if (it == by_color.end()) {
                it = by_color.emplace(M.C[k], std::vector<size_t>()).first;
                order.push_back(M.C[k]);
            }
            it->second.push_back(k);
        }
        for (const Color& c : order) {
            auto known = material_index_.find(c);
            if (known == material_index_.end()) {
                known = material_index_.emplace(c, detail::material_name(c)).first;
                materials.emplace_back(c, known->second);
            }
            const std::string& name = known->second;
            if (!has_current_ || c != current_) {
                text += "usemtl " + name + "\n";
                current_ = c;
                has_current_ = true;
            }
            bool textured = !c.image.empty() && M.has_uv;
            for (size_t k : by_color[c])
                text += detail::obj_face_line(M.F[k], textured && !M.UV[k].empty() ? &M.UV[k] : nullptr, base + 1,
                                              vt_index);
        }
    } else {
        for (const Point& p : M.V) {
            std::string x = num(p[0]);
            std::string y = num(p[1]);
            std::string z = num(p[2]);
            text += x + " " + y + " " + z + "\n";
        }
        std::vector<std::string> lines = detail::off_face_lines(M, base);   // at most four corners a face
        std::string joined;
        for (const std::string& line : lines) joined += line;
        faces_file_ << joined;
        bytes += (long long)joined.size();
        faces += (long long)lines.size() - (long long)M.F.size();   // (the pieces are what the file counts)
    }
    if (!text.empty()) {
        file_ << text;
        bytes += (long long)detail::utf8_len(text);            // (Python counts characters)
    }
    vertices += (long long)M.V.size();
    faces += (long long)M.F.size();
    if (clear_after) add::clear();
    return (long long)M.F.size();
}

inline long long Stream::add() { return add(scene()); }

inline std::string Stream::close() {
    if (!open_) return path;
    if (kind_ == "obj") {
        std::ofstream m = detail::open_out(mtl_);
        m << "# written by add.py " << version << "\n";
        for (const auto& item : materials) {
            const Color& c = item.first;
            m << "newmtl " << item.second << "\n";
            m << detail::fmt("Kd %.6f %.6f %.6f\n", c.r / 255.0, c.g / 255.0, c.b / 255.0);
            m << "Ka 0.100000 0.100000 0.100000\n";
            m << "Ks 0.000000 0.000000 0.000000\n";
            m << detail::fmt("d %.3f\n", c.alpha);
            m << "illum 1\n";
            if (!c.image.empty()) m << "map_Kd " << detail::file_stem(c.image) << "\n";
            m << "\n";
        }
    } else {
        file_.close();
        faces_file_.close();
        std::ofstream out = detail::open_out(path);
        std::string header = "OFF\n" + std::to_string(vertices) + " " + std::to_string(faces) + " 0\n";
        out << header;
        bytes += (long long)header.size();
        std::vector<char> chunk(1 << 20);
        for (const std::string& part : {vertices_path_, faces_path_}) {
            std::ifstream src(part, std::ios::in | std::ios::binary);
            while (src.read(chunk.data(), (std::streamsize)chunk.size()) || src.gcount() > 0)
                out.write(chunk.data(), src.gcount());
        }
        out.close();
        std::remove(vertices_path_.c_str());                   // the only files add.hpp removes
        std::remove(faces_path_.c_str());
        open_ = false;
        return path;
    }
    file_.close();
    open_ = false;
    return path;
}

inline std::unique_ptr<Stream> stream(const std::string& path, bool clean, std::optional<int> precision) {
    return std::make_unique<Stream>(path, clean, precision);
}

// -- loading ------------------------------------------------------------------

inline Mesh load(const std::string& path, std::optional<Color> color) {
    std::string ext = "off";
    size_t dot_ = path.rfind('.');
    if (dot_ != std::string::npos) ext = detail::lower(path.substr(dot_ + 1));
    if (ext == "obj") return detail::read_obj(path, color);
    if (ext == "ply") return detail::read_ply(path, color);
    return detail::read_off(path, color);
}

inline std::string write_png(const std::string& path, const std::vector<std::vector<Color>>& rows) {
    size_t height = rows.size();
    size_t width = height ? rows[0].size() : 0;
    std::string raw;
    for (const std::vector<Color>& row : rows) {
        raw += '\0';                                           // filter type "none"
        for (const Color& c : row) {
            raw += (char)c.r;
            raw += (char)c.g;
            raw += (char)c.b;
        }
    }
    auto chunk = [](const std::string& tag, const std::string& data) {
        return detail::be32((uint32_t)data.size()) + tag + data + detail::be32(detail::crc32(tag + data));
    };
    std::string header = detail::be32((uint32_t)width) + detail::be32((uint32_t)height) +
                         std::string("\x08\x02\x00\x00\x00", 5);   // 8 bits, RGB, deflate, no filter, no interlace
    std::ofstream f = detail::open_out(path);
    f << std::string("\x89PNG\r\n\x1a\n", 8);
    f << chunk("IHDR", header);
    f << chunk("IDAT", detail::zlib_stored(raw));              // (add.py: zlib.compress(raw, 6))
    f << chunk("IEND", "");
    return path;
}

inline std::map<std::string, Mesh> load_font(const std::string& folder, std::optional<std::string> characters,
                                             const std::string& suffix) {
    if (characters) return detail::load_names(folder, detail::utf8_chars(*characters), suffix);
    std::vector<std::string> names;
    std::error_code ec;
    std::filesystem::directory_iterator it(folder, ec), end;
    if (ec) return {};                                         // (add.py: OSError from os.listdir)
    for (; it != end; it.increment(ec)) {
        if (ec) return {};
        std::string n = it->path().filename().string();
        if (n.size() >= suffix.size() && n.compare(n.size() - suffix.size(), suffix.size(), suffix) == 0)
            names.push_back(suffix.empty() ? std::string() : n.substr(0, n.size() - suffix.size()));   // n[:-len(suffix)]
    }
    return detail::load_names(folder, names, suffix);
}

inline std::map<std::string, Mesh> load_font(const std::string& folder, const std::vector<std::string>& characters,
                                             const std::string& suffix) {
    return detail::load_names(folder, characters, suffix);
}

inline Mesh typeset(const std::string& characters, const std::map<std::string, Mesh>& font, const Point& at,
                    double size, double spacing, std::optional<Color> color, const std::array<Point, 2>& plane) {
    const Point& u = plane[0];
    Mesh out;
    double x = 0.0;
    for (const std::string& ch : detail::utf8_chars(characters)) {
        auto it = font.find(ch);                               // font.get(ch) or font.get(ch.upper())
        if (it == font.end()) it = font.find(detail::py_upper(ch));
        if (it == font.end()) {
            x += spacing;
            continue;
        }
        Mesh G = fit(it->second, size);
        G = place(G, {0, 0, 0});
        Point pos = {at[0] + u[0] * x * spacing * size, at[1] + u[1] * x * spacing * size,
                     at[2] + u[2] * x * spacing * size};
        G = move(G, pos);
        if (color) G = add::color(G, *color);
        out.extend(G);
        x += 1.0;
    }
    return out;
}

}  // namespace add

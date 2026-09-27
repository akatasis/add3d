// ============================================================================
//  14. Working with vertices, edges and faces
//      (add.py: _src/55_mesh_ops.py)
// ============================================================================
namespace add {

using Edge = std::pair<int, int>;

//: A new position for a vertex: a Point, or {x, y, z} in which a coordinate may be std::nullopt to
//: keep its old value (add.py's None) -- add::set_vertex(M, 3, {std::nullopt, 2.5, std::nullopt}).
struct PartialPoint {
    std::optional<double> x, y, z;
    PartialPoint() {}
    PartialPoint(const Point& p) : x(p.x), y(p.y), z(p.z) {}
    PartialPoint(std::optional<double> x_, std::optional<double> y_, std::optional<double> z_)
        : x(x_), y(y_), z(z_) {}
};

namespace detail {
//: {(a, b): face} for every directed edge of the faces; -1 for an edge in more than one face.
inline std::map<Edge, int> directed_edges(const Mesh& M);
//: The faces round a vertex in order, each as (face, the vertex its edge leaves towards), and whether
//: the ring closes (add.py's _rings gives one such pair per vertex).
struct VertexRing {
    std::vector<std::pair<int, int>> ring;
    bool closed = false;
};
inline std::vector<VertexRing> rings(const Mesh& M);
}  // namespace detail

//: The coordinates of vertex i (a negative i counts from the end, as in Python).
inline Point vertex(const Mesh& M, int i);
//: A copy of the mesh with vertex i moved to ``point`` (a std::nullopt coordinate keeps its value).
inline Mesh set_vertex(const Mesh& M, int i, const PartialPoint& point);
//: Like set_vertex for several vertices at once: {{index, new point}, ...} -- add.py's dict, so the
//: changes are made in the order given, and an index given twice counts once, with its last point.
inline Mesh set_vertices(const Mesh& M, const std::vector<std::pair<int, PartialPoint>>& changes);
//: The same with a std::map {index: new point} (made in the order of the indices).
template <class P, class = std::enable_if_t<std::is_convertible<P, PartialPoint>::value>>
inline Mesh set_vertices(const Mesh& M, const std::map<int, P>& changes) {
    return set_vertices(M, std::vector<std::pair<int, PartialPoint>>(changes.begin(), changes.end()));
}
//: A copy of the mesh with vertex i shifted by ``delta``.
inline Mesh move_vertex(const Mesh& M, int i, const Point& delta);
//: The index of the vertex closest to ``point`` (-1 for a mesh without vertices).
inline int nearest_vertex(const Mesh& M, const Point& point);
//: Every edge once, as (a, b) with a < b, sorted.
inline std::vector<Edge> edges(const Mesh& M);
inline std::vector<Edge> edges();
//: The distance between vertices a and b.
inline double edge_length(const Mesh& M, int a, int b);
//: The length of every edge, in the order edges() lists them.
inline std::vector<double> edge_lengths(const Mesh& M);
inline std::vector<double> edge_lengths();
//: The average edge length.
inline double mean_edge_length(const Mesh& M);
inline double mean_edge_length();
//: neighbours[i] = sorted list of the vertices joined to vertex i.
inline std::vector<std::vector<int>> adjacency(const Mesh& M);
inline std::vector<std::vector<int>> adjacency();
//: The vertices joined to vertex i by an edge (in order round it on a closed mesh).
inline std::vector<int> neighbors(const Mesh& M, int i);
inline std::vector<int> neighbours(const Mesh& M, int i);
//: How many edges vertex i has.
inline int valence(const Mesh& M, int i);
//: The average distance from vertex i to its neighbours.
inline double mean_neighbor_distance(const Mesh& M, int i);
//: The faces that meet at vertex i.
inline std::vector<int> vertex_faces(const Mesh& M, int i);
//: The unit normal at vertex i.
inline Point vertex_normal(const Mesh& M, int i);
//: The centre (average corner) of face i.
inline Point face_center(const Mesh& M, int i);
//: The unit normal of face i.
inline Point face_normal(const Mesh& M, int i);
//: The area of face i.
inline double face_area(const Mesh& M, int i);
//: The centre of every face.
inline Points face_centers(const Mesh& M);
inline Points face_centers();
//: The edges that belong to only one face, as directed (a, b) pairs.
inline std::vector<Edge> boundary_edges(const Mesh& M);
inline std::vector<Edge> boundary_edges();
//: The open borders of a mesh as closed rings of vertex indices.
inline std::vector<std::vector<int>> boundary_loops(const Mesh& M);
inline std::vector<std::vector<int>> boundary_loops();
//: Push every vertex out along its normal by ``amount``.
inline Mesh inflate(const Mesh& M, double amount);
//: Project every vertex onto a sphere (``amount`` 0..1 of the way).
inline Mesh spherify(const Mesh& M, std::optional<Point> center = std::nullopt, std::optional<double> r = std::nullopt,
                     double amount = 1.0);
//: Split every face into four (triangles) or one quad per corner, ``steps`` times.
inline Mesh refine(const Mesh& M, int steps = 1);
//: The dual polyhedron.
inline Mesh dual(const Mesh& M, std::optional<Color> color = std::nullopt);
//: Cut every corner off (``t``: how far along the edges); the new corner faces are painted ``color``.
inline Mesh truncate(const Mesh& M, double t = 1.0 / 3.0, const Color& color = DEFAULT_COLOR);
//: Paint every face by its number of corners: {corners: colour}; the others get ``fallback`` (add.py's
//: ``default``) or keep their colour.
inline Mesh color_by_sides(const Mesh& M, const std::map<int, Color>& colors,
                           std::optional<Color> fallback = std::nullopt);

}  // namespace add
//@@definitions
namespace add {

namespace detail {

inline std::map<Edge, int> directed_edges(const Mesh& M) {
    std::map<Edge, int> out;
    for (size_t fi = 0; fi < M.F.size(); ++fi) {
        const Face& f = M.F[fi];
        size_t n = f.size();
        for (size_t t = 0; t < n; ++t) {
            Edge key(f[t], f[(t + 1) % n]);
            auto it = out.find(key);
            if (it != out.end()) it->second = -1;
            else out.emplace(key, (int)fi);
        }
    }
    return out;
}

inline std::vector<VertexRing> rings(const Mesh& M) {
    std::map<Edge, int> E = directed_edges(M);
    auto get = [&E](int a, int b) {                            // E.get((a, b), -1)
        auto it = E.find(Edge(a, b));
        return it == E.end() ? -1 : it->second;
    };
    struct Corner { int fi, prev, next; };
    std::vector<std::vector<Corner>> corners(M.V.size());     // vertex -> [(face, prev, next)]
    for (size_t fi = 0; fi < M.F.size(); ++fi) {
        const Face& f = M.F[fi];
        size_t n = f.size();
        for (size_t t = 0; t < n; ++t) corners.at(f[t]).push_back({(int)fi, f[(t + n - 1) % n], f[(t + 1) % n]});
    }
    std::vector<VertexRing> out;
    out.reserve(corners.size());
    for (size_t v = 0; v < corners.size(); ++v) {
        const std::vector<Corner>& cs = corners[v];
        VertexRing R;
        if (cs.empty()) {
            out.push_back(R);
            continue;
        }
        std::unordered_map<int, std::pair<int, int>> by_face;
        bool ok = true;
        for (const Corner& c : cs) {
            if (by_face.count(c.fi)) ok = false;               // v twice in one face
            by_face[c.fi] = {c.prev, c.next};
        }
        if (!ok) {
            for (const Corner& c : cs) R.ring.push_back({c.fi, c.next});
            out.push_back(R);
            continue;
        }
        // Start at a border face if there is one: the face whose edge prev -> v has no partner face
        // on the other side.
        int start = cs[0].fi;
        for (const Corner& c : cs)
            if (get((int)v, c.prev) == -1) {
                start = c.fi;
                break;
            }
        std::unordered_set<int> seen;
        int fi = start;
        bool closed = false;
        while (true) {
            if (seen.count(fi)) {                              // (Python's while ... else)
                closed = (fi == start);
                break;
            }
            seen.insert(fi);
            int nxt = by_face[fi].second;
            R.ring.push_back({fi, nxt});
            int g = get(nxt, (int)v);
            if (g == -1 || !by_face.count(g)) break;
            fi = g;
        }
        if (seen.size() != cs.size()) {                        // not all faces reached
            closed = false;
            for (const Corner& c : cs)
                if (!seen.count(c.fi)) R.ring.push_back({c.fi, c.next});
        }
        R.closed = closed;
        out.push_back(R);
    }
    return out;
}

}  // namespace detail

inline Point vertex(const Mesh& M, int i) { return M.V[detail::seq_index(i, M.V.size())]; }

inline Mesh set_vertex(const Mesh& M, int i, const PartialPoint& point) { return set_vertices(M, {{i, point}}); }

inline Mesh set_vertices(const Mesh& M, const std::vector<std::pair<int, PartialPoint>>& changes) {
    // A dict: an index given again keeps its first place and takes the new point.
    std::vector<std::pair<int, PartialPoint>> dict;
    std::unordered_map<int, size_t> where;
    for (const auto& change : changes) {
        auto it = where.find(change.first);
        if (it != where.end()) {
            dict[it->second].second = change.second;
        } else {
            where.emplace(change.first, dict.size());
            dict.push_back(change);
        }
    }
    Mesh out = M;
    for (const auto& change : dict) {
        Point& p = out.V[detail::seq_index(change.first, out.V.size())];
        const PartialPoint& q = change.second;
        if (q.x) p.x = *q.x;
        if (q.y) p.y = *q.y;
        if (q.z) p.z = *q.z;
    }
    return out;
}

inline Mesh move_vertex(const Mesh& M, int i, const Point& delta) {
    const Point& p = M.V[detail::seq_index(i, M.V.size())];
    return set_vertices(M, {{i, Point{p[0] + delta[0], p[1] + delta[1], p[2] + delta[2]}}});
}

inline int nearest_vertex(const Mesh& M, const Point& point) {
    int best = -1;
    double best_d = 0.0;
    for (size_t i = 0; i < M.V.size(); ++i) {
        const Point& p = M.V[i];
        double d = detail::py_pow(p[0] - point[0], 2) + detail::py_pow(p[1] - point[1], 2) +
                   detail::py_pow(p[2] - point[2], 2);                 // (Python's ** 2)
        if (best < 0 || d < best_d) {                          // (the first of equals)
            best = (int)i;
            best_d = d;
        }
    }
    return best;
}

inline std::vector<Edge> edges(const Mesh& M) {
    std::set<Edge> seen;
    for (const Face& f : M.F) {
        size_t n = f.size();
        for (size_t t = 0; t < n; ++t) {
            int a = f[t], b = f[(t + 1) % n];
            if (a != b) seen.insert(a < b ? Edge(a, b) : Edge(b, a));
        }
    }
    return std::vector<Edge>(seen.begin(), seen.end());
}
inline std::vector<Edge> edges() { return edges(scene()); }

inline double edge_length(const Mesh& M, int a, int b) {
    return detail::norm(detail::sub(M.V[detail::seq_index(a, M.V.size())], M.V[detail::seq_index(b, M.V.size())]));
}

inline std::vector<double> edge_lengths(const Mesh& M) {
    std::vector<double> out;
    for (const Edge& e : edges(M)) out.push_back(detail::norm(detail::sub(M.V[e.first], M.V[e.second])));
    return out;
}
inline std::vector<double> edge_lengths() { return edge_lengths(scene()); }

inline double mean_edge_length(const Mesh& M) {
    std::vector<double> L = edge_lengths(M);
    if (L.empty()) return 0.0;
    double s = 0.0;                                            // (add.py's _total: in order)
    for (double x : L) s = s + x;
    return s / (double)L.size();
}
inline double mean_edge_length() { return mean_edge_length(scene()); }

inline std::vector<std::vector<int>> adjacency(const Mesh& M) {
    std::vector<std::set<int>> nb(M.V.size());
    for (const Edge& e : edges(M)) {
        nb.at(e.first).insert(e.second);
        nb.at(e.second).insert(e.first);
    }
    std::vector<std::vector<int>> out;
    out.reserve(nb.size());
    for (const std::set<int>& s : nb) out.push_back(std::vector<int>(s.begin(), s.end()));
    return out;
}
inline std::vector<std::vector<int>> adjacency() { return adjacency(scene()); }

inline std::vector<int> neighbors(const Mesh& M, int i) {
    std::vector<detail::VertexRing> R = detail::rings(M);
    const detail::VertexRing& r = R[detail::seq_index(i, R.size())];
    if (r.closed) {
        std::vector<int> out;
        for (auto it = r.ring.rbegin(); it != r.ring.rend(); ++it) out.push_back(it->second);
        return out;
    }
    std::vector<std::vector<int>> adj = adjacency(M);
    return adj[detail::seq_index(i, adj.size())];
}
inline std::vector<int> neighbours(const Mesh& M, int i) { return neighbors(M, i); }

inline int valence(const Mesh& M, int i) {
    std::vector<std::vector<int>> adj = adjacency(M);
    return (int)adj[detail::seq_index(i, adj.size())].size();
}

inline double mean_neighbor_distance(const Mesh& M, int i) {
    std::vector<std::vector<int>> adj = adjacency(M);
    const std::vector<int>& nb = adj[detail::seq_index(i, adj.size())];
    if (nb.empty()) return 0.0;
    const Point& p = M.V[detail::seq_index(i, M.V.size())];
    double s = 0.0;
    for (int j : nb) s = s + detail::norm(detail::sub(p, M.V[j]));
    return s / (double)nb.size();
}

inline std::vector<int> vertex_faces(const Mesh& M, int i) {
    std::vector<detail::VertexRing> R = detail::rings(M);
    const detail::VertexRing& r = R[detail::seq_index(i, R.size())];
    std::vector<int> out;
    if (r.closed) {
        for (auto it = r.ring.rbegin(); it != r.ring.rend(); ++it) out.push_back(it->first);
        return out;
    }
    std::set<int> faces;
    for (const auto& entry : r.ring) faces.insert(entry.first);
    return std::vector<int>(faces.begin(), faces.end());
}

inline Point vertex_normal(const Mesh& M, int i) {
    Point acc{0.0, 0.0, 0.0};
    for (int fi : vertex_faces(M, i)) {
        Point nrm = detail::face_normal(M, M.F[fi]);
        acc[0] += nrm[0];
        acc[1] += nrm[1];
        acc[2] += nrm[2];
    }
    return detail::norm(acc) > EPS ? detail::unit(acc) : Point{0.0, 1.0, 0.0};
}

inline Point face_center(const Mesh& M, int i) {
    const Face& f = M.F[detail::seq_index(i, M.F.size())];
    if (f.empty()) throw std::domain_error("float division by zero");
    double n = (double)f.size();
    Point out;
    for (int a = 0; a < 3; ++a) {
        double s = 0.0;                                        // (add.py's _total: in order)
        for (int k : f) s = s + M.V[k][a];
        out[a] = s / n;
    }
    return out;
}

inline Point face_normal(const Mesh& M, int i) {
    return detail::unit(detail::face_normal(M, M.F[detail::seq_index(i, M.F.size())]));
}

inline double face_area(const Mesh& M, int i) {
    return detail::norm(detail::face_normal(M, M.F[detail::seq_index(i, M.F.size())])) / 2.0;
}

inline Points face_centers(const Mesh& M) {
    Points out;
    out.reserve(M.F.size());
    for (size_t i = 0; i < M.F.size(); ++i) out.push_back(face_center(M, (int)i));
    return out;
}
inline Points face_centers() { return face_centers(scene()); }

inline std::vector<Edge> boundary_edges(const Mesh& M) {
    std::vector<Edge> out;
    for (const detail::BorderEdge& e : detail::boundary_edges(M)) out.push_back(Edge(e.a, e.b));
    std::sort(out.begin(), out.end());
    return out;
}
inline std::vector<Edge> boundary_edges() { return boundary_edges(scene()); }

inline std::vector<std::vector<int>> boundary_loops(const Mesh& M) {
    std::map<int, std::vector<int>> nxt;
    for (const detail::BorderEdge& e : detail::boundary_edges(M)) nxt[e.a].push_back(e.b);
    std::vector<std::vector<int>> loops;
    while (!nxt.empty()) {
        int start = nxt.begin()->first;                        // min(nxt)
        std::vector<int> loop{start};
        std::vector<int>& from_start = nxt[start];
        int v = from_start.back();                             // (list.pop(): the last one)
        from_start.pop_back();
        if (from_start.empty()) nxt.erase(start);
        while (v != start && nxt.count(v)) {
            loop.push_back(v);
            std::vector<int>& from_v = nxt[v];
            int w = from_v.back();
            from_v.pop_back();
            if (from_v.empty()) nxt.erase(v);
            v = w;
        }
        loops.push_back(loop);
    }
    return loops;
}
inline std::vector<std::vector<int>> boundary_loops() { return boundary_loops(scene()); }

inline Mesh inflate(const Mesh& M, double amount) {
    Points N = detail::vertex_normals(M);
    Mesh out = M;
    out.V.clear();
    for (size_t i = 0; i < M.V.size() && i < N.size(); ++i) {
        const Point& p = M.V[i];
        const Point& n = N[i];
        out.V.push_back({p[0] + n[0] * amount, p[1] + n[1] * amount, p[2] + n[2] * amount});
    }
    return out;
}

inline Mesh spherify(const Mesh& M, std::optional<Point> center, std::optional<double> r, double amount) {
    Point c = center ? *center : add::center(M);
    double radius;
    if (r) {
        radius = *r;
    } else if (M.V.empty()) {
        radius = 1.0;                                          // max([...] or [1.0])
    } else {
        radius = detail::norm(detail::sub(M.V[0], c));
        for (const Point& p : M.V) {
            double x = detail::norm(detail::sub(p, c));
            if (x > radius) radius = x;
        }
    }
    Points V;
    V.reserve(M.V.size());
    for (const Point& p : M.V) {
        Point u = detail::unit(detail::sub(p, c));
        Point target{c[0] + u[0] * radius, c[1] + u[1] * radius, c[2] + u[2] * radius};
        Point q;
        for (int a = 0; a < 3; ++a) q[a] = p[a] + (target[a] - p[a]) * amount;
        V.push_back(q);
    }
    Mesh out = M;
    out.V = V;
    return out;
}

inline Mesh refine(const Mesh& M0, int steps) {
    Mesh M = M0;
    for (int step = 0; step < steps; ++step) {
        Mesh out;                                              // (texture coordinates are not kept)
        out.V = M.V;
        std::map<Edge, int> mid;
        auto midpoint_index = [&](int a, int b) {
            Edge key = a < b ? Edge(a, b) : Edge(b, a);
            auto it = mid.find(key);
            if (it != mid.end()) return it->second;
            const Point& pa = M.V[a];
            const Point& pb = M.V[b];
            int k = out.add_vertex({(pa[0] + pb[0]) / 2.0, (pa[1] + pb[1]) / 2.0, (pa[2] + pb[2]) / 2.0});
            mid.emplace(key, k);
            return k;
        };
        for (size_t q = 0; q < M.F.size() && q < M.C.size(); ++q) {
            const Face& f = M.F[q];
            const Color& c = M.C[q];
            size_t n = f.size();
            if (n == 3) {
                int a = f[0], b = f[1], d = f[2];
                int ab = midpoint_index(a, b);                 // (in this order)
                int bd = midpoint_index(b, d);
                int da = midpoint_index(d, a);
                out.add_face({a, ab, da}, c);
                out.add_face({b, bd, ab}, c);
                out.add_face({d, da, bd}, c);
                out.add_face({ab, bd, da}, c);
            } else if (n >= 4) {
                Point centre_point;
                for (int a = 0; a < 3; ++a) {
                    double s = 0.0;
                    for (int k : f) s = s + M.V[k][a];
                    centre_point[a] = s / (double)n;
                }
                int centre = out.add_vertex(centre_point);
                std::vector<int> m;
                for (size_t t = 0; t < n; ++t) m.push_back(midpoint_index(f[t], f[(t + 1) % n]));
                for (size_t t = 0; t < n; ++t) out.add_face({f[t], m[t], centre, m[(t + n - 1) % n]}, c);
            } else {
                out.add_face(f, c);
            }
        }
        M = std::move(out);
    }
    return M;
}

inline Mesh dual(const Mesh& M, std::optional<Color> color) {
    Mesh out;
    for (size_t i = 0; i < M.F.size(); ++i) out.add_vertex(face_center(M, (int)i));
    std::vector<detail::VertexRing> R = detail::rings(M);
    for (const detail::VertexRing& r : R) {
        if (!r.closed || r.ring.size() < 3) continue;
        Face faces;
        for (auto it = r.ring.rbegin(); it != r.ring.rend(); ++it) faces.push_back(it->first);
        out.add_face(faces, color ? *color : M.C[faces[0]]);
    }
    detail::drop_unused(out);
    return out;
}

inline Mesh truncate(const Mesh& M, double t, const Color& color) {
    if (t > 0.5) t = 0.5;
    Mesh out;
    std::map<Edge, int> cut;
    auto point = [&](int a, int b) {                           // the vertex on edge a -> b at fraction t from a
        Edge key = t < 0.5 - 1e-12 ? Edge(a, b) : (a < b ? Edge(a, b) : Edge(b, a));
        auto it = cut.find(key);
        if (it != cut.end()) return it->second;
        const Point& pa = M.V[a];
        const Point& pb = M.V[b];
        int k = out.add_vertex({pa[0] + (pb[0] - pa[0]) * t, pa[1] + (pb[1] - pa[1]) * t, pa[2] + (pb[2] - pa[2]) * t});
        cut.emplace(key, k);
        return k;
    };
    for (size_t q = 0; q < M.F.size() && q < M.C.size(); ++q) {
        const Face& f = M.F[q];
        size_t n = f.size();
        std::vector<int> poly;
        for (size_t i = 0; i < n; ++i) {
            int v = f[i], prev = f[(i + n - 1) % n], nxt = f[(i + 1) % n];
            int first = point(v, prev);                        // (both made before either is used)
            int second = point(v, nxt);
            for (int idx : {first, second})
                if (poly.empty() || poly.back() != idx) poly.push_back(idx);
        }
        if (poly.size() > 1 && poly.front() == poly.back()) poly.pop_back();
        if (poly.size() >= 3) out.add_face(poly, M.C[q]);
    }
    const Color& corner = color;                               // (add.py: rgb(None) is the default grey)
    std::vector<detail::VertexRing> R = detail::rings(M);
    for (size_t v = 0; v < R.size(); ++v) {
        const std::vector<std::pair<int, int>>& ring = R[v].ring;
        if (ring.size() < 3) continue;
        std::vector<int> poly;
        for (auto it = ring.rbegin(); it != ring.rend(); ++it) poly.push_back(point((int)v, it->second));
        std::set<int> distinct(poly.begin(), poly.end());
        if (distinct.size() >= 3) out.add_face(poly, corner);
    }
    return out;
}

inline Mesh color_by_sides(const Mesh& M, const std::map<int, Color>& colors, std::optional<Color> fallback) {
    Mesh out = M;
    for (size_t i = 0; i < M.F.size(); ++i) {
        auto it = colors.find((int)M.F[i].size());
        if (it != colors.end()) out.C[i] = it->second;
        else if (fallback) out.C[i] = *fallback;
    }
    return out;
}

}  // namespace add

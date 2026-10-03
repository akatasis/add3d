// ============================================================================
//  addbind -- add.py's functions for Python values (py::Py), calling add.hpp
// ============================================================================
//  The castle calls add.cylinder(A, B, r, k, colour) with lists and tuples;
//  here each call turns its arguments into add.hpp's points, colours and
//  meshes and calls the C++ function of the same name, which computes the
//  same numbers as add.py.  A mesh that comes back from add.hpp stays a C++
//  mesh until the castle looks into it (M.V, M.F, M.C): only then is it made
//  into lists, as add.py keeps it.
// ============================================================================
#pragma once
#include "pyrt.hpp"

namespace py {

// ---------------------------------------------------------------------------
//  points, colours
// ---------------------------------------------------------------------------
inline add::Point to_point(const Py& p) {
    const Vec& v = p.k == LIST || p.k == TUPLE ? L_(p)->v : items_of(p);
    add::Point q;
    if (v.size() > 0) q.x = v[0].num();
    if (v.size() > 1) q.y = v[1].num();
    if (v.size() > 2) q.z = v[2].num();
    return q;
}
inline add::Point2 to_point2(const Py& p) {
    const Vec& v = p.vec();
    return {v[0].num(), v[1].num()};
}
inline add::Points to_points(const Py& v) {
    add::Points out;
    for (const Py& p : items_of(v)) out.push_back(to_point(p));
    return out;
}
inline add::Profile to_profile(const Py& v) {
    add::Profile out;
    for (const Py& p : items_of(v)) out.push_back(to_point2(p));
    return out;
}
inline Py point_py(const add::Point& p) { return list({Py(p.x), Py(p.y), Py(p.z)}); }
inline Py point2_py(const add::Point2& p) { return list({Py(p.x), Py(p.y)}); }

// add.py's rgb(): anything colour-like as a tuple (r, g, b[, opacity[, image]])
inline Py rgb_py(const Py& c) {
    if (c.is_none() || c.missing()) return tuple({Py(160), Py(160), Py(160)});
    if (c.k == STR) {
        add::Color k(c.str());                          // (named colours and #hex, as add.py reads them)
        if (k.alpha < 1.0) return tuple({Py(k.r), Py(k.g), Py(k.b), Py(k.alpha)});
        return tuple({Py(k.r), Py(k.g), Py(k.b)});
    }
    Vec v = c.k == LIST || c.k == TUPLE ? L_(c)->v : items_of(c);
    Py r = v[0], g = v[1], b = v[2];
    if (r.k == FLOAT && g.k == FLOAT && b.k == FLOAT && std::max(r.f, std::max(g.f, b.f)) <= 1.0) {
        r = Py(r.f * 255.0);
        g = Py(g.f * 255.0);
        b = Py(b.f * 255.0);
    }
    Vec out;
    for (const Py& x : {r, g, b}) {
        int64_t q = round_(x).i;
        out.push_back(Py(q < 0 ? 0 : (q > 255 ? 255 : q)));
    }
    double alpha = 1.0;
    std::string image;
    bool has_image = false;
    if (v.size() > 3 && !v[3].is_none()) {
        alpha = float_(v[3]).f;
        if (alpha > 1.0) alpha /= 255.0;
        alpha = add::detail::py_round(alpha < 0 ? 0.0 : (alpha > 1 ? 1.0 : alpha), 3);
    }
    if (v.size() > 4 && truthy(v[4])) {
        image = str(v[4]);
        has_image = true;
    }
    if (has_image) {
        out.push_back(Py(alpha));
        out.push_back(Py(image));
    } else if (alpha < 1.0) {
        out.push_back(Py(alpha));
    }
    return tuple(std::move(out));
}
inline add::Color color_of_rgb(const Py& t) {          // a tuple from rgb_py
    const Vec& v = t.vec();
    add::Color c((int)v[0].i, (int)v[1].i, (int)v[2].i);
    if (v.size() > 3) c.alpha = v[3].num();
    if (v.size() > 4) c.image = v[4].str();
    return c;
}
inline add::Color to_color(const Py& c) {
    if (c.is_none() || c.missing()) return add::DEFAULT_COLOR;
    return color_of_rgb(rgb_py(c));
}
inline Py color_py(const add::Color& c) {
    if (!c.image.empty()) return tuple({Py(c.r), Py(c.g), Py(c.b), Py(c.alpha), Py(c.image)});
    if (c.alpha < 1.0) return tuple({Py(c.r), Py(c.g), Py(c.b), Py(c.alpha)});
    return tuple({Py(c.r), Py(c.g), Py(c.b)});
}

// ---------------------------------------------------------------------------
//  meshes: a C++ mesh while only add.hpp handles it, lists once looked into
// ---------------------------------------------------------------------------
struct NMeshObj : MeshObj {
    bool native = true;
    add::Mesh nm;
};
inline NMeshObj* N_(const Py& m) { return static_cast<NMeshObj*>(m.o.get()); }
inline Py mesh_py(add::Mesh M) {
    auto o = std::make_shared<NMeshObj>();
    o->nm = std::move(M);
    return Py(MESH, o);
}
inline Py mesh_lists(Py V, Py F, Py C, Py UV = None) {
    auto o = std::make_shared<NMeshObj>();
    o->native = false;
    o->V = V;
    o->F = F;
    o->C = C;
    o->UV = UV;
    return Py(MESH, o);
}
inline void materialize(NMeshObj* o) {
    if (!o->native) return;
    const add::Mesh& M = o->nm;
    Vec V, F, C;
    V.reserve(M.V.size());
    for (const add::Point& p : M.V) V.push_back(point_py(p));
    F.reserve(M.F.size());
    for (const add::Face& f : M.F) {
        Vec idx;
        idx.reserve(f.size());
        for (int i : f) idx.push_back(Py(i));
        F.push_back(list(std::move(idx)));
    }
    C.reserve(M.C.size());
    std::unordered_map<add::Color, Py, add::ColorHash> made;           // (one tuple per colour: add.py's are shared too)
    for (const add::Color& c : M.C) {
        auto it = made.find(c);
        if (it == made.end()) it = made.emplace(c, color_py(c)).first;
        C.push_back(it->second);
    }
    o->V = list(std::move(V));
    o->F = list(std::move(F));
    o->C = list(std::move(C));
    if (M.has_uv) {
        Vec UV;
        for (auto& t : M.UV) {
            if (t.empty()) {
                UV.push_back(None);
                continue;
            }
            Vec q;
            for (auto& p : t) q.push_back(tuple({Py(p.x), Py(p.y)}));
            UV.push_back(list(std::move(q)));
        }
        o->UV = list(std::move(UV));
    } else {
        o->UV = None;
    }
    o->native = false;
    o->nm = add::Mesh();
}
// the lists of a mesh (M.V, M.F, M.C, M.UV)
inline Py& mesh_V(const Py& m) {
    if (m.k != MESH) raise("AttributeError", "'" + type_name(m) + "' object has no attribute 'V'");
    materialize(N_(m));
    return N_(m)->V;
}
inline Py& mesh_F(const Py& m) {
    if (m.k != MESH) raise("AttributeError", "'" + type_name(m) + "' object has no attribute 'F'");
    materialize(N_(m));
    return N_(m)->F;
}
inline Py& mesh_C(const Py& m) {
    if (m.k != MESH) raise("AttributeError", "'" + type_name(m) + "' object has no attribute 'C'");
    materialize(N_(m));
    return N_(m)->C;
}
inline Py& mesh_UV(const Py& m) {
    materialize(N_(m));
    return N_(m)->UV;
}
// a mesh as add.hpp takes it (made from the lists when it has been looked into)
inline add::Mesh native_of(const Py& m) {
    if (m.k != MESH) raise("TypeError", "expected a mesh, got '" + type_name(m) + "'");
    NMeshObj* o = N_(m);
    if (o->native) return o->nm;
    add::Mesh M;
    const Vec& V = o->V.vec();
    M.V.reserve(V.size());
    for (const Py& p : V) {
        const Vec& c = p.vec();
        M.V.push_back({c[0].num(), c[1].num(), c[2].num()});
    }
    const Vec& F = o->F.vec();
    const Vec& C = o->C.vec();
    M.F.reserve(F.size());
    M.C.reserve(F.size());
    std::unordered_map<const Obj*, add::Color> seen;
    for (size_t j = 0; j < F.size(); ++j) {
        add::Face f;
        for (const Py& i : items_of(F[j])) f.push_back((int)i.to_i());
        M.F.push_back(std::move(f));
        const Py& c = C[j];
        auto it = seen.find(c.o.get());
        if (it != seen.end() && c.o) {
            M.C.push_back(it->second);
        } else {
            add::Color col = to_color(c);
            if (c.o) seen.emplace(c.o.get(), col);
            M.C.push_back(col);
        }
    }
    if (!o->UV.is_none()) {
        M.has_uv = true;
        for (const Py& t : o->UV.vec()) {
            std::vector<add::Point2> q;
            if (!t.is_none())
                for (const Py& p : items_of(t)) q.push_back(to_point2(p));
            M.UV.push_back(q);
        }
    }
    return M;
}
// (read-only access without a copy when it is a C++ mesh)
struct NativeRef {
    add::Mesh tmp;
    const add::Mesh* p;
    explicit NativeRef(const Py& m) {
        if (m.k == MESH && N_(m)->native) {
            p = &N_(m)->nm;
        } else {
            tmp = native_of(m);
            p = &tmp;
        }
    }
    const add::Mesh& operator*() const { return *p; }
};

// the methods of a mesh, as add.py's Mesh has them
inline Py mesh_add_vertex(const Py& m, const Py& p) {
    Vec& V = mesh_V(m).vec();
    const Vec& c = p.k == LIST || p.k == TUPLE ? p.vec() : items_of(p);
    V.push_back(list({float_(c[0]), float_(c[1]), float_(c[2])}));
    return Py((int64_t)V.size() - 1);
}
inline Py mesh_add_face(const Py& m, const Py& idx, const Py& color = None, const Py& uv = None) {
    NMeshObj* o = N_(m);
    materialize(o);
    o->F.vec().push_back(list(items_of(idx)));
    o->C.vec().push_back(rgb_py(color.missing() ? None : color));
    if (!uv.is_none() && !uv.missing()) {
        if (o->UV.is_none()) o->UV = list(Vec(o->F.vec().size() - 1, None));
        o->UV.vec().push_back(list(items_of(uv)));
    } else if (!o->UV.is_none()) {
        o->UV.vec().push_back(None);
    }
    return None;
}
inline Py mesh_add_polygon(const Py& m, const Py& points, const Py& color = None) {
    int64_t base = mesh_V(m).vec().size();
    for (const Py& p : items_of(points)) mesh_add_vertex(m, p);
    int64_t n = mesh_V(m).vec().size();
    Vec idx;
    for (int64_t j = base; j < n; ++j) idx.push_back(Py(j));
    return mesh_add_face(m, list(std::move(idx)), color);
}
inline Py mesh_extend(const Py& m, const Py& other) {
    NMeshObj* a = N_(m);
    NMeshObj* b = N_(other);
    if (a->native && b->native) {                     // (both C++ meshes: add.hpp's own extend)
        a->nm.extend(b->nm);
        return m;
    }
    materialize(a);
    materialize(b);
    Vec& V = a->V.vec();
    Vec& F = a->F.vec();
    Vec& C = a->C.vec();
    int64_t shift = V.size();
    for (const Py& p : Vec(b->V.vec())) V.push_back(list(items_of(p)));
    if (!b->UV.is_none() && a->UV.is_none()) a->UV = list(Vec(F.size(), None));
    const Vec bF = b->F.vec(), bC = b->C.vec();
    for (size_t j = 0; j < bF.size() && j < bC.size(); ++j) {
        Vec f;
        for (const Py& i : items_of(bF[j])) f.push_back(Py(i.to_i() + shift));
        F.push_back(list(std::move(f)));
        C.push_back(bC[j]);
    }
    if (!a->UV.is_none()) {
        if (b->UV.is_none()) {
            for (size_t j = 0; j < bF.size(); ++j) a->UV.vec().push_back(None);
        } else {
            for (const Py& t : Vec(b->UV.vec())) a->UV.vec().push_back(t.is_none() ? None : list(items_of(t)));
        }
    }
    return m;
}
inline Py mesh_copy(const Py& m) {
    NMeshObj* o = N_(m);
    if (o->native) return mesh_py(o->nm);
    Vec V, F;
    for (const Py& p : o->V.vec()) V.push_back(list(items_of(p)));
    for (const Py& f : o->F.vec()) F.push_back(list(items_of(f)));
    Py UV = None;
    if (!o->UV.is_none()) {
        Vec u;
        for (const Py& t : o->UV.vec()) u.push_back(t.is_none() ? None : list(items_of(t)));
        UV = list(std::move(u));
    }
    return mesh_lists(list(std::move(V)), list(std::move(F)), list(items_of(o->C)), UV);
}

// ---------------------------------------------------------------------------
//  functions as values: add.cylinder passed to add.make, castle functions
// ---------------------------------------------------------------------------
inline Py native_fn(const char* name, std::vector<std::string> names, size_t nreq, std::function<Py(Vec&)> fn,
                    bool varargs = false, bool kwargs = false) {
    return func(sig(name, std::move(names), {}, nreq, varargs, kwargs), std::move(fn));
}
inline Py dflt(const Py& x, const Py& d) { return x.missing() ? d : x; }
inline bool given(const Py& x) { return !x.missing() && !x.is_none(); }
inline int I(const Py& x) { return x.k == FLOAT ? (int)x.f : (int)x.to_i(); }
inline double D(const Py& x) { return x.num(); }

// a number or a function of t (add.hpp's Scalar)
inline add::Scalar scalar_of(const Py& r) {
    if (r.k == FUNC) {
        Py f = r;
        return add::Scalar([f](double t) { return call(f, {Py(t)}).num(); });
    }
    if (r.is_none() || r.missing()) return add::Scalar();
    return add::Scalar(r.num());
}
template <class... A>
inline add::ColorOf<A...> colorof(const Py& c) {
    if (c.k == FUNC) {
        Py f = c;
        add::ColorOf<A...> out;
        out.fn = [f](A... a) { return color_of_rgb(rgb_py(call(f, {Py(a)...}))); };
        return out;
    }
    return add::ColorOf<A...>(to_color(c));
}
template <>
inline add::ColorOf<add::Point> colorof<add::Point>(const Py& c) {
    if (c.k == FUNC) {
        Py f = c;
        add::ColorOf<add::Point> out;
        out.fn = [f](add::Point p) { return color_of_rgb(rgb_py(call(f, {point_py(p)}))); };
        return out;
    }
    return add::ColorOf<add::Point>(to_color(c));
}

}  // namespace py

// ===========================================================================
//  add.<name>(...) for the castle: addpy::<name>
// ===========================================================================
namespace addpy {
using namespace py;

inline const Py pi = Py(add::pi);
inline Py sin(const Py& x) { return Py(std::sin(x.num())); }
inline Py cos(const Py& x) { return Py(std::cos(x.num())); }
inline Py tan(const Py& x) { return Py(std::tan(x.num())); }
inline Py asin(const Py& x) {
    double v = x.num();
    if (v < -1.0 || v > 1.0) raise("ValueError", "math domain error");
    return Py(std::asin(v));
}
inline Py acos(const Py& x) {
    double v = x.num();
    if (v < -1.0 || v > 1.0) raise("ValueError", "math domain error");
    return Py(std::acos(v));
}
inline Py atan(const Py& x) { return Py(std::atan(x.num())); }
inline Py atan2(const Py& y, const Py& x) { return Py(std::atan2(y.num(), x.num())); }
inline Py sqrt(const Py& x) {
    double v = x.num();
    if (v < 0.0) raise("ValueError", "math domain error");
    return Py(std::sqrt(v));
}
inline Py exp(const Py& x) { return Py(std::exp(x.num())); }
inline Py hypot(const Py& x, const Py& y) { return Py(std::hypot(x.num(), y.num())); }
inline Py radians(const Py& x) { return Py(x.num() * (add::pi / 180.0)); }
inline Py floor(const Py& x) {
    if (x.is_int()) return Py(x.i);
    return Py((int64_t)std::floor(x.num()));
}
inline Py ceil(const Py& x) {
    if (x.is_int()) return Py(x.i);
    return Py((int64_t)std::ceil(x.num()));
}
inline Py clamp(const Py& x, const Py& lo = Py(0.0), const Py& hi = Py(1.0)) {
    Py l = dflt(lo, Py(0.0)), h = dflt(hi, Py(1.0));
    return lt(x, l) ? l : (lt(h, x) ? h : x);
}
inline Py lerp(const Py& a, const Py& b, const Py& t) {
    if (a.is_num()) return a + (b - a) * t;
    Vec out;
    const Vec& va = a.vec();
    const Vec& vb = b.vec();
    for (size_t j = 0; j < va.size(); ++j) out.push_back(va[j] + (vb[j] - va[j]) * t);
    return list(std::move(out));
}
inline Py rgb(const Py& c) { return rgb_py(c); }
inline Py shade(const Py& color, const Py& factor) {
    Vec c = rgb_py(color).vec();
    Py r = c[0], g = c[1], b = c[2];
    if (factor <= Py(1.0)) return tuple({int_(r * factor), int_(g * factor), int_(b * factor)});
    Py t = min2(Py(1.0), factor - Py(1.0));
    return tuple({int_(r + (Py(255) - r) * t), int_(g + (Py(255) - g) * t), int_(b + (Py(255) - b) * t)});
}
inline Py transparent(const Py& color, const Py& alpha = Py(0.5)) {
    Vec c = rgb_py(color).vec();
    Vec t = {c[0], c[1], c[2], dflt(alpha, Py(0.5))};
    if (c.size() > 4) t.push_back(c[4]);
    return rgb_py(tuple(t));
}

// random numbers: Python's own sequence
inline Py seed(const Py& a) {
    add::detail::rng().seed(a.to_i());
    return None;
}
inline Py random() { return Py(add::detail::rng().random()); }
inline Py uniform(const Py& a, const Py& b) {
    double r = add::detail::rng().random();
    return a + (b - a) * Py(r);
}
inline Py choice(const Py& seq) {
    Vec v = items_of(seq);
    if (v.empty()) raise("IndexError", "Cannot choose from an empty sequence");
    return v[(size_t)add::detail::rng().randbelow((long long)v.size())];
}

// the scene
inline Py push() {
    add::push();
    return None;
}
inline Py pop() { return mesh_py(add::pop()); }
inline Py layer() { return mesh_py(add::layer()); }
inline Py mesh(const Py& M) {
    NativeRef n(M);
    add::mesh(*n);
    return M;
}
template <class F>
inline Py make(F&& draw) {
    add::push();
    draw();
    return mesh_py(add::pop());
}
inline Py Mesh(const Py& V = None, const Py& F = None, const Py& C = None, const Py& UV = None) {
    return mesh_lists(given(V) ? V : list(), given(F) ? F : list(), given(C) ? C : list(), given(UV) ? UV : None);
}

// drawing
inline Py polygon(const Py& points, const Py& color = None) {
    add::polygon(to_points(points), to_color(color));
    return None;
}
inline Py triangle(const Py& a, const Py& b, const Py& c, const Py& color = None) {
    add::triangle(to_point(a), to_point(b), to_point(c), to_color(color));
    return None;
}
inline Py quad(const Py& a, const Py& b, const Py& c, const Py& d, const Py& color = None) {
    add::quad(to_point(a), to_point(b), to_point(c), to_point(d), to_color(color));
    return None;
}
inline Py cuboid(const Py& center, const Py& sizes, const Py& color = None) {
    add::cuboid(to_point(center), to_point(sizes), to_color(color));
    return None;
}
inline Py pyramid(const Py& center, const Py& edge, const Py& height, const Py& color = None) {
    add::pyramid(to_point(center), D(edge), D(height), to_color(color));
    return None;
}
inline Py prism(const Py& profile, const Py& height, const Py& color = None, const Py& center = MISSING_,
                const Py& axis = MISSING_) {
    add::prism(to_profile(profile), D(height), to_color(color), given(center) ? to_point(center) : add::Point{0, 0, 0},
               given(axis) ? to_point(axis) : add::Point{0, 1, 0});
    return None;
}
inline Py octahedron(const Py& center = MISSING_, const Py& r = MISSING_, const Py& color = None) {
    add::octahedron(given(center) ? to_point(center) : add::Point{0, 0, 0}, given(r) ? D(r) : 1.0, to_color(color));
    return None;
}
inline Py icosahedron(const Py& center = MISSING_, const Py& r = MISSING_, const Py& color = None) {
    add::icosahedron(given(center) ? to_point(center) : add::Point{0, 0, 0}, given(r) ? D(r) : 1.0, to_color(color));
    return None;
}
inline Py sphere(const Py& center, const Py& r, const Py& k = MISSING_, const Py& color = None, const Py& subdivisions = None) {
    std::optional<int> sub;
    if (given(subdivisions)) sub = I(subdivisions);
    add::sphere(to_point(center), D(r), given(k) ? I(k) : 10, colorof<add::Point>(color), sub);
    return None;
}
inline Py ellipsoid(const Py& center, const Py& radii, const Py& k = MISSING_, const Py& color = None) {
    add::ellipsoid(to_point(center), to_point(radii), given(k) ? I(k) : 10, to_color(color));
    return None;
}
inline Py torus(const Py& center, const Py& R, const Py& r, const Py& nu = MISSING_, const Py& nv = MISSING_,
                const Py& color = None, const Py& axis = MISSING_) {
    add::torus(to_point(center), D(R), D(r), given(nu) ? I(nu) : 48, given(nv) ? I(nv) : 24, to_color(color),
               given(axis) ? to_point(axis) : add::Point{0, 1, 0});
    return None;
}
inline Py cylinder(const Py& A, const Py& B, const Py& r, const Py& k = MISSING_, const Py& color = None) {
    add::cylinder(to_point(A), to_point(B), D(r), given(k) ? I(k) : 24, to_color(color));
    return None;
}
inline Py cup(const Py& A, const Py& B, const Py& r, const Py& k = MISSING_, const Py& color = None) {
    add::cup(to_point(A), to_point(B), D(r), given(k) ? I(k) : 24, to_color(color));
    return None;
}
inline Py cone(const Py& A, const Py& B, const Py& r, const Py& k = MISSING_, const Py& color = None) {
    add::cone(to_point(A), to_point(B), D(r), given(k) ? I(k) : 24, to_color(color));
    return None;
}
inline Py frustum(const Py& A, const Py& B, const Py& r1, const Py& r2, const Py& k = MISSING_, const Py& color = None,
                  const Py& caps = MISSING_) {
    add::frustum(to_point(A), to_point(B), D(r1), D(r2), given(k) ? I(k) : 24, to_color(color),
                 caps.missing() ? true : truthy(caps));
    return None;
}
inline Py pipe(const Py& A, const Py& B, const Py& r_outer, const Py& r_inner, const Py& k = MISSING_, const Py& color = None) {
    add::pipe(to_point(A), to_point(B), D(r_outer), D(r_inner), given(k) ? I(k) : 24, to_color(color));
    return None;
}
inline Py capsule(const Py& A, const Py& B, const Py& r, const Py& k = MISSING_, const Py& color = None) {
    add::capsule(to_point(A), to_point(B), D(r), given(k) ? I(k) : 24, to_color(color));
    return None;
}
inline Py hemisphere(const Py& center, const Py& r, const Py& k = MISSING_, const Py& color = None, const Py& axis = MISSING_) {
    add::hemisphere(to_point(center), D(r), given(k) ? I(k) : 16, colorof<double, double>(color),
                    given(axis) ? to_point(axis) : add::Point{0, 1, 0});
    return None;
}
inline Py helix(const Py& center, const Py& r, const Py& pitch, const Py& turns, const Py& k = MISSING_,
                const Py& thickness = MISSING_, const Py& sides = MISSING_, const Py& color = None, const Py& axis = MISSING_) {
    add::helix(to_point(center), D(r), D(pitch), D(turns), given(k) ? I(k) : 200, given(thickness) ? D(thickness) : 0.1,
               given(sides) ? I(sides) : 12, to_color(color), given(axis) ? to_point(axis) : add::Point{0, 1, 0});
    return None;
}
inline Py beam(const Py& A, const Py& B, const Py& width, const Py& height = None, const Py& color = None,
               const Py& up = MISSING_) {
    std::optional<double> h;
    if (given(height)) h = D(height);
    add::beam(to_point(A), to_point(B), D(width), h, to_color(color), given(up) ? to_point(up) : add::Point{0, 1, 0});
    return None;
}
inline Py arch(const Py& A, const Py& B, const Py& height, const Py& thickness, const Py& color = None,
               const Py& steps = MISSING_, const Py& k = MISSING_, const Py& up = MISSING_) {
    int st = given(steps) ? I(steps) : 32, kk = given(k) ? I(k) : 12;
    add::Point u = given(up) ? to_point(up) : add::Point{0, 1, 0};
    if (thickness.k == LIST || thickness.k == TUPLE)
        add::arch(to_point(A), to_point(B), D(height), to_point2(thickness), to_color(color), st, kk, u);
    else
        add::arch(to_point(A), to_point(B), D(height), D(thickness), to_color(color), st, kk, u);
    return None;
}
inline Py wheel(const Py& center, const Py& r, const Py& width, const Py& color = MISSING_, const Py& axis = MISSING_,
                const Py& k = MISSING_, const Py& spokes = MISSING_, const Py& hub_color = MISSING_) {
    add::wheel(to_point(center), D(r), D(width), color.missing() ? add::Color("black") : to_color(color),
               given(axis) ? to_point(axis) : add::Point{0, 0, 1}, given(k) ? I(k) : 32, given(spokes) ? I(spokes) : 0,
               hub_color.missing() ? add::Color("silver") : to_color(hub_color));
    return None;
}
inline Py polyline(const Py& points, const Py& r = MISSING_, const Py& k = MISSING_, const Py& color = None,
                   const Py& closed = MISSING_, const Py& smooth = MISSING_) {
    add::polyline(to_points(points), r.missing() ? add::Scalar(0.1) : scalar_of(r), given(k) ? I(k) : 12,
                  colorof<double, double>(color), closed.missing() ? false : truthy(closed), given(smooth) ? I(smooth) : 0);
    return None;
}
inline Py loft(const Py& sections, const Py& color = None, const Py& closed = MISSING_, const Py& caps = MISSING_,
               const Py& flip = MISSING_) {
    std::vector<add::Points> s;
    for (const Py& ring : items_of(sections)) s.push_back(to_points(ring));
    add::loft(s, to_color(color), closed.missing() ? false : truthy(closed), caps.missing() ? true : truthy(caps),
              flip.missing() ? false : truthy(flip));
    return None;
}
inline Py revolve(const Py& profile, const Py& A = MISSING_, const Py& B = MISSING_, const Py& t0 = MISSING_,
                  const Py& t1 = MISSING_, const Py& steps = MISSING_, const Py& k = MISSING_, const Py& color = None,
                  const Py& angle = MISSING_, const Py& caps = MISSING_) {
    add::Point a = given(A) ? to_point(A) : add::Point{0, 0, 0}, b = given(B) ? to_point(B) : add::Point{0, 1, 0};
    double u0 = given(t0) ? D(t0) : 0.0, u1 = given(t1) ? D(t1) : 1.0, ang = given(angle) ? D(angle) : 2.0 * add::pi;
    int st = given(steps) ? I(steps) : 40, kk = given(k) ? I(k) : 32;
    bool cp = caps.missing() ? true : truthy(caps);
    if (profile.k == FUNC) {
        Py f = profile;
        std::function<add::Point2(double)> pf = [f](double t) { return to_point2(call(f, {Py(t)})); };
        add::revolve(pf, a, b, u0, u1, st, kk, colorof<double, double>(color), ang, cp);
    } else {
        add::revolve(to_profile(profile), a, b, u0, u1, st, kk, colorof<double, double>(color), ang, cp);
    }
    return None;
}
inline Py parametric(const Py& S, const Py& min_u, const Py& max_u, const Py& grid_u, const Py& min_v, const Py& max_v,
                     const Py& grid_v, const Py& RGB = None, const Py& wrap_u = MISSING_, const Py& wrap_v = MISSING_,
                     const Py& flip = MISSING_, const Py& thickness = MISSING_, const Py& double_sided = MISSING_,
                     const Py& color = None) {
    Py f = S;
    add::SurfaceFn fn = [f](double u, double v) { return to_point(call(f, {Py(u), Py(v)})); };
    Py c = given(color) ? color : RGB;
    add::parametric(fn, D(min_u), D(max_u), I(grid_u), D(min_v), D(max_v), I(grid_v), colorof<double, double>(c),
                    wrap_u.missing() ? false : truthy(wrap_u), wrap_v.missing() ? false : truthy(wrap_v),
                    flip.missing() ? false : truthy(flip), given(thickness) ? D(thickness) : 0.0,
                    double_sided.missing() ? false : truthy(double_sided));
    return None;
}
inline Py sweep(const Py& profile, const Py& path, const Py& t0 = MISSING_, const Py& t1 = MISSING_, const Py& steps = MISSING_,
                const Py& color = None, const Py& closed = MISSING_, const Py& scale = None, const Py& twist = None,
                const Py& caps = MISSING_) {
    Py f = path;
    add::PathFn pf = [f](double t) { return to_point(call(f, {Py(t)})); };
    add::sweep(to_profile(profile), pf, given(t0) ? D(t0) : 0.0, given(t1) ? D(t1) : 1.0, given(steps) ? I(steps) : 100,
               colorof<double, int>(color), closed.missing() ? false : truthy(closed), scalar_of(scale), scalar_of(twist),
               caps.missing() ? true : truthy(caps));
    return None;
}
inline Py text(const Py& string, const Py& at = MISSING_, const Py& size = MISSING_, const Py& thickness = None,
               const Py& color = None, const Py& u = MISSING_, const Py& v = MISSING_, const Py& align = MISSING_,
               const Py& spacing = MISSING_, const Py& k = MISSING_) {
    std::optional<double> th;
    if (given(thickness)) th = D(thickness);
    double w = add::text(string.str(), given(at) ? to_point(at) : add::Point{0, 0, 0}, given(size) ? D(size) : 1.0, th,
                         to_color(color), given(u) ? to_point(u) : add::Point{1, 0, 0}, given(v) ? to_point(v) : add::Point{0, 1, 0},
                         given(align) ? align.str() : std::string("left"), given(spacing) ? D(spacing) : 1.0, given(k) ? I(k) : 8);
    return Py(w);
}
inline Py text_width(const Py& string, const Py& size = MISSING_, const Py& spacing = MISSING_) {
    return Py(add::text_width(string.str(), given(size) ? D(size) : 1.0, given(spacing) ? D(spacing) : 1.0));
}

// meshes in, meshes out
inline Py move(const Py& M, const Py& V) { return mesh_py(add::move(*NativeRef(M), to_point(V))); }
inline Py rotateX(const Py& M, const Py& angle, const Py& P = MISSING_) {
    return mesh_py(add::rotateX(*NativeRef(M), D(angle), given(P) ? to_point(P) : add::Point{0, 0, 0}));
}
inline Py rotateY(const Py& M, const Py& angle, const Py& P = MISSING_) {
    return mesh_py(add::rotateY(*NativeRef(M), D(angle), given(P) ? to_point(P) : add::Point{0, 0, 0}));
}
inline Py rotateZ(const Py& M, const Py& angle, const Py& P = MISSING_) {
    return mesh_py(add::rotateZ(*NativeRef(M), D(angle), given(P) ? to_point(P) : add::Point{0, 0, 0}));
}
inline Py rotate(const Py& M, const Py& axis, const Py& angle, const Py& P = MISSING_) {
    return mesh_py(add::rotate(*NativeRef(M), to_point(axis), D(angle), given(P) ? to_point(P) : add::Point{0, 0, 0}));
}
inline Py stretch(const Py& M, const Py& s, const Py& about = None) {
    std::optional<add::Point> a;
    if (given(about)) a = to_point(about);
    return mesh_py(add::stretch(*NativeRef(M), to_point(s), a));
}
inline Py mirror(const Py& M, const Py& point = MISSING_, const Py& normal = MISSING_) {
    return mesh_py(add::mirror(*NativeRef(M), given(point) ? to_point(point) : add::Point{0, 0, 0},
                               given(normal) ? to_point(normal) : add::Point{1, 0, 0}));
}
inline Py transform(const Py& M, const Py& matrix) {
    std::vector<std::vector<double>> m;
    for (const Py& row : items_of(matrix)) {
        std::vector<double> r;
        for (const Py& x : items_of(row)) r.push_back(x.num());
        m.push_back(r);
    }
    return mesh_py(add::transform(*NativeRef(M), m));
}
inline Py aim(const Py& M, const Py& direction, const Py& axis = MISSING_, const Py& P = MISSING_) {
    return mesh_py(add::aim(*NativeRef(M), to_point(direction), given(axis) ? to_point(axis) : add::Point{0, 1, 0},
                            given(P) ? to_point(P) : add::Point{0, 0, 0}));
}
inline Py deform(const Py& M, const Py& f) {
    Py fn = f;
    return mesh_py(add::deform(*NativeRef(M), [fn](const add::Point& p) { return to_point(call(fn, {point_py(p)})); }));
}
inline Py color(const Py& M, const Py& RGB) { return mesh_py(add::color(*NativeRef(M), to_color(RGB))); }
inline Py color_by(const Py& M, const Py& fn) {
    Py f = fn;
    return mesh_py(add::color_by(*NativeRef(M), [f](const add::Point& p) { return color_of_rgb(rgb_py(call(f, {point_py(p)}))); }));
}
inline Py cut(const Py& M, const Py& point = MISSING_, const Py& normal = MISSING_, const Py& cap = MISSING_,
              const Py& color = None) {
    std::optional<add::Color> c;
    if (given(color)) c = to_color(color);
    return mesh_py(add::cut(*NativeRef(M), given(point) ? to_point(point) : add::Point{0, 0, 0},
                            given(normal) ? to_point(normal) : add::Point{0, 1, 0}, cap.missing() ? true : truthy(cap), c));
}
inline Py fix_normals(const Py& M = None, const Py& outward = MISSING_) {
    bool out = outward.missing() ? true : truthy(outward);
    if (!given(M)) return mesh_py(add::fix_normals(add::scene(), out));
    return mesh_py(add::fix_normals(*NativeRef(M), out));
}
inline Py clean(const Py& M = None, const Py& tol = MISSING_, const Py& weld = MISSING_, const Py& degenerate = MISSING_,
                const Py& duplicates = MISSING_, const Py& internal = MISSING_, const Py& unused = MISSING_,
                const Py& normals = MISSING_, const Py& report = MISSING_, const Py& overlaps = MISSING_,
                const Py& convex = MISSING_) {
    auto b = [](const Py& x, bool d) { return x.missing() ? d : truthy(x); };
    if (b(report, false)) raise("NotImplementedError", "clean(report=True)");
    double t = given(tol) ? D(tol) : 1e-7;
    if (!given(M))
        return mesh_py(add::clean(add::scene(), t, b(weld, true), b(degenerate, true), b(duplicates, true), b(internal, true),
                                  b(unused, true), b(normals, false), nullptr, b(overlaps, true), b(convex, true)));
    return mesh_py(add::clean(*NativeRef(M), t, b(weld, true), b(degenerate, true), b(duplicates, true), b(internal, true),
                              b(unused, true), b(normals, false), nullptr, b(overlaps, true), b(convex, true)));
}
inline Py solidify(const Py& M = None, const Py& thickness = MISSING_, const Py& both_ways = MISSING_) {
    double t = given(thickness) ? D(thickness) : 0.1;
    bool bw = both_ways.missing() ? true : truthy(both_ways);
    if (!given(M)) return mesh_py(add::solidify(add::scene(), t, bw));
    return mesh_py(add::solidify(*NativeRef(M), t, bw));
}
inline Py bbox(const Py& M = None) {
    std::array<add::Point, 2> b = given(M) ? add::bbox(*NativeRef(M)) : add::bbox();
    if (given(M) && !N_(M)->native) {                   // (add.py keeps the numbers as they are in M.V)
        const Vec& V = N_(M)->V.vec();
        if (V.empty()) return list({list({Py(0), Py(0), Py(0)}), list({Py(0), Py(0), Py(0)})});
        Vec lo, hi;
        for (int a = 0; a < 3; ++a) {
            Py l = V[0].vec()[a], h = V[0].vec()[a];
            for (const Py& p : V) {
                const Py& c = p.vec()[a];
                if (lt(c, l)) l = c;
                if (lt(h, c)) h = c;
            }
            lo.push_back(l);
            hi.push_back(h);
        }
        return list({list(lo), list(hi)});
    }
    const add::Mesh& m = given(M) ? *NativeRef(M) : add::scene();
    if (m.V.empty()) return list({list({Py(0), Py(0), Py(0)}), list({Py(0), Py(0), Py(0)})});
    return list({point_py(b[0]), point_py(b[1])});
}
inline void flatten_into(std::vector<add::Mesh>& out, const Py& x) {
    if (x.k == MESH) {
        out.push_back(native_of(x));
    } else if (x.k == LIST || x.k == TUPLE) {
        for (const Py& y : L_(x)->v) flatten_into(out, y);
    } else {
        raise("TypeError", "expected a mesh, got '" + type_name(x) + "'");
    }
}
inline Py difference(const Py& A, const Py& others, const Py& color = None) {     // (others: the tuple of *others)
    std::vector<add::Mesh> o;
    flatten_into(o, others);
    std::optional<add::Color> paint;
    if (given(color)) paint = to_color(color);
    return mesh_py(add::difference(*NativeRef(A), o, paint));
}
inline Py union_(const Py& meshes) {
    std::vector<add::Mesh> o;
    flatten_into(o, meshes);
    return mesh_py(add::union_(o));
}
inline Py intersect(const Py& meshes) {
    std::vector<add::Mesh> o;
    flatten_into(o, meshes);
    return mesh_py(add::intersect(o));
}

// files written part by part
inline Py stream(const Py& path, const Py& clean = MISSING_, const Py& precision = None) {
    auto s = std::make_shared<StreamObj>();
    std::optional<int> p;
    if (given(precision)) p = I(precision);
    s->s = add::stream(path.str(), clean.missing() ? true : truthy(clean), p);
    return Py(STREAM, s);
}

}  // namespace addpy

namespace py {
inline add::Stream& stream_of(const Py& s) {
    if (s.k != STREAM) raise("TypeError", "not a Stream");
    return *static_cast<StreamObj*>(s.o.get())->s;
}
inline Py stream_add(const Py& s, const Py& M, const Py& clean = MISSING_) {
    std::optional<bool> c;
    if (!clean.missing() && !clean.is_none()) c = truthy(clean);
    return Py((int64_t)stream_of(s).add(*NativeRef(M), c));
}
inline Py stream_close(const Py& s) { return Py(stream_of(s).close()); }
}  // namespace py

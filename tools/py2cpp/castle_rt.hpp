// ============================================================================
//  castle_rt -- the last pieces: list/dict/mesh methods, the castle's Spots
// ============================================================================
#pragma once
#include "addbind.hpp"

namespace py {

inline Py Py::extend(const Py& x) const {
    if (k == LIST) {
        Vec w = items_of(x);
        L_(*this)->v.insert(L_(*this)->v.end(), w.begin(), w.end());
        return None;
    }
    if (k == MESH) return mesh_extend(*this, x);
    raise("AttributeError", "'" + type_name(*this) + "' object has no attribute 'extend'");
}
inline Py Py::copy() const {
    switch (k) {
        case LIST: return list(L_(*this)->v);
        case DICT: return dict_copy(*this);
        case SET: {
            Py s = set_();
            S_(*this)->d.each([&](const Py& kk, const Py&) { S_(s)->d.set(kk, None); });
            return s;
        }
        case MESH: return mesh_copy(*this);
        default: raise("AttributeError", "'" + type_name(*this) + "' object has no attribute 'copy'");
    }
}
inline Py Py::pop(const Py& key, const Py& dflt) const {
    if (k == LIST) {
        Vec& v = L_(*this)->v;
        if (v.empty()) raise("IndexError", "pop from empty list");
        size_t j = norm_index(key.missing() ? -1 : key.to_i(), v.size(), "pop");
        Py x = v[j];
        v.erase(v.begin() + j);
        return x;
    }
    if (k == DICT) {
        Py out;
        if (D_(*this)->erase(key, &out)) return out;
        if (!dflt.missing()) return dflt;
        raise("KeyError", repr(key));
    }
    raise("AttributeError", "'" + type_name(*this) + "' object has no attribute 'pop'");
}

inline void slice_assign(const Py& x, const Py& a, const Py& b, const Py& c, const Py& v) {
    if (!(c.is_none() || c.missing()) && c.to_i() != 1) raise("NotImplementedError", "extended slice assignment");
    Vec& w = x.vec();
    int64_t st, sp, se;
    slice_indices((int64_t)w.size(), a, b, None, st, sp, se);
    if (sp < st) sp = st;
    Vec items = items_of(v);
    w.erase(w.begin() + st, w.begin() + sp);
    w.insert(w.begin() + st, items.begin(), items.end());
}

// objects of the castle's own class, Spots: points on a grid of 0.5 m cells
inline Py inst_attr(const Py& o, const char* name) {
    if (o.k != INST) raise("AttributeError", "'" + type_name(o) + "' object has no attribute '" + name + "'");
    Py* p = I_(o)->attrs.find(Py(name));
    if (!p) raise("AttributeError", std::string("no attribute '") + name + "'");
    return *p;
}
inline void inst_set(const Py& o, const char* name, const Py& v) { I_(o)->attrs.set(Py(name), v); }
inline Py spots_add(const Py& self, const Py& p) {
    // self.cells.setdefault((int(p[0] // 0.5), int(p[1] // 0.5)), []).append(p)
    Py key = tuple({int_(floordiv(p[0], Py(0.5))), int_(floordiv(p[1], Py(0.5)))});
    inst_attr(self, "cells").setdefault(key, list()).append(p);
    return None;
}
inline Py Spots(const Py& points = MISSING_) {
    auto o = std::make_shared<InstObj>();
    o->cls = "Spots";
    Py self(INST, o);
    inst_set(self, "cells", dict());
    if (!points.missing())
        for (const Py& p : items_of(points)) spots_add(self, p);
    return self;
}
inline Py method_near(const Py& self, const Py& x, const Py& z, const Py& d) {
    // any((x - p[0]) ** 2 + (z - p[1]) ** 2 < d * d for a in range(i - k, i + k + 1)
    //     for b in range(j - k, j + k + 1) for p in self.cells.get((a, b), ()))
    int64_t k = int_(floordiv(d, Py(0.5))).i + 1;
    int64_t i = int_(floordiv(x, Py(0.5))).i, j = int_(floordiv(z, Py(0.5))).i;
    Py cells = inst_attr(self, "cells");
    Py dd = d * d;
    for (int64_t a = i - k; a < i + k + 1; ++a)
        for (int64_t b = j - k; b < j + k + 1; ++b) {
            Py* got = D_(cells)->find(tuple({Py(a), Py(b)}));
            if (!got) continue;
            for (const Py& p : items_of(*got))
                if (pow_(x - p[0], Py(2)) + pow_(z - p[1], Py(2)) < dd) return True;
        }
    return False;
}
inline Py method_add(const Py& o, const Py& x, const Py& clean = MISSING_) {
    switch (o.k) {
        case SET: S_(o)->d.set(x, None); return None;
        case STREAM: return stream_add(o, x, clean);
        case INST: return spots_add(o, x);
        default: raise("AttributeError", "'" + type_name(o) + "' object has no attribute 'add'");
    }
}
inline Py stream_attr(const Py& s, const char* name) {
    add::Stream& st = stream_of(s);
    std::string n = name;
    if (n == "faces") return Py((int64_t)st.faces);
    if (n == "vertices") return Py((int64_t)st.vertices);
    if (n == "bytes") return Py((int64_t)st.bytes);
    if (n == "materials") {
        Vec m;
        for (auto& c : st.materials) m.push_back(tuple({color_py(c.first), Py(c.second)}));
        return list(std::move(m));
    }
    raise("AttributeError", "Stream has no attribute '" + n + "'");
}

// add.py's functions used as values
inline const Py ADDF_floor = func(sig("floor", {"x"}, {}, 1), [](Vec& p) -> Py { return addpy::floor(p[0]); });

}  // namespace py

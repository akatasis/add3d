// ============================================================================
//  pyrt -- the few pieces of Python that 46_castle.cpp needs, in C++
// ============================================================================
//
//  46_castle.cpp is 46_castle.py line by line.  Python's values -- numbers,
//  strings, lists, tuples, dicts, functions, meshes -- are all one C++ type
//  here, ``Py``, with Python's rules: 7 // 2 is 3, -7 // 2 is -4, 1 / 2 is
//  0.5, a list is shared by everyone who holds it, a dict keeps the order
//  its keys came in, sorted() is stable, and the floats are IEEE doubles
//  computed in the same order -- so the model comes out the same, number for
//  number.
// ============================================================================
#pragma once
#include "add.hpp"
#include <cfenv>
#include <chrono>

namespace py {

struct Obj {
    virtual ~Obj() = default;
};

enum Kind : uint8_t { NONE, BOOL, INT, FLOAT, STR, LIST, TUPLE, DICT, SET, FUNC, MESH, INST, STREAM, MISSING };

struct Py;
using Vec = std::vector<Py>;
struct Args;

// Python stops a program with a traceback; the castle never catches anything, so here an error is the end too
[[noreturn]] inline void raise(const std::string& kind, const std::string& msg) noexcept {
    std::fflush(stdout);
    std::fprintf(stderr, "Error -- %s: %s\n", kind.c_str(), msg.c_str());
    std::exit(1);
}

struct Py {
    Kind k = NONE;
    union {
        int64_t i;
        double f;
    };
    std::shared_ptr<Obj> o;

    Py() : i(0) {}
    Py(std::nullptr_t) : i(0) {}
    Py(bool v) : k(BOOL), i(v ? 1 : 0) {}
    Py(int v) : k(INT), i(v) {}
    Py(long v) : k(INT), i(v) {}
    Py(long long v) : k(INT), i(v) {}
    Py(unsigned v) : k(INT), i(v) {}
    Py(unsigned long v) : k(INT), i((int64_t)v) {}
    Py(unsigned long long v) : k(INT), i((int64_t)v) {}
    Py(double v) : k(FLOAT), f(v) {}
    Py(const char* s);
    Py(const std::string& s);
    Py(Kind kind, std::shared_ptr<Obj> obj) : k(kind), i(0), o(std::move(obj)) {}
    Py(const Py&) = default;
    Py(Py&&) = default;
    Py& operator=(const Py&) = default;
    Py& operator=(Py&&) = default;
    ~Py() = default;

    bool is_none() const { return k == NONE; }
    bool missing() const { return k == MISSING; }
    bool is_num() const { return k == INT || k == FLOAT || k == BOOL; }
    bool is_int() const { return k == INT || k == BOOL; }
    double num() const;                 // as a double (int, bool, float)
    int64_t to_i() const;               // an int (or bool)

    // the containers
    Vec& vec() const;                   // a list's or tuple's items
    const std::string& str() const;

    Py operator[](const Py& key) const;   // reading an item: x[i], d[k]
    Py operator[](int key) const { return (*this)[Py(key)]; }

    // the methods add.py and the castle use
    Py append(const Py& x) const;
    Py extend(const Py& x) const;
    Py insert(const Py& i, const Py& x) const;
    Py pop(const Py& key = Py(Kind::MISSING, nullptr), const Py& dflt = Py(Kind::MISSING, nullptr)) const;
    Py get(const Py& key, const Py& dflt = Py()) const;
    Py setdefault(const Py& key, const Py& dflt = Py()) const;
    Py items() const;
    Py keys() const;
    Py values() const;
    Py update(const Py& other) const;
    Py copy() const;
    Py index(const Py& x) const;
    Py reverse() const;
    Py sort(const Py& key = Py(), const Py& rev = Py(false)) const;
    Py join(const Py& seq) const;
    Py startswith(const Py& s) const;
    Py count(const Py& x) const;
};

// a string or a tuple of constants in the source: made once, the first time it is met (Python keeps them as constants)
#define S(lit) ([]() -> const ::py::Py& { static const ::py::Py s_(lit); return s_; }())
#define K(expr) ([&]() -> const ::py::Py& { static const ::py::Py k_(expr); return k_; }())

inline const Py None = Py();
inline const Py True = Py(true);
inline const Py False = Py(false);
inline const Py MISSING_ = Py(Kind::MISSING, nullptr);
#define MISSING_ARG ::py::MISSING_

// ---------------------------------------------------------------------------
//  the objects
// ---------------------------------------------------------------------------
struct StrObj : Obj {
    std::string s;
    explicit StrObj(std::string v) : s(std::move(v)) {}
};
struct ListObj : Obj {                  // a list or a tuple
    Vec v;
    ListObj() {}
    explicit ListObj(Vec x) : v(std::move(x)) {}
};

size_t hash_of(const Py& x);
bool eq(const Py& a, const Py& b);
struct PyHash {
    size_t operator()(const Py& x) const { return hash_of(x); }
};
struct PyEq {
    bool operator()(const Py& a, const Py& b) const { return eq(a, b); }
};

struct DictObj : Obj {                  // keys in the order they came, as Python's dict
    std::vector<std::pair<Py, Py>> items;
    std::vector<char> dead;
    std::unordered_map<Py, size_t, PyHash, PyEq> index;
    size_t live = 0;
    Py* find(const Py& k) {
        auto it = index.find(k);
        return it == index.end() ? nullptr : &items[it->second].second;
    }
    void set(const Py& k, const Py& v) {
        auto it = index.find(k);
        if (it != index.end()) {
            items[it->second].second = v;
            return;
        }
        index.emplace(k, items.size());
        items.emplace_back(k, v);
        dead.push_back(0);
        ++live;
    }
    bool erase(const Py& k, Py* out) {
        auto it = index.find(k);
        if (it == index.end()) return false;
        size_t at = it->second;
        if (out) *out = items[at].second;
        index.erase(it);
        dead[at] = 1;
        items[at] = {Py(), Py()};
        --live;
        if (live * 2 < items.size() && items.size() > 32) compact();
        return true;
    }
    void compact() {
        std::vector<std::pair<Py, Py>> keep;
        keep.reserve(live);
        for (size_t j = 0; j < items.size(); ++j)
            if (!dead[j]) keep.push_back(std::move(items[j]));
        items = std::move(keep);
        dead.assign(items.size(), 0);
        index.clear();
        for (size_t j = 0; j < items.size(); ++j) index.emplace(items[j].first, j);
    }
    template <class F>
    void each(F f) const {
        for (size_t j = 0; j < items.size(); ++j)
            if (!dead[j]) f(items[j].first, items[j].second);
    }
};
struct SetObj : Obj {                   // (iterated in the order the items came: the castle sorts what it iterates)
    DictObj d;
};
struct Sig {                            // a function's parameters: names, defaults (MISSING: none)
    std::string name;
    std::vector<std::string> names;
    Vec defaults;
    size_t nreq = 0;                    // (the ones after these may be left out: MISSING, the function's own default)
    bool varargs = false, kwargs = false;
};
struct FuncObj : Obj {
    std::shared_ptr<Sig> sig;
    std::function<Py(Vec&)> fn;         // called with the parameters bound, in order
};
struct MeshObj : Obj {                  // add.Mesh: lists V, F, C (and UV), as in add.py
    Py V, F, C, UV;
};
struct InstObj : Obj {                  // an object of a class of the castle's own (Spots)
    std::string cls;
    DictObj attrs;
};
struct StreamObj : Obj {
    std::unique_ptr<add::Stream> s;
};

inline Py::Py(const char* s) : k(STR), i(0), o(std::make_shared<StrObj>(s)) {}
inline Py::Py(const std::string& s) : k(STR), i(0), o(std::make_shared<StrObj>(s)) {}

inline ListObj* L_(const Py& x) { return static_cast<ListObj*>(x.o.get()); }
inline DictObj* D_(const Py& x) { return static_cast<DictObj*>(x.o.get()); }
inline SetObj* S_(const Py& x) { return static_cast<SetObj*>(x.o.get()); }
inline FuncObj* F_(const Py& x) { return static_cast<FuncObj*>(x.o.get()); }
inline MeshObj* M_(const Py& x) { return static_cast<MeshObj*>(x.o.get()); }
inline InstObj* I_(const Py& x) { return static_cast<InstObj*>(x.o.get()); }

std::string type_name(const Py& x);
std::string repr(const Py& x);
std::string str(const Py& x);

inline Vec& Py::vec() const {
    if (k != LIST && k != TUPLE) raise("TypeError", "'" + type_name(*this) + "' object is not a list");
    return L_(*this)->v;
}
inline const std::string& Py::str() const {
    if (k != STR) raise("TypeError", "not a str: " + type_name(*this));
    return static_cast<StrObj*>(o.get())->s;
}
inline double Py::num() const {
    if (k == FLOAT) return f;
    if (k == INT || k == BOOL) return (double)i;
    raise("TypeError", "must be real number, not " + type_name(*this));
}
inline int64_t Py::to_i() const {
    if (k == INT || k == BOOL) return i;
    raise("TypeError", "'" + type_name(*this) + "' object cannot be interpreted as an integer");
}

// ---------------------------------------------------------------------------
//  making values
// ---------------------------------------------------------------------------
inline Py list(Vec v = {}) { return Py(LIST, std::make_shared<ListObj>(std::move(v))); }
inline Py list(std::initializer_list<Py> v) { return Py(LIST, std::make_shared<ListObj>(Vec(v))); }
inline Py tuple(Vec v = {}) { return Py(TUPLE, std::make_shared<ListObj>(std::move(v))); }
inline Py tuple(std::initializer_list<Py> v) { return Py(TUPLE, std::make_shared<ListObj>(Vec(v))); }
inline Py dict() { return Py(DICT, std::make_shared<DictObj>()); }
inline Py dict(std::initializer_list<std::pair<Py, Py>> kv) {
    Py d = dict();
    for (auto& p : kv) D_(d)->set(p.first, p.second);
    return d;
}
inline Py set_() { return Py(SET, std::make_shared<SetObj>()); }
inline Py set_(std::initializer_list<Py> v) {
    Py s = set_();
    for (auto& x : v) S_(s)->d.set(x, None);
    return s;
}
inline Py str_(const std::string& s) { return Py(s); }

// ---------------------------------------------------------------------------
//  what kind of thing it is
// ---------------------------------------------------------------------------
inline std::string type_name(const Py& x) {
    switch (x.k) {
        case NONE: return "NoneType";
        case BOOL: return "bool";
        case INT: return "int";
        case FLOAT: return "float";
        case STR: return "str";
        case LIST: return "list";
        case TUPLE: return "tuple";
        case DICT: return "dict";
        case SET: return "set";
        case FUNC: return "function";
        case MESH: return "Mesh";
        case INST: return I_(x)->cls;
        case STREAM: return "Stream";
        case MISSING: return "<missing>";
    }
    return "?";
}

inline bool truthy(const Py& x) {
    switch (x.k) {
        case NONE: return false;
        case BOOL:
        case INT: return x.i != 0;
        case FLOAT: return x.f != 0.0;
        case STR: return !x.str().empty();
        case LIST:
        case TUPLE: return !L_(x)->v.empty();
        case DICT: return D_(x)->live != 0;
        case SET: return S_(x)->d.live != 0;
        default: return true;               // functions, meshes (len 2), objects
    }
}

// ---------------------------------------------------------------------------
//  equality and hashing (1 == 1.0 == True, as Python)
// ---------------------------------------------------------------------------
inline bool num_eq(const Py& a, const Py& b) {
    if (a.k == FLOAT || b.k == FLOAT) return a.num() == b.num();
    return a.i == b.i;
}
inline bool eq(const Py& a, const Py& b) {
    if (a.is_num() && b.is_num()) return num_eq(a, b);
    if (a.k != b.k) return false;
    switch (a.k) {
        case NONE: return true;
        case STR: return a.str() == b.str();
        case LIST:
        case TUPLE: {
            const Vec &x = L_(a)->v, &y = L_(b)->v;
            if (x.size() != y.size()) return false;
            for (size_t j = 0; j < x.size(); ++j)
                if (!eq(x[j], y[j])) return false;
            return true;
        }
        case DICT: {
            DictObj *x = D_(a), *y = D_(b);
            if (x->live != y->live) return false;
            bool same = true;
            x->each([&](const Py& k, const Py& v) {
                Py* w = y->find(k);
                if (!w || !eq(v, *w)) same = false;
            });
            return same;
        }
        case SET: {
            if (S_(a)->d.live != S_(b)->d.live) return false;
            bool same = true;
            S_(a)->d.each([&](const Py& k, const Py&) {
                if (!S_(b)->d.find(k)) same = false;
            });
            return same;
        }
        default: return a.o == b.o;
    }
}
inline size_t mix(size_t h, size_t v) { return h ^ (v + 0x9e3779b97f4a7c15ULL + (h << 6) + (h >> 2)); }
inline size_t hash_of(const Py& x) {
    switch (x.k) {
        case NONE: return 0x51ed270b;
        case BOOL:
        case INT: return std::hash<int64_t>()(x.i);
        case FLOAT: {
            double t = std::trunc(x.f);
            if (t == x.f && std::fabs(t) < 9.2e18) return std::hash<int64_t>()((int64_t)t);
            return std::hash<double>()(x.f);
        }
        case STR: return std::hash<std::string>()(x.str());
        case TUPLE: {
            size_t h = 0x345678;
            for (const Py& e : L_(x)->v) h = mix(h, hash_of(e));
            return h;
        }
        case LIST:
        case DICT:
        case SET: raise("TypeError", "unhashable type: '" + type_name(x) + "'");
        default: return std::hash<const void*>()(x.o.get());
    }
}
inline bool operator==(const Py& a, const Py& b) { return eq(a, b); }
inline bool operator!=(const Py& a, const Py& b) { return !eq(a, b); }
inline bool is(const Py& a, const Py& b) {
    if (a.k != b.k) return false;
    if (a.k == NONE || a.k == MISSING) return true;
    if (a.k == BOOL || a.k == INT) return a.i == b.i;
    if (a.k == FLOAT) return a.f == b.f;
    return a.o == b.o;
}

// ---------------------------------------------------------------------------
//  order (numbers, strings, lists and tuples item by item)
// ---------------------------------------------------------------------------
inline bool lt(const Py& a, const Py& b) {
    if (a.is_num() && b.is_num()) {
        if (a.k == FLOAT || b.k == FLOAT) return a.num() < b.num();
        return a.i < b.i;
    }
    if (a.k == STR && b.k == STR) return a.str() < b.str();
    if ((a.k == LIST && b.k == LIST) || (a.k == TUPLE && b.k == TUPLE)) {
        const Vec &x = L_(a)->v, &y = L_(b)->v;
        size_t n = std::min(x.size(), y.size());
        for (size_t j = 0; j < n; ++j)
            if (!eq(x[j], y[j])) return lt(x[j], y[j]);
        return x.size() < y.size();
    }
    raise("TypeError", "'<' not supported between instances of '" + type_name(a) + "' and '" + type_name(b) + "'");
}
inline bool operator<(const Py& a, const Py& b) { return lt(a, b); }
inline bool operator>(const Py& a, const Py& b) { return lt(b, a); }
inline bool operator<=(const Py& a, const Py& b) {
    if (a.is_num() && b.is_num()) {
        if (a.k == FLOAT || b.k == FLOAT) return a.num() <= b.num();
        return a.i <= b.i;
    }
    return lt(a, b) || eq(a, b);
}
inline bool operator>=(const Py& a, const Py& b) { return b <= a; }

// ---------------------------------------------------------------------------
//  arithmetic, with Python's rules
// ---------------------------------------------------------------------------
[[noreturn]] inline void bad_operands(const char* op, const Py& a, const Py& b) {
    raise("TypeError", std::string("unsupported operand type(s) for ") + op + ": '" + type_name(a) + "' and '" +
                           type_name(b) + "'");
}
inline Py repeat(const Py& seq, int64_t n) {
    const Vec& v = L_(seq)->v;
    Vec out;
    if (n > 0) {
        out.reserve(v.size() * (size_t)n);
        for (int64_t j = 0; j < n; ++j) out.insert(out.end(), v.begin(), v.end());
    }
    return seq.k == LIST ? list(std::move(out)) : tuple(std::move(out));
}
inline Py operator+(const Py& a, const Py& b) {
    if (a.k == FLOAT && b.k == FLOAT) return Py(a.f + b.f);
    if (a.is_num() && b.is_num()) {
        if (a.k == FLOAT || b.k == FLOAT) return Py(a.num() + b.num());
        int64_t r;
        if (__builtin_add_overflow(a.i, b.i, &r)) raise("OverflowError", "int too big");
        return Py(r);
    }
    if (a.k == STR && b.k == STR) return Py(a.str() + b.str());
    if ((a.k == LIST && b.k == LIST) || (a.k == TUPLE && b.k == TUPLE)) {
        Vec v = L_(a)->v;
        const Vec& w = L_(b)->v;
        v.insert(v.end(), w.begin(), w.end());
        return a.k == LIST ? list(std::move(v)) : tuple(std::move(v));
    }
    bad_operands("+", a, b);
}
inline Py operator-(const Py& a, const Py& b) {
    if (a.k == FLOAT && b.k == FLOAT) return Py(a.f - b.f);
    if (a.is_num() && b.is_num()) {
        if (a.k == FLOAT || b.k == FLOAT) return Py(a.num() - b.num());
        int64_t r;
        if (__builtin_sub_overflow(a.i, b.i, &r)) raise("OverflowError", "int too big");
        return Py(r);
    }
    if (a.k == SET && b.k == SET) {
        Py s = set_();
        S_(a)->d.each([&](const Py& k, const Py&) {
            if (!S_(b)->d.find(k)) S_(s)->d.set(k, None);
        });
        return s;
    }
    bad_operands("-", a, b);
}
inline Py operator*(const Py& a, const Py& b) {
    if (a.k == FLOAT && b.k == FLOAT) return Py(a.f * b.f);
    if (a.is_num() && b.is_num()) {
        if (a.k == FLOAT || b.k == FLOAT) return Py(a.num() * b.num());
        int64_t r;
        if (__builtin_mul_overflow(a.i, b.i, &r)) raise("OverflowError", "int too big");
        return Py(r);
    }
    if ((a.k == LIST || a.k == TUPLE) && b.is_int()) return repeat(a, b.i);
    if ((b.k == LIST || b.k == TUPLE) && a.is_int()) return repeat(b, a.i);
    if (a.k == STR && b.is_int()) {
        std::string s;
        for (int64_t j = 0; j < b.i; ++j) s += a.str();
        return Py(s);
    }
    bad_operands("*", a, b);
}
inline Py operator/(const Py& a, const Py& b) {
    if (!a.is_num() || !b.is_num()) bad_operands("/", a, b);
    if (a.is_int() && b.is_int()) {               // int / int: true division, correctly rounded
        if (b.i == 0) raise("ZeroDivisionError", "division by zero");
        const int64_t big = (int64_t)1 << 53;
        if (a.i > -big && a.i < big && b.i > -big && b.i < big) return Py((double)a.i / (double)b.i);
        return Py((double)((long double)a.i / (long double)b.i));
    }
    double y = b.num();
    if (y == 0.0) raise("ZeroDivisionError", "float division by zero");
    return Py(a.num() / y);
}
inline void float_divmod(double vx, double wx, double& floordiv, double& mod) {   // CPython's float_divmod
    if (wx == 0.0) raise("ZeroDivisionError", "float divmod()");
    mod = std::fmod(vx, wx);
    double div = (vx - mod) / wx;
    if (mod) {
        if ((wx < 0) != (mod < 0)) {
            mod += wx;
            div -= 1.0;
        }
    } else {
        mod = std::copysign(0.0, wx);
    }
    if (div) {
        floordiv = std::floor(div);
        if (div - floordiv > 0.5) floordiv += 1.0;
    } else {
        floordiv = std::copysign(0.0, vx / wx);
    }
}
inline Py floordiv(const Py& a, const Py& b) {
    if (!a.is_num() || !b.is_num()) bad_operands("//", a, b);
    if (a.is_int() && b.is_int()) {
        if (b.i == 0) raise("ZeroDivisionError", "integer division or modulo by zero");
        int64_t q = a.i / b.i, r = a.i % b.i;
        if (r != 0 && ((r < 0) != (b.i < 0))) --q;
        return Py(q);
    }
    double q, m;
    float_divmod(a.num(), b.num(), q, m);
    return Py(q);
}
inline Py mod(const Py& a, const Py& b);
inline Py operator%(const Py& a, const Py& b) { return mod(a, b); }
inline Py pow_(const Py& a, const Py& b) {
    if (!a.is_num() || !b.is_num()) bad_operands("** or pow()", a, b);
    if (a.is_int() && b.is_int() && b.i >= 0) {
        int64_t r = 1, base = a.i, e = b.i;
        while (e > 0) {
            if (e & 1)
                if (__builtin_mul_overflow(r, base, &r)) raise("OverflowError", "int too big");
            e >>= 1;
            if (e > 0 && __builtin_mul_overflow(base, base, &base)) raise("OverflowError", "int too big");
        }
        return Py(r);
    }
    return Py(add::detail::py_pow(a.num(), b.num()));
}
inline Py operator-(const Py& a) {
    if (a.k == FLOAT) return Py(-a.f);
    if (a.is_int()) return Py(-a.i);
    raise("TypeError", "bad operand type for unary -: '" + type_name(a) + "'");
}
inline Py operator+(const Py& a) {
    if (a.k == BOOL) return Py(a.i);
    if (a.is_num()) return a;
    raise("TypeError", "bad operand type for unary +: '" + type_name(a) + "'");
}
inline Py operator!(const Py& a) { return Py(!truthy(a)); }
inline Py operator&(const Py& a, const Py& b) {
    if (a.is_int() && b.is_int()) {
        if (a.k == BOOL && b.k == BOOL) return Py((a.i & b.i) != 0);
        return Py(a.i & b.i);
    }
    if (a.k == SET && b.k == SET) {
        Py s = set_();
        S_(a)->d.each([&](const Py& k, const Py&) {
            if (S_(b)->d.find(k)) S_(s)->d.set(k, None);
        });
        return s;
    }
    bad_operands("&", a, b);
}
inline Py operator|(const Py& a, const Py& b) {
    if (a.is_int() && b.is_int()) {
        if (a.k == BOOL && b.k == BOOL) return Py((a.i | b.i) != 0);
        return Py(a.i | b.i);
    }
    if (a.k == SET && b.k == SET) {
        Py s = set_();
        S_(a)->d.each([&](const Py& k, const Py&) { S_(s)->d.set(k, None); });
        S_(b)->d.each([&](const Py& k, const Py&) { S_(s)->d.set(k, None); });
        return s;
    }
    bad_operands("|", a, b);
}
inline Py operator^(const Py& a, const Py& b) {
    if (a.is_int() && b.is_int()) {
        if (a.k == BOOL && b.k == BOOL) return Py((a.i ^ b.i) != 0);
        return Py(a.i ^ b.i);
    }
    bad_operands("^", a, b);
}
inline Py operator>>(const Py& a, const Py& b) {
    if (a.is_int() && b.is_int()) return Py(b.i >= 64 ? (a.i < 0 ? -1 : 0) : (a.i >> b.i));
    bad_operands(">>", a, b);
}
inline Py operator<<(const Py& a, const Py& b) {
    if (a.is_int() && b.is_int()) {
        if (b.i >= 63 || (a.i != 0 && (std::abs(a.i) >> (63 - b.i)) != 0)) raise("OverflowError", "int too big");
        return Py(a.i << b.i);
    }
    bad_operands("<<", a, b);
}
inline Py operator~(const Py& a) {
    if (a.is_int()) return Py(~a.i);
    raise("TypeError", "bad operand type for unary ~");
}

// in-place forms: a list += extends itself (everyone who holds it sees it)
inline Py& iadd(Py& a, const Py& b) {
    if (a.k == LIST) {
        if (b.k == LIST || b.k == TUPLE) {
            Vec w = L_(b)->v;
            L_(a)->v.insert(L_(a)->v.end(), w.begin(), w.end());
            return a;
        }
        bad_operands("+=", a, b);
    }
    a = a + b;
    return a;
}

// ---------------------------------------------------------------------------
//  items: x[i], x[i] = v, slices
// ---------------------------------------------------------------------------
inline size_t norm_index(int64_t i, size_t n, const char* what) {
    if (i < 0) i += (int64_t)n;
    if (i < 0 || i >= (int64_t)n) raise("IndexError", std::string(what) + " index out of range");
    return (size_t)i;
}
inline Py getitem(const Py& x, const Py& key) {
    switch (x.k) {
        case LIST:
        case TUPLE: {
            const Vec& v = L_(x)->v;
            return v[norm_index(key.to_i(), v.size(), x.k == LIST ? "list" : "tuple")];
        }
        case DICT: {
            Py* p = D_(x)->find(key);
            if (!p) raise("KeyError", repr(key));
            return *p;
        }
        case STR: {
            const std::string& s = x.str();
            return Py(std::string(1, s[norm_index(key.to_i(), s.size(), "string")]));
        }
        default: raise("TypeError", "'" + type_name(x) + "' object is not subscriptable");
    }
}
inline Py Py::operator[](const Py& key) const { return getitem(*this, key); }
inline void setitem(const Py& x, const Py& key, const Py& v) {
    switch (x.k) {
        case LIST: {
            Vec& w = L_(x)->v;
            w[norm_index(key.to_i(), w.size(), "list assignment")] = v;
            return;
        }
        case DICT: D_(x)->set(key, v); return;
        default: raise("TypeError", "'" + type_name(x) + "' object does not support item assignment");
    }
}
inline void slice_indices(int64_t n, const Py& a, const Py& b, const Py& c, int64_t& start, int64_t& stop, int64_t& step) {
    step = c.is_none() || c.missing() ? 1 : c.to_i();
    if (step == 0) raise("ValueError", "slice step cannot be zero");
    if (step > 0) {
        start = a.is_none() || a.missing() ? 0 : a.to_i();
        stop = b.is_none() || b.missing() ? n : b.to_i();
        if (start < 0) start = std::max<int64_t>(0, start + n);
        if (start > n) start = n;
        if (stop < 0) stop = std::max<int64_t>(0, stop + n);
        if (stop > n) stop = n;
    } else {
        start = a.is_none() || a.missing() ? n - 1 : a.to_i();
        stop = b.is_none() || b.missing() ? -1 : b.to_i();
        if (start < 0) start = std::max<int64_t>(-1, start + n);
        if (start >= n) start = n - 1;
        if (!(b.is_none() || b.missing())) {
            if (stop < 0) stop = std::max<int64_t>(-1, stop + n);
            if (stop >= n) stop = n - 1;
        }
    }
}
inline Py slice(const Py& x, const Py& a, const Py& b, const Py& c = None) {
    if (x.k == STR) {
        const std::string& s = x.str();
        int64_t st, sp, se;
        slice_indices((int64_t)s.size(), a, b, c, st, sp, se);
        std::string out;
        for (int64_t j = st; se > 0 ? j < sp : j > sp; j += se) out += s[(size_t)j];
        return Py(out);
    }
    const Vec& v = x.vec();
    int64_t st, sp, se;
    slice_indices((int64_t)v.size(), a, b, c, st, sp, se);
    Vec out;
    for (int64_t j = st; se > 0 ? j < sp : j > sp; j += se) out.push_back(v[(size_t)j]);
    return x.k == LIST ? list(std::move(out)) : tuple(std::move(out));
}

// ---------------------------------------------------------------------------
//  iterating: a list is walked live (what is appended while walking is
//  walked too); everything else is taken as it is when the walk begins
// ---------------------------------------------------------------------------
Vec items_of(const Py& x);
struct Iter {
    Py src;
    Vec snap;
    size_t j = 0;
    bool live = false;
    explicit Iter(const Py& x) {
        if (x.k == LIST) {
            src = x;
            live = true;
        } else if (x.k == TUPLE) {
            src = x;
            live = true;                          // (a tuple never changes)
        } else {
            snap = items_of(x);
        }
    }
    bool next(Py& out) {
        if (live) {
            const Vec& v = L_(src)->v;
            if (j >= v.size()) return false;
            out = v[j++];
            return true;
        }
        if (j >= snap.size()) return false;
        out = snap[j++];
        return true;
    }
};
inline Vec items_of(const Py& x) {
    switch (x.k) {
        case LIST:
        case TUPLE: return L_(x)->v;
        case STR: {
            Vec out;
            for (char ch : x.str()) out.push_back(Py(std::string(1, ch)));
            return out;
        }
        case DICT: {
            Vec out;
            out.reserve(D_(x)->live);
            D_(x)->each([&](const Py& k, const Py&) { out.push_back(k); });
            return out;
        }
        case SET: {
            Vec out;
            S_(x)->d.each([&](const Py& k, const Py&) { out.push_back(k); });
            return out;
        }
        default: raise("TypeError", "'" + type_name(x) + "' object is not iterable");
    }
}
// for (Py x : each(seq)) -- a range-for over Iter
struct EachEnd {};
struct EachIt {
    Iter* it;
    Py cur;
    bool done;
    bool operator!=(const EachEnd&) const { return !done; }
    void operator++() { done = !it->next(cur); }
    const Py& operator*() const { return cur; }
};
struct Each {
    Iter it;
    explicit Each(const Py& x) : it(x) {}
    EachIt begin() {
        EachIt e{&it, Py(), false};
        e.done = !it.next(e.cur);
        return e;
    }
    EachEnd end() { return {}; }
};
inline Each each(const Py& x) { return Each(x); }

// range(): for (Py i : range(a, b, s))
struct RangeIt {
    int64_t i, stop, step;
    bool operator!=(const RangeIt&) const { return step > 0 ? i < stop : i > stop; }
    void operator++() { i += step; }
    Py operator*() const { return Py(i); }
};
struct Range {
    int64_t a, b, s;
    RangeIt begin() const { return {a, b, s}; }
    RangeIt end() const { return {b, b, s}; }
    Py list() const {
        Vec v;
        if (s > 0)
            for (int64_t j = a; j < b; j += s) v.push_back(Py(j));
        else
            for (int64_t j = a; j > b; j += s) v.push_back(Py(j));
        return py::list(std::move(v));
    }
    operator Py() const { return list(); }      // (a range used as a value: its numbers, as a list)
};
inline Range range(const Py& b) { return {0, b.to_i(), 1}; }
inline Range range(const Py& a, const Py& b) { return {a.to_i(), b.to_i(), 1}; }
inline Range range(const Py& a, const Py& b, const Py& s) {
    if (s.to_i() == 0) raise("ValueError", "range() arg 3 must not be zero");
    return {a.to_i(), b.to_i(), s.to_i()};
}

// unpacking: a, b = x
inline Vec unpack(const Py& x, size_t n) {
    Vec v = (x.k == LIST || x.k == TUPLE) ? L_(x)->v : items_of(x);
    if (v.size() != n)
        raise("ValueError", v.size() > n ? "too many values to unpack (expected " + std::to_string(n) + ")"
                                          : "not enough values to unpack (expected " + std::to_string(n) + ", got " +
                                                std::to_string(v.size()) + ")");
    return v;
}
// a, *b, c = x
inline Vec unpack_star(const Py& x, size_t before, size_t after) {
    Vec v = (x.k == LIST || x.k == TUPLE) ? L_(x)->v : items_of(x);
    if (v.size() < before + after) raise("ValueError", "not enough values to unpack");
    Vec out(v.begin(), v.begin() + before);
    out.push_back(list(Vec(v.begin() + before, v.end() - after)));
    out.insert(out.end(), v.end() - after, v.end());
    return out;
}

// ---------------------------------------------------------------------------
//  functions: called with positional and keyword arguments, bound by name
// ---------------------------------------------------------------------------
struct Args {
    Vec pos;
    std::vector<std::pair<std::string, Py>> kw;
    Args() {}
    Args(Vec p) : pos(std::move(p)) {}
    Args(Vec p, std::vector<std::pair<std::string, Py>> k) : pos(std::move(p)), kw(std::move(k)) {}
};
inline Vec bind(const Sig& s, Args& a) {
    size_t n = s.names.size();
    Vec out(n, MISSING_);
    size_t np = a.pos.size();
    size_t fixed = n - (s.varargs ? 1 : 0) - (s.kwargs ? 1 : 0);
    if (np > fixed && !s.varargs)
        raise("TypeError", s.name + "() takes " + std::to_string(fixed) + " positional arguments but " +
                               std::to_string(np) + " were given");
    for (size_t j = 0; j < std::min(np, fixed); ++j) out[j] = std::move(a.pos[j]);
    if (s.varargs) out[fixed] = tuple(np > fixed ? Vec(a.pos.begin() + fixed, a.pos.end()) : Vec());
    Py extra;
    if (s.kwargs) extra = dict();
    for (auto& kv : a.kw) {
        size_t j = 0;
        while (j < fixed && s.names[j] != kv.first) ++j;
        if (j < fixed) {
            if (!out[j].missing()) raise("TypeError", s.name + "() got multiple values for argument '" + kv.first + "'");
            out[j] = std::move(kv.second);
        } else if (s.kwargs) {
            D_(extra)->set(Py(kv.first), kv.second);
        } else {
            raise("TypeError", s.name + "() got an unexpected keyword argument '" + kv.first + "'");
        }
    }
    if (s.kwargs) out[n - 1] = extra;
    for (size_t j = 0; j < fixed; ++j)
        if (out[j].missing()) {
            if (j < s.defaults.size() && !s.defaults[j].missing())
                out[j] = s.defaults[j];
            else if (j < s.nreq)
                raise("TypeError", s.name + "() missing required argument: '" + s.names[j] + "'");
        }
    return out;
}
inline Py func(std::shared_ptr<Sig> sig, std::function<Py(Vec&)> fn) {
    auto f = std::make_shared<FuncObj>();
    f->sig = std::move(sig);
    f->fn = std::move(fn);
    return Py(FUNC, f);
}
inline std::shared_ptr<Sig> sig(std::string name, std::vector<std::string> names, Vec defaults = {}, size_t nreq = 0,
                                bool varargs = false, bool kwargs = false) {
    auto s = std::make_shared<Sig>();
    s->name = std::move(name);
    s->names = std::move(names);
    s->defaults = std::move(defaults);
    s->defaults.resize(s->names.size(), MISSING_);
    s->nreq = nreq;
    s->varargs = varargs;
    s->kwargs = kwargs;
    return s;
}
inline Py call(const Py& f, Args a) {
    if (f.k != FUNC) raise("TypeError", "'" + type_name(f) + "' object is not callable");
    FuncObj* fo = F_(f);
    Vec p = bind(*fo->sig, a);
    return fo->fn(p);
}
inline Py call(const Py& f, std::initializer_list<Py> pos) { return call(f, Args(Vec(pos))); }
// f(*a, x, **k) -- the arguments gathered as Python gathers them
inline void star_into(Vec& pos, const Py& seq) {
    Vec v = items_of(seq);
    pos.insert(pos.end(), v.begin(), v.end());
}
inline void starstar_into(std::vector<std::pair<std::string, Py>>& kw, const Py& d) {
    D_(d)->each([&](const Py& k, const Py& v) { kw.emplace_back(k.str(), v); });
}
inline bool callable(const Py& x) { return x.k == FUNC; }

// ---------------------------------------------------------------------------
//  builtins
// ---------------------------------------------------------------------------
inline Py len(const Py& x) {
    switch (x.k) {
        case STR: return Py((int64_t)add::detail::utf8_len(x.str()));
        case LIST:
        case TUPLE: return Py((int64_t)L_(x)->v.size());
        case DICT: return Py((int64_t)D_(x)->live);
        case SET: return Py((int64_t)S_(x)->d.live);
        case MESH: return Py(2);
        default: raise("TypeError", "object of type '" + type_name(x) + "' has no len()");
    }
}
inline Py abs_(const Py& x) {
    if (x.k == FLOAT) return Py(std::fabs(x.f));
    if (x.is_int()) return Py(x.i < 0 ? -x.i : x.i);
    raise("TypeError", "bad operand type for abs()");
}
inline Py int_(const Py& x) {
    switch (x.k) {
        case BOOL:
        case INT: return Py(x.i);
        case FLOAT: {
            if (std::isnan(x.f)) raise("ValueError", "cannot convert float NaN to integer");
            if (std::isinf(x.f)) raise("OverflowError", "cannot convert float infinity to integer");
            double t = std::trunc(x.f);
            if (std::fabs(t) >= 9.2e18) raise("OverflowError", "int too big");
            return Py((int64_t)t);
        }
        case STR: return Py((int64_t)std::stoll(add::detail::strip(x.str())));
        default: raise("TypeError", "int() argument must be a string or a number, not '" + type_name(x) + "'");
    }
}
inline Py int_(const Py& x, const Py& base) { return Py((int64_t)std::stoll(add::detail::strip(x.str()), nullptr, (int)base.to_i())); }
inline Py float_(const Py& x) {
    if (x.k == FLOAT) return x;
    if (x.is_int()) return Py((double)x.i);
    if (x.k == STR) return Py(std::strtod(x.str().c_str(), nullptr));
    raise("TypeError", "float() argument must be a string or a number, not '" + type_name(x) + "'");
}
inline Py round_(const Py& x) {
    if (x.is_int()) return Py(x.i);
    double r = std::nearbyint(x.num());          // (round half to even: the default rounding mode)
    if (std::isnan(r)) raise("ValueError", "cannot convert float NaN to integer");
    return Py((int64_t)r);
}
inline Py round_(const Py& x, const Py& n) {
    if (x.is_int()) {
        if (n.to_i() >= 0) return Py(x.i);
        double p = std::pow(10.0, (double)-n.to_i());
        return Py((int64_t)(std::nearbyint((double)x.i / p) * p));
    }
    return Py(add::detail::py_round(x.num(), (int)n.to_i()));
}
inline Py sorted(const Py& seq, const Py& key = None, const Py& reverse = Py(false));
inline Py min_(const Vec& v, const Py& key = None, const Py& dflt = MISSING_) {
    if (v.empty()) {
        if (!dflt.missing()) return dflt;
        raise("ValueError", "min() arg is an empty sequence");
    }
    size_t best = 0;
    Py bk = key.is_none() ? v[0] : call(key, {v[0]});
    for (size_t j = 1; j < v.size(); ++j) {
        Py k = key.is_none() ? v[j] : call(key, {v[j]});
        if (lt(k, bk)) {
            best = j;
            bk = k;
        }
    }
    return v[best];
}
inline Py max_(const Vec& v, const Py& key = None, const Py& dflt = MISSING_) {
    if (v.empty()) {
        if (!dflt.missing()) return dflt;
        raise("ValueError", "max() arg is an empty sequence");
    }
    size_t best = 0;
    Py bk = key.is_none() ? v[0] : call(key, {v[0]});
    for (size_t j = 1; j < v.size(); ++j) {
        Py k = key.is_none() ? v[j] : call(key, {v[j]});
        if (lt(bk, k)) {
            best = j;
            bk = k;
        }
    }
    return v[best];
}
// min(a, b) of two numbers, the common case: no list built
inline Py min2(const Py& a, const Py& b) { return lt(b, a) ? b : a; }
inline Py max2(const Py& a, const Py& b) { return lt(a, b) ? b : a; }
inline Py sum_(const Vec& v, const Py& start = Py(0)) {
    Py acc = start;
    for (const Py& x : v) acc = acc + x;
    return acc;
}
inline Py any_(const Vec& v) {
    for (const Py& x : v)
        if (truthy(x)) return True;
    return False;
}
inline Py all_(const Vec& v) {
    for (const Py& x : v)
        if (!truthy(x)) return False;
    return True;
}
inline Py list_(const Py& x) { return list(items_of(x)); }
inline Py tuple_(const Py& x) { return x.k == TUPLE ? x : tuple(items_of(x)); }
inline Py set_of(const Py& x) {
    Py s = set_();
    for (const Py& e : items_of(x)) S_(s)->d.set(e, None);
    return s;
}
inline Py dict_of_pairs(const Py& x) {
    Py d = dict();
    for (const Py& e : items_of(x)) {
        Vec kv = unpack(e, 2);
        D_(d)->set(kv[0], kv[1]);
    }
    return d;
}
inline Py dict_copy(const Py& x) {
    Py d = dict();
    D_(x)->each([&](const Py& k, const Py& v) { D_(d)->set(k, v); });
    return d;
}
inline Py zip_(std::initializer_list<Py> seqs) {
    std::vector<Vec> vs;
    size_t n = SIZE_MAX;
    for (const Py& s : seqs) {
        vs.push_back(items_of(s));
        n = std::min(n, vs.back().size());
    }
    if (vs.empty()) n = 0;
    Vec out;
    out.reserve(n);
    for (size_t j = 0; j < n; ++j) {
        Vec t;
        t.reserve(vs.size());
        for (auto& v : vs) t.push_back(v[j]);
        out.push_back(tuple(std::move(t)));
    }
    return list(std::move(out));
}
inline Py enumerate_(const Py& seq, const Py& start = Py(0)) {
    Vec v = items_of(seq), out;
    out.reserve(v.size());
    int64_t j = start.to_i();
    for (auto& x : v) out.push_back(tuple({Py(j++), x}));
    return list(std::move(out));
}
inline Py reversed_(const Py& seq) {
    Vec v = items_of(seq);
    std::reverse(v.begin(), v.end());
    return list(std::move(v));
}
inline Py sorted(const Py& seq, const Py& key, const Py& reverse) {
    Vec v = items_of(seq);
    bool rev = truthy(reverse);
    if (key.is_none()) {
        if (rev)
            std::stable_sort(v.begin(), v.end(), [](const Py& a, const Py& b) { return lt(b, a); });
        else
            std::stable_sort(v.begin(), v.end(), [](const Py& a, const Py& b) { return lt(a, b); });
        return list(std::move(v));
    }
    std::vector<std::pair<Py, size_t>> ks;
    ks.reserve(v.size());
    for (size_t j = 0; j < v.size(); ++j) ks.emplace_back(call(key, {v[j]}), j);
    if (rev)
        std::stable_sort(ks.begin(), ks.end(), [](const auto& a, const auto& b) { return lt(b.first, a.first); });
    else
        std::stable_sort(ks.begin(), ks.end(), [](const auto& a, const auto& b) { return lt(a.first, b.first); });
    Vec out;
    out.reserve(v.size());
    for (auto& p : ks) out.push_back(v[p.second]);
    return list(std::move(out));
}
inline bool contains(const Py& seq, const Py& x) {          // x in seq
    switch (seq.k) {
        case LIST:
        case TUPLE:
            for (const Py& e : L_(seq)->v)
                if (eq(e, x)) return true;
            return false;
        case DICT: return D_(seq)->find(x) != nullptr;
        case SET: return S_(seq)->d.find(x) != nullptr;
        case STR: return seq.str().find(x.str()) != std::string::npos;
        default: raise("TypeError", "argument of type '" + type_name(seq) + "' is not iterable");
    }
}
inline bool isinstance_(const Py& x, Kind k) {
    if (k == INT) return x.k == INT || x.k == BOOL;
    return x.k == k;
}

// ---------------------------------------------------------------------------
//  text: str(), repr(), "%" formatting, print()
// ---------------------------------------------------------------------------
inline std::string repr_str(const std::string& s) {
    bool dq = s.find('\'') != std::string::npos && s.find('"') == std::string::npos;
    std::string out(1, dq ? '"' : '\'');
    for (char ch : s) {
        if (ch == '\\') out += "\\\\";
        else if (ch == '\n') out += "\\n";
        else if (ch == '\t') out += "\\t";
        else if (ch == '\'' && !dq) out += "\\'";
        else out += ch;
    }
    out += dq ? '"' : '\'';
    return out;
}
inline std::string repr(const Py& x) {
    switch (x.k) {
        case NONE: return "None";
        case BOOL: return x.i ? "True" : "False";
        case INT: return std::to_string(x.i);
        case FLOAT: return add::detail::py_repr(x.f);
        case STR: return repr_str(x.str());
        case LIST:
        case TUPLE: {
            std::string s = x.k == LIST ? "[" : "(";
            const Vec& v = L_(x)->v;
            for (size_t j = 0; j < v.size(); ++j) s += (j ? ", " : "") + repr(v[j]);
            if (x.k == TUPLE && v.size() == 1) s += ",";
            return s + (x.k == LIST ? "]" : ")");
        }
        case DICT: {
            std::string s = "{";
            bool first = true;
            D_(x)->each([&](const Py& k, const Py& v) {
                s += (first ? "" : ", ") + repr(k) + ": " + repr(v);
                first = false;
            });
            return s + "}";
        }
        case SET: {
            if (!S_(x)->d.live) return "set()";
            std::string s = "{";
            bool first = true;
            S_(x)->d.each([&](const Py& k, const Py&) {
                s += (first ? "" : ", ") + repr(k);
                first = false;
            });
            return s + "}";
        }
        case FUNC: return "<function " + F_(x)->sig->name + ">";
        case MESH: return "<Mesh>";
        default: return "<" + type_name(x) + " object>";
    }
}
inline std::string str(const Py& x) { return x.k == STR ? x.str() : repr(x); }
inline Py str_of(const Py& x) { return Py(str(x)); }
inline Py format(const Py& fmt, const Py& args) {           // fmt % args
    const std::string& f = fmt.str();
    Vec a = args.k == TUPLE ? L_(args)->v : Vec{args};
    size_t ai = 0;
    std::string out;
    for (size_t j = 0; j < f.size(); ++j) {
        if (f[j] != '%') {
            out += f[j];
            continue;
        }
        ++j;
        if (j < f.size() && f[j] == '%') {
            out += '%';
            continue;
        }
        std::string spec = "%";
        while (j < f.size() && std::strchr("-+ #0", f[j])) spec += f[j++];
        while (j < f.size() && std::isdigit((unsigned char)f[j])) spec += f[j++];
        if (j < f.size() && f[j] == '.') {
            spec += f[j++];
            while (j < f.size() && std::isdigit((unsigned char)f[j])) spec += f[j++];
        }
        char conv = f[j];
        if (ai >= a.size()) raise("TypeError", "not enough arguments for format string");
        const Py& v = a[ai++];
        char buf[512];
        if (conv == 's' || conv == 'r') {
            std::string s = conv == 's' ? str(v) : repr(v);
            std::snprintf(buf, sizeof buf, (spec + "s").c_str(), s.c_str());
        } else if (conv == 'd' || conv == 'i') {
            long long n = v.k == FLOAT ? (long long)std::trunc(v.f) : (long long)v.to_i();
            std::snprintf(buf, sizeof buf, (spec + "lld").c_str(), n);
        } else if (conv == 'x' || conv == 'X') {
            std::snprintf(buf, sizeof buf, (spec + "ll" + conv).c_str(), (long long)v.to_i());
        } else if (std::strchr("feEgG", conv)) {
            std::snprintf(buf, sizeof buf, (spec + conv).c_str(), v.num());
        } else {
            raise("ValueError", std::string("unsupported format character '") + conv + "'");
        }
        out += buf;
    }
    if (ai < a.size() && args.k == TUPLE) raise("TypeError", "not all arguments converted during string formatting");
    return Py(out);
}
inline Py mod(const Py& a, const Py& b) {
    if (a.k == STR) return format(a, b);
    if (!a.is_num() || !b.is_num()) bad_operands("%", a, b);
    if (a.is_int() && b.is_int()) {
        if (b.i == 0) raise("ZeroDivisionError", "integer division or modulo by zero");
        int64_t r = a.i % b.i;
        if (r != 0 && ((r < 0) != (b.i < 0))) r += b.i;
        return Py(r);
    }
    double vx = a.num(), wx = b.num();
    if (wx == 0.0) raise("ZeroDivisionError", "float modulo");
    double m = std::fmod(vx, wx);
    if (m) {
        if ((wx < 0) != (m < 0)) m += wx;
    } else {
        m = std::copysign(0.0, wx);
    }
    return Py(m);
}
inline void print_(const Vec& v) {
    std::string s;
    for (size_t j = 0; j < v.size(); ++j) s += (j ? " " : "") + str(v[j]);
    std::fputs((s + "\n").c_str(), stdout);
}

// ---------------------------------------------------------------------------
//  the methods
// ---------------------------------------------------------------------------
inline Py Py::append(const Py& x) const {
    if (k != LIST) raise("AttributeError", "'" + type_name(*this) + "' object has no attribute 'append'");
    L_(*this)->v.push_back(x);
    return None;
}
inline Py Py::insert(const Py& at, const Py& x) const {
    Vec& v = vec();
    int64_t j = at.to_i(), n = (int64_t)v.size();
    if (j < 0) j = std::max<int64_t>(0, j + n);
    if (j > n) j = n;
    v.insert(v.begin() + j, x);
    return None;
}
inline Py Py::get(const Py& key, const Py& dflt) const {
    if (k != DICT) raise("AttributeError", "'" + type_name(*this) + "' object has no attribute 'get'");
    Py* p = D_(*this)->find(key);
    return p ? *p : dflt;
}
inline Py Py::setdefault(const Py& key, const Py& dflt) const {
    DictObj* d = D_(*this);
    Py* p = d->find(key);
    if (p) return *p;
    d->set(key, dflt);
    return dflt;
}
inline Py Py::items() const {
    Vec out;
    D_(*this)->each([&](const Py& kk, const Py& v) { out.push_back(tuple({kk, v})); });
    return list(std::move(out));
}
inline Py Py::keys() const { return list(items_of(*this)); }
inline Py Py::values() const {
    Vec out;
    D_(*this)->each([&](const Py&, const Py& v) { out.push_back(v); });
    return list(std::move(out));
}
inline Py Py::update(const Py& other) const {
    if (k == SET) {
        for (const Py& e : items_of(other)) S_(*this)->d.set(e, None);
        return None;
    }
    if (other.k == DICT)
        D_(other)->each([&](const Py& kk, const Py& v) { D_(*this)->set(kk, v); });
    else
        for (const Py& e : items_of(other)) {
            Vec kv = unpack(e, 2);
            D_(*this)->set(kv[0], kv[1]);
        }
    return None;
}
inline Py Py::index(const Py& x) const {
    if (k == STR) {                                     // str.index(sub)
        size_t at = str().find(x.str());
        if (at == std::string::npos) raise("ValueError", "substring not found");
        return Py((int64_t)add::detail::utf8_len(str().substr(0, at)));
    }
    const Vec& v = vec();
    for (size_t j = 0; j < v.size(); ++j)
        if (eq(v[j], x)) return Py((int64_t)j);
    raise("ValueError", repr(x) + " is not in list");
}
inline Py Py::count(const Py& x) const {
    int64_t n = 0;
    if (k == STR) {                                     // str.count(sub): non-overlapping
        const std::string& h = str();
        const std::string& w = x.str();
        if (w.empty()) return Py((int64_t)add::detail::utf8_len(h) + 1);
        for (size_t at = h.find(w); at != std::string::npos; at = h.find(w, at + w.size())) ++n;
        return Py(n);
    }
    for (const Py& e : vec())
        if (eq(e, x)) ++n;
    return Py(n);
}
inline Py Py::reverse() const {
    Vec& v = vec();
    std::reverse(v.begin(), v.end());
    return None;
}
inline Py Py::sort(const Py& key, const Py& rev) const {
    Py s = sorted(*this, key.missing() ? None : key, rev.missing() ? Py(false) : rev);
    vec() = L_(s)->v;
    return None;
}
inline Py Py::join(const Py& seq) const {
    std::string out;
    bool first = true;
    for (const Py& e : items_of(seq)) {
        if (!first) out += str();
        out += e.str();
        first = false;
    }
    return Py(out);
}
inline Py Py::startswith(const Py& s) const { return Py(str().compare(0, s.str().size(), s.str()) == 0); }

// mesh attributes (add.Mesh: M.V, M.F, M.C, M.UV are lists)
inline Py& mesh_attr(const Py& m, const char* name) {
    if (m.k != MESH) raise("AttributeError", "'" + type_name(m) + "' object has no attribute '" + name + "'");
    MeshObj* M = M_(m);
    switch (name[0]) {
        case 'V': return M->V;
        case 'F': return M->F;
        case 'C': return M->C;
        default: return M->UV;
    }
}

// ---------------------------------------------------------------------------
//  a clock, the environment
// ---------------------------------------------------------------------------
inline Py time_() {
    using namespace std::chrono;
    return Py(duration<double>(system_clock::now().time_since_epoch()).count());
}
inline Py environ_get(const Py& key, const Py& dflt) {
    const char* v = std::getenv(key.str().c_str());
    return v ? Py(std::string(v)) : dflt;
}

}  // namespace py

"""
py2cpp.py -- write the castle (examples/46_castle.py) out as C++
(examples/46_castle.cpp), statement by statement.

    python3 tools/py2cpp/py2cpp.py            examples/46_castle.py -> examples/46_castle.cpp
    python3 tools/py2cpp/py2cpp.py --check    is 46_castle.cpp up to date? (exit 1 if not)
    python3 tools/py2cpp/py2cpp.py IN.py OUT.cpp

Every function of the castle becomes a C++ function of the same name, every
statement a C++ statement, every comment stays where it was.  Python's
values are py::Py (pyrt.hpp: Python's rules for numbers, strings, lists,
dicts, ...) and add.py's functions are addpy::<name> (addbind.hpp: the same
calls of add.hpp), so the C++ program computes the same numbers in the same
order -- and writes the same castle, byte for byte.  The runtime goes into
the .cpp with the castle, so it needs only add.hpp.

It translates the Python the castle is written in, not every Python: a
construct it does not know stops it with the line number.
"""
import ast
import io
import os
import keyword
import sys
import tokenize

# ---------------------------------------------------------------------------
#  names
# ---------------------------------------------------------------------------
CPP_RESERVED = set("""
alignas alignof and and_eq asm auto bitand bitor bool break case catch char char16_t char32_t char8_t class compl
concept const consteval constexpr constinit const_cast continue co_await co_return co_yield decltype default delete do
double dynamic_cast else enum explicit export extern false float for friend goto if inline int long mutable namespace
new noexcept not not_eq nullptr operator or or_eq private protected public register reinterpret_cast requires return
short signed sizeof static static_assert static_cast struct switch template this thread_local throw true try typedef
typeid typename union unsigned using virtual void volatile wchar_t while xor xor_eq
main std py add addpy Py Vec Args None True False list tuple dict set_ range len each items_of call func sig
min max abs int_ float_ round_ sorted repr str format print_ truthy contains raise unpack slice getitem setitem
floordiv mod pow_ is iadd NONE BOOL INT FLOAT STR LIST TUPLE DICT SET FUNC MESH INST STREAM MISSING
errno stdin stdout stderr EOF NULL assert near far small time signal y0 y1 yn j0 j1 jn exp log floor ceil sqrt sin cos
tan pi gamma isnan isinf fabs index
""".split())

PURE_ADD = {"pi", "cos", "sin", "sqrt", "atan2", "floor", "radians", "clamp", "acos", "tan", "atan", "asin", "ceil",
            "hypot", "exp", "rgb", "shade", "transparent", "lerp", "text_width", "bbox"}
PURE_BUILTINS = {"len", "int", "float", "abs", "round", "min", "max", "range", "list", "tuple", "zip", "enumerate",
                 "sorted", "sum", "any", "all", "reversed", "callable", "isinstance", "str", "dict", "set", "next"}

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ADD_SIGS = {}       # add.py's signatures: name -> (names, has_varargs, has_kwargs)


def load_add_sigs():
    import inspect
    sys.path.insert(0, ROOT)
    import add
    for name in dir(add):
        f = getattr(add, name)
        if callable(f):
            try:
                s = inspect.signature(f)
            except (TypeError, ValueError):
                continue
            names, var, kw = [], False, False
            for p in s.parameters.values():
                if p.kind == p.VAR_POSITIONAL:
                    var = True
                elif p.kind == p.VAR_KEYWORD:
                    kw = True
                else:
                    names.append(p.name)
            ADD_SIGS[name] = (names, var, kw)
    ADD_SIGS["hypot"] = (["x", "y"], False, False)


def runtime_names(paths):
    """The names the runtime declares in namespace py (castle names that are the same get a '_')."""
    import re
    out = set()
    for path in paths:
        text = open(path).read()
        text = text.split("namespace addpy")[0] if "namespace addpy" in text else text
        for m in re.finditer(r"^inline\s+(?:const\s+)?[\w:<>,&\*\s]*?\b(\w+)\s*\(", text, re.M):
            out.add(m.group(1))
        for m in re.finditer(r"^inline\s+const\s+Py\s+(\w+)\s*=", text, re.M):
            out.add(m.group(1))
        for m in re.finditer(r"^struct\s+(\w+)", text, re.M):
            out.add(m.group(1))
    return out


def cname(name):
    """A Python name as a C++ name."""
    return name + "__" if name in CPP_RESERVED else name


def cstr(s):
    """A C++ string literal."""
    out = []
    for ch in s:
        o = ord(ch)
        if ch == "\\":
            out.append("\\\\")
        elif ch == '"':
            out.append('\\"')
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\t":
            out.append("\\t")
        elif o < 32:
            out.append("\\x%02x" % o)
        else:
            out.append(ch)
    return '"' + "".join(out) + '"'


def cfloat(x):
    r = repr(x)
    if r == "inf":
        return "INFINITY"
    if r == "-inf":
        return "-INFINITY"
    if "e" not in r and "." not in r:
        r += ".0"
    return r


# ---------------------------------------------------------------------------
#  scopes: which names are whose, which must live in cells
# ---------------------------------------------------------------------------
class Scope:
    def __init__(self, node, kind, parent):
        self.node, self.kind, self.parent = node, kind, parent    # kind: module, func, lambda, comp, class
        self.bound = set()
        self.params = []
        self.cells = set()          # bound here, used by an inner def or lambda
        self.frees = set()          # used here, bound in an enclosing function
        self.children = []
        if parent:
            parent.children.append(self)

    def is_closure(self):
        return self.kind in ("func", "lambda")


def target_names(t, out):
    if isinstance(t, ast.Name):
        out.add(t.id)
    elif isinstance(t, (ast.Tuple, ast.List)):
        for e in t.elts:
            target_names(e, out)
    elif isinstance(t, ast.Starred):
        target_names(t.value, out)


class ScopeBuilder(ast.NodeVisitor):
    """First pass: every scope's bound names."""

    def __init__(self):
        self.scopes = {}            # id(node) -> Scope
        self.stack = []

    def push(self, node, kind):
        s = Scope(node, kind, self.stack[-1] if self.stack else None)
        self.scopes[id(node)] = s
        self.stack.append(s)
        return s

    def pop(self):
        self.stack.pop()

    def cur(self):
        return self.stack[-1]

    def visit_Module(self, node):
        self.push(node, "module")
        self.generic_visit(node)
        self.pop()

    def args_of(self, a):
        return [x.arg for x in a.posonlyargs + a.args] + ([a.vararg.arg] if a.vararg else []) + \
            [x.arg for x in a.kwonlyargs] + ([a.kwarg.arg] if a.kwarg else [])

    def visit_FunctionDef(self, node):
        self.cur().bound.add(node.name)
        for d in node.args.defaults + [d for d in node.args.kw_defaults if d is not None]:
            self.visit(d)
        s = self.push(node, "func")
        s.params = self.args_of(node.args)
        s.bound.update(s.params)
        for st in node.body:
            self.visit(st)
        self.pop()

    def visit_Lambda(self, node):
        for d in node.args.defaults + [d for d in node.args.kw_defaults if d is not None]:
            self.visit(d)
        s = self.push(node, "lambda")
        s.params = self.args_of(node.args)
        s.bound.update(s.params)
        self.visit(node.body)
        self.pop()

    def visit_ClassDef(self, node):
        self.cur().bound.add(node.name)
        s = self.push(node, "class")
        for st in node.body:
            self.visit(st)
        self.pop()

    def comp(self, node, elts):
        gens = node.generators
        self.visit(gens[0].iter)                    # (the first iterable: in the enclosing scope)
        s = self.push(node, "comp")
        for i, g in enumerate(gens):
            target_names(g.target, s.bound)
            self.visit(g.target)
            if i:
                self.visit(g.iter)
            for c in g.ifs:
                self.visit(c)
        for e in elts:
            self.visit(e)
        self.pop()

    def visit_ListComp(self, node):
        self.comp(node, [node.elt])

    def visit_SetComp(self, node):
        self.comp(node, [node.elt])

    def visit_GeneratorExp(self, node):
        self.comp(node, [node.elt])

    def visit_DictComp(self, node):
        self.comp(node, [node.key, node.value])

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.cur().bound.add(node.id)

    def visit_Import(self, node):
        for a in node.names:
            self.cur().bound.add((a.asname or a.name).split(".")[0])


class ScopeResolver(ast.NodeVisitor):
    """Second pass: every name read, resolved to the scope that binds it."""

    def __init__(self, scopes):
        self.scopes = scopes
        self.stack = []
        self.where = {}             # id(Name node) -> the Scope that binds it (None: global/builtin)

    def enter(self, node):
        self.stack.append(self.scopes[id(node)])

    def resolve(self, name):
        cur = self.stack[-1]
        if cur.kind == "module":
            return None
        if name in cur.bound and cur.kind != "class":
            return cur
        chain = []
        s = cur.parent
        while s is not None:
            if s.kind == "class":
                s = s.parent
                continue
            if s.kind == "module":
                return None
            if name in s.bound:
                # a cell, when some def or lambda between here and there (or here) uses it
                closures = [cur] + chain
                if any(c.is_closure() for c in closures):
                    s.cells.add(name)
                for c in closures:
                    c.frees.add(name)
                return s
            chain.append(s)
            s = s.parent
        return None

    def visit_Module(self, node):
        self.enter(node)
        self.generic_visit(node)
        self.stack.pop()

    def visit_FunctionDef(self, node):
        for d in node.args.defaults + [d for d in node.args.kw_defaults if d is not None]:
            self.visit(d)
        self.enter(node)
        for st in node.body:
            self.visit(st)
        self.stack.pop()

    def visit_Lambda(self, node):
        for d in node.args.defaults + [d for d in node.args.kw_defaults if d is not None]:
            self.visit(d)
        self.enter(node)
        self.visit(node.body)
        self.stack.pop()

    def visit_ClassDef(self, node):
        self.enter(node)
        for st in node.body:
            self.visit(st)
        self.stack.pop()

    def comp(self, node, elts):
        gens = node.generators
        self.visit(gens[0].iter)
        self.enter(node)
        for i, g in enumerate(gens):
            self.visit(g.target)
            if i:
                self.visit(g.iter)
            for c in g.ifs:
                self.visit(c)
        for e in elts:
            self.visit(e)
        self.stack.pop()

    def visit_ListComp(self, node):
        self.comp(node, [node.elt])

    def visit_SetComp(self, node):
        self.comp(node, [node.elt])

    def visit_GeneratorExp(self, node):
        self.comp(node, [node.elt])

    def visit_DictComp(self, node):
        self.comp(node, [node.key, node.value])

    def visit_Name(self, node):
        self.where[id(node)] = self.resolve(node.id)


# ---------------------------------------------------------------------------
#  comments: every line's own comment, to carry over
# ---------------------------------------------------------------------------
def line_comments(src):
    out = {}
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type == tokenize.COMMENT:
            out[tok.start[0]] = (tok.start[1], tok.string[1:].rstrip())
    return out


# ---------------------------------------------------------------------------
#  the translator
# ---------------------------------------------------------------------------
class E:
    """A translated expression: its C++ text, and what it is in C++: 'py'
    (a py::Py), 'lit' (a C++ literal: needs Py(...) where both sides are),
    'bool' (a C++ bool), 'range' (a py::Range)."""

    def __init__(self, code, kind="py", prec=100):
        self.code, self.kind, self.prec = code, kind, prec

    def __str__(self):
        return self.code


PREC = {ast.Or: 1, ast.And: 2, ast.Not: 3, "cmp": 4, ast.BitOr: 5, ast.BitXor: 6, ast.BitAnd: 7, ast.LShift: 8,
        ast.RShift: 8, ast.Add: 9, ast.Sub: 9, ast.Mult: 10, ast.Div: 10, ast.FloorDiv: 10, ast.Mod: 10,
        ast.MatMult: 10, "unary": 11, ast.Pow: 12}
CPP_PREC = {ast.Add: 6, ast.Sub: 6, ast.Mult: 5, ast.Div: 5, ast.BitAnd: 11, ast.BitOr: 13, ast.BitXor: 12,
            ast.LShift: 7, ast.RShift: 7}
CPP_OP = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/", ast.BitAnd: "&", ast.BitOr: "|", ast.BitXor: "^",
          ast.LShift: "<<", ast.RShift: ">>"}


class Translator:
    def __init__(self, src, path):
        self.src = src
        self.lines = src.split("\n")
        self.tree = ast.parse(src, path)
        sb = ScopeBuilder()
        sb.visit(self.tree)
        self.scopes = sb.scopes
        res = ScopeResolver(self.scopes)
        res.visit(self.tree)
        self.where = res.where
        self.module = self.scopes[id(self.tree)]
        self.comments = line_comments(src)
        self.used_comment_lines = set()
        self.tmp = 0
        self.out = []                   # function definitions
        self.main = []                  # the module's own statements
        self.globals = set()
        self.static_funcs = {}          # name -> FunctionDef (defined once at module level, never rebound)
        self.dyn_defs = {}              # id(FunctionDef) -> C++ name of a function bound more than once
        self.func_sigs = {}             # name -> (params, varargs, kwargs, node)
        self.scope_stack = [self.module]
        self.func_stack = []
        self.prepare_module()

    # -- the module's names ---------------------------------------------------
    def prepare_module(self):
        stores = {}

        def visit(node):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                stores.setdefault(node.name, []).append(node)
                return
            if isinstance(node, (ast.Lambda, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                return
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                stores.setdefault(node.id, []).append(node)
            for c in ast.iter_child_nodes(node):
                visit(c)
        for st in self.tree.body:
            visit(st)
        counter = {}
        for name, nodes in stores.items():
            defs = [n for n in nodes if isinstance(n, ast.FunctionDef)]
            if len(nodes) == 1 and len(defs) == 1 and defs[0] in self.tree.body:
                self.static_funcs[name] = defs[0]
                f = defs[0]
                a = f.args
                self.func_sigs[name] = ([x.arg for x in a.args], a.vararg.arg if a.vararg else None,
                                        a.kwarg.arg if a.kwarg else None, f)
            else:
                for d in defs:
                    counter[name] = counter.get(name, 0) + 1
                    self.dyn_defs[id(d)] = "%s__%d" % (cname(name), counter[name])
                if name != "Spots":
                    self.globals.add(name)
        for name in self.module.bound:
            if name not in self.static_funcs and name not in ("os", "sys", "time", "add", "Spots"):
                self.globals.add(name)

    # -- helpers ----------------------------------------------------------------
    def fresh(self, base="t"):
        self.tmp += 1
        return "_%s%d" % (base, self.tmp)

    def scope(self):
        return self.scope_stack[-1]

    def comment_for(self, node, last=None):
        """The comments on the lines of a statement (header lines for a compound one)."""
        first = node.lineno
        if last is None:
            last = getattr(node, "end_lineno", first)
        texts = []
        for ln in range(first, last + 1):
            c = self.comments.get(ln)
            if c and ln not in self.used_comment_lines:
                self.used_comment_lines.add(ln)
                texts.append(c[1].strip())
        return texts

    def leading_comments(self, node, ind, sink):
        """Whole-line comments just above a statement."""
        ln = node.lineno - 1
        block = []
        while ln >= 1:
            text = self.lines[ln - 1].strip()
            if text.startswith("#") and ln not in self.used_comment_lines:
                block.append(ln)
                ln -= 1
            elif text == "" and block == []:
                ln -= 1
                if ln < node.lineno - 3:
                    break
            else:
                break
        for l in reversed(block):
            self.used_comment_lines.add(l)
            sink.append(ind + "// " + self.lines[l - 1].strip()[1:].strip())

    # -- names --------------------------------------------------------------
    def name_ref(self, node):
        """A Name being read."""
        name = node.id
        sc = self.where.get(id(node), "unknown")
        if sc == "unknown":
            sc = None
        if sc is not None:
            if name in sc.cells:
                return E("(*%s__c)" % cname(name))
            return E(cname(name))
        # global or builtin
        if name in self.static_funcs:
            return E("F_" + name)
        if name in self.globals:
            return E(cname(name))
        if name == "True":
            return E("True")
        if name == "False":
            return E("False")
        if name == "None":
            return E("None")
        raise NotImplementedError("name %r (line %d)" % (name, node.lineno))

    def store_name(self, name, node=None):
        """The C++ lvalue of a name being assigned in the current scope."""
        sc = self.scope()
        if sc.kind == "module":
            return cname(name)
        if name in sc.cells:
            return "(*%s__c)" % cname(name)
        return cname(name)

    # -- purity: may evaluating it change something, or depend on order? ----
    def impure(self, node):
        for n in ast.walk(node):
            if isinstance(n, ast.Call):
                f = n.func
                if isinstance(f, ast.Name) and f.id in PURE_BUILTINS:
                    continue
                if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id == "add" and \
                        f.attr in PURE_ADD:
                    continue
                if isinstance(f, ast.Name) and f.id in self.static_funcs and f.id in self.pure_funcs:
                    continue
                return True
        return False

    # -- expressions ----------------------------------------------------------
    def py(self, e):
        """An expression as a py::Py (wrapping literals and bools)."""
        if e.kind in ("lit", "bool"):
            return "Py(%s)" % e.code
        if e.kind == "range":
            return "Py(%s)" % e.code
        return e.code

    def truth(self, node):
        """An expression as a C++ bool."""
        e = self.expr(node, ctx="bool")
        if e.kind == "bool":
            return e.code
        if e.kind == "lit":
            return "truthy(Py(%s))" % e.code
        return "truthy(%s)" % e.code

    def expr(self, node, ctx="value"):
        m = getattr(self, "x_" + type(node).__name__, None)
        if m is None:
            raise NotImplementedError("%s at line %d" % (type(node).__name__, node.lineno))
        return m(node, ctx) if type(node).__name__ in ("BoolOp", "UnaryOp", "Compare") else m(node)

    def x_Constant(self, node):
        v = node.value
        if v is None:
            return E("None")
        if v is True:
            return E("True")
        if v is False:
            return E("False")
        if isinstance(v, int):
            if abs(v) >= 2 ** 31:
                return E("Py(%dLL)" % v)
            return E(str(v), "lit") if v >= 0 else E("Py(%d)" % v)
        if isinstance(v, float):
            c = cfloat(v)
            return E(c, "lit") if not c.startswith("-") else E("Py(%s)" % c)
        if isinstance(v, str):
            return E("S(%s)" % cstr(v))
        raise NotImplementedError("constant %r" % (v,))

    def x_Name(self, node):
        return self.name_ref(node)

    def operand(self, node, e, parent_prec, right=False, wrap=False):
        """An operand of a C++ operator: parenthesised where C++ would read it otherwise."""
        code = self.py(e) if wrap or e.kind == "range" else e.code
        if isinstance(node, ast.BinOp) and type(node.op) in CPP_OP:
            cp = CPP_PREC[type(node.op)]
            if cp > parent_prec or (right and cp == parent_prec):
                code = "(" + code + ")"
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub) and code.startswith("-"):
            code = "(" + code + ")"
        elif isinstance(node, (ast.IfExp, ast.BoolOp, ast.Compare)) or (e.kind == "bool"):
            code = "Py(" + code + ")" if e.kind == "bool" else "(" + code + ")"
        return code

    def x_BinOp(self, node):
        op = type(node.op)
        if self.impure(node.left) and self.impure(node.right):
            l, r = self.fresh(), self.fresh()
            inner = self.binop(op, l, r)
            return E("[&] { Py %s = %s; Py %s = %s; return %s; }()" % (l, self.py(self.expr(node.left)), r,
                                                                      self.py(self.expr(node.right)), inner))
        le, re_ = self.expr(node.left), self.expr(node.right)
        raw = le.kind in ("lit", "bool") and re_.kind in ("lit", "bool")     # (two C++ numbers: one made a Py)
        if op in CPP_OP:
            p = CPP_PREC[op]
            l = self.operand(node.left, le, p, wrap=raw)
            r = self.operand(node.right, re_, p, right=True)
            return E("%s %s %s" % (l, CPP_OP[op], r), prec=p)
        return E(self.binop(op, self.py(le), self.py(re_)))

    def binop(self, op, l, r):
        if op in CPP_OP:
            return "%s %s %s" % (l, CPP_OP[op], r)
        if op is ast.FloorDiv:
            return "floordiv(%s, %s)" % (l, r)
        if op is ast.Mod:
            return "mod(%s, %s)" % (l, r)
        if op is ast.Pow:
            return "pow_(%s, %s)" % (l, r)
        raise NotImplementedError(op.__name__)

    def x_UnaryOp(self, node, ctx="value"):
        op = node.op
        if isinstance(op, ast.Not):
            return E("!%s" % self.paren_bool(self.truth(node.operand)), "bool")
        e = self.expr(node.operand)
        if isinstance(op, ast.USub):
            if e.kind == "lit":
                return E("Py(-%s)" % e.code)
            c = self.py(e)
            if isinstance(node.operand, (ast.BinOp, ast.UnaryOp)):
                c = "(" + c + ")"
            return E("-" + c)
        if isinstance(op, ast.UAdd):
            return E("+" + self.py(e))
        if isinstance(op, ast.Invert):
            return E("~" + self.py(e))
        raise NotImplementedError

    def paren_bool(self, code):
        if self.is_atom(code):
            return code
        return "(" + code + ")"

    @staticmethod
    def is_atom(code):
        """Is ``code`` one operand as it stands: a name, or a name(...) / (...) whose first bracket closes at the end?"""
        if code.replace("_", "").replace(":", "").isalnum():
            return True
        i = 0
        while i < len(code) and (code[i].isalnum() or code[i] in "_:!"):
            i += 1
        if i >= len(code) or code[i] != "(" or not code.endswith(")"):
            return False
        depth = 0
        in_str = False
        for j in range(i, len(code)):
            ch = code[j]
            if in_str:
                if ch == "\\":
                    continue
                if ch == '"' and code[j - 1] != "\\":
                    in_str = False
                continue
            if ch == '"':
                in_str = True
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    return j == len(code) - 1
        return False

    def x_BoolOp(self, node, ctx="value"):
        isand = isinstance(node.op, ast.And)
        if ctx == "bool":
            parts = [self.paren_bool(self.truth(v)) for v in node.values]
            return E((" && " if isand else " || ").join(parts), "bool")
        # a value: the first falsy (and) / truthy (or) one, or the last
        t = self.fresh()
        body = ["Py %s = %s;" % (t, self.py(self.expr(node.values[0])))]
        for v in node.values[1:]:
            body.append("if (%struthy(%s)) return %s;" % ("!" if isand else "", t, t))
            body.append("%s = %s;" % (t, self.py(self.expr(v))))
        body.append("return %s;" % t)
        return E("[&]() -> Py { %s }()" % " ".join(body))

    def cmp1(self, op, l, r):
        if isinstance(op, ast.In):
            return "contains(%s, %s)" % (r, l)
        if isinstance(op, ast.NotIn):
            return "!contains(%s, %s)" % (r, l)
        if isinstance(op, ast.Is):
            return "is(%s, %s)" % (l, r)
        if isinstance(op, ast.IsNot):
            return "!is(%s, %s)" % (l, r)
        sym = {ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">=", ast.Eq: "==", ast.NotEq: "!="}[type(op)]
        return "%s %s %s" % (l, sym, r)

    def cmp_operand(self, e, node=None):
        c = self.py(e) if e.kind in ("range",) else (e.code if e.kind in ("lit", "py") else self.py(e))
        if node is not None and isinstance(node, (ast.BinOp, ast.IfExp, ast.BoolOp, ast.Compare)) and not c.startswith("["):
            if not (c.startswith("(") and c.endswith(")")):
                c = "(" + c + ")"
        return c

    def x_Compare(self, node, ctx="value"):
        ops, comps = node.ops, node.comparators
        if len(ops) == 1:
            le, re_ = self.expr(node.left), self.expr(comps[0])
            l = self.cmp_operand(le, node.left)
            r = self.cmp_operand(re_, comps[0])
            if le.kind == "lit" and re_.kind == "lit":
                l = "Py(%s)" % l
            if self.impure(node.left) and self.impure(comps[0]):
                a, b = self.fresh(), self.fresh()
                return E("[&] { Py %s = %s; Py %s = %s; return %s; }()" % (a, l, b, r, self.cmp1(ops[0], a, b)), "bool")
            # (a None or a constant on the left: no Py(...) wrapping needed, Py converts)
            return E(self.cmp1(ops[0], l, r), "bool")
        # a chain: a < b < c -- b once
        names = [self.fresh() for _ in range(len(comps) + 1)]
        body = ["Py %s = %s;" % (names[0], self.py(self.expr(node.left)))]
        for i, (op, c) in enumerate(zip(ops, comps)):
            body.append("Py %s = %s;" % (names[i + 1], self.py(self.expr(c))))
            if i < len(ops) - 1:
                body.append("if (!(%s)) return false;" % self.cmp1(op, names[i], names[i + 1]))
            else:
                body.append("return %s;" % self.cmp1(op, names[i], names[i + 1]))
        return E("[&]() -> bool { %s }()" % " ".join(body), "bool")

    def x_IfExp(self, node):
        return E("(%s ? %s : %s)" % (self.truth(node.test), self.py(self.expr(node.body)), self.py(self.expr(node.orelse))))

    def seq_items(self, elts):
        """{a, b, c} -- or, with *x among them, a Vec put together."""
        if not any(isinstance(e, ast.Starred) for e in elts):
            return "{%s}" % ", ".join(self.py(self.expr(e)) for e in elts), False
        t = self.fresh("v")
        parts = ["Vec %s;" % t]
        for e in elts:
            if isinstance(e, ast.Starred):
                parts.append("star_into(%s, %s);" % (t, self.py(self.expr(e.value))))
            else:
                parts.append("%s.push_back(%s);" % (t, self.py(self.expr(e))))
        return "[&] { %s return %s; }()" % (" ".join(parts), t), True

    def x_List(self, node):
        items, built = self.seq_items(node.elts)
        return E("list(%s)" % items) if not built else E("list(%s)" % items)

    def x_Tuple(self, node):
        items, built = self.seq_items(node.elts)
        if not built and node.elts and all(self.is_const(e) for e in node.elts):
            return E("K(tuple(%s))" % items)                  # (a tuple of constants: made once, as Python does)
        return E("tuple(%s)" % items)

    def x_Set(self, node):
        items, built = self.seq_items(node.elts)
        return E("set_(%s)" % items) if not built else E("set_of(list(%s))" % items)

    def x_Dict(self, node):
        if any(k is None for k in node.keys):
            t = self.fresh("d")
            parts = ["Py %s = dict();" % t]
            for k, v in zip(node.keys, node.values):
                if k is None:
                    parts.append("%s.update(%s);" % (t, self.py(self.expr(v))))
                else:
                    parts.append("setitem(%s, %s, %s);" % (t, self.py(self.expr(k)), self.py(self.expr(v))))
            return E("[&] { %s return %s; }()" % (" ".join(parts), t))
        return E("dict({%s})" % ", ".join("{%s, %s}" % (self.py(self.expr(k)), self.py(self.expr(v)))
                                           for k, v in zip(node.keys, node.values)))

    def x_Subscript(self, node):
        v = self.py(self.expr(node.value))
        s = node.slice
        if isinstance(s, ast.Slice):
            parts = [self.py(self.expr(x)) if x is not None else "None" for x in (s.lower, s.upper, s.step)]
            if s.step is None:
                return E("slice(%s, %s, %s)" % (v, parts[0], parts[1]))
            return E("slice(%s, %s, %s, %s)" % (v, parts[0], parts[1], parts[2]))
        if isinstance(s, ast.Tuple):
            return E("%s[%s]" % (self.wrap_postfix(v), self.py(self.x_Tuple(s))))
        k = self.expr(s)
        if k.kind == "lit" and k.code.isdigit():
            return E("%s[%s]" % (self.wrap_postfix(v), k.code))
        return E("%s[%s]" % (self.wrap_postfix(v), self.py(k)))

    def wrap_postfix(self, code):
        """Something to put [..] or .x after: parenthesised unless it is a plain name or call."""
        if code.replace("_", "").replace(":", "").isalnum():
            return code
        if code.startswith("(*") and code.endswith(")"):
            return code
        depth = 0
        for i, ch in enumerate(code):
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
            elif depth == 0 and not (ch.isalnum() or ch in "_:.<>"):
                return "(" + code + ")"
        return code

    def x_Attribute(self, node):
        v = node.value
        if isinstance(v, ast.Name) and v.id == "add" and self.where.get(id(v)) is None:
            if node.attr == "pi":
                return E("addpy::pi")
            return E("ADDF_" + node.attr)           # (an add.py function as a value)
        if isinstance(v, ast.Name) and v.id == "os" and node.attr == "environ":
            return E("ENVIRON")
        o = self.py(self.expr(v))
        a = node.attr
        if a in ("V", "F", "C", "UV"):
            return E("mesh_%s(%s)" % (a, o))
        if a in ("faces", "vertices", "bytes", "materials"):
            return E("stream_attr(%s, %s)" % (o, cstr(a)))
        if a == "cells":
            return E("inst_attr(%s, %s)" % (o, cstr(a)))
        raise NotImplementedError("attribute .%s at line %d" % (a, node.lineno))

    # -- calls ------------------------------------------------------------------
    def args_list(self, node, sig_names=None, varargs=None, kwargs=None, fname="?"):
        """Positional C++ arguments for a call with a known signature: keywords put in their places,
        the gaps filled with MISSING_ARG (the default), *args packed into a tuple, **kw into a dict."""
        pos = list(node.args)
        if any(isinstance(a, ast.Starred) for a in pos) or any(k.arg is None for k in node.keywords):
            return None
        names = sig_names
        n = len(names)
        out = [None] * n
        extra_pos = []
        for i, a in enumerate(pos):
            if i < n:
                out[i] = a
            else:
                extra_pos.append(a)
        extra_kw = []
        for k in node.keywords:
            if k.arg in names:
                j = names.index(k.arg)
                if out[j] is not None:
                    raise ValueError("%s: argument %s given twice (line %d)" % (fname, k.arg, node.lineno))
                out[j] = k.value
            else:
                extra_kw.append(k)
        if extra_pos and not varargs:
            raise ValueError("%s: too many arguments (line %d)" % (fname, node.lineno))
        if extra_kw and not kwargs:
            raise ValueError("%s: unknown keyword %s (line %d)" % (fname, extra_kw[0].arg, node.lineno))
        # evaluated left to right as written in Python, when it matters
        written = list(pos) + [k.value for k in node.keywords]
        order_matters = sum(1 for a in written if self.impure(a)) >= 2
        code = []
        last = max([i for i in range(n) if out[i] is not None] + [-1])
        for i in range(last + 1):
            code.append(self.py(self.expr(out[i])) if out[i] is not None else "MISSING_ARG")
        if varargs:
            while len(code) < n:
                code.append("MISSING_ARG")
            code.append("tuple({%s})" % ", ".join(self.py(self.expr(a)) for a in extra_pos))
        if kwargs:
            while len(code) < n + (1 if varargs else 0):
                code.append("MISSING_ARG")
            code.append("dict({%s})" % ", ".join("{Py(%s), %s}" % (cstr(k.arg), self.py(self.expr(k.value)))
                                                  for k in extra_kw))
        return code, order_matters, written

    def sequenced_call(self, fn, code, written_nodes):
        """f(a, b) where a and b must be evaluated in this order: through temporaries."""
        temps = []
        args = []
        for c in code:
            if c == "MISSING_ARG" or c.replace("_", "").replace(".", "").isalnum():
                args.append(c)
            else:
                t = self.fresh("a")
                temps.append("Py %s = %s;" % (t, c))
                args.append(t)
        return "[&] { %s return %s(%s); }()" % (" ".join(temps), fn, ", ".join(args))

    def dyn_call(self, fcode, node):
        """A call through a value: py::call with the arguments bound by name at run time."""
        pos = []
        star = False
        for a in node.args:
            if isinstance(a, ast.Starred):
                star = True
        kws = node.keywords
        if not star and not any(k.arg is None for k in kws):
            p = ", ".join(self.py(self.expr(a)) for a in node.args)
            if not kws:
                return E("call(%s, {%s})" % (fcode, p))
            k = ", ".join("{%s, %s}" % (cstr(x.arg), self.py(self.expr(x.value))) for x in kws)
            return E("call(%s, Args(Vec{%s}, {%s}))" % (fcode, p, k))
        t = self.fresh("args")
        parts = ["Args %s;" % t]
        for a in node.args:
            if isinstance(a, ast.Starred):
                parts.append("star_into(%s.pos, %s);" % (t, self.py(self.expr(a.value))))
            else:
                parts.append("%s.pos.push_back(%s);" % (t, self.py(self.expr(a))))
        for k in kws:
            if k.arg is None:
                parts.append("starstar_into(%s.kw, %s);" % (t, self.py(self.expr(k.value))))
            else:
                parts.append("%s.kw.emplace_back(%s, %s);" % (t, cstr(k.arg), self.py(self.expr(k.value))))
        return E("[&] { %s return call(%s, std::move(%s)); }()" % (" ".join(parts), fcode, t))

    def x_Call(self, node):
        f = node.func
        # add.<name>(...)
        if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id == "add" and \
                self.where.get(id(f.value)) is None:
            return self.add_call(f.attr, node)
        # x.method(...)
        if isinstance(f, ast.Attribute):
            return self.method_call(f, node)
        # globals()["name"](...)
        if isinstance(f, ast.Subscript) and isinstance(f.value, ast.Call) and isinstance(f.value.func, ast.Name) and \
                f.value.func.id == "globals":
            name = f.slice.value
            e = self.static_call(name, node)
            return E(e.code.replace(cname(name) + "(", "castle::" + cname(name) + "(", 1))
        if isinstance(f, ast.Name):
            sc = self.where.get(id(f))
            if sc is None:
                if f.id in self.static_funcs:
                    return self.static_call(f.id, node)
                if f.id in self.globals:
                    return self.dyn_call(cname(f.id), node)
                return self.builtin_call(f.id, node)
            return self.dyn_call(self.name_ref(f).code, node)
        return self.dyn_call(self.py(self.expr(f)), node)

    def static_call(self, name, node):
        names, var, kw, fnode = self.func_sigs[name]
        r = self.args_list(node, names, var, kw, name)
        if r is None:
            return self.dyn_call("F_" + name, node)
        code, order_matters, written = r
        fn = cname(name)
        if order_matters:
            return E(self.sequenced_call(fn, code, written))
        return E("%s(%s)" % (fn, ", ".join(code)))

    def add_call(self, name, node):
        if name == "make":
            return self.add_make(node)
        if name in ("difference",):
            first = self.py(self.expr(node.args[0]))
            rest = self.seq_items(node.args[1:])[0]
            color = "None"
            for k in node.keywords:
                if k.arg == "color":
                    color = self.py(self.expr(k.value))
                else:
                    raise NotImplementedError("difference keyword %s" % k.arg)
            return E("addpy::difference(%s, tuple(%s), %s)" % (first, rest, color))
        if name in ("union", "intersect"):
            items = self.seq_items(node.args)[0]
            fn = "union_" if name == "union" else name
            return E("addpy::%s(tuple(%s))" % (fn, items))
        if name == "uniform" and any(isinstance(a, ast.Starred) for a in node.args):
            t = self.fresh("u")
            return E("[&] { Vec %s = items_of(%s); return addpy::uniform(%s[0], %s[1]); }()" %
                     (t, self.py(self.expr(node.args[0].value)), t, t))
        if name == "stream":
            pass
        if name not in ADD_SIGS:
            raise NotImplementedError("add.%s" % name)
        names, var, kw = ADD_SIGS[name]
        r = self.args_list(node, names, var, kw, "add." + name)
        if r is None:
            raise NotImplementedError("add.%s with * or ** (line %d)" % (name, node.lineno))
        code, order_matters, written = r
        fn = "addpy::" + name
        if order_matters:
            return E(self.sequenced_call(fn, code, written))
        return E("%s(%s)" % (fn, ", ".join(code)))

    def add_make(self, node):
        draw = node.args[0]
        rest = ast.Call(func=draw, args=node.args[1:], keywords=node.keywords)
        ast.copy_location(rest, node)
        if isinstance(draw, ast.Attribute) and isinstance(draw.value, ast.Name) and draw.value.id == "add":
            inner = self.add_call(draw.attr, rest)
        elif isinstance(draw, ast.Name) and self.where.get(id(draw)) is None and draw.id in self.static_funcs:
            inner = self.static_call(draw.id, rest)
        else:
            inner = self.dyn_call(self.py(self.expr(draw)), rest)
        return E("addpy::make([&] { %s; })" % inner.code)

    def method_call(self, f, node):
        obj_node, m = f.value, f.attr
        # modules
        if isinstance(obj_node, ast.Attribute) and isinstance(obj_node.value, ast.Name) and obj_node.value.id == "sys" \
                and obj_node.attr == "stdout" and m == "flush":
            return E("Py((std::fflush(stdout), 0))")
        if isinstance(obj_node, ast.Attribute) and isinstance(obj_node.value, ast.Name) and obj_node.value.id == "os" \
                and obj_node.attr == "environ" and m == "get":
            a = [self.py(self.expr(x)) for x in node.args]
            return E("environ_get(%s, %s)" % (a[0], a[1] if len(a) > 1 else "None"))
        if isinstance(obj_node, ast.Name) and obj_node.id == "time" and m == "time":
            return E("time_()")
        o = self.py(self.expr(obj_node))
        args = [self.py(self.expr(a)) for a in node.args if not isinstance(a, ast.Starred)]
        if any(isinstance(a, ast.Starred) for a in node.args):
            raise NotImplementedError("*args in a method call (line %d)" % node.lineno)
        kw = {k.arg: self.py(self.expr(k.value)) for k in node.keywords}
        if len([a for a in node.args if self.impure(a)] + [k for k in node.keywords if self.impure(k.value)]) >= 2:
            raise NotImplementedError("two impure arguments to a method (line %d)" % node.lineno)
        po = self.wrap_postfix(o)
        if m in ("add_face",):
            a = args + [kw[k] for k in ("color", "uv") if k in kw]
            return E("mesh_add_face(%s)" % ", ".join([o] + a))
        if m in ("add_vertex", "add_polygon"):
            a = args + [kw[k] for k in ("color",) if k in kw]
            return E("mesh_%s(%s)" % (m, ", ".join([o] + a)))
        if m == "add":
            a = args + [kw[k] for k in ("clean",) if k in kw]
            return E("method_add(%s)" % ", ".join([o] + a))
        if m == "near":
            return E("method_near(%s)" % ", ".join([o] + args))
        if m == "close":
            return E("stream_close(%s)" % o)
        if m == "sort":
            return E("%s.sort(%s, %s)" % (po, kw.get("key", "None"), kw.get("reverse", "False")))
        if m == "update" and kw:
            t = self.fresh("o")
            parts = ["Py %s = %s;" % (t, o)] + ["%s.update(%s);" % (t, x) for x in args]
            parts += ["setitem(%s, Py(%s), %s);" % (t, cstr(k.arg), self.py(self.expr(k.value))) for k in node.keywords]
            return E("[&] { %s return None; }()" % " ".join(parts))
        if kw:
            raise NotImplementedError("keywords to .%s (line %d)" % (m, node.lineno))
        if m in ("append", "extend", "insert", "pop", "get", "setdefault", "items", "keys", "values", "update", "copy",
                 "index", "reverse", "join", "startswith", "count"):
            return E("%s.%s(%s)" % (po, m, ", ".join(args)))
        raise NotImplementedError("method .%s (line %d)" % (m, node.lineno))

    # -- builtins -----------------------------------------------------------------
    def items_vec(self, node):
        """A sequence argument as a C++ Vec (a generator expression run here)."""
        if isinstance(node, ast.GeneratorExp):
            return "L_(%s)->v" % self.comp_code(node, "list")
        return "items_of(%s)" % self.py(self.expr(node))

    def builtin_call(self, name, node):
        a = node.args
        kw = {k.arg: k.value for k in node.keywords}
        P = lambda x: self.py(self.expr(x))
        if name == "range":
            return E("range(%s)" % ", ".join(P(x) for x in a), "range")
        if name == "len":
            return E("len(%s)" % P(a[0]))
        if name == "int":
            return E("int_(%s)" % ", ".join(P(x) for x in a))
        if name == "float":
            return E("float_(%s)" % P(a[0]))
        if name == "abs":
            return E("abs_(%s)" % P(a[0]))
        if name == "round":
            return E("round_(%s)" % ", ".join(P(x) for x in a))
        if name == "str":
            return E("str_of(%s)" % P(a[0]))
        if name == "repr":
            return E("Py(repr(%s))" % P(a[0]))
        if name in ("min", "max"):
            key = P(kw["key"]) if "key" in kw else "None"
            dflt = P(kw["default"]) if "default" in kw else "MISSING_ARG"
            if len(a) == 2 and "key" not in kw and not any(isinstance(x, ast.Starred) for x in a):
                if self.impure(a[0]) and self.impure(a[1]):
                    x, y = self.fresh(), self.fresh()
                    return E("[&] { Py %s = %s; Py %s = %s; return %s2(%s, %s); }()" % (x, P(a[0]), y, P(a[1]), name, x, y))
                return E("%s2(%s, %s)" % (name, P(a[0]), P(a[1])))
            if len(a) == 1:
                return E("%s_(%s, %s, %s)" % (name, self.items_vec(a[0]), key, dflt))
            items, built = self.seq_items(a)
            return E("%s_(Vec%s, %s, %s)" % (name, items, key, dflt) if not built else
                     "%s_(L_(list(%s))->v, %s, %s)" % (name, items, key, dflt))
        if name == "sum":
            start = P(a[1]) if len(a) > 1 else ("Py(0)" if "start" not in kw else P(kw["start"]))
            return E("sum_(%s, %s)" % (self.items_vec(a[0]), start))
        if name in ("any", "all"):
            if isinstance(a[0], ast.GeneratorExp):
                return E(self.lazy_anyall(a[0], name == "any"), "bool")
            return E("truthy(%s_(%s))" % (name, self.items_vec(a[0])), "bool")
        if name == "next":
            g = a[0]
            if not isinstance(g, ast.GeneratorExp):
                raise NotImplementedError("next() of a non-generator (line %d)" % node.lineno)
            dflt = P(a[1]) if len(a) > 1 else None
            return E(self.lazy_next(g, dflt))
        if name == "enumerate":
            start = P(a[1]) if len(a) > 1 else (P(kw["start"]) if "start" in kw else "Py(0)")
            return E("enumerate_(%s, %s)" % (self.seq_arg(a[0]), start))
        if name == "zip":
            return E("zip_({%s})" % ", ".join(self.seq_arg(x) for x in a))
        if name == "sorted":
            return E("sorted(%s, %s, %s)" % (self.seq_arg(a[0]), P(kw["key"]) if "key" in kw else "None",
                                             P(kw["reverse"]) if "reverse" in kw else "False"))
        if name == "reversed":
            return E("reversed_(%s)" % self.seq_arg(a[0]))
        if name == "list":
            if not a:
                return E("list()")
            if isinstance(a[0], ast.GeneratorExp):
                return E(self.comp_code(a[0], "list"))
            return E("list_(%s)" % P(a[0]))
        if name == "tuple":
            if not a:
                return E("tuple()")
            if isinstance(a[0], ast.GeneratorExp):
                return E("tuple_(%s)" % self.comp_code(a[0], "list"))
            return E("tuple_(%s)" % P(a[0]))
        if name == "set":
            if not a:
                return E("set_()")
            return E("set_of(%s)" % self.seq_arg(a[0]))
        if name == "dict":
            if not a:
                if not node.keywords:
                    return E("dict()")
                return E("dict({%s})" % ", ".join("{Py(%s), %s}" % (cstr(k.arg), P(k.value)) for k in node.keywords))
            base = a[0]
            if isinstance(base, ast.GeneratorExp):
                d = "dict_of_pairs(%s)" % self.comp_code(base, "list")
            elif node.keywords:
                d = "dict_copy(%s)" % P(base)
            else:
                d = "dict_of_pairs(%s)" % P(base)
            if not node.keywords:
                return E(d)
            t = self.fresh("d")
            sets = " ".join("setitem(%s, Py(%s), %s);" % (t, cstr(k.arg), P(k.value)) for k in node.keywords)
            return E("[&] { Py %s = %s; %s return %s; }()" % (t, d, sets, t))
        if name == "callable":
            return E("callable(%s)" % P(a[0]), "bool")
        if name == "isinstance":
            kinds = a[1].elts if isinstance(a[1], ast.Tuple) else [a[1]]
            k = {"tuple": "TUPLE", "list": "LIST", "int": "INT", "float": "FLOAT", "str": "STR", "dict": "DICT"}
            x = P(a[0])
            return E(" || ".join("isinstance_(%s, %s)" % (x, k[t.id]) for t in kinds), "bool")
        if name == "print":
            return E("Py((print_(Vec{%s}), 0))" % ", ".join(P(x) for x in a))
        if name == "Spots":
            return E("Spots(%s)" % ", ".join(P(x) for x in a))
        raise NotImplementedError("builtin %s (line %d)" % (name, node.lineno))

    def seq_arg(self, node):
        if isinstance(node, ast.GeneratorExp):
            return self.comp_code(node, "list")
        e = self.expr(node)
        return self.py(e)

    # -- comprehensions ---------------------------------------------------------------
    def comp_loops(self, node, body_lines, scope):
        """The nested loops of a comprehension around ``body_lines``."""
        code = []
        depth = 0
        for i, g in enumerate(node.generators):
            v = self.fresh("x")
            it = self.iter_code(g.iter)
            code.append("for (Py %s : %s) {" % (v, it))
            code.extend(self.assign_target_lines(g.target, v))
            for c in g.ifs:
                code.append("if (!(%s)) continue;" % self.truth(c))
            depth += 1
        code.extend(body_lines)
        code.extend(["}"] * depth)
        return code

    def iter_code(self, node):
        """What a C++ range-for walks: range(...) itself, or each(seq)."""
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "range" and \
                self.where.get(id(node.func)) is None:
            return "range(%s)" % ", ".join(self.py(self.expr(x)) for x in node.args)
        return "each(%s)" % self.py(self.expr(node))

    def iter_type(self, code):
        return "Range" if code.startswith("range(") else "Each"

    def comp_locals(self, scope):
        decls = []
        for n in sorted(scope.bound):
            if n in scope.cells:
                decls.append("auto %s__c = std::make_shared<Py>();" % cname(n))
            else:
                decls.append("Py %s;" % cname(n))
        return decls

    def comp_code(self, node, kind):
        """A comprehension as a lambda run on the spot, building a list, set or dict."""
        scope = self.scopes[id(node)]
        # the first iterable is evaluated outside, before the comprehension's own scope
        first_it = node.generators[0].iter
        first = self.fresh("it")
        first_code = self.iter_code(first_it)
        self.scope_stack.append(scope)
        r = self.fresh("r")
        if kind == "dict":
            body = ["setitem(%s, %s, %s);" % (r, self.py(self.expr(node.key)), self.py(self.expr(node.value)))]
            init = "Py %s = dict();" % r
        elif kind == "set":
            body = ["S_(%s)->d.set(%s, None);" % (r, self.py(self.expr(node.elt)))]
            init = "Py %s = set_();" % r
        else:
            body = ["L_(%s)->v.push_back(%s);" % (r, self.py(self.expr(node.elt)))]
            init = "Py %s = list();" % r
        loops = self.comp_loops_first(node, body, first)
        self.scope_stack.pop()
        decls = self.comp_locals(scope)
        return "[&](%s %s) { %s %s %s return %s; }(%s)" % (self.iter_type(first_code), first, " ".join(decls), init,
                                                           " ".join(loops), r, first_code)

    def comp_loops_first(self, node, body_lines, first):
        code = []
        depth = 0
        for i, g in enumerate(node.generators):
            v = self.fresh("x")
            it = first if i == 0 else self.iter_code(g.iter)
            code.append("for (Py %s : %s) {" % (v, it))
            code.extend(self.assign_target_lines(g.target, v))
            for c in g.ifs:
                code.append("if (!(%s)) continue;" % self.truth(c))
            depth += 1
        code.extend(body_lines)
        code.extend(["}"] * depth)
        return code

    def lazy_anyall(self, g, is_any):
        scope = self.scopes[id(g)]
        first = self.fresh("it")
        first_code = self.iter_code(g.generators[0].iter)
        self.scope_stack.append(scope)
        test = self.truth(g.elt)
        body = ["if (%s(%s)) return %s;" % ("" if is_any else "!", test, "true" if is_any else "false")]
        loops = self.comp_loops_first(g, body, first)
        self.scope_stack.pop()
        decls = self.comp_locals(scope)
        return "[&](%s %s) -> bool { %s %s return %s; }(%s)" % (self.iter_type(first_code), first, " ".join(decls),
                                                               " ".join(loops), "false" if is_any else "true", first_code)

    def lazy_next(self, g, dflt):
        scope = self.scopes[id(g)]
        first = self.fresh("it")
        first_code = self.iter_code(g.generators[0].iter)
        self.scope_stack.append(scope)
        body = ["return %s;" % self.py(self.expr(g.elt))]
        loops = self.comp_loops_first(g, body, first)
        self.scope_stack.pop()
        decls = self.comp_locals(scope)
        end = "return %s;" % dflt if dflt is not None else 'raise("StopIteration", "");'
        return "[&](%s %s) -> Py { %s %s %s }(%s)" % (self.iter_type(first_code), first, " ".join(decls),
                                                     " ".join(loops), end, first_code)

    def x_ListComp(self, node):
        return E(self.comp_code(node, "list"))

    def x_SetComp(self, node):
        return E(self.comp_code(node, "set"))

    def x_DictComp(self, node):
        return E(self.comp_code(node, "dict"))

    def x_GeneratorExp(self, node):
        return E(self.comp_code(node, "list"))         # (run at once: what consumes it walks it in order)

    # -- lambdas and nested functions: closures -------------------------------------------
    def closure(self, node, name, body_fn):
        """func(sig(...), [captures](Vec& p) -> Py { ... }) for a lambda or a nested def."""
        scope = self.scopes[id(node)]
        a = node.args
        params = [x.arg for x in a.args]
        defaults = a.defaults
        dcode = ["MISSING_ARG"] * (len(params) - len(defaults)) + [self.py(self.expr(d)) for d in defaults]
        allnames = params + ([a.vararg.arg] if a.vararg else []) + ([a.kwarg.arg] if a.kwarg else [])
        caps = sorted(scope.frees)
        cap = ", ".join("%s__c" % cname(c) for c in caps)
        self.scope_stack.append(scope)
        self.func_stack.append(scope)
        lines = []
        for i, p in enumerate(allnames):
            if p in scope.cells:
                lines.append("auto %s__c = std::make_shared<Py>(_A_[%d]);" % (cname(p), i))
            else:
                lines.append("Py %s = _A_[%d];" % (cname(p), i))
        for n in sorted(scope.bound - set(allnames)):
            if n in scope.cells:
                lines.append("auto %s__c = std::make_shared<Py>();" % cname(n))
            else:
                lines.append("Py %s;" % cname(n))
        lines.extend(body_fn())
        self.func_stack.pop()
        self.scope_stack.pop()
        nreq = len(params) - len(defaults)
        sig = 'sig(%s, {%s}, {%s}, %d%s)' % (cstr(name), ", ".join(cstr(x) for x in allnames), ", ".join(dcode), nreq,
                                             (", %s, %s" % ("true" if a.vararg else "false", "true" if a.kwarg else "false"))
                                             if (a.vararg or a.kwarg) else "")
        return sig, cap, lines

    def x_Lambda(self, node):
        holder = []

        def body():
            return ["return %s;" % self.py(self.expr(node.body))]
        sig, cap, lines = self.closure(node, "lambda", body)
        return E("func(%s, [%s](Vec& _A_) -> Py { %s })" % (sig, cap, " ".join(lines)))

    # -- statements ------------------------------------------------------------------
    def assign_target_lines(self, t, value):
        """Assigning the C++ expression ``value`` (a name, evaluated once) to a Python target."""
        if isinstance(t, ast.Name):
            return ["%s = %s;" % (self.store_name(t.id), value)]
        if isinstance(t, (ast.Tuple, ast.List)):
            starred = [i for i, e in enumerate(t.elts) if isinstance(e, ast.Starred)]
            u = self.fresh("u")
            if starred:
                i = starred[0]
                lines = ["Vec %s = unpack_star(%s, %d, %d);" % (u, value, i, len(t.elts) - i - 1)]
            else:
                lines = ["Vec %s = unpack(%s, %d);" % (u, value, len(t.elts))]
            for i, e in enumerate(t.elts):
                if isinstance(e, ast.Starred):
                    e = e.value
                lines.extend(self.assign_target_lines(e, "%s[%d]" % (u, i)))
            return lines
        if isinstance(t, ast.Subscript):
            obj = self.py(self.expr(t.value))
            if isinstance(t.slice, ast.Slice):
                s = t.slice
                parts = [self.py(self.expr(x)) if x is not None else "None" for x in (s.lower, s.upper, s.step)]
                return ["slice_assign(%s, %s, %s, %s, %s);" % (obj, parts[0], parts[1], parts[2], value)]
            if isinstance(t.slice, ast.Tuple):
                key = self.py(self.x_Tuple(t.slice))
            else:
                key = self.py(self.expr(t.slice))
            return ["setitem(%s, %s, %s);" % (obj, key, value)]
        if isinstance(t, ast.Attribute):
            obj = self.py(self.expr(t.value))
            if t.attr in ("V", "F", "C", "UV"):
                return ["mesh_%s(%s) = %s;" % (t.attr, obj, value)]
            if t.attr == "cells":
                return ["inst_set(%s, %s, %s);" % (obj, cstr(t.attr), value)]
            raise NotImplementedError("assigning .%s (line %d)" % (t.attr, t.lineno))
        raise NotImplementedError("target %s" % type(t).__name__)

    def stmt_Assign(self, node, ind, out):
        v = self.expr(node.value)
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            out.append(ind + "%s = %s;" % (self.store_name(node.targets[0].id), self.py(v)))
            return
        t = self.fresh()
        lines = ["Py %s = %s;" % (t, self.py(v))]
        for tg in node.targets:
            lines.extend(self.assign_target_lines(tg, t))
        out.append(ind + "{ " + " ".join(lines) + " }")

    def stmt_AugAssign(self, node, ind, out):
        op = type(node.op)
        t = node.target
        val = self.py(self.expr(node.value))
        if op in CPP_OP and not self.is_atom(val):
            val = "(" + val + ")"                       # (x -= a + b is x = x - (a + b))
        if isinstance(t, ast.Name):
            lv = self.store_name(t.id)
            if op is ast.Add:
                out.append(ind + "iadd(%s, %s);" % (lv, val))
            else:
                out.append(ind + "%s = %s;" % (lv, self.binop(op, lv, val)))
            return
        if isinstance(t, ast.Subscript):
            o, k, cur = self.fresh("o"), self.fresh("k"), self.fresh("c")
            obj = self.py(self.expr(t.value))
            key = self.py(self.expr(t.slice))
            if op is ast.Add:
                upd = "iadd(%s, %s);" % (cur, val)
            else:
                upd = "%s = %s;" % (cur, self.binop(op, cur, val))
            out.append(ind + "{ Py %s = %s; Py %s = %s; Py %s = getitem(%s, %s); %s setitem(%s, %s, %s); }" %
                       (o, obj, k, key, cur, o, k, upd, o, k, cur))
            return
        raise NotImplementedError("augmented assignment to %s" % type(t).__name__)

    def stmt_Expr(self, node, ind, out):
        v = node.value
        if isinstance(v, ast.Constant) and isinstance(v.value, str):
            for line in v.value.strip().split("\n"):            # a docstring: a comment
                out.append(ind + "// " + line.strip() if line.strip() else ind + "//")
            return
        e = self.expr(v)
        out.append(ind + e.code + ";")

    def stmt_If(self, node, ind, out):
        out.append(ind + "if (%s) {" % self.truth(node.test) + self.trailing(node, node.test))
        self.block(node.body, ind + "    ", out)
        orelse = node.orelse
        while len(orelse) == 1 and isinstance(orelse[0], ast.If):
            n2 = orelse[0]
            self.leading_comments(n2, ind, out)
            out.append(ind + "} else if (%s) {" % self.truth(n2.test) + self.trailing(n2, n2.test))
            self.block(n2.body, ind + "    ", out)
            orelse = n2.orelse
        if orelse:
            out.append(ind + "} else {")
            self.block(orelse, ind + "    ", out)
        out.append(ind + "}")

    def trailing(self, node, header_end):
        texts = self.comment_for(node, getattr(header_end, "end_lineno", node.lineno))
        return ("  // " + " ".join(texts)) if texts else ""

    def stmt_While(self, node, ind, out):
        if node.orelse:
            raise NotImplementedError("while-else")
        out.append(ind + "while (%s) {" % self.truth(node.test) + self.trailing(node, node.test))
        self.block(node.body, ind + "    ", out)
        out.append(ind + "}")

    def stmt_For(self, node, ind, out):
        v = self.fresh("v")
        it = self.iter_code(node.iter)
        flag = None
        if node.orelse:
            flag = self.fresh("broke")
            out.append(ind + "bool %s = false;" % flag)
            self.break_flags.append(flag)
        else:
            self.break_flags.append(None)
        out.append(ind + "for (Py %s : %s) {" % (v, it) + self.trailing(node, node.iter))
        for line in self.assign_target_lines(node.target, v):
            out.append(ind + "    " + line)
        self.block(node.body, ind + "    ", out)
        out.append(ind + "}")
        self.break_flags.pop()
        if flag:
            out.append(ind + "if (!%s) {" % flag)
            self.block(node.orelse, ind + "    ", out)
            out.append(ind + "}")

    def stmt_Break(self, node, ind, out):
        if self.break_flags and self.break_flags[-1]:
            out.append(ind + "{ %s = true; break; }" % self.break_flags[-1])
        else:
            out.append(ind + "break;")

    def stmt_Continue(self, node, ind, out):
        out.append(ind + "continue;")

    def stmt_Pass(self, node, ind, out):
        out.append(ind + ";")

    def stmt_Return(self, node, ind, out):
        if node.value is None:
            out.append(ind + "return None;")
        else:
            out.append(ind + "return %s;" % self.py(self.expr(node.value)))

    def stmt_Assert(self, node, ind, out):
        msg = self.py(self.expr(node.msg)) if node.msg is not None else 'Py("")'
        src = ast.get_source_segment(self.src, node.test) or "assert"
        out.append(ind + "if (!(%s)) raise(\"AssertionError\", str(%s) + \" [%s]\");" %
                   (self.truth(node.test), msg, cstr(src)[1:-1][:120]))

    def stmt_Raise(self, node, ind, out):
        exc = node.exc
        if isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name):
            arg = self.py(self.expr(exc.args[0])) if exc.args else 'Py("")'
            out.append(ind + "raise(%s, str(%s));" % (cstr(exc.func.id), arg))
            return
        raise NotImplementedError("raise")

    def stmt_Import(self, node, ind, out):
        pass

    def stmt_FunctionDef(self, node, ind, out):
        scope = self.scope()
        if scope.kind == "module":
            if node.name in self.static_funcs:
                self.module_func(node, cname(node.name))
                out.append(ind + "F_%s = %s;" % (node.name, self.func_value(node, cname(node.name))))
            else:
                cn = self.dyn_defs[id(node)]
                self.module_func(node, cn)
                out.append(ind + "%s = %s;" % (cname(node.name), self.func_value(node, cn)))
            return
        # a def inside a function: a closure, bound to its name

        def body():
            lines = []
            self.block(node.body, "", lines)
            if not lines or not lines[-1].strip().startswith("return"):
                lines.append("return None;")
            return lines
        sig, cap, lines = self.closure(node, node.name, body)
        target = self.store_name(node.name)
        out.append(ind + "%s = func(%s, [%s](Vec& _A_) -> Py {" % (target, sig, cap))
        for l in lines:
            out.append(ind + "    " + l)
        out.append(ind + "});")

    def stmt_ClassDef(self, node, ind, out):
        if node.name != "Spots":
            raise NotImplementedError("class %s" % node.name)
        # (written by hand in the runtime: see Spots in castle_rt.hpp)

    def block(self, stmts, ind, out):
        for st in stmts:
            self.leading_comments(st, ind, out)
            m = getattr(self, "stmt_" + type(st).__name__, None)
            if m is None:
                raise NotImplementedError("%s at line %d" % (type(st).__name__, st.lineno))
            before = len(out)
            m(st, ind, out)
            if not isinstance(st, (ast.If, ast.For, ast.While, ast.FunctionDef, ast.ClassDef)) and len(out) > before:
                texts = self.comment_for(st)
                if texts:
                    out[before] = out[before] + "  // " + " ".join(texts)

    # -- module-level functions ----------------------------------------------------------
    def default_name(self, fname, pname):
        return "D_%s__%s" % (fname, pname)

    def is_const(self, node):
        if isinstance(node, ast.Constant):
            return True
        if isinstance(node, ast.UnaryOp) and isinstance(node.operand, ast.Constant):
            return True
        if isinstance(node, ast.Tuple):
            return all(self.is_const(e) for e in node.elts)
        return False

    def module_func(self, node, cn=None):
        name = node.name
        cn = cn or ("f_" + name)
        scope = self.scopes[id(node)]
        a = node.args
        params = [x.arg for x in a.args]
        allp = params + ([a.vararg.arg] if a.vararg else []) + ([a.kwarg.arg] if a.kwarg else [])
        nd = len(a.defaults)
        defaults = {params[len(params) - nd + i]: d for i, d in enumerate(a.defaults)}
        decl_params = []
        for p in allp:
            decl_params.append("Py %s" % (cname(p) + ("__p" if p in scope.cells else "")))
        sig_decl = "Py %s(%s)" % (cn, ", ".join(decl_params))
        defaults_decl = ", ".join("Py %s%s" % (cname(p) + ("__p" if p in scope.cells else ""),
                                               " = MISSING_ARG" if (p in defaults or p in (a.vararg.arg if a.vararg else "",
                                                                                            a.kwarg.arg if a.kwarg else ""))
                                               else "") for p in allp)
        self.forward.append("Py %s(%s);" % (cn, defaults_decl))
        self.scope_stack.append(scope)
        self.func_stack.append(scope)
        lines = []
        doc = ast.get_docstring(node)
        head = []
        if doc:
            for line in doc.split("\n"):
                head.append("// " + line if line.strip() else "//")
        # defaults
        for p in allp:
            v = cname(p) + ("__p" if p in scope.cells else "")
            if p in defaults:
                d = defaults[p]
                if self.is_const(d):
                    dc = self.py(self.expr(d))
                else:
                    gname = self.default_name(cn, p)
                    self.default_globals.append(gname)
                    self.pending_defaults.append((gname, d))
                    dc = gname
                lines.append("if (%s.missing()) %s = %s;" % (v, v, dc))
            elif a.vararg and p == a.vararg.arg:
                lines.append("if (%s.missing()) %s = tuple();" % (v, v))
            elif a.kwarg and p == a.kwarg.arg:
                lines.append("if (%s.missing()) %s = dict();" % (v, v))
            if p in scope.cells:
                lines.append("auto %s__c = std::make_shared<Py>(%s);" % (cname(p), v))
        for n in sorted(scope.bound - set(allp)):
            if n in scope.cells:
                lines.append("auto %s__c = std::make_shared<Py>();" % cname(n))
            else:
                lines.append("Py %s;" % cname(n))
        body = node.body
        if doc:
            body = body[1:]
        self.block(body, "    ", lines)
        if not body or not isinstance(body[-1], ast.Return):
            lines.append("return None;")
        self.func_stack.pop()
        self.scope_stack.pop()
        first_line = "    " if False else ""
        text = head + [sig_decl + " {" + self.trailing(node, node.args)]
        text += [("    " + l if not l.startswith("    ") else l) for l in lines]
        text.append("}")
        self.out.append("\n".join(text))
        # the defaults are evaluated where the def is, in module order
        self.flush_defaults_at_def = True

    def func_value(self, node, cn):
        """The function as a value (to pass to add.make, to store): binding by name at run time."""
        a = node.args
        params = [x.arg for x in a.args]
        allp = params + ([a.vararg.arg] if a.vararg else []) + ([a.kwarg.arg] if a.kwarg else [])
        nd = len(a.defaults)
        dcode = ["MISSING_ARG"] * (len(params) - nd)
        for d in a.defaults:
            dcode.append("MISSING_ARG")                 # (the function fills in its own defaults)
        # a bound parameter left MISSING means: use the default -- the C++ function does that itself
        call = "%s(%s)" % (cn, ", ".join("_A_[%d]" % i for i in range(len(allp))))
        sig = 'sig(%s, {%s}, {}, %d%s)' % (cstr(node.name), ", ".join(cstr(x) for x in allp), len(params) - nd,
                                           (", %s, %s" % ("true" if a.vararg else "false", "true" if a.kwarg else "false"))
                                           if (a.vararg or a.kwarg) else "")
        return "func(%s, [](Vec& _A_) -> Py { return %s; })" % (sig, call)

    # -- the whole module ----------------------------------------------------------------
    def translate(self):
        self.forward = []
        self.default_globals = []
        self.pending_defaults = []
        self.break_flags = []
        self.compute_purity()
        main = []
        for st in self.tree.body:
            self.leading_comments(st, "    ", main)
            if isinstance(st, ast.FunctionDef):
                self.stmt_FunctionDef(st, "    ", main)
                for g, d in self.pending_defaults:
                    main.append("    %s = %s;" % (g, self.py(self.expr(d))))
                self.pending_defaults = []
                continue
            m = getattr(self, "stmt_" + type(st).__name__)
            before = len(main)
            m(st, "    ", main)
            if not isinstance(st, (ast.If, ast.For, ast.While, ast.ClassDef)) and len(main) > before:
                texts = self.comment_for(st)
                if texts:
                    main[before] = main[before] + "  // " + " ".join(texts)
        return main

    def compute_purity(self):
        """The module's functions that draw nothing, change nothing and draw no random numbers:
        two calls of them may run in either order."""
        impure_prims = True
        calls = {}
        bad = set()
        for name, f in self.static_funcs.items():
            cs = set()
            for n in ast.walk(f):
                if isinstance(n, ast.Call):
                    fn = n.func
                    if isinstance(fn, ast.Name):
                        if fn.id in self.static_funcs:
                            cs.add(fn.id)
                        elif fn.id in PURE_BUILTINS:
                            pass
                        else:
                            bad.add(name)
                    elif isinstance(fn, ast.Attribute):
                        if isinstance(fn.value, ast.Name) and fn.value.id == "add":
                            if fn.attr not in PURE_ADD:
                                bad.add(name)
                        elif fn.attr in ("get", "items", "keys", "values", "index", "count", "copy", "join", "startswith"):
                            pass
                        else:
                            bad.add(name)
                    else:
                        bad.add(name)
                if isinstance(n, (ast.Assign, ast.AugAssign)):
                    for t in (n.targets if isinstance(n, ast.Assign) else [n.target]):
                        if isinstance(t, (ast.Subscript, ast.Attribute)):
                            bad.add(name)
                if isinstance(n, (ast.Lambda,)) or (isinstance(n, ast.FunctionDef) and n is not f):
                    bad.add(name)
            calls[name] = cs
        changed = True
        while changed:
            changed = False
            for name, cs in calls.items():
                if name not in bad and any(c in bad or c not in calls for c in cs):
                    bad.add(name)
                    changed = True
        self.pure_funcs = set(calls) - bad


BANNER = """\
// ============================================================================
//  46_castle.cpp -- the castle of 46_castle.py, in C++ (with add.hpp)
// ============================================================================
//
//  The same island, castle and people as 46_castle.py, made by the same
//  program: this file is 46_castle.py translated statement by statement by
//  tools/py2cpp/py2cpp.py (do not edit it: edit the Python and translate
//  again) onto a small runtime -- the first part of this file -- that keeps
//  Python's rules for its values: 7 // 2 is 3 and -7 // 2 is -4, a dict
//  keeps the order its keys came in, sorted() is stable, the floats are
//  IEEE doubles computed in the same order and printed the same way.  So
//  castle.off, castle.obj and castle.mtl come out byte for byte the same as
//  from ``python3 46_castle.py``.  The comments are the Python's.
//
//  Build -- add.hpp next to this file, a 64-bit C++17 compiler:
//
//      g++ -std=c++17 -O1 -fno-exceptions 46_castle.cpp -o castle
//      ./castle                    -> castle.off + castle.obj + castle.mtl
//
//  (clang++ the same.)  The file is big -- the castle is %s lines of
//  Python -- and the compiler needs about 5 GB of memory and 6 minutes for
//  it at -O1 (at -O0 3 GB and 2 minutes, but the castle then runs 5 times
//  slower); -fno-exceptions keeps it there: nothing here throws -- an error
//  stops the program with a message, as Python's would.  The castle takes
//  7 minutes and 1.3 GB of memory (Python: 36 minutes and 1.9 GB) and
//  writes the same three files.  CASTLE_DENSITY=0.1 in the environment
//  makes the quick run, as in Python.
// ============================================================================
"""

def runtime_source():
    """pyrt.hpp, addbind.hpp and castle_rt.hpp, one after the other, ready to go into the .cpp."""
    out = []
    for name, drop in (("pyrt.hpp", ["#pragma once", '#include "add.hpp"']),
                       ("addbind.hpp", ["#pragma once", '#include "pyrt.hpp"']),
                       ("castle_rt.hpp", ["#pragma once", '#include "addbind.hpp"'])):
        text = open(os.path.join(HERE, name), encoding="utf-8").read()
        for line in drop:
            assert line + "\n" in text, (name, line)
            text = text.replace(line + "\n", "", 1)
        out.append(text)
    return "".join(out)


def translate(src_path):
    """The whole of 46_castle.cpp for the Python in ``src_path``, as a string."""
    load_add_sigs()
    CPP_RESERVED.update(runtime_names([os.path.join(HERE, f) for f in ("pyrt.hpp", "addbind.hpp", "castle_rt.hpp")]))
    src = open(src_path, encoding="utf-8").read()
    t = Translator(src, src_path)
    main_lines = t.translate()
    head = open(os.path.join(HERE, "head.hpp"), encoding="utf-8").read()
    head = head.split("\n", 1)[1]                                    # (its first line: the banner's)
    inc = '#include "castle_rt.hpp"\n'
    assert head.endswith(inc), "head.hpp should end by including the runtime"
    lines = "{:,}".format(round(src.count("\n"), -2)).replace(",", " ")
    f = io.StringIO()
    f.write(BANNER % lines)
    f.write(head[:-len(inc)])
    f.write(runtime_source())
    f.write("\n// ---------------------------------------------------------------------------\n")
    f.write("//  the castle's module-level names\n")
    f.write("// ---------------------------------------------------------------------------\n")
    f.write("namespace castle {\nusing namespace py;\n\n")
    for g in sorted(t.globals):
        f.write("Py %s;\n" % cname(g))
    for name in sorted(t.static_funcs):
        f.write("Py F_%s;\n" % name)
    for g in t.default_globals:
        f.write("Py %s;\n" % g)
    f.write("\n")
    for d in t.forward:
        f.write(d + "\n")
    f.write("\n")
    for fn in t.out:
        f.write(fn + "\n\n")
    # the module's statements, in parts (one huge function is more than a compiler wants to hold at once)
    parts, cur, depth = [], [], 0
    for line in main_lines:
        cur.append(line)
        depth += line.count("{") - line.count("}")
        if depth == 0 and len(cur) >= 60 and not line.lstrip().startswith("//"):
            parts.append(cur)
            cur = []
    if cur:
        parts.append(cur)
    for i, part in enumerate(parts):
        f.write("void part_%d() {\n" % (i + 1))
        f.write("\n".join(part))
        f.write("\n}\n\n")
    f.write("void castle_main() {\n")
    for i in range(len(parts)):
        f.write("    part_%d();\n" % (i + 1))
    f.write("}\n\n}  // namespace castle\n\n")
    f.write("int main() {\n    castle::castle_main();\n    return 0;\n}\n")
    return f.getvalue()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    src = args[0] if args else os.path.join(ROOT, "examples", "46_castle.py")
    out = args[1] if len(args) > 1 else os.path.join(ROOT, "examples", "46_castle.cpp")
    code = translate(src)
    if "--check" in sys.argv:
        old = open(out, encoding="utf-8").read() if os.path.exists(out) else ""
        if old != code:
            print("%s is not %s translated: run python3 tools/py2cpp/py2cpp.py" % (os.path.basename(out), os.path.basename(src)))
            return 1
        print("%s is %s translated" % (os.path.basename(out), os.path.basename(src)))
        return 0
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(code)
    print("%s: %d lines, %.1f MB" % (out, code.count("\n"), len(code.encode("utf-8")) / 1e6))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
coverage.py -- which example uses which add.py function?

    python3 tools/coverage.py            table of every public name and its examples
    python3 tools/coverage.py --unused   only the names no example uses
    python3 tools/coverage.py --strict   exit 1 if a public function is unused (CI)

The examples are read with ``ast``; every ``add.<name>`` attribute counts as a
use.  Names that are aliases of the same function (``ball`` / ``sphere``)
count as used when any of them is.  ``make_docs.py`` calls :func:`usage` to
print "used in ..." links under every entry of the reference.
"""
import ast
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EXAMPLES = os.path.join(ROOT, "examples")
sys.path.insert(0, ROOT)
import add                                                   # noqa: E402

#: Values (not functions) and classes -- reached through ``layer`` /
#: ``stream`` -- that an example does not have to name itself.
OPTIONAL = {"EPS", "BOOL_EPS", "DEFAULT_COLOR", "vertices", "faces", "Mesh", "Stream"}


def example_files():
    return sorted(n for n in os.listdir(EXAMPLES)
                  if n.endswith(".py") and n[0].isdigit())


def names_used(path):
    """Set of ``add.<name>`` attribute names used in one script."""
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), path)
    used = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
                and node.value.id == "add"):
            used.add(node.attr)
    return used


def usage():
    """``{public name: [example file, ...]}`` for every name in ``add.__all__``."""
    table = {name: [] for name in add.__all__}
    for script in example_files():
        for name in names_used(os.path.join(EXAMPLES, script)):
            if name in table:
                table[name].append(script)
    # an alias counts as used whenever the function it names is used
    by_object = {}
    for name in add.__all__:
        by_object.setdefault(id(getattr(add, name)), []).append(name)
    for names in by_object.values():
        if len(names) > 1:
            merged = sorted(set(s for n in names for s in table[n]))
            for n in names:
                table[n] = merged
    return table


def main(argv):
    table = usage()
    unused = [n for n, files in table.items() if not files]
    if "--unused" in argv or "--strict" in argv:
        must = [n for n in unused if n not in OPTIONAL and callable(getattr(add, n))]
        extra = [n for n in unused if n not in must]
        if must:
            print("public functions no example uses (%d):" % len(must))
            for n in must:
                print("   ", n)
        else:
            print("every public function is used by at least one example")
        if extra:
            print("values no example uses:", ", ".join(extra))
        return 1 if ("--strict" in argv and must) else 0
    width = max(len(n) for n in table)
    for name in add.__all__:
        files = table[name]
        print("%-*s  %s" % (width, name, ", ".join(f[:-3] for f in files) or "--"))
    print("\n%d public names, %d used by an example, %d unused"
          % (len(table), len(table) - len(unused), len(unused)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

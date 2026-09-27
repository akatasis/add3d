#!/usr/bin/env python3
"""Concatenate _src/*.py into the single-file module add.py, and _cpp/*.hpp
into the single-file C++ header add.hpp.

add.py and add.hpp are delivered as one file each on purpose: a student
downloads one, drops it next to their model and it works.  The sources are
kept in sections so that they stay readable while being written.

Every C++ section but the first (the core) has two parts, its declarations
and, after a line ``//@@definitions``, its definitions: add.hpp gets all the
declarations first and then all the definitions, so that any function may
call any other, as in Python.

    python3 build.py              build add.py and add.hpp (and the copies)
    python3 build.py --check      exit 1 if either is out of date (CI)
    python3 build.py --cpp-dev OUT.hpp 10,20
                                  a header with the core, every section's
                                  declarations and only the definitions of
                                  sections 10 and 20 (for working on them)
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "_src")
OUT = os.path.join(HERE, "add.py")
CPP_SRC = os.path.join(HERE, "_cpp")
CPP_OUT = os.path.join(HERE, "add.hpp")
MARK = "//@@definitions"

#: Places that keep an identical copy of add.py, so that the example models
#: can say plain ``import add`` exactly the way a student's model does.
COPIES = [os.path.join(HERE, "examples", "add.py")]


def cpp_text(only=None):
    """The text of add.hpp: the core, then every section's declarations,
    then the definitions (with ``only``: just those of these sections)."""
    parts = sorted(n for n in os.listdir(CPP_SRC) if n.endswith(".hpp"))
    core, decls, defs = [], [], []
    for name in parts:
        with open(os.path.join(CPP_SRC, name)) as f:
            text = f.read().rstrip("\n")
        if MARK not in text:
            core.append(text)
            continue
        head, tail = text.split(MARK, 1)
        decls.append(head.rstrip("\n"))
        if only is None or name[:2] in only:
            defs.append(tail.strip("\n"))
    return "\n\n".join(core + decls + defs) + "\n\n#endif  // ADD_HPP\n"


#: Places that keep an identical copy of add.hpp (so that the C++ examples say
#: plain ``#include "add.hpp"``, as a student's model does).
CPP_COPIES = [os.path.join(HERE, "examples", "add.hpp")]


def build_cpp():
    text = cpp_text()
    for path in [CPP_OUT] + CPP_COPIES:
        with open(path, "w", newline="\n") as f:
            f.write(text)
    print("add.hpp built from %d sections, %d lines"
          % (len([n for n in os.listdir(CPP_SRC) if n.endswith(".hpp")]), text.count("\n")))


def build():
    parts = sorted(n for n in os.listdir(SRC) if n.endswith(".py"))
    text = []
    for name in parts:
        with open(os.path.join(SRC, name)) as f:
            text.append(f.read().rstrip("\n"))
    with open(OUT, "w") as f:
        f.write("\n".join(text) + "\n")
    for path in COPIES:
        shutil.copyfile(OUT, path)
    lines = sum(t.count("\n") + 1 for t in text)
    print("add.py built from %d sections, %d lines" % (len(parts), lines))
    build_cpp()


def check():
    """Exit with an error if add.py or a copy is out of date (used by CI)."""
    stale = []
    with open(OUT) as f:
        built = f.read()
    parts = sorted(n for n in os.listdir(SRC) if n.endswith(".py"))
    text = []
    for name in parts:
        with open(os.path.join(SRC, name)) as f:
            text.append(f.read().rstrip("\n"))
    if "\n".join(text) + "\n" != built:
        stale.append(OUT)
    for path in COPIES:
        if not os.path.exists(path) or open(path).read() != built:
            stale.append(path)
    for path in [CPP_OUT] + CPP_COPIES:
        if not os.path.exists(path) or open(path).read() != cpp_text():
            stale.append(path)
    if stale:
        print("out of date -- run  python3 build.py :", *stale)
        return 1
    print("add.py, add.hpp and their copies are up to date")
    return 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(check())
    if "--cpp-dev" in sys.argv:
        i = sys.argv.index("--cpp-dev")
        out = sys.argv[i + 1]
        only = set(sys.argv[i + 2].split(",")) if len(sys.argv) > i + 2 else set()
        with open(out, "w", newline="\n") as f:
            f.write(cpp_text(only))
        sys.exit(0)
    build()

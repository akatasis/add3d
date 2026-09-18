#!/usr/bin/env python3
"""Concatenate _src/*.py into the single-file module add.py.

add.py is delivered as one file on purpose: a student downloads it, drops it
next to their model script and it works.  The sources are kept in sections so
that they stay readable while being written.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "_src")
OUT = os.path.join(HERE, "add.py")

#: Places that keep an identical copy of add.py, so that the example models
#: can say plain ``import add`` exactly the way a student's model does.
COPIES = [os.path.join(HERE, "examples", "add.py")]


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
    if stale:
        print("out of date -- run  python3 build.py :", *stale)
        return 1
    print("add.py and its copies are up to date")
    return 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(check())
    build()

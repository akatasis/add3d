#!/usr/bin/env python3
"""Concatenate _src/*.py into the single-file module add.py.

add.py is delivered as one file on purpose: a student downloads it, drops it
next to their model script and it works.  The sources are kept in sections so
that they stay readable while being written.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "_src")
OUT = os.path.join(HERE, "add.py")

parts = sorted(n for n in os.listdir(SRC) if n.endswith(".py"))
text = []
for name in parts:
    with open(os.path.join(SRC, name)) as f:
        text.append(f.read().rstrip("\n"))

with open(OUT, "w") as f:
    f.write("\n".join(text) + "\n")

lines = sum(t.count("\n") + 1 for t in text)
print("add.py built from %d sections, %d lines" % (len(parts), lines))

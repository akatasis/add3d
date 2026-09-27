"""The Python half of the parity tests (see parity.hpp): every case builds a
model with add.py exactly as its C++ twin does with add.hpp and writes it to
<case>.off / <case>.txt."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import add  # noqa: E402

CASES = []
_current = [None]
_out = [None]


def case(fn):
    """Register a test case (its name is the function's name)."""
    CASES.append(fn)
    return fn


def save_case():
    """Write the scene exactly as it is (add.off) to <case>.off, and clear it."""
    add.off(_current[0] + ".off")


def save_mesh(M, tag=""):
    add.off(_current[0] + ("_" + tag if tag else "") + ".off", M)


def save_as(ext, M):
    add.save(_current[0] + "." + ext, M)


def _txt():
    if _out[0] is None:
        _out[0] = open(_current[0] + ".txt", "w", newline="\n")
    return _out[0]


def record(x):
    """Write a number, a point, a colour, a string or a list of them."""
    f = _txt()
    if isinstance(x, bool):
        f.write("%s\n" % x)
    elif isinstance(x, int):
        f.write("%d\n" % x)
    elif isinstance(x, float):
        f.write("%r\n" % x)
    elif isinstance(x, str):
        f.write(x + "\n")
    elif isinstance(x, tuple) and len(x) >= 3 and all(isinstance(c, int) for c in x[:3]):
        c = add.rgb(x)
        f.write("(%d, %d, %d" % c[:3])
        if len(c) > 3:
            f.write(", %r" % float(c[3]))
        if len(c) > 4:
            f.write(", '%s'" % c[4])
        f.write(")\n")
    elif isinstance(x, (list, tuple)) and len(x) in (2, 3) and all(isinstance(c, (int, float)) for c in x):
        f.write("[%s]\n" % ", ".join(repr(float(c)) for c in x))
    else:
        f.write("%d\n" % len(x))
        for item in x:
            record(item)


def run(argv):
    only = argv[1:]
    n = 0
    for fn in CASES:
        if only and fn.__name__ not in only:
            continue
        _current[0] = fn.__name__
        add.clear()
        add.seed(20260926)
        try:
            fn()
        except Exception as e:                    # noqa: BLE001
            sys.stderr.write("case %s: exception: %s\n" % (fn.__name__, e))
            _txt().write("EXCEPTION\n")
        if _out[0] is not None:
            _out[0].close()
            _out[0] = None
        n += 1
    print("%d cases" % n)

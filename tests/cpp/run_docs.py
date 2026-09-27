"""
Every C++ example in the documentation must compile, run and build the same
model as its Python twin.

``docs/reference.py`` holds a short Python example for every public name of
add.py, and ``docs/reference_cpp.py`` the same example written in C++ for
add.hpp.  This script puts all the C++ examples into one program (a function
each), runs every example of both languages in a folder of its own, with a
fresh scene and ``seed(0)``, writes what is left in the scene at the end to
``scene.off`` (exactly, with ``off``), and checks that the two folders hold
the same files, byte for byte -- a PNG picture: the same pixels.  What the
examples print is not compared (Python prints a list as ``[1.0, 2.0]``, C++
as it is told to).

    python3 tests/cpp/run_docs.py                 all of them
    python3 tests/cpp/run_docs.py box sweep       only these
    python3 tests/cpp/run_docs.py --header H      compile against header H
    python3 tests/cpp/run_docs.py --examples F    the examples in file F (a dict
                                                  EXAMPLES) instead of docs/reference_cpp.py
    CXX=clang++ python3 tests/cpp/run_docs.py     another compiler
"""
import io
import os
import shutil
import subprocess
import sys
import tempfile
import traceback
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "docs"))
import add                                                          # noqa: E402
import reference                                                    # noqa: E402
import reference_cpp                                                # noqa: E402

CXX = os.environ.get("CXX", "g++")


def png_pixels(path):
    """The header and the pixel rows of a PNG file (add.hpp stores the
    picture uncompressed, add.py compresses it: the same picture)."""
    import struct
    import zlib
    data = open(path, "rb").read()
    i, idat, head = 8, b"", None
    while i < len(data):
        n = struct.unpack(">I", data[i:i + 4])[0]
        tag, body = data[i + 4:i + 8], data[i + 8:i + 8 + n]
        if tag == b"IHDR":
            head = body
        elif tag == b"IDAT":
            idat += body
        i += 12 + n
    return head, zlib.decompress(idat)


EXAMPLES = reference_cpp.EXAMPLES


def program(names):
    """One C++ program with every example as a function; ``prog NAME`` runs one."""
    out = ['#include "add.hpp"', "",
           "#include <cstdio>", "#include <cstring>", "#include <iostream>", "",
           "namespace docs_example {"]
    for i, name in enumerate(names):
        body = EXAMPLES[name].rstrip("\n")
        out.append("// ---- %s" % name)
        out.append("static void ex%d() {" % i)
        out.extend(("    " + line) if line.strip() else "" for line in body.split("\n"))
        out.append("}")
    out.append("}  // namespace docs_example")
    out.append("")
    out.append("int main(int argc, char** argv) {")
    out.append("    static const struct { const char* name; void (*run)(); } table[] = {")
    for i, name in enumerate(names):
        out.append('        {"%s", docs_example::ex%d},' % (name, i))
    out.append("    };")
    out.append("    if (argc < 2) return 2;")
    out.append("    for (const auto& t : table) {")
    out.append("        if (std::strcmp(t.name, argv[1]) != 0) continue;")
    out.append("        add::clear();")
    out.append("        add::seed(0);")
    out.append("        try {")
    out.append("            t.run();")
    out.append("        } catch (const std::exception& e) {")
    out.append('            std::fprintf(stderr, "exception: %s\\n", e.what());')
    out.append("            return 1;")
    out.append("        }")
    out.append('        add::off("scene.off");')
    out.append("        return 0;")
    out.append("    }")
    out.append('    std::fprintf(stderr, "no example called %s\\n", argv[1]);')
    out.append("    return 2;")
    out.append("}")
    return "\n".join(out) + "\n"


def run_python(name, folder):
    keep = os.getcwd()
    os.chdir(folder)
    text = io.StringIO()
    try:
        add.clear()
        add.seed(0)
        with redirect_stdout(text):
            exec(compile(reference.EXAMPLES[name], "<example %s>" % name, "exec"), {"add": add})
        add.off("scene.off")
        return None, text.getvalue()
    except Exception:                                                # noqa: BLE001
        return traceback.format_exc(limit=3), text.getvalue()
    finally:
        add.clear()
        os.chdir(keep)


def files_in(folder):
    """Every file under ``folder`` (an example may write into a folder of its own)."""
    out = set()
    for base, _, files in os.walk(folder):
        for f in files:
            out.add(os.path.relpath(os.path.join(base, f), folder).replace(os.sep, "/"))
    return out


def compare(a_dir, b_dir):
    problems = []
    names = sorted(files_in(a_dir) | files_in(b_dir))
    for n in names:
        a, b = os.path.join(a_dir, n), os.path.join(b_dir, n)
        if not (os.path.exists(a) and os.path.exists(b)):
            problems.append("%s only from %s" % (n, "c++" if os.path.exists(b) else "python"))
        elif n.lower().endswith(".png"):
            if png_pixels(a) != png_pixels(b):
                problems.append(n + ": other pixels")
        else:
            da, db = open(a, "rb").read(), open(b, "rb").read()
            if da != db:
                la, lb = da.split(b"\n"), db.split(b"\n")
                where = next((i for i, (x, y) in enumerate(zip(la, lb)) if x != y), min(len(la), len(lb)))
                problems.append("%s differs at line %d: python %r / c++ %r"
                                % (n, where + 1, la[where][:80] if where < len(la) else b"",
                                   lb[where][:80] if where < len(lb) else b""))
    return problems, len(names)


def main(argv):
    header = os.path.join(ROOT, "add.hpp")
    args = list(argv[1:])
    verbose = "-v" in args
    if verbose:
        args.remove("-v")
    if "--header" in args:
        i = args.index("--header")
        header = os.path.abspath(args[i + 1])
        del args[i:i + 2]
    global EXAMPLES
    everything = list(add.__all__)
    failures = []
    if "--examples" in args:
        i = args.index("--examples")
        namespace = {}
        path = os.path.abspath(args[i + 1])
        exec(compile(open(path, encoding="utf-8").read(), path, "exec"), namespace)
        EXAMPLES = namespace["EXAMPLES"]
        del args[i:i + 2]
        everything = [n for n in everything if n in EXAMPLES]
    missing = [n for n in everything if n not in EXAMPLES]
    stale = [n for n in EXAMPLES if n not in add.__all__]
    if not args:
        if missing:
            failures.append("no C++ example for: " + ", ".join(missing))
        if stale:
            failures.append("a C++ example for a name that is not public: " + ", ".join(stale))
    names = [n for n in (args or everything) if n in EXAMPLES]
    unknown = [n for n in args if n not in EXAMPLES]
    if unknown:
        failures.append("no C++ example for: " + ", ".join(unknown))

    work = tempfile.mkdtemp(prefix="add_docs_cpp_")
    try:
        inc = os.path.join(work, "include")
        os.makedirs(inc)
        shutil.copy(header, os.path.join(inc, "add.hpp"))
        src, exe = os.path.join(work, "docs_examples.cpp"), os.path.join(work, "docs_examples.exe")
        with open(src, "w", encoding="utf-8", newline="\n") as f:
            f.write(program(names))
        flags = ["-std=c++17", "-O1", "-Wall", "-Wno-unused-variable", "-Wno-unused-but-set-variable"]
        if "clang" not in subprocess.run([CXX, "--version"], capture_output=True, text=True).stdout.lower():
            flags.append("-Wno-maybe-uninitialized")      # (GCC's false alarms about std::optional arguments)
        p = subprocess.run([CXX] + flags + ["-I", inc, src, "-o", exe], capture_output=True, text=True)
        if p.returncode:
            print(p.stderr[-6000:])
            print("the C++ examples do not compile (%s)" % CXX)
            return 1
        if p.stderr.strip():
            print(p.stderr[-4000:])
            failures.append("warnings when compiling the C++ examples")
        for name in names:
            py_dir, cpp_dir = os.path.join(work, "py", name), os.path.join(work, "cpp", name)
            os.makedirs(py_dir)
            os.makedirs(cpp_dir)
            error, py_out = run_python(name, py_dir)
            q = subprocess.run([exe, name], cwd=cpp_dir, capture_output=True, text=True)
            problems = []
            if error:
                problems.append("python: " + error.strip().split("\n")[-1])
            if q.returncode:
                problems.append("c++ exit %d: %s" % (q.returncode, q.stderr.strip()[-300:]))
            diff, count = compare(py_dir, cpp_dir)
            problems += diff
            if problems:
                failures.append("%s: %s" % (name, "; ".join(problems)))
            if verbose or problems:
                print("%-24s %s" % (name, "FAIL " + "; ".join(problems) if problems else "same (%d files)" % count))
                if verbose:
                    for line in py_out.rstrip().split("\n") if py_out.strip() else []:
                        print("    py  | " + line)
                    for line in q.stdout.rstrip().split("\n") if q.stdout.strip() else []:
                        print("    c++ | " + line)
    finally:
        shutil.rmtree(work, ignore_errors=True)
        os.chdir(ROOT)
    if failures:
        print()
        for f in failures:
            print("FAIL", f)
        return 1
    print("%d documentation examples: the C++ twin of each builds the same model, byte for byte (%s)"
          % (len(names), CXX))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

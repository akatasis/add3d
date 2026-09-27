"""Run the parity tests: the same models made with add.py (Python) and with
add.hpp (C++) must be the same files, byte for byte.

    python3 tests/cpp/run_parity.py              every cases_*.cpp / cases_*.py pair
    python3 tests/cpp/run_parity.py 20_round     only cases_20_round.*
    python3 tests/cpp/run_parity.py --header H   compile against header H instead of add.hpp

Each pair is compiled (g++ -std=c++17) and run in a folder of its own, the
Python twin in another; every file both wrote is compared.  Exit status 1
when anything differs, fails to compile or is missing on one side."""
import glob
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CXX = os.environ.get("CXX", "g++")


def first_difference(a, b):
    la, lb = a.split(b"\n"), b.split(b"\n")
    for i, (x, y) in enumerate(zip(la, lb)):
        if x != y:
            return "line %d: python %r / c++ %r" % (i + 1, x[:100], y[:100])
    return "lengths differ: %d / %d lines" % (len(la), len(lb))


def run_pair(stem, header, work):
    cpp, py = os.path.join(HERE, stem + ".cpp"), os.path.join(HERE, stem + ".py")
    out_cpp, out_py = os.path.join(work, stem, "cpp"), os.path.join(work, stem, "py")
    os.makedirs(out_cpp)
    os.makedirs(out_py)
    inc = os.path.join(work, "include")
    exe = os.path.join(work, stem + ".exe")
    p = subprocess.run([CXX, "-std=c++17", "-O1", "-I", inc, "-I", HERE, cpp, "-o", exe],
                       capture_output=True, text=True)
    if p.returncode:
        return ["compile error:\n" + p.stderr[-3000:]]
    problems = []
    p = subprocess.run([exe], cwd=out_cpp, capture_output=True, text=True)
    if p.returncode or p.stderr:
        problems.append("c++ run: %s %s" % (p.returncode, p.stderr[-1500:]))
    p = subprocess.run([sys.executable, py], cwd=out_py, capture_output=True, text=True)
    if p.returncode or p.stderr:
        problems.append("python run: %s %s" % (p.returncode, p.stderr[-1500:]))
    names = sorted(set(os.listdir(out_cpp)) | set(os.listdir(out_py)))
    same = 0
    for name in names:
        a, b = os.path.join(out_py, name), os.path.join(out_cpp, name)
        if not os.path.exists(a) or not os.path.exists(b):
            problems.append("%s: only in %s" % (name, "c++" if os.path.exists(b) else "python"))
            continue
        da, db = open(a, "rb").read(), open(b, "rb").read()
        if da != db:
            problems.append("%s differs -- %s" % (name, first_difference(da, db)))
        else:
            same += 1
    return problems, same, len(names)


def main(argv):
    header = os.path.join(ROOT, "add.hpp")
    if "--header" in argv:
        i = argv.index("--header")
        header = os.path.abspath(argv[i + 1])
        del argv[i:i + 2]
    wanted = argv[1:]
    stems = sorted(os.path.basename(p)[:-4] for p in glob.glob(os.path.join(HERE, "cases_*.cpp")))
    if wanted:
        stems = [s for s in stems if any(w in s for w in wanted)]
    work = tempfile.mkdtemp(prefix="add_parity_")
    os.makedirs(os.path.join(work, "include"))
    shutil.copyfile(header, os.path.join(work, "include", "add.hpp"))
    failed = 0
    for stem in stems:
        res = run_pair(stem, header, work)
        if isinstance(res, list):
            print("%-28s FAILED %s" % (stem, res[0]))
            failed += 1
            continue
        problems, same, total = res
        if problems:
            failed += 1
            print("%-28s %d of %d files the same" % (stem, same, total))
            for pr in problems[:40]:
                print("    " + pr)
            if len(problems) > 40:
                print("    ... and %d more" % (len(problems) - 40))
        else:
            print("%-28s ok: %d files the same" % (stem, same))
    shutil.rmtree(work, ignore_errors=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

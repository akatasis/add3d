"""
Backwards-compatibility regression test.

``tests/legacy/`` holds model scripts written for add.py 1.2 -- four course
demonstrations, three versions of a draughts board, a clock, a Sierpinski
tetrahedron that does not even import add.py, a mixed feature test, and two
models an LLM was asked to write against the 1.2 documentation.  None of them
has been edited.

The test runs every one of them against the current add.py and checks that the
mesh it produces still has exactly the same number of faces.  Vertex counts
are allowed to fall, because 2.0 welds the seams inside a primitive, and file
sizes are allowed to fall, because numbers are written more compactly.  The
one deliberate change is ``sphere``, which is now geodesic (triangles) --
the expected count of the model that uses it is adjusted below.

    python3 tests/test_legacy.py
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LEGACY = os.path.join(HERE, "legacy")
sys.path.insert(0, ROOT)

#: script -> {output file: expected face count, as produced by add.py 1.2b}
EXPECTED = {
    "modelis1.py": {"modelis1.off": None},        # contains axes(): see below
    "modelis2.py": {"modelis2.off": 111000},
    # modelis3 draws 48 spheres with sphere(c, r, 10, RGB): 600 quads each in
    # 1.2, 1280 triangles each since 2.0 made the sphere geodesic (+32640).
    "modelis3.py": {"modelis3.off": 99456},
    "modelis4.py": {"modelis4.off": 78000},
    "checkers_v1.py": {"checkers1.off": None},    # contains axes()
    "checkers_v2.py": {"checkers2.off": 60857},
    "checkers.py": {"checkers7.off": 60857},
    "Laikrodis.py": {"laikrodis.off": 912},
    "testing_add.py": {"cube.off": None},         # contains axes()
    "Sierpinski_tetrahedrons.py": {"tetra2.off": 65536},
    # The two rose scripts write to the same file names, so each script gets a
    # working directory of its own.
    "rose.py": {"100_roziu.off": 118644, "3_rozes_vazoje.off": 44818},
    "rose2.py": {"100_roziu.off": 171008, "3_rozes_vazoje.off": 68706},
}

# add.py 2.0 draws the X/Y/Z axis labels as thin bars instead of the baked-in
# letter meshes of 1.2, so any model calling axes() has a different face count
# by design.  For those we only check that the model is still produced and is
# not obviously broken.
MIN_FACES = 500


def sandbox():
    """A fresh working directory holding the legacy files and add.py 2.0."""
    work = tempfile.mkdtemp(prefix="addpy-legacy-")
    for name in os.listdir(LEGACY):
        src = os.path.join(LEGACY, name)
        dst = os.path.join(work, name)
        (shutil.copytree if os.path.isdir(src) else shutil.copy)(src, dst)
    shutil.copy(os.path.join(ROOT, "add.py"), os.path.join(work, "add.py"))
    return work


def run_all():
    import add
    failures = []
    made = []
    for script, outputs in sorted(EXPECTED.items()):
        work = sandbox()
        made.append(work)
        p = subprocess.run([sys.executable, script], cwd=work,
                           capture_output=True)
        if p.returncode != 0:
            failures.append("%s did not run: %s"
                            % (script, p.stderr.decode()[-400:]))
            continue
        for filename, expected in outputs.items():
            path = os.path.join(work, filename)
            if not os.path.exists(path):
                failures.append("%s produced no %s" % (script, filename))
                continue
            faces = add.stats(add.load(path))["faces"]
            if expected is None:
                ok = faces >= MIN_FACES
                note = ">= %d" % MIN_FACES
            else:
                ok = faces == expected
                note = "== %d" % expected
            print("%-28s %-22s %8d faces  %s  %s"
                  % (script, filename, faces, note, "ok" if ok else "FAIL"))
            if not ok:
                failures.append("%s: %s has %d faces, expected %s"
                                % (script, filename, faces, note))
    for work in made:
        shutil.rmtree(work, ignore_errors=True)
    return failures


def test_legacy_models_still_build():
    failures = run_all()
    assert not failures, "\n".join(failures)


if __name__ == "__main__":
    bad = run_all()
    for line in bad:
        print("FAIL", line)
    print("\n%s" % ("all legacy models reproduce" if not bad
                    else "%d problems" % len(bad)))
    sys.exit(1 if bad else 0)

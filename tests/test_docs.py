"""
Every example in the documentation must run.

``docs/reference.py`` holds a short example for every public name of add.py;
this test executes each of them in a scratch directory with a fresh scene,
so an example that no longer matches the code fails here (and in CI)
instead of in front of a reader.  It also checks that every public name has
its Lithuanian explanation and its example.

    python3 tests/test_docs.py
"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "docs"))
import add                                                  # noqa: E402
import reference                                            # noqa: E402


def run_all():
    failures = []
    missing = [n for n in add.__all__ if n not in reference.EXPLAIN_LT]
    if missing:
        failures.append("no Lithuanian explanation for: " + ", ".join(missing))
    missing = [n for n in add.__all__ if n not in reference.EXAMPLES]
    if missing:
        failures.append("no example for: " + ", ".join(missing))
    stale = [n for n in list(reference.EXPLAIN_LT) + list(reference.EXAMPLES)
             if n not in add.__all__]
    if stale:
        failures.append("documented but not public: " + ", ".join(sorted(set(stale))))

    keep = os.getcwd()
    work = tempfile.mkdtemp(prefix="addpy-docs-")
    os.chdir(work)
    try:
        for name in add.__all__:
            code = reference.EXAMPLES.get(name)
            if code is None:
                continue
            folder = os.path.join(work, name)
            os.mkdir(folder)
            os.chdir(folder)
            add.clear()
            add.seed(0)
            try:
                exec(compile(code, "<example %s>" % name, "exec"), {"add": add})
            except Exception as exc:                        # noqa: BLE001
                failures.append("%s: %s: %s" % (name, type(exc).__name__, exc))
            os.chdir(work)
    finally:
        os.chdir(keep)
        add.clear()
        shutil.rmtree(work, ignore_errors=True)
    return failures


def test_every_example_runs():
    failures = run_all()
    assert not failures, "\n".join(failures)


if __name__ == "__main__":
    import io
    import contextlib
    quiet = io.StringIO()
    with contextlib.redirect_stdout(quiet):
        bad = run_all()
    for line in bad:
        print("FAIL", line)
    print("%d documentation examples ran%s" % (
        len(reference.EXAMPLES), "" if not bad else ", %d problems" % len(bad)))
    sys.exit(1 if bad else 0)

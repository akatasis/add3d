# Publishing add.py

The repository is ready to go: `.gitignore`, `LICENSE`, `CITATION.cff`,
GitHub Actions for the tests and for the documentation site, and a commit
history. This page explains the three steps that only the owner of the
GitHub account can do, and the naming question that comes with them.
[Lietuviškai](PUBLISHING.lt.md).

## 1. The name

The module has always been `add.py`, and it stays `add.py`: a student
downloads one file and writes `import add`. A file on a disk needs no
permission from anyone, and "add" is an ordinary English word that nobody
owns, so there is no trademark or licence problem in keeping it.

The **repository** and the **package**, however, are called `add3d`:

* On PyPI the name `add` is already registered -- an empty placeholder
  (version 1.0, no files, no description, no licence) uploaded by someone
  else. Nothing can be published under it, and a project called `add` on
  GitHub would send people looking for a `pip install add` that installs
  nothing. (PyPI's name-transfer procedure, PEP 541, can reclaim an
  abandoned name, but it takes months and is not guaranteed.)
* `add3d` is free on PyPI and on GitHub, is easy to say, and still reads
  as "add, 3D".

So: `pip install add3d` gives you `import add`; the documentation lives at
`…/add3d/`; the file is `add.py`. The README, the paper and the slides all
use this pair of names already.

## 2. Putting the repository on GitHub

**Option A -- restore from the `.bundle` (keeps the whole history).**
Next to this folder is `add3d-2.0-git-history.bundle`, the complete git
history in one file:

```bash
git clone add3d-2.0-git-history.bundle add3d
cd add3d
git remote remove origin
```

Then create an **empty** repository called `add3d` on GitHub (no README,
no licence, or the first push will conflict) and:

```bash
git remote add origin https://github.com/YOUR_NAME/add3d.git
git push -u origin main
```

**Option B -- start the history afresh.** If the history does not matter,
this folder is enough:

```bash
cd add3d
git init -b main
git add .
git commit -m "add.py 2.0"
git remote add origin https://github.com/YOUR_NAME/add3d.git
git push -u origin main
```

## 3. After the first push

**Switch on GitHub Pages.** *Settings → Pages → Source*: choose **GitHub
Actions**. The workflow in `.github/workflows/pages.yml` builds
`docs/index.html` from the docstrings and publishes it at
`https://YOUR_NAME.github.io/add3d/`.

**The links.** The files point to `github.com/akatasis/add3d` and
`akatasis.github.io/add3d`. In a copy published under another account,
replace the name in one go:

```bash
grep -rl "akatasis" . | xargs sed -i "s/akatasis/YOUR_NAME/g"
python3 tools/make_docs.py
```

**Check the Actions tab.** The tests run on Python 3.8-3.13; a second job
checks that `add.py` and `examples/add.py` match `_src/`, that every
example runs and stays within the Sketchfab limits, that every public
function is used by an example (`tools/coverage.py --strict`), that every
documented example runs (`tests/test_docs.py`) and that `docs/index.html`
matches the docstrings. After editing anything in `_src/`, run `python3
build.py` and `python3 tools/make_docs.py` before committing; a new public
function also needs its Lithuanian explanation and example in
`docs/reference.py`, or the documentation build refuses.

**Description and topics.** Suggested description:

> Build 3D models with nothing but Python code. One file, no dependencies,
> mesh booleans from scratch.

Topics: `3d`, `python`, `geometry`, `csg`, `computational-geometry`,
`education`, `parametric-surfaces`, `mesh-processing`, `teaching`,
`no-dependencies`.

## 4. Releasing on PyPI (optional)

The one-file download stays the recommended way, but a package lets people
`pip install add3d`. `pyproject.toml` already carries the metadata; a
release is:

```bash
python3 -m pip install --upgrade build twine
python3 build.py && python3 tests/test_add.py
python3 -m build                      # -> dist/add3d-2.0.tar.gz and .whl
python3 -m twine upload dist/*        # needs a PyPI account and an API token
```

Test first on `test.pypi.org` (`twine upload --repository testpypi dist/*`)
if in doubt. The version number lives in `_src/00_core.py` (`__version__`),
`pyproject.toml`, `CITATION.cff` and `docs/content.py`.

## 5. Sharing beyond GitHub

* **Sketchfab**: `add.save("model.obj")` writes `.obj` + `.mtl` (opacity
  and textures included); upload both, with any texture images, in one
  archive. Keep under 50 MB and 50 colours (`add.check()` tells you;
  `add.save("model.obj", colors=50)` reduces a colourful model). A model
  too big for memory is written with `add.stream("model.obj")` part by
  part (the castle of example 46 is: a 400 MB `.off` and an `.obj` that
  is under 100 MB once 7-Zip has compressed it). `save` and `stream` tidy
  the model on the way out, so nothing flickers in the viewer.
* **Paper**: `paper/paper.md` (+ `references.bib`) is written for a
  computer-science-education venue; the repository link and the DOI (if
  you archive a release on Zenodo) go into `CITATION.cff` too.
* **Talks and video**: `outreach/` holds the script and the outline;
  `slides/` the lecture decks in English and Lithuanian.

## What is where

| Folder | Contents |
|---|---|
| `add.py` | the library -- the only file students need |
| `_src/` + `build.py` | the sections `add.py` is assembled from |
| `examples/` | 43 commented example programs and a copy of `add.py` |
| `tests/` | 91 unit tests, the add.py 1.2 compatibility fixture and the documentation-example runner |
| `tools/` | `preview.py` (renderer), `make_docs.py`, `coverage.py` |
| `docs/` | the documentation site (EN/LT) and its pictures |
| `slides/` | the lecture slides (.pptx, .pdf and the generator) |
| `paper/` | the paper (Markdown + BibTeX) |
| `outreach/` | video script (EN/LT) and talk outline |

## Quick check before pushing

```bash
python3 build.py --check          # add.py and examples/add.py are up to date
python3 tests/test_add.py         # 91 passed, 0 failed
python3 tests/test_legacy.py      # all legacy models reproduce
python3 tests/test_docs.py        # 231 documentation examples ran
python3 tools/coverage.py --strict
python3 tools/make_docs.py        # docs/index.html
python3 examples/build_all.py --models   # every example fits the Sketchfab limits
```

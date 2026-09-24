---
title: "Modelling with Code Alone: add.py 2.0, a Single-File Python Library with Dependency-Free Mesh Booleans and Subdivision Surfaces for an Algorithms Course"
author: "Martynas Sabaliauskas"
affiliation: "Institute of Data Science and Digital Technologies, Faculty of Mathematics and Informatics, Vilnius University, Lithuania"
email: "martynas.sabaliauskas@mif.vu.lt"
date: "2026-09-18"
keywords:
  - computer science education
  - 3D modelling
  - constructive solid geometry
  - mesh Boolean operations
  - computational thinking
  - Python
  - creative assignment
  - Bloom's taxonomy
bibliography: references.bib
---

# Abstract

We describe `add.py` 2.0, a single-file, dependency-free Python library used for a creative assignment in the courses *Algorithms and Data Structures* and *Algorithm Design and Analysis* at Vilnius University, in which students must build a 3D model of at least ten thousand polygons using nothing but program code — no modelling application, and no mesh library from which a model could be taken. The library imports only `math` and `random`, so every triangle in a student's model is traceable to a line of code the student can read. Version 2.0 adds mesh Boolean operations — union, intersection and difference — implemented from scratch, and deliberately not in the textbook BSP formulation: an earlier BSP prototype in the same codebase degenerated to quadratic behaviour on exactly the convex inputs students use most, taking 37.7 s for a 6144-face quad sphere minus a box. The algorithm we ship instead splits each triangle incrementally against the planes of nearby triangles of the other solid, found through a uniform spatial hash; classifies each piece as inside, outside, or on the shared surface facing the same or the opposite way, using ray casting with a direction-aligned bucket index; and applies a small per-operation keep-set table. The same input now takes 0.53 s, and the result is watertight, which the prototype's was not. Alongside the Booleans we add T-junction healing, mesh repair and validation, a `solidify` operation that turns a zero-thickness parametric sheet into a closed solid, export to OBJ, PLY and STL, and a dependency-free software rasteriser. Version 2.0 also replaces the quad sphere by a geodesic sphere of triangles built from the icosahedron, adds the five regular polyhedra with the tools needed to build on their vertices (neighbours, valence, duals, truncation — a football is one call), a catalogue of twenty-five named parametric surfaces, and smooth surfaces: classical Catmull–Clark subdivision together with a pure-Python port of the author's generalised algorithm, which samples the limit surface with any number of cells per control edge and is cross-checked against the reference implementation to machine precision. Export is aimed at Sketchfab: `check()` reports the file-size and material limits, a palette-reduction pass keeps colourful models within them, and optional transparency and image textures are written to the `.mtl` file without changing anything for models that use neither. A backwards-compatibility technique — a float-based `Mesh` class that also behaves like the old pair of string lists — lets every model written for version 1.2 run unchanged. We report measured timings, a suite of 94 unit tests checking closedness and analytic volumes of every primitive and of Boolean results, a documentation whose 235 examples are executed by the test suite, and we discuss the limitations of a pure-Python, tolerance-based implementation and the role of generative AI in an assignment whose defining constraint is that the reasoning must be written down as code.

**Keywords:** computer science education; 3D modelling; constructive solid geometry; mesh Boolean operations; subdivision surfaces; computational thinking; Python; creative assignment; Bloom's taxonomy.

# 1. Introduction

Students in *Algorithms and Data Structures* (*Algoritmai ir duomenų struktūros*) and *Algorithm Design and Analysis* (*Algoritmų kūrimas ir analizė*) at the Faculty of Mathematics and Informatics of Vilnius University are set a creative assignment: produce a 3D model using nothing but program code. No 3D modelling application, and no mesh library from which a ready-made model could be lifted. The model must contain at least 10 000 polygons, use at least three colours, be produced by code containing a loop, and expose at least one parameter that changes its shape. The output is a file in OFF [@offformat] or OBJ [@objspec] format.

The assignment is deliberately awkward. A student who wants a sphere cannot fetch one and must decide how to tile it; a student who wants a cathedral must decompose it into repeated elements, because ten thousand polygons cannot be typed out by hand; a student who wants a hole in a plate must work out what a hole *is* in terms of triangles. Forbidding anything drawn by hand is what turns a modelling exercise into an algorithmic one.

The tool the students are given is `add.py`, a single Python file that we wrote and have revised every year since around 2018. Version 1.2b was 922 lines: primitives, the parametric-surface function at the heart of the library, a lathe (`spin3D`), a tube-along-a-curve (`curve`), a few transforms over a "layer" of accumulated geometry, and an OFF writer. It had no repair functions, no validation, no Boolean operations, and no way to look at the result without installing something else.

This paper describes version 2.0: about 7 800 lines, 235 public names, still a single file importing only `math` and `random`. The substantive additions are:

1. **Mesh Boolean operations** — union, intersection and difference — written from scratch (Section 5); the technical core of the paper.
2. **T-junction healing** and a **mesh repair** pass, which is what makes Boolean output watertight rather than merely plausible (Section 6).
3. **`solidify`, `thickness=` and `double_sided=`**, turning a zero-thickness parametric sheet into a closed solid so that it is lit correctly from both sides (Section 4.5).
4. **Export to OBJ+MTL, PLY and STL** alongside OFF, and tolerant loaders (Section 7.2).
5. **`check()`**, a validator reporting polygon count, colour count, closedness, and whether the assignment's requirements are met (Section 6.4).
6. **A dependency-free software renderer** (`tools/preview.py`): a z-buffered flat-shaded rasteriser writing PNG via `zlib` (Section 7.1).
7. **A much larger, more descriptive vocabulary** while keeping every 1.2 name working, through a backwards-compatibility technique we believe is reusable elsewhere (Section 4.6).
8. **Ready-made parts, placement functions and colour functions**, derived from a survey of the recurring sub-problems in student models (Section 4.7).
9. **The five regular polyhedra, a geodesic sphere and vertex-level tools** — neighbours, valence, duals, truncation — so that a model can be built *on* a polyhedron rather than merely out of them (Section 4.8).
10. **Smooth surfaces**: classical Catmull–Clark subdivision and a pure-Python port of the generalised algorithm of [@sabaliauskas2026uniform], which samples the limit surface with any number of cells per control edge (Section 4.9).
11. **A catalogue of twenty-five named parametric surfaces** (Section 4.10).
12. **Sketchfab-oriented export** — size and material limits reported by `check()`, palette reduction, and optional transparency and image textures in the `.mtl` file (Section 7.3).

We want to be precise about what is and is not new. BSP-based constructive solid geometry [@thibault1987set; @naylor1990merging], boundary evaluation [@requicha1985boolean], ray-casting point classification and uniform spatial hashing [@teschner2003optimized] are standard, decades-old techniques, and the state of the art in robust mesh Booleans [@zhou2016mesh; @cherchi2020fast] is far beyond anything here. What we claim is the *combination*: a Boolean evaluator fast and robust enough for teaching, packaged in a single dependency-free file, short enough that a second-year student can read all of it, inside a library designed around one assignment — together with the backwards-compatibility technique and the pedagogical framing.

# 2. Related work

## 2.1 Constructive solid geometry and BSP trees

Boolean set operations on solids are a founding problem of solid modelling. Requicha and Voelcker [@requicha1985boolean] set out the classical *boundary evaluation* framework: split the faces of each operand against the other, classify the resulting pieces with respect to the other solid, and keep the pieces the operation calls for. Every polygonal Boolean algorithm we know of, including ours, is an instance of that framework; the differences lie in how splitting is organised, how classification is decided, and how degeneracies are handled.

The best-known organisation is the binary space partitioning tree, introduced for visibility ordering by Fuchs, Kedem and Naylor [@fuchs1980visible] and applied to set operations by Thibault and Naylor [@thibault1987set] and then by Naylor, Amanatides and Thibault [@naylor1990merging], who showed that merging two BSP trees directly yields the polyhedral set operations. The formulation is elegant: splitting and classification become the same recursive traversal, and the tree is a complete representation of the solid rather than an acceleration structure bolted on. Its practical drawback is quantified in the theory: Paterson and Yao [@paterson1990efficient] prove a Θ(n²) worst-case bound on BSP size for n planar facets in three dimensions. The auto-partition BSP of a *convex* polyhedron is a degenerate case — no face ever splits another, so the tree is a linear chain of n nodes, and classifying a polygon against it costs Θ(n). Since convex primitives (boxes, cylinders, quad spheres) are precisely what a teaching library produces, the worst case is the common case; Section 5.1 reports what that costs in practice.

The most widely copied implementation is `csg.js` by Evan Wallace [@wallace2011csgjs], which expresses all three operations in terms of two tree methods, `clipTo` and `invert`, and has been ported many times, including to Python as `pycsg` [@knip2014pycsg]. These implementations are small and readable — which is why they attract teachers — but they inherit the BSP cost model and neither weld nor heal their output, so a difference typically has cracks along the cut.

## 2.2 Robust mesh Booleans

A second line of work trades speed-through-structure for exactness. Bernstein and Fussell [@bernstein2009fast] keep BSP trees but move to a plane-based representation with exactly decided predicates, reporting large speedups over CGAL's Nef polyhedra while remaining fully robust. Nef polyhedra themselves [@hachenberger2007boolean; @cgalnef] give a complete and exact set-theoretic representation over an exact number type, at a substantial cost in time and memory, and Barki, Guennebaud and Foufou [@barki2015exact] give exact regularised Booleans for general — including non-manifold and self-intersecting — meshes.

Zhou, Grinspun, Zorin and Jacobson [@zhou2016mesh] reframed the problem: rather than computing one Boolean at a time, resolve all intersections exactly to obtain a *mesh arrangement*, label each of its cells with a winding-number vector, and extract any Boolean — including n-ary operations that have no CSG expression — by evaluating a function of those numbers; their implementation is part of `libigl` [@libigl]. Cherchi, Livesu, Scateni and Attene [@cherchi2020fast] made the arrangement stage fast by representing intersection points implicitly and filtering predicates through floating point, interval arithmetic and expansions in turn, obtaining exactness at close to floating-point speed.

`add.py` does none of this. It uses ordinary double-precision arithmetic and tolerances, so it is not robust in the technical sense, and Section 9.1 states plainly what that costs. What it borrows from this literature is the *shape* of the answer: split, classify, select — and the awareness that the hard part is degeneracy, not the common case.

## 2.3 Programmatic and script-based modelling

Describing shapes by code rather than by mouse is established practice. OpenSCAD [@openscad; @gohde2021openscad] is the best-known example: a declarative language whose primitives are combined with `union`, `difference` and `intersection`, evaluated by a CGAL-based kernel. CadQuery [@cadquery] gives Python a fluent API over the OCCT boundary-representation kernel; Blender's Python API [@blenderpython] exposes a full production modelling system to scripts; JSCAD [@jscad] brings the OpenSCAD idea to JavaScript in the browser, and ImplicitCAD [@implicitcad] replaces meshes with implicit functions. Outside CAD, Processing [@reas2007processing] established the pattern of a small, friendly API whose purpose is to make programming produce something visible immediately.

`add.py` differs from all of these in ways that matter for the assignment rather than for engineering:

- **No dependencies, no installation, no kernel.** A student copies one file next to their script: no CGAL, no OCCT, no build step, no virtual environment. Where the marked artefact is the code, this removes a whole class of "it does not work on my machine" from the assessment.
- **Teaching scale and readability.** The whole implementation — including the Boolean evaluator — is Python a second-year student can open and read. When a student asks how `difference` works, the answer is a page of code in the file they already have.
- **Meshes, not solids.** OpenSCAD and CadQuery hide the mesh; `add.py` is the mesh. Faces, vertices, winding and watertightness stay visible, because they are the concepts the assignment is about.
- **A library in the student's own language.** The model is a Python program with loops, functions and parameters, not a script in a domain-specific language, so what the course teaches about decomposition and complexity applies directly.

We are not aware of published work describing a dependency-free single-file mesh-modelling library built specifically for a creative programming assignment; the nearest published material is the practitioner literature around OpenSCAD in the classroom [@gohde2021openscad].

## 2.4 Educational background

The assignment sits in a long tradition. Papert's constructionism [@papert1980mindstorms; @papert1991situating] holds that learning is most effective when the learner is building a public, shareable artefact; Turtle geometry [@abelson1981turtle] is the canonical demonstration that geometry can be *done* by programming rather than merely illustrated by it. Wing's framing of computational thinking [@wing2006computational] describes exactly the reformulation the assignment forces: to make a rose, you must first decide what a rose is in terms of repeatable operations. Guzdial's media computation courses [@guzdial2003media] showed that a visible artefact changes student engagement with otherwise dry material.

The course states its objectives in terms of the revised Bloom taxonomy [@anderson2001taxonomy], whose highest level, *Create*, is characterised as putting elements together into a coherent new whole. The creative assignment exists to occupy that level; Section 3 explains how.

Finally, there is a growing literature on 3D printing and 3D modelling in education [@pearson2022printing; @ng2022exploring], most of it about school-level or pre-service-teacher settings and about *using* modelling tools. Our setting is the complement: the modelling tool is forbidden, and the geometry has to be programmed.

# 3. The pedagogical design

## 3.1 The assignment

The assignment is one of the graded components of the course, and its statement fits on one slide:

> Build a 3D model using only program code. You may not use 3D modelling software, and you may not take a model from a mesh library. The model must have at least 10 000 polygons and at least three colours, the code must contain a loop, and the model must have at least one parameter whose value changes the shape. Deliver the code and the model in OFF or OBJ format.

Each clause does a specific job:

- **"Only program code"** removes the possibility of producing the artefact by craft rather than by reasoning, and makes the work reviewable: what the student submits *is* the reasoning.
- **At least 10 000 polygons** makes manual enumeration impossible. The threshold is well beyond what anybody will type, so some generative structure — a loop, a recursion, a parametric surface, a repeated component — becomes mandatory.
- **At least three colours** forces the student to see the model as a structured object with distinguishable parts, and incidentally to carry per-face attributes through whatever transformations they apply.
- **A loop** is the minimum syntactic evidence of generative construction.
- **A parameter that changes the shape** is the clause students find hardest and learn most from: it converts a model from a fixed object into a family of objects, which is the difference between drawing and designing. It is also a cheap plagiarism check, since a copied model rarely survives a request to vary it.

## 3.2 Why "code only"

There are three reasons, in increasing order of importance.

First, **it makes geometry computational.** Asked to make a torus in Blender, a student selects a torus. Asked to make one in code, a student must find the parametrisation, choose a sampling density in each direction, work out the order in which a quad's four corners must be listed for the face to point outwards, and notice that the last row must be joined back to the first or there will be a seam. Every one of those is an algorithmic decision with a visible consequence.

Second, **it connects to the course.** A model with 10 000 polygons makes cost concrete: a naive `O(n²)` weld on a 200 000-vertex model is not a theoretical concern, it is a coffee break, and a student writing a recursive Sierpiński construction watches the recursion's growth in the file size.

Third, **it makes the reasoning visible and reviewable** — the reason that has grown most in importance (Section 9.2). The submitted program is a complete, executable record of how the artefact came to exist: no hidden step, no undo history, no intermediate file that only the student's laptop saw. For assessment at the *Create* level of the taxonomy, that is exactly what one wants to read.

## 3.3 A deduction-first philosophy

The course is graded deduction-first: a submission starts from the full mark and loses points for concrete, named defects — a requirement not met, an unjustified constant, code that does not run, a claim in the report that the code does not support. This matters for tool design. A student who knows that a non-closed surface, a missing colour or a polygon count of 9 870 will each cost marks wants to check those things *before* submitting, without asking anybody. That is the direct motivation for `check()` (Section 6.4): it closes the feedback loop inside the student's own workflow and removes from the grading conversation every dispute that is a matter of counting rather than of judgement.

## 3.4 Where the assignment sits in the taxonomy

Mapping the assignment onto the revised taxonomy [@anderson2001taxonomy] is instructive because the lower levels are not skipped, they are traversed quickly (Table 1).

**Table 1. The assignment mapped onto the levels of the revised Bloom taxonomy.**

| Level | What the assignment demands |
|---|---|
| Remember | The coordinate convention, the OFF face syntax, the names of the primitives. |
| Understand | Why a face has an orientation; why a sheet has a "wrong side"; what a closed surface is. |
| Apply | Use `parametric`, `revolve` or `sweep` to realise a shape that has been decided on. |
| Analyse | Decompose an intended object into parts, repetitions and parameters; find the reason a model is not closed. |
| Evaluate | Judge whether a construction meets the requirements and whether a chosen sampling density is adequate; read `check()` and act on it. |
| Create | Design and build a coherent model that did not exist before, together with the parameterisation that generates its family. |

The library is designed so that the *Apply* level is cheap. Students learn little from re-deriving the vertex order of a cylinder cap for the fourth time; they learn from deciding what to build and how to generate it. Every function in `add.py` exists to take a student quickly to the point where the remaining difficulty is their own design problem.

# 4. The library: data model and API design

## 4.1 One data structure

`add.py` has exactly one data structure. A `Mesh` holds three parallel lists: `M.V`, the `[x, y, z]` float points; `M.F`, one index list per face, of any length ≥ 3; and `M.C`, one `(r, g, b)` colour per face. `len(M.F)` is the polygon count that the assignment asks about. There is no half-edge structure, no cached adjacency, no cached normals; adjacency is rebuilt when needed as a dictionary keyed on sorted vertex-index pairs, which at course sizes is fast enough and keeps the data structure something a student can print.

Faces are polygons, not triangles. A quad grid, which is what every parametric surface produces, reads better in a file, halves the face count, and is supported natively by OFF. Triangulation happens only where it is needed — inside the Boolean evaluator, in the STL writer, and in the OFF writer for a face of five or more corners, which it cuts into quadrilaterals and at most a triangle or two, because MeshLab, the viewer the course uses, can crash on bigger OFF faces.

Orientation follows the usual convention: a face is outward when its vertices run counter-clockwise as seen from outside. The library enforces this with a signed-volume test (`_signed_volume`, six times the volume by the divergence-theorem sum over faces), so that a primitive built "upside down" — `pyramid` with a negative height, `mirror` applied to a solid, a negative scale factor — is flipped back before it reaches the scene. The unit tests check it for every primitive (Section 8.3).

## 4.2 Three layers of API

The public surface is organised into three layers, and the documentation, the examples and the course slides all use the same three words.

**Draw.** `box`, `sphere`, `cylinder`, `torus`, `parametric`, `revolve`, `sweep`, `extrude`, `loft`, `voxels`, `polyhedron`, … add geometry to a current scene. A first program is three lines: draw, draw, save.

**Shape.** `layer()` takes the accumulated scene out as a `Mesh` and starts a fresh empty one; `mesh(M)` (also spelled `paste`) puts one back in. Between the two, a mesh can be moved, rotated, mirrored, twisted, tapered, bent, coloured, arrayed, or combined with another by a Boolean. Every transform returns a *new* mesh and leaves its argument alone, so `move(rotateY(M, a), [0, 3, 0])` is safe to write and a part can be reused. `push()`/`pop()` bracket a helper function so that it cannot scoop up everything drawn before it — the commonest surprise for anyone using `layer()`.

**Finish.** `clean()` repairs, `check()` reports, `save()` writes.

This layering is the main API lesson of version 2.0. Version 1.2 had really only the Draw layer, and students wrote one long list of drawing calls. The `layer`/`mesh` pair makes "build a part once, then place forty copies of it" the natural thing to write — exactly the decomposition the assignment is trying to teach.

## 4.3 Descriptive names

Version 1.2 named shapes by numbering variants: `cube`, `cube2`, `cylinder2`, `cylinder3`, `cone2`, `rectangle3D`. Nobody could remember which was which, and code written with those names could not be read aloud. Version 2.0 introduces a descriptive vocabulary — `box`, `cuboid`, `frame`, `tube`, `cup`, `cone_open`, `frustum`, `pipe`, `capsule`, `revolve`, `sweep`, `extrude`, `loft`, `ribbon`, `voxels`, `polyhedron` — chosen so that the name states what the shape is and, where it matters, which ends are closed: `cylinder` has two lids, `tube` has none, `cup` has one.

Growing to 178 public names is a real cost — a larger surface to learn. We mitigate it by grouping the names into the three layers above, so a student needs only the Draw layer to produce something, and by shipping thirty numbered example scripts — eighteen studies of one group each and twelve complete models — every one a runnable program that produces a model file and a rendered image. A coverage script (`tools/coverage.py`) checks on every commit that each public function is used by at least one example, so nothing in the reference is undocumented by a working program.

## 4.4 Curves and sweeps

`sweep`, `curve`, `extrude` and `ribbon` all slide a two-dimensional cross-section along a three-dimensional path, and they share one piece of machinery: a rotation-minimising frame along the path. The naive choice, the Frenet frame, spins wildly at an inflection point and reverses at a straight segment, so a swept profile visibly twists on its own — a defect students reported against version 1.2's `curve`. Version 2.0 computes the frame with the double-reflection method of Wang, Jüttler, Zheng and Liu [@wang2008computation]: each frame is carried to the next by two successive reflections, one in the bisecting plane of the two points and one in the bisecting plane of the two tangents. It is a dozen lines, it needs no trigonometry, and for a closed path the residual twist is measured once and distributed evenly around the loop so that the seam matches.

## 4.5 Sheets, solids and the wrong side

A parametric surface is a sheet with no thickness. Every face points one way, and from the other side a renderer shows the back face, usually drawn black or not at all. Students hit this the first time they look at a saddle from underneath, and the symptom ("my model is black") gives no hint of the cause.

Version 2.0 makes the cure a keyword. `parametric(..., double_sided=True)` adds a reversed copy of every face: cheap, still zero thickness, correct from both sides, twice the polygon count. `parametric(..., thickness=t)` calls `solidify`, which offsets every vertex along its area-weighted average normal by ±t/2, emits the outer shell and the reversed inner shell, then stitches the boundary — every edge used by exactly one face — with a wall running outer → inner → inner → outer so that it faces outwards. The result is watertight, printable and correct from every angle by construction rather than by a rendering trick; `ribbon` uses the same machinery to turn a swept band into a solid bar.

The motivating anecdote is worth recording. We asked a general-purpose large language model to generate a rose using this library. The code ran and produced a plausible rose — but seen from above it was black, because every petal was a one-sided sheet whose faces all pointed downward. The model was geometrically fine and visually broken, and nothing in the code said so. Diagnosing it requires knowing that faces have sides; fixing it, now, requires typing one keyword.

## 4.6 Backwards compatibility as a design technique

Eight years of student and author models are written against add.py 1.2, where a "mesh" was a two-element list: vertex *strings* (`"1.5 0 -2"`) and face *strings* (`"4 0 1 2 3 255 0 0"` — corner count, indices, RGB). The module also exposed two global lists, `add.vertices` and `add.faces`, that user code read, appended to and took the length of. Version 2.0 needed floats in a structured object — string parsing inside a Boolean evaluator would be absurd — without breaking any of that. The technique has two halves.

**A dual-personality mesh.** `Mesh` stores floats, but implements `__len__` returning 2, `__iter__` yielding two lists, and `__getitem__` such that `M[0]` materialises the vertex strings and `M[1]` the face strings. Old code that writes `V, F = M` or `len(M[1])` or `M[1][3].split()` keeps working; the strings are generated on demand and thrown away. In the other direction, `as_mesh()` accepts a `Mesh`, a `[vertex_strings, face_strings]` pair, or `None` (the current scene), and always returns a `Mesh`. Every public function begins by calling it; a dozen lines of adapter make the whole new API accept the whole old representation.

**Live views for module-level state.** `add.vertices` and `add.faces` are instances of a `_StringView` class holding nothing but a flag saying which of the two it is. `__len__` reports `len(_scene.V)` or `len(_scene.F)` directly; `__getitem__`, `__iter__`, `__repr__` and `__eq__` materialise the string list on demand; `__iadd__` parses incoming strings back into the scene, so `add.faces += ["3 0 1 2 255 0 0"]` still works for anybody who learned the 1.2 internals. Being windows on the current scene, they never go stale.

The general lesson: when a library's public data representation must change, it is usually cheaper and far less disruptive to keep the old representation as a *computed view* of the new one, plus one normalising adapter at every entry point, than to maintain two code paths or ask users to migrate. The precondition is that the old representation be reconstructible — here it is, since the string form carries exactly vertices, faces and colours.

Table 2 gives the mapping as implemented (`add.py` section 19).

**Table 2. add.py 1.2 names and their 2.0 equivalents. Every name in the left column still exists and still behaves as it did.**

| add.py 1.2 name | 2.0 name | What it produces |
|---|---|---|
| `newface(A, RGB)` | `polygon` | one flat face through the given points |
| `cube(c, e, RGB)` | `box` | axis-aligned cube of edge `e` |
| `rectangle3D(c, e, RGB)` | `cuboid` | box with three separate side lengths |
| `cube2(c, e, b, RGB)` | `frame` | hollow cube of twelve bars of thickness `b` |
| `cylinder2(A, B, r, k, RGB)` | `tube` | cylinder wall, no lids |
| `cylinder3(A, B, r, k, RGB)` | `cup` | cylinder closed at `A` only |
| `cone2(A, B, r, k, RGB)` | `cone_open` | cone wall only, no base |
| `circle(A, B, r, k, RGB)` | `disc` | filled circle facing `B` |
| `spin3D(A, B, S, …)` | `revolve` | surface of revolution of profile `S` |
| `curve(P, …, isConnected)` | `curve` (kept; now uses rotation-minimising frames) | round tube along a 3D curve |
| `off(path)` | `save(path)` | write OFF, then empty the scene |
| `zoom(M, s)` | `zoom` (alias `scale`) | uniform scaling |
| `add.vertices`, `add.faces` | live string views on the scene | 1.2 string representation |
| — | `ball`, `block`, `lathe`, `translate`, `reflect`, `weld`, `cuboid3D`, `solid_of_revolution`, `paste`, `common`, `add_solids`, `subtract` | further spellings people reach for |

## 4.7 What students keep building: parts, placement and colour functions

The last round of additions was shaped by reading the models of several cohorts and asking which sub-problems recur regardless of subject. Three did. First, *a bar between two points*: tank barrels, bridge cables, table legs, crane booms — every second model contains a hand-written oriented box, each with its own orientation bug. `beam(A, B, width, height)` computes the frame from the two endpoints and an `up` hint. Around it sit the other parts that turned out to be universal — `wheel`, `gear`, `arch`, `stairs`, `roof`, `column`, `bricks`, `tree`, `rounded_box`, `hemisphere` — and two voxel builders, `pixels` (strings of characters → coloured cubes) and `heightmap` (a table of integers → columns of cubes), both emitting only the exposed faces so the result is watertight by construction. Second, *placement*: parts are built around the origin and then have to be pointed and dropped somewhere. `aim(M, direction)` applies the minimal rotation taking a chosen axis of the mesh onto a direction; `rotate_point` gives the position of a crank pin for a given wheel angle so that connecting rods fit for every angle; `random_points(..., height=f)` returns points lying on a height field and `scatter` places randomly turned and scaled copies on them; `along` strings copies along a curve, each turned to follow it. Third, *colour as a function*: a striped tower, a banded planet, a chequered floor, a terrain coloured by height were all being done with per-face loops after the fact. Every surface constructor now accepts a callable in place of a colour and calls it once per cell with the surface's own two parameters — `(u, v)` for `parametric`, `(t, angle)` for `revolve` and `curve`, `(x, z)` for `grid` — so a colour rule is one `lambda` beside the geometry it belongs to.

Two smaller changes follow the same principle of removing friction that has nothing to do with geometry. `math` and `random` are re-exported from the module, so a model file needs exactly one import (`add.sin`, `add.pi`, `add.randint`); and a built-in stroke font, `text()`, lets a model carry its own title or a date — including the Lithuanian letters, which the previous approach of loading letter meshes from the course's OFF files could not. A third removes the commonest trap of the layer protocol: `make(draw, *args)` calls a drawing function inside `push()`/`pop()` and returns the part as a mesh, so a part built inside a larger scene can no longer scoop up everything drawn before it.

## 4.8 Regular polyhedra, the geodesic sphere and the vertex tools

Three requests recur in models that start from a polyhedron, and each needed a different kind of function. The first is the polyhedra themselves: `tetrahedron`, `octahedron`, `dodecahedron`, `icosahedron` (and `polyhedron("cube")`) are stored with their centre at the origin, so that the average of the vertex coordinates is exactly the requested centre, and `polyhedron_points` returns the coordinates alone for anyone who wants to place twelve things evenly around a point. The second is the sphere. Version 1.2 tiled it with six warped square patches — the construction of the course's own Maple worksheet, kept as `quadsphere` — but a dome of nearly equal triangles is what an observatory, a geodesic house or a 3D printer wants, so `sphere` is now geodesic: the icosahedron's twenty triangles are split into four and the midpoints pushed out onto the sphere, `subdivisions` times, with midpoints shared through a dictionary so that the result is watertight (`20·4^s` faces). The old detail number `k` is mapped onto the nearest level (`k=10` gives 1280 triangles, `k=20` gives 5120), so a 1.2 script still produces a sphere of comparable size — the one deliberate change in face counts that the compatibility suite records.

The third is the ability to *ask a mesh about itself*. Building a football, a virus with a spike on every vertex or a molecule from a truncated icosahedron requires the neighbours of a vertex in order around it (`neighbors`), how many there are (`valence`: the twelve five-valent vertices of a geodesic sphere are where its pentagons sit), how far they are (`mean_neighbor_distance`, `mean_edge_length`), the normal at a vertex, the centre and normal of a face, and the open borders of a sheet (`boundary_loops`). These are all computed from one ordered-ring walk over the face list, the same walk that `dual` (a vertex per face, a face per vertex) and `truncate` (a small face per vertex, cut at a fraction *t* of every edge; *t* = 1/3 on the icosahedron gives the truncated icosahedron) are built on. `refine` splits faces without moving anything and `spherify` projects vertices onto a sphere, so a geodesic dome comes out of *any* polyhedron; `set_vertex` moves one corner of a coarse mesh while keeping its faces, which is exactly what the next section needs.

## 4.9 Smooth surfaces: the generalised Catmull–Clark algorithm

A coarse polygon mesh — a box with a corner pulled out, a letter united from a few blocks, a dodecahedron — can be read as the control net of a smooth surface. `catmull_clark(M, steps)` is the classical subdivision [@catmull1978recursively], with the cubic B-spline curve rules on border edges so that an open sheet keeps a smooth rim, and with every new quad inheriting the colour of the face it came from. Its limitation is well known: it reaches only 2, 4, 8 … cells per control edge, and the cells crowd around extraordinary vertices.

`smooth(M, n)` is a line-by-line port into plain Python of the reference implementation of the algorithm in [@sabaliauskas2026uniform]. For any *n* ≥ 1 it places an *n* × *n* grid of nodes on each kite of each control face, evaluates every node *exactly* on the Catmull–Clark limit surface — through the bicubic B-spline patch where the neighbourhood is regular, and otherwise through a lazily subdivided patch tree that recurses until the queried point falls in a regular patch — and, with `uniform=True`, first maps the nodes through the paper's reparameterisation of the regular *m*-gon (radial maps with exponent γ = −1/log₂ λ at the extraordinary vertices, blended with Wachspress coordinates, and a centre map for non-quad faces) so that the cells come out evenly sized. Even *n* produces quads meeting at a centre node, odd *n* leaves a small *m*-gon in the middle of each face; `n = 1` simply moves the control vertices to their limit positions. Non-manifold input — two voxels touching along an edge — is cut apart rather than refused, so the models students actually build can be smoothed. The port was validated against the JavaScript reference on twenty control meshes (closed and open, triangles, quads and pentagons, with and without the reparameterisation): the node coordinates agree to within 10⁻¹⁵, and the unit tests further check that for *n* = 2^k the grid coincides with *k* classical subdivision steps followed by the limit projection, and that every grid on a closed mesh is watertight with Euler characteristic 2. Evaluating a 32-panel football with *n* = 16 (11 520 cells) takes 0.2 s in CPython.

## 4.10 A catalogue of named surfaces

`parametric` asks the student for a formula, and most students want one they have seen. `surface(name, center, size, grid, color)` draws any of twenty-five classical surfaces — Klein bottle, Möbius strip, Dini, Enneper, Kuen, Henneberg, Maeder's owl, the apple, the tranguloid trefoil, twisted tori — from a table that holds the formula, the parameter ranges, whether the surface closes in each direction (so that it is drawn without a seam), a default grid and its constants, which can be overridden by keyword. `surface_function(name)` returns the bare *f*(*u*, *v*) for a student who wants their own range or colouring, so the catalogue is a starting point rather than a black box.

# 5. Boolean operations without dependencies

Union, intersection and difference are what students ask for first and what version 1.2 could not do. A hole in a plate, a hollow shell, a cube with rounded edges, a cross drilled through a block, an engraved letter: all of them are one line with Booleans and a research project without.

## 5.1 Why not BSP

The obvious implementation is a BSP tree in the `csg.js` style [@wallace2011csgjs]: it is short, it is well documented, and a Python port already exists [@knip2014pycsg]. We implemented it first, and measured it.

The problem is structural rather than incidental. In an auto-partition BSP the splitting planes are the planes of the input faces themselves. For a convex polyhedron, no face's plane cuts any other face, so every insertion goes to the same side and the tree degenerates into a linear chain of n nodes. Classifying one polygon against that chain costs Θ(n) plane tests, and a Boolean classifies every polygon of each operand against the other's tree, so the whole operation costs Θ(n·m) — and both spheres and boxes, the shapes a teaching library produces constantly, are convex. This is the practical face of the Θ(n²) BSP-size bound of Paterson and Yao [@paterson1990efficient]: it is not a pathological input, it is the default one.

Measured on our reference case — a 6144-face quad sphere minus a box — the BSP prototype took **37.7 s**. Worse, its output was not watertight: BSP splitting introduces T-junctions where a split edge of one face meets the unsplit edge of its neighbour, and neither `csg.js` nor its ports do anything about them, so the result has hairline cracks. A student who then tried to subtract something else from that result got garbage, because the second Boolean needs a closed input.

Two conclusions followed. The splitting had to be driven by a spatial index rather than by a tree, so that its cost scales with how much of the two surfaces actually overlaps; and the output had to be repaired, not just produced.

## 5.2 Overview of the algorithm

The evaluator follows the classical boundary-evaluation pattern [@requicha1985boolean] with three stages.

1. **Split.** Cut every face of each solid until no piece straddles the other solid's surface. A piece is cut only by the planes of triangles of the *other* solid that are actually near it, found through a uniform spatial hash. Cutting is incremental, one plane at a time, and the search is redone for each new piece, so a fragment that moves away from the action stops being cut.
2. **Classify.** Give each surviving piece one of four states with respect to the other solid: `IN`, `OUT`, `ON_SAME` (lying on the other solid's surface and facing the same way) or `ON_OPP` (lying on it and facing the opposite way). `IN`/`OUT` is decided by ray casting; `ON_SAME`/`ON_OPP` by a containment test against the coplanar triangles found during splitting.
3. **Select.** Keep the pieces named by a small per-operation table, reversing the borrowed ones where the table says so, then rebuild a mesh and repair it.

Everything is triangulated on entry (`_to_polys`), so no face can be non-planar or twisted, and the plane of a piece is exact in the sense that it is inherited unchanged from the triangle it came from rather than recomputed after each cut.

## 5.3 Two indexes

**A uniform 3D hash (`_BoxGrid`)** answers "which triangles of this solid lie near this box?". The cell size is one thirty-second of the solid's bounding-box diagonal, and each triangle is filed in every cell its axis-aligned bounding box touches; a triangle long enough to occupy more than 64 cells goes instead on a short *oversize* list that every query also scans. A query gathers candidates from the cells the query box touches, then filters them by a real box-overlap test, so it returns only triangles that could matter. This is the standard uniform-grid construction [@teschner2003optimized]; the oversize list is the only deviation, and it exists because a teaching library really does produce the occasional enormous ground plane beside a millimetre-scale detail.

**A direction-aligned 2D bucket index (`_RayIndex`)** answers "is this point inside?". All rays for a given query travel in the same fixed direction **d**, so the triangles can be projected once onto the two axes across **d** and bucketed in 2D. Testing a point then looks only at the handful of triangles standing in that ray's way, and each test is a Möller–Trumbore ray–triangle intersection [@moller1997fast]. The parity of the number of forward hits gives inside/outside.

The interesting part is what happens when the ray grazes an edge or a vertex. Rather than perturbing the geometry, `_RayIndex.inside` returns *undecided* whenever a hit has a barycentric coordinate within 10⁻⁹ of an edge or a hit distance within 10⁻⁹ of zero, and the caller retries with the next of three fixed, deliberately irrational-looking directions; only if all three are undecided does the query answer "outside". In practice the first direction decides nearly every query, and the fallbacks exist for the axis-aligned, exactly-touching configurations that a library full of boxes produces constantly.

## 5.4 Splitting incrementally

The splitting loop is where the performance comes from, and it is worth stating why it is not simply "collect all nearby planes and split by all of them".

Suppose a large plate is being drilled by a 48-sided cylinder. Collecting the cylinder's ~150 triangle planes and splitting the plate's top face by all of them yields a fan of slivers radiating to the edge of the plate, because every one of those planes is infinite. Instead we split by *one* plane, obtaining a front and a back piece, and re-query the hash for each piece separately: the piece that no longer overlaps the drill gets no cutters back and is finished immediately, while the piece that does overlap continues. The number of output fragments is therefore governed by the local complexity of the intersection curve rather than by the global number of planes.

Two bookkeeping details make this correct and terminating. Each piece carries the set of plane identifiers that have already been applied to it or found not to cut it, so the same plane is never tried twice on a descendant. And a counter aborts after 20 000 splits of a single input face, emitting whatever is left; this has never triggered on course models, but it turns a potential hang into a visible artefact.

## 5.5 Coplanar overlap

The case that breaks naive implementations is two faces lying in the same plane — two boxes stacked so that their tops are flush, a cylinder whose flat end sits exactly on a plate. A coplanar triangle cannot cut the piece at all, since the two planes coincide, yet the two faces may partly overlap, and the overlapping part must be attributed to exactly one of the two solids or the result will have a doubled or a missing wall.

`_Solid.cutters` handles this by substituting, for each coplanar neighbour triangle, the three planes *standing on that triangle's edges* — each perpendicular to the shared plane, through one edge. Splitting by those carves the shared patch out of the piece exactly, so afterwards every fragment is either wholly inside the coplanar triangle or wholly outside it. `_Solid.facing_at` then tests the fragment's centroid against those same edge half-spaces to decide whether it lies on the neighbour, and compares the two normals to say `ON_SAME` or `ON_OPP`.

## 5.6 The keep-set table

With four states available, the three operations are three rows of a table (`_RULES` in the source). The essential design decision is that the shared, coplanar surface is always attributed to **A**, never to B, so a flush patch is kept exactly once.

**Table 3. Which pieces each operation keeps. `ON_SAME` and `ON_OPP` mean "lying on the other solid's surface, facing the same / the opposite way".**

| Operation | Keep from A | Keep from B | Reverse B's pieces |
|---|---|---|---|
| `union(A, B)` | `OUT`, `ON_SAME` | `OUT` | no |
| `intersect(A, B)` | `IN`, `ON_SAME` | `IN` | no |
| `difference(A, B)` | `OUT`, `ON_OPP` | `IN` | yes |

The three rows read naturally. For a union we keep whatever of A is outside B and whatever of B is outside A, plus the flush patches once. For an intersection we keep whatever of each is inside the other. For a difference we keep the part of A outside B, plus the part of B inside A turned inside out — which is what makes the wall of the hole. The `ON_OPP` entry in the difference row is the case where A's face lies flush against a B face that points the other way, meaning B's material is on the far side and A's face survives.

`difference` also paints: the newly exposed surface keeps the colour of the tool that cut it, and `difference(plate, drill, color="black")` overrides that. This is a teaching decision, not a geometric one — a hole the same colour as the plate is invisible in a flat-shaded preview, and students could not tell a successful cut from a failed one.

## 5.7 The algorithm in full

```
Algorithm 1: Boolean evaluation of A op B
------------------------------------------------------------------
CSG(A, B, op):
    (keepA, keepB, flipB) <- RULES[op]              # Table 3
    a <- Prepare(A);  b <- Prepare(B)
    P <- KeepPieces(a, b, keepA, flip = false)
       + KeepPieces(b, a, keepB, flip = flipB)
    return Rebuild(P)

Prepare(M):
    polys <- triangles of M, each carrying its plane (n, w) and colour
    grid  <- UniformHash(polys, cell = bbox_diagonal / 32)
    rays  <- empty; ray indexes are built lazily, one per direction

KeepPieces(source, other, keep, flip):
    out <- []
    for poly in source.polys:
        if box(poly) does not meet box(other):       # cheap early exit
            if "OUT" in keep: out.append(poly)
            continue
        for (piece, flush) in SplitAgainst(poly, other):
            c     <- centroid(piece)
            f     <- other.FacingAt(c, normal(piece), flush)
            state <- (f > 0 ? ON_SAME : ON_OPP)   if f is defined
                     (other.Contains(c) ? IN : OUT)  otherwise
            if state in keep:
                out.append(flip ? reversed(piece) : piece)
    return out

SplitAgainst(poly, other):                 # incremental, locality-driven
    done <- []
    work <- [ (poly, {}) ]                 # piece, planes already settled
    while work is not empty:
        (piece, settled) <- work.pop()
        (planes, flush)  <- other.Cutters(piece)     # hash query on box(piece)
        chosen <- none
        for (id, n, w) in planes:
            if id in settled: continue
            if piece has vertices strictly on both sides of (n, w):
                chosen <- (id, n, w); break
            settled <- settled + {id}      # this plane can never cut this piece
        if chosen is none:
            done.append( (piece, flush) )  # no straddle left: piece is final
            continue
        (front, back) <- SplitPolygon(piece, chosen)
        for part in front + back:
            work.push( (part, settled + {id(chosen)}) )
    return done

Cutters(poly):                              # method of solid "other"
    planes <- []; flush <- []
    for t in grid.near(box(poly)):
        if |<n_t, n_poly>| = 1 and t lies in poly's plane:      # coplanar
            flush.append(t)
            for each edge (p, q) of t:                          # edge planes
                s <- normalise(n_t x (q - p))
                planes.append( ((t, edge), s, <s, p>) )
        else:
            planes.append( ((t, 0), n_t, w_t) )
    return planes, flush

Contains(p):                                # ray casting, parity rule
    for d in three fixed directions:
        r <- RayIndex(d)                    # built on first use
        answer <- r.Parity(p)               # Moller-Trumbore, 2D bucketed
        if answer is not undecided: return answer
    return false

Rebuild(P):
    M <- mesh of the polygons in P
    weld(M, 1e-7); drop degenerate faces; drop repeated faces
    M <- heal(M, 1e-7)                      # close T-junctions (Section 6.1)
    drop degenerate faces; drop unused vertices
    return M
------------------------------------------------------------------
```

`union`, `intersect` and `difference` accept any number of operands and fold pairwise. Each fold first tests whether the two bounding boxes are disjoint: if they are, `union` degenerates to a concatenation, `difference` to a no-op and `intersect` to the empty mesh, all without touching a single triangle. Two further conveniences share the machinery: `symmetric_difference(A, B)` is `union(difference(A, B), difference(B, A))`, and `cut(M, point, normal)` slices with a single infinite plane and caps the exposed cross-section by chaining the rim segments into loops — far cheaper than a full Boolean, because a plane needs no searching, and the natural way to make a cut-away drawing.

# 6. Mesh repair and validation

The Boolean evaluator produces correct pieces; it does not by itself produce a correct *mesh*. A handful of repair passes, all also available to students directly, turn one into the other.

## 6.1 T-junction healing

When a face is split, its neighbour is not: the split introduces a new vertex in the middle of a shared edge, and the neighbour's long edge knows nothing about it. The two faces still meet in space but no longer share an edge, so an edge-count test reports two boundary edges where there should be none, and a 3D printer or a subsequent Boolean sees a crack.

`heal(M, tol)` inserts the missing corners. It builds a vertex grid whose cell size is the model's mean edge length, then for each edge of each face gathers candidate vertices from the cells the edge passes through and keeps those whose perpendicular distance to the edge is within tolerance and whose parameter along the edge is strictly interior; the survivors are sorted along the edge and spliced into the face. Two cases are handled separately: a short edge sweeps the cells of its bounding box, while a long edge walks along itself sampling cells (with a 3×3×3 neighbourhood at each sample) rather than filling a box that might contain the whole model.

This single pass is what makes Boolean output watertight rather than merely plausible, and it is the clearest difference in behaviour between `add.py` 2.0 and the BSP prototype or the `csg.js` family.

## 6.2 Repairing a model built by stacking

Stacked shapes collect rubbish that is invisible on screen but bloats the file and breaks printing and Booleans. `clean()` removes all of it:

- **Coincident vertices** are welded by `_weld`, which hashes each point into a grid of cell size `tol` and compares only within the cell. Because a point near a cell boundary can round either way, `_cell_keys` returns up to eight neighbouring cells when the point sits in the outer quarter of a cell in any axis, and a new vertex is registered under all of them — boundary-aware probing that prevents the classic grid-weld failure in which two points 10⁻¹² apart land in different cells and are never compared.
- **Degenerate faces** — fewer than three distinct corners, or zero area by Newell's normal [@tampieri1992newell] — are dropped.
- **Repeated faces** (the same corner set appearing twice with the same winding) are dropped.
- **Back-to-back face pairs** — the same corner set appearing twice with *opposite* winding — are dropped in pairs by `_drop_internal`. This is exactly the internal wall where two solids touch: two copies of the same square, facing each other, buried inside the model. A cheap orientation signature (`_winding`: does the smallest index run towards its smaller or its larger neighbour?) distinguishes the two windings without computing any geometry.
- **Faces pinched at a vertex** — a polygon that visits the same corner twice, which a Boolean cut occasionally leaves behind and which viewers refuse ("identical vertex indices in the same face") — are split into their separate loops by `_split_repeats`.
- **Coplanar overlaps** are the cause of the flicker ("z-fighting") that students report most: the side of a beam running into a wall, two boxes of the same height crossing, a tile laid on a floor of the same colour. `_cut_overlaps` groups faces by plane and orientation, sorts each group largest first, and cuts every smaller face back by the larger ones it overlaps (convex pieces by ear clipping, subtraction by Sutherland–Hodgman clipping, candidates found through a grid of cells so that a floor of ten thousand tiles is handled in seconds), so that exactly one face covers every patch of a plane. Faces in one plane that look opposite ways are the other case — a chest standing on a floor, a tower on its plinth: the patch they share is a contact between two solids that nobody can see, and it is cut out of both, which is exactly what a Boolean union would leave, so the result stays watertight (a face that would shatter into more than 64 pieces, a floor under a thousand boxes, is left whole together with the faces on it). `overlaps()` counts the offenders and `check()` names them; `save()` and the streaming writer apply the whole repair on the way to the file, which is why a model saved by add.py does not flicker. The same pass cuts every face that is not convex into triangles by ear clipping in its own plane: a viewer draws a polygon as a fan from its first corner, which for an L-shaped slab or a floor with a stairwell covers the notch.
- **Unused vertices** are removed last.

Cutting overlaps adds corners, which are welded to their neighbours and healed into the long edges beside them; a corner welded onto the next one can leave a face that visits a vertex twice, so degenerate and repeated faces are dropped once more after the cut — a cylinder standing on a box then comes out closed. Whatever `clean` is told, the writers never put into a file a face that visits a vertex twice or a coordinate that is not a finite number: these are the two things MeshLab reports ("degenerated faces", "vertices with NAN coords") when it opens a file.

`fix_normals()` is offered separately because it is the expensive one. It builds the shared-edge graph, walks it breadth-first flipping any face that disagrees with its neighbour along their shared edge (two faces sharing an edge must traverse it in opposite directions), then per connected component computes the signed volume and flips the whole component if it came out negative. On a closed model this makes every face point outward; on an open one it at least makes the orientation consistent.

## 6.3 Measuring a model

`stats()` returns a dictionary: vertex, face and triangle counts, distinct colour count, bounding box and size, surface area, enclosed volume, the number of open edges (used by exactly one face), of non-manifold edges (used by more than two) and of duplicate and back-to-back faces, and a `closed` flag that is true when there are neither open nor non-manifold edges. The volume is the signed-volume sum divided by six and is meaningful only for a closed mesh — which is why the report prints it only when `closed` is true.

## 6.4 `check()`: closing the feedback loop

`check()` prints that dictionary as a short human-readable report against the assignment's thresholds:

```
--------------------------------------------------------
  vertices            22410
OK  polygons            22406  (need 10000)
OK  colours             3  (need 3)
   size                10.000 x 3.600 x 10.000
   surface area        352.475
OK  closed surface      yes
   volume              106.375
--------------------------------------------------------
```

and returns a boolean. When the surface is not closed it says *why* — "no, 24 edges have nothing on the other side", or "no, 3 edges are shared by more than two faces" — and when it finds repeated or back-to-back faces it names them and suggests `clean()`. Pedagogically this is the most valuable addition of version 2.0 after the Booleans: under a deduction-first scheme (Section 3.3) it lets a student verify every mechanically checkable requirement without a viewer and without asking anybody, and it turns "my model is broken" into a specific, searchable sentence.

# 7. Implementation notes

## 7.1 A renderer in the standard library

`tools/preview.py` is 243 lines and imports only `math`, `os`, `struct`, `sys` and `zlib`. It loads an OFF, OBJ or PLY file (or takes a mesh in memory), and writes a shaded PNG.

It is a straightforward z-buffered triangle rasteriser: vertices are transformed once into camera space, each polygon is fan-triangulated, projected perspectively, and filled by scanning the projected triangle's bounding box and testing barycentric coordinates, with depth interpolated and compared against a per-pixel buffer. Shading is flat, from a fixed directional light plus a dimmer light along the view direction that keeps cavities readable; the light term uses the absolute value of the dot product, so a one-sided sheet is at least visible from behind. PNG output is hand-rolled — a zero filter byte per scanline, `zlib.compress` on the raster, and IHDR/IDAT/IEND assembled with `struct` and `zlib.crc32` — about twenty lines, and the last reason to install anything is gone.

It is not fast — a 24 576-face model at 880×620 takes 0.63 s — but it does not need to be. Its purpose is that a student on a laboratory machine, a shared server or a locked-down laptop can *see* their model, and that the course materials regenerate by running one script: `examples/build_all.py` runs every example and renders every result.

## 7.2 File formats

`save()` dispatches on the file extension.

**OFF** [@offformat; @geomview] is the course format and the default. `add.py` writes the widely used per-face-colour variant: corner count, corner indices, then three integers giving RGB. Numbers are formatted by a helper that prints an integral value as an integer and otherwise rounds to nine decimals, which alone makes files 23–25 % smaller than version 1.2's `str(float)` output (Section 8.1) with no visible loss of precision.

**OBJ + MTL** [@objspec] is what students need to upload a coloured model to a sharing site. Faces are grouped by colour so that one `usemtl` line covers many faces, and the companion `.mtl` file is written alongside with one `newmtl` per distinct colour.

**PLY** is written in ASCII with per-face RGB properties, and **STL** in ASCII with computed facet normals; STL carries no colour at all, which is worth knowing before a student sends a model to a printer.

Loading is deliberately tolerant, because the files students and previous cohorts produce are not always pristine: comments and blank lines are stripped; the OFF reader accepts the counts on the `OFF` line, faces with or without colours, and colour components as 0–255 integers or 0–1 floats; the OBJ reader handles `v/vt/vn` index triples, negative indices and `usemtl` with an accompanying `.mtl`; the PLY reader parses the header for element counts and vertex property names. A regression test loads a hand-written OFF file in the exact shape the course has distributed for years. Finally, `load_font` and `typeset` read a folder of per-character OFF files and lay out a string, because a surprising number of students want their name on their model.

## 7.3 Sketchfab: size, materials, transparency and textures

Since the models are meant to be shared on Sketchfab, the constraints of that site became requirements of the library. Sketchfab accepts uploads of up to 100 MB on its free plan (200 MB and 500 MB on paid ones) and imposes an upper limit of 100 materials, beyond which it merges some [@sketchfabplans; @sketchfabmaterials]; in an `.obj` file every distinct colour is a material, and a gradient painted with `color_by` produces thousands of them. The course therefore asks for models under 50 MB and 50 colours. Three things make this checkable before the upload: `obj_size(M)` computes the byte count of the `.obj` that `save` would write, from the numbers themselves and without writing the file; `check()` reports both quantities against the limits, with `!!` when they are exceeded; and `limit_colors(M, n)` quantises the palette by median cut, weighted by how many faces use each shade, so that a colourful model is reduced to *n* materials with hardly visible change (`save(path, colors=n)` does it while saving). The example builder runs the same check over every example model and fails if one breaks the limits.

Two optional extras go into the `.mtl` file and nowhere else, so that a model using neither is byte-for-byte what it was. `transparent(colour, α)` is a see-through colour accepted wherever a colour is (a fourth element of the colour tuple, written as `d` in the material); `opacity(M, α)` applies it to a finished part. `texture(M, image, mapping)` wraps an image around a part: it computes a texture coordinate for every corner from a box, planar, spherical or cylindrical projection (or a user function), stores them with the mesh, and the OBJ writer emits `vt` lines, `f v/vt` faces and a `map_Kd` reference. Texture coordinates survive transforms, `merge`, `clean`, `heal` and `triangulate`; Booleans and subdivision rebuild faces and drop them, which the documentation states plainly ("apply textures last"). `write_png` writes an RGB image from a table of colours through `zlib`, so a texture can be *computed* — bricks, wood grain, a planet map — and the example needs no image files. OFF files keep plain RGB, since the course's OFF readers expect exactly three colour components; the software renderer blends transparent triangles back to front and samples textures, so the documentation pictures show both.

# 8. Evaluation

## 8.1 Backwards compatibility

Twelve model scripts written for add.py 1.2 by students of earlier years and by ourselves — `modelis1`–`modelis4`, three versions of a draughts board, `Laikrodis` ("Clock"), `testing_add`, `Sierpinski_tetrahedrons` (which does not even import the library, having copied the parts it needed), and `rose` and `rose2`, two models an LLM was asked to write against the 1.2 documentation — were run against version 2.0 without editing a single character. They are kept in the repository under `tests/legacy/`, and `tests/test_legacy.py` reruns every one of them and compares the face counts, so the claim below is checked on every commit rather than asserted once.

All of them run, and all produce meshes with *identical face counts* — 111 000, 66 816, 78 000, 60 857, 912, 171 008 and 68 706 among them; the three that call `axes()` are excepted, because 2.0 draws the axis labels as thin bars instead of 1.2's baked-in letter meshes, and the `.off` files of the draughts board and the clock count 48 faces more (60 905 and 960), because mending their T-junctions leaves some faces with five or six corners, which the OFF writer cuts in two or three — which is the strongest statement we can make cheaply: the generating code takes the same branches and emits the same number of polygons as before. Vertex counts drop slightly, because primitives are now welded at the seams where their patches meet (`_emit` welds with a 10⁻⁹ tolerance), so a cylinder no longer carries two copies of each rim vertex. File sizes drop by 20–30 % purely from the shorter number formatting: on three representative models we measured savings of 24.8 %, 23.4 % and 23.7 % on byte-identical geometry.

The compatibility layer is itself tested: `test_old_string_api` asserts that `M[0][0]` and `M[1][0]` are strings, that a face string begins with its corner count and ends with three colour integers, and that a raw `[vertices, faces]` pair can be passed to `as_mesh`, `move` and `volume`; `test_global_lists_still_writable` asserts that `add.vertices += [...]` and `add.faces += [...]` still modify the scene; `test_old_names_exist_and_run` calls the 1.2-era functions with their 1.2 signatures.

## 8.2 Boolean performance

Table 4 reports wall-clock timings, best of three runs, on CPython 3.11 on an x86-64 Linux machine. "In" is the total number of input faces of both operands; "out" is the face count after splitting, welding, healing and cleaning. Boolean output usually has more faces than the input, because splitting subdivides and nothing merges the fragments back (Section 9.1); an intersection, which discards most of both operands, can have fewer.

**Table 4. Measured Boolean timings. The first row is the reference case; the BSP prototype took 37.7 s on the same input and produced a result that was not watertight.**

| Case | In (faces) | Time (s) | Out (faces) | Out (vertices) | Watertight |
|---|---:|---:|---:|---:|:--:|
| box − box, flush side faces | 12 | 0.01 | 12 | 12 | yes |
| plate − cylinder (drill a hole) | 150 | 0.12 | 568 | 646 | yes |
| torus − box | 2 054 | 0.18 | 4 145 | 2 193 | yes |
| cylinder ∪ cylinder (cross) | 288 | 0.19 | 1 148 | 1 096 | yes |
| **quad sphere (6 144) − box** | **6 150** | **0.53** | **10 587** | **5 576** | **yes** |
| sphere (5 400) ∪ sphere (5 400) | 10 800 | 1.45 | 19 429 | 11 799 | one non-manifold edge |
| box ∩ sphere (9 600), rounded cube | 9 606 | 1.67 | 7 152 | 5 024 | yes |
| quad sphere (24 576) − box | 24 582 | 2.17 | 41 811 | 21 498 | yes |

The reference case is about **70× faster** than the BSP prototype, and it is watertight, which the prototype's output was not. The scaling from 6 144 to 24 576 input faces — a factor of four in input for a factor of about four in time — is what one expects when the work is governed by the local complexity of the intersection curve rather than by the product of the two face counts.

For calibration, the repair passes are a modest share of that total: run again on the reference case's 10 587-face result, `heal` takes 0.14 s, `clean` 0.04 s and `fix_normals` 0.04 s. Splitting and classification dominate.

## 8.3 Test coverage

The test suite is `tests/test_add.py` with 94 tests, plus `tests/test_docs.py`, which executes the example attached to every one of the 235 public names in the documentation, and `tests/test_legacy.py`; they run under `pytest` or as plain scripts, on Python 3.8 to 3.13, and all of them pass. Its distinctive feature is that primitives are checked against *analytic* quantities rather than stored reference meshes, so a failure means the geometry is wrong, not that a mesh changed. Every closed primitive is also asserted watertight by the edge-count test of Section 6.3, which catches missing lids, unwelded seams and inverted faces at once.

**Table 5. The analytic checks in the test suite (selection). Tolerances are relative; the sampling density is chosen so that discretisation error is comfortably inside the tolerance.**

| Construction | Analytic quantity | Tol. |
|---|---|---:|
| `box(c, 2)` | V = 8 | 2 % |
| `cuboid(c, [2,3,4])` | V = 24 | 2 % |
| `sphere(c, 1.5, 20)` (geodesic, 5120 faces) | V = 4/3·π·r³ | 1 % |
| `quadsphere(c, 1, 10)` | 600 quads, closed | — |
| `uvsphere(c, 1, 48, 24)` | V = 4/3·π·r³ | 1 % |
| `ellipsoid(c, [1,2,3], 20)` | V = 4/3·π·a·b·c | 1 % |
| `cylinder(A, B, 1, 64)` | V = π·r²·h | 1 % |
| `cone(A, B, 1, 64)` | V = π·r²·h/3 | 1 % |
| `frustum(A, B, 2, 1, 64)` | V = π·h/3·(R² + R·r + r²) | 1 % |
| `torus(c, 3, 1, 64, 32)` | V = 2·π²·R·r² | 1 % |
| `capsule(A, B, 1, 48)` | V = π·r²·h + 4/3·π·r³ | 2 % |
| `pipe(A, B, 2, 1, 64)` | V = π·h·(R² − r²) | 1 % |
| `pyramid(c, 2, 3)` | V = a²·h/3 | 2 % |
| `prism(square 2×2, 5)` | V = 20 | 2 % |
| `frame(c, 2, 0.2)` | V = 12·1.6·0.04 + 8·0.008 | 1 % |
| `voxels` (3 unit cells) | V = 3 | 2 % |
| `revolve` of a constant profile | V = π·r²·h (a cylinder) | 1 % |
| `curve`, closed loop | V = 2·π²·R·r² (a torus tube) | 5 % |
| `curve`, open with caps | V = π·r²·L | 5 % |
| `extrude(square 2×2, [0,3,0])` | V = 12 | 2 % |
| `parametric(..., thickness=0.1)` | V ≈ 0.1 (unit sheet) | 5 % |
| `union` of two unit-overlap boxes | V = 8 + 8 − 4 | 1 % |
| `difference` of the same | V = 8 − 4 | 1 % |
| `intersect` of the same | V = 4 | 1 % |
| plate − drill | V = 16 − π·0.8² | 1 % |
| sphere − smaller sphere | V = V(outer) − V(inner) | 1 % |
| `symmetric_difference` | V = 4 + 4 | 5 % |
| `cut` sphere in half | V = V(sphere)/2 | 2 % |
| five Platonic solids | V, F, valence, equal edges, vertex mean = centre | — |
| `truncate(icosahedron, 1/3)` | 60 vertices, 12 pentagons + 20 hexagons, equal edges | — |
| `dual(cube)`, `dual(icosahedron)` | 8 and 12 faces, closed | — |
| `smooth(cube, 2^k)` | = `catmull_clark(cube, k)` at the limit (point sets) | 10⁻⁹ |
| `smooth(M, n)`, n = 1 … 7 | closed, V − E + F = 2, cell count formula | — |
| `smooth(polygon, n)` | stays planar, rim keeps 5·n vertices | 10⁻¹² |
| `obj_size(M)` | = size of the written file | 80 B |
| `.obj` round trip | opacity, texture name and `vt` survive | — |

Beyond volumes, the suite covers colour parsing (named, hexadecimal, 0–255, 0–1, `None`, with opacity and texture), the scene/layer protocol and `make`, transforms (including that mirroring and negative scaling keep the volume positive), arrays and patterns, all four repair passes, file round-trips for OFF, OBJ, PLY and STL, loading legacy and colourless OFF files, the vertex tools, the surface catalogue (every named surface is drawn at low resolution), the Sketchfab limits, and the 1.2 compatibility names. The port of the generalised subdivision algorithm was additionally cross-checked against its JavaScript reference implementation on twenty control meshes, with a worst-case coordinate difference of 9·10⁻¹⁶.

## 8.4 Robustness in the large

Tolerance-based Booleans fail sometimes, and we would rather quantify that than assert it away, so we ran two randomised sweeps.

In the first, 40 random pairs of quad spheres (resolution k ∈ {8, 12, 16, 20}, random offsets, random radii) were combined with a randomly chosen operation. **36 of 40 results were watertight.** Of the four failures, one had three open edges and three had one or two non-manifold edges — edges shared by three faces rather than two. Such a result still renders correctly and still has the right volume, but it would upset a subsequent Boolean or a slicer.

In the second, a box was drilled by a cylinder along 30 random axes with random radii; **all 30 results were watertight.** The contrast is informative: failures cluster on curved-against-curved intersections between nearly tangent surfaces, where a fragment's centroid falls within tolerance of the other surface and the containment test is genuinely ambiguous. Box-against-cylinder, which is what most student models need, is reliable.

## 8.5 What students produce

The examples shipped with the library are a fair sample of what the assignment produces, since several began as student work: a chess set built by revolving profiles and arraying the result; a procedural city; a Sierpiński tetrahedron and other fractals; a gallery of lathed vessels; supershape surfaces driven by the Gielis formula [@gielis2003generic], which fits the "one parameter changes the shape" requirement almost perfectly because a single exponent turns a sphere into a starfish; height fields; sweeps with twist and taper; and a Boolean gallery with a hollow ball cut open, a cube whose twelve edges are rounded by intersecting it with a sphere, and a block with a cross drilled through it. Finished models typically run from about 30 000 to about 170 000 faces — comfortably over the threshold, which is where students stop optimising polygon count and start thinking about shape.

# 9. Discussion

## 9.1 Limitations

**Speed.** `add.py` is pure Python with no vectorisation. A Boolean on 25 000 faces takes seconds; on 250 000 it would take minutes. That is acceptable for the assignment — students apply Booleans to parts, not to finished 170 000-face models — but it is a real ceiling, and it is why the library offers `cut` (plane slicing, no search) and early bounding-box rejection as cheaper alternatives. We think the constraint is worth paying: a vectorised rewrite over NumPy would speed the inner loops up considerably, but it would break the single-file, zero-install property that makes the tool usable in every environment a student might have.

**No exact arithmetic.** Every predicate is a floating-point comparison against a tolerance: 10⁻⁹ for plane classification, 10⁻⁷ for welding and healing, 10⁻⁹ for barycentric edge grazing. There is no symbolic perturbation and no exact filter of the kind that makes the modern literature robust [@bernstein2009fast; @zhou2016mesh; @cherchi2020fast; @barki2015exact]. Section 8.4 measures the consequence: roughly one in ten randomised curved-against-curved Booleans produces a small topological defect, and a model whose scale is wrong for the tolerance — features below 10⁻⁷ units — will fail more often. The tolerances are module constants (`EPS`, `BOOL_EPS`) precisely so that a student who hits this can see and change them.

**No coplanar face merging.** After a Boolean, adjacent fragments lying in the same plane are not merged back into one face, and T-junction healing *adds* corners rather than removing them, so output has substantially more faces than necessary — the reference case turns 6 150 input faces into 10 587. For the assignment this is harmless, even welcome, since the polygon threshold is a floor and not a ceiling; it is nonetheless the most obvious piece of unfinished work.

**Non-manifold and self-intersecting input.** The evaluator assumes both operands are closed. It detects neither self-intersection nor an open input: `check()` will tell the student the input is open, but the Boolean still runs and produces something wrong. A pre-flight rejection would be friendlier.

**The scene is global.** A single module-level current scene is what makes a three-line first program possible and what makes `push()`/`pop()` necessary. We inherited the trade-off from version 1.2 and have kept it, because the alternative — an explicit context object in every call — costs beginners more than it saves.

## 9.2 Generative AI and an assignment made of code

Large language models write Python competently, and a creative assignment delivered as a Python program is obviously exposed; the computing-education community has been working through the implications since Codex [@finnieansley2022robots; @becker2023programming], and this assignment is not exempt. We have experimented with LLM-generated models against this library, and three observations seem worth recording.

First, **the constraint that makes the assignment hard is the constraint that makes it reviewable.** Because nothing may be produced by a modelling application, the submitted program is a complete account of how the artefact came to exist. Whether it was written by the student, by a model, or by both, what is assessed is a readable argument about how to generate a shape, and an assessor can ask the student to explain, extend or re-parameterise any part of it. An assignment whose deliverable is a mesh file is trivially outsourced; one whose deliverable is the generating reasoning is at least *discussable*.

Second, **AI-generated modelling code fails in characteristic, diagnosable ways.** The rose anecdote of Section 4.5 is the clearest example: a structurally sensible rose whose petals were one-sided sheets, so the model was black from above. That is not a syntax error and not a crash; it is a failure to reason about surface orientation, and it is exactly what a student who has understood the material can spot and one who has not cannot. Other recurring signatures are face counts that miss the threshold by an order of magnitude because the generated loop is too coarse, "parameters" that are passed around but never change the geometry, and constructions left open because caps were forgotten. Each is caught by `check()` in one line — so the tool that helps an honest student also raises the floor on what an unreviewed generated submission can get away with.

Third, **the parameter requirement does real work here.** Asking a student to demonstrate their model at three values of its shape parameter and explain why the shape changes as it does is a cheap oral check that generated code rarely survives unaided, because it requires holding the relation between a number and a geometry in one's head.

We do not claim to have solved anything. We note only that a design choice made for pedagogical reasons in 2018 — code only, no modelling software — turns out to be the choice that keeps the assignment meaningful now, and that a validator which makes mechanical requirements self-checkable moves the assessment conversation towards the parts that are about understanding.

## 9.3 What we would tell someone building a similar tool

Three things generalise. Keep the implementation readable at the level of the students who use it, because "read the source" is the best answer to "how does it work" and it is available only if the source is short and dependency-free. Make mechanically checkable requirements self-checkable, because a requirement a student can verify alone never becomes a grading dispute. And when the internal representation must change, keep the old one as a computed view rather than migrating users (Section 4.6): eight years of accumulated student work is worth a hundred lines of adapter.

# 10. Conclusions and future work

`add.py` 2.0 is a single Python file, dependent on nothing but `math` and `random`, that lets students build 3D models of tens or hundreds of thousands of polygons using only code. Its Boolean operations are implemented from scratch: not the textbook BSP formulation, which degenerates to quadratic behaviour on exactly the convex inputs a teaching library produces, but an incremental splitting scheme driven by a uniform spatial hash, a ray-casting classifier with a direction-aligned bucket index and a three-direction fallback for degenerate hits, a four-state classification that handles coplanar overlap, and a three-row keep-set table. On the reference case this is about 70 times faster than the BSP prototype it replaced (0.53 s against 37.7 s) and, unlike the prototype, watertight — because T-junction healing and mesh repair are part of the operation rather than an afterthought.

Around the Booleans, version 2.0 adds repair and validation, `solidify` for one-sided surfaces, three more export formats, tolerant loaders, a dependency-free software renderer, the regular polyhedra with a geodesic sphere and the vertex tools to build on them, a catalogue of named surfaces, classical and generalised Catmull–Clark subdivision — a pure-Python port of the reference implementation, verified against it — Sketchfab-aware export with palette reduction, transparency and image textures, and a vocabulary of 231 descriptive names, each documented in English and Lithuanian with an example that the test suite runs, while keeping every model written for version 1.2 running unchanged through a dual-representation `Mesh` and live string views on the scene.

Several directions are open. **Coplanar face merging** after a Boolean would cut output size substantially and is the most valuable single addition. **Filtered predicates** — floating point first, with an exact fallback in the style of Cherchi et al. [@cherchi2020fast] but written in Python's unbounded integer arithmetic, which is exact for free — could remove the tolerance failures of Section 8.4 without adding a dependency; this is the most interesting work the library still invites, precisely because big integers make an exact filter unusually cheap to write. **An n-ary evaluator** in the spirit of mesh arrangements [@zhou2016mesh] would let a student write one expression over many solids rather than folding pairwise. On the teaching side, we would like to **instrument `check()`** so that, with students' consent, we can see which failure modes are commonest and in what order they are fixed; that data would say far more about what the assignment teaches than the finished models do.

# Acknowledgements

We thank the students of *Algorithms and Data Structures* and *Algorithm Design and Analysis* at the Faculty of Mathematics and Informatics, Vilnius University, whose models — and whose bug reports — shaped every version of this library, and whose 1.2-era scripts served as the backwards-compatibility test suite for version 2.0.

# References

# -*- coding: utf-8 -*-
"""
Prose and translations for the add.py documentation site.

``tools/make_docs.py`` combines this with the docstrings it reads out of
add.py itself, so the reference can never drift away from the code.

Every entry has an English and a Lithuanian version.  The long function
descriptions come from the source and are in English; ``SHORT`` below gives
each function a one-line Lithuanian description for the Lithuanian view.
"""

VERSION = "2.0"

#: Where the project lives.  The module is ``add.py``; the repository and the
#: distribution are called ``add3d`` because plain "add" is taken on PyPI.
REPO_URL = "https://github.com/akatasis/add3d"
DOCS_URL = "https://akatasis.github.io/add3d/"

UI = {
    "title": {"en": "add.py", "lt": "add.py"},
    "tagline": {
        "en": "Build 3D models with nothing but Python code.",
        "lt": "3D modeliai, sukurti vien tik programiniu kodu.",
    },
    "nav_start": {"en": "Start here", "lt": "Nuo ko pradėti"},
    "nav_concepts": {"en": "How it works", "lt": "Kaip tai veikia"},
    "nav_gallery": {"en": "Gallery", "lt": "Galerija"},
    "nav_cookbook": {"en": "Recipes", "lt": "Receptai"},
    "nav_reference": {"en": "Reference", "lt": "Funkcijos"},
    "nav_upgrade": {"en": "From 1.2", "lt": "Iš 1.2 versijos"},
    "nav_faq": {"en": "Questions", "lt": "Klausimai"},
    "search": {"en": "Filter functions...", "lt": "Ieškoti funkcijos..."},
    "lang_note": {
        "en": "",
        "lt": "Išsamūs funkcijų aprašymai kode pateikti angliškai; "
              "čia rasite lietuviškus paaiškinimus ir tuos pačius pavyzdžius.",
    },
    "args": {"en": "Arguments", "lt": "Argumentai"},
    "example_source": {"en": "source", "lt": "kodas"},
    "copy": {"en": "copy", "lt": "kopijuoti"},
    "copied": {"en": "copied", "lt": "nukopijuota"},
    "footer": {
        "en": "add.py %s &middot; MIT licence &middot; "
              "Martynas Sabaliauskas, Vilnius University, "
              "Faculty of Mathematics and Informatics" % VERSION,
        "lt": "add.py %s &middot; MIT licencija &middot; "
              "Martynas Sabaliauskas, Vilniaus universitetas, "
              "Matematikos ir informatikos fakultetas" % VERSION,
    },
}

# --------------------------------------------------------------------------
#  Narrative sections.  Markdown-ish: blank lines separate paragraphs,
#  ``` fences give code blocks, and a line starting with "!" is an image.
# --------------------------------------------------------------------------

SECTIONS = [

("start", {
"en": ("""# Start here

`add.py` is one file. Download it, put it next to your own script, and
`import add`. There is nothing to install and nothing to configure: the
library uses only `math` and `random` from the Python standard library.

```
import add

add.box([0, 0, 0], 2, "red")
add.sphere([3, 0, 0], 1, 20, "blue")
add.cylinder([0, 2, 0], [3, 2, 0], 0.3, 24, "gold")

add.check()
add.save("first_model.off")
```

`check()` prints a short report -- how many polygons, how many colours,
whether the surface is closed. `save()` writes the file; the extension
decides the format (`.off`, `.obj`, `.ply` or `.stl`).

!first_model.png|The three shapes above.

## Only `import add`

`math` and `random` are re-exported by the module, so a model file needs no
other import: `add.sin(t)`, `add.pi`, `add.sqrt(2)`, `add.randint(1, 6)`,
`add.uniform(-1, 1)`, `add.seed(7)` and `add.Random(seed)` all work. (Plain
`import math` still works too, if you prefer it.)

```
import add

for i in range(12):
    a = 2 * add.pi * i / 12
    add.sphere([3 * add.cos(a), 0, 3 * add.sin(a)], 0.4, 8, add.hsv(i / 12))
add.save("ring.off")
```

## Looking at what you made

Open the file in [MeshLab](https://www.meshlab.net/), or render it without
installing anything at all:

```
python3 tools/preview.py first_model.off
```

`tools/preview.py` is a small software renderer that ships with the library
and also uses only the standard library. It writes a PNG.

## Sharing it

Save as `.obj` and you get an `.obj` and a `.mtl` file. Put both in one zip
and upload them to [Sketchfab](https://sketchfab.com) to get a model anyone
can turn around in a browser.
"""),
"lt": ("""# Nuo ko pradėti

`add.py` yra vienas failas. Atsisiųskite jį, padėkite šalia savo programos ir
parašykite `import add`. Nieko diegti nereikia: modulis naudoja tik `math` ir
`random` iš standartinės Python bibliotekos.

```
import add

add.box([0, 0, 0], 2, "red")
add.sphere([3, 0, 0], 1, 20, "blue")
add.cylinder([0, 2, 0], [3, 2, 0], 0.3, 24, "gold")

add.check()
add.save("pirmas_modelis.off")
```

`check()` išspausdina trumpą ataskaitą: kiek daugiakampių, kiek spalvų, ar
paviršius uždaras. `save()` išsaugo failą, o formatą nulemia plėtinys
(`.off`, `.obj`, `.ply` arba `.stl`).

!first_model.png|Trys aukščiau sukurtos figūros.

## Užtenka `import add`

`math` ir `random` eksportuojami iš paties modulio, todėl modelio failui
nereikia jokio kito importo: veikia `add.sin(t)`, `add.pi`, `add.sqrt(2)`,
`add.randint(1, 6)`, `add.uniform(-1, 1)`, `add.seed(7)` ir `add.Random(seed)`.
(Įprastas `import math`, žinoma, irgi tebeveikia.)

```
import add

for i in range(12):
    a = 2 * add.pi * i / 12
    add.sphere([3 * add.cos(a), 0, 3 * add.sin(a)], 0.4, 8, add.hsv(i / 12))
add.save("ziedas.off")
```

## Kaip pažiūrėti, kas gavosi

Atidarykite failą [MeshLab](https://www.meshlab.net/) programa arba
atvaizduokite nieko nediegdami:

```
python3 tools/preview.py pirmas_modelis.off
```

`tools/preview.py` yra nedidelis programinis atvaizdavimo įrankis, einantis
kartu su biblioteka. Jis irgi naudoja tik standartinę biblioteką ir sukuria
PNG paveikslėlį.

## Kaip pasidalinti

Išsaugokite `.obj` formatu -- gausite `.obj` ir `.mtl` failus. Abu sudėkite į
vieną archyvą ir įkelkite į [Sketchfab](https://sketchfab.com): modelį galės
pasukioti bet kas naršyklėje.
"""),
}),

("concepts", {
"en": ("""# How it works

## A model is two lists

A 3D model is a list of points and a list of which points to join into a
face. That is all an OFF file contains:

```
OFF
8 6 0
-1 -1 -1
-1 -1 1
...
4 0 4 5 1 255 0 0
```

The first line says "this is an OFF file". The second gives the number of
vertices, faces and edges. Then come the vertex coordinates, then the faces:
`4 0 4 5 1` means "a quadrilateral joining vertices 0, 4, 5 and 1", and the
three numbers after it are its colour.

Every drawing function in this library does the same thing: it works out some
points and adds some faces.

## Inside and outside

A face has a side. Looking at the model from *outside*, the corners of a face
must run counter-clockwise. Get it backwards and the face is inside out --
renderers draw it black or not at all.

You rarely have to think about this, because the library orients its own
shapes; but it matters when you write `add.polygon(...)` by hand, and it is
why a thin parametric surface has a good side and a bad side. See
[recipes](#cookbook) for the cure.

## The scene, and layers

Drawing functions add to the **current scene**. `layer()` takes the scene
away and hands it to you as a mesh, leaving the scene empty:

```
add.box([0, 0, 0], 1, "red")
brick = add.layer()             # the scene is now empty again
```

A mesh in your hands can be moved, turned, scaled, coloured and combined --
and then put back with `mesh()`:

```
for i in range(10):
    add.mesh(add.move(brick, [i * 1.2, 0, 0]))
```

That is the whole idea: **build once, place many times**.

Transformations never change the mesh you give them; they return a new one.
So you can chain them and keep the original:

```
tilted = add.rotateY(add.zoom(brick, 0.5), 0.4)
```

## One trap, and the tool for it

`layer()` takes away *everything* drawn so far -- including things you drew
earlier for another purpose. Inside a function that builds a part, start with
`push()` and finish with `pop()`:

```
def wheel(r):
    add.push()                  # the rest of the scene is put aside
    add.cylinder([0, 0, -0.2], [0, 0, 0.2], r, 32, "black")
    add.torus([0, 0, 0], r, 0.1, 40, 16, "grey")
    return add.pop()            # and comes back
```
"""),
"lt": ("""# Kaip tai veikia

## Modelis -- tai du sąrašai

3D modelis yra taškų sąrašas ir sąrašas, kurie taškai jungiami į sieną.
Būtent tai ir yra OFF failas:

```
OFF
8 6 0
-1 -1 -1
-1 -1 1
...
4 0 4 5 1 255 0 0
```

Pirma eilutė sako, kad tai OFF failas. Antroje -- viršūnių, sienų ir briaunų
skaičius. Toliau eina viršūnių koordinatės, paskui sienos: `4 0 4 5 1` reiškia
„keturkampis, jungiantis viršūnes 0, 4, 5 ir 1", o trys skaičiai po to -- jo
spalva.

Visos šios bibliotekos braižymo funkcijos daro tą patį: apskaičiuoja taškus ir
prideda sienas.

## Vidinė ir išorinė siena

Siena turi pusę. Žiūrint į modelį *iš išorės*, sienos viršūnės turi būti
išdėstytos prieš laikrodžio rodyklę. Jei atvirkščiai -- siena bus išversta, ir
atvaizdavimo programos ją nupieš juodą arba visai nerodys.

Apie tai retai tenka galvoti, nes biblioteka savo figūras orientuoja pati. Bet
tai svarbu, kai `add.polygon(...)` rašote patys, ir būtent dėl to plonas
parametrinis paviršius turi gerąją ir blogąją pusę. Vaistus rasite
[receptuose](#cookbook).

## Scena ir sluoksniai

Braižymo funkcijos prideda figūras į **dabartinę sceną**. `layer()` sceną
paima ir grąžina ją kaip modelį, o scena lieka tuščia:

```
add.box([0, 0, 0], 1, "red")
plyta = add.layer()             # scena vėl tuščia
```

Rankose turimą modelį galima stumdyti, sukti, keisti mastelį, perdažyti ir
jungti, o paskui grąžinti į sceną su `mesh()`:

```
for i in range(10):
    add.mesh(add.move(plyta, [i * 1.2, 0, 0]))
```

Tai ir yra visa esmė: **sukurk vieną kartą, padėk daug kartų**.

Transformacijos niekada nekeičia joms perduoto modelio -- jos grąžina naują.
Todėl jas galima jungti į grandinę ir originalas išlieka:

```
pakreipta = add.rotateY(add.zoom(plyta, 0.5), 0.4)
```

## Viena spąstų vieta ir įrankis jai

`layer()` paima *viską*, kas nupiešta iki tol -- taip pat ir tai, ką piešėte
anksčiau visai kitam tikslui. Funkcijoje, kuri kuria atskirą detalę, pradėkite
nuo `push()` ir baikite `pop()`:

```
def ratas(r):
    add.push()                  # likusi scena padedama į šalį
    add.cylinder([0, 0, -0.2], [0, 0, 0.2], r, 32, "black")
    add.torus([0, 0, 0], r, 0.1, 40, 16, "grey")
    return add.pop()            # ir sugrįžta
```
"""),
}),

("cookbook", {
"en": ("""# Recipes

## My surface is black from one side

A parametric surface is a sheet with no thickness, so it has a front and a
back. Two fixes, both one keyword:

```
add.parametric(f, 0, 1, 40, 0, 1, 40, "red", double_sided=True)   # cheap
add.parametric(f, 0, 1, 40, 0, 1, 40, "red", thickness=0.1)       # a solid
```

`double_sided` adds a reversed copy of every face. `thickness` makes a real
solid with a wall -- watertight, printable, correct from every angle.

!two_sided.png|The same saddle: plain sheet, double sided, and solid.

## I need a hole

```
add.cuboid([0, 0, 0], [4, 1, 4], "brown")
plate = add.layer()
add.cylinder([0, -1, 0], [0, 1, 0], 0.6, 32, "black")
drill = add.layer()
add.mesh(add.difference(plate, drill))
```

Booleans want closed solids on both sides. `add.check()` will tell you
whether yours is closed. The cut surface takes the colour of the tool that
cut it; pass `color=` to `difference` to override that.

## I need 10000 polygons

You almost certainly already have them -- a `sphere(c, r, 30, ...)` alone is
5400. If not, the honest ways are more detail (`grid_u`, `grid_v`, `k`) or
more repetition. `add.check()` counts them for you.

## I want the shape to depend on a parameter

Put the number at the top of the file and use it everywhere:

```
PETALS = 7
for i in range(PETALS):
    ...
```

Then changing one number changes the whole model, which is exactly what the
assignment asks for.

## My model flickers, or has stray faces inside it

Flicker ("z-fighting") is two faces in exactly the same plane, facing the
same way: the side of a beam running into a wall, two boxes of the same
height crossing, a tile laid on a floor of the same colour. The viewer
cannot decide which is in front and shows a little of each. Stray faces
are the other case: two solids touch, and each keeps its own wall buried
where nobody sees it.

`add.py` checks the model for the three things that cause this --
repeated vertices, repeated or overlapping faces, and repeated edges --
and repairs them: `check()` reports them, `clean()` welds vertices on one
spot, removes repeated and buried faces, and cuts the smaller of two
overlapping faces back so that the larger one alone covers the shared
patch. Where two solids stand on each other (a chest on a floor) the
patch they share is cut out of both, as a union would, and the model
stays watertight. `save()` and `stream()` do the same on the way to the
file, so a model needs nothing extra; `add.save("x.obj", clean=False)`
writes it exactly as drawn. The repair works on what it is given: a
model written in parts with `stream()` is repaired part by part, so two
parts that share a plane -- a floor laid in one part under a roof drawn
in another -- must be kept apart by the model itself.

```
add.check()                              # "!! overlapping faces  146"
model, report = add.clean(add.layer(), report=True)
print(report["faces_cut"], add.overlaps(model))    # 106, 0
add.mesh(model)
```

## I want a vase / chess piece / bottle

Spin a profile: `revolve(profile, A, B, t0, t1, steps, k, colour)` where
`profile(t)` returns `[radius, height]`.

```
def vase(t):
    return [1 + 0.4 * add.sin(3 * t), t]

add.revolve(vase, [0, 0, 0], [0, 1, 0], 0, 4, 60, 40, "teal")
```

!lathe.png|Twelve shapes, each a single profile function.

## I want to bend or twist something

```
M = add.twist(M, 0.5)                   # a corkscrew
M = add.taper(M, -0.2)                  # thinner as it rises
M = add.bend(M, 0.3)                    # into an arc
M = add.deform(M, lambda p: [p[0], p[1] + add.sin(p[0]), p[2]])
```

`deform` takes any function you like, so it can do anything the others cannot.

## I want a rainbow

```
M = add.color_by(M, lambda p: add.hsv(p[1] / 10.0))
```

`color_by` calls your function with the centre of each face.

## I want to paint a surface with a function

Every surface maker accepts a *colour function* instead of a colour. It is
called once per cell with the surface's own two parameters, so stripes,
chequerboards, gradients and maps cost one `lambda`:

```
add.parametric(f, 0, 1, 40, 0, 1, 40, color=lambda u, v: add.hsv(u))
add.revolve(vase, A, B, 0, 4, 60, 40, color=lambda t, a: "red" if int(t) % 2 else "white")
add.sweep(square, path, 0, 1, 60, color=lambda t, j: ["red", "green", "blue", "gold"][j])
add.curve(spiral, 0, 20, 300, 12, 0.2, color=lambda t, a: add.hsv(t / 20))
add.grid([0, 0, 0], [10, 10], 40, 40, color=lambda x, z: "sky" if hills(x, z) < 0 else "green", height=hills)
```

`revolve` passes the profile parameter and the angle, `sweep` the path
parameter and the index of the profile edge, `curve` and `polyline` the
parameter and the angle around the tube. For a mesh you already have,
`color_by(M, fn)` paints by the position of each face.

!solar_system.png|Planets are lathes with colour functions: bands, a red spot, continents.

## I am building a machine, or a figure

Build every part around the origin, between `push()` and `pop()`, then
place it. `beam(A, B, w, h)` gives you a bar between two points;
`aim(M, direction)` turns a part so its axis points somewhere;
`rotate_point` tells you where a point on a wheel ends up:

```
def wheel(r):
    add.push()
    add.wheel([0, 0, 0], r, 0.2, "black", axis=[0, 0, 1], spokes=10)
    return add.pop()

pin = add.rotate_point([x + 0.5, y, z], [0, 0, 1], ANGLE, [x, y, z])   # on the wheel
add.beam(pin, piston, 0.08, 0.12, "silver")                              # the rod follows
arm = add.aim(arm, add.direction(shoulder, hand))                        # point the arm
add.mesh(add.move(arm, shoulder))
```

`array_mirror` gives you the other side of a symmetric machine for free.

!locomotive.png|Wheels, rods and cranks that fit for any angle of the wheels.

## I want a landscape with things on it

A `grid` with a height function is the ground; `random_points` with the
same function returns spots that lie *on* it; `scatter` puts copies of a
part there, each turned and sized at random; `along` strings copies along
a path. `tree`, `bricks`, `roof`, `arch`, `stairs`, `column` are the parts
that most models turn out to need.

```
add.grid([0, 0, 0], [40, 40], 80, 80, paint, hills, thickness=0.3)
spots = add.random_points(30, [-15, 0, -15], [15, 0, 15], seed=1, height=hills)
add.push(); add.tree([0, 0, 0], 3, seed=1); one = add.pop()
add.mesh(add.scatter(one, spots, seed=1, scale=(0.7, 1.4)))
```

!lighthouse.png|Island, tower, house, palms, rocks and a boat -- one script.

## I want to write on the model

`text(string, at, size, color=...)` draws a label from a built-in stroke
font: letters, digits, punctuation and the Lithuanian letters ĄČĘĖĮŠŲŪŽ.
`u` and `v` set the writing and up directions, so a label can stand on a
wall or lie flat on the ground:

```
add.text("MALŪNAS 2026", [0, 0, 0], 1.0, color="navy")                  # upright
add.text("SALA", [0, 0.01, 0], 1.0, color="white", u=[1, 0, 0], v=[0, 0, -1])   # on the floor
```

## I want a block world, or pixel art

`pixels` turns strings into a wall of coloured cubes; `heightmap` turns a
table of integers into columns of cubes and builds only the visible faces:

```
add.pixels([".r.r.", "rrrrr", ".rrr.", "..r.."], 0.5)                         # a heart
H = [[int(3 + 2 * add.sin(i / 3) * add.cos(j / 3)) for j in range(30)] for i in range(30)]
add.heightmap(H, 0.5, color=lambda i, j, k: "sky" if j < 2 else "green")
```

!voxel_island.png|A height table, a colour function, a flag from strings.

## I want a curve from an equation of motion

`flow(field, p0, dt, steps)` integrates a vector field (Runge-Kutta) and
returns the points; `trace` draws them as a tube; `polyline` draws any
list of points as a tube, with `smooth=` rounding the corners:

```
def lorenz(p):
    x, y, z = p
    return [10 * (y - x), x * (28 - z) - y, x * y - 8 / 3 * z]

add.trace(lorenz, [1, 1, 1], 0.006, 6000, r=0.3, color=lambda t, a: add.hsv(t))
add.wireframe(add.polyhedron("icosahedron"), 0.03)          # every edge as a bar
```

!vector_fields.png|Lorenz, Rössler, an arrow field, beads on a helix.

## I want a regular polyhedron, a football, a geodesic dome

The five Platonic solids are one call each (`tetrahedron`, `cube` via
`polyhedron("cube")`, `octahedron`, `dodecahedron`, `icosahedron`), all
centred so that the average of their vertices is exactly the centre, and
`polyhedron_points` gives just the coordinates. `truncate` cuts the corners
off (the icosahedron becomes the football), `dual` swaps faces and
vertices, `refine` + `spherify` turns any of them into a geodesic dome, and
`sphere` itself is now such a dome: an icosahedron split and pushed out
onto the sphere, all triangles nearly equal.

```
ico = add.make(add.icosahedron, [0, 0, 0], 3, "white")
ball = add.truncate(ico, 1 / 3.0, "black")               # 12 pentagons, 20 hexagons
ball = add.color_by_sides(ball, {5: "black", 6: "white"})
add.mesh(add.smooth(ball, 12))                           # and round it off
add.mesh(add.spherify(add.refine(add.make(add.octahedron, [7, 0, 0], 3), 3)))
```

!football.png|A football from the vertices of an icosahedron, flat and smoothed.

## I want to round a shape off

Build a coarse shape -- a box with a corner pulled out, a letter from a few
blocks, a dodecahedron -- and treat it as the *control net* of a smooth
surface. `catmull_clark(M, steps)` is the classical subdivision; `smooth(M,
n)` is the generalised algorithm: `n` cells on every control edge for *any*
`n`, all the new vertices exactly on the smooth limit surface, evenly sized
cells near the odd corners, and every cell keeps the colour of the face it
came from.

```
add.box([0, 0, 0], 2, "gold")
block = add.layer()
i = add.nearest_vertex(block, [1, 1, 1])
block = add.set_vertex(block, i, [2.5, 2.5, None])      # move one corner, keep z
add.mesh(add.smooth(block, 8))
```

!smooth_shapes.png|A pulled box rounded off; one prism with n = 1 ... 7; a flat star with and without the uniform grid.

## I want a Klein bottle

Twenty-five classical surfaces are in the catalogue: `add.surface_names()`
lists them and `add.surface(name, center, size, grid, color)` draws one,
scaled to `size`. `add.surface_function(name)` gives you the bare formula
for `parametric` when you want your own range or colouring.

```
add.surface("klein_bottle", [0, 0, 0], 4, 120, "teal")
add.surface("dini", [6, 0, 0], 4, color=lambda u, v: add.hsv(u / 12))
```

!surface_zoo.png|All twenty-five named surfaces.

## I want to know a vertex's neighbours

`neighbors(M, i)` (in order around the vertex), `valence(M, i)`,
`mean_neighbor_distance(M, i)`, `edges(M)`, `mean_edge_length(M)`,
`vertex_normal`, `face_center`, `face_normal`, `boundary_loops` -- the
questions you need answered to build on the vertices of an icosahedron or
a dodecahedron:

```
ico = add.make(add.icosahedron, [0, 0, 0], 2)
for i, p in enumerate(ico.V):
    n = add.vertex_normal(ico, i)
    tip = [p[a] + n[a] for a in range(3)]
    add.cone(p, tip, 0.25 * add.mean_neighbor_distance(ico, i), 8,
             "red" if add.valence(ico, i) == 5 else "blue")
```

!vertex_tools.png|A buckyball, a spiky virus, a stellated dodecahedron, a cage with its dual.

## I want to upload it to Sketchfab

Sketchfab takes `.obj` + `.mtl` (zip them together). Two limits matter:
the file size (100 MB on the free plan -- the course asks for 50) and the
number of materials, which is the number of distinct colours (100 at most;
50 to be safe). `check()` reports both. Gradients easily make thousands of
shades; `limit_colors(M, 50)` groups them, or `save("x.obj", colors=50)`
does it while saving, and `obj_size(M)` tells the size before writing.

```
model = add.limit_colors(add.layer(), 50)
add.check(model)
add.save("model.obj", model)
```

## I want glass, or a picture on a wall

`transparent(colour, alpha)` is a see-through colour that works wherever a
colour does; `opacity(M, alpha)` makes a finished part see-through. Both go
into the `.mtl` file (`d`). `texture(M, "picture.png", mapping)` wraps an
image around a part (`map_Kd`), with box, planar, spherical or cylindrical
mapping; `write_png` writes a picture you computed yourself. `.off` files
keep plain colours, so old models are unchanged.

```
glass = add.transparent("sky", 0.35)
add.cuboid([0, 1.5, 2], [2, 1.2, 0.05], glass)                 # a window
wall = add.make(add.cuboid, [0, 1.5, 0], [6, 3, 0.3])
add.mesh(add.texture(wall, "bricks.png", "box", scale=1.5))
add.save("house.obj")                                          # + house.mtl
```

!glass_and_textures.png|A fish tank, a brick house with glass windows and a textured globe.

## My model is bigger than the memory of the computer

`save` keeps the whole model in memory, which is fine up to a few million
faces. A model with every brick, cobblestone and roof tile as its own
piece can run to hundreds of megabytes -- so build it in parts and hand
each part to a *stream* as soon as it is finished: `stream("castle.obj")`
returns a `Stream`, `out.add()` writes the scene and clears it,
`out.close()` writes the `.mtl` (or fills in the OFF header). Every part
is tidied on the way (welded, no repeated, buried or overlapping faces),
`precision=4` keeps the coordinates short, and `out.faces`, `out.bytes`
and `out.materials` count as you go, so the limits can be checked before
the file is complete. The same parts can go to two streams -- an `.off`
and an `.obj` -- at once.

```
out = add.stream("castle.obj", precision=4)
for k in range(8):
    wall_segment(k)                    # thousands of bricks
    out.add()                          # written now, memory freed
out.add(add.make(add.tree, [0, 0, 0], 5))
out.close()
print(out.faces, "faces,", out.bytes / 1e6, "MB,", len(out.materials), "colours")
```

!castle.png|The castle of example 46, written streaming to castle.off (about 400 MB) and castle.obj: no textures, every stone a polygon; the .obj is under 100 MB once 7-Zip has compressed it.
"""),
"lt": ("""# Receptai

## Mano paviršius iš vienos pusės juodas

Parametrinis paviršius yra lakštas be storio, todėl turi priekį ir nugarą. Du
sprendimai, abu -- vienas raktažodis:

```
add.parametric(f, 0, 1, 40, 0, 1, 40, "red", double_sided=True)   # pigiai
add.parametric(f, 0, 1, 40, 0, 1, 40, "red", thickness=0.1)       # tikras kūnas
```

`double_sided` prideda apverstą kiekvienos sienos kopiją. `thickness` sukuria
tikrą kūną su sienele: uždarą, spausdinamą, teisingą iš visų pusių.

!two_sided.png|Tas pats balnas: paprastas lakštas, dvipusis ir tūrinis.

## Reikia skylės

```
add.cuboid([0, 0, 0], [4, 1, 4], "brown")
plokste = add.layer()
add.cylinder([0, -1, 0], [0, 1, 0], 0.6, 32, "black")
grezlas = add.layer()
add.mesh(add.difference(plokste, grezlas))
```

Loginėms operacijoms reikia uždarų kūnų iš abiejų pusių. `add.check()`
pasakys, ar jūsiškis uždaras. Naujai atsiveręs paviršius perima įrankio, kuris
pjovė, spalvą; ją galima pakeisti `difference(..., color=...)`.

## Reikia 10000 daugiakampių

Greičiausiai jų jau turite: vien `sphere(c, r, 30, ...)` duoda 5400. Jei ne --
sąžiningi būdai yra didesnis detalumas (`grid_u`, `grid_v`, `k`) arba daugiau
pasikartojimų. `add.check()` juos suskaičiuoja už jus.

## Noriu, kad forma priklausytų nuo parametro

Skaičių aprašykite failo pradžioje ir naudokite jį visur:

```
ZIEDLAPIU = 7
for i in range(ZIEDLAPIU):
    ...
```

Tada vieno skaičiaus pakeitimas pakeičia visą modelį -- to ir prašo užduotis.

## Mano modelis mirga arba jo viduje liko nereikalingų sienų

Mirgėjimas („z-fighting") -- tai dvi sienos lygiai toje pačioje plokštumoje,
žiūrinčios ta pačia kryptimi: sija, įeinanti į sieną, du vienodo aukščio
susikertantys blokai, plytelė ant tokios pat spalvos grindų. Peržiūros
programa negali nuspręsti, kuri priekyje, ir rodo po truputį abiejų.
Nereikalingos sienos -- kitas atvejis: du kūnai liečiasi ir kiekvienas
pasilieka savo sienelę, palaidotą ten, kur jos niekas nemato.

`add.py` patikrina modelį dėl trijų šito priežasčių -- pasikartojančių
viršūnių, pasikartojančių ar persidengiančių sienų ir pasikartojančių
briaunų -- ir jas taiso: `check()` apie jas praneša, `clean()` suklijuoja
viename taške esančias viršūnes, pašalina pasikartojančias ir palaidotas
sienas, o mažesnę iš dviejų persidengiančių apkerpa, kad bendrą lopą dengtų
tik didesnioji. Kur du kūnai stovi vienas ant kito (skrynia ant grindų),
bendras lopas iškerpamas iš abiejų, kaip padarytų sąjunga, ir modelis
lieka sandarus. `save()` ir `stream()` tą patį padaro rašydami failą, todėl
modeliui nieko papildomo nereikia; `add.save("x.obj", clean=False)` įrašo
lygiai taip, kaip nupiešta. Taisoma tai, kas paduota: dalimis per
`stream()` rašomas modelis taisomas dalis po dalies, tad dvi dalys toje
pačioje plokštumoje -- grindys vienoje dalyje po stogu iš kitos -- turi
būti atskirtos paties modelio.

```
add.check()                              # "!! overlapping faces  146"
modelis, ataskaita = add.clean(add.layer(), report=True)
print(ataskaita["faces_cut"], add.overlaps(modelis))    # 106, 0
add.mesh(modelis)
```

## Noriu vazos / šachmatų figūros / butelio

Sukite profilį: `revolve(profilis, A, B, t0, t1, steps, k, spalva)`, kur
`profilis(t)` grąžina `[spindulys, aukštis]`.

```
def vaza(t):
    return [1 + 0.4 * add.sin(3 * t), t]

add.revolve(vaza, [0, 0, 0], [0, 1, 0], 0, 4, 60, 40, "teal")
```

!lathe.png|Dvylika formų, kiekviena -- viena profilio funkcija.

## Noriu ką nors sulenkti ar susukti

```
M = add.twist(M, 0.5)                   # kaip kamščiatraukis
M = add.taper(M, -0.2)                  # kylant plonėja
M = add.bend(M, 0.3)                    # į lanką
M = add.deform(M, lambda p: [p[0], p[1] + add.sin(p[0]), p[2]])
```

`deform` priima bet kokią jūsų funkciją, todėl padaro tai, ko kiti negali.

## Noriu vaivorykštės

```
M = add.color_by(M, lambda p: add.hsv(p[1] / 10.0))
```

`color_by` iškviečia jūsų funkciją su kiekvienos sienos centru.

## Noriu nuspalvinti paviršių funkcija

Kiekviena paviršių kurianti funkcija vietoj spalvos priima *spalvos funkciją*.
Ji kviečiama kiekvienai langelio (sienos) porai paviršiaus parametrų, todėl
juostos, šachmatų lenta, gradientai ir žemėlapiai kainuoja vieną `lambda`:

```
add.parametric(f, 0, 1, 40, 0, 1, 40, color=lambda u, v: add.hsv(u))
add.revolve(vaza, A, B, 0, 4, 60, 40, color=lambda t, a: "red" if int(t) % 2 else "white")
add.sweep(kvadratas, kelias, 0, 1, 60, color=lambda t, j: ["red", "green", "blue", "gold"][j])
add.curve(spirale, 0, 20, 300, 12, 0.2, color=lambda t, a: add.hsv(t / 20))
add.grid([0, 0, 0], [10, 10], 40, 40, color=lambda x, z: "sky" if kalvos(x, z) < 0 else "green", height=kalvos)
```

`revolve` perduoda profilio parametrą ir kampą, `sweep` -- kelio parametrą ir
profilio briaunos numerį, `curve` bei `polyline` -- parametrą ir kampą aplink
vamzdį. Jau turimą modelį nuspalvina `color_by(M, fn)` pagal kiekvienos
sienos padėtį.

!solar_system.png|Planetos -- sukiniai su spalvų funkcijomis: juostos, raudonoji dėmė, žemynai.

## Kuriu mechanizmą arba figūrą

Kiekvieną detalę kurkite aplink koordinačių pradžią tarp `push()` ir `pop()`,
o tada padėkite į vietą. `beam(A, B, w, h)` duoda siją tarp dviejų taškų,
`aim(M, kryptis)` pasuka detalę taip, kad jos ašis rodytų reikiama kryptimi,
`rotate_point` pasako, kur atsidurs taškas ant pasukto rato:

```
def ratas(r):
    add.push()
    add.wheel([0, 0, 0], r, 0.2, "black", axis=[0, 0, 1], spokes=10)
    return add.pop()

kaistis = add.rotate_point([x + 0.5, y, z], [0, 0, 1], KAMPAS, [x, y, z])   # ant rato
add.beam(kaistis, stumoklis, 0.08, 0.12, "silver")                          # trauklė seka
ranka = add.aim(ranka, add.direction(petys, plastaka))                      # nukreipti ranką
add.mesh(add.move(ranka, petys))
```

`array_mirror` nemokamai duoda kitą simetriško mechanizmo pusę.

!locomotive.png|Ratai, trauklės ir alkūnės, kurios tinka esant bet kokiam ratų kampui.

## Noriu kraštovaizdžio su daiktais ant jo

`grid` su aukščio funkcija -- tai žemė; `random_points` su ta pačia funkcija
grąžina taškus, gulinčius *ant* jos; `scatter` ten padeda detalės kopijas,
kiekvieną atsitiktinai pasuktą ir padidintą; `along` išdėsto kopijas išilgai
kelio. `tree`, `bricks`, `roof`, `arch`, `stairs`, `column` -- detalės, kurių
prireikia daugumai modelių.

```
add.grid([0, 0, 0], [40, 40], 80, 80, spalva, kalvos, thickness=0.3)
vietos = add.random_points(30, [-15, 0, -15], [15, 0, 15], seed=1, height=kalvos)
add.push(); add.tree([0, 0, 0], 3, seed=1); vienas = add.pop()
add.mesh(add.scatter(vienas, vietos, seed=1, scale=(0.7, 1.4)))
```

!lighthouse.png|Sala, bokštas, namas, palmės, akmenys ir valtis -- viena programa.

## Noriu užrašo ant modelio

`text(tekstas, kur, dydis, color=...)` nubraižo užrašą įmontuotu šriftu:
raidės, skaitmenys, skyryba ir lietuviškos raidės ĄČĘĖĮŠŲŪŽ. `u` ir `v`
nurodo rašymo ir aukštyn kryptis, todėl užrašas gali stovėti ant sienos arba
gulėti ant žemės:

```
add.text("MALŪNAS 2026", [0, 0, 0], 1.0, color="navy")                  # stačias
add.text("SALA", [0, 0.01, 0], 1.0, color="white", u=[1, 0, 0], v=[0, 0, -1])   # ant grindų
```

## Noriu kubelių pasaulio arba pikselinio piešinio

`pixels` paverčia eilutes spalvotų kubelių siena; `heightmap` sveikųjų
skaičių lentelę paverčia kubelių stulpeliais ir sukuria tik matomas sienas:

```
add.pixels([".r.r.", "rrrrr", ".rrr.", "..r.."], 0.5)                         # širdelė
H = [[int(3 + 2 * add.sin(i / 3) * add.cos(j / 3)) for j in range(30)] for i in range(30)]
add.heightmap(H, 0.5, color=lambda i, j, k: "sky" if j < 2 else "green")
```

!voxel_island.png|Aukščių lentelė, spalvos funkcija, vėliava iš eilučių.

## Noriu kreivės iš judėjimo lygties

`flow(laukas, p0, dt, žingsniai)` integruoja vektorinį lauką (Rungės ir Kutos
metodu) ir grąžina taškus; `trace` juos nubraižo kaip vamzdį; `polyline`
nubraižo bet kokį taškų sąrašą kaip vamzdį, o `smooth=` suapvalina kampus:

```
def lorenz(p):
    x, y, z = p
    return [10 * (y - x), x * (28 - z) - y, x * y - 8 / 3 * z]

add.trace(lorenz, [1, 1, 1], 0.006, 6000, r=0.3, color=lambda t, a: add.hsv(t))
add.wireframe(add.polyhedron("icosahedron"), 0.03)          # kiekviena briauna -- strypelis
```

!vector_fields.png|Lorencas, Rösleris, rodyklių laukas, karoliukai ant spiralės.

## Noriu taisyklingojo briaunainio, futbolo kamuolio, geodezinio kupolo

Penki Platono kūnai -- po vieną kvietimą (`tetrahedron`, `cube` per
`polyhedron("cube")`, `octahedron`, `dodecahedron`, `icosahedron`), visi
sucentruoti taip, kad viršūnių vidurkis būtų lygiai centras, o
`polyhedron_points` duoda vien koordinates. `truncate` nupjauna kampus
(ikosaedras virsta futbolo kamuoliu), `dual` sukeičia sienas ir viršūnes,
`refine` + `spherify` iš bet kurio padaro geodezinį kupolą, o pati `sphere`
dabar ir yra toks kupolas: ikosaedras, padalytas ir išstumtas ant sferos,
visi trikampiai beveik lygūs.

```
ico = add.make(add.icosahedron, [0, 0, 0], 3, "white")
ball = add.truncate(ico, 1 / 3.0, "black")               # 12 penkiakampių, 20 šešiakampių
ball = add.color_by_sides(ball, {5: "black", 6: "white"})
add.mesh(add.smooth(ball, 12))                           # ir suapvaliname
add.mesh(add.spherify(add.refine(add.make(add.octahedron, [7, 0, 0], 3), 3)))
```

!football.png|Futbolo kamuolys iš ikosaedro viršūnių: plokščias ir suapvalintas.

## Noriu suapvalinti formą

Sukurkite grubią formą -- dėžę su ištrauktu kampu, raidę iš kelių blokų,
dodekaedrą -- ir laikykite ją glotnaus paviršiaus *kontroliniu tinklu*.
`catmull_clark(M, steps)` yra klasikinis dalijimas; `smooth(M, n)` --
apibendrintas algoritmas: ant kiekvienos kontrolinės briaunos `n` langelių
*bet kokiam* `n`, visos naujos viršūnės tiksliai ant ribinio paviršiaus,
vienodo dydžio langeliai prie ypatingųjų kampų, o kiekvienas langelis
išlaiko sienos, iš kurios kilo, spalvą.

```
add.box([0, 0, 0], 2, "gold")
block = add.layer()
i = add.nearest_vertex(block, [1, 1, 1])
block = add.set_vertex(block, i, [2.5, 2.5, None])      # pastumiame kampą, z paliekame
add.mesh(add.smooth(block, 8))
```

!smooth_shapes.png|Ištraukto kampo dėžė suapvalinta; ta pati prizmė su n = 1 ... 7; plokščia žvaigždė su tolygiu tinklu ir be jo.

## Noriu Kleino butelio

Kataloge -- dvidešimt penki klasikiniai paviršiai: `add.surface_names()`
juos išvardija, `add.surface(vardas, centras, dydis, tinklelis, spalva)`
nupiešia, sumastelintą iki `size`. `add.surface_function(vardas)` duoda
gryną formulę funkcijai `parametric`, kai norite savos srities ar spalvinimo.

```
add.surface("klein_bottle", [0, 0, 0], 4, 120, "teal")
add.surface("dini", [6, 0, 0], 4, color=lambda u, v: add.hsv(u / 12))
```

!surface_zoo.png|Visi dvidešimt penki vardiniai paviršiai.

## Noriu žinoti viršūnės kaimynes

`neighbors(M, i)` (eilės tvarka aplink viršūnę), `valence(M, i)`,
`mean_neighbor_distance(M, i)`, `edges(M)`, `mean_edge_length(M)`,
`vertex_normal`, `face_center`, `face_normal`, `boundary_loops` -- atsakymai
į klausimus, kurių reikia statant ant ikosaedro ar dodekaedro viršūnių:

```
ico = add.make(add.icosahedron, [0, 0, 0], 2)
for i, p in enumerate(ico.V):
    n = add.vertex_normal(ico, i)
    tip = [p[a] + n[a] for a in range(3)]
    add.cone(p, tip, 0.25 * add.mean_neighbor_distance(ico, i), 8,
             "red" if add.valence(ico, i) == 5 else "blue")
```

!vertex_tools.png|Fulerenas, spygliuotas virusas, žvaigždinis dodekaedras, narvas su dualiuoju kūnu viduje.

## Noriu įkelti į Sketchfab

Sketchfab priima `.obj` + `.mtl` (suarchyvuokite kartu). Svarbūs du
apribojimai: failo dydis (nemokamame plane 100 MB -- kursas prašo 50) ir
medžiagų skaičius, kuris lygus skirtingų spalvų skaičiui (daugiausia 100;
50 saugu). `check()` praneša abu. Gradientai lengvai padaro tūkstančius
atspalvių; `limit_colors(M, 50)` juos sugrupuoja, `save("x.obj",
colors=50)` tai padaro įrašant, o `obj_size(M)` pasako dydį dar prieš
rašant failą.

```
model = add.limit_colors(add.layer(), 50)
add.check(model)
add.save("modelis.obj", model)
```

## Noriu stiklo arba paveikslo ant sienos

`transparent(spalva, alpha)` -- permatoma spalva, tinkanti visur, kur
tinka spalva; `opacity(M, alpha)` padaro permatomą jau sukurtą detalę.
Abu įrašomi į `.mtl` failą (`d`). `texture(M, "paveikslas.png",
mapping)` apvynioja detalę paveikslėliu (`map_Kd`) -- dėžės, plokštumos,
sferos ar cilindro atvaizdžiu; `write_png` įrašo patį paskaičiuotą
paveikslėlį. `.off` failuose lieka paprastos spalvos, todėl seni modeliai
nesikeičia.

```
glass = add.transparent("sky", 0.35)
add.cuboid([0, 1.5, 2], [2, 1.2, 0.05], glass)                 # langas
wall = add.make(add.cuboid, [0, 1.5, 0], [6, 3, 0.3])
add.mesh(add.texture(wall, "bricks.png", "box", scale=1.5))
add.save("namas.obj")                                          # + namas.mtl
```

!glass_and_textures.png|Akvariumas, plytų namas su stiklo langais ir tekstūruotas gaublys.

## Mano modelis didesnis už kompiuterio atmintį

`save` laiko visą modelį atmintyje -- to užtenka iki kelių milijonų sienų.
Modelis, kuriame kiekviena plyta, grindinio akmuo ir stogo čerpė yra
atskira detalė, siekia šimtus megabaitų, todėl jį reikia kurti dalimis ir
kiekvieną baigtą dalį iš karto atiduoti *srautui*: `stream("pilis.obj")`
grąžina `Stream`, `out.add()` įrašo sceną ir ją išvalo, `out.close()`
įrašo `.mtl` (arba užpildo OFF antraštę). Kiekviena dalis pakeliui
sutvarkoma (suklijuota, be pasikartojančių, palaidotų ir persidengiančių
sienų), `precision=4` trumpina koordinates, o `out.faces`, `out.bytes` ir
`out.materials` skaičiuoja rašant, todėl ribas galima tikrinti dar
nebaigus failo. Tos pačios dalys gali eiti į du srautus -- `.off` ir
`.obj` -- iš karto.

```
out = add.stream("pilis.obj", precision=4)
for k in range(8):
    siena(k)                           # tūkstančiai plytų
    out.add()                          # įrašyta dabar, atmintis laisva
out.add(add.make(add.tree, [0, 0, 0], 5))
out.close()
print(out.faces, "sienų,", out.bytes / 1e6, "MB,", len(out.materials), "spalvų")
```

!castle.png|46 pavyzdžio pilis, rašyta srautu į castle.off (apie 400 MB) ir castle.obj: be tekstūrų, kiekvienas akmuo -- daugiakampis; .obj, suglaudintas 7-Zip, telpa į 100 MB.
"""),
}),

("upgrade", {
"en": ("""# Coming from add.py 1.2

**Everything still works.** Models written for 1.2 run on 2.0 unchanged and
produce the same faces; twelve of them are in `tests/legacy/` and the test
suite checks exactly that on every commit. (The one deliberate change:
`sphere` is now made of triangles, so a model with spheres has more, and
different, faces than before -- see below.)

The old names are all still there. New code can use the clearer ones:

| add.py 1.2 | add.py 2.0 | what it is |
|---|---|---|
| `cube(c, e, RGB)` | `box` | a cube |
| `rectangle3D(c, e, RGB)` | `cuboid` | a rectangular block |
| `cube2(c, e, b, RGB)` | `frame` | a hollow cube of bars |
| `cylinder2(A, B, r, k, RGB)` | `tube` | a cylinder with no lids |
| `cylinder3(A, B, r, k, RGB)` | `cup` | closed at one end |
| `cone2(A, B, r, k, RGB)` | `cone_open` | the slanted wall only |
| `newface(A, RGB)` | `polygon` | one flat face |
| `spin3D(A, B, S, ...)` | `revolve` | a lathe |
| `off(path)` | `save(path)` | any of .off, .obj, .ply, .stl |
| `zoom(M, s)` | `zoom` *(unchanged)* | scale |

`add.vertices` and `add.faces` still look and behave like the old lists of
strings, and `layer()` still returns something you can index as `M[0]` and
`M[1]`. `example1()` ... `example8()` live in `examples/20_classic_1_2.py`,
and `examples/32_old_names.py` is a whole model written in the 1.2
vocabulary.

## What is new in 2.0

* **Boolean operations** written from scratch: `union`, `intersect`,
  `difference`, `symmetric_difference`, and the cheap `cut`.
* **Only `import add`**: `math` and `random` are re-exported.
* **The five regular polyhedra**, centred: `tetrahedron`, `octahedron`,
  `dodecahedron`, `icosahedron`, `polyhedron("cube")`, `polyhedron_points`.
* **A geodesic `sphere`** built from triangles (the observatory dome
  principle); the old quad sphere is `quadsphere`.
* **Smooth surfaces**: `catmull_clark`, and `smooth` -- the generalised
  Catmull-Clark algorithm with any number of cells per edge.
* **Vertex tools**: `set_vertex`, `neighbors`, `valence`,
  `mean_neighbor_distance`, `edges`, `vertex_normal`, `face_center`,
  `dual`, `truncate`, `refine`, `spherify`, `inflate` ...
* **A catalogue of 25 named surfaces**: `surface("klein_bottle", ...)`.
* **Sketchfab-ready files**: `limit_colors`, `obj_size`, `save(...,
  colors=50)`, and `check()` reports the size and colour limits.
* **Glass and pictures**: `transparent`, `opacity`, `texture`, `write_png`
  -- written to the `.mtl` file of an `.obj` model.
* **Streaming output** for models bigger than memory: `stream`, `Stream`.
* **No flicker**: `clean`, `save` and `stream` weld repeated vertices,
  remove repeated and buried faces and cut back faces that overlap in one
  plane -- the smaller of two looking the same way, and the patch where
  two solids stand on each other out of both; `check` reports them,
  `overlaps` counts them.
* **Colour functions** on `parametric`, `revolve`, `sweep`, `curve`,
  `polyline` and `grid`.
* **Parts**: `beam`, `rounded_box`, `hemisphere`, `arch`, `stairs`, `gear`,
  `wheel`, `roof`, `column`, `bricks`, `tree`, `pixels`, `heightmap`,
  `polyline`, `wireframe`, `flow`, `trace`.
* **Placing**: `aim`, `ground`, `align`, `random_points`, `scatter`, `along`,
  and `make` to build any part as a separate mesh.
* **Profiles and helpers**: `profile_circle/ellipse/polygon/star/rect/gear`,
  `chaikin`, `points_on_line/circle/helix/spiral/curve`, `lerp`, `clamp`,
  `remap`, `distance`, `midpoint`, `direction`, `rotate_point`, `shade`.
* **Labels**: `text` with a built-in font (Lithuanian letters included);
  loaded letter meshes are laid out with `typeset`.
* **Repair and checking**: `clean`, `heal`, `fix_normals`, `stats`,
  `check`; four file formats; a dependency-free renderer in `tools/`.

## Three things that did change

`sphere(center, r, k, color)` is now a geodesic sphere of triangles: `k`
still sets the detail (k=10 gives 1280 triangles, k=20 gives 5120), but the
faces are different from the old `6*k*k` quads. The old construction is
`quadsphere` with exactly the same arguments.

`example1()` ... `example8()` no longer live inside `add.py`; they are in
`examples/20_classic_1_2.py`. This keeps the module to shapes and tools.

`axes()` draws its X/Y/Z labels as thin bars instead of the baked-in letter
meshes, so a model that calls `axes()` has a slightly different face count.
"""),
"lt": ("""# Pereinant nuo add.py 1.2

**Viskas veikia kaip veikę.** 1.2 versijai rašyti modeliai 2.0 versijoje
paleidžiami nepakeisti ir duoda tas pačias sienas; dvylika jų guli
`tests/legacy/` aplanke, ir testai tikrina būtent tai. (Vienintelis
sąmoningas pokytis: `sphere` dabar sudaryta iš trikampių, todėl modelis su
sferomis turi daugiau ir kitokių sienų -- žr. žemiau.)

Seni vardai niekur nedingo. Naujame kode verta rinktis aiškesnius:

| add.py 1.2 | add.py 2.0 | kas tai |
|---|---|---|
| `cube(c, e, RGB)` | `box` | kubas |
| `rectangle3D(c, e, RGB)` | `cuboid` | stačiakampis gretasienis |
| `cube2(c, e, b, RGB)` | `frame` | kubo briaunų karkasas |
| `cylinder2(A, B, r, k, RGB)` | `tube` | cilindras be dangtelių |
| `cylinder3(A, B, r, k, RGB)` | `cup` | uždarytas iš vieno galo |
| `cone2(A, B, r, k, RGB)` | `cone_open` | tik šoninis kūgio paviršius |
| `newface(A, RGB)` | `polygon` | viena plokščia siena |
| `spin3D(A, B, S, ...)` | `revolve` | sukinys |
| `off(path)` | `save(path)` | .off, .obj, .ply arba .stl |
| `zoom(M, s)` | `zoom` *(nepakito)* | mastelis |

`add.vertices` ir `add.faces` tebeatrodo ir tebeveikia kaip seni eilučių
sąrašai, o `layer()` grąžina tai, ką galima indeksuoti `M[0]` ir `M[1]`.
`example1()` ... `example8()` gyvena `examples/20_classic_1_2.py`, o
`examples/32_old_names.py` -- ištisas modelis, parašytas 1.2 žodynu.

## Kas naujo 2.0 versijoje

* **Loginės operacijos**, parašytos nuo nulio: `union`, `intersect`,
  `difference`, `symmetric_difference` ir pigus `cut`.
* **Užtenka `import add`**: `math` ir `random` eksportuojami iš modulio.
* **Penki taisyklingieji briaunainiai**, sucentruoti: `tetrahedron`,
  `octahedron`, `dodecahedron`, `icosahedron`, `polyhedron("cube")`,
  `polyhedron_points`.
* **Geodezinė `sphere`** iš trikampių (observatorijos kupolo principu);
  senoji keturkampių sfera -- `quadsphere`.
* **Glotnūs paviršiai**: `catmull_clark` ir `smooth` -- apibendrintas
  Catmull–Clark algoritmas su bet kokiu langelių skaičiumi ant briaunos.
* **Viršūnių įrankiai**: `set_vertex`, `neighbors`, `valence`,
  `mean_neighbor_distance`, `edges`, `vertex_normal`, `face_center`,
  `dual`, `truncate`, `refine`, `spherify`, `inflate` ...
* **25 vardinių paviršių katalogas**: `surface("klein_bottle", ...)`.
* **Sketchfab tinkami failai**: `limit_colors`, `obj_size`, `save(...,
  colors=50)`, o `check()` praneša dydžio ir spalvų ribas.
* **Stiklas ir paveikslėliai**: `transparent`, `opacity`, `texture`,
  `write_png` -- įrašomi į `.obj` modelio `.mtl` failą.
* **Srautinis rašymas** už atmintį didesniems modeliams: `stream`, `Stream`.
* **Jokio mirgėjimo**: `clean`, `save` ir `stream` suklijuoja pasikartojančias
  viršūnes, pašalina pasikartojančias ir palaidotas sienas, apkerpa vienoje
  plokštumoje persidengiančias sienas -- mažesnę iš dviejų, žiūrinčių ta
  pačia kryptimi, o lopą, kuriuo du kūnai stovi vienas ant kito, iš abiejų;
  `check` apie jas praneša, `overlaps` suskaičiuoja.
* **Spalvų funkcijos** funkcijoms `parametric`, `revolve`, `sweep`, `curve`,
  `polyline` ir `grid`.
* **Detalės**: `beam`, `rounded_box`, `hemisphere`, `arch`, `stairs`, `gear`,
  `wheel`, `roof`, `column`, `bricks`, `tree`, `pixels`, `heightmap`,
  `polyline`, `wireframe`, `flow`, `trace`.
* **Išdėstymas**: `aim`, `ground`, `align`, `random_points`, `scatter`,
  `along`, ir `make` bet kuriai detalei sukurti kaip atskirą tinklą.
* **Profiliai ir pagalbininkai**: `profile_circle/ellipse/polygon/star/rect/gear`,
  `chaikin`, `points_on_line/circle/helix/spiral/curve`, `lerp`, `clamp`,
  `remap`, `distance`, `midpoint`, `direction`, `rotate_point`, `shade`.
* **Užrašai**: `text` su įmontuotu šriftu (yra lietuviškos raidės); įkeltų
  raidžių figūros dėliojamos su `typeset`.
* **Taisymas ir tikrinimas**: `clean`, `heal`, `fix_normals`, `stats`,
  `check`; keturi failų formatai; `tools/` aplanke -- atvaizdavimo įrankis be
  priklausomybių.

## Trys dalykai, kurie pasikeitė

`sphere(centras, r, k, spalva)` dabar yra geodezinė sfera iš trikampių: `k`
tebenurodo detalumą (k=10 duoda 1280 trikampių, k=20 -- 5120), bet sienos
kitokios nei senieji `6*k*k` keturkampiai. Senoji konstrukcija -- `quadsphere`
su lygiai tais pačiais argumentais.

`example1()` ... `example8()` nebegyvena `add.py` viduje -- jie perkelti į
`examples/20_classic_1_2.py`. Taip modulyje liko tik figūros ir įrankiai.

`axes()` X/Y/Z raides braižo plonomis juostelėmis, o ne įrašytais raidžių
modeliais, todėl modelis, kviečiantis `axes()`, turi kiek kitokį sienų
skaičių.
"""),
}),

("faq", {
"en": ("""# Questions

**Is it fast enough?** For everything in the gallery, yes -- the whole
example set builds in about a minute and a half. Booleans are the expensive
part: two 5000-face solids take a second or two. If something feels slow,
lower the detail (`k`, `grid_u`, `grid_v`) before doing anything else; a
smooth-looking result usually needs far less detail than you think.

**Why no NumPy?** Because the point is that you can read every line. Nothing
here is hidden behind a library call, and the module runs on any Python 3
anywhere, including a school computer where you cannot install anything.

**Can I use it for 3D printing?** Yes -- `save("model.stl")`. Run
`add.clean(..., normals=True)` first and check that `add.check()` says the
surface is closed.

**Why is my boolean result not closed?** Almost always because one of the
inputs was not closed. Check both with `add.check()` before combining them.
Surfaces made with `parametric` are open sheets unless you give them
`thickness` or wrap them (`wrap_u`, `wrap_v`).

**Does it do textures and glass?** Yes, since 2.0: `texture(M, "picture.png")`
wraps an image around a part and `transparent(colour, alpha)` makes a colour
see-through; both are written to the `.mtl` file of an `.obj` model
(`map_Kd` and `d`). Colour is still per face, and `.off` files keep plain
colours, so nothing changes for a model that uses neither.

**Can I use it in my own project?** Yes, MIT licence. Attribution is welcome
but not required.

**What does "touching edges" in the report mean?** Two parts meet along an
edge only (think of a chequerboard of cubes). The surface is still
watertight -- there are no open edges -- but that edge is shared by four
faces. It is normal for `pixels`, `heightmap` and `voxels` models and does
no harm.

**Why is the file called `add.py` but the project `add3d`?** The module has
been `add.py` in the course since the beginning, and a file on your disk can
be called whatever you like. On PyPI, however, the name `add` is registered to
someone else (an empty placeholder with no releases), so the
repository and the installable package are called `add3d`. `pip install
add3d` and `import add` go together.
"""),
"lt": ("""# Klausimai

**Ar pakankamai greita?** Viskam, kas yra galerijoje, taip: visi pavyzdžiai
sugeneruojami maždaug per pusantros minutės. Brangiausia dalis -- loginės
operacijos: du 5000 sienų kūnai užtrunka sekundę ar dvi. Jei kas nors
strigdo, pirmiausia sumažinkite detalumą (`k`, `grid_u`, `grid_v`); gražiai
atrodančiam rezultatui paprastai reikia kur kas mažiau detalumo, nei atrodo.

**Kodėl nenaudojama NumPy?** Nes visa esmė ta, kad galite perskaityti
kiekvieną eilutę. Čia niekas nepaslėpta už bibliotekos kvietimo, ir modulis
veikia bet kuriame Python 3, taip pat ir mokyklos kompiuteryje, kuriame nieko
įdiegti negalima.

**Ar tinka 3D spausdinimui?** Taip -- `save("modelis.stl")`. Prieš tai
paleiskite `add.clean(..., normals=True)` ir įsitikinkite, kad `add.check()`
sako, jog paviršius uždaras.

**Kodėl loginės operacijos rezultatas neuždaras?** Beveik visada todėl, kad
neuždaras buvo vienas iš pradinių kūnų. Prieš jungdami patikrinkite abu su
`add.check()`. Su `parametric` sukurti paviršiai yra atviri lakštai, nebent
duosite jiems `thickness` arba uždarysite (`wrap_u`, `wrap_v`).

**Ar yra tekstūros ir stiklas?** Taip, nuo 2.0: `texture(M, "paveikslas.png")`
apvynioja detalę paveikslėliu, o `transparent(spalva, alpha)` padaro spalvą
permatomą; abu įrašomi į `.obj` modelio `.mtl` failą (`map_Kd` ir `d`).
Spalva ir toliau priskiriama sienai, o `.off` failuose lieka paprastos
spalvos, todėl modeliui, kuris nei vieno, nei kito nenaudoja, niekas
nesikeičia.

**Ar galiu naudoti savo projekte?** Taip, MIT licencija. Nuoroda į autorių
maloni, bet neprivaloma.

**Ką ataskaitoje reiškia "touching edges"?** Dvi dalys liečiasi tik briauna
(įsivaizduokite kubelių šachmatų lentą). Paviršius vis tiek sandarus --
atvirų briaunų nėra -- tik tą briauną dalijasi keturios sienos. Modeliams iš
`pixels`, `heightmap` ir `voxels` tai įprasta ir nekenkia.

**Kodėl failas vadinasi `add.py`, o projektas -- `add3d`?** Kurse modulis nuo
pat pradžių buvo `add.py`, o failą savo diske galima vadinti kaip norite.
Tačiau PyPI kataloge vardą `add` prieš daugelį metų užregistravo kitas
žmogus (tuščias, be jokių versijų), todėl saugykla ir diegiamas paketas
vadinasi `add3d`. `pip install add3d` ir `import add` eina kartu.
"""),
}),
]

# --------------------------------------------------------------------------
#  Gallery: (image, example script, English caption, Lithuanian caption)
# --------------------------------------------------------------------------

GALLERY = [
    ("primitives.png", "02_primitives.py",
     "Every ready-made shape in the library.",
     "Visos bibliotekoje esančios paruoštos figūros."),
    ("surfaces_classic.png", "06_surfaces_classic.py",
     "Classic parametric surfaces: sphere, torus, helicoid, catenoid, "
     "pseudosphere.",
     "Klasikiniai parametriniai paviršiai: sfera, toras, helikoidas, "
     "katenoidas, pseudosfera."),
    ("surfaces_exotic.png", "07_surfaces_exotic.py",
     "One-sided and self-intersecting surfaces: Mobius, Klein, Boy, Roman.",
     "Vienpusiai ir save kertantys paviršiai: Miobijaus, Kleino, Boy, Romos."),
    ("supershapes.png", "08_surfaces_superformula.py",
     "Twelve shapes from a single equation -- Gielis's superformula.",
     "Dvylika formų iš vienos lygties -- Gielio superformulė."),
    ("surfaces_nature.png", "09_surfaces_nature.py",
     "Shells, fruit, horns and waves, all written down as formulas.",
     "Kriauklės, vaisiai, ragai ir bangos -- viskas užrašyta formulėmis."),
    ("height_fields.png", "10_height_fields.py",
     "Graphs of two-variable functions, y = f(x, z).",
     "Dviejų kintamųjų funkcijų grafikai, y = f(x, z)."),
    ("curves.png", "12_curves.py",
     "Parametric curves drawn as round tubes: knots, spirals, Lissajous.",
     "Parametrinės kreivės kaip apvalūs vamzdeliai: mazgai, spiralės, "
     "Lissajous kreivės."),
    ("sweeps.png", "13_sweep_and_twist.py",
     "A cross-section copied, turned and stretched along a path.",
     "Skerspjūvis, kopijuojamas, sukamas ir tempiamas išilgai kelio."),
    ("lathe.png", "14_lathe_gallery.py",
     "The lathe: a vase, a wine glass, chess pieces, a doughnut.",
     "Sukinys: vaza, taurė, šachmatų figūros, spurga."),
    ("patterns.png", "15_patterns.py",
     "One piece, many copies: rows, rings, spirals, sunflower packing.",
     "Viena detalė, daug kopijų: eilės, žiedai, spiralės, saulėgrąžos "
     "išdėstymas."),
    ("booleans.png", "16_booleans.py",
     "Union, intersection and difference: holes, a gear, a pipe elbow.",
     "Sąjunga, sankirta ir skirtumas: skylės, krumpliaratis, vamzdžio alkūnė."),
    ("fractals.png", "17_fractals.py",
     "A Menger sponge, a Sierpinski tetrahedron, a tree, a Koch prism.",
     "Mengerio kempinė, Sierpinskio tetraedras, medis, Kocho prizmė."),
    ("chess_set.png", "18_chess_set.py",
     "A complete chess set: lathe, layers, booleans, a board.",
     "Pilnas šachmatų komplektas: sukinys, sluoksniai, loginės operacijos, "
     "lenta."),
    ("city.png", "19_city.py",
     "A procedural city. One seed decides the whole town.",
     "Procedūriškai sugeneruotas miestas. Vienas skaičius nulemia visą "
     "miestą."),
    ("text.png", "21_text_and_loading.py",
     "Models loaded back from files: a word, an alphabet, a reloaded torus.",
     "Iš failų įkelti modeliai: žodis, abėcėlė, iš naujo įkeltas toras."),
    ("lighthouse.png", "22_lighthouse.py",
     "A lighthouse island: height field, striped lathe, bricks, palms, a "
     "lofted boat.",
     "Švyturio sala: aukščių laukas, dryžuotas sukinys, plytos, palmės, "
     "valtis iš pjūvių."),
    ("locomotive.png", "23_locomotive.py",
     "A steam locomotive: spoked wheels, rods that follow the crank angle, "
     "smoke along a curve.",
     "Garvežys: ratai su stipinais, trauklės, sekančios alkūnės kampą, "
     "dūmai išilgai kreivės."),
    ("windmill.png", "24_windmill.py",
     "A windmill on a hill: an extruded octagon, four sails from one, a "
     "fence along a ring.",
     "Malūnas ant kalvos: ištemptas aštuonkampis, keturi sparnai iš vieno, "
     "tvora išilgai žiedo."),
    ("temple.png", "25_temple.py",
     "A round temple: columns on a circle, a pipe entablature, a dome, a "
     "chequered floor from a colour function.",
     "Apvali šventykla: kolonos ant apskritimo, antablementas, kupolas, "
     "languotos grindys iš spalvos funkcijos."),
    ("vector_fields.png", "26_vector_fields.py",
     "Lorenz and Rössler attractors, an arrow field, beads on a helix, "
     "cubes on a spiral.",
     "Lorenco ir Röslerio atraktoriai, rodyklių laukas, karoliukai ant "
     "spiralės, kubeliai ant sraigto."),
    ("robot.png", "27_robot.py",
     "A robot reaching for a ball: limbs aimed at points, a pixel face, a "
     "sheared shadow.",
     "Robotas siekia kamuolio: galūnės, nukreiptos į taškus, pikselinis "
     "veidas, šešėlis iš šlyties."),
    ("voxel_island.png", "28_voxel_island.py",
     "A block-world island from a height table, painted by layer, with a "
     "flag from strings.",
     "Kubelių sala iš aukščių lentelės, nuspalvinta sluoksniais, su vėliava "
     "iš eilučių."),
    ("bridge.png", "29_bridge.py",
     "A suspension bridge and a stone bridge: beams, cables, hangers, "
     "arches, cars along the road.",
     "Kabantis ir akmeninis tiltai: sijos, lynai, pakabos, arkos, "
     "automobiliai išilgai kelio."),
    ("solar_system.png", "30_solar_system.py",
     "Planets painted by colour functions, orbits, moons, an asteroid belt, "
     "a comet.",
     "Planetos, nuspalvintos spalvų funkcijomis, orbitos, mėnuliai, "
     "asteroidų žiedas, kometa."),
    ("workbench.png", "31_workbench.py",
     "The workbench: a broken mesh repaired, a union healed, points tested "
     "with inside(), every file format.",
     "Dirbtuvės: sutaisytas sugadintas modelis, sujungti kūnai, taškai, "
     "patikrinti su inside(), visi failų formatai."),
    ("old_names.png", "32_old_names.py",
     "A still life written entirely in the add.py 1.2 vocabulary.",
     "Natiurmortas, parašytas vien add.py 1.2 žodynu."),
    ("cross_sections.png", "33_cross_sections.py",
     "Cross-sections on the move: star, gear, ellipse, circle, rounded "
     "rectangle, polygon -- extruded, swept, lofted, bent.",
     "Skerspjūviai kelyje: žvaigždė, krumpliaratis, elipsė, apskritimas, "
     "suapvalintas stačiakampis, daugiakampis -- ištempti, nušluoti, "
     "sulenkti."),
    ("example4.png", "20_classic_1_2.py",
     "A Christmas tree made only of parametric surfaces (from add.py 1.2).",
     "Eglutė vien iš parametrinių paviršių (iš add.py 1.2)."),
    ("example7.png", "20_classic_1_2.py",
     "A ball-and-stick buckyball (from add.py 1.2).",
     "Fulerenas iš rutuliukų ir strypelių (iš add.py 1.2)."),
    ("surface_zoo.png", "34_surface_zoo.py",
     "The surface zoo: all twenty-five named surfaces of the catalogue, "
     "labelled.",
     "Paviršių zoologijos sodas: visi dvidešimt penki katalogo paviršiai su "
     "užrašais."),
    ("knot_curve.png", "35_knot_curve.py",
     "An epicyclic knot: a sum of rotating circles drawn as a closed tube "
     "of 60 000 quads.",
     "Epiciklinis mazgas: besisukančių apskritimų suma, nubraižyta kaip "
     "uždaras 60 000 keturkampių vamzdis."),
    ("minecraft_sphere.png", "36_minecraft_sphere.py",
     "Three spheres: the Maple cube-sphere, a ball of blocks, and the "
     "geodesic sphere.",
     "Trys sferos: Maple kubo sfera, kubelių rutulys ir geodezinė sfera."),
    ("football.png", "37_football.py",
     "A football built from the vertices of an icosahedron -- flat panels "
     "and the smoothed ball.",
     "Futbolo kamuolys iš ikosaedro viršūnių -- plokšti skydeliai ir "
     "suapvalintas kamuolys."),
    ("polyhedra.png", "38_polyhedra.py",
     "The five Platonic solids, their duals, truncations, geodesic domes "
     "and smooth limit surfaces.",
     "Penki Platono kūnai, jų dualieji kūnai, nupjovimai, geodeziniai "
     "kupolai ir glotnūs ribiniai paviršiai."),
    ("smooth_shapes.png", "39_smooth_shapes.py",
     "Generalised Catmull-Clark: a pulled box rounded off, n = 1 ... 7 on "
     "one prism, uniform and plain grids on a star.",
     "Apibendrintas Catmull–Clark: suapvalinta ištraukto kampo dėžė, n = 1 "
     "... 7 ant vienos prizmės, tolygus ir paprastas tinklas ant žvaigždės."),
    ("vertex_tools.png", "40_vertex_tools.py",
     "Building on vertices, edges and faces: a buckyball, a spiky virus, a "
     "stellated dodecahedron, a cage with its dual inside.",
     "Statyba ant viršūnių, briaunų ir sienų: fulerenas, spygliuotas "
     "virusas, žvaigždinis dodekaedras, narvas su dualiuoju kūnu."),
    ("sketchfab_ready.png", "41_sketchfab_ready.py",
     "Thousands of shades reduced to fifty materials for Sketchfab.",
     "Tūkstančiai atspalvių, sumažinti iki penkiasdešimties medžiagų "
     "Sketchfab."),
    ("pillow_letters.png", "42_pillow_letters.py",
     "Pillow letters: blocks united and rounded into cushions.",
     "Pagalvinės raidės: sujungti blokai, suapvalinti į pagalvėles."),
    ("planet.png", "43_planet.py",
     "A planet with craters, an ocean, a ring and two rocky moons.",
     "Planeta su krateriais, vandenynu, žiedu ir dviem uolėtais mėnuliais."),
    ("geodesic_dome.png", "44_geodesic_dome.py",
     "A geodesic dome house: panels, struts, hubs and a door.",
     "Geodezinio kupolo namas: skydai, statramsčiai, mazgai ir durys."),
    ("glass_and_textures.png", "45_glass_and_textures.py",
     "Glass and pictures: a fish tank, a brick house with windows and a "
     "textured globe (rendered from the .obj).",
     "Stiklas ir paveikslėliai: akvariumas, plytų namas su langais ir "
     "tekstūruotas gaublys (atvaizduota iš .obj)."),
    ("castle.png", "46_castle.py",
     "The castle: an island in a transparent lake, a wall of stone blocks "
     "with eight hollow towers (spiral stairs inside), a gatehouse with a "
     "portcullis and a drawbridge on chains, a palace with glass windows "
     "and a tiled roof, a chapel with stained glass, a courtyard full of "
     "barrels, carts, weapons and animals -- and, inside, the king in his "
     "throne hall with a feast, a dormitory, an attic and a dragon on its "
     "treasure. No textures: every stone, tile and coat of arms is "
     "geometry. Written streaming: a 400 MB .off, an .obj under 100 MB "
     "compressed.",
     "Pilis: sala permatomame ežere, akmens blokų siena su aštuoniais "
     "tuščiaviduriais bokštais (viduje sraigtiniai laiptai), vartai su "
     "pakeliamomis grotomis ir tiltu ant grandinių, rūmai su stiklo langais "
     "ir čerpių stogu, koplyčia su vitražais, kiemas pilnas statinių, "
     "vežimų, ginklų ir gyvūnų -- o viduje karalius sosto menėje su puota, "
     "miegamasis, palėpė ir drakonas ant lobio. Be tekstūrų: kiekvienas "
     "akmuo, čerpė ir herbas -- daugiakampiai. Rašyta srautu: 400 MB .off, "
     ".obj suglaudintas mažiau nei 100 MB."),
    ("castle_hall.png", "46_castle.py",
     "Inside the castle: the great hall with the king's throne, the feast "
     "on the long tables and the chandeliers (a view from the .obj).",
     "Pilies viduje: didžioji menė su karaliaus sostu, puota ant ilgųjų "
     "stalų ir sietynai (vaizdas iš .obj)."),
    ("castle_treasury.png", "46_castle.py",
     "The second easter egg: the treasury in the big tower, with a dragon "
     "asleep on the gold.",
     "Antrasis siurprizas: lobynas didžiajame bokšte su drakonu, miegančiu "
     "ant aukso."),
]

# --------------------------------------------------------------------------
#  One-line Lithuanian description for every public function.
# --------------------------------------------------------------------------

SHORT = {
# -- scene and meshes
"scene": "Grąžina dabartinę sceną (Mesh objektą).",
"clear": "Ištrina viską, kas iki šiol nupiešta.",
"layer": "Paima sceną kaip modelį ir palieka sceną tuščią.",
"mesh": "Prideda modelį M į dabartinę sceną.",
"paste": "Tas pats, kas mesh(M).",
"push": "Padeda sceną į šalį ir pradeda naują, tuščią.",
"pop": "Grąžina tai, kas nupiešta po push(), ir atkuria ankstesnę sceną.",
"merge": "Sujungia kelis modelius į vieną (geometrija nekeičiama).",
"copy": "Nepriklausoma modelio kopija.",
"as_mesh": "Priima Mesh arba senąjį [viršūnės, sienos] sąrašą ir grąžina Mesh.",
"Mesh": "Modelio klasė: viršūnių sąrašas V, sienų sąrašas F ir spalvos C.",
# -- flat shapes
"polygon": "Viena plokščia siena iš nurodytų 3D taškų.",
"newface": "Senas polygon vardas.",
"triangle": "Vienas trikampis.",
"quad": "Vienas keturkampis.",
"disc": "Užpildytas skritulys, statmenas nurodytai krypčiai.",
"ring": "Plokščias žiedas (skritulys su skyle).",
"grid": "Plokščias arba kalvotas stačiakampis lopas XZ plokštumoje.",
# -- solids
"box": "Kubas su nurodyta briauna.",
"cube": "Senas box vardas.",
"cuboid": "Stačiakampis gretasienis; briaunų ilgiai X, Y ir Z kryptimis.",
"block": "Tas pats, kas cuboid.",
"cuboid3D": "Tas pats, kas cuboid.",
"rectangle3D": "Senas cuboid vardas.",
"frame": "Kubo briaunų karkasas -- dvylika strypelių.",
"cube2": "Senas frame vardas.",
"voxels": "Kubelių aibės paviršius -- „Minecraft“ stiliaus modelis.",
"pyramid": "Kvadratinė piramidė; neigiamas aukštis nukreipia ją žemyn.",
"prism": "Prizmė: 2D profilis, ištemptas per nurodytą storį.",
"polyhedron": "Vienas iš penkių Platono kūnų.",
"sphere": "Sfera iš šešių kreivų kvadratinių lopų.",
"ball": "Tas pats, kas sphere.",
"uvsphere": "Sfera iš dienovidinių ir lygiagrečių (gaublio stiliaus).",
"ellipsoid": "Elipsoidas: atskiras spindulys X, Y ir Z kryptimis.",
"torus": "Spurga: r spindulio vamzdis apie R spindulio apskritimą.",
"capsule": "Cilindras su pusrutuliais galuose.",
"cylinder": "Uždaras cilindras nuo A iki B.",
"tube": "Cilindras be dangtelių -- tik šoninė sienelė.",
"cylinder2": "Senas tube vardas.",
"cup": "Cilindras, uždarytas tik ties A.",
"cylinder3": "Senas cup vardas.",
"cone": "Uždaras kūgis: pagrindas ties A, viršūnė ties B.",
"cone_open": "Tik šoninis kūgio paviršius.",
"cone2": "Senas cone_open vardas.",
"frustum": "Nupjautinis kūgis: spindulys r1 ties A, r2 ties B.",
"pipe": "Tuščiaviduris vamzdis su cilindrine skyle viduryje.",
"arrow": "Strypelis su kūgio smaigaliu -- patogu vektoriams.",
"helix": "Spyruoklė arba sraigtinis vamzdis apie ašį.",
"axes": "Koordinačių ašys: X raudona, Y žalia, Z mėlyna, su raidėmis.",
"glyph": "Nubraižo raidę X, Y arba Z plonomis juostelėmis.",
# -- surfaces
"parametric": "Pagrindinė funkcija: nubraižo paviršių S(u, v) -> [x, y, z].",
"two_sided": "Kopija, kurioje kiekviena siena yra ir apversta.",
"solidify": "Suteikia plonam paviršiui tikrą storį ir grąžina uždarą kūną.",
"revolve": "Sukinys: 2D profilio sukimas apie ašį A -> B.",
"lathe": "Tas pats, kas revolve.",
"solid_of_revolution": "Tas pats, kas revolve.",
"spin3D": "Senas revolve vardas (be dangtelių).",
"sweep": "Skerspjūvio stūmimas išilgai 3D kelio; galima sukti ir tempti.",
"curve": "3D parametrinė kreivė, nubraižyta kaip apvalus vamzdis.",
"extrude": "2D formos ištempimas į 3D; pakeliui galima sukti ir siaurinti.",
"loft": "Paviršius, uždengiantis skerspjūvių seką.",
"ribbon": "Plokščia juosta, einanti 3D keliu.",
"circle": "Senas disc vardas.",
# -- measuring
"bbox": "Modelio gaubiančiojo stačiakampio kampai.",
"size": "Modelio plotis, aukštis ir gylis.",
"center": "Visų viršūnių vidurkis (kaip add.py 1.2).",
"middle": "Gaubiančiojo stačiakampio centras.",
"area": "Bendras paviršiaus plotas.",
"volume": "Uždaro modelio tūris.",
# -- transforms
"move": "Pastumia modelį vektoriumi V.",
"translate": "Tas pats, kas move.",
"place": "Pastumia modelį taip, kad jo centras atsidurtų nurodytame taške.",
"rotateX": "Pasuka modelį apie X ašį per tašką P.",
"rotateY": "Pasuka modelį apie Y ašį per tašką P.",
"rotateZ": "Pasuka modelį apie Z ašį per tašką P.",
"rotate": "Pasuka modelį apie bet kokią ašį (Rodrigo formulė).",
"zoom": "Pakeičia modelio mastelį koeficientu s.",
"scale": "Tas pats, kas zoom.",
"stretch": "Atskiras mastelis kiekvienai ašiai, s = [sx, sy, sz].",
"fit": "Pakeičia mastelį taip, kad didžiausias matmuo būtų lygus nurodytam.",
"mirror": "Atspindi modelį plokštumoje ir apsuka sienų kryptį.",
"reflect": "Tas pats, kas mirror.",
"transform": "Pritaiko 3x3 arba 4x4 matricą.",
"deform": "Bet kokia funkcija f(p) -> naujas taškas; galingiausia priemonė.",
"twist": "Susuka modelį apie ašį, kaip kamščiatraukį.",
"taper": "Siaurina arba platina modelį išilgai ašies.",
"bend": "Sulenkia modelį į lanką.",
"jitter": "Truputį atsitiktinai pastumdo kiekvieną viršūnę.",
# -- colour
"rgb": "Bet ką, kas panašu į spalvą, paverčia (r, g, b) reikšme.",
"hsv": "Spalva iš atspalvio, sodrumo ir šviesumo (visi 0..1).",
"gradient": "Perėjimas tarp dviejų spalvų.",
"random_color": "Atsitiktinė spalva.",
"color": "Perdažo visą modelį viena spalva.",
"color_by": "Kiekvienos sienos spalva pagal jos padėtį: fn(taškas) -> spalva.",
"color_gradient": "Perėjimas nuo spalvos a iki b išilgai ašies.",
"color_random": "Kiekvienai sienai -- sava atsitiktinė spalva.",
"COLORS": "Spalvų vardų žodynas („red“, „gold“, „sky“ ir kt.).",
# -- patterns
"repeat": "Bendriausias kopijavimas: transformacija, taikoma n kartų.",
"array_linear": "n kopijų eilėje.",
"array_grid": "Kopijų blokas 2D arba 3D tinkleliu.",
"array_radial": "n kopijų apie ašį; su rise -- sraigtiniai laiptai.",
"array_mirror": "Modelis kartu su savo veidrodiniu atvaizdu.",
# -- repair
"clean": "Sutvarko modelį: suklijuoja viršūnes, pašalina dublikatus ir "
         "vidines sienas, apkerpa persidengiančias (mirgančias) sienas, "
         "neiškilas supjausto trikampiais.",
"overlaps": "Kiek sienų persidengia vienoje plokštumoje (mirga peržiūroje).",
"concave_faces": "Kiek sienų neiškilos (peržiūroje jų įdubą uždengtų trikampis).",
"weld": "Tas pats, kas clean.",
"heal": "Uždaro plyšelius ten, kur briauna praeina pro svetimą viršūnę.",
"triangulate": "Kopija, kurioje visos sienos -- trikampiai.",
"fix_normals": "Nukreipia visas sienas ta pačia kryptimi, uždarame modelyje "
               "-- į išorę.",
"stats": "Žodynas su modelio skaičiais: sienos, spalvos, plotas, tūris.",
"check": "Išspausdina modelio ataskaitą ir pasako, ar atitinka užduotį.",
# -- booleans
"union": "Sujungia kūnus į vieną, pašalindama viską, kas paslėpta viduje.",
"add_solids": "Tas pats, kas union.",
"difference": "Iškerpa kitus kūnus iš A.",
"subtract": "Tas pats, kas difference.",
"intersect": "Palieka tik tai, kas bendra visiems kūnams.",
"common": "Tas pats, kas intersect.",
"symmetric_difference": "Kas yra viename ar kitame kūne, bet ne abiejuose.",
"cut": "Perpjauna kūną plokštuma ir palieka pusę už jos.",
"inside": "Ar taškas yra uždaro modelio viduje?",
# -- files
"save": "Išsaugo modelį; formatą nulemia plėtinys.",
"off": "Įrašo OFF failą (ir ištuština sceną) -- kaip add.py 1.2.",
"obj": "Įrašo OBJ failą ir kartu MTL spalvų failą.",
"load": "Nuskaito modelį iš .off, .obj arba .ply failo.",
"load_font": "Nuskaito visą raidžių ar skaitmenų aplanką į žodyną.",
"typeset": "Išdėsto įkeltų raidžių (Mesh) eilutę ir sujungia į vieną modelį.",
# -- 2.1: numbers, profiles and points
"lerp": "Tarpinė reikšmė tarp a ir b (t nuo 0 iki 1); veikia ir taškams.",
"clamp": "Apriboja skaičių intervalu lo..hi.",
"remap": "Perveda x iš intervalo a0..a1 į intervalą b0..b1.",
"distance": "Atstumas tarp dviejų taškų.",
"midpoint": "Atkarpos vidurio taškas.",
"direction": "Vienetinis vektorius nuo a link b.",
"rotate_point": "Pasuka vieną tašką apie ašį per tašką P.",
"shade": "Tamsesnis (factor < 1) arba šviesesnis (> 1) spalvos atspalvis.",
"chaikin": "Suapvalina laužtės kampus (Chaikin algoritmas).",
"profile_circle": "k taškų ant apskritimo -- profilis extrude/sweep/prism funkcijoms.",
"profile_ellipse": "Elipsės profilis.",
"profile_polygon": "Taisyklingo n-kampio profilis.",
"profile_star": "Žvaigždės profilis su n spinduliais.",
"profile_rect": "Stačiakampio profilis, galima suapvalinti kampus.",
"profile_gear": "Krumpliaračio kontūras.",
"points_on_line": "n taškų, tolygiai išdėstytų atkarpoje.",
"points_on_circle": "n taškų ant apskritimo erdvėje.",
"points_on_helix": "n taškų ant spiralinės linijos (sraigto).",
"points_on_spiral": "n taškų ant plokščios spiralės, kurios spindulys auga.",
"points_on_curve": "n taškų ant kreivės path(t).",
# -- 2.1: parts
"beam": "Stačiakampė sija nuo taško A iki taško B.",
"rounded_box": "Dėžė suapvalintomis briaunomis ir kampais.",
"hemisphere": "Pusrutulis (kupolas, dubuo).",
"arch": "Arka, stovinti ant taškų A ir B, apvalaus arba stačiakampio pjūvio.",
"stairs": "Laiptai iš n pakopų.",
"gear": "Krumpliaratis su nurodytu dantų skaičiumi (galima su skyle ašiai).",
"wheel": "Ratas: diskas su stebule arba padanga su stipinais.",
"roof": "Dvišlaitis stogas virš stačiakampio pagrindo.",
"column": "Kolona su pjedestalu ir kapiteliu.",
"bricks": "Plytų siena su perslinktomis eilėmis.",
"tree": "Medis: apvalus, eglė arba palmė; seed duoda skirtingus medžius.",
"pixels": "Pikselinis piešinys iš eilučių tekstas -> spalvoti kubeliai.",
"heightmap": "Kubelių stulpeliai pagal aukščių lentelę.",
"polyline": "Apvalus vamzdis per taškų sąrašą.",
"wireframe": "Visos modelio briaunos kaip ploni strypeliai su rutuliukais kampuose.",
"flow": "Vektorinio lauko trajektorija (Runge-Kutta) -- taškų sąrašas.",
"trace": "Nubraižo vektorinio lauko trajektoriją kaip vamzdį.",
"PALETTE": "Numatytoji pixels() spalvų lentelė: viena raidė -- viena spalva.",
# -- 2.1: placing
"aim": "Pasuka modelį taip, kad jo ašis rodytų nurodyta kryptimi.",
"ground": "Nuleidžia modelį taip, kad jo apačia būtų aukštyje y.",
"align": "Perkelia modelį taip, kad pasirinktas gabarito taškas atsidurtų nurodytoje vietoje.",
"random_points": "n atsitiktinių taškų dėžėje (arba ant reljefo, jei duota height).",
"scatter": "Modelio kopijos nurodytuose taškuose, atsitiktinai pasuktos ir padidintos.",
"along": "n modelio kopijų išilgai kreivės, pasuktų pagal jos kryptį.",
# -- 2.1: labels
"text": "Užrašas iš įmontuoto šrifto (raidės, skaitmenys, lietuviškos raidės).",
"write": "Tas pats, kas text().",
"label": "Tas pats, kas text().",
"text_width": "Kokio pločio bus text() užrašas.",
# -- misc
"demo": "Sukuria nedidelį modelį, išbandantį beveik visą biblioteką.",
"EPS": "Skaitinė paklaida, naudojama klijuojant ir lyginant.",
"BOOL_EPS": "Paklaida, naudojama loginėse operacijose.",
"DEFAULT_COLOR": "Spalva, naudojama, kai jokia nenurodyta.",
"vertices": "Dabartinės scenos viršūnės senuoju eilučių pavidalu.",
"faces": "Dabartinės scenos sienos senuoju eilučių pavidalu.",
}


# --------------------------------------------------------------------------
#  Lithuanian names of the reference sections (keyed by the English title
#  as it appears in add.py's section headers, without the number)
# --------------------------------------------------------------------------

SECTION_TITLES_LT = {
    "Constants": "Konstantos",
    "Small helpers -- vectors and colours": "Pagalbinės funkcijos -- vektoriai ir spalvos",
    "Mesh -- the one data structure in this library": "Mesh -- vienintelė bibliotekos duomenų struktūra",
    "The current scene (the \"default layer\")": "Dabartinė scena (numatytasis sluoksnis)",
    "Building blocks used by every shape below": "Statybiniai blokai, naudojami visų figūrų",
    "Flat shapes": "Plokščios figūros",
    "Boxes and other flat-sided solids": "Dėžės ir kiti plokščiasieniai kūnai",
    "The five regular polyhedra (Platonic solids)": "Penki taisyklingieji briaunainiai (Platono kūnai)",
    "Numbers, points and 2D profiles": "Skaičiai, taškai ir 2D profiliai",
    "Round solids": "Apvalūs kūnai",
    "Coordinate axes": "Koordinačių ašys",
    "Parts that models keep needing": "Detalės, kurių modeliams nuolat reikia",
    "Parametric surfaces": "Parametriniai paviršiai",
    "Curves, sweeps and lofts -- \"copy, turn, stretch a cross-section\"":
        "Kreivės, šlavimai ir loftai -- „kopijuok, pasuk, ištempk skerspjūvį“",
    "A catalogue of named surfaces": "Vardinių paviršių katalogas",
    "Measuring a mesh": "Tinklo matavimas",
    "Moving, turning and reshaping a mesh": "Tinklo stūmimas, sukimas ir formos keitimas",
    "Colour": "Spalva",
    "Copies and patterns": "Kopijos ir raštai",
    "Placing parts: aim, scatter, line up": "Detalių išdėstymas: nukreipti, išbarstyti, sustatyti",
    "Repairing a model": "Modelio taisymas",
    "Looking at a model": "Modelio apžiūra",
    "Vertices, edges and neighbours": "Viršūnės, briaunos ir kaimynės",
    "Boolean operations: union, intersection, difference": "Loginės operacijos: sąjunga, sankirta, skirtumas",
    "Smooth surfaces: Catmull-Clark and uniform n-grids": "Glotnūs paviršiai: Catmull–Clark ir tolygūs n-tinklai",
    "Saving and loading": "Įrašymas ir įkėlimas",
    "Letters and labels": "Raidės ir užrašai",
    "add.py 1.2 names": "add.py 1.2 vardai",
    "A one-line demonstration": "Demonstracija viena eilute",
}

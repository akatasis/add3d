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

## My model has stray faces inside it

That happens when two solids touch: each keeps its own wall, buried where
nobody can see it. `clean()` finds and removes them, along with repeated
vertices and zero-area faces:

```
model = add.clean(add.layer())
add.mesh(model)
```

## I want a vase / chess piece / bottle

Spin a profile: `revolve(profile, A, B, t0, t1, steps, k, colour)` where
`profile(t)` returns `[radius, height]`.

```
def vase(t):
    return [1 + 0.4 * math.sin(3 * t), t]

add.revolve(vase, [0, 0, 0], [0, 1, 0], 0, 4, 60, 40, "teal")
```

!lathe.png|Twelve shapes, each a single profile function.

## I want to bend or twist something

```
M = add.twist(M, 0.5)                   # a corkscrew
M = add.taper(M, -0.2)                  # thinner as it rises
M = add.bend(M, 0.3)                    # into an arc
M = add.deform(M, lambda p: [p[0], p[1] + math.sin(p[0]), p[2]])
```

`deform` takes any function you like, so it can do anything the others cannot.

## I want a rainbow

```
M = add.color_by(M, lambda p: add.hsv(p[1] / 10.0))
```

`color_by` calls your function with the centre of each face.
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

## Modelio viduje liko nereikalingų sienų

Taip nutinka, kai du kūnai liečiasi: kiekvienas pasilieka savo sienelę,
palaidotą ten, kur jos niekas nemato. `clean()` jas suranda ir pašalina kartu
su besidubliuojančiomis viršūnėmis ir nulinio ploto sienomis:

```
modelis = add.clean(add.layer())
add.mesh(modelis)
```

## Noriu vazos / šachmatų figūros / butelio

Sukite profilį: `revolve(profilis, A, B, t0, t1, steps, k, spalva)`, kur
`profilis(t)` grąžina `[spindulys, aukštis]`.

```
def vaza(t):
    return [1 + 0.4 * math.sin(3 * t), t]

add.revolve(vaza, [0, 0, 0], [0, 1, 0], 0, 4, 60, 40, "teal")
```

!lathe.png|Dvylika formų, kiekviena -- viena profilio funkcija.

## Noriu ką nors sulenkti ar susukti

```
M = add.twist(M, 0.5)                   # kaip kamščiatraukis
M = add.taper(M, -0.2)                  # kylant plonėja
M = add.bend(M, 0.3)                    # į lanką
M = add.deform(M, lambda p: [p[0], p[1] + math.sin(p[0]), p[2]])
```

`deform` priima bet kokią jūsų funkciją, todėl padaro tai, ko kiti negali.

## Noriu vaivorykštės

```
M = add.color_by(M, lambda p: add.hsv(p[1] / 10.0))
```

`color_by` iškviečia jūsų funkciją su kiekvienos sienos centru.
"""),
}),

("upgrade", {
"en": ("""# Coming from add.py 1.2

**Everything still works.** Models written for 1.2 run on 2.0 unchanged and
produce the same faces; twelve of them are in `tests/legacy/` and the test
suite checks exactly that on every commit.

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
`M[1]`.

## Two things that did change

`example1()` ... `example8()` no longer live inside `add.py`; they are in
`examples/20_classic_1_2.py`. This keeps the module to shapes and tools.

`axes()` draws its X/Y/Z labels as thin bars instead of the baked-in letter
meshes, so a model that calls `axes()` has a slightly different face count.
"""),
"lt": ("""# Pereinant nuo add.py 1.2

**Viskas veikia kaip veikę.** 1.2 versijai rašyti modeliai 2.0 versijoje
paleidžiami nepakeisti ir duoda tas pačias sienas; dvylika jų guli
`tests/legacy/` aplanke, ir testai tikrina būtent tai.

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

## Du dalykai, kurie pasikeitė

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

**Does it do textures?** No. Colour is per face. That is enough for the kind
of model this library is for, and it keeps the file format simple.

**Can I use it in my own project?** Yes, MIT licence. Attribution is welcome
but not required.
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

**Ar yra tekstūros?** Ne. Spalva priskiriama sienai. Tokio tipo modeliams to
pakanka, o failo formatas lieka paprastas.

**Ar galiu naudoti savo projekte?** Taip, MIT licencija. Nuoroda į autorių
maloni, bet neprivaloma.
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
    ("example4.png", "20_classic_1_2.py",
     "A Christmas tree made only of parametric surfaces (from add.py 1.2).",
     "Eglutė vien iš parametrinių paviršių (iš add.py 1.2)."),
    ("example7.png", "20_classic_1_2.py",
     "A ball-and-stick buckyball (from add.py 1.2).",
     "Fulerenas iš rutuliukų ir strypelių (iš add.py 1.2)."),
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
         "vidines sienas.",
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
"text": "Išdėsto įkeltų raidžių eilutę ir sujungia į vieną modelį.",
# -- misc
"demo": "Sukuria nedidelį modelį, išbandantį beveik visą biblioteką.",
"EPS": "Skaitinė paklaida, naudojama klijuojant ir lyginant.",
"BOOL_EPS": "Paklaida, naudojama loginėse operacijose.",
"DEFAULT_COLOR": "Spalva, naudojama, kai jokia nenurodyta.",
"vertices": "Dabartinės scenos viršūnės senuoju eilučių pavidalu.",
"faces": "Dabartinės scenos sienos senuoju eilučių pavidalu.",
}

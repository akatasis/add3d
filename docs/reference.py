# -*- coding: utf-8 -*-
"""
Per-function documentation that does not live in the source: a Lithuanian
explanation and a short, runnable example for EVERY public name of add.py.

``tools/make_docs.py`` puts them under each entry of the reference (the
English explanation is the docstring itself) and refuses to build when a
name is missing here, so the reference cannot be incomplete.
``tests/test_docs.py`` runs every example, so they cannot go stale.

Examples are plain add.py code; they may assume ``import add`` and run in
a scratch directory (files they write are thrown away).
"""

# --------------------------------------------------------------------------
#  Lithuanian explanations (one to three sentences each)
# --------------------------------------------------------------------------

EXPLAIN_LT = {
    # -- constants
    "EPS": "Skaitinė paklaida, kurią naudoja viršūnių suliejimas, loginės "
           "operacijos ir plokštumų testai. Paprastai jos keisti nereikia.",
    "DEFAULT_COLOR": "Spalva, kuria piešiama, kai funkcijai spalva nenurodyta "
                     "(pilka).",
    "BOOL_EPS": "Kiek taškas gali būti nutolęs nuo plokštumos, kad loginės "
                "operacijos jį laikytų gulinčiu joje.",
    "COLORS": "Žodynas su spalvų vardais: „red“, „sky“, „gold“ ir kt. Bet kur, "
              "kur laukiama spalvos, galima rašyti tokį vardą.",
    "PALETTE": "Numatytoji paletė funkcijai pixels: viena raidė – viena spalva.",
    "SKETCHFAB_MB": "Didžiausias .obj failo dydis megabaitais, kurį check() "
                    "laiko tinkamu Sketchfab (50).",
    "SKETCHFAB_COLORS": "Didžiausias spalvų (medžiagų) skaičius, kurį check() "
                        "laiko tinkamu Sketchfab (50).",
    "SURFACES": "Vardinių paviršių katalogas: kiekvienam vardui – formulė f, "
                "parametrų sritys u ir v, uždarumo požymiai wrap, numatytas "
                "tinklelis, pastaba ir konstantos. Piešiama su surface().",

    # -- colours
    "rgb": "Paverčia bet kokį spalvos užrašą į (r, g, b) trejetą 0..255: sąrašą, "
           "0..1 trupmenas, „#ff0000“ ar vardą „red“. Ketvirtas skaičius – "
           "permatomumas, penktas – tekstūros failas (žr. transparent, texture).",
    "transparent": "Permatoma spalvos versija: alpha – nepermatomumas nuo 0 "
                   "(nematoma) iki 1 (vientisa). Rezultatą galima naudoti visur, "
                   "kur laukiama spalvos; permatomumas įrašomas į .obj modelio "
                   ".mtl failą (d), o .off lieka paprastos spalvos.",
    "hsv": "Spalva iš atspalvio, sodrumo ir šviesumo (visi 0..1). Atspalvis "
           "sukasi ratu, todėl hsv(i / n) duoda vaivorykštę.",
    "gradient": "Spalva tarp a ir b: t = 0 duoda a, t = 1 – b.",
    "random_color": "Atsitiktinė spalva; su seed – ta pati kaskart.",

    # -- mesh
    "Mesh": "Vienintelė bibliotekos duomenų struktūra: viršūnių sąrašas V, "
            "sienų (indeksų sąrašų) sąrašas F ir kiekvienos sienos spalva C. "
            "Suderinamumui M[0] ir M[1] tebeduoda senuosius add.py 1.2 eilučių "
            "sąrašus.",
    "as_mesh": "Priima Mesh, seną [viršūnių_eilutės, sienų_eilutės] porą arba "
               "None (dabartinę sceną) ir visada grąžina Mesh.",

    # -- scene
    "vertices": "Dabartinės scenos viršūnės add.py 1.2 eilučių pavidalu "
                "(„x y z“); langas į sceną, ne kopija.",
    "faces": "Dabartinės scenos sienos add.py 1.2 eilučių pavidalu; "
             "len(add.faces) – kiek daugiakampių jau nupiešta.",
    "scene": "Mesh objektas, į kurį šiuo metu piešiama.",
    "clear": "Išmeta viską, kas nupiešta iki šiol.",
    "layer": "Paima visą sceną kaip Mesh objektą ir pradeda naują tuščią sceną. "
             "Tai pagrindinis darbo būdas: nupiešti, paimti su layer(), "
             "transformuoti, grąžinti su mesh(). Dėmesio: paima VISKĄ, kas "
             "nupiešta iki tol – dalims patogiau make() arba push()/pop().",
    "push": "Atideda dabartinę sceną į šalį ir pradeda tuščią. Naudokite "
            "funkcijoje, kuri kuria detalę, kad ji nepasiimtų viso, kas "
            "nupiešta anksčiau.",
    "pop": "Grąžina tai, kas nupiešta nuo push(), ir atkuria senąją sceną.",
    "make": "Iškviečia piešimo funkciją ir grąžina, ką ji nupiešė, kaip Mesh, "
            "nepaliesdama dabartinės scenos: make(add.sphere, c, r) yra "
            "push(); sphere(...); pop() viename žingsnyje.",
    "mesh": "Nupiešia Mesh objektą į dabartinę sceną.",
    "paste": "Kitas vardas funkcijai mesh().",
    "merge": "Sujungia kelis Mesh objektus į vieną (geometrija nekeičiama). "
             "Sandariam sujungimui, kai dalys kertasi, naudokite union().",
    "copy": "Nepriklausoma M (arba scenos) kopija.",

    # -- flat shapes
    "polygon": "Viena plokščia siena per nurodytus 3D taškus (kiek norite "
               "kampų). Taškai eina prieš laikrodžio rodyklę, žiūrint iš išorės.",
    "triangle": "Vienas trikampis per tris taškus.",
    "quad": "Vienas keturkampis per keturis taškus.",
    "disc": "Užpildytas skritulys: spindulys r, centras center, atsuktas į "
            "normal (kryptį arba antrą tašką).",
    "ring": "Plokščias žiedas – skritulys su skyle.",
    "grid": "Stačiakampis XZ plokštumos lopas, o su height(x, z) – kalvotas "
            "reljefas. Spalva gali būti funkcija (x, z), thickness paverčia "
            "lakštą plokšte.",

    # -- boxes
    "box": "Kubas, kurio kraštinė edge, centras center.",
    "cuboid": "Stačiakampis gretasienis; sizes – kraštinių ilgiai išilgai X, Y "
              "ir Z.",
    "frame": "Dvylika kubo briaunų kaip storio thickness strypai – tuščiaviduris "
             "kubo karkasas.",
    "voxels": "Vienetinių kubelių aibės paviršius – Minecraft stiliaus modelis. "
              "cells – (i, j, k) trejetų rinkinys; piešiamos tik išorinės "
              "sienelės, todėl rezultatas sandarus.",
    "pyramid": "Keturkampė piramidė: pagrindo kraštinė edge, viršūnė height "
               "aukštyje (neigiamas height – žemyn).",
    "prism": "Kūnas su pastoviu skerspjūviu: 2D profilis ištemptas per height "
             "išilgai axis.",

    # -- polyhedra
    "polyhedron": "Vienas iš penkių taisyklingųjų briaunainių (Platono kūnų) "
                  "pagal vardą, įbrėžtas į spindulio r sferą. Viršūnių "
                  "koordinačių vidurkis yra tiksliai center.",
    "tetrahedron": "Taisyklingasis tetraedras: 4 viršūnės, 4 trikampiai, "
                   "apibrėžtinės sferos spindulys r.",
    "octahedron": "Taisyklingasis oktaedras: 6 viršūnės, 8 trikampiai.",
    "dodecahedron": "Taisyklingasis dodekaedras: 20 viršūnių, 12 penkiakampių.",
    "icosahedron": "Taisyklingasis ikosaedras: 12 viršūnių, 20 trikampių. Nuo "
                   "jo prasideda geodezinė sfera (sphere) ir futbolo kamuolys "
                   "(truncate).",
    "polyhedron_points": "Platono kūno viršūnių koordinatės kaip taškų sąrašas "
                         "(vidurkis lygiai center). Tinka daiktams tolygiai "
                         "išdėstyti aplink tašką.",
    "polyhedron_faces": "Platono kūno sienų lentelė: indeksų sąrašai į "
                        "polyhedron_points, prieš laikrodžio rodyklę iš išorės.",

    # -- numbers, profiles
    "lerp": "Tiesinis perėjimas nuo a (t = 0) iki b (t = 1); veikia ir "
            "skaičiams, ir taškams.",
    "clamp": "x, apribotas intervalu lo..hi.",
    "remap": "Perkelia x iš intervalo a0..a1 į intervalą b0..b1.",
    "distance": "Atstumas tarp dviejų taškų (2D arba 3D).",
    "midpoint": "Atkarpos tarp a ir b vidurio taškas.",
    "direction": "Vienetinis vektorius iš a į b.",
    "rotate_point": "Pasuka vieną tašką aplink ašį, einančią per P (Rodrigues "
                    "formulė). Tinka, pavyzdžiui, švaistiklio kaiščio padėčiai "
                    "pagal rato kampą.",
    "shade": "Tamsesnė (factor < 1) arba šviesesnė (factor > 1) spalvos "
             "versija.",
    "chaikin": "Suapvalina laužtės kampus juos nukirsdama (Chaikin algoritmas).",
    "profile_circle": "k taškų ant spindulio r apskritimo – skerspjūvis "
                      "funkcijoms prism, extrude, sweep.",
    "profile_ellipse": "k taškų ant elipsės su pusašiais a ir b.",
    "profile_polygon": "Taisyklingas n-kampis su apibrėžtinio apskritimo "
                       "spinduliu r.",
    "profile_star": "Žvaigždė su n spinduliais, pakaitomis dviem spinduliais.",
    "profile_rect": "Stačiakampis w × h, kurio kampai gali būti suapvalinti "
                    "spinduliu r.",
    "profile_gear": "Krumpliaračio kontūras: teeth dantų, depth aukščio, ant "
                    "spindulio r.",
    "points_on_line": "n taškų, tolygiai išdėstytų nuo a iki b (įskaitant abu).",
    "points_on_circle": "n taškų, tolygiai išdėstytų ant apskritimo plokštumoje, "
                        "statmenoje axis.",
    "points_on_helix": "n taškų ant spiralės (sraigtinės linijos), kylančios per "
                       "pitch kiekvienu apsisukimu.",
    "points_on_spiral": "n taškų ant plokščios spiralės, kurios spindulys auga "
                        "nuo r0 iki r1.",
    "points_on_curve": "n taškų path(t), kai t tolygiai eina per t0..t1.",
}

EXAMPLES = {
    "EPS": "print(add.EPS)                       # 1e-09",
    "DEFAULT_COLOR": "add.box([0, 0, 0], 1)                 # drawn in add.DEFAULT_COLOR\nprint(add.DEFAULT_COLOR)",
    "BOOL_EPS": "print(add.BOOL_EPS)",
    "COLORS": 'print(sorted(add.COLORS))            # "black", "blue", "brown", ...\nadd.box([0, 0, 0], 1, "gold")',
    "PALETTE": 'print(add.PALETTE)\nadd.pixels(["rgb", "b.r"], 0.5)      # letters of the palette',
    "SKETCHFAB_MB": "print(add.SKETCHFAB_MB, add.SKETCHFAB_COLORS)",
    "SKETCHFAB_COLORS": "add.sphere([0, 0, 0], 1, 10, \"red\")\nadd.check(max_colors=add.SKETCHFAB_COLORS)",
    "SURFACES": 'info = add.SURFACES["klein_bottle"]\nprint(info["note"], info["u"], info["v"], info["params"])',

    "rgb": 'print(add.rgb("sky"), add.rgb("#ff8000"), add.rgb((1.0, 0.5, 0.0)))\nprint(add.rgb([0, 0, 255, 0.5]))       # with an opacity',
    "transparent": 'glass = add.transparent("sky", 0.35)\nadd.cuboid([0, 1, 0], [2, 1.5, 0.05], glass)     # a window pane\nadd.save("window.obj")                           # opacity goes into the .mtl',
    "hsv": "for i in range(12):\n    add.box([i, 0, 0], 0.9, add.hsv(i / 12.0))",
    "gradient": 'for i in range(10):\n    add.box([i, 0, 0], 0.9, add.gradient(i / 9.0, "navy", "white"))',
    "random_color": "add.seed(1)\nfor i in range(5):\n    add.box([i, 0, 0], 0.9, add.random_color())\nprint(add.random_color(7) == add.random_color(7))   # True",

    "Mesh": "M = add.Mesh()\na = M.add_vertex([0, 0, 0])\nb = M.add_vertex([1, 0, 0])\nc = M.add_vertex([0, 1, 0])\nM.add_face([a, b, c], \"red\")\nprint(M, M.polygons, M.V[1], M.F[0], M.C[0])\nadd.mesh(M)",
    "as_mesh": 'add.box([0, 0, 0], 1, "red")\nM = add.as_mesh(None)                 # the scene itself\npair = [list(M[0]), list(M[1])]       # the old string lists ...\nprint(add.as_mesh(pair).polygons)     # ... accepted anywhere',

    "vertices": 'add.box([0, 0, 0], 1, "red")\nprint(len(add.vertices), add.vertices[0])',
    "faces": 'add.box([0, 0, 0], 1, "red")\nprint(len(add.faces), add.faces[0])',
    "scene": 'add.box([0, 0, 0], 1, "red")\nprint(add.scene())                    # <Mesh 8 vertices, 6 faces>',
    "clear": 'add.box([0, 0, 0], 1, "red")\nadd.clear()\nprint(len(add.faces))                 # 0',
    "layer": 'add.box([0, 0, 0], 1, "red")\nbrick = add.layer()                    # the scene is empty again\nfor i in range(5):\n    add.mesh(add.move(brick, [i * 1.2, 0, 0]))',
    "push": 'add.box([0, 0, 0], 1, "red")           # already in the scene\nadd.push()\nadd.sphere([0, 0, 0], 1, 10, "blue")\nball = add.pop()                       # only the sphere\nprint(ball.polygons, len(add.faces))    # 1280 6',
    "pop": 'add.push()\nadd.cylinder([0, 0, 0], [0, 2, 0], 0.5, 24, "gold")\npart = add.pop()\nadd.mesh(add.move(part, [3, 0, 0]))',
    "make": 'ball = add.make(add.sphere, [0, 0, 0], 1, 10, "red")\nadd.mesh(add.move(ball, [3, 0, 0]))\nadd.mesh(add.move(ball, [-3, 0, 0]))',
    "mesh": 'ball = add.make(add.sphere, [0, 0, 0], 1, 10, "red")\nadd.mesh(ball)\nadd.mesh(add.move(ball, [2.5, 0, 0]))',
    "paste": 'ball = add.make(add.sphere, [0, 0, 0], 1, 10, "red")\nadd.paste(ball)                        # same as add.mesh(ball)',
    "merge": 'a = add.make(add.box, [0, 0, 0], 1, "red")\nb = add.make(add.sphere, [2, 0, 0], 0.6, 10, "blue")\nboth = add.merge([a, b])\nprint(both.polygons)\nadd.mesh(both)',
    "copy": 'add.box([0, 0, 0], 1, "red")\nM = add.copy()                         # a copy of the scene\nM.V[0][1] += 5                         # the scene is untouched\nprint(add.scene().V[0][1])',

    "polygon": 'add.polygon([[0, 0, 0], [2, 0, 0], [2, 2, 0], [1, 3, 0], [0, 2, 0]], "gold")',
    "triangle": 'add.triangle([0, 0, 0], [2, 0, 0], [1, 2, 0], "red")',
    "quad": 'add.quad([0, 0, 0], [2, 0, 0], [2, 2, 0], [0, 2, 0], "sky")',
    "disc": 'add.disc([0, 0, 0], [0, 1, 0], 2, 48, "gold")     # facing up',
    "ring": 'add.ring([0, 0, 0], [0, 1, 0], 2, 1.5, 48, "silver")',
    "grid": 'def hills(x, z):\n    return 0.6 * add.sin(x) * add.cos(z)\n\nadd.grid([0, 0, 0], [10, 10], 40, 40, height=hills,\n         color=lambda x, z: "sky" if hills(x, z) < 0 else "green")',

    "box": 'add.box([0, 0, 0], 2, "red")',
    "cuboid": 'add.cuboid([0, 0, 0], [4, 1, 2], "brown")',
    "frame": 'add.frame([0, 0, 0], 3, 0.2, "gold")',
    "voxels": 'blocks = {(x, y, z) for x in range(6) for y in range(3)\n                    for z in range(6) if (x + y + z) % 3}\nadd.voxels(blocks, 0.5, color="sky")',
    "pyramid": 'add.pyramid([0, 0, 0], 3, 2, "gold")',
    "prism": 'add.prism(add.profile_star(5, 1.0, 0.5), 2, "purple")\nadd.prism([[0, 0], [1, 0], [0.5, 1]], 3, "gold", center=[3, 0, 0])',

    "polyhedron": 'for i, name in enumerate(["tetrahedron", "cube", "octahedron",\n                          "dodecahedron", "icosahedron"]):\n    add.polyhedron(name, [i * 2.5, 0, 0], 1, add.hsv(i / 5.0))',
    "tetrahedron": 'add.tetrahedron([0, 0, 0], 1.5, "red")',
    "octahedron": 'add.octahedron([0, 0, 0], 1.5, "green")',
    "dodecahedron": 'add.dodecahedron([0, 0, 0], 1.5, "gold")',
    "icosahedron": 'add.icosahedron([0, 0, 0], 1.5, "purple")\nico = add.make(add.icosahedron, [0, 0, 0], 1.5)\nprint(add.valence(ico, 0), add.mean_edge_length(ico))',
    "polyhedron_points": 'for p in add.polyhedron_points("icosahedron", [0, 0, 0], 2):\n    add.cone([0, 0, 0], p, 0.3, 12, "red")          # twelve spikes',
    "polyhedron_faces": 'P = add.polyhedron_points("cube", [0, 0, 0], 1)\nfor f in add.polyhedron_faces("cube"):\n    add.polygon([P[i] for i in f], "sky")           # the cube, face by face',

    "lerp": "print(add.lerp(0, 10, 0.25))                  # 2.5\nprint(add.lerp([0, 0, 0], [2, 4, 6], 0.5))     # [1.0, 2.0, 3.0]",
    "clamp": "print(add.clamp(1.7), add.clamp(-3, -1, 1))   # 1.0 -1",
    "remap": "print(add.remap(5, 0, 10, -1, 1))            # 0.0",
    "distance": "print(add.distance([0, 0, 0], [3, 4, 0]))     # 5.0",
    "midpoint": "print(add.midpoint([0, 0, 0], [2, 2, 2]))     # [1.0, 1.0, 1.0]",
    "direction": "print(add.direction([0, 0, 0], [0, 5, 0]))    # (0.0, 1.0, 0.0)",
    "rotate_point": "pin = add.rotate_point([1, 0, 0], [0, 0, 1], add.pi / 2)\nprint([round(c, 6) for c in pin])              # [0, 1, 0]",
    "shade": 'dark = add.shade("gold", 0.6)\nadd.box([0, 0, 0], 1, "gold")\nadd.box([1.5, 0, 0], 1, dark)',
    "chaikin": "outline = add.chaikin([[0, 0], [2, 0], [2, 2], [0, 2]], 3, closed=True)\nadd.prism(outline, 1, \"teal\")             # a rounded square bar",
    "profile_circle": 'add.extrude(add.profile_circle(1, 24), [0, 3, 0], "gold")',
    "profile_ellipse": 'add.extrude(add.profile_ellipse(1.5, 0.7, 32), [0, 2, 0], "sky")',
    "profile_polygon": 'add.prism(add.profile_polygon(6, 1), 2, "gold")',
    "profile_star": 'add.prism(add.profile_star(5, 1.0, 0.45), 0.5, "gold")',
    "profile_rect": 'add.extrude(add.profile_rect(2, 1, 0.3), [0, 3, 0], "purple")',
    "profile_gear": 'add.prism(add.profile_gear(12, 1.0, 0.25), 0.4, "silver")',
    "points_on_line": 'for p in add.points_on_line([0, 0, 0], [8, 0, 0], 5):\n    add.sphere(p, 0.3, 6, "red")',
    "points_on_circle": 'for p in add.points_on_circle([0, 0, 0], 3, 12):\n    add.box(p, 0.5, "gold")',
    "points_on_helix": 'for p in add.points_on_helix([0, 0, 0], 2, 1.5, 3, 60):\n    add.sphere(p, 0.2, 6, "sky")',
    "points_on_spiral": 'for p in add.points_on_spiral([0, 0, 0], 0.5, 4, 3, 80):\n    add.box(p, 0.25, "purple")',
    "points_on_curve": 'wave = lambda t: [t, add.sin(t), 0]\nfor p in add.points_on_curve(wave, 0, 2 * add.pi, 20):\n    add.sphere(p, 0.15, 6, "red")',
}

# --------------------------------------------------------------------------
#  round solids, axes, parts, surfaces, curves, catalogue
# --------------------------------------------------------------------------

EXPLAIN_LT.update({
    "revolve": "Apsuka 2D profilį aplink ašį A→B (tekinimo staklės). profile(t) "
               "grąžina [spindulys, aukštis]; steps – smulkumas išilgai profilio, "
               "k – aplink ašį. Spalva gali būti funkcija color(t, kampas), "
               "angle mažesnis už pilną apsisukimą palieka išpjovą.",
    "spin3D": "add.py 1.2 tekinimo funkcija: apsuka kreivę S(t) = [spindulys, "
              "aukštis] aplink A→B be dangtelių.",
    "icosphere": "Geodezinė sfera: ikosaedro trikampiai dalijami į keturis ir "
                 "naujos viršūnės išstumiamos ant sferos subdivisions kartų "
                 "(0..7). Sienų skaičius 20·4^subdivisions; spalva gali būti "
                 "sienos krypties funkcija.",
    "sphere": "Sfera iš trikampių – observatorijos kupolo principu: ikosaedras, "
              "kurio trikampiai vis dalijami į keturis, o vidurio taškai "
              "projektuojami į sferą. k – įprastas add.py smulkumo skaičius: "
              "k=10 duoda 1280 trikampių, k=20 – 5120. Lygį galima nurodyti ir "
              "tiesiogiai per subdivisions=.",
    "quadsphere": "Sfera iš šešių išgaubtų kvadratinių lopų (visos sienos "
                  "keturkampės), 6·k·k sienų – toks buvo sphere iki 1.2 "
                  "versijos ir tokia yra „Minecraft sfera“ (kubas, išpūstas į "
                  "rutulį).",
    "ellipsoid": "Kaip quadsphere, bet su atskirais spinduliais X, Y ir Z "
                 "kryptimis.",
    "uvsphere": "Gaublio tipo sfera: nu dienovidinių ir nv lygiagrečių.",
    "torus": "Riestainis: spindulio r vamzdis, apsuktas aplink spindulio R "
             "apskritimą.",
    "cylinder": "Uždaras cilindras nuo A iki B, spindulys r, k šonų.",
    "tube": "Cilindras be dangtelių – tik šoninė siena (senasis cylinder2).",
    "cup": "Cilindras, uždarytas tik A gale (senasis cylinder3).",
    "cone": "Uždaras kūgis: pagrindas spindulio r taške A, viršūnė B.",
    "cone_open": "Tik nuožulni kūgio siena (senasis cone2).",
    "frustum": "Nupjautas kūgis: spindulys r1 taške A, r2 taške B.",
    "pipe": "Tuščiaviduris vamzdis – cilindras su cilindrine skyle.",
    "capsule": "Cilindras su pusrutuliais abiejuose galuose („tabletė“).",
    "arrow": "Strypas nuo A iki B su kūgio smaigaliu – vektoriams vaizduoti.",
    "helix": "Spyruoklė – spiralinis vamzdis, apsisukantis turns kartų aplink "
             "axis.",
    "axes": "Nupiešia koordinačių ašis: X raudona, Y žalia, Z mėlyna, su "
            "raidėmis.",

    "beam": "Stačiakampis strypas nuo taško A iki taško B: sijos, kabeliai, "
            "stalo kojos. up nurodo, kur strypo „viršus“.",
    "rounded_box": "Dėžė, kurios visos briaunos ir kampai suapvalinti spinduliu r.",
    "hemisphere": "Pusė rutulio plokščiu dugnu: kupolas, dubuo, šalmas.",
    "arch": "Lenkta arka, stovinti ant žemės taškuose A ir B.",
    "stairs": "Vientisi n pakopų laiptai, prasidedantys taške origin.",
    "gear": "Krumpliaratis su teeth dantų, gulintis plokštumoje, statmenoje axis; "
            "hole – skylė ašiai.",
    "wheel": "Ratas, kurio ašis nukreipta išilgai axis; spokes – stipinų skaičius.",
    "roof": "Dvišlaitis stogas virš size = [plotis_x, gylis_z] pagrindo; center "
            "– pastogės linijos vidurys, overhang – kiek stogas kyšo už sienų.",
    "column": "Klasikinė kolona, stovinti ant taško base (apačios centras).",
    "bricks": "Siena iš perslinktų plytų, prasidedanti taške origin.",
    "tree": "Paprastas medis, stovintis ant taško at: kamienas ir laja "
            "(kind – „round“, „cone“ ir kt.).",
    "pixels": "Pikselinis menas 3D: eilučių sąrašas tampa spalvotų kubelių "
              "bloku; raidės žymi paletės spalvas.",
    "heightmap": "Kubelių kolonos: heights[i][j] kubelių, sudėtų kolonoje (i, j) – "
                 "blokinis reljefas.",
    "polyline": "Apvalus vamzdis per taškų sąrašą – laidai, vamzdžiai, bėgiai, "
                "šakos; smooth suapvalina kampus.",
    "wireframe": "Nupiešia kiekvieną tinklo briauną kaip ploną strypą, o kampuose "
                 "rutuliukus. Tinka struktūrai parodyti; tinklas turi būti "
                 "nedidelis.",
    "flow": "Seka vektorinį lauką: taškų, kuriuos aplanko dalelė, sąrašas.",
    "trace": "Nupiešia flow kelią kaip vamzdį (every palieka kas n-tą tašką).",

    "parametric": "Bibliotekos širdis: nupiešia paviršių S(u, v) → [x, y, z]. "
                  "grid_u ir grid_v – kiek langelių; wrap_u/wrap_v uždaro "
                  "siūles, thickness suteikia lakštui storį, double_sided "
                  "prideda atvirkščias sienas, color gali būti funkcija (u, v).",
    "two_sided": "Kopija, kurioje kiekviena siena yra ir apversta – kai plonas "
                 "paviršius iš kitos pusės atrodo juodas ar dingsta.",
    "solidify": "Suteikia plonam paviršiui tikrą storį ir grąžina uždarą kūną: "
                "viršūnės pastumiamos išilgai normalių, kraštas užsiuvamas.",
    "sweep": "Stumia 2D skerspjūvį išilgai 3D kelio – bendriausias formų "
             "kūrimo būdas; scale ir twist gali būti funkcijos.",
    "curve": "Nupiešia 3D parametrinę kreivę kaip apvalų spindulio r vamzdį; "
             "isConnected uždaro vamzdį į kilpą, r ir color gali būti funkcijos.",
    "extrude": "Ištempia 2D figūrą į 3D kryptimi direction, pakeliui gali sukti "
               "(twist) ir siaurinti (scale).",
    "loft": "Aptraukia paviršių per pjūvių sąrašą (kiekvienas – 3D taškų žiedas).",
    "ribbon": "Plokščia juosta išilgai 3D kelio – kaip popieriaus juostelė; "
              "thickness suteikia storį.",
    "circle": "add.py 1.2 skritulys: užpildytas apskritimas su centru A, "
              "atsuktas į B.",

    "surface_names": "Vardai, kuriuos supranta surface(), abėcėlės tvarka.",
    "surface_function": "Vardinio paviršiaus funkcija f(u, v) → [x, y, z] su "
                        "įstatytomis konstantomis (jas galima pakeisti "
                        "raktažodžiais) – kai norite patys paduoti ją "
                        "parametric() su kita sritimi ar spalvinimu.",
    "surface": "Nupiešia katalogo paviršių pagal vardą: Kleino butelis, Dini, "
               "Enneper, obuolys ir kt. size sumastelio iki norimo dydžio, "
               "grid – langelių skaičius, color gali būti funkcija (u, v), o "
               "paviršiaus konstantos keičiamos raktažodžiais.",
})

EXAMPLES.update({
    "revolve": 'def vase(t):\n    return [1 + 0.4 * add.sin(3 * t), t]\n\nadd.revolve(vase, [0, 0, 0], [0, 1, 0], 0, 4, 60, 40, "teal")\nadd.revolve(vase, [4, 0, 0], [4, 1, 0], 0, 4, 60, 40,\n            color=lambda t, a: add.hsv(t / 4.0))',
    "spin3D": "add.spin3D([0, 0, 0], [0, 1, 0], lambda t: [1 + 0.3 * add.sin(4 * t), t],\n           0, 3, 40, 32, [200, 120, 60])",
    "icosphere": 'add.icosphere([0, 0, 0], 2, 4, lambda d: "white" if d[1] > 0.7 else "blue")\nadd.icosphere([5, 0, 0], 2, 1, "gold")            # 80 triangles',
    "sphere": 'add.sphere([0, 0, 0], 1.5, 20, "sky")             # 5120 triangles\nadd.sphere([4, 0, 0], 1.5, 5, "gold")             # 320\nadd.sphere([8, 0, 0], 1.5, subdivisions=2, color="red")',
    "quadsphere": 'add.quadsphere([0, 0, 0], 1.5, 12, "sky")          # 864 quads',
    "ellipsoid": 'add.ellipsoid([0, 0, 0], [3, 1, 1.5], 12, "gold")',
    "uvsphere": 'add.uvsphere([0, 0, 0], 1.5, 32, 16, "sky")',
    "torus": 'add.torus([0, 0, 0], 3, 0.8, 48, 24, "gold")\nadd.torus([0, 0, 0], 3, 0.3, 48, 12, "silver", axis=[1, 0, 0])',
    "cylinder": 'add.cylinder([0, 0, 0], [0, 3, 0], 0.5, 24, "gold")',
    "tube": 'add.tube([0, 0, 0], [0, 3, 0], 0.5, 24, "gold")',
    "cup": 'add.cup([0, 0, 0], [0, 2, 0], 0.8, 32, "teal")',
    "cone": 'add.cone([0, 0, 0], [0, 3, 0], 1, 32, "red")',
    "cone_open": 'add.cone_open([0, 0, 0], [0, 3, 0], 1, 32, "red")',
    "frustum": 'add.frustum([0, 0, 0], [0, 2, 0], 1.0, 0.5, 32, "gold")',
    "pipe": 'add.pipe([0, 0, 0], [0, 3, 0], 0.6, 0.4, 32, "silver")',
    "capsule": 'add.capsule([0, 0, 0], [0, 3, 0], 0.5, 24, "red")',
    "arrow": 'add.arrow([0, 0, 0], [3, 2, 0], 0.08, "red")',
    "helix": 'add.helix([0, 0, 0], 1.5, 0.8, 5, 300, 0.15, 12, "silver")',
    "axes": "add.axes([0, 0, 0], 3)\nadd.box([1, 1, 1], 1, \"gold\")",

    "beam": 'add.beam([0, 0, 0], [4, 2, 1], 0.3, 0.2, "brown")',
    "rounded_box": 'add.rounded_box([0, 0, 0], [3, 2, 1], 0.3, 8, "sky")',
    "hemisphere": 'add.hemisphere([0, 0, 0], 2, 16, "gold")',
    "arch": 'add.arch([-2, 0, 0], [2, 0, 0], 3, 0.4, "grey")',
    "stairs": 'add.stairs([0, 0, 0], 8, 2, 0.3, 0.5, "grey")',
    "gear": 'add.gear([0, 0, 0], 16, 2, 0.4, "silver", hole=0.4)',
    "wheel": 'add.wheel([0, 0, 0], 1.5, 0.5, "black", spokes=8)',
    "roof": 'add.cuboid([0, 1, 0], [4, 2, 3], "brown")\nadd.roof([0, 2, 0], [4, 3], 1.2, [120, 40, 30], overhang=0.3)',
    "column": 'add.column([0, 0, 0], 4, 0.4, "white")',
    "bricks": 'add.bricks([0, 0, 0], 6, 3, color="brown")',
    "tree": 'add.tree([0, 0, 0], 4)\nadd.tree([3, 0, 0], 3, kind="cone")',
    "pixels": 'add.pixels(["..r..",\n            ".rrr.",\n            "rrrrr",\n            "..g..",\n            "..g.."], 0.5, color="red")',
    "heightmap": 'add.heightmap([[1, 2, 3], [2, 4, 2], [3, 2, 1]], 0.8, color="green")',
    "polyline": 'add.polyline([[0, 0, 0], [2, 1, 0], [3, 3, 1], [1, 4, 0]], 0.15, 12, "sky", smooth=2)',
    "wireframe": 'cube = add.make(add.box, [0, 0, 0], 2)\nadd.wireframe(cube, 0.05, 8, "gold")',
    "flow": "field = lambda p: [-p[2], 0.3, p[0]]           # a spiral field\npts = add.flow(field, [1, 0, 0], 0.05, 200)\nprint(len(pts), pts[-1])",
    "trace": "field = lambda p: [-p[2], 0.3, p[0]]\nadd.trace(field, [1, 0, 0], 0.05, 200, 0.08, 8, \"red\")",

    "parametric": 'def torus(u, v):\n    return [(3 + add.cos(u)) * add.cos(v), add.sin(u), (3 + add.cos(u)) * add.sin(v)]\n\nadd.parametric(torus, 0, 2 * add.pi, 24, 0, 2 * add.pi, 60, "gold",\n               wrap_u=True, wrap_v=True)\nadd.parametric(lambda u, v: [u, add.sin(u) * add.cos(v), v], -3, 3, 30, -3, 3, 30,\n               thickness=0.1, color=lambda u, v: add.hsv(u / 6.0))',
    "two_sided": 'sheet = add.make(add.grid, [0, 0, 0], [4, 4], 10, 10, "sky")\nadd.mesh(add.two_sided(sheet))',
    "solidify": 'sheet = add.make(add.parametric, lambda u, v: [u, add.sin(u) * add.cos(v), v],\n                 -3, 3, 30, -3, 3, 30, "sky")\nadd.mesh(add.solidify(sheet, 0.2))',
    "sweep": 'path = lambda t: [add.cos(t) * 3, t * 0.5, add.sin(t) * 3]\nadd.sweep(add.profile_star(5, 0.5, 0.25), path, 0, 4 * add.pi, 120, "gold",\n          twist=lambda t: t)',
    "curve": "def knot(t):\n    return [add.sin(t) + 2 * add.sin(2 * t), add.cos(t) - 2 * add.cos(2 * t), -add.sin(3 * t)]\n\nadd.curve(knot, 0, 2 * add.pi, 200, 16, 0.25, \"red\", True)",
    "extrude": 'add.extrude(add.profile_star(6, 1.0, 0.5), [0, 3, 0], "gold",\n            steps=40, twist=add.pi, scale=lambda t: 1 - 0.5 * t)',
    "loft": "rings = []\nfor i in range(6):\n    r = 1 + 0.5 * add.sin(i)\n    rings.append([[r * add.cos(a), i, r * add.sin(a)]\n                  for a in [2 * add.pi * k / 24 for k in range(24)]])\nadd.loft(rings, \"teal\")",
    "ribbon": 'add.ribbon(lambda t: [add.cos(t) * 2, t * 0.3, add.sin(t) * 2], 0, 4 * add.pi, 120, 0.5,\n           "purple", twist=lambda t: t / 2)',
    "circle": 'add.circle([0, 0, 0], [0, 1, 0], 2, 32, [255, 200, 0])',

    "surface_names": "print(add.surface_names())",
    "surface_function": 'owl = add.surface_function("owl")\nadd.parametric(owl, 0, 4 * add.pi, 120, 0.001, 1, 30,\n               color=lambda u, v: add.hsv(v), thickness=0.03)',
    "surface": 'add.surface("klein_bottle", [0, 0, 0], 4, 100, "teal")\nadd.surface("apple", [6, 0, 0], 3, color=lambda u, v: add.hsv(u / 6.3))\nadd.surface("pillow", [-6, 0, 0], 3, a=0.9, thickness=0.1)',
})

# --------------------------------------------------------------------------
#  measuring, transforms, colour, patterns, placing, repair
# --------------------------------------------------------------------------

EXPLAIN_LT.update({
    "bbox": "Tinklo gaubiantis stačiakampis: [[xmin, ymin, zmin], [xmax, ymax, "
            "zmax]].",
    "size": "Tinklo plotis, aukštis ir gylis.",
    "center": "Visų viršūnių vidurkis (tai, ką add.py 1.2 vadino centru).",
    "middle": "Gaubiančio stačiakampio centras – dažniausiai tai, ko iš tikrųjų "
              "reikia.",
    "area": "Visas paviršiaus plotas.",
    "volume": "Uždaro kūno tūris (prasmingas tik sandariam tinklui).",
    "move": "Pastumia tinklą vektoriumi V (grąžina naują tinklą; originalas "
            "nekeičiamas, kaip ir visose transformacijose).",
    "place": "Perkelia tinklą taip, kad jo centras atsidurtų taške at.",
    "rotateX": "Pasuka tinklą aplink X ašį, einančią per tašką P.",
    "rotateY": "Pasuka tinklą aplink Y ašį, einančią per tašką P.",
    "rotateZ": "Pasuka tinklą aplink Z ašį, einančią per tašką P.",
    "rotate": "Pasuka tinklą kampu angle aplink bet kokią ašį per P (Rodrigues "
              "formulė).",
    "zoom": "Padidina arba sumažina tinklą s kartų (pagal nutylėjimą apie jo "
            "paties centrą).",
    "stretch": "Mastelis skirtingas kiekvienai ašiai: s = [sx, sy, sz].",
    "fit": "Sumastelio tinklą taip, kad didžiausias jo matmuo būtų target.",
    "mirror": "Atspindi tinklą plokštumoje per point su normale normal; sienų "
              "kryptis irgi apverčiama, kad atspindys nebūtų išverstas.",
    "transform": "Pritaiko 3×3 arba 4×4 matricą (eilučių sąrašą).",
    "deform": "Perlenkia tinklą bet kokia funkcija f(p) → naujas taškas – "
              "galingiausia bibliotekos funkcija.",
    "twist": "Sukinėja tinklą vis labiau išilgai ašies – kamščiatraukis; angle "
             "– posūkis vienam ilgio vienetui.",
    "taper": "Siaurina (ar platina) tinklą išilgai ašies: factor – papildomas "
             "mastelis vienam ilgio vienetui.",
    "bend": "Sulenkia tinklą į lanką: atstumas išilgai axis virsta kampu aplink "
            "around.",
    "jitter": "Truputį pastumdo kiekvieną viršūnę atsitiktinai – rankų darbo "
              "įspūdis.",

    "color": "Nudažo visą tinklą viena spalva ir grąžina nudažytą kopiją.",
    "opacity": "Kopija, kurioje kiekviena siena permatoma: alpha – nepermatomumas "
               "(0 nematoma, 1 vientisa, ir tai pašalina permatomumą). Spalvos "
               "ir tekstūros išlieka; į .obj modelio .mtl failą įrašoma d.",
    "texture": "Apvynioja tinklą paveikslėliu (.png ar .jpg failas šalia .obj) "
               "ir grąžina kopiją su tekstūros koordinatėmis kiekvienam kampui. "
               "mapping – „box“ (kiekviena siena projektuojama pagal savo "
               "kryptį), „xy“/„xz“/„yz“, „fit“ (paveikslėlis ištemptas per visą "
               "objektą), „sphere“, „cylinder“ arba sava funkcija (taškas, "
               "normalė) → (u, v). color atspalvina paveikslėlį. Tekstūras "
               "dėkite paskutines: transformacijos, clean ir merge jas išlaiko, "
               "o loginės operacijos ir apvalinimas perkuria sienas ir jas "
               "praranda. Į .mtl įrašoma map_Kd.",
    "color_by": "Nudažo kiekvieną sieną pagal jos vietą: fn(taškas) → spalva, "
                "kur taškas – sienos centras.",
    "color_gradient": "Nudažo tinklą perėjimu nuo spalvos a iki b išilgai vienos "
                      "ašies.",
    "color_random": "Kiekvienai sienai – sava atsitiktinė spalva.",
    "palette": "Skirtingos tinklo spalvos, dažniausios pirmos, kaip [(spalva, "
               "sienų skaičius), ...].",
    "limit_colors": "Sumažina tinklo spalvų skaičių iki n ir grąžina kopiją: "
                    "panašūs atspalviai sugrupuojami (median-cut kvantavimas) ir "
                    "pakeičiami vidurkiu. Kiekviena .obj spalva Sketchfab yra "
                    "medžiaga, o jų leidžiama iki 100 – 50 saugu. Permatomos ir "
                    "tekstūruotos medžiagos paliekamos.",

    "repeat": "Pakartotinai taiko transformaciją step(tinklas, i) ir sujungia "
              "kopijas – bendriausias raštų kūrimo būdas.",
    "array_linear": "n kopijų eilėje, kiekviena pastumta per step.",
    "array_grid": "2D arba 3D kopijų blokas; steps ir counts turi po 3 reikšmes.",
    "array_radial": "n kopijų aplink ašį; rise paverčia ratą sraigtiniais "
                    "laiptais.",
    "array_mirror": "Tinklas kartu su savo veidrodiniu atspindžiu.",
    "aim": "Pasuka tinklą taip, kad jo ašis axis rodytų kryptimi direction.",
    "ground": "Nuleidžia (ar pakelia) tinklą taip, kad žemiausias jo taškas būtų "
              "aukštyje y.",
    "align": "Perkelia tinklą taip, kad pasirinktas jo gaubiančio stačiakampio "
             "taškas (anchor) atsidurtų taške at.",
    "random_points": "n atsitiktinių taškų dėžėje lo..hi; su height(x, z) taškai "
                     "guli ant reljefo.",
    "scatter": "Tinklo kopijos kiekviename taške, kiekviena atsitiktinai pasukta "
               "ir sumastelinta.",
    "along": "n tinklo kopijų, suvertų išilgai kreivės, kiekviena pasukta pagal "
             "jos kryptį.",

    "heal": "Užtaiso mažyčius plyšius ten, kur briauna praeina pro kitos sienos "
            "viršūnę (T sandūros) – po loginių operacijų modelis vėl sandarus.",
    "triangulate": "Kopija, kurioje kiekviena siena – trikampis.",
    "fix_normals": "Padaro, kad visos kopijos sienos žiūrėtų į tą pačią pusę, o "
                   "uždaro modelio – į išorę.",
    "clean": "Sutvarko modelį ir grąžina kopiją: sulieja sutampančias viršūnes, "
             "išmeta nulinio ploto ir pasikartojančias sienas bei sienas, "
             "paslėptas ten, kur du kūnai liečiasi, o mažesnę iš dviejų toje "
             "pačioje plokštumoje persidengiančių sienų apkerpa (overlaps=True), "
             "kad modelis peržiūroje nemirgėtų; neiškilas sienas supjausto "
             "trikampiais (convex=True). normals=True dar ir atsuka "
             "sienas į išorę. save() tai daro pats (clean=True).",
    "overlaps": "Kiek sienų guli vienoje plokštumoje su didesne siena ir su ja "
                "persidengia – žiūrinčios ta pačia kryptimi peržiūroje mirga, o "
                "nugaromis viena į kitą (kūnas ant kūno) slepia nematomą lopą. "
                "clean() (ir save()) jas apkerpa; check() apie jas praneša.",
    "concave_faces": "Kiek sienų nėra iškilos. Peržiūros programa daugiakampį piešia "
                     "kaip trikampių vėduoklę iš pirmojo kampo, todėl neiškilos sienos "
                     "įdubą (pvz., laiptų angą grindyse) uždengia. clean() (ir save()) "
                     "tokias sienas supjausto trikampiais; check() apie jas praneša.",
    "stats": "Žodynas apie modelį: viršūnių, sienų, spalvų skaičius, matmenys, "
             "plotas, tūris, sandarumas, .obj dydis, permatomos sienos, "
             "tekstūros.",
    "check": "Atspausdina modelio būklės ataskaitą ir pasako, ar jis atitinka "
             "užduotį: ≥ 10000 daugiakampių, ≥ 3 spalvos, uždaras paviršius, "
             "ir ar .obj tiktų Sketchfab (≤ 50 MB, ≤ 50 spalvų). Grąžina True, "
             "kai viskas tvarkoje.",
})

EXAMPLES.update({
    "bbox": 'M = add.make(add.sphere, [1, 2, 3], 1, 5)\nprint(add.bbox(M))',
    "size": 'M = add.make(add.cuboid, [0, 0, 0], [4, 1, 2])\nprint(add.size(M))                    # [4.0, 1.0, 2.0]',
    "center": 'M = add.make(add.box, [1, 2, 3], 2)\nprint(add.center(M))                  # [1.0, 2.0, 3.0]',
    "middle": 'M = add.make(add.cone, [0, 0, 0], [0, 4, 0], 1, 12)\nprint(add.middle(M), add.center(M))   # bbox centre vs. vertex average',
    "area": 'M = add.make(add.box, [0, 0, 0], 2)\nprint(add.area(M))                    # 24.0',
    "volume": 'M = add.make(add.sphere, [0, 0, 0], 1, 20)\nprint(round(add.volume(M), 3), round(4 / 3 * add.pi, 3))',
    "move": 'ball = add.make(add.sphere, [0, 0, 0], 1, 10, "red")\nadd.mesh(add.move(ball, [3, 0, 0]))',
    "place": 'ball = add.make(add.sphere, [7, 7, 7], 1, 10, "red")\nadd.mesh(add.place(ball, [0, 1, 0]))   # now centred at (0, 1, 0)',
    "rotateX": 'bar = add.make(add.cuboid, [0, 0, 0], [1, 4, 1], "gold")\nadd.mesh(add.rotateX(bar, add.pi / 4))',
    "rotateY": 'bar = add.make(add.cuboid, [3, 0, 0], [1, 1, 4], "gold")\nfor i in range(6):\n    add.mesh(add.rotateY(bar, i * add.pi / 3))',
    "rotateZ": 'bar = add.make(add.cuboid, [0, 0, 0], [4, 1, 1], "gold")\nadd.mesh(add.rotateZ(bar, add.pi / 6, [-2, 0, 0]))',
    "rotate": 'bar = add.make(add.cuboid, [0, 0, 0], [4, 1, 1], "gold")\nadd.mesh(add.rotate(bar, [1, 1, 0], add.pi / 3))',
    "zoom": 'ball = add.make(add.sphere, [0, 0, 0], 1, 10, "red")\nadd.mesh(add.zoom(ball, 2.5))',
    "stretch": 'ball = add.make(add.sphere, [0, 0, 0], 1, 10, "red")\nadd.mesh(add.stretch(ball, [3, 1, 0.5]))   # an ellipsoid',
    "fit": 'ball = add.make(add.sphere, [0, 0, 0], 37, 10, "red")\nadd.mesh(add.fit(ball, 2))             # now 2 units across',
    "mirror": 'wing = add.make(add.cuboid, [2, 0, 0], [3, 0.2, 1], "gold")\nadd.mesh(wing)\nadd.mesh(add.mirror(wing, [0, 0, 0], [1, 0, 0]))',
    "transform": 'M = add.make(add.box, [0, 0, 0], 1, "red")\nshear = [[1, 0.5, 0], [0, 1, 0], [0, 0, 1]]\nadd.mesh(add.transform(M, shear))',
    "deform": 'bar = add.make(add.cuboid, [0, 0, 0], [8, 0.5, 0.5], "gold")\nbar = add.refine(bar, 3)              # more vertices to bend\nadd.mesh(add.deform(bar, lambda p: [p[0], p[1] + add.sin(p[0]), p[2]]))',
    "twist": 'bar = add.make(add.cuboid, [0, 2, 0], [1, 4, 1], "gold")\nbar = add.refine(bar, 3)\nadd.mesh(add.twist(bar, 0.6))',
    "taper": 'bar = add.make(add.cuboid, [0, 2, 0], [1, 4, 1], "gold")\nadd.mesh(add.taper(bar, -0.2))         # 20 % thinner per unit of height',
    "bend": 'bar = add.make(add.cuboid, [0, 3, 0], [0.5, 6, 0.5], "gold")\nbar = add.refine(bar, 3)\nadd.mesh(add.bend(bar, 0.4, axis=1, around=0))',
    "jitter": 'rock = add.make(add.sphere, [0, 0, 0], 1, 5, "grey")\nadd.mesh(add.jitter(rock, 0.08, seed=1))',

    "color": 'ball = add.make(add.sphere, [0, 0, 0], 1, 10, "red")\nadd.mesh(add.color(ball, "blue"))',
    "opacity": 'glass = add.opacity(add.make(add.box, [0, 0, 0], 2, "sky"), 0.3)\nadd.mesh(glass)\nadd.sphere([0, 0, 0], 0.5, 10, "red")  # seen through the glass in .obj',
    "texture": 'rows = [["white" if (x // 8 + y // 8) % 2 else "black"\n         for x in range(64)] for y in range(64)]\nadd.write_png("check.png", rows)\nwall = add.make(add.cuboid, [0, 0, 0], [4, 2, 0.3])\nadd.mesh(add.texture(wall, "check.png", "box", scale=1.0))\nball = add.make(add.sphere, [0, 3, 0], 1, 10)\nadd.mesh(add.texture(ball, "check.png", "sphere", scale=4))\nadd.save("textured.obj")               # .obj + .mtl (map_Kd check.png)',
    "color_by": 'M = add.make(add.sphere, [0, 0, 0], 2, 20)\nadd.mesh(add.color_by(M, lambda p: add.hsv((p[1] + 2) / 4.0)))',
    "color_gradient": 'M = add.make(add.cylinder, [0, 0, 0], [0, 5, 0], 1, 32)\nadd.mesh(add.color_gradient(M, "navy", "white"))',
    "color_random": 'M = add.make(add.dodecahedron, [0, 0, 0], 2)\nadd.mesh(add.color_random(M, seed=3))',
    "palette": 'M = add.make(add.sphere, [0, 0, 0], 2, 10)\nM = add.color_by(M, lambda p: "red" if p[1] > 0 else "blue")\nprint(add.palette(M))                 # [((255, 0, 0), 640), ((0, 0, 255), 640)]',
    "limit_colors": 'M = add.make(add.sphere, [0, 0, 0], 2, 20)\nM = add.color_by(M, lambda p: add.hsv(p[1] / 4.0))\nprint(len(add.palette(M)))\nfew = add.limit_colors(M, 50)\nprint(len(add.palette(few)))          # 50\nadd.save("few.obj", few)',

    "repeat": 'brick = add.make(add.box, [0, 0, 0], 0.9, "red")\nspiral = add.repeat(brick, 40, lambda X, i: add.move(add.rotateY(X, i * 0.3), [3, i * 0.2, 0]))\nadd.mesh(spiral)',
    "array_linear": 'post = add.make(add.cylinder, [0, 0, 0], [0, 2, 0], 0.1, 8, "brown")\nadd.mesh(add.array_linear(post, [1.5, 0, 0], 8))',
    "array_grid": 'block = add.make(add.box, [0, 0, 0], 0.8, "sky")\nadd.mesh(add.array_grid(block, [1, 1, 1], [4, 3, 4]))',
    "array_radial": 'step = add.make(add.cuboid, [2, 0, 0], [2, 0.2, 0.6], "grey")\nadd.mesh(add.array_radial(step, 24, rise=0.25))   # a spiral staircase',
    "array_mirror": 'half = add.make(add.cone, [1, 0, 0], [3, 2, 0], 0.5, 12, "gold")\nadd.mesh(add.array_mirror(half, [0, 0, 0], [1, 0, 0]))',
    "aim": 'rocket = add.make(add.cone, [0, 0, 0], [0, 3, 0], 0.5, 16, "red")\nadd.mesh(add.aim(rocket, [1, 1, 0]))   # its axis now points along (1, 1, 0)',
    "ground": 'ball = add.make(add.sphere, [0, 5, 0], 1, 10, "red")\nadd.mesh(add.ground(ball))            # now resting on y = 0',
    "align": 'M = add.make(add.box, [0, 0, 0], 2, "gold")\nadd.mesh(add.align(M, [0, 0, 0], anchor=[-1, -1, -1]))   # corner at the origin',
    "random_points": 'pts = add.random_points(30, [-5, 0, -5], [5, 0, 5], seed=1,\n                        height=lambda x, z: 0.3 * add.sin(x) * add.cos(z))\nfor p in pts:\n    add.sphere(p, 0.2, 5, "red")',
    "scatter": 'tree = add.make(add.tree, [0, 0, 0], 2)\npts = add.random_points(12, [-6, 0, -6], [6, 0, 6], seed=2)\nadd.mesh(add.scatter(tree, pts, seed=1, scale=(0.6, 1.4)))',
    "along": 'car = add.make(add.cuboid, [0, 0.2, 0], [0.6, 0.4, 1], "red")\nloop = lambda t: [4 * add.cos(t), 0, 4 * add.sin(t)]\nadd.mesh(add.along(car, loop, 12, 0, 2 * add.pi, closed=True))',

    "heal": 'a = add.make(add.box, [0, 0, 0], 2, "red")\nb = add.make(add.box, [1, 1, 1], 2, "blue")\nfixed = add.heal(add.difference(a, b))\nprint(add.stats(fixed)["closed"])',
    "triangulate": 'M = add.make(add.box, [0, 0, 0], 2, "red")\nprint(add.triangulate(M).polygons)   # 12',
    "fix_normals": 'M = add.make(add.box, [0, 0, 0], 2, "red")\nM.F[0].reverse()                     # spoil one face\nprint(add.volume(M), add.volume(add.fix_normals(M)))',
    "clean": 'add.box([0, 0, 0], 2, "red")\nadd.box([2, 0, 0], 2, "red")          # touches the first one\nadd.cuboid([1, 0, 0], [6, 0.5, 2], "blue")   # runs through both: overlapping faces\nmodel, report = add.clean(add.layer(), report=True)\nprint(report)                         # hidden walls gone, overlaps cut\nadd.mesh(model)',
    "overlaps": 'add.cuboid([0, 0, 0], [2, 6, 1], "red")\nadd.cuboid([0, 0, 0], [5, 1, 1], "blue")   # the front faces share a plane\nprint(add.overlaps())                     # 2 -- they would flicker\nadd.mesh(add.clean(add.layer()))\nprint(add.overlaps())                     # 0',
    "concave_faces": 'add.polygon([[0, 0, 0], [0, 0, 3], [1, 0, 3], [1, 0, 1], [4, 0, 1], [4, 0, 0]], "red")   # an L\nprint(add.concave_faces())                # 1 -- a viewer would fan it over the notch\nadd.mesh(add.clean(add.layer()))\nprint(add.concave_faces())                # 0 -- cut into triangles',
    "stats": 'M = add.make(add.torus, [0, 0, 0], 3, 1)\ns = add.stats(M)\nprint(s["faces"], s["closed"], round(s["volume"], 2), s["obj_bytes"])',
    "check": 'add.sphere([0, 0, 0], 2, 30, "red")\nadd.box([3, 0, 0], 1, "blue")\nadd.cone([0, 3, 0], [0, 5, 0], 1, 12, "gold")\nok = add.check()\nprint(ok)',
})

# --------------------------------------------------------------------------
#  vertices, booleans, smoothing, files, text, old names
# --------------------------------------------------------------------------

EXPLAIN_LT.update({
    "vertex": "Viršūnės i koordinatės kaip naujas [x, y, z] sąrašas.",
    "set_vertex": "Kopija, kurioje viršūnė i perkelta į point; koordinatė None "
                  "paliekama kokia buvusi. Sienos nekeičiamos – kaip tik to reikia "
                  "prieš apvalinant su smooth().",
    "set_vertices": "Kaip set_vertex, bet kelioms viršūnėms iš karto: changes "
                    "yra {indeksas: taškas, ...}.",
    "move_vertex": "Kopija, kurioje viršūnė i pastumta vektoriumi delta.",
    "nearest_vertex": "Viršūnės, artimiausios taškui point, indeksas – kad kampą "
                      "būtų galima rinktis pagal vietą, o ne pagal numerį.",
    "edges": "Visos tinklo briaunos po vieną kartą, kaip (a, b) indeksų poros su "
             "a < b.",
    "edge_length": "Atstumas tarp viršūnių a ir b.",
    "edge_lengths": "Kiekvienos briaunos ilgis ta tvarka, kuria jas išvardija "
                    "edges().",
    "mean_edge_length": "Vidutinis briaunos ilgis – natūralus tinklo „vienetas“ "
                        "(taisyklingojo briaunainio visos briaunos lygios).",
    "adjacency": "neighbours[i] – viršūnių, sujungtų briauna su viršūne i, "
                 "sąrašas visoms viršūnėms iš karto (greičiau nei neighbors "
                 "cikle).",
    "neighbors": "Viršūnės i kaimynės – viršūnės, sujungtos su ja briauna. "
                 "Uždaram tvarkingam paviršiui jos grąžinamos eilės tvarka aplink "
                 "viršūnę (prieš laikrodžio rodyklę iš išorės).",
    "neighbours": "Britiška neighbors rašyba.",
    "valence": "Kiek briaunų (ir kaimynių) turi viršūnė i: 3 kube ir "
               "dodekaedre, 4 oktaedre, 5 ikosaedre.",
    "mean_neighbor_distance": "Vidutinis atstumas nuo viršūnės i iki jos kaimynių.",
    "vertex_faces": "Sienų, susieinančių viršūnėje i, indeksai (eilės tvarka "
                    "aplink viršūnę, kai paviršius ten uždaras ir tvarkingas).",
    "vertex_normal": "Vienetinė normalė viršūnėje i – jos sienų normalių vidurkis.",
    "face_center": "Sienos i centras (kampų vidurkis).",
    "face_normal": "Vienetinė sienos i normalė (uždarame modelyje rodo į išorę).",
    "face_area": "Sienos i plotas.",
    "face_centers": "Visų sienų centrai kaip taškų sąrašas.",
    "boundary_edges": "Briaunos, priklausančios tik vienai sienai, kaip kryptinės "
                      "(a, b) poros; tuščias sąrašas reiškia uždarą paviršių.",
    "boundary_loops": "Atviri tinklo kraštai kaip uždari viršūnių indeksų žiedai "
                      "– po vieną sąrašą kiekvienai skylei.",
    "inflate": "Išstumia kiekvieną viršūnę išilgai jos normalės per amount "
               "(neigiamas – į vidų): pripučia kamuolio skydelius, sustorina "
               "ploną formą.",
    "spherify": "Projektuoja kiekvieną viršūnę į sferą (centras – viršūnių "
                "vidurkis, spindulys – iki tolimiausios viršūnės); amount < 1 "
                "eina tik dalį kelio. Su refine() taip iš bet kokio briaunainio "
                "gaunamas geodezinis kupolas.",
    "refine": "Padalija kiekvieną sieną į keturias (trikampius) arba po "
              "keturkampį kiekvienam kampui (kitus daugiakampius) steps kartų "
              "nieko nejudinant; naujos viršūnės bendros, todėl tinklas lieka "
              "sandarus. Plokščias „observatorijos kupolo“ dalijimas.",
    "dual": "Dualusis briaunainis: viršūnė kiekvienos sienos centre ir siena "
            "kiekvienai viršūnei. Kubas ↔ oktaedras, dodekaedras ↔ ikosaedras, "
            "tetraedras – pats sau dualus.",
    "truncate": "Nupjauna visus kampus: kiekviena viršūnė virsta maža siena, o "
                "senos sienos netenka kampų. t – kiek išilgai briaunos pjaunama "
                "(1/3 iš ikosaedro daro futbolo kamuolį, 1/2 pjauna iki briaunų "
                "vidurių). Kampų sienos dažomos color.",
    "color_by_sides": "Nudažo kiekvieną sieną pagal jos kampų skaičių: colors – "
                      "žodynas, pvz. {5: „black“, 6: „white“} (futbolo kamuolys).",

    "union": "Sulieja kūnus į vieną, pašalindama viską, kas paslėpta viduje "
             "(sąjunga).",
    "difference": "Išpjauna kitus kūnus iš A (skirtumas) – taip daromos skylės "
                  "ir įpjovos.",
    "intersect": "Palieka tik erdvę, kuri bendra visiems kūnams (sankirta).",
    "symmetric_difference": "Viskas, kas yra viename kūne arba kitame, bet ne "
                            "abiejuose.",
    "add_solids": "Kitas vardas funkcijai union().",
    "subtract": "Kitas vardas funkcijai difference().",
    "common": "Kitas vardas funkcijai intersect().",
    "cut": "Perpjauna kūną begaline plokštuma ir palieka dalį už jos (tą pusę, "
           "nuo kurios normalė rodo tolyn). Daug pigiau už loginę operaciją; "
           "cap=True uždaro pjūvį plokščia siena.",
    "inside": "Ar taškas p yra (uždaro) tinklo viduje? Spindulio metimas: "
              "nelyginis susikirtimų skaičius – viduje.",

    "catmull_clark": "Klasikinis Catmull–Clark dalijimas: kiekviena siena virsta "
                     "keturkampiais, o forma apvalinama, steps kartų. Kraštinės "
                     "briaunos lieka glotniomis kreivėmis, sienos paveldi "
                     "spalvas; repair=True pirmiau sutvarko tinklą (besiliečiančios "
                     "dalys atskiriamos).",
    "smooth": "Apibendrintas Catmull–Clark algoritmas (Sabaliauskas, 2026): "
              "apvalina daugiakampių tinklą į jo ribinį paviršių, ant "
              "kiekvienos kontrolinės briaunos padėdamas n langelių bet kokiam "
              "n (klasikinis dalijimas duoda tik 2, 4, 8, ...), o visos naujos "
              "viršūnės guli tiksliai ant glotnaus paviršiaus. n = 1 tik "
              "perkelia kontrolines viršūnes ant paviršiaus, nelyginis n "
              "palieka mažą daugiakampį sienos viduryje. uniform=True taiko "
              "reparametrizaciją prie ypatingųjų viršūnių ir ne keturkampių "
              "sienų, kad langeliai būtų vienodo dydžio. Langeliai paveldi "
              "kontrolinės sienos spalvą.",
    "subdivide": "Kitas vardas funkcijai catmull_clark().",

    "save": "Įrašo modelį į diską; formatą lemia plėtinys: .off (kurso "
            "formatas), .obj (+ .mtl spalvų failas, kurio reikia Sketchfab), "
            ".ply arba .stl. Iškviesta be tinklo įrašo ir išvalo sceną (kaip "
            "add.py 1.2 off()). colors=50 pirmiau sumažina spalvų skaičių. "
            "Prieš rašant modelis sutvarkomas kaip clean() – suklijuojamos "
            "viršūnės, pašalinamos pasikartojančios ir palaidotos sienos, "
            "apkerpamos persidengiančios (mirgančios) sienos; clean=False "
            "įrašo lygiai taip, kaip nupiešta.",
    "off": "Įrašo OFF failą ir išvalo sceną – add.py 1.2 elgsena.",
    "obj": "Įrašo OBJ failą kartu su MTL spalvų failu; abu įkelkite į "
           "Sketchfab viename archyve.",
    "obj_size": "Kiek baitų užimtų šio modelio .obj failas (skaičiuojama iš "
                "pačių skaičių, failo nerašant). Sketchfab nemokamas planas "
                "priima iki 100 MB, kursas prašo iki 50 MB.",
    "load": "Nuskaito modelį iš .off, .obj ar .ply failo ir grąžina Mesh, kurį "
            "galima transformuoti ir įdėti į sceną.",
    "write_png": "Įrašo paveikslėlį – eilučių sąrašą, kurio kiekviena eilutė "
                 "yra spalvų sąrašas – kaip .png failą tekstūrai (žr. texture).",
    "stream": "Atidaro srautinį rašymą į .obj ar .off failą: modelis rašomas "
              "dalimis, todėl gali būti daug didesnis už kompiuterio atmintį "
              "(pilis su kiekviena plyta – šimtai megabaitų). Grąžina Stream: "
              "out.add() įrašo sceną ir ją išvalo, out.add(M) įrašo modelį, "
              "out.close() užbaigia failą (.mtl arba OFF antraštę). Kiekviena "
              "dalis prieš rašant sutvarkoma kaip clean() (clean=False – ne); "
              "precision=4 rašo koordinates keturiais skaitmenimis po kablelio, "
              "todėl failas mažesnis ir geriau glaudinasi.",
    "Stream": "Srautinio rašymo objektas, kurį grąžina stream(kelias): metodai "
              "add(M=None, clean=None) ir close(), skaitikliai faces, vertices, "
              "bytes, materials, removed (išmestos sienos) ir cut (apkirptos "
              "persidengiančios sienos). Veikia ir kaip with blokas.",
    "load_font": "Įkelia visą raidžių ar skaitmenų modelių aplanką į žodyną "
                 "{„A“: tinklas, ...}.",
    "typeset": "Išdėsto jau įkeltų raidžių tinklus (iš load_font) į eilutę ir "
               "sujungia.",
    "text_width": "Plotis, kurį užims text() eilutė, modelio vienetais.",
    "text": "Užrašo tekstą scenoje apvaliais strypais: size – didžiosios raidės "
            "aukštis, at – apatinis kairysis kampas, u ir v – rašymo ir aukštyn "
            "kryptys. Yra lietuviškos raidės ĄČĘĖĮŠŲŪŽ; \\n pradeda naują "
            "eilutę.",
    "write": "Kitas vardas funkcijai text().",
    "label": "Kitas vardas funkcijai text().",
    "glyph": "Nupiešia vieną simbolį plonais strypais u/v plokštumoje.",

    "newface": "add.py 1.2 vardas funkcijai polygon().",
    "cube": "add.py 1.2 vardas funkcijai box().",
    "rectangle3D": "add.py 1.2 vardas funkcijai cuboid().",
    "cube2": "add.py 1.2 vardas funkcijai frame() (kubo karkasas iš strypų).",
    "cylinder2": "add.py 1.2 vardas funkcijai tube() (cilindras be dangtelių).",
    "cylinder3": "add.py 1.2 vardas funkcijai cup() (cilindras, uždarytas A "
                 "gale).",
    "cone2": "add.py 1.2 vardas funkcijai cone_open() (tik nuožulni siena).",
    "ball": "Kitas vardas funkcijai sphere().",
    "block": "Kitas vardas funkcijai cuboid().",
    "cuboid3D": "Kitas vardas funkcijai cuboid().",
    "lathe": "Kitas vardas funkcijai revolve().",
    "solid_of_revolution": "Kitas vardas funkcijai revolve().",
    "weld": "Kitas vardas funkcijai clean().",
    "scale": "Kitas vardas funkcijai zoom().",
    "translate": "Kitas vardas funkcijai move().",
    "reflect": "Kitas vardas funkcijai mirror().",
    "demo": "Sukuria nedidelį modelį, išbandantį didžiąją dalį bibliotekos; "
            "python add.py įrašo demo.off ir parodo ataskaitą.",
})

EXAMPLES.update({
    "vertex": 'M = add.make(add.box, [0, 0, 0], 2)\nprint(add.vertex(M, 7))',
    "set_vertex": 'block = add.make(add.box, [0, 0, 0], 2, "gold")\ni = add.nearest_vertex(block, [1, 1, 1])\nblock = add.set_vertex(block, i, [2.5, 2.5, None])   # pull a corner, keep z\nadd.mesh(add.smooth(block, 6))',
    "set_vertices": 'block = add.make(add.box, [0, 0, 0], 2, "gold")\ntop = [i for i, p in enumerate(block.V) if p[1] > 0]\nblock = add.set_vertices(block, {i: [None, 3, None] for i in top})   # a taller box\nadd.mesh(block)',
    "move_vertex": 'block = add.make(add.box, [0, 0, 0], 2, "gold")\nblock = add.move_vertex(block, 0, [-1, -1, -1])\nadd.mesh(block)',
    "nearest_vertex": 'M = add.make(add.sphere, [0, 0, 0], 1, 10)\ni = add.nearest_vertex(M, [0, 5, 0])       # the top of the ball\nprint(i, add.vertex(M, i))',
    "edges": 'M = add.make(add.box, [0, 0, 0], 2)\nprint(len(add.edges(M)), add.edges(M)[:3])   # 12 edges',
    "edge_length": 'M = add.make(add.icosahedron, [0, 0, 0], 1)\na, b = add.edges(M)[0]\nprint(add.edge_length(M, a, b))',
    "edge_lengths": 'M = add.make(add.dodecahedron, [0, 0, 0], 1)\nL = add.edge_lengths(M)\nprint(len(L), min(L), max(L))',
    "mean_edge_length": 'M = add.make(add.icosahedron, [0, 0, 0], 1)\nprint(add.mean_edge_length(M))            # 1.0515 for r = 1',
    "adjacency": 'M = add.make(add.octahedron, [0, 0, 0], 1)\nfor i, nb in enumerate(add.adjacency(M)):\n    print(i, nb)',
    "neighbors": 'ico = add.make(add.icosahedron, [0, 0, 0], 1)\nprint(add.neighbors(ico, 0))              # five of them, in order around',
    "neighbours": 'ico = add.make(add.icosahedron, [0, 0, 0], 1)\nprint(add.neighbours(ico, 0))',
    "valence": 'for name in ["cube", "octahedron", "icosahedron"]:\n    M = add.make(add.polyhedron, name)\n    print(name, add.valence(M, 0))',
    "mean_neighbor_distance": 'ico = add.make(add.icosahedron, [0, 0, 0], 2)\nprint(add.mean_neighbor_distance(ico, 0))',
    "vertex_faces": 'M = add.make(add.box, [0, 0, 0], 2)\nprint(add.vertex_faces(M, 0))             # three faces meet at a corner',
    "vertex_normal": 'M = add.make(add.sphere, [0, 0, 0], 1, 10)\nprint(add.vertex_normal(M, 0))\nfor i in range(0, len(M.V), 40):             # a few spikes along the normals\n    n = add.vertex_normal(M, i)\n    add.cone(M.V[i], [M.V[i][a] + 0.5 * n[a] for a in range(3)], 0.05, 6, "red")',
    "face_center": 'M = add.make(add.box, [0, 0, 0], 2)\nprint(add.face_center(M, 0))',
    "face_normal": 'M = add.make(add.box, [0, 0, 0], 2)\nfor i in range(6):\n    c, n = add.face_center(M, i), add.face_normal(M, i)\n    add.arrow(c, [c[a] + n[a] for a in range(3)], 0.05, "red")',
    "face_area": 'M = add.make(add.box, [0, 0, 0], 2)\nprint(add.face_area(M, 0))                # 4.0',
    "face_centers": 'M = add.make(add.dodecahedron, [0, 0, 0], 2)\nfor c in add.face_centers(M):\n    add.sphere(c, 0.15, 5, "red")',
    "boundary_edges": 'sheet = add.make(add.grid, [0, 0, 0], [4, 4], 4, 4)\nprint(len(add.boundary_edges(sheet)))    # 16 edges around the rim\nprint(add.boundary_edges(add.make(add.box, [0, 0, 0], 1)))   # [] -- closed',
    "boundary_loops": 'sheet = add.make(add.grid, [0, 0, 0], [4, 4], 4, 4)\nrim = add.boundary_loops(sheet)[0]\nadd.polyline([sheet.V[i] for i in rim], 0.05, 8, "red", closed=True)',
    "inflate": 'ico = add.make(add.icosahedron, [0, 0, 0], 2, "white")\nball = add.color_by_sides(add.truncate(ico), {5: "black", 6: "white"})\nadd.mesh(add.inflate(ball, 0.15))',
    "spherify": 'octa = add.make(add.octahedron, [0, 0, 0], 2, "sky")\nadd.mesh(add.spherify(add.refine(octa, 3)))   # a geodesic dome, 512 triangles\ncube = add.make(add.box, [5, 0, 0], 2, "gold")\nadd.mesh(add.spherify(add.refine(cube, 2), amount=0.5))   # a cushion',
    "refine": 'cube = add.make(add.box, [0, 0, 0], 2, "gold")\nprint(add.refine(cube, 2).polygons)      # 96 quads, same shape\ntet = add.make(add.tetrahedron, [0, 0, 0], 2, "red")\nadd.mesh(add.refine(tet, 3))              # 256 triangles',
    "dual": 'cube = add.make(add.box, [0, 0, 0], 2, "gold")\nadd.mesh(add.dual(cube))                  # an octahedron\nadd.wireframe(cube, 0.03, 6, "black")',
    "truncate": 'ico = add.make(add.icosahedron, [0, 0, 0], 3, "white")\nball = add.truncate(ico, 1 / 3.0, "black")      # 20 hexagons + 12 pentagons\nadd.mesh(ball)\ncube = add.make(add.box, [7, 0, 0], 3, "gold")\nadd.mesh(add.truncate(cube, 0.5, "red"))       # a cuboctahedron',
    "color_by_sides": 'ico = add.make(add.icosahedron, [0, 0, 0], 3)\nball = add.color_by_sides(add.truncate(ico), {5: "black", 6: "white"})\nadd.mesh(add.smooth(ball, 8))',

    "union": 'a = add.make(add.box, [0, 0, 0], 2, "red")\nb = add.make(add.sphere, [1, 1, 1], 1.2, 10, "blue")\nadd.mesh(add.union(a, b))',
    "difference": 'plate = add.make(add.cuboid, [0, 0, 0], [4, 1, 4], "brown")\ndrill = add.make(add.cylinder, [0, -1, 0], [0, 1, 0], 0.6, 32, "black")\nadd.mesh(add.difference(plate, drill))',
    "intersect": 'a = add.make(add.box, [0, 0, 0], 2, "red")\nb = add.make(add.sphere, [0, 0, 0], 1.3, 10, "blue")\nadd.mesh(add.intersect(a, b))',
    "symmetric_difference": 'a = add.make(add.box, [0, 0, 0], 2, "red")\nb = add.make(add.box, [1, 1, 1], 2, "blue")\nadd.mesh(add.symmetric_difference(a, b))',
    "add_solids": 'a = add.make(add.box, [0, 0, 0], 2, "red")\nb = add.make(add.box, [1, 1, 1], 2, "blue")\nadd.mesh(add.add_solids(a, b))',
    "subtract": 'a = add.make(add.box, [0, 0, 0], 2, "red")\nb = add.make(add.box, [1, 1, 1], 2, "blue")\nadd.mesh(add.subtract(a, b))',
    "common": 'a = add.make(add.box, [0, 0, 0], 2, "red")\nb = add.make(add.box, [1, 1, 1], 2, "blue")\nadd.mesh(add.common(a, b))',
    "cut": 'ball = add.make(add.sphere, [0, 0, 0], 2, 10, "red")\nadd.mesh(add.cut(ball, [0, 0.5, 0], [0, 1, 0]))     # keeps the part below y = 0.5',
    "inside": 'ball = add.make(add.sphere, [0, 0, 0], 2, 10)\nprint(add.inside(ball, [0, 0, 0]), add.inside(ball, [5, 0, 0]))   # True False',

    "catmull_clark": 'add.box([0, 0, 0], 2, "red")\nadd.mesh(add.catmull_clark(add.layer(), 3))     # a rounded cube, 384 quads',
    "smooth": 'add.dodecahedron([0, 0, 0], 2, "gold")\nadd.mesh(add.smooth(add.layer(), 5))            # 12 * 61 cells, 5 per edge\nblock = add.make(add.box, [5, 0, 0], 2, "sky")\nblock = add.set_vertex(block, 7, [7, 3, 2])     # pull a corner out ...\nadd.mesh(add.smooth(block, 8))                  # ... and round it',
    "subdivide": 'add.box([0, 0, 0], 2, "red")\nadd.mesh(add.subdivide(add.layer(), 2))',

    "save": 'add.box([0, 0, 0], 2, "red")\nadd.sphere([3, 0, 0], 1, 10, "blue")\nadd.save("model.off")                  # and the scene is cleared\nM = add.make(add.sphere, [0, 0, 0], 1, 10, "red")\nadd.save("model.obj", M)               # .obj + .mtl, the scene stays\nadd.save("model.stl", M)',
    "off": 'add.box([0, 0, 0], 2, "red")\nadd.off("model.off")',
    "obj": 'add.box([0, 0, 0], 2, "red")\nadd.obj("model.obj")                   # model.obj + model.mtl',
    "obj_size": 'M = add.make(add.sphere, [0, 0, 0], 1, 30, "red")\nprint(add.obj_size(M) / 1e6, "MB")',
    "load": 'add.box([0, 0, 0], 2, "red")\nadd.save("part.off")\npart = add.load("part.off")\nadd.mesh(add.move(part, [3, 0, 0]))',
    "write_png": 'rows = [[add.hsv(x / 64.0, 1, 1 - y / 128.0) for x in range(64)] for y in range(64)]\nadd.write_png("rainbow.png", rows)\nadd.mesh(add.texture(add.make(add.box, [0, 0, 0], 2), "rainbow.png", "box", scale=2))',
    "stream": 'out = add.stream("big.obj")\nfor i in range(20):\n    add.bricks([0, 0, i * 2], 10, 2, [1, 0.5, 0.5], "brown", seed=i)\n    out.add()                            # written now, scene cleared\nout.add(add.make(add.tree, [12, 0, 0], 5))\nout.close()                              # writes big.mtl too\nprint(out.faces, "faces,", out.bytes, "bytes,", len(out.materials), "materials")',
    "Stream": 'with add.Stream("parts.off") as out:\n    for i in range(5):\n        add.sphere([i * 3, 0, 0], 1, 10, add.hsv(i / 5.0))\n        out.add()\nprint(out.faces, out.vertices)',

    "load_font": 'import os\nos.mkdir("letters")\nfor ch in "AB":\n    add.text(ch, [0, 0, 0], 1, color="navy")\n    add.save("letters/%s.off" % ch)\nfont = add.load_font("letters")\nprint(sorted(font))                    # ["A", "B"]',
    "typeset": 'import os\nos.mkdir("glyphs")\nfor ch in "ADD":\n    add.text(ch, [0, 0, 0], 1, color="navy")\n    add.save("glyphs/%s.off" % ch)\nfont = add.load_font("glyphs")\nadd.mesh(add.typeset("ADD", font, [0, 0, 0], 2, color="gold"))',
    "text_width": 'w = add.text_width("LABAS", 1.0)\nadd.text("LABAS", [-w / 2, 0, 0], 1.0, color="navy")   # centred by hand',
    "text": 'add.text("LABAS 2026", [0, 0, 0], 1.0, color="navy")\nadd.text("ĄČĘ\\nĖĮŠ", [0, 3, 0], 0.8, color="red", align="center")\nadd.text("FLAT", [0, -2, 0], 1.0, color="teal", u=[1, 0, 0], v=[0, 0, -1])',
    "write": 'add.write("HELLO", [0, 0, 0], 1.0, color="navy")',
    "label": 'add.label("A", [0, 0, 0], 1.0, color="navy")',
    "glyph": 'add.glyph("Ž", [0, 0, 0], [1, 0, 0], [0, 1, 0], 2, 0.1, "red")',

    "newface": "add.newface([[0, 0, 0], [2, 0, 0], [1, 2, 0]], [255, 0, 0])",
    "cube": "add.cube([0, 0, 0], 2, [255, 0, 0])",
    "rectangle3D": "add.rectangle3D([0, 0, 0], [4, 1, 2], [0, 128, 255])",
    "cube2": "add.cube2([0, 0, 0], 3, 0.2, [212, 175, 55])",
    "cylinder2": "add.cylinder2([0, 0, 0], [0, 3, 0], 0.5, 24, [212, 175, 55])",
    "cylinder3": "add.cylinder3([0, 0, 0], [0, 2, 0], 0.8, 32, [0, 128, 128])",
    "cone2": "add.cone2([0, 0, 0], [0, 3, 0], 1, 32, [255, 0, 0])",
    "ball": 'add.ball([0, 0, 0], 1, 10, "red")',
    "block": 'add.block([0, 0, 0], [4, 1, 2], "brown")',
    "cuboid3D": 'add.cuboid3D([0, 0, 0], [4, 1, 2], "brown")',
    "lathe": 'add.lathe(lambda t: [1 + 0.3 * add.sin(3 * t), t], [0, 0, 0], [0, 1, 0], 0, 4, 40, 32, "teal")',
    "solid_of_revolution": 'add.solid_of_revolution(lambda t: [1 + 0.3 * add.sin(3 * t), t], [0, 0, 0], [0, 1, 0], 0, 4, 40, 32, "teal")',
    "weld": 'add.box([0, 0, 0], 2, "red")\nadd.box([2, 0, 0], 2, "red")\nadd.mesh(add.weld(add.layer()))',
    "scale": 'ball = add.make(add.sphere, [0, 0, 0], 1, 10, "red")\nadd.mesh(add.scale(ball, 2))',
    "translate": 'ball = add.make(add.sphere, [0, 0, 0], 1, 10, "red")\nadd.mesh(add.translate(ball, [3, 0, 0]))',
    "reflect": 'wing = add.make(add.cuboid, [2, 0, 0], [3, 0.2, 1], "gold")\nadd.mesh(add.reflect(wing, [0, 0, 0], [1, 0, 0]))',
    "demo": 'add.demo("demo.off")',
})

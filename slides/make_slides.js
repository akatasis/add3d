/*
 * Builds the add.py lecture deck in two languages from one script:
 *
 *     node slides/make_slides.js          ->  add_py_2026_en.pptx, add_py_2026_lt.pptx
 *     node slides/make_slides.js lt       ->  Lithuanian only
 *
 * Every string is written as T("English", "Lietuviškai"); the English text
 * is the primary version, the Lithuanian one follows it.  4:3, to match
 * the rest of the lecture.
 */
const pptxgen = require("pptxgenjs");
const path = require("path");
const fs = require("fs");

const ROOT = path.join(__dirname, "..");
const IMG = path.join(ROOT, "docs", "images");
const VERSION = "2.0";

// ---------------------------------------------------------------- palette
const BROWN = "8A4B1E";      // the colour of the documentation's accent
const DARK = "241C15";
const INK = "24282E";
const MUTED = "6B7280";
const SAND = "F6EFE8";
const TEAL = "1E6B5A";
const LINE = "E3E1DD";
const WHITE = "FFFFFF";

const TITLE_FONT = "Cambria";
const BODY_FONT = "Calibri";
const MONO = "Consolas";

const W = 10.0, H = 7.5;               // 4:3, like the rest of the lecture
const M = 0.62;                        // side margin

function img(name) {
  const p = path.join(IMG, name);
  if (!fs.existsSync(p)) throw new Error("missing image: " + p);
  return p;
}

function build(lang) {
  const T = (en, lt) => (lang === "lt" ? lt : en);
  const pres = new pptxgen();
  pres.layout = "LAYOUT_4x3";
  pres.author = "Martynas Sabaliauskas";
  pres.company = T("Vilnius University, MIF", "Vilniaus universitetas, MIF");
  pres.title = "add.py " + VERSION;
  const OUT = path.join(__dirname, "add_py_2026_" + lang + ".pptx");

  let slideNumber = 0;

  /* A content slide: title at the top, everything else placed by the caller. */
  function sheet(title, kicker) {
    const s = pres.addSlide();
    slideNumber += 1;
    s.background = { color: WHITE };
    if (kicker) {
      s.addText(kicker.toUpperCase(), {
        x: M, y: 0.36, w: W - 2 * M, h: 0.26, isTextBox: true, margin: 0,
        fontFace: BODY_FONT, fontSize: 11, bold: true, charSpacing: 1.6,
        color: BROWN,
      });
    }
    s.addText(title, {
      x: M, y: kicker ? 0.60 : 0.46, w: W - 2 * M, h: 0.72, isTextBox: true,
      margin: 0, fontFace: TITLE_FONT, fontSize: 30, bold: true, color: INK,
      valign: "top",
    });
    s.addText(String(slideNumber), {
      x: W - M - 0.5, y: H - 0.52, w: 0.5, h: 0.26, isTextBox: true, margin: 0,
      fontFace: BODY_FONT, fontSize: 10, color: MUTED, align: "right",
    });
    return s;
  }

  function bullets(s, items, opt) {
    opt = opt || {};
    const text = items.map((t, i) => ({
      text: typeof t === "string" ? t : t.text,
      options: Object.assign(
        { bullet: { indent: 14 }, breakLine: i < items.length - 1 },
        typeof t === "string" ? {} : (t.options || {})
      ),
    }));
    s.addText(text, Object.assign({
      x: M, y: 1.55, w: W - 2 * M, h: 4.6, isTextBox: true, margin: 0,
      fontFace: BODY_FONT, fontSize: opt.fontSize || 16, color: INK,
      lineSpacing: (opt.fontSize || 16) * 1.55, valign: "top",
      paraSpaceAfter: 6,
    }, opt));
  }

  function code(s, lines, opt) {
    opt = opt || {};
    const box = Object.assign({ x: M, y: 1.6, w: 5.1, h: 2.6 }, opt);
    s.addShape(pres.ShapeType.roundRect, {
      x: box.x, y: box.y, w: box.w, h: box.h, rectRadius: 0.06,
      fill: { color: "F7F7F8" }, line: { color: LINE, width: 0.75 },
    });
    s.addText(lines.join("\n"), {
      x: box.x + 0.16, y: box.y + 0.14, w: box.w - 0.32, h: box.h - 0.28,
      isTextBox: true, margin: 0, fontFace: MONO,
      fontSize: opt.fontSize || 12, color: "2C3138", lineSpacing: 16,
      valign: "top",
    });
  }

  function picture(s, name, opt) {
    opt = opt || {};
    const box = Object.assign({ x: 5.95, y: 1.6, w: 3.43, h: 2.42 }, opt);
    s.addShape(pres.ShapeType.roundRect, {
      x: box.x, y: box.y, w: box.w, h: box.h, rectRadius: 0.06,
      fill: { color: "FAFAFA" }, line: { color: LINE, width: 0.75 },
    });
    s.addImage({
      path: img(name), x: box.x + 0.06, y: box.y + 0.06,
      w: box.w - 0.12, h: box.h - 0.12,
      sizing: { type: "contain", w: box.w - 0.12, h: box.h - 0.12 },
    });
    if (opt.caption) {
      s.addText(opt.caption, {
        x: box.x, y: box.y + box.h + 0.07, w: box.w, h: 0.5, isTextBox: true,
        margin: 0, fontFace: BODY_FONT, fontSize: 11, color: MUTED,
        align: "center", valign: "top",
      });
    }
  }

  /* A row of small cards.  `items` is [[heading, body], ...]. */
  function cards(s, items, opt) {
    opt = opt || {};
    const y = opt.y || 1.65;
    const h = opt.h || 1.42;
    const perRow = opt.perRow || 2;
    const gap = 0.26;
    const x0 = opt.x || M;
    const totalW = opt.w || (W - x0 - M);
    const w = (totalW - gap * (perRow - 1)) / perRow;
    items.forEach((it, i) => {
      const col = i % perRow, row = Math.floor(i / perRow);
      const x = x0 + col * (w + gap);
      const yy = y + row * (h + gap);
      s.addShape(pres.ShapeType.roundRect, {
        x: x, y: yy, w: w, h: h, rectRadius: 0.05,
        fill: { color: opt.tint || SAND },
      });
      s.addText(it[0], {
        x: x + 0.22, y: yy + 0.16, w: w - 0.44, h: 0.32, isTextBox: true,
        margin: 0, fontFace: BODY_FONT, fontSize: 15, bold: true, color: BROWN,
      });
      s.addText(it[1], {
        x: x + 0.22, y: yy + 0.52, w: w - 0.44, h: h - 0.68, isTextBox: true,
        margin: 0, fontFace: BODY_FONT, fontSize: 12.5, color: INK,
        lineSpacing: 16, valign: "top",
      });
    });
  }

  function note(s, text) {
    s.addText(text, {
      x: M, y: H - 1.22, w: W - 2 * M - 0.6, h: 0.62, isTextBox: true,
      margin: 0, fontFace: BODY_FONT, fontSize: 12.5, italic: true,
      color: MUTED, valign: "top",
    });
  }

  function mono(text, extra) {
    return { text: text, options: Object.assign({ fontFace: MONO, fontSize: 12,
      breakLine: true }, extra || {}) };
  }

  // =========================================================== 1. title
  {
    const s = pres.addSlide();
    s.background = { color: DARK };
    s.addText("add.py " + VERSION, {
      x: M, y: 1.25, w: W - 2 * M, h: 1.0, isTextBox: true, margin: 0,
      fontFace: TITLE_FONT, fontSize: 54, bold: true, color: WHITE,
    });
    s.addText(T("Build 3D models with nothing but Python code",
                "Trimačiai modeliai, sukurti vien tik programiniu kodu"), {
      x: M, y: 2.25, w: W - 2 * M, h: 0.5, isTextBox: true, margin: 0,
      fontFace: BODY_FONT, fontSize: 19, color: "E9C9AE",
    });
    s.addShape(pres.ShapeType.roundRect, {
      x: M, y: 3.15, w: W - 2 * M, h: 3.2, rectRadius: 0.04,
      fill: { color: "F4F3F1" },
    });
    s.addImage({
      path: img("lighthouse.png"), x: M + 0.08, y: 3.23, w: W - 2 * M - 0.16,
      h: 3.04, sizing: { type: "contain", w: W - 2 * M - 0.16, h: 3.04 },
    });
    s.addText(T("Algorithms and Data Structures  ·  Algorithm Design and Analysis  ·  creative assignment",
                "Algoritmai ir duomenų struktūros  ·  Algoritmų kūrimas ir analizė  ·  kūrybinė užduotis"), {
      x: M, y: 6.6, w: W - 2 * M, h: 0.4, isTextBox: true, margin: 0,
      fontFace: BODY_FONT, fontSize: 13, color: "C9BFB6",
    });
    s.addNotes(T("The add.py part of the first lecture, updated for version 2.0 -- for students and for anyone "
      + "who wants to build 3D models from code. The module is refreshed every year; 2.0 is the largest change since 1.2.",
      "Šiose skaidrėse – atnaujinta add.py modulio dalis (2.0 versija) – studentams ir visiems, "
      + "kas nori kurti 3D modelius programuodami. Modulis kasmet atnaujinamas; 2.0 versija yra didžiausias pokytis nuo 1.2."));
  }

  // =========================================================== 2. what's new
  {
    const s = sheet(T("What is new in " + VERSION, "Kas naujo " + VERSION + " versijoje"), "add.py");
    cards(s, [
      [T("Boolean operations", "Loginės operacijos"),
        T("union, intersect, difference -- written from scratch, no libraries.",
          "union, intersect, difference – sąjunga, sankirta ir skirtumas. "
          + "Parašyta nuo nulio, be jokių bibliotekų.")],
      [T("Regular polyhedra and a geodesic sphere", "Taisyklingieji briaunainiai ir geodezinė sfera"),
        T("tetrahedron ... icosahedron, centred; sphere() is now a dome of triangles.",
          "tetrahedron ... icosahedron, sucentruoti; sphere() dabar – kupolas iš trikampių.")],
      [T("Smooth surfaces", "Glotnūs paviršiai"),
        T("catmull_clark, and smooth(): the generalised Catmull-Clark algorithm, any number of cells per edge.",
          "catmull_clark ir smooth(): apibendrintas Catmull–Clark algoritmas, bet koks langelių skaičius ant briaunos.")],
      [T("Vertex tools", "Viršūnių įrankiai"),
        T("set_vertex, neighbors, valence, dual, truncate -- a football from the vertices of an icosahedron.",
          "set_vertex, neighbors, valence, dual, truncate – futbolo kamuolys iš ikosaedro viršūnių.")],
      [T("Named surfaces, colour functions, parts", "Vardiniai paviršiai, spalvų funkcijos, detalės"),
        T("25 surfaces by name; color=lambda u, v: ...; beam, wheel, gear, roof, tree, text ...",
          "25 paviršių pagal vardą; color=lambda u, v: ...; beam, wheel, gear, roof, tree, text ...")],
      [T("Sketchfab-ready export", "Išsaugojimas Sketchfab"),
        T("check() watches the 50 MB / 50 colour limits; glass (transparent) and image textures go into the .mtl.",
          "check() prižiūri 50 MB / 50 spalvų ribas; stiklas (transparent) ir tekstūros įrašomi į .mtl.")],
    ], { h: 1.28 });
    note(s, T("Everything written for 1.2 keeps working without a single change; only import add is needed.",
              "Viskas, kas parašyta senajai 1.2 versijai, veikia be jokių pataisymų; užtenka import add."));
    s.addNotes(T("The key message: nothing has to be rewritten. For students and for anyone interested.",
                 "Svarbiausia žinia: nieko perrašinėti nereikia. Studentams ir visiems besidomintiems."));
  }

  // =========================================================== 3. assignment
  {
    const s = sheet(T("The creative assignment", "Kūrybinė užduotis"),
                    T("reminder", "priminimas"));
    bullets(s, [
      { text: T("Make a 3D model using nothing but program source code.",
                "Sukurti 3D modelį naudojant tik pirminį programos tekstą."),
        options: { bold: true } },
      T("File format: OFF or OBJ.", "Modelio failo formatas – OFF arba OBJ."),
      T("At least 10 000 polygons.", "Bent 10 000 daugiakampių."),
      T("At least 3 different colours.", "Bent 3 skirtingos spalvos."),
      T("The algorithm must contain a for or while loop.",
        "Algoritme privalo būti for arba while ciklas."),
      T("At least one parameter that changes the shape.",
        "Bent 1 parametras, nuo kurio priklauso modelio forma."),
      T("No 3D modelling programs.", "Negalima naudoti 3D modeliavimui skirtų programų."),
      T("Individually or in pairs.", "Modelį galima kurti individualiai arba komandoje dviese."),
    ], { w: 5.3 });
    picture(s, "city.png", {
      x: 6.05, y: 1.62, w: 3.33, h: 2.35,
      caption: T("One number (SEED) decides the whole city",
                 "Vienas skaičius (SEED) nulemia visą miestą"),
    });
    s.addText([
      { text: "add.check()", options: { fontFace: MONO, bold: true,
        color: BROWN, breakLine: true } },
      { text: T("tells you which requirements are already met.",
                "pasako, kurie reikalavimai jau įvykdyti."),
        options: { fontFace: BODY_FONT } },
    ], {
      x: 6.05, y: 4.65, w: 3.33, h: 0.8, isTextBox: true, margin: 0,
      fontSize: 13, color: INK, valign: "top",
    });
  }

  // =========================================================== 4. tools
  {
    const s = sheet(T("Recommended tools", "Rekomenduojami įrankiai"),
                    T("environment", "aplinka"));
    cards(s, [
      ["Python 3", T("Nothing else to install: add.py uses only math and random.",
                     "Daugiau nieko diegti nereikia. add.py naudoja tik math ir random.")],
      ["add.py", T("One file next to your script. Downloaded from GitHub (project add3d).",
                   "Vienas failas šalia jūsų programos. Parsisiunčiamas iš GitHub (projektas add3d).")],
      ["tools/preview.py", T("Look at a model without any other program: writes a PNG.",
                             "Modelio peržiūra be jokios kitos programos: sukuria PNG paveikslėlį.")],
      ["GeoGebra", T("Handy for checking curve and surface formulas before coding them.",
                     "Patogu pasitikrinti kreivių ir paviršių formules prieš rašant kodą.")],
      ["MeshLab", T("Viewing and converting OFF. No longer required: add.py writes OBJ itself.",
                    "OFF peržiūra ir konvertavimas. Nebebūtinas – OBJ išsaugo pats add.py.")],
      ["Sketchfab.com", T(".obj + .mtl in one archive -- and anyone can turn the model in a browser.",
                          ".obj + .mtl viename archyve – ir modelį galima pasukioti naršyklėje.")],
    ], { h: 1.3 });
    s.addNotes(T("MeshLab used to be required for OBJ. Not any more.",
                 "Anksčiau MeshLab buvo būtinas norint gauti OBJ. Dabar ne."));
  }

  // =========================================================== 5. OFF format
  {
    const s = sheet(T("A model is two lists", "Modelis – tai du sąrašai"),
                    T("basics", "pagrindai"));
    code(s, ["OFF", "8 6 0", "-1 -1 -1", "-1 -1  1", "  ...",
             "4 0 4 5 1 255 0 0", "4 0 1 3 2 255 0 0", "  ..."],
         { x: M, y: 1.62, w: 4.1, h: 2.5, fontSize: 13 });
    s.addText([
      { text: "OFF", options: { fontFace: MONO, bold: true } },
      { text: T("  -- the format's name", "  – formato vardas"), options: { breakLine: true } },
      { text: "8 6 0", options: { fontFace: MONO, bold: true } },
      { text: T("  -- number of vertices, faces and edges",
                "  – viršūnių, sienų ir briaunų skaičius"), options: { breakLine: true } },
      { text: T("then the vertex coordinates", "toliau – viršūnių koordinatės"),
        options: { breakLine: true } },
      { text: "4 0 4 5 1", options: { fontFace: MONO, bold: true } },
      { text: T("  -- a quadrilateral joining vertices 0, 4, 5 and 1",
                "  – keturkampis, jungiantis viršūnes 0, 4, 5 ir 1"), options: { breakLine: true } },
      { text: "255 0 0", options: { fontFace: MONO, bold: true } },
      { text: T("  -- the face's colour", "  – sienos spalva") },
    ], {
      x: 5.0, y: 1.72, w: 4.4, h: 2.4, isTextBox: true, margin: 0,
      fontFace: BODY_FONT, fontSize: 13.5, color: INK, lineSpacing: 21, valign: "top",
    });
    s.addText(T("Every drawing function in the library does the same thing: "
                + "it works out some points and adds some faces.",
                "Visos šios bibliotekos braižymo funkcijos daro tą patį: "
                + "apskaičiuoja taškus ir prideda sienas."), {
      x: M, y: 4.45, w: W - 2 * M, h: 0.6, isTextBox: true, margin: 0,
      fontFace: BODY_FONT, fontSize: 16, color: INK,
    });
    code(s, ["import add", "", "add.box([0, 0, 0], 2, \"red\")",
             T("add.save(\"cube.off\")", "add.save(\"kubas.off\")")],
         { x: M, y: 5.15, w: 4.1, h: 1.35, fontSize: 13 });
    s.addText(T("The same cube -- four lines.", "Tas pats kubas – keturios eilutės."), {
      x: 5.0, y: 5.6, w: 4.4, h: 0.5, isTextBox: true, margin: 0,
      fontFace: BODY_FONT, fontSize: 14, italic: true, color: MUTED,
    });
  }

  // =========================================================== 6. winding
  {
    const s = sheet(T("Inside and outside", "Vidinė ir išorinė siena"), T("basics", "pagrindai"));
    bullets(s, [
      T("Seen from outside the model, the corners of a face run counter-clockwise.",
        "Žvelgiant į modelį iš išorės, viršūnių indeksus reikia išdėstyti prieš laikrodžio rodyklę."),
      T("Seen from inside -- clockwise.", "Žvelgiant iš vidaus – pagal laikrodžio rodyklę."),
      T("A face the wrong way round is drawn black or not at all.",
        "Apversta siena atvaizduojama juoda arba visai nerodoma."),
      T("The library orients its own shapes; you only think about it when writing add.polygon(...) by hand.",
        "Bibliotekos figūros orientuojamos pačios – galvoti apie tai reikia tik rašant add.polygon(...) ranka."),
      { text: T("add.fix_normals(M) fixes a whole model; add.check() says whether the surface is closed.",
                "add.fix_normals(M) sutvarko visą modelį; add.check() pasako, ar paviršius uždaras."),
        options: { bold: true } },
    ], { w: 5.2, fontSize: 15.5 });
    picture(s, "two_sided.png", {
      x: 5.95, y: 1.62, w: 3.43, h: 2.42,
      caption: T("The same saddle: sheet, two-sided, solid",
                 "Tas pats balnas: lakštas, dvipusis ir tūrinis"),
    });
  }

  // =========================================================== 7. scene
  {
    const s = sheet(T("The scene, layers and meshes", "Scena, sluoksniai ir modeliai"),
                    T("the main idea", "pagrindinė idėja"));
    code(s, [
      "add.box([0, 0, 0], 1, \"red\")",
      T("brick = add.layer()     # the scene is empty again",
        "plyta = add.layer()     # scena vėl tuščia"),
      "",
      "for i in range(10):",
      T("    add.mesh(add.move(brick, [i * 1.2, 0, 0]))",
        "    add.mesh(add.move(plyta, [i * 1.2, 0, 0]))"),
      "",
      T("add.save(\"wall.off\")", "add.save(\"siena.off\")"),
    ], { x: M, y: 1.62, w: 5.25, h: 2.3, fontSize: 12.5 });
    cards(s, [
      ["layer()", T("Takes the scene out as a mesh and leaves the scene empty.",
                    "Paima sceną kaip modelį ir palieka sceną tuščią.")],
      ["mesh(M)", T("Puts a mesh back into the scene.", "Grąžina modelį atgal į sceną.")],
      ["merge([...])", T("Joins several meshes into one.", "Sujungia kelis modelius į vieną.")],
      ["push() / pop()", T("Inside a function that builds a part: put the scene aside, then bring it back.",
                           "Funkcijoje, kuriančioje atskirą detalę: padeda sceną į šalį ir po to grąžina.")],
    ], { y: 4.15, h: 1.24, perRow: 2 });
    s.addText(T("Build once -- place many times.", "Sukurk vieną kartą – padėk daug kartų."), {
      x: 6.1, y: 2.05, w: 3.3, h: 1.0, isTextBox: true, margin: 0,
      fontFace: TITLE_FONT, fontSize: 21, bold: true, color: BROWN, valign: "top",
    });
    s.addText(T("Transformations never change the mesh you give them -- they return a new one.",
                "Transformacijos niekada nekeičia joms perduoto modelio – jos grąžina naują."), {
      x: 6.1, y: 3.0, w: 3.3, h: 0.9, isTextBox: true, margin: 0,
      fontFace: BODY_FONT, fontSize: 13, color: MUTED, valign: "top",
    });
  }

  // =========================================================== 8. first model
  {
    const s = sheet(T("The first model", "Pirmasis modelis"), T("start", "pradžia"));
    code(s, [
      "import add", "",
      "add.box([0, 0, 0], 2, \"red\")",
      "add.sphere([3, 0, 0], 1, 20, \"blue\")",
      "add.cylinder([0, 2, 0], [3, 2, 0],",
      "             0.3, 24, \"gold\")", "",
      "add.check()",
      T("add.save(\"first.off\")", "add.save(\"pirmas.off\")"),
    ], { x: M, y: 1.62, w: 4.5, h: 2.85, fontSize: 13 });
    picture(s, "first_model.png", { x: 5.4, y: 1.62, w: 3.98, h: 2.85 });
    code(s, [
      "  vertices            2460",
      "!! polygons            2478  (need 10000)",
      "OK colours             3     (need 3)",
      "OK closed surface      yes",
    ], { x: M, y: 4.85, w: 8.76, h: 1.35, fontSize: 12 });
    s.addText(T("The check() report: still short of polygons.",
                "check() ataskaita: dar trūksta daugiakampių."), {
      x: M, y: 6.3, w: 8.76, h: 0.4, isTextBox: true, margin: 0,
      fontFace: BODY_FONT, fontSize: 13, italic: true, color: MUTED,
    });
  }

  // =========================================================== 9. only import add
  {
    const s = sheet(T("Only import add", "Užtenka import add"), T("new", "nauja"));
    code(s, [
      "import add", "",
      "for i in range(12):",
      "    a = 2 * add.pi * i / 12",
      "    p = [3 * add.cos(a), 0, 3 * add.sin(a)]",
      "    add.sphere(p, 0.4, 8, add.hsv(i / 12))",
      "",
      "add.seed(7)",
      "add.box([add.uniform(-3, 3), 0, 0], 1, \"red\")",
    ], { x: M, y: 1.6, w: 5.3, h: 2.9, fontSize: 11 });
    cards(s, [
      ["add.sin, add.pi, add.sqrt ...",
        T("Everything from math, straight from add.", "Viskas iš math – tiesiai iš add.")],
      ["add.randint, add.seed, add.Random",
        T("Everything from random, too.", "Ir viskas iš random.")],
    ], { x: 6.05, y: 1.6, h: 1.35, perRow: 1 });
    s.addText(T("A model file has exactly one import. (Plain import math still works.)",
                "Modelio faile – lygiai vienas importas. (Įprastas import math irgi veikia.)"), {
      x: M, y: 4.75, w: W - 2 * M, h: 0.6, isTextBox: true, margin: 0,
      fontFace: TITLE_FONT, fontSize: 17, color: BROWN,
    });
    note(s, T("The examples in examples/ are written this way: import add and nothing else.",
              "Visi examples/ pavyzdžiai parašyti taip: import add ir daugiau nieko."));
  }

  // =========================================================== 10. primitives
  {
    const s = sheet(T("Ready-made shapes", "Paruoštos figūros"), T("functions", "funkcijos"));
    picture(s, "primitives.png", { x: M, y: 1.55, w: 5.15, h: 3.6 });
    s.addText([
      { text: T("Solids\n", "Kūnai\n"), options: { bold: true, color: BROWN, breakLine: true } },
      mono("box, cuboid, rounded_box, frame, pyramid, prism, polyhedron, voxels\n", { fontSize: 10.5 }),
      { text: T("\nRound\n", "\nApvalūs\n"), options: { bold: true, color: BROWN, breakLine: true } },
      mono("sphere, hemisphere, uvsphere, ellipsoid, torus, capsule, cylinder, tube, "
           + "cup, cone, cone_open, frustum, pipe\n", { fontSize: 10.5 }),
      { text: T("\nFlat\n", "\nPlokšti\n"), options: { bold: true, color: BROWN, breakLine: true } },
      mono("polygon, triangle, quad, disc, ring, grid\n", { fontSize: 10.5 }),
      { text: T("\nParts\n", "\nDetalės\n"), options: { bold: true, color: BROWN, breakLine: true } },
      mono("beam, arch, stairs, gear, wheel, roof, column, bricks, tree, pixels, heightmap, text",
           { fontSize: 10.5, breakLine: false }),
    ], {
      x: 6.0, y: 1.5, w: 3.4, h: 4.9, isTextBox: true, margin: 0,
      fontFace: BODY_FONT, fontSize: 12, color: INK, lineSpacing: 13.5, valign: "top",
    });
    note(s, T("examples/02_primitives.py -- every shape in one program.",
              "examples/02_primitives.py – visos figūros vienoje programoje."));
  }

  // =========================================================== 11. parametric
  {
    const s = sheet(T("parametric() -- the central function", "parametric() – pagrindinė funkcija"),
                    T("surfaces", "paviršiai"));
    code(s, [
      T("def torus(u, v):", "def toras(u, v):"),
      "    return [(5 + add.cos(u)) * add.cos(v),",
      "            add.sin(u),",
      "            (5 + add.cos(u)) * add.sin(v)]", "",
      T("add.parametric(torus, 0, 2*add.pi, 40,", "add.parametric(toras, 0, 2*add.pi, 40,"),
      "                      0, 2*add.pi, 80,",
      "               \"gold\", wrap_u=True, wrap_v=True)",
    ], { x: M, y: 1.6, w: 5.3, h: 2.4, fontSize: 12 });
    picture(s, "surfaces_classic.png", { x: 6.05, y: 1.6, w: 3.33, h: 2.4 });
    cards(s, [
      ["wrap_u, wrap_v", T("Close the surface without a seam or repeated vertices.",
                           "Uždaro paviršių be siūlės ir be pasikartojančių viršūnių.")],
      ["thickness=", T("Give the sheet a real thickness -- a closed solid.",
                       "Suteikia lakštui tikrą storį – gaunamas uždaras kūnas.")],
      ["color=lambda u, v: ...", T("Paint every cell by its own parameters.",
                                   "Nuspalvina kiekvieną langelį pagal jo parametrus.")],
    ], { y: 4.25, h: 1.35, perRow: 3 });
  }

  // =========================================================== 12. colour functions
  {
    const s = sheet(T("Colour functions", "Spalvų funkcijos"), T("new", "nauja"));
    code(s, [
      "add.parametric(f, 0, 1, 40, 0, 1, 40,",
      "    color=lambda u, v: add.hsv(u))",
      "",
      T("add.revolve(vase, A, B, 0, 4, 60, 40,", "add.revolve(vaza, A, B, 0, 4, 60, 40,"),
      "    color=lambda t, a: \"red\" if int(t) % 2 else \"white\")",
      "",
      T("add.curve(spiral, 0, 20, 300, 12, 0.2,", "add.curve(spirale, 0, 20, 300, 12, 0.2,"),
      "    color=lambda t, a: add.hsv(t / 20))",
    ], { x: M, y: 1.6, w: 5.3, h: 2.75, fontSize: 10 });
    picture(s, "solar_system.png", { x: 6.05, y: 1.6, w: 3.33, h: 2.4,
      caption: T("Planets: lathes painted by (latitude, longitude)",
                 "Planetos: sukiniai, nuspalvinti pagal (platumą, ilgumą)") });
    s.addText(T("The function is called once per cell with the surface's own two parameters: "
                + "(u, v) for parametric, (t, angle) for revolve and curve, (x, z) for grid. "
                + "Stripes, chequerboards, maps and gradients cost one lambda.",
                "Funkcija kviečiama kiekvienam langeliui su dviem paviršiaus parametrais: "
                + "(u, v) – parametric, (t, kampas) – revolve ir curve, (x, z) – grid. "
                + "Juostos, šachmatų lentos, žemėlapiai ir perėjimai kainuoja vieną lambda."), {
      x: M, y: 4.7, w: W - 2 * M, h: 1.2, isTextBox: true, margin: 0,
      fontFace: BODY_FONT, fontSize: 14, color: INK, valign: "top",
    });
    note(s, T("For a mesh you already have: color_by(M, lambda p: ...) paints by position.",
              "Jau turimam modeliui: color_by(M, lambda p: ...) spalvina pagal padėtį."));
  }

  // =========================================================== 13-15. surfaces
  {
    const s = sheet(T("One equation, twelve shapes", "Viena lygtis, dvylika formų"),
                    T("parametric surfaces", "parametriniai paviršiai"));
    picture(s, "supershapes.png", { x: M, y: 1.55, w: 5.3, h: 3.75 });
    s.addText([
      { text: T("Gielis's superformula (2003)\n", "Gielio superformulė (2003)\n"),
        options: { bold: true, color: BROWN, breakLine: true } },
      { text: "r(t) = ( |cos(m·t/4)/a|^n₂ + |sin(m·t/4)/b|^n₃ ) ^ (−1/n₁)\n\n",
        options: { fontFace: MONO, fontSize: 11, breakLine: true } },
      { text: T("Six numbers -- and you get a starfish, a flower, a crystal or a plain ball.\n\n",
                "Šeši skaičiai – ir gaunama jūrų žvaigždė, gėlė, kristalas arba paprasčiausias rutulys.\n\n"),
        options: { breakLine: true } },
      { text: T("Exactly what the assignment asks for: one parameter that changes the shape.",
                "Būtent to ir prašo užduotis: vienas parametras, keičiantis formą."),
        options: { italic: true, color: MUTED } },
    ], {
      x: 6.15, y: 1.65, w: 3.25, h: 3.6, isTextBox: true, margin: 0,
      fontFace: BODY_FONT, fontSize: 13, color: INK, lineSpacing: 17, valign: "top",
    });
    note(s, "examples/08_surfaces_superformula.py");
  }
  {
    const s = sheet(T("Surfaces that look like things", "Paviršiai, kurie panašūs į daiktus"),
                    T("examples", "pavyzdžiai"));
    picture(s, "surfaces_nature.png", { x: M, y: 1.55, w: 8.76, h: 4.1 });
    note(s, T("Shell, snail, Dini's surface, apple, lemon, heart, horn, trumpet, wavy column, "
              + "breather, ripples, drop. examples/09_surfaces_nature.py",
              "Kriauklė, sraigė, Dini paviršius, obuolys, citrina, širdis, ragas, trimitas, "
              + "banguota kolona, „breather“, raibuliai, lašas. examples/09_surfaces_nature.py"));
  }
  {
    const s = sheet(T("Graphs and exotic surfaces", "Grafikai ir egzotiški paviršiai"),
                    T("examples", "pavyzdžiai"));
    picture(s, "height_fields.png", { x: M, y: 1.6, w: 4.3, h: 3.0,
      caption: "y = f(x, z)  ·  10_height_fields.py" });
    picture(s, "surfaces_exotic.png", { x: 5.1, y: 1.6, w: 4.28, h: 3.0,
      caption: T("Möbius, Klein, Boy, Roman surface  ·  07_surfaces_exotic.py",
                 "Miobijus, Kleinas, Boy, Romos paviršius  ·  07_surfaces_exotic.py") });
    s.addText(T("One-sided surfaces have no \"outside\". Give them a thickness and they "
                + "become ordinary two-sided solids.",
                "Vienpusiai paviršiai neturi „išorės“. Duokite jiems storį – "
                + "ir jie tampa įprastais dvipusiais kūnais."), {
      x: M, y: 5.5, w: W - 2 * M, h: 0.7, isTextBox: true, margin: 0,
      fontFace: BODY_FONT, fontSize: 15, color: INK,
    });
  }

  // =========================================================== 16. two-sided
  {
    const s = sheet(T("When a surface is black from one side", "Kai paviršius iš vienos pusės juodas"),
                    T("surfaces", "paviršiai"));
    picture(s, "two_sided.png", { x: M, y: 1.55, w: 8.76, h: 3.2 });
    cards(s, [
      [T("A plain sheet", "Paprastas lakštas"), T("One good side, one \"dead\" side.",
                                                    "Viena gera pusė, viena „negyva“.")],
      ["double_sided=True", T("Every face and its reversed copy. Cheap; still no thickness.",
                              "Kiekviena siena ir jos apversta kopija. Pigu, storio vis dar nėra.")],
      ["thickness=0.1", T("A real solid with a wall: closed, printable, right from every angle.",
                          "Tikras kūnas su sienele: uždaras, spausdinamas, teisingas iš visų pusių.")],
    ], { y: 5.0, h: 1.35, perRow: 3 });
  }

  // =========================================================== 17. revolve
  {
    const s = sheet(T("revolve() -- the lathe", "revolve() – sukinys"), T("surfaces", "paviršiai"));
    code(s, [
      T("def vase(t):", "def vaza(t):"),
      "    return [1 + 0.4*add.sin(3*t), t]", "",
      T("add.revolve(vase, [0, 0, 0], [0, 1, 0],", "add.revolve(vaza, [0, 0, 0], [0, 1, 0],"),
      "            0, 4, 60, 40, \"teal\")",
    ], { x: M, y: 1.6, w: 4.4, h: 1.85, fontSize: 12.5 });
    s.addText([
      { text: T("profile(t)", "profilis(t)"), options: { fontFace: MONO, bold: true } },
      { text: T(" returns [radius, height]", " grąžina [spindulys, aukštis]"), options: { breakLine: true } },
      { text: T("\ncaps=True closes the ends -- a solid ready for booleans",
                "\ncaps=True uždaro galus – gaunamas kūnas, tinkamas loginėms operacijoms"),
        options: { breakLine: true } },
      { text: T("\nangle= less than a full turn cuts out a wedge",
                "\nangle= mažesnis už pilną apsisukimą išpjauna pleištą"), options: {} },
    ], {
      x: M, y: 3.6, w: 4.4, h: 1.5, isTextBox: true, margin: 0,
      fontFace: BODY_FONT, fontSize: 13, color: INK, lineSpacing: 17, valign: "top",
    });
    picture(s, "lathe.png", { x: 5.25, y: 1.6, w: 4.13, h: 3.5 });
    note(s, T("The old spin3D(A, B, S, ...) still works -- the same lathe without lids. "
              + "examples/14_lathe_gallery.py",
              "Senasis spin3D(A, B, S, ...) tebeveikia – tai tas pats sukinys be dangtelių. "
              + "examples/14_lathe_gallery.py"));
  }

  // =========================================================== 18. sweeps
  {
    const s = sheet(T("A cross-section copied, turned and stretched",
                      "Kopijuojamas, sukamas, tempiamas paviršius"), T("surfaces", "paviršiai"));
    code(s, [
      T("add.extrude(star, [0, 3.4, 0], \"gold\",", "add.extrude(zvaigzde, [0, 3.4, 0], \"gold\","),
      "            steps=90, twist=1.6*add.pi,",
      "            scale=lambda t: 1 - 0.45*t)",
    ], { x: M, y: 1.58, w: 5.3, h: 1.1, fontSize: 12 });
    picture(s, "cross_sections.png", { x: 6.05, y: 1.58, w: 3.33, h: 2.4 });
    s.addText(T("twist and scale may be functions of the position along the path -- the shape "
                + "changes as it goes. profile_star, profile_gear, profile_rect ... give the "
                + "outlines. examples/13_sweep_and_twist.py, 33_cross_sections.py",
                "twist ir scale gali būti ir funkcijos nuo padėties kelyje – forma keičiasi "
                + "eidama. profile_star, profile_gear, profile_rect ... duoda kontūrus. "
                + "examples/13_sweep_and_twist.py, 33_cross_sections.py"), {
      x: M, y: 2.85, w: 5.3, h: 1.1, isTextBox: true, margin: 0,
      fontFace: BODY_FONT, fontSize: 12.5, color: MUTED, valign: "top",
    });
    cards(s, [
      ["extrude", T("A 2D shape pulled into 3D; turned and narrowed on the way.",
                    "2D forma ištempiama į 3D; pakeliui sukama ir siaurinama.")],
      ["sweep", T("A cross-section pushed along any 3D path.",
                  "Skerspjūvis stumiamas išilgai bet kokio 3D kelio.")],
      ["loft", T("A surface skinned over a sequence of cross-sections.",
                 "Paviršius, uždengiantis skerspjūvių seką.")],
      ["polyline, trace", T("A tube through a list of points; the path of a vector field.",
                            "Vamzdis per taškų sąrašą; vektorinio lauko trajektorija.")],
    ], { y: 4.05, h: 1.12, perRow: 2 });
  }

  // =========================================================== 19. curves
  {
    const s = sheet(T("curve() -- curves as tubes", "curve() – kreivės kaip vamzdžiai"),
                    T("surfaces", "paviršiai"));
    picture(s, "curves.png", { x: M, y: 1.55, w: 5.3, h: 3.75 });
    code(s, [
      T("def knot(t):", "def mazgas(t):"),
      "  return [add.sin(t) + 2*add.sin(2*t),",
      "          -add.sin(3*t),",
      "          add.cos(t) - 2*add.cos(2*t)]", "",
      T("add.curve(knot, 0, 2*add.pi,", "add.curve(mazgas, 0, 2*add.pi,"),
      "    300, 18, 0.28, \"lime\", True)",
    ], { x: 6.05, y: 1.6, w: 3.33, h: 2.3, fontSize: 9.5 });
    s.addText(T("The radius may be a function r(t) -- the tube swells and narrows. The tube "
                + "does not twist on its own: a rotation-minimising frame is carried along the curve.",
                "Spindulys gali būti ir funkcija r(t) – vamzdis storėja ir plonėja. Vamzdis pats "
                + "nesisuka: išilgai kreivės nešamas minimaliai sukantis rėmas."), {
      x: 6.05, y: 4.05, w: 3.33, h: 1.3, isTextBox: true, margin: 0,
      fontFace: BODY_FONT, fontSize: 12.5, color: MUTED, valign: "top",
    });
  }

  // =========================================================== 20. transforms
  {
    const s = sheet(T("Transformations", "Transformacijos"), T("layers", "sluoksniai"));
    cards(s, [
      ["move, place, align, ground", T("Shift; put the centre, a corner or the bottom at a point.",
                                       "Pastūmimas; centrą, kampą ar apačią pastato į nurodytą tašką.")],
      ["rotateX/Y/Z, rotate, aim", T("Turn about an axis -- any axis -- or aim a part along a direction.",
                                     "Sukimas apie ašį – bet kokią – arba detalės nukreipimas kryptimi.")],
      ["zoom, stretch, fit", T("Scale: uniform, per axis, or to a size.",
                               "Mastelis: vienodas, atskiras kiekvienai ašiai arba pagal dydį.")],
      ["mirror", T("Reflection in a plane; the face winding is reversed too.",
                   "Atspindys plokštumoje; sienų kryptis apsukama.")],
      ["twist, bend, taper", T("Twist, bend, narrow.", "Susukimas, sulenkimas, siaurėjimas.")],
      ["deform", T("Any function of yours: f(p) -> new point.", "Bet kokia jūsų funkcija f(p) → naujas taškas.")],
    ], { h: 1.14 });
    s.addText(T("All of them return a new mesh -- the original is untouched, so they chain:",
                "Visos jos grąžina naują modelį – originalas nepakinta, todėl jas galima jungti į grandinę:"), {
      x: M, y: 5.75, w: W - 2 * M, h: 0.4, isTextBox: true, margin: 0,
      fontFace: BODY_FONT, fontSize: 14, color: INK,
    });
    code(s, ["M = add.move(add.rotateY(add.zoom(M, 0.5), 0.4), [0, 3, 0])"],
         { x: M, y: 6.2, w: W - 2 * M, h: 0.52, fontSize: 12 });
  }

  // =========================================================== 21. patterns
  {
    const s = sheet(T("One part, many copies", "Viena detalė, daug kopijų"), T("layers", "sluoksniai"));
    picture(s, "patterns.png", { x: M, y: 1.55, w: 5.3, h: 3.75 });
    s.addText([
      mono("array_linear(M, step, n)\n"),
      mono("array_grid(M, steps, counts)\n"),
      mono("array_radial(M, n, axis, P)\n"),
      mono("array_mirror(M, point, normal)\n"),
      mono("scatter(M, points, seed)\n"),
      mono("along(M, path, n)\n\n"),
      mono("repeat(M, n, step)\n", { bold: true, color: BROWN }),
      { text: T("The most general: you say where copy number i ends up.",
                "Bendriausias variantas: jūs pasakote, kur atsiduria kopija numeris i."), options: {} },
    ], {
      x: 6.05, y: 1.65, w: 3.33, h: 2.9, isTextBox: true, margin: 0,
      fontFace: BODY_FONT, fontSize: 13, color: INK, lineSpacing: 18, valign: "top",
    });
    code(s, [
      T("spiral = add.repeat(brick, 40,", "spirale = add.repeat(plyta, 40,"),
      "    lambda M, i: add.move(",
      "        add.rotateY(M, i * 0.3),",
      "        [0, i * 0.2, 0]))",
    ], { x: 6.05, y: 4.6, w: 3.33, h: 1.35, fontSize: 10.5 });
  }

  // =========================================================== 22. parts
  {
    const s = sheet(T("Parts that models keep needing", "Detalės, kurių prireikia kiekvienam modeliui"),
                    T("new", "nauja"));
    picture(s, "locomotive.png", { x: M, y: 1.55, w: 4.3, h: 2.55,
      caption: T("23_locomotive.py -- wheel, beam, rotate_point, array_mirror",
                 "23_locomotive.py – wheel, beam, rotate_point, array_mirror") });
    picture(s, "windmill.png", { x: 5.1, y: 1.55, w: 4.28, h: 2.55,
      caption: T("24_windmill.py -- extrude, arch, stairs, tree, scatter, along",
                 "24_windmill.py – extrude, arch, stairs, tree, scatter, along") });
    cards(s, [
      ["beam(A, B, w, h)", T("A bar between two points -- it works out the orientation itself.",
                             "Sija tarp dviejų taškų – orientaciją apskaičiuoja pati.")],
      ["wheel, gear, arch, stairs", T("Wheels with spokes, cogs that mesh, arches, flights of steps.",
                                      "Ratai su stipinais, sukimbantys krumpliaračiai, arkos, laiptai.")],
      ["roof, column, bricks, tree", T("Houses, temples, walls, forests.",
                                       "Namai, šventyklos, sienos, miškai.")],
      ["pixels, heightmap, text", T("Pixel art, block terrain, labels in a built-in font (ĄČĘĖĮŠŲŪŽ too).",
                                    "Pikselinis piešinys, kubelių reljefas, užrašai įmontuotu šriftu (ir ĄČĘĖĮŠŲŪŽ).")],
    ], { y: 4.65, h: 1.1, perRow: 2 });
  }

  // =========================================================== 23. placing
  {
    const s = sheet(T("Placing: aim, scatter, along", "Išdėstymas: aim, scatter, along"), T("new", "nauja"));
    code(s, [
      T("# a part built around the origin, pointing up", "# detalė aplink koordinačių pradžią, žiūri aukštyn"),
      "add.push()",
      "add.capsule([0, 0, 0], [0, 2, 0], 0.2, 12, \"silver\")",
      "arm = add.pop()",
      "",
      T("# aim it from shoulder to hand, then move it",
        "# nukreipti nuo peties į plaštaką, perkelti"),
      "arm = add.aim(arm, add.direction(shoulder, hand))",
      "add.mesh(add.move(arm, shoulder))",
      "",
      T("# forty trees on the hills", "# keturiasdešimt medžių ant kalvų"),
      "spots = add.random_points(40, lo, hi, seed=1,",
      "                          height=hills)",
      "add.mesh(add.scatter(tree, spots, seed=1,",
      "                     scale=(0.7, 1.4)))",
    ], { x: M, y: 1.6, w: 5.3, h: 3.5, fontSize: 10 });
    picture(s, "robot.png", { x: 6.05, y: 1.6, w: 3.33, h: 3.5,
      caption: T("27_robot.py -- every limb aimed at a point", "27_robot.py – kiekviena galūnė nukreipta į tašką") });
    s.addText(T("Build every part around the origin between push() and pop(); then aim it, "
                + "turn it, and move it into place.",
                "Kiekvieną detalę kurkite aplink koordinačių pradžią tarp push() ir pop(); "
                + "tada nukreipkite, pasukite ir perkelkite į vietą."), {
      x: M, y: 5.45, w: W - 2 * M, h: 0.7, isTextBox: true, margin: 0,
      fontFace: TITLE_FONT, fontSize: 16, color: BROWN,
    });
  }

  // =========================================================== 24. colours
  {
    const s = sheet(T("Colours", "Spalvos"), T("layers", "sluoksniai"));
    code(s, [
      T("add.box(c, 1, \"red\")            # by name", "add.box(c, 1, \"red\")            # vardu"),
      "add.box(c, 1, \"#ff8800\")        # hex",
      "add.box(c, 1, [255, 136, 0])    # RGB", "",
      T("add.hsv(0.3, 0.7, 1.0)          # hue", "add.hsv(0.3, 0.7, 1.0)          # atspalvis"),
      T("add.gradient(t, \"navy\", \"gold\") # blend", "add.gradient(t, \"navy\", \"gold\") # perėjimas"),
      T("add.shade(\"red\", 0.6)           # darker", "add.shade(\"red\", 0.6)           # tamsiau"),
      "",
      "M = add.color_by(M,",
      "        lambda p: add.hsv(p[1] / 10.0))",
    ], { x: M, y: 1.6, w: 5.0, h: 2.9, fontSize: 12 });
    cards(s, [
      [T("color(M, colour)", "color(M, spalva)"), T("Repaints the whole mesh.", "Perdažo visą modelį.")],
      ["color_by(M, fn)", T("Colour by the position of each face -- rainbows, height maps.",
                            "Spalva pagal sienos padėtį – vaivorykštės, aukščio žemėlapiai.")],
      ["color_gradient", T("A blend from one colour to another along an axis.",
                           "Perėjimas nuo vienos spalvos iki kitos išilgai ašies.")],
      ["color_random", T("Every face its own random colour.", "Kiekvienai sienai – sava atsitiktinė spalva.")],
    ], { y: 4.6, h: 1.1, perRow: 2 });
    s.addText(T("The assignment wants at least three colours -- it looks better when they mean something.",
                "Užduočiai reikia bent trijų spalvų – bet gražiau, kai jos ką nors reiškia."), {
      x: 5.8, y: 1.85, w: 3.6, h: 1.5, isTextBox: true, margin: 0,
      fontFace: TITLE_FONT, fontSize: 17, color: BROWN, valign: "top",
    });
  }

  // =========================================================== 25. booleans
  {
    const s = sheet(T("Boolean operations on solids", "Loginės operacijos su kūnais"), T("solids", "kūnai"));
    picture(s, "booleans.png", { x: M, y: 1.55, w: 5.3, h: 3.6 });
    s.addText([
      mono("union(A, B)\n", { fontSize: 12.5, bold: true, color: BROWN }),
      { text: T("Union: everything in either solid. Hidden inner walls disappear.\n",
                "Sąjunga: viskas, kas yra bet kuriame kūne. Paslėptos vidinės sienos dingsta.\n"),
        options: { breakLine: true } },
      mono("\nintersect(A, B)\n", { fontSize: 12.5, bold: true, color: BROWN }),
      { text: T("Intersection: only what is common.\n", "Sankirta: tik tai, kas bendra.\n"),
        options: { breakLine: true } },
      mono("\ndifference(A, B)\n", { fontSize: 12.5, bold: true, color: BROWN }),
      { text: T("Difference: A with B cut out. This is how holes and notches are made.\n",
                "Skirtumas: A su iškirptu B. Taip daromos skylės ir įpjovos.\n"),
        options: { breakLine: true } },
      mono(T("\ncut(M, point, normal)\n", "\ncut(M, taškas, normalė)\n"),
           { fontSize: 12.5, bold: true, color: BROWN }),
      { text: T("A cut with a plane -- cheaper.", "Pjūvis plokštuma – pigiau."), options: {} },
    ], {
      x: 6.05, y: 1.55, w: 3.33, h: 3.7, isTextBox: true, margin: 0,
      fontFace: BODY_FONT, fontSize: 11, color: INK, lineSpacing: 13, valign: "top",
    });
    code(s, [
      "add.cuboid([0,0,0], [4,1,4], \"brown\")",
      T("plate = add.layer()", "plokste = add.layer()"),
      "add.cylinder([0,-1,0], [0,1,0], 0.6, 32, \"black\")",
      T("drill = add.layer()", "grezlas = add.layer()"),
      T("add.mesh(add.difference(plate, drill))", "add.mesh(add.difference(plokste, grezlas))"),
    ], { x: M, y: 5.45, w: 8.76, h: 1.4, fontSize: 11.5 });
  }

  // =========================================================== 26. how csg
  {
    const s = sheet(T("How the booleans work", "Kaip veikia loginės operacijos"), T("solids", "kūnai"));
    cards(s, [
      [T("1. Split", "1. Perpjaunama"),
        T("Every face is cut where the other solid's triangles could cross it. Neighbours "
          + "come from a spatial grid, so a distant face is never cut.",
          "Kiekviena siena perpjaunama ten, kur ją galėtų kirsti kito kūno trikampiai. "
          + "Kaimynai randami per erdvinį tinklelį, todėl toli esanti siena nepjaustoma.")],
      [T("2. Ask", "2. Klausiama"),
        T("Each piece is asked: inside, outside, or lying on the other surface? A ray "
          + "counting crossings answers.",
          "Kiekvienos dalies klausiama: ar ji viduje, išorėje, ar guli ant kito kūno "
          + "paviršiaus? Atsako spindulys, skaičiuojantis susikirtimus.")],
      [T("3. Keep", "3. Atrenkama"),
        T("Union keeps what is outside; intersection what is inside; difference A's "
          + "outside and B's inside, reversed.",
          "Sąjunga palieka tai, kas išorėje; sankirta – kas viduje; skirtumas – A išorę "
          + "ir apverstą B vidų.")],
    ], { y: 1.6, h: 1.95, perRow: 3 });
    s.addText([
      { text: T("About 600 lines of plain Python. No libraries.\n\n",
                "Apie 600 eilučių gryno Python. Jokių bibliotekų.\n\n"),
        options: { bold: true, breakLine: true } },
      { text: T("A 6000-face sphere minus a box: about 0.5 s.  ", "6000 sienų sfera minus dėžė – apie 0,5 s.  "), options: {} },
      { text: T("25 000 faces: about 2 s.\n", "25 000 sienų – apie 2 s.\n"), options: { breakLine: true } },
      { text: T("The result is welded, its T-junctions healed, the surface closed.",
                "Rezultatas suklijuotas, plyšeliai užtaisyti, paviršius uždaras."), options: {} },
    ], {
      x: M, y: 3.9, w: W - 2 * M, h: 1.3, isTextBox: true, margin: 0,
      fontFace: BODY_FONT, fontSize: 15, color: INK, lineSpacing: 22, valign: "top",
    });
    s.addShape(pres.ShapeType.roundRect, {
      x: M, y: 5.25, w: W - 2 * M, h: 1.05, rectRadius: 0.05, fill: { color: "EAF3EF" },
    });
    s.addText(T("Booleans need closed solids. If the result looks odd, check both inputs with add.check() first.",
                "Loginėms operacijoms reikia uždarų kūnų. Jei rezultatas keistas – pirmiausia "
                + "patikrinkite abu pradinius kūnus su add.check()."), {
      x: M + 0.25, y: 5.45, w: W - 2 * M - 0.5, h: 0.7, isTextBox: true,
      margin: 0, fontFace: BODY_FONT, fontSize: 14, color: TEAL, valign: "top",
    });
  }

  // =========================================================== 27. clean
  {
    const s = sheet(T("Repairing and checking a model", "Modelio taisymas ir tikrinimas"), T("tools", "įrankiai"));
    cards(s, [
      ["clean(M)", T("Welds coincident vertices, drops zero-area and repeated faces, removes "
                     + "the inner walls where two solids touch.",
                     "Suklijuoja sutampančias viršūnes, pašalina nulinio ploto ir pasikartojančias "
                     + "sienas, išmeta vidines sieneles ten, kur du kūnai liečiasi.")],
      ["heal(M)", T("Closes the hairline gaps where an edge passes a foreign vertex.",
                    "Užtaiso plyšelius ten, kur briauna praeina pro svetimą viršūnę.")],
      ["fix_normals(M)", T("Points every face the same way -- outwards, for a closed model.",
                           "Nukreipia visas sienas ta pačia kryptimi, uždarame modelyje – į išorę.")],
      ["triangulate(M), inside(M, p)", T("Every face a triangle; is a point inside the solid?",
                                         "Visos sienos – trikampiai; ar taškas yra kūno viduje?")],
    ], { y: 1.58, h: 1.24, perRow: 2 });
    code(s, [
      T("model = add.clean(add.layer())", "modelis = add.clean(add.layer())"),
      T("add.mesh(model)", "add.mesh(modelis)"),
      "add.check()",
    ], { x: M, y: 4.45, w: 4.3, h: 1.1, fontSize: 12.5 });
    code(s, [
      "  vertices            136768",
      "OK polygons            163132",
      "OK colours             6",
      "OK closed surface      yes",
      "   volume              60.286",
    ], { x: 5.15, y: 4.45, w: 4.23, h: 1.55, fontSize: 11 });
    note(s, T("Two touching cubes each keep a wall where nobody can see it. clean() finds and removes them. "
              + "examples/31_workbench.py shows every repair tool at work.",
              "Sudėjus du besiliečiančius kubus, kiekvienas pasilieka savo sienelę toje vietoje, kur jos "
              + "niekas nemato. clean() jas randa ir pašalina. examples/31_workbench.py rodo visus taisymo įrankius."));
  }

  // =========================================================== 27b. polyhedra + sphere
  {
    const s = sheet(T("The five regular polyhedra, and a sphere of triangles",
                      "Penki taisyklingieji briaunainiai ir sfera iš trikampių"), T("shapes", "figūros"));
    code(s, [
      "add.icosahedron([0, 0, 0], 2, \"purple\")",
      "add.dodecahedron([5, 0, 0], 2, \"gold\")",
      "P = add.polyhedron_points(\"icosahedron\")",
      "",
      "add.sphere([0, 5, 0], 2, 20, \"sky\")    # 5120 tri",
      "add.icosphere([5, 5, 0], 2, 3, \"red\")  # 1280",
      "add.quadsphere([9, 5, 0], 2, 12, \"gold\")",
    ], { x: M, y: 1.6, w: 5.15, h: 2.45, fontSize: 11.5 });
    picture(s, "polyhedra.png", { x: 5.95, y: 1.6, w: 3.43, h: 2.45,
      caption: T("38_polyhedra.py -- solids, duals, truncations, domes, smooth",
                 "38_polyhedra.py – kūnai, dualieji, nupjovimai, kupolai, glotnūs") });
    cards(s, [
      [T("Centred", "Sucentruota"), T("The average of the vertices is exactly the centre; every vertex at distance r.",
                                      "Viršūnių vidurkis yra lygiai centras; kiekviena viršūnė atstumu r.")],
      [T("The dome principle", "Kupolo principas"), T("Split every triangle in four, push the midpoints out to the sphere, repeat: 20, 80, 320, 1280 ...",
                                                        "Kiekvieną trikampį į keturis, vidurio taškus – ant sferos, kartoti: 20, 80, 320, 1280 ...")],
      [T("k as before", "k kaip anksčiau"), T("sphere(c, r, k) picks the level from k: k=10 -> 1280, k=20 -> 5120 faces.",
                                             "sphere(c, r, k) lygį parenka pagal k: k=10 -> 1280, k=20 -> 5120 sienų.")],
    ], { y: 4.5, h: 1.5, perRow: 3 });
    s.addNotes(T("Example 36 shows the same sphere three ways: the Maple cube-sphere, a ball of blocks, the geodesic one.",
                 "36 pavyzdys rodo tą pačią sferą trimis būdais: Maple kubo sferą, kubelių rutulį, geodezinę."));
  }

  // =========================================================== 27c. football
  {
    const s = sheet(T("A football from the vertices of an icosahedron", "Futbolo kamuolys iš ikosaedro viršūnių"),
                    T("vertex tools", "viršūnių įrankiai"));
    code(s, [
      "ico = add.make(add.icosahedron, [0, 0, 0], 3)",
      "print(add.neighbors(ico, 0))   # 5, in order",
      "print(add.valence(ico, 0))",
      "",
      "ball = add.truncate(ico, 1 / 3.0)   # corners off",
      "ball = add.color_by_sides(ball,",
      "                          {5: \"black\", 6: \"white\"})",
      "add.mesh(add.smooth(ball, 16))      # rounded",
    ], { x: M, y: 1.6, w: 5.15, h: 2.6, fontSize: 11.5 });
    picture(s, "football.png", { x: 5.95, y: 1.6, w: 3.43, h: 2.6,
      caption: T("37_football.py", "37_football.py") });
    cards(s, [
      [T("Ask the mesh", "Paklauskite tinklo"), T("neighbors, valence, mean_neighbor_distance, edges, vertex_normal, face_center, boundary_loops.",
                                                  "neighbors, valence, mean_neighbor_distance, edges, vertex_normal, face_center, boundary_loops.")],
      [T("Change one corner", "Pakeiskite vieną kampą"), T("set_vertex(M, i, [x, None, z]) moves vertex i and keeps the faces -- then smooth() it.",
                                                            "set_vertex(M, i, [x, None, z]) perkelia viršūnę i ir palieka sienas – tada smooth().")],
      [T("Rebuild", "Perkurkite"), T("dual, truncate, refine + spherify, inflate -- new solids from old ones.",
                                    "dual, truncate, refine + spherify, inflate – nauji kūnai iš senų.")],
    ], { y: 4.65, h: 1.45, perRow: 3 });
  }

  // =========================================================== 27d. smooth
  {
    const s = sheet(T("Smooth surfaces: generalised Catmull-Clark", "Glotnūs paviršiai: apibendrintas Catmull–Clark"),
                    T("smooth()", "smooth()"));
    code(s, [
      "add.box([0, 0, 0], 2, \"gold\")",
      "block = add.layer()",
      "i = add.nearest_vertex(block, [1, 1, 1])",
      "block = add.set_vertex(block, i, [2.5, 2.5, None])",
      "",
      "add.mesh(add.smooth(block, 8))    # 8 per edge",
      "add.mesh(add.catmull_clark(block, 3))",
    ], { x: M, y: 1.6, w: 5.15, h: 2.35, fontSize: 11.5 });
    picture(s, "smooth_shapes.png", { x: 5.95, y: 1.6, w: 3.43, h: 2.35,
      caption: T("39_smooth_shapes.py -- n = 1 ... 7 on one prism", "39_smooth_shapes.py – n = 1 ... 7 ant vienos prizmės") });
    cards(s, [
      [T("Any n", "Bet koks n"), T("n cells on every control edge for n = 1, 2, 3, 4, 5 ... -- classical subdivision only gives 2, 4, 8.",
                                  "n langelių ant kiekvienos kontrolinės briaunos, n = 1, 2, 3, 4, 5 ... – klasikinis dalijimas duoda tik 2, 4, 8.")],
      [T("Exactly on the limit surface", "Tiksliai ant ribinio paviršiaus"), T("Every new vertex is evaluated on the limit surface; near odd corners the grid is reparameterised to stay even.",
                                                                              "Kiekviena nauja viršūnė skaičiuojama ant ribinio paviršiaus; prie ypatingųjų kampų tinklas perparametrizuojamas, kad liktų tolygus.")],
      [T("The paper", "Straipsnis"), T("Sabaliauskas, Uniform n-grids on Catmull-Clark limit surfaces of arbitrary polygon meshes (2026); a line-by-line port to pure Python.",
                                       "Sabaliauskas, Uniform n-grids on Catmull–Clark limit surfaces of arbitrary polygon meshes (2026); perkelta eilutė po eilutės į gryną Python.")],
    ], { y: 4.4, h: 1.75, perRow: 3 });
  }

  // =========================================================== 27e. catalogue
  {
    const s = sheet(T("Twenty-five surfaces by name", "Dvidešimt penki paviršiai pagal vardą"), T("surface()", "surface()"));
    code(s, [
      "print(add.surface_names())",
      "add.surface(\"klein_bottle\", [0, 0, 0], 4, 120)",
      "add.surface(\"dini\", [6, 0, 0], 4,",
      "            color=lambda u, v: add.hsv(u / 12))",
      "add.surface(\"pillow\", [-6, 0, 0], 3, a=0.9)",
      "",
      "owl = add.surface_function(\"owl\")   # bare f(u, v)",
    ], { x: M, y: 1.6, w: 5.15, h: 2.35, fontSize: 11.5 });
    picture(s, "surface_zoo.png", { x: 5.95, y: 1.6, w: 3.43, h: 2.35,
      caption: T("34_surface_zoo.py", "34_surface_zoo.py") });
    picture(s, "knot_curve.png", { x: M, y: 4.35, w: 4.3, h: 2.2,
      caption: T("35_knot_curve.py -- a knot from rotating circles, one curve() call",
                 "35_knot_curve.py – mazgas iš besisukančių apskritimų, vienas curve() kvietimas") });
    picture(s, "minecraft_sphere.png", { x: 5.1, y: 4.35, w: 4.28, h: 2.2,
      caption: T("36_minecraft_sphere.py -- Maple, blocks, geodesic", "36_minecraft_sphere.py – Maple, kubeliai, geodezinė") });
  }

  // =========================================================== 27f. glass and textures
  {
    const s = sheet(T("Glass, pictures and the Sketchfab limits", "Stiklas, paveikslėliai ir Sketchfab ribos"),
                    T(".obj + .mtl", ".obj + .mtl"));
    code(s, [
      "glass = add.transparent(\"sky\", 0.35)  # 0..1",
      "add.cuboid([0, 1.5, 2], [2, 1.2, 0.1], glass)",
      "wall = add.make(add.cuboid, [0, 1.5, 0], [6, 3, 1])",
      "add.mesh(add.texture(wall, \"bricks.png\", \"box\"))",
      "",
      "add.check()     # <= 50 MB, <= 50 colours",
      "add.save(\"house.obj\", colors=50)   # .mtl",
    ], { x: M, y: 1.6, w: 5.15, h: 2.35, fontSize: 11.5 });
    picture(s, "glass_and_textures.png", { x: 5.95, y: 1.6, w: 3.43, h: 2.35,
      caption: T("45_glass_and_textures.py", "45_glass_and_textures.py") });
    cards(s, [
      [T("Optional", "Neprivaloma"), T("Without transparent/texture everything is exactly as before; .off files keep plain colours.",
                                      "Be transparent/texture viskas lygiai kaip anksčiau; .off failuose lieka paprastos spalvos.")],
      [T("Limits", "Ribos"), T("Sketchfab: 100 MB free plan, 100 materials merged beyond that. The course: 50 MB, 50 colours. limit_colors() and obj_size() help.",
                              "Sketchfab: 100 MB nemokamai, medžiagos virš 100 suliejamos. Kursas: 50 MB, 50 spalvų. Padeda limit_colors() ir obj_size().")],
      [T("Pictures from code", "Paveikslėliai iš kodo"), T("write_png(\"bricks.png\", rows) writes a picture you computed -- no image files needed.",
                                                          "write_png(\"bricks.png\", rows) įrašo patį paskaičiuotą paveikslėlį – failų nereikia.")],
    ], { y: 4.4, h: 1.75, perRow: 3 });
  }

  // =========================================================== 27g. the castle
  {
    const s = sheet(T("The castle: a model bigger than memory", "Pilis: modelis, didesnis už atmintį"),
                    T("46_castle.py, stream()", "46_castle.py, stream()"));
    picture(s, "castle.png", { x: M, y: 1.45, w: 5.3, h: 3.4,
      caption: T("no textures, every stone a polygon: a 400 MB .off and an .obj that 7-Zip brings under 100 MB for Sketchfab",
                 "be tekstūrų, kiekvienas akmuo – daugiakampis: 400 MB .off ir .obj, kurį 7-Zip suglaudina iki 100 MB Sketchfab") });
    picture(s, "castle_hall.png", { x: 5.85, y: 1.45, w: 3.55, h: 1.55,
      caption: T("the throne hall and the feast", "sosto menė ir puota") });
    picture(s, "castle_treasury.png", { x: 5.85, y: 3.3, w: 3.55, h: 1.55,
      caption: T("the dragon on the treasure", "drakonas ant lobio") });
    code(s, [
      "out = add.stream(\"castle.off\", precision=4)   # parts go to disk at once,",
      "wall_of_bricks(); out.add()   # tidied (no overlaps), written, cleared",
      "out.close()                   # fills in the OFF header (.mtl for .obj)",
    ], { x: M, y: 5.55, w: 9.1, h: 1.05, fontSize: 11 });
  }

  // =========================================================== 28. export
  {
    const s = sheet(T("Saving and sharing a model", "Modelio išsaugojimas ir viešinimas"), T("files", "failai"));
    code(s, [
      T("add.save(\"model.off\")   # the course format", "add.save(\"modelis.off\")   # kurso formatas"),
      T("add.save(\"model.obj\")   # + .mtl for colours", "add.save(\"modelis.obj\")   # + .mtl spalvoms"),
      T("add.save(\"model.ply\")", "add.save(\"modelis.ply\")"),
      T("add.save(\"model.stl\")   # for 3D printing", "add.save(\"modelis.stl\")   # 3D spausdinimui"),
    ], { x: M, y: 1.6, w: 5.0, h: 1.65, fontSize: 12.5 });
    cards(s, [
      ["Sketchfab", T("Put .obj and .mtl in one archive and upload -- anyone can turn the model in a browser.",
                      "Sudėkite .obj ir .mtl į vieną archyvą ir įkelkite – modelį galės pasukioti bet kas naršyklėje.")],
      [T("3D printing", "3D spausdinimas"), T("clean(..., normals=True), then save(\"m.stl\"). The surface must be closed.",
                                              "clean(..., normals=True), tada save(\"m.stl\"). Paviršius turi būti uždaras.")],
      [T("Preview without MeshLab", "Peržiūra be MeshLab"), T("python3 tools/preview.py model.off writes a PNG. No libraries either.",
                                                              "python3 tools/preview.py modelis.off sukuria PNG. Irgi be jokių bibliotekų.")],
      [T("Loading back", "Įkėlimas atgal"), T("load(\"letter.off\") returns a mesh you can move and paint.",
                                              "load(\"raide.off\") grąžina modelį, kurį galima stumdyti ir dažyti.")],
    ], { y: 3.45, h: 1.35, perRow: 2 });
    s.addText(T("The MeshLab conversion step is gone -- add.py writes OBJ and MTL itself.",
                "MeshLab konvertavimo žingsnis nebereikalingas – add.py OBJ ir MTL parašo pats."), {
      x: 5.8, y: 1.85, w: 3.6, h: 1.2, isTextBox: true, margin: 0,
      fontFace: TITLE_FONT, fontSize: 17, color: BROWN, valign: "top",
    });
  }

  // =========================================================== 29-30. examples
  {
    const s = sheet(T("Complete models", "Pilni modeliai"), T("gallery", "galerija"));
    picture(s, "temple.png", { x: M, y: 1.55, w: 4.3, h: 2.6,
      caption: T("25_temple.py -- columns on a circle, a chequered floor",
                 "25_temple.py – kolonos ant apskritimo, languotos grindys") });
    picture(s, "bridge.png", { x: 5.1, y: 1.55, w: 4.28, h: 2.6,
      caption: T("29_bridge.py -- beams, cables, hangers, cars along the road",
                 "29_bridge.py – sijos, lynai, pakabos, automobiliai kelyje") });
    picture(s, "voxel_island.png", { x: M, y: 4.55, w: 4.3, h: 2.1 });
    picture(s, "vector_fields.png", { x: 5.1, y: 4.55, w: 4.28, h: 2.1 });
  }
  {
    const s = sheet(T("Larger studies", "Didesnės studijos"), T("gallery", "galerija"));
    picture(s, "chess_set.png", { x: M, y: 1.55, w: 4.3, h: 2.6,
      caption: T("18_chess_set.py -- lathe, layers, booleans", "18_chess_set.py – sukinys, sluoksniai, loginės operacijos") });
    picture(s, "fractals.png", { x: 5.1, y: 1.55, w: 4.28, h: 2.6,
      caption: T("17_fractals.py -- Menger sponge, Sierpinski, a tree", "17_fractals.py – Mengerio kempinė, Sierpinskis, medis") });
    picture(s, "city.png", { x: M, y: 4.55, w: 4.3, h: 2.1 });
    picture(s, "example4.png", { x: 5.1, y: 4.55, w: 4.28, h: 2.1 });
    s.addNotes(T("42 example programs; every public function is used by at least one of them "
                 + "(python3 tools/coverage.py), and every model fits the Sketchfab limits.",
                 "42 pavyzdinės programos; kiekviena vieša funkcija panaudota bent vienoje "
                 + "(python3 tools/coverage.py), ir kiekvienas modelis telpa į Sketchfab ribas."));
  }

  // =========================================================== 31. migration
  {
    const s = sheet(T("From 1.2 to " + VERSION, "Nuo 1.2 prie " + VERSION), T("compatibility", "suderinamumas"));
    const rows = [
      ["cube2(c, e, b, RGB)", "frame", T("a hollow cube of bars", "kubo briaunų karkasas")],
      ["cylinder2(A, B, r, k, RGB)", "tube", T("a cylinder with no lids", "cilindras be dangtelių")],
      ["cylinder3(A, B, r, k, RGB)", "cup", T("closed at one end", "uždarytas iš vieno galo")],
      ["cone2(A, B, r, k, RGB)", "cone_open", T("the slanted wall only", "tik šoninis paviršius")],
      ["rectangle3D(c, e, RGB)", "cuboid", T("a rectangular block", "stačiakampis gretasienis")],
      ["newface(A, RGB)", "polygon", T("one flat face", "viena plokščia siena")],
      ["spin3D(A, B, S, ...)", "revolve", T("a lathe", "sukinys")],
      [T("off(file)", "off(failas)"), T("save(file)", "save(failas)"), T(".off, .obj, .ply or .stl", ".off, .obj, .ply arba .stl")],
    ];
    const head = (t) => ({ text: t, options: { bold: true, color: WHITE, fill: { color: BROWN }, fontSize: 12 } });
    const tableRows = [[head("add.py 1.2"), head("add.py " + VERSION), head(T("what it is", "kas tai"))]]
      .concat(rows.map(r => [
        { text: r[0], options: { fontFace: MONO, fontSize: 11.5 } },
        { text: r[1], options: { fontFace: MONO, fontSize: 11.5, bold: true, color: BROWN } },
        { text: r[2], options: { fontSize: 11.5 } },
      ]));
    s.addTable(tableRows, {
      x: M, y: 1.6, w: W - 2 * M, colW: [3.5, 2.2, 3.06],
      border: { type: "solid", color: LINE, pt: 0.75 },
      fontFace: BODY_FONT, color: INK, valign: "middle", rowH: 0.34, margin: 0.06,
    });
    s.addShape(pres.ShapeType.roundRect, {
      x: M, y: 5.35, w: W - 2 * M, h: 1.15, rectRadius: 0.05, fill: { color: SAND },
    });
    s.addText(T("All the old names still work. Twelve models written for 1.2 live in tests/legacy/, "
                + "and the tests check that they produce exactly as many faces as before "
                + "(only sphere changed: it is geodesic now; quadsphere is the old one). "
                + "examples/32_old_names.py is a whole model in the 1.2 vocabulary.",
                "Visi seni vardai tebeveikia. Dvylika 1.2 versijai rašytų modelių guli tests/legacy/ "
                + "aplanke, ir testai tikrina, kad jie duotų lygiai tiek pat sienų kaip anksčiau "
                + "(pasikeitė tik sphere: dabar geodezinė; senoji – quadsphere). "
                + "examples/32_old_names.py – ištisas modelis 1.2 žodynu."), {
      x: M + 0.25, y: 5.55, w: W - 2 * M - 0.5, h: 0.8, isTextBox: true,
      margin: 0, fontFace: BODY_FONT, fontSize: 13, color: INK, valign: "top",
    });
  }

  // =========================================================== 32. where
  {
    const s = pres.addSlide();
    slideNumber += 1;
    s.background = { color: DARK };
    s.addText(T("Where to find everything", "Kur viską rasti"), {
      x: M, y: 1.15, w: W - 2 * M, h: 0.8, isTextBox: true, margin: 0,
      fontFace: TITLE_FONT, fontSize: 38, bold: true, color: WHITE,
    });
    s.addText([
      { text: T("The module, the examples, the tests and the documentation\n",
                "Modulis, pavyzdžiai, testai ir dokumentacija\n"),
        options: { color: "E9C9AE", breakLine: true } },
      { text: "github.com/…/add3d\n\n", options: { fontFace: MONO, fontSize: 17, color: WHITE, breakLine: true } },
      { text: T("Documentation in English and Lithuanian\n", "Dokumentacija angliškai ir lietuviškai\n"),
        options: { color: "E9C9AE", breakLine: true } },
      { text: "…github.io/add3d\n\n", options: { fontFace: MONO, fontSize: 17, color: WHITE, breakLine: true } },
      { text: T("Questions\n", "Klausimai\n"), options: { color: "E9C9AE", breakLine: true } },
      { text: "akatasis@gmail.com  ·  martynas.sabaliauskas@mif.vu.lt", options: { fontSize: 15, color: WHITE } },
    ], {
      x: M, y: 2.25, w: 5.6, h: 3.4, isTextBox: true, margin: 0,
      fontFace: BODY_FONT, fontSize: 14, lineSpacing: 22, valign: "top",
    });
    s.addImage({
      path: img("supershapes.png"), x: 6.0, y: 2.1, w: 3.4, h: 2.4,
      sizing: { type: "contain", w: 3.4, h: 2.4 },
    });
    s.addText(T("Thank you.", "Ačiū už dėmesį."), {
      x: M, y: 6.1, w: W - 2 * M, h: 0.5, isTextBox: true, margin: 0,
      fontFace: TITLE_FONT, fontSize: 20, color: "C9BFB6",
    });
    s.addNotes(T("For students: start with examples/01_first_model.py, then 02_primitives.py. "
                 + "For the assignment, examples 06-16 and the complete models 22-33 are the most useful.",
                 "Studentams: pradėkite nuo examples/01_first_model.py, paskui 02_primitives.py. "
                 + "Užduočiai labiausiai praverčia 06-16 pavyzdžiai ir pilni modeliai 22-33."));
  }

  return pres.writeFile({ fileName: OUT }).then(() => {
    console.log("written: " + OUT + " (" + slideNumber + " slides)");
  });
}

(async () => {
  const langs = process.argv[2] ? [process.argv[2]] : ["en", "lt"];
  for (const lang of langs) {
    await build(lang);
  }
})();

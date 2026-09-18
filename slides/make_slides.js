/*
 * Builds slides/add_py_2026.pptx -- the add.py part of the first lecture,
 * updated for version 2.0.  Lithuanian, 4:3 to match the existing deck.
 *
 *     node slides/make_slides.js
 */
const pptxgen = require("pptxgenjs");
const path = require("path");
const fs = require("fs");

const ROOT = path.join(__dirname, "..");
const IMG = path.join(ROOT, "docs", "images");
const OUT = path.join(__dirname, "add_py_2026.pptx");

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

const pres = new pptxgen();
pres.layout = "LAYOUT_4x3";
pres.author = "Martynas Sabaliauskas";
pres.company = "Vilniaus universitetas, MIF";
pres.title = "add.py 2.0";

let slideNumber = 0;

function img(name) {
  const p = path.join(IMG, name);
  if (!fs.existsSync(p)) throw new Error("missing image: " + p);
  return p;
}

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
    fontFace: BODY_FONT, fontSize: 16, color: INK, lineSpacing: 24,
    paraSpaceAfter: 8, valign: "top",
  }, opt));
}

function code(s, lines, opt) {
  opt = opt || {};
  const box = Object.assign({
    x: M, y: 1.6, w: 5.1, h: 2.6,
  }, opt);
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
    w: box.w - 0.12, h: box.h - 0.12, sizing: {
      type: "contain", w: box.w - 0.12, h: box.h - 0.12,
    },
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
  const w = (W - 2 * M - gap * (perRow - 1)) / perRow;
  items.forEach((it, i) => {
    const col = i % perRow, row = Math.floor(i / perRow);
    const x = M + col * (w + gap);
    const yy = y + row * (h + gap);
    s.addShape(pres.ShapeType.roundRect, {
      x: x, y: yy, w: w, h: h, rectRadius: 0.05,
      fill: { color: opt.tint || SAND }
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

// =========================================================== 1. title
{
  const s = pres.addSlide();
  s.background = { color: DARK };
  s.addText("add.py 2.0", {
    x: M, y: 1.25, w: W - 2 * M, h: 1.0, isTextBox: true, margin: 0,
    fontFace: TITLE_FONT, fontSize: 54, bold: true, color: WHITE,
  });
  s.addText("Trimačiai modeliai, sukurti vien tik programiniu kodu", {
    x: M, y: 2.25, w: W - 2 * M, h: 0.5, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 19, color: "E9C9AE",
  });
  s.addShape(pres.ShapeType.roundRect, {
    x: M, y: 3.15, w: W - 2 * M, h: 3.2, rectRadius: 0.04,
    fill: { color: "F4F3F1" },
  });
  s.addImage({
    path: img("chess_set.png"), x: M + 0.08, y: 3.23, w: W - 2 * M - 0.16,
    h: 3.04, sizing: { type: "contain", w: W - 2 * M - 0.16, h: 3.04 },
  });
  s.addText("Algoritmų kūrimas ir analizė  ·  kūrybinė užduotis  ·  2026",
    {
      x: M, y: 6.6, w: W - 2 * M, h: 0.4, isTextBox: true, margin: 0,
      fontFace: BODY_FONT, fontSize: 13, color: "C9BFB6",
    });
  s.addNotes("Šiose skaidrėse – atnaujinta add.py modulio dalis. "
    + "Modulis kasmet atnaujinamas; 2.0 versija yra didžiausias pokytis "
    + "nuo 1.2.");
}

// =========================================================== 2. what's new
{
  const s = sheet("Kas naujo 2.0 versijoje", "add.py");
  cards(s, [
    ["Loginės operacijos",
      "union, intersect, difference – sąjunga, sankirta ir skirtumas. "
      + "Parašyta nuo nulio, be jokių bibliotekų."],
    ["OBJ, PLY ir STL",
      "save(\"modelis.obj\") sukuria .obj ir .mtl – tiesiai į Sketchfab. "
      + "STL tinka 3D spausdinimui."],
    ["Modelio taisymas",
      "clean() suklijuoja viršūnes, pašalina pasikartojančias ir vidines "
      + "sienas; heal() užtaiso plyšelius."],
    ["check()",
      "Pasako, kiek turite daugiakampių ir spalvų, ar paviršius uždaras "
      + "ir ar užduoties reikalavimai jau įvykdyti."],
    ["Storis paviršiams",
      "thickness= paverčia ploną parametrinį lakštą tikru kūnu, "
      + "apšviestu iš abiejų pusių."],
    ["130 funkcijų",
      "Aiškesni vardai (box, tube, frame, revolve, sweep), bet visi seni "
      + "vardai tebeveikia."],
  ], { h: 1.28 });
  note(s, "Viskas, kas parašyta senajai 1.2 versijai, veikia be jokių "
    + "pataisymų.");
  s.addNotes("Svarbiausia žinia: nieko perrašinėti nereikia.");
}

// =========================================================== 3. assignment
{
  const s = sheet("Kūrybinė užduotis", "priminimas");
  bullets(s, [
    { text: "Sukurti 3D modelį naudojant tik pirminį programos tekstą.",
      options: { bold: true } },
    "Modelio failo formatas – OFF arba OBJ.",
    "Bent 10 000 daugiakampių.",
    "Bent 3 skirtingos spalvos.",
    "Algoritme privalo būti for arba while ciklas.",
    "Bent 1 parametras, nuo kurio priklauso modelio forma.",
    "Negalima naudoti 3D modeliavimui skirtų programų.",
    "Modelį galima kurti individualiai arba komandoje dviese.",
  ], { w: 5.3 });
  picture(s, "city.png", {
    x: 6.05, y: 1.62, w: 3.33, h: 2.35,
    caption: "Vienas skaičius (SEED) nulemia visą miestą",
  });
  s.addText([
    { text: "add.check()", options: { fontFace: MONO, bold: true,
      color: BROWN, breakLine: true } },
    { text: "pasako, kurie reikalavimai jau įvykdyti.",
      options: { fontFace: BODY_FONT } },
  ], {
    x: 6.05, y: 4.65, w: 3.33, h: 0.8, isTextBox: true, margin: 0,
    fontSize: 13, color: INK, valign: "top",
  });
}

// =========================================================== 4. tools
{
  const s = sheet("Rekomenduojami įrankiai", "aplinka");
  cards(s, [
    ["Python 3", "Daugiau nieko diegti nereikia. add.py naudoja tik "
      + "math ir random."],
    ["add.py", "Vienas failas šalia jūsų programos. Parsisiunčiamas iš "
      + "GitHub."],
    ["tools/preview.py", "Modelio peržiūra be jokios kitos programos: "
      + "sukuria PNG paveikslėlį."],
    ["GeoGebra", "Patogu pasitikrinti kreivių ir paviršių formules prieš "
      + "rašant kodą."],
    ["MeshLab", "OFF peržiūra ir konvertavimas. Nuo 2.0 nebebūtinas – "
      + "OBJ išsaugo pats add.py."],
    ["Sketchfab.com", ".obj + .mtl viename archyve – ir modelį galima "
      + "pasukioti naršyklėje."],
  ], { h: 1.3 });
  s.addNotes("Anksčiau MeshLab buvo būtinas norint gauti OBJ. Dabar ne.");
}

// =========================================================== 5. OFF format
{
  const s = sheet("Modelis – tai du sąrašai", "pagrindai");
  code(s, [
    "OFF",
    "8 6 0",
    "-1 -1 -1",
    "-1 -1  1",
    "  ...",
    "4 0 4 5 1 255 0 0",
    "4 0 1 3 2 255 0 0",
    "  ...",
  ], { x: M, y: 1.62, w: 4.1, h: 2.5, fontSize: 13 });
  s.addText([
    { text: "OFF", options: { fontFace: MONO, bold: true } },
    { text: "  – formato vardas", options: { breakLine: true } },
    { text: "8 6 0", options: { fontFace: MONO, bold: true } },
    { text: "  – viršūnių, sienų ir briaunų skaičius",
      options: { breakLine: true } },
    { text: "toliau – viršūnių koordinatės",
      options: { breakLine: true } },
    { text: "4 0 4 5 1", options: { fontFace: MONO, bold: true } },
    { text: "  – keturkampis, jungiantis viršūnes 0, 4, 5 ir 1",
      options: { breakLine: true } },
    { text: "255 0 0", options: { fontFace: MONO, bold: true } },
    { text: "  – sienos spalva" },
  ], {
    x: 5.0, y: 1.72, w: 4.4, h: 2.4, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 13.5, color: INK, lineSpacing: 21,
    valign: "top",
  });
  s.addText("Visos šios bibliotekos braižymo funkcijos daro tą patį: "
    + "apskaičiuoja taškus ir prideda sienas.", {
    x: M, y: 4.45, w: W - 2 * M, h: 0.6, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 16, color: INK,
  });
  code(s, [
    "import add",
    "",
    "add.box([0, 0, 0], 2, \"red\")",
    "add.save(\"kubas.off\")",
  ], { x: M, y: 5.15, w: 4.1, h: 1.35, fontSize: 13 });
  s.addText("Tas pats kubas – keturios eilutės.", {
    x: 5.0, y: 5.6, w: 4.4, h: 0.5, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 14, italic: true, color: MUTED,
  });
}

// =========================================================== 6. winding
{
  const s = sheet("Vidinė ir išorinė siena", "pagrindai");
  bullets(s, [
    "Žvelgiant į modelį iš išorės, viršūnių indeksus reikia išdėstyti "
      + "prieš laikrodžio rodyklę.",
    "Žvelgiant iš vidaus – pagal laikrodžio rodyklę.",
    "Apversta siena atvaizduojama juoda arba visai nerodoma.",
    "Bibliotekos figūros orientuojamos pačios – galvoti apie tai reikia "
      + "tik rašant add.polygon(...) ranka.",
    { text: "add.fix_normals(M) sutvarko visą modelį; add.check() pasako, "
      + "ar paviršius uždaras.", options: { bold: true } },
  ], { w: 5.2, fontSize: 15.5 });
  picture(s, "two_sided.png", {
    x: 5.95, y: 1.62, w: 3.43, h: 2.42,
    caption: "Tas pats balnas: lakštas, dvipusis ir tūrinis",
  });
}

// =========================================================== 7. scene
{
  const s = sheet("Scena, sluoksniai ir modeliai", "pagrindinė idėja");
  code(s, [
    "add.box([0, 0, 0], 1, \"red\")",
    "plyta = add.layer()     # scena vėl tuščia",
    "",
    "for i in range(10):",
    "    add.mesh(add.move(plyta, [i * 1.2, 0, 0]))",
    "",
    "add.save(\"siena.off\")",
  ], { x: M, y: 1.62, w: 5.25, h: 2.3, fontSize: 12.5 });
  cards(s, [
    ["layer()", "Paima sceną kaip modelį ir palieka sceną tuščią."],
    ["mesh(M)", "Grąžina modelį atgal į sceną."],
    ["merge([...])", "Sujungia kelis modelius į vieną."],
    ["push() / pop()", "Funkcijoje, kurianti atskirą detalę: padeda sceną "
      + "į šalį ir po to grąžina."],
  ], { y: 4.15, h: 1.24, perRow: 2 });
  s.addText("Sukurk vieną kartą – padėk daug kartų.", {
    x: 6.1, y: 2.05, w: 3.3, h: 1.0, isTextBox: true, margin: 0,
    fontFace: TITLE_FONT, fontSize: 21, bold: true, color: BROWN,
    valign: "top",
  });
  s.addText("Transformacijos niekada nekeičia joms perduoto modelio – "
    + "jos grąžina naują.", {
    x: 6.1, y: 3.0, w: 3.3, h: 0.9, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 13, color: MUTED, valign: "top",
  });
}

// =========================================================== 8. first model
{
  const s = sheet("Pirmasis modelis", "pradžia");
  code(s, [
    "import add",
    "",
    "add.box([0, 0, 0], 2, \"red\")",
    "add.sphere([3, 0, 0], 1, 20, \"blue\")",
    "add.cylinder([0, 2, 0], [3, 2, 0],",
    "             0.3, 24, \"gold\")",
    "",
    "add.check()",
    "add.save(\"pirmas.off\")",
  ], { x: M, y: 1.62, w: 4.5, h: 2.85, fontSize: 13 });
  picture(s, "first_model.png", { x: 5.4, y: 1.62, w: 3.98, h: 2.85 });
  code(s, [
    "  vertices            2460",
    "!! polygons            2478  (need 10000)",
    "OK colours             3     (need 3)",
    "OK closed surface      yes",
  ], { x: M, y: 4.85, w: 8.76, h: 1.35, fontSize: 12 });
  s.addText("check() ataskaita: dar trūksta daugiakampių.", {
    x: M, y: 6.3, w: 8.76, h: 0.4, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 13, italic: true, color: MUTED,
  });
}

// =========================================================== 9. primitives
{
  const s = sheet("Paruoštos figūros", "funkcijos");
  picture(s, "primitives.png", { x: M, y: 1.55, w: 5.15, h: 3.6 });
  s.addText([
    { text: "Kūnai\n", options: { bold: true, color: BROWN,
      breakLine: true } },
    { text: "box, cuboid, frame, pyramid, prism, polyhedron, voxels\n",
      options: { fontFace: MONO, fontSize: 11.5, breakLine: true } },
    { text: "\nApvalūs\n", options: { bold: true, color: BROWN,
      breakLine: true } },
    { text: "sphere, uvsphere, ellipsoid, torus, capsule, cylinder, tube, "
      + "cup, cone, cone_open, frustum, pipe\n",
      options: { fontFace: MONO, fontSize: 11.5, breakLine: true } },
    { text: "\nPlokšti\n", options: { bold: true, color: BROWN,
      breakLine: true } },
    { text: "polygon, triangle, quad, disc, ring, grid\n",
      options: { fontFace: MONO, fontSize: 11.5, breakLine: true } },
    { text: "\nPagalbiniai\n", options: { bold: true, color: BROWN,
      breakLine: true } },
    { text: "arrow, helix, axes, glyph",
      options: { fontFace: MONO, fontSize: 11.5 } },
  ], {
    x: 6.0, y: 1.6, w: 3.4, h: 4.6, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 13, color: INK, lineSpacing: 16,
    valign: "top",
  });
  note(s, "examples/02_primitives.py – visos figūros vienoje programoje.");
}

// =========================================================== 10. parametric
{
  const s = sheet("parametric() – pagrindinė funkcija", "paviršiai");
  code(s, [
    "def toras(u, v):",
    "    return [(5 + math.cos(u)) * math.cos(v),",
    "            math.sin(u),",
    "            (5 + math.cos(u)) * math.sin(v)]",
    "",
    "add.parametric(toras, 0, 2*math.pi, 40,",
    "                      0, 2*math.pi, 80,",
    "               \"gold\", wrap_u=True, wrap_v=True)",
  ], { x: M, y: 1.6, w: 5.3, h: 2.4, fontSize: 12 });
  picture(s, "surfaces_classic.png", { x: 6.05, y: 1.6, w: 3.33, h: 2.4 });
  cards(s, [
    ["wrap_u, wrap_v", "Uždaro paviršių be siūlės ir be pasikartojančių "
      + "viršūnių."],
    ["thickness=", "Suteikia lakštui tikrą storį – gaunamas uždaras kūnas."],
    ["double_sided=", "Pigesnis variantas: kiekviena siena ir jos "
      + "apversta kopija."],
  ], { y: 4.25, h: 1.35, perRow: 3 });
}

// =========================================================== 11-13. surfaces
{
  const s = sheet("Parametriniai paviršiai: viena lygtis, dvylika formų",
    "pavyzdžiai");
  picture(s, "supershapes.png", { x: M, y: 1.55, w: 5.3, h: 3.75 });
  s.addText([
    { text: "Gielio superformulė (2003)\n",
      options: { bold: true, color: BROWN, breakLine: true } },
    { text: "r(t) = ( |cos(m·t/4)/a|^n₂ + |sin(m·t/4)/b|^n₃ ) ^ (−1/n₁)\n\n",
      options: { fontFace: MONO, fontSize: 11, breakLine: true } },
    { text: "Šeši skaičiai – ir gaunama jūrų žvaigždė, gėlė, kristalas "
      + "arba paprasčiausias rutulys.\n\n", options: { breakLine: true } },
    { text: "Būtent to ir prašo užduotis: vienas parametras, keičiantis "
      + "formą.", options: { italic: true, color: MUTED } },
  ], {
    x: 6.15, y: 1.65, w: 3.25, h: 3.6, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 13, color: INK, lineSpacing: 17,
    valign: "top",
  });
  note(s, "examples/08_surfaces_superformula.py");
}

{
  const s = sheet("Paviršiai, kurie panašūs į daiktus", "pavyzdžiai");
  picture(s, "surfaces_nature.png", { x: M, y: 1.55, w: 8.76, h: 4.1 });
  note(s, "Kriauklė, sraigė, Dini paviršius, obuolys, citrina, širdis, "
    + "ragas, trimitas, banguota kolona, „breather“, raibuliai, lašas. "
    + "examples/09_surfaces_nature.py");
}

{
  const s = sheet("Grafikai ir egzotiški paviršiai", "pavyzdžiai");
  picture(s, "height_fields.png", { x: M, y: 1.6, w: 4.3, h: 3.0,
    caption: "y = f(x, z)  ·  10_height_fields.py" });
  picture(s, "surfaces_exotic.png", { x: 5.1, y: 1.6, w: 4.28, h: 3.0,
    caption: "Miobijus, Kleinas, Boy, Romos paviršius  ·  07_surfaces_exotic.py" });
  s.addText("Vienpusiai paviršiai neturi „išorės“. Duokite jiems storį – "
    + "ir jie tampa įprastais dvipusiais kūnais.", {
    x: M, y: 5.5, w: W - 2 * M, h: 0.7, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 15, color: INK,
  });
}

// =========================================================== 14. two-sided
{
  const s = sheet("Kai paviršius iš vienos pusės juodas", "nauja");
  picture(s, "two_sided.png", { x: M, y: 1.55, w: 8.76, h: 3.2 });
  cards(s, [
    ["Paprastas lakštas", "Viena gera pusė, viena „negyva“."],
    ["double_sided=True", "Kiekviena siena ir jos apversta kopija. "
      + "Pigu, storio vis dar nėra."],
    ["thickness=0.1", "Tikras kūnas su sienele: uždaras, spausdinamas, "
      + "teisingas iš visų pusių."],
  ], { y: 5.0, h: 1.35, perRow: 3 });
}

// =========================================================== 15. revolve
{
  const s = sheet("revolve() – sukinys", "paviršiai");
  code(s, [
    "def vaza(t):",
    "    return [1 + 0.4*math.sin(3*t), t]",
    "",
    "add.revolve(vaza, [0, 0, 0], [0, 1, 0],",
    "            0, 4, 60, 40, \"teal\")",
  ], { x: M, y: 1.6, w: 4.4, h: 1.85, fontSize: 12.5 });
  s.addText([
    { text: "profilis(t)", options: { fontFace: MONO, bold: true } },
    { text: " grąžina [spindulys, aukštis]", options: { breakLine: true } },
    { text: "\ncaps=True uždaro galus – gaunamas kūnas, tinkamas loginėms "
      + "operacijoms", options: { breakLine: true } },
    { text: "\nangle= mažesnis už pilną apsisukimą išpjauna pleištą",
      options: {} },
  ], {
    x: M, y: 3.6, w: 4.4, h: 1.5, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 13, color: INK, lineSpacing: 17,
    valign: "top",
  });
  picture(s, "lathe.png", { x: 5.25, y: 1.6, w: 4.13, h: 3.5 });
  note(s, "Senasis spin3D(A, B, S, ...) tebeveikia – tai tas pats sukinys "
    + "be dangtelių. examples/14_lathe_gallery.py");
}

// =========================================================== 16. sweeps
{
  const s = sheet("Kopijuojamas, sukamas, tempiamas paviršius", "paviršiai");
  code(s, [
    "add.extrude(zvaigzde, [0, 3.4, 0], \"gold\",",
    "            steps=90, twist=1.6*math.pi,",
    "            scale=lambda t: 1 - 0.45*t)",
  ], { x: M, y: 1.58, w: 5.3, h: 1.1, fontSize: 12 });
  picture(s, "sweeps.png", { x: 6.05, y: 1.58, w: 3.33, h: 2.4 });
  s.addText("twist ir scale gali būti ir funkcijos nuo padėties kelyje – "
    + "forma keičiasi eidama. Dvylika pavyzdžių: "
    + "examples/13_sweep_and_twist.py", {
    x: M, y: 2.85, w: 5.3, h: 0.85, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 13.5, color: MUTED, valign: "top",
  });
  cards(s, [
    ["extrude", "2D forma ištempiama į 3D; pakeliui sukama ir siaurinama."],
    ["sweep", "Skerspjūvis stumiamas išilgai bet kokio 3D kelio."],
    ["loft", "Paviršius, uždengiantis skerspjūvių seką."],
    ["ribbon", "Plokščia juosta, einanti 3D keliu."],
  ], { y: 4.05, h: 1.12, perRow: 2 });
}

// =========================================================== 17. curves
{
  const s = sheet("curve() – kreivės kaip vamzdžiai", "paviršiai");
  picture(s, "curves.png", { x: M, y: 1.55, w: 5.3, h: 3.75 });
  code(s, [
    "def mazgas(t):",
    "    return [math.sin(t) + 2*math.sin(2*t),",
    "            -math.sin(3*t),",
    "            math.cos(t) - 2*math.cos(2*t)]",
    "",
    "add.curve(mazgas, 0, 2*math.pi, 300,",
    "          18, 0.28, \"lime\", True)",
  ], { x: 6.05, y: 1.6, w: 3.33, h: 2.3, fontSize: 10.5 });
  s.addText("Spindulys gali būti ir funkcija r(t) – vamzdis storėja ir "
    + "plonėja. Vamzdis pats nesisuka: išilgai kreivės nešamas "
    + "minimaliai sukantis rėmas.", {
    x: 6.05, y: 4.05, w: 3.33, h: 1.3, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 12.5, color: MUTED, valign: "top",
  });
}

// =========================================================== 18. transforms
{
  const s = sheet("Transformacijos", "sluoksniai");
  cards(s, [
    ["move, place", "Pastūmimas; place pastato centrą į nurodytą tašką."],
    ["rotateX/Y/Z, rotate", "Sukimas apie ašį – taip pat ir apie bet "
      + "kokią kryptį."],
    ["zoom, stretch, fit", "Mastelis: vienodas, atskiras kiekvienai ašiai "
      + "arba pagal dydį."],
    ["mirror", "Atspindys plokštumoje; sienų kryptis apsukama."],
    ["twist, bend, taper", "Susukimas, sulenkimas, siaurėjimas."],
    ["deform", "Bet kokia jūsų funkcija f(p) → naujas taškas."],
  ], { h: 1.14 });
  s.addText("Visos jos grąžina naują modelį – originalas nepakinta, "
    + "todėl jas galima jungti į grandinę:", {
    x: M, y: 5.75, w: W - 2 * M, h: 0.4, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 14, color: INK,
  });
  code(s, [
    "M = add.move(add.rotateY(add.zoom(M, 0.5), 0.4), [0, 3, 0])",
  ], { x: M, y: 6.2, w: W - 2 * M, h: 0.52, fontSize: 12 });
}

// =========================================================== 19. patterns
{
  const s = sheet("Viena detalė, daug kopijų", "sluoksniai");
  picture(s, "patterns.png", { x: M, y: 1.55, w: 5.3, h: 3.75 });
  s.addText([
    { text: "array_linear(M, step, n)\n",
      options: { fontFace: MONO, fontSize: 12, breakLine: true } },
    { text: "array_grid(M, steps, counts)\n",
      options: { fontFace: MONO, fontSize: 12, breakLine: true } },
    { text: "array_radial(M, n, axis, P)\n",
      options: { fontFace: MONO, fontSize: 12, breakLine: true } },
    { text: "array_mirror(M, point, normal)\n\n",
      options: { fontFace: MONO, fontSize: 12, breakLine: true } },
    { text: "repeat(M, n, step)\n",
      options: { fontFace: MONO, fontSize: 12, bold: true, color: BROWN,
        breakLine: true } },
    { text: "Bendriausias variantas: jūs pasakote, kur atsiduria "
      + "kopija numeris i.", options: {} },
  ], {
    x: 6.05, y: 1.65, w: 3.33, h: 2.6, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 13, color: INK, lineSpacing: 18,
    valign: "top",
  });
  code(s, [
    "spirale = add.repeat(plyta, 40,",
    "    lambda M, i: add.move(",
    "        add.rotateY(M, i * 0.3),",
    "        [0, i * 0.2, 0]))",
  ], { x: 6.05, y: 4.3, w: 3.33, h: 1.35, fontSize: 10.5 });
}

// =========================================================== 20. colours
{
  const s = sheet("Spalvos", "sluoksniai");
  code(s, [
    "add.box(c, 1, \"red\")            # vardu",
    "add.box(c, 1, \"#ff8800\")        # hex",
    "add.box(c, 1, [255, 136, 0])    # RGB",
    "",
    "add.hsv(0.3, 0.7, 1.0)          # atspalvis",
    "add.gradient(t, \"navy\", \"gold\") # perėjimas",
    "",
    "M = add.color_by(M,",
    "        lambda p: add.hsv(p[1] / 10.0))",
  ], { x: M, y: 1.6, w: 5.0, h: 2.9, fontSize: 12 });
  cards(s, [
    ["color(M, spalva)", "Perdažo visą modelį."],
    ["color_by(M, fn)", "Spalva pagal sienos padėtį – vaivorykštės, "
      + "aukščio žemėlapiai."],
    ["color_gradient", "Perėjimas nuo vienos spalvos iki kitos išilgai "
      + "ašies."],
    ["color_random", "Kiekvienai sienai – sava atsitiktinė spalva."],
  ], { y: 4.6, h: 1.1, perRow: 2 });
  s.addText("Užduočiai reikia bent trijų spalvų – bet gražiau, kai jos "
    + "ką nors reiškia.", {
    x: 5.8, y: 1.85, w: 3.6, h: 1.5, isTextBox: true, margin: 0,
    fontFace: TITLE_FONT, fontSize: 17, color: BROWN, valign: "top",
  });
}

// =========================================================== 21. booleans
{
  const s = sheet("Loginės operacijos su kūnais", "nauja");
  picture(s, "booleans.png", { x: M, y: 1.55, w: 5.3, h: 3.6 });
  s.addText([
    { text: "union(A, B)\n", options: { fontFace: MONO, fontSize: 12.5,
      bold: true, color: BROWN, breakLine: true } },
    { text: "Sąjunga: viskas, kas yra bet kuriame kūne. Paslėptos vidinės "
      + "sienos dingsta.\n", options: { breakLine: true } },
    { text: "\nintersect(A, B)\n", options: { fontFace: MONO,
      fontSize: 12.5, bold: true, color: BROWN, breakLine: true } },
    { text: "Sankirta: tik tai, kas bendra.\n",
      options: { breakLine: true } },
    { text: "\ndifference(A, B)\n", options: { fontFace: MONO,
      fontSize: 12.5, bold: true, color: BROWN, breakLine: true } },
    { text: "Skirtumas: A su iškirptu B. Taip daromos skylės ir įpjovos.\n",
      options: { breakLine: true } },
    { text: "\ncut(M, taškas, normalė)\n", options: { fontFace: MONO,
      fontSize: 12.5, bold: true, color: BROWN, breakLine: true } },
    { text: "Pjūvis plokštuma – pigiau.", options: {} },
  ], {
    x: 6.05, y: 1.55, w: 3.33, h: 3.7, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 11, color: INK, lineSpacing: 13,
    valign: "top",
  });
  code(s, [
    "add.cuboid([0,0,0], [4,1,4], \"brown\")",
    "plokste = add.layer()",
    "add.cylinder([0,-1,0], [0,1,0], 0.6, 32, \"black\")",
    "grezlas = add.layer()",
    "add.mesh(add.difference(plokste, grezlas))",
  ], { x: M, y: 5.45, w: 8.76, h: 1.4, fontSize: 11.5 });
}

// =========================================================== 22. how csg
{
  const s = sheet("Kaip veikia loginės operacijos", "nauja");
  cards(s, [
    ["1. Perpjaunama",
      "Kiekviena siena perpjaunama ten, kur ją galėtų kirsti kito kūno "
      + "trikampiai. Kaimynai randami per erdvinį tinklelį, todėl toli "
      + "esanti siena nepjaustoma."],
    ["2. Klausiama",
      "Kiekvienos dalies klausiama: ar ji viduje, išorėje, ar guli ant "
      + "kito kūno paviršiaus? Atsako spindulys, skaičiuojantis "
      + "susikirtimus."],
    ["3. Atrenkama",
      "Sąjunga palieka tai, kas išorėje; sankirta – kas viduje; "
      + "skirtumas – A išorę ir apverstą B vidų."],
  ], { y: 1.6, h: 1.95, perRow: 3 });
  s.addText([
    { text: "Apie 600 eilučių gryno Python. Jokių bibliotekų.\n\n",
      options: { bold: true, breakLine: true } },
    { text: "6000 sienų sfera minus dėžė – apie 0,5 s.  ", options: {} },
    { text: "25 000 sienų – apie 2 s.\n", options: { breakLine: true } },
    { text: "Rezultatas suklijuotas, plyšeliai užtaisyti, paviršius "
      + "uždaras.", options: {} },
  ], {
    x: M, y: 3.9, w: W - 2 * M, h: 1.3, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 15, color: INK, lineSpacing: 22,
    valign: "top",
  });
  s.addShape(pres.ShapeType.roundRect, {
    x: M, y: 5.25, w: W - 2 * M, h: 1.05, rectRadius: 0.05,
    fill: { color: "EAF3EF" }
  });
  s.addText("Loginėms operacijoms reikia uždarų kūnų. Jei rezultatas "
    + "keistas – pirmiausia patikrinkite abu pradinius kūnus su "
    + "add.check().", {
    x: M + 0.25, y: 5.45, w: W - 2 * M - 0.5, h: 0.7, isTextBox: true,
    margin: 0, fontFace: BODY_FONT, fontSize: 14, color: TEAL,
    valign: "top",
  });
}

// =========================================================== 23. clean
{
  const s = sheet("Modelio taisymas ir tikrinimas", "nauja");
  cards(s, [
    ["clean(M)", "Suklijuoja sutampančias viršūnes, pašalina nulinio "
      + "ploto ir pasikartojančias sienas, išmeta vidines sieneles ten, "
      + "kur du kūnai liečiasi."],
    ["heal(M)", "Užtaiso plyšelius ten, kur briauna praeina pro svetimą "
      + "viršūnę."],
    ["fix_normals(M)", "Nukreipia visas sienas ta pačia kryptimi, "
      + "uždarame modelyje – į išorę."],
    ["triangulate(M)", "Paverčia visas sienas trikampiais."],
  ], { y: 1.58, h: 1.24, perRow: 2 });
  code(s, [
    "modelis = add.clean(add.layer())",
    "add.mesh(modelis)",
    "add.check()",
  ], { x: M, y: 4.45, w: 4.3, h: 1.1, fontSize: 12.5 });
  code(s, [
    "  vertices            136768",
    "OK polygons            163132",
    "OK colours             6",
    "OK closed surface      yes",
    "   volume              60.286",
  ], { x: 5.15, y: 4.45, w: 4.23, h: 1.55, fontSize: 11 });
  note(s, "Sudėjus du besiliečiančius kubus, kiekvienas pasilieka savo "
    + "sienelę toje vietoje, kur jos niekas nemato. clean() jas randa ir "
    + "pašalina.");
}

// =========================================================== 24. export
{
  const s = sheet("Modelio išsaugojimas ir viešinimas", "nauja");
  code(s, [
    "add.save(\"modelis.off\")   # kurso formatas",
    "add.save(\"modelis.obj\")   # + .mtl spalvoms",
    "add.save(\"modelis.ply\")",
    "add.save(\"modelis.stl\")   # 3D spausdinimui",
  ], { x: M, y: 1.6, w: 5.0, h: 1.65, fontSize: 12.5 });
  cards(s, [
    ["Sketchfab", "Sudėkite .obj ir .mtl į vieną archyvą ir įkelkite – "
      + "modelį galės pasukioti bet kas naršyklėje."],
    ["3D spausdinimas", "clean(..., normals=True), tada save(\"m.stl\"). "
      + "Paviršius turi būti uždaras."],
    ["Peržiūra be MeshLab", "python3 tools/preview.py modelis.off "
      + "sukuria PNG. Irgi be jokių bibliotekų."],
    ["Įkėlimas atgal", "load(\"raide.off\") grąžina modelį, kurį galima "
      + "stumdyti ir dažyti."],
  ], { y: 3.45, h: 1.35, perRow: 2 });
  s.addText("MeshLab konvertavimo žingsnis nebereikalingas – add.py OBJ "
    + "ir MTL parašo pats.", {
    x: 5.8, y: 1.85, w: 3.6, h: 1.2, isTextBox: true, margin: 0,
    fontFace: TITLE_FONT, fontSize: 17, color: BROWN, valign: "top",
  });
}

// =========================================================== 25-26. examples
{
  const s = sheet("Didesni pavyzdžiai", "galerija");
  picture(s, "chess_set.png", { x: M, y: 1.55, w: 4.3, h: 2.6,
    caption: "18_chess_set.py – sukinys, sluoksniai, loginės operacijos" });
  picture(s, "fractals.png", { x: 5.1, y: 1.55, w: 4.28, h: 2.6,
    caption: "17_fractals.py – Mengerio kempinė, Sierpinskis, medis" });
  picture(s, "city.png", { x: M, y: 4.55, w: 4.3, h: 2.1 });
  picture(s, "example4.png", { x: 5.1, y: 4.55, w: 4.28, h: 2.1 });
}

// =========================================================== 27. migration
{
  const s = sheet("Nuo 1.2 prie 2.0", "suderinamumas");
  const rows = [
    ["cube2(c, e, b, RGB)", "frame", "kubo briaunų karkasas"],
    ["cylinder2(A, B, r, k, RGB)", "tube", "cilindras be dangtelių"],
    ["cylinder3(A, B, r, k, RGB)", "cup", "uždarytas iš vieno galo"],
    ["cone2(A, B, r, k, RGB)", "cone_open", "tik šoninis paviršius"],
    ["rectangle3D(c, e, RGB)", "cuboid", "stačiakampis gretasienis"],
    ["newface(A, RGB)", "polygon", "viena plokščia siena"],
    ["spin3D(A, B, S, ...)", "revolve", "sukinys"],
    ["off(failas)", "save(failas)", ".off, .obj, .ply arba .stl"],
  ];
  const tableRows = [[
    { text: "add.py 1.2", options: { bold: true, color: WHITE,
      fill: { color: BROWN }, fontSize: 12 } },
    { text: "add.py 2.0", options: { bold: true, color: WHITE,
      fill: { color: BROWN }, fontSize: 12 } },
    { text: "kas tai", options: { bold: true, color: WHITE,
      fill: { color: BROWN }, fontSize: 12 } },
  ]].concat(rows.map(r => [
    { text: r[0], options: { fontFace: MONO, fontSize: 11.5 } },
    { text: r[1], options: { fontFace: MONO, fontSize: 11.5, bold: true,
      color: BROWN } },
    { text: r[2], options: { fontSize: 11.5 } },
  ]));
  s.addTable(tableRows, {
    x: M, y: 1.6, w: W - 2 * M, colW: [3.5, 2.2, 3.06],
    border: { type: "solid", color: LINE, pt: 0.75 },
    fontFace: BODY_FONT, color: INK, valign: "middle",
    rowH: 0.34, margin: 0.06,
  });
  s.addShape(pres.ShapeType.roundRect, {
    x: M, y: 5.35, w: W - 2 * M, h: 1.15, rectRadius: 0.05,
    fill: { color: SAND }
  });
  s.addText("Visi seni vardai tebeveikia. Dvylika 1.2 versijai rašytų "
    + "modelių guli tests/legacy/ aplanke, ir testai tikrina, kad jie "
    + "duotų lygiai tiek pat sienų kaip anksčiau.", {
    x: M + 0.25, y: 5.55, w: W - 2 * M - 0.5, h: 0.8, isTextBox: true,
    margin: 0, fontFace: BODY_FONT, fontSize: 14, color: INK,
    valign: "top",
  });
}

// =========================================================== 28. where
{
  const s = pres.addSlide();
  slideNumber += 1;
  s.background = { color: DARK };
  s.addText("Kur viską rasti", {
    x: M, y: 1.15, w: W - 2 * M, h: 0.8, isTextBox: true, margin: 0,
    fontFace: TITLE_FONT, fontSize: 38, bold: true, color: WHITE,
  });
  s.addText([
    { text: "Modulis, pavyzdžiai, testai ir dokumentacija\n",
      options: { color: "E9C9AE", breakLine: true } },
    { text: "github.com/…/add.py\n\n",
      options: { fontFace: MONO, fontSize: 17, color: WHITE,
        breakLine: true } },
    { text: "Dokumentacija lietuviškai ir angliškai\n",
      options: { color: "E9C9AE", breakLine: true } },
    { text: "…github.io/add.py\n\n",
      options: { fontFace: MONO, fontSize: 17, color: WHITE,
        breakLine: true } },
    { text: "Klausimai\n", options: { color: "E9C9AE", breakLine: true } },
    { text: "akatasis@gmail.com  ·  martynas.sabaliauskas@mif.vu.lt",
      options: { fontSize: 15, color: WHITE } },
  ], {
    x: M, y: 2.25, w: 5.6, h: 3.4, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 14, lineSpacing: 22, valign: "top",
  });
  s.addImage({
    path: img("supershapes.png"), x: 6.0, y: 2.1, w: 3.4, h: 2.4,
    sizing: { type: "contain", w: 3.4, h: 2.4 },
  });
  s.addText("Ačiū už dėmesį.", {
    x: M, y: 6.1, w: W - 2 * M, h: 0.5, isTextBox: true, margin: 0,
    fontFace: TITLE_FONT, fontSize: 20, color: "C9BFB6",
  });
  s.addNotes("Studentams: pradėkite nuo examples/01_first_model.py, "
    + "paskui 02_primitives.py. Užduočiai labiausiai praverčia "
    + "06-16 pavyzdžiai.");
}

pres.writeFile({ fileName: OUT }).then(() => {
  console.log("written: " + OUT + " (" + slideNumber + " slides)");
});

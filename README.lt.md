# add.py

**3D modeliai, sukurti vien tik programiniu kodu.**

Vienas failas. Tik `math` ir `random`. Jokios modeliavimo programos, jokios
geometrijos bibliotekos, nieko diegti nereikia.

[Dokumentacija](https://martynas-sabaliauskas.github.io/add.py/) &middot;
[Galerija](https://martynas-sabaliauskas.github.io/add.py/#gallery) &middot;
[In English](README.md)

```python
import add

add.box([0, 0, 0], 2, "red")
add.sphere([3, 0, 0], 1, 20, "blue")
add.cylinder([0, 2, 0], [3, 2, 0], 0.3, 24, "gold")

add.check()                      # 2478 daugiakampiai, 3 spalvos, uždaras
add.save("pirmas_modelis.off")   # arba .obj (+ .mtl), .ply, .stl
```

<p align="center">
  <img src="docs/images/chess_set.png" width="49%" alt="Šachmatų komplektas">
  <img src="docs/images/city.png" width="49%" alt="Procedūrinis miestas">
  <img src="docs/images/supershapes.png" width="49%" alt="Dvylika superformų">
  <img src="docs/images/booleans.png" width="49%" alt="Loginės operacijos">
</p>

Nė vienas jų nenupieštas ranka. Kiekvienas – viena trumpa programa
[`examples/`](examples/) aplanke.

---

## Kam to reikia

`add.py` parašytas antro kurso universiteto kursui, kuriame studentams
skiriama sąmoningai nepatogi užduotis: **sukurti 3D modelį, bet neliesti
jokios modeliavimo programos ir neatsisiųsti jokio paruošto modelio.**
Viskas turi būti apskaičiuota jūsų pačių parašyta formule arba ciklu.

Paaiškėja, kad atimti įrankiai darbą padaro ne nuobodesnį, o įdomesnį. Sfera
nustoja būti mygtuku įrankių juostoje ir tampa trimis trigonometrijos
eilutėmis. Šachmatų figūra tampa kreive, sukama apie ašį. Miestas tampa
atsitiktinių skaičių generatoriumi ir dviem ciklais. Nustojate matyti figūras
ir pradedate matyti matematiką jų viduje.

Biblioteka tam ir yra, kad įdomioji dalis – geometrija – liktų jums, o
nuobodžioji – viršūnių indeksų sekimas ir failo rašymas – ne.

## Kaip pradėti

Diegti nieko nereikia. Atsisiųskite [`add.py`](add.py), padėkite šalia savo
programos ir parašykite `import add`. Reikia tik Python 3.

```bash
curl -O https://raw.githubusercontent.com/martynas-sabaliauskas/add.py/main/add.py
```

Arba klonuokite repozitoriją – tada gausite ir pavyzdžius, ir testus, ir
dokumentaciją.

## Kas viduje

| | |
|---|---|
| **Figūros** | kubas, gretasienis, karkasas, piramidė, prizmė, penki Platono kūnai, sfera, elipsoidas, toras, kapsulė, cilindras, vamzdis, kūgis, nupjautinis kūgis, tuščiaviduris vamzdis, skritulys, žiedas, tinklelis, rodyklė, spiralė, kubeliai |
| **Paviršiai** | `parametric(S, ...)` bet kokiai `S(u, v)` funkcijai – su siūlių uždarymu, tikru storiu ir dvipusiais lakštais |
| **Sukimas ir tempimas** | `revolve` (sukinys), `sweep` išilgai 3D kelio su mastelio ir sukimo keitimu, `extrude`, `loft`, `curve` (vamzdis išilgai kreivės), `ribbon` |
| **Transformacijos** | stūmimas, sukimas apie bet kokią ašį, mastelis, tempimas, veidrodis, `place`, `fit`, `twist`, `bend`, `taper`, `jitter` ir `deform` su bet kokia jūsų funkcija |
| **Kopijos** | `repeat` ir tiesiniai / tinklelio / žiediniai / veidrodiniai masyvai |
| **Loginės operacijos** | `union`, `intersect`, `difference`, `symmetric_difference` ir pigesnis `cut` plokštuma |
| **Taisymas** | `clean` (viršūnių klijavimas, dublikatų ir vidinių sienų šalinimas), `heal`, `fix_normals`, `triangulate` |
| **Spalvos** | vardinės spalvos, hex, HSV, perėjimai ir `color_by` – spalva pagal padėtį |
| **Failai** | rašo `.off`, `.obj` + `.mtl`, `.ply`, `.stl`; skaito `.off`, `.obj`, `.ply` |
| **Tikrinimas** | `stats()` ir `check()` – daugiakampių skaičius, spalvos, uždarumas, tūris |
| **Peržiūra** | `tools/preview.py` – atvaizdavimo įrankis, irgi be jokių priklausomybių |

130 viešų funkcijų, visos su aprašymais, viename 3500 eilučių faile, kurį
galima perskaityti.

## Loginės operacijos, parašytos nuo nulio

Vieno kūno iškirpimas iš kito yra ta vieta, kur dažniausiai tikimasi
bibliotekos. Čia tai padaryta maždaug šešiais šimtais eilučių gryno Python:

1. Kiekviena siena perpjaunama ten, kur ją galėtų kirsti kito kūno
   trikampiai; kaimynai randami per erdvinį tinklelį, o pjaustoma
   palaipsniui, todėl siena nustoja būti pjaustoma, kai tik atitolsta.
2. Kiekvienos dalies klausiama, ar ji viduje, išorėje, ar guli ant kito kūno
   paviršiaus – paleidžiant spindulį ir skaičiuojant susikirtimus.
3. Paliekamos tos dalys, kurių prašo operacija.

6000 sienų sfera minus dėžė užtrunka apie pusę sekundės, 25000 sienų – apie
dvi. Rezultatas suklijuotas, plyšeliai užtaisyti, paviršius uždaras.

```python
add.cuboid([0, 0, 0], [4, 1, 4], "brown")
plokste = add.layer()
add.cylinder([0, -1, 0], [0, 1, 0], 0.6, 32, "black")
grezlas = add.layer()
add.mesh(add.difference(plokste, grezlas))
```

## Pereinant nuo add.py 1.2

Viskas veikia kaip veikę. 1.2 versijai rašyti modeliai paleidžiami nepakeisti
ir duoda tas pačias sienas – dvylika jų guli [`tests/legacy/`](tests/legacy/)
aplanke, ir testai tikrina būtent tai. Naujame kode verta rinktis aiškesnius
vardus: `cube2` → `frame`, `cylinder2` → `tube`, `cylinder3` → `cup`,
`cone2` → `cone_open`, `spin3D` → `revolve`, `off` → `save`.

## Repozitorijos sandara

```
add.py               biblioteka – vienintelis failas, kurio jums reikia
_src/                dalys, iš kurių surenkamas add.py
build.py             sujungia _src/*.py į add.py
examples/            17 pavyzdinių programų su komentarais
  build_all.py       paleidžia visas ir sugeneruoja paveikslėlius
tools/
  preview.py         atvaizdavimo įrankis be priklausomybių
  make_docs.py       sukuria docs/index.html iš kodo aprašymų
tests/
  test_add.py        68 vienetiniai testai
  test_legacy.py     paleidžia add.py 1.2 modelius ir tikrina sienų skaičių
  legacy/            tie modeliai, nepakeisti
docs/                dokumentacijos svetainė (lietuvių ir anglų kalbomis)
paper/               mokslinis straipsnis apie sandarą ir algoritmus
outreach/            populiarinimo vaizdo įrašo scenarijus ir pranešimo planas
slides/              paskaitos skaidrės
```

Jei keičiate biblioteką, keiskite failus `_src/` aplanke ir paleiskite
`python3 build.py` – `add.py` yra generuojamas. Jis laikomas repozitorijoje
tam, kad studentui reikėtų tik vieno failo.

## Testai

```bash
python3 tests/test_add.py        # 68 vienetiniai testai
python3 tests/test_legacy.py     # add.py 1.2 modeliai
python3 examples/build_all.py    # visi pavyzdžiai ir paveikslėliai
```

Vienetiniai testai tikrina kiekvienos figūros analitinį tūrį – sferą pagal
4/3·πr³, torą pagal 2π²Rr² – ir kad kiekvienas uždaras kūnas tikrai uždaras.

## Kaip pasidalinti modeliu

`save("modelis.obj")` sukuria `.obj` ir `.mtl` failus. Abu sudėkite į vieną
archyvą ir įkelkite į [Sketchfab](https://sketchfab.com) – modelį galės
pasukioti bet kas naršyklėje. 3D spausdinimui naudokite
`save("modelis.stl")` po `clean(..., normals=True)`.

## Licencija

MIT. Žr. [LICENSE](LICENSE).

---

Martynas Sabaliauskas, Vilniaus universitetas, Matematikos ir informatikos
fakultetas, Duomenų mokslo ir skaitmeninių technologijų institutas.

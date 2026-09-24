# Kaip paskelbti add.py

Repozitorija paruošta: yra `.gitignore`, `LICENSE`, `CITATION.cff`, GitHub
Actions veiksmai testams ir dokumentacijos svetainei, ir commit'ų istorija.
Čia aprašyti trys žingsniai, kuriuos gali atlikti tik GitHub paskyros
savininkas, ir su jais susijęs pavadinimo klausimas.
[In English](PUBLISHING.md).

## 1. Pavadinimas

Modulis visada buvo `add.py` ir toks lieka: studentas atsisiunčia vieną
failą ir rašo `import add`. Failui diske niekieno leidimo nereikia, o „add“
yra paprastas anglų kalbos žodis, kuris niekam nepriklauso, todėl jokios
prekių ženklo ar licencijos problemos jį pasilikti nėra.

Tačiau **repozitorija** ir **paketas** vadinasi `add3d`:

* PyPI kataloge vardas `add` jau užregistruotas – tai tuščias kito žmogaus
  įrašas (versija 1.0, jokių failų, aprašymo ar licencijos). Po juo nieko
  paskelbti negalima, o GitHub projektas vardu `add` siųstų žmones ieškoti
  `pip install add`, kuris nieko neįdiegia. (PyPI vardų perėmimo procedūra,
  PEP 541, leidžia atsiimti apleistą vardą, bet tai trunka mėnesius ir nėra
  garantuota.)
* `add3d` laisvas ir PyPI, ir GitHub, lengvai ištariamas ir vis dar
  skaitosi kaip „add, 3D“.

Taigi: `pip install add3d` duoda `import add`; dokumentacija gyvena adresu
`…/add3d/`; failas – `add.py`. README, straipsnis ir skaidrės šią vardų porą
jau naudoja.

## 2. Repozitorijos įkėlimas į GitHub

**Variantas A – atkurti iš `.bundle` failo (su visa istorija).** Šalia šio
aplanko yra `add3d-2.0-git-history.bundle` – visa git istorija viename
faile:

```bash
git clone add3d-2.0-git-history.bundle add3d
cd add3d
git remote remove origin
```

Tada GitHub svetainėje susikurkite **tuščią** repozitoriją vardu `add3d`
(be README, be licencijos – kitaip pirmasis `push` susidurs su konfliktu)
ir:

```bash
git remote add origin https://github.com/JUSU_VARDAS/add3d.git
git push -u origin main
```

**Variantas B – pradėti istoriją iš naujo.** Jei istorija nesvarbi, užtenka
šio aplanko:

```bash
cd add3d
git init -b main
git add .
git commit -m "add.py 2.0"
git remote add origin https://github.com/JUSU_VARDAS/add3d.git
git push -u origin main
```

## 3. Po pirmojo įkėlimo

**Įjunkite GitHub Pages.** *Settings → Pages → Source*: pasirinkite **GitHub
Actions**. Veiksmas `.github/workflows/pages.yml` sukuria `docs/index.html`
iš kodo aprašymų ir paskelbia adresu `https://JUSU_VARDAS.github.io/add3d/`.

**Nuorodos.** Failuose nurodyta `github.com/akatasis/add3d` ir
`akatasis.github.io/add3d`. Jei kopiją skelbiate kita paskyra, pakeiskite
vardą vienu ypu:

```bash
grep -rl "akatasis" . | xargs sed -i "s/akatasis/JUSU_VARDAS/g"
python3 tools/make_docs.py
```

**Pasitikrinkite skirtuką Actions.** Testai paleidžiami su Python 3.8–3.13;
antras darbas tikrina, ar `add.py` ir `examples/add.py` sutampa su `_src/`,
ar veikia visi pavyzdžiai ir telpa į Sketchfab ribas, ar kiekviena vieša
funkcija panaudota bent viename pavyzdyje (`tools/coverage.py --strict`), ar
veikia kiekvienas dokumentacijos pavyzdys (`tests/test_docs.py`) ir ar
`docs/index.html` atitinka kodo aprašymus. Ką nors pakeitę `_src/` aplanke,
prieš commit'ą paleiskite `python3 build.py` ir `python3 tools/make_docs.py`;
naujai viešai funkcijai dar reikia lietuviško paaiškinimo ir pavyzdžio faile
`docs/reference.py`, kitaip dokumentacija nesigeneruoja.

**Aprašymas ir raktažodžiai.** Siūlomas aprašymas:

> Build 3D models with nothing but Python code. One file, no dependencies,
> mesh booleans from scratch.

Raktažodžiai (*topics*): `3d`, `python`, `geometry`, `csg`,
`computational-geometry`, `education`, `parametric-surfaces`,
`mesh-processing`, `teaching`, `no-dependencies`.

## 4. Išleidimas PyPI kataloge (neprivaloma)

Vieno failo atsisiuntimas lieka pagrindinis būdas, bet paketas leidžia
`pip install add3d`. `pyproject.toml` jau turi visus metaduomenis; leidimas:

```bash
python3 -m pip install --upgrade build twine
python3 build.py && python3 tests/test_add.py
python3 -m build                      # -> dist/add3d-2.0.tar.gz ir .whl
python3 -m twine upload dist/*        # reikia PyPI paskyros ir API rakto
```

Jei abejojate, pirmiausia išbandykite `test.pypi.org`
(`twine upload --repository testpypi dist/*`). Versijos numeris įrašytas
`_src/00_core.py` (`__version__`), `pyproject.toml`, `CITATION.cff` ir
`docs/content.py`.

## 5. Dalijimasis ne tik GitHub

* **Sketchfab**: `add.save("modelis.obj")` sukuria `.obj` + `.mtl` (su
  permatomumu ir tekstūromis); įkelkite abu, kartu su tekstūrų paveikslėliais,
  viename archyve. Neviršykite 50 MB ir 50 spalvų (`add.check()` pasako;
  `add.save("modelis.obj", colors=50)` sumažina spalvingą modelį). Į
  atmintį netelpantis modelis rašomas dalimis su `add.stream("modelis.obj")`
  (taip rašoma 46 pavyzdžio pilis: 400 MB `.off` ir `.obj`, kuris
  suglaudintas 7-Zip telpa į 100 MB). `save` ir `stream` modelį pakeliui
  sutvarko, todėl peržiūroje niekas nemirga.
* **Straipsnis**: `paper/paper.md` (+ `references.bib`) parašytas
  informatikos didaktikos leidiniui; repozitorijos nuorodą ir DOI (jei
  leidimą archyvuosite Zenodo) įrašykite ir į `CITATION.cff`.
* **Pranešimai ir vaizdo įrašas**: `outreach/` – scenarijus ir planas;
  `slides/` – paskaitos skaidrės anglų ir lietuvių kalbomis.

## Kas kur

| Aplankas | Kas viduje |
|---|---|
| `add.py` | pati biblioteka – vienintelis failas, kurio reikia studentams |
| `_src/` + `build.py` | dalys, iš kurių surenkamas `add.py` |
| `examples/` | 43 pavyzdinės programos su komentarais ir `add.py` kopija |
| `tests/` | 94 vienetiniai testai, add.py 1.2 suderinamumo testas ir dokumentacijos pavyzdžių paleidiklis |
| `tools/` | `preview.py` (peržiūra), `make_docs.py`, `coverage.py` |
| `docs/` | dokumentacijos svetainė (EN/LT) ir paveikslėliai |
| `slides/` | paskaitos skaidrės (.pptx, .pdf ir generatorius) |
| `paper/` | straipsnis (Markdown + BibTeX) |
| `outreach/` | vaizdo įrašo scenarijus (EN/LT) ir pranešimo planas |

## Greitas patikrinimas prieš keliant

```bash
python3 build.py --check          # add.py ir examples/add.py atnaujinti
python3 tests/test_add.py         # 93 passed, 0 failed
python3 tests/test_legacy.py      # all legacy models reproduce
python3 tests/test_docs.py        # 235 documentation examples ran
python3 tools/coverage.py --strict
python3 tools/make_docs.py        # docs/index.html
python3 examples/build_all.py --models   # visi pavyzdžiai telpa į Sketchfab ribas
```

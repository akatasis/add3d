# Kaip įkelti šį projektą į GitHub

Repozitorija jau paruošta: yra `.gitignore`, `LICENSE`, `CITATION.cff`,
GitHub Actions veiksmai testams ir dokumentacijai, ir devynių žingsnių
commit'ų istorija. Belieka ją perkelti į GitHub.

## Variantas A – atkurti iš `.bundle` failo (su visa istorija)

Šalia šio aplanko yra `add.py-2.0-git-history.bundle`. Jame – visa git
istorija viename faile.

```bash
git clone add.py-2.0-git-history.bundle add.py
cd add.py
git remote remove origin
```

Tada GitHub svetainėje susikurkite **tuščią** repozitoriją (be README, be
licencijos – kitaip susidursite su konfliktu) ir:

```bash
git remote add origin https://github.com/JUSU_VARDAS/add.py.git
git push -u origin main
```

## Variantas B – pradėti istoriją iš naujo

Jei istorija nesvarbi, užtenka šio aplanko:

```bash
cd "add.py 2.0"
git init -b main
git add .
git commit -m "add.py 2.0"
git remote add origin https://github.com/JUSU_VARDAS/add.py.git
git push -u origin main
```

## Po įkėlimo

**1. Įjunkite GitHub Pages.** Repozitorijos *Settings → Pages → Source*
pasirinkite **GitHub Actions**. Veiksmas `.github/workflows/pages.yml` pats
paskelbs dokumentaciją adresu
`https://JUSU_VARDAS.github.io/add.py/`.

**2. Pataisykite nuorodas.** Failuose `README.md` ir `README.lt.md` yra
laikinas adresas `martynas-sabaliauskas`. Pakeiskite jį savo GitHub vardu
(taip pat ir `docs/content.py` nuorodose, jei jas naudosite):

```bash
grep -rl "martynas-sabaliauskas" . | xargs sed -i "s/martynas-sabaliauskas/JUSU_VARDAS/g"
```

**3. Pasitikrinkite, kad veiksmai praeina.** Skirtukas *Actions*: testai
paleidžiami su Python 3.8–3.13 ir papildomai tikrina, ar `add.py` sutampa su
`_src/` turiniu, o `docs/index.html` – su kodo aprašymais. Jei ką nors
keisite `_src/` aplanke, nepamirškite paleisti `python3 build.py`.

**4. Repozitorijos aprašymas ir raktažodžiai.** Siūlomas aprašymas:

> Build 3D models with nothing but Python code. One file, no dependencies,
> mesh booleans from scratch.

Raktažodžiai (*topics*): `3d`, `python`, `geometry`, `csg`,
`computational-geometry`, `education`, `parametric-surfaces`,
`mesh-processing`, `teaching`, `no-dependencies`.

**5. Nuoroda straipsnyje ir skaidrėse.** Kai adresas bus galutinis, jį verta
įrašyti į `paper/paper.md`, `CITATION.cff` ir paskutinę skaidrę
(`slides/make_slides.js`, ieškokite `github.com/…/add.py`).

## Kas kur

| Aplankas | Kas viduje |
|---|---|
| `add.py` | pati biblioteka – vienintelis failas, kurio reikia studentams |
| `_src/` + `build.py` | dalys, iš kurių surenkamas `add.py` |
| `examples/` | 18 pavyzdinių programų su komentarais |
| `tests/` | 68 vienetiniai testai + 12 senų modelių suderinamumo testas |
| `tools/` | `preview.py` (peržiūra be jokių bibliotekų), `make_docs.py` |
| `docs/` | dokumentacijos svetainė (LT/EN) ir paveikslėliai |
| `slides/` | atnaujintos paskaitos skaidrės (.pptx, .pdf ir generatorius) |
| `paper/` | mokslinis straipsnis (Markdown + BibTeX) |
| `outreach/` | populiarinimo vaizdo įrašo scenarijus (LT/EN) ir pranešimo planas |

## Greitas patikrinimas prieš keliant

```bash
python3 tests/test_add.py         # 68 passed, 0 failed
python3 tests/test_legacy.py      # all legacy models reproduce
python3 build.py                  # add.py surenkamas iš _src/
python3 tools/make_docs.py        # docs/index.html
```

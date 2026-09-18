# Nobody drew any of this

**A 20-minute popular talk about `add.py` — 3D models built from formulas, for a science festival, a teachers' conference or a school visit.**

Slide titles are given in English with the Lithuanian title in brackets, so the same deck works for either language.

- 18 slides, 20 minutes, roughly 65 seconds each
- Six of them are live demos. Everything else is a single picture and a sentence.
- Assumed audience: bright, curious, has never written a line of graphics code. Some of them are fourteen.

---

## Before you start

Have this ready and tested on the machine you will actually present from:

- A terminal and an editor side by side, font at 24 pt or larger.
- `add.py` and the `examples/` folder in one directory. Nothing installed.
- `examples/out/` already populated, so nothing slow has to run on stage.
- `docs/images/` open in a picture viewer as a fallback, in case a demo fails.
- Four files pre-written but not yet run: `demo1_triangle.py`, `demo2_sphere.py`, `demo3_city.py`, `demo4_gear.py`. You will type the last two or three lines of each live and run it. Typing a whole file on stage is a bad use of everyone's time; typing the last line is theatre worth having.

If a demo fails, do not debug it. Switch to the picture and carry on. The talk survives losing every demo; it does not survive four minutes of you squinting at a traceback.

---

## The talk

### 1. Nobody drew any of this [Niekas viso to nepiešė]
**Must land:** Everything you are about to see was computed, not drawn.
**On screen:** `docs/images/chess_set.png`, full bleed, no text but the title.
**Timing:** 0:00–0:30
Say the title, let the picture sit for three seconds before you say anything else. Do not explain yet.

### 2. Three things that were never drawn [Trys dalykai, kurių niekas nepiešė]
**Must land:** A chess set, a city and a fractal all came out of short text files.
**On screen:** Three pictures in a row — `chess_set.png`, `city.png`, `fractals.png`. Under each, the size of the file that made it: 6.1 KB, 4.4 KB, 5.8 KB.
**Timing:** 0:30–1:30
The numbers under the pictures are the argument. Point at them, do not read them out.

### 3. The rule [Taisyklė]
**Must land:** The assignment forbids modelling programs and downloaded meshes — everything must come from a formula or a loop you wrote.
**On screen:** Plain text slide: *Make a 3D model. No modelling program. No downloaded meshes. At least 10 000 polygons. At least 3 colours. Use a loop. One number must change the shape.*
**Timing:** 1:30–2:30
This is the spine of the talk. Read it out slowly, all of it.

### 4. Why take the tools away [Kodėl atimti įrankius]
**Must land:** When you cannot drag a corner with the mouse, you have to say where the corner is — and that is the whole lesson.
**On screen:** Split slide. Left: a crowded professional modelling interface, greyed out. Right: eight lines of Python.
**Timing:** 2:30–3:30
The honest version: this rule exists so that nobody can hand in something they downloaded. But it turns out to teach more than the unrestricted version ever did. Say both halves.

### 5. What a 3D model actually is [Kas iš tikrųjų yra trimatis modelis]
**Must land:** A 3D model is a list of points and a list of which points to join — nothing else is hiding in the file.
**On screen:** **LIVE DEMO.** `demo1_triangle.py`. Type `add.triangle([0,0,0], [1,0,0], [0,1,0], "red")` and `add.save("t.off")`, run it, then open `t.off` in the editor. Six lines. Then change it to `add.box([0,0,0], 1, "red")`, run, open `cube.off`, and walk through the header `8 6 0`, the eight coordinates, the six faces.
**Timing:** 3:30–5:15
The single most important ninety seconds in the talk. Go slowly. Let somebody in the third row read the file out loud if they want to.

### 6. And a function that marks your homework [Ir funkcija, kuri tikrina namų darbus]
**Must land:** `check()` reads the model back and tells you how far you are from the ten thousand.
**On screen:** **LIVE DEMO.** Run `examples/01_first_model.py`. The output shows 2478 polygons, three colours, closed surface yes, and a red mark next to the polygon count.
**Timing:** 5:15–6:00
Worth saying out loud: it also tells you whether your surface is closed, which matters later for cutting holes in things.

### 7. A sphere is three lines [Sfera – trys eilutės]
**Must land:** Two angles pick out one point on a ball, and sine and cosine do the picking.
**On screen:** **LIVE DEMO.** `demo2_sphere.py`. The function is already written; type the `add.parametric(...)` call and run it. Beside it, draw the two angles on a whiteboard or a sheet of paper: a circle, a line round the equator, a line up to the pole, a dot where they meet.
**Timing:** 6:00–7:30
The paper drawing matters more than the code. Do it first, then show the code and say: that is the same thing, written down.

### 8. One number [Vienas skaičius]
**Must land:** Push the circle away from the axis before you spin it, and the same three lines give a ball, an apple or a doughnut.
**On screen:** **LIVE DEMO.** Edit two characters — `(R + math.cos(v))` — and run with R = 0, R = 0.4, R = 2. Three renders on screen together.
**Timing:** 7:30–8:30
This is the assignment's "one number must change the shape" rule, satisfied in front of them. Say so.

### 9. One equation, twelve creatures [Viena lygtis, dvylika padarų]
**Must land:** Starfish, flowers, crystals and plain circles all fall out of the same equation, depending on six numbers.
**On screen:** `docs/images/supershapes.png`, full bleed. The superformula written across the top in large type.
**Timing:** 8:30–10:00
Johan Gielis, botanist, 2003. Point at the green cube and the blue sea urchin and say: those two differ by what somebody typed inside the brackets. Then pause. This is the emotional centre of the talk — you stop seeing a starfish and start seeing the exponent that made it.

### 10. A loop is a city [Ciklas – tai miestas]
**Must land:** Two loops and a die-roll per block produce twenty thousand polygons of city that nobody has ever seen.
**On screen:** `docs/images/city.png`, then **LIVE DEMO**: `demo3_city.py`, change `SEED = 2026` to a number an audience member shouts out, run, render. Second town beside the first.
**Timing:** 10:00–11:15
Let the audience pick the seed. It takes ten seconds and it is the moment the room realises the model is not stored anywhere.

### 11. A small rule, applied again and again [Maža taisyklė, kartojama vėl ir vėl]
**Must land:** Recursion makes objects nobody could draw by hand — eighteen lines of Menger sponge, fifteen of tree.
**On screen:** `docs/images/fractals.png`. Overlay the `menger` function on the left half, the `branch` function on the right.
**Timing:** 11:15–12:30
Describe the sponge in words before showing the code: take a cube, throw away the middle of every face and the middle of the middle, then do the same to the twenty cubes that are left.

### 12. Six kilobytes in, six megabytes out [Šeši kilobaitai į vidų, šeši megabaitai į išorę]
**Must land:** A formula is a short description of a very large object.
**On screen:** Two file listings, nothing else: `17_fractals.py — 5.8 KB` and `fractals.off — 6.0 MB`.
**Timing:** 12:30–13:15
One sentence, then silence for two seconds. Do not elaborate.

### 13. The other half: taking material away [Kita pusė: medžiagos atėmimas]
**Must land:** `difference` does what a drill does, and `union` does what welding does.
**On screen:** `docs/images/booleans.png`, zoomed to the green cube with three holes and the gold gear. The four-line gear code beside it.
**Timing:** 13:15–14:30
The gear is the one to dwell on: a disc, one tooth, sixteen copies round a circle, a hole through the middle.

### 14. How do you know what is inside? [Iš kur žinoti, kas yra viduje?]
**Must land:** Chop both surfaces along each other, then fire a ray from each piece and count crossings — an odd number means inside.
**On screen:** A hand drawing, done live if you can: two overlapping outlines, a dotted line chopping them, then an arrow leaving one small piece and crossing the other outline three times.
**Timing:** 14:30–15:45
Say that this is a genuinely hard problem and that the six hundred lines that solve it are in the file, readable. Do not use the words "constructive solid geometry" until after you have drawn the picture.

### 15. So: a chess set [Taigi: šachmatai]
**Must land:** Every piece is a curve spun around an axis, and the rook's battlements are two boxes subtracted from the top.
**On screen:** `docs/images/chess_set.png` again, with `rook_profile` and the `make_rook` difference call beside it. Also `docs/images/lathe.png` if you have a spare fifteen seconds.
**Timing:** 15:45–16:45
The callback to slide 1. The audience has now been given every idea the chess set needed, and they should feel that.

### 16. It runs on the school laptop [Veikia ir mokykliniame nešiojamajame]
**Must land:** One file, two imports, no installation — and a renderer in the box, so you can see the result without admin rights.
**On screen:** **LIVE DEMO.** `python3 tools/preview.py examples/out/chess_set.off` in a terminal, then open the PNG. Beside it, `add.py` scrolled to the top: `import math`, `import random`.
**Timing:** 16:45–17:45
Say the constraint out loud: a locked disk, no admin password, no internet in the room. That was the design brief, and it is why there are no dependencies.

### 17. Who this is for [Kam tai skirta]
**Must land:** If you liked the geometry lessons and assumed graphics was somewhere else behind a price tag, it is not.
**On screen:** A grid of six: `patterns.png`, `surfaces_nature.png`, `lathe.png`, `curves.png`, `height_fields.png`, `two_sided.png`.
**Timing:** 17:45–18:45
Name the audiences explicitly: pupils, teachers who want a lesson that ends in something you can hold up, hobbyists, and anybody who likes an equation and would like to see it from the side.

### 18. Start with a triangle [Pradėkite nuo trikampio]
**Must land:** It is free, it is one file, and the first model takes about ten minutes.
**On screen:** The project address, large. Underneath, small: *Martynas Sabaliauskas, VU MIF. MIT licence.* In the corner, the six-line triangle file from slide 5.
**Timing:** 18:45–20:00
End on the triangle, not on the chess set. The last thing they should see is the smallest thing, because that is the thing they can do tonight.

---

## Three questions you will be asked

### "Why not just use Blender? It would take five minutes."

For a chess set, yes — Blender is faster, and if a chess set is what you want, use it. The assignment is not trying to compete with Blender. It is trying to make you say out loud what a shape *is*, which you never have to do when you can drag a corner into place with a mouse.

But there is a second answer, and it is the more interesting one. Some things are genuinely easier this way. A city with four hundred buildings, each one different: in a modelling program that is four hundred acts of work, or it is learning that program's own scripting language, which is a bigger detour than learning this. A Menger sponge at level three has eighty-seven thousand faces and no human patience behind it. Anything with a parameter you want to sweep — every wheel size, every tooth count, every seed — is a loop here and a long afternoon there.

And yes, you can print what comes out. Save as `.stl`, and `check()` will tell you beforehand whether the surface is closed, which is what a printer cares about.

### "Do you have to be good at maths?"

You have to be willing to look at a formula, which is not the same thing.

The sphere is `cos`, `sin`, and knowing that two angles pick out a point. That is one lesson of school trigonometry, and it is the deepest piece of mathematics in the whole first month. The city needs no trigonometry at all — it is a loop, a random number and a box. The tree is a function that calls itself three times. Plenty of students get to ten thousand polygons using only boxes, cylinders and loops, and their models are not worse for it.

What actually separates the students who enjoy this from the ones who do not is not mathematical ability. It is whether they are willing to change a number, run it again, and look. The ones who iterate get somewhere. The ones who try to derive the whole thing on paper first get stuck. That is worth telling a class on day one.

### "How does this actually go with a class of thirty, and what goes wrong?"

Roughly: two hours to the first model, two weeks to something they are pleased with.

The three things that reliably go wrong, in order of frequency:

1. **The surface is not closed**, so booleans behave strangely and the volume comes out as nonsense. `check()` names this one directly — it counts the edges that have nothing on the other side. Usually it is a parametric surface that needed `wrap_u=True`, or a sheet that needed thickness.
2. **They aim for ten thousand polygons by adding detail to one object**, which gets slow and ugly, instead of by repetition, which is what the loop requirement is quietly pushing them towards. A hundred copies of a hundred-face object is the intended route.
3. **They build the scene in the wrong order.** `layer()` takes away everything drawn so far, so a student who draws the floor first and then builds a chair will find the floor inside the chair. Both the chess set and the city examples have a comment about exactly this, because it catches almost everyone once.

For a single lesson rather than a course, the reliable ninety minutes is: triangle, cube, open the `.off` file, sphere, change one number, then let them loose on the city example with instructions to change the seed and nothing else. Every pupil leaves with a different city and a picture of it.

---

## The 3-minute lightning version

Five slides. For a festival stage, a lightning-talk slot, or the two minutes you get in a staff meeting.

**1. Nobody drew this. (0:00–0:30)** [Niekas to nepiešė]
`chess_set.png`, full bleed. "A chess set. A hundred and sixty thousand polygons. It came out of a six-kilobyte text file. There is no modelling program anywhere in this story."

**2. A 3D model is a list of points. (0:30–1:15)** [Trimatis modelis – tai taškų sąrašas]
The six-line `cube.off` file on screen, large. "Eight corners. Six faces. Six lines saying which corners to join and what colour. That is all a 3D model is, and once you know that, you can write one."

**3. A sphere is three lines; one number makes it a doughnut. (1:15–2:00)** [Sfera – trys eilutės]
The three-line sphere function, then three renders as R goes 0, 0.4, 2. "Two angles pick out a point on a ball. Sine and cosine do the picking. Push the circle off the axis before you spin it and the same three lines give you a doughnut. The shape was never in the code. It was in the number."

**4. A loop is a city. (2:00–2:35)** [Ciklas – tai miestas]
`city.png`. "Two loops over street blocks, a die-roll per building. Twenty thousand polygons out of a hundred lines. Change the seed and you get a town nobody has ever seen."

**5. One file, free, runs on a school laptop. (2:35–3:00)** [Vienas failas, nemokamas, veikia mokykloje]
The project address and the six-line triangle. "One Python file, two imports, MIT licence, nothing to install. Start with a triangle. It takes about ten minutes."

If you have only one slide, make it number 3. The sphere-to-doughnut is the whole idea in forty-five seconds.

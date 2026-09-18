# Nobody drew any of this

**A short film about `add.py` — building 3D models out of nothing but code.**

- Target length: 8 minutes (7:55 as written)
- Narration: about 1180 words, read at a measured pace, roughly 145 words per minute
- Audience: bright, curious, has never written a line of graphics code
- All images referenced live in `docs/images/`; all code shown is real and runs

---

## Storyboard

| Time | On screen | Narration |
|---|---|---|
| **0:00–0:14** | `docs/images/chess_set.png`. Start on the whole board, push in slowly until the white king fills a third of the frame. No music yet. | This is a chess set. Thirty-two pieces, a board, a hundred and sixty thousand polygons. Nobody drew it. |
| **0:14–0:26** | Cross-fade to `docs/images/city.png`. Slow drift left to right across the skyline. Music enters, quiet. | This is a city. Nobody drew that either. There are no buildings stored in the file that made it. Only a loop, and a random number generator. |
| **0:26–0:40** | `docs/images/fractals.png`. Push into the Menger sponge — the green-and-gold cube left of centre. Hold on the holes. | And this is a cube with its middle taken out. Then the middles of what is left taken out. Then again, until there is more hole than cube. There is no modelling program anywhere in this story. |
| **0:40–0:48** | Title card on black: **add.py — 3D models made of nothing but code.** Below, small: *Martynas Sabaliauskas, Vilnius University, Faculty of Mathematics and Informatics.* | Every shape you just saw is a Python file you could read over a cup of coffee. |
| **0:48–1:08** | Plain slide, one line at a time, typed in: *Make a 3D model.* / *No modelling program.* / *No downloaded meshes.* / *At least 10 000 polygons.* / *At least 3 colours.* / *Use a loop.* / *One number must change the shape.* | It starts as a university assignment. Make a 3D model. But you may not open a modelling program, and you may not download one from the internet. Everything in it has to come out of a formula or a loop that you wrote. Ten thousand polygons at least. Three colours at least. Somewhere, a loop. And one number that, when you change it, changes the shape. |
| **1:08–1:28** | Split screen. Left: a screenshot of a crowded professional modelling interface, desaturated, with a red line through it. Right: a text editor holding eight lines of Python, in colour. | That sounds like taking the tools away, and it is. It also turns out to be the interesting part. When you cannot drag a corner with the mouse, you have to say where the corner is. A shape stops being something you nudge into place and becomes something you can describe. |
| **1:28–1:50** | Screen recording. Empty editor. Type live: `import add` / `add.triangle([0,0,0], [1,0,0], [0,1,0], "red")` / `add.save("t.off")`. Run it. The rendered triangle appears beside the code. | So start as small as it goes. Three points in space, and an instruction to stretch a skin between them. That is a triangle. A triangle is the only thing a computer really draws. Everything else is a great many of them. |
| **1:50–2:05** | Same recording: open `t.off` in a text editor. It is six lines. Highlight `3 1 0`, then the three coordinate lines, then the last line. | And this is the file. Six lines. Three corners, one face. Three lines of coordinates. Then one line that says: join corner nought to corner one to corner two, and paint it red. |
| **2:05–2:32** | Change the code to `add.box([0,0,0], 1, "red")`. Run. Open `cube.off`. Highlight the header `8 6 0`, then the eight coordinate lines, then the six face lines, one group at a time. | Now a cube. Eight corners, six faces. Eight lines of coordinates. Then six lines saying which corners to join, and what colour each patch should be. That is a 3D model. A list of points, and a list of which points to join. There is nothing else hiding in there. |
| **2:32–2:52** | Run `examples/01_first_model.py` in a terminal. The `check()` output prints. Hold on the two lines `!! polygons 2478 (need 10000)` and `OK colours 3 (need 3)`. Then cut to `docs/images/first_model.png`. | Three shapes, three colours. There is a function called `check` that reads your model back and tells you where you stand. Two and a half thousand polygons. Three colours. Closed surface: yes. Ten thousand needed, so — not yet. Which is the whole game. |
| **2:52–3:22** | Screen recording. Type the sphere function from scratch: `def ball(u, v): return [math.cos(u)*math.cos(v), math.sin(v), math.sin(u)*math.cos(v)]`, then the `add.parametric(...)` call. As it runs, an overlay animates two angles sweeping round a globe. | A sphere is three lines. Think of two angles. How far round you have walked, and how far up. Every pair of angles picks out exactly one point on the ball, and sine and cosine do the picking. The library walks a grid of those two angles and joins the dots. Sixty steps round, thirty up: eighteen hundred little squares, and a sphere. |
| **3:22–3:44** | Same code, one edit: `(R + math.cos(v))` in two places. A slider overlay shows R. Cross-fade between three renders as R goes 0 → 0.4 → 2.0. | Now push that circle away from the axis before you spin it. One number. R. At zero, it is still a ball. At nought point four, it is an apple. At two, it is a doughnut. The same handful of sines and cosines every time. The shape was never really in the code. It was in the number. |
| **3:44–4:10** | `examples/08_surfaces_superformula.py`, scrolled to the `super_r` function. Then the `SHAPES` list, with the twelve names visible. | In 2003 a botanist called Johan Gielis wrote down a single equation and noticed that starfish, flowers, diatoms, crystals and plain circles all fall out of it, depending on six numbers. Here is the equation. Eight lines. And here are twelve sets of six numbers. |
| **4:10–4:34** | `docs/images/supershapes.png`. Slow pan across all twelve: the green cube, the red ball, the yellow star, the magenta flower, the blue urchin. | Twelve creatures, one piece of code. The only difference between the sphere and the sea urchin is what somebody typed inside the brackets. This is the moment the course is really for. You stop seeing a starfish, and start seeing the exponent that made it. |
| **4:34–5:02** | `examples/19_city.py`, scrolled to the double loop over `bx` and `bz`. Highlight `rng.random() < 0.12` and `rng.uniform(1.2, 7.0)`. Then `docs/images/city.png`. Then change `SEED = 2026` to another number and re-render to a visibly different town. | A loop is the cheapest thing in programming and the most useful thing in modelling. This is a city. Two loops over street blocks. For each block, roll a die: park, or buildings. For each building, roll again for its width, its height, its style. Twenty thousand polygons out of a hundred lines. Change the seed at the top and you get a different town — one that nobody has ever seen. That is a strange and rather good feeling. |
| **5:02–5:30** | `examples/17_fractals.py`, the `menger` function, all eighteen lines on screen at once. Then push into the sponge in `docs/images/fractals.png`, right into the holes. | Recursion is stranger still. This is the whole Menger sponge. Take a cube, throw away the middle of every face and the middle of the middle, then do exactly the same thing to each of the twenty cubes that survive. Eighteen lines. Eighty-seven thousand polygons. |
| **5:30–5:46** | The `branch` function, fifteen lines. Then pan right across `docs/images/fractals.png` to the tree. | And this is a tree. A trunk that draws three smaller trunks. Each of which draws three smaller trunks. Until they are small enough to be leaves. Fifteen lines. |
| **5:46–5:58** | Two file listings side by side: `17_fractals.py — 5.8 KB` and `fractals.off — 6.0 MB`. Let the numbers sit. | Six kilobytes of program. Six megabytes of model. A thousand times bigger coming out than going in. A short description of a very large object is exactly what a formula is for. |
| **5:58–6:22** | `examples/16_booleans.py`, the "three holes" block: a box, three cylinders, one `add.difference` call. Then push into the green cube in `docs/images/booleans.png` — the one with black holes through three faces. | Until now we have only added material. The other half of modelling is taking it away. Here is a block, and here are three cylinders passing through it. The word `difference` does what a drill does. Keep the block, minus wherever the cylinders were. The fresh surface inside each hole takes the colour of the drill, so you can see what you did. |
| **6:22–6:42** | The gear block from the same file: four lines. Then push into the gold gear at the far left of `docs/images/booleans.png`, and rotate it. | Join and cut in the same breath, and you get a gear. A disc. One tooth. Sixteen copies of that tooth around a circle, welded into the disc. Then a hole through the middle. Four lines. And it is a real solid, not a picture of one. You could send it to a printer. |
| **6:42–7:04** | Simple hand-drawn animation, white on dark: two overlapping outlines; a dotted line chops them along each other; then an arrow flies out from one small piece and crosses the other outline — one, two, three crossings, counted on screen. | Working out where one solid stops and another starts is a genuinely hard problem, and in this file it is written out from scratch, in about six hundred lines. The trick is smaller than you would expect. First, chop both surfaces along each other, until no piece is half in and half out. Then, for each piece, fire an arrow off into the distance and count how many times it crosses the other surface. An odd number means you started inside. That is the whole test. |
| **7:04–7:20** | Back to `docs/images/chess_set.png`. Callout circles the rook. Beside it, the `rook_profile` function and the `add.difference` call in `make_rook`. | Which brings us back to where we started. Every piece on that board is a curve spun around an axis, the way a potter turns a pot. The rook's battlements are two boxes subtracted from the top. That is the whole chess set. |
| **7:20–7:36** | `add.py` open in an editor, scrolling fast from top to bottom. Stop at the top and hold on `import math` and `import random`. | It is one file. Three and a half thousand lines, about a hundred and thirty functions, and at the top of it, two imports. Maths, and random. That is everything it needs. No installation. No package manager. No account. If a machine has Python on it, it already has this. |
| **7:36–7:48** | An ordinary laptop, terminal only: `python3 tools/preview.py chess_set.off`. A PNG appears in the file browser. Open it. | Including looking at it. There is a renderer in the box, also written from nothing, that turns a model into a picture. So a school laptop with a locked disk and no admin password can do all of this. That was rather the point. |
| **7:48–8:00** | Grid of six stills, each held for two seconds: `patterns.png`, `surfaces_nature.png`, `lathe.png`, `curves.png`, `height_fields.png`, `two_sided.png`. Then the project address on black, and a last slow rotation of the chess set. | It is free, under an MIT licence, written by Martynas Sabaliauskas at the Faculty of Mathematics and Informatics in Vilnius. If you liked the geometry lessons and assumed graphics was somewhere else, behind a price tag — it is not. Take it, make something, and put a picture of it where somebody else can see. The first one takes about ten minutes. Start with a triangle. |

---

## Production notes

### What to screen-record

Six recordings carry the whole film. Record each one clean, at 1920×1080, with the editor font at 18–20 pt so it survives a phone screen.

1. **The triangle and the cube.** One take, typed live and slowly, from empty file to `t.off` open in a text editor, then edited into `cube.off`. This is the single most important shot in the video. Do not speed it up. A viewer needs to see a human being type six lines and get a file.
2. **`check()` running.** `python3 examples/01_first_model.py` in a terminal with a large font. The red `!!` markers should be legible.
3. **Sphere to torus.** Type the sphere, run, then add `R +` in two places and run again with three values of R. If you can, wire R to an on-screen slider in the edit; if not, three cuts with a number overlay work as well.
4. **The city reseeded.** `SEED = 2026`, run, render. Change to `SEED = 7`, run, render. Two towns side by side.
5. **Booleans.** The three-holes block and the gear block from `examples/16_booleans.py`, run one after the other.
6. **`preview.py`.** The terminal command, then the PNG opening. Shoot this on the oldest, plainest laptop you can find. It matters that it looks like a school machine.

All the finished models already exist in `examples/out/`, and the rendered stills in `docs/images/`, so nothing needs to be generated on camera except what is being explained.

### Music

Quiet, unhurried, mostly piano or a small string figure. It should sound like somebody thinking, not like a product launch. Enter at 0:14 under the city, drop out entirely at 1:28 when the typing starts, and stay out until 4:10 so the code sections are dry and clear. Come back under the supershapes pan, lift slightly at the Menger sponge, and carry the last ninety seconds. Nothing percussive. No build to a drop.

### If there is no budget for animation

There does not need to be. The film works as screen recordings plus the rendered PNGs, and only two moments genuinely want a drawing:

- **The two angles on a sphere (2:52).** If you cannot animate it, film a hand drawing them on paper: a circle, a line round the equator, a line up to the pole, a dot where they meet. Ten seconds of hand and pencil is warmer than a motion graphic anyway.
- **The ray crossing a surface (6:42).** The same solution. Two overlapping shapes drawn on paper, a dotted arrow, and three tick marks counted out loud.

For everything else: take the PNGs in `docs/images/` at their native resolution and give them slow camera pushes — twelve to fifteen seconds of movement across a still, never more than a ten per cent zoom, always easing in and out. Five of them are wide gallery images (`supershapes.png`, `booleans.png`, `fractals.png`, `patterns.png`, `surfaces_nature.png`), which means each one contains six to twelve separate shots if you push into individual objects. That is more than enough material.

If you want live rotation instead of stills, `tools/preview.py` takes a `--turn` angle. Render the same model at one-degree steps and assemble the frames into a loop; thirty-six frames at twelve frames per second gives a three-second turntable, and it costs nothing but time.

### Two things to avoid

- Do not cut the typing faster than a person can read. The film's whole argument is that this is small enough to understand, and fast cuts say the opposite.
- Do not put a polygon count on screen as a boast. The numbers are there to show that a short program makes a big thing, not to impress anyone.

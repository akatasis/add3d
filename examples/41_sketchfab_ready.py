"""
41 -- getting a model ready for Sketchfab: file size and colour count.

Sketchfab takes ``.obj`` + ``.mtl`` (upload both in one zip).  Two things
matter: the file size (100 MB on the free plan; the course asks for 50) and
the number of *materials* -- every distinct colour of the model becomes
one, and Sketchfab starts merging them above 100.  A gradient painted with
``add.color_by`` can easily use thousands of shades, so the recipe is:

1. build, and paint as freely as you like;
2. ``add.palette`` shows how many colours there are and which are common;
3. ``add.limit_colors(M, 50)`` groups similar shades into at most 50;
4. ``add.obj_size`` says how big the .obj will be before writing it;
5. ``add.save("x.obj", M, colors=50)`` does step 3 while saving.

The model: a vase from ``add.revolve`` painted with a two-way gradient, a
quad sphere with a rainbow, and an owl surface (``add.surface_function``
fed to ``add.parametric`` with our own range and colouring).

Parameter: ``COLORS`` (the colour budget).
"""
import add

COLORS = 50

# a vase painted by height *and* angle: thousands of different shades
def vase(t):
    return [1.2 + 0.5 * add.sin(2.2 * t) + 0.15 * add.cos(9 * t), t]


add.revolve(vase, [-4, 0, 0], [-4, 1, 0], 0, 4.5, 90, 72, caps=True,
            color=lambda t, a: add.hsv(t / 6.0 + 0.1 * add.sin(4 * a), 0.8, 0.95))

# a quad sphere (six patches of quads) painted by direction.  add.make()
# builds it as a separate mesh, so the vase is not scooped up with it.
ball = add.make(add.quadsphere, [0, 1.5, 0], 1.5, 30)
ball = add.color_by(ball, lambda p: add.hsv((p[1] + 1) / 6.0, 0.9, 1.0))
add.mesh(ball)

# the owl from the catalogue, but on our own parameter range and colouring
owl = add.surface_function("owl")
sheet = add.make(add.parametric, owl, 0, 4 * add.pi, 160, 0.001, 1, 30,
                 color=lambda u, v: add.gradient(v, "navy", "white"), thickness=0.04)
add.mesh(add.place(add.fit(sheet, 3.2), [4.5, 1.6, 0]))

model = add.layer()
print("colours before:", len(add.palette(model)))
print("most used:", add.palette(model)[:3])
print("obj size before: %.2f MB" % (add.obj_size(model) / 1e6))

small = add.limit_colors(model, COLORS)
print("colours after :", len(add.palette(small)))
add.mesh(small)
add.check()
add.save("sketchfab_ready.off")
add.save("sketchfab_ready.obj", small)          # .obj + .mtl, at most 50 materials
print("written sketchfab_ready.obj, %.2f MB" % (add.obj_size(small) / 1e6))

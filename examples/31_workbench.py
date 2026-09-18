"""
31 -- the workbench: measuring, repairing, inspecting and saving.

Not every function draws.  This example is a tour of the ones that look
*at* a model: ``stats``/``check`` report on it, ``bbox``, ``size``,
``center``, ``middle``, ``area`` and ``volume`` measure it, ``inside``
asks whether a point is in it, and ``clean``, ``heal``, ``fix_normals``
and ``triangulate`` repair it.  A deliberately broken mesh is built by
hand with the ``Mesh`` class, repaired, and shown next to the original.
The models are saved in every format (``save``, ``off``, ``obj``) and one
is ``load``-ed straight back.

Parameter: ``SAMPLES`` (points thrown at the torus for the inside test).
"""
import os
import add

SAMPLES = 400
rng = add.Random(1)
add.axes([0, 0, 0], 2.5)

# --------------------------------------------------------------------------
#  1. a broken model, made by hand, and its repaired twin
# --------------------------------------------------------------------------
M = add.Mesh()                                           # a cube, face by face
corners = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]]
for p in corners:
    M.add_vertex(p)
M.add_face([0, 3, 2, 1], "red")                          # bottom
M.add_face([4, 5, 6, 7], "red")                          # top
M.add_face([0, 1, 5, 4], "red")                          # front
M.add_face([2, 3, 7, 6], "red")                          # back
M.add_face([1, 2, 6, 5], "red")                          # right
M.add_face([3, 0, 4, 7], "red")                          # left, wound the WRONG way
M.add_face([3, 0, 4, 7], "red")                          # ... and added twice
M.add_face([0, 3, 7, 4], "red")                          # ... and once more, the right way
M.add_vertex([0.5, 0.5, 0.5])                            # an unused vertex
print("hand-made cube:", M, "outward volume %.3f" % add.volume(M))
broken = add.zoom(M, 2.0, (0, 0, 0))
add.mesh(add.move(broken, [-6, 0, -3]))

repaired = add.clean(broken)                             # weld, drop duplicates, fix winding
repaired = add.fix_normals(repaired)
print("after clean():", repaired, "volume %.3f" % add.volume(repaired),
      "closed:", add.stats(repaired)["closed"])
add.mesh(add.color(add.move(repaired, [-3, 0, -3]), "green"))
add.text("BROKEN", [-6.2, -0.7, -0.9], 0.4, color="red", k=5, u=[1, 0, 0], v=[0, 0, -1])
add.text("CLEANED", [-3.4, -0.7, -0.9], 0.4, color="green", k=5, u=[1, 0, 0], v=[0, 0, -1])

# --------------------------------------------------------------------------
#  2. a T-junction: two boxes sharing a wall at different resolutions
# --------------------------------------------------------------------------
add.push()
add.cuboid([0, 0.5, 0], [2, 1, 2], "sky")
add.cuboid([0, 1.5, 0.5], [1, 1, 1], "sky")             # sits on the first one's top
pair = add.pop()
print("stacked boxes: open edges before heal:", add.stats(pair)["open_edges"])
joined = add.heal(add.union(add.cut(pair, [0, 1, 0], [0, 1, 0]), add.cut(pair, [0, 1, 0], [0, -1, 0])))
print("               open edges after union+heal:", add.stats(joined)["open_edges"])
add.mesh(add.move(joined, [1.5, 0, -3.5]))
add.mesh(add.move(add.color(add.triangulate(joined), "teal"), [4.5, 0, -3.5]))
add.text("UNION", [1.0, -0.7, -0.9], 0.4, color="navy", k=5, u=[1, 0, 0], v=[0, 0, -1])
add.text("TRIANGLES", [3.6, -0.7, -0.9], 0.4, color="teal", k=5, u=[1, 0, 0], v=[0, 0, -1])

# --------------------------------------------------------------------------
#  3. inside or outside?  random points coloured by a torus
# --------------------------------------------------------------------------
add.push()
add.torus([0, 0, 0], 1.6, 0.6, 36, 18, "gold")
ring = add.pop()
add.mesh(add.move(ring, [-4, 1.2, 3]))
points = add.random_points(SAMPLES, [-2.4, -0.8, -2.4], [2.4, 0.8, 2.4], 3)
answers = add.inside(ring, points)                       # one call for all the points
hits = sum(answers)
for q, hit in zip(points, answers):
    if hit:
        add.sphere([q[0] - 4, q[1] + 1.2, q[2] + 3], 0.07, 3, "red")
    else:
        add.sphere([q[0] - 4, q[1] + 1.2, q[2] + 3], 0.04, 2, [90, 90, 100])
box_volume = 4.8 * 1.6 * 4.8
print("torus volume by counting: %.2f, exact %.2f, mesh %.2f"
      % (box_volume * hits / SAMPLES, 2 * add.pi ** 2 * 1.6 * 0.6 ** 2, add.volume(ring)))

# --------------------------------------------------------------------------
#  4. measuring: bounding box, sizes, centres, area
# --------------------------------------------------------------------------
add.push()
add.cone([0, 0, 0], [0, 2.5, 0], 1.0, 24, "orange")
cone = add.pop()
lo, hi = add.bbox(cone)
print("cone bbox", lo, hi, "size", add.size(cone))
print("cone centre of mass %s, middle of box %s" % (
    [round(c, 2) for c in add.center(cone)], [round(c, 2) for c in add.middle(cone)]))
print("cone area %.3f (exact %.3f)" % (add.area(cone), add.pi * 1.0 * (1.0 + add.sqrt(1 + 2.5 ** 2))))
add.mesh(add.move(cone, [1.5, 0, 3]))
add.push()
add.box([0, 0, 0], 0.12, "black")
dot = add.pop()
add.mesh(add.move(dot, [1.5 + add.center(cone)[0], add.center(cone)[1], 3]))    # mark the centroid
frame = add.copy(cone)                                   # an independent copy to play with
add.wireframe(add.move(add.triangulate(frame), [4.5, 0, 3]), 0.02, 5, "orange", nodes=False)

# --------------------------------------------------------------------------
#  5. colours and saving
# --------------------------------------------------------------------------
print("rgb('sky') =", add.rgb("sky"), " gradient =", add.gradient(0.5, "red", "blue"),
      " random =", add.random_color(7))
add.push()
add.sphere([0, 0, 0], 0.9, 12, "white")
ball = add.color_random(add.pop(), seed=2)               # every face its own colour
add.mesh(add.move(ball, [7.5, 1.0, 3]))
add.glyph("Z", [7.0, 2.3, 3], [1, 0, 0], [0, 1, 0], 0.6, 0.04, "navy")

everything = add.scene()                                 # the live scene object
print("scene so far:", everything)
add.save("workbench.obj")                                # .obj + .mtl, scene stays
add.save("workbench.ply")
add.obj("workbench_copy.obj")                            # add.py 1.2 style: writes and clears
print("after obj(): scene is", add.scene())
os.remove("workbench_copy.obj")
os.remove("workbench_copy.mtl")
back = add.load("workbench.obj")                         # and straight back in
add.mesh(back)
add.check()
add.off("workbench.off")

# and finally the library's own one-line demonstration model
print("demo written to", add.demo("demo.off"))

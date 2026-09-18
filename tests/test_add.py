"""Tests for add.py.  Run with:  python3 -m pytest tests  (or just python3 tests/test_add.py)"""
import math
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import add


# --------------------------------------------------------------------------
#  helpers
# --------------------------------------------------------------------------

def closed(M):
    return add.stats(M)["closed"]


def check_volume(M, expected, tol=0.02):
    v = add.volume(M)
    assert abs(v - expected) <= tol * max(1.0, abs(expected)), \
        "volume %.5f, expected %.5f" % (v, expected)


# --------------------------------------------------------------------------
#  core
# --------------------------------------------------------------------------

def test_scene_and_layer():
    add.clear()
    add.box([0, 0, 0], 2, [255, 0, 0])
    assert len(add.faces) == 6
    assert len(add.vertices) == 8
    M = add.layer()
    assert len(add.faces) == 0
    assert M.polygons == 6
    add.mesh(M)
    assert len(add.faces) == 6
    add.clear()


def test_push_and_pop():
    add.clear()
    add.box([0, 0, 0], 1, "red")           # something already in the scene
    add.push()
    assert len(add.faces) == 0
    add.sphere([0, 0, 0], 1, 6, "blue")
    part = add.pop()
    assert part.polygons == 216
    assert len(add.faces) == 6              # the box came back
    add.clear()


def test_old_string_api():
    """M[0] / M[1] must still look like add.py 1.2's string lists."""
    add.clear()
    add.box([1, 2, 3], 2, [10, 20, 30])
    M = add.layer()
    assert isinstance(M[0][0], str)
    assert isinstance(M[1][0], str)
    assert M[1][0].split()[0] == "4"
    assert M[1][0].split()[-3:] == ["10", "20", "30"]
    # and a raw [vertices, faces] pair must be accepted everywhere
    pair = [list(M[0]), list(M[1])]
    assert add.as_mesh(pair).polygons == 6
    assert add.volume(add.move(pair, [1, 0, 0])) > 7.9


def test_global_lists_still_writable():
    add.clear()
    add.vertices += ["0 0 0", "1 0 0", "0 1 0"]
    add.faces += ["3 0 1 2 255 0 0"]
    assert len(add.faces) == 1
    assert add.stats()["faces"] == 1
    add.clear()


def test_colors():
    assert add.rgb([255, 0, 0]) == (255, 0, 0)
    assert add.rgb("red") == (255, 0, 0)
    assert add.rgb("#00ff00") == (0, 255, 0)
    assert add.rgb((1.0, 0.0, 0.0)) == (255, 0, 0)
    assert add.rgb(None) == add.DEFAULT_COLOR
    assert add.gradient(0.0, "black", "white") == (0, 0, 0)
    assert add.gradient(1.0, "black", "white") == (255, 255, 255)
    assert add.hsv(0.0) == (255, 0, 0)


# --------------------------------------------------------------------------
#  primitives -- every closed solid must be watertight and outward-facing
# --------------------------------------------------------------------------

def test_box_is_closed_with_right_volume():
    add.clear()
    add.box([0, 0, 0], 2, "red")
    check_volume(add.layer(), 8.0)


def test_cuboid_volume():
    add.clear()
    add.cuboid([1, 2, 3], [2, 3, 4], "red")
    M = add.layer()
    assert closed(M)
    check_volume(M, 24.0)


def test_sphere_volume_and_closure():
    add.clear()
    add.sphere([0, 0, 0], 1.0, 24, "blue")
    M = add.layer()
    assert closed(M), add.stats(M)
    check_volume(M, 4.0 / 3.0 * math.pi, 0.01)


def test_uvsphere_volume():
    add.clear()
    add.uvsphere([0, 0, 0], 1.0, 48, 24, "blue")
    M = add.layer()
    assert closed(M), add.stats(M)
    check_volume(M, 4.0 / 3.0 * math.pi, 0.01)


def test_ellipsoid_volume():
    add.clear()
    add.ellipsoid([0, 0, 0], [1, 2, 3], 20, "blue")
    check_volume(add.layer(), 4.0 / 3.0 * math.pi * 6, 0.01)


def test_cylinder_volume():
    add.clear()
    add.cylinder([0, 0, 0], [0, 3, 0], 1.0, 64, "red")
    M = add.layer()
    assert closed(M)
    check_volume(M, math.pi * 3, 0.01)


def test_cone_volume():
    add.clear()
    add.cone([0, 0, 0], [0, 3, 0], 1.0, 64, "red")
    M = add.layer()
    assert closed(M)
    check_volume(M, math.pi * 3 / 3.0, 0.01)


def test_frustum_volume():
    add.clear()
    add.frustum([0, 0, 0], [0, 2, 0], 2.0, 1.0, 64, "red")
    M = add.layer()
    assert closed(M)
    check_volume(M, math.pi * 2 / 3.0 * (4 + 2 + 1), 0.01)


def test_torus_volume():
    add.clear()
    add.torus([0, 0, 0], 3.0, 1.0, 64, 32, "gold")
    M = add.layer()
    assert closed(M)
    check_volume(M, 2 * math.pi ** 2 * 3 * 1, 0.01)


def test_capsule_volume():
    add.clear()
    add.capsule([0, 0, 0], [0, 4, 0], 1.0, 48, "red")
    M = add.layer()
    assert closed(M)
    check_volume(M, math.pi * 4 + 4.0 / 3.0 * math.pi, 0.02)


def test_pipe_volume():
    add.clear()
    add.pipe([0, 0, 0], [0, 2, 0], 2.0, 1.0, 64, "grey")
    M = add.layer()
    assert closed(M)
    check_volume(M, math.pi * 2 * (4 - 1), 0.01)


def test_pyramid_volume():
    add.clear()
    add.pyramid([0, 0, 0], 2.0, 3.0, "green")
    M = add.layer()
    assert closed(M)
    check_volume(M, 4 * 3 / 3.0)


def test_pyramid_downwards_is_still_outward():
    add.clear()
    add.pyramid([0, 0, 0], 2.0, -3.0, "green")
    M = add.layer()
    assert closed(M)
    assert add.volume(M) > 0


def test_prism_volume():
    add.clear()
    add.prism([[0, 0], [2, 0], [2, 2], [0, 2]], 5.0, "gold")
    M = add.layer()
    assert closed(M)
    check_volume(M, 4 * 5)


def test_frame_is_closed():
    add.clear()
    add.frame([0, 0, 0], 2.0, 0.2, "blue")
    M = add.layer()
    assert closed(M), add.stats(M)
    # 12 bars of 0.2 x 0.2 cross-section, total length 12 * 1.6, plus 8 corners
    check_volume(M, 12 * 1.6 * 0.04 + 8 * 0.008, 0.01)


def test_voxels():
    add.clear()
    add.voxels([(0, 0, 0), (1, 0, 0), (0, 1, 0)], 1.0, color="red")
    M = add.layer()
    assert closed(M)
    check_volume(M, 3.0)


def test_platonic_solids():
    for name, faces in (("tetrahedron", 4), ("cube", 6), ("octahedron", 8),
                        ("dodecahedron", 12), ("icosahedron", 20)):
        add.clear()
        add.polyhedron(name, [0, 0, 0], 1.0, "red")
        M = add.layer()
        assert M.polygons == faces, (name, M.polygons)
        assert closed(M), (name, add.stats(M))
        assert add.volume(M) > 0, name


def test_disc_and_ring_are_open():
    add.clear()
    add.disc([0, 0, 0], [0, 1, 0], 1.0, 32, "red")
    assert add.layer().polygons == 32
    add.ring([0, 0, 0], [0, 1, 0], 2.0, 1.0, 32, "red")
    assert add.layer().polygons == 32


# --------------------------------------------------------------------------
#  surfaces and sweeps
# --------------------------------------------------------------------------

def test_parametric_counts():
    add.clear()
    add.parametric(lambda u, v: [u, v, 0], 0, 1, 4, 0, 1, 5, "red")
    M = add.layer()
    assert M.polygons == 20
    assert len(M.V) == 5 * 6


def test_parametric_wrap_has_no_seam():
    add.clear()

    def torus(u, v):
        return [(3 + math.cos(u)) * math.cos(v), math.sin(u),
                (3 + math.cos(u)) * math.sin(v)]
    add.parametric(torus, 0, 2 * math.pi, 30, 0, 2 * math.pi, 60, "gold",
                   wrap_u=True, wrap_v=True)
    M = add.layer()
    assert len(M.V) == 30 * 60
    assert closed(M), add.stats(M)


def test_parametric_thickness_makes_a_solid():
    add.clear()
    add.parametric(lambda u, v: [u, 0, v], 0, 1, 4, 0, 1, 4, "red",
                   thickness=0.1)
    M = add.layer()
    assert closed(M), add.stats(M)
    check_volume(M, 0.1, 0.05)


def test_two_sided_doubles_faces():
    add.clear()
    add.parametric(lambda u, v: [u, 0, v], 0, 1, 2, 0, 1, 2, "red")
    M = add.layer()
    assert add.two_sided(M).polygons == 2 * M.polygons


def test_revolve_matches_a_cylinder():
    add.clear()
    add.revolve(lambda t: [1.0, t], [0, 0, 0], [0, 1, 0], 0, 3, 8, 64, "red")
    M = add.layer()
    assert closed(M)
    check_volume(M, math.pi * 3, 0.01)


def test_spin3d_still_works():
    add.clear()
    add.spin3D([0, 0, 0], [0, 1, 0], lambda t: [1.0, t], 0, 3, 8, 64, [255, 0, 0])
    assert add.layer().polygons == 8 * 64


def test_curve_tube_is_closed():
    add.clear()
    add.curve(lambda t: [math.cos(t), math.sin(t), 0], 0, 2 * math.pi, 64, 12,
              0.2, "red", True)
    M = add.layer()
    assert closed(M), add.stats(M)
    check_volume(M, 2 * math.pi ** 2 * 1 * 0.04, 0.05)


def test_open_curve_has_caps():
    add.clear()
    add.curve(lambda t: [t, 0, 0], 0, 5, 20, 12, 0.3, "red", False)
    M = add.layer()
    assert closed(M), add.stats(M)
    check_volume(M, math.pi * 0.09 * 5, 0.05)


def test_sweep_with_scale_and_twist():
    add.clear()
    square = [[-1, -1], [1, -1], [1, 1], [-1, 1]]
    add.sweep(square, lambda t: [0, t, 0], 0, 4, 20, "gold",
              scale=lambda t: 1 - 0.5 * t, twist=math.pi)
    M = add.layer()
    assert closed(M), add.stats(M)
    assert add.volume(M) > 0


def test_extrude_volume():
    add.clear()
    add.extrude([[0, 0], [2, 0], [2, 2], [0, 2]], [0, 3, 0], "red")
    M = add.layer()
    assert closed(M)
    check_volume(M, 4 * 3)


def test_loft():
    add.clear()
    a = [(math.cos(t), 0, math.sin(t)) for t in
         [2 * math.pi * i / 16 for i in range(16)]]
    b = [(p[0] * 2, 3, p[2] * 2) for p in a]
    add.loft([a, b], "red")
    M = add.layer()
    assert closed(M), add.stats(M)
    assert add.volume(M) > 0


# --------------------------------------------------------------------------
#  transforms
# --------------------------------------------------------------------------

def test_move_rotate_scale():
    add.clear()
    add.box([0, 0, 0], 2, "red")
    M = add.layer()
    assert add.middle(add.move(M, [5, 0, 0]))[0] == 5
    R = add.rotate(M, [0, 1, 0], math.pi / 2, [0, 0, 0])
    check_volume(R, 8.0)
    check_volume(add.zoom(M, 2), 64.0)
    check_volume(add.stretch(M, [2, 1, 1]), 16.0)


def test_mirror_keeps_volume_positive():
    add.clear()
    add.cone([0, 0, 0], [0, 2, 0], 1.0, 32, "red")
    M = add.layer()
    assert add.volume(add.mirror(M, [0, 0, 0], [1, 0, 0])) > 0


def test_negative_scale_keeps_volume_positive():
    add.clear()
    add.cone([0, 0, 0], [0, 2, 0], 1.0, 32, "red")
    M = add.layer()
    assert add.volume(add.zoom(M, -1)) > 0
    assert add.volume(add.stretch(M, [1, -1, 1])) > 0


def test_place_and_fit():
    add.clear()
    add.box([7, 7, 7], 3, "red")
    M = add.layer()
    assert add.middle(add.place(M, [0, 0, 0])) == [0, 0, 0]
    assert abs(max(add.size(add.fit(M, 1.0))) - 1.0) < 1e-9


def test_deform_twist_taper_bend_run():
    add.clear()
    add.cuboid([0, 2, 0], [1, 4, 1], "red")
    M = add.layer()
    for T in (add.deform(M, lambda p: [p[0], p[1], p[2] + 0.1]),
              add.twist(M, 0.5), add.taper(M, -0.1), add.bend(M, 0.2),
              add.jitter(M, 0.01, seed=1)):
        assert len(T.V) == len(M.V)


def test_color_functions():
    add.clear()
    add.box([0, 0, 0], 1, "red")
    M = add.layer()
    assert set(add.color(M, "blue").C) == {(0, 0, 255)}
    assert len(set(add.color_random(M, seed=3).C)) > 1
    G = add.color_gradient(M, "black", "white", 1)
    assert len(set(G.C)) > 1


def test_arrays():
    add.clear()
    add.box([0, 0, 0], 1, "red")
    M = add.layer()
    assert add.array_linear(M, [2, 0, 0], 5).polygons == 30
    assert add.array_grid(M, [2, 2, 2], [2, 3, 4]).polygons == 6 * 24
    assert add.array_radial(M, 8).polygons == 48
    assert add.array_mirror(M, [2, 0, 0], [1, 0, 0]).polygons == 12
    assert add.repeat(M, 3, lambda X, i: add.move(X, [i, 0, 0])).polygons == 18


# --------------------------------------------------------------------------
#  cleaning
# --------------------------------------------------------------------------

def test_weld_removes_duplicate_vertices():
    add.clear()
    add.box([0, 0, 0], 1, "red")
    add.box([0, 0, 0], 1, "red")
    M = add.layer()
    assert len(M.V) == 16
    C = add.clean(M)
    assert len(C.V) == 8
    assert C.polygons == 6          # the two coincident shells become one
    check_volume(C, 1.0)


def test_clean_removes_internal_wall():
    add.clear()
    add.box([0, 0, 0], 1, "red")
    add.box([1, 0, 0], 1, "blue")
    M = add.layer()
    assert M.polygons == 12
    C = add.clean(M)
    assert C.polygons == 10, add.stats(C)
    assert add.stats(C)["closed"]
    check_volume(C, 2.0)


def test_clean_removes_degenerate_faces():
    add.clear()
    add.vertices += ["0 0 0", "1 0 0", "2 0 0"]
    add.faces += ["3 0 1 2 255 0 0"]
    assert add.clean().polygons == 0
    add.clear()


def test_triangulate():
    add.clear()
    add.box([0, 0, 0], 1, "red")
    T = add.triangulate(add.layer())
    assert T.polygons == 12
    assert all(len(f) == 3 for f in T.F)
    check_volume(T, 1.0)


def test_fix_normals():
    add.clear()
    add.box([0, 0, 0], 2, "red")
    M = add.layer()
    M.F[0].reverse()
    M.F[3].reverse()
    F = add.fix_normals(M)
    check_volume(F, 8.0)


def test_stats_and_check():
    add.clear()
    add.sphere([0, 0, 0], 1, 10, "red")
    s = add.stats()
    assert s["faces"] == 600
    assert s["closed"]
    assert not add.check(quiet=True)
    add.clear()


# --------------------------------------------------------------------------
#  booleans
# --------------------------------------------------------------------------

def two_boxes(offset):
    add.clear()
    add.box([0, 0, 0], 2, "red")
    a = add.layer()
    add.box([offset, 0, 0], 2, "blue")
    b = add.layer()
    return a, b


def test_union_of_overlapping_boxes():
    a, b = two_boxes(1.0)
    U = add.union(a, b)
    assert closed(U), add.stats(U)
    check_volume(U, 8 + 8 - 4, 0.01)


def test_difference_of_overlapping_boxes():
    a, b = two_boxes(1.0)
    D = add.difference(a, b)
    assert closed(D), add.stats(D)
    check_volume(D, 8 - 4, 0.01)


def test_intersection_of_overlapping_boxes():
    a, b = two_boxes(1.0)
    I = add.intersect(a, b)
    assert closed(I), add.stats(I)
    check_volume(I, 4.0, 0.01)


def test_boolean_with_disjoint_boxes():
    a, b = two_boxes(10.0)
    assert abs(add.volume(add.union(a, b)) - 16) < 1e-6
    assert abs(add.volume(add.difference(a, b)) - 8) < 1e-6
    assert add.intersect(a, b).polygons == 0


def test_drill_a_hole_through_a_plate():
    add.clear()
    add.cuboid([0, 0, 0], [4, 1, 4], "brown")
    plate = add.layer()
    add.cylinder([0, -2, 0], [0, 2, 0], 0.8, 48, "brown")
    drill = add.layer()
    D = add.difference(plate, drill)
    assert closed(D), add.stats(D)
    check_volume(D, 16 - math.pi * 0.64, 0.01)


def test_sphere_minus_sphere():
    add.clear()
    add.sphere([0, 0, 0], 1.0, 16, "red")
    a = add.layer()
    add.sphere([0, 0, 0], 0.7, 16, "blue")
    b = add.layer()
    D = add.difference(a, b)
    assert closed(D), add.stats(D)
    outer = add.volume(a)
    inner = add.volume(b)
    check_volume(D, outer - inner, 0.01)


def test_union_keeps_colors():
    a, b = two_boxes(1.0)
    U = add.union(a, b)
    assert (255, 0, 0) in set(U.C)
    assert (0, 0, 255) in set(U.C)


def test_union_of_many():
    add.clear()
    add.box([0, 0, 0], 2, "red")
    a = add.layer()
    add.box([1, 0, 0], 2, "blue")
    b = add.layer()
    add.box([2, 0, 0], 2, "green")
    c = add.layer()
    U = add.union(a, b, c)
    assert closed(U), add.stats(U)
    check_volume(U, 8 + 4 + 4, 0.01)


def test_symmetric_difference():
    a, b = two_boxes(1.0)
    X = add.symmetric_difference(a, b)
    check_volume(X, 4 + 4, 0.05)


def test_cut_plane():
    add.clear()
    add.sphere([0, 0, 0], 1.0, 20, "red")
    M = add.layer()
    H = add.cut(M, [0, 0, 0], [0, 1, 0])
    assert closed(H), add.stats(H)
    check_volume(H, add.volume(M) / 2.0, 0.02)


def test_inside():
    add.clear()
    add.box([0, 0, 0], 2, "red")
    M = add.layer()
    assert add.inside(M, [0, 0, 0])
    assert not add.inside(M, [5, 0, 0])


# --------------------------------------------------------------------------
#  files
# --------------------------------------------------------------------------

def roundtrip(name, M):
    folder = tempfile.mkdtemp()
    path = os.path.join(folder, name)
    add.save(path, M)
    return add.load(path)


def test_off_roundtrip():
    add.clear()
    add.sphere([1, 2, 3], 1.5, 8, [12, 34, 56])
    M = add.layer()
    L = roundtrip("m.off", M)
    assert L.polygons == M.polygons
    assert len(L.V) == len(M.V)
    assert set(L.C) == {(12, 34, 56)}
    check_volume(L, add.volume(M))


def test_obj_roundtrip_with_colors():
    add.clear()
    add.box([0, 0, 0], 1, [200, 100, 50])
    add.box([2, 0, 0], 1, [10, 20, 30])
    M = add.layer()
    L = roundtrip("m.obj", M)
    assert L.polygons == M.polygons
    assert set(L.C) == {(200, 100, 50), (10, 20, 30)}


def test_ply_roundtrip():
    add.clear()
    add.box([0, 0, 0], 1, [7, 8, 9])
    M = add.layer()
    L = roundtrip("m.ply", M)
    assert L.polygons == M.polygons
    assert set(L.C) == {(7, 8, 9)}


def test_stl_is_written():
    add.clear()
    add.box([0, 0, 0], 1, "red")
    folder = tempfile.mkdtemp()
    path = os.path.join(folder, "m.stl")
    add.save(path, add.layer())
    with open(path) as f:
        assert f.read().count("facet normal") == 12


def test_off_clears_the_scene():
    add.clear()
    add.box([0, 0, 0], 1, "red")
    folder = tempfile.mkdtemp()
    add.off(os.path.join(folder, "m.off"))
    assert len(add.faces) == 0


def test_loading_an_old_course_file():
    """The .off files shipped with the course must still load."""
    text = ("OFF\n4 2 0\n0 0 0\n1 0 0\n1 1 0\n0 1 0\n"
            "3 0 1 2 255 0 0\n3 0 2 3 0 255 0\n")
    folder = tempfile.mkdtemp()
    path = os.path.join(folder, "old.off")
    with open(path, "w") as f:
        f.write(text)
    M = add.load(path)
    assert M.polygons == 2
    assert set(M.C) == {(255, 0, 0), (0, 255, 0)}


def test_loading_off_without_colors():
    text = "OFF\n3 1 0\n0 0 0\n1 0 0\n0 1 0\n3 0 1 2\n"
    folder = tempfile.mkdtemp()
    path = os.path.join(folder, "plain.off")
    with open(path, "w") as f:
        f.write(text)
    M = add.load(path)
    assert M.polygons == 1
    assert M.C[0] == add.DEFAULT_COLOR


# --------------------------------------------------------------------------
#  1.2 compatibility names
# --------------------------------------------------------------------------

def test_old_names_exist_and_run():
    add.clear()
    add.cube([0, 0, 0], 1, [255, 0, 0])
    add.cube2([3, 0, 0], 1, 0.1, [0, 255, 0])
    add.rectangle3D([6, 0, 0], [1, 2, 3], [0, 0, 255])
    add.cylinder([0, 3, 0], [0, 4, 0], 0.5, 12, [255, 255, 0])
    add.cylinder2([2, 3, 0], [2, 4, 0], 0.5, 12, [255, 255, 0])
    add.cylinder3([4, 3, 0], [4, 4, 0], 0.5, 12, [255, 255, 0])
    add.cone([0, 6, 0], [0, 7, 0], 0.5, 12, [255, 0, 255])
    add.cone2([2, 6, 0], [2, 7, 0], 0.5, 12, [255, 0, 255])
    add.sphere([4, 6, 0], 0.5, 6, [0, 255, 255])
    add.pyramid([6, 6, 0], 1, 1, [255, 255, 255])
    add.circle([8, 6, 0], [8, 7, 0], 0.5, 12, [255, 255, 255])
    add.newface([[0, 9, 0], [1, 9, 0], [0, 10, 0]], [128, 128, 128])
    add.axes([0, 0, 0])
    s = add.stats()
    assert s["faces"] > 100
    assert s["colors"] >= 3
    add.clear()


def test_aliases():
    assert add.ball is add.sphere
    assert add.block is add.cuboid
    assert add.translate is add.move
    assert add.subtract is not None


def test_demo_runs():
    folder = tempfile.mkdtemp()
    path = add.demo(os.path.join(folder, "demo.off"))
    assert os.path.getsize(path) > 1000
    add.clear()


# --------------------------------------------------------------------------

if __name__ == "__main__":
    passed = failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                passed += 1
            except Exception as exc:                     # noqa: BLE001
                failed += 1
                print("FAIL %-48s %s: %s" % (name, type(exc).__name__, exc))
    print("\n%d passed, %d failed" % (passed, failed))
    sys.exit(1 if failed else 0)

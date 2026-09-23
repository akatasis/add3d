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
    assert part.polygons == 320                # geodesic: 20 * 4 ** 2
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
    assert s["faces"] == 1280                  # geodesic: 20 * 4 ** 3
    assert s["closed"]
    assert not add.check(quiet=True)
    assert s["obj_bytes"] > 0
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
#  only "import add", colour functions, parts, placing, text
# --------------------------------------------------------------------------

def test_math_and_random_are_reexported():
    assert abs(add.sin(add.pi / 2) - 1.0) < 1e-12
    assert add.sqrt(16) == 4
    add.seed(3)
    a = add.randint(1, 1000)
    add.seed(3)
    assert add.randint(1, 1000) == a
    assert "sin" not in add.__all__          # not part of add.py's own vocabulary
    assert "sphere" in add.__all__


def test_color_functions_on_surfaces():
    add.clear()
    add.parametric(lambda u, v: [u, 0, v], 0, 4, 4, 0, 4, 4,
                   color=lambda u, v: "red" if (int(u) + int(v)) % 2 else "white")
    M = add.layer()
    assert add.stats(M)["colors"] == 2
    add.revolve(lambda t: [1, t], [0, 0, 0], [0, 1, 0], 0, 2, 4, 8,
                color=lambda t, a: add.hsv(a / (2 * add.pi)))
    M = add.layer()
    assert closed(M) and add.stats(M)["colors"] >= 8
    add.sweep([[-1, -1], [1, -1], [1, 1], [-1, 1]], lambda t: [0, t, 0], 0, 3, 3,
              color=lambda t, j: ["red", "green", "blue", "gold", "white"][j])
    M = add.layer()
    assert closed(M) and add.stats(M)["colors"] == 5
    add.curve(lambda t: [t, 0, 0], 0, 1, 4, 8, 0.1,
              color=lambda t, a: "red" if a < add.pi else "blue")
    M = add.layer()
    assert closed(M) and add.stats(M)["colors"] == 2
    add.grid([0, 0, 0], [4, 4], 4, 4, color=lambda x, z: "red" if x < 0 else "blue")
    assert add.stats(add.layer())["colors"] == 2
    add.clear()


def test_revolve_wedge_is_watertight():
    add.clear()
    add.revolve(lambda t: [1.0, t], [0, 0, 0], [0, 1, 0], 0, 2, 4, 8, "red",
                angle=add.pi / 2)
    M = add.layer()
    assert closed(M), add.stats(M)
    check_volume(M, add.pi / 4 * 2, 0.06)        # a quarter of a cylinder


def test_numbers_and_profiles():
    assert add.lerp(1, 3, 0.5) == 2
    assert add.lerp([0, 0, 0], [2, 4, 6], 0.5) == [1, 2, 3]
    assert add.clamp(7, 0, 1) == 1 and add.clamp(-1, 0, 1) == 0
    assert abs(add.remap(5, 0, 10, -1, 1)) < 1e-12
    assert add.distance([0, 0, 0], [3, 4, 0]) == 5
    assert add.midpoint([0, 0], [2, 2]) == [1, 1]
    assert add.direction([0, 0, 0], [0, 5, 0]) == [0, 1, 0]
    p = add.rotate_point([1, 0, 0], [0, 1, 0], add.pi / 2)
    assert abs(p[0]) < 1e-9 and abs(p[2] + 1) < 1e-9
    assert add.shade("white", 0.5) == (127, 127, 127)
    assert len(add.chaikin([[0, 0], [1, 0], [1, 1]], 1)) == 6
    assert len(add.profile_circle(1, 12)) == 12
    assert len(add.profile_star(5, 1, 0.5)) == 10
    assert len(add.profile_rect(2, 1)) == 4
    assert len(add.profile_rect(2, 1, 0.2, 3)) == 16
    assert len(add.profile_gear(8, 1)) == 32
    assert len(add.points_on_circle([0, 0, 0], 1, 6)) == 6
    assert len(add.points_on_helix([0, 0, 0], 1, 1, 2, 9)) == 9
    assert len(add.points_on_spiral([0, 0, 0], 0, 1, 2, 9)) == 9
    assert len(add.points_on_line([0, 0, 0], [1, 0, 0], 5)) == 5
    assert len(add.points_on_curve(lambda t: [t, 0, 0], 0, 1, 5)) == 5


def test_parts_are_watertight():
    parts = {
        "beam": lambda: add.beam([0, 0, 0], [4, 3, 1], 0.3, 0.5, "brown"),
        "rounded_box": lambda: add.rounded_box([0, 0, 0], [2, 1, 3], 0.3, 6, "red"),
        "hemisphere": lambda: add.hemisphere([0, 0, 0], 1, 8, "sky"),
        "arch": lambda: add.arch([-2, 0, 0], [2, 0, 0], 2, [0.6, 0.3], "grey"),
        "arch_round": lambda: add.arch([-2, 0, 0], [2, 0, 0], 1, 0.2, "grey", 16, 8),
        "stairs": lambda: add.stairs([0, 0, 0], 5, 2, 0.25, 0.4, "grey", [1, 0, 1]),
        "gear": lambda: add.gear([0, 0, 0], 12, 1, 0.3, "gold"),
        "gear_hole": lambda: add.gear([0, 0, 0], 12, 1, 0.3, "gold", hole=0.3),
        "wheel": lambda: add.wheel([0, 0, 0], 1, 0.4),
        "wheel_spokes": lambda: add.wheel([0, 0, 0], 1, 0.3, spokes=6),
        "roof": lambda: add.roof([0, 2, 0], [4, 6], 1.5, "red", 0.3),
        "column": lambda: add.column([0, 0, 0], 4, 0.3, "white", 12),
        "bricks": lambda: add.bricks([0, 0, 0], 4, 1.5, seed=1),
        "tree": lambda: add.tree([0, 0, 0], 3, seed=1),
        "pine": lambda: add.tree([0, 0, 0], 3, kind="pine"),
        "palm": lambda: add.tree([0, 0, 0], 3, kind="palm", seed=2),
        "pixels": lambda: add.pixels([".r.", "rrr", ".r."], 0.5),
        "heightmap": lambda: add.heightmap([[1, 2, 3], [2, 3, 1]], 0.5),
        "polyline": lambda: add.polyline([[0, 0, 0], [1, 0, 0], [1, 1, 0]], 0.1, 8, "red", smooth=1),
        "polyline_closed": lambda: add.polyline([[0, 0, 0], [1, 0, 0], [1, 1, 0]], 0.1, 8, "red", closed=True),
        "text": lambda: add.text("AB", [0, 0, 0], 1, color="navy", k=6),
    }
    for name, draw in parts.items():
        add.clear()
        draw()
        M = add.layer()
        assert M.polygons > 0, name
        assert closed(M), (name, add.stats(M))
        assert add.volume(M) > 0, name
    add.clear()


def test_beam_dimensions():
    add.clear()
    add.beam([0, 0, 0], [5, 0, 0], 0.5, 1.0, "brown")
    M = add.layer()
    check_volume(M, 5 * 0.5 * 1.0)
    lo, hi = add.bbox(M)
    assert abs(hi[1] - lo[1] - 1.0) < 1e-9 and abs(hi[2] - lo[2] - 0.5) < 1e-9
    add.beam([0, 0, 0], [0, 4, 0], 0.5, "brown")              # straight up
    M = add.layer()
    check_volume(M, 4 * 0.25)


def test_stairs_volume():
    add.clear()
    add.stairs([0, 0, 0], 4, 2, 0.5, 1.0, "grey")
    M = add.layer()
    check_volume(M, (1 + 2 + 3 + 4) * 0.5 * 1.0 * 2)
    assert add.stats(M)["open_edges"] == 0


def test_pixels_and_heightmap_counts():
    add.clear()
    add.pixels(["#.", ".#"], 1.0)
    M = add.layer()
    assert M.polygons == 12                  # two cubes touching at an edge
    add.pixels(["rg", "by"], 1.0)
    assert add.stats(add.layer())["colors"] == 4
    add.heightmap([[2, 0], [0, 1]], 1.0, color=lambda i, j, k: "sky" if j == 0 else "white")
    M = add.layer()
    check_volume(M, 3.0)
    assert add.stats(M)["colors"] == 2


def test_wireframe_and_flow():
    add.clear()
    add.box([0, 0, 0], 1, "red")
    B = add.layer()
    add.wireframe(B, 0.05, 6)
    M = add.layer()
    assert M.polygons == 12 * (6 + 2 * 6) + 8 * 20
    pts = add.flow(lambda p: [0, 1, 0], [0, 0, 0], 0.1, 10)
    assert len(pts) == 11 and abs(pts[-1][1] - 1.0) < 1e-9
    add.trace(lambda p: [1, 0, 0], [0, 0, 0], 0.1, 10, 0.1, 6, "red")
    M = add.layer()
    assert closed(M)
    add.clear()


def test_aim_ground_align():
    add.clear()
    add.cone([0, 0, 0], [0, 2, 0], 0.5, 12, "red")
    C = add.layer()
    A = add.aim(C, [1, 0, 0])
    lo, hi = add.bbox(A)
    assert abs(hi[0] - 2.0) < 1e-9 and abs(hi[1] - 0.5) < 1e-6
    assert add.bbox(add.aim(C, [0, 1, 0]))[1][1] == 2.0           # already aimed
    D = add.aim(C, [0, -1, 0])                                     # exact opposite
    assert abs(add.bbox(D)[0][1] + 2.0) < 1e-9
    G = add.ground(C, 5)
    assert abs(add.bbox(G)[0][1] - 5) < 1e-9
    E = add.align(C, [1, 2, 3], [1, 1, 1])
    assert [round(x, 9) for x in add.bbox(E)[1]] == [1, 2, 3]
    F = add.align(C, [0, 0, 0])
    lo, hi = add.bbox(F)
    assert abs(lo[1]) < 1e-9 and abs(lo[0] + hi[0]) < 1e-9


def test_scatter_and_along():
    add.clear()
    add.box([0, 0.5, 0], 1, "red")
    B = add.layer()
    pts = add.random_points(10, [-5, 0, -5], [5, 0, 5], seed=4,
                            height=lambda x, z: 2.0)
    assert len(pts) == 10 and all(p[1] == 2.0 for p in pts)
    assert pts == add.random_points(10, [-5, 0, -5], [5, 0, 5], seed=4,
                                    height=lambda x, z: 2.0)
    S = add.scatter(B, pts, seed=1, scale=(0.5, 1.5))
    assert S.polygons == 60
    A = add.along(B, lambda t: [t, 0, 0], 5, 0, 8)
    assert A.polygons == 30
    A = add.along(B, [[0, 0, 0], [1, 0, 0], [2, 0, 0]], 3, axis=None, scale=2)
    assert A.polygons == 18 and abs(add.bbox(A)[1][1] - 2.0) < 1e-9
    A = add.along(B, lambda t: [add.cos(t), 0, add.sin(t)], 6, 0, 2 * add.pi,
                  closed=True)
    assert A.polygons == 36


def test_text():
    add.clear()
    w = add.text("ABC", [0, 0, 0], 1.0, color="navy", k=6)
    M = add.layer()
    assert M.polygons > 100 and w > 2.0
    assert abs(add.text_width("ABC") - w) < 1e-9
    assert add.text_width("I") < add.text_width("W")
    add.text("ąčęėįšųūž 0-9!?", [0, 0, 0], 1.0, color="navy", k=6)
    assert add.layer().polygons > 0
    add.text("two\nlines", [0, 0, 0], 1.0, align="center", u=[1, 0, 0], v=[0, 0, -1])
    lo, hi = add.bbox(add.layer())
    assert hi[1] - lo[1] < 0.5 and lo[2] < 0 < hi[2]
    assert add.write is add.text and add.label is add.text
    add.clear()


# --------------------------------------------------------------------------
#  2.0: regular polyhedra, geodesic sphere, vertex tools, subdivision,
#  named surfaces, Sketchfab limits
# --------------------------------------------------------------------------

def test_regular_polyhedra():
    expect = {"tetrahedron": (4, 4, 3), "cube": (8, 6, 3), "octahedron": (6, 8, 4),
              "dodecahedron": (20, 12, 3), "icosahedron": (12, 20, 5)}
    for name, (nv, nf, val) in expect.items():
        M = add.make(add.polyhedron, name, [1, 2, 3], 2.0, "red")
        s = add.stats(M)
        assert (s["vertices"], s["faces"]) == (nv, nf), name
        assert s["closed"] and add.volume(M) > 0
        # every vertex on the sphere of radius r, average exactly at the centre
        P = add.polyhedron_points(name, [1, 2, 3], 2.0)
        assert len(P) == nv
        for p in P:
            assert abs(add.distance(p, [1, 2, 3]) - 2.0) < 1e-9
        mean = [sum(p[a] for p in P) / nv for a in range(3)]
        assert max(abs(mean[a] - [1, 2, 3][a]) for a in range(3)) < 1e-12
        assert add.valence(M, 0) == val
        L = add.edge_lengths(M)
        assert max(L) - min(L) < 1e-9                 # all edges equal
        assert len(add.polyhedron_faces(name)) == nf
    for fn, nf in ((add.tetrahedron, 4), (add.octahedron, 8),
                   (add.dodecahedron, 12), (add.icosahedron, 20)):
        assert add.make(fn, [0, 0, 0], 1, "red").polygons == nf
    # duals: cube <-> octahedron, dodecahedron <-> icosahedron
    cube = add.make(add.polyhedron, "cube")
    assert add.dual(cube).polygons == 8 and closed(add.dual(cube))
    ico = add.make(add.icosahedron)
    assert add.dual(ico).polygons == 12 and closed(add.dual(ico))
    assert add.dual(add.make(add.tetrahedron)).polygons == 4


def test_geodesic_sphere():
    add.clear()
    for level, faces, verts in ((0, 20, 12), (1, 80, 42), (2, 320, 162),
                                (3, 1280, 642)):
        M = add.make(add.icosphere, [0, 0, 0], 1.0, level, "red")
        s = add.stats(M)
        assert (s["faces"], s["vertices"]) == (faces, verts)
        assert s["closed"] and all(len(f) == 3 for f in M.F)
        for p in M.V:
            assert abs(add.distance(p, [0, 0, 0]) - 1.0) < 1e-12
    # sphere(): the old detail number picks a level; k=10 -> 1280 triangles
    for k, faces in ((1, 20), (3, 80), (5, 320), (10, 1280), (20, 5120)):
        assert add.make(add.sphere, [0, 0, 0], 1, k).polygons == faces
    assert add.make(add.sphere, [0, 0, 0], 1, 10, subdivisions=1).polygons == 80
    M = add.make(add.sphere, [2, 0, 0], 1.5, 20, "sky")
    check_volume(M, 4.0 / 3 * math.pi * 1.5 ** 3, 0.01)
    assert closed(M) and add.ball is add.sphere
    # painting by direction
    M = add.make(add.icosphere, [0, 0, 0], 1, 2,
                 lambda d: "white" if d[1] > 0 else "blue")
    assert add.stats(M)["colors"] == 2
    # the old quad sphere is still there
    Q = add.make(add.quadsphere, [0, 0, 0], 1, 10, "red")
    assert Q.polygons == 600 and closed(Q) and all(len(f) == 4 for f in Q.F)


def test_vertex_tools():
    cube = add.make(add.box, [0, 0, 0], 2, "red")
    assert len(add.edges(cube)) == 12
    assert abs(add.mean_edge_length(cube) - 2.0) < 1e-12
    assert abs(add.edge_length(cube, *add.edges(cube)[0]) - 2.0) < 1e-12
    assert add.adjacency(cube)[0] == add.neighbors(cube, 0) or \
        sorted(add.adjacency(cube)[0]) == sorted(add.neighbors(cube, 0))
    assert len(add.neighbors(cube, 0)) == 3 == add.valence(cube, 0)
    assert abs(add.mean_neighbor_distance(cube, 0) - 2.0) < 1e-12
    assert len(add.vertex_faces(cube, 0)) == 3
    i = add.nearest_vertex(cube, [1, 1, 1])
    assert add.vertex(cube, i) == [1.0, 1.0, 1.0]
    moved = add.set_vertex(cube, i, [None, 3, None])
    assert add.vertex(moved, i) == [1.0, 3.0, 1.0] and add.vertex(cube, i)[1] == 1.0
    moved = add.move_vertex(cube, i, [1, 1, 1])
    assert add.vertex(moved, i) == [2.0, 2.0, 2.0]
    moved = add.set_vertices(cube, {0: [0, 0, 0], 1: [None, None, 9]})
    assert add.vertex(moved, 0) == [0.0, 0.0, 0.0] and add.vertex(moved, 1)[2] == 9.0
    n = add.vertex_normal(cube, i)
    assert abs(add.distance(n, [0, 0, 0]) - 1.0) < 1e-9 and n[0] > 0 and n[1] > 0
    assert abs(add.face_area(cube, 0) - 4.0) < 1e-9
    assert len(add.face_centers(cube)) == 6
    c, nrm = add.face_center(cube, 0), add.face_normal(cube, 0)
    assert abs(add.distance(c, [0, 0, 0]) - 1.0) < 1e-9
    assert abs(sum(c[a] * nrm[a] for a in range(3)) - 1.0) < 1e-9   # outward
    assert add.boundary_edges(cube) == [] and add.boundary_loops(cube) == []
    sheet = add.make(add.grid, [0, 0, 0], [2, 2], 2, 2, "red")
    assert len(add.boundary_edges(sheet)) == 8
    assert len(add.boundary_loops(sheet)) == 1 and len(add.boundary_loops(sheet)[0]) == 8
    # neighbours of an icosahedron vertex go around it
    ico = add.make(add.icosahedron, [0, 0, 0], 1)
    ring = add.neighbors(ico, 0)
    assert len(ring) == 5 and add.neighbours is add.neighbors
    for k in range(5):                              # consecutive ones are joined
        assert ring[(k + 1) % 5] in add.neighbors(ico, ring[k])
    # refine / spherify / inflate / truncate / color_by_sides
    R = add.refine(cube, 2)
    assert R.polygons == 96 and closed(R) and abs(add.volume(R) - 8.0) < 1e-9
    D = add.spherify(add.refine(add.make(add.octahedron), 3))
    assert D.polygons == 512 and closed(D)
    assert all(abs(add.distance(p, [0, 0, 0]) - 1.0) < 1e-9 for p in D.V)
    big = add.inflate(cube, 0.5)
    assert add.volume(big) > 8.0 and closed(big)
    ball = add.truncate(ico, 1 / 3.0, "black")
    s = add.stats(ball)
    assert (s["vertices"], s["faces"]) == (60, 32) and s["closed"]
    sides = sorted(len(f) for f in ball.F)
    assert sides.count(5) == 12 and sides.count(6) == 20
    L = add.edge_lengths(ball)
    assert max(L) - min(L) < 1e-9                    # a regular truncation
    ball = add.color_by_sides(ball, {5: "black", 6: "white"})
    assert add.stats(ball)["colors"] == 2
    half = add.truncate(cube, 0.5)                   # cuboctahedron
    assert half.polygons == 14 and closed(half)


def test_catmull_clark():
    cube = add.make(add.box, [0, 0, 0], 2, "gold")
    S = add.catmull_clark(cube, 1)
    assert S.polygons == 24 and closed(S) and all(len(f) == 4 for f in S.F)
    assert add.stats(S)["colors"] == 1 and S.C[0] == add.rgb("gold")
    S3 = add.catmull_clark(cube, 3)
    assert S3.polygons == 384 and closed(S3)
    assert 8 * 0.25 < add.volume(S3) < 8.0            # rounded, so smaller
    assert add.subdivide is add.catmull_clark
    # a coloured control mesh keeps its colours per face
    painted = add.color_random(cube, seed=1)
    assert add.stats(add.catmull_clark(painted, 2))["colors"] == 6
    # an open sheet keeps a smooth border
    sheet = add.make(add.grid, [0, 0, 0], [4, 4], 4, 4, "red")
    S = add.catmull_clark(sheet, 2)
    assert S.polygons == 256 and add.stats(S)["open_edges"] == 64


def test_smooth_uniform_grids():
    cube = add.make(add.box, [0, 0, 0], 2, "gold")
    # n = 1: the control vertices moved to the limit surface, faces kept
    L = add.smooth(cube, 1)
    assert L.polygons == 6 and len(L.V) == 8 and closed(L)
    # for n = 2^k the grid is the classical subdivision at its limit
    def points(M):
        return sorted(tuple(round(c, 9) for c in p) for p in M.V)
    for k in (1, 2, 3):
        A = add.smooth(cube, 2 ** k, uniform=False)
        B = add.smooth(add.catmull_clark(cube, k), 1)
        assert A.polygons == B.polygons == 6 * 4 ** k
        assert points(A) == points(B)
    # any n: node counts, closedness, Euler characteristic 2 of a ball
    for n in range(1, 8):
        S = add.smooth(cube, n)
        assert closed(S), n
        q = n // 2
        cells = 6 * (4 * q * q + (4 * q + 1 if n % 2 else 0))
        assert S.polygons == cells, (n, S.polygons)
        V, E, F = len(S.V), len(add.edges(S)), len(S.F)
        assert V - E + F == 2, (n, V, E, F)
        assert add.stats(S)["colors"] == 1
    # every node lies on the limit surface: a cube's limit surface is
    # symmetric and convex, all 2^k grids are subsets of one another
    fine = points(add.smooth(cube, 8, uniform=False))
    coarse = points(add.smooth(cube, 4, uniform=False))
    assert set(coarse) <= set(fine)
    # non-quad control faces: dodecahedron and a triangle mesh
    dode = add.make(add.dodecahedron, [0, 0, 0], 1, "sky")
    S = add.smooth(dode, 5)
    assert closed(S) and S.polygons == 12 * (5 * 4 + 5 * 2 + 1)
    ico = add.make(add.icosahedron, [0, 0, 0], 1, "sky")
    S = add.smooth(ico, 4)
    assert closed(S) and S.polygons == 20 * 3 * 4
    # the boundary of an open mesh is a smooth curve: a single flat polygon
    # stays flat and keeps its corner count on the rim
    face = add.make(add.polygon, [[0, 0, 0], [2, 0, 0], [2, 2, 0], [1, 3, 0], [0, 2, 0]],
                    "red")
    for uniform in (False, True):
        S = add.smooth(face, 3, uniform=uniform)
        assert all(abs(p[2]) < 1e-12 for p in S.V)
        assert len(add.boundary_loops(S)) == 1
        assert len(add.boundary_loops(S)[0]) == 5 * 3
    # options run and give the same counts
    S1 = add.smooth(dode, 3, uniform=True, centre=False, p=3.0, scale=0.5)
    assert S1.polygons == add.smooth(dode, 3).polygons and closed(S1)
    # meshes that only touch are cut apart, not refused
    add.clear()
    add.voxels([(0, 0, 0), (1, 1, 0)], 1, color="red")
    vox = add.layer()
    S = add.smooth(vox, 2)
    assert closed(S) and S.polygons == 2 * 24
    # a mesh with a moved corner (the classroom use case)
    block = add.set_vertex(cube, add.nearest_vertex(cube, [1, 1, 1]), [3, 3, 3])
    S = add.smooth(block, 6)
    assert closed(S) and add.bbox(S)[1][0] > 1.1     # the plain cube stays under 0.8


def test_named_surfaces():
    names = add.surface_names()
    assert len(names) == 25 and "klein_bottle" in names and names == sorted(names)
    for name in names:
        M = add.make(add.surface, name, [0, 0, 0], 2.0, 12, "red")
        assert M.polygons > 0, name
        assert abs(max(add.size(M)) - 2.0) < 1e-9, name
        for p in M.V:
            assert all(abs(c) < 10 for c in p), name
    f = add.surface_function("pillow", a=2.0)
    assert abs(f(math.pi / 2, math.pi / 2)[2] - 2.0) < 1e-12
    M = add.make(add.surface, "sine_surface", [5, 0, 0], grid=[10, 20], color="red")
    assert M.polygons == 200 and closed(M)
    assert abs(add.middle(M)[0] - 5.0) < 1e-9
    M = add.make(add.surface, "enneper", size=1, grid=8, thickness=0.05)
    assert closed(M)
    M = add.make(add.surface, "apple", grid=8, color=lambda u, v: add.hsv(u))
    assert add.stats(M)["colors"] > 3
    assert set(add.SURFACES["dini"]) >= {"f", "u", "v", "wrap", "grid", "note", "params"}


def test_sketchfab_limits():
    add.clear()
    add.sphere([0, 0, 0], 1, 10)
    M = add.color_by(add.layer(), lambda p: add.hsv(p[1]))
    assert add.stats(M)["colors"] > 50
    assert len(add.palette(M)) == add.stats(M)["colors"]
    assert add.palette(M)[0][1] >= add.palette(M)[-1][1]
    small = add.limit_colors(M, 50)
    assert add.stats(small)["colors"] <= 50 and small.polygons == M.polygons
    assert add.stats(add.limit_colors(M, 5))["colors"] <= 5
    assert add.stats(add.limit_colors(add.make(add.box, [0, 0, 0], 1, "red"), 5))["colors"] == 1
    # obj_size predicts the written file to within a few bytes
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "m.obj")
        add.save(path, M, colors=50)
        assert abs(os.path.getsize(path) - add.obj_size(small)) < 40
        assert add.stats(add.load(path))["colors"] <= 50
    assert add.stats(M)["obj_bytes"] == add.obj_size(M)
    # check() reports the Sketchfab limits
    assert not add.check(M, min_faces=10, quiet=True)          # too many colours
    assert add.check(small, min_faces=10, quiet=True)
    assert not add.check(small, min_faces=10, quiet=True, max_mb=0.01)
    assert add.SKETCHFAB_MB == 50 and add.SKETCHFAB_COLORS == 50


def test_transparency_and_textures():
    # colours with an opacity
    assert add.rgb([10, 20, 30]) == (10, 20, 30)
    assert add.rgb([10, 20, 30, 0.5]) == (10, 20, 30, 0.5)
    assert add.rgb([10, 20, 30, 1.0]) == (10, 20, 30)          # solid = plain
    assert add.rgb("#ff000080") == (255, 0, 0, 0.502)
    assert add.transparent("red", 0.25) == (255, 0, 0, 0.25)
    assert add.transparent(add.transparent("red", 0.25), 1) == (255, 0, 0)
    add.clear()
    add.box([0, 0, 0], 1, add.transparent("sky", 0.4))
    add.box([3, 0, 0], 1, "sky")
    M = add.layer()
    s = add.stats(M)
    assert s["transparent_faces"] == 6 and s["colors"] == 2 and s["textures"] == []
    G = add.opacity(M, 0.5)
    assert add.stats(G)["transparent_faces"] == 12 and add.stats(G)["colors"] == 1
    assert add.stats(add.opacity(G, 1))["transparent_faces"] == 0
    # the old string API and .off output only see r g b
    assert M.face_strings()[0].split()[-3:] == ["120", "190", "255"]
    # textures: coordinates per corner, kept through transforms and clean()
    with tempfile.TemporaryDirectory() as folder:
        png = os.path.join(folder, "check.png")
        rows = [["white" if (x // 4 + y // 4) % 2 else "black" for x in range(16)]
                for y in range(16)]
        add.write_png(png, rows)
        assert os.path.getsize(png) > 50
        wall = add.texture(add.make(add.cuboid, [0, 0, 0], [4, 2, 1], "red"),
                           "check.png", "box", scale=2.0)
        assert wall.UV is not None and len(wall.UV) == 6
        assert all(len(uv) == 4 for uv in wall.UV)
        assert wall.C[0] == (255, 255, 255, 1.0, "check.png")
        assert add.stats(wall)["textures"] == ["check.png"]
        moved = add.clean(add.mirror(add.move(wall, [1, 2, 3])))
        assert moved.UV is not None and len(moved.UV) == 6 and moved.UV[0] is not None
        tri = add.triangulate(wall)
        assert len(tri.UV) == 12 and len(tri.UV[0]) == 3
        both = add.merge([wall, add.make(add.box, [9, 0, 0], 1, "red")])
        assert len(both.UV) == 12 and both.UV[6] is None
        for mapping in ("xy", "xz", "yz", "fit", "sphere", "cylinder",
                        lambda p, n: (p[0], p[1])):
            T = add.texture(add.make(add.sphere, [0, 0, 0], 1, 5), "check.png",
                            mapping)
            assert len(T.UV) == T.polygons
        tinted = add.texture(add.opacity(wall, 0.5), "check.png", color="red")
        assert tinted.C[0] == (255, 0, 0, 0.5, "check.png")
        # .obj + .mtl round trip: d, map_Kd, vt and f v/vt
        path = os.path.join(folder, "t.obj")
        scene = add.merge([wall, add.opacity(add.make(add.box, [9, 0, 0], 1, "sky"), 0.3)])
        add.save(path, scene)
        text = open(path).read()
        mtl = open(os.path.join(folder, "t.mtl")).read()
        assert "vt " in text and "/" in text.split("\nf ")[1]
        assert "map_Kd check.png" in mtl and "d 0.300" in mtl and "d 1.000" in mtl
        assert abs(os.path.getsize(path) - add.obj_size(scene)) < 80
        back = add.load(path)
        assert add.stats(back)["textures"] == ["check.png"]
        assert add.stats(back)["transparent_faces"] == 6
        assert back.UV is not None and back.UV[0] is not None
        # .off keeps colours only, and plain models are written as before
        off = os.path.join(folder, "t.off")
        add.save(off, scene)
        assert add.stats(add.load(off))["textures"] == []
        add.save(off, add.make(add.box, [0, 0, 0], 1, "red"))
        assert "255 0 0" in open(off).read()
    # limit_colors leaves glass and textures alone
    many = add.color_by(add.make(add.sphere, [0, 0, 0], 1, 10), lambda p: add.hsv(p[1]))
    mixed = add.merge([many, wall, add.opacity(add.make(add.box, [5, 0, 0], 1, "sky"), 0.3)])
    few = add.limit_colors(mixed, 10)
    assert add.stats(few)["colors"] <= 12 and add.stats(few)["textures"] == ["check.png"]
    assert add.stats(few)["transparent_faces"] == 6


def test_stream():
    """A model written part by part is the same model as one saved at once."""
    with tempfile.TemporaryDirectory() as folder:
        png = os.path.join(folder, "dots.png")
        add.write_png(png, [["red" if (x + y) % 2 else "white" for x in range(4)] for y in range(4)])
        parts = [add.make(add.box, [0, 0, 0], 1, "red"),
                 add.texture(add.make(add.cuboid, [3, 0, 0], [2, 1, 1]), "dots.png", "box"),
                 add.opacity(add.make(add.sphere, [6, 0, 0], 1, 8, "sky"), 0.4)]
        whole = add.merge(parts)
        for ext in (".obj", ".off"):
            path = os.path.join(folder, "s" + ext)
            with add.stream(path) as out:
                assert isinstance(out, add.Stream)
                add.clear()
                add.mesh(parts[0])
                n = out.add()                             # the scene, then cleared
                assert n == 6 and add.layer().polygons == 0
                out.add(parts[1])
                out.add(parts[2])
            assert out.faces == whole.polygons and out.vertices == len(whole.V)
            assert 0 < out.bytes <= os.path.getsize(path)
            back = add.load(path)
            assert back.polygons == whole.polygons and len(back.V) == len(whole.V)
            assert abs(add.volume(back) - add.volume(whole)) < 1e-6
            if ext == ".obj":
                assert len(out.materials) == 3 and add.stats(back)["textures"] == ["dots.png"]
                assert add.stats(back)["transparent_faces"] == parts[2].polygons
                mtl = open(os.path.join(folder, "s.mtl")).read()
                assert "map_Kd dots.png" in mtl and "d 0.400" in mtl
            else:
                assert add.stats(back)["colors"] == 3
                header = open(path).read().split("\n")[1].split()
                assert int(header[0]) == len(whole.V) and int(header[1]) == whole.polygons
        try:
            out.add(parts[0])                             # closed
            assert False, "writing to a closed stream must fail"
        except ValueError:
            pass


def test_concave_faces():
    """A face that is not convex is cut into triangles that cover exactly
    the polygon (a viewer's fan would cover its notch); convex faces stay."""
    L = [(0, 0), (4, 0), (4, 1), (1, 1), (1, 3), (0, 3)]
    M = add.Mesh()
    top = [M.add_vertex([x, 1.0, z]) for x, z in L]
    bot = [M.add_vertex([x, 0.0, z]) for x, z in L]
    M.add_face(top, "red")
    M.add_face(bot[::-1], "red")
    for i in range(6):
        j = (i + 1) % 6
        M.add_face([bot[i], bot[j], top[j], top[i]], "red")
    M = add.fix_normals(M)
    assert add.concave_faces(M) == 2
    C, info = add.clean(M, report=True)
    assert info["faces_split"] == 2 and add.concave_faces(C) == 0
    assert abs(add.area(C) - 26.0) < 1e-9                  # 2 x 6 (the L) + 14 (its sides)
    assert abs(add.volume(C) - 6.0) < 1e-9 and add.stats(C)["closed"]
    assert add.clean(add.make(add.cuboid, [0, 0, 0], [1, 2, 3], "blue")).polygons == 6


def test_overlaps_and_pinched_faces():
    """clean() cuts back coplanar overlapping faces (the cause of flicker),
    splits faces pinched at a vertex, and save() does the same on the way
    to the file; check() and overlaps() report them."""
    tall = add.make(add.cuboid, [0, 0, 0], [2, 6, 1], "red")
    wide = add.make(add.cuboid, [0, 0, 0], [5, 1, 1], "blue")     # the front faces share a plane
    M = add.merge([tall, wide])
    assert add.overlaps(M) == 2                                    # front and back of the wide box
    C, info = add.clean(M, report=True)
    assert info["faces_cut"] == 2 and add.overlaps(C) == 0
    # the smaller face was cut into the two stubs outside the tall box; area is kept
    front = [f for f in C.F if all(abs(C.V[i][2] - 0.5) < 1e-9 for i in f)]
    assert len(front) == 3
    assert abs(add.area(C) - (add.area(M) - 2 * 2 * 1)) < 1e-9      # minus the two hidden 2x1 patches
    # a face that is not overlapped is left exactly as it was
    assert add.clean(tall).polygons == 6
    # a box standing on a floor: the patch they share is cut out of both and
    # the union is watertight; a floor under many boxes is left alone
    floor = add.make(add.cuboid, [0, 0, 0], [10, 1, 10], "grey")
    box = add.make(add.cuboid, [2, 1, 2], [2, 1, 2], "red")
    assert add.overlaps(add.merge([floor, box])) == 2
    U, info = add.clean(add.merge([floor, box]), report=True)
    assert info["faces_cut"] == 2 and add.stats(U)["closed"] and abs(add.volume(U) - 104) < 1e-9
    crowd = [floor] + [add.make(add.cuboid, [-4.5 + i * 0.8, 0.75, -4.5 + j * 0.8], [0.5, 0.5, 0.5], "red")
                       for i in range(12) for j in range(12)]
    U, info = add.clean(add.merge(crowd), report=True)
    assert info["faces_cut"] == 0 and add.stats(U)["closed"]
    # a face pinched at a vertex (a bow tie) is split into its two loops
    P = add.Mesh()
    for q in ([0, 0, 0], [1, 0, 0], [1, 1, 0], [-1, 0, 0], [-1, -1, 0]):
        P.add_vertex(q)
    P.add_face([0, 1, 2, 0, 3, 4], "red")
    assert sorted(len(f) for f in add.clean(P).F) == [3, 3]
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "o.obj")
        add.save(path, M)
        back = add.load(path)
        assert add.overlaps(back) == 0 and back.polygons == C.polygons
        add.save(path, M, clean=False)
        assert add.overlaps(add.load(path)) == 2
        with add.stream(os.path.join(folder, "s.obj")) as out:
            out.add(M)
        assert out.cut == 2
        add.save(path, P)
        for line in open(path):
            if line.startswith("f "):
                idx = line.split()[1:]
                assert len(set(idx)) == len(idx)                    # no repeated index in any face
    # the report in check()
    import io
    import contextlib
    text = io.StringIO()
    with contextlib.redirect_stdout(text):
        add.check(M, min_faces=1, min_colors=1)
    assert "overlapping faces   2" in text.getvalue()


def test_make_and_every_public_name():
    ball = add.make(add.sphere, [0, 0, 0], 1, 5, "red")
    assert ball.polygons == 320 and len(add.faces) == 0
    add.box([0, 0, 0], 1, "red")
    part = add.make(add.box, [0, 0, 0], 1, "blue")       # the scene is untouched
    assert len(add.faces) == 6 and part.polygons == 6
    add.clear()
    # every public name is documented and, if callable, has a docstring
    for name in add.__all__:
        obj = getattr(add, name)
        if callable(obj) and not isinstance(obj, type):
            assert obj.__doc__, name
    assert add.__version__ == "2.0"


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

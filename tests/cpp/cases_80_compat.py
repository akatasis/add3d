from parity_case import add, case, record, run, save_case, save_mesh  # noqa: F401
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def ported(section):
    """Is section NN_name of add.hpp there?  (See the .cpp: the cases that need a section
    that is still being ported run once that section's own tests are here too.)"""
    return bool(os.environ.get("PARITY_PENDING")) or os.path.exists(os.path.join(HERE, "cases_%s.cpp" % section))


WITH_60_70 = ported("60_boolean") and ported("70_io")      # demo: difference(), save()


def from_list(pts):
    """The points of a list one after the other -- what add.hpp's revolve does with a list
    of [radius, height] points (add.py itself wants a function)."""
    it = iter(pts)
    return lambda t: next(it)


@case
def old_names():
    add.newface([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], "red")
    add.newface([[0, 0, 1], [1, 0, 1], [0.5, 1, 1.5]], (0.2, 0.4, 0.6))
    add.cube([3, 0, 0], 1.5, "blue")
    add.rectangle3D([6, 0, 0], [1, 2, 3], (10, 20, 30))
    add.cube2([0, 4, 0], 2.0, 0.2, "gold")
    add.cylinder2([3, 4, 0], [3, 6, 0], 0.5, 8, "teal")
    add.cylinder3([6, 4, 0], [7, 5, 1], 0.4, 6, "navy")
    add.cone2([9, 4, 0], [9, 6, 0], 0.6, 7, "pink")
    save_case()


@case
def other_names():
    add.ball([0, 0, 0], 1.0)
    add.ball([3, 0, 0], 0.5, 5, "red")
    add.ball([6, 0, 0], 0.7, 10, lambda d: "white" if d[1] > 0.5 else "blue", 1)
    add.ball([9, 0, 0], 0.4, 3, None, 0)
    add.block([0, 3, 0], [1, 2, 3], "gold")
    add.block([3, 3, 0], [0.5, 0.5, 0.5])
    add.cuboid3D([6, 3, 0], [2, 1, 1], "teal")
    add.cuboid3D([9, 3, 0], [1, 1, 1])
    save_case()


@case
def lathes():
    add.lathe(lambda t: [0.5 + 0.2 * math.sin(3 * t), t], [0, 0, 0], [0, 1, 0], 0, 2, 12, 10, "red")
    add.solid_of_revolution(lambda t: [1 - 0.5 * t, t], [3, 0, 0], [3, 1, 0], 0, 1, 4, 8,
                            lambda t, a: add.hsv(a / 6.0))
    pts = [[0.0, 0.0], [1.0, 0.0], [1.2, 0.5], [0.8, 1.0], [0.0, 1.2]]
    add.lathe(from_list(pts), [6, 0, 0], [6, 1, 0], 0, 1, len(pts) - 1, 9, "gold")
    add.solid_of_revolution(from_list(pts[1:4]), [9, 0, 0], [9, 2, 0], 0.5, 1.5, 2, 7, "blue", math.pi)
    add.lathe(lambda t: [0.3, t])
    add.solid_of_revolution(lambda t: [0.4 + 0.1 * t, t], [0, 4, 0], [1, 5, 0])
    add.lathe(from_list(pts[1:4]), [3, 4, 0], [3, 5, 0], 0, 1, 2, 6, "teal", 2 * math.pi, False)
    add.solid_of_revolution(lambda t: [0.5, t], [6, 4, 0], [6, 5, 0], 0, 1, 3, 5, "red", 1.5, False)
    save_case()


@case
def mesh_names():
    add.box([0, 0, 0], 1, "red")
    add.box([0.5, 0, 0], 1, "blue")
    add.box([0.25, 0.25, 0.25], 0.5, "gold")
    M = add.layer()
    save_mesh(add.weld(M), "weld")
    save_mesh(add.weld(M, 1e-3, True, True, True, True, True, True), "weld_normals")
    save_mesh(add.weld(M, 1e-7, False, False, False, False, False, False, False, False, False), "weld_nothing")
    W, info = add.weld(M, 1e-7, True, True, True, True, True, False, True)
    for key in ("vertices_removed", "faces_removed", "faces_cut", "faces_split"):
        record(info[key])
    save_mesh(W, "weld_report")
    save_mesh(add.scale(M, 2.0), "scale")
    save_mesh(add.scale(M, -0.5, [1, 1, 1]), "scale_about")
    save_mesh(add.translate(M, [1, 2, 3]), "translate")
    save_mesh(add.reflect(M), "reflect")
    save_mesh(add.reflect(M, [1, 0, 0], [1, 1, 0]), "reflect_plane")


@case
def weld_scene():
    add.box([0, 0, 0], 1, "red")
    add.box([1, 0, 0], 1, "red")
    save_mesh(add.weld(), "weld")
    save_case()                               # the scene is left as it was


# -- demo (needs difference: section 60, and save: write_ply / write_stl of section 70) ----

if WITH_60_70:
    @case
    def demo_model():
        record(add.demo())                    # writes demo.off (about half a minute in Python)
        save_case()                           # demo() leaves the scene empty


if __name__ == "__main__":
    import sys
    run(sys.argv)

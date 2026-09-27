from parity_case import add, case, record, run, save_case  # noqa: F401
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def ported(section):
    """Is section NN_name of add.hpp there?  (See the .cpp: the cases that need a section
    that is still being ported run once that section's own tests are here too.)"""
    return bool(os.environ.get("PARITY_PENDING")) or os.path.exists(os.path.join(HERE, "cases_%s.cpp" % section))


WITH_40 = ported("40_transform")  # surface: fit()


def raises(fn, *args):
    """Record whether fn(*args) raises (an exception would end the case)."""
    try:
        fn(*args)
    except Exception:                 # noqa: BLE001
        record("raises")
        return
    record("returns")


@case
def names():
    names = add.surface_names()
    record(len(names))
    for name in names:
        record(name)
    record(len(add.SURFACES))
    for name in add.SURFACES:                 # the dictionary's own order
        record(name)
    record("apple" in add.SURFACES)
    record("nope" in add.SURFACES)


@case
def catalogue():
    for name in add.surface_names():
        e = add.SURFACES[name]
        record(name)
        record([float(x) for x in e["u"]])
        record([float(x) for x in e["v"]])
        record(e["wrap"][0])
        record(e["wrap"][1])
        record(e["grid"][0])
        record(e["grid"][1])
        record(e["note"])
        record(e["flip"])
        for key in sorted(e["params"]):
            record(key)
            record(float(e["params"][key]))


@case
def functions():
    for name in add.surface_names():
        f = add.surface_function(name)
        e = add.SURFACES[name]
        (u0, u1), (v0, v1) = e["u"], e["v"]
        for a, b in ((0.0, 0.0), (0.25, 0.3), (0.5, 0.5), (0.8, 0.9), (1.0, 1.0), (0.37, 0.61)):
            u = u0 + (u1 - u0) * a
            v = v0 + (v1 - v0) * b
            record(name)
            record([float(c) for c in f(u, v)])


@case
def functions_params():
    f = add.surface_function("bohemian_dome", a=0.8, c=2)
    record([float(c) for c in f(1.0, 2.0)])
    f = add.surface_function("horn", b=2.0)
    record([float(c) for c in f(0.5, 1.0)])
    f = add.surface_function("klein_bottle", a=3.0, b=8.0)
    record([float(c) for c in f(1.0, 2.0)])
    record([float(c) for c in f(4.0, 2.0)])
    f = add.surface_function("antisymmetric_torus", R=3.0, r=1.0, a=0.5)
    record([float(c) for c in f(0.3, 0.7)])
    f = add.surface_function("twisted_eight_torus", r=0.25)
    record([float(c) for c in f(5.0, 1.0)])
    f = add.surface_function("mobius", R=1.0)
    record([float(c) for c in f(2.0, 0.25)])
    f = add.surface_function("enneper")
    record([float(c) for c in f(0.5, -1.5)])
    f = add.surface_function("hyperbolic_helicoid", a=1.0)
    record([float(c) for c in f(-1.0, 2.0)])
    f = add.surface_function("worm", b=3.0)
    record([float(c) for c in f(10.0, 1.0)])


@case
def function_errors():
    f = add.surface_function("dini", z=1.0)
    record("made")
    raises(f, 1.0, 1.0)
    f = add.surface_function("enneper", a=1.0)
    record("made")
    raises(f, 0.5, 0.5)
    raises(add.surface_function, "nope")
    f = add.surface_function("pillow", a=0.9)
    raises(f, 1.0, 1.0)


# -- surface (needs fit: section 40) ---------------------------------------------------

if WITH_40:
    @case
    def surfaces_all():
        for i, name in enumerate(add.surface_names()):
            add.surface(name, [4 * i, 0, 0], 3, 8)
        save_case()

    @case
    def surface_options():
        add.surface("pillow")
        add.surface("klein_bottle", [10, 0, 0], 4, [12, 6], "teal")
        add.surface("dini", [20, 0, 0], 4, 10, lambda u, v: add.hsv(u / 12))
        add.surface("pillow", [0, 10, 0], 3, 6, "red", 0.1)
        add.surface("mobius", [10, 10, 0], 2, [20, 4], "blue", 0.0, True)
        add.surface("horn", [20, 10, 0], None, 8, "gold", a=2.0, c=0.5)
        add.surface("cosine_surface", [0, 20, 0], 2, 6)
        add.surface("sine_surface", [10, 20, 0], 2, [5, 7], lambda u, v: add.random_color())
        add.surface("snail", [20, 20, 0], 0.5, 9, "navy", -0.05, False, )
        save_case()

    @case
    def surface_errors():
        raises(add.surface, "nope")
        raises(lambda: add.surface("dini", [0, 0, 0], 2, 4, z=1.0))   # (it leaves the scene pushed)
        record(len(add.pop().F))
        add.box([0, 0, 0], 1)
        save_case()


if __name__ == "__main__":
    import sys
    run(sys.argv)

from parity_case import add, case, record, run, save_case  # noqa: F401


@case
def numbers():
    xs = [0.1, 1e-5, 2.5, -3.0, 1.0 / 3, 1e16, 123456789.123456789, -0.0, 5e-324, 0.000123, 1e15 + 0.5]
    for x in xs:
        record(add._num(x))
    for x in xs:
        record(x)


@case
def colors():
    record(add.rgb("red"))
    record(add.rgb("#78beff66"))
    record(add.rgb((1.0, 0.5, 0.25)))
    record(add.rgb((2.0, 0.5, 0.25)))
    record(add.rgb((300, -5, 128)))
    record(add.transparent("sky", 0.35))
    record(add.hsv(0.3))
    record(add.hsv(-0.25, 0.5, 0.8))
    record(add.gradient(0.3, "red", "blue"))
    record(add.random_color(7))


@case
def random_numbers():
    add.seed(7)
    for i in range(5):
        record(add.random())
    for i in range(5):
        record(add.randint(1, 6))
    for i in range(5):
        record(add.uniform(-2.0, 3.0))
    add.seed(-12345678901)
    record(add.random())
    record(add.randint(0, 1000000000000))


@case
def mesh_basics():
    M = add.Mesh()
    M.add_polygon([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0.5, 1.5, 0], [0, 1, 0]], "red")
    M.add_polygon([[0, 0, 1], [1, 0, 1], [1, 1, 1]], add.transparent("blue", 0.25))
    add.mesh(M)
    add.push()
    add.mesh(add.move(M, [2, 0, 0]))
    moved = add.pop()
    add.mesh(add.rotateY(moved, 0.7, [1, 0, 0]))
    save_case()


@case
def gauss_numbers():
    add.seed(3)
    for i in range(5):
        record(add.gauss(2.5, 1.2))
    r = add.Random(11)
    a, b, c = r.gauss(2.5, 1.2), r.gauss(2.5, 1.2), r.gauss()
    record(a); record(b); record(c)
    r.seed(11)
    record(r.gauss(2.5, 1.2))


if __name__ == "__main__":
    import sys
    run(sys.argv)

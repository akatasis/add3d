"""
20 -- the eight examples that used to live inside add.py 1.2.

They are kept here, lightly tidied and using the new function names, so
that older course material still has something to point at.  Run the file to
generate example1.off ... example8.off.
"""
import add


def example1():
    """A stepped pyramid of little cubes, mirrored top and bottom."""
    m = 10
    for k in range(m):
        for i in range(m - k):
            for j in range(m - k):
                if i in (0, m - k - 1) or j in (0, m - k - 1):
                    add.cube([i + k / 2, k / 2, j + k / 2], 0.8,
                             add.random_color())
                    if k != 0:
                        add.cube([i + k / 2, -k / 2, j + k / 2], 0.8,
                                 add.random_color())
    add.save("example1.off")


def example2():
    """The same pyramid, built from hollow cube frames."""
    m = 10
    for k in range(m):
        for i in range(m - k):
            for j in range(m - k):
                if i in (0, m - k - 1) or j in (0, m - k - 1):
                    add.frame([i + k / 2, k / 2, j + k / 2], 0.8, 0.1,
                              add.random_color())
                    if k != 0:
                        add.frame([i + k / 2, -k / 2, j + k / 2], 0.8, 0.1,
                                  add.random_color())
    add.save("example2.off")


def example3():
    """Three interlocking tori, each a parametric surface."""
    a, b = 5, 1

    def torus1(u, v):
        return [(a + b * add.cos(u)) * add.cos(v), b * add.sin(u),
                (a + b * add.cos(u)) * add.sin(v)]

    def torus2(u, v):
        return [(a + b * add.cos(u)) * add.cos(v),
                -(a + b * add.cos(u)) * add.sin(v), b * add.sin(u)]

    def torus3(u, v):
        return [b * add.sin(u), -(a + b * add.cos(u)) * add.cos(v),
                (a + b * add.cos(u)) * add.sin(v)]

    for f, col in ((torus1, [0, 255, 0]), (torus2, [255, 0, 0]),
                   (torus3, [0, 0, 255])):
        add.parametric(f, 0, 2 * add.pi, 50, 0, 2 * add.pi, 200, col,
                       wrap_u=True, wrap_v=True)
    add.save("example3.off")


def example4():
    """A Christmas tree, entirely out of parametric surfaces."""
    a, b, c, h, r, s = 36, 0.85, 1, 15, 0.15, 0.5

    def branches(u, v):
        return [add.sqrt(u) * add.cos(u) * v, h - h / a * u,
                add.sqrt(u) * add.sin(u) * v]

    def top(u, v):
        w = 1.5 * add.sqrt(3)
        return [c * add.sqrt(1 - u * u) * (1 - u) / w * add.cos(v),
                h + c * u + c,
                c * add.sqrt(1 - u * u) * (1 - u) / w * add.sin(v)]

    def trunk(u, v):
        return [s * add.cos(u) * add.sqrt(v / h), h - v,
                s * add.sin(u) * add.sqrt(v / h)]

    def base(u, v):
        return [u * add.cos(v), 0, u * add.sin(v)]

    def bauble(u, v):
        return [r * add.cos(u) * add.sin(v), r * add.cos(v) + h,
                r * add.sin(u) * add.sin(v)]

    add.parametric(branches, 0, a * b, 500, 0.98 * s / add.sqrt(a), 1, 15,
                   [0, 255, 0])
    add.parametric(top, -1, 1, 50, 0, 2 * add.pi, 40, [255, 0, 0])
    add.parametric(trunk, 0, 2 * add.pi, 20, 0, h, 100, [139, 69, 19])
    add.parametric(base, 0, s, 1, 0, 2 * add.pi, 20, [139, 69, 19])
    add.parametric(bauble, 0, 2 * add.pi, 30, 0, add.pi, 30, [255, 255, 255])
    add.save("example4.off")


def example5():
    """A tetrahedral stack of spheres."""
    m = 7
    for i in range(m):
        for j in range(m - i):
            for k in range(m - i - j):
                add.sphere([i * add.sqrt(3) / 2 + (k - 1) * add.sqrt(3) / 6,
                            k * add.sqrt(2 / 3),
                            j + 0.5 * (i - 1) + (k - 1) / 2],
                           0.5, 10, add.random_color())
    add.save("example5.off")


ICOSA = [[-0.262865, 0, 0.425325], [0.262865, 0, 0.425325],
         [-0.262865, 0, -0.425325], [0.262865, 0, -0.425325],
         [0, 0.425325, 0.262865], [0, 0.425325, -0.262865],
         [0, -0.425325, 0.262865], [0, -0.425325, -0.262865],
         [0.425325, 0.262865, 0], [-0.425325, 0.262865, 0],
         [0.425325, -0.262865, 0], [-0.425325, -0.262865, 0]]
ICOSA_EDGES = [[0, 1], [0, 4], [0, 6], [0, 9], [0, 11], [1, 4], [1, 6], [1, 8],
               [1, 10], [2, 3], [2, 5], [2, 7], [2, 9], [2, 11], [3, 5],
               [3, 7], [3, 8], [3, 10], [4, 5], [4, 8], [4, 9], [5, 8],
               [5, 9], [6, 7], [6, 10], [6, 11], [7, 10], [7, 11], [8, 10],
               [9, 11]]


def example6():
    """A ball-and-stick icosahedron."""
    for v in ICOSA:
        add.sphere(v, 0.06, 10, [0, 255, 0])
    for e in ICOSA_EDGES:
        add.tube(ICOSA[e[0]], ICOSA[e[1]], 0.02, 15, [0, 0, 255])
    add.save("example6.off")





BUCKY = [
    [-1.411334, 3.199887, 0], [-.705666, 3.199887, 1.222252],
    [.705666, 3.199887, 1.222252], [1.411334, 3.199887, 0],
    [.705666, 3.199887, -1.22225], [-.705666, 3.199887, -1.22225],
    [-2.55312, 2.385067, -.155618], [-2.98926, 1.570227, .911012],
    [-2.28358, 1.570227, 2.133254], [-1.141792, 2.385067, 2.288874],
    [-1.411334, 2.385067, -2.133266], [-2.55312, 1.881465, -1.474048],
    [-.705666, 1.570228, -3.044266], [1.411334, 2.385067, -2.133266],
    [.705666, 1.570228, -3.044266], [-1.141792, .251797, -3.296066],
    [-2.28358, -.251797, -2.636866], [-2.98926, .563037, -1.725844],
    [0, -.563034, -3.451686], [0, -1.881465, -2.948087],
    [-1.141792, -2.385053, -2.288887], [-2.28358, -1.570225, -2.133266],
    [1.141792, .251797, -3.296066], [2.28358, -.251797, -2.636866],
    [2.28358, -1.570225, -2.133266], [1.141792, -2.385053, -2.288887],
    [2.55312, 1.881465, -1.474048], [2.98926, .563037, -1.725844],
    [2.55312, 2.385067, -.155618], [2.98926, 1.570227, .911012],
    [3.42538, .251797, .659216], [3.42538, -.251797, -.659214],
    [1.141792, 2.385067, 2.288874], [2.28358, 1.570227, 2.133254],
    [0, 1.881464, 2.948094], [-2.28358, .251797, 2.636854],
    [-1.141792, -.251798, 3.296074], [0, .563036, 3.451694],
    [-3.42538, .251797, .659216], [-2.98926, -.563035, 1.725846],
    [-3.42538, -.251797, -.659214], [-2.98926, -1.570225, -.91101],
    [-2.55312, -2.385053, .15562], [-2.55312, -1.881465, 1.474048],
    [-.705666, -3.199893, -1.222251], [-1.411334, -3.199893, 0],
    [.705666, -3.199893, -1.222251], [2.98926, -1.570225, -.91101],
    [2.55312, -2.385053, .15562], [1.411334, -3.199893, 0],
    [2.98926, -.563035, 1.725846], [2.55312, -1.881465, 1.474048],
    [2.28358, .251797, 2.636854], [1.141792, -.251798, 3.296074],
    [.705666, -1.570226, 3.044274], [1.411334, -2.385053, 2.133253],
    [-.705666, -1.570226, 3.044274], [-1.411334, -2.385053, 2.133253],
    [-.705666, -3.199893, 1.222251], [.705666, -3.199893, 1.222251]]

BUCKY_EDGES = [
    [0, 1], [0, 5], [0, 6], [1, 2], [1, 9], [2, 3], [2, 32], [3, 4], [3, 28],
    [4, 5], [4, 13], [5, 10], [6, 7], [6, 11], [7, 8], [7, 38], [8, 9],
    [8, 35], [9, 34], [10, 11], [10, 12], [11, 17], [12, 14], [12, 15],
    [13, 14], [13, 26], [14, 22], [15, 16], [15, 18], [16, 17], [16, 21],
    [17, 40], [18, 19], [18, 22], [19, 20], [19, 25], [20, 21], [20, 44],
    [21, 41], [22, 23], [23, 24], [23, 27], [24, 25], [24, 47], [25, 46],
    [26, 27], [26, 28], [27, 31], [28, 29], [29, 30], [29, 33], [30, 31],
    [30, 50], [31, 47], [32, 33], [32, 34], [33, 52], [34, 37], [35, 36],
    [35, 39], [36, 37], [36, 56], [37, 53], [38, 39], [38, 40], [39, 43],
    [40, 41], [41, 42], [42, 43], [42, 45], [43, 57], [44, 45], [44, 46],
    [45, 58], [46, 49], [47, 48], [48, 49], [48, 51], [49, 59], [50, 51],
    [50, 52], [51, 55], [52, 53], [53, 54], [54, 55], [54, 56], [55, 59],
    [56, 57], [57, 58], [58, 59]]


def example7():
    """A ball-and-stick buckyball (C60)."""
    for v in BUCKY:
        add.sphere(v, 0.2, 10, [0, 255, 0])
    for e in BUCKY_EDGES:
        add.tube(BUCKY[e[0]], BUCKY[e[1]], 0.08, 15, [0, 0, 255])
    add.save("example7.off")


def example8():
    """A sea urchin: spikes pointing at every buckyball vertex."""
    add.sphere([0, 0, 0], 1.5, 15, [0, 0, 255])
    for v in BUCKY:
        add.tube([0, 0, 0], v, 0.2, 15, [255, 255, 0])
        add.cone(v, [1.3 * v[0], 1.3 * v[1], 1.3 * v[2]], 0.5, 15, [255, 0, 0])
    add.save("example8.off")


if __name__ == "__main__":
    for i in range(1, 9):
        globals()["example%d" % i]()
        print("example%d.off written" % i)

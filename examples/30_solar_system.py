"""
30 -- a solar system with banded planets.

A planet is a lathe: ``revolve`` spins a half circle, and a *colour
function* of (t, angle) paints it -- latitude bands for Jupiter, a
pseudo-random map of continents for Earth, a great red spot, ice caps.
Orbits are closed ``curve`` loops, moons are one small sphere strung
``along`` a circle, the asteroid belt is a jittered rock ``scatter``-ed on
random points of an annulus, the comet a ``polyline`` whose radius and
colour both fade along its tail.  Names are written with ``text``.

Parameters: ``DAY`` (turns the planets on their orbits), ``SEED``.
"""
import add

DAY = 40.0
SEED = 9
rng = add.Random(SEED)


def planet(center, r, paint, k=24, tilt=0.0):
    """A ball of radius ``r`` painted by ``paint(latitude, longitude)``.

    Latitude runs -1 (south pole) .. 1 (north pole), longitude 0 .. 2pi.
    """
    add.push()
    add.revolve(lambda t: [r * add.sin(t), r * add.cos(t)], [0, -r, 0], [0, r, 0],
                0, add.pi, k, 2 * k,
                color=lambda t, a: paint(add.cos(t), a))
    body = add.rotateZ(add.pop(), tilt)
    add.mesh(add.move(body, center))


def noise(lat, lon, seed):
    """A cheap, repeatable 'noise': a few sine waves added up."""
    v = 0.0
    for i in range(1, 5):
        v += add.sin(i * 2.3 * lon + seed * i) * add.cos(i * 1.7 * lat * 3 + seed) / i
    return v


def orbit(radius, phase, tilt=0.0):
    """A closed thin ring, and the point on it where the planet sits today."""
    add.curve(lambda t: [radius * add.cos(t), radius * 0.0 + tilt * add.sin(t), radius * add.sin(t)],
              0, 2 * add.pi, 160, 6, 0.03, [70, 70, 90], isConnected=True)
    a = phase + DAY / radius ** 1.5 * 4.0
    return [radius * add.cos(a), tilt * add.sin(a), radius * add.sin(a)]


# --------------------------------------------------------------------------
#  the sun and the planets
# --------------------------------------------------------------------------
planet([0, 0, 0], 3.0, lambda lat, lon: add.gradient(0.5 + 0.5 * noise(lat, lon, 1), "yellow", "orange"), 28)
for q in add.points_on_circle([0, 0, 0], 3.0, 24):             # solar flares
    tip = add.lerp([0, 0, 0], q, rng.uniform(1.15, 1.45))
    add.cone(q, tip, rng.uniform(0.15, 0.3), 8, "orange")

p = orbit(5.0, 0.3)
planet(p, 0.35, lambda lat, lon: add.gradient(0.5 + 0.4 * noise(lat, lon, 2), [140, 130, 120], [90, 80, 70]), 12)
add.text("MERCURY", [p[0] - 0.8, p[1] + 0.6, p[2]], 0.35, color="white", k=5)

p = orbit(7.0, 2.0)
planet(p, 0.55, lambda lat, lon: add.gradient(0.5 + 0.5 * noise(lat, lon, 3), [230, 200, 150], [200, 150, 90]), 14)
add.text("VENUS", [p[0] - 0.6, p[1] + 0.8, p[2]], 0.35, color="white", k=5)


def earth(lat, lon):
    if abs(lat) > 0.88:
        return "white"                                   # ice caps
    land = noise(lat, lon, 4) + 0.3 * noise(lat, 2 * lon, 5)
    if land > 0.55:
        return [90, 140, 60] if abs(lat) < 0.7 else [150, 160, 140]
    if land > 0.45:
        return [200, 190, 130]                           # beaches
    return [40, 90, 190] if land > 0.0 else [25, 60, 150]


p = orbit(9.5, 4.1)
planet(p, 0.6, earth, 18, tilt=0.4)
add.text("EARTH", [p[0] - 0.6, p[1] + 0.85, p[2]], 0.35, color="white", k=5)
add.push()
add.sphere([0, 0, 0], 0.14, 4, [200, 200, 205])
moon = add.pop()
add.mesh(add.along(moon, lambda t: [p[0] + 1.1 * add.cos(t), p[1] + 0.2 * add.sin(t), p[2] + 1.1 * add.sin(t)],
                   1, DAY / 3.0, DAY / 3.0 + 1, axis=None))

p = orbit(12.0, 5.5)
planet(p, 0.45, lambda lat, lon: add.gradient(0.5 + 0.5 * noise(lat, lon, 6), [200, 90, 50], [140, 60, 40])
       if abs(lat) < 0.9 else "white", 14)
add.text("MARS", [p[0] - 0.5, p[1] + 0.7, p[2]], 0.35, color="white", k=5)

# the asteroid belt: one jittered rock, scattered on random points of a ring
add.push()
add.sphere([0, 0, 0], 0.12, 3, [120, 110, 100])
rock = add.jitter(add.pop(), 0.04, seed=SEED)
belt = []
for _ in range(260):
    a, rr = rng.uniform(0, 2 * add.pi), rng.uniform(14.0, 16.5)
    belt.append([rr * add.cos(a), rng.uniform(-0.3, 0.3), rr * add.sin(a)])
add.mesh(add.scatter(rock, belt, seed=SEED, scale=(0.4, 1.8)))


def jupiter(lat, lon):
    band = int((lat + 1) * 6.5)
    base = [[220, 190, 150], [190, 140, 100], [230, 210, 180], [170, 120, 90]][band % 4]
    d = (lon - 4.0) ** 2 * 3 + ((lat + 0.35) * 8) ** 2
    if d < 1.2:
        return [200, 70, 50]                             # the great red spot
    return add.shade(base, 0.9 + 0.15 * add.sin(9 * lon + 20 * lat))


p = orbit(20.0, 1.2)
planet(p, 1.7, jupiter, 26)
add.text("JUPITER", [p[0] - 1.0, p[1] + 2.0, p[2]], 0.4, color="white", k=5)
add.push()
add.sphere([0, 0, 0], 0.1, 3, [220, 200, 160])
add.mesh(add.along(add.pop(), lambda t: [p[0] + 2.4 * add.cos(t), p[1] + 0.3 * add.sin(2 * t), p[2] + 2.4 * add.sin(t)],
                   4, DAY / 5.0, DAY / 5.0 + 2 * add.pi, axis=None, closed=True))

p = orbit(26.0, 3.3)
planet(p, 1.4, lambda lat, lon: add.gradient(0.5 + 0.5 * add.sin(9 * lat), [230, 215, 170], [200, 175, 120]), 24, tilt=0.45)
add.push()
add.ring([0, 0, 0], [0, 1, 0], 3.0, 1.9, 64, [210, 195, 160])
add.ring([0, 0, 0], [0, 1, 0], 1.85, 1.7, 64, [160, 140, 110])
rings = add.two_sided(add.rotateZ(add.pop(), 0.45))
add.mesh(add.move(rings, p))
add.text("SATURN", [p[0] - 0.9, p[1] + 2.2, p[2]], 0.4, color="white", k=5)

# a comet with a tail that thins and fades away from the sun
head = [-9.0, 2.5, -13.0]
away = add.direction([0, 0, 0], head)
tail = [add.lerp(head, [head[i] + away[i] * 9 for i in range(3)], t) for t in [i / 12.0 for i in range(13)]]
add.polyline(tail, lambda t: 0.3 * (1 - t) + 0.02, 8,
             color=lambda t, a: add.gradient(t, "white", [40, 40, 60]))
add.sphere(head, 0.35, 5, "white")

# a ground plane of stars: tiny bright spheres far below
for q in add.random_points(200, [-32, -6, -32], [32, -6, 32], SEED + 1):
    add.sphere(q, rng.uniform(0.05, 0.12), 2, "white")

add.check()
add.save("solar_system.off")

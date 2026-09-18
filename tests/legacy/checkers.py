import math
import add

#add.axes([0,0,0])

def curve1(t):
  x = 0.05 + 0.05 * math.cos(t)
  y = 0.3 + 0.05 * math.sin(t)
  return([x, y])
add.spin3D([0, 0, 0], [0, 1, 0], curve1, 0, math.pi, 16, 50, [55, 200, 55])

def curve2(t):
  x = 0.15 + 0.05 * math.cos(t)
  y = 0.3 + 0.05 * math.sin(t)
  return([x, y])
add.spin3D([0, 0, 0], [0, 1, 0], curve2, 0, math.pi, 16, 50, [55, 200, 55])

def curve3(t):
  x = 0.25 + 0.05 * math.cos(t)
  y = 0.3 + 0.05 * math.sin(t)
  return([x, y])
add.spin3D([0, 0, 0], [0, 1, 0], curve3, 0, math.pi, 16, 50, [55, 200, 55])

add.cylinder3([0, 0.12, 0], [0, 0.3, 0], 0.3, 50, [55, 200, 55])

saske = add.layer()

for i in range(8):
  for j in range(8):
    c = (i + j + 1) % 2
    add.rectangle3D([i, 0.1, j], [1, 0.05, 1], [255 * c, 255 * c, 255 * c])
    if c == 0 and j > 4:
      #add.cylinder([i, 0.12, j], [i, 0.3, j], 0.3, 50, [255, 255, 255])
      add.mesh(add.move(saske, [i, 0, j]))
    if c == 0 and j < 3:
      #add.cylinder([i, 0.12, j], [i, 0.3, j], 0.3, 50, [100, 0, 0])
      add.color(saske, [200, 55, 55])
      add.mesh(add.move(add.color(saske, [200, 55, 55]), [i, 0, j]))

add.rectangle3D([3.5, -0.07, 3.5], [9.5, 0.3, 9.5], [125, 22, 22])

raide = [add.load("letters/A.off"),
add.load("letters/B.off"),
add.load("letters/C.off"),
add.load("letters/D.off"),
add.load("letters/E.off"),
add.load("letters/F.off"),
add.load("letters/G.off"),
add.load("letters/H.off")
]

skaicius = [add.load("numbers/8.off"),
add.load("numbers/7.off"),
add.load("numbers/6.off"),
add.load("numbers/5.off"),
add.load("numbers/4.off"),
add.load("numbers/3.off"),
add.load("numbers/2.off"),
add.load("numbers/1.off")
]

for i in range(8):
  raide[i] = add.rotateX(raide[i], -math.pi / 2, [0, 0, 0])
  raide[i] = add.zoom(raide[i], 0.07)
  centras = add.center(raide[i])
  raide[i] = add.move(raide[i],[-centras[0] + i, -centras[1] + 0.1, -centras[2] + 7.9])
  raide[i] = add.color(raide[i],[55, 55, 255])
  add.mesh(raide[i])
  #add.cube([i, 0.1, 7.9], 0.1, [55, 55, 255])
  #add.cube([-0.9, 0.1, i], 0.1, [55, 255, 55])

  skaicius[i] = add.rotateX(skaicius[i], -math.pi / 2, [0, 0, 0])
  skaicius[i] = add.zoom(skaicius[i], 0.07)
  centras = add.center(skaicius[i])
  skaicius[i] = add.move(skaicius[i],[-centras[0] -0.9, -centras[1] + 0.1, -centras[2] + i])
  skaicius[i] = add.color(skaicius[i],[55, 255, 55])
  add.mesh(skaicius[i])

#A = add.load("letters/E.off")
#A = add.rotateX(A, -math.pi / 2, [0, 0, 0])
#A = add.zoom(A, 0.1)
#print(add.center(A))

#add.mesh(A)

add.off('checkers7.off')
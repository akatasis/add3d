import add
import math

# Padalos
add.rectangle3D([0, 0.9, 0],[0.008, 0.15, 0.008],[0, 0, 0])
V = add.layer()

add.rectangle3D([0, 0.9, 0],[0.005, 0.1, 0.005],[255, 0, 0])
L1 = add.layer()
for i in range(60):
  if (i % 5 != 0):
    M = add.rotateZ(L1, i*math.pi/30, [0, 0, 0])
  else:
    M = add.rotateZ(V, i*math.pi/30, [0, 0, 0])
  add.mesh(M)

T1 = add.layer()

#add.axes([0, 0, 0])

h = 3
m = 20
s = 6

# valandine rodykle
add.rectangle3D([0, 0.2, 0], [0.05, 0.6, 0.05], [0, 0, 0])
M1 = add.layer()
M1 = add.rotateZ(M1,-2 * math.pi * (h / 12 + m / 720 + s / 43200), [0, 0, 0])


# minutine rodykle
add.rectangle3D([0, 0.25, 0], [0.05, 0.8, 0.05], [0, 0, 0])
M2 = add.layer()
M2 = add.rotateZ(M2,-2 * math.pi * (m / 60 + s / 3600), [0, 0, 0])


# sekundine rodykle
add.rectangle3D([0, 0.25, 0], [0.02, 0.68, 0.02], [255, 0, 0])
M3 = add.layer()
M3 = add.rotateZ(M3,-2 * math.pi * (s / 60), [0, 0, 0])

add.mesh(M1)
add.mesh(M2)
add.mesh(M3)

alpha = math.pi / 3

for i in range(1, 10):
  n1 = add.load("numbers/"+str(i)+".off")
  n1 = add.zoom(n1, 0.02)
  n1 = add.move(n1, [-add.center(n1)[0], -add.center(n1)[1], -add.center(n1)[2]])
  n1 = add.move(n1, [0.75*math.cos(alpha), 0.75*math.sin(alpha), 0])
  n1 = add.color(n1, [0, 0, 0])
  add.mesh(n1)
  alpha -= math.pi / 6

n1 = add.load("numbers/1.off")
n1 = add.zoom(n1, 0.02)
n1 = add.move(n1, [-add.center(n1)[0], -add.center(n1)[1], -add.center(n1)[2]])
n1 = add.move(n1, [0.75*math.cos(alpha), 0.75*math.sin(alpha), 0])
n1 = add.move(n1,[-0.04,0,0])
n1 = add.color(n1, [0, 0, 0])
add.mesh(n1)

n1 = add.load("numbers/0.off")
n1 = add.zoom(n1, 0.02)
n1 = add.move(n1, [-add.center(n1)[0], -add.center(n1)[1], -add.center(n1)[2]])
n1 = add.move(n1, [0.75*math.cos(alpha), 0.75*math.sin(alpha), 0])
n1 = add.move(n1,[0.04,0,0])
n1 = add.color(n1, [0, 0, 0])
add.mesh(n1)

alpha -= math.pi / 6

n1 = add.load("numbers/1.off")
n1 = add.zoom(n1, 0.02)
n1 = add.move(n1, [-add.center(n1)[0], -add.center(n1)[1], -add.center(n1)[2]])
n1 = add.move(n1, [0.75*math.cos(alpha), 0.75*math.sin(alpha), 0])
n1 = add.move(n1,[-0.04,0,0])
n1 = add.color(n1, [0, 0, 0])
add.mesh(n1)

n1 = add.load("numbers/1.off")
n1 = add.zoom(n1, 0.02)
n1 = add.move(n1, [-add.center(n1)[0], -add.center(n1)[1], -add.center(n1)[2]])
n1 = add.move(n1, [0.75*math.cos(alpha), 0.75*math.sin(alpha), 0])
n1 = add.move(n1,[0.04,0,0])
n1 = add.color(n1, [0, 0, 0])
add.mesh(n1)

alpha -= math.pi / 6

n1 = add.load("numbers/1.off")
n1 = add.zoom(n1, 0.02)
n1 = add.move(n1, [-add.center(n1)[0], -add.center(n1)[1], -add.center(n1)[2]])
n1 = add.move(n1, [0.75*math.cos(alpha), 0.75*math.sin(alpha), 0])
n1 = add.move(n1,[-0.04,0,0])
n1 = add.color(n1, [0, 0, 0])
add.mesh(n1)

n1 = add.load("numbers/2.off")
n1 = add.zoom(n1, 0.02)
n1 = add.move(n1, [-add.center(n1)[0], -add.center(n1)[1], -add.center(n1)[2]])
n1 = add.move(n1, [0.75*math.cos(alpha), 0.75*math.sin(alpha), 0])
n1 = add.move(n1,[0.04,0.01,0])
n1 = add.color(n1, [0, 0, 0])
add.mesh(n1)

alpha -= math.pi / 6

add.circle([0, 0, 0], [0, 0, 1], 1, 120, [255, 255, 255])
#add.sphere([0 ,0, 0], 0.05, 10, [0, 0, 255])

add.mesh(T1)

add.off("laikrodis.off")
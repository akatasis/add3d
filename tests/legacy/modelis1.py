import add
import math

def kreive1(t):
  x = 0
  y = -t*t
  z = t
  return [x,y,z]
def kreive2(t):
  x = t
  y = t*t
  z = 0
  return [x,y,z]
def kreive3(t):
  x = t
  y = t*t
  return [x,y]
def pavirsius1(u,v):
  x = v
  y = v*v-u*u
  z = u
  return [x,y,z]
a = 1.7
add.axes([0,0,0])
add.curve(kreive1,-a,a,200,15,0.05,[255,0,255],False)
add.curve(kreive2,-a,a,200,15,0.05,[0,255,255],False)
add.spin3D([0,0,0],[0,1,0],kreive3,0,a,100,100,[255,255,0])
add.spin3D([0,0,0],[0,-1,0],kreive3,0,a,100,100,[255,255,0])
add.parametric(pavirsius1,-a,a,80,-a,a,80,[0,255,0])

add.off('modelis1.off')



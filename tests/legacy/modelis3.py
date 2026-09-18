import add
import math

a = 16
b = math.pi/a
r = 2

def kreive1(t):
  x = r*math.cos(t)
  y = r*math.sin(t)
  z = 0
  return [x,y,z]
def kreive2(t):
  x = r*math.cos(t)
  y = 0
  z = r*math.sin(t)
  return [x,y,z]
def kreive3(t):
  x = 0
  y = r*math.cos(t)
  z = r*math.sin(t)
  return [x,y,z]

for i in range(a):
  add.curve(kreive1,-b/2+2*i*b,-b/2+(2*i+1)*b,20,36,0.15,[255,0,0],False)
  add.curve(kreive2,-b/2+2*i*b,-b/2+(2*i+1)*b,20,36,0.15,[0,255,0],False)
  add.curve(kreive3,-b/2+2*i*b,-b/2+(2*i+1)*b,20,36,0.15,[0,0,255],False)
  add.sphere(kreive1(b+2*i*b),0.16,10,[0,255,255])
  add.sphere(kreive2(b+2*i*b),0.16,10,[255,0,255])
  add.sphere(kreive3(b+2*i*b),0.16,10,[255,255,0])

# variacija 1:
#modelis1 = add.layer()
#modelis2 = add.rotateX(add.rotateY(add.zoom(modelis1,0.7),math.pi/4,[0,0,0]),-math.pi/4,[0,0,0])
#modelis3 = add.rotateY(add.rotateZ(add.zoom(modelis2,0.6),math.pi/4,[0,0,0]),-math.pi/4,[0,0,0])
#add.mesh(add.merge([modelis1,modelis2,modelis3]))

add.off('modelis3.off')



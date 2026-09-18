# parametric(S,min_u,max_u,grid_u,min_v,max_v,grid_v,RGB)
# curve(P,min_t,max_t,grid_t,k,r,RGB,isConnected)
# spin3D(A,B,S,min_t,max_t,grid_t,k,RGB)
# stretch(M,s)

import add
import math

a1 = 2.04
b1 = -13.92
s1 = 1
v1 = -0.2

a2 = 13.32
b2 = 6.24
s2 = -0.8
v2 = -0.6

a3 = -0.24
b3 = -0.48
s3 = 1
v3 = -3.2

def vector(A,B):
  l = 10
  k = 1
  d = 0.1
  col = [0,255,0]
  col2 = [255,0,255]
  n = l/math.sqrt((B[0]-A[0])**2+(B[1]-A[1])**2+(B[2]-A[2])**2)
  B1 = [A[0]+(B[0]-A[0])*n,A[1]+(B[1]-A[1])*n,A[2]+(B[2]-A[2])*n]
  B2 = [B1[0]+(B[0]-A[0])*n/l*k,B1[1]+(B[1]-A[1])*n/l*k,B1[2]+(B[2]-A[2])*n/l*k]  
  add.cylinder(A,B1,d,12,col)
  add.cone(B1,B2,d*2,12,col2)

def qvect1(t,h):
  a = P(t)
  b = P(t+h)
  return([a[0]+(b[0]-a[0])/h,a[1]+(b[1]-a[1])/h,a[2]+(b[2]-a[2])/h])

def P(t):
  x = math.sin(s3*t)*b3*math.cos(v3*t)+math.cos(s3*t)*a3*math.sin(v3*t)-a2*math.sin(v2*t)*math.sin(s2*t)+b2*math.cos(v2*t)*math.cos(s2*t)
  y = math.sin(s1*t)*b1*math.cos(v1*t)+math.cos(s1*t)*a1*math.sin(v1*t)-a3*math.sin(v3*t)*math.sin(s3*t)+b3*math.cos(v3*t)*math.cos(s3*t)
  z = math.sin(s2*t)*b2*math.cos(v2*t)+math.cos(s2*t)*a2*math.sin(v2*t)-a1*math.sin(v1*t)*math.sin(s1*t)+b1*math.cos(v1*t)*math.cos(s1*t)
  return [x,y,z]

add.curve(P,0,10*math.pi,1000,18,0.3,[255,0,0],True)

for i in range(1000):
  t = i*10*math.pi/1000
  vector(P(t),qvect1(t,1e-8))
  
add.off('modelis4.off')


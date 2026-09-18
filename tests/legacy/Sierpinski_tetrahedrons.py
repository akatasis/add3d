vertices = []
faces = []
def tetra(c,RGB): # c - center, RGB - color
  global vertices, faces
  F = [[0,1,2],[3,1,0],[2,3,0],[3,2,1]]
  V = [[-0.5,-0.5,-0.5],[0.5,0.5,-0.5],[0.5,-0.5,0.5],[-0.5,0.5,0.5]] 
  for i in range (0,4):
    faces += ['3 '+str(F[i][0]+len(vertices))+' '+str(F[i][1]+len(vertices))+' '+str(F[i][2]+len(vertices))+
    ' '+str(RGB[i][0])+' '+str(RGB[i][1])+' '+str(RGB[i][2])]
  for j in range (0,4):
    vertices += [str(c[0]+V[j][0])+' '+str(c[1]+V[j][1])+' '+str(c[2]+V[j][2])]

def layer():
  global vertices, faces
  M = [vertices, faces]
  clear()
  return(M)

def clear():
  global vertices, faces
  vertices = []
  faces = []

def off(mesh): # mesh - off file
  global vertices, faces
  file = open(mesh, 'w')
  file.write('%s\n%d %d %d\n' % ('OFF',len(vertices),len(faces),0))
  for i in range (len(vertices)):
    file.write('%s\n' % vertices[i])
  for j in range (len(faces)):
    file.write('%s\n' % faces[j])
  file.close()
  clear()

def mesh(M):
  global vertices, faces
  for F in M[1]:
    n = int(F.split(' ',1)[0])
    f = F.split(' ',n + 1)
    f2 = ''
    for j in range(1, n + 1):
      f2 += str(int(f[j]) + len(vertices)) + ' '
    faces += [str(n) + ' ' + f2 + f[n+1]]
  vertices += M[0]

def move(M,V):
  N = []
  for i in range(len(M[0])):
    T = [float(j) for j in M[0][i].split(' ',2)]
    N += [str(T[0]+V[0]) + ' ' + str(T[1]+V[1]) + ' ' + str(T[2]+V[2])]
  return([N,M[1]])

def Sierpinski(iter):
  tetra([0,0,0],[[255,0,0],[0,255,0],[0,0,255],[255,255,0]])
  tetra([0,1,1],[[255,0,0],[0,255,0],[0,0,255],[255,255,0]])
  tetra([1,0,1],[[255,0,0],[0,255,0],[0,0,255],[255,255,0]])
  tetra([1,1,0],[[255,0,0],[0,255,0],[0,0,255],[255,255,0]])
  L = layer()
  for i in range(1, iter):
    mesh(move(L,[0,0,0]))
    mesh(move(L,[0,2**i,2**i]))
    mesh(move(L,[2**i,0,2**i]))
    mesh(move(L,[2**i,2**i,0]))
    L = layer()
  mesh(L)
  off('tetra2.off')

Sierpinski(7)
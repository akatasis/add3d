import add
import math
def saddle(u,v):
	x = u + 2
	y = v ** 2 - u ** 2
	z = -v + 2
	return([x,y,z])
add.parametric(saddle, -1, 1, 20,  -1, 1, 20, [255, 0, 255])
L = add.layer()
L = add.rotateX(L, 0.5, [2, 0, 2])
L = add.rotateY(L, 0.2, [2, 0, 2])
L = add.rotateZ(L, 0.3, [2, 0, 2])
L = add.stretch(L, [1.5, 0.8, 1.2])
add.mesh(L)
add.sphere([0, 2, 0], 0.5, 15, [255, 255, 0])
add.axes([0, 0, 0])
add.cube([0, 0, 0], 1, [255, 0, 0])
add.cube([0, 1, 0], 1, [0, 255, 0])
add.cube2([0, 2, 0], 1, 0.1, [0, 0, 255])
add.cylinder3([1, -0.5, 0], [1, 2.5, 0], 0.5, 20, [0, 255, 255])
add.cone2([1, 2.5, 0], [1, 4, 0], 0.5, 20, [255, 0, 0])
add.newface([[-0.5, 0.5, 0.5001], [0.5, 0.5, 0.5001], [0, 1, 0.5001]], [255, 0, 0])
add.pyramid([0, 3, 0], 1, 1.5, [0, 255, 0])
add.rectangle3D([-2, 0.5,0],[3,2,1],[0, 255, 255])
add.circle([-2, 5, 0], [-2, 5, 1], 1, 20, [255, 255, 0])
def curve(t):
	x = t/10
	y = math.cos(t)/10
	return([x, y])
add.spin3D([0, 5, 0], [0, 5, -1], curve, 0, 10, 20, 40, [255, 255, 0])

add.off('cube.off')
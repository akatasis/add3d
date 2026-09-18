import add

add.axes([0, 0, 0])
for i in range(8):
	for j in range(8):
		c = (i + j + 1) % 2
		add.rectangle3D([i, 0.1, j], [1, 0.05, 1], [255 * c, 255 * c, 255 * c])
		if c == 0 and j > 4:
			add.cylinder([i, 0.1, j], [i, 0.3, j], 0.3, 50, [255, 255, 255])
		if c == 0 and j < 3:
			add.cylinder([i, 0.1, j], [i, 0.3, j], 0.3, 50, [100, 0, 0])

add.rectangle3D([3.5, -0.07, 3.5], [9.5, 0.3, 9.5], [125, 22, 22])

add.off("checkers1.off")
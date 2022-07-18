import math

import numpy as np

WCAG_LEVELS = [3, 4.5, 7]
WCAG4_LEVELS = [1.6, 2.5, 3.8, 5.7, 8.7, 13.2]
APCA_LEVELS = [15, 30, 45, 60, 75, 90]


def wcag_y(color):
	c = color / 255
	c = np.where(c < 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
	return 0.2126 * c[:, 0] + 0.7152 * c[:, 1] + 0.0722 * c[:, 2]


def wcag_contrast(yfg, ybg, ambient=0.05):
	c = (ybg + ambient) / (yfg + ambient)
	c = np.where(c < 1, 1 / c, c)

	y0 = ambient
	y1 = 1 + ambient
	return c ** math.log(21, y1 / y0)


def apca_y(color):
	c = color / 255
	c **= 2.4
	y = 0.2126729 * c[:, 0] + 0.7151522 * c[:, 1] + 0.0721750 * c[:, 2]
	y += np.where(y < 0.022, 0.022 - y, 0) ** 1.414
	return y


def apca_contrast(yfg, ybg):
	_yfg = yfg ** np.where(ybg > yfg, 0.57, 0.62)
	_ybg = ybg ** np.where(ybg > yfg, 0.56, 0.65)
	c = (_ybg - _yfg) * 1.14
	c = np.where(np.abs(c) < 0.1, 0, np.where(c > 0, c - 0.027, c + 0.027))
	return np.abs(c) * 100


def count(a, b):
	return sum(a * b)


def iter_levels(levels):
	for i in range(len(levels) + 1):
		if i == 0:
			yield -math.inf, levels[i]
		elif i == len(levels):
			yield levels[i - 1], math.inf
		else:
			yield levels[i - 1], levels[i]


def print_row(row, sep=' | ', end=['']):
	_row = [''] + [f'{x:.1f}' for x in row] + end
	_row = [f'{s: >5}' for s in _row]
	print(sep.join(_row).strip())


def print_table(rows):
	for row in rows:
		print_row(row + [sum(row)])

	r = np.array(rows)
	totals = [sum(r[:, i]) for i in range(r.shape[1])]
	print_row(totals, end=['', ''])
	print()


if __name__ == '__main__':
	size = 20_000
	fg = np.random.randint(0, 256, size=(size, 3))
	bg = np.random.randint(0, 256, size=(size, 3))

	apca_yfg = apca_y(fg)
	apca_ybg = apca_y(bg)
	apca = apca_contrast(apca_yfg, apca_ybg)

	wcag_yfg = wcag_y(fg)
	wcag_ybg = wcag_y(bg)
	wcag = wcag_contrast(wcag_yfg, wcag_ybg)
	wcag4 = wcag_contrast(wcag_yfg, wcag_ybg, 0.4)

	for _wcag, wcag_levels in [(wcag, WCAG_LEVELS), (wcag4, WCAG4_LEVELS)]:
		rows = []
		for wcag_lower, wcag_upper in iter_levels(wcag_levels):
			rows.append([])
			a = (wcag_lower <= _wcag) * (_wcag < wcag_upper)
			for apca_lower, apca_upper in iter_levels(APCA_LEVELS):
				b = (apca_lower <= apca) * (apca < apca_upper)
				v = sum(a * b) / size * 100
				rows[-1].append(v)
		print_table(rows)

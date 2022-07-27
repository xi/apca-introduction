import math

from matplotlib import pyplot as plt
import numpy as np


def wcag_y(color):
	c = color / 255
	c = np.where(c < 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
	return 0.2126 * c[:, 0] + 0.7152 * c[:, 1] + 0.0722 * c[:, 2]


def wcag_contrast(yfg, ybg, ambient=0.05):
	c = (ybg + ambient) / (yfg + ambient)

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
	c = _ybg - _yfg
	c = np.exp(c)

	y0 = math.exp((0.022 ** 1.414) ** 0.6)
	y1 = math.exp(1)
	return c ** math.log(21, y1 / y0)


if __name__ == '__main__':
	fig, axes = plt.subplots(2, 2, sharex='row', sharey='row', figsize=(7, 6))

	options = {
		'marker': '.',
		'cmap': 'seismic',
	}

	size = 10_000
	fg = np.random.randint(0, 256, size=(size, 3))
	bg = np.random.randint(0, 256, size=(size, 3))

	apca_yfg = apca_y(fg)
	apca_ybg = apca_y(bg)
	apca = apca_contrast(apca_yfg, apca_ybg)

	wcag_yfg = wcag_y(fg)
	wcag_ybg = wcag_y(bg)
	wcag = wcag_contrast(wcag_yfg, wcag_ybg)
	wcag4 = wcag_contrast(wcag_yfg, wcag_ybg, 0.4)

	axes[0][0].set_title('APCA vs WCAG 2.x')

	axes[0][0].scatter(wcag, apca, **options)
	axes[0][0].set_xlabel('WCAG 2.x')
	axes[0][0].set_ylabel('APCA')
	axes[0][0].set_xscale('log')
	axes[0][0].set_yscale('log')

	p2 = axes[1][0].scatter(wcag_yfg, wcag_ybg, c=np.log(apca / wcag), **options)
	axes[1][0].set_xlabel('Yfg')
	axes[1][0].set_ylabel('Ybg')
	plt.colorbar(p2, ax=axes[1][0])

	axes[0][1].set_title('APCA vs WCAG 2.x (0.4)')

	axes[0][1].scatter(wcag4, apca, **options)
	axes[0][1].set_xlabel('WCAG 2.x (0.4)')
	axes[0][1].set_ylabel('APCA')
	axes[0][1].set_xscale('log')
	axes[0][1].set_yscale('log')

	p4 = axes[1][1].scatter(wcag_yfg, wcag_ybg, c=np.log(apca / wcag4), **options)
	axes[1][1].set_xlabel('Yfg')
	axes[1][1].set_ylabel('Ybg')
	plt.colorbar(p4, ax=axes[1][1])

	plt.tight_layout()
	plt.savefig('contrast_comparison.png')

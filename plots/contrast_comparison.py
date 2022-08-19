from matplotlib import pyplot as plt
import numpy as np


def wcag_y(color):
	c = color / 255
	c = np.where(c < 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
	return 0.2126 * c[:, 0] + 0.7152 * c[:, 1] + 0.0722 * c[:, 2]


def wcag_l(y, flare=0.05):
	return np.log(y / flare + 1) / np.log(1 / flare + 1)


def wcag_contrast(jfg, jbg):
	return jbg - jfg


def apca_y(color):
	c = color / 255
	c **= 2.4
	y = 0.2126729 * c[:, 0] + 0.7151522 * c[:, 1] + 0.0721750 * c[:, 2]
	y += np.where(y < 0.022, 0.022 - y, 0) ** 1.414
	return y


def apca_l(y):
	return y ** 0.6


def apca_contrast(jfg, jbg):
	_jfg = jfg ** (np.where(jbg > jfg, 0.57, 0.62) / 0.6)
	_jbg = jbg ** (np.where(jbg > jfg, 0.56, 0.65) / 0.6)
	return _jbg - _jfg


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
	apca_jfg = apca_l(apca_yfg)
	apca_jbg = apca_l(apca_ybg)
	apca = apca_contrast(apca_jfg, apca_jbg)

	for a, b, y, l, contrast, title in [
		(0, 0, wcag_y, apca_l, apca_contrast, 'sRGBtoY'),
		(0, 1, apca_y, wcag_l, apca_contrast, 'YtoJ'),
		(1, 0, apca_y, apca_l, wcag_contrast, 'contrast'),
		(1, 1, wcag_y, wcag_l, wcag_contrast, 'all'),
	]:
		values = apca - contrast(l(y(fg)), l(y(bg)))
		vmax = np.max(np.abs(values))
		p = axes[a][b].scatter(
			apca_ybg, apca_yfg, c=values, vmin=-vmax, vmax=vmax, **options
		)
		plt.colorbar(p, ax=axes[a][b])
		axes[a][b].set_title(title)

	plt.tight_layout()
	plt.savefig('contrast_comparison.png')

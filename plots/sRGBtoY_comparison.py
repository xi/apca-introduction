import math

from matplotlib import pyplot as plt
import numpy as np

WCAG_FACTORS = [1, 0.2126, 0.7152, 0.0722]
APCA_FACTORS = [1, 0.2126729, 0.7151522, 0.0721750]
APCA_EXPONENTS = [0.56, 0.57, 0.62, 0.65]


def wcag(x, factor, ambient):
	y = x / 255
	y = np.where(y < 0.04045, y / 12.92, ((y + 0.055) / 1.055) ** 2.4)
	y *= factor
	y += ambient

	y0 = ambient
	y1 = 1 + ambient
	return (y / y0) ** math.log(21, y1 / y0) / 20


def apca(x, factor, exp):
	y = x / 255
	y **= 2.4
	y *= factor
	y += np.where(y < 0.022, 0.022 - y, 0) ** 1.414
	y **= exp
	y = np.exp(y)

	y0 = math.exp((0.022 ** 1.414) ** 0.6)
	y1 = math.exp(1)
	return (y / y0) ** math.log(21, y1 / y0) / 20


if __name__ == '__main__':
	x = np.linspace(0, 255, 256)
	fig, axes = plt.subplots(4, 2, sharex=True, sharey='col', figsize=(6.4, 8))

	for i in range(4):
		wcag6 = wcag(x, WCAG_FACTORS[i], 0.4)

		for exp in APCA_EXPONENTS:
			y = apca(x, APCA_FACTORS[i], exp)
			axes[i][0].plot(x, y)
			axes[i][1].plot(x, y / wcag6)

		axes[i][0].plot(x, wcag(x, WCAG_FACTORS[i], 0.05))
		axes[i][0].plot(x, wcag6)

	axes[0][0].set_ylabel('gray')
	axes[1][0].set_ylabel('red')
	axes[2][0].set_ylabel('green')
	axes[3][0].set_ylabel('blue')

	axes[0][0].set_title('sRGBtoY')
	axes[0][1].set_title('ratio APCA / WCAG 0.4')

	fig.legend([
		'APCA 0.56',
		'APCA 0.57',
		'APCA 0.62',
		'APCA 0.65',
		'WCAG 0.05',
		'WCAG 0.4',
	], ncol=3, loc='lower center')

	plt.tight_layout()
	plt.subplots_adjust(bottom=0.1)
	plt.savefig('sRGBtoY_comparison.png')

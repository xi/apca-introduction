from matplotlib import pyplot as plt
import numpy as np


def norm(x, f):
	return (f(x) - f(0)) / (f(1) - f(0))


if __name__ == '__main__':
	plt.xlabel('luminance of screen (Y)')
	plt.ylabel('predicted perceived lightness (L)')

	x = np.linspace(0, 1) ** 2
	legend = []

	def weber(flare):
		plt.plot(x, norm(x, lambda y: np.log(y + flare)))
		legend.append(f'log(x + {flare})')

	def stevens(flare, alpha):
		plt.plot(x, norm(x, lambda y: (y + flare) ** alpha))
		legend.append(f'pow(x + {flare}, {alpha})')

	weber(0.05)
	weber(0.4)
	stevens(0, 0.333)
	stevens(0.025, 0.333)
	stevens(0, 0.56)
	stevens(0, 0.68)

	plt.legend(legend)
	plt.savefig('lightness_comparison.png')

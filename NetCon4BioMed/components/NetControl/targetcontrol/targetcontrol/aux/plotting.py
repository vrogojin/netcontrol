from __future__ import division

import matplotlib.pyplot as plt
from math import floor



# plots given data with various options
# - x = values for the x axis
# - y = list of lists, one for each x value, used for generating the plot
# - mean = style for the  mean line
# - median = style for the median line
# - primary = data to include in the primary shaded area
#   - None -> don't draw
#   - < 1 -> fraction of data (quantile)
#   - >= 1 -> number of stdev's away from the mean
# - secondary = data to include for the secondary shaded area
#   - None -> don't draw
#   - 0 -> min-max
#   - < 1 -> fraction of data (quantile)
#   - >= 1 -> number of stdev's away from the mean
# - label = label for the plot (useful whem plotting several data sets
# - color = the color of the plot (transparent versions used for box and whiskers intervals
def plot(x, y, ax, mean = '-', median = ' ', primary = None, secondary = None, label = None, color = None, linewidth = 1) :
	
	# computes p quantile of vector z
	# assumes z is sorted, sort before use !!!
	def quantile(z, p) :
		if len(z) == 1 :
			return z[0]
		cutoff = (len(z) - 1) * p
		left = int(floor(cutoff))
		ratio = cutoff - left
		return (1 - ratio) * z[left] + ratio * z[left + 1]

	# computes the mean and standard deviation for vector z
	def stdev(z) :
		m = sum(z) / len(z)
		s = (sum([(t - m) * (t - m) for t in z]) / (len(z) - 1)) ** 0.5 if len(z) > 1 else 0
		return m, s

	# sort vectors
	for z in y :
		z.sort()
	# decide plot labels: only label lines that are drawn
	if mean != ' ' and median != ' ' :
		label_mean = '{} (mean)'.format(label)
		label_median = '{} (median)'.format(label)
	elif mean != ' ' :
		label_mean = label
		label_median = None
	elif median != ' ' :
		label_median = label
		label_mean = None
	# compute and draw main lines
	y_median = [quantile(z, 0.5) for z in y]
	y_mean, y_stdev = zip(*[stdev(z) for z in y])
	# plot main lines
	if color is not None :
		ax.plot(x, y_median, median, color = color, label = label_median, linewidth = linewidth)
	else :
		line, = ax.plot(x, y_median, median, label = label_median, linewidth = linewidth)
		color = line.get_color()
	ax.plot(x, y_mean, mean, label = label_mean, color = color, linewidth = linewidth)
	# compute and draw primary shade bounds
	if primary is not None :
		if primary < 1 :
			primary_lo = [quantile(z, 0.5 - primary / 2) for z in y]
			primary_hi = [quantile(z, 0.5 + primary / 2) for z in y]
		else :
			primary_lo = [m - primary * s for (m, s) in zip(y_mean, y_stdev)]
			primary_hi = [m + primary * s for (m, s) in zip(y_mean, y_stdev)]
		ax.fill_between(x, primary_lo, primary_hi, facecolor = color, alpha = .2)
	# compute secondary shade bounds
	if secondary is not None :
		if secondary == 0 :
			secondary_lo = [min(z) for z in y]
			secondary_hi = [max(z) for z in y]
		elif secondary < 1 :
			secondary_lo = [quantile(z, 0.5 - secondary / 2) for z in y]
			secondary_hi = [quantile(z, 0.5 + secondary / 2) for z in y]
		else :
			secondary_lo = [m - secondary * s for (m, s) in zip(y_mean, y_stdev)]
			secondary_hi = [m + secondary * s for (m, s) in zip(y_mean, y_stdev)]
		ax.fill_between(x, secondary_lo, secondary_hi, facecolor = color, alpha = .1)



#=======
# package tests
#==============

if __name__ == '__main__' :
	from random import random
	from math import sin
	n = 100
	x = range(n)
	y = [[sin(t / 10) + 2 * random() - 1 for _ in range(100)] for t in x]
	fig, ax = plt.subplots(nrows = 2, ncols = 1)
	plot(x, y, ax[0], mean = '.', median = '-', primary = 0.5, secondary = 0, label = 'y')
	ax[0].legend(loc = 'upper left')
	plot(x, y, ax[1], primary = 1, secondary = 3, label = 'y')
	ax[1].legend(loc = 'upper left')
	plt.show()

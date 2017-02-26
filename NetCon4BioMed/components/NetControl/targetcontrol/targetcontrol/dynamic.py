# dynamic plots - testing for now
from __future__ import division
import matplotlib.pyplot as plt
import random

n = 10000
x = [random.gauss(0.5, 0.5) for _ in range(n)]
y = [random.gauss(0.5, 0.5) for _ in range(n)]
fig, ax = plt.subplots(nrows = 1, ncols = 1)
#f = ax.hist2d(x, y, bins=50)
f = ax.hexbin(x, y, bins=50)
plt.show()

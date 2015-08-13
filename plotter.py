import matplotlib.pyplot as plt
import numpy as np
import sys

"""given a row from a csv return a list of the elements in the row."""
def parseRow(row):
	elements = []
	word = ''
	for c in row:
		if c == ',':
			elements.append(int(word))
			word = ''
		elif c == '\n':
			elements.append(int(word))
			word = ''
		else:
			word = word + c

	return elements

path = 'logfile.csv'
if len(sys.argv) == 2:
	path = sys.argv[1]

data = open(path, 'r')

xs = []
ys = []
y2 = []

firstTime = -1

for line in data:
	items = parseRow(line)

	if firstTime == -1:
		firstTime = items[0]

	xs.append(items[0] - firstTime)
	ys.append(items[1])
	y2.append(items[2])

plt.plot(xs, ys, 'r--', xs, y2, 'b--')
plt.show()

data.closed()

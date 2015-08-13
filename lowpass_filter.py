"""this file moves through the sensor data and rejects deltas larger than
a given threshold"""

import matplotlib.pyplot as plt
import numpy as np
import sys

threshold = 100

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

def quietGetElement(N, i):
  try:
    n = N[i]
  except:
    n = None
  if i < 0:
    n = None
  return n

def outsideDelta(a, b, d):
  if abs(a-b) > d:
    return True
  return False

def getRow(array, i):
  return array[i]

def getColumn(array, j):
  column = []
  for row in array:
    column.append(row[j])
  return column

"""return true if the value n in N is seperated
from it's neighbors by more than t."""
def getOutliers(N, d):
  if len(N) < 3:
    print "you need more elements to filter."
    return None

  outliers = []

  lastn = None
  n = None
  nextn = None
  for i in range(len(N)):
    lastn = quietGetElement(N, i-1)
    n = quietGetElement(N, i)
    nextn = quietGetElement(N, i+1)

    if lastn == None:#we are at the first element
     if outsideDelta(n, nextn, d):
       outliers.append((lastn, n, nextn, i))
    elif nextn == None:#we are at the last element
      if outsideDelta(n, lastn, d):
        outliers.append((lastn, n, nextn, i))
    else:#we are in the middle of the list
      if outsideDelta(n, lastn, d) and outsideDelta(n, nextn, d):
        outliers.append((lastn, n, nextn, i))
  return outliers


path = 'logfile.csv'
if len(sys.argv) >= 2:
    path = sys.argv[1]

column = 0
if len(sys.argv) >= 3:
  column = int(sys.argv[2])

with open(path, 'rw') as file:
  lines = []
  for line in file:
    items = parseRow(line)
    lines.append(items)

if len(lines[0]) < column:
  print "the requested column does not exist."
  sys.abort()

data = []
for line in lines:
  data.append(line)

filterColumn = getColumn(data, column)

outliers = getOutliers(filterColumn, 200)

for outlier in outliers:
  mean = ((outlier[0] + outlier[2])/2, outlier[3])
  data[mean[1]][column] = mean[0]

t = getColumn(data, 0)
lidar = getColumn(data, 1)
big = getColumn(data, 2)
small = getColumn(data, 3)

#add the range that the manufacturer quotes
#add more options for filtering
plt.plot(lidar, big, 'b-', lidar, small, 'g-')
plt.show()

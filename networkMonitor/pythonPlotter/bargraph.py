import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import csv

#plt.ion()
#
#data = np.loadtxt('testdata.csv')
#plt.figure()
with open('testdata.csv', 'rb') as f:
	reader= csv.reader(f)
	#header = 0
	#for row in reader:
	#	if header == 0:
	#		header = row
	#	print row
	#row = header
	counter = 0
	timeaxis = [0] * 99
	data = [0] * 99
	for row in reader:
		header = row
		colnum = 0
		for col in row:
			if colnum != 0:
				timeaxis[counter] = int(header[colnum - 1])
				data[counter] = int(col) 
				print '%s %s' % (header[colnum - 1], col)
        		colnum += 1
		counter +=1

#for i in range(counter):
        
for i in range(counter):
        print '%d %d %d' % (data[i],timeaxis[i],i)
	#Before plotting add the data quantities
	if i > 0:
		data[i] = data[i] + data[i-1]
	plt.plot(timeaxis[i],data[i], 'ro--')
	plt.draw()
	#time.sleep(2)
plt.savefig("/var/www/html/plotTest.png")
#raw_input("done >>")


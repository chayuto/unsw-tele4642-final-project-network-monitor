import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import csv

from pylab import *
sites = []

#Simulate sample dictionary from the previous section of the code
testData = {}
testData['Fb'] = 1000
testData['Yt'] = 1250
testData['RD'] = 500
plt.clf()

servListRAW = tuple(open('/root/networkMonitor/servList.csv', 'r'))
hostListRAW = tuple(open('/root/networkMonitor/hostList.csv', 'r'))

servList = []
hostList = []
for i in servListRAW:
	servList.append(i.strip()) #remove \n character at the end of the line

for i in hostListRAW:
	hostList.append(i.strip()) #remove \n character at the end of the line

for i in servList:
	print i 

for i in hostList:
	print i

for i in testData:
	print i
sizes = [0] * len(testData)

j = 0
for i in testData:
	sites.append(i)
	sizes[j] = testData[i]
	j = j + 1
	
dataval = [sizes[0], sizes[1], sizes[2]]
columns = ['Data(Bytes)']
#plot table to the right of the chart
#plt.subplots_adjust(right= 0.75, top =0.85)
#plot percentage to 2 decimal places
patches, texts, autotexts = plt.pie(sizes, labels = sites, autopct = '%.2f%%')
for i in texts:
	i.set_fontsize(20)
#plot the legend of the pie chart instead of the table
plt.legend(dataval,loc=(1, 0.4), shadow=True)
plt.axis('equal')
plt.draw()
#shift the title up
plt.title('User 1 Data Consumption',fontsize = 30, y = 1.08)
#Make sure to set bbox_inches to tight
plt.savefig("/var/www/html/plotTest.png", bbox_iches = 'tight')
#plt.savefig("pie.png", bbox_inches = 'tight')


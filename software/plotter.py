import numpy as np
import matplotlib.pyplot as plt
import sys
import csv

filenames = sys.argv

timestamp = filenames[1][13:-4]

data = []

for i in range(1,len(filenames)):
	with open(filenames[i], 'r') as csvfile:
		raw = csv.reader(csvfile)
		raw = list(raw)
		data.append(raw)

data 		= np.asarray(data)

Original	= data[0]
Stramp		= data[1]
Trigger		= data[2]
Origtime	= data[3]
Stramptime	= data[4]*3


for i in range(np.shape(Original)[0]):
	eventno = Original[i][0]
	plt.figure(figsize=(7,5))
	plt.plot(Origtime[0], Original[i][2:], 'y', Stramptime[0], Stramp[i][2:], 'b', Stramptime[0], Trigger[i][2:], 'p')
	#pl.legend()
	plt.grid()
	#pl.show()
	plt.savefig('Plot_' + timestamp + '_' + eventno + '.pdf')
	plt.close()



#plt.figure(figsize=(7,5))
#plt.plot(time_value, volt_value1, 'y', time_value, volt_value2, 'b')
#plt.legend()
#plt.grid()
#plt.show()
#plt.savefig(timestamp + '.pdf')
#plt.close()

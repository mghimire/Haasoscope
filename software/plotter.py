import numpy as np
import matplotlib.pyplot as plt
import sys
import csv

filenames = sys.argv

timestamp = filenames[1][13:-4]

#print(filenames)

data = []

for i in range(1,len(filenames)):
	with open(filenames[i], 'r') as csvfile:
		raw = csv.reader(csvfile)
		raw = list(raw)
		data.append(raw)

Original	= np.array(data[0])
Stramp		= np.array(data[1])
Trigger		= np.array(data[2])
Origtime	= np.array(data[3])[0].astype(float)
Stramptime	= np.array(data[4])[0].astype(float)

for i in range(np.shape(Original)[0]):
	eventno 	= Original[i][0]
	Origvals 	= (Original[i][2:].astype(float) - 82.0)/1000.0
	Strampvals 	= (Stramp[i][2:].astype(float) + 3)/10.0
	Trigvals	= Trigger[i][2:].astype(float)
	plt.figure(figsize=(7,5))
	plt.plot(Origtime, Origvals, 'b.-')
	plt.plot(Stramptime, Strampvals, 'y.-')
#	plt.plot(Stramptime, Trigvals, 'r')
	plt.grid()
#	plt.legend()
#	plt.show()
	plt.xlim([-350,350])
	plt.savefig('Plot_' + timestamp + '_' + eventno + '.pdf')
	plt.close()



#plt.figure(figsize=(7,5))
#plt.plot(time_value, volt_value1, 'y', time_value, volt_value2, 'b')
#plt.legend()
#plt.grid()
#plt.show()
#plt.savefig(timestamp + '.pdf')
#plt.close()

import numpy as np
import matplotlib.pyplot as plt
import sys
import csv

filenames = sys.argv

#print(filenames)

timestamp = filenames[1][13:-4]

data 	     = []

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

fastres		= Origtime[1] - Origtime[0]
slowres		= Stramptime[1] - Stramptime[0]

datanum		= np.shape(Original)[0] - 2

print('There are', datanum, 'events')

timerngmin	= -350	#in ns
timerngmax	= 350	#in ns

origbaseval	= 82	#in mV
origscale	= 1000.	#convert mV to V
strampbaseval	= -3	#in V
strampscale	= 10.	#due to x10 gain

fastdata	= -1.0*(Original[:,2:].astype(float) - origbaseval)/origscale
slowdata	= (Stramp[:,2:].astype(float) - strampbaseval)/strampscale

minindex	= np.where(Stramptime > timerngmin)[0][0]
maxindex	= np.where(Stramptime < timerngmax)[0][-1]

slowdata	= slowdata[:,minindex:maxindex]


#classify into single signal and multiple signal first

noiserms	= np.sqrt(np.mean(fastdata[0]**2))
print('rms is', noiserms)
noisethres	= noiserms*3

monosgnl   	= []	#signals with a single peak
multisgnl   	= []	#signals with multiple peaks

for i in range(datanum):
	peaks = np.where(fastdata[i] > noisethres)
	if np.any(np.ediff1d(peaks) > 1):
		multisgnl.append(i)
	else:
		monosgnl.append(i)

monosgnl 	= np.asarray(monosgnl)
print('There are', np.shape(monosgnl)[0], 'single signal events')
multisgnl 	= np.asarray(multisgnl)
print('There are', np.shape(multisgnl)[0], 'multiple signal events')

#examples of mono signal, multi signal and anomaly
plt.figure(figsize=(7,5))
plt.plot(Stramptime[minindex:maxindex], slowdata[monosgnl[0]], 'y', Origtime, fastdata[monosgnl[0]], 'b')
#plt.legend()
plt.grid()
plt.xlim([-350,350])
#plt.show()
plt.savefig('mono.jpg')
plt.close()

plt.figure(figsize=(7,5))
plt.plot(Stramptime[minindex:maxindex], slowdata[multisgnl[0]], 'y', Origtime, fastdata[multisgnl[0]], 'b')
#plt.legend()
plt.grid()
plt.xlim([-350,350])
#plt.show()
plt.savefig('multi.jpg')
plt.close()

#single signal analysis
#----------------------
#idea is to compare the integrals under the peaks of the signal event and the expanded signal event

mononum		= np.shape(monosgnl)[0]
slowint		= np.zeros(mononum)
fastint		= np.zeros(mononum)

slowmax		= np.zeros(mononum)
fastmax		= np.zeros(mononum)

slowloc		= np.zeros(mononum)
fastloc 	= np.zeros(mononum)

j	= 0 #counter variable for integral arrays
for i in monosgnl:
	fastpeaks 	= np.where(fastdata[i]>noisethres)
	fastint[j]	= np.sum(fastdata[i][fastpeaks])*fastres
	fastmax[j]	= np.amax(fastdata[i])
	fastloc[j]	= Origtime[np.argmax(fastdata[i])]

	slowint[j]	= 0	
	slowpeaks	= np.where(slowdata[i]>0.01)
	slowint[j]	= np.sum(slowdata[i][slowpeaks])*slowres
	slowmax[j]	= np.amax(slowdata[i])
	slowloc[j]	= Stramptime[minindex:maxindex][np.argmax(slowdata[i])]

	j += 1


minpeakval 	= np.amin(fastmax)
maxpeakval	= np.amax(fastmax)

print('fast data saturates at', maxpeakval)

newpeaks	= np.where(fastmax > minpeakval + noisethres)
newmonosgnl	= monosgnl[newpeaks]
newfastint 	= fastint[newpeaks]
newslowint	= slowint[newpeaks]
newfastmax	= fastmax[newpeaks]
newslowmax	= slowmax[newpeaks]
newfastloc	= fastloc[newpeaks]
newslowloc	= slowloc[newpeaks]

print('There are', np.shape(newpeaks)[1], 'filtered events')

plt.figure(figsize=(7,5))
plt.scatter(slowint, fastint, marker='.')
ax = plt.gca()
ax.set_xlabel('integral around slow signal peak')
ax.set_ylabel('integral around fast signal peak')
plt.grid()
#plt.show()
plt.savefig('peakint_correlation.jpg')
plt.close()

plt.figure(figsize=(7,5))
plt.scatter(slowint, fastint, marker='.')
plt.plot(np.unique(slowint), np.poly1d(np.polyfit(slowint, fastint, 1))(np.unique(slowint)), 'r')
ax = plt.gca()
ax.set_xlabel('integral around slow signal peak')
ax.set_ylabel('integral around fast signal peak')
plt.grid()
plt.text(0.7, 0.1,'m = ' + '%.5f' % np.polyfit(slowint, fastint, 1)[0] + ' b = ' + '%.5f' % np.polyfit(slowint, fastint, 1)[1],
     horizontalalignment='center',
     verticalalignment='center',
     transform = ax.transAxes)
#plt.show()
plt.savefig('peakint_lobf.jpg')
plt.close()

plt.figure(figsize=(7,5))
plt.scatter(slowint, fastint, marker='.')
plt.plot(np.unique(slowint), np.poly1d(np.polyfit(slowint, fastint, 2))(np.unique(slowint)), 'r')
ax = plt.gca()
ax.set_xlabel('integral around slow signal peak')
ax.set_ylabel('integral around fast signal peak')
plt.grid()
plt.text(0.7, 0.1,'a = ' + '%.5f' % np.polyfit(slowint, fastint, 2)[0] + ' b = ' + '%.5f' % np.polyfit(slowint, fastint, 2)[1] + ' c = ' + '%.5f' % np.polyfit(slowint, fastint, 2)[2], horizontalalignment='center', verticalalignment='center', transform = ax.transAxes)
#plt.show()
plt.savefig('peakint_pobf.jpg')
plt.close()

plt.figure(figsize=(7,5))
plt.scatter(newslowint, newfastint, marker='.')
plt.plot(np.unique(newslowint), np.poly1d(np.polyfit(newslowint, newfastint, 2))(np.unique(newslowint)), 'r')
ax = plt.gca()
ax.set_xlabel('integral around slow signal peak')
ax.set_ylabel('integral around fast signal peak')
plt.grid()
plt.text(0.7, 0.1,'a = ' + '%.5f' % np.polyfit(newslowint, newfastint, 2)[0] + ' b = ' + '%.5f' % np.polyfit(newslowint, newfastint, 2)[1] + ' c = ' + '%.5f' % np.polyfit(newslowint, newfastint, 2)[2], horizontalalignment='center', verticalalignment='center', transform = ax.transAxes)
#plt.show()
plt.savefig('newpeakint_pobf.jpg')
plt.close()

plt.figure(figsize=(7,5))
plt.scatter(slowmax, fastmax, marker='.')
ax = plt.gca()
ax.set_xlabel('highest value of slow signal')
ax.set_ylabel('highest value of fast signal')
plt.grid()
#plt.show()
plt.savefig('peaks_correlation.jpg')
plt.close()

plt.figure(figsize=(7,5))
plt.scatter(newslowmax, newfastmax, marker='.')
ax = plt.gca()
ax.set_xlabel('highest value of slow signal')
ax.set_ylabel('highest value of fast signal')
plt.grid()
#plt.show()
plt.savefig('newpeaks_correlation.jpg')
plt.close()

plt.figure(figsize=(7,5))
plt.scatter(slowloc, fastloc, marker='.')
ax = plt.gca()
ax.set_xlabel('location of slow signal peak')
ax.set_ylabel('location of fast signal peak')

j = 0
for i in monosgnl:
	ax.annotate(Original[i][0], (slowloc[j], fastloc[j]))
	j += 1

plt.grid()
# #plt.show()
plt.savefig('peakloc_correlation.jpg')
plt.close()

plt.figure(figsize=(7,5))
plt.scatter(newslowloc, newfastloc, marker='.')
plt.plot(np.unique(newslowloc), np.poly1d(np.polyfit(newslowloc, newfastloc, 1))(np.unique(newslowloc)), 'r')
ax = plt.gca()
ax.set_xlabel('location of slow signal peak')
ax.set_ylabel('location of fast signal peak')

j = 0
for i in newmonosgnl:
	ax.annotate(Original[i][0], (newslowloc[j], newfastloc[j]))
	j += 1

plt.grid()
plt.text(0.7, 0.1,'m = ' + '%.5f' % np.polyfit(newslowloc, newfastloc, 1)[0] + ' b = ' + '%.5f' % np.polyfit(newslowloc, newfastloc, 1)[1],
     horizontalalignment='center',
     verticalalignment='center',
     transform = ax.transAxes)
#plt.show()
plt.savefig('newpeakloc_lobf.jpg')
plt.close()

# trnsgrsrs = []

# def error(i):
# 	return newfastloc[i] - np.polyfit(newslowloc, newfastloc, 1)[0]*newslowloc[i] - np.polyfit(newslowloc, newfastloc, 1)[1]

# for i in range(np.shape(newpeaks)[1]):
# 	err = error(i)
# 	if np.abs(err) > 2:
# 		trnsgrsrs.append([i,err])
# #		plt.figure(figsize=(7,5))
# #		plt.plot(time, expndata[monosgnl[i]], 'y', time, sgnldata[monosgnl[i]], 'b')
# 		#plt.legend()
# #		plt.grid()
# 		#plt.show()
# #		plt.savefig(filenames[newmonosgnl[i]] + '.jpg')
# #		plt.close()

# trnsgrsrs = np.asarray(trnsgrsrs).astype(int)

# print(trnsgrsrs[:,0])

# cleanfastint = np.delete(newfastint, trnsgrsrs[:,0], 0)
# cleanslowint = np.delete(newslowint, trnsgrsrs[:,0], 0)
# cleanfastloc = np.delete(newfastloc, trnsgrsrs[:,0], 0)
# cleanslowloc = np.delete(newslowloc, trnsgrsrs[:,0], 0)
# cleanmonosgnl = np.delete(newmonosgnl, trnsgrsrs[:,0], 0)

# plt.figure(figsize=(7,5))
# plt.scatter(cleanslowint, cleanfastint, marker='.')
# ax = plt.gca()
# ax.set_xlabel('integral around slow signal peak without anomalies')
# ax.set_ylabel('integral around fast signal peak without anomalies')
# plt.grid()
# #plt.show()
# plt.savefig('cleanint_correlation.jpg')
# plt.close()

# plt.figure(figsize=(7,5))
# plt.scatter(cleanslowint, cleanfastint, marker='.')
# ax = plt.gca()
# ax.set_xlabel('integral around slow signal peak without anomalies')
# ax.set_ylabel('integral around fast signal peak without anomalies')

# j = 0
# for i in cleanmonosgnl:
# 	ax.annotate(Original[i][0], (cleanslowint[j], cleanfastint[j]))
# 	j += 1

# plt.grid()
# #plt.show()
# plt.savefig('labeled_cleanint_correlation.jpg')
# plt.close()

# plt.figure(figsize=(7,5))
# plt.scatter(cleanslowint, cleanfastint, marker='.')
# plt.plot(np.unique(cleanslowint), np.poly1d(np.polyfit(cleanslowint, cleanfastint, 1))(np.unique(cleanslowint)), 'r')
# ax = plt.gca()
# ax.set_xlabel('integral around slow signal peak')
# ax.set_ylabel('integral around fast signal peak')
# plt.grid()
# plt.text(0.7, 0.1,'m = ' + '%.5f' % np.polyfit(cleanslowint, cleanfastint, 1)[0] + ' b = ' + '%.5f' % np.polyfit(cleanslowint, cleanfastint, 1)[1],
#      horizontalalignment='center',
#      verticalalignment='center',
#      transform = ax.transAxes)
# #plt.show()
# plt.savefig('cleanint_lobf.jpg')
# plt.close()

# plt.figure(figsize=(7,5))
# plt.scatter(cleanslowint, cleanfastint, marker='.')
# plt.plot(np.unique(cleanslowint), np.poly1d(np.polyfit(cleanslowint, cleanfastint, 2))(np.unique(cleanslowint)), 'r')
# ax = plt.gca()
# ax.set_xlabel('integral around slow signal peak')
# ax.set_ylabel('integral around fast signal peak')
# plt.grid()
# plt.text(0.7, 0.1,'a = ' + '%.5f' % np.polyfit(cleanslowint, cleanfastint, 2)[0] + ' b = ' + '%.5f' % np.polyfit(cleanslowint, cleanfastint, 2)[1] + ' c = ' + '%.5f' % np.polyfit(cleanslowint, cleanfastint, 2)[2], horizontalalignment='center', verticalalignment='center', transform = ax.transAxes)
# #plt.show()
# plt.savefig('cleanint_pobf.jpg')
# plt.close()

# plt.figure(figsize=(7,5))
# plt.scatter(cleanslowloc, cleanfastloc, marker='.')
# plt.plot(np.unique(cleanslowloc), np.poly1d(np.polyfit(cleanslowloc, cleanfastloc, 1))(np.unique(cleanslowloc)), 'r')
# ax = plt.gca()
# ax.set_xlabel('location of slow signal peak')
# ax.set_ylabel('location of fast signal peak')

# j = 0
# for i in cleanmonosgnl:
# 	ax.annotate(Original[i][0], (cleanslowloc[j], cleanfastloc[j]))
# 	j += 1

# plt.grid()
# plt.text(0.7, 0.1,'m = ' + '%.5f' % np.polyfit(cleanslowloc, cleanfastloc, 1)[0] + ' b = ' + '%.5f' % np.polyfit(cleanslowloc, cleanfastloc, 1)[1],
#      horizontalalignment='center',
#      verticalalignment='center',
#      transform = ax.transAxes)
# #plt.show()
# plt.savefig('cleanpeakloc_lobf.jpg')
# plt.close()

# locdiff = cleanslowloc - cleanfastloc

# plt.figure(figsize=(7,5))
# plt.scatter(cleanslowint, locdiff, marker='.')
# plt.plot(np.unique(cleanslowint), np.poly1d(np.polyfit(cleanslowint, locdiff, 1))(np.unique(cleanslowint)), 'r')
# ax = plt.gca()
# ax.set_xlabel('integral around slow signal peak')
# ax.set_ylabel('slow signal peak location - fast signal peak location')

# #j = 0
# #for i in monosgnl:
# #	ax.annotate(Original[i][0], (slowloc[j], fastloc[j]))
# #	j += 1

# plt.grid()
# plt.text(0.7, 0.1,'m = ' + '%.5f' % np.polyfit(cleanslowint, locdiff, 1)[0] + ' b = ' + '%.5f' % np.polyfit(cleanslowint, locdiff, 1)[1],
#      horizontalalignment='center',
#      verticalalignment='center',
#      transform = ax.transAxes)
# #plt.show()
# plt.savefig('cleanslowint_peaklocdiff_correlation.jpg')
# plt.close()


"""cleanerr = sgnlint - (expnint + 226.62)/11.43

plt.figure(figsize=(7,5))
plt.hist(cleanerr, bins=100, label = 'error distribution')
ax = plt.gca()
ax.set_xlabel('difference between predicted and actual area under signal')
plt.grid()
plt.text(0.7, 0.1,'mean = ' + '%.5f' % np.mean(cleanerr) + ' std dev = ' + '%.5f' % np.std(cleanerr),
     horizontalalignment='center',
     verticalalignment='center',
     transform = ax.transAxes)
#plt.show()
plt.savefig('err_hist.jpg')
plt.close()

# sgnlpksval	= np.zeros(datanum)
# expnpksval	= np.zeros(datanum)
# sgnlpksloc	= np.zeros(datanum)
# expnpksloc	= np.zeros(datanum)

# for i in range(datanum):
# 	sgnlpksval[i] = np.amax(data[i][:,2])
# 	expnpksval[i] = np.amax(data[i][:,1])
# 	sgnlpksloc[i] = data[i][np.argmax(data[i][:,2]),0]
# 	expnpksloc[i] = data[i][np.argmax(data[i][:,1]),0]
     


# sgnlpksloc = sgnlpksloc*1e7
# expnpksloc = expnpksloc*1e7

# plt.figure(figsize=(7,5))
# plt.scatter(sgnlpksval, expnpksval)
# ax = plt.gca()
# ax.set_xlabel('value of original signal peak')
# ax.set_ylabel('value of stretched signal peak')
# plt.grid()
# #plt.show()
# plt.savefig('peakval_correlation.pdf')
# plt.close()

# plt.figure(figsize=(7,5))
# plt.scatter(sgnlpksval, expnpksval)
# plt.plot(np.unique(sgnlpksval), np.poly1d(np.polyfit(sgnlpksval, expnpksval, 1))(np.unique(sgnlpksval)), 'r')
# ax = plt.gca()
# ax.set_xlabel('value of original signal peak')
# ax.set_ylabel('value of stretched signal peak')
# plt.grid()
# plt.text(0.7, 0.1,'m = ' + '%.5f' % np.polyfit(sgnlpksval, expnpksval, 1)[0] + ' b = ' + '%.5f' % np.polyfit(sgnlpksval, expnpksval, 1)[1],
#      horizontalalignment='center',
#      verticalalignment='center',
#      transform = ax.transAxes)
# #plt.show()
# plt.savefig('peakval_lobf.pdf')
# plt.close()

# plt.figure(figsize=(7,5))
# plt.scatter(sgnlpksval, expnpksval)
# plt.plot(np.unique(sgnlpksval), np.poly1d(np.polyfit(sgnlpksval, expnpksval, 2))(np.unique(sgnlpksval)), 'r')
# ax = plt.gca()
# ax.set_xlabel('value of original signal peak')
# ax.set_ylabel('value of stretched signal peak')
# plt.grid()
# plt.text(0.7, 0.1,'a = ' + '%.5f' % np.polyfit(sgnlpksval, expnpksval, 2)[0] + ' b = ' + '%.5f' % np.polyfit(sgnlpksval, expnpksval, 2)[1] + ' c = ' + '%.5f' % np.polyfit(sgnlpksval, expnpksval, 2)[2],
#      horizontalalignment='center',
#      verticalalignment='center',
#      transform = ax.transAxes)
# #plt.show()
# plt.savefig('peakval_pobf.pdf')
# plt.close()

# plt.figure(figsize=(7,5))
# plt.scatter(sgnlpksloc, expnpksloc)
# ax = plt.gca()
# ax.set_xlabel('location of original signal peak')
# ax.set_ylabel('location of stretched signal peak')
# plt.grid()
# #plt.show()
# plt.savefig('peakloc_correlation.pdf')
# plt.close()

# outliers = np.argwhere(sgnlpksloc > -2)

# sgnlpksloc = np.delete(sgnlpksloc, outliers)
# expnpksloc = np.delete(expnpksloc, outliers)

# plt.figure(figsize=(7,5))
# plt.scatter(sgnlpksloc, expnpksloc)
# plt.plot(np.unique(sgnlpksloc), np.poly1d(np.polyfit(sgnlpksloc, expnpksloc, 1))(np.unique(sgnlpksloc)), 'r')
# ax = plt.gca()
# ax.set_xlabel('location of original signal peak')
# ax.set_ylabel('location of stretched signal peak')
# plt.text(0.7, 0.1,'m = ' + '%.5f' % np.polyfit(sgnlpksloc, expnpksloc, 1)[0] + ' b = ' + '%.5f' % np.polyfit(sgnlpksloc, expnpksloc, 1)[1],
#      horizontalalignment='center',
#      verticalalignment='center',
#      transform = ax.transAxes)
# plt.grid()
# #plt.show()
# plt.savefig('peakloc_lobf_no_outliers.pdf')
# plt.close()"""

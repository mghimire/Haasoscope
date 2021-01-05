import vxi11
import time, sys

#data collection variables

starttime	= time.time()
runtime 	= sys.argv[1]	#in hours
timeres		= 0.5			#in seconds

def main():
	sds = vxi11.Instrument("192.168.1.5") #read instrument IP address based on lxi discover
	sds.write("chdr off") #turn off command header in responses
	vdiv1 = sds.ask("c1:vdiv?") #get vertical sensitivity in Volts/div
	vdiv2 = sds.ask("c2:vdiv?")
	ofst1 = sds.ask("c1:ofst?") #get vertical offset of channels
	ofst2 = sds.ask("c2:ofst?")
	tdiv = sds.ask("tdiv?") #get horizontal scale per division
	sara = sds.ask("sara?") #get sample rate
	sara_unit = {'G':1E9,'M':1E6,'k':1E3} #set G, M, k unit multipliers
	
	for unit in sara_unit.keys():
		if sara.find(unit)!=-1: #verify unit type
			sara = sara.split(unit) #get number before unit and multiply
			sara = float(sara[0])*sara_unit[unit] #with appropriate unit multiplier
			break
	sara = float(sara)

	nevents = 0	
	
	outf = open("Siglent_out_"+time.strftime("%Y%m%d-%H%M%S")+".csv", 'wt')
	#set up file to save
		
	while (time.time() - starttime)/(60*60) <= runtime:
		updatedtime = time.time()
		
		sds.timeout = timeres*1000 #default value is 2000(2s)
		sds.chunk_size = 20*1024*1024 #default value is 20*1024(20k bytes)
		sds.write("c1:wf? dat2") #get data from channel 1
		recv1 = list(sds.read_raw())[15:] #set to list, getting rid of header
		recv1.pop() #get rid of last two \n elements
		recv1.pop()
		volt_value1 = []
		
		for data in recv1:
			data = data.encode('hex')
			data = int(data, 16)
			if data > 127:
				data = data - 255
			else:
				pass
			volt_value1.append(data)
		
		for idx in range(0,len(volt_value1)):
#			volt_value[idx] = volt_value[idx]/25*float(vdiv)-float(ofst)
			time_data = -(float(tdiv)*14/2)+idx*(1/sara)
			time_value.append(time_data)
		
		outf.write(str(nevents)); outf.write(",") # start of each line is the event number
        outf.write(str(updatedtime)); outf.write(",") # next column is the time in seconds of the current event
        .xydata[0][1].tofile(outf,",",format="%.3f") # save y data (1) from fast adc channel 0
        outf.write("\n")
		
		if time.time() - updatedtime < 2.0:
			time.sleep(2.0 - ((time.time() - updatedtime)/2.0))
	
	
if __name__=='__main__':
	main()

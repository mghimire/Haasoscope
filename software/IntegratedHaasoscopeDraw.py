import HaasoscopeLib
reload(HaasoscopeLib) # in case you changed it, and to always load some defaults
import vxi11
import time, sys
import matplotlib.pyplot as plt
import numpy as np
from serial import SerialException

#Some options
#HaasoscopeLib.num_board = 2 # Number of Haasoscope boards to read out (default is 1)
#HaasoscopeLib.ram_width = 12 # width in bits of sample ram to use (e.g. 9==512 samples (default), 12(max)==4096 samples) (min is 2)
#HaasoscopeLib.max10adcchans = [(0,110),(0,118),(1,110),(1,118)] #max10adc channels to draw (board, channel on board), channels: 110=ain1, 111=pin6, ..., 118=pin14, 119=temp # default is none, []

d = HaasoscopeLib.Haasoscope()
d.construct()

#Some other options
#d.serport="COM7" # the name of the serial port on your computer, connected to Haasoscope, like /dev/ttyUSB0 or COM8, leave blank to detect automatically!
#d.domaindrawing=False # whether to keep updating the main plot (on by default)
#d.serialdelaytimerwait=0 #50 #100 #150 #300 # 600 # delay (in 2 us steps) between each 32 bytes of serial output (set to 600 for some slow USB serial setups, but 0 normally)
#d.dolockin=True; d.dolockinplot=d.domaindrawing # whether to calculate the lockin info on the FPGA and read it out (off by default)

try:
	savetofile=True # save scope data to file
	if savetofile:
		outH = open("Stramplified_out_"+time.strftime("%Y%m%d-%H%M%S")+".csv","wt")
		outS = open("Original_out_"+time.strftime("%Y%m%d-%H%M%S")+".csv","wt")
		outT = open("Trigger_out_"+time.strftime("%Y%m%d-%H%M%S")+".csv","wt")
		resH = open("Stramplified_timeres.csv","wt")
		resS = open("Original_timeres.csv","wt")
    	
	if not d.setup_connections(): sys.exit()
	if not d.init(): sys.exit()
	d.on_launch()
    
	#can change some things
	#d.selectedchannel=0
	#d.tellswitchgain(d.selectedchannel)
	#d.togglesupergainchan(d.selectedchannel)
	#d.toggletriggerchan(d.selectedchannel)
	#d.togglelogicanalyzer() # run the logic analyzer
	#d.sendi2c("21 13 f0") # set extra pins E24 B0,1,2,3 off and B4,5,6,7 on (works for v8 only)
	
	#Siglent scope reader setup
	sds = vxi11.Instrument("192.168.1.5") #read instrument IP address based on lxi discover
	sds.write("chdr off") #turn off command header in responses
	vdiv1 = sds.ask("c1:vdiv?") #get vertical sensitivity in Volts/div
	ofst1 = sds.ask("c1:ofst?") #get vertical offset of channels
	tdiv = sds.ask("tdiv?") #get horizontal scale per division
	sara = sds.ask("sara?") #get sample rate
	sara_unit = {'G':1E9,'M':1E6,'k':1E3} #set G, M, k unit multipliers
	
	for unit in sara_unit.keys():
		if sara.find(unit)!=-1: #verify unit type
			sara = sara.split(unit) #get number before unit and multiply
			sara = float(sara[0])*sara_unit[unit] #with appropriate unit multiplier
			break

	sara = float(sara)
	
	writtentimeres = False
	
	nevents=0; oldnevents=0; tinterval=100.; oldtime=time.time()
	while 1:
		if d.paused: time.sleep(.1)
		else:
			if not d.getchannels(): break
            
			#print d.xydata[0][0][12], d.xydata[0][1][12] # print the x and y data, respectively, for the 13th sample on fast adc channel 0parse string python
            
			sds.chunk_size = 20*1024*1024 		#default value is 20*1024(20k bytes)
			sds.write("c1:wf? dat2") 			#get data from channel 1
			recv1 = list(sds.read_raw())[15:] 	#set to list, getting rid of header
			recv1.pop() 						#get rid of last two \n elements
			recv1.pop()
			volt_value = []
			time_value = []
		
			for data in recv1:
				data = data.encode('hex')
				data = int(data, 16)
#				if data > 127:
#					data = data - 255
#				else:
#					pass
				volt_value.append(data)
		    
			for idx in range(0,len(volt_value)):
#				volt_value[idx] = volt_value[idx]/25*float(vdiv)-float(ofst)
				time_data = -(float(tdiv)*14/2)+idx*(1/sara)
				time_value.append(time_data)
		    
			volt_value = np.asarray(volt_value)
			time_value = np.asarray(time_value)*1e9		#convert to ns
			
			if savetofile and d.writetofile:
				outH.write(str(nevents)); outH.write(",")
				outS.write(str(nevents)); outS.write(",")
				outT.write(str(nevents)); outT.write(",") # start of each line is the event number
				eventtime = str(time.time())
				outH.write(eventtime); outH.write(",")
				outS.write(eventtime); outS.write(",")
				outT.write(eventtime); outT.write(",") # next column is the time in seconds of the current event
				d.xydata[3][1].tofile(outH,",",format="%.3f") # save y data (1) from fast adc channel 3
				outH.write("\n")
				d.xydata[0][1].tofile(outT,",",format="%.3f") # save y data (1) from fast adc channel 0
				outT.write("\n")
				volt_value.tofile(outS,",",format="%.3f")
				outS.write("\n")
				
				if not writtentimeres: #create timeres files one time
					d.xydata[0][0].tofile(resH,",",format="%.3f")
					time_value.tofile(resS,",",format="%.3f")
					resH.close()
					resS.close()
					writtentimeres = True
			#if len(HaasoscopeLib.max10adcchans)>0: print "slow", d.xydataslow[0][0][99], d.xydataslow[0][1][99] # print the x and y data, respectively, for the 100th sample on slow max10 adc channel 0
			
			#if d.dolockin: print d.lockinamp, d.lockinphase # print the lockin info
			
			#if d.fftdrawn: # print some fft info (the freq with the biggest amplitude)
			#    fftxdata = d.fftfreqplot.get_xdata(); fftydata = d.fftfreqplot.get_ydata()
			#    maxfftydata=np.max(fftydata); maxfftfrq=fftxdata[fftydata.argmax()]
			#    print "max amp=",maxfftydata, "at freq=",maxfftfrq, d.fftax.get_xlabel().replace('Freq ','')
			
			if d.db: print time.time()-d.oldtime,"done with evt",nevents
			nevents+=1
			if nevents-oldnevents >= tinterval:
			    elapsedtime=time.time()-oldtime
			    lastrate = round(tinterval/elapsedtime,2)
			    print nevents,"events,",lastrate,"Hz"
			    oldtime=time.time()
			    if lastrate>40: tinterval=500.
			    else: tinterval=100.
			    oldnevents=nevents
			if d.getone and not d.timedout: d.paused=True
		d.redraw()
		if len(plt.get_fignums())==0:
			if d.domaindrawing: break # quit when all the plots have been closed
			elif nevents>50: break
except SerialException:
	print "serial com failed!"
finally:
	d.cleanup()
	if savetofile:
		outH.close()
		outS.close()
		outT.close()

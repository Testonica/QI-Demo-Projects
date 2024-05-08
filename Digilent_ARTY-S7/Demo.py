import os, sys, clr, System
py_dir = os.path.dirname(__file__)
clr.AddReference(r'C:\Testonica\QuickInstruments\Runtime\QI')
from Evi import *

if __name__ == '__main__':
 
	driver = TestbusController('Digilent') #Set up controller
	testbus = Testbus(System.Array[str](['IC1:xc7s50_csga324']), driver) #specify test bus
	testbus.IpLibrary = py_dir + '\ARTY_S7-demo.ipl' #specify library for the project
	
	if testbus.Check() : #check infra
		freq = Frequency(testbus) #Define instrument
		value = freq.Measure('IC1.#R2', System.Int64(0)) #Perform measurement
		#print(value)
		
		driver.Close() #CLEAN-UP
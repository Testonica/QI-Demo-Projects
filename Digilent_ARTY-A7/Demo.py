import os, sys, clr, System
py_dir = os.path.dirname(__file__)
clr.AddReference(r'C:\Testonica\QuickInstruments\Runtime\QI')
from Evi import *

if __name__ == '__main__':
 
	driver = TestbusController('Digilent') #Set up controller
	testbus = Testbus(System.Array[str](['IC1:xc7a35t_csg324']), driver) #specify test bus
	testbus.IpLibrary = py_dir + '\ARTY_A7.ipl' #specify library for the project
	
	if testbus.Check() : #check infra
		freq = Frequency(testbus) #Define instrument
		value = freq.Measure('IC1.IO_E3', System.Int64(0)) #Perform measurement
	
		driver.Close() #CLEAN-UP
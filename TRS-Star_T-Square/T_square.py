###########################################
# Project: T-Square-TRS-STAR
# Author: Igor Aleksejev
# Company: Testonica Lab
# QI API: https://qi.testonica.com/docs/api
###########################################

from __future__ import print_function
import clr, os, sys, subprocess
import time
import msvcrt

#Add paths
from os.path import dirname, abspath, join
py_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(py_dir)

import Settings as ts

#Import QI Runtime DLL
clr.AddReference(ts.path_to_quick_instruments+'\Runtime\QI')
from Evi import *
from Evi.SpiFlashModels import *

#Import QI python modules
sys.path.append(ts.path_to_quick_instruments)
from sequencer import sequencer
from scripts.test_helpers import *

#Import Pythonnet modules
import System
from System import Array
from System import Int32

################
# HELP FUNCTIONS
################
def isIpLoaded():
	svf = SvfPlayer(ts.testbus)
	svf.AlwaysCaptureTDO = True
	res = svf.Play(py_dir + './readIpCode.svf')
	
	if svf.LastTDO == 'A1985F04':
		return True
	
	return False

def resetTrion():
	driverA = TestbusController('FTDI', 'T*Square T20 Education Board A', 1, System.Array[str](['', '0x08', '0x00'])) #Keep GPIO_L00_SS_N line LOW
	print('')
	print('')
	print('Efinix Trion T20 FPGA requires special reset sequence')
	print('Press the RST button on the board and then press any key to continue the test..')
	print('')
	msvcrt.getch()
	
	driverA.Close()
	
################
# TEST FUNCTIONS
################

# TEST OF LEDS
def LEDS_TEST():
	ledPinArray = ["U200.#19", "U200.#18", "U200.#16", "U200.#15"]	
	
	ledPT = PinTouch(ts.testbus)
	ledPinsCLR = Array[str](ledPinArray)
		
	print ('')
	print('Press any key to run the test..')
	msvcrt.getch()
	print ('Press Y if all leds are blinking..')
	print ('Press N if not..')

	for x in range (20):
		ledPT.WriteMultiple(ledPinsCLR, Array[bool]([False] * len(ledPinsCLR)))
		time.sleep(0.5)

		ledPT.WriteMultiple(ledPinsCLR, Array[bool]([True] * len(ledPinsCLR)))
		time.sleep(0.5)

		if msvcrt.kbhit():
			c = msvcrt.getch()
			if c == b'y' or c == b'Y':
				ledPT.Stop()
				print ('Led test.. PASS')
				return 0
			if c == b'n' or c == b'N':
				ledPT.Stop()
				print ('Led test.. FAIL')
				return 1

	ledPT.Stop()
	return 0

# TEST OF PUSH BUTTONS
def PUSH_BUTTONS_TEST():
	
	if isIpLoaded():	
		resetTrion()
		
	testRes = 0
	
	pbPinArray = [
		{'Pin':'U200.#87', 'Name':'S100'}, 
		{'Pin':'U200.#89', 'Name':'S101'},
		]	
	
	print('')
	pbPT = PinTouch(ts.testbus)
	for pb in pbPinArray:
		res = False
		init_value = pbPT.Read(pb['Pin'], bool())
		print('Press', pb['Name'], 'push button')

		for x in range(16):
			value_after_change = pbPT.Read(pb['Pin'], bool())
			if value_after_change != init_value:
				res = True
				break
			else:
				time.sleep(0.5)
		
		if not res:
			print('Push button', pb['Name'], 'FAIL: measured value is always', init_value)
			testRes = 1
			
	return testRes

# Frequency measurement of the clock coming from X200
def FREQ_COUNTER_TEST() :
	
	if not isIpLoaded():	
		resetTrion()
	
	freq_counter = Frequency(ts.testbus)
	
	#pin, pin_freq, tolerance
	res = freq_counter.Expect('U200.#132', 10000000, 10000)
	if not res:
		value = freq_counter.Measure('U200.#132', System.Int64(0))
		print('')
		print('Frequecy Expect() Error on a pin: #132')
		print('Expected frequency: ' + str(10000000) + ', Measured: ' + str(value))
		return 1
		
	return 0

# JTAG mode of testing clock line (measurement of oscillating signal)
def OSC_TEST():
	
	oscPT = PinTouch(ts.testbus)
	res1 = oscPT.Read('U200.#132', bool())
	for i in range(20):
		res2 = oscPT.Read('U200.#132', bool())
		if res1 != res2 :
			return 0
	
	print('\nERROR: CLK test at U200.#132 FAILED, constantly measuring', 'HIGH' if res1 else 'LOW')
	return 1

# Communication with SPI device in a slow mode
def SPI_BASIC_TEST():
	
	#SCK, MISO, MOSI, SS
	spi_ic3 = Spi(ts.testbus, "U200.#30", "U200.#28", "U200.#29", "U200.#31");
	
	#Set FTDI ADBUS lines to HIGH-Z
	driverA = TestbusController('FTDI', 'T*Square T20 Education Board A', 1, System.Array[str](['', '0x00', '0x00'])) 
	
	#SPI ID expected values:
	manufacturer_id = 0xef
	device_id0 = 0x40
	device_id1 = 0x15
	
	spi_ic3.Stop()
	spi_ic3.WriteByte(0x9F) #Read ID command
	byte = spi_ic3.ReadByte(System.Int32(0)) #dummy byte
	if byte != manufacturer_id:
		print ("Manufacturer ID error! Expected: ", hex(manufacturer_id), ", Read:", hex(byte))
		return 1
		
	byte = spi_ic3.ReadByte(System.Int32(0))
	if byte != device_id0:
		print ("Device ID MSB error! Expected: ", hex(device_id0), ", Read:", hex(byte))
		return 1
		
	byte = spi_ic3.ReadByte(System.Int32(0))
	if byte != device_id1:
		print ("Device ID LSB error! Expected: ", hex(device_id1), ", Read:", hex(byte))
		return 1
		
	spi_ic3.Stop()
	driverA.Close()
	
	return 0

# Communication with SPI device in a high-speed mode
def SPI_PROGRAMMER_TEST():
	
	if not isIpLoaded():	
		resetTrion()
	
	bootSPI = BootSPI(ts.testbus)
	bootSPI.Init('U200');
	
	bootSPI.TestbyteEnabled = False	
	bootSPI.Stop()
	
	#Read ID code from the SPI Flash
	bootSPI.WriteByte(0x9F)
	spiReadByte = bootSPI.ReadByte(int()) #dummy
	for i in range(3):
		spiReadByte = bootSPI.ReadByte(int())
		print(hex(spiReadByte))
	bootSPI.Stop()
	
	return 0

	
##############
# END OF TESTS
##############
	
if __name__ == "__main__":

	tests = [
		{'Name': 'D400-D403 LEDs Test', 'Func_name' : LEDS_TEST },
		{'Name': 'BTN0-3 Push buttons Test', 'Func_name' : PUSH_BUTTONS_TEST },
		{'Name': 'U2001 Frequency counter test', 'Func_name': FREQ_COUNTER_TEST},
		{'Name': 'U2001 oscillating test', 'Func_name': OSC_TEST},
		{'Name': 'IC6 SpiFlashProgrammer test', 'Func_name': SPI_BASIC_TEST},
		{'Name': 'IC6 SPI Basic test', 'Func_name': SPI_PROGRAMMER_TEST},		
	]

	sequencer.run_tests(sys.argv[1:], tests, ts)
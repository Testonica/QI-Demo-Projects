########################
# Project: ARTY_S7
# Author: Igor Aleksejev
#
########################

from __future__ import print_function
import clr, os, sys, subprocess
import time
import msvcrt

#Add paths
from os.path import dirname, abspath, join
py_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(py_dir)

import ARTY_S7_settings as ts

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
# TEST FUNCTIONS
################
	
def QIS1200_FREQ_TEST() :
	
	freq_counter = Frequency(ts.testbus)
	#freq_counter.IpLibrary = ipl
	return FREQUENCY_COUNTER_TEST(freq_counter, 'IC1.#R2', 100000000)

def QIS5100_MEM_TEST():
	memTester = MemTester(ts.testbus)
	#mem.IpLibrary = ipl
	return MEMORY_INTERCONNECT_TEST(memTester, 'IC1.#K2')

def QIS5102_MEM_TEST():
	memTester = MemTester(ts.testbus)
	#mem.IpLibrary = ipl
	return MEMORY_MARGINS_TEST(memTester, 'IC1.#K2', ts.reports_folder+'/ddr3_margins.png')

def QIS2200_SPI_READ_FLASH_ID():
	
	spi_ic3 = Spi(ts.testbus, "IC1.#C8", "IC1.#K18", "IC1.#K17", "IC1.#M13");

	return SPI_TEST_SPI_FLASH_ID(spi_ic3, 0x01, 0x20, 0x18)


def QIS6100_SPI_PROGRAM():
	
	ic3_flash = SpiFlashProgrammer("IC1.#K17", ts.testbus)	
	ic3_flash.FlashModel = Cypress_S25()
	
	ic3_flash.Initialize()
	
	res = ic3_flash.VerifyID(0x01, 0x1820);
	if not res:
		print('VerifyID error')
		return 1
	
	pathToFile = py_dir + './../128KB.DAT'
	startAddress = 0x0;
	size = os.stat(pathToFile).st_size
	
	#Set QUAD mode
	ic3_flash.WriteRegister(System.Byte(0x01), Array[System.Byte]([0x00, 0x02]))
	
	res = ic3_flash.BlankCheck(startAddress, size);
	if not res:
		print('Flash is not blank. Erasing..')
		ic3_flash.Erase(startAddress, startAddress + size)
		res = ic3_flash.BlankCheck(startAddress, size);
		if not res:
			print('Flash still is not blank. Erase FAILED')
			return 1
	
	res = ic3_flash.ProgramAndVerify(pathToFile, startAddress, size);

	if not res:
		print('Erase or ProgramAndVerify operation FAILED')
		return 1
	
	return 0

#
# NB! An external connection between J7-3 <-> J7-4 is required
#
def QIS2300_UART_TEST():	
	#At first, verify that there is a connection
	iocondPT = PinTouch(ts.testbus)
	res = iocondPT.TestConnection('IC1.#G16', 'IC1.#H17') #unidirectional due to FPGA config!
	if not res:
		print('Verify that there is an external connection between J7-3 <-> J7-4')
		return 1
	
	#Verify link in UART mode
	uartLink = UartLink(ts.testbus, 'IC1.#G16', 'IC1.#H17')
	#uartLink.IpLibrary = mainIpl
	return UART_LINK_TEST(uartLink)

#
# NB! An external connection between PMOD JC-1 <-> PMOD JC-7 is required
#
def QIS1500_GENERATOR_TEST():	
	#At first, verify that there is a connection
	iocondPT = PinTouch(ts.testbus)
	res = iocondPT.TestConnection('IC1.#G16', 'IC1.#H17') #unidirectional due to FPGA config!
	if not res:
		print('Verify that there is an external connection between J7-3 <-> J7-4')
		return 1
	
	#Verify that Generator drives the expected clock signal
	freq_counter = Frequency(ts.testbus)
	#freq_counter.IpLibrary = ipl
	return FREQUENCY_COUNTER_TEST(freq_counter, 'IC1.#H17', 25000000)
	
def QIS1300_READ_XADC():

	monitor = SystemMonitor(ts.testbus)

	temp = monitor.Temperature("IC1", float())
	voltage = monitor.VoltageCore("IC1", float())
	
	res = 10 < temp < 95 and 0 < voltage < 1.8
	
	if not res:
		print('')
		print('Measured values are out of bounds')
		print('Measured Core Temperature is: ',temp)
		print('Measured Voltage is: ', voltage)
		return 1

	return 0

def TEST_LEDS_LD2_5():
	ledPinArray = ["IC1.#E18", "IC1.#F13", "IC1.#E13", "IC1.#H15"]	
	
	ledPT = PinTouch(ts.testbus)
	return PT_TEST_LEDS(ledPT, ledPinArray, "GPIO")

def TEST_PUSH_BUTTONS_BTN0_3():
	
	testRes = 0
	
	pbPinArray = [
		{'Pin':'IC1.#G15', 'Name':'BTN0'}, 
		{'Pin':'IC1.#K16', 'Name':'BTN1'},
		{'Pin':'IC1.#J16', 'Name':'BTN2'}, 
		{'Pin':'IC1.#H13', 'Name':'BTN3'}
		]	
	
	print('')
	pbPT = PinTouch(ts.testbus)
	for pb in pbPinArray:
		res = PT_TEST_PUSH_BUTTON(pbPT, pb['Pin'], pb['Name'])
		if (not res):
			testRes = 1
			
	return testRes
  
def TEST_SWITCHES_SW0_3():
	testRes = 0
	
	swPinArray = [
		{'Pin':'IC1.#H14', 'Name':'SW0'}, 
		{'Pin':'IC1.#H18', 'Name':'SW1'},
		{'Pin':'IC1.#G18', 'Name':'SW2'}, 
		{'Pin':'IC1.#M5', 'Name':'SW3'}
		]	
	
	print('')
	swPT = PinTouch(ts.testbus)
	for sw in swPinArray:
		res = PT_TEST_SWITCH(swPT, sw['Pin'], sw['Name'])
		if (not res):
			testRes = 1
			
	return testRes
	
##############
# END OF TESTS
##############
	
if __name__ == "__main__":

	tests = [
		{'Name': 'IC11 Oscillator test', 'Func_name': QIS1200_FREQ_TEST},
		{'Name': 'Generator test', 'Func_name': QIS1500_GENERATOR_TEST},
		{'Name': 'IC6 SpiFlashProgrammer test', 'Func_name': QIS6100_SPI_PROGRAM},
		{'Name': 'IC6 SPI Basic test', 'Func_name': QIS2200_SPI_READ_FLASH_ID},
		{'Name': 'IC8 Memory test', 'Func_name': QIS5100_MEM_TEST},
		{'Name': 'IC8 Memory Margin test', 'Func_name': QIS5102_MEM_TEST},
		{'Name': 'UART test', 'Func_name': QIS2300_UART_TEST},
		{'Name': 'IC1 FPGA ADC read', 'Func_name': QIS1300_READ_XADC},
		{'Name': 'BTN0-3 Push buttons Test', 'Func_name' : TEST_PUSH_BUTTONS_BTN0_3 },
		{'Name': 'LD2-5 LEDs Test', 'Func_name' : TEST_LEDS_LD2_5 },
		{'Name': 'SW0-3 Switches Test', 'Func_name' : TEST_SWITCHES_SW0_3 },
	]

	sequencer.run_tests(sys.argv[1:], tests, ts)
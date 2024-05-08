########################
# Project: ARTY
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

import ARTY_settings as ts

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
	return FREQUENCY_COUNTER_TEST(freq_counter, 'IC1.#E3', 100000000)

def QIS5100_MEM_TEST():
	memTester = MemTester(ts.testbus)
	#mem.IpLibrary = ipl
	return MEMORY_INTERCONNECT_TEST(memTester, 'IC1.#K5')

def QIS5102_MEM_TEST():
	memTester = MemTester(ts.testbus)
	#mem.IpLibrary = ipl
	return MEMORY_MARGINS_TEST(memTester, 'IC1.#K5', ts.reports_folder+'/ddr3_margins.png')

def QI3100_ETH_BASIC_TEST():

	eth_ic = Ethernet(ts.testbus)
	#eth_ic.IpLibrary = mainIpl
	
	txPins = Array[str](['#H14', '#J14', '#J13', '#H17', '#H15'])
	rxPins = Array[str](['#D18', '#E17', '#E18', '#G17'])
	ctrlPins = Array[str](['#H16', '#F15', '#G16', '#C17', '#F16', '#K13', '#C16', 'NC'])
	options = Array[str](['ENABLELOOPBACK=1'])
	
	return ETHERNET_BASIC_PHY_TO_PHY_TEST(eth_ic, txPins, rxPins, ctrlPins, 'IC1', 'IC6', 1, 'MII', 100, options)


def QI3108_ETH_STRESS_TEST():

	fert = EthernetStress(ts.testbus)
	#fert.IpLibrary = mainIpl
	
	return ETHERNET_STRESS_TEST(fert, 1, 'IC1.#H17', 'IC1.#D18')

def QIS2200_SPI_READ_FLASH_ID():
	
	spi_ic3 = Spi(ts.testbus, "IC1.#L16", "IC1.#K18", "IC1.#K17", "IC1.#L13");

	return SPI_TEST_SPI_FLASH_ID(spi_ic3, 0x01, 0x20, 0x18)


def QIS6100_SPI_PROGRAM():
	
	ic3_flash = SpiFlashProgrammer("IC1.#K17", ts.testbus)
	
	ic3_flash.FlashModel = Cypress_S25()
	#ic3_flash.FlashModel = Micron_N25X128()
	
	ic3_flash.Initialize()
		
	res = ic3_flash.VerifyID(0x01, 0x1820);
	if not res:
		print('VerifyID error')
		res, mId, dId = ic3_flash.ReadID(int(), int());
		print('Read manufacturer ID:', hex(mId), ' Device ID:', hex(dId))
		return 1
	
	
	pathToFile = py_dir + '/../128KB.DAT'
	startAddress = 0x0;
	size = os.stat(pathToFile).st_size
	
	res = ic3_flash.BlankCheck(startAddress, size);
	if not res:
		#print('Flash is not blank. Erasing..')
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
# NB! An external connection between PMOD JC-0 <-> PMOD JC-7 is required
#
def QIS2300_UART_TEST():	
	#At first, verify that there is a connection
	iocondPT = PinTouch(ts.testbus)
	res = iocondPT.TestConnection('IC1.#U12', 'IC1.#U14') #unidirectional due to FPGA config!
	if not res:
		print('Verify that there is an external connection between PMOD JC-0 <-> PMOD JC-7')
		return 1
	
	#Verify link in UART mode
	uartLink = UartLink(ts.testbus, 'IC1.#U12', 'IC1.#U14')
	#uartLink.IpLibrary = mainIpl
	return UART_LINK_TEST(uartLink)

#
# NB! An external connection between PMOD JC-1 <-> PMOD JC-8 is required
#
def QIS1500_GENERATOR_TEST():	
	#At first, verify that there is a connection
	iocondPT = PinTouch(ts.testbus)
	res = iocondPT.TestConnection('IC1.#V12', 'IC1.#V14') #unidirectional due to FPGA config!
	if not res:
		print('Verify that there is an external connection between PMOD JC-1 <-> PMOD JC-8')
		return 1
	
	#Verify that Generator drives the expected clock signal
	freq_counter = Frequency(ts.testbus)
	#freq_counter.IpLibrary = ipl
	return FREQUENCY_COUNTER_TEST(freq_counter, 'IC1.#V14', 25000000)

#
# NB! An external connection between PMOD JC-2 (#V10 - driven from IPL IoCond instrument) <-> PMOD JC-9 is required
# 
def QIS1900_IOCOND_PINTOUCH_TEST():
	#At first, verify that there is a connection
	iocondPT = PinTouch(ts.testbus)
	res = iocondPT.TestConnection('IC1.#V10', 'IC1.#T13', True)
	if not res:
		print('Verify that there is an external connection between PMOD JC-2 <-> PMOD JC-9')
		return 1
	
	return 0
	
	'''
	#Verify that IoCond drives the expected value
	meas_value = iocondPT.Read('IC1.#T13', bool())
	iocondPT.Stop()
	
	if meas_value == False:
		return 0
	else:
		print('')
		print ("IoCond FAIL: Measured value HIGH, expected LOW")
		return 1
    '''
    
def QIS1300_READ_XADC():

	monitor = SystemMonitor(ts.testbus)

	temp = monitor.Temperature("IC1", float())
	vcc_int = monitor.VoltageCore("IC1", float())
	vcc_bram = monitor.VoltageBram("IC1", float())
	vcc_aux = monitor.VoltageAux("IC1", float())
	
	res = 10 < temp < 95 and 0.9 < vcc_int < 1.0 and 0.9 < vcc_bram < 1.0 and 1.7 < vcc_aux < 1.9
	
	if not res:
		print('')
		print('Measured values are out of bounds')
		print('Measured Core Temperature is: ',temp)
		print('Measured Core Voltage is: ', vcc_int)
		print('Measured BRAM Voltage is: ', vcc_bram)
		print('Measured AUX Voltage is: ', vcc_aux)
		return 1

	return 0

def QIS6200_DEMO_SVF():

	svf = SvfPlayer(ts.testbus)
	pathToSVF = py_dir + './demo.svf'
	res = svf.Play(pathToSVF)

	if not res:
		return 1

	return 0

##############
# END OF TESTS
##############

if __name__ == "__main__":

	tests = [
		{'Name': 'IC2 Oscillator test', 'Func_name': QIS1200_FREQ_TEST},
		{'Name': 'Generator test', 'Func_name': QIS1500_GENERATOR_TEST},
		{'Name': 'IC6 Ethernet basic test', 'Func_name': QI3100_ETH_BASIC_TEST},
		{'Name': 'IOCOND test', 'Func_name': QIS1900_IOCOND_PINTOUCH_TEST},
		{'Name': 'IC3 SPI Flash programming', 'Func_name': QIS6100_SPI_PROGRAM},
		{'Name': 'IC3 SPI Flash ID check', 'Func_name': QIS2200_SPI_READ_FLASH_ID},
		{'Name': 'IC6 Ethernet stress test', 'Func_name': QI3108_ETH_STRESS_TEST},
		{'Name': 'IC7 Memory test', 'Func_name': QIS5100_MEM_TEST},
		{'Name': 'IC7 Memory Margin test', 'Func_name': QIS5102_MEM_TEST},
		{'Name': 'UART test', 'Func_name': QIS2300_UART_TEST},
		{'Name': 'IC1 FPGA ADC read', 'Func_name': QIS1300_READ_XADC},
		{'Name': 'SVF Demo', 'Func_name': QIS6200_DEMO_SVF},
	]

	sequencer.run_tests(sys.argv[1:], tests, ts)
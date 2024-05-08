import configparser, clr, os
from os.path import dirname, abspath, join
py_dir = os.path.dirname(os.path.abspath(__file__))

#Board parameters
dut_name = 'T_square'

#Controller settings
driverName = 'FTDI'
controllerId = 'T*Square T20 Education Board B'

#Testbus settings
testbus_devices = ['U200:t20_lqfp144']
testbus_frequency = 4000000 #10MHz
testbus = None #shared variable across modules. Will be initialized during an execution
testbus_IpLibrary = py_dir + './t_square.ipl' #Main IpLibrary for the project

#Report filenames
reports_folder = py_dir + './test_reports'
combinedReportFilename = 'testReportCombined.html'
boardReportFilename = 'testReport_##.html'
reportOutput = 'Console' #use 'Logfile' for production, 'Console' for debug
testLogFilename = 'log_#SN.txt' # '##" -> will be substituted to current date and time

log_level = 0

path_to_quick_instruments = 'C:\Testonica\QuickInstruments'
clr.AddReference(path_to_quick_instruments+'\Runtime\QI')
from Evi import *

def init_board_settings() :
	pass #no specific settings
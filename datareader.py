"""this file is the computer side application for an arduino based datalogger. 
On startup this file connects to the ardino at the selected port and issues a start message.
Once the connection is established the arduio will send a config struct listing the 
data format."""

import serial
import serial.tools.list_ports
import io
import sys
import time
import os

sampleTime = 20


"""find the correct port in the list of ports. Assume that the arduino is the
	only serial usb device connected."""

print "searching ports for connected devices"

ports = serial.tools.list_ports.comports()

arduinoAddress = ""
for port in ports:
	print port
	typ = port[0]
	dev = port[2]
	if "USB VID:PID=2341" in dev:
		print "arduino found."
		arduinoAddress = typ

"""if we still don't have a port, abort."""
if arduinoAddress == "":
	print "no arduino found"
	sys.abort()

path = 'logfile.csv'
if len(sys.argv) == 2:
	path = sys.argv[1]

"""get the current system path and create a log file for the sensor data."""
log = open(path, 'w')

arcom = serial.Serial(arduinoAddress, 115200)

startTime = time.time()
while time.time() - startTime < sampleTime+5:
	message = arcom.readline()
	sys.stdout.write(message)
	if(time.time() - startTime > 5):
		log.write(message)
log.close()
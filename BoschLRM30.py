"""this file is the computer side application for logging the data output from a
Bosch LRM30 OEM laser range finder."""

import serial
import serial.tools.list_ports
import io
import sys
import time
import os

sampleTime = 60

#Bosch specific constants
CRC8_POLYNOMIAL = 0xA6
CRC8_INITIAL_VALUE = 0xAA
RET_NOERR        =  1
RET_ERR_TIMEOUT=   -1
RET_ERR_STATUS =   -2

LASERON, LASEROFF, MEAS_INFO, MEAS_NORMAL, MEAS_CONT_START, MEAS_FAST_05HZ, MEAS_FAST_10HZ, MEAS_FAST_20HZ, MEAS_FAST_30HZ, MEAS_CONT_STOP = range(10)

commands = [
  (0xC0, 0x41, 0x00),
  (0xC0, 0x42, 0x00),
  (0xC0, 0x73, 0x00),
  (0xC0, 0x40, 0x01, 0x00),
  (0xC0, 0x40, 0x01, 0x01),
  (0xC0, 0x40, 0x01, 0x05),
  (0xC0, 0x40, 0x01, 0x0D),
  (0xC0, 0x40, 0x01, 0x15),
  (0xC0, 0x40, 0x01, 0x1D),
  (0xC0, 0x40, 0x01, 0x02)
]

def calcCRC8(data, init):
	for i in range(8):
		if (((init & 0x80) != 0) != ((data >> (7-i)) & 1)):
			init = (init << 1) ^ CRC8_POLYNOMIAL
		else:
			init <<= 1
	return init

def calcCRC8FromTuple(pData, init):
	for d in pData:
		init = calcCRC8(d, init)
	return init & 0xFF

def sendCommand(cmd, comport):
	command = commands[cmd]

	comport.flushInput()
	comport.flushOutput()

	cksum = calcCRC8FromTuple(command, CRC8_INITIAL_VALUE)
 	comport.write(command)
	comport.write([cksum])


def measureDistance(comport, command, timeout):
	sendCommand(command, comport)

	startTime = time.time()
	done = 0
	while not done:
		if time.time() - startTime > timeout:
			done = 2
		if comport.inWaiting() > 0:
			done = 1
	if done == 2:
		print "timeout error"
		return -1

	n =  comport.inWaiting()
	msg = comport.read(n)
	msg_bytes = bytearray(msg)

	value = 0

	#check for the status
	if msg_bytes[0] == 0:
		length = msg_bytes[1]

		payload = msg_bytes[2:2+length]

		for i in range(length):
			value += payload[i] << (i*8)

	#to get mm from the returned value:
	if value == 0:
		value = -1
	else:
		value = value * 50e-3 - 50

	return value

"""find the correct port in the list of ports. Assume that the arduino is the
	only serial usb device connected."""

print "searching ports for connected devices"

ports = serial.tools.list_ports.comports()

laserAddress = ""
for port in ports:
	#print port
	typ = port[0]
	dev = port[2]
	if "USB VID:PID=483" in dev:
		print "range finder found."
		laserAddress = typ

"""if we still don't have a port, abort."""
if laserAddress == "":
	print "no ranger found"
	sys.abort()

path = 'logfile.csv'
if len(sys.argv) == 2:
	path = sys.argv[1]

arcom = serial.Serial(laserAddress, 115200)

"""get the current system path and create a log file for the sensor data."""
log = open(path, 'w')

startTime = time.time()
lastTime = 0
measureDistance(arcom, MEAS_CONT_START, 2)
while time.time() - startTime < sampleTime+1:
	if time.time() - lastTime > 0.035:
		print measureDistance(arcom, MEAS_FAST_30HZ, 2)
		lastTime = time.time()

	#message = "bleh"
	#sys.stdout.write(message)
	#if(time.time() - startTime > 5):
	#	log.write(message)
log.close()
measureDistance(arcom, LASEROFF, 2)

#!/usr/bin/python                                                                                                                                        

import os,sys
import time
import datetime
import sys

sys.path.append('/home/pi/cloned/Adafruit-Raspberry-Pi-Python-Code/Adafruit_I2C')
sys.path.append('/home/pi/cloned/Adafruit-Raspberry-Pi-Python-Code/Adafruit_MCP4725')
sys.path.append('/home/pi/raspberrypi')
sys.path.append('/home/pi/raspberrypi_python')

from Adafruit_MCP4725 import MCP4725
import time

DAC_RESOLUTION    = 12

# Initialise the DAC using the default address                                                                                                           
dac = MCP4725(0x62)

if len(sys.argv)==0:
    print 'Must supply a value 0->5 V'
    sys.exit(1)

# make sure input is between 0 and 5 V
value=min(float(sys.argv[1]),5)
value=max(value,0)
print "Output %.1f V" % value
val=int((value/5.0)*2**DAC_RESOLUTION)
dac.setVoltage(val)

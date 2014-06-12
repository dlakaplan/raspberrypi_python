#!/usr/bin/python

import os,sys
import time
import datetime

sys.path.append('/home/pi/cloned/Adafruit-Raspberry-Pi-Python-Code/Adafruit_LEDBackpack')
sys.path.append('/home/pi/raspberrypi')
sys.path.append('/home/pi/raspberrypi_python')

import TSL2561

tsl=TSL2561.TSL2561(debug=True)
while True:
    lux=tsl.readLux()
    print lux
    time.sleep(5)

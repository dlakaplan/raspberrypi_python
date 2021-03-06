#!/usr/bin/python

import os,sys
import time
import datetime

import subprocess
import requests


sys.path.append('/home/pi/cloned/Adafruit-Raspberry-Pi-Python-Code/Adafruit_LEDBackpack')
sys.path.append('/home/pi/raspberrypi')
sys.path.append('/home/pi/raspberrypi_python')

from Adafruit_7Segment import SevenSegment
from Adafruit_LEDBackpack import LEDBackpack
import sun_altitude
import TSL2561b


def get_latest_file(maxdelay=3600):
  modtime=os.path.getmtime('/home/pi/.weewx_latest')
  if time.time()-modtime>maxdelay:
    return -99
  f=open('/home/pi/.weewx_latest')
  line=f.readlines()[0]
  try:
    tlast=int(line.split()[0])
    #if tlast % 60 == 0:
    #print line
  except:
    pass
  f.close()
  return float(line.split()[-1])


def write_time():
  now = datetime.datetime.now()
  hour = now.hour
  minute = now.minute
  second = now.second
  # Set hours
  segment.writeDigit(0, int(hour / 10))     # Tens
  segment.writeDigit(1, hour % 10)          # Ones
  # Set minutes
  segment.writeDigit(3, int(minute / 10))   # Tens
  segment.writeDigit(4, minute % 10)        # Ones
  # Toggle color
  segment.setColon(second % 2)              # Toggle colon at 1Hz

def write_temp(temp, F=True):
  """
  https://learn.adafruit.com/large-pi-based-thermometer-and-clock/software
  """
  if temp < -90:
    # it is a null value
      segment.writeDigitRaw(0, 0x40)       # - sign
      segment.writeDigitRaw(1, 0x40)       # - sign
      segment.writeDigitRaw(2, 0x40)       # - sign
      segment.writeDigitRaw(3, 0x40)       # - sign    
      return

  segment.setColon(False)
  sign = (temp < 0)
  temp = abs(temp)
  digit_1 = temp % 10
  temp = temp / 10
  digit_2 = temp % 10
  temp = temp / 10
  digit_3 = temp % 10
  if sign and (digit_2 > 0 or digit_3 > 0):
      segment.writeDigitRaw(0, 0x40)       # - sign
  elif digit_3 > 0 :
    segment.writeDigit(0, digit_3)       # Hundreds
  else:
    segment.writeDigitRaw(0, 0)
  if sign and not (digit_2 > 0 or digit_3 > 0):
      segment.writeDigitRaw(1, 0x40)       # - sign
  elif digit_2 > 0 :
    segment.writeDigit(1, digit_2)       # Tens
  else:
    segment.writeDigitRaw(1, 0)
  segment.writeDigit(3, digit_1)           # Ones
  if F:
    segment.writeDigitRaw(4, 0x71) #F        # Temp units letter
  else:
    segment.writeDigitRaw(4, 0x39) #C

# function to return a datastream object. This either creates a new datastream,
# or returns an existing one
def get_datastream(feed):
  try:
    datastream = feed.datastreams.get("external_temp")
    return datastream
  except:
    datastream = feed.datastreams.create("external_temp", tags="temp_01")
    return datastream
 


# ===========================================================================
# Clock Example
# ===========================================================================
led=LEDBackpack(address=0x70)


segment = SevenSegment(address=0x70)

try:
  interval=int(sys.argv[1])
except:
  print 'Interval required'
  sys.exit(1)

daybrightness=15
nightbrightness=5

minbrightness=1
maxbrightness=15

#tsl=TSL2561.TSL2561()


LightSensor = TSL2561b.Adafruit_TSL2561()
LightSensor.enableAutoGain(True)


# Continually update the time on a 4 char, 7-segment display
while(True):
  for i in xrange(interval):
    write_time()
    time.sleep(1)
  try:
    last=get_latest_file()
    temp=int(round(last))
    tempC=int(round((last-32)/1.8))      
  except:
    pass
  write_temp(temp)
  time.sleep(interval/2)
  write_temp(tempC, F=False)
  time.sleep(interval/2)
  try:
    alt,az=sun_altitude.sun_altitude()
  except:
    pass
  
  if True:
    lux=LightSensor.calculateLux()
    # 90 lux is dim daylight
    # 3000 lux is flashlight shining on sensor
    brightness=int(lux/10)
    brightness=min(brightness, maxbrightness)
    brightness=max(brightness, minbrightness)
    led.setBrightness(brightness)
    #print lux,brightness
  else:
    if alt > 0:
      led.setBrightness(daybrightness)
    else:
      led.setBrightness(nightbrightness)


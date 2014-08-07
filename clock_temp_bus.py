#!/usr/bin/python

import os,sys
import time
import datetime
import sqlite3
import mcts

sys.path.append('/home/pi/cloned/Adafruit-Raspberry-Pi-Python-Code/Adafruit_LEDBackpack')
sys.path.append('/home/pi/raspberrypi')
sys.path.append('/home/pi/raspberrypi_python')

from Adafruit_7Segment import SevenSegment
from Adafruit_LEDBackpack import LEDBackpack
import sun_altitude
import TSL2561b


def get_last(conn):
  c=conn.cursor()
  c.execute('select * from archive order by dateTime desc')
  result=c.fetchone()
  return result

def get_latest_file():
  f=open('/home/pi/.weewx_latest')
  line=f.readlines()[0]
  try:
    tlast=int(line.split()[0])
    if tlast % 600 == 0:
      print line
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
  segment.setColon(False)
  sign = (temp < 0)
  temp = abs(temp)
  digit_1 = temp % 10
  temp = temp / 10
  digit_2 = temp % 10
  temp = temp / 10
  digit_3 = temp % 10
  if sign :
    segment.writeDigitRaw(0, 0x40)       # - sign
  if digit_3 > 0 :
    segment.writeDigit(0, digit_3)       # Hundreds
  else:
    segment.writeDigitRaw(0, 0)
  if digit_2 > 0 :
    segment.writeDigit(1, digit_2)       # Tens
  else:
    segment.writeDigitRaw(1, 0)
  segment.writeDigit(3, digit_1)           # Ones
  if F:
    segment.writeDigitRaw(4, 0x71) #F        # Temp units letter
  else:
    segment.writeDigitRaw(4, 0x39) #C


def write_bus(timefromnow, bustype):
  """
  d = 0, 0x5E
  m = 0x54, 0x44 
  """
  digit_1 =timefromnow / 10
  digit_2 = timefromnow % 10
  segment.writeDigit(0, digit_1)       # tens of minutes
  segment.writeDigit(1, digit_2)       # minutes
  if bustype == 'M':
    segment.writeDigitRaw(3, 0x54)
    segment.writeDigitRaw(4, 0x44)
  else:
    segment.writeDigitRaw(3, 0)
    segment.writeDigitRaw(4, 0x5E)
    
# ===========================================================================
# Clock Example
# ===========================================================================
led=LEDBackpack(address=0x70)


segment = SevenSegment(address=0x70)
#conn=sqlite3.connect('/home/pi/weewx/archive/weewx.sdb')

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
  #last=get_last(conn)
  #temp=int(last[7])
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

  # get and display bus info
  try:
    data=mcts.check_route(mcts.APIkey, 
                          mcts.Stops['home']['rt'],
                          mcts.Stops['home']['stpid'],
                          mcts.Stops['home']['rtdir'])
  except:
    pass
  if data is not None:
    buses_printed=0
    for bus in data['bustime-response']['prd']:
      prdtm=datetime.datetime.strptime(bus['prdtm'],'%Y%m%d %H:%M')
      timefromnow=int(round((prdtm-datetime.datetime.now()).seconds/60.0))
      if not bus['rtdir']==mcts.Stops['home']['rtdir']:
        continue
      if len(bus['vid'])==0:
        continue
      delay=bus['dly']
      if 'Maryland' in bus['des']:
        bustype='M'
      else:
        bustype='D'
      write_bus(timefromnow, bustype)
      buses_printed+=1
      time.sleep(interval/2)
      if buses_printed==2:
        break



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

#conn.close()

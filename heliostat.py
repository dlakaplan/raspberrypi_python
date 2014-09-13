#!/usr/bin/python

import sys
sys.path.append('/home/pi/cloned/Adafruit-Raspberry-Pi-Python-Code/Adafruit_PWM_Servo_Driver')


from Adafruit_PWM_Servo_Driver import PWM
import time, math
import datetime
import ephem

# basic servo scalings and settings
_servoMin = 150  # Min pulse length out of 4096
_servoMax = 600  # Max pulse length out of 4096
# min and max angles corresponding to _servoMin and _servoMax
_minAngle=5
_maxAngle=175
_servoFreq = 60 # 60 Hz
_pwmaddress=0x40



def putinrange(angle, sign=+1):
  """
  result=putinrange(angle, sign=+1)
  will take an angle and return the appropriate servo value
  angle is scaled from the interval (_minAngle, _maxAngle)
  to (_servoMin, _servoMax)
  if sign < 0, then flips the direction of the scaling

  """
  if sign>0:
    if angle < _minAngle:
      angle=_minAngle
    if angle > _maxAngle:
      angle=_maxAngle
    return float(angle-_minAngle)/(_maxAngle-_minAngle)*(_servoMax-_servoMin)+_servoMin
  else:
    if angle < _minAngle:
      angle=_minAngle
    if angle > _maxAngle:
      angle=_maxAngle
    return float(angle-_minAngle)/(_maxAngle-_minAngle)*(_servoMin-_servoMax)+_servoMax
    

class heliostat():
    
    def __init__(self, azchannel, altchannel, azsign=1, altsign=1, debug=False):
        
      # Initialise the PWM device using the default address        
      self.pwm = PWM(_pwmaddress, debug=True)
      
      self.pwm.setPWMFreq(_servoFreq)
      self.azchannel=azchannel
      self.azsign=azsign
      self.altchannel=altchannel
      self.altsign=altsign
      self.debug=debug
      self.sun=ephem.Sun()
      self.observer=ephem.Observer()
      self.observer.lat='+43:03:08'
      self.observer.lon='-87:57:21'
      self.observer.elevation=188
      self.datetime=None

    def sunaltaz(self, inputdatetime=None):
      """
      computes the Sun alt and az for a given datetime (UTC)
      """
      if inputdatetime is None:
        self.datetime=datetime.datetime.utcnow()
      else:
        self.datetime=inputdatetime
      self.observer.date=self.datetime.strftime('%Y/%m/%d %H:%M:%S')
      self.sun.compute(self.observer)
      self.alt=self.sun.alt*180/math.pi
      self.az=self.sun.az*180/math.pi

    def setServoPulse(self, channel, pulse):
      """
      send a pulse of the given width to a selected servo channel
      """
      pulseLength = 1000000                   # 1,000,000 us per second
      pulseLength /= _servoFreq
      pulseLength /= 4096                     # 12 bits of resolution
      pulse *= 1000
      pulse /= pulseLength
      self.pwm.setPWM(channel, 0, pulse)


    def setalt(self, alt):
      altwidth=putinrange(alt, sign=self.altsign)
      if self.debug:
        print 'alt=%.1f -> width=%.1f ms' % (alt, altwidth)        
      self.setServoPulse(self.altchannel, altwidth)

    def setaz(self, az):
      azwidth=putinrange(az, sign=self.azsign)
      if self.debug:
        print 'az=%.1f -> width=%.1f ms' % (az, azwidth)        
      self.setServoPulse(self.azchannel, azwidth)

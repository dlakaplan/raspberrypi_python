
import time,sys

sys.path.append('/home/pi/cloned/Adafruit-Raspberry-Pi-Python-Code/Adafruit_MCP4725')
import TSL2561b
from Adafruit_MCP4725 import MCP4725

# 12-bit
dacmax=2**12
minbrightness=0
maxbrightness=5.0
# 90 lux is dim daylight
# 3000 lux is flashlight shining on sensor
maxlux=1000.

class light2dac():

    def __init__(self):
        self.LightSensor = TSL2561b.Adafruit_TSL2561()
        self.LightSensor.enableAutoGain(True)

        # Initialise the DAC using the default address
        self.dac = MCP4725(0x62)

    def __call__(self):
        self.lux=self.LightSensor.calculateLux()
        self.brightness=maxbrightness*float(self.lux/1000.)
        self.brightness=min(self.brightness, maxbrightness)
        self.brightness=max(self.brightness, minbrightness)
        self.dacvalue=int((self.brightness/maxbrightness)*dacmax)
        self.dac.setVoltage(self.dacvalue)
        


#l=light2dac()
#
#while True:
#    
#    l()
#    print l.lux,l.brightness,l.dacvalue
#    time.sleep(1)

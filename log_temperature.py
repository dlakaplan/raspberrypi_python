# https://learn.adafruit.com/mcp9808-temperature-sensor-python-library/software
# log temperature using MCP9808 and Raspberry pi

import time,datetime
import sys,os
import Adafruit_MCP9808.MCP9808 as MCP9808
sys.path.append('/home/pi/raspberry_python')
import TSL2561_newI2C


import time
import datetime
import httplib
import random
import urllib

#GroveStreams Settings

api_key=open('/home/pi/grovestream.api').read()

component_id = "KIRC - 4075"
base_url = '/api/feed?'

conn = httplib.HTTPConnection('www.grovestreams.com')


tempsensor = MCP9808.MCP9808()
tempsensor.begin()
LightSensor=TSL2561_newI2C.Adafruit_TSL2561()
LightSensor.begin()
LightSensor.enableAutoGain(True)

now=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
fout=open('temperature_KIRC4075_%s.log' % now,'w')
print 'Writing to temperature_KIRC4075_%s.log' % now

delay=int(sys.argv[1])

while True:
    temp = tempsensor.readTempC()
    now=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    lux=LightSensor.calculateLux()
    print '%s %.3f C %d lux' % (now,temp,lux)
    fout.write('%s %.3f C %d lux\n' % (now,temp,lux))
    fout.flush()

    try:    
        #Let the GS servers set the sample times. Encode parameters
        #url = base_url + urllib.urlencode({'compId' : component_id,
        #                                   'temperature' : temp,
        #                                   'light' : lux})
           
        #Alternative URL that includes the sample time
        now = datetime.datetime.now()
        sample_time = int(time.mktime(now.timetuple())) * 1000
        url = base_url + urllib.urlencode({'compId' : component_id,
                                           'time' : sample_time,
                                           'temperature' : temp,
                                           'light': lux})
        
        #Alternative URL that uses the stream order to determine where
        # to insert the samples
        #url = base_url + urllib.urlencode({'compId' : component_id, 'data' : [temperature_val, humidity_val]}, True)
           
        #The api_key token can be passed as URL parameters or as a cookie.
        # We've chosen to pass it as a cookie to keep the URL length small as
        # some devices have a URL size limit
        headers = {"Connection" : "close", "Content-type": "application/json",
                   "Cookie" : "api_key="+api_key}
           
        #GS limits feed calls to one per 10 seconds per outward facing router IP address
        #Use the ip_addr and headers assignment below to work around this
        # limit by setting the below to this device's IP address
        #ip_addr = "192.168.1.72"
        #headers = {"Connection" : "close", "Content-type": "application/json", "X-Forwarded-For": ip_addr, "Cookie" : "org="+org+";api_key="+api_key}
           
        print 'Uploading feed to: ' + url
           
        conn.request("PUT", url, "", headers)
        
        #Check for errors
        response = conn.getresponse()
        status = response.status
        
        if status != 200 and status != 201:
            try:
                if (response.reason != None):
                    print 'HTTP Failure Reason: ' + response.reason + ' body: ' + response.read()
                else:
                    print 'HTTP Failure Body: ' + response.read()
            except Exception:
                print 'HTTP Failure Status: %d' % (status) 
       
    except Exception as e:
        print 'HTTP Failure: ' + str(e)
       
    finally:
        if conn != None:
            conn.close()
    time.sleep(delay)            

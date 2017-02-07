import sys, time, os, datetime

import heliostat, light2dac

import xively
import subprocess
import requests

# extract feed_id and api_key from environment variables
try:
  FEED_ID = os.environ["FEED_ID"]
except:
  FEED_ID =  276439635
try:
  API_KEY = os.environ["API_KEY"]
except:
  API_KEY=open('/home/pi/xively.api').read().strip()
  
DEBUG=True

# initialize Xively api client
api = xively.XivelyAPIClient(API_KEY)




# here is the Xively connection info
feed = api.feeds.get(FEED_ID)

h=heliostat.heliostat(4, 7, debug=DEBUG)
if h.alt>10:
  l=light2dac.light2dac()


  h()
  l()

  feed.datastreams = [
    xively.Datastream(id='light_intensity', current_value=l.lux, at=datetime.datetime.utcnow()),
    xively.Datastream(id='sun_altitude', current_value=round(h.alt,2), at=datetime.datetime.utcnow()),
    xively.Datastream(id='sun_azimuth', current_value=round(h.az,2), at=datetime.datetime.utcnow()),
    ]
    
  if DEBUG:
    print 'Updating Xively feed with %d at %s UTC' % (l.lux,
                                                      datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
  try:
    feed.update()
  except requests.HTTPError as e:
    print "HTTPError({0}): {1}".format(e.errno, e.strerror)
 
    

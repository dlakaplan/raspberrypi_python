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

# function to return a datastream object. This either creates a new datastream,
# or returns an existing one
def get_datastream(feed):
  try:
    datastream = feed.datastreams.get("light_intensity")
    if DEBUG:
        print 'Found existing datastream'
    return datastream
  except:
    datastream = feed.datastreams.create("light_intensity", tags="light_01")
    if DEBUG:
        print 'Creating new datastream'
    return datastream



# here is the Xively connection info
feed = api.feeds.get(FEED_ID)
#datastream = get_datastream(feed)
#datastream.max_value = None
#datastream.min_value = None



h=heliostat.heliostat(4, 7, debug=True)

l=light2dac.light2dac()


while True:
    h()
    l()
    #datastream.current_value = l.lux
    #datastream.at = datetime.datetime.utcnow()

    feed.datastreams = [
        xively.Datastream(id='light_intensity', current_value=l.lux, at=datetime.datetime.utcnow()),
        xively.Datastream(id='sun_altitude', current_value=h.alt, at=datetime.datetime.utcnow()),
        xively.Datastream(id='sun_azimuth', current_value=h.az, at=datetime.datetime.utcnow()),
        ]
    
    if DEBUG:
        print 'Updating Xively feed with %d at %s UTC' % (l.lux,
                                                          datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
    try:
        feed.update()
    except requests.HTTPError as e:
        print "HTTPError({0}): {1}".format(e.errno, e.strerror)
 
    time.sleep(10)
    

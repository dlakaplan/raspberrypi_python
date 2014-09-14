import os,sys,json,urllib
from optparse import OptionParser
import datetime

APIkeyfile=os.path.join(os.environ['HOME'],
                        '.wunderground')
if not os.path.exists(APIkeyfile):
    print 'Cannot find API key: %s' % APIkeyfile
    sys.exit(1)

APIkey=open(APIkeyfile).readlines()[0].strip()

def get_conditions(station, debug=False):
    url='http://api.wunderground.com/api/%s/conditions/pwd:1/q/pws:%s.json' % (APIkey, station)
    if debug:
        print 'Requesting %s' % url
    try:
        data=urllib.urlopen(url).readlines()
    except:
        print 'Unable to retrieve bus info'
        return None
    try:
        data=json.loads('\n'.join(data))
    except:
        print 'Unable to interpret weather info'
        return None
    return data


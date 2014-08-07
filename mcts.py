"""
Use the MCTS BusTime API
to get realtime bus info
"""

import os,sys,json,urllib
from optparse import OptionParser
import datetime

APIkeyfile=os.path.join(os.environ['HOME'],
                        '.mcts')
if not os.path.exists(APIkeyfile):
    print 'Cannot find API key: %s' % APIkeyfile
    sys.exit(1)

APIkey=open(APIkeyfile).readlines()[0].strip()

Stops={'home': {'rt': '30',
                'stpid': '4365',
                'rtdir': 'EAST'},
       'office': {'rt': '30',
                  'stpid': '4377',
                  'rtdir': 'WEST'}}

Stops['work']=Stops['office']

def check_route(APIkey, rt, stpid, rtdir, n=2):
    url='http://realtime.ridemcts.com/bustime/api/v2/getpredictions'
    url+="?key=%s&rt=%s&stpid=%s&format=json" % (APIkey, rt, stpid)
    try:
        data=urllib.urlopen(url).readlines()
    except:
        print 'Unable to retrieve bus info'
        return None
    try:
        data=json.loads('\n'.join(data))
    except:
        print 'Unable to interpret bus info'
        return None
    if data['bustime-response'].has_key('error'):
        print 'Bustime return error:'
        print data
        return None
    buses_printed=0
    for bus in data['bustime-response']['prd']:
        prdtm=datetime.datetime.strptime(bus['prdtm'],'%Y%m%d %H:%M')
        timefromnow=prdtm-datetime.datetime.now()
        if not bus['rtdir']==rtdir:
            continue
        if len(bus['vid'])==0:
            continue
        delay=bus['dly']
        if 'Maryland' in bus['des']:
            bustype='M'
        else:
            bustype='D'
        print 'Bus %s(%s) due at %s in %.1f min' % (rt,
                                                    bustype,
                                                    bus['stpnm'],
                                                    timefromnow.seconds/60.0)
        buses_printed+=1
        if buses_printed==n:
            break
    return data
    
       

usage="Usage: %prog [options]\n"
parser = OptionParser(usage=usage)
parser.add_option('-l','--location',dest='location',
                  type='choice',
                  choices=['home','office','work'],
                  default='home',
                  help='Stop location [default=%default]')

(options, args) = parser.parse_args()
data=check_route(APIkey, Stops[options.location]['rt'],
                 Stops[options.location]['stpid'],
                 Stops[options.location]['rtdir'])

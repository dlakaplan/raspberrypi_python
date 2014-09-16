#!/usr/bin/env python

import datetime, json, os, sys
from optparse import OptionParser
import logging

import mcts
import wunderground

import write_ppm

Stops={'office': {'rt': '30',
                  'stpid': '4377',
                  'rtdir': 'WEST'},
       'green-north': {'rt': 'GRE',
                       'stpid': '257',
                       'rtdir': 'NORTH'},
       'green-south': {'rt': 'GRE',
                       'stpid': '1402',
                       'rtdir': 'SOUTH'}}

Station='KWIMILWA39'

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)
logger = logging.getLogger()


##################################################
class businfo():
    def __init__(self, stops=Stops):
        self.Stops=stops
        self.busdata=None
        self.directory='./'
        self.filename='businfo.data'

    def update(self):
        logger.info('Updating bus info...')
        self.busdata=None
        for stop in self.Stops.keys():
            if self.busdata is None:
                self.busdata=mcts.check_route(mcts.APIkey,
                                              self.Stops[stop]['rt'],
                                              self.Stops[stop]['stpid'],
                                              self.Stops[stop]['rtdir'],
                                              debug=False)
            else:
                temp_busdata=mcts.check_route(mcts.APIkey,
                                              self.Stops[stop]['rt'],
                                              self.Stops[stop]['stpid'],
                                              self.Stops[stop]['rtdir'],
                                              debug=False)
                for bus in temp_busdata['bustime-response']['prd']:
                    self.busdata['bustime-response']['prd'].append(bus)
        self.busdata['querytime']=datetime.datetime.now().strftime('%Y%m%d %H:%M')
        
    def writetofile(self):
        try:
            f=open(os.path.join(self.directory, self.filename), 'w')
        except:
            logger.error('Error opening %s for writing' % os.path.join(self.directory, self.filename))
        json.dump(self.busdata, f)
        f.close()
        logger.info('Bus info written to %s' % os.path.join(self.directory, self.filename))

    def readfromfile(self):
        try:
            f=open(os.path.join(self.directory, self.filename))
        except:
            logger.error('Error opening %s for reading' % os.path.join(self.directory, self.filename))
            return None
        try:
            self.busdata=json.load(f)
        except:
            logger.error('Unable to read bus data from file %s' % os.path.join(self.directory, self.filename))
            return None
        logger.info('Bus info read from %s' % os.path.join(self.directory, self.filename))
        return datetime.datetime.strptime(self.busdata['querytime'],
                                          '%Y%m%d %H:%M')
        
        
    def __str__(self):
        now=datetime.datetime.now()
        
        if self.busdata is None:
            self.update()
        sout=[]
        sout.append(now.strftime('%a %Y-%m-%d %H:%M'))
        for bus in self.busdata['bustime-response']['prd']:
            prdtm=datetime.datetime.strptime(bus['prdtm'],'%Y%m%d %H:%M')
            timefromnow=prdtm-now
            if timefromnow.seconds > 30*60:
                continue
            sym=''
            if len(bus['vid'])==0:
                sym='*'
            delay=bus['dly']
            if delay:
                sym+='(D)'
            sout.append('%s(%s) due in %d min%s' % (bus['rt'],
                                                    bus['des'],
                                                    round(timefromnow.seconds/60.0),
                                                    sym))
        return '; '.join(sout)
##################################################
class weatherinfo():
    def __init__(self, station=Station):
        self.Station=station
        self.weatherdata=None
        self.directory='./'
        self.filename='weatherinfo.data'

    def update(self):    
        logger.info('Updating weather info...')
        self.weatherdata=wunderground.get_conditions(self.Station,
                                                     debug=False)
        self.weatherdata['querytime']=datetime.datetime.now().strftime('%Y%m%d %H:%M')


    def writetofile(self):
        try:
            f=open(os.path.join(self.directory, self.filename),'w')
        except:
            logger.error('Error opening %s for writing' % os.path.join(self.directory, self.filename))
        json.dump(self.weatherdata, f)
        f.close()
        logger.info('Weather info written to %s' % os.path.join(self.directory, self.filename))

    def readfromfile(self):
        try:
            f=open(os.path.join(self.directory, self.filename))
        except:
            logger.error('Error opening %s for reading' % os.path.join(self.directory, self.filename))
            return None
        try:
            self.weatherdata=json.load(f)
        except:
            logger.error('Unable to read weather data from file %s' % os.path.join(self.directory, self.filename))
            return None
        logger.info('Weather info read from %s' % os.path.join(self.directory, self.filename))
        return datetime.datetime.strptime(self.weatherdata['querytime'],
                                          '%Y%m%d %H:%M')
                
    def __str__(self):
        now=datetime.datetime.now()
        
        if self.weatherdata is None:
            self.update()
        sout=[]
        sout.append(now.strftime('%a %Y-%m-%d %H:%M'))
        sout.append('%.1f F' % self.weatherdata['current_observation']['temp_f'])
        return '; '.join(sout)

        
##################################################
class localinfo():    
    def __init__(self, directory=None):
        self.Stops=Stops
        self.Station=Station
        if directory is None:
            self.directory='./'
        else:
            self.directory=directory
        self.businfo=businfo(stops=self.Stops)
        self.weatherinfo=weatherinfo(station=self.Station)
        self.businfo.directory=self.directory
        self.weatherinfo.directory=self.directory
        
    def update_stops(self):
        self.businfo.update()
        
    def update_weather(self):
        self.weatherinfo.update()

    def update(self):
        self.update_stops()
        self.update_weather()
        
    def writetofile(self):
        self.businfo.writetofile()
        self.weatherinfo.writetofile()

    def readfromfile(self):
        result=self.businfo.readfromfile()
        if result is None:
            logger.warning('Could not read bus info from file; updating from net...')
            self.update_stops()
            self.businfo.writetofile()
        result=self.weatherinfo.readfromfile()
        if result is None:
            logger.warning('Could not read weather info from file; updating from net...')
            self.update_weather()
            self.weatherinfo.writetofile()            
        
    def __str__(self):
        now=datetime.datetime.now()
        
        if self.businfo.busdata is None:
            logger.warning('Bus info not loaded; updating from net...')
            self.update_stops()
        if self.weatherinfo.weatherdata is None:
            logger.warning('Weather info not loaded; updating from net...')
            self.update_weather()
        sout=[]
        soutbus=str(self.businfo)
        soutweather=str(self.weatherinfo)
        
        sout.append(now.strftime('%a %Y-%m-%d %H:%M'))
        sout+=soutweather.split('; ')[1:]
        sout+=soutbus.split('; ')[1:]

        return '; '.join(sout)
    
        
    def writeimage(self, filename='localinfo.ppm'):
        sout=str(self)
        t=write_ppm.textppm(sout)
        t.write(os.path.join(self.directory, filename))
        logger.info('Local info written to %s' % os.path.join(self.directory, filename))
        
##################################################
def main():
    usage="Usage: %prog [options]\n"
    parser = OptionParser(usage=usage)
    parser.add_option('-d','--directory',dest='directory',default='./',
                      help='Output directory [default=%default]')
    parser.add_option('-u','--update',dest='update',default='none',
                      type='choice',
                      choices=['none','all','bus','weather'],
                      help='Which info (if any) to update [default=%default]')
    parser.add_option('-r','--read',dest='read',default=False,
                      action='store_true',
                      help='Read data from local files (instead of updating?)')
    parser.add_option('-w','--write',dest='write',default=False,
                      action='store_true',
                      help='Write PPM image?')
    parser.add_option('-i','--image', dest='image', default='localinfo.ppm',
                      help='Output PPM image name [default=%default]')
    parser.add_option('-v','--verbose', dest='verbose',default=False,
                      action='store_true',
                      help='Increase verbosity of output?')


    (options, args) = parser.parse_args()
    if options.verbose:
        logger.setLevel(logging.INFO)

    l=localinfo()
    l.directory=options.directory

    if options.read:
        l.readfromfile()

    if options.update == 'bus':
        l.update_stops()
        self.businfo.writetofile()
    elif options.update == 'weather':
        l.update_weather()
        self.weatherinfo.writetofile()            
    elif options.update == 'all':
        l.update()
        l.writetofile()


    if options.write:
        l.writeimage(filename=options.image)
        

######################################################################
# Running as executable
if __name__=='__main__':
    main()

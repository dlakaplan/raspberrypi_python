import mcts
import wunderground
import datetime, json
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

class localinfo():    
    def __init__(self):
        self.Stops=Stops
        self.Station=Station
        self.busdata=None
        self.weatherdata=None
        
    def update_stops(self):
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
                
    def update_weather(self):
    
        self.weatherdata=wunderground.get_conditions(self.Station,
                                                     debug=False)
        self.weatherdata['querytime']=datetime.datetime.now().strftime('%Y%m%d %H:%M')

    def update_all(self):
        self.update_stops()
        self.update_weather()

        
    def writetofile(self, filename='localinfo.data'):
        try:
            f=open(filename, 'w')
        except:
            print 'Error opening %s for writing' % filename
        json.dump(self.busdata, f)
        f.write('\n')
        json.dump(self.weatherdata, f)
        f.write('\n')
        f.close()

    def readfromfile(self, filename='localinfo.data'):
        try:
            f=open(filename)
        except:
            print 'Error opening %s for reading' % filename
        lines=f.readlines()
        f.close()
        try:
            self.busdata=json.loads(lines[0])
        except:
            print 'Unable to read bus data from file %s' % filename
        try:
            self.weatherdata=json.loads(lines[1])
        except:
            print 'Unable to read weather data from file %s' % filename
            
        
    def __str__(self):
        now=datetime.datetime.now()
        
        if self.busdata is None:
            self.update_stops()
        if self.weatherdata is None:
            self.update_weather()
        sout=[]
        sout.append(now.strftime('%a %Y-%m-%d %H:%M'))
        sout.append('%.1f F' % self.weatherdata['current_observation']['temp_f'])
        
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
    
        
    def writeimage(self, filename='localinfo.ppm'):
        sout=str(self)
        t=write_ppm.textppm(sout)
        t.write(filename)
        

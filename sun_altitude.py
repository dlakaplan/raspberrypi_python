import ephem
import numpy
import datetime
from pytz import timezone

def sun_altitude():
    observer=ephem.Observer()
    # make sure no refraction is included
    observer.long=numpy.radians( -87.8866)
    observer.lat=numpy.radians(43.0564)
    observer.elevation=.3048*642
    t=datetime.datetime.now(timezone('UTC'))
    observer.date=t.strftime('%Y/%m/%d %H:%M:%S')
    observer.epoch=ephem.J2000
    
    S=ephem.Sun()
    
    S.compute(observer)
    
    return numpy.degrees(S.alt), numpy.degrees(S.az)

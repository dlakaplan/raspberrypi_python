import numpy, matplotlib.cm as cm
import sys
import pyaudio

import pygame
pygame.init()

p=pyaudio.PyAudio()
ndevice=p.get_device_count()
for i in xrange(ndevice):
    if 'CODEC' in p.get_device_info_by_index(i)['name'] and p.get_device_info_by_index(i)['maxInputChannels']>0:
        break
idevice=i

CHUNK = 1024
FORMAT = pyaudio.paInt32
CHANNELS = p.get_device_info_by_index(idevice)['maxInputChannels']
RATE = 44100
RECORD_SECONDS = 5

greymax=16

nreads=int(RATE / CHUNK * RECORD_SECONDS)
DT=CHUNK/float(RATE)
ffdyn=numpy.fft.fftfreq(CHUNK, 1.0/RATE)[:CHUNK/2-1]
d=numpy.zeros((CHUNK*nreads,2),dtype=numpy.int32)
pdyn=numpy.ones((CHUNK/2-1, nreads))
rgbdata=numpy.zeros((pdyn.shape[0],pdyn.shape[1],3),
                    dtype=numpy.uint8)



size = width, height = pdyn.shape
screen = pygame.display.set_mode(size, 0, 32)
font = pygame.font.Font(None, 12)
c=cm.jet

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=False,
                input_device_index=idevice,
                frames_per_buffer=CHUNK)
print("* recording")
bad=0
last=0
i=0
while True:
    data = stream.read(CHUNK)
    i+=1
    if i==nreads:
        i=0
    try:

        
        d[last:(last+CHUNK),:]=numpy.fromstring(data,dtype=numpy.int32).reshape((CHUNK,2))
        # capture one channel for the dynamic spectrum
        ddyn=numpy.fromstring(data,dtype=numpy.int32).reshape((CHUNK,2))[:,0]
        
        pdyn[:,i]=(numpy.abs(numpy.fft.fft(ddyn))**2)[:CHUNK/2-1]
        
        rgbdata[:]=c(numpy.log10(pdyn)/greymax,bytes=True)[:,:,:3]
        if i < nreads-1:
            rgbdata[:,i,:]=0
        pygame.surfarray.blit_array(screen, rgbdata)
        for f in xrange(1000,22000,1000):
            x=int(f/ffdyn[1])
            text=font.render('%d' % (f/1000),
                             1, (10,10,10))
            textpos=text.get_rect(centerx=x)
            textpos[1]=height-text.get_height()
            screen.blit(text, textpos)

            pygame.draw.lines(screen, (0,0,0), False,
                              [(x,height-text.get_height()),
                               (x,height-text.get_height()-10)])
            
        pygame.display.flip()

        
    except IOError:
        print 'dropped frame'
        bad+=1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)
        elif event.type == pygame.KEYDOWN:            
            if event.unicode=='q':
                sys.exit(0)
            elif event.unicode==u'\uf700':
                greymax+=1
                print greymax
            elif event.unicode==u'\uf701':
                greymax-=1
                if greymax<1:
                    greymax=1
                print greymax
        elif event.type == pygame.MOUSEBUTTONDOWN:
            print '%.1f Hz' % (ffdyn[pygame.mouse.get_pos()[0]])

print("* done recording")
#print 'Good: %d; Bad: %d' % (good, bad)
    
stream.stop_stream()
stream.close()

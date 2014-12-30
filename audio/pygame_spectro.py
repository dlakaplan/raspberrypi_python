import numpy, matplotlib.cm as cm
import sys,datetime
import wave
try:
    import alsaaudio as aa
    _useALSA=True
except:
    import pyaudio
    _useALSA=False
import pygame

class Dynamicspectrum():
    def __init__(self, rate=44100, bits=32, time=5, chunk=1024):
        assert rate in [44100]
        assert bits in [8,16,32]
        self.CHUNK = chunk
        # make sure chunk is even
        self.CHUNK=2*(int(self.CHUNK)/2)
        self.RATE = rate
        self.RECORD_SECONDS = time
        self.bits=bits

        # initialize the audio input
        # this depends on whether we are using
        # pyaudio or alsa
        if not _useALSA:
            self.p=pyaudio.PyAudio()
            ndevice=self.p.get_device_count()
            for i in xrange(ndevice):
                if 'CODEC' in self.p.get_device_info_by_index(i)['name'] and self.p.get_device_info_by_index(i)['maxInputChannels']>0:
                    break            
            idevice=i
            self.CHANNELS = self.p.get_device_info_by_index(idevice)['maxInputChannels']
            if self.bits==32:
                self.FORMAT = pyaudio.paInt32
            elif self.bits==16:
                self.FORMAT = pyaudio.paInt32
            elif self.bits==8:
                self.FORMAT = pyaudio.paInt8            
            self.stream = self.p.open(format=self.FORMAT,
                                      channels=self.CHANNELS,
                                      rate=self.RATE,
                                      input=True,
                                      output=False,
                                      input_device_index=idevice,
                                      frames_per_buffer=self.CHUNK)
        else:
            self.stream = aa.PCM(aa.PCM_CAPTURE, aa.PCM_NONBLOCK)
            self.stream.setchannels(2)
            self.CHANNELS=2
            self.stream.setrate(self.RATE)
            self.stream.setperiodsize(self.CHUNK)
            if self.bits==32:
                self.stream.setformat(aa.PCM_FORMAT_S32_LE)
            elif self.bits==16:
                self.stream.setformat(aa.PCM_FORMAT_S16_LE)                
            elif self.bits==8:
                self.stream.setformat(aa.PCM_FORMAT_S8_LE)                
                

        # this is the number of independent reads
        # i.e. lines
        self.nreads=int(self.RATE / self.CHUNK * self.RECORD_SECONDS)
        # this is the duration of each read
        self.DT=self.CHUNK/float(self.RATE)
        # map FFT index into frequency
        self.frequencies=numpy.fft.fftfreq(self.CHUNK, 1.0/self.RATE)[:self.CHUNK/2-1]
        # this stores the actual audio data
        if self.bits==32:
            self.dtype=numpy.int32
        elif self.bits==16:
            self.dtype=numpy.int16
        elif self.bits==8:
            self.dtype=numpy.int8
            
        self.data=numpy.zeros((self.CHUNK*self.nreads,2),dtype=self.dtype)
        self.latestdata=numpy.zeros((self.CHUNK), dtype=self.dtype)

        # and the dynamic spectrum
        self.dynspec=numpy.ones((self.CHUNK/2-1, self.nreads))
        self.iread=-1

    def read(self):
        """
        read a new chunk from the input device
        """
        if not _useALSA:
            audiodata = self.stream.read(self.CHUNK)
            l=True
        else:
            l,audiodata = self.stream.read()
        if l:
            # got some new data
            self.iread+=1
            if self.iread==self.nreads:
                self.iread=0
            self.data[(self.iread*self.CHUNK):((self.iread+1)*self.CHUNK),:]=numpy.fromstring(audiodata,dtype=self.dtype).reshape((self.CHUNK,2))
            # capture one channel for the dynamic spectrum
            self.latestdata[:]=numpy.fromstring(audiodata,dtype=self.dtype).reshape((self.CHUNK,2))[:,0]
            
            self.dynspec[:,self.iread]=(numpy.abs(numpy.fft.fft(self.latestdata))**2)[:self.CHUNK/2-1]
            return True
        else:
            return False

    def save(self):
        """
        save the latest to a wav file
        """
        filename=datetime.datetime.utcnow().strftime('UT%Y%m%dT%H%M%S') + '.wav'
        
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.bits/8)
        wf.setframerate(self.RATE)
        wf.writeframes(self.data.tostring())
        wf.close()
        print 'Wrote %s' % filename


class DynamicspectrumDisplay():
    def __init__(self, shape, frequencies):
        self.greymax=16
        self.font=pygame.font.Font(None, 12)
        self.cm=cm.jet
        self.rgbdata=numpy.zeros((shape[0], shape[1], 3),
                                 dtype=numpy.uint8)
        self.frequencies=frequencies
        
    def update(self, data, i):
        """
        update the rgb array with new scaled data
        """
        self.rgbdata[:]=self.cm(numpy.log10(data)/self.greymax,bytes=True)[:,:,:3]
        if i < self.rgbdata.shape[1]:
            self.rgbdata[:,i,:]=0

    def render(self, screen):
        pygame.surfarray.blit_array(screen, self.rgbdata)
        # put in frequency ticks
        for f in xrange(1000,22000,1000):
            x=int(f/self.frequencies[1])
            text=self.font.render('%d' % (f/1000),
                                  1, (10,10,10))
            textpos=text.get_rect(centerx=x)
            textpos[1]=height-text.get_height()
            screen.blit(text, textpos)
                
            pygame.draw.lines(screen, (0,0,0), False,
                              [(x,height-text.get_height()),
                               (x,height-text.get_height()-10)])
            
pygame.init()
ds=Dynamicspectrum()
size = width, height = ds.dynspec.shape
screen = pygame.display.set_mode(size, 0, 32)
dsdisplay=DynamicspectrumDisplay(size, ds.frequencies)

print("* recording")
while True:
    new=ds.read()
    if new:
        dsdisplay.update(ds.dynspec, ds.iread)
        dsdisplay.render(screen)
                
        pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)
        elif event.type == pygame.KEYDOWN:            
            if event.unicode=='q':
                sys.exit(0)
            if event.unicode=='s':
                ds.save()
            elif event.unicode==u'\uf700':
                dsdisplay.greymax+=1
            elif event.unicode==u'\uf701':
                dsdisplay.greymax-=1
                if dsdisplay.greymax<1:
                    dsdisplay.greymax=1
        elif event.type == pygame.MOUSEBUTTONDOWN:
            print '%.1f Hz' % (ds.frequencies[pygame.mouse.get_pos()[0]])

    

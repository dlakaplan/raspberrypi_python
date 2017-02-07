import numpy, matplotlib.cm as cm
import sys,datetime
from optparse import OptionParser
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
                self.FORMAT = pyaudio.paInt16
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
                self.stream.setformat(aa.PCM_FORMAT_S8)                
                
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
        self.read_total=0
        self.skipped_total=0

    def read(self):
        """
        read a new chunk from the input device
        """
        if not _useALSA:
            try:
                audiodata = self.stream.read(self.CHUNK)
                l=True
            except IOError as e:
                #print "I/O error({0}): {1}".format(e.errno, e.strerror)
                l=False
        else:
            l,audiodata = self.stream.read()
        if l>0:
            self.read_total+=1
            # got some new data
            self.iread+=1
            if self.iread==self.nreads:
                self.iread=0
            self.data[(self.iread*self.CHUNK):((self.iread+1)*self.CHUNK),:]=numpy.fromstring(audiodata,dtype=self.dtype).reshape((self.CHUNK,2))
            # capture one channel for the dynamic spectrum
            self.latestdata[:]=numpy.fromstring(audiodata,dtype=self.dtype).reshape((self.CHUNK,2))[:,0]
            # compute the power spectrum
            self.dynspec[:,self.iread]=(numpy.abs(numpy.fft.fft(self.latestdata))**2)[:self.CHUNK/2-1]
            return True
        else:
            self.skipped_total+=1
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
    def __init__(self, shape, frequencies, bits=32):
        assert bits in [32,16,8]
        if bits==32:
            self.greymax=16
        elif bits==16:
            self.greymax=12
        elif bits==8:
            self.greymax=8
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
if _useALSA:
    # don't know why this is, but it works on the pi
    chunk=940
else:
    chunk=1024

parser = OptionParser(usage='pygame_spectro: display a live dynamic spectrograph of microphone input using pygame')
parser.add_option('-t','--time',dest="time",default=5,
                  help="Recording interval for display (s) [default=%default]")
parser.add_option('-b','--bits',dest="bits",default='32',
                  type='choice',choices=['32','16','8'],
                  help='Bits per sample [default=%default]')
(options, args) = parser.parse_args()


ds=Dynamicspectrum(chunk=chunk, bits=int(options.bits), time=options.time)
size = width, height = ds.dynspec.shape
screen = pygame.display.set_mode(size, 0, 32)
dsdisplay=DynamicspectrumDisplay(size, ds.frequencies, bits=ds.bits)

print("* recording")
while True:
    new=ds.read()
    if new:
        dsdisplay.update(ds.dynspec, ds.iread)
        dsdisplay.render(screen)
                
        pygame.display.flip()
        pass

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)
        elif event.type == pygame.KEYDOWN:            
            if event.unicode=='q':
                print 'Read %d / Skipped %d (%.1f%% good)' % (ds.read_total,
                                                              ds.skipped_total,
                                                              100*float(ds.read_total)/(ds.read_total+ds.skipped_total))
                sys.exit(0)
            if event.unicode=='s':
                ds.save()            
            elif event.unicode==u'\uf700' or event.key==273:
                # this should be up
                # don't know why the unicode is different on pi and mac
                dsdisplay.greymax+=1
            elif event.unicode==u'\uf701' or event.key==274:
                # this should be down
                dsdisplay.greymax-=1
                if dsdisplay.greymax<1:
                    dsdisplay.greymax=1
        elif event.type == pygame.MOUSEBUTTONDOWN:
            print '%.1f Hz' % (ds.frequencies[pygame.mouse.get_pos()[0]])

    

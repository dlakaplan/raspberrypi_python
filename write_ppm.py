from PIL import Image,ImageFont,ImageDraw
import os

_height=16
_width=32
_fonts=['/usr/local/texlive/2011/texmf-dist/fonts/truetype/public/gnu-freefont/FreeSans.ttf',
        '/usr/share/fonts/truetype/freefont/FreeSans.ttf']
for _font in _fonts:
    if os.path.exists(_font):
        break
if not os.path.exists(_font):
    print 'No font file found'
    _font=None
_fontsize=12

class textppm():

    def __init__(self, text,
                 color=(255,255,255),
                 font=_font,
                 fontsize=_fontsize,
                 height=_height,
                 width=_width):
        if len(color)==1:
            self.color=(color,color,color)
        else:
            self.color=color
        self.fontsize=_fontsize
        try:
            self.font=ImageFont.truetype(_font,
                                         self.fontsize)
        except:
            self.font=ImageFont.load_default()
        if len(text)>0:
            self.drawtext(text)
        else:
            self.text=None
            self.im=None
            self.drawtext=None
            self.width=None
            


    def drawtext(self, text):
        self.text=text
        self.im = Image.new("RGB", (_width, _height))
        self.draw = ImageDraw.Draw(self.im)
        self.width=self.font.getsize(self.text)[0]
        self.im = Image.new("RGB", (self.width, _height))
        self.draw = ImageDraw.Draw(self.im)

        self.draw.text((0, 0),self.text,
                       self.color,
                       font=self.font)

    def write(self, filename):
        self.im.save(filename)
        


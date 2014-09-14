from PIL import Image,ImageFont,ImageDraw

_height=16
_width=32
_font='/usr/local/texlive/2011/texmf-dist/fonts/truetype/public/gnu-freefont/FreeSans.ttf'
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
        

t=textppm('Sample text ABC cats')
t.write('out.png')

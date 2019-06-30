# encoding: utf-8


import ctypes
import numpy as np
import itertools
import os.path

from PIL import Image, ImageDraw, ImageFont

from pi3d.constants import *
import pi3d

from math import sqrt, ceil

CODEPOINTS = list(range(32, 126)) + list(range(160,255)) + ['ʒ', '~', 'ä']
TEXTURE_SIZE = 2048

class Font(pi3d.Texture):

    def __init__(self, font, codepoints, size):
        """Arguments:
        *font*:
            File path/name to a TrueType font file.

        *codepoints*:
            Iterable list of characters. All these formats will work:

                'ABCDEabcde '
                [65, 66, 67, 68, 69, 97, 98, 99, 100, 101, 145, 148, 172, 32]
                [c for c in range(65, 173)]

            Note that Font will ONLY use the codepoints in this list - if you
            forget to list a codepoint or character here, it won't be displayed.

            If the string version is used then the program file might need to
            have the coding defined at the top:    # -*- coding: utf-8 -*-

            The default is *codepoints*=range(256).


        """
        super(Font, self).__init__(font, automatic_resize=False)

        self.font = font

        if codepoints is not None:
            codepoints = list(codepoints)
        else:
            codepoints = list(range(256))

        ch_per_line = int(ceil(sqrt(len(codepoints))))

        font_size = int(size / ch_per_line / 1.2)
        imgfont = ImageFont.truetype(font, font_size)
        ascent, descent = imgfont.getmetrics()
        self.line_height = int(size / ch_per_line)

        y_correction = 0# (self.line_height-ascent-descent) / 2
        glyph_img = Image.new("RGBA", (size, size), (0, 0, 0, 255))


        self.ix, self.iy = size, size

        self.glyph_table = {}

        draw = ImageDraw.Draw(glyph_img)

        curX = 0.0
        curY = 0.0
        yindex = 0
        xindex = 0

        self.ratio = 1.0
        self.nominal_height = 0

        for i in itertools.chain([0], codepoints):

            try:
                ch = chr(i)
            except TypeError:
                ch = i

            chwidth, chheight = imgfont.getsize(ch)
            chwidth += 10

            if ch == 'A':
                self.nominal_height = chheight
                self.ratio = 1.0 * chheight / chwidth

            curX = xindex * self.line_height
            curY = yindex * self.line_height

            h_offset = (self.line_height - chwidth) / 2.0
            draw.text((curX + h_offset, curY), ch, font=imgfont, fill=(255,255,255,255))

            x = float(curX + h_offset) / self.ix
            y = float(curY + self.line_height - y_correction) / self.iy
            tw = float(chwidth) / self.ix
            th = float(self.line_height) / self.iy

            table_entry = [
                chwidth,
                chheight,
                [[x + tw, y - th], [x , y - th], [x, y], [x + tw, y]], # UV texture coordinates
                [[chwidth, 0, 0], [0, 0, 0], [0, -self.line_height, 0], [chwidth, -self.line_height, 0]], # xyz vertex coordinates of corners
            ]

            self.glyph_table[ch] = table_entry

            xindex += 1
            if xindex >= ch_per_line:
                xindex = 0
                yindex += 1

        self.image = np.array(glyph_img)

        self._tex = ctypes.c_uint()


    def _load_disk(self):
        """
        we need to stop the normal file loading by overriding this method
        """


class SdfFont(Font):

    def __init__(self, font, codepoints=CODEPOINTS, size=TEXTURE_SIZE):

        super(SdfFont, self).__init__(font, codepoints, size)

        self.sdf_path = '.'.join(self.font.split('.')[0:-1]) + '-sdf.png'

        try:
            self.load_sdf()
        except:
            self.create_sdf()

    def create_sdf(self):
        from subprocess import call
        print('Generating hi-res font texture for %s' % self.font)
        tmp = Font(self.font, size=TEXTURE_SIZE*8, sdf_tmp=True)
        image = Image.fromarray(tmp.image)
        image.save(self.sdf_path)
        print('Generating signed distance field for %s' % self.font)
        call(['./fonts/sdfgen', self.sdf_path, self.sdf_path, '--maxdst', '200', '--size', str(TEXTURE_SIZE)])
        self.load_sdf()


    def load_sdf(self):
        tex = pi3d.Texture(self.sdf_path, automatic_resize=False)
        self.image =  tex.image

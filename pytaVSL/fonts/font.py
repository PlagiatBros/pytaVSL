# encoding: utf-8


import ctypes
import numpy as np
import itertools
import os.path
import json

from PIL import Image, ImageDraw, ImageFont

from pi3d.constants import *
import pi3d

class MsdfFont(pi3d.Texture):

    def __init__(self, font):
        """Arguments:
        *font*:
            File path/name to a msdf-bmfont font file.
        """

        self.mono = 'mono' in font.lower()

        super(MsdfFont, self).__init__(font, automatic_resize=False)

        self.glyph_table = {}

        font_data = json.loads(open(font.replace('.png', '.json'), 'r').read())
        self.line_height = font_data['common']['lineHeight']
        for char in font_data ['chars']:

            x = char['x'] / self.ix
            y = 1 - char['y'] / self.iy
            w = char['width'] / self.ix
            h = char['height'] / self.iy

            self.glyph_table[char['char']] = [
                char['xadvance'],
                char['height'],
                [[x + w, y], [x, y], [x, y - h], [x + w, y - h]], # tex coords
                [[char['width'] + char['xoffset'], -char['yoffset'], 0], [0, -char['yoffset'], 0], [0, -char['yoffset']-char['height'], 0], [char['width'] + char['xoffset'], -char['yoffset']-char['height'], 0]] # vertex
            ]

        self.nominal_height = self.glyph_table['A'][1]
        self.ratio = self.glyph_table['A'][1] / self.glyph_table['A'][0]


    def get_glyph(self, char):

        return self.glyph_table[char] if char in self.glyph_table else self.glyph_table[' ']

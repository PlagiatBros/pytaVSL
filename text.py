#!/usr/bin/python
# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

"""This is the main file of pytaVSL. It aims to provide a VJing and lights-projector-virtualisation tool.

Images are loaded as textures, which then are mapped onto slides (canvases - 8 of them).

This file was deeply instpired by Slideshow.py demo file of pi3d.
"""

import time, glob, threading
import pi3d
import liblo
import random
import os.path
import os
import sys
import getopt
import math

from six.moves import queue
from font import Font

# LOGGER = pi3d.Log.logger(__name__)
LOGGER = pi3d.Log()
LOGGER.info("Log using this expression.")

FONT_SIZE = 220
FONTS = {
    "sans": Font('sans.ttf', background_color=(0,0,0,0), font_size=FONT_SIZE),
    "mono": Font('sans.ttf', background_color=(0,0,0,0), font_size=FONT_SIZE)
}


class Text:
    def __init__(self, parent, font="sans"):

        self.parent = parent

        self.font = FONTS[font]
        self.font.blend=True
        self.font.mipmap=True

        self.shader = pi3d.Shader("uv_flat")

        self.string = ''
        self.color = (1.0, 1.0, 1.0)
        self.size = 1
        self.h_align = 'C'
        self.v_align = 'C'

        self.x = 0
        self.y = 0

        self.need_regen = False
        self.regen()

    def set_text(self, string):
        self.string = string
        if len(self.string) == len(self.text.string):
            self.text.quick_change(self.string)
        else:
            self.need_regen = True

    def set_color(self, color):
        self.color = color
        self.need_regen = True

    def set_align(self, h, v):
        h = h[0].upper()
        v = v[0].upper()
        if h in ['C', 'L', 'R']:
            self.set_h_align(h)
        if v in ['C', 'T', 'B']:
            self.set_v_align(v)

    def set_v_align(self, align):
        self.v_align = align
        self.need_regen = True

    def set_h_align(self, align):
        self.h_align = align
        self.need_regen = True

    def set_size(self, size):
        self.size = min(max(float(size),0.),1.)
        self.need_regen = True

    def regen(self):

        x = self.x
        y = self.y

        if self.h_align == 'L':
            x -= self.parent.DISPLAY.width / 2.
        elif self.h_align == 'R':
            x += self.parent.DISPLAY.width / 2.

        if self.v_align == 'T':
            y = y + self.parent.DISPLAY.height / 2. - FONT_SIZE * self.size * 2
        elif self.v_align == 'B':
            y = y - self.parent.DISPLAY.height / 2. + FONT_SIZE * self.size * 2

        self.text = pi3d.String(font=self.font, string=self.string, size=self.size,
                      camera=self.parent.CAMERA, x=x, y=y, z=1.0, is_3d=False, justify=self.h_align)
        self.text.set_shader(self.shader)

    def draw(self):
        # pipshow mode for testing
        # r = random.random()
        # self.string = str(r) if r > 0.5 else ''
        # self.changed = True
        if self.need_regen:
            self.need_regen = False
            self.regen()

        self.text.set_material(self.color)
        self.text.draw()

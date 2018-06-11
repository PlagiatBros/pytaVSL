#!/usr/bin/python
# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

"""This is the main file of pytaVSL. It aims to provide a VJing and lights-projector-virtualisation tool.

Images are loaded as textures, which then are mapped onto slides (canvases - 8 of them).

This file was deeply instpired by Slideshow.py demo file of pi3d.
"""

import time, glob
import pi3d
import liblo
import random
import os.path
import os
import sys
import getopt
import math

from utils import KillableThread as Thread

from six.moves import queue
from font import Font

LOGGER = pi3d.Log()

RESOLUTION = 0.5

FONTS = {
    "sans": Font('sans.ttf', color=(127,127,127,255), background_color=(0,0,0,0), font_size=int(170*RESOLUTION), offset_y=0.015),
    "mono": Font('mono.ttf', color=(127,127,127,255), background_color=(0,0,0,0), font_size=int(200*RESOLUTION), offset_y=-0.005,
                add_codepoints=range(439, 441)) # ʒ
}

V_ALIGN = ['C', 'B', 'T']
H_ALIGN = ['C', 'L', 'R']

class Text:
    """
    Dynamic text
    """
    def __init__(self, parent, font="mono"):
        """
        Text constructur

        Args:
            font (str): "sans" or "mono" (see FONTS global)
        """

        self.parent = parent

        self.font = FONTS[font]

        self.shader = pi3d.Shader("uv_flat")

        self.visible = True

        self.strobe = False
        self.strobe_state = True

        self.string = ''
        self.color = (1.0, 1.0, 1.0)
        self.color_strobe = False
        self.alpha = 1.0

        self.size = 1

        self.h_align = 'C'
        self.v_align = 'C'

        self.x = 0
        self.y = 0

        self.rx = 0
        self.ry = 0
        self.rz = 0

        self.animations = {}

        self.need_regen = False
        self.new_string()

    def new_string(self):
        """
        Generate a new string instance and apply all options.
        """

        x = self.x
        y = self.y

        if self.h_align == 'L':
            x -= self.parent.DISPLAY.width / 2.
        elif self.h_align == 'R':
            x += self.parent.DISPLAY.width / 2.

        if self.v_align == 'T':
            y = y + self.parent.DISPLAY.height / 2. - self.font.size * self.size * 2
        elif self.v_align == 'B':
            y = y - self.parent.DISPLAY.height / 2. + self.font.size * self.size * 2

        self.text = pi3d.String(font=self.font, string=self.string, size=self.size/RESOLUTION,
                      camera=self.parent.CAMERA, x=x, y=y, z=1000, is_3d=False,
                      justify=self.h_align, rx=self.rx, ry=self.ry, rz=self.rz)

        self.text.set_shader(self.shader)

    def draw(self):

        if self.need_regen:
            self.need_regen = False
            self.new_string()

        if self.strobe:
            self.strobe_state = not self.strobe_state

        if self.visible and self.string and (not self.strobe or self.strobe_state):

            if len(self.string) == len(self.text.string):
                self.text.quick_change(self.string)

            if self.color_strobe:
                self.text.set_material((random.random(),random.random(),random.random()))
            else:
                self.text.set_material(self.color)

            self.text.draw()

    def set_text(self, string):
        """
        Set the text's string regenerate inner String instance
        if the string's length has changed, otherwise use optimized
        quick_change method (can distort some characters).
        """

        self.string = string
        if len(self.string) != len(self.text.string):
            self.need_regen = True


    def set_color(self, color):
        """
        Set the text's color. Triggers String regeneration.

        Args:
            color (tuple): rgb float values between 0.0 and 1.0
        """
        self.color = color
        self.need_regen = True

    def set_alpha(self, alpha):
        """
        Set the text's opacity.

        Args:
            alpha (tuple): alpha float values between 0.0 and 1.0
        """
        if alpha != self.alpha:
            self.alpha = alpha
            self.text.set_alpha(self.alpha)

    def set_color_strobe(self, strobe):
        self.color_strobe = bool(strobe)

    def set_align(self, h, v):
        """
        Set horizontal and vertical alignments with support for inverted args.
        Triggers String regeneration.

        Args:
            h (str): center, left or right (only the first letter is parsed)
            v (str): center, top or bottom (only the first letter is parsed)
        """
        h = h[0].upper()
        v = v[0].upper()
        reverse = False

        if h == v and h == 'C':
            self.set_h_align(h)
            self.set_v_align(v)
            return

        if (v != 'C' and v in H_ALIGN) or (h != 'C' and h in V_ALIGN):
            # invert args
            a = v
            v = h
            h = a

        if h in H_ALIGN:
            self.set_h_align(h)
        if v in V_ALIGN:
            self.set_v_align(v)

    def set_h_align(self, align):
        """
        Set heorizontal alignment. Triggers String regeneration.

        Args:
            align (str): C, L or R
        """
        self.h_align = align
        self.need_regen = True

    def set_v_align(self, align):
        """
        Set vertical alignment. Triggers String regeneration.

        Args:
            align (str): C, T or B
        """
        self.v_align = align
        self.need_regen = True

    def set_position(self, x, y):
        """
        Set position (relative to alignment). Triggers String regeneration.

        Args:
            x (int): horizontal offset in pixels
            y (int): vertical offset in pixels
        """
        self.x = x
        self.y = y
        self.text.positionX(self.x)
        self.text.positionY(self.x)

    def set_rotation(self, rx, ry, rz):
        """
        Set rotation. Triggers String regeneration.

        Args:
            rx (float):
            ry (float):
            rz (float):
        """
        if rx is not None:
            self.rx = rx
            self.text.rotateToX(self.rx)
        if ry is not None:
            self.ry = ry
            self.text.rotateToY(self.ry)
        if rz is not None:
            self.rz = rz
            self.text.rotateToZ(self.rz)

    def set_size(self, size):
        """
        Set size. Triggers String regeneration.

        Args:
            size (float): between 0.0 and 1.0. 1.0 for full height characters
        """
        self.size = min(max(float(size),0.),1.)
        s = self.size * 4.0 * RESOLUTION
        self.text.scale(s, s, 1.0)

    def set_visible(self, visible):
        """
        Set visibility.

        Args:
            visible (bool): True to show, False to hide
        """
        self.visible = bool(visible)

    def set_strobe(self, strobe):
        """
        Set strobe mode

        Args:
            strobe (bool): True to enable strobe mode
        """
        self.strobe_state = False
        self.strobe = bool(strobe)

    def animate(self, name, start, end, duration):
        """
        Animate one of the Text's properties (25fps)

        Args:
            name  (str):
            start (int):
            end   (int):
            duration (float):
        """
        def threaded():

            nb_step = int(round(duration * 25.))

            if nb_step < 1:
                return

            a = float(end - start) / nb_step

            set_val = self.get_animate_function(name)

            for i in range(nb_step + 1):

                set_val(a * i + start)

                time.sleep(1/25.)

        if name in self.animations:
            self.animations[name].kill()

        self.animations[name] = Thread(target=threaded)
        self.animations[name].start()

    def get_animate_function(self, name):
        if name == 'size':
            def set_val(val):
                self.set_size(val)
        else:
            def set_val(val):
                pass
        return set_val

# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import pi3d
from pi3d.Display import Display
import random

from strobe import Strobe
from animation import Animable
from pi3d_string import String

try:
    # python3 compat
    unicode
except:
    unicode = str

from pi3d_font import Font
from config import *

import logging
LOGGER = logging.getLogger(__name__)

FONTS = {
    "sans": Font('fonts/sans.ttf', color=(127,127,127,255), background_color=(0,0,0,0), font_size=int(170*TEXT_RESOLUTION), offset_y=0.015, codepoints=CODEPOINTS),
    "mono": Font('fonts/mono.ttf', color=(127,127,127,255), background_color=(0,0,0,0), font_size=int(200*TEXT_RESOLUTION), offset_y=-0.005, codepoints=CODEPOINTS)
}
V_ALIGN = ['C', 'B', 'T']
H_ALIGN = ['C', 'L', 'R']

class Text(Strobe, Animable):
    """
    Dynamic text
    """
    def __init__(self, shader, font="mono", z=-100):
        """
        Text constructur

        Args:
            font (str): "sans" or "mono" (see FONTS global)
        """

        super(Text, self).__init__()

        self.font = FONTS[font]
        self.shader = shader

        self.visible = True

        self.string = ' '
        self.length = max(len(self.string), 1)
        self.color = (1.0, 1.0, 1.0)
        self.color_strobe = False

        self.size = 'auto'

        self.h_align = 'C'
        self.v_align = 'C'

        self.x = 0
        self.y = 0
        self.z = z
        self.align_offset = [0, 0]

        self.sx = 1
        self.sy = 1

        self.rx = 0
        self.ry = 0
        self.rz = 0

        self.need_regen = False
        self.new_string()

        # cool
        self.glitch = False
        self.glitch_from = None
        self.glitch_to = None
        self.glitch_duration = 1
        self.glitch_start = 0

    def new_string(self):
        """
        Generate a new string instance and apply all options.
        """

        size = self.font.ratio / self.length if self.size == 'auto' else self.size

        self.text = String(font=self.font, string=self.string, size=size / TEXT_RESOLUTION,
                      x=0, y=0, z=self.z, is_3d=False,
                      justify=self.h_align, rx=self.rx, ry=self.ry, rz=self.rz)

        self.text.set_shader(self.shader)

        self.set_v_align(self.v_align)

        self.text.scale(self.sx, self.sy, 1)


    def draw(self):

        if self.glitch:
            self.glitch_next()

        if self.string == '':
            return

        self.animate_next_frame()

        if self.need_regen:
            self.need_regen = False
            self.new_string()

        if self.visible and self.string and (not self.strobe or self.strobe_state.visible()):

            if self.color_strobe > 0:
                zero = random.randint(0, 2)
                rgb = [0,0,0]
                rgb[(zero + 1) % 3] = -random.random() * self.color_strobe / 2
                rgb[(zero - 1) % 3] = random.random() * self.color_strobe
                rgb[zero] = random.random() * 1
                self.text.set_material(rgb)
            else:
                self.text.set_material(self.color)

            self.text.draw()
            # self.children = [self.text]
            # super(Text, self).draw()

    def set_text(self, string, duration=None, stop_glitch=True):
        """
        Set the text's string
        """

        if duration is not None:
            return self.set_glitch(string, duration)
        if stop_glitch:
            self.glitch = False

        self.string = string.decode('utf8')

        if '\n' in self.string:
            self.length = max(max(map(lambda line: len(line), self.string.split('\n'))), 1)
        else:
            self.length = max(len(self.string), 1)

        self.need_regen = True

    def set_glitch(self, string, duration=1):
        """
        Glitch from current string to another

        Args:
            string  (string): destination string
            duration (float): glitch duration
        """
        self.glitch = True
        self.glitch_from = self.string
        self.glitch_to = string
        self.glitch_start = Display.INSTANCE.time
        if isinstance(duration, (float, int)):
            self.glitch_duration = max(duration, 0.01)

    def glitch_next(self):
        """
        Compute current glitched text
        """
        progress = min(1, (Display.INSTANCE.time - self.glitch_start) / self.glitch_duration)

        if progress == 1.0:
            self.set_text(self.glitch_to)
        else:
            if random.random()>0.75:
                return

            string = ""

            for i in range(len(self.glitch_to)):
                r = random.random() / 2
                c = self.glitch_to[i]
                str_from = self.glitch_from if random.random() > 0.5 else self.string
                if progress < r:
                    c = str_from[random.randint(0, len(str_from)-1)] if len(str_from) > 0 else " "
                if r > 0.48:
                    c = c.upper()

                string += c

            self.set_text(string, stop_glitch=False)

    def set_color(self, color):
        """
        Set the text's color. Triggers String regeneration.

        Args:
            color (tuple): rgb float values between 0.0 and 1.0
        """
        self.color = color

    def set_alpha(self, alpha):
        """
        Set the text's opacity.

        Args:
            alpha (tuple): alpha float values between 0.0 and 1.0
        """
        self.text.set_alpha(alpha)

    def set_color_strobe(self, strobe):
        self.color_strobe = strobe

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

        if h in H_ALIGN and h != self.h_align:
            self.set_h_align(h)
        if v in V_ALIGN and v != self.v_align:
            self.set_v_align(v)

    def set_h_align(self, align):
        """
        Set heorizontal alignment. Triggers String regeneration.

        Args:
            align (str): C, L or R
        """
        self.h_align = align

        x = 0

        if self.h_align == 'L':
            x = - Display.INSTANCE.width / 2.
        elif self.h_align == 'R':
            x = Display.INSTANCE.width / 2.

        self.align_offset[0] = x
        self.set_position(self.x, self.y)
        self.need_regen = True

    def set_v_align(self, align):
        """
        Set vertical alignment. Triggers String regeneration.

        Args:
            align (str): C, T or B
        """
        self.v_align = align

        size = self.font.ratio / self.length if self.size == 'auto' else self.size

        y = 0

        if self.v_align == 'T':
            y = Display.INSTANCE.height / 2. - self.font.size * size * self.sy * 2 / TEXT_RESOLUTION * (1+self.string.count('\n'))
        elif self.v_align == 'B':
            y = - Display.INSTANCE.height / 2. + self.font.size * size * self.sy * 2 / TEXT_RESOLUTION * (1+self.string.count('\n'))

        self.align_offset[1] = y
        self.set_position(self.x, self.y)

    def set_position(self, x, y):
        """
        Set position (relative to alignment). Triggers String regeneration.

        Args:
            x (int): horizontal offset in pixels
            y (int): vertical offset in pixels
        """
        self.x = x
        self.y = y
        self.text.position(self.x + self.align_offset[0], self.y + self.align_offset[1], self.text.z())

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
            size (str|float): 'auto' or between 0.0 and 1.0. 1.0 for full height characters
        """
        if size == 'auto':
            self.size = 'auto'
        elif size == 'current':
            self.size = self.font.ratio / self.length
        elif isinstance(size, (int, float)):
            self.size = float(size)

        self.need_regen = True

    def set_scale(self, sx, sy):
        """
        set_scale sets the scale of the text
        """
        self.sx = sx
        self.sy = sy

        if self.v_align != 'C':
            self.need_regen = True
        else:
            self.text.scale(sx, sy, 1)

    def set_zoom(self, zoom):
        """
        Scaling relative to initial size, aka zoom
        """
        self.set_scale(zoom, zoom)

    def set_visible(self, visible):
        """
        Set visibility.

        Args:
            visible (bool): True to show, False to hide
        """
        self.visible = bool(visible)

    def reset(self):
        self.set_size('auto')
        self.set_scale(1, 1)
        self.set_strobe(0, 2, 0.5)
        self.set_rotation(0, 0, 0)
        self.set_position(0, 0)
        self.set_align('c', 'c')
        self.set_alpha(1)
        self.set_color((1, 1, 1))
        self.set_color_strobe(False)
        self.set_visible(0)
        self.set_text('')
        self.stop_animate()

    def get_param_getter(self, name):
        """
        Getters for animations
        """
        val = 0
        if name == 'size':
            val = self.font.ratio / self.length if self.size == 'auto' else self.size
        elif name == 'position_x':
            val = self.x
        elif name == 'position_y':
            val = self.y
        elif name == 'rotate_x':
            val = self.rx
        elif name == 'rotate_y':
            val = self.ry
        elif name == 'rotate_z':
            val = self.rz
        elif name == 'scale_x':
            val = self.sx
        elif name == 'scale_y':
            val = self.sy
        elif name == 'zoom':
            val = self.sx
        elif name == 'alpha':
            val = self.text.alpha()

        return val

    def get_param_setter(self, name):
        """
        Setters for one-arg animations
        """
        if name == 'size':
            def set_val(val):
                self.set_size(val)
        elif name == 'rotate_x':
            def set_val(val):
                self.set_rotation(val, None, None)
        elif name == 'rotate_y':
            def set_val(val):
                self.set_rotation(None, val, None)
        elif name == 'rotate_z':
            def set_val(val):
                self.set_rotation(None, None, val)
        elif name == 'scale_x':
            def set_val(val):
                self.set_scale(val, self.sy)
        elif name == 'scale_y':
            def set_val(val):
                self.set_scale(self.sx, val)
        elif name == 'zoom':
            def set_val(val):
                self.set_zoom(val)
        elif name == 'position_x':
            def set_val(val):
                self.set_position(val, None)
        elif name == 'position_y':
            def set_val(val):
                self.set_position(None, val)
        elif name == 'alpha':
            def set_val(val):
                self.set_alpha(val)
        else:
            set_val = None

        return set_val

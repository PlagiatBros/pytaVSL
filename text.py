# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import pi3d
from pi3d.Display import Display
import random

from state import State
from slide import SlideBase
from perspective import Perspective
from utils import unicode, unichr
from osc import osc_property
from pi3d_font import Font
from config import *

import logging
LOGGER = logging.getLogger(__name__)

V_ALIGN = ['C', 'B', 'T']
H_ALIGN = ['C', 'L', 'R']
_NORMALS = [[0.0, 0.0, -1.0], [0.0, 0.0, -1.0], [0.0, 0.0, -1.0], [0.0, 0.0, -1.0]]
GAP = 1

class Text(State, Perspective, SlideBase):
    """
    Dynamic text
    """
    def __init__(self, parent, name, font="mono", init_z=0.0):

        self.font = font

        self.string = ' '
        self.length = max(len(self.string), 1)

        self.size = 'auto'

        self.h_align = 'C'
        self.v_align = 'C'

        self.align_offset = [0, 0]

        self.need_regen = False

        # cool
        self.glitch = False
        self.glitch_from = None
        self.glitch_to = None
        self.glitch_duration = 1
        self.glitch_start = 0

        super(Text, self).__init__(parent, name, texture=self.font, width=Display.INSTANCE.width, height=Display.INSTANCE.height, init_z=init_z)

        self.color = [1.0, 1.0, 1.0]

        self.new_string() # remove ?


    def new_string(self):
        """
        Update string buffer. Mostly copied from pi3d.String
        """
        size = min(1, self.font.ratio / self.length) if self.size == 'auto' else self.size
        size /= TEXT_RESOLUTION
        size /= 600. / Display.INSTANCE.height # size was calibrated on 800x600

        justify = self.h_align
        string = self.string
        font = self.font

        sy = sx = size * 4.0

        sy *= self.sy
        sx *= self.sx

        self.verts = []
        self.texcoords = []
        self.norms = []
        self.inds = []
        temp_verts = []

        xoff = 0.0
        yoff = 0.0
        lines = 0
        nlines = string.count("\n") + 1

        def make_verts(): #local function to justify each line
            if justify.upper() == "C":
                cx = xoff / 2.0
            elif justify.upper() == "L":
                cx = 0.0
            else:
                cx = xoff
            for j in temp_verts:
                self.verts.append([(j[0] - cx) * sx,
                                 (j[1] + nlines * font.height * GAP / 2.0 - yoff) * sy,
                                 j[2]])

        default = font.glyph_table.get(unichr(0), None)
        for i, c in enumerate(string):
            if c == '\n':
                make_verts()
                yoff += font.height * GAP
                xoff = 0.0
                temp_verts = []
                lines += 1
                continue #don't attempt to draw this character!

            glyph = font.glyph_table.get(c, default)
            if not glyph:
                continue
            w, h, texc, verts = glyph[0:4]
            for j in verts:
                temp_verts.append((j[0]+xoff, j[1], j[2]))
            xoff += w
            for j in texc:
                self.texcoords.append(j)
            self.norms.extend(_NORMALS)

            # Take Into account unprinted \n characters
            stv = 4 * (i - lines)
            self.inds.extend([[stv, stv + 2, stv + 1], [stv, stv + 3, stv + 2]])

        make_verts()

        self.buf = [pi3d.Buffer(self, self.verts, self.texcoords, self.inds, self.norms)]
        self.buf[0].textures = [font]

        # only used in PostProcess
        self.buf[0].unib[13] = 0.0
        # only used in Video
        self.buf[0].unib[12] = 0.0

        self.set_v_align(self.v_align)
        self.set_h_align(self.h_align)
        self.set_shader(self.shader)
        self.set_scale(self.sx, self.sy)
        self.set_material(self.color)
        self.set_tiles(*self.tiles)

    def draw(self, *args, **kwargs):

        if self.visible:

            if self.glitch:
                self.glitch_next()

            if self.string == '':
                return

            if self.need_regen:
                self.new_string()
                self.need_regen = False

            super(Text, self).draw(*args, **kwargs)

    def scale(self, sx, sy, sz):
        """
        Override Slide.scale to trigger string regeneration when needed
        """
        super(Text, self).scale(sx, sy, sz)
        if self.v_align != 'C':
            self.need_regen = True

    def position(self, x, y, z):
        """
        Override Shape.position to take text alignment into account
        """
        super(Text, self).position(x + self.align_offset[0], y + self.align_offset[1], z)


    def set_text(self, string, duration=0, stop_glitch=True):
        """
        Set the text's string
        """

        if duration != 0:
            return self.set_glitch(string, duration)
        if stop_glitch:
            self.glitch = False

        if unicode is str:
            self.string = str(string)
        else:
            self.string = str(string).decode('utf8')

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

            self.set_text(string, 0, False)


    @osc_property('text', 'string')
    def set_text_osc(self, text, glitch_duration=0):
        """
        text string with optional glitch duration
        """
        self.set_text(text, glitch_duration)

    @osc_property('align', 'h_align', 'v_align')
    def set_align(self, h, v):
        """
        horizontal and vertical alignment (center|left|right, center|top|bottom)
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

    @osc_property('align_h', 'h_align')
    def set_h_align(self, align):
        """
        horizontal alignment (center|left|right)
        """
        align = str(align)[0].upper()

        if align == self.h_align:
            return

        self.h_align = align

        x = 0

        if self.h_align == 'L':
            x = - Display.INSTANCE.width / 2.
        elif self.h_align == 'R':
            x = Display.INSTANCE.width / 2.

        self.align_offset[0] = x
        self.set_position(self.pos_x, self.pos_y, None)
        self.need_regen = True

    @osc_property('align_v', 'v_align')
    def set_v_align(self, align):
        """
        vertical alignment (center|top|bottom)
        """
        align = str(align)[0].upper()

        if align == self.v_align:
            return

        self.v_align = align

        size = min(1, self.font.ratio / self.length) if self.size == 'auto' else self.size

        y = 0

        if self.v_align == 'T':
            y = Display.INSTANCE.height / 2. - self.font.size * size * self.sy * 2 / TEXT_RESOLUTION * (1+self.string.count('\n'))
        elif self.v_align == 'B':
            y = - Display.INSTANCE.height / 2. + self.font.size * size * self.sy * 2 / TEXT_RESOLUTION * (1+self.string.count('\n'))

        self.align_offset[1] = y
        self.set_position(self.pos_x, self.pos_y, None)


    @osc_property('size', 'size')
    def set_size(self, size):
        """
        text size (1=full height, "auto"=fit, "current"=fix current size if "auto")
        """
        if size == 'auto':
            self.size = 'auto'
        elif size == 'current':
            self.size = self.font.ratio / self.length
        elif isinstance(size, (int, float)):
            self.size = float(size)

        self.need_regen = True

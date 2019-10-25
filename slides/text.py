# encoding: utf-8

import pi3d
import random

from state import State
from slide import SlideBase
from perspective import Perspective
from osc import osc_property
from config import *

import logging
LOGGER = logging.getLogger(__name__)

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
        self.computed_size = 0

        self.need_regen = False
        self.last_draw_align_h = 'center'

        # cool
        self.glitch_duration = 1
        self.glitch_start = 0
        self.glitch = False
        self.glitch_to = None
        self.glitch_indices = []

        self.letter_spacing = 1.

        self.outline = 0.0
        self.outline_color = [1.0, 0.0, 0.0]

        super(Text, self).__init__(parent, name, texture=self.font, width=parent.width, height=parent.height, init_z=init_z)

        self.color = [1.0, 1.0, 1.0]
        self.active_effects.append('TEXT')

        # fix alignment (handled in new_string())
        self.width = 0

        # disable mesh feature
        del self.osc_attributes['mesh_size']
        del self.osc_attributes['mesh_debug']

        # init empty string
        self.new_string()

    def get_osc_path(self):
        return '/%s/text/%s' % (self.parent.name, self.name)

    def new_string(self):
        """
        Update string buffer. Mostly copied from pi3d.String
        """
        size = min(1, self.font.ratio / self.length) if self.size == 'auto' else self.size
        size /= self.font.nominal_height / self.parent.height # relative to screend height
        self.computed_size = size

        string = self.string
        font = self.font

        sy = sx = size

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
            if self.h_align == 'center':
                cx = xoff / 2.0
            elif self.h_align == 'left':
                cx = 0.0
            else:
                cx = xoff

            for j in temp_verts:
                self.verts.append([(j[0] - cx) * sx,
                                 (j[1] + nlines * font.line_height * GAP / 2.0 - yoff) * sy,
                                 j[2]])

        default = font.glyph_table.get(chr(0), None)
        for i, c in enumerate(string):
            if c == '\n':
                make_verts()
                yoff += font.line_height * GAP
                xoff = 0.0
                temp_verts = []
                lines += 1
                continue #don't attempt to draw this character!

            glyph = font.glyph_table.get(c, default)
            if not glyph:
                continue
            w, h, texc, verts = glyph[0:4]

            if self.glitch and not self.font.mono:
                # use the destination letter's width when glitching
                w = font.glyph_table.get(self.glitch_to[i], default)[0]

            for j in verts:
                glitch_offset = 0
                if self.glitch and not self.font.mono:
                    # center glitching letters
                    glitch_offset += (glyph[0] - w) / 2.0
                temp_verts.append((j[0] + xoff - glitch_offset, j[1], j[2] - i/1000.)) # "-i/1000." => allow letter overlap

            xoff += w * self.letter_spacing
            for j in texc:
                self.texcoords.append(j)
            self.norms.extend(_NORMALS)

            # Take Into account unprinted \n characters
            stv = 4 * (i - lines)
            self.inds.extend([[stv, stv + 2, stv + 1], [stv, stv + 3, stv + 2]])

        make_verts()

        tex = self.buf[0].textures
        self.buf = [pi3d.Buffer(self, self.verts, self.texcoords, self.inds, self.norms)]
        self.buf[0].textures = tex

        self.height = self.font.line_height * (1+self.string.count('\n')) * size
        self.last_draw_align_h = self.h_align


        self.set_v_align(self.v_align)
        self.set_h_align(self.h_align)
        self.set_shader(self.shader)
        self.set_scale(self.sx, self.sy)
        self.set_material(self.color)
        self.set_tiles(*self.tiles)
        self.set_text_outline(self.outline)
        self.set_text_outline_color(*self.outline_color)

    def draw(self, *args, **kwargs):

        if self.visible:

            if self.glitch:
                self.glitch_next()

            if self.string == '':
                return

            if self.need_regen:
                self.new_string()
                self.need_regen = False

            # font smoothing
            self.buf[0].unib[8] = self.computed_size * self.sy

            super(Text, self).draw(*args, **kwargs)

    def scale(self, sx, sy, sz):
        """
        Override Slide.scale to trigger string regeneration when needed
        """
        super(Text, self).scale(sx, sy, sz)
        if self.v_align != 'center':
            self.need_regen = True

    def position(self, x, y, z):
        """
        Override Slide.position to trigger string regeneration if h_align has changed
        """
        super(Text, self).position(x, y, z)
        if self.h_align != self.last_draw_align_h:
            self.need_regen = True

    def set_text(self, string, duration=0, stop_glitch=True):
        """
        Set the text's string
        """

        if duration != 0:
            return self.set_glitch(string, duration)
        if stop_glitch:
            self.glitch = False

        self.string = str(string)

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
        self.glitch_to = string
        self.glitch_start = self.parent.time
        if isinstance(duration, (float, int)):
            self.glitch_duration = max(duration, 0.01)
        self.glitch_next()

    def glitch_next(self):
        """
        Compute current glitched text
        """
        progress = min(1, (self.parent.time - self.glitch_start) / self.glitch_duration)

        if progress == 1.0:
            self.glitch_indices = []
            self.glitch = False
        elif progress == 0.0:
            self.glitch_indices = list(range(0, len(self.glitch_to)))
            del self.glitch_indices[random.randint(0, len(self.glitch_indices) -1)]
        else:
            nglitch = int((1-progress) * (len(self.glitch_to) - 1)) + 1
            while len(self.glitch_indices) > nglitch:
                del self.glitch_indices[random.randint(0, len(self.glitch_indices) -1)]

        glitched_text = ''
        for i in range(len(self.glitch_to)):
            if i in self.glitch_indices:
                glitched_text += random.choice(list(self.font.glyph_table.keys()))
            else:
                glitched_text += self.glitch_to[i]

        self.set_text(glitched_text, 0, False)


    @osc_property('text', 'string')
    def set_text_osc(self, text, glitch_duration=0):
        """
        text string with optional glitch duration
        """
        self.set_text(str(text), float(glitch_duration))

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

    @osc_property('outline', 'outline')
    def set_text_outline(self, outline):
        """
        text outline width (0<>1)
        """
        self.outline = min(max(0, outline), 1)
        self.buf[0].unib[11] = self.outline

    @osc_property('outline_color', 'outline_color')
    def set_text_outline_color(self, r, g, b):
        """
        text outline color (0<>1)
        """
        self.outline_color = [float(r), float(g), float(b)]
        self.buf[0].unib[12:15] = self.outline_color

    @osc_property('spacing', 'letter_spacing')
    def set_text_spacing(self, spacing):
        """
        letter spacing
        """
        if spacing != self.letter_spacing:
            self.need_regen = True
        self.letter_spacing = float(spacing)

# encoding: utf-8

import pi3d
import random

from ..slides.state import State
from ..slides.slide import SlideBase
from ..slides.perspective import Perspective
from ..engine.osc import osc_property
from ..fonts.font import MsdfFont
from ..utils import relative_path


import logging
LOGGER = logging.getLogger(__name__)

GLITCH_CHARS = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+:;,?!$____***')

FONTS = {
    "sans": MsdfFont(relative_path('fonts/leaguegothic.png')),
    "mono": MsdfFont(relative_path('fonts/freemono.png'))
}

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
        self.last_draw_align_v = 'center'

        # cool
        self.glitch_duration = 1
        self.glitch_start = 0
        self.glitch = False
        self.glitch_to = None
        self.glitch_indices = []

        self.letter_spacing = 1.
        self.line_height = 1.

        self.outline = 0.0
        self.outline_color = [1.0, 0.0, 0.0]

        super(Text, self).__init__(parent, name, texture=self.font, width=parent.width, height=parent.height, init_z=init_z)

        self.color = [1.0, 1.0, 1.0]
        self.active_effects.append('TEXT')

        # fix alignment (handled in new_string())
        self.width = 0
        self.video = False

        # disable mesh feature
        del self.osc_attributes['mesh_size']
        del self.osc_attributes['mesh_debug']

        # init empty string
        self.new_string()

    def get_osc_path(self):
        return '/%s/text/%s' % (self.parent.name, self.name)

    def new_string(self):
        """
        Update string buffer. Derivated from pi3d.String
        """
        size = min(1, self.font.ratio / self.length) if self.size == 'auto' else self.size
        size /= self.font.nominal_height / self.parent.height # relative to screend height
        self.computed_size = size

        string = self.string
        font = self.font

        vertices = []
        texcoords = []
        indices = []
        tmp_vertices = []

        nlines = 0

        pos_x = 0
        pos_y = 0

        gap = self.font.line_height * self.line_height

        nlines_total = len(self.string.split('\n')) + 1
        total_height = self.font.line_height + (nlines_total - 1) * self.font.line_height * self.line_height

        def make_line():
            nonlocal nlines, pos_x, pos_y, tmp_vertices

            nlines += 1

            if self.h_align == 'center':
                cx = pos_x / 2.0
            elif self.h_align == 'left':
                cx = 0.0
            else:
                cx = pos_x

            if self.v_align == 'top':
                cy = gap / 2.
            elif self.v_align == 'bottom':
                cy = -gap / 2.
            else:
                cy = 0

            for vert in tmp_vertices:
                vertices.append([
                    (vert[0] - cx) * size,
                    (vert[1] + total_height / 2. - gap / 2.  - pos_y + cy) * size,
                    vert[2]
                ])

            tmp_vertices = []
            pos_x = 0
            pos_y += gap


        for i, char in enumerate(string):

            if char == '\n' or (self.glitch and self.glitch_to[i] == '\n'):
                make_line()
                continue

            glyph = font.get_glyph(char)

            w, h, texc, verts = glyph[0:4]

            if self.glitch and not self.font.mono:
                # use the destination letter's width when glitching
                w = font.get_glyph(char)[0]

            for j in verts:
                glitch_offset = 0
                if self.glitch and not self.font.mono:
                    # center glitching letters
                    glitch_offset += (glyph[0] - w) / 2.0
                tmp_vertices.append((j[0] + pos_x - glitch_offset, j[1], j[2] - i/1000.)) # "-i/1000." => allow letter overlap

            pos_x += w * self.letter_spacing

            for c in texc:
                texcoords.append(c)

            # Take Into account unprinted \n characters
            stv = 4 * (i - nlines)
            indices.extend([[stv, stv + 2, stv + 1], [stv, stv + 3, stv + 2]])

        make_line()

        tex = self.buf[0].textures
        self.buf = [pi3d.Buffer(self, vertices, texcoords, indices, None)]
        self.buf[0].textures = tex

        self.height = total_height * size
        self.last_draw_align_h = self.h_align
        self.last_draw_align_v = self.h_align


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
        if self.h_align != self.last_draw_align_h or self.v_align != self.last_draw_align_v:
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
        else:
            nglitch = int((1-progress) * len(self.glitch_to)) + 1
            while len(self.glitch_indices) > nglitch:
                del self.glitch_indices[random.randint(0, len(self.glitch_indices) -1)]

        glitched_text = ''
        for i in range(len(self.glitch_to)):
            if i in self.glitch_indices:
                glitched_text += random.choice(GLITCH_CHARS)
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

    @osc_property('line_height', 'line_height')
    def set_text_line_height(self, line_height):
        """
        line height
        """
        if line_height != self.line_height:
            self.need_regen = True
        self.line_height = float(line_height)

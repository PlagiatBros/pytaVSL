# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import pi3d
import random

from strobe import Strobe
from animation import Animation

from font import Font

LOGGER = pi3d.Log(__name__)

RESOLUTION = 0.5
CODEPOINTS = range(32, 126) + range(160,255) + ['ʒ', '~']
FONTS = {
    "sans": Font('sans.ttf', color=(127,127,127,255), background_color=(0,0,0,0), font_size=int(170*RESOLUTION), offset_y=0.015, codepoints=CODEPOINTS),
    "mono": Font('mono.ttf', color=(127,127,127,255), background_color=(0,0,0,0), font_size=int(200*RESOLUTION), offset_y=-0.005, codepoints=CODEPOINTS)
}
V_ALIGN = ['C', 'B', 'T']
H_ALIGN = ['C', 'L', 'R']

class Text(Strobe, Animation):
    """
    Dynamic text
    """
    def __init__(self, parent, font="mono"):
        """
        Text constructur

        Args:
            font (str): "sans" or "mono" (see FONTS global)
        """

        super(Text, self).__init__()

        self.parent = parent

        self.font = FONTS[font]

        self.shader = pi3d.Shader("uv_flat")

        self.visible = True

        self.string = ' '
        self.color = (1.0, 1.0, 1.0)
        self.color_strobe = False
        self.alpha = 1.0

        self.size = 'auto'

        self.h_align = 'C'
        self.v_align = 'C'

        self.x = 0
        self.y = 0

        self.sx = 1
        self.sy = 1
        self.sz = 1

        self.rx = 0
        self.ry = 0
        self.rz = 0

        self.quick_change = False
        self.need_regen = False
        self.new_string()

    def new_string(self):
        """
        Generate a new string instance and apply all options.
        """

        x = self.x
        y = self.y

        size = min(1, self.font.ratio / len(self.string) if self.size == 'auto' else self.size)

        if self.h_align == 'L':
            x -= self.parent.DISPLAY.width / 2.
        elif self.h_align == 'R':
            x += self.parent.DISPLAY.width / 2.

        if self.v_align == 'T':
            y = y + self.parent.DISPLAY.height / 2. - self.font.size * size * 2 / RESOLUTION
        elif self.v_align == 'B':
            y = y - self.parent.DISPLAY.height / 2. + self.font.size * size * 2 / RESOLUTION

        self.text = pi3d.String(font=self.font, string=self.string, size=size / RESOLUTION,
                      camera=self.parent.CAMERA, x=x, y=y, z=0, is_3d=False,
                      justify=self.h_align, rx=self.rx, ry=self.ry, rz=self.rz)

        self.text.set_shader(self.shader)

        self.text.scale(self.sx, self.sy, self.sz)


    def draw(self):

        self.animate_next_frame()

        if self.string == '':
            return

        if self.need_regen:
            self.need_regen = False
            self.new_string()

        if self.strobe:
            self.strobe_state.next()

        if self.visible and self.string and (not self.strobe or self.strobe_state.visible):

            if self.quick_change:
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

        # self.quick_change = len(self.string) == len(string)
        self.string = string

        if not self.quick_change:
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
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y

        self.need_regen = True

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
        self.size = 'auto' if type(size) is str else min(max(float(size),0.),1.)
        self.need_regen = True

    def set_scale(self, sx, sy, sz):
        """
        set_scale sets the scale of the text
        """
        self.sx = sx
        self.sy = sy
        self.sz = sz
        self.text.scale(sx, sy, sz)

    def set_zoom(self, zoom):
        """
        Scaling relative to initial size, aka zoom
        """
        self.set_scale(zoom, zoom, self.sz)

    def set_visible(self, visible):
        """
        Set visibility.

        Args:
            visible (bool): True to show, False to hide
        """
        self.visible = bool(visible)

    def reset(self):
        self.set_size('auto')
        self.set_scale(1, 1, 1)
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

    def get_animate_value(self, name):
        """
        Getters for animations
        """
        val = 0
        if name == 'size':
            val = self.size
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
            val = self.alpha

        return val

    def get_animate_setter(self, name):
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
                self.set_scale(val, self.sy, self.sz)
        elif name == 'scale_y':
            def set_val(val):
                self.set_scale(self.sx, val, self.sz)
        elif name == 'scale_z':
            def set_val(val):
                self.set_scale(self.sx, self.sy, val)
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

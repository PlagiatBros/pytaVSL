# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import time
import pi3d
import random

from utils import KillableThread as Thread

from font import Font

LOGGER = pi3d.Log(__name__)

RESOLUTION = 0.5
CODEPOINTS = range(32, 126) + range(160,255) + ['ʒ']
FONTS = {
    "sans": Font('sans.ttf', color=(127,127,127,255), background_color=(0,0,0,0), font_size=int(170*RESOLUTION), offset_y=0.015, codepoints=CODEPOINTS),
    "mono": Font('mono.ttf', color=(127,127,127,255), background_color=(0,0,0,0), font_size=int(200*RESOLUTION), offset_y=-0.005, codepoints=CODEPOINTS)
}
V_ALIGN = ['C', 'B', 'T']
H_ALIGN = ['C', 'L', 'R']

class Strobe():
    def __init__(self):
        self.period = 2.0
        self.ratio = 0.5
        self.cursor = 0
        self.visble = False
        self.regen()

    def regen(self):
        self.breakpoint = self.period * self.ratio

    def set_period(self, l):
        self.period = max(int(l), 0.0)
        self.regen()

    def set_ratio(self, r):
        self.ratio = max(float(r), 0.0)
        self.regen()

    def next(self):
        self.cursor += 1
        if self.cursor < self.breakpoint:
            self.visible = False
        elif self.cursor < self.period:
            self.visible = True
        else:
            self.cursor = 0
            self.visible = False

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
        self.strobe_state = Strobe()

        self.string = ' '
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

        self.quick_change = False
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
            y = y + self.parent.DISPLAY.height / 2. - self.font.size * self.size * 2 / RESOLUTION
        elif self.v_align == 'B':
            y = y - self.parent.DISPLAY.height / 2. + self.font.size * self.size * 2 / RESOLUTION

        self.text = pi3d.String(font=self.font, string=self.string, size=self.size/RESOLUTION,
                      camera=self.parent.CAMERA, x=x, y=y, z=0, is_3d=False,
                      justify=self.h_align, rx=self.rx, ry=self.ry, rz=self.rz)

        self.text.set_shader(self.shader)

    def draw(self):

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
            size (float): between 0.0 and 1.0. 1.0 for full height characters
        """
        self.size = min(max(float(size),0.),1.)
        self.need_regen = True

    def set_visible(self, visible):
        """
        Set visibility.

        Args:
            visible (bool): True to show, False to hide
        """
        self.visible = bool(visible)

    def set_strobe(self, strobe=None, period=None, ratio=None):
        """
        Set strobe mode

        Args:
            strobe  (bool): True to enable strobe mode
            period (float): (optional) period of the strobe cycle in frames
            ratio  (float): (optional) ratio between hidden and show frames
        """
        if not self.strobe and strobe:
            self.strobe_state.cursor = 0

        if period is not None:
            self.strobe_state.set_period(period)

        if ratio is not None:
            self.strobe_state.set_ratio(ratio)

        if strobe is not None:
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

        self.stop_animate(name)

        self.animations[name] = Thread(target=threaded)
        self.animations[name].start()

    def stop_animate(self, name=None):
        """
        Stop animations
        """
        if name is not None and name in self.animations:
            try:
                self.animations[name].kill()
            except:
                pass
            del self.animations[name]
        elif name is None:
            for name in self.animations:
                try:
                    self.animations[name].kill()
                except:
                    pass
                self.animations = {}


    def get_animate_function(self, name):
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
        elif name == 'size':
            def set_val(val):
                self.set_size(val)
        elif name == 'position_x':
            def set_val(val):
                self.set_position(val, None)
        elif name == 'position_y':
            def set_val(val):
                self.set_position(None, val)
        else:
            def set_val(val):
                pass
        return set_val

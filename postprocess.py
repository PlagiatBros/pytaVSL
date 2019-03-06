# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import time
import pi3d
import liblo

import random
from slide import Slide
from pi3d.util.OffScreenTexture import OffScreenTexture

LOGGER = pi3d.Log(__name__)

class PostProcess(Slide):

        def __init__(self):

            super(PostProcess, self).__init__("postprocessing", None, 1)

            self.texture = OffScreenTexture("postprocess")
            self.shader = pi3d.Shader("shaders/glitcher")
            self.set_draw_details(self.shader, [self.texture])

            self.init_w = 800
            self.init_h = 600
            self.set_scale(800, 600, 1.0)
            self.set_visible(True)

            self.set_glitch_strength(0.0)
            self.set_glitch_noise(0.0)

            self.set_color_shift(0.0)
            self.set_color_invert(0.0)
            self.set_color_alpha(1.0)

        def capture_start(self):
            self.texture._start()

        def capture_end(self):
            self.texture._end()

        def set_glitch_strength(self, x):
            self.set_custom_data(56, [x])

        def set_glitch_noise(self, x):
            self.set_custom_data(55, [x])

        def set_color_shift(self, x):
            self.set_custom_data(51, [x])

        def set_color_invert(self, x):
            self.set_custom_data(52, [x])

        def set_color_alpha(self, x):
            self.set_custom_data(53, [x])

        def draw(self, *args, **kwargs):
            self.set_custom_data(45, [random.random()])
            super(PostProcess, self).draw(*args, **kwargs)

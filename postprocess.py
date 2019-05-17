# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import time
import pi3d
import liblo

import random
from slide import Slide
from pi3d.util.OffScreenTexture import OffScreenTexture

import logging
LOGGER = logging.getLogger(__name__)

class PostProcess(Slide):

        def __init__(self):

            super(PostProcess, self).__init__("postprocessing", None, 1)

            self.texture = OffScreenTexture("postprocess")
            self.shader = pi3d.Shader("shaders/glitcher")
            self.set_draw_details(self.shader, [self.texture])

            self.init_w = 800
            self.init_h = 600
            self.set_scale(800, 600, 1.0)

            self.rand = 0.0

            self.strength = 0.0
            self.noise = 0.0
            self.hue = 0.0
            self.saturation = 0.0
            self.value = 0.0
            self.alpha = 0.0
            self.noise = 0.0

            self.reset()

        def capture_start(self):
            self.texture._start()

        def capture_end(self):
            self.texture._end()

        def reset(self):
            super(PostProcess, self).reset()
            self.set_visible(False)
            self.set_glitch_strength(0.0)
            self.set_glitch_noise(0.0)
            self.set_color_hue(0.0)
            self.set_color_saturation(1.0)
            self.set_color_value(1.0)
            self.set_color_invert(0.0)
            self.set_color_alpha(1.0)
            self.set_tiles(1.0, 1.0)

        def set_color(self, *args):
            pass

        def set_glitch_strength(self, x):
            self.strength = x
            self.set_custom_data(56, [x])

        def set_glitch_noise(self, x):
            self.noise = x
            self.set_custom_data(55, [x])

        def set_color_hue(self, x):
            self.hue = x
            self.set_custom_data(48, [x])

        def set_color_saturation(self, x):
            self.saturation = x
            self.set_custom_data(49, [x])

        def set_color_value(self, x):
            self.value = x
            self.set_custom_data(50, [x])

        def set_color_alpha(self, x):
            self.alpha = x
            self.set_custom_data(51, [x])

        def set_color_invert(self, x):
            self.invert = x
            self.set_custom_data(52, [x])

        def draw(self, *args, **kwargs):
            rand = random.random()
            mean = (self.rand*49+rand)/50.0
            self.set_custom_data(45, [mean])
            self.rand = rand
            super(PostProcess, self).draw(*args, **kwargs)


        def get_param_getter(self, name):
            """
            Getters for osc & animations
            """
            _val = super(PostProcess, self).get_param_getter(name)

            val = 0
            if name == 'glitch_strength':
                val = self.strength
            elif name == 'glitch_noise':
                val = self.noise
            elif name == 'color_hue':
                val = self.hue
            elif name == 'color_saturation':
                val = self.saturation
            elif name == 'color_value':
                val = self.value
            elif name == 'alpha':
                val = self.alpha
            elif name == 'color_alpha':
                val = self.alpha
            elif name == 'color_invert':
                val = self.invert

            return val if val is not 0 else _val

        def get_param_setter(self, name):
            """
            Setters for osc & animations
            """

            _set_val = super(PostProcess, self).get_param_setter(name)

            if name == 'glitch_strength':
                def set_val(val):
                    self.set_glitch_strength(val)
            elif name == 'glitch_noise':
                def set_val(val):
                    self.set_glitch_noise(val)
            elif name == 'color_hue':
                def set_val(val):
                    self.set_color_hue(val)
            elif name == 'color_saturation':
                def set_val(val):
                    self.set_color_saturation(val)
            elif name == 'color_value':
                def set_val(val):
                    self.set_color_value(val)
            elif name == 'alpha':
                def set_val(val):
                    self.set_color_alpha(val)
            elif name == 'color_alpha':
                def set_val(val):
                    self.set_color_alpha(val)
            elif name == 'color_invert':
                def set_val(val):
                    self.set_color_invert(val)
            else:
                set_val = None

            return set_val if set_val is not None else _set_val

# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import pi3d
import random

from shaders import SHADERS

import logging
LOGGER = logging.getLogger(__name__)

class Effect():

    def __init__(self, *args, **kwargs):

        super(Effect, self).__init__(*args, **kwargs)

        self.effect = False
        self.set_base_effect()

        """
            uniforms:
            47 random float
            48:50 key color (r, g, b)
            51 key threshold
            52 invert
            53 rgbwave
            54:56 charcoal (radius, thresh, strengh)
            57:59 noise (density, seed1, seed2)
        """


        self.effect_key_color = (0, 0, 0)
        self.effect_key_threshold = -1.0
        self.effect_invert = 0.0
        self.effect_rgbwave = 0.0
        self.effect_charcoal = (2.0, 0.0, 2.0)
        self.effect_noise = (0.5, 0.0, 0.0)

        self.set_custom_data(48, [
            self.effect_key_color[0], self.effect_key_color[1], self.effect_key_color[2],
            self.effect_key_threshold, self.effect_invert, self.effect_rgbwave,
            self.effect_charcoal[0], self.effect_charcoal[1], self.effect_charcoal[2],
            self.effect_noise[0], self.effect_noise[1], self.effect_noise[2],
        ])

    def set_base_effect(self, effect='default'):
        self.base_shader = SHADERS[effect]
        self.set_shader(self.base_shader)
        self.effect = False

    def set_effect(self, effect=None):
        if effect is None:
            return self.set_base_effect()
        try:
            self.set_shader(SHADERS[effect])
            self.effect = True
        except:
            self.set_base_effect()
            LOGGER.error('could not load shader %s' % effect)

    def draw(self, *args, **kwargs):
        if self.effect:
            self.unif[47] = random.random()
        super(Effect, self).draw(*args, **kwargs)

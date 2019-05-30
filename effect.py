# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import pi3d
import random

from shaders import SHADERS
from osc import osc_property

import logging
LOGGER = logging.getLogger(__name__)

class Effect(object):

    def __init__(self, *args, **kwargs):

        super(Effect, self).__init__(*args, **kwargs)

        self.effect_active = False
        self.current_effect = 'default'
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


        self.effect_key_color = [0.0, 0.0, 0.0]
        self.effect_key_threshold = -0.001
        self.effect_invert = 0.0
        self.effect_rgbwave = 0.0
        self.effect_charcoal = [2.0, 0.0, 2.0]
        self.effect_noise = [0.5, 0.0, 0.0]

        self.set_custom_data(48, [
            self.effect_key_color[0], self.effect_key_color[1], self.effect_key_color[2],
            self.effect_key_threshold, self.effect_invert, self.effect_rgbwave,
            self.effect_charcoal[0], self.effect_charcoal[1], self.effect_charcoal[2],
            self.effect_noise[0], self.effect_noise[1], self.effect_noise[2],
        ])

    def set_base_effect(self, effect='default'):
        self.current_effect = effect
        self.base_shader = SHADERS[effect]
        self.set_shader(self.base_shader)
        self.effect_active = False

    @osc_property('effect', 'current_effect')
    def set_effect(self, effect='default'):
        try:
            self.set_shader(SHADERS[effect])
            self.current_effect = effect
            self.effect_active = True
        except:
            self.set_base_effect()
            LOGGER.error('could not load shader %s' % effect)

    @osc_property('key_color', 'effect_key_color')
    def set_effect_key_color(self, r, g, b):
        self.effect_key_color = [r, g, b]
        self.unif[48] = self.effect_key_color[0]
        self.unif[49] = self.effect_key_color[1]
        self.unif[50] = self.effect_key_color[2]

    @osc_property('key_threshold', 'effect_key_threshold')
    def set_effect_key_threshold(self, value):
        self.effect_key_threshold = float(value) - 0.001
        self.unif[51] = self.effect_key_threshold

    @osc_property('invert', 'effect_invert')
    def set_effect_invert(self, value):
        self.effect_invert = float(bool(value))
        self.unif[52] = self.effect_invert

    @osc_property('rgbwave', 'effect_rgbwave')
    def set_effect_rgbwave(self, value):
        self.effect_rgbwave = float(value)
        self.unif[53] = self.effect_rgbwave

    @osc_property('charcoal', 'effect_charcoal')
    def set_effect_charcoal(self, radius, threshold, strength):
        self.effect_charcoal = [float(value) for value in [radius, threshold, strength]]
        self.unif[54] = self.effect_charcoal[0]
        self.unif[55] = self.effect_charcoal[1]
        self.unif[56] = self.effect_charcoal[2]

    @osc_property('noise', 'effect_noise')
    def set_effect_noise(self, density, seed1, seed2):
        self.effect_noise = [float(value) for value in [density, seed1, seed2]]
        self.unif[57] = self.effect_noise[0]
        self.unif[58] = self.effect_noise[1]
        self.unif[59] = self.effect_noise[2]

    def draw(self, *args, **kwargs):

        if self.effect_active:
            self.unif[47] = random.random()

        super(Effect, self).draw(*args, **kwargs)

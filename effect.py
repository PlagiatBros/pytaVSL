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
        """ shader uniform variables overrides

        ===== ========================================== ==== ==
        vec3  description                                python
        ----- ------------------------------------------ -------
        index                                            from to
        ===== ========================================== ==== ==
          12  random, unused, unused                      36  38
          13  key_color r, g, b                           39  41
          14  key_threshold, mask, mask_strength          42  43
          15  invert, unused, unused                      45  46
          16  rgbwave, unused, unused                     48  50
          17  charcoal radius, thresh, strength           51  53
          18  noise, seed1, seed2                         54  56
          19  unused, unused, unused                      57  59
        ===== ========================================== ==== ==
        """

        super(Effect, self).__init__(*args, **kwargs)

        self.effect_active = False
        self.current_effect = 'default'
        self.set_effect()

        self.effect_key_color = [0.0, 0.0, 0.0]
        self.effect_key_threshold = -0.001
        self.effect_invert = 0.0
        self.effect_rgbwave = 0.0
        self.effect_charcoal = [2.0, 0.0, 2.0]
        self.effect_noise = [0.5, 0.0, 0.0]

        self.set_effect_key_color(*self.effect_key_color)
        self.set_effect_key_threshold(self.effect_key_threshold)
        self.set_effect_invert(self.effect_invert)
        self.set_effect_rgbwave(self.effect_rgbwave)
        self.set_effect_charcoal(*self.effect_charcoal)
        self.set_effect_noise(*self.effect_noise)

        # only used in PostProcess
        self.buf[0].unib[13] = 0.0
        # only used in Video
        self.buf[0].unib[12] = 0.0

    @osc_property('effect', 'current_effect')
    def set_effect(self, effect='default'):
        """
        special effect (default|rgbwave|charcoal|noise)
        """
        try:
            self.set_shader(SHADERS[effect])
            self.current_effect = effect
            self.effect_active = True
        except:
            self.set_effect()
            self.effect_active = False
            LOGGER.error('could not load shader %s' % effect)

    @osc_property('key_color', 'effect_key_color')
    def set_effect_key_color(self, r, g, b):
        """
        key rgb color (0-1)
        """
        self.effect_key_color = [r, g, b]
        self.unif[39] = self.effect_key_color[0]
        self.unif[40] = self.effect_key_color[1]
        self.unif[41] = self.effect_key_color[2]

    @osc_property('key_threshold', 'effect_key_threshold')
    def set_effect_key_threshold(self, value):
        """
        discard pixels when color distance to key_color is below this threshold (0-1)
        """
        self.effect_key_threshold = float(value) - 0.001
        self.unif[42] = self.effect_key_threshold

    @osc_property('invert', 'effect_invert')
    def set_effect_invert(self, value):
        """
        invert colors (0|1)
        """
        self.effect_invert = float(bool(value))
        self.unif[45] = self.effect_invert

    @osc_property('rgbwave', 'effect_rgbwave')
    def set_effect_rgbwave(self, value):
        """
        rgbwave strength
        """
        self.effect_rgbwave = float(value)
        self.unif[48] = self.effect_rgbwave

    @osc_property('charcoal', 'effect_charcoal')
    def set_effect_charcoal(self, size, threshold, strength):
        """
        charcoal pen size (px), edge threshold and stroke strength
        """
        self.effect_charcoal = [float(value) for value in [size, threshold, strength]]
        self.unif[51] = self.effect_charcoal[0]
        self.unif[52] = self.effect_charcoal[1]
        self.unif[53] = self.effect_charcoal[2]

    @osc_property('noise', 'effect_noise')
    def set_effect_noise(self, density, x, y):
        """
        noise density (0-1) and xy chaos stretching
        """
        self.effect_noise = [float(value) for value in [density, x, y]]
        self.unif[54] = self.effect_noise[0]
        self.unif[55] = self.effect_noise[1]
        self.unif[56] = self.effect_noise[2]

    def draw(self, *args, **kwargs):

        if self.effect_active:
            self.unif[36] = random.random()

        super(Effect, self).draw(*args, **kwargs)

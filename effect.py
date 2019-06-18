# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import pi3d
from pi3d.constants import (opengles, GL_TEXTURE_2D)
import random

from shaders import get_shader
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
          14  key_threshold, unused, unused               42  43
          15  invert, unused, unused                      45  46
          16  rgbwave, fish, unused                       48  50
          17  charcoal radius, thresh, strength           51  53
          18  noise, seed1, seed2                         54  56
          19  mask, mask_hardness, unused                 57  59
        ===== ========================================== ==== ==
        """

        super(Effect, self).__init__(*args, **kwargs)

        self.active_effects = []
        self.active_effects_changed = True

        self.effect_key_color = [0.0, 0.0, 0.0]
        self.effect_key_threshold = 0
        self.set_effect_key_color(*self.effect_key_color)
        self.set_effect_key_threshold(self.effect_key_threshold)

        self.effect_invert = 0.0
        self.set_effect_invert(self.effect_invert)

        self.effect_rgbwave = 0.0
        self.set_effect_rgbwave(self.effect_rgbwave)

        self.effect_charcoal = 0.0
        self.effect_charcoal_settings = [2.0, 0.0, 2.0]
        self.set_effect_charcoal_settings(*self.effect_charcoal_settings)

        self.effect_noise = [0.0, 0.0, 0.0]
        self.set_effect_noise(*self.effect_noise)

        self.effect_mask = ''
        self.effect_mask_hardness = 0.0
        self.effect_mask_threshold = 1.0
        self.set_effect_mask(self.effect_mask)
        self.set_effect_mask_hardness(self.effect_mask_hardness)
        self.set_effect_mask_threshold(self.effect_mask_threshold)

        self.effect_fish = 0.0
        self.set_effect_fish(self.effect_fish)

    def toggle_effect(self, name, state):
        if state and name not in self.active_effects:
            self.active_effects.append(name)
            self.active_effects_changed = True
        elif not state and name in self.active_effects:
            self.active_effects.remove(name)
            self.active_effects_changed = True

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
        self.effect_key_threshold = float(value)
        self.unif[42] = self.effect_key_threshold

        self.toggle_effect('KEY', self.effect_key_threshold != 0)

    @osc_property('invert', 'effect_invert')
    def set_effect_invert(self, value):
        """
        invert colors (0|1)
        """
        self.effect_invert = int(bool(value))
        self.toggle_effect('INVERT', self.effect_invert != 0)

    @osc_property('rgbwave', 'effect_rgbwave')
    def set_effect_rgbwave(self, value):
        """
        rgbwave strength
        """
        self.effect_rgbwave = float(value)
        self.unif[48] = self.effect_rgbwave
        self.toggle_effect('RGBWAVE', self.effect_rgbwave != 0)

    @osc_property('charcoal', 'effect_charcoal')
    def set_effect_charcoal(self, value):
        """
        enable charcoal effect (0|1)
        """
        self.effect_charcoal = int(bool(value))
        self.toggle_effect('CHARCOAL', self.effect_charcoal != 0)

    @osc_property('charcoal_settings', 'effect_charcoal_settings')
    def set_effect_charcoal_settings(self, size, threshold, strength):
        """
        charcoal pen size (px), edge threshold and stroke strength
        """
        self.effect_charcoal_settings = [float(value) for value in [size, threshold, strength]]
        self.unif[51] = self.effect_charcoal_settings[0]
        self.unif[52] = self.effect_charcoal_settings[1]
        self.unif[53] = self.effect_charcoal_settings[2]

    @osc_property('noise', 'effect_noise')
    def set_effect_noise(self, density, x, y):
        """
        noise density (0-1) and xy chaos stretching
        """
        self.effect_noise = [float(value) for value in [density, x, y]]
        self.unif[54] = self.effect_noise[0]
        self.unif[55] = self.effect_noise[1]
        self.unif[56] = self.effect_noise[2]
        self.toggle_effect('NOISE', self.effect_noise[0] != 0)


    @osc_property('mask', 'effect_mask')
    def set_effect_mask(self, slide=''):
        """
        slide name to use as a mask (empty or ommitted to reset)
        """
        if slide == '':
            if len(self.buf[0].textures) == 2:
                self.effect_mask = ''
                del self.buf[0].textures[1]
                self.toggle_effect('MASK', False)
            return

        target = self.parent.get_children(self.parent.slides, slide)
        if target:
            target = target[0]
            self.effect_mask = target.name
            tex = target.buf[0].textures[0]
            if len(self.buf[0].textures) == 1:
                self.buf[0].textures.append(tex)
            else:
                self.buf[0].textures[1] = tex

            self.toggle_effect('MASK', True)
        else:
            LOGGER.error('mask "%s" not found' % (slide))

    @osc_property('mask_hardness', 'effect_mask_hardness')
    def set_effect_mask_hardness(self, strength):
        """
        mask hardness (0-1)
        """
        self.effect_mask_hardness = float(strength)
        self.unif[58] = self.effect_mask_hardness

    @osc_property('mask_threshold', 'effect_mask_threshold')
    def set_effect_mask_threshold(self, thresh):
        """
        mask threshold (0-1)
        """
        self.effect_mask_threshold = float(thresh)
        self.unif[59] = self.effect_mask_threshold

    @osc_property('fish', 'effect_fish')
    def set_effect_fish(self, value):
        """
        fish (-1-1)
        """
        self.effect_fish = float(value)
        self.unif[49] = self.effect_fish
        self.toggle_effect('FISH', self.effect_fish != 0)

    def draw(self, *args, **kwargs):

        self.unif[36] = random.random()
        if self.active_effects_changed:
            self.set_shader(get_shader(self.active_effects))
            self.active_effects_changed = False

        super(Effect, self).draw(*args, **kwargs)

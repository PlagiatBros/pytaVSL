# encoding: utf-8

import random

from shaders import get_shader
from osc import osc_property

import logging
LOGGER = logging.getLogger(__name__)

import time
origin = time.time()

class Effect(object):

    def __init__(self, *args, **kwargs):
        """ shader uniform variables overrides

        ===== ========================================== ==== ==
        vec3  description                                python
        ----- ------------------------------------------ -------
        index                                            from to
        ===== ========================================== ==== ==
          12  random, time, unused                        36  38
          13  key_color r, g, b                           39  41
          14  key_threshold, mask_hardness, mask_thresh.  42  44
          15  invert, noise, charcoal                     45  47
          16  rgbwave, fish, hue                          48  50
          17  brightness, contrast, saturation            51  53
          18  unused, unused, unused                      54  56
          19  unused, unused, unused                      57  59
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
        self.set_effect_charcoal(self.effect_charcoal)

        self.effect_noise = 0.0
        self.set_effect_noise(self.effect_noise)

        self.effect_mask = ''
        self.effect_mask_hardness = 0.0
        self.effect_mask_threshold = 1.0
        self.set_effect_mask(self.effect_mask)
        self.set_effect_mask_hardness(self.effect_mask_hardness)
        self.set_effect_mask_threshold(self.effect_mask_threshold)

        self.effect_fish = 0.0
        self.set_effect_fish(self.effect_fish)

        self.effect_hue = 0.0
        self.effect_brightness = 1.0
        self.effect_contrast = 1.0
        self.effect_saturation = 1.0
        self.set_effect_hue(self.effect_hue)
        self.set_effect_brightness(self.effect_brightness)
        self.set_effect_contrast(self.effect_contrast)
        self.set_effect_saturation(self.effect_saturation)

    def toggle_effect(self, name, state):
        if state and name not in self.active_effects:
            self.active_effects.append(name)
            self.active_effects_changed = True
        elif not state and name in self.active_effects:
            self.active_effects.remove(name)
            self.active_effects_changed = True

    def apply_effect_changes(self):
        self.set_shader(get_shader(self.active_effects))
        self.active_effects_changed = False

    @osc_property('key_color', 'effect_key_color')
    def set_effect_key_color(self, r, g, b):
        """
        key rgb color (0<>1)
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
        rgbwave effect (strength)
        """
        self.effect_rgbwave = float(value)
        self.unif[48] = self.effect_rgbwave
        self.toggle_effect('RGBWAVE', self.effect_rgbwave != 0)

    @osc_property('charcoal', 'effect_charcoal')
    def set_effect_charcoal(self, value):
        """
        charcoal effect (size)
        """
        self.effect_charcoal = float(value)
        self.unif[47] = self.effect_charcoal
        self.toggle_effect('CHARCOAL', self.effect_charcoal != 0)

    @osc_property('noise', 'effect_noise')
    def set_effect_noise(self, density):
        """
        noise (density)
        """
        self.effect_noise = float(density)
        self.unif[46] = self.effect_noise
        self.toggle_effect('NOISE', self.effect_noise != 0)


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
        mask hardness (0<>1)
        """
        self.effect_mask_hardness = float(strength)
        self.unif[43] = self.effect_mask_hardness

    @osc_property('mask_threshold', 'effect_mask_threshold')
    def set_effect_mask_threshold(self, thresh):
        """
        mask threshold (0<>1)
        """
        self.effect_mask_threshold = float(thresh)
        self.unif[44] = self.effect_mask_threshold

    @osc_property('fish', 'effect_fish')
    def set_effect_fish(self, value):
        """
        fish effect(-1<>1)
        """
        self.effect_fish = float(value)
        self.unif[49] = self.effect_fish
        self.toggle_effect('FISH', self.effect_fish != 0)


    @osc_property('hue', 'effect_hue')
    def set_effect_hue(self, value):
        """
        hue shift (0<>1)
        """
        self.effect_hue = float(value)
        self.unif[50] = self.effect_hue
        self.toggle_colors_effect()

    @osc_property('brightness', 'effect_brightness')
    def set_effect_brightness(self, value):
        """
        brightness (0<>1)
        """
        self.effect_brightness = float(value)
        self.unif[51] = self.effect_brightness
        self.toggle_colors_effect()

    @osc_property('contrast', 'effect_contrast')
    def set_effect_contrast(self, value):
        """
        contrast (0<>1)
        """
        self.effect_contrast = float(value)
        self.unif[52] = self.effect_contrast
        self.toggle_colors_effect()

    @osc_property('saturation', 'effect_saturation')
    def set_effect_saturation(self, value):
        """
        saturation (0<>1)
        """
        self.effect_saturation = float(value)
        self.unif[53] = self.effect_saturation
        self.toggle_colors_effect()


    def toggle_colors_effect(self):
        self.toggle_effect('COLORS', self.effect_hue != 0.0 or self.effect_brightness != 1.0 or self.effect_contrast != 1.0 or self.effect_saturation != 1.0)

    def draw(self, *args, **kwargs):

        self.unif[36] = random.random()
        self.unif[37] = self.parent.time - origin
        if self.active_effects_changed:
            self.apply_effect_changes()

        super(Effect, self).draw(*args, **kwargs)

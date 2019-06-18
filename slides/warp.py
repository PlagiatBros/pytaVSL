# encoding: utf-8

import pi3d
from pi3d.constants import opengles
import ctypes

from osc import osc_property

import logging
LOGGER = logging.getLogger(__name__)

WARP_ZERO = [0, 0]

class Warp(object):

    def __init__(self, *args, **kwargs):

        self.warp_1 = [0.0, 0.0]
        self.warp_2 = [0.0, 0.0]
        self.warp_3 = [0.0, 0.0]
        self.warp_4 = [0.0, 0.0]

        self.warp = False
        self.unif_warp_loc = 0;
        self.unif_warp = (ctypes.c_float * 8) (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

        super(Warp, self).__init__(*args, **kwargs)

    def set_shader(self, shader):
        super(Warp, self).set_shader(shader)
        self.unif_warp_loc = opengles.glGetUniformLocation(self.shader.program, b'warp')

    @osc_property('warp_1', 'warp_1')
    def set_warp_1(self, x, y):
        """
        top left warping
        """
        self.warp_1 = [float(x), float(y)]
        self.unif_warp[0] = self.warp_1[0]
        self.unif_warp[1] = self.warp_1[1]
        self.toggle_warp_effect()

    @osc_property('warp_2', 'warp_2')
    def set_warp_2(self, x, y):
        """
        top right warping
        """
        self.warp_2 = [float(x), float(y)]
        self.unif_warp[2] = self.warp_2[0]
        self.unif_warp[3] = self.warp_2[1]
        self.toggle_warp_effect()

    @osc_property('warp_3', 'warp_3')
    def set_warp_3(self, x, y):
        """
        top left warping
        """
        self.warp_3 = [float(x), float(y)]
        self.unif_warp[4] = self.warp_3[0]
        self.unif_warp[5] = self.warp_3[1]
        self.toggle_warp_effect()

    @osc_property('warp_4', 'warp_4')
    def set_warp_4(self, x, y):
        """
        bottom left warping
        """
        self.warp_4 = [float(x), float(y)]
        self.unif_warp[6] = self.warp_4[0]
        self.unif_warp[7] = self.warp_4[1]
        self.toggle_warp_effect()

    def toggle_warp_effect(self):
        self.warp = self.warp_1 != WARP_ZERO or self.warp_2 != WARP_ZERO or self.warp_3 != WARP_ZERO or self.warp_4 != WARP_ZERO
        self.toggle_effect('WARP', self.warp)

    def draw(self, *args, **kwargs):

        if self.visible:

            if self.shader and self.warp:
                self.shader.use()
                opengles.glUniform2fv(self.unif_warp_loc, 4, self.unif_warp)

            super(Warp, self).draw(*args, **kwargs)

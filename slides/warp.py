# encoding: utf-8

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
        self.unif_warp = (ctypes.c_float * 4) (0.0, 0.0, 0.0, 0.0)

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
        self.toggle_warp_effect()

    @osc_property('warp_2', 'warp_2')
    def set_warp_2(self, x, y):
        """
        top right warping
        """
        self.warp_2 = [float(x), float(y)]
        self.toggle_warp_effect()

    @osc_property('warp_3', 'warp_3')
    def set_warp_3(self, x, y):
        """
        top left warping
        """
        self.warp_3 = [float(x), float(y)]
        self.toggle_warp_effect()

    @osc_property('warp_4', 'warp_4')
    def set_warp_4(self, x, y):
        """
        bottom left warping
        """
        self.warp_4 = [float(x), float(y)]
        self.toggle_warp_effect()

    def toggle_warp_effect(self):
        self.warp = self.warp_1 != WARP_ZERO or self.warp_2 != WARP_ZERO or self.warp_3 != WARP_ZERO or self.warp_4 != WARP_ZERO
        self.warp_texture()
        self.warp_shape()
        self.toggle_effect('WARP', self.warp)

    def warp_texture(self):

        p0x = self.warp_1[0]
        p0y = self.warp_1[1] + 1

        p1x = self.warp_2[0] + 1
        p1y = self.warp_2[1] + 1

        p2x = self.warp_3[0] + 1
        p2y = self.warp_3[1]

        p3x = self.warp_4[0]
        p3y = self.warp_4[1]


        ax = p2x - p0x;
        ay = p2y - p0y;
        bx = p3x - p1x;
        by = p3y - p1y;

        cross = ax * by - ay * bx;

        if cross != 0:
            cy = p0y - p1y;
            cx = p0x - p1x;

            s = (ax * cy - ay * cx) / cross;

            if s > 0 and s < 1:
                t = (bx * cy - by * cx) / cross;

                if t > 0 and t < 1:
                    q0 = 1. / (1 - t);
                    q1 = 1. / (1 - s);
                    q2 = 1. / t;
                    q3 = 1. / s;

                    self.unif_warp[0] = q0
                    self.unif_warp[1] = q1
                    self.unif_warp[2] = q2
                    self.unif_warp[3] = q3

                    return
        # error
        LOGGER.error('%s: impossible texture warping' % self.name)

    def warp_shape(self):

        self.buf[0].array_buffer[0][0] = -self.width/2. + self.width  * self.warp_1[0]
        self.buf[0].array_buffer[0][1] = self.height/2. + self.height * self.warp_1[1]

        self.buf[0].array_buffer[1][0] = -self.width/2. + self.width  * self.warp_4[0]
        self.buf[0].array_buffer[1][1] = -self.height/2. + self.height * self.warp_4[1]

        self.buf[0].array_buffer[2][0] = self.width/2. + self.width  * self.warp_2[0]
        self.buf[0].array_buffer[2][1] = self.height/2. + self.height * self.warp_2[1]

        self.buf[0].array_buffer[3][0] = self.width/2. + self.width  * self.warp_3[0]
        self.buf[0].array_buffer[3][1] = -self.height/2. + self.height * self.warp_3[1]

        self.buf[0].re_init()


    def draw(self, *args, **kwargs):

        if self.visible:

            if self.shader and self.warp:
                self.shader.use()
                opengles.glUniform4fv(self.unif_warp_loc, 1, self.unif_warp)

            super(Warp, self).draw(*args, **kwargs)

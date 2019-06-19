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
        self.warp_vertices()
        self.toggle_effect('WARP', self.warp)

    def warp_texture(self):
        """
        Compute homogeneous coordinates factor at each angle and pass it to the shader
            https://bitlush.com/blog/arbitrary-quadrilaterals-in-opengl-es-2-0
            http://www.reedbeta.com/blog/quadrilateral-interpolation-part-1/
        """

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

    def warp_vertices(self):
        """
        Move vertices to warped quadrilateral
            Positions are interpolated linearly -> no projective warping if mesh_size > [1, 1]
        """

        p0x = (self.warp_1[0] - 0.5) * self.width
        p0y = (self.warp_1[1] + 1 - 0.5) * self.height

        p1x = (self.warp_2[0] + 1 - 0.5) * self.width
        p1y = (self.warp_2[1] + 1 - 0.5) * self.height

        p2x = (self.warp_3[0] + 1 - 0.5) * self.width
        p2y = (self.warp_3[1] - 0.5) * self.height

        p3x = (self.warp_4[0] - 0.5) * self.width
        p3y = (self.warp_4[1] - 0.5) * self.height

        def interpolate(v1, v2, x):
            r1 = v1[0] + (v2[0] - v1[0]) * x
            r2 = v1[1] + (v2[1] - v1[1]) * x
            return [r1, r2]

        ww = self.width / 2.0
        hh = self.height / 2.0
        nx, ny = self.mesh_size
        i = 0
        for x in range(nx + 1):
            for y in range(ny + 1):
                p = [-ww + self.width * x / nx, hh - self.height * y / ny ]
                x1 = interpolate([p0x, p0y], [p1x, p1y], 1.*x/nx)
                x2 = interpolate([p3x, p3y], [p2x, p2y], 1.*x/nx)
                p = interpolate(x1, x2, 1.*y/ny);
                self.buf[0].array_buffer[i][0] = p[0]
                self.buf[0].array_buffer[i][1] = p[1]
                i += 1

        self.buf[0].re_init()

    def create_mesh_buffer(self):
        """
        Override Mesh.create_mesh_buffer to re-warp vertices after changing mesh_size
        """
        super(Warp, self).create_mesh_buffer()
        if self.warp:
            self.warp_vertices()

    def draw(self, *args, **kwargs):

        if self.visible:

            if self.shader and self.warp:
                if self.active_effects_changed:
                    self.apply_effect_changes()
                self.shader.use()
                opengles.glUniform4fv(self.unif_warp_loc, 1, self.unif_warp)

            super(Warp, self).draw(*args, **kwargs)

# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import pi3d
from pi3d.util.OffScreenTexture import OffScreenTexture
from pi3d.Display import Display
from pi3d.constants import opengles
import ctypes

from perspective import Perspective
from slide import SlideBase
from state import State
from osc import osc_property

import logging
LOGGER = logging.getLogger(__name__)

class PostProcess(State, Perspective, SlideBase):

        def __init__(self, parent):

            texture = OffScreenTexture("post_process")

            self.warp_1 = [0.0, 0.0]
            self.warp_2 = [0.0, 0.0]
            self.warp_3 = [0.0, 0.0]
            self.warp_4 = [0.0, 0.0]
            self.unif_warp_loc = 0;
            self.unif_warp = (ctypes.c_float * 8) (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

            super(PostProcess, self).__init__(parent=parent, name="post_process", texture=texture, tiles=[64, 64])

            self.active_effects.append('POST_PROCESS')

        def scale(self, x, y, z):
            """
            Override pi3d.Shape.scale to prevent OffScreenTexture v-flip
            """
            super(PostProcess, self).scale(x, -y, z)

        def capture_start(self):
            self.buf[0].textures[0]._start()

        def capture_end(self):
            self.buf[0].textures[0]._end()


        def set_shader(self, shader):
            super(PostProcess, self).set_shader(shader)
            self.unif_warp_loc = opengles.glGetUniformLocation(self.shader.program, b'warp')


        @osc_property('warp_1', 'warp_1')
        def set_warp_1(self, x, y):
            """
            top left warping
            """
            self.warp_1 = [float(x), float(y)]
            self.unif_warp[0] = self.warp_1[0]
            self.unif_warp[1] = self.warp_1[1]

        @osc_property('warp_2', 'warp_2')
        def set_warp_2(self, x, y):
            """
            top right warping
            """
            self.warp_2 = [float(x), float(y)]
            self.unif_warp[2] = self.warp_2[0]
            self.unif_warp[3] = self.warp_2[1]

        @osc_property('warp_3', 'warp_3')
        def set_warp_3(self, x, y):
            """
            top left warping
            """
            self.warp_3 = [float(x), float(y)]
            self.unif_warp[4] = self.warp_3[0]
            self.unif_warp[5] = self.warp_3[1]

        @osc_property('warp_4', 'warp_4')
        def set_warp_4(self, x, y):
            """
            bottom left warping
            """
            self.warp_4 = [float(x), float(y)]
            self.unif_warp[6] = self.warp_4[0]
            self.unif_warp[7] = self.warp_4[1]


        def draw(self, *args, **kwargs):

            if self.visible:
                if self.shader:
                    self.shader.use()
                    opengles.glUniform2fv(self.unif_warp_loc, 4, self.unif_warp)
                super(PostProcess, self).draw(*args, **kwargs)

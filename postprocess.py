# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import pi3d
from pi3d.util.OffScreenTexture import OffScreenTexture
from pi3d.Display import Display

from perspective import Perspective
from slide import SlideBase
from state import State

import logging
LOGGER = logging.getLogger(__name__)

class PostProcess(State, Perspective, SlideBase):

        def __init__(self, parent):

            texture = OffScreenTexture("post_process")

            super(PostProcess, self).__init__(parent=parent, name="post_process", texture=texture)

            # force alpha to 1.0
            self.unif[37] = 1.0

        def scale(self, x, y, z):
            """
            Override pi3d.Shape.scale to prevent OffScreenTexture v-flip
            """
            super(PostProcess, self).scale(x, -y, z)

        def capture_start(self):
            self.buf[0].textures[0]._start()

        def capture_end(self):
            self.buf[0].textures[0]._end()

# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import pi3d
from pi3d.util.OffScreenTexture import OffScreenTexture
from pi3d.Display import Display

from slide import SlideBase
from state import State

import logging
LOGGER = logging.getLogger(__name__)

class PostProcess(State, SlideBase):

        def __init__(self, parent):

            texture = OffScreenTexture("post_process")

            super(PostProcess, self).__init__(parent=parent, name="post_process", texture=texture, width=texture.ix, height=texture.iy)

        def capture_start(self):
            self.buf[0].textures[0]._start()

        def capture_end(self):
            self.buf[0].textures[0]._end()

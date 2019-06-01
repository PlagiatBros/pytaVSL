# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import pi3d
from pi3d.util.OffScreenTexture import OffScreenTexture
from pi3d.Display import Display

from slide import SlideBase

import logging
LOGGER = logging.getLogger(__name__)

class PostProcess(SlideBase):

        def __init__(self, parent):

            texture = OffScreenTexture("postprocess")

            super(PostProcess, self).__init__(parent, "postprocessing", texture, Display.INSTANCE.width, Display.INSTANCE.height)

            self.texture = texture
            self.set_base_effect('rgbwave')

        def capture_start(self):
            self.texture._start()

        def capture_end(self):
            self.texture._end()

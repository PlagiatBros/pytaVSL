# encoding: utf-8

from pi3d.util.OffScreenTexture import OffScreenTexture

from perspective import Perspective
from slide import SlideBase
from state import State
from warp import Warp

import logging
LOGGER = logging.getLogger(__name__)

class PostProcess(State, Perspective, Warp, SlideBase):

    def __init__(self, parent):

        texture = OffScreenTexture("post_process")

        super(PostProcess, self).__init__(parent=parent, name="post_process", texture=texture, mesh_size=[64, 64])

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

    def get_osc_path(self):
        return '/%s/post_process' % self.parent.name

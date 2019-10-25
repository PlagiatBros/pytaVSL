# encoding: utf-8

from offscreen import OffScreenTexture

from perspective import Perspective
from slide import SlideBase
from state import State
from warp import Warp

import logging
LOGGER = logging.getLogger(__name__)

class PostProcess(State, Perspective, Warp, SlideBase):

    def __init__(self, parent):

        texture = OffScreenTexture("post_process")

        super(PostProcess, self).__init__(parent=parent, name="post_process", texture=texture, mesh_size=[1, 1])

    def capture_start(self):
        self.buf[0].textures[0]._start()

    def capture_end(self):
        self.buf[0].textures[0]._end()

    def get_osc_path(self):
        return '/%s/post_process' % self.parent.name

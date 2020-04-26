# encoding: utf-8

from pi3d.util.OffScreenTexture import OffScreenTexture

from perspective import Perspective
from slide import SlideBase
from state import State
from warp import Warp

import logging
LOGGER = logging.getLogger(__name__)


class FakeTexImage():
    def __init__(self, x, y):
        self.nbytes = x * y * 3

class OffScreenTex(OffScreenTexture):
    def __init__(self, *args, **kwargs):
        super(OffScreenTex, self).__init__(*args, **kwargs)
        self.image = FakeTexImage(self.ix, self.iy)

class PostProcess(State, Perspective, Warp, SlideBase):

    def __init__(self, parent):

        texture = OffScreenTex("post_process")

        super(PostProcess, self).__init__(parent=parent, name="post_process", texture=texture, mesh_size=[1, 1])

    def capture_start(self):
        self.buf[0].textures[0]._start()

    def capture_end(self):
        self.buf[0].textures[0]._end()

    def get_osc_path(self):
        return '/%s/post_process' % self.parent.name

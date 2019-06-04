# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import pi3d
from pi3d.Display import Display
from pi3d.constants import opengles
from utils import unicode
from osc import osc_method

import logging
LOGGER = logging.getLogger(__name__)

class Video(object):

    def __init__(self, texture, *args, **kwargs):

        self.video = False
        self.video_reader = 0

        if isinstance(texture, (str, unicode)) and '.mp4' in texture:
            import imageio
            LOGGER.warning('video support is experimental !')
            self.video_reader = imageio.get_reader(texture,  'ffmpeg', loop=True)
            texture = pi3d.Texture(self.video_reader.get_next_data())
            self.video = True

        super(Video, self).__init__(texture=texture, *args, **kwargs)

    def draw(self, *args, **kwargs):

        self.video_next_frame()

        super(Video, self).draw(*args, **kwargs)

    def video_next_frame(self):
        if self.video and self.visible:
            self.buf[0].textures[0].update_ndarray(self.video_reader.get_next_data())

# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import pi3d
from pi3d.Display import Display
from pi3d.constants import opengles
from utils import unicode
from osc import osc_method

import cv2
import numpy as np

class Video(object):

    def __init__(self, texture, *args, **kwargs):

        self.video = False
        self.video_start = 0

        if isinstance(texture, (str, unicode)) and '.mp4' in texture:
            self.video = cv2.VideoCapture(texture)
            # width = self.video.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
            # height = self.video.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
            texture = pi3d.Texture(self.video.read()[1])
            self.video.set(0,30000)

        super(Video, self).__init__(texture=texture, *args, **kwargs)


    def draw(self, *args, **kwargs):

        self.video_next_frame()

        super(Video, self).draw(*args, **kwargs)


    @osc_method('video_next')
    def video_next_frame(self):
        pass
        # if self.video and self.visible:
        #     (ok, frame) = self.video.read()
        #     if ok:
        #         self.buf[0].textures[0].update_ndarray(frame)

# encoding: utf-8

import pi3d
from osc import osc_property

import logging
LOGGER = logging.getLogger(__name__)

import numpy
import re

videos_formats = re.compile('^.*\.(mov|avi|mpg|mpeg|mp4|mkv|wmv|webm)$')

class Video(object):

    def __init__(self, texture, *args, **kwargs):

        self.video = False
        self.video_speed = 1.0
        self.video_time = 0

        if isinstance(texture, str):
            match = videos_formats.match(texture.lower())
            if match and match.string:
                LOGGER.warning('video support is experimental !')
                try:
                    global cv2
                    import cv2
                except:
                    LOGGER.error('python-opencv is required to play videos')

                self.video = True

                self.video_reader = cv2.VideoCapture(texture)
                self.video_shape = (int(self.video_reader.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(self.video_reader.get(cv2.CAP_PROP_FRAME_WIDTH)), 3)
                self.video_texture = pi3d.Texture(numpy.zeros(self.video_shape, dtype='uint8'), mipmap=False)

                self.video_frame_duration = 1. / min(self.video_reader.get(cv2.CAP_PROP_FPS), 60)
                self.video_elapsed_time = 0

                texture = self.video_texture

        super(Video, self).__init__(texture=texture, *args, **kwargs)

        if self.video:
            self.active_effects.append('VIDEO')

    def draw(self, *args, **kwargs):

        if self.video and self.visible:
            self.video_next_frame()

        super(Video, self).draw(*args, **kwargs)


    @osc_property('video_time', 'video_time')
    def set_video_time(self, time):
        """
        current video time in seconds (cpu expensive for any value other than 0)
        """
        if not self.video:
            return

        self.video_reader.set(cv2.CAP_PROP_POS_MSEC, float(time) * 1000)
        self.video_time = self.video_reader.get(cv2.CAP_PROP_POS_MSEC) / 1000.

        if self.video_time > 0:
            self.video_elapsed_time = self.parent.time


    @osc_property('video_speed', 'video_speed')
    def set_video_speed(self, speed):
        """
        video playback speed (0=paused, no reverse playback, high speed is cpu expensive)
        """
        if not self.video:
            return

        self.video_speed = max(float(speed), 0)
        self.video_elapsed_time = 0

    def video_next_frame(self):

        time = self.parent.time

        if self.video_elapsed_time is 0 or self.video_speed == 0:
            self.video_elapsed_time = time
            if self.video_speed == 0:
                return

        delta = (time - self.video_elapsed_time)
        frames = int(delta / (self.video_frame_duration / self.video_speed))

        if frames > 0:

            for i in range(frames):

                ok = self.video_reader.grab()
                if not ok:
                    self.set_video_time(0)

            self.video_elapsed_time += frames * (self.video_frame_duration / self.video_speed)
            self.video_load_current_frame()

            self.video_time = self.video_reader.get(cv2.CAP_PROP_POS_MSEC) / 1000.


    def video_load_current_frame(self):
        ok, frame = self.video_reader.retrieve()
        if ok:
            self.video_texture.update_ndarray(frame, 0)

# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import pi3d
from pi3d.Display import Display
from utils import unicode
from osc import osc_method, osc_property

import logging
LOGGER = logging.getLogger(__name__)

import numpy
import re



videos_formats = re.compile('^.*\.(mov|avi|mpg|mpeg|mp4|mkv|wmv|webm)$')

class Video(object):

    def __init__(self, texture, *args, **kwargs):

        self.video = False

        if isinstance(texture, (str, unicode)):
            match = videos_formats.match(texture)
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
                self.video_texture = pi3d.Texture(numpy.zeros(self.video_shape, dtype='uint8'))
                self.video_length = self.video_reader.get(cv2.CAP_PROP_FRAME_COUNT)
                self.video_fps = min(self.video_reader.get(cv2.CAP_PROP_FPS), 60)
                self.video_frame_duration = 1. / self.video_fps
                self.video_speed = 1.0
                self.video_frame = 0
                self.video_changed_time = 0

                texture = self.video_texture

        super(Video, self).__init__(texture=texture, *args, **kwargs)

    def draw(self, *args, **kwargs):

        if self.video and self.visible:
            self.video_next_frame()

        super(Video, self).draw(*args, **kwargs)


    @osc_property('video_frame', 'video_frame')
    def set_video_frame(self, frame):

        new_frame = int(frame) % self.video_length

        if new_frame == self.video_frame:

            return

        elif new_frame < self.video_frame:

            self.video_reader.set(cv2.CAP_PROP_POS_MSEC, new_frame * self.video_frame_duration * 1000) # faster ?
            # self.video_reader.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
            self.video_reader.grab()
            self.video_frame = new_frame

        else:

            while new_frame > self.video_frame :
                self.video_frame += 1
                ok = self.video_reader.grab()
                if not ok:
                    self.set_video_frame(0)
                    break

    # @osc_property('video_time', 'video_time')
    # def set_video_time(self, time):
    #     self.video_reader.set(cv2.CAP_PROP_POS_MSEC, float(time * 1000))
    #     self.video_frame = self.video_reade.get(cv2.CAP_PROP_POS_FRAMES)

    @osc_property('video_speed', 'video_speed')
    def set_video_speed(self, speed):
        self.video_speed = max(float(speed), 0)

    def video_next_frame(self):

        now = Display.INSTANCE.time

        if self.video_changed_time is 0 or self.video_speed == 0:
            self.video_changed_time = now

        if self.video_speed == 0:
            return

        initial_frame = self.video_frame
        current_frame = self.video_frame
        elapsed = now - self.video_changed_time
        duration = self.video_frame_duration
        duration = max(duration / abs(self.video_speed), 1. / Display.INSTANCE.frames_per_second / 1000)

        while elapsed >= duration:

            elapsed = elapsed - duration

            if self.video_speed < 0:
                current_frame = current_frame - 1
                if abs(current_frame) >= self.video_length:
                    current_frame = self.video_length - 1
            else:
                current_frame = current_frame + 1
                if abs(current_frame) >= self.video_length:
                    current_frame = 0

        if current_frame != initial_frame:

            self.video_changed_time = now + elapsed
            self.set_video_frame(current_frame)
            self.video_load_current_frame()



    def video_load_current_frame(self):
        ok, frame = self.video_reader.retrieve()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.video_texture.update_ndarray(frame)

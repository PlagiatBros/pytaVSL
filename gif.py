# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import pi3d
from pi3d.Display import Display
from PIL.GifImagePlugin import GifImageFile

from utils import unicode
from osc import osc_property

import logging
LOGGER = logging.getLogger(__name__)

class Frame(object):

    def __init__(self, ndarray, duration):
        self.ndarray = ndarray
        self.duration = duration


class Gif(object):

    def __init__(self, texture, *args, **kwargs):

        super(Gif, self).__init__(texture=texture, *args, **kwargs)

        self.gif = None
        self.gif_index = -1
        self.gif_changed_time = 0
        self.gif_duration = 0
        self.gif_speed = 1.0

        if isinstance(texture, pi3d.Texture) and  isinstance(texture.file_string, (str, unicode)) and '.gif' in texture.file_string:
            gif = GifImageFile(texture.file_string)
            if gif.is_animated:
                self.set_frames(gif)

    def set_frames(self, gif):
        self.gif = []
        for i in range(gif.n_frames):
            gif.seek(i)
            t = pi3d.Texture(gif, blend=True, mipmap=True)
            d = gif.info['duration'] / 1000.
            if d == 0:
                d = 1. / Display.INSTANCE.frames_per_second
            self.gif.append(Frame(t.image, d))
            if i == 0:
                self.texture = t
                self.set_textures([t])

    def gif_next_frame(self):

        now = Display.INSTANCE.time

        if self.gif_changed_time is 0 or self.gif_speed == 0:
            self.gif_changed_time = now

        if self.gif_speed == 0:
            return

        initial_frame = self.gif[self.gif_index]
        current_frame = self.gif[self.gif_index]
        elapsed = now - self.gif_changed_time
        duration = self.gif_duration if self.gif_duration != 0 else current_frame.duration
        duration = max(duration / abs(self.gif_speed), 1. / Display.INSTANCE.frames_per_second / 1000)

        while elapsed >= duration:

            elapsed = elapsed - duration

            if self.gif_speed < 0:
                self.gif_index = self.gif_index - 1
                if abs(self.gif_index) >= len(self.gif):
                    self.gif_index = -1
            else:
                self.gif_index = self.gif_index + 1
                if abs(self.gif_index) >= len(self.gif):
                    self.gif_index = 0

            current_frame = self.gif[self.gif_index]
            duration = self.gif_duration if self.gif_duration != 0 else current_frame.duration
            duration = max(duration / abs(self.gif_speed), 1. / Display.INSTANCE.frames_per_second / 1000)


        if current_frame is not initial_frame:

            self.buf[0].textures[0].update_ndarray(current_frame.ndarray)
            self.gif_changed_time = now + elapsed


    def draw(self, *args, **kwargs):

        if self.gif and self.visible:
            self.gif_next_frame()

        super(Gif, self).draw(*args, **kwargs)

    @osc_property('frame', 'gif_index')
    def set_frame(self, frame):
        self.gif_changed_time = 0
        frame = int(frame)
        if self.gif_speed < 0:
            frame += 1
        else:
            frame -= 1
        self.gif_index = frame
        if self.gif:
            self.buf[0].textures[0].update_ndarray(self.gif[self.gif_index].ndarray)

    @osc_property('speed', 'gif_speed')
    def set_speed(self, speed):
        self.gif_speed = float(speed)

    @osc_property('duration', 'gif_duration')
    def set_duration(self, duration):
        self.gif_duration = float(duration)

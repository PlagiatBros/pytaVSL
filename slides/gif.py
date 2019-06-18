# encoding: utf-8

import pi3d
from PIL.GifImagePlugin import GifImageFile

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
        self.gif_length = 0

        if isinstance(texture, str) and '.gif' in texture:
            gif = GifImageFile(texture)
            if gif.is_animated:
                self.set_frames(gif)

    def set_frames(self, gif):
        self.gif = []
        for i in range(gif.n_frames):
            gif.seek(i)
            t = pi3d.Texture(gif, mipmap=False)
            d = gif.info['duration'] / 1000.
            if d == 0:
                d = 1. / self.parent.fps
            self.gif.append(Frame(t.image, d))
            if i == 0:
                self.texture = t
                self.set_textures([t])
        self.gif_length = len(self.gif)

    def gif_next_frame(self):

        now = self.parent.time

        if self.gif_changed_time is 0 or self.gif_speed == 0:
            self.gif_changed_time = now

        if self.gif_speed == 0:
            return

        initial_frame = self.gif[self.gif_index]
        current_frame = self.gif[self.gif_index]
        elapsed = now - self.gif_changed_time
        duration = self.gif_duration / self.gif_length if self.gif_duration != 0 else current_frame.duration
        duration = max(duration / abs(self.gif_speed), 1. / self.parent.fps / 1000)

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
            duration = self.gif_duration / self.gif_length if self.gif_duration != 0 else current_frame.duration
            duration = max(duration / abs(self.gif_speed), 1. / self.parent.fps / 1000)


        if current_frame is not initial_frame:

            self.buf[0].textures[0].update_ndarray(current_frame.ndarray, 0)

            self.gif_changed_time = now + elapsed


    def draw(self, *args, **kwargs):

        if self.gif and self.visible:
            self.gif_next_frame()

        super(Gif, self).draw(*args, **kwargs)

    @osc_property('gif_frame', 'gif_index')
    def set_frame(self, frame):
        """
        current gif frame
        """
        self.gif_changed_time = 0
        frame = int(frame)
        if self.gif_speed < 0:
            frame += 1
        else:
            frame -= 1
        self.gif_index = frame
        if self.gif:
            self.buf[0].textures[0].update_ndarray(self.gif[self.gif_index].ndarray, 0)

    @osc_property('gif_speed', 'gif_speed')
    def set_speed(self, speed):
        """
        gif playback speed (0=paused, negative=reverse)
        """
        self.gif_speed = float(speed)

    @osc_property('gif_duration', 'gif_duration')
    def set_duration(self, duration):
        """
        gif total duration (override frames' durations)
        """
        self.gif_duration = float(duration)

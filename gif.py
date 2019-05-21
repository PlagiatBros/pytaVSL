# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import pi3d

from pi3d.Display import Display

import logging
LOGGER = logging.getLogger(__name__)

class Frame(object):

    def __init__(self, ndarray, duration):
        self.ndarray = ndarray
        self.duration = duration

class Gif(object):

    def __init__(self, *args, **kwargs):

        super(Gif, self).__init__()

        self.gif = None
        self.gif_index = -1
        self.gif_changed_time = 0
        self.gif_duration = 0
        self.gif_speed = 1.0


    def set_speed(self, speed):
        self.gif_speed = float(speed)

    def set_duration(self, duration):
        self.gif_duration = float(duration)

    def set_frames(self, gif):
        self.gif = []
        for i in range(gif.n_frames):
            gif.seek(i)
            t = pi3d.Texture(gif, blend=True, mipmap=True)
            d = gif.info['duration'] / 1000.
            self.gif.append(Frame(t.image, d))
            if i == 0:
                self.set_textures([t])

    def gif_reset(self):
        self.gif_changed_time = 0
        self.gif_index = -1 if self.gif_speed > 0 else 0

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

            # self.set_textures([current_frame])
            self.buf[0].textures[0].update_ndarray(current_frame.ndarray)
            # initial_frame.unload_opengl()
            self.gif_changed_time = now + elapsed


    def draw(self, *args, **kwargs):

        if self.gif:
            self.gif_next_frame()

        super(Gif, self).draw(*args, **kwargs)


    def get_param_getter(self, name):
        """
        Getters for osc & animations
        """
        _val = super(Gif, self).get_param_getter(name)

        val = 0
        if name == 'speed':
            val = self.gif_speed
        elif name == 'duration':
            val = self.gif_duration

        return val if val is not 0 else _val

    def get_param_setter(self, name):
        """
        Setters for osc & animations
        """

        _set_val = super(Gif, self).get_param_setter(name)

        if name == 'speed':
            def set_val(val):
                self.set_speed(val)
        elif name == 'duration':
            def set_val(val):
                self.set_duration(val)
        else:
            set_val = None

        return set_val if set_val is not None else _set_val

# encoding: utf-8

from math import floor
from abc import abstractmethod
import pi3d
from pi3d.Display import Display

from utils import KillableThread as Thread

import logging
LOGGER = logging.getLogger(__name__)

class Animation():

    def __init__(self, name, start, end, duration, setter, loop):
        self.name = name
        self.start = start
        self.end = end
        self.duration = duration
        self.forward_a = 1.0 * (end - start) / duration
        self.backward_a = 1.0 * (start - end) / duration
        self.setter = setter
        self.loop = loop
        self.backward = False
        self.reset()

    def reset(self):
        self.done = False
        self.start_date = Display.INSTANCE.time
        self.end_date = self.duration + self.start_date
        if self.loop == -1:
            self.backward = not self.backward

    def play(self):
        t = Display.INSTANCE.time - self.start_date
        t += 1. / Display.INSTANCE.frames_per_second # always 1 frame early for smooth anims
        if t >= self.duration:
            t = self.duration
            self.done = True
        if self.backward:
            self.setter(self.backward_a * t + self.end)
        else:
            self.setter(self.forward_a * t + self.start)


class Animable(object):

    def __init__(self, *args, **kwargs):

        super(Animable, self).__init__(*args, **kwargs)

        self.animations = {}


    def animate(self, name, start, end, duration, loop=False):
        """
        Animate a property

        Args:
            name  (str):
            start (int):
            end   (int):
            duration (float):
        """
        current = self.get_param_getter(name)
        _start = self.parse_animate_value(start, current)
        _end = self.parse_animate_value(end, current)
        setter = self.get_param_setter(name)

        if setter is None:
            LOGGER.error('ERROR: Attempting to animate non-animable property "%s" on %s' % (name, self))
            return

        self.animations[name] = Animation(name, _start, _end, duration, setter, loop)

    def animate_next_frame(self):
        if self.animations:
            anims = list(self.animations.values())
            for anim in anims:
                anim.play()
                if anim.done:
                    if anim.loop:
                        anim.reset()
                        anim.play()
                    else:
                        self.stop_animate(anim.name)

    def stop_animate(self, name=None):
        """
        Stop animations
        """
        if name is not None and name in self.animations:
            del self.animations[name]
        elif name is None:
            self.animations = {}

    def parse_animate_value(self, val, current):

        if type(val) is str and len(val) > 1:
            operator = val[0]
            if operator == '+' or operator == '-':
                return current + float(val)
            elif operator == '*':
                return current * float(val[1:])
            elif operator == '/':
                return current / float(val[1:])

        if type(val) is not str:
            return val
        else:
            LOGGER.error('ERROR: failed to parse animate value %s (%s)' % (val, type(val)))
            return current

    @abstractmethod
    def get_param_getter(self, name):
        """
        Getters for animations
        """
        val = 0

        return val

    @abstractmethod
    def get_param_setter(self, name):
        """
        Setters for animations
        """
        def set_val(val):
            pass

        return set_val

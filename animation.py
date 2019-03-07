# encoding: utf-8

import time
from math import floor
from abc import abstractmethod
import pi3d

from utils import KillableThread as Thread

import logging
LOGGER = logging.getLogger(__name__)

FPS = 25

class Animation():

    def __init__(self, start, end, duration, setter):
        self.start = start
        self.duration = duration
        self.start_date = time.time()
        self.end_date = duration + self.start_date
        self.a = 1.0 * (end - start) / duration
        self.setter = setter
        self.done = False

    def play(self):
        t = time.time() - self.start_date
        if t >= self.duration:
            t = self.duration
            self.done = True
        self.setter(self.a * t + self.start)


class Animable(object):

    def __init__(self, *args, **kwargs):

        super(Animable, self).__init__()

        self.rate = FPS #pi3d.Display.Display.INSTANCE.frames_per_second

        self.wait_for_next_frame = False

        self.animations = {}


    def animate(self, name, start, end, duration):
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

        self.animations[name] = Animation(_start, _end, duration, setter)

    def animate_next_frame(self):
        delete = []
        for name in self.animations:
            self.animations[name].play()
            if self.animations[name].done:
                delete.append(name)
        for n in delete:
            del self.animations[n]

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
    def get_animate_value(self, name):
        """
        Getters for animations
        """
        val = 0

        return val

    @abstractmethod
    def get_animate_setter(self, name):
        """
        Setters for animations
        """
        def set_val(val):
            pass

        return set_val

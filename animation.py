# encoding: utf-8

from math import floor
from abc import abstractmethod
import pi3d
from pi3d.Display import Display

from utils import KillableThread as Thread

import logging
LOGGER = logging.getLogger(__name__)

class Animation():

    def __init__(self, name, start, end, duration, setter):
        self.name = name
        self.start = start
        self.duration = duration
        self.start_date = Display.INSTANCE.time
        self.end_date = duration + self.start_date
        self.a = 1.0 * (end - start) / duration
        self.setter = setter
        self.done = False

    def play(self):
        t = Display.INSTANCE.time - self.start_date
        if t >= self.duration:
            t = self.duration
            self.done = True
        self.setter(self.a * t + self.start)


class Animable(object):

    def __init__(self, *args, **kwargs):

        super(Animable, self).__init__()

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

        self.animations[name] = Animation(name, _start, _end, duration, setter)

    def animate_next_frame(self):
        delete = []
        anims = self.animations.values()
        for anim in anims:
            anim.play()
            if anim.done:
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

# encoding: utf-8

import time
from abc import abstractmethod
import pi3d

from utils import KillableThread as Thread

LOGGER = pi3d.Log(__name__)

class Animation(object):

    def __init__(self, *args, **kwargs):

        super(Animation, self).__init__()

        self.rate = pi3d.Display.Display.INSTANCE.frames_per_second
        self.framelength = 1. / self.rate

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
        def threaded():

            nb_step = int(round(duration * self.rate))

            if nb_step < 1:
                return

            current = self.get_animate_value(name)
            _start = self.parse_animate_value(start, current)
            _end = self.parse_animate_value(end, current)

            a = float(_end - _start) / nb_step

            set_val = self.get_animate_setter(name)

            for i in range(nb_step + 1):

                set_val(a * i + _start)

                time.sleep(self.framelength)

        self.stop_animate(name)

        self.animations[name] = Thread(target=threaded)
        self.animations[name].start()

    def stop_animate(self, name=None):
        """
        Stop animations
        """
        if name is not None and name in self.animations:
            try:
                self.animations[name].kill()
            except:
                pass
            del self.animations[name]
        elif name is None:
            for name in self.animations:
                try:
                    self.animations[name].kill()
                except:
                    pass
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

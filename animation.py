# encoding: utf-8

import time
from math import floor
from abc import abstractmethod
import pi3d

from utils import KillableThread as Thread

LOGGER = pi3d.Log(__name__)

FPS = 25

class Animation(object):

    def __init__(self, *args, **kwargs):

        super(Animation, self).__init__()

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
        def threaded():

            nb_step = int(round(duration * self.rate))
            step_duration = 1.0 * duration / nb_step

            if nb_step < 1:
                nb_step = 1

            current = self.get_param_getter(name)
            _start = self.parse_animate_value(start, current)
            _end = self.parse_animate_value(end, current)

            a = float(_end - _start) / nb_step

            set_val = self.get_param_setter(name)

            tick = -1
            clock_tick = 0
            clock_time = time.time()
            run = True

            while run:
                delta = time.time() - clock_time
                delta_ticks = floor(delta/step_duration)
                clock_tick += delta_ticks
                clock_time += delta_ticks * step_duration
                if tick < clock_tick:
                    tick = clock_tick
                    if tick >= nb_step :
                        run = False
                        tick = nb_step
                    set_val(a * tick + _start)
                while self.wait_for_next_frame:
                    time.sleep(0.001)
                self.wait_for_next_frame = True


        if self.get_animate_setter(name) is None:
            LOGGER.error('ERROR: Attempting to animate non-animable property "%s" on %s' % (name, self))
            return

        self.stop_animate(name)

        self.animations[name] = Thread(target=threaded)
        self.animations[name].start()

    def animate_next_frame(self):
        self.wait_for_next_frame = False

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

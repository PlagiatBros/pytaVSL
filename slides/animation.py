# encoding: utf-8

from osc import osc_method

import logging
LOGGER = logging.getLogger(__name__)


from inspect import getmembers
import easing_functions

EASING_NAMES = [
    "linear",
    "back",
    "bounce",
    "circular",
    "cubic",
    "elastic",
    "exponential",
    "quad",
    "quartic",
    "quintic",
    "sine"
]
EASING_FUNCTIONS = {}
for name, easing in getmembers(easing_functions):
    name = name.replace('Ease', '').replace('InOut', '').lower()
    if name in EASING_NAMES or name[0:-2] in EASING_NAMES or name[0:-3] in EASING_NAMES:
        EASING_FUNCTIONS[name] = easing



class Animation():

    def __init__(self, parent, name, start, end, duration, loop, easing, setter):

        self.parent = parent
        self.name = name

        self.start = start
        self.end = end
        self.duration = max(0.01, duration)
        self.loop = loop

        self.nargs = len(start)

        if not easing in EASING_FUNCTIONS:
            LOGGER.error('unknown easing "%s", falling back to "linear"' % easing)
            easing = "linear"

        self.easing = easing
        self.easing_func = [EASING_FUNCTIONS[easing](start=start[i], end=end[i], duration=self.duration) for i in range(self.nargs)]

        self.setter = setter
        self.backward = False
        self.current = None
        self.reset(True)

    def reset(self, init=False):
        self.done = False
        self.current = None
        self.start_date = self.parent.time
        self.end_date = self.duration + self.start_date
        if self.loop == -1 and not init:
            self.backward = not self.backward

    def play(self):
        t = self.parent.time - self.start_date
        t += 1. / self.parent.fps # always 1 frame early for smooth anims
        if t >= self.duration:
            t = self.duration
            self.done = True

        if self.backward:
            t = self.duration - t

        value = [self.easing_func[i].ease(t) for i in range(self.nargs)]

        if value != self.current:
            self.setter(*value)
            self.current = value

    def get_state(self):
        return {
            'from': self.start,
            'to': self.end,
            'duration': [self.duration],
            'loop': [self.loop],
            'easing': [self.easing],
        }

class Strobe():

    def __init__(self, parent, start, end, duration, ratio, setter):

        self.parent = parent

        self.duration = max(float(duration), 0.001)
        self.ratio = ratio
        self.start = start
        self.end = end
        self.setter = setter

        self.date = self.parent.time
        self.breakpoint = max(float(self.ratio), 0.0) * self.duration
        self.current = None

    def play(self):
        t = self.parent.time + 1. / self.parent.fps # always 1 frame early for smooth anims
        delta = t - self.date
        progress = delta % self.duration
        state = progress < self.breakpoint
        if state != self.current:
            value = self.start if state else self.end
            self.setter(*value)
            self.current = state

    def get_state(self):
        return {
            'from': self.start,
            'to': self.end,
            'duration': [self.duration],
            'ratio': [self.ratio],
        }

class Animable(object):

    def __init__(self, *args, **kwargs):

        super(Animable, self).__init__(*args, **kwargs)

        self.animations = {}
        self.strobes = {}

    @osc_method('animate')
    def animate(self, property, *args):
        """
        Animate a property
            property: exposed osc property
            args: [from ...] [to ...] duration loop=0 easing="linear"
                from: initial value(s) (items with default values must be omitted)
                to: destination value(s) (items with default values must be omitted)
                duration: animation duration in seconds
                loop: omitted / 0 (no loop), 1 (infinte loop) or -1 (infinite back-and-forth)
                easing: easing function (case-insentive), optionally suffixed with "in" or "out"

            note: loop and easing can be interchanged
            available easing functions: linear, back, bounce, circular, cubic, elastic, exponential, quad, quartic, quintic, sine

        """

        attribute = str(property).lower()

        if attribute == 'visible':
            LOGGER.error('invalid property argument "%s" for %s/animate' % (attribute, self.get_osc_path()))
            return

        if attribute in self.osc_attributes:
            method = self.osc_attributes[attribute]
            argcount = method.osc_argcount_min

            if len(args) < argcount * 2 + 1 or len(args) > argcount * 2 + 3:
                LOGGER.error('bad number of argument for %s/animate %s (%i to %i expected, %i provided)' % (self.get_osc_path(), attribute, argcount * 2 + 1, argcount * 2 + 3, len(args)))
                return

            duration = args[-1]
            loop = 0
            easing = "linear"
            if len(args) == (argcount * 2 + 2):
                if type(args[-1]) is str:
                    easing = args[-1].lower()
                else:
                    loop = args[-1]
                duration = args[-2]
            if len(args) == (argcount * 2 + 3):
                if type(args[-1]) is str:
                    easing = args[-1].lower()
                    loop = args[-2]
                else:
                    loop = args[-1]
                    easing = args[-2].lower()
                duration = args[-3]

            current = self.osc_get_value(attribute)
            if current is not None:
                args = [self.osc_parse_value(args[i], current[i % argcount]) for i in range(argcount * 2)]

            start = [args[i] for i in range(argcount)]
            end = [args[i + argcount] for i in range(argcount)]

            self.animations[attribute] = Animation(self.parent, attribute, start, end, duration, loop, easing, method)

        else:
            LOGGER.error('invalid property argument "%s" for %s/animate' % (attribute, self.get_osc_path()))

    @osc_method('animate_stop')
    def stop_animate(self, *properties):
        """
        Stop animation
            property: exposed osc property (stop all animations if omitted)
        """
        for name in properties:
            if name in self.animations:
                del self.animations[name]

        if len(properties) == 0:
            self.animations = {}

    @osc_method('strobe')
    def strobe(self, property, *args):
        """
        Strobe a property
            property: exposed osc property
            args: [from ...] [to ...] period ratio
                from: initial value(s) (items with default values must be omitted)
                to: destination value(s) (items with default values must be omitted)
                duration: strobe period in seconds
                ratio: time proportion spent on "from" (0<>1)
        """
        attribute = str(property).lower()

        if attribute == 'visible':
            LOGGER.error('invalid property argument "%s" for %s/strobe' % (attribute, self.get_osc_path()))
            return

        if attribute in self.osc_attributes:
            method = self.osc_attributes[attribute]
            argcount = method.osc_argcount_min

            if len(args) != argcount * 2 + 2:
                LOGGER.error('bad number of argument for %s/strobe %s (%i expected, %i provided)' % (self.get_osc_path(), attribute, argcount * 2 + 2, len(args)))
                return

            duration = args[-2]
            ratio = args[-1]

            current = self.osc_get_value(attribute)
            if current is not None:
                args = [self.osc_parse_value(args[i], current[i % argcount]) for i in range(argcount * 2)]

                start = [args[i] for i in range(argcount)]
                end = [args[i + argcount] for i in range(argcount)]

                self.strobes[attribute] = Strobe(self.parent, start, end, duration, ratio, method)

        else:
            LOGGER.error('invalid property argument "%s" for %s/strobe' % (attribute, self.get_osc_path()))

    @osc_method('strobe_stop')
    def stop_strobe(self, *properties):
        """
        Stop strobe
            property: exposed osc property (stop all strobes if omitted)
        """
        for name in properties:
            if name in self.strobes:
                del self.strobes[name]

        if len(properties) == 0:
            self.strobes = {}

    def draw(self, *args, **kwargs):
        """
        Compute current state of animations
        """
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
        if self.strobes:
            for name in self.strobes:
                self.strobes[name].play()

        super(Animable, self).draw(*args, **kwargs)

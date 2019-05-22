# encoding: utf-8

import pi3d
from pi3d.Display import Display

import logging
LOGGER = logging.getLogger(__name__)

class StrobeState():

    def __init__(self):
        self.period = 2.0 * 0.04
        self.ratio = 0.5
        self.reset()

    def reset(self):
        self.date = Display.INSTANCE.time
        self.breakpoint = self.ratio * self.period

    def set_period(self, l):
        self.period = max(int(l), 0.001) * 0.04
        self.reset()

    def set_ratio(self, r):
        self.ratio = max(float(r), 0.0)
        self.reset()

    def visible(self):
        delta = Display.INSTANCE.time - self.date
        progress = delta % self.period
        return progress < self.breakpoint

class Strobe(object):

    def __init__(self, *args, **kwargs):

        super(Strobe, self).__init__(*args, **kwargs)

        self.strobe = False
        self.strobe_state = StrobeState()

    def set_strobe(self, strobe=None, period=None, ratio=None):
        """
        Set strobe mode

        Args:
            strobe  (bool): True to enable strobe mode
            period (float): (optional) period of the strobe cycle in frames
            ratio  (float): (optional) ratio between hidden and show frames
        """
        if not self.strobe and strobe:
            self.strobe_state.cursor = 0

        if period is not None:
            self.strobe_state.set_period(period)

        if ratio is not None:
            self.strobe_state.set_ratio(ratio)

        if strobe is not None:
            self.strobe = bool(strobe)

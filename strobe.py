# encoding: utf-8

import pi3d

import logging
LOGGER = logging.getLogger(__name__)

class StrobeState():

    def __init__(self):
        self.period = 2.0
        self.ratio = 0.5
        self.cursor = 0
        self.visble = True
        self.regen()

    def regen(self):
        self.breakpoint = self.period * self.ratio

    def set_period(self, l):
        self.period = max(int(l), 0.0)
        self.regen()

    def set_ratio(self, r):
        self.ratio = max(float(r), 0.0)
        self.regen()

    def next(self):
        self.cursor += 1
        if self.cursor < self.breakpoint:
            self.visible = True
        elif self.cursor < self.period:
            self.visible = False
        else:
            self.cursor = 0
            self.visible = True

class Strobe(object):

    def __init__(self, *args, **kwargs):

        super(Strobe, self).__init__()

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

# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

from threading import Thread, current_thread
from sys import settrace
import pi3d

import logging
LOGGER = logging.getLogger(__name__)


class osc_range_method():

    def __init__(self, n):

        self.n = n
        self.range = range(n)

    def __call__(self, method):

        def range_method(this, path, args):

            if args[0] == -1:
                for i in self.range:
                    args[0] = i
                    method(this, path, args)
            elif args[0] < self.n:
                method(this, path, args)
            else:
                LOGGER.error("OSC ARGS ERROR: Slide number out of range")

        return range_method


class KillableThread(Thread):
    """
    A subclass of Thread, with a kill() method.
    Original code: Connelly Barnes
    """

    def __init__(self, *args, **keywords):
        Thread.__init__(self, *args, **keywords)
        self.killed = False

    def start(self):
        """Start the thread."""
        self.__run_backup = self.run
        self.run = self.__run # Force the Thread to install our trace.
        Thread.start(self)

    def __run(self):
        """ Hacked run function, which installs the trace."""
        settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, why, arg):
        if why == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, why, arg):
        if self.killed:
            if why == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True

    @staticmethod
    def get_current():
        return current_thread()

try:
    # python3 compat
    unicode = unicode
except:
    unicode = str

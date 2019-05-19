# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
LOGGER = logging.getLogger(__name__)
import sys

from text import FONTS

class MemoryMonitor(object):

    def __init__(self, max=512, flush=None):

        self.allocated = 0
        self.max = max * 1000000
        self.flush = flush

        for k in FONTS:
            self.allocated += FONTS[k].image.nbytes

    def slide_size(self, slide):
        return slide.buf[0].textures[0].image.nbytes

    def alloc(self, slide):
        self.allocated += self.slide_size(slide)
        if self.full() and self.flush is not None:
            LOGGER.debug('Too much texture memory alloacted: flushing...')
            self.flush()
        LOGGER.debug('Texture uploaded to GPU. Total allocated: %.1fMB' % (self.allocated / 1000000.))

    def free(self, slide):
        self.allocated -= self.slide_size(slide)
        LOGGER.debug('Texture flushed from GPU. Total allocated: %.1fMB' % (self.allocated / 1000000.))


    def full(self):
        return self.allocated >= self.max


gpu_monitor = MemoryMonitor(64)

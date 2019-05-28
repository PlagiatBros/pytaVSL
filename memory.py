# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

from config import *

import logging
LOGGER = logging.getLogger(__name__)

class MemoryMonitor(object):

    def __init__(self, max=512, flush=None):

        self.allocated = 0
        self.max = max * 1000000
        self.flush = flush
        self.loaded = []

        for k in FONTS:
            self.allocated += FONTS[k].image.nbytes * 1.33 # 1.33 = mipmap

    def get_data(self, slide):
        if len(slide.buf[0].textures) > 0:
            return slide.buf[0].textures[0]
        else:
            return None

    def alloc(self, slide):

        data = self.get_data(slide)
        if data and not data in self.loaded:
            self.allocated += data.image.nbytes * 1.33 # 1.33 = mipmap
            LOGGER.debug('Texture uploaded to GPU. Total allocated: %.1fMB' % (self.allocated / 1000000.))

        self.loaded.append(data)

        if self.full() and self.flush is not None:
            LOGGER.debug('Too much texture memory allocated: flushing...')
            self.flush(slide)
            return False

        return True

    def free(self, slide):
        data = self.get_data(slide)
        if data and data in self.loaded:
            self.loaded.remove(data)
            if not data in self.loaded:
                self.allocated -= data.image.nbytes * 1.33 # 1.33 = mipmap
                LOGGER.debug('Texture flushed from GPU. Total allocated: %.1fMB' % (self.allocated / 1000000.))

    def full(self):
        return self.allocated >= self.max


gpu_monitor = MemoryMonitor(64)

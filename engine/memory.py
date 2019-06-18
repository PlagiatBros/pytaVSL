# encoding: utf-8

from config import *

import logging
LOGGER = logging.getLogger(__name__)

class MemoryMonitor(object):

    def __init__(self, max=512, flush=None):

        self.allocated = 0
        self.max = max * 1000000
        self.flush = flush
        self.loaded = []

    def get_data(self, slide):
        if len(slide.buf[0].textures) > 0:
            tex = slide.buf[0].textures[0]
            size = tex.image.nbytes
            if tex.mipmap:
                size *= 1.33
            return [tex, size]
        else:
            return [None, 0]

    def alloc(self, slide):

        tex, size = self.get_data(slide)
        if tex and not tex in self.loaded:
            self.allocated += size
            LOGGER.debug('%s uploaded to GPU. Total allocated: %.1fMB' % (slide.name, self.allocated / 1000000.))

        self.loaded.append(tex)

        if self.full() and self.flush is not None:
            LOGGER.debug('Too much texture memory allocated: flushing...')
            self.flush(slide)
            return False

        return True

    def free(self, slide):
        tex, size = self.get_data(slide)
        if tex and tex in self.loaded:
            self.loaded.remove(tex)
            if not tex in self.loaded:
                self.allocated -= size
                LOGGER.debug('%s flushed from GPU. Total allocated: %.1fMB' % (slide.name, self.allocated / 1000000.))

    def full(self):
        return self.allocated >= self.max

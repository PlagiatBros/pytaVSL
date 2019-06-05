# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

from threading import Thread, current_thread
from sys import settrace
import numpy
import pi3d

import logging
LOGGER = logging.getLogger(__name__)

_empty_texture = None
def empty_texture():
    global _empty_texture
    if not _empty_texture:
        _empty_texture = pi3d.Texture(numpy.zeros((1,1,4), dtype='uint8'))
    return _empty_texture

try:
    # python3 compat
    unicode = unicode
    unichr = unichr
except:
    unicode = str
    unichr = chr

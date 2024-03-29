# encoding: utf-8

from ..utils import relative_path

from pi3d.Display import Display
import pi3d

from itertools import combinations

import logging
LOGGER = logging.getLogger(__name__)

def _load_shader(text):
    new_text = ''
    if '#include' in text:
        for line in text.split('\n'):
            if '#include' in line:
                inc_file = line.split()[1]
                new_text += _load_shader(open(relative_path(inc_file), 'r').read()) + '\n'
            else:
                new_text += line + '\n'
    else:
        new_text = text
    return new_text

baseFs = _load_shader(open(relative_path('shaders/base.fs'), 'r').read())
baseVs = _load_shader(open(relative_path('shaders/base.vs'), 'r').read())


SHADER_CACHE = {}

def get_shader(effects, log=True):

    effects.sort()
    name = '_'.join(effects)

    if not name in SHADER_CACHE:

        if log:
            LOGGER.debug('compiling shader "%s"' % name)

        defines = ''

        if 'TEXT' in name:
            defines += '#extension GL_OES_standard_derivatives : enable\n'

        for fx in effects:
            defines += '#define %s\n' % fx

        fs = defines + baseFs.replace('{WIDTH}', str(float(Display.INSTANCE.width))).replace('{HEIGHT}', str(float(Display.INSTANCE.height)))
        vs = defines + baseVs

        SHADER_CACHE[name] = pi3d.Shader(None, vs, fs)

    return SHADER_CACHE[name]


def init_shader_cache():
    print('precompiling shaders...')

    PRECOMPILED = ['KEY', 'CHARCOAL', 'RGBWAVE', 'INVERT', 'MASK', 'NOISE', 'COLORS', 'BLUR']

    for i in range(len(PRECOMPILED)):
        combos = list(combinations(PRECOMPILED, i))
        for combo in combos:
            for prefix in [None, 'TEXT', 'VIDEO']:
                c = list(combo)
                if prefix:
                    c.append(prefix)
                get_shader(c, False)

    print('%i shaders combinations in cache' % len(SHADER_CACHE))

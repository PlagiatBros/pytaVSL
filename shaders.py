# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

from pi3d.Display import Display
import pi3d

from itertools import combinations

def _load_shader(text):
    new_text = ''
    if '#include' in text:
        for line in text.split('\n'):
            if '#include' in line:
                inc_file = line.split()[1]
                new_text += _load_shader(open(inc_file, 'r').read()) + '\n'
            else:
                new_text += line + '\n'
    else:
        new_text = text
    return new_text

baseFs = _load_shader(open('shaders/base.fs', 'r').read())
baseVs = _load_shader(open('shaders/base.vs', 'r').read())


SHADER_CACHE = {}

def get_shader(effects):

    effects.sort()
    name = '_'.join(effects)

    if not name in SHADER_CACHE:

        fsdata = ''
        for fx in effects:
            fsdata += '#define %s\n' % fx
        fsdata += baseFs

        fs = fsdata.replace('{WIDTH}', str(float(Display.INSTANCE.width))).replace('{HEIGHT}', str(float(Display.INSTANCE.height)))
        vs = baseVs

        SHADER_CACHE[name] = pi3d.Shader(None, vs, fs)

    return SHADER_CACHE[name]


def init_shader_cache():

    EFFECTS = ['KEY', 'CHARCOAL', 'RGBWAVE', 'INVERT', 'MASK', 'NOISE']

    for prefix in [None, 'VIDEO', 'POST_PROCESS']:

        effects = EFFECTS[:]
        if prefix:
            effects.append(prefix)

        for i in range(len(effects)):
            combos = list(combinations(effects, i))
            for combo in combos:
                get_shader(list(combo))

    print('%i shaders combinations in cache' % len(SHADER_CACHE))

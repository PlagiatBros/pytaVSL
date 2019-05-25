# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import pi3d

EFFECTS = [
    'default',
    'noise',
    'rgbwave',
    'charcoal'
]

SHADERS = {}

baseFs = open('shaders/base.fs', 'r').read()
baseVs = open('shaders/base.vs', 'r').read()
_loader = pi3d.Shader._default_instance()

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

def init_shaders():

    for name in EFFECTS:

        fs = _load_shader(baseFs.replace('{}', name))
        vs = _load_shader(baseVs)

        SHADERS[name] = pi3d.Shader(None, vs, fs)

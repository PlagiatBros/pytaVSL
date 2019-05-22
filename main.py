#!/usr/bin/python

"""
Usage: python main.py port path [options]
    port: udp port or unix socket path
    path: image files to load (glob pattern)

Options:
    --debug: enable debug loggin

"""

import os.path
import liblo
import sys

from pyta import PytaVSL

p = None
path = None

for arg in sys.argv:
    if arg.isdigit() or '/tmp' in arg:
        p = arg
    elif '/' in arg and arg != 'main.py':
        if os.path.isabs(arg):
            path = arg
        else:
            path = os.path.join(os.path.dirname(__file__), arg)


def loaded(pyta):
    print('%i slides loaded in %s' % (len(pyta.slides.values()), pyta.path))

pyta = PytaVSL(port=p, path=path, load_cb=loaded, fps=25, depth=24, fullscreen='--fullscreen' in sys.argv)

pyta.start()

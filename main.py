#!/usr/bin/python

import os.path
import liblo
import sys

from pyta import PytaVSL

p = None
path = None

for arg in sys.argv:
    if arg.isdigit():
        p = arg
    if '/' in arg and arg != 'main.py':
        if os.path.isabs(arg):
            path = arg
        else:
            path = os.path.join(os.path.dirname(__file__), arg)


def loaded(pyta):
    print('%i slides loaded in %s' % (len(pyta.slides.values()), pyta.path))
    if 'Mask_1' in pyta.slides:
        print('Displaying Mask_1 with Z = -99')
        liblo.send('osc.udp://127.0.0.1:%i' % pyta.port, '/pyta/slide/position_z', 'Mask_1', -99)
        liblo.send('osc.udp://127.0.0.1:%i' % pyta.port, '/pyta/slide/visible', 'Mask_1', 1)

pyta = PytaVSL(port=p, path=path, load_cb=loaded)

pyta.start()

#!/usr/bin/python
# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

"""This is the main file of pytaVSL. It aims to provide a VJing and lights-projector-virtualisation tool.

Images are loaded as textures, which then are mapped onto slides (canvases - 8 of them).

This file was deeply instpired by Slideshow.py demo file of pi3d.
"""

import time, glob, threading
import pi3d
import liblo
import random
import os.path
import os
import sys
import getopt

from font import Font
from TextBlock import TextBlock

from six.moves import queue

# LOGGER = pi3d.Log.logger(__name__)
LOGGER = pi3d.Log()
LOGGER.info("Log using this expression.")


class Container:
    '''
    Container might contains several slides which inherits from its position, angle, scale...
    # TODO : container might be moved
    # TODO : several containers in one pytaVSL instance
    '''
    def __init__(self, parent):
        self.parent = parent

        # Text
        self.font = pi3d.Font('sans.ttf', font_size=128, codepoints="ABCDEFGHIJKLMNOPQRSTUVWXYZ ?$.", background_color='#ff000000')
        self.textmanager = pi3d.PointText(self.font, parent.CAMERA, max_chars=300, point_size=256)
        self.text = pi3d.TextBlock(0, 0, 0.01, 0.0, 200, text_format='CUL',
          size=0.99, spacing="C", space=1.5, colour=(1.0, 1.0, 1.0, 1.0))
        self.textmanager.add_text_block(self.text)

    def draw(self):
        self.textmanager.draw()


class PytaText(object):
    '''
    PytaVSL contains the screen, the camera, the light, and the slides containers. It's also an OSC server which contains the method to control all of its children.
    '''
    def __init__(self, port=56418):
        # setup OSC
        self.port = port

        # setup OpenGL
        self.DISPLAY = pi3d.Display.create(background=(0.0, 0.0, 0.0, 0.0), frames_per_second=25)
        self.shader = pi3d.Shader("uv_light")
        self.matsh = pi3d.Shader("mat_light")
        self.CAMERA = pi3d.Camera(is_3d=True)
        self.light = pi3d.Light(lightpos=(1, 1, -3))
        self.light.ambient((1, 1, 1))

        # Containers
        self.ctnr = Container(parent=self)



    def on_start(self):
        if self.port is not None:
            self.server = liblo.ServerThread(self.port)
            self.server.register_methods(self)
            self.server.start()
            LOGGER.info("Listening on OSC port: " + str(self.port))

    def on_exit(self):
        if self.port is not None:
            self.server.stop()
            del self.server


    def destroy(self):
        self.DISPLAY.destroy()


    @liblo.make_method('/pyta/text', 's')
    def text(self, path, args):
        self.ctnr.text.set_text(text_format=args[0])

########## MAIN APP ##########

for arg in sys.argv:
    if arg != 'main.py':
        p = arg

pyta = PytaText(port=p)
pyta.on_start()

mykeys = pi3d.Keyboard()
pyta.CAMERA = pi3d.Camera.instance()
pyta.CAMERA.was_moved = False # to save a tiny bit of work each loop

while pyta.DISPLAY.loop_running():
    pyta.ctnr.draw()

    k = mykeys.read()

    if k> -1:
        first = False
        if k == 27: #ESC
            mykeys.close()
            pyta.DISPLAY.stop()
            break

pyta.destroy()

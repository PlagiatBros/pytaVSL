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

from text import Text
from utils import osc_range_method

from six.moves import queue

LOGGER = pi3d.Log()

TEXTS_FONTS = ["sans", "sans", "mono", "mono"]
N_TEXTS = len(TEXTS_FONTS)

MAX_SLIDE_Z = 2000

class Slide(pi3d.Sprite):
    '''
    The slide are sprites to be textured. They might be transformed using OSC messages, and the textures they do draw too.
    There might be several of them in one container.
    '''
    def __init__(self, name, path):

        super(Slide, self).__init__(w=1.0, h=1.0)

        self.visible = False

        self.name = name
        self.path = path

        self.animations = {}

        # Scales
        self.sx = 1.0
        self.sy = 1.0
        self.sz = 1.0

        # Angle
        self.ax = 0.0
        self.ay = 0.0
        self.az = 0.0

    def set_position(self, x, y, z):
        '''
        set_position aims to set the position of the slides and to keep a trace of it
        '''
        self.position(x, y, z)

    def set_translation(self, dx, dy, dz):
        '''
        set_translation does a translation operation on the slide
        '''
        self.translate(dx, dy, dz)

    def set_scale(self, sx, sy, sz):
        '''
        set_scale sets the scale of the slides and keeps track of it
        '''
        self.sx = sx
        self.sy = sy
        self.sz = sz
        self.scale(sx, sy, sz)

    def set_angle(self, ax, ay, az):
        # set angle (absolute)
        '''
        set_angle sets the rotation of the slide and keeps track of it. It's an absolute angle, not a rotation one.
        '''
        self.ax = ax
        self.ay = ay
        self.az = az
        self.rotateToX(ax)
        self.rotateToY(ay)
        self.rotateToZ(az)

    def draw(self, *args, **kwargs):
        if self.visible:
            super(Slide, self).draw(*args, **kwargs)

    def animate(self, name, start, end, duration):
        """
        Animate one of the Slide's properties (25fps)

        Args:
            name  (str):
            start (int):
            end   (int):
            duration (float):
        """
        def threaded():

            nb_step = int(round(duration * 25.))

            a = float(end - start) / nb_step

            set_val = self.get_animate_function(name)

            for i in range(nb_step + 1):

                set_val(a * i + start)

                time.sleep(1/25.)

        if name in self.animations:
            self.animations[name].kill()

        self.animations[name] = Thread(target=threaded)
        self.animations[name].start()


    def get_animate_function(self, name):

        if function == 'position_x':
            def set_val(val):
                self.set_position(val, self.y(), self.z())
        elif function == 'position_y':
            def set_val(val):
                self.set_position(self.x(), val, self.z())
        elif function == 'position_z':
            def set_val(val):
                self.set_position(self.x(), self.y(), val)
        elif function == 'rotate_x':
            def set_val(val):
                self.set_rotate(val, self.ay, self.az)
        elif function == 'rotate_y':
            def set_val(val):
                self.set_rotate(self.ax, val, self.az)
        elif function == 'rotate_z':
            def set_val(val):
                self.set_angle(self.ax, self.ay, val)
        elif function == 'scale_x':
            def set_val(val):
                self.set_scale(val, self.sy, self.sz)
        elif function == 'scale_y':
            def set_val(val):
                self.set_scale(self.sx, val, self.sz)
        elif function == 'scale_z':
            def set_val(val):
                self.set_scale(self.sx, self.sy, val)
        elif function == 'alpha':
            def set_val(val):
                self.set_alpha(val)
        else:
            def set_val(val):
                pass

        return set_val

class PytaVSL(object):
    '''
    PytaVSL contains the screen, the camera, the light, and the slides containers. It's also an OSC server which contains the method to control all of its children.
    '''
    def __init__(self, port=56418):
        # setup OSC
        self.port = port

        # setup OpenGL
        self.DISPLAY = pi3d.Display.create(w=800, h=600, background=(0.0, 0.0, 0.0, 1.0), frames_per_second=25)
        self.shader = pi3d.Shader("uv_light")
        self.matsh = pi3d.Shader("mat_light")

        self.CAMERA = pi3d.Camera(is_3d=False)
        self.CAMERA.was_moved = False

        self.light = pi3d.Light(lightpos=(1, 1, -3))
        self.light.ambient((1, 1, 1))

        self.fileQ = queue.Queue()

        # Slides
        self.slides = {}
        self.slides_order = []

        # Texts
        self.text = {}
        for i in range(N_TEXTS):
            self.text[i] = Text(self, font=TEXTS_FONTS[i])


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

    def tex_load(self):
        """ Threaded function. mimap = False will make it faster.
        """
        while True:
            path = self.fileQ.get()
            tex = pi3d.Texture(path, blend=True, mipmap=True)
            name = path.split('/')[-1].split('.')[0]

            if name not in self.slides:
                self.slides[name] = Slide(name, path)
                self.slides_order.insert(0, name)

            xrat = self.DISPLAY.width/tex.ix
            yrat = self.DISPLAY.height/tex.iy
            if yrat < xrat:
                xrat = yrat
            wi, hi = tex.ix * xrat, tex.iy * xrat

            self.slides[name].set_scale(wi, hi, 1.0)
            self.slides[name].set_draw_details(self.shader,[tex])

            self.fileQ.task_done()

    def destroy(self):
        self.DISPLAY.destroy()


    def get_slide(self, name):

        if name in self.slides:
            return [self.slides[name]]
        elif name == -1:
            return self.slides.values()
        else:
            LOGGER.error("OSC ARGS ERROR: Slide \"%s\" not found" % name)
            return []


    # OSC Methods
    @liblo.make_method('/pyta/slide/visible', 'si')
    @liblo.make_method('/pyta/slide/visible', 'ii')
    def slide_visible_cb(self, path, args):
        slides = self.get_slide(args[0])
        for slide in slides:
	        slide.visible = bool(args[1])

    @liblo.make_method('/pyta/slide/alpha', 'sf')
    @liblo.make_method('/pyta/slide/alpha', 'if')
    def slide_alpha_cb(self, path, args):
        slides = self.get_slide(args[0])
        for slide in slides:
            slide.set_alpha(args[1])

    @liblo.make_method('/pyta/slide/position', 'sfff')
    @liblo.make_method('/pyta/slide/position_x', 'sf')
    @liblo.make_method('/pyta/slide/position_y', 'sf')
    @liblo.make_method('/pyta/slide/position_z', 'sf')
    @liblo.make_method('/pyta/slide/position', 'ifff')
    @liblo.make_method('/pyta/slide/position_x', 'if')
    @liblo.make_method('/pyta/slide/position_y', 'if')
    @liblo.make_method('/pyta/slide/position_z', 'if')
    def slide_position_cb(self, path, args):
        slides = self.get_slide(args[0])
        for slide in slides:
            if path == "/pyta/slide/position":
                slide.set_position(args[1], args[2], args[3])
            elif path == "/pyta/slide/position_x":
                slide.set_position(args[1], slide.y(), slide.z())
            elif path == "/pyta/slide/position_y":
                slide.set_position(slide.x(), args[1], slide.z())
            elif path == "/pyta/slide/position_z":
                slide.set_position(slide.x(), slide.y(), args[1])

    @liblo.make_method('/pyta/slide/translate', 'sfff')
    @liblo.make_method('/pyta/slide/translate_x', 'sf')
    @liblo.make_method('/pyta/slide/translate_y', 'sf')
    @liblo.make_method('/pyta/slide/translate_z', 'sf')
    @liblo.make_method('/pyta/slide/translate', 'ifff')
    @liblo.make_method('/pyta/slide/translate_x', 'if')
    @liblo.make_method('/pyta/slide/translate_y', 'if')
    @liblo.make_method('/pyta/slide/translate_z', 'if')
    def slide_translate_cb(self, path, args):
        slides = self.get_slide(args[0])
        for slide in slides:
            if path == "/pyta/slide/translate":
                slide.set_translation(args[1], args[2], args[3])
            elif path == "/pyta/slide/translate_x":
                slide.set_translation(args[1], 0.0, 0.0)
            elif path == "/pyta/slide/translate_y":
                slide.set_translation(0.0, args[1], 0.0)
            elif path == "/pyta/slide/translate_z":
                slide.set_translation(0.0, 0.0, args[1])

    @liblo.make_method('/pyta/slide/scale', 'sfff')
    @liblo.make_method('/pyta/slide/scale_x', 'sf')
    @liblo.make_method('/pyta/slide/scale_y', 'sf')
    @liblo.make_method('/pyta/slide/scale_z', 'sf')
    @liblo.make_method('/pyta/slide/relative_scale_xy', 'sf')
    @liblo.make_method('/pyta/slide/rsxy', 'sf')
    @liblo.make_method('/pyta/slide/scale', 'ifff')
    @liblo.make_method('/pyta/slide/scale_x', 'if')
    @liblo.make_method('/pyta/slide/scale_y', 'if')
    @liblo.make_method('/pyta/slide/scale_z', 'if')
    @liblo.make_method('/pyta/slide/relative_scale_xy', 'if')
    @liblo.make_method('/pyta/slide/rsxy', 'if')
    def slide_scale_cb(self, path, args):
        slides = self.get_slide(args[0])
        for slide in slides:
            if path == "/pyta/slide/scale":
                slide.set_scale(args[1], args[2], args[3])
            elif path == "/pyta/slide/scale_x":
                slide.set_scale(args[1], slide.sy, slide.sz)
            elif path == "/pyta/slide/scale_y":
                slide.set_scale(slide.sx, args[1], slide.sz)
            elif path == "/pyta/slide/scale_z":
                slide.set_scale(slide.sx, slide.sy, args[1])
            elif path == "/pyta/slide/relative_scale_xy" or path == "/pyta/slide/rsxy":
                slide.set_scale(slide.sx*args[1], slide.sy*args[1], slide.sz)

    @liblo.make_method('/pyta/slide/rotate', 'sfff')
    @liblo.make_method('/pyta/slide/rotate_x', 'sf')
    @liblo.make_method('/pyta/slide/rotate_y', 'sf')
    @liblo.make_method('/pyta/slide/rotate_z', 'sf')
    @liblo.make_method('/pyta/slide/rotate', 'ifff')
    @liblo.make_method('/pyta/slide/rotate_x', 'if')
    @liblo.make_method('/pyta/slide/rotate_y', 'if')
    @liblo.make_method('/pyta/slide/rotate_z', 'if')
    def slide_rotate_cb(self, path, args):
        slides = self.get_slide(args[0])
        for slide in slides:
            if path == "/pyta/slide/rotate":
                slide.set_angle(args[1], args[2], args[3])
            elif path == "/pyta/slide/rotate_x":
                slide.set_angle(args[1], slide.ay, slide.az)
            elif path == "/pyta/slide/rotate_y":
                slide.set_angle(slide.ax, args[1], slide.az)
            elif path == "/pyta/slide/rotate_z":
                slide.set_angle(slide.ax, slide.ay, args[1])

    @liblo.make_method('/pyta/slide/animate', 'ssfff')
    @liblo.make_method('/pyta/slide/animate', 'isfff')
    def slide_animate(self, path, args):
        slides = self.get_slide(args[0])
        for slide in slides:
            slide.animate(*args[1:])

    @liblo.make_method('/pyta/slide/rgb', 'sfff')
    @liblo.make_method('/pyta/slide/rgb', 'ifff')
    def slide_enlighten(self, path, args):
        '''
        Colorize the slide with rgb color.
        '''
        self.light.ambient((args[1], args[2], args[3]))
        slides = self.get_slide(args[0])
        for slide in slides:
            slide.set_light(self.light,0)


    @liblo.make_method('/pyta/slide/load_file', 's')
    def slide_load_file_cb(self, path, args):
        files = glob.glob(args[0])
        if len(files):
            for file in files:
                self.fileQ.put(file)
        else:
            LOGGER.info("ERROR: file \"%s\" not found" % file)

    @liblo.make_method('/pyta/slide/slide_info', 'si')
    @liblo.make_method('/pyta/slide/slide_info', 'ii')
    def slide_info_cb(self, path, args, types, src):
        slides = self.get_slide(args[0])
        for slide in slides:
            dest = src.get_url().split(":")[0] + ':' + src.get_url().split(":")[1] + ':' + str(args[1])
            prefix = '/pyta/slide_info/'
            liblo.send(dest, prefix + 'slidenumber', args[0])
            liblo.send(dest, prefix + 'position', slide.x(), slide.y(), slide.z())
            liblo.send(dest, prefix + 'scale', slide.sx, slide.sy, slide.sz)
            liblo.send(dest, prefix + 'angle', slide.ax, slide.ay, slide.az)
            liblo.send(dest, prefix + 'visible', slide.visible)
            liblo.send(dest, prefix + 'alpha', slide.alpha())

    @liblo.make_method('/pyta/slide/save_state', 's')
    @liblo.make_method('/pyta/slide/save_state', 'i')
    def slide_save_state(self, path, args):
        slides = self.get_slide(args[0])
        for slide in slides:
            prefix = '/pyta/slide/'
            filename = 's' + str(slide.name + '.state')
            LOGGER.info('Write in progress in ' + filename)

            statef = open(filename, 'w')
            statef.write("slide " + str(args[0]) + "\n")
            statef.write("file " + str(slide.path) + "\n")
            statef.write("position " + str(slide.x()) + " " + str(slide.y()) + " " + str(slide.z()) + "\n")
            statef.write("scale " + str(slide.sx) + " " + str(slide.sy) + " " + str(slide.sy) + "\n")
            statef.write("angle " + str(slide.ax) + " " + str(slide.ay) + " " + str(slide.az) + "\n")
            statef.write("alpha " + str(slide.alpha()) + "\n")
            statef.close()

    @liblo.make_method('/pyta/slide/load_state', 's')
    def slide_load_state(self, path, args):
        statef = open(args[0], 'r')
        param = statef.read()
        # sn = int(param.split("\n")[0].split(" ")[1])
        # fn = param.split("\n")[1].split(" ")[1]
        sn = param.split("\n")[0].split(" ")[1]
        pos = param.split("\n")[2].split(" ")[1:]
        sc = param.split("\n")[3].split(" ")[1:]
        ag = param.split("\n")[4].split(" ")[1:]
        al = float(param.split("\n")[5].split(" ")[1])

        slides = self.get_slide(sn)
        for slide in slides:
            # self.slide_load_file_cb('/hop', (fn))
            slide.position(float(pos[0]), float(pos[1]), float(pos[2]))
            slide.set_scale(float(sc[0]), float(sc[1]), float(sc[2]))
            slide.set_angle(float(ag[0]), float(ag[1]), float(ag[2]))
            slide.set_alpha(al)


    @liblo.make_method('/pyta/text', 'is')
    @osc_range_method(N_TEXTS)
    def set_text_string(self, path, args):
        self.text[args[0]].set_text(args[1])

    @liblo.make_method('/pyta/text/size', 'if')
    @osc_range_method(N_TEXTS)
    def set_text_size(self, path, args):
        self.text[args[0]].set_size(args[1])

    @liblo.make_method('/pyta/text/visible', 'ii')
    @osc_range_method(N_TEXTS)
    def set_text_visible(self, path, args):
        self.text[args[0]].set_visible(args[1])

    @liblo.make_method('/pyta/text/strobe', 'ii')
    @osc_range_method(N_TEXTS)
    def set_text_strobe(self, path, args):
        self.text[args[0]].set_strobe(args[1])


    @liblo.make_method('/pyta/text/position', 'iii')
    @osc_range_method(N_TEXTS)
    def set_text_position(self, path, args):
        self.text[args[0]].set_position(args[1], args[2])

    @liblo.make_method('/pyta/text/rotate', 'ifff')
    @liblo.make_method('/pyta/text/rotate_x', 'if')
    @liblo.make_method('/pyta/text/rotate_y', 'if')
    @liblo.make_method('/pyta/text/rotate_z', 'if')
    @osc_range_method(N_TEXTS)
    def set_text_rotate_x(self, path, args):
        if path == '/pyta/text/rotate':
            self.text[args[0]].set_rotation(args[1], args[2], args[3])
        elif path == '/pyta/text/rotate_x':
            self.text[args[0]].set_rotation(args[1], None, None)
        elif path == '/pyta/text/rotate_y':
            self.text[args[0]].set_rotation(None, args[1], None)
        elif path == '/pyta/text/rotate_z':
            self.text[args[0]].set_rotation(None, None, args[1])

    @liblo.make_method('/pyta/text/align', 'iss')
    @osc_range_method(N_TEXTS)
    def set_text_align(self, path, args):
        self.text[args[0]].set_align(args[1], args[2])

    @liblo.make_method('/pyta/text/rgb', 'iiiii')
    @liblo.make_method('/pyta/text/rgb', 'iiii')
    @osc_range_method(N_TEXTS)
    def set_text_color(self, path, args):
        args[1] /= 255.
        args[2] /= 255.
        args[3] /= 255.
        self.text[args[0]].set_color(args[1:])
        if len(args) == 5:
            self.text[args[0]].set_alpha(args[4] / 255.)

    @liblo.make_method('/pyta/text/rgb/strobe', 'ii')
    @osc_range_method(N_TEXTS)
    def set_text_color_strobe(self, path, args):
        self.text[args[0]].set_color_strobe(args[1])

    @liblo.make_method('/pyta/text/alpha', 'if')
    @osc_range_method(N_TEXTS)
    def set_text_alpha(self, path, args):
        self.text[args[0]].set_alpha(args[1])

    @liblo.make_method('/pyta/text/animate', 'isfff')
    @osc_range_method(N_TEXTS)
    def text_animate(self, path, args):
        self.text[args[0]].animate(*args[1:])

########## MAIN APP ##########

for arg in sys.argv:
    if arg != 'main.py':
        p = arg

pyta = PytaVSL(port=p)
pyta.on_start()

t = threading.Thread(target=pyta.tex_load)
t.daemon = True
t.start()

pyta.fileQ.join()

mykeys = pi3d.Keyboard()

while pyta.DISPLAY.loop_running():

    for name in pyta.slides_order:
        pyta.slides[name].draw()

    for i in pyta.text:
        pyta.text[i].draw()

    k = mykeys.read()

    if k == 27: #ESC
        mykeys.close()
        pyta.DISPLAY.stop()
        break

pyta.destroy()

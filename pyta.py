# encoding: utf-8

"""
This is the main file of pytaVSL.
It aims to provide a VJing and lights-projector-virtualisation tool.
Images are loaded as textures, which then are mapped onto slides.
This file was deeply instpired by Slideshow.py demo file of pi3d.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import time, glob
import pi3d
import liblo
import random
import sys
from signal import signal, SIGINT, SIGTERM
from six.moves import queue

from text import Text
from slide import Slide
from utils import osc_range_method
from utils import KillableThread as Thread

LOGGER = pi3d.Log(__name__)

TEXTS_FONTS = ["sans", "sans", "mono", "mono"]
N_TEXTS = len(TEXTS_FONTS)

SLIDE_BASE_Z = 100

class PytaVSL(object):
    '''
    PytaVSL contains the screen, the camera, the light, and the slides containers. It's also an OSC server which contains the method to control all of its children.
    '''
    def __init__(self, port=56418, path=None, load_cb=None):
        # setup OSC
        self.port = int(port)

        # setup OpenGL
        self.DISPLAY = pi3d.Display.create(w=800, h=600, background=(0.0, 0.0, 0.0, 1.0), frames_per_second=25)
        self.CAMERA = pi3d.Camera(is_3d=False)
        self.CAMERA.was_moved = False

        self.shader = pi3d.Shader("uv_light")

        self.light = pi3d.Light(lightpos=(0, 0, -1))
        self.light.ambient((0, 0, 0))

        self.fileQ = queue.Queue()
        self.path = path
        self.load_cb = load_cb

        # Slides
        self.slides = {}
        self.sorted_slides = []

        # Texts
        self.text = {}
        for i in range(N_TEXTS):
            self.text[i] = Text(self, font=TEXTS_FONTS[i])


        # sys
        self.keyboard = pi3d.Keyboard()
        signal(SIGINT, self.stop)
        signal(SIGTERM, self.stop)

    def start(self):

        t = Thread(target=self.tex_load)
        t.daemon = True
        t.start()

        if self.path:
            self.slide_load_file_cb(None, [self.path])

        self.server = liblo.ServerThread(self.port)
        self.server.register_methods(self)
        self.server.start()
        LOGGER.info("Listening on OSC port: " + str(self.port))

        while self.DISPLAY.loop_running():

            for slide in self.sorted_slides:
                slide.draw()

            for i in self.text:
                self.text[i].draw()

            if self.keyboard.read() == 27: #ESC
                self.stop()
                break

    def stop(self, *args):
        self.keyboard.close()
        self.DISPLAY.stop()
        self.DISPLAY.destroy()

    def tex_load(self):
        """ Threaded function. mimap = False will make it faster.
        """
        while True:

            path = self.fileQ.get()
            tex = pi3d.Texture(path, blend=True, mipmap=True)
            name = path.split('/')[-1].split('.')[0]

            if name not in self.slides:
                self.slides[name] = Slide(name, path, self.light, SLIDE_BASE_Z)
                self.slides[name].set_position(self.slides[name].x(), self.slides[name].y(), SLIDE_BASE_Z)

            xrat = self.DISPLAY.width/tex.ix
            yrat = self.DISPLAY.height/tex.iy
            if yrat < xrat:
                xrat = yrat
            wi, hi = tex.ix * xrat, tex.iy * xrat

            self.slides[name].init_w = wi
            self.slides[name].init_h = hi
            self.slides[name].set_scale(wi, hi, 1.0)
            self.slides[name].set_draw_details(self.shader,[tex])

            self.fileQ.task_done()

            if self.fileQ.empty():
                self.sort_slides()
                LOGGER.info("Total slides in memory: %i" % len(self.slides.values()))
                if self.load_cb is not None:
                    self.load_cb(self)
                    self.load_cb = None


    def sort_slides(self):
        self.sorted_slides = sorted(self.slides.values(), key=lambda slide: slide.z(), reverse=True)

    def get_slide(self, name):

        slides = []

        if type(name) is str  and ' ' in name:

            for n in name.split(' '):
                slides += self.get_slide(n)

        else:
            if name in self.slides:
                slides += [self.slides[name]]
            elif name == -1:
                slides += self.slides.values()
            else:
                LOGGER.error("OSC ARGS ERROR: Slide \"%s\" not found" % name)

        return slides

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
                slide.set_position(args[1], args[2], args[3] + SLIDE_BASE_Z)
            elif path == "/pyta/slide/position_x":
                slide.set_position(args[1], slide.y(), slide.z())
            elif path == "/pyta/slide/position_y":
                slide.set_position(slide.x(), args[1], slide.z())
            elif path == "/pyta/slide/position_z":
                z = slide.z()
                nz = args[1] + SLIDE_BASE_Z
                if z != nz:
                    slide.set_position(slide.x(), slide.y(), nz)
                    self.sort_slides()

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
                self.sort_slides()

    @liblo.make_method('/pyta/slide/scale', 'sfff')
    @liblo.make_method('/pyta/slide/scale_x', 'sf')
    @liblo.make_method('/pyta/slide/scale_y', 'sf')
    @liblo.make_method('/pyta/slide/scale_z', 'sf')
    @liblo.make_method('/pyta/slide/relative_scale_xy', 'sf')
    @liblo.make_method('/pyta/slide/rsxy', 'sf')
    @liblo.make_method('/pyta/slide/zoom', 'sf')
    @liblo.make_method('/pyta/slide/scale', 'ifff')
    @liblo.make_method('/pyta/slide/scale_x', 'if')
    @liblo.make_method('/pyta/slide/scale_y', 'if')
    @liblo.make_method('/pyta/slide/scale_z', 'if')
    @liblo.make_method('/pyta/slide/relative_scale_xy', 'if')
    @liblo.make_method('/pyta/slide/rsxy', 'if')
    @liblo.make_method('/pyta/slide/zoom', 'if')
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
            elif path == "/pyta/slide/relative_scale_xy" or path == "/pyta/slide/rsxy" or path == "/pyta/slide/zoom":
                slide.set_zoom(args[1])


    @liblo.make_method('/pyta/slide/reset', 'i')
    @liblo.make_method('/pyta/slide/reset', 's')
    @liblo.make_method('/pyta/slide/scale/reset', 's')
    def slide_reset_scale_cb(self, path, args):
        slides = self.get_slide(args[0])
        for slide in slides:
            slide.reset()

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
    @liblo.make_method('/pyta/slide/animate', 'sssff')
    @liblo.make_method('/pyta/slide/animate', 'issff')
    @liblo.make_method('/pyta/slide/animate', 'ssfsf')
    @liblo.make_method('/pyta/slide/animate', 'isfsf')
    @liblo.make_method('/pyta/slide/animate', 'ssssf')
    @liblo.make_method('/pyta/slide/animate', 'isssf')
    def slide_animate(self, path, args):
        slides = self.get_slide(args[0])
        for slide in slides:
            slide.animate(*args[1:])

    @liblo.make_method('/pyta/slide/animate/stop', 'i')
    @liblo.make_method('/pyta/slide/animate/stop', 's')
    @liblo.make_method('/pyta/slide/animate/stop', 'is')
    @liblo.make_method('/pyta/slide/animate/stop', 'ss')
    @osc_range_method(N_TEXTS)
    def slide_stop_animate(self, path, args):
        slides = self.get_slide(args[0])
        for slide in slides:
            slide.stop_animate(args[1] if len(args) > 1 else None)


    @liblo.make_method('/pyta/slide/rgb', 'sfff')
    @liblo.make_method('/pyta/slide/rgb', 'ifff')
    def slide_enlighten(self, path, args):
        '''
        Colorize the slide with rgb color.
        '''
        slides = self.get_slide(args[0])
        for slide in slides:
            slide.set_color((args[1], args[2], args[3]))

    @liblo.make_method('/pyta/slide/strobe', 'ii')
    @liblo.make_method('/pyta/slide/strobe', 'iiff')
    @liblo.make_method('/pyta/slide/strobe', 'si')
    @liblo.make_method('/pyta/slide/strobe', 'siff')
    def set_slide_strobe(self, path, args):
        slides = self.get_slide(args[0])
        for slide in slides:
            slide.set_strobe(*args[1:])

    @liblo.make_method('/pyta/slide/strobe/period', 'if')
    @liblo.make_method('/pyta/slide/strobe/period', 'sf')
    def set_slide_strobe_len(self, path, args):
        slides = self.get_slide(args[0])
        for slide in slides:
            slide.set_strobe(None, args[1], None)

    @liblo.make_method('/pyta/slide/strobe/ratio', 'if')
    @liblo.make_method('/pyta/slide/strobe/ratio', 'sf')
    def set_slide_strobe_per(self, path, args):
        slides = self.get_slide(args[0])
        for slide in slides:
            slide.set_strobe(None, None, args[1])


    @liblo.make_method('/pyta/slide/clone', 'ss')
    def slide_clone(self, path, args):
        '''
        Create a slide clone
        '''
        slides = self.get_slide(args[0])
        if len(slides) > 1:
            LOGGER.error('ERROR: cannot clone more than one slide at a time')
        elif len(slides) == 1:
            if args[1] not in self.slides:
                self.slides[args[1]] = slides[0].clone(args[1])
                self.sort_slides()

    @liblo.make_method('/pyta/slide/load_file', 's')
    def slide_load_file_cb(self, path, args):
        files = glob.glob(args[0])
        if len(files):
            for file in files:
                self.fileQ.put(file)
        else:
            LOGGER.info("ERROR: file \"%s\" not found" % args[0])

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

    @liblo.make_method('/pyta/text/reset', 'i')
    @osc_range_method(N_TEXTS)
    def set_text_reset(self, path, args):
        self.text[args[0]].reset()

    @liblo.make_method('/pyta/text/size', 'if')
    @osc_range_method(N_TEXTS)
    def set_text_size(self, path, args):
        self.text[args[0]].set_size(args[1])

    @liblo.make_method('/pyta/text/visible', 'ii')
    @osc_range_method(N_TEXTS)
    def set_text_visible(self, path, args):
        self.text[args[0]].set_visible(args[1])

    @liblo.make_method('/pyta/text/strobe', 'ii')
    @liblo.make_method('/pyta/text/strobe', 'iiff')
    @osc_range_method(N_TEXTS)
    def set_text_strobe(self, path, args):
        self.text[args[0]].set_strobe(*args[1:])

    @liblo.make_method('/pyta/text/strobe/period', 'if')
    @osc_range_method(N_TEXTS)
    def set_text_strobe_len(self, path, args):
        self.text[args[0]].set_strobe(None, args[1], None)

    @liblo.make_method('/pyta/text/strobe/ratio', 'if')
    @osc_range_method(N_TEXTS)
    def set_text_strobe_per(self, path, args):
        self.text[args[0]].set_strobe(None, None, args[1])

    @liblo.make_method('/pyta/text/position', 'iii')
    @liblo.make_method('/pyta/text/position_x', 'ii')
    @liblo.make_method('/pyta/text/position_y', 'ii')
    @osc_range_method(N_TEXTS)
    def set_text_position(self, path, args):
        if path == '/pyta/text/position':
            self.text[args[0]].set_position(args[1], args[2])
        elif path == '/pyta/text/position_x':
            self.text[args[0]].set_position(args[1], None)
        elif path == '/pyta/text/position_y':
            self.text[args[0]].set_position(None, args[1])

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
    @liblo.make_method('/pyta/text/animate', 'issff')
    @liblo.make_method('/pyta/text/animate', 'isfsf')
    @liblo.make_method('/pyta/text/animate', 'isssf')
    @osc_range_method(N_TEXTS)
    def text_animate(self, path, args):
        self.text[args[0]].animate(*args[1:])

    @liblo.make_method('/pyta/text/animate/stop', 'is')
    @liblo.make_method('/pyta/text/animate/stop', 's')
    @osc_range_method(N_TEXTS)
    def text_stop_animate(self, path, args):
        self.text[args[0]].stop_animate(args[1] if len(args) > 1 else None)

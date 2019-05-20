# encoding: utf-8

"""
This is the main file of pytaVSL.
It aims to provide a VJing and lights-projector-virtualisation tool.
Images are loaded as textures, which then are mapped onto slides.
This file was deeply instpired by Slideshow.py demo file of pi3d.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import pi3d
import sys
from signal import signal, SIGINT, SIGTERM
from six.moves import queue

from PIL.GifImagePlugin import GifImageFile

from text import Text
from postprocess import PostProcess
from slide import Slide
from utils import KillableThread as Thread
from memory import gpu_monitor
from osc import OscServer
from config import *

LOGGER = pi3d.Log(name=None, level='DEBUG' if '--debug' in sys.argv else 'CRITICAL' if '--quiet' in sys.argv else 'WARNING', file="/dev/null" if '--quiet' in sys.argv else None)

class PytaVSL(OscServer):
    '''
    PytaVSL contains the screen, the , the light, and the slides containers. It's also an OSC server which contains the method to control all of its children.
    '''
    def __init__(self, port=56418, path=None, load_cb=None, fps=25, depth=24):

        super(PytaVSL, self).__init__(port)

        # setup OpenGL
        self.DISPLAY = pi3d.Display.create(w=800, h=600, background=(0.0, 0.0, 0.0, 1.0), frames_per_second=fps, depth=depth)
        self.CAMERA = pi3d.Camera(is_3d=False)
        self.CAMERA.was_moved = False

        self.shader = pi3d.Shader("uv_light")

        self.light = pi3d.Light(lightpos=(0, 0, -1))
        self.light.ambient((0, 0, 0))

        self.post_process = PostProcess()

        self.fileQ = queue.Queue()
        self.path = path
        self.load_cb = load_cb

        # Slides
        self.slides = {}
        self.sorted_slides = []
        self.locked_slides = []

        # Texts
        self.text = {}
        for i in range(N_TEXTS):
            self.text[i] = Text(self, font=TEXTS_FONTS[i])

        # Memory
        self.monitor = gpu_monitor
        gpu_monitor.flush = self.flush

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


        super(PytaVSL, self).start()


        while self.DISPLAY.loop_running():

            post_processing = self.post_process.visible

            if post_processing:
                self.post_process.capture_start()

            for slide in self.sorted_slides:
                slide.draw()

            for i in self.text:
                self.text[i].draw()

            if post_processing:
                self.post_process.capture_end()

            self.post_process.draw()

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
            name = path.split('/')[-1].split('.')[0]

            self.init_slide(name, path)

            self.fileQ.task_done()

            if self.fileQ.empty():
                self.sort_slides()
                LOGGER.info("Total slides in memory: %i" % len(self.slides.values()))
                if self.load_cb is not None:
                    self.load_cb(self)
                return


    def init_slide(self, name, path):

        tex = pi3d.Texture(path, blend=True, mipmap=True)

        self.slides[name] = Slide(name, self.light, SLIDE_BASE_Z)
        self.slides[name].set_position(self.slides[name].x(), self.slides[name].y(), SLIDE_BASE_Z)

        xrat = self.DISPLAY.width/tex.ix
        yrat = self.DISPLAY.height/tex.iy
        if yrat < xrat:
            xrat = yrat
        wi, hi = tex.ix * xrat, tex.iy * xrat

        self.slides[name].init_w = wi
        self.slides[name].init_h = hi
        self.slides[name].set_scale(wi, hi, 1.0)
        self.slides[name].set_shader(self.shader)

        if '.gif' in path:
            gif = GifImageFile(path)
            if gif.is_animated:
                self.slides[name].set_frames(gif)
                return

        self.slides[name].set_textures([tex])


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
                for locked in self.locked_slides:
                    if locked in slides:
                        slides.remove(locked)
            else:
                LOGGER.error("OSC ARGS ERROR: Slide \"%s\" not found" % name)

        return slides


    def flush(self, added_slide=None):
        for slide in self.sorted_slides:
            if not slide.visible and slide.loaded and slide not in self.locked_slides:
                slide.unload()
        if self.monitor.full():
            for slide in self.sorted_slides:
                if slide.visible and slide is not added_slide and slide not in self.locked_slides:
                    slide.set_visible(False)
                    slide.unload()
                    LOGGER.warning("GPU memory full: forced unload of slide %s" % slide.name)
                    if not self.monitor.full():
                        return

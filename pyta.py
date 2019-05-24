# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import pi3d
from pi3d.constants import DISPLAY_CONFIG_FULLSCREEN, DISPLAY_CONFIG_DEFAULT

import sys
import glob
import fnmatch
import numpy
import random
from signal import signal, SIGINT, SIGTERM
from six.moves import queue

from text import Text
from postprocess import PostProcess
from slide import Slide
from utils import KillableThread as Thread
from memory import gpu_monitor
from osc import OscServer
from config import *

LOGGER = pi3d.Log(name=None, level='DEBUG' if '--debug' in sys.argv else 'CRITICAL' if '--quiet' in sys.argv else 'WARNING', file="/dev/null" if '--quiet' in sys.argv else None)

class PytaVSL(OscServer):
    """
    Main object, contains the screen and the slides.
    It's also an OSC server which contains the method to control all of its children.
    """

    def __init__(self, port=56418, path=None, load_cb=None, fps=25, depth=24, fullscreen=False):

        super(PytaVSL, self).__init__(port)

        # setup OpenGL
        self.DISPLAY = pi3d.Display.create(w=800, h=600, background=(0.0, 0.0, 0.0, 1.0), frames_per_second=fps, depth=depth, display_config=DISPLAY_CONFIG_FULLSCREEN if fullscreen else DISPLAY_CONFIG_DEFAULT)
        self.CAMERA = pi3d.Camera(is_3d=False, eye=(0, 0, -100))
        self.CAMERA.was_moved = False

        self.shader = pi3d.Shader("uv_flat")

        self.DISPLAY.loop_running()
        self.post_process = PostProcess()

        # Slides
        self.slides = {}
        self.sorted_slides = []
        self.locked_slides = []

        # Texts
        self.text = {}
        self.text['debug'] = Text(shader=self.shader, font=TEXTS_FONTS[2], z=-99)
        for i in range(N_TEXTS):
            self.text[i] = Text(shader=self.shader, font=TEXTS_FONTS[i], z=i-98)
        self.sorted_texts = sorted(self.text.values(), key=lambda text: text.z, reverse=True)


        # Memory
        self.monitor = gpu_monitor
        gpu_monitor.flush = self.flush

        # Signal
        signal(SIGINT, self.stop)
        signal(SIGTERM, self.stop)

        # Init
        self.fileQ = queue.Queue()
        self.path = path
        self.load_cb = load_cb

    def start(self):
        """
        - load textures
        - run the main loop
             - receive osc messages
             - draw slides, skip grouped slides (drawn by their parents)
        """

        if self.path:
            self.load_textures(self.path, self.load_cb)

        while self.DISPLAY.loop_running():

            # process osc messages
            while self.server.recv(0):
                pass

            post_processing = self.post_process.visible

            if post_processing:
                self.post_process.capture_start()

            for slide in self.sorted_slides:
                if not slide.grouped:
                    slide.draw()

            for text in self.sorted_texts:
                text.draw()

            if post_processing:
                self.post_process.capture_end()

            self.post_process.draw()

    def stop(self, *args):
        """
        Stop main loop and osc server
        """
        self.DISPLAY.stop()
        self.DISPLAY.destroy()
        super(PytaVSL, self).stop()

    def load_textures(self, path, callback=None):
        """
        Load textures (threaded)
        """

        files = glob.glob(path)
        if len(files) == 0:
            LOGGER.error("file \"%s\" not found" % path)

        def threaded():

            size = len(files)

            self.text['debug'].reset()
            self.text['debug'].set_visible(True)
            self.text['debug'].set_size(0.025)
            self.text['debug'].set_align('top', 'right')
            self.text['debug'].set_text('0/' + str(size))

            for i in range(size):
                path = files[i]
                name = path.split('/')[-1].split('.')[0]
                self.slides[name] = Slide(name, path, self.shader)
                self.slides[name].set_position(self.slides[name].x(), self.slides[name].y(), i / 1000.)
                self.text['debug'].set_text(str(i + 1) + '/' + str(size))

            self.text['debug'].reset()

            self.sort_slides()

            LOGGER.info("Total slides in memory: %i" % len(self.slides.values()))

            if callback is not None:

                callback(self)

        t = Thread(target=threaded)
        t.daemon = True
        t.start()

    def sort_slides(self):
        """
        Sort slides in drawing order (by z-index)
        """
        self.sorted_slides = sorted(self.slides.values(), key=lambda slide: slide.z(), reverse=True)

    def get_slide(self, name):
        """
        Get a list of slides

        Args:
            name (str): - slide name
                        - list of names separated by spaces
                        - glob pattern
                 (int): - -1 (equivalent to "*"), locked slides excluded
        """

        slides = []

        if type(name) is str:

            if ' ' in name:

                for n in name.split(' '):
                    if n:
                        slides += self.get_slide(n)

            if '*' in name:
                if name == '*':
                    return self.get_slide(-1)
                for n in fnmatch.filter(self.slides.keys(), name):
                    slides += self.get_slide(n)

            elif name  == '?':
                slides += [random.choice(self.sorted_slides)]

            elif name in self.slides:
                slides += [self.slides[name]]

        elif name == -1:
            slides += self.slides.values()
            for locked in self.locked_slides:
                if locked in slides:
                    slides.remove(locked)

        if not slides:
            LOGGER.error("slide \"%s\" not found" % name)

        return slides


    def create_group(self, name, slides):
        """
        Create slide group
        """
        if name in self.slides:
            LOGGER.error("could not create group \"%s\" (name not available)" % name)
            return

        group = Slide(name, pi3d.Texture(numpy.array([[[0,0,0]]])), self.shader, self.DISPLAY.width, self.DISPLAY.height)
        for child in self.get_slide(slides):
            if not child.grouped:
                child.grouped = name
                group.add_child(child)
            else:
                LOGGER.error("could add \"%s\" to group \"%s\" (slide already in group \"%s\")" % (child.name, name, child.grouped))
        self.slides[name] = group
        self.sort_slides()

    def remove_group(self, name):
        """
        Remove slide group
        """
        for group in self.get_slide(name):
            if group.children:
                for child in group.children:
                    child.grouped = False
                group.children = []
                group.set_visible(False)
                group.unload()
                del self.slides[group.name]
        self.sort_slides()

    def flush(self, added_slide=None):
        """
        Unload hidden slides from gpu.
        If necessary, unload visible slides too.
        """

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

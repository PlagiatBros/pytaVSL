# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import pi3d
from pi3d.constants import DISPLAY_CONFIG_FULLSCREEN, DISPLAY_CONFIG_DEFAULT

from threading import Thread
from signal import signal, SIGINT, SIGTERM

from text import Text
from postprocess import PostProcess
from slide import Slide
from utils import unicode, empty_texture
from memory import MemoryMonitor
from osc import OscServer, osc_method
from config import *
from shaders import init_shaders

import logging
LOGGER = logging.getLogger(__name__)

class PytaVSL(OscServer):
    """
    Main object, contains the screen and the slides.
    It's also an OSC server which contains the method to control all of its children.
    """

    def __init__(self, name, port, files=[], fps=25, fullscreen=False, max_gpu_memory=64):

        super(PytaVSL, self).__init__(name, port)

        # setup OpenGL
        self.DISPLAY = pi3d.Display.create(window_title="pytaVSL", w=800, h=600, background=(0.0, 0.0, 0.0, 1.0), frames_per_second=fps, depth=24, display_config=DISPLAY_CONFIG_FULLSCREEN if fullscreen else DISPLAY_CONFIG_DEFAULT)
        self.CAMERA = pi3d.Camera(is_3d=False, eye=(0, 0, -100))
        self.CAMERA.was_moved = False

        init_shaders()

        self.DISPLAY.loop_running()
        self.post_process = PostProcess()

        # Slides
        self.slides = {}

        # Texts
        self.texts = {}
        self.texts['debug'] = Text(self, 'debug', font=TEXTS_FONTS[2])
        self.texts['debug'].set_position_z(-99)
        for i in range(N_TEXTS):
            self.texts[str(i)] = Text(self, str(i), font=TEXTS_FONTS[i])
            self.texts[str(i)].set_position_z(i-99)

        # Z-sorted slides
        self.sorted_slides = []
        self.slides_need_sorting = True

        # Memory
        self.monitor = MemoryMonitor(max_gpu_memory, self.flush)

        # Signal
        signal(SIGINT, self.stop)
        signal(SIGTERM, self.stop)

        # Init
        self.files = files if files else []

    def start(self):
        """
        - load textures
        - run the main loop
             - receive osc messages
             - draw slides, skip grouped slides (drawn by their parents)
        """

        if self.files:
            self.load_textures(self.files)

        while self.DISPLAY.loop_running():

            # process osc messages
            while self.server.recv(0):
                pass

            post_processing = self.post_process.visible

            if post_processing:
                self.post_process.capture_start()

            if self.slides_need_sorting:
                self.sorted_slides = sorted(list(self.slides.values()) + list(self.texts.values()), key=lambda slide: slide.z(), reverse=True)
                self.slides_need_sorting = False

            for slide in self.sorted_slides:
                if not slide.parent_slide:
                    slide.draw()

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

    def load_textures(self, files, callback=None):
        """
        Load textures (threaded)
        """

        if len(files) == 0:
            LOGGER.error("file \"%s\" not found" % path)

        def threaded():

            size = len(files)

            self.texts['debug'].reset()
            self.texts['debug'].set_visible(1)
            self.texts['debug'].set_size(0.025)
            self.texts['debug'].set_align('top', 'right')
            self.texts['debug'].set_text('0/' + str(size))

            for i in range(size):
                try:
                    path = files[i]
                    name = path.split('/')[-1].split('.')[0].lower()
                    slide = Slide(parent=self, name=name, texture=path)
                    slide.set_position_z(i / 1000.)
                    self.add_slide(slide)
                except:
                    LOGGER.error('could not load file %s' %path)
                self.texts['debug'].set_text(str(i + 1) + '/' + str(size))

            self.texts['debug'].set_visible(0)

            LOGGER.info("total slides in memory: %i" % len(self.slides.values()))

            if callback is not None:

                callback(self)

        t = Thread(target=threaded)
        t.daemon = True
        t.start()

    def sort_slides(self):
        """
        Sort slides in drawing order (by z-index)
        """
        self.slides_need_sorting = True

    def flush(self, added_slide=None):
        """
        Unload hidden slides from gpu.
        If necessary, unload visible slides too.
        """

        for slide in self.sorted_slides:
            if not slide.visible and slide.loaded and slide:
                slide.unload()

        if self.monitor.full():
            for slide in self.sorted_slides:
                if slide.visible and slide is not added_slide and slide:
                    slide.set_visible(0)
                    slide.unload()
                    LOGGER.warning("GPU memory full: forced unload of slide %s" % slide.name)
                    if not self.monitor.full():
                        return


    def add_slide(self, slide):
        self.slides[slide.name] = slide
        self.sort_slides()

    def remove_slide(self, slide):
        if slide.children:
            for child in slide.children:
                child.quit_group()
        slide.quit_group()
        slide.set_visible(0)
        slide.unload()
        del self.slides[slide.name]
        self.sort_slides()

    @osc_method('group')
    def create_group(self, slides, group_name):
        """
        Create slide group
        """
        name = group_name.lower()
        slides = slides.lower()

        if name in self.slides:
            if self.slides[name].is_group:
                self.remove_group(name)
            else:
                LOGGER.error("could not create group \"%s\" (name taken by a non-group slide)" % name)
                return

        group = Slide(parent=self, name=name, texture=empty_texture(), width=self.DISPLAY.width, height=self.DISPLAY.height)
        group.is_group = True

        for child in self.get_children(self.slides, slides):

            if child.parent_slide:
                LOGGER.debug("slide %s moved from group %s to %s" % (child.name, child.parent_slide.name, name))
                child.quit_group()

            child.parent_slide = group
            group.add_child(child)

        self.add_slide(group)

    @osc_method('ungroup')
    def remove_group(self, group_name):
        """
        Remove slide group
        """
        name = group_name.lower()
        for group in self.get_children(self.slides, name):
            if group.is_group:
                self.remove_slide(group)

    @osc_method('clone')
    def create_clone(self, slide, clone_name):
        """
        Create slide clone
        """
        clone_name = slide.lower()
        target_name = target_name.lower()

        if clone_name in self.slides:
            if self.slides[clone_name].is_clone:
                self.remove_slide(self.slides[clone_name])
            else:
                LOGGER.error("could not create clone \"%s\" (name taken by a non-clone slide)" % clone_name)
                return

        target = self.get_children(self.slides, target_name)
        if len(target) > 1:
            LOGGER.error('cannot clone more than 1 slide at a time (%s matches %i slides)' % (target_name, len(target)))
            return

        if not target:
            LOGGER.error('no slide to clone (%s)' % (target_name))
            return

        target = target[0]

        clone = Slide(parent=self, name=clone_name, texture=pi3d.Texture(target.buf[0].textures[0].image), width=target.width, height=target.height)
        clone.set_position_z(target.pos_z - 0.001)
        clone.gif = target.gif
        clone.is_clone = True

        self.add_slide(clone)

    @osc_method('unclone')
    def remove_clone(self, clone_name):
        """
        Remove slide clone
        """
        clone_name = clone_name.lower()
        for clone in self.get_children(self.slides, clone_name):
            if clone.is_clone:
                self.remove_slide(clone)
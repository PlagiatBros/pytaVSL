# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import pi3d
from pi3d.constants import opengles, DISPLAY_CONFIG_FULLSCREEN, DISPLAY_CONFIG_DEFAULT, GL_CULL_FACE
import ctypes

import glob
from threading import Thread
from signal import signal, SIGINT, SIGTERM
import traceback
from time import time, sleep

import toml
tomlencoder = toml.TomlEncoder()
def dump_float(f):
    return "%g" % f
tomlencoder.dump_funcs[float] = dump_float

from shaders import init_shader_cache
from text import Text
from postprocess import PostProcess
from slide import Slide
from utils import unicode, empty_texture
from memory import MemoryMonitor
from osc import OscServer, osc_method
from config import *

import logging
LOGGER = logging.getLogger(__name__)

class PytaVSL(OscServer):
    """
    Main object, contains the screen and the slides.
    It's also an OSC server which contains the method to control all of its children.
    """

    def __init__(self, name, port, fps=25, fullscreen=False, max_gpu_memory=64, width=800, height=600, window_title='', show_fps=False):

        super(PytaVSL, self).__init__(name, port)

        # setup OpenGL
        self.height = height
        self.DISPLAY = pi3d.Display.create(window_title=window_title, w=width, h=height, background=(0.0, 0.0, 0.0, 1.0), frames_per_second=0, depth=24, display_config=DISPLAY_CONFIG_FULLSCREEN if fullscreen else DISPLAY_CONFIG_DEFAULT, far=100000)
        self.CAMERA = pi3d.Camera(is_3d=False, eye=(0, 0, -height))
        self.CAMERA3D = pi3d.Camera(is_3d=True, eye=(0, 0, -height), scale=0.8465)
        self.CAMERA.was_moved = False
        self.CAMERA3D.was_moved = False

        # enable texture backside
        opengles.glDisable(GL_CULL_FACE)

        # wireframe size
        opengles.glLineWidth(ctypes.c_float(1.0))

        self.time = time()

        init_shader_cache()

        self.post_process = PostProcess(self)

        # Slides
        self.slides = {}

        # Texts
        self.texts = {}

        self.debug_text = Text(self, 'debug', font=FONTS["mono"], init_z=-100)
        self.debug_text.set_size(0.025)
        self.debug_text.set_align('top', 'right')

        # fps
        self.show_fps = show_fps
        self.fps = fps or 60

        # Z-sorted slides
        self.sorted_slides = []
        self.slides_need_sorting = False
        self._sort_slides()

        # Memory
        self.monitor = MemoryMonitor(max_gpu_memory, self.flush)

        # Scenes
        self.scenes = {}

        # Signal
        signal(SIGINT, self.stop)
        signal(SIGTERM, self.stop)

    def start(self):
        """
        - load textures
        - run the main loop
             - receive osc messages
             - draw slides, skip grouped slides (drawn by their parents)
        """

        ####### upload fonts and post_process to gpu
        for n in self.texts:
            self.texts[n].set_visible(1)
            self.texts[n].draw()
        self.post_process.set_visible(1)
        self.post_process.draw()

        for n in self.texts:
            self.texts[n].set_visible(0)
        self.post_process.set_visible(0)
        #######

        if self.show_fps:
            nframes = 0
            elapsed = 0
            start = time()
            elapsed = 0

        while self.DISPLAY.loop_running():

            # wait last frame end
            now = time()
            delta = 1. / self.fps - (now - self.time)
            if delta > 0:
                sleep(delta)

            # update clock
            self.time = time()

            # process osc messages
            while self.server.recv(0):
                pass

            post_processing = self.post_process.visible

            if post_processing:
                self.post_process.capture_start()

            if self.slides_need_sorting:
                self._sort_slides()

            for slide in self.sorted_slides:
                if not slide.parent_slide:
                    slide.draw()

            if post_processing:
                self.post_process.capture_end()
                self.post_process.draw()

            if self.show_fps:
                if time() - start > 1.0:
                    self.debug_text.set_visible(1)
                    self.debug_text.set_text('fps: %i' % nframes)
                    start = time()
                    nframes = 0
                nframes += 1

            self.debug_text.draw()



    def stop(self, *args):
        """
        Stop main loop and osc server
        """
        self.DISPLAY.stop()
        self.DISPLAY.destroy()
        super(PytaVSL, self).stop()

    @osc_method('stop')
    def osc_stop(self):
        """
        Shutdown pytaVSL
        """
        self.stop()

    @osc_method('load')
    def load_textures(self, *files):
        """
        Load files to slides
            files: file path or glob patterns
        """
        paths = []
        for f in files:
            paths += glob.glob(f)

        if len(files) == 0:
            LOGGER.error("file \"%s\" not found" % path)

        def threaded():

            size = len(paths)

            self.debug_text.set_visible(1)
            self.debug_text.set_text('0/' + str(size))

            for i in range(size):
                try:
                    path = paths[i]
                    name = path.split('/')[-1].split('.')[0].lower()
                    slide = Slide(parent=self, name=name, texture=path, init_z=len(self.slides) / 1000.)
                    self.add_slide(slide)
                except Exception as e:
                    LOGGER.error('could not load file %s' % path)
                    print(traceback.format_exc())
                self.debug_text.set_text(str(i + 1) + '/' + str(size))

            self.debug_text.set_visible(0)

            LOGGER.info("total slides in memory: %i" % len(self.slides.values()))

        t = Thread(target=threaded)
        t.daemon = True
        t.start()

    def sort_slides(self):
        """
        Sort slides in drawing order (by z-index)
        """
        self.slides_need_sorting = True

    def _sort_slides(self):
        self.sorted_slides = sorted(list(self.slides.values()) + list(self.texts.values()), key=lambda slide: slide.z(), reverse=True)
        self.slides_need_sorting = False

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
        if slide.name in self.slides:
            LOGGER.error('could not add slide "%s" (name taken)' % slide.name)
            return
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

    @osc_method('text')
    def create_text(self, name, font):
        """
        Create text object
            name: text name
            font: font name (as defined in config.py)
        """
        name = str(name)
        font = str(font)
        if name in self.texts:
            LOGGER.error('could not add text "%s" (name taken)' % name)
            return
        if not font in FONTS:
            LOGGER.error('could not add text "%s" (font "%s" not found)' % (name, font))
            return
        self.texts[name] = Text(self, name, font=FONTS[font], init_z=-100 + len(self.texts))
        self.sort_slides()

    @osc_method('group')
    def create_group(self, slides, group_name):
        """
        Create slide group
            slides: slide name pattern
            group_name: new group's name (replaces any previously created group with the same name)
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
        group.is_group = slides

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
            group_name: group's name
        """
        name = group_name.lower()
        for group in self.get_children(self.slides, name):
            if group.is_group:
                self.remove_slide(group)

    @osc_method('clone')
    def create_clone(self, slide, clone_name):
        """
        Create a clone slide
            slide: target slide name (can't be a clone nor a group)
            clone_name: new clone name (replaces any previously created clone with the same name)
        """
        clone_name = clone_name.lower()
        target_name = slide.lower()

        target = self.get_children(self.slides, target_name)
        if len(target) > 1:
            LOGGER.error('could not create clone "%s" (target "%s" matches %i slides)' % (clone_name, target_name, len(target)))
            return

        target = target[0]

        if target.is_group:
            LOGGER.error('could not create clone "%s" (target "%s" is a group' % (clone_name, target.name))
            return

        if target.is_clone:
            LOGGER.error('could not create clone "%s" (target "%s" is a clone' % (clone_name, target.name))
            return

        if not target:
            LOGGER.error('no slide to clone (%s)' % (target_name))
            return

        if clone_name in self.slides:
            if self.slides[clone_name].is_clone:
                self.remove_slide(self.slides[clone_name])
            else:
                LOGGER.error("could not create clone \"%s\" (name taken by a non-clone slide)" % clone_name)
                return

        clone_z = target.pos_z - 0.001
        clone = Slide(parent=self, name=clone_name, texture=pi3d.Texture(target.buf[0].textures[0].image), width=target.width, height=target.height, init_z=clone_z)
        clone.state_set(target.state_get())
        clone.set_position_z(clone_z)

        clone.gif = target.gif
        clone.is_clone = target.name

        self.add_slide(clone)

    @osc_method('unclone')
    def remove_clone(self, clone_name):
        """
        Remove clone slide
            clone_name: clone's name
        """
        clone_name = clone_name.lower()
        for clone in self.get_children(self.slides, clone_name):
            if clone.is_clone:
                self.remove_slide(clone)


    def scene_get(self):
        scene = {}

        for n in self.slides:
            slide = self.slides[n]
            if slide.visible:
                if not 'slides' in scene:
                    scene['slides'] = {}
                scene['slides'][slide.name] = slide.state_get()
                if slide.is_clone:
                    if not 'clones' in scene:
                        scene['clones'] = {}
                    scene['clones'][slide.name] = {'target': slide.is_clone}
                if slide.is_group:
                    if not 'groups' in scene:
                        scene['groups'] = {}
                    scene['groups'][slide.name] = {'children': slide.is_group}

        for n in self.texts:
            slide = self.texts[n]
            if slide.visible:
                if not 'texts' in scene:
                    scene['texts'] = {}
                scene['texts'][slide.name] = slide.state_get()

        if self.post_process.visible:
            scene['post_process'] = self.post_process.state_get()

        return scene

    @osc_method('scene_save')
    def scene_save(self, name):
        """
        Save current scene (visible slides/texts/clones/groups' state)
            name: slot name
        """
        self.scenes[name] = self.scene_get()

    @osc_method('scene_recall')
    def scene_recall(self, name):
        """
        Recall scene (visible slides/texts/clones/groups' state)
            name: slot name
        """
        if name not in self.scenes:
            LOGGER.error('scene "%s" not found' % name)
            return

        for slide in self.sorted_slides:
            slide.set_visible(0)

        scene = self.scenes[name]

        if 'clones' in scene:
            for name in scene['clones']:
                self.create_clone(*scene['clones'][name]['target'], name)

        if 'groups' in scene:
            for name in scene['groups']:
                self.create_group(*scene['groups'][name]['children'], name)

        if 'slides' in scene:
            for name in scene['slides']:
                self.slides[name].reset()
                self.slides[name].state_set(scene['slides'][name])

        if 'texts' in scene:
            for name in scene['texts']:
                self.texts[name].reset()
                self.texts[name].state_set(scene['texts'][name])

        if 'post_process' in scene:
            self.post_process.reset()
            self.post_process.state_set(scene['post_process'])
        else:
            self.post_process.set_visible(0)

    @osc_method('scene_export')
    def scenes_export(self, file_or_name, file=None):
        """
        Save scene to file (visible slides/texts/clones/groups' state)
            file_or_name: scene slot name or file path to save current scene
            file: file path (if file_or_name is a slot name)
        """

        if file:
            if name not in self.scenes:
                LOGGER.error('scene "%s" not found' % name)
                return
            scene = self.scenes[file_or_name]
        else:
            scene = self.scene_get()
            file = file_or_name

        def threaded():

            try:
                content  = '# pytaVSL scene file\n\n'
                content += toml.dumps(scene, tomlencoder)
                content = content.replace(',]', '')
                content = content.replace('= [ ', '= ')
                writer = open(file, 'w')
                writer.write(content)
                writer.close()
            except Exception as e:
                LOGGER.error('could not export scene to file %s' % file)
                print(traceback.format_exc())

        t = Thread(target=threaded)
        t.daemon = True
        t.start()

    @osc_method('scene_import')
    def scenes_import(self, *files):
        """
        Load scene files
            files: file path or glob patterns
        """
        paths = []
        for f in files:
            paths += glob.glob(f)

        if len(files) == 0:
            LOGGER.error("file \"%s\" not found" % path)

        def threaded():

            size = len(paths)

            for i in range(size):
                try:
                    path = paths[i]
                    name = path.split('/')[-1].split('.')[0].lower()
                    _content = open(path, 'r').read()
                    content = ''
                    for line in _content.split('\n'):
                        if '=' in line:
                            line += ']'
                        content += line + '\n'
                    content = content.replace('=', '= [')
                    self.scenes[name] = toml.loads(content)
                except Exception as e:
                    LOGGER.error('could not load scene file %s' % path)
                    print(traceback.format_exc())

        t = Thread(target=threaded)
        t.daemon = True
        t.start()

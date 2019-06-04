# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import pi3d
from pi3d.Display import Display
from utils import unicode
from osc import osc_method

import logging
LOGGER = logging.getLogger(__name__)

import subprocess
import threading
import time
import numpy
import re

videos_formats = re.compile('^.*\.(mov|avi|mpg|mpeg|mp4|mkv|wmv|webm)$')

class Player(object):
    def __init__(self, file):

        self.resolution = self.get_video_resolution(file)
        self.depth = 8
        self.array_shape = (self.resolution[1], self.resolution[0], int(self.depth / 8))

        self.frame = None
        self.new_frame = False
        self.process = None
        self.running = False
        self.bufsize = int(self.resolution[0] * self.resolution[1] * self.depth / 8)
        self.command = [ 'ffmpeg', '-i', file, '-f', 'image2pipe', '-r', '25',
                                  '-pix_fmt', 'rgb' + str(self.depth), '-vcodec', 'rawvideo', '-']

        t = threading.Thread(target=self.loop)
        t.daemon = True
        t.start()

    def loop(self):

        while True:

            if self.running:

                self.new_frame = False

                frame = self.process.stdout.read(self.bufsize)

                self.process.stdout.flush()
                self.process.stderr.flush()

                if len(frame) < self.bufsize:
                    self.start()
                elif frame != self.frame:
                    self.frame = frame
                    self.new_frame = True

            time.sleep(0.04)

    def start(self):
        if self.process:
            self.stop()
        self.process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=self.bufsize)
        self.running = True

    def stop(self):
        self.process.terminate()
        self.running = False
        self.new_frame = False

    def get_frame_array(self):
        array = numpy.fromstring(self.frame, dtype='uint8')
        array.shape = self.array_shape
        return array

    def get_video_resolution(self, file):
        out = subprocess.check_output('ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0'.split(' ') + [file])
        res = out.split(b'\n')[0]
        res = res.split(b'x')
        res = [int(x) for x in res]
        return res

class Video(object):

    def __init__(self, texture, *args, **kwargs):

        self.video = False
        self.video_player = None

        if isinstance(texture, (str, unicode)):
            match = videos_formats.match(texture)
            if match and match.string:
                LOGGER.warning('video support is experimental !')
                self.video_player = Player(texture)
                texture = pi3d.Texture(numpy.zeros(self.video_player.array_shape, dtype='uint8'))
                self.video = True

        super(Video, self).__init__(texture=texture, *args, **kwargs)

    def draw(self, *args, **kwargs):

        self.video_next_frame()

        super(Video, self).draw(*args, **kwargs)

    def video_next_frame(self):
        if self.video and self.visible:
            if not self.video_player.running:
                self.video_player.start()
            if self.video_player.new_frame:
                self.buf[0].textures[0].update_ndarray(self.video_player.get_frame_array())

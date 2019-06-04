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

import cv2

videos_formats = re.compile('^.*\.(mov|avi|mpg|mpeg|mp4|mkv|wmv|webm)$')

class Player(object):
    def __init__(self, file):


        self.file = file
        self.process = None
        # self.process.set(cv2.CAP_PROP_PVAPI_PIXELFORMAT, cv2.CAP_PVAPI_PIXELFORMAT_BGR24)
        # self.process.set(cv2.CAP_PROP_FORMAT, cv2.CAP_PVAPI_PIXELFORMAT_BGR24)
        self.resolution = self.get_video_resolution(file)
        self.depth = 8
        self.array_shape = (self.resolution[1], self.resolution[0], int(self.depth / 8))

        self.frame = None
        self.running = False


    def start(self):
        self.stop()
        self.process = cv2.VideoCapture(self.file)
        self.running = True

    def stop(self):
        self.process = None
        self.running = False
        self.new_frame = False

    def next_frame(self):
        if not self.running:
            self.start()
        ok = self.process.grab()
        if not ok:
            self.process.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.process.grab()
        ok, frame = self.process.retrieve(0, 0)
        self.frame = frame
        self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GA)
        # self.frame.shape = self.array_shape

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
            self.video_player.next_frame()
            self.buf[0].textures[0].update_ndarray(self.video_player.frame)

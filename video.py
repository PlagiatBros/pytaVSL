# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import pi3d
from pi3d.Display import Display
from pi3d.constants import opengles
from utils import unicode
from osc import osc_method

import logging
LOGGER = logging.getLogger(__name__)

import subprocess
import threading
import time
import numpy

def read_video(file, h, w, p):

    player = {
        'frame': None,
        'new': False,
        'restart': True
    }

    def pipe_thread():
        pipe = None

        while True:

            if player['restart']:
                if pipe is not None:
                    pipe.terminate()

                command = [ 'ffmpeg', '-i', file, '-f', 'image2pipe', '-r', '25',
                                          '-pix_fmt', 'rgb8', '-vcodec', 'rawvideo', '-']
                pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=w*h*p)
                player['restart'] = False

            player['new'] = False
            frame =  pipe.stdout.read(h * w * p)
            pipe.stdout.flush()
            pipe.stderr.flush()

            if len(frame) < h * w * p:
                player['restart'] = True
            elif frame != player['frame']:
                player['frame'] = frame
                player['new'] = True

            time.sleep(0.04)

    t = threading.Thread(target=pipe_thread)
    t.daemon = True
    t.start()

    return player


def get_video_resolution(file):
    out = subprocess.check_output('ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0'.split(' ') + [file])
    res = out.split(b'\n')[0]
    res = res.split(b'x')
    res = [int(x) for x in res]
    return res

class Video(object):

    def __init__(self, texture, *args, **kwargs):

        self.video = False
        self.video_reader = 0

        if isinstance(texture, (str, unicode)) and '.mp4' in texture:
            LOGGER.warning('video support is experimental !')
            w, h = get_video_resolution(texture)
            self.video_resolution = (h, w, 1)
            self.video_reader = read_video(texture, *self.video_resolution)
            texture = pi3d.Texture(numpy.zeros(self.video_resolution, dtype='uint8'))
            self.video = True

        super(Video, self).__init__(texture=texture, *args, **kwargs)

    def draw(self, *args, **kwargs):

        self.video_next_frame()

        super(Video, self).draw(*args, **kwargs)

    def video_next_frame(self):
        if self.video and self.visible:
            if self.video_reader['new']:
                array = numpy.fromstring(self.video_reader['frame'], dtype='uint8')
                array.shape = self.video_resolution
                self.buf[0].textures[0].update_ndarray(array)

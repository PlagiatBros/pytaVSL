# encoding: utf-8

import pi3d
import ctypes
from pi3d.constants import (opengles, GL_TEXTURE0, GL_TEXTURE_2D, GL_UNSIGNED_BYTE)
from osc import osc_property
from config import config

import logging
LOGGER = logging.getLogger(__name__)

import subprocess
import os.path

import numpy
import re


video_support = False
audio_support = False
videos_formats = re.compile('^.*\.(mov|avi|mpg|mpeg|mp4|mkv|wmv|webm)$')

class Video(object):

    def __init__(self, parent, name, texture, *args, **kwargs):

        self.video = False
        self.audio = False
        self.video_speed = 1.0
        self.video_time = 0

        if isinstance(texture, str):
            match = videos_formats.match(texture.lower())
            if match and match.string:

                try:
                    global cv2, video_support
                    import cv2
                    video_support = True
                except:
                    LOGGER.error('python-opencv is required to play videos')

                if config.audio:
                    try:
                        global Player, audio_support
                        from mplayer import Player, CmdPrefix
                        Player.cmd_prefix = CmdPrefix.PAUSING_KEEP
                        audio_support = True
                    except:
                        LOGGER.warning('mplayer.py not found, video will play without audio')


                if audio_support:

                    self.audio = True

                    audiopath = texture + '.wav'
                    if not os.path.isfile(audiopath):
                        print('extracting audio stream to ' + audiopath)
                        subprocess.run(['ffmpeg', '-i', texture, '-acodec', 'pcm_s16le', '-ac', '2', audiopath])

                    mplayer_args = ['-vo', 'null']

                    if config.jack:
                        jackname = parent.name + '/' + name
                        if len(jackname) > 63:
                            jackname = jackname[0:62]
                        mplayer_args.append('-ao')
                        mplayer_args.append('jack:name=%s' % jackname)

                    self.audio_reader = Player(args=mplayer_args)
                    self.audio_reader.loadfile(texture + '.wav')
                    self.audio_bypass = 0
                    self.audio_sync = 0
                    self.set_audio_bypass(1)

                if video_support:

                    self.video = True

                    self.video_reader = cv2.VideoCapture(texture)
                    self.video_shape = (int(self.video_reader.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(self.video_reader.get(cv2.CAP_PROP_FRAME_WIDTH)), 3)
                    self.video_texture = pi3d.Texture(numpy.zeros(self.video_shape, dtype='uint8'), mipmap=True)
                    self.frame_format = self.video_texture._get_format_from_array(self.video_texture.image, self.video_texture.i_format)

                    self.video_frame_duration = 1. / min(self.video_reader.get(cv2.CAP_PROP_FPS), 60)
                    self.video_duration = self.video_frame_duration * self.video_reader.get(cv2.CAP_PROP_FRAME_COUNT)

                    self.video_elapsed_time = 0

                    texture = self.video_texture

        super(Video, self).__init__(parent=parent, name=name, texture=texture, *args, **kwargs)

        if self.video:
            self.active_effects.append('VIDEO')

    def draw(self, *args, **kwargs):

        if self.video and self.visible:
            self.video_next_frame()

            if self.audio and self.audio_sync:
                self.audio_reader.seek(self.video_time, 2)
                self.audio_sync = 0

        super(Video, self).draw(*args, **kwargs)


    @osc_property('video_time', 'video_time')
    def set_video_time(self, time):
        """
        current video time in seconds (cpu expensive for any value other than 0)
        """
        if not self.video:
            return

        time = float(time)

        if time > self.video_duration:
            time = 0

        self.video_reader.set(cv2.CAP_PROP_POS_MSEC, time * 1000)
        self.video_time = time
        # self.video_reader.get(cv2.CAP_PROP_POS_MSEC) / 1000.

        if self.video_time > 0:
            self.video_elapsed_time = self.parent.time

        if self.audio:
            self.set_audio_sync()


    @osc_property('video_speed', 'video_speed')
    def set_video_speed(self, speed):
        """
        video playback speed (0=paused, no reverse playback, high speed is cpu expensive)
        """
        if not self.video:
            return

        self.video_speed = max(float(speed), 0)
        self.video_elapsed_time = 0

        if self.audio:
            if self.video_speed == 1:
                self.set_audio_sync()
                if self.visible:
                    self.set_audio_bypass(0)
            else:
                self.set_audio_bypass(1)


    def video_next_frame(self):

        time = self.parent.time

        if self.video_elapsed_time == 0 or self.video_speed == 0:
            self.video_elapsed_time = time
            if self.video_speed == 0:
                return

        delta = (time - self.video_elapsed_time)
        frames = int(delta / (self.video_frame_duration / self.video_speed))

        if frames > 0:

            for i in range(frames):

                ok = self.video_reader.grab()
                if not ok:
                    self.set_video_time(0)

            self.video_elapsed_time += frames * (self.video_frame_duration / self.video_speed)

            self.video_time += frames * self.video_frame_duration
            # self.video_time = self.video_reader.get(cv2.CAP_PROP_POS_MSEC) / 1000.

            self.video_load_current_frame()

    def video_load_current_frame(self):
        ok, frame = self.video_reader.retrieve()
        if ok:
            # return self.video_texture.update_ndarray(frame, 0)
            tex = self.video_texture
            opengles.glActiveTexture(GL_TEXTURE0)
            opengles.glBindTexture(GL_TEXTURE_2D, tex._tex)
            opengles.glTexSubImage2D(GL_TEXTURE_2D, 0,
                                     0, 0, tex.ix, tex.iy,
                                     self.frame_format, GL_UNSIGNED_BYTE,
                                     # frame.__array_interface__['data'][0])
                                     frame.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte)))


    def set_audio_bypass(self, state):
        state = int(bool(state))
        if self.audio_bypass != state:
            self.audio_bypass = state
            self.audio_reader.mute = bool(state)

    def set_audio_sync(self):
        self.audio_sync = 1

    def property_changed(self, name):

        super(Video, self).property_changed(name)

        if self.audio:
            if name == 'visible':
                if self.visible:
                    self.set_audio_sync()
                self.set_audio_bypass(self.visible == 0)

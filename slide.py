# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import time
import pi3d
import liblo

from pi3d.Display import Display

import random
from utils import KillableThread as Thread
from strobe import Strobe
from animation import Animable
from gif import Gif
from memory import gpu_monitor

import logging
LOGGER = logging.getLogger(__name__)

class Slide(Strobe, Gif, Animable, pi3d.Plane):

    def __init__(self, name, light, z):

        super(Slide, self).__init__(w=1.0, h=1.0, light=light)

        self.visible = False

        self.name = name
        self.light = light
        self.color = (0,0,0)
        self.color_strobe = 0

        # Scales
        self.sx = 1.0
        self.sy = 1.0
        self.sz = 1.0

        self.init_w = 1.0
        self.init_h = 1.0
        self.init_z = z

        # Angle
        self.ax = 0.0
        self.ay = 0.0
        self.az = 0.0

        # texture tiling
        self.tiles = [1.0, 1.0]

        self.loaded = False

    def unload(self):
        if self.loaded and not self.visible:
            self.loaded = False
            for t in self.textures:
                t.unload_opengl()
                # t.__del__()
            for b in self.buf:
                b.unload_opengl()
                # b.__del__()
                for t in b.textures:
                    t.unload_opengl()
                    # t.__del__()
            gpu_monitor.free(self)

    def draw(self, *args, **kwargs):

        self.animate_next_frame()

        if self.color_strobe > 0:
            zero = random.randint(0, 2)
            rgb = [0,0,0]
            rgb[(zero + 1) % 3] = -random.random() * self.color_strobe / 2
            rgb[(zero - 1) % 3] = random.random() * self.color_strobe
            rgb[zero] = - random.random() * 1
            self.set_color(rgb, True)

        if self.strobe:
            self.strobe_state.next()
        if self.visible and (not self.strobe or self.strobe_state.visible):
            if not self.loaded:
                self.loaded = True
                if not gpu_monitor.alloc(self):
                    return
            super(Slide, self).draw(*args, **kwargs)

    def clone(self, name):
        state = self.__getstate__()
        clone = Slide(name, self.light, self.z())
        clone.__setstate__(state)
        clone.init_w = self.init_w
        clone.init_h = self.init_h
        return clone

    def set_tiles(self, x, y):
        self.tiles = [x, y]
        for b in self.buf:
            b.unib[6] = x
            b.unib[7] = y

        self.set_offset(((1-x)/2.,(1-y)/2.))

    def set_visible(self, visible):
        self.visible = bool(visible)

    def set_color(self, color, tmp = False):
        if tmp is False:
            self.color = color
        self.light.ambient(color)
        self.set_light(self.light)

    def set_color_strobe(self, strobe):
        self.color_strobe = strobe
        if strobe == 0:
            self.set_color(self.color)

    def set_position(self, x, y, z):
        """
        set_position aims to set the position of the slides and to keep a trace of it
        """
        self.position(x, y, z)

    def set_translation(self, dx, dy, dz):
        """
        set_translation does a translation operation on the slide
        """
        self.translate(dx, dy, dz)

    def set_scale(self, sx, sy, sz):
        """
        set_scale sets the scale of the slides and keeps track of it
        """
        self.sx = sx
        self.sy = sy
        self.sz = sz
        self.scale(sx, sy, sz)

    def set_zoom(self, zoom):
        """
        Scaling relative to initial size, aka zoom
        """
        self.set_scale(zoom * self.init_w, zoom * self.init_h, self.z())

    def set_angle(self, ax, ay, az):
        # set angle (absolute)
        """
        set_angle sets the rotation of the slide and keeps track of it. It's an absolute angle, not a rotation one.
        """
        self.ax = ax
        self.ay = ay
        self.az = az
        self.rotateToX(ax)
        self.rotateToY(ay)
        self.rotateToZ(az)

    def reset(self):
        self.sx = self.init_w
        self.sy = self.init_h
        self.sz = 1.0
        self.scale(self.sx, self.sy, self.sz)
        self.set_position(0, 0, self.init_z)
        self.set_color((0,0,0))
        self.set_color_strobe(0)
        self.set_angle(0, 0, 0)
        self.set_visible(False)
        self.set_strobe(0, 2, 0.5)
        self.set_tiles(1.0, 1.0)
        self.stop_animate()

    def get_param_getter(self, name):
        """
        Getters for osc & animations
        """

        _val = super(Slide, self).get_param_getter(name)

        val = 0
        if name == 'position_x':
            val = self.x()
        elif name == 'position_y':
            val = self.y()
        elif name == 'position_z':
            val = self.z()
        elif name == 'rotate_x':
            val = self.ax
        elif name == 'rotate_y':
            val = self.ay
        elif name == 'rotate_z':
            val = self.az
        elif name == 'scale_x':
            val = self.sx
        elif name == 'scale_y':
            val = self.sy
        elif name == 'scale_z':
            val = self.sz
        elif name == 'zoom' or name == 'rsxy':
            val = self.sx / self.init_h
        elif name == 'alpha':
            val = self.alpha()
        elif name == 'tiles':
            val = self.tiles[0]

        return val if val is not 0 else _val

    def get_param_setter(self, name):
        """
        Setters for osc & animations
        """

        _set_val = super(Slide, self).get_param_setter(name)

        if name == 'position_x':
            def set_val(val):
                self.set_position(val, self.y(), self.z())
        elif name == 'position_y':
            def set_val(val):
                self.set_position(self.x(), val, self.z())
        elif name == 'position_z':
            def set_val(val):
                self.set_position(self.x(), self.y(), val)
        elif name == 'rotate_x':
            def set_val(val):
                self.set_angle(val, self.ay, self.az)
        elif name == 'rotate_y':
            def set_val(val):
                self.set_angle(self.ax, val, self.az)
        elif name == 'rotate_z':
            def set_val(val):
                self.set_angle(self.ax, self.ay, val)
        elif name == 'scale_x':
            def set_val(val):
                self.set_scale(val, self.sy, self.sz)
        elif name == 'scale_y':
            def set_val(val):
                self.set_scale(self.sx, val, self.sz)
        elif name == 'scale_z':
            def set_val(val):
                self.set_scale(self.sx, self.sy, val)
        elif name == 'zoom' or name == 'rsxy':
            def set_val(val):
                self.set_zoom(val)
        elif name == 'alpha':
            def set_val(val):
                self.set_alpha(val)
        elif name == 'tiles':
            def set_val(val):
                self.set_tiles(val, val)
        else:
            set_val = None

        return set_val if set_val is not None else _set_val

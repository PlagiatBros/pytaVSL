# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import time
import pi3d
import liblo

from utils import KillableThread as Thread
from strobe import Strobe
from animation import Animation

LOGGER = pi3d.Log(__name__)

class Slide(Strobe, Animation, pi3d.Plane):

    def __init__(self, name, path, light, z):

        super(Slide, self).__init__(w=1.0, h=1.0, light=light)

        self.visible = False

        self.name = name
        self.path = path
        self.light = light

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

    def clone(self, name):
        state = self.__getstate__()
        clone = Slide(name, self.path, self.light)
        clone.__setstate__(state)
        clone.init_w = self.init_w
        clone.init_h = self.init_h
        return clone

    def set_color(self, color):
        self.light.ambient(color)
        self.set_light(self.light)

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

    def reset(self):
        self.sx = self.init_w
        self.sy = self.init_h
        self.sz = 1.0
        self.scale(self.sx, self.sy, self.sz)
        self.set_position(0, 0, self.init_z)
        self.set_angle(0, 0, 0)

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

    def set_visible(self, visible):
        self.visible = bool(visible)

    def draw(self, *args, **kwargs):

        self.animate_next_frame()

        if self.strobe:
            self.strobe_state.next()
        if self.visible and (not self.strobe or self.strobe_state.visible):
            super(Slide, self).draw(*args, **kwargs)

    def get_animate_value(self, name):
        """
        Getters for animations
        """
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
        elif name == 'alpha':
            val = self.alpha()

        return val

    def get_animate_setter(self, name):
        """
        Setters for animations
        """
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
        elif name == 'alpha':
            def set_val(val):
                self.set_alpha(val)
        else:
            def set_val(val):
                pass

        return set_val

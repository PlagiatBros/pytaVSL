# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import time
import pi3d
import liblo
import copy
import colorsys

from pi3d.Display import Display

import random
from utils import KillableThread as Thread
from strobe import Strobe
from effect import Effect
from animation import Animable
from gif import Gif
from memory import gpu_monitor
from config import *

import logging
LOGGER = logging.getLogger(__name__)

class Slide(Effect, Strobe, Gif, Animable, pi3d.Plane):

    def __init__(self, parent, name, texture, width=1, height=1):

        if type(texture) is str:

            texture = pi3d.Texture(texture, blend=True, mipmap=True)
            width = texture.ix
            height = texture.iy

        super(Slide, self).__init__(texture=texture, w=width, h=height)

        self.name = name
        self.visible = False
        self.parent = parent
        self.parent_slide = None

        if texture:
            self.set_textures([texture])

        # Color
        self.color = (0.5,0.5,0.5)
        self.color_strobe = 0

        # Scale
        self.init_scale = min(Display.INSTANCE.width / width, Display.INSTANCE.height / height)
        self.sx = 1.0
        self.sy = 1.0

        # Angle
        self.ax = 0.0
        self.ay = 0.0
        self.az = 0.0

        # texture tiling
        self.tiles = [1.0, 1.0]
        self.offset= [0.0, 0.0]

        self.loaded = False
        self.grouped = False

        self.set_zoom(1.0)

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

        if self.color_strobe > 0:
            rgb = list(colorsys.hsv_to_rgb(random.random(), 1.0, 1.0))
            rgb[random.randint(0,2)] *= self.color_strobe
            self.set_color(rgb, True)

        if self.visible and (not self.strobe or self.strobe_state.visible()):
            if not self.loaded:
                self.loaded = True
                if not gpu_monitor.alloc(self):
                    return
            self.animate_next_frame()

            super(Slide, self).draw(*args, **kwargs)

    def clone(self, name):
        clone = Slide(self.parent, name, pi3d.Texture(self.buf[0].textures[0].image), self.width, self.height)
        clone.gif = self.gif
        return clone

    def set_tiles(self, x, y):
        if x is not None:
            self.tiles[0] = x
        if y is not None:
            self.tiles[1] = y

        for b in self.buf:
            b.unib[6] = self.tiles[0]
            b.unib[7] = self.tiles[1]

        self.set_offset()

    def set_offset(self, x=None, y=None):
        if x is not None:
            self.offset[0] = x
        if y is not None:
            self.offset[1] = y
        super(Slide, self).set_offset((self.offset[0] + (1-self.tiles[0])/2, self.offset[1] + (1-self.tiles[1])/2.))

    def set_visible(self, visible):
        """
        set visibility
        """
        self.visible = bool(visible)

    def set_color(self, color, tmp = False):
        """
        set color
        """
        if not tmp:
            self.color = color
        self.set_material(color)


    def set_color_strobe(self, strobe):
        """
        set color strobing strength
        """
        self.color_strobe = strobe
        if strobe <= 0:
            self.set_color(self.color)

    def set_position(self, x, y, z, prevent_sorting=False):
        """
        set_position aims to set the position of the slides and to keep a trace of it
        """
        sort_parent = z != self.z() and not prevent_sorting
        self.position(x, y, z)
        if sort_parent:
            parent = self.parent_slide if self.parent_slide is not None else self.parent
            parent.sort_slides()

    def set_translation(self, dx, dy, dz):
        """
        set_translation does a translation operation on the slide
        """
        self.translate(dx, dy, dz)

    def set_scale(self, sx, sy):
        """
        set_scale sets the scale of the slides and keeps track of it
        """
        self.sx = sx
        self.sy = sy
        self.scale(sx * self.init_scale, sy * self.init_scale, 1.0)

    def set_zoom(self, zoom):
        """
        Scaling relative to initial size, aka zoom
        """
        self.set_scale(zoom, zoom)

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

    def sort_slides(self):
        """
        Sort slides in drawing order (by z-index)
        """
        self.children = sorted(self.children, key=lambda slide: slide.z(), reverse=True)

    def reset(self):
        self.set_scale(1.0, 1.0)
        self.set_position(0, 0, 0)
        self.set_color((0.5,0.5,0.5))
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
        elif name == 'zoom' or name == 'rsxy':
            val = self.sx
        elif name == 'alpha':
            val = self.alpha()
        elif name == 'tiles':
            val = self.tiles[0]
        elif name == 'tiles_x':
            val = self.tiles[0]
        elif name == 'tiles_y':
            val = self.tiles[1]
        elif name == 'offset_x':
            val = self.offset[0]
        elif name == 'offset_y':
            val = self.offset[1]

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
                self.set_scale(val, self.sy)
        elif name == 'scale_y':
            def set_val(val):
                self.set_scale(self.sx, val)
        elif name == 'zoom' or name == 'rsxy':
            def set_val(val):
                self.set_zoom(val)
        elif name == 'alpha':
            def set_val(val):
                self.set_alpha(val)
        elif name == 'tiles':
            def set_val(val):
                self.set_tiles(val, val)
        elif name == 'tiles_x':
            def set_val(val):
                self.set_tiles(val, None)
        elif name == 'tiles_y':
            def set_val(val):
                self.set_tiles(None, val)
        elif name == 'offset_x':
            def set_val(val):
                self.set_offset(val, None)
        elif name == 'offset_y':
            def set_val(val):
                self.set_offset(None, val)
        else:
            set_val = None

        return set_val if set_val is not None else _set_val

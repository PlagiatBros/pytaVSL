# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import pi3d
import colorsys
import random

from pi3d.Display import Display

from state import State
from effect import Effect
from animation import Animable
from perspective import Perspective
from gif import Gif
from video import Video
from osc import OscNode, osc_property
from config import *

import logging
LOGGER = logging.getLogger(__name__)

class SlideBase(OscNode, Effect, Animable, pi3d.Plane):

    def __init__(self, parent, name, texture, width=None, height=None, init_z=0.0):

        if type(texture) is str:

            texture = pi3d.Texture(texture, blend=True, mipmap=True)

        super(SlideBase, self).__init__(w=width if width is not None else texture.ix, h=height if height is not None else texture.iy)

        self.name = name
        self.parent = parent
        self.parent_slide = None
        self.is_group = False
        self.children_need_sorting = False
        self.is_clone = False

        if texture:
            self.set_textures([texture])

        self.visible = 0

        # Color
        self.color = [0.5,0.5,0.5]
        self.color_strobe = 0
        self.color_alpha = 1.0

        # Position
        self.pos_x = 0.0
        self.pos_y = 0.0
        self.pos_z = init_z

        # Scale
        self.init_scale = min(Display.INSTANCE.width / self.width, Display.INSTANCE.height / self.height)
        self.sx = 1.0
        self.sy = 1.0

        # Rotate
        self.rx = 0.0
        self.ry = 0.0
        self.rz = 0.0

        # texture tiling
        self.tiles = [1.0, 1.0]
        self.offset= [0.0, 0.0]

        self.loaded = False
        self.grouped = False

        # init
        self.set_zoom(1.0)
        self.set_position_z(self.pos_z)

    def draw(self, *args, **kwargs):

        if self.visible:

            if self.color_strobe > 0:
                rgb = list(colorsys.hsv_to_rgb(random.random(), 1.0, 1.0))
                rgb[random.randint(0,2)] *= self.color_strobe
                self.set_material(rgb)

            if not self.loaded:
                self.loaded = True
                if not self.parent.monitor.alloc(self):
                    return

            if self.children_need_sorting:
                self.children = sorted(self.children, key=lambda slide: slide.z(), reverse=True)
                self.children_need_sorting = False

            super(SlideBase, self).draw(*args, **kwargs)


    def quit_group(self):
        if self.parent_slide:
            self.parent_slide.children.remove(self)
            self.parent_slide.sort_slides()
            self.parent_slide = None

    def sort_slides(self):
        """
        Sort children in drawing order (by z-index)
        """
        self.children_need_sorting = True

    def unload(self):
        if self.loaded and not self.visible:
            self.loaded = False
            for t in self.textures:
                t.unload_opengl()
            for b in self.buf:
                b.unload_opengl()
                for t in b.textures:
                    t.unload_opengl()
            self.parent.monitor.free(self)

    @osc_property('tiles', 'tiles')
    def set_tiles(self, x, y):
        if x is not None:
            self.tiles[0] = float(x)
        if y is not None:
            self.tiles[1] = float(y)

        for b in self.buf:
            b.unib[6] = self.tiles[0]
            b.unib[7] = self.tiles[1]

        self.set_offset(None, None)

    @osc_property('offset', 'offset')
    def set_offset(self, x, y):
        if x is not None:
            self.offset[0] = float(x)
        if y is not None:
            self.offset[1] = float(y)
        super(SlideBase, self).set_offset((self.offset[0] + (1-self.tiles[0])/2, self.offset[1] + (1-self.tiles[1])/2.))

    @osc_property('visible', 'visible')
    def set_visible(self, visible):
        """
        set visibility
        """
        self.visible = int(bool(visible))

    @osc_property('color', 'color')
    def set_color(self, r, g, b):
        """
        set color
        """
        self.color = [float(r), float(g), float(b)]
        self.set_material(self.color)

    @osc_property('alpha', 'color_alpha')
    def set_color_alpha(self, alpha):
        self.color_alpha = float(alpha)
        self.set_alpha(self.color_alpha)


    @osc_property('color_strobe', 'color_strobe')
    def set_color_strobe(self, strobe):
        """
        set color strobing strength
        """
        self.color_strobe = float(strobe)
        if strobe <= 0:
            self.set_color(*self.color)

    @osc_property('position', 'pos_x', 'pos_y', 'pos_z')
    def set_position(self, x, y, z):
        sort_parent = False
        if x is not None:
            self.pos_x = float(x)
        if y is not None:
            self.pos_y = float(y)
        if z is not None:
            sort_parent = self.pos_z != float(z)
            self.pos_z = float(z)
        self.position(self.pos_x, self.pos_y, self.pos_z)
        if sort_parent:
            parent = self.parent_slide if self.parent_slide is not None else self.parent
            parent.sort_slides()

    @osc_property('position_x', 'pos_x')
    def set_position_x(self, x):
        self.set_position(x, None, None)

    @osc_property('position_y', 'pos_y')
    def set_position_y(self, y):
        self.set_position(None, y, None)

    @osc_property('position_z', 'pos_z')
    def set_position_z(self, z):
        self.set_position(None, None, z)

    @osc_property('scale', 'sx', 'sy')
    def set_scale(self, sx, sy):
        """
        Scaling
        """
        self.sx = float(sx)
        self.sy = float(sy)
        self.scale(sx * self.init_scale, sy * self.init_scale, 1.0)

    @osc_property('zoom', 'sx')
    def set_zoom(self, zoom):
        """
        Scaling relative to initial size, aka zoom
        """
        self.set_scale(zoom, zoom)

    @osc_property('rotate', 'rx', 'ry', 'rz')
    def set_rotate(self, rx, ry, rz):
        """
        Set the rotation of the slide
        """

        if rx is not None:
            self.rx = float(rx)
            self.rotateToX(self.rx)
        if ry is not None:
            self.ry = float(ry)
            self.rotateToY(self.ry)
        if rz is not None:
            self.rz = float(rz)
            self.rotateToZ(self.rz)

    @osc_property('rotate_x', 'rx')
    def set_rotate_x(self, rx):
        self.set_rotate(rx, None, None)

    @osc_property('rotate_y', 'ry')
    def set_rotate_y(self, ry):
        self.set_rotate(None, ry, None)

    @osc_property('rotate_z', 'rz')
    def set_rotate_z(self, rz):
        self.set_rotate(None, None, rz)

class Slide(State, Perspective, Video, Gif, SlideBase):

    def __init__(self, *args, **kwargs):

        super(Slide, self).__init__(*args, **kwargs)

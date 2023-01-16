# encoding: utf-8

import pi3d
import colorsys
import random

from ..slides.state import State
from ..slides.effect import Effect
from ..slides.animation import Animable
from ..slides.perspective import Perspective
from ..slides.gif import Gif
from ..slides.video import Video
from ..slides.mesh import Mesh
from ..slides.warp import Warp
from ..slides.group import Group
from ..engine.osc import OscNode, osc_property, osc_method

import logging
LOGGER = logging.getLogger(__name__)

V_ALIGN = {
    'C': 'center',
    'B': 'bottom',
    'T': 'top'
}

H_ALIGN ={
    'C': 'center',
    'L': 'left',
    'R': 'right'
}

class SlideBase(OscNode, Effect, Animable, Mesh):

    def __init__(self, parent, name, texture, width=None, height=None, init_z=0.0, mesh_size=[1,1]):

        if type(texture) is str:

            texture = pi3d.Texture(texture, flip=True)

        super(SlideBase, self).__init__(w=width if width is not None else texture.ix, h=height if height is not None else texture.iy, mesh_size=mesh_size)

        self.name = name
        self.parent = parent
        self.server = parent.server
        self.parent_slide = None

        self.is_clone = False
        self.clone_target = None

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
        self.pos_z = self.init_z = self.last_z = init_z

        # Position offest
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.offset_z = 0.0

        # Alignment
        self.h_align = 'center'
        self.v_align = 'center'

        # Scale
        self.init_scale = min(self.parent.width / self.width, self.parent.height / self.height)
        self.sx = 1.0
        self.sy = 1.0

        # Rotate
        self.rx = 0.0
        self.ry = 0.0
        self.rz = 0.0

        # texture tiling
        self.tiles = [1.0, 1.0]
        self.texture_offset= [0.0, 0.0]

        self.loaded = False
        self.grouped = False

        # init
        self.set_zoom(1.0)
        self.set_position_z(self.pos_z)

    def draw(self, *args, **kwargs):
        """
        Main drawing function
        """

        if self.get_is_visible():

            if self.color_strobe > 0:
                rgb = list(colorsys.hsv_to_rgb(random.random(), 1.0, 1.0))
                rgb[random.randint(0,2)] *= self.color_strobe
                self.set_material(rgb)

            if not self.loaded:
                self.loaded = True
                if not self.parent.monitor.alloc(self):
                    return

            super(SlideBase, self).draw(*args, **kwargs)

    @osc_method('quit_group')
    def quit_group(self):
        """
        Quit current group (if part of one)
        """
        if self.parent_slide:
            self.parent_slide.children.remove(self)
            self.set_position_z(self.pos_z + self.parent_slide.init_z)
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

    def position(self, x, y, z):
        """
        Override Shape.position to take text alignment into account
        """
        offx = 0
        if self.h_align != 'center':
            offx = (self.parent.width - self.width * self.sx * self.init_scale) / 2.0
        if self.h_align == 'left':
            offx *= -1

        offy = 0
        if self.v_align != 'center':
            offy = (self.parent.height - self.height * self.sy * self.init_scale) / 2.0
        if self.v_align == 'bottom':
            offy *= -1

        super(SlideBase, self).position(x * self.parent.width  + offx, y * self.parent.height + offy, z)

    @osc_property('mesh_size', 'mesh_size')
    def set_mesh_size(self, x, y):
        """
        mesh definition (number of tiles on the x and y-axis)
        """
        new_size = [abs(int(x)), abs(int(y))]
        if new_size != self.mesh_size:
            self.mesh_size = new_size
            self.create_mesh_buffer()

    @osc_property('mesh_debug', 'mesh_debug')
    def set_mesh_wireframe(self, debug):
        """
        wireframe mode (0|1)
        """
        self.mesh_debug = int(bool(debug))
        self.set_mesh_debug(self.mesh_debug)

    @osc_property('tiles', 'tiles')
    def set_tiles(self, x, y):
        """
        texture tiling (normalized)
        """
        if x is not None:
            self.tiles[0] = float(x)
        if y is not None:
            self.tiles[1] = float(y)

        for b in self.buf:
            b.unib[6] = self.tiles[0]
            b.unib[7] = self.tiles[1]

        self.set_texture_offset(None, None)

    @osc_property('texture_offset', 'texture_offset')
    def set_texture_offset(self, x, y):
        """
        texture offset (normalized)
        """
        if x is not None:
            self.texture_offset[0] = float(x)
        if y is not None:
            self.texture_offset[1] = float(y)
        # call pi3d set_offset, not to be confused with our position offset
        super(SlideBase, self).set_offset((self.texture_offset[0] + (1-self.tiles[0])/2, self.texture_offset[1] + (1-self.tiles[1])/2.))

    @osc_property('visible', 'visible')
    def set_visible(self, visible):
        """
        object visibility (0|1)
        """
        self.visible = int(bool(visible))

    def get_is_visible(self):
        """
        return True if slide is actually visible
        checks parent slides (groups) visiblity
        """
        if not self.visible:
            return False

        if self.parent_slide is not None and not self.parent_slide.get_is_visible():
            return False

        return True

    @osc_property('color', 'color')
    def set_color(self, r, g, b):
        """
        rgb balance (0<>1)
        """
        self.color = [float(r), float(g), float(b)]
        self.set_material(self.color)

    @osc_property('alpha', 'color_alpha')
    def set_color_alpha(self, alpha):
        """
        object opacity (0<>1)
        """
        self.color_alpha = float(alpha)
        self.set_alpha(self.color_alpha)


    @osc_property('color_strobe', 'color_strobe')
    def set_color_strobe(self, strobe):
        """
        random color strobing (0|1)
        """
        self.color_strobe = float(strobe)
        if strobe <= 0:
            self.set_color(*self.color)

    @osc_property('align', 'h_align', 'v_align')
    def set_align(self, h, v):
        """
        horizontal and vertical alignment (center|left|right, center|top|bottom)
        """
        h = h[0].upper()
        v = v[0].upper()
        reverse = False

        if h == v and h == 'C':
            self.set_h_align('center')
            self.set_v_align('center')
            return

        if (v != 'C' and v in H_ALIGN) or (h != 'C' and h in V_ALIGN):
            # invert args
            a = v
            v = h
            h = a

        if h in H_ALIGN and H_ALIGN[h] != self.h_align:
            self.set_h_align(h)
        if v in V_ALIGN and V_ALIGN[v] != self.v_align:
            self.set_v_align(v)

    @osc_property('align_h', 'h_align', shorthand=True)
    def set_h_align(self, align):
        """
        horizontal alignment (center|left|right)
        """
        align = H_ALIGN[str(align)[0].upper()]

        if align != self.h_align:
            self.h_align = align
            self.set_position(self.pos_x, self.pos_y, None)

    @osc_property('align_v', 'v_align', shorthand=True)
    def set_v_align(self, align):
        """
        vertical alignment (center|top|bottom)
        """
        align = V_ALIGN[str(align)[0].upper()]

        if align != self.v_align:
            self.v_align = align
            self.set_position(self.pos_x, self.pos_y, None)

    @osc_property('position', 'pos_x', 'pos_y', 'pos_z')
    def set_position(self, x, y, z):
        """
        object xyz position, relative to alignment (0<>1)
        """
        sort_parent = False
        if x is not None:
            self.pos_x = float(x)
        if y is not None:
            self.pos_y = float(y)
        if z is not None:
            self.pos_z = float(z)

        z_changed = self.last_z != self.pos_z + self.offset_z

        self.position(self.pos_x + self.offset_x, self.pos_y + self.offset_y, self.pos_z + self.offset_z)

        if z_changed:
            self.last_z = self.pos_z + self.offset_z
            parent = self.parent_slide if self.parent_slide is not None else self.parent
            parent.sort_slides()

    @osc_property('position_x', 'pos_x', shorthand=True)
    def set_position_x(self, x):
        """
        object x position (0<>1, bottom to top)
        """
        self.set_position(x, None, None)

    @osc_property('position_y', 'pos_y', shorthand=True)
    def set_position_y(self, y):
        """
        object y position (0<>1, left to right)
        """
        self.set_position(None, y, None)

    @osc_property('position_z', 'pos_z', shorthand=True)
    def set_position_z(self, z):
        """
        object z position (near to far)
        """
        self.set_position(None, None, z)

    @osc_property('offset', 'offset_x', 'offset_y', 'offset_z')
    def set_position_offset(self, x, y, z):
        """
        object xyz offset relative to position (0<>1)
        """
        if x is not None:
            self.offset_x = float(x)
        if y is not None:
            self.offset_y = float(y)
        if z is not None:
            self.offset_z = float(z)

        self.set_position(None, None, None)

    @osc_property('offset_x', 'offset_x', shorthand=True)
    def set_position_offset_x(self, x):
        """
        object x-axis offset (0<>1, bottom to top)
        """
        self.set_position_offset(x, None, None)

    @osc_property('offset_y', 'offset_y', shorthand=True)
    def set_position_offset_y(self, y):
        """
        object y-axis offset (0<>1, left to right)
        """
        self.set_position_offset(None, y, None)

    @osc_property('offset_z', 'offset_z', shorthand=True)
    def set_position_offset_z(self, z):
        """
        object z-axis offset (near to far)
        """
        self.set_position_offset(None, None, z)


    @osc_property('scale', 'sx', 'sy')
    def set_scale(self, sx, sy):
        """
        object xy scaling
        """
        self.sx = float(sx)
        self.sy = float(sy)
        self.scale(sx * self.init_scale, sy * self.init_scale, 1.0)
        if self.h_align != 'C' or self.v_align != 'C':
            self.position(self.pos_x, self.pos_y, self.pos_z)

    @osc_property('zoom', 'sx', shorthand=True)
    def set_zoom(self, zoom):
        """
        object scaling (scale shorthand)
        """
        self.set_scale(zoom, zoom)

    @osc_property('rotate', 'rx', 'ry', 'rz')
    def set_rotate(self, rx, ry, rz):
        """
        object rotation around xyz axis (deg)
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

    @osc_property('rotate_x', 'rx', shorthand=True)
    def set_rotate_x(self, rx):
        """
        object rotation around x axis (deg)
        """
        self.set_rotate(rx, None, None)

    @osc_property('rotate_y', 'ry', shorthand=True)
    def set_rotate_y(self, ry):
        """
        object rotation around y axis (deg)
        """
        self.set_rotate(None, ry, None)

    @osc_property('rotate_z', 'rz', shorthand=True)
    def set_rotate_z(self, rz):
        """
        object rotation around z axis (deg)
        """
        self.set_rotate(None, None, rz)

class Slide(State, Group, Perspective, Video, Gif, Warp, SlideBase):

    def __init__(self, *args, **kwargs):

        super(Slide, self).__init__(*args, **kwargs)

    def get_osc_path(self):
        return '/%s/slide/%s' % (self.parent.name, self.name)

    @osc_method('unload')
    def osc_unload(self):
        """
        Unload slide from memory
        """
        self.unload()

    @osc_method('remove')
    def osc_remove(self):
        """
        Remove slide object and all its children
        """
        self.parent.remove_slide(self)

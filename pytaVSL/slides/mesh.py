# encoding: utf-8

from pi3d.Shape import Shape
from pi3d.Buffer import Buffer
from pi3d.constants import GL_TRIANGLES, GL_LINE_LOOP

class Mesh(Shape):
    """
    One-sided mesh (use opengles.glDisable(GL_CULL_FACE) to enable backface)
    """
    def __init__(self, camera=None, light=None, w=1.0, h=1.0, name="",
                             x=0.0, y=0.0, z=20.0,
                             rx=0.0, ry=0.0, rz=0.0,
                             sx=1.0, sy=1.0, sz=1.0,
                             cx=0.0, cy=0.0, cz=0.0, mesh_size=[1, 1]):
        """Uses standard constructor for Shape. Extra Keyword arguments:

            *w*
                Width.
            *h*
                Height.
            *mesh_size*
                [x, y] number of tiles in the mesh (2 triangles per tile)
        """
        super(Mesh, self).__init__(camera, light, name, x, y, z, rx, ry, rz,
                                                                 sx, sy, sz, cx, cy, cz)
        self.width = w
        self.height = h
        self.mesh_size = mesh_size
        self.mesh_debug = 0
        self.buf = []

        self.create_mesh_buffer()


    def create_mesh_buffer(self):

        ww = self.width / 2.0
        hh = self.height / 2.0
        nx, ny = self.mesh_size

        verts = []
        texcoords = []
        inds = []

        for x in range(nx + 1):
            for y in range(ny + 1):
                coords = (-ww + self.width / nx * x, hh - self.height / ny * y, 0.0)
                verts.append(coords)
                texcoords.append(((coords[0] + ww) / self.width, -(coords[1] - hh) / self.height))

        for y in range(ny):
            for x in range(nx):
                a = y + (ny + 1) * x
                b = a + 1
                c = y + (ny + 1) * (x + 1)
                inds.append((a, b, c))

                a = y + (ny + 1) * (x + 1)
                # b = b
                c = a + 1
                inds.append((a, b, c))

        # for wireframe mode
        topright = nx * (ny + 1)
        bottomright = (nx + 1) * (ny + 1) - 1
        inds.append((bottomright, topright, topright))

        new_buffer = Buffer(self, verts, texcoords, inds, None)

        if self.buf:
            old_buffer = self.buf[0]
            new_buffer.set_material(old_buffer.unib[3:6])
            new_buffer.set_textures(old_buffer.textures)
            new_buffer.shader = old_buffer.shader

        self.buf = [new_buffer]

        if self.mesh_debug:
            self.set_mesh_debug(self.mesh_debug)

    def set_mesh_debug(self, debug):
        self.buf[0].draw_method = GL_LINE_LOOP if self.mesh_debug else GL_TRIANGLES

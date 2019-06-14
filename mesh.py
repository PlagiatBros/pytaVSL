from pi3d.Shape import Shape
from pi3d.Buffer import Buffer

class Mesh(Shape):
  """
  One-sided mesh (use opengles.glDisable(GL_CULL_FACE) to enable backface)
  """
  def __init__(self, camera=None, light=None, w=1.0, h=1.0, name="",
               x=0.0, y=0.0, z=20.0,
               rx=0.0, ry=0.0, rz=0.0,
               sx=1.0, sy=1.0, sz=1.0,
               cx=0.0, cy=0.0, cz=0.0, tiles=[1, 1]):
    """Uses standard constructor for Shape. Extra Keyword arguments:

      *w*
        Width.
      *h*
        Height.
      *tiles*
        [x, y] number of tiles in the mesh (2 triangles per tile)
    """
    super(Mesh, self).__init__(camera, light, name, x, y, z, rx, ry, rz,
                                 sx, sy, sz, cx, cy, cz)
    self.width = w
    self.height = h

    ww = w / 2.0
    hh = h / 2.0

    nx, ny = tiles

    verts = []
    texcoords = []
    inds = []

    for x in range(nx + 1):
        for y in range(ny + 1):
            coords = (-ww + w / nx * x, hh - h / ny * y, 0.0)
            verts.append(coords)
            texcoords.append(((coords[0] + ww) / w, -(coords[1] - hh) / h))

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


    self.buf = [Buffer(self, verts, texcoords, inds, None)]
    self.buf[0].calc_normals()

    # self.set_line_width(2.0)
    # self.set_material((0.0, 1.0, 0.0))

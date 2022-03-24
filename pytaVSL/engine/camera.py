from .osc import OscNode, osc_property
from ..slides.animation import Animable
from ..slides.state import State

class FakeSlide():
    def draw(self):
        pass

class Camera(State,OscNode,Animable,FakeSlide):

    def __init__(self, name, parent):


        self.name = name
        self.parent = parent

        self.cameras = [self.parent.CAMERA, self.parent.CAMERA3D]
        self.height = self.parent.height


        # Position
        self.pos_x = 0.0
        self.pos_y = 0.0
        self.pos_z = 0.0
        self.init_z = 0.0

        # Rotate
        self.rx = 0.0
        self.ry = 0.0
        self.rz = 0.0

        super().__init__()

    def update(self):
        Animable.draw(self)

    def update_camera(self):
        for cam in self.cameras:
            cam.position([self.pos_x, self.pos_y, self.pos_z])
            cam.rotate(self.rx, self.ry, self.rz)
            cam.reset(scale=cam.scale)
            cam.was_moved = True

    @osc_property('position', 'pos_x', 'pos_y', 'pos_z')
    def set_position(self, x, y, z):
        """
        camera xyz position
        """
        if x is not None:
            self.pos_x = float(x)
        if y is not None:
            self.pos_y = float(y)
        if z is not None:
            self.pos_z = float(z)

        self.update_camera()

    @osc_property('position_x', 'pos_x', shorthand=True)
    def set_position_x(self, x):
        """
        camera x-offset
        """
        self.set_position(x, None, None)

    @osc_property('position_y', 'pos_y', shorthand=True)
    def set_position_y(self, y):
        """
        camera y-offset
        """
        self.set_position(None, y, None)

    @osc_property('position_z', 'pos_z', shorthand=True)
    def set_position_z(self, z):
        """
        camera z-axis offset (near to far)
        """
        self.set_position(None, None, z)


    @osc_property('rotate', 'rx', 'ry', 'rz')
    def set_rotate(self, rx, ry, rz):
        """
        camera rotation around xyz axis (deg)
        """
        if rx is not None:
            self.rx = float(rx)
        if ry is not None:
            self.ry = float(ry)
        if rz is not None:
            self.rz = float(rz)

        self.update_camera()

    @osc_property('rotate_x', 'rx', shorthand=True)
    def set_rotate_x(self, rx):
        """
        camera rotation around x axis (deg)
        """
        self.set_rotate(rx, None, None)

    @osc_property('rotate_y', 'ry', shorthand=True)
    def set_rotate_y(self, ry):
        """
        camera rotation around y axis (deg)
        """
        self.set_rotate(None, ry, None)

    @osc_property('rotate_z', 'rz', shorthand=True)
    def set_rotate_z(self, rz):
        """
        camera rotation around z axis (deg)
        """
        self.set_rotate(None, None, rz)

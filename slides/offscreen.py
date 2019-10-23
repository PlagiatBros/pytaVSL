"""
Derivated from pi3d.OffScreenTexture

Changes:
- remove depthbuffer & use GL_RGB instead of GL_DEPTH_COMPONENT16 because we don't need depth
- add OFFSCREEN_QUEUE to manage nested offscreen drawings
"""




import ctypes, time
import numpy as np

import pi3d
from pi3d.constants import (GL_FRAMEBUFFER, GL_RENDERBUFFER, GL_COLOR_ATTACHMENT0,
                                        GL_TEXTURE_2D, GL_DEPTH_COMPONENT16, GL_DEPTH_ATTACHMENT,
                                        GL_DEPTH_BUFFER_BIT, GL_COLOR_BUFFER_BIT, GLuint, GLsizei,
                                        GL_RGB)


from pi3d.Texture import Texture

OFFSCREEN_QUEUE = []

class OffScreenTexture(Texture):
    """For creating special effect after rendering to texture rather than
    onto the display. Used by Defocus, ShadowCaster, Clashtest etc
    """
    def __init__(self, name):
        """ calls Texture.__init__ but doesn't need to set file name as
        texture generated from the framebuffer
        """
        super(OffScreenTexture, self).__init__(name)
        from pi3d.Display import Display
        self.disp = Display.INSTANCE
        self.ix, self.iy = self.disp.width, self.disp.height
        self.image = np.zeros((self.iy, self.ix, 4), dtype=np.uint8)
        self.blend = False
        self.mipmap = False

        self._tex = GLuint()
        self.framebuffer = (GLuint * 1)()
        pi3d.opengles.glGenFramebuffers(GLsizei(1), self.framebuffer)

    def _load_disk(self):
        """ have to override this
        """

    def _start(self, clear=True):
        """ after calling this method all object.draw()s will rendered
        to this texture and not appear on the display. Large objects
        will obviously take a while to draw and re-draw
        """
        global OFFSCREEN_QUEUE
        if self not in OFFSCREEN_QUEUE:
            OFFSCREEN_QUEUE.append(self)

        self.disp.offscreen_tex = True # flag used in Buffer.draw()
        pi3d.opengles.glBindFramebuffer(GL_FRAMEBUFFER, self.framebuffer[0])
        pi3d.opengles.glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0,
                                GL_TEXTURE_2D, self._tex.value, 0)
        if clear:
            pi3d.opengles.glClear(GL_COLOR_BUFFER_BIT)


    def _end(self):
        """ stop capturing to texture and resume normal rendering to default
        """
        self.disp.offscreen_tex = False # flag used in Buffer.draw()
        pi3d.opengles.glBindTexture(GL_TEXTURE_2D, 0)
        pi3d.opengles.glBindFramebuffer(GL_FRAMEBUFFER, 0)

        global OFFSCREEN_QUEUE
        del OFFSCREEN_QUEUE[-1]
        if OFFSCREEN_QUEUE:
            OFFSCREEN_QUEUE[-1]._start(clear=False)


    def delete_buffers(self):
        pi3d.opengles.glDeleteFramebuffers(GLsizei(1), self.framebuffer)

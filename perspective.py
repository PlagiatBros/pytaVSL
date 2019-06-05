# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

from osc import osc_property

class Perspective(object):

    def __init__(self, *args, **kwargs):

        super(Perspective, self).__init__(*args, **kwargs)

        # perspective
        self.perspective = 0.0

    @osc_property('perspective', 'perspective')
    def set_perspective(self, perspective):
        """
        enable perspective (0|1)
        """
        self.perspective = int(bool(perspective))
        if self.perspective:
            self._camera = self.parent.CAMERA3D
        else:
            self._camera = self.parent.CAMERA
        # trigger matrix recalculation
        self.MFlg = True
        self.rozflg = True

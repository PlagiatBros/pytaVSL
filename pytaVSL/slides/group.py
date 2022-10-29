from ..engine.osc import osc_property

import logging
LOGGER = logging.getLogger(__name__)

class Group(object):

    def __init__(self, *args, **kwargs):

        self.is_group = False
        self.children_need_sorting = False

        self.is_sequence = 0
        self.sequence_index = 0
        self.sequence_normal_index = 0

        self.post_process = None

        super(Group, self).__init__(*args, **kwargs)

    def draw(self, *args, **kwargs):

        if self.visible:

            if self.children_need_sorting:
                self.children = sorted(self.children, key=lambda slide: slide.pos_z, reverse=True)
                self.children_need_sorting = False

                if self.is_sequence:
                    self.set_sequence_index(self.sequence_index)

            if self.is_group and self.active_effects:
                # capture children.draw()
                self.post_process.capture_start()

            super(Group, self).draw(*args, **kwargs)

            if self.is_group and self.active_effects:
                # stop capture
                self.post_process.capture_end()
                # copy shader uniforms
                self.post_process.unif[:] = self.unif[:]
                self.post_process.buf[0].unib[:] = self.buf[0].unib[:]
                self.post_process.unif_warp[:] = self.unif_warp[:]
                # draw
                if self.pos_z != self.post_process.pos_z:
                    self.post_process.position(self.post_process.pos_x, self.post_process.pos_y, self.pos_z)
                self.post_process.draw()

    def toggle_effect(self, *args, **kwargs):
        """
        override Effect.toggle_effect to copy shaders to group post_process
        """
        super(Group, self).toggle_effect(*args, **kwargs)

        if self.is_group and (self.active_effects or self.post_process):

            if not self.post_process:
                from ..slides.postprocess import PostProcess
                self.post_process = PostProcess(self.parent)
                self.post_process.set_visible(1)

            self.post_process.toggle_effect(*args, **kwargs)

            # MASK is a bit tricky
            #it has issues with scale
            # if self.effect_mask != self.post_process.effect_mask:
            #     self.post_process.set_effect_mask(self.effect_mask)
            # if len(self.buf[0].textures) == 2:
            #     del self.buf[0].textures[1]

            # same for warp
            # if self.warp != self.post_process.warp or (self.post_process.warp_1 != self.warp_1 or self.post_process.warp_2 != self.warp_2 or self.post_process.warp_3 != self.warp_3 or self.post_process.warp_4 != self.warp_4):
            #     self.post_process.warp_1 = self.warp_1
            #     self.post_process.warp_2 = self.warp_2
            #     self.post_process.warp_3 = self.warp_3
            #     self.post_process.warp_4 = self.warp_4
            #     self.post_process.toggle_warp_effect()

    def add_child(self, child):
        """
        Override add_child to handle z-sorting
        """
        super(Group, self).add_child(child)
        child.set_position_z(child.pos_z - self.pos_z)
        self.children_need_sorting = True

    @osc_property('sequence_mode', 'is_sequence')
    def set_sequence_mode(self, mode):
        """
        sequence mode (0=disabled, 1=enabled)
        """
        if self.children:
            self.is_sequence = int(bool(mode))

    @osc_property('sequence_index', 'sequence_index')
    def set_sequence_index(self, index):
        """
        currently visible child by index (z-sorted)
        """
        if self.is_sequence and self.children:
            for c in self.children:
                c.set_visible(0)
            index = int(index) % len(self.children)
            self.sequence_index = index
            self.children[index].set_visible(1)

    @osc_property('sequence_position', 'sequence_normal_index', shorthand=True)
    def set_sequence_normal_index(self, index):
        """
        relative sequence position, normalized index (0<>1)
        """
        if self.children:
            self.sequence_normal_index = max(0, min(float(index), 1))
            if self.sequence_normal_index == 1:
                self.set_sequence_index(len(self.children) - 1)
            else:
                self.set_sequence_index(int(self.sequence_normal_index * len(self.children)))

from osc import osc_property

import logging
LOGGER = logging.getLogger(__name__)

class Group(object):

    def __init__(self, *args, **kwargs):

        self.is_group = False
        self.children_need_sorting = False

        self.sequence_index = None
        self.sequence_normal_index = None

        super(Group, self).__init__(*args, **kwargs)

    def draw(self, *args, **kwargs):

        if self.visible:

            if self.children_need_sorting:
                self.children = sorted(self.children, key=lambda slide: slide.z(), reverse=True)
                self.children_need_sorting = False

            super(Group, self).draw(*args, **kwargs)

    @osc_property('sequence_index', 'sequence_index')
    def set_sequence_index(self, index):
        """
        currently visible child by index (z-sorted)
        """
        if index is not None and self.children:
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
            self.sequence_normal_index = float(index)
            if self.sequence_normal_index < 0 or self.sequence_normal_index > 1:
                self.sequence_normal_index = self.sequence_normal_index % 1

            self.set_sequence_index(int(self.sequence_normal_index * (len(self.children) - 1)))

# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

from osc import osc_method

import logging
LOGGER = logging.getLogger(__name__)

RESET_STATES = {}

class State(object):

    def __init__(self, *args, **kwargs):

        super(State, self).__init__(*args, **kwargs)

        self.osc_states = {}

        if type(self).__name__ not in RESET_STATES:
            RESET_STATES[type(self).__name__] = self.state_get()

    def state_get(self):
        state = {}
        for name in self.osc_attributes:
            state[name] = self.osc_get_value(name)
        return state

    def state_set(self, state):
        for name in state:
            self.osc_set(name, *state[name])

    @osc_method('reset')
    def state_reset(self):
        self.state_set(RESET_STATES[type(self).__name__])
        self.stop_strobe()
        self.stop_animate()

    @osc_method('save')
    def state_save(self, name="quicksave"):
        if not name:
            self.osc_quickstate = self.state_get()
        else:
            self.osc_states[name] = self.state_get()

    @osc_method('recall')
    def state_recall(self, name="quicksave"):
        if name in self.osc_states:
            state = self.osc_states[name]
            self.state_set(state)
            self.stop_animate()
            self.stop_strobe()
            # TODO we could serialize strobes and anim to recall them ?
        else:
            LOGGER.error('no state "%s" in %s' % (name, self.name))
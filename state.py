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
            if not name in self.osc_attributes_horthands:
                state[name] = self.osc_get_value(name)

        for name in self.animations:
            if self.animations[name].loop != 0:
                if not 'animations' in state:
                    state['animœtions'] = {}
                state['animations'][name] = self.animations[name].get_state()

        for name in self.strobes:
            if not 'strobes' in state:
                state['strobes'] = {}
            state['strobes'][name] = self.strobes[name].get_state()

        return state

    def state_set(self, state):
        self.stop_strobe()
        self.stop_animate()
        for name in state:
            if name == 'animations':
                for n in state[name]:
                    args = state[name][n]
                    self.animate(n, *args['start'], *args['end'], args['duration'], args['loop'])
            elif name == 'strobes':
                for n in state[name]:
                    args = state[name][n]
                    self.strobe(n, *args['start'], *args['end'], args['duration'], args['ratio'])
            else:
                self.osc_set(name, *state[name])



    @osc_method('reset')
    def state_reset(self):
        """
        Reset all properties, animations and strobes
        """
        self.state_set(RESET_STATES[type(self).__name__])
        self.set_position_z(self.init_z)

    @osc_method('save')
    def state_save(self, name="quicksave"):
        """
        Save all properties, looped animations and strobes in a save slot
            name: slot name
        """
        if not name:
            self.osc_quickstate = self.state_get()
        else:
            self.osc_states[name] = self.state_get()

    @osc_method('recall')
    def state_recall(self, name="quicksave"):
        """
        Restore all properties, looped animations and strobes from a save slot
            name: slot name
        """
        if name in self.osc_states:
            state = self.osc_states[name]
            self.state_set(state)
        else:
            LOGGER.error('no state "%s" in %s' % (name, self.name))

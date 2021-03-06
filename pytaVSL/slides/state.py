# encoding: utf-8

from ..engine.osc import osc_method
from ..engine.scenes import tomlencoder

import toml
import logging
LOGGER = logging.getLogger(__name__)

RESET_STATES = {}

class State(object):

    def __init__(self, *args, **kwargs):

        super(State, self).__init__(*args, **kwargs)

        self.osc_states = {}

        if type(self).__name__ not in RESET_STATES:
            RESET_STATES[type(self).__name__] = self.state_get()

            # Text exception
            if type(self).__name__ == 'Text':
                 RESET_STATES[type(self).__name__]['color'] = [1.0, 1.0, 1.0]
                 del RESET_STATES[type(self).__name__]['mesh_size']
                 del RESET_STATES[type(self).__name__]['mesh_debug']

    def state_get(self):
        state = {}
        for name in self.osc_attributes:
            if not name in self.osc_attributes_horthands:
                state[name] = self.osc_get_value(name)

        for name in self.animations:
            if self.animations[name].loop != 0:
                if not 'animations' in state:
                    state['animations'] = {}
                state['animations'][name] = self.animations[name].get_state()

        for name in self.strobes:
            if not 'strobes' in state:
                state['strobes'] = {}
            state['strobes'][name] = self.strobes[name].get_state()

        return state

    def state_set(self, new_state=None, reset=False):
        if new_state is None:
            new_state = {}
        if reset:
            state = {}
            state.update(RESET_STATES[type(self).__name__])
            state['position'][2] = self.init_z
            state.update(new_state)
        else:
            state = new_state

        self.stop_strobe()
        self.stop_animate()
        for name in state:
            if name == 'animations':
                for n in state[name]:
                    args = state[name][n]
                    self.animate(n, *args['from'], *args['to'], *args['duration'], *args['loop'], *args['easing'])
            elif name == 'strobes':
                for n in state[name]:
                    args = state[name][n]
                    self.strobe(n, *args['from'], *args['to'], *args['duration'], *args['ratio'])
            else:
                self.osc_set(name, *state[name])



    @osc_method('reset')
    def state_reset(self):
        """
        Reset all properties, animations and strobes
        """
        self.state_set(None, reset=True)

    @osc_method('save')
    def state_save(self, name="quicksave"):
        """
        Save all properties, looped animations and strobes in a save slot
            name: slot name
        """
        name = str(name).lower()
        self.osc_states[name] = self.state_get()

    @osc_method('recall')
    def state_recall(self, name="quicksave"):
        """
        Restore all properties, looped animations and strobes from a save slot
            name: slot name
        """
        name = str(name).lower()
        if name in self.osc_states:
            state = self.osc_states[name]
            self.state_set(state)
        else:
            LOGGER.error('no state "%s" in %s' % (name, self.name))

    @osc_method('log')
    def state_log(self, property=None):
        """
        Print object's state in the console
            property: name of the property to display (all when omitted)
        """
        if property is None:
            state = self.state_get()
        elif property in self.osc_attributes:
            state = {}
            state[property] = self.osc_get_value(property)
        else:
            LOGGER.error('invalid property argument "%s" for %s/log' % (property, self.get_osc_path()))
            return

        print(self.get_osc_path() + '/log')
        print('  ' + toml.dumps(state, tomlencoder).replace(',]', ' ]').replace('\n', '\n  ').strip())

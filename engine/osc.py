# encoding: utf-8

import logging
from inspect import getmembers, getargspec

from config import *

LOGGER = logging.getLogger(__name__)

class osc_method():
    """
    Decorator for exposing class methods to osc
    """
    def __init__(self, alias):

        if alias[0] == '/':
            alias = alias[1:]
        if alias[-1] == '/':
            alias = alias[:-1]

        self.alias = alias.lower()

    def __call__(self, method):

        if not hasattr(method, 'osc_method_aliases'):
            method.osc_method_aliases = []

        method.osc_method_aliases.append(self.alias)
        method.osc_argcount = method.__code__.co_argcount - 1
        method.osc_argcount_min = method.osc_argcount if not method.__defaults__ else method.osc_argcount - len(method.__defaults__)
        method.osc_varargs = getargspec(method).varargs

        return method

class osc_property():
    """
    Decorator for exposing class attributes to osc set
    """
    def __init__(self, alias, *attributes, shorthand=False):

        self.osc_setter_alias = alias
        self.osc_getter_attributes = attributes
        self.shorthand = shorthand

    def __call__(self, method):

        method.osc_attribute = True
        method.osc_setter_alias = self.osc_setter_alias
        method.osc_getter_attributes = self.osc_getter_attributes
        method.osc_argcount = method.__code__.co_argcount - 1
        method.osc_argcount_min = method.osc_argcount if not method.__defaults__ else method.osc_argcount - len(method.__defaults__)
        method.shorthand = self.shorthand

        return method

class OscNode(object):

    def __init__(self, *args, **kwargs):

        super(OscNode, self).__init__(*args, **kwargs)

        self.osc_methods = {}
        self.osc_attributes = {}
        self.osc_state = {}
        self.osc_attributes_horthands = []

        for name, method in getmembers(self):

            if hasattr(method, 'osc_method_aliases'):
                for alias in method.osc_method_aliases:
                    self.osc_methods[alias] = method

            if hasattr(method, 'osc_attribute'):
                self.osc_attributes[method.osc_setter_alias] = method
                if method.shorthand:
                    self.osc_attributes_horthands.append(method.osc_setter_alias)

    def get_osc_path(self):
        return ''

    def osc_get_value(self, attribute):
        if attribute in self.osc_attributes:
            method = self.osc_attributes[attribute]
            value = [getattr(self, x) for x in method.osc_getter_attributes]
            flat = []
            for x in value:
                if type(x) is list:
                    for y in x:
                        flat.append(y)
                else:
                    flat.append(x)

            return flat
        else:
            return None


    def osc_parse_value(self, value, current):

        if isinstance(value, str) and len(value) > 1:
            operator = value[0]
            if operator == '+' or operator == '-':
                return current + float(value)
            elif operator == '*':
                return current * float(value[1:])
            elif operator == '/':
                return current / float(value[1:])

        return value

    @osc_method('set')
    def osc_set(self, property, *value):
        """
        Set a property
            property: exposed osc property
            value: new value (items with default values can be omitted)
        """
        attribute = str(property).lower()
        if attribute in self.osc_attributes:
            method = self.osc_attributes[attribute]
            argcount = method.osc_argcount
            argcount_min = method.osc_argcount_min

            if len(value) > argcount or len(value) < argcount_min:
                if method.osc_argcount_min == argcount:
                    LOGGER.error('bad number of argument for %s/set %s (%i expected, %i provided)' % (self.get_osc_path(), attribute, argcount, len(value)))
                else:
                    LOGGER.error('bad number of argument for %s/set %s (%i to %i, expected, %i provided)' % (self.get_osc_path(), attribute, argcount_min, argcount, len(value)))
                return

            current = self.osc_get_value(attribute)
            if current is not None:
                value = list(value)
                value[:argcount_min] = [self.osc_parse_value(value[i], current[i]) for i in range(argcount_min)]

            method(*value)

            self.property_changed(attribute)

        else:
            LOGGER.error('invalid property argument "%s" for %s/set' % (attribute, self.get_osc_path()))

    def property_changed(self, name):
        """
        Property changed callback
        """
        pass

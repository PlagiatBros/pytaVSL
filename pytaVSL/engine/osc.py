# encoding: utf-8

import liblo
import logging
from inspect import getmembers, getargspec

LOGGER = logging.getLogger(__name__)

def normalize_osc_port(port):

    if str(port).isdigit():
        port = 'osc.udp://127.0.0.1:' + str(port)
    elif type(port) is str and '://' not in port:
        port = 'osc.udp://' + port

    try:
        test = liblo.Address(port)
    except:
        LOGGER.error('invalid osc port %s' % port)
        port = None

    return port

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
        self.osc_subscribes = {}

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
                if argcount == 0:
                    # read-only
                    pass
                elif method.osc_argcount_min == argcount:
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


    @osc_method('get')
    def osc_get(self, property, return_port):
        """
        Send property's current value to return_port at /slide_address/get/reply
            property: exposed osc property, '*' for all properties
            return_port: port number, ip:port string, or valid full osc address
        """

        return_port = normalize_osc_port(return_port)

        if return_port is None:
            LOGGER.error('invalid return_port argument "%s" for %s/subscribe' % (return_port, self.get_osc_path()))
            return

        if property == '*':
            for p in self.osc_attributes:
                self.osc_get(p, return_port)
            self.server.send(return_port, self.get_osc_path() + '/get/reply/end')
        elif property in self.osc_attributes:
            address = self.get_osc_path() + '/get/reply'
            self.server.send(return_port, address, property, *self.osc_get_value(property))
        else:
            LOGGER.error('invalid property argument "%s" for %s' % (property, address))

    @osc_method('ping')
    def osc_ping(self,  return_port):
        """
        Reply to return_port at /slide_address/ping/reply
        """

        return_port = normalize_osc_port(return_port)

        if return_port is None:
            LOGGER.error('invalid return_port argument "%s" for %s/ping' % (return_port, self.get_osc_path()))
            return

        address = self.get_osc_path() + '/ping/reply'
        self.server.send(return_port, address)

    @osc_method('subscribe')
    def osc_subscribe(self, property, return_port):
        """
        Subscribe to property's updates and send them to return_port at /slide_address/subscribe/update
            property: exposed osc property
            return_port: (optional) port number, ip:port string, or valid full osc address
        """

        if property not in self.osc_attributes:
            LOGGER.error('invalid property argument "%s" for %s/subscribe' % (property, self.get_osc_path()))
            return

        return_port = normalize_osc_port(return_port)

        if return_port is None:
            LOGGER.error('invalid return_port argument "%s" for %s/subscribe' % (property, self.get_osc_path()))
            return

        if property not in self.osc_subscribes:
            self.osc_subscribes[property] = {}

        if return_port not in self.osc_subscribes[property]:
            value = self.osc_get_value(property)[:]
            self.osc_subscribes[property][return_port] = value
            address = self.get_osc_path() + '/subscribe/update'
            self.server.send(return_port, address, property, *value)


    @osc_method('unsubscribe')
    def osc_unsubscribe(self, property, *return_port):
        """
        Unsubscribe from property's updates
            property: exposed osc property
            return_port: (optional) port number, ip:port string, or valid full osc address
                         if omitted, applies to all registered ports
        """

        if property not in self.osc_attributes:
            LOGGER.error('invalid property argument "%s" for %s/unsubscribe' % (property, self.get_osc_path()))
            return

        if len(return_port) == 0 and property in self.osc_subscribes:

            del self.osc_subscribes[property]

        elif len(return_port) > 0 and property in self.osc_subscribes:

            return_port = normalize_osc_port(return_port[0])

            if return_port is None:
                LOGGER.error('invalid return_port argument "%s" for %s/unsubscribe' % (return_port, self.get_osc_path()))
                return

            if return_port in self.osc_subscribes[property]:
                del self.osc_subscribes[property][return_port]

    def osc_feed_subscribers(self):

        for property in self.osc_subscribes:
            self.osc_feed_subscribers_property(property)

    def osc_feed_subscribers_property(self, property):

        if property in self.osc_subscribes:
            value = self.osc_get_value(property)[:]
            address = self.get_osc_path() + '/subscribe/update'
            for return_port in self.osc_subscribes[property]:
                if value != self.osc_subscribes[property][return_port]:
                    self.osc_subscribes[property][return_port] = value
                    self.server.send(return_port, address, property, *value)

    def property_changed(self, property):
        """
        Property changed callback
        """
        pass

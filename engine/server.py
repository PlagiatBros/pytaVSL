# encoding: utf-8

from osc import *

import liblo
import re
import logging
LOGGER = logging.getLogger(__name__)

def osc_to_regexp_transliteration(match):
    s = match.group(0)
    s = s.replace("{","(")
    s = s.replace("}",")")
    s = s.replace(",","|")
    return s

osc_to_regexp_re = re.compile(r"\{[^\}]*\}")

osc_to_regexp_patterns = {
    r"\?": ".",
    r"\*": ".*",
    r"\[!([^\]]*)\]": r"[^\1]",
    r"\$": r"\$",
    r"\^": r"\^",
    r"\\": r"\\"
}

def osc_to_regexp(address):
    """
    Convert OSC 1.1 compliant address to regexp pattern standards
    Escape ^, $ (start/end of string delimiters) and \ (escape char)
    ?           -> .?
    [!a-Z]      -> [^a-Z]
    {foo,bar}   -> (foo|bar)

    Params:
    address : str

    Borrowed from pyoChainsaw @ https://framagit.org/groolot-association/pyoChainsaw
    Copyleft Gregory David & JE Doucet (GNU GPLv3)
    """

    for pattern, repl in osc_to_regexp_patterns.items():
        address = re.sub(pattern, repl, address)

    return re.compile("^" + re.sub(osc_to_regexp_re, osc_to_regexp_transliteration, address) + "$")


class OscServer(OscNode):

    def __init__(self, name, port, *args, **kwargs):

        super(OscServer, self).__init__(*args, **kwargs)

        self.name = name.lower()

        self.server = liblo.Server(port)
        self.server.add_method(None, None, self.route_osc)

    def stop(self):

        self.server.free()
        self.server = None

    def get_osc_path(self):
        return '/%s' % self.name

    def get_children(self, store, name):

        children = []

        if name == '-1':
            return list(store.values())
        else:
            name = str(name)
            if name in store:
                children.append(store[name])
            elif '{' in name or '[' in name or '*' in name:
                regexp = osc_to_regexp(name)
                for name in store:
                    match = regexp.match(name)
                    if match != None and len(match.string) > 0:
                        children.append(store[name])

        return children


    def route_osc(self, path, args):

        address = path

        if path[-1] != '/':
            path += '/'

        path = path[1:].lower().split('/')

        target = None
        cmd = None

        if path.pop(0) != self.name:
            LOGGER.debug('ignored message %s %s' % (address, args))
            return

        if path[0] == 'slide':
            target = self.get_children(self.slides, path[1])
            cmd = path[2]
        elif path[0] == 'post_process':
            target = [self.post_process]
            cmd = path[1]
        elif path[0] == 'text':
            target = self.get_children(self.texts, path[1])
            cmd = path[2]
        else:
            target = [self]
            cmd = path[0]

        if not target:
            LOGGER.error("no target match for %s" % address)

        for t in target:

            if cmd in t.osc_methods:

                method = t.osc_methods[cmd]
                argcount = method.osc_argcount
                argcount_min = method.osc_argcount_min

                if len(args) >= argcount_min and len(args) <= argcount:
                    method(*args[:argcount])
                elif method.osc_varargs:
                    method(*args)
                else:
                    LOGGER.error('bad number of argument for %s (%i expected, %i provided)' % (address, argcount, len(args)))

            else:
                LOGGER.error('no matching method for %s' % address)


    def print_api(self, obj=None):

        import inspect
        def get_class_that_defined_method(meth):
            if inspect.ismethod(meth):
                for cls in inspect.getmro(meth.__self__.__class__):
                   if cls.__dict__.get(meth.__name__) is meth:
                        return cls
                meth = meth.__func__  # fallback to __qualname__ parsing
            if inspect.isfunction(meth):
                cls = getattr(inspect.getmodule(meth),
                              meth.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0])
                if isinstance(cls, type):
                    return cls
            return getattr(meth, '__objclass__', None)  # handle special descriptor objects


        try:
            get_class_that_defined_method(self.print_api)
        except:
            LOGGER.error('python3 is required to print the API')
            return

        def alpha_sort(obj):
            classes = [get_class_that_defined_method(x).__name__ for x in obj.values()]
            keys = list(obj.keys())
            out = {}
            for i in range(len(keys)):
                if classes[i] not in out:
                    out[classes[i]] = []
                out[classes[i]].append(keys[i])
            for c in out:
                out[c] = sorted(out[c], key=lambda item: (int(item.partition(' ')[0]) if item[0].isdigit() else float('inf'), item))

            return out


        colors = {
            'BLUE': '\033[94m',
            'GREEN': '\033[92m',
            'ITALIC': '\033[3m',
            'YELLOW': '\033[93m',
            'RED': '\033[91m',
            'TEAL': '\033[36m',
            'BROWN': '\033[33m',
            'ENDC': '\033[0m',
            'BOLD': '\033[1m',
            'UNDERLINE': '\033[4m'
        }
        def printc(indent, s, *c):
            for line in s.split('\n'):
                print("  " * indent + "".join([colors[x.upper()] for x in c]) + line + colors['ENDC'])

        def print_methods(prefix, obj):

            printc(1, '\nExposed methods:\n', 'italic')

            if not obj.osc_methods:
                print('    None')

            methods = alpha_sort(obj.osc_methods)
            for c in methods:
                printc(1, '(from %s)\n' % c, 'brown')

                for name in methods[c]:
                    method = obj.osc_methods[name]
                    spec = getargspec(method)
                    args = spec.args[1:]
                    if spec.defaults:
                        l = len(spec.defaults)
                        for i in range(l):
                            d = spec.defaults[i] if type(spec.defaults[i]) != str else '"%s"' % spec.defaults[i]
                            args[i - l] = "%s=%s" % (args[i - l], d)
                    if spec.varargs:
                        args += ["[%s ...]" % spec.varargs]
                    args = " ".join(args)

                    print('  %s%s %s' % (prefix, name, args))
                    printc(1, method.__doc__.replace('    ', '  '), 'blue')

        def print_properties(obj):

            printc(1, '\nExposed properties:\n', 'italic')

            if not obj.osc_attributes:
                print('    None\n')


            methods = alpha_sort(obj.osc_attributes)
            for c in methods:
                printc(1, '(from %s)\n' % c, 'brown')

                for name in methods[c]:
                    method = obj.osc_attributes[name]
                    spec = getargspec(method)
                    args = spec.args[1:]
                    if spec.defaults:
                        l = len(spec.defaults)
                        for i in range(l):
                            d = spec.defaults[i] if type(spec.defaults[i]) != str else '"%s"' % spec.defaults[i]
                            args[i - l] = "%s=%s" % (args[i - l], d)
                    args = ", ".join(args)
                    print('    %s [%s]' % (name, args))
                    printc(3, '\n' + method.__doc__.replace('    ', '  ').strip(), 'blue')
                    printc(3, 'init: %s\n' % str(obj.osc_get_value(name)).replace("'", '"'), 'teal')

        printc(0, '\nPytaVSL: OSC API', 'teal', 'bold')
        printc(0, '\nMethod paths, property names and slide/text names are always case insensitive.', 'italic')

        print('\nEngine')
        print_methods('  /%s/' % self.name, self)
        print_properties(self)


        print('\nPost Processing')
        print_methods('  /%s/post_process/' % self.name, self.post_process)
        print_properties(self.post_process)

        print('\nSlides')
        self.create_group('', 'api')
        print_methods('  /%s/slide/<name>/' % self.name, self.slides['api'])
        print_properties(self.slides['api'])

        print('\nTexts')
        print_methods('  /%s/text/<name>/' % self.name, self.debug_text)
        print_properties(self.debug_text)

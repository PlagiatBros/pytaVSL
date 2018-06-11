class osc_range_method():

    def __init__(self, n):

        self.n = n
        self.range = range(n)

    def __call__(self, method):

        def range_method(this, path, args):

            if args[0] == -1:
                for i in self.range:
                    args[0] = i
                    method(this, path, args)
            elif args[0] < self.n:
                method(this, path, args)
            else:
                LOGGER.error("OSC ARGS ERROR: Slide number out of range")

        return range_method

class osc_range_method():

    def __init__(self, n):

        self.range = range(n)

    def __call__(self, method):

        def range_method(this, path, args):

            if args[0] == -1:
                for i in self.range:
                    args[0] = i
                    method(this, path, args)
            else:
                method(this, path, args)

        return range_method

class AutoExcuteFunction:
    def __init__(self, executes=[]):
        self.executes = executes

    def add(self, execute):
        self.executes.append(execute)
        return len(self.executes) - 1

    def remove(self, node):
        return self.execute.pop(node)

    def __execute(self, execute, node=1):
        #print(node, execute)
        func = execute[0]
        args = []
        kwargs = {}
        if len(execute) > 1:
            for arg in execute[1:]:
                _skip = []
                if isinstance(arg, list):
                    for i in range(len(arg)):
                        if callable(arg[i]):
                            args.append(self.__execute(arg[i:], node + 1))
                            for x in range(len(arg[i:])):
                                _skip.append(i + x + 1)
                        elif isinstance(arg[i], list):
                            for x in range(len(arg[i])):
                                if callable(arg[i][x]):
                                    args.append(self.__execute(arg[i], node + 1))
                                    break
                        else:
                            if i in _skip: continue
                            args.append(arg[i])
                elif callable(arg):
                    args.append(self.__execute([arg], node + 1))
                else:
                    args.append(arg)
        return func(*args, **kwargs)

    def __call__(self, node):
        return self.__execute(self.executes[node])

    def execute(self, execute):
        return self.__execute(execute)

if __name__ == '__main__':
    execute_func = AutoExcuteFunction()
    irange = lambda i: [i + 1 for i in range(i)]
    #node = execute_func.add([print, [lambda i: [i + 1 for i in range(i)], 8]])
    #execute_func(node)
    iprint = lambda *x: print(', '.join(['%s=%s' % (_, i) for _, i in enumerate(x)]))
    execute_func.execute([iprint, [irange, 3], ['HELLO', irange, 3]])
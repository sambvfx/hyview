import inspect
import zerorpc


class Client(zerorpc.Client):
    """
    Slightly extended version of the `zerorpc.Client` that allows use as
    context manager.
    """
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class Server(zerorpc.Server):
    """
    Slightly extended version of the `zerorpc.Server` that fixes some issues
    with ipython tab completion (over rpc) and promotes methods with the
    appropriate zerorpc decorators.
    """
    def __init__(self, methods=None, name=None, context=None, pool_size=None,
                 heartbeat=5):

        _methods = self._filter_methods(Server, self, methods)
        # for ipython tab completion
        _methods['trait_names'] = lambda: _methods.keys()
        _methods['_getAttributeNames'] = lambda: _methods.keys()

        # I wonder way base zerorpc implementation didn't do this?
        methods = {}
        for (k, f) in _methods.items():
            if inspect.isgeneratorfunction(f):
                f = zerorpc.stream(f)
            else:
                f = zerorpc.rep(f)
            methods[k] = f

        super(Server, self).__init__(
            methods=methods, name=name, context=context, pool_size=pool_size,
            heartbeat=heartbeat)

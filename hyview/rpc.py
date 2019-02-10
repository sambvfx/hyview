
import os
import string

import six

import zerorpc

from hyview.utils import serialize
from hyview.c4 import C4


def client(host=None, port=None):
    if host is None:
        host = os.environ.get('HYVIEW_CLIENT_HOST', '127.0.0.1')
    if port is None:
        port = os.environ.get('HYVIEW_CLIENT_PORT', '4242')

    c = zerorpc.Client()
    c.connect('tcp://{}:{}'.format(host, port))

    return c


def controller_client(host=None, port=None):
    if host is None:
        host = os.environ.get('HYVIEW_CLIENT_HOST', '127.0.0.1')
    if port is None:
        port = os.environ.get('HYVIEW_CONTROLLER_PORT', '4241')

    c = zerorpc.Client()
    c.connect('tcp://{}:{}'.format(host, port))

    return c


def _run(url):
    from hyview.houdini.hy import Controller

    s = zerorpc.Server(Controller())
    print('Starting hyview controller @ {!r}'.format(url))
    s.bind(url)
    s.run()


_thread = None


def start_controller(host=None, port=None):
    import threading

    global _thread

    if _thread is not None:
        raise RuntimeError('Controller thread already started')

    if host is None:
        host = os.environ.get('HYVIEW_CONTROLLER_HOST', '127.0.0.1')
    if port is None:
        port = os.environ.get('HYVIEW_CONTROLLER_PORT', '4241')

    url = 'tcp://{}:{}'.format(host, port)

    _thread = threading.Thread(target=_run, args=(url,))
    _thread.daemon = True
    _thread.start()


class RPCGeo(object):
    def __init__(self, geometry, name=None):
        self.geometry = geometry
        if name is not None:
            assert isinstance(name, six.string_types)
            assert name[0] in string.ascii_letters
        self._name = name
        self._server = None

    def build(self, host=None, port=None):
        s = zerorpc.Server(self)
        self._server = s

        if host is None:
            host = os.environ.get('HYVIEW_SERVER_HOST', '127.0.0.1')
        if port is None:
            port = os.environ.get('HYVIEW_SERVER_PORT', '4242')

        url = 'tcp://{}:{}'.format(host, port)

        s.bind(url)

        c = controller_client()
        c.create(self.name())

        s.run()

    def name(self):
        return self._name or str(C4(self.geometry))

    def complete(self):
        print('complete')
        self._server.stop()
        self._server.close()

    @zerorpc.stream
    def iter_attributes(self):
        print('iter_attributes')
        for attr in self.geometry.attributes:
            yield serialize(attr)

    @zerorpc.stream
    def iter_points(self):
        print('iter_points')
        for prim in self.geometry.primitives:
            for point in prim.points:
                yield serialize(point)


def send(obj, name=None):
    rpc = RPCGeo(obj, name=name)
    print('Starting build {!r}...'.format(rpc.name()))
    rpc.build()
    print('Done building {!r}'.format(obj))


def rpc_build(name, geo):
    """
    Called from the houdini python nodes.

    Parameters
    ----------
    name : str
    geo : hou.Geometry
    """
    from hyview.houdini.hy import build

    print('RPC build called for {!r}...'.format(name))

    c = client()
    assert name == c.name()
    build(geo, c)
    # shuts down the server
    del c
    c.complete()

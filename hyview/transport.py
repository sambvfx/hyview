"""
The plumbing of hyview to talk between processess.
"""
import string
import six
import attr

import zerorpc
import gevent
from gevent.event import Event

from hyview.c4 import C4
from hyview.constants import HOST, PORT, APP_PORT
import hyview.log

from typing import *


T = TypeVar('T')


_logger = hyview.log.get(__name__)


class Client(zerorpc.Client):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class Server(zerorpc.Server):
    def __init__(self, methods=None, name=None, context=None, pool_size=None,
                 heartbeat=5):
        super(Server, self).__init__(
            methods=methods, name=name, context=context, pool_size=pool_size,
            heartbeat=heartbeat)


def client(url):
    c = Client()
    c.connect(url)
    return c


def server(obj, url, **kwargs):
    s = zerorpc.Server(obj, **kwargs)
    s.bind(url)
    return s


class ApplicationInterface(object):
    def __init__(self):
        self._server = None
        self._thread = None
        self._client = None

        self._active = None
        self.is_done = Event()

        self._start()

    def __getattribute__(self, item):
        try:
            return super(ApplicationInterface, self).__getattribute__(item)
        except AttributeError:
            return getattr(self.hy, item)

    @property
    def hy(self):
        return self._client

    def _start(self):
        self._client = client('tcp://{}:{}'.format(HOST, APP_PORT))
        # TODO: confirm it's connected
        self._server = server(self, 'tcp://{}:{}'.format(HOST, PORT))
        self._thread = gevent.spawn(self._server.run)

    def stop(self):
        self._server.close()
        self._thread.join()

    def build(self, obj, name=None):

        if name is not None:
            # We want valid names for houdini.
            assert isinstance(name, six.string_types)
            assert name[0] in string.ascii_letters
        elif name is None:
            name = str(C4(obj))

        assert name not in self.hy.names()

        _logger.debug('Starting build {!r}'.format(name))

        self._active = obj

        self.hy.create(name)

        # block until complete is called
        self.is_done.wait()

        self.hy.complete(name)

        _logger.debug('Done building {!r}'.format(name))

    def _clear(self):
        """
        Delete all geometry.
        """
        self.hy.clear()

    def complete(self):
        self.is_done.set()
        self.is_done.clear()
        self._active = None

    @zerorpc.stream
    def iter_attributes(self):
        """
        Yield all custom attributes of the geometry.

        Returns
        -------
        Iterator[Dict[str, Any]]
        """
        for x in self._active.attributes:
            yield attr.asdict(x)

    @zerorpc.stream
    def iter_points(self):
        """
        Yield all the points of the geometry.

        Returns
        -------
        Iterator[Dict[str, Any]]
        """
        for prim in self._active.primitives:
            for point in prim.points:
                yield attr.asdict(point)


_app = None


def start():
    """
    Start and return the app interface.

    Returns
    -------
    ApplicationInterface
    """
    global _app

    if _app is None:
        _app = ApplicationInterface()

    return _app


def app():
    """
    Get app interface.

    Returns
    -------
    ApplicationInterface
    """
    return start()

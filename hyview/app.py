import string
import six

import attr

import gevent
from gevent.event import Event
import zerorpc

import hyview.transport
from hyview.constants import HOST, PORT, APP_PORT
from hyview.c4 import C4

import hyview.hy.implementation

from typing import *


_logger = hyview.get_logger(__name__)


class ApplicationInterface(object):
    """
    Object for streaming data to Houdini.
    """
    def __init__(self):
        self._active = None
        self.is_done = Event()

    def build(self, obj, name=None):
        """
        Build a houdini object remotely.

        Parameters
        ----------
        obj : hyview.Geometry
        name : Optional[str]
            Unique identifier
        """
        if name is not None:
            # We want valid names for houdini.
            assert isinstance(name, six.string_types)
            assert name[0] in string.ascii_letters
        elif name is None:
            name = str(C4(obj))

        assert name not in hyview.hy.implementation.all_nodes()

        _logger.debug('Starting build {!r}'.format(name))

        self._active = obj

        hyview.hy.implementation.create(name)

        # block until complete is called
        self.is_done.wait()

        hyview.hy.implementation.sync_complete(name)

        _logger.debug('Done building {!r}'.format(name))

    def complete(self):
        self.is_done.set()
        self.is_done.clear()
        self._active = None

    def iter_attributes(self):
        """
        Yield all custom attributes of the geometry.

        Returns
        -------
        Iterator[Dict[str, Any]]
        """
        for x in self._active.attributes:
            yield attr.asdict(x)

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


class App(object):
    def __init__(self, interface):
        self.interface = interface

        self._thread = None
        self.server = None
        self.client = None
        self.start()

    def start(self):

        # TODO: confirm it's connected
        self.client = hyview.transport.Client()
        self.client.connect('tcp://{}:{}'.format(HOST, APP_PORT))

        self.server = hyview.transport.Server(self.interface)
        self.server.bind('tcp://{}:{}'.format(HOST, PORT))
        self._thread = gevent.spawn(self.server.run)

    def stop(self):
        self.server.close()
        self._thread.join()


_app = None


def initialize():
    """
    Start and return the app interface.

    Returns
    -------
    App
    """
    global _app

    if _app is None:
        _app = App(ApplicationInterface())

    return _app


def app():
    """
    Get app interface.

    Returns
    -------
    App
    """
    return initialize()


def build(obj, name=None):
    app().interface.build(obj, name=name)

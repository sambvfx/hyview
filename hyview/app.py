import string
import six

import attr

from kids.cache import cache

import gevent
from gevent.event import Event

import hyview.transport
from hyview.constants import HOST, PORT, APP_PORT
from hyview.c4 import C4

import hyview.hy.impl

from typing import *


_logger = hyview.get_logger(__name__)


class ApplicationInterface(object):
    """
    Object for streaming data to Houdini. This is the object hosted by the
    zerorpc.Server and is what Houdini will interface with for pulling data
    between processes. There should only be one object "active" at a time
    while it waits for Houdini to consume the object being built.
    """
    def __init__(self):
        self._active = None  # type: hyview.interface.Geometry
        self.is_done = Event()

    def build(self, obj, name=None, frame=1):
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

        assert name not in hyview.hy.impl.all_nodes()

        _logger.debug('Starting build {!r}'.format(name))

        self._active = obj

        hyview.hy.impl.create(name, frame)

        # block until complete is called
        self.is_done.wait()

        hyview.hy.impl.sync_complete(name)

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
        for x in self._active.points:
            yield attr.asdict(x)


class App(object):
    """
    Object responsible for hosting the transport layer that interfaces with
    the remote rpc server and clients. All calls should go through the
    singleton instance of this class (accessible via the `app` method).
    """
    def __init__(self, interface):
        """
        Parameters
        ----------
        interface : ApplicationInterface
        """
        self.interface = interface

        self._thread = None  # type: gevent.Greenlet
        self.server = None  # type: hyview.transport.Server
        self.client = None  # type: hyview.transport.Client
        self.start()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

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
        self._thread = None
        self.server = None
        self.client = None


@cache
def app():
    """
    Get app interface.

    Note: This is a cached method with the intention of treating the app like
     a singleton.

    Returns
    -------
    App
    """
    return App(ApplicationInterface())


def build(obj, name=None, frame=1):
    """
    Build a houdini object remotely.

    Parameters
    ----------
    obj : hyview.Geometry
    name : Optional[str]
        Unique identifier
    frame : int
        Represents time.
    """
    app().interface.build(obj, name=name, frame=frame)

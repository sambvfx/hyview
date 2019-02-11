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
from hyview.constants import SERVER_HOST, SERVER_PORT, BUILD_PORT, LOGGING_LEVEL

import logging

from typing import *


T = TypeVar('T')


logging.basicConfig()
_logger = logging.getLogger(__name__)
_logger.setLevel(LOGGING_LEVEL)


class Client(zerorpc.Client):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def client(url):
    c = Client()
    c.connect(url)
    return c


def server(obj, url):
    s = zerorpc.Server(obj)
    s.bind(url)
    return s


def app_client():
    return client('tcp://{}:{}'.format(SERVER_HOST, SERVER_PORT))


def app_server(obj):
    return server(obj, 'tcp://{}:{}'.format(SERVER_HOST, SERVER_PORT))


def tmp_client():
    return client('tcp://{}:{}'.format(SERVER_HOST, BUILD_PORT))


def tmp_server(obj):
    return server(obj, 'tcp://{}:{}'.format(SERVER_HOST, BUILD_PORT))


class RPCGeo(object):
    """
    Wrapper object of a `hyview.interface.Geometry` object. This is the object
    hosted as a zerorpc server and interfaced from the client in Houdini.

    There should only be one of these active at any given time.
    """
    def __init__(self, geometry, name=None):
        self._geometry = geometry
        if name is not None:
            # We want valid names for houdini.
            assert isinstance(name, six.string_types)
            assert name[0] in string.ascii_letters
        elif name is None:
            name = str(C4(self._geometry))
        self._name = name
        self.is_done = Event()

    def name(self):
        """
        Get the geometry's unique identifier.

        Returns
        -------
        str
        """
        return self._name

    def complete(self):
        """
        Mark the object build as being complete.
        """
        self.is_done.set()

    @zerorpc.stream
    def iter_attributes(self):
        """
        Yield all custom attributes of the geometry.

        Returns
        -------
        Iterator[Dict[str, Any]]
        """
        for x in self._geometry.attributes:
            yield attr.asdict(x)

    @zerorpc.stream
    def iter_points(self):
        """
        Yield all the points of the geometry.

        Returns
        -------
        Iterator[Dict[str, Any]]
        """
        for prim in self._geometry.primitives:
            for point in prim.points:
                yield attr.asdict(point)


def send(obj, name=None):
    """
    Send a geometry object to be built.

    Parameters
    ----------
    obj : hyview.interface.Geometry
    name : Optional[str]
        Used for uniqueness. Depending on how we deal with caching, this may
        result in using an existing cached file if one exists with this name.
        If not proivded, we generated a C4 hash of `obj` and use that.
    """
    rpc = RPCGeo(obj, name=name)
    name = rpc.name()

    _logger.debug('Starting build {!r}'.format(name))

    s = tmp_server(rpc)
    thread = gevent.spawn(s.run)

    c = client('tcp://{}:{}'.format(SERVER_HOST, SERVER_PORT))
    c.create(name)

    rpc.is_done.wait()

    c.complete(name)

    c.close()
    s.close()
    thread.join()

    _logger.debug('Done building {!r}'.format(name))

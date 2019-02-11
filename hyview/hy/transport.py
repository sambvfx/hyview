"""
Methods dealing with plumbing between Houdini commands and other processes.

NOTE: This module should remain importable from outside of Houdini.
"""
import hyview.transport
import hyview.log
from hyview.constants import HOST, PORT


_logger = hyview.log.get(__name__)


def build(node):
    """
    Called from the houdini python node to build the geometry.

    Parameters
    ----------
    node : hou.Node
    """
    import hyview.hy.implementation

    name = node.parent().name()

    _logger.debug('RPC build called for {!r}...'.format(name))

    with hyview.transport.client('tcp://{}:{}'.format(HOST, PORT)) as c:
        hyview.hy.implementation.build(
            node.geometry(), c.iter_attributes(), c.iter_points())


def call(node, cmd, *args, **kwargs):
    """
    Called from the houdini python node to execute arbitrary command.

    Parameters
    ----------
    node : hou.Node
    cmd : str
    args : *Any
    kwargs : **Any
    """
    name = node.parent().name()

    _logger.debug('RPC command {!r} called for {!r}...'.format(cmd, name))

    with hyview.transport.client('tcp://{}:{}'.format(HOST, PORT)) as c:
        getattr(c, cmd)(*args, **kwargs)


def complete(node):
    """
    Called from the houdini python node to signal the cook is complete.

    Parameters
    ----------
    node : hou.Node
    """
    name = node.parent().name()

    _logger.debug('RPC complete called for {!r}...'.format(name))

    with hyview.transport.client('tcp://{}:{}'.format(HOST, PORT)) as c:
        c.complete()

    node.parm('python').set('')


def _run(plugin_paths=None):
    from hyview.hy.implementation import HoudiniApplicationController
    from hyview.registry import Registry
    from hyview.constants import HOST, APP_PORT

    Registry.initialize(paths=plugin_paths)

    s = hyview.transport.server(
        Registry.new(HoudiniApplicationController)(),
        'tcp://{}:{}'.format(HOST, APP_PORT))
    _logger.debug('Starting hyview controller')
    s.run()


_thread = None


def start_houdini(plugin_paths=None):
    """
    Start the hyview server thread. This is the method called within houdini
    to start the rpc server and interface for Houdini.
    """
    try:
        import hou
    except ImportError:
        raise RuntimeError('This method must be called by houdini python.')

    import threading

    global _thread

    if _thread is not None:
        raise RuntimeError('Houdini server already started')

    _thread = threading.Thread(
        target=_run, kwargs=dict(plugin_paths=plugin_paths))
    _thread.daemon = True
    _thread.start()

"""
Startup for the Houdini RPC server.
"""
import os
import hyview.transport
import hyview.plugins
from hyview.constants import HOST, APP_PORT


_logger = hyview.get_logger(__name__)


def _run(plugin_paths=None):
    import hyview.hy.core

    plugin_paths = plugin_paths or os.environ.get('HYVIEW_PLUGIN_PATH')
    if plugin_paths:
        hyview.plugins.import_modules(plugin_paths)

    hyview.hy.core.initialize()

    s = hyview.transport.Server(hyview.plugins.RPC_METHODS)
    s.bind('tcp://{}:{}'.format(HOST, APP_PORT))
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

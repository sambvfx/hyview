"""
Initialization methods for the Houdini RPC server.
"""
import os
import threading
import hyview.transport
import hyview.plugins
from hyview.constants import HOST, APP_PORT


_logger = hyview.get_logger(__name__)


_thread = None  # type: threading.Thread


def _run(plugin_paths=None):
    """
    Callback ran within the Houdini thread. This imports the plugin modules,
    starts the zerorpc Server and runs/blocks forever.

    Parameters
    ----------
    plugin_paths : Optional[Union[str, Iterable[str]]]
    """
    import hyview.hy.core

    plugin_paths = plugin_paths or os.environ.get('HYVIEW_PLUGIN_PATH')
    if plugin_paths:
        hyview.plugins.import_modules(plugin_paths)

    hyview.hy.core.initialize()

    s = hyview.transport.Server(hyview.plugins.RPC_METHODS)
    s.bind('tcp://{}:{}'.format(HOST, APP_PORT))
    _logger.debug('Starting hyview controller')
    s.run()


def start_houdini(plugin_paths=None):
    """
    Start the hyview server thread. This is the method called within Houdini
    to start the rpc server and interface for Houdini.

    Parameters
    ----------
    plugin_paths : Optional[Union[str, Iterable[str]]]
    """
    try:
        import hou
    except ImportError:
        raise RuntimeError('This method must be called by houdini python.')

    global _thread

    if _thread is not None:
        raise RuntimeError('Houdini server already started')

    _thread = threading.Thread(
        target=_run, kwargs=dict(plugin_paths=plugin_paths))
    # daemon to make sure the thread dies with Houdini
    _thread.daemon = True
    _thread.start()

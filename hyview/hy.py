"""
hyview Houdini module. This is the module imported and used within Houdini.

# TODO: Manage cache files?
"""
import os

import hou

import hyview.rpc
from hyview.constants import CACHE_DIR, LOGGING_LEVEL

import logging


logging.basicConfig()
_logger = logging.getLogger(__name__)
_logger.setLevel(LOGGING_LEVEL)


class BatchUpdate(object):
    """
    Context manager for blocking any cooking
    """
    def __init__(self):
        self._current = hou.updateModeSetting()

    def __enter__(self):
        hou.setUpdateMode(hou.updateMode.Manual)
        hou.updateModeSetting()

    def __exit__(self, exc_type, exc_val, exc_tb):
        hou.setUpdateMode(self._current)
        hou.updateModeSetting()


def reformat(s):
    return '\n'.join(x.strip() for x in s.strip().split('\n'))


class ApplicationController(object):
    def __init__(self, parent=None, cachedir=CACHE_DIR):
        if parent is None:
            parent = hou.node('/obj/hyview')
            if parent:
                parent.destroy()
            parent = hou.node('/obj').createNode('subnet', 'hyview')
            parent.moveToGoodPosition()
        self.parent = parent

        self.cachedir = cachedir

    @property
    def nodes(self):
        return {n.name(): n for n in self.parent.children()}

    def clear(self):
        for node in self.parent.children():
            node.destroy()

    def complete(self, name):
        node = self.nodes.get(name)
        for child in node.children():
            if child.type().name() == 'python':
                child.destroy()

    def create(self, name, cache=True):
        if name in self.nodes:
            raise ValueError('{!r} already exists'.format(name))

        cache_path = os.path.join(self.cachedir, '{}.bgeo'.format(name))

        use_cache = False
        if os.path.exists(cache_path):
            if not cache:
                os.remove(cache_path)
            else:
                use_cache = True

        with BatchUpdate():

            geo = self.parent.createNode('geo', node_name=name)
            geo.moveToGoodPosition()

            fnode = geo.createNode('file')
            fnode.parm('file').set(cache_path)
            fnode.parm('filemode').set(0)

            signal_node = geo.createNode('python')
            signal_node.moveToGoodPosition()
            signal_node.setInput(0, fnode)
            signal_node.parm('python').set(reformat('''
                import hyview.hy
                hyview.hy.rpc_complete(hou.pwd())
            '''))
            signal_node.setDisplayFlag(True)

            if not use_cache:
                python_in = geo.createNode('python')
                python_in.parm('python').set(reformat('''
                    import hyview.hy
                    hyview.hy.rpc_build(hou.pwd())
                '''))
                python_in.moveToGoodPosition()
                fnode.setInput(0, python_in)

            fnode.moveToGoodPosition()
            signal_node.moveToGoodPosition()


def build(geo, rpc):
    """
    Build a geometry in Houdini.

    Parameters
    ----------
    geo : hou.Geometry
    rpc : hyview.rpc.RPCGeo
        NOTE: We lie here about the type and pretend we're dealing with our
        RPCGeo object, even though we're interacting with it via the
        `zeroprc.Client`.
    """
    for attr in rpc.iter_attributes():
        geo.addAttrib(
            getattr(hou.attribType, attr['type']),
            attr['name'],
            default_value=attr['default'])

    for point in rpc.iter_points():
        p = geo.createPoint()
        p.setPosition(hou.Vector3((point['x'], point['y'], point['z'])))
        for k, v in point['attrs'].items():
            p.setAttribValue(k, v)


def rpc_build(node):
    """
    Called from the houdini python node to build the geometry.

    Parameters
    ----------
    node : hou.Node
    """
    name = node.parent().name()

    _logger.debug('RPC build called for {!r}...'.format(name))

    with hyview.rpc.tmp_client() as c:
        assert name == c.name()
        build(node.geometry(), c)


def rpc_complete(node):
    """
    Called from the houdini python node to signal the cook is complete.

    Parameters
    ----------
    node : hou.Node
    """
    name = node.parent().name()

    _logger.debug('RPC complete called for {!r}...'.format(name))

    with hyview.rpc.tmp_client() as c:
        assert name == c.name()
        c.complete()

    node.parm('python').set('')


def _run():
    s = hyview.rpc.app_server(ApplicationController())
    _logger.debug('Starting hyview controller')
    s.run()


_thread = None


def start():
    import threading

    global _thread

    if _thread is not None:
        raise RuntimeError('Controller thread already started')

    _thread = threading.Thread(target=_run)
    _thread.daemon = True
    _thread.start()

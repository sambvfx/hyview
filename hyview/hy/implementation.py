"""
hyview Houdini module. This is the module imported and used within Houdini.

# TODO: Manage cache files?
"""
import os

import hou

from hyview.constants import CACHE_DIR
import hyview.log


_logger = hyview.log.get(__name__)


class BatchUpdate(object):
    """
    Context manager for blocking any cooking.
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


class HoudiniApplicationController(object):
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

    def names(self):
        return self.nodes.keys()

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
                import hyview.hy.transport
                hyview.hy.transport.complete(hou.pwd())
            '''))
            signal_node.setDisplayFlag(True)

            if not use_cache:
                python_in = geo.createNode('python')
                python_in.parm('python').set(reformat('''
                    import hyview.hy.transport
                    hyview.hy.transport.build(hou.pwd())
                '''))
                python_in.moveToGoodPosition()
                fnode.setInput(0, python_in)

            fnode.moveToGoodPosition()
            signal_node.moveToGoodPosition()


def build(geo, attrs, points):
    """
    Build a geometry in Houdini.

    Parameters
    ----------
    geo : hou.Geometry
    attrs : Iterable[Union[hyview.interface.AttributeDefinition, Dict[str, Any]]]
    points : Iterable[Union[hyview.interface.Point, Dict[str, Any]]]
    """
    for attr in attrs:
        geo.addAttrib(
            getattr(hou.attribType, attr['type']),
            attr['name'],
            default_value=attr['default'])

    for point in points:
        p = geo.createPoint()
        p.setPosition(hou.Vector3((point['x'], point['y'], point['z'])))
        for k, v in point['attrs'].items():
            p.setAttribValue(k, v)

"""
Remote procedures to run in Houdini.
"""
import os
from hyview.constants import CACHE_DIR, HOST, PORT
import hyview


_logger = hyview.get_logger(__name__)


@hyview.rpc()
def all_nodes():
    from hyview.hy.core import root
    return [x.name() for x in root().children()]


@hyview.rpc()
def clear():
    from hyview.hy.core import root
    for node in root().children():
        node.destroy()


@hyview.rpc()
def sync_complete(name):
    """
    Called after a geometry sync is completed. This removes the python nodes
    responsible for syncing the data and will use what's on disk.

    Parameters
    ----------
    name : str
    """
    import hyview.hy.core

    for node in hyview.hy.core.root().children():
        if node.name() == name:
            for child in node.children():
                if child.type().name() == 'python':
                    child.destroy()


def build(geo, attrs, points):
    """
    Build a geometry in Houdini.

    Parameters
    ----------
    geo : hou.Geometry
    attrs : Iterable[Dict[str, Any]]
    points : Iterable[Dict[str, Any]]
    """
    import hou

    # First build the attributes.
    for attr in attrs:
        geo.addAttrib(
            getattr(hou.attribType, attr['type']),
            attr['name'],
            default_value=attr['default'])

    # Then build the points.
    for point in points:
        p = geo.createPoint()
        p.setPosition(hou.Vector3((point['x'], point['y'], point['z'])))
        for k, v in point['attrs'].items():
            p.setAttribValue(k, v)


def stream(node):
    """
    Called from the Houdini python node to build the geometry.

    Parameters
    ----------
    node : hou.Node
    """
    import hyview.transport

    name = node.parent().name()

    _logger.debug('RPC build called for {!r}...'.format(name))

    client = hyview.transport.Client()
    client.connect('tcp://{}:{}'.format(HOST, PORT))

    with client as c:
        build(node.geometry(), c.iter_attributes(), c.iter_points())


def cook_complete(node):
    """
    Called from the houdini python node to signal the cook is complete.

    Parameters
    ----------
    node : hou.Node
    """
    import hyview.transport

    name = node.parent().name()

    _logger.debug('RPC complete called for {!r}...'.format(name))

    client = hyview.transport.Client()
    client.connect('tcp://{}:{}'.format(HOST, PORT))

    with client as c:
        c.complete()

    node.parm('python').set('')


@hyview.rpc()
def create(name, frame=1, cache=True):
    """
    Create a new geometry.

    This creates some python nodes that will connect up to a rpc server and
    stream attributes and points to be created.

    Parameters
    ----------
    name : str
    frame : int
    cache : bool
        Use existing cached files with `name` identifier if it exists.
    """
    import hou
    from hyview.hy.core import root, BatchUpdate, reformat_python

    hou.setFrame(frame)

    fpath = os.path.join(CACHE_DIR, '{}.$F4.bgeo'.format(name))
    cache_path = hou.expandString(fpath)

    use_cache = False
    if os.path.exists(cache_path):
        if not cache:
            os.remove(cache_path)
        else:
            use_cache = True

    for node in root().children():
        if node.name() == name:
            node.destroy()

    with BatchUpdate():

        geo = root().createNode('geo', node_name=name)
        geo.moveToGoodPosition()

        fnode = geo.createNode('file')
        fnode.parm('file').set(fpath)
        fnode.parm('filemode').set(0)

        signal_node = geo.createNode('python')
        signal_node.moveToGoodPosition()
        signal_node.setInput(0, fnode)
        signal_node.parm('python').set(reformat_python('''
            import hyview.hy.implementation
            hyview.hy.implementation.cook_complete(hou.pwd())
        '''))
        signal_node.setDisplayFlag(True)

        if not use_cache:
            python_in = geo.createNode('python')
            python_in.parm('python').set(reformat_python('''
                import hyview.hy.implementation
                hyview.hy.implementation.stream(hou.pwd())
            '''))
            python_in.moveToGoodPosition()
            fnode.setInput(0, python_in)

        fnode.moveToGoodPosition()
        signal_node.moveToGoodPosition()


# Provided helper methods that are more for examples.


@hyview.rpc()
def mesh_all(**kwargs):
    """
    Create a particle fliud mesh for all geo within the hyview root subnet.

    Parameters
    ----------
    kwargs : **Any
    """
    import hyview.hy.core

    kwargs.setdefault('particlesep', 8)
    kwargs.setdefault('transferattribs', 'Cd')

    for node in hyview.hy.core.root().children():

        last = node.children()[-1]

        if 'particlefluidsurface' in last.type().name():
            # already meshed
            continue

        p = node.createNode('particlefluidsurface')

        # apply parm values
        for k, v in kwargs.items():
            p.parm(k).set(v)
            p.parm(k).set(v)

        p.setInput(0, last)
        p.setDisplayFlag(True)

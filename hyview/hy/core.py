import hou


def initialize():
    """
    Initialize the hyview node. Mulitiple calls to this will delete and
    recreate the root hyview subnet node.
    """
    result = hou.node('/obj/hyview')
    if result:
        result.destroy()
    result = hou.node('/obj').createNode('subnet', 'hyview')
    result.moveToGoodPosition()


def root():
    """
    Get the root hyview node.

    Returns
    -------
    hou.Node
    """
    return hou.node('/obj/hyview')


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


def reformat_python(s):
    return '\n'.join(x.strip() for x in s.strip().split('\n'))

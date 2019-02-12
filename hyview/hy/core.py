import hou


def initialize():
    root = hou.node('/obj/hyview')
    if root:
        root.destroy()
    root = hou.node('/obj').createNode('subnet', 'hyview')
    root.moveToGoodPosition()


def root():
    return hou.node('/obj/hyview')


def get_node(name):
    for child in root().children():
        if child.name() == name:
            return child


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

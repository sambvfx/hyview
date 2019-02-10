import os

import hou


# TODO: manage cache files?


class Controller(object):
    def __init__(self, parent=None, cache='/tmp/hyview'):
        self.cache = cache
        if parent is None:
            parent = hou.node('/obj/hyview')
            if parent:
                parent.destroy()
            parent = hou.node('/obj').createNode('subnet', 'hyview')
            parent.moveToGoodPosition()
        self.parent = parent

        self._pending = {}

    def clear(self):
        for node in self.parent.children():
            node.destroy()
        # clear pending items
        self._pending = {}

    def create(self, name=None):
        if name in [x.name for x in self.parent.children()]:
            raise ValueError('{!r} already exists'.format(name))

        geo = self.parent.createNode('geo', node_name=name)
        geo.moveToGoodPosition()

        python = geo.createNode('python')
        python.moveToGoodPosition()

        cache_path = os.path.join(self.cache, '{}.bgeo'.format(name))

        write = geo.createNode('file')
        write.setInput(0, python)
        write.moveToGoodPosition()
        write.parm('file').set(cache_path)
        write.parm('filemode').set(2)

        read = geo.createNode('file')
        read.setInput(0, write)
        read.moveToGoodPosition()
        read.parm('file').set(cache_path)
        read.parm('filemode').set(1)

        python.parm('python').set(
            'from hyview.rpc import rpc_build\n'
            'rpc_build(hou.pwd().parent().name(), node.geometry())\n')

    def fetch(self, name):
        return self._pending.pop(name, None)


def build(geo, rpc):
    print('Running build procedure...')
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

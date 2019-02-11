"""
Module for testing...
"""
import random
from collections import defaultdict

import hyview.data
import hyview.interface
import hyview.rpc


def neuron_sample(filters=None, size=None, znth=None, nth=None, zmult=10):
    images, labels = hyview.data.load_data_from_h5py(
        '~/projects/hyview/_data/sample_A_20160501.hdf',
        'volumes/raw',
        'volumes/labels/neuron_ids')

    it = hyview.data.iterfilter(
        images, labels, size=size, znth=znth, nth=nth, zmult=zmult)

    points = defaultdict(list)

    for label, x, y, z, c in it:
        if filters and label not in filters:
            continue
        cd = float(c) / 255.0
        point = hyview.interface.Point(
            x=x, y=y, z=z, attrs={
                'label': label,
                'luminance': c,
                'Cd': (cd, cd, cd)
            }
        )
        points[label].append(point)

    primitives = []

    for k, v in points.items():
        primitive = hyview.interface.Primitive(points=v)
        primitives.append(primitive)

    attributes = [
        hyview.interface.AttributeDefinition(
            name='Cd', type='Point', default=(0.1, 0.1, 0.1)),
        hyview.interface.AttributeDefinition(
            name='luminance', type='Point', default=1),
        hyview.interface.AttributeDefinition(
            name='label', type='Point', default=-1),
    ]

    geo = hyview.interface.Geometry(
        attributes=attributes, primitives=primitives)

    hyview.rpc.send(geo)


class RandomColor(object):

    COLORS = {
        'purple': (0.619, 0.525, 0.784),
        'pink': (0.690, 0.321, 0.474),
        'orange': (0.909, 0.4901, 0.2431),
        'grey': (0.474, 0.474, 0.474),
        'white': (0.839, 0.839, 0.839),
        'blue': (0.423, 0.6, 0.733),
        'green': (0.705, 0.823, 0.4509),
        'yellow': (0.898, 0.709, 0.40),
    }

    def __init__(self, colors=None):
        if colors is None:
            self._colors = list(self.COLORS.values())
        self._index = 0
        self._max = len(self._colors)
        self._cache = {}

    def __call__(self, name=None):
        return self.get(name=name)

    def next(self):
        result = self._colors[self._index]
        self._index += 1
        if self._index >= self._max:
            self._index = 0
        return result

    def get(self, name=None):
        if name is None:
            return self.next()
        result = self._cache.get(name)
        if result is None:
            result = self.next()
            self._cache[name] = result
        return result


def neuron_sample_by_label(filters=None, size=None, znth=None, nth=None,
                           zmult=10):

    from hyview.c4 import C4

    colors = RandomColor()

    images, labels = hyview.data.load_data_from_h5py(
        '~/projects/hyview/_data/sample_A_20160501.hdf',
        'volumes/raw',
        'volumes/labels/neuron_ids')

    it = hyview.data.iterfilter(
        images, labels, size=size, znth=znth, nth=nth, zmult=zmult)

    points = defaultdict(list)

    for label, x, y, z, c in it:
        if filters and label not in filters:
            continue
        cd = float(c) / 255.0
        point = hyview.interface.Point(
            x=x, y=y, z=z, attrs={
                'label': label,
                'luminance': c,
                'Cd': colors.get(label),
                'Alpha': cd,
            }
        )
        points[label].append(point)

    for k, v in points.items():
        primitive = hyview.interface.Primitive(points=v)

        attributes = [
            hyview.interface.AttributeDefinition(
                name='Cd', type='Point', default=(0.1, 0.1, 0.1)),
            hyview.interface.AttributeDefinition(
                name='Alpha', type='Point', default=1.0),
            hyview.interface.AttributeDefinition(
                name='luminance', type='Point', default=1),
            hyview.interface.AttributeDefinition(
                name='label', type='Point', default=-1),
        ]

        geo = hyview.interface.Geometry(
            attributes=attributes, primitives=[primitive])

        hyview.rpc.send(geo, name='label-{}-{}'.format(
            k, C4(filters, size, znth, nth, zmult)))


def _random_point_gen(size=None):
    i = 0
    while size is None or i < size:
        c = random.randint(0, 255)
        cd = float(c) / 255.0
        yield hyview.interface.Point(
            x=random.randint(0, 10),
            y=random.randint(0, 10),
            z=random.randint(0, 10),
            attrs={
                'Cd': (cd, cd, cd),
                'luminance': c,
                'label': random.randint(1, 30)
            }
        )
        i += 1


def random_data(size=200):

    primitive = hyview.interface.Primitive(
        points=list(_random_point_gen(size=size)))

    attributes = [
        hyview.interface.AttributeDefinition(
            name='Cd', type='Point', default=(0.1, 0.1, 0.1)),
        hyview.interface.AttributeDefinition(
            name='luminance', type='Point', default=1),
        hyview.interface.AttributeDefinition(
            name='label', type='Point', default=-1),
    ]

    geo = hyview.interface.Geometry(
        attributes=attributes, primitives=[primitive])

    hyview.rpc.send(geo)

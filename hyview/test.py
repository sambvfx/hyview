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


def random_point_gen(size=None):
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
        points=list(random_point_gen(size=size)))

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

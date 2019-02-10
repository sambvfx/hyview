import itertools


def iterfilter(images, labels, size=None, znth=None, nth=None, zmult=10):
    if size:
        images = images[:size]
        labels = labels[:size]

    def islice(it, n):
        if n:
            return itertools.islice(it, 0, None, n)
        return it

    for z, (image, zlabels) in islice(enumerate(zip(images, labels)), znth):
        for y, (row, ylabels) in islice(enumerate(zip(image, zlabels)), nth):
            for x, (c, label) in islice(enumerate(zip(row, ylabels)), nth):
                yield int(label), int(x), int(y), int(z * zmult), int(c)


def load_data_from_h5py(path, *keys):
    """
    Examples
    --------
    >>> images, lables = load_data_from_h5py(
    ...     '/path/to/file.h5py',
    ...     'volumes/raw',
    ...     'volumes/labels/neuron_ids'
    ... )

    Parameters
    ----------
    path : str
    keys : *str

    Returns
    -------
    Tuple[Any, ...]
    """
    import os
    import h5py
    data = h5py.File(os.path.expandvars(os.path.expanduser(path)))
    return tuple(data[x] for x in keys)


def test(filters=None, size=None, znth=None, nth=None, zmult=10):
    from collections import defaultdict
    import hyview.interface
    import hyview.rpc

    images, labels = load_data_from_h5py(
        '~/projects/hyview/_data/sample_A_20160501.hdf',
        'volumes/raw',
        'volumes/labels/neuron_ids')

    it = iterfilter(images, labels, size=size, znth=znth, nth=nth, zmult=zmult)

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

    for k, v in points.items():
        primitive = hyview.interface.Primitive(points=v)

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

        hyview.rpc.send(geo, name='label-{}'.format(k))


def test_random_data(points=200):
    import random
    import hyview.interface
    import hyview.rpc

    def random_point_gen():
        while True:
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

    inf_points = random_point_gen()

    primitive = hyview.interface.Primitive(
        points=list(itertools.islice(inf_points, points)))

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

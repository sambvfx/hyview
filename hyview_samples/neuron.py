"""
Sample module showcasing uses displaying datasets from neurons.

NOTE: Some thirdparty modules may be required to use some of these methods.
"""
import os
from collections import defaultdict

import hyview
import hyview.log


_logger = hyview.log.get_logger(__name__)


SAMPLE_PATH = os.path.join(
    os.path.dirname(__file__),
    '_data',
    'sample_A_20160501.hdf')


def sample(filters=None, minimum=2000000, nth=8, mesh=True):
    """
    Visualize interesting data structures within the neuron dataset.

    Parameters
    ----------
    filters : Optional[List[int]]
        Provide labels to filter the dataset to manually. If not provided,
        then it will use labels that contain more than the `minimum` points.
    minimum : int
        Filter to labels that have point counts over this number.
    nth : int
        Skip to every nth sample.
    mesh : bool
        Mesh the points.
    """
    import hyview.hy.impl

    _logger.info('Loading data from {!r}...'.format(SAMPLE_PATH))

    images, labels = load_data()

    _logger.info('Finding labels with more than {!r} entries...'.format(minimum))

    if filters is None:
        filters = list(iter_unique_by_count(labels, minimum=minimum))

    _logger.info('Filtering data...')

    for name, geo in geogen(
            images, labels,
            group='label',
            colorize=True,
            filters=filters,
            size=0, znth=0, nth=nth, zmult=10):

        _logger.info('Sending {!r} to Houdini...'.format(name))

        hyview.build(geo, name=name)

    if mesh:
        _logger.info('Meshing all geo...')
        hyview.hy.impl.mesh_all(particlesep=8)


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


def load_data():
    """
    Gets "images" and "labels" test numpy arrays.

    Returns
    -------
    Tuple[numpy.array, numpy.array]
    """
    return load_data_from_h5py(
        SAMPLE_PATH, 'volumes/raw', 'volumes/labels/neuron_ids')


def iterfilter(images, labels, size=None, znth=None, nth=None, zmult=10):
    """
    Helper to iterate and filter over dataset.

    Parameters
    ----------
    images : numpy.array
    labels : numpy.array
    size : Optional[int]
    znth : Optional[int]
    nth : Optionl[int]
    zmult : int
        Scale multiplier for z coordinate.

    Returns
    -------
    Iterator[Tuple[int, float, float, float, int]]
    """
    import itertools

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
                yield int(label), float(x), float(y), float(z * zmult), int(c)


def iter_unique_by_count(ar, minimum=None, maximum=None, return_counts=False):
    """
    Filter an array by unique count.

    Parameters
    ----------
    ar : numpy.array
    minimum : Optional[int]
    maximum : Optional[int]
    return_counts : bool

    Returns
    -------
    Union[Iterator[Any], Iterator[Tuple[Any, int]]]
    """
    import numpy

    for item, count in zip(*numpy.unique(ar, return_counts=True)):
        if minimum is not None and count < minimum:
            continue
        if maximum is not None and count > maximum:
            continue
        if return_counts:
            yield item, count
        else:
            yield item


def pointgen(images, labels, colorize=False, filters=None, size=None, znth=3,
             nth=8, zmult=10):
    """
    Parameters
    ----------
    images : numpy.array
    labels : numpy.array
    colorize : bool
        Colorize the data per-label.
    filters : Optional[List[int]]
        Filters the data to only those that have labels within this list.
    size : Optional[int]
        Specify the number of z slices.
    znth : Optional[int]
        Specify how many of each z slice to use.
    nth : Optional[int]
        Filters the points to every `nth`.
    zmult : int
        Scale multiplier for z.

    Returns
    -------
    Iterator[hyview.Point]
    """
    from hyview_samples.utils import ColorGenerator

    colors = ColorGenerator()

    it = iterfilter(
        images, labels,
        size=size,
        znth=znth,
        nth=nth,
        zmult=zmult
    )

    for label, x, y, z, c in it:
        if filters and label not in filters:
            continue
        cd = float(c) / 255.0
        if colorize:
            color = colors.get(label)
        else:
            color = (cd, cd, cd)
        yield hyview.Point(
            x=x, y=y, z=z, attrs={
                'label': label,
                'luminance': c,
                'Cd': color,
                'Alpha': cd,
            }
        )


def geogen(images, labels, group=None, **kwargs):
    """
    Helper to generate abstract data representations of the test neuron data.

    Parameters
    ----------
    images : numpy.array
    labels : numpy.array
    group : Optional[str]
        {'label', 'z'}
        Whether geo is generated by label, by z slice or other.
    kwargs : **Any
        See `pointgen`

    Returns
    -------
    Iterator[Tuple[str, hyview.Geometry]]
    """
    from hyview.c4 import C4

    points = defaultdict(list)

    piter = pointgen(images, labels, **kwargs)

    if group is None:
        points['*'] = piter
    else:
        for point in piter:
            if group == 'label':
                points[point.attrs['label']].append(point)
            elif group == 'z':
                points[point.z].append(point)
            else:
                raise NotImplementedError('Unknown group {!r}'.format(group))

    attributes = [
        hyview.AttributeDefinition(
            name='Cd', type='Point', default=(0.1, 0.1, 0.1)),
        hyview.AttributeDefinition(
            name='Alpha', type='Point', default=1.0),
        hyview.AttributeDefinition(
            name='luminance', type='Point', default=1),
        hyview.AttributeDefinition(
            name='label', type='Point', default=-1),
    ]

    for k, v in points.items():
        geo = hyview.Geometry(attributes=attributes, points=v)
        if k == '*':
            name = str(C4(kwargs))
        else:
            name = '{}-{}-{}'.format(group, k, C4(kwargs))
        yield name, geo


def build_neuron_sample(images, labels, **kwargs):
    """
    Helper to visualize the neuron dataset.

    Parameters
    ----------
    images : numpy.array
    labels : numpy.array
    kwargs : **Any
        See `geogen`.
    """
    kwargs.setdefault('group', 'z')
    for name, geo in geogen(images, labels, **kwargs):
        hyview.build(geo, name=name)


def build_slice(nth=3):
    """
    Visualize an image "slice".

    Parameters
    ----------
    nth : int
        Density of the points created. Skips to every `nth` point.
    """
    images, labels = load_data()

    build_neuron_sample(
        images, labels,
        group=None,
        colorize=False,
        size=1, znth=0, nth=nth, zmult=10)

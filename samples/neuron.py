"""
Sample module showcasing uses displaying datasets from neurons.

NOTE: Some thirdparty modules may be required to use some of these methods.
"""
import os
from collections import defaultdict

import hyview
import hyview.log
import samples.utils


_logger = hyview.log.get_logger(__name__)


TEST_H5PY_SAMPLE_PATH = os.path.join(
    os.path.dirname(__file__),
    '_data',
    'sample_A_20160501.hdf')


@hyview.rpc()
def mesh_all(names=None):
    """
    RPC method for "meshing" all geometry.

    Parameters
    ----------
    names : Optional[str]
    """
    import hyview.hy.core
    for node in hyview.hy.core.root().children():
        if names and node.name() not in names:
            continue
        last = node.children()[-1]
        if 'particlefluidsurface' in last.type().name():
            # already meshed
            continue
        p = node.createNode('particlefluidsurface')
        p.parm('particlesep').set(8)
        p.parm('transferattribs').set('Cd')
        p.setInput(0, last)
        p.setDisplayFlag(True)


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
    from samples.utils import ColorGenerator

    colors = ColorGenerator()

    it = samples.utils.iterfilter(
        images, labels, size=size, znth=znth, nth=nth, zmult=zmult)

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
        geo = hyview.Geometry(
            attributes=attributes, primitives=[hyview.Primitive(points=v)])
        if k == '*':
            name = str(C4(kwargs))
        else:
            name = '{}-{}-{}'.format(group, k, C4(kwargs))
        yield name, geo


def get_test_data():
    """
    Gets "images" and "labels" test numpy arrays.

    Returns
    -------
    Tuple[numpy.array, numpy.array]
    """
    return samples.utils.load_data_from_h5py(
        TEST_H5PY_SAMPLE_PATH, 'volumes/raw', 'volumes/labels/neuron_ids')


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
    images, labels = samples.utils.load_data_from_h5py(
        TEST_H5PY_SAMPLE_PATH, 'volumes/raw', 'volumes/labels/neuron_ids')

    build_neuron_sample(
        images, labels,
        group=None,
        colorize=False,
        size=1, znth=0, nth=nth, zmult=10)


def build_interesting(minimum=2000000, mesh=True):
    """
    Visualize interesting data structures within the neuron dataset.

    Parameters
    ----------
    minimum : int
        Filter to labels that have point counts over this number.
    mesh : bool
        Mesh the points.
    """
    _logger.info('Loading data from {!r}...'.format(TEST_H5PY_SAMPLE_PATH))

    images, labels = samples.utils.load_data_from_h5py(
        TEST_H5PY_SAMPLE_PATH, 'volumes/raw', 'volumes/labels/neuron_ids')

    _logger.info('Finding labels with more than {!r} entries...'.format(minimum))

    filters = list(samples.utils.iter_unique_by_count(labels, minimum=minimum))

    _logger.info('Filtering data...')

    for name, geo in geogen(
            images, labels,
            group='label',
            colorize=True,
            filters=filters,
            size=0, znth=0, nth=8, zmult=10):

        _logger.info('Sending {!r} to Houdini...'.format(name))

        hyview.build(geo, name=name)

    _logger.info('Meshing all geo...')

    if mesh:
        mesh_all()

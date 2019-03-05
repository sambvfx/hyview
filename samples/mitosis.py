"""
Sample module showcasing uses displaying datasets from a mitosis sample.

NOTE: Some thirdparty modules may be required to use some of these methods.
"""
import os

import hyview
import hyview.log


_logger = hyview.log.get_logger(__name__)


SAMPLE_PATH = os.path.join(
    os.path.dirname(__file__),
    '_data',
    'mitosis.tif')

Z_SCALE = 5.0


def load_data():
    from skimage import io

    # 5D array (time, z, y, x, channels(dna, microtubles))
    sample = io.imread(SAMPLE_PATH)

    return sample


def iterdata(data, size=None, znth=None, nth=None, zmult=Z_SCALE):

    import itertools

    if size:
        data = data[:size]

    def islice(it, n):
        if n:
            return itertools.islice(it, 0, None, n)
        return it

    for time, z_arrays in enumerate(data):
        for z, y_arrays in enumerate(islice(z_arrays, znth)):
            for y, x_arrays in enumerate(islice(y_arrays, nth)):
                for x, (dna, microtubules) in enumerate(islice(x_arrays, nth)):
                    yield int(time + 1), int(x), int(y), int(z * zmult), \
                          {'dna': int(dna), 'microtubles': int(microtubules)}


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


def pointgen(channel, minimum=3500, **kwargs):
    """
    Returns
    -------
    Iterator[Tuple[str, hyview.Geometry]]
    """
    from samples.utils import ColorGenerator

    colors = ColorGenerator()

    it = iterdata(load_data(), **kwargs)

    for time, x, y, z, channels in it:
        value = channels[channel]
        if minimum and value < minimum:
            continue
        color = colors.get(channel)
        yield hyview.Point(
            x=x, y=y, z=z, attrs={
                'Cd': color,
                'time': time,
                channel: value,
            }
        )


def geogen(channels, **kwargs):
    """
    Returns
    -------
    Iterator[Tuple[hyview.Geometry, str, int]]
    """
    from collections import defaultdict
    from hyview.c4 import C4

    attributes = [
        hyview.AttributeDefinition(
            name='Cd', type='Point', default=(0.1, 0.1, 0.1)),
        hyview.AttributeDefinition(
            name='time', type='Point', default=-1),
        hyview.AttributeDefinition(
            name='dna', type='Point', default=-1),
        hyview.AttributeDefinition(
            name='microtubles', type='Point', default=-1),
    ]

    for chan in channels:
        bytime = defaultdict(list)
        for point in pointgen(chan, **kwargs):
            bytime[point.attrs['time']].append(point)
        for frame, points in bytime.items():
            geo = hyview.Geometry(attributes=attributes, points=points)
            yield geo, 'mitosis-{}-{}'.format(chan, C4(kwargs)), frame


def build_interesting(channels=('dna', 'microtubles'), **kwargs):
    for geo, name, frame in geogen(channels, **kwargs):
        hyview.build(geo, name=name, frame=frame)

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


DEFAULTS = {
    'size': None,
    'znth': None,
    'nth': None,
    'zmult': 5.0,
    'colorize': False,
    'minimum': 0.5,
    'channels': ('dna',),
}


def sample(**kwargs):
    """
    Build a sample of the mitosis data set.
    """
    for geo, name, frame in geogen(**kwargs):
        hyview.build(geo, name=name, frame=frame)


def load_data():
    """
    Load the dataset from disk.

    Returns
    -------
    numpy.array
    """
    from skimage import io

    # 5D array (time, z, y, x, channels(dna, microtubles))
    return io.imread(SAMPLE_PATH)


def iterdata(data, **kwargs):
    """
    Helper to iterate over the dataset.

    Parameters
    ----------
    data : numpy.array
    kwargs : **Any
        size : Optional[int]
        znth : Optional[int]
        nth : Optionl[int]
        zmult : int
            Scale multiplier for z coordinate.

    Returns
    -------
    Iterator[Tuple[int, float, float, float, Dict[str, float]]]
    """
    import itertools

    size = kwargs.get('size', DEFAULTS['size'])
    znth = kwargs.get('znth', DEFAULTS['znth'])
    nth = kwargs.get('nth', DEFAULTS['nth'])
    zmult = kwargs.get('zmult', DEFAULTS['zmult'])

    if size:
        data = data[:size]

    def islice(it, n):
        if n:
            return itertools.islice(it, 0, None, n)
        return it

    for time, z_arrays in enumerate(data):
        for z, y_arrays in enumerate(islice(z_arrays, znth)):
            for y, x_arrays in enumerate(islice(y_arrays, nth)):
                minimum = float(x_arrays.min())
                maximum = float(x_arrays.max()) - minimum
                for x, (dna, microtubules) in enumerate(islice(x_arrays, nth)):
                    yield int(time + 1), float(x), float(y), float(z * zmult), \
                          {'dna': float(dna - minimum) / maximum,
                           'microtubles': float(microtubules - minimum) / maximum}


def pointgen(channel, **kwargs):
    """
    Parameters
    ----------
    channel : str
    kwargs : **Any
        colorize : bool
        minimum : float

    Returns
    -------
    Iterator[hyview.Point]
    """
    from hyview_samples.utils import ColorGenerator

    minimum = kwargs.get('minimum', DEFAULTS['minimum'])
    colorize = kwargs.get('colorize', DEFAULTS['colorize'])

    colors = ColorGenerator()

    for time, x, y, z, channels in iterdata(load_data(), **kwargs):
        value = channels[channel]
        if minimum and value < minimum:
            continue
        if colorize:
            color = colors.get(channel)
        else:
            color = (value, value, value)
        yield hyview.Point(
            x=x, y=y, z=z, attrs={
                'Cd': color,
                'Alpha': value,
                'time': time,
                channel: value,
            }
        )


def geogen(**kwargs):
    """
    Parameters
    ----------
    kwargs : **Any
        channels : Iterable[str]

    Returns
    -------
    Iterator[Tuple[hyview.Geometry, str, int]]
    """
    from collections import defaultdict
    from hyview.c4 import C4

    channels = kwargs.get('channels', DEFAULTS['channels'])

    # Do this for the hash!
    for k, v in DEFAULTS.items():
        kwargs.setdefault(k, v)

    attributes = [
        hyview.AttributeDefinition(
            name='Cd', type='Point', default=(0.1, 0.1, 0.1)),
        hyview.AttributeDefinition(
            name='Alpha', type='Point', default=1.0),
        hyview.AttributeDefinition(
            name='time', type='Point', default=-1),
        hyview.AttributeDefinition(
            name='dna', type='Point', default=0.0),
        hyview.AttributeDefinition(
            name='microtubles', type='Point', default=0.0),
    ]

    for chan in channels:
        bytime = defaultdict(list)
        for point in pointgen(chan, **kwargs):
            bytime[point.attrs['time']].append(point)
        for frame, points in bytime.items():
            geo = hyview.Geometry(attributes=attributes, points=points)
            yield geo, 'mitosis-{}-{}'.format(
                chan, C4(kwargs)), frame

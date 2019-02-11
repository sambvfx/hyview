"""
Misc helper tools for interacting with data.
"""


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
    Iterator[Tuple[int, int, int, int, int]]
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
                yield int(label), int(x), int(y), int(z * zmult), int(c)


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


def point_generator(size=None):
    import random
    import hyview.interface

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


def color_gen(precision=3):
    import random
    while True:
        yield round(random.random(), precision), \
              round(random.random(), precision), \
              round(random.random(), precision)


class ColorGenerator(object):
    """
    Object for generating random colors forever. Can also remember colors by
    name to ensure you get the same results.
    """
    def __init__(self, colors=None):
        if colors is None:
            colors = color_gen()
        else:
            colors = iter(colors)
        self._colors = colors
        self._iter = None
        self._cache = {}
        self.reset()

    def reset(self):
        self._iter = iter(self._colors)

    def __call__(self, name=None):
        return self.get(name=name)

    def __iter__(self):
        while True:
            yield self.next()

    def next(self):
        try:
            return next(self._iter)
        except StopIteration:
            self.reset()
            return self.next()

    def get(self, name=None):
        if name is None:
            return self.next()
        result = self._cache.get(name)
        if result is None:
            result = self.next()
            self._cache[name] = result
        return result

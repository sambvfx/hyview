"""
Misc helper tools for interacting with data.
"""
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

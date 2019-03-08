"""
Misc helper tools.
"""
from typing import *


def color_gen(precision=3):
    """
    Generate random RGB colors forever.

    Parameters
    ----------
    precision : int
        Float precision.

    Returns
    -------
    Tuple[float, float, float]
    """
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
        self._cache = None  # type: Dict[Hashable, Tuple[float, float, float]]
        self.reset()

    def reset(self):
        self._cache = {}
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

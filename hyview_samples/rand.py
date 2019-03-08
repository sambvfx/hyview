import random
import hyview
from hyview_samples.utils import ColorGenerator


def point_generator(size):
    """
    Generate random points.

    Parameters
    ----------
    size : int

    Returns
    -------
    Iterator[hyview.Point]
    """
    colors = ColorGenerator()

    for _ in range(size):
        yield hyview.Point(
            x=random.random() * 100,
            y=random.random() * 100,
            z=random.random() * 100,
            attrs={
                'Cd': colors.next(),
            }
        )


def get_geo(size=200):
    """
    Get a Geometry object with `size` points.

    Parameters
    ----------
    size : int

    Returns
    -------
    hyview.Geometry
    """
    return hyview.Geometry(
        attributes=[
            hyview.AttributeDefinition(
                name='Cd',
                type='Point',
                default=(0.1, 0.1, 0.1)
            ),
        ],
        points=list(point_generator(size=size)))


def sample(size=200):
    """
    Generate some random sample points.

    Parameters
    ----------
    size : int
        Number of points.
    """
    hyview.build(get_geo(size=size))

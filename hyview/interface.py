"""
Abstract representations of Houdini objects.
"""
import attr
from attr.validators import in_ as choices

from typing import *


@attr.s
class AttributeDefinition(object):
    """
    Abstract representation of a Houdini attribute. This is the definition of
    what attributes look like, and the values should be part of other objects
    `attrs` attributes (e.g. `Point.attrs`).

    Houdini reserves certain attribute names for specific purposes.
    For a complete list visit:
        http://www.sidefx.com/docs/houdini/model/attributes.html#attributes

    Examples
    --------
    >>> color_attribute = AttributeDefinition(
    ...     name='Cd',
    ...     type=AttributeDefinition.Types.Point,
    ...     default=(0.1, 0.1, 0.1))
    """
    class Types:
        Global = 'Global'
        Point = 'Point'
        Prim = 'Prim'
        Vertex = 'Vertex'
        ALL = [Global, Point, Prim, Vertex]

    name = attr.ib(type=str)
    type = attr.ib(type=str, validator=choices(Types.ALL))
    default = attr.ib(type=Union[str, Tuple, int, float], default=-1)


@attr.s
class Point(object):
    """
    Abstract represention of a Houdini point.

    A point is simply a point in 3D space with optional custom attributes
    associated with it.

    For reference:
        http://www.sidefx.com/docs/houdini/model/points.html
    """
    x = attr.ib(type=int)
    y = attr.ib(type=int)
    z = attr.ib(type=int)
    attrs = attr.ib(
        type=Dict[str, Any],
        default=attr.Factory(dict))

    @property
    def pos(self):
        # type: () -> Tuple[int, int, int]
        return self.x, self.y, self.z


@attr.s
class Geometry(object):
    """
    Abstract representation of a Houdini geometry.

    A geometry is a simple container of points.

    For reference:
        http://www.sidefx.com/docs/houdini/basics/objects.html
    """
    attributes = attr.ib(
        type=Iterable[AttributeDefinition],
        default=attr.Factory(list),
        repr=False)
    points = attr.ib(
        type=Iterable[Point],
        default=attr.Factory(list),
        repr=False)

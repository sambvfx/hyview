"""
Abstract representations of Houdini objects.
"""
import attr
from attr.validators import in_ as choices

from typing import *


@attr.s
class AttributeDefinition(object):
    name = attr.ib(type=str)
    type = attr.ib(type=str, validator=choices([
        'Global',
        'Point',
        'Prim',
        'Vertex',
    ]))
    default = attr.ib(type=Union[str, Tuple, int, float], default=-1)


@attr.s
class Point(object):
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
class Primitive(object):
    points = attr.ib(
        type=List[Point],
        default=attr.Factory(list),
        repr=False)
    attrs = attr.ib(
        type=Dict[str, Any],
        default=attr.Factory(dict))


@attr.s
class Geometry(object):
    attributes = attr.ib(
        type=List[AttributeDefinition],
        default=attr.Factory(list),
        repr=False)
    primitives = attr.ib(
        type=List[Primitive],
        default=attr.Factory(list),
        repr=False)

import attr

import hyview.interface


def serialize(obj):
    return attr.asdict(obj)


def deserialize(obj):
    return hyview.interface.Point(**obj)

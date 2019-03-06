import hyview


def sample(size=200):

    from samples.utils import point_generator

    attributes = [
        hyview.AttributeDefinition(
            name='Cd', type='Point', default=(0.1, 0.1, 0.1)),
        hyview.AttributeDefinition(
            name='luminance', type='Point', default=1),
        hyview.AttributeDefinition(
            name='label', type='Point', default=-1),
    ]

    geo = hyview.Geometry(
        attributes=attributes, points=point_generator(size=size))

    hyview.build(geo)

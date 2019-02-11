import hyview


def random_data(size=200):

    from samples.utils import point_generator

    app = hyview.app()

    primitive = hyview.Primitive(
        points=list(point_generator(size=size)))

    attributes = [
        hyview.AttributeDefinition(
            name='Cd', type='Point', default=(0.1, 0.1, 0.1)),
        hyview.AttributeDefinition(
            name='luminance', type='Point', default=1),
        hyview.AttributeDefinition(
            name='label', type='Point', default=-1),
    ]

    geo = hyview.Geometry(
        attributes=attributes, primitives=[primitive])

    app.build(geo)

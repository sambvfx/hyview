"""
Sample module showcasing uses displaying datasets from neurons.

NOTE: Some thirdparty modules may be required to use some of these methods.
"""
import os
from collections import defaultdict

import hyview
import samples.utils


@hyview.rpc()
def mesh_all(self, names=None):
    """
    RPC method for "meshing" all geometry.

    Parameters
    ----------
    self : hyview.hy.implementation.HoudiniApplicationController
    names : Optional[str]
    """
    for name, node in self.nodes.items():
        if names and name not in names:
            continue
        last = node.children()[-1]
        p = node.createNode('particlefluidsurface')
        p.parm('particlesep').set(8)
        p.parm('transferattribs').set('Cd')
        p.setInput(0, last)
        p.setDisplayFlag(True)


TEST_H5PY_SAMPLE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    '_data',
    'sample_A_20160501.hdf')


def neuron_sample(images, labels, by_label=False, colorize=False,
                  filters=None, size=None, znth=None, nth=None, zmult=10):
    from hyview.c4 import C4
    from samples.utils import ColorGenerator

    app = hyview.app()

    colors = ColorGenerator()

    it = samples.utils.iterfilter(
        images, labels, size=size, znth=znth, nth=nth, zmult=zmult)

    points = defaultdict(list)

    for label, x, y, z, c in it:
        if filters and label not in filters:
            continue
        cd = float(c) / 255.0
        if colorize:
            color = colors.get(label)
        else:
            color = (cd, cd, cd)
        point = hyview.Point(
            x=x, y=y, z=z, attrs={
                'label': label,
                'luminance': c,
                'Cd': color,
                'Alpha': cd,
            }
        )
        points[label if by_label else '*'].append(point)

    primitives = []

    for k, v in points.items():
        primitive = hyview.Primitive(points=v)
        primitives.append(primitive)
        attributes = [
            hyview.AttributeDefinition(
                name='Cd', type='Point', default=(0.1, 0.1, 0.1)),
            hyview.AttributeDefinition(
                name='Alpha', type='Point', default=1.0),
            hyview.AttributeDefinition(
                name='luminance', type='Point', default=1),
            hyview.AttributeDefinition(
                name='label', type='Point', default=-1),
        ]

        geo = hyview.Geometry(
            attributes=attributes, primitives=[primitive])

        if by_label:
            app.build(geo, name='label-{}-{}'.format(
                k, C4(filters, size, znth, nth, zmult)))
        else:
            app.build(geo)


def neuron_sample_from_h5py(path, **kwargs):
    images, labels = samples.utils.load_data_from_h5py(
        path, 'volumes/raw', 'volumes/labels/neuron_ids')

    neuron_sample(images, labels, **kwargs)


def mesh():
    # Generate some data
    neuron_sample_from_h5py(
        TEST_H5PY_SAMPLE_PATH, by_label=True,
        colorize=True,
        filters=[4944, 20474],
        size=0, znth=0, nth=5, zmult=10)

    app = hyview.app()
    app.mesh_all()


def build_interesting(minimum=2000000):
    images, labels = samples.utils.load_data_from_h5py(
        TEST_H5PY_SAMPLE_PATH, 'volumes/raw', 'volumes/labels/neuron_ids')

    neuron_sample(
        images, labels,
        by_label=True,
        colorize=True,
        filters=list(iter_unique_by_count(labels, minimum=minimum)),
        size=0, znth=0, nth=8, zmult=10)

    app = hyview.app()
    app.mesh_all()

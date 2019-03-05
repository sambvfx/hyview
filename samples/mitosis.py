"""
Sample module showcasing uses displaying datasets from a mitosis sample.

NOTE: Some thirdparty modules may be required to use some of these methods.
"""
import os

import hyview
import hyview.log


_logger = hyview.log.get_logger(__name__)


SAMPLE_PATH = os.path.join(
    os.path.dirname(__file__),
    '_data',
    'mitosis.tif')

Z_SCALE = 1.0 / 0.088


def load_data():
    from skimage import io
    import numpy as np

    # 5D array (time, z, channel, y, x)
    sample = io.imread(SAMPLE_PATH)

    # (time, z, y, x, channel)
    sample = np.transpose(sample, (0, 1, 3, 4, 2))


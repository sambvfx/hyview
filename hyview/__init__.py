"""
Houdini RPC
"""
__version__ = '0.0.1'

__title__ = 'hyview'
__description__ = 'RPC Houdini Data Visualizer'
__url__ = 'https://github.com/sambvfx/hyview'
__uri__ = __url__

__author__ = 'Sam Bourne'
__contact__ = 'sambvfx@gmail.com'

__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2019 Sam Bourne'


from hyview.log import get_logger

from hyview.plugins import rpc

from hyview.app import app, build
from hyview.hy.init import start_houdini

from hyview.interface import AttributeDefinition, Point, Geometry

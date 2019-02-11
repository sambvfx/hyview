"""
Houdini data visualizer.
"""
__version__ = '0.0.1'
__author__ = 'Sam Bourne'
__contact__ = 'sambvfx@gmail.com'
__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2019 Sam Bourne'


from hyview.interface import AttributeDefinition, Point, Primitive, Geometry
from hyview.registry import register as rpc

from hyview.transport import start, app
from hyview.hy.transport import start_houdini

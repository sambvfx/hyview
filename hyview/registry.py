"""
Registry layer to support registering custom RPC commands to execute in
Houdini.

Registered methods methods will be patched onto the
`hyview.hy.implementation.HoudiniApplicationController` as instance methods
and can be interfaced with like any of the other rpc commands.

Registered methods should accept `self` as the first arg.
"""
import sys
import os
import six
import uuid
from kids.cache import cache

import hyview.log


from typing import *


_logger = hyview.log.get(__name__)


ModuleType = type(sys)


class Registry(object):

    registered = {}

    @classmethod
    def register(cls, name=None):
        def _deco(f):
            if name is None:
                fname = f.__name__
            else:
                fname = name
            _logger.debug('Registering custom method {!r}'.format(fname))
            if fname in cls.registered:
                raise ValueError('{!r} is already a registered method name')
            cls.registered[fname] = f
            return f
        return _deco

    @classmethod
    @cache
    def initialize(cls, paths=None):
        paths = paths or os.environ.get('HYVIEW_PLUGIN_PATH')
        if paths:
            import_modules(paths)

    @classmethod
    def new(cls, obj):
        cls.initialize()
        return type(obj.__name__, tuple([obj]), dict(cls.registered))


register = Registry.register


def iter_modules(paths):
    # type: (Union[str, Iterable[str]]) -> List[str]
    """
    Get filepaths for all valid python modules from `paths`.

    Parameters
    ----------
    paths : Union[str, Iterable[str]]
        Supports various path separation methods: e.g.
           - '/project/package/mymodule.py'
           - '/project/package'
           - '/project/package:project/package/mymodule.py'
           - ['/project/package']

    Returns
    -------
    List[str]
    """
    import pydoc

    if isinstance(paths, six.string_types):
        paths = paths.split(os.pathsep)

    for path in paths:
        path = os.path.expanduser(os.path.expandvars(path))
        # ignore empty paths
        path = path.strip()
        if not path:
            continue

        obj = pydoc.locate(path)
        if obj:
            if obj.__file__.endswith('pyc'):
                yield obj.__file__[:-1]
            else:
                yield obj.__file__
        else:
            if os.path.isfile(path) and path.endswith('py'):
                yield path
            elif os.path.isdir(path):
                for base, directories, filenames in os.walk(path):
                    for filename in filenames:
                        if filename.endswith('py'):
                            yield os.path.join(base, filename)
            else:
                raise ValueError(
                    'Cannot locate plugin path {!r}'.format(path))


def import_modules(paths):
    # type: (Union[str, Iterable[str]]) -> List[ModuleType]
    """
    Import modules from `paths`.

    Parameters
    ----------
    paths : Union[str, Iterable[str]]

    Returns
    -------
    List[ModuleType]
    """
    def _py2_import(name, path):
        # import modules for python 2
        import imp
        return imp.load_source(name, path)

    def _py33_to_34_import(name, path):
        # import modules for python 3.3 and 3.4
        from importlib.machinery import SourceFileLoader
        return SourceFileLoader(name, path).load_module()

    def _py35plus_import(name, path):
        # import modules for python 3.5+
        import importlib.util
        spec = importlib.util.spec_from_file_location(name, path)
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)
        return foo

    if sys.version_info[0] == 3 and sys.version_info[1] in (3, 4):
        loader = _py33_to_34_import
    elif sys.version_info[0] == 3 and sys.version_info[1] >= 5:
        loader = _py35plus_import
    else:
        loader = _py2_import

    return [loader(uuid.uuid4().hex, mod) for mod in set(iter_modules(paths))]

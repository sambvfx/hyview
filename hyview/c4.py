"""
Module for generating C4 ids.
"""
import os
import inspect
import hashlib

try:
    import cPickle as pickle
except ImportError:
    import pickle

import six

from kids.cache import hashing

from typing import *


# Used to indentify filepaths where C4 will hash the contents of the filepath
# as part of it's id generation.
PATH_TYPES = [six.string_types]
try:
    import pathlib
except ImportError:
    pass
else:
    PATH_TYPES.append(pathlib.Path)


__all__ = [
    'C4',
    'C4Error',
    'to_bytes',
]


class C4Error(Exception):
    """
    Raised if an object is encountered that cannot be hashed without a custom
    hash implementation.
    """
    pass


def to_bytes(obj):
    """
    Helper to generate bytes from a variety of objects.

    Parameters
    ----------
    obj : Any

    Returns
    -------
    bytes
    """
    if isinstance(obj, six.binary_type):
        return obj
    elif isinstance(obj, six.string_types):
        # python3 uses utf-8 as the default encoding and there is a small
        # performance improvement not providing the default value.
        if six.PY2:
            return obj.encode('utf-8')
        return obj.encode()
    elif isinstance(obj, int):
        return obj.to_bytes((obj.bit_length() + 7) // 8, 'big', signed=obj < 0)

    try:
        # FIXME: Could this end up in a recursive loop with some broken
        #  __hash__ implementation on a custom object?
        return to_bytes(hash(hashing(strict=False, typed=True)(obj)))
    except ValueError:
        try:
            # Try to simply pickling the object.
            return pickle.dumps(obj)
        except ValueError:
            raise C4Error(
                'Can not hash {!r}. Consider registering a custom hasher for '
                'your object. See `C4.register` for more information.')


def _b58encode(b):
    """
    Base58 encode bytes to string.

    Parameters
    ----------
    b : bytes

    Returns
    -------
    str
    """
    __b58chars = '123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
    __b58base = len(__b58chars)
    if six.PY2:
        long_value = int(b.encode("hex_codec"), 16)
    else:
        long_value = int(b.hex(), 16)

    result = ''
    while long_value >= __b58base:
        div, mod = divmod(long_value, __b58base)
        result = __b58chars[mod] + result
        long_value = div

    result = __b58chars[long_value] + result

    return result


class C4(object):
    """
    An object used to generate a C4 id for provided data. Provided the same
    data this will generate the same id string.

    A C4 hash is essentially a `hashlib.sha512()` hash  with certain
    characters removed to make the ids easy to pass around.

    Examples
    --------
    >>> c4 = C4('foo')
    >>> str(c4)
    # 'c45XyDwWmrPQwJPdULBhma6LGNaLghKtN7R9vLn2tFrepZJ9jJFSDzpCKei11EgA5r1veenBu3Q8qfvWeDuPc7fJK2'

    >>> c4.update('bar')
    >>> str(c4)
    # 'c41cXCrFq1EfA5ADVN2C8Nev2kN35H3QEarxFe9h39yh7QzoxK4DKaHUJ3RYvWC1wxyFJjwmHQqUucNwCYn2hFvEBF'

    >>> assert c4 == C4('foo', 'bar')

    C4 also consider the contents of any filepaths provided.

    >>> with open('/tmp/c4example', 'wb') as f:
    ...     f.write(b'foo')
    >>> c4_1 = C4('/tmp/c4example')
    >>> with open('/tmp/c4example', 'wb') as f:
    ...     f.write(b'bar')
    >>> c4_2 = C4('/tmp/c4example')
    >>> assert c4_1 != c4_2
    """
    _hashers = []  # type: List[Tuple[Callable[Any, bool], Callable[Any, Union[bytes, Iterator[bytes]]]]]

    @classmethod
    def register(cls, claim_func):
        """
        Decorator for registering a callable to hash certain object types.
        This method is called with a callable which can "claim" an object to
        be responsible for hashing it.

        Parameters
        ----------
        claim_func : Callable[Any, bool]

        Returns
        -------
        Callable[Any, Union[bytes, Iterator[bytes]]]
        """
        def _deco(f):
            cls._hashers.insert(0, (claim_func, f))
            return f
        return _deco

    def __init__(self, *objects):
        self._hash = hashlib.sha512()
        if objects:
            self.update(*objects)

    def __str__(self):
        c4_id_length = 90
        b58_hash = _b58encode(self._hash.digest())

        # pad with '1's if needed
        padding = ''
        if len(b58_hash) < (c4_id_length - 2):
            padding = ('1' * (c4_id_length - 2 - len(b58_hash)))

        # combine to form C4 ID
        string_id = 'c4' + padding + b58_hash
        return string_id

    def __repr__(self):
        return '<{}({!r})>'.format(self.__class__.__name__, str(self))

    def __eq__(self, other):
        if not isinstance(other, C4):
            return False
        return str(self) == str(other)

    def update(self, *objects):
        """
        Update the data within the c4 hash.

        Parameters
        ----------
        objects : *Any
        """
        for obj in objects:
            for claim, f in self._hashers:
                if claim(obj):
                    if inspect.isgeneratorfunction(f):
                        for block in f(obj):
                            self._hash.update(block)
                    else:
                        self._hash.update(f(obj))
                    break
            else:
                self._hash.update(to_bytes(obj))


def _claim_c4(obj):
    return isinstance(obj, C4)


@C4.register(_claim_c4)
def hash_c4(obj):
    return to_bytes(str(obj))


def _claim_filepath(obj):
    return isinstance(obj, tuple(PATH_TYPES)) and os.sep in str(obj) and \
           os.path.exists(obj)


@C4.register(_claim_filepath)
def hash_filepath(obj):
    """
    Yield bytes from the contents of a filepath.

    Parameters
    ----------
    obj : six.string_types

    Returns
    -------
    Iterator[bytes]
    """
    with open(obj, 'r') as f:
        block_size = 100 * (2 ** 20)
        cnt_blocks = 0
        while True:
            try:
                block = f.read(block_size)
            except UnicodeDecodeError:
                break
            if not block:
                break
            if six.PY3:
                block = block.encode('utf-8')
            yield block
            cnt_blocks = cnt_blocks + 1
        f.close()

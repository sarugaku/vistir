# -*- coding=utf-8 -*-
from __future__ import absolute_import, unicode_literals
import sys
import six

if sys.version_info >= (3, 5):
    from pathlib import Path
else:
    from pathlib2 import Path

if sys.version_info < (3, 3):
    from backports.shutil_get_terminal_size import get_terminal_size
else:
    from shutil import get_terminal_size

try:
    from weakref import finalize
except ImportError:
    from backports.weakref import finalize

try:
    from functools import partialmethod
except:
    from .backports.functools import partialmethod

try:
    from json import JSONDecodeError
except ImportError:     # Old Pythons.
    JSONDecodeError = ValueError

if six.PY2:
    class ResourceWarning(Warning):
        pass

    class FileNotFoundError(IOError):
        pass

ResourceWarning = ResourceWarning
FileNotFoundError = FileNotFoundError


def fs_str(string):
    """Encodes a string into the proper filesystem encoding

    Borrowed from pip-tools
    """
    if isinstance(string, str):
        return string
    assert not isinstance(string, bytes)
    return string.encode(_fs_encoding)


_fs_encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()

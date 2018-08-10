# -*- coding=utf-8 -*-
from __future__ import absolute_import, unicode_literals

__all__ = [
    "NamedTemporaryFile",
    "TemporaryDirectory",
]

from .tempfile import NamedTemporaryFile, TemporaryDirectory
from .functools import partialmethod

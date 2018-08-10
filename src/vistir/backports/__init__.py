# -*- coding=utf-8 -*-
from __future__ import absolute_import, unicode_literals

from .functools import partialmethod
from .tempfile import NamedTemporaryFile, TemporaryDirectory


__all__ = [
    "NamedTemporaryFile",
    "TemporaryDirectory",
    "partialmethod"
]

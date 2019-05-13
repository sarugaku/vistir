# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import os


def is_type_checking():
    try:
        from typing import TYPE_CHECKING
    except ImportError:
        return False
    return TYPE_CHECKING


MYPY_RUNNING = os.environ.get("MYPY_RUNNING", is_type_checking())

# -*- coding=utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os
import stat


READ_ONLY = stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
NON_WRITEABLE = ~stat.S_IWUSR & ~stat.S_IWGRP & ~stat.S_IWOTH
NON_WRITE_OR_EXEC = NON_WRITEABLE & ~stat.S_IXUSR & ~stat.S_IXGRP & ~stat.S_IXOTH
WRITEABLE = stat.S_IWUSR | stat.S_IWGRP


def get_mode(fn):
    return stat.S_IMODE(os.lstat(fn).st_mode)


def read_file(fn):
    contents = ""
    with open(fn, "r") as fh:
        contents = fh.read().strip()
    return contents

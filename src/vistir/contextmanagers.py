# -*- coding=utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
import os
import sys

from contextlib import contextmanager

import six

from .compat import Path
from .misc import run
from .path import is_file_url, url_to_path


__all__ = ["temp_environ", "temp_path", "cd", "atomic_open_for_write", "open_file"]


# Borrowed from Pew.
# See https://github.com/berdario/pew/blob/master/pew/_utils.py#L82
@contextmanager
def temp_environ():
    """Allow the ability to set os.environ temporarily"""
    environ = dict(os.environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(environ)


@contextmanager
def temp_path():
    """A context manager which allows the ability to set sys.path temporarily

    >>> path_from_virtualenv = load_path("/path/to/venv/bin/python")
    >>> print(sys.path)
    ['/home/user/.pyenv/versions/3.7.0/bin', '/home/user/.pyenv/versions/3.7.0/lib/python37.zip', '/home/user/.pyenv/versions/3.7.0/lib/python3.7', '/home/user/.pyenv/versions/3.7.0/lib/python3.7/lib-dynload', '/home/user/.pyenv/versions/3.7.0/lib/python3.7/site-packages']
    >>> with temp_path():
            sys.path = path_from_virtualenv
            # Running in the context of the path above
            run(["pip", "install", "stuff"])
    >>> print(sys.path)
    ['/home/user/.pyenv/versions/3.7.0/bin', '/home/user/.pyenv/versions/3.7.0/lib/python37.zip', '/home/user/.pyenv/versions/3.7.0/lib/python3.7', '/home/user/.pyenv/versions/3.7.0/lib/python3.7/lib-dynload', '/home/user/.pyenv/versions/3.7.0/lib/python3.7/site-packages']

    """
    path = [p for p in sys.path]
    try:
        yield
    finally:
        sys.path = [p for p in path]


@contextmanager
def cd(path):
    """Context manager to temporarily change working directories

    :param str path: The directory to move into

    >>> print(os.path.abspath(os.curdir))
    '/home/user/code/myrepo'
    >>> with cd("/home/user/code/otherdir/subdir"):
            print("Changed directory: %s" % os.path.abspath(os.curdir))
    Changed directory: /home/user/code/otherdir/subdir
    >>> print(os.path.abspath(os.curdir))
    '/home/user/code/myrepo'
    """
    if not path:
        return
    prev_cwd = Path.cwd().as_posix()
    if isinstance(path, Path):
        path = path.as_posix()
    os.chdir(str(path))
    try:
        yield
    finally:
        os.chdir(prev_cwd)


@contextmanager
def atomic_open_for_write(target, binary=False, newline=None, encoding=None):
    """Atomically open `target` for writing.

    This is based on Lektor's `atomic_open()` utility, but simplified a lot
    to handle only writing, and skip many multi-process/thread edge cases
    handled by Werkzeug.

    How this works:

    * Create a temp file (in the same directory of the actual target), and
      yield for surrounding code to write to it.
    * If some thing goes wrong, try to remove the temp file. The actual target
      is not touched whatsoever.
    * If everything goes well, close the temp file, and replace the actual
      target with this new file.
    """
    from ._compat import NamedTemporaryFile

    mode = "w+b" if binary else "w"
    f = NamedTemporaryFile(
        dir=os.path.dirname(target),
        prefix=".__atomic-write",
        mode=mode,
        encoding=encoding,
        newline=newline,
        delete=False,
    )
    # set permissions to 0644
    os.chmod(f.name, stat.S_IWUSR | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    try:
        yield f
    except BaseException:
        f.close()
        try:
            os.remove(f.name)
        except OSError:
            pass
        raise
    else:
        f.close()
        try:
            os.remove(target)  # This is needed on Windows.
        except OSError:
            pass
        os.rename(f.name, target)  # No os.replace() on Python 2.


@contextmanager
def open_file(link, session=None):
    """
    Open local or remote file for reading.

    :type link: pip._internal.index.Link or str
    :type session: requests.Session
    :raises ValueError: If link points to a local directory.
    :return: a context manager to the opened file-like object
    """
    if not isinstance(link, six.string_types):
        try:
            link = link.url_without_fragment
        except AttributeError:
            raise ValueError("Cannot parse url from unkown type: {0!r}".format(link))

    if is_file_url(link):
        # Local URL
        local_path = url_to_path(link)
        if os.path.isdir(local_path):
            raise ValueError("Cannot open directory for read: {}".format(url))
        else:
            with open(local_path, "rb") as local_file:
                yield local_file
    else:
        # Remote URL
        headers = {"Accept-Encoding": "identity"}
        if not session:
            from requests import Session

            session = Session()
        response = session.get(url, headers=headers, stream=True)
        try:
            yield response.raw
        finally:
            response.close()

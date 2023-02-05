# -*- coding=utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import contextlib
import importlib
import io
import os
import shutil
import sys
import warnings

import pytest

from vistir import contextmanagers

from .utils import read_file

from unittest.mock import patch


GUTENBERG_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "fixtures/gutenberg_document.txt"
)


def is_fp_closed(fp):
    try:
        return fp.isclosed()
    except AttributeError:
        pass
    try:
        return fp.closed
    except AttributeError:
        pass
    try:
        return fp.fp is None
    except AttributeError:
        pass
    raise ValueError("could not find fp on object")


class MockUrllib3Response(object):
    def __init__(self, path):
        self._fp = io.open(path, "rb")
        self._fp_bytes_read = 0
        self.auto_close = True
        self.length_remaining = 799738

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    def stream(self, amt=2 ** 16, decode_content=None):
        while not is_fp_closed(self._fp):
            data = self.read(amt=amt, decode_content=decode_content)
            if data:
                yield data

    def close(self):
        if not self.closed:
            self._fp.close()

    @property
    def closed(self):
        if not self.auto_close:
            return io.IOBase.closed.__get__(self)
        elif self._fp is None:
            return True
        elif hasattr(self._fp, "isclosed"):
            return self._fp.isclosed()
        elif hasattr(self._fp, "closed"):
            return self._fp.closed
        else:
            return True

    def fileno(self):
        if self._fp is None:
            raise IOError("HTTPResponse has no file to get a fileno from")
        elif hasattr(self._fp, "fileno"):
            return self._fp.fileno()
        else:
            raise IOError(
                "The file-like object this HTTPResponse is wrapped "
                "around has no file descriptor"
            )

    def readinto(self, b):
        # This method is required for `io` module compatibility.
        temp = self.read(len(b))
        if len(temp) == 0:
            return 0
        else:
            b[: len(temp)] = temp
            return len(temp)

    @property
    def data(self):
        if self._body:
            return self._body
        if self._fp:
            return self.read(cache_content=True)

    def read(self, amt=None, decode_content=None, cache_content=False):
        if self._fp is None:
            return
        fp_closed = getattr(self._fp, "closed", False)
        if amt is None:
            # cStringIO doesn't like amt=None
            data = self._fp.read() if not fp_closed else b""
            flush_decoder = True
        else:
            cache_content = False
            data = self._fp.read(amt) if not fp_closed else b""
            if amt != 0 and not data:  # Platform-specific: Buggy versions of Python.
                self._fp.close()

        if data:
            self._fp_bytes_read += len(data)
            if self.length_remaining is not None:
                self.length_remaining -= len(data)

            if cache_content:
                self._body = data

        return data

    def isclosed(self):
        return is_fp_closed(self._fp)

    def tell(self):
        """
        Obtain the number of bytes pulled over the wire so far. May differ from
        the amount of content returned by :meth:``HTTPResponse.read`` if bytes
        are encoded on the wire (e.g, compressed).
        """
        return self._fp_bytes_read

    def __iter__(self):
        buffer = []
        for chunk in self.stream(decode_content=True):
            if b"\n" in chunk:
                chunk = chunk.split(b"\n")
                yield b"".join(buffer) + chunk[0] + b"\n"
                for x in chunk[1:-1]:
                    yield x + b"\n"
                if chunk[-1]:
                    buffer = [chunk[-1]]
                else:
                    buffer = []
            else:
                buffer.append(chunk)
        if buffer:
            yield b"".join(buffer)


def test_path():
    old_path = sys.path
    new_path = sys.path[2:]
    with contextmanagers.temp_path():
        sys.path = new_path
        assert sys.path == new_path
    assert sys.path == old_path


def test_cd(tmpdir):
    second_dir = tmpdir.join("second_dir").mkdir()
    original_dir = os.path.abspath(os.curdir)
    assert original_dir != os.path.abspath(second_dir.strpath)
    with contextmanagers.cd(second_dir.strpath):
        assert os.path.abspath(os.curdir) == os.path.abspath(second_dir.strpath)
    assert os.path.abspath(os.curdir) == original_dir


def test_environ():
    os.environ["VISTIR_TEST_KEY"] = "test_value"
    assert os.environ.get("VISTIR_OTHER_KEY") is None
    with contextmanagers.temp_environ():
        os.environ["VISTIR_TEST_KEY"] = "temporary test value"
        os.environ["VISTIR_OTHER_KEY"] = "some_other_key_value"
        assert os.environ["VISTIR_TEST_KEY"] == "temporary test value"
        assert os.environ["VISTIR_OTHER_KEY"] == "some_other_key_value"
    assert os.environ["VISTIR_TEST_KEY"] == "test_value"
    assert os.environ.get("VISTIR_OTHER_KEY") is None


def test_atomic_open(tmpdir, monkeypatch):
    test_file = tmpdir.join("test_file.txt")
    replace_with_text = "new test text"
    test_file.write_text("some test text", encoding="utf-8")
    assert read_file(test_file.strpath) == "some test text"

    # Raise an error to make sure we don't write text on errors
    def raise_exception_while_writing(filename, new_text):
        with contextmanagers.atomic_open_for_write(filename) as fh:
            fh.write(new_text)
            raise RuntimeError("This should not overwrite the file")

    def raise_oserror_on_chmod(path, mode, dir_fd=None, follow_symlinks=True):
        raise OSError("No permission!")

    try:
        raise_exception_while_writing(test_file.strpath, replace_with_text)
    except RuntimeError:
        pass
    # verify that the file is not overwritten
    assert read_file(test_file.strpath) == "some test text"
    with contextmanagers.atomic_open_for_write(test_file.strpath) as fh:
        fh.write(replace_with_text)
    # make sure that we now have the new text in the file
    assert read_file(test_file.strpath) == replace_with_text
    another_test_file = tmpdir.join("test_file_for_exceptions.txt")
    another_test_file.write_text("original test text", encoding="utf-8")
    more_text = "this is more test text"
    with monkeypatch.context() as m:
        m.setattr(os, "chmod", raise_oserror_on_chmod)
        with contextmanagers.atomic_open_for_write(
            another_test_file.strpath
        ) as fh:
            fh.write(more_text)
        assert read_file(another_test_file.strpath) == more_text


class MockLink(object):
    def __init__(self, url):
        self.url = url

    @property
    def url_without_fragment(self):
        return self.url


@pytest.mark.parametrize(
    "stream, use_requests, use_link",
    [
        (True, True, True),
        (True, True, False),
        (True, False, True),
        (True, False, False),
        (False, True, True),
        (False, True, False),
        (False, False, True),
        (False, False, False),
    ],
)
def test_open_file_without_requests(monkeypatch, tmpdir, stream, use_requests, use_link):

    module_prefix = "builtins"
    bi = importlib.import_module(module_prefix)
    import_func = bi.__import__
    del bi

    def _import(name, globals=None, locals=None, fromlist=(), level=0):
        if not use_requests and name.startswith("requests"):
            raise ImportError(name)
        return import_func(name, globals, locals, fromlist, level)

    warnings.filterwarnings(
        "ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>"
    )
    if stream:
        target_file = (
            "https://www2.census.gov/geo/tiger/GENZ2017/shp/cb_2017_02_tract_500k.zip"
        )
    else:
        target_file = "https://www.fakegutenberg.org/files/1342/1342-0.txt"
    if use_link:
        target_file = MockLink(target_file)
    filecontents = io.BytesIO(b"")
    module_name = "{0}.__import__".format(module_prefix)

    @contextlib.contextmanager
    def patch_context():
        if not stream and use_requests:
            import requests

            with patch(
                "requests.Session.get", return_value=MockUrllib3Response(GUTENBERG_FILE)
            ):
                yield
        elif stream and not use_requests:

            import http

            with patch(
                "http.client.HTTPSConnection.request",
                return_value=MockUrllib3Response(GUTENBERG_FILE),
            ), patch(
                "urllib.request.urlopen",
                return_value=MockUrllib3Response(GUTENBERG_FILE),
            ):
                yield

        else:
            yield

    with monkeypatch.context() as m, patch_context():
        if not use_requests:
            m.delitem(sys.modules, "requests", raising=False)
            m.delitem(sys.modules, "requests.sessions", raising=False)
            import urllib.request

            def do_urlopen(*args, **kwargs):
                return MockUrllib3Response(GUTENBERG_FILE)
            
            m.setattr(urllib.request, "urlopen", do_urlopen)

        with patch(module_name, _import):
            with contextmanagers.open_file(target_file, stream=stream) as fp:
                if stream:
                    shutil.copyfileobj(fp, filecontents)
                else:
                    filecontents.write(fp.read())
    local_file = tmpdir.join("local_copy.txt")
    with io.open(local_file.strpath, "w", encoding="utf-8") as fp:
        fp.write(filecontents.read().decode())

    local_contents = b""
    with contextmanagers.open_file(local_file.strpath) as fp:
        for chunk in iter(lambda: fp.read(16384), b""):
            local_contents += chunk
    assert local_contents == filecontents.read()


def test_replace_stream(capsys):
    with contextmanagers.replaced_stream("stdout") as stdout:
        sys.stdout.write("hello")
        assert stdout.getvalue() == "hello"
    out, err = capsys.readouterr()
    assert out.strip() != "hello"


def test_replace_streams(capsys):
    with contextmanagers.replaced_streams() as streams:
        stdout, stderr = streams
        sys.stdout.write("hello")
        sys.stderr.write("this is an error")
        assert stdout.getvalue() == "hello"
        assert stderr.getvalue() == "this is an error"
    out, err = capsys.readouterr()
    assert out.strip() != "hello"
    assert err.strip() != "this is an error"

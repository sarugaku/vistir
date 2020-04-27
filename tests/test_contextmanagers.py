# -*- coding=utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import importlib
import io
import os
import shutil
import sys
import warnings

import pytest
import six

import vistir

from .utils import read_file

if six.PY2:
    ResourceWarning = RuntimeWarning
    from mock import patch
else:
    from unittest.mock import patch


def test_path():
    old_path = sys.path
    new_path = sys.path[2:]
    with vistir.temp_path():
        sys.path = new_path
        assert sys.path == new_path
    assert sys.path == old_path


def test_cd(tmpdir):
    second_dir = tmpdir.join("second_dir").mkdir()
    original_dir = os.path.abspath(os.curdir)
    assert original_dir != os.path.abspath(second_dir.strpath)
    with vistir.contextmanagers.cd(second_dir.strpath):
        assert os.path.abspath(os.curdir) == os.path.abspath(second_dir.strpath)
    assert os.path.abspath(os.curdir) == original_dir


def test_environ():
    os.environ["VISTIR_TEST_KEY"] = "test_value"
    assert os.environ.get("VISTIR_OTHER_KEY") is None
    with vistir.contextmanagers.temp_environ():
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
        with vistir.contextmanagers.atomic_open_for_write(filename) as fh:
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
    with vistir.contextmanagers.atomic_open_for_write(test_file.strpath) as fh:
        fh.write(replace_with_text)
    # make sure that we now have the new text in the file
    assert read_file(test_file.strpath) == replace_with_text
    another_test_file = tmpdir.join("test_file_for_exceptions.txt")
    another_test_file.write_text("original test text", encoding="utf-8")
    more_text = "this is more test text"
    with monkeypatch.context() as m:
        m.setattr(os, "chmod", raise_oserror_on_chmod)
        with pytest.raises(OSError):
            os.chmod(another_test_file.strpath, 0o644)
        with vistir.contextmanagers.atomic_open_for_write(
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
    module_prefix = "__builtins__" if six.PY2 else "builtins"
    if six.PY3:
        bi = importlib.import_module(module_prefix)
        import_func = bi.__import__
        del bi
    else:
        import_func = __builtins__["__import__"]

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
        target_file = "https://www.gutenberg.org/files/1342/1342-0.txt"
    if use_link:
        target_file = MockLink(target_file)
    filecontents = io.BytesIO(b"")
    module_name = "{0}.__import__".format(module_prefix)
    with monkeypatch.context() as m:
        if not use_requests:
            m.delitem(sys.modules, "requests", raising=False)
            m.delitem(sys.modules, "requests.sessions", raising=False)
        if six.PY3:
            with patch(module_name, _import):
                with vistir.contextmanagers.open_file(target_file, stream=stream) as fp:
                    if stream:
                        shutil.copyfileobj(fp, filecontents)
                    else:
                        filecontents.write(fp.read())
        else:
            with patch.dict("vistir.contextmanagers.__builtins__", __import__=_import):
                with vistir.contextmanagers.open_file(target_file, stream=stream) as fp:
                    if stream:
                        shutil.copyfileobj(fp, filecontents)
                    else:
                        filecontents.write(fp.read())
    local_file = tmpdir.join("local_copy.txt")
    with io.open(local_file.strpath, "w", encoding="utf-8") as fp:
        fp.write(filecontents.read().decode())

    local_contents = b""
    with vistir.contextmanagers.open_file(local_file.strpath) as fp:
        for chunk in iter(lambda: fp.read(16384), b""):
            local_contents += chunk
    assert local_contents == filecontents.read()


def test_replace_stream(capsys):
    with vistir.contextmanagers.replaced_stream("stdout") as stdout:
        sys.stdout.write("hello")
        assert stdout.getvalue() == "hello"
    out, err = capsys.readouterr()
    assert out.strip() != "hello"


def test_replace_streams(capsys):
    with vistir.contextmanagers.replaced_streams() as streams:
        stdout, stderr = streams
        sys.stdout.write("hello")
        sys.stderr.write("this is an error")
        assert stdout.getvalue() == "hello"
        assert stderr.getvalue() == "this is an error"
    out, err = capsys.readouterr()
    assert out.strip() != "hello"
    assert err.strip() != "this is an error"

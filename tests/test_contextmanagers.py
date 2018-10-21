# -*- coding=utf-8 -*-
from __future__ import absolute_import, unicode_literals

import io
import os
import shutil
import sys

import vistir

from .utils import read_file


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


def test_atomic_open(tmpdir):
    test_file = tmpdir.join("test_file.txt")
    replace_with_text = "new test text"
    test_file.write_text("some test text", encoding="utf-8")
    assert read_file(test_file.strpath) == "some test text"

    # Raise an error to make sure we don't write text on errors
    def raise_exception_while_writing(filename, new_text):
        with vistir.contextmanagers.atomic_open_for_write(filename) as fh:
            fh.write(new_text)
            raise RuntimeError("This should not overwrite the file")

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


def test_open_file(tmpdir):
    target_file = (
        "http://www2.census.gov/geo/tiger/GENZ2017/shp/cb_2017_02_tract_500k.zip"
    )
    filecontents = io.BytesIO(b"")
    with vistir.contextmanagers.open_file(target_file) as fp:
        shutil.copyfileobj(fp, filecontents)
    local_file = tmpdir.join("local_copy.txt")
    local_file.write_text(filecontents.read().decode(), encoding="utf-8")

    local_contents = b""
    with vistir.contextmanagers.open_file(local_file.strpath) as fp:
        for chunk in iter(lambda: fp.read(16384), b""):
            local_contents += chunk
    assert local_contents == filecontents.read()

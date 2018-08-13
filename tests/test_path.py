# -*- coding=utf-8 -*-
from __future__ import absolute_import, unicode_literals

import os
import shutil
import stat

from hypothesis import assume, given
from hypothesis import strategies as st
from six.moves.urllib import parse as urllib_parse

import vistir

from hypothesis_fspaths import fspaths

from .strategies import legal_path_chars, relative_paths, url_alphabet, urls
from .utils import NON_WRITE_OR_EXEC, NON_WRITEABLE, WRITEABLE, get_mode


def test_safe_expandvars():
    with vistir.contextmanagers.temp_environ():
        os.environ["TEST_VAR"] = "some_password"
        expected = "https://myuser:some_password@myfakewebsite.com"
        sanitized = "https://myuser:${TEST_VAR}@myfakewebsite.com"
        assert vistir.path.safe_expandvars(sanitized) == expected


@given(legal_path_chars(), legal_path_chars())
def test_mkdir_p(base_dir, subdir):
    assume(not any((dir_name in ["", ".", "./"] for dir_name in [base_dir, subdir])))
    assume(not subdir.endswith("/."))
    assume(os.path.abspath(base_dir) != os.path.abspath(os.path.join(base_dir, subdir)))
    with vistir.compat.TemporaryDirectory() as temp_dir:
        joined_path = os.path.join(temp_dir.name, base_dir, subdir)
        assume(os.path.abspath(joined_path) != os.path.abspath(os.path.join(temp_dir.name, base_dir)))
        vistir.path.mkdir_p(joined_path)
        assert os.path.exists(joined_path)


def test_rmtree(tmpdir):
    """This will also test `handle_remove_readonly` and `set_write_bit`."""
    new_dir = tmpdir.mkdir("test_dir")
    new_file = tmpdir.join("test_file.py")
    new_file.write_text("some test text", encoding="utf-8")
    os.chmod(new_file, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    os.chmod(new_dir, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    assert new_dir.exists()
    vistir.path.rmtree(new_dir)
    assert not new_dir.exists()


def test_is_readonly_path(tmpdir):
    new_dir = tmpdir.mkdir("some_dir")
    new_file = new_dir.join("some_file.txt")
    new_file.write_text("this is some text", encoding="utf-8")
    assert not vistir.path.is_readonly_path(new_dir.strpath)
    assert not vistir.path.is_readonly_path(new_file.strpath)
    os.chmod(new_file, get_mode(new_file.strpath) & NON_WRITEABLE)
    assert vistir.path.is_readonly_path(new_file.strpath)
    os.chmod(new_dir, get_mode(new_dir.strpath) & NON_WRITEABLE)
    assert vistir.path.is_readonly_path(new_dir.strpath)
    for pth in [new_file.strpath, new_dir.strpath]:
        os.chmod(pth, get_mode(pth) & WRITEABLE)


@given(relative_paths())
def test_get_converted_relative_path(path):
    path = "".join(path)
    relpath = vistir.path.get_converted_relative_path(path)
    assert relpath.startswith(".")
    assert os.path.abspath(relpath) == os.path.abspath(vistir.path._encode_path(path))


@given(urls())
def test_is_valid_url(url):
    unparsed_url = urllib_parse.urlunparse(url)
    assume(not unparsed_url.startswith("file://"))
    assert vistir.path.is_valid_url(unparsed_url)


@given(fspaths())
def test_path_to_url(filepath):
    filename = str(filepath)
    assume(any(letter in filename for letter in url_alphabet))
    file_url = vistir.path.path_to_url(filename)
    assume(file_url != filename)
    assert file_url.startswith("file:")
    assert vistir.path.is_file_url(file_url)

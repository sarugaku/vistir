# -*- coding=utf-8 -*-
from __future__ import absolute_import, unicode_literals

import os
import six
import stat

from hypothesis import assume, given, example
from six.moves.urllib import parse as urllib_parse

import vistir

from hypothesis_fspaths import fspaths

from .strategies import legal_path_chars, relative_paths, url_alphabet, urls
from .utils import NON_WRITE_OR_EXEC, NON_WRITEABLE, WRITEABLE, get_mode


def test_abspathu(tmpdir):
    tmpdir.mkdir("new_dir")
    new_dir = tmpdir.join("new_dir")
    with vistir.contextmanagers.cd(tmpdir.strpath):
        assert vistir.path.abspathu(new_dir.purebasename) == vistir.misc.to_text(new_dir.strpath)


def test_safe_expandvars():
    with vistir.contextmanagers.temp_environ():
        os.environ["TEST_VAR"] = "some_password"
        expected = "https://myuser:some_password@myfakewebsite.com"
        sanitized = "https://myuser:${TEST_VAR}@myfakewebsite.com"
        assert vistir.path.safe_expandvars(sanitized) == expected


@given(legal_path_chars(), legal_path_chars())
def test_mkdir_p(base_dir, subdir):
    assume(not any((dir_name in ["", ".", "./", ".."] for dir_name in [base_dir, subdir])))
    assume(not (os.path.relpath(subdir, start=base_dir) == "."))
    assume(not any(base_dir.endswith(illegal_character) for illegal_character in [".", "/", "./", "/."]))
    assume(not subdir.endswith("/."))
    assume(os.path.abspath(base_dir) != os.path.abspath(os.path.join(base_dir, subdir)))
    with vistir.compat.TemporaryDirectory() as temp_dir:
        target = os.path.join(temp_dir.name, base_dir, subdir)
        assume(vistir.path.abspathu(target) != vistir.path.abspathu(os.path.join(temp_dir.name, base_dir)))
        if six.PY2:
            target = vistir.misc.to_bytes(target, encoding="utf-8")
        vistir.path.mkdir_p(target)
        assert os.path.exists(target)


def test_rmtree(tmpdir):
    """This will also test `handle_remove_readonly` and `set_write_bit`."""
    new_dir = tmpdir.join("test_dir").mkdir()
    new_file = new_dir.join("test_file.py")
    new_file.write_text(u"some test text", encoding="utf-8")
    os.chmod(new_file.strpath, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    assert new_dir.exists()
    vistir.path.rmtree(new_dir.strpath)
    assert not new_dir.exists()


def test_is_readonly_path(tmpdir):
    new_dir = tmpdir.join("some_dir").mkdir()
    new_file = new_dir.join("some_file.txt")
    new_file.write_text(u"this is some text", encoding="utf-8")
    assert not vistir.path.is_readonly_path(new_dir.strpath)
    assert not vistir.path.is_readonly_path(new_file.strpath)
    os.chmod(new_file.strpath, get_mode(new_file.strpath) & NON_WRITEABLE)
    assert vistir.path.is_readonly_path(new_file.strpath)
    for pth in [new_file.strpath, new_dir.strpath]:
        os.chmod(pth, get_mode(pth) & WRITEABLE)


@given(relative_paths())
def test_get_converted_relative_path(path):
    assume(not vistir.path.abspathu("".join(path)) == vistir.path.abspathu(os.curdir))
    path = "".join(path)
    relpath = vistir.path.get_converted_relative_path(path)
    assert relpath.startswith(u".")
    assert vistir.path.abspathu(relpath) == os.path.abspath(vistir.misc.to_text(path))


@given(urls())
def test_is_valid_url(url):
    unparsed_url = urllib_parse.urlunparse(url)
    assume(not unparsed_url.startswith("file://"))
    assert vistir.path.is_valid_url(unparsed_url)


@given(fspaths())
def test_path_to_url(filepath):
    filename = vistir.misc.to_text(filepath)
    if filepath and filename:
        assume(any(letter in filename for letter in url_alphabet))
    file_url = vistir.path.path_to_url(filename)
    if filename:
        assume(file_url != filename)
        assert file_url.startswith("file:")
        assert vistir.path.is_file_url(file_url)
    else:
        assert file_url == filename
        assert not file_url


@given(fspaths())
def test_normalize_drive(filepath):
    filename = vistir.misc.to_text(filepath)
    if filepath and filename:
        assume(any(letter in filename for letter in url_alphabet))
    if os.name == 'nt':
        upper_drive = "C:"
        lower_drive = upper_drive.lower()
        lower_path = os.path.join(lower_drive, filename)
        upper_path = os.path.join(upper_drive, filename)
        assert vistir.path.normalize_drive(lower_path) == upper_path
        assert vistir.path.normalize_drive(upper_path) == upper_path
    assert vistir.path.normalize_drive(filename) == filename


def test_walk_up(tmpdir):
    tmpdir.join("test.txt").write_text("some random text", encoding="utf-8")
    one_down = tmpdir.join("one_down").mkdir()
    one_down.join("test.txt").write_text("some random text", encoding="utf-8")
    one_down.join("test1.txt").write_text("some random text 2", encoding="utf-8")
    one_down.join("test2.txt").write_text("some random text 3", encoding="utf-8")
    two_down = one_down.join("two_down").mkdir()
    two_down.join("test2.txt").write_text("some random text", encoding="utf-8")
    two_down.join("test2_1.txt").write_text("some random text 2", encoding="utf-8")
    two_down.join("test2_2.txt").write_text("some random text 3", encoding="utf-8")
    expected = (
        (os.path.abspath(two_down.strpath), [], sorted(["test2.txt", "test2_1.txt", "test2_2.txt"])),
        (os.path.abspath(one_down.strpath), sorted([two_down.purebasename,]), sorted(["test.txt", "test1.txt", "test2.txt"])),
        (os.path.abspath(tmpdir.strpath), sorted([one_down.purebasename,]), sorted(["test.txt",])),
    )
    walk_up = vistir.path.walk_up(two_down.strpath)
    for i in range(3):
        results = next(walk_up)
        results = (results[0], sorted(results[1]), sorted(results[2]))
        assert results == expected[i]


def test_handle_remove_readonly(tmpdir):
    test_file = tmpdir.join("test_file.txt")
    test_file.write_text("a bunch of text", encoding="utf-8")
    os.chmod(test_file.strpath, NON_WRITE_OR_EXEC)
    fake_oserror = OSError("Fake os error")
    fake_oserror.errno = 13  # EACCES error
    vistir.path.handle_remove_readonly(os.unlink, test_file.strpath, (OSError, fake_oserror, "Fake Traceback"))
    assert not os.path.exists(test_file.strpath)

# -*- coding=utf-8 -*-
from __future__ import absolute_import, unicode_literals

import io
import os
import shutil
import stat

import pytest
import six
from hypothesis import HealthCheck, assume, example, given, settings
from hypothesis_fspaths import _PathLike, fspaths
from six.moves.urllib import parse as urllib_parse

import vistir

from .strategies import legal_path_chars, paths, relative_paths, url_alphabet, urls
from .utils import EXEC, NON_WRITE_OR_EXEC, NON_WRITEABLE, WRITEABLE, get_mode


def get_ord(char):
    if isinstance(char, int):
        return char
    return ord(char)


def test_abspathu(tmpdir):
    tmpdir.mkdir("new_dir")
    new_dir = tmpdir.join("new_dir")
    with vistir.contextmanagers.cd(tmpdir.strpath):
        assert vistir.path.abspathu(new_dir.purebasename) == vistir.misc.to_text(
            new_dir.strpath
        )


def test_normalize_path():
    with vistir.contextmanagers.temp_environ():
        os.environ["PATH_VAR"] = "some_path"
        try:
            assert os.environ.get("HOME")
        except AssertionError:
            os.environ["HOME"] = os.getcwd()
        orig_path = os.path.normcase(
            str(vistir.compat.Path("~").expanduser() / "some_path" / "other_path")
        )
        assert vistir.path.normalize_path("~/${PATH_VAR}/other_path") == orig_path


@pytest.mark.parametrize(
    "path, root, result",
    [
        ("~/some/path/child", "~/some/path", True),
        ("~/some", "~/some/path", False),
        ("~/some/path/child", "~", True),
    ],
)
def test_is_in_path(path, root, result):
    assert vistir.path.is_in_path(path, root) == result


def test_safe_expandvars():
    with vistir.contextmanagers.temp_environ():
        os.environ["TEST_VAR"] = "some_password"
        expected = "https://myuser:some_password@myfakewebsite.com"
        sanitized = "https://myuser:${TEST_VAR}@myfakewebsite.com"
        assert vistir.path.safe_expandvars(sanitized) == expected


@given(paths(), paths())
@example(base_dir="0", subdir="\x80")
@settings(suppress_health_check=(HealthCheck.filter_too_much,), deadline=None)
def test_mkdir_p(base_dir, subdir):
    # base_dir_path = base_dir._value if isinstance(base_dir, _PathLike) else base_dir
    # subdir_path = subdir._value if isinstance(subdir, _PathLike) else subdir
    base_dir_path = base_dir
    subdir_path = subdir
    assume(base_dir_path.strip() and subdir_path.strip())
    # if not isinstance(base_dir_path, type(subdir_path)):
    #     base_dir_path = vistir.compat.fs_decode(base_dir_path)
    #     subdir_path = vistir.compat.fs_decode(subdir_path)
    assume(
        not any(
            (
                dir_name in ["", ".", "./", ".."]
                for dir_name in [base_dir_path, subdir_path]
            )
        )
    )
    assume(not (os.path.relpath(subdir_path, start=base_dir_path) == "."))
    assume(
        os.path.abspath(base_dir_path)
        != os.path.abspath(os.path.join(base_dir_path, subdir_path))
    )
    total_len = len(
        vistir.compat.fs_encode(os.path.join(os.path.abspath(base_dir_path), subdir_path))
    )
    assume(total_len <= 255)
    with vistir.compat.TemporaryDirectory() as temp_dir:
        temp_dirname = (
            temp_dir.name
            if isinstance(base_dir_path, six.text_type)
            else vistir.compat.fs_encode(temp_dir.name)
        )
        target = os.path.join(temp_dirname, base_dir_path, subdir_path)
        assume(
            vistir.path.abspathu(target)
            != vistir.path.abspathu(os.path.join(temp_dirname, base_dir_path))
        )
        vistir.path.mkdir_p(target)
        assert os.path.exists(target)


@given(paths(), paths())
@example(base_dir="0", subdir="\x80")
@settings(suppress_health_check=(HealthCheck.filter_too_much,), deadline=None)
def test_ensure_mkdir_p(base_dir, subdir):
    # base_dir_path = base_dir._value if isinstance(base_dir, _PathLike) else base_dir
    # subdir_path = subdir._value if isinstance(subdir, _PathLike) else subdir
    # assume(base_dir_path.strip() and subdir_path.strip())
    base_dir_path = base_dir
    subdir_path = subdir
    # if not isinstance(base_dir, type(subdir_path)):
    #     base_dir_path = vistir.compat.fs_decode(base_dir_path)
    #     subdir_path = vistir.compat.fs_decode(subdir_path)
    assume(
        not any(
            (
                dir_name in ["", ".", "./", ".."]
                for dir_name in [base_dir_path, subdir_path]
            )
        )
    )
    assume(not (os.path.relpath(subdir_path, start=base_dir_path) == "."))
    assume(
        os.path.abspath(base_dir_path)
        != os.path.abspath(os.path.join(base_dir_path, subdir_path))
    )
    total_len = len(
        vistir.compat.fs_encode(os.path.join(os.path.abspath(base_dir_path), subdir_path))
    )
    assume(total_len <= 255)
    with vistir.compat.TemporaryDirectory() as temp_dir:
        temp_dirname = (
            temp_dir.name
            if isinstance(temp_dir.name, type(base_dir_path))
            else vistir.compat.fs_encode(temp_dir.name)
        )

        @vistir.path.ensure_mkdir_p(mode=0o777)
        def join_with_dir(_base_dir, _subdir, base=temp_dirname):
            return os.path.join(base, _base_dir, _subdir)

        target = join_with_dir(base_dir_path, subdir_path, base=temp_dirname)
        assume(
            vistir.path.abspathu(target)
            != vistir.path.abspathu(os.path.join(temp_dirname, base_dir_path))
        )
        assert os.path.exists(target)


@pytest.mark.xfail(raises=OSError)
def test_mkdir_p_fails_when_path_exists(tmpdir):
    myfile = tmpdir.join("myfile")
    myfile.write_text("some text", encoding="utf-8")
    vistir.path.mkdir_p(myfile.strpath)


def test_create_tracked_tempdir(tmpdir):
    subdir = tmpdir.join("subdir")
    subdir.mkdir()
    temp_dir = vistir.path.create_tracked_tempdir(prefix="test_dir", dir=subdir.strpath)
    assert os.path.basename(temp_dir).startswith("test_dir")
    with io.open(os.path.join(temp_dir, "test_file.txt"), "w") as fh:
        fh.write("this is a test")
    assert len(os.listdir(temp_dir)) > 0


def test_create_tracked_tempfile(tmpdir):
    tmpfile = vistir.path.create_tracked_tempfile(
        prefix="test_file", dir=tmpdir.strpath, delete=False
    )
    tmpfile.write(b"this is some text")
    tmpfile.close()
    assert os.path.basename(tmpfile.name).startswith("test_file")
    assert os.path.exists(tmpfile.name)
    with io.open(tmpfile.name, "r") as fh:
        contents = fh.read().strip()
    assert contents == "this is some text"


def test_rmtree(tmpdir):
    """This will also test `handle_remove_readonly` and `set_write_bit`."""
    new_dir = tmpdir.join("test_dir").mkdir()
    new_file = new_dir.join("test_file.py")
    new_file.write_text("some test text", encoding="utf-8")
    os.chmod(new_file.strpath, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    assert new_dir.exists()
    vistir.path.rmtree(new_dir.strpath)
    assert not new_dir.exists()


def test_is_readonly_path(tmpdir):
    new_dir = tmpdir.join("some_dir").mkdir()
    new_file = new_dir.join("some_file.txt")
    new_file.write_text("this is some text", encoding="utf-8")
    assert not vistir.path.is_readonly_path(new_dir.strpath)
    assert not vistir.path.is_readonly_path(new_file.strpath)
    os.chmod(new_file.strpath, get_mode(new_file.strpath) & NON_WRITEABLE)
    assert vistir.path.is_readonly_path(new_file.strpath)
    assert vistir.path.is_readonly_path("fake_path") is False
    WRITE_EXEC = WRITEABLE | EXEC
    os.chmod(new_dir.strpath, WRITE_EXEC)
    os.chmod(new_file.strpath, WRITEABLE)
    shutil.rmtree(new_dir.strpath)


@given(relative_paths())
def test_get_converted_relative_path(path):
    assume(not vistir.path.abspathu("".join(path)) == vistir.path.abspathu(os.curdir))
    path = "".join(path)
    relpath = vistir.path.get_converted_relative_path(path)
    assert relpath.startswith(".")
    assert vistir.path.abspathu(relpath) == os.path.abspath(vistir.misc.to_text(path))


@given(urls())
def test_is_valid_url(url):
    unparsed_url = urllib_parse.urlunparse(url)
    assume(not unparsed_url.startswith("file://"))
    assert vistir.path.is_valid_url(unparsed_url)


def test_none_as_valid_url_returns_none():
    assert vistir.path.is_valid_url(None) is None


def test_is_file_url_returns_none_when_passed_none():
    assert vistir.path.is_file_url(None) is False


@pytest.mark.xfail(raises=ValueError)
def test_is_file_url_raises_valueerror_when_no_url_attribute_found():
    class FakeLink(object):
        def __init__(self, url_path):
            self.url_path = url_path

    assert not vistir.path.is_file_url(FakeLink(vistir.path.path_to_url("some/link")))


@given(fspaths())
@example("0\ud800")
@settings(suppress_health_check=(HealthCheck.filter_too_much,))
def test_path_to_url(filepath):
    class FakeLink(object):
        def __init__(self, url=None):
            self.url = url

    filename = vistir.compat.fs_decode(filepath)
    if filepath and filename:
        assume(any(letter in filename for letter in url_alphabet))
    file_url = vistir.path.path_to_url(filename)
    if filename:
        assume(file_url != filename)
        assert file_url.startswith("file:")
        assert vistir.path.is_file_url(file_url) is True
        assert vistir.path.is_file_url(FakeLink(url=file_url)) is True
    else:
        assert file_url == filename
        assert not file_url


@given(fspaths())
@settings(suppress_health_check=(HealthCheck.filter_too_much,))
def test_normalize_drive(filepath):
    filename = vistir.misc.to_text(filepath)
    if filepath and filename:
        assume(any(letter in filename for letter in url_alphabet))
    if os.name == "nt":
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
        (
            os.path.abspath(two_down.strpath),
            [],
            sorted(["test2.txt", "test2_1.txt", "test2_2.txt"]),
        ),
        (
            os.path.abspath(one_down.strpath),
            sorted([two_down.purebasename]),
            sorted(["test.txt", "test1.txt", "test2.txt"]),
        ),
        (
            os.path.abspath(tmpdir.strpath),
            sorted([one_down.purebasename]),
            sorted(["test.txt"]),
        ),
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
    fake_oserror = OSError(13, "Permission denied")
    fake_oserror.filename = test_file.strpath
    vistir.path.handle_remove_readonly(
        os.unlink,
        test_file.strpath,
        (fake_oserror.__class__, fake_oserror, "Fake traceback"),
    )
    assert not os.path.exists(test_file.strpath)

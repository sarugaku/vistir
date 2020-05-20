# -*- coding=utf-8 -*-
from __future__ import absolute_import, print_function

import io
import itertools
import os
import sys

import pytest
import six
from hypothesis import assume, given, strategies as st

import vistir

from .strategies import legal_path_chars


def test_get_logger():
    from logging import Logger

    logger = vistir.misc._get_logger(name="vistir_logger", level="DEBUG")
    assert isinstance(logger, Logger)


def test_shell_escape():
    printfoo = u"python -c \"print('foo')\""
    assert vistir.misc.shell_escape(printfoo) == u"python -c print('foo')"
    appendscript = u"cmd arg1"
    assert vistir.misc.shell_escape(appendscript) == u"cmd arg1"
    multicommand = u'bash -c "cd docs && make html"'
    assert vistir.misc.shell_escape(multicommand) == u'bash -c "cd docs && make html"'
    escaped_python = u'"{}" -c \'print("hello")\''.format(sys.executable)
    if os.name == "nt" and " " in sys.executable:
        expected = u'"{}" -c print("hello")'.format(sys.executable)
    else:
        expected = u'{} -c print("hello")'.format(sys.executable)
    assert vistir.misc.shell_escape(escaped_python) == expected


@given(
    st.lists(st.integers(min_value=1), min_size=1),
    st.lists(
        st.lists(st.integers(min_value=1, max_value=9999999999), min_size=1),
        min_size=1,
        max_size=5,
    ),
)
def test_unnest(seed_ints, additional_lists):
    assume(len(additional_lists) > 0 and len(seed_ints) > 0)
    composite_list = seed_ints[:]
    flattened_list = seed_ints[:]
    flattened_list.extend(list(itertools.chain.from_iterable(additional_lists)))
    list_copies = additional_lists[:]
    for i in reversed(range(len(additional_lists))):
        if len(additional_lists[i]) > 0:
            if not isinstance(additional_lists[i], int):
                if i > 0:
                    list_copies[i - 1].append(additional_lists[i])
                else:
                    composite_list.append(list_copies[i])
    assert all(
        (isinstance(x, six.integer_types) or x.isdigit()) for x in flattened_list
    ), flattened_list
    assert sorted(list(vistir.misc.unnest(composite_list))) == sorted(flattened_list)


@pytest.mark.parametrize(
    "iterable, result",
    [
        [[u"abc", u"def"], True],
        [(u"abc", u"def"), True],
        [u"abcdef", True],
        [None, False],
        [1234, False],
    ],
)
def test_is_iterable(iterable, result):
    assert vistir.misc._is_iterable(iterable) is result


def test_unnest_none():
    assert list(vistir.misc.unnest(None)) == [None]


def test_dedup():
    dup_strings = [u"abcde", u"fghij", u"klmno", u"pqrst", u"abcde", u"klmno"]
    assert list(vistir.misc.dedup(dup_strings)) == [
        u"abcde",
        u"fghij",
        u"klmno",
        u"pqrst",
    ]
    dup_ints = (12345, 56789, 12345, 54321, 98765, 54321)
    assert list(vistir.misc.dedup(dup_ints)) == [12345, 56789, 54321, 98765]


def test_get_stream_results():
    class MockCmd(object):
        def __init__(self, stdout, stderr):
            self.stdout = stdout
            self.stderr = stderr

        def poll(self):
            return 0

        def wait(self):
            return 0

    stdout_buffer = six.StringIO()
    stderr_buffer = six.StringIO()
    test_line = (
        u"this is a test line that goes on for many characters and will eventually be "
        "truncated because it is far too long to display on a normal terminal so we will"
        " use an ellipsis to break it\n"
    )
    stdout_buffer.write(test_line)
    stdout_buffer.seek(0)
    cmd_instance = MockCmd(stdout=stdout_buffer, stderr=stderr_buffer)
    instance = vistir.misc.attach_stream_reader(
        cmd_instance, False, 50, spinner=None, stdout_allowed=False
    )
    assert instance.text_stdout_lines == [test_line.strip()], "\n".join(
        ["{}: {}".format(k, v) for k, v in instance.__dict__.items()]
    )


def test_run():
    out, err = vistir.misc.run(
        [r"{}".format(sys.executable), "-c", "print('hello')"], nospin=True
    )
    assert out == "hello"
    out, err = vistir.misc.run(
        [sys.executable, "-c", "import ajwfoiejaoiwj"], nospin=True
    )
    assert any(
        error_text in err for error_text in ["ImportError", "ModuleNotFoundError"]
    ), "{} => {}".format(out, err)


def test_run_return_subprocess():
    c = vistir.misc.run(
        [r"{}".format(sys.executable), "-c", "print('test')"],
        return_object=True,
        nospin=True,
    )
    assert c.returncode == 0
    assert c.out.strip() == "test"


@pytest.mark.flaky(reruns=5)
def test_run_failing_subprocess(capsys):
    c = vistir.misc.run(
        ["fakecommandthatdoesntexist", "fake", "argument"],
        nospin=True,
        return_object=True,
        block=False,
    )
    out, err = capsys.readouterr()
    assert "FAIL" in out


@pytest.mark.flaky(reruns=5)
def test_run_with_long_output():
    long_str = "this is a very long string which exceeds the maximum length per the settings we are passing in to vistir"
    print_cmd = "import time; print('{}'); time.sleep(2)".format(long_str)
    run_args = [r"{}".format(sys.executable), "-c", print_cmd]
    c = vistir.misc.run(
        run_args, block=False, display_limit=100, nospin=True, return_object=True
    )
    c.wait()
    assert c.out == long_str
    c = vistir.misc.run(
        run_args,
        block=False,
        display_limit=100,
        nospin=True,
        verbose=True,
        return_object=True,
    )
    c.wait()
    assert c.out == long_str

    c = vistir.misc.run(
        run_args,
        block=False,
        write_to_stdout=False,
        nospin=True,
        verbose=True,
        return_object=True,
    )
    c.wait()
    assert c.out == long_str


@pytest.mark.flaky(reruns=5)
def test_nonblocking_run():
    c = vistir.misc.run(
        [r"{}".format(sys.executable), "--help"],
        block=False,
        return_object=True,
        nospin=True,
    )
    assert c.returncode == 0
    c.wait()
    assert "PYTHONDONTWRITEBYTECODE" in c.out, c.out
    out, _ = vistir.misc.run(
        [r"{}".format(sys.executable), "--help"], block=False, nospin=True
    )
    assert "PYTHONDONTWRITEBYTECODE" in out, out


def test_load_path():
    loaded_path = vistir.misc.load_path(sys.executable)
    assert any(sys.exec_prefix in loaded_sys_path for loaded_sys_path in loaded_path)


def test_partialclass():
    text_io_wrapper = vistir.misc.partialclass(io.TextIOWrapper)
    instantiated_wrapper = text_io_wrapper(io.BytesIO(b"hello"))
    assert instantiated_wrapper.read() == "hello"


DIVIDE_ITERABLE = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


@pytest.mark.parametrize(
    "n, iterable, expected",
    [
        (1, DIVIDE_ITERABLE, [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]),
        (2, DIVIDE_ITERABLE, [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]]),
        (3, DIVIDE_ITERABLE, [[1, 2, 3, 4], [5, 6, 7], [8, 9, 10]]),
        (10, DIVIDE_ITERABLE, [[n] for n in range(1, 10 + 1)]),
        (6, [1, 2, 3, 4], [[1], [2], [3], [4], [], []]),
    ],
)
def test_divide(n, iterable, expected):
    assert [list(x) for x in vistir.misc.divide(n, iterable)] == expected


@pytest.mark.parametrize(
    "as_text, as_bytes, encoding",
    (
        [u"mystring", b"mystring", "utf-8"],
        [u"mystring", b"mystring", "latin1"],
        [u"mystring", memoryview(b"mystring"), "utf-8"],
    ),
)
def test_to_bytes(as_text, as_bytes, encoding):
    assert vistir.misc.to_bytes(as_text, encoding) == vistir.misc.to_bytes(
        as_bytes, encoding
    )


@given(legal_path_chars())
def test_decode_encode(path):
    assert vistir.misc.to_text(vistir.misc.to_bytes(path)) == u"{}".format(path)


@pytest.mark.parametrize(
    "test_str", [u"this is a test unicode string", u"unicode\u0141", u"latin\xe9"]
)
def test_wrapped_stream(test_str):
    stream = io.BytesIO()
    if sys.version_info[0] > 2:
        if sys.version_info < (3, 5):
            err_text = r".*does not support the buffer interface.*"
        else:
            err_text = r"a bytes-like object is required, not*"
    else:
        err_text = r".*does not have the buffer interface.*"
    with pytest.raises(TypeError, match=u"{}".format(err_text)):
        stream.write(test_str)
    wrapped_stream = vistir.misc.get_wrapped_stream(
        stream, encoding="utf-8", errors="surrogateescape"
    )
    wrapped_stream.write(test_str)
    wrapped_stream.seek(0)
    assert wrapped_stream.read() == test_str


def test_stream_wrapper(capsys):
    new_stream = vistir.misc.get_text_stream("stdout")
    sys.stdout = new_stream
    print(u"this is a new method\u0141asdf", file=sys.stdout)
    out, err = capsys.readouterr()
    assert out.strip() == u"this is a new method\u0141asdf"


def test_colorized_stream(capsys):
    new_stream = vistir.misc.get_text_stream("stdout")
    sys.stdout = new_stream
    green_string = u"\x1b[32m\x1b[22mhello\x1b[39m\x1b[22m"
    print(green_string, file=sys.stdout)
    out, _ = capsys.readouterr()
    assert r"\x1b[32m" not in out
    assert u"hello" in out
    vistir.misc.echo(u"hello", fg="green")
    out, _ = capsys.readouterr()
    assert r"\x1b[32m" not in out
    assert u"hello" in out


def test_strip_colors(capsys, monkeypatch):
    with monkeypatch.context() as m:
        m.setattr("vistir.termcolors.DISABLE_COLORS", True)
        sys.stdout = vistir.misc.get_text_stream("stdout")
        sys.stdin = vistir.misc.get_text_stream("stdin")
        vistir.misc.echo(u"hello", fg="green")
        out, _ = capsys.readouterr()
        assert "\x1b[32m" not in out
        assert u"hello" in out
        green_string = u"\x1b[32m\x1b[22mhello\x1b[39m\x1b[22m"
        vistir.misc.echo(green_string)
        out, _ = capsys.readouterr()
        assert u"hello" in out
        assert u"\x1b[32m" not in out


@pytest.mark.skipif(sys.version_info[0] < 3, reason="Python 2 uses bytes by default")
def test_write_bytes(capsys):
    sys.stdout = vistir.misc.get_text_stream("stdout")
    sys.stdin = vistir.misc.get_text_stream("stdin")
    vistir.misc.echo(vistir.misc.to_bytes("hello"), fg="green")
    out, _ = capsys.readouterr()
    assert u"\x1b[32m" not in out
    assert u"hello" in out
    green_string = vistir.misc.to_bytes(u"\x1b[32m\x1b[22mhello\x1b[39m\x1b[22m")
    vistir.misc.echo(green_string)
    out, _ = capsys.readouterr()
    assert u"hello" in out
    assert u"\x1b[32m" in out
    # now add color=True to make sure this works right
    green_string = vistir.misc.to_bytes(u"\x1b[32m\x1b[22mhello\x1b[39m\x1b[22m")
    vistir.misc.echo(green_string, color=True)
    out, _ = capsys.readouterr()
    assert u"hello" in out
    assert u"\x1b[32m" in out

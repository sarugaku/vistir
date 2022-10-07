# -*- coding=utf-8 -*-

import io
import itertools
import locale
import os
import sys

import pytest
from hypothesis import assume, given, strategies as st

import vistir

from .strategies import legal_path_chars


def test_get_logger():
    from logging import Logger

    logger = vistir.misc._get_logger(name="vistir_logger", level="DEBUG")
    assert isinstance(logger, Logger)


def test_shell_escape():
    printfoo = "python -c \"print('foo')\""
    assert vistir.misc.shell_escape(printfoo) == "python -c print('foo')"
    appendscript = "cmd arg1"
    assert vistir.misc.shell_escape(appendscript) == "cmd arg1"
    multicommand = u'bash -c "cd docs && make html"'
    assert vistir.misc.shell_escape(multicommand) == 'bash -c "cd docs && make html"'
    escaped_python = '"{}" -c \'print("hello")\''.format(sys.executable)
    if os.name == "nt" and " " in sys.executable:
        expected = '"{}" -c print("hello")'.format(sys.executable)
    else:
        expected = '{} -c print("hello")'.format(sys.executable)
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
        (isinstance(x, int) or x.isdigit()) for x in flattened_list
    ), flattened_list
    assert sorted(list(vistir.misc.unnest(composite_list))) == sorted(flattened_list)


@pytest.mark.parametrize(
    "iterable, result",
    [
        [["abc", "def"], True],
        [("abc", "def"), True],
        ["abcdef", True],
        [None, False],
        [1234, False],
    ],
)
def test_is_iterable(iterable, result):
    assert vistir.misc._is_iterable(iterable) is result


def test_unnest_none():
    assert list(vistir.misc.unnest(None)) == [None]


def test_dedup():
    dup_strings = ["abcde", "fghij", "klmno", "pqrst", "abcde", "klmno"]
    assert list(vistir.misc.dedup(dup_strings)) == [
        "abcde",
        "fghij",
        "klmno",
        "pqrst",
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

    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
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
        encoding=locale.getpreferredencoding(),
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


def test_stream_wrapper(capsys):
    new_stream = vistir.misc.get_text_stream("stdout")
    sys.stdout = new_stream
    print("this is a new method\u0141asdf", file=sys.stdout)
    out, err = capsys.readouterr()
    assert out.strip() == "this is a new method\u0141asdf"

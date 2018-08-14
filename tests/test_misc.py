# -*- coding=utf-8 -*-
from __future__ import absolute_import, unicode_literals

import io
import os
import six
import sys
import itertools

from hypothesis import given, assume
from hypothesis import strategies as st

import vistir


def test_shell_escape():
    printfoo = "python -c \"print('foo')\""
    assert vistir.misc.shell_escape(printfoo) == "python -c print('foo')"
    appendscript = "cmd arg1"
    assert vistir.misc.shell_escape(appendscript) == "cmd arg1"
    multicommand = "bash -c \"cd docs && make html\""
    assert vistir.misc.shell_escape(multicommand) == 'bash -c "cd docs && make html"'
    escaped_python = "\"{0}\" -c 'print(\"hello\")'".format(sys.executable)
    if os.name == 'nt' and " " in sys.executable:
        expected = '"{0}" -c print("hello")'.format(sys.executable)
    else:
        expected = '{0} -c print("hello")'.format(sys.executable)
    assert vistir.misc.shell_escape(escaped_python) == expected


@given(
    st.lists(st.integers(min_value=1), min_size=1),
    st.lists(st.lists(st.integers(min_value=1, max_value=9999999999), min_size=1), min_size=1, max_size=5),
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
    assert all((isinstance(x, six.integer_types) or x.isdigit()) for x in flattened_list), flattened_list
    assert sorted(list(vistir.misc.unnest(composite_list))) == sorted(flattened_list)


def test_dedup():
    dup_strings = ["abcde", "fghij", "klmno", "pqrst", "abcde", "klmno"]
    assert list(vistir.misc.dedup(dup_strings)) == ["abcde", "fghij", "klmno", "pqrst"]
    dup_ints = (12345, 56789, 12345, 54321, 98765, 54321)
    assert list(vistir.misc.dedup(dup_ints)) == [12345, 56789, 54321, 98765]


def test_run():
    out, err = vistir.misc.run(["python", "-c", "print('hello')"])
    assert out == "hello"
    out, err = vistir.misc.run(["python", "-c", "import ajwfoiejaoiwj"])
    assert any(error_text in err for error_text in ["ImportError", "ModuleNotFoundError"])


def test_load_path():
    loaded_path = vistir.misc.load_path(sys.executable)
    assert any(sys.exec_prefix in loaded_sys_path for loaded_sys_path in loaded_path)


def test_partialclass():
    text_io_wrapper = vistir.misc.partialclass(io.TextIOWrapper)
    instantiated_wrapper = text_io_wrapper(io.BytesIO(b"hello"))
    assert instantiated_wrapper.read() == "hello"

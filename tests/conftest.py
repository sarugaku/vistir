# -*- coding=utf-8 -*-
import pytest
from vistir.contextmanagers import replaced_stream


@pytest.fixture(scope="function")
def capture_streams():
    with replaced_stream("stdout") as stdout:
        with replaced_stream("stderr") as stderr:
            yield (stdout, stderr)

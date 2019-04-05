# -*- coding: utf-8 -*-

from hypothesis import assume, example, given, strategies as st

import vistir

from .strategies import legal_path_chars


# This fails in the normal backports library:
# see https://github.com/PiDelport/backports.os/issues/13
@given(legal_path_chars())
@example(path=u"unicode\u0141")
def test_decode_encode(path):
    assert vistir.compat.fs_decode(vistir.compat.fs_encode(path)) == path

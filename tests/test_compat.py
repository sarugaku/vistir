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


def test_samefile(tmpdir):
    tmp_file = tmpdir.join("testfile.txt")
    tmp_file.write_text(u"asdf", encoding="utf-8")
    assert vistir.compat.samefile(str(tmp_file), tmp_file.strpath) is True

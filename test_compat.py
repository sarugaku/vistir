# -*- coding: utf-8 -*-

from vistir.compat import fs_decode, fs_encode


def test_fs_encode():
    # This fails in the normal backports library:
    # see https://github.com/PiDelport/backports.os/issues/13
    assert fs_decode(fs_encode(u"unicode\u0141")) == u"unicode\u0141"

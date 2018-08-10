# -*- coding=utf-8 -*-
from hypothesis import assume, given
from hypothesis import strategies as st
from hypothesis_fspaths import fspaths
import os
import vistir

# "handle_remove_readonly",
# "is_readonly_path",
# "mkdir_p",
# "rmtree",
# "safe_expandvars",
# "set_write_bit",
# "walk_up",

uri_schemes = ("http", "https", "ssh", "file", "sftp", "ftp")
url_alphabet = "abcdefghijklmnopqrstuvwxyz1234567890-"


@given(fspaths(allow_pathlike=False))
def test_get_converted_relative_path(filepath):
    filename = str(filepath)
    assume(any(letter in filename for letter in url_alphabet))
    relpath = vistir.path.get_converted_relative_path(filename, relative_to=os.path.dirname(filename))
    assert relpath.startswith('./')
    # assert os.path.abspath(str(filepath)) == str(relpath)


@given(st.sampled_from(uri_schemes), st.text(alphabet=url_alphabet, min_size=6, max_size=15), st.sampled_from(['com', 'com.au', '']))
def test_is_valid_url(scheme, host, tld):
    url = "{0}://{1}".format(scheme, host)
    assume((tld == '') == (scheme == 'file'))
    if tld:
        url = "{0}.{1}".format(url, tld)
    assert vistir.path.is_valid_url(url)


@given(fspaths())
def test_path_to_url(filepath):
    filename = str(filepath)
    assume(any(letter in filename for letter in url_alphabet))
    file_url = vistir.path.path_to_url(filename)
    assume(file_url != filename)
    assert file_url.startswith('file:')
    assert vistir.path.is_file_url(file_url)

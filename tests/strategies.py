# -*- coding=utf-8 -*-
from __future__ import absolute_import, unicode_literals

import codecs
import os

from collections import namedtuple

from hypothesis import strategies as st
from six.moves.urllib import parse as urllib_parse
import six


parsed_url = namedtuple("ParsedUrl", "scheme netloc path params query fragment")
parsed_url.__new__.__defaults__ = ("", "", "", "", "", "")
relative_path = namedtuple("RelativePath", "leading_dots separator dest")
relative_path.__new__.__defaults__ = ("", "", "")
url_alphabet = "abcdefghijklmnopqrstuvwxyz1234567890-"
uri_schemes = ("http", "https", "ssh", "file", "sftp", "ftp")
vcs_schemes = (
    "git",
    "git+http",
    "git+https",
    "git+ssh",
    "git+git",
    "git+file",
    "hg",
    "hg+http",
    "hg+https",
    "hg+ssh",
    "hg+static-http",
    "svn",
    "svn+ssh",
    "svn+http",
    "svn+https",
    "svn+svn",
    "bzr",
    "bzr+http",
    "bzr+https",
    "bzr+ssh",
    "bzr+sftp",
    "bzr+ftp",
    "bzr+lp",
)


# from https://github.com/twisted/txacme/blob/master/src/txacme/test/strategies.py
def dns_labels():
    """
    Strategy for generating limited charset DNS labels.
    """
    # This is too limited, but whatever
    return st.text(
        "abcdefghijklmnopqrstuvwxyz0123456789-", min_size=1, max_size=25
    ).filter(
        lambda s: not any(
            [s.startswith("-"), s.endswith("-"), s.isdigit(), s[2:4] == "--"]
        )
    )


def dns_names():
    """
    Strategy for generating limited charset DNS names.
    """
    return st.lists(dns_labels(), min_size=1, max_size=10).map(".".join)


def urls():
    """
    Strategy for generating urls.
    """
    return st.builds(
        parsed_url,
        scheme=st.sampled_from(uri_schemes),
        netloc=dns_names(),
        path=st.lists(
            st.text(
                max_size=64,
                alphabet=st.characters(
                    blacklist_characters="/?#", blacklist_categories=("Cs",)
                ),
            ),
            min_size=1,
            max_size=10,
        ).map("".join),
    )


def legal_path_chars():
    # Control characters
    # blacklist = [u"{0}".format(chr(n)).encode() for n in range(32)]
    blacklist = []
    if os.name == "nt":
        blacklist.extend(["<", ">", ":", '"', "/", "\\", "|", "?", "*"])
    # errors = "surrogateescape" if six.PY3 else "replace"
    # blacklist = "".join([codecs.decode(s, "utf-8", errors) for s in blacklist])
    return (
        st.text(
            st.characters(
                blacklist_characters=blacklist,
                blacklist_categories=("Cs",),
                min_codepoint=32,
            ),
            min_size=0,
            max_size=64,
        ).filter(lambda s: not s.endswith(" ")).filter(lambda s: not s.startswith("/"))
    )


def relative_paths():
    relative_leaders = (".", "..")
    separators = [
        sep for sep in (os.sep, os.path.sep, os.path.altsep) if sep is not None
    ]
    return st.builds(
        relative_path,
        leading_dots=st.sampled_from(relative_leaders),
        separator=st.sampled_from(separators),
        dest=legal_path_chars(),
    )


def unparsed_urls():
    return st.builds(urllib_parse.urlunparse, urls())

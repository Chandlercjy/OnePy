# This file is inspired and copied from www.backtrader.com
# -*- coding: utf-8; py-indent-offset:4 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import itertools
import sys

PY2 = sys.version_info.major == 2


if PY2:
    try:
        import _winreg as winreg
    except ImportError:
        winreg = None

    MAXINT = sys.maxint
    MININT = -sys.maxint - 1

    MAXFLOAT = sys.float_info.max
    MINFLOAT = sys.float_info.min

    string_types = str, unicode
    integer_types = int, long

    filter = itertools.ifilter
    map = itertools.imap
    range = xrange
    zip = itertools.izip
    long = long

    cmp = cmp

    bytes = bytes
    bstr = bytes

    from io import StringIO

    from urllib2 import urlopen, ProxyHandler, build_opener, install_opener
    from urllib import quote as urlquote

    def iterkeys(d): return d.iterkeys()

    def itervalues(d): return d.itervalues()

    def iteritems(d): return d.iteritems()

    def keys(d): return d.keys()

    def values(d): return d.values()

    def items(d): return d.items()

    import Queue as queue

else:
    try:
        import winreg
    except ImportError:
        winreg = None

    MAXINT = sys.maxsize
    MININT = -sys.maxsize - 1

    MAXFLOAT = sys.float_info.max
    MINFLOAT = sys.float_info.min

    string_types = str,
    integer_types = int,

    filter = filter
    map = map
    range = range
    zip = zip
    long = int

    def cmp(a, b): return (a > b) - (a < b)

    def bytes(x): return x.encode('utf-8')

    def bstr(x): return str(x)

    from io import StringIO

    from urllib.request import (urlopen, ProxyHandler, build_opener,
                                install_opener)
    from urllib.parse import quote as urlquote

    def iterkeys(d): return iter(d.keys())

    def itervalues(d): return iter(d.values())

    def iteritems(d): return iter(d.items())

    def keys(d): return list(d.keys())

    def values(d): return list(d.values())

    def items(d): return list(d.items())

    import queue as queue


# This is from Armin Ronacher from Flash simplified later by six
def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""
    # This requires a bit of explanation: the basic idea is to make a dummy
    # metaclass for one level of class instantiation that replaces itself with
    # the actual metaclass.
    class metaclass(meta):

        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, str('temporary_class'), (), {})

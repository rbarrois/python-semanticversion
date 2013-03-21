# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Raphaël Barrois
# This code is distributed under the two-clause BSD License.

import sys

is_python2 = (sys.version_info[0] == 2)


try:  # pragma: no cover
    import unittest2 as unittest
except ImportError:  # pragma: no cover
    import unittest


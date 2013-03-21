# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Raphaël Barrois
# This code is distributed under the two-clause BSD License.

import sys

is_python2 = (sys.version_info[0] == 2)

if is_python2:  # pragma: no cover
    base_cmp = cmp
else:  # pragma: no cover
    def base_cmp(x, y):
        if x < y:
            return -1
        elif x > y:
            return 1
        else:
            return 0

# -*- coding: utf-8 -*-
# Copyright (c) The python-semanticversion project
# This code is distributed under the two-clause BSD License.

try:  # pragma: no cover
    import django
    from django.conf import settings
    django_loaded = True
except ImportError:  # pragma: no cover
    django_loaded = False


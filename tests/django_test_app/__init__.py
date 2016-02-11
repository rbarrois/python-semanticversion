# -*- coding: utf-8 -*-
# Copyright (c) The python-semanticversion project
# This code is distributed under the two-clause BSD License.

try:  # pragma: no cover
    import django
    from django.conf import settings
    django_loaded = True
except ImportError:  # pragma: no cover
    django_loaded = False


if django_loaded:  # pragma: no cover
    if not settings.configured:
        settings.configure(
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': 'tests/db/test.sqlite',
                }
            },
            INSTALLED_APPS=[
                'tests.django_test_app',
            ],
            MIDDLEWARE_CLASSES=[],
        )
    # https://docs.djangoproject.com/en/dev/releases/1.7/#app-loading-changes
    if django.VERSION >= (1, 7):
        from django.apps import apps
        apps.populate(settings.INSTALLED_APPS)

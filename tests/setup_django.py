# -*- coding: utf-8 -*-
# Copyright (c) The python-semanticversion project

try:  # pragma: no cover
    import django
    django_loaded = True
except ImportError:  # pragma: no cover
    django_loaded = False
    django = None


if django_loaded:
    from django.conf import settings
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
    django.setup()
    from django.apps import apps
    apps.populate(settings.INSTALLED_APPS)

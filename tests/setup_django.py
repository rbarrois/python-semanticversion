# -*- coding: utf-8 -*-
# Copyright (c) The python-semanticversion project


import django
from django.apps import apps
from django.conf import settings


def configure_django():
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

    apps.populate(settings.INSTALLED_APPS)

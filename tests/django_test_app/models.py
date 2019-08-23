# -*- coding: utf-8 -*-
# Copyright (c) The python-semanticversion project

try:
    from django.db import models
    django_loaded = True
except ImportError:
    django_loaded = False


if django_loaded:
    from semantic_version import django_fields as semver_fields

    class VersionModel(models.Model):
        version = semver_fields.VersionField(verbose_name='my version')
        spec = semver_fields.SpecField(verbose_name='my spec')
        npm_spec = semver_fields.SpecField(syntax='npm', blank=True, verbose_name='npm spec')

    class PartialVersionModel(models.Model):
        partial = semver_fields.VersionField(partial=True, verbose_name='partial version')
        optional = semver_fields.VersionField(verbose_name='optional version', blank=True, null=True)
        optional_spec = semver_fields.SpecField(verbose_name='optional spec', blank=True, null=True)

    class CoerceVersionModel(models.Model):
        version = semver_fields.VersionField(verbose_name='my version', coerce=True)
        partial = semver_fields.VersionField(verbose_name='partial version', coerce=True, partial=True)

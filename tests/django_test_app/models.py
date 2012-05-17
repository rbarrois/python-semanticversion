# -*- coding: utf-8 -*-
# Copyright (c) 2012 Raphaël Barrois

from django.db import models
from semantic_version import django_fields as semver_fields


class VersionModel(models.Model):
    version = semver_fields.VersionField(verbose_name='my version')
    spec = semver_fields.SpecField(verbose_name='my spec')
    speclist = semver_fields.SpecListField(verbose_name='my spec list')


class PartialVersionModel(models.Model):
    partial = semver_fields.VersionField(partial=True, verbose_name='partial version')
    optional = semver_fields.VersionField(verbose_name='optional version', blank=True, null=True)
    optional_spec = semver_fields.SpecField(verbose_name='optional spec', blank=True, null=True)
    optional_speclist = semver_fields.SpecListField(verbose_name='optional spec list',
        blank=True, null=True)

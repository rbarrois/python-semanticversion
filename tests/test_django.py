#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012 Raphaël Barrois

try:  # pragma: no cover
    import unittest2 as unittest
except ImportError:  # pragma: no cover
    import unittest

import semantic_version

try:  # pragma: no cover
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
            ]
        )
    from django_test_app import models
    from django.core import serializers


@unittest.skipIf(not django_loaded, "Django not installed")
class DjangoFieldTestCase(unittest.TestCase):
    def test_version(self):
        obj = models.VersionModel(version='0.1.1', spec='>0.1.0', speclist='~=0.1,!~0.1.1')

        self.assertEqual(semantic_version.Version('0.1.1'), obj.version)
        self.assertEqual(semantic_version.Spec('>0.1.0'), obj.spec)
        self.assertEqual(semantic_version.SpecList('~=0.1,!~0.1.1'), obj.speclist)

        alt_obj = models.VersionModel(version=obj.version, spec=obj.spec, speclist=obj.speclist)

        self.assertEqual(semantic_version.Version('0.1.1'), alt_obj.version)
        self.assertEqual(semantic_version.Spec('>0.1.0'), alt_obj.spec)
        self.assertEqual(semantic_version.SpecList('~=0.1,!~0.1.1'), alt_obj.speclist)
        self.assertEqual(obj.spec, alt_obj.spec)
        self.assertEqual(obj.version, alt_obj.version)
        self.assertEqual(obj.speclist, alt_obj.speclist)

    def test_invalid_input(self):
        self.assertRaises(ValueError, models.VersionModel,
            version='0.1.1', spec='blah', speclist='~=0.1,!~0.1.1')
        self.assertRaises(ValueError, models.VersionModel,
            version='0.1', spec='>0.1.1', speclist='~=0.1,!~0.1.1')
        self.assertRaises(ValueError, models.VersionModel,
            version='0.1.1', spec='>0.1.1', speclist='~=0,!=0.2')

    def test_partial(self):
        obj = models.PartialVersionModel(partial='0.1')

        self.assertEqual(semantic_version.Version('0.1', partial=True), obj.partial)
        self.assertIsNone(obj.optional)
        self.assertIsNone(obj.optional_spec)
        self.assertIsNone(obj.optional_speclist)

        alt_obj = models.PartialVersionModel(partial=obj.partial, optional=obj.optional,
            optional_spec=obj.optional_spec, optional_speclist=obj.optional_speclist)
        self.assertEqual(semantic_version.Version('0.1', partial=True), alt_obj.partial)
        self.assertEqual(obj.partial, alt_obj.partial)
        self.assertIsNone(obj.optional)
        self.assertIsNone(obj.optional_spec)
        self.assertIsNone(obj.optional_speclist)

    def test_serialization(self):
        o1 = models.VersionModel(version='0.1.1', spec='<0.2.4-rc42',
            speclist='~=0.1,!=0.1.1')
        o2 = models.VersionModel(version='0.4.3-rc3+build3', spec='~=0.4',
            speclist='<=0.1.1-rc2,!~0.1.1-rc1')

        data = serializers.serialize('json', [o1, o2])

        obj1, obj2 = serializers.deserialize('json', data)
        self.assertEqual(o1, obj1.object)
        self.assertEqual(o2, obj2.object)

    def test_serialization_partial(self):
        o1 = models.PartialVersionModel(partial='0.1.1', optional='0.2.4-rc42',
            optional_spec=None, optional_speclist=None)
        o2 = models.PartialVersionModel(partial='0.4.3-rc3+build3', optional='',
            optional_spec='~=1.1', optional_speclist='~=0.1,!=0.1.1')

        data = serializers.serialize('json', [o1, o2])

        obj1, obj2 = serializers.deserialize('json', data)
        self.assertEqual(o1, obj1.object)
        self.assertEqual(o2, obj2.object)


if django_loaded:
    from django.test import TestCase
    from django.test.simple import DjangoTestSuiteRunner

    class DbInteractingTestCase(TestCase):

        @classmethod
        def setUpClass(cls):
            cls.old_state = DjangoTestSuiteRunner().setup_databases()

        @classmethod
        def tearDownClass(cls):
            DjangoTestSuiteRunner().teardown_databases(cls.old_state)

        def test_db_interaction(self):
            o1 = models.VersionModel(version='0.1.1', spec='<0.2.4-rc42')
            o2 = models.VersionModel(version='0.4.3-rc3+build3', spec='~=0.4')

            o1.save()
            o2.save()

            obj1 = models.VersionModel.objects.get(pk=o1.pk)
            self.assertEqual(o1.version, obj1.version)

            obj2 = models.VersionModel.objects.get(pk=o2.pk)
            self.assertEqual(o2.version, obj2.version)

else:  # pragma: no cover
    pass

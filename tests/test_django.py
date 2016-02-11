# -*- coding: utf-8 -*-
# Copyright (c) The python-semanticversion project
# This code is distributed under the two-clause BSD License.

from __future__ import unicode_literals

try:  # pragma: no cover
    import unittest2 as unittest
except ImportError:  # pragma: no cover
    import unittest

import semantic_version

try:  # pragma: no cover
    import django
    from django.conf import settings
    from .django_test_app import models
    from django.core import serializers
    django_loaded = True
except ImportError:  # pragma: no cover
    django_loaded = False

south = None
# south has reached end of life, and it does not work with django 1.7 and newer
if django_loaded and django.VERSION < (1, 7):  # pragma: no cover
    try:
        import south
        import south.creator.freezer
        import south.modelsinspector
    except ImportError:
        pass

# the refresh_from_db method only came in with 1.8, so in order to make this
# work will all supported versions we have our own function.
def save_and_refresh(obj):
    """Saves an object, and refreshes from the database."""
    obj.save()
    obj = obj.__class__.objects.get(id=obj.id)


@unittest.skipIf(not django_loaded, "Django not installed")
class DjangoFieldTestCase(unittest.TestCase):
    def test_version(self):
        obj = models.VersionModel(version='0.1.1', spec='==0.1.1,!=0.1.1-alpha')

        self.assertEqual(semantic_version.Version('0.1.1'), obj.version)
        self.assertEqual(semantic_version.Spec('==0.1.1,!=0.1.1-alpha'), obj.spec)

        alt_obj = models.VersionModel(version=obj.version, spec=obj.spec)

        self.assertEqual(semantic_version.Version('0.1.1'), alt_obj.version)
        self.assertEqual(semantic_version.Spec('==0.1.1,!=0.1.1-alpha'), alt_obj.spec)
        self.assertEqual(obj.spec, alt_obj.spec)
        self.assertEqual(obj.version, alt_obj.version)

        obj.full_clean()

    def test_version_save(self):
        """Test saving object with a VersionField."""
        # first test with a null value
        obj = models.PartialVersionModel()
        self.assertIsNone(obj.id)
        self.assertIsNone(obj.optional)
        save_and_refresh(obj)
        self.assertIsNotNone(obj.id)
        self.assertIsNone(obj.optional_spec)

        # now set to something that is not null
        spec = semantic_version.Spec('==0,!=0.2')
        obj.optional_spec = spec
        save_and_refresh(obj)
        self.assertEqual(obj.optional_spec, spec)

    def test_spec_save(self):
        """Test saving object with a SpecField."""
        # first test with a null value
        obj = models.PartialVersionModel()
        self.assertIsNone(obj.id)
        self.assertIsNone(obj.optional_spec)
        save_and_refresh(obj)
        self.assertIsNotNone(obj.id)
        self.assertIsNone(obj.optional_spec)

        # now set to something that is not null
        spec = semantic_version.Spec('==0,!=0.2')
        obj.optional_spec = spec
        save_and_refresh(obj)
        self.assertEqual(obj.optional_spec, spec)

    def test_partial_spec(self):
        obj = models.VersionModel(version='0.1.1', spec='==0,!=0.2')
        self.assertEqual(semantic_version.Version('0.1.1'), obj.version)
        self.assertEqual(semantic_version.Spec('==0,!=0.2'), obj.spec)

    def test_coerce(self):
        obj = models.CoerceVersionModel(version='0.1.1a+2', partial='23')
        self.assertEqual(semantic_version.Version('0.1.1-a+2'), obj.version)
        self.assertEqual(semantic_version.Version('23', partial=True), obj.partial)

        obj2 = models.CoerceVersionModel(version='23', partial='0.1.2.3.4.5/6')
        self.assertEqual(semantic_version.Version('23.0.0'), obj2.version)
        self.assertEqual(semantic_version.Version('0.1.2+3.4.5-6', partial=True), obj2.partial)

    def test_invalid_input(self):
        self.assertRaises(ValueError, models.VersionModel,
            version='0.1.1', spec='blah')
        self.assertRaises(ValueError, models.VersionModel,
            version='0.1', spec='==0.1.1,!=0.1.1-alpha')

    def test_partial(self):
        obj = models.PartialVersionModel(partial='0.1.0')

        self.assertEqual(semantic_version.Version('0.1.0', partial=True), obj.partial)
        self.assertIsNone(obj.optional)
        self.assertIsNone(obj.optional_spec)

        # Copy values to another model
        alt_obj = models.PartialVersionModel(
            partial=obj.partial,
            optional=obj.optional,
            optional_spec=obj.optional_spec,
        )

        self.assertEqual(semantic_version.Version('0.1.0', partial=True), alt_obj.partial)
        self.assertEqual(obj.partial, alt_obj.partial)
        self.assertIsNone(obj.optional)
        self.assertIsNone(obj.optional_spec)

        obj.full_clean()

    def test_serialization(self):
        o1 = models.VersionModel(version='0.1.1', spec='==0.1.1,!=0.1.1-alpha')
        o2 = models.VersionModel(version='0.4.3-rc3+build3',
            spec='<=0.1.1-rc2,!=0.1.1-rc1')

        data = serializers.serialize('json', [o1, o2])

        obj1, obj2 = serializers.deserialize('json', data)
        self.assertEqual(o1.version, obj1.object.version)
        self.assertEqual(o1.spec, obj1.object.spec)
        self.assertEqual(o2.version, obj2.object.version)
        self.assertEqual(o2.spec, obj2.object.spec)

    def test_serialization_partial(self):
        o1 = models.PartialVersionModel(partial='0.1.1', optional='0.2.4-rc42',
            optional_spec=None)
        o2 = models.PartialVersionModel(partial='0.4.3-rc3+build3', optional='',
            optional_spec='==0.1.1,!=0.1.1-alpha')

        data = serializers.serialize('json', [o1, o2])

        obj1, obj2 = serializers.deserialize('json', data)
        self.assertEqual(o1.partial, obj1.object.partial)
        self.assertEqual(o1.optional, obj1.object.optional)
        self.assertEqual(o2.partial, obj2.object.partial)
        self.assertEqual(o2.optional, obj2.object.optional)


@unittest.skipIf(not django_loaded or south is None, "Couldn't import south and django")
class SouthTestCase(unittest.TestCase):
    def test_freezing_version_model(self):
        frozen = south.modelsinspector.get_model_fields(models.VersionModel)

        self.assertEqual(frozen['version'],
            ('semantic_version.django_fields.VersionField', [], {'max_length': '200'}))

        self.assertEqual(frozen['spec'],
            ('semantic_version.django_fields.SpecField', [], {'max_length': '200'}))

    def test_freezing_partial_version_model(self):
        frozen = south.modelsinspector.get_model_fields(models.PartialVersionModel)

        self.assertEqual(frozen['partial'],
            ('semantic_version.django_fields.VersionField', [], {'max_length': '200', 'partial': 'True'}))

        self.assertEqual(frozen['optional'],
            ('semantic_version.django_fields.VersionField', [], {'max_length': '200', 'blank': 'True', 'null': 'True'}))

        self.assertEqual(frozen['optional_spec'],
            ('semantic_version.django_fields.SpecField', [], {'max_length': '200', 'blank': 'True', 'null': 'True'}))

    def test_freezing_coerce_version_model(self):
        frozen = south.modelsinspector.get_model_fields(models.CoerceVersionModel)

        self.assertEqual(frozen['version'],
            ('semantic_version.django_fields.VersionField', [], {'max_length': '200', 'coerce': 'True'}))

        self.assertEqual(frozen['partial'],
                ('semantic_version.django_fields.VersionField', [], {'max_length': '200', 'partial': 'True', 'coerce': 'True'}))

    def test_freezing_app(self):
        frozen = south.creator.freezer.freeze_apps('django_test_app')

        # Test VersionModel
        self.assertEqual(frozen['django_test_app.versionmodel']['version'],
            ('semantic_version.django_fields.VersionField', [], {'max_length': '200'}))

        self.assertEqual(frozen['django_test_app.versionmodel']['spec'],
            ('semantic_version.django_fields.SpecField', [], {'max_length': '200'}))

        # Test PartialVersionModel
        self.assertEqual(frozen['django_test_app.partialversionmodel']['partial'],
            ('semantic_version.django_fields.VersionField', [], {'max_length': '200', 'partial': 'True'}))

        self.assertEqual(frozen['django_test_app.partialversionmodel']['optional'],
            ('semantic_version.django_fields.VersionField', [], {'max_length': '200', 'blank': 'True', 'null': 'True'}))

        self.assertEqual(frozen['django_test_app.partialversionmodel']['optional_spec'],
            ('semantic_version.django_fields.SpecField', [], {'max_length': '200', 'blank': 'True', 'null': 'True'}))

        # Test CoerceVersionModel
        self.assertEqual(frozen['django_test_app.coerceversionmodel']['version'],
            ('semantic_version.django_fields.VersionField', [], {'max_length': '200', 'coerce': 'True'}))

        self.assertEqual(frozen['django_test_app.coerceversionmodel']['partial'],
            ('semantic_version.django_fields.VersionField', [], {'max_length': '200', 'partial': 'True', 'coerce': 'True'}))


if django_loaded:
    from django.test import TestCase
    if django.VERSION[:2] < (1, 6):
        from django.test.simple import DjangoTestSuiteRunner as TestRunner
    else:
        from django.test.runner import DiscoverRunner as TestRunner

    class DbInteractingTestCase(TestCase):

        @classmethod
        def setUpClass(cls):
            cls.old_state = TestRunner().setup_databases()

        @classmethod
        def tearDownClass(cls):
            TestRunner().teardown_databases(cls.old_state)

        def test_db_interaction(self):
            o1 = models.VersionModel(version='0.1.1', spec='<0.2.4-rc42')
            o2 = models.VersionModel(version='0.4.3-rc3+build3', spec='==0.4.3')

            o1.save()
            o2.save()

            obj1 = models.VersionModel.objects.get(pk=o1.pk)
            self.assertEqual(o1.version, obj1.version)

            obj2 = models.VersionModel.objects.get(pk=o2.pk)
            self.assertEqual(o2.version, obj2.version)

else:  # pragma: no cover
    pass

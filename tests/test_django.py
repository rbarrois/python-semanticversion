# -*- coding: utf-8 -*-
# Copyright (c) The python-semanticversion project
# This code is distributed under the two-clause BSD License.

import unittest

from semantic_version import Version, SimpleSpec, NpmSpec

from .setup_django import django_loaded


if django_loaded:  # pragma: no cover
    from semantic_version import django_fields
    from .django_test_app import models

    from django.core import serializers
    from django.core.management import call_command
    from django.db import connection
    from django.test import TestCase as DjangoTestCase
    from django.test import TransactionTestCase
    from django.test import runner as django_test_runner
    from django.test import utils as django_test_utils

else:
    DjangoTestCase = unittest.TestCase
    TransactionTestCase = unittest.TestCase


test_state = {}


def setUpModule():
    if not django_loaded:  # pragma: no cover
        raise unittest.SkipTest("Django not installed")
    django_test_utils.setup_test_environment()
    runner = django_test_runner.DiscoverRunner()
    runner_state = runner.setup_databases()
    test_state.update({
        'runner': runner,
        'runner_state': runner_state,
    })


def tearDownModule():
    if not django_loaded:  # pragma: no cover
        return
    runner = test_state['runner']
    runner_state = test_state['runner_state']
    runner.teardown_databases(runner_state)
    django_test_utils.teardown_test_environment()


# the refresh_from_db method only came in with 1.8, so in order to make this
# work will all supported versions we have our own function.
def save_and_refresh(obj):
    """Saves an object, and refreshes from the database."""
    obj.save()
    obj = obj.__class__.objects.get(id=obj.id)


@unittest.skipIf(not django_loaded, "Django not installed")
class DjangoFieldTestCase(unittest.TestCase):
    def test_version(self):
        obj = models.VersionModel(
            version=Version('0.1.1'),
            spec=SimpleSpec('==0.1.1,!=0.1.1-alpha'),
            npm_spec=NpmSpec('1.2 - 2.3'),
        )

        self.assertEqual(Version('0.1.1'), obj.version)
        self.assertEqual(SimpleSpec('==0.1.1,!=0.1.1-alpha'), obj.spec)
        self.assertEqual(NpmSpec('1.2 - 2.3'), obj.npm_spec)

        alt_obj = models.VersionModel(version=obj.version, spec=obj.spec, npm_spec=obj.npm_spec)

        self.assertEqual(Version('0.1.1'), alt_obj.version)
        self.assertEqual(SimpleSpec('==0.1.1,!=0.1.1-alpha'), alt_obj.spec)
        self.assertEqual(obj.spec, alt_obj.spec)
        self.assertEqual(obj.npm_spec, alt_obj.npm_spec)
        self.assertEqual(obj.version, alt_obj.version)

    def test_version_clean(self):
        """Calling .full_clean() should convert str to Version/Spec objects."""
        obj = models.VersionModel(version='0.1.1', spec='==0.1.1,!=0.1.1-alpha', npm_spec='1.x')
        obj.full_clean()

        self.assertEqual(Version('0.1.1'), obj.version)
        self.assertEqual(SimpleSpec('==0.1.1,!=0.1.1-alpha'), obj.spec)
        self.assertEqual(NpmSpec('1.x'), obj.npm_spec)

    def test_version_save(self):
        """Test saving object with a VersionField."""
        # first test with a null value
        obj = models.PartialVersionModel()
        self.assertIsNone(obj.id)
        self.assertIsNone(obj.optional)
        save_and_refresh(obj)
        self.assertIsNotNone(obj.id)
        self.assertIsNone(obj.optional)

        # now set to something that is not null
        version = Version('1.2.3')
        obj.optional = version
        save_and_refresh(obj)
        self.assertEqual(obj.optional, version)

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
        spec = SimpleSpec('==0,!=0.2')
        obj.optional_spec = spec
        save_and_refresh(obj)
        self.assertEqual(obj.optional_spec, spec)

    def test_partial_spec_clean(self):
        obj = models.VersionModel(version='0.1.1', spec='==0,!=0.2')
        obj.full_clean()
        self.assertEqual(Version('0.1.1'), obj.version)
        self.assertEqual(SimpleSpec('==0,!=0.2'), obj.spec)

    def test_coerce_clean(self):
        obj = models.CoerceVersionModel(version='0.1.1a+2', partial='23')
        obj.full_clean()
        self.assertEqual(Version('0.1.1-a+2'), obj.version)
        self.assertEqual(Version('23', partial=True), obj.partial)

        obj2 = models.CoerceVersionModel(version='23', partial='0.1.2.3.4.5/6')
        obj2.full_clean()
        self.assertEqual(Version('23.0.0'), obj2.version)
        self.assertEqual(Version('0.1.2+3.4.5-6', partial=True), obj2.partial)

    def test_invalid_input(self):
        v = models.VersionModel(version='0.1.1', spec='blah')
        self.assertRaises(ValueError, v.full_clean)

        v2 = models.VersionModel(version='0.1', spec='==0.1.1,!=0.1.1-alpha')
        self.assertRaises(ValueError, v2.full_clean)

    def test_partial(self):
        obj = models.PartialVersionModel(partial=Version('0.1.0'))

        self.assertEqual(Version('0.1.0', partial=True), obj.partial)
        self.assertIsNone(obj.optional)
        self.assertIsNone(obj.optional_spec)

        # Copy values to another model
        alt_obj = models.PartialVersionModel(
            partial=obj.partial,
            optional=obj.optional,
            optional_spec=obj.optional_spec,
        )

        self.assertEqual(Version('0.1.0', partial=True), alt_obj.partial)
        self.assertEqual(obj.partial, alt_obj.partial)
        self.assertIsNone(obj.optional)
        self.assertIsNone(obj.optional_spec)

        # Validation should be fine
        obj.full_clean()

    def test_serialization(self):
        o1 = models.VersionModel(
            version=Version('0.1.1'),
            spec=SimpleSpec('==0.1.1,!=0.1.1-alpha'),
            npm_spec=NpmSpec('1.2 - 2.3'),
        )
        o2 = models.VersionModel(
            version=Version('0.4.3-rc3+build3'),
            spec=SimpleSpec('<=0.1.1-rc2,!=0.1.1-rc1'),
            npm_spec=NpmSpec('1.2 - 2.3'),
        )

        data = serializers.serialize('json', [o1, o2])

        obj1, obj2 = serializers.deserialize('json', data)
        self.assertEqual(o1.version, obj1.object.version)
        self.assertEqual(o1.spec, obj1.object.spec)
        self.assertEqual(o1.npm_spec, obj1.object.npm_spec)
        self.assertEqual(o2.version, obj2.object.version)
        self.assertEqual(o2.spec, obj2.object.spec)
        self.assertEqual(o2.npm_spec, obj2.object.npm_spec)

    def test_serialization_partial(self):
        o1 = models.PartialVersionModel(
            partial=Version('0.1.1', partial=True),
            optional=Version('0.2.4-rc42', partial=True),
            optional_spec=None,
        )
        o2 = models.PartialVersionModel(
            partial=Version('0.4.3-rc3+build3', partial=True),
            optional='',
            optional_spec=SimpleSpec('==0.1.1,!=0.1.1-alpha'),
        )

        data = serializers.serialize('json', [o1, o2])

        obj1, obj2 = serializers.deserialize('json', data)
        self.assertEqual(o1.partial, obj1.object.partial)
        self.assertEqual(o1.optional, obj1.object.optional)
        self.assertEqual(o2.partial, obj2.object.partial)
        self.assertEqual(o2.optional, obj2.object.optional)


@unittest.skipIf(not django_loaded, "Django not installed")
class FieldMigrationTests(DjangoTestCase):
    def test_version_field(self):
        field = django_fields.VersionField(
            partial=True,
            coerce=True,
        )
        expected = {
            'coerce': True,
            'partial': True,
            'max_length': 200,
        }
        self.assertEqual(field.deconstruct()[3], expected)

    def test_spec_field(self):
        field = django_fields.SpecField()
        expected = {'max_length': 200}
        self.assertEqual(field.deconstruct()[3], expected)

    def test_nondefault_spec_field(self):
        field = django_fields.SpecField(syntax='npm')
        expected = {'max_length': 200, 'syntax': 'npm'}
        self.assertEqual(field.deconstruct()[3], expected)


@unittest.skipIf(not django_loaded, "Django not installed")
class FullMigrateTests(TransactionTestCase):
    def test_migrate(self):
        # Let's check that this does not crash
        call_command('makemigrations', verbosity=0)
        call_command('migrate', verbosity=0)
        with connection.cursor() as cursor:
            table_list = connection.introspection.get_table_list(cursor)
            table_list = [t.name for t in connection.introspection.get_table_list(cursor)]
            self.assertIn('django_test_app_versionmodel', table_list)


@unittest.skipIf(not django_loaded, "Django not installed")
class DbInteractingTestCase(DjangoTestCase):

    def test_db_interaction(self):
        o1 = models.VersionModel(version=Version('0.1.1'), spec=SimpleSpec('<0.2.4-rc42'))
        o2 = models.VersionModel(version=Version('0.4.3-rc3+build3'), spec=SimpleSpec('==0.4.3'))

        o1.save()
        o2.save()

        obj1 = models.VersionModel.objects.get(pk=o1.pk)
        self.assertEqual(o1.version, obj1.version)

        obj2 = models.VersionModel.objects.get(pk=o2.pk)
        self.assertEqual(o2.version, obj2.version)

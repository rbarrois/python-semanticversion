#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2012 Raphaël Barrois

"""Test the various functions from 'base'."""

try:  # pragma: no cover
    import unittest2 as unittest
except ImportError:  # pragma: no cover
    import unittest


from semantic_version import base

class ComparisonTestCase(unittest.TestCase):
    def test_identifier_cmp(self):
        cases = [
            # Integers
            ('1', '1', 0),
            ('1', '2', -1),
            ('11', '2', 1),
            ('3333', '40', 1),

            # Text
            ('aa', 'ab', -1),
            ('aa', 'aa', 0),
            ('ab', 'aa', 1),
            ('aaa', 'ab', -1),

            # Mixed
            ('10', '1a', -1),
            ('1a', '10', 1),
            ('ab1', '42', 1),
        ]

        for a, b, expected in cases:
            result = base.identifier_cmp(a, b)
            self.assertEqual(expected, result,
                "identifier_cmp(%r, %r) returned %d instead of %d" % (
                    a, b, result, expected))

    def test_identifier_list_cmp(self):
        cases = [
            # Same length
            (['1', '2', '3'], ['1', '2', '3'], 0),
            (['1', '2', '3'], ['1', '3', '2'], -1),
            (['1', '2', '4'], ['1', '2', '3'], 1),

            # Mixed lengths
            (['1', 'a'], ['1', 'a', '0'], -1),
            (['1', 'a', '0'], ['1', 'a'], 1),
            (['1', 'b'], ['1', 'a', '1000'], 1),
        ]

        for a, b, expected in cases:
            result = base.identifier_list_cmp(a, b)
            self.assertEqual(expected, result,
                "identifier_list_cmp(%r, %r) returned %d instead of %d" % (
                    a, b, result, expected))


class VersionTestCase(unittest.TestCase):
    versions = {
        '1.0.0-alpha': (1, 0, 0, ['alpha'], []),
        '1.0.0-alpha.1': (1, 0, 0, ['alpha', '1'], []),
        '1.0.0-beta.2': (1, 0, 0, ['beta', '2'], []),
        '1.0.0-beta.11': (1, 0, 0, ['beta', '11'], []),
        '1.0.0-rc.1': (1, 0, 0, ['rc', '1'], []),
        '1.0.0-rc.1+build.1': (1, 0, 0, ['rc', '1'], ['build', '1']),
        '1.0.0': (1, 0, 0, [], []),
        '1.0.0+0.3.7': (1, 0, 0, [], ['0', '3', '7']),
        '1.3.7+build': (1, 3, 7, [], ['build']),
        '1.3.7+build.2.b8f12d7': (1, 3, 7, [], ['build', '2', 'b8f12d7']),
        '1.3.7+build.11.e0f985a': (1, 3, 7, [], ['build', '11', 'e0f985a']),
        '1.1.1': (1, 1, 1, [], []),
        '1.1.2': (1, 1, 2, [], []),
        '1.1.3-rc4.5': (1, 1, 3, ['rc4', '5'], []),
        '1.1.3-rc42.3-14-15.24+build.2012-04-13.223':
            (1, 1, 3, ['rc42', '3-14-15', '24'], ['build', '2012-04-13', '223']),
        '1.1.3+build.2012-04-13.HUY.alpha-12.1':
            (1, 1, 3, [], ['build', '2012-04-13', 'HUY', 'alpha-12', '1']),
    }

    def test_parsing(self):
        for text, expected_fields in self.versions.items():
            version = base.Version(text)
            actual_fields = (version.major, version.minor, version.patch,
                version.prerelease, version.build)
            self.assertEqual(expected_fields, actual_fields)

    def test_str(self):
        for text, fields in self.versions.items():
            version = base.Version(text)
            self.assertEqual(text, str(version))
            for field in fields:
                self.assertIn(repr(field), repr(version))

    def test_compare_to_self(self):
        for text in self.versions:
            self.assertEqual(base.Version(text), base.Version(text))
            self.assertNotEqual(text, base.Version(text))

    partial_versions = {
        '1.0': (1, 0, None, None, None),
        '1': (1, None, None, None, None),
        '1.0.0-alpha': (1, 0, 0, ['alpha'], None),
        '1.0.0-alpha.1': (1, 0, 0, ['alpha', '1'], None),
        '1.0.0-beta.2': (1, 0, 0, ['beta', '2'], None),
        '1.0.0-beta.11': (1, 0, 0, ['beta', '11'], None),
        '1.0.0-rc.1': (1, 0, 0, ['rc', '1'], None),
        '1.0.0-rc.1+build.1': (1, 0, 0, ['rc', '1'], ['build', '1']),
        '1.0.0': (1, 0, 0, None, None),
        '1.0.0+0.3.7': (1, 0, 0, [], ['0', '3', '7']),
        '1.3.7+build': (1, 3, 7, [], ['build']),
        '1.3.7+build.2.b8f12d7': (1, 3, 7, [], ['build', '2', 'b8f12d7']),
        '1.3.7+build.11.e0f985a': (1, 3, 7, [], ['build', '11', 'e0f985a']),
        '1.1.1': (1, 1, 1, None, None),
        '1.1.2': (1, 1, 2, None, None),
        '1.1.3-rc4.5': (1, 1, 3, ['rc4', '5'], None),
        '1.1.3-rc42.3-14-15.24+build.2012-04-13.223':
            (1, 1, 3, ['rc42', '3-14-15', '24'], ['build', '2012-04-13', '223']),
        '1.1.3+build.2012-04-13.HUY.alpha-12.1':
            (1, 1, 3, [], ['build', '2012-04-13', 'HUY', 'alpha-12', '1']),
    }

    def test_parsing_partials(self):
        for text, expected_fields in self.partial_versions.items():
            version = base.Version(text, partial=True)
            actual_fields = (version.major, version.minor, version.patch,
                version.prerelease, version.build)
            self.assertEqual(expected_fields, actual_fields)

    def test_str_partials(self):
        for text, fields in self.partial_versions.items():
            version = base.Version(text, partial=True)
            self.assertEqual(text, str(version))
            for field in fields:
                self.assertIn(repr(field), repr(version))

    def test_compare_partial_to_self(self):
        for text in self.partial_versions:
            self.assertEqual(
                base.Version(text, partial=True),
                base.Version(text, partial=True))
            self.assertNotEqual(text, base.Version(text, partial=True))


class SpecTestCase(unittest.TestCase):
    def test_equality(self):
        spec1 = base.Spec('==0.1.0')
        spec2 = base.Spec('==0.1.0')
        self.assertEqual(spec1, spec2)
        self.assertFalse(spec1 == '==0.1.0')

    def test_to_string(self):
        spec = base.Spec('==0.1.0')
        self.assertEqual('==0.1.0', str(spec))
        self.assertEqual(base.Spec.KIND_EQUAL, spec.kind)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()

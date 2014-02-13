#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Raphaël Barrois
# This code is distributed under the two-clause BSD License.

"""Test the various functions from 'base'."""

from .compat import unittest, is_python2

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


class TopLevelTestCase(unittest.TestCase):
    """Test module-level functions."""

    versions = (
        ('0.1.0', '0.1.1', -1),
        ('0.1.1', '0.1.1', 0),
        ('0.1.1', '0.1.0', 1),
        ('0.1.0-alpha', '0.1.0', -1),
        ('0.1.0-alpha+2', '0.1.0-alpha', 1),
    )

    def test_compare(self):
        for a, b, expected in self.versions:
            result = base.compare(a, b)
            self.assertEqual(expected, result,
                "compare(%r, %r) should be %r instead of %r" % (a, b, expected, result))

    matches = (
        ('>=0.1.1', '0.1.2'),
        ('>=0.1.1', '0.1.1'),
        ('>=0.1.1', '0.1.1-alpha'),
        ('>=0.1.1,!=0.2.0', '0.2.1'),
    )

    def test_match(self):
        for spec, version in self.matches:
            self.assertTrue(base.match(spec, version),
                "%r should accept %r" % (spec, version))

    valid_strings = (
        '1.0.0-alpha',
        '1.0.0-alpha.1',
        '1.0.0-beta.2',
        '1.0.0-beta.11',
        '1.0.0-rc.1',
        '1.0.0-rc.1+build.1',
        '1.0.0',
        '1.0.0+0.3.7',
        '1.3.7+build',
        '1.3.7+build.2.b8f12d7',
        '1.3.7+build.11.e0f985a',
        '1.1.1',
        '1.1.2',
        '1.1.3-rc4.5',
        '1.1.3-rc42.3-14-15.24+build.2012-04-13.223',
        '1.1.3+build.2012-04-13.HUY.alpha-12.1',
    )

    def test_validate_valid(self):
        for version in self.valid_strings:
            self.assertTrue(base.validate(version),
                "%r should be a valid version" % (version,))

    invalid_strings = (
        '1',
        'v1',
        '1.2.3.4',
        '1.2',
        '1.2a3',
        '1.2.3a4',
        'v12.34.5',
        '1.2.3+4+5',
    )

    def test_validate_invalid(self):
        for version in self.invalid_strings:
            self.assertFalse(base.validate(version),
                "%r should not be a valid version" % (version,))


class VersionTestCase(unittest.TestCase):
    versions = {
        '1.0.0-alpha': (1, 0, 0, ('alpha',), ()),
        '1.0.0-alpha.1': (1, 0, 0, ('alpha', '1'), ()),
        '1.0.0-beta.2': (1, 0, 0, ('beta', '2'), ()),
        '1.0.0-beta.11': (1, 0, 0, ('beta', '11'), ()),
        '1.0.0-rc.1': (1, 0, 0, ('rc', '1'), ()),
        '1.0.0-rc.1+build.1': (1, 0, 0, ('rc', '1'), ('build', '1')),
        '1.0.0': (1, 0, 0, (), ()),
        '1.0.0+0.3.7': (1, 0, 0, (), ('0', '3', '7')),
        '1.3.7+build': (1, 3, 7, (), ('build',)),
        '1.3.7+build.2.b8f12d7': (1, 3, 7, (), ('build', '2', 'b8f12d7')),
        '1.3.7+build.11.e0f985a': (1, 3, 7, (), ('build', '11', 'e0f985a')),
        '1.1.1': (1, 1, 1, (), ()),
        '1.1.2': (1, 1, 2, (), ()),
        '1.1.3-rc4.5': (1, 1, 3, ('rc4', '5'), ()),
        '1.1.3-rc42.3-14-15.24+build.2012-04-13.223':
            (1, 1, 3, ('rc42', '3-14-15', '24'), ('build', '2012-04-13', '223')),
        '1.1.3+build.2012-04-13.HUY.alpha-12.1':
            (1, 1, 3, (), ('build', '2012-04-13', 'HUY', 'alpha-12', '1')),
    }

    def test_parsing(self):
        for text, expected_fields in self.versions.items():
            version = base.Version(text)
            actual_fields = (version.major, version.minor, version.patch,
                version.prerelease, version.build)
            self.assertEqual(expected_fields, actual_fields)

    def test_str(self):
        for text in self.versions:
            version = base.Version(text)
            self.assertEqual(text, str(version))
            self.assertEqual("Version('%s')" % text, repr(version))

    def test_compare_to_self(self):
        for text in self.versions:
            self.assertEqual(base.Version(text), base.Version(text))
            self.assertNotEqual(text, base.Version(text))

    partial_versions = {
        '1.1': (1, 1, None, None, None),
        '2': (2, None, None, None, None),
        '1.0.0-alpha': (1, 0, 0, ('alpha',), None),
        '1.0.0-alpha.1': (1, 0, 0, ('alpha', '1'), None),
        '1.0.0-beta.2': (1, 0, 0, ('beta', '2'), None),
        '1.0.0-beta.11': (1, 0, 0, ('beta', '11'), None),
        '1.0.0-rc.1': (1, 0, 0, ('rc', '1'), None),
        '1.0.0': (1, 0, 0, None, None),
        '1.1.1': (1, 1, 1, None, None),
        '1.1.2': (1, 1, 2, None, None),
        '1.1.3-rc4.5': (1, 1, 3, ('rc4', '5'), None),
        '1.0.0-': (1, 0, 0, (), None),
        '1.0.0+': (1, 0, 0, (), ()),
        '1.0.0-rc.1+build.1': (1, 0, 0, ('rc', '1'), ('build', '1')),
        '1.0.0+0.3.7': (1, 0, 0, (), ('0', '3', '7')),
        '1.3.7+build': (1, 3, 7, (), ('build',)),
        '1.3.7+build.2.b8f12d7': (1, 3, 7, (), ('build', '2', 'b8f12d7')),
        '1.3.7+build.11.e0f985a': (1, 3, 7, (), ('build', '11', 'e0f985a')),
        '1.1.3-rc42.3-14-15.24+build.2012-04-13.223':
            (1, 1, 3, ('rc42', '3-14-15', '24'), ('build', '2012-04-13', '223')),
        '1.1.3+build.2012-04-13.HUY.alpha-12.1':
            (1, 1, 3, (), ('build', '2012-04-13', 'HUY', 'alpha-12', '1')),
    }

    def test_parsing_partials(self):
        for text, expected_fields in self.partial_versions.items():
            version = base.Version(text, partial=True)
            actual_fields = (version.major, version.minor, version.patch,
                version.prerelease, version.build)
            self.assertEqual(expected_fields, actual_fields)
            self.assertTrue(version.partial, "%r should have partial=True" % version)

    def test_str_partials(self):
        for text in self.partial_versions:
            version = base.Version(text, partial=True)
            self.assertEqual(text, str(version))
            self.assertEqual("Version('%s', partial=True)" % text, repr(version))

    def test_compare_partial_to_self(self):
        for text in self.partial_versions:
            self.assertEqual(
                base.Version(text, partial=True),
                base.Version(text, partial=True))
            self.assertNotEqual(text, base.Version(text, partial=True))

    def test_hash(self):
        self.assertEqual(1,
            len(set([base.Version('0.1.0'), base.Version('0.1.0')])))

        self.assertEqual(2,
            len(set([base.Version('0.1.0'), base.Version('0.1.0', partial=True)])))

        # A fully-defined 'partial' version isn't actually partial.
        self.assertEqual(1,
            len(set([
                base.Version('0.1.0-a1+34'),
                base.Version('0.1.0-a1+34', partial=True)
            ]))
        )

    @unittest.skipIf(is_python2, "Comparisons to other objects are broken in Py2.")
    def test_invalid_comparisons(self):
        v = base.Version('0.1.0')
        with self.assertRaises(TypeError):
            v < '0.1.0'
        with self.assertRaises(TypeError):
            v <= '0.1.0'
        with self.assertRaises(TypeError):
            v > '0.1.0'
        with self.assertRaises(TypeError):
            v >= '0.1.0'

        self.assertTrue(v != '0.1.0')
        self.assertFalse(v == '0.1.0')


class SpecItemTestCase(unittest.TestCase):
    components = {
        '==0.1.0': (base.SpecItem.KIND_EQUAL, 0, 1, 0, None, None),
        '==0.1.2-rc3': (base.SpecItem.KIND_EQUAL, 0, 1, 2, ('rc3',), None),
        '==0.1.2+build3.14': (base.SpecItem.KIND_EQUAL, 0, 1, 2, (), ('build3', '14')),
        '<=0.1.1+': (base.SpecItem.KIND_LTE, 0, 1, 1, (), ()),
        '<0.1.1': (base.SpecItem.KIND_LT, 0, 1, 1, None, None),
        '<=0.1.1': (base.SpecItem.KIND_LTE, 0, 1, 1, None, None),
        '<=0.1.1-': (base.SpecItem.KIND_LTE, 0, 1, 1, (), None),
        '>=0.2.3-rc2': (base.SpecItem.KIND_GTE, 0, 2, 3, ('rc2',), None),
        '>0.2.3-rc2+': (base.SpecItem.KIND_GT, 0, 2, 3, ('rc2',), ()),
        '>=2.0.0': (base.SpecItem.KIND_GTE, 2, 0, 0, None, None),
        '!=0.1.1+': (base.SpecItem.KIND_NEQ, 0, 1, 1, (), ()),
        '!=0.3.0': (base.SpecItem.KIND_NEQ, 0, 3, 0, None, None),
    }

    def test_components(self):
        for spec_text, components in self.components.items():
            kind, major, minor, patch, prerelease, build = components
            spec = base.SpecItem(spec_text)

            self.assertEqual(kind, spec.kind)
            self.assertEqual(major, spec.spec.major)
            self.assertEqual(minor, spec.spec.minor)
            self.assertEqual(patch, spec.spec.patch)
            self.assertEqual(prerelease, spec.spec.prerelease)
            self.assertEqual(build, spec.spec.build)

            self.assertNotEqual(spec, spec_text)
            self.assertEqual(spec_text, str(spec))

    matches = {
        '==0.1.0': (
            ['0.1.0', '0.1.0-rc1', '0.1.0+build1', '0.1.0-rc1+build2'],
            ['0.0.1', '0.2.0', '0.1.1'],
        ),
        '==0.1.2-rc3': (
            ['0.1.2-rc3+build1', '0.1.2-rc3+build4.5'],
            ['0.1.2-rc4', '0.1.2', '0.1.3'],
        ),
        '==0.1.2+build3.14': (
            ['0.1.2+build3.14'],
            ['0.1.2-rc+build3.14', '0.1.2+build3.15'],
        ),
        '<=0.1.1': (
            ['0.0.0', '0.1.1-alpha1', '0.1.1', '0.1.1+build2'],
            ['0.1.2'],
        ),
        '<0.1.1': (
            ['0.1.0', '0.0.0'],
            ['0.1.1', '0.1.1-zzz+999', '1.2.0', '0.1.1+build3'],
        ),
        '<=0.1.1': (
            ['0.1.1+build4', '0.1.1-alpha', '0.1.0'],
            ['0.2.3', '1.1.1', '0.1.2'],
        ),
        '<0.1.1-': (
            ['0.1.0', '0.1.1-alpha', '0.1.1-alpha+4'],
            ['0.2.0', '1.0.0', '0.1.1', '0.1.1+build1'],
        ),
        '>=0.2.3-rc2': (
            ['0.2.3-rc3', '0.2.3', '0.2.3+1', '0.2.3-rc2', '0.2.3-rc2+1'],
            ['0.2.3-rc1', '0.2.2'],
        ),
        '>0.2.3-rc2+': (
            ['0.2.3-rc3', '0.2.3', '0.2.3-rc2+1'],
            ['0.2.3-rc1', '0.2.2', '0.2.3-rc2'],
        ),
        '>2.0.0+': (
            ['2.1.1', '2.0.0+b1', '3.1.4'],
            ['1.9.9', '1.9.9999', '2.0.0', '2.0.0-rc4'],
        ),
        '!=0.1.1': (
            ['0.1.2', '0.1.0', '1.4.2'],
            ['0.1.1', '0.1.1-alpha', '0.1.1+b1'],
        ),
        '!=0.3.4-': (
            ['0.4.0', '1.3.0', '0.3.4-alpha', '0.3.4-alpha+b1'],
            ['0.3.4', '0.3.4+b1'],
        ),
    }

    def test_matches(self):
        for spec_text, versions in self.matches.items():
            spec = base.SpecItem(spec_text)
            matching, failing = versions

            for version_text in matching:
                version = base.Version(version_text)
                self.assertTrue(spec.match(version), "%r should match %r" % (version, spec))

            for version_text in failing:
                version = base.Version(version_text)
                self.assertFalse(spec.match(version),
                    "%r should not match %r" % (version, spec))

    def test_equality(self):
        spec1 = base.SpecItem('==0.1.0')
        spec2 = base.SpecItem('==0.1.0')
        self.assertEqual(spec1, spec2)
        self.assertFalse(spec1 == '==0.1.0')

    def test_to_string(self):
        spec = base.SpecItem('==0.1.0')
        self.assertEqual('==0.1.0', str(spec))
        self.assertEqual(base.SpecItem.KIND_EQUAL, spec.kind)

    def test_hash(self):
        self.assertEqual(1,
            len(set([base.SpecItem('==0.1.0'), base.SpecItem('==0.1.0')])))


class CoerceTestCase(unittest.TestCase):
    examples = {
        # Dict of target: [list of equivalents]
        '0.0.0': ('0', '0.0', '0.0.0', '0.0.0+', '0-'),
        '0.1.0': ('0.1', '0.1+', '0.1-', '0.1.0'),
        '0.1.0+2': ('0.1.0+2', '0.1.0.2'),
        '0.1.0+2.3.4': ('0.1.0+2.3.4', '0.1.0+2+3+4', '0.1.0.2+3+4'),
        '0.1.0+2-3.4': ('0.1.0+2-3.4', '0.1.0+2-3+4', '0.1.0.2-3+4', '0.1.0.2_3+4'),
        '0.1.0-a2.3': ('0.1.0-a2.3', '0.1.0a2.3', '0.1.0_a2.3'),
        '0.1.0-a2.3+4.5-6': ('0.1.0-a2.3+4.5-6', '0.1.0a2.3+4.5-6', '0.1.0a2.3+4.5_6', '0.1.0a2.3+4+5/6'),
    }

    def test_coerce(self):
        for equivalent, samples in self.examples.items():
            target = base.Version(equivalent)
            for sample in samples:
                v_sample = base.Version.coerce(sample)
                self.assertEqual(target, v_sample)

    def test_invalid(self):
        self.assertRaises(ValueError, base.Version.coerce, 'v1')


class SpecTestCase(unittest.TestCase):
    examples = {
        '>=0.1.1,<0.1.2': ['>=0.1.1', '<0.1.2'],
        '>=0.1.0,!=0.1.3-rc1,<0.1.3': ['>=0.1.0', '!=0.1.3-rc1', '<0.1.3'],
    }

    def test_parsing(self):
        for spec_list_text, specs in self.examples.items():
            spec_list = base.Spec(spec_list_text)

            self.assertEqual(spec_list_text, str(spec_list))
            self.assertNotEqual(spec_list_text, spec_list)
            self.assertEqual(specs, [str(spec) for spec in spec_list])

            for spec_text in specs:
                self.assertTrue(repr(base.SpecItem(spec_text)) in repr(spec_list))

    split_examples = {
        ('>=0.1.1', '<0.1.2', '!=0.1.1+build1'): ['>=0.1.1', '<0.1.2', '!=0.1.1+build1'],
        ('>=0.1.0', '!=0.1.3-rc1,<0.1.3'): ['>=0.1.0', '!=0.1.3-rc1', '<0.1.3'],
    }

    def test_parsing_split(self):
        for spec_list_texts, specs in self.split_examples.items():
            spec_list = base.Spec(*spec_list_texts)

            self.assertEqual(','.join(spec_list_texts), str(spec_list))
            self.assertEqual(specs, [str(spec) for spec in spec_list])
            self.assertEqual(spec_list, base.Spec(','.join(spec_list_texts)))

            for spec_text in specs:
                self.assertTrue(repr(base.SpecItem(spec_text)) in repr(spec_list))

    matches = {
        '>=0.1.1,<0.1.2': (
            ['0.1.1', '0.1.1+4', '0.1.1-alpha'],
            ['0.1.2-alpha', '0.1.2', '1.3.4'],
        ),
        '>=0.1.0+,!=0.1.3-rc1,<0.1.4': (
            ['0.1.1', '0.1.0+b4', '0.1.2', '0.1.3-rc2'],
            ['0.0.1', '0.1.4', '0.1.4-alpha', '0.1.3-rc1+4',
             '0.1.0-alpha', '0.2.2', '0.1.4-rc1'],
        ),
    }

    def test_matches(self):
        for spec_list_text, versions in self.matches.items():
            spec_list = base.Spec(spec_list_text)
            matching, failing = versions

            for version_text in matching:
                version = base.Version(version_text)
                self.assertTrue(version in spec_list,
                    "%r should be in %r" % (version, spec_list))
                self.assertTrue(spec_list.match(version),
                    "%r should match %r" % (version, spec_list))

            for version_text in failing:
                version = base.Version(version_text)
                self.assertFalse(version in spec_list,
                    "%r should not be in %r" % (version, spec_list))
                self.assertFalse(spec_list.match(version),
                    "%r should not match %r" % (version, spec_list))

    def test_equality(self):
        for spec_list_text in self.examples:
            slist1 = base.Spec(spec_list_text)
            slist2 = base.Spec(spec_list_text)
            self.assertEqual(slist1, slist2)
            self.assertFalse(slist1 == spec_list_text)

    def test_filter_empty(self):
        s = base.Spec('>=0.1.1')
        res = tuple(s.filter(()))
        self.assertEqual((), res)

    def test_filter_incompatible(self):
        s = base.Spec('>=0.1.1,!=0.1.4')
        res = tuple(s.filter([
            base.Version('0.1.0'),
            base.Version('0.1.4'),
            base.Version('0.1.4-alpha'),
        ]))
        self.assertEqual((), res)

    def test_filter_compatible(self):
        s = base.Spec('>=0.1.1,!=0.1.4,<0.2.0')
        res = tuple(s.filter([
            base.Version('0.1.0'),
            base.Version('0.1.1'),
            base.Version('0.1.5'),
            base.Version('0.1.4-alpha'),
            base.Version('0.1.2'),
            base.Version('0.2.0-rc1'),
            base.Version('3.14.15'),
        ]))

        expected = (
            base.Version('0.1.1'),
            base.Version('0.1.5'),
            base.Version('0.1.2'),
        )

        self.assertEqual(expected, res)

    def test_select_empty(self):
        s = base.Spec('>=0.1.1')
        self.assertIsNone(s.select(()))

    def test_select_incompatible(self):
        s = base.Spec('>=0.1.1,!=0.1.4')
        res = s.select([
            base.Version('0.1.0'),
            base.Version('0.1.4'),
            base.Version('0.1.4-alpha'),
        ])
        self.assertIsNone(res)

    def test_select_compatible(self):
        s = base.Spec('>=0.1.1,!=0.1.4,<0.2.0')
        res = s.select([
            base.Version('0.1.0'),
            base.Version('0.1.1'),
            base.Version('0.1.5'),
            base.Version('0.1.4-alpha'),
            base.Version('0.1.2'),
            base.Version('0.2.0-rc1'),
            base.Version('3.14.15'),
        ])

        self.assertEqual(base.Version('0.1.5'), res)

    def test_contains(self):
        self.assertFalse('ii' in base.Spec('>=0.1.1'))

    def test_hash(self):
        self.assertEqual(1,
            len(set([base.Spec('>=0.1.1'), base.Spec('>=0.1.1')])))


if __name__ == '__main__':  # pragma: no cover
    unittest.main()

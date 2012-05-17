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
        '1.0.0-alpha': (1, 0, 0, ('alpha',), None),
        '1.0.0-alpha.1': (1, 0, 0, ('alpha', '1'), None),
        '1.0.0-beta.2': (1, 0, 0, ('beta', '2'), None),
        '1.0.0-beta.11': (1, 0, 0, ('beta', '11'), None),
        '1.0.0-rc.1': (1, 0, 0, ('rc', '1'), None),
        '1.0.0-rc.1+build.1': (1, 0, 0, ('rc', '1'), ('build', '1')),
        '1.0.0': (1, 0, 0, None, None),
        '1.0.0+0.3.7': (1, 0, 0, (), ('0', '3', '7')),
        '1.3.7+build': (1, 3, 7, (), ('build',)),
        '1.3.7+build.2.b8f12d7': (1, 3, 7, (), ('build', '2', 'b8f12d7')),
        '1.3.7+build.11.e0f985a': (1, 3, 7, (), ('build', '11', 'e0f985a')),
        '1.1.1': (1, 1, 1, None, None),
        '1.1.2': (1, 1, 2, None, None),
        '1.1.3-rc4.5': (1, 1, 3, ('rc4', '5'), None),
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


class SpecTestCase(unittest.TestCase):
    components = {
        '~=0.1': (base.Spec.KIND_EQ_LOOSE, 0, 1, None, None, None),
        '~=0.1.2-rc3': (base.Spec.KIND_EQ_LOOSE, 0, 1, 2, ('rc3',), None),
        '~=0.1.2+build3.14': (base.Spec.KIND_EQ_LOOSE, 0, 1, 2, (), ('build3', '14')),
        '<=0.1.1': (base.Spec.KIND_LTE, 0, 1, 1, (), ()),
        '<0.1.1': (base.Spec.KIND_LT, 0, 1, 1, (), ()),
        '<~0.1.1': (base.Spec.KIND_LTE_LOOSE, 0, 1, 1, None, None),
        '<~0.1': (base.Spec.KIND_LTE_LOOSE, 0, 1, None, None, None),
        '>=0.2.3-rc2': (base.Spec.KIND_GTE, 0, 2, 3, ('rc2',), ()),
        '>0.2.3-rc2': (base.Spec.KIND_GT, 0, 2, 3, ('rc2',), ()),
        '>~2': (base.Spec.KIND_GTE_LOOSE, 2, None, None, None, None),
        '!=0.1.1': (base.Spec.KIND_NEQ, 0, 1, 1, (), ()),
        '!~0.3': (base.Spec.KIND_NEQ_LOOSE, 0, 3, None, None, None),
    }

    def test_components(self):
        for spec_text, components in self.components.items():
            kind, major, minor, patch, prerelease, build = components
            spec = base.Spec(spec_text)

            self.assertNotEqual(spec, spec_text)
            self.assertEqual(spec_text, str(spec))

            self.assertEqual(kind, spec.kind)
            self.assertEqual(major, spec.spec.major)
            self.assertEqual(minor, spec.spec.minor)
            self.assertEqual(patch, spec.spec.patch)
            self.assertEqual(prerelease, spec.spec.prerelease)
            self.assertEqual(build, spec.spec.build)

    matches = {
        '~=0.1': (
            ['0.1.0', '0.1.99', '0.1.0-rc1', '0.1.4-rc1+build2'],
            ['0.0.1', '0.2.0'],
        ),
        '~=0.1.2-rc3': (
            ['0.1.2-rc3+build1', '0.1.2-rc3+build4.5'],
            ['0.1.2-rc4', '0.1.2', '0.1.3'],
        ),
        '~=0.1.2+build3.14': (
            ['0.1.2+build3.14'],
            ['0.1.2-rc+build3.14', '0.1.2+build3.15'],
        ),
        '<=0.1.1': (
            ['0.0.0', '0.1.1-alpha1', '0.1.1'],
            ['0.1.1+build2', '0.1.2'],
        ),
        '<0.1.1': (
            ['0.1.0', '0.1.1-zzz+999', '0.0.0'],
            ['0.1.1', '1.2.0', '0.1.1+build3'],
        ),
        '<~0.1.1': (
            ['0.1.1+build4', '0.1.1-alpha', '0.1.0'],
            ['0.2.3', '1.1.1', '0.1.2'],
        ),
        '<~0.1': (
            ['0.1.0', '0.1.1+4', '0.1.99', '0.1.0-alpha', '0.0.1'],
            ['0.2.0', '1.0.0'],
        ),
        '>=0.2.3-rc2': (
            ['0.2.3-rc3', '0.2.3', '0.2.3+1', '0.2.3-rc2', '0.2.3-rc2+1'],
            ['0.2.3-rc1', '0.2.2'],
        ),
        '>0.2.3-rc2': (
            ['0.2.3-rc3', '0.2.3', '0.2.3-rc2+1'],
            ['0.2.3-rc1', '0.2.2'],
        ),
        '>~2': (
            ['2.1.1', '2.0.0-alpha1', '3.1.4'],
            ['1.9.9', '1.9.9999'],
        ),
        '!=0.1.1': (
            ['0.1.1-alpha', '0.1.2', '0.1.0', '1.4.2'],
            ['0.1.1'],
        ),
        '!~0.3': (
            ['0.4.0', '1.3.0'],
            ['0.3.0', '0.3.99', '0.3.0-alpha', '0.3.999999+4'],
        ),
    }

    def test_matches(self):
        for spec_text, versions in self.matches.items():
            spec = base.Spec(spec_text)
            matching, failing = versions

            for version_text in matching:
                version = base.Version(version_text)
                self.assertTrue(version in spec, "%r should be in %r" % (version, spec))
                self.assertTrue(spec.match(version), "%r should match %r" % (version, spec))

            for version_text in failing:
                version = base.Version(version_text)
                self.assertFalse(version in spec,
                    "%r should not be in %r" % (version, spec))
                self.assertFalse(spec.match(version),
                    "%r should not match %r" % (version, spec))

    def test_equality(self):
        spec1 = base.Spec('==0.1.0')
        spec2 = base.Spec('==0.1.0')
        self.assertEqual(spec1, spec2)
        self.assertFalse(spec1 == '==0.1.0')

    def test_to_string(self):
        spec = base.Spec('==0.1.0')
        self.assertEqual('==0.1.0', str(spec))
        self.assertEqual(base.Spec.KIND_EQUAL, spec.kind)

    def test_hash(self):
        self.assertEqual(1,
            len(set([base.Spec('==0.1.0'), base.Spec('==0.1.0')])))


class SpecListTestCase(unittest.TestCase):
    examples = {
        '>=0.1.1,<0.1.2': ['>=0.1.1', '<0.1.2'],
        '>~0.1,!=0.1.3-rc1,<0.1.3': ['>~0.1', '!=0.1.3-rc1', '<0.1.3'],
    }

    def test_parsing(self):
        for spec_list_text, specs in self.examples.items():
            spec_list = base.SpecList(spec_list_text)

            self.assertEqual(spec_list_text, str(spec_list))
            self.assertNotEqual(spec_list_text, spec_list)
            self.assertEqual(specs, [str(spec) for spec in spec_list])

            for spec_text in specs:
                self.assertTrue(repr(base.Spec(spec_text)) in repr(spec_list))

    split_examples = {
        ('>=0.1.1', '<0.1.2', '!=0.1.1+build1'): ['>=0.1.1', '<0.1.2', '!=0.1.1+build1'],
        ('>~0.1', '!=0.1.3-rc1,<0.1.3'): ['>~0.1', '!=0.1.3-rc1', '<0.1.3'],
    }

    def test_parsing_split(self):
        for spec_list_texts, specs in self.split_examples.items():
            spec_list = base.SpecList(*spec_list_texts)

            self.assertEqual(','.join(spec_list_texts), str(spec_list))
            self.assertEqual(specs, [str(spec) for spec in spec_list])
            self.assertEqual(spec_list, base.SpecList(','.join(spec_list_texts)))

            for spec_text in specs:
                self.assertTrue(repr(base.Spec(spec_text)) in repr(spec_list))

    matches = {
        '>=0.1.1,<0.1.2': (
            ['0.1.1', '0.1.2-alpha', '0.1.1+4'],
            ['0.1.1-alpha', '0.1.2', '1.3.4'],
        ),
        '>~0.1,!=0.1.3-rc1,<0.1.3': (
            ['0.1.1', '0.1.3-rc1+4', '0.1.3-alpha'],
            ['0.0.1', '0.1.3', '0.2.2', '0.1.3-rc1'],
        ),
    }

    def test_matches(self):
        for spec_list_text, versions in self.matches.items():
            spec_list = base.SpecList(spec_list_text)
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
            slist1 = base.SpecList(spec_list_text)
            slist2 = base.SpecList(spec_list_text)
            self.assertEqual(slist1, slist2)
            self.assertFalse(slist1 == spec_list_text)

    def test_contains(self):
        self.assertFalse('ii' in base.SpecList('>=0.1.1'))

    def test_hash(self):
        self.assertEqual(1,
            len(set([base.SpecList('>=0.1.1'), base.SpecList('>=0.1.1')])))


if __name__ == '__main__':  # pragma: no cover
    unittest.main()

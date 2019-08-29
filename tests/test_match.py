#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) The python-semanticversion project
# This code is distributed under the two-clause BSD License.

import unittest
import sys

import semantic_version


class MatchTestCase(unittest.TestCase):
    if sys.version_info[0] <= 2:
        import contextlib
        @contextlib.contextmanager
        def subTest(self, **kwargs):
            yield

    invalid_specs = [
        '',
        '!0.1',
        '<=0.1.4a',
        '>0.1.1.1',
        '<0.1.2-rc1.3-14.15+build.2012-01-01.11h34',
    ]

    valid_specs = [
        '*',
        '==0.1.0',
        '=0.1.0',
        '0.1.0',
        '<=0.1.1',
        '<0.1',
        '1',
        '>0.1.2-rc1',
        '>=0.1.2-rc1.3.4',
        '==0.1.2+build42-12.2012-01-01.12h23',
        '!=0.1.2-rc1.3-14.15+build.2012-01-01.11h34',
        '^0.1.2',
        '~0.1.2',
        '~=0.1.2',
    ]

    matches = {
        '*': [
            '0.1.1',
            '0.1.1+build4.5',
            '0.1.2-rc1',
            '0.1.2-rc1.3',
            '0.1.2-rc1.3.4',
            '0.1.2+build42-12.2012-01-01.12h23',
            '0.1.2-rc1.3-14.15+build.2012-01-01.11h34',
            '0.2.0',
            '1.0.0',
        ],
        '==0.1.2': [
            '0.1.2+build42-12.2012-01-01.12h23',
        ],
        '=0.1.2': [
            '0.1.2+build42-12.2012-01-01.12h23',
        ],
        '0.1.2': [
            '0.1.2+build42-12.2012-01-01.12h23',
        ],
        '<=0.1.2': [
            '0.1.1',
            '0.1.2-rc1',
            '0.1.2-rc1.3.4',
            '0.1.2',
            '0.1.2+build4',
        ],
        '!=0.1.2+': [
            '0.1.2+1',
            '0.1.2-rc1',
        ],
        '!=0.1.2-': [
            '0.1.1',
            '0.1.2-rc1',
        ],
        '!=0.1.2+345': [
            '0.1.1',
            '0.1.2-rc1+345',
            '0.1.2+346',
            '0.2.3+345',
        ],
        '>=0.1.1': [
            '0.1.1',
            '0.1.1+build4.5',
            '0.1.2-rc1.3',
            '0.2.0',
            '1.0.0',
        ],
        '>0.1.1': [
            '0.1.2+build4.5',
            '0.1.2-rc1.3',
            '0.2.0',
            '1.0.0',
        ],
        '<0.1.1-': [
            '0.1.1-alpha',
            '0.1.1-rc4',
            '0.1.0+12.3',
        ],
        '^0.1.2': [
            '0.1.2',
            '0.1.2+build4.5',
            '0.1.3-rc1.3',
            '0.1.4',
        ],
        '~0.1.2': [
            '0.1.2',
            '0.1.2+build4.5',
            '0.1.3-rc1.3',
        ],
        '~=1.4.5': (
            '1.4.5',
            '1.4.10-alpha',
            '1.4.10',
        ),
        '~=1.4': [
            '1.4.0',
            '1.6.10-alpha',
            '1.6.10',
        ],
    }

    def test_invalid(self):
        for invalid in self.invalid_specs:
            with self.subTest(spec=invalid):
                with self.assertRaises(ValueError, msg="Spec(%r) should be invalid" % invalid):
                    semantic_version.Spec(invalid)

    def test_simple(self):
        for valid in self.valid_specs:
            with self.subTest(spec=valid):
                spec = semantic_version.SpecItem(valid)
                normalized = str(spec)
                self.assertEqual(spec, semantic_version.SpecItem(normalized))

    def test_match(self):
        for spec_text, versions in self.matches.items():
            for version_text in versions:
                with self.subTest(spec=spec_text, version=version_text):
                    spec = semantic_version.Spec(spec_text)
                    self.assertNotEqual(spec, spec_text)
                    version = semantic_version.Version(version_text)
                    self.assertIn(version, spec)
                    self.assertTrue(spec.match(version), "%r does not match %r" % (version, spec))
                    self.assertTrue(semantic_version.match(spec_text, version_text))

    def test_contains(self):
        spec = semantic_version.Spec('<=0.1.1')
        self.assertFalse('0.1.0' in spec, "0.1.0 should not be in %r" % spec)

        version = semantic_version.Version('0.1.1+4.2')
        self.assertTrue(version in spec, "%r should be in %r" % (version, spec))

        version = semantic_version.Version('0.1.1-rc1+4.2')
        self.assertTrue(version in spec, "%r should be in %r" % (version, spec))

    def test_prerelease_check(self):
        strict_spec = semantic_version.Spec('>=0.1.1-')
        lax_spec = semantic_version.Spec('>=0.1.1')
        version = semantic_version.Version('0.1.1-rc1+4.2')
        self.assertFalse(version in lax_spec, "%r should not be in %r" % (version, lax_spec))
        self.assertFalse(version in strict_spec, "%r should not be in %r" % (version, strict_spec))

    def test_build_check(self):
        spec = semantic_version.Spec('<=0.1.1-rc1')
        version = semantic_version.Version('0.1.1-rc1+4.2')
        self.assertTrue(version in spec, "%r should be in %r" % (version, spec))


if __name__ == '__main__':  # pragma: no cover
    unittest.main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Raphaël Barrois
# This code is distributed under the two-clause BSD License.

import unittest

import semantic_version


class MatchTestCase(unittest.TestCase):
    invalid_specs = [
        '',
        '!0.1',
        '<=0.1.4a',
        '>0.1.1.1',
        '~0.1.2-rc23,1',
    ]

    valid_specs = [
        '==0.1.0',
        '<=0.1.1',
        '<0.1',
        '>0.1.2-rc1',
        '>=0.1.2-rc1.3.4',
        '==0.1.2+build42-12.2012-01-01.12h23',
        '<0.1.2-rc1.3-14.15+build.2012-01-01.11h34',
    ]

    matches = {
        '==0.1.2': [
            '0.1.2-rc1',
            '0.1.2-rc1.3.4',
            '0.1.2+build42-12.2012-01-01.12h23',
            '0.1.2-rc1.3-14.15+build.2012-01-01.11h34',
        ],
        '<=0.1.2': [
            '0.1.1',
            '0.1.2-rc1',
            '0.1.2-rc1.3.4',
            '0.1.2',
            '0.1.2+build4',
        ],
        '<0.1.2+': [
            '0.1.1',
            '0.1.2-rc1',
            '0.1.2-rc1.3.4',
            '0.1.2-rc1+build4.5',
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
        '>0.1.1+': [
            '0.1.1+b2',
            '0.1.2-rc1',
            '1.1.1',
            '2.0.4',
        ],
        '<0.1.1-': [
            '0.1.1-alpha',
            '0.1.1-rc4',
            '0.1.0+12.3',
        ],
    }

    def test_invalid(self):
        for invalid in self.invalid_specs:
            self.assertRaises(ValueError, semantic_version.Spec, invalid)

    def test_simple(self):
        for valid in self.valid_specs:
            version = semantic_version.Spec(valid)
            self.assertEqual(valid, str(version))

    def test_match(self):
        for spec_txt, versions in self.matches.items():
            spec = semantic_version.Spec(spec_txt)
            self.assertNotEqual(spec, spec_txt)
            for version_txt in versions:
                version = semantic_version.Version(version_txt)
                self.assertTrue(spec.match(version), "%r does not match %r" % (version, spec))
                self.assertTrue(semantic_version.match(spec_txt, version_txt))
                self.assertTrue(version in spec, "%r not in %r" % (version, spec))

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
        self.assertTrue(version in lax_spec, "%r should be in %r" % (version, lax_spec))
        self.assertFalse(version in strict_spec, "%r should not be in %r" % (version, strict_spec))

    def test_build_check(self):
        strict_spec = semantic_version.Spec('<=0.1.1-rc1+')
        lax_spec = semantic_version.Spec('<=0.1.1-rc1')
        version = semantic_version.Version('0.1.1-rc1+4.2')
        self.assertTrue(version in lax_spec, "%r should be in %r" % (version, lax_spec))
        self.assertFalse(version in strict_spec, "%r should not be in %r" % (version, strict_spec))


if __name__ == '__main__':  # pragma: no cover
    unittest.main()


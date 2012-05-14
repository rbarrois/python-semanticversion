#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import semantic_version


class MatchTestCase(unittest.TestCase):
    invalid_specs = [
        '',
        '!0.1',
        '<0.1',
        '<=0.1.4a',
        '>0.1.1.1',
        '~0.1.2-rc23,1',
    ]

    valid_specs = [
        '~0.1',
        '<=0.1.1',
        '>0.1.2-rc1',
        '>=0.1.2-rc1.3.4',
        '==0.1.2+build42-12.2012-01-01.12h23',
        '<0.1.2-rc1.3-14.15+build.2012-01-01.11h34',
    ]

    matches = {
        '~0.1': [
            '0.1.1',
            '0.1.2-rc1',
            '0.1.2-rc1.3.4',
            '0.1.2+build42-12.2012-01-01.12h23',
            '0.1.2-rc1.3-14.15+build.2012-01-01.11h34',
        ],
        '~0.1.2': [
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
        ],
        '<0.1.2': [
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
            '0.1.1+build4.5',
            '0.1.2-rc1.3',
            '0.2.0',
            '1.0.0',
        ],
    }

    def test_invalid(self):
        for invalid in self.invalid_specs:
            self.assertRaises(ValueError, semantic_version.RequirementSpec, invalid)

    def test_simple(self):
        for valid in self.valid_specs:
            version = semantic_version.RequirementSpec(valid)
            self.assertEqual(valid, str(version))

    def test_match(self):
        for spec_txt, versions in self.matches.items():
            spec = semantic_version.RequirementSpec(spec_txt)
            for version_txt in versions:
                version = semantic_version.SemanticVersion(version_txt)
                
                self.assertTrue(spec.match(version), "%r does not match %r" % (version, spec))
                self.assertTrue(semantic_version.match(spec_txt, version_txt))


if __name__ == '__main__':  # pragma: no cover
    unittest.main()


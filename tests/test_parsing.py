#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Raphaël Barrois
# This code is distributed under the two-clause BSD License.

import unittest

import semantic_version


class ParsingTestCase(unittest.TestCase):
    invalids = [
        None,
        '',
        '0',
        '0.1',
        '0.1.4a',
        '0.1.1.1',
        '0.1.2-rc23,1',
    ]

    valids = [
        '0.1.1',
        '0.1.2-rc1',
        '0.1.2-rc1.3.4',
        '0.1.2+build42-12.2012-01-01.12h23',
        '0.1.2-rc1.3-14.15+build.2012-01-01.11h34',
    ]

    def test_invalid(self):
        for invalid in self.invalids:
            self.assertRaises(ValueError, semantic_version.Version, invalid)

    def test_simple(self):
        for valid in self.valids:
            version = semantic_version.Version(valid)
            self.assertEqual(valid, str(version))


class ComparisonTestCase(unittest.TestCase):
    order = [
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
    ]

    def test_comparisons(self):
        for i, first in enumerate(self.order):
            first_ver = semantic_version.Version(first)
            for j, second in enumerate(self.order):
                second_ver = semantic_version.Version(second)
                if i < j:
                    self.assertTrue(first_ver < second_ver, '%r !< %r' % (first_ver, second_ver))
                elif i == j:
                    self.assertTrue(first_ver == second_ver, '%r != %r' % (first_ver, second_ver))
                else:
                    self.assertTrue(first_ver > second_ver, '%r !> %r' % (first_ver, second_ver))

                cmp_res = -1 if i < j else (1 if i > j else 0)
                self.assertEqual(cmp_res, semantic_version.compare(first, second))


if __name__ == '__main__':  # pragma: no cover
    unittest.main()

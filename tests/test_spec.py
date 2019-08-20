#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) The python-semanticversion project
# This code is distributed under the two-clause BSD License.

"""Test conformance to the specs."""

import unittest

import semantic_version

# shortcut
Version = semantic_version.Version


class FormatTests(unittest.TestCase):
    """Tests proper version validation."""

    def test_major_minor_patch(self):
        # SPEC:
        # A normal version number MUST take the form X.Y.Z

        with self.assertRaises(ValueError):
            Version('1')
        with self.assertRaises(ValueError):
            Version('1.1')
        # Doesn't raise
        Version('1.2.3')
        with self.assertRaises(ValueError):
            Version('1.2.3.4')

        # SPEC:
        # Where X, Y, and Z are non-negative integers,

        with self.assertRaises(ValueError):
            Version('1.2.A')
        with self.assertRaises(ValueError):
            Version('1.-2.3')
        # Valid
        v = Version('1.2.3')
        self.assertEqual(1, v.major)
        self.assertEqual(2, v.minor)
        self.assertEqual(3, v.patch)

        # SPEC:
        # And MUST NOT contain leading zeroes
        with self.assertRaises(ValueError):
            Version('1.2.01')
        with self.assertRaises(ValueError):
            Version('1.02.1')
        with self.assertRaises(ValueError):
            Version('01.2.1')
        # Valid
        v = Version('0.0.0')
        self.assertEqual(0, v.major)
        self.assertEqual(0, v.minor)
        self.assertEqual(0, v.patch)

    def test_prerelease(self):
        # SPEC:
        # A pre-release version MAY be denoted by appending a hyphen and a
        # series of dot separated identifiers immediately following the patch
        # version.

        with self.assertRaises(ValueError):
            Version('1.2.3 -23')
        # Valid
        v = Version('1.2.3-23')
        self.assertEqual(('23',), v.prerelease)

        # SPEC:
        # Identifiers MUST comprise only ASCII alphanumerics and hyphen.
        # Identifiers MUST NOT be empty
        with self.assertRaises(ValueError):
            Version('1.2.3-a,')
        with self.assertRaises(ValueError):
            Version('1.2.3-..')

        # SPEC:
        # Numeric identifiers MUST NOT include leading zeroes.

        with self.assertRaises(ValueError):
            Version('1.2.3-a0.01')
        with self.assertRaises(ValueError):
            Version('1.2.3-00')
        # Valid
        v = Version('1.2.3-0a.0.000zz')
        self.assertEqual(('0a', '0', '000zz'), v.prerelease)

    def test_build(self):
        # SPEC:
        # Build metadata MAY be denoted by appending a plus sign and a series of
        # dot separated identifiers immediately following the patch or
        # pre-release version

        v = Version('1.2.3')
        self.assertEqual((), v.build)
        with self.assertRaises(ValueError):
            Version('1.2.3 +4')

        # SPEC:
        # Identifiers MUST comprise only ASCII alphanumerics and hyphen.
        # Identifiers MUST NOT be empty
        with self.assertRaises(ValueError):
            Version('1.2.3+a,')
        with self.assertRaises(ValueError):
            Version('1.2.3+..')

        # Leading zeroes allowed
        v = Version('1.2.3+0.0a.01')
        self.assertEqual(('0', '0a', '01'), v.build)

    def test_precedence(self):
        # SPEC:
        # Precedence is determined by the first difference when comparing from
        # left to right as follows: Major, minor, and patch versions are always
        # compared numerically.
        # Example: 1.0.0 < 2.0.0 < 2.1.0 < 2.1.1
        self.assertLess(Version('1.0.0'), Version('2.0.0'))
        self.assertLess(Version('2.0.0'), Version('2.1.0'))
        self.assertLess(Version('2.1.0'), Version('2.1.1'))

        # SPEC:
        # When major, minor, and patch are equal, a pre-release version has
        # lower precedence than a normal version.
        # Example: 1.0.0-alpha < 1.0.0
        self.assertLess(Version('1.0.0-alpha'), Version('1.0.0'))

        # SPEC:
        # Precedence for two pre-release versions with the same major, minor,
        # and patch version MUST be determined by comparing each dot separated
        # identifier from left to right until a difference is found as follows:
        # identifiers consisting of only digits are compared numerically
        self.assertLess(Version('1.0.0-1'), Version('1.0.0-2'))

        # and identifiers with letters or hyphens are compared lexically in
        # ASCII sort order.
        self.assertLess(Version('1.0.0-aa'), Version('1.0.0-ab'))

        # Numeric identifiers always have lower precedence than
        # non-numeric identifiers.
        self.assertLess(Version('1.0.0-9'), Version('1.0.0-a'))

        # A larger set of pre-release fields has a higher precedence than a
        # smaller set, if all of the preceding identifiers are equal.
        self.assertLess(Version('1.0.0-a.b.c'), Version('1.0.0-a.b.c.0'))

        # Example: 1.0.0-alpha < 1.0.0-alpha.1 < 1.0.0-alpha.beta
        # < 1.0.0-beta < 1.0.0-beta.2 < 1.0.0-beta.11 < 1.0.0-rc.1 < 1.0.0.
        self.assertLess(Version('1.0.0-alpha'), Version('1.0.0-alpha.1'))
        self.assertLess(Version('1.0.0-alpha.1'), Version('1.0.0-alpha.beta'))
        self.assertLess(Version('1.0.0-alpha.beta'), Version('1.0.0-beta'))
        self.assertLess(Version('1.0.0-beta'), Version('1.0.0-beta.2'))
        self.assertLess(Version('1.0.0-beta.2'), Version('1.0.0-beta.11'))
        self.assertLess(Version('1.0.0-beta.11'), Version('1.0.0-rc.1'))
        self.assertLess(Version('1.0.0-rc.1'), Version('1.0.0'))

# -*- coding: utf-8 -*-
# Copyright (c) 2012 Raphaël Barrois


import itertools
import re


def _to_int(value):
    try:
        return int(value), True
    except ValueError:
        return value, False


def identifier_cmp(a, b):
    """Compare two identifier (for pre-release/build components)."""

    a_cmp, a_is_int = _to_int(a)
    b_cmp, b_is_int = _to_int(b)

    if a_is_int and b_is_int:
        # Numeric identifiers are compared as integers
        return cmp(a_cmp, b_cmp)
    elif a_is_int:
        # Numeric identifiers have lower precedence
        return -1
    elif b_is_int:
        return 1
    else:
        # Non-numeric identifers are compared lexicographically
        return cmp(a_cmp, b_cmp)


def identifier_list_cmp(a, b):
    identifier_pairs = zip(a, b)
    for id_a, id_b in identifier_pairs:
        cmp_res = identifier_cmp(id_a, id_b)
        if cmp_res != 0:
            return cmp_res
    # alpha1.3 < alpha1.3.1
    return cmp(len(a), len(b))


class SemanticVersion(object):

    version_re = re.compile('^(\d+)\.(\d+)\.(\d+)(?:-([0-9a-zA-Z.-]+))?(?:\+([0-9a-zA-Z.-]+))?$')

    def __init__(self, version_string):
        major, minor, patch, prerelease, build = self.parse(version_string)
        self.major = int(major)
        self.minor = int(minor)
        self.patch = int(patch)
        if prerelease is None:
            self.prerelease = []
        else:
            self.prerelease = prerelease.split('.')
        if build is None:
            self.build = []
        else:
            self.build = build.split('.')

    @classmethod
    def parse(cls, version_string):
        if not version_string:
            raise ValueError('Invalid version string %r.' % version_string)

        match = cls.version_re.match(version_string)
        if match:
            return match.groups()
        else:
            raise ValueError('Invalid version string %r.' % version_string)

    def __str__(self):
        prerelease = '.'.join(self.prerelease)
        build = '.'.join(self.build)
        version = '%d.%d.%d' % (self.major, self.minor, self.patch)
        if prerelease:
            version = '%s-%s' % (version, prerelease)
        if build:
            version = '%s+%s' % (version, build)
        return version

    def __repr__(self):
        return '<SemVer(%d, %d, %d, %r, %r)>' % (
            self.major,
            self.minor,
            self.patch,
            self.prerelease,
            self.build,
        )

    def __cmp__(self, other):
        if not isinstance(other, SemanticVersion):
            return NotImplemented

        base_cmp = cmp(
            (self.major, self.minor, self.patch),
            (other.major, other.minor, other.patch))

        if base_cmp != 0:
            return base_cmp

        if self.prerelease and other.prerelease:
            prerelease_cmp = identifier_list_cmp(self.prerelease, other.prerelease)
            if prerelease_cmp != 0:
                return prerelease_cmp
        elif self.prerelease:
            # Prerelease version have lower precedence
            return -1
        elif other.prerelease:
            return 1

        if self.build and other.build:
            return identifier_list_cmp(self.build, other.build)
        elif self.build:
            # Build version have higher precedence
            return 1
        elif other.build:
            return -1
        else:
            return 0


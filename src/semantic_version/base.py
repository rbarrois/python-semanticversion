# -*- coding: utf-8 -*-
# Copyright (c) 2012 Raphaël Barrois


import functools
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
    """Compare two identifier list (pre-release/build components).

    The rule is:
        - Identifiers are paired between lists
        - They are compared from left to right
        - If all first identifiers match, the longest list is greater.

    >>> identifier_list_cmp(['1', '2'], ['1', '2'])
    0
    >>> identifier_list_cmp(['1', '2a'], ['1', '2b'])
    -1
    >>> identifier_list_cmp(['1'], ['1', '2'])
    -1
    """
    identifier_pairs = zip(a, b)
    for id_a, id_b in identifier_pairs:
        cmp_res = identifier_cmp(id_a, id_b)
        if cmp_res != 0:
            return cmp_res
    # alpha1.3 < alpha1.3.1
    return cmp(len(a), len(b))


class Version(object):

    version_re = re.compile('^(\d+)\.(\d+)\.(\d+)(?:-([0-9a-zA-Z.-]+))?(?:\+([0-9a-zA-Z.-]+))?$')
    partial_version_re = re.compile('^(\d+)(?:\.(\d+)(?:\.(\d+)(?:-([0-9a-zA-Z.-]+))?(?:\+([0-9a-zA-Z.-]+))?)?)?$')

    def __init__(self, version_string, partial=False):
        major, minor, patch, prerelease, build = self.parse(version_string, partial)

        self.major = major
        self.minor = minor
        self.patch = patch
        self.prerelease = prerelease
        self.build = build

        self.partial = partial

    @classmethod
    def parse(cls, version_string, partial=False):
        if not version_string:
            raise ValueError('Invalid empty version string: %r' % version_string)

        if partial:
            version_re = cls.partial_version_re
        else:
            version_re = cls.version_re

        match = version_re.match(version_string)
        if not match:
            raise ValueError('Invalid version string: %r' % version_string)

        major, minor, patch, prerelease, build = match.groups()

        major = int(major)

        if minor is None:
            return (major, None, None, None, None)
        else:
            minor = int(minor)

        if patch is None:
            return (major, minor, None, None, None)
        else:
            patch = int(patch)

        if prerelease is None:
            if partial and not build:
                # No build info, strip here
                return (major, minor, patch, None, None)
            else:
                prerelease = []
        else:
            prerelease = prerelease.split('.')

        if build is None:
            if partial:
                build = None
            else:
                build = []
        else:
            build = build.split('.')

        return (major, minor, patch, prerelease, build)

    def __iter__(self):
        return iter((self.major, self.minor, self.patch, self.prerelease, self.build))

    def __str__(self):
        if self.minor is None:
            return '%d' % self.major
        elif self.patch is None:
            return '%d.%d' % (self.major, self.minor)

        version = '%d.%d.%d' % (self.major, self.minor, self.patch)

        if self.prerelease:
            version = '%s-%s' % (version, '.'.join(self.prerelease))
        if self.build:
            version = '%s+%s' % (version, '.'.join(self.build))
        return version

    def __repr__(self):
        return '<%sSemVer(%s, %s, %s, %r, %r)>' % (
            '~' if self.partial else '',
            self.major,
            self.minor,
            self.patch,
            self.prerelease,
            self.build,
        )

    def _comparison_functions(self, partial=False):
        def prerelease_cmp(a, b):
            if a and b:
                return identifier_list_cmp(a, b)
            elif a:
                # Versions with prerelease field have lower precedence
                return -1
            elif b:
                return 1
            else:
                return 0

        def build_cmp(a, b):
            if a and b:
                return identifier_list_cmp(a, b)
            elif a:
                # Versions with build field have higher precedence
                return 1
            elif b:
                return -1
            else:
                return 0

        def make_optional(orig_cmp_fun):
            @functools.wraps(orig_cmp_fun)
            def alt_cmp_fun(a, b):
                if a is None or b is None:
                    return 0
                return orig_cmp_fun(a, b)

            return alt_cmp_fun

        if partial:
            return [
                cmp,
                make_optional(cmp),
                make_optional(cmp),
                make_optional(prerelease_cmp),
                make_optional(build_cmp),
            ]
        else:
            return [
                cmp,
                cmp,
                cmp,
                prerelease_cmp,
                build_cmp,
            ]

    def __cmp__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented

        field_pairs = zip(self, other)
        comparison_functions = self._comparison_functions(partial=self.partial or other.partial)

        for cmp_fun, field_pair in zip(comparison_functions, field_pairs):
            self_field, other_field = field_pair
            cmp_res = cmp_fun(self_field, other_field)
            if cmp_res != 0:
                return cmp_res

        return 0


class Spec(object):
    """A requirement specification."""

    KIND_LT = '<'
    KIND_LTE = '<='
    KIND_EQUAL = '=='
    KIND_GTE = '>='
    KIND_GT = '>'
    KIND_ALMOST = '~'

    re_spec = re.compile(r'^(<|<=|==|>=|>|~)(\d.*)$')

    def __init__(self, requirement_string):
        kind, spec = self.parse(requirement_string)
        self.kind = kind
        self.spec = spec

    @classmethod
    def parse(cls, requirement_string):
        if not requirement_string:
            raise ValueError("Invalid empty requirement specification: %r" % requirement_string)

        match = cls.re_spec.match(requirement_string)
        if not match:
            raise ValueError("Invalid requirement specification: %r" % requirement_string)

        kind, version = match.groups()
        spec = Version(version, partial=(kind == cls.KIND_ALMOST))
        return (kind, spec)

    def match(self, version):
        if self.kind == self.KIND_LT:
            return version < self.spec
        elif self.kind == self.KIND_LTE:
            return version <= self.spec
        elif self.kind in (self.KIND_EQUAL, self.KIND_ALMOST):
            # self.spec must be on left side, since it is a partial match.
            return self.spec == version
        elif self.kind == self.KIND_GTE:
            return version >= self.spec
        elif self.kind == self.KIND_GT:
            return version > self.spec
        else:  # pragma: no cover
            raise ValueError('Unexpected match kind: %r' % self.kind)

    def __contains__(self, version):
        if isinstance(version, Version):
            return self.match(version)
        return False

    def __str__(self):
        return '%s%s' % (self.kind, self.spec)

    def __repr__(self):
        return '<Spec: %s %r>' % (self.kind, self.spec)

    def __eq__(self, other):
        if not isinstance(other, Spec):
            return NotImplemented
        return self.kind == other.kind and self.spec == other.spec


def compare(v1, v2):
    return cmp(Version(v1), Version(v2))


def match(spec, version):
    return Spec(spec).match(Version(version))

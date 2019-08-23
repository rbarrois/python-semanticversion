# -*- coding: utf-8 -*-
# Copyright (c) The python-semanticversion project
# This code is distributed under the two-clause BSD License.

import functools
import re


def _to_int(value):
    try:
        return int(value), True
    except ValueError:
        return value, False


def _has_leading_zero(value):
    return (value
            and value[0] == '0'
            and value.isdigit()
            and value != '0')


def base_cmp(x, y):
    if x == y:
        return 0
    elif x > y:
        return 1
    elif x < y:
        return -1
    else:
        return NotImplemented


def identifier_cmp(a, b):
    """Compare two identifier (for pre-release/build components)."""

    a_cmp, a_is_int = _to_int(a)
    b_cmp, b_is_int = _to_int(b)

    if a_is_int and b_is_int:
        # Numeric identifiers are compared as integers
        return base_cmp(a_cmp, b_cmp)
    elif a_is_int:
        # Numeric identifiers have lower precedence
        return -1
    elif b_is_int:
        return 1
    else:
        # Non-numeric identifiers are compared lexicographically
        return base_cmp(a_cmp, b_cmp)


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
    return base_cmp(len(a), len(b))


class Version:

    version_re = re.compile(r'^(\d+)\.(\d+)\.(\d+)(?:-([0-9a-zA-Z.-]+))?(?:\+([0-9a-zA-Z.-]+))?$')
    partial_version_re = re.compile(r'^(\d+)(?:\.(\d+)(?:\.(\d+))?)?(?:-([0-9a-zA-Z.-]*))?(?:\+([0-9a-zA-Z.-]*))?$')

    def __init__(
            self,
            version_string=None,
            *,
            major=None,
            minor=None,
            patch=None,
            prerelease=None,
            build=None,
            partial=False):
        has_text = version_string is not None
        has_parts = not (major is minor is patch is prerelease is build is None)
        if not has_text ^ has_parts:
            raise ValueError("Call either Version('1.2.3') or Version(major=1, ...).")

        if has_text:
            major, minor, patch, prerelease, build = self.parse(version_string, partial)
        else:
            # Convenience: allow to omit prerelease/build.
            prerelease = tuple(prerelease or ())
            if not partial:
                build = tuple(build or ())
            self._validate_kwargs(major, minor, patch, prerelease, build, partial)

        self.major = major
        self.minor = minor
        self.patch = patch
        self.prerelease = prerelease
        self.build = build

        self.partial = partial

    @classmethod
    def _coerce(cls, value, allow_none=False):
        if value is None and allow_none:
            return value
        return int(value)

    def next_major(self):
        if self.prerelease and self.minor == self.patch == 0:
            return Version(
                major=self.major,
                minor=0,
                patch=0,
                partial=self.partial,
            )
        else:
            return Version(
                major=self.major + 1,
                minor=0,
                patch=0,
                partial=self.partial,
            )

    def next_minor(self):
        if self.prerelease and self.patch == 0:
            return Version(
                major=self.major,
                minor=self.minor,
                patch=0,
                partial=self.partial,
            )
        else:
            return Version(
                major=self.major,
                minor=self.minor + 1,
                patch=0,
                partial=self.partial,
            )

    def next_patch(self):
        if self.prerelease:
            return Version(
                major=self.major,
                minor=self.minor,
                patch=self.patch,
                partial=self.partial,
            )
        else:
            return Version(
                major=self.major,
                minor=self.minor,
                patch=self.patch + 1,
                partial=self.partial,
            )

    def truncate(self, level='patch'):
        """Return a new Version object, truncated up to the selected level."""
        if level == 'build':
            return self
        elif level == 'prerelease':
            return Version(
                major=self.major,
                minor=self.minor,
                patch=self.patch,
                prerelease=self.prerelease,
                partial=self.partial,
            )
        elif level == 'patch':
            return Version(
                major=self.major,
                minor=self.minor,
                patch=self.patch,
                partial=self.partial,
            )
        elif level == 'minor':
            return Version(
                major=self.major,
                minor=self.minor,
                patch=None if self.partial else 0,
                partial=self.partial,
            )
        elif level == 'major':
            return Version(
                major=self.major,
                minor=None if self.partial else 0,
                patch=None if self.partial else 0,
                partial=self.partial,
            )
        else:
            raise ValueError("Invalid truncation level `%s`." % level)

    @classmethod
    def coerce(cls, version_string, partial=False):
        """Coerce an arbitrary version string into a semver-compatible one.

        The rule is:
        - If not enough components, fill minor/patch with zeroes; unless
          partial=True
        - If more than 3 dot-separated components, extra components are "build"
          data. If some "build" data already appeared, append it to the
          extra components

        Examples:
            >>> Version.coerce('0.1')
            Version(0, 1, 0)
            >>> Version.coerce('0.1.2.3')
            Version(0, 1, 2, (), ('3',))
            >>> Version.coerce('0.1.2.3+4')
            Version(0, 1, 2, (), ('3', '4'))
            >>> Version.coerce('0.1+2-3+4_5')
            Version(0, 1, 0, (), ('2-3', '4-5'))
        """
        base_re = re.compile(r'^\d+(?:\.\d+(?:\.\d+)?)?')

        match = base_re.match(version_string)
        if not match:
            raise ValueError(
                "Version string lacks a numerical component: %r"
                % version_string
            )

        version = version_string[:match.end()]
        if not partial:
            # We need a not-partial version.
            while version.count('.') < 2:
                version += '.0'

        if match.end() == len(version_string):
            return Version(version, partial=partial)

        rest = version_string[match.end():]

        # Cleanup the 'rest'
        rest = re.sub(r'[^a-zA-Z0-9+.-]', '-', rest)

        if rest[0] == '+':
            # A 'build' component
            prerelease = ''
            build = rest[1:]
        elif rest[0] == '.':
            # An extra version component, probably 'build'
            prerelease = ''
            build = rest[1:]
        elif rest[0] == '-':
            rest = rest[1:]
            if '+' in rest:
                prerelease, build = rest.split('+', 1)
            else:
                prerelease, build = rest, ''
        elif '+' in rest:
            prerelease, build = rest.split('+', 1)
        else:
            prerelease, build = rest, ''

        build = build.replace('+', '.')

        if prerelease:
            version = '%s-%s' % (version, prerelease)
        if build:
            version = '%s+%s' % (version, build)

        return cls(version, partial=partial)

    @classmethod
    def parse(cls, version_string, partial=False, coerce=False):
        """Parse a version string into a Version() object.

        Args:
            version_string (str), the version string to parse
            partial (bool), whether to accept incomplete input
            coerce (bool), whether to try to map the passed in string into a
                valid Version.
        """
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

        if _has_leading_zero(major):
            raise ValueError("Invalid leading zero in major: %r" % version_string)
        if _has_leading_zero(minor):
            raise ValueError("Invalid leading zero in minor: %r" % version_string)
        if _has_leading_zero(patch):
            raise ValueError("Invalid leading zero in patch: %r" % version_string)

        major = int(major)
        minor = cls._coerce(minor, partial)
        patch = cls._coerce(patch, partial)

        if prerelease is None:
            if partial and (build is None):
                # No build info, strip here
                return (major, minor, patch, None, None)
            else:
                prerelease = ()
        elif prerelease == '':
            prerelease = ()
        else:
            prerelease = tuple(prerelease.split('.'))
            cls._validate_identifiers(prerelease, allow_leading_zeroes=False)

        if build is None:
            if partial:
                build = None
            else:
                build = ()
        elif build == '':
            build = ()
        else:
            build = tuple(build.split('.'))
            cls._validate_identifiers(build, allow_leading_zeroes=True)

        return (major, minor, patch, prerelease, build)

    @classmethod
    def _validate_identifiers(cls, identifiers, allow_leading_zeroes=False):
        for item in identifiers:
            if not item:
                raise ValueError(
                    "Invalid empty identifier %r in %r"
                    % (item, '.'.join(identifiers))
                )

            if item[0] == '0' and item.isdigit() and item != '0' and not allow_leading_zeroes:
                raise ValueError("Invalid leading zero in identifier %r" % item)

    @classmethod
    def _validate_kwargs(cls, major, minor, patch, prerelease, build, partial):
        if (
                major != int(major)
                or minor != cls._coerce(minor, partial)
                or patch != cls._coerce(patch, partial)
                or prerelease is None and not partial
                or build is None and not partial
        ):
            raise ValueError(
                "Invalid kwargs to Version(major=%r, minor=%r, patch=%r, "
                "prerelease=%r, build=%r, partial=%r" % (
                    major, minor, patch, prerelease, build, partial
                ))
        if prerelease is not None:
            cls._validate_identifiers(prerelease, allow_leading_zeroes=False)
        if build is not None:
            cls._validate_identifiers(build, allow_leading_zeroes=True)

    def __iter__(self):
        return iter((self.major, self.minor, self.patch, self.prerelease, self.build))

    def __str__(self):
        version = '%d' % self.major
        if self.minor is not None:
            version = '%s.%d' % (version, self.minor)
        if self.patch is not None:
            version = '%s.%d' % (version, self.patch)

        if self.prerelease or (self.partial and self.prerelease == () and self.build is None):
            version = '%s-%s' % (version, '.'.join(self.prerelease))
        if self.build or (self.partial and self.build == ()):
            version = '%s+%s' % (version, '.'.join(self.build))
        return version

    def __repr__(self):
        return '%s(%r%s)' % (
            self.__class__.__name__,
            str(self),
            ', partial=True' if self.partial else '',
        )

    @classmethod
    def _comparison_functions(cls, partial=False):
        """Retrieve comparison methods to apply on version components.

        This is a private API.

        Args:
            partial (bool): whether to provide 'partial' or 'strict' matching.

        Returns:
            5-tuple of cmp-like functions.
        """

        def prerelease_cmp(a, b):
            """Compare prerelease components.

            Special rule: a version without prerelease component has higher
            precedence than one with a prerelease component.
            """
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
            """Compare build metadata.

            Special rule: there is no ordering on build metadata.
            """
            if a == b:
                return 0
            else:
                return NotImplemented

        def make_optional(orig_cmp_fun):
            """Convert a cmp-like function to consider 'None == *'."""
            @functools.wraps(orig_cmp_fun)
            def alt_cmp_fun(a, b):
                if a is None or b is None:
                    return 0
                return orig_cmp_fun(a, b)

            return alt_cmp_fun

        if partial:
            return [
                base_cmp,  # Major is still mandatory
                make_optional(base_cmp),
                make_optional(base_cmp),
                prerelease_cmp,
                make_optional(build_cmp),
            ]
        else:
            return [
                base_cmp,
                base_cmp,
                base_cmp,
                prerelease_cmp,
                build_cmp,
            ]

    def __compare(self, other):
        comparison_functions = self._comparison_functions(partial=self.partial or other.partial)
        comparisons = zip(comparison_functions, self, other)

        for cmp_fun, self_field, other_field in comparisons:
            cmp_res = cmp_fun(self_field, other_field)
            if cmp_res != 0:
                return cmp_res

        return 0

    def __hash__(self):
        # We don't include 'partial', since this is strictly equivalent to having
        # at least a field being `None`.
        return hash((self.major, self.minor, self.patch, self.prerelease, self.build))

    def __cmp__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__compare(other)

    def __compare_helper(self, other, condition, notimpl_target):
        """Helper for comparison.

        Allows the caller to provide:
        - The condition
        - The return value if the comparison is meaningless (ie versions with
            build metadata).
        """
        if not isinstance(other, self.__class__):
            return NotImplemented

        cmp_res = self.__cmp__(other)
        if cmp_res is NotImplemented:
            return notimpl_target

        return condition(cmp_res)

    def __eq__(self, other):
        return self.__compare_helper(other, lambda x: x == 0, notimpl_target=False)

    def __ne__(self, other):
        return self.__compare_helper(other, lambda x: x != 0, notimpl_target=True)

    def __lt__(self, other):
        return self.__compare_helper(other, lambda x: x < 0, notimpl_target=False)

    def __le__(self, other):
        return self.__compare_helper(other, lambda x: x <= 0, notimpl_target=False)

    def __gt__(self, other):
        return self.__compare_helper(other, lambda x: x > 0, notimpl_target=False)

    def __ge__(self, other):
        return self.__compare_helper(other, lambda x: x >= 0, notimpl_target=False)


class SpecItem:
    """A requirement specification."""

    KIND_ANY = '*'
    KIND_LT = '<'
    KIND_LTE = '<='
    KIND_EQUAL = '=='
    KIND_SHORTEQ = '='
    KIND_EMPTY = ''
    KIND_GTE = '>='
    KIND_GT = '>'
    KIND_NEQ = '!='
    KIND_CARET = '^'
    KIND_TILDE = '~'
    KIND_COMPATIBLE = '~='

    # Map a kind alias to its full version
    KIND_ALIASES = {
        KIND_SHORTEQ: KIND_EQUAL,
        KIND_EMPTY: KIND_EQUAL,
    }

    re_spec = re.compile(r'^(<|<=||=|==|>=|>|!=|\^|~|~=)(\d.*)$')

    def __init__(self, requirement_string):
        kind, spec = self.parse(requirement_string)
        self.kind = kind
        self.spec = spec
        self._clause = Spec(requirement_string).clause

    @classmethod
    def parse(cls, requirement_string):
        if not requirement_string:
            raise ValueError("Invalid empty requirement specification: %r" % requirement_string)

        # Special case: the 'any' version spec.
        if requirement_string == '*':
            return (cls.KIND_ANY, '')

        match = cls.re_spec.match(requirement_string)
        if not match:
            raise ValueError("Invalid requirement specification: %r" % requirement_string)

        kind, version = match.groups()
        if kind in cls.KIND_ALIASES:
            kind = cls.KIND_ALIASES[kind]

        spec = Version(version, partial=True)
        if spec.build is not None and kind not in (cls.KIND_EQUAL, cls.KIND_NEQ):
            raise ValueError(
                "Invalid requirement specification %r: build numbers have no ordering."
                % requirement_string
            )
        return (kind, spec)

    @classmethod
    def from_matcher(cls, matcher):
        if matcher == Always():
            return cls('*')
        elif matcher == Never():
            return cls('<0.0.0-')
        elif isinstance(matcher, Range):
            return cls('%s%s' % (matcher.operator, matcher.target))

    def match(self, version):
        return self._clause.match(version)

    def __str__(self):
        return '%s%s' % (self.kind, self.spec)

    def __repr__(self):
        return '<SpecItem: %s %r>' % (self.kind, self.spec)

    def __eq__(self, other):
        if not isinstance(other, SpecItem):
            return NotImplemented
        return self.kind == other.kind and self.spec == other.spec

    def __hash__(self):
        return hash((self.kind, self.spec))


def compare(v1, v2):
    return base_cmp(Version(v1), Version(v2))


def match(spec, version):
    return Spec(spec).match(Version(version))


def validate(version_string):
    """Validates a version string againt the SemVer specification."""
    try:
        Version.parse(version_string)
        return True
    except ValueError:
        return False


DEFAULT_SYNTAX = 'simple'


class BaseSpec:
    """A specification of compatible versions.

    Usage:
    >>> Spec('>=1.0.0', syntax='npm')

    A version matches a specification if it matches any
    of the clauses of that specification.

    Internally, a Spec is AnyOf(
        AllOf(Matcher, Matcher, Matcher),
        AllOf(...),
    )
    """
    SYNTAXES = {}

    @classmethod
    def register_syntax(cls, subclass):
        syntax = subclass.SYNTAX
        if syntax is None:
            raise ValueError("A Spec needs its SYNTAX field to be set.")
        elif syntax in cls.SYNTAXES:
            raise ValueError(
                "Duplicate syntax for %s: %r, %r"
                % (syntax, cls.SYNTAXES[syntax], subclass)
            )
        cls.SYNTAXES[syntax] = subclass
        return subclass

    def __init__(self, expression):
        super().__init__()
        self.expression = expression
        self.clause = self._parse_to_clause(expression)

    @classmethod
    def parse(cls, expression, syntax=DEFAULT_SYNTAX):
        """Convert a syntax-specific expression into a BaseSpec instance."""
        return cls.SYNTAXES[syntax](expression)

    @classmethod
    def _parse_to_clause(cls, expression):
        """Converts an expression to a clause."""
        raise NotImplementedError()

    def filter(self, versions):
        """Filter an iterable of versions satisfying the Spec."""
        for version in versions:
            if self.match(version):
                yield version

    def match(self, version):
        """Check whether a Version satisfies the Spec."""
        return self.clause.match(version)

    def select(self, versions):
        """Select the best compatible version among an iterable of options."""
        options = list(self.filter(versions))
        if options:
            return max(options)
        return None

    def __contains__(self, version):
        if isinstance(version, Version):
            return self.match(version)
        return False

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.clause == other.clause

    def __hash__(self):
        return hash(self.clause)

    def __str__(self):
        return self.expression

    def __repr__(self):
        return '<%s: %r>' % (self.__class__.__name__, self.expression)


class Clause:
    __slots__ = []

    def match(self, version):
        raise NotImplementedError()

    def __and__(self, other):
        raise NotImplementedError()

    def __or__(self, other):
        raise NotImplementedError()

    def __eq__(self, other):
        raise NotImplementedError()

    def __ne__(self, other):
        return not self == other

    def simplify(self):
        return self


class AnyOf(Clause):
    __slots__ = ['clauses']

    def __init__(self, *clauses):
        super().__init__()
        self.clauses = frozenset(clauses)

    def match(self, version):
        return any(c.match(version) for c in self.clauses)

    def simplify(self):
        subclauses = set()
        for clause in self.clauses:
            simplified = clause.simplify()
            if isinstance(simplified, AnyOf):
                subclauses |= simplified.clauses
            elif simplified == Never():
                continue
            else:
                subclauses.add(simplified)
        if len(subclauses) == 1:
            return subclauses.pop()
        return AnyOf(*subclauses)

    def __hash__(self):
        return hash((AnyOf, self.clauses))

    def __iter__(self):
        return iter(self.clauses)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.clauses == other.clauses

    def __and__(self, other):
        if isinstance(other, AllOf):
            return other & self
        elif isinstance(other, Matcher) or isinstance(other, AnyOf):
            return AllOf(self, other)
        else:
            return NotImplemented

    def __or__(self, other):
        if isinstance(other, AnyOf):
            clauses = list(self.clauses | other.clauses)
        elif isinstance(other, Matcher) or isinstance(other, AllOf):
            clauses = list(self.clauses | set([other]))
        else:
            return NotImplemented
        return AnyOf(*clauses)

    def __repr__(self):
        return 'AnyOf(%s)' % ', '.join(sorted(repr(c) for c in self.clauses))


class AllOf(Clause):
    __slots__ = ['clauses']

    def __init__(self, *clauses):
        super().__init__()
        self.clauses = frozenset(clauses)

    def match(self, version):
        return all(clause.match(version) for clause in self.clauses)

    def simplify(self):
        subclauses = set()
        for clause in self.clauses:
            simplified = clause.simplify()
            if isinstance(simplified, AllOf):
                subclauses |= simplified.clauses
            elif simplified == Always():
                continue
            else:
                subclauses.add(simplified)
        if len(subclauses) == 1:
            return subclauses.pop()
        return AllOf(*subclauses)

    def __hash__(self):
        return hash((AllOf, self.clauses))

    def __iter__(self):
        return iter(self.clauses)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.clauses == other.clauses

    def __and__(self, other):
        if isinstance(other, Matcher) or isinstance(other, AnyOf):
            clauses = list(self.clauses | set([other]))
        elif isinstance(other, AllOf):
            clauses = list(self.clauses | other.clauses)
        else:
            return NotImplemented
        return AllOf(*clauses)

    def __or__(self, other):
        if isinstance(other, AnyOf):
            return other | self
        elif isinstance(other, Matcher):
            return AnyOf(self, AllOf(other))
        elif isinstance(other, AllOf):
            return AnyOf(self, other)
        else:
            return NotImplemented

    def __repr__(self):
        return 'AllOf(%s)' % ', '.join(sorted(repr(c) for c in self.clauses))


class Matcher(Clause):
    __slots__ = []

    def __and__(self, other):
        if isinstance(other, AllOf):
            return other & self
        elif isinstance(other, Matcher) or isinstance(other, AnyOf):
            return AllOf(self, other)
        else:
            return NotImplemented

    def __or__(self, other):
        if isinstance(other, AnyOf):
            return other | self
        elif isinstance(other, Matcher) or isinstance(other, AllOf):
            return AnyOf(self, other)
        else:
            return NotImplemented


class Never(Matcher):
    __slots__ = []

    def match(self, version):
        return False

    def __hash__(self):
        return hash((Never,))

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __and__(self, other):
        return self

    def __or__(self, other):
        return other

    def __repr__(self):
        return 'Never()'


class Always(Matcher):
    __slots__ = []

    def match(self, version):
        return True

    def __hash__(self):
        return hash((Always,))

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __and__(self, other):
        return other

    def __or__(self, other):
        return self

    def __repr__(self):
        return 'Always()'


class Range(Matcher):
    OP_EQ = '=='
    OP_GT = '>'
    OP_GTE = '>='
    OP_LT = '<'
    OP_LTE = '<='
    OP_NEQ = '!='

    # <1.2.3 matches 1.2.3-a1
    PRERELEASE_ALWAYS = 'always'
    # <1.2.3 does not match 1.2.3-a1
    PRERELEASE_NATURAL = 'natural'
    # 1.2.3-a1 is only considered if target == 1.2.3-xxx
    PRERELEASE_SAMEPATCH = 'same-patch'

    # 1.2.3 matches 1.2.3+*
    BUILD_IMPLICIT = 'implicit'
    # 1.2.3 matches only 1.2.3, not 1.2.3+4
    BUILD_STRICT = 'strict'

    __slots__ = ['operator', 'target', 'prerelease_policy', 'build_policy']

    def __init__(self, operator, target, prerelease_policy=PRERELEASE_NATURAL, build_policy=BUILD_IMPLICIT):
        super().__init__()
        if target.build and operator not in (self.OP_EQ, self.OP_NEQ):
            raise ValueError(
                "Invalid range %s%s: build numbers have no ordering."
                % (operator, target))
        self.operator = operator
        self.target = target
        self.prerelease_policy = prerelease_policy
        self.build_policy = self.BUILD_STRICT if target.build else build_policy

    def match(self, version):
        if self.build_policy != self.BUILD_STRICT:
            version = version.truncate('prerelease')

        if version.prerelease:
            same_patch = self.target.truncate() == version.truncate()

            if self.prerelease_policy == self.PRERELEASE_SAMEPATCH and not same_patch:
                return False

        if self.operator == self.OP_EQ:
            if self.build_policy == self.BUILD_STRICT:
                return (
                    self.target.truncate('prerelease') == version.truncate('prerelease')
                    and version.build == self.target.build
                )
            return version == self.target
        elif self.operator == self.OP_GT:
            return version > self.target
        elif self.operator == self.OP_GTE:
            return version >= self.target
        elif self.operator == self.OP_LT:
            if (
                version.prerelease
                and self.prerelease_policy == self.PRERELEASE_NATURAL
                and version.truncate() == self.target.truncate()
                and not self.target.prerelease
            ):
                return False
            return version < self.target
        elif self.operator == self.OP_LTE:
            return version <= self.target
        else:
            assert self.operator == self.OP_NEQ
            if self.build_policy == self.BUILD_STRICT:
                return not (
                    self.target.truncate('prerelease') == version.truncate('prerelease')
                    and version.build == self.target.build
                )

            if (
                version.prerelease
                and self.prerelease_policy == self.PRERELEASE_NATURAL
                and version.truncate() == self.target.truncate()
                and not self.target.prerelease
            ):
                return False
            return version != self.target

    def __hash__(self):
        return hash((Range, self.operator, self.target, self.prerelease_policy))

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.operator == other.operator
            and self.target == other.target
            and self.prerelease_policy == other.prerelease_policy
        )

    def __str__(self):
        return '%s%s' % (self.operator, self.target)

    def __repr__(self):
        policy_part = (
            '' if self.prerelease_policy == self.PRERELEASE_NATURAL
            else ', prerelease_policy=%r' % self.prerelease_policy
        ) + (
            '' if self.build_policy == self.BUILD_IMPLICIT
            else ', build_policy=%r' % self.build_policy
        )
        return 'Range(%r, %r%s)' % (
            self.operator,
            self.target,
            policy_part,
        )


@BaseSpec.register_syntax
class Spec(BaseSpec):

    SYNTAX = 'simple'

    def __init__(self, expression, *legacy_extras):
        expression = ','.join((expression,) + legacy_extras)
        super().__init__(expression)

    def __iter__(self):
        for clause in self.clause:
            yield SpecItem.from_matcher(clause)

    @classmethod
    def _parse_to_clause(cls, expression):
        return cls.Parser.parse(expression)

    class Parser:
        NUMBER = r'\*|0|[1-9][0-9]*'
        NAIVE_SPEC = re.compile(r"""^
            (?P<op><|<=||=|==|>=|>|!=|\^|~|~=)
            (?P<major>{nb})(?:\.(?P<minor>{nb})(?:\.(?P<patch>{nb}))?)?
            (?:-(?P<prerel>[a-z0-9A-Z.-]*))?
            (?:\+(?P<build>[a-z0-9A-Z.-]*))?
            $
            """.format(nb=NUMBER),
            re.VERBOSE,
        )

        @classmethod
        def parse(cls, expression):
            blocks = expression.split(',')
            clause = Always()
            for block in blocks:
                if not cls.NAIVE_SPEC.match(block):
                    raise ValueError("Invalid simple block %r" % block)
                clause &= cls.parse_block(block)

            return clause

        PREFIX_CARET = '^'
        PREFIX_TILDE = '~'
        PREFIX_COMPATIBLE = '~='
        PREFIX_EQ = '=='
        PREFIX_NEQ = '!='
        PREFIX_GT = '>'
        PREFIX_GTE = '>='
        PREFIX_LT = '<'
        PREFIX_LTE = '<='

        PREFIX_ALIASES = {
            '=': PREFIX_EQ,
            '': PREFIX_EQ,
        }

        EMPTY_VALUES = ['*', 'x', 'X', None]

        @classmethod
        def parse_block(cls, expr):
            if not cls.NAIVE_SPEC.match(expr):
                raise ValueError("Invalid simple spec component: %r" % expr)
            prefix, major_t, minor_t, patch_t, prerel, build = cls.NAIVE_SPEC.match(expr).groups()
            prefix = cls.PREFIX_ALIASES.get(prefix, prefix)

            major = None if major_t in cls.EMPTY_VALUES else int(major_t)
            minor = None if minor_t in cls.EMPTY_VALUES else int(minor_t)
            patch = None if patch_t in cls.EMPTY_VALUES else int(patch_t)

            if major is None:  # '*'
                target = Version(major=0, minor=0, patch=0)
                if prefix not in (cls.PREFIX_EQ, cls.PREFIX_GTE):
                    raise ValueError("Invalid simple spec: %r" % expr)
            elif minor is None:
                target = Version(major=major, minor=0, patch=0)
            elif patch is None:
                target = Version(major=major, minor=minor, patch=0)
            else:
                target = Version(
                    major=major,
                    minor=minor,
                    patch=patch,
                    prerelease=prerel.split('.') if prerel else (),
                    build=build.split('.') if build else (),
                )

            if (major is None or minor is None or patch is None) and (prerel or build):
                raise ValueError("Invalid simple spec: %r" % expr)

            if build is not None and prefix not in (cls.PREFIX_EQ, cls.PREFIX_NEQ):
                raise ValueError("Invalid simple spec: %r" % expr)

            if prefix == cls.PREFIX_CARET:
                # Accept anything with the same most-significant digit
                if target.major:
                    high = target.next_major()
                elif target.minor:
                    high = target.next_minor()
                else:
                    high = target.next_patch()
                return Range(Range.OP_GTE, target) & Range(Range.OP_LT, high)

            elif prefix == cls.PREFIX_TILDE:
                assert major is not None
                # Accept any higher patch in the same minor
                # Might go higher if the initial version was a partial
                if minor is None:
                    high = target.next_major()
                else:
                    high = target.next_minor()
                return Range(Range.OP_GTE, target) & Range(Range.OP_LT, high)

            elif prefix == cls.PREFIX_COMPATIBLE:
                assert major is not None
                # ~1 is 1.0.0..2.0.0; ~=2.2 is 2.2.0..3.0.0; ~=1.4.5 is 1.4.5..1.5.0
                if minor is None or patch is None:
                    # We got a partial version
                    high = target.next_major()
                else:
                    high = target.next_minor()
                return Range(Range.OP_GTE, target) & Range(Range.OP_LT, high)

            elif prefix == cls.PREFIX_EQ:
                if major is None:
                    return Range(Range.OP_GTE, target)
                elif minor is None:
                    return Range(Range.OP_GTE, target) & Range(Range.OP_LT, target.next_major())
                elif patch is None:
                    return Range(Range.OP_GTE, target) & Range(Range.OP_LT, target.next_patch())
                elif build == '':
                    return Range(Range.OP_EQ, target, build_policy=Range.BUILD_STRICT)
                else:
                    return Range(Range.OP_EQ, target)

            elif prefix == cls.PREFIX_NEQ:
                assert major is not None
                if minor is None:
                    # !=1.x => <1.0.0 || >=2.0.0
                    return Range(Range.OP_LT, target) | Range(Range.OP_GTE, target.next_major())
                elif patch is None:
                    # !=1.2.x => <1.2.0 || >=1.3.0
                    return Range(Range.OP_LT, target) | Range(Range.OP_GTE, target.next_minor())
                elif prerel == '':
                    # !=1.2.3-
                    return Range(Range.OP_NEQ, target, prerelease_policy=Range.PRERELEASE_ALWAYS)
                elif build == '':
                    # !=1.2.3+ or !=1.2.3-a2+
                    return Range(Range.OP_NEQ, target, build_policy=Range.BUILD_STRICT)
                else:
                    return Range(Range.OP_NEQ, target)

            elif prefix == cls.PREFIX_GT:
                assert major is not None
                if minor is None:
                    # >1.x => >=2.0
                    return Range(Range.OP_GTE, target.next_major())
                elif patch is None:
                    return Range(Range.OP_GTE, target.next_minor())
                else:
                    return Range(Range.OP_GT, target)

            elif prefix == cls.PREFIX_GTE:
                return Range(Range.OP_GTE, target)

            elif prefix == cls.PREFIX_LT:
                assert major is not None
                if prerel == '':
                    # <1.2.3-
                    return Range(Range.OP_LT, target, prerelease_policy=Range.PRERELEASE_ALWAYS)
                return Range(Range.OP_LT, target)

            else:
                assert prefix == cls.PREFIX_LTE
                assert major is not None
                if minor is None:
                    # <=1.x => <2.0
                    return Range(Range.OP_LT, target.next_major())
                elif patch is None:
                    return Range(Range.OP_LT, target.next_minor())
                else:
                    return Range(Range.OP_LTE, target)






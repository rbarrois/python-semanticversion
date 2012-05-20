Reference
=========


.. module:: semantic_version


Module-level functions
----------------------

.. function:: compare(v1, v2)

    Compare two version strings, and return a result similar to that of :func:`cmp`::

        >>> compare('0.1.1', '0.1.2')
        -1
        >>> compare('0.1.1', '0.1.1')
        0
        >>> compare('0.1.1', '0.1.1-alpha')
        1

    :param str v1: The first version to compare
    :param str v2: The second version to compare
    :raises: :exc:`ValueError`, if any version string is invalid
    :rtype: ``int``, -1 / 0 / 1 as for a :func:`cmp` comparison



.. function:: match(spec, version)

    Check whether a version string matches a specification string::

        >>> match('>=0.1.1', '0.1.2')
        True
        >>> match('>=0.1.1', '0.1.1-alpha')
        False
        >>> match('~0.1.1', '0.1.1-alpha')
        True

    :param str spec: The specification to use, as a string
    :param str version: The version string to test against the spec
    :raises: :exc:`ValueError`, if the ``spec`` or the ``version`` is invalid
    :rtype: ``bool``


Representing a version (the Version class)
------------------------------------------

.. class:: Version(version_string[, partial=False])

    Object representation of a `SemVer`_-compliant version.

    Constructed from a textual version string::

        >>> Version('1.1.1')
        <SemVer(1, 1, 1, [], [])>
        >>> str(Version('1.1.1'))
        '1.1.1'


    .. rubric:: Attributes


    .. attribute:: partial

        ``bool``, whether this is a 'partial' or a complete version number.
        Partial version number may lack :attr:`minor` or :attr:`patch` version numbers.

    .. attribute:: major

        ``int``, the major version number

    .. attribute:: minor

        ``int``, the minor version number.

        May be ``None`` for a :attr:`partial` version number in a ``<major>`` format.

    .. attribute:: patch

        ``int``, the patch version number.

        May be ``None`` for a :attr:`partial` version number in a ``<major>`` or ``<major>.<minor>`` format.

    .. attribute:: prerelease

        ``tuple`` of ``strings``, the prerelease component.

        It contains the various dot-separated identifiers in the prerelease component.

        May be ``None`` for a :attr:`partial` version number in a ``<major>``, ``<major>.<minor>`` or ``<major>.<minor>.<patch>`` format.

    .. attribute:: build

        ``tuple`` of ``strings``, the build component.

        It contains the various dot-separated identifiers in the build component.

        May be ``None`` for a :attr:`partial` version number in a ``<major>``, ``<major>.<minor>``,
        ``<major>.<minor>.<patch>`` or ``<major>.<minor>.<patch>-<prerelease>`` format.


    .. rubric:: Methods


    .. method:: __iter__(self)

        Iterates over the version components (:attr:`major`, :attr:`minor`,
        :attr:`patch`, :attr:`prerelease`, :attr:`build`)::

            >>> list(Version('0.1.1'))
            [0, 1, 1, [], []]

        .. note:: This may pose some subtle bugs when iterating over a single version
                  while expecting an iterable of versions -- similar to::

                      >>> list('abc')
                      ['a', 'b', 'c']
                      >>> list(('abc',))
                      ['abc']


    .. method:: __cmp__(self, other)

        Provides comparison methods with other :class:`Version` objects.

        The rules are:

        - For non-:attr:`partial` versions, compare using the `SemVer`_ scheme
        - If any compared object is :attr:`partial`:
            - Begin comparison using the `SemVer`_ scheme
            - If a component (:attr:`minor`, :attr:`patch`, :attr:`prerelease` or :attr:`build`)
              was absent from the :attr:`partial` :class:`Version` -- represented with :obj:`None`
              --, consider both versions equal.

            For instance, ``Version('1.0', partial=True)`` means "any version beginning in ``1.0``".

            ``Version('1.0.1-alpha', partial=True)`` means "The ``1.0.1-alpha`` version or any
            ulterior build of that same version": ``1.0.1-alpha+build3`` matches, ``1.0.1-alpha.2`` doesn't.

        Examples::

              >>> Version('1.0', partial=True) == Version('1.0.1')
              True
              >>> Version('1.0.1-rc1.1') == Version('1.0.1-rc1', partial=True)
              False
              >>> Version('1.0.1-rc1+build345') == Version('1.0.1-rc1')
              False
              >>> Version('1.0.1-rc1+build345') == Version('1.0.1-rc1', partial=True)
              True


    .. method:: __str__(self)

        Returns the standard text representation of the version::

            >>> v = Version('0.1.1-rc2+build4.4')
            >>> v
            <SemVer(0, 1, 1, ['rc2'], ['build4', '4'])>
            >>> str(v)
            '0.1.1-rc2+build4.4'


    .. method:: __hash__(self)

        Provides a hash based solely on the components.

        Allows using a :class:`Version` as a dictionary key.

        .. note:: A fully qualified :attr:`partial` :class:`Version`

                  (up to the :attr:`build` component) will hash the same as the
                  equally qualified, non-:attr:`partial` :class:`Version`::

                      >>> hash(Version('1.0.1+build4')) == hash(Version('1.0.1+build4', partial=True))
                      True


    .. rubric:: Class methods


    .. classmethod:: parse(cls, version_string[, partial=False])

        Parse a version string into a ``(major, minor, patch, prerelease, build)`` tuple.

        :param str version_string: The version string to parse
        :param bool partial: Whether this should be considered a :attr:`partial` version
        :raises: :exc:`ValueError`, if the :attr:`version_string` is invalid.
        :rtype: (major, minor, patch, prerelease, build)


Version specifications (the Spec class)
---------------------------------------


Version specifications describe a 'range' of accepted versions:
older than, equal, similar to, …

The main issue with representing version specifications is that the usual syntax
does not map well onto `SemVer`_ precedence rules:

* A specification of ``<1.3.4`` is not expected to allow ``1.3.4-rc2``, but strict `SemVer`_ comparisons allow it ;
* Converting the previous specification to ``<=1.3.3`` in order to avoid ``1.3.4``
  prereleases has the issue of excluding ``1.3.3+build3`` ;
* It may be necessary to exclude either all variations on a patch-level release
  (``!=1.3.3``) or specifically one build-level release (``1.3.3-build.434``).


In order to have version specification behave naturally, the rules are the following:

* If no pre-release number was included in the specification, pre-release numbers
  are ignored when deciding whether a version satisfies a specification.
* If no build number was included in the specification, build numbers are ignored
  when deciding whether a version satisfies a specification.

This means that::

    >>> Version('1.1.1-rc1') in Spec('<1.1.1')
    False
    >>> Version('1.1.1-rc1') in Spec('<1.1.1-rc4')
    True
    >>> Version('1.1.1-rc1+build4') in Spec('<=1.1.1-rc1')
    True
    >>> Version('1.1.1-rc1+build4') in Spec('<=1.1.1-rc1+build2')
    False

In order to force matches to *strictly* compare version numbers, these additional
rules apply:

* Setting a pre-release separator without a pre-release identifier (``<=1.1.1-``)
  forces match to take into account pre-release version::

    >>> Version('1.1.1-rc1') in Spec('<1.1.1')
    False
    >>> Version('1.1.1-rc1') in Spec('<1.1.1-')
    True

* Setting a build separator without a build identifier (``>1.1.1+``) forces
  satisfaction tests to include build identifiers::

    >>> Version('1.1.1+build2') in Spec('>1.1.1')
    False
    >>> Version('1.1.1+build2') in Spec('>1.1.1+')
    True

* Including both pre-release and build separators while omitting identifiers is
  strictly equivalent to including only the build separator::

    >>> Spec('>1.1.1-+') == Spec('>1.1.1+')
    True

.. class:: Spec(spec_string)

    Stores a version specification, defined from a string::

        >>> Spec('>=0.1.1')
        <Spec: >= <SemVer(0, 1, 1, [], [])>>

    This allows to test :class:`Version` objects against the :class:`Spec`::

        >>> Spec('>=0.1.1').match(Version('0.1.1-rc1'))  # pre-release have lower precedence
        False
        >>> Version('0.1.1+build2') in Spec('>=0.1.1')   # build version have higher precedence
        True


    .. rubric:: Attributes


    .. attribute:: kind

        One of :data:`KIND_LT`, :data:`KIND_LTE`, :data:`KIND_EQUAL`, :data:`KIND_GTE`,
        :data:`KIND_GT`, :data:`KIND_NEQ`, :data:`KIND_LTE_LOOSE`, :data:`KIND_EQ_LOOSE`,
        :data:`KIND_GTE_LOOSE`, :data:`KIND_NEQ_LOOSE`.

    .. attribute:: spec

        :class:`Version` in the :class:`Spec` description.

        If :attr:`kind` is a ``_LOOSE`` kind, this will be a :attr:`~Version.partial` :class:`Version`.


    .. rubric:: Class methods


    .. classmethod:: parse(cls, requirement_string)

        Retrieve a ``(kind, version)`` tuple from a string.

        :param str requirement_string: The textual description of the specification
        :raises: :exc:`ValueError`: if the ``requirement_string`` is invalid.
        :rtype: (``kind``, ``version``) tuple


    .. rubric:: Methods


    .. method:: match(self, version)

        Test whether a given :class:`Version` matches this :class:`Spec`::

            >>> Spec('>0.1.1').match(Version('0.1.1-alpha'))
            False

        :param version: The version to test against the spec
        :type version: :class:`Version`
        :rtype: ``bool``


    .. method:: __contains__(self, version)

        Alias of the :func:`match` method;
        allows the use of the ``version in spec`` syntax::

            >>> Version('1.1.1') in Spec('<=1.1.2')
            True


    .. method:: __str__(self)

        Converting a :class:`Spec` to a string returns the initial description string::

            >>> str(Spec('>=0.1.1'))
            '>=0.1.1'


    .. method:: __hash__(self)

        Provides a hash based solely on the current kind and the specified version.

        Allows using a :class:`Spec` as a dictionary key.


    .. rubric:: Class attributes


    .. data:: KIND_LT

        The kind of 'Less than' specifications::

            >>> Version('1.0.0-alpha') in Spec('<1.0.0')
            True

    .. data:: KIND_LTE

        The kind of 'Less or equal to' specifications::

            >>> Version('1.0.0-alpha1+build999') in Spec('<=1.0.0-alpha1')
            False

    .. data:: KIND_EQUAL

        The kind of 'equal to' specifications::

            >>> Version('1.0.0+build3.3') in Spec('==1.0.0')
            False

    .. data:: KIND_GTE

        The kind of 'Greater or equal to' specifications::

            >>> Version('1.0.0') in Spec('>=1.0.0')
            True

    .. data:: KIND_GT

        The kind of 'Greater than' specifications::

            >>> Version('1.0.0+build667') in Spec('>1.0.1')
            True

    .. data:: KIND_NEQ

        The kind of 'Not equal to' specifications::

            >>> Version('1.0.1') in Spec('!=1.0.1')
            False

        The kind of 'Almost equal to' specifications


    .. data:: KIND_LTE_LOOSE

        The kind of 'Loosely lesser or equal to' specifications::

            >>> Version('1.0.1-alpha+build99') in Spec('<=1.0.1-alpha')
            False
            >>> Version('1.0.1-alpha+build99') in Spec('<~1.0.1-alpha')
            True

    .. data:: KIND_EQ_LOOSE

        The kind of 'Almost equal to' specifications::

            >>> Version('1.0.1-alpha') in Spec('~=1.0.1')
            True

    .. data:: KIND_GTE_LOOSE

        The kind of 'Loosely greater or equal to' specifications::

            >>> Version('1.0.1-alpha') in Spec('>=1.0.1')
            False
            >>> Version('1.0.1-alpha') in Spec('>~1.0.1')
            True

    .. data:: KIND_NEQ_LOOSE

        The kind of 'Loosely not equal to' specifications::

            >>> Version('1.0.1-alpha') not in Spec('!=1.0.1')
            False
            >>> Version('1.0.1-alpha') not in Spec('!~1.0.1')
            True


Combining version specifications (the SpecList class)
-----------------------------------------------------

It may be useful to define a rule such as
"Accept any version between the first 1.0.0 (incl. pre-release) and strictly before 1.2.0; ecluding 1.1.4 which was broken.".

This is possible with the :class:`SpecList` class.


.. class:: SpecList(spec_string[, spec_string[, ...]])

    Stores a list of :class:`Spec` and matches any :class:`Version` against all
    contained :class:`specs <Spec>`.

    It is build from a comma-separated list of version specifications::

        >>> SpecList('>~1.0.0,<1.2.0,!~1.1.4')
        <SpecList: (
            <Spec: >~ <~SemVer: 1 0 0 None None>>,
            <Spec: < <SemVer: 1 2 0 [] []>>,
            <Spec: !~ <~SemVer: 1 1 4 None None>>
        )>

    Version specifications may also be passed in separated arguments::

        >>> SpecList('>~1.0.0', '<1.2.0', '!~1.1.4,!~1.1.13')
        <SpecList: (
            <Spec: >~ <~SemVer: 1 0 0 None None>>,
            <Spec: < <SemVer: 1 2 0 [] []>>,
            <Spec: !~ <~SemVer: 1 1 4 None None>>
            <Spec: !~ <~SemVer: 1 1 13 None None>>
        )>


    .. rubric:: Attributes


    .. attribute:: specs

        Tuple of :class:`Spec`, the included specifications.


    .. rubric:: Methods


    .. method:: match(self, version)

        Test whether a given :class:`Version` matches all included :class:`Spec`::

            >>> SpecList('>=1.1.0,<1.1.2').match(Version('1.1.1'))
            True

        :param version: The version to test against the specs
        :type version: :class:`Version`
        :rtype: ``bool``

    .. method:: __contains__(self, version)

        Alias of the :func:`match` method;
        allows the use of the ``version in speclist`` syntax::

            >>> Version('1.1.1-alpha') in SpecList('>=1.1.0,<1.1.1')
            True


    .. method:: __str__(self)

        Converting a :class:`SpecList` returns the initial description string::

            >>> str(SpecList('>=0.1.1,!=0.1.2'))
            '>=0.1.1,!=0.1.2'

    .. method:: __iter__(self)

        Returns an iterator over the contained specs::

            >>> for spec in SpecList('>=0.1.1,!=0.1.2'):
            ...     print spec
            >=0.1.1
            !=0.1.2

    .. method:: __hash__(self)

        Provides a hash based solely on the hash of contained specs.

        Allows using a :class:`SpecList` as a dictionary key.


    .. rubric:: Class methods


    .. classmethod:: parse(self, specs_string)

        Retrieve a ``(*specs)`` tuple from a string.

        :param str requirement_string: The textual description of the specifications
        :raises: :exc:`ValueError`: if the ``requirement_string`` is invalid.
        :rtype: ``(*spec)`` tuple


.. _SemVer: http://semver.org/

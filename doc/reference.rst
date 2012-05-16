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


Representing a version
----------------------

.. class:: Version

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

        ``list`` of ``strings``, the prerelease component.

        It contains the various dot-separated identifiers in the prerelease component.

        May be ``None`` for a :attr:`partial` version number in a ``<major>``, ``<major>.<minor>`` or ``<major>.<minor>.<patch>`` format.

    .. attribute:: build

        ``list`` of ``strings``, the build component.

        It contains the various dot-separated identifiers in the build component.

        May be ``None`` for a :attr:`partial` version number in a ``<major>``, ``<major>.<minor>``,
        ``<major>.<minor>.<patch>`` or ``<major>.<minor>.<patch>-<prerelease>`` format.


    .. rubric:: Methods


    .. method:: __iter__(self)

        Iterates over the version components (:attr:`major`, :attr:`minor`,
        :attr:`patch`, :attr:`prerelease`, :attr:`build`).

    .. method:: __cmp__(self, other)

        Provides comparison methods with other :class:`Version` objects.

        The rules are:

        - For non-:attr:`partial` versions, compare using the `SemVer`_ scheme
        - If any compared object is :attr:`partial`, compare using the `SemVer`_ scheme,
          but stop at the first component undefined in the :attr:`partial` :class:`Version`;
          that is, a component whose value is ``None``.


    .. method:: __str__(self)

        Returns the standard text representation of the version.

        .. code-block:: pycon

            >>> v = Version('0.1.1-rc2+build4.4')
            >>> v
            <SemVer(0, 1, 1, ['rc2'], ['build4', '4'])>
            >>> str(v)
            '0.1.1-rc2+build4.4'


    .. rubric:: Class methods


    .. classmethod:: parse(cls, version_string[, partial=False])

        Parse a version string into a ``(major, minor, patch, prerelease, build)`` tuple.

        :param str version_string: The version string to parse
        :param bool partial: Whether this should be considered a :attr:`partial` version
        :raises: :exc:`ValueError`, if the :attr:`version_string` is invalid.
        :rtype: (major, minor, patch, prerelease, build)


Version specifications
----------------------


Version specifications describe a 'range' of accepted versions:
older than, equal, similar to, …

.. class:: Spec

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
        :data:`KIND_GT`, :data:`KIND_ALMOST`.

    .. attribute:: spec

        :class:`Version` in the :class:`Spec` description.

        If :attr:`kind` is :data:`KIND_ALMOST`, this will be a :attr:`~Version.partial` :class:`Version`.


    .. rubric:: Class methods


    .. classmethod:: parse(cls, requirement_string)

        Retrieve a ``(kind, version)`` tuple from a string.

        :param str requirement_string: The textual description of the specification
        :raises: :exc:`ValueError`: if the ``requirement_string`` is invalid.
        :rtype: (``kind``, ``version``) tuple


    .. rubric:: Methods


    .. method:: match(self, version)

        Test whether a given :class:`Version` matches this :class:`Spec`.

        :param version: The version to test against the spec
        :type version: :class:`Version`
        :rtype: ``bool``


    .. method:: __contains__(self, version)

        Allows the use of the ``version in spec`` syntax.
        Simply an alias of the :func:`match` method.


    .. rubric:: Class attributes


    .. data:: KIND_LT

        The kind of 'Less than' specifications

    .. data:: KIND_LTE

        The kind of 'Less or equal to' specifications

    .. data:: KIND_EQUAL

        The kind of 'equal to' specifications

    .. data:: KIND_GTE

        The kind of 'Greater or equal to' specifications

    .. data:: KIND_GT

        The kind of 'Greater than' specifications

    .. data:: KIND_ALMOST

        The kind of 'Almost equal to' specifications


.. _SemVer: http://semver.org/

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
    :rtype: ``int``, -1 / 0 / 1 as for a :func:`cmp` comparison;
            ``NotImplemented`` if versions only differ by build metadata


.. warning:: Since build metadata has no ordering,
             ``compare(Version('0.1.1'), Version('0.1.1+3'))`` returns ``NotImplemented``


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


.. function:: validate(version)

    Check whether a version string complies with the `SemVer`_ rules.

    .. code-block:: pycon

        >>> semantic_version.validate('1.1.1')
        True
        >>> semantic_version.validate('1.2.3a4')
        False

    :param str version: The version string to validate
    :rtype: ``bool``


Representing a version (the Version class)
------------------------------------------

.. class:: Version(version_string[, partial=False])

    Object representation of a `SemVer`_-compliant version.

    Constructed from a textual version string::

        >>> Version('1.1.1')
        Version('1.1.1')
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

        ``tuple`` of ``strings``, the build metadata.

        It contains the various dot-separated identifiers in the build metadata.

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
            any release differing only in build metadata": ``1.0.1-alpha+build3`` matches, ``1.0.1-alpha.2`` doesn't.

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
            Version('0.1.1-rc2+build4.4')
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

    .. classmethod:: coerce(cls, version_string[, partial=False])

        Try to convert an arbitrary version string into a :class:`Version` instance.

        Rules are:

        - If no minor or patch component, and :attr:`partial` is :obj:`False`,
          replace them with zeroes
        - Any character outside of ``a-zA-Z0-9.+-`` is replaced with a ``-``
        - If more than 3 dot-separated numerical components, everything from the
          fourth component belongs to the :attr:`build` part
        - Any extra ``+`` in the :attr:`build` part will be replaced with dots

        Examples:

        .. code-block:: pycon

          >>> Version.coerce('02')
          Version('2.0.0')
          >>> Version.coerce('1.2.3.4')
          Version('1.2.3+4')
          >>> Version.coerce('1.2.3.4beta2')
          Version('1.2.3+4beta2')
          >>> Version.coerce('1.2.3.4.5_6/7+8+9+10')
          Version('1.2.3+4.5-6-7.8.9.10')

        :param str version_string: The version string to coerce
        :param bool partial: Whether to allow generating a :attr:`partial` version
        :raises: :exc:`ValueError`, if the :attr:`version_string` is invalid.
        :rtype: :class:`Version`


Version specifications (the Spec class)
---------------------------------------


Version specifications describe a 'range' of accepted versions:
older than, equal, similar to, …

The main issue with representing version specifications is that the usual syntax
does not map well onto `SemVer`_ precedence rules:

* A specification of ``<1.3.4`` is not expected to allow ``1.3.4-rc2``, but strict `SemVer`_ comparisons allow it ;
  prereleases has the issue of excluding ``1.3.3+build3`` ;
* It may be necessary to exclude either all variations on a patch-level release
  (``!=1.3.3``) or specifically one build-level release (``1.3.3-build.434``).


In order to have version specification behave naturally, the rules are the following:

* If no pre-release number was included in the specification, pre-release numbers
  are ignored when deciding whether a version satisfies a specification.
* If no build metadata was included in the specification, build metadata is ignored
  when deciding whether a version satisfies a specification.

This means that::

    >>> Version('1.1.1-rc1') in Spec('<1.1.1')
    False
    >>> Version('1.1.1-rc1') in Spec('<1.1.1-rc4')
    True
    >>> Version('1.1.1-rc1+build4') in Spec('<=1.1.1-rc1')
    True
    >>> Version('1.1.1-rc1+build4') in Spec('==1.1.1-rc1+build2')
    False


.. note:: python-semanticversion also accepts ``"*"`` as a version spec,
          that matches all (valid) version strings.

.. note:: python-semanticversion includes support for NPM-style specs:

          * ``~1.2.3`` means "Any release between 1.2.3 and 1.3.0"
          * ``^1.3.4`` means "Any release between 1.3.4 and 2.0.0"

In order to force matches to *strictly* compare version numbers, these additional
rules apply:

* Setting a pre-release separator without a pre-release identifier (``<=1.1.1-``)
  forces match to take into account pre-release version::

    >>> Version('1.1.1-rc1') in Spec('<1.1.1')
    False
    >>> Version('1.1.1-rc1') in Spec('<1.1.1-')
    True

* Setting a build metadata separator without build metadata (``<=1.1.1+``)
  forces matches "up to the build metadata"; use this to include/exclude a
  release lacking build metadata while excluding/including all other builds
  of that release

    >>> Version('1.1.1') in Spec('==1.1.1+')
    True
    >>> Version('1.1.1+2') in Spec('==1.1.1+')
    False


.. warning:: As stated in the `SemVer`_ specification, the ordering of build metadata is *undefined*.
             Thus, a :class:`Spec` string can only mention build metadata to include or exclude a specific version:

             * ``==1.1.1+b1234`` includes this specific build
             * ``!=1.1.1+b1234`` excludes it (but would match ``1.1.1+b1235``
             * ``<1.1.1+b1`` is invalid



.. class:: Spec(spec_string[, spec_string[, ...]])

    Stores a list of :class:`SpecItem` and matches any :class:`Version` against all
    contained :class:`specs <SpecItem>`.

    It is built from a comma-separated list of version specifications::

        >>> Spec('>=1.0.0,<1.2.0,!=1.1.4')
        <Spec: (
            <SpecItem: >= Version('1.0.0', partial=True)>,
            <SpecItem: < Version('1.2.0', partial=True)>,
            <SpecItem: != Version('1.1.4', partial=True)>
        )>

    Version specifications may also be passed in separated arguments::

        >>> Spec('>=1.0.0', '<1.2.0', '!=1.1.4,!=1.1.13')
        <Spec: (
            <SpecItem: >= Version('1.0.0', partial=True)>,
            <SpecItem: < Version('1.2.0', partial=True)>,
            <SpecItem: != Version('1.1.4', partial=True)>,
            <SpecItem: != Version('1.1.13', partial=True)>,
        )>


    .. rubric:: Attributes


    .. attribute:: specs

        Tuple of :class:`SpecItem`, the included specifications.


    .. rubric:: Methods


    .. method:: match(self, version)

        Test whether a given :class:`Version` matches all included :class:`SpecItem`::

            >>> Spec('>=1.1.0,<1.1.2').match(Version('1.1.1'))
            True

        :param version: The version to test against the specs
        :type version: :class:`Version`
        :rtype: ``bool``


    .. method:: filter(self, versions)

        Extract all compatible :class:`versions <Version>` from an iterable of
        :class:`Version` objects.

        :param versions: The versions to filter
        :type versions: iterable of :class:`Version`
        :yield: :class:`Version`


    .. method:: select(self, versions)

        Select the highest compatible version from an iterable of :class:`Version`
        objects.

        .. sourcecode:: pycon

            >>> s = Spec('>=0.1.0')
            >>> s.select([])
            None
            >>> s.select([Version('0.1.0'), Version('0.1.3'), Version('0.1.1')])
            Version('0.1.3')

        :param versions: The versions to filter
        :type versions: iterable of :class:`Version`
        :rtype: The highest compatible :class:`Version` if at least one of the
                given versions is compatible; :class:`None` otherwise.


    .. method:: __contains__(self, version)

        Alias of the :func:`match` method;
        allows the use of the ``version in speclist`` syntax::

            >>> Version('1.1.1-alpha') in Spec('>=1.1.0,<1.1.1')
            True


    .. method:: __str__(self)

        Converting a :class:`Spec` returns the initial description string::

            >>> str(Spec('>=0.1.1,!=0.1.2'))
            '>=0.1.1,!=0.1.2'

    .. method:: __iter__(self)

        Returns an iterator over the contained specs::

            >>> for spec in Spec('>=0.1.1,!=0.1.2'):
            ...     print spec
            >=0.1.1
            !=0.1.2

    .. method:: __hash__(self)

        Provides a hash based solely on the hash of contained specs.

        Allows using a :class:`Spec` as a dictionary key.


    .. rubric:: Class methods


    .. classmethod:: parse(self, specs_string)

        Retrieve a ``(*specs)`` tuple from a string.

        :param str requirement_string: The textual description of the specifications
        :raises: :exc:`ValueError`: if the ``requirement_string`` is invalid.
        :rtype: ``(*spec)`` tuple


.. class:: SpecItem(spec_string)

    .. note:: This class belong to the private python-semanticversion API.

    Stores a version specification, defined from a string::

        >>> SpecItem('>=0.1.1')
        <SpecItem: >= Version('0.1.1', partial=True)>

    This allows to test :class:`Version` objects against the :class:`SpecItem`::

        >>> SpecItem('>=0.1.1').match(Version('0.1.1-rc1'))  # pre-release satisfy conditions
        True
        >>> Version('0.1.1+build2') in SpecItem('>=0.1.1')   # build metadata is ignored when checking for precedence
        True
        >>>
        >>> # Use the '-' marker to include the pre-release component in checks
        >>> SpecItem('>=0.1.1-').match(Version('0.1.1-rc1')
        False
        >>> # Use the '+' marker to include the build metadata in checks
        >>> SpecItem('==0.1.1+').match(Version('0.1.1+b1234')
        False
        >>>


    .. rubric:: Attributes


    .. attribute:: kind

        One of :data:`KIND_LT`, :data:`KIND_LTE`, :data:`KIND_EQUAL`, :data:`KIND_GTE`,
        :data:`KIND_GT` and :data:`KIND_NEQ`.

    .. attribute:: spec

        :class:`Version` in the :class:`SpecItem` description.

        It is alway a :attr:`~Version.partial` :class:`Version`.


    .. rubric:: Class methods


    .. classmethod:: parse(cls, requirement_string)

        Retrieve a ``(kind, version)`` tuple from a string.

        :param str requirement_string: The textual description of the specification
        :raises: :exc:`ValueError`: if the ``requirement_string`` is invalid.
        :rtype: (``kind``, ``version``) tuple


    .. rubric:: Methods


    .. method:: match(self, version)

        Test whether a given :class:`Version` matches this :class:`SpecItem`::

            >>> SpecItem('>=0.1.1').match(Version('0.1.1-alpha'))
            True
            >>> SpecItem('>=0.1.1-').match(Version('0.1.1-alpha'))
            False

        :param version: The version to test against the spec
        :type version: :class:`Version`
        :rtype: ``bool``


    .. method:: __str__(self)

        Converting a :class:`SpecItem` to a string returns the initial description string::

            >>> str(SpecItem('>=0.1.1'))
            '>=0.1.1'


    .. method:: __hash__(self)

        Provides a hash based solely on the current kind and the specified version.

        Allows using a :class:`SpecItem` as a dictionary key.


    .. rubric:: Class attributes


    .. data:: KIND_LT

        The kind of 'Less than' specifications::

            >>> Version('1.0.0-alpha') in Spec('<1.0.0')
            False

    .. data:: KIND_LTE

        The kind of 'Less or equal to' specifications::

            >>> Version('1.0.0-alpha1+build999') in Spec('<=1.0.0-alpha1')
            True

    .. data:: KIND_EQUAL

        The kind of 'equal to' specifications::

            >>> Version('1.0.0+build3.3') in Spec('==1.0.0')
            True

    .. data:: KIND_GTE

        The kind of 'Greater or equal to' specifications::

            >>> Version('1.0.0') in Spec('>=1.0.0')
            True

    .. data:: KIND_GT

        The kind of 'Greater than' specifications::

            >>> Version('1.0.0+build667') in Spec('>1.0.1')
            False

    .. data:: KIND_NEQ

        The kind of 'Not equal to' specifications::

            >>> Version('1.0.1') in Spec('!=1.0.1')
            False

        The kind of 'Almost equal to' specifications



.. _SemVer: http://semver.org/

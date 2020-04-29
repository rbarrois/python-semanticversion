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

.. class:: Version(major: int, minor: int, patch: int, prereleases: tuple, build: tuple[, partial=False])

    Constructed from named components:

        .. code-block:: pycon

            >>> Version(major=1, minor=2, patch=3)
            Version('1.2.3')



    .. rubric:: Attributes


    .. attribute:: partial

        ``bool``, whether this is a 'partial' or a complete version number.
        Partial version number may lack :attr:`minor` or :attr:`patch` version numbers.

        .. deprecated:: 2.7
            The ability to define a partial version will be removed in version 3.0.
            Use :class:`SimpleSpec` instead: ``SimpleSpec('1.x.x')``.

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

    .. attribute:: precedence_key

        Read-only attribute; suited for use in ``sort(versions, key=lambda v: v.precedence_key)``.
        The actual value of the attribute is considered an implementation detail; the only
        guarantee is that ordering versions by their precedence_key will comply with semver precedence rules.

        Note that the :attr:`~Version.build` isn't included in the precedence_key computatin.

    .. rubric:: Methods


    .. method:: next_major(self)

        Return the next major version, i.e the smallest version strictly greater
        than the current one with minor and patch set to 0 and no prerelease/build.

        .. code-block:: pycon

            >>> Version('1.0.2').next_major()
            Version('2.0.0')
            >>> Version('1.0.0+b3').next_major()
            Version('2.0.0')
            >>> Version('1.0.0-alpha').next_major()
            Version('1.0.0')

    .. method:: next_minor(self)

        Return the next minor version, i.e the smallest version strictly greater
        than the current one, with a patch level of ``0``.

        .. code-block:: pycon

            >>> Version('1.0.2').next_minor()
            Version('1.1.0')
            >>> Version('1.0.0+b3').next_minor()
            Version('1.1.0')
            >>> Version('1.1.2-alpha').next_minor()
            Version('1.2.0')
            >>> Version('1.1.0-alpha').next_minor()
            Version('1.1.0')

    .. method:: next_patch(self):

        Return the next patch version, i.e the smallest version strictly
        greater than the current one with empty :attr:`prerelease` and :attr:`build`.

        .. code-block:: pycon

            >>> Version('1.0.2').next_patch()
            Version('1.0.3')
            >>> Version('1.0.2+b3').next_patch()
            Version('1.0.3')
            >>> Version('1.0.2-alpha').next_patch()
            Version('1.0.2')

        .. warning:: The next patch version of a version with a non-empty
                     :attr:`prerelease` is the version without that
                     :attr:`prerelease` component: it's the smallest "pure"
                     patch version strictly greater than that version.

    .. method:: truncate(self, level='patch']):

        Returns a similar level, but truncated at the provided level.

        .. code-block:: pycon

            >>> Version('1.0.2-rc1+b43.24').truncate()
            Version('1.0.2')
            >>> Version('1.0.2-rc1+b43.24').truncate('minor')
            Version('1.0.0')
            >>> Version('1.0.2-rc1+b43.24').truncate('prerelease')
            Version('1.0.2-rc1')


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

The `SemVer`_ specification doesn't provide a standard description of version ranges.
And simply using a naive implementation leads to unexpected situations: ``>=1.2.0,<1.3.0`` isn't expected to match
version ``1.3.0-rc.1``, yet a strict application of `SemVer`_ precedence rules would include it.

In order to solve this problem, each `SemVer`_-based package management platform has designed its own rules.
python-semanticversion provides a couple of implementations of those range definition syntaxes:

- ``'simple'`` (through :class:`SimpleSpec`): A python-semanticversion specific syntax, which supports simple / intuitive patterns, and some NPM-inspired extensions;
- ``'npm'`` (through :class:`NpmSpec`): The NPM syntax, based on https://docs.npmjs.com/misc/semver.html
- More might be added in the future.

Each of those ``Spec`` classes provides a shared set of methods to work with versions:

.. class:: BaseSpec(spec_string)

    Converts an expression describing a range of versions into a set of clauses,
    and matches any :class:`Version` against those clauses.


    .. rubric:: Attributes

    This class has no public attributes.

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

    .. method:: __hash__(self)

        Provides a hash based solely on the hash of contained specs.

        Allows using a :class:`Spec` as a dictionary key.


    .. rubric:: Class methods


    .. classmethod:: parse(self, expression, syntax='simple')

        Retrieve a :class:`BaseSpec` object tuple from a string.

        :param str requirement_string: The textual description of the specifications
        :param str syntax: The identifier of the syntax to use for parsing
        :raises: :exc:`ValueError`: if the ``requirement_string`` is invalid.
        :rtype: :class:`BaseSpec` subclass

        .. versionchanged:: 2.7
            This method used to return a tuple of :class:`SpecItem` objects.


.. class:: SimpleSpec(spec_string)

    .. versionadded:: 2.7
        Previously reachable through :class:`Spec`.

    Applies the python-semanticversion range specification:

    * A specification of ``<1.3.4`` is not expected to allow ``1.3.4-rc2``, but strict `SemVer`_ comparisons allow it ;
    * It may be necessary to exclude either all variations on a patch-level release
      (``!=1.3.3``) or specifically one build-level release (``1.3.3+build.434``).


    .. rubric:: Specification structure:

    In order to have version specification behave naturally, the :class:`SimpleSpec` syntax uses the following rules:

    * A specification expression is a list of clauses separated by a comma (``,``);
    * A version is matched by an expression if, and only if, it matches every clause in the expression;
    * A clause of ``*`` matches every valid version;

    .. rubric:: Equality clauses

    * A clause of ``==0.1.2`` will match version ``0.1.2`` and any version differing only through its build number (``0.1.2+b42`` matches);
    * A clause of ``==0.1.2+b42`` will only match that specific version: ``0.1.2+b43`` and ``0.1.2`` are excluded;
    * A clause of ``==0.1.2+`` will only match that specific version: ``0.1.2+b42`` is excluded;
    * A clause of ``!=0.1.2`` will prevent all versions with the same major/minor/patch combination: ``0.1.2-rc.1`` and ``0.1.2+b42`` are excluded'
    * A clause of ``!=0.1.2-`` will only prevent build variations of that version: ``0.1.2-rc.1`` is included, but not ``0.1.2+b42``;
    * A clause of ``!=0.1.2+`` will exclude only that exact version: ``0.1.2-rc.1`` and ``0.1.2+b42`` are included;
    * Only a ``==`` or ``!=`` clause may contain build-level metadata: ``==1.2.3+b42`` is valid, ``>=1.2.3+b42`` isn't.

    .. rubric:: Comparison clauses

    * A clause of ``<0.1.2`` will match versions strictly below ``0.1.2``, excluding prereleases of ``0.1.2``: ``0.1.2-rc.1`` is excluded;
    * A clause of ``<0.1.2-`` will match versions strictly below ``0.1.2``, including prereleases of ``0.1.2``: ``0.1.2-rc.1`` is included;
    * A clause of ``<0.1.2-rc.3`` will match versions strictly below ``0.1.2-rc.3``, including prereleases: ``0.1.2-rc.2`` is included;
    * A clause of ``<=XXX`` will match versions that match ``<XXX`` or ``==XXX``
    * A clause of ``>0.1.2`` will match versions strictly above ``0.1.2``, including all prereleases of ``0.1.3``.
    * A clause of ``>0.1.2-rc.3`` will match versions strictly above ``0.1.2-rc.3``, including matching prereleases of ``0.1.2``: ``0.1.2-rc.10`` is included;
    * A clause of ``>=XXX`` will match versions that match ``>XXX`` or ``==XXX``

    ..rubric:: Wildcards

    * A clause of ``==0.1.*`` is equivalent to ``>=0.1.0,<0.2.0``
    * A clause of ``>=0.1.*`` is equivalent to ``>=0.1.0``
    * A clause of ``==1.*`` or ``==1.*.*`` is equivalent to ``>=1.0.0,<2.0.0``
    * A clause of ``>=1.*`` or ``>=1.*.*`` is equivalent to ``>=1.0.0``
    * A clause of ``==*`` maps to ``>=0.0.0``
    * A clause of ``>=*`` maps to ``>=0.0.0``

    .. rubric:: Extensions

    Additionnally, python-semanticversion supports extensions from specific packaging platforms:

    PyPI-style `compatible release clauses`_:

              * ``~=2.2`` means "Any release between 2.2.0 and 3.0.0"
              * ``~=1.4.5`` means "Any release between 1.4.5 and 1.5.0"

    NPM-style specs:

              * ``~1.2.3`` means "Any release between 1.2.3 and 1.3.0"
              * ``^1.3.4`` means "Any release between 1.3.4 and 2.0.0"

    Some examples:

    .. code-block:: pycon

        >>> Version('0.1.2-rc.1') in SimpleSpec('*')
        True
        >>> SimpleSpec('<0.1.2').filter([Version('0.1.2-rc.1'), Version('0.1.1'), Version('0.1.2+b42')])
        [Version('0.1.1')]
        >>> SimpleSpec('<0.1.2-').filter([Version('0.1.2-rc.1'), Version('0.1.1'), Version('0.1.2+b42')])
        [Version('0.1.2-rc.1'), Version('0.1.1')]
        >>> SimpleSpec('>=0.1.2,!=0.1.3,!=0.1.4-rc.1',!=0.1.5+b42).filter([
                Version('0.1.2'), Version('0.1.3'), Version('0.1.3-beta'),
                Version('0.1.4'), Version('0.1.5'), Version('0.1.5+b42'),
                Version('2.0.1-rc.1'),
            ])
        [Version('0.1.2'), Version('0.1.4'), Version('0.1.5'), Version('2.0.1-rc.1')]

.. class:: NpmSpec(spec_string)

    .. versionadded:: 2.7

    A NPM-compliant version matching engine, based on the https://docs.npmjs.com/misc/semver.html specification.

    .. code-block:: pycon

        >>> Version('0.1.2') in NpmSpec('0.1.0-alpha.2 .. 0.2.4')
        True
        >>> Version('0.1.2') in NpmSpec('>=0.1.1 <0.1.3 || 2.x')
        True
        >>> Version('2.3.4') in NpmSpec('>=0.1.1 <0.1.3 || 2.x')
        True


.. class:: Spec(spec_string)

    .. deprecated:: 2.7
        The alias from :class:`Spec` to :class:`SimpleSpec` will be removed in 3.1.

    Alias to :class:`LegacySpec`, for backwards compatibility.


.. class:: LegacySpec(spec_string)

    .. deprecated:: 2.7
        The :class:`LegacySpec` class will be removed in 3.0; use :class:`SimpleSpec` instead.

    A :class:`LegacySpec` class has the exact same behaviour as :class:`SimpleSpec`, with
    backwards-compatible features:

    It accepts version specifications passed in as separated arguments::

        >>> Spec('>=1.0.0', '<1.2.0', '!=1.1.4,!=1.1.13')
        <Spec: (
            <SpecItem: >= Version('1.0.0', partial=True)>,
            <SpecItem: < Version('1.2.0', partial=True)>,
            <SpecItem: != Version('1.1.4', partial=True)>,
            <SpecItem: != Version('1.1.13', partial=True)>,
        )>

    Its keeps a list of :class:`SpecItem` objects, based on the initial expression
    components.

    .. method:: __iter__(self)

        Returns an iterator over the contained specs::

            >>> for spec in Spec('>=0.1.1,!=0.1.2'):
            ...     print spec
            >=0.1.1
            !=0.1.2

    .. rubric:: Attributes

    .. attribute:: specs

        Tuple of :class:`SpecItem`, the included specifications.


.. class:: SpecItem(spec_string)

    .. deprecated:: 2.7
        This class will be removed in 3.0.

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
.. _`compatible release clauses`: https://www.python.org/dev/peps/pep-0440/#compatible-release

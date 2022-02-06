Guide
=====

.. currentmodule:: semantic_version

This module covers the 2.0.0 version of the SemVer scheme, with additional
extensions:

- Coercing any version string into a SemVer version, through
  :meth:`Version.coerce`;
- Comparing versions;
- Computing next versions;
- Modelling version range specifcations, and choosing the best match -- for both
  its custom logic, and NPM semantics (custom range specification schemes can
  be added).


Version basics
--------------

Building :class:`Version` instances
"""""""""""""""""""""""""""""""""""

The core of the module is the :class:`Version` class; it is usually instantiated
from a version string:

.. code-block:: pycon

    >>> import semantic_version as semver
    >>> v = semver.Version("0.1.1")

The version's components are available through its attributes:

* :attr:`~Version.major`, :attr:`~Version.minor`, :attr:`~Version.patch` are
  integers:

  .. code-block:: pycon

      >>> v.major
      0
      >>> v.minor
      1
      >>> v.patch
      1


* The :attr:`~Version.prerelease` and :attr:`~Version.build` attributes are
  iterables of text elements:

  .. code-block:: pycon

      >>> v2 = semver.Version("0.1.1-dev+23.git2")
      >>> v2.prerelease
      ["dev"]
      >>> v2.build
      ["23", "git2"]


One may also build a :class:`Version` from named components directly:

.. code-block:: pycon

    >>> semantic_version.Version(major=0, minor=1, patch=2)
    Version('0.1.2')


In that case, ``major``, ``minor`` and ``patch`` are mandatory, and must be integers.
``prerelease`` and ``build``, if provided, must be tuples of strings:

.. code-block:: pycon

    >>> semantic_version.Version(major=0, minor=1, patch=2, prerelease=('alpha', '2'))
    Version('0.1.2-alpha.2')


If the provided version string is invalid, a :exc:`ValueError` will be raised:

.. code-block:: pycon

    >>> semver.Version('0.1')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/Users/rbarrois/dev/semantic_version/src/semantic_version/base.py", line 64, in __init__
        major, minor, patch, prerelease, build = self.parse(version_string, partial)
      File "/Users/rbarrois/dev/semantic_version/src/semantic_version/base.py", line 86, in parse
        raise ValueError('Invalid version string: %r' % version_string)
    ValueError: Invalid version string: '0.1'


Working with non-SemVer version strings
"""""""""""""""""""""""""""""""""""""""

Some user-supplied input might not match the semantic version scheme.
For such cases, the ``Version.coerce`` method will try to convert any
version-like string into a valid semver version:

.. code-block:: pycon

    >>> semver.Version.coerce('0')
    Version('0.0.0')
    >>> semver.Version.coerce('0.1.2.3.4')
    Version('0.1.2+3.4')
    >>> semver.Version.coerce('0.1.2a3')
    Version('0.1.2-a3')


Comparing versions
""""""""""""""""""

Versions can be compared, following the SemVer scheme:

.. code-block:: pycon

    >>> semver.Version("0.1.0") < semver.Version("0.1.1")
    True
    >>> max(
    ...   semver.Version("0.1.0"),
    ...   semver.Version("0.2.2"),
    ...   semver.Version("0.1.1"),
    ...   semver.Version("0.2.2-rc1"),
    ... )
    Version("0.2.2")


.. note::

    As defined in SemVer, build metadata is ignored in comparisons,
    but not in equalities:

    .. code-block:: pycon

        >>> semver.Version("0.1.2") <= semver.Version("0.1.2+git2")
        True
        >>> semver.Version("0.1.2") >= semver.Version("0.1.2+git2")
        True
        >>> semver.Version("0.1.2") == semver.Version("0.1.2+git2")
        False


Iterating versions
""""""""""""""""""

One can get a new version that represents a bump in one of the version levels
through the :meth:`Version.next_major`, :meth:`Version.next_minor` or
:meth:`Version.next_patch` functions:

.. code-block:: pycon

    >>> v = semver.Version('0.1.1+build')
    >>> new_v = v.next_major()
    >>> str(new_v)
    '1.0.0'
    >>> v = semver.Version('1.1.1+build')
    >>> new_v = v.next_minor()
    >>> str(new_v)
    '1.2.0'
    >>> v = semver.Version('1.1.1+build')
    >>> new_v = v.next_patch()
    >>> str(new_v)
    '1.1.2'

.. note::

    * If the version includes :attr:`~Version.build` or
      :attr:`~Version.prerelease` metadata, that value will be empty in the
      next version;
    * The next patch following a version with a pre-release identifier
      is the same version with its prerelease and build identifiers removed:
      ``Version("0.1.1-rc1").next_patch() == Version("0.1.1")``
    * Pre-release and build naming schemes are often custom and specific
      to a project's internal design; thus, the library can't provide a
      ``next_xxx`` method for those fields.

One may also truncate versions through the :meth:`Version.truncate` method,
removing components beyond the selected level:

.. code-block:: pycon

    >>> v = semver.Version("0.1.2-dev+git3")
    >>> v.truncate("prerelease")
    Version("0.1.2-dev")
    >>> v.truncate("minor")
    Version("0.1.0")


Range specifications
--------------------

Comparing version numbers isn't always enough; in many situations, one needs to
define a *range of acceptable versions*.

That notion is not defined in SemVer; moreover, several systems exists, with
their own notations.

The ``semantic_version`` package provides a couple of implementations for these
notions:

- :class:`SimpleSpec` is a simple implementation, with reasonable expectations;
- :class:`NpmSpec` sticks to the NPM specification.

Further schemes can be built in a similar manner, relying on the :class:`BaseSpec`
class for basics.

Core API
""""""""

The core API is provided by the :class:`BaseSpec` class.

.. note::

    These examples use :class:`SimpleSpec` in order to be easily reproduced
    by users, but only exhibit the standard parts of the interface.

It is possible to check whether a given :class:`Version` matches a
:class:`BaseSpec` through :meth:`~BaseSpec.match`:

.. code-block:: pycon

    >>> s = semver.SimpleSpec(">=0.1.1")
    >>> s.match(Version("0.1.1"))
    True
    >>> s.match(Version("0.1.0"))
    False

This feature is also available through the ``in`` keyword:

.. code-block:: pycon

    >>> s = semver.SimpleSpec(">=0.1.1")
    >>> Version("0.1.1") in s
    True
    >>> Version("0.1.0") in s
    False

A specification can filter compatible values from an iterable of versions
with :meth:`~BaseSpec.filter`:

.. code-block:: pycon

    >>> s = semver.SimpleSpec(">=0.2.1")
    >>> versions = [
    ...   Version("0.1.0"),
    ...   Version("0.2.0"),
    ...   Version("0.3.0"),
    ...   Version("0.4.0"),
    ... ]
    >>> list(s.filter(versions))
    [Version("0.3.0"), Version("0.4.0")]

It can also select the "best" version from such an iterable through
:meth:`~BaseSpec.select`:

.. code-block:: pycon

    >>> s = semver.SimpleSpec(">=0.2.1")
    >>> versions = [
    ...   Version("0.1.0"),
    ...   Version("0.2.0"),
    ...   Version("0.3.0"),
    ...   Version("0.4.0"),
    ... ]
    >>> s.select(versions)
    Version("0.4.0")


The :class:`SimpleSpec` scheme
""""""""""""""""""""""""""""""

The :class:`SimpleSpec` provides a hopefully intuitive version range
specification scheme:

- A specification expression is composed of comma-separated clauses;
- Each clause can be:

  - An equality match (``==`` or ``!=``);
  - A comparison (``>``, ``>=``, ``<`` , ``<=``);
  - A compatible release clause, PyPI style (``~=2.2`` for ``>=2.2.0,<3.0.0``);
  - An NPM style clause:

    - ``~1.2.3`` for ``>=1.2.3,<1.3.0``;
    - ``^1.3.4`` for ``>=1.3.4,<2.0.0``;

- The range in each clause may include a wildcard:

  * ``==0.1.*`` maps to ``>=0.1.0,<0.2.0``;
  * ``==1.*`` or ``==1.*.*`` map to ``>=1.0.0,<2.0.0``


.. rubric:: Special matching rules

When testing a :class:`Version` against a :class:`SimpleSpec`, comparisons are
adjusted for common user expectations; thus, a pre-release version (``1.0.0-alpha``)
will not satisfy the ``==1.0.0`` :class:`SimpleSpec`.

Pre-release identifiers will only be compared if included in the :class:`BaseSpec`
definition or (for the empty pre-release number) if a single dash is appended
(``1.0.0-``):


.. code-block:: pycon

    >>> Version('0.1.0-alpha') in SimpleSpec('<0.1.0')  # No pre-release identifier
    False
    >>> Version('0.1.0-alpha') in SimpleSpec('<0.1.0-')  # Include pre-release in checks
    True


Build metadata has no ordering; thus, the only meaningful comparison including
build metadata is equality:


.. code-block:: pycon

    >>> Version('1.0.0+build2') in SimpleSpec('<=1.0.0')   # Build metadata ignored
    True
    >>> Version('1.0.0+build1') in SimpleSpec('==1.0.0+build2')  # Include build in checks
    False

.. note::

    The full documentation is provided in the reference section
    for the :class:`SimpleSpec` class.


The :class:`NpmSpec` scheme
"""""""""""""""""""""""""""

The :class:`NpmSpec` class implements the full NPM specification (from
https://github.com/npm/node-semver#ranges):

.. code-block:: pycon

    >>> semver.Version("0.1.2") in semver.NpmSpec("0.1.0-alpha.2 .. 0.2.4")
    True
    >>> semver.Version('0.1.2') in semver.NpmSpec('>=0.1.1 <0.1.3 || 2.x')
    True
    >>> semver.Version('2.3.4') in semver.NpmSpec('>=0.1.1 <0.1.3 || 2.x')
    True

Using with Django
-----------------

The :mod:`semantic_version.django_fields` module provides django fields to
store :class:`Version` or :class:`BaseSpec` objects.

More documentation is available in the :doc:`django` section.

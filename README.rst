.. python-semanticversion documentation master file, created by
   sphinx-quickstart on Wed May 16 10:41:34 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

python-semanticversion
======================

This small python library provides a few tools to handle `SemVer`_ in Python.
It follows strictly the 2.0.0 version of the SemVer scheme.

.. image:: https://secure.travis-ci.org/rbarrois/python-semanticversion.png?branch=master
    :target: http://travis-ci.org/rbarrois/python-semanticversion/

semantic_version supports Python 2.6, 2.7, 3.2, 3.3, and is distributed under the two-clause BSD licence.

Links
-----

- Package on `PyPI`_: http://pypi.python.org/pypi/semantic_version/
- Doc on `ReadTheDocs <http://readthedocs.org/>`_: http://readthedocs.org/docs/python-semanticversion/
- Source on `GitHub <http://github.com/>`_: http://github.com/rbarrois/python-semanticversion/
- Build on `Travis CI <http://travis-ci.org/>`_: http://travis-ci.org/rbarrois/python-semanticversion/
- Semantic Version specification: `SemVer`_


Getting started
===============

Intall the package from `PyPI`_, using pip:

.. code-block:: sh

    pip install semantic_version

Or from GitHub:

.. code-block:: sh

    $ git clone git://github.com/rbarrois/python-semanticversion.git


Import it in your code:


.. code-block:: python

    import semantic_version


.. currentmodule:: semantic_version

This module provides two classes to handle semantic versions:

- :class:`Version` represents a version number (``0.1.1-alpha+build.2012-05-15``)
- :class:`Spec` represents a requirement specification (``>=0.1.1,<0.3.0``)

Versions
--------

Defining a :class:`Version` is quite simple:


.. code-block:: pycon

    >>> import semantic_version
    >>> v = semantic_version.Version('0.1.1')
    >>> v.major
    0
    >>> v.minor
    1
    >>> v.patch
    1
    >>> v.prerelease
    []
    >>> v.build
    []
    >>> list(v)
    [0, 1, 1, [], []]

If the provided version string is invalid, a :exc:`ValueError` will be raised:

.. code-block:: pycon

    >>> semantic_version.Version('0.1')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/Users/rbarrois/dev/semantic_version/src/semantic_version/base.py", line 64, in __init__
        major, minor, patch, prerelease, build = self.parse(version_string, partial)
      File "/Users/rbarrois/dev/semantic_version/src/semantic_version/base.py", line 86, in parse
        raise ValueError('Invalid version string: %r' % version_string)
    ValueError: Invalid version string: '0.1'

In order to define "relaxed" version strings, you must pass in ``partial=True``:

.. code-block:: pycon

    >>> v = semantic_version.Version('0.1', partial=True)
    >>> list(v)
    [0, 1, None, None, None]


Obviously, :class:`Versions <Version>` can be compared:


.. code-block:: pycon

    >>> semantic_version.Version('0.1.1') < semantic_version.Version('0.1.2')
    True
    >>> semantic_version.Version('0.1.1') > semantic_version.Version('0.1.1-alpha')
    True
    >>> semantic_version.Version('0.1.1') <= semantic_version.Version('0.1.1-alpha')
    False

You can also get a new version that represents a bump in one of the version levels:

.. code-block:: pycon

    >>> v = semantic_version.Version('0.1.1-pre+build')
    >>> new_v = v.next_major()
    >>> str(new_v)
    '1.0.0'
    >>> v = semantic_version.Version('1.1.1-pre+build')
    >>> new_v = v.next_minor()
    >>> str(new_v)
    '1.1.0'
    >>> v = semantic_version.Version('1.1.1-pre+build')
    >>> new_v = v.next_patch()
    >>> str(new_v)
    '1.1.2'

It is also possible to check whether a given string is a proper semantic version string:


.. code-block:: pycon

    >>> semantic_version.validate('0.1.3')
    True
    >>> semantic_version.validate('0a2')
    False


Requirement specification
-------------------------

The :class:`Spec` object describes a range of accepted versions:


.. code-block:: pycon

    >>> s = Spec('>=0.1.1')  # At least 0.1.1
    >>> s.match(Version('0.1.1'))
    True
    >>> s.match(Version('0.1.1-alpha1'))  # pre-release satisfy version spec
    True
    >>> s.match(Version('0.1.0'))
    False

Simpler test syntax is also available using the ``in`` keyword:

.. code-block:: pycon

    >>> s = Spec('==0.1.1')
    >>> Version('0.1.1-alpha1') in s
    True
    >>> Version('0.1.2') in s
    False


Combining specifications can be expressed in two ways:

- Components separated by commas in a single string:

  .. code-block:: pycon

      >>> Spec('>=0.1.1,<0.3.0')

- Components given as different arguments:

  .. code-block:: pycon

      >>> Spec('>=0.1.1', '<0.3.0')

- A mix of both versions:

  .. code-block:: pycon

      >>> Spec('>=0.1.1', '!=0.2.4-alpha,<0.3.0')


Using a specification
"""""""""""""""""""""

The :func:`Spec.filter` method filters an iterable of :class:`Version`:

.. code-block:: pycon

    >>> s = Spec('>=0.1.0,<0.4.0')
    >>> versions = (Version('0.%d.0' % i) for i in range(6))
    >>> for v in s.filter(versions):
    ...     print v
    0.1.0
    0.2.0
    0.3.0

It is also possible to select the 'best' version from such iterables:


.. code-block:: pycon

    >>> s = Spec('>=0.1.0,<0.4.0')
    >>> versions = (Version('0.%d.0' % i) for i in range(6))
    >>> s.select(versions)
    Version('0.3.0')


Coercing an arbitrary version string
""""""""""""""""""""""""""""""""""""

Some user-supplied input might not match the semantic version scheme.
For such cases, the :meth:`Version.coerce` method will try to convert any
version-like string into a valid semver version:

.. code-block:: pycon

    >>> Version.coerce('0')
    Version('0.0.0')
    >>> Version.coerce('0.1.2.3.4')
    Version('0.1.2+3.4')
    >>> Version.coerce('0.1.2a3')
    Version('0.1.2-a3')


Including pre-release identifiers in specifications
"""""""""""""""""""""""""""""""""""""""""""""""""""

When testing a :class:`Version` against a :class:`Spec`, comparisons are only
performed for components defined in the :class:`Spec`; thus, a pre-release
version (``1.0.0-alpha``), while not strictly equal to the non pre-release
version (``1.0.0``), satisfies the ``==1.0.0`` :class:`Spec`.

Pre-release identifiers will only be compared if included in the :class:`Spec`
definition or (for the empty pre-release number) if a single dash is appended
(``1.0.0-``):


.. code-block:: pycon

    >>> Version('0.1.0-alpha') in Spec('>=0.1.0')  # No pre-release identifier
    True
    >>> Version('0.1.0-alpha') in Spec('>=0.1.0-')  # Include pre-release in checks
    False


Including build identifiers in specifications
"""""""""""""""""""""""""""""""""""""""""""""

The same rule applies for the build identifier: comparisons will include it only
if it was included in the :class:`Spec` definition, or - for the unnumbered build
version - if a single + is appended to the definition(``1.0.0+``, ``1.0.0-alpha+``):


.. code-block:: pycon

    >>> Version('1.0.0+build2') in Spec('<=1.0.0')   # Build identifier ignored
    True
    >>> Version('1.0.0+build2') in Spec('<=1.0.0+')  # Include build in checks
    False


Using with Django
=================

The :mod:`semantic_version.django_fields` module provides django fields to
store :class:`Version` or :class:`Spec` objects.

More documentation is available in the :doc:`django` section.


Contributing
============

In order to contribute to the source code:

- Open an issue on `GitHub`_: https://github.com/rbarrois/python-semanticversion/issues
- Fork the `repository <https://github.com/rbarrois/python-semanticversion>`_
  and submit a pull request on `GitHub`_
- Or send me a patch (mailto:raphael.barrois+semver@polytechnique.org)

When submitting patches or pull requests, you should respect the following rules:

- Coding conventions are based on :pep:`8`
- The whole test suite must pass after adding the changes
- The test coverage for a new feature must be 100%
- New features and methods should be documented in the :doc:`reference` section
  and included in the :doc:`changelog`
- Include your name in the :ref:`contributors` section

.. note:: All files should contain the following header::

          # -*- encoding: utf-8 -*-
          # Copyright (c) 2012-2014 The python-semanticversion project


Contents
========

.. toctree::
   :maxdepth: 2

   reference
   django
   changelog
   credits


.. _SemVer: http://semver.org/
.. _PyPI: http://pypi.python.org/

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


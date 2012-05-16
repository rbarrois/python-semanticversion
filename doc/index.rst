.. python-semanticversion documentation master file, created by
   sphinx-quickstart on Wed May 16 10:41:34 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

python-semanticversion
======================

This small python library provides a few tools to handle `SemVer`_ in Python.


The first release (1.0.0) should handle the 2.0.0-rc1 version of the SemVer scheme.


Getting started
===============

Intall the package from `PyPI`_, using pip::

    pip install python-semanticversion


Import it in your code::

    import semantic_version

.. currentmodule:: semantic_version

This module provides two classes to handle semantic versions:

- :class:`Version` represents a version number (``0.1.1-alpha+build.2012-05-15``)
- :class:`Spec` represents a requirement specification (``>=0.1.1``)

Versions
--------

Defining a :class:`Version` is quite simple::

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

If the provided version string is invalid, a :exc:`ValueError` will be raised::

    >>> semantic_version.Version('0.1')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/Users/rbarrois/dev/semantic_version/src/semantic_version/base.py", line 64, in __init__
        major, minor, patch, prerelease, build = self.parse(version_string, partial)
      File "/Users/rbarrois/dev/semantic_version/src/semantic_version/base.py", line 86, in parse
        raise ValueError('Invalid version string: %r' % version_string)
    ValueError: Invalid version string: '0.1'

In order to define "relaxed" version strings, you must pass in ``partial=True``::

    >>> v = semantic_version.Version('0.1', partial=True)
    >>> list(v)
    [0, 1, None, None, None]


Obviously, :class:`Versions <Version>` can be compared::

    >>> semantic_version.Version('0.1.1') < semantic_version.Version('0.1.2')
    True
    >>> semantic_version.Version('0.1.1') > semantic_version.Version('0.1.1-alpha')
    True
    >>> semantic_version.Version('0.1.1') <= semantic_version.Version('0.1.1-alpha')
    False


Requirement specification
-------------------------

The :class:`Spec` object describes a range of accepted versions::

    >>> s = Spec('>=0.1.1')  # At least 0.1.1
    >>> s.match(Version('0.1.1'))
    True
    >>> s.match(Version('0.1.1-alpha1'))
    False

It is also possible to define 'approximate' version specifications::

    >>> s = Spec('~0.1')  # Matches 0.1.*
    >>> s.match(Version('0.1.0-alpha1'))
    True
    >>> s.match(Version('0.1.9999999999+build99'))
    True
    >>> s.match(Version('0.2.0'))
    False

Simpler test syntax is also available using the ``in`` keyword::

    >>> s = Spec('~0.1.1')
    >>> Version('0.1.1-alpha1') in s
    True
    >>> Version('0.1.2') in s
    False


Contents
========

.. toctree::
   :maxdepth: 2

   reference
   django

Links
=====

- Package on `PyPI`_: http://pypi.python.org/semantic_version/
- Doc on `ReadTheDocs <http://readthedocs.org/>`_: http://readthedocs.org/docs/python-semanticversion/
- Source on `GitHub <http://github.com/>`_: http://github.com/rbarrois/python-semanticversion/
- Build on `Travis CI <http://travis-ci.org/>`_: http://travis-ci.org/rbarrois/python-semanticversion/
- Semantic Version specification: `SemVer`_

.. _SemVer: http://semver.org/
.. _PyPI: http://pypi.python.org/


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


ChangeLog
=========

2.8.5 (2020-04-29)
------------------

*Bugfix:*

    * `98 <https://github.com/rbarrois/python-semanticversion/issues/98>`_:
      Properly handle wildcards in ``SimpleSpec`` (e.g. ``==1.2.*``).


2.8.4 (2019-12-21)
------------------

*Bugfix:*

    * `#89 <https://github.com/rbarrois/python-semanticversion/issues/89>`_:
      Properly coerce versions with leading zeroes in components (e.g.
      ``1.01.007``)


2.8.3 (2019-11-21)
------------------

*New:*
    - Add `Clause.prettyprint()` for debugging

*Bugfix:*

    * `#86 <https://github.com/rbarrois/python-semanticversion/issues/86>`_:
      Fix handling of prerelease ranges within `NpmSpec`


2.8.2 (2019-09-06)
------------------

*Bugfix:*

    * `#82 <https://github.com/rbarrois/python-semanticversion/issues/82>`_:
      Restore computation of ``Spec.specs`` for single-term expressions
      (``>=0.1.2``)


2.8.1 (2019-08-29)
------------------

*Bugfix:*

    * Restored attribute ``Spec.specs``, removed by mistake during the refactor.


2.8.0 (2019-08-29)
------------------

*New:*

    * Restore support for Python 2.


2.7.1 (2019-08-28)
------------------

*Bugfix:*

    * Fix parsing of npm-based caret expressions.


2.7.0 (2019-08-28)
------------------

This release brings a couple of significant changes:

- Allow to define several range description syntaxes (``SimpleSpec``, ``NpmSpec``, ...)
- Fix bugs and unexpected behaviours in the ``SimpleSpec`` implementation.

Backwards compatibility has been kept, but users should adjust their code for the new features:

- Use ``SimpleSpec`` instead of ``Spec``
- Replace calls to ``Version('1.2', partial=True)`` with ``SimpleSpec('~1.2')``
- ``iter(some_spec)`` is deprecated.

*New:*

    * Allow creation of a ``Version`` directly from parsed components, as keyword arguments
      (``Version(major=1, minor=2, patch=3)``)
    * Add ``Version.truncate()`` to build a truncated copy of a ``Version``
    * Add ``NpmSpec(...)``, following strict NPM matching rules (https://docs.npmjs.com/misc/semver)
    * Add ``Spec.parse('xxx', syntax='<syntax>')`` for simpler multi-syntax support
    * Add ``Version().precedence_key``, for use in ``sort(versions, key=lambda v: v.precedence_key)`` calls.
      The contents of this attribute is an implementation detail.

*Bugfix:*

    * Fix inconsistent behaviour regarding versions with a prerelease specification.

*Deprecated:*

    * Deprecate the ``Spec`` class (Removed in 3.1); use the ``SimpleSpec`` class instead
    * Deprecate the internal ``SpecItem`` class (Removed in 3.0).
    * Deprecate the ``partial=True`` form of ``Version``; use ``SimpleSpec`` instead.

*Removed:*

    * Remove support for Python2 (End of life 4 months after this release)

*Refactor:*

    * Switch spec computation to a two-step process: convert the spec to a combination
      of simple comparisons with clear semantics, then use those.


2.6.0 (2016-09-25)
------------------

*New:*

    * `#43 <https://github.com/rbarrois/python-semanticversion/issues/43>`_:
      Add support for Django up to 1.10.

*Removed:*

    * Remove support for Django<1.7

*Bugfix:*

    * `#35 <https://github.com/rbarrois/python-semanticversion/issues/35>`_:
      Properly handle `^0.X.Y` in a NPM-compatible way

2.5.0 (2016-02-12)
------------------

*Bugfix:*

    `#18 <https://github.com/rbarrois/python-semanticversion/issues/18>`_: According to SemVer 2.0.0, build numbers aren't ordered.

    * Remove specs of the ``Spec('<1.1.3+')`` form
    * Comparing ``Version('0.1.0')`` to ``Version('0.1.0+bcd')`` has new
      rules::

          >>> Version('0.1.0+1') == Version('0.1.0+bcd')
          False
          >>> Version('0.1.0+1') != Version('0.1.0+bcd')
          True
          >>> Version('0.1.0+1') < Version('0.1.0+bcd')
          False
          >>> Version('0.1.0+1') > Version('0.1.0+bcd')
          False
          >>> Version('0.1.0+1') <= Version('0.1.0+bcd')
          False
          >>> Version('0.1.0+1') >= Version('0.1.0+bcd')
          False
          >>> compare(Version('0.1.0+1'), Version('0.1.0+bcd'))
          NotImplemented

    * :func:`semantic_version.compare` returns ``NotImplemented`` when its
      parameters differ only by build metadata
    * ``Spec('<=1.3.0')`` now matches ``Version('1.3.0+abde24fe883')``

    * `#24 <https://github.com/rbarrois/python-semanticversion/issues/24>`_: Fix handling of bumping pre-release versions, thanks to @minchinweb.
    * `#30 <https://github.com/rbarrois/python-semanticversion/issues/30>`_: Add support for NPM-style ``^1.2.3`` and ``~2.3.4`` specs, thanks to @skwashd

2.4.2 (2015-07-02)
------------------

*Bugfix:*

    * Fix tests for Django 1.7+, thanks to @mhrivnak.

2.4.1 (2015-04-01)
------------------

*Bugfix:*

    * Fix packaging metadata (advertise Python 3.4 support)

2.4.0 (2015-04-01)
------------------

*New:*

    * `#16 <https://github.com/rbarrois/python-semanticversion/issues/16>`_: Add an API for bumping versions,
      by @RickEyre.

2.3.1 (2014-09-24)
------------------

*Bugfix:*

    * `#13 <https://github.com/rbarrois/python-semanticversion/issues/13>`_: Fix handling of files encoding
      in ``setup.py``.

2.3.0 (2014-03-16)
------------------

*New:*

    * Handle the full ``semver-2.0.0`` specifications (instead of the ``2.0.0-rc2`` of previous releases)
    * `#8  <https://github.com/rbarrois/python-semanticversion/issues/8>`_: Allow ``'*'`` as a valid version spec


2.2.2 (2013-12-23)
------------------

*Bugfix:*

    * `#5 <https://github.com/rbarrois/python-semanticversion/issues/5>`_: Fix packaging (broken
      symlinks, old-style distutils, etc.)

2.2.1 (2013-10-29)
------------------

*Bugfix:*

    * `#2 <https://github.com/rbarrois/python-semanticversion/issues/2>`_: Properly expose
      :func:`~semantic_version.validate` as a top-level module function.

2.2.0 (2013-03-22)
------------------

*Bugfix:*

    * `#1 <https://github.com/rbarrois/python-semanticversion/issues/1>`_: Allow partial
      versions without minor or patch level

*New:*

    * Add the :meth:`Version.coerce <semantic_version.Version.coerce>` class method to
      :class:`~semantic_version.Version` class for mapping arbitrary version strings to
      semver.
    * Add the :func:`~semantic_version.validate` method to validate a version
      string against the SemVer rules.
    * Full Python3 support

2.1.2 (2012-05-22)
------------------

*Bugfix:*

    * Properly validate :class:`~semantic_version.django_fields.VersionField` and
      :class:`~semantic_version.django_fields.SpecField`.

2.1.1 (2012-05-22)
------------------

*New:*

    * Add introspection rules for south

2.1.0 (2012-05-22)
------------------

*New:*

    * Add :func:`semantic_version.Spec.filter` (filter a list of :class:`~semantic_version.Version`)
    * Add :func:`semantic_version.Spec.select` (select the highest
      :class:`~semantic_version.Version` from a list)
    * Update :func:`semantic_version.Version.__repr__`

2.0.0 (2012-05-22)
------------------

*Backwards incompatible changes:*

    * Removed "loose" specification support
    * Cleanup :class:`~semantic_version.Spec` to be more intuitive.
    * Merge Spec and SpecList into :class:`~semantic_version.Spec`.
    * Remove :class:`~semantic_version.django_fields.SpecListField`

1.2.0 (2012-05-18)
------------------

*New:*

    * Allow split specifications when instantiating a
      :class:`~semantic_version.SpecList`::

            >>> SpecList('>=0.1.1', '!=0.1.3') == SpecList('>=0.1.1,!=0.1.3')
            True

1.1.0 (2012-05-18)
------------------

*New:*

    * Improved "loose" specification support (``>~``, ``<~``, ``!~``)
    * Introduced "not equal" specifications (``!=``, ``!~``)
    * :class:`~semantic_version.SpecList` class combining many :class:`~semantic_version.Spec`
    * Add :class:`~semantic_version.django_fields.SpecListField` to store a :class:`~semantic_version.SpecList`.

1.0.0 (2012-05-17)
------------------

First public release.

*New:*

    * :class:`~semantic_version.Version` and :class:`~semantic_version.Spec` classes
    * Related django fields: :class:`~semantic_version.django_fields.VersionField`
      and :class:`~semantic_version.django_fields.SpecField`

.. vim:et:ts=4:sw=4:tw=79:ft=rst:

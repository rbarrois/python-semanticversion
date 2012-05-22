ChangeLog
=========

2.1.0 (22/05/2012)
------------------

*New:*

    * Add :func:`semantic_version.Spec.filter` (filter a list of :class:`~semantic_version.Version`)
    * Add :func:`semantic_version.Spec.select` (select the highest
      :class:`~semantic_version.Version` from a list)
    * Update :func:`semantic_version.Version.__repr__`

2.0.0 (22/05/2012)
------------------

*Backwards incompatible changes:*

    * Removed "loose" specification support
    * Cleanup :class:`~semantic_version.Spec` to be more intuitive.
    * Merge Spec and SpecList into :class:`~semantic_version.Spec`.
    * Remove :class:`~semantic_version.django_fields.SpecListField`

1.2.0 (18/05/2012)
------------------

*New:*

    * Allow split specifications when instantiating a
      :class:`~semantic_version.SpecList`::

            >>> SpecList('>=0.1.1', '!=0.1.3') == SpecList('>=0.1.1,!=0.1.3')
            True

1.1.0 (18/05/2012)
------------------

*New:*

    * Improved "loose" specification support (``>~``, ``<~``, ``!~``)
    * Introduced "not equal" specifications (``!=``, ``!~``)
    * :class:`~semantic_version.SpecList` class combining many :class:`~semantic_version.Spec`
    * Add :class:`~semantic_version.django_fields.SpecListField` to store a :class:`~semantic_version.SpecList`.

1.0.0 (17/05/2012)
------------------

First public release.

*New:*

    * :class:`~semantic_version.Version` and :class:`~semantic_version.Spec` classes
    * Related django fields: :class:`~semantic_version.django_fields.VersionField`
      and :class:`~semantic_version.django_fields.SpecField`

.. vim:et:ts=4:sw=4:tw=79:ft=rst:

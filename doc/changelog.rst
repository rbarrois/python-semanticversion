ChangeLog
=========

1.1.0 (current)
------------------

*New:*

    * Improved "loose" specification support (``>~``, ``<~``, ``!~``)
    * Introduced "not equal" specifications (``!=``, ``!~``)
    * :class:`~semantic_version.SpecList` class combining many :class:`~semantic_version.Spec`
    * Add :class:`~semantic_version.django_fields.SpecListField` to store a :class:`~semantic_version.SpecList`.

1.0.0 (18/05/2012)
------------------

First public release.

*New:*

    * :class:`~semantic_version.Version` and :class:`~semantic_version.Spec` classes
    * Related django fields: :class:`~semantic_version.django_fields.VersionField`
      and :class:`~semantic_version.django_fields.SpecField`

.. vim:et:ts=4:sw=4:tw=79:ft=rst:

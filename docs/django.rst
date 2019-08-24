Interaction with Django
=======================

.. module:: semantic_version.django_fields

The ``python-semanticversion`` package provides two custom fields for Django:

- :class:`VersionField`: stores a :class:`semantic_version.Version` object
- :class:`SpecField`: stores a :class:`semantic_version.BaseSpec` object

Those fields are :class:`django.db.models.CharField` subclasses,
with their :attr:`~django.db.models.CharField.max_length` defaulting to 200.


.. class:: VersionField

    Stores a :class:`semantic_version.Version` as its string representation.

    .. attribute:: partial

        .. deprecated:: 2.7
            Support for partial versions will be removed in 3.0.

        Boolean; whether :attr:`~semantic_version.Version.partial` versions are allowed.

    .. attribute:: coerce

        Boolean; whether passed in values should be coerced into a semver string
        before storing.


.. class:: SpecField

    Stores a :class:`semantic_version.BaseSpec` as its textual representation.

    .. attribute:: syntax

        The syntax to use for the field; defaults to ``'simple'``.

        .. versionaddedd:: 2.7

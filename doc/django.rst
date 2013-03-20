Interaction with Django
=======================

.. module:: semantic_version.django_fields

The ``python-semanticversion`` package provides two custom fields for Django:

- :class:`VersionField`: stores a :class:`semantic_version.Version` object
- :class:`SpecField`: stores a :class:`semantic_version.Spec` object

Those fields are :class:`django.db.models.CharField` subclasses,
with their :attr:`~django.db.models.CharField.max_length` defaulting to 200.


.. class:: VersionField

    Stores a :class:`semantic_version.Version` as its string representation.

    .. attribute:: partial

        Boolean; whether :attr:`~semantic_version.Version.partial` versions are allowed.

    .. attribute:: coerce

        Boolean; whether passed in values should be coerced into a semver string
        before storing.


.. class:: SpecField

    Stores a :class:`semantic_version.Spec` as its comma-separated string representation.

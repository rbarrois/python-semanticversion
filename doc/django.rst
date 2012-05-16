Interaction with Django
=======================

.. module:: semantic_version.django_fields

The ``python-semanticversion`` package provides two custom fields for Django:

- :class:`VersionField`: stores a :class:`semantic_version.Version` object
- :class:`SpecField`: stores a :class:`semantic_version.Spec` object


.. class:: VersionField

    Stores a :class:`semantic_version.Version`.

    .. attribute:: partial

        Boolean; whether :attr:`~semantic_version.Version.partial` versions are allowed.


.. class:: SpecField

    Stores a :class:`semantic_version.Spec`.

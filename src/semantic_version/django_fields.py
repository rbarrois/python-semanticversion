# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Raphaël Barrois

from django.db import models
from django.utils.translation import ugettext_lazy as _

from . import base


class BaseSemVerField(models.CharField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 200)
        super(BaseSemVerField, self).__init__(*args, **kwargs)

    def get_prep_value(self, obj):
        return str(obj)

    def get_db_prep_value(self, value, connection, prepared=False):
        if not prepared:
            value = self.get_prep_value(value)
        return value

    def value_to_string(self, obj):
        value = self.to_python(self._get_val_from_obj(obj))
        return str(value)

    def run_validators(self, value):
        return super(BaseSemVerField, self).run_validators(str(value))


class VersionField(BaseSemVerField):
    default_error_messages = {
        'invalid': _(u"Enter a valid version number in X.Y.Z format."),
    }
    description = _(u"Version")

    def __init__(self, *args, **kwargs):
        self.partial = kwargs.pop('partial', False)
        super(VersionField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        """Converts any value to a base.Version field."""
        if value is None or value == '':
            return value
        if isinstance(value, base.Version):
            return value
        return base.Version(value, partial=self.partial)


class SpecField(BaseSemVerField):
    default_error_messages = {
        'invalid': _(u"Enter a valid version number spec list in ==X.Y.Z,>=A.B.C format."),
    }
    description = _(u"Version specification list")

    def to_python(self, value):
        """Converts any value to a base.Spec field."""
        if value is None or value == '':
            return value
        if isinstance(value, base.Spec):
            return value
        return base.Spec(value)


def add_south_rules():
    from south.modelsinspector import add_introspection_rules

    add_introspection_rules([
        (
            (VersionField,),
            [],
            {'partial': ('partial', {'default': False})},
        ),
    ], ["semantic_version\.django_fields"])


try:  # pragma: no cover
    import south
except ImportError: # pragma: no cover
    south = None

if south:  # pragma: no cover
    add_south_rules()

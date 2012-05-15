# -*- coding: utf-8 -*-
# Copyright (c) 2012 Raphaël Barrois

from django.db import models
from django.utils.translation import ugettext_lazy as _

from . import base


class VersionField(models.CharField):
    default_error_messages = {
        'invalid': _(u"Enter a valid version number in X.Y.Z format."),
    }
    description = _(u"Version")

    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.partial = kwargs.pop('partial', False)
        kwargs.setdefault('max_length', 40)
        super(VersionField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        """Converts any value to a base.Version field."""
        if value is None or value == '':
            return value
        if isinstance(value, base.Version):
            return value
        return base.Version(value, partial=self.partial)

    def get_prep_value(self, obj):
        return str(obj)

    def get_db_prep_value(self, value, connection, prepared=False):
        if not prepared:
            value = self.get_prep_value(value)
        return value

    def value_to_string(self, obj):
        value = self.to_python(self._get_val_from_obj(obj))
        return str(value)


class SpecField(models.CharField):
    default_error_messages = {
        'invalid': _(u"Enter a valid version number spec in ==X.Y.Z format."),
    }
    description = _(u"Version specification")

    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 42)
        return super(SpecField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        """Converts any value to a base.Version field."""
        if value is None or value == '':
            return value
        if isinstance(value, base.Spec):
            return value
        return base.Spec(value)

    def get_prep_value(self, obj):
        return str(obj)

    def get_db_prep_value(self, value, connection, prepared=False):
        if not prepared:
            value = self.get_prep_value(value)
        return value

    def value_to_string(self, obj):
        value = self.to_python(self._get_val_from_obj(obj))
        return str(value)

# -*- coding: UTF-8 -*-
from __future__ import absolute_import, unicode_literals

# Standard Library
from builtins import bytes  # noqa
from builtins import str  # noqa
from itertools import groupby

# Third Party
import six


class MemberDoesNotExist(Exception):
    pass


class DataEnumType(type):
    def __init__(cls, *args, **kwargs):
        data_attribute_names = cls._data_attribute_names_flat
        for invalid_key in ['register', 'get', 'value', 'members', 'data_attribute_names']:
            if invalid_key in data_attribute_names:
                raise Exception('Invalid data attribute name "{}"'.format(invalid_key))

        if any(key.startswith('_') for key in data_attribute_names):
            raise Exception('Invalid data attribute prefix "_"')

        cls.members = set()

    def __getattr__(cls, attr):
        try:
            return cls._members_by_value[attr]
        except KeyError:
            raise AttributeError('"{}" has no attribute "{}"'.format(cls.__name__, attr))

    def _sort_members_by_attr(cls, attr):
        if attr == 'value' or attr in cls._data_attribute_names_flat_unique:
            return {getattr(obj, attr): obj for obj in cls.members}

    @property
    def _members_by_value(cls):
        return cls._sort_members_by_attr('value')

    @property
    def _data_attribute_names_flat(cls):
        flat_names = []
        for name in cls.data_attribute_names:
            if type(name) in [tuple, list]:
                flat_names.append(name[0])
            else:
                flat_names.append(name)
        return tuple(flat_names)

    @property
    def _data_attribute_names_flat_unique(cls):
        flat_names = []
        for name in cls.data_attribute_names:
            if type(name) in [tuple, list] and name[1]:
                flat_names.append(name[0])
        return tuple(flat_names)


class DataEnum(six.with_metaclass(DataEnumType, object)):
    data_attribute_names = ()

    _is_registered = False

    @classmethod
    def register(cls, members):
        if cls._is_registered:
            raise Exception('Enum members have already been registered')

        unique_attribute_names = cls._data_attribute_names_flat_unique
        for attr in unique_attribute_names:
            for value, grouper in groupby(members, key=lambda m: getattr(m, attr)):
                group_list = list(grouper)

                if len(group_list) != 1:
                    raise Exception('Duplicate enum value "{}" for unique attribute "{}"'.format(value, attr))

        cls.members = set(members)

        cls._is_registered = True

    @classmethod
    def get(cls, *args, **kwargs):
        has_default = False

        if len(args) == 2:
            has_default = True
            default = args[1]
            args = args[:1]
        else:
            try:
                default = kwargs.pop('default')
            except KeyError:
                pass
            else:
                has_default = True

        if len(args) == 1 and not kwargs:
            attr = 'value'
            value = args[0]
        elif len(kwargs) == 1 and not args:
            attr = next(iter(kwargs))
            value = kwargs[attr]
        else:
            raise Exception('Unexpected lookup arguments')

        objects = cls._sort_members_by_attr(attr)
        try:
            return objects[value]
        except KeyError:
            if not has_default:
                raise MemberDoesNotExist()

            return default

    def __init__(self, *args, **kwargs):
        if self._is_registered:
            raise Exception('Cannot initialize DataEnum member after registration')

        data_attribute_names_flat = type(self)._data_attribute_names_flat
        if 'value' in data_attribute_names_flat:
            raise Exception('Invalid data attribute name "value"')

        if not args:
            raise Exception('Initialize with a unique string value')

        args_list = list(args)

        self.value = args_list.pop(0)

        num_args = len(args_list)
        for i in range(num_args):
            setattr(self, data_attribute_names_flat[i], args_list[i])

        remaining_attribute_names = data_attribute_names_flat[num_args:]
        num_kwargs = len(kwargs)
        num_remaining_attributes = len(remaining_attribute_names)
        if num_kwargs < num_remaining_attributes:
            missing_attribute_names = [
                attribute_name
                for attribute_name in remaining_attribute_names
                if attribute_name not in kwargs
            ]
            raise Exception('Missing data attributes: {}'.format(', '.join(missing_attribute_names)))

        for kw, value in six.iteritems(kwargs):
            if kw not in remaining_attribute_names:
                raise Exception('Unexpected data attribute: {}'.format(kw))

            setattr(self, kw, value)

        unique_attribute_names = type(self)._data_attribute_names_flat_unique
        for member in self.members:
            for attr in unique_attribute_names:
                if getattr(member, attr) == getattr(self, attr):
                    raise Exception('Duplicate data attribute: {}'.format(attr))

    def __eq__(self, other):
        try:
            return self.value == other.value
        except AttributeError:
            return False

    # Backwards compatibility for Python 2.7
    def __ne__(self, other):
        try:
            return self.value != other.value
        except AttributeError:
            return False

    def __hash__(self):
        return hash(self.value)

    def __unicode__(self):
        return self.value

    def __int__(self):
        return self.value

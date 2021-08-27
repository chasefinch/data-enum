# -*- coding: UTF-8 -*-
from __future__ import absolute_import, unicode_literals

# Standard Library
from builtins import bytes  # noqa
from builtins import str  # noqa
from itertools import groupby

# Third Party
import six


class ConfigurationError(Exception):
    pass


class MemberDoesNotExistError(Exception):
    pass


class DataEnumType(type):
    """Metaclass for custom class-level functionality for DataEnum."""

    def __init__(cls, *args, **kwargs):
        """Define the new type in place."""
        try:
            assert type(cls.data_attribute_names) in (tuple, list)
        except AssertionError:
            raise ConfigurationError('Expected tuple or list of attribute names')

        # Make sure there are no conflicts with data_attribute_names
        data_attribute_names = cls._data_attribute_names_flat
        for invalid_key in ['register', 'get', 'value', 'members', 'data_attribute_names']:
            try:
                assert invalid_key not in data_attribute_names
            except AssertionError:
                raise ConfigurationError('Unexpected data attribute name "{}"'.format(invalid_key))

        # Disallow underscores in attribute names
        try:
            assert not any(key.startswith('_') for key in data_attribute_names)
        except AssertionError:
            raise ConfigurationError('Unexpected data attribute prefix "_"')

        # Set this here so that each type definition gets their own set.
        cls.members = set()

    def __getattr__(cls, attr):
        """Enable attribute syntax for member lookup."""
        members_by_value = cls._get_member_dict_by_attr('value')
        try:
            return members_by_value[attr]
        except KeyError:
            raise AttributeError('"{}" has no attribute "{}"'.format(cls.__name__, attr))

    def _get_member_dict_by_attr(cls, attr):
        """Return the members as a dictionary.

        The dictionary can be ordered by any unique attribute or 'value'.
        """
        try:
            assert attr == 'value' or attr in cls._data_attribute_names_flat_unique
        except AssertionError:
            raise AttributeError('"{}" has no attribute "{}"'.format(cls.__name__, attr))

        return {getattr(obj, attr): obj for obj in cls.members}

    @property
    def _data_attribute_names_flat(cls):
        """Return a flat list of data attribute names.

        `data_attribute_names` accepts tuples in the form of ('name', True)
        which would mark the attribute 'name' as unique, and therefore
        available for member lookup.

        This flattens those tuples for internal use, ignoring the second value
        of the tuple.
        """
        flat_names = []
        for name in cls.data_attribute_names:
            if type(name) in (tuple, list):
                flat_names.append(name[0])
            else:
                flat_names.append(name)
        return tuple(flat_names)

    @property
    def _data_attribute_names_flat_unique(cls):
        """Return a flat list of unique data attribute names.

        `data_attribute_names` accepts tuples in the form of ('name', True)
        which would mark the attribute 'name' as unique, and therefore
        available for member lookup.

        This returns only the names of data attributes which have been marked
        as unique.
        """
        flat_names = []
        for name in cls.data_attribute_names:
            if type(name) in (tuple, list) and name[1]:
                flat_names.append(name[0])
        return tuple(flat_names)


class DataEnum(six.with_metaclass(DataEnumType, object)):
    data_attribute_names = ()

    _is_registered = False

    @classmethod
    def register(cls, members):
        """Add the members to the DataEnum.

        Call this method once, immediately after the class definition, with all
        of the initialized members of the DataEnum.
        """
        # Only allow registration once
        try:
            assert not cls._is_registered
        except AssertionError:
            raise ConfigurationError('Enum members have already been registered')

        """Make sure there are unique values for attributes which have been
        marked unique, including 'value'."""
        unique_attribute_names = ('value',) + cls._data_attribute_names_flat_unique
        for attr in unique_attribute_names:
            for value, grouper in groupby(members, key=lambda m: getattr(m, attr)):
                # Group by the value of the attribute
                group_list = list(grouper)

                # Make sure the value isn't repeated
                try:
                    assert len(group_list) == 1
                except AssertionError:
                    raise ValueError('Duplicate enum value "{}" for unique attribute "{}"'.format(value, attr))

        for member in members:
            cls.members.add(member)

        # Mark the enum as registered so that no more members can be added.
        cls._is_registered = True

    @classmethod
    def get(cls, *args, **kwargs):
        """Look up a member of the enumeration."""
        has_default = False

        if len(args) == 2:
            # Two positional arguments; the second one is the default
            has_default = True
            # A default exists, even if it's None
            default = args[1]
            args = args[:1]
        else:
            # No positional default; look for a keyword-based default
            try:
                default = kwargs.pop('default')
            except KeyError:
                # No default; will throw an error if the member can't be found
                pass
            else:
                # A default exists, even if it's None
                has_default = True

        if len(args) == 1 and not kwargs:
            # Look up by value
            attr = 'value'
            value = args[0]
        elif len(kwargs) == 1 and not args:
            # Look up by attribute or value
            attr = next(iter(kwargs))
            value = kwargs[attr]
        else:
            raise TypeError('Unexpected argument count')

        member_dict = cls._get_member_dict_by_attr(attr)
        try:
            # Return the member
            return member_dict[value]
        except KeyError:
            try:
                assert has_default
            except AssertionError:
                # No default available
                raise MemberDoesNotExistError()

            # Return the passed-in default
            return default

    def __init__(self, *args, **kwargs):
        # Make sure member isn't being initialized after initial registration
        try:
            assert not self._is_registered
        except AssertionError:
            raise ConfigurationError('Cannot initialize DataEnum member after registration')

        # Make sure member was given a value
        try:
            assert args
        except AssertionError:
            raise TypeError('Expected unique value as first argument')

        args_list = list(args)

        # The first argument is the value
        self.value = args_list.pop(0)

        num_args = len(args_list)

        # Get a list of data attribute names
        data_attribute_names_flat = type(self)._data_attribute_names_flat
        num_attributes = len(data_attribute_names_flat)

        # Make sure there aren't too many positional args
        try:
            assert num_args <= num_attributes
        except AssertionError:
            raise TypeError('Expected {} data attributes; got {}'.format(num_attributes, num_args))

        # Set the values for each positional attribute directly on the member
        for i in range(num_args):
            setattr(self, data_attribute_names_flat[i], args_list[i])

        # Make sure there are enough keyword arguments
        num_kwargs = len(kwargs)

        remaining_attribute_names = data_attribute_names_flat[num_args:]
        num_remaining_attributes = len(remaining_attribute_names)
        try:
            assert num_kwargs >= num_remaining_attributes
        except AssertionError:
            missing_attribute_names = [
                attribute_name
                for attribute_name in remaining_attribute_names
                if attribute_name not in kwargs
            ]
            raise TypeError('Expected data attributes: {}'.format(', '.join(missing_attribute_names)))

        for kw, value in six.iteritems(kwargs):
            # Ensure no keyword arguments for attributes that don't exist
            try:
                assert kw in remaining_attribute_names
            except AssertionError:
                raise TypeError('Unexpected data attribute: {}'.format(kw))

            # Set the value for the keyword attribute on the member
            setattr(self, kw, value)

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
            return True

    def __hash__(self):
        return hash(self.value)

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return self.value

    def __int__(self):
        return self.value

"""An alternative to the built-in Python `enum` implementation."""


class ConfigurationError(Exception):
    """An error to be thrown when DataEnum is not set up correctly."""


class MemberDoesNotExistError(Exception):
    """An error to be thrown when the requested member does not exist."""


DEFAULT_PRIMARY_ATTRIBUTE = "_id_"


class DataEnumType(type):
    """Metaclass for custom class-level functionality for DataEnum."""

    def __init__(cls, *args):
        """Define the new type in place."""
        cls.primary_attribute = getattr(cls, "primary_attribute", DEFAULT_PRIMARY_ATTRIBUTE)

        if not isinstance(getattr(cls, "data_attributes", ()), (tuple, list)):
            # Expected data_attributes to be a tuple or list, if provided
            raise ConfigurationError("Expected tuple or list of attribute names")

        # Make sure there are no conflicts with data_attributes
        data_attrs = cls._data_attrs_flat
        invalid_keys = (
            cls.primary_attribute,
            "get",
            "members",
            "data_attributes",
            "primary_attribute",
        )
        for invalid_key in invalid_keys:
            if invalid_key in data_attrs:
                raise ConfigurationError(f'Unexpected data attribute name "{invalid_key}"')

        # Disallow underscores in attribute names
        if any(key.startswith("_") for key in data_attrs):
            raise ConfigurationError('Unexpected data attribute prefix "_"')

        # Set this here so that each type definition gets their own set.
        cls.members = []

    def _get_member_dict_by_attr(cls, attr):
        """Return the members as a dictionary.

        The dictionary can be ordered by any unique attribute or the primary
        key attribute.
        """
        if attr != cls.primary_attribute and attr not in cls._data_attrs_flat_unique:
            raise AttributeError('"{}" has no attribute "{}"'.format(cls.__name__, attr))

        return {getattr(member, attr): member for member in cls.members}

    @property
    def _data_attrs_flat(cls):
        """Return a flat list of data attribute names.

        `data_attributes` accepts tuples in the form of ('name', True)
        which would mark the attribute 'name' as unique, and therefore
        available for member lookup.

        This flattens those tuples for internal use, ignoring the second value
        of the tuple.
        """
        flat_names = []
        for name in getattr(cls, "data_attributes", ()):
            if isinstance(name, (tuple, list)):
                flat_names.append(name[0])
            else:
                flat_names.append(name)
        return tuple(flat_names)

    @property
    def _data_attrs_flat_unique(cls):
        """Return a flat list of unique data attribute names.

        `data_attributes` accepts tuples in the form of ('name', True)
        which would mark the attribute 'name' as unique, and therefore
        available for member lookup.

        This returns only the names of data attributes which have been marked
        as unique.
        """
        flat_names = []
        for name in getattr(cls, "data_attributes", ()):
            if isinstance(name, (tuple, list)) and name[1]:
                flat_names.append(name[0])
        return tuple(flat_names)


class DataEnum(metaclass=DataEnumType):
    """An implementation of Enum that allows attached static data."""

    def __init__(self, *args, **kwargs):
        """Initialize the DataEnum."""
        self.is_auto = False

        args_list = list(args)
        if args_list:
            # The first argument is the primary key
            member_id = args_list.pop(0)
        else:
            try:
                # The primary key was passed by name
                member_id = kwargs.pop(self._primary_attr)
            except KeyError:
                # Auto-generate a primary key
                member_id = len(self.members)
                self.is_auto = True

        setattr(self, self._primary_attr, member_id)

        num_args = len(args_list)

        # Get a list of data attribute names
        data_attrs_flat = type(self)._data_attrs_flat
        num_attrs = len(data_attrs_flat)

        # Make sure there aren't too many positional args
        if num_args > num_attrs:
            raise TypeError(f"Expected {num_attrs} data attributes; got {num_args}")

        # Set the values for each positional attribute directly on the member
        for arg_index in range(num_args):
            setattr(self, data_attrs_flat[arg_index], args_list[arg_index])

        # Make sure there are enough keyword arguments
        num_kwargs = len(kwargs)

        remaining_attrs = data_attrs_flat[num_args:]
        num_remaining_attrs = len(remaining_attrs)
        if num_kwargs < num_remaining_attrs:
            missing_attrs = [attr for attr in remaining_attrs if attr not in kwargs]
            raise TypeError("Expected data attributes: {}".format(", ".join(missing_attrs)))

        for keyword, value in kwargs.items():
            # Ensure no keyword arguments for attributes that don't exist
            if keyword not in remaining_attrs:
                raise TypeError(f"Unexpected data attribute: {keyword}")

            # Set the value for the keyword attribute on the member
            setattr(self, keyword, value)

        # Check for a duplicate value for a unique attribute
        unique_attrs = (self._primary_attr,) + type(self)._data_attrs_flat_unique
        for attr in unique_attrs:
            value = getattr(self, attr)

            for member in self.members:
                if value == getattr(member, attr):
                    raise ValueError(
                        f'Duplicate enum value "{value}" for unique attribute "{attr}"',
                    )

        self.members.append(self)

    @classmethod
    def get(cls, *args, **kwargs):
        """Look up a member of the enumeration."""
        has_default = False
        should_bail_if_auto = False

        if len(args) == 2:
            # Two positional arguments; the second one is the default
            has_default = True
            # A default exists, even if it's None
            default = args[1]
            args = args[:1]
        else:
            # No positional default; look for a keyword-based default
            try:
                default = kwargs.pop("default")
            except KeyError:
                # No default; will throw an error if the member can't be found
                pass
            else:
                # A default exists, even if it's None
                has_default = True

        if len(args + tuple(kwargs.items())) != 1:
            raise TypeError("Unexpected arguments")

        if args:
            # Look up by primary key
            attr = cls.primary_attribute
            if attr == DEFAULT_PRIMARY_ATTRIBUTE:
                # Don't expose the default ID if it's auto generated
                should_bail_if_auto = True

            value = args[0]
        else:
            # Look up by attribute or id
            attr = next(iter(kwargs))
            if attr == DEFAULT_PRIMARY_ATTRIBUTE:
                # Don't expose the default ID by keyword
                raise AttributeError('Attribute "{}" not found'.format(cls.primary_attribute))

            value = kwargs[attr]

        member_dict = cls._get_member_dict_by_attr(attr)
        try:
            # Return the member
            member = member_dict[value]
        except KeyError:
            if not has_default:
                # No default available
                raise MemberDoesNotExistError()

            # Return the passed-in default
            return default

        if member.is_auto and should_bail_if_auto:
            # Don't expose the default ID if it's auto generated
            raise MemberDoesNotExistError()

        return member

    def __eq__(self, other):
        """Determine whether two members are equal based on their ID."""
        try:
            return self._member_id == other._member_id
        except AttributeError:
            return False

    def __hash__(self):
        """Return a hash of only the ID, since that's what's needed for EQ."""
        return hash(self._member_id)

    def __str__(self):
        """Return the member ID as a string."""
        return str(self._member_id)

    def __int__(self):
        """Return the member ID as an int, if it can be cast to one."""
        return int(self._member_id)

    def __repr__(self):
        """Return a full python-friendly representation of the member."""
        enum_type = type(self)
        attr_values = ((attr, getattr(self, attr)) for attr in enum_type._data_attrs_flat)
        return "{type}({pk}{args})".format(
            type=enum_type.__name__,
            pk=repr(self._member_id),
            args="".join((", {}={}".format(attr, repr(value)) for (attr, value) in attr_values)),
        )

    @property
    def _primary_attr(self):
        return type(self).primary_attribute

    @property
    def _member_id(self):
        return getattr(self, self._primary_attr)

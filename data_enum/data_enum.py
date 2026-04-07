"""An alternative to the built-in Python `enum` implementation."""

from __future__ import annotations

from typing import Annotated, Any, dataclass_transform, get_args, get_origin

_MISSING = object()

UNIQUE = object()


class UniqueTogether:
    """Marker for composite unique constraints in Annotated type hints.

    Attributes sharing the same group name form a composite unique constraint.
    """

    __slots__ = ("group",)

    def __init__(self, group: str) -> None:
        """Store the group name."""
        self.group = group


class ConfigurationError(Exception):
    """An error to be thrown when DataEnum is not set up correctly."""


class MemberDoesNotExistError(Exception):
    """An error to be thrown when the requested member does not exist."""


@dataclass_transform(kw_only_default=True)
class DataEnumMeta(type):
    """Metaclass for DataEnum that handles member registration and lookup."""

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs: Any,  # noqa: ANN401
    ) -> DataEnumMeta:
        """Create a new DataEnum class."""
        # Don't process the base DataEnum class itself
        is_enum_subclass = any(isinstance(base, DataEnumMeta) for base in bases)
        if not is_enum_subclass:
            return super().__new__(mcs, name, bases, namespace)

        # Prevent subclassing a concrete enum
        for base in bases:
            if isinstance(base, DataEnumMeta) and hasattr(base, "_members_decl"):
                raise ConfigurationError(
                    f"Cannot subclass {base.__name__}",
                )

        # Extract __members__
        members_decl = namespace.pop("__members__", None)
        if members_decl is None:
            raise ConfigurationError("__members__ must be defined")
        if not isinstance(members_decl, tuple):
            raise ConfigurationError("__members__ must be a tuple")
        if len(members_decl) != len(set(members_decl)):
            raise ConfigurationError("__members__ contains duplicate names")

        reserved = frozenset(("get", "filter", "members"))
        for member_name in members_decl:
            if not isinstance(member_name, str) or not member_name.isidentifier():
                raise ConfigurationError(
                    f"Invalid member name: {member_name!r}",
                )
            if member_name.startswith("_"):
                raise ConfigurationError(
                    f"Member name must not start with underscore: {member_name!r}",
                )
            if member_name in reserved:
                raise ConfigurationError(
                    f"Member name conflicts with reserved name: {member_name!r}",
                )

        # Parse annotations to find data attributes.
        # Python 3.14+ (PEP 749) stores annotations via __annotate_func__
        # instead of __annotations__ in the class namespace.
        annotate_func = namespace.get("__annotate_func__")
        if annotate_func is None:
            annotations = namespace.get("__annotations__", {})
        else:
            annotations = annotate_func(1)  # FORMAT_VALUE = 1

        data_attrs: dict[str, type] = {}
        unique_attrs: set[str] = set()
        default_attrs: dict[str, Any] = {}
        unique_together_map: dict[str, list[str]] = {}  # group -> [attr_names]

        for attr_name, annotation in annotations.items():
            if attr_name.startswith("_"):
                continue
            if get_origin(annotation) is Annotated:
                args = get_args(annotation)
                if UNIQUE in args:
                    unique_attrs.add(attr_name)
                for arg in args[1:]:
                    if isinstance(arg, UniqueTogether):
                        unique_together_map.setdefault(arg.group, []).append(attr_name)
                data_attrs[attr_name] = args[0]
            else:
                data_attrs[attr_name] = annotation

        # Extract defaults from namespace values (field: type = value syntax)
        for attr_name in data_attrs:
            if attr_name in namespace:
                default_attrs[attr_name] = namespace.pop(attr_name)

        # Validate unique-together groups have at least 2 attributes
        for group_name, group_attrs in unique_together_map.items():
            if len(group_attrs) < 2:  # noqa: PLR2004
                raise ConfigurationError(
                    f"UniqueTogether group {group_name!r} must have at least 2 attributes; "
                    f"found only {group_attrs[0]!r}. Use UNIQUE for single-attribute uniqueness",
                )

        for attr_name in data_attrs:
            if attr_name in reserved:
                raise ConfigurationError(
                    f"Attribute name conflicts with reserved name: {attr_name!r}",
                )

        # Add __slots__ for the data attributes plus the internal _name
        namespace["__slots__"] = (*data_attrs, "_name")
        # Remove annotations so they don't conflict with slots
        namespace.pop("__annotations__", None)
        namespace.pop("__annotate_func__", None)

        enum_cls = super().__new__(mcs, name, bases, namespace)

        # Freeze unique-together groups as tuples (preserving annotation order)
        unique_together_groups: dict[str, tuple[str, ...]] = {
            gn: tuple(ga) for gn, ga in unique_together_map.items()
        }
        # Build a reverse lookup: frozenset of attr names -> group name
        unique_together_by_attrs: dict[frozenset[str], str] = {
            frozenset(ga): gn for gn, ga in unique_together_groups.items()
        }

        enum_cls._data_attrs = data_attrs
        enum_cls._unique_attrs = frozenset(unique_attrs)
        enum_cls._default_attrs = default_attrs
        enum_cls._unique_together_groups = unique_together_groups
        enum_cls._unique_together_by_attrs = unique_together_by_attrs
        enum_cls._members_decl = members_decl
        enum_cls._member_map: dict[str, DataEnum] = {}
        enum_cls._unique_indexes: dict[str, dict[Any, DataEnum]] = {ua: {} for ua in unique_attrs}
        enum_cls._unique_together_indexes: dict[str, dict[tuple[Any, ...], DataEnum]] = {
            gn: {} for gn in unique_together_groups
        }
        enum_cls._non_unique_indexes: dict[str, dict[Any, frozenset[DataEnum]]] = {
            da: {} for da in data_attrs if da not in unique_attrs
        }
        enum_cls._is_complete = len(members_decl) == 0
        enum_cls._instances_created = 0

        return enum_cls

    def __setattr__(cls, name: str, value: Any) -> None:  # noqa: ANN401
        """Intercept member assignment on the class."""
        if hasattr(cls, "_members_decl") and name in cls._members_decl:
            if name in cls._member_map:
                raise ConfigurationError(f"Member {name!r} is already defined")
            if not isinstance(value, cls):
                raise ConfigurationError(
                    f"Member {name!r} must be an instance of {cls.__name__}",
                )
            if hasattr(value, "_name"):
                raise ConfigurationError(
                    f"This instance is already assigned to member {value._name!r}; "  # noqa: SLF001
                    f"create a new instance for {name!r}",
                )

            # Set the internal name
            object.__setattr__(value, "_name", name)
            cls._member_map[name] = value

            # Index unique attributes
            for attr in cls._unique_attrs:
                attr_value = getattr(value, attr)
                attr_index = cls._unique_indexes[attr]
                if attr_value in attr_index:
                    raise ConfigurationError(
                        f"Duplicate value {attr_value!r} for unique attribute {attr!r}",
                    )
                attr_index[attr_value] = value

            # Index unique-together groups
            for group_name, group_attrs in cls._unique_together_groups.items():
                composite_key = tuple(getattr(value, ga) for ga in group_attrs)
                group_index = cls._unique_together_indexes[group_name]
                if composite_key in group_index:
                    attr_desc = ", ".join(f"{ga}={getattr(value, ga)!r}" for ga in group_attrs)
                    raise ConfigurationError(
                        f"Duplicate values for unique-together group {group_name!r}: {attr_desc}",
                    )
                group_index[composite_key] = value

            # Index non-unique attributes
            for attr in cls._non_unique_indexes:
                attr_value = getattr(value, attr)
                bucket = cls._non_unique_indexes[attr]
                if attr_value not in bucket:
                    bucket[attr_value] = set()
                bucket[attr_value].add(value)

            # Check completeness
            if len(cls._member_map) == len(cls._members_decl):
                # Freeze non-unique index sets
                for attr in cls._non_unique_indexes:
                    cls._non_unique_indexes[attr] = {
                        key: frozenset(members)
                        for key, members in cls._non_unique_indexes[attr].items()
                    }
                cls._is_complete = True

            type.__setattr__(cls, name, value)
        else:
            # Prevent assigning enum instances to non-member names
            if hasattr(cls, "_members_decl") and isinstance(value, cls):
                raise ConfigurationError(
                    f"{name!r} is not a declared member of {cls.__name__}; add it to __members__",
                )
            type.__setattr__(cls, name, value)

    @property
    def members(cls) -> tuple[DataEnum, ...]:
        """Return all members in declaration order."""
        cls._ensure_complete()
        return tuple(cls._member_map[name] for name in cls._members_decl)


class DataEnum(metaclass=DataEnumMeta):  # noqa: WPS338
    """An alternative to the built-in Python `enum` implementation."""

    __slots__ = ()

    def __init__(self, **kwargs: Any) -> None:  # noqa: ANN401
        """Initialize a DataEnum member."""
        enum_cls = type(self)
        data_attrs = enum_cls._data_attrs  # noqa: SLF001

        # Enforce that no more instances are created than declared members
        max_members = len(enum_cls._members_decl)  # noqa: SLF001
        if enum_cls._instances_created >= max_members:  # noqa: SLF001
            raise ConfigurationError(
                f"{enum_cls.__name__} already has {max_members} "
                f"instance(s) (matching __members__); cannot create more",
            )
        enum_cls._instances_created += 1  # noqa: SLF001

        extra = set(kwargs) - set(data_attrs)
        if extra:
            raise TypeError(
                "Unknown attributes: {}".format(", ".join(sorted(extra))),
            )

        # Apply defaults for missing attributes
        defaults = enum_cls._default_attrs  # noqa: SLF001
        for attr_name, default_value in defaults.items():
            if attr_name not in kwargs:
                kwargs[attr_name] = default_value

        missing = set(data_attrs) - set(kwargs)
        if missing:
            raise TypeError(
                "Missing required attributes: {}".format(", ".join(sorted(missing))),
            )

        for attr, attr_value in kwargs.items():
            object.__setattr__(self, attr, attr_value)

    def __setattr__(self, name: str, value: Any) -> None:  # noqa: ANN401
        """Prevent modification of member attributes."""
        raise AttributeError(
            f"{type(self).__name__} members are immutable",
        )

    def __delattr__(self, name: str) -> None:  # noqa: WPS603
        """Prevent deletion of member attributes."""
        raise AttributeError(
            f"{type(self).__name__} members are immutable",
        )

    def __eq__(self, other: object) -> bool:
        """Members are equal only if they are the same object."""
        return self is other

    def __hash__(self) -> int:
        """Hash by class and member name."""
        return hash((type(self).__name__, self._name))

    def __repr__(self) -> str:
        """Return e.g. 'Currency.USD'."""
        return f"{type(self).__name__}.{self._name}"

    def __str__(self) -> str:
        """Return the member name, e.g. 'USD'."""
        return self._name

    def __reduce__(self) -> tuple[Any, ...]:  # noqa: WPS603
        """Support pickling by reconstituting via get()."""
        return (type(self).get, (self._name,))

    @classmethod
    def _ensure_complete(cls) -> None:
        if cls._is_complete:
            return

        missing = set(cls._members_decl) - set(cls._member_map)
        defined = set(cls._member_map)
        if defined:
            msg = (
                f"{cls.__name__} is not fully defined. "
                f"Missing members: {', '.join(sorted(missing))}"
            )
        else:
            msg = f"{cls.__name__} is not fully defined. No members have been assigned yet"
        raise ConfigurationError(msg)

    @classmethod
    def get(
        cls,
        _name: Any = _MISSING,  # noqa: ANN401
        /,
        *,
        default: Any = _MISSING,  # noqa: ANN401
        **kwargs: Any,  # noqa: ANN401
    ) -> Any:  # noqa: ANN401
        """Look up a member by name or unique attribute."""
        cls._ensure_complete()

        if _name is not _MISSING and kwargs:
            raise TypeError(
                "Cannot combine positional name with keyword attribute lookup",
            )

        if _name is not _MISSING:
            # Name lookup
            return cls._get_by_name(_name, default)

        if len(kwargs) == 1:
            attr, attr_value = next(iter(kwargs.items()))
            if attr not in cls._unique_attrs:
                raise TypeError(
                    f"{attr!r} is not a unique attribute of {cls.__name__}",
                )
            return cls._get_by_unique_attr(attr, attr_value, default)

        # Multiple kwargs: check for unique-together group match
        kwarg_keys = frozenset(kwargs)
        group_name = cls._unique_together_by_attrs.get(kwarg_keys)
        if group_name is not None:
            return cls._get_by_unique_together(group_name, kwargs, default)

        if not kwargs:
            raise TypeError(
                "get() requires a member name, a unique attribute, "
                "or a unique-together attribute group",
            )

        raise TypeError(
            f"No unique or unique-together constraint matches "
            f"attributes: {', '.join(sorted(kwargs))}",
        )

    @classmethod
    def filter(cls, **kwargs: Any) -> frozenset[Any]:  # noqa: ANN401
        """Look up members by any attribute.

        Returns a frozenset.
        """
        cls._ensure_complete()

        if len(kwargs) != 1:
            raise TypeError("filter() requires exactly one keyword argument")

        attr, attr_value = next(iter(kwargs.items()))
        if attr not in cls._data_attrs:
            raise TypeError(
                f"{attr!r} is not an attribute of {cls.__name__}",
            )

        # For unique attrs, check the unique index
        if attr in cls._unique_attrs:
            return (
                cls._unique_indexes[attr].get(attr_value, _MISSING) is not _MISSING
                and frozenset(  # noqa: E501
                    (cls._unique_indexes[attr][attr_value],),
                )
            ) or frozenset()

        # For non-unique attrs, check the non-unique index
        return cls._non_unique_indexes[attr].get(attr_value, frozenset())

    @classmethod
    def _get_by_name(cls, name: Any, default: Any) -> Any:  # noqa: ANN401
        """Look up a member by its declared name."""
        member = cls._member_map.get(name, _MISSING)
        if member is not _MISSING:
            return member
        if default is not _MISSING:
            return default
        raise MemberDoesNotExistError(
            f"{cls.__name__} has no member {name!r}",
        )

    @classmethod
    def _get_by_unique_attr(cls, attr: str, attr_value: Any, default: Any) -> Any:  # noqa: ANN401
        """Look up a member by a unique attribute value."""
        member = cls._unique_indexes[attr].get(attr_value, _MISSING)
        if member is not _MISSING:
            return member
        if default is not _MISSING:
            return default
        raise MemberDoesNotExistError(
            f"No {cls.__name__} with {attr}={attr_value!r}",
        )

    @classmethod
    def _get_by_unique_together(
        cls,
        group_name: str,
        kwargs: dict[str, Any],
        default: Any,  # noqa: ANN401
    ) -> Any:  # noqa: ANN401
        """Look up a member by a unique-together composite key."""
        group_attrs = cls._unique_together_groups[group_name]
        composite_key = tuple(kwargs[attr] for attr in group_attrs)
        group_index = cls._unique_together_indexes[group_name]
        member = group_index.get(composite_key, _MISSING)
        if member is not _MISSING:
            return member
        if default is not _MISSING:
            return default
        attr_desc = ", ".join(f"{attr}={kwargs[attr]!r}" for attr in group_attrs)
        raise MemberDoesNotExistError(
            f"No {cls.__name__} with {attr_desc}",
        )

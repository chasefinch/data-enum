"""Tests for DataEnum."""

# Standard Library
import pickle
from typing import Annotated

# Third Party
import pytest

# Data Enum
from data_enum import (
    UNIQUE,
    ConfigurationError,
    DataEnum,
    Default,
    MemberDoesNotExistError,
    UniqueTogether,
)


class Currency(DataEnum):
    """A test enum representing currencies."""

    __members__ = ("USD", "EUR", "GBP", "JPY", "CAD", "AUD")

    symbol: str
    name: str
    code: Annotated[str, UNIQUE]
    plural_name: str


Currency.USD = Currency(symbol="$", name="US Dollar", code="USD", plural_name="US Dollars")
Currency.EUR = Currency(symbol="€", name="Euro", code="EUR", plural_name="Euros")
Currency.GBP = Currency(
    symbol="£",
    name="Pound Sterling",
    code="GBP",
    plural_name="Pounds Sterling",
)
Currency.JPY = Currency(symbol="¥", name="Japanese Yen", code="JPY", plural_name="Japanese Yen")
Currency.CAD = Currency(
    symbol="$",
    name="Canadian Dollar",
    code="CAD",
    plural_name="Canadian Dollars",
)
Currency.AUD = Currency(
    symbol="$",
    name="Australian Dollar",
    code="AUD",
    plural_name="Australian Dollars",
)


class TestConfiguration:
    """Test class definition and configuration errors."""

    def test_missing_members(self) -> None:
        with pytest.raises(ConfigurationError, match="__members__ must be defined"):

            class Bad(DataEnum):
                name: str

    def test_members_not_tuple(self) -> None:
        with pytest.raises(ConfigurationError, match="__members__ must be a tuple"):

            class Bad(DataEnum):
                __members__ = ["A", "B"]
                name: str

    def test_duplicate_member_names(self) -> None:
        with pytest.raises(ConfigurationError, match="duplicate names"):

            class Bad(DataEnum):
                __members__ = ("A", "A")
                name: str

    def test_invalid_member_name(self) -> None:
        with pytest.raises(ConfigurationError, match="Invalid member name"):

            class Bad(DataEnum):
                __members__ = ("123bad",)
                name: str

    def test_underscore_member_name(self) -> None:
        with pytest.raises(ConfigurationError, match="underscore"):

            class Bad(DataEnum):
                __members__ = ("_HIDDEN",)
                name: str

    def test_reserved_member_name(self) -> None:
        with pytest.raises(ConfigurationError, match="reserved"):

            class Bad(DataEnum):
                __members__ = ("get",)
                name: str

    def test_no_data_attrs(self) -> None:
        class PureEnum(DataEnum):
            __members__ = ("A", "B")

        PureEnum.A = PureEnum()
        PureEnum.B = PureEnum()
        assert PureEnum.get("A") is PureEnum.A
        assert PureEnum.members == (PureEnum.A, PureEnum.B)

    def test_private_annotations_ignored(self) -> None:
        class WithPrivate(DataEnum):
            __members__ = ("A",)
            _internal: str
            name: str

        WithPrivate.A = WithPrivate(name="Alpha")
        assert WithPrivate.A.name == "Alpha"
        assert not hasattr(WithPrivate.A, "_internal")

    def test_reserved_attr_name(self) -> None:
        with pytest.raises(ConfigurationError, match="reserved"):

            class Bad(DataEnum):
                __members__ = ("A",)
                members: str

    def test_cannot_subclass_enum(self) -> None:
        with pytest.raises(ConfigurationError, match="Cannot subclass"):

            class Bad(Currency):
                __members__ = ("X",)
                extra: str


class TestMemberAssignment:
    """Test member registration and validation."""

    def test_duplicate_member(self) -> None:
        class Color(DataEnum):
            __members__ = ("RED", "BLUE", "GREEN")
            name: str

        Color.RED = Color(name="Red")
        with pytest.raises(ConfigurationError, match="already defined"):
            Color.RED = Color(name="Also Red")

    def test_wrong_type(self) -> None:
        class Color(DataEnum):
            __members__ = ("RED",)
            name: str

        with pytest.raises(ConfigurationError, match="must be an instance"):
            Color.RED = "not an enum"

    def test_duplicate_unique_value(self) -> None:
        class Color(DataEnum):
            __members__ = ("RED", "BLUE")
            name: str
            hex_code: Annotated[str, UNIQUE]

        Color.RED = Color(name="Red", hex_code="#FF0000")
        with pytest.raises(ConfigurationError, match="Duplicate value"):
            Color.BLUE = Color(name="Blue", hex_code="#FF0000")

    def test_non_member_class_attr(self) -> None:
        """Assigning a non-enum value to a non-member name is fine."""

        class Color(DataEnum):
            __members__ = ("RED",)
            name: str

        Color.EXTRA = "some value"
        assert Color.EXTRA == "some value"

    def test_instance_to_non_member_name(self) -> None:
        """Assigning an enum instance to a non-member name raises."""

        class Color(DataEnum):
            __members__ = ("RED",)
            name: str

        with pytest.raises(ConfigurationError, match="not a declared member"):
            Color.BLUE = Color(name="Blue")

    def test_double_assign_instance(self) -> None:
        """Cannot assign the same instance to two member names."""

        class Color(DataEnum):
            __members__ = ("RED", "BLUE")
            name: str

        instance = Color(name="Red")
        Color.RED = instance
        with pytest.raises(ConfigurationError, match="already assigned"):
            Color.BLUE = instance

    def test_too_many_instances(self) -> None:
        """Cannot create more instances than declared members."""

        class Color(DataEnum):
            __members__ = ("RED",)
            name: str

        Color.RED = Color(name="Red")
        with pytest.raises(ConfigurationError, match="cannot create more"):
            Color(name="Extra")

    def test_immutable_members(self) -> None:
        with pytest.raises(AttributeError, match="immutable"):
            Currency.USD.name = "Bitcoin"

    def test_immutable_delete(self) -> None:
        with pytest.raises(AttributeError, match="immutable"):
            del Currency.USD.name  # noqa: WPS420


class TestInit:
    """Test member instance creation."""

    def test_missing_attr(self) -> None:
        class Color(DataEnum):
            __members__ = ("RED",)
            name: str
            hex_code: str

        with pytest.raises(TypeError, match="Missing required"):
            Color.RED = Color(name="Red")

    def test_extra_attr(self) -> None:
        class Color(DataEnum):
            __members__ = ("RED",)
            name: str

        with pytest.raises(TypeError, match="Unknown"):
            Color.RED = Color(name="Red", extra="bad")

    def test_keyword_only(self) -> None:
        class Color(DataEnum):
            __members__ = ("RED",)
            name: str

        with pytest.raises(TypeError):
            Color("Red")


class TestGet:
    """Test member lookup."""

    def test_get_by_name(self) -> None:
        assert Currency.get("USD") is Currency.USD
        assert Currency.get("EUR") is Currency.EUR

    def test_get_by_unique_attr(self) -> None:
        assert Currency.get(code="USD") is Currency.USD
        assert Currency.get(code="GBP") is Currency.GBP

    def test_get_name_default(self) -> None:
        assert Currency.get("MISSING", default=None) is None
        assert Currency.get("MISSING", default=Currency.USD) is Currency.USD

    def test_get_unique_default(self) -> None:
        assert Currency.get(code="MISSING", default=None) is None
        assert Currency.get(code="MISSING", default=Currency.USD) is Currency.USD

    def test_get_name_not_found(self) -> None:
        with pytest.raises(MemberDoesNotExistError, match="no member"):
            Currency.get("MISSING")

    def test_get_unique_not_found(self) -> None:
        with pytest.raises(MemberDoesNotExistError, match="No Currency"):
            Currency.get(code="MISSING")

    def test_get_non_unique_attr_rejected(self) -> None:
        with pytest.raises(TypeError, match="not a unique attribute"):
            Currency.get(symbol="$")

    def test_get_no_args(self) -> None:
        with pytest.raises(TypeError, match="requires a member name"):
            Currency.get()

    def test_get_mixed_args(self) -> None:
        with pytest.raises(TypeError, match="Cannot combine"):
            Currency.get("USD", code="USD")

    def test_get_multiple_kwargs(self) -> None:
        with pytest.raises(TypeError, match="No unique"):
            Currency.get(code="USD", name="US Dollar")

    def test_get_before_complete(self) -> None:
        class Color(DataEnum):
            __members__ = ("RED", "BLUE")
            name: str

        Color.RED = Color(name="Red")
        with pytest.raises(ConfigurationError, match="not fully defined"):
            Color.get("RED")

    def test_get_no_members_assigned(self) -> None:
        class Color(DataEnum):
            __members__ = ("RED",)
            name: str

        with pytest.raises(ConfigurationError, match="No members have been assigned"):
            Color.get("RED")


class TestFilter:
    """Test non-unique attribute lookup."""

    def test_filter_non_unique(self) -> None:
        result = Currency.filter(symbol="$")
        assert isinstance(result, frozenset)
        assert Currency.USD in result
        assert Currency.CAD in result
        assert Currency.AUD in result
        assert len(result) == 3

    def test_filter_no_match(self) -> None:
        result = Currency.filter(symbol="₿")
        assert result == frozenset()

    def test_filter_unique_attr(self) -> None:
        result = Currency.filter(code="USD")
        assert result == frozenset((Currency.USD,))

    def test_filter_unique_no_match(self) -> None:
        result = Currency.filter(code="MISSING")
        assert result == frozenset()

    def test_filter_invalid_attr(self) -> None:
        with pytest.raises(TypeError, match="not an attribute"):
            Currency.filter(bad_attr="x")

    def test_filter_no_args(self) -> None:
        with pytest.raises(TypeError, match="exactly one keyword"):
            Currency.filter()

    def test_filter_multiple_args(self) -> None:
        with pytest.raises(TypeError, match="exactly one keyword"):
            Currency.filter(symbol="$", name="US Dollar")

    def test_filter_before_complete(self) -> None:
        class Color(DataEnum):
            __members__ = ("RED", "BLUE")
            name: str

        Color.RED = Color(name="Red")
        with pytest.raises(ConfigurationError, match="not fully defined"):
            Color.filter(name="Red")


class TestMembers:
    """Test the members property."""

    def test_members_order(self) -> None:
        assert Currency.members == (
            Currency.USD,
            Currency.EUR,
            Currency.GBP,
            Currency.JPY,
            Currency.CAD,
            Currency.AUD,
        )

    def test_members_before_complete(self) -> None:
        class Color(DataEnum):
            __members__ = ("RED", "BLUE")
            name: str

        Color.RED = Color(name="Red")
        with pytest.raises(ConfigurationError, match="not fully defined"):
            Color.members  # noqa: B018

    def test_empty_enum(self) -> None:
        class Empty(DataEnum):
            __members__ = ()
            name: str

        assert Empty.members == ()


class TestSpecialMethods:
    """Test __eq__, __hash__, __repr__, __str__, __reduce__."""

    def test_eq_identity(self) -> None:
        assert Currency.USD == Currency.USD
        assert Currency.USD is Currency.USD

    def test_neq(self) -> None:
        assert Currency.USD != Currency.EUR

    def test_eq_non_enum(self) -> None:
        assert Currency.USD != "USD"
        assert not (Currency.USD == "USD")  # noqa: SIM201

    def test_hash(self) -> None:
        member_set = {Currency.USD, Currency.EUR, Currency.USD}
        assert len(member_set) == 2

    def test_hash_as_dict_key(self) -> None:
        member_dict = {Currency.USD: "dollar", Currency.EUR: "euro"}
        assert member_dict[Currency.USD] == "dollar"

    def test_repr(self) -> None:
        assert repr(Currency.USD) == "Currency.USD"

    def test_str(self) -> None:
        assert str(Currency.USD) == "USD"

    def test_pickle(self) -> None:
        loaded = pickle.loads(pickle.dumps(Currency.USD))  # noqa: S301
        assert loaded is Currency.USD

    def test_pickle_roundtrip_identity(self) -> None:
        for member in Currency.members:
            loaded = pickle.loads(pickle.dumps(member))  # noqa: S301
            assert loaded is member


class TestAttributeAccess:
    """Test reading data attributes on members."""

    def test_read_attrs(self) -> None:
        assert Currency.USD.symbol == "$"
        assert Currency.USD.name == "US Dollar"
        assert Currency.USD.code == "USD"
        assert Currency.USD.plural_name == "US Dollars"

    def test_read_attrs_other(self) -> None:
        assert Currency.EUR.symbol == "€"
        assert Currency.EUR.name == "Euro"
        assert Currency.GBP.symbol == "£"


class TestDefault:
    """Test Default(...) for attribute default values."""

    def test_default_applied(self) -> None:
        class Status(DataEnum):
            __members__ = ("ACTIVE", "INACTIVE")
            label: str
            enabled: Annotated[bool, Default(True)]  # noqa: FBT003

        Status.ACTIVE = Status(label="Active")
        Status.INACTIVE = Status(label="Inactive", enabled=False)  # noqa: FBT003
        assert Status.ACTIVE.enabled is True
        assert Status.INACTIVE.enabled is False

    def test_default_with_unique(self) -> None:
        class Item(DataEnum):
            __members__ = ("A", "B")
            code: Annotated[str, UNIQUE]
            priority: Annotated[int, Default(0)]

        Item.A = Item(code="a", priority=5)
        Item.B = Item(code="b")
        assert Item.A.priority == 5
        assert Item.B.priority == 0

    def test_unique_and_default_combined(self) -> None:
        class Tag(DataEnum):
            __members__ = ("X", "Y")
            name: Annotated[str, UNIQUE, Default("unnamed")]

        Tag.X = Tag()
        Tag.Y = Tag(name="why")
        assert Tag.X.name == "unnamed"
        assert Tag.Y.name == "why"
        assert Tag.get(name="why") is Tag.Y

    def test_default_override(self) -> None:
        class Thing(DataEnum):
            __members__ = ("A",)
            value: Annotated[int, Default(42)]

        Thing.A = Thing(value=99)
        assert Thing.A.value == 99

    def test_missing_required_with_defaults(self) -> None:
        class Mixed(DataEnum):
            __members__ = ("A",)
            required: str
            optional: Annotated[str, Default("default")]

        with pytest.raises(TypeError, match=r"Missing required.*required"):
            Mixed(optional="ok")

    def test_filter_on_default_value(self) -> None:
        class Status(DataEnum):
            __members__ = ("ON", "OFF", "STANDBY")
            label: str
            active: Annotated[bool, Default(True)]  # noqa: FBT003

        Status.ON = Status(label="On")
        Status.OFF = Status(label="Off", active=False)  # noqa: FBT003
        Status.STANDBY = Status(label="Standby")
        result = Status.filter(active=True)
        assert result == frozenset((Status.ON, Status.STANDBY))


class TestUniqueTogether:
    """Test UniqueTogether(...) for composite unique constraints."""

    def test_basic_unique_together(self) -> None:
        class State(DataEnum):
            __members__ = ("CA_US", "TX_US", "ON_CA", "BC_CA")
            country: Annotated[str, UniqueTogether("location")]
            code: Annotated[str, UniqueTogether("location")]
            name: str

        State.CA_US = State(country="US", code="CA", name="California")
        State.TX_US = State(country="US", code="TX", name="Texas")
        State.ON_CA = State(country="CA", code="ON", name="Ontario")
        State.BC_CA = State(country="CA", code="BC", name="British Columbia")

        # Same country (US, US) is fine
        # Same code (CA, CA) is fine
        # But (US, CA) + (US, CA) would not be
        assert State.get(country="US", code="CA") is State.CA_US
        assert State.get(country="CA", code="ON") is State.ON_CA

    def test_duplicate_composite_rejected(self) -> None:
        class State(DataEnum):
            __members__ = ("A", "B")
            country: Annotated[str, UniqueTogether("loc")]
            code: Annotated[str, UniqueTogether("loc")]

        State.A = State(country="US", code="CA")
        with pytest.raises(ConfigurationError, match=r"Duplicate values.*unique-together"):
            State.B = State(country="US", code="CA")

    def test_get_unique_together_default(self) -> None:
        class State(DataEnum):
            __members__ = ("A",)
            country: Annotated[str, UniqueTogether("loc")]
            code: Annotated[str, UniqueTogether("loc")]

        State.A = State(country="US", code="CA")
        assert State.get(country="US", code="XX", default=None) is None
        assert State.get(country="US", code="XX", default=State.A) is State.A

    def test_get_unique_together_not_found(self) -> None:
        class State(DataEnum):
            __members__ = ("A",)
            country: Annotated[str, UniqueTogether("loc")]
            code: Annotated[str, UniqueTogether("loc")]

        State.A = State(country="US", code="CA")
        with pytest.raises(MemberDoesNotExistError, match="No State"):
            State.get(country="XX", code="YY")

    def test_get_mismatched_kwargs(self) -> None:
        class State(DataEnum):
            __members__ = ("A",)
            country: Annotated[str, UniqueTogether("loc")]
            code: Annotated[str, UniqueTogether("loc")]
            name: str

        State.A = State(country="US", code="CA", name="California")
        with pytest.raises(TypeError, match="No unique"):
            State.get(country="US", name="California")

    def test_single_attr_group_rejected(self) -> None:
        with pytest.raises(ConfigurationError, match="at least 2 attributes"):

            class Bad(DataEnum):
                __members__ = ("A",)
                solo: Annotated[str, UniqueTogether("group")]

    def test_multiple_groups(self) -> None:
        class Record(DataEnum):
            __members__ = ("A", "B")
            region: Annotated[str, UniqueTogether("geo")]
            zone: Annotated[str, UniqueTogether("geo")]
            dept: Annotated[str, UniqueTogether("org")]
            team: Annotated[str, UniqueTogether("org")]

        Record.A = Record(region="US", zone="west", dept="eng", team="core")
        Record.B = Record(region="US", zone="east", dept="eng", team="infra")

        assert Record.get(region="US", zone="west") is Record.A
        assert Record.get(region="US", zone="east") is Record.B
        assert Record.get(dept="eng", team="infra") is Record.B

    def test_unique_together_with_unique(self) -> None:
        class Place(DataEnum):
            __members__ = ("A", "B")
            country: Annotated[str, UniqueTogether("loc")]
            code: Annotated[str, UniqueTogether("loc")]
            full_name: Annotated[str, UNIQUE]

        Place.A = Place(country="US", code="CA", full_name="California")
        Place.B = Place(country="CA", code="ON", full_name="Ontario")

        # Look up by unique attr
        assert Place.get(full_name="California") is Place.A
        # Look up by unique-together
        assert Place.get(country="CA", code="ON") is Place.B

    def test_filter_still_single_attr(self) -> None:
        class State(DataEnum):
            __members__ = ("A", "B")
            country: Annotated[str, UniqueTogether("loc")]
            code: Annotated[str, UniqueTogether("loc")]

        State.A = State(country="US", code="CA")
        State.B = State(country="US", code="TX")

        result = State.filter(country="US")
        assert result == frozenset((State.A, State.B))

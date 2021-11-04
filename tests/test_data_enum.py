"""Tests for DataEnum."""

# Standard Library
import pickle
import sys

# Third Party
import pytest

# Data Enum
# AMP Renderer
from data_enum import ConfigurationError, DataEnum, MemberDoesNotExistError


class IntEnum(DataEnum):
    """An integer-based enum for testing."""

    data_attributes = ("name",)


class TestDataEnum:
    """Test the DataEnum class."""

    def simple_setup(self):
        """Set up a default test enumeration."""

        class Currency(DataEnum):
            data_attributes = ("symbol", "name", "plural_name")

        Currency.AUD = Currency(
            "AUD",
            symbol="$",
            name="Australian dollar",
            plural_name="Australian dollars",
        )
        Currency.CAD = Currency(
            "CAD",
            symbol="$",
            name="Canadian dollar",
            plural_name="Canadian dollars",
        )
        Currency.EUR = Currency("EUR", symbol="€", name="Euro", plural_name="Euros")
        Currency.INR = Currency(
            "INR",
            symbol="₹",
            name="Indian rupee",
            plural_name="Indian rupees",
        )
        Currency.JPY = Currency("JPY", symbol="¥", name="Japanese yen", plural_name="Japanese yen")
        Currency.GBP = Currency(
            "GBP",
            symbol="£",
            name="Pound sterling",
            plural_name="Pounds sterling",
        )
        Currency.MXN = Currency(
            "MXN",
            symbol="$",
            name="Mexican peso",
            plural_name="Mexican pesos",
        )
        Currency.NZD = Currency(
            "NZD",
            symbol="$",
            name="New Zealand dollar",
            plural_name="New Zealand dollars",
        )
        Currency.SGD = Currency(
            "SGD",
            symbol="$",
            name="Singapore dollar",
            plural_name="Singapore dollars",
        )
        Currency.USD = Currency(
            "USD",
            symbol="$",
            name="United States dollar",
            plural_name="United States dollars",
        )

        self.Currency = Currency

    def test_simple(self):
        """Test basic setup."""
        self.simple_setup()

        assert self.Currency.AUD == self.Currency.get("AUD")
        assert self.Currency.AUD == self.Currency.get("YYY", default=self.Currency.AUD)

    def test_attributes_type_error(self):
        """Test value attribute error."""
        with pytest.raises(ConfigurationError):

            class TestEnum(DataEnum):
                data_attributes = "value"

    def test_attributes_error_1(self):
        """Test id attribute error."""
        with pytest.raises(ConfigurationError):

            class TestEnum(DataEnum):
                primary_attribute = "id"
                data_attributes = ("id",)

    def test_attributes_error_2(self):
        """Test hidden attribute error."""
        with pytest.raises(ConfigurationError):

            class TestEnum(DataEnum):
                data_attributes = ("_hidden",)

    def test_nested_attributes(self):
        """Test nested attributes."""

        class Currency(DataEnum):
            data_attributes = ("symbol", ("name", True), "plural_name")

        Currency("CAD", symbol="$", name="Canadian dollar", plural_name="Canadian dollars")
        Currency(
            "USD",
            symbol="$",
            name="United States dollar",
            plural_name="United States dollars",
        )

    def test_duplicate_element_error(self):
        """Test invalid duplicate element declaration."""

        class Currency(DataEnum):
            data_attributes = ("symbol", "name", "plural_name")

        Currency("CAD", symbol="$", name="Canadian dollar", plural_name="Canadian dollars")

        with pytest.raises(ValueError):
            Currency(
                "CAD",
                symbol="$",
                name="United States dollar",
                plural_name="United States dollars",
            )

    def test_get(self):
        """Test member lookup."""
        self.simple_setup()

        # Positional default
        usd = self.Currency.get("AAA", self.Currency.USD)
        assert usd == self.Currency.USD

        # Keyword default
        usd = self.Currency.get("AAA", default=self.Currency.USD)
        assert usd == self.Currency.USD

        # Invalid keywords
        with pytest.raises(AttributeError):
            self.Currency.get(three_letters="AAA")

        with pytest.raises(AttributeError):
            self.Currency.get(_id_="abc")

        # Invalid keyword count
        with pytest.raises(TypeError):
            self.Currency.get("USD", self.Currency.USD, "extra")

        with pytest.raises(TypeError):
            self.Currency.get("USD", self.Currency.USD, hello="there")

        # Member not found
        with pytest.raises(MemberDoesNotExistError):
            self.Currency.get("AAA")

    def test_init(self):
        """Test various enum definitions."""

        class Currency1(DataEnum):
            data_attributes = ("symbol", "name", "plural_name")

        Currency1("CAD", symbol="$", name="Canadian dollar", plural_name="Canadian dollars")
        Currency1(
            "USD",
            symbol="$",
            name="United States dollar",
            plural_name="United States dollars",
        )

        # Prevent initialization with no arguments
        class TestEnum(DataEnum):
            data_attributes = ("description",)

        with pytest.raises(TypeError):
            TestEnum()

        # Positional initialization
        class Currency2(DataEnum):
            data_attributes = ("symbol", "name", "plural_name")

        Currency2.CAD = Currency2("CAD", "$", "Canadian dollar", "Canadian dollars")
        Currency2.USD = Currency2(
            "USD",
            "$",
            "United States dollar",
            plural_name="United States dollars",
        )

        assert Currency2.CAD.plural_name == "Canadian dollars"
        assert Currency2.USD.plural_name == "United States dollars"

        # Missing attribute
        with pytest.raises(TypeError):
            Currency2("MXN", symbol="$", name="Mexican peso")

        # Extra positional attribute
        with pytest.raises(TypeError):
            Currency2("USD", "$", "United States dollar", "United States dollars", 100)

        # Extra keyword attribute
        with pytest.raises(TypeError):
            Currency2(
                "MXN",
                symbol="$",
                name="Mexican peso",
                plural_name="United States dollars",
                count=10,
            )

        class Currency3(DataEnum):
            data_attributes = ("symbol", ("name", True), "plural_name")

        Currency3("CAD", symbol="$", name="Canadian dollar", plural_name="Canadian dollars")

        # Duplicate values for unique attribute
        with pytest.raises(ValueError):
            Currency3(
                "USD",
                symbol="$",
                name="Canadian dollar",
                plural_name="United States dollars",
            )

    def test_other(self):
        """Test remaining builtin overrides."""
        self.simple_setup()

        assert not self.Currency.USD == "bitcoin"  # noqa: SIM201 (testing this specifically)
        assert self.Currency.USD != "bitcoin"

        class TestStringEnum(DataEnum):
            data_attributes = ("name", "age")

        TestStringEnum("person A", "Susan", 13)

        susan = TestStringEnum.get("person A")

        assert str(susan) == "person A"

        IntEnum(1, "Linda")

        linda = IntEnum.get(1)

        assert int(linda) == 1

        class TestAutoEnum(DataEnum):
            data_attributes = ("name",)

        sharon = TestAutoEnum(name="Sharon")

        assert int(sharon) == 0

        with pytest.raises(MemberDoesNotExistError):
            TestAutoEnum.get(0)

        if sys.version_info >= (3, 0):
            repr_susan = "TestStringEnum('person A', name='Susan', age=13)"
            repr_linda = "IntEnum(1, name='Linda')"
            repr_sharon = "TestAutoEnum(0, name='Sharon')"
        else:
            repr_susan = "TestStringEnum(u'person A', name=u'Susan', age=13)"
            repr_linda = "IntEnum(1, name=u'Linda')"
            repr_sharon = "TestAutoEnum(0, name=u'Sharon')"

        assert repr(susan) == repr_susan
        assert repr(linda) == repr_linda
        assert repr(sharon) == repr_sharon

        assert hash(linda) == hash(1)

        assert linda == pickle.loads(pickle.dumps(linda))

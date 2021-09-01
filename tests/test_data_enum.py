# -*- coding: UTF-8 -*-
from __future__ import absolute_import, unicode_literals

# Standard Library
import sys
from builtins import bytes  # noqa
from builtins import str  # noqa

# Third Party
import pytest

# Data Enum
from data_enum import ConfigurationError, DataEnum, MemberDoesNotExistError


class TestLayout:
    def simple_setup(self):
        class Currency(DataEnum):
            data_attributes = ('symbol', 'name', 'plural_name')

        Currency.AUD = Currency('AUD', symbol='$', name='Australian dollar', plural_name='Australian dollars')
        Currency.CAD = Currency('CAD', symbol='$', name='Canadian dollar', plural_name='Canadian dollars')
        Currency.EUR = Currency('EUR', symbol='€', name='Euro', plural_name='Euros')
        Currency.INR = Currency('INR', symbol='₹', name='Indian rupee', plural_name='Indian rupees')
        Currency.JPY = Currency('JPY', symbol='¥', name='Japanese yen', plural_name='Japanese yen')
        Currency.GBP = Currency('GBP', symbol='£', name='Pound sterling', plural_name='Pounds sterling')
        Currency.MXN = Currency('MXN', symbol='$', name='Mexican peso', plural_name='Mexican pesos')
        Currency.NZD = Currency('NZD', symbol='$', name='New Zealand dollar', plural_name='New Zealand dollars')
        Currency.SGD = Currency('SGD', symbol='$', name='Singapore dollar', plural_name='Singapore dollars')
        Currency.USD = Currency('USD', symbol='$', name='United States dollar', plural_name='United States dollars')

        self.Currency = Currency

    def test_simple(self):
        self.simple_setup()

        assert self.Currency.AUD == self.Currency.get('AUD')
        assert self.Currency.AUD == self.Currency.get('YYY', default=self.Currency.AUD)

    def test_attributes_type_error(self):
        with pytest.raises(ConfigurationError):
            class TestEnum(DataEnum):
                data_attributes = 'value'

    def test_attributes_error_1(self):
        with pytest.raises(ConfigurationError):
            class TestEnum(DataEnum):
                primary_attribute = 'id'
                data_attributes = ('id',)

    def test_attributes_error_2(self):
        with pytest.raises(ConfigurationError):
            class TestEnum(DataEnum):
                data_attributes = ('_hidden',)

    def test_nested_attributes(self):
        class Currency(DataEnum):
            data_attributes = ('symbol', ('name', True), 'plural_name')

        Currency('CAD', symbol='$', name='Canadian dollar', plural_name='Canadian dollars')
        Currency('USD', symbol='$', name='United States dollar', plural_name='United States dollars')

    def test_duplicate_element_error(self):
        class Currency(DataEnum):
            data_attributes = ('symbol', 'name', 'plural_name')

        Currency('CAD', symbol='$', name='Canadian dollar', plural_name='Canadian dollars')

        with pytest.raises(ValueError):
            Currency('CAD', symbol='$', name='United States dollar', plural_name='United States dollars')

    def test_get(self):
        self.simple_setup()

        # Positional default
        usd = self.Currency.get('AAA', self.Currency.USD)
        assert usd == self.Currency.USD

        # Keyword default
        usd = self.Currency.get('AAA', default=self.Currency.USD)
        assert usd == self.Currency.USD

        # Invalid keywords
        with pytest.raises(AttributeError):
            self.Currency.get(three_letters='AAA')

        with pytest.raises(AttributeError):
            self.Currency.get(_id_='abc')

        # Invalid keyword count
        with pytest.raises(TypeError):
            self.Currency.get('USD', self.Currency.USD, 'extra')

        with pytest.raises(TypeError):
            self.Currency.get('USD', self.Currency.USD, hello='there')

        # Member not found
        with pytest.raises(MemberDoesNotExistError):
            self.Currency.get('AAA')

    def test_init(self):
        class Currency1(DataEnum):
            data_attributes = ('symbol', 'name', 'plural_name')

        Currency1('CAD', symbol='$', name='Canadian dollar', plural_name='Canadian dollars')
        Currency1('USD', symbol='$', name='United States dollar', plural_name='United States dollars')

        # Prevent initialization with no arguments
        class TestEnum(DataEnum):
            data_attributes = ('description',)

        with pytest.raises(TypeError):
            TestEnum()

        # Positional initialization
        class Currency2(DataEnum):
            data_attributes = ('symbol', 'name', 'plural_name')

        Currency2.CAD = Currency2('CAD', '$', 'Canadian dollar', 'Canadian dollars')
        Currency2.USD = Currency2('USD', '$', 'United States dollar', plural_name='United States dollars')

        assert Currency2.CAD.plural_name == 'Canadian dollars'
        assert Currency2.USD.plural_name == 'United States dollars'

        # Missing attribute
        with pytest.raises(TypeError):
            Currency2('MXN', symbol='$', name='Mexican peso')

        # Extra positional attribute
        with pytest.raises(TypeError):
            Currency2('USD', '$', 'United States dollar', 'United States dollars', 100)

        # Extra keyword attribute
        with pytest.raises(TypeError):
            Currency2('MXN', symbol='$', name='Mexican peso', plural_name='United States dollars', count=10)

        class Currency3(DataEnum):
            data_attributes = ('symbol', ('name', True), 'plural_name')

        Currency3('CAD', symbol='$', name='Canadian dollar', plural_name='Canadian dollars')

        # Duplicate values for unique attribute
        with pytest.raises(ValueError):
            Currency3('USD', symbol='$', name='Canadian dollar', plural_name='United States dollars')

    def test_other(self):
        self.simple_setup()

        assert not self.Currency.USD == 'bitcoin'
        assert self.Currency.USD != 'bitcoin'

        class TestStringEnum(DataEnum):
            data_attributes = ('name', 'age')

        TestStringEnum('person A', 'Susan', 13)

        susan = TestStringEnum.get('person A')

        assert str(susan) == 'person A'
        assert susan.__unicode__() == 'person A'

        class TestIntEnum(DataEnum):
            data_attributes = ('name',)

        TestIntEnum(1, 'Linda')

        linda = TestIntEnum.get(1)

        assert int(linda) == 1

        class TestAutoEnum(DataEnum):
            data_attributes = ('name',)

        sharon = TestAutoEnum(name='Sharon')

        assert int(sharon) == 0

        with pytest.raises(MemberDoesNotExistError):
            TestAutoEnum.get(0)

        if sys.version_info >= (3, 0):
            repr_susan = "TestStringEnum('person A', name='Susan', age=13)"
            repr_linda = "TestIntEnum(1, name='Linda')"
            repr_sharon = "TestAutoEnum(0, name='Sharon')"
        else:
            repr_susan = "TestStringEnum(u'person A', name=u'Susan', age=13)"
            repr_linda = "TestIntEnum(1, name=u'Linda')"
            repr_sharon = "TestAutoEnum(0, name=u'Sharon')"

        assert repr(susan) == repr_susan
        assert repr(linda) == repr_linda
        assert repr(sharon) == repr_sharon

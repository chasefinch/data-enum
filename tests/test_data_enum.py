# -*- coding: UTF-8 -*-
from __future__ import absolute_import, unicode_literals

# Standard Library
from builtins import bytes  # noqa
from builtins import str  # noqa

# Third Party
import pytest

# Data Enum
from data_enum import ConfigurationError, DataEnum, MemberDoesNotExistError


class TestLayout:
    def simple_setup(self):
        class Currency(DataEnum):
            data_attribute_names = ('symbol', 'name', 'plural_name')

        Currency.register([
            Currency('AUD', symbol='$', name='Australian dollar', plural_name='Australian dollars'),
            Currency('CAD', symbol='$', name='Canadian dollar', plural_name='Canadian dollars'),
            Currency('EUR', symbol='€', name='Euro', plural_name='Euros'),
            Currency('INR', symbol='₹', name='Indian rupee', plural_name='Indian rupees'),
            Currency('JPY', symbol='¥', name='Japanese yen', plural_name='Japanese yen'),
            Currency('GBP', symbol='£', name='Pound sterling', plural_name='Pounds sterling'),
            Currency('MXN', symbol='$', name='Mexican peso', plural_name='Mexican pesos'),
            Currency('NZD', symbol='$', name='New Zealand dollar', plural_name='New Zealand dollars'),
            Currency('SGD', symbol='$', name='Singapore dollar', plural_name='Singapore dollars'),
            Currency('USD', symbol='$', name='United States dollar', plural_name='United States dollars'),
        ])

        self.Currency = Currency

    def test_simple(self):
        self.simple_setup()

        assert self.Currency.AUD == self.Currency.get('AUD')
        assert self.Currency.AUD == self.Currency.get(value='AUD')
        assert self.Currency.AUD == self.Currency.get(value='YYY', default=self.Currency.AUD)

    def test_attribute_names_type_error(self):
        with pytest.raises(ConfigurationError):
            class TestEnum(DataEnum):
                data_attribute_names = 'value'

    def test_attribute_name_error_1(self):
        with pytest.raises(ConfigurationError):
            class TestEnum(DataEnum):
                data_attribute_names = ('value',)

    def test_attribute_name_error_2(self):
        with pytest.raises(ConfigurationError):
            class TestEnum(DataEnum):
                data_attribute_names = ('_hidden',)

    def test_nested_attribute_names(self):
        class Currency(DataEnum):
            data_attribute_names = ('symbol', ('name', True), 'plural_name')

        Currency.register([
            Currency('CAD', symbol='$', name='Canadian dollar', plural_name='Canadian dollars'),
            Currency('USD', symbol='$', name='United States dollar', plural_name='United States dollars'),
        ])

    def test_duplicate_registration_error(self):
        class Currency(DataEnum):
            data_attribute_names = ('symbol', 'name', 'plural_name')

        cad = Currency('CAD', symbol='$', name='Canadian dollar', plural_name='Canadian dollars')
        usd = Currency('USD', symbol='$', name='United States dollar', plural_name='United States dollars')

        Currency.register([cad])

        with pytest.raises(ConfigurationError):
            Currency.register([usd])

    def test_duplicate_element_error(self):
        class Currency(DataEnum):
            data_attribute_names = ('symbol', 'name', 'plural_name')

        cad1 = Currency('CAD', symbol='$', name='Canadian dollar', plural_name='Canadian dollars')
        cad2 = Currency('CAD', symbol='$', name='United States dollar', plural_name='United States dollars')

        with pytest.raises(ValueError):
            Currency.register([cad1, cad2])

    def test_get(self):
        self.simple_setup()

        # Positional default
        usd = self.Currency.get('AAA', self.Currency.USD)
        assert usd == self.Currency.USD

        # Keyword default
        usd = self.Currency.get('AAA', default=self.Currency.USD)
        assert usd == self.Currency.USD

        cad = self.Currency.get(value='AAA', default=self.Currency.CAD)
        assert cad == self.Currency.CAD

        # Invalid keyword
        with pytest.raises(AttributeError):
            self.Currency.get(three_letters='AAA')

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
            data_attribute_names = ('symbol', 'name', 'plural_name')

        cad1 = Currency1('CAD', symbol='$', name='Canadian dollar', plural_name='Canadian dollars')
        usd1 = Currency1('USD', symbol='$', name='United States dollar', plural_name='United States dollars')

        Currency1.register([usd1, cad1])

        # Prevent initialization after registration
        with pytest.raises(ConfigurationError):
            Currency1('MXN', symbol='$', name='Mexican peso', plural_name='Mexican pesos')

        # Prevent initialization with no arguments
        class TestEnum(DataEnum):
            data_attribute_names = ('description',)

        with pytest.raises(TypeError):
            TestEnum()

        # Positional initialization
        class Currency2(DataEnum):
            data_attribute_names = ('symbol', 'name', 'plural_name')

        cad2 = Currency2('CAD', '$', 'Canadian dollar', 'Canadian dollars')
        usd2 = Currency2('USD', '$', 'United States dollar', plural_name='United States dollars')

        assert cad2.plural_name == 'Canadian dollars'
        assert usd2.plural_name == 'United States dollars'

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
            data_attribute_names = ('symbol', ('name', True), 'plural_name')

        cad3 = Currency3('CAD', symbol='$', name='Canadian dollar', plural_name='Canadian dollars')
        usd3 = Currency3('USD', symbol='$', name='Canadian dollar', plural_name='United States dollars')

        # Duplicate values for unique attribute
        with pytest.raises(ValueError):
            Currency3.register([cad3, usd3])

    def test_other(self):
        self.simple_setup()

        assert not self.Currency.USD == 'bitcoin'
        assert self.Currency.USD != 'bitcoin'

        class TestStringEnum(DataEnum):
            data_attribute_names = ('name',)

        TestStringEnum.register([
            TestStringEnum('person A', 'Susan'),
        ])

        susan = TestStringEnum.get('person A')

        assert str(susan) == 'person A'
        assert susan.__unicode__() == 'person A'

        class TestIntEnum(DataEnum):
            data_attribute_names = ('name',)

        TestIntEnum.register([
            TestIntEnum(1, 'Linda'),
        ])

        linda = TestIntEnum.get(1)

        assert int(linda) == 1

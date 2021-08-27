# -*- coding: UTF-8 -*-
from __future__ import absolute_import, unicode_literals

# Standard Library
from builtins import bytes  # noqa
from builtins import str  # noqa

# Data Enum
from data_enum import DataEnum


class TestLayout:
    def test_currency(self):
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

        assert Currency.AUD == Currency.get('AUD')
        assert Currency.AUD == Currency.get(value='AUD')
        assert Currency.AUD == Currency.get(value='YYY', default=Currency.AUD)

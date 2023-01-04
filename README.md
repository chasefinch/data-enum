# Data Enums

![Python 3.6+](https://img.shields.io/badge/python-3.6%2B-blue) [![Build Status](https://travis-ci.com/chasefinch/amp-renderer.svg?branch=main)](https://travis-ci.com/chasefinch/data-enum) ![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)

An alternative to the built-in Python `enum` implementation. Tested in Python 3.8 and above, but works on Python 3.6+.

Data enums allow you to:

- Associate data with enum members without using tuple-based initialization
- Use an intuitive initialization syntax to define members
- Define pure enums without using `auto()`
- Define value-based enums without storing them as class attributes
- Define secondary unique keys & use them to look up enum members
- Use classmethod syntax (`.get(…)`) to look up members, instead of using initializers

## Usage

Install via PyPI:

``` bash
pip install data-enum
```

Minimal usage:

``` py
from data_enum import DataEnum

class Currency(DataEnum):
    data_attrs = ('symbol', 'name')

Currency('CAD', symbol='$', name='Canadian dollar')
Currency('USD', symbol='$', name='United States dollar')
Currency('EUR', symbol='€', name='Euro')
```

Access the members by value:

``` py
Currency.get('USD')
Currency.get('CAD')
Currency.get('EUR')
```

Store the members as attributes:

``` py
class Currency(DataEnum):
    data_attrs = ('symbol', 'name')

Currency.CAD = Currency('CAD', symbol='$', name='Canadian dollar')
Currency.USD = Currency('USD', symbol='$', name='United States dollar')
Currency.EUR = Currency('EUR', symbol='€', name='Euro')
```

Use a custom attribute as the primary ID:

``` py
class Currency(DataEnum):
    primary_attr = 'code'
    data_attrs = ('symbol', 'name')

Currency('CAD', symbol='$', name='Canadian dollar')
Currency('USD', symbol='$', name='United States dollar')
Currency('EUR', symbol='€', name='Euro')
```

Use integers as primary IDs:

``` py
class Door(DataEnum):
    data_attrs = ('description',)

Door(1, description='Door #1')
Door(2, description='Door #2')
Door(3, description='Door #3')

d2 = Door.get(2)  # returns Door(2, description='Door #2')

int(d2)  # returns 2
```

Or, skip primary IDs altogether for a pure enumeration:

``` py
from data_enum import DataEnum

class Currency(DataEnum):
    data_attrs = ('symbol', 'name')

Currency.CAD = Currency(symbol='$', name='Canadian dollar')
Currency.USD = Currency(symbol='$', name='United States dollar')
Currency.EUR = Currency(symbol='€', name='Euro')
```

Access the attached data:

``` py
print(Currency.USD.name)  # prints 'United States dollar'
print(Currency.EUR.symbol)  # prints '€'

print(Currency.USD)  # prints 'USD'
```

Compare directly:

``` py
Currency.USD == Currency.CAD  # returns False
Currency.EUR == Currency.EUR  # returns True
```

Enforce unique secondary attributes:

``` py
class Currency(DataEnum):
    # Use a tuple with the second value as True for unique keys
    data_attrs = (('symbol', True), 'name')

# Throws ValueError
Currency('CAD', symbol='$', name='Canadian dollar')
Currency('USD', symbol='$', name='United States dollar')
```

Look up members by unique secondary attributes:

``` py
Currency.get(symbol='€')  # returns Currency.EUR
Currency.get(symbol='&')  # throws MemberDoesNotExistError
```

Look up with members with defaults:

``` py
Currency.get('ZZZ', Currency.USD)  # returns Currency.USD
Currency.get('ZZZ', default=Currency.USD)  # returns Currency.USD
Currency.get(symbol='&', default=Currency.USD)  # returns Currency.USD
```

## Testing, etc.

Install development requirements (Requires Python >= 3.8):

``` bash
make install
```

Sort imports:

``` bash
make format
```

Lint:

``` bash
make lint
```

Test:

``` bash
make test
```

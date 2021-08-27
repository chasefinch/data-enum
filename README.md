# Data Enums

An alternative to the built-in Python `enum` implementation. Data enums allow you to:

- Associate data with enum members
- Add secondary unique keys
- Lookup enum members by secondary unique keys

## Usage

Install via PyPI:

    pip install data-enum

Minimal usage:

    from data_enum import DataEnum

    class Currency(DataEnum):
       data_attribute_names = ('symbol', 'name', 'plural_name')

    # Call the register function only once
    Currency.register([
        Currency('CAD', symbol='$', name='Canadian dollar', plural_name='Canadian dollars'),
        Currency('USD', symbol='$', name='United States dollar', plural_name='United States dollars'),
        Currency('EUR', symbol='€', name='Euro', plural_name='Euros'),
    ])

Access the members by attribute (if the member value is an attribute-name-friendly string):
  
    Currency.USD
    Currency.CAD
    Currency.EUR

Access the members by value:

    Currency.get('USD')
    Currency.get('CAD')
    Currency.get('EUR')

Access the attached data:

    print(Currency.USD.name)  # prints 'United States dollar'
    print(Currency.EUR.symbol)  # prints '€'

    print(Currency.USD)  # prints 'USD'

Compare directly:

    Currency.USD == Currency.CAD  # returns False
    Currency.EUR == Currency.EUR  # returns True

Enforce unique secondary attributes:

    class Currency(DataEnum):
        # Use a tuple with the second value as True for unique keys
        data_attribute_names = (('symbol', True), 'plural_name')

    # Throws ValueError
    Currency.register([
        Currency('CAD', symbol='$', name='Canadian dollar', plural_name='Canadian dollars'),
        Currency('USD', symbol='$', name='United States dollar', plural_name='United States dollars'),
        Currency('EUR', symbol='€', name='Euro', plural_name='Euros'),
    ])

Look up members by unique secondary attributes:

    Currency.get(symbol='€')  # returns Currency.EUR
    Currency.get(symbol='&')  # throws MemberDoesNotExist exception

Look up with members with defaults:

    Currency.get('AAA', Currency.USD)  # returns Currency.USD
    Currency.get('AAA', default=Currency.USD)  # returns Currency.USD
    Currency.get(symbol='&', default=Currency.USD)  # returns Currency.USD

Use integers as values:

    class Door(DataEnum):
        data_attribute_names = ('description',)

    # Call the register function only once
    Door.register([
        Door(1, name='Door #1'),
        Door(2, name='Door #2'),
        Door(3, name='Door #3'),
    ])

    d2 = Door(2)  # returns Door(2, name='Door #2')

    int(d2)  # returns 2

## Testing, etc.

Sort imports (Requires Python >= 3.6):

    make format

Lint (Requires Python >= 3.6):

    make lint

Test:

    make test

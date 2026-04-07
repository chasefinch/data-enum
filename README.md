# Data Enums

[![Build Status](https://github.com/chasefinch/data-enum/actions/workflows/build.yml/badge.svg?branch=main)](https://github.com/chasefinch/data-enum/actions/workflows/build.yml) ![Coverage: 90%+](https://img.shields.io/badge/coverage-90%25-brightgreen) [![PyPI version](https://img.shields.io/pypi/v/data-enum)](https://pypi.org/project/data-enum/)

An alternative to the built-in Python `enum` implementation. Supports Python 3.11+.

Data enums allow you to:

- Define enum members with associated data using type hints
- Enforce unique constraints on attributes
- Look up members by name or unique attribute values
- Filter members by any attribute
- Use pure enums without any data attributes

## Usage

Install via PyPI:

```bash
pip install data-enum
```

### Basic example

```py
from typing import Annotated

from data_enum import DataEnum, UNIQUE

class Currency(DataEnum):
    __members__ = ("USD", "EUR", "GBP")

    symbol: str
    name: str
    code: Annotated[str, UNIQUE]

Currency.USD = Currency(symbol="$", name="US Dollar", code="USD")
Currency.EUR = Currency(symbol="€", name="Euro", code="EUR")
Currency.GBP = Currency(symbol="£", name="Pound Sterling", code="GBP")
```

### Access data on members

```py
Currency.USD.name      # 'US Dollar'
Currency.EUR.symbol    # '€'
str(Currency.USD)      # 'USD'
repr(Currency.USD)     # 'Currency.USD'
```

### Look up members by name

```py
Currency.get("USD")                          # Currency.USD
Currency.get("MISSING", default=None)        # None
Currency.get("MISSING", default=Currency.USD)  # Currency.USD
```

### Look up by unique attribute

```py
Currency.get(code="EUR")                          # Currency.EUR
Currency.get(code="MISSING", default=Currency.USD)  # Currency.USD
```

### Filter by any attribute

```py
Currency.filter(symbol="$")  # frozenset({Currency.USD})
Currency.filter(symbol="₿")  # frozenset()
```

### Compare and hash

```py
Currency.USD == Currency.EUR  # False
Currency.USD == Currency.USD  # True

{Currency.USD, Currency.EUR}  # works in sets
{Currency.USD: "dollar"}      # works as dict keys
```

### No-data enums

```py
class Direction(DataEnum):
    __members__ = ("NORTH", "SOUTH", "EAST", "WEST")

Direction.NORTH = Direction()
Direction.SOUTH = Direction()
Direction.EAST = Direction()
Direction.WEST = Direction()
```

### All members (in declaration order)

```py
Currency.members  # (Currency.USD, Currency.EUR, Currency.GBP)
```

### Safety

Members are immutable:

```py
Currency.USD.name = "Bitcoin"  # raises AttributeError
```

Duplicate unique values are rejected:

```py
Currency.GBP = Currency(symbol="£", name="Pound", code="EUR")  # raises ConfigurationError
```

All declared members must be assigned before use:

```py
class Color(DataEnum):
    __members__ = ("RED", "BLUE")
    name: str

Color.RED = Color(name="Red")
Color.get("RED")  # raises ConfigurationError (BLUE not yet assigned)
```

## Development

Set up the development environment:

```bash
make setup
source .venv/bin/activate
```

Run the full pipeline:

```bash
make
```

| Task | Command |
|---|---|
| **Full pipeline** | `make` (sync, configure, format, lint, check, test) |
| **Format** | `make format` |
| **Lint** | `make lint` (format first!) |
| **Type check** | `make check` |
| **Test** | `make test` |

## License

Licensed under the Apache License, Version 2.0.

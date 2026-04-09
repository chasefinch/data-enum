# Data Enums

[![Build Status](https://github.com/chasefinch/data-enum/actions/workflows/build.yml/badge.svg?branch=main)](https://github.com/chasefinch/data-enum/actions/workflows/build.yml) ![Coverage: 10%0](https://img.shields.io/badge/coverage-100%25-brightgreen) [![PyPI version](https://img.shields.io/pypi/v/data-enum)](https://pypi.org/project/data-enum/)

An alternative to the built-in Python `enum` implementation. Supports Python 3.11+, including free-threaded Python (3.14t).

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

from data_enum import DataEnum, UNIQUE, UniqueTogether

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

### Default values

Use standard Python default syntax to make attributes optional:

```py
class Currency(DataEnum):
    __members__ = ("USD", "EUR", "GBP")

    symbol: str
    name: str
    code: Annotated[str, UNIQUE]
    active: bool = True

Currency.USD = Currency(symbol="$", name="US Dollar", code="USD")           # active=True
Currency.EUR = Currency(symbol="€", name="Euro", code="EUR", active=False)  # active=False
```

Defaults work with `Annotated` types too:

```py
tag: Annotated[str, UNIQUE] = "none"
```

### Unique-together constraints

Use `UniqueTogether("group_name")` to enforce that a combination of attributes is unique:

```py
class State(DataEnum):
    __members__ = ("CA_US", "TX_US", "ON_CA", "BC_CA")

    country: Annotated[str, UniqueTogether("location")]
    code: Annotated[str, UniqueTogether("location")]
    name: str

State.CA_US = State(country="US", code="CA", name="California")
State.TX_US = State(country="US", code="TX", name="Texas")
State.ON_CA = State(country="CA", code="ON", name="Ontario")
State.BC_CA = State(country="CA", code="BC", name="British Columbia")
```

Individual attributes can repeat (`country="US"` appears twice), but the combination must be unique. Look up by passing all group attributes to `get()`:

```py
State.get(country="US", code="CA")  # State.CA_US
State.get(country="CA", code="ON")  # State.ON_CA
```

`UniqueTogether` works alongside `UNIQUE` and defaults:

```py
class Place(DataEnum):
    __members__ = ("A", "B")

    country: Annotated[str, UniqueTogether("location")]
    code: Annotated[str, UniqueTogether("location")]
    full_name: Annotated[str, UNIQUE]
    active: bool = True
```

### Type checker support

DataEnum uses PEP 681 (`@dataclass_transform`) so type checkers (mypy, pyright, ty) understand the constructor signature generated from your annotations:

```py
Currency(symbol="$", name="US Dollar", code="USD")  # type checker knows these kwargs
Currency(symbol="$")                                  # type checker flags missing args
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

### Thread safety

DataEnum is safe for use with free-threaded Python (3.14t, no-GIL). All runtime operations — `get()`, `filter()`, attribute access, iteration — are read-only on frozen data structures. Define your enum members at module load time (the normal usage pattern), and they are safe to access concurrently from any number of threads.

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

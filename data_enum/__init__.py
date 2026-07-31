# Copyright (C) 2021 Chase Finch
"""An alternative to the built-in Python `enum` implementation."""

from .data_enum import (
    UNIQUE as UNIQUE,
    ConfigurationError as ConfigurationError,
    DataEnum as DataEnum,
    MemberDoesNotExistError as MemberDoesNotExistError,
    UniqueTogether as UniqueTogether,
)

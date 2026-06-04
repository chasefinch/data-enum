"""Back-compatibility shims for supported Python versions.

`typing.override` only exists on Python 3.12+, but this package supports
3.11+, so provide a no-op fallback on older interpreters.
"""

import sys

if sys.version_info >= (3, 12):  # noqa: UP036  # pragma: no cover
    from typing import override
else:  # pragma: no cover
    from collections.abc import Callable
    from typing import TypeVar

    _Method = TypeVar("_Method", bound=Callable[..., object])

    def override(method: _Method) -> _Method:  # noqa: UP047
        """Return the method unchanged (PEP 695 generics need py3.12+)."""
        return method

import sys
from functools import partial
from hashlib import algorithms_available, file_digest
from typing import Any

from orjson import dumps


def wrapper(
    filepath: str,
    hasher: str,
    buffering: int = 65536,
    *args: list[Any],
    **kwargs: dict[Any, Any]
) -> tuple[str, str]:
    with open(filepath, 'rb', buffering=buffering) as file:
        hash_value = file_digest(file, hasher).hexdigest()
    func_hash = f'hashlib.{hasher}'
    str_func_hash = dumps(func_hash).decode('utf-8')
    return str_func_hash, hash_value

# This code block is dynamically creating new functions based on the functions
# defined in the `hashers` module.
thismodule = sys.modules[__name__]
for fn in algorithms_available:
    new_function = partial(wrapper, hasher = fn)
    setattr(thismodule, fn, new_function)
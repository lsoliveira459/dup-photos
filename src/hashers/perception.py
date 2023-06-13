import sys
from functools import partial
from typing import Any

import perception.hashers
from orjson import dumps


def wrapper(
    filepath: str,
    hasher: perception.hashers.Hasher,
    *args: list[Any],
    **kwargs: dict[Any, Any]
) -> tuple[str, str]:
    hash_value = hasher.compute(filepath)
    func_hash  = f'perception.{hasher.__name__}'
    str_func_hash = dumps(func_hash).decode('utf-8')
    return str_func_hash, hash_value

# This code block is dynamically creating new functions based on the functions
# defined in the `hashers` module.
thismodule = sys.modules[__name__]
for fn in perception.hashers.__all__:
    old_function = getattr(perception.hashers, fn)
    new_function = partial(wrapper, hasher = old_function)
    setattr(thismodule, fn, new_function)
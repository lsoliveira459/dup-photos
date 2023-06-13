from inspect import stack
from pathlib import Path
from typing import Any

from orjson import OPT_NAIVE_UTC, OPT_NON_STR_KEYS, dumps


def function_call_to_str(*a: list[Any], **k: dict[Any, Any]) -> str | bytes:
    '''
    The function retrieves module and function names, and returns a JSON string
    representation of the function call with its given arguments and keyword
    arguments.

    Parameters
    ----------
     : list[Any]
        - `*a` is a variable-length argument list of any type
     : dict[Any]
        - `*a` is a variable-length argument list, which can contain any number of
    positional arguments.

    Returns
    -------
        a JSON string representation of a tuple containing the filename, function name,
    positional arguments (as a list), and keyword arguments (as a dictionary) passed
    to the function. The options for the JSON serialization are determined by the
    'option' key in the keyword arguments, defaulting to OPT_NON_STR_KEYS |
    OPT_NAIVE_UTC.

    '''

    cur_stack = stack()
    # https://docs.python.org/3/library/inspect.html#inspect.stack
    # returns A list of named tuples FrameInfo(frame, filename, lineno, function, code_context, index) is returned.
    _, filepath, _, function, _, _ = cur_stack[1]
    filename = Path(filepath).name

    return dumps(
        (filename, function, (), {},),
        option = k.get('option', OPT_NON_STR_KEYS | OPT_NAIVE_UTC)
    ).decode('utf-8')

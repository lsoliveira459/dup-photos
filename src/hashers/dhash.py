from typing import Any

from dhash import dhash_row_col, format_hex
from PIL.Image import \
    open  # PIL chosen due to vast image format support and lazy-loading.

from src.werkzeug.return_functions import function_call_to_str


def dhash(
    filepath: str,
    *args: list,
    **kwargs: dict
) -> tuple[bytes | str, str]:
    '''The function takes a file path, generates a hash value using dhash algorithm,
    and returns the hash value along with function name, file path, and arguments as
    a JSON string.

    Parameters
    ----------
    filepath : str
        A string representing the file path of the image to be processed.
    *args : list[Any]
        - `filepath`: a string representing the path to an image file
    **kwargs : dict[Any, Any]
        - `filepath`: a string representing the path to an image file

    Returns
    -------
        a tuple containing a JSON-encoded string and a string representing the hash
    value of the image file specified by the `filepath` argument. The JSON-encoded
    string contains the name of the function (`dhash`), and arguments used
    on function.

    '''
    # Pass dhash arguments through
    dhash_kwargs = {'size': int}
    intersect_kwargs = {
        k: dhash_kwargs[k](kwargs[k])
        for k in (dhash_kwargs.keys() & kwargs.keys())
    }

    with open(filepath) as im:
        row, col = dhash_row_col(im, **intersect_kwargs)
        hash_value = format_hex(row, col, **intersect_kwargs)

        return f'dhash.dhash', hash_value
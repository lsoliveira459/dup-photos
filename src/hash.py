"""
_summary_

Sources:
- [stackoverflow.com/.../fast-way-of-counting-non-zero-bits-in-positive-integer](https://stackoverflow.com/a/64848298)
"""
from pathlib import Path
from hashlib import file_digest
from PIL import Image, UnidentifiedImageError
import dhash
from loguru import logger
from io import StringIO


def binary(filepath: str | Path,
            hash_algorithm: "Union[str, Callable[[str], _Hash]]" = 'md5',
            buffering: int = 65536) -> str:
    """
    Compute hash of binary file.

    Sources:
    - https://stackoverflow.com/a/44873382
    - https://docs.python.org/3/library/hashlib.html#hashlib.file_digest

    Args:
        filepath (str | Path): File path as string of pathlib.Path
        hash_algorithm (str | Callable[[str], hashlib._Hash], optional): Defaults to 'md5'.
        buffering (int, optional): Buffer in bytes. Defaults to 65536.

    Returns:
        str: Return hexdigest from hashlib
    """
    with open(filepath, 'rb', buffering=buffering) as file:
        return file_digest(file, hash_algorithm).hexdigest()

async def async_binary(*args, **kwargs):
    return binary(*args, **kwargs)

def visual(filepath: str | Path,
            hash_algorithm: str = 'dhash',
            buffering: int = 65536,
            **kwargs):
    try:
        with Image.open(filepath) as im:
            row, col = dhash.dhash_row_col(im)
            hash_value = dhash.format_hex(row, col)
            return hash_value

    except UnidentifiedImageError as exc:
        logger.warning(f'{filepath}: Format not supported')
        raise exc

async def async_visual(*args, **kwargs):
    return visual(*args, **kwargs)

def hamming_distance(a: int, b: int) -> int:
    return (~(a^(~b))).bit_count()

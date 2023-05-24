from pathlib import Path
from hashlib import file_digest
from PIL import Image, UnidentifiedImageError
import click
import dhash


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
        hash_algorithm (str | Callable[[str], hashlib._Hash], optional): _description_. Defaults to 'md5'.
        buffering (int, optional): Buffer in bytes. Defaults to 65536.

    Returns:
        str: Return hexdigest from hashlib
    """
    with open(filepath, 'rb', buffering=buffering) as f:
        return file_digest(f, hash_algorithm).hexdigest()

async def async_binary(*args, **kwargs):
    return binary(*args, **kwargs)

def visual(filepath: str | Path,
            hash_algorithm: str = 'dhash',
            buffering: int = 65536,
            **kwargs):
    try:
        file_size = filepath.stat().st_size

        with Image.open(filepath) as im:
            fmt  = im.format

            #click.echo(f'{filepath}: ', nl=False)
            #click.echo(f'{file_size}, {fmt}, {im.size}, {im.mode} ', nl=False)

            row, col = dhash.dhash_row_col(im)
            hash_value = dhash.format_hex(row, col)
    except UnidentifiedImageError as e:
        click.echo(err = f'{filepath}: Format not supported')
        raise e

    return hash_value

async def async_visual(*args, **kwargs):
    return visual(*args, **kwargs)

def hamming_distance(a: int, b: int) -> int:
    return (~(a^(~b))).bit_count()

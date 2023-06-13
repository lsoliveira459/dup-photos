"""


Sources:
- https://loguru.readthedocs.io/en/stable/resources/recipes.html#interoperability-with-tqdm-iterations
- https://github.com/uburuntu/throttler
"""

import pathlib
from asyncio import as_completed
from functools import partial
from typing import Callable, Dict, Iterable, Set, Tuple

import aiofiles
import aiofiles.os
from loguru import logger
from PIL import UnidentifiedImageError
from throttler import throttle_simultaneous
from tqdm.asyncio import tqdm

from src.hashers import enabled_hashers
from src.models import Files, Hashes
from src.models.files import add_all
from src.werkzeug.async2sync import async_, await_
from src.werkzeug.dynamic_buffer import DynamicBuffer, StaticBuffer
from src.werkzeug.filetype import filetype

logger.remove()
logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True)


@throttle_simultaneous(count=5)
async def process(file: str, functions: tuple):
    """
    Returns fmt is supported or None and True if should count as file

    Args:
        file (_type_): _description_

    Returns:
        _type_: _description_
    """
    # Async check if is file
    if not await aiofiles.os.path.isfile(file):
        raise RuntimeWarning(f"{file!s} skipped. Not a file.")

    # Check if format is supported
    result = {"fmt": await filetype.async_(file)}
    is_supported = filetype.is_image(result.get("fmt", ""))

    if is_supported:  # If supported, calculate hashes
        subtasks = [async_(func, file) for _, func in functions]

        tqdm_subtasks = tqdm(
            total=len(subtasks),
            desc=f"Processing file {file!s}",
            leave=False,
            disable=len(subtasks) > 1,  # Disable tqdm if only one hash to be calculated
        )
        for t in as_completed(subtasks):
            k, v = await t
            result[k] = v
            tqdm_subtasks.update()
        tqdm_subtasks.close()

    return str(file), result


async def gather_and_save(
    tasks: list,
    maximum_buffer: int = 200,
    enable_dynamic_buffer: bool = True,
) -> Tuple[int, int, int, int]:
    '''
    This function takes a list of tasks, processes them asynchronously, and saves
    the results to a database with a buffer to speed up interactions.

    Parameters
    ----------
    tasks : list
        A list of coroutines (async functions) that will be executed concurrently using
    asyncio.as_completed().
    maximum_buffer : int, optional
        The maximum number of files to buffer before writing them to the database.
    enable_dynamic_buffer : bool, optional
        A boolean flag that determines whether to use a dynamic buffer or a static
    buffer to speed up database interactions. If set to True, a DynamicBuffer object
    will be used, otherwise a StaticBuffer object will be used.

    Returns
    -------
        a tuple of four integers: ok_files, n_unsupported, n_directories, and n_errors.

    '''

    n_unsupported = 0
    n_errors = 0
    n_directories = 0

    # Buffer to speed up db interactions
    buffer = (
        DynamicBuffer(maximum_buffer)
        if enable_dynamic_buffer
        else StaticBuffer(maximum_buffer)
    )

    sql_add_buffer = []

    # total_cache = await Files.total_cached()
    # initial= total_cache,
    tqdm_ = partial(tqdm, leave=False)
    tqdm_tasks = tqdm_(desc="Files", total=len(tasks),)
    tqdm_buffer = tqdm_(desc="Buffer", total=buffer.next())

    for coro in as_completed(tasks):
        logger.info(
            f"Processing file {tqdm_buffer.n+1} out of {tqdm_buffer.total} files on buffer."
        )
        try:
            file, results = await coro
        except UnidentifiedImageError as exc:
            n_unsupported += 1
            logger.warning(f"Format not supported. {str(exc)}")
        except OSError as exc:
            n_errors += 1
            logger.warning(f"Error reading file. {str(exc)}")
        except RuntimeWarning as exc:
            n_directories += 1
            logger.warning(f"Not a file. Skipping. {str(exc)}")
        else:
            hashes = [
                Hashes(hashtype=algo, hashvalue=value)
                for algo, value in results.items()
            ]
            if fmt := results.get("fmt", None):
                sql_add_buffer.append(Files(path=file, filetype=fmt, hashes=hashes))
            else:
                await Files.update_hashes(file, hashes)
            tqdm_buffer.update()
            tqdm_tasks.update()

        # Persist results
        if tqdm_buffer.n >= tqdm_buffer.total:
            await add_all(sql_add_buffer)
            logger.debug(f"{tqdm_buffer.total} files saved to db.")
            tqdm_buffer.reset(buffer.next())

    tqdm_buffer.close()
    tqdm_tasks.close()

    ok_files = len(tasks) - n_unsupported - n_directories - n_errors

    return ok_files, n_unsupported, n_directories, n_errors


def filter_cached(
    files_iter: Iterable,
    enabled_hash: Dict[str, Callable],
    cached_items: Set[Tuple[str, str]],
    **kwargs,
) -> Dict[str, Tuple[str, Callable]]:
    """
    The function filters a list of files based on their hash values and returns a
    dictionary of files with their corresponding hash algorithms and functions.

    Parameters
    ----------
    files_iter : Iterable
        an iterable of file paths
    enabled_hash : Dict[str, Callable]
        A dictionary containing the names of hash algorithms as keys and their
    corresponding hash functions as values. These hash functions are used to
    calculate the hash of a file.
    cached_items : Set[Tuple[str, str]]
        A set of tuples representing cached items. Each tuple contains a filename and a
    hash algorithm used to generate the hash value for the file.

    Returns
    -------
        The function `filter_cached` returns a dictionary where the keys are the files
    in the `files_iter` iterable and the values are tuples of the hash algorithm and
    hash function for each enabled hash algorithm that has not been cached for that
    file (i.e. the `(file, algo)` tuple is not in the `cached_items` set). The
    `kwargs` argument is used to filter out any arguments

    """
    # # Remove kwargs unrelated to hash function
    # TODO: store kwargs related to hash function
    # TODO: register hash functions arguments on cli
    # kw = {
    #     k: v
    #     for k, v in kwargs.items()
    #     if k not in ('directory', 'hash')
    # }
    return {
        file: {
            (algo, func)
            for algo, func in enabled_hash.items()
            if (file, algo) not in cached_items
        }
        for file in files_iter
    }


def cmd(*args, **kwargs):
    logger.info("Initiating RUN command")
    logger.info(f"{args}\n{kwargs}")

    # Prepare functions to run hashes
    enabled_hash = {v: enabled_hashers[v] for v in kwargs.get("hash", ())}

    # Prepare list of files to process
    directories = kwargs.get("directory", ())
    files_iter = (str(p) for v in directories for p in pathlib.Path(v).iterdir())

    # Remove already processed files/hashes
    cached_items = await_(Files.get_cached_items())
    pending_files = filter_cached(files_iter, enabled_hash, cached_items, **kwargs)

    # Creating tasks to be awaited
    tasks = [process(file, algos) for file, algos in pending_files.items()]

    ok_files, n_unsupported, n_directories, n_errors = await_(gather_and_save(tasks))

    logger.info(
        f"{ok_files} unique files processed (\
          {n_unsupported} unsupported files, \
          {n_directories} diretories skipped, \
          {n_errors} file access failed)"
    )

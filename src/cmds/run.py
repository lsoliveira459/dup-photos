"""


Sources:
- https://loguru.readthedocs.io/en/stable/resources/recipes.html#interoperability-with-tqdm-iterations
- https://github.com/uburuntu/throttler
"""

from typing import Callable, List, Tuple, Dict, Any, BinaryIO
from tqdm.asyncio import tqdm
from throttler import throttle_simultaneous
from functools import partial
from loguru import logger
import pathlib
import hashlib
import itertools as it
import aiofiles, aiofiles.os
import asyncio
from PIL import Image, UnidentifiedImageError
from src.hash import binary, visual, async_binary, async_visual
from ..models.files import Session, Files, engine
from ..werkzeug.async2sync import async2sync
from ..werkzeug.filetype import filetype

logger.remove()
logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True)

algorithms_available = tuple(set(hashlib.algorithms_available) | {"visual"})


async def get_cached_items() -> Dict[str, Dict[str, Dict[str, str]]]:
    """Helper function to get already processed files and results

    Returns:
        Dict[str, Dict[str, str]]: _description_
    """
    async with Session.begin() as session:
        coro = await session.execute(Files.select())
        cached_set = {
            item[0]: {param: value}
            for item in coro.fetchall()
            for param, value in zip(coro.keys(), item) if value
        }
    return cached_set

def walk_and_apply(files_iter, cached_files, enabled_hash):
    @throttle_simultaneous(count=3)
    async def process(function, file, algo):
        """
        Returns fmt is supported or None and True if should count as file

        Args:
            file (_type_): _description_

        Returns:
            _type_: _description_
        """
        if not await aiofiles.os.path.isfile(file):
            raise RuntimeWarning(f"{str(file)} skipped. Not a file.")

        fmt    = await filetype.async_(file)
        result = await function(file, algo)

        return str(file), result, algo, fmt

    async def async_dirwalk(files_iter):
        n_unsupported = 0
        n_errors       = 0
        n_directories = 0
        ok_files      = {}
        sql_add_buffer= []
        sql_upd_buffer= []

        def isitcached(file, algo, cached_files):
            # check if algo was processed for given file
            return algo in cached_files.get(str(file), {})

        tasks = [
            process(function, file, algo)
            for file in files_iter
            for algo, function in enabled_hash.items()
            if not isitcached(file, algo, cached_files)
        ]

        for coro in tqdm(asyncio.as_completed(tasks),
                         initial = len(cached_files),
                         total   = len(cached_files) + len(tasks)):
            try:
                file, results, algo, fmt = await coro
            except UnidentifiedImageError as exc:
                n_unsupported += 1
                logger.warning(f'Format not supported. {str(exc)}')
            except OSError as exc:
                n_errors += 1
                logger.error(f"Error reading file. {str(exc)}")
            except RuntimeWarning as exc:
                n_directories += 1
                logger.error(f"Not a file. Skipping. {str(exc)}")
            else:
                if not isitcached(file, algo, cached_files):
                    cached_file = cached_files.get(file, {})
                    if not cached_file:
                        item = {h: None for h in enabled_hash.keys()} | {
                            "path": file,
                            "filetype": fmt,
                            algo: results,
                        }
                        sql_add_buffer.append(item)
                    else:
                        item = cached_file | {algo: results}
                        sql_upd_buffer.append(item)
                    cached_files[file] = item


                if len(sql_add_buffer) + len(sql_upd_buffer) >= 25:
                    logger.info(f"Sending last {len(sql_add_buffer)+len(sql_upd_buffer)} files db.")
                    async with Session.begin() as session:
                        if sql_add_buffer:
                            await session.execute(Files.insert(), sql_add_buffer)
                            sql_add_buffer = []
                        if sql_upd_buffer:
                            await session.execute(Files.update(), sql_upd_buffer)
                            sql_upd_buffer = []
                    logger.debug(f"Files saved on db.")

        return ok_files, (n_unsupported, n_directories, n_errors)

    return async2sync(async_dirwalk(files_iter))


def cmd(*args, **kwargs):
    logger.info("Initiating RUN command")
    logger.info(f"{args}\n{kwargs}")

    # Prepare functions to run hashes
    enabled_hash = {v: partial(async_binary, **{}) for v in kwargs.get("hash", tuple())}

    if "visual" in kwargs["hash"]:
        enabled_hash["visual"] = partial(async_visual, **{})

    # Prepare list of files to process
    directories = kwargs.get("directory", tuple())
    files_iter = it.chain(*(pathlib.Path(v).iterdir() for v in directories))

    cached_files = async2sync(get_cached_items())

    ok_files, (n_unsupported, n_directories, n_errors) = walk_and_apply(
        files_iter, cached_files, enabled_hash
    )

    logger.info(
        f"{len(ok_files)} unique files processed \
               ({n_unsupported} unsupported files, {n_directories} diretories skipped, {n_errors} file access failed)"
    )


from operator import itemgetter
from pathlib import Path
from src.hash import binary, visual, async_binary, async_visual
from PIL import Image, UnidentifiedImageError
from tqdm.asyncio import tqdm
from whatimage import identify_image
from throttler import throttle_simultaneous
from functools import partial
from ..models.files import Session, Files
import hashlib
import click
import itertools as it
import aiofiles, aiofiles.os
import asyncio

algorithms_available = tuple(set(hashlib.algorithms_available) | {'visual'})


def walk_and_apply(files_iter, enabled_hash):
    @throttle_simultaneous(count = 3)
    async def process_file(file):
        """
        Returns fmt is supported or None and True if should count as file

        Args:
            file (_type_): _description_

        Returns:
            _type_: _description_
        """
        if not await aiofiles.os.path.isfile(file):
            return file, {}

        # async with aiofiles.open(file, 'rb') as opened_file:
        #     data = await opened_file.read()
        #     fmt  = identify_image(data)
        #     if fmt:
        #         return file, fmt, True
        #     else:
        #         return file, None, False

        try:
            results = dict()
            for k, function in enabled_hash.items():
                results[k] = await function(file)
        except UnidentifiedImageError:
            return file, {}
        else:
            return file, results

    async def async_dirwalk(files_iter):
        n_unsupported   = 0
        ok_files        = {}

        tasks = [process_file(file) for file in files_iter]
        sql_buffer = []

        pbar = tqdm(asyncio.as_completed(tasks), total=len(tasks))

        for coro in pbar:
            try:
                file, results = await coro
                pbar.set_description(f"{file} {results}")
            except OSError:
                n_unsupported += 1
            else:
                if results:
                    ok_files[file] = results
                    results['path'] = str(file)

                    sql_buffer.append(results)

                    if len(sql_buffer) > 10:
                        async with Session.begin() as session:
                            await session.execute(Files.insert(), sql_buffer)
                            sql_buffer = []
                else:
                    n_unsupported += 1

        return ok_files, n_unsupported

    loop = asyncio.get_event_loop()
    coroutine = async_dirwalk(files_iter)
    return loop.run_until_complete(coroutine)


def cmd(*args, **kwargs):
    click.echo('Initiating RUN command')
    click.echo(f'{args}\n{kwargs}')

    # Prepare functions to run hashes
    enabled_hash = {v: partial(async_binary, **{}) for v in kwargs.get('hash', tuple())}

    if 'visual' in kwargs['hash']:
        enabled_hash['visual'] = partial(async_visual, **{})

    # Prepare list of files to process
    directories = kwargs.get('directory', tuple())
    files_iter  = it.chain(*(Path(v).iterdir() for v in directories))

    ok_files, n_unsupported, results = walk_and_apply(files_iter, enabled_hash)

    click.echo(f'{len(ok_files)} unique files processed ({n_unsupported} unsupported files)')


# with Path('X:\\Photos') as root:
#     items = {i for i in root.iterdir()}

#     print(f'{root.absolute()}: {len(items)} files found in folder')

#     for k, item in enumerate(items):
#         if not item.is_file():
#             continue
#         try:
#             with Image.open(item) as im:
#                 print(f'{item}:', end=' ')
#                 print(f'{item.stat().st_size}, {im.format}, {im.size}, {im.mode}', end=' ')

#                 row, col = dhash.dhash_row_col(im)
#                 hash_value = dhash.format_hex(row, col)
#                 bin_hash_value = compute_hash(item)

#             print(f'{hash_value} {bin_hash_value}')

#             if k == 3:
#                 break
#         except UnidentifiedImageError:
#             print(f'{item}: Format not supported')
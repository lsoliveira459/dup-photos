import asyncio
import pathlib
from typing import Any

import aiofiles
import aiofiles.os
import filetype as filetype_lib
import PIL
import whatimage
from loguru import logger
from PIL import UnidentifiedImageError


class filetype:
    @classmethod
    def __call__(cls, *args, **kwargs) -> str:
        return async2sync(cls.async_, *args, **kwargs)

    @classmethod
    def is_image(cls, mime: str):
        return (mime.split('/')[0] == 'image') if mime else False

    @staticmethod
    def _whatimage(file: str | pathlib.Path | Any) -> str:
        """Minimal wrapper for whatimmage library => github.com/david-poirier-csn/whatimage

        Args:
            file (str | pathlib.Path | Any): file path

        Raises:
            UnidentifiedImageError: If filetype not available through this library

        Returns:
            str: mimetype of file
        """
        fmt = whatimage.identify_image(file)
        if not fmt:
            logger.exception('{file} format not identified')
            raise UnidentifiedImageError(f'{file} format not identified')
        logger.debug(f"{file} format is {fmt} => (image/{fmt}).")
        return f'image/{fmt}'.lower()

    @staticmethod
    async def _filetype(file: str | pathlib.Path | Any) -> str:
        """Minimal wrapper for filetype library => github.com/h2non/filetype.py

        Args:
            file (str | pathlib.Path | Any): file path

        Raises:
            UnidentifiedImageError: If filetype not available through this library

        Returns:
            str: mimetype of file
        """
        async with aiofiles.open(file, 'rb') as openned_file:
            logger.debug(f"{file} file openned.")
            header = await openned_file.read(2048)
            fmt = filetype_lib.guess(header)
            if not fmt:
                logger.exception('{file} format not identified')
                raise UnidentifiedImageError(f'{file} format not identified')
        logger.debug(f"{file} format is {fmt.mime.lower()}.")
        return fmt.mime.lower()

    @staticmethod
    def _pillow(file: str | pathlib.Path | Any) -> str:
        """Minimal wrapper for pillow library => github.com/python-pillow/Pillow

        Args:
            file (str | pathlib.Path | Any): file path

        Raises:
            UnidentifiedImageError: If filetype not available through this library

        Returns:
            str: mimetype of file
        """
        try:
            openned_file = PIL.Image.open(file)
            logger.debug(f"{file} file openned.")
            fmt = openned_file.format
        except UnidentifiedImageError as exc:
            raise UnidentifiedImageError(
                f'{file} format not identified.'
            ) from exc
        logger.debug(f"{file} format is image/{fmt.lower()}.")
        return f"image/{fmt.lower()}"

    @classmethod
    async def async_(cls, file: str | pathlib.Path | Any) -> str:
        """Async guess filetype.

        Args:
            file (str | pathlib.Path | Any): file path

        Returns:
            str: guessed file, if any.
        """
        # logger.debug(f"file variable is of type {type(file)}")

        fmt = None
        if isinstance(file, (str, pathlib.Path)):
            # Test multiple file_identifiers
            fmt = None
            for func in cls._file_identifiers:
                try:
                    logger.debug(f"Trying {func.__name__} type identifier.")
                    temp = func(file)
                    if asyncio.iscoroutine(temp):
                        fmt = await temp
                    else:
                        fmt = temp
                except UnidentifiedImageError:
                    continue
                break
        if fmt:
            logger.debug(f"{file} is of type {fmt}.")
        else:
            logger.warning(f"Failed to identify type of {file}.")
        return fmt

    _file_identifiers = [_filetype, _whatimage]

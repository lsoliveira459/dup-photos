"""
Sources:
- [stackoverflow.com/../test-if-function-or-method-is-normal-or-asynchronous](https://stackoverflow.com/a/36076663)
"""
import asyncio
from functools import partial
from typing import Any, Callable, Coroutine

from loguru import logger


async def async_(
    func: Callable,
    *args: list,
    **kwargs: dict
) -> Any:
    '''
    The function `async_` allows for the asynchronous execution of blocking
    functions using `asyncio.to_thread`.

    Parameters
    ----------
    func : Callable
        The function that needs to be executed asynchronously.
    *args : list
        - `async_`: This is the name of the asynchronous function being defined.
    **kwargs : dict
        - `async_`: This is the name of the asynchronous function being defined.

    Returns
    -------
        The function `async_` returns the result of the `await
    asyncio.to_thread(blocking_fn)` call, which is the result of running the
    blocking function `func` with the given arguments and keyword arguments in a
    separate thread using asyncio. The return type is `Any`, which means it can be
    any type of object depending on the implementation of the `func` function.

    '''
    blocking_fn = partial(func, *args, **kwargs)
    return await asyncio.to_thread(blocking_fn)

def await_(
    func: Callable | Coroutine,
    *args: list,
    **kwargs: dict
) -> Any:
    '''
    This function allows for the execution of asynchronous functions or coroutines
    in a synchronous context.

    Parameters
    ----------
    func : Callable[Any, Any]
        A callable object that can be either an async function or a coroutine.
     : List[Any]
        - `func`: a callable object (function or coroutine) that will be executed
    asynchronously
     : Dict[Any, Any]
        - `func`: a callable object (function or coroutine) that will be executed
    asynchronously

    Returns
    -------
        The function `await_` returns the result of the executed coroutine or async
    function.

    '''
    if asyncio.iscoroutinefunction(func):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))
    elif asyncio.iscoroutine(func):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(func)
    else:
        logger.exception("Expected async function or coroutine, sync received.")
        raise RuntimeError("Expected async functionor coroutine, sync received.")

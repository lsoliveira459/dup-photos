"""
Sources:
- [stackoverflow.com/../test-if-function-or-method-is-normal-or-asynchronous](https://stackoverflow.com/a/36076663)
"""


from typing import Callable, List, Dict, Any
from loguru import logger
import asyncio

def async2sync(func: Callable[Any, Any], *args: List[Any], **kwargs: Dict[Any, Any]) -> Any:
    """Helper function to run async functions as sync

    Args:
        func (Callable[Any, Any]): function to be called
        *args (List[Any]): positional arguments of func
        **kwargs (Dict[Any]): named arguments of func

    Returns:
        Any: func return value
    """
    if asyncio.iscoroutinefunction(func):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))
    elif asyncio.iscoroutine(func):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(func)
    else:
        logger.exception("Expected async function or coroutine, sync received.")
        raise RuntimeError("Expected async functionor coroutine, sync received.")
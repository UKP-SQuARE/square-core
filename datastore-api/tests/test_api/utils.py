import asyncio
import sys


def async_return(result):
    """
    Prepares the return value for mocked async functions.
    The default behavior for unittest.mock.patch() has changed for async functions in Python 3.8.
    """
    if sys.version_info >= (3, 8):
        return result
    else:
        f = asyncio.Future()
        f.set_result(result)
    return f

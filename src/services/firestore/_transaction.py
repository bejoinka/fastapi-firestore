from contextlib import asynccontextmanager, contextmanager
import logging

from ._client import client, aclient

@asynccontextmanager
async def get_async_transaction():
    t = aclient.transaction()
    try:
        yield t
    except Exception:
        raise
    finally:
        logging.debug('transaction complete')
        # await t.commit()

@contextmanager
def get_transaction():
    t = client.transaction()
    try:
        yield t
    except Exception:
        raise
    finally:
        logging.debug('transaction complete')
        # t.commit()
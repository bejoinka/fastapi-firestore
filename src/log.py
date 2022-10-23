from functools import partial, wraps
import logging
from config import config
from loguru import logger
import sys

class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging(**kwargs):
    # intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]
    if kwargs.get('loglevel') and kwargs.get('loglevel') > 20:
        logging.warn('log level was set to warning. Will not catch info or debug')
    logging.root.setLevel(kwargs.get('loglevel', config.log.log_level))

    # remove every other logger's handlers
    # and propagate to root logger
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # configure loguru
    logger.configure(handlers=[{"sink": sys.stdout, "serialize": config.log.is_json}])

# I'm cheating here rather than doing a cuter decorator that allows to modify the level

def debug(func):
    """Wrapper to log a function
    ```python
    import log

    @log.debug
    def some_function():
        pass
    ```"""
    @wraps(func)
    def wrapper(*args, **kwds):
        # logger.log(level, f"Calling {func.__name__}" + msg if msg else "")
        logging.debug(f"Calling {func.__name__}")
        resp = func(*args, **kwds)
        logging.debug(f"{func.__name__} returns {resp}")
        return resp
    return wrapper

def info(func):
    """Wrapper to log a function
    ```python
    import log

    @log.info
    def some_function():
        pass
    ```"""
    @wraps(func)
    def wrapper(*args, **kwds):
        # logger.log(level, f"Calling {func.__name__}" + msg if msg else "")
        logging.info(f"Calling {func.__name__}")
        resp = func(*args, **kwds)
        logging.info(f"{func.__name__} returns {resp}")
        return resp
    return wrapper

def warn(func):
    """Wrapper to log a function
    ```python
    import log

    @log.warn
    def some_function():
        pass
    ```"""
    @wraps(func)
    def wrapper(*args, **kwds):
        # logger.log(level, f"Calling {func.__name__}" + msg if msg else "")
        logging.warn(f"Calling {func.__name__}")
        resp = func(*args, **kwds)
        logging.warn(f"{func.__name__} returns {resp}")
        return resp
    return wrapper
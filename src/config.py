import os
import logging
import pydantic
from dotenv import load_dotenv

try:
    load_dotenv(".env")
except:
    logging.warn('unable to load `.env`')
    pass

try:
    load_dotenv(".env-public")
except:
    logging.warn('unable to load `.env-public`')
    pass

env = os.environ

@pydantic.dataclasses.dataclass
class ServerConfig:
    host: str = os.environ.get("HOST", "http://localhost")
    port: str | int = os.environ.get("PORT", 8080)
    number_of_workers: int = int(os.environ.get("NUMBER_OF_WORKERS", 1))

@pydantic.dataclasses.dataclass
class GoogleConfig:
    credentials: str = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

ll = logging.getLevelName(os.environ.get("LOG_LEVEL", "DEBUG"))
# try:
#     logging.addLevelName(TRACE_LOG_LEVEL, 'TRACE')
#     LOG_LEVELS = {
#         50: logging.CRITICAL,
#         40: logging.ERROR,
#         30: logging.WARNING,
#         20: logging.INFO,
#         10: logging.DEBUG
#     }
#     ll = LOG_LEVELS[ll]
# except:
#     ...

@pydantic.dataclasses.dataclass
class LogConfig:
    log_level = ll
    is_json = True if os.environ.get("JSON_LOGS", "0") == "1" else False


@pydantic.dataclasses.dataclass
class Config:
    server: ServerConfig
    google: GoogleConfig
    log: LogConfig


server_config = ServerConfig()

google_config = GoogleConfig()

log_config = LogConfig()

config = Config(
    server=server_config,
    google=google_config,
    log=log_config,
)

if __name__ == '__main__':
    from rich.console import Console
    c = Console()
    c.print(config)
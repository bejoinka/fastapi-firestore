from fastapi import FastAPI
from middleware import add_middlewares
from routes import add_routers
from uvicorn import Config, Server
from config import config
from rich.console import Console
from log import setup_logging
c = Console()

app = FastAPI()
add_routers(app)
add_middlewares(app)

def run(**kwargs):
    server = Server(
        Config(
            app="server:app",
            host="0.0.0.0",
            port=8080,
            log_level=config.log.log_level,
            **kwargs,
        ),
    )
    setup_logging()
    server.run()

setup_logging()
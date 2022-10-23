from fastapi import FastAPI
from middleware.timing import TimingMiddleware
from .health import router as health_router

def add_routers(app: FastAPI):
    app.include_router(health_router, prefix='')
    
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .timing import TimingMiddleware
from .exception import validation_exception_handler, RequestValidationError

def add_middlewares(app: FastAPI):
    app.add_middleware(CORSMiddleware, **{
        'allow_origins': '*',
        'allow_origins': '*',
        'allow_headers': '*',
        'allow_credentials': True,
        'allow_methods': '*',

    })
    app.add_middleware(TimingMiddleware)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
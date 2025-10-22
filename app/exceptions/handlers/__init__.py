from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.exceptions.base import BaseAPIException
from app.exceptions.handlers.custom import base_api_exception_handler
from app.exceptions.handlers.validation import validation_exception_handler


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(BaseAPIException, base_api_exception_handler)

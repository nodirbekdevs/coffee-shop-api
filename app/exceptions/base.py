from __future__ import annotations

from typing import Any
from fastapi import status

from app.fields.common import CookieModel


class BaseAPIException(Exception):
    status_code: int = status.HTTP_400_BAD_REQUEST
    default_message: str = "An error occurred"
    default_message_key: str = "error"
    default_headers: dict[str, str] = {}
    default_cookies: list[CookieModel] = []

    def __init__(
        self,
        message: str | None = None,
        message_key: str | None = None,
        errors: Any | None = None,
        status_code: int | None = None,
        exception_class: str | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
    ) -> None:
        self.message = message or self.default_message
        self.message_key = message_key or self.default_message_key
        self.errors = errors
        self.status_code = status_code or self.status_code
        self.headers = headers or self.default_headers
        self.cookies = cookies or self.default_cookies
        self.exception_class = exception_class or self.__class__.__name__

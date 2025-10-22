import json

from fastapi.requests import Request
from fastapi.responses import Response

from app.exceptions.base import BaseAPIException


async def base_api_exception_handler(request: Request, exc: BaseAPIException) -> Response:
    response = Response(
        content=json.dumps(
            {
                "message": exc.message,
                "message_key": exc.message_key,
                "errors": exc.errors,
                "exception_class": exc.exception_class,
            }
        ),
        status_code=exc.status_code,
        headers=exc.headers,
        media_type="application/json",
    )

    if exc.cookies:
        for cookie in exc.cookies:
            response.set_cookie(
                key=cookie.key,
                value=cookie.value,
                max_age=cookie.max_age,
                path=cookie.path,
                domain=cookie.domain,
                httponly=cookie.httponly,
                secure=cookie.secure,
                samesite=cookie.samesite,
            )

    return response

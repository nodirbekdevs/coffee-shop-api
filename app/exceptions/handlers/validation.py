from fastapi.exceptions import RequestValidationError
from fastapi import status
from fastapi.requests import Request
from fastapi.responses import JSONResponse


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = {}
    for err in exc.errors():
        field = err["loc"][-1]
        errors[field] = err["msg"]

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "message": "Validation error occurred",
            "message_key": "validation_error",
            "errors": errors,
            "exception_class": exc.__class__.__name__,
        },
    )

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.services.babel import babel


class TranslationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        lang = request.headers.get("Accept-Language")
        if lang:
            babel.locale = lang
        response = await call_next(request)
        return response
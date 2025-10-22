from fastapi import FastAPI
from pydantic_settings import BaseSettings
from starlette.middleware.cors import CORSMiddleware

from app.constants.cors import CORS_ALLOWED_HEADERS
from app.middlewares.babel import TranslationMiddleware


def register_middlewares(app: FastAPI, settings: BaseSettings) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=CORS_ALLOWED_HEADERS,
    )


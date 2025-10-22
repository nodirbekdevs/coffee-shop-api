from fastapi import FastAPI

from app.config import settings
from app.middlewares import register_middlewares
from app.api.router import router as api_router

from app.exceptions.handlers import register_exception_handlers
from app.utils.common import get_debug_value_from_deployment_stage

app = FastAPI(
    debug=get_debug_value_from_deployment_stage(
        deployment_stage=settings.DEPLOYMENT_STAGE
    ),
    title="Coffee Shop Backend API",
    description="This API allows work with Coffee Shop Backend.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

register_exception_handlers(app=app)
register_middlewares(app=app, settings=settings)

app.include_router(api_router)

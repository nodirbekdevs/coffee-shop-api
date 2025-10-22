from fastapi import APIRouter
from app.api.auth.endpoints import router as auth_endpoints
from app.api.user.endpoints import router as user_endpoints


router = APIRouter()

router.include_router(router=auth_endpoints)
router.include_router(router=user_endpoints)

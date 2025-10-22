from app.config import settings
from app.fields.common import CookieModel
from app.utils.common import get_debug_value_from_deployment_stage


class SessionCookieHandler:
    def __init__(self):
        self.cookie_name = settings.VERIFICATION.COOKIE_NAME
        self.max_age = settings.VERIFICATION.BAN_TIME_SECONDS
        self.secure = get_debug_value_from_deployment_stage(
            deployment_stage=settings.DEPLOYMENT_STAGE
        )

    def create_cookie_model(self, session_id: str) -> "CookieModel":
        return CookieModel(
            value=session_id,
            key=self.cookie_name,
            max_age=self.max_age,
            secure=self.secure,
        )

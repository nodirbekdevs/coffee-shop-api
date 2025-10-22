from typing import Literal

import jwt
import datetime

from app.config import settings
from app.utils.datetime import utc_now


class JWTManager:
    def __init__(
        self, secret_key: str = settings.JWT.SECRET_KEY, algorithm: str = "HS256"
    ) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm

    def encode(self, payload: dict, token_type: Literal["access", "refresh"], expire_minutes: int) -> str:
        data = payload.copy()

        data.update(
            {
                "exp": utc_now() + datetime.timedelta(minutes=expire_minutes),
                "token_type": token_type,
            }
        )
        token = jwt.encode(data, self.secret_key, algorithm=self.algorithm)
        return token

    def decode(self, token: str) -> dict:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {str(e)}")

from fastapi import Request, Depends

from app.services.jwt import JWTManager
from app.enums.common import TokenTypeEnum
from app.repositories import UserRepository
from app.exceptions.common import (
    InvalidDataException,
    ObjectNotFoundException,
    InsufficientPermissionsException
)


class JWTAuthentication:
    def __init__(self, required_roles: tuple = None):
        self.required_roles = required_roles or ()

    async def __call__(
        self,
        request: Request,
        jwt_manager: JWTManager = Depends(),
        user_repository: UserRepository = Depends()
    ):
        auth_header = request.headers.get("Authorization")
        token = None

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split("Bearer ")[1]

        if not token:
            raise InvalidDataException(
                message="Authentication required",
                message_key="token_required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            payload = jwt_manager.decode(token=token)
            print(payload)
            if payload.get("token_type") != TokenTypeEnum.ACCESS.value or not payload.get("user_id"):
                raise InvalidDataException(
                    message="Invalid access token",
                    message_key="invalid_access_token"
                )
            print("O'tti")
            user = await user_repository.find_one_or_none(id=payload.get("user_id"))
            if not user:
                raise ObjectNotFoundException(
                    message="User not found",
                    message_key="user_not_found"
                )

            if self.required_roles and user.role not in self.required_roles:
                raise InsufficientPermissionsException(
                    message="Insufficient permissions",
                    message_key="insufficient_permissions"
                )

            request.state.user = user
            request.state.user_id = user.id
            request.state.is_authenticated = True

            return user
        except (InvalidDataException, ObjectNotFoundException, InsufficientPermissionsException):
            raise
        except Exception as e:
            raise InvalidDataException(
                message="Invalid or expired token",
                message_key="invalid_token"
            )


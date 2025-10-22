from __future__ import annotations

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

from app.enums.user import UserStatusEnum, UserRoleEnum


class UserResponseSchema(BaseModel):
    id: int
    email: EmailStr
    first_name: str | None
    last_name: str | None
    role: UserRoleEnum
    status: UserStatusEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserUpdateSchema(BaseModel):
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    role: UserRoleEnum | None = None
    status: UserStatusEnum | None = None


class UsersListResponseSchema(BaseModel):
    users: list[UserResponseSchema]
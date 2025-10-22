import re

from zxcvbn import zxcvbn
from pydantic import BaseModel, Field, field_validator, model_validator, EmailStr

from app.enums.auth import ContactTypeEnum
from app.enums.user import UserStatusEnum, UserRoleEnum
from app.services.password import password_manager


class SignUpRequestSchema(BaseModel):
    email: str = Field(..., min_length=9, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)
    re_password: str = Field(..., min_length=8, max_length=128)
    first_name: str = Field(default=None, min_length=3, max_length=30)
    last_name: str = Field(default=None, min_length=5, max_length=30)
    role: str = Field(default=UserRoleEnum.USER.value, min_length=4, max_length=10)
    status: str = Field(default=UserStatusEnum.NOT_VERIFIED.value)
    contact_type: str = Field(default=ContactTypeEnum.EMAIL.value)

    @field_validator("email", mode="after")
    @classmethod
    def validate_email(cls, v):
        try:
            EmailStr._validate(v)
        except Exception:
            raise ValueError("Invalid email address")

        return v

    @field_validator("password", mode="after")
    @classmethod
    def validate_password(cls, v):
        if not v:
            return v

        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Password must contain at least one special character")

        if re.search(r"\s", v):
            raise ValueError("Password must not contain whitespace")

        result = zxcvbn(password=v)

        if result["score"] < 2:
            warning = result["feedback"].get("warning", "Password is too weak")
            suggestions = result["feedback"].get("suggestions", [])

            error_msg = warning
            if suggestions:
                error_msg += ". " + " ".join(suggestions)

            raise ValueError(error_msg)

        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        valid_values = {member.value for member in UserRoleEnum}
        if v not in valid_values:
            raise ValueError(f"Invalid role type. Must be one of: {valid_values}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        valid_values = {member.value for member in UserStatusEnum}
        if v not in valid_values:
            raise ValueError(f"Invalid status type. Must be one of: {valid_values}")
        return v

    @field_validator("contact_type")
    @classmethod
    def validate_contact_type(cls, v: str) -> str:
        valid_values = {member.value for member in ContactTypeEnum}
        if v not in valid_values:
            raise ValueError(f"Invalid contact_type type. Must be one of: {valid_values}")
        return v

    @model_validator(mode="after")
    def validate(self):
        if self.password:
            if not self.re_password:
                raise ValueError("Password must not be empty")

            if self.password != self.re_password:
                raise ValueError("Passwords don't match")

            self.password = password_manager.hash(plain_password=self.password)
        return self


class SignUpResponseSchema(BaseModel):
    expiry_seconds: int


class VerifySecurityCodeRequestSchema(BaseModel):
    security_code: str = Field(..., min_length=6, max_length=6)
    user_id: int = Field(...)


class LoginRequestSchema(BaseModel):
    email: str = Field(..., min_length=9, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("email", mode="after")
    @classmethod
    def validate_email(cls, v):
        try:
            EmailStr._validate(v)
        except Exception:
            raise ValueError("Invalid email address")

        return v

    @field_validator("password", mode="after")
    @classmethod
    def validate_password(cls, v):
        if not v:
            return v

        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Password must contain at least one special character")

        if re.search(r"\s", v):
            raise ValueError("Password must not contain whitespace")

        result = zxcvbn(password=v)

        if result["score"] < 2:
            warning = result["feedback"].get("warning", "Password is too weak")
            suggestions = result["feedback"].get("suggestions", [])

            error_msg = warning
            if suggestions:
                error_msg += ". " + " ".join(suggestions)

            raise ValueError(error_msg)

        return v


class AccessTokenSchema(BaseModel):
    access_token: str


class RefreshAccessTokenSchema(BaseModel):
    refresh_token: str


class TokensSchema(AccessTokenSchema, RefreshAccessTokenSchema):
    pass


class LoginResponseSchema(BaseModel):
    tokens: TokensSchema


class RefreshAccessTokenRequestSchema(RefreshAccessTokenSchema):
    pass

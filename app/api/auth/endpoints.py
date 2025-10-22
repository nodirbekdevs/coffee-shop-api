from __future__ import annotations

from fastapi import APIRouter, Depends, Cookie
from starlette import status

from app.config import settings
from app.services.jwt import JWTManager

from app.exceptions.base import BaseAPIException

from app.enums.user import UserStatusEnum
from app.enums.common import TokenTypeEnum
from app.enums.auth import VerificationMethodEnum

from app.handlers.cookie import SessionCookieHandler

from app.exceptions.common import ObjectAlreadyExistsException, ObjectNotFoundException, InvalidDataException

from app.repositories import UserRepository, VerificationRepository
from app.services.password import PasswordManager

from app.utils.datetime import utc_now
from app.utils.common import generate_random_security_code, hash_security_code

from app.api.auth.limiters import VerificationLimiter
from app.api.auth.schemas import (
    SignUpRequestSchema,
    SignUpResponseSchema,
    VerifySecurityCodeRequestSchema,
    LoginRequestSchema,
    LoginResponseSchema,
    RefreshAccessTokenRequestSchema, AccessTokenSchema,
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post(
    "/signup",
    summary="Register new user",
    description="""
        Creates a new user account and sends verification code.
    
        This endpoint:
        - Validates that email is not already registered
        - Creates a new user with 'pending' status
        - Generates and hashes a security code
        - Stores verification record in database
        - Returns verification expiry time
    
        After successful registration, user must verify their email using the security code
        sent to their email address before they can login.
    """,
    status_code=status.HTTP_201_CREATED,
    response_model=SignUpResponseSchema,
)
async def signup(
    data: SignUpRequestSchema,
    user_repository: UserRepository = Depends(),
    verification_repository: VerificationRepository = Depends(),
) -> SignUpResponseSchema:
    """Register a new user account and initiate email verification process."""

    if await user_repository.check_exist(email=data.email):
        raise ObjectAlreadyExistsException(
            message="User already exists.",
            message_key="user_already_exists",
        )

    user_data = data.model_dump(exclude={"re_password", "contact_type"})
    security_code = generate_random_security_code()
    hashed_code = hash_security_code(security_code=security_code)

    user_id = await user_repository.add_one(data=user_data)

    verification_data = {
        "contact": data.email,
        "contact_type": data.contact_type,
        "security_code": hashed_code,
        "method": VerificationMethodEnum.EMAIL.value,
        "user_id": user_id
    }
    await verification_repository.add_one(data=verification_data)

    # TODO: Send email with security code instead of printing
    print(f"Security code for {data.email}: {security_code}")

    return SignUpResponseSchema(expiry_seconds=settings.VERIFICATION.EXPIRE_SECONDS)


@router.post(
    "/verify",
    summary="Verify user email",
    description="""
        Verifies user's email address using security code.
    
        This endpoint:
        - Validates security code against stored hash
        - Checks if user exists and is not already verified
        - Updates user status to 'verified'
        - Marks verification code as used
        - Implements rate limiting to prevent brute force attacks
    
        Rate limiting is applied using session cookies to prevent excessive
        verification attempts. Failed attempts are tracked and may temporarily
        block further verification requests.
    """,
    status_code=status.HTTP_200_OK,
    response_model=dict
)
async def verify(
    verifying_data: VerifySecurityCodeRequestSchema,
    user_repository: UserRepository = Depends(),
    verification_repository: VerificationRepository = Depends(),
    limiter: VerificationLimiter = Depends(),
    cookie_handler: SessionCookieHandler = Depends(),
    session_cookie_value: str | None = Cookie(default=None, alias=settings.VERIFICATION.COOKIE_NAME)
):
    """Verify user's email address with security code and activate account."""

    session_id, is_new = await limiter.check_and_prepare(session_cookie_value)

    try:
        user = await user_repository.find_one_or_none(id=verifying_data.user_id)
        if not user:
            raise InvalidDataException(
                message="User doesn't exist.",
                message_key="user_not_exists",
            )

        if user.status == UserStatusEnum.VERIFIED.value:
            raise InvalidDataException(
                message="User already verified.",
                message_key="user_already_verified",
            )

        verified_code = await verification_repository.code_verify(
            **verifying_data.model_dump()
        )

        update_verification = verification_repository.update_if_exists(
            pk=verified_code.id,
            data={"is_verified": True, "verified_at": utc_now()}
        )

        update_user = user_repository.update_if_exists(
            pk=verifying_data.user_id,
            data={"status": UserStatusEnum.VERIFIED.value}
        )

        await update_verification
        await update_user

        await limiter.reset(session_id)

        return {"message": "Verification successful"}

    except BaseAPIException as error:
        if (
            hasattr(error, "message_key")
            and error.message_key == "verification_code_invalid"
        ):
            await limiter.record_failure(session_id)

            if is_new:
                cookie = cookie_handler.create_cookie_model(session_id)
                error.cookies = [cookie]

        raise error


@router.post(
    "/login",
    summary="User login",
    description="""
        Authenticates user and returns JWT tokens.
    
        This endpoint:
        - Validates user credentials (email and password)
        - Checks if user account is verified
        - Verifies password against stored hash
        - Generates access and refresh JWT tokens
        - Returns token pair for authenticated requests
    
        Users must have verified their email before they can successfully login.
        The returned tokens are used for accessing protected endpoints and
        refreshing expired access tokens.
    """,
    status_code = status.HTTP_200_OK,
    response_model=LoginResponseSchema
)
async def login(
    data: LoginRequestSchema,
    user_repository: UserRepository = Depends(),
    password_manager: PasswordManager = Depends(),
    jwt_manager: JWTManager = Depends()
):
    """Authenticate user and return access/refresh token pair."""

    user = await user_repository.find_one_or_none(email=data.email)

    if not user:
        raise ObjectNotFoundException(
            message="User doesn't exist.",
            message_key="user_not_exists",
        )

    if user.status != UserStatusEnum.VERIFIED.value:
        raise InvalidDataException(
            message="User not verified.",
            message_key="user_not_verified",
        )

    if not password_manager.verify(
        plain_password=data.password,
        hashed_password=user.password
    ):
        raise InvalidDataException(
            message="Password is incorrect.",
            message_key="password_incorrect",
        )

    token_type = TokenTypeEnum

    payload = {"user_id": user.id}
    access_token = jwt_manager.encode(
        payload=payload,
        token_type=token_type.ACCESS.value,
        expire_minutes=settings.JWT.ACCESS_TOKEN_EXPIRY_SECONDS,
    )
    refresh_token = jwt_manager.encode(
        payload=payload,
        token_type=token_type.REFRESH.value,
        expire_minutes=settings.JWT.REFRESH_TOKEN_EXPIRY_SECONDS,
    )

    return {
        "tokens": {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    }


@router.post(
    "/refresh",
    summary="Refresh access token",
    description="""
       Generates new access token using valid refresh token.
    
       This endpoint:
       - Validates the refresh token signature and expiration
       - Checks if the token type is 'refresh'
       - Verifies that user still exists in database
       - Issues new access token with extended validity
    
       Refresh tokens have longer expiration times and can be used to
       obtain new access tokens without requiring users to login again.
       This maintains user session continuity while maintaining security.
   """,
    status_code = status.HTTP_200_OK,
    response_model=AccessTokenSchema
)
async def refresh_access_token(
    token_data: RefreshAccessTokenRequestSchema,
    jwt_manager: JWTManager = Depends(),
    user_repository: UserRepository = Depends(),
):
    """Generate new access token using valid refresh token."""

    payload = jwt_manager.decode(token=token_data.refresh_token)

    if not payload.get("token_type") or not payload.get("user_id"):
        raise InvalidDataException(
            message="Invalid refresh token.",
            message_key="invalid_refresh_token"
        )

    access_token_type = TokenTypeEnum.ACCESS.value

    if payload.get("token_type") == access_token_type:
        raise InvalidDataException(
            message="Invalid refresh token.",
            message_key="invalid_refresh_token"
        )

    IS_USER_EXISTS = await user_repository.check_exist(id=payload.get("user_id"))
    if not IS_USER_EXISTS:
        raise ObjectNotFoundException(
            message="User not found.",
            message_key="user_not_found"
        )

    return {
        "access_token": jwt_manager.encode(
            payload={"user_id": payload.get("user_id")},
            token_type=access_token_type,
            expire_minutes=settings.JWT.ACCESS_TOKEN_EXPIRY_SECONDS,
        )
    }
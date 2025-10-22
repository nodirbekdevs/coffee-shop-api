from __future__ import annotations

from fastapi import Request, APIRouter, Depends, Query, HTTPException

from starlette import status

from app.enums.user import UserRoleEnum
from app.repositories import UserRepository
from app.permissions.jwt import JWTAuthentication
from app.exceptions.common import ObjectNotFoundException, InsufficientPermissionsException, InvalidDataException

from app.api.user.schemas import UserResponseSchema, UserUpdateSchema, UsersListResponseSchema

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    dependencies=[Depends(JWTAuthentication())],
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Get the profile information of the currently authenticated user"
)
async def get_current_user(request: Request) -> UserResponseSchema:
    """Get current authenticated user's profile"""

    return request.state.user


@router.get(
    "",
    dependencies=[
        Depends(
            JWTAuthentication(
                required_roles=(UserRoleEnum.ADMIN.value,)
            )
        )
    ],
    status_code=status.HTTP_200_OK,
    response_model=UsersListResponseSchema,
    summary="Get users list",
    description="Get paginated list of all users (Admin only)"
)
async def get_users_list(
    request: Request,
    user_repository: UserRepository = Depends(),
) -> UsersListResponseSchema:
    """Get list of users"""

    users = await user_repository.find_all()

    return UsersListResponseSchema(users=users)


@router.get(
    "/{user_id}",
    dependencies=[
        Depends(
            JWTAuthentication(
                required_roles=(UserRoleEnum.ADMIN.value,)
            )
        )
    ],
    status_code=status.HTTP_200_OK,
    response_model=UserResponseSchema,
    summary="Get user by ID",
    description="Get user details by user ID (Admin only)"
)
async def get_user_by_id(
    request: Request,
    user_id: int,
    user_repository: UserRepository = Depends()
) -> UserResponseSchema:
    """Get specific user details by ID"""

    user = await user_repository.find_one_or_none(id=user_id)
    if not user:
        raise ObjectNotFoundException(
            message="User not found",
            message_key="user_not_found"
        )

    return user


@router.patch(
    "/{user_id}",
    dependencies=[
        Depends(
            JWTAuthentication(
                required_roles=(UserRoleEnum.ADMIN.value, UserRoleEnum.USER.value)
            )
        )
    ],
    status_code=status.HTTP_200_OK,
    response_model=UserResponseSchema,
    summary="Update user",
    description="Partially update user data. Users can update their own profile, admins can update any user."
)
async def update_user(
    request: Request,
    user_id: int,
    update_data: UserUpdateSchema,
    user_repository: UserRepository = Depends()
) -> UserResponseSchema:
    """Partially update user data"""

    user = await user_repository.find_one_or_none(id=user_id)
    if not user:
        raise ObjectNotFoundException(
            message="User not found",
            message_key="user_not_found"
        )

    current_user = request.state.user

    if current_user.id != user_id and current_user.role != UserRoleEnum.ADMIN.value:
        raise InsufficientPermissionsException(
            message="You can only update your own profile",
            message_key="update_own_profile_only"
        )

    if current_user.role != UserRoleEnum.ADMIN.value:
        if update_data.role is not None:
            raise InsufficientPermissionsException(
                message="You cannot change your role",
                message_key="cannot_change_role"
            )
        if update_data.status is not None:
            raise InsufficientPermissionsException(
                message="You cannot change your status",
                message_key="cannot_change_status"
            )

    update_dict = update_data.model_dump(exclude_unset=True)

    if not update_dict:
        return user  # No changes

    await user_repository.update_if_exists(
        pk=user_id,
        data=update_dict
    )

    updated_user = await user_repository.find_one_or_none(id=user_id)

    return updated_user


@router.delete(
    "/{user_id}",
    dependencies=[
        Depends(
            JWTAuthentication(
                required_roles=(UserRoleEnum.ADMIN.value,)
            )
        )
    ],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Delete user by ID (Admin only)"
)
async def delete_user(
    request: Request,
    user_id: int,
    user_repository: UserRepository = Depends()
):
    """Delete user (Admin only)"""

    current_user = request.state.user

    user = await user_repository.find_one_or_none(id=user_id)
    if not user:
        raise ObjectNotFoundException(
            message="User not found",
            message_key="user_not_found"
        )

    if current_user.id == user_id:
        raise InvalidDataException(
            message="You cannot delete your own profile",
            message_key="cannot_delete_profile"
        )

    await user_repository.delete_if_exists(pk=user_id)

    return None
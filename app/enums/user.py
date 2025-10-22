from app.enums.base import BaseEnumWithChoices


class UserStatusEnum(BaseEnumWithChoices):
    VERIFIED = "VERIFIED"
    NOT_VERIFIED = "NOT_VERIFIED"


class UserRoleEnum(BaseEnumWithChoices):
    USER = "USER"
    ADMIN = "ADMIN"

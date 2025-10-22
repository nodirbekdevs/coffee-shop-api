from app.enums.base import BaseEnumWithChoices


class ContactTypeEnum(BaseEnumWithChoices):
    PHONE = "PHONE"
    EMAIL = "EMAIL"


class VerificationMethodEnum(BaseEnumWithChoices):
    EMAIL = "EMAIL"
    SMS = "SMS"

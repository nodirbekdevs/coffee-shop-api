from enum import Enum


class BaseEnumWithChoices(str, Enum):
    @classmethod
    def choices(cls):
        return [(member.name, member.value) for member in cls]

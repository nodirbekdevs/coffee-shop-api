from enum import Enum


class DeploymentStageEnum(str, Enum):
    LOCAL = "LOCAL"
    DEVELOPMENT = "DEVELOPMENT"
    PRODUCTION = "PRODUCTION"


class TokenTypeEnum(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"

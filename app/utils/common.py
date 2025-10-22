import hashlib
import random
import uuid

from app.enums.common import DeploymentStageEnum


def get_debug_value_from_deployment_stage(deployment_stage: str) -> bool:
    if not deployment_stage:
        return False

    if deployment_stage in (
        DeploymentStageEnum.LOCAL.value,
        DeploymentStageEnum.DEVELOPMENT.value,
    ):
        return True

    if deployment_stage == DeploymentStageEnum.PRODUCTION.value:
        return False

    return False


def generate_random_security_code() -> str:
    return str(random.randint(100000, 999999))


def md5_hash(
    value: str | list[str] | tuple[str] | set[str], separator: str = "."
) -> str:
    if isinstance(value, (list, tuple, set)):
        value = separator.join(str(v) for v in value)

    md5 = hashlib.md5()
    md5.update(value.encode("utf-8"))
    return str(md5.hexdigest())


def hash_security_code(security_code: str) -> str:
    return md5_hash(value=security_code)


def generate_uuid() -> str:
    return str(uuid.uuid4())
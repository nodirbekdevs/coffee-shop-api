from fastapi import status

from app.exceptions.base import BaseAPIException


class AbstractAPIException(BaseAPIException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class InvalidDataException(AbstractAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "Invalid Data"
    default_message_key = "invalid_data"


class InvalidCredentialsException(AbstractAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_message = "Invalid service credentials"
    default_message_key = "invalid_service"


class InsufficientPermissionsException(AbstractAPIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_message = "Insufficient permissions"
    default_message_key = "insufficient_permissions"


class ObjectNotFoundException(AbstractAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_message = "Object not found"
    default_message_key = "object_not_found"


class ObjectAlreadyExistsException(AbstractAPIException):
    status_code = status.HTTP_409_CONFLICT
    default_message = "Object already exists"
    default_message_key = "object_already_exists"


class TooManyRequestsException(AbstractAPIException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_message = "Too many requests"
    default_message_key = "too_many_requests"


class InternalServerErrorException(AbstractAPIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_message = "Internal Server Error"
    default_message_key = "internal_server_error"


class ServiceUnavailableException(AbstractAPIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_message = "Service Unavailable"
    default_message_key = "service_unavailable"

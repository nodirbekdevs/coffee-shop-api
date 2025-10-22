from fastapi import status

from app.exceptions.common import AbstractAPIException


class SmsCodeTimeoutException(AbstractAPIException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_message = "Too many verification attempts. Please try again later."
    default_message_key = "sms_code_timeout"

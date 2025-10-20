from enum import Enum


class CustomExceptionEnum(Enum):
    """
    example

    NOT_AUTHORIZED = (
        "권한이 없습니다",
        "AU001",
        status.HTTP_403_FORBIDDEN,
    )
    """

    def __init__(self, message, code, status):
        self.message = message
        self.code = code
        self.status = status

from rest_framework.views import status

from common.exceptions.custom_exceptions import CustomExceptionEnum


class AuthCustomExceptions(CustomExceptionEnum):
    JWT_TOKEN_MISSING = (
        "JWT 토큰이 제공되지 않았습니다",
        "JWT001",
        status.HTTP_401_UNAUTHORIZED,
    )
    JWT_TOKEN_INVALID = (
        "유효하지 않은 JWT 토큰입니다",
        "JWT002",
        status.HTTP_401_UNAUTHORIZED,
    )
    JWT_TOKEN_EXPIRED = (
        "JWT 토큰이 만료되었습니다",
        "JWT003",
        status.HTTP_401_UNAUTHORIZED,
    )
    JWT_TOKEN_MALFORMED = (
        "잘못된 형식의 JWT 토큰입니다",
        "JWT004",
        status.HTTP_401_UNAUTHORIZED,
    )
    JWT_USER_NOT_FOUND = (
        "토큰의 사용자를 찾을 수 없습니다",
        "JWT005",
        status.HTTP_401_UNAUTHORIZED,
    )
    JWT_USER_INACTIVE = (
        "비활성화된 사용자입니다",
        "JWT006",
        status.HTTP_401_UNAUTHORIZED,
    )

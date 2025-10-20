from rest_framework import status

from common.exceptions.exception_enum import CustomExceptionEnum


class UserExceptionEnum(CustomExceptionEnum):
    ## Refresh 토큰 관련 에러
    REFRESH_TOKEN_MISSING = (
        "Refresh 토큰이 제공되지 않았습니다",
        "RT001",
        status.HTTP_401_UNAUTHORIZED,
    )
    REFRESH_TOKEN_INVALID = (
        "유효하지 않은 Refresh 토큰입니다",
        "RT002",
        status.HTTP_401_UNAUTHORIZED,
    )
    REFRESH_TOKEN_EXPIRED = (
        "Refresh 토큰이 만료되었습니다",
        "RT003",
        status.HTTP_401_UNAUTHORIZED,
    )
    REFRESH_TOKEN_BLACKLISTED = (
        "이미 사용된 Refresh 토큰입니다",
        "RT004",
        status.HTTP_401_UNAUTHORIZED,
    )


class OAuthCustomExceptions(CustomExceptionEnum):
    #
    INVALID_TOKEN = ("유효하지 않은 토큰입니다", "SE001", status.HTTP_401_UNAUTHORIZED)

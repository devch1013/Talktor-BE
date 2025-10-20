from django.contrib.auth import get_user_model
from loguru import logger
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import (
    AuthenticationFailed,
    InvalidToken,
    TokenError,
)

from common.authentication.exceptions import AuthCustomExceptions
from common.exceptions.custom_exceptions import CustomException

User = get_user_model()


class CustomJWTAuthentication(JWTAuthentication):
    """
    커스텀 JWT 인증 클래스
    각 인증 오류 상황에 맞는 커스텀 에러 메시지를 반환합니다.
    """

    def authenticate(self, request):
        # Authorization 헤더 확인
        header = self.get_header(request)
        if header is None:
            # 헤더가 없으면 None 반환 (인증되지 않은 상태로 처리)
            return None

        # raw token 추출
        raw_token = self.get_raw_token(header)
        if raw_token is None:
            # Bearer 형식이 아니거나 토큰이 없으면 커스텀 에러
            raise CustomException(AuthCustomExceptions.JWT_TOKEN_MISSING)

        try:
            # 부모 클래스의 토큰 검증 및 사용자 조회
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            return (user, validated_token)

        except AuthenticationFailed as e:
            # AuthenticationFailed 예외를 커스텀 예외로 변환
            error_detail = str(e)
            logger.error(f"JWT Authentication failed: {error_detail}")

            raise CustomException(AuthCustomExceptions.JWT_TOKEN_INVALID)

        except InvalidToken as e:
            # InvalidToken 예외를 커스텀 예외로 변환
            error_detail = str(e)
            logger.error(f"Invalid JWT token: {error_detail}")

            if "expired" in error_detail.lower():
                raise CustomException(AuthCustomExceptions.JWT_TOKEN_EXPIRED)
            elif "signature" in error_detail.lower():
                raise CustomException(AuthCustomExceptions.JWT_TOKEN_INVALID)
            elif (
                "malformed" in error_detail.lower() or "decode" in error_detail.lower()
            ):
                raise CustomException(AuthCustomExceptions.JWT_TOKEN_MALFORMED)
            else:
                raise CustomException(AuthCustomExceptions.JWT_TOKEN_INVALID)

        except TokenError as e:
            # TokenError 예외를 커스텀 예외로 변환
            error_detail = str(e)
            logger.error(f"JWT token error: {error_detail}")

            if "expired" in error_detail.lower():
                raise CustomException(AuthCustomExceptions.JWT_TOKEN_EXPIRED)
            else:
                raise CustomException(AuthCustomExceptions.JWT_TOKEN_INVALID)

        except Exception as e:
            # 기타 예외 처리
            logger.error(f"Unexpected JWT authentication error: {e}")
            raise CustomException(AuthCustomExceptions.JWT_TOKEN_INVALID)

    def get_user(self, validated_token):
        """
        검증된 토큰에서 사용자를 가져오는 메서드 오버라이드
        """
        try:
            user = super().get_user(validated_token)
            if not user.is_active:
                raise CustomException(AuthCustomExceptions.JWT_USER_INACTIVE)
            return user
        except User.DoesNotExist:
            raise CustomException(AuthCustomExceptions.JWT_USER_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error getting user from token: {e}")
            raise CustomException(AuthCustomExceptions.JWT_USER_NOT_FOUND)

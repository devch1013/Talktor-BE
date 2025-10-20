from abc import ABC, abstractmethod

import requests
from rest_framework_simplejwt.tokens import RefreshToken

from api.user.exceptions import OAuthCustomExceptions
from api.user.models import User
from common.exceptions.custom_exceptions import CustomException


class AuthService(ABC):
    @abstractmethod
    def get_or_create_user(self, identifier: str, fcmToken: str, name: str = None):
        pass

    def get_token(self, user: User):
        print(user)
        return RefreshToken.for_user(user)


class GoogleAuthService(AuthService):
    def get_or_create_user(self, identifier: str, fcmToken: str, name: str = None):
        return self._create_user(identifier, fcmToken, name)

    def _get_google_user_info(self, access_token):
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        response = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo", headers=headers
        )
        if response.status_code == 500:
            retry_response = requests.get(
                f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}"
            )
            if retry_response.status_code == 200:
                return retry_response.json()
            return None
        if response.status_code == 200:
            return response.json()
        return None

    def _create_user(self, google_token, fcmToken, name):
        if not google_token:
            raise CustomException(OAuthCustomExceptions.INVALID_TOKEN)

        # Google API로 사용자 정보 가져오기
        user_info = self._get_google_user_info(google_token)
        if not user_info:
            raise CustomException(OAuthCustomExceptions.INVALID_TOKEN)

        if "user_id" in user_info:
            user_info["sub"] = user_info["user_id"]

        # 사용자 생성 또는 조회
        user, is_created = User.objects.get_or_create(
            identifier=user_info["sub"],  # Google의 고유 사용자 ID
            defaults={
                "username": user_info.get("name", ""),
                "email": user_info.get("email", ""),
                "provider": "google",
            },
        )

        if fcmToken:
            user.fcm_token = fcmToken
            user.save()

        return user


class NativeAuthService(AuthService):
    def get_or_create_user(self, identifier: str, password: str):
        if not identifier or not password:
            raise CustomException(OAuthCustomExceptions.INVALID_TOKEN)

        user, is_created = User.objects.get_or_create(
            identifier=identifier,
            defaults={
                "password": password,
                "username": identifier,
                "provider": "native",
            },
        )

        return user

from django.db import models


class Provider(models.TextChoices):
    KAKAO = "kakao", "Kakao"
    GOOGLE = "google", "Google"
    APPLE = "apple", "Apple"

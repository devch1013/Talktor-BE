from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from api.user.enums import Provider


class CustomUserManager(BaseUserManager):
    def create_user(self, identifier, password=None, **extra_fields):
        if not identifier:
            raise ValueError("The Identifier field must be set")
        user = self.model(identifier=identifier, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, identifier, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(identifier, password, **extra_fields)


class User(AbstractUser):
    identifier = models.CharField(max_length=255, unique=True, null=True)
    username = models.CharField(max_length=255, null=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    profile_image = models.URLField(null=True)
    provider = models.CharField(
        max_length=255, choices=Provider.choices, default=Provider.KAKAO
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "identifier"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        db_table = "users"

from rest_framework import status

from common.exceptions.exception_enum import CustomExceptionEnum


class ProjectExceptions(CustomExceptionEnum):
    PROJECT_NOT_FOUND = (
        "프로젝트를 찾을 수 없습니다",
        "PRJ001",
        status.HTTP_404_NOT_FOUND,
    )

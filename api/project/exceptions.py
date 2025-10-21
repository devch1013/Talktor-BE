from rest_framework import status

from common.exceptions.exception_enum import CustomExceptionEnum


class ProjectExceptions(CustomExceptionEnum):
    PROJECT_NOT_FOUND = (
        "프로젝트를 찾을 수 없습니다",
        "PRJ001",
        status.HTTP_404_NOT_FOUND,
    )


class QuizExceptions(CustomExceptionEnum):
    QUIZ_GENERATION_TASK_NOT_FOUND = (
        "퀴즈 생성 작업을 찾을 수 없습니다",
        "QUIZ001",
        status.HTTP_404_NOT_FOUND,
    )
    QUIZ_NOT_FOUND = (
        "퀴즈를 찾을 수 없습니다",
        "QUIZ002",
        status.HTTP_404_NOT_FOUND,
    )
    QUIZ_GENERATION_NOT_COMPLETED = (
        "퀴즈 생성이 아직 완료되지 않았습니다",
        "QUIZ003",
        status.HTTP_400_BAD_REQUEST,
    )
    QUIZ_GENERATION_FAILED = (
        "퀴즈 생성에 실패했습니다",
        "QUIZ004",
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    MATERIAL_NOT_FOUND = (
        "자료를 찾을 수 없습니다",
        "QUIZ005",
        status.HTTP_404_NOT_FOUND,
    )
    INVALID_MATERIAL_SELECTION = (
        "잘못된 자료 선택입니다",
        "QUIZ006",
        status.HTTP_400_BAD_REQUEST,
    )
    PERMISSION_DENIED = (
        "접근 권한이 없습니다",
        "QUIZ007",
        status.HTTP_403_FORBIDDEN,
    )

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.project.exceptions import ProjectExceptions
from api.quiz.exceptions import QuizExceptions
from api.quiz.models import Quiz, QuizQuestions
from api.quiz.serializers.quiz_serializers import (
    QuizAnswerBatchSubmitSerializer,
    QuizAnswerSubmitSerializer,
    QuizCreateSerializer,
    QuizListSerializer,
    QuizResultSerializer,
    QuizSerializer,
    QuizStatusSerializer,
)
from api.quiz.services.quiz_service import QuizService
from common.exceptions.custom_exceptions import CustomException
from common.swagger.schema import get_swagger_response_dict


class QuizViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    """
    퀴즈 관리 API

    퀴즈 생성, 조회, 풀이 기능을 제공합니다.
    퀴즈 생성은 백그라운드에서 처리되며, polling을 통해 상태를 확인할 수 있습니다.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="프로젝트의 퀴즈 목록 조회",
        operation_description="""
        특정 프로젝트의 모든 퀴즈를 조회합니다.

        프로젝트 ID를 쿼리 파라미터로 받아 해당 프로젝트의 완료된 퀴즈 목록을 반환합니다.
        최근 생성일 기준으로 정렬됩니다.
        """,
        manual_parameters=[
            openapi.Parameter(
                "project_id",
                openapi.IN_QUERY,
                description="프로젝트 ID",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses=get_swagger_response_dict(
            success_response={
                200: QuizListSerializer(many=True),
            },
            exception_enums=[ProjectExceptions.PROJECT_NOT_FOUND],
        ),
        tags=["퀴즈"],
    )
    def list(self, request, project_id: int):
        """프로젝트의 퀴즈 목록 조회"""
        quizzes = QuizService.get_project_quizzes(project_id, request.user)
        serializer = QuizListSerializer(quizzes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="퀴즈 상세 조회",
        operation_description="""
        특정 퀴즈의 상세 정보를 조회합니다.

        퀴즈 ID를 통해 퀴즈의 모든 문제를 반환합니다.
        문제의 정답은 포함되지 않습니다 (풀이용).
        """,
        responses=get_swagger_response_dict(
            success_response={
                200: QuizSerializer,
            },
            exception_enums=[
                QuizExceptions.QUIZ_NOT_FOUND,
                QuizExceptions.PERMISSION_DENIED,
                QuizExceptions.QUIZ_GENERATION_NOT_COMPLETED,
            ],
        ),
        tags=["퀴즈"],
    )
    def retrieve(self, request, *args, **kwargs):
        """퀴즈 상세 조회"""
        quiz_id = kwargs.get("pk")

        try:
            quiz = QuizService.get_quiz(quiz_id, request.user)
        except Quiz.DoesNotExist:
            raise CustomException(QuizExceptions.QUIZ_NOT_FOUND)
        except PermissionError:
            raise CustomException(QuizExceptions.PERMISSION_DENIED)
        except ValueError:
            raise CustomException(QuizExceptions.QUIZ_GENERATION_NOT_COMPLETED)

        serializer = QuizSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="퀴즈 생성 요청",
        operation_description="""
        새로운 퀴즈 생성 작업을 시작합니다.

        프로젝트의 여러 Material을 선택하여 퀴즈를 생성할 수 있습니다.
        퀴즈 생성은 백그라운드에서 처리되며, 반환된 quiz_id로 생성 상태를 확인할 수 있습니다.

        - material_ids: 퀴즈를 생성할 Material ID 목록 (최소 1개)
        - question_type: 문제 유형 (multiple_choice, short_answer, mixed)
        - question_count: 문제 개수 (1-50)
        - difficulty: 난이도 (easy, medium, hard)
        """,
        request_body=QuizCreateSerializer,
        manual_parameters=[
            openapi.Parameter(
                "project_id",
                openapi.IN_QUERY,
                description="프로젝트 ID",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses=get_swagger_response_dict(
            success_response={
                201: QuizStatusSerializer,
            },
            exception_enums=[
                ProjectExceptions.PROJECT_NOT_FOUND,
                QuizExceptions.MATERIAL_NOT_FOUND,
                QuizExceptions.INVALID_MATERIAL_SELECTION,
            ],
        ),
        tags=["퀴즈"],
    )
    @action(detail=False, methods=["post"], url_path="generate")
    def generate_quiz(self, request, project_id: int):
        """퀴즈 생성 요청"""
        # 요청 데이터 검증
        serializer = QuizCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 퀴즈 생성 작업 시작
        try:
            quiz = QuizService.create_quiz(
                project_id=project_id,
                **serializer.validated_data,
            )
        except ValueError:
            raise CustomException(QuizExceptions.INVALID_MATERIAL_SELECTION)

        response_serializer = QuizStatusSerializer(quiz)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="퀴즈 생성 상태 조회 (Polling)",
        operation_description="""
        퀴즈 생성 작업의 현재 상태를 조회합니다.

        클라이언트는 이 엔드포인트를 주기적으로 호출(polling)하여 퀴즈 생성 진행 상태를 확인합니다.

        상태 종류:
        - pending: 대기중
        - processing: 처리중 (progress_percentage로 진행률 확인 가능)
        - completed: 완료 (이 경우 퀴즈 조회 가능)
        - failed: 실패 (error_message 확인)
        """,
        responses=get_swagger_response_dict(
            success_response={
                200: QuizStatusSerializer,
            },
            exception_enums=[
                QuizExceptions.QUIZ_NOT_FOUND,
                QuizExceptions.PERMISSION_DENIED,
            ],
        ),
        tags=["퀴즈"],
    )
    @action(detail=True, methods=["get"], url_path="status")
    def get_generation_status(self, request, pk=None):
        """퀴즈 생성 상태 조회 (Polling)"""
        quiz_id = pk

        try:
            quiz = QuizService.get_quiz_status(quiz_id, request.user)
        except Quiz.DoesNotExist:
            raise CustomException(QuizExceptions.QUIZ_NOT_FOUND)
        except PermissionError:
            raise CustomException(QuizExceptions.PERMISSION_DENIED)

        serializer = QuizStatusSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ============ 퀴즈 풀이 관련 엔드포인트 ============

    @swagger_auto_schema(
        operation_summary="퀴즈 답안 제출 (단일 문제)",
        operation_description="""
        퀴즈의 단일 문제에 대한 답안을 제출합니다.

        - question_id: 문제 ID
        - answer: 답안 (객관식: 선택지 번호, 서술형: 텍스트)

        같은 문제에 대해 여러 번 제출하면 마지막 답안으로 업데이트됩니다.
        """,
        request_body=QuizAnswerSubmitSerializer,
        responses=get_swagger_response_dict(
            success_response={
                200: openapi.Response(
                    description="답안 제출 성공",
                    schema=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "message": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                example="답안이 제출되었습니다.",
                            ),
                            "is_correct": openapi.Schema(
                                type=openapi.TYPE_BOOLEAN, example=True
                            ),
                        },
                    ),
                ),
            },
            exception_enums=[QuizExceptions.QUIZ_NOT_FOUND],
        ),
        tags=["퀴즈 풀이"],
    )
    @action(detail=True, methods=["post"], url_path="submit-answer")
    def submit_answer(self, request, pk=None):
        """퀴즈 답안 제출 (단일 문제)"""
        serializer = QuizAnswerSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            answer_history = QuizService.submit_answer(
                user=request.user,
                question_id=serializer.validated_data["question_id"],
                answer=serializer.validated_data["answer"],
            )
        except QuizQuestions.DoesNotExist:
            raise CustomException(QuizExceptions.QUIZ_NOT_FOUND)

        return Response(
            {
                "message": "답안이 제출되었습니다.",
                "is_correct": answer_history.is_correct,
            },
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_summary="퀴즈 답안 일괄 제출",
        operation_description="""
        퀴즈의 여러 문제에 대한 답안을 한 번에 제출합니다.

        - answers: 답안 목록
          - question_id: 문제 ID
          - answer: 답안

        제출 후 자동으로 채점되어 결과를 확인할 수 있습니다.
        """,
        request_body=QuizAnswerBatchSubmitSerializer,
        responses=get_swagger_response_dict(
            success_response={
                200: openapi.Response(
                    description="답안 일괄 제출 성공",
                    schema=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "message": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                example="모든 답안이 제출되었습니다.",
                            ),
                            "submitted_count": openapi.Schema(
                                type=openapi.TYPE_INTEGER, example=10
                            ),
                        },
                    ),
                ),
            },
            exception_enums=[QuizExceptions.QUIZ_NOT_FOUND],
        ),
        tags=["퀴즈 풀이"],
    )
    @action(detail=True, methods=["post"], url_path="submit-answers")
    def submit_answers_batch(self, request, pk=None):
        """퀴즈 답안 일괄 제출"""
        serializer = QuizAnswerBatchSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            answer_histories = QuizService.submit_answers_batch(
                user=request.user, answers=serializer.validated_data["answers"]
            )
        except QuizQuestions.DoesNotExist:
            raise CustomException(QuizExceptions.QUIZ_NOT_FOUND)

        return Response(
            {
                "message": "모든 답안이 제출되었습니다.",
                "submitted_count": len(answer_histories),
            },
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_summary="퀴즈 결과 조회",
        operation_description="""
        퀴즈의 채점 결과를 조회합니다.

        사용자가 제출한 답안을 기준으로 정답/오답 개수, 점수, 문제별 결과를 반환합니다.
        정답과 해설이 포함됩니다.
        """,
        responses=get_swagger_response_dict(
            success_response={
                200: QuizResultSerializer,
            },
            exception_enums=[QuizExceptions.QUIZ_NOT_FOUND],
        ),
        tags=["퀴즈 풀이"],
    )
    @action(detail=True, methods=["get"], url_path="result")
    def get_quiz_result(self, request, pk=None):
        """퀴즈 결과 조회"""
        quiz_id = pk

        try:
            result = QuizService.get_quiz_result(request.user, quiz_id)
        except Quiz.DoesNotExist:
            raise CustomException(QuizExceptions.QUIZ_NOT_FOUND)

        serializer = QuizResultSerializer(result)
        return Response(serializer.data, status=status.HTTP_200_OK)

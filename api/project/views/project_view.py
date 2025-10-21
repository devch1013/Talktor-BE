from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.project.models import Material, Project
from api.project.serializers import (
    MaterialCreateSerializer,
    MaterialListSerializer,
    MaterialSerializer,
    ProjectSerializer,
)
from api.project.serializers.project_serializers import (
    ProjectCreateSerializer,
    ProjectListSerializer,
)
from api.project.services import MaterialService, ProjectService


class SubjectViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    """
    과목 관리 API

    사용자의 과목 생성, 조회, 수정, 삭제 기능을 제공합니다.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer

    def get_queryset(self):
        """현재 사용자의 과목만 조회"""
        return Project.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_summary="과목 목록 조회",
        operation_description="""
        현재 로그인한 사용자의 모든 과목을 조회합니다.

        각 과목의 학습 자료 개수와 마지막 활동 날짜를 포함합니다.
        최근 수정일 기준으로 정렬됩니다.
        """,
        responses={
            200: ProjectListSerializer(many=True),
            401: "인증되지 않은 사용자",
        },
        tags=["과목"],
    )
    def list(self, request, *args, **kwargs):
        """과목 목록 조회"""
        projects = ProjectService.get_user_projects(request.user)
        serializer = ProjectListSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="과목 생성",
        operation_description="""
        새로운 과목을 생성합니다.

        과목명과 색상 코드를 입력받아 과목을 생성합니다.
        색상 코드는 Hex 형식 (예: #3B82F6)을 사용합니다.
        """,
        request_body=ProjectCreateSerializer,
        responses={
            201: ProjectSerializer,
            400: "잘못된 요청 데이터",
            401: "인증되지 않은 사용자",
        },
        tags=["과목"],
    )
    def create(self, request, *args, **kwargs):
        """과목 생성"""
        serializer = ProjectCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project = ProjectService.create_project(
            user=request.user,
            name=serializer.validated_data["name"],
            color=serializer.validated_data.get("color", "#3B82F6"),
        )

        return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="과목 상세 조회",
        operation_description="""
        특정 과목의 상세 정보를 조회합니다.

        자신이 생성한 과목만 조회할 수 있습니다.
        """,
        responses={
            200: ProjectSerializer,
            401: "인증되지 않은 사용자",
            404: "과목을 찾을 수 없음",
        },
        tags=["과목"],
    )
    def retrieve(self, request, *args, **kwargs):
        """과목 상세 조회"""
        subject = ProjectService.get_subject(kwargs["pk"], request.user)
        serializer = ProjectSerializer(subject)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="과목 수정",
        operation_description="""
        특정 과목의 정보를 수정합니다.

        과목명과 색상 코드를 수정할 수 있습니다.
        자신이 생성한 과목만 수정할 수 있습니다.
        """,
        request_body=ProjectSerializer,
        responses={
            200: ProjectSerializer,
            400: "잘못된 요청 데이터",
            401: "인증되지 않은 사용자",
            404: "과목을 찾을 수 없음",
        },
        tags=["과목"],
    )
    def update(self, request, *args, **kwargs):
        """과목 수정 (전체)"""
        serializer = ProjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project = ProjectService.update_project(
            kwargs["pk"], request.user, **serializer.validated_data
        )

        return Response(ProjectSerializer(project).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="과목 부분 수정",
        operation_description="""
        특정 과목의 일부 정보만 수정합니다.

        수정하고자 하는 필드만 전송하면 됩니다.
        자신이 생성한 과목만 수정할 수 있습니다.
        """,
        request_body=ProjectSerializer,
        responses={
            200: ProjectSerializer,
            400: "잘못된 요청 데이터",
            401: "인증되지 않은 사용자",
            404: "과목을 찾을 수 없음",
        },
        tags=["과목"],
    )
    def partial_update(self, request, *args, **kwargs):
        """과목 부분 수정"""
        serializer = ProjectSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        subject = ProjectService.update_subject(
            kwargs["pk"], request.user, **serializer.validated_data
        )

        return Response(ProjectSerializer(subject).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="과목 삭제",
        operation_description="""
        특정 과목을 삭제합니다.

        과목에 속한 모든 학습 자료도 함께 삭제됩니다.
        자신이 생성한 과목만 삭제할 수 있습니다.
        """,
        responses={
            204: "삭제 성공",
            401: "인증되지 않은 사용자",
            404: "과목을 찾을 수 없음",
        },
        tags=["과목"],
    )
    def destroy(self, request, *args, **kwargs):
        """과목 삭제"""
        ProjectService.delete_subject(kwargs["pk"], request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MaterialViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    """
    학습 자료 관리 API

    과목별 학습 자료 생성, 조회, 수정, 삭제 기능을 제공합니다.
    파일 업로드 및 URL 자료 추가를 지원합니다.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = MaterialSerializer

    def get_queryset(self):
        """현재 사용자의 자료만 조회"""
        return Material.objects.filter(subject__user=self.request.user)

    @swagger_auto_schema(
        operation_summary="학습 자료 목록 조회",
        operation_description="""
        특정 과목의 모든 학습 자료를 조회합니다.

        파일 타입과 URL 타입 자료를 모두 포함합니다.
        최근 생성일 기준으로 정렬됩니다.
        """,
        manual_parameters=[
            openapi.Parameter(
                "subject_id",
                openapi.IN_QUERY,
                description="과목 ID",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={
            200: MaterialListSerializer(many=True),
            400: "과목 ID가 필요합니다",
            401: "인증되지 않은 사용자",
        },
        tags=["학습 자료"],
    )
    def list(self, request, *args, **kwargs):
        """학습 자료 목록 조회"""
        subject_id = request.query_params.get("subject_id")

        if not subject_id:
            return Response(
                {"error": "subject_id 파라미터가 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        materials = MaterialService.get_subject_materials(subject_id, request.user)
        serializer = MaterialListSerializer(materials, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="학습 자료 생성",
        operation_description="""
        새로운 학습 자료를 생성합니다.

        파일 업로드:
        - material_type: 'file'
        - files: 업로드할 파일 목록 (여러 개 가능)
        - title: 자료명

        URL 추가:
        - material_type: 'url'
        - url: 웹 주소
        - title: 자료명

        선택 사항:
        - page_count: 페이지 수
        - thumbnail_url: 썸네일 이미지 URL
        """,
        manual_parameters=[
            openapi.Parameter(
                "subject_id",
                openapi.IN_QUERY,
                description="과목 ID",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        request_body=MaterialCreateSerializer,
        responses={
            201: MaterialSerializer,
            400: "잘못된 요청 데이터",
            401: "인증되지 않은 사용자",
            404: "과목을 찾을 수 없음",
        },
        tags=["학습 자료"],
    )
    def create(self, request, *args, **kwargs):
        """학습 자료 생성"""
        subject_id = request.query_params.get("subject_id")

        if not subject_id:
            return Response(
                {"error": "subject_id 파라미터가 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 과목 조회 (권한 확인)
        subject = ProjectService.get_subject(subject_id, request.user)

        # 요청 데이터 검증
        serializer = MaterialCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 파일 처리 (multipart/form-data)
        files = request.FILES.getlist("files")

        # 자료 생성
        material = MaterialService.create_material(
            subject=subject,
            title=serializer.validated_data["title"],
            material_type=serializer.validated_data["material_type"],
            url=serializer.validated_data.get("url"),
            files=files if files else None,
            page_count=serializer.validated_data.get("page_count", 0),
            thumbnail_url=serializer.validated_data.get("thumbnail_url"),
        )

        return Response(
            MaterialSerializer(material).data, status=status.HTTP_201_CREATED
        )

    @swagger_auto_schema(
        operation_summary="학습 자료 상세 조회",
        operation_description="""
        특정 학습 자료의 상세 정보를 조회합니다.

        업로드된 파일 목록을 포함합니다.
        자신이 소유한 과목의 자료만 조회할 수 있습니다.
        """,
        responses={
            200: MaterialSerializer,
            401: "인증되지 않은 사용자",
            404: "학습 자료를 찾을 수 없음",
        },
        tags=["학습 자료"],
    )
    def retrieve(self, request, *args, **kwargs):
        """학습 자료 상세 조회"""
        material = MaterialService.get_material(kwargs["pk"], request.user)
        serializer = MaterialSerializer(material)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="학습 자료 수정",
        operation_description="""
        특정 학습 자료의 정보를 수정합니다.

        수정 가능한 필드:
        - title: 자료명
        - url: 웹 주소 (URL 타입인 경우)
        - page_count: 페이지 수
        - thumbnail_url: 썸네일 URL

        추가 파일 업로드도 가능합니다.
        자신이 소유한 과목의 자료만 수정할 수 있습니다.
        """,
        request_body=MaterialSerializer,
        responses={
            200: MaterialSerializer,
            400: "잘못된 요청 데이터",
            401: "인증되지 않은 사용자",
            404: "학습 자료를 찾을 수 없음",
        },
        tags=["학습 자료"],
    )
    def update(self, request, *args, **kwargs):
        """학습 자료 수정 (전체)"""
        serializer = MaterialSerializer(data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)

        # 파일 처리
        files = request.FILES.getlist("files")

        update_data = serializer.validated_data.copy()
        if files:
            update_data["files"] = files

        material = MaterialService.update_material(
            kwargs["pk"], request.user, **update_data
        )

        return Response(MaterialSerializer(material).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="학습 자료 부분 수정",
        operation_description="""
        특정 학습 자료의 일부 정보만 수정합니다.

        수정하고자 하는 필드만 전송하면 됩니다.
        자신이 소유한 과목의 자료만 수정할 수 있습니다.
        """,
        request_body=MaterialSerializer,
        responses={
            200: MaterialSerializer,
            400: "잘못된 요청 데이터",
            401: "인증되지 않은 사용자",
            404: "학습 자료를 찾을 수 없음",
        },
        tags=["학습 자료"],
    )
    def partial_update(self, request, *args, **kwargs):
        """학습 자료 부분 수정"""
        serializer = MaterialSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # 파일 처리
        files = request.FILES.getlist("files")

        update_data = serializer.validated_data.copy()
        if files:
            update_data["files"] = files

        material = MaterialService.update_material(
            kwargs["pk"], request.user, **update_data
        )

        return Response(MaterialSerializer(material).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="학습 자료 삭제",
        operation_description="""
        특정 학습 자료를 삭제합니다.

        업로드된 파일도 함께 삭제됩니다.
        자신이 소유한 과목의 자료만 삭제할 수 있습니다.
        """,
        responses={
            204: "삭제 성공",
            401: "인증되지 않은 사용자",
            404: "학습 자료를 찾을 수 없음",
        },
        tags=["학습 자료"],
    )
    def destroy(self, request, *args, **kwargs):
        """학습 자료 삭제"""
        MaterialService.delete_material(kwargs["pk"], request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

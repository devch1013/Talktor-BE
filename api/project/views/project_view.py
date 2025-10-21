from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.project.exceptions import ProjectExceptions
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
from common.swagger.schema import get_swagger_response_dict


class ProjectViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    """
    프로젝트 관리 API

    사용자의 프로젝트 생성, 조회, 수정, 삭제 기능을 제공합니다.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer

    def get_queryset(self):
        """현재 사용자의 프로젝트만 조회"""
        return Project.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_summary="프로젝트 목록 조회",
        operation_description="""
        현재 로그인한 사용자의 모든 프로젝트을 조회합니다.

        각 프로젝트의 학습 자료 개수와 마지막 활동 날짜를 포함합니다.
        최근 수정일 기준으로 정렬됩니다.
        """,
        responses=get_swagger_response_dict(
            success_response={
                200: ProjectListSerializer(many=True),
            },
            exception_enums=[],
        ),
        tags=["프로젝트"],
    )
    def list(self, request, *args, **kwargs):
        """프로젝트 목록 조회"""
        projects = ProjectService.get_user_projects(request.user)
        serializer = ProjectListSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="프로젝트 생성",
        operation_description="""
        새로운 프로젝트을 생성합니다.

        프로젝트명과 색상 코드를 입력받아 프로젝트을 생성합니다.
        색상 코드는 Hex 형식 (예: #3B82F6)을 사용합니다.
        """,
        request_body=ProjectCreateSerializer,
        responses=get_swagger_response_dict(
            success_response={
                201: ProjectSerializer,
            },
            exception_enums=[],
        ),
        tags=["프로젝트"],
    )
    def create(self, request, *args, **kwargs):
        """프로젝트 생성"""
        serializer = ProjectCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project = ProjectService.create_project(
            user=request.user,
            name=serializer.validated_data["name"],
            color=serializer.validated_data.get("color", "#3B82F6"),
        )

        return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="프로젝트 상세 조회",
        operation_description="""
        특정 프로젝트의 상세 정보를 조회합니다.

        자신이 생성한 프로젝트만 조회할 수 있습니다.
        """,
        responses=get_swagger_response_dict(
            success_response={
                200: ProjectSerializer,
            },
            exception_enums=[ProjectExceptions.PROJECT_NOT_FOUND],
        ),
        tags=["프로젝트"],
    )
    def retrieve(self, request, project_id: int):
        """프로젝트 상세 조회"""
        project = ProjectService.get_project(project_id, request.user)
        serializer = ProjectSerializer(project)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="프로젝트 수정",
        operation_description="""
        특정 프로젝트의 정보를 수정합니다.

        프로젝트명과 색상 코드를 수정할 수 있습니다.
        자신이 생성한 프로젝트만 수정할 수 있습니다.
        """,
        request_body=ProjectSerializer,
        responses=get_swagger_response_dict(
            success_response={
                200: ProjectSerializer,
            },
            exception_enums=[ProjectExceptions.PROJECT_NOT_FOUND],
        ),
        tags=["프로젝트"],
    )
    def update(self, request, project_id: int):
        """프로젝트 수정 (전체)"""
        serializer = ProjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project = ProjectService.update_project(
            project_id, request.user, **serializer.validated_data
        )

        return Response(ProjectSerializer(project).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="프로젝트 부분 수정",
        operation_description="""
        특정 프로젝트의 일부 정보만 수정합니다.

        수정하고자 하는 필드만 전송하면 됩니다.
        자신이 생성한 프로젝트만 수정할 수 있습니다.
        """,
        request_body=ProjectSerializer,
        responses=get_swagger_response_dict(
            success_response={
                200: ProjectSerializer,
            },
            exception_enums=[ProjectExceptions.PROJECT_NOT_FOUND],
        ),
        tags=["프로젝트"],
    )
    def partial_update(self, request, project_id: int):
        """프로젝트 부분 수정"""
        serializer = ProjectSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        project = ProjectService.update_project(
            project_id, request.user, **serializer.validated_data
        )

        return Response(ProjectSerializer(project).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="프로젝트 삭제",
        operation_description="""
        특정 프로젝트을 삭제합니다.

        프로젝트에 속한 모든 학습 자료도 함께 삭제됩니다.
        자신이 생성한 프로젝트만 삭제할 수 있습니다.
        """,
        responses=get_swagger_response_dict(
            success_response={
                204: None,
            },
            exception_enums=[ProjectExceptions.PROJECT_NOT_FOUND],
        ),
        tags=["프로젝트"],
    )
    def destroy(self, request, project_id: int):
        """프로젝트 삭제"""
        ProjectService.delete_project(project_id, request.user)
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

    프로젝트별 학습 자료 생성, 조회, 수정, 삭제 기능을 제공합니다.
    파일 업로드 및 URL 자료 추가를 지원합니다.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = MaterialSerializer

    def get_queryset(self):
        """현재 사용자의 자료만 조회"""
        return Material.objects.filter(project__user=self.request.user)

    @swagger_auto_schema(
        operation_summary="학습 자료 목록 조회",
        operation_description="""
        특정 프로젝트의 모든 학습 자료를 조회합니다.

        파일 타입과 URL 타입 자료를 모두 포함합니다.
        최근 생성일 기준으로 정렬됩니다.
        """,
        responses=get_swagger_response_dict(
            success_response={
                200: MaterialListSerializer(many=True),
            },
            exception_enums=[ProjectExceptions.PROJECT_NOT_FOUND],
        ),
        tags=["학습 자료"],
    )
    def list(self, request, project_id: int):
        """학습 자료 목록 조회"""
        materials = MaterialService.get_project_materials(project_id, request.user)
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
        request_body=MaterialCreateSerializer,
        responses=get_swagger_response_dict(
            success_response={
                201: MaterialSerializer,
            },
            exception_enums=[ProjectExceptions.PROJECT_NOT_FOUND],
        ),
        tags=["학습 자료"],
    )
    def create(self, request, project_id: int):
        """학습 자료 생성"""

        # 프로젝트 조회 (권한 확인)
        project = ProjectService.get_project(project_id, request.user)

        # 요청 데이터 검증
        serializer = MaterialCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # urls와 files 추출
        urls = serializer.validated_data.get("urls", [])
        files = request.FILES.getlist("files")

        # Service를 통해 학습 자료 생성
        materials = MaterialService.create_materials(
            project=project,
            urls=urls,
            files=files,
        )

        # 생성된 자료 목록 반환
        return Response(
            MaterialSerializer(materials, many=True).data,
            status=status.HTTP_201_CREATED,
        )

    @swagger_auto_schema(
        operation_summary="학습 자료 상세 조회",
        operation_description="""
        특정 학습 자료의 상세 정보를 조회합니다.

        업로드된 파일 목록을 포함합니다.
        자신이 소유한 프로젝트의 자료만 조회할 수 있습니다.
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
        자신이 소유한 프로젝트의 자료만 수정할 수 있습니다.
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
        자신이 소유한 프로젝트의 자료만 수정할 수 있습니다.
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
        자신이 소유한 프로젝트의 자료만 삭제할 수 있습니다.
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

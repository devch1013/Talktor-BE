import os
from typing import List

from django.db import transaction
from django.shortcuts import get_object_or_404

from api.project.models import Material, Project
from api.project.models.material import MaterialType
from api.user.models import User
from common.utils.s3_utils import S3KeyPrefix, S3UploadUtil


class ProjectService:
    """과목 관련 비즈니스 로직 처리"""

    @staticmethod
    def create_project(user: User, name: str, color: str = "#3B82F6") -> Project:
        """
        과목 생성

        Args:
            user: 사용자 객체
            name: 과목명
            color: 색상 코드 (hex)

        Returns:
            생성된 과목 객체
        """
        project = Project.objects.create(user=user, name=name, color=color)
        return project

    @staticmethod
    def get_project(project_id: int, user: User) -> Project:
        """
        프로젝트 조회

        Args:
            project_id: 프로젝트 ID
            user: 사용자 객체 (권한 확인용)

        Returns:
            프로젝트 객체
        """
        project = get_object_or_404(Project, id=project_id, user=user)
        return project

    @staticmethod
    def update_project(project_id: int, user: User, **kwargs) -> Project:
        """
        프로젝트 수정

        Args:
            project_id: 프로젝트 ID
            user: 사용자 객체
            **kwargs: 수정할 필드 (name, color)

        Returns:
                수정된 프로젝트 객체
        """
        project = get_object_or_404(Project, id=project_id, user=user)

        for key, value in kwargs.items():
            if hasattr(project, key):
                setattr(project, key, value)

        project.save()
        return project

    @staticmethod
    def delete_project(project_id: int, user: User) -> None:
        """
        프로젝트 삭제

        Args:
            project_id: 프로젝트 ID
            user: 사용자 객체
        """
        project = get_object_or_404(Project, id=project_id, user=user)
        project.delete()

    @staticmethod
    def get_user_projects(user: User) -> List[Project]:
        """
        사용자의 프로젝트 목록 조회

        Args:
            user: 사용자 객체

        Returns:
            프로젝트 목록 (최근 수정일 기준 정렬)
        """
        return Project.objects.filter(user=user).prefetch_related("materials")


class MaterialService:
    """학습 자료 관련 비즈니스 로직 처리"""

    @staticmethod
    @transaction.atomic
    def create_material(
        project: Project,
        title: str,
        material_type: str,
        url: str = None,
        files: List = None,
        page_count: int = 0,
        thumbnail_url: str = None,
    ) -> Material:
        """
        학습 자료 생성

        Args:
            project: 프로젝트 객체
            title: 자료명
            material_type: 자료 타입 ('file' 또는 'url')
            url: 웹 주소 (material_type이 'url'인 경우)
            files: 업로드할 파일 목록 (material_type이 'file'인 경우)
            page_count: 페이지 수
            thumbnail_url: 썸네일 URL

        Returns:
            생성된 자료 객체
        """
        # 자료 생성
        material = Material.objects.create(
            project=project,
            title=title,
            material_type=material_type,
            url=url,
            page_count=page_count,
            thumbnail_url=thumbnail_url,
        )

        # 파일 타입인 경우 파일 업로드 처리
        if material_type == MaterialType.FILE and files:
            MaterialService._upload_files(material, files)

        return material

    @staticmethod
    def _upload_files(material: Material, files: List) -> None:
        """
        파일 업로드 처리 (내부 메서드)

        Args:
            material: 자료 객체
            files: 업로드할 파일 목록
        """
        for file in files:
            file_name = file.name
            file_size = file.size

            s3_key, s3_url = S3UploadUtil.upload(file, S3KeyPrefix.MATERIAL, file_name)
            Material.objects.create(
                url=s3_url,
                title=file_name,
                material_type=MaterialType.FILE,
                metadata={
                    "file_size": file_size,
                },
            )

    @staticmethod
    def get_material(material_id: int, user: User) -> Material:
        """
        학습 자료 조회

        Args:
            material_id: 자료 ID
            user: 사용자 객체 (권한 확인용)

        Returns:
            자료 객체
        """
        material = get_object_or_404(
            Material.objects.select_related("subject"),
            id=material_id,
            subject__user=user,
        )
        return material

    @staticmethod
    @transaction.atomic
    def update_material(material_id: int, user: User, **kwargs) -> Material:
        """
        학습 자료 수정

        Args:
            material_id: 자료 ID
            user: 사용자 객체
            **kwargs: 수정할 필드

        Returns:
            수정된 자료 객체
        """
        material = MaterialService.get_material(material_id, user)

        # files는 별도 처리
        files = kwargs.pop("files", None)

        for key, value in kwargs.items():
            if hasattr(material, key):
                setattr(material, key, value)

        material.save()

        # 파일이 제공된 경우 추가 업로드
        if files:
            MaterialService._upload_files(material, files)

        return material

    @staticmethod
    def delete_material(material_id: int, user: User) -> None:
        """
        학습 자료 삭제

        Args:
            material_id: 자료 ID
            user: 사용자 객체
        """
        material = MaterialService.get_material(material_id, user)

        # 파일 삭제 (실제 파일 시스템에서도 삭제)
        for file in material.files.all():
            if file.file and os.path.isfile(file.file.path):
                os.remove(file.file.path)

        material.delete()

    @staticmethod
    def get_project_materials(project_id: int, user: User) -> List[Material]:
        """
        프로젝트의 학습 자료 목록 조회

        Args:
            project_id: 프로젝트 ID
            user: 사용자 객체

        Returns:
            자료 목록 (최근 생성일 기준 정렬)
        """
        project = get_object_or_404(Project, id=project_id, user=user)
        return Material.objects.filter(project=project)

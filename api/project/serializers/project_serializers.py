from rest_framework import serializers

from api.project.models import Material, Project


class ProjectSerializer(serializers.ModelSerializer):
    """과목 상세 정보 Serializer"""

    class Meta:
        model = Project
        fields = ["id", "name", "color", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProjectListSerializer(serializers.ModelSerializer):
    """
    과목 목록 Serializer
    자료 개수와 마지막 활동 날짜를 포함
    """

    material_count = serializers.SerializerMethodField(help_text="학습 자료 개수")
    last_activity_date = serializers.SerializerMethodField(help_text="마지막 활동 날짜")

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "color",
            "material_count",
            "last_activity_date",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_material_count(self, obj):
        """해당 과목의 학습 자료 개수 반환"""
        return obj.materials.count()

    def get_last_activity_date(self, obj):
        """해당 과목의 마지막 활동 날짜 (가장 최근 자료 업로드 날짜) 반환"""
        last_material = obj.materials.first()  # ordering = ['-created_at']
        return last_material.created_at if last_material else obj.updated_at


class ProjectCreateSerializer(serializers.ModelSerializer):
    """과목 생성 Serializer"""

    class Meta:
        model = Project
        fields = ["name", "color"]


class ProjectIdQuerySerializer(serializers.Serializer):
    """프로젝트 ID 조회 Serializer"""

    project_id = serializers.IntegerField(required=True, help_text="프로젝트 ID")


class MaterialSerializer(serializers.ModelSerializer):
    """
    학습 자료 상세 정보 Serializer
    파일 목록을 포함
    """

    class Meta:
        model = Material
        fields = [
            "id",
            "project",
            "title",
            "material_type",
            "url",
            "page_count",
            "thumbnail_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MaterialListSerializer(serializers.ModelSerializer):
    """
    학습 자료 목록 Serializer
    목록 조회 시 필요한 정보만 포함
    """

    class Meta:
        model = Material
        fields = [
            "id",
            "title",
            "material_type",
            "url",
            "page_count",
            "thumbnail_url",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class MaterialCreateSerializer(serializers.Serializer):
    """
    학습 자료 생성 Serializer
    단일 URL 또는 단일 파일만 지원 (클라이언트에서 병렬 처리)
    """

    material_type = serializers.ChoiceField(
        choices=["url", "file"],
        required=True,
        help_text="자료 타입 (url 또는 file)",
    )
    url = serializers.URLField(
        required=False,
        allow_null=True,
        help_text="웹 주소 (material_type이 url인 경우 필수)",
    )
    file = serializers.FileField(
        required=False,
        allow_null=True,
        help_text="파일 (material_type이 file인 경우 필수)",
    )

    def validate(self, data):
        """
        material_type에 따라 url 또는 file이 필수인지 검증
        """
        material_type = data.get("material_type")

        if material_type == "url":
            if not data.get("url"):
                raise serializers.ValidationError(
                    {"url": "material_type이 url인 경우 url은 필수입니다."}
                )
        elif material_type == "file":
            if not data.get("file"):
                raise serializers.ValidationError(
                    {"file": "material_type이 file인 경우 file은 필수입니다."}
                )

        return data

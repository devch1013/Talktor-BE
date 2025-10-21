from rest_framework import serializers

from api.project.models import Material, Project
from api.project.models.material import MaterialType


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


class MaterialSerializer(serializers.ModelSerializer):
    """
    학습 자료 상세 정보 Serializer
    파일 목록을 포함
    """

    class Meta:
        model = Material
        fields = [
            "id",
            "Project",
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

    file_count = serializers.SerializerMethodField(help_text="파일 개수")

    class Meta:
        model = Material
        fields = [
            "id",
            "title",
            "material_type",
            "url",
            "page_count",
            "thumbnail_url",
            "file_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_file_count(self, obj):
        """해당 자료의 파일 개수 반환"""
        return obj.files.count()


class MaterialCreateSerializer(serializers.Serializer):
    """
    학습 자료 생성 Serializer
    파일 여러 개 동시 업로드 및 URL 지원
    """

    title = serializers.CharField(max_length=200, required=True, help_text="자료명")
    material_type = serializers.ChoiceField(
        choices=MaterialType.choices,
        required=True,
        help_text="자료 타입 (file 또는 url)",
    )
    url = serializers.URLField(
        max_length=500,
        required=False,
        allow_blank=True,
        help_text="웹 주소 (material_type이 url인 경우 필수)",
    )
    files = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        allow_empty=True,
        help_text="업로드할 파일 목록 (material_type이 file인 경우 필수)",
    )
    page_count = serializers.IntegerField(
        default=0, required=False, help_text="페이지 수"
    )
    thumbnail_url = serializers.URLField(
        max_length=500, required=False, allow_blank=True, help_text="썸네일 URL"
    )

    def validate(self, data):
        """자료 타입에 따른 필수 필드 검증"""
        material_type = data.get("material_type")

        if material_type == Material.MATERIAL_TYPE_FILE:
            if not data.get("files"):
                raise serializers.ValidationError(
                    {"files": "파일 타입인 경우 최소 1개 이상의 파일이 필요합니다."}
                )

        elif material_type == Material.MATERIAL_TYPE_URL:
            if not data.get("url"):
                raise serializers.ValidationError(
                    {"url": "URL 타입인 경우 웹 주소가 필요합니다."}
                )

        return data

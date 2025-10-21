import uuid

from django.db import models

from .project import Project


class MaterialType(models.TextChoices):
    FILE = "file", "파일"
    URL = "url", "URL"


class Material(models.Model):
    """
    프로젝트 내부의 학습 자료 객체
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="materials",
        verbose_name="Project",
    )
    title = models.CharField(max_length=200, verbose_name="Title")
    material_type = models.CharField(
        max_length=10,
        choices=MaterialType.choices,
        default=MaterialType.FILE,
        verbose_name="Material Type",
    )
    ## file인 경우는 S3 경로, url인 경우는 웹 주소
    url = models.URLField(max_length=500, null=True, blank=True, verbose_name="URL")
    page_count = models.IntegerField(default=0, verbose_name="Page Count")
    thumbnail_url = models.URLField(
        max_length=500, null=True, blank=True, verbose_name="Thumbnail URL"
    )
    metadata = models.JSONField(default=dict, verbose_name="Metadata")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        db_table = "materials"
        ordering = ["-created_at"]
        verbose_name = "Material"
        verbose_name_plural = "Materials"

    def __str__(self):
        return f"{self.title} ({self.project.name})"

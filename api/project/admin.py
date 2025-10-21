from django.contrib import admin

from api.project.models import Material, Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """프로젝트 관리자 페이지"""

    list_display = ["id", "name", "user", "color", "created_at", "updated_at"]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["name", "user__email"]
    ordering = ["-updated_at"]


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    """자료 관리자 페이지"""

    list_display = [
        "id",
        "title",
        "project",
        "material_type",
        "page_count",
        "created_at",
    ]
    list_filter = ["material_type", "created_at"]
    search_fields = ["title", "project__name"]
    ordering = ["-created_at"]

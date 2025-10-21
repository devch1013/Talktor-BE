from django.contrib import admin

from api.project.models import Material, Project, Quiz, QuizQuestions, QuizAnswerHistory


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


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """퀴즈 관리자 페이지"""

    list_display = [
        "id",
        "project",
        "status",
        "question_type",
        "question_count",
        "difficulty",
        "progress_percentage",
        "created_at",
        "completed_at",
    ]
    list_filter = ["status", "question_type", "difficulty", "created_at"]
    search_fields = ["project__name", "project__user__email"]
    ordering = ["-created_at"]
    readonly_fields = ["id", "created_at", "updated_at", "started_at", "completed_at"]


@admin.register(QuizQuestions)
class QuizQuestionsAdmin(admin.ModelAdmin):
    """퀴즈 문제 관리자 페이지"""

    list_display = [
        "id",
        "quiz",
        "question_preview",
        "created_at",
    ]
    list_filter = ["created_at"]
    search_fields = ["question", "quiz__id"]
    ordering = ["-created_at"]
    readonly_fields = ["id", "created_at", "updated_at"]

    def question_preview(self, obj):
        """문제 미리보기 (50자까지)"""
        return obj.question[:50] + "..." if len(obj.question) > 50 else obj.question

    question_preview.short_description = "문제 미리보기"


@admin.register(QuizAnswerHistory)
class QuizAnswerHistoryAdmin(admin.ModelAdmin):
    """퀴즈 답안 기록 관리자 페이지"""

    list_display = [
        "id",
        "user",
        "quiz_question",
        "answer_preview",
        "is_correct",
        "created_at",
    ]
    list_filter = ["is_correct", "created_at"]
    search_fields = ["user__email", "quiz_question__question"]
    ordering = ["-created_at"]
    readonly_fields = ["id", "created_at", "updated_at"]

    def answer_preview(self, obj):
        """답안 미리보기 (30자까지)"""
        return obj.answer[:30] + "..." if len(obj.answer) > 30 else obj.answer

    answer_preview.short_description = "답안 미리보기"

from django.urls import path

from api.project.views import MaterialViewSet, ProjectViewSet
from api.project.views.quiz_view import QuizViewSet

urlpatterns = [
    # 프로젝트 관련 API
    path(
        "",
        ProjectViewSet.as_view({"get": "list", "post": "create"}),
        name="project-list-create",
    ),
    path(
        "/<int:project_id>",
        ProjectViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="project-detail",
    ),
    # 학습 자료 관련 API
    path(
        "/materials/<str:material_id>",
        MaterialViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="material-detail",
    ),
    path(
        "/<int:project_id>/materials",
        MaterialViewSet.as_view({"get": "list", "post": "create"}),
        name="material-list-create",
    ),
    # 퀴즈 관련 API
    path(
        "/<int:project_id>/quizzes",
        QuizViewSet.as_view({"get": "list"}),
        name="quiz-list",
    ),
    path(
        "/<int:project_id>/quizzes/generate",
        QuizViewSet.as_view({"post": "generate_quiz"}),
        name="quiz-generate",
    ),
    path(
        "/quizzes/<str:pk>",
        QuizViewSet.as_view({"get": "retrieve"}),
        name="quiz-detail",
    ),
    path(
        "/quizzes/<str:pk>/status",
        QuizViewSet.as_view({"get": "get_generation_status"}),
        name="quiz-generation-status",
    ),
    # 퀴즈 풀이 관련 API
    path(
        "/quizzes/<str:pk>/submit-answer",
        QuizViewSet.as_view({"post": "submit_answer"}),
        name="quiz-submit-answer",
    ),
    path(
        "/quizzes/<str:pk>/submit-answers",
        QuizViewSet.as_view({"post": "submit_answers_batch"}),
        name="quiz-submit-answers",
    ),
    path(
        "/quizzes/<str:pk>/result",
        QuizViewSet.as_view({"get": "get_quiz_result"}),
        name="quiz-result",
    ),
]

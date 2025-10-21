from django.urls import path

from api.quiz.views.quiz_view import QuizViewSet

urlpatterns = [
    # 퀴즈 관련 API
    path(
        "",
        QuizViewSet.as_view({"get": "list", "post": "generate_quiz"}),
        name="quiz-list",
    ),
    path(
        "/<str:pk>",
        QuizViewSet.as_view({"get": "retrieve"}),
        name="quiz-detail",
    ),
    path(
        "/<str:pk>/status",
        QuizViewSet.as_view({"get": "get_generation_status"}),
        name="quiz-generation-status",
    ),
    # 퀴즈 풀이 관련 API
    path(
        "/<str:pk>/submit-answer",
        QuizViewSet.as_view({"post": "submit_answer"}),
        name="quiz-submit-answer",
    ),
    path(
        "/<str:pk>/submit-answers",
        QuizViewSet.as_view({"post": "submit_answers_batch"}),
        name="quiz-submit-answers",
    ),
    path(
        "/<str:pk>/result",
        QuizViewSet.as_view({"get": "get_quiz_result"}),
        name="quiz-result",
    ),
]

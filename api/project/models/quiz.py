import uuid

from django.db import models

from api.project.models.material import Material
from api.project.models.project import Project
from api.user.models.user import User
from common.abstract_models.time_stamp_model import TimeStampModel


class QuizStatus(models.TextChoices):
    PENDING = "pending", "대기중"
    PROCESSING = "processing", "처리중"
    COMPLETED = "completed", "완료"
    FAILED = "failed", "실패"


class QuizQuestionType(models.TextChoices):
    MULTIPLE_CHOICE = "multiple_choice", "객관식"
    SHORT_ANSWER = "short_answer", "서술형"
    MIXED = "mixed", "혼합"


class QuizDifficulty(models.TextChoices):
    EASY = "easy", "쉬움"
    MEDIUM = "medium", "보통"
    HARD = "hard", "어려움"


class Quiz(TimeStampModel):
    """
    퀴즈 정보
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="quizzes"
    )
    materials = models.ManyToManyField(Material, related_name="quizzes")

    # 퀴즈 설정
    question_type = models.CharField(
        max_length=20,
        choices=QuizQuestionType.choices,
        default=QuizQuestionType.MULTIPLE_CHOICE,
    )
    question_count = models.IntegerField(default=10)
    difficulty = models.CharField(
        max_length=10, choices=QuizDifficulty.choices, default=QuizDifficulty.MEDIUM
    )

    # 상태 관리
    status = models.CharField(
        max_length=20, choices=QuizStatus.choices, default=QuizStatus.PENDING
    )
    error_message = models.TextField(null=True, blank=True)
    progress_percentage = models.IntegerField(default=0)

    # 타임스탬프
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "quiz_generation_tasks"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Quiz {self.id} - {self.status}"


class QuizQuestions(TimeStampModel):
    """
    퀴즈 문제 정보
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question = models.TextField()

    ## 객관식인 경우 {1: "선택지 1", 2: "선택지 2", 3: "선택지 3", 4: "선택지 4"}
    ## 서술형인 경우 {answer: "정답"}
    answers = models.JSONField(default=dict)

    # 메타데이터
    metadata = models.JSONField(default=dict)

    # 타임스탬프
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "quizzes"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Quiz: {self.id}"


class QuizAnswerHistory(TimeStampModel):
    """
    유저의 퀴즈 풀이 기록
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="quiz_answer_histories"
    )
    quiz_question = models.ForeignKey(
        QuizQuestions, on_delete=models.CASCADE, related_name="answer_histories"
    )
    ## 객관식인 경우 integer 형태, 서술형인 경우 text
    answer = models.TextField()
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "quiz_answer_histories"
        ordering = ["-created_at"]

from rest_framework import serializers

from api.project.models.material import Material
from api.quiz.models import Quiz, QuizAnswerHistory, QuizQuestions
from api.quiz.models.quiz import QuizDifficulty, QuizQuestionType


class QuizCreateSerializer(serializers.Serializer):
    """퀴즈 생성 요청 Serializer"""

    material_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        help_text="퀴즈를 생성할 Material ID 목록",
        min_length=1,
    )
    question_type = serializers.ChoiceField(
        choices=QuizQuestionType.choices,
        default=QuizQuestionType.MULTIPLE_CHOICE,
        help_text="문제 유형 (multiple_choice: 객관식, short_answer: 서술형, mixed: 혼합)",
    )
    question_count = serializers.IntegerField(
        default=10, min_value=1, max_value=50, help_text="문제 개수 (1-50)"
    )
    difficulty = serializers.ChoiceField(
        choices=QuizDifficulty.choices,
        default=QuizDifficulty.MEDIUM,
        help_text="난이도 (easy: 쉬움, medium: 보통, hard: 어려움)",
    )

    def validate_material_ids(self, value):
        """Material ID 유효성 검증"""
        if not value:
            raise serializers.ValidationError(
                "최소 1개 이상의 Material을 선택해야 합니다."
            )

        # Material 존재 여부 확인
        existing_materials = Material.objects.filter(id__in=value)
        if existing_materials.count() != len(value):
            raise serializers.ValidationError(
                "존재하지 않는 Material이 포함되어 있습니다."
            )

        return value


class QuizStatusSerializer(serializers.ModelSerializer):
    """퀴즈 생성 상태 Serializer (Polling용)"""

    material_ids = serializers.SerializerMethodField(
        help_text="선택된 Material ID 목록"
    )
    estimated_time = serializers.SerializerMethodField(
        help_text="예상 소요 시간 (초 단위)"
    )

    class Meta:
        model = Quiz
        fields = [
            "id",
            "status",
            "question_type",
            "question_count",
            "difficulty",
            "material_ids",
            "progress_percentage",
            "error_message",
            "estimated_time",
            "created_at",
            "updated_at",
            "started_at",
            "completed_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "progress_percentage",
            "error_message",
            "created_at",
            "updated_at",
            "started_at",
            "completed_at",
        ]

    def get_material_ids(self, obj):
        """선택된 Material ID 목록 반환"""
        return [str(material.id) for material in obj.materials.all()]

    def get_estimated_time(self, obj):
        """예상 소요 시간 계산 (문제 개수 * 2초)"""
        return obj.question_count * 2


class QuizQuestionSerializer(serializers.ModelSerializer):
    """퀴즈 문제 Serializer (문제 조회용)"""

    question_type = serializers.SerializerMethodField(help_text="문제 유형")
    choices = serializers.SerializerMethodField(
        help_text="객관식 선택지 (객관식인 경우만)"
    )

    class Meta:
        model = QuizQuestions
        fields = [
            "id",
            "question",
            "question_type",
            "choices",
            "metadata",
        ]
        read_only_fields = ["id", "metadata"]

    def get_question_type(self, obj):
        """문제 유형 반환"""
        # metadata에서 question_type 추출
        return obj.metadata.get("question_type", "multiple_choice")

    def get_choices(self, obj):
        """객관식 선택지 반환 (answers에서 answer 키 제외)"""
        if self.get_question_type(obj) == "multiple_choice":
            # answers에서 answer 키를 제외하고 선택지만 반환
            return {k: v for k, v in obj.answers.items() if k != "answer"}
        return None


class QuizQuestionWithAnswerSerializer(serializers.ModelSerializer):
    """퀴즈 문제 Serializer (정답 포함 - 결과 조회용)"""

    question_type = serializers.SerializerMethodField(help_text="문제 유형")
    choices = serializers.SerializerMethodField(
        help_text="객관식 선택지 (객관식인 경우만)"
    )
    correct_answer = serializers.SerializerMethodField(help_text="정답")
    explanation = serializers.SerializerMethodField(help_text="해설")

    class Meta:
        model = QuizQuestions
        fields = [
            "id",
            "question",
            "question_type",
            "choices",
            "correct_answer",
            "explanation",
            "metadata",
        ]
        read_only_fields = ["id", "metadata"]

    def get_question_type(self, obj):
        """문제 유형 반환"""
        return obj.metadata.get("question_type", "multiple_choice")

    def get_choices(self, obj):
        """객관식 선택지 반환"""
        if self.get_question_type(obj) == "multiple_choice":
            return {k: v for k, v in obj.answers.items() if k != "answer"}
        return None

    def get_correct_answer(self, obj):
        """정답 반환"""
        return obj.answers.get("answer")

    def get_explanation(self, obj):
        """해설 반환"""
        return obj.metadata.get("explanation", "")


class QuizSerializer(serializers.ModelSerializer):
    """퀴즈 상세 정보 Serializer"""

    material_ids = serializers.SerializerMethodField(
        help_text="사용된 Material ID 목록"
    )
    material_titles = serializers.SerializerMethodField(
        help_text="사용된 Material 제목 목록"
    )
    questions = QuizQuestionSerializer(many=True, read_only=True)
    total_questions = serializers.SerializerMethodField(help_text="전체 문제 개수")

    class Meta:
        model = Quiz
        fields = [
            "id",
            "project",
            "material_ids",
            "material_titles",
            "question_type",
            "difficulty",
            "total_questions",
            "questions",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_material_ids(self, obj):
        """사용된 Material ID 목록 반환"""
        return [str(material.id) for material in obj.materials.all()]

    def get_material_titles(self, obj):
        """사용된 Material 제목 목록 반환"""
        return [material.title for material in obj.materials.all()]

    def get_total_questions(self, obj):
        """전체 문제 개수 반환"""
        return obj.questions.count()


class QuizListSerializer(serializers.ModelSerializer):
    """퀴즈 목록 Serializer"""

    material_count = serializers.SerializerMethodField(help_text="사용된 Material 개수")
    material_titles = serializers.SerializerMethodField(
        help_text="사용된 Material 제목 목록 (최대 3개)"
    )
    total_questions = serializers.SerializerMethodField(help_text="전체 문제 개수")

    class Meta:
        model = Quiz
        fields = [
            "id",
            "material_count",
            "material_titles",
            "question_type",
            "difficulty",
            "total_questions",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_material_count(self, obj):
        """사용된 Material 개수 반환"""
        return obj.materials.count()

    def get_material_titles(self, obj):
        """사용된 Material 제목 목록 반환 (최대 3개)"""
        materials = obj.materials.all()[:3]
        titles = [material.title for material in materials]
        if obj.materials.count() > 3:
            titles.append("...")
        return titles

    def get_total_questions(self, obj):
        """전체 문제 개수 반환"""
        return obj.questions.count()


# ============ 퀴즈 풀이 관련 Serializers ============


class QuizAnswerSubmitSerializer(serializers.Serializer):
    """퀴즈 답안 제출 Serializer"""

    question_id = serializers.UUIDField(required=True, help_text="문제 ID")
    answer = serializers.CharField(
        required=True, help_text="답안 (객관식: 선택지 번호, 서술형: 텍스트)"
    )


class QuizAnswerBatchSubmitSerializer(serializers.Serializer):
    """퀴즈 답안 일괄 제출 Serializer"""

    answers = serializers.ListField(
        child=QuizAnswerSubmitSerializer(),
        required=True,
        help_text="답안 목록",
        min_length=1,
    )


class QuizAnswerHistorySerializer(serializers.ModelSerializer):
    """퀴즈 답안 기록 Serializer"""

    question = QuizQuestionWithAnswerSerializer(source="quiz_question", read_only=True)
    user_answer = serializers.CharField(source="answer", read_only=True)

    class Meta:
        model = QuizAnswerHistory
        fields = [
            "id",
            "question",
            "user_answer",
            "is_correct",
            "created_at",
        ]
        read_only_fields = ["id", "is_correct", "created_at"]


class QuizResultSerializer(serializers.Serializer):
    """퀴즈 결과 Serializer"""

    quiz_id = serializers.UUIDField(help_text="퀴즈 ID")
    total_questions = serializers.IntegerField(help_text="전체 문제 개수")
    correct_count = serializers.IntegerField(help_text="정답 개수")
    wrong_count = serializers.IntegerField(help_text="오답 개수")
    score = serializers.FloatField(help_text="점수 (정답률 %)")
    answers = QuizAnswerHistorySerializer(many=True, help_text="문제별 결과")

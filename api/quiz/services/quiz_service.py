import threading
import time
from typing import Dict, List

from django.db import transaction
from django.utils import timezone

from api.project.models import Material, Project
from api.quiz.models import (
    Quiz,
    QuizAnswerHistory,
    QuizDifficulty,
    QuizQuestions,
    QuizQuestionType,
)
from api.user.models import User


class QuizService:
    """퀴즈 생성 및 관리 서비스"""

    @staticmethod
    @transaction.atomic
    def create_quiz(
        project_id: int,
        material_ids: List[str],
        question_type: QuizQuestionType,
        question_count: int,
        difficulty: QuizDifficulty,
    ) -> Quiz:
        """
        퀴즈 생성 작업 생성 및 백그라운드에서 실행

        Args:
            project: 프로젝트
            material_ids: Material ID 목록
            question_type: 문제 유형
            question_count: 문제 개수
            difficulty: 난이도

        Returns:
            Quiz: 생성된 퀴즈 객체
        """
        project = Project.objects.get(id=project_id)

        # 1. Material 조회 및 검증
        materials = Material.objects.filter(id__in=material_ids)

        if materials.count() != len(material_ids):
            raise ValueError(
                "일부 Material이 존재하지 않거나 해당 프로젝트에 속하지 않습니다."
            )

        # 2. Quiz 생성
        quiz = Quiz.objects.create(
            project=project,
            question_type=question_type,
            question_count=question_count,
            difficulty=difficulty,
            status="pending",
        )

        # 3. ManyToMany 관계 설정
        quiz.materials.set(materials)

        # 4. 백그라운드에서 퀴즈 생성 시작
        thread = threading.Thread(
            target=QuizService._generate_quiz_background, args=(quiz.id,)
        )
        thread.daemon = True
        thread.start()

        return quiz

    @staticmethod
    def _generate_quiz_background(quiz_id: str):
        """
        백그라운드에서 퀴즈 생성 (별도 스레드)

        Args:
            quiz_id: Quiz ID
        """
        try:
            # Quiz 조회
            quiz = Quiz.objects.get(id=quiz_id)

            # 상태를 processing으로 변경
            quiz.status = "processing"
            quiz.started_at = timezone.now()
            quiz.progress_percentage = 0
            quiz.save()

            # Mock AI 퀴즈 생성 함수 호출
            questions = QuizService._mock_generate_quiz_with_langgraph(quiz)

            # QuizQuestions 객체 생성
            with transaction.atomic():
                for question_data in questions:
                    QuizQuestions.objects.create(
                        quiz=quiz,
                        question=question_data["question"],
                        answers=question_data["answers"],
                        metadata=question_data["metadata"],
                    )

                # Quiz 상태 업데이트
                quiz.status = "completed"
                quiz.completed_at = timezone.now()
                quiz.progress_percentage = 100
                quiz.save()

        except Exception as e:
            # 에러 발생 시 상태 업데이트
            try:
                quiz = Quiz.objects.get(id=quiz_id)
                quiz.status = "failed"
                quiz.error_message = str(e)
                quiz.completed_at = timezone.now()
                quiz.save()
            except Exception:
                pass  # Quiz 조회 실패 시 무시

    @staticmethod
    def _mock_generate_quiz_with_langgraph(quiz: Quiz) -> List[dict]:
        """
        Mock AI 퀴즈 생성 함수 (LangGraph 대체용)
        실제로는 여기에 LangGraph를 사용한 AI 로직이 들어갑니다.

        Args:
            quiz: Quiz 객체

        Returns:
            List[dict]: 생성된 문제 목록
        """
        questions = []

        # 문제 생성 시뮬레이션 (각 문제마다 2초 소요)
        for i in range(quiz.question_count):
            # Progress 업데이트
            quiz.progress_percentage = int(((i + 1) / quiz.question_count) * 100)
            quiz.save()

            # 문제 생성 시간 시뮬레이션
            time.sleep(2)

            # Mock 문제 생성
            if quiz.question_type == "multiple_choice" or (
                quiz.question_type == "mixed" and i % 2 == 0
            ):
                question = {
                    "question": f"Mock 문제 {i + 1}: 이것은 객관식 문제입니다. ({quiz.difficulty} 난이도)",
                    "answers": {
                        "1": "선택지 1",
                        "2": "선택지 2 (정답)",
                        "3": "선택지 3",
                        "4": "선택지 4",
                        "answer": "2",  # 정답은 2번
                    },
                    "metadata": {
                        "question_type": "multiple_choice",
                        "difficulty": quiz.difficulty,
                        "explanation": "이 문제의 정답은 '선택지 2'입니다. Mock 생성된 해설입니다.",
                        "question_number": i + 1,
                    },
                }
            else:
                question = {
                    "question": f"Mock 문제 {i + 1}: 이것은 서술형 문제입니다. ({quiz.difficulty} 난이도)",
                    "answers": {
                        "answer": "Mock 정답입니다.",
                    },
                    "metadata": {
                        "question_type": "short_answer",
                        "difficulty": quiz.difficulty,
                        "explanation": "서술형 문제의 모범 답안입니다. Mock 생성된 해설입니다.",
                        "question_number": i + 1,
                    },
                }

            questions.append(question)

        return questions

    @staticmethod
    def get_quiz_status(quiz_id: str, user: User) -> Quiz:
        """
        퀴즈 생성 상태 조회

        Args:
            quiz_id: Quiz ID
            user: 사용자 (권한 검증용)

        Returns:
            Quiz: 퀴즈 객체

        Raises:
            Quiz.DoesNotExist: 퀴즈를 찾을 수 없음
            PermissionError: 권한 없음
        """
        quiz = Quiz.objects.get(id=quiz_id)

        if quiz.project.user != user:
            raise PermissionError("해당 퀴즈에 접근할 권한이 없습니다.")

        return quiz

    @staticmethod
    def get_quiz(quiz_id: str, user: User) -> Quiz:
        """
        퀴즈 ID로 퀴즈 조회

        Args:
            quiz_id: Quiz ID
            user: 사용자 (권한 검증용)

        Returns:
            Quiz: 퀴즈 객체

        Raises:
            Quiz.DoesNotExist: 퀴즈를 찾을 수 없음
            PermissionError: 권한 없음
        """
        quiz = Quiz.objects.get(id=quiz_id)

        if quiz.project.user != user:
            raise PermissionError("해당 퀴즈에 접근할 권한이 없습니다.")

        if quiz.status != "completed":
            raise ValueError("퀴즈 생성이 아직 완료되지 않았습니다.")

        return quiz

    @staticmethod
    def get_project_quizzes(project_id: int, user: User) -> List[Quiz]:
        """
        프로젝트의 모든 퀴즈 조회

        Args:
            project_id: 프로젝트 ID
            user: 사용자 (권한 검증용)

        Returns:
            List[Quiz]: 퀴즈 목록

        Raises:
            PermissionError: 권한 없음
        """
        project = Project.objects.get(id=project_id, user=user)

        if project.user != user:
            raise PermissionError("해당 프로젝트에 접근할 권한이 없습니다.")

        return Quiz.objects.filter(project=project, status="completed").order_by(
            "-created_at"
        )

    # ============ 퀴즈 풀이 관련 서비스 ============

    @staticmethod
    @transaction.atomic
    def submit_answer(user: User, question_id: str, answer: str) -> QuizAnswerHistory:
        """
        퀴즈 답안 제출 (단일 문제)

        Args:
            user: 사용자
            question_id: 문제 ID
            answer: 답안

        Returns:
            QuizAnswerHistory: 답안 기록

        Raises:
            QuizQuestions.DoesNotExist: 문제를 찾을 수 없음
        """
        question = QuizQuestions.objects.get(id=question_id)

        # 정답 확인
        correct_answer = question.answers.get("answer")
        is_correct = str(answer).strip() == str(correct_answer).strip()

        # 기존 답안이 있으면 업데이트, 없으면 생성
        answer_history, created = QuizAnswerHistory.objects.update_or_create(
            user=user,
            quiz_question=question,
            defaults={
                "answer": answer,
                "is_correct": is_correct,
            },
        )

        return answer_history

    @staticmethod
    @transaction.atomic
    def submit_answers_batch(
        user: User, answers: List[Dict[str, str]]
    ) -> List[QuizAnswerHistory]:
        """
        퀴즈 답안 일괄 제출

        Args:
            user: 사용자
            answers: 답안 목록 [{"question_id": "...", "answer": "..."}, ...]

        Returns:
            List[QuizAnswerHistory]: 답안 기록 목록
        """
        answer_histories = []

        for answer_data in answers:
            answer_history = QuizService.submit_answer(
                user=user,
                question_id=answer_data["question_id"],
                answer=answer_data["answer"],
            )
            answer_histories.append(answer_history)

        return answer_histories

    @staticmethod
    def get_quiz_result(user: User, quiz_id: str) -> Dict:
        """
        퀴즈 결과 조회

        Args:
            user: 사용자
            quiz_id: Quiz ID

        Returns:
            Dict: 퀴즈 결과
            {
                "quiz_id": "...",
                "total_questions": 10,
                "correct_count": 8,
                "wrong_count": 2,
                "score": 80.0,
                "answers": [...]
            }

        Raises:
            Quiz.DoesNotExist: 퀴즈를 찾을 수 없음
        """
        quiz = Quiz.objects.get(id=quiz_id)

        # 퀴즈의 모든 문제 조회
        questions = quiz.questions.all()
        total_questions = questions.count()

        # 사용자의 답안 기록 조회
        answer_histories = QuizAnswerHistory.objects.filter(
            user=user, quiz_question__quiz=quiz
        ).select_related("quiz_question")

        # 정답/오답 개수 계산
        correct_count = answer_histories.filter(is_correct=True).count()
        wrong_count = total_questions - correct_count
        score = (correct_count / total_questions * 100) if total_questions > 0 else 0

        return {
            "quiz_id": str(quiz.id),
            "total_questions": total_questions,
            "correct_count": correct_count,
            "wrong_count": wrong_count,
            "score": round(score, 2),
            "answers": answer_histories,
        }

    @staticmethod
    def get_user_answer_history(user: User, quiz_id: str) -> List[QuizAnswerHistory]:
        """
        사용자의 퀴즈 답안 기록 조회

        Args:
            user: 사용자
            quiz_id: Quiz ID

        Returns:
            List[QuizAnswerHistory]: 답안 기록 목록
        """
        return QuizAnswerHistory.objects.filter(
            user=user, quiz_question__quiz_id=quiz_id
        ).select_related("quiz_question")

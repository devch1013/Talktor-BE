import os

import django
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
if not settings.configured:
    django.setup()

from langchain.chat_models import init_chat_model


class TestLLMInitialize:
    def test_llm_initialize(self):
        # sys.stdout.reconfigure(encoding="utf-8")

        model = init_chat_model("openai:gpt-5-mini", temperature=0)
        print(model)

        response = model.invoke("Hello, how are you?")
        print(response.content)

    def test_make_questions(self):
        # 변수 정의 (여기에 값을 넣으면 됨)
        data_file_path = "llm/documents/ML1.md"  # 문서 txt 파일 경로
        num_questions = 5  # 생성할 문제 개수
        output_file_path = "llm/tests/quiz_output4.txt"  # 결과 저장 경로

        # 프롬프트 파일 읽기
        prompt_file_path = "llm/prompts/create_quizzes.prompt.txt"
        with open(prompt_file_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()

        # 문서 파일 읽기
        with open(data_file_path, "r", encoding="utf-8") as f:
            data = f.read()

        # 프롬프트에 변수 삽입
        prompt = prompt_template.format(data=data, num_questions=num_questions)

        # LLM 호출
        model = init_chat_model("openai:gpt-5", temperature=0.2)
        response = model.invoke(prompt)

        # 결과를 txt 파일로 저장
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(response.content)

        print(f"퀴즈가 {output_file_path}에 저장되었습니다.")
        print(response.content)

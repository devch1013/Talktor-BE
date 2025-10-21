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

    def test_graph(self):
        pass

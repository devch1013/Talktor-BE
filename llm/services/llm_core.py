from langchain.chat_models import init_chat_model


class LLMCore:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "model"):
            self.model = init_chat_model("openai:gpt-5-mini", temperature=0)

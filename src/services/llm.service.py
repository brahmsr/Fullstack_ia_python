from langchain_ollama import ChatOllama

class LLMService:

    def __init__(self, model):
        self.llm = ChatOllama(
            model=model,
            temperature=0
        )

    def get_llm(self):
        return self.llm
from langchain_ollama import OllamaEmbeddings

class EmbeddingService:

    def __init__(self, model):

        self.embeddings = OllamaEmbeddings(
            model=model
        )

    def get_embeddings(self):

        return self.embeddings
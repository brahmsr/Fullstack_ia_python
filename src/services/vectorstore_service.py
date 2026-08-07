from langchain_community.vectorstores import FAISS
import os

class VectorStoreService:

    def __init__(self, embeddings):

        self.embeddings = embeddings
        self.vectorstore = None

    def existe_vectorstore(self, pasta):
        return os.path.exists(os.path.join(pasta, "index.faiss")) and \
        os.path.exists(os.path.join(pasta, "index.pkl"))

    def criar_vectorstore(self, chunks):

        return FAISS.from_documents(chunks, self.embeddings)

    def salvar_vectorstore(self, pasta):
        self.vectorstore.save_local(pasta)

    def carregar_vectorstore(self, pasta):
        self.vectorstore = FAISS.load_local(
            pasta, 
            self.embeddings,
            allow_dangerous_deserialization=True
        )

    def get_retriever(self):
        return self.vectorstore.as_retriever()
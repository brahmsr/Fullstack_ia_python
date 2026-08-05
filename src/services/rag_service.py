from langchain_classic.chains import RetrievalQA

class RAGService:

    def __init__(self, llm_service, vectorstore_service):

        self.llm = llm_service.get_llm()

        self.retriever = vectorstore_service.get_retriever()

        self.chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=self.retriever,
            chain_type="stuff"
        )

    def perguntar(self, pergunta: str):

        return self.chain.invoke(
            {"query": pergunta}
        )["result"]
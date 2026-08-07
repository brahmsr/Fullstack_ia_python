from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

PROMPT_TEMPLATE = """Você é um assistente técnico de manutenção industrial. Responda sempre em português do Brasil, mesmo que o contexto ou a pergunta estejam em outro idioma.

Use o contexto abaixo para responder à pergunta. Se não souber a resposta com base no contexto, diga que não encontrou essa informação na documentação.

Contexto:
{context}

Pergunta:
{question}

Resposta em português:"""

class RAGService:

    def __init__(self, llm_service, vectorstore_service):

        self.llm = llm_service.get_llm()

        self.retriever = vectorstore_service.get_retriever()

        self.chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=self.retriever,
            chain_type="stuff",
            chain_type_kwargs={
                "prompt": PromptTemplate(
                    template=PROMPT_TEMPLATE,
                    input_variables=["context", "question"]
                )
            }
        )

    def perguntar(self, pergunta: str):

        return self.chain.invoke(
            {"query": pergunta}
        )["result"]
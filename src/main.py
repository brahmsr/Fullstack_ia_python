import json

from services.pdf_service import PDFService
from services.chunk_service import ChunkService
from services.embedding_service import EmbeddingService
from services.vectorstore_service import VectorStoreService
from services.llm_service import LLMService
from services.rag_service import RAGService

print("Iniciando o processo de ingestão de documentos...")

# Carregar o arquivo de configuração
with open("config/config.json", "r") as f:
    config = json.load(f)

print("Carregando documentos...")
pdf_service = PDFService()
documentos = pdf_service.carregar_documentos(config["DATA_DIR"])

print("Gerando chunks...")
chunk_service = ChunkService()
chunks = chunk_service.gerar_chunks(documentos)

# embeddings + vectorstore
print("Gerando embeddings e vectorstore...")
embedding_service = EmbeddingService(config["EMBEDDING_MODEL"])
vector_service = VectorStoreService(
    embedding_service.get_embeddings()
)

vector_service.criar(chunks)

vector_service.salvar(config["VECTOR_DIR"])

# RAG
print("Iniciando RAG...")
llm_service = LLMService(config["MODEL"])
rag = RAGService(
    llm_service,
    vector_service
)

print(
    rag.perguntar(
        "Como corrigir o problema de cocked_rotor?"
    )
)
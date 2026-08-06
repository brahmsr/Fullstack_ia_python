from sensor_service import carregar_dados_bd
from src.services.prediction_service import PredictionService
from src.services.train_service import TrainService
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
print("Vectorstore criado")
vector_service.salvar(config["VECTOR_DIR"])
print("Vectorstore salvo")

# RAG
print("Iniciando RAG...")
llm_service = LLMService(config["MODEL"])
rag = RAGService(
    llm_service,
    vector_service
)

# Modelo de predição
print("Validando se o modelo já foi treinado...")
if TrainService.is_trained():
    print("Modelo já treinado...")
    metrics = TrainService.get_metrics()
    print(f"({metrics['algorithm']}) ")
    
else:
    print("Modelo não encontrado. Iniciando treinamento...")
    TrainService.train()

# Pergunta de teste RAG
print(
    rag.perguntar(
        "Como corrigir o problema de cocked_rotor?"
    )
)

# Teste de predição
df = carregar_dados_bd()
prediction = PredictionService()
ultima_leitura = df.iloc[-1].drop("fault").to_dict()
resultado = prediction.predict(ultima_leitura)

print(resultado)

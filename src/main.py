import os
import subprocess
import sys
import pygame

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)

#musiquinha de elevador
pygame.mixer.init()
pygame.mixer.music.load(os.path.join(SRC_DIR, "misc", "waitmusic.mp3"))
pygame.mixer.music.play(-1)

print("Iniciando os imports...")

from services.sensor_service import carregar_dados_bd
from services.prediction_service import PredictionService
from services.train_service import TrainService
import json

from services.pdf_service import PDFService
from services.chunk_service import ChunkService
from services.embedding_service import EmbeddingService
from services.vectorstore_service import VectorStoreService
from services.llm_service import LLMService
from services.rag_service import RAGService

print("Iniciando o processo de ingestão de documentos...")

# Carregar o arquivo de configuração
with open(os.path.join(SRC_DIR, "config", "config.json"), "r") as f:
    config = json.load(f)

print("Carregando documentos...")
vector_path = os.path.join(ROOT_DIR, config["VECTOR_STORE_DIR"])
embedding_service = EmbeddingService(config["EMBEDDING_MODEL"])
vector_service = VectorStoreService(embedding_service.get_embeddings())

if vector_service.existe_vectorstore(vector_path):
    print("vectorstore já existe, carregando do disco...")
    vector_service.carregar_vectorstore(vector_path)
    print("vectorstore carregado")
else:
    pdf_service = PDFService()
    documentos = pdf_service.carregar_documentos(os.path.join(SRC_DIR, config["DATA_DIR"]))

    print("Gerando chunks...")
    chunk_service = ChunkService()
    chunks = chunk_service.gerar_chunks(documentos)

    # embeddings e vectorstore
    print("Gerando embeddings e vectorstore...")
    vector_service.vectorstore = vector_service.criar_vectorstore(chunks)
    print("vectorstore criado")
    vector_service.salvar_vectorstore(vector_path)
    print("vectorstore salvo")

# RAG
print("iniciando RAG...")
llm_service = LLMService(config["MODEL"])
rag = RAGService(
    llm_service,
    vector_service
)

# Modelo de predição
print("validando se o modelo já foi treinado...")
if TrainService.is_trained():
    print("Modelo já treinado...")
    metrics = TrainService.get_metrics()
    print(f"({metrics['algorithm']}) ")
    
else:
    print("modelo não encontrado. Iniciando treinamento...")
    TrainService.train()

# Predição de um novo evento
df = carregar_dados_bd()
prediction = PredictionService()
ultima_leitura = df.iloc[-1].drop("fault").to_dict()
resultado = prediction.predict(ultima_leitura)

print(resultado)

# A leitura só é encaminhada ao RAG se representar um problema real, os estados operacionais (normal, baseline, teste, acelerando, motor_desligado) não geram consulta de correção.
if resultado["is_state"]:
    print(
        f"leitura corresponde ao estado operacional '{resultado['fault']}'. "
        "nenhuma ação de manutenção é necessária."
    )
else:
    print(
        rag.perguntar(
            f"como corrigir o problema de {resultado['fault']}?"
        )
    )

pygame.mixer.music.stop()

#start frontend
subprocess.run(
    [sys.executable, "-m", "streamlit", "run", os.path.join(SRC_DIR, "views", "init_front.py")],
    cwd=SRC_DIR,
)
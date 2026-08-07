import sys
import os

_SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(_SRC_DIR)
sys.path.append(os.path.join(_SRC_DIR, 'services'))

import json
import streamlit as st
from sensor_service import carregar_dados_bd
from services.prediction_service import PredictionService
from services.fault_labels import canonicalizar_fault
from services.embedding_service import EmbeddingService
from services.vectorstore_service import VectorStoreService
from services.llm_service import LLMService
from services.rag_service import RAGService

st.set_page_config(page_title="Chat de Manutenção", layout="wide")
st.title("Chat de Manutenção")

if st.button("Voltar ao dashboard", icon=":material/bar_chart:", type="secondary"):
    st.switch_page("dashboard_view.py")

with open(os.path.join(_SRC_DIR, "config", "config.json"), "r", encoding="utf-8") as f:
    config = json.load(f)

VECTOR_DIR = os.path.join(_SRC_DIR, "..", config["VECTOR_STORE_DIR"])

# Score é a distância L2 do FAISS (quanto menor, mais relevante). fora do limite deixei como "sem documentação", só falar de problemas documentados.
LIMITE_RELEVANCIA = 1.0


@st.cache_resource
def carregar_rag():
    embedding_service = EmbeddingService(config["EMBEDDING_MODEL"])
    vector_service = VectorStoreService(embedding_service.get_embeddings())
    vector_service.carregar_vectorstore(VECTOR_DIR)
    llm_service = LLMService(config["MODEL"])
    return RAGService(llm_service, vector_service), vector_service


try:
    rag, vector_service = carregar_rag()
except Exception as e:
    st.error(f"Não foi possível carregar a base de documentos (o Ollama está rodando?): {e}")
    st.stop()


def possui_documentacao(pergunta: str) -> bool:
    resultados = vector_service.vectorstore.similarity_search_with_score(pergunta, k=4)
    if not resultados:
        return False
    return min(score for _, score in resultados) <= LIMITE_RELEVANCIA


def responder(pergunta: str) -> str:
    if not possui_documentacao(pergunta):
        return (
            "Ainda não encontrei documentação sobre esse problema na base atual. "
            "Cadastre um documento orientativo para esse defeito na aba de Upload "
            "para que eu possa ajudar da próxima vez."
        )
    return rag.perguntar(pergunta)


@st.cache_data(ttl=300)
def carregar_ultimo_evento():
    df = carregar_dados_bd()
    ultima = df.iloc[-1].drop("fault").to_dict()
    return PredictionService().predict(ultima)


if "mensagens" not in st.session_state:
    st.session_state["mensagens"] = []

evento = carregar_ultimo_evento()
familia = canonicalizar_fault(evento["fault"])

with st.container(border=True):
    if evento["is_state"]:
        st.info(
            f"Último evento registrado: **{familia}** "
            "(estado operacional, sem ação necessária)."
        )
    else:
        col1, col2 = st.columns([3, 1])
        col1.warning(
            f"Último evento registrado: falha **{familia}** "
            f"(confiança {evento['confidence']:.0%})."
        )
        if col2.button("Perguntar como corrigir", icon=":material/build:"):
            pergunta_rapida = f"Como corrigir o problema de {familia.replace('_', ' ')}?"
            st.session_state["mensagens"].append({"role": "user", "content": pergunta_rapida})
            st.session_state["mensagens"].append(
                {"role": "assistant", "content": responder(pergunta_rapida)}
            )

for msg in st.session_state["mensagens"]:
    avatar = ":material/smart_toy:" if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

prompt = st.chat_input("Pergunte sobre uma falha ou como corrigi-la...")
if prompt:
    st.session_state["mensagens"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=":material/smart_toy:"):
        with st.spinner("Consultando a base de documentos..."):
            resposta = responder(prompt)
        st.markdown(resposta)

    st.session_state["mensagens"].append({"role": "assistant", "content": resposta})

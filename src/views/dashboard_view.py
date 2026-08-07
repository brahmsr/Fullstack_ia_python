import sys
import os

_SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(_SRC_DIR)
sys.path.append(os.path.join(_SRC_DIR, 'services'))

import streamlit as st
import pandas as pd
from datetime import datetime
from sensor_service import carregar_dados_bd
from services.fault_labels import is_state, canonicalizar_fault, STATE_LABELS
from services.train_service import TrainService
from services.prediction_service import PredictionService

st.set_page_config(page_title="Manutenção de equipamentos", layout="wide")
st.title("Dashboard de Manutenção de equipamentos")

@st.cache_data(ttl=300)
def carregar_dados():
    return carregar_dados_bd()

df = carregar_dados()
df["familia"] = df["fault"].apply(canonicalizar_fault)
df["is_state"] = df["familia"].isin(STATE_LABELS)

if st.button("Abrir o chat", icon=":material/smart_toy:", type="primary"):
    st.switch_page("chat_view.py")

col1, col2, col3 = st.columns(3) # gera colunas para métricas
col1.metric("Todas as Leituras", len(df), icon=":material/settings:", border=True)
col2.metric("Registros Normais", int((~df["is_state"]).sum()), icon=":material/check_circle:", border=True)
col3.metric("Registros de Erro", int(df["is_state"].sum()), icon=":material/cancel:", border=True)

#falhas
falhas = df[~df["is_state"]]
st.subheader("Quantidade de ocorrências por falha")
st.bar_chart(falhas["familia"].value_counts(), color="#1B4855")

st.subheader("Linha do tempo por falha")
tipo = st.selectbox("Filtrar por falha", ["Todas"] + sorted(falhas["familia"].unique()))
dados_freq = falhas if tipo == "Todas" else falhas[falhas["familia"] == tipo]
st.line_chart(dados_freq.set_index("created_at").resample("D").size(), color="#0082C8")

# infos do modelo
metrics = TrainService.get_metrics()
if metrics:
    st.subheader("Qualidade do modelo")
    st.markdown("Podemos verificar que está dentro do esperado para um modelo com essas medições")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Acurácia", f"{metrics['accuracy']:.2%}", border=True)
    col2.metric("Precisão", f"{metrics['precision']:.2%}", border=True)
    col3.metric("Recall", f"{metrics['recall']:.2%}", border=True)
    col4.metric("F1", f"{metrics['f1']:.2%}", border=True)
    st.subheader("Importância das features")
    st.bar_chart(pd.Series(metrics["feature_importance"]))
else:
    st.warning("Modelo ainda não foi treinado.")

# Predição
st.subheader("Predição")
st.markdown("Podemos verificar que está dentro do esperado para um modelo com essas medições")
ultima = df.iloc[-1].drop(["fault", "is_state"]).to_dict()
resultado = PredictionService().predict(ultima)
col1, col2 = st.columns(2)
col1.metric("Tipo de defeito previsto", canonicalizar_fault(resultado["fault"]))
col2.metric("Confiança", f"{resultado['confidence']:.2%}")

if resultado["is_state"]:
    st.info("Estado operacional — nenhuma ação necessária.")
else:
    st.warning("Falha real detectada — consulte a aba Chat para instruções de correção.")

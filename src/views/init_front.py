import streamlit as st


def inicio():
    st.title("Manutenção Prescritiva")
    st.write("Escolha uma seção:")

    col1, col2 = st.columns(2)
    if col1.button("Dashboard", icon=":material/monitoring:", use_container_width=True, type="primary"):
        st.switch_page(DASHBOARD)
    if col2.button("Chat", icon=":material/smart_toy:", use_container_width=True, type="secondary"):
        st.switch_page(CHAT)


HOME = st.Page(inicio, title="Início", icon=":material/home:", default=True,)
DASHBOARD = st.Page("dashboard_view.py", title="Dashboard", icon=":material/monitoring:")
CHAT = st.Page("chat_view.py", title="Chat", icon=":material/smart_toy:")

pg = st.navigation([HOME, DASHBOARD, CHAT])
pg.run()

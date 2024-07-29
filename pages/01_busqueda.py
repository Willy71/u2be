import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Busquedas",
    page_icon="▶️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

with st.container():
    col01, col02, col03 = st.columns(3)
    with col01:
        if st.button("Anterior", use_container_width=True):
            st.switch_page("app.py")

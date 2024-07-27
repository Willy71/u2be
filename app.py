import streamlit as st

st.title("Reproductor de Youtube sem publicidade")

video = st.input("Cole o endereço de Youtube")

st.video(video, autoplay=True)


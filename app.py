import streamlit as st
import pandas as pd
import os
import re
from pytube import YouTube

# Colocar nome na pagina, icone e ampliar a tela
st.set_page_config(
    page_title="You2be",
    page_icon="▶️",
    layout="wide"
)

# Definir el nombre del archivo CSV
CSV_FILE = 'youtube_videos.csv'

def centrar_texto(texto, tamanho, color):
    st.markdown(f"<h{tamanho} style='text-align: center; color: {color}'>{texto}</h{tamanho}>",
                unsafe_allow_html=True)

# Crear o actualizar la estructura del archivo CSV si no existe
def initialize_csv():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=['Category', 'URL', 'Title'])
        df.to_csv(CSV_FILE, index=False)
    else:
        df = pd.read_csv(CSV_FILE)
        if 'Title' not in df.columns:
            df['Title'] = ''
            df.to_csv(CSV_FILE, index=False)

initialize_csv()

def main():
    # Sidebar para agregar y seleccionar videos
    with st.sidebar:
        centrar_texto("Agregar video", 5, "white")

        # Input de texto para ingresar la URL del video de YouTube
        video_url = st.text_input("Ingresa la URL del video de YouTube:")

        # Input de texto para ingresar la categoría
        category = st.text_input("Ingresa la categoría del video:")

        # Mostrar categorías disponibles
        st.text("Categorías Disponibles")
        df = load_videos()
        categories = df['Category'].unique()

        selected_category = st.selectbox("Selecciona una categoría para ver los videos:", categories)
        # Botón para agregar el video
        if st.button("Agregar Video"):
            if video_url and category:
                video_id = extract_video_id(video_url)
                if video_id:
                    video_title = get_video_title(video_url)
                    if video_title:
                        add_video(category, video_url, video_title)
                        st.success(f"Video '{video_title}' agregado a la categoría '{category}'")
                    else:
                        st.error("No se pudo obtener el título del video. Verifica la URL.")
                else:
                    st.error("Por favor, ingresa una URL de YouTube válida.")
            else:
                st.error("Por favor, ingresa una URL y una categoría.")

    # Reproductor principal de video
    if 'selected_video_url' in st.session_state:
        st.video(st.session_state.selected_video_url)

    if selected_category:
        st.subheader(f"Videos en la categoría: {selected_category}")
        videos_in_category = df[df['Category'] == selected_category]
        for idx, row in videos_in_category.iterrows():
            st.write(f"{row['Title']}")
            if st.button(f"Reproducir Video", key=f"play_{idx}"):
                st.session_state.selected_video_url = row['URL']
                st.rerun()
            if st.button(f"Eliminar Video", key=f"delete_{idx}"):
                delete_video(idx)
                st.success(f"Video '{row['Title']}' eliminado")
                st.rerun()

def extract_video_id(url):
    """
    Extrae el ID del video de una URL de YouTube.
    """
    regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

    match = re.match(regex, url)
    if match:
        return match.group(6)
    return None

def get_video_title(url):
    """
    Obtiene el título de un video de YouTube usando pytube.
    """
    try:
        yt = YouTube(url)
        return yt.title
    except Exception as e:
        st.error(f"Error al obtener el título del video: {e}")
        return None

def add_video(category, url, title):
    df = load_videos()
    new_row = pd.DataFrame({'Category': [category], 'URL': [url], 'Title': [title]})
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

def load_videos():
    return pd.read_csv(CSV_FILE)

def delete_video(index):
    df = load_videos()
    df = df.drop(index)
    df.to_csv(CSV_FILE, index=False)

if __name__ == "__main__":
    main()

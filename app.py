import streamlit as st
import pandas as pd
import os
import re
from pytube import YouTube

# Configuración de la página
st.set_page_config(
    page_title="You 2 be",
    page_icon="▶️",
)

# Definir el nombre del archivo CSV
CSV_FILE = 'youtube_videos.csv'

# Función para centrar el texto
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
        # Mostrar categorías disponibles
        centrar_texto("Videos", 4, 'white')
        df = load_videos()

        # Filtrar por categoría
        df_1 = df["Category"].unique()
        df_1_1 = sorted(df_1)
        slb_1 = st.selectbox('Selecciona una categoría para ver los videos:', df_1_1)
        df = df[df["Category"] == slb_1]

        # Filtrar por título de video
        df_2 = df["Title"].unique()
        df_2_1 = sorted(df_2)
        slb_2 = st.selectbox('Titulo', df_2_1)
        df_video = df[df["Title"] == slb_2].iloc[0]

        # Guardar la URL del video seleccionado en el estado de la sesión
        if 'selected_video_url' not in st.session_state:
            st.session_state.selected_video_url = df_video['URL']
            st.session_state.selected_video_idx = df.index[df['Title'] == slb_2].tolist()[0]
        
        st.session_state.selected_video_url = df_video['URL']
        st.session_state.selected_video_idx = df.index[df['Title'] == slb_2].tolist()[0]

    # Reproductor principal de video
    if 'selected_video_url' in st.session_state:
        st.video(st.session_state.selected_video_url)

        if 'selected_video_idx' in st.session_state:
            selected_idx = st.session_state.selected_video_idx
            if st.button(f"Eliminar Video", key=f"delete_{selected_idx}"):
                delete_video(selected_idx)
                st.success("Video eliminado")
                del st.session_state['selected_video_url']
                del st.session_state['selected_video_idx']
                st.experimental_rerun()

    st.title("")
    centrar_texto("Agregar video", 4, "white")

    # Input de texto para ingresar la URL del video de YouTube
    video_url = st.text_input("Ingresa la URL del video de YouTube:")

    # Input de texto para ingresar la categoría
    category = st.text_input("Ingresa la categoría del video:")

    # Botón para agregar el video
    if st.button("Agregar Video"):
        if video_url and category:
            video_id = extract_video_id(video_url)
            if video_id:
                video_title = get_video_title(video_url)
                if video_title:
                    add_video(category, video_url, video_title)
                    st.success(f"Video '{video_title}' agregado a la categoría '{category}'")
                    st.experimental_rerun()
                else:
                    st.error("No se pudo obtener el título del video. Verifica la URL.")
            else:
                st.error("Por favor, ingresa una URL de YouTube válida.")
        else:
            st.error("Por favor, ingresa una URL y una categoría.")

    # Botón para activar/desactivar la reproducción continua
    if 'continuous_playback' not in st.session_state:
        st.session_state.continuous_playback = False

    st.sidebar.write("")
    if st.sidebar.button("Activar Reproducción Continua"):
        st.session_state.continuous_playback = not st.session_state.continuous_playback

    if st.session_state.continuous_playback:
        st.sidebar.write("Reproducción Continua Activada")

    # Reproducción continua
    if st.session_state.continuous_playback and 'selected_video_idx' in st.session_state:
        df = load_videos()
        df = df[df["Category"] == slb_1]
        current_index = st.session_state.selected_video_idx
        next_index = (current_index + 1) % len(df)
        next_video_url = df.iloc[next_index]['URL']

        # Reproducir el siguiente video automáticamente
        st.session_state.selected_video_url = next_video_url
        st.session_state.selected_video_idx = next_index
        st.experimental_rerun()

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

import streamlit as st
import pandas as pd
import re
from pytube import YouTube
from streamlit_gsheets import GSheetsConnection

# Configuración de la página
st.set_page_config(
    page_title="You 2 be",
    page_icon="▶️",
)

# Establecer conexión con Google Sheets
conn = st.experimental_connection("gsheets", type=GSheetsConnection)

# Leer datos existentes de la hoja de Google Sheets
df = conn.read(worksheet="youtube_videos", usecols=list(range(3)), ttl=5)
df = df.dropna(how="all")

# Función para centrar el texto
def centrar_texto(texto, tamanho, color):
    st.markdown(f"<h{tamanho} style='text-align: center; color: {color}'>{texto}</h{tamanho}>",
                unsafe_allow_html=True)

def main():
    # Sidebar para agregar y seleccionar videos
    with st.sidebar:
        st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#1717dc;" /> """, unsafe_allow_html=True)
        # Mostrar categorías disponibles
        centrar_texto("Videos", 4, 'white')

        # feature_1 filters
        df_1 = df["Category"].unique()
        df_1_1 = sorted(df_1)
        slb_1 = st.selectbox('Selecciona una categoría para ver los videos:', df_1_1)
        # filter out data
        filtered_df = df[df["Category"] == slb_1]

        # feature_2 filters
        df_2 = filtered_df["Title"].unique()
        df_2_1 = sorted(df_2)
        slb_2 = st.selectbox('Titulo', df_2_1)
        # filter out data
        selected_video = filtered_df[filtered_df["Title"] == slb_2].iloc[0]

        # Guardar la URL del video seleccionado en el estado de la sesión
        if 'selected_video_url' not in st.session_state:
            st.session_state.selected_video_url = selected_video['URL']
            st.session_state.selected_video_idx = filtered_df.index[filtered_df['Title'] == slb_2].tolist()[0]

        st.session_state.selected_video_url = selected_video['URL']
        st.session_state.selected_video_idx = filtered_df.index[filtered_df['Title'] == slb_2].tolist()[0]

        # Botón para activar/desactivar la reproducción continua
        if 'continuous_playback' not in st.session_state:
            st.session_state.continuous_playback = False

        if st.button("Activar Reproducción Continua"):
            st.session_state.continuous_playback = not st.session_state.continuous_playback

        if st.session_state.continuous_playback:
            st.write("Reproducción Continua Activada")

    # Reproductor principal de video
    if 'selected_video_url' in st.session_state:
        st.video(st.session_state.selected_video_url, autoplay=True)

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
    new_row = pd.DataFrame({'Category': [category], 'URL': [url], 'Title': [title]})
    df = pd.concat([df, new_row], ignore_index=True)
    conn.update(worksheet="youtube_videos", data=df)
    st.success("Video agregado con éxito")

def load_videos():
    return df

def delete_video(index):
    df = load_videos()
    df = df.drop(index)
    conn.update(worksheet="youtube_videos", data=df)

if __name__ == "__main__":
    main()

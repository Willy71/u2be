import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os
import re
from pytube import YouTube

# Configuración de la página
st.set_page_config(
    page_title="You 2 be",
    page_icon="▶️",
)

# Configuración de la conexión a Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = os.path.join('credentials.json')  # Ruta al archivo de credenciales

credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
gc = gspread.authorize(credentials)

# Abre la hoja de cálculo usando la clave del documento
SPREADSHEET_KEY = "1WXqOfW6Fd8qaY5gDfTw0kuiqasTKEhFZ2k13aQAVvVw"  # Reemplaza con la clave de tu documento

try:
    sheet = gc.open_by_key(SPREADSHEET_KEY).sheet1
except gspread.exceptions.SpreadsheetNotFound:
    st.error(f"No se encontró la hoja de cálculo con la clave '{SPREADSHEET_KEY}'. Asegúrate de que la clave es correcta y que has compartido la hoja con el correo electrónico del cliente de servicio.")
except Exception as e:
    st.error(f"Error al abrir la hoja de cálculo: {e}")

# Función para centrar el texto
def centrar_texto(texto, tamanho, color):
    st.markdown(f"<h{tamanho} style='text-align: center; color: {color}'>{texto}</h{tamanho}>",
                unsafe_allow_html=True)

# Cargar los videos desde Google Sheets
def load_videos():
    rows = sheet.get_all_records()
    df = pd.DataFrame(rows)
    return df

# Agregar un video a Google Sheets
def add_video(category, url, title):
    new_row = {'Category': category, 'URL': url, 'Title': title}
    sheet.append_row(list(new_row.values()))

# Eliminar un video de Google Sheets
def delete_video(index):
    sheet.delete_row(index + 2)  # +2 porque Google Sheets es 1-indexed y hay una fila de encabezado

def main():
    # Sidebar para agregar y seleccionar videos
    with st.sidebar:
        st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#1717dc;" /> """, unsafe_allow_html=True)
        # Mostrar categorías disponibles
        centrar_texto("Videos", 4, 'white')
        df = load_videos()
        
        # Feature 1 filters
        df_1 = df["Category"].unique()
        df_1_1 = sorted(df_1)
        slb_1 = st.selectbox('Selecciona una categoría para ver los videos:', df_1_1)
        # Filter out data
        df = df[(df["Category"] == slb_1)]
        
        # Feature 2 filters
        df_2 = df["Title"].unique()
        df_2_1 = sorted(df_2)
        slb_2 = st.selectbox('Titulo', df_2_1)
        # Filter out data
        df = df[(df["Title"] == slb_2)]
             
        df_video = df[df["Title"] == slb_2].iloc[0]

        # Reproductor principal de video
        if 'selected_video_url' not in st.session_state:
            st.session_state.selected_video_url = df_video['URL']

        st.session_state.selected_video_url = df_video['URL']

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
       
    # Sidebar para agregar videos
    with st.sidebar:
        st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#1717dc;" /> """, unsafe_allow_html=True)
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
        st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#1717dc;" /> """, unsafe_allow_html=True)

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

if __name__ == "__main__":
    main()

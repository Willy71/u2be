import streamlit as st
import pandas as pd
import re
import gspread
from google.oauth2.service_account import Credentials
from pytube import YouTube

# Configuración de la página
st.set_page_config(
    page_title="You 2 be",
    page_icon="▶️",
)

# Reducir el espacio en el encabezado
reduce_space ="""
            <style type="text/css">
            div[data-testid="stAppViewBlockContainer"]{
                padding-top:30px;
            }
            </style>
            """
st.markdown(reduce_space, unsafe_allow_html=True)

#=============================================================================================================================
# Conexión via gspread a través de Google Sheets
SERVICE_ACCOUNT_INFO = st.secrets["gsheets"]
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
gc = gspread.authorize(credentials)
SPREADSHEET_KEY = '1NQN92mhMxhhj9CP3OfYxo_aowkI74y49sSPvStIiXn0'
SHEET_NAME = 'youtube_videos'
#=============================================================================================================================

try:
    sheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(SHEET_NAME)
except gspread.exceptions.SpreadsheetNotFound:
    st.error(f"No se encontró la hoja de cálculo con la clave '{SPREADSHEET_KEY}'.")

# Función para centrar el texto
def centrar_texto(texto, tamanho, color):
    st.markdown(f"<h{tamanho} style='text-align: center; color: {color}'>{texto}</h{tamanho}>", unsafe_allow_html=True)

# Cargar los videos desde Google Sheets
def load_videos():
    rows = sheet.get_all_records()
    df = pd.DataFrame(rows)
    df.columns = df.columns.str.lower()  # Convertir todos los nombres de columnas a minúsculas
    return df

# Agregar un video a Google Sheets
def add_video(category, url, title):
    new_row = {'category': category, 'url': url, 'title': title}
    sheet.append_row(list(new_row.values()))
    st.rerun()

# Eliminar un video de Google Sheets
def delete_video(url):
    cell = sheet.find(url)
    if cell:
        sheet.delete_rows(cell.row)

def main():
    # Sidebar para agregar y seleccionar videos
    with st.sidebar:
        centrar_texto("Videos", 2, 'white')
        df = load_videos()
        
        # Filtrar por categorías
        categories = df["category"].unique()
        category_selected = st.selectbox('Categoría', sorted(categories))
        df_filtered = df[df["category"] == category_selected]
        
        # Filtrar por títulos
        titles = df_filtered["title"].unique()
        title_selected = st.selectbox('Título', sorted(titles))
        video_selected = df_filtered[df_filtered["title"] == title_selected].iloc[0]

        # Reproductor de video
        if 'selected_video_url' not in st.session_state:
            st.session_state.selected_video_url = video_selected['url']

        st.session_state.selected_video_url = video_selected['url']

    # Reproductor principal de video
    if 'selected_video_url' in st.session_state:
        st.video(st.session_state.selected_video_url, autoplay=False)

        if st.session_state.selected_video_url:
            with st.container():
                col15, col19 = st.columns([3, 2])
                with col15:
                    if st.button("Eliminar Video"):
                        delete_video(st.session_state.selected_video_url)
                        st.success("Video eliminado")
                        del st.session_state['selected_video_url']
                        st.rerun()
                with col19:
                    if st.button("Siguiente", use_container_width=True):
                        st.switch_page("pages/01_Busquedas.py")

    # Agregar videos en la barra lateral
    with st.sidebar:
        st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#1717dc;" /> """, unsafe_allow_html=True)
        centrar_texto("Agregar video", 2, "white")

        # Input de texto para ingresar la URL del video de YouTube
        video_url = st.text_input("URL del video de YouTube:")

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
                        st.rerun()
                    else:
                        st.error("No se pudo obtener el título del video. Verifica la URL.")
                else:
                    st.error("Por favor, ingresa una URL de YouTube válida.")
            else:
                st.error("Por favor, ingresa una URL y una categoría.")

# Funciones auxiliares
def extract_video_id(url):
    regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    match = re.match(regex, url)
    if match:
        return match.group(6)
    return None

def get_video_title(url):
    try:
        yt = YouTube(url)
        return yt.title
    except Exception as e:
        st.error(f"Error al obtener el título del video: {e}")
        return None

if __name__ == "__main__":
    main()

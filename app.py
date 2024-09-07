import streamlit as st
import pandas as pd
import re
import gspread
from google.oauth2.service_account import Credentials
from pytube import YouTube

# Configuración de la página
st.set_page_config(page_title="You 2 be", page_icon="▶️")

# Estilo para reducir el espacio superior
reduce_space = """
            <style type="text/css">
            div[data-testid="stAppViewBlockContainer"]{
                padding-top:30px;
            }
            </style>
            """
st.markdown(reduce_space, unsafe_allow_html=True)

# Configuración de Google Sheets
SERVICE_ACCOUNT_INFO = st.secrets["gsheets"]
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
gc = gspread.authorize(credentials)
SPREADSHEET_KEY = '1NQN92mhMxhhj9CP3OfYxo_aowkI74y49sSPvStIiXn0'
SHEET_NAME = 'youtube_videos'

# Cargar hoja de cálculo
try:
    sheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(SHEET_NAME)
except gspread.exceptions.SpreadsheetNotFound:
    st.error(f"No se encontró la hoja de cálculo con la clave '{SPREADSHEET_KEY}'.")

# Función para centrar texto
def centrar_texto(texto, tamanho, color):
    st.markdown(f"<h{tamanho} style='text-align: center; color: {color}'>{texto}</h{tamanho}>", unsafe_allow_html=True)

# Cargar videos desde Google Sheets
def load_videos():
    rows = sheet.get_all_records()
    return pd.DataFrame(rows)

# Agregar video a Google Sheets
def add_video(category, url, title):
    new_row = {'Category': category, 'URL': url, 'Title': title}
    sheet.append_row(list(new_row.values()))
    st.rerun()

# Eliminar video de Google Sheets por URL
def delete_video(url):
    cell = sheet.find(url)
    if cell:
        sheet.delete_rows(cell.row)

# Extraer video_id de la URL de YouTube
def extract_video_id(url):
    regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    match = re.match(regex, url)
    if match:
        return match.group(6)
    return None

# Obtener título del video
def get_video_title(url):
    try:
        yt = YouTube(url)
        return yt.title
    except Exception as e:
        st.error(f"Error al obtener el título del video: {e}")
        return None

# Reproductor de videos
def main():
    with st.sidebar:
        centrar_texto("Videos", 2, 'white')
        df = load_videos()

        # Filtrar por categoría
        df_1 = df["Category"].unique()
        df_1_1 = sorted(df_1)
        slb_1 = st.selectbox('Categoria', df_1_1)

        df = df[(df["Category"] == slb_1)]

        # Seleccionar video por título
        df_2 = df["Title"].unique()
        df_2_1 = sorted(df_2)
        slb_2 = st.selectbox('Titulo', df_2_1)
        df_video = df[df["Title"] == slb_2].iloc[0]

        # Reproductor de video seleccionado
        if 'selected_video_url' not in st.session_state:
            st.session_state.selected_video_url = df_video['URL']

        st.session_state.selected_video_url = df_video['URL']

        # Crear lista de reproducción continua
        playlist = ','.join(df['URL'].apply(lambda x: extract_video_id(x)))

        # Mostrar reproductor
        st.markdown(f"""
        <div style="display: flex; justify-content: center;">
            <iframe id="player" type="text/html" width="832" height="507"
            src="https://www.youtube.com/embed/{extract_video_id(st.session_state.selected_video_url)}?playlist={playlist}&autoplay=1&controls=1&loop=1"
            frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
        </div>
        """, unsafe_allow_html=True)

        # Botones de eliminar y siguiente
        with st.container():
            col15, col19 = st.columns([3, 2])
            with col15:
                if st.button("Eliminar Video"):
                    delete_video(st.session_state.selected_video_url)
                    st.success("Video eliminado")
                    st.rerun()

            with col19:
                if st.button("Siguiente", use_container_width=True):
                    st.session_state.selected_video_url = df.iloc[(df.index[df["URL"] == st.session_state.selected_video_url].tolist()[0] + 1) % len(df)]['URL']
                    st.rerun()

    # Sidebar para agregar videos
    with st.sidebar:
        st.markdown("<hr style='height:10px;border:none;color:#333;background-color:#1717dc;' />", unsafe_allow_html=True)
        centrar_texto("Agregar video", 2, "white")

        # Agregar video
        video_url = st.text_input("URL del video de YouTube:")
        category = st.text_input("Ingresa la categoría del video:")

        if st.button("Agregar Video"):
            if video_url and category:
                video_id = extract_video_id(video_url)
                if video_id:
                    video_title = get_video_title(video_url)
                    if video_title:
                        add_video(category, video_url, video_title)
                        st.success(f"Video '{video_title}' agregado a la categoría '{category}'")
                    else:
                        st.error("No se pudo obtener el título del video.")
                else:
                    st.error("Por favor, ingresa una URL válida.")
            else:
                st.error("Por favor, ingresa una URL y una categoría.")

if __name__ == "__main__":
    main()

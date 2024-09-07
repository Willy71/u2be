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

# Reducir espacio en la parte superior
reduce_space ="""
            <style type="text/css">
            div[data-testid="stAppViewBlockContainer"]{
                padding-top:30px;
            }
            </style>
            """
st.markdown(reduce_space, unsafe_allow_html=True)

#=============================================================================================================================
# Conexión con Google Sheets
SERVICE_ACCOUNT_INFO = st.secrets["gsheets"]
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
gc = gspread.authorize(credentials)
SPREADSHEET_KEY = '1NQN92mhMxhhj9CP3OfYxo_aowkI74y49sSPvStIiXn0'
SHEET_NAME = 'youtube_videos'

try:
    sheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(SHEET_NAME)
except gspread.exceptions.SpreadsheetNotFound:
    st.error(f"No se encontró la hoja de cálculo con la clave '{SPREADSHEET_KEY}'.")

# Funciones auxiliares
def centrar_texto(texto, tamanho, color):
    st.markdown(f"<h{tamanho} style='text-align: center; color: {color}'>{texto}</h{tamanho}>", unsafe_allow_html=True)

def load_videos():
    rows = sheet.get_all_records()
    df = pd.DataFrame(rows)
    return df

def extract_video_id(url):  
    regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+\?v=([^&=%\?]{11})'
    match = re.match(regex, url)
    if match:
        return match.group(4)
    return None

def get_video_title(url):
    try:
        yt = YouTube(url)
        return yt.title
    except Exception as e:
        st.error(f"Error al obtener el título del video: {e}")
        return None

def main():
    # Cargar los videos desde Google Sheets
    df = load_videos()

    if df.empty:
        st.warning("No se encontraron videos en la base de datos.")
        return

    # Sidebar para seleccionar videos
    with st.sidebar:
        centrar_texto("Videos", 2, 'white')

        # Mostrar las categorías
        df_1 = df["Category"].unique()
        df_1_1 = sorted(df_1)
        slb_1 = st.selectbox('Categoria', df_1_1)

        # Filtrar videos por categoría
        df = df[df["Category"] == slb_1]

        # Mostrar los títulos y URLs en radio buttons
        if not df.empty:
            video_ids = df["Url"].apply(extract_video_id)
            video_ids = video_ids[video_ids.notnull()]

            if not video_ids.empty:
                clicked_video_id = st.radio(
                    "Selecciona un video para reproducir",
                    video_ids,
                    format_func=lambda url: df[df["Url"].apply(extract_video_id) == url]["Title"].values[0]
                )

                # Generar la lista de reproducción en formato JavaScript
                playlist = ','.join(video_ids)

                # Insertar el reproductor de YouTube centrado en la pantalla principal
                st.markdown(f"""
                <div style="display: flex; justify-content: center;">
                    <iframe id="player" type="text/html" width="832" height="507"
                    src="https://www.youtube.com/embed/{clicked_video_id}?playlist={playlist}&autoplay=1&controls=1&loop=1"
                    frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("No se encontraron URLs válidas para los videos.")
        else:
            st.warning("No se encontraron videos en la categoría seleccionada.")

    # Sección para agregar videos
    with st.sidebar:
        st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#1717dc;" /> """, unsafe_allow_html=True)
        centrar_texto("Agregar video", 2, "white")
        
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
                        st.rerun()
                    else:
                        st.error("No se pudo obtener el título del video.")
                else:
                    st.error("Por favor, ingresa una URL de YouTube válida.")
            else:
                st.error("Por favor, ingresa una URL y una categoría.")

if __name__ == "__main__":
    main()

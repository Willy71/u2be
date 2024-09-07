import streamlit as st
import pandas as pd
import re
import gspread
from google.oauth2.service_account import Credentials
from pytube import YouTube
from googleapiclient.discovery import build

# Configuración de la página
st.set_page_config(
    page_title="You 2 be",
    page_icon="▶️",
)

# We reduced the empty space at the beginning of the streamlit
reduce_space ="""
            <style type="text/css">
            /* Remueve el espacio en el encabezado por defecto de las apps de Streamlit */
            div[data-testid="stAppViewBlockContainer"]{
                padding-top:30px;
            }
            </style>
            """
# We load reduce_space
st.html(reduce_space)

# Clave de la API de YouTube
api_key = st.secrets["youtube"]["api_key"]

# Crear el cliente de la API de YouTube
youtube = build('youtube', 'v3', developerKey=api_key)

# Ruta al archivo de credenciales
SERVICE_ACCOUNT_INFO = st.secrets["gsheets"]

# Scopes necesarios
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Cargar credenciales y autorizar
credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
gc = gspread.authorize(credentials)

# Clave de la hoja de cálculo (la parte de la URL después de "/d/" y antes de "/edit")
SPREADSHEET_KEY = '1NQN92mhMxhhj9CP3OfYxo_aowkI74y49sSPvStIiXn0'
SHEET_NAME = 'youtube_videos'

try:
    sheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(SHEET_NAME)
except gspread.exceptions.SpreadsheetNotFound:
    st.error(f"No se encontró la hoja de cálculo con la clave '{SPREADSHEET_KEY}'.")

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
    st.rerun()

# Eliminar un video de Google Sheets
def delete_video(url):
    cell = sheet.find(url)
    if cell:
        sheet.delete_rows(cell.row)

def get_playlists(channel_id):
    # Recuperar listas de reproducción del canal
    request = youtube.playlists().list(
        part='snippet',
        channelId=channel_id,
        maxResults=25
    )
    response = request.execute()
    return response['items']

def get_videos(playlist_id):
    # Recuperar videos dentro de una lista de reproducción
    request = youtube.playlistItems().list(
        part='snippet',
        playlistId=playlist_id,
        maxResults=50
    )
    response = request.execute()
    return response['items']

def main():
    # Sidebar para agregar y seleccionar videos
    with st.sidebar:
        centrar_texto("Videos", 2, 'white')
        df = load_videos()
        
        # Filtros para las categorías y títulos
        df_1 = df["Category"].unique()
        df_1_1 = sorted(df_1)
        slb_1 = st.selectbox('Categoria', df_1_1)
        df = df[(df["Category"] == slb_1)]
        
        df_2 = df["Title"].unique()
        df_2_1 = sorted(df_2)
        slb_2 = st.selectbox('Titulo', df_2_1)
        df = df[(df["Title"] == slb_2)]
             
        df_video = df[df["Title"] == slb_2].iloc[0]

        # Reproductor principal de video
        if 'selected_video_url' not in st.session_state:
            st.session_state.selected_video_url = df_video['Url']

        st.session_state.selected_video_url = df_video['Url']

    # Sección para la reproducción continua y listado de videos
    channel_id = st.sidebar.text_input("Ingresa un Channel ID")
    
    if api_key and channel_id:
        youtube = build('youtube', 'v3', developerKey=api_key)
        try:
            playlists = get_playlists(channel_id)
            playlist_titles = [playlist['snippet']['title'] for playlist in playlists]
            selected_playlist = st.sidebar.selectbox("Selecciona una lista de reproducción", playlist_titles)

            if selected_playlist:
                playlist_id = next(playlist['id'] for playlist in playlists if playlist['snippet']['title'] == selected_playlist)
                videos = get_videos(playlist_id)
                video_ids = [video['snippet']['resourceId']['videoId'] for video in videos]

                st.sidebar.markdown("### Videos en la lista de reproducción")
                clicked_video_id = st.sidebar.radio(
                    "Selecciona un video para reproducir",
                    video_ids,
                    format_func=lambda vid_id: next(video['snippet']['title'] for video in videos if video['snippet']['resourceId']['videoId'] == vid_id)
                )

                playlist = ','.join(video_ids)

                # Reproducción continua del video seleccionado
                st.markdown(f"""
                <div style="display: flex; justify-content: center;">
                    <iframe id="player" type="text/html" width="832" height="507"
                    src="https://www.youtube.com/embed/{clicked_video_id}?playlist={playlist}&autoplay=1&controls=1&loop=1"
                    frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error al recuperar datos de YouTube: {e}")
    else:
        st.warning("Por favor, ingresa tu API Key y Channel ID.")

    # Funcionalidad para agregar videos
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
                        st.error("No se pudo obtener el título del video. Verifica la URL.")
                else:
                    st.error("Por favor, ingresa una URL de YouTube válida.")
            else:
                st.error("Por favor, ingresa una URL y una categoría.")

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

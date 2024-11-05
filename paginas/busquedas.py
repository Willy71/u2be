import streamlit as st
from googleapiclient.discovery import build
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="Busquedas de You2be",
    page_icon="▶️",
    layout="wide",
    initial_sidebar_state="collapsed"
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

# Configuración de la API de Google Sheets
SERVICE_ACCOUNT_INFO = st.secrets["gsheets"]
SCOPES = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]

credentials = Credentials.from_service_account_info(
    SERVICE_ACCOUNT_INFO, scopes=SCOPES)
gc = gspread.authorize(credentials)

# Reemplaza con tu clave de Google Sheets
SPREADSHEET_KEY = '1NQN92mhMxhhj9CP3OfYxo_aowkI74y49sSPvStIiXn0'
SHEET_NAME = 'youtube_videos'  # Reemplaza con el nombre de tu hoja de cálculo

# Configuración de la API de YouTube
YOUTUBE_API_KEY = st.secrets["youtube"]["api_key"]
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Función para centrar el texto
def centrar_texto(texto, tamanho, color):
    st.markdown(
        f"<h{tamanho} style='text-align: center; color: {color}'>{texto}</h{tamanho}>", unsafe_allow_html=True)

# Función para cargar listas de Google Sheets


def load_lists():
    try:
        sheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(SHEET_NAME)
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except gspread.exceptions.SpreadsheetNotFound:
        st.error("No se encontró la hoja de cálculo. Verifica la clave del documento y comparte la hoja con el correo de tu cuenta de servicio.")
        return pd.DataFrame()
    except gspread.exceptions.WorksheetNotFound:
        st.error(
            "No se encontró la hoja dentro del documento. Verifica el nombre de la hoja.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al cargar las listas: {e}")
        return pd.DataFrame()

# Función para buscar videos en YouTube


def search_youtube(query, max_results=10):
    search_response = youtube.search().list(
        q=query,
        part='id,snippet',
        maxResults=max_results
    ).execute()

    videos = []
    for search_result in search_response.get('items', []):
        if search_result['id']['kind'] == 'youtube#video':
            video_id = search_result['id']['videoId']
            title = search_result['snippet']['title']
            thumbnail_url = search_result['snippet']['thumbnails']['high']['url']
            url = f"https://www.youtube.com/watch?v={video_id}"
            videos.append({'Title': title, 'URL': url,
                          'Thumbnail': thumbnail_url})

    return videos

# Función para agregar video a una lista
def add_video_to_list(category, url, title):
    try:
        sheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(SHEET_NAME)
        new_row = {'Category': category, 'URL': url, 'Title': title}
        sheet.append_row(list(new_row.values()))
        st.session_state['success'] = f"Video '{title}' agregado a la lista '{category}'"
    except Exception as e:
        st.error(f"Error al agregar el video a la lista: {e}")

# Función principal
def main():
    centrar_texto("Búsqueda de Videos en YouTube", 1, 'white')

    if 'search_results' not in st.session_state:
        st.session_state['search_results'] = []

    if 'success' not in st.session_state:
        st.session_state['success'] = ''

    if 'lists' not in st.session_state:
        st.session_state['lists'] = load_lists()

    with st.container():
        col01, col02, col03 = st.columns(3)
        with col02:
            search_query = st.text_input("Buscar videos en YouTube:")
            if st.button("Buscar"):
                if search_query:
                    st.session_state['search_results'] = search_youtube(
                        search_query)
                    st.session_state['success'] = ''

            if st.session_state['success']:
                st.success(st.session_state['success'])

            centrar_texto("Resultados de la búsqueda", 4, 'white')
            for idx, result in enumerate(st.session_state['search_results']):
                st.markdown(
                    f"""
                    <div style="text-align: center;">
                        <img src="{result['Thumbnail']}" alt="{result['Title']}" style="width: 400px;">
                        <br>
                        <a href="{result['URL']}" target="_blank">{result['Title']}</a>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Selección de lista
                df = st.session_state['lists']
                if not df.empty:
                    existing_categories = sorted(
                        df['Category'].unique().tolist())
                    selected_category = st.selectbox(
                        "Selecciona una lista", existing_categories, key=f"selectbox_{idx}")
                    new_category = st.text_input(
                        "O crea una nueva lista", key=f"new_category_{idx}")

                    if st.button("Agregar a la lista", key=f"add_button_{idx}"):
                        category = new_category if new_category else selected_category
                        if category:
                            add_video_to_list(
                                category, result['URL'], result['Title'])
                        else:
                            st.error(
                                "Por favor, selecciona una lista existente o ingresa una nueva lista.")
    
    with st.container():
        col01, col02, col03 = st.columns(3)
        with col01:
            if st.button("Anterior", use_container_width=True):
                st.switch_page("app.py")

if __name__ == "__main__":
    main()




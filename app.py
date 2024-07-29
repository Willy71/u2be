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
    layout="wide",
    initial_sidebar_state="collapsed"
)

#=============================================================================================================================
# Conexion via gspread a traves de https://console.cloud.google.com/ y Google sheets

# Credenciales de Google como un diccionario
SERVICE_ACCOUNT_INFO = st.secrets["gsheets"]

# Scopes necesarios
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Cargar credenciales y autorizar
credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
gc = gspread.authorize(credentials)

# Clave de la hoja de cálculo (la parte de la URL después de "/d/" y antes de "/edit")
SPREADSHEET_KEY = '1NQN92mhMxhhj9CP3OfYxo_aowkI74y49sSPvStIiXn0'  # Reemplaza con la clave de tu documento
SHEET_NAME = 'youtube_videos'  # Nombre de la hoja dentro del documento
#=============================================================================================================================

try:
    sheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(SHEET_NAME)
except gspread.exceptions.SpreadsheetNotFound:
    st.error(f"No se encontró la hoja de cálculo con la clave '{SPREADSHEET_KEY}'. Asegúrate de que la clave es correcta y que has compartido la hoja con el correo electrónico del cliente de servicio.")
except gspread.exceptions.APIError as e:
    st.error(f"Error de API al intentar acceder a la hoja de cálculo: {e}")
except Exception as e:
    st.error(f"Ha ocurrido un error inesperado: {e}")

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
def delete_video(url):
    try:
        cell = sheet.find(url)
        st.write(f"Buscando URL: {url}")
        if cell:
            st.write(f"Encontrado en la fila: {cell.row}")
            sheet.delete_rows(cell.row)  # Cambiado a delete_rows
            st.write("Fila eliminada")
        else:
            st.write("URL no encontrado en la hoja de cálculo")
    except Exception as e:
        st.error(f"Error al intentar eliminar el video: {e}")

def main():
    with st.container():
        col11, col12, col13, col14 = st.columns([2, 1.2, 4.5, 0.8])
        with col11:
            # Mostrar categorías disponibles
            centrar_texto("Videos", 4, 'white')
            df = load_videos()
            
            # Feature 1 filters
            df_1 = df["Category"].unique()
            df_1_1 = sorted(df_1)
            slb_1 = st.selectbox('Categoria', df_1_1, key='category_selectbox')
            
            # Botón para actualizar la lista de títulos
            if st.button("Actualizar títulos", key='update_titles_button', use_container_width=True):
                st.session_state['category_selected'] = slb_1
    
            # Filtro por categoría seleccionada
            if 'category_selected' in st.session_state:
                df = df[df["Category"] == st.session_state['category_selected']]
            else:
                df = df[df["Category"] == slb_1]
            
            # Feature 2 filters
            df_2 = df["Title"].unique()
            df_2_1 = sorted(df_2)
            slb_2 = st.selectbox('Titulo', df_2_1, key='title_selectbox')
            
            # Filtro por título seleccionado
            df_video = df[df["Title"] == slb_2].iloc[0]
    
            # Reproductor principal de video
            if 'selected_video_url' not in st.session_state:
                st.session_state.selected_video_url = df_video['Url']
    
            st.session_state.selected_video_url = df_video['Url']
    
                        
    #==========================================================================================================================================
               
            st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#1717dc;" /> """, unsafe_allow_html=True)
            centrar_texto("Agregar video", 4, "white")
    
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
                        else:
                            st.error("No se pudo obtener el título del video. Verifica la URL.")
                    else:
                        st.error("Por favor, ingresa una URL de YouTube válida.")
                else:
                    st.error("Por favor, ingresa una URL y una categoría.")
#==========================================================================================================================================
    with col13:
        # Pagina principal - Reproductor principal de video
        #centrar_texto("You2be", 1, "white")
        if 'selected_video_url' in st.session_state:
            st.video(st.session_state.selected_video_url, autoplay=False)
            if st.session_state.selected_video_url:
                with st.container():
                    col15, col16, col17, col18, col19 = st.columns([3,1,1,1,2])
                    with col15:         
                        if st.button("Eliminar Video"):
                            delete_video(st.session_state.selected_video_url)
                            st.success("Video eliminado")
                            if 'selected_video_url' in st.session_state:
                                del st.session_state['selected_video_url']
                            st.rerun()
                    with col19:               
                        if st.button("Siguiente", use_container_width=True):
                            st.switch_page("pages/01_busqueda.py")
    
#=========================================================================================================================================
def extract_video_id(url):  
    # Extrae el ID del video de una URL de YouTube.
    regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

    match = re.match(regex, url)
    if match:
        return match.group(6)
    return None

def get_video_title(url):
    # Obtiene el título de un video de YouTube usando pytube.
    try:
        yt = YouTube(url)
        return yt.title
    except Exception as e:
        st.error(f"Error al obtener el título del video: {e}")
        return None

if __name__ == "__main__":
    main()

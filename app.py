import streamlit as st
import pandas as pd
import re
import gspread
from google.oauth2.service_account import Credentials
from pytube import YouTube

# Configuración de la página
st.set_page_config(page_title="You 2 be", page_icon="▶️")

# Reducir espacio en la parte superior
reduce_space = """
            <style type="text/css">
            div[data-testid="stAppViewBlockContainer"]{
                padding-top:30px;
            }
            </style>
            """
st.markdown(reduce_space, unsafe_allow_html=True)

# Conexión con Google Sheets
SERVICE_ACCOUNT_INFO = st.secrets["gsheets"]
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
gc = gspread.authorize(credentials)
SPREADSHEET_KEY = '1NQN92mhMxhhj9CP3OfYxo_aowkI74y49sSPvStIiXn0'
SHEET_NAME = 'youtube_videos'
link_sheet = "https://docs.google.com/spreadsheets/d/1NQN92mhMxhhj9CP3OfYxo_aowkI74y49sSPvStIiXn0/edit?usp=sharing"

# Intentar acceder a la hoja
try:
    sheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(SHEET_NAME)
except gspread.exceptions.SpreadsheetNotFound:
    st.error(f"A planilha com a chave não foi encontrada '{SPREADSHEET_KEY}'.")

def center_text_link(link_text, link_url, size, color):
    """
    Centers a hyperlink on the Streamlit page.

    Parameters:
    - link_text (str): The text to display as a hyperlink.
    - link_url (str): The URL the link points to.
    - size (str): The size of the text (HTML heading size, e.g., "1" for <h1>).
    - color (str): The color of the text.
    """
    st.markdown(
        f"<h{size} style='text-align: center; color: {color}'><a href='{link_url}' target='_blank'>{link_text}</a></h{size}>",
        unsafe_allow_html=True
    )

# Funciones auxiliares
def centrar_texto(texto, tamanho, color):
    st.markdown(f"<h{tamanho} style='text-align: center; color: {color}'>{texto}</h{tamanho}>", unsafe_allow_html=True)

def load_videos():
    rows = sheet.get_all_records()
    df = pd.DataFrame(rows)
    return df

def extract_video_id(url):
    regex = r'(?:https?://)?(?:www\.)?(?:youtube\.com|youtu\.be)/(?:watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    match = re.match(regex, url)
    if match:
        return match.group(1)
    return None

def get_video_title(url):
    try:
        yt = YouTube(url)
        return yt.title
    except Exception as e:
        st.error(f"Error al obtener el título del video: {e}")
        return None

# Eliminar un video de Google Sheets
def delete_video(url):
    cell = sheet.find(url)
    if cell:
        sheet.delete_rows(cell.row)

def add_video(category, url, title):
    sheet.append_row([category, url, title])

# Función principal
def main():
    df = load_videos()

    if df.empty:
        st.warning("Nenhum vídeo encontrado no banco de dados.")
        return

    # Sidebar para seleccionar videos
    with st.sidebar:
        df_1 = df["Category"].unique()
        df_1_1 = sorted(df_1)
        slb_1 = st.selectbox('Categoria', df_1_1)

        df_filtered = df[df["Category"] == slb_1]

        if not df_filtered.empty:
            df_titles = df_filtered["Title"].unique()
            #df_titles = sorted(df_titles)
            slb_2 = st.radio("Selecione um vídeo para reproduzir", df_titles)

            df_video = df_filtered[df_filtered["Title"] == slb_2].iloc[0]

            # Generar lista de reproducción con los video_ids de la categoría seleccionada
            video_ids = [extract_video_id(url) for url in df_filtered['Url']]
            playlist = ','.join(video_ids)  # Crear la lista de reproducción en formato de string

    # Reproductor principal de video con autoplay y lista de reproducción
    st.markdown(f"""
    <div style="display: flex; justify-content: center;">
        <iframe id="player" type="text/html" width="832" height="507"
        src="https://www.youtube.com/embed/{extract_video_id(df_video['Url'])}?playlist={playlist}&autoplay=1&controls=1&loop=1"
        frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
    </div>
    """, unsafe_allow_html=True)

    st.text("")

    # Botón para eliminar el video
    with st.container():
        col15, col16, col17, col18, col19 = st.columns([3,1,1,1,2])
        with col15:
            if st.button("Excluir vídeo"):
                delete_video(df_video['Url'])
                st.success("Vídeo excluído")
                st.rerun()

    # Sección para agregar videos
    with st.sidebar:
        st.markdown("""<hr style="height:5px;border:none;color:#333;background-color:#1717dc;" /> """, unsafe_allow_html=True)
        centrar_texto("Adicionar vídeo", 2, "white")
        
        video_url = st.text_input("URL do video de YouTube:")
        category = st.text_input("Insira a categoria do vídeo:")

        if st.button("Adicionar vídeo"):
            if video_url and category:
                video_id = extract_video_id(video_url)
                if video_id:
                    video_title = get_video_title(video_url)
                    if video_title:
                        add_video(category, video_url, video_title)
                        st.success(f"Video '{video_title}' adicionado à categoria '{category}'")
                        st.rerun()
                    else:
                        st.error("Não foi possível obter o título do vídeo.")
                else:
                    st.error("Insira um URL válido do YouTube.")
            else:
                st.error("Insira um URL e uma categoria.")
        st.text("")                    
        center_text_link("Hoja de Google Sheets", link_sheet, "green", 1)

if __name__ == "__main__":
    main()
